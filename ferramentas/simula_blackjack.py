# -*- coding: utf-8 -*-
"""Mede o vies das mesas de blackjack do Cassino de Comodo.

    python simula_blackjack.py                 # as duas mesas como estao hoje
    python simula_blackjack.py --varredura     # a tabela de vies, para calibrar
    python simula_blackjack.py --maos 200000   # mais maos, menos ruido

POR QUE ELE EXISTE
------------------
As duas mesas do cassino (npc/guerra/cassino_de_comodo.txt) sao VICIADAS de
proposito, e em direcoes opostas: no primeiro andar o baralho ajuda o jogador,
no segundo ajuda a casa. E o gancho de uma quest futura, em que se descobre a
falcatrua.

O problema e que "quanto" nao se responde de cabeca. O vies age nos DOIS lados
da mesa ao mesmo tempo - melhora a mao de um e piora a do outro -, entao o
efeito dele e mais que o dobro do que o numero sugere. Medido: 10% a favor do
jogador nao dao 10% de vantagem, dao +18% de lucro medio, que e faucet de
moeda. O numero que se escolhe a olho erra por muito, e erra para o lado caro.

ELE ESPELHA O SCRIPT, LINHA A LINHA. Se um dia o `S_Compra` do NPC mudar, este
arquivo tem de mudar junto - senao ele passa a medir um jogo que nao existe, e
responde com a mesma cara de certeza. As quatro decisoes que precisam bater:

  1. o baralho e de 52 cartas, sem reposicao dentro da mao, e o que se sorteia
     e o VALOR (1 a 13) proporcional ao que resta de cada um - o naipe so
     enfeita a tela;
  2. o As vale 11 e cai para 1 quando estouraria, e so um As pode valer 11 de
     cada vez (por isso a mao guarda o total DURO e a quantidade de ases);
  3. "a melhor carta" e a que leva ao maior total <= 21; "a pior" e uma que
     estoure, e se nenhuma estoura, a que deixa a mao mais baixa;
  4. o crupie pede ate 17 e para em TODO 17, inclusive mole.

O QUE ESTA EM JOGO HOJE
-----------------------
  primeiro andar   aposta  2   21 natural paga 3:2   vies  5% pro jogador
  segundo andar    aposta 10   21 natural paga 2:1   vies 10% pra casa

A ESTRATEGIA DO JOGADOR MUDA A CONTA, e por isso sao medidas tres. "pede ate
17" e a que quase todo mundo joga; "para sempre" e a do jogador que desconfiou
da mesa de cima e parou de comprar - e ela precisa continuar ruim, senao a
falcatrua tem contra-jogo. "pede ate 12" e o extremo cauteloso.
"""

import random
import sys


def _valor_duro(rank):
    """Quanto a carta soma no total DURO (As conta 1)."""
    if rank == 1:
        return 1
    return 10 if rank > 10 else rank


def _mole(duro, ases):
    """O total que vale: um unico As sobe para 11 se couber em 21."""
    if ases > 0 and duro + 10 <= 21:
        return duro + 10
    return duro


class Mao(object):
    def __init__(self):
        self.duro = 0
        self.ases = 0
        self.cartas = 0

    @property
    def total(self):
        return _mole(self.duro, self.ases)

    def simula(self, rank):
        """O total que esta mao teria com essa carta, sem aceita-la."""
        return _mole(self.duro + _valor_duro(rank),
                     self.ases + (1 if rank == 1 else 0))

    def poe(self, rank):
        self.duro += _valor_duro(rank)
        if rank == 1:
            self.ases += 1
        self.cartas += 1


def compra(resta, mao, modo):
    """Tira uma carta do baralho e poe na mao. Devolve o valor tirado.

    modo: 0 sorteia limpo, +1 escolhe a MELHOR carta para essa mao,
    -1 escolhe a PIOR. A ordem de varredura e a mesma do script - valor 1
    a 13, ficando com o primeiro que empata.
    """
    esc = 0

    if modo > 0:
        alvo = -1
        for r in range(1, 14):
            if resta[r] <= 0:
                continue
            t = mao.simula(r)
            if t <= 21 and t > alvo:
                alvo, esc = t, r
    elif modo < 0:
        alvo = 99
        for r in range(1, 14):
            if resta[r] <= 0:
                continue
            t = mao.simula(r)
            if t > 21:
                esc = r
                break
            if t < alvo:
                alvo, esc = t, r

    # Sorteio limpo - e tambem o que socorre a falcatrua quando o baralho
    # nao tem mais a carta que ela queria.
    if esc == 0:
        i = random.randrange(sum(resta[1:]))
        for r in range(1, 14):
            i -= resta[r]
            if i < 0:
                esc = r
                break

    resta[esc] -= 1
    mao.poe(esc)
    return esc


def rodada(vies, lado, estrategia, bj_lucro):
    """Uma mao. Devolve o lucro do jogador em unidades de aposta.

    lado: +1 a falcatrua favorece o JOGADOR, -1 favorece a CASA.
    """
    resta = [0] + [4] * 13
    jog, cru = Mao(), Mao()

    def modo(de_quem):
        # de_quem: +1 mao do jogador, -1 mao do crupie. Favorecer o jogador
        # e melhorar a mao dele E piorar a do crupie - e o mesmo numero
        # agindo nos dois lados, que e o que dobra o efeito dele.
        if random.randrange(100) >= vies:
            return 0
        return lado * de_quem

    for i in range(4):
        if i % 2 == 0:
            compra(resta, jog, modo(+1))
        else:
            compra(resta, cru, modo(-1))

    if jog.total == 21 or cru.total == 21:
        if jog.total == 21 and cru.total == 21:
            return 0
        return bj_lucro if jog.total == 21 else -1

    while jog.total < 21:
        if estrategia == 'parar':
            break
        if estrategia == 'ate17' and jog.total >= 17:
            break
        if estrategia == 'ate12' and jog.total >= 12:
            break
        compra(resta, jog, modo(+1))
    if jog.total > 21:
        return -1

    while cru.total < 17:
        compra(resta, cru, modo(-1))
    if cru.total > 21:
        return 1
    if cru.total > jog.total:
        return -1
    if cru.total < jog.total:
        return 1
    return 0


ESTRATEGIAS = ('ate17', 'parar', 'ate12')
ROTULO = {'ate17': 'pede ate 17', 'parar': 'para sempre', 'ate12': 'pede ate 12'}


def mede(vies, lado, bj_lucro, maos):
    """{estrategia: (lucro medio %, vitorias %, derrotas %, empates %)}."""
    saida = {}
    for est in ESTRATEGIAS:
        # Semente fixa por estrategia: as tres veem o MESMO baralho, entao a
        # diferenca entre elas e a estrategia e nao o ruido.
        random.seed(20260812)
        lucro = vit = der = emp = 0
        for _ in range(maos):
            r = rodada(vies, lado, est, bj_lucro)
            lucro += r
            if r > 0:
                vit += 1
            elif r < 0:
                der += 1
            else:
                emp += 1
        saida[est] = (100.0 * lucro / maos, 100.0 * vit / maos,
                      100.0 * der / maos, 100.0 * emp / maos)
    return saida


# As duas mesas como estao no npc/guerra/cassino_de_comodo.txt.
# (rotulo, aposta, lucro do 21 natural, vies, lado)
MESAS = [
    ('PRIMEIRO ANDAR (salao leste)  185,94 / 170,94 / 178,92', 2, 3, 5, +1),
    ('SEGUNDO ANDAR  (salao oeste)  77,84 / 102,59 / 92,47 / 45,59', 10, 20, 10, -1),
]


def relatorio(maos):
    for rotulo, aposta, bj, vies, lado in MESAS:
        quem = 'JOGADOR' if lado > 0 else 'CASA'
        print rotulo
        print '  aposta %d, 21 natural da +%d de lucro, vies %d%% a favor do %s' % (
            aposta, bj, vies, quem)
        r = mede(vies, lado, float(bj) / aposta, maos)
        for est in ESTRATEGIAS:
            ev, v, d, e = r[est]
            print '    %-12s lucro medio %+6.2f%% da aposta (%+6.2f moeda por mao)' % (
                ROTULO[est], ev, ev * aposta / 100.0)
            print '                 ganha %4.1f%% das maos, perde %4.1f%%, empata %4.1f%%' % (
                v, d, e)
        print


def varredura(maos):
    for rotulo, aposta, bj, _, lado in MESAS:
        quem = 'JOGADOR' if lado > 0 else 'CASA'
        print '%s - vies a favor do %s, 21 natural +%d sobre %d' % (
            rotulo.split('(')[0].strip(), quem, bj, aposta)
        print '  %5s | %-34s | %-14s | %-14s' % (
            'vies', 'pede ate 17', 'para sempre', 'pede ate 12')
        for vies in (0, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20):
            r = mede(vies, lado, float(bj) / aposta, maos)
            a = r['ate17']
            print '  %4d%% | %+6.2f%%  V%4.1f D%4.1f E%4.1f | %+6.2f%%       | %+6.2f%%' % (
                vies, a[0], a[1], a[2], a[3], r['parar'][0], r['ate12'][0])
        print


def main():
    maos = 80000
    if '--maos' in sys.argv:
        maos = int(sys.argv[sys.argv.index('--maos') + 1])
    print '%d maos por ponto.\n' % maos
    if '--varredura' in sys.argv:
        varredura(maos)
    else:
        relatorio(maos)
    return 0


if __name__ == '__main__':
    sys.exit(main())
