# -*- coding: utf-8 -*-
u"""Gera os catorze monstros e o mapa da Ilusao do Labirinto (prt_mz03_i).

    python monta_ilusao_do_labirinto.py             # gera os tres arquivos
    python monta_ilusao_do_labirinto.py --conferir  # so relata; sai 1 se divergir

O PROBLEMA QUE ISTO RESOLVE

A Ilusao do Labirinto e o mapa `prt_mz03_i`, que o nosso vendor LIGA
(`conf/maps_athena.conf` linha 1383, descomentada) e que este cliente tem
inteiro - `.gat`, `.gnd`, `.rsw`, minimapa e ate o `effecttool`. O que nao
existe e o conteudo: os catorze monstros estao no `db/re/mob_db.yml` como
PLACEHOLDER COMENTADO, duas linhas cada um, so `Id` e `AegisName`:

    #  - Id: 20520
    #    AegisName: ILL_BAPHOMET

Descomentar nao adianta, nao ha o que descomentar - e a mesma situacao da
Glast Heim Sombria (ver `monta_mobs_da_sombria.py`). Mas com uma diferenca
que muda tudo: la havia regra de derivacao (o `_H` e o normal com Level
+30, HP x2, EXP x2, conferida campo a campo). Aqui NAO HA: o ilusional e
outro monstro, com status proprio de nivel 172 a 178. Entao os numeros
deste arquivo nao sao derivados - sao MEDIDOS, um a um.

DE ONDE VEM CADA NUMERO

  - status, HP, elemento, tamanho, raca e drops: das paginas do
    divine-pride dos catorze, em 2026-09-11. Onze delas chegaram como
    screenshot do dono (em portugues do bRO) e as tres restantes (20520,
    20522 e 20533) por leitura direta. Onde as duas fontes se tocam elas
    concordam: HP e defesa batem nos onze, e a lista de drops bate item a
    item - o `Corda Curta` do print e o 25779 da pagina, o `Veneno de
    Cobra` e o 25773, o `Barril de Suco` e o 25772;

  - EXP de base e de classe: da aba Exp da mesma pagina, na linha de 100%;

  - `MvpExp`: metade do `BaseExp`, que e a relacao do PROPRIO vendor no
    Bafome normal (1039: BaseExp 218089, MvpExp 109044). O divine-pride nao
    publica esse campo;

  - `Attack` e `Attack2`: NAO estao publicados em lugar nenhum - o
    divine-pride mostra a faixa ja calculada. Foram invertidos da formula
    do rAthena, e a inversao tem solucao INTEIRA UNICA nos catorze;

  - tempos de andar e de atacar: do monstro original de cada um (medido,
    ver abaixo);

  - nome em portugues: do arquivo.browiki.org, pagina Ilusao_do_Labirinto -
    a fonte do bRO, como manda a regra 3 do CLAUDE.md.

A INVERSAO DO `Attack`, E POR QUE ELA E CONFIAVEL

O que o divine-pride mostra e o que o `status_calc_misc` monta, e nao o
campo do `mob_db`. Para monstro, em renewal (`src/map/status.cpp`):

    faixa fisica min = (Str + Level) + Attack  * 80/100     (linha 2524)
    faixa fisica max = (Str + Level) + Attack  * 120/100    (linha 2543)
    faixa magica min = (Int + Level) + Attack2 * 70/100     (linha 2560)
    faixa magica max = (Int + Level) + Attack2 * 130/100

O `(Str + Level)` e o `status_base_atk` no ramo `default` de renewal
(`status.cpp:2487`, `str = dstr + level`), que e por onde monstro passa.

A formula foi conferida ANTES de ser usada, num monstro que existe dos dois
lados: o `ILL_MERMAN` (20805), `Attack: 2801`, `Attack2: 401`, Str 159,
Int 74, nivel 148. A formula preve 2547-3668 e 502-743; o divine-pride
mostra exatamente 2547-3668 e 502-743.

Invertendo, cada um dos catorze tem UM UNICO inteiro que satisfaz as DUAS
pontas da faixa ao mesmo tempo - as duas divisoes inteiras (80/100 e
120/100) so fecham juntas num valor. Nao ha escolha a fazer, e por isso
estes numeros sao tao bons quanto os publicados.

OS TEMPOS VEM DO MONSTRO ORIGINAL, E ISSO TAMBEM FOI MEDIDO

O divine-pride publica `Speed (cells/sec)` e `ASPD (attacks/sec)`, que sao
`1000/WalkSpeed` e `1000/AttackMotion` - conferido no mesmo ILL_MERMAN
(WalkSpeed 220 -> 4,55; AttackMotion 1225 -> 0,82). O `AttackDelay`, o
`ClientAttackMotion` e o `DamageMotion` ele NAO publica.

Entao comparamos, nos dez que tem monstro original, o que da para medir
contra o que o original traz:

    WalkSpeed     bate em 10 de 10
    AttackMotion  bate em  9 de 10 (dentro do arredondamento de 2 casas)

A excecao e o MVP: o Bafome Caotico mede ASPD 1,74 (=576) contra os 768 do
Bafome normal - ou seja ele ataca mais rapido, e nisso a medicao vence.
Nos outros treze os cinco campos de tempo vem do original, que e a leitura
que os dois medidos sustentam.

Os quatro Novicos nao tem original. Os dois campos que dao para medir
(WalkSpeed 130, AttackMotion 432) batem EXATAMENTE com os de um monstro
so do vendor inteiro que e humanoide e chefe: a Lora (2250, Demihuman,
Ai 21). Os outros tres campos deles vem de la, e essa e a unica parte
deste arquivo que e escolha e nao medicao.

O QUE MAIS FOI CONFERIDO, E DEU O CONTRARIO DO ESPERADO

A coluna "Element" do divine-pride e a tabela de RESISTENCIA, e ela NAO
bate com o `db/re/attr_fix.yml` do rAthena em nenhum dos nove - as duas
tabelas sao diferentes (a de la e a do kRO). Ou seja ela nao serve para
conferir o nivel do elemento, e quem confere e outra coisa: o elemento do
monstro ORIGINAL, que concorda com o chip em SETE dos nove (Bafome Dark/3,
Bafinho Dark/1, Sorrateiro Poison/1, Mosca Wind/2, os dois Mantis Earth/1,
Talo Wind/1). Os dois que discordam do original sao o Ghostring (Ghost 4
no normal, Ghost 2 no ilusional) e o Poporing (Poison 1 e Poison 3), e nos
dois o chip e texto explicito na pagina.

`DamageTaken` tambem foi conferido e NAO entra: 66 dos 193 MVPs do vendor
tem o campo, mas NENHUM dos seis MVPs ilusionais que ja existem aqui tem.

O MAPA E UM LABIRINTO DE PORTAIS - E ISSO E O QUE MAIS IMPORTA AQUI

O chao andavel do `prt_mz03_i` esta partido em 26 pedacos que NAO se
tocam, nem na diagonal: 25 salas de umas 500 celulas mais um punhado de
ruido espalhado pela borda. Nao e defeito do mapa - e o desenho do
Labirinto da Floresta, onde quem liga uma sala na outra sao os portais.

Duas consequencias, e as duas sao armadilha da secao 5 do CLAUDE.md:

  1. spawn com `0,0` sorteia no ruido, e monstro sorteado ali fica
     INALCANCAVEL (o caso do `vis_h01`). Por isso o povoamento daqui e por
     SALA, com area explicita, e o ruido fica de fora;

  2. sem portal nenhum o jogador entra e fica preso numa sala de 500
     celulas, com 24 salas que ele nunca vera.

A fiacao nao precisou ser inventada: o `prt_mz03_i` e o `prt_maze03` com
340 celulas de diferenca em 40.000, e os 73 portais internos que o vendor
escreve para o `prt_maze03` (`npc/warps/dungeons/prt_maze.txt`) tem origem
E destino andaveis no mapa ilusional - os 73. Este gerador copia aquela
fiacao, confere celula por celula contra o `map_cache.dat` do proprio
servidor, e recusa gerar se um portal cair em parede.

E confere mais uma coisa, que e a que de fato importa: que das 26 salas,
as 25 de verdade sejam ALCANCAVEIS a pe e por portal a partir da entrada.
Sao. O 26o pedaco e o ruido, e e o unico que fica fora.

O QUE ELE GERA

    rathena/db/guerra/mob_db_labirinto.yml      os catorze monstros
    rathena/db/import/mob_skill_db.txt          a secao LABIRINTO
    rathena/npc/guerra/ilusao_do_labirinto_mapa.txt   portais e povoamento

O `db/import/mob_skill_db.txt` tem DOIS donos desde 2026-09-11 - este e o
`monta_mobs_da_sombria.py` - e por isso cada um escreve so a sua secao,
pelo `secao_de_arquivo.py`. Gerador que reescrevesse o arquivo inteiro
apagaria os monstros do outro em silencio.

As habilidades sao as do monstro original com o id trocado, como na
Sombria. Os quatro Novicos nao tem original e ficam sem habilidade nenhuma
nesta rodada - esta no PENDENCIAS.md.

DEPOIS DE RODAR

Reiniciar o map-server (ou `@reloadmobdb` + `@reloadscript`). E ligar o
arquivo de monstros, se ainda nao estiver: uma linha
`- Path: db/guerra/mob_db_labirinto.yml` no rodape de `db/re/mob_db.yml`,
que passa a ter QUATRO.
"""

import codecs
import os
import re
import sys
from collections import deque

import confere_celula
import secao_de_arquivo

# Sem isto, imprimir "Bafome Caotico" com acento derruba a ferramenta DEPOIS
# de ela ja ter gravado os arquivos - CLAUDE.md secao 5. O `or` nao e
# enfeite: com a saida redirecionada, `sys.stdout.encoding` e None.
sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout,
                                                               'replace')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOB_DB_RA = os.path.join(RAIZ, 'rathena', 'db', 're', 'mob_db.yml')
SKILL_RA = os.path.join(RAIZ, 'rathena', 'db', 're', 'mob_skill_db.txt')
WARPS_RA = os.path.join(RAIZ, 'rathena', 'npc', 'warps', 'dungeons',
                        'prt_maze.txt')
ITEM_DB = [os.path.join(RAIZ, 'rathena', 'db', 're', nome) for nome in
           ('item_db_equip.yml', 'item_db_etc.yml', 'item_db_usable.yml')]

SAIDA_MOB = os.path.join(RAIZ, 'rathena', 'db', 'guerra', 'mob_db_labirinto.yml')
SAIDA_SKILL = os.path.join(RAIZ, 'rathena', 'db', 'import', 'mob_skill_db.txt')
SAIDA_NPC = os.path.join(RAIZ, 'rathena', 'npc', 'guerra',
                         'ilusao_do_labirinto_mapa.txt')

SECAO = 'LABIRINTO'

MAPA = 'prt_mz03_i'
MAPA_BASE = 'prt_maze03'

# ---------------------------------------------------------------- povoamento
#
# Quantos de CADA tipo comum nascem em CADA uma das 25 salas. Com 8 tipos
# comuns dao 8 x 2 x 25 = 400 monstros no mapa, que e a densidade das outras
# ilusionais do vendor ajustada ao tamanho daqui (o ant_d02_i poe 200 num
# mapa bem menor).
POR_SALA = 2

# Renascimento, em ms - o mesmo que o vendor usa nas outras ilusionais.
RENASCE = 5000

# Por onde se entra e para onde se sai. A entrada e a sala 14, que e a mesma
# por onde se entra no prt_maze03 (o portal do prt_maze02 cai em 182,88).
ENTRADA = (182, 88)
SAIDA_CELULA = (182, 85)
SAIDA_DESTINO = ('prt_maze01', 99, 25)

# ------------------------------------------------------------ os catorze
#
# `base` e o AegisName do monstro original, de onde saem os cinco campos de
# tempo, o `SkillRange`/`ChaseRange`, o `Ai` e as habilidades. None nos
# quatro Novicos, que nao tem original.
#
# `amotion` so aparece quando a medicao DISCORDA do original (o MVP).
#
# `drops` e uma lista de (id do item, taxa em n/10000). Carta e o ultimo, e
# leva StealProtected.
MONSTROS = [
    dict(id=20520, aegis='ILL_BAPHOMET', nome='Chaos Baphomet',
         pt=u'Bafomé Caótico', base='BAPHOMET', nivel=178, hp=21278744,
         base_exp=4255749, job_exp=2979024, mvp=True,
         atk=6141, atk2=3168, defesa=343, mdef=122,
         stats=(276, 188, 55, 267, 244, 99), alcance=2,
         tamanho='Large', raca='Demon', elemento='Dark', nivel_elemento=3,
         amotion=576, classe='Boss',
         drops=[(6004, 1000), (1466, 150), (25780, 5000), (1181, 100),
                (923, 3500), (1231, 200), (512, 1), (27334, 1)],
         mvp_drops=[(617, 3000), (616, 4000), (12246, 5000)]),
    dict(id=20521, aegis='ILL_ANDREA', nome='Chaos Andrea',
         pt=u'Andrea', base=None, nivel=177, hp=1057547,
         base_exp=96141, job_exp=67298,
         atk=4248, atk2=1337, defesa=330, mdef=110,
         stats=(192, 122, 51, 175, 188, 68), alcance=2,
         tamanho='Medium', raca='Demihuman', elemento='Neutral',
         nivel_elemento=3, classe='Boss',
         drops=[(7054, 5000), (7321, 2500), (2648, 100), (607, 50),
                (608, 50), (27343, 1)]),
    dict(id=20522, aegis='ILL_ANES', nome='Chaos Anes',
         pt=u'Agnes', base=None, nivel=177, hp=1057444,
         base_exp=96131, job_exp=67292,
         atk=4314, atk2=1369, defesa=327, mdef=110,
         stats=(195, 122, 50, 174, 178, 61), alcance=2,
         tamanho='Medium', raca='Demihuman', elemento='Neutral',
         nivel_elemento=3, classe='Boss',
         drops=[(7054, 5000), (7321, 3500), (5126, 100), (608, 50),
                (607, 50), (27343, 1)]),
    dict(id=20523, aegis='ILL_SILVANO', nome='Chaos Silvano',
         pt=u'Silvano', base=None, nivel=177, hp=1057650,
         base_exp=96150, job_exp=67305,
         atk=4292, atk2=1385, defesa=333, mdef=111,
         stats=(194, 122, 52, 176, 184, 57), alcance=2,
         tamanho='Medium', raca='Demihuman', elemento='Neutral',
         nivel_elemento=3, classe='Boss',
         drops=[(7054, 5000), (7321, 3500), (2518, 100), (607, 50),
                (608, 50), (27343, 1)]),
    dict(id=20524, aegis='ILL_CECILIA', nome='Chaos Cecilia',
         pt=u'Cecília', base=None, nivel=177, hp=1056411,
         base_exp=96037, job_exp=67226,
         atk=4359, atk2=1392, defesa=297, mdef=111,
         stats=(197, 122, 40, 177, 186, 61), alcance=2,
         tamanho='Medium', raca='Demihuman', elemento='Neutral',
         nivel_elemento=3, classe='Boss',
         drops=[(7054, 5000), (7321, 3500), (2649, 100), (607, 50),
                (608, 50), (27343, 1)]),
    dict(id=20525, aegis='ILL_BAPHOMET_J', nome='Chaos Baphomet Jr',
         pt=u'Bafinho Caótico', base='BAPHOMET_', nivel=177, hp=1057444,
         base_exp=173089, job_exp=121125,
         atk=4093, atk2=847, defesa=327, mdef=108,
         stats=(185, 101, 50, 158, 178, 77), alcance=1,
         tamanho='Small', raca='Formless', elemento='Dark', nivel_elemento=1,
         drops=[(7054, 2500), (923, 1750), (508, 1750), (984, 100),
                (25779, 1250), (13106, 25), (27335, 1)]),
    dict(id=20526, aegis='ILL_SIDE_WINDER', nome='Chaos Side Winder',
         pt=u'Sorrateiro Caótico', base='SIDE_WINDER', nivel=176, hp=1051983,
         base_exp=172143, job_exp=120499,
         atk=4026, atk2=832, defesa=341, mdef=108,
         stats=(183, 94, 55, 156, 177, 70), alcance=1,
         tamanho='Medium', raca='Brute', elemento='Poison', nivel_elemento=1,
         drops=[(926, 2500), (937, 1750), (972, 5), (1119, 25),
                (509, 700), (25773, 1250), (27336, 1)]),
    dict(id=20527, aegis='ILL_HUNTER_FLY', nome='Chaos Hunter Fly',
         pt=u'Mosca Caótica', base='HUNTER_FLY', nivel=175, hp=1045087,
         base_exp=171014, job_exp=119710,
         atk=3916, atk2=817, defesa=313, mdef=107,
         stats=(179, 115, 46, 154, 189, 66), alcance=1,
         tamanho='Small', raca='Formless', elemento='Wind', nivel_elemento=2,
         drops=[(943, 2500), (999, 50), (912, 1750), (756, 70),
                (25772, 1250), (996, 20), (27337, 1)]),
    dict(id=20528, aegis='ILL_MANTIS', nome='Chaos Mantis',
         pt=u'Louva-Caos', base='MANTIS', nivel=174, hp=1039216,
         base_exp=170053, job_exp=119037,
         atk=3937, atk2=817, defesa=315, mdef=71,
         stats=(181, 96, 47, 155, 184, 67), alcance=1,
         tamanho='Medium', raca='Insect', elemento='Earth', nivel_elemento=1,
         drops=[(1031, 2250), (993, 60), (943, 1000), (25774, 1250),
                (721, 10), (507, 500), (27338, 1)]),
    dict(id=20529, aegis='ILL_GHOSTRING', nome='Chaos Ghostring',
         pt=u'Ghostring Caótico', base='GHOSTRING', nivel=173, hp=1033446,
         base_exp=169110, job_exp=118377,
         atk=3979, atk2=834, defesa=320, mdef=71,
         stats=(184, 87, 49, 159, 182, 61), alcance=1,
         tamanho='Medium', raca='Demon', elemento='Ghost', nivel_elemento=2,
         drops=[(1059, 2500), (7166, 1750), (911, 1000), (7321, 1750),
                (25775, 1250), (27339, 1)]),
    dict(id=20530, aegis='ILL_KILLER_MANTIS', nome='Chaos Killer Mantis',
         pt=u'Mantis Caótico', base='KILLER_MANTIS', nivel=177, hp=1058167,
         base_exp=173154, job_exp=121280,
         atk=4027, atk2=842, defesa=348, mdef=72,
         stats=(182, 105, 57, 157, 194, 47), alcance=1,
         tamanho='Medium', raca='Insect', elemento='Earth', nivel_elemento=1,
         drops=[(1031, 2500), (943, 1250), (607, 15), (993, 70),
                (13158, 25), (25776, 1250), (27340, 1)]),
    dict(id=20531, aegis='ILL_POPORING', nome='Chaos Poporing',
         pt=u'Poporing Caótico', base='POPORING', nivel=173, hp=1032638,
         base_exp=168976, job_exp=118283,
         atk=3828, atk2=797, defesa=296, mdef=70,
         stats=(177, 85, 41, 152, 172, 29), alcance=1,
         tamanho='Medium', raca='Plant', elemento='Poison', nivel_elemento=3,
         drops=[(938, 2500), (511, 1000), (608, 20), (7321, 1750),
                (25778, 1250), (985, 50), (27341, 1)]),
    dict(id=20532, aegis='ILL_STEM_WORM', nome='Chaos Stem Worm',
         pt=u'Talo Caótico', base='STEM_WORM', nivel=172, hp=1027071,
         base_exp=168066, job_exp=117646,
         atk=3917, atk2=804, defesa=307, mdef=70,
         stats=(180, 95, 45, 156, 187, 69), alcance=1,
         tamanho='Medium', raca='Plant', elemento='Wind', nivel_elemento=1,
         drops=[(7012, 2500), (509, 1000), (984, 100), (997, 20),
                (25777, 1250), (608, 20), (27342, 1)]),
    # O invocado do Bafinho: um decimo do HP, sem EXP e sem drop nenhum -
    # senao o MVP vira fonte infinita da Gold Lux que o 20525 derruba.
    dict(id=20533, aegis='G_ILL_BAPHOMET_J', nome='Chaos Baphomet Jr',
         pt=u'Bafinho Caótico', base='G_BAPHOMET_', nivel=177, hp=105744,
         base_exp=0, job_exp=0,
         atk=4093, atk2=847, defesa=327, mdef=108,
         stats=(185, 101, 50, 158, 178, 77), alcance=1,
         tamanho='Small', raca='Formless', elemento='Dark', nivel_elemento=1,
         drops=[]),
]

# Os oito comuns, que sao os que povoam as salas. Os quatro Novicos e o MVP
# nascem pelo script (npc/guerra/ilusao_do_labirinto.txt), nao por linha de
# spawn - eles tem posicao fixa e renascimento de uma hora.
COMUNS = [20525, 20526, 20527, 20528, 20529, 20530, 20531, 20532]

# Os quatro Novicos nao tem monstro original, e os dois campos que dao para
# medir (WalkSpeed 130 e AttackMotion 432) batem exatamente com os da Lora
# (2250), o unico humanoide-chefe do vendor com esse par. Os outros tres
# campos vem de la.
NOVICO_TEMPOS = dict(walk=130, adelay=1600, amotion=432, cliam=360, dmgm=360,
                     ai='21', skill_range=10, chase_range=12)

# ------------------------------------------------------------- a invocacao
#
# Copiar as habilidades do monstro original cru tem UM caso que nao funciona,
# e ele nao da erro nenhum: a linha de NPC_SUMMONSLAVE traz o ID DO ESCRAVO
# DO ORIGINAL. Medido em jogo em 2026-09-11, com o mapa povoado: o nosso
# Ghostring Caotico (nivel 173) herdou do Ghostring comum um
# `onspawn -> 1186` e encheu o labirinto de DUZENTOS E CINQUENTA Cochichos de
# nivel 66 - cinco por Ghostring, cinquenta Ghostrings. O mapa tinha 654
# monstros no lugar de 404, e nada no log dizia isso.
#
# O que o kRO faz, conferido na aba Skills do divine-pride dos tres:
#
#   20529 Ghostring Caotico  - NENHUMA invocacao (tem Teleport, Heal, Hiding,
#                              Soul Strike, Dark Breath, Ghost Attack...)
#   20530 Mantis Caotico     - NENHUMA invocacao
#   20520 Bafome Caotico     - TEM "Call Slave" e "Summon Slave"
#
# Dai a regra, e ela explica por que o 20533 existe: invocacao cujo escravo
# tem contraparte ilusional passa a invocar A CONTRAPARTE; invocacao sem
# contraparte e DESCARTADA. As duas pontas batem com o kRO nos tres casos.
INVOCACOES = {
    '1101': '20525',    # Bafinho -> Bafinho Caotico
    '1431': '20533',    # Bafinho invocado -> o nosso invocado
}
SKILLS_DE_INVOCACAO = set(['196'])   # NPC_SUMMONSLAVE
COLUNA_SKILL = 3
COLUNA_VAL1 = 12

CABECA_MOB = u"""\
###########################################################################
# Guerra do Emperium - os monstros da Ilusao do Labirinto (prt_mz03_i)
###########################################################################
#
# GERADO por ferramentas/monta_ilusao_do_labirinto.py. Editar a mao morre na
# proxima rodada - o arquivo e reescrito inteiro. De onde sai cada numero, e
# a medicao que o sustenta, estao no cabecalho daquela ferramenta.
#
# Sao os ids 20520..20533, que o vendor traz COMENTADOS (so Id e AegisName) e
# que o rAthena nunca implementou. Ao contrario da Glast Heim Sombria, aqui
# nao ha regra de derivacao: sao monstros proprios, de nivel 172 a 178, e
# todo status foi medido no divine-pride em 2026-09-11.
#
# `Attack` e `Attack2` nao sao publicados em lugar nenhum - foram invertidos
# da formula do renewal (status.cpp:2524 e :2543) e a inversao tem solucao
# inteira UNICA nos catorze.
#
# O nome que o jogador le e o `JapaneseName` (o `memcpy(md->name,
# md->db->jname)` do mob.cpp); o `Name` fica em ingles porque e a chave de
# @monster e dos scripts.
#
# Alcancado por uma linha `- Path: db/guerra/mob_db_labirinto.yml` no rodape
# de db/re/mob_db.yml, que passa a ter quatro.
#
# Encoding: cp1252, como todo texto que o jogo le (CLAUDE.md secao 4.1).
#
###########################################################################

Header:
  Type: MOB_DB
  Version: 5

Body:
"""

CABECA_SKILL = """\
//===========================================================================
// Guerra do Emperium - habilidades dos monstros da Ilusao do Labirinto
//===========================================================================
//
// GERADO por ferramentas/monta_ilusao_do_labirinto.py. Editar a mao morre na
// proxima rodada.
//
// ESTE ARQUIVO TEM DOIS DONOS. A outra secao e a da Glast Heim Sombria, e
// quem a escreve e o monta_mobs_da_sombria.py. Cada gerador troca so a
// propria secao (ferramentas/secao_de_arquivo.py) - um que reescrevesse o
// arquivo inteiro apagaria os monstros do outro em silencio, porque monstro
// sem linha aqui simplesmente nao conjura, sem erro nenhum.
//
// As linhas sao as do monstro ORIGINAL de cada ilusional, com o id trocado.
// Os quatro Novicos (20521..20524) nao tem original e por isso nao aparecem
// aqui - esta no PENDENCIAS.md.
//
// A INVOCACAO E A UNICA LINHA QUE NAO SE COPIA CRUA. O NPC_SUMMONSLAVE traz o
// id do escravo DO ORIGINAL, e copiar isso encheu o mapa de 250 Cochichos de
// nivel 66 (o Ghostring comum invoca cinco por spawn) - medido em jogo em
// 2026-09-11. Aqui, invocacao cujo escravo tem contraparte ilusional passa a
// invocar a contraparte (1101 -> 20525, 1431 -> 20533) e invocacao sem
// contraparte e descartada. As duas pontas batem com a aba Skills do kRO: o
// Ghostring e o Mantis ilusionais nao invocam nada, e o Bafome Caotico invoca.
//
// MobID,Dummy value (info only),State,SkillID,SkillLv,Rate,CastTime,Delay,Cancelable,Target,Condition type,Condition value,val1,val2,val3,val4,val5,Emotion,Chat
//===========================================================================
"""


def le(caminho):
    aberto = open(caminho, 'rb')
    try:
        return aberto.read()
    finally:
        aberto.close()


def grava(caminho, dados):
    aberto = open(caminho, 'wb')
    try:
        aberto.write(dados)
    finally:
        aberto.close()


# ------------------------------------------------------------------ mob_db

def registros_do_vendor():
    u"""{AegisName: {campo: valor}} dos registros NAO comentados do mob_db."""
    texto = le(MOB_DB_RA).replace('\r\n', '\n')
    fora = {}
    marcas = list(re.finditer(r'^  - Id: (\d+)$', texto, re.M))
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        bloco = texto[m.end():fim]
        campos = {'Id': m.group(1)}
        for linha in bloco.split('\n'):
            mm = re.match(r'^    (\w+): (.*)$', linha)
            if mm:
                campos[mm.group(1)] = mm.group(2)
        if 'AegisName' in campos:
            fora[campos['AegisName']] = campos
    return fora


def nomes_de_item():
    u"""{id do item: AegisName}, dos tres item_db do vendor."""
    fora = {}
    for caminho in ITEM_DB:
        texto = le(caminho).replace('\r\n', '\n')
        for m in re.finditer(r'^  - Id: (\d+)\n    AegisName: (\S+)$',
                             texto, re.M):
            fora[int(m.group(1))] = m.group(2)
    return fora


def monta_mob(bicho, vendor, itens):
    u"""O registro YAML de um monstro."""
    if bicho['base']:
        if bicho['base'] not in vendor:
            raise SystemExit('o monstro original %s nao esta no mob_db'
                             % bicho['base'])
        orig = vendor[bicho['base']]
        tempos = dict(walk=int(orig['WalkSpeed']),
                      adelay=int(orig['AttackDelay']),
                      amotion=int(orig['AttackMotion']),
                      cliam=int(orig['ClientAttackMotion']),
                      dmgm=int(orig['DamageMotion']),
                      ai=orig.get('Ai', '06'),
                      skill_range=int(orig.get('SkillRange', 10)),
                      chase_range=int(orig.get('ChaseRange', 12)))
    else:
        tempos = dict(NOVICO_TEMPOS)
    if bicho.get('amotion'):
        tempos['amotion'] = bicho['amotion']

    forca, agi, vit, intel, dex, luk = bicho['stats']
    saida = []
    p = saida.append
    p(u'  - Id: %d\n' % bicho['id'])
    p(u'    AegisName: %s\n' % bicho['aegis'])
    p(u'    Name: %s\n' % bicho['nome'])
    p(u'    JapaneseName: "%s"\n' % bicho['pt'])
    p(u'    Level: %d\n' % bicho['nivel'])
    p(u'    Hp: %d\n' % bicho['hp'])
    p(u'    BaseExp: %d\n' % bicho['base_exp'])
    p(u'    JobExp: %d\n' % bicho['job_exp'])
    if bicho.get('mvp'):
        # metade do BaseExp, que e a relacao do proprio vendor no 1039
        p(u'    MvpExp: %d\n' % (bicho['base_exp'] // 2))
    p(u'    Attack: %d\n' % bicho['atk'])
    p(u'    Attack2: %d\n' % bicho['atk2'])
    p(u'    Defense: %d\n' % bicho['defesa'])
    p(u'    MagicDefense: %d\n' % bicho['mdef'])
    p(u'    Str: %d\n' % forca)
    p(u'    Agi: %d\n' % agi)
    p(u'    Vit: %d\n' % vit)
    p(u'    Int: %d\n' % intel)
    p(u'    Dex: %d\n' % dex)
    p(u'    Luk: %d\n' % luk)
    p(u'    AttackRange: %d\n' % bicho['alcance'])
    p(u'    SkillRange: %d\n' % tempos['skill_range'])
    p(u'    ChaseRange: %d\n' % tempos['chase_range'])
    p(u'    Size: %s\n' % bicho['tamanho'])
    p(u'    Race: %s\n' % bicho['raca'])
    p(u'    Element: %s\n' % bicho['elemento'])
    p(u'    ElementLevel: %d\n' % bicho['nivel_elemento'])
    p(u'    WalkSpeed: %d\n' % tempos['walk'])
    p(u'    AttackDelay: %d\n' % tempos['adelay'])
    p(u'    AttackMotion: %d\n' % tempos['amotion'])
    p(u'    ClientAttackMotion: %d\n' % tempos['cliam'])
    p(u'    DamageMotion: %d\n' % tempos['dmgm'])
    p(u'    Ai: %s\n' % tempos['ai'])
    if bicho.get('classe'):
        p(u'    Class: %s\n' % bicho['classe'])
    if bicho.get('mvp'):
        p(u'    Modes:\n      Mvp: true\n')
    if bicho.get('mvp_drops'):
        p(u'    MvpDrops:\n')
        for item, taxa in bicho['mvp_drops']:
            p(u'      - Item: %s\n        Rate: %d\n' % (item_nome(item, itens),
                                                         taxa))
    if bicho['drops']:
        p(u'    Drops:\n')
        for i, (item, taxa) in enumerate(bicho['drops']):
            p(u'      - Item: %s\n        Rate: %d\n' % (item_nome(item, itens),
                                                         taxa))
            # a carta e sempre a ultima, e o divine-pride a marca como
            # protegida contra roubo - igual as do vendor
            if i == len(bicho['drops']) - 1 and taxa <= 10:
                p(u'        StealProtected: true\n')
    return u''.join(saida)


def item_nome(item_id, itens):
    if item_id not in itens:
        raise SystemExit('o item %d nao existe no item_db - drop sem fonte'
                         % item_id)
    return itens[item_id]


def linhas_de_habilidade(texto, velho, novo, nome, relato_invoc):
    u"""As linhas do mob_skill_db do monstro original, com o id novo.

    A INVOCACAO E O CASO QUE NAO PODE SER COPIADO CRU - ver o cabecalho.
    """
    fora = []
    for linha in texto.replace('\r\n', '\n').split('\n'):
        if not linha.startswith('%d,' % velho):
            continue
        campos = linha.split(',')
        if len(campos) > COLUNA_VAL1 and campos[COLUNA_SKILL] in SKILLS_DE_INVOCACAO:
            alvo = campos[COLUNA_VAL1].strip()
            if alvo in INVOCACOES:
                relato_invoc.append((novo, alvo, INVOCACOES[alvo], 'trocado'))
                campos[COLUNA_VAL1] = INVOCACOES[alvo]
            else:
                relato_invoc.append((novo, alvo, None, 'descartado'))
                continue
        campos[0] = str(novo)
        # coluna 1 e o "Dummy value (info only)" - so serve para ler
        if len(campos) > 1 and '@' in campos[1]:
            campos[1] = nome + '@' + campos[1].split('@', 1)[1]
        fora.append(','.join(campos))
    return fora


def monta_mobs():
    vendor = registros_do_vendor()
    itens = nomes_de_item()
    skill_texto = le(SKILL_RA)

    partes = [CABECA_MOB]
    skills = []
    relato = []
    relato_invoc = []
    for bicho in MONSTROS:
        partes.append(monta_mob(bicho, vendor, itens))
        linhas = []
        if bicho['base']:
            velho = int(vendor[bicho['base']]['Id'])
            linhas = linhas_de_habilidade(skill_texto, velho, bicho['id'],
                                          bicho['nome'], relato_invoc)
        skills.extend(linhas)
        relato.append((bicho['id'], bicho['aegis'], bicho['pt'], len(linhas)))
    return u''.join(partes), skills, relato, relato_invoc


# -------------------------------------------------------------------- mapa

VIZINHOS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if (dx, dy) != (0, 0)]


def salas():
    u"""(xs, ys, celula->sala, lista de salas) do mapa ilusional.

    Sala e pedaco de chao andavel conectado - com diagonal, que e como o
    jogador anda. Sao 26: as 25 do labirinto mais um punhado de ruido de
    borda espalhado pelo mapa inteiro.
    """
    dados = confere_celula.carrega(MAPA)
    if dados is None:
        raise SystemExit('o mapa %s nao esta em map_cache nenhum - o servidor '
                         'nao o conhece' % MAPA)
    xs, ys, celulas, _cache = dados
    de_qual = [-1] * (xs * ys)
    grupos = []
    for inicio in range(xs * ys):
        if de_qual[inicio] >= 0 or celulas[inicio] != '\0':
            continue
        atual = len(grupos)
        fila = deque([inicio])
        de_qual[inicio] = atual
        membros = []
        while fila:
            i = fila.popleft()
            membros.append(i)
            x, y = i % xs, i // xs
            for dx, dy in VIZINHOS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < xs and 0 <= ny < ys:
                    j = ny * xs + nx
                    if de_qual[j] < 0 and celulas[j] == '\0':
                        de_qual[j] = atual
                        fila.append(j)
        grupos.append(membros)
    return xs, ys, celulas, de_qual, grupos


def portais_do_original():
    u"""Os portais internos do prt_maze03: [(nome, ox, oy, [(dx, dy), ...])].

    Dois deles nao sao `warp` e sim script com destino sorteado entre quatro
    (os `#mazewarp5303` e `#mazewarp5339` do vendor); por isso o destino e
    lista, e nao par.
    """
    texto = le(WARPS_RA).replace('\r\n', '\n')
    fora = []
    for linha in texto.split('\n'):
        m = re.match(r'^%s,(\d+),(\d+),\d+\twarp\tmazewarp(\d+)\t'
                     r'\d+,\d+,(\w+),(\d+),(\d+)' % MAPA_BASE, linha)
        if not m:
            continue
        if m.group(4) != MAPA_BASE:
            continue      # o que sai do mapa vira a nossa saida, mais abaixo
        fora.append((m.group(3), int(m.group(1)), int(m.group(2)),
                     [(int(m.group(5)), int(m.group(6)))]))
    for m in re.finditer(r'^%s,(\d+),(\d+),\d+\tscript\t#mazewarp(\d+)\t'
                         r'45,1,1,\{(.*?)^\}' % MAPA_BASE, texto, re.M | re.S):
        destinos = [(int(d.group(1)), int(d.group(2))) for d in
                    re.finditer(r'warp "%s",(\d+),(\d+);' % MAPA_BASE,
                                m.group(4))]
        fora.append((m.group(3), int(m.group(1)), int(m.group(2)), destinos))
    fora.sort(key=lambda p: int(p[0]))
    return fora


def confere_mapa():
    u"""Valida a fiacao contra o map_cache e devolve (salas uteis, portais).

    Recusa gerar se um portal cair em parede, ou se alguma sala ficar
    inalcancavel a partir da entrada - as duas coisas produzem monstro que
    ninguem mata e jogador que nao sai do lugar, e nenhuma das duas da erro
    no servidor.
    """
    xs, ys, celulas, de_qual, grupos = salas()

    def sala_de(x, y):
        if not (0 <= x < xs and 0 <= y < ys):
            return None
        s = de_qual[y * xs + x]
        return None if s < 0 else s

    portais = portais_do_original()
    ruins = []
    grafo = {}
    for nome, ox, oy, destinos in portais:
        origem = sala_de(ox, oy)
        if origem is None:
            ruins.append((nome, ox, oy, 'origem em parede'))
            continue
        for dx, dy in destinos:
            alvo = sala_de(dx, dy)
            if alvo is None:
                ruins.append((nome, dx, dy, 'destino em parede'))
                continue
            grafo.setdefault(origem, set()).add(alvo)
    if ruins:
        for nome, x, y, o_que in ruins:
            print u'  PORTAL RUIM: %s em %d,%d - %s' % (nome, x, y, o_que)
        raise SystemExit('a fiacao do %s nao vale para o %s' % (MAPA_BASE, MAPA))

    entrada = sala_de(*ENTRADA)
    if entrada is None:
        raise SystemExit('a entrada %d,%d nao e celula andavel' % ENTRADA)
    vistas = set([entrada])
    fila = deque([entrada])
    while fila:
        s = fila.popleft()
        for d in grafo.get(s, ()):
            if d not in vistas:
                vistas.add(d)
                fila.append(d)

    # o ruido de borda e o pedaco que nenhum portal toca; ele fica de fora do
    # povoamento, e e por isso que nao se usa `0,0` no spawn (CLAUDE.md 5).
    uteis = []
    for i, membros in enumerate(grupos):
        if i not in vistas:
            continue
        X = [m % xs for m in membros]
        Y = [m // xs for m in membros]
        # O centro do spawn tem de ser celula ANDAVEL, e nao o meio da caixa:
        # quando as 8 tentativas na area falham, o mob_spawn testa a celula
        # central e, se ela for parede, sorteia no MAPA INTEIRO (mob.cpp:1152)
        # - ou seja um centro em parede pode jogar monstro no ruido de borda,
        # que e exatamente o que o povoamento por sala existe para evitar.
        (cx, cy), _folga = confere_celula.centro(xs, ys, celulas, membros)
        uteis.append(dict(sala=i, celulas=len(membros), cx=cx, cy=cy,
                          x0=min(X), x1=max(X), y0=min(Y), y1=max(Y)))
    fora_de_alcance = [(i, len(g)) for i, g in enumerate(grupos)
                       if i not in vistas]
    return uteis, fora_de_alcance, portais, len(grupos)


def monta_npc(uteis, portais, fora_de_alcance, total_salas):
    u"""O arquivo de NPC com os portais e o povoamento."""
    por_id = dict((b['id'], b) for b in MONSTROS)
    l = []
    p = l.append
    p(u'//===== Guerra do Emperium ===================================\n')
    p(u'//= Ilusao do Labirinto - portais e povoamento de %s\n' % MAPA)
    p(u'//===========================================================\n')
    p(u'//= ARQUIVO GERADO por ferramentas/monta_ilusao_do_labirinto.py.\n')
    p(u'//= Editar a mao funciona ate a proxima geracao, que apaga tudo.\n')
    p(u'//=\n')
    p(u'//= A MECANICA NAO ESTA AQUI. A Fenda Retorcida, os quatro\n')
    p(u'//= Novicos, o Bafome Caotico e a invencibilidade dele moram em\n')
    p(u'//= npc/guerra/ilusao_do_labirinto.txt, que e escrito a mao.\n')
    p(u'//=\n')
    p(u'//= POR QUE O POVOAMENTO E SALA A SALA, E NAO `0,0`\n')
    p(u'//=\n')
    p(u'//= O chao andavel deste mapa esta partido em %d pedacos que nao\n'
      % total_salas)
    p(u'//= se tocam nem na diagonal - e um labirinto de portais, como o\n')
    p(u'//= prt_maze03 de onde ele foi desenhado. %d sao salas de verdade\n'
      % len(uteis))
    p(u'//= e o resto e ruido de borda. Spawn com `0,0` sorteia no ruido, e\n')
    p(u'//= monstro sorteado la fica INALCANCAVEL sem uma linha de erro -\n')
    p(u'//= e a armadilha do vis_h01, na secao 5 do CLAUDE.md.\n')
    p(u'//=\n')
    p(u'//= Cada sala recebe %d de cada um dos %d tipos comuns.\n'
      % (POR_SALA, len(COMUNS)))
    p(u'//=\n')
    p(u'//= Em spawn com area, `<xs>,<ys>` e RAIO+1 e nao lado: o mob_spawn\n')
    p(u'//= chama map_search_freecell com xs-1 (mob.cpp:1149). As areas\n')
    p(u'//= daqui sao a caixa exata de cada sala, calculada do map_cache.\n')
    p(u'//=\n')
    p(u'//= OS PORTAIS\n')
    p(u'//=\n')
    p(u'//= Sao os %d portais internos que o vendor escreve para o\n'
      % len(portais))
    p(u'//= prt_maze03, com o mesmo numero no nome (mazewarp5301 ->\n')
    p(u'//= ilusaolab5301). Os dois mapas diferem em 340 celulas de 40.000, e\n')
    p(u'//= o gerador confere que origem E destino dos %d sao andaveis aqui,\n'
      % len(portais))
    p(u'//= e que as %d salas se alcancam a partir da entrada. Se um dia\n'
      % len(uteis))
    p(u'//= deixarem de ser, ele recusa gerar em vez de publicar labirinto\n')
    p(u'//= sem saida.\n')
    if fora_de_alcance:
        p(u'//=\n')
        p(u'//= Fora do povoamento (ruido de borda, nenhum portal chega la):\n')
        for sala, quantas in fora_de_alcance:
            p(u'//=   pedaco %d, %d celulas\n' % (sala, quantas))
    p(u'//===========================================================\n')
    p(u'\n')
    p(u'// --------------------------------------------------- portais\n')
    for nome, ox, oy, destinos in portais:
        if len(destinos) == 1:
            p(u'%s,%d,%d,0\twarp\tilusaolab%s\t1,1,%s,%d,%d\n'
              % (MAPA, ox, oy, nome, MAPA, destinos[0][0], destinos[0][1]))
        else:
            p(u'%s,%d,%d,0\tscript\t#ilusaolab%s\t45,1,1,{\n'
              % (MAPA, ox, oy, nome))
            p(u'\tswitch(rand(%d)) {\n' % len(destinos))
            for i, (dx, dy) in enumerate(destinos):
                p(u'\t\tcase %d: warp "%s",%d,%d; end;\n' % (i, MAPA, dx, dy))
            p(u'\t}\n}\n')
    p(u'\n')
    p(u'// A saida. No prt_maze03 esta celula leva ao andar de baixo; aqui ela\n')
    p(u'// devolve o jogador para o lado de fora da Fenda Retorcida.\n')
    p(u'%s,%d,%d,0\twarp\tilusaolabsaida\t1,1,%s,%d,%d\n'
      % (MAPA, SAIDA_CELULA[0], SAIDA_CELULA[1], SAIDA_DESTINO[0],
         SAIDA_DESTINO[1], SAIDA_DESTINO[2]))
    p(u'\n')
    p(u'// ------------------------------------------------ povoamento\n')
    p(u'// O nome na tela vem da TERCEIRA COLUNA, e nao do mob_db: `--ja--`\n')
    p(u'// e o que manda usar o JapaneseName, que e onde esta o portugues.\n')
    for sala in uteis:
        cx, cy = sala['cx'], sala['cy']
        rx = max(cx - sala['x0'], sala['x1'] - cx) + 1
        ry = max(cy - sala['y0'], sala['y1'] - cy) + 1
        p(u'// sala %d - %d celulas, de %d,%d a %d,%d\n'
          % (sala['sala'], sala['celulas'], sala['x0'], sala['y0'],
             sala['x1'], sala['y1']))
        for mob in COMUNS:
            p(u'%s,%d,%d,%d,%d\tmonster\t--ja--\t%d,%d,%d\n'
              % (MAPA, cx, cy, rx, ry, mob, POR_SALA, RENASCE))
    return u''.join(l)


def monta():
    texto_mob, skills, relato, relato_invoc = monta_mobs()
    uteis, fora_de_alcance, portais, total_salas = confere_mapa()
    texto_npc = monta_npc(uteis, portais, fora_de_alcance, total_salas)
    corpo_skill = CABECA_SKILL + '\n'.join(skills) + '\n'
    return (texto_mob, corpo_skill, texto_npc, relato, uteis, portais,
            relato_invoc)


def gerar():
    (texto_mob, corpo_skill, texto_npc, relato, uteis, portais,
     relato_invoc) = monta()

    grava(SAIDA_MOB, texto_mob.encode('cp1252'))
    velho = le(SAIDA_SKILL) if os.path.exists(SAIDA_SKILL) else ''
    grava(SAIDA_SKILL, secao_de_arquivo.troca(velho, SECAO, corpo_skill))
    grava(SAIDA_NPC, texto_npc.encode('cp1252'))

    print u'Gerado %s' % os.path.relpath(SAIDA_MOB, RAIZ)
    print u'Gerado %s (secao %s)' % (os.path.relpath(SAIDA_SKILL, RAIZ), SECAO)
    print u'Gerado %s' % os.path.relpath(SAIDA_NPC, RAIZ)
    print
    print u'  %-7s %-22s %-22s %s' % ('Id', 'AegisName', 'Nome PT', 'habilidades')
    for mob_id, aegis, pt, n in relato:
        print u'  %-7d %-22s %-22s %d' % (mob_id, aegis, pt, n)
    if relato_invoc:
        print
        print u'  Invocacoes ajustadas (o escravo do original nao serve aqui):'
        for mob_id, alvo, novo_alvo, o_que in relato_invoc:
            if o_que == 'trocado':
                print u'    %d: invoca %s -> passa a invocar %s' % (
                    mob_id, alvo, novo_alvo)
            else:
                print (u'    %d: invocava %s, sem contraparte ilusional - '
                       u'linha descartada' % (mob_id, alvo))
    print
    print u'  %d monstros, %d salas povoadas, %d portais.' % (
        len(relato), len(uteis), len(portais))
    print u'  %d monstros comuns no mapa (%d tipos x %d por sala x %d salas).' % (
        len(COMUNS) * POR_SALA * len(uteis), len(COMUNS), POR_SALA, len(uteis))
    print
    print u'Falta, se ainda nao estiver:'
    print u'  - Path: db/guerra/mob_db_labirinto.yml   no rodape de db/re/mob_db.yml'
    print u'  npc: npc/guerra/ilusao_do_labirinto_mapa.txt  no scripts_guerra.conf'
    print u'E reiniciar o map-server (ou @reloadmobdb + @reloadscript).'
    return 0


def conferir():
    texto_mob, corpo_skill, texto_npc, relato, uteis, portais, _inv = monta()
    problemas = []

    if not os.path.exists(SAIDA_MOB):
        problemas.append('%s nao existe' % os.path.relpath(SAIDA_MOB, RAIZ))
    elif le(SAIDA_MOB) != texto_mob.encode('cp1252'):
        problemas.append('%s esta diferente do que o gerador produz'
                         % os.path.relpath(SAIDA_MOB, RAIZ))

    if not os.path.exists(SAIDA_NPC):
        problemas.append('%s nao existe' % os.path.relpath(SAIDA_NPC, RAIZ))
    elif le(SAIDA_NPC) != texto_npc.encode('cp1252'):
        problemas.append('%s esta diferente do que o gerador produz'
                         % os.path.relpath(SAIDA_NPC, RAIZ))

    if not os.path.exists(SAIDA_SKILL):
        problemas.append('%s nao existe' % os.path.relpath(SAIDA_SKILL, RAIZ))
    else:
        atual = secao_de_arquivo.le(le(SAIDA_SKILL), SECAO)
        if atual is None:
            problemas.append('a secao %s nao esta em %s'
                             % (SECAO, os.path.relpath(SAIDA_SKILL, RAIZ)))
        elif atual != corpo_skill:
            problemas.append('a secao %s de %s esta diferente do que o gerador '
                             'produz' % (SECAO,
                                         os.path.relpath(SAIDA_SKILL, RAIZ)))

    rodape = le(MOB_DB_RA)
    if 'db/guerra/mob_db_labirinto.yml' not in rodape:
        problemas.append('falta o `- Path: db/guerra/mob_db_labirinto.yml` no '
                         'rodape de db/re/mob_db.yml')

    conf = le(os.path.join(RAIZ, 'rathena', 'npc', 'guerra',
                           'scripts_guerra.conf'))
    for arquivo in ('ilusao_do_labirinto_mapa.txt', 'ilusao_do_labirinto.txt'):
        if 'npc/guerra/%s' % arquivo not in conf:
            problemas.append('falta a linha `npc: npc/guerra/%s` no '
                             'scripts_guerra.conf' % arquivo)

    ignore = le(os.path.join(RAIZ, 'rathena', '.gitignore'))
    if '!/db/import/mob_skill_db.txt' not in ignore:
        problemas.append('falta o `!/db/import/mob_skill_db.txt` no '
                         'rathena/.gitignore - sem ele as habilidades nao '
                         'chegam a producao')

    if problemas:
        for p in problemas:
            print u'  FALTA: %s' % p
        return 1
    print u'  ok: os %d monstros, as %d salas e os %d portais estao em dia.' % (
        len(relato), len(uteis), len(portais))
    return 0


if __name__ == '__main__':
    if '--conferir' in sys.argv:
        sys.exit(conferir())
    sys.exit(gerar())
