# -*- coding: utf-8 -*-
u"""Poe `Buy: 1` em todo item vendido nas lojas de Prontera.

    python zera_revenda_das_lojas.py             # gera db/guerra/item_db_lojas.yml
    python zera_revenda_das_lojas.py --conferir  # so relata; sai 1 se achar lucro

O PROBLEMA QUE ISTO RESOLVE

As lojas de Prontera vendem a 1 zeny. O dinheiro infinito nunca esteve na
vitrine: esta na REVENDA. Quem compra por 1 zeny revende em QUALQUER NPC pelo
`Sell` do `item_db`, e `Sell` vale `Buy/2` quando o item nao declara o campo.
Lucro por clique, em laco, num servidor de drop 50x.

Medido em 2026-08-17, antes desta ferramenta existir: 913 dos 1513 itens das
vinte e uma lojas davam lucro. Quase todos 9 zeny (carta de `Buy: 20`), e tres
nao:

    19446  Tapa-Olho Ferido   vitrine 1 z, revenda 1.000.000 z
    500009 Copia de Gram      vitrine 1 z, revenda   250.000 z
    2204   Oculos_            vitrine 1 z, revenda     2.000 z

COMO ELE RESOLVE

Um override que declara SO o `Buy: 1`. O `Sell` cai junto sem precisar ser
escrito, e isso e uma consequencia do leitor, nao sorte: o
`ItemDatabase::parseBodyNode` (src/map/itemdb.cpp) guarda, POR ITEM, se aquele
bloco trouxe `Buy` e se trouxe `Sell` -

    hasPriceValue[item->nameid] = { has_buy, has_sell };

- e essa linha e uma ATRIBUICAO, entao o ultimo arquivo a falar do item vence.
Como o nosso e o ultimo, o item passa a ter `has_buy = true` e
`has_sell = false` ainda que o `db/re/` tenha declarado `Sell` explicito; e no
fim do carregamento o rAthena faz

    else if (has_buy && !has_sell)  item->value_sell = item->value_buy / 2;

ou seja `1 / 2 = 0`. Vitrine 1 zeny, revenda 0 zeny, lucro 0.

O QUE ISSO ALCANCA, E E PRECISO SABER: TODA COPIA DO ITEM NO SERVIDOR, nao so
a que saiu da loja. Valor de item nao e por instancia - e do `item_db`. Carta
que o jogador cacou tambem deixa de valer 10 zeny no NPC. Foi a saida numero 1
que o cabecalho do mercado_contemporaneo.txt tinha CONSIDERADO E RECUSADO em
2026-08-12, exatamente por isso; a decisao do dono em 2026-08-17 foi a
contraria, com o numero dos 913 na mao.

QUE LOJAS ENTRAM: as tres de VITRINE A 1 ZENY -

    npc/guerra/mercado_contemporaneo.txt   9 lojas de equipamento
    npc/guerra/mercado_de_cartas.txt       8 lojas de carta
    npc/guerra/mercado_de_visuais.txt      4 lojas de visual

A TRANQUEIRAS FICA DE FORA, por decisao do dono no mesmo dia. Ela nao vende a
1 zeny: vende a `-1`, que o `npc_parse_shop` troca pelo `Buy` do item
(src/map/npc.cpp linha 4146). Com o preco valendo o `Buy`, revender da
prejuizo - ela ja tinha lucro por clique ZERO nos 55 itens, medido. Por `Buy: 1`
nela nao fecharia buraco nenhum e abriria outro: o Ouro (969) cairia de 150.000
para 1 zeny, e com ele as dez receitas de Runa e os 29 ingredientes da alquimia.

POR QUE UMA FERRAMENTA, E NAO UM ARQUIVO ESCRITO A MAO

Porque a lista das lojas muda. Item novo posto numa vitrine sem passar por aqui
nasce com o `Buy` do `item_db` e reabre o buraco calado - nada no log denuncia,
a loja sobe, vende, e o jogador acha o lucro antes da gente. Rodar este script
depois de mexer em qualquer uma das tres lojas fecha isso; o `--conferir` diz
se falta rodar.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import codecs
import os
import re
import sys

sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RATHENA = os.path.join(RAIZ, 'rathena')

# Ordem de leitura = ordem de override. O nosso item_db entra por ultimo
# porque e ele que o servidor deixa vencer (Footer: Imports de
# db/re/item_db.yml).
ITEM_DB = [
    os.path.join('db', 're', 'item_db_usable.yml'),
    os.path.join('db', 're', 'item_db_equip.yml'),
    os.path.join('db', 're', 'item_db_etc.yml'),
    os.path.join('db', 'guerra', 'item_db.yml'),
    # O que este script gera. Entra na leitura para que o `--conferir` meca a
    # REALIDADE do servidor, e nao o estado anterior a ele: e assim que ele
    # denuncia item posto numa vitrine depois da ultima geracao.
    os.path.join('db', 'guerra', 'item_db_lojas.yml'),
]

LOJAS = [
    os.path.join('npc', 'guerra', 'mercado_contemporaneo.txt'),
    os.path.join('npc', 'guerra', 'mercado_de_cartas.txt'),
    os.path.join('npc', 'guerra', 'mercado_de_visuais.txt'),
]

SAIDA = os.path.join('db', 'guerra', 'item_db_lojas.yml')

RE_ID = re.compile(r'^\s*-\s+Id:\s*(\d+)')
RE_AEGIS = re.compile(r'^\s*AegisName:\s*(\S+)')
RE_BUY = re.compile(r'^\s*Buy:\s*(\d+)')
RE_SELL = re.compile(r'^\s*Sell:\s*(\d+)')
# Os campos de uma linha de NPC sao separados por TAB, e o nome da loja PODE
# ter espaco ("Senhor das Armas#loja") - por isso [^\t]+ e nao \S+.
RE_SHOP = re.compile(r'^-\t(?:shop|itemshop|pointshop)\t([^\t]+)\t-1,(.*)$')


def le_item_db():
    u"""id -> {'aegis','buy','sell'}, mesclado campo a campo na ordem de import.

    Mesclar e o unico jeito certo: o nosso db/guerra/item_db.yml e bloco
    PARCIAL de YAML e so traz os campos que a gente declarou. Ficar so com o
    ultimo bloco perde o que o rAthena ja dizia; ficar so com o primeiro
    ignora o override. Ver CLAUDE.md secao 5, entrada do `le_item_db`.
    """
    itens = {}
    for rel in ITEM_DB:
        caminho = os.path.join(RATHENA, rel)
        if not os.path.exists(caminho):
            # Vale so para o item_db_lojas.yml, que este script gera: na
            # primeira rodada de um clone limpo ele ainda nao existe.
            continue
        atual = None
        for linha in open(caminho, 'rb'):
            linha = linha.decode('cp1252', 'replace')
            m = RE_ID.match(linha)
            if m:
                atual = int(m.group(1))
                itens.setdefault(atual, {})
                continue
            if atual is None:
                continue
            for regex, campo in ((RE_AEGIS, 'aegis'), (RE_BUY, 'buy'), (RE_SELL, 'sell')):
                m = regex.match(linha)
                if m:
                    itens[atual][campo] = m.group(1) if campo == 'aegis' else int(m.group(1))
                    break
    return itens


def le_lojas():
    u"""[(arquivo, loja, [(id, preco_escrito)])] das tres lojas de 1 zeny."""
    lojas = []
    for rel in LOJAS:
        for linha in open(os.path.join(RATHENA, rel), 'rb'):
            linha = linha.decode('cp1252', 'replace').rstrip('\r\n')
            m = RE_SHOP.match(linha)
            if not m:
                continue
            pares = []
            for p in m.group(2).split(','):
                if ':' not in p:
                    continue
                sid, preco = p.split(':')
                pares.append((int(sid), int(preco)))
            lojas.append((os.path.basename(rel), m.group(1), pares))
    return lojas


def revenda(d):
    u"""O `Sell` efetivo, pela mesma regra do itemdb.cpp."""
    if 'sell' in d:
        return d['sell']
    if 'buy' in d:
        return d['buy'] // 2
    return 0


def vitrine(preco, d):
    u"""`-1` na linha do shop vira o `Buy` do item (npc.cpp linha 4146)."""
    if preco >= 0:
        return preco
    if 'buy' in d:
        return d['buy']
    if 'sell' in d:
        return d['sell'] * 2
    return 0


def confere(itens, lojas):
    u"""Relata todo item cuja revenda passa do preco de vitrine."""
    achados = []
    for arquivo, loja, pares in lojas:
        for sid, preco in pares:
            d = itens.get(sid)
            if d is None:
                continue
            p = vitrine(preco, d)
            r = revenda(d)
            if r > p:
                achados.append((r - p, sid, d.get('aegis', '?'), loja, p, r))
    achados.sort(reverse=True)
    return achados


def main():
    conferir = '--conferir' in sys.argv

    itens = le_item_db()
    lojas = le_lojas()

    ids = []
    vistos = set()
    ausentes = []
    for arquivo, loja, pares in lojas:
        for sid, preco in pares:
            if sid in vistos:
                continue
            vistos.add(sid)
            if sid not in itens or 'aegis' not in itens[sid]:
                # Item que a vitrine cita e o item_db nao tem. Escrever um
                # bloco parcial para ele faria o rAthena recusar por falta de
                # AegisName - e o problema de verdade e a loja citar id morto.
                ausentes.append((sid, loja))
                continue
            ids.append((sid, itens[sid].get('aegis', '?'), loja))

    print u'lojas lidas: %d, com %d itens (%d ids distintos)' % (
        len(lojas), sum(len(p) for _, _, p in lojas), len(vistos))

    for sid, loja in ausentes:
        print u'AVISO: id %d, citado por %s, nao existe no item_db - pulado' % (sid, loja)

    if conferir:
        achados = confere(itens, lojas)
        if not achados:
            print u'OK: nenhum item das tres lojas revende por mais do que custa.'
            return 0
        print u''
        print u'LUCRO POR CLIQUE em %d itens - falta rodar este script sem --conferir:' % len(achados)
        for lucro, sid, aegis, loja, p, r in achados[:30]:
            print u'   %10d z/clique  %-7d %-34s %-24s vitrine %-9d revenda %d' % (
                lucro, sid, aegis, loja, p, r)
        if len(achados) > 30:
            print u'   ... e mais %d' % (len(achados) - 30)
        return 1

    caminho = os.path.join(RATHENA, SAIDA)
    f = open(caminho, 'wb')
    f.write(CABECALHO.encode('ascii'))
    for sid, aegis, loja in sorted(ids):
        f.write(('  - Id: %d\n    Buy: 1                # %s\n' % (sid, aegis)).encode('ascii'))
    f.close()

    print u'gravado: %s' % caminho
    print u'%d itens a Buy: 1 (revenda 0)' % len(ids)
    print u''
    print u'FALTA: reiniciar o map-server ou dar `@reloaditemdb` em jogo.'
    return 0


CABECALHO = u'''###########################################################################
# Guerra do Emperium - AS LOJAS DE PRONTERA VALEM 1 ZENY
#
# ARQUIVO GERADO por ferramentas/zera_revenda_das_lojas.py. Editar a mao
# funciona ate a proxima geracao, que apaga tudo. Item novo numa vitrine
# entra rodando o script de novo.
#
# Este arquivo e VERSIONADO e vale para qualquer clone do repo. Ele e
# importado por db/re/item_db.yml, DEPOIS de db/guerra/item_db.yml (para
# vencer qualquer preco escrito la) e ANTES de db/import/item_db.yml.
#
# ------------------------------------------------------------- o que ele e
#
# `Buy: 1` em todo item vendido nas tres lojas de vitrine a 1 zeny de
# Prontera - o Mercado Contemporaneo, o Mercado de Cartas e o Mercado de
# Visuais. Decisao do dono em 2026-08-17: "itens que sao vendidos nas lojas
# de Prontera devem ter valor 1 zeny pra evitar criacao de dinheiro
# infinito".
#
# A TRANQUEIRAS NAO ESTA AQUI, de proposito. Ela vende a `-1`, ou seja pelo
# `Buy` do item, e ja tinha lucro por clique zero - ver o cabecalho de
# npc/guerra/tranqueiras.txt.
#
# ---------------------------------------------------- por que so o `Buy`
#
# Porque o `Sell` cai junto. O leitor do item_db guarda por item se aquele
# bloco trouxe `Buy` e se trouxe `Sell`, e a ultima palavra e de quem falar
# por ultimo - este arquivo. Com `has_buy` e sem `has_sell`, o rAthena faz
# `value_sell = value_buy / 2` no fim do carregamento, o que da 0.
#
# Escrever `Sell: 0` aqui seria a mesma coisa com um campo a mais para
# divergir.
#
# ---------------------------------------------------------- o que alcanca
#
# TODA COPIA DO ITEM NO SERVIDOR, nao so a que saiu da loja - valor de item
# mora no item_db, nao na instancia. Carta cacada por jogador tambem passa a
# revender por 0. E o preco da decisao, e ele foi tomado sabendo disso.
#
# --------------------------------------------------------- como recarregar
#
# `@reloaditemdb` em jogo, ou reiniciar o map-server. As linhas do `shop`
# nao mudam com isso: elas ja estao todas a 1 zeny.
###########################################################################

Header:
  Type: ITEM_DB
  Version: 3

Body:
'''


if __name__ == '__main__':
    sys.exit(main())
