# -*- coding: utf-8 -*-
"""Aplica trocas e acréscimos de modelo num mapa, por receita declarativa.

Python 2.7, como o resto de ferramentas/.

Substitui o `destroi_mapa.py` na frente de Izlude. A diferença de abordagem
importa: aquele **simulava** destruição inclinando e afundando casa inteira;
este **troca** o modelo pelo de ruína que a Gravity já modelou. Depois que o
inventário do GRF mostrou 228 modelos de ruína, simular deixou de fazer
sentido -- ver ../CUSTOMIZACAO-VISUAL.md.

A ficção nesta fase: o meteoro já passou faz tempo e o céu limpou. Luz e chão
ficam ORIGINAIS; a destruição vive só na geometria.

Duas operações:

  substituir  -- troca o `filename` de instâncias existentes, mantendo posição
                 e rotação. Aceita fração (ex.: 30% dos muros) e sorteio entre
                 vários substitutos.
  acrescentar -- planta um modelo novo numa coordenada de jogo, com a altura
                 lida do .gat.

O que NÃO se toca: luz, água, chão, .gat. Nada aqui atravessa a fronteira do
servidor.

Uso:
    python edita_mapa.py <pasta-entrada> <pasta-saida> <data.grf> [mapa]
"""

import math
import os
import random
import sys

from gat import Gat
from grf import Grf
from rsw import Rsw, Modelo, texto
from catalogo_ingame import PREFIXO_MODELO, sem_prefixo, mundo


SEMENTE = 20260731   # fixa: rodar duas vezes dá o mesmo mapa

# -- o vocabulário da receita --------------------------------------------

ARVORES = [u'리히타르젠\\나무01.rsm', u'리히타르젠\\나무02.rsm',
           u'나무잡초꽃\\나무02.rsm']
MURO = u'프론테라\\시계탑벽.rsm'

OSSADA_02 = u'모로코\\동물뼈02.rsm'          # catálogo nº 117
OSSADA_04 = u'모로코\\동물뼈04.rsm'          # catálogo nº 119
ESPINHEIRO = u'나무잡초꽃\\묘르닐_가시덤불.rsm'   # catálogo nº 74
PAREDE_RUINA = u'중국\\중국-폐가벽03.rsm'     # catálogo nº 39

FONTE = u'oldcastle\\fountain.rsm'
ESCRIVANINHA = u'prontera_re\\desk_h_02.rsm'
SOFA = u'prontera\\sofa_01.rsm'
ESTATUA_03 = u'prontera\\prn_statue_03.rsm'
ESTATUA_08 = u'prontera\\prn_statue_08.rsm'

RECEITA = {
    'izlude': {
        'substituir': [
            # (o que trocar, por quais, fração das instâncias)
            (ARVORES, [OSSADA_02, ESPINHEIRO, OSSADA_04], 1.00),
            ([MURO], [PAREDE_RUINA], 0.30),
        ],
        'acrescentar': [
            # (modelo, célula x, célula y[, rotação Y[, escala]])
            # -- a altura sai do .gat
        ],
    },
    # O Centro da Ordem (npc/guerra/centro_da_ordem.txt). O mapa do antigo
    # leilao virou casa da cidade, e o meio do salao estava vazio: um pedestal
    # quadrado de 4x4 celulas (x178-181, y70-73), cercado de fosso e com quatro
    # pontes chegando nele. So faltava o que as pontes vao ver.
    #
    # ROTACAO 0, e nao sorteada: as CINCO instancias oficiais deste modelo no
    # GRF do bRO (1@def02, 1@gl_k, 1@gl_kh, 2@gl_k, 2@gl_kh) estao todas com
    # rot 0,0,0 e escala 1,0 -- so as de 1@gl_k/kh usam 1,04. Fonte e radial,
    # entao girar nao acrescenta nada; o que acrescenta e nao inventar numero.
    #
    # ESCALA 0,57, e a escala oficial NAO SERVIU AQUI. O modelo tem 35,34
    # unidades de largura (7,1 celulas) e o pedestal do centro tem 4 celulas,
    # 20 unidades: a 1,0 ela transbordava sobre o fosso, e em tela ficou grande
    # (visto pelo dono em 2026-08-11). 20 / 35,34 = 0,566, arredondado para
    # 0,57 -- 20,1 unidades, o pedestal exato.
    #
    # A licao, e ela vale para o proximo modelo: escala oficial e boa PISTA e
    # nao resposta. A Gravity usa esta fonte em patio de castelo de Glast Heim,
    # onde ha espaco; aqui o lugar tem 4 celulas. Quem copia a escala oficial
    # copia junto o tamanho do lugar de origem.
    #
    # CELULA 179.5, 71.5 E NAO 180, 72 -- e o pedido era "180,72". O pedestal
    # ocupa QUATRO celulas (x178-181, y70-73), numero PAR, entao o centro dele
    # cai na fronteira entre a 179 e a 180: mundo (400, 110). A celula 180 tem
    # centro em 402.5, meia celula fora. Em tela isso apareceu como a fonte
    # deslocada para cima e um pouco a direita do tampo (2026-08-11).
    #
    # -- A ESCRIVANINHA DA ALA LESTE (2026-08-11) --
    #
    # Pedido: `prontera_re\desk_h_02.rsm` em 191,72. Mesma correcao de meia
    # celula da fonte, e pela mesma razao -- so que aqui o vao NAO e o chao.
    #
    # O CHAO DA ALA LESTE E UNIFORME e os TAPETES SAO UV. O corredor leste
    # (x188-195) tem a textura 3 (모로코성-바닥3.bmp) do inicio ao fim; ler o id
    # de textura por tile mostra chao liso e ESCONDE os tres tapetes, que sao
    # outra regiao do mesmo .bmp escolhida pelas coordenadas UV da superficie.
    # Mapeando o UV aparecem tres tapetes de 8x8 celulas: x188-195 em y60-67,
    # y68-75 e y76-83. Os de fora tem sofa; o do meio estava vazio, e e nele
    # que 191,72 cai.
    #
    # CELULA 191.5, 71.5 E NAO 191, 72. O tapete do meio tem OITO celulas de
    # lado -- par --, entao o centro dele cai na fronteira: mundo (460, 110).
    # As quatro celulas centrais sao 191/192 x 71/72, e qualquer uma delas erra
    # o centro por meia celula. `191,72` e onde o personagem estava parado,
    # que e a leitura certa da intencao e o numero errado para centrar. Mesma
    # armadilha da fonte, com a diferenca de que o vao aqui e invisivel para
    # quem olha so o .gat: o chao e liso e andavel nas oito celulas.
    #
    # ROTACAO 90, alinhada com a ala e nao com o modelo. Os tres usos oficiais
    # no GRF do bRO (1@gol1 x2, brz_gld) dao 90, 180 e 270 -- nao decidem nada,
    # e dois deles ainda vem espelhados em X. Quem decide aqui e a sala: os
    # QUATRO sofas de auction_01 (x165 e x194, y64 e y80) estao todos em 90, e
    # 90 poe o lado longo do modelo (20,0 unidades em X a 0 graus) ao longo do
    # corredor. **Este e o numero para mexer se o dono quiser outra cara** --
    # 0 ou 180 atravessam a mesa no corredor, 270 e o 90 de costas.
    #
    # ESCALA 1,0, e desta vez a oficial serve. O modelo mede 20,02 x 13,84
    # unidades (4,0 x 2,8 celulas) num tapete de 8x8 -- ocupa metade da largura
    # dele. A conta e a mesma que rebaixou a fonte para 0,57; aqui ela aprova.
    #
    # As TRES TEXTURAS do .rsm (prontera_re\prt_h_14, prontera\prt_h_09,
    # prontera_re\prt_h_13) foram conferidas a parte no nosso GRF. O
    # `edita_mapa.py` so confere o caminho do .rsm -- textura que falta nao da
    # erro de parser, da superficie quebrada na tela.
    #
    # -- O SOFA DA ALCOVA NORTE (2026-08-11) --
    #
    # Pedido: `prontera\sofa_01.rsm` "entre as celulas 179,84 e 180,84, virado
    # para frente, para 180,83". As tres coisas que o pedido fixa - o par de
    # celulas, o eixo e o lado - caem em (179.5, 84.0) e rotacao 0.
    #
    # CELULA 179.5, 84.0. Mesma correcao de meia celula da fonte e da mesa, e
    # desta vez ela veio JUNTO COM O PEDIDO: o dono pediu duas celulas
    # (`179,84` e `180,84`), e o centro de um vao de largura 2 cai na fronteira
    # entre elas -- mundo (400.0, 172.5). O `84.0` fica inteiro porque em Y o
    # vao e de uma celula so.
    #
    # E o 179.5 nao e so aritmetica: e o eixo da ALCOVA NORTE. As tres cortinas
    # (`커텐01`) do fundo estao em x175.4, **179.4** e 183.4, a renda de cima
    # (`침대레이스2-1`) em 176.0, **179.5** e 182.9, e o forro de teto
    # (`천정틀`) em **179.5**, 86.5. O sofa entra no eixo que a sala ja tinha.
    #
    # ROTACAO 0, e desta vez ha MEDIDA por tras, nao escolha. Foram tres passos:
    #
    #   1) Qual eixo do .rsm e a altura? O **Z**. Medido nos proprios modelos
    #      deste salao: a coluna `기둥2` da 6,34 x 6,34 x 30,21 e a estatua
    #      `동상` da 8,57 x 5,43 x 29,25. Logo X = largura, Y = profundidade.
    #   2) De que lado do Y esta o encosto? **+Y**, nos dois sofas -- e o lado
    #      onde o modelo e alto (Z 17,60 contra 9,18 do lado do assento).
    #   3) Para onde aponta o +Y em cada rotacao? Calibrado nos QUATRO sofas
    #      que o mapa ja tem (`리히타르젠\소파02`, x164,9 e x193,9): os quatro
    #      estao em rot 90 e o que separa o par leste do oeste e o SINAL da
    #      terceira escala (+1,50 contra -1,50), que espelha a profundidade.
    #      O par leste encosta na parede leste, entao em rot 90 o +Y aponta
    #      para +X. Os 22 usos oficiais em `prt_cas`/`prt_cas_q` fecham a
    #      conta pelo outro lado: os de rot 270 tem parede colada a oeste.
    #      Ou seja +Y -> (sin, cos) em (X, Z), e em **rot 0 o encosto aponta
    #      para +Z, que e o norte** -- o sofa olha para o sul, para 180,83.
    #
    # Reparar que rot 0 e rot 180 poem a LARGURA no eixo leste-oeste, e 90/270
    # a poem no norte-sul. Nao e o contrario, e confundir isso poria o sofa
    # atravessado. As quatro pontes do fosso (`성_다리`, 58,97 de comprimento)
    # confirmam: as duas de rot 90 estao nos corredores norte-sul de x175 e
    # x184, e as duas de rot 180 nos vaos leste-oeste de y67 e y76.
    #
    # ESCALA 1,0, e aqui a oficial serve e a sala concorda. Os 22 usos no
    # castelo de Prontera vao de 0,80 a 1,00, com 1,00 sendo o mais comum. E a
    # conta que rebaixou a fonte para 0,57 aprova: 27,71 x 11,27 unidades =
    # **5,54 x 2,25 celulas** numa alcova de ~9 celulas (entre as colunas de
    # arco de x174,9 e x184,0). Sobra 1,7 celula de cada lado. Em profundidade
    # o sofa vai de y82,9 a y85,1, parando antes da renda de y85,6.
    #
    # As TRES TEXTURAS (prontera\prt_h_04, prt_h_05, prt_h_01) foram conferidas
    # no nosso GRF pelo `mede_rsm.py`: as tres resolvem. O `edita_mapa.py` so
    # confere o caminho do .rsm.
    #
    # E ELE NAO BLOQUEIA PASSAGEM, como todo modelo de .rsw. Ate 2026-08-11 as
    # celulas do sofa continuam andaveis; fechar e um `setwall` no
    # centro_da_ordem.txt, como o da escrivaninha.
    #
    # -- AS DUAS ESTATUAS DOS PLINTOS DO SUL (2026-08-11) --
    #
    # Pedido: `prn_statue_03` em 183,69 "virado pra esquerda" e `prn_statue_08`
    # em 177,69 "virado pra frente (177 67 por exemplo)", com a escala ajustada
    # para encaixar na base disponivel, no centro.
    #
    # OS QUATRO PLINTOS DE CANTO SAO DEGRAU NO `.gat`, e desta vez o vao estava
    # a vista -- diferente do tapete da escrivaninha, que so o UV mostrava.
    # Varrendo a altura media em volta do fosso aparecem quatro blocos de 2x2
    # celulas na altura **0,0**, contra 4,0 do piso do salao (no `.gat` o
    # negativo e para CIMA, entao 0,0 esta 4 unidades ACIMA do chao): x176-177 e
    # x182-183, nos y68-69 (sul) e y74-75 (norte). O pedestal da fonte, no meio,
    # esta em -5,0; o fosso em 15/20. Os quatro estavam vazios -- a varredura de
    # modelos em x172-188, y62-80 devolve so as quatro pontes.
    #
    # CELULA 182.5, 68.5 E 176.5, 68.5 -- QUARTA vez que a coordenada e
    # fracionaria, e pelo mesmo motivo das tres anteriores: plinto de **duas**
    # celulas de lado e vao de largura PAR, entao o centro cai na fronteira.
    # `183,69` e `177,69` sao a celula de canto de cada plinto, a mais perto do
    # meio do salao; centrar nelas erraria meia celula nos dois eixos. Mundo
    # (415.0, 95.0) e (385.0, 95.0) -- simetricos em volta de 400,0, que e o
    # eixo do salao (o mesmo da fonte e do sofa, a celula 179,5).
    #
    # A ORIGEM DESTES MODELOS E O CENTRO DA BASE, e isso teve de ser provado
    # porque as duas caixas nao se encontram na leitura crua: no
    # `prn_statue_03` a base (`Box031`) da X -21,50..-14,45 e a figura
    # (`Object07`) da X -5,13..3,91 -- uma nao esta em cima da outra. O que
    # reconcilia e o `pos` do NO RAIZ, que vale exatamente o centro da base
    # (-17,976 = o centro de -21,50..-14,45): os vertices da raiz sao em espaco
    # do modelo e entram como `vertice - pos`, e o filho entra deslocado de
    # `pos_filho - pos_raiz`, que aqui e (0,008; 0,441). Com isso a base cai em
    # **-3,53..+3,53 nos dois eixos** -- um quadrado de 7,06 perfeitamente
    # centrado na origem --, e e essa coincidencia que prova a leitura. O
    # `mede_rsm.py` mede NO A NO e nao aplica esse deslocamento; para decidir
    # centro de peca, ler a caixa de um no so nao basta.
    #
    # ESCALA 1,0 nas duas, e aqui a oficial serve **e a conta aprova**, ao
    # contrario da fonte. Os usos oficiais sao unanimes: `prt_lib`, `prt_lib_q`
    # e `prt_cas_q` usam as duas estatuas em 1,00, e os tres sao salao fechado
    # como o nosso -- e a ressalva que derrubou a fonte para 0,57 (patio de
    # Glast Heim) nao se aplica. A conta: o plinto tem 10x10 unidades, a
    # `_08` mede 7,98 de pegada (alcance 4,41 do centro, sobra 0,59) e a `_03`
    # mede 9,04 (alcance 5,22). **A `_03` passa 0,22 unidade da beirada** -- 4%
    # do meio-lado, um braco a 3,5 celulas de altura, e nao a base, que e de
    # 7,06 e sobra 1,47 de cada lado. Nao vale trocar a escala oficial por
    # 0,96 para corrigir isso. Altura: 25,03 e 23,92 unidades (5,0 e 4,8
    # celulas), menos que os quatro `모로코\동상` que o salao ja tem em pe
    # (29,25, escala 1,0) -- nao esbarram em nada.
    #
    # ROTACAO 90 e 0, e o "esquerda"/"frente" do pedido sao tela: em RO a
    # camera padrao poe o norte para cima, entao esquerda = oeste.
    #   `_03` -> oeste (olha para o meio do salao) -> **rot 90**
    #   `_08` -> sul   (olha para a entrada, 177,67) -> **rot 0**
    #
    # A CONVENCAO E A MESMA DO SOFA, e foi reconfirmada por fora: **rot 0 olha
    # para o SUL, 90 para oeste, 180 para norte, 270 para leste**. Tres provas
    # independentes, e a terceira so porque a segunda quase enganou:
    #   1) Os 22 usos do sofa em `prt_cas` ja tinham fechado `+Y -> (sen, cos)`,
    #      ou seja costas ao norte em rot 0.
    #   2) As quatro instancias oficiais destas duas estatuas: em `prt_lib` a
    #      `_08` esta em rot 180 encostada na parede sul de y29 com o salao
    #      aberto ao norte, e a `_03` em rot 180 na parede sul da alcova de
    #      x103-106/y40-41; em `prt_cas_q` a `_08` em rot 0 tem chao ao sul e
    #      parede ao norte, e a `_03` em rot 90 esta num nicho fechado a leste.
    #      Nenhuma outra convencao poe as quatro olhando para fora da parede.
    #   3) A figura pende para +Y nas duas (centro em +0,70 e +0,42 contra a
    #      base), que e o passo a frente -- e +Y e o sul em rot 0.
    #
    # **A FAMILIA NAO TEM FRENTE COMUM, e supor que tem inverte metade dela.**
    # No mesmo salao do `prt_lib`, lado a lado na mesma parede e olhando as
    # duas para o norte, a `_08` esta em rot 180 e a `prn_statue_02` em rot 0.
    # Sao oito modelos numerados, da mesma pasta, com a mesma cara de conjunto,
    # e pelo menos um deles nasceu virado ao contrario. Calibrar um e usar o
    # numero nos outros sete poe estatua de costas, calado. Medir POR MODELO.
    #
    # As duas texturas de cada uma (`prontera\prt_j_12.bmp` mais `prt_j_25` na
    # `_03` e `prt_j_30` na `_08`) resolvem no nosso GRF, conferidas pelo
    # `mede_rsm.py`. E, como todo modelo de .rsw, elas NAO bloqueiam passagem --
    # so que aqui isso nao custa nada: as celulas dos plintos ja nascem
    # bloqueadas no `.gat` (tipo 1). Nada de `setwall` desta vez.
    'auction_01': {
        'substituir': [],
        'acrescentar': [
            (FONTE, 179.5, 71.5, 0.0, 0.57),
            (ESCRIVANINHA, 191.5, 71.5, 90.0, 1.0),
            (SOFA, 179.5, 84.0, 0.0, 1.0),
            (ESTATUA_03, 182.5, 68.5, 90.0, 1.0),
            (ESTATUA_08, 176.5, 68.5, 0.0, 1.0),
        ],
    },
}

# Ao trocar um modelo por outro de tipo diferente, a escala do original quase
# nunca serve: ela foi escolhida para AQUELE modelo. Herdar 1,5 de uma árvore
# daria uma ossada gigante. A rotação, ao contrário, é preservada sempre --
# para muro ela é essencial (um segmento girado 90 graus é outra coisa), e para
# objeto espalhado ela só dá variedade.
ESCALA_NOVA = [1.0, 1.0, 1.0]


def cp949(u):
    return u.encode('cp949')


def aplica(r, g, receita, rnd, relatorio):
    subs = receita.get('substituir', [])
    total_trocado = 0

    for origens, destinos, fracao in subs:
        chaves = set(sem_prefixo(cp949(o)) for o in origens)
        alvos = [m for m in r.modelos if m.rsm in chaves]
        if not alvos:
            relatorio.append(u'  AVISO: nenhuma instância de %s'
                             % u', '.join(origens))
            continue
        quantos = int(round(len(alvos) * fracao))
        escolhidos = alvos if fracao >= 1.0 else rnd.sample(alvos, quantos)
        conta = {}
        for m in escolhidos:
            d = rnd.choice(destinos)
            m.arquivo = cp949(d).ljust(80, '\x00')
            m.escala = list(ESCALA_NOVA)
            conta[d] = conta.get(d, 0) + 1
        total_trocado += len(escolhidos)
        relatorio.append(
            u'  %d de %d instâncias de %s trocadas (%.0f%%): %s'
            % (len(escolhidos), len(alvos),
               u'/'.join(o.rsplit(u'\\', 1)[-1][:-4] for o in origens),
               fracao * 100,
               u', '.join(u'%s x%d' % (k.rsplit(u'\\', 1)[-1][:-4], v)
                          for k, v in sorted(conta.items()))))

    criados = 0
    for entrada in receita.get('acrescentar', []):
        # Os dois ultimos campos sao opcionais: rotacao Y em graus e escala.
        #
        # Sem rotacao, sorteia -- que e o certo para destroco espalhado
        # (variedade de graca) e o errado para peca posta de proposito, onde
        # numero sorteado e numero inventado.
        #
        # Sem escala, 1,0, que e o que a Gravity usa na maioria dos modelos.
        # A escala escala EM VOLTA DA ORIGEM do modelo, e a origem destes esta
        # na base: encolher nao tira a peca do chao.
        arquivo, cx, cy = entrada[0], entrada[1], entrada[2]
        giro = entrada[3] if len(entrada) > 3 else None
        esc = entrada[4] if len(entrada) > 4 else 1.0

        # A CELULA PODE SER FRACIONARIA, e para peca centrada isso nao e luxo:
        # o `mundo()` devolve o CENTRO da celula, entao coordenada inteira so
        # centraliza em vao de largura IMPAR. Num vao de 4 celulas o centro cai
        # na FRONTEIRA entre a 2a e a 3a, e a unica forma de acerta-lo e o meio
        # (ex.: 179.5). Ver a fonte do Centro da Ordem, na receita abaixo.
        #
        # A altura sai da celula que CONTEM o ponto -- `altura_media` indexa o
        # .gat e precisa de inteiro. Num vao plano tanto faz qual das quatro.
        wx, wz = mundo(g, cx, cy)
        wy = g.altura_media(int(cx), int(cy))
        m = Modelo.novo(cp949(arquivo), 'guerra_add_%03d' % criados, (wx, wy, wz))
        m.rot[1] = rnd.uniform(0.0, 360.0) if giro is None else giro
        m.escala = [esc, esc, esc]
        r.objetos.append(m)
        criados += 1
        relatorio.append(
            u'  + %s em %s,%s  mundo(%.2f, %.2f, %.2f)  rot Y %.1f  escala %.2f'
            % (arquivo, cx, cy, wx, wy, wz, m.rot[1], esc))
    if criados:
        relatorio.append(u'  %d modelos acrescentados' % criados)

    return total_trocado, criados


def main():
    if len(sys.argv) < 4:
        print __doc__
        return 1
    ent, sai, caminho_grf = sys.argv[1], sys.argv[2], sys.argv[3]
    mapa = sys.argv[4] if len(sys.argv) > 4 else 'izlude'

    if mapa.lower().startswith('prontera'):
        print 'recusado: Prontera fica intacta por decisao de ficcao.'
        return 3
    if mapa not in RECEITA:
        print 'sem receita para %s' % mapa
        return 1
    if not os.path.isdir(sai):
        os.makedirs(sai)

    r = Rsw(open(os.path.join(ent, mapa + '.rsw'), 'rb').read())
    ok, msg = r.verificar()
    if not ok:
        print 'rsw nao passou na verificacao: %s' % msg
        return 2
    g = Gat(open(os.path.join(ent, mapa + '.gat'), 'rb').read())

    rnd = random.Random(SEMENTE)
    relatorio = [u'%s:' % mapa]
    antes = len(r.objetos)
    aplica(r, g, RECEITA[mapa], rnd, relatorio)

    # Todo filename gravado tem que resolver no GRF. Caminho errado nao da erro
    # em parser nenhum -- so aparece no cliente, um dialogo por modelo, e trava
    # quem tiver personagem salvo no mapa. Custou uma rodada; nao custa de novo.
    tabela = Grf(caminho_grf).entries
    faltando = sorted(set(m.rsm for m in r.modelos
                          if (PREFIXO_MODELO + m.rsm) not in tabela))
    if faltando:
        print 'ABORTADO: %d modelos nao resolvem no GRF:' % len(faltando)
        for f in faltando[:5]:
            print '  %s' % texto(f)
        return 2

    open(os.path.join(sai, mapa + '.rsw'), 'wb').write(r.to_bytes())
    conf = Rsw(open(os.path.join(sai, mapa + '.rsw'), 'rb').read())
    ok, msg = conf.verificar()
    relatorio.append(u'  objetos %d -> %d, reabre: %s'
                     % (antes, len(conf.objetos), msg))
    relatorio.append(u'  %d modelos conferidos contra o GRF: todos resolvem'
                     % len(conf.modelos))
    print u'\n'.join(relatorio).encode('utf-8')
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
