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
    'auction_01': {
        'substituir': [],
        'acrescentar': [
            (FONTE, 179.5, 71.5, 0.0, 0.57),
            (ESCRIVANINHA, 191.5, 71.5, 90.0, 1.0),
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
