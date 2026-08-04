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
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Os DOIS bancos, na mesma ordem em que o servidor os encadeia: o do rAthena e
# depois o nosso, que o `Footer: Imports:` faz vencer em caso de ID repetido.
#
# O segundo entrou em 2026-08-01. Sem ele as ferramentas ficavam cegas para
# item NOSSO: os cinco placeholders do Mercado Contemporaneo (Ceuci, Armadura
# Resistente, Roupa de Natal do Antonio, Broche da Celine e Garra Diabolica)
# foram pulados com "nao esta no item_db_equip.yml" numa passada de instalacao
# que resolveu todos os outros - e o motivo nao era arte faltando, era o
# arquivo nao ser lido.
ITEM_DB = [os.path.join(_RAIZ, 'rathena', 'db', 're', 'item_db_equip.yml'),
           os.path.join(_RAIZ, 'rathena', 'db', 'guerra', 'item_db.yml')]

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


def caminho_disco(caminho):
    u"""Caminho CP949 do GRF -> o nome que o arquivo REALMENTE tem no disco.

    Esta funcao e o assunto inteiro do bug de 2026-07-31, entao vale escrever
    por extenso. O cliente e um app coreano que chama as APIs **ANSI** do
    Windows: ele monta o caminho em bytes CP949 e entrega para `CreateFileA`,
    que interpreta esses bytes na **codepage ANSI do sistema** - cp1252 nesta
    maquina, nao CP949. Resultado: o nome que o cliente procura no disco nao e
    `유저인터페이스`, e o mojibake `À¯ÀúÀÎÅÍÆäÀÌ½º`.

    Dentro do GRF isso nao aparece, porque la a tabela guarda os bytes crus e
    eles casam. So no disco a diferenca existe.

    A prova esta na propria instalacao: a pasta que o ROenglishRE criou e que o
    cliente le sem reclamar chama-se `À¯ÀúÀÎÅÍÆäÀÌ½º`. Gravar em
    `유저인터페이스` cria uma segunda pasta, de aparencia correta, que o cliente
    nunca abre - foi exatamente o que aconteceu com 5855 arquivos, e o sintoma
    foi `Resource File Loading fail` num arquivo que estava la.

    `decode('mbcs')` e a expressao exata disso: usa a codepage ANSI do sistema,
    que e o que `CreateFileA` vai usar.
    """
    return os.path.join(CLIENTE.decode('mbcs'), caminho.decode('mbcs'))


def rotulo(caminho):
    """Troca o trecho coreano por um marcador legivel no terminal."""
    return (caminho.replace(ITEM, '<item>').replace(ACESS, '<acessorio>')
            .replace(UI, '<ui>').replace(HOMEM, '<M>').replace(MULHER, '<F>'))


# ---------------------------------------------------------------- fontes

def le_item_db(caminhos):
    """TODOS os itens dos arquivos dados (um caminho ou uma lista deles).

    Varredura linha a linha: o YAML tem 6 MB e a estrutura das entradas e
    regular, entao nao vale trazer parser.

    Ate 2026-08-01 esta funcao devolvia so `item de cabeca COM View`, e as duas
    ferramentas herdavam esse recorte. O recorte estava errado: dos oito
    recursos que um item pode ter, **quatro valem para qualquer item** - os dois
    de sprite de chao e os dois de icone. So os quatro de cabeca dependem de
    ser chapeu.

    O que provou isso foi o Mercado Contemporaneo: o Anel de Jupiter (32258) e
    acessorio, nao passava nem perto deste filtro, e entregava caixa modal
    `Resource File Loading fail ... item\\ringofjupiter.bmp` ao abrir a loja.
    Nove dos onze acessorios do mercado estavam nesse estado, e o
    `valida_visual.py` dizia que estava tudo bem porque nem olhava para eles.

    Quem filtra agora e quem chama. O campo `view_cabeca` e o que interessa
    para a camada de cabeca: um item que nao seja chapeu recebe None ali AINDA
    QUE tenha `View`, porque em arma o `View` significa outra coisa (a classe
    de sprite da arma) e passa-lo ao `accessoryid` daria resposta sem sentido.
    """
    if isinstance(caminhos, str):
        caminhos = [caminhos]
    itens = []
    estado = {'atual': None}
    locais = False

    def fecha():
        atual = estado['atual']
        if atual:
            atual['view_cabeca'] = atual['view'] if atual['cabeca'] else None
            itens.append(atual)
        estado['atual'] = None

    for caminho in caminhos:
        if not os.path.exists(caminho):
            continue
        fecha()
        for linha in open(caminho, 'rb'):
            m = re.match(r'\s*- Id:\s*(\d+)', linha)
            if m:
                fecha()
                estado['atual'] = {'id': int(m.group(1)), 'aegis': '',
                                   'nome': '', 'view': None, 'cabeca': False,
                                   'view_cabeca': None}
                locais = False
                continue
            atual = estado['atual']
            if atual is None:
                continue
            m = re.match(r'\s*AegisName:\s*(\S+)', linha)
            if m:
                atual['aegis'] = m.group(1)
                continue
            m = re.match(r'\s*Name:\s*(.+?)\s*$', linha)
            if m:
                # Corta comentario YAML no fim da linha. O item_db do rAthena
                # nao usa, mas o nosso db/guerra/item_db.yml usa para anotar o
                # nome do bRO ao lado do nome em ingles, e sem isto o nome
                # exibido vira "Sturdy Armor # bRO: Armadura Resistente".
                atual['nome'] = re.sub(r'\s+#.*$', '', m.group(1))
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
    fecha()
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


# ------------------------------------------------- tabelas de acessorio

# Onde as duas tabelas moram, tanto na tabela do GRF quanto no disco. Tudo
# ASCII aqui - o coreano do `caminho_disco` nao entra nesta parte da arvore.
ACC_DIR = q('data', 'luafiles514', 'lua files', 'datainfo')
ACC_ID = q(ACC_DIR, 'accessoryid.lub')
ACC_NOME = q(ACC_DIR, 'accname.lub')


def _desescapa(s):
    """Desfaz os escapes Lua que o `estende_accessoryid.py` grava."""
    return re.sub(r'\\(\d{1,3}|.)',
                  lambda m: chr(int(m.group(1))) if m.group(1).isdigit()
                  else m.group(1), s)


def _pares_de_texto(texto):
    """Le a forma TEXTO das duas tabelas - a que o nosso override usa.

    O cliente le `.lub` em texto e em bytecode indiferentemente (os arquivos do
    ROenglishRE em `data\\` sao texto puro e sao lidos todo dia), entao o
    override e gravado em texto. O formato e fechado e gerado por nos, logo
    regex basta - nao ha Lua arbitrario para interpretar aqui.
    """
    pares = []
    # O nome da constante NAO pode ser preso a `ACCESSORY_`: a tabela da
    # propria Gravity tem `ACCESORY_RED_NAVY_HAT` e `ACCESORY_BERET`, com um S
    # so. Prender ao prefixo perdia essas duas caladas, e foi o round-trip do
    # `estende_accessoryid.py` que acusou (2191 lidas contra 2193 gravadas).
    # A linha `ACCESSORY_IDs = {` nao casa porque o valor tem que ser numero
    # ou string entre aspas.
    padrao = (r'(?m)^\s*(?:\[ACCESSORY_IDs\.)?([A-Za-z_]\w*)\]?\s*=\s*'
              r'(?:(-?\d+)|"((?:[^"\\]|\\.)*)")\s*,')
    for m in re.finditer(padrao, texto):
        const, num, txt = m.group(1), m.group(2), m.group(3)
        pares.append((const, int(num) if num is not None else _desescapa(txt)))
    return pares


def le_tabelas_acessorio(grf):
    """(const -> view id, const -> sufixo do arquivo de cabeca).

    **Disco primeiro, porque e assim que o cliente le**: o `DataFolderFirst`
    faz `cliente\\data\\` vencer o GRF. Sem esta ordem as ferramentas
    continuariam respondendo pelo GRF de 2021 depois de o override do
    `estende_accessoryid.py` ter entrado, e jurariam que um View recem-
    acrescentado nao existe - com o cliente desenhando o chapeu na tela.
    """
    def le(caminho):
        disco = caminho_disco(caminho)
        if os.path.exists(disco):
            return _pares_de_texto(open(disco, 'rb').read())
        return tabela_lua(luadis.read_func(luadis.R(grf.read(caminho), 12)), [])

    ids = dict((k, int(v)) for k, v in le(ACC_ID) if isinstance(k, str))
    nomes = dict((k, v) for k, v in le(ACC_NOME) if isinstance(k, str))
    return ids, nomes


class Cliente(object):
    """Responde uma pergunta so: este caminho existe para o cliente?

    O `DataFolderFirst` esta ligado, entao o disco vence o GRF - mas para
    *existir* basta estar num dos dois.
    """

    def __init__(self):
        self.grf = Grf(GRF)
        ids, nomes = le_tabelas_acessorio(self.grf)
        # view id -> sufixo do arquivo de sprite de cabeca
        self.acc = {}
        for const, vid in ids.items():
            if const in nomes:
                self.acc[int(vid)] = nomes[const]

    def existe(self, caminho):
        if caminho.lower() in self.grf.entries:
            return True
        return os.path.exists(caminho_disco(caminho))

    def caminhos(self, res, view):
        """Os arquivos que o cliente abre para um item, em CP949.

        Os QUATRO primeiros valem para qualquer item - sprite de chao e icones.
        Os quatro de cabeca so entram quando `view` nao e None, ou seja quando
        o chamador ja decidiu que o item e chapeu (ver `le_item_db`, campo
        `view_cabeca`). Passar `view=None` para acessorio ou arma e o uso
        normal, nao caso de borda.

        Fonte unica da verdade: o `instala_visual.py` usa esta mesma lista para
        saber onde gravar. Caminho em CP949 porque e assim que ele existe na
        tabela do GRF; quem for tocar no disco converte com `caminho_disco`.
        """
        fora = [
            ('sprite de chao (.spr)', q('data', 'sprite', ITEM, res + '.spr')),
            ('sprite de chao (.act)', q('data', 'sprite', ITEM, res + '.act')),
            ('icone do inventario', q('data', 'texture', UI, 'item', res + '.bmp')),
            ('icone grande', q('data', 'texture', UI, 'collection', res + '.bmp')),
        ]
        if view is None:
            return fora
        suf = self.acc.get(view)
        if suf is None:
            fora.append(('view %d no accessoryid' % view, None))
        else:
            for g, rot in ((HOMEM, 'masculina'), (MULHER, 'feminina')):
                for ext in ('.spr', '.act'):
                    fora.append(('cabeca %s (%s)' % (rot, ext[1:]),
                                 q('data', 'sprite', ACESS, g, g + suf + ext)))
        return fora

    def recursos(self, res, view):
        """Os arquivos que o cliente abre para um chapeu, e se cada um existe."""
        return [(nome, cam, cam is not None and self.existe(cam))
                for nome, cam in self.caminhos(res, view)]


# ---------------------------------------------------------------- relatorio

# O que derruba o cliente com caixa de erro modal, em vez de so ficar feio.
#
# `icone do inventario` entrou nesta lista em 2026-08-01, medido in-game: abrir
# a loja do Acessorista do Mercado Contemporaneo entregou
#
#   Resource File Loading fail
#   texture\<ui>\item\ringofjupiter.bmp
#
# num item que nao tem sprite de cabeca nenhuma. Ou seja, **icone que falta e
# modal, nao so feio** - o que muda a conta antiga de "quebram: 548", medida em
# 2026-07-31 sob o criterio estreito. Numero de antes dessa data nao e
# comparavel com numero de depois.
#
# `icone grande` (a imagem da janela de descricao) ficou de fora por enquanto:
# nao foi visto dando modal. Ele e instalado junto de qualquer jeito, porque
# vem do mesmo lugar e custa o mesmo.
FATAIS = ('sprite de chao (.spr)', 'sprite de chao (.act)',
          'icone do inventario',
          'cabeca masculina (spr)', 'cabeca masculina (act)',
          'cabeca feminina (spr)', 'cabeca feminina (act)')


def main():
    args = sys.argv[1:]
    cli = Cliente()
    info = le_iteminfo(ITEMINFO)

    itens = le_item_db(ITEM_DB)

    if '--id' in args:
        # Aceita lista: `--id 32258,490337`. Um item so continua funcionando.
        for iid in [int(x) for x in args[args.index('--id') + 1].split(',')]:
            res = info.get(iid)
            item = ([i for i in itens if i['id'] == iid] or [None])[0]
            if res is None:
                print '%d nao esta no itemInfo.lua' % iid
                continue
            view = item['view_cabeca'] if item else None
            print '%d  %s  (%s, recurso "%s")' % (
                iid, item['nome'] if item else '?',
                ('View %d' % view) if view is not None else 'nao e chapeu',
                res)
            for nome, cam, tem in cli.recursos(res.lower(), view):
                print '  [%-5s] %-22s %s' % ('ok' if tem else 'FALTA', nome,
                                             rotulo(cam) if cam else '-')
        return 0

    # `--cabeca` reproduz o recorte antigo (so chapeu com View), para quem
    # quiser comparar com as medicoes de 2026-07-31.
    if '--cabeca' in args:
        itens = [i for i in itens if i['view_cabeca']]

    ok, quebrados, sem_info = [], [], []
    for it in itens:
        res = info.get(it['id'])
        if not res:
            sem_info.append(it)
            continue
        faltas = [n for n, _, tem in cli.recursos(res.lower(),
                                                  it['view_cabeca'])
                  if not tem]
        if [n for n in faltas if n in FATAIS or n.startswith('view ')]:
            quebrados.append((it, res, faltas))
        else:
            ok.append((it, res))

    print 'itens considerados no item_db:   %d' % len(itens)
    print '  desenhaveis por este cliente:  %d' % len(ok)
    print '  QUEBRAM (falta arte no GRF):   %d' % len(quebrados)
    print '  sem entrada no itemInfo.lua:   %d' % len(sem_info)

    def linha(it, res, extra):
        marca = ('view %-5d' % it['view_cabeca']) if it['view_cabeca'] else \
                '         '
        return '%7d  %s  %-34s %s' % (it['id'], marca, res, extra)

    if '--listar' in args:
        print
        for it, res, faltas in quebrados:
            print linha(it, res, ', '.join(faltas))
    if '--ok' in args:
        print
        for it, res in ok:
            print linha(it, res, it['nome'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
