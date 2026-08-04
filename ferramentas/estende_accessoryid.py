# -*- coding: utf-8 -*-
"""Ensina a este cliente um slot de visual que ele nao conhece.

    python estende_accessoryid.py                          # o que ja foi acrescentado
    python estende_accessoryid.py --id 400287 --grf <bro>  # pelo item
    python estende_accessoryid.py --view 2260 --grf <bro>  # pelo View
    python estende_accessoryid.py --id 400287 --grf <bro> --verificar
    python estende_accessoryid.py --reverter               # apaga o override

O PROBLEMA QUE ELE RESOLVE, e por que o `instala_visual.py` nao resolvia

    O `instala_visual.py` copia ARQUIVO de arte. Mas 377 itens do mercado nao
    quebravam por falta de arquivo: quebravam porque o `View` deles nao existe
    na tabela `accessoryid.lub` do nosso GRF de 2021-11-03. O cliente nao sabe
    que aquele slot existe, entao nao ha arquivo que ele va procurar.

    A tabela e bytecode dentro do GRF, e ate 2026-08-02 nenhuma ferramenta
    nossa mexia nela - por isso os quatro chapeus pedidos (400287, 410124,
    410142, 410139) ficaram de fora do Mercado Contemporaneo.

    A GRF do bRO conhece 2654 slots contra os nossos 2192, e tem as sprites.
    Este script traz a ENTRADA DE TABELA; o `instala_visual.py` traz os
    arquivos. Os dois juntos e que curam o item.

COMO ELE GRAVA, e por que nao toca no GRF

    Grava Lua em TEXTO em `cliente\\data\\luafiles514\\lua files\\datainfo\\`.
    O cliente le `.lub` texto e bytecode indiferentemente - os arquivos do
    ROenglishRE que ele consome todo dia sao texto puro -, e o
    `DataFolderFirst` faz o disco vencer o GRF. Apagar os dois arquivos
    reverte, e o GRF nunca e aberto para escrita.

A REGRA QUE MANTEM ISTO SEGURO: a base e SEMPRE o nosso GRF

    O override e derivado, nunca acumulado sobre si mesmo. A cada rodada a
    base e relida do GRF e as entradas nossas sao reaplicadas por cima, de
    modo que as 2192 originais nao podem derivar. As entradas ja
    acrescentadas sao recuperadas do proprio override, como diferenca contra
    o GRF - entao rodar duas vezes nao duplica e nao perde nada.

    Toda entrada nova passa por duas travas antes de entrar, e sao as duas
    formas de estrago que a rodada do `skillid.lub` de 2026-07-30 ensinou:

      - constante que ja existe aqui com id DIFERENTE  -> aborta
      - View que ja existe aqui com constante DIFERENTE -> aborta

    E antes de gravar um byte, o texto gerado e relido e comparado entrada a
    entrada com o que deveria conter. Mesmo criterio de round-trip do
    `rsw.py`: layout errado nao da erro, da arquivo corrompido - e aqui o
    arquivo corrompido levaria junto os 5301 chapeus do cliente.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
import luadis
from grf import Grf

# `str`, nao `unicode`, de proposito: o corpo do arquivo carrega sufixo CP949
# ja escapado em `\\ddd`, e um cabecalho unicode promoveria a concatenacao
# inteira. Ai o round-trip explode ao remontar o byte 0xb0 dentro de um
# unicode - foi o primeiro erro que este script deu, e foi o round-trip que
# pegou.
CABECALHO = """\
-- Gerado por ferramentas/estende_accessoryid.py -- NAO editar a mao.
--
-- Base: %s do data.grf deste cliente (%d entradas de 2021-11-03).
-- Acrescentado por nos: %d entrada(s).
--
-- Este arquivo vence o GRF pelo DataFolderFirst. Apagar reverte.
"""


def _escapa(s):
    """Bytes -> literal Lua seguro.

    Todo byte fora do ASCII imprimivel vira `\\ddd` decimal. Nao e capricho:
    os sufixos de acessorio estao em CP949, e la o byte de continuacao pode
    ser `\\` (0x5C) ou `"` (0x22). Gravar CP949 cru num literal Lua produz
    escape acidental, e o erro so aparece no cliente.
    """
    fora = []
    for c in s:
        b = ord(c)
        if c in ('\\', '"') or b < 0x20 or b > 0x7e:
            fora.append('\\%d' % b)
        else:
            fora.append(c)
    return ''.join(fora)


def tabelas_do_grf(caminho):
    """(const -> view, const -> sufixo) lidos do bytecode de uma GRF."""
    grf = Grf(caminho)
    f = lambda n: luadis.read_func(luadis.R(grf.read(n), 12))
    ids = dict((k, int(v)) for k, v in vv.tabela_lua(f(vv.ACC_ID), [])
               if isinstance(k, str))
    nomes = dict((k, v) for k, v in vv.tabela_lua(f(vv.ACC_NOME), [])
                 if isinstance(k, str))
    return ids, nomes


def tabelas_do_override():
    """O que o override tem hoje, ou (None, None) se ele nao existe."""
    caminhos = [vv.caminho_disco(c) for c in (vv.ACC_ID, vv.ACC_NOME)]
    if not all(os.path.exists(c) for c in caminhos):
        return None, None
    ler = lambda c: vv._pares_de_texto(open(c, 'rb').read())
    ids = dict((k, int(v)) for k, v in ler(caminhos[0]))
    nomes = dict(ler(caminhos[1]))
    return ids, nomes


def monta(base_ids, base_nomes, extras):
    """As duas tabelas finais = a base do GRF + os extras, com as travas.

    `extras` e {const: (view, sufixo)}. Devolve (ids, nomes) ou levanta.
    """
    ids, nomes = dict(base_ids), dict(base_nomes)
    por_view = dict((v, k) for k, v in base_ids.items())
    for const in sorted(extras, key=lambda c: extras[c][0]):
        view, suf = extras[const]
        if const in base_ids and base_ids[const] != view:
            raise ValueError(
                '%s ja existe neste cliente com View %d, e a fonte diz %d. '
                'Mesma armadilha do skillid.lub: constante igual com id '
                'diferente. Nao da para acrescentar sem decidir quem manda.'
                % (const, base_ids[const], view))
        if view in por_view and por_view[view] != const:
            raise ValueError(
                'View %d ja e de %s neste cliente, e a fonte quer dar a %s. '
                'Sobrescrever trocaria a arte de um chapeu que hoje funciona.'
                % (view, por_view[view], const))
        ids[const] = view
        if suf is not None:
            nomes[const] = suf
    return ids, nomes


def texto(ids, nomes, n_extras):
    """As duas tabelas em Lua texto, na ordem do View (diff legivel)."""
    ordem = sorted(ids, key=lambda c: (ids[c], c))
    linhas_id = ['%s = %d,' % (c, ids[c]) for c in ordem]
    linhas_nome = ['[ACCESSORY_IDs.%s] = "%s",' % (c, _escapa(nomes[c]))
                   for c in ordem if c in nomes]
    faz = lambda cab, glob, corpo: (
        (CABECALHO % (cab, len(ids) - n_extras, n_extras)) +
        '%s = {\n' % glob + ''.join('\t%s\n' % l for l in corpo) + '}\n')
    return (faz('accessoryid.lub', 'ACCESSORY_IDs', linhas_id),
            faz('accname.lub', 'AccNameTable', linhas_nome))


def confere(txt_id, txt_nome, ids, nomes):
    """Round-trip: reler o texto gerado tem que devolver exatamente as tabelas.

    Sem isto nao ha como saber se um sufixo CP949 sobreviveu ao escape - e um
    sufixo errado nao da erro em lugar nenhum, so faz o cliente procurar um
    arquivo que nao existe.
    """
    volta_id = dict((k, int(v)) for k, v in vv._pares_de_texto(txt_id))
    volta_nome = dict(vv._pares_de_texto(txt_nome))
    esperado_nome = dict((k, v) for k, v in nomes.items() if k in ids)
    if volta_id != ids:
        raise ValueError('round-trip falhou em accessoryid.lub (%d != %d)'
                         % (len(volta_id), len(ids)))
    if volta_nome != esperado_nome:
        raise ValueError('round-trip falhou em accname.lub (%d != %d)'
                         % (len(volta_nome), len(esperado_nome)))


def views_pedidos(argv_id, argv_view):
    """Os View ids pedidos, seja por --view, seja pelo item de --id."""
    views = set(int(v) for v in argv_view.replace(',', ' ').split()) \
        if argv_view else set()
    if argv_id:
        alvos = set(int(v) for v in argv_id.replace(',', ' ').split())
        por_id = dict((i['id'], i) for i in vv.le_item_db(vv.ITEM_DB))
        for i in sorted(alvos):
            item = por_id.get(i)
            if item is None:
                print '  [!] item %d nao esta em item_db nenhum' % i
            elif not item['view_cabeca']:
                print ('  [!] item %d (%s) nao e chapeu com View - nada a '
                       'fazer aqui' % (i, item['nome']))
            else:
                views.add(item['view_cabeca'])
    return sorted(views)


def main(argv):
    arg = lambda n, p=None: (argv[argv.index(n) + 1]
                             if n in argv and argv.index(n) + 1 < len(argv)
                             else p)
    destinos = [vv.caminho_disco(c) for c in (vv.ACC_ID, vv.ACC_NOME)]

    if '--reverter' in argv:
        for d in destinos:
            if os.path.exists(d):
                os.remove(d)
                print 'apagado  %s' % d.encode('mbcs')
        print 'o cliente volta a ler a tabela do GRF.'
        return 0

    base_ids, base_nomes = tabelas_do_grf(vv.GRF)
    print 'base (nosso GRF): %d constantes, %d nomes, View maximo %d' % (
        len(base_ids), len(base_nomes), max(base_ids.values()))

    # As entradas nossas, recuperadas como diferenca do override contra o GRF.
    # Recuperar em vez de acumular e o que impede o arquivo de derivar.
    ov_ids, ov_nomes = tabelas_do_override()
    extras = {}
    if ov_ids:
        for const, view in ov_ids.items():
            if const not in base_ids:
                extras[const] = (view, ov_nomes.get(const))
        print 'override no disco: %d constantes, %d nossas' % (
            len(ov_ids), len(extras))
    else:
        print 'override no disco: nao existe ainda'

    novos = views_pedidos(arg('--id'), arg('--view'))
    if novos:
        fonte = arg('--grf')
        if not fonte:
            print '\nfalta --grf <caminho da GRF do bRO>'
            return 2
        f_ids, f_nomes = tabelas_do_grf(fonte)
        por_view = dict((v, k) for k, v in f_ids.items())
        for view in novos:
            const = por_view.get(view)
            if const is None:
                print '  [!] View %d nao existe nem na GRF de origem' % view
            elif view in base_ids.values():
                print '  [ja tem] View %d - o GRF deste cliente ja conhece' % view
            elif const in extras:
                print '  [ja tem] View %d (%s) - ja esta no override' % (view, const)
            else:
                extras[const] = (view, f_nomes.get(const))
                print '  [novo  ] View %d -> %s  sufixo %r' % (
                    view, const, f_nomes.get(const))

    if not extras:
        print '\nnada acrescentado. O override seria identico ao GRF.'
        return 0

    ids, nomes = monta(base_ids, base_nomes, extras)
    txt_id, txt_nome = texto(ids, nomes, len(extras))
    confere(txt_id, txt_nome, ids, nomes)
    print '\nround-trip OK: %d constantes, %d nomes' % (len(ids), len(nomes))
    print 'nossas: %s' % ', '.join(
        '%d %s' % (extras[c][0], c) for c in sorted(extras, key=lambda c: extras[c][0]))

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
    print 'Depois:  python instala_visual.py --id <n> --grf "<grf do bRO>"'
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
