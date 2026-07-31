# Ferramentas de inspeção do cliente

Escritas em 2026-07-30 para diagnosticar o erro `RecommendedQuestInfoLoad`.
Rodam em **Python 2.7** (`C:\Python27\python.exe`), que já está instalado nesta
máquina por causa do `get4.py` do NEMO.

## `traduz_setup.py` — põe o `Setup.exe` em português

```
python traduz_setup.py <Setup.exe>              # aplica (faz backup antes)
python traduz_setup.py <Setup.exe> --verificar  # só relata, não grava
```

O `Setup.exe` da Gravity já traz os diálogos compilados em **sete idiomas**. O
idioma não vem do locale nem de arquivo de configuração — o exe não importa uma
única API de idioma; o ID do recurso está cravado no código, e no build coreano
é o do par coreano (105/106).

Este script não reescreve texto: faz o `IMAGE_RESOURCE_DATA_ENTRY` do ID coreano
apontar para os bytes do par português (112/139), 8 bytes por diálogo. Os
diálogos coreanos continuam no arquivo.

Os três botões do rodapé não estão nos diálogos — são literais **CP949 em
`.rdata`**. Como o texto novo não cabia no slot original, as strings vão para o
padding zerado do fim de `.text` e os três `push imm32` passam a apontar para lá.

**É idempotente** e valida tudo antes de gravar um byte: aborta se o literal
coreano não aparecer exatamente uma vez, se a referência não for `push imm32`, se
o padding de `.text` não estiver zerado ou se o cave for pequeno. Recalcula o
checksum do PE (o algoritmo foi conferido reproduzindo o checksum do exe
original, byte a byte).

**Para trocar o idioma**, editar `PARES` no topo do arquivo — `103`/`104` é o
par inglês. Ver a tabela completa de IDs no `PENDENCIAS.md`.

**O arquivo fica travado enquanto o Setup estiver aberto.** O Windows deixa
renomear um exe em uso, então o caminho é patchar uma cópia e trocar por
`mv`.

## `grf.py` — extrator de GRF 0x200

```
python grf.py <data.grf> find    <padrao>                # lista nomes que casam
python grf.py <data.grf> get     <nome-exato> <saida>
python grf.py <data.grf> getlike <padrao-ascii> <saida> [indice]
```

Lê o header de 46 bytes, descomprime a tabela de arquivos com zlib e extrai por
nome.

**Limitação conhecida:** não lê entradas com flag DES (`flags & 6`). O GRF oficial
da Gravity tem muitas — inclusive `data\texture\유저인터페이스\loading07.jpg`.

**Por que existe o `getlike`:** caminhos com trecho coreano não sobrevivem ao
console do PowerShell até o `argv` do Python. O `getlike` casa por substring ASCII
dentro do próprio script, contornando o problema.

## `filtra_lub_por_skid.py` — recorta arquivo de habilidade do ROenglishRE

```
python filtra_lub_por_skid.py <skillid-do-GRF.lub> <entrada.lub> <saida.lub>
```

Os arquivos de habilidade do ROenglishRE são tabelas indexadas por constante
(`SKILL_INFO_LIST = { [SKID.NV_BASIC] = {...} }`). A versão de 2026 traz ~140
habilidades de 4ª classe que o nosso cliente de 2021 não conhece. Como
`[nil] = {...}` é erro em Lua, o arquivo inteiro aborta, a tabela nunca é criada
e a janela de habilidades recebe nil — o que estoura em C++ com `0xC0000005`.

Este script mantém só as entradas cuja constante existe no `skillid.lub` do
**nosso** cliente (extraído do GRF com o `grf.py`). Ele também respeita strings ao
contar chaves, porque as descrições têm texto livre.

**É a alternativa a jogar o arquivo fora.** Antes a receita para `.lub` novo
demais era mover para o backup e perder a tradução inteira. Recortar preserva
tudo que o cliente sabe exibir — no caso das habilidades, 1559 de 1694.

**Sempre validar a saída**: além das entradas de primeiro nível, o arquivo tem
referências aninhadas a `SKID` (os pré-requisitos em `_NeedSkillList`). Uma
referência órfã traz o crash de volta. Conferir com:

```
python -c "import re;t=open('saida.lub','rb').read();print len(set(re.findall(r'SKID\.(\w+)',t)))"
```

e comparar com o conjunto conhecido do cliente.

## `rsw.py` e `gnd.py` — leitor/escritor dos arquivos de mapa

```
python rsw.py <mapa.rsw>     # relatorio + verificacao
python gnd.py <mapa.gnd>     # idem
```

Os dois são biblioteca e ferramenta de linha de comando ao mesmo tempo. Rodados
direto, imprimem o que o arquivo contém e **verificam a si mesmos**.

O `.rsw` é o "mundo": luz, água, e a lista de objetos posicionados. Não guarda
geometria — os modelos são referências por nome para `.rsm` dentro do GRF. Por
isso dá para tombar, afundar, clonar e remover prédio mexendo só nele, sem
extrair `.rsm` nenhum (o que importa, porque `.rsm` no GRF oficial está atrás da
flag DES que o `grf.py` ainda não lê; os arquivos de mapa **não** estão).

O `.gnd` é a malha do chão. O que interessa: **cada superfície tem cor BGRA
própria**, multiplicada pela textura na hora de desenhar. Escurecer e amarelar
essas cores suja o chão sem trocar textura alguma — nenhum arquivo novo, nenhum
byte a mais de memória de vídeo.

**O critério de correção é round-trip byte a byte:** ler e reescrever um arquivo
não modificado tem que devolver os bytes originais, e o parser tem que consumir
até o último byte. `verificar()` roda as duas e é chamada antes de qualquer
gravação. Sem isso não há como saber se o layout está certo — e layout errado
não dá erro, dá arquivo corrompido.

Duas coisas que confundiram e estão resolvidas no código:

- os **65520 bytes no fim do `.rsw`** não são sobra: são a QuadTree, 1365 nós de
  48 bytes (árvore de 5 níveis). Derivada do `.gnd`, não da posição dos modelos,
  então mexer em modelo não a invalida;
- os 4 inteiros que a documentação chama de "limites do chão" vêm todos com o
  mesmo valor grande. O alinhamento está certo (a lista de objetos depois deles
  parseia inteira e a quadtree fecha no byte exato), então o campo é isso mesmo
  — só não sabemos o que significa. Preservado sem interpretar.

Versões conferidas: `.rsw` 2.1 e `.gnd` 1.7, que é o que o kRO 2021-11-03 usa.
Fora dessas, os dois **abortam de propósito** em vez de arriscar corromper.

## `destroi_mapa.py` — aplica a temática de destruição num mapa

```
python destroi_mapa.py <pasta-entrada> <pasta-saida> [mapa]
```

Lê `<mapa>.rsw` e `<mapa>.gnd` da entrada e grava as versões destruídas na
saída. A receita inteira é constante no topo do arquivo — calibrar é editar
número e rodar de novo. Semente fixa: mesma entrada dá sempre o mesmo mapa.

A ficção dita o que ele faz: meteoro no mar, e foi a **onda** que destruiu. Onda
tomba, afunda e varre — não abre cratera nem arremessa escombro. Ver
`../CUSTOMIZACAO-VISUAL.md`.

**Recusa rodar em Prontera**, que na ficção é o centro da sobrevivência e já foi
restaurada.

Duas restrições de projeto, e como estão atendidas: o chão suja por **cor de
superfície** em vez de textura nova, e os destroços são **clones de modelos que
o mapa já carrega** em vez de `.rsm` novo. Como se varre mais adereço do que se
cria destroço, a contagem de objetos do mapa **cai** — em Izlude, 679 → 669.

Instalação: copiar a saída para `cliente\data\`, que vence o GRF pelo
`DataFolderFirst`. **Apagar o arquivo reverte**; o original nunca saiu do GRF,
então não há backup a manter.

## `catalogo_mapa.py` — a tabela de modelos traduzida, para conferência humana

```
python catalogo_mapa.py <mapa.rsw> <saida.md>
```

Lista os modelos distintos do mapa com **pasta e nome traduzidos do coreano**, a
quantidade, a faixa de altura, o que a receita do `destroi_mapa.py` faz com cada
um, e uma coluna **"o que é de verdade" que nasce vazia de propósito** — é onde
entra a correção de quem consegue ver o jogo.

Existe por causa de um erro concreto: `나무잡초꽃\나무기둥01.rsm` foi lido como
"pilar de madeira" (`기둥` é pilar) e usado como destroço de construção. Só que a
pasta `나무잡초꽃` é "árvore / erva / flor" — a pasta de **vegetação** — e o
modelo é tronco de árvore, enorme. Deitado a 90° virou tora atravessada na rua.

**A regra: a pasta manda mais que o nome do arquivo.** Por isso o catálogo mostra
sempre as duas, lado a lado, e a tradução literal aparece rotulada como literal.

Também mora aqui o tradutor por **morfema** (`traduz_partes`), usado por este
script e pelo `catalogo_ingame.py`. Enumerar tradução nome a nome não escala:
são 7034 modelos no GRF. Compondo morfema, `민가폐허01a` vira "casa ruina 01a"
a partir de `민가` (casa) + `폐허` (ruína) + o sufixo, e ~80 morfemas cobrem 218
dos 228 modelos de ruína.

Onde o morfema é desconhecido sai `?` — então **o próprio catálogo diz o que
falta no dicionário**. Foi lendo os `?` da primeira rodada que veio a segunda
leva de termos. Ressalva: morfema de uma sílaba (`성` castelo, `벽` parede) pode
casar dentro de outra palavra; o casamento é pelo mais longo primeiro, o que
reduz mas não elimina.

## `gat.py` — leitor de colisão e altura andável

```
python gat.py <mapa.gat>
```

**Só lê, nunca escreve.** O `.gat` é a única camada de mapa que o *servidor*
também consome — é dele que o `map_cache.dat` é gerado — então escrever nele
puxaria regeração de cache. A frente visual usa apenas para saber onde dá para
pisar e em que altura o chão está.

O `.gat` tem o **dobro** da resolução do `.gnd` em cada eixo. Confirmado pelo
tamanho: Izlude é `.gnd` 134×150 e `.gat` 268×300, e
`268 × 300 × 20 + 14 = 1608014`, que é o tamanho exato do arquivo.

## `inventario_rsm.py` — o que existe de modelo 3D no GRF

```
python inventario_rsm.py <data.grf> pastas [saida.md]
python inventario_rsm.py <data.grf> ruina  [saida.md]
python inventario_rsm.py <data.grf> busca <termo-em-portugues> [saida.md]
```

**7034 modelos `.rsm` em 91 pastas.** O `ruina` filtra por termo de destruição no
nome e devolve 228 em 25 pastas, sendo **78 só em `model\모로코`** — incluindo 24
variantes de casa em ruínas (`민가폐허01a`…`14e`), paredes quebradas e ruínas de
castelo.

**O DES não bloqueia isto**, e o motivo vale guardar: a *tabela* do GRF é zlib e
o `grf.py` já a lê inteira, com nome e flag de todo arquivo — o DES protege o
conteúdo das entradas, não o índice. E para plantar um modelo num mapa basta o
**nome**: o `.rsw` referencia por caminho e quem abre o `.rsm` é o cliente.
Só se precisaria do DES para **editar** geometria.

A busca é por nome de arquivo, então **erra nos dois sentidos** — pega o que só
tem a palavra no nome, e perde ruína batizada de outro jeito. Serve para reduzir
o acervo a algo que caiba num catálogo, não para decidir.

## `catalogo_ingame.py` — monta o mapa-catálogo

```
python catalogo_ingame.py <pasta-de-entrada> <pasta-de-saida>              # de um mapa
python catalogo_ingame.py <pasta-de-entrada> <pasta-de-saida> <data.grf>   # do acervo de ruina
```

Gera três coisas de uma vez: o `.rsw` do mapa-catálogo, o script de NPC com as
placas numeradas, e o markdown com as coordenadas de `@warp`.

**Duas fontes, e a diferença é o ponto:** de um **mapa** saem os modelos que
aquele mapa já usa, com a escala real — bom para conferir classificação, mas não
mostra peça nova. Do **GRF** sai o acervo inteiro, inclusive o que nenhum mapa
nosso usa, que é onde estão as ruínas; sem exemplar, vão com escala 1.

A primeira versão só tinha a fonte "mapa", e por isso o catálogo mostrava apenas
os 90 modelos de Izlude — 1,3% do acervo.

Põe **um exemplar de cada modelo, de pé, em grade, com placa numerada ao lado**.
Uma volta a pé resolve o mapa inteiro — que é a diferença para o screenshot (um
caso por vez) e para o catálogo em markdown (depende de adivinhar pelo nome).

Detalhes que importam:

- **apaga a lista de objetos do mapa base inteira** antes de plantar o catálogo,
  então o entulho do mapa base não atrapalha;
- **grade compacta e retangular**, ancorada no ponto do mapa que deixa mais
  pontos em chão livre, com folga de propósito para nenhum modelo ficar de fora;
- **ordem por pasta**, para cada fileira ter um tema e a caminhada fazer sentido;
- clona o exemplar que o mapa de origem usa, **preservando a escala real** — de
  pé e em tamanho verdadeiro, o tronco de árvore teria se denunciado na hora;
- luz forçada para neutra e clara: catálogo é para identificar, não ambientar;
- as placas saem **sem acento**, pela mesma razão dos outros NPCs nossos (ver
  `PENDENCIAS.md`, "Acentuação no diálogo"), com uma rede de segurança que troca
  por `_` qualquer caractere não-ASCII que a tabela não previu.

**A conversão entre coordenada do jogo e coordenada de mundo do `.rsw` foi
medida, não suposta** — é o tipo de erro que não acusa, só põe o modelo no lugar
errado. Ver `../CUSTOMIZACAO-VISUAL.md`, seção do mapa-catálogo.

Mapa base: `prt_fild08`, campo aberto de 400×400, sem DES e no `map_index`. Tem
spawn, mas só de bicho passivo (Poring, Lunatic, Fabre), então nada ataca. A
primeira versão usou `x_prt` e ficou confusa: mapa de cidade, com parede e beco
no meio do catálogo. `x_prt` continua como alternativa — é o único candidato
**sem spawn nenhum** — trocando `MAPA_BASE` no topo do arquivo.

## `luadis.py` — desassemblador de bytecode Lua 5.1

```
python luadis.py <arquivo.lub>
```

Os `.lub` do cliente são bytecode (header `1b 4c 75 61 51`), não texto — busca de
string neles não é confiável. Este script imprime, para cada função, os opcodes
com o **número de linha do fonte original**, as constantes e os globais lidos e
escritos.

Foi o que mostrou que `QuestInfo_f.lua:57` era o laço externo
(`pairs(RecommendedQuestInfoList)`), e não uma tabela aninhada como se supunha.
Também serve para descobrir que global um `.lub` define, via `SETGLOBAL`.

**Só os `.lub` do GRF são bytecode.** Os do ROenglishRE são Lua em **texto puro**
com extensão `.lub` — o cliente lê os dois. Conferir o header antes de gastar
tempo com desassemblador:

```
python -c "print open('x.lub','rb').read(4) == '\x1bLua'"
```

Isso também significa que comparar o tamanho de um arquivo do GRF com o do
ROenglishRE **não diz nada**: um é bytecode e o outro é texto.

**Armadilha ao ler tabela grande de bytecode:** no Lua 5.1 o operando `RK` só
endereça constante até o índice 255. Passando disso o compilador emite `LOADK`
num registrador e o `SETTABLE` passa a referenciar `R<n>` em vez da constante.
Quem lê só as linhas `SETTABLE ... ; B="NOME" C=<valor>` captura apenas as ~127
primeiras entradas e conclui, errado, que a tabela é minúscula. É preciso
acompanhar os `LOADK` e resolver os registradores — ver
`filtra_lub_por_skid.py:skids_do_cliente`.
