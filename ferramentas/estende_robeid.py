# -*- coding: utf-8 -*-
"""Poe a arte de um manto num slot que ESTE cliente aceita desenhar.

    python estende_robeid.py                              # aplica e relata
    python estende_robeid.py --verificar                  # so relata
    python estende_robeid.py --reverter                   # apaga o override
    python estende_robeid.py --sonda 114=C_20th_Anniversary_Wing   # ver abaixo

O TETO DE 120, e por que este script nao "estende" mais nada

    Este cliente NAO USA slot de manto acima de 120, e a tabela nao tem nada a
    ver com isso. Medido em 2026-08-09, na tela, com estes itens:

        desenham   View 61, 73, 75, 82, 90, 99, 104, 114
        nao        View 122, 136, 148, 154, 158

    A tabela do GRF vai justamente ate 120. Antes de concluir, as tres coisas
    que poderiam explicar sozinhas foram descartadas UMA A UMA:

      - arte faltando? Nao. O Escudo de Oridecon (View 90) desenha, e a arte
        dele foi copiada na mesma rodada, pelo mesmo instala_manto.py.
      - o arquivo nao chega ao cliente? Chega. O horario de acesso dos dois
        .lub mostra que o cliente os abriu na inicializacao - e a SONDA (abaixo)
        provou na tela: reapontar o View 114 para a pasta das Asas Laureadas
        fez a Espada do General desenhar asas.
      - buraco na numeracao? Nao. A tabela foi refeita contigua de 1 a 158, o
        cliente a leu, e os View acima de 120 continuaram sem desenhar.

    Sobra o teto no proprio cliente. Levanta-lo seria patch de exe; a busca
    pela constante ficou registrada no PENDENCIAS.md e NAO foi feita - varredura
    de bytes sem desmontador so devolveu `cmp` que nao sao instrucao.

O QUE ELE FAZ ENTAO: REAPROVEITA SLOT MORTO

    Dos 120 slots deste cliente, 40 nao tem arte nenhuma - a tabela conhece o
    nome da pasta e a pasta nao existe em GRF nenhum. Esses slots ja nao
    desenham coisa alguma hoje, entao apontar um deles para a arte de um manto
    novo nao tira nada de ninguem. E o que este script faz.

    A FONTE DA VERDADE E O `db/guerra/item_db.yml`, e isto e deliberado. Quem
    decide qual manto usa qual slot e o `View:` do nosso item_db; o script LE
    de la e escreve a tabela do cliente para combinar. Nao ha lista de-para
    escrita aqui, e nao pode haver: seria a metade-no-cliente do CLAUDE.md
    secao 9 outra vez - duas listas, uma em cada lado, divergindo sem erro.
    Com uma fonte so, rodar de novo nao muda nada e nao ha como divergir.

A SONDA - "este arquivo chega a tela?", sem depender do efeito procurado

    `--sonda <view>=<pasta>` reaponta um View que JA FUNCIONA para a pasta de
    outro manto, bem diferente. Serve para uma pergunta so, e e a pergunta que
    tentativa e erro nao responde: o cliente esta mesmo montando a tabela a
    partir DESTE arquivo, ou le o arquivo e usa a do GRF?

        python estende_robeid.py --sonda 114=C_20th_Anniversary_Wing

    O View 114 e a Espada do General, que desenha hoje. Depois de reabrir o
    cliente, equipar a Espada:

        aparecem ASAS  -> o override manda; a tabela sai daqui
        aparece a ESPADA -> o override e lido e IGNORADO; o GRF vence

    E a mesma licao do `ajusta_tamanho_fonte.py` (CLAUDE.md secao 5): antes de
    calibrar valor, provar que o patch chega a tela com uma marca que nao
    dependa do efeito procurado. Rodar de novo sem `--sonda` desfaz.

IRMAO DO `estende_accessoryid.py`, do lado do manto. E a metade que faltava

    Manto tem duas camadas a mais que chapeu, e ate 2026-08-09 so uma tinha
    ferramenta:

        camada            chapeu                     manto
        slot de visual    accessoryid.lub  ........  spriterobeid.lub
                          accname.lub               spriterobename.lub
        estende o slot    estende_accessoryid.py     ESTE ARQUIVO
        arte              instala_visual.py          instala_manto.py

    A nossa `spriterobeid.lub` de 2021-11-03 conhece 120 slots; a do bRO
    conhece 258. Este script cuida do NOME DA PASTA de cada slot; o
    `instala_manto.py` traz os arquivos. Os dois juntos e que curam o manto.

TRES GLOBAIS, NAO DOIS - e o terceiro e uma LISTA

    Do lado do chapeu sao duas tabelas em dois arquivos. Aqui sao tres globais
    em dois arquivos, e a forma do terceiro e diferente:

        spriterobeid.lub     SPRITE_ROBE_IDs     {const = view}
        spriterobename.lub   RobeNameTable       {[SPRITE_ROBE_IDs.const] = "pasta"}
                             RobeNameTable_Eng   {[SPRITE_ROBE_IDs.const] = "pasta"}
                             RobeTopLayer        { SPRITE_ROBE_IDs.const, ... }

    `RobeNameTable` e quem da o nome da PASTA de sprite; nas entradas velhas
    ela vem em coreano (CP949) e nas novas em ASCII. A `_Eng` e a lista
    paralela em ingles. `RobeTopLayer` NAO e mapa: e um vetor dos mantos que o
    cliente desenha POR CIMA do personagem - mochila, bolsa, asa que passa na
    frente. Sao 38 dos nossos 120, e 151 dos 258 do bRO.

    Reescrever o arquivo sem o `RobeTopLayer` compila, sobe e nao da erro
    nenhum: os 38 mantos que hoje desenham na frente passariam a desenhar
    atras, calados. Por isso ele e preservado inteiro, e um manto novo entra
    nele se, e so se, o bRO tambem o poe la.

COMO ELE GRAVA, e por que nao toca no GRF

    Grava Lua em TEXTO em `cliente\\data\\luafiles514\\lua files\\datainfo\\`.
    O cliente le `.lub` texto e bytecode indiferentemente, e o
    `DataFolderFirst` faz o disco vencer o GRF. Apagar os dois arquivos
    reverte (`--reverter` faz isso), e o GRF nunca e aberto para escrita.

A REGRA QUE MANTEM ISTO SEGURO: a base e SEMPRE o nosso GRF

    O override e derivado, nunca acumulado sobre si mesmo. A cada rodada a base
    e relida do GRF e o reaproveitamento e reaplicado por cima a partir do
    item_db, de modo que as 120 originais nao podem derivar. O arquivo do disco
    NAO e lido para recuperar nada: ele e refeito do zero toda vez. Isso e o que
    faz `--reverter` e "tirar o `View:` do item_db" darem no mesmo.

    Todo reaproveitamento passa por TRES travas, e as tres abortam:

      - slot doador ACIMA de 120                -> este cliente nao o desenha
      - slot doador que TEM arte neste cliente  -> reaproveitar apagaria um
                                                   manto que hoje funciona
      - pasta de destino que nao existe em GRF
        nem no disco                            -> viraria caixa de erro

    A segunda e a que protege o acervo: 80 dos 120 slots tem arte e sao
    intocaveis; os outros 40 ja nao desenham nada e sao os candidatos.

    E antes de gravar um byte, o texto gerado e relido e comparado global a
    global com o que deveria conter. Mesmo criterio de round-trip do
    `estende_accessoryid.py`: layout errado nao da erro, da arquivo corrompido
    - e aqui o arquivo corrompido levaria junto os 120 mantos que funcionam.

O QUE JA FOI TENTADO E NAO ERA - para ninguem repetir

    **Buraco na numeracao.** A tabela do GRF vai de 1 a 120 sem faltar numero;
    pedir o View 154 sozinho deixava 29 vazios no meio. A tabela foi refeita
    contigua de 1 a 158, o cliente a leu, e nada mudou. Nao era.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
import instala_manto as im
import luadis
from grf import Grf

ROBE_ID = im.ROBE_ID
ROBE_NOME = im.ROBE_NOME

# Os nomes dos globais, exatamente como estao no bytecode do cliente. Trocar
# qualquer um por outro deixa a tabela orfa: o cliente le o arquivo, nao acha o
# global que procura, e desenha nada - sem erro.
G_ID = 'SPRITE_ROBE_IDs'
G_NOME = 'RobeNameTable'
G_ENG = 'RobeNameTable_Eng'
G_TOPO = 'RobeTopLayer'

# O maior slot de manto que ESTE cliente desenha. Nao e o tamanho da tabela: a
# tabela foi levada a 158 entradas contiguas, o cliente a leu, e slot acima
# deste continuou sem desenhar. Medido na tela em 2026-08-09 - ver a docstring.
TETO = 120

# `str`, nao `unicode`, pela mesma razao do estende_accessoryid.py: o corpo
# carrega nome de pasta em CP949 ja escapado em `\\ddd`, e um cabecalho unicode
# promoveria a concatenacao inteira.
CABECALHO = """\
-- Gerado por ferramentas/estende_robeid.py -- NAO editar a mao.
--
-- Base: %s do data.grf deste cliente (%d entradas de 2021-11-03).
-- Acrescentado por nos: %d entrada(s).
--
-- Este arquivo vence o GRF pelo DataFolderFirst. Apagar reverte.
"""


def _escapa(s):
    """Bytes -> literal Lua seguro.

    Todo byte fora do ASCII imprimivel vira `\\ddd` decimal. Nao e capricho: os
    nomes de pasta velhos estao em CP949, e la o byte de continuacao pode ser
    `\\` (0x5C) ou `"` (0x22). Gravar CP949 cru num literal Lua produz escape
    acidental, e o erro so aparece no cliente.
    """
    fora = []
    for c in s:
        b = ord(c)
        if c in ('\\', '"') or b < 0x20 or b > 0x7e:
            fora.append('\\%d' % b)
        else:
            fora.append(c)
    return ''.join(fora)


# ------------------------------------------------------------ leitura do GRF

def _globais(f):
    """[(nome do global, [(chave, valor)], [valor de lista])] de um bytecode.

    O `vv.tabela_lua` devolve os pares de TODAS as tabelas do arquivo numa
    lista so, o que basta quando ha um global. Aqui ha tres, dois deles com as
    MESMAS chaves - um `dict()` por cima colapsaria a `RobeNameTable` na
    `_Eng`, calado. Entao o corte e feito no `SETGLOBAL`, que e onde o Lua 5.1
    fecha cada construtor.

    O `SETLIST` e o que distingue vetor de mapa, e e por ele que o
    `RobeTopLayer` sai como lista em vez de sair vazio.
    """
    saida = []
    regs = {}
    pares, lista = [], []
    for ins in f['code']:
        op = ins & 0x3f
        nome = luadis.OPNAMES[op] if op < len(luadis.OPNAMES) else ''
        A = (ins >> 6) & 0xff
        C = (ins >> 14) & 0x1ff
        B = (ins >> 23) & 0x1ff
        Bx = (ins >> 14) & 0x3ffff
        if nome == 'LOADK':
            regs[A] = f['k'][Bx]
        elif nome == 'SETTABLE':
            kb = f['k'][B - 256] if B >= 256 else regs.get(B)
            kc = f['k'][C - 256] if C >= 256 else regs.get(C)
            pares.append((kb, kc))
        elif nome == 'GETTABLE':
            regs[A] = f['k'][C - 256] if C >= 256 else regs.get(C)
        elif nome == 'SETLIST':
            lista.extend(regs.get(A + i) for i in range(1, B + 1))
        elif nome == 'SETGLOBAL':
            saida.append((f['k'][Bx], pares, lista))
            pares, lista = [], []
            regs.pop(A, None)
        elif nome in ('GETGLOBAL', 'MOVE', 'NEWTABLE', 'CALL'):
            regs.pop(A, None)
    return saida


def tabelas_do_grf(caminho):
    """(ids, nomes, eng, topo) de uma GRF.

    `ids` e {const: view}; `nomes` e `eng` sao {const: pasta}; `topo` e a lista
    de constantes do `RobeTopLayer`, na ordem original.
    """
    grf = Grf(caminho)
    ler = lambda n: dict(((g, (p, l)) for g, p, l in _globais(
        luadis.read_func(luadis.R(grf.read(n), 12)))))
    tid = ler(ROBE_ID)
    tnm = ler(ROBE_NOME)
    ids = dict((k, int(v)) for k, v in tid[G_ID][0] if isinstance(k, str))
    nomes = dict((k, v) for k, v in tnm[G_NOME][0] if isinstance(k, str))
    eng = dict((k, v) for k, v in tnm[G_ENG][0] if isinstance(k, str))
    topo = [c for c in tnm[G_TOPO][1] if isinstance(c, str)]
    return ids, nomes, eng, topo


# --------------------------------------------------------- leitura do override

# O `vv._pares_de_texto` esta preso ao prefixo `[ACCESSORY_IDs.`, entao nao
# serve aqui. O formato continua sendo fechado e gerado por nos, logo regex
# basta - mas ela precisa saber em qual global esta, porque `RobeNameTable` e
# `RobeNameTable_Eng` tem chave igual e valor diferente.
_ABRE = re.compile(r'(?m)^(\w+)\s*=\s*\{')
_PAR = re.compile(r'(?m)^\s*(?:\[' + G_ID + r'\.)?([A-Za-z_]\w*)\]?\s*=\s*'
                  r'(?:(-?\d+)|"((?:[^"\\]|\\.)*)")\s*,')
_ITEM = re.compile(r'(?m)^\s*' + G_ID + r'\.([A-Za-z_]\w*)\s*,')


def _corpos(texto):
    """{nome do global: corpo entre as chaves}."""
    fora = {}
    marcas = list(_ABRE.finditer(texto))
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        fora[m.group(1)] = texto[m.end():fim]
    return fora


def _pares(corpo):
    saida = []
    for m in _PAR.finditer(corpo):
        const, num, txt = m.group(1), m.group(2), m.group(3)
        saida.append((const, int(num) if num is not None
                      else vv._desescapa(txt)))
    return saida


def tabelas_do_override():
    """O que o override tem hoje, ou (None, None, None, None) se nao existe."""
    caminhos = [vv.caminho_disco(c) for c in (ROBE_ID, ROBE_NOME)]
    if not all(os.path.exists(c) for c in caminhos):
        return None, None, None, None
    c_id = _corpos(open(caminhos[0], 'rb').read())
    c_nm = _corpos(open(caminhos[1], 'rb').read())
    ids = dict(_pares(c_id.get(G_ID, '')))
    nomes = dict(_pares(c_nm.get(G_NOME, '')))
    eng = dict(_pares(c_nm.get(G_ENG, '')))
    topo = _ITEM.findall(c_nm.get(G_TOPO, ''))
    return ids, nomes, eng, topo


# ------------------------------------------------------------------ montagem

def monta(base, extras):
    """As quatro tabelas finais = a base do GRF + os extras, com as travas.

    `base` e (ids, nomes, eng, topo); `extras` e {const: (view, nome, eng,
    topo)}. Devolve o mesmo formato de `base` ou levanta.
    """
    base_ids, base_nomes, base_eng, base_topo = base
    ids, nomes, eng = dict(base_ids), dict(base_nomes), dict(base_eng)
    topo = list(base_topo)
    por_view = dict((v, k) for k, v in base_ids.items())
    for const in sorted(extras, key=lambda c: extras[c][0]):
        view, nm, en, no_topo = extras[const]
        if const in base_ids and base_ids[const] != view:
            raise ValueError(
                '%s ja existe neste cliente com View %d, e a fonte diz %d. '
                'Mesma armadilha do skillid.lub: constante igual com id '
                'diferente. Nao da para acrescentar sem decidir quem manda.'
                % (const, base_ids[const], view))
        if view in por_view and por_view[view] != const:
            raise ValueError(
                'View %d ja e de %s neste cliente, e a fonte quer dar a %s. '
                'Sobrescrever trocaria a arte de um manto que hoje funciona.'
                % (view, por_view[view], const))
        ids[const] = view
        if nm is not None:
            nomes[const] = nm
        if en is not None:
            eng[const] = en
        if no_topo and const not in topo:
            topo.append(const)
    return ids, nomes, eng, topo


def texto(tabelas, n_extras):
    """Os dois arquivos em Lua texto, na ordem do View (diff legivel)."""
    ids, nomes, eng, topo = tabelas
    ordem = sorted(ids, key=lambda c: (ids[c], c))

    def bloco(glob, linhas):
        return '%s = {\n' % glob + ''.join('\t%s\n' % l for l in linhas) + '}\n'

    txt_id = (CABECALHO % ('spriterobeid.lub', len(ids) - n_extras, n_extras)
              + bloco(G_ID, ['%s = %d,' % (c, ids[c]) for c in ordem]))
    # O `RobeTopLayer` sai na ordem ORIGINAL do cliente, nao na do View: e
    # vetor, e reordenar vetor e mudanca de conteudo. Os nossos vao no fim.
    txt_nome = (
        CABECALHO % ('spriterobename.lub', len(ids) - n_extras, n_extras)
        + bloco(G_NOME, ['[%s.%s] = "%s",' % (G_ID, c, _escapa(nomes[c]))
                         for c in ordem if c in nomes])
        + bloco(G_ENG, ['[%s.%s] = "%s",' % (G_ID, c, _escapa(eng[c]))
                        for c in ordem if c in eng])
        + bloco(G_TOPO, ['%s.%s,' % (G_ID, c) for c in topo]))
    return txt_id, txt_nome


def confere(txt_id, txt_nome, tabelas):
    """Round-trip: reler o texto gerado tem que devolver exatamente o esperado.

    Sem isto nao ha como saber se um nome de pasta CP949 sobreviveu ao escape -
    e um nome errado nao da erro em lugar nenhum, so faz o cliente procurar uma
    pasta que nao existe.
    """
    ids, nomes, eng, topo = tabelas
    c_id, c_nm = _corpos(txt_id), _corpos(txt_nome)
    volta = (dict(_pares(c_id[G_ID])), dict(_pares(c_nm[G_NOME])),
             dict(_pares(c_nm[G_ENG])), _ITEM.findall(c_nm[G_TOPO]))
    esperado = (ids,
                dict((k, v) for k, v in nomes.items() if k in ids),
                dict((k, v) for k, v in eng.items() if k in ids),
                topo)
    for i, rot in enumerate((G_ID, G_NOME, G_ENG, G_TOPO)):
        if volta[i] != esperado[i]:
            raise ValueError('round-trip falhou em %s (%d != %d)'
                             % (rot, len(volta[i]), len(esperado[i])))


# --------------------------------------------------------------------- alvos

def tem_arte(nome_pasta, grfs):
    u"""Existe pasta de sprite com esse nome em algum dos GRF, ou no disco?

    A TERCEIRA TRAVA. Manto sem entrada de tabela e invisivel e calado; com
    entrada e sem arte, e `Cannot find File` modal. Gravar sem conferir troca
    uma coisa ruim por outra pior, e foi exatamente o estrago que os tres
    sufixos de 2026-08-05 fizeram do lado do chapeu.
    """
    alvo = (im.RAIZ_MANTO + nome_pasta).lower() + chr(92)
    for g in grfs:
        for e in g.entries:
            if e.startswith(alvo):
                return True
    disco = vv.caminho_disco(im.RAIZ_MANTO + nome_pasta)
    return os.path.isdir(disco)


def manto(item):
    """O item e manto com desenho vestido?

    A mesma cautela do `view_cabeca` do valida_visual, do outro lado: em ARMA o
    `View` significa a classe de sprite da arma, e passa-lo ao spriterobeid
    daria resposta sem sentido. E manto sem `View` nao e defeito - a Aura
    Nevada (480097) e um `hateffect` no Script, efeito de tela.
    """
    return bool(item['view']) and bool(
        item['locais'] & set(['Garment', 'Costume_Garment']))


def reaproveitamentos():
    u"""Os manto que o NOSSO item_db reaponta, lidos como (item, origem, doador).

    A FONTE DA VERDADE. O `db/guerra/item_db.yml` vence o `db/re/` no servidor,
    entao um `View:` diferente la e uma decisao ja tomada: "esta peca usa o slot
    tal". Este script so faz a tabela do cliente combinar.

    Ler daqui, em vez de guardar uma lista de-para propria, e o que impede as
    duas metades de divergirem - CLAUDE.md secao 9. Com uma fonte so, rodar de
    novo nao muda nada.
    """
    do_rathena = dict((i['id'], i) for i in vv.le_item_db(vv.ITEM_DB[0]))
    do_nosso = dict((i['id'], i) for i in vv.le_item_db(vv.ITEM_DB[1]))
    fora = []
    for iid in sorted(do_nosso):
        nosso, deles = do_nosso[iid], do_rathena.get(iid)
        if deles is None or not manto(deles) or not nosso['view']:
            continue
        if int(nosso['view']) != int(deles['view']):
            fora.append((iid, int(deles['view']), int(nosso['view']),
                         nosso['nome'] or deles['nome']))
    return fora


def main(argv):
    arg = lambda n, p=None: (argv[argv.index(n) + 1]
                             if n in argv and argv.index(n) + 1 < len(argv)
                             else p)
    destinos = [vv.caminho_disco(c) for c in (ROBE_ID, ROBE_NOME)]

    if '--reverter' in argv:
        for d in destinos:
            if os.path.exists(d):
                os.remove(d)
                print 'apagado  %s' % d.encode('mbcs')
        print 'o cliente volta a ler a tabela do GRF.'
        return 0

    base = tabelas_do_grf(vv.GRF)
    base_ids, base_nomes, base_eng, base_topo = base
    print 'base (nosso GRF): %d constantes, %d nomes, %d no RobeTopLayer, ' \
          'View maximo %d' % (len(base_ids), len(base_nomes), len(base_topo),
                              max(base_ids.values()))

    # NADA E RECUPERADO DO OVERRIDE, e isso e deliberado. A versao de 2026-08-09
    # relia o proprio arquivo para nao perder o que rodadas anteriores tinham
    # posto - fazia sentido quando o script ACRESCENTAVA slot. Agora ele so
    # reaponta, e o de-para inteiro mora no db/guerra/item_db.yml: reler o
    # disco so serviria para arrastar decisao velha que ninguem tomou de novo.
    # Foi o que aconteceu - as 38 entradas acima de 120 da tentativa que nao
    # funcionou sobreviviam a cada rodada sem que nada as pedisse.
    ov = tabelas_do_override()
    extras = {}
    print 'override no disco: %s' % (
        '%d constantes (sera refeito do zero)' % len(ov[0]) if ov[0]
        else 'nao existe ainda')

    # A SONDA vem antes de tudo: ela reaponta um View da BASE, e por isso nao
    # passa pelo laco dos pedidos (que so trata View que a base nao tem).
    sonda = arg('--sonda')
    if sonda:
        alvo, pasta = sonda.split('=', 1)
        alvo = int(alvo)
        por_view_base = dict((v, k) for k, v in base_ids.items())
        const = por_view_base.get(alvo)
        if const is None:
            print '\n--sonda: o View %d nao esta na base deste cliente. A ' \
                  'sonda so vale para View que JA desenha.' % alvo
            return 2
        extras[const] = (alvo, pasta, pasta, const in base_topo)
        print '\n  [SONDA ] View %d (%s): pasta %r -> %r' % (
            alvo, const, base_nomes.get(const), pasta)
        print '          Reabra o cliente e vista a peca desse View.'
        print '          Mudou o desenho -> o override manda.'
        print '          Nao mudou       -> o override e lido e ignorado.'

    # O REAPROVEITAMENTO, lido do nosso item_db - ver a docstring.
    pedidos = reaproveitamentos()
    if pedidos:
        fonte = arg('--grf', im.BRO_GRF)
        f_ids, f_nomes, f_eng, f_topo = tabelas_do_grf(fonte)
        f_por_view = dict((v, k) for k, v in f_ids.items())
        por_view_base = dict((v, k) for k, v in base_ids.items())
        grfs = [Grf(vv.GRF), Grf(fonte)]
        print
        for iid, origem, doador, nome in pedidos:
            const = por_view_base.get(doador)
            pasta = f_nomes.get(f_por_view.get(origem))
            if const is None:
                print ('  [X] %d (%s): o slot doador %d nao existe neste '
                       'cliente' % (iid, nome, doador))
                return 2
            if doador > TETO:
                # A medicao de 2026-08-09, na tela. Ver a docstring.
                print ('  [X] %d (%s): o slot doador %d passa do teto %d - '
                       'este cliente nao desenha manto acima disso'
                       % (iid, nome, doador, TETO))
                return 2
            if tem_arte(base_nomes.get(const, ''), grfs[:1]):
                # A trava que protege o acervo: doador com arte propria e um
                # manto que HOJE funciona, e reaproveita-lo o apagaria.
                print ('  [X] %d (%s): o slot doador %d (%s) TEM arte neste '
                       'cliente - reaproveitar apagaria um manto que funciona'
                       % (iid, nome, doador, const))
                return 2
            if not pasta:
                print ('  [X] %d (%s): o View de origem %d nao tem pasta na '
                       'GRF de origem' % (iid, nome, origem))
                return 2
            if not tem_arte(pasta, grfs):
                print ('  [X] %d (%s): a pasta %r nao existe em GRF nenhum - '
                       'gravar trocaria invisivel por caixa de erro'
                       % (iid, nome, pasta))
                return 2
            no_topo = f_por_view.get(origem) in f_topo
            extras[const] = (doador, pasta, pasta, no_topo)
            print '  [slot  ] %-8d %-30s View %3d -> %3d  %s%s' % (
                iid, nome[:30], origem, doador, pasta,
                '  (desenha na frente)' if no_topo else '')

    else:
        print '\nnenhum manto reapontado no db/guerra/item_db.yml.'

    if not extras:
        print '\nnada acrescentado. O override seria identico ao GRF.'
        return 0

    tabelas = monta(base, extras)
    txt_id, txt_nome = texto(tabelas, len(extras))
    confere(txt_id, txt_nome, tabelas)
    if sonda:
        # Escrito NO ARQUIVO, e nao so na tela: sonda esquecida no disco e um
        # manto desenhando a coisa errada meses depois, sem ninguem lembrar por
        # que. Rodar sem --sonda apaga - a base e relida do GRF toda vez.
        aviso = ('-- SONDA ATIVA: %s. Isto NAO e configuracao - e um teste.\n'
                 '-- Rode `python estende_robeid.py` sem --sonda para desfazer.\n'
                 % sonda)
        txt_id = aviso + txt_id
        txt_nome = aviso + txt_nome
    print '\nround-trip OK: %d constantes, %d nomes, %d no RobeTopLayer' % (
        len(tabelas[0]), len(tabelas[1]), len(tabelas[3]))
    print 'nossas: %s' % ', '.join(
        '%d %s' % (extras[c][0], c)
        for c in sorted(extras, key=lambda c: extras[c][0]))

    if '--verificar' in argv:
        print '\n--verificar: nada gravado.'
        return 0

    pasta = os.path.dirname(destinos[0])
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    for destino, conteudo in zip(destinos, (txt_id, txt_nome)):
        with open(destino, 'wb') as fp:
            fp.write(conteudo)
        print 'gravado  %s  (%d bytes)' % (destino.encode('mbcs'), len(conteudo))
    print '\nO cliente so le isto na INICIALIZACAO - fechar e reabrir.'
    print 'Depois:  python instala_manto.py --ids <n> --aplicar'
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
