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

RECEITA = {
    'izlude': {
        'substituir': [
            # (o que trocar, por quais, fração das instâncias)
            (ARVORES, [OSSADA_02, ESPINHEIRO, OSSADA_04], 1.00),
            ([MURO], [PAREDE_RUINA], 0.30),
        ],
        'acrescentar': [
            # (modelo, célula x, célula y) -- a altura sai do .gat
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
    for arquivo, cx, cy in receita.get('acrescentar', []):
        wx, wz = mundo(g, cx, cy)
        m = Modelo.novo(cp949(arquivo), 'guerra_add_%03d' % criados,
                        (wx, g.altura_media(cx, cy), wz))
        m.rot[1] = rnd.uniform(0.0, 360.0)
        r.objetos.append(m)
        criados += 1
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
