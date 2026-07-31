# -*- coding: utf-8 -*-
"""Recorta um .lub do ROenglishRE para as habilidades que o NOSSO cliente conhece.

Os arquivos de habilidade do ROenglishRE sao tabelas Lua indexadas por
constante:

    SKILL_INFO_LIST = {
        [SKID.NV_BASIC] = { ... },
        ...
    }

Quem define `SKID` e o `skillid.lub`. Se usarmos o `skillid.lub` do nosso
cliente (2021) mas um `skillinfolist.lub` de 2026, as ~140 habilidades de 4a
classe viram `SKID.XXX == nil`, e `[nil] = {...}` e erro em Lua ("table index
is nil") que aborta o arquivo inteiro - a tabela nunca e criada e a janela de
habilidades do cliente recebe nil, o que estoura em C++ (0xC0000005).

Este script mantem so as entradas cuja constante existe no `skillid.lub` do
cliente, produzindo um arquivo internamente consistente.

Uso (Python 2.7):

    python filtra_lub_por_skid.py <skillid-do-GRF.lub> <entrada.lub> <saida.lub>

O primeiro argumento e o `skillid.lub` extraido do data.grf (bytecode) com o
`grf.py` - e ele que define o que o cliente conhece de verdade.
"""
import re
import subprocess
import sys
import os

LUADIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'luadis.py')


def skids_do_cliente(caminho_bytecode):
    """Le a tabela SKID do bytecode do cliente e devolve o conjunto de nomes.

    Cuidado: no Lua 5.1 o operando RK so endereca constante ate o indice 255.
    Passando disso o compilador emite LOADK num registrador e o SETTABLE
    referencia R<n>. Ler so os SETTABLE com constante literal captura apenas
    as ~127 primeiras entradas - e da a impressao falsa de um arquivo minusculo.
    """
    out = subprocess.check_output([sys.executable, LUADIS, caminho_bytecode])
    regs = {}
    nomes = set()
    for linha in out.splitlines():
        m = re.search(r'LOADK\s+A=(\d+)\s+Bx=\d+\s+;\s*(.+)$', linha)
        if m:
            regs[int(m.group(1))] = m.group(2).strip()
            continue
        m = re.search(r'SETTABLE\s+A=\d+\s+B=\S+\s+C=\S+\s+;\s*B=(\S+)', linha)
        if m:
            b = m.group(1)
            if b.startswith('R'):
                b = regs.get(int(b[1:]), '')
            b = b.strip('"')
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', b):
                nomes.add(b)
    return nomes


def fatia_entradas(texto):
    """Quebra o corpo da tabela em (nome_do_skid, trecho) na ordem original.

    Conta chaves ignorando as que estiverem dentro de string, porque as
    descricoes tem texto livre.
    """
    entradas = []
    for m in re.finditer(r'\[SKID\.([A-Za-z0-9_]+)\]\s*=\s*\{', texto):
        nome = m.group(1)
        i = texto.index('{', m.start())
        prof = 0
        aspas = False
        j = i
        while j < len(texto):
            c = texto[j]
            if aspas:
                if c == '\\':
                    j += 2
                    continue
                if c == '"':
                    aspas = False
            elif c == '"':
                aspas = True
            elif c == '{':
                prof += 1
            elif c == '}':
                prof -= 1
                if prof == 0:
                    break
            j += 1
        fim = j + 1
        if texto[fim:fim + 1] == ',':
            fim += 1
        entradas.append((nome, m.start(), fim))
    return entradas


def main():
    if len(sys.argv) != 4:
        print __doc__
        return 1
    conhecidas = skids_do_cliente(sys.argv[1])
    texto = open(sys.argv[2], 'rb').read()

    entradas = fatia_entradas(texto)
    if not entradas:
        print "ERRO: nenhuma entrada [SKID.X] = { encontrada em", sys.argv[2]
        return 1

    mantidas = [e for e in entradas if e[0] in conhecidas]
    removidas = [e[0] for e in entradas if e[0] not in conhecidas]

    cabecalho = texto[:entradas[0][1]]
    rodape = texto[entradas[-1][2]:]

    partes = [cabecalho]
    for nome, ini, fim in mantidas:
        partes.append(texto[ini:fim])
        partes.append('\n\t')
    partes.append(rodape.lstrip('\r\n\t, '))

    open(sys.argv[3], 'wb').write(''.join(partes))

    print "SKID conhecidas pelo cliente : %d" % len(conhecidas)
    print "entradas na entrada          : %d" % len(entradas)
    print "mantidas                     : %d" % len(mantidas)
    print "removidas (cliente nao tem)  : %d" % len(removidas)
    if removidas:
        print "   ->", ", ".join(sorted(removidas)[:10]), "..."
    return 0


if __name__ == '__main__':
    sys.exit(main())
