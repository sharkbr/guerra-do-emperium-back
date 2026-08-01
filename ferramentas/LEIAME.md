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

## `instala_item.py` — põe a entrada de um item nosso no `itemInfo.lua`

```
python instala_item.py              # aplica (faz backup antes)
python instala_item.py --verificar  # só relata, não grava
python instala_item.py <itemInfo.lua> [--verificar]
```

O `itemInfo.lua` é a tabela que dá **nome, descrição e arte** a cada item do lado
do cliente. Item novo no `item_db` do servidor sem entrada aqui aparece sem nome.
Ele **não é alcançado por `@reloaditemdb`** — é lido uma vez, na inicialização,
então toda mudança exige fechar e reabrir o cliente.

**Por que é script e não edição à mão**, que é a razão de o arquivo existir: o
`itemInfo.lua` tem 22 MB, está em ANSI, e os `resourceName` são **bytes CP949
coreanos**. Editor ou ferramenta que assuma UTF-8 reescreve esses bytes e corrompe
as ~26 mil entradas de uma vez, **sem dar erro** — o estrago só aparece no jogo, e
depois de salvo não dá para saber o que era. Aqui é tudo `rb`/`wb`, byte a byte,
sem decodificar nada.

Isso também resolve o `cliente\` estar fora do git: o **gerador** fica versionado,
a saída não. Rodar o script reconstrói a alteração num cliente novo.

**A receita é a tabela `ITENS` no topo do arquivo** — acrescentar item é editar a
tabela, não o código. O campo `arte_de` é o pulo do gato: em vez de criar ícone,
imagem de *collection* e sprite de chão, ele **copia o `resourceName` de outro
item, em tempo de execução**. `resourceName` é só um nome de recurso, e nada impede
dois IDs apontarem para o mesmo desenho. A Maçã da Inocência (30999) usa a arte da
Maçã comum (512). Quando um item nosso merecer arte exclusiva, aí entra o
`instala_visual.py`.

**É idempotente**: entrada idêntica não faz nada, entrada diferente é substituída
em bloco, e rodar duas vezes nunca duplica. O `--verificar` relata sem gravar um
byte, e o backup vai para `itemInfo.lua.BACKUP-AAAAMMDD-HHMM`.

Uma premissa que foi **medida, não suposta**: o arquivo está ordenado por ID, mas
com **10 inversões locais** (`15877 → 15858` e parecidas). Nenhuma joga um ID
grande para o começo, que é o único caso que enganaria a busca do ponto de
inserção. E mesmo se enganasse, o efeito seria estético — `tbl` é um construtor de
tabela Lua com chave explícita, então a posição não muda nada para o jogo.

Aplicado em 2026-07-31: +670 bytes, entrada entre 29715 e 31000, e o resto do
arquivo **byte a byte idêntico ao backup**.

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

## `edita_mapa.py` — troca e acrescenta modelo num mapa

```
python edita_mapa.py <pasta-entrada> <pasta-saida> <data.grf> [mapa]
```

Substitui o `destroi_mapa.py` na frente de Izlude. A diferença de abordagem é o
ponto: aquele **simulava** destruição inclinando e afundando casa inteira; este
**troca** o modelo pelo de ruína que a Gravity já modelou. Depois que o
inventário mostrou 228 modelos de ruína no GRF, simular deixou de fazer sentido.

Receita declarativa no topo do arquivo, semente fixa. Duas operações:
`substituir` (com fração e sorteio entre vários destinos) e `acrescentar` (por
coordenada de jogo, com a altura lida do `.gat`).

Duas decisões de comportamento que vale conhecer antes de escrever receita:

- **rotação preservada sempre.** Para muro é essencial — um segmento girado 90°
  é outra coisa. Para objeto espalhado, só dá variedade.
- **escala resetada para 1.** A escala do original foi escolhida para *aquele*
  modelo; herdar 1,5 de uma árvore daria uma ossada gigante.

Antes de gravar, **todo `filename` é conferido contra a tabela do GRF**. Caminho
errado não dá erro em parser nenhum: só aparece no cliente, um diálogo por
modelo, e trava quem tiver personagem salvo no mapa.

Não toca luz, água, chão nem `.gat` — nada aqui atravessa a fronteira do
servidor.

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

## `valida_visual.py` — quais chapéus este cliente consegue desenhar

```
python valida_visual.py               # resumo
python valida_visual.py --id 420047   # um item, com os 6 recursos
python valida_visual.py --listar      # os que quebram
python valida_visual.py --ok          # os que funcionam
```

Nasceu do crash do item **420047** (Costume Honorable Knight Cloak): equipar
abria uma caixa de erro modal

```
Spr :: Cannot find File : sprite\<item>\c_h_knight_cloak.spr
```

O ponto que faz o script existir é que **as três tabelas concordavam que o item
existia** — `item_db_equip.yml` do rAthena, `itemInfo.lua` do ROenglishRE e o
próprio `accessoryid.lub` do GRF de 2021 (`ACCESSORY_C_H_Knight_Cloak = 2059`).
Quem discordava era o GRF, que não tem **nenhum** dos seis arquivos. Olhar
tabela não detecta isso; só testar arquivo detecta.

Para cada item de cabeça com `View` no `item_db`, confere os seis caminhos que o
cliente abre — `.spr`/`.act` de chão, ícone de inventário, ícone grande e sprite
de cabeça masculina e feminina —, no GRF **e** no `data\` solto (o
`DataFolderFirst` faz o disco vencer, mas para existir basta um dos dois).

Medido em 2026-07-31, dos 5301 itens de cabeça com `View`:

| | |
|---|---|
| desenháveis | 2709 |
| **quebram o cliente** | **1457** |
| sem entrada no `itemInfo.lua` | 1135 |

Falta de ícone só deixa feio; falta de `.spr`/`.act` é a caixa modal. O script
separa os dois.

## `instala_visual.py` — põe a arte de um chapéu no lugar certo

```
python instala_visual.py --id 420047                     # só mostra os destinos
python instala_visual.py --id 420047 --grf <outra.grf>   # puxa da outra GRF
python instala_visual.py --id 420047 --de C:\extraido    # ou de pasta extraída
python instala_visual.py --todos --grf <outra.grf>       # conta o que daria
python instala_visual.py --todos --grf <outra.grf> --aplicar
```

O par do `valida_visual.py`: aquele diz o que falta, este põe no lugar.

**A fonte é a GRF do bRO**, em
`C:\Program Files (x86)\Gravity Interactive, Inc\Ragnarok Brazil\data.grf`. É
mais nova que a nossa de 2021-11-03 — 205117 entradas — e tem a arte que falta.

Aplicado em 2026-07-31: **5247 arquivos**, e o resultado medido pelo
`valida_visual.py`:

| | antes | depois |
|---|---|---|
| desenháveis | 2709 | **3618** |
| quebram o cliente | 1457 | **548** |

**909 chapéus curados**, e a cura já estava no disco desta máquina.

O que sobrou dos 548, e por quê:

| | |
|---|---|
| `View` fora do `accessoryid.lub` do cliente | 374 |
| a GRF do bRO não tem a arte | 101 |
| a GRF do bRO tem parte da arte | 73 |

Os 374 **não têm cura por arte**: o cliente de 2021 não conhece aquele View, então
não sabe que slot desenhar. Resolver exigiria mexer no `accessoryid.lub`, que é
outro problema.

**Não precisa de GRF Editor nem de repack**, por dois motivos: as entradas de
sprite lá estão com `flags=1` (sem DES), então o `grf.py` lê direto; e o
`DataFolderFirst` faz o disco vencer o GRF, então os arquivos vão soltos para
`cliente\data\` — reversível apagando, versionável, e o servidor não fica
sabendo de nada.

**Em lote é tudo-ou-nada por item.** Instalar só parte é pior que não instalar:
`.spr` sem o `.act` do par quebra o cliente igual, e ainda esconde o problema do
`valida_visual`. Por isso os 73 parciais são pulados em vez de meio-instalados.

**Duas armadilhas de contagem no modo `--todos`**, ambas encontradas rodando de
verdade e ambas subnotificando ou inventando resultado:

1. **Itens diferentes compartilham arquivo** — vários chapéus com o mesmo `View`
   usam a mesma sprite de cabeça. Depois que o primeiro do lote a instala, os
   seguintes não têm mais nada a instalar. Contar isso como fracasso fez a
   primeira passada relatar 752 resolvidos quando o `valida_visual` media 909.
2. **`View` fora do `accessoryid.lub`** — esses itens só têm os 4 arquivos de
   item, sem os 4 de cabeça. Se o contador não os separa, "nada falta" vira
   "resolvido" e o lote relata sucesso sem tocar em arquivo nenhum. Foi assim
   que uma passada disse 164 resolvidos e o `valida_visual` continuou acusando
   os mesmos 548.

A lição prática: **o `valida_visual.py` é a medida, o `instala_visual.py` é a
ação.** Quando os dois discordam, quem está errado é o contador do instalador.

O que o script resolve é a parte que se perde na mão: **os destinos têm pasta em
coreano** (`아이템`, `악세사리`, `남`, `여`, `유저인터페이스`), e o arquivo de
cabeça começa com o caractere de gênero — `남_C_H_Knight_Cloak.spr`. Já está
registrado que caminho com trecho coreano não sobrevive ao `argv` do console
aqui, então:

- as pastas de destino são criadas pelo script, em unicode;
- vindo de GRF (`--grf`), a busca é **tradução de encoding**: o caminho de
  destino já é o mesmo caminho de lá dentro, só que a tabela do GRF é CP949 e o
  sistema de arquivos é unicode;
- vindo de pasta (`--de`), o casamento é pelo **sufixo ASCII**
  (`_c_h_knight_cloak.spr`), que sobrevive a qualquer codificação de nome. O
  `--de` varre recursivamente, então pode apontar para uma extração inteira;
- o que é impresso troca o coreano por `<item>`, `<M>`, `<F>` — o console desta
  máquina não imprime coreano, e ninguém precisa do literal.

### A armadilha grande: **a pasta no disco NÃO tem o nome coreano**

Custou 5855 arquivos instalados em pastas que o cliente nunca abre, e o sintoma
não ajudava — `Resource File Loading fail` num arquivo que estava lá, íntegro e
byte a byte idêntico a um que o cliente lê sem reclamar.

O cliente é um app coreano que chama as APIs **ANSI** do Windows. Ele monta o
caminho em bytes CP949 e entrega para `CreateFileA`, que interpreta esses bytes
na **codepage ANSI do sistema** — cp1252 aqui, não CP949. O nome que ele procura
no disco é o mojibake:

```
o que se espera:  data\texture\유저인터페이스\item\...
o que o cliente procura: data\texture\À¯ÀúÀÎÅÍÆäÀÌ½º\item\...
```

Dentro do GRF isso não aparece: a tabela guarda os bytes crus e eles casam. **Só
no disco a diferença existe** — e é justamente onde o `DataFolderFirst` nos põe.

**A prova está na própria instalação:** a pasta que o ROenglishRE criou e que o
cliente lê todo dia chama-se `À¯ÀúÀÎÅÍÆäÀÌ½º`. Gravar em `유저인터페이스` cria
uma **segunda** pasta, de aparência correta, invisível para o cliente. Dava para
ver as duas lado a lado em `data\texture\` antes da correção.

A conversão mora num lugar só, `valida_visual.caminho_disco`, e a expressão
exata dela é `decode('mbcs')` — a codepage ANSI do sistema, que é o que
`CreateFileA` vai usar. Corolário: `os.path.exists` do Python 2 com caminho em
**bytes** faz essa mesma conversão sozinho, e por isso um teste de existência
escrito com bytes CP949 responde certo por acidente, enquanto um escrito com o
unicode coreano "correto" responde errado.

Os oito de um chapéu (`--id 420047`):

```
data\sprite\<item>\c_h_knight_cloak.spr           .act
data\texture\<ui>\item\c_h_knight_cloak.bmp
data\texture\<ui>\collection\c_h_knight_cloak.bmp
data\sprite\<acessorio>\<M>\<M>_C_H_Knight_Cloak.spr   .act
data\sprite\<acessorio>\<F>\<F>_C_H_Knight_Cloak.spr   .act
```

Conferir depois com `valida_visual.py --id <n>`.

**Armadilha ao ler tabela grande de bytecode:** no Lua 5.1 o operando `RK` só
endereça constante até o índice 255. Passando disso o compilador emite `LOADK`
num registrador e o `SETTABLE` passa a referenciar `R<n>` em vez da constante.
Quem lê só as linhas `SETTABLE ... ; B="NOME" C=<valor>` captura apenas as ~127
primeiras entradas e conclui, errado, que a tabela é minúscula. É preciso
acompanhar os `LOADK` e resolver os registradores — ver
`filtra_lub_por_skid.py:skids_do_cliente`.
