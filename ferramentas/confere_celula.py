# -*- coding: utf-8 -*-
u"""Diz se uma celula e andavel, e acha lugar bom para nascer coisa.

    python confere_celula.py 1@gl_he 150,46 151,71 148,67
    python confere_celula.py 1@gl_he2 --salas 8      # as 8 maiores areas abertas
    python confere_celula.py 1@gl_he2 --perto 150,100

POR QUE ISTO EXISTE

Coordenada de spawn escrita a olho, ou copiada de um mapa parecido, produz
uma falha das caras: o monstro nasce (ou nao nasce) e nada aparece no log.
O `mob_spawn` sorteia em `map_search_freecell`, entao celula fechada vira
"o bicho nasceu em outro lugar" e nao "erro"; e NPC plantado em celula
fechada fica inalcancavel. A secao 5 do CLAUDE.md ja traz o caso do
`vis_h01`, que tem um pedaco andavel SOLTO em y=239 - monstro sorteado ali
nunca e achado.

DE ONDE VEM A RESPOSTA

Do `map_cache.dat` do proprio servidor, que e o que o rAthena de fato le -
nao do `.gat` do GRF. Isso importa por dois motivos:

  1. metade dos `.gat` de mapa de instancia esta cifrada com DES no
     data.grf (o `1@gl_k.gat` esta), e o grf.py recusa - ler dali daria
     "mapa nao existe" sobre um mapa que existe;
  2. sao TRES map_cache e o primeiro que tiver o mapa vence
     (`map.cpp:3922`): db/import, db/re e db/. Uma ferramenta que abra so
     o db/map_cache.dat responde pelo mapa errado - e a `prontera` de
     renewal, por exemplo, so existe no db/re.

Esta ferramenta percorre os tres na ordem certa e diz de qual veio.

O QUE `--salas` FAZ

Varre os pedacos conectados de chao andavel e devolve, de cada um dos
maiores, o ponto mais "no meio" - o de maior distancia ate a parede mais
proxima. E o que se quer para plantar chefe, portal ou grupo de monstro:
lugar aberto o bastante para o combate acontecer e longe de canto.

O tamanho de cada pedaco tambem responde a pergunta que o `vis_h01`
levantou: pedaco de 400 celulas solto no canto do mapa e ruido do .gat, e
nao sala.
"""

import os
import struct
import sys
import zlib
from collections import deque

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHES = [
    os.path.join(RAIZ, 'rathena', 'db', 'import', 'map_cache.dat'),
    os.path.join(RAIZ, 'rathena', 'db', 're', 'map_cache.dat'),
    os.path.join(RAIZ, 'rathena', 'db', 'map_cache.dat'),
]


def carrega(mapa):
    u"""(xs, ys, celulas, de_qual_cache) - percorrendo os tres na ordem do rAthena."""
    for caminho in CACHES:
        if not os.path.exists(caminho):
            continue
        aberto = open(caminho, 'rb')
        try:
            dados = aberto.read()
        finally:
            aberto.close()
        # cabecalho: uint32 file_size; uint16 map_count - e o compilador
        # alinha em 8, nao 6. Ler a partir do byte 6 desalinha o arquivo
        # inteiro e estoura umas dezenas de mapas adiante (CLAUDE.md 5).
        _tam, qtd = struct.unpack_from('<IH', dados, 0)
        pos = 8
        for _ in range(qtd):
            nome, xs, ys, ln = struct.unpack_from('<12shhi', dados, pos)
            pos += 20
            bruto = dados[pos:pos + ln]
            pos += ln
            if nome.split('\0')[0] == mapa:
                return xs, ys, zlib.decompress(bruto), caminho
    return None


def andavel(celulas, xs, x, y):
    return celulas[y * xs + x] == '\0'


def pedacos(xs, ys, celulas):
    u"""Os pedacos conectados de chao andavel, do maior para o menor."""
    visto = bytearray(xs * ys)
    fora = []
    for inicio in range(xs * ys):
        if visto[inicio] or celulas[inicio] != '\0':
            continue
        fila = deque([inicio])
        visto[inicio] = 1
        grupo = []
        while fila:
            i = fila.popleft()
            grupo.append(i)
            x, y = i % xs, i // xs
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < xs and 0 <= ny < ys:
                    j = ny * xs + nx
                    if not visto[j] and celulas[j] == '\0':
                        visto[j] = 1
                        fila.append(j)
        fora.append(grupo)
    fora.sort(key=len, reverse=True)
    return fora


def centro(xs, ys, celulas, grupo):
    u"""O ponto do grupo mais longe de qualquer parede (distancia de Chebyshev)."""
    dentro = set(grupo)
    melhor, melhor_d = None, -1
    for i in grupo:
        x, y = i % xs, i // xs
        d = 0
        while True:
            passo = d + 1
            if passo > 12:
                break
            ok = True
            for ax in range(x - passo, x + passo + 1):
                for ay in (y - passo, y + passo):
                    if (ay * xs + ax) not in dentro:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                for ay in range(y - passo, y + passo + 1):
                    for ax in (x - passo, x + passo):
                        if (ay * xs + ax) not in dentro:
                            ok = False
                            break
                    if not ok:
                        break
            if not ok:
                break
            d = passo
        if d > melhor_d:
            melhor, melhor_d = (x, y), d
    return melhor, melhor_d


def main(argv):
    if len(argv) < 2:
        print __doc__
        return 2
    mapa = argv[1]
    achado = carrega(mapa)
    if not achado:
        print u'%s nao esta em cache nenhum dos tres.' % mapa
        return 1
    xs, ys, celulas, cache = achado
    print u'%s  %dx%d  (de %s)' % (mapa, xs, ys,
                                   os.path.relpath(cache, RAIZ))

    if '--salas' in argv:
        quantas = int(argv[argv.index('--salas') + 1])
        grupos = pedacos(xs, ys, celulas)
        print u'  %d pedacos conectados; os %d maiores:' % (len(grupos), quantas)
        for g in grupos[:quantas]:
            (x, y), folga = centro(xs, ys, celulas, g)
            print u'    %6d celulas   centro %3d,%-3d   folga %d celulas' % (
                len(g), x, y, folga)
        sobra = sum(len(g) for g in grupos[quantas:])
        if sobra:
            print u'    (mais %d celulas em %d pedacos menores)' % (
                sobra, len(grupos) - quantas)
        return 0

    faltou = 0
    for arg in argv[2:]:
        if ',' not in arg:
            continue
        x, y = [int(v) for v in arg.split(',')]
        if not (0 <= x < xs and 0 <= y < ys):
            print u'  %3d,%-3d  FORA do mapa' % (x, y)
            faltou = 1
            continue
        ok = andavel(celulas, xs, x, y)
        # quanta folga em volta - um NPC precisa de pouco, um chefe de muito
        livres = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                     if 0 <= x + dx < xs and 0 <= y + dy < ys
                     and andavel(celulas, xs, x + dx, y + dy))
        print u'  %3d,%-3d  %-12s  %d das 9 celulas em volta livres' % (
            x, y, 'andavel' if ok else 'FECHADA', livres)
        if not ok:
            faltou = 1
    return faltou


if __name__ == '__main__':
    sys.exit(main(sys.argv))
