# -*- coding: utf-8 -*-
"""Leitor e escritor de .rsw (o arquivo de "mundo" de um mapa de RO).

Python 2.7, como o resto de ferramentas/.

O .rsw guarda o que define a atmosfera de um mapa e a lista de objetos
posicionados nele: modelos 3D, luzes, sons e efeitos. Nao guarda geometria
nenhuma -- os modelos sao referencias por nome de arquivo para .rsm dentro do
GRF. Por isso da para tombar, afundar, escalar e remover predio inteiro
mexendo SO neste arquivo, sem tocar em .rsm (que no GRF oficial estao atras da
flag DES e o nosso grf.py ainda nao le).

Validacao: to_bytes() do arquivo nao modificado tem que devolver os bytes
originais, identicos. E o parser tem que consumir o arquivo ate o ultimo byte.
Se qualquer uma das duas falhar, o layout esta errado e nao se escreve nada.
Ver a funcao main(), modo --verificar.
"""

import struct
import sys


def texto(s):
    """Nome de arquivo do .rsw -> utf-8 legivel.

    Os caminhos de modelo sao coreanos em CP949 (a pasta de Prontera e
    literalmente 'prontera' em hangul). Impressos crus viram mojibake.
    """
    s = s.split('\x00')[0]
    try:
        return s.decode('cp949').encode('utf-8')
    except UnicodeDecodeError:
        return s


def _u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def _i32(b, o):
    return struct.unpack_from('<i', b, o)[0]


def _f32(b, o):
    return struct.unpack_from('<f', b, o)[0]


class Modelo(object):
    """Um objeto do tipo 1: um .rsm posicionado no mapa."""

    TAMANHO = 248  # 40 + 4 + 4 + 4 + 80 + 80 + 12 + 12 + 12

    def __init__(self, b, o):
        self.nome = b[o:o + 40]
        self.anim_tipo = _i32(b, o + 40)
        self.anim_velocidade = _f32(b, o + 44)
        self.bloco_tipo = _i32(b, o + 48)
        self.arquivo = b[o + 52:o + 132]
        self.no = b[o + 132:o + 212]
        self.pos = list(struct.unpack_from('<3f', b, o + 212))
        self.rot = list(struct.unpack_from('<3f', b, o + 224))
        self.escala = list(struct.unpack_from('<3f', b, o + 236))

    def to_bytes(self):
        return (self.nome
                + struct.pack('<ifi', self.anim_tipo, self.anim_velocidade,
                              self.bloco_tipo)
                + self.arquivo
                + self.no
                + struct.pack('<3f', *self.pos)
                + struct.pack('<3f', *self.rot)
                + struct.pack('<3f', *self.escala))

    @property
    def rsm(self):
        """O nome do .rsm, em minusculas e sem o padding de zeros."""
        return self.arquivo.split('\x00')[0].lower().replace('/', '\\')


class Bruto(object):
    """Luz, som ou efeito. Nao mexemos neles -- guardamos os bytes crus.

    Precisamos so do tamanho certo para conseguir andar pela lista de objetos.
    """

    def __init__(self, tipo, b, o, tamanho):
        self.tipo = tipo
        self.dados = b[o:o + tamanho]

    def to_bytes(self):
        return self.dados


class Rsw(object):

    def __init__(self, dados):
        b = dados
        if b[:4] != 'GRSW':
            raise ValueError('nao e um .rsw: magic %r' % b[:4])
        self.maior = ord(b[4])
        self.menor = ord(b[5])
        v = self.maior * 10 + self.menor
        self.versao = v
        if v < 14 or v > 24:
            # 2.1 e o que o kRO 2021-11-03 usa. Fora dessa faixa o layout muda
            # (2.5 ganha buildNumber, 2.2 ganha um byte, 2.6 tira a agua) e este
            # parser nao foi conferido -- melhor parar que corromper.
            raise ValueError('versao %d.%d nao suportada' % (self.maior,
                                                             self.menor))

        o = 6
        self.ini = b[o:o + 40]
        self.gnd = b[o + 40:o + 80]
        self.gat = b[o + 80:o + 120]
        self.scr = b[o + 120:o + 160]
        o += 160

        # Agua
        self.agua_nivel = _f32(b, o)
        self.agua_tipo = _i32(b, o + 4)
        self.agua_altura_onda = _f32(b, o + 8)
        self.agua_velocidade_onda = _f32(b, o + 12)
        self.agua_inclinacao_onda = _f32(b, o + 16)
        self.agua_velocidade_anim = _i32(b, o + 20)
        o += 24

        # Luz
        self.luz_longitude = _i32(b, o)
        self.luz_latitude = _i32(b, o + 4)
        self.luz_difusa = list(struct.unpack_from('<3f', b, o + 8))
        self.luz_ambiente = list(struct.unpack_from('<3f', b, o + 20))
        self.luz_opacidade_sombra = _f32(b, o + 32)
        o += 36

        # Limites do chao
        self.chao = list(struct.unpack_from('<4i', b, o))
        o += 16

        # Objetos
        quantos = _i32(b, o)
        o += 4
        self.objetos = []
        for _ in range(quantos):
            tipo = _i32(b, o)
            o += 4
            if tipo == 1:
                obj = Modelo(b, o)
                o += Modelo.TAMANHO
            elif tipo == 2:
                obj = Bruto(2, b, o, 108)   # luz
                o += 108
            elif tipo == 3:
                # som: ganha um float de ciclo a partir da versao 2.0
                t = 192 if self.versao >= 20 else 188
                obj = Bruto(3, b, o, t)
                o += t
            elif tipo == 4:
                obj = Bruto(4, b, o, 116)   # efeito
                o += 116
            else:
                raise ValueError('tipo de objeto desconhecido: %d em %d'
                                 % (tipo, o - 4))
            self.objetos.append(obj)

        # Depois dos objetos vem a QuadTree: uma arvore de 5 niveis de
        # subdivisao, 1 + 4 + 16 + 64 + 256 + 1024 = 1365 nos de 48 bytes
        # (max, min, halfSize, center -- quatro vec3), 65520 bytes ao todo.
        # E indice espacial para descarte de geometria, derivado do .gnd; nao
        # depende da posicao dos modelos, entao mexer neles nao a invalida.
        self.quadtree = b[o:]
        self._consumido = o
        self._original = dados

    def to_bytes(self):
        p = ['GRSW', chr(self.maior), chr(self.menor),
             self.ini, self.gnd, self.gat, self.scr,
             struct.pack('<fifffi', self.agua_nivel, self.agua_tipo,
                         self.agua_altura_onda, self.agua_velocidade_onda,
                         self.agua_inclinacao_onda, self.agua_velocidade_anim),
             struct.pack('<ii', self.luz_longitude, self.luz_latitude),
             struct.pack('<3f', *self.luz_difusa),
             struct.pack('<3f', *self.luz_ambiente),
             struct.pack('<f', self.luz_opacidade_sombra),
             struct.pack('<4i', *self.chao),
             struct.pack('<i', len(self.objetos))]
        for obj in self.objetos:
            tipo = 1 if isinstance(obj, Modelo) else obj.tipo
            p.append(struct.pack('<i', tipo))
            p.append(obj.to_bytes())
        p.append(self.quadtree)
        return ''.join(p)

    @property
    def modelos(self):
        return [o for o in self.objetos if isinstance(o, Modelo)]

    QUADTREE = 1365 * 48

    def verificar(self):
        """Devolve (ok, mensagem). Round-trip byte a byte + consumo total."""
        if len(self.quadtree) != self.QUADTREE:
            return False, ('quadtree tem %d bytes, esperado %d -- o parser'
                           ' provavelmente saiu do trilho'
                           % (len(self.quadtree), self.QUADTREE))
        saida = self.to_bytes()
        if saida != self._original:
            for i in range(min(len(saida), len(self._original))):
                if saida[i] != self._original[i]:
                    return False, ('round-trip diverge no byte %d (%d vs %d)'
                                   % (i, len(saida), len(self._original)))
            return False, ('round-trip: tamanhos diferentes, %d vs %d'
                           % (len(saida), len(self._original)))
        return True, 'ok'


def main():
    if len(sys.argv) < 2:
        print __doc__
        print 'uso: python rsw.py <arquivo.rsw> [--verificar]'
        return 1

    dados = open(sys.argv[1], 'rb').read()
    r = Rsw(dados)

    ok, msg = r.verificar()
    print 'versao         %d.%d' % (r.maior, r.menor)
    print 'round-trip     %s' % msg
    print 'gnd/gat        %s / %s' % (r.gnd.split('\x00')[0],
                                      r.gat.split('\x00')[0])
    print
    print 'agua   nivel %.2f  tipo %d  onda alt %.2f vel %.2f incl %.2f  anim %d' % (
        r.agua_nivel, r.agua_tipo, r.agua_altura_onda,
        r.agua_velocidade_onda, r.agua_inclinacao_onda, r.agua_velocidade_anim)
    print 'luz    longitude %d  latitude %d  opacidade da sombra %.2f' % (
        r.luz_longitude, r.luz_latitude, r.luz_opacidade_sombra)
    print '       difusa   R %.3f  G %.3f  B %.3f' % tuple(r.luz_difusa)
    print '       ambiente R %.3f  G %.3f  B %.3f' % tuple(r.luz_ambiente)
    # Os 4 inteiros que a documentacao chama de limites do chao vem todos com o
    # mesmo valor grande neste arquivo. O alinhamento esta certo (a lista de
    # objetos depois dele parseia inteira e a quadtree fecha no byte exato),
    # entao o campo e isso mesmo -- so nao sabemos o que significa. Preservado
    # sem interpretar.
    print 'campo dos limites  %r' % (r.chao,)
    print

    tipos = {}
    for o in r.objetos:
        t = 1 if isinstance(o, Modelo) else o.tipo
        tipos[t] = tipos.get(t, 0) + 1
    print 'objetos  %d  (modelos %d, luzes %d, sons %d, efeitos %d)' % (
        len(r.objetos), tipos.get(1, 0), tipos.get(2, 0), tipos.get(3, 0),
        tipos.get(4, 0))
    print

    porrsm = {}
    for m in r.modelos:
        porrsm.setdefault(m.rsm, []).append(m)
    print '%d .rsm distintos:' % len(porrsm)
    for nome in sorted(porrsm, key=lambda n: -len(porrsm[n])):
        ms = porrsm[nome]
        ys = [m.pos[1] for m in ms]
        print '  %4d  y %8.1f..%-8.1f  %s' % (len(ms), min(ys), max(ys),
                                              texto(nome))

    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
