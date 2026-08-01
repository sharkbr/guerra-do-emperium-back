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
#   nome      o que aparece no inventario. SEM ACENTO - o cliente roda em
#             langtype 0 (Coreia) e ainda nao testamos como ele desenha byte
#             acentuado. Ver PENDENCIAS.md, secao "Acentuacao no dialogo".
#   descricao uma linha da caixa de descricao por elemento. "____..." e a regua
#             separadora que o proprio arquivo usa, e `^RRGGBB` troca a cor.
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
        'nome': 'Maca da Inocencia',
        'arte_de': 512,                     # a Maca comum
        'descricao': [
            'Ao adentrar em Valhalla caida o viajante recebe uma maca',
            'que simboliza a inocencia na renovacao.',
            'Optar por atalhos pode fazer com que a maca desapareca.',
            '_______________________',
            'Pode ser concedida ao Deus da Guerra no level maximo em',
            'troca de melhorias.',
            '_______________________',
            '^0000CCType:^000000 Etc',
            '^0000CCWeight:^000000 1',
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
    # Rede de seguranca contra o acento que escapa: um byte alto aqui nao daria
    # erro nenhum, so um nome torto no inventario e a duvida de sempre sobre
    # encoding num arquivo de 22 MB.
    for texto in [item['nome']] + list(item['descricao']):
        try:
            texto.encode('ascii')
        except UnicodeDecodeError:
            raise Erro('o item %d tem byte nao-ASCII em %r; textos de jogo '
                       'vao sem acento' % (item['id'], texto))

    linhas = ['\r\n\t[%d] = {' % item['id']]
    a = linhas.append
    a('\t\tunidentifiedDisplayName = "%s",' % item['nome'])
    a('\t\tunidentifiedResourceName = "%s",' % arte)
    a('\t\tunidentifiedDescriptionName = { "" },')
    a('\t\tidentifiedDisplayName = "%s",' % item['nome'])
    a('\t\tidentifiedResourceName = "%s",' % arte)
    a('\t\tidentifiedDescriptionName = {')
    for i, linha in enumerate(item['descricao']):
        virgula = '' if i == len(item['descricao']) - 1 else ','
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
        novo = monta(item, recurso(dados, item['arte_de']))
        lim = bloco(dados, item['id'])
        if lim is None:
            pos, ant, seg = onde_entra(dados, item['id'])
            dados = dados[:pos] + novo + dados[pos:]
            print '  [novo   ] %d %s  (+%d bytes, entre %s e %s)' % (
                item['id'], item['nome'], len(novo), ant, seg)
            mudou = True
        elif dados[lim[0]:lim[1]] == novo:
            print '  [ja tem ] %d %s  identica, nada a fazer' % (
                item['id'], item['nome'])
        else:
            velho = lim[1] - lim[0]
            dados = dados[:lim[0]] + novo + dados[lim[1]:]
            print '  [troca  ] %d %s  (%d -> %d bytes)' % (
                item['id'], item['nome'], velho, len(novo))
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
