# -*- coding: utf-8 -*-
u"""Traduz o Setup.exe do cliente kRO do coreano para o portugues.

O Setup.exe da Gravity ja traz os dialogos em sete idiomas compilados dentro
dele. O idioma nao e escolhido por locale nem por arquivo de configuracao: o
codigo pede um ID de recurso fixo, e no build coreano esse ID e o do par
coreano. Os pares sao:

    103 / 104  ingles          107 / 108  chines simplificado
    105 / 106  coreano  <- em uso    110 / 111  chines tradicional
    112 / 139  portugues            140 / 141  russo
                                    142 / 143  japones

Em vez de reescrever recursos, este script faz o ID coreano apontar para os
bytes do par portugues, mexendo so no IMAGE_RESOURCE_DATA_ENTRY (8 bytes por
dialogo). Os dialogos originais continuam no arquivo, intactos.

Os tres botoes do rodape nao estao nos dialogos: sao literais CP949 em .rdata,
cada um com 1 referencia `push imm32` no codigo. Como "Cancelar" e "Restaurar"
nao cabem no slot original, as strings novas vao para o padding zerado do fim
da secao .text e as tres instrucoes passam a apontar para la.

Uso:
    python traduz_setup.py <Setup.exe>              # aplica (faz backup antes)
    python traduz_setup.py <Setup.exe> --verificar  # so relata, nao grava
"""
import os
import re
import shutil
import struct
import sys
import time

# ---------------------------------------------------------------- parametros

# dialogo coreano -> dialogo portugues
PARES = ((105, 112, u'aba Opcoes'), (106, 139, u'aba Sistema'))

# literal CP949 -> texto novo (ASCII puro: independe da codepage do sistema)
BOTOES = ((b'\xc8\xae\xc0\xce', b'OK', u'confirmar'),
          (b'\xc3\xeb\xbc\xd2', b'Cancelar', u'cancelar'),
          (b'\xc3\xca\xb1\xe2\xc8\xad', b'Restaurar', u'restaurar'))

RT_DIALOG = 5


class Erro(Exception):
    pass


# ---------------------------------------------------------------------- PE

class PE(object):
    def __init__(self, path):
        with open(path, 'rb') as fp:
            self.d = bytearray(fp.read())
        d = self.d
        self.pe = self.u32(0x3c)
        if bytes(d[self.pe:self.pe + 4]) != b'PE\0\0':
            raise Erro('%s nao e um PE' % path)
        nsec = self.u16(self.pe + 6)
        optsz = self.u16(self.pe + 20)
        self.opt = self.pe + 24
        self.imagebase = self.u32(self.opt + 28)
        self.sections = []
        so = self.pe + 24 + optsz
        for i in range(nsec):
            b = so + i * 40
            name = bytes(d[b:b + 8]).rstrip(b'\0').decode('ascii')
            vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', d, b + 8)
            self.sections.append((name, vaddr, vsize, raddr, rsize))
        dd = self.opt + 96                      # PE32
        self.res_rva = self.u32(dd + 2 * 8)
        self.checksum_off = self.opt + 64

    def u16(self, o):
        return struct.unpack_from('<H', self.d, o)[0]

    def u32(self, o):
        return struct.unpack_from('<I', self.d, o)[0]

    def rva2off(self, rva):
        for name, va, vs, ra, rs in self.sections:
            if va <= rva < va + max(vs, rs):
                return ra + (rva - va)
        return None

    def off2rva(self, off):
        for name, va, vs, ra, rs in self.sections:
            if ra <= off < ra + rs:
                return va + (off - ra)
        return None

    def data_entries(self):
        u"""{(tipo, id, lang): (offset_do_entry, rva, tamanho)}"""
        base = self.rva2off(self.res_rva)
        out = {}

        def rec(off, path):
            n = self.u16(off + 12) + self.u16(off + 14)
            for i in range(n):
                e = off + 16 + i * 8
                nameval, dataval = struct.unpack_from('<II', self.d, e)
                nm = 'str' if nameval & 0x80000000 else nameval
                if dataval & 0x80000000:
                    rec(base + (dataval & 0x7fffffff), path + [nm])
                else:
                    de = base + dataval
                    rva, size = struct.unpack_from('<II', self.d, de)
                    out[tuple(path + [nm])] = (de, rva, size)

        rec(base, [])
        return out

    def cave(self):
        u"""Padding zerado no fim de .text. Fica na ultima pagina da secao,
        portanto e mapeado na memoria, e nunca e referenciado pelo codigo."""
        name, va, vs, ra, rs = self.sections[0]
        if name != '.text':
            raise Erro('primeira secao nao e .text')
        off = ra + vs
        tam = rs - vs
        if any(self.d[off:ra + rs]):
            raise Erro('padding do fim de .text nao esta zerado')
        return off, va + vs, tam

    def checksum(self):
        u"""Checksum do PE conforme CheckSumMappedFile."""
        d = self.d
        soma = 0
        for i in range(0, len(d) - 1, 2):
            if self.checksum_off <= i < self.checksum_off + 4:
                continue
            soma += d[i] | (d[i + 1] << 8)
            soma = (soma & 0xffff) + (soma >> 16)
        if len(d) & 1:
            soma += d[-1]
            soma = (soma & 0xffff) + (soma >> 16)
        soma = (soma & 0xffff) + (soma >> 16)
        return (soma + len(d)) & 0xffffffff


# ------------------------------------------------------------------ patch

def localiza_botoes(pe):
    u"""Para cada literal coreano: (offset, site do push imm32, texto novo)."""
    achados = []
    for antigo, novo, nome in BOTOES:
        offs = [m.start() for m in re.finditer(re.escape(antigo), bytes(pe.d))]
        if len(offs) != 1:
            raise Erro(u'literal %s: esperava 1 ocorrencia, achei %d'
                       % (nome, len(offs)))
        off = offs[0]
        # o slot precisa terminar em NUL para o literal ser uma string C
        if pe.d[off + len(antigo)] != 0:
            raise Erro(u'literal %s nao termina em NUL' % nome)
        addr = pe.imagebase + pe.off2rva(off)
        sites = [m.start() for m in
                 re.finditer(re.escape(struct.pack('<I', addr)), bytes(pe.d))]
        if len(sites) != 1:
            raise Erro(u'literal %s: esperava 1 referencia, achei %d'
                       % (nome, len(sites)))
        site = sites[0]
        if pe.d[site - 1] != 0x68:
            raise Erro(u'referencia a %s nao e push imm32 (byte %02x)'
                       % (nome, pe.d[site - 1]))
        achados.append((off, site, novo, nome, addr))
    return achados


def aplica(path, verificar):
    pe = PE(path)
    de = pe.data_entries()
    relato = []

    # --- dialogos ---------------------------------------------------------
    planos = []
    for de_id, para_id, nome in PARES:
        origem = [v for k, v in de.items() if k[0] == RT_DIALOG and k[1] == de_id]
        destino = [v for k, v in de.items() if k[0] == RT_DIALOG and k[1] == para_id]
        if len(origem) != 1 or len(destino) != 1:
            raise Erro(u'dialogos %d/%d nao encontrados' % (de_id, para_id))
        entry, rva_a, size_a = origem[0]
        _, rva_b, size_b = destino[0]
        if rva_a == rva_b:
            relato.append(u'  %-12s ja aponta para o dialogo %d' % (nome, para_id))
            continue
        planos.append((entry, rva_b, size_b))
        relato.append(u'  %-12s id %d -> id %d   entry@%08x  rva %08x->%08x'
                      % (nome, de_id, para_id, entry, rva_a, rva_b))

    # --- botoes -----------------------------------------------------------
    botoes = []
    try:
        achados = localiza_botoes(pe)
    except Erro as e:
        if u'esperava 1 ocorrencia, achei 0' in unicode(e):
            achados = []
            relato.append(u'  botoes: ja traduzidos')
        else:
            raise
    if achados:
        cave_off, cave_rva, cave_tam = pe.cave()
        preciso = sum((len(n) + 4) & ~3 for _, _, n, _, _ in achados)
        if preciso > cave_tam:
            raise Erro(u'cave de %d bytes e pequeno para %d' % (cave_tam, preciso))
        p = 0
        for off, site, novo, nome, addr in achados:
            dest_off = cave_off + p
            dest_rva = cave_rva + p
            botoes.append((dest_off, novo, site, pe.imagebase + dest_rva))
            relato.append(u'  botao %-10s "%s"  string@rva %08x  push@%08x'
                          % (nome, novo.decode('ascii'), dest_rva, site))
            p += (len(novo) + 4) & ~3

    if not planos and not botoes:
        print u'Nada a fazer: o arquivo ja esta traduzido.'
        return

    print u'Alteracoes:'
    for l in relato:
        print l

    if verificar:
        print u'\n--verificar: nenhum byte foi gravado.'
        return

    backup = '%s.BACKUP-%s' % (path, time.strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(path, backup)
    print u'\nBackup: %s' % os.path.basename(backup)

    for entry, rva, size in planos:
        struct.pack_into('<II', pe.d, entry, rva, size)
    for dest_off, novo, site, addr in botoes:
        pe.d[dest_off:dest_off + len(novo) + 1] = novo + b'\0'
        struct.pack_into('<I', pe.d, site, addr)

    if pe.u32(pe.checksum_off):
        struct.pack_into('<I', pe.d, pe.checksum_off, 0)
        struct.pack_into('<I', pe.d, pe.checksum_off, pe.checksum())

    with open(path, 'wb') as fp:
        fp.write(bytes(pe.d))
    print u'Gravado: %s' % path


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        print __doc__
        sys.exit(1)
    try:
        aplica(args[0], '--verificar' in sys.argv)
    except Erro as e:
        print u'ERRO: %s' % e
        sys.exit(1)
