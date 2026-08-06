# -*- coding: utf-8 -*-
u"""Aumenta o tamanho de TODA fonte que o cliente desenha.

    python ajusta_tamanho_fonte.py --verificar   # so relata
    python ajusta_tamanho_fonte.py               # aplica +2 (faz backup)
    python ajusta_tamanho_fonte.py --aumento 4   # aplica outro valor
    python ajusta_tamanho_fonte.py --reverter    # volta ao original

------------------------------------------------------------------ o problema

A fonte do jogo e pequena demais para ler confortavel. E o cliente NAO tem
opcao de tamanho de fonte: nem no Setup.exe, nem no menu de opcoes, nem no
`OptionInfo.lua` (a lista inteira de chaves que ele grava esta em
`data/luafiles514/lua files/optioninfo/optioninfo.lub`, e nao ha nenhuma de
fonte). O `/font` que existe na lista de comandos e outra coisa - e o comando
de trocar a fonte do CHAT por uma das `.eot` de `System/Font`.

Nao existe pequeno/medio/grande para escolher. O que existe e a altura em
pixels que o cliente pede ao Windows, e e nela que este script mexe. Por isso
o valor default e +2: e um degrau, nao um salto - o layout da interface do RO
e de tamanho fixo, e fonte grande demais transborda das caixas.

O tamanho de partida esta no proprio binario, em `push 0Dh` logo antes da
chamada: a fonte principal e altura de CARACTERE 13. Com +2 ela vai a 15, uns
15% maior - de "pequeno" para "medio". As outras chamadas recebem a altura por
variavel, e sobem os mesmos 2 pixels.

------------------------------------------------------------------ o caminho

O caminho obvio - o patch `CustomFontHgtOffset` do WARP - **nao serve para
este cliente, e a razao vale registro** porque e a mesma da armadilha do
`FixFontsCharset` (ver `ajusta_charset_fonte.py`): ele aplica sem erro e nao
muda nada.

O FONTAIN do WARP (`Scripts/Init/FontUpdater.mjs`) desvia os call sites de
`CreateFontA` para um cave que soma na altura. Só que:

    CreateFontA           importado, e chamado ZERO vezes
    CreateFontIndirectA   importado, e chamado 8 vezes

Este cliente cria **toda** fonte pelo `CreateFontIndirectA`, que nao recebe a
altura como argumento solto e sim dentro de um `LOGFONTA`. O FONTAIN nao tem
nada para desviar, escreve zero bytes e responde sucesso. Foi tambem o que
aconteceu com o `CustomFontCharset` na fase do charset - mesma causa, e la
demorou a aparecer.

------------------------------------------------------------------ a correcao

Os 8 call sites viram `call` para um stub nosso, que soma na altura ANTES de
deixar a chamada seguir:

    push eax
    mov  eax, [esp+8]        ; o LOGFONTA* que o chamador empilhou
    cmp  dword ptr [eax], 0  ; lfHeight, no offset 0 da struct
    jge  positivo
    sub  dword ptr [eax], N  ; altura de CARACTERE: negativa, cresce descendo
    jmp  pronto
    positivo:
    add  dword ptr [eax], N  ; altura de CELULA: positiva, cresce subindo
    pronto:
    pop  eax
    jmp  dword ptr [CreateFontIndirectA]

O sinal do `lfHeight` nao e detalhe: negativo quer dizer altura do CARACTERE e
positivo altura da CELULA (documentacao do LOGFONT). Somar cegamente
diminuiria a fonte na metade dos casos. Este cliente usa negativo nos 8, mas o
stub trata os dois - custa tres instrucoes e nao ha por que apostar.

Modificar o LOGFONTA no lugar, sem copia, e seguro **porque foi conferido**:
nos 8 sites o chamador monta a struct na pilha (`lea eax,[ebp-XX]; push eax`)
e escreve o `lfHeight` na instrucao imediatamente anterior. Nao ha struct
global reaproveitada entre chamadas, entao a soma nao se acumula.

O stub vai para o fim da secao `.xdiff` - a secao que o proprio WARP criou
para os caves dele, que e executavel e gravavel. Os caves do WARP ocupam ate
~0x320; o resto dos 0x400 esta zerado, e o script procura o espaco livre em
vez de fixar endereco.

Duas coisas que so nao quebram por sorte medida, e ficam registradas:
o exe **nao tem ASLR** (`DllCharacteristics` sem DYNAMICBASE), entao endereco
absoluto no stub vale; e `call [IAT]` ocupa 6 bytes contra 5 do `call rel32`,
entao sobra exatamente um byte para o `nop` - nao ha aperto.

Idempotente, com backup, e `--reverter` desfaz. Roda em Python 2.7.
"""
import os
import struct
import sys
import time

EXE_PADRAO = os.path.join(r'C:\GuerraDoEmperium\cliente',
                          'GuerraDoEmperium.exe')

AUMENTO_PADRAO = 2      # um degrau: "medio", nao "grande"
AUMENTO_MAX = 20        # acima disso a interface do RO transborda feio

ALVO = 'CreateFontIndirectA'


class Erro(Exception):
    pass


# ------------------------------------------------------------------ o PE

class PE(object):
    def __init__(self, d):
        self.d = d
        pe = struct.unpack('<I', str(d[0x3c:0x40]))[0]
        nsec = struct.unpack('<H', str(d[pe + 6:pe + 8]))[0]
        optsz = struct.unpack('<H', str(d[pe + 20:pe + 22]))[0]
        opt = pe + 24
        self.base = struct.unpack('<I', str(d[opt + 28:opt + 32]))[0]
        self.csoff = opt + 64
        ndir = struct.unpack('<I', str(d[opt + 92:opt + 96]))[0]
        self.dirs = [struct.unpack('<II', str(d[opt + 96 + i * 8:
                                                opt + 104 + i * 8]))
                     for i in range(ndir)]
        self.secs = []
        so = opt + optsz
        for i in range(nsec):
            h = str(d[so + i * 40:so + (i + 1) * 40])
            vsz, va, rsz, raw = struct.unpack('<IIII', h[8:24])
            self.secs.append(dict(nome=h[0:8].rstrip('\x00'), vsz=vsz, va=va,
                                  rsz=rsz, raw=raw))

    def off(self, rva):
        for s in self.secs:
            if s['va'] <= rva < s['va'] + max(s['vsz'], s['rsz']):
                return s['raw'] + (rva - s['va'])
        return None

    def va2off(self, va):
        return self.off(va - self.base)

    def off2va(self, off):
        for s in self.secs:
            if s['raw'] <= off < s['raw'] + s['rsz']:
                return self.base + s['va'] + (off - s['raw'])
        return None

    def secao(self, nome):
        for s in self.secs:
            if s['nome'] == nome:
                return s
        raise Erro('nao achei a secao %s' % nome)

    def iat(self, funcao):
        u"""VA da entrada da IAT da funcao importada, ou None."""
        off = self.off(self.dirs[1][0])
        d = str(self.d)
        i = 0
        while True:
            oft, _ts, _fc, nm, ft = struct.unpack(
                '<IIIII', d[off + i * 20:off + (i + 1) * 20])
            if nm == 0:
                return None
            t = oft or ft
            to = self.off(t)
            j = 0
            while True:
                v = struct.unpack('<I', d[to + j * 4:to + j * 4 + 4])[0]
                if v == 0:
                    break
                if not (v & 0x80000000):
                    no = self.off(v)
                    nome = d[no + 2:d.index('\x00', no + 2)]
                    if nome == funcao:
                        return self.base + ft + j * 4
                j += 1
            i += 1


def checksum(d, off):
    u"""Checksum do PE, igual ao CheckSumMappedFile. Os 4 bytes do proprio
    campo entram como zero. Copia da funcao do `ajusta_charset_fonte.py` - o
    WARP mantem o checksum dele, entao mantemos tambem."""
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


# ------------------------------------------------------------------ o stub

def stub(iat, n):
    u"""Os 25 bytes do desvio. Ver a secao "a correcao" do cabecalho."""
    return ('\x50'                              # push eax
            '\x8b\x44\x24\x08'                  # mov eax, [esp+8]
            '\x83\x38\x00'                      # cmp dword ptr [eax], 0
            '\x7d\x05'                          # jge positivo
            '\x83\x28' + chr(n) +               # sub dword ptr [eax], n
            '\xeb\x03'                          # jmp pronto
            '\x83\x00' + chr(n) +               # add dword ptr [eax], n
            '\x58'                              # pop eax
            '\xff\x25' + struct.pack('<I', iat))  # jmp dword ptr [iat]


TAM_STUB = 25
OFF_N1 = 12         # onde o N do `sub` mora, dentro do stub
OFF_N2 = 17         # e o do `add`


def parece_stub(bytes_, iat):
    u"""E um stub nosso? Compara tudo menos os dois bytes do N."""
    if len(bytes_) < TAM_STUB:
        return False
    molde = stub(iat, ord(bytes_[OFF_N1]))
    return (bytes_[:TAM_STUB] == molde
            and bytes_[OFF_N1] == bytes_[OFF_N2])


def acha_livre(pe, quanto):
    u"""Offset de arquivo de um trecho zerado no fim da `.xdiff`.

    Procura o espaco em vez de fixar endereco: os caves do WARP ocupam a
    parte de baixo da secao, e quanto eles ocupam depende de quais patches
    foram aplicados.
    """
    s = pe.secao('.xdiff')
    bloco = str(pe.d[s['raw']:s['raw'] + s['rsz']])
    fim = len(bloco.rstrip('\x00'))
    inicio = (fim + 15) & ~15           # alinhado, com folga do ultimo cave
    if inicio + quanto > len(bloco):
        raise Erro('nao ha %d bytes livres na .xdiff' % quanto)
    return s['raw'] + inicio


# ------------------------------------------------------------------ o estado

def sites(pe, iat):
    u"""Offsets dos `call [CreateFontIndirectA]` ainda originais."""
    alvo = '\xff\x15' + struct.pack('<I', iat)
    d = str(pe.d)
    res, pos = [], 0
    while True:
        i = d.find(alvo, pos)
        if i < 0:
            return res
        res.append(i)
        pos = i + 1


def desviados(pe, iat):
    u"""[(offset do call, offset do stub)] dos sites ja patchados por nos.

    Reconhece pelo formato: `call rel32` cujo destino tem o molde do stub. Nao
    guarda endereco em lugar nenhum - o proprio binario e o registro.
    """
    d = str(pe.d)
    s = pe.secao('.text')
    res = []
    pos = s['raw']
    fim = s['raw'] + s['rsz'] - 5
    while pos < fim:
        i = d.find('\xe8', pos)
        if i < 0 or i >= fim:
            break
        pos = i + 1
        if d[i + 5:i + 6] != '\x90':
            continue
        rel = struct.unpack('<i', d[i + 1:i + 5])[0]
        va = pe.off2va(i)
        if va is None:
            continue
        destino = pe.va2off(va + 5 + rel)
        if destino is None:
            continue
        if parece_stub(d[destino:destino + TAM_STUB], iat):
            res.append((i, destino))
    return res


# ------------------------------------------------------------------ principal

def main(argv):
    verificar = '--verificar' in argv
    reverter = '--reverter' in argv

    aumento = AUMENTO_PADRAO
    if '--aumento' in argv:
        aumento = int(argv[argv.index('--aumento') + 1])
    if reverter:
        aumento = 0
    if not 0 <= aumento <= AUMENTO_MAX:
        raise Erro('aumento fora de 0..%d' % AUMENTO_MAX)

    alvos = [a for a in argv if not a.startswith('--')
             and not a.isdigit()]
    EXE = alvos[0] if alvos else EXE_PADRAO
    if not os.path.exists(EXE):
        raise Erro('nao achei %s' % EXE)

    fh = open(EXE, 'rb')
    d = bytearray(fh.read())
    fh.close()
    pe = PE(d)

    iat = pe.iat(ALVO)
    if iat is None:
        raise Erro('%s nao e importada por este exe' % ALVO)

    originais = sites(pe, iat)
    ja = desviados(pe, iat)
    # `d` e bytearray: indexar da int, nao caractere.
    atual = d[ja[0][1] + OFF_N1] if ja else 0

    print 'exe:      %s' % EXE
    print '%s: IAT em 0x%08X' % (ALVO, iat)
    print 'chamadas: %d originais, %d ja desviadas' % (len(originais), len(ja))
    print 'aumento:  %+d  ->  %+d pixels de altura' % (atual, aumento)

    if not originais and not ja:
        raise Erro('nenhuma chamada a %s neste exe' % ALVO)
    if originais and ja:
        print
        print ('AVISO: o exe esta pela metade - %d chamadas desviadas e %d '
               'nao.' % (len(ja), len(originais)))
        print 'Vou desviar as que faltam tambem.'

    if atual == aumento and not originais:
        print 'Nada a fazer: ja esta assim.'
        return 0
    if aumento == 0 and not ja:
        print 'Nada a fazer: o exe esta original.'
        return 0
    if verificar:
        print '\n--verificar: nenhum byte gravado.'
        return 0

    if aumento == 0:
        # Reverter: o `call rel32 + nop` volta a ser `call [IAT]`, e o stub
        # vira zero de novo - para um --aumento seguinte reaproveitar o espaco.
        for site, alvo_stub in ja:
            d[site:site + 6] = '\xff\x15' + struct.pack('<I', iat)
            d[alvo_stub:alvo_stub + TAM_STUB] = '\x00' * TAM_STUB
        print 'revertidas %d chamadas.' % len(ja)
    else:
        if ja:
            # Ja ha stub: so trocar o N nos dois lugares. Nao criar outro.
            off = ja[0][1]
            d[off + OFF_N1] = chr(aumento)
            d[off + OFF_N2] = chr(aumento)
            print 'stub em 0x%08X: N trocado para %d.' % (pe.off2va(off),
                                                          aumento)
        if originais:
            off = ja[0][1] if ja else acha_livre(pe, TAM_STUB)
            if not ja:
                d[off:off + TAM_STUB] = stub(iat, aumento)
                print 'stub gravado em 0x%08X (.xdiff).' % pe.off2va(off)
            va_stub = pe.off2va(off)
            for site in originais:
                rel = va_stub - (pe.off2va(site) + 5)
                d[site:site + 6] = '\xe8' + struct.pack('<i', rel) + '\x90'
            print 'desviadas %d chamadas.' % len(originais)

    pe = PE(d)          # o checksum le o buffer ja alterado
    if struct.unpack('<I', str(d[pe.csoff:pe.csoff + 4]))[0]:
        struct.pack_into('<I', d, pe.csoff, 0)
        struct.pack_into('<I', d, pe.csoff, checksum(str(d), pe.csoff))
        print 'checksum do PE recalculado.'

    # A troca e por RENOMEACAO, e nao por gravar por cima: o exe fica travado
    # enquanto o cliente roda, e escrever nele da `Permission denied` na hora.
    # Renomear tem chance - foi a manobra do `traduz_setup.py`. Mas o LEIAME
    # registra que com o CLIENTE aberto nem isso passou, ao contrario do
    # Setup.exe. Entao aqui nao ha promessa: se o rename falhar, o `.novo` e
    # apagado, o exe fica intacto e a mensagem diz o que fazer - fechar o
    # cliente. De quebra o backup sai de graca: o arquivo antigo vira ele.
    # Segundos no nome, e nao so minutos como no `ajusta_charset_fonte.py`:
    # aqui o backup NASCE de um rename, e rename para nome existente falha no
    # Windows. Duas rodadas no mesmo minuto sao comuns ao calibrar o valor.
    backup = '%s.BACKUP-fonte-%s' % (EXE, time.strftime('%Y%m%d-%H%M%S'))
    n = 0
    while os.path.exists(backup):
        n += 1
        backup = '%s.BACKUP-fonte-%s-%d' % (EXE,
                                            time.strftime('%Y%m%d-%H%M%S'), n)
    novo = EXE + '.novo'
    fh = open(novo, 'wb')
    fh.write(str(d))
    fh.close()
    try:
        os.rename(EXE, backup)
    except OSError:
        os.remove(novo)
        raise Erro('nao consegui renomear %s - o cliente esta aberto?'
                   % os.path.basename(EXE))
    os.rename(novo, EXE)
    print 'backup: %s' % os.path.basename(backup)
    print 'gravado.'
    print
    print 'Feche e reabra o cliente: o que ja esta aberto roda a copia antiga,'
    print 'que continua na memoria mesmo com o arquivo trocado.'
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Erro, e:
        print >> sys.stderr, 'ERRO: %s' % e
        sys.exit(1)
