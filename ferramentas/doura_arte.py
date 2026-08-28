# -*- coding: utf-8 -*-
u"""Faz a arte DOURADA de um item nosso recolorindo a arte de outro item.

    python doura_arte.py --de 6121 --recurso pincel_do_infinito
    python doura_arte.py --de 6121 --recurso pincel_do_infinito --aplicar
    python doura_arte.py --de 6121 --recurso pincel_do_infinito --previa <pasta>
    python doura_arte.py --recurso pincel_do_infinito --reverter

POR QUE ISTO EXISTE
-------------------
O `instala_item.py` resolve a arte de um item nosso copiando o `resourceName`
de outro (o campo `arte_de`): dois IDs apontando para o mesmo desenho. Isso
serve para "a caixa tem a cara do que tem dentro", mas nao serve quando o item
NOVO precisa ser reconhecivel ao lado do VELHO. O Pincel do Infinito e o
Pincel de Maquiagem comum sao dois itens diferentes com a mesma funcao: se
desenharem igual, o jogador nao distingue um do outro na mochila.

Fazer arte a mao (Photoshop + repack do GRF) era o caminho conhecido. Este
script e o terceiro caminho: **recolorir a arte que ja existe**, byte a byte,
sem editor e sem GRF.

E BARATO PORQUE A ARTE DE RO E QUASE TODA INDEXADA. Dos quatro arquivos de um
item, dois (o `.spr` de chao e o icone de 24x24) sao imagens de 256 cores com
a paleta guardada em bloco proprio - recolorir e reescrever 1024 bytes, e
nenhum pixel e tocado. So a imagem de `collection` e RGB de verdade, e mesmo
ela e 75x100.

DE ONDE SAI A ARTE, E POR QUE NAO DO NOSSO GRF
----------------------------------------------
Do `data.grf` do bRO, como o `instala_visual.py`. O nosso GRF de 2021-11-03
tem essas entradas com DES (flags 3 e 5) e o `grf.py` nao le arquivo cifrado;
o do bRO e mais novo e nao usa DES, entao sai direto. Ver o LEIAME.md, secao
`instala_visual.py`.

ONDE ELE GRAVA, E POR QUE ISSO IMPORTA
--------------------------------------
Em `cliente/data/...`, que vence o GRF pelo DataFolderFirst - a mesma logica
do `tinge_dimensao.py` e do `destroi_mapa.py`. Ou seja: e mudanca de CLIENTE.
Ela NAO vai ao jogador pelo implanta.sh, precisa de PATCH (CLAUDE.md 4.18,
RECEITAS.md secao 0). Quem nao receber o patch ve o item sem arte - e icone
que falta e caixa de erro MODAL, nao so feio (ver `valida_visual.FATAIS`).

O ORIGINAL NUNCA SAI DO GRF, entao `--reverter` e so apagar os arquivos: nao
ha backup a manter.

O NOME DO RECURSO E ASCII, DE PROPOSITO
---------------------------------------
O `resourceName` dos itens do kRO e byte CP949 coreano, e e por isso que o
`instala_item.py` tem o campo `arte_de` (copia byte a byte) em vez de um campo
de texto. Recurso NOVO nao tem essa amarra: escrevemos o nome que quisermos, e
ASCII e o unico que sobrevive ao console, ao git e ao campo `recurso` do
`instala_item.py`. As pastas continuam coreanas - quem monta o caminho e o
`valida_visual.caminhos()`, que e a fonte unica desses caminhos no projeto.

A RAMPA DE OURO
---------------
Nao se escolhe cor por pixel: escolhe-se uma RAMPA. Cada cor da origem vira
uma luminancia (a formula de sempre, 0.299R + 0.587G + 0.114B) e a luminancia
escolhe um ponto da rampa. O desenho inteiro muda de metal de uma vez, e o
volume - o que e sombra e o que e brilho na peca original - fica intacto,
porque a luminancia e justamente o que carrega essa informacao.

A rampa vai de marrom escuro a amarelo palido passando por ouro; e o que
diferencia "dourado" de "amarelo", que era o risco de simplesmente empurrar o
matiz. Trocar a rampa e trocar cinco pares de numeros em RAMPA_OURO.

O QUE NUNCA E TOCADO
--------------------
- **A cor de transparencia.** No icone e no `.spr` e o magenta puro
  (255,0,255); no `.spr` e tambem o indice 0, que o cliente trata como vazio
  independentemente da cor que esteja la. Dourar qualquer um dos dois pinta
  o fundo do icone de ouro solido.
- **O branco puro da `collection`.** Aquela imagem nao tem canal alfa: o fundo
  E branco (6902 dos 7500 pixels do pincel), e o cliente desenha por cima do
  painel claro da janela de descricao. Dourar o branco pintaria a moldura
  inteira.

A AURA
------
Opcional, e so na `collection` - no icone de 24x24 ela vira um borrao. E um
halo radial que puxa o que estiver embaixo na direcao de uma cor quente, com
intensidade caindo com o quadrado da distancia. Sobre o fundo BRANCO ela
aparece como halo dourado; sobre a peca, como brilho.

Somar luz nao funcionaria aqui: o fundo ja e (255,255,255) e nao tem para
onde subir. Por isso a mistura e por interpolacao, nao por soma.

Roda em Python 2.7 (`C:/Python27/python.exe`), como o resto de `ferramentas/`.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
from grf import Grf

GRF_BRO = os.path.join(os.environ.get('ProgramFiles(x86)', ''),
                       'Gravity Interactive, Inc', 'Ragnarok Brazil', 'data.grf')

# Luminancia -> cor. Cinco paradas bastam: menos que isso o meio-tom vira
# amarelo chapado, mais que isso nao se distingue na tela.
RAMPA_OURO = [(0.00, (38, 22, 4)),
              (0.30, (124, 82, 16)),
              (0.55, (198, 150, 40)),
              (0.75, (240, 204, 92)),
              (1.00, (255, 250, 214))]

MAGENTA = (255, 0, 255)     # transparencia do icone e do .spr
BRANCO = (255, 255, 255)    # fundo da imagem de collection

AURA_COR = (255, 205, 80)


def dourado(r, g, b, rampa=RAMPA_OURO):
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    for i in range(len(rampa) - 1):
        ini, cor_ini = rampa[i]
        fim, cor_fim = rampa[i + 1]
        if lum <= fim or i == len(rampa) - 2:
            t = 0.0 if fim == ini else max(0.0, min(1.0, (lum - ini) / (fim - ini)))
            return tuple(int(round(cor_ini[k] + (cor_fim[k] - cor_ini[k]) * t))
                         for k in range(3))
    return rampa[-1][1]


def mistura(cor, alvo, forca):
    return tuple(int(round(cor[k] + (alvo[k] - cor[k]) * forca)) for k in range(3))


# ------------------------------------------------------------------ formatos

def paleta(pal, ordem, preserva_indice_zero):
    """Doura os 1024 bytes de uma paleta de 256 cores.

    `ordem` e 'bgra' (BMP) ou 'rgba' (SPR) - a diferenca e real e trocar os
    canais transformaria o marrom da rampa em azul.
    """
    fora = []
    for i in range(256):
        c = pal[i * 4:i * 4 + 4]
        b0, b1, b2, b3 = struct.unpack('4B', c)
        if ordem == 'bgra':
            b, g, r, a = b0, b1, b2, b3
        else:
            r, g, b, a = b0, b1, b2, b3
        if (r, g, b) == MAGENTA or (preserva_indice_zero and i == 0):
            fora.append(c)
            continue
        nr, ng, nb = dourado(r, g, b)
        if ordem == 'bgra':
            fora.append(struct.pack('4B', nb, ng, nr, a))
        else:
            fora.append(struct.pack('4B', nr, ng, nb, a))
    return b''.join(fora)


def doura_bmp8(dados):
    """Icone de inventario: 8 bits, paleta de 1024 bytes logo apos o cabecalho."""
    ini = 54
    return dados[:ini] + paleta(dados[ini:ini + 1024], 'bgra', False) + dados[ini + 1024:]


def doura_bmp24(dados, aura=None):
    """Imagem de collection: 24 bits, sem paleta - pixel a pixel.

    `aura` e (x, y, raio, forca) em coordenadas de TELA (y=0 no topo), que sao
    as que se leem olhando a imagem; o BMP guarda as linhas de baixo para cima
    e a conversao e feita aqui, num lugar so.
    """
    off = struct.unpack('<I', dados[10:14])[0]
    larg, alt = struct.unpack('<ii', dados[18:26])
    passo = (larg * 3 + 3) // 4 * 4
    corpo = bytearray(dados[off:])
    for y in range(alt):
        tela_y = alt - 1 - y
        base = y * passo
        for x in range(larg):
            p = base + x * 3
            b, g, r = corpo[p], corpo[p + 1], corpo[p + 2]
            if (r, g, b) == BRANCO:
                novo = BRANCO
            else:
                novo = dourado(r, g, b)
            if aura is not None:
                ax, ay, raio, forca = aura
                d2 = (x - ax) ** 2 + (tela_y - ay) ** 2
                if d2 < raio * raio:
                    t = 1.0 - (d2 ** 0.5) / float(raio)
                    novo = mistura(novo, AURA_COR, t * t * forca)
            corpo[p], corpo[p + 1], corpo[p + 2] = novo[2], novo[1], novo[0]
    return dados[:off] + bytes(corpo)


def doura_spr(dados):
    """Sprite de chao: a paleta sao os ULTIMOS 1024 bytes do arquivo.

    Vale para .spr versao 1.1 em diante, que e o caso de todo item deste
    cliente (o do 6121 e 2.1). Versao 1.0 nao tem paleta e nao chega aqui -
    o script recusa antes.
    """
    if dados[:2] != b'SP':
        raise Exception('nao e um .spr')
    menor, maior = ord(dados[2:3]), ord(dados[3:4])
    if (maior, menor) < (1, 1):
        raise Exception('.spr versao %d.%d nao tem paleta' % (maior, menor))
    return dados[:-1024] + paleta(dados[-1024:], 'rgba', True)


def doura_act(dados):
    """O .act e animacao, nao imagem: passa intacto. Existe so para o item ter
    os QUATRO arquivos - sem ele o cliente da `Cannot find File` ao desenhar
    o item no chao."""
    return dados


# ------------------------------------------------------------------ o trabalho

def arquivos(res_origem, res_novo):
    """(rotulo, caminho de origem, caminho de destino, funcao) para os 4 arquivos.

    Os caminhos saem do `valida_visual.caminhos()`, que e a fonte unica deles
    no projeto - o `instala_visual.py` usa a mesma.
    """
    cli = vv.Cliente()
    de = cli.caminhos(res_origem, None)
    para = cli.caminhos(res_novo, None)
    trata = {'sprite de chao (.spr)': doura_spr,
             'sprite de chao (.act)': doura_act,
             'icone do inventario': doura_bmp8,
             'icone grande': doura_bmp24}
    return [(rot, cam_de, para[i][1], trata[rot])
            for i, (rot, cam_de) in enumerate(de)]


def main():
    args = sys.argv[1:]

    def opt(nome, padrao=None):
        return args[args.index(nome) + 1] if nome in args else padrao

    res_novo = opt('--recurso')
    if not res_novo:
        print __doc__
        return 2
    if any(ord(c) > 127 for c in res_novo):
        print 'ERRO: --recurso tem que ser ASCII (ver o cabecalho).'
        return 1

    aplicar = '--aplicar' in args
    previa = opt('--previa')

    if '--reverter' in args:
        cli = vv.Cliente()
        for rot, cam in cli.caminhos(res_novo, None):
            disco = vv.caminho_disco(cam)
            if os.path.exists(disco):
                if aplicar:
                    os.remove(disco)
                print '%s  %s' % ('apagado' if aplicar else 'apagaria', rot)
        if not aplicar:
            print '(nada foi apagado - repita com --aplicar)'
        return 0

    origem_id = opt('--de')
    if not origem_id:
        print 'ERRO: falta --de <id do item de onde sai a arte>.'
        return 1
    origem_id = int(origem_id)

    aura = None
    if opt('--aura'):
        x, y, raio, forca = opt('--aura').split(',')
        aura = (int(x), int(y), int(raio), float(forca))

    if not os.path.exists(GRF_BRO):
        print 'ERRO: nao achei a GRF do bRO em %s' % GRF_BRO
        return 1
    grf = Grf(GRF_BRO)

    info = vv.le_iteminfo(vv.ITEMINFO)
    if origem_id not in info:
        print 'ERRO: o item %d nao esta no itemInfo.lua do cliente.' % origem_id
        return 1
    res_origem = info[origem_id]

    print 'origem : item %d, recurso de %d bytes' % (origem_id, len(res_origem))
    print 'destino: recurso "%s"' % res_novo
    print 'aura   : %s' % ('nenhuma' if aura is None else str(aura))
    print

    for rot, cam_de, cam_para, trata in arquivos(res_origem, res_novo):
        chave = cam_de.lower()
        if chave not in grf.entries:
            print '  FALTA na GRF do bRO: %s' % rot
            return 1
        dados = grf.read(chave)
        if trata is doura_bmp24:
            novo = trata(dados, aura)
        else:
            novo = trata(dados)
        disco = vv.caminho_disco(cam_para)
        print '  %-24s %6d bytes -> %s' % (rot, len(novo),
                                           'gravado' if aplicar else 'gravaria')
        if aplicar:
            pasta = os.path.dirname(disco)
            if not os.path.isdir(pasta):
                os.makedirs(pasta)
            fh = open(disco, 'wb')
            fh.write(novo)
            fh.close()
        if previa:
            escreve_previa(previa, rot, dados, novo, aura)

    print
    if aplicar:
        print 'pronto. Confira com: python valida_visual.py --id <id do item novo>'
        print 'E LEMBRE: isto e cliente. Vai por PATCH, nao pelo implanta.sh.'
    else:
        print '(nada foi gravado - repita com --aplicar)'
    return 0


# ------------------------------------------------------------------- a previa
#
# PNG cru, so para olhar antes de gravar. Nao entra no cliente e nao depende
# de biblioteca nenhuma - o cliente nao le PNG, e instalar PIL para conferir
# uma imagem de 75x100 seria trocar uma dependencia por um olhar.

def _png(caminho, larg, alt, linhas):
    import zlib
    bruto = b''.join(b'\x00' + l for l in linhas)

    def bloco(tipo, dados):
        c = tipo + dados
        return (struct.pack('>I', len(dados)) + c +
                struct.pack('>I', zlib.crc32(c) & 0xffffffff))

    d = (b'\x89PNG\r\n\x1a\n' +
         bloco(b'IHDR', struct.pack('>IIBBBBB', larg, alt, 8, 2, 0, 0, 0)) +
         bloco(b'IDAT', zlib.compress(bruto, 9)) +
         bloco(b'IEND', b''))
    fh = open(caminho, 'wb')
    fh.write(d)
    fh.close()


def _rasteriza(dados, zoom=4):
    """(largura, altura, linhas RGB) de um BMP de 8 ou 24 bits, ja virado."""
    off = struct.unpack('<I', dados[10:14])[0]
    larg, alt = struct.unpack('<ii', dados[18:26])
    bpp = struct.unpack('<H', dados[28:30])[0]
    if bpp == 8:
        pal = dados[54:54 + 1024]
        passo = (larg + 3) // 4 * 4
    else:
        passo = (larg * 3 + 3) // 4 * 4
    linhas = []
    for y in range(alt - 1, -1, -1):
        lin = []
        for x in range(larg):
            if bpp == 8:
                i = ord(dados[off + y * passo + x])
                b, g, r = struct.unpack('3B', pal[i * 4:i * 4 + 3])
            else:
                p = off + y * passo + x * 3
                b, g, r = struct.unpack('3B', dados[p:p + 3])
            if (r, g, b) == MAGENTA:
                r, g, b = 40, 40, 40      # so na previa, para o fundo aparecer
            lin.append(struct.pack('3B', r, g, b) * zoom)
        for _ in range(zoom):
            linhas.append(b''.join(lin))
    return larg * zoom, alt * zoom, linhas


def escreve_previa(pasta, rotulo, antes, depois, aura):
    if 'icone' not in rotulo:
        return
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    tag = 'icone' if 'inventario' in rotulo else 'collection'
    for nome, d in (('antes', antes), ('depois', depois)):
        larg, alt, linhas = _rasteriza(d)
        _png(os.path.join(pasta, '%s_%s.png' % (tag, nome)), larg, alt, linhas)


if __name__ == '__main__':
    sys.exit(main())
