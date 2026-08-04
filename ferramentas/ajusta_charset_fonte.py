# -*- coding: utf-8 -*-
u"""Faz o cliente desenhar texto Latin-1 em vez de tratar byte alto como hangul.

    python ajusta_charset_fonte.py --verificar   # so relata
    python ajusta_charset_fonte.py               # aplica (faz backup)
    python ajusta_charset_fonte.py --reverter    # volta ao HANGUL original

------------------------------------------------------------------ o problema

Com o cliente em portugues, todo acento saia errado - e nao "some": ele
**come a letra seguinte**. "Carvao" com til virava "Carv?", "Indestrutivel"
virava "Indestrut?el". Assinatura de byte-lider CP949: `0xE3` e lido como
inicio de silaba coreana, engole o proximo byte, e o par vira um glifo hanja
ou um `?`.

------------------------------------------------------------------ o caminho

Tres tentativas erradas antes desta, e as tres valem registro porque cada uma
parecia obvia:

1. **`AlwaysAscii`** - o patch ja estava aplicado e nao tem nada a ver: ele
   anula um `jnz` dentro de `CSession::IsOnlyEnglish`, que e sobre chat.
2. **`CustomFontCharset` = ANSI** - aplicou de verdade (17 bytes, desviando o
   `call [CreateFontA]` para um cave que forca charset 0), e nao mudou nada.
   O cliente tambem usa `CreateFontIndirectA`, e quem alimenta os dois e uma
   variavel, nao o argumento daquela chamada.
3. **`FixFontsCharset`** - e o patch certo em conceito, e **nao existe para
   este exe**: o `.qjs` dele so tem `case` para `Exe.Version` 6, 9, 10 e 11
   (VC6 a VC2012), e o nosso e VC140 (MSVCP140/VCRUNTIME140). Ele cai no
   `throw Error("Function not found")` e o WARP descarta calado - o binario
   sai byte a byte igual, so com data de modificacao nova. Foi o que
   confundiu: "apliquei e nao mudou" era "nao aplicou".

------------------------------------------------------------------ a correcao

O proprio cliente ja tem a tabela de charset por idioma, em `.data`:

    VA 0x00F392D0   [0]=0x81 HANGUL  [1]=0x00 ANSI  [2]=0x80 SHIFTJIS
                    [3]=0x86 GB2312  [4]=0x88 BIG5  [5]=0xDE THAI ...

E ela e lida em UM lugar so, no `DrawDC::SetFont`:

    85 ff                  test edi, edi
    75 0a                  jnz  +10
    a1 d0 92 f3 00         mov  eax, [tabela]          ; indice 0
    83 fa 14               cmp  edx, 14h
    7d 07                  jge  +7
    8b 04 95 d0 92 f3 00   mov  eax, [edx*4 + tabela]  ; indice = langtype

O indice vem do **langtype**, nao do servicetype - por isso trocar o
`<servicetype>` para `brazil` no clientinfo.xml nao adiantou sozinho. Com
`<langtype>0</langtype>` o cliente cai no indice 0, que e HANGUL.

Este script troca **a entrada 0 da tabela**, de `0x81` (HANGUL) para `0x00`
(ANSI). Um dword de dados, sem tocar em codigo. Pega os dois caminhos do `if`
acima e independe de qual variavel alimenta o `EDX`.

O custo e nao poder mais desenhar coreano, o que nao custa nada aqui: o
cliente e inteiro portugues, com ingles de reserva.

Idempotente, com backup, e `--reverter` desfaz. Roda em Python 2.7.
"""
import os
import shutil
import struct
import sys
import time

EXE_PADRAO = os.path.join(r'C:\GuerraDoEmperium\cliente',
                          'GuerraDoEmperium.exe')

HANGUL = 0x81
ANSI = 0x00

# A tabela e reconhecida pelo conteudo, nao pelo endereco: os cinco charsets
# seguintes ao coreano sao invariantes entre builds e nao aparecem nessa
# ordem em nenhum outro lugar do binario.
ASSINATURA = [None, 0x00, 0x80, 0x86, 0x88, 0xDE]


class Erro(Exception):
    pass


def acha_tabela(d):
    u"""Offset da tabela de charset por idioma, achado por assinatura.

    A busca e ancorada na ENTRADA 1 (`0x00000080` de SHIFTJIS em diante), e
    nao na entrada 0 - porque a entrada 0 e justamente a que este script
    troca, e ancorar nela faria a ferramenta nao se achar depois de aplicada.
    Foi o que aconteceu na primeira versao: aplicou certo e o `--verificar`
    seguinte respondeu "nao achei a tabela".
    """
    achados = []
    ancora = struct.pack('<I', ASSINATURA[2])       # japan = SHIFTJIS
    pos = 0
    while True:
        i = d.find(ancora, pos)
        if i < 0:
            break
        pos = i + 4
        ini = i - 8                                # duas entradas antes
        if ini < 0 or ini + 80 > len(d):
            continue
        vals = struct.unpack('<20I', d[ini:ini + 80])
        if vals[0] not in (HANGUL, ANSI):
            continue
        if all(esperado is None or vals[n] == esperado
               for n, esperado in enumerate(ASSINATURA)):
            achados.append((ini, vals))
    if not achados:
        raise Erro('nao achei a tabela de charset neste exe')
    if len(achados) > 1:
        raise Erro('achei %d candidatas a tabela; nao vou adivinhar'
                   % len(achados))
    return achados[0]


def checksum(d, off):
    u"""Checksum do PE, igual ao CheckSumMappedFile. Os 4 bytes do proprio
    campo entram como zero."""
    soma = 0
    for i in range(0, len(d) - 1, 2):
        if off <= i < off + 4:
            continue
        soma += struct.unpack('<H', d[i:i + 2])[0]
        soma = (soma & 0xffff) + (soma >> 16)
    if len(d) % 2:
        soma += ord(d[-1])
        soma = (soma & 0xffff) + (soma >> 16)
    soma = (soma & 0xffff) + (soma >> 16)
    return (soma + len(d)) & 0xffffffff


NOMES = ['korea', 'america', 'japan', 'china', 'taiwan', 'thai', 'turkey',
         '(7)', '(8)', 'russia', 'vietnam', 'arabic', '(12)', '(13)', '(14)',
         '(15)', '(16)', '(17)', '(18)', '(19)']


def main(argv):
    verificar = '--verificar' in argv
    reverter = '--reverter' in argv
    novo = HANGUL if reverter else ANSI

    # Caminho alternativo: o exe fica travado enquanto o cliente roda, e o
    # jeito de contornar e patchar uma copia e trocar por renomeacao - o
    # Windows deixa renomear um exe em uso. Mesma manobra do traduz_setup.py.
    alvos = [a for a in argv if not a.startswith('--')]
    EXE = alvos[0] if alvos else EXE_PADRAO

    if not os.path.exists(EXE):
        raise Erro('nao achei %s' % EXE)
    fh = open(EXE, 'rb')
    d = bytearray(fh.read())
    fh.close()

    off, vals = acha_tabela(str(d))
    print 'exe:     %s' % EXE
    print 'tabela:  offset 0x%X' % off
    for i in range(6):
        print '   [%d] %-9s 0x%02X%s' % (i, NOMES[i], vals[i],
                                         '   <-- a que muda' if i == 0 else '')
    atual = vals[0]
    print
    print 'entrada 0: 0x%02X (%s)  ->  0x%02X (%s)' % (
        atual, 'HANGUL' if atual == HANGUL else 'ANSI',
        novo, 'HANGUL' if novo == HANGUL else 'ANSI')

    if atual == novo:
        print 'Nada a fazer: ja esta assim.'
        return 0
    if verificar:
        print '\n--verificar: nenhum byte gravado.'
        return 0

    struct.pack_into('<I', d, off, novo)

    # Checksum do PE. O WARP mantem o dele, entao mantemos tambem - exe com
    # checksum errado passa despercebido ate o dia em que alguma camada de
    # seguranca resolve conferir.
    pe = struct.unpack('<I', str(d[0x3c:0x40]))[0]
    opt = pe + 24
    csoff = opt + 64
    if struct.unpack('<I', str(d[csoff:csoff + 4]))[0]:
        struct.pack_into('<I', d, csoff, 0)
        struct.pack_into('<I', d, csoff, checksum(str(d), csoff))
        print 'checksum do PE recalculado.'

    backup = '%s.BACKUP-charset-%s' % (EXE, time.strftime('%Y%m%d-%H%M'))
    if not os.path.exists(backup):
        shutil.copy2(EXE, backup)
        print 'backup: %s' % os.path.basename(backup)
    fh = open(EXE, 'wb')
    fh.write(str(d))
    fh.close()
    print 'gravado.'
    print
    print 'Feche e reabra o cliente. O exe fica travado enquanto ele roda -'
    print 'se der erro de permissao, e porque o cliente ainda esta aberto.'
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
