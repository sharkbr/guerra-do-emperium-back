# -*- coding: utf-8 -*-
u"""Base comum da traducao PT-BR: ler o bRO, escrever no nosso cliente.

Nao faz nada sozinho. Quem usa e o `traduz_ptbr.py`; este arquivo guarda as
tres coisas que todas as partes precisam:

  1. **onde estao as fontes** - a instalacao do Ragnarok Brazil desta maquina,
     que e a nossa fonte de referencia por acordo de 2026-08-02 (PENDENCIAS.md).
  2. **um leitor de bytecode Lua 5.1** que devolve as tabelas montadas, e nao
     so as strings soltas. E a peca reaproveitada: os arquivos de texto do bRO
     vem metade em texto puro e metade em bytecode, sem aviso.
  3. **a conversao de codificacao**, que e onde este projeto ja se queimou.

--------------------------------------------------------------- codificacao

O texto do bRO sai em **UTF-8** quando vem do `iteminfo_new.lub` e em
**cp1252** quando vem do GRF (os `.lua` de habilidade, o `msgstringtable.txt`).
O cliente le tudo como ANSI, e a codepage ANSI desta maquina e a cp1252 - entao
o destino e sempre cp1252, e a unica pergunta e de onde veio.

`decodifica()` responde isso sozinho: tenta UTF-8 e cai para cp1252. A ordem
importa e nao e simetrica - todo UTF-8 valido com acento e cp1252 invalido ou
diferente, mas nem todo cp1252 e UTF-8 valido. Tentar cp1252 primeiro aceitaria
o UTF-8 cru e produziria "AÃ§Ã£o" calado.

O acento **fica**, por decisao da fase PT-BR: o patch `AlwaysAscii` esta
aplicado no nosso exe (WARP `LastSession.yml`), e e ele que faz o cliente
desenhar com ANSI_CHARSET em vez do charset coreano. Se o jogo mostrar lixo
mesmo assim, `--sem-acento` reverte a fase inteira sem tocar em codigo.
"""
import os
import re
import struct
import unicodedata

# ------------------------------------------------------------------ caminhos

CLIENTE = r'C:\GuerraDoEmperium\cliente'

BRO = os.path.join(r'C:\Program Files (x86)\Gravity Interactive, Inc',
                   'Ragnarok Brazil')
BRO_GRF = os.path.join(BRO, 'data.grf')

# O nosso GRF, o oficial da Gravity de 2021-11-03. E fonte tambem: quando um
# `.lub` so existe la dentro, e a versao DELE que casa com este cliente - a do
# bRO e mais nova e pode citar constante que este exe nao conhece.
NOSSO_GRF = os.path.join(CLIENTE, 'data.grf')

# Os arquivos de texto do cliente, todos relativos a CLIENTE.
ALVOS = {
    # Os DOIS, e a ordem nao importa mas a lista sim: extraindo as strings do
    # `GuerraDoEmperium.exe` e filtrando por `msgstring`, o que ele pede e
    # `Lua Files\MsgString_KR_S` - o `_S`. O `msgstring_kr.lub` e copia
    # identica que o ROenglishRE tambem entrega, e traduzir so ele nao mudaria
    # nada na tela. Mesma receita do `_sak` vs `_Sakray` que ja custou uma
    # rodada (PENDENCIAS.md): so o exe diz o nome exato.
    'msgstrid':  [os.path.join('data', 'luafiles514', 'lua files',
                               'msgstring_kr_s.lub'),
                  os.path.join('data', 'luafiles514', 'lua files',
                               'msgstring_kr.lub')],
    'msgtable':  os.path.join('data', 'msgstringtable.txt'),
    'quests':    os.path.join('data', 'questid2display.txt'),
    'cartas':    os.path.join('data', 'cardprefixnametable.txt'),
    'mapas':     os.path.join('data', 'mapnametable.txt'),
    'itens':     os.path.join('SystemEN', 'LuaFiles514', 'itemInfo.lua'),
    'skillnome': os.path.join('data', 'luafiles514', 'lua files', 'skillinfoz',
                              'skillinfolist.lub'),
    'skilldesc': os.path.join('data', 'luafiles514', 'lua files', 'skillinfoz',
                              'skilldescript.lub'),
}


class Erro(Exception):
    pass


def caminho(chave):
    return os.path.join(CLIENTE, ALVOS[chave])


def caminhos(chave):
    u"""Todos os arquivos de uma parte - algumas tem mais de um."""
    alvo = ALVOS[chave]
    if isinstance(alvo, list):
        return [os.path.join(CLIENTE, a) for a in alvo]
    return [os.path.join(CLIENTE, alvo)]


# =========================================================== codificacao

# Ligado por --sem-acento na linha de comando do traduz_ptbr.py.
SEM_ACENTO = [False]


def decodifica(bruto):
    u"""bytes vindos do bRO -> unicode. Ver a nota de codificacao no topo."""
    if isinstance(bruto, unicode):
        return bruto
    try:
        return bruto.decode('utf-8')
    except UnicodeDecodeError:
        return bruto.decode('cp1252', 'replace')


def codifica(texto):
    u"""unicode -> os bytes que vao para o arquivo do cliente.

    cp1252 por padrao. Caractere que nao couber (as aspas tipograficas que o
    bRO usa em alguns textos, por exemplo) e reduzido ao equivalente ASCII em
    vez de virar '?', que apareceria no jogo.
    """
    texto = texto.replace(u'\u2019', u"'").replace(u'\u2018', u"'")
    texto = texto.replace(u'\u201c', u'"').replace(u'\u201d', u'"')
    texto = texto.replace(u'\u2013', u'-').replace(u'\u2014', u'-')
    texto = texto.replace(u'\u2026', u'...')
    if SEM_ACENTO[0]:
        return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore')
    try:
        return texto.encode('cp1252')
    except UnicodeEncodeError:
        # Ultimo recurso: so o que nao coube perde o acento.
        saida = []
        for c in texto:
            try:
                saida.append(c.encode('cp1252'))
            except UnicodeEncodeError:
                saida.append(unicodedata.normalize('NFKD', c)
                             .encode('ascii', 'ignore'))
        return ''.join(saida)


def pt(bruto):
    u"""Atalho: bytes do bRO -> bytes prontos para o cliente."""
    return codifica(decodifica(bruto))


# =========================================================== GRF do bRO

_GRF = {}


def grf(caminho=None):
    import grf as _mod
    caminho = caminho or BRO_GRF
    if caminho not in _GRF:
        if not os.path.exists(caminho):
            raise Erro('nao achei o GRF em %s' % caminho)
        _GRF[caminho] = _mod.Grf(caminho)
    return _GRF[caminho]


def do_bro(nome):
    u"""Le um arquivo de dentro do GRF do bRO. `nome` usa barra invertida."""
    try:
        return grf().read(nome)
    except KeyError:
        raise Erro('o GRF do bRO nao tem %s' % nome)


def do_nosso(nome):
    u"""Le um arquivo de dentro do NOSSO GRF, o da Gravity de 2021-11-03."""
    try:
        return grf(NOSSO_GRF).read(nome)
    except KeyError:
        raise Erro('o nosso GRF nao tem %s' % nome)


def troca_constante(dados, velho, novo):
    u"""Troca uma string do pool de constantes de um chunk Lua 5.1.

    A string e gravada como `<u32 tamanho><bytes><\\0>`, e **o formato nao tem
    offset absoluto nenhum** - o `luaU_undump` le o arquivo em sequencia, do
    comeco ao fim. Por isso da para trocar por outra de tamanho diferente sem
    corrigir mais nada: tudo que vem depois so escorrega.

    Devolve (dados, quantas). Nao mexe em ocorrencia que nao seja precedida
    pelo tamanho certo - isso evita acertar o mesmo texto embutido em outro
    lugar por acaso.
    """
    alvo = struct.pack('<I', len(velho) + 1) + velho + '\x00'
    troca = struct.pack('<I', len(novo) + 1) + novo + '\x00'
    quantas = dados.count(alvo)
    return dados.replace(alvo, troca), quantas


# ================================================== bytecode Lua 5.1

class _R(object):
    def __init__(s, d, p=0):
        s.d, s.p = d, p

    def u8(s):
        v = ord(s.d[s.p]); s.p += 1; return v

    def u32(s):
        v = struct.unpack('<I', s.d[s.p:s.p + 4])[0]; s.p += 4; return v

    def f64(s):
        v = struct.unpack('<d', s.d[s.p:s.p + 8])[0]; s.p += 8; return v

    def sz(s):
        n = s.u32()
        if n == 0:
            return ''
        v = s.d[s.p:s.p + n - 1]; s.p += n; return v


def _funcao(r):
    f = {}
    f['source'] = r.sz(); r.u32(); r.u32()
    r.u8(); r.u8(); r.u8(); r.u8()
    n = r.u32(); f['code'] = [r.u32() for _ in range(n)]
    n = r.u32(); k = []
    for _ in range(n):
        t = r.u8()
        if t == 0:
            k.append(None)
        elif t == 1:
            k.append(bool(r.u8()))
        elif t == 3:
            k.append(r.f64())
        elif t == 4:
            k.append(r.sz())
        else:
            raise Erro('constante de tipo %d: nao e Lua 5.1 32 bits' % t)
    f['k'] = k
    n = r.u32(); f['protos'] = [_funcao(r) for _ in range(n)]
    n = r.u32(); [r.u32() for _ in range(n)]                     # linhas
    n = r.u32(); [(r.sz(), r.u32(), r.u32()) for _ in range(n)]  # locais
    n = r.u32(); [r.sz() for _ in range(n)]                      # upvalues
    return f


class Sym(object):
    u"""Valor que so existiria em tempo de execucao, guardado pelo nome.

    E o que torna legivel um `[SKID.NV_BASIC] = {...}`: no bytecode a chave nao
    e constante nenhuma, e `GETGLOBAL SKID` seguido de `GETTABLE "NV_BASIC"`.
    Sem isto a tabela inteira sai com chave `None`.
    """
    __slots__ = ('nome',)

    def __init__(s, nome):
        s.nome = nome

    def __repr__(s):
        return s.nome

    def __hash__(s):
        return hash(s.nome)

    def __eq__(s, o):
        return isinstance(o, Sym) and o.nome == s.nome

    def __ne__(s, o):
        return not s.__eq__(o)


def _interpreta(f, globais):
    u"""Percorre uma funcao e devolve as tabelas que ela monta.

    Nao e um interpretador de verdade - nao segue salto, nao executa chamada.
    Nao precisa: estes arquivos sao literais de tabela em sequencia, e o
    compilador emite exatamente NEWTABLE, LOADK, SETTABLE e SETLIST.

    O que ele NAO pode fazer e copiar tabela ao guardar: as tabelas sao
    preenchidas por SETLIST **depois** de ja terem sido atribuidas ao pai, e
    guardar copia perderia todo o conteudo. Por isso o dicionario vive por
    referencia. Foi a pegadinha que o leitor antigo do completa_iteminfo.py
    documenta.
    """
    reg = {}
    k = f['k']

    def rk(i):
        return k[i - 256] if i >= 256 else reg.get(i)

    i = 0
    codigo = f['code']
    while i < len(codigo):
        ins = codigo[i]
        i += 1
        op = ins & 0x3f
        A = (ins >> 6) & 0xff
        C = (ins >> 14) & 0x1ff
        B = (ins >> 23) & 0x1ff
        Bx = (ins >> 14) & 0x3ffff
        if op == 0:                                   # MOVE
            reg[A] = reg.get(B)
        elif op == 1:                                 # LOADK
            reg[A] = k[Bx]
        elif op == 2:                                 # LOADBOOL
            reg[A] = bool(B)
        elif op == 3:                                 # LOADNIL
            for x in range(A, B + 1):
                reg[x] = None
        elif op == 5:                                 # GETGLOBAL
            nome = k[Bx]
            reg[A] = globais.get(nome, Sym(nome))
        elif op == 6:                                 # GETTABLE
            base = reg.get(B)
            chave = rk(C)
            if isinstance(base, dict):
                reg[A] = base.get(chave)
            elif isinstance(base, Sym) and isinstance(chave, str):
                reg[A] = Sym('%s.%s' % (base.nome, chave))
            else:
                reg[A] = None
        elif op == 7:                                 # SETGLOBAL
            globais[k[Bx]] = reg.get(A)
        elif op == 9:                                 # SETTABLE
            alvo = reg.get(A)
            if isinstance(alvo, dict):
                alvo[rk(B)] = rk(C)
        elif op == 10:                                # NEWTABLE
            reg[A] = {}
        elif op == 34:                                # SETLIST
            alvo = reg.get(A)
            if not isinstance(alvo, dict):
                continue
            bloco = C
            if bloco == 0:                # o C real esta na proxima palavra
                bloco = codigo[i]
                i += 1
            base = (bloco - 1) * 50
            if B == 0:                    # ate o topo da pilha: usa o que ha
                n = max([x - A for x in reg if x > A] or [0])
            else:
                n = B
            for j in range(1, n + 1):
                if (A + j) in reg:
                    alvo[float(base + j)] = reg[A + j]
        # CLOSURE(36) e os saltos nao importam aqui; os protos sao percorridos
        # em separado, logo abaixo.

    for p in f['protos']:
        _interpreta(p, globais)
    return globais


def tabelas(dados):
    u"""bytecode Lua 5.1 -> {nome do global: valor}."""
    if dados[:5] != '\x1bLuaQ':
        raise Erro('nao e bytecode Lua 5.1 (header %r)' % dados[:5])
    return _interpreta(_funcao(_R(dados, 12)), {})


def tabelas_de(caminho_arquivo):
    fh = open(caminho_arquivo, 'rb')
    d = fh.read()
    fh.close()
    return tabelas(d)


def lista(tabela):
    u"""A parte sequencial de uma tabela lida do bytecode, na ordem."""
    if not isinstance(tabela, dict):
        return []
    chaves = sorted(c for c in tabela if isinstance(c, float))
    return [tabela[c] for c in chaves]


# ================================================== Lua em texto puro

# A chave de uma entrada: `[SKID.XXX]`, `[123]` ou `["prontera.rsw"]`. As tres
# formas aparecem, e o mapInfo usa so a terceira.
CHAVE_ENTRADA = r'\[\s*("(?:[^"\\]|\\.)*"|[A-Za-z_][\w.]*|\d+)\s*\]\s*=\s*\{'
_RE_CHAVE = re.compile(CHAVE_ENTRADA)
_RE_TOKEN = re.compile(r'\[\[|[{}"]')


def blocos_lua(texto):
    u"""Quebra `TABELA = { [chave] = {...}, ... }` em (chave, bloco).

    Trabalha por contagem de chaves `{}` fora de string, que e o suficiente
    para estes arquivos e nao exige um parser de Lua. Devolve os blocos na
    ordem do arquivo, com o texto exato - quem chama reescreve so o que quer e
    o resto atravessa byte a byte.
    """
    saida = []
    n = len(texto)
    i = 0
    while True:
        m = _RE_CHAVE.search(texto, i)
        if not m:
            break
        chave = m.group(1).strip('"')
        ini = m.start()
        p = m.end()              # logo depois da chave de abertura
        nivel = 1
        while nivel and p < n:
            # Salta direto ao proximo caractere que importa. Percorrer byte a
            # byte custaria minutos no itemInfo.lua, que tem 22 MB.
            t = _RE_TOKEN.search(texto, p)
            if not t:
                p = n
                break
            p = t.end()
            achado = t.group(0)
            if achado == '{':
                nivel += 1
            elif achado == '}':
                nivel -= 1
            elif achado == '[[':
                fim = texto.find(']]', p)
                p = n if fim < 0 else fim + 2
            else:                                    # abriu aspas
                while p < n:
                    c = texto[p]
                    if c == '\\':
                        p += 2
                    elif c == '"':
                        p += 1
                        break
                    else:
                        p += 1
        saida.append((chave, ini, p))
        i = p
    return saida
