# -*- coding: utf-8 -*-
"""Inventaria os modelos 3D do GRF -- o que existe para usar sem desenhar nada.

Python 2.7, como o resto de ferramentas/.

Por que existe: o mapa-catalogo montado antes tinha so os 90 modelos que Izlude
ja usa, o que servia para conferir classificacao mas nao mostra **peca nova**.
Para a tematica de destruicao interessa o acervo inteiro do GRF: se a Gravity ja
modelou parede quebrada, telhado desabado ou entulho, a temaica sai por troca de
nome de arquivo, sem desenhar nada.

**O DES nao bloqueia isto.** A tabela do GRF e zlib e o grf.py ja a le inteira,
com nome e flag de todo arquivo. E para por um modelo num mapa basta o **nome**:
o .rsw referencia por caminho e quem abre o .rsm e o cliente. So se precisaria do
DES para ler a geometria -- que nao e o caso aqui.

Uso:
    python inventario_rsm.py <data.grf> pastas [saida.md]
    python inventario_rsm.py <data.grf> ruina [saida.md]
    python inventario_rsm.py <data.grf> busca <termo-em-portugues> [saida.md]
"""

import collections
import io
import sys

from grf import Grf


BARRA = chr(92)   # a barra invertida via argv de console e uma dor; isolada aqui

# Termos coreanos que aparecem em nome de modelo. A chave e o que se procura em
# portugues; o valor sao as formas coreanas.
TERMOS = {
    u'ruina': [u'폐허', u'폐'],
    u'quebrado': [u'부서진', u'깨진', u'부러진'],
    u'desmoronado': [u'무너진', u'쓰러진'],
    u'destrocos': [u'잔해', u'파편', u'잔재'],
    u'fissura': [u'균열'],
    u'velho': [u'낡은', u'헌'],
    u'parede': [u'벽'],
    u'telhado': [u'지붕', u'기와'],
    u'pedra': [u'돌', u'바위'],
    u'tumulo': [u'무덤', u'묘'],
    u'osso': [u'뼈', u'해골'],
    u'madeira': [u'나무'],
    u'coluna': [u'기둥'],
    u'caixa': [u'상자'],
    u'barril': [u'통'],
    u'casa': [u'집', u'가옥'],
    u'loja': [u'상점'],
    u'ponte': [u'다리'],
    u'cerca': [u'울타리'],
    u'escombro': [u'더미'],
}

# Os grupos que a temaica de destruicao deveria varrer primeiro.
RUINA = [u'ruina', u'quebrado', u'desmoronado', u'destrocos', u'fissura',
         u'velho', u'tumulo', u'osso', u'escombro']


def modelos(g):
    return sorted(e[5] for k, e in g.entries.items() if k.endswith('.rsm'))


def parte_pasta(nome):
    p = nome.split(BARRA)
    return BARRA.join(p[1:-1]) if len(p) > 2 else u'(raiz)'


def u(s):
    try:
        return s.decode('cp949')
    except UnicodeDecodeError:
        return s.decode('latin-1')


def escreve(linhas, saida):
    texto = u'\n'.join(linhas) + u'\n'
    if saida:
        with io.open(saida, 'w', encoding='utf-8') as f:
            f.write(texto)
        print 'gravado %s (%d linhas)' % (saida, len(linhas))
    else:
        print texto.encode('utf-8')


def cmd_pastas(g, saida):
    ms = modelos(g)
    cont = collections.Counter(parte_pasta(n) for n in ms)
    linhas = [u'# Pastas de modelo no GRF',
              u'',
              u'`%d` modelos `.rsm` em `%d` pastas.' % (len(ms), len(cont)),
              u'',
              u'| modelos | pasta |', u'|---|---|']
    for p, c in cont.most_common():
        linhas.append(u'| %d | `%s` |' % (c, u(p)))
    escreve(linhas, saida)


def busca(g, chaves):
    ms = modelos(g)
    achados = collections.OrderedDict()
    for chave in chaves:
        for termo in TERMOS.get(chave, [chave]):
            alvo = termo.encode('cp949')
            for n in ms:
                if alvo in n:
                    achados.setdefault(n, set()).add(chave)
    return achados


def cmd_busca(g, chaves, saida, titulo):
    achados = busca(g, chaves)
    porpasta = collections.defaultdict(list)
    for n, qs in achados.items():
        porpasta[parte_pasta(n)].append((n, qs))

    linhas = [u'# %s' % titulo,
              u'',
              u'`%d` modelos, em `%d` pastas. Termos procurados: %s.'
              % (len(achados), len(porpasta),
                 u', '.join(u'**%s**' % c for c in chaves)),
              u'',
              u'A busca e por nome de arquivo, entao ela **erra nos dois '
              u'sentidos**: pega coisa que so tem a palavra no nome, e perde '
              u'modelo de ruina batizado de outro jeito. Serve para reduzir o '
              u'acervo a algo que caiba num mapa-catalogo, nao para decidir.',
              u'']
    for p in sorted(porpasta, key=lambda k: -len(porpasta[k])):
        linhas.append(u'## `%s` — %d' % (u(p), len(porpasta[p])))
        linhas.append(u'')
        for n, qs in sorted(porpasta[p]):
            linhas.append(u'- `%s` — %s'
                          % (u(n.split(BARRA)[-1]), u', '.join(sorted(qs))))
        linhas.append(u'')
    escreve(linhas, saida)


def main():
    if len(sys.argv) < 3:
        print __doc__
        return 1
    g = Grf(sys.argv[1])
    cmd = sys.argv[2]

    if cmd == 'pastas':
        cmd_pastas(g, sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == 'ruina':
        cmd_busca(g, RUINA, sys.argv[3] if len(sys.argv) > 3 else None,
                  u'Modelos com cara de ruina no GRF')
    elif cmd == 'busca':
        cmd_busca(g, [sys.argv[3].decode('utf-8')],
                  sys.argv[4] if len(sys.argv) > 4 else None,
                  u'Busca: %s' % sys.argv[3].decode('utf-8'))
    else:
        print __doc__
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
