# -*- coding: utf-8 -*-
u"""Poe os drops de MAPA na mesma escala de drop do resto do servidor.

    python escala_drops_de_mapa.py             # gera db/guerra/map_drops.yml
    python escala_drops_de_mapa.py --fator 50  # o padrao
    python escala_drops_de_mapa.py --conferir  # so relata; sai 1 se divergir

O PROBLEMA QUE ISTO RESOLVE

Equipamento ilusional nao cai. O pedido chega como "o Congelador Ominoso
deveria dropar a Espada Ilusional e nao dropa", e a primeira coisa que se
descobre e que ele REALMENTE nao dropa: a espada nao esta no `Drops:` do
monstro em db/re/mob_db.yml. Ela e DROP DE MAPA, um mecanismo separado que
vive em db/re/map_drops.yml e que o `mob_dead` processa depois dos drops
normais (src/map/mob.cpp, "Process map specific drops").

E o drop de mapa NAO PASSA PELA TAXA DO SERVIDOR. O `mob_getdroprate`
chamado ali (mob.cpp linha 3388) so aplica bonus de LUK e de equipamento do
jogador; os nossos `item_rate_*: 5000` de conf/guerra/battle_guerra.txt nao
alcancam campo nenhum daquele arquivo. O proprio cabecalho do map_drops.yml
diz isso em ingles, numa linha so: "These drops are unaffected by server drop
rate and cannot be stolen."

Resultado medido em 2026-08-18, antes desta ferramenta existir: num servidor
de drop 50x, o conteudo de drop de mapa inteiro rodava a 1x.

    Espada Ilusional (13469)  Rate 25     = 0,025% por Congelador Ominoso
    Pedra da Ilusao           Rate 10     = 0,010% - e a troca pede CEM
    Caixa da Ilha da Tartaruga Rate 5     = 0,005%

O Congelador Ominoso tem 549.071 de HP. A 0,025% sao ~2.800 mortes para uma
chance de meio a meio - e isso e a espada, que e o item barato do mapa. A
troca de barter_ill_turtle (npc/re/merchants/barters/enchan_illusion_dungeons
.yml) pede 100 Pedras da Ilusao a 0,01% cada. Na pratica: o ramo ilusional
inteiro estava inerte, e nada no log dizia isso porque nada estava quebrado.

O QUE ESTE SCRIPT FAZ

Um override que redeclara CADA drop de mapa do vendor com a taxa multiplicada
pelo fator (50 por padrao, o mesmo `item_rate_equip: 5000` do servidor), com
teto de 100000 (=100%).

A mescla e por (Mapa, Monstro, Index) e e o leitor do rAthena que a faz - o
`MapDropDatabase::parseBodyNode` (mob.cpp linha 6945) procura o mapa antes de
criar, e o `parseDrop` procura o Index dentro do monstro. Campo nao declarado
fica como estava, e e por isso que este arquivo NAO escreve
`RandomOptionGroup`: as opcoes aleatorias do vendor continuam valendo.

TETO DE 100000, E ELE NAO E DETALHE: `Rate` acima de 100000 faz o parseDrop
devolver `false`, o parseBodyNode devolver 0 e o registro do MAPA INTEIRO ser
descartado - com o agravante de que os drops ja lidos daquele mapa ficaram
aplicados, entao o override sairia pela metade, calado. Por isso o `min()`
esta neste script e nao na cabeca de quem edita.

QUANTOS BATEM NO TETO: 117 dos 687, todos de chefe (taxa base >= 2%). Isso
NAO e exagero desta ferramenta - e o mesmo que ja acontece com todo drop
normal do servidor: com `item_rate_equip: 5000` e `item_drop_equip_max:
10000`, qualquer drop de 2% ou mais ja e 100% aqui. O drop de mapa so passa a
se comportar como o resto.

POR QUE UMA FERRAMENTA, E NAO UM ARQUIVO ESCRITO A MAO

Sao 687 taxas em 18 mapas, e elas vem do vendor - atualizar o rAthena traz
mapa novo, monstro novo e Index novo. Arquivo escrito a mao envelhece calado:
o mapa novo entra a 1x e ninguem percebe, porque o sintoma e "esse item nunca
cai", que e indistinguivel de azar. O `--conferir` compara o gerado com o
vendor e denuncia tres coisas: taxa fora do fator, par (Index -> Item) que
mudou de lado no vendor, e drop que existe no vendor e nao aqui.

O par Index -> Item e o que exige o cuidado maior. A mescla do rAthena e por
INDEX, nao por item: se um dia o vendor reordenar os Index de um monstro, o
nosso arquivo passaria a escrever a taxa de um item na linha de outro. Por
isso o `Item:` e escrito aqui - nao porque o leitor precise dele (nao
precisa), mas para que o `--conferir` tenha como ver o deslocamento.

Roda em Python 2.7 (`C:\\Python27\\python.exe`). Precisa de PyYAML.
"""
import codecs
import io
import os
import sys

try:
    import yaml
except ImportError:
    print 'ERRO: este script precisa do PyYAML (import yaml).'
    sys.exit(2)

sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RATHENA = os.path.join(RAIZ, 'rathena')

VENDOR = os.path.join('db', 're', 'map_drops.yml')
SAIDA = os.path.join('db', 'guerra', 'map_drops.yml')

FATOR = 50      # o mesmo item_rate_equip: 5000 de conf/guerra/battle_guerra.txt
TETO = 100000   # asUInt32Rate(node, "Rate", rate, 100000) - acima disto o
                # registro do mapa inteiro e descartado (mob.cpp linha 7072)


def le(rel):
    u"""Devolve [(mapa, [(monstro, [(index, item, taxa)])])] na ordem do arquivo.

    Os dois arquivos - o do vendor e o nosso - tem a mesma forma, entao um
    leitor so serve para os dois. GlobalDrops nao aparece no vendor de hoje,
    mas e lido do mesmo jeito: o dia em que aparecer, entra na conta sem que
    alguem precise lembrar disto.
    """
    caminho = os.path.join(RATHENA, rel)
    if not os.path.exists(caminho):
        return None
    dados = yaml.safe_load(io.open(caminho, encoding='ascii'))
    mapas = []
    for m in dados.get('Body') or []:
        globais = [(d['Index'], d.get('Item'), d.get('Rate'))
                   for d in m.get('GlobalDrops') or []]
        especificos = []
        for s in m.get('SpecificDrops') or []:
            especificos.append((s['Monster'],
                                [(d['Index'], d.get('Item'), d.get('Rate'))
                                 for d in s.get('Drops') or []]))
        mapas.append((m['Map'], globais, especificos))
    return mapas


def escala(taxa, fator):
    return min(taxa * fator, TETO)


def indexa(mapas):
    u"""(mapa, monstro, index) -> (item, taxa). `monstro` e None nos globais."""
    d = {}
    for mapa, globais, especificos in mapas:
        for idx, item, taxa in globais:
            d[(mapa, None, idx)] = (item, taxa)
        for monstro, drops in especificos:
            for idx, item, taxa in drops:
                d[(mapa, monstro, idx)] = (item, taxa)
    return d


def confere(vendor, nosso, fator):
    u"""Lista de queixas em texto. Vazia quer dizer que o arquivo esta em dia."""
    queixas = []
    v = indexa(vendor)
    n = indexa(nosso)

    for chave in sorted(v):
        mapa, monstro, idx = chave
        item_v, taxa_v = v[chave]
        onde = u'%s / %s / Index %d' % (mapa, monstro or u'(global)', idx)
        if chave not in n:
            queixas.append(u'FALTA   %-52s %s a %d/100000 nao esta no nosso arquivo'
                           % (onde, item_v, taxa_v))
            continue
        item_n, taxa_n = n[chave]
        if item_n != item_v:
            # O vendor reordenou os Index. Escrever taxa aqui e escrever na
            # linha errada - regenerar e obrigatorio, nao opcional.
            queixas.append(u'TROCOU  %-52s vendor diz %s, nosso diz %s'
                           % (onde, item_v, item_n))
            continue
        esperado = escala(taxa_v, fator)
        if taxa_n != esperado:
            queixas.append(u'TAXA    %-52s %s esta %d, deveria ser %d (%dx de %d)'
                           % (onde, item_v, taxa_n, esperado, fator, taxa_v))

    for chave in sorted(n):
        if chave not in v:
            mapa, monstro, idx = chave
            queixas.append(u'SOBRA   %s / %s / Index %d nao existe mais no vendor'
                           % (mapa, monstro or u'(global)', idx))

    return queixas


def grava(vendor, fator):
    linhas = [CABECALHO % {'fator': fator}]
    for mapa, globais, especificos in vendor:
        linhas.append(u'  - Map: %s\n' % mapa)
        if globais:
            linhas.append(u'    GlobalDrops:\n')
            for idx, item, taxa in globais:
                linhas.append(u'      - Index: %d\n        Item: %s\n        Rate: %d\n'
                              % (idx, item, escala(taxa, fator)))
        if especificos:
            linhas.append(u'    SpecificDrops:\n')
            for monstro, drops in especificos:
                linhas.append(u'      - Monster: %s\n        Drops:\n' % monstro)
                for idx, item, taxa in drops:
                    linhas.append(u'          - Index: %d\n            Item: %s\n'
                                  u'            Rate: %d\n'
                                  % (idx, item, escala(taxa, fator)))

    caminho = os.path.join(RATHENA, SAIDA)
    # 'wb' e \n a mao: o .gitattributes tem `*.yml eol=lf`, e este arquivo e
    # lido pelo servidor Linux.
    f = open(caminho, 'wb')
    f.write(u''.join(linhas).encode('ascii'))
    f.close()
    return caminho


def main():
    argv = sys.argv[1:]
    conferir = '--conferir' in argv
    fator = FATOR
    if '--fator' in argv:
        fator = int(argv[argv.index('--fator') + 1])
        if fator < 1:
            print u'ERRO: fator tem de ser >= 1.'
            return 2

    vendor = le(VENDOR)
    if vendor is None:
        print u'ERRO: nao achei %s' % VENDOR
        return 2

    total = sum(len(g) + sum(len(d) for _, d in e) for _, g, e in vendor)
    capados = 0
    for _, globais, especificos in vendor:
        for _, _, taxa in globais:
            if taxa * fator > TETO:
                capados += 1
        for _, drops in especificos:
            for _, _, taxa in drops:
                if taxa * fator > TETO:
                    capados += 1

    print u'vendor: %d mapas, %d drops de mapa' % (len(vendor), total)

    if conferir:
        nosso = le(SAIDA)
        if nosso is None:
            print u'FALTA: %s nao existe - rodar este script sem --conferir.' % SAIDA
            return 1
        queixas = confere(vendor, nosso, fator)
        if not queixas:
            print u'OK: os %d drops estao a %dx do vendor (teto %d).' % (total, fator, TETO)
            return 0
        print u''
        print u'%d divergencias - falta rodar este script sem --conferir:' % len(queixas)
        for q in queixas[:40]:
            print u'   ' + q
        if len(queixas) > 40:
            print u'   ... e mais %d' % (len(queixas) - 40)
        return 1

    caminho = grava(vendor, fator)
    print u'gravado: %s' % caminho
    print u'%d drops a %dx; %d bateram no teto de %d (=100%%)' % (
        total, fator, capados, TETO)
    print u''
    print u'FALTA: `@reloadmobdb` em jogo (ele recarrega o map_drop_db,'
    print u'       src/map/mob.cpp linha 7216) ou reiniciar o map-server.'
    return 0


CABECALHO = u'''###########################################################################
# Guerra do Emperium - DROP DE MAPA NA ESCALA DO SERVIDOR
#
# ARQUIVO GERADO por ferramentas/escala_drops_de_mapa.py. Editar a mao
# funciona ate a proxima geracao, que apaga tudo.
#
# ------------------------------------------------------------- o que ele e
#
# Toda taxa de db/re/map_drops.yml multiplicada por %(fator)d, com teto de
# 100000 (=100%%). Importado pelo rodape de db/re/map_drops.yml.
#
# ------------------------------------------------------------ por que existe
#
# Drop de mapa NAO passa pela taxa do servidor. O `mob_getdroprate` chamado
# em src/map/mob.cpp linha 3388 so aplica bonus de LUK e de equipamento do
# jogador - os nossos `item_rate_*: 5000` nao alcancam este arquivo. O
# cabecalho do proprio map_drops.yml do rAthena diz isso: "These drops are
# unaffected by server drop rate and cannot be stolen."
#
# Ou seja: num servidor de 50x, o ramo ilusional inteiro rodava a 1x. A
# Espada Ilusional caia a 25/100000 = 0,025%% por Congelador Ominoso (549.071
# de HP), e a Pedra da Ilusao a 0,010%% - sendo que a troca de
# barter_ill_turtle pede CEM pedras. Nada estava quebrado, e por isso nada
# aparecia no log.
#
# Decisao do dono em 2026-08-18: por o drop de mapa na mesma escala do
# `item_rate_equip: 5000`, nos 18 mapas do arquivo e nao so nos dez
# ilusionais.
#
# ------------------------------------------------------- o que a mescla faz
#
# O rAthena mescla por (Mapa, Monstro, Index): o parseBodyNode procura o mapa
# antes de criar e o parseDrop procura o Index dentro do monstro. Campo nao
# declarado aqui fica como estava - e e por isso que este arquivo nao escreve
# `RandomOptionGroup`: as opcoes aleatorias do vendor continuam valendo.
#
# O `Item:` esta escrito em cada linha ainda que o leitor nao precise dele.
# Ele existe para o `--conferir` conseguir ver o dia em que o vendor
# reordenar um Index - a mescla e por Index, entao um deslocamento la poria a
# taxa de um item na linha de outro, calado.
#
# ---------------------------------------------------------------- o teto
#
# `Rate` acima de 100000 nao e cortado pelo leitor: ele recusa o drop, e a
# recusa derruba o registro do MAPA INTEIRO (parseDrop devolve false ->
# parseBodyNode devolve 0). Os 117 drops de chefe que batem no teto ficam em
# 100%%, que e o mesmo que ja acontece com todo drop normal de 2%% ou mais
# neste servidor (item_rate_equip 5000 com item_drop_equip_max 10000).
#
# --------------------------------------------------------- como recarregar
#
# `@reloadmobdb` em jogo - ele chama mob_reload(), que refaz o map_drop_db
# (src/map/mob.cpp linha 7216). `@reloaditemdb` e `@reloadscript` nao pegam.
###########################################################################

Header:
  Type: MAP_DROP_DB
  Version: 2

Body:
'''


if __name__ == '__main__':
    sys.exit(main())
