# -*- coding: utf-8 -*-
"""Ensina o exe a abrir a roleta da captura de pet quando o SERVIDOR pede.

    python abre_roleta_do_cassino.py              # diz se o exe ja tem o desvio
    python abre_roleta_do_cassino.py --aplicar    # patcheia (guarda backup ao lado)
    python abre_roleta_do_cassino.py --reverter   # volta ao backup
    python abre_roleta_do_cassino.py --mostrar    # desmonta o desvio (pede capstone)

PARA QUE SERVE. A roleta do cassino (npc/guerra/roleta_do_cassino.txt) usa a
janela que o cliente desenha ao capturar um monstro. O servidor nao tem como
abri-la: quem abre e o proprio cliente, no clique do cursor de captura sobre o
monstro. O pacote de resultado (0x1a0, ZC_TRYCAPTURE_MONSTER) so atualiza uma
janela que ja esteja aberta - com ela fechada, cai no vazio. O caso inteiro, e
o lado do servidor, esta em rathena/src/custom/roleta_do_cassino.hpp.

O QUE O EXE FAZ HOJE (medido em 2026-09-26, capstone). O tratador do 0x1a0:

    007f9160  push ebp / mov ebp,esp
    007f9163  mov  eax, [ebp+8]            ; o pacote
    007f9166  mov  ecx, [0x00f816c4]       ; a janela 0x5b, ou 0
    007f916c  cmp  byte [eax+2], 0         ; resultado
    007f9170  je   perdeu                  ;   -> SendMsg(0x50, 1, 3)
    ...                                    ;   ganhou -> SendMsg(0x50, 1, 7)
                                           ;   (o quadro onde a roleta para)

A janela e a UIPetTamingDeceiveWnd, id 0x5b; quem a cria e o
`MakeWindow` 0x00629610 (ecx = 0x00f81370, o gerenciador de janelas). O
caminho de captura faz, depois do clique no monstro:

    push 0x5b / mov ecx, 0xf81370 / call 0x629610      ; abre, girando
    SendMsg(0, 0x50, 0, <id do alvo>, 0, 0)            ; guarda o alvo (+0xa0)

O DESVIO. Os 6 bytes do `mov ecx, [0xf816c4]` viram um `jmp` para 0x013B5700,
na `.xdiff`, onde o mesmo `mov` e refeito e entao:

  - resultado 2 (que o rAthena nunca manda) e janela fechada: abre a janela
    como a captura abre, com alvo 0, e sai. O clique nela manda 0x19f com 0,
    e o servidor reconhece como a roleta do cassino.
  - resultado 0/1 e janela aberta: antes de seguir para o tratador original,
    marca a janela como CLICADA (+0x98 = 1, a animacao de frear; +0xb0 = 1, a
    trava do clique). Na captura isso ja esta assim e nada muda. No cassino,
    e o que faz os 10 segundos sem clique pararem a roleta igual a um clique:
    sem isso ela pararia no quadro da animacao OCIOSA, e um clique atrasado
    ainda trocaria o quadro de parada para 7 - "ganhou" na tela de quem
    perdeu (o tratador do clique, 0x0057fcf0, grava +0xa4 = 7 sem olhar nada).

A `.xdiff` CRESCE EM DISCO. Ela tem 0x1000 de tamanho virtual e so 0x400 vindo
do arquivo (a armadilha do CLAUDE.md secao 5): nao ha como por codigo acima de
0x013B5400 sem aumentar o `SizeOfRawData`. O maior vao livre na metade que vem
do arquivo tem 41 bytes, e o desvio tem 87. Por isso:

  - `SizeOfRawData` da `.xdiff` 0x400 -> 0x800, e o arquivo cresce ate o novo
    fim (0x00C4CE00). Ela e a ULTIMA secao, entao nada anda de lugar; o que
    havia depois dela no arquivo eram 256 zeros.
  - o cache de HFONT do ajusta_tamanho_fonte.py (0x013B5400, 256 bytes) passa
    a vir do arquivo, e vem ZERO, que e o estado inicial de que ele precisa.
    O script confere que a faixa esta zerada antes de mexer.
  - o desvio mora em 0x013B5700..0x013B5757 (87 bytes). Nenhum `e8`/`e9` do exe salta
    para 0x013B5500..0x013B6000 e nenhuma constante aponta para la
    (varridos em 2026-09-26; os tres "acertos" da varredura cairam em
    `.reloc` e no meio de instrucao).

POR PADRAO DE BYTES: o tratador e achado pelos 22 bytes do comeco dele e tem
de aparecer EXATAMENTE uma vez. Os enderecos que o desvio chama (MakeWindow,
gerenciador, ponteiro da janela) sao conferidos contra o proprio caminho de
captura do exe, que tambem e achado por padrao. Exe de outra versao da zero
acertos e o script recusa.

Depois: e mudanca de CLIENTE, vai por patch (CLAUDE.md 4.18) - e o exe so se
grava com o cliente FECHADO. O .epi do NEMO nao sabe deste desvio: exe
regravado pelo NEMO volta sem ele, e este script diz.

Roda em Python 2.7.
"""
import os
import shutil
import struct
import sys

EXE = r'C:\GuerraDoEmperium\cliente\GuerraDoEmperium.exe'
BACKUP = EXE + '.antes-de-abre_roleta_do_cassino'

# O comeco do tratador do 0x1a0, ate o segundo `je` - ja com o mov ecx.
TRATADOR = '558bec8b45088b0dc416f80080780200741c85c97430'.decode('hex')
TRATADOR_MOV = 6            # onde comeca o `mov ecx, [janela]` dentro dele

# O caminho de captura: push 0x5b / mov ecx, gerenciador / call MakeWindow.
# Prova que os tres enderecos abaixo sao os deste exe.
CAPTURA = '6a5bb97013f800e8'.decode('hex')

JANELA_PTR = 0x00F816C4     # onde o gerenciador guarda a janela 0x5b
GERENCIADOR = 0x00F81370
MAKEWINDOW = 0x00629610
ID_JANELA = 0x5B

CAVERNA_VA = 0x013B5700
XDIFF_RAW_ANTES = 0x400
XDIFF_RAW_DEPOIS = 0x800


def secoes(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    opt = pe + 24
    base = struct.unpack_from('<I', d, opt + 28)[0]
    so = struct.unpack_from('<H', d, pe + 20)[0]
    out = []
    for i in range(n):
        h = opt + so + i * 40
        vs, va, rs, ra = struct.unpack_from('<IIII', d, h + 8)
        out.append({'nome': d[h:h + 8].rstrip('\0'), 'h': h,
                    'va': base + va, 'vs': vs, 'ra': ra, 'rs': rs})
    return base, out


def para_arquivo(secs, va):
    for s in secs:
        if s['va'] <= va < s['va'] + s['rs']:
            return s['ra'] + va - s['va']
    return None


def para_va(secs, o):
    for s in secs:
        if s['ra'] <= o < s['ra'] + s['rs']:
            return s['va'] + o - s['ra']
    return None


def rel32(de, para):
    """Deslocamento de um e8/e9 que COMECA em `de` (5 bytes) ate `para`."""
    return struct.pack('<i', para - (de + 5))


def monta_caverna(volta_va):
    """O desvio, montado a mao. Os rotulos sao resolvidos em duas passadas."""
    c = CAVERNA_VA
    b = ''
    b += '\x8b\x0d' + struct.pack('<I', JANELA_PTR)   # mov ecx, [janela]
    b += '\x80\x78\x02\x02'                           # cmp byte [eax+2], 2
    b += '\x75' + '{FECHA}'                           # jne FECHA
    b += '\x85\xc9'                                   # test ecx, ecx
    b += '\x75' + '{SAI}'                             # jne SAI  (ja aberta)
    b += '\x6a' + chr(ID_JANELA)                      # push 0x5b
    b += '\xb9' + struct.pack('<I', GERENCIADOR)      # mov ecx, gerenciador
    b += '\xe8' + '{MAKEWINDOW}'                      # call MakeWindow
    b += '\x85\xc0'                                   # test eax, eax
    b += '\x74' + '{SAI}'                             # je SAI
    b += '\x8b\xc8'                                   # mov ecx, eax
    b += '\x8b\x10'                                   # mov edx, [eax]
    b += '\x6a\x00' * 4                               # push 0 (x4: alvo 0)
    b += '\x6a\x50'                                   # push 0x50
    b += '\x6a\x00'                                   # push 0
    b += '\xff\x92\x88\x00\x00\x00'                   # call [edx+0x88] SendMsg
    b += '{L:SAI}'
    b += '\x5d'                                       # pop ebp
    b += '\xc2\x04\x00'                               # ret 4
    b += '{L:FECHA}'
    b += '\x85\xc9'                                   # test ecx, ecx
    b += '\x74\x14'                                   # je VOLTA (20 bytes)
    b += '\xc7\x81\x98\x00\x00\x00\x01\x00\x00\x00'   # mov [ecx+0x98], 1
    b += '\xc7\x81\xb0\x00\x00\x00\x01\x00\x00\x00'   # mov [ecx+0xb0], 1
    b += '\xe9' + '{VOLTA}'                           # jmp de volta

    # Primeira passada: posicoes, com cada marcador no tamanho final.
    tam = {'{FECHA}': 1, '{SAI}': 1, '{MAKEWINDOW}': 4, '{VOLTA}': 4}
    rotulo = {}
    pos = 0
    i = 0
    partes = []
    while i < len(b):
        if b[i] == '{':
            j = b.index('}', i) + 1
            m = b[i:j]
            if m.startswith('{L:'):
                rotulo[m[3:-1]] = pos
            else:
                partes.append((pos, m))
                pos += tam[m]
            i = j
        else:
            pos += 1
            i += 1

    # Segunda passada: preenche.
    out = ''
    i = 0
    while i < len(b):
        if b[i] == '{':
            j = b.index('}', i) + 1
            m = b[i:j]
            if not m.startswith('{L:'):
                aqui = len(out)
                if m == '{MAKEWINDOW}':
                    out += rel32(c + aqui - 1, MAKEWINDOW)
                elif m == '{VOLTA}':
                    out += rel32(c + aqui - 1, volta_va)
                else:
                    salto = rotulo[m[1:-1]] - (aqui + 1)
                    assert -128 <= salto < 128
                    out += struct.pack('<b', salto)
            i = j
        else:
            out += b[i]
            i += 1
    assert len(out) == pos
    return out


def acha_tudo(d):
    base, secs = secoes(d)
    x = [s for s in secs if s['nome'] == '.xdiff']
    if len(x) != 1 or x[0] is not secs[-1]:
        return None, 'a .xdiff nao e a ultima secao'
    x = x[0]

    hits = []
    i = d.find(TRATADOR)
    while i >= 0:
        hits.append(i)
        i = d.find(TRATADOR, i + 1)

    ok_captura = False
    i = d.find(CAPTURA)
    while i >= 0:
        de = para_va(secs, i + len(CAPTURA) - 1)
        alvo = de + 5 + struct.unpack_from('<i', d, i + len(CAPTURA))[0]
        if alvo == MAKEWINDOW:
            ok_captura = True
        i = d.find(CAPTURA, i + 1)
    if not ok_captura:
        return None, 'o caminho de captura nao chama MakeWindow em 0x%x' % MAKEWINDOW

    return {'secs': secs, 'x': x, 'tratador': hits}, None


def estado(d):
    info, erro = acha_tudo(d)
    if erro:
        return 'estranho', erro, None
    x = info['x']
    hits = info['tratador']
    if len(hits) != 1:
        return 'estranho', 'tratador do 0x1a0 achado %d vezes' % len(hits), info
    mov = hits[0] + TRATADOR_MOV
    if x['rs'] == XDIFF_RAW_DEPOIS:
        return 'aplicado?', 'a .xdiff ja cresceu, mas o tratador esta original', info
    return 'original', None, info


def aplicado(d):
    """Procura o tratador ja desviado: o jmp no lugar do mov."""
    base, secs = secoes(d)
    antes = TRATADOR[:TRATADOR_MOV]
    depois = TRATADOR[TRATADOR_MOV + 6:]
    i = d.find(antes + '\xe9')
    while i >= 0:
        j = i + TRATADOR_MOV
        if d[j + 5] == '\x90' and d[j + 6:j + 6 + len(depois)] == depois:
            de = para_va(secs, j)
            if de + 5 + struct.unpack_from('<i', d, j + 1)[0] == CAVERNA_VA:
                return j
        i = d.find(antes + '\xe9', i + 1)
    return None


def aplica(d):
    info, erro = acha_tudo(d)
    if erro:
        return None, erro
    secs, x = info['secs'], info['x']
    if len(info['tratador']) != 1:
        return None, 'tratador do 0x1a0 achado %d vezes; esperava 1' % len(info['tratador'])
    if x['rs'] != XDIFF_RAW_ANTES:
        return None, '.xdiff com SizeOfRawData 0x%x; esperava 0x%x' % (x['rs'], XDIFF_RAW_ANTES)

    fim_antes = x['ra'] + XDIFF_RAW_ANTES
    fim_depois = x['ra'] + XDIFF_RAW_DEPOIS
    if len(d) > fim_depois:
        return None, 'o arquivo passa do novo fim da .xdiff (0x%x > 0x%x)' % (len(d), fim_depois)
    if d[fim_antes:].strip('\0'):
        return None, 'ha bytes nao-zero depois da .xdiff; nao sei o que sao'

    # Cresce a secao: arquivo ate o novo fim, cabecalho com o novo tamanho.
    d = d + '\0' * (fim_depois - len(d))
    d = d[:x['h'] + 16] + struct.pack('<I', XDIFF_RAW_DEPOIS) + d[x['h'] + 20:]
    x['rs'] = XDIFF_RAW_DEPOIS

    mov = info['tratador'][0] + TRATADOR_MOV
    mov_va = para_va(secs, mov)
    caverna = monta_caverna(mov_va + 6)
    co = para_arquivo(secs, CAVERNA_VA)
    if co is None or d[co:co + len(caverna)].strip('\0'):
        return None, 'a caverna em 0x%x nao esta livre' % CAVERNA_VA
    # O cache de HFONT (ajusta_tamanho_fonte.py) tem de nascer zero.
    cache = para_arquivo(secs, 0x013B5400)
    if d[cache:cache + 0x100].strip('\0'):
        return None, 'a faixa do cache de HFONT nao esta zerada'

    d = d[:co] + caverna + d[co + len(caverna):]
    salto = '\xe9' + rel32(mov_va, CAVERNA_VA) + '\x90'
    d = d[:mov] + salto + d[mov + 6:]
    return d, None


def mostra(d):
    try:
        import capstone
    except ImportError:
        print 'sem capstone (pip install capstone==4.0.2)'
        return
    base, secs = secoes(d)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    j = aplicado(d)
    if j is None:
        print 'desvio nao aplicado'
        return
    for va, n in ((para_va(secs, j) - 6, 32), (CAVERNA_VA, 0x57)):
        o = para_arquivo(secs, va)
        print '---- 0x%08x' % va
        for ins in md.disasm(d[o:o + n], va):
            print '  %08x  %-6s %s' % (ins.address, ins.mnemonic, ins.op_str)


def main():
    d = open(EXE, 'rb').read()
    j = aplicado(d)

    if '--mostrar' in sys.argv:
        mostra(d)
        return 0

    if '--reverter' in sys.argv:
        if j is None:
            print 'o exe nao tem o desvio; nada a reverter'
            return 1
        if not os.path.exists(BACKUP):
            print 'sem backup em %s' % BACKUP
            return 1
        shutil.copy2(BACKUP, EXE)
        print 'exe devolvido do backup'
        return 0

    if '--aplicar' in sys.argv:
        if j is not None:
            print 'o exe ja tem o desvio (0x%x); nada a fazer' % j
            return 0
        novo, erro = aplica(d)
        if erro:
            print 'nao mexo: ' + erro
            return 1
        if not os.path.exists(BACKUP):
            shutil.copy2(EXE, BACKUP)
            print 'backup em %s' % BACKUP
        open(EXE, 'wb').write(novo)
        if aplicado(open(EXE, 'rb').read()) is None:
            print 'gravei e nao reachei o desvio - algo esta errado'
            return 1
        print 'desvio aplicado: 0x1a0 com resultado 2 abre a roleta'
        return 0

    if j is not None:
        print 'exe COM o desvio da roleta do cassino'
        return 0
    st, erro, _ = estado(d)
    print 'exe SEM o desvio (%s)%s' % (st, ': ' + erro if erro else '')
    return 1


if __name__ == '__main__':
    sys.exit(main())
