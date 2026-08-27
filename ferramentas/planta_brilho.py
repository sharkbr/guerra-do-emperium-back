# -*- coding: utf-8 -*-
"""Poe um emissor de particulas numa celula de mapa, pelo EffectTool do cliente.

    python planta_brilho.py                 # mostra o que ha no mapa hoje
    python planta_brilho.py --aplicar       # grava o override no cliente
    python planta_brilho.py --reverter      # apaga o override

POR QUE ISTO EXISTE
-------------------
O pedido foi "uns brilhos embaixo da celula do Sabio Varmunt, com a textura
epi_glow_01.bmp". Nao da para fazer isso pelo servidor: `specialeffect` so
alcanca efeitos que o cliente numera, e o brilho de Epiclesis nao e um deles
- ele e desenhado como UNIDADE DE HABILIDADE (UNT_EPICLESIS), que so existe
enquanto a magia esta no chao. Nao ha constante EF_ para ele no rAthena, e
nao ha como pedi-lo por script.

O que existe e melhor: o cliente tem um sistema de EMISSORES DE PARTICULAS
por mapa, em `data\\luafiles514\\lua files\\effecttool\\<mapa>.lub`, e ele
aceita o CAMINHO DA TEXTURA direto. E o mesmo mecanismo que faz a fumaca
sair das chamines de Prontera (tres emissores com `effect\\smoke1.bmp`).
Ou seja: da para pedir exatamente aquela arte, na coordenada que se quiser.

ISTO E CLIENTE. Vai ao jogador por PATCH, nao por deploy (CLAUDE.md 4.18).

A CONVERSAO DE CELULA PARA MUNDO
--------------------------------
O `pos` do emissor e (x, altura, z) em unidades de mundo, nao em celulas:

    mundo_x = (celula_x + 0.5 - largura/2) * 5
    mundo_z = (celula_y + 0.5 - altura_mapa/2) * 5
    mundo_y = -altura_do_terreno        (o eixo Y e negativo para cima)

Os dois primeiros nao sao chute: saem do unico caso do projeto que ja foi
conferido EM TELA pelo dono - a fonte do Centro da Ordem, em `auction_01`
(200x100), documentada no cabecalho do edita_mapa.py como "centro na
fronteira entre a 179 e a 180: mundo (400, 110)". Conferindo:

    x: 180 * 5 - (200/2) * 5 = 900 - 500 = 400   ok
    z:  72 * 5 - (100/2) * 5 = 360 - 250 = 110   ok

E o Z NAO e invertido - cresce junto com o y de celula. A altura sai do
`.gat` (o `altura_media` do gat.py), com o sinal trocado.

O QUE O ARQUIVO TEM
-------------------
Duas globais e nada mais - sem funcoes, o que torna a regeracao segura:

    _<mapa>_effect_version = 2.0
    _<mapa>_emitterInfo    = { [0] = {...}, [1] = {...}, ... }

Cada emissor tem 15 campos. Os que importam aqui: `texture` (caminho
relativo a `data\\texture\\`), `pos`, `size`, `life`, `rate`, `maxcount`,
`color` (RGBA) e `gravity`. Os outros sao copiados do que o mapa ja usava,
para nao inventar valor que nao se pode conferir.

O `.lub` e BYTECODE Lua 5.1: o arquivo e gerado como texto e compilado com
o `luac.exe` do ROenglishRE, que e tambem a unica prova de que ele compila
(CLAUDE.md secao 5).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grf
import gat
import ptbr

GRF_CLIENTE = r'C:\GuerraDoEmperium\cliente\data.grf'
PASTA_EFX = r'C:\GuerraDoEmperium\cliente\data\luafiles514\lua files\effecttool'
LUAC = r'C:\Users\User\Downloads\ROenglishRE\Tools\luac.exe'

MAPA = 'prontera'
CELULA = (156, 303)          # o Sabio Varmunt (npc/guerra/anomalia_dimensional.txt)
TEXTURA = 'effect\\mineffect\\new_epiclesis\\epi_glow_01.bmp'


def _interno(caminho):
    return 'data\\luafiles514\\lua files\\effecttool\\%s.lub' % caminho


def _le_original():
    """Sempre do GRF: o override do cliente nao serve de base para si mesmo.

    Reler o proprio arquivo gerado faria a receita apontar para si mesma, e
    uma rodada ruim viraria a fonte da seguinte - a armadilha do `arte_de`
    do instala_item.py (CLAUDE.md secao 5).
    """
    g = grf.Grf(GRF_CLIENTE)
    return g.read(_interno(MAPA))


def _tamanho_e_altura():
    g = grf.Grf(GRF_CLIENTE)
    d = gat.Gat(g.read('data\\%s.gat' % MAPA))
    cx, cy = CELULA
    return d.largura, d.altura, d.altura_media(cx, cy)


def _mundo():
    larg, alt, h = _tamanho_e_altura()
    cx, cy = CELULA
    x = (cx + 0.5 - larg / 2.0) * 5.0
    z = (cy + 0.5 - alt / 2.0) * 5.0
    # meia unidade acima do chao, para o brilho nao brigar com o terreno
    y = -h - 0.5
    return x, y, z


def _vetor(t):
    """A tabela do bytecode vem como {1.0: v, 2.0: v, ...}; devolve lista."""
    if not isinstance(t, dict):
        return [t]
    return [t[k] for k in sorted(t)]


def _lua_valor(v):
    if isinstance(v, str):
        return '"%s"' % v.replace('\\', '\\\\')
    if isinstance(v, dict):
        return '{ ' + ', '.join(_lua_num(x) for x in _vetor(v)) + ' }'
    return _lua_num(v)


def _lua_num(v):
    if isinstance(v, float) and v == int(v):
        return '%.1f' % v
    return repr(v)


def _emissor_nosso(pos, modelo):
    """O brilho, HERDANDO do emissor de fumaca que o mapa ja usa.

    A primeira versao inventou os quinze campos do zero e nao apareceu em
    tela. Esta parte do `modelo` - um dos emissores de fumaca das chamines
    de Prontera, que comprovadamente desenham neste cliente - e troca **so
    o que precisa mudar**. Os campos de desenho (`srcmode`, `destmode`,
    `zenable`, `speed`) vem de la sem serem tocados: sao modos de blending
    do Direct3D, nao ha como conferir o valor certo offline, e o que se
    sabe e que aqueles funcionam.

    E a mesma regra do resto do projeto - mesclar por chave em vez de
    escrever por cima (CLAUDE.md 4.5).

    O que muda, e por que:
      texture   a arte pedida;
      pos       a celula do Varmunt;
      gravity   ZERADA - a fumaca sobe porque tem -2.0 no eixo Y, e um halo
                de chao tem que ficar parado;
      dir1/dir2 zerados pelo mesmo motivo (a fumaca se espalha);
      size      maior que os 15-20 da fumaca, para cobrir a celula;
      color     claro e quente, contra o [5,15,20,50] escuro da fumaca;
      life/rate/maxcount  poucas particulas, vivendo mais - brilho continuo
                em vez de jato.
    """
    e = dict(modelo)
    e['texture'] = TEXTURA
    e['pos'] = {1.0: pos[0], 2.0: pos[1], 3.0: pos[2]}
    e['gravity'] = {1.0: 0.0, 2.0: 0.0, 3.0: 0.0}
    e['dir1'] = {1.0: 0.0, 2.0: 0.0, 3.0: 0.0}
    e['dir2'] = {1.0: 0.0, 2.0: 0.0, 3.0: 0.0}
    e['size'] = {1.0: 35.0, 2.0: 45.0}
    e['color'] = {1.0: 200.0, 2.0: 170.0, 3.0: 110.0, 4.0: 60.0}
    e['life'] = {1.0: 3.0, 2.0: 4.0}
    e['rate'] = {1.0: 8.0, 2.0: 10.0}
    e['maxcount'] = {1.0: 8.0}
    e['radius'] = {1.0: 0.0, 2.0: 0.0, 3.0: 0.0}
    return e


ORDEM = ['texture', 'pos', 'size', 'life', 'rate', 'maxcount', 'color',
         'gravity', 'dir1', 'dir2', 'radius', 'speed', 'srcmode', 'destmode',
         'zenable']


def gera_lua(emissores, versao):
    linhas = ['_%s_effect_version = %s' % (MAPA, _lua_num(versao)),
              '_%s_emitterInfo = {' % MAPA]
    for i in sorted(emissores):
        e = emissores[i]
        linhas.append('\t[%d] = {' % int(i))
        for campo in ORDEM:
            if campo in e:
                linhas.append('\t\t%s = %s,' % (campo, _lua_valor(e[campo])))
        # campos que o mapa tenha e nao estejam na ORDEM, para nao perder nada
        for campo in sorted(e):
            if campo not in ORDEM:
                linhas.append('\t\t%s = %s,' % (campo, _lua_valor(e[campo])))
        linhas.append('\t},')
    linhas.append('}')
    return '\n'.join(linhas) + '\n'


def carrega():
    t = ptbr.tabelas(_le_original())
    versao = t['_%s_effect_version' % MAPA]
    emissores = dict(t['_%s_emitterInfo' % MAPA])
    return versao, emissores


def mostra():
    versao, em = carrega()
    print 'ORIGINAL (do data.grf): versao %s, %d emissores' % (versao, len(em))
    for i in sorted(em):
        e = em[i]
        print '  [%d] %-46s pos=%s' % (int(i), e.get('texture'),
                                       _vetor(e.get('pos')))
    x, y, z = _mundo()
    larg, alt, h = _tamanho_e_altura()
    print
    print 'O NOSSO iria em: celula %d,%d de %s (%dx%d, terreno %.2f)' % (
        CELULA[0], CELULA[1], MAPA, larg, alt, h)
    print '  mundo (%.1f, %.1f, %.1f)   textura %s' % (x, y, z, TEXTURA)
    d = os.path.join(PASTA_EFX, '%s.lub' % MAPA)
    print
    print 'override no cliente: %s' % ('SIM  ' + d if os.path.exists(d) else 'nao')


def _grava(texto, destino):
    """Grava o .lub como TEXTO Lua, nao como bytecode.

    O cliente aceita os dois, e o texto e o formato que este projeto ja usa
    e comprovou: o `OngoingQuestInfoList.lub`, o `CheckAttendance.lub` e os
    `.lub` de `data\\` gerados pelo traduz_ptbr.py sao todos texto puro
    (comecam com `--`), e sao lidos.

    A primeira versao desta ferramenta compilava com `luac -s`, e o
    resultado nao apareceu em tela. Nao ficou provado que o bytecode era a
    causa - mas ele era a unica peca do caminho sem precedente no projeto,
    e trocar por texto custa nada e elimina a duvida.

    O `luac -p` continua rodando, agora so como CONFERENCIA de sintaxe: ele
    e a unica prova de que o arquivo carrega (CLAUDE.md secao 5).
    """
    if not os.path.isdir(PASTA_EFX):
        os.makedirs(PASTA_EFX)
    open(destino, 'wb').write(texto)
    r = subprocess.call([LUAC, '-p', destino])
    if r != 0:
        print '### o luac recusou o arquivo gerado'
        return False
    return True


def _confere(destino, esperado, n_antes):
    """Le de volta o que foi gravado, PASSANDO PELO INTERPRETADOR.

    O arquivo e texto, e conferir texto com regex provaria pouco - diria
    que a string esta la, nao que o Lua entende o arquivo. Entao ele e
    compilado para um bytecode temporario e lido com o mesmo parser que le
    os `.lub` do GRF: se as tabelas sairem certas daqui, sairao certas no
    cliente.
    """
    tmp = destino + '.conferencia'
    if subprocess.call([LUAC, '-o', tmp, destino]) != 0:
        print '### o luac nao compilou o arquivo para conferencia'
        return False
    try:
        conf = ptbr.tabelas(open(tmp, 'rb').read())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    dep = conf['_%s_emitterInfo' % MAPA]
    print 'gravado: %s' % destino
    print '  %d bytes, %d emissores (eram %d)' % (
        os.path.getsize(destino), len(dep), n_antes)
    achou = [i for i in dep if dep[i].get('texture') == esperado]
    if not achou:
        print '### a textura %s NAO esta no arquivo lido de volta' % esperado
        return False
    for i in sorted(achou):
        print '  [%d] %s pos=%s size=%s' % (
            int(i), esperado, _vetor(dep[i]['pos']), _vetor(dep[i]['size']))
    return True


def aplica(sonda=False):
    versao, em = carrega()
    n_antes = len(em)

    # a textura tem que existir, senao o cliente desenha um quadrado branco
    g = grf.Grf(GRF_CLIENTE)
    if ('data\\texture\\' + TEXTURA).lower() not in g.entries:
        print '### a textura nao esta no GRF: %s' % TEXTURA
        return 1

    destino = os.path.join(PASTA_EFX, '%s.lub' % MAPA)

    if sonda:
        # A MARCA QUE NAO DEPENDE DO EFEITO PROCURADO (CLAUDE.md secao 5).
        # Troca a textura das fumacas que JA APARECEM, sem mexer em mais
        # nada. Se as chamines de Prontera passarem a soltar o brilho, o
        # arquivo esta sendo lido e o problema e do nosso emissor; se
        # continuarem soltando fumaca, o cliente nao le este arquivo - e
        # nenhum ajuste de tamanho ou cor vai resolver.
        for i in em:
            em[i]['texture'] = TEXTURA
            em[i]['size'] = {1.0: 30.0, 2.0: 40.0}
        print 'MODO SONDA: as tres fumacas de Prontera passam a usar %s' % TEXTURA
        print '  (nenhum emissor novo; so a textura e o tamanho mudaram)'
        print
    else:
        modelo = em[min(em)]          # um emissor que o mapa ja desenha
        novo = max(int(i) for i in em) + 1
        em[float(novo)] = _emissor_nosso(_mundo(), modelo)

    if not _grava(gera_lua(em, versao), destino):
        return 1
    if not _confere(destino, TEXTURA, n_antes):
        return 1
    print
    print 'O cliente so rele o mapa ao ENTRAR nele - saia de Prontera e volte.'
    print 'ISTO E CLIENTE: vai ao jogador por PATCH, nao por deploy.'
    return 0


def reverte():
    for ext in ('lub', 'lua'):
        d = os.path.join(PASTA_EFX, '%s.%s' % (MAPA, ext))
        if os.path.exists(d):
            os.remove(d)
            print 'apagado: %s' % d
    print 'O cliente volta a ler o effecttool do GRF, sem o brilho.'


def main():
    if '--reverter' in sys.argv:
        reverte()
        return 0
    if '--sonda' in sys.argv:
        return aplica(sonda=True)
    if '--aplicar' in sys.argv:
        return aplica()
    mostra()
    return 0


if __name__ == '__main__':
    sys.exit(main())
