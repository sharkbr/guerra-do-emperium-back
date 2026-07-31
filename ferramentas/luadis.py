# -*- coding: utf-8 -*-
# Desassemblador minimo de bytecode Lua 5.1 (little-endian, 32 bits)
import struct, sys

OPNAMES = """MOVE LOADK LOADBOOL LOADNIL GETUPVAL GETGLOBAL GETTABLE SETGLOBAL
SETUPVAL SETTABLE NEWTABLE SELF ADD SUB MUL DIV MOD POW UNM NOT LEN CONCAT JMP
EQ LT LE TEST TESTSET CALL TAILCALL RETURN FORLOOP FORPREP TFORLOOP SETLIST
CLOSE CLOSURE VARARG""".split()

# formato de cada opcode: iABC, iABx, iAsBx
FMT = {
 'LOADK':'ABx','GETGLOBAL':'ABx','SETGLOBAL':'ABx','CLOSURE':'ABx',
 'JMP':'AsBx','FORLOOP':'AsBx','FORPREP':'AsBx',
}

class R(object):
    def __init__(s, d, p=0): s.d, s.p = d, p
    def u8(s):
        v = ord(s.d[s.p]); s.p += 1; return v
    def u32(s):
        v = struct.unpack('<I', s.d[s.p:s.p+4])[0]; s.p += 4; return v
    def i32(s):
        v = struct.unpack('<i', s.d[s.p:s.p+4])[0]; s.p += 4; return v
    def f64(s):
        v = struct.unpack('<d', s.d[s.p:s.p+8])[0]; s.p += 8; return v
    def sz(s):
        n = s.u32()
        if n == 0: return ''
        v = s.d[s.p:s.p+n-1]; s.p += n; return v

def read_func(r):
    f = {}
    f['source'] = r.sz()
    f['line'] = r.u32()
    f['lastline'] = r.u32()
    f['nups'] = r.u8()
    f['nparams'] = r.u8()
    f['isvar'] = r.u8()
    f['maxstack'] = r.u8()
    n = r.u32(); f['code'] = [r.u32() for _ in range(n)]
    n = r.u32(); k = []
    for _ in range(n):
        t = r.u8()
        if t == 0: k.append(None)
        elif t == 1: k.append(bool(r.u8()))
        elif t == 3: k.append(r.f64())
        elif t == 4: k.append(r.sz())
        else: raise Exception('const tipo %d' % t)
    f['k'] = k
    n = r.u32(); f['protos'] = [read_func(r) for _ in range(n)]
    n = r.u32(); f['lines'] = [r.u32() for _ in range(n)]
    n = r.u32(); f['locals'] = [(r.sz(), r.u32(), r.u32()) for _ in range(n)]
    n = r.u32(); f['upvals'] = [r.sz() for _ in range(n)]
    return f

def kstr(f, i):
    if i >= 256:
        v = f['k'][i - 256]
        return ('%r' % v) if not isinstance(v, str) else '"%s"' % v
    return 'R%d' % i

def dump(f, depth=0, path='main'):
    ind = '  ' * depth
    print '%s== %s  (linhas %d-%d, params=%d, ups=%d)' % (
        ind, path, f['line'], f['lastline'], f['nparams'], f['nups'])
    if f['upvals']:
        print '%s   upvals: %s' % (ind, ', '.join(f['upvals']))
    for pc, ins in enumerate(f['code']):
        op = ins & 0x3f
        A = (ins >> 6) & 0xff
        C = (ins >> 14) & 0x1ff
        B = (ins >> 23) & 0x1ff
        Bx = (ins >> 14) & 0x3ffff
        sBx = Bx - 131071
        name = OPNAMES[op] if op < len(OPNAMES) else '??%d' % op
        fmt = FMT.get(name, 'ABC')
        if fmt == 'ABx':
            arg = 'A=%d Bx=%d' % (A, Bx)
            if name in ('LOADK', 'GETGLOBAL', 'SETGLOBAL'):
                v = f['k'][Bx]
                arg += '   ; %s' % (('"%s"' % v) if isinstance(v, str) else repr(v))
        elif fmt == 'AsBx':
            arg = 'A=%d sBx=%d  -> pc %d' % (A, sBx, pc + 1 + sBx)
        else:
            arg = 'A=%d B=%d C=%d' % (A, B, C)
            if name in ('GETTABLE','SETTABLE','SELF','ADD','SUB','MUL','DIV','EQ','LT','LE'):
                arg += '   ; B=%s C=%s' % (kstr(f, B), kstr(f, C))
        ln = f['lines'][pc] if pc < len(f['lines']) else -1
        print '%s  [%3d] L%-4d %-10s %s' % (ind, pc, ln, name, arg)
    for i, p in enumerate(f['protos']):
        dump(p, depth + 1, '%s/proto%d' % (path, i))

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    assert d[0:4] == '\x1bLua' and ord(d[4]) == 0x51, 'nao e Lua 5.1'
    r = R(d, 12)
    dump(read_func(r))
