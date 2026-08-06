# -*- coding: utf-8 -*-
u"""Varre as CARTAS do item_db, classifica por slot e monta as lojas.

    python varre_cartas.py                    # resumo por loja
    python varre_cartas.py --listar curavel   # o que o bRO resolve
    python varre_cartas.py --listar sem-cura  # o que nao ha como salvar
    python varre_cartas.py --ids curavel      # os ids, prontos para o --id
    python varre_cartas.py --gerar            # escreve o NPC e o catalogo

Irma da `varre_cosmeticos.py`, e reaproveita dela a parte que decide se o
cliente desenha o item - a pergunta de arte e a mesma. O que muda e a
CLASSIFICACAO, e e nela que mora tudo o que este arquivo tem de proprio.

O FILTRO DE ARTE NAO SEGURA NADA AQUI, e isso mudou o projeto do script

    Medido em 2026-08-05: **toda** carta do `itemInfo.lua` tem o mesmo
    `identifiedResourceName` - `이름없는카드` ("carta sem nome"), a arte
    generica de verso de carta. Nao e defeito da nossa tabela: o
    `iteminfo_new.lub` do bRO tem o mesmo valor para todas.

    Consequencia direta: `vc.estado` responde `ok` para as 1410, porque os
    quatro arquivos que ele confere sao os mesmos quatro para todas. Arte nao
    distingue carta boa de carta ruim - **o nome distingue**, e por isso este
    script ganhou um segundo eixo.

O SEGUNDO EIXO: o NOME QUE O JOGADOR LE NA LOJA

    A lista da loja e desenhada com o `identifiedDisplayName` do
    `itemInfo.lua` do NOSSO cliente - nao com o `Name` do `item_db`. Vale aqui
    a mesma regra do `npcidentity.lub` e do `accessoryid.lub`: **manda o
    arquivo que o cliente le.** Tres estados possiveis, e so o primeiro presta:

      `pt`       963 - o bRO traduziu, e a fase PT-BR trouxe o nome
      `ingles`   392 - o bRO nunca implementou; sobrou o do ROenglishRE
      `coreano`   54 - existe no bRO, mas nem o bRO traduziu

    Os dois criterios que separam ingles de portugues foram medidos um contra
    o outro antes de escolher, e **concordam nas 1410 sem uma excecao**: das
    392 cujo nome tem a palavra `Card`, nenhuma esta no `iteminfo_new.lub` do
    bRO; e nenhuma das que estao no bRO deixa de ter nome em portugues. Como
    concordam, o criterio gravado e a presenca no bRO - que e um fato sobre a
    tabela, e nao um palpite sobre a forma da palavra.

    O coreano tem de ser testado SEPARADAMENTE da presenca no bRO, porque as
    54 estao no bRO. E o teste e por byte, com uma pegadinha: nome PT deste
    cliente esta em cp1252 e **tem acento de proposito** (ver
    `texto-de-jogo-e-cp1252`). "Byte alto = coreano" acusaria `Carta Lunático`.
    O que vale e byte alto FORA do conjunto de acentos que a fase PT-BR grava.

TRES ARMADILHAS DE CLASSIFICACAO, e nenhuma e obvia de fora

1) `Type: Card` NAO quer dizer carta de monstro. Sao 5593 entradas, e **4048
   delas nao tem `Locations:` nenhum**: sao as pedras de encanto, que o mesmo
   tipo abriga. Delas, 1915 nao tem arte em GRF nenhum - iriam sujar o relatorio
   com "sem cura" que nao e problema de arte, e sujar a loja com item que nao se
   encaixa em equipamento nenhum. O filtro e ter slot, nao ser do tipo.

2) O SLOT vem do `Locations:`, e para carta ele tem outro sentido: nao e onde a
   carta se equipa, e sim **em que equipamento ela pode ser encaixada**.
   `Right_Hand` e carta de arma, `Left_Hand` e carta de escudo. A mesma chave
   que num chapeu significa "vai na cabeca" aqui significa "encaixa em coisa de
   cabeca".

3) MVP e CHEFE nao existem no item_db. Sao derivados do `mob_db`: quem dropa.
   E ha DUAS formas de o rAthena marcar um MVP - `MvpExp:` (91 cartas) e
   `Modes: Mvp: true` (mais 56, entre elas Dark Lord, Fenrir, os chefes de Bio
   Lab e os de instancia). Ler so uma das duas perde metade. `Class: Boss` que
   nao seja MVP e chefe menor: Ghostring, Angeling, Mysteltainn.

MVP e chefe sao EXCLUSIVOS: saem da loja do slot deles e ficam so na propria.
Decidido em 2026-08-05 - a alternativa era a mesma carta em duas lojas, que
para o jogador parece erro de catalogo.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import io
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valida_visual as vv
import varre_cosmeticos as vc
import completa_iteminfo as ci

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARTAS_DB = [os.path.join(_RAIZ, 'rathena', 'db', 're', 'item_db_etc.yml'),
             os.path.join(_RAIZ, 'rathena', 'db', 'guerra', 'item_db.yml')]
MOB_DB = os.path.join(_RAIZ, 'rathena', 'db', 're', 'mob_db.yml')
NPC = os.path.join(_RAIZ, 'rathena', 'npc', 'guerra', 'mercado_de_cartas.txt')
CATALOGO = os.path.join(_RAIZ, 'CATALOGO-CARTAS.md')

# Locations -> loja. A ordem decide: a primeira que casar ganha, e carta que
# aceita mais de um slot (as poucas que ha) fica na primeira da lista.
SLOTS = [(('Right_Hand', 'Both_Hand'), 'arma'),
         (('Left_Hand',), 'escudo'),
         (('Armor',), 'armadura'),
         (('Head_Top', 'Head_Mid', 'Head_Low'), 'capacete'),
         (('Garment',), 'capa'),
         (('Shoes',), 'sapato'),
         (('Right_Accessory', 'Left_Accessory', 'Both_Accessory'), 'acessorio')]

# Onde cada loja fica, com que nome, que sprite e o que diz a PLACA sobre a
# cabeca. Os sprites foram conferidos nas DUAS tabelas antes de entrar -
# `npcidentity.lub` deste cliente e `src/map/npc.hpp` do rAthena -, porque as
# duas discordam: o rAthena conhece nome que este cliente de 2021 nao desenha,
# e o contrario tambem acontece.
#
# A placa leva a CONTAGEM (ver `gera`), e nao so o rotulo: aqui o nome do NPC
# ja diz o encaixe, entao repeti-lo sobre a cabeca nao informaria nada. Nas
# lojas do mercado_contemporaneo.txt e o oposto - "Chapeleiro" nao diz que
# vende cabeca topo -, e por isso la a placa e so o rotulo.
LOJAS = [
    ('arma',      151, 149, u'Carta de Arma',      '4_M_JOB_KNIGHT1', u'Cartas de arma'),
    ('escudo',    155, 149, u'Carta de Escudo',    '4_F_JOB_KNIGHT',  u'Cartas de escudo'),
    ('armadura',  159, 149, u'Carta de Armadura',  '4_M_KY_KNT',      u'Cartas de armadura'),
    ('capacete',  151, 143, u'Carta de Capacete',  '4_M_SAGE_A',      u'Cartas de capacete'),
    ('capa',      155, 143, u'Carta de Capa',      '4_F_ALCHE',       u'Cartas de capa'),
    ('sapato',    159, 143, u'Carta de Sapato',    '4_M_ORIENT02',    u'Cartas de sapato'),
    ('acessorio', 151, 137, u'Carta de Acessorio', '4_F_JOB_HUNTER',  u'Cartas de acessório'),
    ('mvp',       155, 137, u'Carta de MVP',       '4_M_DIEMAN',      u'Cartas de MVP'),
    ('chefe',     159, 137, u'Carta de Chefe',     '4_M_ROGUE',       u'Cartas de chefe'),
]

# O parser do rAthena copia o quarto campo para um `char w4[2048]` e **trunca
# com aviso** se nao couber (`npc.cpp`, npc_parsesrcfile). Uma loja grande
# passa disso: a de arma da 2804 caracteres. O corpo de um `script`, esse nao
# tem o limite - o `npc_parse_script` procura o `,{` no buffer original, nao no
# w4 -, entao o excedente entra por `npcshopadditem` num OnInit.
TETO_W4 = 1900          # folga proposital sobre os 2047 que o parser aceita
POR_CHAMADA = 50        # cartas por npcshopadditem, para a linha ficar legivel

# O `shop` de cada loja e FLUTUANTE (mapa `-`) e invisivel: quem aparece no
# mapa e o `script` que o chama. Ver a secao "A PLACA SOBRE A CABECA" do
# cabecalho gerado.
VIEW_LOJA = '-1'


# ------------------------------------------------------------------ leitura

def le_cartas(caminhos):
    u"""So as entradas `Type: Card`, com nome, Locations e preco.

    Varredura linha a linha como o `vv.le_item_db`, e pelo mesmo motivo: o YAML
    tem megabytes e a forma das entradas e regular. Nao da para reusar aquela
    funcao porque ela nao guarda `Type` nem preco, e carta precisa dos dois.
    """
    fora = []
    at = None
    locais = False

    def fecha():
        if at and at['tipo'] == 'Card':
            fora.append(at)

    for caminho in caminhos:
        if not os.path.exists(caminho):
            continue
        for linha in open(caminho, 'rb'):
            m = re.match(r'\s*- Id:\s*(\d+)', linha)
            if m:
                fecha()
                at = {'id': int(m.group(1)), 'aegis': '', 'nome': '',
                      'tipo': None, 'locais': set(), 'buy': None, 'sell': None,
                      # Carta nunca tem camada de cabeca: sao os 4 arquivos de
                      # item e mais nada. O campo existe porque o
                      # `vc.estado` o consulta.
                      'view_cabeca': None}
                locais = False
                continue
            if at is None:
                continue
            m = re.match(r'\s*AegisName:\s*(\S+)', linha)
            if m:
                at['aegis'] = m.group(1)
                continue
            m = re.match(r'\s*Type:\s*(\S+)', linha)
            if m:
                at['tipo'] = m.group(1)
                continue
            m = re.match(r'\s*Name:\s*(.+?)\s*$', linha)
            if m and not at['nome']:
                at['nome'] = re.sub(r'\s+#.*$', '', m.group(1)).strip('"')
                continue
            m = re.match(r'\s*(Buy|Sell):\s*(\d+)', linha)
            if m:
                at[m.group(1).lower()] = int(m.group(2))
                continue
            if re.match(r'\s*Locations:', linha):
                locais = True
                continue
            m = re.match(r'\s*(\w+):\s*true', linha)
            if locais and m and m.group(1) in vv.LOCAIS:
                at['locais'].add(m.group(1))
        fecha()
        at = None
    return fora


# --------------------------------------------------- o nome que vai na tela

# Os bytes altos que a fase PT-BR grava de proposito no `itemInfo.lua`, em
# cp1252. Byte alto que NAO esteja aqui e byte-lider de hangul CP949, e o nome
# saiu em coreano na tela do jogador.
#
# O `\xa0` (espaco nao separavel) nao e acento e mesmo assim entra: o bRO o usa
# em pelo menos um nome de carta - `Carta\xa0Violinista` (4209). Sem ele, essa
# carta seria acusada de coreana e sairia da loja por engano. Foi o unico falso
# positivo que a medicao de 2026-08-05 encontrou, e vale como aviso: esta lista
# e sobre BYTES do arquivo, nao sobre a ortografia do portugues.
ACENTOS_PT = set(
    u'áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇñÑºª°\xa0'.encode('cp1252'))

# O `identifiedResourceName` que TODA carta do `itemInfo.lua` tem, em CP949:
# 이름없는카드, "carta sem nome" - a arte generica de verso. Nao e usado para
# decidir nada; esta aqui para que a afirmacao do cabecalho possa ser conferida
# com uma linha, sem precisar reabrir a tabela:
#
#   python -c "import varre_cartas as v, valida_visual as vv; \
#              i=vv.le_iteminfo(vv.ITEMINFO); \
#              print set(i[c['id']] for c in v.le_cartas(v.CARTAS_DB) \
#                        if c['id'] in i) == set([v.GENERICO])"
GENERICO = '\xc0\xcc\xb8\xa7\xbe\xf8\xb4\xc2\xc4\xab\xb5\xe5'


def le_nomes_da_tela(caminho):
    u"""id -> `identifiedDisplayName` cru, do `itemInfo.lua` do NOSSO cliente.

    Cru quer dizer bytes cp1252, sem decodificar: a pergunta que se faz deles e
    justamente sobre os bytes (ver `em_coreano`).

    O `re.match` ancora no comeco da linha, e e ele que evita a armadilha que o
    LEIAME registra: `unidentifiedDisplayName` **contem**
    `identifiedDisplayName`. Com `search` no lugar de `match`, todo item viria
    com o nome do nao-identificado - que para carta e sempre "Carta".
    """
    res = {}
    atual = None
    for linha in open(caminho, 'rb'):
        m = re.match(r'\s*\[(\d+)\]\s*=\s*\{', linha)
        if m:
            atual = int(m.group(1))
            continue
        m = re.match(r'\s*identifiedDisplayName\s*=\s*"(.*)"', linha)
        if m and atual is not None and atual not in res:
            res[atual] = m.group(1)
    return res


def em_coreano(bruto):
    u"""O nome saiu em hangul na tela? Ver a nota de `ACENTOS_PT`."""
    return any(ord(c) >= 0x80 and c not in ACENTOS_PT for c in bruto)


def estado_do_nome(iid, nomes, bro_info):
    u"""'pt', 'ingles', 'coreano' ou 'ausente' - o que o jogador le na loja."""
    nome = nomes.get(iid)
    if nome is None:
        return 'ausente'
    if em_coreano(nome):
        return 'coreano'
    if iid not in bro_info:
        return 'ingles'
    return 'pt'


def chefes(aegis_de_carta):
    u"""(ids de MVP, ids de chefe menor), derivados de quem dropa.

    `aegis_de_carta` e {AegisName: id} - o `mob_db` referencia o drop pelo
    AegisName, nunca pelo id.
    """
    mvp, chefe = set(), set()
    at = None

    def fecha():
        if not at:
            return
        for aegis in at['drops']:
            iid = aegis_de_carta.get(aegis)
            if iid is None:
                continue
            if at['mvp']:
                mvp.add(iid)
            elif at['chefe']:
                chefe.add(iid)

    for linha in open(MOB_DB, 'rb'):
        m = re.match(r'\s*- Id:\s*(\d+)', linha)
        if m:
            fecha()
            at = {'mvp': False, 'chefe': False, 'drops': []}
            continue
        if at is None:
            continue
        # As DUAS marcacoes de MVP. Ver a nota (3) do cabecalho.
        if re.match(r'\s*MvpExp:\s*[1-9]', linha) or \
           re.match(r'\s*Mvp:\s*true', linha):
            at['mvp'] = True
            continue
        if re.match(r'\s*Class:\s*Boss', linha):
            at['chefe'] = True
            continue
        m = re.match(r'\s*- Item:\s*(\S+)', linha)
        if m:
            at['drops'].append(m.group(1))
    fecha()
    # MVP vence chefe: um mob pode ser as duas coisas, e o drop pode vir de
    # mais de um mob.
    return mvp, (chefe - mvp)


# ------------------------------------------------------------ classificacao

def slot_de(carta):
    for chaves, rotulo in SLOTS:
        if set(chaves) & carta['locais']:
            return rotulo
    return None


def varre():
    u"""[(carta, loja, estado, motivo, nome)] de toda carta COM slot.

    `loja` ja e a loja final - MVP e chefe substituem o slot, nao acumulam.
    Carta sem slot (pedra de encanto) nao volta daqui: ver a nota (1).

    Os dois ultimos campos sao os DOIS EIXOS: `estado` e sobre arte (o que o
    cliente desenha) e `nome` e sobre texto (o que o jogador le). Sao
    independentes, e hoje so o segundo separa alguma coisa - ver o cabecalho.

    O `bro_info` sai do `vc.Fonte`, que ja o carrega para responder pela arte.
    Ler o `iteminfo_new.lub` de novo aqui custaria alguns segundos por nada.
    """
    cartas = le_cartas(CARTAS_DB)
    mvp, chefe = chefes(dict((c['aegis'], c['id']) for c in cartas if c['aegis']))
    fonte = vc.Fonte()
    nomes = le_nomes_da_tela(ci.ITEMINFO)
    fora = []
    for c in cartas:
        slot = slot_de(c)
        if slot is None:
            continue
        loja = 'mvp' if c['id'] in mvp else \
               'chefe' if c['id'] in chefe else slot
        est, motivo = vc.estado(fonte, c)
        fora.append((c, loja, est, motivo,
                     estado_do_nome(c['id'], nomes, fonte.bro_info)))
    return fora


def na_loja(linhas):
    u"""As que entram na loja: arte que o cliente desenha E nome em portugues."""
    return [(c, loja) for c, loja, est, _m, nome in linhas
            if est == 'ok' and nome == 'pt']


def ordem_alfabetica(nomes):
    u"""Devolve a chave de ordenacao das lojas: o NOME que o jogador le.

    O cliente desenha a lista da loja **na ordem em que o servidor manda** -
    nao ordena nada por conta. Entao a ordem da lista de itens no `shop` e
    exatamente a ordem na tela, e e aqui que ela se decide.

    Tres cuidados, e nenhum e detalhe:

    1) Ordena pelo `identifiedDisplayName` do `itemInfo.lua` - o mesmo nome que
       o filtro de PT usa. Ordenar pelo `Name` do `item_db` daria uma lista que
       parece fora de ordem na tela, porque os dois divergem.

    2) O nome vem em bytes cp1252 COM ACENTO (ver `texto-de-jogo-e-cp1252`), e
       em cp1252 todo acentuado tem byte >= 0x80: ordenar os bytes crus jogaria
       `Carta Lunático` depois de `Carta Zumbi`. Por isso decodifica e tira o
       acento so para comparar - `Á` ordena junto de `A`, como o jogador espera.

    3) Desempate pelo id, para a saida do gerador ser sempre a mesma. Ha cartas
       de nome repetido, e sem desempate a ordem delas mudaria a cada varredura.
    """
    def chave(carta):
        bruto = nomes.get(carta['id'], '')
        texto = bruto.decode('cp1252', 'replace')
        plano = unicodedata.normalize('NFD', texto)
        plano = u''.join(c for c in plano
                         if unicodedata.category(c) != 'Mn')
        return (plano.upper(), carta['id'])
    return chave


def revenda(carta):
    u"""Por quanto o jogador revende. A derivacao e a do rAthena: so `Buy` ->
    `Sell` = Buy/2; so `Sell` -> vale ele mesmo; nenhum dos dois -> 0."""
    if carta['sell'] is not None:
        return carta['sell']
    if carta['buy'] is not None:
        return carta['buy'] // 2
    return 0


# ----------------------------------------------------------------- geracao

CABECALHO = u"""\
//===== Guerra do Emperium ===================================
//= Mercado de Cartas
//===== Onde =================================================
//= prontera, o quarteirão logo ao sul do Mercado de Visuais.
//= Nove lojas, uma por encaixe:
//=
//=            x=151             x=155            x=159
//=  y=155   Costumeiro        Adereceiro       Camareiro      (visuais)
//=  y=149   Carta de Arma     Carta de Escudo  Carta de Armadura
//=  y=143   Carta de Capacete Carta de Capa    Carta de Sapato
//=  y=137   Carta de Acessorio Carta de MVP    Carta de Chefe
//=
//= As nove células foram conferidas no prontera.gat antes de
//= plantar: tipo 0, andável. A faixa x=146..164 está livre de
//= y=131 a y=155 inteira.
//===== Descrição ============================================
//= %(total)d cartas, todas a 1 zeny. GERADO por
//= ferramentas/varre_cartas.py - rodar o script de novo é a
//= forma de atualizar, não editar a mão.
//===== Notas ================================================
//= O QUE É CARTA, E O QUE SÓ PARECE
//=
//= O `item_db` tem %(tipo_card)d entradas `Type: Card`, e só %(com_slot)d são
//= carta de monstro. As outras %(sem_slot)d não têm `Locations:`
//= nenhum: são as PEDRAS DE ENCANTO, que o mesmo tipo abriga.
//= %(sem_arte)d delas não têm arte em GRF nenhum.
//=
//= O filtro desta loja é ter slot, não ser do tipo. Vender
//= pedra de encanto aqui encheria as lojas de item que não
//= encaixa em equipamento nenhum.
//=
//= E o `Locations:` de uma carta tem outro sentido: não é onde
//= ela se equipa, é EM QUE EQUIPAMENTO ela encaixa.
//= `Right_Hand` é carta de arma; `Left_Hand` é carta de escudo.
//=
//= ------------------------------------------------------------
//= SÓ ENTRA CARTA COM NOME EM PORTUGUÊS
//=
//= Das %(com_slot)d com encaixe, só %(nome_pt)d entram. O que decide é o
//= nome que o cliente desenha na lista da loja:
//=
//=   em português  %(nome_pt)4d   entram
//=   em inglês     %(nome_ingles)4d   fora: o bRO nunca as implementou
//=   em coreano    %(nome_coreano)4d   fora: nem o bRO as traduziu
//=   sem nome      %(nome_ausente)4d   fora: sem entrada no itemInfo.lua
//=
//= O nome sai do `identifiedDisplayName` do `itemInfo.lua` do
//= NOSSO cliente, não do `Name` do `item_db` - vale aqui a mesma
//= regra do `npcidentity.lub` e do `accessoryid.lub`: manda o
//= arquivo que o cliente lê.
//=
//= Inglês e coreano se detectam por caminhos DIFERENTES, e um não
//= serve para o outro. Inglês é ausência no `iteminfo_new.lub` do
//= bRO. Coreano não pode ser isso, porque as %(nome_coreano)d coreanas ESTÃO
//= no bRO - elas se detectam por byte, e aí mora a pegadinha: o
//= nome PT deste cliente está em cp1252 e tem acento de propósito,
//= então "byte alto = coreano" acusaria `Carta Lunático`. O que
//= vale é byte alto FORA do conjunto de acentos da fase PT-BR.
//=
//= ------------------------------------------------------------
//= O FILTRO DE ARTE NÃO SEGURA NADA AQUI
//=
//= Toda carta do `itemInfo.lua` tem o MESMO `resourceName`: a arte
//= genérica de verso, cujo nome em coreano quer dizer "carta sem
//= nome" (os bytes CP949 estão em GENERICO, no topo do gerador -
//= aqui não cabem, este arquivo é gravado em cp1252). Não é
//= defeito da nossa tabela: o `iteminfo_new.lub` do bRO traz o
//= mesmo valor para todas. Então os quatro arquivos que o
//= `varre_cosmeticos.estado` confere são os mesmos quatro para
//= todas, e ele responde `ok` para as %(arte_ok)d que têm entrada no
//= `itemInfo.lua` - as outras %(nome_ausente)d ele nem consegue avaliar, e é
//= só isso que a coluna `sem-cura` do resumo mede.
//=
//= Daí a consequência que vale registrar: o
//= `Resource File Loading fail` de `texture\\<ui>\\cardbmp\\...bmp`
//= que aparece no chat ao abrir a arte de uma carta NÃO é sintoma
//= de carta ruim. Esse arquivo não existe em GRF nenhum - nem no
//= nosso, nem no do bRO -, então o erro sai para QUALQUER carta.
//= Tirar as em inglês limpa a loja e não mexe nesse erro; é
//= frente separada.
//=
//= ------------------------------------------------------------
//= MVP E CHEFE NÃO EXISTEM NO item_db
//=
//= Saem do `mob_db`, por quem dropa. E o rAthena marca MVP de
//= DUAS formas - `MvpExp:` e `Modes: Mvp: true` -, então ler só
//= uma perde metade: a segunda é que traz Dark Lord, Fenrir, os
//= chefes de Bio Lab e os de instância. `Class: Boss` que não
//= seja MVP é chefe menor: Ghostring, Angeling, Mysteltainn.
//=
//= São EXCLUSIVOS: a Carta do Doppelganger saiu da loja de arma
//= e está só na de MVP. A alternativa era a mesma carta em duas
//= lojas, que para o jogador parece erro de catálogo.
//=
//= ------------------------------------------------------------
//= PREÇO: 1 zeny, como os dois mercados de cima.
//=
//= A revenda foi medida nas %(tipo_card)d antes de escolher o preço, e o
//= máximo é %(max_revenda)d zeny - toda carta do rAthena tem `Buy: 20`
//= e nenhuma declara `Sell`. São 9 de lucro por compra, a mesma
//= ordem dos itens do Mercado Contemporâneo. Não move nada.
//=
//= O rAthena vai imprimir um aviso por item ao carregar
//= (`npc_parse_shop: Item X discounted buying price`). NÃO é
//= erro de sintaxe e não impede a loja de subir - é o próprio
//= servidor apontando o lucro de 9 zeny acima.
//=
//= ------------------------------------------------------------
//= A ORDEM DA LISTA É ALFABÉTICA, e ela se decide AQUI
//=
//= O cliente desenha a lista da loja na ordem em que o servidor
//= manda - não ordena nada por conta. Então a ordem dos ids na
//= linha do `shop` é a ordem na tela, e por isso o gerador
//= ordena pelo NOME, não pelo id.
//=
//= O nome usado é o `identifiedDisplayName` do `itemInfo.lua` -
//= o mesmo que decide quem entra na loja, e o mesmo que o
//= jogador lê. E o acento sai da comparação: em cp1252 todo
//= acentuado tem byte >= 0x80, então ordenar os bytes crus
//= jogaria `Carta Lunático` depois de `Carta Zumbi`.
//=
//= ------------------------------------------------------------
//= A PLACA SOBRE A CABEÇA, e por que cada loja são DUAS linhas
//=
//= Cada vendedor mostra uma placa com o que vende e quantas
//= cartas tem - "Cartas de arma (359)". Quem a desenha é o
//= `placadevenda`, comando NOSSO (src/custom/placa_de_venda.hpp):
//= a placa amarela de quem abriu barraca, sobre a cabeça do NPC.
//= Até 2026-08-06 era o `waitingroom`, que desenha a barra de
//= sala de conversa - a troca foi pedida porque balão de conversa
//= não diz "aqui se compra". Clicar na placa não faz nada, igual
//= à barra de antes; o clique que vale é o do corpo do NPC.
//=
//= É comando COMPILADO: só existe em map-server recompilado com
//= src/custom. Num binário antigo a linha dá comando desconhecido
//= e a loja não sobe.
//=
//= O `placadevenda` só existe dentro de um `script`, e um `shop`
//= não tem corpo. Então cada loja é um `script` na coordenada,
//= com o sprite e o nome, mais um `shop` FLUTUANTE (mapa `-`,
//= view -1) chamado "<Nome>#loja" com as cartas. O clique no NPC
//= chama `callshop <loja>,0`, que é o mesmo caminho do clique
//= num `shop` - para o jogador nada muda.
//=
//= O porquê inteiro está no cabeçalho do
//= mercado_contemporaneo.txt, seção "A PLACA SOBRE A CABECA".
//=
//= ------------------------------------------------------------
//= O TETO DO `w4`, hoje adormecido - e por que fica no gerador
//=
//= O parser copia o quarto campo para um `char w4[2048]` e
//= **trunca com aviso** se não couber (`npc.cpp`,
//= `npc_parsesrcfile`) - limite que não dá erro, dá loja com
//= metade dos itens.
//=
//= Quando as lojas vendiam as 1410, a de arma dava 2804
//= caracteres e estourava. **Depois do filtro de nome ela dá
//= %(w4_arma)d, e nenhuma das nove passa do teto** - por isso não há
//= nenhum `npcshopadditem` neste arquivo agora.
//=
//= A máquina fica: o corpo de um `script` não tem o limite (o
//= `npc_parse_script` procura o `,{` no buffer original, não no
//= w4), então a linha do `shop` carrega o que cabe e o resto
//= entra por `npcshopadditem` no `OnInit`, que roda depois de
//= todos os NPCs terem carregado. O corte é por TAMANHO, não por
//= nome: se uma loja voltar a crescer, o gerador refaz isso
//= sozinho, sem ninguém precisar lembrar.
//=
//= ------------------------------------------------------------
//= A lista completa, com nome de cada carta, está em
//= CATALOGO-CARTAS.md, na raiz.
//=
//= Os textos vão COM ACENTO, gravados em Latin-1, como os dois
//= mercados de cima. Nome de NPC, esse vai sem acento de
//= propósito: no rAthena ele é identificador, e `duplicate`,
//= `enablenpc` e `donpcevent` referenciam por ele.
//=
//= Mudança neste arquivo pega com @reloadscript.
//============================================================
"""


def gera(linhas):
    u"""Escreve o arquivo de NPC e o catalogo. Devolve (total, por loja)."""
    cartas = le_cartas(CARTAS_DB)
    nomes = le_nomes_da_tela(ci.ITEMINFO)
    por_loja = {}
    for c, loja in na_loja(linhas):
        por_loja.setdefault(loja, []).append(c)

    alfabetica = ordem_alfabetica(nomes)

    corpo = []
    for chave, x, y, nome, sprite, placa in LOJAS:
        do_loja = sorted(por_loja.get(chave, []), key=alfabetica)
        lista = ['%d:1' % c['id'] for c in do_loja]

        # Quantos cabem na propria linha, sem estourar o w4. O que vai na
        # frente do w4 e o view do `shop` flutuante, nao o sprite do vendedor -
        # esse esta na linha do `script`, que nao tem teto.
        cabem, tamanho = 0, len(VIEW_LOJA)
        for pedaco in lista:
            if tamanho + 1 + len(pedaco) > TETO_W4:
                break
            tamanho += 1 + len(pedaco)
            cabem += 1

        # O excedente entra no OnInit da propria loja. Roda depois de TODOS os
        # NPCs carregarem, entao o `shop` la embaixo ja existe.
        extras = []
        for i in range(cabem, len(lista), POR_CHAMADA):
            trecho = do_loja[i:i + POR_CHAMADA]
            extras.append(u'\tnpcshopadditem "%s#loja",%s;'
                          % (nome, ','.join('%d,1' % c['id'] for c in trecho)))

        corpo.append(u'// ----- %s (%d,%d): %d cartas' % (nome, x, y, len(lista)))
        if extras:
            corpo.append(u'// Nao cabe na linha (%d chars com todas): as %d '
                         u'primeiras vao na' % (
                             len(VIEW_LOJA) + sum(1 + len(p) for p in lista),
                             cabem))
            corpo.append(u'// linha do `shop` e as outras %d entram por '
                         u'npcshopadditem no OnInit.' % (len(lista) - cabem))
        corpo.append(u'prontera,%d,%d,4\tscript\t%s\t%s,{' % (x, y, nome, sprite))
        corpo.append(u'\tcallshop "%s#loja",0;' % nome)
        corpo.append(u'\tend;')
        corpo.append(u'')
        corpo.append(u'OnInit:')
        corpo.append(u'\tplacadevenda "%s (%d)";' % (placa, len(lista)))
        corpo.extend(extras)
        corpo.append(u'\tend;')
        corpo.append(u'}')
        corpo.append(u'-\tshop\t%s#loja\t%s,%s'
                     % (nome, VIEW_LOJA, ','.join(lista[:cabem])))
        corpo.append(u'')

    total = sum(len(v) for v in por_loja.values())
    sem_slot = [c for c in cartas if slot_de(c) is None]
    fonte = vc.Fonte()
    sem_arte = 0
    for c in sem_slot:
        if vc.estado(fonte, c)[0] == 'sem-cura':
            sem_arte += 1
    arma = sorted(por_loja.get('arma', []), key=alfabetica)
    w4_arma = len(VIEW_LOJA) + sum(len(',%d:1' % c['id']) for c in arma)

    conta_nome = lambda alvo: len([l for l in linhas if l[4] == alvo])

    texto = (CABECALHO % {
        'total': total, 'tipo_card': len(cartas),
        'com_slot': len(cartas) - len(sem_slot), 'sem_slot': len(sem_slot),
        'sem_arte': sem_arte, 'w4_arma': w4_arma,
        'max_revenda': max(revenda(c) for c in cartas),
        'nome_pt': conta_nome('pt'), 'nome_ingles': conta_nome('ingles'),
        'nome_coreano': conta_nome('coreano'), 'nome_ausente': conta_nome('ausente'),
        'fora': len(linhas) - total,
        'arte_ok': len([l for l in linhas if l[2] == 'ok']),
    }) + u'\n' + u'\n'.join(corpo)
    with io.open(NPC, 'wb') as fp:
        fp.write(texto.replace(u'\n', u'\r\n').encode('cp1252'))

    cat = [u'# Catálogo de cartas — Mercado de Cartas', u'',
           u'As %d cartas à venda a 1 zeny no quarteirão ao sul do Mercado de'
           % total,
           u'Visuais, em Prontera. Gerado por `ferramentas/varre_cartas.py`;',
           u'a loja em `rathena/npc/guerra/mercado_de_cartas.txt`.', u'',
           u'**Só entra carta com nome em português.** Das %d que têm encaixe,'
           % len(linhas),
           u'%d ficaram de fora, e a soma fecha assim:'
           % (len(linhas) - total),
           u'',
           u'| motivo | quantas |',
           u'|---|---|',
           u'| nunca saiu do inglês — o bRO não a implementou | %d |'
           % conta_nome('ingles'),
           u'| aparece em coreano — nem o bRO a traduziu | %d |'
           % conta_nome('coreano'),
           u'| sem entrada nenhuma no `itemInfo.lua` — sai sem nome | %d |'
           % conta_nome('ausente'),
           u'',
           u'O nome abaixo é o que o cliente **desenha na loja** — sai do',
           u'`identifiedDisplayName` do `itemInfo.lua`, não do `Name` do',
           u'`item_db`. Os dois divergem em alguns casos, e quem está na tela',
           u'é este.', u'']
    for chave, x, y, nome, sprite, _placa in LOJAS:
        do_loja = sorted(por_loja.get(chave, []), key=alfabetica)
        cat.append(u'## %s (%d cartas)' % (nome, len(do_loja)))
        cat.append(u'')
        cat.append(u'`prontera %d,%d` — sprite `%s`' % (x, y, sprite))
        cat.append(u'')
        cat.append(u'| id | carta |')
        cat.append(u'|---|---|')
        for c in do_loja:
            cat.append(u'| %d | %s |'
                       % (c['id'],
                          nomes[c['id']].decode('cp1252', 'replace')))
        cat.append(u'')
    with io.open(CATALOGO, 'w', encoding='utf-8', newline='\n') as fp:
        fp.write(u'\n'.join(cat))
    return total, por_loja


def main():
    args = sys.argv[1:]
    linhas = varre()

    if '--ids' in args:
        alvo = args[args.index('--ids') + 1]
        print ','.join(str(c['id']) for c, _l, e, _m, n in linhas
                       if alvo in (e, n))
        return 0

    if '--listar' in args:
        alvo = args[args.index('--listar') + 1]
        # A coluna de nome e a da TELA, nao a do `item_db`. Mostrar a do
        # item_db aqui enganava: uma carta classificada `coreano` aparecia com
        # nome ingles, que e o que o servidor guarda para ela - e o eixo sendo
        # relatado e justamente o outro.
        da_tela = le_nomes_da_tela(ci.ITEMINFO)
        for c, loja, est, motivo, nome in linhas:
            if alvo in (est, loja, nome):
                print '%7d  %-10s %-9s %-8s %-38s %s' % (
                    c['id'], loja, est, nome,
                    da_tela.get(c['id'], '(sem entrada)')[:38], motivo)
        return 0

    if '--gerar' in args:
        total, por_loja = gera(linhas)
        print 'gravado %s' % NPC
        print 'gravado %s' % CATALOGO
        for chave, _x, _y, nome, _s, _p in LOJAS:
            print '  %-20s %4d cartas' % (nome, len(por_loja.get(chave, [])))
        print '  %-20s %4d' % ('TOTAL', total)
        return 0

    # Os DOIS eixos, um em cada tabela. Separados de proposito: juntar arte e
    # nome numa coluna so esconderia justamente o que a medicao de 2026-08-05
    # descobriu - que o eixo da arte nao separa nada nas cartas.
    print 'cartas com slot de equipamento: %d' % len(linhas)
    print
    print '  ARTE (o que o cliente desenha)'
    print '  %-10s %7s %8s %9s' % ('loja', 'ok', 'curavel', 'sem-cura')
    print '  ' + '-' * 38
    for chave, _x, _y, _n, _s, _p in LOJAS:
        da_loja = [l for l in linhas if l[1] == chave]
        conta = lambda e: len([l for l in da_loja if l[2] == e])
        print '  %-10s %7d %8d %9d' % (chave, conta('ok'), conta('curavel'),
                                       conta('sem-cura'))
    print '  ' + '-' * 38
    conta = lambda e: len([l for l in linhas if l[2] == e])
    print '  %-10s %7d %8d %9d' % ('total', conta('ok'), conta('curavel'),
                                   conta('sem-cura'))
    print
    print '  NOME (o que o jogador le na loja)'
    print '  %-10s %7s %8s %9s %8s %8s' % ('loja', 'pt', 'ingles', 'coreano',
                                           'ausente', 'na loja')
    print '  ' + '-' * 56
    entram = dict((chave, 0) for chave, _x, _y, _n, _s, _p in LOJAS)
    for _c, loja in na_loja(linhas):
        entram[loja] += 1
    for chave, _x, _y, _n, _s, _p in LOJAS:
        da_loja = [l for l in linhas if l[1] == chave]
        conta = lambda e: len([l for l in da_loja if l[4] == e])
        print '  %-10s %7d %8d %9d %8d %8d' % (
            chave, conta('pt'), conta('ingles'), conta('coreano'),
            conta('ausente'), entram[chave])
    print '  ' + '-' * 56
    conta = lambda e: len([l for l in linhas if l[4] == e])
    print '  %-10s %7d %8d %9d %8d %8d' % (
        'total', conta('pt'), conta('ingles'), conta('coreano'),
        conta('ausente'), sum(entram.values()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
