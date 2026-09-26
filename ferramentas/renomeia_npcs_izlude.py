# -*- coding: utf-8 -*-
u"""Traduz o NOME EXIBIDO dos NPCs de Izlude, e as referencias a eles.

    python renomeia_npcs_izlude.py             # aplica
    python renomeia_npcs_izlude.py --conferir  # so mede; sai 1 se faltar

Irma da `renomeia_npcs_brasilis.py`, e existe pelo mesmo motivo: o
`traduz_npcs.py` nao alcanca o nome do NPC, que mora na LINHA DE DECLARACAO,
fora de aspas. Entrou em 2026-09-26, junto com o grupo `izlude` do
`traduz_npcs.py` - Izlude e a cidade de chegada de todo personagem novo (o
Emissario da Nova Ordem desembarca todo mundo la), e o dono pediu que ela
deixasse de ter NPC chamado "Hypnotist".

A FONTE DOS NOMES e o `navi_npc_br.lub` do GRF do bRO, lido por mapa e
coordenada (CLAUDE.md 4.3 e 4.12). Dele vieram, entre outros, a
Hipnotizadora, a Loja Elemental, a Agente do Armazem, o Velhaco e os cinco
da Ilusao Submarina - Sirood, Soup, Raket, Gein e Jerrymon sao Sirud,
Canjica, Lais, Gael e Jeremias no bRO, e o dialogo traduzido no mesmo dia
ja os chama assim.

POR QUE OS NOMES PROPRIOS DE `npc/cities/izlude.txt` FICAM (Bonne, Red,
Cebalis, Dega, Charfri, Cuskoal, Kylick): o bRO chama tres deles de outro
jeito (Paula, Dan, Rami), mas o dialogo deles foi traduzido antes, pelo
grupo `cidades`, e manteve o nome do vendor nos cabecalhos (`[Red]`). Trocar
so o nome flutuante poria um "Dan" na tela falando como "[Red]". Se um dia o
`cidades.cat` adotar os nomes do bRO, entram aqui junto.

POR QUE A ACADEMIA CRIATURA NAO ESTA AQUI: o dialogo dela (~2.500 falas,
npc/re/jobs/novice/academy.txt) ficou para depois, por decisao do dono, e
os nomes do bRO para ela sao quase todos outros (Capitao Chobber,
Bartolomeu, Casamenteira Meire...). Mesmo motivo do paragrafo acima: nome e
cabecalho entram juntos.

TRES FAMILIAS DE CHAVE, e renomear sem elas QUEBRA o NPC:

  - os Assistentes (mercenarios) de Prontera, Izlude e Payon. O gerente
    compara `strnpcinfo(2)` - a parte ESCONDIDA do nome, depois do `#` - com
    "Spear"/"Sword"/"Bow", e o Mercenary Switch monta `disablenpc
    "Mercenary Manager#" + <aquilo>`. O catalogo `izlude.cat` traduz as tres
    palavras para Lanceiro/Espadachim/Arqueiro; aqui a parte escondida muda
    para as mesmas tres, e o prefixo do `disablenpc` muda junto com o nome.
    Rodar so um dos dois lados deixa o gerente sem achar o proprio tipo
    (cai no indice 3, fora do array) e o GM sem conseguir desligar ninguem.
  - os tres NPCs NOSSOS que citam nome de NPC do vendor (armazem_do_cla,
    porteiro_do_treinamento, festival_de_brasilis_encantes) citam as copias
    de PRONTERA e de BRASILIS (`#prontera`, `#prt`, `#bra`). As chaves daqui
    sao de proposito especificas de Izlude (`#izlude`, `#iz`) para nao
    alcanca-las.
  - `Hypnotist#novice` e nao `Hypnotist#`: ha um `Hypnotist#doram08t` em
    Lasagna, outro NPC, que o lasagna_npcs.txt chama por `npctalk`.

O QUE FICA EM INGLES, e por que: `Mercenary Switch` (o bRO tambem o deixa
em ingles - "Mercenary Guild Switch"), `Shorty`, `Edgar`, `Odgnalam`,
`Vigilante Penne` e os nomes proprios acima.

A mesma regra da irma: rodar isto depois de todo `--aplicar izlude`, e
depois de todo `--aplicar cidades` - o `npc/re/cities/izlude.txt` e dos dois
grupos. Linha de comentario do vendor fica intocada.

Roda em Python 2.7.
"""
import io
import os
import sys

# arquivo -> [(nome antigo, nome novo)], na forma em que aparecem nele.
# A ordem importa dentro de cada arquivo: a troca e sequencial por linha.
MAPA = [
    ('npc/re/cities/izlude.txt', [
        (u'Sailor#izlude',          u'Marinheiro#izlude'),
        (u'Soldier#izlude',         u'Soldado#izlude'),
        (u'Talkative Kid#iz',       u'Criança Falante#iz'),
        (u'Talkative Adventurer#iz', u'Aventureiro Falante#iz'),
        (u'Channel Warp Official',  u'Oficial de Canal'),
        # As opcoes do menu do Oficial de Canal. Sao argumento de
        # `callfunc`, que o catalogo nao extrai (o RE_TECNICO protege o
        # primeiro literal de toda chamada) - e o F_IzludeChannel, que as
        # mostra, ja fala portugues.
        (u'Go to copy ',            u'Ir para a cópia '),
    ]),
    ('npc/re/airports/izlude.txt', [
        (u'Airship Staff#izlude',   u'Assistente do Aeroplano#izlude'),
    ]),
    ('npc/re/cities/jawaii.txt', [
        (u'Honeymoon Helper#Izlude', u'Agente Matrimonial#Izlude'),
    ]),
    ('npc/re/guides/guides_izlude.txt', [
        (u'Guide#01izlude',         u'Guia de Izlude#01izlude'),
        (u'Guide#02izlude',         u'Guia de Izlude#02izlude'),
    ]),
    ('npc/re/kafras/kafras.txt', [
        (u'Kafra Employee#iz',      u'Funcionária Kafra#iz'),
    ]),
    ('npc/re/merchants/3rd_trader.txt', [
        (u'Point Merchant#Izlude',  u'Loja Elemental#Izlude'),
    ]),
    ('npc/re/merchants/guild_warehouse.txt', [
        (u'Guild Warehouse Manager#izlude', u'Agente do Armazém#izlude'),
    ]),
    ('npc/re/merchants/shops.txt', [
        (u'Fruit Gardener#iz',      u'Vendedora de Frutas#iz'),
        (u'Butcher#iz',             u'Açougueiro#iz'),
        (u'Vendor from Milk Ranch#iz', u'Vendedora de Leite#iz'),
    ]),
    ('npc/re/other/bulletin_boards.txt', [
        (u'Bulletin Board#5',       u'Quadro de Avisos#5'),
    ]),
    ('npc/re/other/resetskill.txt', [
        (u'Hypnotist#novice',       u'Hipnotizadora#novice'),
    ]),
    # O correio e o MESMO bloco de dialogo em todas as cidades
    # (`::MailBox`), entao o nome muda em todas.
    ('npc/other/mail.txt', [
        (u'Mailbox#',               u'Caixa de Correio#'),
    ]),
    ('npc/re/other/mail.txt', [
        (u'Mailbox#',               u'Caixa de Correio#'),
    ]),
    # Assistentes (mercenarios): ver "TRES FAMILIAS DE CHAVE" acima. O
    # prefixo muda primeiro, e a parte escondida depois, pela forma nova.
    ('npc/other/mercenary_rent.txt', [
        (u'Mercenary Manager#',     u'Gerente de Assistentes#'),
        (u'Mercenary Merchant#',    u'Itens para Assistentes#'),
        (u'Assistentes#Spear',      u'Assistentes#Lanceiro'),
        (u'Assistentes#Sword',      u'Assistentes#Espadachim'),
        (u'Assistentes#Bow',        u'Assistentes#Arqueiro'),
        (u'Mercenary Switch#Spear', u'Mercenary Switch#Lanceiro'),
        (u'Mercenary Switch#Sword', u'Mercenary Switch#Espadachim'),
        (u'Mercenary Switch#Bow',   u'Mercenary Switch#Arqueiro'),
    ]),
    ('npc/re/other/mercenary_rent.txt', [
        (u'Mercenary Manager#',     u'Gerente de Assistentes#'),
        (u'Mercenary Merchant#',    u'Itens para Assistentes#'),
        (u'Assistentes#Sword',      u'Assistentes#Espadachim'),
    ]),
    # O Oficial do Eden e o mesmo bloco (`::eto`) nas 38 copias.
    ('npc/re/quests/eden/eden_common.txt', [
        (u'Eden Teleport Officer#', u'Oficial do Éden#'),
    ]),
    ('npc/re/quests/HelpMeShorty.txt', [
        (u'Black Shadow#fgtg01',    u'Sombra Negra#fgtg01'),
        (u'Mysterious Creature#fgtg01', u'Criatura Misteriosa#fgtg01'),
    ]),
    ('npc/re/quests/mrsmile.txt', [
        (u'Smile Assistance#iz',    u'Campanha Sorriso#iz'),
    ]),
    ('npc/re/quests/quests_13_1.txt', [
        (u'Promotional Staff#iz',   u'Equipe de Promoções#iz'),
    ]),
    # A cadeia inteira da Ilusao Submarina, e nao so a entrada em Izlude:
    # o dialogo de todos eles ja foi traduzido com os nomes do bRO (o
    # catalogo troca `[Gein]` em todo o arquivo), entao o nome flutuante
    # tem de acompanhar tambem no iz_d04_i.
    ('npc/re/quests/quests_illusion_dungeons.txt', [
        (u'Sirood#SRD',             u'Sirud#SRD'),
        (u'Jerrymon#jerry',         u'Jeremias#jerry'),
        (u'Soup#Soup',              u'Canjica#Soup'),
        (u'Raket#Raket',            u'Laís#Raket'),
        (u'Gein#Gein',              u'Gael#Gein'),
    ]),
    ('npc/re/quests/quests_lighthalzen.txt', [
        (u'Scamp#iz',               u'Velhaco#iz'),
    ]),
    ('npc/re/custom/lasagna/lasagna_npcs.txt', [
        (u'Cat Paw Shrimp Merchant#', u'Mercador Doram#'),
        (u'Con-Chliina Crewman#',   u'Marinheiro#'),
    ]),
    ('npc/re/quests/quests_dicastes.txt', [
        (u'\tFish Tails\t',         u'\tRabo de Peixe\t'),
    ]),
]

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATHENA = os.path.join(REPO, 'rathena')
CONFERIR = '--conferir' in sys.argv


def main():
    total = 0
    for rel, pares in MAPA:
        p = os.path.join(RATHENA, rel.replace('/', os.sep))
        d = io.open(p, 'r', encoding='cp1252', newline='').read()
        linhas = d.split(u'\n')
        n = 0
        for i, ln in enumerate(linhas):
            if ln.lstrip().startswith(u'//'):
                continue
            nova = ln
            for velho, novo in pares:
                if velho in nova:
                    n += nova.count(velho)
                    nova = nova.replace(velho, novo)
            linhas[i] = nova
        if n and not CONFERIR:
            io.open(p, 'w', encoding='cp1252',
                    newline='').write(u'\n'.join(linhas))
        print '%-46s %d' % (rel, n)
        total += n
    if CONFERIR:
        print 'total: %d nome(s) ainda em ingles' % total
        return 1 if total else 0
    print 'total: %d troca(s)' % total
    return 0


if __name__ == '__main__':
    sys.exit(main())
