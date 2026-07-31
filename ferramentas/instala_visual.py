# -*- coding: utf-8 -*-
"""Instala a arte de um chapeu/costume em `cliente\\data\\`, no caminho certo.

Complemento do `valida_visual.py`: aquele diz o que falta, este poe no lugar.

    python instala_visual.py --id 420047                       # so mostra os destinos
    python instala_visual.py --id 420047 --grf <outra.grf>     # puxa da outra GRF
    python instala_visual.py --id 420047 --de C:\\extraido      # ou de pasta extraida
    python instala_visual.py --todos --grf <outra.grf>         # conta o que daria
    python instala_visual.py --todos --grf <outra.grf> --aplicar

A GRF do bRO (`Gravity Interactive, Inc\\Ragnarok Brazil\\data.grf`) e mais nova
que a nossa de 2021-11-03 e tem a arte que falta. Como as entradas estao sem
DES, o `grf.py` le direto e o GRF Editor nao entra na jogada.

Nao mexe no GRF: o `DataFolderFirst` faz o disco vencer, entao apagar reverte.

**O nome da pasta no disco nao e o nome coreano.** Ver `vv.caminho_disco` - e a
armadilha que fez 5855 arquivos irem para pastas que o cliente nunca abre.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
from grf import Grf

# Os caminhos vivem em CP949 do inicio ao fim, como na tabela do GRF; a lista
# canonica dos oito e a do `vv.Cliente.caminhos`. A conversao para o sistema de
# arquivos acontece num lugar so, `vv.caminho_disco`.
rotulo = vv.rotulo


def indexa_origem(raiz):
    u"""Todo arquivo da origem, indexado pelo nome em minusculas.

    Guarda tambem uma chave sem o prefixo de genero, para casar `남_X.spr`
    independente de como o nome foi gravado no disco.
    """
    idx = {}
    for dirpath, _, arquivos in os.walk(raiz):
        for nome in arquivos:
            baixo = nome.lower()
            idx.setdefault(baixo, os.path.join(dirpath, nome))
            corte = baixo.find(u'_')
            if corte > 0:
                idx.setdefault(baixo[corte:], os.path.join(dirpath, nome))
    return idx


def procura(idx, caminho):
    u"""Casa o destino com a origem pelo trecho ASCII do nome.

    O sufixo ASCII (`_c_h_knight_cloak.spr`) sobrevive a qualquer codificacao,
    que e o que torna o `--de` utilizavel com pasta extraida por outra
    ferramenta.
    """
    baixo = os.path.basename(caminho).decode('mbcs').lower()
    if baixo in idx:
        return idx[baixo]
    corte = baixo.find(u'_')
    if corte > 0 and baixo[corte:] in idx:
        return idx[baixo[corte:]]
    return None


class OrigemGrf(object):
    u"""Le direto de outra GRF, sem passar pelo GRF Editor.

    O caminho de destino ja e o mesmo caminho que a entrada tem la dentro, e na
    mesma codificacao - entao aqui e consulta direta, sem conversao nenhuma.
    """

    def __init__(self, caminho):
        self.grf = Grf(caminho.encode('mbcs') if isinstance(caminho, unicode)
                       else caminho)

    def le(self, rel):
        chave = rel.lower()
        if chave not in self.grf.entries:
            return None
        if self.grf.entries[chave][3] & 6:
            # Nao e "nao achei": e "achei e nao sei abrir". Dizer as duas
            # coisas com a mesma mensagem ja custou tempo nesta base.
            raise Exception('entrada com DES, o grf.py nao le: %s'
                            % rotulo(rel))
        return self.grf.read(chave)


def alvos_do_item(cli, info, itens, iid):
    u"""Os oito caminhos do item, ou [] se ele nao for um chapeu conhecido."""
    res = info.get(iid)
    item = itens.get(iid)
    if not res or not item:
        return []
    return [(rot, cam) for rot, cam in cli.caminhos(res.lower(), item['view'])
            if cam is not None]


def instala(iid, cli, info, itens, idx, fonte_grf, silencioso=False):
    u"""Poe no lugar os arquivos de um item. Devolve (copiados, faltando)."""
    item = itens[iid]
    if not silencioso:
        print '%d  %s  (View %d, recurso "%s")' % (
            iid, item['nome'], item['view'], info[iid])
        if cli.acc.get(item['view']) is None:
            print ('  view %d nao existe no accessoryid.lub deste cliente - a '
                   'arte sozinha nao resolve, o cliente nem sabe desenhar esse '
                   'slot' % item['view'])
        print

    copiados = faltando = 0
    for rot, rel in alvos_do_item(cli, info, itens, iid):
        disco = vv.caminho_disco(rel)
        if os.path.exists(disco):
            if not silencioso:
                print '  [ja tem] %-24s %s' % (rot, rotulo(rel))
            continue

        dados = fonte_grf.le(rel) if fonte_grf is not None else None
        fonte = procura(idx, rel) if (dados is None and idx) else None
        if dados is None and fonte is None:
            faltando += 1
            if not silencioso:
                print '  [FALTA ] %-24s %s' % (rot, rotulo(rel))
            continue

        pasta = os.path.dirname(disco)
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
        if dados is not None:
            fh = open(disco, 'wb')
            fh.write(dados)
            fh.close()
        else:
            shutil.copy2(fonte, disco)
        copiados += 1
        if not silencioso:
            print '  [%s] %-24s %s' % (
                'da grf' if dados is not None else 'copiou', rot, rotulo(rel))
    return (copiados, faltando)


def simula(iid, cli, info, itens, idx, fonte_grf):
    u"""(quantos a origem tem, quantos nao tem) do que ainda falta no disco."""
    tem = nao = 0
    for _, rel in alvos_do_item(cli, info, itens, iid):
        if os.path.exists(vv.caminho_disco(rel)):
            continue
        achou = fonte_grf is not None and rel.lower() in fonte_grf.grf.entries
        if not achou and idx:
            achou = procura(idx, rel) is not None
        if achou:
            tem += 1
        else:
            nao += 1
    return (tem, nao)


def main():
    args = sys.argv[1:]
    if '--id' not in args and '--todos' not in args:
        print __doc__
        return 2
    origem = args[args.index('--de') + 1] if '--de' in args else None
    caminho_grf = args[args.index('--grf') + 1] if '--grf' in args else None

    cli = vv.Cliente()
    info = vv.le_iteminfo(vv.ITEMINFO)
    itens = dict((i['id'], i) for i in vv.le_item_db(vv.ITEM_DB))
    idx = indexa_origem(origem.decode('mbcs')) if origem else {}
    fonte_grf = OrigemGrf(caminho_grf) if caminho_grf else None
    if origem:
        print 'origem: %s  (%d arquivos indexados)' % (origem, len(idx))
    if caminho_grf:
        print 'origem: %s  (%d entradas)' % (caminho_grf,
                                             len(fonte_grf.grf.entries))
    if origem or caminho_grf:
        print

    if '--todos' in args:
        return lote(args, cli, info, itens, idx, fonte_grf)

    iid = int(args[args.index('--id') + 1])
    if iid not in info:
        print '%d nao esta no itemInfo.lua' % iid
        return 1
    if iid not in itens:
        print '%d nao tem entrada de cabeca com View no item_db' % iid
        return 1
    copiados, faltando = instala(iid, cli, info, itens, idx, fonte_grf)
    print
    if not origem and not caminho_grf:
        print ('nenhuma copia feita - rode de novo com --grf <arquivo.grf> ou '
               '--de <pasta>.')
    else:
        print 'instalados %d, faltando %d' % (copiados, faltando)
    print 'para conferir:  python valida_visual.py --id %d' % iid
    return 0


def lote(args, cli, info, itens, idx, fonte_grf):
    u"""Varre tudo o que o valida_visual considera quebrado.

    Sem `--aplicar` so conta: escrever milhares de arquivos no cliente merece um
    segundo comando, nao um efeito colateral de listar.
    """
    aplicar = '--aplicar' in args
    alvos = []
    for iid, it in sorted(itens.items()):
        res = info.get(iid)
        if not res:
            continue
        faltas = [n for n, _, tem in cli.recursos(res.lower(), it['view'])
                  if not tem]
        if [n for n in faltas if n in vv.FATAIS or n.startswith('view ')]:
            alvos.append(iid)
    print 'itens quebrados: %d' % len(alvos)

    resolvidos = parciais = intactos = sem_view = 0
    for iid in alvos:
        # Se o View nao esta no accessoryid.lub deste cliente, arte nenhuma
        # resolve: o cliente nao sabe que slot desenhar. Sem esta linha o lote
        # os conta como "resolvidos" - eles tem so os 4 arquivos de item, sem
        # os 4 de cabeca, entao nada falta e nada e instalado. Foi assim que
        # uma passada relatou 164 resolvidos sem mexer em arquivo nenhum,
        # enquanto o valida_visual continuava acusando os mesmos 548.
        if cli.acc.get(itens[iid]['view']) is None:
            sem_view += 1
            continue
        tem, nao = simula(iid, cli, info, itens, idx, fonte_grf)
        # O criterio e `nao == 0`: nada do que falta esta fora do alcance da
        # origem. `tem == 0 and nao == 0` significa "nao falta mais nada", que
        # acontece muito com --aplicar porque itens diferentes compartilham
        # arquivo - varios chapeus com o mesmo View usam a mesma sprite de
        # cabeca, e o primeiro do lote ja instalou. Contar esse caso como
        # fracasso subnotifica: a primeira rodada relatou 752 resolvidos
        # quando o valida_visual media 909 curados.
        if not nao:
            resolvidos += 1
            if aplicar and tem:
                instala(iid, cli, info, itens, idx, fonte_grf, silencioso=True)
        elif tem:
            # Instalar so parte e pior que nao instalar: o cliente quebra do
            # mesmo jeito se faltar o .act do par, e agora com arquivo solto no
            # disco escondendo o problema do valida_visual. Tudo-ou-nada.
            parciais += 1
        else:
            intactos += 1

    print '  %s completos:      %d' % (
        'resolvidos' if aplicar else 'a origem resolve', resolvidos)
    print '  parciais - PULADOS (tudo-ou-nada): %d' % parciais
    print '  a origem nao tem:                  %d' % intactos
    print '  view fora do accessoryid.lub:      %d  (arte nao resolve)' % sem_view
    print
    if aplicar:
        print 'confira com: python valida_visual.py'
    else:
        print 'nada foi escrito. repita com --aplicar para valer.'
    return 0


if __name__ == '__main__':
    sys.exit(main())
