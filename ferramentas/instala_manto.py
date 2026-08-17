# -*- coding: utf-8 -*-
"""Instala a arte de MANTO (`Costume_Garment`) em `cliente\\data\\`.

    python instala_manto.py --id 480117                    # so relata
    python instala_manto.py --id 480117 --aplicar
    python instala_manto.py --ids 480055,480096 --aplicar
    python instala_manto.py --id 480117 --grf <outra.grf>   # outra origem

Irmao do `instala_visual.py`, para a camada que ele nao alcanca. A diferenca
esta na FORMA da arte, e e ela que obrigou um script separado:

    chapeu   4 arquivos de item + 4 de cabeca, nomes fixos, sufixo unico
    manto    4 arquivos de item + UMA PASTA INTEIRA por recurso, com um
             .spr e um .act para cada CLASSE de personagem e cada sexo

Por isso aqui nao ha lista canonica de caminhos como o `vv.Cliente.caminhos`:
o alvo e a subarvore `data\\sprite\\<manto>\\<recurso>\\` inteira, e o que
mandamos para o disco e a diferenca entre o que a origem tem e o que o nosso
cliente ja tem. Um item de manto custa entre 250 e 700 arquivos.

O QUE ESTE SCRIPT NAO FAZ - e quem faz, desde 2026-08-09
-------------------------------------------------------
Ele NAO estende o `spriterobeid.lub`/`spriterobename.lub` - a tabela que
traduz o `View` do item_db no nome da pasta. Isso e do `estende_robeid.py`,
como o `estende_accessoryid.py` e do lado do chapeu. A divisao e a mesma:
UM TRAZ A ENTRADA DE TABELA, O OUTRO TRAZ OS ARQUIVOS, e so os dois juntos
curam o item. A ordem nao e preferencia:

    python estende_robeid.py --id <n>              # a entrada de tabela
    python instala_manto.py  --ids <n> --aplicar   # a arte

Invertido, este aqui recusa - so sabe em que PASTA copiar depois que a tabela
conhece o `View`.

A tabela do nosso GRF tem 120 entradas, e todo manto cujo `View` ja esteja la
precisa apenas da ARTE. Item com `View` fora dela e recusado aqui, com o motivo
por extenso, em vez de copiar 600 arquivos que o cliente nunca vai procurar - e
a recusa agora tem conserto, que e rodar o `estende_robeid.py` e voltar.

Nao mexe no GRF: o `DataFolderFirst` faz o disco vencer, entao apagar reverte.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
import luadis
from grf import Grf

BRO_GRF = os.path.join(r'C:\Program Files (x86)\Gravity Interactive, Inc',
                       'Ragnarok Brazil', 'data.grf')

ROBE_ID = vv.q(vv.ACC_DIR, 'spriterobeid.lub')
ROBE_NOME = vv.q(vv.ACC_DIR, 'spriterobename.lub')

# 로브 - "robe" em coreano. Escrito como escape de proposito, pela mesma razao
# que os nomes de pasta do valida_visual.py: caminho com coreano nao sobrevive
# ao console nem a leitura casual do arquivo.
MANTO = u'\ub85c\ube0c'.encode('cp949')
RAIZ_MANTO = 'data\\sprite\\' + MANTO + '\\'


class Erro(Exception):
    pass


def tabelas_robe(caminho_grf):
    u"""(view -> constante, constante -> nome do recurso) de uma GRF.

    Mesmo par de tabelas que o `estende_accessoryid.py` le do lado do chapeu:
    uma leva o numero a uma constante (`ROBE_Calabash`) e a outra a constante
    ao nome da pasta (`Calabash`).

    Duas correcoes de 2026-08-09, as duas do `estende_robeid.py`:

    **DISCO PRIMEIRO quando o GRF e o NOSSO**, pela mesma razao do
    `vv.le_tabelas_acessorio`: o `DataFolderFirst` faz `cliente\\data\\` vencer
    o GRF, entao depois de o `estende_robeid.py` gravar o override e ele que o
    cliente le. Sem isto o script continuava respondendo pelo GRF de 2021 e
    RECUSAVA - "view X so existe no spriterobeid do bRO" - um manto cuja
    entrada acabara de ser posta.

    **`RobeNameTable`, e nao `RobeNameTable_Eng`.** O `spriterobename.lub` tem
    TRES globais, e o `vv.tabela_lua` devolve os pares de todos numa lista so -
    um `dict()` por cima ficava com a ultima, que e a `_Eng`. Das 120 entradas
    do nosso cliente, 98 tem os dois nomes iguais e a diferenca nao aparecia;
    nas 17 em que eles diferem, a pasta que existe no GRF e a da
    `RobeNameTable` (nome coreano) em 17 de 17, e a da `_Eng` em 0. Ou seja: o
    `_Eng` e lista paralela de consulta, nao caminho. Com ele, manto antigo dava
    "a origem nao tem a pasta de manto" - alto, mas pelo motivo errado.
    """
    # Import adiado de proposito: o `estende_robeid` importa ESTE modulo (pelas
    # constantes ROBE_ID/RAIZ_MANTO/BRO_GRF), entao a importacao no topo
    # fecharia um ciclo. Adiada para a chamada, o ciclo nao existe.
    import estende_robeid as er
    if caminho_grf == vv.GRF:
        ov_ids, ov_nomes, _eng, _topo = er.tabelas_do_override()
        if ov_ids:
            return dict((int(v), k) for k, v in ov_ids.items()), ov_nomes
    ids, nomes, _eng, _topo = er.tabelas_do_grf(caminho_grf)
    return dict((int(v), k) for k, v in ids.items()), nomes


def recurso_do_view(por_view, nomes, view):
    u"""O nome da pasta de manto de um View, ou None se a tabela nao o conhece."""
    chave = por_view.get(view)
    if chave is None:
        return None
    return nomes.get(chave)


def item_de(itens, iid):
    u"""O item, com o `db/guerra/item_db.yml` VENCENDO o `db/re/`.

    O `vv.le_item_db` recebe os dois arquivos e devolve uma LISTA CHATA, com
    uma entrada por bloco - entao um item que tenha override aparece DUAS
    vezes. Devolver a primeira e devolver a do rAthena, que e justamente a que
    o servidor NAO usa: o `Footer: Imports:` faz o nosso arquivo ser lido
    depois, e o `View:` de la e a fonte da verdade do de-para de manto (ver o
    bloco "OS DEZ MANTOS DE SLOT REAPROVEITADO" no item_db.yml).

    A consequencia da versao antiga era uma recusa com o motivo invertido:
    para os DEZ mantos ja instalados, e para os dois de 2026-08-16, ele lia o
    View original (122, 131, 160, 165), nao o achava na tabela do cliente - que
    para em 120 de proposito - e respondia *"view X so existe no spriterobeid
    do bRO, rode antes o estende_robeid.py"* sobre itens cujo estende_robeid ja
    tinha rodado. Alto, e pelo motivo errado.

    Devolver a ULTIMA tambem nao serve: o bloco de override so tem Id,
    AegisName, Name e View - `locais` viria vazio e a trava de capa recusaria
    a peca. Por isso e MESCLA, campo a campo, com o que o override declarou
    vencendo e o resto vindo do rAthena.
    """
    achados = [it for it in itens if it['id'] == iid]
    if not achados:
        raise Erro('item %d nao esta em item_db nenhum' % iid)
    junto = dict(achados[0])
    for it in achados[1:]:
        for campo, valor in it.items():
            # "Declarou" = trouxe conteudo. Campo ausente num bloco parcial de
            # YAML nasce vazio aqui (None, '', set()), e vazio nao e decisao.
            if valor not in (None, '', 0) and valor != set():
                junto[campo] = valor
    return junto


def alvos(origem, res):
    u"""Toda entrada da origem sob a pasta do recurso.

    Prefixo EXATO com a barra no fim, e nao `in`: `Wing_Of_Angel_Move` e
    prefixo de `Wing_Of_Angel_Move_RD`, e casar por substring misturaria tres
    mantos diferentes num so - o vermelho, o preto e o dourado.
    """
    alvo = (RAIZ_MANTO + res + '\\').lower()
    return [e for e in origem.entries if e.lower().startswith(alvo)]


def resolve(iid, itens, cli, por_view, nomes, bro_view, bro_nomes, origem):
    u"""(recurso, [caminhos que faltam]) - ou levanta Erro dizendo por que nao."""
    item = item_de(itens, iid)
    # `Garment` TAMBEM, e nao so `Costume_Garment`. A trava nasceu estreita em
    # 2026-08-08, quando o Manteleiro era a unica frente de manto e todo item
    # que passava por aqui era cosmetico - e ficou errada no dia em que uma capa
    # de STATUS com `View` precisou de arte (480278 e 480446, 2026-08-16, no
    # Capeiro). O cliente nao pergunta em que slot a peca se equipa: quem manda
    # o sprite desenhar e o `View`, e o caminho da arte e o mesmo nos dois casos.
    # Mesmo criterio do `estende_robeid.manto()`, que ja lia os dois locais -
    # eram DUAS definicoes da mesma coisa, e so uma estava certa.
    if not (item['locais'] & set(['Garment', 'Costume_Garment'])):
        raise Erro('%d (%s) nao e capa (Garment/Costume_Garment) - use o '
                   'instala_visual.py' % (iid, item['nome']))
    view = item['view']
    if view is None:
        raise Erro('%d (%s) nao tem View: ele nao desenha manto nenhum, so o '
                   'efeito de tela do Script (hateffect). Nao ha arte a instalar.'
                   % (iid, item['nome']))

    res = recurso_do_view(por_view, nomes, view)
    if res is None:
        # A recusa deliberada. Ver o cabecalho: copiar arte aqui nao adianta,
        # porque o cliente nem chega a procurar o arquivo.
        no_bro = recurso_do_view(bro_view, bro_nomes, view)
        if no_bro:
            raise Erro('view %d de %d so existe no spriterobeid do bRO (%s). '
                       'Copiar arte agora nao resolve - o cliente nem chega a '
                       'procurar o arquivo. Rode antes:  python '
                       'estende_robeid.py --id %d'
                       % (view, iid, no_bro, iid))
        raise Erro('view %d de %d nao existe em spriterobeid nenhum' % (view, iid))

    do_origem = alvos(origem, res)
    if not do_origem:
        raise Erro('a origem nao tem a pasta de manto "%s" (view %d)' % (res, view))
    return res, [e for e in do_origem if not cli.existe(e)]


def copia(origem, caminhos):
    u"""Grava cada caminho em cliente\\data\\. Devolve quantos foram escritos.

    O nome no disco NAO e o nome coreano: quem explica e o `vv.caminho_disco`.
    """
    escritos = 0
    for cam in caminhos:
        destino = vv.caminho_disco(cam)
        pasta = os.path.dirname(destino)
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
        with open(destino, 'wb') as f:
            f.write(origem.read(cam))
        escritos += 1
    return escritos


def main():
    args = sys.argv[1:]

    def opcao(nome, padrao=None):
        return args[args.index(nome) + 1] if nome in args else padrao

    ids = []
    if '--id' in args:
        ids = [int(opcao('--id'))]
    elif '--ids' in args:
        ids = [int(x) for x in opcao('--ids').replace(',', ' ').split()]
    if not ids:
        print __doc__
        return 2

    caminho_grf = opcao('--grf', BRO_GRF)
    aplicar = '--aplicar' in args

    origem = Grf(caminho_grf)
    cli = vv.Cliente()
    itens = vv.le_item_db(vv.ITEM_DB)
    por_view, nomes = tabelas_robe(vv.GRF)
    bro_view, bro_nomes = tabelas_robe(caminho_grf)

    print 'origem: %s' % caminho_grf
    print

    total, falhas = 0, 0
    for iid in ids:
        try:
            res, faltam = resolve(iid, itens, cli, por_view, nomes,
                                  bro_view, bro_nomes, origem)
        except Erro, e:
            print '%7d  RECUSADO: %s' % (iid, e)
            falhas += 1
            continue
        if not faltam:
            print '%7d  %-24s ja completo neste cliente' % (iid, res)
            continue
        if aplicar:
            n = copia(origem, faltam)
            print '%7d  %-24s %4d arquivo(s) copiado(s)' % (iid, res, n)
        else:
            print '%7d  %-24s %4d arquivo(s) faltando' % (iid, res, len(faltam))
        total += len(faltam)

    print
    if aplicar:
        print 'copiados: %d arquivo(s). O cliente le sprite sob demanda, mas' % total
        print 'a tabela de manto so na inicializacao - se ele estava aberto,'
        print 'feche e reabra.'
    else:
        print 'faltando: %d arquivo(s). Rode de novo com --aplicar.' % total
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
