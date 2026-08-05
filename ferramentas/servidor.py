# -*- coding: utf-8 -*-
"""Sobe, para e confere os servidores do Guerra do Emperium.

O problema que motivou o script: em 2026-08-04 o emblema de cla nao subia. O
clique na lista de emblemas simplesmente nao fazia nada -- sem caixa de erro,
sem linha no chat, sem nada na janela do map-server. A causa era que os
servidores tinham sido subidos com os `.bat` um a um, e o `web-server.exe`
ficou de fora. Com PACKETVER > 20200300 o emblema sobe por HTTP na porta 8888,
entao sem esse processo o upload morre calado.

Sao QUATRO servidores, nao tres. Subir na mao erra silenciosamente, e o
`PENDENCIAS.md` chegou a listar tres por dias sem ninguem notar. Documento nao
se confere sozinho; este script confere.

    python servidor.py status      # o que esta no ar, e o que quebra se nao estiver
    python servidor.py subir       # sobe o que faltar, na ordem certa
    python servidor.py parar       # derruba todos
    python servidor.py reiniciar   # parar + subir

`subir` e idempotente: pula quem ja esta no ar, entao da para rodar a qualquer
momento sem medo de duplicar processo. `status` sai com codigo 1 se algo estiver
fora, para dar de usar em outro script.

Cada servidor abre a PROPRIA janela de console, de proposito. Erro de script de
NPC so aparece na janela do map-server -- nao existe arquivo de log para isso.
"""

import os
import socket
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATHENA = os.path.join(RAIZ, 'rathena')

# A ordem importa: o char precisa do login de pe, e o map precisa do char.
# O web so precisa do banco, mas sobe junto para nao ser esquecido de novo.
#
# nome, executavel, porta, segundos de espera, o que quebra se estiver fora
SERVIDORES = [
    ('login-server', 'login-server.exe', 6900, 40,
     'ninguem loga'),
    ('char-server', 'char-server.exe', 6121, 40,
     'trava na selecao de personagem'),
    ('web-server', 'web-server.exe', 8888, 40,
     'emblema de cla nao sobe -- e a falha e CALADA'),
    ('map-server', 'map-server.exe', 5121, 120,
     'ninguem entra no mapa'),
]

# O banco nao e nosso processo (roda como servico do Windows), mas sem ele
# nenhum servidor sobe, entao entra no status.
BANCO_PORTA = 3306

CREATE_NEW_CONSOLE = 0x00000010


def no_ar(porta):
    """Verdadeiro se da para conectar em 127.0.0.1:porta.

    Testa conectando de fato, em vez de ler a saida do netstat, porque o
    netstat desta maquina pode sair traduzido e a palavra LISTENING vira
    OUVINDO. Conexao nao depende de idioma.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        return s.connect_ex(('127.0.0.1', porta)) == 0
    finally:
        s.close()


def pid_da_porta(porta):
    """PID de quem escuta a porta, ou None. So para exibir -- nunca decide."""
    try:
        saida = subprocess.check_output(['netstat', '-ano', '-p', 'TCP'],
                                        stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError):
        return None
    alvo = ':%d' % porta
    for linha in saida.splitlines():
        campos = linha.split()
        if len(campos) < 5 or not campos[1].endswith(alvo):
            continue
        # LISTENING em ingles, OUVINDO em portugues; o estado e o 4o campo.
        if campos[3].upper() in ('LISTENING', 'OUVINDO'):
            return campos[4]
    return None


def esperar(porta, segundos):
    """Espera a porta abrir. Verdadeiro se abriu dentro do prazo."""
    limite = time.time() + segundos
    while time.time() < limite:
        if no_ar(porta):
            return True
        time.sleep(0.5)
    return False


def cmd_status():
    print
    print '  %-14s %-6s %-8s %s' % ('SERVICO', 'PORTA', 'ESTADO', 'PID')
    print '  ' + '-' * 52

    banco = no_ar(BANCO_PORTA)
    print '  %-14s %-6d %-8s %s' % ('MariaDB', BANCO_PORTA,
                                    'no ar' if banco else 'FORA',
                                    pid_da_porta(BANCO_PORTA) or '')

    fora = []
    if not banco:
        fora.append(('MariaDB', 'nenhum servidor sobe sem o banco'))

    for nome, _exe, porta, _espera, sintoma in SERVIDORES:
        ativo = no_ar(porta)
        print '  %-14s %-6d %-8s %s' % (nome, porta,
                                        'no ar' if ativo else 'FORA',
                                        pid_da_porta(porta) or '')
        if not ativo:
            fora.append((nome, sintoma))

    print
    if not fora:
        print '  Tudo de pe.'
        return 0

    print '  O que voce vai ver no jogo:'
    for nome, sintoma in fora:
        print '    %-14s -> %s' % (nome, sintoma)
    print
    print '  Para resolver:  python servidor.py subir'
    return 1


def cmd_subir():
    if not no_ar(BANCO_PORTA):
        print 'MariaDB nao esta respondendo na porta %d.' % BANCO_PORTA
        print 'Nenhum servidor sobe sem o banco. Confira o servico:'
        print '    Get-Service MariaDB'
        return 1

    if not os.path.isdir(RATHENA):
        print 'Pasta do rathena nao encontrada: %s' % RATHENA
        return 1

    houve_erro = False
    for nome, exe, porta, espera, _sintoma in SERVIDORES:
        if no_ar(porta):
            print '  %-14s ja estava no ar (porta %d)' % (nome, porta)
            continue

        caminho = os.path.join(RATHENA, exe)
        if not os.path.isfile(caminho):
            print '  %-14s ERRO: %s nao existe -- falta compilar?' % (nome, exe)
            houve_erro = True
            continue

        print '  %-14s subindo...' % nome,
        sys.stdout.flush()
        # Janela propria de proposito: erro de script de NPC so aparece la.
        subprocess.Popen([caminho], cwd=RATHENA,
                         creationflags=CREATE_NEW_CONSOLE)

        if esperar(porta, espera):
            print 'no ar (porta %d)' % porta
        else:
            print 'NAO ABRIU a porta %d em %ds' % (porta, espera)
            print '                 veja a janela do %s -- e ali que o erro sai' % nome
            houve_erro = True

    print
    if houve_erro:
        print '  Subida incompleta. Rode "python servidor.py status".'
        return 1
    print '  Os quatro estao de pe.'
    return 0


def cmd_parar():
    # Ordem inversa da subida: o map depende do char, que depende do login.
    parou_algo = False
    for nome, exe, porta, _espera, _sintoma in reversed(SERVIDORES):
        if not no_ar(porta):
            print '  %-14s ja estava fora' % nome
            continue
        subprocess.call(['taskkill', '/F', '/IM', exe],
                        stdout=open(os.devnull, 'w'),
                        stderr=subprocess.STDOUT)
        parou_algo = True
        print '  %-14s parado' % nome

    if parou_algo:
        time.sleep(1.5)

    restou = [n for n, _e, p, _s, _y in SERVIDORES if no_ar(p)]
    if restou:
        print
        print '  Ainda respondendo: %s' % ', '.join(restou)
        return 1
    return 0


def cmd_reiniciar():
    if cmd_parar() != 0:
        return 1
    print
    return cmd_subir()


COMANDOS = {
    'status': cmd_status,
    'subir': cmd_subir,
    'parar': cmd_parar,
    'reiniciar': cmd_reiniciar,
}


def main():
    args = sys.argv[1:]
    if len(args) != 1 or args[0] not in COMANDOS:
        print __doc__
        return 2
    return COMANDOS[args[0]]()


if __name__ == '__main__':
    sys.exit(main())
