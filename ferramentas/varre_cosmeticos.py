# -*- coding: utf-8 -*-
u"""Varre os itens COSMETICOS do item_db e diz em que estado cada um esta.

    python varre_cosmeticos.py                    # resumo por slot
    python varre_cosmeticos.py --listar ok        # os que o cliente ja desenha
    python varre_cosmeticos.py --listar curavel   # os que o bRO resolve
    python varre_cosmeticos.py --listar sem-cura  # os que nao ha como salvar
    python varre_cosmeticos.py --ids curavel      # so os ids, separados por virgula

A pergunta que ele responde e diferente da do `valida_visual.py`. Aquele mede o
estado de AGORA: o que o cliente desenha hoje. Este mede o estado POSSIVEL:
o que o cliente desenharia depois de rodar as tres ferramentas de cura
(`completa_iteminfo.py`, `estende_accessoryid.py`, `instala_visual.py`).

A diferenca importa porque as tres camadas se encadeiam, e nenhuma sozinha
enxerga o fim. Um item sem entrada no `itemInfo.lua` nem tem `resourceName`
para o validador consultar - ele responde "nao esta no itemInfo.lua", que
parece um veredito e e so uma pergunta sem resposta. Este script vai buscar o
`resourceName` no bRO, o sufixo de cabeca no `accessoryid.lub` do bRO, e so
entao pergunta pelos arquivos - nos dois GRFs ao mesmo tempo.

Por isso o estado `curavel` e uma PROMESSA VERIFICAVEL: significa que os oito
arquivos existem em algum dos dois lados. Quem cumpre a promessa e o
`instala_visual.py`; quem confere se ela foi cumprida e o `valida_visual.py`.

O QUE FICA DE FORA: `Costume_Garment` (manto cosmetico)

    Manto tem uma NONA camada que nenhuma ferramenta nossa toca: a tabela
    `spriterobeid.lub`/`spriterobename.lub`, que e para o manto o que o
    `accessoryid.lub` e para o chapeu. A nossa tem 120 entradas. Item de manto
    cujo `View` esteja fora dela nao desenha, e nenhuma quantidade de arte
    resolve - exatamente o caso que o `estende_accessoryid.py` existe para
    curar do lado do chapeu, e que ainda nao tem equivalente aqui.

    Entao os mantos sao CONTADOS e classificados (ver `--listar manto`), mas
    nao entram como `curavel`: prometer o que nao ha como cumprir era o erro
    que a rodada de 2026-08-01 cometeu ao chamar de "sem cura" o que so
    precisava de outra ferramenta.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
import completa_iteminfo as ci
import estende_accessoryid as ea
import luadis
from grf import Grf

BRO_GRF = os.path.join(r'C:\Program Files (x86)\Gravity Interactive, Inc',
                       'Ragnarok Brazil', 'data.grf')

# Slot cosmetico -> rotulo curto. A ordem e a que aparece no resumo e a que
# decide a coluna da loja.
SLOTS = [('Costume_Head_Top', 'topo'),
         ('Costume_Head_Mid', 'meio'),
         ('Costume_Head_Low', 'baixo'),
         ('Costume_Garment', 'manto')]

ROBE_ID = vv.q(vv.ACC_DIR, 'spriterobeid.lub')


def slot_de(item):
    u"""O slot cosmetico do item, ou None se ele nao for cosmetico.

    Item com mais de um slot cosmetico existe (chapeu que ocupa topo e meio) e
    fica no PRIMEIRO da lista, que e o mais alto. Poe-lo em duas lojas o faria
    aparecer duas vezes para o jogador, o que parece erro de catalogo.
    """
    for chave, rotulo_ in SLOTS:
        if chave in item['locais']:
            return rotulo_
    return None


def views_do_robe(caminho_grf):
    u"""Os View de manto que uma GRF conhece, lidos do spriterobeid.lub."""
    grf = Grf(caminho_grf)
    pares = vv.tabela_lua(luadis.read_func(luadis.R(grf.read(ROBE_ID), 12)), [])
    return set(int(v) for k, v in pares if isinstance(k, str))


class Fonte(object):
    u"""As duas GRFs e as duas tabelas de item, vistas como uma so.

    Toda pergunta aqui e "existe em ALGUM dos dois lados", porque e isso que
    determina se a cura e possivel. Qual dos dois responde nao interessa para
    este script - interessa para o `instala_visual.py`, que faz a copia.
    """

    def __init__(self):
        self.cli = vv.Cliente()
        self.info = vv.le_iteminfo(vv.ITEMINFO)
        self.bro_info = ci.le_bro(ci.BRO)
        self.bro_grf = Grf(BRO_GRF)
        # accessoryid: o nosso (GRF + override) ja vem no `cli.acc`; o do bRO
        # tem de ser montado a parte, view -> sufixo do arquivo de cabeca.
        b_ids, b_nomes = ea.tabelas_do_grf(BRO_GRF)
        self.bro_acc = dict((int(v), b_nomes[k])
                            for k, v in b_ids.items() if k in b_nomes)
        self.robe_nosso = views_do_robe(vv.GRF)
        self.robe_bro = views_do_robe(BRO_GRF)

    def recurso(self, iid):
        u"""O `resourceName` do item: o nosso, ou o do bRO se ainda nao houver.

        A conversao para CP949 e a mesma do `completa_iteminfo.py` - o campo e
        nome de arquivo dentro do GRF, nao texto de tela. Recurso que nao couber
        em CP949 nao tem como ser gravado no `itemInfo.lua`, entao vale como
        ausente.
        """
        if iid in self.info:
            return self.info[iid]
        campos = self.bro_info.get(iid)
        if not campos or 'identifiedResourceName' not in campos:
            return None
        try:
            return ci.para_cp949(campos['identifiedResourceName'])
        except ci.Erro:
            return None

    def sufixo(self, view):
        u"""O sufixo da sprite de cabeca do View, nosso ou do bRO."""
        return self.cli.acc.get(view) or self.bro_acc.get(view)

    def existe(self, caminho):
        return self.cli.existe(caminho) or caminho.lower() in self.bro_grf.entries


def estado(fonte, item):
    u"""(estado, motivo) do item, olhando os dois lados.

    Estados: 'ok' (o cliente ja desenha), 'curavel' (as ferramentas resolvem),
    'sem-cura' (falta em ambos os lados).
    """
    iid = item['id']
    res = fonte.recurso(iid)
    if res is None:
        return 'sem-cura', 'sem resourceName em lado nenhum'

    view = item['view_cabeca']
    if view is not None and fonte.sufixo(view) is None:
        return 'sem-cura', 'view %d fora do accessoryid dos dois' % view

    # Os caminhos sao montados com o sufixo POSSIVEL, nao com o que o cliente
    # conhece hoje: e a diferenca entre "o que falta" e "o que faltaria depois
    # da cura". `vv.Cliente.caminhos` usa `self.acc`, que so tem o nosso, entao
    # o sufixo do bRO e injetado antes e retirado depois.
    injetado = view is not None and view not in fonte.cli.acc
    if injetado:
        fonte.cli.acc[view] = fonte.bro_acc[view]
    try:
        alvos = [(rot, cam) for rot, cam in fonte.cli.caminhos(res.lower(), view)
                 if cam is not None]
    finally:
        if injetado:
            del fonte.cli.acc[view]

    faltam_nos_dois = [rot for rot, cam in alvos
                       if rot in vv.FATAIS and not fonte.existe(cam)]
    if faltam_nos_dois:
        return 'sem-cura', 'o bRO tambem nao tem: %s' % ', '.join(faltam_nos_dois)

    faltam_aqui = [rot for rot, cam in alvos
                   if rot in vv.FATAIS and not fonte.cli.existe(cam)]
    # `view is not None` nao e defensivo, e a diferenca entre chapeu e o resto:
    # item sem camada de cabeca tem `view_cabeca` None, e `None not in acc` e
    # sempre verdadeiro. Sem esta guarda, TODO manto e todo acessorio caia em
    # `curavel` - a primeira rodada relatou 152 mantos curaveis e nenhum ok,
    # que era o proprio bug se anunciando.
    falta_slot = view is not None and view not in fonte.cli.acc
    # O motivo diz QUAL das tres ferramentas o item precisa, porque e disso que
    # a cura em lote depende - as tres tem de rodar na ordem, e so a do meio
    # (`estende_accessoryid.py`) e obrigatoriamente anterior a ultima.
    falta = []
    if iid not in fonte.info:
        falta.append('iteminfo')
    if falta_slot:
        falta.append('accessoryid')
    if faltam_aqui:
        falta.append('%d arquivo(s)' % len(faltam_aqui))
    if falta:
        return 'curavel', ' + '.join(falta)
    return 'ok', ''


def estado_manto(fonte, item):
    u"""Manto tem a camada do `spriterobeid.lub` por cima de tudo o mais."""
    est, motivo = estado(fonte, item)
    view = item['view']
    if view is None:
        return est, motivo
    if view in fonte.robe_nosso:
        return est, motivo
    if view in fonte.robe_bro:
        return 'sem-cura', ('view %d de manto so existe no robe do bRO - falta '
                            'ferramenta' % view)
    return 'sem-cura', 'view %d de manto nao existe em robe nenhum' % view


def varre():
    u"""[(item, slot, estado, motivo)] de todo cosmetico do item_db."""
    fonte = Fonte()
    fora = []
    for item in vv.le_item_db(vv.ITEM_DB):
        slot = slot_de(item)
        if slot is None:
            continue
        if slot == 'manto':
            est, motivo = estado_manto(fonte, item)
        else:
            est, motivo = estado(fonte, item)
        fora.append((item, slot, est, motivo))
    return fora


def main():
    args = sys.argv[1:]
    linhas = varre()

    if '--ids' in args:
        alvo = args[args.index('--ids') + 1]
        print ','.join(str(i['id']) for i, _, e, _m in linhas if e == alvo)
        return 0

    if '--listar' in args:
        alvo = args[args.index('--listar') + 1]
        for item, slot, est, motivo in linhas:
            if est != alvo and alvo != 'manto':
                continue
            if alvo == 'manto' and slot != 'manto':
                continue
            print '%7d  %-6s %-9s %-38s %s' % (
                item['id'], slot, est, item['nome'][:38], motivo)
        return 0

    print 'cosmeticos no item_db: %d' % len(linhas)
    print
    print '  %-8s %8s %8s %9s' % ('slot', 'ok', 'curavel', 'sem-cura')
    print '  ' + '-' * 36
    for _, rotulo_ in SLOTS:
        do_slot = [l for l in linhas if l[1] == rotulo_]
        conta = lambda e: len([l for l in do_slot if l[2] == e])
        print '  %-8s %8d %8d %9d' % (rotulo_, conta('ok'), conta('curavel'),
                                      conta('sem-cura'))
    print '  ' + '-' * 36
    conta = lambda e: len([l for l in linhas if l[2] == e])
    print '  %-8s %8d %8d %9d' % ('total', conta('ok'), conta('curavel'),
                                  conta('sem-cura'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
