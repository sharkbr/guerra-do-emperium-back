# -*- coding: utf-8 -*-
u"""Onde um item existe, onde ele falta, e o que quebra se o ID for trocado.

    python estado_item.py --id 19455              # estado de um item
    python estado_item.py --id 19024,19455        # de varios
    python estado_item.py --loja Ocleiro          # de uma loja inteira
    python estado_item.py --troca 19024:19455     # ANALISA a troca (a trava)
    python estado_item.py --troca 19024:19455 --aplicar   # e executa o que da

Nasceu em 2026-08-05, depois de uma troca de quatro itens na loja do Ocleiro
(npc/guerra/mercado_contemporaneo.txt) em que a EDICAO foi o barato e a
DESCOBERTA foi o caro. O trabalho de verdade foi responder duas perguntas que
nenhuma ferramenta respondia:

  1. "este ID existe onde?" - a resposta mora em QUATRO tabelas diferentes, e
     faltar em cada uma quebra de um jeito diferente;
  2. "trocar este ID por aquele derruba alguma coisa?" - derrubava tres
     conjuntos, e conjunto que nao fecha NAO DA ERRO.

--------------------------------------------------------------- as quatro tabelas

O mesmo item precisa estar em quatro lugares, e cada ausencia tem um sintoma
proprio. Confundi-los custa tempo, porque tres deles nao dao erro nenhum:

  | tabela                        | quem le   | falta = o jogador ve            |
  |-------------------------------|-----------|---------------------------------|
  | db/re/item_db_*.yml           | servidor  | `@item` falha, loja nao abre     |
  | db/guerra/item_db.yml         | servidor  | (nosso, para o que o vendor      |
  |                               |           |  nao tem - ver o cabecalho de la)|
  | cliente SystemEN/.../         | cliente   | item SEM NOME e SEM ICONE,       |
  |   itemInfo.lua                |           | calado                           |
  | arte no GRF/data (8 arquivos) | cliente   | caixa modal de erro ao equipar   |

E a quinta, que nao e tabela de item mas manda no resultado: o
`iteminfo_new.lub` do bRO, que e de onde se TRAZ o que falta nas de cima. Ver
o ACORDO no PENDENCIAS.md - quando falta algo, traz-se de la em vez de
inventar.

Este script nao grava nada nessas tabelas por conta propria: ele diz o que
falta e imprime o comando exato que resolve. Com `--aplicar` ele chama esses
comandos, mas so os que ja existem e ja sao idempotentes.

------------------------------------------------------------- a trava de conjunto

E a razao de o `--troca` existir, e o unico pedaco daqui que impede um bug em
vez de so descrever o mundo.

Conjunto no rAthena e casado por **AegisName**, nao por familia. A versao com
cova de um chapeu e OUTRO item - `Protect_Feathers_` nao e `Protect_Feathers`.
Entao trocar o ID de uma loja pela versao com cova DERRUBA todo conjunto que
citava a versao sem cova. E a perda e calada nos dois sentidos: nao ha erro na
subida, e o jogador nao ve bonus faltando, ve um numero menor.

O proprio rAthena tem receita para isso, e onde ele conhece as duas versoes ele
a aplica: lista a com cova como ALTERNATIVA dentro do mesmo `- Combos:`, duas
listas `- Combo:` dividindo um `Script:` so. Foi assim que 19444, 19446 e
410125 sobreviveram a troca de 2026-08-05 sem ninguem fazer nada.

Com o 19455 nao dava, porque ele nao existe no vendor - nao ha alternativa para
o rAthena listar. Os tres conjuntos do 19024 foram espelhados a mao em
db/guerra/item_combos.yml, e este script existe para que da proxima vez isso
seja uma linha de saida em vez de uma descoberta.

**O casamento e feito no banco INTEIRO, nao dentro da entrada.** Vale escrever
por que, porque a leitura intuitiva e a errada: o jeito do rAthena e por na
mesma entrada, mas de um arquivo de import nao se acrescenta linha a uma
entrada alheia - o nosso espelho e entrada separada. Procurar so dentro da
entrada daria BLOQUEIO num conjunto que esta perfeitamente coberto.

---------------------------------------------------------------------- cuidados

Ler nao muda nada, mas `--aplicar` muda tres coisas, todas idempotentes e todas
com backup ou reversao propria: a entrada do cliente (completa_iteminfo.py), o
`Name` do servidor (nomes_pt_item_db.py) e nada mais. **Ele NAO cria entrada de
item_db**: preencher bonus e leitura de descricao, e isso e julgamento, nao
mecanica. Quando o item falta no servidor a saida diz isso e para.

Depois de aplicar: `@reloaditemdb` pega item e conjunto (conferido em
src/map/itemdb.cpp - `itemdb_reload` chama `itemdb_read`, que chama
`itemdb_combo.load`), `@reloadscript` pega a loja, e o `itemInfo.lua` so e lido
na INICIALIZACAO do cliente, ou seja fechar e reabrir.

Roda em Python 2.7, como as vizinhas.
"""
import os
import re
import subprocess
import sys

import completa_iteminfo as ci
import valida_visual as vv

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATHENA = os.path.join(_RAIZ, 'rathena')
NPC = os.path.join(RATHENA, 'npc')

# Os quatro arquivos de item na ordem em que o servidor os encadeia. O
# `vv.ITEM_DB` tem so equip + o nosso, porque aquele script so cuida de arte;
# aqui interessa qualquer item, inclusive consumivel e carta.
ITEM_DB = [os.path.join(RATHENA, 'db', 're', 'item_db_usable.yml'),
           os.path.join(RATHENA, 'db', 're', 'item_db_equip.yml'),
           os.path.join(RATHENA, 'db', 're', 'item_db_etc.yml'),
           os.path.join(RATHENA, 'db', 'guerra', 'item_db.yml')]

COMBO_DB = [os.path.join(RATHENA, 'db', 're', 'item_combos.yml'),
            os.path.join(RATHENA, 'db', 'guerra', 'item_combos.yml')]

PYTHON = sys.executable
AQUI = os.path.dirname(os.path.abspath(__file__))


class Erro(Exception):
    pass


# =============================================================== as tabelas


def le_servidor():
    u"""id -> item, dos quatro arquivos de item_db.

    Reaproveita o varredor do valida_visual.py, que em 2026-08-05 ganhou
    `slots`, `tipo` e `arquivo` justamente para este script. ID repetido: o
    ULTIMO vence, que e o que o servidor faz (o `Footer: Imports:` le o nosso
    depois, e `parseBodyNode` mescla por cima).
    """
    por_id = {}
    for item in vv.le_item_db(ITEM_DB):
        anterior = por_id.get(item['id'])
        if anterior is not None:
            item = dict(item)
            item['sobrepoe'] = anterior['arquivo']
        por_id[item['id']] = item
    return por_id


CAMPOS_CLIENTE = ('identifiedDisplayName', 'identifiedResourceName')


def le_cliente(dados, iid):
    u"""O que o itemInfo.lua diz do item, ou None se ele nao esta la.

    O arquivo tem 22 MB e a busca e por entrada, entao le-se o bloco daquele ID
    em vez de varrer o arquivo todo - o `ci.bloco` ja sabe onde ele comeca e
    termina (e sabe que o terminador tem UM tab, o que impede cortar a entrada
    no meio de uma descricao aninhada).
    """
    faixa = ci.bloco(dados, iid)
    if faixa is None:
        return None
    texto = dados[faixa[0]:faixa[1]]
    saida = {}
    for campo in CAMPOS_CLIENTE:
        m = re.search(r'(?<![A-Za-z])%s\s*=\s*"((?:[^"\\]|\\.)*)"' % campo,
                      texto)
        saida[campo] = m.group(1) if m else ''
    m = re.search(r'slotCount\s*=\s*(\d+)', texto)
    saida['slots'] = int(m.group(1)) if m else 0
    m = re.search(r'ClassNum\s*=\s*(\d+)', texto)
    saida['view'] = int(m.group(1)) if m else None
    saida['do_bro'] = ci.MARCA in texto
    return saida


# ================================================================= conjuntos


def le_combos():
    u"""Uma lista de (arquivo, [conjunto, ...]) por entrada `- Combos:`.

    Cada conjunto e uma TUPLA ORDENADA de AegisNames - ordenada porque a ordem
    dentro do `- Combo:` nao tem significado para o rAthena, e comparar listas
    cruas daria diferenca onde nao ha.

    Varredura linha a linha, como as vizinhas: os dois arquivos somam 8 MB e a
    estrutura e regular.
    """
    entradas = []
    for caminho in COMBO_DB:
        if not os.path.exists(caminho):
            continue
        atual = None       # a entrada `- Combos:` sendo montada
        combo = None       # a lista `- Combo:` sendo montada
        for linha in open(caminho, 'rb'):
            if re.match(r'\s*- Combos:', linha):
                if atual:
                    entradas.append((caminho, atual))
                atual, combo = [], None
                continue
            if atual is None:
                continue
            if re.match(r'\s*- Combo:', linha):
                combo = []
                atual.append(combo)
                continue
            m = re.match(r'\s*-\s+(\w+)\s*(?:#.*)?$', linha)
            if m and combo is not None:
                combo.append(m.group(1))
                continue
            # `Script: |` fecha as listas mas nao a entrada: a proxima linha
            # `- Combos:` e quem fecha.
            if re.match(r'\s*Script:', linha):
                combo = None
        if atual:
            entradas.append((caminho, atual))
    # normaliza
    saida = []
    for caminho, listas in entradas:
        saida.append((caminho, [tuple(sorted(l)) for l in listas if l]))
    return saida


def conjuntos_de(combos, aegis):
    u"""Os conjuntos que citam este AegisName: [(arquivo, conjunto), ...]."""
    achados = []
    for caminho, listas in combos:
        for conjunto in listas:
            if aegis in conjunto:
                achados.append((caminho, conjunto))
    return achados


def todos_conjuntos(combos):
    u"""Todo conjunto do banco, em set, para o casamento da trava."""
    tudo = set()
    for _, listas in combos:
        tudo.update(listas)
    return tudo


def trava_de_conjunto(combos, de_aegis, para_aegis):
    u"""Os conjuntos que a troca `de -> para` DERRUBA.

    Devolve [(arquivo, conjunto_antigo, conjunto_esperado), ...]. Lista vazia
    quer dizer que a troca esta coberta.

    O casamento e no banco inteiro (ver o cabecalho): um conjunto sobrevive se
    existe, EM QUALQUER ENTRADA, a mesma lista com o AegisName trocado. Nao
    importa se o rAthena a pos como alternativa na propria entrada (o jeito
    dele) ou se nos a espelhamos como entrada separada em db/guerra (o unico
    jeito possivel a partir de um import).
    """
    tudo = todos_conjuntos(combos)
    quebrados = []
    for caminho, conjunto in conjuntos_de(combos, de_aegis):
        esperado = tuple(sorted(
            [para_aegis if a == de_aegis else a for a in conjunto]))
        if esperado not in tudo:
            quebrados.append((caminho, conjunto, esperado))
    return quebrados


# ===================================================================== lojas
#
# Sintaxe da loja no rAthena (doc/script_commands.txt):
#
#   <mapa>,<x>,<y>,<dir>%TAB%shop%TAB%<nome>%TAB%<sprite>,<id>:<preco>,...
#   -%TAB%shop%TAB%<nome>%TAB%<sprite>,<id>:<preco>,...        (flutuante)
#
# `itemshop` e `pointshop` poem um campo A MAIS logo depois do sprite - o item
# ou a variavel que serve de moeda -, e ele tem a forma `<id>{:<desconto>}`,
# que e indistinguivel de um par `<id>:<preco>`. Por isso os dois sao tratados
# a parte: o primeiro campo depois do sprite e descartado. Sem isso a moeda
# entraria na lista como se estivesse a venda.

TIPOS_LOJA = ('shop', 'cashshop', 'itemshop', 'pointshop', 'marketshop')
COM_MOEDA = ('itemshop', 'pointshop')

CABECA_LOJA = re.compile(
    r'^(?P<pos>[^\t]+)\t(?P<tipo>%s)\t(?P<nome>[^\t]+)\t(?P<corpo>.+)$'
    % '|'.join(TIPOS_LOJA))


def le_lojas():
    u"""Toda loja de npc/, com os itens que vende: [(arquivo, nome, [ids])]."""
    lojas = []
    for raiz, _, arquivos in os.walk(NPC):
        for nome_arq in arquivos:
            if not nome_arq.endswith('.txt'):
                continue
            caminho = os.path.join(raiz, nome_arq)
            for n, linha in enumerate(open(caminho, 'rb'), 1):
                m = CABECA_LOJA.match(linha.rstrip('\r\n'))
                if not m:
                    continue
                campos = m.group('corpo').split(',')
                campos = campos[1:]                    # fora o sprite
                if m.group('tipo') in COM_MOEDA and campos:
                    campos = campos[1:]                # fora a moeda
                ids = []
                for campo in campos:
                    par = re.match(r'\s*(\d+):', campo)
                    if par:
                        ids.append(int(par.group(1)))
                if ids:
                    lojas.append({'arquivo': os.path.relpath(caminho, RATHENA),
                                  'linha': n, 'tipo': m.group('tipo'),
                                  'nome': m.group('nome'), 'ids': ids})
    return lojas


def lojas_de(lojas, iid):
    return [l for l in lojas if iid in l['ids']]


# ==================================================================== estado


class Mundo(object):
    u"""As tabelas todas, lidas uma vez so.

    O bRO e o caro (bytecode de 18845 itens) e o unico preguicoso: quem so
    pergunta o estado de um item que ja esta em toda parte nunca paga por ele.
    """

    def __init__(self):
        self.servidor = le_servidor()
        self.dados_cliente = open(ci.ITEMINFO, 'rb').read()
        self.combos = le_combos()
        self.lojas = le_lojas()
        self._bro = None

    @property
    def bro(self):
        if self._bro is None:
            self._bro = ci.le_bro(ci.BRO)
        return self._bro

    def estado(self, iid):
        srv = self.servidor.get(iid)
        cli = le_cliente(self.dados_cliente, iid)
        bro = self.bro.get(iid)
        return {
            'id': iid,
            'servidor': srv,
            'cliente': cli,
            'bro': bro,
            'conjuntos': (conjuntos_de(self.combos, srv['aegis'])
                          if srv and srv['aegis'] else []),
            'lojas': lojas_de(self.lojas, iid),
        }


def texto_bro(bro, campo):
    valor = bro.get(campo) if bro else None
    if isinstance(valor, bytes):
        try:
            valor = valor.decode('utf-8')
        except UnicodeDecodeError:
            return repr(valor)
    if isinstance(valor, unicode):
        return valor.encode('cp1252', 'replace')
    return '' if valor is None else str(valor)


def arte(iid):
    u"""(faltando, total) do valida_visual, ou None se ele nao sabe avaliar.

    Chamado como processo separado de proposito: o `main` do valida_visual.py
    e uma ferramenta de linha de comando, nao uma funcao que devolva contagem,
    e reescreve-lo para isso seria mexer no que ja funciona.
    """
    p = subprocess.Popen([PYTHON, os.path.join(AQUI, 'valida_visual.py'),
                          '--id', str(iid)],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         cwd=AQUI)
    saida = p.communicate()[0]
    if 'nao esta no itemInfo.lua' in saida:
        return None
    ok = len(re.findall(r'\[ok\s*\]', saida))
    falta = len(re.findall(r'\[FALTA\s*\]', saida))
    if ok + falta == 0:
        return None
    return (falta, ok + falta)


def relata(mundo, iid, com_arte=True):
    u"""Imprime o estado de um item. Devolve a lista de pendencias."""
    e = mundo.estado(iid)
    srv, cli, bro = e['servidor'], e['cliente'], e['bro']
    pendencias = []

    nome = (srv['nome'] if srv else '') or texto_bro(bro, 'identifiedDisplayName')
    print
    print '=== %d  %s' % (iid, nome or '(sem nome em lugar nenhum)')

    if srv:
        onde = os.path.relpath(srv['arquivo'], RATHENA).replace('\\', '/')
        extra = []
        if srv['slots']:
            extra.append('%d cova(s)' % srv['slots'])
        if srv['view'] is not None:
            extra.append('View %s' % srv['view'])
        if srv['locais']:
            extra.append('/'.join(sorted(srv['locais'])))
        print '  servidor  %-28s %s  %s' % (onde, srv['aegis'],
                                            '  '.join(extra))
        if srv.get('sobrepoe'):
            print '            (sobrepoe %s)' % os.path.relpath(
                srv['sobrepoe'], RATHENA).replace('\\', '/')
    else:
        print '  servidor  FORA - nao existe em item_db nenhum'
        if bro:
            pendencias.append(
                'criar a entrada em rathena/db/guerra/item_db.yml. O bRO tem o\n'
                '    item e a descricao dele traz os bonus por extenso:\n'
                '      python estado_item.py --id %d --descricao' % iid)
        else:
            pendencias.append(
                'ID desconhecido: nao esta no rAthena NEM nos 18845 do bRO.\n'
                '    Conferir o numero antes de qualquer outra coisa.')

    if cli:
        marca = '  (importada do bRO)' if cli['do_bro'] else ''
        print '  cliente   %-28s "%s"  %d cova(s)%s' % (
            'itemInfo.lua', cli['identifiedDisplayName'], cli['slots'], marca)
    else:
        print '  cliente   FORA - o item aparece SEM NOME e SEM ICONE'
        if bro:
            pendencias.append(
                'por a entrada de cliente (e por o ID na tabela ITENS de la):\n'
                '      python completa_iteminfo.py --id %d' % iid)

    if bro:
        print '  bRO       %-28s "%s"  %s cova(s)' % (
            'iteminfo_new.lub', texto_bro(bro, 'identifiedDisplayName'),
            int(bro.get('slotCount') or 0))
    else:
        print '  bRO       nao tem este ID'

    if srv and cli and srv['nome'] != cli['identifiedDisplayName']:
        print '  NOME      servidor "%s" != cliente "%s"' % (
            srv['nome'], cli['identifiedDisplayName'])
        pendencias.append(
            'sincronizar o nome do servidor com o do cliente (o de dialogo de\n'
            '    NPC sai do servidor):\n'
            '      python nomes_pt_item_db.py')

    if com_arte and cli:
        conta = arte(iid)
        if conta is None:
            print '  arte      valida_visual nao avalia este item'
        elif conta[0]:
            print '  arte      %d de %d FALTANDO' % conta
            pendencias.append(
                'instalar a arte, senao equipar entrega caixa de erro:\n'
                '      python instala_visual.py --id %d --grf <bRO>' % iid)
        else:
            print '  arte      %d de %d ok' % (conta[1], conta[1])

    if e['conjuntos']:
        print '  conjunto  %d, citando %s:' % (len(e['conjuntos']),
                                               srv['aegis'])
        for caminho, conjunto in e['conjuntos']:
            outros = [a for a in conjunto if a != srv['aegis']]
            print '              + %-40s %s' % (
                ', '.join(outros),
                os.path.relpath(caminho, RATHENA).replace('\\', '/'))
    elif srv:
        print '  conjunto  nenhum'

    if e['lojas']:
        for loja in e['lojas']:
            print '  loja      %-28s %s:%d' % (
                loja['nome'], loja['arquivo'].replace('\\', '/'),
                loja['linha'])
    else:
        print '  loja      nao esta a venda em npc/'

    return pendencias


# ==================================================================== a troca


def analisa_troca(mundo, de_id, para_id):
    u"""Diz se a troca pode ser feita. Devolve (pode, bloqueios, avisos)."""
    de = mundo.servidor.get(de_id)
    para = mundo.servidor.get(para_id)
    bloqueios, avisos = [], []

    print
    print '=' * 74
    print 'TROCA  %d -> %d' % (de_id, para_id)
    print '=' * 74

    if de is None:
        avisos.append('%d nao existe no item_db - nao da para saber que '
                      'conjuntos ele tinha.' % de_id)
    if para is None:
        bloqueios.append(
            '%d NAO EXISTE no item_db do servidor. Sem entrada, a loja nao\n'
            '  abre. Criar em rathena/db/guerra/item_db.yml - e julgamento,\n'
            '  nao mecanica: os bonus vem da descricao do bRO, ou copiados da\n'
            '  peca irma quando o rAthena tem uma.' % para_id)

    # --- o que o de e o para tem em comum, para pegar troca por engano
    if de and para:
        if de['tipo'] != para['tipo']:
            avisos.append('tipos diferentes: %s vira %s.' % (de['tipo'],
                                                             para['tipo']))
        if de['locais'] != para['locais']:
            avisos.append('lugares de equipar diferentes: %s vira %s.' % (
                '/'.join(sorted(de['locais'])) or '-',
                '/'.join(sorted(para['locais'])) or '-'))
        if de['view'] != para['view']:
            avisos.append(
                'View muda (%s -> %s): a arte NAO e a mesma, entao o par\n'
                '  estende_accessoryid.py + instala_visual.py pode ser '
                'preciso.' % (de['view'], para['view']))
        else:
            print 'View %s nos dois - a arte ja instalada serve.' % de['view']

    # --- a trava
    if de and para and de['aegis'] and para['aegis']:
        quebrados = trava_de_conjunto(mundo.combos, de['aegis'], para['aegis'])
        tinha = conjuntos_de(mundo.combos, de['aegis'])
        if not tinha:
            print 'Conjunto: %s nao esta em nenhum - nada a perder.' % de['aegis']
        elif not quebrados:
            print ('Conjunto: %d conjunto(s) citam %s, e todos ja tem o par '
                   'com %s no banco - cobertos.' % (len(tinha), de['aegis'],
                                                    para['aegis']))
        else:
            linhas = []
            for caminho, conjunto, esperado in quebrados:
                outros = [a for a in conjunto if a != de['aegis']]
                linhas.append('    + %-38s (%s)' % (
                    ', '.join(outros),
                    os.path.relpath(caminho, RATHENA).replace('\\', '/')))
            bloqueios.append(
                'A TROCA DERRUBA %d CONJUNTO(S), e a perda e CALADA:\n%s\n'
                '  Conjunto e casado por AegisName: %s nao e %s. Espelhar os\n'
                '  conjuntos para o ID novo em rathena/db/guerra/item_combos.yml,\n'
                '  copiando o Script do db/re/ sem mudar numero.' % (
                    len(quebrados), '\n'.join(linhas),
                    para['aegis'], de['aegis']))

    # --- o lado do cliente
    if para is not None:
        pendencias = relata(mundo, para_id)
        for p in pendencias:
            bloqueios.append(p)

    print
    if bloqueios:
        print 'NAO PODE TROCAR AINDA - %d ponto(s):' % len(bloqueios)
        for i, b in enumerate(bloqueios, 1):
            print '  %d) %s' % (i, b)
    else:
        print 'PODE TROCAR.'
    for a in avisos:
        print '  aviso: %s' % a
    return (not bloqueios, bloqueios, avisos)


def aplica_troca(mundo, pares):
    u"""Roda o que da para rodar sozinho. Nada aqui inventa conteudo."""
    faltam_cliente = []
    for _, para_id in pares:
        if (mundo.servidor.get(para_id) is not None
                and le_cliente(mundo.dados_cliente, para_id) is None):
            faltam_cliente.append(para_id)

    if faltam_cliente:
        ids = ','.join(str(i) for i in faltam_cliente)
        print
        print '-> completa_iteminfo.py --id %s  (entrada de cliente, do bRO)' % ids
        print '   ATENCAO: por estes IDs na tabela ITENS do completa_iteminfo.py'
        print '   tambem, senao um cliente novo nasce sem eles.'
        if subprocess.call([PYTHON, os.path.join(AQUI, 'completa_iteminfo.py'),
                            '--id', ids], cwd=AQUI) != 0:
            raise Erro('completa_iteminfo.py falhou')
        mundo.dados_cliente = open(ci.ITEMINFO, 'rb').read()

    desalinhados = []
    for _, para_id in pares:
        srv = mundo.servidor.get(para_id)
        cli = le_cliente(mundo.dados_cliente, para_id)
        if srv and cli and srv['nome'] != cli['identifiedDisplayName']:
            desalinhados.append(para_id)
    if desalinhados:
        print
        print '-> nomes_pt_item_db.py  (o Name do servidor, para %s)' % (
            ','.join(str(i) for i in desalinhados))
        print '   Ele reescreve o item_db INTEIRO e deixa .INGLES ao lado;'
        print '   e idempotente, entao o git diff mostra so o que mudou.'
        if subprocess.call([PYTHON, os.path.join(AQUI, 'nomes_pt_item_db.py')],
                           cwd=AQUI) != 0:
            raise Erro('nomes_pt_item_db.py falhou')

    print
    print 'O QUE ESTE SCRIPT NAO FAZ, e continua com voce:'
    print '  - trocar o ID na linha da loja (npc/guerra/*.txt);'
    print '  - criar entrada de item_db que falte;'
    print '  - espelhar conjunto em db/guerra/item_combos.yml.'
    print
    print 'Depois: @reloaditemdb (item e conjunto) + @reloadscript (loja), e'
    print 'FECHAR E REABRIR O CLIENTE se a entrada de cliente mudou.'


# ====================================================================== main


def uso():
    print __doc__.split('\n\n')[0]
    print
    print 'python estado_item.py --id <n>[,<n>...]'
    print 'python estado_item.py --loja <nome>'
    print 'python estado_item.py --troca <de>:<para>[,<de>:<para>...] [--aplicar]'
    print 'python estado_item.py --descricao --id <n>   (a descricao do bRO)'
    return 2


def main():
    argv = sys.argv[1:]
    if not argv or '--ajuda' in argv or '-h' in argv:
        return uso()

    def opcao(nome):
        return argv[argv.index(nome) + 1] if nome in argv else None

    mundo = Mundo()

    if '--troca' in argv:
        pares = []
        for par in opcao('--troca').split(','):
            de, para = par.split(':')
            pares.append((int(de), int(para)))
        ok = True
        for de_id, para_id in pares:
            if not analisa_troca(mundo, de_id, para_id)[0]:
                ok = False
        if '--aplicar' in argv:
            if not ok:
                print
                print 'NAO APLIQUEI: resolva os bloqueios acima primeiro.'
                return 1
            aplica_troca(mundo, pares)
        return 0 if ok else 1

    if '--loja' in argv:
        alvo = opcao('--loja').lower()
        achadas = [l for l in mundo.lojas if alvo in l['nome'].lower()]
        if not achadas:
            print 'nenhuma loja com "%s" no nome' % opcao('--loja')
            return 1
        for loja in achadas:
            print
            print '#' * 74
            print '# %s   %s:%d   %d itens' % (
                loja['nome'], loja['arquivo'].replace('\\', '/'),
                loja['linha'], len(loja['ids']))
            print '#' * 74
            for iid in loja['ids']:
                relata(mundo, iid, com_arte='--sem-arte' not in argv)
        return 0

    if '--id' in argv:
        ids = [int(x) for x in opcao('--id').split(',')]
        if '--descricao' in argv:
            for iid in ids:
                entrada = mundo.bro.get(iid)
                print
                print '=== %d  descricao do bRO' % iid
                if not entrada:
                    print '  o bRO nao tem este ID'
                    continue
                for linha in (entrada.get('identifiedDescriptionName') or []):
                    print '  ' + (linha.encode('cp1252', 'replace')
                                  if isinstance(linha, unicode) else linha)
            return 0
        pendentes = 0
        for iid in ids:
            p = relata(mundo, iid, com_arte='--sem-arte' not in argv)
            if p:
                print
                print '  FALTA:'
                for i, item in enumerate(p, 1):
                    print '    %d) %s' % (i, item)
                pendentes += 1
        return 1 if pendentes else 0

    return uso()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
