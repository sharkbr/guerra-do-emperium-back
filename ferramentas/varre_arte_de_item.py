# -*- coding: cp1252 -*-
u"""Todo item OBTENIVEL cuja arte de chao/icone falta no cliente.

    python varre_arte_de_item.py              # a lista, e sai 1 se houver
    python varre_arte_de_item.py --tudo       # sem filtrar por obtenibilidade

Complemento do `valida_visual.py`, que so olha `item_db_equip.yml` - chapeu,
arma, acessorio. Este olha QUALQUER item, inclusive Etc e Usable, porque a
caixa de erro nao pergunta o tipo: ela sai quando o cliente abre um arquivo
que nao existe.

**Item de DROP tambem derruba o cliente.** O habito da CLAUDE.md 4.4 nasceu de
loja ("validar arte antes de por item na vitrine"), e por isso item que so cai
de monstro nunca passou por conferencia nenhuma. Nao precisa de vitrine: basta
o jogador carregar o item e arrastar, vender ou largar. Foi assim que a
Fragrant Flowers (1001089), que cai do Napeo no Laboratorio Abandonado, chegou
como relato de "o jogo crasha ao mover ou vender" em 2026-09-22.

Os QUATRO arquivos conferidos sao os que valem para qualquer item, e sao os
mesmos do `valida_visual.Cliente.caminhos(res, None)`:

    data\\sprite\\<item>\\<res>.spr              sprite do chao
    data\\sprite\\<item>\\<res>.act              idem
    data\\texture\\<ui>\\item\\<res>.bmp          icone do inventario  (modal)
    data\\texture\\<ui>\\collection\\<res>.bmp    icone grande

"Obtenivel" aqui e drop de monstro (`db/re/mob_db.yml`) ou venda em loja de
NPC (qualquer `shop`/`cashshop`/`itemshop`/`pointshop`/`marketshop` em
`npc/`). E um piso, nao um teto: item que so sai de caixa, de missao ou de
`getitem` em script NAO entra na conta - para esses, `--tudo`.

O nome do recurso sai do `itemInfo.lua` do NOSSO cliente, que e quem o cliente
le. Quando ele e ASCII e parece um AegisName (`Fruits_Set_Trap`), a entrada
provavelmente nasceu do `completa_iteminfo.py` sobre um id que o bRO nao tem -
e ai a arte tende a faltar nos dois GRFs.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
import completa_iteminfo as ci

RATHENA = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'rathena')

# A linha de loja de um NPC: os campos vem separados por TAB, e o que interessa
# e o resto da linha depois do tipo - dali saem os pares `<id>:<preco>`.
LOJA = re.compile(r'\t(?:shop|cashshop|itemshop|pointshop|marketshop)\t[^\n]*')
PAR_DE_LOJA = re.compile(r'(\d+):-?\d+')

ID = re.compile(r'  - Id: (\d+)')
AEGIS = re.compile(r'    AegisName: (\S+)')
NOME = re.compile(r'    Name: (.+)')
DROP = re.compile(r'\s+- Item: (\S+)')
ENTRADA = re.compile(r'\[(\d+)\] = \{')
# A quebra de linha e a indentacao NAO sao enfeite: `unidentifiedResourceName`
# TERMINA em `identifiedResourceName`, e um regex solto casa com a linha errada
# (CLAUDE.md secao 5). Os dois campos sao iguais na maioria dos itens, e ai o
# engano nao aparece - so nos poucos em que diferem, que sao justamente os que
# esta ferramenta existe para achar.
RECURSO = re.compile(r'\n\t\tidentifiedResourceName = "([^"]*)"')


def le_item_db():
    u"""(AegisName -> id, id -> Name) de todos os item_db do vendor."""
    aegis, nomes = {}, {}
    for arq in ('item_db.yml', 'item_db_equip.yml',
                'item_db_etc.yml', 'item_db_usable.yml'):
        caminho = os.path.join(RATHENA, 'db', 're', arq)
        if not os.path.exists(caminho):
            continue
        iid = None
        for linha in open(caminho, 'rb'):
            m = ID.match(linha)
            if m:
                iid = int(m.group(1))
                continue
            if iid is None:
                continue
            m = AEGIS.match(linha)
            if m:
                aegis[m.group(1)] = iid
            m = NOME.match(linha)
            if m:
                nomes[iid] = m.group(1).strip().strip('"')
    return aegis, nomes


def dropados(aegis):
    u"""Id de todo item que aparece num `Drops:`/`MvpDrops:` do mob_db."""
    saida = set()
    caminho = os.path.join(RATHENA, 'db', 're', 'mob_db.yml')
    for linha in open(caminho, 'rb'):
        m = DROP.match(linha)
        if m and m.group(1) in aegis:
            saida.add(aegis[m.group(1)])
    return saida


def vendidos():
    u"""Id de todo item que aparece numa linha de loja de NPC.

    Nao distingue loja ligada de desligada, de proposito: um `disablenpc` no
    original nao apaga a vitrine da nossa duplicata (CLAUDE.md secao 2).
    """
    saida = set()
    for raiz, _, arquivos in os.walk(os.path.join(RATHENA, 'npc')):
        for nome in arquivos:
            if not nome.endswith('.txt'):
                continue
            texto = open(os.path.join(raiz, nome), 'rb').read()
            for m in LOJA.finditer(texto):
                for p in PAR_DE_LOJA.finditer(m.group(0)):
                    saida.add(int(p.group(1)))
    return saida


def main(argv):
    tudo = '--tudo' in argv
    aegis, nomes = le_item_db()
    cai = dropados(aegis)
    vende = vendidos()
    cliente = vv.Cliente()
    dados = open(ci.ITEMINFO, 'rb').read()

    ruins = []
    for m in ENTRADA.finditer(dados):
        ini = m.end()
        fim = dados.find('\n\t},', ini)
        bloco = dados[ini:fim]
        res = RECURSO.search(bloco)
        if not res or not res.group(1):
            continue
        iid = int(m.group(1))
        if not tudo and iid not in cai and iid not in vende:
            continue
        faltam = [rot for rot, cam in cliente.caminhos(res.group(1), None)
                  if not cliente.existe(cam)]
        if not faltam:
            continue
        de_onde = 'drop' if iid in cai else ('loja' if iid in vende else '-')
        ruins.append((iid, nomes.get(iid, '?'), len(faltam), de_onde,
                      res.group(1)))

    titulo = 'todos os itens' if tudo else 'itens obteniveis (drop ou loja)'
    print '%s com arte de chao/icone faltando: %d' % (titulo, len(ruins))
    for iid, nome, quantos, de_onde, res in ruins:
        print '  %8d  %d/4  %-5s %-34s res=%r' % (iid, quantos, de_onde,
                                                  nome[:34], res)
    if ruins:
        print
        print 'Cada um destes entrega caixa de erro ao ser movido, vendido ou'
        print 'largado. A saida e a arte do bRO quando ele a tem, ou apontar o'
        print 'resourceName do itemInfo.lua para uma arte que o cliente ja tem.'
    return 1 if ruins else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
