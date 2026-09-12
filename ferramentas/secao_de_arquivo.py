# -*- coding: utf-8 -*-
u"""Secao marcada dentro de um arquivo que tem MAIS DE UM dono.

POR QUE ISTO EXISTE

O `db/import/mob_skill_db.txt` e o unico lugar onde habilidade de monstro
nossa pode morar: o `mob_skill_db.txt` nao e YAML, nao tem rodape
`Footer: Imports:`, e o `mob_readskilldb` (`src/map/mob.cpp:7184`) le de
`db/re/` e de `db/import/` e mais nada. Como `db/re/` e arquivo de
terceiro, sobra um arquivo so - e a partir de 2026-09-11 ele tem DOIS
geradores: o `monta_mobs_da_sombria.py` e o `monta_ilusao_do_labirinto.py`.

Dois geradores que reescrevem o arquivo inteiro se apagam em silencio: o
ultimo a rodar leva o outro junto, o servidor sobe, e os monstros do
perdedor simplesmente param de conjurar - sem erro, sem log, sem nada.
Foi para isso que este modulo existe.

COMO SE USA

Cada gerador escreve SO a sua secao, entre duas marcas, e preserva byte a
byte tudo o que estiver fora dela:

    //>>> INICIO SOMBRIA
    ...
    //<<< FIM SOMBRIA

`troca` devolve o texto novo (acrescenta a secao no fim se ela ainda nao
existir); `le` devolve o corpo da secao, ou None. O `--conferir` de cada
ferramenta compara so a propria secao - assim uma nao reprova por causa da
outra.
"""

INICIO = '//>>> INICIO %s'
FIM = '//<<< FIM %s'


def _marcas(nome):
    return INICIO % nome, FIM % nome


def le(texto, nome):
    u"""O corpo da secao `nome`, ou None se ela nao estiver no texto."""
    ini, fim = _marcas(nome)
    i = texto.find(ini)
    if i < 0:
        return None
    j = texto.find(fim, i)
    if j < 0:
        raise SystemExit('a secao %s comeca e nao termina - marca `%s` ausente'
                         % (nome, fim))
    return texto[i + len(ini):j].lstrip('\n')


def troca(texto, nome, corpo):
    u"""Troca (ou acrescenta) a secao `nome`, sem tocar no resto do arquivo."""
    ini, fim = _marcas(nome)
    bloco = '%s\n%s%s\n' % (ini, corpo if corpo.endswith('\n') else corpo + '\n',
                            fim)
    i = texto.find(ini)
    if i < 0:
        antes = texto.rstrip('\n')
        return (antes + '\n\n' + bloco) if antes else bloco
    j = texto.find(fim, i)
    if j < 0:
        raise SystemExit('a secao %s comeca e nao termina - marca `%s` ausente'
                         % (nome, fim))
    depois = texto[j + len(fim):].lstrip('\n')
    return texto[:i] + bloco + ('\n' + depois if depois else '')
