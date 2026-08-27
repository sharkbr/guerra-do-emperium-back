# -*- coding: utf-8 -*-
"""Tira placas mortas do cliente, regerando o `signboardlist.lub`.

O QUE E UMA PLACA
=================

O `data\\luafiles514\\lua files\\signboardlist.lub` e uma tabela de 514 entradas
que o CLIENTE desenha sozinho, por mapa e celula, sem o servidor participar: um
icone em moldura laranja mais uma placa marrom com um texto. Nao ha NPC por
tras - a placa fica boiando sobre a celula, e clicar nela nao faz nada.

Cada entrada tem 6 ou 8 campos, e os nomes saem do `signboardlist_f.lub`:

    { MAPNAME, CELLX, CELLY, HEIGHT, ICONID, FILEPATH [, CONTENTS, CHARCOLOR] }

O `ICONID` e uma das quatro globais que o proprio arquivo define no topo
(`IT_NONE`, `IT_BMP`, `IT_SPRITE`, `IT_SIGNBOARD`).

POR QUE ALGUMAS PRECISAM SAIR
=============================

Boa parte das placas anuncia coisa do kRO que aqui nunca existiu. As tres que
esta ferramenta tira sao da "Ragnarok Booster Promotion" de 2021, uma campanha
paga de pre-venda: o `itemInfo` ainda traz a Moeda Booster com um `<NAVI>` para
`prontera,166,300`, que era onde ficava o NPC de troca. Aqui so sobrou a placa,
em coreano, sobre chao vazio.

POR QUE REGERAR A TABELA, E NAO USAR O `SignBoardIgnore`
=======================================================

O `signboardlist_f.lub` que o ROenglishRE poe em `cliente\\data\\...` tem um
`SignBoardIgnore` feito exatamente para isto - tres linhas em
`SystemEN\\Sign_Data.lub` e pronto. Nao e o caminho escolhido porque ele depende
de uma corrente que nao esta provada neste cliente: o `_f` do override precisa
ser lido no lugar do que esta no GRF, e o `require('SystemEN/LuaFiles514/rotp_f')`
do topo dele precisa achar um arquivo que existe como `.lua` e nao como `.lub`.
Se qualquer um dos dois falhar, o cliente cai no `_f` do GRF - que nao conhece
`SignBoardIgnore` - e a placa continua na tela, calada.

Tirar a entrada da propria tabela nao depende de nada disso: seja qual for o
`_f` que rodar, ele indexa `SignBoardList[idx]`, e o que nao esta la nao e
desenhado.

O ARQUIVO GRAVADO E TEXTO LUA, NAO BYTECODE
===========================================

O do GRF e bytecode (`\\x1bLuaQ`), mas o cliente aceita os dois, e texto e o
formato que este projeto ja comprovou - o `OngoingQuestInfoList.lub`, o
`CheckAttendance.lub` e os `.lub` gerados pelo `traduz_ptbr.py` sao todos texto
puro. Ver `ferramentas/LEIAME.md`, secao do `planta_brilho.py`.

A BASE VEM SEMPRE DO GRF
========================

Nunca do override que esta ferramenta grava. Reler o proprio arquivo gerado
faria a receita apontar para si mesma, e uma rodada ruim viraria a fonte da
seguinte - a armadilha do `arte_de` do `instala_item.py` (`CLAUDE.md` §5).

A CONFERENCIA
=============

Conferir o texto por regex provaria so que a string sumiu, nao que o Lua
entende o arquivo. Entao o `--conferir` compila o que foi gravado para um
bytecode temporario e o le com o MESMO parser que leu o do GRF, e compara
entrada por entrada com a base menos as tres. Mais um teste de que o parser nao
esta jogando dado fora em silencio: o conjunto de instrucoes do arquivo tem de
ser exatamente o esperado, e qualquer opcode a mais aborta.

E CLIENTE: VAI POR PATCH
========================

`C:\\GuerraDoEmperium\\cliente\\` esta fora do git e nao anda por deploy. Ver
`CLAUDE.md` §4.18 e `RECEITAS.md` §11. O cliente so rele a tabela ao entrar no
mapa - sair e voltar a Prontera.
"""

import os
import struct
import subprocess
import sys
import time

GRF = u'C:\\GuerraDoEmperium\\cliente\\data.grf'
DENTRO_DO_GRF = 'data\\luafiles514\\lua files\\signboardlist.lub'
SAIDA = u'C:\\GuerraDoEmperium\\cliente\\data\\luafiles514\\lua files\\signboardlist.lub'
LUAC = u'C:\\Users\\User\\Downloads\\ROenglishRE\\Tools\\luac.exe'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# As placas a arrancar, por mapa/celula MAIS o texto exato. Duas chaves de
# proposito: coordenada sozinha nao identifica (a tabela tem entrada repetida
# de coordenada em mapa diferente), e texto sozinho se repete entre cidades.
# O texto esta em cp949, que e como o arquivo do GRF o guarda.
MORTAS = [
    ('prontera', 166, 300,
     '  \xba\xce\xbd\xba\xc5\xcd \xc7\xc1\xb7\xce\xb8\xf0\xbc\xc7',
     'Booster Promotion - o NPC de troca da campanha de 2021, que aqui nunca existiu'),
    ('sp_cor', 98, 136,
     ' \xba\xce\xbd\xba\xc5\xcd\xc0\xcf\xb7\xe7\xbd\xc3\xbf\xc2\xc0\xce\xc3\xa6\xc6\xae',
     'Booster Illusion Enchantment - encantamento pago da mesma campanha'),
    ('malangdo', 152, 136,
     '  \xba\xce\xbd\xba\xc5\xcd \xc0\xc7\xbb\xf3 \xc0\xce\xc3\xa6\xc6\xae',
     'Booster Costume Enchantment - encantamento pago da mesma campanha'),
]

# Opcodes que este arquivo pode conter. Qualquer outro quer dizer que a tabela
# ganhou construcao que o parser nao entende, e ai regerar joga dado fora.
OP_MOVE, OP_LOADK, OP_GETGLOBAL, OP_SETGLOBAL = 0, 1, 5, 7
OP_NEWTABLE, OP_SETLIST, OP_RETURN = 10, 34, 30
PERMITIDOS = set([OP_LOADK, OP_GETGLOBAL, OP_SETGLOBAL,
                  OP_NEWTABLE, OP_SETLIST, OP_RETURN])
NOME_OP = {OP_MOVE: 'MOVE', OP_LOADK: 'LOADK', OP_GETGLOBAL: 'GETGLOBAL',
           OP_SETGLOBAL: 'SETGLOBAL', OP_NEWTABLE: 'NEWTABLE',
           OP_SETLIST: 'SETLIST', OP_RETURN: 'RETURN'}


class Global(object):
    """Um valor que no fonte e um identificador, nao um literal."""

    def __init__(self, nome):
        self.nome = nome

    def __eq__(self, outro):
        return isinstance(outro, Global) and outro.nome == self.nome

    def __ne__(self, outro):
        return not self.__eq__(outro)

    def __repr__(self):
        return self.nome


class Bytecode(object):
    """Leitor minimo de Lua 5.1 - so o que este arquivo usa."""

    def __init__(self, dados):
        if dados[:4] != '\x1bLua' or ord(dados[4]) != 0x51:
            raise Exception('nao e bytecode Lua 5.1')
        self.d = dados
        self.p = 12
        self.opcodes = set()
        self.globais = []      # [(nome, valor)] na ordem em que sao definidas
        self.entradas = []     # [[campo, ...]]
        self._funcao()

    def _u8(self):
        v = ord(self.d[self.p])
        self.p += 1
        return v

    def _u32(self):
        v = struct.unpack('<I', self.d[self.p:self.p + 4])[0]
        self.p += 4
        return v

    def _dbl(self):
        v = struct.unpack('<d', self.d[self.p:self.p + 8])[0]
        self.p += 8
        return v

    def _str(self):
        n = self._u32()
        if n == 0:
            return ''
        s = self.d[self.p:self.p + n - 1]
        self.p += n
        return s

    def _funcao(self):
        self._str()                       # source
        self._u32(), self._u32()          # linedefined, lastlinedefined
        self._u8(), self._u8(), self._u8(), self._u8()
        code = [self._u32() for _ in range(self._u32())]
        ks = []
        for _ in range(self._u32()):
            t = self._u8()
            if t == 0:
                ks.append(None)
            elif t == 1:
                ks.append(bool(self._u8()))
            elif t == 3:
                ks.append(self._dbl())
            elif t == 4:
                ks.append(self._str())
            else:
                raise Exception('constante de tipo %d' % t)
        if self._u32() != 0:
            raise Exception('o arquivo tem funcao aninhada; nao deveria')
        # `self.p += 4 * self._u32()` seria errado: o `+=` guarda o `self.p`
        # de antes, e o `_u32()` avanca o ponteiro no meio da conta.
        n_linhas = self._u32()
        self.p = self.p + 4 * n_linhas                # linhas
        for _ in range(self._u32()):                  # locais
            self._str(), self._u32(), self._u32()
        for _ in range(self._u32()):                  # upvalues
            self._str()
        self._interpreta(code, ks)

    def _interpreta(self, code, ks):
        regs = {}
        aberta = None
        for ins in code:
            op = ins & 0x3f
            A = (ins >> 6) & 0xff
            B = (ins >> 23) & 0x1ff
            Bx = (ins >> 14) & 0x3ffff
            self.opcodes.add(op)
            if op not in PERMITIDOS:
                raise Exception('opcode inesperado %d (%s)'
                                % (op, NOME_OP.get(op, '?')))
            if op == OP_LOADK:
                regs[A] = ks[Bx]
                if aberta is not None:
                    aberta.append(ks[Bx])
            elif op == OP_GETGLOBAL:
                regs[A] = Global(ks[Bx])
                if aberta is not None:
                    aberta.append(regs[A])
            elif op == OP_SETGLOBAL:
                if aberta is not None:
                    raise Exception('SETGLOBAL dentro de entrada')
                self.globais.append((ks[Bx], regs[A]))
            elif op == OP_NEWTABLE:
                if A == 0:
                    continue              # a tabela de fora
                if aberta is not None:
                    raise Exception('entrada dentro de entrada')
                aberta = []
            elif op == OP_SETLIST:
                if A == 0:
                    continue              # despejo de um bloco na tabela de fora
                if aberta is None:
                    raise Exception('SETLIST sem NEWTABLE')
                if B != len(aberta):
                    raise Exception('SETLIST diz %d campos, li %d' % (B, len(aberta)))
                self.entradas.append(aberta)
                aberta = None
        if aberta is not None:
            raise Exception('entrada sem SETLIST no fim do arquivo')


def le_base():
    """Le a tabela do GRF - a base e sempre ele, nunca o override."""
    from grf import Grf
    g = Grf(GRF)
    b = Bytecode(g.read(DENTRO_DO_GRF))
    # A tabela de fora vira uma global so; as outras sao os IT_*.
    nomes = [n for n, _ in b.globais]
    if 'SignBoardList' not in nomes:
        raise Exception('o arquivo do GRF nao define SignBoardList')
    for campos in b.entradas:
        if len(campos) not in (6, 8):
            raise Exception('entrada com %d campos: %r' % (len(campos), campos))
    return b


def separa(entradas):
    """Devolve (fica, arrancadas) e grita se alguma alvo nao casou."""
    alvo = {}
    for mapa, x, y, texto, _ in MORTAS:
        alvo[(mapa, x, y)] = texto
    fica, tirou = [], []
    for campos in entradas:
        chave = (campos[0], int(campos[1]), int(campos[2]))
        texto = alvo.get(chave)
        if texto is not None and len(campos) >= 7 and campos[6] == texto:
            tirou.append(campos)
        else:
            fica.append(campos)
    if len(tirou) != len(MORTAS):
        achadas = set((c[0], int(c[1]), int(c[2])) for c in tirou)
        faltam = [m[:3] for m in MORTAS if m[:3] not in achadas]
        raise Exception('casaram %d de %d placas; nao achei: %r'
                        % (len(tirou), len(MORTAS), faltam))
    return fica, tirou


def literal(v):
    if isinstance(v, Global):
        return v.nome
    if isinstance(v, float):
        return str(int(v)) if v == int(v) else repr(v)
    if isinstance(v, str):
        s = v.replace('\\', '\\\\').replace('"', '\\"')
        s = s.replace('\r', '\\r').replace('\n', '\\n')
        return '"%s"' % s
    raise Exception('campo de tipo inesperado: %r' % (v,))


def monta(base, fica, tirou):
    """Monta o fonte Lua. Tudo em bytes: o arquivo e cp949, nunca UTF-8."""
    L = []
    L.append('-- Guerra do Emperium - GERADO por ferramentas/remove_placas_mortas.py')
    L.append('-- Nao editar a mao: a proxima rodada reescreve o arquivo inteiro.')
    L.append('-- Base: %s, dentro do data.grf.' % DENTRO_DO_GRF)
    L.append('-- Gerado em %s.' % time.strftime('%Y-%m-%d %H:%M'))
    L.append('--')
    L.append('-- Placas arrancadas em relacao ao original (%d de %d):'
             % (len(tirou), len(base.entradas)))
    for mapa, x, y, _, porque in MORTAS:
        L.append('--   %s %d,%d - %s' % (mapa, x, y, porque))
    L.append('')
    for nome, valor in base.globais:
        if nome == 'SignBoardList':
            continue
        L.append('%s = %s' % (nome, literal(valor)))
    L.append('')
    L.append('SignBoardList = {')
    for campos in fica:
        L.append('\t{ %s },' % ', '.join(literal(c) for c in campos))
    L.append('}')
    L.append('')
    return '\r\n'.join(L)


def compila(fonte, destino=None):
    """Roda o luac. Sem destino e so conferencia de sintaxe (-p)."""
    if not os.path.exists(LUAC):
        raise Exception('luac.exe nao encontrado em %s' % LUAC)
    tmp = os.path.join(os.environ.get('TEMP', '.'), 'placas_%d.lua' % os.getpid())
    fh = open(tmp, 'wb')
    fh.write(fonte)
    fh.close()
    try:
        if destino is None:
            cod = subprocess.call([LUAC, '-p', tmp])
        else:
            cod = subprocess.call([LUAC, '-o', destino, tmp])
        if cod != 0:
            raise Exception('luac recusou o fonte gerado (codigo %d)' % cod)
    finally:
        os.remove(tmp)


def confere(fonte, base, fica):
    """Compila o que foi gravado e le o bytecode com o mesmo parser da base."""
    tmp = os.path.join(os.environ.get('TEMP', '.'), 'placas_%d.lub' % os.getpid())
    compila(fonte, tmp)
    try:
        lido = Bytecode(open(tmp, 'rb').read())
    finally:
        os.remove(tmp)

    if len(lido.entradas) != len(fica):
        raise Exception('reli %d entradas, esperava %d'
                        % (len(lido.entradas), len(fica)))
    for i, (a, b) in enumerate(zip(fica, lido.entradas)):
        if a != b:
            raise Exception('entrada %d nao bate:\n  esperava %r\n  reli     %r'
                            % (i, a, b))
    if [n for n, _ in lido.globais] != [n for n, _ in base.globais]:
        raise Exception('as globais nao batem: %r' % ([n for n, _ in lido.globais],))
    for mapa, x, y, texto, _ in MORTAS:
        for campos in lido.entradas:
            if len(campos) >= 7 and campos[6] == texto:
                raise Exception('a placa %s %d,%d continua na tabela' % (mapa, x, y))
    print '  luac -o + releitura: %d entradas conferidas uma a uma, as %d mortas ausentes' \
        % (len(lido.entradas), len(MORTAS))


def sem_carimbo(dados):
    return '\r\n'.join(l for l in dados.split('\r\n')
                       if not l.startswith('-- Gerado em '))


def salva_backup(caminho):
    if not os.path.exists(caminho):
        return None
    novo = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M%S'))
    fh = open(novo, 'wb')
    fh.write(open(caminho, 'rb').read())
    fh.close()
    return novo


def main():
    so_confere = '--conferir' in sys.argv

    print 'Base: %s' % DENTRO_DO_GRF
    base = le_base()
    print '  %d entradas, %d globais, opcodes %s' % (
        len(base.entradas), len(base.globais),
        ' '.join(sorted(NOME_OP.get(o, '?%d' % o) for o in base.opcodes)))

    fica, tirou = separa(base.entradas)
    print '  arrancando %d, ficam %d' % (len(tirou), len(fica))
    for campos in tirou:
        print '    %s %d,%d  %r' % (campos[0], int(campos[1]), int(campos[2]),
                                    campos[6] if len(campos) > 6 else '')

    fonte = monta(base, fica, tirou)
    compila(fonte)
    print '  luac -p: o fonte gerado compila (%d bytes)' % len(fonte)
    confere(fonte, base, fica)

    if so_confere:
        if not os.path.exists(SAIDA):
            print '\n! o override NAO existe em %s' % SAIDA
            return 1
        atual = open(SAIDA, 'rb').read()
        # Fora o carimbo de hora do cabecalho, que muda a cada rodada e nao
        # diz nada sobre o conteudo.
        if sem_carimbo(atual) != sem_carimbo(fonte):
            print '\n! o override em disco esta DIFERENTE do que esta receita gera'
            return 1
        print '\nok: o override em disco e exatamente o que esta receita gera.'
        return 0

    velho = salva_backup(SAIDA)
    if velho:
        print '  backup: %s' % os.path.basename(velho)
    fh = open(SAIDA, 'wb')
    fh.write(fonte)
    fh.close()
    print '\ngravado: %s' % SAIDA

    if '\xef\xbf\xbd' in fonte:
        print '! o arquivo tem U+FFFD - acento perdido. NAO usar.'
        return 1

    print
    print 'E CLIENTE: fechar e reabrir o cliente, e sair e voltar ao mapa.'
    print 'Para chegar ao jogador precisa de PATCH (CLAUDE.md 4.18).'
    return 0


if __name__ == '__main__':
    sys.exit(main())
