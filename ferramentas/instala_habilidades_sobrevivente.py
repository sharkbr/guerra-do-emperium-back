# -*- coding: ascii -*-
"""Poe as tres habilidades de Sobrevivente no CLIENTE - nome, descricao e icone.

O SERVIDOR ja sabe delas sozinho: `db/guerra/skill_db.yml` (o cadastro) e
`src/custom/habilidades_sobrevivente.hpp` (o efeito). Esta ferramenta cuida da
OUTRA METADE, a que mora em `C:\\GuerraDoEmperium\\cliente\\` e nao esta em git
- e que, por isso, so chega ao jogador por patch (CLAUDE.md par. 4.18).

    python instala_habilidades_sobrevivente.py             # instala
    python instala_habilidades_sobrevivente.py --conferir  # so mede; sai 1 se faltar

POR QUE ESTA FERRAMENTA PRECISA EXISTIR
=======================================
Nao e "um script que eu rodei uma vez". O `traduz_ptbr.py skills` reescreve
estes mesmos dois arquivos a partir do bRO - troca o `SkillName` de cada bloco
do `skillinfolist` e o bloco INTEIRO do `skilldescript`. Os tres ids que usamos
sao habilidades que o bRO conhece pelo nome antigo (Biotecnologia, Criar
Criatura, Cultivo), entao a proxima rodada daquela ferramenta DESFAZ as tres, em
silencio: o efeito continua valendo no servidor e a janela volta a chamar a
habilidade de "Cultivo". E a mesma armadilha do `nomes_pt_item_db.py`, que
desfaz o nome em portugues de item que ganhou bloco proprio depois.

Entao: rodar isto DEPOIS de qualquer `traduz_ptbr.py skills`, e antes de montar
patch que leve o `skillinfoz`.

AS TRES METADES QUE ELA ESCREVE
===============================
1. `skillinfolist.lub` - o `SkillName` (o que a janela mostra) e o primeiro
   campo do bloco, que e o nome AEGIS com que o cliente vai buscar a textura do
   icone.
2. `skilldescript.lub` - a descricao da janela.
3. `data\\texture\\<ui>\\item\\<aegis>.bmp` - o icone, copiado do GRF a partir da
   habilidade que o dono escolheu para cada uma (2026-09-22):
   Pragmatico o de Cair das Petalas, Astuto o de Telecinesia, Caotico o de
   Frenesi.

   O icone e gravado com DOIS nomes, o novo e o antigo (`am_cultivation.bmp` e
   `gue_sobrevivente_caotico.bmp`). O cliente resolve a textura pelo nome AEGIS
   do lua; como nao ha prova de que ele nunca use o nome que o servidor manda no
   pacote da lista de habilidades, os dois nomes apontam para o mesmo desenho e
   os dois caminhos dao certo. Custa 1,6 KB.

TODO ACENTO AQUI E ESCAPE DE BYTE (\\xe1, \\xf3), nunca letra acentuada. O
arquivo do cliente e cp1252, e a ferramenta de edicao do assistente grava UTF-8:
com letra acentuada no fonte, o byte que chega ao `.lub` e o do UTF-8 e o acento
se perde para sempre (CLAUDE.md par. 4.1, e a entrada do U+FFFD na secao 5).
Escape de byte nao depende da codificacao deste arquivo - foi o round-trip
abaixo que pegou esse erro na primeira rodada.

Roda em Python 2.7 (`C:\\Python27\\python.exe`), como o resto de `ferramentas/`.
"""
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grf import Grf

CLI = r'C:\GuerraDoEmperium\cliente'
SKILLZ = os.path.join(CLI, r'data\luafiles514\lua files\skillinfoz')
GRF = os.path.join(CLI, 'data.grf')

# (SKID do cliente, nome AEGIS novo, nome na tela, linhas da descricao,
#  nome AEGIS da habilidade de onde sai o icone)
#
# O SKID e a chave que liga os dois lados: e o mesmo numero do `Id:` do
# `db/guerra/skill_db.yml` (239, 240, 241).
TRES = [
    ('AM_BIOTECHNOLOGY', 'GUE_SOBREVIVENTE_PRAGMATICO',
     'Sobrevivente Pragm\xe1tico',
     ['Tipo: ^777777Passiva^000000',
      'Efeito: ^777777AGI +20.^000000',
      '^777777Capacidade de peso +2000.^000000'],
     'mo_dodge'),
    ('AM_CREATECREATURE', 'GUE_SOBREVIVENTE_ASTUTO',
     'Sobrevivente Astuto',
     ['Tipo: ^777777Passiva^000000',
      'Efeito: ^777777INT +20.^000000',
      '^777777Ataque M\xe1gico +100.^000000'],
     'wl_telekinesis_intense'),
    ('AM_CULTIVATION', 'GUE_SOBREVIVENTE_CAOTICO',
     'Sobrevivente Ca\xf3tico',
     ['Tipo: ^777777Passiva^000000',
      'Efeito: ^777777Todos os atributos +10.^000000',
      '^777777Ataque +100.^000000'],
     'lk_berserk'),
]


def bloco_info(skid, aegis, nome):
    """O bloco do skillinfolist. MaxLv 1 e IsPassive, que e o que elas sao."""
    return ('\t[SKID.%s] = {\n'
            '\t\t"%s",\n'
            '\t\tSkillName = "%s",\n'
            '\t\tMaxLv = 1,\n'
            '\t\tSpAmount = { 0 },\n'
            '\t\tbSeperateLv = false,\n'
            '\t\tIsPassive = true,\n'
            '\t\tAttackRange = { 1 }\n'
            '\t},\n') % (skid, aegis, nome)


def bloco_desc(skid, nome, linhas):
    corpo = ',\n'.join('\t\t"%s"' % l for l in [nome] + linhas)
    return '\t[SKID.%s] = {\n%s\n\t},\n' % (skid, corpo)


def troca_bloco(texto, skid, novo):
    """Troca o bloco `[SKID.<skid>] = { ... }` inteiro.

    O fim do bloco e a linha com tabulacao + '},' - o criterio que o proprio
    arquivo usa. Casar por '}' solto pegaria o fecho de um `SpAmount` interno.

    Como a CHAVE nao muda (continua `SKID.AM_CULTIVATION`), rodar duas vezes
    nao duplica nada: a segunda rodada acha o bloco que a primeira escreveu e
    o reescreve igual. E se o `traduz_ptbr.py` tiver desfeito, acha o bloco do
    bRO e o substitui de novo.
    """
    marca = '\t[SKID.%s] = {' % skid
    i = texto.find(marca)
    if i < 0:
        raise Exception('nao achei o bloco de %s' % skid)
    fim = texto.find('\n\t},\n', i)
    if fim < 0:
        raise Exception('nao achei o fim do bloco de %s' % skid)
    return texto[:i] + novo + texto[fim + len('\n\t},\n'):]


def pasta_e_fonte_do_icone(g):
    """Acha a pasta de icone do cliente pelo GRF.

    O caminho tem um trecho em coreano (`\\uc720\\uc800\\uc778\\ud130\\ud398\\uc774\\uc2a4`, "interface do
    usuario") que nao sobrevive a argv do console - por isso ele e lido do
    proprio GRF em vez de escrito aqui.
    """
    for k in g.entries:
        if k.endswith('\\item\\mo_dodge.bmp'):
            return os.path.join(CLI, os.path.dirname(g.entries[k][5])), k
    raise Exception('nao achei a pasta de icone dentro do GRF')


def confere():
    """Mede as tres metades sem escrever nada. Devolve a lista de faltas."""
    faltas = []
    info = open(os.path.join(SKILLZ, 'skillinfolist.lub'), 'rb').read()
    desc = open(os.path.join(SKILLZ, 'skilldescript.lub'), 'rb').read()
    pasta, _fonte = pasta_e_fonte_do_icone(Grf(GRF))

    for skid, aegis, nome, linhas, _icone in TRES:
        if bloco_info(skid, aegis, nome) not in info:
            faltas.append('%s: fora do skillinfolist.lub' % aegis)
        if bloco_desc(skid, nome, linhas) not in desc:
            faltas.append('%s: fora do skilldescript.lub' % aegis)
        for alvo in (aegis.lower() + '.bmp', skid.lower() + '.bmp'):
            if not os.path.isfile(os.path.join(pasta, alvo)):
                faltas.append('%s: falta o icone %s' % (aegis, alvo))
    return faltas


def instala():
    carimbo = time.strftime('%Y%m%d-%H%M%S')
    alvo_info = os.path.join(SKILLZ, 'skillinfolist.lub')
    alvo_desc = os.path.join(SKILLZ, 'skilldescript.lub')

    print 'backup:'
    for caminho in (alvo_info, alvo_desc):
        destino = '%s.BACKUP-%s' % (caminho, carimbo)
        shutil.copy2(caminho, destino)
        print ' ', os.path.basename(destino)

    info = open(alvo_info, 'rb').read()
    desc = open(alvo_desc, 'rb').read()
    for skid, aegis, nome, linhas, _icone in TRES:
        info = troca_bloco(info, skid, bloco_info(skid, aegis, nome))
        desc = troca_bloco(desc, skid, bloco_desc(skid, nome, linhas))
    open(alvo_info, 'wb').write(info)
    open(alvo_desc, 'wb').write(desc)

    # Round-trip: reler do DISCO e conferir. O \xc3 e o primeiro byte de todo
    # acento em UTF-8; se ele aparecer colado no nome, o arquivo saiu na
    # codificacao errada e o acento ja se perdeu.
    info2 = open(alvo_info, 'rb').read()
    desc2 = open(alvo_desc, 'rb').read()
    for skid, aegis, nome, linhas, _icone in TRES:
        assert bloco_info(skid, aegis, nome) in info2, 'infolist: %s' % skid
        assert bloco_desc(skid, nome, linhas) in desc2, 'descript: %s' % skid
    assert 'Pragm\xe1tico' in info2 and 'Pragm\xc3' not in info2, 'acento errado'
    assert 'Ca\xf3tico' in info2 and 'Ca\xc3' not in info2, 'acento errado'
    assert 'M\xe1gico' in desc2 and 'M\xc3' not in desc2, 'acento errado'
    print 'lua: os seis blocos conferidos em cp1252'

    g = Grf(GRF)
    pasta, fonte = pasta_e_fonte_do_icone(g)
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    for skid, aegis, nome, _linhas, icone in TRES:
        dados = g.read(fonte.replace('mo_dodge.bmp', icone + '.bmp'))
        for alvo in (aegis.lower() + '.bmp', skid.lower() + '.bmp'):
            open(os.path.join(pasta, alvo), 'wb').write(dados)
        print '  %-28s <- %-24s %d bytes, dois nomes' % (aegis, icone, len(dados))

    faltas = confere()
    if faltas:
        print 'FALHOU:'
        for f in faltas:
            print '  -', f
        return 1
    print 'as tres metades das tres habilidades estao no cliente.'
    print 'O cliente so le isto na INICIALIZACAO: fechar e reabrir.'
    return 0


def main():
    if '--conferir' in sys.argv:
        faltas = confere()
        if faltas:
            print 'FALTA:'
            for f in faltas:
                print '  -', f
            return 1
        print 'as tres habilidades estao instaladas no cliente.'
        return 0
    return instala()


if __name__ == '__main__':
    sys.exit(main())
