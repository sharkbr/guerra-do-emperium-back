# -*- coding: utf-8 -*-
u"""aponta_cliente.py - para onde o cliente desta maquina aponta, e como trocar.

    python aponta_cliente.py                # so' diz o estado, nao grava
    python aponta_cliente.py --dev          # aponta para 127.0.0.1 (o padrao daqui)
    python aponta_cliente.py --producao     # aponta para o servidor de verdade

O cliente de C:\\GuerraDoEmperium\\cliente e' o de DEV/HML desde 2026-08-16, e
producao se testa NOUTRA pasta, instalada pelo instalador como um jogador faria
(CLAUDE.md secao 1). Este script existe porque manter esse combinado a mao ja'
falhou duas vezes.

--------------------------------------------------------------------------
O QUE ELE MEXE, E POR QUE SAO DOIS ARQUIVOS E DOIS CAMPOS

Sao DOIS xml, e o que vale e' o segundo: este exe e' `<servertype>sakray`,
entao o par dele e' o `sclientinfo.xml`. Trocar so' o `clientinfo.xml` deixa o
cliente indo para o lugar antigo, e foi uma hora perdida em 2026-08-14. Os dois
se mantem iguais - e' a regra da secao 5 do CLAUDE.md.

E sao DOIS campos por arquivo, nao um:

    <address>   para onde o jogo conecta
    <admin>     a conta que ganha o VISUAL de GM (o group_id 99 do banco da'
                os comandos; quem da' o visual e' esta lista, dentro do
                cliente). A conta de GM daqui e' a 2000000 (`teste`); a de la'
                e' a 2000004 (`librasupremo`), que nem existe neste banco.

Trocar so' o endereco deixa o GM sem visual do outro lado - o que ja' custou o
patch 0004.

--------------------------------------------------------------------------
O QUE DESFEZ O APONTAMENTO, E VAI DESFAZER DE NOVO

Nao foi o sanduiche da RECEITAS secao 11. Foi o **Atualizador**: existe um
`Jogar.exe` dentro da pasta de dev, e o patch 0004 leva os dois clientinfo com
o endereco de PRODUCAO. Rodar o Atualizador ali aplica esse patch e o cliente
de dev vira cliente de producao, sem perguntar nada.

O `monta_patch.py` protege a SAIDA (`confere_apontamento` recusa publicar um
cliente apontado para local). Nada protegia a ENTRADA - e a falha e' calada da
pior maneira: o jogo abre, loga e joga, so' que no servidor errado.

Enquanto o `Jogar.exe` estiver naquela pasta, isso volta a acontecer em todo
patch que leve os xml. O remedio barato e' rodar este script depois - e' um
comando so'.

--------------------------------------------------------------------------
OS BACKUPS SAO DOS DOIS LADOS

Ao lado de cada xml ficam `.BACKUP-127.0.0.1` e `.BACKUP-138.197.155.31`. Ate'
2026-08-18 so' existia o de producao, e por isso o de dev se perdeu quando foi
sobrescrito: nao havia de onde restaurar. Os dois pacotadores ignoram nome com
"BACKUP" (o `LIXO` de `monta_patch.py` e `monta_cliente.py`), entao eles nao
vao para patch nem para a base.
"""
import codecs
import os
import re
import sys

sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(
    sys.stdout, 'replace')

DADOS = ur'C:\GuerraDoEmperium\cliente\data'
ARQUIVOS = (u'clientinfo.xml', u'sclientinfo.xml')

# O `sclientinfo.xml` e' o que vale - ver o cabecalho.
QUE_VALE = u'sclientinfo.xml'

# (endereco, conta de GM). O 138.197.155.31 e' o `libraro.filiponegrao.com.br`
# do REFERENCIA.md; o 2000004 e' a unica conta com group_id 99 la'.
LADOS = {
    u'dev': (u'127.0.0.1', u'2000000'),
    u'producao': (u'138.197.155.31', u'2000004'),
}

RE_END = re.compile(r'<address>([^<]*)</address>')
RE_ADM = re.compile(r'<admin>([^<]*)</admin>')


def morre(msg):
    print u'ERRO: %s' % msg
    sys.exit(1)


def le(nome):
    u"""(bytes, endereco, admin) de um dos xml."""
    caminho = os.path.join(DADOS, nome)
    if not os.path.exists(caminho):
        morre(u'nao achei %s' % caminho)
    d = open(caminho, 'rb').read()
    end = RE_END.findall(d)
    adm = RE_ADM.findall(d)
    if len(end) != 1:
        morre(u'%s tem %d <address> - esperava 1' % (nome, len(end)))
    if len(adm) != 1:
        morre(u'%s tem %d <admin> - esperava 1' % (nome, len(adm)))
    return d, end[0].decode('cp1252').strip(), adm[0].decode('cp1252').strip()


def rotulo(endereco):
    for lado, (end, _) in LADOS.items():
        if endereco == end:
            return lado.upper()
    return u'DESCONHECIDO'


def estado():
    u"""Imprime para onde cada xml aponta. Devolve True se os dois batem."""
    visto = {}
    for nome in ARQUIVOS:
        _, end, adm = le(nome)
        visto[nome] = (end, adm)
        marca = u'  <- e este que vale' if nome == QUE_VALE else u''
        print u'  %-18s %-16s admin %-8s %s%s' % (
            nome, end, adm, rotulo(end), marca)

    ends = set(v[0] for v in visto.values())
    adms = set(v[1] for v in visto.values())
    if len(ends) != 1 or len(adms) != 1:
        print u''
        print u'  !! OS DOIS NAO BATEM. Quem manda e o %s, mas deixar o outro' % QUE_VALE
        print u'     diferente e a receita de uma hora perdida - CLAUDE.md secao 5.'
        return False
    return True


def aplica(lado):
    alvo_end, alvo_adm = LADOS[lado]
    for nome in ARQUIVOS:
        caminho = os.path.join(DADOS, nome)
        d, end, adm = le(nome)

        # Guarda o lado em que ele esta ANTES de mexer - e' o backup que
        # faltava, e sem ele o apontamento de dev se perdeu em 2026-08-18.
        if end in [e for e, _ in LADOS.values()]:
            bkp = u'%s.BACKUP-%s' % (caminho, end)
            if not os.path.exists(bkp) or open(bkp, 'rb').read() != d:
                open(bkp, 'wb').write(d)

        novo = RE_END.sub('<address>%s</address>' % alvo_end.encode('cp1252'), d)
        novo = RE_ADM.sub('<admin>%s</admin>' % alvo_adm.encode('cp1252'), novo)
        if novo != d:
            open(caminho, 'wb').write(novo)

        # E o backup do lado para onde acabamos de ir, para a volta existir.
        bkp = u'%s.BACKUP-%s' % (caminho, alvo_end)
        open(bkp, 'wb').write(novo)

    print u'Agora aponta para %s:' % lado.upper()
    estado()
    print u''
    if lado == u'dev':
        print u'  O cliente so le esses arquivos na ABERTURA - se ele estiver'
        print u'  aberto, fechar e abrir de novo (CLAUDE.md secao 3).'
        print u'  E nao abrir pelo Jogar.exe desta pasta: ele reaplica o patch'
        print u'  que traz o endereco de producao. Abrir pelo GuerraDoEmperium.exe.'
    else:
        print u'  Lembre de voltar para --dev depois de montar o patch.'


def main(argv):
    if not argv:
        print u'Para onde o cliente de C:\\GuerraDoEmperium aponta hoje:'
        print u''
        estado()
        print u''
        print u'  --dev        aponta para 127.0.0.1 (o servidor desta maquina)'
        print u'  --producao   aponta para o servidor de verdade'
        return 0

    if len(argv) != 1 or argv[0] not in (u'--dev', u'--producao'):
        morre(u'use --dev ou --producao, um de cada vez')

    aplica(argv[0][2:])
    return 0


if __name__ == '__main__':
    sys.exit(main([a.decode('mbcs') if isinstance(a, str) else a
                   for a in sys.argv[1:]]))
