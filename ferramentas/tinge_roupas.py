# -*- coding: utf-8 -*-
"""Gera cores novas de roupa para todas as classes, a partir das que a Gravity fez.

    python tinge_roupas.py --listar                 # o que existe, classe a classe
    python tinge_roupas.py --previa <pasta>         # PNG de amostra, sem gravar no cliente
    python tinge_roupas.py --previa <pasta> --classe dragon_knight
    python tinge_roupas.py --ensaio                 # o que --aplicar gravaria
    python tinge_roupas.py --aplicar                # grava em cliente\\data\\palette\\
    python tinge_roupas.py --conferir               # tudo que devia estar no disco esta? (sai 1 se nao)
    python tinge_roupas.py --reverter --aplicar     # apaga o que este script gravou

Cor de roupa em Ragnarok nao e sprite, e PALETTE: um arquivo de 1024 bytes
(256 cores RGBA) em `data\\palette\\<corpo>\\<classe>_<sexo>_<n>.pal`, um por
classe, sexo e indice. O sprite e indexado e o cliente so troca a tabela. O
servidor manda o indice (`setlook LOOK_CLOTHES_COLOR`) e mais nada - indice
sem palette NAO da erro, o cliente desenha a cor padrao.

A Gravity fez poucas: classes base 0..4, 2a e 3a classes 0..3, 4a classes e
trajes 0..7 - e e por isso que o jogador ve "a basica e mais duas".

COMO SE ACHA A ROUPA DENTRO DA PALETTE. Nao ha campo que diga quais dos 256
indices sao tecido e quais sao pele, cabelo ou metal. Mas as palettes oficiais
entregam isso de graca: entre a 0 e cada uma das outras so mudam os indices
da roupa (16 a 40 dos 256, medido em sete classes). A uniao dessas diferencas
e a MASCARA, e e so nela que este script mexe - pele e cabelo ficam iguais.
Diferenca acima de METADE da palette e descartada: a `_4` do Cavaleiro muda
254 indices, e uma tabela inteira de outra origem, nao uma cor.

Tres casos que a regra acima nao cobre, e o que se faz em cada um:
- roupa SEM cor oficial (casamento, Papai Noel, verao, hanbok, Oktoberfest):
  as oito palettes sao identicas. Gravity diz que nao se tinge, e nao se tinge;
- so tabela de outra origem (Renegado: `_2` e `_3` mudam 250 indices): a
  mascara vem de HEURISTICA - todo indice que os quadros usam, menos pele
  (matiz de 8 a 45 graus, saturacao media, claro), contorno (escuro) e
  cinza. Pinta metal junto, e e o preco de nao pintar nada;
- palette com nome de classe que nao e o nome do SPRITE (Sentinela e
  `레인저` na palette e `레인져` no sprite; Sumo Sacerdote e `하이프리스트`
  e `하이프리`): sao duas tabelas do exe, e a de palette envelheceu
  separada. `APELIDO_SPRITE` liga uma a outra, e foi montada olhando a
  lista de sprites de corpo do nosso GRF.

A BASE de cada cor nova e a palette EMBUTIDA no `.spr` (os 1024 bytes do
fim), nao a `_0.pal`: e ela que o cliente desenha quando nao carrega palette
nenhuma, e as duas diferem em 4 a 60 indices em 146 das 270 classes/sexos.
Quando o sprite nao existe com nome nenhum, a `_0.pal` serve de base.

COMO SE TINGE. Cada indice da mascara vira HSV. A cor-alvo diz o matiz
dominante que a roupa deve ter; o script mede o matiz dominante da roupa
original (media circular, pesada por saturacao x valor) e desloca TODOS os
indices pela mesma diferenca - assim um detalhe que era de outro tom que o
tecido continua de outro tom, so que girado junto. Saturacao e valor sao
multiplicados, e e isso que faz o preto, o branco e o cinza. Roupa que ja e
cinza (saturacao dominante abaixo de 0.2) nao tem matiz para deslocar: ai o
alvo e absoluto e a saturacao ganha um piso.

ONDE ENTRAM AS CORES NOVAS: a partir do indice 4, para TODA classe, e isso
e uma decisao. A alternativa era comecar depois da ultima oficial de cada
classe, mas ai "cor 6" seria uma coisa para o Aprendiz e outra para o
Cavaleiro Dragao, e o Edgard (o NPC) nao tem como saber a classe de quem
clica. Custo: as classes base perdem a `_4` da Gravity e as 4a classes
perdem as `_4`..`_7` - sobrescritas no disco pelo DataFolderFirst, intactas
no GRF. Trocar a lista `CORES` desfaz a decisao.

FONTE: o nosso `data.grf`, e so ele. 492 das 1434 palettes de corpo estao
com DES la, e o primeiro rascunho deste script as lia do GRF do bRO - ate
medir que 434 dessas 492 sao DIFERENTES no bRO (2026-09-13). Foi o que pos
o DES da Gravity no `grf.py`. Sprite do bRO tambem difere do nosso, e o
`.pal` tem de casar com o `.spr` que ESTE cliente desenha.

NOME COREANO NO DISCO: a pasta e `¸ö`, nao `몸`. O cliente e programa ANSI e
abre o arquivo pelos bytes CP949 do GRF interpretados na codepage desta
maquina (1252) - o mesmo motivo de `data\\sprite\\¾Ç¼¼»ç¸®\\` ja existir com
esse nome. `decode('mbcs')` e a expressao exata disso (valida_visual.py).

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
Depois de gravar: e mudanca de CLIENTE, vai por patch (CLAUDE.md §4.18), e o
cliente precisa ser fechado e reaberto. O teto do Edgard
(npc/guerra/xanin_e_edgard.txt) tem de bater com `ULTIMO_INDICE`.
"""
import codecs
import collections
import colorsys
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grf import Grf
from doura_arte import _png

# Nome coreano estoura o print do console; o byte no disco e o que importa.
sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

CLIENTE = r'C:\GuerraDoEmperium\cliente'
GRF_NOSSO = os.path.join(CLIENTE, 'data.grf')

BS = chr(92)


def _k(u):
    return u.encode('cp949')

CORPO = _k(u'\ubab8')                # 몸
DORAM = _k(u'\ub3c4\ub78c\uc871')    # 도람족
HUMANO = _k(u'\uc778\uac04\uc871')   # 인간족
TRONCO = _k(u'\ubab8\ud1b5')         # 몸통
HOMEM = _k(u'\ub0a8')                # 남
MULHER = _k(u'\uc5ec')               # 여

# As pastas de palette de CORPO. `머리` e cabelo e fica de fora.
PASTAS = [
    (BS.join(['data', 'palette', CORPO]), HUMANO, ''),
    (BS.join(['data', 'palette', CORPO, 'costume_1']), HUMANO, 'costume_1'),
    (BS.join(['data', 'palette', CORPO, 'costume_2']), HUMANO, 'costume_2'),
    (BS.join(['data', 'palette', CORPO, 'costume_3']), HUMANO, 'costume_3'),
    (BS.join(['data', 'palette', CORPO, 'costume_4']), HUMANO, 'costume_4'),
    (BS.join(['data', 'palette', DORAM, 'body']), DORAM, ''),
]

# <classe>_<sexo>_<cor>[_<traje>].pal
NOME = re.compile(r'^(?P<classe>.+)_(?P<sexo>' + HOMEM + '|' + MULHER +
                  r')_(?P<cor>\d+)(?P<traje>_\d+)?\.pal$', re.I)

# Palette com um nome, sprite com outro. Chave e valor em CP949, como no GRF.
APELIDO_SPRITE = {
    u'레인저': u'레인져',                  # Sentinela
    u'울프레인저': u'레인져늑대',          # Sentinela no lobo
    u'하이프리스트': u'하이프리',          # Sumo Sacerdote
    u'어세신크로스': u'어쌔신크로스',      # Algoz
    u'어새신': u'어세신',                  # Mercenario (grafia velha)
    u'로얄가드': u'가드',                  # Guardiao Real
    u'그리폰로얄': u'그리폰가드',          # Guardiao Real no grifo
    u'크루': u'크루세이더',                # Templario
    u'페코페코_크루': u'신페코크루세이더', # Templario no pecopeco
    u'댄서': u'무희',                      # Odalisca
    u'룬드래곤': u'룬나이트쁘띠',          # Cavaleiro Runico no dragao
    u'미케닉_마도기어': u'마도기어',       # Mecanico no Magitrone
    u'미케닉_마도아머': u'마도아머',
    u'검사페코': u'페코검사',              # Espadachim no pecopeco
    u'페코팔라': u'페코팔라딘',            # Paladino no pecopeco
    u'페코로나': u'로드페코',              # Lorde no pecopeco
    u'크라운': u'클라운',                  # Menestrel
    u'고양이카트': u'cart_summoner',       # doram com carrinho
    u'묘족': u'summoner',                  # doram
    u'hanbok': u'한복',
    u'santa': u'산타',
    u'summer': u'여름',
    u'summer2': u'여름2',
    u'oktoberfest': u'옥토버패스트',
}
# O GRF guarda os nomes em minusculas, e `.lower()` em CP949 tambem mexe no
# segundo byte de algumas silabas - entao a chave se compara ja rebaixada.
APELIDO_SPRITE = dict((_k(k).lower(), _k(v)) for k, v in APELIDO_SPRITE.items())

# As cores novas, por indice ABSOLUTO. `h` e o matiz dominante que a roupa
# deve ficar (graus); `s` e `v` multiplicam saturacao e valor; `smin` e o piso
# de saturacao para roupa que nasce cinza. Trocar a lista e trocar as cores;
# o Edgard precisa saber o ultimo indice.
CORES = [
    (4, 'vermelho', dict(h=0)),
    (5, 'laranja', dict(h=28)),
    (6, 'amarelo', dict(h=52)),
    (7, 'verde', dict(h=125)),
    (8, 'verde-agua', dict(h=172)),
    (9, 'azul', dict(h=218)),
    (10, 'roxo', dict(h=272)),
    (11, 'rosa', dict(h=325)),
    (12, 'marrom', dict(h=25, s=0.75, v=0.62)),
    (13, 'branco', dict(s=0.12, v=1.55)),
    (14, 'cinza', dict(s=0.08, v=0.9)),
    (15, 'preto', dict(s=0.25, v=0.35)),
]
PRIMEIRO_INDICE = CORES[0][0]
ULTIMO_INDICE = CORES[-1][0]

# Palette oficial que difere da 0 em mais indices que isto nao e "outra cor",
# e outra tabela - a `_4` do Cavaleiro muda 254 dos 256.
DIFERENCA_MAXIMA = 128
RETOQUE_MAXIMO = 20
SATURACAO_CINZA = 0.2
PISO_SATURACAO = 0.55


# ---------------------------------------------------------------- fontes

class Fontes(object):
    """O nosso data.grf. O grf.py le as entradas com DES desde 2026-09-13."""

    def __init__(self):
        self.nosso = Grf(GRF_NOSSO)

    def le(self, nome):
        k = nome.lower()
        if k not in self.nosso.entries:
            return None
        return self.nosso.read(k)

    def corpos(self):
        """(pasta, raca, traje, classe, sexo) -> {indice: nome no GRF}.

        E o nosso GRF que decide quais classes existem.
        """
        grupos = {}
        for k, e in self.nosso.entries.items():
            for pasta, raca, traje in PASTAS:
                p = pasta.lower() + BS
                if not k.startswith(p) or BS in k[len(p):]:
                    continue
                m = NOME.match(e[5][len(p):])
                if not m:
                    continue
                chave = (pasta, raca, traje, m.group('classe'), m.group('sexo'))
                grupos.setdefault(chave, {})[int(m.group('cor'))] = e[5]
        return grupos


def nome_palette(pasta, classe, sexo, cor, traje):
    sufixo = '_' + traje.split('_')[1] if traje else ''
    return BS.join([pasta, '%s_%s_%d%s.pal' % (classe, sexo, cor, sufixo)])


def nome_sprite(raca, traje, classe, sexo):
    sufixo = '_' + traje.split('_')[1] if traje else ''
    partes = ['data', 'sprite', raca, TRONCO, sexo]
    if traje:
        partes.append(traje)
    partes.append('%s_%s%s.spr' % (APELIDO_SPRITE.get(classe.lower(), classe), sexo, sufixo))
    return BS.join(partes)


def caminho_disco(nome):
    """Onde o cliente vai procurar este nome do GRF, nesta maquina."""
    return os.path.join(CLIENTE.decode('mbcs'), nome.decode('mbcs'))


def legivel(nome):
    return nome.decode('cp949', 'replace')


# Romanizacao revisada, so para batizar arquivo de previa - 기사 vira gisa.
_INI = ['g', 'kk', 'n', 'd', 'tt', 'r', 'm', 'b', 'pp', 's', 'ss', '', 'j', 'jj', 'ch', 'k', 't', 'p', 'h']
_MED = ['a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'oe', 'yo', 'u', 'wo', 'we', 'wi', 'yu', 'eu', 'ui', 'i']
_FIM = ['', 'k', 'k', 'k', 'n', 'n', 'n', 't', 'l', 'k', 'm', 'l', 'l', 'l', 'l', 'l', 'm', 'p', 'l', 't', 't', 'ng', 't', 't', 'k', 't', 'p', 't']


def romaniza(u):
    saida = []
    for ch in u:
        c = ord(ch)
        if 0xAC00 <= c <= 0xD7A3:
            c -= 0xAC00
            saida.append(_INI[c // 588] + _MED[(c % 588) // 28] + _FIM[c % 28])
        else:
            saida.append(ch)
    return u''.join(saida).encode('ascii', 'replace')


def rotulo(chave, sep=u' '):
    pasta, raca, traje, classe, sexo = chave
    r = u'%s%s%s' % (legivel(classe), sep, u'M' if sexo == HOMEM else u'F')
    if traje:
        r += sep + traje
    if raca == DORAM:
        r += sep + u'doram'
    return r


# ---------------------------------------------------------------- palette

def desempacota(dados):
    return [struct.unpack('<BBBB', dados[i * 4:i * 4 + 4]) for i in range(256)]


def empacota(pal):
    return b''.join(struct.pack('<BBBB', *c) for c in pal)


def carrega_oficiais(fontes, indices):
    oficiais = {}
    for i, nome in sorted(indices.items()):
        dados = fontes.le(nome)
        if dados is not None and len(dados) == 1024:
            oficiais[i] = desempacota(dados)
    return oficiais


def mascara_oficial(oficiais):
    """Os indices que a Gravity muda entre as cores oficiais - a roupa.

    Devolve (mascara, tem_cor): tem_cor e False quando as oficiais sao todas
    iguais a 0, isto e, roupa que a Gravity nao tinge.
    """
    base = oficiais[0]
    m = set()
    tem_cor = False
    for i, pal in oficiais.items():
        if i == 0:
            continue
        dif = set(j for j in range(1, 256) if pal[j][:3] != base[j][:3])
        if dif:
            tem_cor = True
        # retoque miudo nao e roupa: o marrom do enfeite de cabeca do
        # Arcebispo muda 7 pontos entre a 0 e a 2, e girado junto com a
        # batina viraria verde. So entra quem a Gravity trocou de verdade.
        dif = set(j for j in dif if max(abs(pal[j][c] - base[j][c]) for c in range(3)) > RETOQUE_MAXIMO)
        if 0 < len(dif) <= DIFERENCA_MAXIMA:
            m |= dif
    return sorted(m), tem_cor


def mascara_heuristica(pal, usados):
    """Tudo que os quadros usam menos pele, contorno e cinza. Para quando as
    oficiais nao servem de mascara (Renegado)."""
    m = []
    for j in sorted(usados):
        if j == 0:
            continue
        r, g, b = [c / 255.0 for c in pal[j][:3]]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        h *= 360
        if v < 0.12 or s < 0.12:
            continue
        if 8 <= h <= 45 and 0.15 <= s <= 0.65 and v > 0.5:
            continue
        m.append(j)
    return m


class Plano(object):
    """O que se sabe de uma classe/sexo antes de tingir."""

    def __init__(self, chave, oficiais, base, mascara, origem, sprite, area):
        self.chave = chave
        self.oficiais = oficiais
        self.base = base
        self.mascara = mascara
        self.origem = origem    # 'oficial' | 'heuristica', + '/pal0' se a base nao veio do sprite
        self.sprite = sprite    # bytes do .spr, ou None
        self.area = area        # indice -> pixels em todos os quadros (1 para todos sem sprite)

    def tinge(self, alvo):
        return tinge(self.base, self.mascara, alvo, self.area)


def planeja(fontes, chave, indices):
    """Plano de uma classe/sexo, ou None se a roupa nao se tinge."""
    pasta, raca, traje, classe, sexo = chave
    oficiais = carrega_oficiais(fontes, indices)
    if 0 not in oficiais:
        return None
    m, tem_cor = mascara_oficial(oficiais)
    if not tem_cor:
        return None
    spr = fontes.le(nome_sprite(raca, traje, classe, sexo))
    area = collections.Counter()
    if spr is None:
        base, origem_base = oficiais[0], '/pal0'
        area.update(range(1, 256))
    else:
        base = desempacota(spr[-1024:])
        origem_base = ''
        for w, h, px in le_spr(spr):
            area.update(px)
    if m:
        return Plano(chave, oficiais, base, m, 'oficial' + origem_base, spr, area)
    return Plano(chave, oficiais, base, mascara_heuristica(base, area), 'heuristica' + origem_base, spr, area)


def planos(fontes, grupos):
    lista = []
    for chave in sorted(grupos):
        p = planeja(fontes, chave, grupos[chave])
        if p is not None:
            lista.append(p)
    return lista


def dominante(pal, m, area):
    """Matiz dominante (graus) dos indices COM cor da roupa, pesado por
    AREA x s x v; None se a roupa inteira e cinza/branca.

    A area e o que faz o dominante ser o que o olho ve: a batina do
    Arcebispo e lavanda a 0.21 de saturacao em meia duzia de indices que
    cobrem o sprite inteiro, e sem a area o dominante vai para o detalhe
    saturado de dez pixels - e a batina gira para um tom e o detalhe para
    outro."""
    x = y = 0.0
    for j in m:
        r, g, b = [c / 255.0 for c in pal[j][:3]]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if s < SATURACAO_CINZA:
            continue
        w = area.get(j, 0) * s * v
        x += w * math.cos(h * 2 * math.pi)
        y += w * math.sin(h * 2 * math.pi)
    if x == 0.0 and y == 0.0:
        return None
    return math.degrees(math.atan2(y, x)) % 360.0


def tinge(pal, m, alvo, area):
    """Uma cor nova a partir da base e da mascara.

    Indice COM cor gira junto com o dominante (mantem o tom relativo do
    detalhe); indice SEM cor (branco, cinza) recebe o alvo direto, com um
    piso de saturacao - e o que a Gravity fez com a batina branca do
    Arcebispo, que na `_2` oficial vira vermelha inteira.
    """
    dom_h = dominante(pal, m, area)
    nova = list(pal)
    for j in m:
        r, g, b, a = pal[j]
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if 'h' in alvo:
            if s < SATURACAO_CINZA or dom_h is None:
                h = alvo['h'] / 360.0
            else:
                h = (h + (alvo['h'] - dom_h) / 360.0) % 1.0
            # o piso vale para TODO indice da mascara, e nao so para os
            # cinzas: a batina do Arcebispo e lavanda a 0.21 de saturacao,
            # e girar o matiz de um tom desses nao muda nada na tela
            s = max(s, alvo.get('smin', PISO_SATURACAO))
        s = min(1.0, s * alvo.get('s', 1.0))
        v = min(1.0, v * alvo.get('v', 1.0))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        nova[j] = (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), a)
    return nova


# ---------------------------------------------------------------- sprite

def le_spr(dados):
    """Quadros indexados de um .spr (v2.1 com RLE), sem os RGBA."""
    if dados[:2] != 'SP':
        raise Exception('nao e SPR')
    versao = ord(dados[3]) * 10 + ord(dados[2])
    p = 4
    n_idx = struct.unpack('<H', dados[p:p + 2])[0]
    p += 2
    if versao >= 20:
        p += 2
    quadros = []
    for _ in range(n_idx):
        w, h = struct.unpack('<HH', dados[p:p + 4])
        p += 4
        if versao >= 21:
            tam = struct.unpack('<H', dados[p:p + 2])[0]
            p += 2
            bruto = dados[p:p + tam]
            p += tam
            px = bytearray()
            q = 0
            while q < len(bruto):
                b = ord(bruto[q])
                q += 1
                if b == 0:
                    px.extend(b'\x00' * ord(bruto[q]))
                    q += 1
                else:
                    px.append(b)
            px.extend(b'\x00' * (w * h - len(px)))
        else:
            px = bytearray(dados[p:p + w * h])
            p += w * h
        quadros.append((w, h, px))
    return quadros


FUNDO = (40, 40, 40)


def desenha(quadro, pal, zoom):
    w, h, px = quadro
    linhas = []
    for y in range(h):
        lin = []
        for x in range(w):
            i = px[y * w + x]
            c = FUNDO if i == 0 else pal[i][:3]
            lin.append(struct.pack('3B', *c) * zoom)
        for _ in range(zoom):
            linhas.append(b''.join(lin))
    return w * zoom, h * zoom, linhas


def previa(fontes, pasta_saida, grupos, filtro):
    """Um PNG por classe/sexo: as oficiais e depois as nossas, lado a lado,
    no quadro 0 do sprite (parado, de frente)."""
    if not os.path.isdir(pasta_saida):
        os.makedirs(pasta_saida)
    zoom, vao = 2, 6
    feitos = 0
    for chave in sorted(grupos):
        r = rotulo(chave, u'_')
        # o filtro vem ANTES do plano: planejar tudo le e desenrola todo
        # sprite de corpo do GRF, e leva um minuto
        if filtro and not any(f.lower() in r.lower() or f.lower() in romaniza(r).lower() for f in filtro):
            continue
        plano = planeja(fontes, chave, grupos[chave])
        if plano is None:
            continue
        if plano.sprite is None:
            print u'  sem sprite para %s, sem previa' % r
            continue
        quadro = le_spr(plano.sprite)[0]
        pals = [(i, plano.oficiais[i]) for i in sorted(plano.oficiais)]
        pals += [(i, plano.tinge(alvo)) for i, _, alvo in CORES]
        larg = alt = 0
        blocos = []
        for i, pal in pals:
            bw, bh, linhas = desenha(quadro, pal, zoom)
            blocos.append((bw, linhas))
            larg += bw + vao
            alt = max(alt, bh)
        saida = []
        for y in range(alt):
            lin = []
            for bw, linhas in blocos:
                lin.append(linhas[y] if y < len(linhas) else struct.pack('3B', *FUNDO) * bw)
                lin.append(struct.pack('3B', *FUNDO) * vao)
            saida.append(b''.join(lin))
        # nome ASCII de proposito: o coreano nao sobrevive ao console
        nome_png = re.sub(r'[^A-Za-z0-9_]+', '_', romaniza(r)).strip('_')
        _png(os.path.join(pasta_saida, nome_png + '.png'), larg, alt, saida)
        print u'  %-40s -> %s.png  (%s, %d indices)' % (r, nome_png, plano.origem, len(plano.mascara))
        feitos += 1
    print u'%d previas em %s' % (feitos, pasta_saida)


# ---------------------------------------------------------------- comandos

def listar(fontes, grupos):
    tingiveis = 0
    heuristicas = []
    for chave in sorted(grupos):
        plano = planeja(fontes, chave, grupos[chave])
        r = rotulo(chave)
        if plano is None:
            print u'  %-44s oficiais %-26s (nao se tinge)' % (r, sorted(grupos[chave]))
            continue
        tingiveis += 1
        print u'  %-44s oficiais %-26s roupa=%3d indices (%s)' % (
            r, sorted(plano.oficiais), len(plano.mascara), plano.origem)
        if plano.origem.startswith('heuristica'):
            heuristicas.append(r)
    print u'%d classes/sexos, %d se tingem, %d por heuristica' % (len(grupos), tingiveis, len(heuristicas))
    for r in heuristicas:
        print u'  heuristica: ' + r


def aplicar(fontes, grupos, gravar):
    gravados = 0
    lista = planos(fontes, grupos)
    for plano in lista:
        pasta, raca, traje, classe, sexo = plano.chave
        for i, _, alvo in CORES:
            destino = caminho_disco(nome_palette(pasta, classe, sexo, i, traje))
            if gravar:
                d = os.path.dirname(destino)
                if not os.path.isdir(d):
                    os.makedirs(d)
                fh = open(destino, 'wb')
                fh.write(empacota(plano.tinge(alvo)))
                fh.close()
            gravados += 1
    print u'%s %d palettes, %d classes/sexos x %d cores (indices %d..%d)' % (
        u'gravadas' if gravar else u'a gravar', gravados, len(lista), len(CORES),
        PRIMEIRO_INDICE, ULTIMO_INDICE)
    if not gravar:
        print u'(ensaio; --aplicar para gravar)'


def esperados(fontes, grupos):
    for plano in planos(fontes, grupos):
        pasta, raca, traje, classe, sexo = plano.chave
        for i, _, _ in CORES:
            yield caminho_disco(nome_palette(pasta, classe, sexo, i, traje))


def conferir(fontes, grupos):
    todos = list(esperados(fontes, grupos))
    faltam = [p for p in todos if not os.path.isfile(p)]
    print u'%d de %d no disco' % (len(todos) - len(faltam), len(todos))
    for p in faltam[:10]:
        print u'  falta: ' + p
    return 1 if faltam else 0


def reverter(fontes, grupos, gravar):
    n = 0
    for p in esperados(fontes, grupos):
        if os.path.isfile(p):
            if gravar:
                os.remove(p)
            n += 1
    print u'%s %d arquivos' % (u'apagados' if gravar else u'a apagar', n)


def main():
    args = sys.argv[1:]
    comandos = ('--listar', '--previa', '--aplicar', '--conferir', '--reverter', '--ensaio')
    if not args or args[0] not in comandos:
        print __doc__
        return 2
    fontes = Fontes()
    grupos = fontes.corpos()
    if args[0] == '--listar':
        listar(fontes, grupos)
    elif args[0] == '--previa':
        filtro = []
        if '--classe' in args:
            filtro = [args[args.index('--classe') + 1].decode('mbcs')]
        previa(fontes, args[1], grupos, filtro)
    elif args[0] == '--conferir':
        return conferir(fontes, grupos)
    elif args[0] == '--reverter':
        reverter(fontes, grupos, '--aplicar' in args)
    else:
        aplicar(fontes, grupos, args[0] == '--aplicar')
    return 0


if __name__ == '__main__':
    sys.exit(main())
