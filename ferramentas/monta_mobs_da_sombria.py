# -*- coding: utf-8 -*-
u"""Gera os 14 monstros da Maldicao de Glast Heim Sombria.

    python monta_mobs_da_sombria.py             # gera db/guerra/mob_db_sombria.yml
                                                #   e db/import/mob_skill_db.txt
    python monta_mobs_da_sombria.py --conferir  # so relata; sai 1 se divergir

O PROBLEMA QUE ISTO RESOLVE

A Sombria e a versao dificil da Maldicao de Glast Heim, e os monstros dela
NAO EXISTEM em versao nenhuma do rAthena. No `db/re/mob_db.yml` do nosso
vendor - e tambem no master do rAthena de 2026-08-28, conferido - os
catorze estao la como PLACEHOLDER: duas linhas comentadas cada um, com o
`Id` e o `AegisName` e mais nada.

    #  - Id: 3139
    #    AegisName: MG_ZOMBIE_H

Nao ha status, nao ha drop, nao ha habilidade. Descomentar nao adianta: nao
ha o que descomentar.

O QUE O CLIENTE JA TEM, E POR ISSO ISTO E BARATO

Este kRO de 2021-11-03 conhece os catorze: os ids 3139..3152 estao no
`npcidentity.lub` casando exatamente com os AegisName acima, e o
`jobname.lub` da o sprite de cada um. Doze reusam arte que ja existe
(`zombie`, `ghoul`, `khalitzburg`...) e os DOIS MVPs tem arte propria -
`mg_amdarais_h.spr` e `mg_corruption_root_h.spr`, os dois presentes no
`data.grf`. Ou seja: nada disto precisa de patch de cliente.

A REGRA DE DERIVACAO, E POR QUE ELA NAO E INVENCAO

Cada `_H` e o monstro normal da Maldicao com tres campos mexidos:

    Level    +30
    Hp       x2   (x10 nos dois MVPs, 3150 e 3151)
    BaseExp  x2
    JobExp   x2

e TODO o resto identico - Str/Agi/Vit/Int/Dex/Luk, Defense, MagicDefense,
AttackRange, Size, Race, Element, ElementLevel, velocidades, Ai, Class e a
tabela de drops.

Isto nao foi deduzido: foi CONFERIDO campo a campo contra o divine-pride,
nos treze pares, em 2026-08-28. Os seis atributos batem em todos; o HP bate
nos treze (135.600 -> 271.200, 208.100 -> 416.200, ... e 4.290.000 ->
42.900.000 no Amdarais); o EXP bate nos treze; DEF/MDEF batem em todos.

O `Attack`/`Attack2` NAO mudam, e isso tambem foi medido: o divine-pride
mostra a faixa ja CALCULADA (statusAtk etc.), nao o campo. A razao entre a
faixa do `_H` e o `Attack2` do normal deu 1,50 nos dois casos magicos que
dao para isolar - 4804/3200 no Sanguinario e 4179/2787 na Alma -, ou seja o
campo e o mesmo e o que sobe e o nivel.

O ELEMENTO vem do normal, nao do divine-pride: la a linha "Element" e a
tabela de RESISTENCIA, e ela mostra "Neutral (100%)" para bicho de elemento
Morto-vivo. As duas leituras concordam onde da para separar (Cavaleiro
Sombrio "Dark 4" = o `Element: Dark/4` do 2470; Arclouse "Earth 2" = o do
2467), e a linha de resistencia "Dark 0% | Undead 0%" do 3146 confirma
elemento Morto-vivo no Khalitzburg. Ler a coluna errada poria metade dos
catorze em Neutro.

ONDE MORAM AS HABILIDADES, E POR QUE NAO E EM db/guerra/

O `mob_skill_db.txt` nao tem rodape `Footer: Imports:` - nao e YAML. O
`mob_readskilldb` (src/map/mob.cpp linha 7184) le de DOIS lugares e so
dois: `db/re/` e `db/import/`. Como `db/re/mob_skill_db.txt` e arquivo de
terceiro e a secao 2 do CLAUDE.md proibe enxertar dado nele, o nosso vai em
`db/import/mob_skill_db.txt` - que o `.gitignore` do vendor ignora e que
por isso ganhou uma excecao, `!/db/import/mob_skill_db.txt`, do mesmo jeito
que o `!/src/custom/` que ja estava la. Sem a excecao o arquivo nao chega a
producao e os catorze ficam sem habilidade nenhuma, calados.

As linhas sao as do monstro normal com o id trocado. Onze dos treze tem
habilidade; o Khalitzburg (2471) e os dois Comandantes (2473, 2474) nao tem
nenhuma no vendor, entao os `_H` deles tambem nao ganham.

O DECIMO QUARTO

O 3152 (`G_MG_KHALITZBURG_H`) e o Khalitzburg invocado. O normal dele
(`G_MG_KHALITZBURG`, 2482) tambem esta comentado no vendor, entao ele sai
do 2471 com `Ai: 21` - o de escravo -, que e o que o rAthena usa nos outros
`G_`.

DEPOIS DE RODAR

Reiniciar o map-server ou `@reloadmobdb`. E ligar o arquivo, se ainda nao
estiver: uma linha `- Path: db/guerra/mob_db_sombria.yml` no rodape de
`db/re/mob_db.yml`, que passa a ter TRES.
"""

import codecs
import os
import re
import sys

# Sem isto, imprimir "Carnical Sombrio" com cedilha derruba a ferramenta
# DEPOIS de ela ja ter gravado os arquivos - CLAUDE.md secao 5. E o `or`
# nao e enfeite: com a saida redirecionada, `sys.stdout.encoding` e None.
sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout,
                                                               'replace')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOB_DB_RA = os.path.join(RAIZ, 'rathena', 'db', 're', 'mob_db.yml')
SKILL_RA = os.path.join(RAIZ, 'rathena', 'db', 're', 'mob_skill_db.txt')
SAIDA_MOB = os.path.join(RAIZ, 'rathena', 'db', 'guerra', 'mob_db_sombria.yml')
SAIDA_SKILL = os.path.join(RAIZ, 'rathena', 'db', 'import', 'mob_skill_db.txt')

# normal -> (id_H, AegisName_H, Name_H em ingles, nome PT do bRO)
#
# O nome PT saiu da pagina Glast_Heim_Sombria do arquivo.browiki.org - e a
# fonte do bRO, como manda a regra 3 do CLAUDE.md. O `Name` fica em ingles
# de proposito: e por ele que @monster e os scripts do rAthena procuram o
# bicho, e o teto e 24 caracteres (NAME_LENGTH).
PARES = [
    (2464, 3139, 'MG_ZOMBIE_H',            'Ominous Steward',        u'Zumbi Sombrio'),
    (2465, 3140, 'MG_WRAITH_H',            'Ominous Monk',           u'Alma Sombria'),
    (2466, 3141, 'MG_GHOUL_H',             'Ominous Chamberlain',    u'Carniçal Sombrio'),
    (2467, 3142, 'MG_ARCLOUSE_H',          'Ominous Maggot',         u'Arclouse Sombrio'),
    (2468, 3143, 'MG_RAYDRIC_H',           'Ominous Palace Guard',   u'Raydric Sombrio'),
    (2469, 3144, 'MG_RAYDRIC_ARCHER_H',    'Ominous Archer',         u'Arqueiro Sombrio'),
    (2470, 3145, 'MG_KNIGHT_OF_ABYSS_H',   'Ominous Abysmal Knight', u'Cavaleiro Sombrio'),
    (2471, 3146, 'MG_KHALITZBURG_H',       'Ominous Khalitzburg',    u'Khalitzburg Sombria'),
    (2472, 3147, 'MG_BLOODY_KNIGHT_H',     'Ominous Bloody Knight',  u'Sanguinário Sombrio'),
    (2473, 3148, 'MG_M_UNDEAD_KNIGHT_H',   'Ominous 1st Commander',  u'Desmorto Sombrio'),
    (2474, 3149, 'MG_F_UNDEAD_KNIGHT_H',   'Ominous 2nd Commander',  u'Desmorta Sombria'),
    (2475, 3151, 'MG_CORRUPTION_ROOT_H',   'Ominous Corrupted Soul', u'Origem da Escuridão'),
    (2476, 3150, 'MG_AMDARAIS_H',          'Ominous Amdarais',       u'Amdarais Sombrio'),
]

# O invocado sai do Khalitzburg com Ai de escravo.
ESCRAVO = (2471, 3152, 'G_MG_KHALITZBURG_H', 'Ominous Khalitzburg', u'Khalitzburg Sombria')

# A tabela de drops vem inteira do monstro normal, com UMA excecao: os dois
# MVPs tem carta propria, e ela ja existe no item_db do vendor. Copiar a
# carta do normal faria a Sombria - que custa dez vezes mais HP - entregar
# exatamente o mesmo premio da facil, e deixaria as duas cartas `_H` sem
# fonte nenhuma no servidor. Elas sao itens diferentes, com efeito melhor:
# a 4602 da +20% de dano em toda classe e +20% de MATK contra os +10/+10 da
# 4601.
CARTAS = {
    'Amdarais_Card': 'AmdaraisH_Card',                # 4601 -> 4602
    'CorruptionRoot_Card': 'CorruptionRootH_Card',    # 4603 -> 4604
}

MVPS = (3150, 3151)          # os unicos com HP x10
DELTA_NIVEL = 30
FATOR_HP_COMUM = 2
FATOR_HP_MVP = 10
FATOR_EXP = 2

CABECA = u"""\
###########################################################################
# Guerra do Emperium - os monstros da Maldicao de Glast Heim Sombria
###########################################################################
#
# GERADO por ferramentas/monta_mobs_da_sombria.py. Editar a mao morre na
# proxima rodada - o arquivo e reescrito inteiro. O porque de cada numero,
# e a medicao que o sustenta, estao no cabecalho daquela ferramenta.
#
# Sao os ids 3139..3152, que o vendor traz COMENTADOS (so Id e AegisName) e
# que o rAthena nunca implementou - nem no master. Cada um e o monstro
# correspondente da Maldicao normal com Level +%(nivel)d, HP x%(hp)d
# (x%(hpmvp)d nos dois MVPs) e EXP x%(exp)d; todo o resto e identico, e isso
# foi conferido campo a campo contra o divine-pride em 2026-08-28.
#
# O nome que o jogador le e o `JapaneseName` (o `memcpy(md->name,
# md->db->jname)` do mob.cpp); o `Name` fica em ingles porque e a chave de
# @monster e dos scripts.
#
# Alcancado por uma linha `- Path: db/guerra/mob_db_sombria.yml` no rodape
# de db/re/mob_db.yml, que passa a ter tres.
#
# Encoding: cp1252, como todo texto que o jogo le (CLAUDE.md secao 4.1).
#
###########################################################################

Header:
  Type: MOB_DB
  Version: 5

Body:
"""


def le(caminho):
    aberto = open(caminho, 'rb')
    try:
        return aberto.read()
    finally:
        aberto.close()


def bloco_do_mob(texto, mob_id):
    u"""Devolve as linhas do registro `- Id: <mob_id>` do mob_db, sem o `- Id:`."""
    marca = '  - Id: %d\n' % mob_id
    ini = texto.find(marca)
    if ini < 0:
        marca = '  - Id: %d\r\n' % mob_id
        ini = texto.find(marca)
    if ini < 0:
        raise SystemExit('nao achei o registro do mob %d em %s' % (mob_id, MOB_DB_RA))
    corpo = ini + len(marca)
    # o proximo registro NAO comentado
    fim = re.search(r'^  - Id: \d+\s*$', texto[corpo:], re.M)
    if not fim:
        raise SystemExit('nao achei o fim do registro do mob %d' % mob_id)
    return texto[corpo:corpo + fim.start()]


def converte(bloco, novo_id, aegis, nome, nome_pt, escravo=False):
    u"""Aplica a derivacao ao bloco do monstro normal."""
    saida = [u'  - Id: %d\n' % novo_id]
    fator_hp = FATOR_HP_MVP if novo_id in MVPS else FATOR_HP_COMUM
    posto_japones = False

    for linha in bloco.decode('cp1252').split(u'\n'):
        crua = linha.rstrip(u'\r')
        if not crua.strip():
            continue

        m = re.match(r'^    (\w+): (.*)$', crua)
        chave = m.group(1) if m else None
        valor = m.group(2) if m else None

        if chave == 'AegisName':
            saida.append(u'    AegisName: %s\n' % aegis)
            continue
        if chave == 'Name':
            saida.append(u'    Name: %s\n' % nome)
            # o JapaneseName vem logo depois, que e onde o rAthena o espera
            saida.append(u'    JapaneseName: "%s"\n' % nome_pt)
            posto_japones = True
            continue
        if chave == 'Level':
            saida.append(u'    Level: %d\n' % (int(valor) + DELTA_NIVEL))
            continue
        if chave == 'Hp':
            saida.append(u'    Hp: %d\n' % (int(valor) * fator_hp))
            continue
        if chave in ('BaseExp', 'JobExp'):
            saida.append(u'    %s: %d\n' % (chave, int(valor) * FATOR_EXP))
            continue
        if chave == 'Ai' and escravo:
            saida.append(u'    Ai: 21\n')
            continue
        # linha comentada do vendor (ex.: "#   MvpExp:") nao vale a pena levar
        if crua.lstrip().startswith(u'#'):
            continue
        if chave is None:
            m2 = re.match(r'^(\s+- Item: )(\w+)$', crua)
            if m2 and m2.group(2) in CARTAS:
                saida.append(u'%s%s\n' % (m2.group(1), CARTAS[m2.group(2)]))
                continue
        saida.append(crua + u'\n')

    if not posto_japones:
        raise SystemExit('o registro de %s nao tinha campo Name' % aegis)

    if escravo:
        # invocado nao entrega drop nem carta - senao o Khalitzburg vira
        # fonte infinita das duas armas que o 2471 derruba.
        texto = u''.join(saida)
        texto = re.sub(r'    Drops:\n(      .*\n)+', u'', texto)
        texto = re.sub(r'    MvpDrops:\n(      .*\n)+', u'', texto)
        return texto
    return u''.join(saida)


def linhas_de_habilidade(texto, velho, novo, nome):
    u"""As linhas do mob_skill_db do monstro normal, com o id novo."""
    fora = []
    for linha in texto.split('\n'):
        crua = linha.rstrip('\r')
        if not crua.startswith('%d,' % velho):
            continue
        campos = crua.split(',')
        campos[0] = str(novo)
        # coluna 1 e o "Dummy value (info only)" - so serve para ler
        if len(campos) > 1 and '@' in campos[1]:
            campos[1] = nome + '@' + campos[1].split('@', 1)[1]
        fora.append(','.join(campos))
    return fora


def monta():
    mob_texto = le(MOB_DB_RA)
    skill_texto = le(SKILL_RA)

    partes = [CABECA % {'nivel': DELTA_NIVEL, 'hp': FATOR_HP_COMUM,
                        'hpmvp': FATOR_HP_MVP, 'exp': FATOR_EXP}]
    skills = []
    relato = []

    for velho, novo, aegis, nome, nome_pt in PARES + [ESCRAVO]:
        eh_escravo = (novo == ESCRAVO[1])
        bloco = bloco_do_mob(mob_texto, velho)
        partes.append(converte(bloco, novo, aegis, nome, nome_pt, eh_escravo))
        linhas = [] if eh_escravo else linhas_de_habilidade(
            skill_texto, velho, novo, nome)
        skills.extend(linhas)
        relato.append((novo, aegis, nome_pt, len(linhas)))

    return u''.join(partes), skills, relato


CABECA_SKILL = """\
//===========================================================================
// Guerra do Emperium - habilidades dos monstros da Glast Heim Sombria
//===========================================================================
//
// GERADO por ferramentas/monta_mobs_da_sombria.py. Editar a mao morre na
// proxima rodada.
//
// POR QUE ESTE ARQUIVO MORA AQUI, E NAO EM db/guerra/
//
// O mob_skill_db.txt nao e YAML - nao tem rodape `Footer: Imports:`. O
// mob_readskilldb (src/map/mob.cpp linha 7184) le de dois lugares e so
// dois: db/re/ e db/import/. Como db/re/mob_skill_db.txt e arquivo de
// terceiro, e a secao 2 do CLAUDE.md proibe enxertar dado nele, o nosso vem
// para ca.
//
// E POR ISSO O .gitignore DO VENDOR GANHOU UMA EXCECAO
//
// O rathena/.gitignore ignora /db/import inteiro. Sem um
// `!/db/import/mob_skill_db.txt` este arquivo NAO chega a producao, e os
// catorze monstros ficam sem habilidade nenhuma - calados, porque monstro
// sem linha aqui simplesmente nao conjura. E a mesma excecao que o
// `!/src/custom/` ja fazia.
//
// As linhas sao as do monstro NORMAL correspondente com o id trocado. O
// Khalitzburg (2471) e os dois Comandantes (2473, 2474) nao tem habilidade
// no vendor, entao os _H deles tambem nao tem.
//
// MobID,Dummy value (info only),State,SkillID,SkillLv,Rate,CastTime,Delay,Cancelable,Target,Condition type,Condition value,val1,val2,val3,val4,val5,Emotion,Chat
//===========================================================================

"""


def gerar():
    texto, skills, relato = monta()

    aberto = open(SAIDA_MOB, 'wb')
    try:
        aberto.write(texto.encode('cp1252'))
    finally:
        aberto.close()

    aberto = open(SAIDA_SKILL, 'wb')
    try:
        aberto.write(CABECA_SKILL + '\n'.join(skills) + '\n')
    finally:
        aberto.close()

    print u'Gerado %s' % os.path.relpath(SAIDA_MOB, RAIZ)
    print u'Gerado %s' % os.path.relpath(SAIDA_SKILL, RAIZ)
    print
    print u'  %-6s %-24s %-22s %s' % ('Id', 'AegisName', 'Nome PT', 'habilidades')
    for novo, aegis, nome_pt, n in relato:
        print u'  %-6d %-24s %-22s %d' % (novo, aegis, nome_pt, n)
    print
    print u'  %d monstros, %d linhas de habilidade.' % (len(relato), len(skills))
    print
    print u'Falta, se ainda nao estiver:'
    print u'  - Path: db/guerra/mob_db_sombria.yml   no rodape de db/re/mob_db.yml'
    print u'  !/db/import/mob_skill_db.txt           no rathena/.gitignore'
    print u'E reiniciar o map-server (ou @reloadmobdb).'
    return 0


def conferir():
    texto, skills, _ = monta()
    problemas = []

    if not os.path.exists(SAIDA_MOB):
        problemas.append('%s nao existe' % os.path.relpath(SAIDA_MOB, RAIZ))
    elif le(SAIDA_MOB) != texto.encode('cp1252'):
        problemas.append('%s esta diferente do que o gerador produz'
                         % os.path.relpath(SAIDA_MOB, RAIZ))

    esperado = CABECA_SKILL + '\n'.join(skills) + '\n'
    if not os.path.exists(SAIDA_SKILL):
        problemas.append('%s nao existe' % os.path.relpath(SAIDA_SKILL, RAIZ))
    elif le(SAIDA_SKILL) != esperado:
        problemas.append('%s esta diferente do que o gerador produz'
                         % os.path.relpath(SAIDA_SKILL, RAIZ))

    rodape = le(os.path.join(RAIZ, 'rathena', 'db', 're', 'mob_db.yml'))
    if 'db/guerra/mob_db_sombria.yml' not in rodape:
        problemas.append('falta o `- Path: db/guerra/mob_db_sombria.yml` no '
                         'rodape de db/re/mob_db.yml')

    ignore = le(os.path.join(RAIZ, 'rathena', '.gitignore'))
    if '!/db/import/mob_skill_db.txt' not in ignore:
        problemas.append('falta o `!/db/import/mob_skill_db.txt` no '
                         'rathena/.gitignore - sem ele as habilidades nao '
                         'chegam a producao')

    if problemas:
        for p in problemas:
            print u'  FALTA: %s' % p
        return 1
    print u'  ok: os %d monstros e as %d linhas de habilidade estao em dia.' % (
        len(PARES) + 1, len(skills))
    return 0


if __name__ == '__main__':
    if '--conferir' in sys.argv:
        sys.exit(conferir())
    sys.exit(gerar())
