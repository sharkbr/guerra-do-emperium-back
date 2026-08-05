# -*- coding: utf-8 -*-
u"""Traduz o dialogo dos NPCs do rAthena, por catalogo.

    python traduz_npcs.py --extrair kafra        # gera/atualiza o catalogo
    python traduz_npcs.py --aplicar kafra        # escreve nos arquivos
    python traduz_npcs.py --aplicar tudo --verificar
    python traduz_npcs.py --estado               # quanto ja foi traduzido

------------------------------------------------------------------ o problema

Sao ~15 mil falas espalhadas por centenas de arquivos do rAthena. Editar
arquivo a arquivo nao termina, nao da para revisar e nao sobrevive a uma
atualizacao do vendor.

E ha um conflito com a CONVENCAO DE CUSTOMIZACAO (PENDENCIAS.md): "tudo que e
nosso mora em pasta propria, e tocamos arquivo do rAthena so para apontar para
ela". Diálogo traduzido nao tem como morar em pasta propria - o servidor le o
script de onde ele esta.

A saida e separar **fonte** de **resultado**:

  - a TRADUCAO vive em `rathena/npc/guerra/traducao/*.cat`, que e nosso,
    versionado e revisavel linha a linha;
  - o arquivo do rAthena e o RESULTADO de aplicar o catalogo, e pode ser
    refeito a qualquer momento.

No dia da atualizacao do vendor: restaurar os arquivos do upstream, rodar
`--aplicar` de novo, e o que nao casar mais aparece no relatorio em vez de
sumir calado.

------------------------------------------------------------------ o formato

Um registro por texto, no arquivo `.cat`:

    #: npc/kafras/functions_kafras.txt#12 (mes)
    - "Welcome to the"
    + "Bem-vindo a"

**`+ ""` quer dizer "deixa como esta".** E o padrao, e por isso extrair demais
nao faz mal: string que nao deve ser traduzida so fica sem traducao.

A chave e `<arquivo>#<indice>`, onde o indice e a ordem do literal DENTRO do
arquivo - nao o byte, que muda a cada aplicacao. O `- "..."` guarda o original
e serve de trava: se o upstream mudar aquela linha, o original nao bate mais e
a traducao e recusada em vez de ir para o lugar errado.

------------------------------------------------------------------ cuidados

**So string de funcao de exibicao e extraida.** `warp "prontera",...` e
`getitem "Red_Potion"` tem literal tambem, e traduzir aqueles quebraria o
script. A lista esta em `CONTEXTOS`.

**Os arquivos sao gravados em Latin-1**, como todo texto de jogo daqui - ver
PENDENCIAS.md, "Acentuacao no dialogo". UTF-8 poe dois bytes por acento e sai
lixo na tela.

Roda em Python 2.7.
"""
import os
import re
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATHENA = os.path.join(REPO, 'rathena')
CATALOGOS = os.path.join(RATHENA, 'npc', 'guerra', 'traducao')

# Conteudo de um literal de script do rAthena, respeitando escape. Mesma
# licao que custou o cliente em 2026-08-03: ler como `[^"]*` erra em toda
# string que tenha `\"` dentro.
VALOR = r'(?:[^"\\\r\n]|\\.)*'

# As funcoes cujo argumento o jogador LE. Fora desta lista, literal e dado
# tecnico (nome de mapa, de item, de label) e nao se toca.
CONTEXTOS = (
    'mes', 'mesf', 'npctalk', 'dispbottom', 'message', 'select', 'prompt',
    'menu', 'setarray', 'cutin', 'title', 'mesq',
)
RE_CHAMADA = re.compile(
    r'\b(%s)\b([^\r\n;]*)' % '|'.join(CONTEXTOS))
RE_LITERAL = re.compile(r'"(%s)"' % VALOR)

# `setarray` so entra quando o array e de texto de menu. `.@nome$` guarda
# string; um `setarray .@mapas$` de nome de mapa passaria batido se nao fosse
# a regra de "+ vazio = nao traduz" - o revisor ve e deixa em branco.
RE_SETARRAY_TEXTO = re.compile(r'setarray\s+[.@$\w\[\]]*\$')

# Atribuicao a variavel de texto: `.@type$ = "Weapon";`, `.@menu$ += "..."`.
#
# Entrou em 2026-08-04, com o Mestre do Refino. O ticket_refiner.txt guarda a
# palavra "Weapon"/"Armor" numa variavel e depois a INTERPOLA em tres frases de
# `mes`. Sem este contexto o catalogo nao via a palavra, e as tres frases saiam
# meio em portugues e meio em ingles - "Se quiser refinar este ^006400Weapon".
#
# E exatamente o **token interno** que a doutrina de `tokens_intocaveis` manda
# traduzir: nasce e morre no arquivo, e o unico destino dele e a tela. O que
# continua protegido e o nome externo, porque o RE_TECNICO e testado depois e
# ganha de qualquer contexto.
#
# Blast radius medido antes de ligar: +54 pares nos dez catalogos (campal 14,
# guerra 17, kafra 12, servico 11, o resto zero). Nascem VAZIOS, e vazio quer
# dizer "deixa em ingles" - nenhuma traducao existente se mexe. Os indices
# tambem nao andam: eles contam TODOS os literais, justamente para a lista de
# contextos poder crescer (ver `literais_todos`).
RE_ATRIB = re.compile(r'\.?@?[A-Za-z_]\w*\$\s*(?:\+)?=')

GRUPOS = {
    'kafra': ['npc/kafras/functions_kafras.txt',
              'npc/kafras/kafras.txt'],
    'servico': ['npc/merchants/refine.txt',
                'npc/re/merchants/refine.txt',
                'npc/merchants/inn.txt',
                # Entrou em 2026-08-04, junto com o Mestre do Refino. Vinha
                # desligado no rAthena (npc/re/scripts_athena.conf:174) e e
                # ligado pelo nosso npc/guerra/scripts_guerra.conf.
                'npc/re/merchants/ticket_refiner.txt'],
    'cidades': ['npc/cities/prontera.txt',
                'npc/cities/izlude.txt',
                'npc/re/cities/izlude.txt'],
    'guerra': None,       # preenchido por glob, abaixo
    'campal': None,
    'pvp': None,
    'classe1': None,
    'classe2': None,
    'novico': ['npc/jobs/novice/supernovice.txt',
               'npc/re/jobs/novice/novice_skills.txt'],
}


def _glob(*padroes):
    import glob
    saida = []
    for p in padroes:
        saida.extend(sorted(x.replace(os.sep, '/')
                            for x in glob.glob(os.path.join(RATHENA, p))))
    return [x[len(RATHENA.replace(os.sep, '/')) + 1:] if x.startswith(
        RATHENA.replace(os.sep, '/')) else x for x in saida]


GRUPOS['guerra'] = _glob('npc/guild/*.txt', 'npc/guild2/*.txt')
GRUPOS['campal'] = _glob('npc/battleground/*.txt',
                         'npc/battleground/*/*.txt')
GRUPOS['pvp'] = _glob('npc/other/pvp*.txt')
GRUPOS['classe1'] = _glob('npc/re/jobs/1-1/*.txt', 'npc/jobs/1-1e/*.txt')
GRUPOS['classe2'] = _glob('npc/jobs/2-1/*.txt', 'npc/jobs/2-2/*.txt',
                          'npc/jobs/2-1a/*.txt', 'npc/jobs/2-2a/*.txt')


class Erro(Exception):
    pass


# =============================================================== extracao

def literais_todos(dados):
    u"""[(indice, texto, contexto ou None)] de TODOS os literais do arquivo.

    O indice conta todos, exibiveis ou nao. E de proposito: assim ele nao se
    desloca quando a lista de CONTEXTOS mudar, e um catalogo antigo continua
    casando.
    """
    saida = []
    n = 0
    for linha in dados.split('\n'):
        limpa = '' if linha.lstrip().startswith('//') else linha.split('//')[0]
        contexto = None
        m = RE_CHAMADA.search(limpa)
        if m:
            contexto = m.group(1)
            if contexto == 'setarray' and not RE_SETARRAY_TEXTO.search(limpa):
                contexto = None
        elif RE_ATRIB.search(limpa):
            contexto = 'atrib'
        for lit in RE_LITERAL.finditer(linha):
            n += 1
            saida.append((n, lit.group(1), contexto))
    return saida


def literais(dados):
    u"""So os exibiveis, que sao os que entram no catalogo."""
    return [(n, t, c) for n, t, c in literais_todos(dados)
            if c and t.strip() and not t.startswith('#')]


# Funcoes cujo literal e um nome que existe FORA deste arquivo - mapa, item,
# label de evento. Traduzir qualquer um deles quebra o script de verdade.
RE_TECNICO = re.compile(
    r'\b(?:warp|areawarp|savepoint|memo|mapannounce|getmapxy|setmapflag|'
    r'removemapflag|getitem|getitem2|delitem|countitem|checkweight|'
    r'makeitem|monster|areamonster|killmonster|donpcevent|doevent|'
    r'enablenpc|disablenpc|hideoffnpc|hideonnpc|setnpcdisplay|'
    r'initnpctimer|stopnpctimer|instance_npcname|getvariableofnpc|'
    r'callfunc|callsub|setd|getd|guildopenstorage|npcshopitem)\s*\(?\s*"'
    r'(%s)"' % VALOR)


# Label de evento: `OnTouch`, `OnInit`, `Algum NPC::OnAlgo`. A forma importa.
#
# A primeira versao era `t.startswith('On')`, e isso marcava como label toda
# fala que comecasse com "On" - `"Once again,"`, `"Only you can..."`, `"On the
# other hand"`. Elas ficavam em ingles no meio do dialogo traduzido, sem erro
# nenhum, so um relatorio dizendo "e nome de mapa, item ou label". Label de
# verdade nao tem espaco e tem maiuscula depois do `On`.
RE_LABEL = re.compile(r'^(?:\S*::)?On[A-Z]\w*$')


def tokens_intocaveis(dados):
    u"""Textos que NAO podem ser traduzidos de jeito nenhum.

    A primeira versao desta trava era grossa demais: recusava todo texto que
    aparecesse fora de funcao de exibicao. So que o menu da Kafra e
    exatamente isso -

        setarray .@K_Menu0$[0], "Save", "Use Storage", "Cancel";
        ...
        if (.@escolha$ == "Use Storage") ...

    - e recusar teria deixado o menu inteiro em ingles. A string ali e um
    **token interno**: nasce e morre dentro do arquivo, entao traduzir TODAS
    as ocorrencias dela e seguro, e e o que a ferramenta faz.

    O que nao pode mudar e o nome que existe fora do arquivo: mapa (`warp
    "prontera"`), item (`getitem "Red_Potion"`), label de evento
    (`donpcevent "Coisa::OnAlgo"`). Esses sao os de verdade, e sao os que esta
    funcao devolve.

    Foi um caso real que ensinou a diferenca, no `functions_kafras.txt`:

        setarray @wrpD$[0], "Izlude", "Geffen", "Orc Dungeon", ...
        else if (@wrpD$[.@j] == "Orc Dungeon") warp "gef_fild10", 52, 326;

    "Orc Dungeon" e token interno - da para traduzir os dois lados. O
    `"gef_fild10"` do `warp` e nome de mapa - nunca se toca. Traduzir so o
    `setarray` faria o teletransporte parar em silencio: menu bonito em
    portugues, destino que nunca chega.
    """
    intocaveis = set(RE_TECNICO.findall(dados))
    for _, t, _c in literais_todos(dados):
        if RE_LABEL.match(t):
            intocaveis.add(t)
    return intocaveis


def extrair(grupo, arquivos):
    caminho = os.path.join(CATALOGOS, grupo + '.cat')
    antigo = carregar(caminho) if os.path.exists(caminho) else {}

    blocos = []
    novos = mantidos = 0
    for rel in arquivos:
        p = os.path.join(RATHENA, rel.replace('/', os.sep))
        if not os.path.exists(p):
            continue
        # A FONTE E SEMPRE O INGLES. Se o `--aplicar` ja passou por este
        # arquivo, ele deixou um `.INGLES` ao lado e o arquivo vivo esta em
        # portugues -- extrair dali gravaria a TRADUCAO na linha `-`, que e a
        # trava, e a linha `+` sairia vazia. O catalogo perderia o original e
        # ficaria sem como recusar mudanca do upstream depois.
        #
        # Aconteceu em 2026-08-04, ao acrescentar um arquivo novo a um grupo
        # ja aplicado: um `--extrair servico` esvaziou 595 pares do
        # servico.cat de uma vez. Um `git checkout` desfez, mas o proximo pode
        # nao perceber -- o comando nao da erro, so imprime "595 mudaram no
        # upstream", que parece informacao e nao estrago.
        fonte = p + '.INGLES' if os.path.exists(p + '.INGLES') else p
        fh = open(fonte, 'rb')
        dados = fh.read()
        fh.close()
        itens = literais(dados)
        if not itens:
            continue
        blocos.append('\n### %s  (%d textos)\n' % (rel, len(itens)))
        for idx, texto, ctx in itens:
            chave = '%s#%d' % (rel, idx)
            traducao = ''
            velho = antigo.get(chave)
            if velho and velho[0] == texto:
                traducao = velho[1]
                mantidos += 1 if traducao else 0
            elif velho:
                novos += 1     # o upstream mudou este texto
            blocos.append('#: %s (%s)\n- "%s"\n+ "%s"\n'
                          % (chave, ctx, texto, traducao))

    if not os.path.isdir(CATALOGOS):
        os.makedirs(CATALOGOS)
    fh = open(caminho, 'wb')
    fh.write(CABECALHO % grupo)
    fh.write(''.join(blocos))
    fh.close()
    total = sum(1 for b in blocos if b.startswith('#: '))
    print '%-10s %5d textos, %d ja traduzidos, %d mudaram no upstream' % (
        grupo, total, mantidos, novos)
    return total


CABECALHO = '''\
# Catalogo de traducao PT-BR - grupo "%s"
#
# GERADO por ferramentas/traduz_npcs.py --extrair, e depois EDITADO A MAO.
# Editar apenas as linhas `+`. Re-extrair preserva o que ja foi traduzido.
#
#   #: <arquivo>#<indice> (<contexto>)
#   - "<original em ingles>"     <- trava: se o upstream mudar, recusa
#   + "<traducao>"               <- vazio quer dizer "deixa em ingles"
#
# Arquivo em Latin-1 (ISO-8859-1). Ver PENDENCIAS.md, "Acentuacao no dialogo".
'''


# =============================================================== aplicacao

RE_REG = re.compile(r'^#: (\S+) \([^)]*\)\r?\n- "(.*)"\r?\n\+ "(.*)"\r?$',
                    re.M)


def carregar(caminho):
    u"""chave -> (original, traducao)."""
    fh = open(caminho, 'rb')
    dados = fh.read()
    fh.close()
    saida = {}
    for m in RE_REG.finditer(dados):
        saida[m.group(1)] = (m.group(2), m.group(3))
    return saida


def aplicar(grupo, arquivos, verificar):
    caminho = os.path.join(CATALOGOS, grupo + '.cat')
    if not os.path.exists(caminho):
        raise Erro('nao existe catalogo para "%s" - rode --extrair antes'
                   % grupo)
    cat = carregar(caminho)
    traduzidos = sum(1 for _, t in cat.values() if t)
    print '%-10s catalogo com %d textos, %d traduzidos' % (grupo, len(cat),
                                                           traduzidos)

    mudou = trocas = recusas = travados = 0
    avisados = set()
    for rel in arquivos:
        p = os.path.join(RATHENA, rel.replace('/', os.sep))
        if not os.path.exists(p):
            continue
        fh = open(p, 'rb')
        dados = fh.read()
        fh.close()

        # Um texto do catalogo vale para TODAS as ocorrencias dele no
        # arquivo, e nao so para a que foi extraida - senao o rotulo do menu
        # sai traduzido e o `if` que o compara continua em ingles. Ver
        # `tokens_intocaveis`.
        intocaveis = tokens_intocaveis(dados)
        porto = {}
        for chave, (orig, trad) in cat.items():
            if not trad or not chave.startswith(rel + '#'):
                continue
            if orig in intocaveis:
                if orig not in avisados:
                    avisados.add(orig)
                    print ('    NAO TRADUZO %r: e nome de mapa, item ou '
                           'label' % orig[:50])
                travados += 1
                continue
            porto[orig] = trad

        # Aplica de tras para frente: assim o offset dos anteriores nao muda.
        alvos = []
        n = 0
        for lit in RE_LITERAL.finditer(dados):
            n += 1
            atual = lit.group(1)
            if atual in porto:
                alvos.append((lit.start(1), lit.end(1), porto[atual]))
                continue
            par = cat.get('%s#%d' % (rel, n))
            if not par or not par[1]:
                continue
            if par[0] in intocaveis:
                continue
            if lit.group(1) != par[0]:
                # So recusa quando o texto tambem nao e o traduzido - senao
                # seria um falso alarme a cada segunda aplicacao.
                if lit.group(1) != par[1]:
                    recusas += 1
                    print ('    RECUSADO %s#%d: o original mudou\n'
                           '      catalogo: %r\n'
                           '      arquivo : %r' % (rel, n, par[0],
                                                   lit.group(1)))
                continue
            alvos.append((lit.start(1), lit.end(1), par[1]))

        if not alvos:
            continue
        novo = dados
        for ini, fim, texto in reversed(alvos):
            novo = novo[:ini] + texto + novo[fim:]

        confere(dados, novo, rel)
        if novo == dados:
            continue
        trocas += len(alvos)
        mudou += 1
        if not verificar:
            backup = p + '.INGLES'
            if not os.path.exists(backup):
                shutil.copy2(p, backup)
            fh = open(p, 'wb')
            fh.write(novo)
            fh.close()

    print ('           %d arquivos, %d textos trocados, %d recusas, '
           '%d travados por serem dado' % (mudou, trocas, recusas,
                                           travados))
    if verificar:
        print '           --verificar: nada gravado'
    return mudou


def confere(antes, depois, rel):
    u"""Trava estrutural, na mesma linha da do traduz_ptbr.py.

    O script do rAthena e sensivel a linha e a aspas: uma aspa a mais faz o
    parser engolir o resto do arquivo, e o erro sai na subida do servidor
    citando uma linha que nao tem nada a ver.
    """
    if antes.count('\n') != depois.count('\n'):
        raise Erro('%s mudou de numero de linhas' % rel)
    if len(RE_LITERAL.findall(antes)) != len(RE_LITERAL.findall(depois)):
        raise Erro('%s mudou de numero de literais' % rel)
    for i, linha in enumerate(depois.split('\n'), 1):
        if linha.count('"') % 2:
            if antes.split('\n')[i - 1].count('"') % 2:
                continue          # ja era assim no original
            raise Erro('%s linha %d ficou com aspas impares' % (rel, i))


# ================================================================ glossario

GLOSSARIO = os.path.join(CATALOGOS, 'glossario.cat')

RE_GLOS = re.compile(r'^- "(.*)"\r?\n\+ "(.*)"\r?$', re.M)


def carrega_glossario():
    if not os.path.exists(GLOSSARIO):
        return {}
    fh = open(GLOSSARIO, 'rb')
    d = fh.read()
    fh.close()
    return dict((m.group(1), m.group(2)) for m in RE_GLOS.finditer(d)
                if m.group(2))


def preencher(forcar=False):
    u"""Copia o glossario para dentro dos catalogos, por texto identico.

    43% dos 19260 textos sao repeticao - `Cancel`, `[Kafra Employee]`, o nome
    de cada NPC que se repete uma vez por fala. Traduzir por OCORRENCIA seria
    fazer o mesmo trabalho 8357 vezes e ainda arriscar traduzir diferente nos
    dois lugares.

    Aqui a unidade e o texto distinto: traduz uma vez no glossario, entra em
    todo catalogo onde aquele texto aparecer.
    """
    glos = carrega_glossario()
    print 'glossario: %d textos traduzidos' % len(glos)
    total = 0
    for nome in sorted(GRUPOS):
        p = os.path.join(CATALOGOS, nome + '.cat')
        if not os.path.exists(p):
            continue
        fh = open(p, 'rb')
        d = fh.read()
        fh.close()
        postos = [0]

        def troca(m):
            orig, atual = m.group(2), m.group(3)
            novo = glos.get(orig)
            if novo and (not atual or (forcar and atual != novo)):
                postos[0] += 1
                return '#: %s\n- "%s"\n+ "%s"' % (m.group(1), orig, novo)
            return m.group(0)

        novo = re.sub(r'^#: (\S+ \([^)]*\))\r?\n- "(.*)"\r?\n\+ "(.*)"\r?$',
                      troca, d, flags=re.M)
        if postos[0]:
            fh = open(p, 'wb')
            fh.write(novo)
            fh.close()
        print '  %-9s +%d' % (nome, postos[0])
        total += postos[0]
    print '%d textos preenchidos.' % total
    return 0


# =================================================================== driver

def resolve(nomes):
    if 'tudo' in nomes:
        return sorted(GRUPOS.items())
    faltando = [n for n in nomes if n not in GRUPOS]
    if faltando:
        raise Erro('grupo desconhecido: %s (conhecidos: %s)'
                   % (', '.join(faltando), ' '.join(sorted(GRUPOS))))
    return [(n, GRUPOS[n]) for n in nomes]


def estado():
    print '%-10s %8s %8s %6s' % ('grupo', 'textos', 'feitos', '%')
    for nome in sorted(GRUPOS):
        p = os.path.join(CATALOGOS, nome + '.cat')
        if not os.path.exists(p):
            print '%-10s %8s' % (nome, '(sem catalogo)')
            continue
        cat = carregar(p)
        feitos = sum(1 for _, t in cat.values() if t)
        pct = 100.0 * feitos / len(cat) if cat else 0
        print '%-10s %8d %8d %5.1f%%' % (nome, len(cat), feitos, pct)
    return 0


def main(argv):
    if '--estado' in argv:
        return estado()
    if '--preencher' in argv:
        # --forcar tambem SOBRESCREVE traducao que divirja do glossario. Sem
        # ele so os vazios sao preenchidos, o que preserva ajuste feito a mao
        # num catalogo. Com ele o glossario vira a verdade - foi preciso ao
        # descobrir que cinco nomes de habilidade nao batiam com os do bRO.
        return preencher('--forcar' in argv)
    verificar = '--verificar' in argv
    nomes = [a for a in argv if not a.startswith('--')]
    if '--extrair' in argv:
        total = 0
        for nome, arqs in resolve(nomes or ['tudo']):
            total += extrair(nome, arqs)
        print '\n%d textos no total.' % total
        return 0
    if '--aplicar' in argv:
        for nome, arqs in resolve(nomes or ['tudo']):
            aplicar(nome, arqs, verificar)
        if not verificar:
            print '\nMudanca em script de NPC pega com @reloadscript.'
        return 0
    print __doc__
    print 'grupos: %s' % ' '.join(sorted(GRUPOS))
    return 1


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Erro as e:
        print 'ERRO: %s' % e
        sys.exit(1)
