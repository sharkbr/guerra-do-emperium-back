# -*- coding: utf-8 -*-
u"""Traduz o NOME EXIBIDO dos 30 NPCs de Brasilis, e as referencias a eles.

    python renomeia_npcs_brasilis.py             # aplica
    python renomeia_npcs_brasilis.py --conferir  # so mede; sai 1 se faltar

O `traduz_npcs.py` NAO alcanca isto, e nao e descuido dele: o nome do NPC
mora na LINHA DE DECLARACAO, fora de aspas, e o catalogo so troca literal.
Aqui isso deixou de ser detalhe - o dialogo traduzido chama as pessoas de
**Paulao**, **Jurema** e **Carmen**, que sao os nomes do bRO. Deixar o nome
flutuante em Cherto/Marta/Karmen mandaria o jogador procurar alguem que nao
existe na tela.

A FONTE DOS NOMES e o `navi_npc_br.lub` do GRF do Ragnarok Brazil, lido por
mapa e coordenada - nao invencao nossa (`CLAUDE.md` 4.3 e 4.12). Foi de la
que vieram tambem os tres nomes que ninguem adivinharia: o fantasma do museu
e a **Loira do Banheiro**, o Recluse e o **Ermitao**, e a Lucia aparece como
**Biologa Marinha**.

POR QUE ISTO E UMA FERRAMENTA E NAO UM `sed` DE UMA VEZ SO: o `.INGLES` ao
lado de cada arquivo e o ingles cru, e e dele que o `--extrair` le. Quem
restaurar o vendor e reaplicar o catalogo recupera o DIALOGO e **perde os
nomes** - sem erro nenhum, com o dialogo mandando procurar o Paulao e o NPC
de novo chamado Cherto. Rodar isto depois de todo `--aplicar brasilis`
fecha esse buraco, e o `--conferir` prova que esta fechado.

A troca e por SUBSTRING, e cada chave foi escolhida para pegar a declaracao
E as referencias de uma vez:

  - "Puppy#"    pega o base, os 12 `duplicate` e o `donpcevent "Puppy#"+...`
  - "Ghost#bra" pega tambem o "Ghost#bra_end"
  - "Pipe#bra"  pega tambem o "Pipe#brafild"

Linha de comentario do vendor fica intocada, de proposito: o cabecalho do
arquivo continua dizendo o nome original, que e por onde se acha o script no
upstream.

O que NAO se renomeia, e o motivo: `Crewman_bra2` (o nome unico depois do
`::`, e ele e chamado por `getnpcid` de dois outros arquivos, um deles
nosso), `inbathroom#bra` e `#Monkeybra` (nome vazio ou puramente tecnico), e
os nomes proprios que o bRO manteve - Angelo, Pedro, Mariana, Fabio, Daniel,
Poring, Iara.

Roda em Python 2.7.
"""
import io
import os
import sys

# nome antigo -> nome novo, na forma em que aparecem no arquivo.
MAPA = [
    (u'Crewman#bra1',          u'Marinheiro#bra1'),
    (u'Signpost#bra',          u'Placa#bra'),
    (u'Ice-Cream Maker',       u'Vendedor de Sorvete'),
    (u'Brasilis Guide',        u'Guia de Brasilis'),
    (u'Puppy#',                u'Filhote#'),
    (u'Lucia#brasilis',        u'Bióloga Marinha#brasilis'),
    (u'Candy Maker',           u'Doceira'),
    (u'Cherto',                u'Paulão'),
    (u'Strange Kid#bra',       u'Garoto Estranho#bra'),
    (u'Mage Paje#bra',         u'Pajé Ubirajá#bra'),
    (u'Toucan#bra',            u'Tucano#bra'),
    (u'Jaguar#bra',            u'Onça#bra'),
    (u'Monkey#bra',            u'Macaco#bra'),
    (u'Botanist Karmen#bra',   u'Botânica Carmen#bra'),
    (u'Marta#bra',             u'Anciã Jurema#bra'),
    (u'Brasilis Boy#bra',      u'Menino#bra'),
    (u'Brasilis Girl#bra',     u'Menina#bra'),
    (u'Recluse#bra',           u'Ermitão#bra'),
    (u'Water lily#bra',        u'Vitória-Régia#bra'),
    (u'Door#bra',              u'Porta#bra'),
    (u'Toilet#bra',            u'Privada#bra'),
    (u'Faucet#bra',            u'Torneira#bra'),
    (u'Carpet#bra',            u'Tapete#bra'),
    (u'Mirror#bra',            u'Espelho#bra'),
    (u'Ghost#bra',             u'Loira do Banheiro#bra'),
    (u'Curator#bra',           u'Curador#bra'),
    (u'Open Manhole#todunbra', u'Bueiro Aberto#todunbra'),
    (u'Pipe#bra',              u'Cano#bra'),
    (u'Shaman#nk',             u'Pajé#nk'),
    (u'Native Warrior#nk',     u'Índio Guerreiro#nk'),
]

ARQUIVOS = ['npc/cities/brasilis.txt',
            'npc/re/guides/guides_brasilis.txt',
            'npc/quests/quests_brasilis.txt']

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATHENA = os.path.join(REPO, 'rathena')
CONFERIR = '--conferir' in sys.argv


def main():
    total = 0
    for rel in ARQUIVOS:
        p = os.path.join(RATHENA, rel.replace('/', os.sep))
        d = io.open(p, 'r', encoding='cp1252', newline='').read()
        linhas = d.split(u'\n')
        n = 0
        for i, ln in enumerate(linhas):
            if ln.lstrip().startswith(u'//'):
                continue
            nova = ln
            for velho, novo in MAPA:
                if velho in nova:
                    n += nova.count(velho)
                    nova = nova.replace(velho, novo)
            linhas[i] = nova
        if n and not CONFERIR:
            io.open(p, 'w', encoding='cp1252',
                    newline='').write(u'\n'.join(linhas))
        print '%-40s %d' % (rel, n)
        total += n
    if CONFERIR:
        print 'total: %d nome(s) ainda em ingles' % total
        return 1 if total else 0
    print 'total: %d troca(s)' % total
    return 0


if __name__ == '__main__':
    sys.exit(main())
