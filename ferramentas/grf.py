# -*- coding: utf-8 -*-
# Extrator minimo de GRF 0x200 (sem DES) para Python 2.7
import struct, zlib, sys, os

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
        if flags & 6:
            raise Exception('arquivo com DES: %s' % real)
        self.f.seek(46 + offset)
        return zlib.decompress(self.f.read(csize))

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
