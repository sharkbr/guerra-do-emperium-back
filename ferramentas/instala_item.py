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
#   arte_de   ID de outro item de quem copiamos o `resourceName`, BYTE A BYTE.
#             O `resourceName` e so um nome de recurso: nada impede dois IDs
#             apontarem para o mesmo desenho, e assim nao precisamos criar
#             icone, imagem de collection nem sprite de chao. Quando um item
#             nosso for merecer arte exclusiva, ai entra o instala_visual.py.
#             Copiar em tempo de execucao, e nao colar os bytes aqui, e o que
#             garante que eles cheguem intactos.

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
        # A caixa de 20 do bRO (Guyak_Pudding_20_Box). O item dela foi
        # reprovado por trazer 20 e por ter nome COREANO no itemInfo.lua -
        # mas a ARTE esta completa, e e so ela que aproveitamos.
        'arte_de': 22668,
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
    m = re.search(r'identifiedResourceName = "([^"]*)"', dados[lim[0]:lim[1]])
    if not m:
        raise Erro('item %d nao tem identifiedResourceName' % iid)
    return m.group(1)


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
    a('\t\tslotCount = 0,')
    a('\t\tClassNum = 0,')
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
        novo = monta(item, recurso(dados, item['arte_de']))
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
