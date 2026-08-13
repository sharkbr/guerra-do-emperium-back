# -*- coding: utf-8 -*-
"""Decide qual bandeira cada CTRL+<n> solta no cliente.

Python 2.7.

    python ordena_bandeiras_ctrl.py --verificar   # so relata, nao grava
    python ordena_bandeiras_ctrl.py               # aplica (faz backup antes)

O PEDIDO, 2026-08-12: "CTRL+1 tem que ser bandeira do Brasil". Estava em
CTRL+6, e o CTRL+1 dava a da Coreia.

ONDE ISSO MORA, e nao e em lua nenhum. As emocoes de bandeira NAO estao no
`EMOTION_ORDERLIST` do `emotionlist.lub` - aquela lista tem 64 entradas e
nenhuma bandeira, porque bandeira nao aparece na janela de emocoes. Quem
trata CTRL+<n> e o EXE, num `switch` de nove casos:

    0x00638950  mov  ecx, [00F3D1D4]        ; o objeto que envia a emocao
                test ecx, ecx / jz fim
                mov  eax, [ebp+8]           ; a tecla
                add  eax, -0D2h             ; 210 -> caso 0
                cmp  eax, 8 / ja fim
                jmp  [eax*4 + 00638B1Ch]    ; A TABELA DE SALTOS

Cada caso e uma CADEIA DE COMPARACOES contra o <servicetype> do
`clientinfo.xml` (o global `[012BF51C]`: korea=0, america=1, ... brazil=12,
na ordem em que os nomes estao no `.rdata`), e so no fim vem o "rabicho" que
de fato empurra a emocao:

    8B 01                mov  eax, [ecx]
    6A 00 6A 00 6A 00    push 0, 0, 0
    6A <emocao>          push <id da emocao>       <- a bandeira
    6A 1F                push 1Fh
    FF 50 18             call [eax+18h]

Ou seja a mesma tecla da bandeiras diferentes conforme o servicetype, e na
maioria deles nao da bandeira nenhuma: com `brazil` (12) SO o CTRL+1
funciona, e os outros oito casos caem fora sem fazer nada.

O QUE ESTA FERRAMENTA FAZ: reescreve as nove entradas da tabela de saltos
para apontarem DIRETO no rabicho de cada bandeira, pulando a cadeia de
servicetype inteira. Sao 36 bytes, todos de dados, nenhum de codigo.

Duas consequencias, as duas boas:

  1) a ordem passa a ser a da tabela ORDEM aqui embaixo, e nao mais uma
     funcao do servicetype - as nove teclas funcionam sempre;
  2) entrar no rabicho e seguro porque ele so precisa do `ecx`, que o
     prologo carrega ANTES do salto. Nao ha nada na cadeia pulada alem das
     comparacoes.

CUIDADO DE PE: a tabela esta em `.text` (arquivo 0x00237F1C), muito antes do
fim do `SizeOfRawData` - nao e o caso da `.xdiff`, onde metade da secao nao
existe em disco (CLAUDE.md secao 5). E as entradas sao VAs absolutos, que ja
tem entrada em `.reloc`; escrever outro VA da MESMA secao nao mexe nisso.

NADA AQUI E PROCURADO POR ENDERECO FIXO. A tabela e achada pelo padrao do
prologo e os rabichos pelo padrao dos nove `push`; os enderecos acima sao
so documentacao. Se o exe for repatchado ou trocado, a ferramenta reacha.

DEPOIS DE RODAR: FECHAR O CLIENTE ANTES, nao depois - o exe fica travado
enquanto roda, e o que ja esta aberto segue na copia em memoria (CLAUDE.md
secao 3).

E O AVISO QUE VALE PARA TODO PATCH DE EXE DESTE PROJETO: `--verificar`
dizendo "aplicado" NAO e prova de efeito, e script que confere o proprio
trabalho nao prova nada (CLAUDE.md secao 5, "Tamanho da fonte"). Quem prova
e apertar CTRL+1 no jogo e ver a bandeira verde e amarela.
"""

import os
import shutil
import struct
import sys
import time


EXE = os.path.join('C:\\', 'GuerraDoEmperium', 'cliente',
                   'GuerraDoEmperium.exe')

# Os ids do `enum emotion_type` (src/map/clif.hpp) que sao bandeira.
NOMES = {
    13: 'Coreia',
    35: 'Indonesia',
    48: 'Filipinas',
    49: 'Malasia',
    50: 'Cingapura',
    51: 'Brasil',
    64: 'India',
    66: 'Bandeira 8',
    67: 'Bandeira 9',
}

# A ORDEM QUE QUEREMOS, de CTRL+1 a CTRL+9.
#
# E a ordem que o cliente ja tinha com servicetype `korea`, com o Brasil e a
# Coreia TROCADOS de lugar - so isso. Trocar e nao empurrar a fila foi de
# proposito: quem ja decorou CTRL+3 continua com Filipinas.
ORDEM = [51, 35, 48, 49, 50, 13, 64, 66, 67]


def carrega():
    f = open(EXE, 'rb')
    d = f.read()
    f.close()
    return d


def secoes(d):
    """Devolve (ImageBase, [(nome, va, vsz, ra, rsz)])."""
    lfanew = struct.unpack('<I', d[0x3C:0x40])[0]
    if d[lfanew:lfanew + 4] != 'PE\x00\x00':
        raise Exception('nao e PE')
    nsec = struct.unpack('<H', d[lfanew + 6:lfanew + 8])[0]
    szopt = struct.unpack('<H', d[lfanew + 20:lfanew + 22])[0]
    opt = lfanew + 24
    base = struct.unpack('<I', d[opt + 28:opt + 32])[0]
    out = []
    p = opt + szopt
    for _ in range(nsec):
        s = d[p:p + 40]
        vsz, va, rsz, ra = struct.unpack('<IIII', s[8:24])
        out.append((s[0:8].rstrip('\x00'), va, vsz, ra, rsz))
        p += 40
    return base, out


def faz_conversores(d):
    base, secs = secoes(d)

    def para_arquivo(va):
        r = va - base
        for _n, sva, vsz, ra, rsz in secs:
            if sva <= r < sva + max(vsz, rsz):
                if r - sva >= rsz:
                    # so existe em memoria - a armadilha da `.xdiff`
                    return None
                return ra + (r - sva)
        return None

    def para_va(o):
        for _n, sva, _vsz, ra, rsz in secs:
            if ra <= o < ra + rsz:
                return base + sva + (o - ra)
        return None

    return para_arquivo, para_va


# add eax,-0D2h ; cmp eax,8 ; ja rel32 ; jmp [eax*4 + <tabela>]
PROLOGO = ('\x05\x2E\xFF\xFF\xFF'      # add eax, -0D2h
           '\x83\xF8\x08'              # cmp eax, 8
           '\x0F\x87')                 # ja  rel32
SALTO = '\xFF\x24\x85'                 # jmp dword ptr [eax*4 + imm32]

# 8B 01 | 6A 00 x3 | 6A <emocao> | 6A 1F | FF 50 18
RABICHO_A = '\x8B\x01\x6A\x00\x6A\x00\x6A\x00\x6A'
RABICHO_B = '\x6A\x1F\xFF\x50\x18'


def acha_tabela(d):
    """Devolve o VA da tabela de saltos das bandeiras."""
    achados = []
    p = 0
    while True:
        p = d.find(PROLOGO, p)
        if p < 0:
            break
        q = p + len(PROLOGO) + 4
        if d[q:q + 3] == SALTO:
            achados.append(struct.unpack('<I', d[q + 3:q + 7])[0])
        p += 1
    if len(achados) != 1:
        raise Exception('esperava UM switch de 9 casos com `add eax,-0D2h`; '
                        'achei %d' % len(achados))
    return achados[0]


def acha_rabichos(d, para_va, ini, fim):
    """Devolve {id da emocao: VA do rabicho} na janela [ini, fim) do arquivo."""
    out = {}
    o = ini
    while o < fim:
        if d[o:o + 9] == RABICHO_A and d[o + 10:o + 15] == RABICHO_B:
            emocao = ord(d[o + 9])
            if emocao in NOMES:
                if emocao in out:
                    raise Exception('dois rabichos para a emocao %d' % emocao)
                out[emocao] = para_va(o)
            o += 15
            continue
        o += 1
    return out


def levanta(d):
    """Devolve (offset da tabela no arquivo, [VAs atuais], {emocao: VA})."""
    para_arquivo, para_va = faz_conversores(d)
    tabela_va = acha_tabela(d)
    tabela_off = para_arquivo(tabela_va)
    if tabela_off is None:
        raise Exception('tabela de saltos fora do que existe em disco')
    atuais = [struct.unpack('<I', d[tabela_off + 4 * i:tabela_off + 4 * i + 4])[0]
              for i in range(9)]

    # Os nove rabichos estao entre o primeiro caso e a propria tabela.
    ini = para_arquivo(min(atuais))
    rabichos = acha_rabichos(d, para_va, ini, tabela_off)
    faltam = [e for e in ORDEM if e not in rabichos]
    if faltam:
        raise Exception('nao achei rabicho para as emocoes %s' % faltam)
    return tabela_off, atuais, rabichos


def descreve(atuais, rabichos):
    """Diz, tecla a tecla, para onde a tabela aponta hoje."""
    de_va = dict((va, e) for e, va in rabichos.items())
    linhas = []
    for i, va in enumerate(atuais):
        emocao = de_va.get(va)
        if emocao is None:
            linhas.append('  CTRL+%d  0x%08X  cadeia de servicetype (o original)'
                          % (i + 1, va))
        else:
            linhas.append('  CTRL+%d  0x%08X  %s (emocao %d)'
                          % (i + 1, va, NOMES[emocao], emocao))
    return linhas


def main():
    so_ver = '--verificar' in sys.argv[1:]
    d = carrega()
    tabela_off, atuais, rabichos = levanta(d)

    print 'exe      %s' % EXE
    print 'tabela   arquivo 0x%08X, 9 entradas' % tabela_off
    print
    print 'HOJE:'
    for l in descreve(atuais, rabichos):
        print l

    novos = [rabichos[e] for e in ORDEM]
    print
    print 'DEPOIS:'
    for l in descreve(novos, rabichos):
        print l

    if novos == atuais:
        print
        print 'nada a fazer - a tabela ja esta assim.'
        return 0
    if so_ver:
        print
        print '--verificar: nada foi gravado.'
        return 0

    carimbo = time.strftime('%Y%m%d-%H%M')
    backup = '%s.BACKUP-bandeiras-%s' % (EXE, carimbo)
    shutil.copy2(EXE, backup)

    novo = d[:tabela_off] + ''.join(struct.pack('<I', v) for v in novos) \
        + d[tabela_off + 36:]
    if len(novo) != len(d):
        raise Exception('o exe mudou de tamanho - abortado')
    f = open(EXE, 'wb')
    f.write(novo)
    f.close()

    print
    print 'gravado. backup em %s' % backup
    print
    print 'FECHE E REABRA O CLIENTE - e aperte CTRL+1 no jogo. Este script'
    print 'nao prova efeito nenhum; so a tela prova.'
    return 0


if __name__ == '__main__':
    sys.exit(main())
