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
    conquistas   o modal de conquista              System\\achievement_list.lub
    mapas        nome do mapa na minimapa          System\\mapInfo.lub
    mapinfo      o letreiro ao entrar no mapa      System\\mapInfo.lub
    cartas       o prefixo que a carta poe no nome data\\cardprefixnametable.txt

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

def _mapas_do_bro():
    u"""rsw -> {displayName, mainTitle, subTitle} em portugues.

    A fonte e o `mapInfo.lub`, **nao** o `mapnametable.txt` do GRF do bRO: o
    do GRF esta com o acento ja perdido na origem (335 '?' dentro dele, um por
    caractere acentuado que passou por uma conversao errada la na Gravity). O
    mapInfo esta intacto.
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
ABAS = [
    ('\xb3\xeb\xba\xf1\xbd\xba\xa1\xa41\xc2\xf7\xc1\xf7\xbe\xf7', 'Aprendiz-1a'),
    ('2\xc2\xf7\xa1\xa4\xc0\xfc\xbd\xc2\xc1\xf7\xbe\xf7', '2a-Transcend.'),
    ('3\xc2\xf7\xc1\xf7\xbe\xf7', '3a'),
    ('4\xc2\xf7\xc1\xf7\xbe\xf7', '4a'),
    ('NV\xa1\xa4EX1', 'NV-EX1'),
    ('\xbb\xf3\xc0\xa7EX1', 'Sup.EX1'),
    ('\xbb\xf3\xc0\xa7EX2', 'Sup.EX2'),
    ('\xb5\xb5\xb6\xf7\xc1\xb7\xa1\xa4\xbc\xd2\xc8\xaf\xbb\xe7', 'Doram-Invocador'),
    ('\xc8\xa5\xb7\xc9\xbb\xe7', 'Espiritualista'),
]

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

PARTES = [
    ('msgstrid',   parte_msgstrid,   'rotulos de janela e de botao'),
    ('msgtable',   parte_msgtable,   'mensagens de sistema e de erro'),
    ('itens',      parte_itens,      'nome e descricao de item'),
    ('skills',     parte_skills,     'nome e descricao de habilidade'),
    ('quests',     parte_quests,     'titulo e texto do diario de quests'),
    ('conquistas', parte_conquistas, 'o modal de conquista'),
    ('mapas',      parte_mapas,      'nome do mapa no minimapa'),
    ('mapinfo',    parte_mapinfo,    'o letreiro ao entrar no mapa'),
    ('cartas',     parte_cartas,     'o prefixo que a carta poe no nome'),
    ('abas',       parte_abas,       'as abas da janela de habilidades'),
    ('monstros',   parte_monstros,   'o nome que flutua sobre o monstro'),
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
