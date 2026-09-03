# -*- coding: utf-8 -*-
u"""Poe no `itemInfo.lua` do cliente o numero de covas que o SERVIDOR declara.

    python ajusta_covas_do_cliente.py             # aplica (faz backup antes)
    python ajusta_covas_do_cliente.py --conferir  # so relata; sai 1 se faltar
    python ajusta_covas_do_cliente.py --id 1328   # so estes (lista com virgula)

Cova de item e mais um caso de **metade da configuracao no cliente** (CLAUDE.md
secao 4.9), e a divisao nao e obvia:

  - quem decide se a carta ENTRA e o servidor. A janela de encaixe e montada
    em `clif_use_card` a partir do `slots` do item_db, entao `Slots: 1` no
    db/ ja basta para o jogador encaixar.
  - quem desenha o **"[1]" no nome da arma** e o `slotCount` do
    `itemInfo.lua`, do lado do cliente, e ele nao pergunta nada ao servidor.

Ou seja: mexer so no `db/` deixa um item que ACEITA carta e nao PARECE aceitar
- o jogador nao tenta, e nada da erro. Mexer so no cliente e pior: promete uma
cova que o servidor recusa. As duas metades andam juntas ou nao andam.

**A fonte da verdade aqui e o SERVIDOR, nao o bRO.** E de proposito: o nosso
item_db pode discordar do bRO por decisao nossa (a secao de OVERRIDES do
db/guerra/item_db.yml existe para isso), e o que o jogador precisa e que a tela
diga o que o servidor faz. Para saber o que o bRO diz de um item, o
`estado_item.py --id <n>` imprime os tres lados numa tela so.

Vizinho de prateleira do `completa_iteminfo.py`, e a diferenca importa: aquele
IMPORTA a entrada inteira de um item que o cliente nao tem, e por desenho nao
toca entrada que ja exista. Este mexe num CAMPO de entrada que ja existe, e nao
olha para o bRO.

---------------------------------------------------------------- a lista fixa

A `COVAS` abaixo e a lista dos itens que este script cuida, e ela e escrita a
mao de proposito. A alternativa - varrer as vitrines e alinhar tudo - foi
medida em 2026-09-03: dos 3396 itens das lojas, 16 divergem, e em 13 deles
quem promete a cova e o CLIENTE (entrada de 2021) enquanto o servidor nao a
da. Alinhar esses 13 tiraria da tela uma cova que o jogador ja ve, e isso e
decisao do dono, nao consequencia de script. Ficam anotados no PENDENCIAS.md.

**Ao mudar `Slots:` de um item, acrescentar o ID aqui e rodar.** O `--conferir`
sai 1 quando alguma das duas metades ficou para tras.

------------------------------------------------------------------- cuidados

O `itemInfo.lua` tem 22 MB, esta em ANSI e os `resourceName` sao bytes CP949
coreanos: aqui e tudo `rb`/`wb`, byte a byte, sem decodificar nada - a mesma
regra do `instala_item.py`. O que se troca e um numero ASCII dentro de uma
linha ASCII.

O cliente le esse arquivo **so na inicializacao**: depois de rodar, fechar e
reabrir. E como ele mora em `C:\\GuerraDoEmperium\\cliente\\`, a mudanca so
chega ao jogador por patch (CLAUDE.md secao 4.18) - `git commit` nao a leva.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como as vizinhas.
"""
import os
import re
import shutil
import sys
import time

import completa_iteminfo as ci

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATHENA = os.path.join(_RAIZ, 'rathena')

# Os quatro arquivos de item na ordem em que o servidor os encadeia - a mesma
# lista do estado_item.py. O ultimo a DECLARAR `Slots:` vence, que e o que o
# `ItemDatabase::parseBodyNode` faz (mescla por campo, ver o topo da secao de
# OVERRIDES do db/guerra/item_db.yml).
ITEM_DB = [os.path.join(RATHENA, 'db', 're', 'item_db_usable.yml'),
           os.path.join(RATHENA, 'db', 're', 'item_db_equip.yml'),
           os.path.join(RATHENA, 'db', 're', 'item_db_etc.yml'),
           os.path.join(RATHENA, 'db', 'guerra', 'item_db.yml')]

# -------------------------------------------------------------------------
# Os itens cuidados, por familia:
#
#   Linha Brutal (2026-09-03) - as quinze armas do Senhor das Armas, em
#   npc/guerra/mercado_contemporaneo.txt. O bRO da uma cova a familia
#   inteira; o nosso vendor nao dava nenhuma, e o cliente de 2021 tambem
#   nao. As duas metades entraram no mesmo dia.
# -------------------------------------------------------------------------
COVAS = [1328, 13147, 13342, 16082, 18171, 26141, 26206, 28033,
         28245, 28246, 28247, 28248, 28746, 32014, 32100]


class Erro(Exception):
    pass


def covas_do_servidor(caminhos):
    u"""id -> covas e id -> nome, mesclando por campo na ordem dada.

    NAO reusa o `valida_visual.le_item_db` de proposito, e a razao e uma
    armadilha: la o `slots` nasce 0 e ausencia de `Slots:` e indistinguivel de
    `Slots: 0`. Serve para quem le um arquivo so; aqui quebraria, porque um
    override que nao fale de cova zeraria a cova declarada no db/re/.
    """
    covas = {}
    nomes = {}
    for caminho in caminhos:
        if not os.path.exists(caminho):
            raise Erro('nao achei %s' % caminho)
        atual = None
        for linha in open(caminho, 'rb'):
            m = re.match(r'\s*- Id:\s*(\d+)', linha)
            if m:
                atual = int(m.group(1))
                continue
            if atual is None:
                continue
            m = re.match(r'\s*Slots:\s*(\d+)', linha)
            if m:
                covas[atual] = int(m.group(1))
                continue
            m = re.match(r'\s*Name:\s*(.+?)\s*$', linha)
            if m:
                nome = re.sub(r'\s+#.*$', '', m.group(1))
                if len(nome) >= 2 and nome[0] == '"' and nome[-1] == '"':
                    nome = nome[1:-1]
                nomes[atual] = nome
    return covas, nomes


# O `\t\t` e o recuo da entrada: `slotCount` mora um nivel dentro do bloco do
# item, e ha `slotCount` de outros itens no arquivo inteiro - por isso a busca
# acontece dentro do bloco daquele ID, nunca no arquivo todo.
SLOTCOUNT = re.compile(r'(\r\n\t\tslotCount = )(\d+)(,)')


def main():
    argv = sys.argv[1:]
    if '--ajuda' in argv or '-h' in argv:
        print __doc__.split('\n\n')[0]
        print
        print 'python ajusta_covas_do_cliente.py [--conferir] [--id <n>,<n>]'
        return 2

    conferir = '--conferir' in argv
    if '--id' in argv:
        alvos = [int(x) for x in argv[argv.index('--id') + 1].split(',')]
    else:
        alvos = list(COVAS)

    covas, nomes = covas_do_servidor(ITEM_DB)

    caminho = ci.ITEMINFO
    dados = open(caminho, 'rb').read()
    antes = len(dados)
    print 'servidor: db/re/ + db/guerra/item_db.yml'
    print 'cliente:  %s' % caminho
    print '          %d bytes' % antes
    print

    trocas = faltas = 0
    for iid in alvos:
        nome = nomes.get(iid, '?')
        quer = covas.get(iid, 0)
        lim = ci.bloco(dados, iid)
        if lim is None:
            print ('  [SEM CLI] %-7d %-28s entrada nao existe - rode o '
                   'completa_iteminfo.py' % (iid, nome))
            faltas += 1
            continue
        trecho = dados[lim[0]:lim[1]]
        m = SLOTCOUNT.search(trecho)
        if not m:
            print ('  [SEM CAM] %-7d %-28s a entrada nao tem linha slotCount'
                   % (iid, nome))
            faltas += 1
            continue
        tem = int(m.group(2))
        if tem == quer:
            print '  [igual  ] %-7d %-28s %d cova(s)' % (iid, nome, tem)
            continue
        novo = (trecho[:m.start()] + m.group(1) + str(quer) + m.group(3) +
                trecho[m.end():])
        dados = dados[:lim[0]] + novo + dados[lim[1]:]
        print '  [troca  ] %-7d %-28s %d -> %d cova(s)' % (
            iid, nome, tem, quer)
        trocas += 1

    print
    print '%d trocas, %d sem caminho' % (trocas, faltas)
    if conferir:
        if trocas or faltas:
            print
            print 'FALTA RODAR: python ajusta_covas_do_cliente.py'
            return 1
        print 'O cliente e o servidor concordam nas %d.' % len(alvos)
        return 0
    if faltas:
        print 'Resolva os "sem caminho" acima antes de dar por fechado.'
    if not trocas:
        print 'Nada a gravar.'
        return 1 if faltas else 0

    backup = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M'))
    shutil.copy2(caminho, backup)
    print 'Backup: %s' % os.path.basename(backup)
    fh = open(caminho, 'wb')
    fh.write(dados)
    fh.close()
    print 'Gravado: %s  (%d -> %d bytes)' % (caminho, antes, len(dados))
    print
    print 'O cliente le o itemInfo.lua so na inicializacao - feche e reabra.'
    print 'E o arquivo mora fora do git: para chegar ao jogador, patch'
    print '(ferramentas/monta_patch.py + publica_patch.sh).'
    return 1 if faltas else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
