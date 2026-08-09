# -*- coding: cp1252 -*-
u"""Preenche as linhas `+` de um catalogo do traduz_npcs.py, em cp1252.

    python preenche_catalogo.py --pendentes <grupo> [saida.txt]
    python preenche_catalogo.py --gravar <grupo> <traducoes.py>

E o par de mao dupla do `traduz_npcs.py`: ele extrai e aplica, este aqui
cuida do meio - tirar do catalogo o que falta traduzir, e devolver a
traducao sem destruir o acento.

=========================================================================
POR QUE ELE EXISTE, JA QUE DA PARA EDITAR O .cat A MAO
=========================================================================

Porque **escrever e o passo perigoso, nao ler** (CLAUDE.md secao 4.1). O
`.cat` e cp1252; todo editor e toda ferramenta de edicao gravam UTF-8 por
padrao, e o estrago e calado - o acento vira `\xef\xbf\xbd` e o byte
original ja nao esta la. Um catalogo de instancia tem 300 a 700 pares e
umas 150 linhas acentuadas: editar isso a mao e apostar 150 vezes seguidas.

Aqui a traducao entra por um modulo Python em UTF-8 e sai em cp1252, com
tres travas fatais no caminho.

=========================================================================
O CICLO, POR GRUPO
=========================================================================

    python traduz_npcs.py --extrair <grupo>          # SEMPRE antes (secao 4.13)
    python preenche_catalogo.py --pendentes <grupo>  # o que falta
    # ... escrever o t_<grupo>.py ...
    python preenche_catalogo.py --gravar <grupo> t_<grupo>.py
    python traduz_npcs.py --aplicar <grupo> --verificar
    python traduz_npcs.py --aplicar <grupo>

=========================================================================
O FORMATO DA TRADUCAO, E POR QUE NAO E TSV
=========================================================================

Um modulo Python em UTF-8 com um dicionario indice -> texto:

    # -*- coding: utf-8 -*-
    TRAD = {
        2: u"O aventureiro ",
        3: u" do grupo ",
    }

O indice e o numero que o `--pendentes` imprimiu, do MESMO catalogo e na
MESMA ordem. Indice ausente fica em branco, e branco quer dizer "deixa em
ingles" - e assim que se marca nome de mapa, label e nome unico de NPC.

**Nao e TSV de proposito:** metade dos textos de instancia sao fragmentos de
frase montada com `+`, e o espaco no inicio e no fim deles e significativo -
` of the party ` vira ` do grupo `. Num TSV esse espaco se perde no primeiro
editor que apara linha, e a frase sai grudada em jogo sem nada denunciar.
Entre aspas ele e visivel e sobrevive.

Pelo mesmo motivo a trava e `if not trad`, e nao `if not trad.strip()`:
traducao de UM ESPACO e legitima. No FacewormsNest o script monta
`n + " unbroken " + ("eggs"|"egg")`, e em portugues o adjetivo muda de lado -
o fragmento do meio vira " " e o substantivo leva o adjetivo junto ("ovos
intactos"). Filtrar por `.strip()` deixava ` unbroken ` em ingles no meio da
frase.

=========================================================================
AS TRES TRAVAS
=========================================================================

 1. **Recusa caractere fora do cp1252.** Aspa curva, travessao longo e
    reticencias de um byte so passam batido num editor e viram `?` no jogo.
 2. **Recusa `\xef\xbf\xbd`** (U+FFFD) em qualquer ponto do resultado - o
    sintoma de cp1252 salvo como UTF-8, que NAO e reversivel.
 3. **Recusa aspa dupla dentro da traducao.** O `.cat` delimita com aspas e
    o script do rAthena tambem; uma a mais faz o parser engolir o resto do
    arquivo, e o erro sai na subida do servidor citando outra linha.

A gravacao troca SO o miolo da linha `+`, por fatia de bytes. Reescrever o
registro inteiro exigiria remontar o cabecalho `#:` com o contexto entre
parenteses, e inventar isso e como se perde informacao.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGOS = os.path.join(REPO, 'rathena', 'npc', 'guerra', 'traducao')

# O mesmo do traduz_npcs.py. Duplicado de proposito: importar de la traria
# junto o carregamento dos GRUPOS por glob, que le o disco inteiro.
RE_REG = re.compile(r'^#: (\S+) \([^)]*\)\r?\n- "(.*)"\r?\n\+ "(.*)"\r?$',
                    re.M)


class Erro(Exception):
    pass


def caminho(grupo):
    p = os.path.join(CATALOGOS, grupo + '.cat')
    if not os.path.exists(p):
        raise Erro('nao existe catalogo para "%s" - rode '
                   'traduz_npcs.py --extrair %s antes' % (grupo, grupo))
    return p


def pendentes(dados):
    u"""Os originais sem traducao, distintos, na ordem do catalogo.

    Distinto por TEXTO, e nao por ocorrencia: a traducao vale para todas as
    ocorrencias, e 43% do acervo e repeticao. A ordem e a de primeira
    aparicao, que e a ordem do script - o dialogo vem em sequencia, e e o
    que torna possivel traduzir uma conversa inteira sem pular de um lado
    para o outro do arquivo.
    """
    vistos = set()
    ordem = []
    for m in RE_REG.finditer(dados):
        orig, trad = m.group(2), m.group(3)
        if trad or orig in vistos:
            continue
        vistos.add(orig)
        ordem.append(orig)
    return ordem


def manda_pendentes(grupo, saida):
    dados = open(caminho(grupo), 'rb').read()
    lista = pendentes(dados)
    texto = u''.join(u'%d\t%s\n' % (i + 1, t.decode('cp1252'))
                     for i, t in enumerate(lista))
    if saida:
        fh = open(saida, 'wb')
        fh.write(texto.encode('utf-8'))
        fh.close()
        print '%s: %d textos pendentes distintos -> %s' % (grupo, len(lista),
                                                           saida)
    else:
        sys.stdout.write(texto.encode('utf-8'))
    return 0


def grava(grupo, fonte):
    cam = caminho(grupo)
    dados = open(cam, 'rb').read()
    ordem = pendentes(dados)

    espaco = {}
    execfile(fonte, espaco)
    tabela = espaco.get('TRAD')
    if tabela is None:
        raise Erro('%s nao define TRAD' % fonte)

    novas = {}
    for n, trad in tabela.items():
        i = n - 1
        if i < 0 or i >= len(ordem):
            raise Erro('indice %d fora do catalogo (%d pendentes) - o '
                       'catalogo mudou depois do --pendentes?'
                       % (n, len(ordem)))
        if not trad:
            continue
        if u'"' in trad:
            raise Erro('aspa dupla na traducao %d: %r' % (n, trad))
        try:
            b = trad.encode('cp1252')
        except UnicodeEncodeError as e:
            raise Erro('caractere fora do cp1252 na traducao %d: %r (%s)'
                       % (n, trad, e))
        if '\xef\xbf\xbd' in b:
            raise Erro('U+FFFD na traducao %d' % n)
        novas[ordem[i]] = b

    if not novas:
        print 'nada a gravar'
        return 0

    partes = []
    fim = 0
    n_troca = 0
    for m in RE_REG.finditer(dados):
        orig, trad = m.group(2), m.group(3)
        if trad or orig not in novas:
            continue
        partes.append(dados[fim:m.start(3)])
        partes.append(novas[orig])
        fim = m.end(3)
        n_troca += 1
    partes.append(dados[fim:])
    saida = ''.join(partes)

    if '\xef\xbf\xbd' in saida:
        raise Erro('U+FFFD no catalogo resultante')

    fh = open(cam, 'wb')
    fh.write(saida)
    fh.close()
    print '%s: %d textos distintos gravados, %d ocorrencias' % (
        grupo, len(novas), n_troca)
    print 'Agora: traduz_npcs.py --aplicar %s --verificar' % grupo
    return 0


def main(argv):
    if '--pendentes' in argv:
        resto = [a for a in argv if not a.startswith('--')]
        if not resto:
            raise Erro('falta o grupo')
        return manda_pendentes(resto[0], resto[1] if len(resto) > 1 else None)
    if '--gravar' in argv:
        resto = [a for a in argv if not a.startswith('--')]
        if len(resto) < 2:
            raise Erro('uso: --gravar <grupo> <traducoes.py>')
        return grava(resto[0], resto[1])
    print __doc__
    return 1


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
