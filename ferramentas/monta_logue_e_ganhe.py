# -*- coding: utf-8 -*-
u"""Gera as DUAS metades do Logue e Ganhe a partir de uma tabela so.

    python monta_logue_e_ganhe.py              # grava os dois lados
    python monta_logue_e_ganhe.py --verificar  # so relata, nao grava

O Logue e Ganhe (attendance, no rAthena) e o unico sistema do projeto em que
servidor e cliente guardam a MESMA lista de premios em arquivos diferentes:

    rathena/db/guerra/attendance.yml         quem ENTREGA o premio (RoDEX)
    cliente\\System\\CheckAttendance.lub       quem DESENHA os 20 quadrados

O servidor nao manda a lista para o cliente. O pacote `ZC_UI_OPEN` leva um
numero so - o contador do jogador - e o cliente pinta os icones a partir do
`.lub` dele. Divergir as duas tabelas nao da erro em lugar nenhum: a janela
mostra um item, a caixa de correio entrega outro. Por isso a tabela e escrita
UMA vez, aqui, e os dois arquivos sao saida.

Roda em Python 2.7 (`C:\\Python27\\python.exe`).
"""
import os
import shutil
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML = os.path.join(RAIZ, 'rathena', 'db', 'guerra', 'attendance.yml')
LUB = os.path.join(r'C:\GuerraDoEmperium\cliente', 'System', 'CheckAttendance.lub')
LUAC = r'C:\Users\User\Downloads\ROenglishRE\Tools\luac.exe'

# --------------------------------------------------------------- a receita
#
# ITEM      o mesmo ID do db/guerra/item_db.yml. Moeda Nova, a moeda do reino.
# PREMIOS   um valor por dia, do dia 1 ao dia 20. VINTE E O TETO, e nao e
#           escolha nossa - ver o cabecalho gerado no .yml.
# PRIMEIRO  (ano, mes) do primeiro ciclo. ULTIMO idem, inclusive.
#
# Mudar premio aqui e rodar de novo; nao editar os arquivos gerados a mao.
ITEM = 30998
PREMIOS = [10] * 19 + [50]
PRIMEIRO = (2026, 8)
ULTIMO = (2027, 12)


def ultimo_dia(ano, mes):
    """Ultimo dia do mes. Sem `calendar` de proposito: a regra bissexta cabe
    numa linha e assim a saida nao depende do locale desta maquina."""
    if mes == 2:
        bissexto = (ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0
        return 29 if bissexto else 28
    return 30 if mes in (4, 6, 9, 11) else 31


def ciclos():
    """Um ciclo por mes civil, de PRIMEIRO ate ULTIMO. Mes civil e o que faz o
    contador zerar: o rAthena so zera `#AttendanceCounter` quando a ultima
    retirada do jogador e anterior ao `Start` do periodo corrente."""
    ano, mes = PRIMEIRO
    while (ano, mes) <= ULTIMO:
        yield ano * 10000 + mes * 100 + 1, ano * 10000 + mes * 100 + ultimo_dia(ano, mes)
        mes += 1
        if mes == 13:
            ano, mes = ano + 1, 1


def monta_yaml():
    L = []
    L.append('# Logue e Ganhe - a fonte diaria de Moeda Nova.')
    L.append('#')
    L.append('# GERADO por ferramentas/monta_logue_e_ganhe.py. Nao editar a mao:')
    L.append('# a mesma tabela de premios tambem sai no CheckAttendance.lub do')
    L.append('# cliente, e as duas metades precisam bater byte a byte no premio.')
    L.append('#')
    L.append('# VINTE DIAS E O TETO, e o teto e do CLIENTE, nao nosso. Tres provas:')
    L.append('# o CheckAttendance.lub do kRO 2021-11-03 tem 20 entradas; o do')
    L.append('# ROenglishRE tambem; e o proprio rAthena so abre a janela no login')
    L.append('# quando `pc_attendance_counter(sd) < 200` (src/map/pc.cpp), que e')
    L.append('# `contador < 20`. Pedir um dia 21 aqui nao daria erro - o quadrado')
    L.append('# simplesmente nao existe na janela.')
    L.append('#')
    L.append('# UM CICLO POR MES CIVIL. O contador (`#AttendanceCounter`) so zera')
    L.append('# quando comeca um periodo NOVO, entao periodo unico e longo daria')
    L.append('# 20 dias por conta na vida inteira. Mes a mes, a conta que loga')
    L.append('# todo dia fecha os 20 e recomeca no dia 1 do mes seguinte.')
    L.append('#')
    L.append('# O contador e de CONTA (`#` = variavel de conta), nao de')
    L.append('# personagem - trocar de personagem nao rende de novo.')
    L.append('#')
    L.append('# ESPERADO no boot: o map-server avisa')
    L.append('#   Node "End" date <n> has already passed, skipping.')
    L.append('# uma vez por mes ja vencido. Nao e defeito - e o rAthena pulando')
    L.append('# ciclo velho. Quando o ULTIMO ciclo daqui vencer, o sistema morre')
    L.append('# calado: sem janela, sem erro. Rodar a ferramenta de novo com')
    L.append('# ULTIMO adiantado antes disso.')
    L.append('')
    L.append('Header:')
    L.append('  Type: ATTENDANCE_DB')
    L.append('  Version: 1')
    L.append('')
    L.append('Body:')
    for inicio, fim in ciclos():
        L.append('  - Start: %d' % inicio)
        L.append('    End: %d' % fim)
        L.append('    Rewards:')
        for dia, qtd in enumerate(PREMIOS, 1):
            L.append('      - Day: %d' % dia)
            L.append('        ItemId: %d' % ITEM)
            L.append('        Amount: %d' % qtd)
        L.append('')
    return '\n'.join(L)


def monta_lub():
    """O cliente le UMA janela de datas, nao uma por ciclo - por isso ela cobre
    o intervalo inteiro. Quem separa mes de mes e o servidor; aqui as datas so
    ligam e desligam a janela.

    `Config.EvendOnOff` fica sem valor de proposito: e assim no bytecode do kRO
    2021-11-03 e no arquivo do ROenglishRE. O erro de digitacao e da Gravity, e
    corrigir para `EventOnOff` passaria a mandar um valor onde hoje vai nil."""
    ciclo = list(ciclos())
    L = []
    L.append('-- Logue e Ganhe - Guerra do Emperium')
    L.append('--')
    L.append('-- GERADO por ferramentas/monta_logue_e_ganhe.py. Nao editar a mao:')
    L.append('-- a lista abaixo TEM que ser a mesma de rathena/db/guerra/attendance.yml.')
    L.append('-- O servidor nao manda a lista para ca; ele manda so o contador, e este')
    L.append('-- arquivo e quem decide o icone de cada um dos 20 quadrados. Divergir as')
    L.append('-- duas tabelas nao da erro: a janela promete um item e o correio entrega')
    L.append('-- outro.')
    L.append('--')
    L.append('-- O cliente le este arquivo so na inicializacao - fechar e reabrir.')
    L.append('')
    L.append('Config = {')
    L.append('\tStartDate = %d,' % ciclo[0][0])
    L.append('\tEndDate = %d' % ciclo[-1][1])
    L.append('}')
    L.append('Reward = {')
    for dia, qtd in enumerate(PREMIOS, 1):
        virgula = ',' if dia < len(PREMIOS) else ''
        L.append('\t{ %d, %d, %d }%s' % (dia, ITEM, qtd, virgula))
    L.append('}')
    L.append('function main()')
    L.append('\tresult, msg = InsertCheckAttendanceConfig(Config.EvendOnOff, Config.StartDate, Config.EndDate)')
    L.append('\tif not result then')
    L.append('\t\treturn false, msg')
    L.append('\tend')
    L.append('\tfor k, rewardtbl in pairs(Reward) do')
    L.append('\t\tresult, msg = InsertCheckAttendanceReward(rewardtbl[1], rewardtbl[2], rewardtbl[3])')
    L.append('\t\tif not result then')
    L.append('\t\t\treturn false, msg')
    L.append('\t\tend')
    L.append('\tend')
    L.append('\treturn true, "success"')
    L.append('end')
    L.append('')
    return '\n'.join(L)


def grava(caminho, texto, verificar):
    """Grava com \\r\\n e backup datado. O `.lub` do cliente e o unico arquivo
    aqui que nao esta no git - o backup e a unica volta atras que existe."""
    dados = texto.replace('\n', '\r\n')
    if os.path.exists(caminho):
        if open(caminho, 'rb').read() == dados:
            print '  = igual, nao mexi: %s' % caminho
            return
    if verificar:
        print '  ! mudaria: %s' % caminho
        return
    pasta = os.path.dirname(caminho)
    if not os.path.isdir(pasta):
        os.makedirs(pasta)
    if os.path.exists(caminho):
        backup = '%s.BACKUP-%s' % (caminho, time.strftime('%Y%m%d-%H%M'))
        shutil.copy2(caminho, backup)
        print '  . backup:  %s' % os.path.basename(backup)
    open(caminho, 'wb').write(dados)
    print '  + gravei:  %s' % caminho


def main():
    verificar = '--verificar' in sys.argv
    if len(PREMIOS) != 20:
        print 'PREMIOS tem %d dias; o cliente so desenha 20.' % len(PREMIOS)
        return 1

    ciclo = list(ciclos())
    total = sum(PREMIOS)
    print 'Logue e Ganhe: item %d, %d ciclos (%d a %d), %d por ciclo/conta.' % (
        ITEM, len(ciclo), ciclo[0][0], ciclo[-1][1], total)
    print '  dias 1-%d: %d cada;  dia %d: %d.' % (
        len(PREMIOS) - 1, PREMIOS[0], len(PREMIOS), PREMIOS[-1])

    grava(YAML, monta_yaml(), verificar)
    grava(LUB, monta_lub(), verificar)

    # O `.lub` so falha no cliente, e falha calado. O luac do ROenglishRE e o
    # unico jeito de provar aqui que ele compila - ver CLAUDE.md secao 5.
    if not verificar and os.path.exists(LUAC):
        # subprocess, nao os.system: no cmd do Windows uma linha que COMECA com
        # aspas perde o primeiro par, e o erro que sai ("sintaxe do nome do
        # arquivo incorreta") parece defeito do .lub gerado, que nao e.
        if subprocess.call([LUAC, '-p', LUB]) == 0:
            print '  . luac -p: compila.'
        else:
            print '  ! luac -p RECUSOU o .lub gerado.'
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
