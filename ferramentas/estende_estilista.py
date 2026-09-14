# -*- coding: utf-8 -*-
"""Poe as cores de roupa 8..15 na janela do estilista - a metade do CLIENTE.

    python estende_estilista.py                  # mostra o que a tabela do GRF tem
    python estende_estilista.py --aplicar        # grava o .lub novo em cliente\\data\\
    python estende_estilista.py --aplicar --ate 9   # so ate a cor 9 (para isolar defeito)
    python estende_estilista.py --conferir       # o arquivo no disco tem as 8..12? (sai 1 se nao)

A janela de estilista (o `openstylist` dos NPCs de npc/re/merchants/
Extended_Stylist.txt) e a 4.9 do CLAUDE.md em estado puro: o servidor tem
`db/re/stylist.yml` e o cliente tem
`data\\luafiles514\\lua files\\stylingshop\\stylingshopinfo.lub`, e os dois
listam AS MESMAS opcoes, cada um do seu lado. O cliente desenha a lista dele
e manda o INDICE (a posicao, 1-based) da opcao escolhida; o servidor procura
esse indice no yml e cobra o que o yml diz. Opcao que so existe num lado nao
da erro: no cliente sem o yml, o servidor recusa calado; no yml sem o cliente,
ninguem consegue pedir.

O `.lub` do GRF e bytecode (Lua 5.1) e define, por chamadas, as listas:
`StylingShop.AddBodyPalette(<cor>, {itid=<cupom>, boxitid=<caixa>})` para as
cores 0, 2..7 de humano (indices 1..7) e `AddDoramBodyPalette` para Doram. As
funcoes moram no `stylingshopinfo_f.lub`, que nao muda. Este script le o
bytecode com o `luadis.py`, reconstroi o arquivo INTEIRO como Lua em texto
(o cliente aceita texto: e assim que os do ROenglishRE vem, e um arquivo
invalido aqui derruba a janela com caixa de erro - provado em 2026-09-13)
e acrescenta as cores 8..12 nas duas listas de corpo, com o mesmo cupom das
2..7 (6046 Cupom de Tintura, caixa 16854). Reconstruir inteiro, e nao
remendar, e o que garante que cabelo, acessorio e traje continuam iguais.

A LISTA NAO BASTA - E O EXE: com a lista certa e as palettes no lugar, a
janela oferecia 3 cores (0, 2, 3) para toda classe que nao fosse de 4a.
Nao era arquivo: e um corte no exe, logo depois de GetSizeInTable
(`cmovne eax, ecx` com ecx = 3, em dois pontos). O
ferramentas/destrava_estilista.py tira o corte; sem ele, nada disto
aparece. As palettes sao lidas de cliente\data\palette\ como as do Edgard -
um guerra.grf foi tentado em 2026-09-14 sob a hipotese errada de que a
janela so via palette em GRF, e nao era preciso.

A metade do SERVIDOR e `db/guerra/stylist.yml`, escrita a mao, importada
pelo rodape de `db/re/stylist.yml`: Index 8..12 -> Value 8..12. O parser
(`StylistDatabase::parseBodyNode`, src/map/npc.cpp) faz merge por Look e
por Index, entao o arquivo nosso so lista o que acrescenta. Recarrega com
`@reloadscript` (o npc_reload chama `stylist_db.reload()`).

O que NAO muda: as cores 0..3 do Edgard (de graca) e o `max_cloth_color`
(15, conf/guerra/battle_guerra.txt) - sem ele o pc_changelook capa em 7
tambem por este caminho.

Roda em Python 2.7. E mudanca de cliente: vai por patch (4.18).
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grf import Grf

CLIENTE = r'C:\GuerraDoEmperium\cliente'
GRF = os.path.join(CLIENTE, 'data.grf')
ENTRADA = r'data\luafiles514\lua files\stylingshop\stylingshopinfo.lub'
DESTINO = os.path.join(CLIENTE, ENTRADA)
LUADIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'luadis.py')

# As cores 13, 14 e 15 (branco, cinza, preto) sao as CORES NOBRES: existem
# como palette, mas nao se compram - decisao do dono em 2026-09-14, para
# uma quest futura (PENDENCIAS.md, "Quest das cores nobres"). Por isso a
# estilista vai so ate a 12. O db/guerra/stylist.yml tem de bater.
CORES_NOVAS = range(8, 13)
# --ate N limita as cores novas a 8..N (N=7 e nenhuma): e o botao de
# isolar defeito, uma cor por vez, quando a janela nao mostra o esperado.
if '--ate' in sys.argv:
    CORES_NOVAS = range(8, int(sys.argv[sys.argv.index('--ate') + 1]) + 1)
CUPOM = {'itid': 6046, 'boxitid': 16854}     # os mesmos das cores 2..7


def chamadas(listagem):
    """[(funcao, [args])] a partir da listagem do luadis, so da funcao main."""
    saida = []
    atual = None
    args = []
    tabela = None
    for linha in listagem.splitlines():
        m = re.match(r'\s+\[\s*\d+\]\s+L-?\d+\s+(\w+)\s+(.*?)(?:\s+; (.*))?$', linha)
        if not m:
            continue
        op, campos, coment = m.group(1), m.group(2), m.group(3) or ''
        if op == 'GETTABLE' and coment.startswith('B=R0 C="'):
            atual = coment.split('"')[1]
            args = []
            tabela = None
        elif atual is None:
            continue
        elif op == 'LOADK':
            args.append(_num(coment))
        elif op == 'NEWTABLE':
            tabela = []
            args.append(tabela)
        elif op == 'SETTABLE' and tabela is not None:
            mk = re.match(r'B="([^"]+)" C=(.*)$', coment)
            tabela.append((mk.group(1), _num(mk.group(2))))
        elif op == 'LOADBOOL':
            args.append('true' if re.search(r'B=1', campos) else 'false')
        elif op == 'CALL':
            saida.append((atual, args))
            atual = None
    return saida


def _num(texto):
    texto = texto.strip()
    try:
        v = float(texto)
        return str(int(v)) if v == int(v) else str(v)
    except ValueError:
        return texto


def lua(chamada):
    nome, args = chamada
    partes = []
    for a in args:
        if isinstance(a, list):
            partes.append('{ ' + ', '.join('%s = %s' % kv for kv in a) + ' }')
        else:
            partes.append(a)
    return 'StylingShop.%s(%s)' % (nome, ', '.join(partes))


def monta(lista):
    linhas = ['-- Gerado por ferramentas/estende_estilista.py a partir do',
              '-- stylingshopinfo.lub do data.grf (Lua em texto, que o cliente aceita).',
              '-- As cores de roupa 8..12 sao nossas (ferramentas/tinge_roupas.py);',
              '-- o resto e o do GRF, chamada por chamada, na mesma ordem.',
              '']
    ultimo = None
    for c in lista:
        if c[0] != ultimo:
            linhas.append('')
            ultimo = c[0]
        linhas.append(lua(c))
        if c[0] in ('AddBodyPalette', 'AddDoramBodyPalette') and c[1][0] == '7':
            for cor in CORES_NOVAS:
                linhas.append(lua((c[0], [str(cor), [('itid', str(CUPOM['itid'])), ('boxitid', str(CUPOM['boxitid']))]])))
    return '\n'.join(linhas) + '\n'


def le_grf():
    g = Grf(GRF)
    dados = g.read(ENTRADA)
    tmp = os.path.join(os.environ.get('TEMP', '.'), 'stylingshopinfo.lub')
    open(tmp, 'wb').write(dados)
    listagem = subprocess.check_output([sys.executable, LUADIS, tmp])
    return chamadas(listagem)


def main():
    lista = le_grf()
    if '--conferir' in sys.argv:
        if not os.path.isfile(DESTINO):
            print 'falta: %s' % DESTINO
            return 1
        texto = open(DESTINO, 'rb').read()
        faltam = [c for c in CORES_NOVAS if 'AddBodyPalette(%d,' % c not in texto]
        print '%d de %d cores novas no disco' % (len(CORES_NOVAS) - len(faltam), len(CORES_NOVAS))
        return 1 if faltam else 0
    corpo = [c for c in lista if c[0] == 'AddBodyPalette']
    doram = [c for c in lista if c[0] == 'AddDoramBodyPalette']
    print 'no GRF: %d chamadas; corpo humano %s; doram %s' % (
        len(lista), [c[1][0] for c in corpo], [c[1][0] for c in doram])
    texto = monta(lista)
    if '--aplicar' not in sys.argv:
        print '(ensaio; --aplicar grava %s)' % DESTINO
        return 0
    d = os.path.dirname(DESTINO)
    if not os.path.isdir(d):
        os.makedirs(d)
    open(DESTINO, 'wb').write(texto)
    print 'gravado %s (%d chamadas + %d cores novas x 2)' % (DESTINO, len(lista), len(CORES_NOVAS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
