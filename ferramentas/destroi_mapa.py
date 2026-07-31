# -*- coding: utf-8 -*-
"""Aplica a temática de destruição num mapa: gera .rsw e .gnd modificados.

Python 2.7, como o resto de ferramentas/.

A ficção: um meteoro caiu no mar e a onda matou o resto. Isso muda o que se
desenha -- nao ha cratera nem escombro projetado. O que a agua faz e **tombar,
afundar e varrer**: construcao inclinada e meio soterrada no limo, adereco leve
levado embora, chao encardido de lama seca. Prontera fica intacta de proposito
(e o centro da sobrevivencia, ja restaurada), entao nunca rode isto nela.

Restricao de projeto: **nao onerar memoria.** Por isso, aqui,
  - nenhum modelo novo entra no mapa. Os destrocos sao clones de modelos que o
    mapa ja carrega, entao o cliente nao abre um .rsm nem uma textura a mais;
  - o chao suja por cor de superficie, nao por textura nova;
  - varre-se mais adereco do que se cria destroco, entao a contagem de objetos
    **cai**.

Uso:
    python destroi_mapa.py <pasta-de-entrada> <pasta-de-saida> [mapa]

Reversao: os arquivos gerados sao overrides soltos em cliente\\data\\. Apagar o
arquivo devolve a versao original, que nunca saiu do GRF. Nao existe backup a
manter.
"""

import copy
import math
import os
import random
import sys

from gnd import Gnd
from rsw import Rsw, Modelo, texto


# -- a receita ------------------------------------------------------------

SEMENTE = 20260731   # fixa: rodar duas vezes da o mesmo mapa

# Luz: o ceu virou cinza de poeira. Difusa cai e perde o azul (o original puxa
# para o frio, 0.99/0.97/1.00); ambiente sobe um tico para o sol sumido nao
# fechar as sombras em preto; sombra fica mais fraca porque dia encoberto nao
# projeta contorno duro.
LUZ_DIFUSA = [0.62, 0.60, 0.57]
LUZ_AMBIENTE = [0.34, 0.32, 0.29]
LUZ_OPACIDADE_SOMBRA = 0.35

# Chao: escurece tudo e derruba o azul mais que o vermelho -- o olho le
# deslocamento para o terra como lama seca. O piso evita que o que ja era
# escuro vire preto chapado e apague o relevo.
CHAO_ESCALA = (0.74, 0.68, 0.55)   # R, G, B
CHAO_PISO = 28

# Construcoes. "arrasada" leva tombo forte e afunda fundo -- le como desabada e
# meio soterrada. "avariada" leva so o suficiente para o prumo sumir, que e o
# que da a leitura de rachadura/recalque sem precisar de arte nova.
ARRASADAS = 0.55        # fracao das construcoes que leva o tratamento pesado
TOMBO_ARRASADA = (11.0, 24.0)   # graus
TOMBO_AVARIADA = (2.5, 7.0)
AFUNDA_ARRASADA = (6.0, 14.0)   # unidades; +y afunda, o eixo de RO aponta para baixo
AFUNDA_AVARIADA = (1.0, 3.5)

CONSTRUCOES = [
    u'프론테라\\상점01.rsm', u'프론테라\\상점03.rsm',
    u'프론테라\\상점04.rsm', u'프론테라\\상점05.rsm',
    u'프론테라\\검사길드.rsm', u'프론테라\\무기점.rsm',
    u'izlude\\iz_academy.rsm', u'izlude\\iz_smelter.rsm',
    u'izlude\\iz_enchant.rsm', u'izlude\\iz_fruitshop.rsm',
]

# Adereco leve: a onda levou. Fracao removida por modelo.
VARRIDOS = 0.7
LEVES = [
    u'나무잡초꽃\\화분01.rsm', u'나무잡초꽃\\화분02.rsm',
    u'malaya\\꽃04.rsm', u'malaya\\꽃05.rsm',
    u'izlude\\iz_flower01.rsm', u'izlude\\iz_flower02.rsm',
    u'외부소품\\벤치01.rsm',
    u'izlude\\iz_sale01.rsm', u'izlude\\iz_sale02.rsm',
    u'izlude\\iz_breads01.rsm', u'izlude\\iz_breads02.rsm',
    u'izlude\\iz_fish01.rsm', u'izlude\\iz_fish02.rsm',
    u'izlude\\iz_fish03.rsm',
    u'내부소품\\간판1.rsm', u'내부소품\\간판2.rsm',
    u'휘겔\\휘겔_노점과일상자01.rsm', u'휘겔\\휘겔_노점과일상자02.rsm',
    u'휘겔\\휘겔_노점빵상자01.rsm',
]

# Destrocos: SO modelos que o mapa ja carrega. Barril e caixote tombados de
# lado leem como coisa que a agua arrastou e largou.
DESTROCOS = [
    u'내부소품\\드럼통1.rsm', u'내부소품\\드럼통2.rsm',
    u'내부소품\\나무상자01.rsm', u'내부소품\\나무상자02.rsm',
    u'내부소품\\양동이1.rsm', u'내부소품\\술통01.rsm',
    # NAO por 나무잡초꽃\나무기둥01.rsm aqui. Traduzido ao pe da letra da
    # "pilar de madeira", mas a pasta 나무잡초꽃 e "arvore/erva/flor" -- e a
    # pasta de vegetacao, e o modelo e TRONCO DE ARVORE, enorme. Deitado a 90
    # graus virou tora gigante espalhada pela cidade. Confirmado in-game em
    # 2026-07-31. A pasta manda mais que o nome do arquivo.
]
DESTROCOS_POR_CONSTRUCAO = 3
DESTROCO_RAIO = 22.0


def cp949(u):
    return u.encode('cp949')


def _campo(valor, tamanho):
    return valor + '\x00' * (tamanho - len(valor))


def destroi_rsw(r, rnd, relatorio):
    r.luz_difusa = list(LUZ_DIFUSA)
    r.luz_ambiente = list(LUZ_AMBIENTE)
    r.luz_opacidade_sombra = LUZ_OPACIDADE_SOMBRA

    construcoes = set(cp949(n).lower() for n in CONSTRUCOES)
    leves = set(cp949(n).lower() for n in LEVES)
    destrocos = [cp949(n).lower() for n in DESTROCOS]

    # Um molde por modelo de destroco, tirado do proprio mapa. Se um deles nao
    # estiver no mapa, nao inventamos: seria carregar .rsm novo.
    moldes = {}
    for m in r.modelos:
        if m.rsm in destrocos and m.rsm not in moldes:
            moldes[m.rsm] = m
    faltando = [d for d in destrocos if d not in moldes]
    for d in faltando:
        relatorio.append('  aviso: %s nao esta no mapa, ignorado como destroco'
                         % texto(d))
    moldes = list(moldes.values())

    alvos = []
    novos = []
    arrasadas = avariadas = varridos = 0

    for obj in r.objetos:
        if not isinstance(obj, Modelo):
            novos.append(obj)
            continue

        if obj.rsm in leves:
            if rnd.random() < VARRIDOS:
                varridos += 1
                continue
            novos.append(obj)
            continue

        if obj.rsm in construcoes:
            pesada = rnd.random() < ARRASADAS
            tombo = TOMBO_ARRASADA if pesada else TOMBO_AVARIADA
            afunda = AFUNDA_ARRASADA if pesada else AFUNDA_AVARIADA
            # Tombo repartido entre os dois eixos horizontais, com sinal
            # sorteado, para nao sair tudo caindo para o mesmo lado.
            grau = rnd.uniform(*tombo)
            direcao = rnd.uniform(0, 2 * math.pi)
            obj.rot[0] += grau * math.cos(direcao)
            obj.rot[2] += grau * math.sin(direcao)
            obj.pos[1] += rnd.uniform(*afunda)
            if pesada:
                arrasadas += 1
            else:
                avariadas += 1
            alvos.append(obj)

        novos.append(obj)

    # Destrocos ao redor do que caiu.
    criados = 0
    if moldes:
        for alvo in alvos:
            for _ in range(DESTROCOS_POR_CONSTRUCAO):
                d = copy.deepcopy(rnd.choice(moldes))
                ang = rnd.uniform(0, 2 * math.pi)
                raio = rnd.uniform(DESTROCO_RAIO * 0.35, DESTROCO_RAIO)
                d.pos[0] = alvo.pos[0] + raio * math.cos(ang)
                d.pos[2] = alvo.pos[2] + raio * math.sin(ang)
                d.pos[1] = alvo.pos[1] + rnd.uniform(-1.0, 1.5)
                # Deitado: 90 graus num eixo horizontal, com guinada livre.
                d.rot[0] = rnd.uniform(72.0, 108.0)
                d.rot[1] = rnd.uniform(0.0, 360.0)
                d.rot[2] = rnd.uniform(-18.0, 18.0)
                d.nome = _campo('guerra_destroco_%03d' % criados, 40)
                novos.append(d)
                criados += 1

    r.objetos = novos
    relatorio.append('  luz          difusa -> %.2f/%.2f/%.2f, ambiente -> '
                     '%.2f/%.2f/%.2f, sombra -> %.2f'
                     % tuple(LUZ_DIFUSA + LUZ_AMBIENTE +
                             [LUZ_OPACIDADE_SOMBRA]))
    relatorio.append('  construcoes  %d arrasadas, %d avariadas'
                     % (arrasadas, avariadas))
    relatorio.append('  adereco      %d varridos pela onda' % varridos)
    relatorio.append('  destrocos    %d clones de %d modelos que o mapa ja '
                     'carregava' % (criados, len(moldes)))
    return criados - varridos


def destroi_gnd(g, relatorio):
    mudadas = g.encardir(CHAO_ESCALA, CHAO_PISO)
    relatorio.append('  chao         %d de %d superficies encardidas '
                     '(escala %.2f/%.2f/%.2f, piso %d)'
                     % ((mudadas, len(g.superficies)) + CHAO_ESCALA +
                        (CHAO_PISO,)))


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1
    entrada, saida = sys.argv[1], sys.argv[2]
    mapa = sys.argv[3] if len(sys.argv) > 3 else 'izlude'

    if mapa.lower().startswith('prontera'):
        print 'recusado: Prontera fica intacta por decisao de ficcao.'
        return 3

    if not os.path.isdir(saida):
        os.makedirs(saida)

    rnd = random.Random(SEMENTE)
    relatorio = ['%s:' % mapa]

    cru_rsw = open(os.path.join(entrada, mapa + '.rsw'), 'rb').read()
    r = Rsw(cru_rsw)
    ok, msg = r.verificar()
    if not ok:
        print 'rsw nao passou na verificacao: %s' % msg
        return 2
    antes = len(r.objetos)
    delta = destroi_rsw(r, rnd, relatorio)
    open(os.path.join(saida, mapa + '.rsw'), 'wb').write(r.to_bytes())

    cru_gnd = open(os.path.join(entrada, mapa + '.gnd'), 'rb').read()
    g = Gnd(cru_gnd)
    ok, msg = g.verificar()
    if not ok:
        print 'gnd nao passou na verificacao: %s' % msg
        return 2
    destroi_gnd(g, relatorio)
    open(os.path.join(saida, mapa + '.gnd'), 'wb').write(g.to_bytes())

    relatorio.append('  objetos      %d -> %d (%+d)'
                     % (antes, len(r.objetos), len(r.objetos) - antes))
    print '\n'.join(relatorio)
    return 0


if __name__ == '__main__':
    sys.exit(main())
