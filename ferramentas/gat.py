# -*- coding: utf-8 -*-
"""Leitor de .gat (colisao e altura andavel de um mapa de RO).

Python 2.7, como o resto de ferramentas/.

O .gat e a unica camada de mapa que o **servidor** tambem le -- e dele que o
map_cache.dat do rAthena e gerado. Por isso a frente visual nao escreve .gat:
so le, para saber onde da para pisar e em que altura o chao esta.

Resolucao: o .gat tem o **dobro** da resolucao do .gnd em cada eixo (uma celula
de .gat e um quarto de tile de .gnd). Confirmado em izlude: .gnd 134x150,
.gat 268x300, e 268*300*20 + 14 = 1608014 bytes, que e o tamanho exato do
arquivo.

Tipos de celula (o que o rAthena chama de terrain type):
    0 andavel           1 bloqueado        2 andavel (agua rasa)
    3 andavel/atiravel  4 andavel          5 atiravel, nao andavel
    6 andavel
"""

import struct
import sys


ANDAVEL = set([0, 2, 3, 4, 6])


class Gat(object):

    CABECALHO = 14
    TAM_CELULA = 20   # 4 floats de altura + int32 de tipo

    def __init__(self, dados):
        b = dados
        if b[:4] != 'GRAT':
            raise ValueError('nao e um .gat: magic %r' % b[:4])
        self.maior = ord(b[4])
        self.menor = ord(b[5])
        self.largura, self.altura = struct.unpack_from('<ii', b, 6)
        esperado = self.CABECALHO + self.largura * self.altura * self.TAM_CELULA
        if len(b) != esperado:
            raise ValueError('tamanho nao bate: %d, esperado %d'
                             % (len(b), esperado))
        self._b = b

    def _off(self, cx, cy):
        return self.CABECALHO + (cy * self.largura + cx) * self.TAM_CELULA

    def alturas(self, cx, cy):
        """Os 4 cantos da celula."""
        return struct.unpack_from('<4f', self._b, self._off(cx, cy))

    def altura_media(self, cx, cy):
        h = self.alturas(cx, cy)
        return sum(h) / 4.0

    def tipo(self, cx, cy):
        return struct.unpack_from('<i', self._b, self._off(cx, cy) + 16)[0]

    def andavel(self, cx, cy):
        if not (0 <= cx < self.largura and 0 <= cy < self.altura):
            return False
        return self.tipo(cx, cy) in ANDAVEL

    def plano_e_livre(self, cx, cy, raio, tolerancia=0.6):
        """A celula e o quadrado de `raio` em volta sao andaveis e nivelados?"""
        base = self.altura_media(cx, cy)
        for y in range(cy - raio, cy + raio + 1):
            for x in range(cx - raio, cx + raio + 1):
                if not self.andavel(x, y):
                    return False
                if abs(self.altura_media(x, y) - base) > tolerancia:
                    return False
        return True


def main():
    if len(sys.argv) < 2:
        print __doc__
        print 'uso: python gat.py <mapa.gat>'
        return 1

    g = Gat(open(sys.argv[1], 'rb').read())
    print 'versao   %d.%d' % (g.maior, g.menor)
    print 'celulas  %d x %d' % (g.largura, g.altura)

    tipos = {}
    hmin, hmax = 1e9, -1e9
    for cy in range(0, g.altura, 3):
        for cx in range(0, g.largura, 3):
            t = g.tipo(cx, cy)
            tipos[t] = tipos.get(t, 0) + 1
            h = g.altura_media(cx, cy)
            hmin = min(hmin, h)
            hmax = max(hmax, h)
    print 'tipos (amostra de 1 em 9):'
    for t in sorted(tipos):
        print '  %d  %6d  %s' % (t, tipos[t],
                                 'andavel' if t in ANDAVEL else 'bloqueado')
    print 'altura   %.1f .. %.1f' % (hmin, hmax)
    return 0


if __name__ == '__main__':
    sys.exit(main())
