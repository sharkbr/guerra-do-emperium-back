# -*- coding: utf-8 -*-
u"""Instala a arte de um chapeu/costume em `cliente\\data\\`, no caminho certo.

Complemento do `valida_visual.py`: aquele diz o que falta, este poe no lugar.

Existe por causa de um detalhe chato: os destinos tem **pasta com nome em
coreano** (`아이템`, `악세사리`, `남`, `여`, `유저인터페이스`), e o nome do
proprio arquivo de cabeca comeca com o caractere de genero. Digitar isso a mao
no Explorer ou no console e onde o trabalho se perde - ja esta registrado que
caminho com trecho coreano nao sobrevive ao argv do console nesta maquina.

Por isso o casamento dos arquivos de origem e feito pelo **sufixo ASCII**
(`_c_h_knight_cloak.spr`), que sobrevive a qualquer codificacao, e as pastas de
destino sao criadas pelo script em unicode.

Nao mexe no GRF. O `DataFolderFirst` faz o disco vencer, entao apagar os
arquivos reverte.

    python instala_visual.py --id 420047                       # so mostra os destinos
    python instala_visual.py --id 420047 --grf <outra.grf>     # puxa da outra GRF
    python instala_visual.py --id 420047 --de C:\\extraido      # ou de pasta extraida
    python instala_visual.py --todos --grf <outra.grf>         # conta o que daria
    python instala_visual.py --todos --grf <outra.grf> --aplicar

A GRF do bRO (`Gravity Interactive, Inc\\Ragnarok Brazil\\data.grf`) e mais nova
que a nossa de 2021-11-03 e tem a arte que falta. Como as entradas estao sem
DES, o `grf.py` le direto e o GRF Editor nao entra na jogada.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
from grf import Grf

CLIENTE = vv.CLIENTE.decode('mbcs') if isinstance(vv.CLIENTE, str) else vv.CLIENTE

# As mesmas pastas do valida_visual, mas em unicode: aqui o alvo e o sistema de
# arquivos do Windows, nao a tabela do GRF (que e CP949).
ITEM = u'\uc544\uc774\ud15c'
ACESS = u'\uc545\uc138\uc0ac\ub9ac'
HOMEM = u'\ub0a8'
MULHER = u'\uc5ec'
UI = u'\uc720\uc800\uc778\ud130\ud398\uc774\uc2a4'


def rotulo(caminho):
    u"""Troca o trecho coreano por marcador. O console desta maquina nao imprime
    coreano - e como o script e quem cria a pasta, ninguem precisa do literal."""
    return (caminho.replace(ITEM, u'<item>').replace(ACESS, u'<acessorio>')
            .replace(UI, u'<ui>').replace(HOMEM, u'<M>').replace(MULHER, u'<F>'))


def destinos(res, suf):
    u"""Os oito arquivos, em (rotulo, caminho relativo a `cliente\\`).

    `res` e `suf` chegam como byte str em CP949: boa parte dos itens antigos
    tem resourceName em coreano no proprio itemInfo (`러시아리본`), nao so os
    romanizados como `C_H_Knight_Cloak`.
    """
    if isinstance(res, str):
        res = res.decode('cp949', 'replace')
    d = [
        (u'sprite de chao (.spr)', [u'data', u'sprite', ITEM, res + u'.spr']),
        (u'sprite de chao (.act)', [u'data', u'sprite', ITEM, res + u'.act']),
        (u'icone do inventario', [u'data', u'texture', UI, u'item', res + u'.bmp']),
        (u'icone grande', [u'data', u'texture', UI, u'collection', res + u'.bmp']),
    ]
    if suf:
        if isinstance(suf, str):
            suf = suf.decode('cp949', 'replace')
        for g, rot in ((HOMEM, u'masculina'), (MULHER, u'feminina')):
            for ext in (u'.spr', u'.act'):
                d.append((u'cabeca %s (%s)' % (rot, ext[1:]),
                          [u'data', u'sprite', ACESS, g, g + suf + ext]))
    return [(rot, os.path.join(*partes)) for rot, partes in d]


def indexa_origem(raiz):
    u"""Todo arquivo da origem, indexado pelo nome em minusculas.

    Guarda tambem uma chave sem o prefixo de genero, para casar `남_X.spr`
    vindo com qualquer codificacao de nome.
    """
    idx = {}
    for dirpath, _, arquivos in os.walk(raiz):
        for nome in arquivos:
            baixo = nome.lower()
            idx.setdefault(baixo, os.path.join(dirpath, nome))
            # `<genero>_nome.spr` -> `_nome.spr`
            corte = baixo.find(u'_')
            if corte > 0:
                idx.setdefault(baixo[corte:], os.path.join(dirpath, nome))
    return idx


def procura(idx, alvo):
    u"""Casa o destino com a origem pelo trecho ASCII do nome."""
    baixo = os.path.basename(alvo).lower()
    if baixo in idx:
        return idx[baixo]
    corte = baixo.find(u'_')
    if corte > 0 and baixo[corte:] in idx:
        return idx[baixo[corte:]]
    return None


class OrigemGrf(object):
    u"""Le direto de outra GRF, sem passar pelo GRF Editor.

    O caminho de destino ja e o mesmo caminho que a entrada tem la dentro -
    so muda a codificacao: no sistema de arquivos e unicode, na tabela da GRF
    e CP949. Entao a busca e uma traducao de encoding, nao um casamento por
    nome. O `grf.py` ja indexa em minusculas, o que resolve a diferenca de
    caixa (`남_c_h_knight_cloak.spr` na GRF, `남_C_H_...` no accname).
    """

    def __init__(self, caminho):
        self.grf = Grf(caminho.encode('mbcs') if isinstance(caminho, unicode)
                       else caminho)

    def le(self, rel):
        chave = rel.encode('cp949', 'replace').lower()
        if chave not in self.grf.entries:
            return None
        flags = self.grf.entries[chave][3]
        if flags & 6:
            # Nao e "nao achei": e "achei e nao sei abrir". Dizer as duas
            # coisas com a mesma mensagem ja custou tempo nesta base.
            raise Exception(u'entrada com DES, o grf.py nao le: %s'
                            % rotulo(rel))
        return self.grf.read(chave)


def instala(iid, cli, info, itens, idx, fonte_grf, silencioso=False):
    u"""Poe no lugar os arquivos de um item. Devolve (copiados, faltando)."""
    res = info.get(iid)
    item = itens.get(iid)
    if not res or not item:
        return (0, 0)
    suf = cli.acc.get(item['view'])
    if not silencioso:
        print u'%d  %s  (View %d, recurso "%s")' % (
            iid, item['nome'].decode('mbcs', 'replace'), item['view'], res)
        if suf is None:
            print (u'  view %d nao existe no accessoryid.lub deste cliente - a '
                   u'arte sozinha nao resolve, o cliente nem sabe desenhar '
                   u'esse slot' % item['view'])
        print

    copiados = faltando = 0
    for rot, rel in destinos(res.lower(), suf):
        alvo = os.path.join(CLIENTE, rel)
        if os.path.exists(alvo):
            if not silencioso:
                print u'  [ja tem] %-24s %s' % (rot, rotulo(rel))
            continue

        dados = fonte = None
        if fonte_grf is not None:
            dados = fonte_grf.le(rel)
        if dados is None and idx:
            fonte = procura(idx, alvo)
        if dados is None and fonte is None:
            faltando += 1
            if not silencioso:
                print u'  [FALTA ] %-24s %s' % (rot, rotulo(rel))
            continue

        pasta = os.path.dirname(alvo)
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
        if dados is not None:
            fh = open(alvo, 'wb')
            fh.write(dados)
            fh.close()
        else:
            shutil.copy2(fonte, alvo)
        copiados += 1
        if not silencioso:
            print u'  [%s] %-24s %s' % (
                u'da grf' if dados is not None else u'copiou', rot, rotulo(rel))
    return (copiados, faltando)


def main():
    args = [a.decode('mbcs') if isinstance(a, str) else a for a in sys.argv[1:]]
    if u'--id' not in args and u'--todos' not in args:
        print __doc__
        return 2
    origem = args[args.index(u'--de') + 1] if u'--de' in args else None
    caminho_grf = args[args.index(u'--grf') + 1] if u'--grf' in args else None

    cli = vv.Cliente()
    info = vv.le_iteminfo(vv.ITEMINFO)
    itens = dict((i['id'], i) for i in vv.le_item_db(vv.ITEM_DB))
    idx = indexa_origem(origem) if origem else {}
    fonte_grf = OrigemGrf(caminho_grf) if caminho_grf else None
    if origem:
        print u'origem: %s  (%d arquivos indexados)' % (origem, len(idx))
    if caminho_grf:
        print u'origem: %s  (%d entradas)' % (caminho_grf,
                                              len(fonte_grf.grf.entries))
    if origem or caminho_grf:
        print

    if u'--todos' in args:
        # Varre tudo o que o valida_visual considera quebrado. Sem --aplicar
        # so conta: escrever milhares de arquivos no cliente merece um
        # segundo comando, nao um efeito colateral de listar.
        aplicar = u'--aplicar' in args
        alvos = []
        for iid, it in sorted(itens.items()):
            res = info.get(iid)
            if not res:
                continue
            faltas = [n for n, _, tem in cli.recursos(res.lower(), it['view'])
                      if not tem]
            if [n for n in faltas if n in vv.FATAIS or n.startswith('view ')]:
                alvos.append(iid)
        print u'itens quebrados: %d' % len(alvos)
        resolvidos = parciais = intactos = sem_view = 0
        for iid in alvos:
            # Se o View nao esta no accessoryid.lub deste cliente, arte nenhuma
            # resolve: o cliente nao sabe que slot desenhar. Sem esta linha o
            # lote os conta como "resolvidos" - eles tem so os 4 arquivos de
            # item, sem os 4 de cabeca, entao nada falta e nada e instalado.
            # Foi assim que uma passada relatou 164 resolvidos sem mexer em
            # arquivo nenhum, e o valida_visual continuou acusando os mesmos
            # 548 quebrados.
            if cli.acc.get(itens[iid]['view']) is None:
                sem_view += 1
                continue
            tem, nao = simula(iid, cli, info, itens, idx, fonte_grf)
            # O criterio e `nao == 0`: nada do que falta esta fora do alcance
            # da origem. Cuidado com o caso `tem == 0 and nao == 0`, que nao e
            # "a origem nao tem" e sim "nao falta mais nada" - acontece muito
            # com --aplicar, porque itens diferentes compartilham arquivo
            # (varios chapeus com o mesmo View usam a mesma sprite de cabeca) e
            # o primeiro do lote ja instalou. Contar esse caso como fracasso
            # subnotifica o resultado: a primeira rodada relatou 752 resolvidos
            # e 631 sem cura quando o valida_visual media 909 itens curados.
            if not nao:
                resolvidos += 1
                if aplicar and tem:
                    instala(iid, cli, info, itens, idx, fonte_grf,
                            silencioso=True)
            elif tem:
                # Instalar so parte e pior que nao instalar: o cliente quebra
                # do mesmo jeito se faltar o .act do par, e agora com arquivo
                # solto no disco escondendo o problema do valida_visual.
                # Em lote e tudo-ou-nada por item.
                parciais += 1
            else:
                intactos += 1
        print u'  %s completos:      %d' % (
            u'resolvidos' if aplicar else u'a origem resolve', resolvidos)
        print u'  parciais - PULADOS (tudo-ou-nada): %d' % parciais
        print u'  a origem nao tem:                  %d' % intactos
        print u'  view fora do accessoryid.lub:      %d  (arte nao resolve)' % sem_view
        if not aplicar:
            print
            print u'nada foi escrito. repita com --aplicar para valer.'
        else:
            print
            print u'confira com: python valida_visual.py'
        return 0

    iid = int(args[args.index(u'--id') + 1])
    if iid not in info:
        print u'%d nao esta no itemInfo.lua' % iid
        return 1
    if iid not in itens:
        print u'%d nao tem entrada de cabeca com View no item_db' % iid
        return 1
    copiados, faltando = instala(iid, cli, info, itens, idx, fonte_grf)
    print
    if not origem and not caminho_grf:
        print (u'nenhuma copia feita - rode de novo com --grf <arquivo.grf> ou '
               u'--de <pasta>.')
    else:
        print u'instalados %d, faltando %d' % (copiados, faltando)
    print (u'para conferir:  python valida_visual.py --id %d' % iid)
    return 0


def simula(iid, cli, info, itens, idx, fonte_grf):
    u"""Quantos dos arquivos que faltam a origem tem, sem escrever nada."""
    res = info.get(iid)
    item = itens.get(iid)
    suf = cli.acc.get(item['view']) if item else None
    tem = nao = 0
    for _, rel in destinos(res.lower(), suf):
        if os.path.exists(os.path.join(CLIENTE, rel)):
            continue
        achou = fonte_grf is not None and \
            rel.encode('cp949', 'replace').lower() in fonte_grf.grf.entries
        if not achou and idx:
            achou = procura(idx, os.path.join(CLIENTE, rel)) is not None
        if achou:
            tem += 1
        else:
            nao += 1
    return (tem, nao)


if __name__ == '__main__':
    sys.exit(main())
