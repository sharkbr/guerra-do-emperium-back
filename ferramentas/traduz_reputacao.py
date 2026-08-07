# -*- coding: utf-8 -*-
"""Poe em portugues o modal Reputation Status, e alinha cliente com servidor.

    python traduz_reputacao.py              # aplica
    python traduz_reputacao.py --verificar  # so relata, nao grava
    python traduz_reputacao.py --reverter   # apaga o override

DE ONDE VEM O TEXTO COREANO DO MODAL

    Nao vem do servidor. O `ZC_REPUTE_INFO` (clif.cpp) carrega SO `type` e
    `points` - dois inteiros por linha. O `Name:` do `db/re/reputation.yml` é
    rótulo interno do rAthena e nunca chega ao cliente.

    Os nomes que aparecem na tela sao do proprio cliente, em dois BSON dentro
    do `data.grf`:

        data\\contentdata\\repute\\reputeinfodata.bson    as reputacoes
        data\\contentdata\\repute\\reputegroupdata.bson   os grupos do combo

    O `type` do pacote e a chave do primeiro arquivo. Ou seja: o servidor diz
    "id 1 tem 250 pontos" e o cliente decide sozinho que id 1 se chama
    오크 부락 e vale ate 3000. Traduzir e mexer no lado do cliente.

POR QUE OS NOMES SAO ASCII, e nao "Vila dos Órcs"

    O BSON guarda string em UTF-8, e o cliente NAO desenha esses bytes como
    estao: ele converte para CP949 antes de mandar para a fonte. Da para
    provar pelo print - 오크 부락 chega na tela como `¿ÀÅ© ºÎ¶ô`, que sao
    exatamente os bytes CP949 de 오크 부락 lidos com a fonte cp1252 que o
    patch `AlwaysAscii` instalou.

    A codepage ANSI desta maquina e 1252 (é o assunto inteiro do
    `valida_visual.caminho_disco`), entao esse 949 e fixo do cliente, nao do
    Windows. E CP949 nao tem á, ã, ç nem ó: letra acentuada nao sobrevive a
    conversao, vira `?` ou par de bytes que a fonte cp1252 desenha como lixo.
    ASCII passa 1:1 porque CP949 e superset de ASCII.

    Por isso `_so_ascii` aborta em vez de deixar passar. Acento aqui nao daria
    erro em lugar nenhum - daria nome sujo na tela do jogador, que e o tipo de
    estrago que so aparece depois.

O QUE ELE ACRESCENTA ALEM DE TRADUZIR

    O `db/re/reputation.yml` do rAthena declara QUATRO reputacoes e o
    `reputation_group.yml` declara TRES grupos. O GRF de 2021-11-03 e mais
    velho que isso e so conhece tres reputacoes e dois grupos - falta Isgard
    nos dois. Sem a entrada, o servidor manda `type=4` e o cliente nao tem o
    que desenhar.

    Isgard entra como `VISIBLE_EXIST`, nao `VISIBLE_TRUE`: so aparece depois
    que o jogador tiver ponto. Enquanto ninguem pontuar, a tela fica igual a
    de hoje em vez de ganhar uma linha morta.

COMO ELE GRAVA, e por que nao toca no GRF

    Grava em `cliente\\data\\contentdata\\repute\\`, e o patch
    `DataFolderFirst` (esta no `GuerraDoEmperium.epi`) faz o disco vencer o
    GRF. `--reverter` apaga os dois arquivos e o cliente volta ao coreano.

    A base e SEMPRE relida do GRF, nunca do override - a mesma regra do
    `estende_accessoryid.py`. Rodar duas vezes da o mesmo arquivo, e um erro
    na tabela abaixo nao pode se acumular sobre si mesmo.

    Antes de gravar um byte, dois round-trips: o BSON do GRF tem que voltar
    IDENTICO ao passar pelo `bson.py`, e o arquivo gerado tem que reler igual
    ao que se pretendia escrever. BSON e formato com tamanho embutido: um
    campo mal medido nao da erro aqui, da arquivo que o cliente descarta
    calado e modal vazio.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bson
from bson import Arr, Doc
from grf import Grf

CLIENTE = r'C:\GuerraDoEmperium\cliente'
GRF = os.path.join(CLIENTE, 'data.grf')
DESTINO = os.path.join(CLIENTE, 'data', 'contentdata', 'repute')
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Os TRES bancos, na ordem em que o `Footer: Imports:` os encadeia: o do
# rAthena, o do gerador e o nosso. O nosso e `db/guerra/` e nao `db/import/`
# porque o .gitignore do rAthena ignora /db/import inteiro.
REP_YML = [os.path.join(_RAIZ, 'rathena', 'db', 're', 'reputation.yml'),
           os.path.join(_RAIZ, 'rathena', 'db', 'import', 'reputation.yml'),
           os.path.join(_RAIZ, 'rathena', 'db', 'guerra', 'reputation.yml')]

INFO = 'data/contentdata/repute/reputeinfodata.bson'
GRUPO = 'data/contentdata/repute/reputegroupdata.bson'

# id -> (nome em portugues, coreano que o GRF DEVE ter nessa entrada).
#
# O segundo termo e trava, nao documentacao: se um dia a base mudar de GRF, a
# ferramenta para em vez de colar "Vila dos Orcs" em cima de outra coisa.
# Escrito como escape unicode porque este arquivo e UTF-8 e o coreano cru aqui
# nao sobrevive a leitura casual.
NOMES_REP = {
    1: ('Vila dos Orcs',            u'\uc624\ud06c \ubd80\ub77d'),
    2: ('Vila dos Goblins',         u'\uace0\ube14\ub9b0 \ubd80\ub77d'),
    3: ('Vila dos Lobos Cinzentos', u'\ud68c\uc0c9\ub291\ub300 \ub9c8\uc744'),
}
NOMES_GRUPO = {
    1: ('Amigos Monstruosos', u'\ub9c8\ubb3c \uce5c\uad6c\ub4e4'),
    2: ('Arunafeltz',         u'\uc544\ub8e8\ub098\ud3a0\uce20'),
}

# O que o GRF de 2021 nao tem. O id 4 e do proprio rAthena (`db/re/`); o 5 e
# NOSSO, e o outro lado dele esta em db/guerra/reputation.yml e em
# npc/guerra/honra_de_combate.txt - os tres precisam do mesmo Id.
#
# O 5 e VISIBLE_TRUE, e nao VISIBLE_EXIST como o 4, porque a pontuacao dele
# fica NEGATIVA (quem morre na arena perde ponto). O print de 2026-08-06
# provou que VISIBLE_EXIST some com o valor zerado - das tres entradas do GRF
# so as duas VISIBLE_TRUE apareceram -, e o comentario coreano do arquivo diz
# que ele mostra "quando o valor e 0 ou mais". Com jogador em -3, sumiria.
#
# (id, nome, Invisible, MaxPoint_Negative, MaxPoint_Positive)
NOVAS_REP = [(4, 'Isgard', 'VISIBLE_EXIST', 3000, 3000),
             (5, 'Honra de Combate', 'VISIBLE_TRUE', 10, 3000)]
# (id, ID de script, nome, reputacoes do grupo)
NOVOS_GRUPOS = [(3, 'Isgard', 'Isgard', [4]),
                (4, 'ArenaPrt', 'Arena de Prontera', [5])]

# Os `// ...` sao chaves de comentario dentro do proprio BSON - o cliente le
# `reputeInfo`/`ReputeGroup` pelo nome e ignora o resto. Ficam em portugues
# porque sao a unica documentacao que acompanha o arquivo gravado.
COMENTARIOS_INFO = [
    '// Gerado por ferramentas/traduz_reputacao.py -- NAO editar a mao.',
    '// Vence o GRF pelo DataFolderFirst; apagar esta pasta reverte.',
    '// Chave = o `type` do pacote ZC_REPUTE_INFO = o `Id:` do reputation.yml.',
    '// Name              : nome mostrado no modal. SO ASCII (o cliente converte para CP949).',
    '// Invisible         : VISIBLE_TRUE sempre / VISIBLE_EXIST so com ponto / VISIBLE_FALSE nunca.',
    '// MaxPoint_Positive : teto positivo; a barra do modal mostra um terco dele por vez.',
    '// MaxPoint_Negative : teto negativo.',
]
COMENTARIOS_GRUPO = [
    '// Gerado por ferramentas/traduz_reputacao.py -- NAO editar a mao.',
    '// Vence o GRF pelo DataFolderFirst; apagar esta pasta reverte.',
    '// Chave       : ordem de exibicao no combo do modal.',
    '// ID          : identificador de script (o ScriptName: do reputation_group.yml).',
    '// Name        : nome mostrado no combo. SO ASCII.',
    '// ReputeList  : os ids de reputeinfodata.bson que caem neste grupo.',
]


def _so_ascii(texto, onde):
    try:
        texto.decode('ascii')
    except UnicodeDecodeError:
        raise ValueError(
            '%s: %r tem byte fora do ASCII. O cliente converte o BSON para '
            'CP949 antes de desenhar, e la nao existe letra acentuada latina '
            '- o nome chegaria sujo na tela. Ver o cabecalho deste arquivo.'
            % (onde, texto))
    return texto


def _comentarios(linhas):
    return [(_so_ascii(l, 'comentario'), 0) for l in linhas]


def traduz(base, chave_raiz, nomes, comentarios):
    """A base do GRF com os nomes trocados. Nao acrescenta nem remove entrada.

    Levanta se um id da tabela nao existir na base, ou se o coreano que ele
    diz esperar nao for o que esta la.
    """
    entradas = base.get(chave_raiz)
    if entradas is None:
        raise ValueError('o BSON do GRF nao tem `%s`' % chave_raiz)
    novo = Doc(_comentarios(comentarios))
    saida = Doc()
    for chave, entrada in entradas:
        try:
            ident = int(chave)
        except ValueError:
            raise ValueError('chave %r nao e numero em `%s`'
                             % (chave, chave_raiz))
        if ident not in nomes:
            raise ValueError(
                'a entrada %d existe no GRF e nao esta na tabela deste script '
                '- traduzir parcialmente deixaria coreano na tela sem aviso.'
                % ident)
        pt, kr = nomes[ident]
        atual = entrada.get('Name')
        if atual != kr.encode('utf-8'):
            raise ValueError(
                'a entrada %d do GRF nao e a esperada: o arquivo diz %r e a '
                'tabela deste script esperava outro nome. Base trocada?'
                % (ident, atual))
        copia = Doc(entrada)
        copia.set('Name', _so_ascii(pt, 'reputacao %d' % ident))
        saida.append((chave, copia))
    novo.append((chave_raiz, saida))
    return novo


def acrescenta_rep(doc, novas):
    entradas = doc.get('reputeInfo')
    existentes = set(k for k, _ in entradas)
    for ident, nome, invisivel, neg, pos in novas:
        chave = str(ident)
        if chave in existentes:
            raise ValueError('reputacao %d ja existe na base do GRF' % ident)
        entradas.append((chave, Doc([
            ('Invisible', invisivel),
            ('MaxPoint_Negative', neg),
            ('MaxPoint_Positive', pos),
            ('Name', _so_ascii(nome, 'reputacao nova %d' % ident)),
        ])))
    return doc


def acrescenta_grupo(doc, novos):
    entradas = doc.get('ReputeGroup')
    existentes = set(k for k, _ in entradas)
    for ident, script, nome, lista in novos:
        chave = str(ident)
        if chave in existentes:
            raise ValueError('grupo %d ja existe na base do GRF' % ident)
        entradas.append((chave, Doc([
            ('ID', _so_ascii(script, 'ID de grupo %d' % ident)),
            ('Name', _so_ascii(nome, 'grupo novo %d' % ident)),
            ('ReputeList', Arr(lista)),
        ])))
    return doc


def ids_do_servidor():
    """Os `Id:` que o rAthena vai mandar, lidos dos reputation.yml que ele le.

    Regex, e nao um parser: nao ha PyYAML neste Python 2.7, e o que se quer
    daqui e uma conferencia de conjunto, nao os dados.
    """
    ids = {}
    for caminho in REP_YML:
        if not os.path.exists(caminho):
            continue
        texto = open(caminho, 'rb').read()
        for bloco in re.finditer(
                r'^  - Id:\s*(\d+)\s*$\n(?:^ {4}\S.*$\n)*', texto, re.M):
            ident = int(bloco.group(1))
            nome = re.search(r'^    Name:\s*(.+?)\s*$', bloco.group(0), re.M)
            ids[ident] = nome.group(1) if nome else '?'
    return ids


def confere_com_servidor(doc):
    """Relata id que so um dos lados conhece. Relata, nao aborta."""
    servidor = ids_do_servidor()
    cliente = set(int(k) for k, _ in doc.get('reputeInfo'))
    if not servidor:
        print '  [!] nao consegui ler nenhum Id: dos reputation.yml'
        return
    for ident in sorted(servidor):
        marca = 'ok ' if ident in cliente else '[!]'
        print '  %s servidor id %d (%s)%s' % (
            marca, ident, servidor[ident],
            '' if ident in cliente else '  - o cliente nao tem entrada, a '
                                        'linha nao apareceria no modal')
    for ident in sorted(cliente - set(servidor)):
        print ('  [!] cliente id %d nao existe no reputation.yml - linha que '
               'nunca recebe ponto' % ident)


def main(argv):
    if '--reverter' in argv:
        achou = False
        for nome in ('reputeinfodata.bson', 'reputegroupdata.bson'):
            caminho = os.path.join(DESTINO, nome)
            if os.path.exists(caminho):
                os.remove(caminho)
                achou = True
                print 'apagado  %s' % caminho
        print ('o cliente volta a ler os BSON do GRF (coreano).' if achou
               else 'nao havia override para apagar.')
        return 0

    grf = Grf(GRF)
    base_info, base_grupo = grf.read(INFO), grf.read(GRUPO)

    # Round-trip da BASE: prova que `bson.py` escreve o que le. Sem isto, um
    # arquivo gerado que o cliente rejeitasse nao teria como ser distinguido
    # de uma tabela errada aqui em cima.
    for rotulo, cru in (('reputeinfodata', base_info),
                        ('reputegroupdata', base_grupo)):
        if bson.dumps(bson.loads(cru)) != cru:
            print '[!] round-trip da base falhou em %s.bson - nao gravo' % rotulo
            return 1
    print 'base (nosso GRF): round-trip OK nos dois arquivos'

    info = traduz(bson.loads(base_info), 'reputeInfo',
                  NOMES_REP, COMENTARIOS_INFO)
    grupo = traduz(bson.loads(base_grupo), 'ReputeGroup',
                   NOMES_GRUPO, COMENTARIOS_GRUPO)
    acrescenta_rep(info, NOVAS_REP)
    acrescenta_grupo(grupo, NOVOS_GRUPOS)

    print '\nreputacoes:'
    for chave, entrada in info.get('reputeInfo'):
        print '  %-3s %-26s %s' % (chave, entrada.get('Name'),
                                   entrada.get('Invisible'))
    print 'grupos:'
    for chave, entrada in grupo.get('ReputeGroup'):
        print '  %-3s %-26s %s -> %s' % (
            chave, entrada.get('Name'), entrada.get('ID'),
            ', '.join(str(i) for i in entrada.get('ReputeList')))

    print '\nconferencia com o rAthena:'
    confere_com_servidor(info)

    saidas = []
    for nome, doc in (('reputeinfodata.bson', info),
                      ('reputegroupdata.bson', grupo)):
        cru = bson.dumps(doc)
        if bson.dumps(bson.loads(cru)) != cru:
            print '\n[!] round-trip do arquivo gerado falhou em %s' % nome
            return 1
        saidas.append((nome, cru))
    print '\nround-trip do gerado: OK nos dois arquivos'

    if '--verificar' in argv:
        print '\n--verificar: nada gravado.'
        return 0

    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)
    for nome, cru in saidas:
        caminho = os.path.join(DESTINO, nome)
        with open(caminho, 'wb') as fp:
            fp.write(cru)
        print 'gravado  %s  (%d bytes)' % (caminho, len(cru))
    print '\nO cliente so le isto na INICIALIZACAO - fechar e reabrir.'
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
