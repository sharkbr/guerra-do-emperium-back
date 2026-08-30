# Armadilhas: Script de NPC do rAthena

Comandos de script, variáveis e arrays, spawn, instância, unidades, sintaxe do parser.

**Este arquivo é um dos seis cadernos de armadilhas do projeto.** O índice de
todos eles — uma linha de gatilho por armadilha, com o caderno onde o caso
está contado por inteiro — está na §5 do `CLAUDE.md`. **Leia aqui a entrada
que o gatilho apontar**; ler o caderno inteiro não é para ser preciso.

As entradas abaixo produziram diagnóstico falso e custaram retrabalho. Cada
uma traz o sintoma, a causa medida (com arquivo e linha, quando existe) e a
saída — e a medição é o que separa esta lista de um palpite. **Armadilha
nova se escreve nas duas pontas:** o caso aqui, o gatilho na §5.

---

- **`setwall` com tamanho maior que 1 pode sair mais curto do que o pedido, e
  não avisa.** O `map_iwall_set` percorre as células uma a uma e **para na
  primeira que já esteja bloqueada** (`map.cpp:3503`), gravando
  `iwall->size = i` — a parede fica com o comprimento que deu, sem erro, sem
  log, e o `checkwall` depois responde que ela existe. Quem precisa das
  células exatas usa **tamanho 1 por célula**, que não tem o que truncar, e
  confere cada uma com `checkcell(..., CELL_CHKNOPASS)` antes de dar por
  fechado. Ver a escrivaninha em `npc/guerra/centro_da_ordem.txt`.

- **Comentário no fim de uma linha de spawn entra DENTRO do nome do evento.**
  O `npc_parsesrcfile` enche o `w4` *"to end of line"* (`src/map/npc.cpp`), e o
  `npc_parse_mob` lê o evento com `%77[^,]` — que só para na vírgula. Um
  `<TAB>// Amon Ra` depois do evento vira parte dele, e o `mob_parse_dataset`
  (`src/map/mob.cpp:446`) só tira a aspa quando ela é o **último** byte. Falha
  **calada**: o chefe nasce, anda, morre, e o evento nunca dispara — nada no log
  aponta para a linha. Quem documenta um spawn documenta **acima** dele, ou no
  cabeçalho do arquivo (ver `npc/guerra/corredor_fantasma.txt`).

- **Uma linha ruim mata o ARQUIVO INTEIRO, não a linha — inclusive linha de
  comentário.** O `npc_parsesrcfile` (`src/map/npc.cpp:5646`) imprime
  *"Unknown syntax in file '...', line 'N'. Stopping..."* e **para de ler o
  arquivo ali**. Tudo que vier abaixo simplesmente não existe, sem outro aviso.
  Achado em 2026-08-08: um `\n` dentro do texto de um gerador partiu uma linha
  `//=` do **cabeçalho** em duas, e a metade órfã (`pc\ do`) derrubou os dois
  NPCs que estavam 25 linhas mais abaixo. Duas consequências:
  1. **Um erro no cabeçalho é tão fatal quanto um erro no código.** Depois de
     gerar arquivo de NPC, conferir que **toda linha antes da primeira definição
     começa com `//`** ou está vazia.
  2. **O log não ajuda a achar.** Essa única linha de `[Error]` fica soterrada
     sob centenas de `[Warning]` inofensivos dos mercados. Procurar por
     `Unknown syntax`, não ler o fim do log.

- **Em spawn com área, `<xs>,<ys>` NÃO é o lado do retângulo.** O `mob_spawn`
  chama `map_search_freecell` com `xs-1` (`src/map/mob.cpp:1149`), que sorteia em
  `rnd_value(bx-rx, bx+rx)`. `mapa,120,120,70,70` é **120 ± 69**, não 120±35 nem
  um quadrado de 70. Ler como lado erra a área por quatro, e o erro não se
  denuncia — os monstros nascem, só que em lugar diferente do planejado.

- **Mapa pode ter pedaço andável solto, e `0,0` no spawn sorteia lá.** O
  `vis_h01` tem 16.104 células no mapa de verdade **mais 479 na linha y=239**,
  ruído do `.gat`. Monstro sorteado ali fica inalcançável. Antes de usar `0,0`,
  varrer os pedaços conectados do `.gat` — ou dar coordenada e área, como o
  `corredor_fantasma.txt` faz.

- **`rand(1)` não devolve 0: ele MATA o script.** O `buildin_rand`
  (`src/map/script.cpp:5604`) na forma de um argumento só faz `maximum -= 1` e
  então recusa `maximum < 1` com *"range is too small. No randomness
  possible"*, pondo `st->state = END`. Ou seja **`rand(n)` só é seguro com
  `n >= 2`** — e o caso perigoso não é a constante, é a **variável**: `rand(.@x)`
  onde `.@x` é um contador que encolhe (cartas que restam, itens que sobraram,
  jogadores vivos) passa por 1 no fim, sempre, e aí o script morre no meio com
  o diálogo aberto e o que já foi cobrado, cobrado. Nada no cliente denuncia; o
  log traz uma linha longe de onde o número nasceu. Achado em 2026-08-12 no
  blackjack do Cassino de Comodo, onde `rand(@bj_resta[valor])` valia 1 toda vez
  que saía a última carta daquele valor. A saída é uma linha:
  `if (.@x > 1) .@i = rand(.@x);` com `.@i` já em 0.

- **`getitem` com a mochila cheia LARGA O ITEM NO CHÃO.** O
  `buildin_getitem` (`src/map/script.cpp`) chama `pc_additem`, e no fracasso
  cai num `map_addflooritem` — então "vai direto para o inventário" não é
  garantia do script, é garantia do **item**. Quem impede a queda é o
  `pc_candrop`, que recusa item `NoDrop`; com ele o item se perde e o cliente
  avisa. Item sem `NoDrop` entregue por script aparece no chão da arena, ao
  alcance de qualquer um, e nada no log denuncia. Caso vivo: a Caveira Humana
  (30995), em `npc/guerra/honra_de_combate.txt`.

- **`mes` que começa com ESPAÇO não abre linha nova — cola na anterior.** O
  `clif_scriptmes` (`src/map/clif.cpp:2472`) manda a string **crua**, sem `\n`:
  quem decide onde quebrar é o cliente, e o critério dele é o primeiro
  caractere. Visível abre linha; espaço é continuação. Então indentar uma
  lista com `mes "  item…"` **concatena a lista inteira**, e o que se vê na
  tela é o resultado da largura da caixa, não do script. Medido em 2026-08-11
  na Máquina de Sombrios Totais: das quatro linhas de prêmio, três pareciam
  certas — tinham estourado a largura e quebrado sozinhas — e a quarta apareceu
  grudada no fim da terceira. **Três das quatro estavam erradas e pareciam
  certas**, e mexer em qualquer texto (nome de item mais curto, porcentagem com
  menos dígitos) reorganiza a janela sem erro nenhum. Para recuar, caractere
  visível (`- `, `. `), nunca espaço.

- **`||` e `&&` do script do rAthena NÃO fazem curto-circuito.** São o `C_LOR`
  e o `C_LAND`, operadores de **dois números** (`script.cpp:3839`) resolvidos
  pelo `op_2num` depois de os dois lados já estarem na pilha — não há salto
  como em C. Então a guarda mais comum de todas, `if (i == 0 || v[i-1] != x)`,
  avalia `v[-1]` na primeira volta, **sempre**. O mesmo vale para
  `if (getarraysize(.a) > 0 && .a[0] == 1)` e para qualquer
  `if (x != 0 && y/x > 2)`. Falha barulhenta no log (*"getelementofarray:
  index out of range (-1)"*) e **calada na tela**: o comando devolve falha, o
  `OnInit` MORRE ALI, e tudo que ele ainda ia montar fica vazio — um menu
  construído depois abre em branco, sem nenhuma linha de erro que aponte para
  o menu. Achado em 2026-08-12 no Guia de Prontera. A saída é `if` aninhado ou
  `if`/`else if`, nunca o operador.

- **O nome único de um NPC é o que vem DEPOIS do `::`, não a linha inteira.**
  Em `<Nome na tela>::<Nome único>` o `npc_parsename` (`src/map/npc.cpp:3674`)
  põe a primeira metade em `nd->name` — que só serve para desenhar — e a
  segunda em `nd->exname`, que é a chave do `npcname_db` e o que
  `disablenpc`/`enablenpc`/`donpcevent` aceitam. Ou seja o
  `Guide#01prontera::GuideProntera` se desliga por **`GuideProntera`**.
  Confunde porque a metade da esquerda **parece** o nome único (tem `#`, é o
  que se lê no arquivo) e porque num NPC **sem** `::` as duas são a mesma
  coisa — inclusive nos `duplicate`, que quase nunca têm `::`. Erra-se num e
  acerta-se nos outros quatro, e o resultado é NPC velho de pé empilhado no
  novo: os dois aparecem, o jogador clica no de cima, e qual é o de cima
  ninguém escolheu. O log traz *"Attempted to disablenpc a non-existing NPC"*.

- **`explode` NÃO limpa o array de destino.** Ele grava a partir do índice
  dado (`script.cpp:17305`) e para quando a string acaba — o que sobrou de uma
  chamada anterior mais longa continua lá. Ler o resultado por
  `getarraysize()` depois de uma linha curta devolve o tamanho da linha
  ANTERIOR, e nada denuncia. `deletearray <array>[0];` antes de cada
  `explode`, sempre.

- **`getarraysize()` de array de texto para no último elemento NÃO VAZIO.**
  Então tabela de colunas paralelas em que a última coluna termine em `""`
  encolhe, e a conferência "todas as colunas têm o mesmo tamanho" — que é o
  que a regra §4.11 pede — passa a mentir justamente quando deveria pegar o
  desalinhamento. Usar um marcador visível (`"-"`) no lugar de `""`, e numerar
  coluna de inteiro a partir de 1 e não de 0, pelo mesmo motivo.

- **Facing de NPC se calcula pela CÉLULA de destino, não pelo lado da tela.**
  Tabela do `enum directions` (`src/map/path.hpp:16`) medida em jogo com a
  câmera padrão: **4 (sul) desenha para baixo-direita, 2 (oeste) para
  baixo-esquerda, 0 (norte) para cima-esquerda, 6 (leste) para cima-direita.**
  A pergunta certa é "que direção me leva daqui até lá". O cabeçalho da
  `npc/guerra/maquina.txt` traz uma tabela em termos de "direita/esquerda" que
  vale **só para aquele sprite** — reusá-la virou a Máquina de Sombrios Gerais
  para o lado errado em 2026-08-12.
  **E há um caso em que o ponto cardeal pedido é a resposta errada: NPC de
  FALA.** Quando o pedido diz "virado para leste" e o NPC fica de frente para o
  jogador, ótimo; quando fica **de costas**, não houve erro de conversão — foi o
  `6` fazendo o que a tabela promete. Para quem conversa, o que importa é a
  direção **na tela**, e com a câmera padrão quem olha para o jogador que sobe o
  salão é **4** ou **2**, nunca 6 ou 0. Custou uma rodada nos três NPCs de fala
  da Sala Secreta da Ordem em 2026-08-13, todos pedidos em "leste" e todos
  entregues de costas. Ao receber ponto cardeal para NPC que dialoga,
  **perguntar para onde ele deve OLHAR na tela**, não só que célula encarar.

- **NPC com sprite de CLASSE DE JOGADOR nasce pedindo o penteado 0, e o 0 não
  existe.** Sprite de NPC normal (`view id` ≥ 44, do `npcidentity.lub`) traz a
  aparência pronta do `npc_viewdb`; id de **classe** (`JOB_MERCHANT` = 5 e
  irmãos) cai noutro caminho — o `npcdb_checkid` recusa, e o
  `status_set_viewdata` (`src/map/status.cpp`, `case BL_NPC`) monta a aparência
  à mão num `else if (pcdb_checkid(class_))`: `look[LOOK_BASE] = class_` e
  `look[LOOK_HAIR] = cap_value(0, MIN_HAIR_STYLE, MAX_HAIR_STYLE)`. Com o nosso
  `min_hair_style: 0` (`conf/battle/client.conf`) isso dá **penteado 0**, e os
  penteados deste cliente vão de **1 a 42** nos dois sexos — não há
  `0_<sexo>.spr`. O corpo da classe existe; a cabeça é que não. Remédio, no
  `OnInit`: `setunitdata(getnpcid(0), UNPC_HAIRSTYLE, 1)` (e `UNPC_SEX`, que
  também nasce zerado pelo `memset`) — as duas **gravam no `nd->vd` do próprio
  NPC** (`clif_changelook`, `case LOOK_HAIR`, faz `vd->look[type] = val`), então
  valem para quem logar depois e não são pacote solto. **Nenhum dos 26 mil
  `script` do rAthena usa id de classe** — a varredura é barata e a ausência
  total é o aviso. Caso vivo: a Tranqueiras, `prontera 151,131`, 2026-08-12.

- **`OnNPCKillEvent` NUNCA dispara para mob que tem evento próprio.** Em
  `mob.cpp:3592` os dois são ramos de um `else if`: se `md->npc_event[0]` está
  preenchido, roda o evento do mob e o global **não roda**. Como todo chefe de
  instância nasce com `instance_npcname(...)+"::OnMyMobDead"`, **nenhum deles
  dispara o evento global** — um contador de caçada feito assim compila, sobe,
  não erra no log e conta zero. Quem conta morte de verdade é o objetivo
  `HUNTING` de quest: o `quest_update_objective` roda antes, fora daquele `if`,
  e o `map_foreachinallrange` (`mob.cpp:3575`) ainda propaga para a **party
  inteira dentro de `AREA_SIZE`**. É o que as instâncias do próprio rAthena
  usam. Mesmo quando o global dispara, é para o `first_sd` — o primeiro do
  registro de dano, não o matador.

- **`disablenpc` NÃO desliga o NPC dentro da instância — a receita de §2 não
  vale para NPC de mapa de instância.** São dois campos diferentes e só um
  atravessa a clonagem: o `buildin_disablenpc` (`script.cpp:12388`) chama
  `npc_enable_target`, que mexe em `is_invisible` e `sc.option` e **nunca
  grava `nd->state`**; e é justamente `state`, e só ele, que o
  `npc_duplicate_sub` copia para a cópia (`npc.cpp:4655-4657`). Então
  `disablenpc "X"` num `OnInit` esconde o NPC do **mapa-molde**, onde ninguém
  entra, e **o clone de dentro da instância nasce ligado** — empilhado no
  substituto, com a regra velha de volta. Falha calada: os dois aparecem, o
  jogador clica no de cima, e qual é o de cima ninguém escolheu. Só o
  `script(DISABLED)` de tempo de parse propaga (`npc.cpp:3974`), e ele mora no
  arquivo do rAthena. **A saída é o `OnInstanceInit` do NPC substituto**, e ela
  é segura porque o `instance_addnpc` cria TODOS os clones antes de rodar
  qualquer `OnInstanceInit` — os dois laços estão um embaixo do outro em
  `instance.cpp:586-598`, com os comentários *"First add the NPCs"* e *"Now run
  their OnInstanceInit"*. Caso vivo: o seletor de dificuldade do Túmulo do
  Monarca, `npc/guerra/tumulo_do_monarca.txt`, 2026-08-12.

- **`getexp` NÃO passa pela taxa de EXP do servidor.** A `base_exp_rate` é
  aplicada uma vez só, ao EXP de **mob**, no carregamento do `mob_db`
  (`mob.cpp:5077`); o `getexp` de script só é multiplicado pelo
  `quest_exp_rate` (`conf/battle/exp.conf`), que está em **100**. Então
  `getexp 800000,800000` entrega 800.000 num servidor cujo monstro rende dez
  vezes mais — a recompensa de NPC vale **um décimo** do que o número sugere,
  em relação ao resto. Ler "somos 10x" e supor que o script acompanha erra a
  economia inteira, e nada denuncia.

- **Literal de `setarray` pode virar NOME DE VARIÁVEL, e aí traduzir quebra.**
  No `DevilTower.txt` os cinco `"DIR_NORTHWEST"`, `"DIR_NORTH"` etc. são
  concatenados: `'coord_seal_DIR_NORTHWEST` e `'round[DIR_NORTHWEST]`. Chegam
  ao catálogo de tradução por um `setarray` de texto, **parecem rótulo de
  direção** e não são — traduzir faz o script procurar variável que não
  existe. Falha calada: o selo mágico simplesmente não anda. O `RE_TECNICO`
  cobre `setd`/`getd`, não este caso. Regra prática: literal em MAIÚSCULA com
  `_` dentro de `setarray` é suspeito até prova em contrário.

- **`F_GetPlural` aplica regra de plural INGLESA à palavra que a gente
  escrever.** O `callfunc("F_InsertPlural", n, "Second")` vira "3 Seconds";
  traduzido para `"Segundo"` vira "3 Segundos", que está certo — mas por sorte
  de terminação. A função (`npc/other/Global_Functions.txt`) acrescenta `-es`
  em `-s/-x/-z/-ch/-sh`, troca `-f/-fe` por `-ves`, `-y` por `-ies`, e tem uma
  lista de exceção em `-o` (`potato|tomato|…`). Palavra portuguesa que caia num
  desses ramos sai errada na tela e **nada avisa**. Conferir a terminação antes
  de traduzir argumento de `F_InsertPlural`.

- **`killmonster` com o terceiro argumento tem o sentido INVERTIDO do que o
  nome sugere:** sem ele o rótulo dos mortos **não** dispara; `1` é que faz
  disparar (`doc/script_commands.txt`, `*killmonster`). Para limpeza silenciosa,
  omitir.

- **`delequip` + `getitem2` devolve o item SEM vínculo, SEM prazo e SEM grau de
  encanto — e nenhum dos três tem função de leitura por slot de equipamento.**
  Remontar um equipamento é a única saída quando se precisa mexer numa cova só
  (o `successremovecards` tira **todas** as cartas de uma vez, e tira a Essência
  de Morroc junto porque ela é `Type: Card`). Mas o que não for passado de volta
  se perde, e três campos não têm `getequip*` nenhum: `bound`, `expire_time` e
  `enchantgrade`. Quem os tem é o **`getinventorylist`**, nos arrays
  `@inventorylist_bound[]`, `@inventorylist_expire[]` e
  `@inventorylist_enchantgrade[]` — a linha do item vestido se acha pelo bit de
  posição (`@inventorylist_equip[] & EQP_*`), que é EQP e não EQI.
  Consequência que engana sozinha: separar carta de um item **vinculado** o
  devolve solto — item de conta virando mercadoria, sem erro nenhum. E item
  **alugado** volta eterno, porque `getitem4` não tem prazo. Os dois só se
  evitam lendo o `getinventorylist` antes. Caso vivo:
  `npc/guerra/separacao_de_cartas.txt`, 2026-08-18.

- **Zero em variável de `.` ou `.@` APAGA a entrada, então `setarray .@x[0],
  0,0,0,0,0;` deixa um array VAZIO.** O `set_reg_num` (`src/map/script.cpp`)
  tem dois ramos para esses dois prefixos: `value != 0` grava, e o `else` faz
  `i64db_remove` mais `script_array_update(..., true)`. Ou seja um array de
  zeros não existe — `getarraysize` devolve 0, e um comando que exija array
  de verdade pode recusar. No caso dos três arrays de opção aleatória que o
  `getitem4` exige isso é inofensivo e até desejável (array vazio = nenhuma
  opção, que é o que se quer ao remontar), mas contar com "o array tem 5
  posições" depois de um `setarray` de zeros é contar com o que não está lá.
  Vale também para `@` (o `pc_setreg` faz o mesmo), e é por isso que
  `@inventorylist_equip[]` de item não equipado simplesmente não existe.
  **E o caso que morde de verdade é a TABELA DE CONSTANTES, não o array de
  zeros escrito à mão.** `EQI_ACC_L` vale **0**; num `setarray .@slot[0],
  EQI_HEAD_TOP,…,EQI_ACC_L;` de dez colunas, o zero é o último, some, e
  `getarraysize` devolve **nove**. Quem usa isso para conferir se as colunas
  paralelas da §4.11 batem recebe um desalinhamento que não existe — foi assim
  que o Richard da separação de cartas recusou atender no primeiro teste em
  jogo, em 2026-08-18, com a própria guarda de integridade se autobloqueando.
  A saída é **sentinela `-1` no fim de toda coluna de inteiro**, e ela deixa a
  conferência mais forte: o último elemento nunca é zero, e como o `setarray`
  grava por posição, uma coluna com um valor a menos desloca a sentinela e o
  tamanho não bate. O tamanho de referência sai da coluna de **texto**, que não
  tem elemento vazio.

- **`mobcount` e `killmonster` com `"all"` não fazem nada, e não avisam.** São
  dois enganos do mesmo dia e da mesma família — o argumento é um **rótulo de
  evento**, não uma palavra mágica, e rótulo que não existe simplesmente não
  casa com nada. No `mobcount("<mapa>","all")` o resultado é **0**, então um
  teto de monstros escrito assim nunca dispara e o mapa entope em silêncio; o
  especial de "todos" ali é a **string vazia**, que conta os monstros *sem*
  rótulo — que é o caso de tudo que nasce por `monster`/`areamonster`. No
  `killmonster "<mapa>","all"` não morre ninguém, porque o buildin compara
  `strcmp(event,"All")` — **maiúsculo e exato** (`script.cpp:11486`). Para
  matar tudo, `killmonsterall "<mapa>"`, que não tem capitalização para errar.

- **`callsub` ABRE ESCOPO `.@` NOVO E VAZIO, igual ao `callfunc` — e ler as
  `.@` do chamador lá dentro devolve ZERO, calado.** As duas últimas linhas do
  `buildin_callsub` (`src/map/script.cpp:5508`) são as mesmas do
  `buildin_callfunc`:

  ```c
  st->stack->scope.vars   = i64db_alloc(DB_OPT_RELEASE_DATA);
  st->stack->scope.arrays = idb_alloc(DB_OPT_BASE);
  ```

  A única diferença entre os dois é que o `callsub` passa `.@` como
  **argumento por referência**, para o `getarg` — quem precisa de valor do
  chamador tem de recebê-lo assim, e **array não passa por `getarg`**, o que
  torna `callsub` errado por natureza para sub-rotina que mexa em array.

  **Até 2026-08-28 esta entrada afirmava o CONTRÁRIO** ("callsub não abre
  escopo; ele enxerga as `.@` de quem chamou; só o `callfunc` isola"), e o
  preço foi um item de jogador apagado: o `S_Remonta` do
  `npc/guerra/encantamento_da_ordem.txt` lia `.@part` (a posição do
  equipamento) e recebia **0**, que é `EQI_ACC_L` — o `delequip 0` tirou e
  destruiu o Anel de Jasper que estava no acessório esquerdo de quem testava,
  e o `getitem4 0` seguinte morreu com *"Nonexistant item 0 requested"*,
  deixando a janela de diálogo travada. **Os dois sintomas eram a mesma
  linha**, e nenhum deles apontava para o `callsub`.

  Duas coisas que sobram, e valem mais que o conserto:
  - **Zero é um valor plausível para quase tudo** — posição de equipamento, id
    de item, índice de tabela. Sub-rotina que devolva zero não parece
    quebrada, parece que "não achou".
  - **Comando que APAGA coisa do jogador (`delequip`, `delitem`,
    `successremovecards`) não roda sobre valor que não foi conferido na linha
    de cima.** A trava redundante imediatamente antes do `delequip` teria
    transformado isso num "o NPC recusou atender". É a mesma família da §4.11
    ("comentário não é trava"), um degrau acima: aqui quem mentia era o
    `CLAUDE.md`.

- **`movenpc` move o BONECO e deixa a ÁREA DE TOQUE para trás.** O
  `npc_movenpc` (`src/map/npc.cpp:5046`) faz `map_moveblock` e mais nada — não
  chama `npc_unsetcells` nem `npc_setcells`. E a área de toque **não mora no
  NPC, mora no MAPA**: o `npc_setcells` (`npc.cpp:4971`) marca `CELL_NPC`
  célula por célula em volta dele, uma vez, no carregamento. Resultado de mover
  um NPC com `<xs>,<ys>` por script: o sprite anda, o gatilho **fica onde
  estava** — dispara no lugar velho e não dispara no novo, sem erro e sem log.
  Para mover NPC com área de toque, a receita da §2 (`disablenpc` no original +
  duplicata nossa na coordenada nova, repetindo o `<xs>,<ys>`), que faz o
  `npc_setcells` rodar no lugar certo. Medido em 2026-08-26, ao tirar o
  Mensageiro Continental de cima da Máquina Dimensional.

- **`strnpcinfo(2)` lê o nome de EXIBIÇÃO, não o nome único — e há script do
  rAthena que guarda dado no sufixo `#`.** São campos diferentes: o `case 2` do
  `buildin_strnpcinfo` (`script.cpp:9276`) devolve o pedaço de `nd->name` depois
  do `#`, enquanto o nome único é o `nd->exname`, que é o `strnpcinfo(3)`. Isso
  importa ao duplicar NPC do rAthena, porque alguns **decidem o comportamento
  por ali**: o `Continental Messenger#01` faz `set .@area$,strnpcinfo(2)` e um
  `if (.@area$ == "01")` para saber que está em Prontera. Uma duplicata chamada
  `#01b` — o reflexo natural para não repetir nome — faria o NPC anunciar
  "01b" como se fosse o nome da cidade, calado. A saída é manter o sufixo
  original na parte visível e pendurar o nome único depois do `::`, que o
  `strnpcinfo(2)` não enxerga.

- **`getunitdata` NÃO é função: é comando que PREENCHE UM ARRAY — e usado como
  função devolve zero, calado na tela.** A forma certa é
  `getunitdata <GID>,<array>;`, e os índices do array são as próprias
  constantes: `.@dados[UMOB_HP]`, `.@dados[UMOB_MAXHP]`. Escrito como
  `.@hp = getunitdata(<GID>, UMOB_HP)` — que é o reflexo natural, porque o
  **`setunitdata` irmão tem três argumentos e parece autorizar a leitura
  simétrica** — o valor sai **sempre 0**.

  O que torna isso caro é onde o aviso aparece: *"buildin_getunitdata: Error in
  argument! Please give a variable to store values in"* sai **só na janela do
  map-server**, e o zero devolvido é um número plausível para quase toda
  pergunta que se faça a uma unidade — HP, nível, velocidade. Em 2026-08-26 isso
  fez a Anomalia Dimensional parecer quebrada de um jeito muito convincente: as
  Pedras Guardiãs recebiam cura na tela (o número verde subia, o efeito saía) e
  o painel do NPC lia **"0 de 15000"** nas quatro, o tempo todo. O diagnóstico
  natural — "a cura não está pegando no monstro" — apontava para o
  `SkillHeal`, para o elemento do mob, para o `damagetaken`: três lugares onde
  não havia defeito nenhum. **A cura sempre funcionou; só a leitura estava
  errada.**

  Duas lições que sobram: ao ler estado de unidade, **conferir a janela do
  map-server antes de acreditar no número** (o log em arquivo não recebe esses
  avisos, `console_msg_log` 3); e, quando um valor lido vier zero de forma
  suspeita, desconfiar **do leitor antes do fenômeno** — é a mesma família do
  "tabela com 1 entrada é sintoma de chave não resolvida".

- **`setunitdata UMOB_MAXHP` para BAIXAR o máximo CORROMPE o HP — é underflow
  `uint32` no rAthena, e o servidor cura em vez de reduzir.** O
  `status_set_maxhp` (`src/map/status.cpp:1343`) faz:

  ```c
  heal = maxhp - status->max_hp;   // os dois lados sao uint32
  ...
  if (heal > 0) status_heal(...); else status_zap(...);
  ```

  Reduzir (15.000 − 120.500) dá underflow: o resultado vira um número enorme e
  **positivo**, o `if (heal > 0)` acerta, e ele **cura**. Medido em 2026-08-26
  ao pôr as Pedras Guardiãs em 15.000: o HP foi para **2.147.604.147**, e
  nenhum `UMOB_HP` depois disso trazia de volta — ficava travado no HP original.
  Aumentar o máximo não tem o problema.

  **A receita são TRÊS chamadas, nesta ordem:** `UMOB_HP` para o valor
  desejado (ainda dentro do máximo velho) → `UMOB_MAXHP` para o novo máximo (o
  underflow ainda acontece, mas o `status_heal` que ele dispara é limitado ao
  máximo recém-gravado, então o HP só sobe até ele) → `UMOB_HP` de novo. Medido
  passo a passo; a sequência `MAXHP` e depois `HP`, que é a que o exemplo do
  `doc/script_commands.txt` sugere, **não funciona** quando o máximo diminui.

  E cuidado com o sintoma, que aponta para longe: um monstro que nasce com o HP
  cheio faz um evento de "encher a barra" terminar no mesmo segundo em que
  começa — o que parece lógica de conclusão errada, e não escrita de HP.

- **Comando de script que "existe no rAthena" pode não existir NESTE rAthena, e
  o erro do parser aponta para o lugar errado.** O vendor foi congelado numa
  revisão; comando que entrou depois, ou que só existe em fork, simplesmente
  não está na tabela de buildins — e o `parse_simpleexpr` não diz *"comando
  desconhecido"*, diz **`unmatched ')'`** na coluna do parêntese de abertura,
  porque tratou o nome como variável e tropeçou no `(` seguinte. A mensagem
  manda procurar erro de sintaxe numa linha que está sintaticamente perfeita.
  Medido em 2026-08-29 ao escrever a Glast Heim Sombria: **`has_instance`** e
  **`getnpcx()`/`getnpcy()`** não existem aqui (o primeiro se resolve pelo
  `IE_NOINSTANCE` do próprio `instance_enter`; o segundo é
  `getmapxy(.@m$,.@x,.@y,BL_NPC)` sem valor de busca, que devolve a posição do
  NPC que está rodando).
  **A conferência que decide é `grep "BUILDIN_DEF(<nome>" src/map/script.cpp`**,
  e ela é de graça. O `doc/script_commands.txt` do próprio vendor também serve,
  e é mais confiável que qualquer wiki — mas cuidado com o inverso: **constante
  de sprite não aparece pelo nome no `grep`**, porque o `export_constant_npc`
  corta o prefixo (`JT_WARPNPC` vira `WARPNPC` em tempo de execução). Procurar
  `\bWARPNPC\b` devolve zero sobre uma constante que existe.
