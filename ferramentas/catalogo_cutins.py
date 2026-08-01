# -*- coding: utf-8 -*-
"""Catálogo dos cutins (retratos de NPC) que ESTE cliente sabe desenhar.

Python 2.7, como o resto de ferramentas/.

Um "cutin" é a ilustração que aparece ao lado do diálogo. No script é uma
linha só:

    cutin "kafra_01",2;     // 2 = canto inferior direito
    ...
    close2;
    cutin "",255;           // 255 = limpa. SEM ISTO a imagem fica na tela.

O cliente lê o arquivo de `data\\texture\\<UI>\\illust\\`, onde `<UI>` é o
nome coreano 유저인터페이스 (bytes CP949 C0AF C0FA C0CE C5CD C6E4 C0CC BDBA).
Confirmado de duas fontes independentes: doc/script_commands.txt do rAthena e
o literal cru dentro do próprio executável deste cliente.

CUIDADO com a pasta `data\\texture\\userinterface\\illust` (nome em ASCII), que
também existe no GRF com 106 arquivos: o executável NÃO a usa para cutin. A
única string ASCII de illust nele é `UserInterface\\illust\\PET_NOIMAGE.bmp`,
um caso isolado. Pôr arte lá não aparece no jogo.

Este script só LÊ o GRF. A saída é um .md para consulta e grep.

    python ferramentas/catalogo_cutins.py <data.grf> [saida.md]
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grf import Grf


SEP = chr(92)                       # backslash, para não brigar com escapes
# 유저인터페이스 em CP949, escrito por bytes para o arquivo continuar ASCII.
UI_KR = ''.join(chr(int(b, 16)) for b in
                'C0 AF C0 FA C0 CE C5 CD C6 E4 C0 CC BD BA'.split())
PASTA = 'data' + SEP + 'texture' + SEP + UI_KR + SEP + 'illust' + SEP


def coleta(grf):
    """Devolve (nomes_ascii, n_coreanos, n_des) da pasta que o cliente lê."""
    nomes, coreanos, des = [], 0, 0
    for chave in sorted(grf.entries):
        if not chave.startswith(PASTA.lower()):
            continue
        entrada = grf.entries[chave]
        base = entrada[5].rsplit(SEP, 1)[-1]
        if entrada[3] & 6:
            des += 1
        if not all(ord(c) < 128 for c in base):
            coreanos += 1
            continue
        if base.lower().endswith('.bmp'):
            base = base[:-4]
        nomes.append(base)
    return nomes, coreanos, des


def agrupa(nomes):
    """Agrupa pelo prefixo alfabético inicial, que é como a Gravity nomeia."""
    grupos = {}
    for n in nomes:
        m = re.match(r'^([a-zA-Z]+)', n)
        grupos.setdefault(m.group(1).lower() if m else '(sem prefixo)',
                          []).append(n)
    return grupos


def escreve(saida, nomes, coreanos, des):
    grupos = agrupa(nomes)
    L = []
    A = L.append
    A('# Catálogo de cutins — os retratos de NPC deste cliente')
    A('')
    A('> Gerado por `ferramentas/catalogo_cutins.py`. Para refazer:')
    A('> `python ferramentas/catalogo_cutins.py <data.grf> CATALOGO-CUTINS.md`')
    A('')
    A('**%d** ilustrações de nome ASCII, em %d prefixos.'
      % (len(nomes), len(grupos)))
    A('Existem ainda **%d** de nome coreano, fora desta lista: o nome teria de'
      % coreanos)
    A('ser escrito em CP949 dentro do script, o que não vale o trabalho.')
    A('')
    A('## Como usar')
    A('')
    A('```')
    A('mes "[Emissario da Ordem]";')
    A('cutin "kafra_01",2;      // 2 = canto inferior direito')
    A('mes "Boa viagem.";')
    A('close2;')
    A('cutin "",255;            // 255 = limpa a tela')
    A('end;')
    A('```')
    A('')
    A('Posições: `0` inferior esquerdo, `1` inferior centro, `2` inferior')
    A('direito, `3` centro em janela arrastável, `4` centro sem moldura,')
    A('`255` limpa tudo.')
    A('')
    A('**A armadilha:** o cliente desenha um cutin por vez e ele NÃO some')
    A('sozinho quando o diálogo fecha. Sem o `cutin "",255;` antes do `end`,')
    A('a ilustração fica na tela do jogador até ele falar com outro NPC que')
    A('a troque. Todo caminho que sai do script precisa limpar — inclusive')
    A('os que saem por `close` no meio de um `if`.')
    A('')
    A('## Onde a arte mora')
    A('')
    A('Dentro do `data.grf`, em `data\\texture\\유저인터페이스\\illust\\`')
    A('(`유저인터페이스` = "interface do usuário", em CP949).')
    A('')
    A('Não confundir com `data\\texture\\userinterface\\illust`, que também')
    A('existe no GRF com 106 arquivos de nome ASCII: **o executável não lê')
    A('essa pasta para cutin.** A única string ASCII de illust dentro dele é')
    A('`UserInterface\\illust\\PET_NOIMAGE.bmp`, um caso isolado. Arte posta')
    A('lá não aparece.')
    A('')
    A('Para pôr ilustração nossa, o caminho é o mesmo dos outros overrides:')
    A('gravar o `.bmp` em `cliente\\data\\texture\\유저인터페이스\\illust\\`,')
    A('que vence o GRF pelo `DataFolderFirst`. Magenta (`#FF00FF`) é tratado')
    A('como transparente. O tamanho típico é 320x480; acima de ~700x700 o')
    A('cliente trava por um instante ao carregar.')
    A('')
    A('## Por que não dá para pré-visualizar tudo fora do jogo')
    A('')
    A('**%d** dos arquivos desta pasta estão com a flag DES do GRF ligada, e o'
      % des)
    A('`ferramentas/grf.py` recusa esses de propósito — ele não implementa a')
    A('cifra. O cliente lê todos normalmente; a limitação é só nossa. O DES')
    A('bate justamente nos retratos clássicos de NPC (`job_*`, `aca_*`,')
    A('`nov_*`, `moc_*` e quase todos os `kafra_*`), então extrair só os')
    A('livres dá uma amostra enviesada.')
    A('')
    A('Duas saídas: um extrator de GRF que saiba DES (o GRF Editor, do Tokei,')
    A('mostra miniatura), ou testar no jogo mesmo — `cutin` aceita qualquer')
    A('nome desta lista e o custo de errar é ver a tela em branco.')
    A('')
    A('## Os nomes')
    A('')
    for p in sorted(grupos, key=lambda x: (-len(grupos[x]), x)):
        lista = sorted(grupos[p])
        A('### `%s` — %d' % (p, len(lista)))
        A('')
        A('`' + '`, `'.join(lista) + '`')
        A('')

    with open(saida, 'wb') as f:
        f.write('\n'.join(L))
    return len(grupos)


def main():
    if len(sys.argv) < 2:
        print __doc__
        return 1
    grf = Grf(sys.argv[1])
    nomes, coreanos, des = coleta(grf)
    if not nomes:
        print 'nenhum cutin encontrado em %r - o GRF e o esperado?' % PASTA
        return 1
    saida = sys.argv[2] if len(sys.argv) > 2 else 'CATALOGO-CUTINS.md'
    n = escreve(saida, nomes, coreanos, des)
    print '%d cutins ASCII (+%d coreanos, %d com DES) em %d prefixos -> %s' % (
        len(nomes), coreanos, des, n, saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
