# -*- coding: utf-8 -*-
"""Tira do exe a trava que corta a lista de cor de roupa do estilista em 3.

    python destrava_estilista.py                 # diz se o exe esta travado ou destravado
    python destrava_estilista.py --aplicar       # patcheia (guarda backup ao lado)
    python destrava_estilista.py --reverter      # devolve os 3 bytes originais

A DESCOBERTA (2026-09-14). A janela do estilista (`openstylist`) le a lista
de cores de roupa do `stylingshopinfo.lub` e desenha com as palettes do
GRF - e mesmo assim so oferecia 3 cores (0, 2, 3) para toda classe que nao
fosse de 4a, com 7, 8 ou 15 entradas na lista e com as palettes 4..15 tanto
soltas em data\\ quanto dentro do guerra.grf. Nao era arquivo: era o exe.
Em `UIStylingShopWnd`, logo depois de `StylingShop_GetSizeInTable`:

    00bf61e5  mov    eax, [tamanho da lista]
    00bf61e8  mov    ecx, 3
    00bf61ed  cmp    byte [flag], 0      ; flag = lista e "BodyPalette" ou
    ...                                  ;   "DoramBodyPalette" E a classe
    00bf61f8  cmovne eax, ecx            ;   NAO e de 4a -> tamanho = 3
    00bf61fb  mov    [tamanho], eax

A funcao que decide "e de 4a" (0x85bd10) devolve verdadeiro so para os
trabalhos 4252..4299 e 4302..4329. Para todo o resto a Gravity corta em 3
de proposito - e o motivo de o kRO nunca ter mostrado mais que isso. O
mesmo trecho existe DUAS vezes (0xbf5f78 e 0xbf61f8, as duas setas), e
so nelas: os outros usos de `GetSizeInTable` nao tem o corte.

O PATCH: os 3 bytes do `cmovne eax, ecx` (0F 45 C1) viram `nop nop nop`
nos dois pontos. O `mov ecx, 3` fica, morto. Nada mais muda: a lista passa
a ter o tamanho do lua para toda classe, como ja tinha para as de 4a.

E POR PADRAO DE BYTES, nao por endereco: o script procura os 20 bytes
`b9 03 00 00 00 80 7d bf 00 c7 45 b0 00 00 00 00 0f 45 c1 89` e exige
EXATAMENTE dois acertos - exe de outra versao da zero ou outro numero, e o
script recusa em vez de chutar. O exe e a unica peca do cliente sem
gerador versionado (REFERENCIA.md, "Patches do NEMO"); este script e a
receita deste patch, e o .epi do NEMO nao sabe dele.

Depois: e mudanca de cliente, vai por patch (CLAUDE.md 4.18) - e o exe so
se grava com o cliente FECHADO (5, "fechar o cliente ANTES de gravar").

Roda em Python 2.7.
"""
import os
import shutil
import sys

EXE = r'C:\GuerraDoEmperium\cliente\GuerraDoEmperium.exe'
BACKUP = EXE + '.antes-de-destrava_estilista'

PADRAO = 'b903000000807dbf00c745b0000000000f45c189'.decode('hex')
TRAVADO = '\x0f\x45\xc1'           # cmovne eax, ecx
DESTRAVADO = '\x90\x90\x90'        # nop nop nop
POS = PADRAO.index(TRAVADO)
ACERTOS = 2


def acha(d, miolo):
    alvo = PADRAO[:POS] + miolo + PADRAO[POS + 3:]
    hits = []
    i = d.find(alvo)
    while i >= 0:
        hits.append(i)
        i = d.find(alvo, i + 1)
    return hits


def main():
    d = open(EXE, 'rb').read()
    travados = acha(d, TRAVADO)
    livres = acha(d, DESTRAVADO)
    print 'exe: %d ponto(s) travado(s), %d destravado(s)' % (len(travados), len(livres))
    if '--aplicar' in sys.argv:
        if len(travados) != ACERTOS:
            print 'esperava %d pontos travados; nao mexo' % ACERTOS
            return 1
        if not os.path.exists(BACKUP):
            shutil.copy2(EXE, BACKUP)
            print 'backup em %s' % BACKUP
        for i in travados:
            d = d[:i + POS] + DESTRAVADO + d[i + POS + 3:]
        open(EXE, 'wb').write(d)
        print 'destravado em %s' % ', '.join('0x%x' % (i + POS) for i in travados)
        return 0
    if '--reverter' in sys.argv:
        if len(livres) != ACERTOS:
            print 'esperava %d pontos destravados; nao mexo' % ACERTOS
            return 1
        for i in livres:
            d = d[:i + POS] + TRAVADO + d[i + POS + 3:]
        open(EXE, 'wb').write(d)
        print 'revertido'
        return 0
    return 0 if len(livres) == ACERTOS else 1


if __name__ == '__main__':
    sys.exit(main())
