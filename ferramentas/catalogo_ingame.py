# -*- coding: utf-8 -*-
"""Monta o mapa-catalogo: um modelo de cada, in-game, etiquetado por NPC.

Python 2.7, como o resto de ferramentas/.

O problema que ele resolve: os modelos do RO tem nome em coreano, quem escreve a
receita nao consegue ver o jogo, e traduzir o nome do arquivo **da errado** (ver
o tronco de arvore em ../CUSTOMIZACAO-VISUAL.md). Screenshot resolve um caso por
vez; catalogo em markdown depende de adivinhar. Este script poe **um exemplar de
cada modelo, de pe, em fila, com uma placa numerada do lado** -- uma volta a pe
resolve o mapa inteiro de uma vez.

Como funciona:

1. Le o `.rsw` do mapa base, **apaga a lista de objetos inteira** e poe no lugar
   um exemplar de cada modelo distinto do mapa de origem. Como tudo e
   substituido, o entulho do mapa base nao atrapalha.
2. Le o `.gat` do mapa base para so posicionar em celula andavel -- o catalogo
   nao serve se voce nao chega perto.
3. Gera o script de NPC que planta uma placa ao lado de cada modelo, com o
   numero e o nome. O numero casa com o do markdown.
4. Gera o markdown com coordenada de cada um, para dar `@warp` direto.

A conversao entre coordenada do jogo e coordenada de mundo do `.rsw` foi
**medida**, nao suposta (a correlacao entre a altura do terreno sob cada modelo
de Izlude e o `y` do proprio modelo so aparece com o sinal certo de z):

    mundo_x = (celula_x - largura_gat/2) * 5 + 2.5
    mundo_z = (celula_y - altura_gat/2)  * 5 + 2.5
    mundo_y = altura do .gat na celula (mesmo sinal, eixo para baixo)

Uso:
    python catalogo_ingame.py <pasta-com-os-arquivos> <pasta-de-saida>
"""

import io
import os
import sys

from gat import Gat
from rsw import Rsw, Modelo, texto
from catalogo_mapa import PASTAS, NOMES


MAPA_BASE = 'x_prt'      # 140x140 celulas, 59% andavel, altura constante 0,
                         # no map_index e sem nenhum spawn de monstro
MAPA_ORIGEM = 'izlude'   # de onde sai a lista de modelos a catalogar

PASSO = 9          # celulas entre um modelo e o seguinte (45 unidades)
MARGEM = 8         # celulas de folga na borda do mapa
FOLGA = 1          # a celula e a vizinhanca precisam ser andaveis
PLACA_A_FRENTE = 3   # celulas ao sul do modelo, para a placa nao ficar dentro dele

# Luz neutra e clara: catalogo e para identificar modelo, nao para ambientar.
LUZ_DIFUSA = [1.0, 1.0, 1.0]
LUZ_AMBIENTE = [0.62, 0.62, 0.62]
LUZ_SOMBRA = 0.20

SPRITE_PLACA = '4_BOARD3'
LIMITE_NOME_NPC = 23   # NAME_LENGTH do rAthena e 24 com o terminador


def rotulo(u):
    """Nome curto e legivel para a placa e para a tabela."""
    if u'\\' in u:
        pasta, arq = u.rsplit(u'\\', 1)
    else:
        pasta, arq = u'', u
    stem = arq[:-4] if arq.lower().endswith(u'.rsm') else arq
    return pasta, stem, NOMES.get(stem, u'')


def sem_acento(u):
    """O cliente esta em langtype 0 e nunca testamos acento vindo do servidor.

    Ver PENDENCIAS.md, "Acentuacao no dialogo". Ate haver teste, placa sai sem
    acento -- e o custo baixo, e nome de NPC quebrado e pior que nome sem til.
    """
    tabela = {u'á': u'a', u'à': u'a', u'ã': u'a', u'â': u'a', u'é': u'e',
              u'ê': u'e', u'í': u'i', u'ó': u'o', u'ô': u'o', u'õ': u'o',
              u'ú': u'u', u'ç': u'c', u'Á': u'A', u'Ã': u'A', u'É': u'E',
              u'Ç': u'C', u'Ó': u'O', u'ª': u'a', u'º': u'o'}
    u = u''.join(tabela.get(c, c) for c in u)
    # Rede de seguranca: o que a tabela nao previu (e ela ja deixou passar um
    # 'a ordinal') sai fora em vez de virar byte alto num arquivo que o rAthena
    # le como Latin-1.
    return u''.join(c if ord(c) < 128 else u'_' for c in u)


def vagas(g):
    """Celulas em grade onde da para plantar um modelo e chegar perto."""
    saida = []
    for cy in range(MARGEM, g.altura - MARGEM, PASSO):
        for cx in range(MARGEM, g.largura - MARGEM, PASSO):
            ok = True
            for y in range(cy - FOLGA, cy + FOLGA + 1):
                for x in range(cx - FOLGA, cx + FOLGA + 1):
                    if not g.andavel(x, y):
                        ok = False
                        break
                if not ok:
                    break
            # a placa tambem precisa de chao
            if ok and not g.andavel(cx, cy - PLACA_A_FRENTE):
                ok = False
            if ok:
                saida.append((cx, cy))
    return saida


def mundo(g, cx, cy):
    return ((cx - g.largura / 2.0) * 5.0 + 2.5,
            (cy - g.altura / 2.0) * 5.0 + 2.5)


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1
    ent, sai = sys.argv[1], sys.argv[2]
    if not os.path.isdir(sai):
        os.makedirs(sai)

    base = Rsw(open(os.path.join(ent, MAPA_BASE + '.rsw'), 'rb').read())
    ok, msg = base.verificar()
    if not ok:
        print 'rsw base nao passou: %s' % msg
        return 2
    g = Gat(open(os.path.join(ent, MAPA_BASE + '.gat'), 'rb').read())

    origem = Rsw(open(os.path.join(ent, MAPA_ORIGEM + '.rsw'), 'rb').read())
    ok, msg = origem.verificar()
    if not ok:
        print 'rsw de origem nao passou: %s' % msg
        return 2

    # Um exemplar de cada modelo, na ordem em que o mapa de origem mais os usa.
    porrsm = {}
    for m in origem.modelos:
        porrsm.setdefault(m.rsm, []).append(m)
    ordem = sorted(porrsm, key=lambda n: -len(porrsm[n]))

    livres = vagas(g)
    print 'mapa base %s: %d vagas para %d modelos' % (MAPA_BASE, len(livres),
                                                      len(ordem))
    if len(livres) < len(ordem):
        print ('AVISO: faltam %d vagas -- os ultimos ficam de fora'
               % (len(ordem) - len(livres)))

    base.luz_difusa = list(LUZ_DIFUSA)
    base.luz_ambiente = list(LUZ_AMBIENTE)
    base.luz_opacidade_sombra = LUZ_SOMBRA
    base.objetos = []

    npcs = []
    linhas_md = []
    for i, nome in enumerate(ordem, 1):
        if i > len(livres):
            break
        cx, cy = livres[i - 1]
        wx, wz = mundo(g, cx, cy)

        # Clonar o exemplar preserva a escala com que o mapa de origem o usa --
        # o que importa, porque tamanho errado foi metade do problema do tronco.
        exemplar = porrsm[nome][0]
        m = Modelo(exemplar.to_bytes(), 0)
        m.pos = [wx, g.altura_media(cx, cy), wz]
        m.rot = [0.0, 0.0, 0.0]
        m.nome = ('catalogo_%03d' % i).ljust(40, '\x00')
        base.objetos.append(m)

        u = nome.decode('cp949')
        pasta, stem, trad = rotulo(u)
        curto = sem_acento(trad or stem)
        etiqueta = (u'%02d %s' % (i, curto))[:LIMITE_NOME_NPC]
        npcs.append((MAPA_BASE, cx, cy - PLACA_A_FRENTE, etiqueta, i, u))
        linhas_md.append(
            u'| %d | `%s` | %s | %s | %d,%d |'
            % (i, stem, (PASTAS.get(pasta, pasta) if pasta else u'—'),
               trad or u'?', cx, cy))

    saida_rsw = os.path.join(sai, MAPA_BASE + '.rsw')
    open(saida_rsw, 'wb').write(base.to_bytes())
    conf = Rsw(open(saida_rsw, 'rb').read())
    ok, msg = conf.verificar()
    print 'gravado %s (%d objetos), reabre: %s' % (saida_rsw,
                                                   len(conf.objetos), msg)

    # -- script de NPC --------------------------------------------------
    s = [u'// ' + u'-' * 62,
         u'// -            Guerra do Emperium - mapa-catalogo             -',
         u'// ' + u'-' * 62,
         u'//',
         u'// GERADO por ferramentas/catalogo_ingame.py. Nao editar a mao:',
         u'// rodar o script de novo e a forma de atualizar.',
         u'//',
         u'// Uma placa por modelo do mapa-catalogo, com o numero que casa com',
         u'// o CATALOGO-IZLUDE-INGAME.md. Serve para conferir o que cada',
         u'// modelo E de verdade, dado que o nome em coreano engana.',
         u'//',
         u'// Ferramenta de trabalho, nao conteudo de jogo: manter desligado',
         u'// no scripts_guerra.conf quando nao estiver em uso.',
         u'//',
         u'// @warp %s <x> <y> vai direto a um modelo -- as coordenadas estao' % MAPA_BASE,
         u'// no markdown.',
         u'']
    for mapa, x, y, etiqueta, i, u in npcs:
        s.append(u'%s,%d,%d,4\tscript\t%s\t%s,{ end; }'
                 % (mapa, x, y, etiqueta, SPRITE_PLACA))
    caminho_npc = os.path.join(sai, 'catalogo_visual.txt')
    with io.open(caminho_npc, 'w', encoding='utf-8') as f:
        f.write(u'\n'.join(s) + u'\n')
    print 'gravado %s (%d placas)' % (caminho_npc, len(npcs))

    # -- markdown -------------------------------------------------------
    md = [u'# Mapa-catálogo de modelos — `%s`' % MAPA_BASE,
          u'',
          u'Gerado por `ferramentas/catalogo_ingame.py`. Um exemplar de cada '
          u'modelo de **%s**, de pé, com uma placa numerada ao lado.' % MAPA_ORIGEM,
          u'',
          u'**Como usar:** `@warp %s` e ande pela grade, ou `@warp %s <x> <y>` '
          u'para cair ao lado de um modelo específico. O número da placa é o '
          u'número desta tabela.' % (MAPA_BASE, MAPA_BASE),
          u'',
          u'O mapa base teve **todos os objetos originais removidos** — o que '
          u'estiver lá é do catálogo. A luz é neutra de propósito.',
          u'',
          u'| # | modelo | pasta | tradução literal | `@warp` |',
          u'|---|---|---|---|---|']
    md.extend(linhas_md)
    caminho_md = os.path.join(sai, 'CATALOGO-INGAME.md')
    with io.open(caminho_md, 'w', encoding='utf-8') as f:
        f.write(u'\n'.join(md) + u'\n')
    print 'gravado %s' % caminho_md
    return 0


if __name__ == '__main__':
    sys.exit(main())
