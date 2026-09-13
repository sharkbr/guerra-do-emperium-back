# -*- coding: utf-8 -*-
# Extrator minimo de GRF 0x200 para Python 2.7 - com o DES da Gravity desde
# 2026-09-13 (antes recusava toda entrada com `flags & 6`).
#
# O "DES" do GRF nao e o DES de verdade: e UMA rodada, sem chave, mais um
# embaralhamento de bytes a cada sete blocos. E a porta do `src/common/des.cpp`
# e do `grf_decode` do `src/common/grfio.cpp` do rAthena, que estao no vendor
# e sao a referencia - as tabelas abaixo foram copiadas de la, nao reescritas.
# Roda sobre os bytes COMPRIMIDOS, antes do zlib; so os 20 primeiros blocos
# de 8 bytes sao sempre cifrados, o resto e periodico, entao mesmo um sprite
# de 300 KB sai em segundos.
import struct, zlib, sys, os

_MASK = (0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01)

_IP = (58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4,
       62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8,
       57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3,
       61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7)

_FP = (40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31,
       38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29,
       36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27,
       34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25)

_TP = (16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10,
       2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25)

_S = (
    (0xef, 0x03, 0x41, 0xfd, 0xd8, 0x74, 0x1e, 0x47, 0x26, 0xef, 0xfb, 0x22, 0xb3, 0xd8, 0x84, 0x1e,
     0x39, 0xac, 0xa7, 0x60, 0x62, 0xc1, 0xcd, 0xba, 0x5c, 0x96, 0x90, 0x59, 0x05, 0x3b, 0x7a, 0x85,
     0x40, 0xfd, 0x1e, 0xc8, 0xe7, 0x8a, 0x8b, 0x21, 0xda, 0x43, 0x64, 0x9f, 0x2d, 0x14, 0xb1, 0x72,
     0xf5, 0x5b, 0xc8, 0xb6, 0x9c, 0x37, 0x76, 0xec, 0x39, 0xa0, 0xa3, 0x05, 0x52, 0x6e, 0x0f, 0xd9),
    (0xa7, 0xdd, 0x0d, 0x78, 0x9e, 0x0b, 0xe3, 0x95, 0x60, 0x36, 0x36, 0x4f, 0xf9, 0x60, 0x5a, 0xa3,
     0x11, 0x24, 0xd2, 0x87, 0xc8, 0x52, 0x75, 0xec, 0xbb, 0xc1, 0x4c, 0xba, 0x24, 0xfe, 0x8f, 0x19,
     0xda, 0x13, 0x66, 0xaf, 0x49, 0xd0, 0x90, 0x06, 0x8c, 0x6a, 0xfb, 0x91, 0x37, 0x8d, 0x0d, 0x78,
     0xbf, 0x49, 0x11, 0xf4, 0x23, 0xe5, 0xce, 0x3b, 0x55, 0xbc, 0xa2, 0x57, 0xe8, 0x22, 0x74, 0xce),
    (0x2c, 0xea, 0xc1, 0xbf, 0x4a, 0x24, 0x1f, 0xc2, 0x79, 0x47, 0xa2, 0x7c, 0xb6, 0xd9, 0x68, 0x15,
     0x80, 0x56, 0x5d, 0x01, 0x33, 0xfd, 0xf4, 0xae, 0xde, 0x30, 0x07, 0x9b, 0xe5, 0x83, 0x9b, 0x68,
     0x49, 0xb4, 0x2e, 0x83, 0x1f, 0xc2, 0xb5, 0x7c, 0xa2, 0x19, 0xd8, 0xe5, 0x7c, 0x2f, 0x83, 0xda,
     0xf7, 0x6b, 0x90, 0xfe, 0xc4, 0x01, 0x5a, 0x97, 0x61, 0xa6, 0x3d, 0x40, 0x0b, 0x58, 0xe6, 0x3d),
    (0x4d, 0xd1, 0xb2, 0x0f, 0x28, 0xbd, 0xe4, 0x78, 0xf6, 0x4a, 0x0f, 0x93, 0x8b, 0x17, 0xd1, 0xa4,
     0x3a, 0xec, 0xc9, 0x35, 0x93, 0x56, 0x7e, 0xcb, 0x55, 0x20, 0xa0, 0xfe, 0x6c, 0x89, 0x17, 0x62,
     0x17, 0x62, 0x4b, 0xb1, 0xb4, 0xde, 0xd1, 0x87, 0xc9, 0x14, 0x3c, 0x4a, 0x7e, 0xa8, 0xe2, 0x7d,
     0xa0, 0x9f, 0xf6, 0x5c, 0x6a, 0x09, 0x8d, 0xf0, 0x0f, 0xe3, 0x53, 0x25, 0x95, 0x36, 0x28, 0xcb),
)

# grf_substitution: simetrica, so estes 14 bytes trocam de lugar.
_SUBST = {0x00: 0x2B, 0x2B: 0x00, 0x6C: 0x80, 0x01: 0x68, 0x68: 0x01,
          0x48: 0x77, 0x60: 0xFF, 0x77: 0x48, 0xB9: 0xC0, 0xC0: 0xB9,
          0xFE: 0xEB, 0xEB: 0xFE, 0x80: 0x6C, 0xFF: 0x60}


def _permuta(b, tabela, alvo_desloc, fonte_desloc):
    tmp = bytearray(8)
    for i, t in enumerate(tabela):
        j = t - 1
        if b[((j >> 3) & 7) + fonte_desloc] & _MASK[j & 7]:
            tmp[((i >> 3) & 7) + alvo_desloc] |= _MASK[i & 7]
    return tmp


def _rodada(b):
    # E: os 4 bytes de cima (32 bits) viram oito grupos de 6 bits
    e = bytearray(8)
    e[0] = ((b[7] << 5) | (b[4] >> 3)) & 0x3f
    e[1] = ((b[4] << 1) | (b[5] >> 7)) & 0x3f
    e[2] = ((b[4] << 5) | (b[5] >> 3)) & 0x3f
    e[3] = ((b[5] << 1) | (b[6] >> 7)) & 0x3f
    e[4] = ((b[5] << 5) | (b[6] >> 3)) & 0x3f
    e[5] = ((b[6] << 1) | (b[7] >> 7)) & 0x3f
    e[6] = ((b[6] << 5) | (b[7] >> 3)) & 0x3f
    e[7] = ((b[7] << 1) | (b[4] >> 7)) & 0x3f
    # S-boxes: dois nibbles por passo
    s = bytearray(8)
    for i in range(4):
        s[i] = (_S[i][e[i * 2]] & 0xf0) | (_S[i][e[i * 2 + 1]] & 0x0f)
    # P-box: le s[0..3], escreve tmp[4..7]
    t = _permuta(s, _TP, 4, 0)
    b[0] ^= t[4]
    b[1] ^= t[5]
    b[2] ^= t[6]
    b[3] ^= t[7]


def _des_bloco(b):
    x = _permuta(b, _IP, 0, 0)
    _rodada(x)
    return _permuta(x, _FP, 0, 0)


def _desembaralha(b):
    return bytearray([b[3], b[4], b[6], b[0], b[1], b[2], b[5], _SUBST.get(b[7], b[7])])


def grf_decode(dados, flags, tamanho_real):
    """Decifra os bytes comprimidos de uma entrada, como o grf_decode do rAthena.

    `dados` e o bloco alinhado (csize_align bytes); `tamanho_real` e o csize
    sem alinhamento, que e o que escolhe o periodo do modo misto.
    """
    buf = bytearray(dados)
    nblocos = len(buf) // 8
    if flags & 0x02:      # misto: cabecalho + periodico + embaralhado
        digitos = 1
        i = 10
        while i <= tamanho_real:
            digitos += 1
            i *= 10
        if digitos < 3:
            ciclo = 1
        elif digitos < 5:
            ciclo = digitos + 1
        elif digitos < 7:
            ciclo = digitos + 9
        else:
            ciclo = digitos + 15
        for i in range(min(20, nblocos)):
            buf[i * 8:i * 8 + 8] = _des_bloco(buf[i * 8:i * 8 + 8])
        j = -1
        for i in range(20, nblocos):
            if i % ciclo == 0:
                buf[i * 8:i * 8 + 8] = _des_bloco(buf[i * 8:i * 8 + 8])
                continue
            j += 1
            if j % 7 == 0 and j != 0:
                buf[i * 8:i * 8 + 8] = _desembaralha(buf[i * 8:i * 8 + 8])
    elif flags & 0x04:    # so o cabecalho
        for i in range(min(20, nblocos)):
            buf[i * 8:i * 8 + 8] = _des_bloco(buf[i * 8:i * 8 + 8])
    return bytes(buf)


class Grf(object):
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        head = self.f.read(46)
        sig = head[0:15]
        if sig != 'Master of Magic':
            raise Exception('assinatura invalida: %r' % sig)
        self.table_off, seed, count_raw, self.version = struct.unpack('<IIII', head[30:46])
        self.count = count_raw - seed - 7
        self.entries = {}
        self._read_table()

    def _read_table(self):
        self.f.seek(46 + self.table_off)
        clen, ulen = struct.unpack('<II', self.f.read(8))
        table = zlib.decompress(self.f.read(clen))
        assert len(table) == ulen
        p = 0
        n = len(table)
        for _ in range(self.count):
            z = table.index('\x00', p)
            name = table[p:z]
            p = z + 1
            csize, csize_align, rsize, flags, offset = struct.unpack('<IIIBI', table[p:p+17])
            p += 17
            self.entries[name.lower()] = (csize, csize_align, rsize, flags, offset, name)
            if p >= n:
                break

    def read(self, name):
        e = self.entries[name.lower().replace('/', '\\')]
        csize, csize_align, rsize, flags, offset, real = e
        self.f.seek(46 + offset)
        bruto = self.f.read(csize_align)
        if flags & 6:
            bruto = grf_decode(bruto, flags, csize)
        dados = zlib.decompress(bruto[:csize])
        if len(dados) != rsize:
            raise Exception('tamanho errado depois de decifrar %s: %d != %d' % (real, len(dados), rsize))
        return dados

if __name__ == '__main__':
    g = Grf(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == 'find':
        pat = sys.argv[3].lower()
        for k in sorted(g.entries):
            if pat in k:
                e = g.entries[k]
                print '%s\t%d bytes\tflags=%d' % (e[5], e[2], e[3])
    elif cmd == 'getlike':
        # extrai o unico arquivo cujo nome contem o padrao (ASCII), ignorando o
        # trecho coreano do caminho, que nao sobrevive ao argv do console
        pat = sys.argv[3].lower()
        hits = sorted(k for k in g.entries if pat in k)
        idx = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        if not hits or idx >= len(hits):
            print 'sem hit utilizavel; achei %d: %s' % (len(hits), hits[:5])
            sys.exit(1)
        data = g.read(hits[idx])
        fh = open(sys.argv[4], 'wb'); fh.write(data); fh.close()
        print 'ok %d bytes -> %s' % (len(data), sys.argv[4])
    elif cmd == 'get':
        data = g.read(sys.argv[3])
        out = sys.argv[4]
        fh = open(out, 'wb')
        fh.write(data)
        fh.close()
        print 'ok %d bytes -> %s' % (len(data), out)
