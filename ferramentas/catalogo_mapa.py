# -*- coding: utf-8 -*-
"""Gera o catalogo traduzido dos modelos de um mapa, para conferencia humana.

Python 2.7, como o resto de ferramentas/.

Por que existe: os modelos do RO tem nome em coreano, e classificar pelo nome do
arquivo **da errado**. O caso que originou este script: eu li
`나무잡초꽃\\나무기둥01.rsm` como "pilar de madeira" e usei como destroco de
construcao. So que a pasta `나무잡초꽃` e "arvore / erva / flor" -- a pasta de
vegetacao -- e o modelo e tronco de arvore, enorme. Deitado a 90 graus virou
tora gigante espalhada pela cidade.

A licao: **a pasta manda mais que o nome do arquivo.** Por isso o catalogo
sempre mostra as duas traduzidas, lado a lado.

Este arquivo nao decide nada -- ele produz a tabela que uma pessoa que consegue
VER o jogo confere e corrige. A coluna "o que e de verdade" nasce vazia de
proposito: e onde a correcao entra.

Uso:
    python catalogo_mapa.py <mapa.rsw> <saida.md>
"""

import io
import os
import sys

from rsw import Rsw, texto
import destroi_mapa as receita


# Pastas. Esta e a parte que mais importa acertar: ela categoriza sozinha.
PASTAS = {
    u'나무잡초꽃': u'VEGETAÇÃO (árvore/erva/flor)',
    u'내부소품': u'adereço de interior',
    u'외부소품': u'adereço de exterior',
    u'프론테라': u'Prontera',
    u'리히타르젠': u'Lighthalzen',
    u'사막도시': u'cidade do deserto (Morroc)',
    u'아요타야': u'Ayothaya',
    u'아인브로크': u'Einbroch',
    u'알베르타': u'Alberta',
    u'라헬': u'Rachel',
    u'휘겔': u'Hugel',
    u'크리스마스마을': u'vila de Natal (Lutie)',
    u'중국': u'China (Louyang)',
    u'지하감옥': u'masmorra',
    u'주가': u'Zhu (China)',
    u'몬스터': u'monstro',
    u'유저인터페이스': u'interface',
    u'필드바닥': u'textura de chão',
}

# Nomes de modelo. Traducao ao pe da letra -- e justamente por isso que ela
# sozinha nao basta.
NOMES = {
    u'바닥블럭': u'bloco de chão',
    u'시계탑벽': u'parede da torre do relógio',
    u'벤치01': u'banco', u'벤치': u'banco',
    u'덤불01': u'arbusto', u'덤불02': u'arbusto', u'덤불04': u'arbusto',
    u'나무01': u'árvore', u'나무02': u'árvore',
    u'휘장가로등': u'poste com estandarte',
    u'휘장': u'estandarte',
    u'나뭇잎01': u'folhagem',
    u'나무받침': u'base de árvore',
    u'화분01': u'vaso de planta', u'화분02': u'vaso de planta',
    u'가로등01': u'poste de luz',
    u'후문기둥': u'pilar do portão dos fundos',
    u'후문울타리': u'cerca do portão dos fundos',
    u'난간기둥': u'pilar de guarda-corpo',
    u'3차전직_기둥01': u'pilar (evento de 3ª classe)',
    u'나무상자01': u'caixote de madeira', u'나무상자02': u'caixote de madeira',
    u'드럼통1': u'tambor de metal', u'드럼통2': u'tambor de metal',
    u'술통01': u'barril de bebida',
    u'양동이1': u'balde',
    u'이즈루드다리': u'ponte de Izlude',
    u'우체통': u'caixa de correio',
    u'지하하수관': u'tubo de esgoto',
    u'동상받침대': u'pedestal de estátua',
    u'기사청동': u'bronze do quartel dos cavaleiros',
    u'나무받침대01': u'suporte de madeira',
    u'나무받침대07': u'suporte de madeira',
    u'나무받침대08': u'suporte de madeira',
    u'주전자': u'bule',
    u'실내등6': u'luminária interna',
    u'나무기둥01': u'TRONCO DE ÁRVORE', u'나무기둥02': u'TRONCO DE ÁRVORE',
    u'나무조각02': u'tora de madeira',
    u'나무다리01': u'ponte de madeira',
    u'넝쿨01': u'trepadeira',
    u'게시판': u'quadro de avisos',
    u'상점01': u'loja', u'상점03': u'loja',
    u'상점04': u'loja', u'상점05': u'loja',
    u'간판1': u'placa', u'간판2': u'placa',
    u'꽃04': u'flor', u'꽃05': u'flor',
    u'대기실무기장': u'suporte de armas',
    u'중국-무기장02': u'suporte de armas',
    u'긴의자': u'banco comprido',
    u'의자4': u'cadeira',
    u'동굴입구': u'entrada de caverna',
    u'유리컵1': u'copo de vidro',
    u'지하감옥_화로1': u'braseiro', u'화로': u'braseiro',
    u'다약화로01': u'braseiro',
    u'xmas_빵1': u'pão de Natal', u'xmas_빵2': u'pão de Natal',
    u'휘겔_노점과일상자01': u'caixa de frutas de banca',
    u'휘겔_노점과일상자02': u'caixa de frutas de banca',
    u'휘겔_노점빵상자01': u'caixa de pães de banca',
    u'퀴즈경기장': u'arena de quiz',
    u'프론아레나': u'arena de Prontera',
    u'검사길드': u'guilda dos espadachins',
    u'무기점': u'loja de armas',
    u'망치': u'martelo',
    u'도끼': u'machado',
    u'범선': u'veleiro',
    u'분수': u'fonte',
    u'비공정': u'aeronave',
    u'주가_대나무울타리01': u'cerca de bambu',
    u'주가_대나무울타리02': u'cerca de bambu',
    u'프론절벽': u'penhasco de Prontera',
    # Izlude ja nomeia em ingles -- traduzido so para a tabela nao ficar com
    # "?" onde nao ha duvida nenhuma.
    u'iz_academy': u'Academia', u'iz_smelter': u'fundição',
    u'iz_enchant': u'oficina de encantamento', u'iz_fruitshop': u'quitanda',
    u'iz_bridge01': u'ponte', u'iz_sale01': u'banca', u'iz_sale02': u'banca',
    u'iz_fish01': u'peixe', u'iz_fish02': u'peixe', u'iz_fish03': u'peixe',
    u'iz_breads01': u'pães', u'iz_breads02': u'pães',
    u'iz_flower01': u'flor', u'iz_flower02': u'flor',
}


# Morfemas coreanos que se repetem em nome de modelo. Servem para traduzir por
# COMPOSICAO o que nao esta no dicionario de nomes inteiros -- e o que torna
# possivel rotular os 7034 modelos do GRF sem enumerar um por um.
#
# Ressalva: morfema de uma silaba (성 castelo, 벽 parede, 문 porta) pode casar
# dentro de outra palavra. O casamento e sempre pelo mais longo primeiro, o que
# reduz o problema mas nao elimina. E rotulo de catalogo, nao verdade -- serve
# para saber para onde olhar.
MORFEMAS = {
    u'폐허': u'ruina', u'폐가': u'casa abandonada', u'민가': u'casa',
    u'깨진': u'quebrada', u'부서진': u'quebrado', u'부러진': u'partido',
    u'무너진': u'desmoronado', u'쓰러진': u'caido', u'낡은': u'velho',
    u'잔해': u'destroco', u'파편': u'fragmento', u'더미': u'monte',
    u'동물': u'animal', u'해골': u'cranio', u'무덤': u'tumulo',
    u'울타리': u'cerca', u'항아리': u'jarro', u'천막': u'toldo',
    u'모로코': u'morroc', u'사막': u'deserto', u'모래': u'areia',
    u'기둥': u'pilar', u'계단': u'escada', u'지붕': u'telhado',
    u'기와': u'telha', u'바닥': u'chao', u'창문': u'janela',
    u'상자': u'caixa', u'나무': u'madeira', u'바위': u'rocha',
    u'동상': u'estatua', u'분수': u'fonte', u'우물': u'poco',
    u'간판': u'placa', u'의자': u'cadeira', u'책상': u'mesa',
    u'침대': u'cama', u'다리': u'ponte', u'텐트': u'tenda',
    u'가옥': u'casa', u'조각': u'pedaco', u'그릇': u'vasilha',
    u'뼈': u'osso', u'묘': u'tumulo', u'성': u'castelo', u'벽': u'parede',
    u'문': u'porta', u'돌': u'pedra', u'집': u'casa', u'탑': u'torre',
    u'통': u'tonel', u'창': u'janela', u'헌': u'velho',
    # segunda leva, tirada dos '?' que sobraram na primeira rodada do
    # catalogo de ruina -- o proprio catalogo diz o que falta no dicionario
    u'마을': u'vila', u'입구': u'entrada', u'성당': u'catedral',
    u'탁자': u'mesa', u'운영청': u'adm', u'공장': u'fabrica',
    u'광석': u'minerio', u'밧줄': u'corda', u'기계': u'maquina',
    u'난간': u'guarda-corpo', u'지하': u'subterraneo', u'감옥': u'prisao',
    u'하수': u'esgoto', u'전장': u'campo de batalha', u'동굴': u'caverna',
    u'침몰': u'afundado', u'수레': u'carroca', u'사다리': u'escada de mao',
    u'횃불': u'tocha', u'철창': u'grade', u'가마': u'forno',
    # nomes de lugar, que aparecem como prefixo
    u'글래스트': u'glast', u'프론테라': u'prontera', u'페이욘': u'payon',
    u'게펜': u'geffen', u'알베르타': u'alberta', u'유노': u'juno',
    u'움발라': u'umbala', u'어비스': u'abismo', u'중국': u'china',
    u'니플헤임': u'niflheim', u'라헬': u'rachel',
}
_ORDEM_MORFEMAS = sorted(MORFEMAS, key=len, reverse=True)


def traduz_partes(stem):
    """Traduz um nome coreano por composicao de morfemas conhecidos.

    Devolve string vazia se nao reconheceu nada -- assim quem chama sabe que
    nao vale mostrar.
    """
    fichas = []
    ascii_buf = []
    reconheceu = False
    i = 0
    while i < len(stem):
        for k in _ORDEM_MORFEMAS:
            if stem.startswith(k, i):
                if ascii_buf:
                    fichas.append(u''.join(ascii_buf))
                    ascii_buf = []
                fichas.append(MORFEMAS[k])
                reconheceu = True
                i += len(k)
                break
        else:
            c = stem[i]
            if ord(c) < 128:
                ascii_buf.append(c)
            elif fichas and fichas[-1] != u'?':
                fichas.append(u'?')
            i += 1
    if ascii_buf:
        fichas.append(u''.join(ascii_buf))
    return u' '.join(f for f in fichas if f) if reconheceu else u''


def parte(u, tabela):
    return tabela.get(u) or traduz_partes(u)


def classificacao():
    """Como a receita atual trata cada modelo."""
    c = {}
    for n in receita.CONSTRUCOES:
        c[n.lower()] = u'CONSTRUÇÃO — tomba e afunda'
    for n in receita.LEVES:
        c[n.lower()] = u'LEVE — %d%% varridos' % int(receita.VARRIDOS * 100)
    for n in receita.DESTROCOS:
        c[n.lower()] = u'DESTROÇO — clonado e deitado'
    return c


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1

    r = Rsw(open(sys.argv[1], 'rb').read())
    ok, msg = r.verificar()
    if not ok:
        print 'rsw nao passou na verificacao: %s' % msg
        return 2

    como = classificacao()
    porrsm = {}
    for m in r.modelos:
        porrsm.setdefault(m.rsm, []).append(m)

    linhas = []
    linhas.append(u'# Catálogo de modelos — %s'
                  % os.path.basename(sys.argv[1]))
    linhas.append(u'')
    linhas.append(u'Gerado por `ferramentas/catalogo_mapa.py`. **A coluna '
                  u'"o que é de verdade" nasce vazia de propósito** — é onde '
                  u'entra a correção de quem consegue ver o jogo.')
    linhas.append(u'')
    linhas.append(u'A tradução é literal e por isso não é confiável sozinha. '
                  u'A pasta categoriza melhor que o nome do arquivo: foi '
                  u'ignorando isso que `나무기둥01` ("pilar de madeira", na '
                  u'pasta de **vegetação**) virou tora gigante deitada na '
                  u'cidade.')
    linhas.append(u'')
    linhas.append(u'`y` é a faixa de altura das instâncias. O eixo Y de RO '
                  u'aponta para baixo: valor menor é mais alto.')
    linhas.append(u'')
    linhas.append(u'| # | qtd | pasta | modelo | tradução literal | y | '
                  u'a receita faz | **o que é de verdade** |')
    linhas.append(u'|---|---|---|---|---|---|---|---|')

    ordem = sorted(porrsm, key=lambda n: -len(porrsm[n]))
    for i, nome in enumerate(ordem, 1):
        ms = porrsm[nome]
        u = nome.decode('cp949')
        if u'\\' in u:
            pasta, arq = u.rsplit(u'\\', 1)
        else:
            pasta, arq = u'', u
        stem = arq[:-4] if arq.lower().endswith(u'.rsm') else arq
        ys = [m.pos[1] for m in ms]
        linhas.append(u'| %d | %d | %s%s | `%s` | %s | %.0f..%.0f | %s | |'
                      % (i, len(ms),
                         pasta,
                         (u' — *%s*' % PASTAS[pasta]) if pasta in PASTAS
                         else u'',
                         stem,
                         parte(stem, NOMES) or u'?',
                         min(ys), max(ys),
                         como.get(u.lower(), u'—')))

    faltam = [n for n in ordem
              if (n.decode('cp949').rsplit(u'\\', 1)[-1][:-4]) not in NOMES]
    linhas.append(u'')
    linhas.append(u'## Sem tradução no dicionário: %d de %d'
                  % (len(faltam), len(ordem)))
    linhas.append(u'')
    if faltam:
        for n in faltam:
            linhas.append(u'- `%s`' % n.decode('cp949'))
    else:
        linhas.append(u'Nenhum.')

    with io.open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(u'\n'.join(linhas) + u'\n')
    print 'gravado %s: %d modelos distintos, %d sem traducao' % (
        sys.argv[2], len(ordem), len(faltam))
    return 0


if __name__ == '__main__':
    sys.exit(main())
