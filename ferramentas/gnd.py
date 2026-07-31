# -*- coding: utf-8 -*-
"""Leitor e escritor de .gnd (a malha do chao de um mapa de RO).

Python 2.7, como o resto de ferramentas/.

O que interessa aqui: cada superficie de chao tem uma **cor BGRA propria**, que
o cliente multiplica pela textura na hora de desenhar. Escurecer e amarelar
essas cores deixa o chao sujo/encardido **sem trocar uma textura sequer** --
nenhum arquivo novo, nenhum byte a mais de memoria de video. E o jeito mais
barato que existe de mudar o aspecto do chao.

O outro caminho -- trocar os nomes de textura no cabecalho -- tambem esta aqui
(troca_textura), e continua barato desde que se aponte para textura que ja
existe no GRF: o custo e o mesmo de qualquer textura de mapa.

Validacao: to_bytes() de arquivo nao modificado devolve os bytes originais, e o
parser consome ate o ultimo byte. Ver main(), que roda as duas.
"""

import struct
import sys

from rsw import texto


class Gnd(object):

    TAM_SUPERFICIE = 40  # 8 floats de uv + int16 textura + uint16 lightmap + 4 de cor
    TAM_CUBO = 28        # 4 floats de altura + 3 int32 de superficie

    def __init__(self, dados):
        b = dados
        if b[:4] != 'GRGN':
            raise ValueError('nao e um .gnd: magic %r' % b[:4])
        self.maior = ord(b[4])
        self.menor = ord(b[5])
        if (self.maior, self.menor) != (1, 7):
            # 1.8 muda o bloco de lightmap. Parar em vez de corromper.
            raise ValueError('versao %d.%d nao conferida' % (self.maior,
                                                             self.menor))
        self.largura, self.altura = struct.unpack_from('<ii', b, 6)
        self.zoom = struct.unpack_from('<f', b, 14)[0]
        qtd_tex, self.tam_nome_tex = struct.unpack_from('<ii', b, 18)

        o = 26
        self.texturas = []
        for _ in range(qtd_tex):
            self.texturas.append(b[o:o + self.tam_nome_tex])
            o += self.tam_nome_tex

        qtd_lm, self.lm_largura, self.lm_altura, self.lm_celulas = \
            struct.unpack_from('<iiii', b, o)
        o += 16
        tam_lm = self.lm_largura * self.lm_altura * 4
        self.lightmaps = b[o:o + qtd_lm * tam_lm]
        o += qtd_lm * tam_lm

        qtd_sup = struct.unpack_from('<i', b, o)[0]
        o += 4
        self.superficies = []
        for _ in range(qtd_sup):
            crua = b[o:o + self.TAM_SUPERFICIE]
            self.superficies.append(bytearray(crua))
            o += self.TAM_SUPERFICIE

        self.cubos = b[o:]
        self._consumido = o
        self._original = dados

    # -- acesso as partes de uma superficie -------------------------------

    @staticmethod
    def id_textura(s):
        return struct.unpack_from('<h', str(s), 32)[0]

    @staticmethod
    def cor(s):
        """Devolve (b, g, r, a) -- e nessa ordem no arquivo."""
        return tuple(s[36:40])

    @staticmethod
    def set_cor(s, bgra):
        s[36:40] = bytearray(bgra)

    def to_bytes(self):
        p = ['GRGN', chr(self.maior), chr(self.menor),
             struct.pack('<ii', self.largura, self.altura),
             struct.pack('<f', self.zoom),
             struct.pack('<ii', len(self.texturas), self.tam_nome_tex)]
        p.extend(self.texturas)
        p.append(struct.pack('<iiii', len(self.lightmaps) //
                             (self.lm_largura * self.lm_altura * 4),
                             self.lm_largura, self.lm_altura, self.lm_celulas))
        p.append(self.lightmaps)
        p.append(struct.pack('<i', len(self.superficies)))
        for s in self.superficies:
            p.append(str(s))
        p.append(self.cubos)
        return ''.join(p)

    def verificar(self):
        esperado = self.largura * self.altura * self.TAM_CUBO
        if len(self.cubos) != esperado:
            return False, ('bloco de cubos tem %d bytes, esperado %d'
                           % (len(self.cubos), esperado))
        saida = self.to_bytes()
        if saida != self._original:
            for i in range(min(len(saida), len(self._original))):
                if saida[i] != self._original[i]:
                    return False, 'round-trip diverge no byte %d' % i
            return False, ('round-trip: tamanhos diferentes, %d vs %d'
                           % (len(saida), len(self._original)))
        return True, 'ok'

    # -- transformacoes ----------------------------------------------------

    def encardir(self, escala_rgb, piso=0):
        """Multiplica a cor de toda superficie por (r, g, b), saturando em 255.

        Escala < 1 escurece; escalas diferentes por canal tingem. Para "sujo"
        o que funciona e derrubar o azul mais que o vermelho -- o olho le
        deslocamento para o amarelo/terra como poeira e lama seca.

        `piso` evita que area ja escura vire preto chapado, o que apaga o
        relevo em vez de sujar.
        """
        mudadas = 0
        for s in self.superficies:
            b, g, r, a = self.cor(s)
            nb = max(piso, min(255, int(b * escala_rgb[2])))
            ng = max(piso, min(255, int(g * escala_rgb[1])))
            nr = max(piso, min(255, int(r * escala_rgb[0])))
            if (nb, ng, nr) != (b, g, r):
                self.set_cor(s, (nb, ng, nr, a))
                mudadas += 1
        return mudadas

    def troca_textura(self, de_indice, novo_nome):
        """Aponta um slot de textura para outro arquivo, mantendo o indice.

        Barato de proposito: nenhuma superficie e remapeada, so o nome muda.
        O nome precisa caber em tam_nome_tex e existir no GRF.
        """
        n = novo_nome + '\x00' * (self.tam_nome_tex - len(novo_nome))
        if len(n) != self.tam_nome_tex:
            raise ValueError('nome de textura longo demais: %r' % novo_nome)
        antes = self.texturas[de_indice]
        self.texturas[de_indice] = n
        return antes


def main():
    if len(sys.argv) < 2:
        print __doc__
        print 'uso: python gnd.py <arquivo.gnd>'
        return 1

    g = Gnd(open(sys.argv[1], 'rb').read())
    ok, msg = g.verificar()
    print 'versao       %d.%d' % (g.maior, g.menor)
    print 'round-trip   %s' % msg
    print 'tiles        %d x %d   (zoom %.1f)' % (g.largura, g.altura, g.zoom)
    print 'superficies  %d' % len(g.superficies)
    print

    uso = {}
    for s in g.superficies:
        i = g.id_textura(s)
        uso[i] = uso.get(i, 0) + 1
    print '%d texturas:' % len(g.texturas)
    for i, t in enumerate(g.texturas):
        print '  [%2d] %6d sup.  %s' % (i, uso.get(i, 0), texto(t))
    print

    cores = {}
    for s in g.superficies:
        cores[g.cor(s)] = cores.get(g.cor(s), 0) + 1
    print 'cores distintas de superficie: %d' % len(cores)
    for c in sorted(cores, key=lambda k: -cores[k])[:8]:
        print '  %6d  B%3d G%3d R%3d A%3d' % ((cores[c],) + c)

    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
