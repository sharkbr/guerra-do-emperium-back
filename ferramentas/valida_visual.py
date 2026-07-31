# -*- coding: utf-8 -*-
"""Diz quais itens de visual o NOSSO cliente consegue desenhar.

O problema que motivou o script: o item 420047 (Costume Honorable Knight Cloak)
existe no `item_db_equip.yml` do rAthena e no `itemInfo.lua` do ROenglishRE, e o
proprio `accessoryid.lub` do cliente conhece o View 2059 - mas **nenhum** dos
arquivos de arte esta no `data.grf` de 2021-11-03. Equipar da

    Spr :: Cannot find File : sprite\\<item>\\c_h_knight_cloak.spr

que e uma caixa de erro modal, nao um aviso.

Nao adianta olhar so o `item_db`, nem so o `itemInfo`, nem so o `accessoryid`:
as tres tabelas concordam que o item existe. Quem discorda e o GRF. Entao o
teste tem que ser feito contra os arquivos, e e isso que este script faz.

    python valida_visual.py                 # resumo
    python valida_visual.py --listar         # os quebrados, um por linha
    python valida_visual.py --id 420047      # um item so, com os 6 recursos
    python valida_visual.py --ok             # os que funcionam

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grf import Grf
import luadis

CLIENTE = r'C:\GuerraDoEmperium\cliente'
GRF = os.path.join(CLIENTE, 'data.grf')
DISCO = os.path.join(CLIENTE, 'data')
ITEMINFO = os.path.join(CLIENTE, 'SystemEN', 'LuaFiles514', 'itemInfo.lua')
ITEM_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'rathena', 'db', 're', 'item_db_equip.yml')

BS = chr(92)
# Nomes de pasta em coreano. Escritos como escape unicode de proposito: caminho
# com coreano nao sobrevive ao console nem a leitura casual do arquivo.
ITEM = u'\uc544\uc774\ud15c'.encode('cp949')                        # 아이템
ACESS = u'\uc545\uc138\uc0ac\ub9ac'.encode('cp949')                 # 악세사리
HOMEM = u'\ub0a8'.encode('cp949')                                   # 남
MULHER = u'\uc5ec'.encode('cp949')                                  # 여
UI = u'\uc720\uc800\uc778\ud130\ud398\uc774\uc2a4'.encode('cp949')  # 유저인터페이스

# Locations do item_db que fazem o cliente carregar sprite de cabeca.
LOCAIS_CABECA = ('Head_Top', 'Head_Mid', 'Head_Low',
                 'Costume_Head_Top', 'Costume_Head_Mid', 'Costume_Head_Low')


def q(*partes):
    return BS.join(partes)


def rotulo(caminho):
    """Troca o trecho coreano por um marcador legivel no terminal."""
    return (caminho.replace(ITEM, '<item>').replace(ACESS, '<acessorio>')
            .replace(UI, '<ui>').replace(HOMEM, '<M>').replace(MULHER, '<F>'))


# ---------------------------------------------------------------- fontes

def le_item_db(caminho):
    """Itens com View e posicao de cabeca. Varredura linha a linha: o YAML tem
    6 MB e a estrutura das entradas e regular, entao nao vale trazer parser."""
    itens = []
    atual = None
    locais = False
    for linha in open(caminho, 'rb'):
        m = re.match(r'\s*- Id:\s*(\d+)', linha)
        if m:
            if atual and atual['view'] and atual['cabeca']:
                itens.append(atual)
            atual = {'id': int(m.group(1)), 'aegis': '', 'nome': '',
                     'view': None, 'cabeca': False}
            locais = False
            continue
        if atual is None:
            continue
        m = re.match(r'\s*AegisName:\s*(\S+)', linha)
        if m:
            atual['aegis'] = m.group(1)
            continue
        m = re.match(r'\s*Name:\s*(.+?)\s*$', linha)
        if m:
            atual['nome'] = m.group(1)
            continue
        m = re.match(r'\s*View:\s*(\d+)', linha)
        if m:
            atual['view'] = int(m.group(1))
            continue
        if re.match(r'\s*Locations:', linha):
            locais = True
            continue
        m = re.match(r'\s*(\w+):\s*true', linha)
        if locais and m and m.group(1) in LOCAIS_CABECA:
            atual['cabeca'] = True
    if atual and atual['view'] and atual['cabeca']:
        itens.append(atual)
    return itens


def le_iteminfo(caminho):
    """id -> identifiedResourceName, do itemInfo.lua (texto, do ROenglishRE)."""
    res = {}
    atual = None
    for linha in open(caminho, 'rb'):
        m = re.match(r'\s*\[(\d+)\]\s*=\s*\{', linha)
        if m:
            atual = int(m.group(1))
            continue
        m = re.match(r'\s*identifiedResourceName\s*=\s*"(.*)"', linha)
        if m and atual is not None:
            res[atual] = m.group(1)
    return res


def tabela_lua(f, saida):
    """Reconstroi `{chave = valor}` seguindo LOADK/GETTABLE ate o SETTABLE.

    Nao da para ler so o pool de constantes: com mais de 256 constantes o Lua
    5.1 nao consegue usar RK direto no SETTABLE e passa a carregar chave e
    valor em registrador antes. As tabelas aqui tem ~2200 entradas, entao a
    forma com registrador e a regra, nao a excecao.
    """
    regs = {}
    for ins in f['code']:
        op = ins & 0x3f
        nome = luadis.OPNAMES[op] if op < len(luadis.OPNAMES) else ''
        A = (ins >> 6) & 0xff
        C = (ins >> 14) & 0x1ff
        B = (ins >> 23) & 0x1ff
        Bx = (ins >> 14) & 0x3ffff
        if nome == 'LOADK':
            regs[A] = f['k'][Bx]
        elif nome == 'SETTABLE':
            kb = f['k'][B - 256] if B >= 256 else regs.get(B)
            kc = f['k'][C - 256] if C >= 256 else regs.get(C)
            saida.append((kb, kc))
        elif nome == 'GETTABLE':
            regs[A] = f['k'][C - 256] if C >= 256 else regs.get(C)
        elif nome in ('GETGLOBAL', 'MOVE', 'NEWTABLE', 'CALL'):
            regs.pop(A, None)
    for p in f['protos']:
        tabela_lua(p, saida)
    return saida


class Cliente(object):
    """Responde uma pergunta so: este caminho existe para o cliente?

    O `DataFolderFirst` esta ligado, entao o disco vence o GRF - mas para
    *existir* basta estar num dos dois.
    """

    def __init__(self):
        self.grf = Grf(GRF)
        f = lambda n: luadis.read_func(luadis.R(self.grf.read(n), 12))
        base = 'data' + BS + 'luafiles514' + BS + 'lua files' + BS + 'datainfo' + BS
        ids = dict((k, v) for k, v in tabela_lua(f(base + 'accessoryid.lub'), [])
                   if isinstance(k, str))
        nomes = dict((k, v) for k, v in tabela_lua(f(base + 'accname.lub'), [])
                     if isinstance(k, str))
        # view id -> sufixo do arquivo de sprite de cabeca
        self.acc = {}
        for const, vid in ids.items():
            if const in nomes:
                self.acc[int(vid)] = nomes[const]

    def existe(self, caminho):
        if caminho.lower() in self.grf.entries:
            return True
        # O caminho vem em CP949 porque e assim que ele existe na tabela do
        # GRF. Para o sistema de arquivos ele precisa virar unicode: em
        # Python 2 no Windows, `os.path.exists` com caminho em bytes usa a
        # codepage ANSI (aqui cp1252), nao CP949 - os bytes coreanos viram
        # lixo e o teste responde "nao existe" para arquivo que esta la.
        # Falha calada, do tipo que produz diagnostico errado com confianca.
        solto = os.path.join(CLIENTE.decode('mbcs'),
                             caminho.decode('cp949', 'replace'))
        return os.path.exists(solto)

    def recursos(self, res, view):
        """Os arquivos que o cliente abre para um chapeu, e se cada um existe."""
        fora = [
            ('sprite de chao (.spr)', q('data', 'sprite', ITEM, res + '.spr')),
            ('sprite de chao (.act)', q('data', 'sprite', ITEM, res + '.act')),
            ('icone do inventario', q('data', 'texture', UI, 'item', res + '.bmp')),
            ('icone grande', q('data', 'texture', UI, 'collection', res + '.bmp')),
        ]
        suf = self.acc.get(view)
        if suf is None:
            fora.append(('view %d no accessoryid' % view, None))
        else:
            for g, rot in ((HOMEM, 'masculina'), (MULHER, 'feminina')):
                fora.append(('cabeca ' + rot,
                             q('data', 'sprite', ACESS, g, g + suf + '.spr')))
        return [(nome, cam, cam is not None and self.existe(cam))
                for nome, cam in fora]


# ---------------------------------------------------------------- relatorio

# O que derruba o cliente com caixa de erro modal, em vez de so ficar feio.
FATAIS = ('sprite de chao (.spr)', 'sprite de chao (.act)',
          'cabeca masculina', 'cabeca feminina')


def main():
    args = sys.argv[1:]
    cli = Cliente()
    info = le_iteminfo(ITEMINFO)

    if '--id' in args:
        iid = int(args[args.index('--id') + 1])
        res = info.get(iid)
        if res is None:
            print '%d nao esta no itemInfo.lua' % iid
            return 1
        item = [i for i in le_item_db(ITEM_DB) if i['id'] == iid]
        view = item[0]['view'] if item else None
        print '%d  %s  (View %s, recurso "%s")' % (
            iid, item[0]['nome'] if item else '?', view, res)
        if view is None:
            print '  sem View no item_db: o cliente nao desenha nada na cabeca'
            return 1
        for nome, cam, tem in cli.recursos(res.lower(), view):
            print '  [%-5s] %-22s %s' % ('ok' if tem else 'FALTA', nome,
                                         rotulo(cam) if cam else '-')
        return 0

    itens = le_item_db(ITEM_DB)
    ok, quebrados, sem_info = [], [], []
    for it in itens:
        res = info.get(it['id'])
        if not res:
            sem_info.append(it)
            continue
        faltas = [n for n, _, tem in cli.recursos(res.lower(), it['view'])
                  if not tem]
        if [n for n in faltas if n in FATAIS or n.startswith('view ')]:
            quebrados.append((it, res, faltas))
        else:
            ok.append((it, res))

    print 'itens de cabeca com View no item_db: %d' % len(itens)
    print '  desenhaveis por este cliente:      %d' % len(ok)
    print '  QUEBRAM (falta arte no GRF):       %d' % len(quebrados)
    print '  sem entrada no itemInfo.lua:       %d' % len(sem_info)

    if '--listar' in args:
        print
        for it, res, faltas in quebrados:
            print '%6d  view %-5d  %-34s %s' % (
                it['id'], it['view'], res, ', '.join(faltas))
    if '--ok' in args:
        print
        for it, res in ok:
            print '%6d  view %-5d  %-34s %s' % (
                it['id'], it['view'], res, it['nome'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
