# -*- coding: utf-8 -*-
u"""Ajusta o tamanho e o peso de toda fonte que o cliente desenha.

    python ajusta_tamanho_fonte.py --verificar   # so relata
    python ajusta_tamanho_fonte.py               # aplica o padrao
    python ajusta_tamanho_fonte.py --mapa        # imprime a tabela de alturas
    python ajusta_tamanho_fonte.py --tabela      # LE o cliente NO AR: que tamanhos ele pediu
    python ajusta_tamanho_fonte.py --bonus 1
    python ajusta_tamanho_fonte.py --teto 16     # ate onde o pedido e achatado
    python ajusta_tamanho_fonte.py --livre 15    # daqui para cima o pedido passa intacto
    python ajusta_tamanho_fonte.py --altura 48=42   # so este pedido, esta altura
    python ajusta_tamanho_fonte.py --negrito 48,17  # estes pedidos saem em negrito
    python ajusta_tamanho_fonte.py --face Gulim
    python ajusta_tamanho_fonte.py --fixo 20     # uma altura so, para diagnostico
    python ajusta_tamanho_fonte.py --reverter
    python ajusta_tamanho_fonte.py <outro.exe>   # alvo alternativo

A altura de cada tamanho pedido sai de uma tabela de 64 bytes gravada no exe -
o stub le, nao calcula. A tabela e montada assim, nesta ordem:

    pedido <  --livre   ->  altura = min(pedido, --teto) + --bonus
    pedido >= --livre   ->  altura = pedido + --bonus      (intacto)
    --altura P=A        ->  sobrepoe o pedido P com a altura A
    --negrito P         ->  o pedido P sai com peso 700 em vez de 400

**Os padroes ja sao os valores aprovados no jogo**: face Arial, `--bonus 0`,
`--teto 11`, `--livre 15`, `--altura 48=42`, `--negrito 48`, sem suavizacao.
Rodar sem argumento reproduz esse estado. O historico esta em "Tamanho da
fonte" no HISTORICO.md.

-------------------------------------------------- que tamanhos este cliente pede

Medido com `--tabela` em 2026-08-10, andando por Prontera. **Sao oito, e so
oito**:

    11  o texto miudo: chat, placas de NPC, nome de personagem
    12  |
    13  |  a janela de informacoes basicas - HP/SP, Base Lv., peso e zeny
    14  |
    16  |
    17  |  titulos de janela e o subtitulo do mapa ("A Capital de Rune-Midgard")
    18  |
    48  O NOME DO MAPA - "Prontera", e nada mais no jogo inteiro

Essa lista e o que torna a calibragem cirurgica: 48 e exclusivo do nome do
mapa, entao mexer nele nao toca em mais nada. Sem a medicao isso seria chute.

**Por que faixa e nao teto** (2026-08-10): ate esta data o stub tinha um teto
plano de 11, e o efeito real dele nao era "limitar exagero" - era **achatar os
oito corpos acima num so**. O jogo inteiro saia na mesma altura, sem hierarquia
nenhuma: o nome do mapa do tamanho do chat. Reparar nisso levou tempo porque
cada texto isolado parecia plausivel; o que denunciou foi o cache, que tinha
**uma unica entrada preenchida**, a de indice 11.

E as duas pontas nao cabem num numero so: a janela de informacoes basicas pede
ate 14 e precisa ser achatada; o nome do mapa pede 48 e precisa passar. Dai o
`--livre`.

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

--------------------------------------------------- o `--tabela`, e por que ele existe

O cache do stub e indexado pelo **tamanho pedido cru**. Entao, com o cliente no
ar, as entradas nao-zeradas dizem exatamente quais tamanhos aquele cliente
pediu - o `--tabela` le isso do processo vivo e imprime. **E o unico jeito
honesto de calibrar**: sem ele, escolher onde cortar e chute, e chute aqui custa
um fechar-e-reabrir por rodada.

Duas ressalvas: so aparece o que ja foi desenhado (para ver o nome do mapa,
entrar num mapa antes), e um cliente patcheado com a versao de ate 2026-08-09
indexava pelo tamanho ja achatado - a leitura dele nao vale nada.

------------------------------------------------- a versao de 2026-08-08 nao funcionava

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

------------------------------------------------------ onde cada peca mora no exe

A `.xdiff` tem 0x1000 de tamanho VIRTUAL e so **0x400 vindos do arquivo**
(`SizeOfRawData`). Isso parte a secao em duas metades com naturezas diferentes,
e confundi-las e o jeito de perder uma tarde:

    0x013B5000 .. 0x013B5400   vem do ARQUIVO - stub e tabela de alturas moram
                               aqui, porque dado nosso so existe se for gravado
    0x013B5400 .. 0x013B6000   NAO vem do arquivo - o carregador zera. Serve de
                               rascunho (o cache de HFONT), e so. Gravar valor
                               aqui no arquivo nao chega na memoria: o byte fica
                               no fim do .exe, fora de qualquer secao mapeada

    0x013B5320  MAPA_VA     64 bytes, altura+negrito por tamanho pedido (arquivo)
    0x013B5390  CODIGO_VA   o stub, 112 bytes ate a tabela              (arquivo)
    0x013B5400  TABELA_VA   64 dwords, cache de HFONT                   (rascunho)

Os 64 bytes de `MAPA_VA` sao um vao de zeros entre dois stubs do NEMO (um acaba
em 0x013B531A, o outro comeca em 0x013B5360). Nada salta para la - conferido
varrendo todo `e8`/`e9` do `.text` e procurando o endereco como constante.

**O negrito viaja no bit 7 do byte de altura**, e nao numa segunda tabela, por
falta de espaco: depois do mapa vem um stub do NEMO, e o maior vao de zeros que
sobra na metade util da secao tem 40 bytes. Por isso a altura vai ate 127.

--------------------------------------------------------------------- dois modos

--teto/--livre  (padrao)  altura por tamanho pedido, lida do MAPA. Preserva a
                          proporcao entre titulo, corpo e rodape. O cache e
                          obrigatorio: sem ele cada pedido criaria um HFONT novo
                          e o processo vazaria handles ate cair.

--fixo N                  devolve UMA altura N para todo pedido. Achata as
                          diferencas que o cliente faz de proposito - use so
                          para diagnostico.

**A interface e de caixa fixa.** Altura alta transborda: em 2026-08-09, com
`--fixo 20`, o painel de selecao de personagem cortou "Interior de Prontera" em
"Interior d" e os valores do inventario se sobrepuseram. Subir de 4 em 4 e
olhar e o caminho.

O exe fica travado enquanto o cliente roda, e o cliente segura o proprio exe
(renomear tambem nao resolve). Fechar e o unico caminho - e o que ja esta
aberto segue na copia em memoria, entao **fechar e reabrir**.
"""
import struct, sys, shutil, datetime, ctypes, subprocess

EXE_PADRAO = r"C:\GuerraDoEmperium\cliente\GuerraDoEmperium.exe"

ALVO_VA   = 0x004C3660      # o distribuidor de fontes
MAPA_VA   = 0x013B5320      # 64 bytes: altura|negrito por pedido (vem do arquivo)
CODIGO_VA = 0x013B5390      # o stub, em .xdiff (executavel e gravavel)
TABELA_VA = 0x013B5400      # cache: 64 dwords, indexado pelo tamanho pedido CRU
TABELA_N  = 64
BIT_NEGRITO = 0x80          # no byte do mapa; a altura fica nos 7 bits de baixo
PESO_NORMAL, PESO_NEGRITO = 400, 700
IAT_CREATEFONTA = 0x00DA2048
FACES_VA = {                # strings de face que ja existem dentro do exe
    "Gulim":   0x00DCCC78,
    "Arial":   0x00DCCC80,
    "Tahoma":  0x00DCCCA4,
    "Verdana": 0x00DCCCAC,
}
ORIGINAL_5 = "\x55\x8b\xec\x6a\xff"    # push ebp; mov ebp,esp; push -1

# O nome do mapa ("Prontera") e o unico texto do jogo que pede 48 - medido com
# --tabela. Menor e em negrito foi o pedido do dono do servidor em 2026-08-10,
# depois de ver o corpo natural na tela. Comecou em 46 ("dois pontos menor") e
# virou 42 na mesma conversa: 46 e uma diferenca de 4%, que some ao lado do
# negrito. Numero de tipografia se decide na tela, nao na aritmetica.
ALTURA_PADRAO  = "48=42"
NEGRITO_PADRAO = "48"


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


def le_pares(texto, quantos):
    u"""'48=46,17=16' -> {48: 46}. Com quantos=1, '48,17' -> {48: None}."""
    fora = {}
    for item in (texto or "").replace(" ", "").split(","):
        if not item:
            continue
        partes = item.split("=")
        if len(partes) != quantos:
            raise SystemExit("nao entendi '%s'" % item)
        try:
            nums = [int(p) for p in partes]
        except ValueError:
            raise SystemExit("nao entendi '%s' - so numero" % item)
        if not (0 <= nums[0] < TABELA_N):
            raise SystemExit("tamanho pedido %d fora de 0..%d" % (nums[0], TABELA_N - 1))
        fora[nums[0]] = nums[1] if quantos == 2 else None
    return fora


def monta_mapa(teto, livre, bonus, fixo, alturas, negritos):
    u"""O byte que cada tamanho pedido recebe: altura nos 7 bits de baixo,
    negrito no bit 7. Indice = tamanho pedido."""
    m = []
    for pedido in range(TABELA_N):
        if fixo:
            h = fixo
        elif pedido >= livre:
            h = pedido + bonus          # passa intacto: e o nome do mapa e os titulos
        else:
            h = min(pedido, teto) + bonus
        h = alturas.get(pedido, h)
        # altura 0 pediria "o padrao do Windows", e o bit 7 e do negrito
        h = max(1, min(BIT_NEGRITO - 1, h))
        m.append(h | (BIT_NEGRITO if pedido in negritos else 0))
    return m


def descreve_mapa(m, de=1, ate=32):
    for i in range(de, ate):
        h, neg = m[i] & (BIT_NEGRITO - 1), m[i] & BIT_NEGRITO
        marca = "" if (h == i and not neg) else "   <-"
        print "  %2d -> %2d%s%s" % (i, h, " negrito" if neg else "", marca)


def pids_no_ar():
    saida = subprocess.check_output(
        ["tasklist", "/FI", "IMAGENAME eq GuerraDoEmperium.exe", "/FO", "CSV", "/NH"])
    pids = []
    for linha in saida.splitlines():
        campos = [c.strip('"') for c in linha.strip().split('","')]
        if len(campos) > 1 and campos[1].isdigit():
            pids.append(int(campos[1]))
    return pids


def le_tabela_do_processo():
    u"""Que tamanhos o cliente NO AR ja pediu.

    O cache e indexado pelo tamanho pedido cru, entao entrada nao-zerada =
    aquele tamanho foi pedido. E a unica medicao honesta de onde cortar.
    """
    pids = pids_no_ar()
    if not pids:
        raise SystemExit("nenhum GuerraDoEmperium.exe no ar - suba o cliente antes")

    PROCESS_VM_READ = 0x0010
    PROCESS_QUERY_INFORMATION = 0x0400
    k = ctypes.windll.kernel32
    for pid in pids:
        h = k.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
        if not h:
            print "pid %d: OpenProcess falhou (erro %d)" % (pid, k.GetLastError())
            continue
        buf = ctypes.create_string_buffer(TABELA_N * 4)
        lidos = ctypes.c_size_t(0)
        ok = k.ReadProcessMemory(h, ctypes.c_void_p(TABELA_VA), buf,
                                 TABELA_N * 4, ctypes.byref(lidos))
        k.CloseHandle(h)
        if not ok:
            print "pid %d: ReadProcessMemory falhou (erro %d)" % (pid, k.GetLastError())
            continue
        vals = struct.unpack("<%dI" % TABELA_N, buf.raw)
        vistos = [(i, v) for i, v in enumerate(vals) if v]
        print
        print "pid %d: %d tamanhos pedidos" % (pid, len(vistos))
        if not vistos:
            print "  tabela vazia - ou o cliente ainda nao desenhou nada, ou este"
            print "  exe nao esta desviado, ou e a versao anterior da ferramenta"
        for i, v in vistos:
            print "  tamanho %2d  -> HFONT 0x%08X" % (i, v)


def main():
    if "--tabela" in sys.argv:
        le_tabela_do_processo()
        return

    alvos = [a for a in sys.argv[1:] if a.lower().endswith(".exe")]
    exe = alvos[0] if alvos else EXE_PADRAO

    # Os padroes sao os valores calibrados no jogo, olhando a tela a cada
    # degrau. Rodar sem argumento reproduz o estado aprovado.
    face = opcao("--face", "Arial")
    fixo = int(opcao("--fixo", "0"))
    bonus = int(opcao("--bonus", "0"))
    teto = int(opcao("--teto", "11"))
    livre = int(opcao("--livre", "15"))
    alturas = le_pares(opcao("--altura", ALTURA_PADRAO), 2)
    negritos = le_pares(opcao("--negrito", NEGRITO_PADRAO), 1)
    if face not in FACES_VA:
        raise SystemExit("face deve ser uma de: %s" % ", ".join(sorted(FACES_VA)))
    if fixo and not (1 <= fixo <= 99):
        raise SystemExit("--fixo fora de faixa (1 a 99)")
    if not (1 <= teto <= TABELA_N - 1):
        raise SystemExit("--teto fora de faixa (1 a %d)" % (TABELA_N - 1))
    if not (teto < livre <= TABELA_N):
        raise SystemExit("--livre tem de ficar acima do --teto e ate %d" % TABELA_N)
    for p, a in alturas.items():
        if not (1 <= a < BIT_NEGRITO):
            raise SystemExit("--altura %d=%d: a altura vai de 1 a %d (o bit 7 e "
                             "do negrito)" % (p, a, BIT_NEGRITO - 1))
    # bonus 0 e negativo sao validos, e nao sao o mesmo que --reverter: a face
    # aqui e NOSSA, nao a do cliente. Duas faces na mesma altura em pixels nao
    # desenham do mesmo tamanho, entao `+0` ja e uma mudanca de tamanho - e
    # pode ser justamente o ponto certo. Ver a nota "nao aumentamos, trocamos".
    if not fixo and not (-8 <= bonus <= 40):
        raise SystemExit("--bonus fora de faixa (-8 a 40)")

    mapa = monta_mapa(teto, livre, bonus, fixo, alturas, negritos)

    if "--mapa" in sys.argv:
        print "tamanho pedido -> altura entregue"
        descreve_mapa(mapa, 1, 32)
        for p in sorted(alturas.keys() + list(negritos)):
            if p >= 32:
                descreve_mapa(mapa, p, p + 1)
        return

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

    mapa_off = va2off(MAPA_VA)

    if "--verificar" in sys.argv:
        if ligado:
            cod = va2off(CODIGO_VA)
            print "stub em 0x%08X: %s ..." % (
                CODIGO_VA, " ".join("%02x" % b for b in d[cod:cod + 12]))
            print "mapa em 0x%08X:" % MAPA_VA
            gravado = [d[mapa_off + i] for i in range(TABELA_N)]
            for i in range(TABELA_N):
                h, neg = gravado[i] & (BIT_NEGRITO - 1), gravado[i] & BIT_NEGRITO
                if neg or (h != i and i):
                    print "  pedido %2d -> altura %2d%s" % (
                        i, h, " NEGRITO" if neg else "")
        print "--verificar: nenhum byte gravado."
        return

    # O Windows abre o exe de um processo vivo negando escrita, entao gravar
    # falharia - mas so DEPOIS do backup, deixando um arquivo orfao com nome de
    # quem mudou alguma coisa. Perguntar antes sai mais barato que explicar
    # depois, e o erro cru ("Permission denied") nao diz que basta fechar o
    # jogo. O teste e abrir para escrita: vale para qualquer alvo, inclusive
    # uma copia de laboratorio, que nao esta travada.
    try:
        open(exe, "r+b").close()
    except IOError:
        raise SystemExit(
            "o exe esta travado - feche o cliente antes (pid %s).\n"
            "Nada foi gravado." % (", ".join(str(p) for p in pids_no_ar()) or "?"))

    carimbo = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    if "--reverter" in sys.argv:
        if not ligado:
            print "Nada a fazer: ja esta original."
            return
        shutil.copy2(exe, exe + ".BACKUP-fonte-" + carimbo)
        d[alvo:alvo + 5] = ORIGINAL_5
        d[mapa_off:mapa_off + TABELA_N] = "\x00" * TABELA_N   # devolve o vao de zeros
        open(exe, "wb").write(str(d))
        print "revertido. backup: %s" % (exe + ".BACKUP-fonte-" + carimbo)
        return

    # ----------------------------------------------------------------- o stub
    # entrada: ecx = this (ignorado); [esp+4..+14h] = os cinco argumentos
    def criar_fonte():
        u"""Os 14 argumentos de CreateFontA, empilhados da direita para a esquerda.

        A altura sai de ecx, ja negada - negativa e altura de CARACTERE;
        positiva seria altura de celula, que da uma letra menor que o pedido.
        O peso sai de eax, que o trecho acima ja resolveu em 400 ou 700.

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
                "\x50" +                # cWeight = eax
                "\x6a\x00" * 3 +        # cOrientation, cEscapement, cWidth
                "\x51" +                # cHeight = ecx
                "\xff\x15" + struct.pack("<I", IAT_CREATEFONTA))

    # O indice tem de caber no MAPA e na TABELA, sempre. A comparacao e SEM
    # SINAL de proposito: valor negativo ou lixo vira um numero enorme e cai no
    # mesmo corte. Achatar o TAMANHO e outra coisa, e mora no MAPA - aqui e so
    # a trava de limite.
    limita = ("\x83\xfa" + chr(TABELA_N - 1) +                # cmp edx, 63
              "\x76\x05" +                                     # jbe +5
              "\xba" + struct.pack("<I", TABELA_N - 1))        # mov edx, 63

    # ebx guarda o indice por cima da chamada: e salvo-pelo-chamado no Win32,
    # entao a CreateFontA tem de devolve-lo intacto. Sai mais barato que
    # reler [esp+8] e limitar de novo depois - e o stub tem 112 bytes, nao mais.
    corpo = ("\x53" +                                         # push ebx
             "\x8b\xda" +                                      # mov ebx,edx
             "\x0f\xb6\x8a" + struct.pack("<I", MAPA_VA) +    # movzx ecx,byte[edx+MAPA]
             "\xb8" + struct.pack("<I", PESO_NORMAL) +        # mov eax,400
             "\xf6\xc1" + chr(BIT_NEGRITO) +                  # test cl,80h
             "\x74\x05" +                                      # jz  +5
             "\xb8" + struct.pack("<I", PESO_NEGRITO) +       # mov eax,700
             "\x83\xe1" + chr(BIT_NEGRITO - 1) +              # and ecx,7Fh
             "\xf7\xd9" +                                      # neg ecx
             criar_fonte() +
             "\x89\x04\x9d" + struct.pack("<I", TABELA_VA) +  # mov [TABELA+ebx*4],eax
             "\x5b")                                           # pop ebx
    stub = ("\x8b\x54\x24\x08" +                              # mov edx,[esp+8]
            limita +
            "\x8b\x04\x95" + struct.pack("<I", TABELA_VA) +   # mov eax,[TABELA+edx*4]
            "\x85\xc0" +                                       # test eax,eax
            "\x75" + struct.pack("<b", len(corpo)) +           # jnz pronto
            corpo + "\xc2\x14\x00")                            # ret 14h

    if len(stub) > TABELA_VA - CODIGO_VA:
        # O stub e CODIGO: tem de vir do arquivo, e o arquivo acaba em
        # TABELA_VA. Passar disso da um salto para memoria zerada.
        raise SystemExit("stub com %d bytes nao cabe nos %d ate a tabela"
                         % (len(stub), TABELA_VA - CODIGO_VA))
    if MAPA_VA + TABELA_N > CODIGO_VA:
        raise SystemExit("o mapa invade o stub")

    shutil.copy2(exe, exe + ".BACKUP-fonte-" + carimbo)
    cod = va2off(CODIGO_VA)
    d[cod:cod + (TABELA_VA - CODIGO_VA)] = "\x00" * (TABELA_VA - CODIGO_VA)
    d[cod:cod + len(stub)] = stub
    d[mapa_off:mapa_off + TABELA_N] = "".join(chr(h) for h in mapa)
    d[alvo:alvo + 5] = "\xe9" + struct.pack("<i", CODIGO_VA - (ALVO_VA + 5))
    open(exe, "wb").write(str(d))

    if fixo:
        como = "fixo: altura %d para todo pedido" % fixo
    else:
        como = ("achata ate %d (altura %d) e solta de %d para cima, bonus %+d"
                % (livre - 1, teto + bonus, livre, bonus))
    print "face %s | %s   (a altura do cliente e 13)" % (face, como)
    print "stub 0x%08X, %d bytes de %d | mapa 0x%08X" % (
        CODIGO_VA, len(stub), TABELA_VA - CODIGO_VA, MAPA_VA)
    for p in sorted(set(alturas.keys()) | set(negritos)):
        h = mapa[p] & (BIT_NEGRITO - 1)
        print "  pedido %d -> altura %d%s" % (
            p, h, " NEGRITO" if mapa[p] & BIT_NEGRITO else "")
    print "backup: %s" % (exe + ".BACKUP-fonte-" + carimbo)
    print
    print "Feche e reabra o cliente: o que ja esta aberto roda a copia antiga,"
    print "que continua na memoria mesmo com o arquivo trocado."


main()
