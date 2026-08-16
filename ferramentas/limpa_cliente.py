# -*- coding: utf-8 -*-
u"""Tira do cliente o que nao deve ser empacotado nem clicado.

    python limpa_cliente.py              # so' mostra (nao move nada)
    python limpa_cliente.py --executar   # move de verdade

Duas faxinas diferentes, e nenhuma delas APAGA - as duas MOVEM:

  1. os BACKUPS que as proprias ferramentas deixam (`*BACKUP*`, `.ORIGINAL`,
     `.INGLES`, `.KOREA`) vao para `C:\\GuerraDoEmperium\\_backups_removidos\\`,
     fora do cliente. Sao 65 arquivos e 711 MB medidos em 2026-08-12 - 28 deles
     copias de 22 MB do itemInfo.lua.

  2. os EXECUTAVEIS do kRO que sobraram na raiz vao para `cliente\\_extras\\`.
     O jogador nao deve clicar em nenhum deles: o `Ragnarok.exe` e' o lancador
     oficial (que fala com o servidor da Gravity), o `Init.exe` e' do patcher
     coreano, e os `Ragexe*` sao a base do nosso exe.

**Mover e nao apagar nao e' excesso de zelo.** Entre os backups estao as duas
unicas copias do exe ANTES dos nossos patches (`Ragexe.exe.original` e o
`GuerraDoEmperium.exe.ORIGINAL-com-acentos-sem-fonte`), e o exe e' o unico
arquivo do cliente sem gerador versionado - o `.epi` do NEMO diz QUAIS patches
foram aplicados, nao com que parametros. Apagar sairia de graca hoje e caro no
dia em que alguem precisasse refazer um patch de exe.

O que fica na raiz, de proposito:

    Jogar.exe             o que o jogador clica
    GuerraDoEmperium.exe  o jogo
    Setup.exe             configuracao de video, que o jogador usa de verdade

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import codecs
import os
import shutil
import sys

sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout, 'replace')

CLIENTE = ur'C:\GuerraDoEmperium\cliente'
BACKUPS = ur'C:\GuerraDoEmperium\_backups_removidos'
EXTRAS = os.path.join(CLIENTE, u'_extras')

# Os mesmos marcadores que o monta_patch.py usa para nao empacotar lixo. Se um
# dia divergirem, o patch levaria backup para o jogador.
LIXO = (u'BACKUP', u'.ORIGINAL', u'.original', u'.INGLES', u'.KOREA', u'.KOR')

# Executavel do kRO que sobrou na instalacao e nao serve ao jogador. `Setup.exe`
# NAO entra: e' o unico que ele tem motivo para abrir.
DO_KRO = (u'Ragnarok.exe', u'RagnarokReplay.exe', u'Init.exe', u'SavePath_Rag.exe',
          u'Ragexe.exe', u'Ragexe_unpacked.exe', u'Ragexe.exe.original')

# O que nunca se move, aconteca o que acontecer. A rede de protecao existe
# porque um padrao mal escrito aqui tira o jogo da pasta em silencio.
INTOCAVEIS = (u'jogar.exe', u'jogar.ini', u'guerradoemperium.exe', u'setup.exe',
              u'data.grf', u'atualizador.exe', u'atualizador.ini')


def e_lixo(nome):
    return any(marca in nome for marca in LIXO)


def acha():
    u"""Devolve (backups, extras) como listas de (caminho, tamanho)."""
    backups, extras = [], []
    for pasta, _sub, arquivos in os.walk(CLIENTE):
        if pasta.startswith(EXTRAS):
            continue
        for nome in arquivos:
            if nome.lower() in INTOCAVEIS:
                continue
            cheio = os.path.join(pasta, nome)
            try:
                tamanho = os.path.getsize(cheio)
            except OSError:
                continue
            if e_lixo(nome):
                backups.append((cheio, tamanho))
            elif pasta == CLIENTE and nome in DO_KRO:
                extras.append((cheio, tamanho))
    return backups, extras


def mostra(titulo, itens, destino):
    total = sum(t for _c, t in itens)
    print u''
    print u'%s -> %s' % (titulo, destino)
    print u'-' * 74
    for cheio, tamanho in sorted(itens, key=lambda x: -x[1])[:12]:
        print u'  %-58s %8.1f MB' % (cheio[len(CLIENTE) + 1:][:58], tamanho / 1048576.0)
    if len(itens) > 12:
        print u'  ... e mais %d arquivo(s)' % (len(itens) - 12)
    print u'-' * 74
    print u'  %d arquivo(s), %.1f MB' % (len(itens), total / 1048576.0)
    return total


def move(itens, destino):
    for cheio, _tamanho in itens:
        relativo = cheio[len(CLIENTE) + 1:]
        alvo = os.path.join(destino, relativo)
        pasta = os.path.dirname(alvo)
        if not os.path.isdir(pasta):
            os.makedirs(pasta)
        if os.path.exists(alvo):
            os.remove(alvo)  # ja movido antes; a copia nova e' a que vale
        shutil.move(cheio, alvo)


def main(argv):
    executar = '--executar' in argv
    backups, extras = acha()

    total = 0
    total += mostra(u'BACKUPS das ferramentas', backups, BACKUPS)
    total += mostra(u'EXECUTAVEIS do kRO', extras, EXTRAS)

    print u''
    if not executar:
        print u'Nada foi movido. Para mover de verdade:'
        print u'    python limpa_cliente.py --executar'
        return

    move(backups, BACKUPS)
    move(extras, EXTRAS)
    print u'Movidos %.1f MB. O cliente ficou %.1f MB mais leve para empacotar.' % (
        total / 1048576.0, total / 1048576.0)


if __name__ == '__main__':
    main(sys.argv[1:])
