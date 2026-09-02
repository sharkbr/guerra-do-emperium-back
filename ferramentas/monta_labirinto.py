# -*- coding: utf-8 -*-
u"""Gera npc/guerra/labirinto_das_valquirias.txt inteiro.

    python monta_labirinto.py              # grava o arquivo
    python monta_labirinto.py --conferir   # so relata, nao grava
    python monta_labirinto.py --tabela     # imprime as salas e o grafo

O PORTAL VAI EM CIMA DO ARCO, E O MAPA DIZ ONDE ELES SAO

Isto e o que este arquivo tem de mais importante. O force_map1/2/3 traz
plantado, no proprio .rsw, o modelo

    내부소품\\반원워프장치.rsm     (semicirculo + warp + dispositivo)

que e o semicirculo de pedra que aparece no chao encostado nas paredes. Sao
22 no 1o andar, 25 no 2o e 40 no 3o, e ELES SAO OS PONTOS DE PORTAL DO MAPA:
quem desenhou a arena marcou onde cada warp devia ficar.

A primeira e a segunda versao deste labirinto ignoravam isso e escolhiam a
celula por conta propria - primeiro pelos extremos da sala, depois pela folga.
As duas ficaram erradas em jogo pelo mesmo motivo: o portal caia no meio do
chao liso, com o semicirculo vazio a dez celulas de distancia. Relatado em
2026-09-01: *"existe um semicirculo no chao no qual o portal deveria estar
la, nenhum portal esta corretamente posto no lugar"*.

A tabela `ARCOS` abaixo esta em coordenada de celula e foi tirada do .rsw:

    celula_x = largura/2 + pos.x / 5
    celula_y = altura/2 + pos.z / 5

O SINAL DO Z E `+`, E ISSO FOI ERRADO NA PRIMEIRA VOLTA. Com `-` a tabela sai
ESPELHADA no eixo norte-sul, e no force_map1 o erro nao aparece: aquele mapa e
simetrico de cima para baixo, entao o conjunto de arcos espelhado cai em cima
de si mesmo e so troca as salas de par (1 com 5, 6 com 8, 7 com 9). No
force_map2, que nao e simetrico, ele apareceu na primeira vez que alguem
entrou: todo portal ficava alguns metros ao lado da marcacao.

QUEM DECIDE A DUVIDA SAO OS PILARES. O mesmo .rsw traz 82 modelos de pilar no
1o andar e 72 no 2o, e pilar e celula FECHADA no .gat. Com `+` a conta acerta
82 de 82 e 72 de 72; com `-`, 70 e 50. Nao ha o que discutir depois disso -
e a regua que o proprio arquivo traz.

e depois encaixada na celula andavel mais proxima, porque parte dos arcos e
desenhada meio dentro da parede. Para refazer a extracao, e o `rsw.py` mais
essa conta - o .rsw esta no data.grf do bRO sem flag DES (no nosso ele tem
DES e o grf.py recusa).

O QUE NAO DA PARA CONFIRMAR, E NAO E POR FALTA DE PROCURA

**Qual portal levava a qual** - a fiacao. Isso morreu com o evento: nem o
wiki, nem as tres noticias oficiais arquivadas, nem o cliente guardam essa
informacao, porque ela so existia no script do servidor do bRO. A fiacao daqui
e NOSSA, e sai do sorteio com semente fixa mais abaixo.

O QUE ISSO CUSTA E O QUE ISSO POUPA: as POSICOES estao certas e nao precisam
de levantamento nenhum; a LIGACAO e escolha nossa, e mudar de ideia e trocar
`SEMENTE` ou escrever a mao no `FIACAO_MANUAL`.

ONDE MEXER, POR PEDIDO

  POR_TIPO         quantos monstros DE CADA TIPO por sala -> o volume
  RENASCE          o renascimento por andar, em ms
  TIPOS            quais monstros em cada andar
  PRECO            o pedagio de cada andar
  SEMENTE          re-sorteia a fiacao inteira
  FIACAO_MANUAL    trava uma aresta especifica, se um dia se quiser

Depois de gerar: mudanca so de spawn ou de portal pega com `@reloadscript`.
Se tiver mexido em mapflag, e reiniciar o map-server.

Roda em Python 2.7, como o resto de ferramentas/.
"""
import os
import random
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import confere_celula as cc

DESTINO = os.path.join(RAIZ, 'rathena', 'npc', 'guerra',
                       'labirinto_das_valquirias.txt')
ANDARES = ('force_map1', 'force_map2', 'force_map3')

# ================================================================ OS ARCOS
# Tirados do .rsw de cada andar - ver o cabecalho. Sala -> celulas.
#
# AS SALAS QUE NAO APARECEM AQUI NAO TEM ARCO NENHUM, e por isso ficam FORA
# do labirinto: as quatro camaras seladas do 1o andar (10 a 13) e a camara
# do sul do 3o (10). Nao e esquecimento do autor do mapa - as camaras do 1o
# andar sao aquelas que se enxerga de dentro do anel e nao se alcanca, e ele
# nao plantou warp em nenhuma. Por em qualquer uma delas um portal fora de
# arco e voltar ao defeito que este arquivo existe para corrigir.
ARCOS = {
    'force_map1': {
        1: [(64, 26), (100, 10), (100, 14), (100, 54), (136, 26)],
        2: [(100, 82), (100, 122), (100, 125)],
        3: [(26, 66), (26, 134)],
        4: [(174, 66), (174, 134)],
        5: [(66, 174), (134, 174)],
        6: [(26, 44), (44, 26)],
        7: [(156, 26), (174, 44)],
        8: [(26, 156), (44, 174)],
        9: [(156, 174), (174, 156)],
    },
    'force_map2': {
        1: [(160, 178), (174, 116)],
        2: [(26, 116), (50, 132)],
        3: [(40, 26)],
        4: [(160, 26)],
        5: [(26, 92), (40, 78)],
        6: [(160, 78), (174, 92)],
        7: [(86, 78), (100, 64), (100, 92), (114, 78)],
        8: [(56, 178), (96, 187), (136, 178)],
        9: [(86, 26), (100, 24), (100, 28), (100, 40), (114, 26)],
        10: [(92, 128), (108, 144)],
        11: [(32, 178)],
    },
    'force_map3': {
        1: [(100, 166)],
        2: [(20, 52), (60, 68), (68, 60)],
        3: [(92, 60), (100, 12), (108, 60)],
        4: [(132, 20), (180, 28)],
        5: [(132, 100), (140, 52), (140, 108)],
        6: [(60, 92), (60, 108), (108, 100)],
        7: [(132, 138), (140, 146), (180, 130)],
        8: [(12, 100), (20, 146), (28, 100)],
        9: [(92, 138), (100, 130), (100, 146), (108, 138)],
        10: [(60, 28), (68, 20)],
        11: [(172, 60), (180, 52)],
        12: [(20, 12), (20, 28)],
        13: [(172, 100), (180, 92), (180, 108)],
        14: [(60, 130), (68, 138)],
        15: [(20, 188), (28, 180)],
        16: [(172, 180), (180, 172)],
    },
}

NOMES = {
    'force_map1': {
        1: u'Atrio da Estatua', 2: u'Encruzilhada', 3: u'Corredor Oeste',
        4: u'Corredor Leste', 5: u'Galeria Norte', 6: u'Anel Sudoeste',
        7: u'Anel Sudeste', 8: u'Anel Noroeste', 9: u'Anel Nordeste',
        10: u'Camara Sudoeste (selada)', 11: u'Camara Sudeste (selada)',
        12: u'Camara Noroeste (selada)', 13: u'Camara Nordeste (selada)',
    },
    'force_map2': {
        1: u'Grande Salao Nordeste', 2: u'Salao Noroeste',
        3: u'Sala Sudoeste', 4: u'Sala Sudeste', 5: u'Sala Oeste',
        6: u'Sala Leste', 7: u'Sala do Centro', 8: u'Galeria do Norte',
        9: u'Sala do Sul', 10: u'Sala Central-Norte', 11: u'Vestibulo',
    },
    'force_map3': {
        1: u'Grande Galeria Norte', 2: u'Corredor Sudoeste',
        3: u'Corredor Central-Sul', 4: u'Corredor Sudeste',
        5: u'Corredor Leste-Central', 6: u'Corredor Central',
        7: u'Corredor Nordeste', 8: u'Corredor Oeste',
        9: u'Camara do Centro', 10: u'Camara do Sul (sem arco)',
        11: u'Camara Leste-Sul', 12: u'Camara Sudoeste',
        13: u'Camara Leste', 14: u'Camara Oeste-Norte',
        15: u'Camara Noroeste', 16: u'Camara Nordeste',
    },
}

ENTRADA = {'force_map1': 1, 'force_map2': 3, 'force_map3': 1}
TEM_ESCADA = ('force_map1', 'force_map2')
VOLTA = ('malangdo', 210, 150)
PORTA = ('malangdo', 211, 155)
PRECO = 1000000

# A fiacao e sorteada, mas com semente FIXA: sem isso cada rodada da
# ferramenta embaralharia o labirinto inteiro, e o jogador que ja aprendeu o
# caminho o perderia sem aviso. Trocar este numero e re-sortear de proposito.
SEMENTE = 20260901
UM_EM_CADA_EXPULSA = 4      # dos arcos que sobram da corrente
# OS DOIS PORTAIS DE EXPULSAO DO 3o ANDAR, do print de 2026-09-01: "tome
# bastante cuidado com esses 2 portais, eles o teleportarao para Malangdo
# novamente". Sao os UNICOS do andar - por isso o force_map3 entra no
# SO_EXPULSA_MANUAL abaixo, e o sorteio nao cria mais nenhum la.
FIACAO_MANUAL = {
    ('force_map3', 9, 0): 'SOBE',   # na Camara do Centro
    ('force_map3', 3, 1): 'SOBE',   # na ponta sul do Corredor Central-Sul
}
# 'SOBE' devolve para a CHEGADA DO 2o ANDAR, e nao para Malangdo nem para o
# ponto de salvamento. Pedido do dono em 2026-09-02: os dois portais que o
# print do bRO marcava como saida do 3o andar deixaram de cuspir o jogador
# para fora do labirinto e passaram a devolve-lo um andar acima, no comeco.
# Quem tomba num deles perde o caminho, nao a sessao - e nao paga pedagio de
# novo para voltar ao 2o.
SOBE_PARA = 'force_map2'
# Nestes andares NENHUM arco vira expulsao por sorteio: so os do
# FIACAO_MANUAL. Nos outros, um em cada UM_EM_CADA_EXPULSA vira.
SO_EXPULSA_MANUAL = ('force_map3',)

# ================================================ A PLANTA MANUAL DO 1o ANDAR
#
# Quando um andar aparece aqui, a fiacao dele NAO passa por ARCOS nem por
# corrente: sai desta lista, portal por portal, e cada destino e uma CELULA e
# nao uma sala. Foi assim que o 1o andar ficou depois do levantamento em jogo
# de 2026-09-01: o dono percorreu o andar e ditou cada portal.
#
# Cada linha e (x, y, raio, destino), e o destino pode ser:
#
#   (x, y)      celula exata deste mesmo mapa
#   'ENTRADA'   a celula de chegada do andar (o CHEGADA_MANUAL abaixo)
#   'SALA', n   a chegada CALCULADA da sala n - usado onde o levantamento
#               nao ditou celula. A conta e a mesma de sempre: a celula mais
#               aberta da sala, a pelo menos quatro celulas de qualquer
#               portal dela, agora contando o RAIO de cada um
#   'FORA'      expulsa para Malangdo
#   'ESCADA'    nao e portal: e onde nasce o NPC da escada
#
# O RAIO 2 DOS ONZE AVULSOS foi pedido assim ("todos com raio 2"): o gatilho
# fica 5x5 em vez de 3x3, e sao os portais que o jogador tromba sem procurar.
# Os dezoito do caminho continuam em raio 1.
#
# TRES DESTINOS DITADOS CAIRAM DENTRO DE PAREDE e foram encaixados na celula
# andavel mais proxima DA SALA CERTA, o que esta anotado linha a linha. O
# terceiro merece atencao: `26,164` tem a camara SELADA a duas celulas e o
# anel a tres - encaixar pelo mais perto teria prendido o jogador numa sala
# sem saida, entao foi para o anel.
CHEGADA_MANUAL = {
    'force_map1': (99, 18),
}

# ============================================ PORTAL NA PAREDE - o 2o andar
#
# Nestes andares o portal NAO fica onde o arco esta: fica na PAREDE DA SALA
# QUE DA PARA A SALA SEGUINTE, alinhado com ela. Pedido do dono em
# 2026-09-01, depois de percorrer o 2o andar:
#
#   "se estou no mapinha 2 e para ir para o mapinha 3, que fica acima,
#    o portal fica horizontalmente no meio e na parte de cima do mapinha"
#
# A regra reproduz os dois exemplos que ele deu, celula por celula:
#
#   sala 6 -> sala 7   a 7 fica a OESTE   ->  159,77   (ele disse "159 77")
#   sala 4 -> sala 6   a 6 fica ao NORTE  ->  173,40   ("no meio, em cima")
#   sala 9 -> sala 4   a 4 fica a LESTE   ->  113,25   ("na direita")
#
# COMO A CONTA FUNCIONA: o eixo dominante entre os dois centros escolhe a
# parede; a posicao AO LONGO da parede mira o centro da sala vizinha, preso
# dentro da caixa. Mirar em vez de centralizar resolve sozinho o caso em que
# as duas vizinhas ficam do mesmo lado - na sala 1 a seguinte e a anterior
# estao as duas a oeste, e os dois portais se separam em 51 celulas porque
# uma vizinha esta ao norte e a outra ao sul.
#
# CADA SALA GANHA DOIS: o de IDA, para a sala seguinte da corrente, e o de
# VOLTA, para a anterior - "sempre levando pro no anterior, para dar o efeito
# de labirinto". A primeira sala nao tem volta; a ultima tem a escada no lugar
# da ida, na parede OPOSTA a de onde se veio.
PORTAL_NA_PAREDE = ('force_map2',)
RAIO_IDA = 1
RAIO_VOLTA = 2
RECUO_DA_PAREDE = 1     # celulas para dentro, para o portal nao ficar no vao
FOLGA_DA_CHEGADA = 4    # celulas entre o pe de quem desembarca e o gatilho
PORTAIS_MANUAIS = {
    'force_map1': [
        # ---- os dezoito do caminho, raio 1
        (63, 26, 1, ('SALA', 6)),
        (134, 26, 1, 'ENTRADA'),
        (100, 81, 1, ('SALA', 7)),
        (99, 123, 1, 'ESCADA'),
        (26, 66, 1, 'ENTRADA'),
        (26, 134, 1, (26, 161)),
        (174, 66, 1, (174, 38)),        # ditado 174,37 - parede, 1 celula
        (174, 134, 1, 'FORA'),
        (65, 174, 1, ('SALA', 7)),
        (134, 174, 1, (161, 175)),      # ditado 163,175 - parede, 2 celulas
        (26, 44, 1, (26, 72)),
        (44, 26, 1, ('SALA', 3)),
        (156, 26, 1, (121, 100)),
        (174, 44, 1, 'FORA'),
        (26, 156, 1, 'ENTRADA'),
        (44, 174, 1, (71, 174)),
        (156, 174, 1, ('SALA', 8)),
        (174, 156, 1, (174, 128)),
        # ---- os onze avulsos, raio 2
        (192, 26, 2, (26, 161)),        # ditado 26,164 - parede; ver acima
        (74, 100, 2, (70, 174)),
        (124, 100, 2, (130, 26)),
        (100, 54, 2, 'ENTRADA'),
        (7, 27, 2, 'ENTRADA'),
        (8, 173, 2, (26, 73)),
        (25, 192, 2, (39, 26)),
        (174, 192, 2, (70, 174)),
        (191, 175, 2, (26, 73)),
        (25, 8, 2, 'ENTRADA'),
        (99, 11, 2, 'FORA'),            # o portal de volta
    ],
}

# ================================================== A CORRENTE DO PROPRIO bRO
#
# O 1o E O 2o ANDAR NAO SAO SORTEADOS: sao o caminho do bRO, levantado dos
# minimapas em 2026-09-01. O dono achou dois prints com o caminho desenhado em
# setas, e as salas casam uma a uma com as nossas, pelo formato.
#
#   1o:  1 -> 6 -> 3 -> 8 -> 5 -> 9 -> 4 -> 7 -> 2
#   2o:  3 -> 9 -> 4 -> 6 -> 7 -> 5 -> 2 -> 10 -> 1 -> 8 -> 11
#
# O print do 1o andar traz "Comeco" e "Fim" escritos. O do 2o nao, mas a sala
# 3 e a UNICA sem seta chegando, o que a faz a chegada - e nao a 11, que era o
# que estavamos usando. Em cada andar o fim da corrente e onde fica a escada.
#
# QUAL ARCO DE CADA SALA, quando a sala tem mais de um: pela direcao da seta
# no print. Seis salas tem arco unico e nao deixam duvida; nas outras cinco a
# seta aponta para um lado so:
#
#    7 -> 5    a seta vai para OESTE      -> arco (92,72), indice 0
#    2 -> 10   a seta vai para LESTE      -> arco (40,122), indice 1
#   10 -> 1    a seta desce para SUDESTE  -> arco (114,123), indice 3
#    1 -> 8    a seta vai para OESTE, no alto -> arco (160,174), indice 1
#    8 -> 11   a seta sobe para NOROESTE  -> arco (86,174), indice 0
#
# O QUE O PRINT NAO DIZ e para onde vao os NOVE arcos que sobram - o desenho
# so traz o caminho que resolve. Esses continuam sorteados, e sao eles que
# fazem o andar ser labirinto em vez de fila.
#
# O 1o ANDAR VEIO DO MESMO JEITO, num segundo print: "Comeco" na sala 1 e
# "Fim" na 2.
#
# DO 3o ANDAR veio um terceiro print, e ele traz menos: a CHEGADA (sala 1, o
# "110 188" do canto do minimapa cai dentro dela) e os DOIS portais que
# expulsam. A fiacao dele nao - e por decisao do dono ela fica livre: "aqui
# nao temos o grafo, de onde vai pra aonde, mas aqui e livre, o importante e
# o comeco".
CORRENTE_MANUAL = {
    # 1o andar - print de 2026-09-01, com "Comeco" na sala 1 e "Fim" na 2.
    # Nove salas, nove elos: a corrente cobre o andar inteiro.
    'force_map1': [1, 6, 3, 8, 5, 9, 4, 7, 2],
    'force_map2': [3, 9, 4, 6, 7, 5, 2, 10, 1, 8, 11],
}
# Qual arco de cada sala a corrente usa, quando a sala tem mais de um. Sai da
# direcao da seta no print, e em todos os casos abaixo a seta aponta para o
# lado em que fica a proxima sala - o que confirma a leitura.
ARCO_DA_CORRENTE = {
    # --- 1o andar
    ('force_map1', 1): 0,    # (66,26)   oeste  -> sala 6, a oeste
    ('force_map1', 6): 0,    # (26,44)   norte  -> sala 3, ao norte
    ('force_map1', 3): 1,    # (26,134)  norte  -> sala 8, ao norte
    ('force_map1', 8): 1,    # (44,174)  leste  -> sala 5, a leste
    ('force_map1', 5): 2,    # (134,174) leste  -> sala 9, a leste
    ('force_map1', 9): 1,    # (174,156) sul    -> sala 4, ao sul
    ('force_map1', 4): 0,    # (174,66)  sul    -> sala 7, ao sul
    ('force_map1', 7): 0,    # (156,26)  oeste  -> sala 2, o "Fim"
    ('force_map1', 2): 0,    # (100,81)  a ESCADA. VER A RESSALVA ABAIXO.
    # --- 3o andar: so um elo travado, e por necessidade. O arco 0 da sala
    #     9 e um dos dois que EXPULSAM, entao a corrente tem de sair pelo
    #     outro. O resto da fiacao do 3o andar continua sorteado, por
    #     decisao do dono: "aqui e livre, o importante e o comeco".
    ('force_map3', 9): 1,    # (108,140), porque o (92,140) expulsa
    # --- 2o andar
    ('force_map2', 7): 0,    # (92,72)   oeste
    ('force_map2', 2): 1,    # (40,122)  leste
    ('force_map2', 10): 3,   # (114,123) sudeste
    ('force_map2', 1): 1,    # (160,174) oeste, no alto
    ('force_map2', 8): 0,    # (86,174)  noroeste
}
# A RESSALVA, e e a unica do levantamento inteiro: o print do 1o andar marca a
# sala 2 como "Fim", mas nao diz QUAL dos dois arcos dela e a escada. A seta
# verde de la aponta para a chegada, nao para a saida. Escolhemos o arco sul
# (100,81), que e o mais perto de onde a seta termina; o outro e (100,118), e
# trocar e mudar o `0` acima para `1`.

# ------------------------------------------------------------- os bichos
# Os monstros de cada andar, em GRUPOS. Cada grupo e uma lista de tipos mais
# quantos DE CADA TIPO por sala - os tipos do grupo entram em TODAS as salas
# do andar, e o que muda de sala para sala e so a quantidade.
#
# SAO DUAS FAMILIAS, e a segunda entrou em 2026-09-02 a pedido do dono:
#
#   BIO 3  (1634..1639)  os seis de transclasse - Seyren, Eremes, Harword,
#                        Magaleta, Shecil, Katrinn. Nivel 140-142.
#   BIO 4  (2221..2227)  os SETE das classes novas - Randel Lawrence, Flamer
#                        Emul, Celia Alde, Chen Liu, Gertie We, Alphoccio
#                        Basil e Trentini. Nivel 141-142, 205k a 479k de HP.
#                        "Percebi que colocamos monstros apenas de
#                        transclasse. Faltaram aqueles que representam as
#                        novas classes."
#
# Os `G_*` de Bio 4 (2228..2234) FICARAM DE FORA, pela mesma decisao que
# tirou os de Bio 3: sao os MVPs do andar, de 2 a 3 milhoes de HP.
#
# A REPARTICAO tambem foi ditada: o 1o andar nao muda; o 2o corta 30% dos de
# Bio 3 e poe os de Bio 4 nesses 30%; o 3o SO ACRESCENTA, na mesma quantidade
# por sala que os seis herois ja tinham.
BIO3 = [1634, 1635, 1636, 1637, 1638, 1639]
BIO4 = [2221, 2222, 2223, 2224, 2225, 2226, 2227]
HEROIS = [1799, 1800, 1801, 1802, 1803, 1804]

GRUPOS = {
    'force_map1': [
        (BIO3, {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 2, 7: 2, 8: 2, 9: 2}),
    ],
    'force_map2': [
        # 27 por tipo contra os 39 de antes: os 30% que sairam
        (BIO3, {1: 4, 2: 4, 3: 3, 4: 3, 5: 3, 6: 3, 7: 2, 8: 2,
                9: 1, 10: 1, 11: 1}),
        (BIO4, {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1,
                9: 1, 10: 1, 11: 1}),
    ],
    'force_map3': [
        (HEROIS, {1: 3, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2,
                  10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1}),
        (BIO4, {1: 3, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2,
                10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1}),
    ],
}
# A MENTE MALIGNA NAO E MAIS DROP DE mob_db: e evento de morte.
#
# Por que mudou (2026-09-02): o labirinto inteiro tem de ser SEM DROP, e o
# `nomobloot` e o unico jeito de garantir isso sem tocar no mob_db - que
# valeria para lhz_dun03 e lhz_dun04 tambem. So que o mapflag mata TODO drop
# do mapa, inclusive a Mente. Enquanto o 3o andar tinha so os seis herois,
# cujo unico drop E a Mente, dava para deixar o andar sem o mapflag; com os
# sete de Bio 4 la dentro, cada um com oito drops, nao da mais.
#
# A saida: `nomobloot` nos TRES andares, e a Mente entregue pelo evento de
# morte dos seis herois. O `mob_npc_event_type` deste servidor e 1
# (conf/battle/monster.conf:266), entao quem recebe e quem deu o ultimo
# golpe - a mesma regra do Corredor Fantasma.
#
# A CHANCE MUDOU DE LUGAR: era `Rate: 2500` em db/guerra/mob_db_guerra.yml e
# agora e este numero. O override de la foi REMOVIDO no mesmo dia, para nao
# existirem duas fontes para o mesmo numero.
#
# `rand(100) < 25` e 25% cravado: o rand(100) do rAthena devolve 0..99.
MENTE_ID = 7583
MENTE_CHANCE = 25
EVENTO_DA_MENTE = 'labirinto_valquirias::OnHeroiMorto'

BRUTAL_ID = 2667
BRUTAL_SALAS = {'force_map2': [1, 2, 3, 4]}
BRUTAL_QTD = 1
RENASCE = {'force_map1': 30000, 'force_map2': 30000, 'force_map3': 60000}
RENASCE_BRUTAL = 60000

# Os quatro aneis do 1o andar tem uma CAMARA SELADA no meio, que e outra
# sala. Area de spawn que cubra o anel inteiro poe monstro dentro dela - o
# map_search_freecell olha se a celula e andavel, nunca se da para chegar
# nela. Por isso estes quatro nascem em dois bracos, escritos a mao, e a
# quantidade do POR_TIPO vale POR BRACO.
BRACOS = {
    6: [(11, 25, 5, 19), (40, 25, 5, 19)],
    7: [(159, 25, 5, 19), (188, 25, 5, 19)],
    8: [(11, 173, 5, 19), (40, 173, 5, 19)],
    9: [(159, 173, 5, 19), (188, 173, 5, 19)],
}


# ================================================== leitura do map_cache
def salas_de(mapa):
    xs, ys, cel, _ = cc.carrega(mapa)
    fora = []
    for g in cc.pedacos(xs, ys, cel):
        if len(g) < 100:
            continue
        gx = [i % xs for i in g]
        gy = [i // xs for i in g]
        if min(gx) == 0 or min(gy) == 0:      # a moldura de borda do mapa
            continue
        fora.append((set(g), min(gx), max(gx), min(gy), max(gy)))
    return xs, ys, fora


def folga(dentro, xs, x, y, teto=6):
    d = 0
    while d < teto:
        p = d + 1
        ok = True
        for ax in range(x - p, x + p + 1):
            for ay in (y - p, y + p):
                if (ay * xs + ax) not in dentro:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            for ay in range(y - p, y + p + 1):
                for ax in (x - p, x + p):
                    if (ax + ay * xs) not in dentro:
                        ok = False
                        break
                if not ok:
                    break
        if not ok:
            break
        d = p
    return d


def portais_da_sala(mapa, dentro, xs):
    u"""[(x, y, raio)] dos portais que caem nesta sala, na planta manual."""
    fora = []
    for (px, py, raio, _d) in PORTAIS_MANUAIS.get(mapa, []):
        if (py * xs + px) in dentro:
            fora.append((px, py, raio))
    return fora


def chegada_de(dentro, xs, x0, x1, y0, y1, arcos):
    u"""A celula onde o jogador desembarca: a mais aberta da sala, LONGE dos
    arcos dela.

    Duas coisas, e as duas vieram de relato em jogo:
      - longe de PAREDE (folga), porque a chegada colada na quina e feia e o
        jogador nao ve para onde ir;
      - a QUATRO celulas de qualquer portal da sala, porque "as vezes ao
        passar de um portal pro outro eu apareco quase no meio do novo
        portal" (2026-09-01). Ficar fora da area de toque de 3x3 nao basta.
    """
    fol = {}
    for i in dentro:
        x, y = i % xs, i // xs
        fol[(x, y)] = folga(dentro, xs, x, y)

    def perto(p):
        u"""Distancia ao portal mais proximo, DESCONTADO o raio dele.

        O raio importa: um portal de raio 2 tem gatilho 5x5, entao chegar a
        quatro celulas do CENTRO dele e chegar a duas da borda. Sem descontar,
        a chegada da sala 6 caia dentro do portal novo de 25,8 e o jogador era
        reteleportado antes de dar um passo.
        """
        ds = []
        for a in arcos:
            raio = a[2] if len(a) > 2 else 1
            ds.append(max(abs(p[0] - a[0]), abs(p[1] - a[1])) - raio)
        return min(ds) if ds else 99

    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for exigido in (6, 5, 4, 3, 2):
        cands = [p for p in fol if perto(p) >= exigido]
        if cands:
            return (max(cands, key=lambda p: (fol[p],
                                              -(abs(p[0] - cx) + abs(p[1] - cy)))),
                    fol, exigido)
    p = max(fol, key=lambda q: fol[q])
    return p, fol, 0


def area_de_spawn(dentro, xs, x0, x1, y0, y1):
    u"""(x, y, xs, ys) que NAO passa da caixa da sala.

    `<xs>,<ys>` de spawn e RAIO+1, nao lado. E o centro tem de ser celula
    andavel DA SALA: nove das salas tem pilar bem no meio da caixa.
    """
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if (cy * xs + cx) not in dentro:
        alvo = min(dentro, key=lambda i: abs(i % xs - cx) + abs(i // xs - cy))
        cx, cy = alvo % xs, alvo // xs
    return cx, cy, min(cx - x0, x1 - cx) + 1, min(cy - y0, y1 - cy) + 1


def parede_para(caixa, alvo_caixa, oposta=False):
    u"""Celula na parede da sala que da para `alvo_caixa`, mirando nela.

    O eixo dominante entre os dois centros escolhe a parede; a posicao AO
    LONGO da parede mira o centro da sala vizinha, presa dentro da caixa.
    Mirar em vez de centralizar resolve sozinho o caso das duas vizinhas do
    mesmo lado - na sala 1 do 2o andar a seguinte e a anterior estao as duas a
    oeste, e e a mira que separa os dois portais.
    """
    x0, x1, y0, y1 = caixa
    ax0, ax1, ay0, ay1 = alvo_caixa
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    acx, acy = (ax0 + ax1) // 2, (ay0 + ay1) // 2
    dx, dy = acx - cx, acy - cy
    if oposta:
        dx, dy = -dx, -dy
    r = RECUO_DA_PAREDE
    if abs(dx) >= abs(dy):
        px = (x1 - r) if dx > 0 else (x0 + r)
        py = min(max(acy if not oposta else cy, y0 + 3), y1 - 3)
    else:
        py = (y1 - r) if dy > 0 else (y0 + r)
        px = min(max(acx if not oposta else cx, x0 + 3), x1 - 3)
    return (px, py)


def encaixa_nos_arcos(mapa, sala, pedidos):
    u"""Poe cada portal EM CIMA de um arco, o mais perto do ideal dele.

    A parede continua sendo escolhida pela geometria (`parede_para`), mas o
    ponto final e o arco - o semicirculo de pedra que o mapa desenha. Foi o
    relato de 2026-09-02: "o portal ta muito pra direita, fora da marcacao",
    seis vezes, e em todas o desvio era exatamente a distancia entre a minha
    conta e o arco.

    Guloso: o par (pedido, arco) mais perto casa primeiro, e arco nao se
    repete. Pedido que fica sem arco - sala com menos arcos que portais - usa
    a posicao geometrica, e isso esta anotado na tabela do arquivo gerado.
    """
    livres = list(ARCOS[mapa].get(sala, []))
    fora = {}
    pares = []
    for i, (rot, ideal, _dest, _r) in enumerate(pedidos):
        for a in livres:
            d = abs(a[0] - ideal[0]) + abs(a[1] - ideal[1])
            pares.append((d, i, a))
    pares.sort()
    usados = set()
    for d, i, a in pares:
        if i in fora or a in usados:
            continue
        fora[i] = a
        usados.add(a)
    return [fora.get(i) for i in range(len(pedidos))]


def chegada_vinda_de(caixa_d, dentro_d, xs, caixa_o, portais_d):
    u"""Onde desembarcar em `d` quem veio de `o`: do lado de `o`.

    Pedido de 2026-09-02: "venho do mapinha da direita, aterrizo no da
    esquerda, e nasco no MEIO dele em vez de nascer no canto direito, como se
    tivesse acabado de atravessar".

    Sai da parede que da para a sala de origem e anda para dentro ate achar
    celula andavel que esteja longe de todo portal da sala - contando o raio
    de cada um, senao o jogador desembarca em cima de um e e cuspido de novo.
    """
    x0, x1, y0, y1 = caixa_d
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    px, py = parede_para(caixa_d, caixa_o)
    passo_x = 0 if px == cx else (1 if cx > px else -1)
    passo_y = 0 if py == cy else (1 if cy > py else -1)
    if passo_x == 0 and passo_y == 0:
        passo_y = 1

    def longe(x, y):
        for (qx, qy, qr) in portais_d:
            if max(abs(x - qx), abs(y - qy)) - qr < FOLGA_DA_CHEGADA:
                return False
        return True

    for k in range(0, 40):
        x, y = px + passo_x * k, py + passo_y * k
        if (y * xs + x) in dentro_d and longe(x, y):
            return (x, y)
    # nao achou andando reto: varre a sala inteira pelo mais perto da parede
    cands = [(abs(i % xs - px) + abs(i // xs - py), i % xs, i // xs)
             for i in dentro_d if longe(i % xs, i // xs)]
    if cands:
        cands.sort()
        return (cands[0][1], cands[0][2])
    return (cx, cy)


def portais_de_parede(mapa, salas, xs):
    u"""A lista (x, y, raio, destino) de um andar com portal na parede."""
    corrente = CORRENTE_MANUAL[mapa]
    caixa, cels = {}, {}
    for k, (dentro, x0, x1, y0, y1) in enumerate(salas, 1):
        caixa[k] = (x0, x1, y0, y1)
        cels[k] = dentro

    # ----- passo 1: onde fica cada portal
    posicoes = {}          # sala -> [(rotulo, (x,y), destino_sala, raio)]
    for i, s in enumerate(corrente):
        pedidos = []
        if i + 1 < len(corrente):
            prox = corrente[i + 1]
            pedidos.append(('ida', parede_para(caixa[s], caixa[prox]),
                            prox, RAIO_IDA))
        else:
            ant = corrente[i - 1]
            pedidos.append(('escada',
                            parede_para(caixa[s], caixa[ant], oposta=True),
                            'ESCADA', 1))
        if i > 0:
            ant = corrente[i - 1]
            pedidos.append(('volta', parede_para(caixa[s], caixa[ant]),
                            ant, RAIO_VOLTA))
        arcos = encaixa_nos_arcos(mapa, s, pedidos)
        posicoes[s] = []
        for j, (rot, ideal, dest, raio) in enumerate(pedidos):
            pos = arcos[j] if arcos[j] else ideal
            posicoes[s].append((rot, pos, dest, raio, arcos[j] is not None))

    # ----- passo 2: os destinos, agora que se sabe onde estao os portais
    por_sala = dict((s, [(p[1][0], p[1][1], p[3]) for p in v])
                    for s, v in posicoes.items())
    fora = []
    for s in corrente:
        for (rot, pos, dest, raio, no_arco) in posicoes[s]:
            if dest == 'ESCADA':
                fora.append((pos[0], pos[1], raio, 'ESCADA'))
                continue
            alvo = chegada_vinda_de(caixa[dest], cels[dest], xs, caixa[s],
                                    por_sala.get(dest, []))
            fora.append((pos[0], pos[1], raio, (alvo[0], alvo[1])))
    return fora


def levanta():
    fora = {}
    for mapa in ANDARES:
        xs, _ys, salas = salas_de(mapa)
        if mapa in PORTAL_NA_PAREDE:
            PORTAIS_MANUAIS[mapa] = portais_de_parede(mapa, salas, xs)
        info = {}
        for k, (dentro, x0, x1, y0, y1) in enumerate(salas, 1):
            if mapa in PORTAIS_MANUAIS:
                arcos = portais_da_sala(mapa, dentro, xs)
            else:
                arcos = ARCOS[mapa].get(k, [])
            cheg, fol, exig = chegada_de(dentro, xs, x0, x1, y0, y1, arcos)
            if mapa in CHEGADA_MANUAL and k == ENTRADA[mapa]:
                cheg = CHEGADA_MANUAL[mapa]
            info[k] = dict(cheg=cheg, arcos=arcos, caixa=(x0, x1, y0, y1),
                           spawn=area_de_spawn(dentro, xs, x0, x1, y0, y1),
                           fc=fol.get(cheg, 0), exig=exig, n=len(dentro),
                           dentro=dentro, xs=xs)
        fora[mapa] = info
    return fora


# ==================================================== a fiacao dos portais
def fia(mapa, info):
    u"""{(sala, indice_do_arco): destino} - destino e sala, 'FORA' ou 'ESCADA'.

    A CORRENTE E O QUE GARANTE QUE DA PARA SAIR. O arco 0 de cada sala liga a
    proxima da corrente, e a corrente passa por TODAS as salas com arco a
    partir da entrada - entao existe sempre um caminho, e ele passa pelo
    andar inteiro. O ultimo elo e a escada.

    Os arcos que sobram sao ruido: levam a uma sala sorteada, e um em cada
    quatro expulsa para Malangdo. Sao eles que fazem o labirinto ser
    labirinto - sem eles a corrente seria uma fila.
    """
    rnd = random.Random(SEMENTE + hash(mapa) % 1000)
    salas = sorted(ARCOS[mapa])
    entrada = ENTRADA[mapa]
    if mapa in CORRENTE_MANUAL:
        corrente = list(CORRENTE_MANUAL[mapa])
        if sorted(corrente) != salas:
            raise ValueError('%s: a corrente manual nao cobre as mesmas salas '
                             'que o ARCOS (%s contra %s)'
                             % (mapa, sorted(corrente), salas))
        if corrente[0] != entrada:
            raise ValueError('%s: a corrente manual comeca na sala %d e o '
                             'ENTRADA diz %d' % (mapa, corrente[0], entrada))
    else:
        resto = [s for s in salas if s != entrada]
        rnd.shuffle(resto)
        corrente = [entrada] + resto

    # o arco que cada sala usa PARA A CORRENTE - o primeiro, salvo quando o
    # levantamento diz outro
    elo = dict((s, ARCO_DA_CORRENTE.get((mapa, s), 0)) for s in salas)

    fiacao = {}
    for i, s in enumerate(corrente):
        if i + 1 < len(corrente):
            fiacao[(s, elo[s])] = corrente[i + 1]
        else:
            fiacao[(s, elo[s])] = 'ESCADA' if mapa in TEM_ESCADA else entrada

    sobra = 0
    for s in salas:
        for idx in range(len(ARCOS[mapa][s])):
            if idx == elo[s]:
                continue
            sobra += 1
            if (mapa not in SO_EXPULSA_MANUAL
                    and sobra % UM_EM_CADA_EXPULSA == 0):
                fiacao[(s, idx)] = 'FORA'
            else:
                # o isca nao pode repetir o destino do elo da corrente: dois
                # portais da mesma sala indo ao mesmo lugar nao enganam
                # ninguem, so tiram uma escolha do jogador
                elo_destino = fiacao.get((s, elo[s]))
                outras = [o for o in salas if o != s and o != elo_destino]
                fiacao[(s, idx)] = rnd.choice(outras or [o for o in salas if o != s])

    for chave, valor in FIACAO_MANUAL.items():
        if chave[0] == mapa:
            fiacao[(chave[1], chave[2])] = valor
    return fiacao, corrente


def sala_da_celula(info, x, y):
    for k, d in info.items():
        if (y * d['xs'] + x) in d['dentro']:
            return k
    return None


def resolve(mapa, destino, info, todos=None):
    u"""destino da planta manual -> (mapa, x, y)."""
    if destino == 'FORA':
        return VOLTA
    if destino == 'SOBE':
        d = todos[SOBE_PARA]
        return (SOBE_PARA,) + tuple(d[ENTRADA[SOBE_PARA]]['cheg'])
    if destino == 'ESCADA':
        raise ValueError('a ESCADA nao e warp: nao se resolve destino dela')
    if destino == 'ENTRADA':
        return (mapa,) + tuple(info[ENTRADA[mapa]]['cheg'])
    if isinstance(destino, tuple) and destino and destino[0] == 'SALA':
        return (mapa,) + tuple(info[destino[1]]['cheg'])
    return (mapa, destino[0], destino[1])


def confere_gatilhos(mapa, portais, info):
    u"""Nenhum destino pode cair DENTRO do gatilho de outro portal.

    Se cair, o jogador desembarca em cima de um warp e e teleportado de novo
    antes de dar um passo - e a cadeia pode ate nao terminar. A conta usa o
    raio de cada portal: gatilho de raio r e (2r+1) por (2r+1).
    """
    erros = []
    for (px, py, raio, destino) in portais:
        if destino == 'ESCADA':
            continue          # NPC de clicar: nao tem area de toque
        alvo = resolve(mapa, destino, info)
        if alvo[0] != mapa:
            continue
        for (qx, qy, qr, _d) in portais:
            if max(abs(alvo[1] - qx), abs(alvo[2] - qy)) <= qr:
                erros.append('o portal %d,%d manda para %d,%d, que esta '
                             'DENTRO do gatilho do portal %d,%d (raio %d)'
                             % (px, py, alvo[1], alvo[2], qx, qy, qr))
    return erros


# ============================================================== o arquivo
CABECALHO = u"""//===== Guerra do Emperium ===================================
//= Labirinto das Valquirias
//===== ARQUIVO GERADO =======================================
//= NAO EDITAR A MAO. Sai inteiro de ferramentas/monta_labirinto.py,
//= e a proxima rodada reescreve tudo.
//=
//= Volume de monstro, renascimento, fiacao dos portais e
//= pedagio sao cada um UMA constante no topo daquela
//= ferramenta.
//===== Onde =================================================
//= A porta: {porta} - o Portal, que se CLICA.
{chegadas}//= A volta, de toda saida: {volta}.
//===== Descricao ============================================
//= Tres andares de salas que NAO SE TOCAM. Nao ha corredor
//= entre elas, nao ha porta: cada sala e uma ilha, e todo
//= deslocamento e por portal. Alguns portais levam a outra
//= sala, alguns devolvem o jogador para Malangdo, e um por
//= andar leva ao andar de baixo - cobrando de novo.
//=
//= Andares 1 e 2: os monstros do Biolaboratorio 3. Dao EXP e
//= NAO largam nada. Andar 3: os seis herois selados, que sao
//= a unica fonte da Mente Maligna.
//===== O PORTAL FICA EM CIMA DO ARCO ========================
//= O mapa TRAZ os pontos de portal desenhados. O semicirculo
//= de pedra que aparece no chao encostado nas paredes e um
//= modelo 3D plantado no .rsw, e o nome dele em coreano
//= significa, ao pe da letra, "dispositivo de warp
//= semicircular". Sao 22 no 1o andar, 25 no 2o e 40 no 3o -
//= o autor do mapa marcou onde cada warp devia ficar.
//=
//= As duas primeiras versoes deste arquivo escolhiam a celula
//= por conta propria e erraram as duas: o portal caia no meio
//= do chao liso com o semicirculo vazio a dez celulas dali.
//= Agora cada portal esta EM CIMA de um arco, e a tabela de
//= cada andar diz qual.
//=
//= AS SALAS SEM ARCO FICAM FORA DO LABIRINTO: as quatro
//= camaras seladas do 1o andar (aquelas que se enxerga de
//= dentro do anel e nao se alcanca) e a camara do sul do 3o.
//= O autor do mapa nao plantou warp em nenhuma delas.
//===== O QUE E DO bRO E O QUE E NOSSO =======================
//= DO bRO, confirmado: o mapa (force_map1/2/3, identificado
//= pelo minimapa de uma screenshot da noticia oficial de 2023
//= comparada contra os 761 minimapas do GRF do bRO); os tres
//= andares; o pedagio de 1.000.000z por andar; nao gravar
//= Portal e nao teleportar; os portais que expulsam do mapa;
//= e a Mente Maligna so no terceiro andar.
//=
//= DO MAPA, que e a fonte mais forte que existe para isto: a
//= POSICAO de cada portal.
//=
//= NOSSO, e nao ha como ser diferente: A FIACAO - qual portal
//= leva a qual sala. Isso morreu com o evento. Nem o wiki, nem
//= as tres noticias oficiais arquivadas, nem o cliente
//= guardam essa informacao, porque ela so existia no script do
//= servidor do bRO, que fechou em 2026-07-29.
//===== Como a fiacao daqui foi montada ======================
//= Sorteio com SEMENTE FIXA, para o labirinto nao mudar a cada
//= rodada da ferramenta.
//=
//= A CORRENTE E O QUE GARANTE QUE DA PARA SAIR: o primeiro
//= arco de cada sala liga a proxima da corrente, e a corrente
//= passa por TODAS as salas com arco a partir da entrada.
//= Existe sempre um caminho, e ele atravessa o andar inteiro.
//= O ultimo elo e a escada.
//=
//= Os arcos que sobram sao o ruido: levam a uma sala sorteada,
//= e um em cada quatro expulsa para Malangdo. Sao eles que
//= fazem o labirinto ser labirinto.
//===== As tres arenas vazias ================================
//= force_map1, force_map2 e force_map3 sao mapas que a Gravity
//= desenhou e nunca usou. O rAthena os traz COMENTADOS em
//= conf/maps_athena.conf (linhas 19-21). Quem os liga e
//= conf/guerra/mapas_guerra.txt, por um `import:` no rodape
//= daquele arquivo.
//=
//= NAO PRECISA DE PATCH DE CLIENTE: os tres mapas ja estao no
//= data.grf deste cliente, minimapa incluso.
//===== Onde o jogador desembarca ============================
//= Na celula mais aberta da sala, e a pelo menos quatro
//= celulas de qualquer portal dela. As duas exigencias vieram
//= de relato em jogo: chegada colada na parede nao deixa ver
//= para onde ir, e chegada ao lado de um portal faz o primeiro
//= passo teleportar - "as vezes ao passar de um portal pro
//= outro eu apareco quase no meio do novo portal".
//===== As areas de spawn nao sao o retangulo obvio ==========
//= `<xs>,<ys>` de spawn e RAIO+1, nao lado: o mob_spawn chama
//= map_search_freecell com xs-1 (src/map/mob.cpp:1149). Cada
//= area foi recortada para caber DENTRO da caixa da sala, e o
//= centro de cada uma e celula andavel - nove salas tem pilar
//= bem no meio da caixa.
//=
//= Os quatro aneis do 1o andar nascem em DOIS BRACOS cada um,
//= porque area que cubra o anel inteiro poe monstro dentro da
//= camara selada, que e outra sala: o map_search_freecell olha
//= se a celula e andavel, nunca se da para chegar nela.
//=
//= E NAO SE USA `0,0`: os tres mapas tem uma moldura andavel de
//= 399 celulas na borda, solta do resto.
//===== O monstro e ALEATORIO, e esta em TODA sala ===========
//= Os seis tipos entram em todas as salas do labirinto,
//= inclusive a de chegada. O que muda de sala para sala e so a
//= quantidade.
//===== As duas regras que mudamos ===========================
//= O bRO dizia "os monstros nao dao EXP e nem dropam nenhum
//= outro item". Decisao do dono em 2026-09-01: EXP FICA nos
//= tres andares; DROP SAI, mas so nos andares 1 e 2 e por
//= MAPFLAG (`nomobloot`), nunca por mob_db - tirar o drop dos
//= monstros de Biolaboratorio 3 no mob_db tiraria o drop em
//= lhz_dun03 tambem (CLAUDE.md 4.16).
//=
//= O 3o andar NAO tem `nomobloot`, e nao pode ter: e ele que
//= deixa a Mente Maligna cair, hoje a 25%.
//===== As regras dos tres mapas =============================
//=   nomemo  noteleport  nosave  nobranch  (+ nomobloot em 1 e 2)
//=
//= O `nosave` NAO E ENFEITE: sem ele, deslogar dentro e voltar
//= depois pula o pedagio do andar.
//===== O renascimento =======================================
//= 30 segundos nos andares 1 e 2, 60 no 3o, sem variacao.
//============================================================
"""


def bloco_chegadas(dados):
    linhas = []
    for n, mapa in enumerate(ANDARES, 1):
        s = ENTRADA[mapa]
        cx, cy = dados[mapa][s]['cheg']
        linhas.append(u'//= %do andar: %-11s chegada %3d,%-3d (%s)'
                      % (n, mapa, cx, cy, NOMES[mapa][s]))
    return u'\n'.join(linhas) + u'\n'


def tabela_do_andar(dados, mapa, n, fiacao, corrente):
    info = dados[mapa]
    out = [u'//============================================================',
           u'// %do ANDAR - %s' % (n, mapa),
           u'//',
           u'// %d salas no mapa, %d no labirinto (as outras nao tem arco).'
           % (len(info), len(ARCOS[mapa])),
           u'// A corrente que resolve o andar: %s'
           % u' -> '.join(str(s) for s in corrente),
           u'//',
           u'//  sala  nome                        chegada   portais (em cima do arco)']
    for k in sorted(info):
        d = info[k]
        if k not in ARCOS[mapa]:
            out.append(u'//   %2d   %-26s   --      sem arco: fora do labirinto'
                       % (k, NOMES[mapa][k]))
            continue
        ps = []
        for i, a in enumerate(d['arcos']):
            alvo = fiacao.get((k, i))
            if alvo == 'FORA':
                rot = u'EXPULSA'
            elif alvo == 'SOBE':
                rot = u'SOBE ao 2o'
            elif alvo == 'ESCADA':
                rot = u'ESCADA'
            else:
                rot = u'->%d' % alvo
            ps.append(u'%d,%d %s' % (a[0], a[1], rot))
        marca = u'  <- entrada' if ENTRADA[mapa] == k else u''
        out.append(u'//   %2d   %-26s %3d,%-3d   %s%s'
                   % (k, NOMES[mapa][k], d['cheg'][0], d['cheg'][1],
                      u' | '.join(ps), marca))
    out.append(u'//============================================================')
    return u'\n'.join(out)


def tabela_manual(dados, mapa, n):
    info = dados[mapa]
    out = [u'//============================================================',
           u'// %do ANDAR - %s' % (n, mapa),
           u'//',
           u'// PLANTA MANUAL: cada portal e cada destino foram ditados pelo',
           u'// levantamento em jogo, celula por celula. Nao ha corrente',
           u'// sorteada aqui.',
           u'//',
           u'// chegada do andar: %d,%d' % tuple(info[ENTRADA[mapa]]['cheg']),
           u'//',
           u'//   portal    raio  sala             ->  destino']
    for (px, py, raio, destino) in PORTAIS_MANUAIS[mapa]:
        s = sala_da_celula(info, px, py)
        if destino == 'ESCADA':
            alvo = u'a ESCADA (NPC, nao e warp)'
        else:
            dm, dx, dy = resolve(mapa, destino, info)
            if dm != mapa:
                alvo = u'EXPULSA para %s %d,%d' % (dm, dx, dy)
            else:
                ds = sala_da_celula(info, dx, dy)
                alvo = u'%3d,%-3d  (sala %s)' % (dx, dy, ds)
        out.append(u'//   %3d,%-3d    %d   %-16s ->  %s'
                   % (px, py, raio, NOMES[mapa].get(s, u'?')[:16], alvo))
    out.append(u'//============================================================')
    return u'\n'.join(out)


def monta():
    dados = levanta()
    fiacoes = {}
    for mapa in ANDARES:
        if mapa in PORTAIS_MANUAIS:
            fiacoes[mapa] = (None, None)
        else:
            fiacoes[mapa] = fia(mapa, dados[mapa])

    p = [CABECALHO.format(porta=u'%s %d,%d' % PORTA,
                          volta=u'%s %d,%d' % VOLTA,
                          chegadas=bloco_chegadas(dados))]

    p.append(u'''
//============================================================
// O controlador: o pedagio, o ponto de volta e a Mente Maligna
//
// A MENTE NAO E DROP. Os tres andares tem `nomobloot` - o
// labirinto e sem drop, e isso vale tambem para os sete de Bio
// 4, que fora daqui largam oito itens cada. Entao ela vem do
// evento de morte dos seis herois, abaixo.
//
// QUEM RECEBE E QUEM DEU O ULTIMO GOLPE: o mob_npc_event_type
// deste servidor e 1 (conf/battle/monster.conf:266). Mesma
// regra do Corredor Fantasma.
//
// `rand(100) < %d` e %d%% cravado - o rand(100) do rAthena
// devolve 0..99.
//
// MOCHILA CHEIA LARGA NO CHAO: o `getitem` chama pc_additem e,
// se nao couber, o item cai aos pes de quem matou. E o que se
// quer aqui - melhor no chao do que evaporar.
//============================================================
-\tscript\tlabirinto_valquirias\t-1,{
\tend;

OnHeroiMorto:
\tif (rand(100) < .MenteChance)
\t\tgetitem .MenteId, 1;
\tend;

OnInit:
\t.Preco = %d;
\t.Volta$ = "%s";
\t.VoltaX = %d;
\t.VoltaY = %d;
\t.MenteId = %d;
\t.MenteChance = %d;
\tend;
}
''' % (MENTE_CHANCE, MENTE_CHANCE, PRECO, VOLTA[0], VOLTA[1], VOLTA[2],
        MENTE_ID, MENTE_CHANCE))

    e1 = dados['force_map1'][ENTRADA['force_map1']]['cheg']
    p.append(PORTAL_TXT % (PORTA[1], PORTA[2], PORTA[0], PORTA[1], PORTA[2],
                           e1[0], e1[1]))

    palavras = {'force_map1': (u'Segundo', 'force_map2'),
                'force_map2': (u'Terceiro', 'force_map3')}
    for de in TEM_ESCADA:
        if de in PORTAIS_MANUAIS:
            pos = [(x, y) for (x, y, _r, d) in PORTAIS_MANUAIS[de]
                   if d == 'ESCADA'][0]
            sala = sala_da_celula(dados[de], pos[0], pos[1])
        else:
            fiacao, _c = fiacoes[de]
            sala = [s for (s, i), d in fiacao.items() if d == 'ESCADA'][0]
            idx = [i for (s, i), d in fiacao.items() if d == 'ESCADA'][0]
            pos = ARCOS[de][sala][idx]
        palavra, para = palavras[de]
        cheg = dados[para][ENTRADA[para]]['cheg']
        extra = u''
        if para == 'force_map3':
            extra = (u'\tmes "[Escada]";\n\tmes "N\u00e3o h\u00e1 escada de volta. '
                     u'Do terceiro andar s\u00f3 se sai pelos portais que expulsam.";\n'
                     u'\tnext;\n')
        p.append(ESCADA_TXT % (palavra.lower(), NOMES[de][sala], sala,
                               de, pos[0], pos[1], palavra, extra,
                               para, cheg[0], cheg[1]))

    p.append(u'//============================================================\n'
             u'// As regras dos tres mapas. O `nomobloot` esta nos TRES: o\n'
             u'// labirinto inteiro e sem drop. A Mente Maligna nao passa por\n'
             u'// ele porque nao e drop - e o evento de morte dos seis herois,\n'
             u'// no OnHeroiMorto la em cima.\n'
             u'//============================================================')
    for mapa in ANDARES:
        p.append(u'%s\tmapflag\tnomemo' % mapa)
        p.append(u'%s\tmapflag\tnoteleport' % mapa)
        p.append(u'%s\tmapflag\tnosave\t%s,%d,%d' % ((mapa,) + VOLTA))
        p.append(u'%s\tmapflag\tnobranch' % mapa)
        p.append(u'%s\tmapflag\tnomobloot' % mapa)
        p.append(u'')

    for n, mapa in enumerate(ANDARES, 1):
        info = dados[mapa]
        fiacao, corrente = fiacoes[mapa]
        if mapa in PORTAIS_MANUAIS:
            p.append(tabela_manual(dados, mapa, n))
            erros = confere_gatilhos(mapa, PORTAIS_MANUAIS[mapa], info)
            if erros:
                raise ValueError('%s: %s' % (mapa, '; '.join(erros)))
            for j, (px, py, raio, destino) in enumerate(PORTAIS_MANUAIS[mapa]):
                if destino == 'ESCADA':
                    continue
                dm, dx, dy = resolve(mapa, destino, info)
                p.append(u'%s,%d,%d,0\twarp\tlv%sp%02d\t%d,%d,%s,%d,%d'
                         % (mapa, px, py, mapa[-1], j, raio, raio, dm, dx, dy))
        else:
            p.append(tabela_do_andar(dados, mapa, n, fiacao, corrente))
            for sala in sorted(ARCOS[mapa]):
                for i, a in enumerate(ARCOS[mapa][sala]):
                    alvo = fiacao[(sala, i)]
                    if alvo == 'ESCADA':
                        continue
                    if alvo == 'FORA':
                        dm, dx, dy = VOLTA
                    elif alvo == 'SOBE':
                        dm = SOBE_PARA
                        dx, dy = dados[SOBE_PARA][ENTRADA[SOBE_PARA]]['cheg']
                    else:
                        dm = mapa
                        dx, dy = info[alvo]['cheg']
                    p.append(u'%s,%d,%d,0\twarp\tlv%ss%02d%d\t1,1,%s,%d,%d'
                             % (mapa, a[0], a[1], mapa[-1], sala, i, dm, dx, dy))
        p.append(u'')
        p.append(u'// OS MONSTROS. Os seis tipos em TODA sala do labirinto - o')
        p.append(u'// que muda e a quantidade. NAO PONHA COMENTARIO NO FIM')
        p.append(u'// DESTAS LINHAS: o npc_parsesrcfile enche o w4 ate o fim da')
        p.append(u'// linha e o comentario entra dentro do nome do evento.')
        total = 0
        for (tipos, por_tipo) in GRUPOS[mapa]:
            for k in sorted(por_tipo):
                q = por_tipo[k]
                areas = BRACOS.get(k) if mapa == 'force_map1' else None
                if not areas:
                    areas = [info[k]['spawn']]
                for (ax, ay, arx, ary) in areas:
                    for mid in tipos:
                        ev = (u',"%s"' % EVENTO_DA_MENTE
                              if mid in HEROIS else u'')
                        p.append(u'%s,%d,%d,%d,%d\tmonster\t--ja--'
                                 u'\t%d,%d,%d,0%s'
                                 % (mapa, ax, ay, arx, ary, mid, q,
                                    RENASCE[mapa], ev))
                        total += q
        for k in BRUTAL_SALAS.get(mapa, []):
            ax, ay, arx, ary = info[k]['spawn']
            p.append(u'%s,%d,%d,%d,%d\tmonster\t--ja--\t%d,%d,%d,0'
                     % (mapa, ax, ay, arx, ary, BRUTAL_ID, BRUTAL_QTD,
                        RENASCE_BRUTAL))
            total += BRUTAL_QTD
        p.append(u'// %d monstros neste andar' % total)
        p.append(u'')

    texto = u'\n'.join(p)
    return texto.encode('ascii', 'backslashreplace').decode('unicode_escape')


PORTAL_TXT = u"""//============================================================
// A porta, em Malangdo
//
// O bRO punha o Portal em malangdo 209,153 e mandava CLICAR
// nele. Aquela celula e FECHADA no nosso map_cache; %d,%d e a
// livre mais proxima com as nove vizinhas livres. Sprite
// `PORTAL` (10007), e nao o 45, que e sprite de warp: este e
// NPC de clicar.
//============================================================
%s,%d,%d,4\tscript\tPortal das Valqu\u00edrias\tPORTAL,{
\t.@preco = getvariableofnpc(.Preco, "labirinto_valquirias");
\tmes "[Portal das Valqu\u00edrias]";
\tmes "O ar range e se abre. Do outro lado h\u00e1 pedra escura, tochas presas em pedestais e um sil\u00eancio que n\u00e3o \u00e9 deste lugar.";
\tnext;
\tmes "[Portal das Valqu\u00edrias]";
\tmes "As guerreiras de Asgard cobram pela passagem. " + callfunc("F_InsertComma", .@preco) + " zeny para pisar no primeiro andar.";
\tnext;
\tmes "[Portal das Valqu\u00edrias]";
\tmes "Uma coisa antes: l\u00e1 dentro as salas n\u00e3o se tocam. N\u00e3o h\u00e1 corredor, n\u00e3o h\u00e1 porta. S\u00f3 portais \u2014 e eles n\u00e3o devem satisfa\u00e7\u00e3o a ningu\u00e9m sobre onde v\u00e3o dar.";
\tnext;
\tif (select("Pagar e atravessar:Ficar onde estou") == 2) {
\t\tmes "[Portal das Valqu\u00edrias]";
\t\tmes "S\u00e1bio.";
\t\tclose;
\t}
\tif (Zeny < .@preco) {
\t\tmes "[Portal das Valqu\u00edrias]";
\t\tmes "Voc\u00ea n\u00e3o tem os " + callfunc("F_InsertComma", .@preco) + " zeny. O rasgo se fecha um pouco, como quem perde o interesse.";
\t\tclose;
\t}
\tZeny -= .@preco;
\tmes "[Portal das Valqu\u00edrias]";
\tmes "Boa sorte. Voc\u00ea vai precisar.";
\tclose2;
\twarp "force_map1", %d, %d;
\tend;
}
"""

ESCADA_TXT = u"""//============================================================
// A descida para o %s andar - fica na %s (sala %d), em cima
// de um arco, como todo portal deste labirinto. Sprite
// `PORTAL`: tambem se clica.
//============================================================
%s,%d,%d,4\tscript\tEscada para o %s Andar\tPORTAL,{
\t.@preco = getvariableofnpc(.Preco, "labirinto_valquirias");
\tmes "[Escada]";
\tmes "Os degraus descem para o escuro.";
\tnext;
\tmes "[Escada]";
\tmes "Descer custa mais " + callfunc("F_InsertComma", .@preco) + " zeny.";
\tnext;
%s\tif (select("Descer:Voltar atr\u00e1s") == 2) {
\t\tmes "[Escada]";
\t\tmes "Os degraus continuam a\u00ed.";
\t\tclose;
\t}
\tif (Zeny < .@preco) {
\t\tmes "[Escada]";
\t\tmes "Faltam zeny. A escada n\u00e3o negocia.";
\t\tclose;
\t}
\tZeny -= .@preco;
\tclose2;
\twarp "%s", %d, %d;
\tend;
}
"""


def main(argv):
    dados = levanta()
    if '--tabela' in argv:
        for n, mapa in enumerate(ANDARES, 1):
            if mapa in PORTAIS_MANUAIS:
                print tabela_manual(dados, mapa, n).encode('utf-8')
            else:
                fiacao, corrente = fia(mapa, dados[mapa])
                print tabela_do_andar(dados, mapa, n, fiacao,
                                      corrente).encode('utf-8')
        return 0
    texto = monta()
    bytes_ = texto.encode('cp1252')
    antes = open(DESTINO, 'rb').read() if os.path.exists(DESTINO) else ''
    n_warp = texto.count(u'\twarp\t')
    n_mob = texto.count(u'\tmonster\t')
    # a quantidade e o campo logo depois do --ja--; contar pelo fim da
    # linha quebrou quando o rotulo de evento entrou nela
    n_mons = sum(int(m.group(1)) for m in
                 re.finditer(r'--ja--	\d+,(\d+),', texto))
    print '%d portais, %d linhas de spawn, %d monstros' % (n_warp, n_mob, n_mons)
    if '--conferir' in argv:
        print 'igual ao que esta em disco' if bytes_ == antes else \
              'DIFERENTE do que esta em disco'
        return 0
    fh = open(DESTINO, 'wb')
    fh.write(bytes_)
    fh.close()
    print 'gravado %s (%d bytes)' % (DESTINO, len(bytes_))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
