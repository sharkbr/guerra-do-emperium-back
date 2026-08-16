# -*- coding: utf-8 -*-
u"""Monta um patch do cliente: um .zip numerado mais a linha do registro.

    python monta_patch.py --nome "IA do homunculo" AI_sakray data\\sclientinfo.xml
    python monta_patch.py --nome "Arte nova da Ordem" --desde 2026-08-14
    python monta_patch.py --lista          # mostra o que ja foi montado
    python monta_patch.py --confere        # confere o registro contra os .zip

O patch e um zip com caminhos RELATIVOS A RAIZ DO CLIENTE, aplicado por
extracao por cima. Nao ha diff binario e nao ha GRF: o cliente tem
`DataFolderFirst`, entao arquivo solto em `cliente\\data\\` vence o `data.grf`,
e e assim que todo o nosso conteudo ja chega hoje. Extrair por cima e
idempotente - reaplicar o mesmo patch nao muda nada -, o que e o que permite
ao jogador apagar o `patch\\aplicados.txt` e recomecar do zero sem estrago.

    C:\\GuerraDoEmperium\\cliente\\          de onde os arquivos saem
    C:\\GuerraDoEmperium\\patches\\          onde o .zip nasce (fora do git)
    patcher/patches.txt                    o registro, VERSIONADO

O registro e a fonte unica: e ele que o `publica_patch.sh` sobe para o servidor
como `lista.txt`, e e ele que o Atualizador le. Por isso a linha nasce aqui e
nao no servidor - assim o git guarda o historico do que foi publicado, e duas
maquinas nao inventam o mesmo numero.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import codecs
import hashlib
import io
import os
import re
import sys
import time
import unicodedata
import zipfile

# O nome coreano de arquivo tambem quebra a IMPRESSAO, e nao so a leitura: um
# `print` de unicode que o console nao representa estoura com UnicodeEncodeError
# no meio da montagem, depois de o zip ja ter sido escrito. Com 'replace' o nome
# sai como `?????` e a ferramenta segue - o que importa e o byte no zip, nao o
# desenho no terminal. Sem `sys.stdout.encoding` (saida redirecionada para
# arquivo ou cano) o Python 2 nao arrisca nada e devolve None; cp1252 e o certo
# para o console desta maquina.
sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

# Os caminhos nascem UNICODE, e nao e detalhe: a pasta `AI_sakray` do cliente
# tem arquivo com nome COREANO (o manual da IA que veio do kRO). Em Python 2 no
# Windows, `os.walk` com caminho `str` usa a API ANSI e devolve `????` - nome
# que depois estoura com "A sintaxe do nome do arquivo esta incorreta" no
# primeiro `os.stat`. Com caminho `unicode` ele usa a API W e o nome chega
# inteiro; o zipfile grava em UTF-8 com a flag 0x800, que e o que o Go le.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).decode('mbcs')
CLIENTE = ur'C:\GuerraDoEmperium\cliente'
SAIDA = ur'C:\GuerraDoEmperium\patches'
REGISTRO = os.path.join(RAIZ, u'patcher', u'patches.txt')

# O nome do arquivo dentro do zip que lista o que APAGAR do cliente. Comeca com
# `_` e nao existe no cliente de verdade, entao nao ha como colidir com arquivo
# de jogo. O Atualizador le, apaga o que estiver listado e nao extrai este.
APAGAR = '_patch_apagar.txt'

# O lixo que as proprias ferramentas deixam na pasta do cliente. Sao 65 arquivos
# e 711 MB (medido em 2026-08-12, `PENDENCIAS.md` §5b) - 28 deles copias do
# itemInfo.lua, de 22 MB cada. Um `--desde` sem este filtro poe tudo isso no
# patch, e o jogador baixa 600 MB de backup nosso.
LIXO = ('BACKUP', '.ORIGINAL', '.original', '.INGLES', '.KOREA', '.KOR',
        '.pyc', 'Thumbs.db', 'desktop.ini')

# O Atualizador nao entra em patch comum: ele nao consegue sobrescrever a si
# mesmo enquanto roda. Quem o troca e o canal proprio (`patcher.txt`), que
# renomeia o exe em execucao antes de gravar o novo - ver `patcher/LEIAME.md`.
FORA_DO_PATCH = ('atualizador.exe', 'atualizador.ini')


def morre(msg):
    print u'ERRO: %s' % msg
    sys.exit(1)


def sem_acento(texto):
    forma = unicodedata.normalize('NFKD', texto)
    return u''.join(c for c in forma if not unicodedata.combining(c))


def apelido(nome):
    u"""Nome do arquivo a partir da descricao: minusculo, sem acento, com
    hifen. Entra na URL, entao fica em ASCII puro de proposito."""
    s = sem_acento(nome).lower()
    s = re.sub(ur'[^a-z0-9]+', u'-', s).strip(u'-')
    return (s or u'patch')[:40]


def e_lixo(caminho):
    nome = os.path.basename(caminho)
    return any(marca in nome for marca in LIXO)


def le_registro():
    u"""Devolve a lista de patches ja montados, cada um um dicionario.

    Formato de linha, separado por TAB:  numero  arquivo  sha256  bytes  nome
    Comentario com `#` e linha vazia sao ignorados. O arquivo e UTF-8 - ele NAO
    e lido pelo jogo, e sim pelo Atualizador, que desenha com API Unicode.
    """
    if not os.path.exists(REGISTRO):
        return []
    patches = []
    with io.open(REGISTRO, 'r', encoding='utf-8') as f:
        for numero_da_linha, linha in enumerate(f, 1):
            linha = linha.rstrip(u'\r\n')
            if not linha.strip() or linha.lstrip().startswith(u'#'):
                continue
            campos = linha.split(u'\t')
            if len(campos) != 5:
                morre(u'%s linha %d: esperava 5 campos separados por TAB, veio %d'
                      % (REGISTRO, numero_da_linha, len(campos)))
            patches.append({'numero': int(campos[0]), 'arquivo': campos[1],
                            'sha': campos[2], 'bytes': int(campos[3]),
                            'nome': campos[4]})
    return patches


def grava_registro(patches):
    L = []
    L.append(u'# Guerra do Emperium - os patches do cliente, em ordem.')
    L.append(u'#')
    L.append(u'# GERADO por ferramentas/monta_patch.py. Este arquivo E a lista que')
    L.append(u'# o Atualizador baixa: o publica_patch.sh o envia ao servidor como')
    L.append(u'# https://libraro.filiponegrao.com.br/patch/lista.txt, sem traducao.')
    L.append(u'#')
    L.append(u'# Uma linha por patch, campos separados por TAB:')
    L.append(u'#     numero  arquivo  sha256  bytes  descricao')
    L.append(u'#')
    L.append(u'# O numero so cresce e nunca se reaproveita: e ele que o cliente')
    L.append(u'# guarda em patch\\aplicados.txt para saber o que ja tem. Corrigir um')
    L.append(u'# patch publicado se faz com um patch NOVO por cima, nunca editando')
    L.append(u'# ou removendo a linha de um antigo - quem ja aplicou nao voltaria.')
    L.append(u'')
    for p in patches:
        L.append(u'%04d\t%s\t%s\t%d\t%s' % (p['numero'], p['arquivo'], p['sha'],
                                            p['bytes'], p['nome']))
    L.append(u'')
    pasta = os.path.dirname(REGISTRO)
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    with io.open(REGISTRO, 'w', encoding='utf-8', newline='\n') as f:
        f.write(u'\n'.join(L))


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        while True:
            bloco = f.read(1024 * 1024)
            if not bloco:
                break
            h.update(bloco)
    return h.hexdigest()


def texto(caminho):
    u"""Todo caminho que entra vira unicode - ver o comentario do CLIENTE."""
    if isinstance(caminho, str):
        return caminho.decode('mbcs')
    return caminho


def relativo(caminho):
    u"""Caminho relativo a raiz do cliente, com barra normal. Recusa o que
    estiver fora do cliente - o zip so pode falar de dentro dele."""
    caminho = texto(caminho)
    inteiro = os.path.abspath(caminho if os.path.isabs(caminho)
                              else os.path.join(CLIENTE, caminho))
    base = os.path.abspath(CLIENTE)
    if not inteiro.lower().startswith(base.lower() + os.sep):
        morre(u'fora do cliente: %s' % inteiro)
    return inteiro[len(base) + 1:].replace('\\', '/')


def junta(alvos):
    u"""Expande arquivos e pastas numa lista de (caminho absoluto, nome no zip),
    sem o lixo e sem repetir."""
    achados = {}
    for alvo in alvos:
        alvo = texto(alvo)
        inteiro = alvo if os.path.isabs(alvo) else os.path.join(CLIENTE, alvo)
        if not os.path.exists(inteiro):
            morre(u'nao existe: %s' % inteiro)
        if os.path.isfile(inteiro):
            if e_lixo(inteiro):
                print u'  pulado (lixo): %s' % relativo(inteiro)
                continue
            achados[relativo(inteiro)] = inteiro
            continue
        for pasta, _subpastas, arquivos in os.walk(inteiro):
            for nome in arquivos:
                cheio = os.path.join(pasta, nome)
                if e_lixo(cheio):
                    continue
                achados[relativo(cheio)] = cheio
    return sorted(achados.items())


def desde(data):
    u"""Todo arquivo do cliente modificado a partir da data `AAAA-MM-DD`.

    E a via preguicosa, e por isso a mais perigosa: ela pega tambem o que foi
    tocado por engano. O resumo impresso antes de gravar existe para isso -
    conferir a lista ANTES de publicar, sempre.
    """
    try:
        corte = time.mktime(time.strptime(data, '%Y-%m-%d'))
    except ValueError:
        morre(u'data invalida: %s (use AAAA-MM-DD)' % data)
    achados = []
    for pasta, _subpastas, arquivos in os.walk(CLIENTE):
        for nome in arquivos:
            cheio = os.path.join(pasta, nome)
            if e_lixo(cheio):
                continue
            try:
                if os.path.getmtime(cheio) >= corte:
                    achados.append(cheio)
            except OSError:
                pass
    return achados


def monta(nome, alvos, apagar):
    patches = le_registro()
    numero = (patches[-1]['numero'] + 1) if patches else 1
    arquivos = junta(alvos) if alvos else []

    for interno, _cheio in arquivos:
        if interno.lower() in FORA_DO_PATCH:
            morre(u'%s nao entra em patch comum - ele se atualiza pelo canal '
                  u'proprio (patcher/LEIAME.md)' % interno)

    if not arquivos and not apagar:
        morre(u'nada a empacotar')

    destino = os.path.join(SAIDA, '%04d-%s.zip' % (numero, apelido(nome)))
    if not os.path.isdir(SAIDA):
        os.makedirs(SAIDA)
    if os.path.exists(destino):
        morre(u'ja existe: %s' % destino)

    print u''
    print u'Patch %04d - %s' % (numero, nome)
    print u'-' * 60
    bruto = 0
    # Nasce com outro nome e so vira o zip de verdade no fim: um erro no meio
    # (arquivo em uso, nome que o Windows nao alcanca) deixaria para tras um zip
    # incompleto com o nome definitivo, e a rodada seguinte pararia nele.
    parcial = destino + u'.parte'
    with zipfile.ZipFile(parcial, 'w', zipfile.ZIP_DEFLATED) as z:
        for interno, cheio in arquivos:
            tamanho = os.path.getsize(cheio)
            bruto += tamanho
            print u'  + %-58s %8.1f KB' % (interno, tamanho / 1024.0)
            z.write(cheio, interno)
        if apagar:
            for caminho in apagar:
                print u'  - %s' % caminho
            z.writestr(APAGAR, (u'\n'.join(apagar) + u'\n').encode('utf-8'))

    os.rename(parcial, destino)
    tamanho = os.path.getsize(destino)
    marca = sha256(destino)
    patches.append({'numero': numero, 'arquivo': os.path.basename(destino),
                    'sha': marca, 'bytes': tamanho, 'nome': nome})
    grava_registro(patches)

    print u'-' * 60
    print u'  %d arquivo(s), %.2f MB crus -> %.2f MB no zip' % (
        len(arquivos), bruto / 1048576.0, tamanho / 1048576.0)
    print u'  %s' % destino
    print u'  sha256 %s' % marca
    print u''
    print u'Registro atualizado: patcher/patches.txt'
    print u'Publicar com:  ferramentas/publica_patch.sh'


def lista():
    patches = le_registro()
    if not patches:
        print u'Nenhum patch montado ainda.'
        return
    print u''
    for p in patches:
        existe = os.path.exists(os.path.join(SAIDA, p['arquivo']))
        print u'  %04d  %-42s %7.1f KB  %s' % (
            p['numero'], p['nome'][:42], p['bytes'] / 1024.0,
            u'' if existe else u'(zip ausente nesta maquina)')
    print u''


def confere():
    u"""Confere cada linha do registro contra o .zip desta maquina.

    Zip ausente NAO e erro: o registro e versionado e o zip nao, entao uma
    maquina que nunca montou aquele patch simplesmente nao o tem. Erro e o zip
    existir com sha diferente - ai o que esta no servidor e o que esta escrito
    discordam, e quem baixar recebe a recusa do Atualizador.
    """
    problemas = 0
    for p in le_registro():
        caminho = os.path.join(SAIDA, p['arquivo'])
        if not os.path.exists(caminho):
            print u'  %04d  ausente nesta maquina (ok)' % p['numero']
            continue
        marca = sha256(caminho)
        if marca != p['sha']:
            print u'  %04d  SHA DIVERGE  registro=%s  arquivo=%s' % (
                p['numero'], p['sha'][:16], marca[:16])
            problemas += 1
        elif os.path.getsize(caminho) != p['bytes']:
            print u'  %04d  TAMANHO DIVERGE' % p['numero']
            problemas += 1
        else:
            print u'  %04d  ok' % p['numero']
    print u''
    print u'%d problema(s).' % problemas
    sys.exit(1 if problemas else 0)


def main(argv):
    nome = None
    alvos = []
    apagar = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--lista':
            lista()
            return
        elif a == '--confere':
            confere()
            return
        elif a == '--nome':
            i += 1
            nome = argv[i].decode('mbcs') if isinstance(argv[i], str) else argv[i]
        elif a == '--apagar':
            i += 1
            apagar.append(relativo(argv[i]))
        elif a == '--desde':
            i += 1
            alvos.extend(desde(argv[i]))
        elif a.startswith('--'):
            morre(u'opcao desconhecida: %s' % a)
        else:
            alvos.append(a)
        i += 1

    if not nome:
        print __doc__
        return
    monta(nome, alvos, apagar)


if __name__ == '__main__':
    main(sys.argv[1:])
