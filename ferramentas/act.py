# -*- coding: utf-8 -*-
"""Leitor de .act (o posicionamento dos quadros de um sprite de RO).

Python 2.7, como o resto de ferramentas/.

O `.spr` guarda os DESENHOS; o `.act` diz, para cada acao e cada quadro, ONDE
cada desenho e colado em relacao a celula do personagem. O par que interessa e
o `(x, y)` de cada CAMADA: e o deslocamento do centro do desenho em relacao ao
ponto de ancoragem no chao.

POR QUE ISSO IMPORTA: `y` perto de zero deixa o CENTRO do sprite na altura do
chao, e a metade de baixo vai para debaixo do piso, onde o depth buffer do
terreno a corta. O resultado na tela e um corte reto e horizontal - o sprite
parece "enterrado". As maquinas oficiais deste cliente levantam o desenho entre
40 e 53 pixels; o `2_COLAVEND` e o unico com `y = 0` nas oito direcoes, e foi
assim que o defeito dele foi achado em 2026-08-12.

Estrutura (versao 2.5, que e a deste cliente):

    "AC" + versao(u16) + n_acoes(u16) + 10 bytes reservados
    por acao:
        n_quadros(u32)
        por quadro:
            32 bytes (range1 + range2)
            n_camadas(u32)
            por camada:
                x(i32) y(i32) indice(i32) espelho(u32)
                cor(4) escalaX(f) escalaY(f) rotacao(i32) tipo(u32)
                largura(i32) altura(i32)          [>= 2.5]
            id_de_evento(i32)                     [>= 2.0]
            n_ancoras(u32) + n * 16               [>= 2.3]
    4 bytes nao identificados                     [ver abaixo]
    n_acoes floats de atraso                      [>= 2.1]

OS 4 BYTES: sem eles sobra exatamente 4 no fim, nos cinco .act de maquina
medidos, e o vetor de atrasos sai deslocado - lido como
[0.0, 4.0 x7] em vez de [4.0 x8]. Pulando-os o arquivo fecha em zero. Nao
descobri o que sao; ficam pulados e documentados, que e melhor que um leitor
que sobra byte (CLAUDE.md secao 5, a regra do mede_rsm.py).

O ALINHAMENTO DOS `(x, y)` FOI PROVADO POR FORA, e nao pelo proprio leitor: no
`2_DROP_MACHINE` as oito camadas dao todas `(6, -44)`, e o padrao de bytes
correspondente aparece exatamente OITO vezes no binario.
"""

import struct


class Act(object):

    def __init__(self, dados):
        b = dados
        if b[:2] != 'AC':
            raise ValueError('nao e um .act: magic %r' % b[:2])
        self.dados = b
        self.versao, = struct.unpack_from('<H', b, 2)
        n_acoes, = struct.unpack_from('<H', b, 4)
        v = self.versao
        p = 6 + 10

        # Uma entrada por camada: (posicao do x no arquivo, x, y). A posicao e
        # o que permite reescrever `y` NO LUGAR, sem re-serializar o resto.
        self.camadas = []
        self.acoes = []

        for _a in range(n_acoes):
            n_quadros, = struct.unpack_from('<I', b, p)
            p += 4
            quadros = []
            for _q in range(n_quadros):
                p += 32
                n_cam, = struct.unpack_from('<I', b, p)
                p += 4
                camadas = []
                for _c in range(n_cam):
                    x, y = struct.unpack_from('<ii', b, p)
                    self.camadas.append((p, x, y))
                    camadas.append((x, y))
                    p += 16                      # x, y, indice, espelho
                    if v >= 0x200:
                        p += 4                   # cor RGBA
                        p += 4                   # escala X
                        if v >= 0x204:
                            p += 4               # escala Y
                        p += 4                   # rotacao
                        p += 4                   # tipo de sprite
                        if v >= 0x205:
                            p += 8               # largura, altura
                if v >= 0x200:
                    p += 4                       # id de evento
                if v >= 0x203:
                    n_anc, = struct.unpack_from('<I', b, p)
                    p += 4 + n_anc * 16
                quadros.append(camadas)
            self.acoes.append(quadros)

        p += 4                                   # ver "OS 4 BYTES", acima
        if v >= 0x201:
            self.atrasos = list(struct.unpack_from('<%df' % n_acoes, b, p))
            p += n_acoes * 4
        else:
            self.atrasos = []

        self.sobra = len(b) - p
        if self.sobra != 0:
            raise ValueError('sobraram %d bytes - leitura desalinhada, os '
                             '(x,y) NAO sao confiaveis' % self.sobra)

    def desloca_y(self, novo_y):
        """Devolve os bytes com o `y` de TODAS as camadas trocado por novo_y.

        Escreve no lugar, byte a byte: tudo o que nao e `y` fica identico, e o
        arquivo mantem o tamanho. Re-serializar o `.act` inteiro seria a outra
        saida, e a pior - qualquer campo que o leitor nao entenda se perderia.
        """
        b = bytearray(self.dados)
        for (pos, _x, _y) in self.camadas:
            struct.pack_into('<i', b, pos + 4, novo_y)
        return bytes(b)
