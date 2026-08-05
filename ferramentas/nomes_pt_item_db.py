# -*- coding: utf-8 -*-
u"""Poe o `Name` do item_db do servidor igual ao nome que o CLIENTE desenha.

Python 2.7, como o resto de ferramentas/.

O problema que ele resolve so aparece dentro de dialogo de NPC: o nome de item
que o jogador ve na bolsa **nao vem do servidor**, vem do `itemInfo.lua` do
cliente -- e aquele ja esta em portugues desde a rodada de traducao. Mas
`getitemname()` e `getequipname()`, que os scripts usam para escrever a fala,
leem o `Name` do `item_db` do rAthena, que esta em ingles.

Resultado: o Mestre do Refino dizia "+5 Weapon Refine Ticket" para um item que
a bolsa do jogador chama de "Pergaminho de Arma +5". Mesmo item, dois nomes, e
o unico que o jogador consegue procurar e o da bolsa.

**A fonte e o `itemInfo.lua` do nosso cliente, e nao o `iteminfo_new.lub` do
bRO.** Os dois quase sempre concordam -- o nosso foi montado importando o dele
--, mas quando discordarem quem esta certo e o do cliente, porque e ele que
esta na tela. Mesma regra do `npcidentity.lub` para view id de NPC e do
`accessoryid.lub` para visual: **manda o arquivo que o cliente le.**

Por isso o objetivo nao e "traduzir o item_db", e sim **sincronizar**: onde o
cliente esta em portugues o servidor fica em portugues, onde o cliente ficou em
ingles o servidor fica com o ingles DELE. Consistencia primeiro; o portugues
vem junto porque o cliente ja esta em portugues.

Uso:
    python nomes_pt_item_db.py --relatar   # so mede, nao grava
    python nomes_pt_item_db.py             # grava
    python nomes_pt_item_db.py --reverter  # devolve os .INGLES

=========================================================================
POR QUE ELE REESCREVE O ARQUIVO DO rAthena EM VEZ DE SOBREPOR POR IMPORT
=========================================================================

A primeira versao gerava um `db/guerra/item_db_nomes.yml` com 16442 entradas
de `Id` + `Name`, encadeado por import -- que e o que a CONVENCAO DE
CUSTOMIZACAO pede, e que o rAthena aceita: `AegisName` e `Name` so sao
exigidos quando o item e novo (`itemdb.cpp:57`).

**Aquilo zerava o preco de venda de 7126 itens, em silencio.** A causa esta em
`itemdb.cpp:239`:

    hasPriceValue[item->nameid] = { has_buy, has_sell };

Essa linha roda a CADA parse do mesmo Id, e guarda apenas se aquele bloco
declarou `Buy`/`Sell`. Um bloco so com `Id` + `Name` grava `{false, false}` por
cima do `{true, false}` que o `db/re/` tinha. Depois, no `loadingFinished`
(`itemdb.cpp:1185`):

    if (!has_buy && has_sell)  value_buy  = value_sell * 2;
    else if (has_buy && !has_sell)  value_sell = value_buy / 2;

Nenhum dos dois roda, e a derivacao se perde. A Pocao Vermelha declara so
`Buy: 10`; com o override o `value_sell` dela ficava em **0** em vez de 5. Idem
Pocao Branca (600 -> 0) e Pocao Azul (2500 -> 0): todo drop que valia dinheiro
passava a nao valer nada.

E foi **silencioso**: dos 7126, um unico item imprimiu aviso na subida (o
`Gray_Shard`, e por outro motivo -- ele caiu na trava de exploit de zeny). Os
outros 7125 nao disseram nada.

Trocar `Name` no lugar nao tem esse problema porque **nao acrescenta parse
nenhum**: o bloco continua sendo um so, com os mesmos campos de preco. So a
string muda.

O conflito com a CONVENCAO e o mesmo que a frente de traducao ja resolveu (ver
`traduz_npcs.py`): texto traduzido nao tem como morar em pasta propria, entao
**a fonte fica separada do resultado**. Aqui a fonte e o `itemInfo.lua` do
cliente mais esta ferramenta; o arquivo do rAthena e o resultado, e tem um
`.INGLES` ao lado. `--reverter` desfaz.

E, pela mesma licao que custou 595 pares do `servico.cat`: **a leitura do nome
antigo sai do `.INGLES` quando ele existe.** Sem isso, rodar duas vezes
compararia contra o proprio resultado e o registro do que o upstream dizia se
perderia.

=========================================================================
O QUE NAO ENTRA
=========================================================================

- **nome que sobrou em coreano.** O `itemInfo.lua` tem dois encodings no mesmo
  arquivo de proposito (ver `completa_iteminfo.py`): o texto do bRO em cp1252 e
  o que nunca foi traduzido em CP949. Lido como cp1252, o coreano vira coisa
  como "¹« ±â 19 ...". Sao rejeitados pelo conjunto de caracteres permitidos --
  para esses o `item_db` fica com o ingles do rAthena, que e melhor que
  mojibake. Sao 4587, e o jogador **tambem ve coreano na bolsa** deles: e um
  buraco do cliente, nao deste script.
- **item que o `item_db` do rAthena nao tem** (1554) -- nao ha linha para
  trocar.
- **os nossos itens** (`db/guerra/item_db.yml`): ja nascem em portugues e com
  nome escolhido por nos.
- **nome com mais de 50 caracteres** (`ITEM_NAME_LENGTH`, `src/common/mmo.hpp`),
  que o rAthena corta com aviso. Sao 40, e todos estao em ingles no cliente
  tambem -- nao se perde portugues nenhum.
- **nome igual ao que ja esta la.**

Riscos conferidos: nome duplicado nao da erro, o `nameToItemDataMap` so
sobrescreve (`itemdb.cpp:104-131`); o que muda e que `@item <nome>` passa a
achar pelo nome em portugues. E nenhum script do `npc/` compara
`getitemname()` com texto -- as unicas comparacoes nos 623 usos sao contra
`"null"` e `""`, que e o que a funcao devolve para id inexistente.
"""

import os
import re
import shutil
import sys


CLIENTE = os.path.join(r'C:\GuerraDoEmperium\cliente',
                       'SystemEN', 'LuaFiles514', 'itemInfo.lua')
RATHENA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       os.pardir, 'rathena')
FONTES = ['db/re/item_db_usable.yml',
          'db/re/item_db_equip.yml',
          'db/re/item_db_etc.yml']
NOSSO = 'db/guerra/item_db.yml'

MAX = 50        # ITEM_NAME_LENGTH

# Os bytes altos que um nome em portugues pode ter. Qualquer outro denuncia
# CP949 lido como cp1252 -- e a rejeicao e a coisa certa, porque para aquele
# item o ingles do rAthena ainda serve.
ACENTOS = set(u'áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑºª')

RE_ENTRADA = re.compile(r'(?m)^\s*\[(\d+)\]\s*=\s*\{')
RE_NOME_LUA = re.compile(r'(?m)^\s*identifiedDisplayName\s*=\s*"([^"]*)"')
RE_ID_YML = re.compile(r'^  - Id: (\d+)\s*$')
RE_NOME_YML = re.compile(r'^    Name: (.*)$')


def latino(texto):
    u"""O nome e escrivel em portugues, ou e coreano lido errado?"""
    return all(c < u'\x80' or c in ACENTOS for c in texto)


def le_cliente(caminho):
    u"""id -> nome exibido, do itemInfo.lua do cliente."""
    fh = open(caminho, 'rb')
    dados = fh.read()
    fh.close()
    saida = {}
    pos = [(m.start(), int(m.group(1))) for m in RE_ENTRADA.finditer(dados)]
    for i, (ini, iid) in enumerate(pos):
        fim = pos[i + 1][0] if i + 1 < len(pos) else len(dados)
        # O `unidentifiedDisplayName` vem antes no bloco e NAO casa: o
        # ancoramento em inicio de linha impede o `un` de ser pulado.
        m = RE_NOME_LUA.search(dados, ini, fim)
        if m:
            saida[iid] = m.group(1)
    return saida


def ids_de(caminho):
    fh = open(caminho, 'rb')
    d = fh.read()
    fh.close()
    return set(int(x) for x in re.findall(r'(?m)^  - Id: (\d+)\s*$', d))


def escalar(nome):
    u"""O nome como escalar YAML. Sempre entre aspas.

    Nome de item tem `+`, `[`, `]`, `:` e as vezes espaco na ponta, e cada um
    deles muda o sentido de um escalar solto. O proprio db do rAthena ja poe
    aspas em 631 nomes pelo mesmo motivo.
    """
    return u'"%s"' % nome.replace(u'\\', u'\\\\').replace(u'"', u'\\"')


def desescalar(valor):
    u"""O caminho de volta: o valor cru do YAML -> o texto do nome.

    Existe so para a comparacao "ja esta igual" nao gerar troca a toa: o db do
    rAthena poe aspas em 631 nomes e deixa 28725 sem, e comparar linha com
    linha acusaria diferenca em todos os que so mudam de aspa.
    """
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == u'"' and valor[-1] == u'"':
        valor = valor[1:-1].replace(u'\\"', u'"').replace(u'\\\\', u'\\')
    return valor


def confere(antes, depois, rel):
    u"""Trava estrutural, na mesma linha da do traduz_npcs.py."""
    if antes.count('\n') != depois.count('\n'):
        raise Exception('%s mudou de numero de linhas' % rel)
    for regex, oque in ((RE_ID_YML, 'Id'), (RE_NOME_YML, 'Name')):
        a = len([1 for l in antes.split('\n') if regex.match(l)])
        b = len([1 for l in depois.split('\n') if regex.match(l)])
        if a != b:
            raise Exception('%s mudou de numero de linhas `%s`: %d -> %d'
                            % (rel, oque, a, b))


def reverter(raiz):
    n = 0
    for rel in FONTES:
        p = os.path.join(raiz, rel.replace('/', os.sep))
        bak = p + '.INGLES'
        if os.path.exists(bak):
            shutil.copy2(bak, p)
            os.remove(bak)
            print '  revertido %s' % rel
            n += 1
    print '%d arquivos revertidos' % n
    return 0


def main():
    raiz = os.path.normpath(RATHENA)
    if '--reverter' in sys.argv:
        return reverter(raiz)
    relatar = '--relatar' in sys.argv

    cliente = le_cliente(CLIENTE)
    print 'cliente : %d itens com nome' % len(cliente)
    nossos = ids_de(os.path.join(raiz, NOSSO.replace('/', os.sep)))
    print 'nossos  : %d itens (nao entram)' % len(nossos)

    conta = {'nossos': 0, 'igual': 0, 'coreano': 0, 'vazio': 0,
             'comprido': 0, 'sem_no_cliente': 0}
    trocados = amostra = 0
    for rel in FONTES:
        p = os.path.join(raiz, rel.replace('/', os.sep))
        bak = p + '.INGLES'
        # A FONTE E SEMPRE O INGLES -- ver o cabecalho.
        fonte = bak if os.path.exists(bak) else p
        fh = open(fonte, 'rb')
        dados = fh.read()
        fh.close()

        linhas = dados.split('\n')
        iid = None
        mudou = 0
        for i, linha in enumerate(linhas):
            m = RE_ID_YML.match(linha)
            if m:
                iid = int(m.group(1))
                continue
            if iid is None:
                continue
            m = RE_NOME_YML.match(linha)
            if not m:
                continue
            atual, alvo = m.group(1), iid
            iid = None

            if alvo not in cliente:
                conta['sem_no_cliente'] += 1
                continue
            if alvo in nossos:
                conta['nossos'] += 1
                continue
            nome = cliente[alvo].decode('cp1252', 'replace').strip()
            if not nome:
                conta['vazio'] += 1
                continue
            if not latino(nome):
                conta['coreano'] += 1
                continue
            if len(nome) > MAX:
                conta['comprido'] += 1
                continue
            if nome == desescalar(atual.decode('cp1252', 'replace')):
                conta['igual'] += 1
                continue
            novo = u'    Name: ' + escalar(nome)
            if amostra < 8:
                print '   %-8d %-36s -> %s' % (
                    alvo, atual[:36], nome.encode('utf-8'))
                amostra += 1
            linhas[i] = novo.encode('cp1252')
            mudou += 1

        trocados += mudou
        if relatar:
            print '%-28s %6d trocas' % (rel, mudou)
            continue

        novo_texto = '\n'.join(linhas)
        confere(dados, novo_texto, rel)
        if novo_texto == dados:
            print '%-28s sem mudanca' % rel
            continue
        if not os.path.exists(bak):
            shutil.copy2(p, bak)
        fh = open(p, 'wb')
        fh.write(novo_texto)
        fh.close()
        print '%-28s %6d trocas gravadas' % (rel, mudou)

    print
    for k in sorted(conta):
        print '  fora por %-15s %6d' % (k, conta[k])
    print '  TROCADOS                %6d' % trocados
    if relatar:
        print
        print '--relatar: nada gravado'
    else:
        print
        print 'pega com @reloaditemdb. O cliente NAO precisa reabrir -'
        print 'o nome que ele desenha ja era este.'
    return 0


if __name__ == '__main__':
    sys.exit(main())
