# -*- coding: utf-8 -*-
u"""Poe as missoes da Ordem dos Exploradores na tabela de missoes do CLIENTE.

    python monta_missoes_da_ordem.py              # aplica (faz backup antes)
    python monta_missoes_da_ordem.py --verificar  # so relata, nao grava

O PROBLEMA QUE ISTO RESOLVE, e ele nao e cosmetico:

Quando o servidor manda uma quest que o cliente nao conhece, o cliente NAO
mostra a missao sem titulo - ele ESTOURA. O `GetOngoingQuestInfoByID` do
`data\\luafiles514\\lua files\\datainfo\\questinfo_f.lub` faz, na linha 4:

    QuestInfoList[id].Title

e sem entrada para o id isso vira
`attempt to index field '?' (a nil value)`. O cliente abre uma caixa de erro
POR MISSAO e por atualizacao da janela - pegar as sete Missoes A de uma vez
rende dezenas de caixas seguidas e derruba a conexao. Foi o que aconteceu em
2026-08-08, no primeiro teste em jogo das placas.

Ou seja: **a janela de missoes tem metade da configuracao no cliente**, como o
Logue e Ganhe (CLAUDE.md secao 4.9). O servidor manda so o id e o contador; o
titulo, a descricao e o resumo saem daqui. Este script e o irmao do
`monta_logue_e_ganhe.py` - existe pelo mesmo motivo e se usa do mesmo jeito.

POR QUE NAO EDITAR O ARQUIVO A MAO: `System\\OngoingQuestInfoList_*.lub` e
GERADO pelo `traduz_ptbr.py questinfo`, que o reconstroi a partir do arquivo
coreano de 2021 congelado no `.COREANO` ao lado. Entrada posta a mao some na
proxima rodada da traducao, sem aviso.

    ORDEM CERTA:  traduz_ptbr.py questinfo   e DEPOIS   este script.

QUAIS MISSOES: as ids saem de `rathena/db/guerra/quest_db.yml` - la e que se
diz quais existem. O TEXTO em portugues mora aqui, na tabela `TEXTO` abaixo.
Quest que exista no YAML e nao tenha texto aqui e denunciada com aviso e o
script nao grava nada: uma quest sem entrada no cliente e exatamente o bug
que este arquivo existe para impedir.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEST_DB = os.path.join(RAIZ, 'rathena', 'db', 'guerra', 'quest_db.yml')
SISTEMA = r'C:\GuerraDoEmperium\cliente\System'

# Os dois que o `traduz_ptbr.py questinfo` grava, e que definem o global
# `QuestInfoList`. Os outros dois do System (OngoingQuestInfoList.lub e
# _sak.lub) sao os do instalador, em bytecode, e nao sao tocados.
ALVOS = ['OngoingQuestInfoList_True.lub', 'OngoingQuestInfoList_Sakray.lub']

# O compilador Lua 5.1 do ROenglishRE - a unica trava que prova a sintaxe de
# verdade. Ver a secao 5 do CLAUDE.md.
LUAC = r'C:\Users\User\Downloads\ROenglishRE\Tools\luac.exe'

# A faixa que e nossa. Serve de rede: se um dia o rAthena usar um id daqui, o
# script avisa em vez de sobrescrever calado.
FAIXA = (30000, 30049)


class Erro(Exception):
    pass


# ---------------------------------------------------------------------------
# O TEXTO. Uma entrada por quest, e o titulo e o que o jogador le na janela.
#
# O padrao de nome segue o do proprio bRO, que este cliente ja tem: a missao
# de cacada leva o nome da instancia, e a de espera vem com "[Espera]" na
# frente (ver a quest 293444 do arquivo, "[Espera] Shibasays").
#
# `Description` e uma LISTA - e assim que o cliente a le, uma linha por
# elemento. `Summary` e a linha curta da lista lateral.
# ---------------------------------------------------------------------------
#
# O TEXTO VAI COM ACENTO, e o arquivo de destino e gravado em cp1252 - o
# mesmo do resto dele (o `.lub` gerado pelo traduz_ptbr.py ja tem ~20 mil
# bytes acentuados). Este .py e UTF-8, como todo fonte nosso; a conversao
# acontece num lugar so, no `.encode('cp1252')` do `monta()`.
TEXTO = {
    # ----- Missoes A -------------------------------------------------------
    30000: (u'Batalha dos Orcs',
            u'A Ordem dos Exploradores quer a cabeça do chefe da Batalha '
            u'dos Orcs. Volte à placa das Missões A quando terminar.',
            u'Derrote o chefe da Batalha dos Orcs.'),
    30002: (u'Memórias de Sarah',
            u'A Ordem dos Exploradores quer a cabeça do chefe das Memórias '
            u'de Sarah. Volte à placa das Missões A quando terminar.',
            u'Derrote o chefe das Memórias de Sarah.'),
    30003: (u'Palácio das Mágoas',
            u'A Ordem dos Exploradores quer a cabeça do chefe do Palácio '
            u'das Mágoas. Volte à placa das Missões A quando terminar.',
            u'Derrote o chefe do Palácio das Mágoas.'),
    30004: (u'Hospital Abandonado',
            u'A Ordem dos Exploradores quer a cabeça do chefe do Hospital '
            u'Abandonado. Volte à placa das Missões A quando terminar.',
            u'Derrote o chefe do Hospital Abandonado.'),
    30005: (u'Aos Pés do Rei',
            u'A Ordem dos Exploradores quer a cabeça do chefe de Aos Pés do '
            u'Rei. Volte à placa das Missões A quando terminar.',
            u'Derrote o chefe de Aos Pés do Rei.'),
    30006: (u'Fábrica do Terror',
            u'A Ordem dos Exploradores quer a cabeça do chefe da Fábrica do '
            u'Terror. Volte à placa das Missões A quando terminar.',
            u'Derrote o chefe da Fábrica do Terror.'),
    30007: (u'Sonho Sombrio',
            u'A Ordem dos Exploradores quer a cabeça do Réquiem de Marfim, '
            u'no Sonho Sombrio. Volte à placa das Missões A quando terminar.',
            u'Derrote o Réquiem de Marfim.'),
    30008: (u'Covil de Vermes',
            u'A Ordem dos Exploradores quer quatro Vermes Sombrios com '
            u'Rosto, no Covil de Vermes. Volte à placa das Missões A quando '
            u'terminar.',
            u'Derrote 4 vermes no Covil de Vermes.'),
    # ----- Missoes B -------------------------------------------------------
    30020: (u'Lago de Bakonawa',
            u'A Ordem dos Exploradores quer o Tesouro de Bakonawa, no Lago '
            u'de Bakonawa. Volte à placa das Missões B quando terminar.',
            u'Derrote o Tesouro de Bakonawa.'),
    30021: (u'Sarah vs Fenrir',
            u'A Ordem dos Exploradores quer seis Gigantes Ancestrais, em '
            u'Sarah vs Fenrir. Volte à placa das Missões B quando terminar.',
            u'Derrote 6 Gigantes Ancestrais.'),
    30022: (u'Torre do Demônio',
            u'A Ordem dos Exploradores quer nove Sombras Malignas na Torre '
            u'do Demônio - três de cada tipo. Volte à placa das Missões B '
            u'quando terminar.',
            u'Derrote 3+3+3 Sombras na Torre do Demônio.'),
    # ----- Missoes C -------------------------------------------------------
    30030: (u'Vila dos Porings',
            u'A Ordem dos Exploradores quer a cabeça do chefe da Vila dos '
            u'Porings. Volte à placa das Missões C quando terminar.',
            u'Derrote o chefe da Vila dos Porings.'),
    30031: (u'Caverna do Polvo',
            u'A Ordem dos Exploradores quer o Polvo Gigante, na Caverna do '
            u'Polvo. Volte à placa das Missões C quando terminar.',
            u'Derrote o Polvo Gigante.'),
    30032: (u'Quarto Crescente',
            u'A Ordem dos Exploradores quer o Espectro de Ktullanux, no '
            u'Quarto Crescente. Volte à placa das Missões C quando terminar.',
            u'Derrote o Espectro de Ktullanux.'),
    30033: (u'Maldição de Glastheim',
            u'A Ordem dos Exploradores quer a Origem da Maldição e o '
            u'Amdarais, na Maldição de Glastheim. Volte à placa das Missões '
            u'C quando terminar.',
            u'Derrote a Origem da Maldição e o Amdarais.'),
    # ----- As tres esperas -------------------------------------------------
    30040: (u'[Espera] Missões A',
            u'Você já prestou contas das Missões A hoje. O escrivão da Ordem '
            u'reabre a escrita às 6h da manhã.',
            u'Reabre às 6 da manhã.'),
    30041: (u'[Espera] Missões B',
            u'Você já prestou contas das Missões B hoje. O escrivão da Ordem '
            u'reabre a escrita às 6h da manhã.',
            u'Reabre às 6 da manhã.'),
    30042: (u'[Espera] Missões C',
            u'Você já prestou contas das Missões C hoje. O escrivão da Ordem '
            u'reabre a escrita às 6h da manhã.',
            u'Reabre às 6 da manhã.'),
}


def ids_do_servidor():
    u"""As ids DA NOSSA FAIXA que existem no db/guerra/quest_db.yml.

    So conta linha `- Id: N` que NAO esteja comentada - as duas missoes
    reservadas (Torneio de Magia e Sonho Sombrio) moram la comentadas, e
    entrada de cliente para quest que o servidor nao tem seria lixo.

    O que estiver FORA da faixa e ignorado de proposito, e nao e engano:
    aquele arquivo tambem carrega override de quest do rAthena (o 12059, o
    tempo de espera da Batalha dos Orcs). Quest do rAthena ja tem entrada no
    cliente - poor uma nossa por cima e que seria o erro.
    """
    achadas = []
    for linha in open(QUEST_DB, 'rb').read().split('\n'):
        m = re.match(r'\s*- Id: (\d+)\s*$', linha)
        if m:
            achadas.append(int(m.group(1)))
    nossas = [i for i in achadas if FAIXA[0] <= i <= FAIXA[1]]
    alheias = [i for i in achadas if i not in nossas]
    if alheias:
        print ('quest_db.yml traz %d override(s) de quest do rAthena, que '
               'este script ignora: %s'
               % (len(alheias), ', '.join(str(i) for i in sorted(alheias))))
    return sorted(nossas)


def bloco(ident):
    u"""O trecho Lua de uma entrada, ja em CRLF."""
    titulo, descricao, resumo = TEXTO[ident]
    for pedaco in (titulo, descricao, resumo):
        if u'"' in pedaco or u'\\' in pedaco:
            raise Erro('texto da quest %d tem aspas ou contrabarra, que este '
                       'gerador nao escapa: %r' % (ident, pedaco))
    linhas = [
        u'\t[%d] = {' % ident,
        u'\t\tTitle = "%s",' % titulo,
        u'\t\tDescription = {',
        u'\t\t\t"%s"' % descricao,
        u'\t\t},',
        u'\t\tSummary = "%s",' % resumo,
        u'\t},',
    ]
    return u'\r\n'.join(linhas) + u'\r\n'


def confere_luac(dados, rotulo):
    if not os.path.exists(LUAC):
        print '    (luac.exe nao encontrado, sintaxe NAO conferida)'
        return
    fd, temporario = tempfile.mkstemp(suffix='.lua')
    try:
        os.write(fd, dados)
        os.close(fd)
        p = subprocess.Popen([LUAC, '-p', temporario],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        saida = p.communicate()[0]
        if p.returncode:
            raise Erro('%s nao compila, nada gravado: %s'
                       % (rotulo, saida.replace(temporario, rotulo).strip()))
        print '    luac -p: sintaxe conferida'
    finally:
        if os.path.exists(temporario):
            os.remove(temporario)


def monta(caminho, ids, verificar):
    rotulo = os.path.basename(caminho)
    print '  %s' % rotulo
    if not os.path.exists(caminho):
        raise Erro('nao achei %s' % caminho)
    dados = open(caminho, 'rb').read()

    # Tira as nossas entradas de antes, se houver - e o que faz o script ser
    # idempotente. O padrao pega o bloco inteiro, do `[id] = {` ate o `},`
    # que o fecha na mesma indentacao.
    tirados = 0
    for ident in range(FAIXA[0], FAIXA[1] + 1):
        padrao = re.compile(
            r'\t\[%d\] = \{\r\n(?:.*?\r\n)*?\t\},\r\n' % ident)
        dados, n = padrao.subn('', dados)
        tirados += n
    if tirados:
        print '    %d entrada(s) nossa(s) de antes, retiradas' % tirados

    novo = ''.join(bloco(i).encode('cp1252') for i in ids)

    # Entra ANTES do `}` que fecha a tabela, que e a ultima linha do arquivo.
    fim = dados.rstrip()
    if not fim.endswith('}'):
        raise Erro('%s nao termina com o `}` da tabela - formato inesperado'
                   % rotulo)
    corte = dados.rindex('}')
    saida = dados[:corte] + novo + dados[corte:]

    confere_luac(saida, rotulo)

    if verificar:
        print '    --verificar: nenhum byte gravado (+%d bytes seriam)' % (
            len(saida) - len(dados))
        return 0
    backup = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M'))
    if not os.path.exists(backup):
        shutil.copy2(caminho, backup)
    fh = open(caminho, 'wb')
    fh.write(saida)
    fh.close()
    print '    gravado: %d -> %d bytes  (backup: %s)' % (
        len(dados), len(saida), os.path.basename(backup))
    return 1


def principal():
    verificar = '--verificar' in sys.argv
    ids = ids_do_servidor()
    print 'quest_db.yml: %d missoes nossas (%s)' % (
        len(ids), ', '.join(str(i) for i in ids))

    faltando = [i for i in ids if i not in TEXTO]
    if faltando:
        raise Erro('estas missoes existem no servidor e NAO tem texto neste '
                   'script: %s\n'
                   'Sem entrada no cliente, cada uma abre uma caixa de erro '
                   'de Lua ao ser pega. Acrescente o texto na tabela TEXTO e '
                   'rode de novo.' % faltando)
    sobrando = [i for i in sorted(TEXTO) if i not in ids]
    if sobrando:
        print ('aviso: texto para missao que o servidor nao tem, sera ignorado'
               ': %s' % sobrando)

    print
    gravados = 0
    for nome in ALVOS:
        gravados += monta(os.path.join(SISTEMA, nome), ids, verificar)

    print
    if gravados:
        print 'O cliente le estes arquivos so na INICIALIZACAO - feche e'
        print 'reabra antes de testar.'


if __name__ == '__main__':
    try:
        principal()
    except Erro as e:
        print
        print 'ERRO: %s' % e
        sys.exit(1)
