# -*- coding: utf-8 -*-
u"""Poe a entrada de um item NOSSO no `itemInfo.lua` do cliente.

    python instala_item.py              # aplica (faz backup antes)
    python instala_item.py --verificar  # so relata, nao grava
    python instala_item.py <itemInfo.lua> [--verificar]

O `itemInfo.lua` e a tabela que da nome, descricao e arte a cada item do lado do
cliente. Sem entrada la, um item novo do servidor aparece sem nome e o cliente
reclama. Ele NAO e alcancado por `@reloaditemdb`: e lido uma vez, na
inicializacao, entao toda mudanca exige fechar e reabrir o cliente.

Por que isto e um script e nao uma edicao a mao: o arquivo tem 22 MB, esta em
ANSI, e os `resourceName` sao bytes CP949 coreanos. Editor ou ferramenta que
assuma UTF-8 reescreve esses bytes e corrompe as ~26 mil entradas de uma vez,
sem dar erro nenhum - o estrago so aparece no jogo, e depois de fechado nao da
para saber o que era. Aqui e tudo `rb`/`wb`, byte a byte, sem decodificar nada.

E tambem por isso o `cliente\\` estar fora do git nao e problema: o gerador fica
versionado, a saida nao. Rodar este script reconstroi a alteracao num cliente
novo.

Idempotente: se a entrada ja existe identica, nao faz nada; se existe diferente,
substitui o bloco inteiro. Rodar duas vezes nunca duplica.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import re
import shutil
import sys
import time

ITEMINFO = os.path.join(r'C:\GuerraDoEmperium\cliente',
                        'SystemEN', 'LuaFiles514', 'itemInfo.lua')

# --------------------------------------------------------------- a receita
#
# Um dicionario por item. Acrescentar item e editar esta tabela, nao o codigo.
#
#   id        o mesmo ID do db/guerra/item_db.yml. Os dois lados TEM que bater:
#             o servidor manda o numero, o cliente procura por ele aqui.
#   nome      o que aparece no inventario. Literal `u'...'`, COM acento: o
#             texto e gravado em cp1252, a mesma codificacao em que o bRO
#             entrega os dele e a que o cliente desenha por causa do patch
#             AlwaysAscii. Ver PENDENCIAS.md, secao "Acentuacao no dialogo".
#   descricao um PARAGRAFO por elemento, nao uma linha de tela. O cliente
#             dobra o texto sozinho na largura da caixa, entao nao ha por que
#             quebrar a mao: quebrar so onde a quebra significa alguma coisa
#             (um item de lista, uma regua, a ficha de Tipo/Peso no fim).
#             Medido em 2026-08-07 contra o `iteminfo_new.lub` do bRO, que
#             entrega a descricao do Emperium (714) numa unica string de 349
#             caracteres e a do Bat-Katar (1298) em 444 - e o bRO esta no ar.
#             O monte de linhas de exatos 60 caracteres do itemInfo.lua e
#             convencao manual velha do kRO, nao um teto do cliente.
#             "____..." e a regua separadora que o proprio arquivo usa, e
#             `^RRGGBB` troca a cor.
#   covas     quantas covas de carta o item tem. OPCIONAL, zero se faltar.
#             E o que poe o "[1]" no fim do nome e o que faz a janela
#             de encaixe de carta enxergar a cova. TEM que bater com o
#             `Slots:` do item_db - o servidor manda o numero, o
#             cliente desenha o que estiver escrito aqui, e divergir
#             nao da erro nenhum.
#   visual    o id de visual (o `View:` do item_db). OPCIONAL, zero se
#             faltar. So peca de cabeca e de manto usa; para o resto
#             zero e o valor certo.
#   arte_de   ID de outro item de quem copiamos o `resourceName`, BYTE A BYTE.
#             O `resourceName` e so um nome de recurso: nada impede dois IDs
#             apontarem para o mesmo desenho, e assim nao precisamos criar
#             icone, imagem de collection nem sprite de chao. Quando um item
#             nosso for merecer arte exclusiva, ai entra o instala_visual.py.
#             Copiar em tempo de execucao, e nao colar os bytes aqui, e o que
#             garante que eles cheguem intactos.
#   recurso   o `resourceName` POR EXTENSO, no lugar de `arte_de`. So ASCII -
#             nome coreano continua sendo caso de `arte_de`. Existe para o caso
#             "traduzir entrada alheia SEM mexer na arte": ali `arte_de`
#             apontando para o proprio item parece a resposta obvia e e uma
#             armadilha, porque o script se le a si mesmo e uma rodada ruim
#             vira a fonte da rodada seguinte. Ver a nota do 19272.

ITENS = [
    {
        'id': 30999,
        'nome': u'Maçã da Inocência',
        'arte_de': 512,                     # a Maca comum
        'descricao': [
            u'Ao adentrar em Valhalla caída o viajante recebe uma maçã',
            u'que simboliza a inocência na renovação.',
            u'Optar por atalhos pode fazer com que a maçã desapareça.',
            u'_______________________',
            u'Pode ser concedida ao Deus da Guerra no level máximo em',
            u'troca de melhorias.',
            u'_______________________',
            u'^0000CCTipo:^000000 Etc',
            u'^0000CCPeso:^000000 1',
        ],
    },
    {
        'id': 30998,
        'nome': u'Moeda Nova',
        'arte_de': 6080,                    # a Moeda Manuk
        # Uma linha por UNIDADE DE SENTIDO, e nao por largura: o paragrafo
        # inteiro cabe numa string so. Quem dobra o texto na caixa e o
        # cliente - medido em 2026-08-07 contra o iteminfo_new.lub do bRO,
        # que entrega a descricao do Emperium (714) numa unica linha de 349
        # caracteres e a do Bat-Katar (1298) em 444. Ver o LEIAME.md.
        'descricao': [
            u'A moeda do reino anterior estava corrompida, e por isso criar uma nova moeda foi a primeira coisa que a Ordem fez quando vieram salvar Rune Midgard.',
            u'_______________________',
            u'- Todo cidadão ganha 10 moedas por dia pelo Logue e Ganhe.',
            u'- As moedas também podem ser obtidas em troca de Flores Visionárias (MVP);',
            u'- As moedas também podem ser obtidas em troca de Moedas do Explorador;',
            u'- As moedas também podem ser obtidas em troca de Caveira Humana;',
            u'_______________________',
            u'Novos serviços aceitam a moeda.',
            u'^FF0000Não tente vender em NPCs comuns!^000000',
            u'_______________________',
            u'^0000CCTipo:^000000 Etc',
            u'^0000CCPeso:^000000 0',
        ],
    },
    # As duas caixas da Maquina, 2026-08-07. Elas nao sao item de jogo novo:
    # sao EMBALAGEM. A loja de troca (npc/guerra/barters_guerra.yml) cobra por
    # unidade, entao "5 por 1 Moeda" so existe se as 5 forem um item so.
    # Dezesseis das dezoito linhas daquela loja usam caixa que o bRO ja tinha
    # pronta; estas duas sao as que faltavam. Ver db/guerra/item_db.yml.
    #
    # O texto segue a VOZ DAS CAIXAS DO bRO, e nao a das duas entradas acima:
    # primeira linha "Uma caixa contendo N ...", depois o efeito do conteudo.
    # Foi lido do iteminfo_new.lub (13610, 16395, 16262) para nao inventar
    # forma nova para um item que o jogador vai ver ao lado de quinze irmaos.
    {
        'id': 30997,
        'nome': u'Cx. Bênção do Ferreiro (5)',
        # A caixa de 3 do bRO. Copiar a arte dela e nao a MECANICA e
        # deliberado: aquela entrega por `getgroupitem`, e sorteio aqui nao
        # faz sentido nenhum.
        'arte_de': 101047,
        'descricao': [
            u'Uma caixa contendo 5 Bênçãos do Ferreiro.',
            u'^000088Garrafa mágica que só pode ser usada junto com outros minérios na hora de refinar. Em casos de falha, você não perderá o equipamento e o refino atual, mas esse item será consumido independente do resultado.^000000',
            u'_______________________',
            u'A janela de refino exige a Bênção para passar de +7, e a quantidade cresce rápido: +8 pede 1, +9 pede 2, e daí 4, 7, 11, 16 e 22.',
            u'_______________________',
            u'^0000CCTipo:^000000 Caixa',
            u'^0000CCPeso:^000000 0',
        ],
    },
    {
        'id': 30996,
        'nome': u'Cx. Poção de Guyak (30)',
        # A PROPRIA Poção de Guyak (12710), desde 2026-08-12, a pedido: a
        # caixa passa a ter a cara do que tem dentro.
        #
        # Ate entao era a arte da caixa de 20 do bRO (Guyak_Pudding_20_Box,
        # 22668) - aquele ITEM foi reprovado por trazer 20 e por ter nome
        # COREANO no itemInfo.lua, e so a arte tinha sido aproveitada. O
        # desenho dela e a caixa generica de consumivel, igual a de meia
        # duzia de irmas da mesma loja, e por isso nao dizia nada.
        #
        # As duas fontes tem "4 de 4 ok" no estado_item.py; a troca e de
        # gosto, nao de disponibilidade.
        'arte_de': 12710,
        'descricao': [
            u'Uma caixa contendo 30 Poções de Guyak.',
            u'^000088Duplica a velocidade de movimento por 5 minutos.^000000',
            u'_______________________',
            u'A produção desse consumível se tornou muito mais eficiente desde que decidiram fazer poções com Guyak, em vez de pudins. O efeito ainda é o mesmo!',
            u'_______________________',
            u'^0000CCTipo:^000000 Caixa',
            u'^0000CCPeso:^000000 0',
        ],
    },
    # O trofeu da arena, 2026-08-08. Ele nao tem fonte ainda: nada no servidor
    # o entrega, e a segunda linha da descricao promete um caminho que sera
    # escrito depois. Ver db/guerra/item_db.yml, entrada 30995, e PENDENCIAS.md.
    {
        'id': 30995,
        'nome': u'Caveira Humana',
        # A Caveira comum (Skull_), que tem os 4 arquivos completos neste
        # cliente - `estado_item.py --id 7420` da "4 de 4 ok". Copiar o
        # resourceName dela poupa criar arte para um item que e, no desenho,
        # exatamente a mesma caveira.
        'arte_de': 7420,
        'descricao': [
            u'Caveira humana de um jogador morto em combate.',
            u'_______________________',
            u'Essa caveira só cai de jogadores no level máximo com reputação positiva dentro da Arena de Prontera.',
            u'_______________________',
            u'^0000CCTipo:^000000 Etc',
            u'^0000CCPeso:^000000 0',
        ],
    },
    # O premio de guerra, 2026-08-13. Como a Caveira acima, ele ainda nao tem
    # fonte: nada no servidor o entrega. Ver db/guerra/item_db.yml, entrada
    # 30994, para o porque de cada numero - e para o porque do NOME, que era
    # para ser "Bolinho de Arroz" e nao pode: 555, 564 e 7613 ja se chamam
    # assim neste itemInfo.lua.
    {
        'id': 30994,
        'nome': u'Rolinho de Arroz',
        # O 555 (Rice_Cake), que o cliente chama de "Bolinho de Arroz" e tem
        # "4 de 4 ok" no estado_item.py. A MECANICA vem do 14524, o
        # consumivel de guerra do bRO; so o desenho vem daqui, porque era o
        # bolinho de arroz que o pedido tinha em mente.
        'arte_de': 555,
        'descricao': [
            u'Bolinho de arroz prensado que os cozinheiros da Ordem preparam na véspera da Guerra do Emperium. Só chega às mãos de quem ainda estava de pé no fim dela.',
            u'_______________________',
            u'^000088Recupera 100% do HP e do SP.^000000',
            u'^000088Não tem tempo de recarga.^000000',
            u'_______________________',
            u'^FF0000Prêmio de guerra: não pode ser negociado, vendido nem largado no chão.^000000',
            u'_______________________',
            u'^0000CCTipo:^000000 Consumível',
            u'^0000CCPeso:^000000 1',
        ],
    },
    # O CHAPEU DO EDEN (19272), 2026-08-18. Nao e item nosso: o rAthena o tem
    # inteiro (Garden_Of_Eden, View 1653, Head_Top, 1 cova). O que faltava era
    # o NOME - o itemInfo.lua deste cliente traz o 19272 com o nome COREANO, e
    # item sem nome em portugues nao entra em loja (regra 4.2).
    #
    # POR QUE NAO FOI PELO completa_iteminfo.py: o bRO tambem tem o 19272 em
    # coreano. Quem tem o nome em portugues la e o 19315, que e o MESMO item
    # com outro numero - mesmo `identifiedResourceName` (Garden_Of_Eden),
    # mesmo ClassNum 1653, mesma cova, e a mesma ficha (DEF 5, peso 40,
    # nivel 90/100). O texto abaixo e o do 19315, palavra por palavra.
    #
    # POR QUE NAO SE CRIOU O 19315 AQUI, que foi a receita da Lacma (13049 ->
    # 28739, ver o cabecalho de mercado_contemporaneo.txt): o 19272 e citado
    # por TRES conjuntos do db/re/item_combos.yml, e dois dos parceiros ja
    # estao a venda no quarteirao - a Fada do Eden (20991) no Capeiro e o
    # Simbolo do Eden (460050) no Escudeiro. Conjunto e casado por AegisName,
    # entao trocar o ID derrubaria os tres, calado. Aqui sai mais barato
    # traduzir a entrada do que renumerar o item.
    #
    # RESSALVA REGISTRADA: a descricao do bRO promete "Dano magico de todas as
    # propriedades +15%" e o `Script:` do nosso vendor da `bMagicAtkEle,10`.
    # E a armadilha de sempre (CLAUDE.md 5, "a descricao discorda do script")
    # - o vendor e de outra revisao. Nao mexi no numero: mudar bonus e decisao
    # do dono, nao consequencia de por o item na vitrine.
    {
        'id': 19272,
        'nome': u'Chapéu do Éden',
        # A PROPRIA ARTE, escrita por extenso e nao por `arte_de: 19272`. Era
        # `arte_de` ate 2026-08-20, e isso somado ao bug do `(?<!un)` (ver
        # `recurso`) deixou o chapeu com o gorro generico de item nao
        # identificado no icone, na collection e no sprite de chao, de
        # 2026-08-18 a 2026-08-20. Auto-referencia nao se recupera sozinha: o
        # valor errado vira a fonte da rodada seguinte.
        'recurso': u'Garden_Of_Eden',   # o mesmo do 19315 do bRO
        # Os dois campos que a entrada coreana ja trazia, e que sao a
        # razao de `covas`/`visual` existirem: sem eles o nome sairia
        # sem o "[1]" e a peca perderia o id de visual. Batem com o
        # `Slots: 1` e o `View: 1653` do 19272 em db/re/item_db_equip.yml.
        'covas': 1,
        'visual': 1653,
        'descricao': [
            u'Este extravagante chapéu adorna sua cabeça com um pedaço do Paraíso. Encantado com a dádiva dos mais altos anjos, este chapéu é um verdadeiro presente do paraíso.',
            u'^0000ffINT +5. DES +5.^000000',
            u'^0000ffDano mágico de todas as propriedades +15%.^000000',
            u'Refino +8 ou mais:',
            u'^0000ffConjuração variável -15%.^000000',
            u'Refino +11 ou mais:',
            u'^0000ffDano mágico de todas as propriedades +20% adicional.^000000',
            u'^FA4E09Conjunto^000000',
            u'^FA4E09[Carta Arquimaga Kathryne]^000000',
            u'^0000ffTempo de recarga de [Telecinesia] -120 segundos.^000000',
            u'^0000ffDesequipar o item remove a [Telecinesia] ativada.^000000',
            u'Tipo: ^777777Equip. para Cabeça^000000',
            u'Equipa em: ^777777Topo^000000',
            u'DEF: ^7777775^000000 DEFM: ^7777770^000000',
            u'Peso: ^77777740^000000',
            u'Nível necessário: ^77777790^000000',
            u'Classes: ^777777Todas^000000',
        ],
    },
    # A NONA ENTRADA, 2026-08-20: a Ferramenta Magica de Gelo (490029). E o
    # segundo caso do tipo "Chapeu do Eden" - item que existe inteiro no nosso
    # vendor e cuja entrada de cliente esta na LINGUA ERRADA. Aqui a lingua e
    # o INGLES (a entrada veio do ROenglishRE, `Server = "jRO"`), e o pedido do
    # dono em 2026-08-20 foi explicito: "vamos traduzir para Ferramenta Magica
    # de Gelo".
    #
    # POR QUE NAO FOI PELO completa_iteminfo.py: o bRO NAO TEM este ID. Nem
    # este, nem nenhum outro item da familia Magictool - varridos os 18845 do
    # `iteminfo_new.lub` em 2026-08-20, por nome e por `identifiedResourceName`,
    # e o resultado foi zero. Nao ha de onde copiar; o texto abaixo foi
    # traduzido a mao.
    #
    # E ELE CONTINUA SEM ARTE, e isso NAO se resolve aqui. O
    # `identifiedResourceName` e `Geffenia_Magictool_Ice`, e os quatro arquivos
    # dele nao existem nem no nosso data.grf nem no do bRO (conferido nos dois
    # em 2026-08-20). Por isso ele NAO ENTROU em loja nenhuma - item sem arte
    # entrega caixa de erro ao jogador (CLAUDE.md 4.4). O `arte_de` aponta para
    # ele mesmo, ou seja preserva o recurso que ja estava la: trocar por um
    # doador seria dar a ele o desenho de outro item, e isso e decisao do dono.
    # Ver a ressalva no cabecalho de npc/guerra/mercado_contemporaneo.txt.
    #
    # O TEXTO SEGUE O `Script:` DO VENDOR, e nao a descricao em ingles que
    # estava no arquivo - as duas discordavam num ponto que a regra manda
    # conferir (CLAUDE.md 5, "a descricao discorda do script"): a linha da
    # Maestria Arcana (`bonus bDelayrate,-30`) simplesmente NAO ESTAVA na
    # descricao inglesa. Foi acrescentada.
    #
    # OS SEIS NOMES DE HABILIDADE saem do `skillinfolist.lub` DESTE cliente,
    # que e a tabela que o jogo le (regra 4.12): WZ_STORMGUST = "Nevasca",
    # WL_COMET = "Cometa", WL_JACKFROST = "Esquife de Gelo", WL_FROSTMISTY =
    # "Zero Absoluto", WL_STASIS = "Distorcao Arcana" e WL_RECOGNIZEDSPELL =
    # "Maestria Arcana". Nenhum e traducao livre.
    #
    # E O SINAL DO `bSkillUseSP` FOI CONFERIDO, porque o nome do bonus sugere o
    # contrario do que ele faz: `bonus2 bSkillUseSP,sk,n` DIMINUI o consumo em
    # n (doc/item_bonus.txt:195). Entao o `,35` e o `,100` do script sao -35 e
    # -100 na tela, e nao +35 e +100.
    {
        'id': 490029,
        'nome': u'Ferramenta Mágica de Gelo',
        # O recurso que a entrada em ingles ja trazia, preservado por extenso.
        # NAO se usa `arte_de: 490029` aqui - ver a nota do 19272 acima.
        'recurso': u'Geffenia_Magictool_Ice',
        # Batem com o `Slots: 1` do 490029 em db/re/item_db_equip.yml. Sem
        # `visual`: acessorio nao tem id de visual, e zero e o valor certo.
        'covas': 1,
        'descricao': [
            u'Um dos grandes tesouros do continente esquecido, Geffenia. Quem a obtém torna-se o soberano do zero absoluto.',
            u'^0000ffDEFM +10.^000000',
            u'^0000ffDano mágico contra todos os tamanhos +10%.^000000',
            u'A cada 3 de nível base:',
            u'^0000ffDano de [Nevasca] +2%.^000000',
            u'Ao aprender [Cometa] nv.5:',
            u'^0000ffConsumo de SP de [Esquife de Gelo] -35.^000000',
            u'^0000ffConjuração fixa de [Esquife de Gelo] -100%.^000000',
            u'Ao aprender [Esquife de Gelo] nv.5:',
            u'^0000ffDano de [Cometa] +50%.^000000',
            u'^0000ffConsumo de SP de [Cometa] -100.^000000',
            u'Ao aprender [Distorção Arcana] nv.5:',
            u'^0000ffDano de [Zero Absoluto] e [Esquife de Gelo] +50%.^000000',
            u'Ao aprender [Maestria Arcana] nv.5:',
            u'^0000ffPós-conjuração -30%.^000000',
            u'Tipo: ^777777Acessório^000000',
            u'DEF: ^7777772^000000 DEFM: ^7777770^000000',
            u'Peso: ^77777750^000000',
            u'Nível necessário: ^777777100^000000',
            u'Classes: ^777777Todas^000000',
        ],
    },
]


class Erro(Exception):
    pass


# ------------------------------------------------------------------ leitura

# Entrada de primeiro nivel: UM tab, `[numero] = {`. As tabelas aninhadas
# (`identifiedDescriptionName = {`) tem dois tabs e nao sao indexadas por
# numero, entao nao casam. O terminador `\r\n\t},` - um tab so - fecha a
# entrada pelo mesmo motivo.
CABECALHO = re.compile(r'\r\n\t\[(\d+)\] = \{')
FIM = '\r\n\t},'


def bloco(dados, iid):
    u"""(inicio, fim) da entrada de `iid`, ou None se ela nao existe."""
    m = re.search(r'\r\n\t\[%d\] = \{' % iid, dados)
    if not m:
        return None
    f = dados.find(FIM, m.start())
    if f < 0:
        raise Erro('entrada [%d] comeca mas nao termina' % iid)
    return (m.start(), f + len(FIM))


def recurso(dados, iid):
    u"""Os bytes crus do `identifiedResourceName` de `iid`."""
    lim = bloco(dados, iid)
    if lim is None:
        raise Erro('item %d nao esta no itemInfo.lua - nao da para copiar a '
                   'arte dele' % iid)
    # O `(?<!un)` NAO E ENFEITE, e a falta dele custou dois itens desenhando
    # errado entre 2026-08-18 e 2026-08-20. A string "unidentifiedResourceName"
    # TERMINA em "identifiedResourceName", e a linha do UNidentified vem
    # primeiro no bloco - entao o regex sem lookbehind casava com ela e
    # devolvia o recurso do item NAO IDENTIFICADO.
    #
    # Falha calada e so pela metade: quando as duas linhas trazem o mesmo
    # recurso - o caso de todo Etc e todo consumivel, e das seis primeiras
    # receitas desta tabela - o resultado e identico e nada aparece. Ela so
    # morde EQUIPAMENTO, que e onde o kRO poe um recurso generico de "item nao
    # identificado" no primeiro campo. Foi o que aconteceu com o Chapeu do Eden
    # (19272): ele ficou com `캡`, o gorro generico, no lugar de
    # `Garden_Of_Eden` - icone de inventario, imagem de collection e sprite de
    # chao trocados. A cabeca vestida continuou certa, porque aquela vem do
    # `accessoryid`/`View` e nao daqui, e por isso o valida_visual.py dava
    # "8 de 8 ok" sobre um item com metade da arte errada.
    m = re.search(r'(?<!un)identifiedResourceName = "([^"]*)"',
                  dados[lim[0]:lim[1]])
    if not m:
        raise Erro('item %d nao tem identifiedResourceName' % iid)
    return m.group(1)


def arte_do(dados, item):
    u"""O recurso que a entrada vai levar: ou o literal de `recurso`, ou o do
    item apontado por `arte_de`.

    `recurso` existe para o caso "traduzir entrada alheia SEM mexer na arte".
    Ali `arte_de` apontando para o proprio item parece a resposta obvia e e uma
    armadilha: o script se le a si mesmo, entao basta uma rodada ruim para o
    valor errado virar a fonte da rodada seguinte, e nao ha mais de onde
    recuperar o certo. Escrever o nome do recurso na receita quebra esse laco -
    a receita e versionada, o cliente nao.

    So ASCII: `resourceName` e bytes CP949, e nome coreano nao sobrevive a um
    literal de arquivo-fonte. Para esses, `arte_de`, que copia byte a byte.
    """
    if 'recurso' in item:
        try:
            return item['recurso'].encode('ascii')
        except UnicodeEncodeError:
            raise Erro('o `recurso` do item %d nao e ASCII - use `arte_de`, '
                       'que copia os bytes sem interpretar' % item['id'])
    return recurso(dados, item['arte_de'])


def onde_entra(dados, iid):
    u"""(offset, id_anterior, id_seguinte) de onde a entrada deve ser posta.

    Para o Lua a posicao e indiferente - `tbl` e um construtor de tabela, e a
    chave e explicita. Isto e so para o arquivo continuar legivel: a entrada
    nova cai entre os vizinhos numericos, como se sempre tivesse estado la.

    O criterio e a primeira entrada com ID maior, em ordem de arquivo. Medido
    em 2026-07-31: o arquivo esta ordenado, com 10 inversoes locais (15877 ->
    15858 e parecidas) - nenhuma joga um ID grande para o comeco, que e o unico
    caso que enganaria esta busca. Se um dia enganar, o pior que acontece e a
    entrada ficar num lugar estranho; o jogo nao muda.
    """
    anterior = None
    for m in CABECALHO.finditer(dados):
        atual = int(m.group(1))
        if atual > iid:
            return (m.start(), anterior, atual)
        anterior = atual
    # Nenhum ID maior: vai para o fim, antes do `\r\n}` que fecha a tabela.
    fim = dados.rfind(FIM)
    if fim < 0:
        raise Erro('nao achei o fim da ultima entrada')
    return (fim + len(FIM), anterior, None)


# ------------------------------------------------------------------ escrita

def monta(item, arte):
    u"""O bloco de texto da entrada, no formato exato do arquivo: CRLF, tabs,
    e o mesmo conjunto de campos que as entradas vizinhas usam."""
    # O texto da receita e unicode; o arquivo e ANSI. A conversao e para
    # cp1252, que e a codepage ANSI desta maquina e a mesma em que o bRO
    # entrega os textos dele. Caractere que nao couber ali e recusado com
    # erro claro: um byte errado num arquivo de 22 MB nao da erro nenhum, so
    # um nome torto no inventario e a duvida de sempre sobre encoding.
    def texto_de(bruto):
        try:
            return bruto.encode('cp1252')
        except UnicodeEncodeError:
            raise Erro('o item %d tem caractere fora da cp1252 em %r'
                       % (item['id'], bruto))

    nome = texto_de(item['nome'])
    descricao = [texto_de(l) for l in item['descricao']]

    linhas = ['\r\n\t[%d] = {' % item['id']]
    a = linhas.append
    a('\t\tunidentifiedDisplayName = "%s",' % nome)
    a('\t\tunidentifiedResourceName = "%s",' % arte)
    a('\t\tunidentifiedDescriptionName = { "" },')
    a('\t\tidentifiedDisplayName = "%s",' % nome)
    a('\t\tidentifiedResourceName = "%s",' % arte)
    a('\t\tidentifiedDescriptionName = {')
    for i, linha in enumerate(descricao):
        virgula = '' if i == len(descricao) - 1 else ','
        a('\t\t\t"%s"%s' % (linha, virgula))
    a('\t\t},')
    # `slotCount` e `ClassNum` nasceram zero fixo, e por seis itens
    # seguidos isso esteve certo: os nossos nao tinham cova nem
    # visual de cabeca. O Chapeu do Eden (19272) e o primeiro que
    # tem os dois, e zerar qualquer um dos dois falha CALADO - o
    # nome sai sem o "[1]" e a janela de encaixe de carta nao
    # sabe da cova, e o ClassNum e o id de visual que o cliente usa
    # para desenhar a peca na cabeca. Continuam OPCIONAIS: quem nao
    # declarar segue com zero, que e o que os seis anteriores
    # querem.
    a('\t\tslotCount = %d,' % item.get('covas', 0))
    a('\t\tClassNum = %d,' % item.get('visual', 0))
    a('\t\tcostume = false')
    a('\t},')
    return '\r\n'.join(linhas)


def aplica(caminho, verificar):
    if not os.path.exists(caminho):
        raise Erro('nao achei %s' % caminho)
    fh = open(caminho, 'rb')
    dados = fh.read()
    fh.close()
    antes = len(dados)
    print 'arquivo: %s' % caminho
    print 'tamanho: %d bytes, %d entradas' % (
        antes, len(CABECALHO.findall(dados)))
    print

    mudou = False
    for item in ITENS:
        # O nome vive em unicode na receita; para o console desta maquina ele
        # vai em cp1252, como vai para o arquivo.
        nome = item['nome'].encode('cp1252', 'replace')
        novo = monta(item, arte_do(dados, item))
        lim = bloco(dados, item['id'])
        if lim is None:
            pos, ant, seg = onde_entra(dados, item['id'])
            dados = dados[:pos] + novo + dados[pos:]
            print '  [novo   ] %d %s  (+%d bytes, entre %s e %s)' % (
                item['id'], nome, len(novo), ant, seg)
            mudou = True
        elif dados[lim[0]:lim[1]] == novo:
            print '  [ja tem ] %d %s  identica, nada a fazer' % (
                item['id'], nome)
        else:
            velho = lim[1] - lim[0]
            dados = dados[:lim[0]] + novo + dados[lim[1]:]
            print '  [troca  ] %d %s  (%d -> %d bytes)' % (
                item['id'], nome, velho, len(novo))
            mudou = True

    print
    if not mudou:
        print 'Nada a fazer: o arquivo ja esta como a receita pede.'
        return 0

    print 'tamanho: %d -> %d bytes  (%+d)' % (antes, len(dados),
                                              len(dados) - antes)
    if verificar:
        print '\n--verificar: nenhum byte foi gravado.'
        return 0

    backup = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M'))
    shutil.copy2(caminho, backup)
    print 'Backup: %s' % os.path.basename(backup)

    fh = open(caminho, 'wb')
    fh.write(dados)
    fh.close()
    print 'Gravado: %s' % caminho
    print
    print 'O cliente le o itemInfo.lua so na inicializacao - feche e reabra.'
    return 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) > 1:
        print __doc__
        sys.exit(1)
    try:
        sys.exit(aplica(args[0] if args else ITEMINFO,
                        '--verificar' in sys.argv))
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
