# -*- coding: utf-8 -*-
"""Mede a caixa envolvente de um modelo 3D (.rsm), NO A NO.

Python 2.7, como o resto de ferramentas/.

Por que existe: antes de plantar um modelo num mapa (`edita_mapa.py`) e preciso
saber o TAMANHO dele em unidades de mundo -- 5 unidades por celula -- para
decidir a escala. A escala oficial dos mapas da Gravity e boa PISTA e nao
resposta: ela veio do lugar de origem do modelo, que costuma ser maior que o
nosso (a fonte do Centro da Ordem entrou com o 1,0 de Glast Heim e ficou
grande num pedestal de 4 celulas).

**MEDIR NO A NO, E NAO TUDO NUMA CAIXA SO.** O `pos` do no raiz e um offset no
espaco do modelo, nao uma dimensao: juntar tudo num box unico soma esse offset
ao tamanho. No `desk_h_02.rsm` (4 nos, raiz em x = -129,35) a medida junta da
148,90 de largura -- 29,8 celulas em vez de 4,0 -- e o numero e plausivel o
bastante para condenar um modelo por "nao cabe". Ver CLAUDE.md secao 5.

**E a trava que prova que o leitor esta certo e sobrar 0 byte.** Formato de
malha e cheio de campo opcional por versao; um campo lido a menos desalinha
tudo o que vem depois e ainda assim devolve numeros. Se o arquivo nao for
consumido ate o fim, nada do que este script imprime vale.

**QUAL EIXO E A ALTURA: o Z.** Nao e o Y, e errar isto troca a profundidade
pela altura do movel -- o que da uma planta plausivel e errada, e ainda leva a
escolher a rotacao pelo lado errado. A prova nao e teorica, sao os proprios
modelos do salao medidos aqui: a coluna `내부소품\기둥2.rsm` da 6,34 x 6,34 x
30,21 e a estatua `모로코\동상.rsm` da 8,57 x 5,43 x 29,25 -- coluna e estatua
sao altas e finas, entao o eixo de 30 e o vertical. Ou seja:

    X = largura   Y = profundidade   Z = altura

e a PLANTA do movel e X x Y. (A medida ja publicada da escrivaninha,
"20,02 x 13,84 unidades, 4,0 x 2,8 celulas", e X x Y -- confere.)

Com isso vem de graca de que lado esta a FRENTE de um movel: o encosto de um
sofa e o lado do Y onde ele e ALTO. Nos dois sofas do Centro da Ordem o
encosto esta no lado **+Y**.

Uso:
    python mede_rsm.py <data.grf> <caminho do rsm sem o prefixo data\model\>

Ex.:
    python mede_rsm.py C:\GuerraDoEmperium\cliente\data.grf prontera/sofa_01.rsm

A barra pode ser normal: o caminho e normalizado aqui, porque barra invertida
no argv do console deste ambiente e uma dor.
"""

import struct
import sys

from grf import Grf


PREFIXO = 'data' + chr(92) + 'model' + chr(92)
POR_CELULA = 5.0     # unidades de mundo por celula de jogo


class Leitor(object):
    """Cursor sobre os bytes, com conta de quanto sobrou."""

    def __init__(self, dados):
        self.b = dados
        self.p = 0

    def bytes(self, n):
        v = self.b[self.p:self.p + n]
        self.p += n
        return v

    def i(self):
        v = struct.unpack_from('<i', self.b, self.p)[0]
        self.p += 4
        return v

    def h(self):
        v = struct.unpack_from('<h', self.b, self.p)[0]
        self.p += 2
        return v

    def f(self, n=1):
        v = struct.unpack_from('<%df' % n, self.b, self.p)
        self.p += 4 * n
        return v if n > 1 else v[0]

    def texto(self, n):
        return self.bytes(n).split('\x00')[0]

    def sobra(self):
        return len(self.b) - self.p


class No(object):
    def __init__(self, nome, pai, pos, vertices):
        self.nome = nome
        self.pai = pai
        self.pos = pos
        self.vertices = vertices

    def caixa(self):
        """(min, max) por eixo, NO ESPACO DO PROPRIO NO."""
        if not self.vertices:
            return None
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        return ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))


def le(dados):
    """[No], versao. Suporta .rsm 1.x e 2.x ate 2.3."""
    r = Leitor(dados)
    magic = r.bytes(4)
    if magic != 'GRSM':
        raise ValueError('nao e um .rsm: magic %r' % magic)
    maior, menor = ord(r.bytes(1)), ord(r.bytes(1))
    ver = maior * 10 + menor

    if ver >= 22:
        r.f()                      # frames por segundo
    r.i()                          # duracao da animacao
    r.i()                          # tipo de sombreamento
    if ver >= 14:
        r.bytes(1)                 # alfa
    if ver >= 23:
        r.f()                      # escala do modelo
    r.bytes(16)                    # reservado

    texturas = []
    if ver < 22:
        n_tex = r.i()
        for _ in range(n_tex):
            texturas.append(r.texto(40))

    raiz = r.texto(40)
    n_nos = r.i()

    nos = []
    for _ in range(n_nos):
        nome = r.texto(40)
        pai = r.texto(40)

        if ver >= 22:
            n_tex = r.i()
            for _ in range(n_tex):
                texturas.append(r.texto(40))
        else:
            n_tex = r.i()
            for _ in range(n_tex):
                r.i()

        r.f(9)                     # matriz de orientacao 3x3
        r.f(3)                     # offset dentro do pai
        pos = r.f(3)
        if ver < 22:
            r.f()                  # angulo de rotacao
            r.f(3)                 # eixo de rotacao
        escala = r.f(3)

        n_v = r.i()
        vertices = [r.f(3) for _ in range(n_v)]

        n_tv = r.i()
        for _ in range(n_tv):
            if ver >= 12:
                r.i()              # cor
            r.f(2)

        n_face = r.i()
        for _ in range(n_face):
            if ver >= 22:
                tam = r.i()
                fim = r.p + tam - 4
            else:
                fim = None
            r.bytes(6)             # 3 indices de vertice
            r.bytes(6)             # 3 indices de coordenada de textura
            r.h()                  # id da textura
            r.h()                  # padding
            r.i()                  # dois lados
            if ver >= 12:
                r.i()              # grupo de suavizacao
            if fim is not None:
                r.p = fim

        if ver >= ance_escala(ver):
            n_k = r.i()
            for _ in range(n_k):
                r.i()              # quadro
                r.f(3)             # escala
                r.f()              # dado

        n_r = r.i()
        for _ in range(n_r):
            r.i()                  # quadro
            r.f(4)                 # quaternio

        if ver >= 22:
            n_p = r.i()
            for _ in range(n_p):
                r.i()              # quadro
                r.f(3)             # posicao
                r.i()              # dado
            n_t = r.i()
            for _ in range(n_t):
                r.i()              # id da textura
                n_tk = r.i()
                for _ in range(n_tk):
                    r.i()
                    r.f()

        nos.append(No(nome, pai, pos, vertices))
        _ = escala

    # O RABICHO DEPOIS DOS NOS, e e ele que faz a trava dos 0 bytes fechar.
    # Sem ele o `sofa_01.rsm` sobra exatamente 8 bytes -- os dois contadores
    # abaixo, os dois zerados. Ler ate aqui e o que prova que a lista de nos
    # terminou onde o leitor achou que terminou.
    if ver < 16:
        n_pk = r.i()               # quadros de posicao do modelo inteiro
        for _ in range(n_pk):
            r.i()                  # quadro
            r.f(3)                 # posicao
    n_vol = r.i()                  # caixas de volume (colisao interna)
    for _ in range(n_vol):
        r.f(3)                     # tamanho
        r.f(3)                     # posicao
        r.f(3)                     # rotacao
        if ver >= 13:
            r.i()                  # flag

    return nos, ver, r.sobra(), raiz, texturas


def ance_escala(ver):
    """A partir de que versao existe a lista de quadros de escala."""
    return 15


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1
    caminho_grf, alvo = sys.argv[1], sys.argv[2]
    interno = (PREFIXO + alvo.replace('/', chr(92))).lower()

    g = Grf(caminho_grf)
    if interno not in g.entries:
        print 'nao esta neste GRF: %s' % interno
        return 2
    dados = g.read(interno)

    nos, ver, sobra, raiz, texturas = le(dados)
    print '%s  (versao %d.%d, %d bytes, %d nos, raiz "%s")' % (
        alvo, ver // 10, ver % 10, len(dados), len(nos), raiz)
    if sobra != 0:
        print 'ABORTADO: sobraram %d bytes -- o leitor esta desalinhado e' % sobra
        print 'NENHUM numero acima ou abaixo vale.'
        return 3
    print 'trava do leitor: 0 bytes sobrando, arquivo consumido inteiro.'
    print

    print '-- no a no, na caixa do proprio no (X largura, Y profundidade, Z altura) --'
    print '%-22s %8s %8s %8s   %s' % ('no', 'X larg', 'Y prof', 'Z alt',
                                      'planta em celulas')
    maior = None
    for n in nos:
        c = n.caixa()
        if c is None:
            print '%-22s  (sem vertice)' % n.nome
            continue
        (x0, y0, z0), (x1, y1, z1) = c
        dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
        print '%-22s %8.2f %8.2f %8.2f   %.1f x %.1f' % (
            n.nome, dx, dy, dz, dx / POR_CELULA, dy / POR_CELULA)
        if maior is None or dx * dy > maior[0]:
            maior = (dx * dy, n.nome, dx, dy, dz, c)

    if maior:
        _, nome, dx, dy, dz, c = maior
        print
        print 'O NO DE MAIOR PLANTA e "%s": %.2f x %.2f unidades' % (nome, dx, dy)
        print '   = %.2f x %.2f CELULAS, altura %.2f (%.2f celulas)' % (
            dx / POR_CELULA, dy / POR_CELULA, dz, dz / POR_CELULA)
        print '   caixa: min %s  max %s' % (
            tuple('%.2f' % v for v in c[0]), tuple('%.2f' % v for v in c[1]))

        # De que lado esta a FRENTE: o encosto/costas e o lado do Y onde o
        # modelo e alto. So faz sentido para movel; para peca radial nao diz
        # nada, e a saida mostra o numero para quem quiser julgar.
        v = [p for n in nos for p in n.vertices]
        zteto = max(p[2] for p in v)
        zpiso = min(p[2] for p in v)
        alto = [p for p in v if p[2] >= zpiso + 0.8 * (zteto - zpiso)]
        my = sum(p[1] for p in alto) / len(alto)
        meio = (min(p[1] for p in v) + max(p[1] for p in v)) / 2.0
        print '   parte ALTA em Y medio %.2f (meio da caixa %.2f) -> lado %sY' % (
            my, meio, '+' if my > meio else '-')

    # TEXTURA QUE FALTA NAO DA ERRO EM PARSER NENHUM -- da superficie quebrada
    # na tela. O edita_mapa.py so confere o caminho do .rsm; esta lista e a
    # outra metade, e tem de ser conferida contra o NOSSO GRF.
    print
    print '-- %d texturas, conferidas contra este GRF --' % len(texturas)
    prefixo_tex = 'data' + chr(92) + 'texture' + chr(92)
    faltam = 0
    for t in texturas:
        ok = (prefixo_tex + t).lower() in g.entries
        if not ok:
            faltam += 1
        print '   [%s] %s' % ('ok' if ok else 'FALTA',
                              t.decode('cp949', 'replace').encode('utf-8'))
    if faltam:
        print '   ATENCAO: %d textura(s) nao resolvem -- superficie quebrada na tela.' % faltam
    return 0


if __name__ == '__main__':
    sys.exit(main())
