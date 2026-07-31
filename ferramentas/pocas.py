# -*- coding: utf-8 -*-
"""Poças de água no chão de um mapa, pelos pontos onde a água empoçaria.

Python 2.7, como o resto de ferramentas/.

**Não existe modelo de poça no GRF.** Procurado por `웅덩이` (poça), `연못`
(lago), `수면` (superfície d'água) e `개울` (riacho): zero resultados. E o plano
de água do `.rsw` é global -- um nível único para o mapa inteiro (Izlude usa 45),
então não serve para poça local.

A saída é pintar o chão. Cada superfície do `.gnd` tem uma cor BGRA que o
cliente multiplica pela textura, então escurecer e esfriar um punhado de tiles
dá chão molhado **sem trocar textura nenhuma**: zero arquivo novo, zero memória
de vídeo. E fica mais natural que a alternativa -- havia 320 texturas de água
em `data\\texture\\워터\\`, mas são quadros de uma animação, e um quadro estático
sobre paralelepípedo vira mancha azul chapada.

Onde: os pontos mais BAIXOS do terreno andável. O eixo Y de RO aponta para
baixo, então mais baixo é o **maior** valor de altura -- é o erro fácil aqui.
Fica de fora tudo que estiver abaixo do nível da água, senão as "poças" cairiam
no mar de Izlude, que já é água e nem é andável.

Uso:
    python pocas.py <pasta-entrada> <pasta-saida> [mapa]
"""

import os
import random
import sys

from gat import Gat
from gnd import Gnd


SEMENTE = 20260731

QUANTAS = 7          # poucas, como pedido
RAIO = 1             # em tiles do .gnd; 1 = 3x3 tiles = 30x30 unidades
DISTANCIA_MINIMA = 6  # tiles entre duas poças, para nao virarem uma mancha só

# Molhado = escuro e frio. O azul cai bem menos que o vermelho, que é o
# oposto do que se faz para sujar (ver destroi_mapa.py) -- lá o objetivo era
# poeira, aqui é água.
CENTRO = (0.42, 0.52, 0.68)   # R, G, B no centro da poça
BORDA = (0.72, 0.78, 0.88)    # na borda, para nao virar um quadrado

MARGEM_AGUA = 6.0    # unidades acima do nível da água, para não pegar o mar


def escala_por_distancia(d, raio):
    """Interpola centro->borda. Fora do raio, 1.0 (não mexe)."""
    if d > raio:
        return (1.0, 1.0, 1.0)
    t = 0.0 if raio == 0 else float(d) / raio
    return tuple(CENTRO[i] + (BORDA[i] - CENTRO[i]) * t for i in range(3))


def candidatos(g, gat, nivel_agua):
    """Tiles andáveis, acima da água, ordenados do mais baixo para o mais alto.

    Um tile do .gnd tem 2x2 células do .gat. Exige-se que **todas** sejam
    andáveis: poça em cima de parede não faz sentido, e a borda do tile
    andável costuma ser degrau.
    """
    saida = []
    for ty in range(1, g.altura - 1):
        for tx in range(1, g.largura - 1):
            if g.superficie_topo(tx, ty) < 0:
                continue
            cx, cy = tx * 2, ty * 2
            if not all(gat.andavel(cx + dx, cy + dy)
                       for dx in (0, 1) for dy in (0, 1)):
                continue
            h = g.altura_tile(tx, ty)
            if h > nivel_agua - MARGEM_AGUA:   # Y para baixo: maior = mais fundo
                continue
            saida.append((h, tx, ty))
    saida.sort(reverse=True)   # do mais baixo (maior h) para o mais alto
    return saida


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1
    ent, sai = sys.argv[1], sys.argv[2]
    mapa = sys.argv[3] if len(sys.argv) > 3 else 'izlude'
    if mapa.lower().startswith('prontera'):
        print 'recusado: Prontera fica intacta por decisao de ficcao.'
        return 3
    if not os.path.isdir(sai):
        os.makedirs(sai)

    g = Gnd(open(os.path.join(ent, mapa + '.gnd'), 'rb').read())
    ok, msg = g.verificar()
    if not ok:
        print 'gnd nao passou na verificacao: %s' % msg
        return 2
    gat = Gat(open(os.path.join(ent, mapa + '.gat'), 'rb').read())

    # o nivel da agua vem do .rsw; Izlude usa 45
    nivel = 45.0
    caminho_rsw = os.path.join(ent, mapa + '.rsw')
    if os.path.exists(caminho_rsw):
        from rsw import Rsw
        nivel = Rsw(open(caminho_rsw, 'rb').read()).agua_nivel

    cand = candidatos(g, gat, nivel)
    print 'nivel da agua %.1f; %d tiles andaveis acima dela' % (nivel,
                                                                len(cand))
    if not cand:
        print 'nenhum candidato'
        return 2
    print 'faixa de altura dos candidatos: %.1f (mais baixo) .. %.1f' % (
        cand[0][0], cand[-1][0])

    rnd = random.Random(SEMENTE)
    escolhidas = []
    for h, tx, ty in cand:
        if len(escolhidas) >= QUANTAS:
            break
        if any(abs(tx - ex) < DISTANCIA_MINIMA and abs(ty - ey) < DISTANCIA_MINIMA
               for _, ex, ey in escolhidas):
            continue
        escolhidas.append((h, tx, ty))

    pintadas = 0
    for h, tx, ty in escolhidas:
        for dy in range(-RAIO, RAIO + 1):
            for dx in range(-RAIO, RAIO + 1):
                d = max(abs(dx), abs(dy))
                i = g.superficie_topo(tx + dx, ty + dy)
                if i < 0:
                    continue
                e = escala_por_distancia(d, RAIO)
                s = g.superficies[i]
                b, gr, r, a = g.cor(s)
                g.set_cor(s, (min(255, int(b * e[2])),
                              min(255, int(gr * e[1])),
                              min(255, int(r * e[0])), a))
                pintadas += 1

    open(os.path.join(sai, mapa + '.gnd'), 'wb').write(g.to_bytes())
    conf = Gnd(open(os.path.join(sai, mapa + '.gnd'), 'rb').read())
    ok, msg = conf.verificar()

    print
    print '%d pocas, %d superficies pintadas, reabre: %s' % (
        len(escolhidas), pintadas, msg)
    print 'onde (coordenada de jogo, para conferir com @warp %s x y):' % mapa
    for h, tx, ty in escolhidas:
        print '  altura %6.1f   @warp %s %d %d' % (h, mapa, tx * 2, ty * 2)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
