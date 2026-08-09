# -*- coding: utf-8 -*-
"""Ensina a este cliente um slot de MANTO que ele nao conhece.

    python estende_robeid.py                              # o que ja foi acrescentado
    python estende_robeid.py --id 480169 --grf <bro>      # pelo item
    python estende_robeid.py --view 125 --grf <bro>       # pelo View
    python estende_robeid.py --id 480169 --grf <bro> --verificar
    python estende_robeid.py --reverter                   # apaga o override

IRMAO DO `estende_accessoryid.py`, do lado do manto. E a metade que faltava

    Manto tem duas camadas a mais que chapeu, e ate 2026-08-09 so uma tinha
    ferramenta:

        camada            chapeu                     manto
        slot de visual    accessoryid.lub  ........  spriterobeid.lub
                          accname.lub               spriterobename.lub
        estende o slot    estende_accessoryid.py     ESTE ARQUIVO
        arte              instala_visual.py          instala_manto.py

    A nossa `spriterobeid.lub` de 2021-11-03 conhece 120 slots; a do bRO
    conhece 258. Manto cujo `View` esteja fora dos nossos 120 NAO DESENHA, e
    arte nenhuma resolve - o `instala_manto.py` recusa esses de proposito, em
    vez de copiar 600 arquivos que o cliente nunca vai procurar. Este script
    traz a ENTRADA DE TABELA; o `instala_manto.py` traz os arquivos. Os dois
    juntos e que curam o manto.

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

    O override e derivado, nunca acumulado sobre si mesmo. A cada rodada a
    base e relida do GRF e as entradas nossas sao reaplicadas por cima, de modo
    que as 120 originais nao podem derivar. As nossas sao recuperadas do
    proprio override, como diferenca contra o GRF - entao rodar duas vezes nao
    duplica e nao perde nada.

    Toda entrada nova passa por TRES travas:

      - constante que ja existe aqui com View DIFERENTE   -> aborta
      - View que ja existe aqui com constante DIFERENTE   -> aborta
      - View cuja PASTA de sprite nao existe em GRF nenhum -> pula, com motivo

    A terceira e a licao de 2026-08-05 do `estende_accessoryid.py`, e aqui ela
    vale para TODO View novo, nao so para um ramo. A assimetria e do formato:
    chapeu sem entrada de tabela ja chega com `Cannot find File` modal, entao
    acrescentar nao piora; manto sem entrada de tabela fica INVISIVEL E CALADO,
    porque o cliente nem tem nome de pasta para procurar. Gravar a entrada sem
    ter a arte troca silencio por caixa de erro - e isso e piorar.

    E antes de gravar um byte, o texto gerado e relido e comparado global a
    global com o que deveria conter. Mesmo criterio de round-trip do
    `estende_accessoryid.py`: layout errado nao da erro, da arquivo corrompido
    - e aqui o arquivo corrompido levaria junto os 120 mantos que funcionam.

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


def views_pedidos(argv_id, argv_view):
    """Os View pedidos, seja por --view, seja pelo item de --id."""
    views = set(int(v) for v in argv_view.replace(',', ' ').split()) \
        if argv_view else set()
    if argv_id:
        alvos = set(int(v) for v in argv_id.replace(',', ' ').split())
        por_id = dict((i['id'], i) for i in vv.le_item_db(vv.ITEM_DB))
        for i in sorted(alvos):
            item = por_id.get(i)
            if item is None:
                print '  [!] item %d nao esta em item_db nenhum' % i
            elif not (item['locais'] & set(['Garment', 'Costume_Garment'])):
                # A mesma cautela do `view_cabeca` do valida_visual, do outro
                # lado: em ARMA o `View` significa a classe de sprite da arma, e
                # passa-lo ao spriterobeid daria resposta sem sentido.
                print ('  [!] item %d (%s) nao e manto - o View dele nao e '
                       'slot de manto' % (i, item['nome']))
            elif not item.get('view'):
                # Manto sem `View` nao e defeito: a Aura Nevada (480097) e um
                # hateffect no Script do item, efeito de tela, sem desenho
                # vestido. Nao ha slot para ensinar.
                print ('  [!] item %d (%s) nao tem View - nada a fazer aqui'
                       % (i, item['nome']))
            else:
                views.add(int(item['view']))
    return sorted(views)


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

    # As entradas nossas, recuperadas como diferenca do override contra o GRF.
    # Recuperar em vez de acumular e o que impede o arquivo de derivar.
    ov = tabelas_do_override()
    extras = {}
    if ov[0]:
        ov_ids, ov_nomes, ov_eng, ov_topo = ov
        for const, view in ov_ids.items():
            if const not in base_ids:
                extras[const] = (view, ov_nomes.get(const), ov_eng.get(const),
                                 const in ov_topo)
        print 'override no disco: %d constantes, %d nossas' % (
            len(ov_ids), len(extras))
    else:
        print 'override no disco: nao existe ainda'

    novos = views_pedidos(arg('--id'), arg('--view'))
    if novos:
        fonte = arg('--grf', im.BRO_GRF)
        f_ids, f_nomes, f_eng, f_topo = tabelas_do_grf(fonte)
        por_view = dict((v, k) for k, v in f_ids.items())
        grfs = [Grf(vv.GRF), Grf(fonte)]
        for view in novos:
            const = por_view.get(view)
            if const is None:
                print '  [!] View %d nao existe nem na GRF de origem' % view
            elif view in base_ids.values():
                print '  [ja tem] View %d - o GRF deste cliente ja conhece' % view
            elif const in extras:
                print '  [ja tem] View %d (%s) - ja esta no override' % (view, const)
            elif not f_nomes.get(const):
                print '  [!] View %d (%s) nao tem nome de pasta na origem' % (
                    view, const)
            elif not tem_arte(f_nomes[const], grfs):
                print ('  [!] View %d (%s) nao tem a pasta %r em GRF nenhum - '
                       'gravar trocaria invisivel por caixa de erro'
                       % (view, const, f_nomes[const]))
            else:
                extras[const] = (view, f_nomes[const], f_eng.get(const),
                                 const in f_topo)
                print '  [novo  ] View %d -> %s  pasta %r%s' % (
                    view, const, f_nomes[const],
                    '  (desenha na frente)' if const in f_topo else '')

    if not extras:
        print '\nnada acrescentado. O override seria identico ao GRF.'
        return 0

    tabelas = monta(base, extras)
    txt_id, txt_nome = texto(tabelas, len(extras))
    confere(txt_id, txt_nome, tabelas)
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
