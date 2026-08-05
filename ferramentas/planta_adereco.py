# -*- coding: utf-8 -*-
u"""Copia um adereço de um mapa para outro, na coordenada que se pedir.

Python 2.7, como o resto de ferramentas/.

Por que existe, se já há o `edita_mapa.py`: aquele é a frente de **destruição**,
tem semente, fração e sorteio, e **recusa rodar em Prontera** por decisão de
ficção. Este aqui é outra coisa -- pôr uma peça específica num lugar específico,
em qualquer mapa, sem tocar em mais nada. Misturar os dois faria a receita de
destruição carregar exceção para Prontera, que é exatamente o que aquele guarda
existe para impedir.

**A peça não é desenhada, é copiada.** A receita não diz "planta o .rsm tal com
rotação tal": diz "vai em `moc_ruins 112,127`, pega o que estiver lá com este
nome de `.rsm`, e põe igual em `prontera 168,199`". Assim rotação, escala,
espelhamento, tipo de animação e o **nodename** vêm do original em vez de serem
chutados -- e um adereço montado de duas metades espelhadas (que é o caso da
tenda do bazar) chega inteiro, com o afastamento entre as metades preservado.

Três coisas que a cópia preserva e que um "planta o .rsm" perderia:

- **a altura relativa ao chão.** A tenda está a `y=-2.5` num chão de `-4.0`, ou
  seja 1,5 afundada de propósito. O que se copia é o **afastamento**, não o `y`
  absoluto -- o chão de Prontera é `+1.0` e a tenda vai para `+2.5`.
- **a escala negativa.** Uma das duas metades tem `escala.x = -0.8`: é a outra
  espelhada. Copiar `1.0` entregaria duas metades iguais, viradas para o mesmo
  lado.
- **o `nodename`** (aqui `RC_sr005`). O `Modelo.novo` do `rsw.py` deixa esse
  campo vazio e o próprio comentário dele avisa que isso é **não verificado**.
  Copiando, a dúvida não se aplica.

O mapa de origem sai do GRF do bRO e não do nosso, por um motivo de ferramenta e
não de conteúdo: no nosso `data.grf` o `moc_ruins.rsw` está com a flag DES, que o
`grf.py` não lê (o de Prontera não está). Os dois arquivos têm o mesmo tamanho.

Nada aqui atravessa a fronteira do servidor: `.rsw` é só do cliente. **O adereço
não bloqueia passagem** -- quem manda em colisão é o `.gat`, que este script não
toca, então o jogador atravessa a tenda. Fechar a passagem seria mexer no `.gat`,
que o servidor também lê, e é decisão de outra ordem.

Uso:
    python planta_adereco.py <nosso-data.grf> <pasta-saida> [mapa] [grf-origem]

A saída se instala copiando para `C:\\GuerraDoEmperium\\cliente\\data\\`, onde o
`DataFolderFirst` a faz vencer o GRF. **Apagar o arquivo reverte**, porque o
original nunca saiu do GRF.
"""

import os
import struct
import sys

from gat import Gat
from grf import Grf
from rsw import Modelo, Rsw


GRF_BRO_PADRAO = (u'C:\\Program Files (x86)\\Gravity Interactive, Inc'
                  u'\\Ragnarok Brazil\\data.grf')

# A tenda do bazar de Morroc. Duas metades espelhadas, e o ponto 112,127 que o
# pedido cita cai no meio das duas -- por isso o raio de 4 células apanha as
# duas e nenhuma terceira.
TENDA_BAZAR = u'\ub77c\ud5ec\\\uc0c1\uc810\ucc9c\ub9c902.rsm'   # 라헬\상점천막02

# A receita de Prontera esta VAZIA de proposito, e a linha comentada abaixo e
# um registro, nao um rascunho: a tenda foi plantada em 2026-08-04 e **tirada
# no mesmo dia**, por decisao do dono do projeto -- nao ficou boa na praca. O
# override foi apagado de `cliente\data\prontera.rsw`, o que devolve o mapa do
# GRF.
#
# Descomentar replanta a tenda. Nao e um TODO.
RECEITA = {
    'prontera': [
        # {
        #     'o_que': u'tenda do bazar de Morroc',
        #     'etiqueta': 'tenda',
        #     'origem': ('moc_ruins', 112, 127, TENDA_BAZAR, 4),
        #     'destino': (168, 199),
        # },
    ],
}


def cp949(u):
    return u.encode('cp949')


def celula(g, m):
    u"""A coordenada de jogo de um modelo, em fração de célula."""
    return (m.pos[0] / 5.0 + g.largura / 2.0,
            m.pos[2] / 5.0 + g.altura / 2.0)


def mundo(g, cx, cy):
    return ((cx - g.largura / 2.0) * 5.0 + 2.5,
            (cy - g.altura / 2.0) * 5.0 + 2.5)


def le_mapa(grf, mapa):
    r = Rsw(grf.read(u'data\\%s.rsw' % mapa))
    ok, msg = r.verificar()
    if not ok:
        raise Exception('rsw de %s nao passou: %s' % (mapa, msg))
    g = Gat(grf.read(u'data\\%s.gat' % mapa))
    return r, g


def recorta(r, g, cx, cy, alvo, raio):
    u"""As instâncias de `alvo` dentro de `raio` células de (cx, cy)."""
    achados = []
    for m in r.modelos:
        if m.rsm != cp949(alvo).lower():
            continue
        mx, my = celula(g, m)
        if abs(mx - cx) <= raio and abs(my - cy) <= raio:
            achados.append((m, mx, my))
    return achados


def planta(destino_rsw, destino_gat, grupo, org_gat, cx, cy, etiqueta):
    u"""Copia `grupo` para (cx, cy) do mapa de destino, preservando a forma.

    O grupo é reposicionado pelo seu **centro**: cada peça guarda o afastamento
    que tinha em relação ao centro do grupo original, e o grupo inteiro é
    transladado. Rotação não é recalculada -- girar o conjunto exigiria girar
    também cada `rot.y`, e o pedido é "a mesma tenda", não "a tenda virada".
    """
    cxs = [mx for _, mx, _ in grupo]
    cys = [my for _, _, my in grupo]
    ccx = sum(cxs) / float(len(cxs))
    ccy = sum(cys) / float(len(cys))

    wx, wz = mundo(destino_gat, cx, cy)
    chao_destino = destino_gat.altura_media(cx, cy)

    relatorio = []
    for i, (m, mx, my) in enumerate(grupo):
        chao_origem = org_gat.altura_media(int(round(mx)), int(round(my)))
        dy = m.pos[1] - chao_origem

        novo = Modelo(m.to_bytes(), 0)   # cópia independente, byte a byte
        novo.nome = ('guerra_%s_%02d' % (etiqueta, i)).ljust(40, '\x00')
        novo.pos = [wx + (mx - ccx) * 5.0,
                    chao_destino + dy,
                    wz + (my - ccy) * 5.0]
        destino_rsw.objetos.append(novo)
        relatorio.append(u'    peça %d: jogo(%.1f,%.1f) y=%.2f (chão %.2f %+.2f)'
                         u'  esc(%.2f,%.2f,%.2f)'
                         % (i,
                            novo.pos[0] / 5.0 + destino_gat.largura / 2.0,
                            novo.pos[2] / 5.0 + destino_gat.altura / 2.0,
                            novo.pos[1], chao_destino, dy,
                            novo.escala[0], novo.escala[1], novo.escala[2]))
    return relatorio


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1
    caminho_grf = sys.argv[1]
    saida = sys.argv[2]
    mapa = sys.argv[3] if len(sys.argv) > 3 else 'prontera'
    grf_origem = sys.argv[4] if len(sys.argv) > 4 else GRF_BRO_PADRAO

    if mapa not in RECEITA:
        print 'sem receita para %s' % mapa
        return 1
    if not os.path.isdir(saida):
        os.makedirs(saida)

    nosso = Grf(caminho_grf)
    outro = Grf(grf_origem)

    destino_rsw, destino_gat = le_mapa(nosso, mapa)
    antes = len(destino_rsw.objetos)

    cache = {}
    linhas = []
    for item in RECEITA[mapa]:
        org_mapa, ocx, ocy, alvo, raio = item['origem']
        dcx, dcy = item['destino']

        # Todo .rsm citado tem de existir no NOSSO GRF -- caminho errado nao da
        # erro em parser nenhum, so aparece no cliente, um dialogo por modelo,
        # e trava quem tiver personagem salvo no mapa.
        chave = cp949(u'data\\model\\' + alvo).lower()
        if chave not in nosso.entries:
            print 'ABORTADO: %s nao existe no nosso GRF' % alvo.encode('utf-8')
            return 2

        if org_mapa not in cache:
            cache[org_mapa] = le_mapa(outro, org_mapa)
        org_rsw, org_gat = cache[org_mapa]

        grupo = recorta(org_rsw, org_gat, ocx, ocy, alvo, raio)
        if not grupo:
            print ('ABORTADO: nada em %s %d,%d (raio %d) com o nome %s'
                   % (org_mapa, ocx, ocy, raio, alvo.encode('utf-8')))
            return 2

        etiqueta = item.get('etiqueta', 'adereco')
        linhas.append(u'  %s: %d peça(s) de %s %d,%d -> %s %d,%d'
                      % (item['o_que'], len(grupo), org_mapa, ocx, ocy,
                         mapa, dcx, dcy))
        linhas += planta(destino_rsw, destino_gat, grupo, org_gat,
                         dcx, dcy, etiqueta)

    # O `verificar()` do rsw.py compara contra os bytes de ENTRADA, entao so
    # vale antes de mexer -- o `le_mapa` ja o rodou. Depois de mexer, a prova
    # possivel e outra: reabrir a saida e conferir que ela parseia inteira, com
    # a contagem de objetos que se espera e a quadtree fechando no byte exato.
    bytes_saida = destino_rsw.to_bytes()
    relido = Rsw(bytes_saida)
    if len(relido.objetos) != len(destino_rsw.objetos):
        print ('ABORTADO: a saida reabriu com %d objetos, esperado %d'
               % (len(relido.objetos), len(destino_rsw.objetos)))
        return 2
    if len(relido.quadtree) != Rsw.QUADTREE:
        print 'ABORTADO: quadtree da saida tem %d bytes' % len(relido.quadtree)
        return 2

    alvo_arq = os.path.join(saida, mapa + '.rsw')
    with open(alvo_arq, 'wb') as f:
        f.write(bytes_saida)

    print u'\n'.join(linhas).encode('utf-8')
    print
    print '%s: %d -> %d objetos' % (mapa, antes, len(destino_rsw.objetos))
    print 'gravado em %s' % alvo_arq
    print
    print 'instalar: copiar para C:\\GuerraDoEmperium\\cliente\\data\\'
    return 0


if __name__ == '__main__':
    sys.exit(main())
