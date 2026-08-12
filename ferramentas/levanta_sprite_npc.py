# -*- coding: utf-8 -*-
"""Levanta o desenho de um sprite de NPC que nasce enterrado no chao.

Python 2.7.

    python levanta_sprite_npc.py --ver <SPRITE>
    python levanta_sprite_npc.py <SPRITE> <y>

O PROBLEMA. O `.act` diz a que altura o desenho e colado em relacao a celula
(ver ferramentas/act.py). Com `y = 0` o CENTRO do sprite fica na altura do
chao: a metade de baixo vai para debaixo do piso, o depth buffer do terreno a
corta, e o NPC aparece com um corte reto e horizontal na base. Nao e o mapa,
nao e a celula, nao e o script - e o `.act`.

Caso vivo, 2026-08-12: a Maquina de Sombrios Gerais (auction_01 193,58, sprite
910 `2_COLAVEND`). As maquinas oficiais deste cliente levantam o desenho entre
40 e 53 pixels e o `2_COLAVEND` e o unico com `y = 0` nas oito direcoes:

    4_vending_machine    122px de altura   y = -53
    4_VENDING_MACHINE    122px             y = -53
    2_DROP_MACHINE       118px             y = -44
    2_VENDING_MACHINE1   114px             y = -40
    2_COLAVEND           123px             y =   0   <- enterrada

QUE VALOR USAR: `-(altura/2 - 8)`, que e a conta que os quatro oficiais seguem
- o centro sobe meia altura e a base afunda uns 8 pixels, para a peca parecer
plantada e nao flutuando. Para o 2_COLAVEND (123px) da -53, o mesmo do
4_vending_machine, que tem praticamente a mesma altura.

ONDE O ARQUIVO VAI PARAR, e este e o aviso: em

    C:\\GuerraDoEmperium\\cliente\\data\\sprite\\npc\\<SPRITE>.act

que e CLIENTE, esta FORA DO GIT e nao sobrevive a um cliente novo (CLAUDE.md
secao 1). Vence o GRF pelo DataFolderFirst. Esta ferramenta e a receita
versionada para repor: apagar o arquivo solto reverte, porque o original nunca
saiu do GRF.

O `.act` de varios sprites antigos esta com DES no NOSSO data.grf e nao se le;
nesses casos ele vem do GRF do bRO, que e a mesma revisao oficial do arquivo.
O `--ver` diz de onde veio.

DEPOIS DE RODAR: fechar e reabrir o cliente. `@reloadscript` nao alcanca isto -
o sprite e do lado de la.
"""

import os
import shutil
import sys
import time

import act
import grf


NOSSO_GRF = os.path.join('C:\\', 'GuerraDoEmperium', 'cliente', 'data.grf')
BRO_GRF = os.path.join('C:\\', 'Program Files (x86)',
                       'Gravity Interactive, Inc', 'Ragnarok Brazil',
                       'data.grf')
DESTINO = os.path.join('C:\\', 'GuerraDoEmperium', 'cliente', 'data',
                       'sprite', 'npc')
BACKUP = os.path.join('C:\\', 'GuerraDoEmperium', 'backup-registro')


def le_act(sprite):
    """Devolve (bytes, de_onde). Tenta o nosso GRF; cai no do bRO se DES."""
    caminho = os.path.join('data', 'sprite', 'npc', sprite + '.act')
    try:
        return grf.Grf(NOSSO_GRF).read(caminho), 'nosso data.grf'
    except Exception as erro:
        if 'DES' not in str(erro) and 'KeyError' not in repr(erro):
            raise
        return grf.Grf(BRO_GRF).read(caminho), 'GRF do bRO (o nosso tem DES)'


def mostra(sprite):
    dados, origem = le_act(sprite)
    a = act.Act(dados)
    pares = sorted(set((x, y) for (_p, x, y) in a.camadas))
    print '%s   %d bytes, de %s' % (sprite, len(dados), origem)
    print '  versao %x, %d acoes, %d camadas' % (
        a.versao, len(a.acoes), len(a.camadas))
    print '  pares (x,y) distintos: %s' % pares
    ys = [y for (_p, _x, y) in a.camadas]
    print '  y de %d a %d' % (min(ys), max(ys))
    if max(ys) > -20:
        print '  AVISO: y perto de zero - este sprite nasce enterrado.'


def aplica(sprite, novo_y):
    dados, origem = le_act(sprite)
    a = act.Act(dados)
    antes = sorted(set(y for (_p, _x, y) in a.camadas))
    saida = a.desloca_y(novo_y)

    # Round-trip: reler o resultado e conferir que so o `y` mudou e que o
    # tamanho nao mexeu. Sem isto, um .act corrompido so aparece na tela.
    b = act.Act(saida)
    depois = sorted(set(y for (_p, _x, y) in b.camadas))
    assert len(saida) == len(dados), 'tamanho mudou'
    assert depois == [novo_y], 'y saiu %s' % depois
    assert [x for (_p, x, _y) in b.camadas] == \
           [x for (_p, x, _y) in a.camadas], 'x mudou'

    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)
    alvo = os.path.join(DESTINO, sprite + '.act')
    if os.path.exists(alvo):
        if not os.path.isdir(BACKUP):
            os.makedirs(BACKUP)
        copia = os.path.join(BACKUP, '%s.act.%s'
                             % (sprite, time.strftime('%Y%m%d-%H%M%S')))
        shutil.copy2(alvo, copia)
        print 'override anterior guardado em %s' % copia

    fh = open(alvo, 'wb')
    fh.write(saida)
    fh.close()
    print '%s: y %s -> %d  (%d camadas), de %s' % (
        sprite, antes, novo_y, len(a.camadas), origem)
    print 'gravado em %s' % alvo
    print 'FECHAR E REABRIR O CLIENTE - @reloadscript nao alcanca sprite.'


def main():
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == '--ver':
        mostra(args[1])
        return 0
    if len(args) == 2:
        aplica(args[0], int(args[1]))
        return 0
    print __doc__
    return 2


if __name__ == '__main__':
    sys.exit(main())
