# -*- coding: utf-8 -*-
u"""Completa o `itemInfo.lua` do cliente com entradas tiradas do bRO.

    python completa_iteminfo.py                 # aplica (faz backup antes)
    python completa_iteminfo.py --verificar     # so relata, nao grava
    python completa_iteminfo.py --id 450222     # um item so (ou lista, com virgula)
    python completa_iteminfo.py --listar        # so mostra o que o bRO tem
    python completa_iteminfo.py --descricoes    # reescreve a descricao das nossas
    python completa_iteminfo.py --id 450222 --descricoes --sem-acento  # ASCII

O problema que este script resolve: o nosso cliente e de 2021-11-03 e o
`itemInfo.lua` que ele usa vem do ROenglishRE, que traduz o que o kRO/iRO tem.
Item que exista no `item_db` do servidor mas nao aqui aparece **sem nome e sem
icone** no inventario e na loja. Foi o que aconteceu ao montar o Mercado
Contemporaneo (npc/guerra/mercado_contemporaneo.txt): 25 dos itens pedidos nao
tinham entrada nenhuma.

A cura ja estava nesta maquina, e e o mesmo padrao que se repetiu a sessao
inteira - **a versao que falta quase sempre ja esta no disco, so nao esta sendo
lida.** A instalacao do Ragnarok Brazil traz

    C:\\Program Files (x86)\\Gravity Interactive, Inc\\Ragnarok Brazil\\System\\iteminfo_new.lub

com 18845 itens **em portugues**, muito mais nova que a nossa. Ela e a fonte.
A mesma instalacao ja era a fonte de arte do `instala_visual.py`.

Diferenca para o `instala_item.py`, que e o vizinho de prateleira: aquele
inventa a entrada de um item NOSSO, a partir de uma receita escrita a mao.
Este COPIA a entrada de um item que ja existe no bRO. Um cria, o outro importa.

--------------------------------------------------------------------- formatos

O `iteminfo_new.lub` do bRO e **bytecode Lua 5.1** (header `\\x1bLuaQ`), nao
texto - por isso a leitura passa por um mini-desassemblador aqui dentro, primo
do `luadis.py`. O `itemInfo.lua` do ROenglishRE, que e o nosso destino, e texto
puro. Nao confundir os dois.

Duas conversoes de codificacao acontecem, e errar qualquer uma corrompe:

  - **nome e descricao** - as strings do bRO sao UTF-8; o arquivo do cliente e
    ANSI. Vao para cp1252 COM acento ("Epitáfio"), que e o que o patch
    AlwaysAscii do nosso exe sabe desenhar. `--sem-acento` reduz a ASCII.
  - **resourceName** - e nome de arquivo dentro do GRF, e no nosso
    `itemInfo.lua` esses bytes sao **CP949 coreano**. No bRO eles vem em UTF-8.
    A conversao UTF-8 -> CP949 e obrigatoria: gravar o UTF-8 cru faria o cliente
    procurar um arquivo que nao existe, e o item apareceria sem icone.

Item cujo `resourceName` nao couber em CP949 e pulado com aviso, nunca gravado
pela metade.

--------------------------------------------------------------------- cuidados

O que este script NAO faz: nao traz a descricao do item. A caixa de descricao
recebe uma linha dizendo de onde a entrada veio. Trazer o texto real exigiria
desmontar as tabelas aninhadas de descricao do bytecode, e o retorno nao paga -
o que faltava era nome e icone.

**Chapeu e caso a parte.** Nome resolvido nao quer dizer chapeu desenhavel: se
o `.spr`/`.act` nao existir no GRF, equipar entrega caixa modal de erro. Depois
de rodar este script, rodar o `valida_visual.py` nos itens de cabeca e, se
faltar arte, o `instala_visual.py`. A ordem importa: o `valida_visual.py` le o
`identifiedResourceName` DAQUI, entao antes deste script ele nem consegue
avaliar o item.

E como o cliente le o `itemInfo.lua` **so na inicializacao**, toda mudanca
exige fechar e reabrir. `@reloaditemdb` nao alcanca este arquivo.

Idempotente: item que ja tenha entrada nao e tocado (nem para conferir se e
igual - a entrada existente pode ser a do ROenglishRE, em ingles, e trocar por
uma nossa sem descricao seria piorar). Roda em Python 2.7.
"""
import os
import re
import shutil
import struct
import sys
import time
import unicodedata

ITEMINFO = os.path.join(r'C:\GuerraDoEmperium\cliente',
                        'SystemEN', 'LuaFiles514', 'itemInfo.lua')

BRO = os.path.join(r'C:\Program Files (x86)\Gravity Interactive, Inc',
                   'Ragnarok Brazil', 'System', 'iteminfo_new.lub')

# ------------------------------------------------------------------- a lista
#
# Os itens do Mercado Contemporaneo que nao tinham entrada no nosso
# `itemInfo.lua`, levantados em 2026-08-01. Acrescentar item aqui, nao no
# codigo. O comentario e o nome que o bRO da - serve para conferir de olho que
# o ID e o item que se espera.

ITENS = [
    # --- Chapeleiro / Ocleiro / Retoqueiro (cabeca: conferir arte depois!)
    400006,   # Cocar do Orc Heroi
    400287,   # Capacete de Intensificacao
    400687,   # Garra Diabolica          (placeholder em db/guerra/item_db.yml)
    410124,   # Orelhas em Chamas
    410142,   # Adorno Angelical
    19445,    # Curativo YSF01
    420110,   # Cachecol Camuflado
    # As duas COM COVA que entraram em 2026-08-05, quando a loja do
    # Ocleiro trocou quatro itens pela versao de um encaixe. As outras
    # duas da troca (19444 e 19446) ja tinham entrada e nao precisam vir.
    410125,   # Orelhas em Chamas [1]
    19455,    # Diadema do Paraiso [1]   (placeholder em db/guerra/item_db.yml)
    # As duas de cabeca meio que entraram no Ocleiro em 2026-08-07. O `Name`
    # do servidor nas duas estava em ingles e foi sincronizado depois, pelo
    # nomes_pt_item_db.py.
    410067,   # Mini Oculos [1]          (servidor: Professor's Mini Glasses)
    410026,   # Heranca Real [1]         (servidor: Floating Artifacts)
    # --- Senhor das Armas
    500009,   # Lamina Sagrada
    510155,   # Ceuci                    (placeholder em db/guerra/item_db.yml)
    # --- Lorde das Armaduras
    450338,   # Algazarra
    450222,   # Epitafio
    450120,   # Armadura Resistente      (placeholder em db/guerra/item_db.yml)
    15371,    # Roupa de Natal do Antonio (placeholder)
    # --- Escudeiro
    460074,   # Broquel Aracnideo
    460025,   # Escudo Alado
    460046,   # Escudo de Carvao
    28962,    # Escudo Divino
    # --- Capeiro
    480220,   # Baleia de Pelucia
    480077,   # Capa de Magma [1]        (entrou em 2026-08-07)
    # --- Sapateiro
    470180,   # Botas Tres Marias
    470206,   # Botas de Prana
    470293,   # Bota Fantasma
    # --- Acessorista
    490337,   # Amuleto Mitologico
    490290,   # Anel de Ameretat
    490367,   # Bracelete de Ulle
    28572,    # Broche da Celine         (placeholder em db/guerra/item_db.yml)
    # --- As NOVE versoes [MEGA] da Valquiria Mega, de Malangdo
    # (npc/guerra/valquirias_de_malangdo.txt), levantadas em 2026-09-02:
    # sao as dez transformacoes do Labirinto das Valquirias menos o
    # 400177 (Elmo de Fafnir), que ja tinha entrada. Sem elas a peca sai
    # da NPC sem nome e sem icone, e as cinco do vendor ainda faziam o
    # DIALOGO dela falar ingles: o menu e escrito com `getitemname()`,
    # que le o `Name` do servidor, e o `Name` do servidor sai daqui pelo
    # nomes_pt_item_db.py.
    22245,    # [MEGA] Botas Espaciais
    470047,   # [MEGA] Patas de Raposas
    450181,   # [MEGA] Vestimenta de Seda
    450158,   # [MEGA] Robe Gelado
    450286,   # [MEGA] Vestes de Cardeal
    # As quatro seguintes sao NOSSAS (db/guerra/item_db.yml, decima leva)
    # e ja nascem em portugues no servidor; nelas falta so o cliente.
    810012,   # [MEGA] A.R.-89
    510065,   # [MEGA] Totsuka
    550074,   # [MEGA] Vara
    590042,   # [MEGA] Mangual do Demonio
]


class Erro(Exception):
    pass


# =========================================================== ler o bytecode
#
# Mini-leitor de Lua 5.1 little-endian 32 bits, igual ao do luadis.py. So o
# necessario para percorrer as instrucoes e o pool de constantes.

class R(object):
    def __init__(s, d, p=0):
        s.d, s.p = d, p

    def u8(s):
        v = ord(s.d[s.p]); s.p += 1; return v

    def u32(s):
        v = struct.unpack('<I', s.d[s.p:s.p + 4])[0]; s.p += 4; return v

    def f64(s):
        v = struct.unpack('<d', s.d[s.p:s.p + 8])[0]; s.p += 8; return v

    def sz(s):
        n = s.u32()
        if n == 0:
            return ''
        v = s.d[s.p:s.p + n - 1]; s.p += n; return v


def le_funcao(r):
    f = {}
    f['source'] = r.sz(); r.u32(); r.u32()
    r.u8(); r.u8(); r.u8(); r.u8()
    n = r.u32(); f['code'] = [r.u32() for _ in range(n)]
    n = r.u32(); k = []
    for _ in range(n):
        t = r.u8()
        if t == 0:
            k.append(None)
        elif t == 1:
            k.append(bool(r.u8()))
        elif t == 3:
            k.append(r.f64())
        elif t == 4:
            k.append(r.sz())
        else:
            raise Erro('constante de tipo %d, arquivo inesperado' % t)
    f['k'] = k
    n = r.u32(); f['protos'] = [le_funcao(r) for _ in range(n)]
    n = r.u32(); [r.u32() for _ in range(n)]                    # linhas
    n = r.u32(); [(r.sz(), r.u32(), r.u32()) for _ in range(n)]  # locais
    n = r.u32(); [r.sz() for _ in range(n)]                      # upvalues
    return f


CAMPOS = ('unidentifiedDisplayName', 'unidentifiedResourceName',
          'identifiedDisplayName', 'identifiedResourceName',
          'slotCount', 'ClassNum')

# Tabelas aninhadas de texto. Sao construidas com NEWTABLE + LOADK em
# registradores consecutivos + SETLIST, e o SETLIST vem no FIM do construtor -
# no momento em que o campo e atribuido a lista ainda esta vazia. Por isso o
# leitor guarda a lista viva no registrador e le o conteudo depois.
LISTAS = ('identifiedDescriptionName', 'unidentifiedDescriptionName')


def _rk(f, reg, i):
    u"""Operando RK: >=256 e constante, senao e registrador.

    O `if i >= 256` e o detalhe que faz este leitor funcionar em arquivo
    grande. O RK so endereca constante ate 255; passando disso o compilador
    emite LOADK num registrador e o SETTABLE referencia R<n>. Parser que so
    olhe a forma "constante" le as ~127 primeiras entradas e devolve um numero
    plausivel e errado - ver ferramentas/LEIAME.md, secao do luadis.py.
    """
    if i >= 256:
        return f['k'][i - 256]
    return reg.get(i)


def _varre(f, saida):
    reg = {}
    campos = {}
    for ins in f['code']:
        op = ins & 0x3f
        A = (ins >> 6) & 0xff
        C = (ins >> 14) & 0x1ff
        B = (ins >> 23) & 0x1ff
        Bx = (ins >> 14) & 0x3ffff
        if op == 1:                                   # LOADK
            reg[A] = f['k'][Bx]
        elif op == 0:                                 # MOVE
            reg[A] = reg.get(B)
        elif op == 10:                                # NEWTABLE
            reg[A] = []          # lista viva; o SETLIST preenche mais adiante
        elif op == 34:                                # SETLIST A B C
            alvo = reg.get(A)
            if isinstance(alvo, list):
                for i in range(1, B + 1):
                    alvo.append(reg.get(A + i))
        elif op == 9:                                 # SETTABLE A B C
            chave = _rk(f, reg, B)
            valor = _rk(f, reg, C)
            if chave in CAMPOS and not isinstance(valor, list):
                campos[chave] = valor
            elif chave in LISTAS and isinstance(valor, list):
                # Guarda a REFERENCIA, nao uma copia: o SETLIST que preenche
                # esta lista ainda nao rodou neste ponto do bytecode.
                campos[chave] = valor
            elif isinstance(chave, float) and isinstance(valor, list):
                # Fecha a entrada: `tbl[<id>] = <tabela recem-montada>`. Em Lua
                # a tabela interna e construida ANTES desta atribuicao, entao
                # tudo que se acumulou ate aqui pertence a ela.
                saida[int(chave)] = campos
                campos = {}
    for p in f['protos']:
        _varre(p, saida)


def le_bro(caminho):
    u"""id -> {campo: valor}, lido do iteminfo do bRO."""
    if not os.path.exists(caminho):
        raise Erro('nao achei a instalacao do bRO em %s' % caminho)
    fh = open(caminho, 'rb')
    dados = fh.read()
    fh.close()
    if dados[:5] != '\x1bLuaQ':
        raise Erro('%s nao e bytecode Lua 5.1' % caminho)
    saida = {}
    _varre(le_funcao(R(dados, 12)), saida)
    return saida


# ======================================================== converter o texto

COM_ACENTO = [True]         # desligado por --sem-acento; ver a nota abaixo


def sem_acento(bruto, exigir=True):
    u"""UTF-8 do bRO -> o texto como ele vai para o arquivo.

    Por padrao **mantem o acento**, gravando em cp1252 - a codepage ANSI desta
    maquina e a mesma em que o bRO entrega os arquivos dele. Quem desenha
    esses bytes e o patch `AlwaysAscii`, aplicado no nosso exe: sem ele o
    cliente usaria o charset coreano, onde 0x80-0xFF e byte-lider de hangul e
    um `a` acentuado engoliria o byte seguinte.

    ATENCAO: o campo `resourceName` NAO passa por aqui - aquele continua em
    CP949, por `para_cp949()`. Sao dois encodings no mesmo arquivo, de
    proposito: um e texto de tela, o outro e nome de arquivo dentro do GRF.

    `--sem-acento` volta ao comportamento antigo (ASCII puro). E a saida de
    emergencia se o jogo mostrar lixo no lugar do acento; a mesma bandeira
    existe no traduz_ptbr.py e as duas tem de andar juntas.
    """
    try:
        texto = bruto.decode('utf-8')
    except UnicodeDecodeError:
        raise Erro('texto nao e UTF-8 valido: %r' % bruto)
    if COM_ACENTO[0]:
        try:
            limpo = texto.encode('cp1252')
        except UnicodeEncodeError:
            limpo = unicodedata.normalize('NFKD', texto).encode('ascii',
                                                                'ignore')
    else:
        limpo = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore')
    if exigir and not limpo.strip():
        raise Erro('texto vira vazio ao tirar o acento: %r' % bruto)
    # Aspas quebrariam o literal Lua; o arquivo nao escapa nada.
    return limpo.replace('"', "'")


# Assinatura das entradas postas por ESTE script. E o que autoriza o
# `--descricoes` a reescrever um bloco: sem ela, o bloco veio do ROenglishRE e
# nao se toca.
MARCA = 'Entrada importada da tabela do bRO'


def para_cp949(bruto):
    u"""UTF-8 do bRO -> os bytes CP949 que o nosso itemInfo.lua usa.

    Nome de recurso puramente ASCII (`Fafnir_Helm`) atravessa igual; nome
    coreano precisa da conversao, e e o caso da maioria dos itens antigos.
    """
    try:
        texto = bruto.decode('utf-8')
    except UnicodeDecodeError:
        raise Erro('resourceName nao e UTF-8 valido: %r' % bruto)
    try:
        return texto.encode('cp949')
    except UnicodeEncodeError:
        raise Erro('resourceName nao cabe em CP949: %r' % texto)


# ============================================== escrever no itemInfo.lua
#
# Reaproveita o formato exato do instala_item.py: CRLF, um tab na entrada de
# primeiro nivel, dois nos campos. As tabelas aninhadas de descricao tem dois
# tabs e nao sao indexadas por numero, entao nao casam com o cabecalho.

CABECALHO = re.compile(r'\r\n\t\[(\d+)\] = \{')
FIM = '\r\n\t},'


def tem(dados, iid):
    return re.search(r'\r\n\t\[%d\] = \{' % iid, dados) is not None


def bloco(dados, iid):
    u"""(inicio, fim) da entrada de `iid`, ou None.

    O terminador e `\\r\\n\\t},` - UM tab. As tabelas aninhadas de descricao
    fecham com dois tabs, entao nao casam e a entrada nao e cortada no meio.
    """
    m = re.search(r'\r\n\t\[%d\] = \{' % iid, dados)
    if not m:
        return None
    fim = dados.find('\r\n\t},', m.start())
    if fim < 0:
        raise Erro('entrada [%d] comeca e nao termina' % iid)
    return (m.start(), fim + len('\r\n\t},'))


def onde_entra(dados, iid):
    u"""Offset da primeira entrada com ID maior - so para o arquivo continuar
    legivel; para o Lua a posicao e indiferente, a chave e explicita."""
    anterior = None
    for m in CABECALHO.finditer(dados):
        atual = int(m.group(1))
        if atual > iid:
            return (m.start(), anterior, atual)
        anterior = atual
    fim = dados.rfind(FIM)
    if fim < 0:
        raise Erro('nao achei o fim da ultima entrada')
    return (fim + len(FIM), anterior, None)


def monta(iid, campos):
    nome_id = sem_acento(campos.get('identifiedDisplayName') or '')
    nome_un = sem_acento(campos.get('unidentifiedDisplayName') or
                         campos.get('identifiedDisplayName') or '')
    arte_id = para_cp949(campos.get('identifiedResourceName') or '')
    arte_un = para_cp949(campos.get('unidentifiedResourceName') or
                         campos.get('identifiedResourceName') or '')
    slots = int(campos.get('slotCount') or 0)
    classe = int(campos.get('ClassNum') or 0)

    # A descricao vem do bRO em portugues e entra COMO ESTA - nao e traduzida
    # nem reescrita. Ela ja traz os numeros do item (DEF, ATQ, peso, nivel,
    # classes) e cada bonus por extenso, que e exatamente o que o jogador
    # precisa ler. A ultima linha e a nossa marca de procedencia.
    desc = [sem_acento(l, exigir=False)
            for l in (campos.get('identifiedDescriptionName') or [])
            if isinstance(l, str)]
    desc = [l for l in desc if l.strip()] or ['Sem descricao na tabela do bRO.']
    desc.append('_______________________')
    desc.append('^777777%s.^000000' % MARCA)

    linhas = ['\r\n\t[%d] = {' % iid]
    a = linhas.append
    a('\t\tunidentifiedDisplayName = "%s",' % nome_un)
    a('\t\tunidentifiedResourceName = "%s",' % arte_un)
    a('\t\tunidentifiedDescriptionName = { "" },')
    a('\t\tidentifiedDisplayName = "%s",' % nome_id)
    a('\t\tidentifiedResourceName = "%s",' % arte_id)
    a('\t\tidentifiedDescriptionName = {')
    for i, l in enumerate(desc):
        a('\t\t\t"%s"%s' % (l, '' if i == len(desc) - 1 else ','))
    a('\t\t},')
    a('\t\tslotCount = %d,' % slots)
    a('\t\tClassNum = %d,' % classe)
    a('\t\tcostume = false')
    a('\t},')
    return '\r\n'.join(linhas), nome_id


def aplica(caminho, alvos, verificar):
    bro = le_bro(BRO)
    print 'fonte:   %s' % BRO
    print '         %d itens' % len(bro)

    fh = open(caminho, 'rb')
    dados = fh.read()
    fh.close()
    antes = len(dados)
    print 'destino: %s' % caminho
    print '         %d bytes, %d entradas' % (antes,
                                              len(CABECALHO.findall(dados)))
    print

    reescrever = '--descricoes' in sys.argv
    postos = pulados = 0
    for iid in alvos:
        lim = bloco(dados, iid) if tem(dados, iid) else None
        if lim is not None:
            # A trava que torna o --descricoes seguro: so reescreve bloco que
            # ESTE script escreveu. Sem a marca, o bloco veio do ROenglishRE e
            # trocar por um nosso seria perder a traducao deles.
            if not reescrever:
                print '  [ja tem ] %-7d nao toco' % iid
                continue
            if MARCA not in dados[lim[0]:lim[1]]:
                print ('  [ALHEIA ] %-7d entrada do ROenglishRE, nao reescrevo'
                       % iid)
                pulados += 1
                continue
            if iid not in bro:
                print '  [SEM BRO] %-7d o bRO tambem nao tem' % iid
                pulados += 1
                continue
            try:
                novo, nome = monta(iid, bro[iid])
            except Erro as e:
                print '  [PULADO ] %-7d %s' % (iid, e)
                pulados += 1
                continue
            if dados[lim[0]:lim[1]] == novo:
                print '  [igual  ] %-7d %s' % (iid, nome)
                continue
            velho = lim[1] - lim[0]
            dados = dados[:lim[0]] + novo + dados[lim[1]:]
            print '  [troca  ] %-7d %-34s (%d -> %d bytes)' % (
                iid, nome, velho, len(novo))
            postos += 1
            continue
        if iid not in bro:
            print '  [SEM BRO] %-7d o bRO tambem nao tem este item' % iid
            pulados += 1
            continue
        try:
            novo, nome = monta(iid, bro[iid])
        except Erro as e:
            print '  [PULADO ] %-7d %s' % (iid, e)
            pulados += 1
            continue
        pos, ant, seg = onde_entra(dados, iid)
        dados = dados[:pos] + novo + dados[pos:]
        print '  [novo   ] %-7d %-34s (entre %s e %s)' % (iid, nome, ant, seg)
        postos += 1

    print
    print '%d postos, %d pulados' % (postos, pulados)
    if not postos:
        print 'Nada a gravar.'
        return 0
    print 'tamanho: %d -> %d bytes  (%+d)' % (antes, len(dados),
                                              len(dados) - antes)
    if verificar:
        print '\n--verificar: nenhum byte foi gravado.'
        return 0

    backup = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M'))
    shutil.copy2(caminho, backup)
    print 'Backup: %s' % os.path.basename(backup)
    fh = open(caminho, 'wb')
    fh.write(dados)
    fh.close()
    print 'Gravado: %s' % caminho
    print
    print 'O cliente le o itemInfo.lua so na inicializacao - feche e reabra.'
    print 'Item de CABECA: rodar valida_visual.py agora, que so depois desta'
    print 'entrada ele consegue avaliar a arte.'
    return 0


def listar(alvos):
    bro = le_bro(BRO)
    for iid in alvos:
        c = bro.get(iid)
        if not c:
            print '%-8d -- o bRO nao tem' % iid
            continue
        print '%-8d %-36s res=%r slots=%s' % (
            iid, c.get('identifiedDisplayName'),
            c.get('identifiedResourceName'), c.get('slotCount'))
    return 0


if __name__ == '__main__':
    argv = sys.argv[1:]
    alvos = ITENS
    if '--id' in argv:
        alvos = [int(x) for x in argv[argv.index('--id') + 1].split(',')]
    COM_ACENTO[0] = '--sem-acento' not in argv
    try:
        if '--listar' in argv:
            sys.exit(listar(alvos))
        sys.exit(aplica(ITEMINFO, alvos, '--verificar' in argv))
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
