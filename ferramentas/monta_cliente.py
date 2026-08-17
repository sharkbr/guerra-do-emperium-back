# -*- coding: utf-8 -*-
u"""Monta o pacote de PRIMEIRO DOWNLOAD do cliente: o que o instalador baixa.

    python monta_cliente.py                # monta tudo, do zero
    python monta_cliente.py --lista        # o que ja foi montado
    python monta_cliente.py --confere      # confere o registro contra os arquivos
    python monta_cliente.py --so nosso     # remonta so um grupo (ver GRUPOS)

E o irmao do `monta_patch.py`, e a diferenca e o publico: o patch fala com quem
JA TEM o cliente, este fala com quem nao tem nada. O patch e pequeno e
incremental; este sao 4,2 GB divididos em pedacos, e o jogador baixa uma vez
so na vida.

    C:\\GuerraDoEmperium\\cliente\\          de onde os arquivos saem
    C:\\GuerraDoEmperium\\instalador\\       onde os pedacos nascem (fora do git)
    patcher/base.txt                       o registro, VERSIONADO

Depois de montado, o instalador segue direto para os patches: quem baixa hoje
recebe a base desta versao mais todos os patches publicados desde entao, na
primeira abertura. E por isso que o pacote NAO precisa ser refeito a cada
mudanca - so quando o acumulo de patches ficar grande demais.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).


POR QUE O `data.grf` NAO E UM ZIP
---------------------------------
Ele tem 2,95 GiB num arquivo unico, e duas coisas decorrem disso. Primeiro, nao
ha como fatia-lo por arquivo: qualquer pedaco de zip que o contenha e do
tamanho dele. Segundo, zipa-lo nao ganha nada - o GRF ja e comprimido por
dentro -, e ainda custaria o dobro do disco no jogador, que precisaria do zip e
do extraido ao mesmo tempo.

Entao ele vai BRUTO: baixado direto para o destino, com retomada por
`Range`, conferido pelo sha256 no fim. Medido em 2026-08-16, o Spaces responde
`accept-ranges: bytes`, que e o que torna a retomada possivel - sem ela, uma
queda de conexao a 90% de 2,95 GB recomecaria do zero.

E dai vem o formato do registro, que tem SEIS campos e nao os cinco do
`patches.txt`: o campo a mais e o tipo.

    zip     extrai por cima da raiz do cliente, igual a um patch
    bruto   grava no caminho que esta no proprio campo `arquivo`

Para `bruto`, o campo `arquivo` e ao mesmo tempo o nome no bucket e o caminho
relativo dentro do cliente. Sao a mesma string de proposito - um campo a menos
e uma divergencia a menos.
"""
import codecs
import hashlib
import io
import os
import re
import sys
import zipfile

# Ver o comentario gemeo no `monta_patch.py`: a pasta `AI_sakray` tem arquivo de
# nome COREANO, e um `print` dele estoura com UnicodeEncodeError DEPOIS de o zip
# ja ter sido escrito - deixando saida pela metade e trabalho feito. Sem
# `sys.stdout.encoding` (saida redirecionada) o Python 2 devolve None.
sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

# Caminhos nascem UNICODE, pelo mesmo motivo: `os.walk` com `str` usa a API ANSI
# e devolve `????`, que estoura no primeiro `os.stat`.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).decode('mbcs')
CLIENTE = ur'C:\GuerraDoEmperium\cliente'
SAIDA = ur'C:\GuerraDoEmperium\instalador'
REGISTRO = os.path.join(RAIZ, u'patcher', u'base.txt')

# Quanto entra em cada zip, medido no tamanho BRUTO dos arquivos. O comprimido
# sai menor - o que esta certo: o que se quer limitar e o pico de disco no
# jogador, que precisa do zip mais o extraido ao mesmo tempo.
#
# 400 MB e um meio-termo: pedaco pequeno demais multiplica requisicao e
# atrapalha a barra de progresso; grande demais faz a retomada custar caro,
# porque um pedaco interrompido volta do comeco.
MAX_PEDACO = 400 * 1024 * 1024

# O lixo que as proprias ferramentas deixam. Mesma lista do `monta_patch.py` -
# se uma mudar, a outra tem de mudar junto.
LIXO = ('BACKUP', '.ORIGINAL', '.original', '.INGLES', '.KOREA', '.KOR',
        '.pyc', 'Thumbs.db', 'desktop.ini')

# ESTADO LOCAL: nasce sozinho na maquina do jogador e NAO entra no pacote.
# Empacotar qualquer um destes entrega ao jogador o estado da NOSSA maquina -
# as nossas teclas, os nossos emblemas baixados, os nossos screenshots.
#
#   savedata     teclas, janelas, opcoes; o cliente cria no primeiro fechamento
#   patch        o `aplicados.txt` do Atualizador. Se fosse junto, o jogador
#                nasceria achando que ja tem patches que nao tem
#   Emblem       cache de emblema de cla baixado do web-server
#   _tmpEmblem   idem, temporario
#   ScreenShot   nossos prints de teste
#   Replay       gravacoes
#   memo         pontos de teleporte gravados
#   _extras      os exes originais (Ragexe, Ragexe_unpacked...). E a COPIA FRIA
#                do binario de origem unica, material NOSSO de trabalho -
#                `PENDENCIAS.md` §5b. O jogador nao tem o que fazer com ela.
ESTADO = (u'savedata', u'patch', u'Emblem', u'_tmpEmblem', u'ScreenShot',
          u'Replay', u'memo', u'_extras')

# O Atualizador NAO entra no pacote, e o motivo e o inverso do `monta_patch.py`:
# la ele fica de fora porque nao consegue se sobrescrever rodando; aqui porque o
# jogador JA O TEM - ele e o instalador. Foi o exe que o jogador baixou e abriu
# numa pasta vazia; poe-lo dentro do proprio pacote faria o programa tentar
# gravar por cima de si mesmo no meio da instalacao, que e exatamente o caminho
# que o Windows nao deixa.
FORA_DO_PACOTE = (u'jogar.exe', u'jogar.ini')

# Os grupos, na ordem em que o instalador aplica. A ordem importa pouco para o
# resultado (sao conjuntos disjuntos de arquivos), mas importa para o jogador:
# ele ve o nome do grupo na barra, e o mundo vindo primeiro da a sensacao certa
# de progresso - e o pedaco de 2,95 GB, ou seja 70% da espera.
#
# `resto` e o que sobra: tudo que nao foi nomeado nos outros grupos e nao e
# estado local. Nasce assim de proposito - um arquivo novo na raiz do cliente
# entra no pacote sozinho, em vez de ser esquecido caladamente. O erro que se
# quer evitar aqui e o do `PENDENCIAS.md` §5b: esquecer o `itemInfo.lua` e
# descobrir com todo item sem nome na loja.
GRUPOS = [
    (u'mundo', u'O mundo', 'bruto', [u'data.grf']),
    (u'musicas', u'As musicas', 'zip', [u'BGM']),
    (u'nosso', u'A Guerra do Emperium', 'zip',
     [u'data', u'System', u'SystemEN', u'AI', u'AI_sakray']),
    (u'resto', u'O motor do jogo', 'zip', None),
]


def morre(msg):
    print u'ERRO: %s' % msg
    sys.exit(1)


def texto(caminho):
    if isinstance(caminho, str):
        return caminho.decode('mbcs')
    return caminho


# ---------------------------------------------------------------------------
# A trava do apontamento (2026-08-16)
#
# Desde que esta maquina virou DEV/HML - producao passou a ser uma instalacao
# separada, feita pelo instalador -, o cliente de `C:\GuerraDoEmperium` aponta
# para 127.0.0.1 na maior parte do tempo. Empacotar a base nesse estado publica
# um cliente que manda todo jogador novo tentar logar na PROPRIA maquina dele:
# 3,4 GB corretos, sha256 fechando, e ninguem entra.
#
# A falha e' calada de duas maneiras que se somam: o `<address>` esta' num
# arquivo de configuracao que ninguem revisa antes de publicar, e SAO DOIS
# ARQUIVOS (o exe e' <servertype>sakray</servertype>, entao quem vale e' o
# `sclientinfo.xml` - CLAUDE.md secao 5). Por isso a conferencia olha os dois:
# um apontando para casa ja' e' motivo de parar.
ENDERECOS_LOCAIS = (u'127.0.0.1', u'localhost', u'0.0.0.0', u'::1', u'')
APONTAMENTOS = (u'clientinfo.xml', u'sclientinfo.xml')


def confere_apontamento(escape=u'--permite-local'):
    """Recusa empacotar cliente apontado para a maquina local."""
    for nome in APONTAMENTOS:
        cam = os.path.join(CLIENTE, u'data', nome)
        if not os.path.isfile(cam):
            continue
        achado = re.search(r'<address>([^<]*)</address>',
                           open(cam, 'rb').read())
        if not achado:
            morre(u'%s nao tem <address> - conferir a mao antes de publicar'
                  % nome)
        endereco = achado.group(1).decode('cp1252').strip()
        if endereco in ENDERECOS_LOCAIS:
            morre(u'data\\%s aponta para "%s" (a maquina local).\n'
                  u'       Esta maquina e dev/hml; empacotar assim publica um\n'
                  u'       cliente que nunca vai achar o servidor.\n'
                  u'       Aponte os DOIS xml para a producao e rode de novo\n'
                  u'       (ou passe %s, se for de proposito).'
                  % (nome, endereco, escape))
    return True


def e_lixo(caminho):
    nome = os.path.basename(caminho)
    return any(marca in nome for marca in LIXO)


def relativo(caminho):
    u"""Caminho relativo a raiz do cliente, com barra normal."""
    caminho = texto(caminho)
    inteiro = os.path.abspath(caminho if os.path.isabs(caminho)
                              else os.path.join(CLIENTE, caminho))
    base = os.path.abspath(CLIENTE)
    if not inteiro.lower().startswith(base.lower() + os.sep):
        morre(u'fora do cliente: %s' % inteiro)
    return inteiro[len(base) + 1:].replace('\\', '/')


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        while True:
            bloco = f.read(4 * 1024 * 1024)
            if not bloco:
                break
            h.update(bloco)
    return h.hexdigest()


def varre(alvo):
    u"""Todos os arquivos de um alvo (arquivo ou pasta), sem o lixo.

    Devolve pares (nome dentro do cliente, caminho absoluto), ordenados. A
    ordenacao nao e enfeite: e ela que faz dois `monta_cliente.py` seguidos
    produzirem os mesmos pedacos com os mesmos arquivos dentro, que e a unica
    forma de o `--confere` significar alguma coisa.
    """
    inteiro = alvo if os.path.isabs(alvo) else os.path.join(CLIENTE, alvo)
    if not os.path.exists(inteiro):
        morre(u'nao existe no cliente: %s' % alvo)
    achados = {}
    if os.path.isfile(inteiro):
        if not e_lixo(inteiro):
            achados[relativo(inteiro)] = inteiro
        return sorted(achados.items())
    for pasta, _sub, arquivos in os.walk(inteiro):
        for nome in arquivos:
            cheio = os.path.join(pasta, nome)
            if not e_lixo(cheio):
                achados[relativo(cheio)] = cheio
    return sorted(achados.items())


def nomeados():
    u"""Tudo que os grupos nomeiam - para o grupo `resto` saber o que sobrou."""
    nomes = set()
    for _chave, _rotulo, _tipo, alvos in GRUPOS:
        for alvo in (alvos or []):
            nomes.add(alvo.lower())
    return nomes


def varre_resto():
    u"""O que nao foi nomeado por nenhum grupo e nao e estado local."""
    ja = nomeados()
    fora = set(e.lower() for e in ESTADO) | set(FORA_DO_PACOTE)
    achados = []
    for nome in sorted(os.listdir(CLIENTE)):
        if nome.lower() in ja or nome.lower() in fora:
            continue
        achados.extend(varre(nome))
    return achados


def fatia(arquivos):
    u"""Divide a lista em pedacos de ate MAX_PEDACO bytes brutos.

    Um arquivo maior que o limite vai sozinho no seu pedaco em vez de ser
    recusado: o limite e uma meta de tamanho, nao uma garantia, e travar a
    montagem por causa de um arquivo grande seria pior que um pedaco grande.
    """
    pedacos, atual, soma = [], [], 0
    for interno, cheio in arquivos:
        tamanho = os.path.getsize(cheio)
        if atual and soma + tamanho > MAX_PEDACO:
            pedacos.append(atual)
            atual, soma = [], 0
        atual.append((interno, cheio))
        soma += tamanho
    if atual:
        pedacos.append(atual)
    return pedacos


def monta_zip(destino, arquivos):
    u"""Grava o zip num nome provisorio e so entao renomeia.

    Um erro no meio (arquivo em uso, caminho longo demais para o Windows)
    deixaria para tras um zip incompleto com o nome definitivo, e a rodada
    seguinte o encontraria pronto. Mesmo cuidado do `monta_patch.py`.
    """
    parcial = destino + u'.parte'
    # allowZip64 mesmo com pedaco de 400 MB: o custo e zero e o dia em que
    # alguem subir o MAX_PEDACO nao deve virar um erro obscuro de formato.
    with zipfile.ZipFile(parcial, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        for interno, cheio in arquivos:
            z.write(cheio, interno)
    if os.path.exists(destino):
        os.remove(destino)
    os.rename(parcial, destino)


def le_registro():
    u"""Formato de linha, separado por TAB:

        numero  arquivo  sha256  bytes  tipo  descricao
    """
    if not os.path.exists(REGISTRO):
        return []
    itens = []
    with io.open(REGISTRO, 'r', encoding='utf-8') as f:
        for n, linha in enumerate(f, 1):
            linha = linha.rstrip(u'\r\n')
            if not linha.strip() or linha.lstrip().startswith(u'#'):
                continue
            campos = linha.split(u'\t')
            if len(campos) != 6:
                morre(u'%s linha %d: esperava 6 campos separados por TAB, veio %d'
                      % (REGISTRO, n, len(campos)))
            itens.append({'numero': int(campos[0]), 'arquivo': campos[1],
                          'sha': campos[2], 'bytes': int(campos[3]),
                          'tipo': campos[4], 'nome': campos[5]})
    return itens


def grava_registro(itens):
    L = [
        u'# Guerra do Emperium - a BASE do cliente, para o primeiro download.',
        u'#',
        u'# GERADO por ferramentas/monta_cliente.py. Este arquivo E a lista que',
        u'# o instalador baixa: o publica_cliente.sh o envia ao bucket como',
        u'# base.txt, sem traducao.',
        u'#',
        u'# Uma linha por pedaco, campos separados por TAB:',
        u'#     numero  arquivo  sha256  bytes  tipo  descricao',
        u'#',
        u'# tipo `zip`   extrai por cima da raiz do cliente',
        u'# tipo `bruto` grava no caminho que esta no proprio campo `arquivo`',
        u'#',
        u'# Ao contrario do patches.txt, este arquivo E REESCRITO INTEIRO a cada',
        u'# montagem, e os numeros podem mudar. Pode, porque ninguem guarda',
        u'# "base aplicada": quem instalou ja instalou, e daqui para a frente so',
        u'# ve patches. O que NAO pode e trocar os arquivos no bucket enquanto',
        u'# alguem esta baixando - por isso o publicador sobe os pedacos antes',
        u'# da lista, como o de patch faz.',
        u'',
    ]
    for i in itens:
        L.append(u'%04d\t%s\t%s\t%d\t%s\t%s' % (i['numero'], i['arquivo'],
                                                i['sha'], i['bytes'],
                                                i['tipo'], i['nome']))
    L.append(u'')
    pasta = os.path.dirname(REGISTRO)
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    with io.open(REGISTRO, 'w', encoding='utf-8', newline='\n') as f:
        f.write(u'\n'.join(L))


def mb(n):
    return n / 1048576.0


def monta(so=None):
    if not os.path.isdir(SAIDA):
        os.makedirs(SAIDA)

    itens, numero = [], 0
    total_bruto = 0
    for chave, rotulo, tipo, alvos in GRUPOS:
        arquivos = varre_resto() if alvos is None else []
        for alvo in (alvos or []):
            arquivos.extend(varre(alvo))
        arquivos = sorted(set(arquivos))
        if not arquivos:
            morre(u'grupo "%s" ficou vazio - o cliente mudou de forma?' % chave)

        for interno, _cheio in arquivos:
            if interno.lower() in FORA_DO_PACOTE:
                morre(u'%s nao entra no pacote: o jogador ja o tem, e o '
                      u'instalador nao pode gravar por cima de si mesmo' % interno)

        print u''
        print u'%s (%s)' % (rotulo, chave)
        print u'-' * 66

        if tipo == 'bruto':
            # Nada e copiado: o pedaco E o arquivo do cliente, e o publicador
            # sobe de la. Copiar 2,95 GB para outra pasta so para subir seria
            # meia hora de disco e 3 GB a toa.
            for interno, cheio in arquivos:
                numero += 1
                tamanho = os.path.getsize(cheio)
                total_bruto += tamanho
                print u'  %-52s %9.1f MB' % (interno, mb(tamanho))
                print u'    conferindo sha256...'
                itens.append({'numero': numero, 'arquivo': interno,
                              'sha': sha256(cheio), 'bytes': tamanho,
                              'tipo': u'bruto', 'nome': rotulo})
            continue

        pedacos = fatia(arquivos)
        for n, pedaco in enumerate(pedacos, 1):
            numero += 1
            bruto = sum(os.path.getsize(c) for _i, c in pedaco)
            total_bruto += bruto
            nome_zip = u'%04d-%s%s.zip' % (numero, chave,
                                           u'-%d' % n if len(pedacos) > 1 else u'')
            destino = os.path.join(SAIDA, nome_zip)
            rotulo_pedaco = rotulo if len(pedacos) == 1 else \
                u'%s (%d de %d)' % (rotulo, n, len(pedacos))
            print u'  %-30s %5d arquivos  %8.1f MB bruto' % (
                nome_zip, len(pedaco), mb(bruto))
            if so and so != chave and os.path.exists(destino):
                print u'    (mantido)'
            else:
                monta_zip(destino, pedaco)
            itens.append({'numero': numero, 'arquivo': nome_zip,
                          'sha': sha256(destino),
                          'bytes': os.path.getsize(destino),
                          'tipo': u'zip', 'nome': rotulo_pedaco})

    grava_registro(itens)

    comprimido = sum(i['bytes'] for i in itens)
    print u''
    print u'=' * 66
    print u'%d pedacos, %.2f GB brutos, %.2f GB para o jogador baixar' % (
        len(itens), total_bruto / 1073741824.0, comprimido / 1073741824.0)
    print u'Registro: %s' % REGISTRO
    print u'Pedacos:  %s' % SAIDA
    print u''
    print u'Agora: ferramentas/publica_cliente.sh'


def confere():
    u"""Confere cada linha do registro contra o arquivo que ela descreve.

    E o que separa "o registro esta certo" de "o registro descreve o que existe
    em disco" - as duas coisas que a montagem promete e que nada mais verifica.
    """
    itens = le_registro()
    if not itens:
        morre(u'registro vazio: rode sem argumento para montar')
    ruins = 0
    for i in itens:
        if i['tipo'] == u'bruto':
            caminho = os.path.join(CLIENTE, i['arquivo'].replace(u'/', os.sep))
        else:
            caminho = os.path.join(SAIDA, i['arquivo'])
        if not os.path.exists(caminho):
            print u'  FALTA    %s' % i['arquivo']
            ruins += 1
            continue
        tamanho = os.path.getsize(caminho)
        if tamanho != i['bytes']:
            print u'  TAMANHO  %s (registro %d, disco %d)' % (
                i['arquivo'], i['bytes'], tamanho)
            ruins += 1
            continue
        if sha256(caminho) != i['sha']:
            print u'  SHA256   %s' % i['arquivo']
            ruins += 1
            continue
        print u'  ok       %-44s %9.1f MB' % (i['arquivo'], mb(tamanho))
    print u''
    if ruins:
        morre(u'%d de %d pedacos nao conferem' % (ruins, len(itens)))
    print u'%d pedacos conferem.' % len(itens)


def lista():
    itens = le_registro()
    if not itens:
        print u'Nada montado ainda.'
        return
    total = 0
    for i in itens:
        total += i['bytes']
        print u'%04d  %-34s %8.1f MB  %-5s  %s' % (
            i['numero'], i['arquivo'], mb(i['bytes']), i['tipo'], i['nome'])
    print u''
    print u'%d pedacos, %.2f GB' % (len(itens), total / 1073741824.0)


def main():
    args = [texto(a) for a in sys.argv[1:]]
    if u'--confere' in args:
        return confere()
    if u'--lista' in args:
        return lista()
    so = None
    if u'--so' in args:
        pos = args.index(u'--so')
        if pos + 1 >= len(args):
            morre(u'--so precisa do nome do grupo (%s)'
                  % u', '.join(g[0] for g in GRUPOS))
        so = args[pos + 1]
        if so not in [g[0] for g in GRUPOS]:
            morre(u'grupo desconhecido: %s (ha %s)'
                  % (so, u', '.join(g[0] for g in GRUPOS)))
    if not os.path.isdir(CLIENTE):
        morre(u'cliente nao encontrado: %s' % CLIENTE)
    # Antes de qualquer sha256 de 3 GB: o apontamento e' a unica coisa que faz
    # um pacote inteiro e correto nao servir para nada.
    if u'--permite-local' not in args:
        confere_apontamento()
    monta(so)


if __name__ == '__main__':
    main()
