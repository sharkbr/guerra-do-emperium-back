# -*- coding: utf-8 -*-
u"""Aumenta o tamanho de toda fonte que o cliente desenha.

    python ajusta_tamanho_fonte.py --verificar   # so relata
    python ajusta_tamanho_fonte.py               # aplica o padrao
    python ajusta_tamanho_fonte.py --bonus 1
    python ajusta_tamanho_fonte.py --teto 16     # ate onde o pedido e respeitado
    python ajusta_tamanho_fonte.py --face Gulim
    python ajusta_tamanho_fonte.py --fixo 20     # uma altura so, para diagnostico
    python ajusta_tamanho_fonte.py --reverter
    python ajusta_tamanho_fonte.py <outro.exe>   # alvo alternativo

A conta e `altura = min(tamanho pedido, --teto) + --bonus`.

**Os padroes ja sao os valores aprovados no jogo** (2026-08-09): face Arial,
`--bonus 0`, `--teto 11`, sem suavizacao. Rodar sem argumento reproduz esse
estado. Como se chegou neles esta em "Tamanho da fonte" no HISTORICO.md - o
resumo e que o tamanho veio de ZERAR o bonus, nao de subir, e que o teto foi
calibrado de 14 para 11 olhando a janela de informacoes basicas.

**`--bonus 0` NAO e o mesmo que `--reverter`.** A face aqui e nossa, nao a do
cliente, e duas faces na mesma altura em pixels nao desenham do mesmo tamanho -
entao `+0` ja e mudanca de tamanho. Foi assim que o ponto certo apareceu em
2026-08-09: nao subindo o bonus, mas zerando ele. Negativo tambem vale, pelo
mesmo motivo. O estado original so volta com `--reverter`.

**Nao existe opcao de tamanho de fonte neste cliente** - nem no Setup.exe, nem
no menu, nem no `OptionInfo.lua`. O `/font` da lista de comandos e outra coisa:
troca a fonte do CHAT por uma das `.eot` de `System/Font`. E resolucao tambem
nao resolve: a interface e de pixel fixo, entao subir a resolucao so deixa tudo
MENOR (medido em 2026-08-09, a 1900x1080).

------------------------------------------------- a versao anterior nao funcionava

Ate 2026-08-09 este arquivo desviava os 8 `CreateFontIndirectA` do exe e somava
na altura do `LOGFONTA`. **Aquilo nao tinha efeito nenhum**, em nenhum valor, e
o script confirmava o proprio trabalho ("8 ja desviadas") porque procurava o
formato do proprio stub. Provado em tres frentes: A/B de capturas entre +2 e
+6 (identicas ao pixel), um stub de diagnostico que forcava SUBLINHADO (nao
apareceu em lugar nenhum) e A/B entre exe patcheado e exe original (identicos).
O detalhe todo esta no HISTORICO.md.

--------------------------------------------------------------- onde e o ponto certo

    0x004C4938  call 0x004C3660    ; pega o HFONT
    0x004C4940  call [SelectObject]
    0x004C494D  call [GetTextExtentPoint32W]   <- MEDE

    0x004C4A6E  call 0x004C3660    ; a MESMA funcao
    0x004C4A79  call [SelectObject]
    0x004C4A89  call [TextOutW]                <- DESENHA

`0x004C3660` e o distribuidor de fontes, e **medicao e desenho tiram a fonte
dele**. Por isso o desvio vai aqui e nao no desenho: fonte trocada so no
desenho daria texto grande medido como pequeno - cortado e sobreposto.

E thiscall (`mov esi,ecx` no prologo), cinco argumentos de [ebp+8] a [ebp+18],
logo `ret 14h`. Devolve HFONT em eax. O **segundo** argumento e o tamanho
pedido - foi medido, comparando a mesma caixa de dialogo com `--fixo` e com
`--bonus`. Por dentro e um cache de entradas de 24 bytes (`mov eax,[eax+10h]`
no acerto), mas nada disso precisa ser preservado: devolvemos a nossa fonte.

**O titulo de janela e os botoes NAO passam por aqui** - saem do outro caminho
de texto (`TextOutA`, em 0x004D83BA) e continuam do tamanho original. Medido:
com o desvio ligado, "Do you agree?" cresce e "message"/"OK"/"cancel" nao.

------------------------------------------------------------------------ a fonte

`CreateFontA` esta importada e tinha ZERO chamadas - livre, sem risco de
atropelar uso existente. Charset 0 (ANSI), o mesmo que o
`ajusta_charset_fonte.py` forcou na tabela e o que faz o acento cp1252
aparecer. Altura NEGATIVA e altura de caractere; positiva seria altura de
celula. A do cliente e 13.

--------------------------------------------------------------------- dois modos

--bonus N  (padrao)  altura = tamanho pedido + N, com cache indexado pelo
                     tamanho. Preserva a proporcao entre titulo, corpo e
                     rodape. O cache e obrigatorio: sem ele cada pedido criaria
                     um HFONT novo e o processo vazaria handles ate cair.

--fixo N             devolve UMA fonte de altura N para todo pedido. Achata as
                     diferencas que o cliente faz de proposito - use so para
                     diagnostico.

**A interface e de caixa fixa.** Bonus alto transborda: em 2026-08-09, com
`--fixo 20`, o painel de selecao de personagem cortou "Interior de Prontera"
em "Interior d" e os valores do inventario se sobrepuseram. Subir de 4 em 4 e
olhar e o caminho.

O exe fica travado enquanto o cliente roda, e o cliente segura o proprio exe
(renomear tambem nao resolve). Fechar e o unico caminho - e o que ja esta
aberto segue na copia em memoria, entao **fechar e reabrir**.
"""
import struct, sys, shutil, datetime

EXE_PADRAO = r"C:\GuerraDoEmperium\cliente\GuerraDoEmperium.exe"

ALVO_VA   = 0x004C3660      # o distribuidor de fontes
CODIGO_VA = 0x013B5390      # o stub, em .xdiff (executavel e gravavel)
TABELA_VA = 0x013B5400      # cache: 64 dwords, indexado pelo tamanho pedido
TABELA_N  = 64
IAT_CREATEFONTA = 0x00DA2048
FACES_VA = {                # strings de face que ja existem dentro do exe
    "Gulim":   0x00DCCC78,
    "Arial":   0x00DCCC80,
    "Tahoma":  0x00DCCCA4,
    "Verdana": 0x00DCCCAC,
}
ORIGINAL_5 = "\x55\x8b\xec\x6a\xff"    # push ebp; mov ebp,esp; push -1


def opcao(nome, padrao):
    return sys.argv[sys.argv.index(nome) + 1] if nome in sys.argv else padrao


def secoes(d):
    pe = struct.unpack_from("<I", d, 0x3c)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    optsz = struct.unpack_from("<H", d, pe + 20)[0]
    opt = pe + 24
    imgbase = struct.unpack_from("<I", d, opt + 28)[0]
    r = []
    for i in range(nsec):
        o = opt + optsz + i * 40
        vsz, va, rsz, ra = struct.unpack_from("<IIII", d, o + 8)
        r.append((va, vsz, ra, rsz))
    return imgbase, r


def main():
    alvos = [a for a in sys.argv[1:] if a.lower().endswith(".exe")]
    exe = alvos[0] if alvos else EXE_PADRAO

    # Os padroes sao os valores calibrados no jogo em 2026-08-09, olhando a
    # tela a cada degrau. Rodar sem argumento reproduz o estado aprovado.
    face = opcao("--face", "Arial")
    fixo = int(opcao("--fixo", "0"))
    bonus = int(opcao("--bonus", "0"))
    if face not in FACES_VA:
        raise SystemExit("face deve ser uma de: %s" % ", ".join(sorted(FACES_VA)))
    teto = int(opcao("--teto", "11"))
    if fixo and not (1 <= fixo <= 99):
        raise SystemExit("--fixo fora de faixa (1 a 99)")
    if not (1 <= teto <= TABELA_N - 1):
        raise SystemExit("--teto fora de faixa (1 a %d)" % (TABELA_N - 1))
    # bonus 0 e negativo sao validos, e nao sao o mesmo que --reverter: a face
    # aqui e NOSSA, nao a do cliente. Duas faces na mesma altura em pixels nao
    # desenham do mesmo tamanho, entao `+0` ja e uma mudanca de tamanho - e
    # pode ser justamente o ponto certo. Ver a nota "nao aumentamos, trocamos".
    if not fixo and not (-8 <= bonus <= 40):
        raise SystemExit("--bonus fora de faixa (-8 a 40)")

    d = bytearray(open(exe, "rb").read())
    imgbase, secs = secoes(str(d))

    def va2off(va):
        r = va - imgbase
        for v, vsz, ra, rsz in secs:
            if v <= r < v + max(vsz, rsz):
                return ra + (r - v)
        raise SystemExit("VA 0x%08X fora das secoes" % va)

    alvo = va2off(ALVO_VA)
    atual = str(d[alvo:alvo + 5])
    ligado = atual[0] == "\xe9"

    print "exe:      %s" % exe
    print "0x%08X: %s  ->  %s" % (
        ALVO_VA, " ".join("%02x" % b for b in d[alvo:alvo + 5]),
        "DESVIADO" if ligado else ("original" if atual == ORIGINAL_5 else "??? "))

    if not ligado and atual != ORIGINAL_5:
        raise SystemExit("prologo inesperado - exe diferente do esperado, nada feito")

    if "--verificar" in sys.argv:
        if ligado:
            cod = va2off(CODIGO_VA)
            print "stub em 0x%08X: %s ..." % (
                CODIGO_VA, " ".join("%02x" % b for b in d[cod:cod + 12]))
        print "--verificar: nenhum byte gravado."
        return

    carimbo = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    if "--reverter" in sys.argv:
        if not ligado:
            print "Nada a fazer: ja esta original."
            return
        shutil.copy2(exe, exe + ".BACKUP-fonte-" + carimbo)
        d[alvo:alvo + 5] = ORIGINAL_5
        open(exe, "wb").write(str(d))
        print "revertido. backup: %s" % (exe + ".BACKUP-fonte-" + carimbo)
        return

    # ----------------------------------------------------------------- o stub
    # entrada: ecx = this (ignorado); [esp+4..+14h] = os cinco argumentos
    def criar_fonte(push_altura):
        u"""Os 14 argumentos de CreateFontA, empilhados da direita para a esquerda.

        `iQuality` = 3 (NONANTIALIASED_QUALITY) NAO e detalhe de gosto. Com o
        DEFAULT_QUALITY o Windows aplica ClearType, que suaviza a borda por
        subpixel - vermelho de um lado, azul do outro. O cliente rasteriza o
        texto num DIB e compoe como textura, e nessa composicao o franjado
        colorido vira um **contorno rosa** em volta de cada letra. Visto em
        2026-08-09: "Abernus", que e preto, saiu magenta. A fonte original do
        cliente nao e suavizada, e e por isso que ela e nitida.
        """
        return ("\x68" + struct.pack("<I", FACES_VA[face]) +   # pszFaceName
                "\x6a\x00" +            # iPitchAndFamily = DEFAULT_PITCH
                "\x6a\x03" +            # iQuality = NONANTIALIASED_QUALITY
                "\x6a\x00" +            # iClipPrecision
                "\x6a\x00" +            # iOutPrecision
                "\x6a\x00" +            # iCharSet = ANSI_CHARSET
                "\x6a\x00" * 3 +        # bStrikeOut, bUnderline, bItalic
                "\x68" + struct.pack("<I", 400) +              # cWeight = FW_NORMAL
                "\x6a\x00" * 3 +        # cOrientation, cEscapement, cWidth
                push_altura +           # cHeight
                "\xff\x15" + struct.pack("<I", IAT_CREATEFONTA))

    # Teto no tamanho PEDIDO, aplicado antes de indexar o cache.
    #
    # Existe porque algumas linhas pedem um corpo bem maior que o resto - na
    # janela de informacoes basicas, HP/SP, Base Lv., Job Lv. e a linha de peso
    # e zeny. Essa hierarquia e do proprio cliente e ja existia antes de
    # qualquer patch (conferido contra captura do estado original), mas a nossa
    # face desenha maior na mesma altura pedida, entao a diferenca ficava
    # exagerada. O teto segura esses poucos casos e deixa o resto passar
    # intacto.
    #
    # A comparacao e SEM SINAL de proposito: valor negativo ou lixo vira um
    # numero enorme e tambem cai no teto. E o outro motivo deste trecho existir
    # - o indice do cache tem de ficar dentro da tabela, sempre.
    limita = ("\x83\xfa" + chr(teto) +                # cmp edx, teto
              "\x76\x05" +                            # jbe +5
              "\xba" + struct.pack("<I", teto))       # mov edx, teto

    if fixo:
        corpo = (criar_fonte("\x6a" + struct.pack("<b", -fixo)) +
                 "\xa3" + struct.pack("<I", TABELA_VA))        # mov [tabela], eax
        stub = ("\xa1" + struct.pack("<I", TABELA_VA) +        # mov eax,[tabela]
                "\x85\xc0" +                                   # test eax,eax
                "\x75" + struct.pack("<b", len(corpo)) +       # jnz pronto
                corpo + "\xc2\x14\x00")                        # ret 14h
        como = "fixo: altura %d para todo pedido" % fixo
    else:
        corpo = ("\x8d\x4a" + struct.pack("<b", bonus) +       # lea ecx,[edx+bonus]
                 "\xf7\xd9" +                                  # neg ecx
                 criar_fonte("\x51") +                         # push ecx (cHeight)
                 "\x8b\x54\x24\x08" + limita +                 # recarrega e limita edx
                 "\x89\x04\x95" + struct.pack("<I", TABELA_VA))
        stub = ("\x8b\x54\x24\x08" +                           # mov edx,[esp+8]
                limita +
                "\x8b\x04\x95" + struct.pack("<I", TABELA_VA) +
                "\x85\xc0" +                                   # test eax,eax
                "\x75" + struct.pack("<b", len(corpo)) +       # jnz pronto
                corpo + "\xc2\x14\x00")                        # ret 14h
        como = "escala: altura = min(pedido, %d) + %d" % (teto, bonus)

    shutil.copy2(exe, exe + ".BACKUP-fonte-" + carimbo)
    tab = va2off(TABELA_VA)
    cod = va2off(CODIGO_VA)
    d[tab:tab + TABELA_N * 4] = "\x00" * (TABELA_N * 4)
    d[cod:cod + 160] = "\x00" * 160
    d[cod:cod + len(stub)] = stub
    d[alvo:alvo + 5] = "\xe9" + struct.pack("<i", CODIGO_VA - (ALVO_VA + 5))
    open(exe, "wb").write(str(d))

    print "face %s | %s   (a altura do cliente e 13)" % (face, como)
    print "stub 0x%08X, %d bytes" % (CODIGO_VA, len(stub))
    print "backup: %s" % (exe + ".BACKUP-fonte-" + carimbo)
    print
    print "Feche e reabra o cliente: o que ja esta aberto roda a copia antiga,"
    print "que continua na memoria mesmo com o arquivo trocado."


main()
