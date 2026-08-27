# -*- coding: utf-8 -*-
"""Tinge a luz de um mapa, para a Prontera da Anomalia Dimensional.

    python tinge_dimensao.py                      # mostra a luz de hoje
    python tinge_dimensao.py --aplicar            # grava o override no cliente
    python tinge_dimensao.py --reverter           # apaga o override
    python tinge_dimensao.py --aplicar --difusa 1,0.55,0.80 --ambiente 0.62,0.3,0.68

POR QUE ISTO EXISTE
-------------------
No bRO a Anomalia Dimensional acontece numa copia CORROMPIDA da cidade -
mesmo mapa, ceu errado. Aqueles mapas de evento sao de 2024 e nao existem
no nosso cliente de 2021-11-03, entao o evento roda na `pprontera`, que e
uma copia limpa de Prontera que ja mora no GRF. Esta ferramenta e o que
faz a copia PARECER outra dimensao: ela troca a cor da luz do mapa.

Nao ha textura nova, nao ha modelo novo, nao ha .gnd (que tem 3,3 MB e
pesaria no patch). So os 24 bytes de luz do .rsw - e eles multiplicam
TUDO que e desenhado ali, entao o mapa inteiro muda de clima de uma vez.

ONDE ELE GRAVA, E POR QUE ISSO IMPORTA
--------------------------------------
Em `cliente\\data\\pprontera.rsw`, que vence o GRF pelo DataFolderFirst.
Ou seja: e mudanca de CLIENTE. Ela NAO vai ao jogador pelo implanta.sh -
precisa de patch (CLAUDE.md 4.18, RECEITAS.md secao 0). Quem nao receber o
patch joga a Anomalia inteira, sem erro nenhum, numa Prontera de cor
normal: a falha e calada e so cosmetica.

O ORIGINAL NUNCA SAI DO GRF, entao `--reverter` e so apagar o arquivo -
nao ha backup a manter, e e a mesma logica do destroi_mapa.py.

A LUZ, EM NUMEROS
-----------------
A `pprontera` nasce com difusa (1,00 / 1,00 / 1,00) e ambiente
(0,55 / 0,50 / 0,50) - exatamente a mesma luz da `prontera` de verdade,
conferido em 2026-08-26; as duas sao o mesmo mapa com nomes diferentes.

A INTENSIDADE, DE 1 A 10
------------------------
Nao se escolhem seis floats: escolhe-se UM numero. O `--intensidade`
mistura a luz de fabrica com um alvo quente, e 0 devolve a Prontera
normal enquanto 10 entrega o alvo puro. Assim calibrar e trocar um
digito, e a cor nunca "vira outra coisa" no meio do caminho - so fica
mais forte ou mais fraca na mesma direcao.

O ALVO E QUENTE: vermelho intacto, verde um pouco abaixo e AZUL BEM
ABAIXO. Tirar azul e o que produz laranja; a primeira tentativa desta
ferramenta (2026-08-26) fez o contrario - derrubou o verde e SUBIU o
azul - e o resultado foi magenta puro, um rosa-choque que nao lembrava
nada. Verde baixo + azul alto = rosa. Azul baixo = laranja. E a unica
coisa que se precisa lembrar aqui.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grf
import rsw

GRF_CLIENTE = r'C:\GuerraDoEmperium\cliente\data.grf'
PASTA_DATA = r'C:\GuerraDoEmperium\cliente\data'
MAPA = 'pprontera'

# A luz de fabrica da pprontera, lida do GRF em 2026-08-26. E o ponto de
# partida da mistura, ou seja o que a intensidade 0 devolve.
BASE_DIFUSA = (1.00, 1.00, 1.00)
BASE_AMBIENTE = (0.55, 0.50, 0.50)

# O alvo da intensidade 10. Terceira versao, e a que ficou:
#
#   1a) difusa (1,00 / 0,55 / 0,80) - verde baixo e AZUL ALTO. Deu MAGENTA,
#       um rosa-choque. Azul acima do verde puxa para o rosa.
#   2a) difusa (1,00 / 0,72 / 0,45) - azul bem abaixo. Deu laranja limpo,
#       mas "muito suave" a 3/10: sem azul nenhum a dimensao vira so uma
#       tarde bonita, e nao uma fenda.
#   3a) a de agora - vermelho intacto, verde ABAIXO do azul, e o azul num
#       meio-termo. E o que da um roxo avermelhado: o verde e quem tem de
#       cair mais, nao o azul.
#
# A regra que sobra: quem manda no matiz e a POSICAO RELATIVA de verde e
# azul. B > G puxa para o roxo/rosa; B < G puxa para o laranja; a distancia
# entre os dois e o quanto disso aparece.
ALVO_DIFUSA = (1.00, 0.58, 0.74)
ALVO_AMBIENTE = (0.74, 0.36, 0.62)

# Calibrado em jogo, em tres rodadas no mesmo dia (2026-08-26): 3/10 no alvo
# laranja ficou "muito suave", 4/10 no alvo roxo agradou, e o pedido final foi
# "aumentar o rosa pra 6/10".
INTENSIDADE = 6.0


def mistura(base, alvo, intensidade):
    """Interpola base->alvo. 0 = luz de fabrica, 10 = alvo puro."""
    t = max(0.0, min(10.0, intensidade)) / 10.0
    return tuple(round(b + (a - b) * t, 3) for b, a in zip(base, alvo))


def _trio(texto):
    partes = [p.strip() for p in texto.split(',')]
    if len(partes) != 3:
        raise argparse.ArgumentTypeError('esperado R,G,B (tres numeros)')
    return tuple(float(p) for p in partes)


def _le_original():
    """O .rsw de fabrica, sempre do GRF - nunca do override."""
    g = grf.Grf(GRF_CLIENTE)
    return g.read('data\\%s.rsw' % MAPA)


def _destino():
    return os.path.join(PASTA_DATA, '%s.rsw' % MAPA)


def mostra():
    bruto = _le_original()
    r = rsw.Rsw(bruto)
    print 'ORIGINAL (do data.grf)'
    print '  difusa   R %.3f  G %.3f  B %.3f' % tuple(r.luz_difusa)
    print '  ambiente R %.3f  G %.3f  B %.3f' % tuple(r.luz_ambiente)
    d = _destino()
    if os.path.exists(d):
        r2 = rsw.Rsw(open(d, 'rb').read())
        print
        print 'OVERRIDE no cliente (%s)' % d
        print '  difusa   R %.3f  G %.3f  B %.3f' % tuple(r2.luz_difusa)
        print '  ambiente R %.3f  G %.3f  B %.3f' % tuple(r2.luz_ambiente)
    else:
        print
        print 'Sem override: o cliente mostra a Prontera de cor normal.'
        print 'Aplicar com --aplicar.'
    print
    print 'A ESCALA (difusa R,G,B  |  ambiente R,G,B):'
    for i in (0, 1, 2, 3, 4, 6, 8, 10):
        dd = mistura(BASE_DIFUSA, ALVO_DIFUSA, i)
        aa = mistura(BASE_AMBIENTE, ALVO_AMBIENTE, i)
        marca = '  <- o preset' if i == int(INTENSIDADE) else ''
        print '  %2d  %.3f,%.3f,%.3f  |  %.3f,%.3f,%.3f%s' % (
            (i,) + dd + aa + (marca,))


def aplica(difusa, ambiente):
    bruto = _le_original()
    r = rsw.Rsw(bruto)

    # A trava do rsw.py: ler e reescrever sem mexer tem que devolver os
    # bytes originais. Sem isso nao ha como saber se o layout esta certo -
    # e layout errado nao da erro, da arquivo corrompido.
    r.verificar()

    antes_d = tuple(r.luz_difusa)
    antes_a = tuple(r.luz_ambiente)
    r.luz_difusa = list(difusa)
    r.luz_ambiente = list(ambiente)
    saida = r.to_bytes()

    # Confere a ida: reler o resultado tem que devolver os numeros pedidos,
    # e o arquivo tem que ter o MESMO tamanho (so trocamos 24 bytes).
    volta = rsw.Rsw(saida)
    assert len(saida) == len(bruto), 'tamanho mudou: %d -> %d' % (len(bruto), len(saida))
    for i in range(3):
        assert abs(volta.luz_difusa[i] - difusa[i]) < 1e-6, 'difusa nao gravou'
        assert abs(volta.luz_ambiente[i] - ambiente[i]) < 1e-6, 'ambiente nao gravou'

    difs = sum(1 for i in range(len(bruto)) if bruto[i] != saida[i])

    if not os.path.isdir(PASTA_DATA):
        os.makedirs(PASTA_DATA)
    d = _destino()
    open(d, 'wb').write(saida)

    print 'gravado: %s' % d
    print '  difusa   %.3f,%.3f,%.3f  ->  %.3f,%.3f,%.3f' % (antes_d + tuple(difusa))
    print '  ambiente %.3f,%.3f,%.3f  ->  %.3f,%.3f,%.3f' % (antes_a + tuple(ambiente))
    print '  %d bytes no total, %d diferentes do original' % (len(saida), difs)
    print
    print 'O cliente so rele o mapa ao ENTRAR nele - se voce ja estiver na'
    print 'pprontera, saia e volte (ou reabra o cliente).'
    print 'ISTO E CLIENTE: vai ao jogador por PATCH, nao por deploy.'


def reverte():
    d = _destino()
    if not os.path.exists(d):
        print 'nao havia override; nada a fazer'
        return
    os.remove(d)
    print 'apagado: %s' % d
    print 'O cliente volta a ler a pprontera do GRF, com a cor de Prontera.'


def main():
    p = argparse.ArgumentParser(description='Tinge a luz da pprontera')
    p.add_argument('--aplicar', action='store_true')
    p.add_argument('--reverter', action='store_true')
    p.add_argument('--intensidade', type=float, default=INTENSIDADE,
                   help='0 a 10; 0 e a Prontera normal (padrao: %d)' % INTENSIDADE)
    p.add_argument('--difusa', type=_trio, default=None,
                   help='sobrepoe a intensidade, se voce quiser os floats na mao')
    p.add_argument('--ambiente', type=_trio, default=None)
    a = p.parse_args()

    difusa = a.difusa or mistura(BASE_DIFUSA, ALVO_DIFUSA, a.intensidade)
    ambiente = a.ambiente or mistura(BASE_AMBIENTE, ALVO_AMBIENTE, a.intensidade)

    if a.reverter:
        reverte()
    elif a.aplicar:
        if not a.difusa and not a.ambiente:
            print 'intensidade %g de 10' % a.intensidade
        aplica(difusa, ambiente)
    else:
        mostra()
    return 0


if __name__ == '__main__':
    sys.exit(main())
