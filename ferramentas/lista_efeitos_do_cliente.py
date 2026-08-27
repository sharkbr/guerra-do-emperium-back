# -*- coding: utf-8 -*-
"""De-para NUMERO DE EFEITO -> arquivo .str, lido do exe do cliente.

    python lista_efeitos_do_cliente.py                 # resumo + grava a lista
    python lista_efeitos_do_cliente.py --id 1642       # o que e o efeito 1642
    python lista_efeitos_do_cliente.py --textura castaura   # quem desenha isso
    python lista_efeitos_do_cliente.py --conferir      # a prova de calibragem

POR QUE ISTO EXISTE
-------------------
O pedido tipico chega pelo nome de um .bmp - "poe a textura tal embaixo do
NPC" - e a pergunta que ninguem sabia responder era: QUE NUMERO DE EFEITO
desenha aquela textura? Sem isso sobra o caminho caro, que e mexer no
`effecttool` do cliente (ver `planta_brilho.py`, que nao funcionou em quatro
idas ao jogo).

Na maioria das vezes nao e preciso: a textura pertence a um efeito que o
cliente ja numera, e ai o pedido inteiro vira UMA LINHA DE SCRIPT no servidor,
sem patch de cliente e sem override de pasta nenhuma.

O TETO DO rAthena NAO E O TETO DO CLIENTE
-----------------------------------------
O `specialeffect` para no `EF_MAX` do emulador, 1243. Este cliente
(kRO 2021-11-03) conhece efeitos ate 2372, e 941 deles - com .str proprio no
GRF - estao ACIMA daquele teto. Para alcanca-los ha o `efeitoespecial`, nosso,
em `src/custom/script.inc`.

COMO A NUMERACAO E LIDA
-----------------------
O cliente despacha o efeito por um switch de tabela DIRETA. Em
`GuerraDoEmperium.exe`, no offset de arquivo 0x006b6ce4:

    lea eax, [ebx-13]                  ; ebx = numero do efeito
    cmp eax, 0x937                     ; 2359
    ja  <default: nao desenha nada>
    jmp dword [eax*4 + 0x00ABFEE0]     ; tabela de 2360 entradas

Ou seja `numero = 13 + indice`, faixa 13..2372. Cada `case` empilha o caminho
de um .str; quando ha dois, sao as variantes `mineffect\\` (efeitos reduzidos)
e normal, escolhidas em tempo de execucao por `cmp [0x011d189c], 1`.

Nada disso e suposto - o `--conferir` refaz a prova (ver abaixo).

A PROVA DE CALIBRAGEM, E POR QUE ELA E NECESSARIA
-------------------------------------------------
Ler `lea eax,[ebx-13]` e concluir "deslocamento 13" seria aceitar uma
instrucao isolada. A prova de verdade e estatistica e cruza com fonte
independente: os efeitos resolvidos sao comparados, pelo NOME do .str, com o
enum `e_special_effects` do proprio rAthena.

    deslocamento 13 -> 25 acertos, de EF_STORMGUST (89) a EF_FULLMOON_KICK (1230)
    qualquer outro  -> ZERO

Pico unico, e os acertos vao de um extremo ao outro da faixa que o rAthena
nomeia - ou seja nao ha deriva nos ids altos. E o mesmo tipo de medicao que
decidiu o eixo Z do `.rsw` (76,1% contra 41,1%).

A ARMADILHA
-----------
Numero fora da faixa cai no `default` do switch: o cliente NAO DESENHA NADA e
NAO AVISA. Nao ha erro de Lua, caixa, nem linha de log. Entao errar o numero e
indistinguivel de "o efeito nao existe" - conferir aqui antes de usar.

E ha uma segunda, mais fina: a variante `mineffect\\` costuma usar OUTRAS
texturas que a normal. Uma textura pode existir so num dos dois lados, e ai
ela so aparece com a opcao de efeitos reduzidos ligada. O `--textura` diz de
qual lado a textura esta.
"""
import codecs
import os
import re
import struct
import sys

sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(
    sys.stdout, 'replace')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EXE = ur'C:\GuerraDoEmperium\cliente\GuerraDoEmperium.exe'
GRF = ur'C:\GuerraDoEmperium\cliente\data.grf'

# Medidos no exe (ver o cabecalho). Cliente novo = remedir.
TABELA_VA = 0x00ABFEE0     # base da tabela de saltos
DESLOCAMENTO = 13          # numero = DESLOCAMENTO + indice
N_ENTRADAS = 2360
BASE_IMAGEM = 0x400000


class Exe(object):
    """Le o exe do cliente e resolve numero de efeito -> caminhos .str."""

    def __init__(self, caminho):
        self.d = open(caminho, 'rb').read()
        pe = struct.unpack_from('<I', self.d, 0x3c)[0]
        nsec = struct.unpack_from('<H', self.d, pe + 6)[0]
        optsz = struct.unpack_from('<H', self.d, pe + 20)[0]
        self.secs = []
        for i in range(nsec):
            o = pe + 24 + optsz + i * 40
            vsz, va, rsz, praw = struct.unpack_from('<IIII', self.d, o + 8)
            self.secs.append((va, vsz, praw, rsz))
        self._mapeia_strings()

    def off2va(self, off):
        for va0, vsz, praw, rsz in self.secs:
            if praw <= off < praw + rsz:
                return BASE_IMAGEM + va0 + (off - praw)
        return None

    def va2off(self, va):
        r = va - BASE_IMAGEM
        for va0, vsz, praw, rsz in self.secs:
            if va0 <= r < va0 + rsz:
                return praw + (r - va0)
        return None

    def _mapeia_strings(self):
        pat = re.compile(r'[\x20-\x7e]{3,120}\.str\x00')
        self.va2str = {}
        for m in pat.finditer(self.d):
            va = self.off2va(m.start())
            if va:
                self.va2str[va] = m.group()[:-1]

    def _strs_do_case(self, oc, limite=200):
        """Os `push <ponteiro .str>` do bloco.

        Um `case` tem UM caminho, ou DOIS quando o efeito muda com a opcao de
        efeitos reduzidos. O de dois tem esta forma, e o segundo push mora
        depois de um `jmp` - parar no primeiro `jmp` perderia a variante
        normal, que e justamente a que a maioria dos jogadores ve:

            cmp  [0x011d189c], 1     ; a opcao de efeitos reduzidos
            jne  +0x16               ; 75 16
            push <mineffect\\...str>
            call ...
            jmp  <fim do case>       ; e9
            push <...str normal>
            call ...

        Por isso o numero de caminhos e decidido ANTES de varrer, pelo `75 16`
        do par - e nao por onde o `jmp` aparece.
        """
        esperados = 2 if '\x75\x16' in self.d[oc:oc + 40] else 1
        out = []
        i = oc
        while i < oc + limite - 4 and len(out) < esperados:
            if self.d[i] == '\x68':
                v = struct.unpack_from('<I', self.d, i + 1)[0]
                if v in self.va2str:
                    out.append(self.va2str[v])
                    i += 5
                    continue
            i += 1
        return out

    def efeito(self, numero):
        """Lista de caminhos .str do efeito, ou [] se ele nao usa .str."""
        k = numero - DESLOCAMENTO
        if not (0 <= k < N_ENTRADAS):
            return None
        tab = self.va2off(TABELA_VA)
        va = struct.unpack_from('<I', self.d, tab + k * 4)[0]
        oc = self.va2off(va)
        if oc is None:
            return []
        return self._strs_do_case(oc)

    def todos(self):
        for n in range(DESLOCAMENTO, DESLOCAMENTO + N_ENTRADAS):
            s = self.efeito(n)
            if s:
                yield n, s


def le_str_do_grf(caminho_str):
    """Texturas de um .str do GRF. Devolve None se nao der para ler."""
    import grf as _grf
    try:
        g = _grf.Grf(GRF)
        d = g.read('data\\texture\\effect\\' + caminho_str)
    except Exception:
        return None
    if d[0:4] != 'STRM':
        return None
    _ver, fps, maxkey, nlay = struct.unpack_from('<IIII', d, 4)
    p = 36
    texs = []
    try:
        for _c in range(nlay):
            ntex = struct.unpack_from('<I', d, p)[0]
            p += 4
            for _t in range(ntex):
                texs.append(d[p:p + 128].split('\x00')[0])
                p += 128
            nkey = struct.unpack_from('<I', d, p)[0]
            p += 4
            p += nkey * 124      # medido: o unico tamanho que fecha os arquivos
    except Exception:
        return None
    if p != len(d):
        # leitor que nao fecha nao vale nada (a regra do mede_rsm.py)
        return None
    return {'fps': fps, 'quadros': maxkey, 'texturas': texs}


def enum_do_rathena():
    """{numero: EF_NOME} do enum e_special_effects do nosso vendor."""
    cam = os.path.join(RAIZ, 'rathena', 'src', 'map', 'script.hpp')
    txt = open(cam).read()
    m = re.search(r'enum e_special_effects \{(.*?)\n\};', txt, re.S)
    i, nomes = -1, {}
    for linha in m.group(1).split('\n'):
        mm = re.match(r'\s*(EF_[A-Z0-9_]+)\s*(?:=\s*(-?\d+))?\s*,?', linha)
        if not mm:
            continue
        if mm.group(2) is not None:
            i = int(mm.group(2))
        else:
            i += 1
        nomes[i] = mm.group(1)
    return nomes


def _base(caminho):
    c = caminho.replace('/', os.sep).split('\\')[-1]
    return c[:-4].lower() if c.lower().endswith('.str') else c.lower()


def _norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def conferir(exe):
    """Refaz a prova de calibragem do deslocamento."""
    nomes = enum_do_rathena()
    res = dict(exe.todos())
    print u'efeitos com .str resolvidos: %d' % len(res)
    print u'enum do rAthena: %d constantes' % len(nomes)
    print
    print u'deslocamento   acertos'
    melhor = (None, -1)
    for desl in range(0, 27):
        ok = 0
        for n, ss in res.items():
            eid = n - DESLOCAMENTO + desl
            if eid not in nomes:
                continue
            a, b = _norm(nomes[eid][3:]), _norm(_base(ss[0]))
            if a and b and (a == b or a.startswith(b) or b.startswith(a)):
                ok += 1
        marca = u''
        if desl == DESLOCAMENTO:
            marca = u'   <- o que esta em uso'
        print u'  %3d          %4d%s' % (desl, ok, marca)
        if ok > melhor[1]:
            melhor = (desl, ok)
    print
    if melhor[0] == DESLOCAMENTO and melhor[1] > 0:
        print u'OK: pico unico no deslocamento %d (%d acertos).' % melhor
        return 0
    print u'FALHOU: o melhor deslocamento e %d (%d acertos), nao %d.' % (
        melhor[0], melhor[1], DESLOCAMENTO)
    print u'O cliente mudou. Remedir - ver o cabecalho deste arquivo.'
    return 1


def main():
    args = sys.argv[1:]
    exe = Exe(EXE)

    if '--conferir' in args:
        return conferir(exe)

    if '--id' in args:
        n = int(args[args.index('--id') + 1])
        ss = exe.efeito(n)
        if ss is None:
            print u'efeito %d esta FORA da faixa %d..%d - o cliente nao ' \
                  u'desenha nada, e nao avisa.' % (
                      n, DESLOCAMENTO, DESLOCAMENTO + N_ENTRADAS - 1)
            return 1
        if not ss:
            print u'efeito %d existe na tabela, mas nao usa .str ' \
                  u'(e desenhado de outro jeito).' % n
            return 0
        nomes = enum_do_rathena()
        print u'efeito %d%s' % (
            n, u'  (%s no rAthena)' % nomes[n] if n in nomes else
            u'  (sem nome EF_ no rAthena - use `efeitoespecial`)')
        for s in ss:
            variante = u'reduzido' if s.lower().startswith('mineffect') \
                else u'normal  '
            print u'  [%s] %s' % (variante, s)
            info = le_str_do_grf(s)
            if info:
                print u'             %d quadros a %d fps = %.2f s' % (
                    info['quadros'], info['fps'],
                    float(info['quadros']) / info['fps'] if info['fps'] else 0)
                vistas = []
                for t in info['texturas']:
                    if t and t not in vistas:
                        vistas.append(t)
                print u'             texturas: %s' % u', '.join(
                    v.decode('cp1252', 'replace') for v in vistas)
        return 0

    if '--textura' in args:
        alvo = args[args.index('--textura') + 1].lower()
        print u'procurando "%s" nos .str de cada efeito...' % alvo
        achou = 0
        for n, ss in exe.todos():
            for s in ss:
                info = le_str_do_grf(s)
                if not info:
                    continue
                bate = [t for t in info['texturas'] if alvo in t.lower()]
                if bate:
                    achou += 1
                    variante = u'reduzido' if s.lower().startswith('mineffect') \
                        else u'normal'
                    print u'  efeito %4d  [%s]  %s' % (
                        n, variante,
                        u', '.join(b.decode('cp1252', 'replace')
                                   for b in bate[:4]))
        if not achou:
            print u'  nenhum efeito usa essa textura.'
        return 0

    # resumo
    nomes = enum_do_rathena()
    res = list(exe.todos())
    acima = [n for n, _ in res if n >= max(nomes)]
    print u'faixa que o cliente aceita: %d..%d' % (
        DESLOCAMENTO, DESLOCAMENTO + N_ENTRADAS - 1)
    print u'efeitos com arte .str: %d' % len(res)
    print u'deles ACIMA do EF_MAX do rAthena (%d): %d' % (max(nomes), len(acima))
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'efeitos_do_cliente.txt')
    fh = open(saida, 'w')
    for n, ss in res:
        fh.write('%d\t%s\t%s\n' % (
            n, nomes.get(n, '-'), ' | '.join(ss)))
    fh.close()
    print u'lista gravada em %s' % saida
    return 0


if __name__ == '__main__':
    sys.exit(main())
