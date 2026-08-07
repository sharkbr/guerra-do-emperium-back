# -*- coding: utf-8 -*-
"""BSON minimo, so o que os `contentdata\\*.bson` do cliente usam.

Le e ESCREVE byte a byte identico ao original - e isso e requisito, nao
capricho. Nao existe `bson` no Python 2.7 desta maquina, e o pymongo traria
tipos (ObjectId, datetime) que estes arquivos nao tem e uma ordem de chave que
nao e a do arquivo. Aqui a ordem e preservada porque documento e uma LISTA de
pares, nao um dicionario: o cliente numera as entradas por chave ("1", "2"),
entao a ordem nao muda nada para ele - mas um round-trip que nao bate deixa de
provar que o escritor esta certo, e essa prova e a unica defesa contra gravar
um arquivo que o cliente rejeita calado.

Tipos tratados, que sao os quatro que aparecem nos dois arquivos de reputacao:

    0x02 string (UTF-8, com terminador)   0x03 documento
    0x04 array (documento de chaves "0", "1", ...)
    0x10 int32

Qualquer outro tipo levanta excecao em vez de ser pulado: arquivo com tipo
novo tem que parar a ferramenta, nao virar dado perdido na regravacao.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import struct

DOC = 0x03
ARR = 0x04
STR = 0x02
I32 = 0x10


class Doc(list):
    """Documento BSON: lista de pares (chave, valor), na ordem do arquivo."""

    def get(self, chave, padrao=None):
        for k, v in self:
            if k == chave:
                return v
        return padrao

    def set(self, chave, valor):
        """Troca o valor de uma chave existente, no lugar em que ela esta."""
        for i, (k, _) in enumerate(self):
            if k == chave:
                self[i] = (chave, valor)
                return
        raise KeyError(chave)


class Arr(list):
    """Array BSON. So existe para se distinguir de `Doc` na hora de gravar."""


def _cstr(b, p):
    z = b.index('\x00', p)
    return b[p:z], z + 1


def _le_doc(b, p, arr=False):
    tam, = struct.unpack_from('<i', b, p)
    fim = p + tam - 1
    p += 4
    saida = Arr() if arr else Doc()
    while p < fim:
        t = ord(b[p])
        p += 1
        chave, p = _cstr(b, p)
        if t == STR:
            n, = struct.unpack_from('<i', b, p)
            p += 4
            valor = b[p:p + n - 1]
            p += n
        elif t in (DOC, ARR):
            valor, p = _le_doc(b, p, t == ARR)
        elif t == I32:
            valor, = struct.unpack_from('<i', b, p)
            p += 4
        else:
            raise ValueError('tipo BSON 0x%02x nao tratado, na chave %r'
                             % (t, chave))
        saida.append(valor if arr else (chave, valor))
    if ord(b[fim]) != 0:
        raise ValueError('documento sem terminador em %d' % fim)
    return saida, fim + 1


def _grava_doc(d):
    corpo = []
    pares = [(str(i), v) for i, v in enumerate(d)] if isinstance(d, Arr) else d
    for chave, valor in pares:
        if isinstance(valor, Arr):
            corpo.append(chr(ARR) + chave + '\x00' + _grava_doc(valor))
        elif isinstance(valor, Doc):
            corpo.append(chr(DOC) + chave + '\x00' + _grava_doc(valor))
        elif isinstance(valor, str):
            corpo.append(chr(STR) + chave + '\x00' +
                         struct.pack('<i', len(valor) + 1) + valor + '\x00')
        elif isinstance(valor, int):
            corpo.append(chr(I32) + chave + '\x00' + struct.pack('<i', valor))
        else:
            raise TypeError('valor %r (%s) na chave %r nao e gravavel'
                            % (valor, type(valor).__name__, chave))
    corpo = ''.join(corpo)
    return struct.pack('<i', len(corpo) + 5) + corpo + '\x00'


def loads(b):
    d, fim = _le_doc(b, 0)
    if fim != len(b):
        raise ValueError('sobraram %d bytes depois do documento'
                         % (len(b) - fim))
    return d


def dumps(d):
    return _grava_doc(d)
