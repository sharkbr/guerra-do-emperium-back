# -*- coding: utf-8 -*-
u"""Faz a trava de "jogo ja aberto" do Setup.exe olhar para a NOSSA janela.

O Setup.exe da Gravity se recusa a abrir enquanto houver cliente de Ragnarok
rodando -- a configuracao de video so vale na proxima abertura do jogo, e o
cliente ainda reescreve parte da chave ao sair. O teste dele e:

    FindWindowA("Ragnarok", "Ragnarok")   -> se achou, mostra caixa e sai

E aqui esse teste esta mirando o alvo errado, nas duas pontas. O nosso cliente
teve o nome da janela trocado: o `GuerraDoEmperium.exe` escreve
`0x00E29170` ("GuerraDoEmperium") no global `0x00F65DBC` (em `0x00C107E1`), e
esse mesmo ponteiro vai como CLASSE e como TITULO no CreateWindowEx. Ou seja:

  - o nosso jogo aberto NAO e detectado -- a trava esta morta para nos;
  - o cliente de QUALQUER outro servidor que ainda se chame "Ragnarok" e,
    esse sim, detectado -- e o nosso Setup se recusa a abrir por causa da
    janela de outro jogo. Aconteceu com um jogador em 2026-09-12.

E a caixa sai VAZIA. O texto vem da chave `alreadyclient` procurada no
`System\LuaFiles514\MsgString.lub`, que no arquivo do kRO nao existe -- so ha
o `SetupMSG` com as dicas da aba Opcoes. Entao a unica pista que o jogador
recebe e uma caixa "Message" sem uma letra dentro.

Este script conserta as duas coisas, mexendo em 32 bytes de codigo:

  - os dois `push "Ragnarok"` passam a apontar para "GuerraDoEmperium";
  - as 22 instrucoes que montavam o texto (a busca da chave que nao existe)
    viram um `push <literal>` mais NOPs, e o titulo da caixa deixa de ser
    "Message".

O tamanho do bloco nao muda de proposito: o `je +0x2A` logo acima pula
exatamente por cima dele, e mexer no comprimento exigiria recalcular o salto.

As strings novas vao para o padding zerado do fim da secao .text, depois das
que o `traduz_setup.py` ja pos la -- e o mesmo cave, e ele tem 492 bytes.

Uso:
    python ajusta_trava_do_setup.py <Setup.exe>              # aplica (faz backup)
    python ajusta_trava_do_setup.py <Setup.exe> --verificar  # so relata
"""
import os
import re
import shutil
import struct
import sys
import time

from traduz_setup import PE, Erro

# ---------------------------------------------------------------- parametros

# Classe E titulo da janela do nosso cliente -- os dois sao a mesma string,
# escrita pelo patch de nome do `GuerraDoEmperium.exe`. Se um dia o cliente
# for renomeado, este e o valor a mudar (e o Setup tem de ser repatchado).
NOME_DA_JANELA = b'GuerraDoEmperium'

# A caixa que o jogador ve quando tenta configurar o video com o jogo aberto.
# cp1252, como todo texto que o jogo desenha (CLAUDE.md 4.1): o MessageBoxA e
# ANSI. Uma linha so por paragrafo -- quem quebra o texto e a propria caixa.
TITULO_DA_CAIXA = b'Guerra do Emperium'
TEXTO_DA_CAIXA = (
    b'O Guerra do Emperium est\xe1 aberto.\n\n'
    b'Feche o jogo e abra esta janela de novo. O cliente l\xea a configura\xe7\xe3o '
    b'de v\xeddeo s\xf3 na abertura, ent\xe3o o que voc\xea mudar aqui vale a partir '
    b'da pr\xf3xima vez que o jogo abrir.')

# O bloco de 22 bytes que montava o texto: push 0x48 (o indice de
# "alreadyclient"), a busca, e o push do resultado. Trocado por um push de
# literal mais NOPs, mantendo o comprimento.
TAM_BLOCO_DO_TEXTO = 22

NOP = b'\x90'

# Marcadores do montador de padrao abaixo.
IMM = object()          # imm32 que interessa ler -> vira grupo
QUALQUER4 = object()    # imm32 que nao interessa (rel32 de call)


def padrao(*partes):
    u"""Monta um regex de bytes escapando os trechos literais.

    Escapar nao e zelo: byte de codigo calha de ser metacaractere. O `0x2A`
    do `je +0x2a` e um `*`, e cru ele vira "repita o byte anterior" -- o
    padrao passa a casar com outra coisa (ou com nada) sem erro nenhum."""
    return re.compile(b''.join(
        b'(....)' if p is IMM else b'....' if p is QUALQUER4 else re.escape(p)
        for p in partes), re.S)


ORIGINAL = padrao(
    b'\x68', IMM,            # push lpWindowName  "Ragnarok"
    b'\x68', IMM,            # push lpClassName   "Ragnarok"
    b'\xff\x15', IMM,        # call FindWindowA
    b'\x85\xc0',             # test eax, eax
    b'\x74\x2a',             # je   +0x2a   (pula a caixa inteira)
    b'\x6a\x00',             # push 0             uType
    b'\x68', IMM,            # push lpCaption     "Message"
    b'\x6a\x48',             # push 72            indice de "alreadyclient"
    b'\xe8', QUALQUER4,      # call  <tabela de chaves>
    b'\x83\xc4\x04',         # add   esp, 4
    b'\xb9', QUALQUER4,      # mov   ecx, <mapa de mensagens>
    b'\x50',                 # push  eax
    b'\xe8', QUALQUER4,      # call  <busca a chave>   -> devolve "" aqui
    b'\x50',                 # push  eax          lpText
    b'\x6a\x00',             # push  0            hWnd
    b'\xff\x15', IMM)        # call MessageBoxA

JA_APLICADO = padrao(
    b'\x68', IMM, b'\x68', IMM, b'\xff\x15', IMM, b'\x85\xc0\x74\x2a',
    b'\x6a\x00\x68', IMM, b'\x68', IMM, NOP * 17, b'\x6a\x00\xff\x15', IMM)


# ------------------------------------------------------------------ leitura

def importados(pe):
    u"""{endereco do thunk: "DLL!Funcao"} -- para provar que os `call [...]`
    do bloco sao mesmo FindWindowA e MessageBoxA, e nao outra coisa que por
    acaso casou com o padrao de bytes."""
    dd = pe.opt + 96
    rva = pe.u32(dd + 8)
    off = pe.rva2off(rva)
    out = {}
    while True:
        oft, tds, fwd, nome_rva, first = struct.unpack_from('<IIIII', pe.d, off)
        if nome_rva == 0:
            break
        dll = bytes(pe.d[pe.rva2off(nome_rva):]).split(b'\0')[0]
        a = pe.rva2off(oft or first)
        thunk = first
        while True:
            v = pe.u32(a)
            if v == 0:
                break
            if not v & 0x80000000:
                nome = bytes(pe.d[pe.rva2off(v) + 2:]).split(b'\0')[0]
                out[pe.imagebase + thunk] = '%s!%s' % (dll, nome)
            a += 4
            thunk += 4
        off += 20
    return out


def cave_livre(pe):
    u"""Padding zerado do fim de .text, a partir do primeiro byte ainda livre.

    Nao e o `cave()` do traduz_setup: aquele exige a area inteira zerada, e
    aqui ela ja tem as strings dos botoes. Devolve (offset, rva, tamanho)."""
    name, va, vs, ra, rs = pe.sections[0]
    if name != '.text':
        raise Erro('primeira secao nao e .text')
    inicio, tam = ra + vs, rs - vs
    area = bytes(pe.d[inicio:inicio + tam])
    usado = len(area.rstrip(b'\0'))
    usado = (usado + 3) & ~3                       # alinha o proximo literal
    if usado >= tam:
        raise Erro('o padding do fim de .text esta cheio')
    return inicio + usado, va + vs + usado, tam - usado


# ------------------------------------------------------------------- patch

def aplica(path, verificar):
    pe = PE(path)
    bruto = bytes(pe.d)

    if JA_APLICADO.search(bruto):
        print u'Nada a fazer: a trava ja olha para a nossa janela.'
        return

    achados = list(ORIGINAL.finditer(bruto))
    if len(achados) != 1:
        raise Erro(u'esperava 1 bloco da trava, achei %d' % len(achados))
    m = achados[0]
    janela1, janela2, thunk_fw, caixa, thunk_mb = [
        struct.unpack('<I', g)[0] for g in m.groups()]

    if janela1 != janela2:
        raise Erro(u'os dois push da FindWindow apontam para strings '
                   u'diferentes (%08x e %08x)' % (janela1, janela2))
    imp = importados(pe)
    for thunk, esperado in ((thunk_fw, 'USER32.dll!FindWindowA'),
                            (thunk_mb, 'USER32.dll!MessageBoxA')):
        if imp.get(thunk) != esperado:
            raise Erro(u'o call [%08x] e %s, esperava %s'
                       % (thunk, imp.get(thunk), esperado))

    def literal(addr):
        o = pe.rva2off(addr - pe.imagebase)
        return bytes(pe.d[o:o + 60]).split(b'\0')[0]

    print u'Encontrado em %08x:' % (pe.imagebase + pe.off2rva(m.start()))
    print u'  FindWindowA("%s", "%s") -- a janela de qualquer servidor' \
          % (literal(janela1), literal(janela2))
    print u'  caixa com titulo "%s" e texto vazio (a chave "alreadyclient" ' \
          u'nao existe no MsgString.lub)' % literal(caixa)

    cave_off, cave_rva, cave_tam = cave_livre(pe)
    escritas, p = [], 0
    for texto in (NOME_DA_JANELA, TITULO_DA_CAIXA, TEXTO_DA_CAIXA):
        escritas.append((cave_off + p, cave_rva + p, texto))
        p += (len(texto) + 4) & ~3
    if p > cave_tam:
        raise Erro(u'faltam %d bytes no cave (%d livres)' % (p - cave_tam, cave_tam))
    end_janela, end_titulo, end_texto = [pe.imagebase + rva for _, rva, _ in escritas]

    # Offsets contados do inicio do casamento, que e o primeiro push:
    #   +0 push imm32 | +5 push imm32 | +10 call | +16 test | +18 je
    #   +20 push 0    | +22 push imm32 (titulo)  | +27 o bloco de 22 bytes
    off_push1 = m.start() + 1
    off_push2 = m.start() + 6
    off_caption = m.start() + 23
    off_bloco = m.start() + 27

    print u'\nAlteracoes:'
    print u'  push@%08x e push@%08x  -> "%s"  (rva %08x)' \
          % (pe.imagebase + pe.off2rva(off_push1),
             pe.imagebase + pe.off2rva(off_push2),
             NOME_DA_JANELA, escritas[0][1])
    print u'  push@%08x  titulo da caixa -> "%s"' \
          % (pe.imagebase + pe.off2rva(off_caption), TITULO_DA_CAIXA)
    print u'  %d bytes em %08x  -> push do texto + %d NOP' \
          % (TAM_BLOCO_DO_TEXTO, pe.imagebase + pe.off2rva(off_bloco),
             TAM_BLOCO_DO_TEXTO - 5)
    print u'  strings novas no fim de .text: %d bytes a partir do rva %08x' \
          % (p, cave_rva)

    if verificar:
        print u'\n--verificar: nenhum byte foi gravado.'
        return

    backup = '%s.BACKUP-%s' % (path, time.strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(path, backup)
    print u'\nBackup: %s' % os.path.basename(backup)

    for off, rva, texto in escritas:
        pe.d[off:off + len(texto) + 1] = texto + b'\0'
    struct.pack_into('<I', pe.d, off_push1, end_janela)
    struct.pack_into('<I', pe.d, off_push2, end_janela)
    struct.pack_into('<I', pe.d, off_caption, end_titulo)
    novo = b'\x68' + struct.pack('<I', end_texto) + NOP * (TAM_BLOCO_DO_TEXTO - 5)
    pe.d[off_bloco:off_bloco + TAM_BLOCO_DO_TEXTO] = novo

    if pe.u32(pe.checksum_off):
        struct.pack_into('<I', pe.d, pe.checksum_off, 0)
        struct.pack_into('<I', pe.d, pe.checksum_off, pe.checksum())

    with open(path, 'wb') as fp:
        fp.write(bytes(pe.d))
    print u'Gravado: %s' % path


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        print __doc__
        sys.exit(1)
    try:
        aplica(args[0], '--verificar' in sys.argv)
    except Erro as e:
        print u'ERRO: %s' % e
        sys.exit(1)
