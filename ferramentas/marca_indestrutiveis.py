# -*- coding: utf-8 -*-
u"""Faz valer o "Indestrutivel em batalha" que a descricao do item promete.

    python marca_indestrutiveis.py             # gera db/guerra/item_db_indestrutivel.yml
    python marca_indestrutiveis.py --conferir  # so relata; sai 1 se achar divergencia

O PROBLEMA QUE ISTO RESOLVE

A descricao que o jogador le vem do `itemInfo.lua` do CLIENTE, que e a
traducao do bRO. O efeito vem do `Script:` do `item_db` do nosso rAthena, que
e outra revisao. Quando os dois discordam, nada avisa - e um dos desacordos
custa item: a descricao diz

    ^a400cdIndestrutivel em batalha.^000000

e o `Script:` nao traz `bonus bUnbreakableWeapon;`. Ai a arma quebra.

Quem quebra equipamento e o `skill_break_equip` (src/map/skill.cpp linha
1944), chamado pelas habilidades de monstro NPC_ARMORBRAKE, NPC_HELMBRAKE,
NPC_SHIELDBRAKE e NPC_WEAPONBRAKER. A PRIMEIRA COISA que ele faz e

    if (sd->bonus.unbreakable_equip)
        where &= ~sd->bonus.unbreakable_equip;

ou seja: a trava existe e funciona - so nao esta ligada nesses itens. Nao ha
campo de item_db para isso, nem flag: `unbreakable_equip` so recebe bit por
`bonus bUnbreakable<slot>` rodando no `Script:` do proprio item
(src/map/pc.cpp linha 4262).

Medido em 2026-08-18: 540 itens do nosso cliente dizem "Indestrutivel" e 27
deles nao tinham o bonus. Sete estao a venda nas lojas de Prontera - entre
eles a Lamina Sagrada (500009), o Escudo Divino (28962) e o Escudo da Fenix
(460023).

COMO ELE RESOLVE

Um override em `db/guerra/item_db_indestrutivel.yml` que REPETE O SCRIPT
INTEIRO do item com uma linha a mais no topo. Repetir e obrigatorio, e nao ha
saida mais barata: o `ItemDatabase::parseBodyNode` SUBSTITUI o `Script:` do
item quando o campo aparece, nao acrescenta. Bonus posto no `EquipScript:`
tambem nao serve - aquele roda uma vez, no clique de equipar, e o
`status_calc_pc_` refaz os bonus do zero sem ele.

O bonus entra na PRIMEIRA linha do script, nao na ultima, de proposito: script
que termine em `if (cond)` sem chaves engoliria a linha seguinte. No topo nao
ha o que engolir.

QUE ITENS ENTRAM

Todo item de equipamento cuja descricao no `itemInfo.lua` contenha
"Indestrut" e cujo script nao tenha o `bonus bUnbreakable<slot>` do proprio
slot. O slot sai do `Locations:` do item_db - nunca do nome:

    Type: Weapon                -> bUnbreakableWeapon
    Locations: Left_Hand        -> bUnbreakableShield
    Locations: Armor            -> bUnbreakableArmor
    Locations: Head_*           -> bUnbreakableHelm
    Locations: Garment          -> bUnbreakableGarment
    Locations: Shoes            -> bUnbreakableShoes

QUE ITENS FICAM DE FORA, E POR QUE

1. MACHADO, MACA, CAJADO, LIVRO E HUUMA. O proprio `skill_break_equip` ja os
   isenta, por tipo de arma, antes de sortear (src/map/skill.cpp linha 1968) -
   sao 241 itens que ja nao quebram. Po-los aqui congelaria o `Script:` de
   241 armas do vendor por um efeito que ja existe: toda correcao futura do
   rAthena naqueles scripts morreria calada sob o nosso override.

2. EQUIPAMENTO SOMBRIO (`Type: Shadowgear`). Nao existe `bUnbreakableShadow`:
   o `unbreakable_equip` so tem bit para os seis slots acima. Equipamento
   sombrio cai no `EQP_SHADOW_GEAR` do `skill_break_equip`, que nenhuma
   habilidade de monstro pede - na pratica nao quebra, mas se um dia quebrar
   nao ha como travar por `db/`. Hoje sao quatro: 24152, 24153, 24154 e
   24155 - o `--conferir` os lista por nome.

DE ONDE VEM A LISTA, E POR QUE ISSO PRENDE A FERRAMENTA AO WINDOWS

Do `itemInfo.lua` do nosso cliente, que esta fora do git e so existe nesta
maquina (CLAUDE.md secao 1). Entao ESTA FERRAMENTA SO RODA NO WINDOWS. O
arquivo que ela gera e versionado e vale para as tres maquinas; o que nao da
para fazer no Mac e regera-lo.

QUANDO RODAR DE NOVO

Sempre que o `itemInfo.lua` ganhar item novo (`instala_item.py`) ou o vendor
do rAthena for atualizado. O `--conferir` responde em segundos e sai 1 se
achar divergencia.

COMO RECARREGAR

`@reloaditemdb`, e so. Nao precisa relogar nem trocar de mapa: o
`itemdb_reload` (src/map/itemdb.cpp) termina com um `status_calc_pc(sd,
SCO_FORCE)` para cada jogador online, e e ele que refaz os bonus. Diferente do
`Locations:`, que exige relogar porque quem reenvia a lista de inventario e o
`clif_parse_LoadEndAck` (CLAUDE.md secao 5).
"""

import os
import re
import sys
import codecs

sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RATHENA = os.path.join(RAIZ, 'rathena')
SAIDA = os.path.join(RATHENA, 'db', 'guerra', 'item_db_indestrutivel.yml')
ITEMINFO = u'C:/GuerraDoEmperium/cliente/SystemEN/LuaFiles514/itemInfo.lua'

# Tipos de arma que o skill_break_equip isenta sozinho (src/map/skill.cpp:1968).
ARMAS_ISENTAS = ('1hAxe', '2hAxe', 'Mace', '2hMace', 'Staff', '2hStaff',
                 'Book', 'Huuma', 'Fist')

CABECALHO = u"""###########################################################################
# Guerra do Emperium - O "INDESTRUTIVEL" DA DESCRICAO PASSA A VALER
#
# ARQUIVO GERADO por ferramentas/marca_indestrutiveis.py. Editar a mao
# funciona ate a proxima geracao, que apaga tudo.
#
# Cada bloco aqui REPETE O SCRIPT INTEIRO do item com uma linha a mais na
# primeira posicao. Repetir e obrigatorio: o leitor do item_db SUBSTITUI o
# `Script:` quando o campo aparece, nao acrescenta.
#
# O motivo, em uma frase: a descricao que o jogador le vem do itemInfo.lua do
# cliente (traducao do bRO) e diz "Indestrutivel em batalha"; o `Script:` do
# nosso vendor nao trazia o `bonus bUnbreakable<slot>`, e o
# `skill_break_equip` (src/map/skill.cpp:1944) so poupa quem tem o bonus.
#
# CONSEQUENCIA DE ESTE ARQUIVO EXISTIR: enquanto ele estiver aqui, correcao
# do rAthena no `Script:` destes itens nao chega ao jogo - o nosso vence.
# Rodar a ferramenta de novo depois de atualizar o vendor.
#
# Recarregar: @reloaditemdb, e so - o itemdb_reload termina com um
# status_calc_pc(sd, SCO_FORCE) por jogador online, que refaz os bonus.
###########################################################################
Header:
  Type: ITEM_DB
  Version: 3

Body:
"""


def blocos_yml(caminho):
    u"""Devolve {id: texto do bloco} de um item_db em YAML."""
    if not os.path.exists(caminho):
        return {}
    texto = open(caminho, 'rb').read().decode('cp1252', 'replace')
    saida = {}
    for parte in re.split(r'\n  - (?=Id:)', texto)[1:]:
        m = re.match(r'Id:\s*(\d+)', parte)
        if m:
            saida[int(m.group(1))] = parte
    return saida


def le_cliente():
    u"""{id: (nome, diz_indestrutivel)} do itemInfo.lua do nosso cliente."""
    if not os.path.exists(ITEMINFO):
        print u'ERRO: nao achei o itemInfo.lua do cliente em'
        print u'      %s' % ITEMINFO
        print u'      Esta ferramenta so roda no Windows (ver o cabecalho).'
        sys.exit(2)
    texto = open(ITEMINFO, 'rb').read().decode('cp1252', 'replace')
    saida = {}
    for m in re.finditer(r'\n\t\[(\d+)\]\s*=\s*\{(.*?)\n\t\},', texto, re.S):
        corpo = m.group(2)
        nome = re.search(r'\n\t\tidentifiedDisplayName\s*=\s*"([^"]*)"', corpo)
        saida[int(m.group(1))] = (nome.group(1) if nome else u'?',
                                  u'Indestrut' in corpo)
    return saida


def campo(bloco, nome):
    m = re.search(r'\n    %s:\s*(\S+)' % nome, bloco)
    return m.group(1) if m else u''


def locais(bloco):
    m = re.search(r'\n    Locations:\n((?:      .*\n)+)', bloco)
    return re.findall(r'(\w+): true', m.group(1)) if m else []


def bonus_do_slot(bloco):
    u"""Qual bUnbreakable* cabe neste item. None = nao ha como travar."""
    tipo = campo(bloco, 'Type')
    loc = locais(bloco)
    if tipo == u'Weapon':
        return u'bUnbreakableWeapon'
    if tipo == u'Shadowgear':
        return None                      # nao existe bUnbreakableShadow
    if u'Left_Hand' in loc:
        return u'bUnbreakableShield'
    if u'Armor' in loc:
        return u'bUnbreakableArmor'
    if [l for l in loc if l.startswith(u'Head_')]:
        return u'bUnbreakableHelm'
    if u'Garment' in loc:
        return u'bUnbreakableGarment'
    if u'Shoes' in loc:
        return u'bUnbreakableShoes'
    return None


def script_de(bloco):
    u"""O corpo do `Script: |` do bloco, com a indentacao original."""
    m = re.search(r'\n    Script: \|\n((?:      .*(?:\n|$))*)', bloco)
    return m.group(1) if m else None


def levanta():
    u"""(pendentes, isentos_por_tipo_de_arma, sem_travamento)."""
    cliente = le_cliente()
    servidor = blocos_yml(os.path.join(RATHENA, 'db', 're', 'item_db_equip.yml'))
    # O nosso override vence: se ele redefine o Script, e dele que partimos.
    for sid, bloco in blocos_yml(os.path.join(RATHENA, 'db', 'guerra',
                                              'item_db.yml')).items():
        if sid in servidor and script_de(bloco) is None:
            continue                     # override que nao mexe no Script
        servidor[sid] = bloco

    pendentes, isentos, sem_trava = [], [], []
    for sid, (nome, indestrutivel) in cliente.items():
        if not indestrutivel or sid not in servidor:
            continue
        bloco = servidor[sid]
        bonus = bonus_do_slot(bloco)
        if bonus is None:
            if campo(bloco, 'Type') == u'Shadowgear':
                sem_trava.append((sid, nome, campo(bloco, 'AegisName')))
            continue
        if bonus in bloco:
            continue                     # ja e indestrutivel
        if bonus == u'bUnbreakableWeapon' and campo(bloco, 'SubType') in ARMAS_ISENTAS:
            isentos.append((sid, nome, campo(bloco, 'SubType')))
            continue
        pendentes.append((sid, nome, campo(bloco, 'AegisName'), bonus,
                          script_de(bloco)))
    pendentes.sort()
    return pendentes, sorted(isentos), sorted(sem_trava)


def conferir():
    pendentes, isentos, sem_trava = levanta()
    for sid, nome, aegis, bonus, script in pendentes:
        print u'  %-8d %-28s %-10s %s' % (sid, aegis, bonus[12:], nome)
    print
    print u'%d itens dizem "Indestrutivel" e nao tem o bonus.' % len(pendentes)
    print u'%d armas ficam de fora: machado/maca/cajado/livro/huuma ja sao isentos no C++.' % len(isentos)
    for sid, nome, aegis in sem_trava:
        print u'ATENCAO: %d (%s) e equipamento sombrio - nao ha bonus para travar.' % (sid, aegis)
    return 1 if pendentes else 0


def gerar():
    pendentes, isentos, sem_trava = levanta()
    if not pendentes:
        print u'Nada a fazer: todo item que diz "Indestrutivel" ja tem o bonus.'
        return 0

    partes = [CABECALHO]
    for sid, nome, aegis, bonus, script in pendentes:
        if script is None:
            print u'ERRO: %d (%s) nao tem `Script: |` para copiar.' % (sid, aegis)
            return 2
        partes.append(u'  - Id: %d\n' % sid)
        partes.append(u'    AegisName: %s\n' % aegis)
        partes.append(u'    Script: |\n')
        partes.append(u'      bonus %s;\n' % bonus)
        partes.append(script if script.endswith(u'\n') else script + u'\n')

    texto = u''.join(partes)
    try:
        bruto = texto.encode('ascii')
    except UnicodeEncodeError:
        # Nenhum script do vendor deveria ter byte acentuado; se tiver,
        # gravar cp1252 e a regra do projeto - nunca UTF-8.
        bruto = texto.encode('cp1252')
    aberto = open(SAIDA, 'wb')           # 'wb' + \n: LF, como manda o .gitattributes
    aberto.write(bruto)
    aberto.close()

    print u'Gerado %s' % os.path.relpath(SAIDA, RAIZ)
    print u'  %d itens ganharam o bonus.' % len(pendentes)
    print u'  %d armas fora por tipo isento (machado/maca/cajado/livro/huuma).' % len(isentos)
    for sid, nome, aegis in sem_trava:
        print u'  ATENCAO: %d (%s) e equipamento sombrio - sem bonus possivel.' % (sid, aegis)
    print
    print u'Falta ligar o arquivo, se ainda nao estiver: uma linha'
    print u'  - Path: db/guerra/item_db_indestrutivel.yml'
    print u'no rodape de db/re/item_db.yml.'
    return 0


if __name__ == '__main__':
    if '--conferir' in sys.argv:
        sys.exit(conferir())
    sys.exit(gerar())
