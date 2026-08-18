# -*- coding: utf-8 -*-
u"""Poe o cliente em portugues, trazendo o texto do bRO.

    python traduz_ptbr.py tudo --verificar     # relata, nao grava nada
    python traduz_ptbr.py tudo                 # aplica
    python traduz_ptbr.py itens skills         # so essas partes
    python traduz_ptbr.py tudo --sem-acento    # a saida de emergencia

Cada parte tem uma fonte diferente dentro da instalacao do Ragnarok Brazil, e
e isso que o arquivo organiza. O acordo de 2026-08-02 (PENDENCIAS.md) e que o
bRO e a fonte de referencia: nada aqui e traduzido por nos, tudo e importado.

    parte        o que aparece traduzido           fonte no bRO
    ---------------------------------------------------------------------------
    msgstrid     rotulos de janela e de botao      msgstring_br.lub (bytecode)
    msgtable     mensagens de sistema e de erro    data\\msgstringtable.txt
    itens        nome e descricao de item          System\\iteminfo_new.lub
    skills       nome e descricao de habilidade    skillinfolist/skilldescript
    quests       titulo e texto do diario          data\\questid2display.txt
    questinfo    a janela de missoes               OngoingQuestInfoList_True
    questreco    a aba RECOMENDADAS               RecommendedQuestInfoList_True
    conquistas   o modal de conquista              System\\achievement_list.lub
    mapas        nome do mapa na minimapa          System\\mapInfo.lub
    mapinfo      o letreiro ao entrar no mapa      System\\mapInfo.lub
    cartas       o prefixo que a carta poe no nome data\\cardprefixnametable.txt
    encantamen.  o efeito do encantamento no item  addrandomoptionnametable.lub

**Toda parte e idempotente**: rodar duas vezes nao muda nada na segunda. O que
manda no destino e sempre o arquivo que o cliente ja usa - o do ROenglishRE -, e
o bRO so preenche o texto. Isso e deliberado: o ROenglishRE e mais NOVO que o
bRO e conhece conteudo que o bRO nunca recebeu. Trocar arquivo por arquivo
traduziria o que existe nos dois e **apagaria** o resto; assim o que o bRO nao
tem simplesmente continua em ingles.

O cliente le quase tudo isto **so na inicializacao**. Depois de aplicar, fechar
e reabrir - nenhum `@reload` do servidor alcanca estes arquivos.
"""
import difflib
import os
import re
import shutil
import sys
import time

import ptbr
from ptbr import Erro, pt, decodifica, codifica


# =============================================================== utilitarios

def le(caminho):
    fh = open(caminho, 'rb')
    d = fh.read()
    fh.close()
    return d


def grava(caminho, dados, verificar, rotulo):
    u"""Grava com backup, ou so relata se for --verificar."""
    antigo = le(caminho)
    if antigo == dados:
        print '    nada mudou (ja estava aplicado)'
        return 0
    print '    %d -> %d bytes (%+d)' % (len(antigo), len(dados),
                                        len(dados) - len(antigo))
    if verificar:
        print '    --verificar: nenhum byte gravado'
        return 0
    backup = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M'))
    if not os.path.exists(backup):
        shutil.copy2(caminho, backup)
    fh = open(caminho, 'wb')
    fh.write(dados)
    fh.close()
    print '    gravado (backup: %s)' % os.path.basename(backup)
    return 1


# O conteudo de um literal Lua entre aspas duplas, **respeitando escape**.
#
# Ler isto como `[^"]*` foi o erro que quebrou o cliente em 2026-08-03: o
# `msgstring_kr_s.lub` tem quatro valores com aspa escapada, do tipo
# `"/organize \"Party Name\": Creates a party."`. O regex ingenuo parava na
# aspa escapada, a substituicao deixava metade da linha solta, o arquivo
# perdia a sintaxe, `MsgStrID` virava nil e o cliente abria numa cascata de
# diálogos de erro que nao mencionavam nada disso.
VALOR = r'(?:[^"\\\r\n]|\\.)*'


def aspas(texto):
    u"""Texto que vai entrar num literal Lua com aspas duplas.

    Os arquivos que geramos nao escapam nada - a aspa dupla vira simples e a
    barra invertida vira barra normal, e assim nenhuma escapada e criada. O
    `\\"` que venha do texto de origem e desfeito ANTES, para nao sobrar uma
    barra solta no meio da frase.
    """
    return (texto.replace('\\"', '"')
                 .replace('"', "'")
                 .replace('\\', '/'))


def confere_linhas(texto, campos, rotulo):
    u"""Toda linha que atribui um destes campos tem de estar inteira.

    **Esta e a trava que importa**, e o motivo de ela existir merece registro.
    O estrago de 2026-08-03 deixou a linha assim:

        MSI_PARTY_BOOKING_MAKE = "/organize 'nome': Cria."Party Name\\": ...",

    Isso e **lexicamente valido** - as aspas fecham, as chaves batem - e so
    quebra na sintaxe (`'}' expected near 'Party'`). Um verificador de
    balanceamento passa batido; foi tentado e passou. O que pega e exigir que
    a linha inteira case com a forma esperada: campo, igual, uma string, e
    nada depois dela.
    """
    padrao = re.compile(r'^\s*(?:%s) = "%s",?$' % ('|'.join(campos), VALOR))
    procura = re.compile(r'\b(?:%s) = "' % '|'.join(campos))
    for i, linha in enumerate(texto.split('\n'), 1):
        linha = linha.rstrip('\r')
        if procura.search(linha) and not padrao.match(linha):
            raise Erro('%s linha %d ficou malformada, nada gravado: %r'
                       % (rotulo, i, linha[:110]))


def confere_blocos(antes, depois, rotulo):
    u"""Trava estrutural: a lista de chaves tem de sair igual a que entrou.

    Existe por causa do estrago acima. Substituicao dentro de literal Lua e
    frágil de um jeito que nao aparece no numero de bytes nem no relatorio -
    aparece so no cliente, como erro que nao cita o arquivo culpado. Comparar
    as chaves de primeiro nivel antes e depois pega o caso em que uma entrada
    engoliu a seguinte.
    """
    a = [c for c, _, _ in ptbr.blocos_lua(antes)]
    d = [c for c, _, _ in ptbr.blocos_lua(depois)]
    if a != d:
        raise Erro('%s: a estrutura mudou (%d blocos -> %d). Nada gravado.'
                   % (rotulo, len(a), len(d)))


# =================================================== msgstrid (rotulos de UI)

RE_MSGSTR = re.compile(r'(\t)(MSI_\w+)( = ")(' + VALOR + r')(")')


def parte_msgstrid(verificar):
    u"""MsgStrID: chave -> texto. Merge por NOME, sem risco de posicao.

    O `msgstring_br.lub` do bRO e a mesma tabela do `msgstring_kr.lub` daqui,
    com os mesmos 425 nomes e o texto em portugues. Como a chave e simbolica,
    nao existe o problema de deslocamento que o msgstringtable.txt tem.

    Os 37 nomes que so o kRO tem sao todos `MSI_HK_SKILLBAR2_x_y` - barras de
    atalho que o cliente do bRO nao chegou a ter. Como o bRO chama a barra 1-1
    de "Habilidade 1-1", esses 37 saem por analogia, trocando a palavra. E o
    unico texto deste projeto inteiro que nao foi importado.
    """
    fonte = ptbr.do_bro(r'data\luafiles514\lua files\msgstring_br.lub')
    tabela = ptbr.tabelas(fonte).get('MsgStrID')
    if not tabela:
        raise Erro('msgstring_br.lub nao definiu MsgStrID')
    print '    fonte: %d chaves no bRO' % len(tabela)

    mudou = 0
    for alvo in ptbr.caminhos('msgstrid'):
        if not os.path.exists(alvo):
            print '    %s nao existe, pulado' % os.path.basename(alvo)
            continue
        postos = [0, 0, 0]     # importados, por analogia, sem fonte

        def troca(m):
            chave, valor = m.group(2), m.group(4)
            novo = tabela.get(chave)
            if novo is not None:
                postos[0] += 1
                return (m.group(1) + chave + m.group(3) + aspas(pt(novo)) +
                        m.group(5))
            if 'Hotkey' in valor:
                postos[1] += 1
                return (m.group(1) + chave + m.group(3) +
                        valor.replace('Hotkey', 'Habilidade') + m.group(5))
            postos[2] += 1
            return m.group(0)

        antigo = le(alvo)
        novo = RE_MSGSTR.sub(troca, antigo)
        confere_linhas(novo, [r'MSI_\w+'], os.path.basename(alvo))
        if novo.count('\n') != antigo.count('\n'):
            raise Erro('%s mudou de numero de linhas' % os.path.basename(alvo))
        print '    %s: %d importados, %d por analogia, %d sem fonte' % (
            (os.path.basename(alvo),) + tuple(postos))
        mudou += grava(alvo, novo, verificar, 'msgstrid')
    return mudou


# ============================================ msgtable (mensagens de sistema)

def _assinatura(s):
    u"""O que sobrevive a traducao numa linha do msgstringtable.

    Numero, especificador de formato, codigo de cor, sigla em maiuscula e
    comando com barra atravessam qualquer idioma. Sao eles que ancoram o
    alinhamento entre a tabela inglesa e a portuguesa.
    """
    s = s.strip()
    cmd = re.match(r'^(/\w+)', s)
    chave = (tuple(re.findall(r'%[-0-9.*]*[a-zA-Z]', s)),
             tuple(re.findall(r'\^[0-9a-fA-F]{6}', s)),
             tuple(re.findall(r'\d+', s)),
             tuple(sorted(set(re.findall(r'\b[A-Z]{2,}\b', s)))),
             cmd.group(1) if cmd else '')
    return chave, any(chave)


# Corrida maxima de linhas sem ancora que ainda se aceita mapear. Acima disso a
# chance de haver uma insercao escondida no meio cresce, e a linha fica em
# ingles em vez de virar uma mensagem errada em portugues.
CORRIDA_MAX = 120


def _alinha(en, br):
    u"""indice no arquivo ingles -> indice no portugues.

    O msgstringtable.txt e o unico arquivo desta traducao **sem chave**: o
    cliente pede a linha pelo numero, e o numero e o que o exe de 2021 espera.
    Trocar o arquivo pelo do bRO inteiro entregaria a mensagem errada em todo
    lugar onde as duas tabelas divergem - e elas divergem: 4023 linhas contra
    4216.

    O alinhamento e por ancora. Linhas com assinatura forte (ver acima) sao
    casadas em ordem entre os dois arquivos; entre duas ancoras consecutivas,
    se a distancia for a mesma dos dois lados, a corrida inteira e mapeada.
    Se nao for, houve insercao ali e so as pontas sao aproveitadas.

    Sai por volta de 73% das linhas mapeadas. O resto fica em ingles de
    proposito - **linha nao mapeada e melhor que linha trocada.**
    """
    ae = [_assinatura(x) for x in en]
    ab = [_assinatura(x) for x in br]
    fe = [(i, k) for i, (k, forte) in enumerate(ae) if forte]
    fb = [(j, k) for j, (k, forte) in enumerate(ab) if forte]
    sm = difflib.SequenceMatcher(None, [k for _, k in fe], [k for _, k in fb],
                                 autojunk=False)
    ancoras = []
    for b in sm.get_matching_blocks():
        for t in range(b.size):
            ancoras.append((fe[b.a + t][0], fb[b.b + t][0]))
    mapa = {}
    for a in range(len(ancoras) - 1):
        i1, j1 = ancoras[a]
        i2, j2 = ancoras[a + 1]
        if i2 - i1 == j2 - j1 and i2 - i1 <= CORRIDA_MAX:
            for t in range(i2 - i1):
                mapa[i1 + t] = j1 + t
        else:
            mapa[i1] = j1
    if ancoras:
        mapa[ancoras[-1][0]] = ancoras[-1][1]
    # Guarda final: linha vazia so casa com linha vazia. Pega o caso em que a
    # corrida bate de tamanho mas o conteudo escorregou.
    return dict((i, j) for i, j in mapa.items()
                if bool(en[i].strip()) == bool(br[j].strip())), len(ancoras)


def parte_msgtable(verificar):
    u"""Ver `_alinha`. O arquivo do lado ingles e guardado a parte.

    Esta e a unica parte que **nao pode ler o proprio destino**: o alinhamento
    e por conteudo, e a primeira rodada muda o conteudo. Lendo o destino, a
    segunda rodada alinha portugues contra portugues, sai diferente da
    primeira, e a terceira sai diferente da segunda. Todas as outras partes
    casam por chave e nao tem esse problema.

    Por isso o ingles do ROenglishRE e congelado em `<alvo>.INGLES` na
    primeira gravacao, e e sempre dele que se parte. Apagar esse arquivo com o
    destino ja traduzido e o unico jeito de estragar esta parte.
    """
    alvo = ptbr.caminho('msgtable')
    base = alvo + '.INGLES'
    congelar = not os.path.exists(base)
    en = le(alvo if congelar else base).split('#\r\n')
    br = ptbr.do_bro(r'data\msgstringtable.txt').split('#\r\n')
    mapa, n_anc = _alinha(en, br)
    print '    %d linhas em ingles, %d no bRO, %d ancoras' % (len(en), len(br),
                                                              n_anc)
    print '    %d linhas mapeadas (%.1f%%); o resto fica em ingles' % (
        len(mapa), 100.0 * len(mapa) / len(en))
    saida = list(en)
    for i, j in mapa.items():
        saida[i] = pt(br[j])
    if congelar and not verificar:
        shutil.copy2(alvo, base)
        print '    ingles congelado em %s' % os.path.basename(base)
    return grava(alvo, '#\r\n'.join(saida), verificar, 'msgtable')


# ================================================================== quests

def _registros(dados):
    u"""(id, texto) de cada quest, na ordem do arquivo.

    O separador e a linha em branco, mas so quando a proxima linha comeca uma
    quest nova - o texto do bRO tem paragrafo em branco no meio da descricao, e
    dividir por linha em branco crua perde 118 registros calado.
    """
    saida = []
    for bloco in re.split(r'\r\n\r\n+(?=\d+#)', dados):
        limpo = bloco.strip('\r\n')
        if not limpo:
            continue
        m = re.match(r'^(?://[^\r\n]*\r\n)*(\d+)#', limpo)
        if m:
            saida.append((int(m.group(1)), limpo))
    return saida


def parte_quests(verificar):
    u"""questid2display.txt: titulo, descricao e resumo de cada quest."""
    alvo = ptbr.caminho('quests')
    fonte = dict(_registros(ptbr.do_bro(r'data\questid2display.txt')))
    en = _registros(le(alvo))
    print '    %d quests aqui, %d no bRO' % (len(en), len(fonte))

    trocadas = 0
    saida = []
    for qid, bloco in en:
        novo = fonte.get(qid)
        if novo is None:
            saida.append(bloco)
            continue
        # Comentario coreano do arquivo do bRO nao vem junto.
        novo = re.sub(r'^(?://[^\r\n]*\r\n)+', '', novo)
        saida.append(pt(novo))
        trocadas += 1
    print '    %d traduzidas, %d sem correspondente no bRO' % (
        trocadas, len(en) - trocadas)
    return grava(alvo, '\r\n\r\n'.join(saida) + '\r\n\r\n', verificar, 'quests')


# ==================================================== a janela de missoes

# **Nao e a mesma coisa que a parte `quests`, e a diferenca custou uma medicao.**
# A quest 5153 esta em ingles no `questid2display.txt` ("Refining tutorial (1)")
# e mesmo assim aparecia em coreano na janela: quem desenha o titulo e o texto e
# o global `QuestInfoList`, do `System\OngoingQuestInfoList_Sakray.lub`, e ele
# vence o `.txt`. O `questid2display.txt` e o fallback, nao a fonte.
#
# A estrutura vem do arquivo **coreano de 2021** e nao do ROenglishRE, e isso e
# deliberado: metade dos campos e referencia (sprite de NPC, nome de mapa, BMP
# de fundo, ID de item de recompensa), e a versao do ROenglishRE e de 2026. E a
# mesma razao do `parte_abas` - sprite que este exe nao conhece derruba a
# janela. So o texto e importado. Ver PENDENCIAS.md, `_sak` vs `_Sakray`: os
# alvos sao o `_Sakray` (o que o exe le) e o `_True` (de onde a copia saiu).

# A ordem em que os campos saem no arquivo gerado.
CAMPOS_ONGOING = ['Title', 'Description', 'Summary', 'IconName',
                  'CoolTimeQuest', 'NpcSpr', 'NpcNavi', 'NpcPosX', 'NpcPosY',
                  'RewardEXP', 'RewardJEXP', 'RewardItemList']
CAMPOS_RECO = ['Title', 'Summary', 'QuestInfo1', 'QuestInfo2', 'QuestInfo3',
               'IconName', 'BgName', 'NpcSpr', 'NpcNavi', 'NpcPosX', 'NpcPosY']

# O que e texto em cada um. O resto atravessa do arquivo coreano sem mudar.
TEXTO_ONGOING = ('Title', 'Description', 'Summary')
TEXTO_RECO = ('Title', 'Summary', 'QuestInfo1', 'QuestInfo2', 'QuestInfo3')

# Os campos que sempre saem como string, para o `confere_linhas`. `RewardEXP` e
# `RewardJEXP` ficam fora: uma quest do arquivo coreano guarda os dois como
# numero, e a trava exigiria aspas.
CAMPOS_ASPAS = ['Title', 'Summary', 'IconName', 'BgName', 'NpcSpr', 'NpcNavi']

CABECALHO_QUEST = (
    '-- Gerado por ferramentas/traduz_ptbr.py. Nao editar a mao.\r\n'
    '-- Estrutura: o %s coreano do instalador da Gravity de\r\n'
    '-- 2021-11-03, congelado no .COREANO ao lado. Texto: Ragnarok Brazil, e\r\n'
    '-- ROenglishRE no que o bRO nao tem.\r\n'
    '\r\n')


def _uma_linha(texto):
    u"""Uma string Lua nao pode conter quebra de linha crua, e o bRO contem.

    Trinta e sete descricoes do bRO vem no formato `titulo\\n\\t\\tcorpo` - lixo
    de formatacao que sobrou da fonte da Gravity. Foi o `luac -p` que apontou:
    `unfinished string near '"Sociedade de Monstros'`. As travas por linha nao
    pegam isso, porque a quebra de dentro da string faz o par de aspas cair em
    duas linhas e as duas ficam com contagem impar mas o `split` por `\\r\\n` nao
    as separa. Nos campos de lista a quebra virou item novo antes de chegar aqui
    (ver `_traduz_valor`); esta funcao e a rede de seguranca do resto.
    """
    return re.sub(r'[\r\n]+\t*', ' ', texto)


def _lua(valor, recuo):
    u"""Um valor lido do bytecode -> texto Lua.

    A virgula sobrando depois do ultimo campo e valida em Lua 5.1 (`{1,2,}`), e
    emitir sempre evita um caso especial em cada nivel.
    """
    if isinstance(valor, str):
        return '"%s"' % aspas(_uma_linha(valor))
    if isinstance(valor, bool):
        return 'true' if valor else 'false'
    if isinstance(valor, (int, long, float)):
        if float(valor) == int(valor):
            return str(int(valor))
        return repr(valor)
    if isinstance(valor, dict):
        if not valor:
            return '{}'
        seq = ptbr.lista(valor)
        if seq:                    # Description, QuestInfoN, RewardItemList
            dentro = recuo + '\t'
            return ('{\r\n'
                    + ',\r\n'.join(dentro + _lua(x, dentro) for x in seq)
                    + '\r\n' + recuo + '}')
        # Registro, do tipo `{ ItemID = 0, ItemNum = 1 }`.
        return '{ %s }' % ', '.join(
            '%s = %s' % (c, _lua(valor[c], recuo))
            for c in sorted(valor) if isinstance(c, str))
    raise Erro('nao sei escrever valor Lua de tipo %s' % type(valor).__name__)


def _bloco_quest(qid, dados, campos):
    linhas = ['\t[%d] = {' % qid]
    for campo in campos:
        if campo in dados:
            linhas.append('\t\t%s = %s,' % (campo, _lua(dados[campo], '\t\t')))
    linhas.append('\t},')
    return '\r\n'.join(linhas)


def _por_id(tabela, rotulo):
    u"""A tabela lida do bytecode, com a chave float virando int."""
    if not isinstance(tabela, dict):
        raise Erro('%s nao definiu a tabela esperada' % rotulo)
    return dict((int(c), v) for c, v in tabela.items()
                if isinstance(c, float) and isinstance(v, dict))


def _traduz_valor(valor):
    u"""O texto da fonte, em cp1252 e pronto para entrar no literal Lua.

    Campo de lista (`Description`, `QuestInfoN`) tem a quebra de linha crua
    promovida a item novo, que e o que ela queria dizer: as 37 descricoes
    `titulo\\n\\t\\tcorpo` do bRO passam a duas linhas na janela, como no bRO.
    """
    if not isinstance(valor, dict):
        return pt(valor)
    linhas = []
    for texto in ptbr.lista(valor):
        if not isinstance(texto, str):
            continue
        for pedaco in re.split(r'[\r\n]+\t*', pt(texto)):
            linhas.append(pedaco)
    return dict((float(i), t) for i, t in enumerate(linhas, 1))


def _texto_en(nome, campos):
    u"""Um `.lub` em texto puro do ROenglishRE -> {id: {campo: texto}}.

    So os campos de texto sao lidos. O `blocos_lua` nao entra em `Description =
    { ... }` porque lá dentro nao existe `[chave] =` - conferido, nenhuma string
    destes dois arquivos tem chave `{}` dentro.
    """
    caminho = os.path.join(ptbr.CLIENTE, 'SystemEN', nome)
    if not os.path.exists(caminho):
        raise Erro('nao achei %s' % caminho)
    dados = le(caminho)
    saida = {}
    for chave, ini, fim in ptbr.blocos_lua(dados):
        if not chave.isdigit():
            continue
        bloco = dados[ini:fim]
        entrada = {}
        for campo in campos:
            m = re.search(r'\b%s = "(%s)"' % (campo, VALOR), bloco)
            if m:
                entrada[campo] = m.group(1)
                continue
            m = re.search(r'\b%s = \{([^{}]*)\}' % campo, bloco)
            if m:
                itens = re.findall(r'"(%s)"' % VALOR, m.group(1))
                if itens:
                    entrada[campo] = dict((float(i), t)
                                          for i, t in enumerate(itens, 1))
        if entrada:
            saida[int(chave)] = entrada
    return saida


def _congela(alvo, verificar):
    u"""Guarda o bytecode coreano ao lado do alvo e devolve de onde ler.

    Sem isto a parte nao seria idempotente: a primeira rodada troca o bytecode
    por texto puro, e a segunda nao teria mais estrutura de onde partir. Mesma
    ideia do `.INGLES` do `parte_msgtable`. Apagar o `.COREANO` com o destino ja
    traduzido e o unico jeito de estragar esta parte - e o erro sai alto,
    `nao e bytecode Lua 5.1`.
    """
    base = alvo + '.COREANO'
    if os.path.exists(base):
        return base
    if verificar:
        return alvo
    shutil.copy2(alvo, base)
    print '    coreano congelado em %s' % os.path.basename(base)
    return base


def _gera_quests(global_lua, rotulo, base, bro, en, campos, campos_texto,
                 so_base):
    u"""Monta o arquivo. Devolve (texto, ids na ordem, contagem por fonte)."""
    ids = sorted(base) if so_base else sorted(set(base) | set(bro) | set(en))
    conta = {'bro': 0, 'en': 0, 'coreano': 0}
    blocos, saiu = [], []
    for qid in ids:
        dados = dict(base.get(qid) or {})
        fonte, origem = bro.get(qid), 'bro'
        if not fonte:
            fonte, origem = en.get(qid), 'en'
        if fonte:
            for campo in campos_texto:
                # Sai fora antes de entrar: se o bRO nao tem `Summary` para
                # esta quest, o coreano nao pode ficar no lugar.
                dados.pop(campo, None)
                if campo in fonte:
                    dados[campo] = _traduz_valor(fonte[campo])
            conta[origem] += 1
        else:
            conta['coreano'] += 1
        if not dados:
            continue
        blocos.append(_bloco_quest(qid, dados, campos))
        saiu.append(str(qid))
    texto = (CABECALHO_QUEST % rotulo
             + '%s = {}\r\n%s = {\r\n' % (global_lua, global_lua)
             + '\r\n'.join(blocos)
             + '\r\n}\r\n')
    return texto, saiu, conta


# O compilador Lua 5.1 que vem no ROenglishRE. E a **unica** trava que prova a
# sintaxe de verdade; as outras conferem forma de linha e balanceamento e
# passaram batido pelo caso da quebra de linha dentro da string. Se o repositorio
# do ROenglishRE nao estiver nesta maquina a conferencia e pulada com aviso - ela
# nao e requisito para gerar, so para ter certeza.
ROENGLISH = r'C:\Users\User\Downloads\ROenglishRE'
LUAC = os.path.join(ROENGLISH, 'Tools', 'luac.exe')


def _confere_luac(texto, rotulo):
    if not os.path.exists(LUAC):
        print '    (luac.exe nao encontrado, sintaxe nao conferida)'
        return
    import subprocess
    import tempfile
    fd, temporario = tempfile.mkstemp(suffix='.lua')
    try:
        os.write(fd, texto)
        os.close(fd)
        p = subprocess.Popen([LUAC, '-p', temporario],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        saida = p.communicate()[0]
        if p.returncode:
            # O caminho do temporario no meio da mensagem so atrapalha.
            saida = saida.replace(temporario, rotulo).strip()
            raise Erro('%s nao compila, nada gravado: %s' % (rotulo, saida))
        print '    luac -p: sintaxe conferida'
    finally:
        if os.path.exists(temporario):
            os.remove(temporario)


def _confere_quests(texto, ids, rotulo):
    confere_linhas(texto, CAMPOS_ASPAS, rotulo)
    # O `aspas()` nao deixa escapada nenhuma no arquivo gerado, entao toda
    # linha tem numero par de aspas. E a trava que pega o estrago de
    # 2026-08-03, que era lexicamente valido e so quebrava na sintaxe.
    for i, linha in enumerate(texto.split('\r\n'), 1):
        if linha.count('"') % 2:
            raise Erro('%s linha %d ficou com aspas impares, nada gravado: %r'
                       % (rotulo, i, linha[:110]))
    saiu = [c for c, _, _ in ptbr.blocos_lua(texto)]
    if saiu != ids:
        raise Erro('%s: a estrutura mudou (%d entradas -> %d). Nada gravado.'
                   % (rotulo, len(ids), len(saiu)))
    _confere_luac(texto, rotulo)


def _parte_quest_lub(nomes, global_lua, fonte_en, campos, campos_texto,
                     so_base, rotulo, verificar):
    u"""O corpo comum das duas partes. Os alvos recebem o mesmo conteudo."""
    alvos = [os.path.join(ptbr.CLIENTE, 'System', n) for n in nomes
             if os.path.exists(os.path.join(ptbr.CLIENTE, 'System', n))]
    if not alvos:
        raise Erro('nenhum de %s existe em System\\' % ', '.join(nomes))

    en = _texto_en(fonte_en, campos_texto)
    bro = _por_id(ptbr.tabelas_de(os.path.join(ptbr.BRO, 'System', nomes[0]))
                  .get(global_lua), 'o %s do bRO' % nomes[0])
    base = _por_id(ptbr.tabelas_de(_congela(alvos[0], verificar))
                   .get(global_lua), 'o %s daqui' % nomes[0])
    print '    %d entradas aqui, %d no bRO, %d no ROenglishRE' % (
        len(base), len(bro), len(en))

    texto, ids, conta = _gera_quests(global_lua, nomes[0], base, bro, en,
                                     campos, campos_texto, so_base)
    print '    %d em portugues (bRO), %d em ingles (ROenglishRE), %d sem' \
          ' fonte' % (conta['bro'], conta['en'], conta['coreano'])
    print '    %d entradas no arquivo gerado' % len(ids)
    _confere_quests(texto, ids, rotulo)

    mudou = 0
    for alvo in alvos:
        _congela(alvo, verificar)
        print '    %s:' % os.path.basename(alvo)
        mudou += grava(alvo, texto, verificar, rotulo)
    return mudou


def parte_questinfo(verificar):
    u"""OngoingQuestInfoList_*.lub: o titulo e o texto da janela de missoes."""
    return _parte_quest_lub(
        ['OngoingQuestInfoList_True.lub', 'OngoingQuestInfoList_Sakray.lub'],
        'QuestInfoList', 'OngoingQuests.lub',
        CAMPOS_ONGOING, TEXTO_ONGOING, False, 'questinfo', verificar)


def parte_questreco(verificar):
    u"""RecommendedQuestInfoList_*.lub: a aba RECOMENDADAS.

    Aqui, ao contrario do `questinfo`, **so as entradas do arquivo de 2021
    saem**. As 12 a mais do ROenglishRE trariam `BgName` e `IconName` que este
    GRF nao tem, e o fundo da pagina viria em branco. As chaves batem uma a uma
    (a 77 e a `바르문트의 바이오스피어` aqui e a "Varmundt's Biosphere" la), e a
    unica sem correspondente e a 11, `왕실 사냥 대회`, evento coreano que nem o
    bRO nem o ROenglishRE receberam - essa fica em coreano.
    """
    return _parte_quest_lub(
        ['RecommendedQuestInfoList_True.lub',
         'RecommendedQuestInfoList_Sakray.lub'],
        'RecommendedQuestInfoList', 'RecommendedQuests.lub',
        CAMPOS_RECO, TEXTO_RECO, True, 'questreco', verificar)


# ================================================================== cartas

def parte_cartas(verificar):
    u"""cardprefixnametable.txt: o prefixo que a carta poe no nome do item."""
    alvo = ptbr.caminho('cartas')
    fonte = {}
    for linha in ptbr.do_bro(r'data\cardprefixnametable.txt').split('\r\n'):
        p = linha.split('#')
        if len(p) >= 2 and p[0].strip().isdigit():
            fonte[int(p[0])] = p[1]
    print '    %d prefixos no bRO' % len(fonte)

    trocadas = 0
    saida = []
    for linha in le(alvo).split('\r\n'):
        p = linha.split('#')
        if len(p) >= 2 and p[0].strip().isdigit() and int(p[0]) in fonte:
            novo = fonte[int(p[0])]
            # '?' no arquivo do bRO e acento que ja se perdeu na origem; nesses
            # o ingles vale mais que um nome torto.
            if '?' not in novo:
                p[1] = pt(novo)
                linha = '#'.join(p)
                trocadas += 1
        saida.append(linha)
    print '    %d prefixos traduzidos' % trocadas
    return grava(alvo, '\r\n'.join(saida), verificar, 'cartas')


# ============================================================ mapas (nomes)

# Mapas que NOS rebatizamos, e que o bRO chama de outra coisa.
#
# Sem esta tabela nao ha como dar nome proprio a mapa: as duas metades do nome
# (o `mapnametable.txt` do canto do minimapa e o `mapInfo_*.lub` do letreiro de
# entrada) sao GERADAS deste modulo a partir do bRO, entao edicao a mao volta
# ao nome do bRO na proxima rodada, calada. Mesma familia do
# OngoingQuestInfoList e do CheckAttendance.lub - ver CLAUDE.md secao 9.
#
# So entra aqui mapa que MUDOU DE FUNCAO no nosso servidor. Mapa cujo nome do
# bRO ja serve nao entra: `auction_02` e a Ordem dos Exploradores porque o bRO
# ja o chama assim, e por isso nao esta nesta tabela.
NOSSOS_MAPAS = {
    # O antigo Salao do Leilao de Morroc/Prontera. No bRO e "Centro Comercial";
    # aqui virou a casa da Ordem em Prontera, alcancada pelo portal da praca
    # (npc/guerra/centro_da_ordem.txt). Renomeado a pedido em 2026-08-11.
    #
    # SO `displayName`: o bloco deste mapa no mapInfo_*.lub do cliente tem esse
    # campo e mais nenhum, e o `parte_mapinfo` so TROCA campo que ja existe --
    # nao acrescenta. Por um `mainTitle` aqui nao daria erro nem efeito; ficaria
    # inerte, que e pior que ausente. Mapa com letreiro de duas linhas (como a
    # Prontera, que tem subTitle) aceitaria os tres.
    'auction_01.rsw': {
        'displayName': u'Centro da Ordem',
    },

    # A arena de PvP, alcancada pela porta de prontera 147,180
    # (npc/guerra/arena_de_combate.txt). No kRO e uma das cinco "Salas"
    # numeradas de PvP e se chama "Sala Bussola"; aqui e A arena, a unica que
    # abrimos, e o nome de origem nao dizia isso a ninguem. Renomeada a pedido
    # em 2026-08-13.
    #
    # SAO DOIS CAMPOS, e os dois precisam estar aqui: o bloco deste mapa no
    # mapInfo_*.lub tem `displayName` -- o canto do minimapa, que e tambem o
    # que o mapnametable.txt recebe -- e um `signName.mainTitle`, o letreiro
    # grande da entrada. Era o letreiro que dizia "PvP Sala Bussola" ao
    # atravessar a porta. Trocar so um deixa metade do nome velho na tela.
    #
    # AS OUTRAS QUATRO SALAS NAO ENTRAM: pvp_n_2-5, _3-5, _4-5 e _5-5 tem o
    # mesmo nome de origem e continuam "PvP : Sala Bussola". Nenhuma tem porta
    # em lugar nenhum do servidor, entao ninguem as le.
    'pvp_n_1-5.rsw': {
        'displayName': u'Arena de Prontera',
        'mainTitle': u'Arena de Prontera',
    },
}


def _mapas_do_bro():
    u"""rsw -> {displayName, mainTitle, subTitle} em portugues.

    A fonte e o `mapInfo.lub`, **nao** o `mapnametable.txt` do GRF do bRO: o
    do GRF esta com o acento ja perdido na origem (335 '?' dentro dele, um por
    caractere acentuado que passou por uma conversao errada la na Gravity). O
    mapInfo esta intacto.

    O `NOSSOS_MAPAS` entra POR CIMA, no fim -- e o unico ponto por onde as duas
    metades do nome passam, entao sobrescrever aqui pega as duas.
    """
    caminho = os.path.join(ptbr.BRO, 'System', 'mapInfo.lub')
    tabela = ptbr.tabelas_de(caminho).get('mapTbl')
    if not tabela:
        raise Erro('mapInfo.lub do bRO nao definiu mapTbl')
    saida = {}
    for rsw, dados in tabela.items():
        if not isinstance(rsw, str) or not isinstance(dados, dict):
            continue
        placa = dados.get('signName') or {}
        saida[rsw.lower()] = {
            'displayName': dados.get('displayName'),
            'mainTitle': placa.get('mainTitle') if isinstance(placa, dict)
                         else None,
            'subTitle': placa.get('subTitle') if isinstance(placa, dict)
                        else None,
        }

    for rsw, nosso in NOSSOS_MAPAS.items():
        # O aviso nao e decoracao: se o bRO deixar de trazer o mapa, o override
        # continua funcionando (ele nao depende do de la) mas a justificativa
        # escrita na tabela -- "o bRO chama de X" -- deixou de ser conferivel.
        if rsw not in saida:
            print '    AVISO: %s esta em NOSSOS_MAPAS e nao no mapInfo do bRO' % rsw
        saida[rsw] = dict(nosso)
    return saida


def parte_mapas(verificar):
    u"""mapnametable.txt: o nome que aparece no canto do minimapa."""
    alvo = ptbr.caminho('mapas')
    fonte = _mapas_do_bro()
    print '    %d mapas no mapInfo do bRO' % len(fonte)

    trocadas = 0
    saida = []
    for linha in le(alvo).split('\r\n'):
        p = linha.split('#')
        if len(p) >= 2 and p[0].lower().endswith('.rsw'):
            nome = (fonte.get(p[0].lower()) or {}).get('displayName')
            if nome:
                p[1] = pt(nome)
                linha = '#'.join(p)
                trocadas += 1
        saida.append(linha)
    print '    %d nomes de mapa traduzidos' % trocadas
    return grava(alvo, '\r\n'.join(saida), verificar, 'mapas')


RE_CAMPO = re.compile(r'(\b(?:displayName|mainTitle|subTitle) = ")'
                      r'(' + VALOR + r')(")')


def parte_mapinfo(verificar):
    u"""mapInfo_*.lub: o letreiro grande que aparece ao entrar num mapa.

    Sao duas copias do mesmo arquivo (`_true` e `_sak`); o exe le a `_sak`, e a
    `_true` e mantida igual porque foi de la que a copia saiu. Ver a tabela de
    sufixos no PENDENCIAS.md - cada arquivo tem o seu e so o exe diz qual.
    """
    fonte = _mapas_do_bro()
    print '    %d mapas no mapInfo do bRO' % len(fonte)
    mudou = 0
    for nome in ('mapInfo_true.lub', 'mapInfo_sak.lub'):
        alvo = os.path.join(ptbr.CLIENTE, 'System', nome)
        if not os.path.exists(alvo):
            print '    %s nao existe, pulado' % nome
            continue
        dados = le(alvo)
        trocadas = [0]
        saida = []
        pos = 0
        for rsw, ini, fim in ptbr.blocos_lua(dados):
            chave = rsw.strip('"[] ').lower()
            info = fonte.get(chave)
            saida.append(dados[pos:ini])
            bloco = dados[ini:fim]
            if info:
                def troca(m, info=info, trocadas=trocadas):
                    novo = info.get(m.group(1).split(' =')[0])
                    if not novo:
                        return m.group(0)
                    trocadas[0] += 1
                    return m.group(1) + aspas(pt(novo)) + m.group(3)
                bloco = RE_CAMPO.sub(troca, bloco)
            saida.append(bloco)
            pos = fim
        saida.append(dados[pos:])
        print '    %s: %d campos traduzidos' % (nome, trocadas[0])
        confere_linhas(''.join(saida),
                       ['displayName', 'mainTitle', 'subTitle'], nome)
        confere_blocos(dados, ''.join(saida), nome)
        mudou += grava(alvo, ''.join(saida), verificar, 'mapinfo')
    return mudou


# ============================================================== habilidades

def _blocos_por_skid(dados):
    u"""[SKID.X] -> (inicio, fim) no texto."""
    saida = {}
    for chave, ini, fim in ptbr.blocos_lua(dados):
        if chave.startswith('SKID.'):
            saida[chave] = (ini, fim)
    return saida


RE_SKILLNAME = re.compile(r'(SkillName = )(\[\[.*?\]\]|"' + VALOR + r'")')


def parte_skills(verificar):
    u"""Nome e descricao de habilidade.

    O bRO guarda os dois em texto puro dentro do GRF (`.lua`, nao `.lub`), o
    que evita desmontar bytecode aqui.

    **Do `skillinfolist` so o `SkillName` e trocado.** O resto do bloco -
    MaxLv, SpAmount, AttackRange, `_NeedSkillList` - e estrutura, e a nossa e
    a que combina com o cliente de 2021: os arquivos daqui ja foram recortados
    por SKID justamente para nao referenciar habilidade de 4a classe, que este
    cliente nao conhece e que derruba a janela de habilidades inteira
    (PENDENCIAS.md, rodada de 2026-07-30 ~22:44). Importar o bloco inteiro
    desfaria esse recorte.

    Do `skilldescript` o bloco inteiro e trocado, porque ali **tudo** e texto.
    """
    mudou = 0

    # ---- nomes
    alvo = ptbr.caminho('skillnome')
    dados = le(alvo)
    fonte = ptbr.do_bro(r'data\luafiles514\lua files\skillinfoz'
                        r'\skillinfolist.lua')
    nomes = {}
    for chave, ini, fim in ptbr.blocos_lua(fonte):
        if not chave.startswith('SKID.'):
            continue
        m = RE_SKILLNAME.search(fonte[ini:fim])
        if m:
            nomes[chave] = m.group(2).strip('[]"')
    print '    %d nomes de habilidade no bRO' % len(nomes)

    trocadas = 0
    saida = []
    pos = 0
    for chave, ini, fim in ptbr.blocos_lua(dados):
        if chave not in nomes:
            continue
        bloco = dados[ini:fim]
        m = RE_SKILLNAME.search(bloco)
        if not m:
            continue
        novo = '%s"%s"' % (m.group(1), aspas(pt(nomes[chave])))
        saida.append(dados[pos:ini + m.start()])
        saida.append(novo)
        pos = ini + m.end()
        trocadas += 1
    saida.append(dados[pos:])
    print '    %d nomes traduzidos' % trocadas
    confere_linhas(''.join(saida), ['SkillName'], 'skillinfolist')
    confere_blocos(dados, ''.join(saida), 'skillinfolist')
    mudou += grava(alvo, ''.join(saida), verificar, 'skillnome')

    # ---- descricoes
    alvo = ptbr.caminho('skilldesc')
    dados = le(alvo)
    fonte = ptbr.do_bro(r'data\luafiles514\lua files\skillinfoz'
                        r'\skilldescript.lua')
    descr = {}
    for chave, ini, fim in ptbr.blocos_lua(fonte):
        if chave.startswith('SKID.'):
            descr[chave] = fonte[ini:fim]
    print '    %d descricoes de habilidade no bRO' % len(descr)

    trocadas = 0
    saida = []
    pos = 0
    for chave, ini, fim in ptbr.blocos_lua(dados):
        if chave not in descr:
            continue
        # Reescreve so a lista de strings, mantendo a indentacao daqui.
        linhas = re.findall(r'"((?:[^"\\]|\\.)*)"|\[\[(.*?)\]\]',
                            descr[chave], re.S)
        linhas = [a or b for a, b in linhas]
        if not linhas:
            continue
        corpo = ',\r\n'.join('\t\t"%s"' % aspas(pt(l)) for l in linhas)
        novo = '[%s] = {\r\n%s\r\n\t}' % (chave, corpo)
        saida.append(dados[pos:ini])
        saida.append(novo)
        pos = fim
        trocadas += 1
    saida.append(dados[pos:])
    print '    %d descricoes traduzidas' % trocadas
    confere_blocos(dados, ''.join(saida), 'skilldescript')
    mudou += grava(alvo, ''.join(saida), verificar, 'skilldesc')
    return mudou


# =================================================================== itens

# O `(?<![A-Za-z])` nao e enfeite: `unidentifiedDisplayName` **contem**
# `identifiedDisplayName`, e sem a trava o nome do item identificado iria parar
# no campo do nao-identificado, deixando o outro em ingles. Mesma coisa para a
# descricao.
RE_NOME_ID = re.compile(r'((?<![A-Za-z])identifiedDisplayName = ")'
                        r'(' + VALOR + r')(")')
RE_NOME_UN = re.compile(r'(unidentifiedDisplayName = ")(' + VALOR + r')(")')
RE_DESC_ID = re.compile(r'((?<![A-Za-z])identifiedDescriptionName = \{)'
                        r'(.*?)(\r\n\t\t\})', re.S)
RE_DESC_UN = re.compile(r'(unidentifiedDescriptionName = \{ )'
                        r'([^\r\n]*?)( \},)')


def parte_itens(verificar):
    u"""itemInfo.lua: nome e descricao de cada item.

    So **texto** e trocado. `identifiedResourceName` fica como esta, e isso e
    obrigatorio: aquele campo e nome de arquivo dentro do GRF, em bytes CP949
    coreanos, e no bRO ele vem em UTF-8. Reescrever com o valor do bRO faria o
    cliente procurar arquivo que nao existe e o item perderia o icone - a
    mesma armadilha que o `instala_item.py` documenta.

    Itens nossos (faixa 30000-30999) nao existem no bRO e atravessam intactos.
    """
    alvo = ptbr.caminho('itens')
    dados = le(alvo)
    fonte = _itens_do_bro()
    print '    %d itens no bRO' % len(fonte)

    nomes = [0]
    descs = [0]
    saida = []
    pos = 0
    for chave, ini, fim in ptbr.blocos_lua(dados):
        if not chave.isdigit():
            continue
        info = fonte.get(int(chave))
        if not info:
            continue
        bloco = dados[ini:fim]
        novo = bloco

        nome = info.get('identifiedDisplayName')
        if nome:
            novo, n = RE_NOME_ID.subn(
                lambda m: m.group(1) + aspas(pt(nome)) + m.group(3), novo, 1)
            nomes[0] += n
        nome_un = (info.get('unidentifiedDisplayName') or
                   info.get('identifiedDisplayName'))
        if nome_un:
            novo = RE_NOME_UN.sub(
                lambda m: m.group(1) + aspas(pt(nome_un)) + m.group(3), novo, 1)

        linhas = [l for l in ptbr.lista(info.get('identifiedDescriptionName'))
                  if isinstance(l, str)]
        if linhas:
            corpo = ',\r\n'.join('\t\t\t"%s"' % aspas(pt(l)) for l in linhas)
            novo, n = RE_DESC_ID.subn(
                lambda m: m.group(1) + '\r\n' + corpo + m.group(3), novo, 1)
            descs[0] += n

        # A descricao do item nao-identificado e uma linha so ("Pode ser
        # identificado com uma Lupa"), e ficaria em ingles no meio do resto.
        linhas = [l for l in ptbr.lista(info.get('unidentifiedDescriptionName'))
                  if isinstance(l, str) and l.strip()]
        if linhas:
            corpo = ', '.join('"%s"' % aspas(pt(l)) for l in linhas)
            novo = RE_DESC_UN.sub(
                lambda m: m.group(1) + corpo + m.group(3), novo, 1)

        if novo == bloco:
            continue
        saida.append(dados[pos:ini])
        saida.append(novo)
        pos = fim
    saida.append(dados[pos:])
    print '    %d nomes e %d descricoes traduzidos' % (nomes[0], descs[0])
    confere_linhas(''.join(saida),
                   ['identifiedDisplayName', 'unidentifiedDisplayName'],
                   'itemInfo.lua')
    confere_blocos(dados, ''.join(saida), 'itemInfo.lua')
    return grava(alvo, ''.join(saida), verificar, 'itens')


def _itens_do_bro():
    caminho = os.path.join(ptbr.BRO, 'System', 'iteminfo_new.lub')
    if not os.path.exists(caminho):
        raise Erro('nao achei %s' % caminho)
    tabela = ptbr.tabelas_de(caminho)
    # O global tem nome diferente conforme a versao; pega a maior tabela
    # indexada por numero, que e sempre a de itens.
    melhor = None
    for valor in tabela.values():
        if not isinstance(valor, dict):
            continue
        if melhor is None or len(valor) > len(melhor):
            melhor = valor
    saida = {}
    for chave, valor in (melhor or {}).items():
        if isinstance(chave, float) and isinstance(valor, dict):
            saida[int(chave)] = valor
    return saida


# ============================================================== conquistas

def parte_conquistas(verificar):
    u"""achievement_list.lub: o modal de conquista.

    Aqui e troca de arquivo, nao merge: o `achievement_list.lub` e **bytecode
    com codigo dentro** (cada conquista carrega a funcao que monta o texto de
    progresso), nao uma tabela de texto que se possa costurar linha a linha.

    Trocar e seguro porque o nosso hoje e o **coreano do instalador de 2021** -
    esta e a unica parte da traducao que nao tinha ingles para preservar. Os
    dois arquivos declaram os mesmos cinco globais e o do bRO tem 349 das 361
    conquistas do nosso. As 12 que faltam (128038-128043, 128050-128052,
    129021, 130005, 200032) passam de coreano para vazio; as outras 349 passam
    de coreano para portugues.
    """
    origem = os.path.join(ptbr.BRO, 'System', 'achievement_list.lub')
    if not os.path.exists(origem):
        raise Erro('nao achei %s' % origem)
    novo = le(origem)

    mudou = 0
    for nome in ('achievement_list.lub',):
        alvo = os.path.join(ptbr.CLIENTE, 'System', nome)
        if not os.path.exists(alvo):
            print '    %s nao existe aqui, pulado' % nome
            continue
        print '    %s: %d -> %d bytes, vindo do bRO' % (
            nome, os.path.getsize(alvo), len(novo))
        mudou += grava(alvo, novo, verificar, 'conquistas')
    return mudou


# ========================================= abas do modal de habilidade

# Os titulos das abas da janela de habilidades. A esquerda, os bytes CP949 que
# estao no `skilltreeview.lub` do NOSSO GRF; a direita, a traducao.
#
# **Tudo em ASCII, e nao por preguica.** Estes rotulos vivem numa aba
# estreita, e nenhum deles precisa de acento no vocabulario do bRO -
# "Aprendiz", "Doram", "Invocador", "Espiritualista", "Transcendental" saem
# todos limpos. O `-` substitui o ponto-medio coreano (`\xa1\xa4`).
#
# O vocabulario foi conferido no proprio bRO: "Doram", "Invocador" e
# "Espiritualista" aparecem no `msgstringtable.txt` dele, e "Aprendiz" e o
# nome que o `map_msg_por.conf` da ao Novice. O bRO chama as abas dele so de
# "1a"/"2a"/"3a"; aqui ha nove abas, entao o padrao dele foi mantido e o resto
# qualificado.
#
# **TETO DE 7 CARACTERES, e ele e o que faz a janela funcionar.** A aba desta
# janela e escrita na VERTICAL, uma letra embaixo da outra, numa coluna de
# ~13px por letra - entao o comprimento do rotulo nao gasta largura, gasta
# ALTURA, e a altura e dividida entre todas as abas do personagem. Com
# "Aprendiz-1a" (11) + "2a-Transcend." (13) as duas primeiras abas de um Sura
# comiam a coluna inteira e a terceira ("3a") ficava cortada ao meio, fora do
# alcance do clique: a habilidade concedida por equipamento (Protecao Arcana,
# da Fada do Eden +11) estava la dentro e era **inalcancavel**. Achado em
# 2026-08-11. O `checa_abas` abaixo faz o teto valer - comentario nao e trava.
LIMITE_ABA = 7

ABAS = [
    ('\xb3\xeb\xba\xf1\xbd\xba\xa1\xa41\xc2\xf7\xc1\xf7\xbe\xf7', 'Apr-1a'),
    ('2\xc2\xf7\xa1\xa4\xc0\xfc\xbd\xc2\xc1\xf7\xbe\xf7', '2a-Tr.'),
    ('3\xc2\xf7\xc1\xf7\xbe\xf7', '3a'),
    ('4\xc2\xf7\xc1\xf7\xbe\xf7', '4a'),
    ('NV\xa1\xa4EX1', 'NV-EX1'),
    ('\xbb\xf3\xc0\xa7EX1', 'Sup.EX1'),
    ('\xbb\xf3\xc0\xa7EX2', 'Sup.EX2'),
    ('\xb5\xb5\xb6\xf7\xc1\xb7\xa1\xa4\xbc\xd2\xc8\xaf\xbb\xe7', 'Doram'),
    ('\xc8\xa5\xb7\xc9\xbb\xe7', 'Espir.'),
]


def checa_abas():
    u"""Nenhum rotulo de aba pode passar de LIMITE_ABA caracteres."""
    longos = [novo for _, novo in ABAS if len(novo) > LIMITE_ABA]
    if longos:
        raise Erro('rotulo de aba acima de %d caracteres: %s'
                   % (LIMITE_ABA, ', '.join(longos)))

SKILLTREEVIEW = os.path.join('data', 'luafiles514', 'lua files', 'skillinfoz',
                             'skilltreeview.lub')


def parte_abas(verificar):
    u"""Os titulos das abas da janela de habilidades.

    Este e o unico arquivo que **nao vem do bRO**: a fonte e o NOSSO GRF, o da
    Gravity de 2021-11-03, e so o texto e traduzido. O motivo esta em
    PENDENCIAS.md, na rodada em que a janela de habilidades derrubava o
    cliente: o `skilltreeview.lub` e a grade `classe -> habilidade`, e a versao
    do ROenglishRE (2025) cita habilidade de 4a classe que este exe nao
    conhece. Por isso ela foi para o backup em definitivo, e o GRF voltou a
    servir a versao coreana - que e a que o jogador ve hoje.

    **A nota que dizia que este arquivo "nao tem texto para traduzir" estava
    errada.** Ele tem nove strings, e sao exatamente os titulos das abas.

    A troca e feita direto no bytecode. Da certo porque o chunk Lua 5.1 nao
    tem offset absoluto nenhum - ver `ptbr.troca_constante`. O resultado e
    reaberto pelo leitor de bytecode antes de gravar; se a estrutura nao
    voltar identica, nada e escrito.
    """
    checa_abas()
    alvo = os.path.join(ptbr.CLIENTE, SKILLTREEVIEW)
    dados = ptbr.do_nosso(r'data\luafiles514\lua files\skillinfoz'
                          r'\skilltreeview.lub')
    antes = ptbr.tabelas(dados).get('SKILL_TREEVIEW_FOR_JOB')
    if not antes:
        raise Erro('skilltreeview.lub do nosso GRF nao definiu '
                   'SKILL_TREEVIEW_FOR_JOB')
    print '    fonte: nosso GRF, %d bytes, %d classes' % (len(dados),
                                                          len(antes))

    trocadas = 0
    for velho, novo in ABAS:
        dados, n = ptbr.troca_constante(dados, velho, ptbr.codifica(
            novo.decode('ascii')))
        if not n:
            print '    AVISO: aba %r nao encontrada' % velho
        trocadas += n
    print '    %d titulos de aba traduzidos' % trocadas

    depois = ptbr.tabelas(dados).get('SKILL_TREEVIEW_FOR_JOB')
    if not depois or len(depois) != len(antes):
        raise Erro('a tabela mudou de forma depois da troca; nada gravado')

    if not os.path.exists(alvo):
        if verificar:
            print '    --verificar: criaria %s' % alvo
            return 0
        pasta = os.path.dirname(alvo)
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
        fh = open(alvo, 'wb')
        fh.write(dados)
        fh.close()
        print '    criado: %s' % os.path.basename(alvo)
        return 1
    return grava(alvo, dados, verificar, 'abas')


# ================================================== monstros (lado servidor)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOB_DB_RA = os.path.join(REPO, 'rathena', 'db', 're', 'mob_db.yml')
MOB_DB_NOSSO = os.path.join(REPO, 'rathena', 'db', 'guerra', 'mob_db.yml')

CABECA_MOB = u'''\
###########################################################################
# Guerra do Emperium - Nomes de monstro em portugues
###########################################################################
#
# GERADO por ferramentas/traduz_ptbr.py monstros. Nao editar a mao: a
# proxima rodada reescreve o arquivo inteiro.
#
# Este e o unico pedaco da traducao que fica do lado do SERVIDOR. O nome que
# flutua sobre o monstro nao vem de tabela do cliente - o map-server manda a
# string pronta, tirada do campo `JapaneseName` do mob_db (src/map/mob.cpp,
# `memcpy(md->name, md->db->jname...)`; o campo `Name` fica so para script e
# para o @monster).
#
# Fonte: navi_mob_br.lub, dentro do GRF do Ragnarok Brazil desta maquina.
# E a tabela que a navegacao do cliente do bRO usa para dizer "o monstro X
# esta no mapa Y", e ela carrega o nome de sprite (AegisName) junto com o
# nome em portugues. Foi por esse par que os IDs daqui foram resolvidos - o
# ID de monstro nao aparece nela.
#
# Cobertura: %(cobertos)d dos %(total)d monstros do rAthena. O que falta e
# monstro que nao aparece na navegacao do bRO (evento, MVP retirado, mob de
# instancia nova) e continua com o nome em ingles.
#
# Encoding: Latin-1 (ISO-8859-1), o mesmo dos map_msg_*.conf do rAthena. O
# nome vai como bytes crus para o cliente, que desenha em cp1252 por causa
# do patch AlwaysAscii. Gravar em UTF-8 faria cada acento virar dois
# caracteres na tela.
#
###########################################################################

Header:
  Type: MOB_DB
  Version: 5

Body:
'''


def _aegis_do_rathena():
    u"""AegisName -> Id, lido do mob_db do rAthena."""
    pares = re.findall(r'^  - Id: (\d+)\r?\n    AegisName: (\S+)',
                       le(MOB_DB_RA), re.M)
    return [(int(i), a) for i, a in pares]


def parte_monstros(verificar):
    u"""db/guerra/mob_db.yml: o nome que flutua sobre o monstro.

    So o `JapaneseName` e escrito. O `Name` fica em ingles de proposito: e
    por ele que `@monster`, `@mobinfo` e os scripts do rAthena procuram o
    bicho, e traduzir quebraria script de terceiro sem avisar.

    Entrada parcial e legitima no rAthena: o leitor de YAML so exige
    `AegisName`/`Name` quando o ID **nao existe** ainda
    (src/map/mob.cpp, MobDatabase::parseBodyNode); para ID ja conhecido cada
    campo e opcional e o que vier sobrescreve.
    """
    bruto = ptbr.do_bro(r'data\luafiles514\lua files\navigation'
                        r'\navi_mob_br.lub')
    tabela = ptbr.tabelas(bruto).get('Navi_Mob')
    if not tabela:
        raise Erro('navi_mob_br.lub nao definiu Navi_Mob')
    # Cada linha e {1=mapa, 2=?, 3=?, 4=?, 5=nome PT, 6=AegisName, 7=nivel}.
    # O mesmo monstro aparece uma vez por mapa; o primeiro nome vale.
    nomes = {}
    for linha in tabela.values():
        if isinstance(linha, dict) and 5.0 in linha and 6.0 in linha:
            nomes.setdefault(linha[6.0], linha[5.0])
    print '    %d nomes de monstro no bRO' % len(nomes)

    todos = _aegis_do_rathena()
    corpo = []
    for mid, aegis in todos:
        nome = nomes.get(aegis)
        if not nome:
            continue
        corpo.append('  - Id: %d\n    JapaneseName: "%s"\n'
                     % (mid, aspas(pt(nome))))
    print '    %d dos %d monstros do rAthena ganham nome PT' % (len(corpo),
                                                                len(todos))

    texto = (codifica(CABECA_MOB % {'cobertos': len(corpo),
                                    'total': len(todos)}) + ''.join(corpo))
    if not os.path.exists(MOB_DB_NOSSO):
        if verificar:
            print '    --verificar: criaria %s (%d bytes)' % (MOB_DB_NOSSO,
                                                              len(texto))
            return 0
        fh = open(MOB_DB_NOSSO, 'wb')
        fh.write(texto)
        fh.close()
        print '    criado: %s' % MOB_DB_NOSSO
        return 1
    return grava(MOB_DB_NOSSO, texto, verificar, 'monstros')


# ==================================================================== driver

# ============================================ encantamentos (opcao aleatoria)

# O destino e um arquivo que NAO existe em `cliente\\data` - ele mora so dentro
# do GRF. Criar o solto e o que faz o DataFolderFirst preferi-lo.
ENC_ALVO = os.path.join('data', 'luafiles514', 'lua files', 'datainfo',
                        'addrandomoptionnametable.lub')
ENC_NO_GRF = ('data\\luafiles514\\lua files\\datainfo'
              '\\addrandomoptionnametable.lub')
ENC_EN = os.path.join(ROENGLISH, 'Translation', 'Renewal', 'data',
                      'luafiles514', 'lua files', 'datainfo',
                      'addrandomoptionnametable.lub')

# `[EnumVAR.VAR_MAXHPAMOUNT[1]] = "MaxHP +%d"` - a forma do arquivo do
# ROenglishRE, que e texto puro. O VALOR respeita escapada, pelo mesmo motivo
# de sempre.
RE_ENC = re.compile(r'\[(EnumVAR\.[A-Za-z0-9_]+\[1\])\]\s*=\s*"(' + VALOR + ')"')

CABECA_ENC = '''\
-- Guerra do Emperium - o efeito do encantamento em portugues
--
-- GERADO por ferramentas/traduz_ptbr.py encantamentos. Nao editar a mao: a
-- proxima rodada reescreve o arquivo inteiro.
--
-- Este arquivo NAO existe solto no cliente de fabrica - ele vive dentro do
-- data.grf, em coreano. O que o faz valer e o DataFolderFirst, que deixa o
-- disco vencer o GRF.
--
-- As CHAVES sao as do NOSSO GRF (Gravity, 2021-11-03) e nao as do bRO nem as
-- do ROenglishRE, e isso e a trava: `EnumVAR.<X>` que este exe nao conhecesse
-- viraria `nil`, e indexar `nil[1]` derruba a tabela INTEIRA - a janela de
-- item voltaria a nao mostrar encantamento nenhum.
--
-- O TEXTO vem do bRO onde ele tem (%(pt)d de %(total)d) e do ROenglishRE no
-- resto (%(en)d) - as siglas de 4a classe (POW, SPL, STA, WIS, CON, CRT,
-- P.ATK, S.MATK, RES, MRES, H.PLUS, C.RATE), que sao iguais nos dois idiomas
-- porque o bRO daquela epoca ainda nao tinha 4a classe.
--
-- Gravado em cp1252, como todo texto que o jogo le. O cliente so le isto na
-- INICIALIZACAO: depois de gerar, fechar e reabrir.

NameTable_VAR = {
'''


def _enc_do_grf(caminho, rotulo):
    u"""GRF -> {'EnumVAR.X[1]': bytes do texto}."""
    import grf as _grf
    if not os.path.exists(caminho):
        raise Erro('nao achei o GRF em %s' % caminho)
    dados = _grf.Grf(caminho).read(ENC_NO_GRF)
    tabela = ptbr.tabelas(dados).get('NameTable_VAR')
    if not tabela:
        raise Erro('%s nao definiu NameTable_VAR' % rotulo)
    # A chave e um Sym: `EnumVAR.VAR_MAXHPAMOUNT[1]`. Sem o ramo de Sym
    # indexado por numero no ptbr._interpreta a tabela inteira colapsaria numa
    # entrada so, com chave None - e sem dar erro nenhum.
    return dict((k.nome, v) for k, v in tabela.items()
                if isinstance(k, ptbr.Sym))


def parte_encantamentos(verificar):
    u"""O texto do encantamento (opcao aleatoria) na janela do item.

    E o que aparece nas duas linhas abaixo da descricao de uma arma ilusional,
    e vinha em COREANO: o `addrandomoptionnametable.lub` deste cliente e o
    original da Gravity, e nunca houve arquivo solto para vencê-lo.

    As tres fontes, e a ordem entre elas:

      1. o NOSSO GRF da as CHAVES - e so ele pode dar. A chave e
         `EnumVAR.<X>[1]`, resolvida em tempo de execucao contra o
         `enumvar.lub` deste exe; chave que ele nao conhecesse seria `nil`, e
         `nil[1]` derruba a tabela toda, calado.
      2. o bRO da o TEXTO em portugues, casado por chave (regra 4.5).
      3. o ROenglishRE preenche o que o bRO nao tem - as siglas de 4a classe.

    Nada fica em coreano: 239 + 13 = 252, medido em 2026-08-18.
    """
    nosso = _enc_do_grf(ptbr.NOSSO_GRF, 'nosso GRF')
    bro = _enc_do_grf(ptbr.BRO_GRF, 'GRF do bRO')

    ingles = {}
    if os.path.exists(ENC_EN):
        for m in RE_ENC.finditer(le(ENC_EN)):
            ingles[m.group(1)] = m.group(2)
    else:
        print '    AVISO: ROenglishRE ausente; o que o bRO nao tiver fica em coreano'

    print '    nosso GRF: %d chaves | bRO: %d | ROenglishRE: %d' % (
        len(nosso), len(bro), len(ingles))

    linhas = []
    de_pt = de_en = de_kr = 0
    for chave in sorted(nosso):
        if chave in bro:
            valor = ptbr.pt(bro[chave])
            de_pt += 1
        elif chave in ingles:
            valor = ingles[chave]
            de_en += 1
        else:
            # Sem fonte: fica como esta hoje, que e o coreano do nosso GRF.
            valor = nosso[chave]
            de_kr += 1
        linhas.append('\t[%s] = "%s",' % (chave, aspas(valor)))

    print '    %d do bRO, %d do ROenglishRE, %d sem fonte (coreano)' % (
        de_pt, de_en, de_kr)

    # A ultima linha nao leva virgula: Lua aceita, mas o arquivo do
    # ROenglishRE tambem nao leva, e o diff com ele fica legivel.
    linhas[-1] = linhas[-1].rstrip(',')
    texto = (CABECA_ENC % {'pt': de_pt, 'en': de_en,
                           'total': len(nosso)}
             + '\n'.join(linhas) + '\n}\n')

    _confere_luac(texto, 'addrandomoptionnametable.lub')

    alvo = os.path.join(ptbr.CLIENTE, ENC_ALVO)
    if not os.path.exists(alvo):
        if verificar:
            print '    --verificar: criaria %s (%d bytes)' % (alvo, len(texto))
            return 0
        pasta = os.path.dirname(alvo)
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
        fh = open(alvo, 'wb')
        fh.write(texto)
        fh.close()
        print '    criado: %s' % os.path.basename(alvo)
        return 1
    return grava(alvo, texto, verificar, 'encantamentos')


PARTES = [
    ('msgstrid',   parte_msgstrid,   'rotulos de janela e de botao'),
    ('msgtable',   parte_msgtable,   'mensagens de sistema e de erro'),
    ('itens',      parte_itens,      'nome e descricao de item'),
    ('skills',     parte_skills,     'nome e descricao de habilidade'),
    ('quests',     parte_quests,     'titulo e texto do diario de quests'),
    ('questinfo',  parte_questinfo,  'a janela de missoes'),
    ('questreco',  parte_questreco,  'a aba RECOMENDADAS da janela de missoes'),
    ('conquistas', parte_conquistas, 'o modal de conquista'),
    ('mapas',      parte_mapas,      'nome do mapa no minimapa'),
    ('mapinfo',    parte_mapinfo,    'o letreiro ao entrar no mapa'),
    ('cartas',     parte_cartas,     'o prefixo que a carta poe no nome'),
    ('abas',       parte_abas,       'as abas da janela de habilidades'),
    ('monstros',   parte_monstros,   'o nome que flutua sobre o monstro'),
    ('encantamentos', parte_encantamentos,
     'o efeito do encantamento na janela do item'),
]


def main(argv):
    verificar = '--verificar' in argv
    ptbr.SEM_ACENTO[0] = '--sem-acento' in argv
    pedidas = [a for a in argv if not a.startswith('--')]
    if not pedidas:
        print __doc__
        print 'partes: %s' % ' '.join(p[0] for p in PARTES)
        return 1
    if 'tudo' in pedidas:
        escolhidas = PARTES
    else:
        conhecidas = dict((p[0], p) for p in PARTES)
        faltando = [p for p in pedidas if p not in conhecidas]
        if faltando:
            print 'parte desconhecida: %s' % ', '.join(faltando)
            print 'conhecidas: %s' % ' '.join(p[0] for p in PARTES)
            return 1
        escolhidas = [conhecidas[p] for p in pedidas]

    print 'cliente: %s' % ptbr.CLIENTE
    print 'fonte:   %s' % ptbr.BRO
    print 'acento:  %s' % ('NAO (--sem-acento)' if ptbr.SEM_ACENTO[0]
                           else 'sim, cp1252')
    print

    mudaram = 0
    for nome, funcao, desc in escolhidas:
        print '[%s] %s' % (nome, desc)
        try:
            mudaram += funcao(verificar)
        except Erro as e:
            print '    ERRO: %s' % e
        print

    if verificar:
        print '--verificar: nada foi gravado.'
    elif mudaram:
        print 'Feche e reabra o cliente - ele le estes arquivos so na'
        print 'inicializacao, e nenhum @reload do servidor os alcanca.'
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
