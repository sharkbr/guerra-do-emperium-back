# Ferramentas de inspeção do cliente

> **Referência por ferramenta — consultar pela seção, não ler inteiro.**
> Para o fluxo completo de uma tarefa (item novo, loja, tradução), ver
> `RECEITAS.md` na raiz, que diz em que ORDEM chamar estas ferramentas e por quê.

Escritas em 2026-07-30 para diagnosticar o erro `RecommendedQuestInfoLoad`.
Rodam em **Python 2.7** (`C:\Python27\python.exe`), que já está instalado nesta
máquina por causa do `get4.py` do NEMO.

A maioria é de inspeção do cliente, mas nem todas — `nomes_pt_item_db.py` e
`traduz_npcs.py` mexem no servidor, o `servidor.py` abaixo só cuida dele, e o
`monta_logue_e_ganhe.py` escreve nos dois lados de uma vez.

## `servidor.py` — sobe, para e confere os quatro servidores

```
python servidor.py status      # o que está no ar, e o que quebra se não estiver
python servidor.py subir       # sobe o que faltar, na ordem certa
python servidor.py parar       # derruba todos
python servidor.py reiniciar   # parar + subir
```

**São quatro servidores, não três.** Além de `login`, `char` e `map`, o rAthena
tem o `web-server.exe` na porta **8888**, e com `PACKETVER > 20200300` é ele
quem recebe o emblema de clã, por HTTP. Em 2026-08-04 o emblema não subia
justamente porque os `.bat` foram chamados um a um e esse ficou de fora — e a
falha é **completamente calada**: sem caixa de erro, sem linha no chat, sem nada
na janela do map-server.

Por isso o `status` não lista só portas, ele diz **o que o jogador vê** quando
cada peça está fora:

```
  SERVICO        PORTA  ESTADO   PID
  ----------------------------------------------------
  MariaDB        3306   no ar    9568
  login-server   6900   no ar    15864
  char-server    6121   no ar    15524
  web-server     8888   FORA
  map-server     5121   no ar    8032

  O que voce vai ver no jogo:
    web-server     -> emblema de cla nao sobe -- e a falha e CALADA
```

Sai com **código 1** se algo estiver fora, então dá para encadear em outro
script. `subir` é **idempotente**: pula quem já está no ar, e serve tanto para
subida do zero quanto para recuperar uma peça que caiu.

A ordem de subida é respeitada (o `char` precisa do `login`, o `map` precisa do
`char`) e cada porta é esperada antes de ir para a próxima — o `map-server` tem
prazo de 120s porque carrega todos os `db/`. Se o banco não responder na 3306,
nem tenta: nenhum servidor sobe sem ele.

Cada servidor abre a **própria janela de console**, de propósito: erro de script
de NPC só aparece na janela do `map-server`, não existe arquivo de log para ele.

Detalhe de implementação: a checagem é uma **conexão TCP de verdade**, não
leitura do `netstat`. O `netstat` desta máquina pode sair traduzido (`OUVINDO`
em vez de `LISTENING`) e quebraria o parse; conexão não depende de idioma. O
`netstat` é usado só para exibir o PID, e nunca para decidir.

## `monta_missoes_da_ordem.py` — põe as missões da Ordem na janela do cliente

```
python monta_missoes_da_ordem.py              # grava (faz backup antes)
python monta_missoes_da_ordem.py --verificar  # só relata, não grava
```

**Sem isto, pegar uma missão da Ordem derruba o cliente.** Não é "aparece sem
título": o `GetOngoingQuestInfoByID` (`questinfo_f.lub`, linha 4) faz
`QuestInfoList[id].Title` **sem guarda de nil**, e uma missão desconhecida sai
como *"attempt to index field '?' (a nil value)"* — uma caixa de erro por
missão e por atualização da janela, até a conexão cair. Foi assim que as sete
Missões A renderam mais de trinta modais em 2026-08-08. As outras funções do
mesmo arquivo (`Description`, `RewardItemList`, `CoolTimeQuest`) **têm** a
guarda; só a do título não tem.

Escreve os dois arquivos que definem o global `QuestInfoList`:
`System\OngoingQuestInfoList_True.lub` e `_Sakray.lub`, em **cp1252 com
CRLF**, como o resto deles.

**A ordem importa, e é a única armadilha de uso:**

```
python traduz_ptbr.py questinfo      # PRIMEIRO — ele reconstrói o arquivo
python monta_missoes_da_ordem.py     # DEPOIS — ele acrescenta as nossas
```

Aqueles `.lub` são **gerados** pelo `traduz_ptbr.py`, que parte do coreano de
2021 congelado no `.COREANO` ao lado. Rodar a tradução depois deste script
apaga as nossas entradas sem avisar — e o sintoma é o cliente voltar a cair.

**As ids vêm do `rathena/db/guerra/quest_db.yml`**, que é onde se diz quais
missões existem; o **texto em português** mora na tabela `TEXTO` do script.
Missão que exista no YAML e não tenha texto aqui **aborta a gravação** com a
lista do que falta — é de propósito: uma missão sem entrada no cliente é
exatamente o bug que este arquivo existe para impedir. As duas missões
reservadas (Torneio de Magia e Sonho Sombrio) estão comentadas no YAML, então
não entram.

É **idempotente**: antes de inserir, retira toda entrada da faixa
30000–30049 que já esteja no arquivo. Rodar duas vezes dá o mesmo tamanho.
Passa pelo `luac -p` do ROenglishRE antes de gravar, e faz backup.

Irmão do `monta_logue_e_ganhe.py` abaixo — existe pelo mesmo motivo (sistema
de UI com metade da configuração no cliente, `CLAUDE.md` §4.9) e se usa do
mesmo jeito. **O cliente lê esses arquivos só na inicialização.**

## `monta_logue_e_ganhe.py` — gera as duas metades do Logue e Ganhe

```
python monta_logue_e_ganhe.py              # grava os dois lados
python monta_logue_e_ganhe.py --verificar  # só relata, não grava
```

É a única ferramenta que escreve no **servidor e no cliente na mesma passada**,
e existe por um motivo específico: a tabela de prêmios do Logue e Ganhe mora nos
dois lugares, em formatos diferentes.

| lado | arquivo | papel |
|---|---|---|
| servidor | `rathena/db/guerra/attendance.yml` | **entrega** o prêmio, por RoDEX |
| cliente | `cliente\System\CheckAttendance.lub` | **desenha** os 20 quadrados |

O servidor não manda a lista para o cliente. O `ZC_UI_OPEN` leva **um número
só** — o contador do jogador —, e quem escolhe o ícone de cada quadrado é o
`.lub`. Divergir as duas tabelas **não dá erro em lugar nenhum**: a janela
promete um item e o correio entrega outro, e quem descobre é o jogador. Por isso
a receita (item, prêmio por dia, primeiro e último ciclo) fica no topo do script
e os dois arquivos são **saída** — editar qualquer um deles à mão é perder o
trabalho na próxima passada.

O que o script sabe e um editor de texto não saberia:

- **Vinte dias é teto do cliente.** Ele recusa `PREMIOS` de outro tamanho.
- **Um ciclo por mês civil**, com o último dia certo de cada mês (a regra
  bissexta está no código, sem `calendar`, para a saída não depender do locale).
  Mês civil não é enfeite: o contador (`#AttendanceCounter`) só zera quando
  começa um período novo.
- **A janela de datas do `.lub` é uma só** e cobre todos os ciclos — o cliente
  não tem como descrever mês a mês; quem separa é o servidor.
- `Config.EvendOnOff` fica sem valor **de propósito**. O erro de digitação é da
  Gravity, está no bytecode do kRO 2021-11-03 e no arquivo do ROenglishRE;
  "corrigir" para `EventOnOff` passaria a mandar um valor onde hoje vai `nil`.
- Faz **backup datado** do `.lub` (é o único dos dois que não está no git) e, no
  fim, prova que ele compila com o `Tools\luac.exe -p` do ROenglishRE.

Idempotente: se um arquivo já está igual, não toca nem faz backup.

Depois de rodar: `@reloadattendancedb` **e fechar e reabrir o cliente** — o
`.lub` só é lido na inicialização. Ver `RECEITAS.md` §10.

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

## `estado_item.py` — onde um item existe, e o que quebra se o ID for trocado

```
python estado_item.py --id 19455              # estado de um item
python estado_item.py --id 19024,19455        # de vários
python estado_item.py --loja Ocleiro          # de uma loja inteira
python estado_item.py --troca 19024:19455     # ANALISA a troca (a trava)
python estado_item.py --troca 19024:19455 --aplicar   # e executa o que dá
python estado_item.py --id 19455 --descricao  # a descrição do bRO, por extenso
```

**É o ponto de entrada da família de itens.** As outras ferramentas desta
seção cada uma cuida de uma tabela; esta responde, antes delas, *em quais
tabelas o item está* e *o que falta fazer*.

Nasceu em 2026-08-05, depois de uma troca de quatro itens na loja do Ocleiro
em que a **edição foi o barato e a descoberta foi o caro**. As duas perguntas
que custaram a tarde:

1. **"este ID existe onde?"** — a resposta mora em quatro tabelas, e faltar em
   cada uma quebra de um jeito diferente. Três das quatro falham **caladas**:

   | tabela | quem lê | falta = o jogador vê |
   |---|---|---|
   | `db/re/item_db_*.yml` | servidor | `@item` falha, a loja não abre |
   | `db/guerra/item_db.yml` | servidor | (o nosso, para o que o vendor não tem) |
   | `itemInfo.lua` do cliente | cliente | item **sem nome e sem ícone** |
   | os 8 arquivos de arte | cliente | caixa modal de erro ao equipar |

2. **"trocar este ID por aquele derruba alguma coisa?"** — derrubava três
   conjuntos, e conjunto que não fecha não dá erro.

### A trava de conjunto é o único pedaço que impede um bug

O resto do script descreve o mundo; `--troca` recusa.

Conjunto no rAthena é casado por **AegisName**, não por família. A versão com
cova de um chapéu é *outro item* — `Protect_Feathers_` não é
`Protect_Feathers`. Trocar o ID de uma loja pela versão com cova derruba todo
conjunto que citava a sem cova, e a perda é calada nos dois sentidos: sem erro
na subida, e o jogador não vê bônus faltando, vê um número menor.

O próprio rAthena tem receita para isso e, onde conhece as duas versões, a
aplica: lista a com cova como **alternativa dentro do mesmo `- Combos:`**, duas
listas `- Combo:` dividindo um `Script:` só. Foi assim que 19444, 19446 e
410125 atravessaram a troca de 2026-08-05 sem ninguém fazer nada. Só a Diadema
precisou de espelho à mão, porque o 19455 não existe no vendor — não há
alternativa para o rAthena listar.

**O casamento é feito no banco inteiro, não dentro da entrada**, e a leitura
intuitiva é a errada: o jeito do rAthena é pôr na mesma entrada, mas de um
arquivo de import não se acrescenta linha a uma entrada alheia — o nosso
espelho é entrada separada em `db/guerra/item_combos.yml`. Procurar só dentro
da entrada daria BLOQUEIO num conjunto perfeitamente coberto.

Sai com **código 1** quando há bloqueio, então dá para encadear.

### O que ele não faz

`--aplicar` só chama o que já existe e já é idempotente: `completa_iteminfo.py`
para a entrada de cliente e `nomes_pt_item_db.py` para o `Name` do servidor.
**Ele não cria entrada de `item_db`** — preencher bônus é leitura de descrição,
e isso é julgamento, não mecânica. Quando o item falta no servidor, a saída diz
isso e para. Trocar o ID na linha da loja e espelhar conjunto também continuam
sendo à mão, e a saída lembra disso.

### O que ele mudou nas vizinhas

Duas alterações em `valida_visual.le_item_db`, que virou o varredor de
`item_db` compartilhado:

- ganhou `slots`, `tipo` e `arquivo`, **aditivos** — quem já usava a função
  (`instala_visual.py`, `estende_accessoryid.py`, `varre_cosmeticos.py`) lê as
  chaves que sempre leu. `slots` nasce `0` e não `None` de propósito: o
  `item_db` **omite** `Slots:` quando é zero, e ausência ali quer dizer "sem
  cova", não "não sei";
- `nome` passou a vir **sem as aspas** do escalar YAML. O db do rAthena põe
  aspas em 631 nomes e deixa 28725 sem, então comparar o nome do servidor com o
  do cliente acusava diferença em todo item que só muda de aspa. O
  `varre_cartas.py` já fazia esse `strip` por conta própria.

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

**Em 2026-08-28 entrou a décima primeira, e ela é a primeira com ARTE PRÓPRIA
de verdade:** o **Pincel do Infinito (30992)**. Aqui o `arte_de` não servia, e o
motivo é o ponto do item — ele senta na mochila **ao lado** do Pincel de
Maquiagem e do de Grafite, e três pincéis idênticos é problema de leitura. A
arte saiu do `doura_arte.py` (seção própria abaixo), que recolore a do 6121 para
ouro e põe uma aura na ponta. Por isso o campo dele é `recurso` e não `arte_de`:
o nome do recurso é nosso e é ASCII, então não há byte CP949 a copiar de
ninguém. **É o primeiro uso do `recurso` para um recurso que não existia antes**
— os dois anteriores (19272 e 490029) o usavam para apontar para a arte que a
própria entrada já trazia.

A tabela tem **dez itens em 2026-08-27** — 30999 Maçã da Inocência, 30998 Moeda
Nova, 30997 e 30996 (as duas caixas da Máquina), 30995 Caveira Humana, que
copia a arte da Caveira comum (7420), e 30994 Rolinho de Arroz, o prêmio de
guerra, que copia a arte do Bolinho de Arroz (555). As três últimas não são
itens nossos: 19272 Chapéu do Éden, 490029 Ferramenta Mágica de Gelo e 18145
Arco Vigilante, os três casos de *"traduzir entrada alheia"* — ver as seções
abaixo.

**Em 2026-08-18 a tabela ganhou `covas` e `visual`, e a sétima entrada.** Os
dois campos são opcionais e valem zero quando faltam — as seis receitas antigas
não mudaram de comportamento. Eles existem porque o script gravava
`slotCount = 0` e `ClassNum = 0` **literais** desde que nasceu, e por seis itens
seguidos isso esteve certo: nenhum dos nossos tinha cova nem visual de cabeça.

A sétima é o **Chapéu do Éden (19272)**, que tem os dois — e é também a
primeira entrada da tabela que **não é de um item nosso**. Ele existe inteiro no
rAthena; o que faltava era o nome, porque o `itemInfo.lua` deste cliente o traz
em **coreano**. O `completa_iteminfo.py` não resolve (o bRO também o tem em
coreano, e o script se recusa a reescrever bloco alheio, de propósito), e a
receita da Lacma — criar o ID traduzido — derrubaria três conjuntos. Sobrou
este script, que é o único que **substitui bloco existente**. O texto veio do
19315 do bRO, que é o mesmo item com outro número.

Com `slotCount` zerado o nome sairia sem o `[1]` e a janela de encaixe de carta
não enxergaria a cova; com `ClassNum` zerado a peça perderia o id de visual. Os
três seriam falhas **caladas**, e o `--verificar` não as pega: ele compara com o
que o próprio gerador produziria. A lição geral subiu para o `CLAUDE.md` §5.

**Os dois campos têm de bater com o `item_db`** — `covas` com o `Slots:` e
`visual` com o `View:`. O servidor manda o número, o cliente desenha o que
estiver escrito aqui, e divergir não dá erro nenhum.

**Mas o `visual` só bate com o `View:` em equipamento de CABEÇA.** Para **arma**
o `ClassNum` do `itemInfo.lua` é a numeração de arma do cliente, que vive só
daquele lado: o `Vigilante_Bow` (18145) tem `ClassNum = 73` e **nenhum `View:`**
no `item_db` — e nenhum arco do vendor tem. Zerá-lo (o padrão do campo) trocaria
o desenho da arma na mão do personagem, calado. Os vizinhos dão a numeração:
18109 e 1748 também são 73, o 18143 e o 18163 são 11. Ao escrever receita de
arma, **copiar o `ClassNum` que a entrada já traz** e não procurar `View:` no
`item_db`.

Em 2026-08-12 o `arte_de` do **30996** mudou de 22668 (a caixa de 20 do bRO,
que é a caixa genérica de consumível) para **12710, a própria Poção de Guyak** —
a pedido: a caixa passa a ter a cara do que tem dentro. É um exemplo do que o
campo serve: trocar o desenho de um item nosso é uma linha da tabela e uma
rodada do script, sem tocar em arte nenhuma.

### O `un` que faltava no regex, e dois dias de gorro errado (2026-08-20)

A tabela ganhou uma **nona entrada** e o script ganhou um **campo novo**, os dois
pelo mesmo achado.

A nona é a **Ferramenta Mágica de Gelo (490029)**, e é o segundo caso do tipo
"Chapéu do Éden": item que existe inteiro no vendor e cuja entrada de cliente
está na língua errada — aqui, **inglês** (veio do ROenglishRE, `Server = "jRO"`).
O `completa_iteminfo.py` não serve, porque **o bRO não tem este ID**; o texto foi
traduzido à mão a partir do `Script:` do vendor, o que de passagem mostrou que a
descrição inglesa estava incompleta (faltava a linha da Maestria Arcana).

Ao fazer isso apareceu o bug. A função `recurso()` procurava

```python
re.search(r'identifiedResourceName = "([^"]*)"', bloco)
```

e **`unidentifiedResourceName` termina em `identifiedResourceName`**. A linha do
*unidentified* vem primeiro no bloco, então o regex casava com ela e devolvia o
recurso do item **não identificado**.

**A falha é calada e seletiva.** Quando as duas linhas trazem o mesmo recurso — o
caso de todo `Etc` e todo consumível, ou seja das **seis primeiras receitas** —
o resultado é idêntico e nada aparece. Ela só morde **equipamento**, que é onde o
kRO põe um gorro/veste genérica de "item não identificado" no primeiro campo.

Foi o que aconteceu com o **Chapéu do Éden (19272)**, a sétima receita, de
2026-08-18 a 2026-08-20: ele ficou com `캡`, o gorro genérico, no ícone de
inventário, na imagem de *collection* e no sprite de chão.

**E o `valida_visual.py` dava "8 de 8 ok"** sobre isso: quatro dos oito arquivos
estavam certos (a cabeça vestida vem do `accessoryid`/`View`, não deste campo) e
os outros quatro apontavam para uma arte que **existe** — só que é a de outro
item. Validador que confere *presença* não pega troca de arte por arte.

O conserto foi `(?<!un)` na âncora. E veio com um segundo, de desenho:

**`recurso` — o nome do recurso por extenso, no lugar de `arte_de`.** Só ASCII
(nome coreano continua sendo caso de `arte_de`, que copia byte a byte). Ele
existe para o caso *"traduzir entrada alheia sem mexer na arte"*, em que
`arte_de: <o próprio id>` parece a resposta óbvia e é uma armadilha: **o script
se lê a si mesmo**, então basta uma rodada ruim para o valor errado virar a fonte
da rodada seguinte, e não há mais de onde recuperar o certo. A receita é
versionada; o cliente não. As duas entradas que apontavam para si mesmas (19272 e
490029) passaram a usá-lo.

A regra geral subiu para o `CLAUDE.md` §5.

### O recurso coreano que não cabe no campo, e o irmão que o compartilha (2026-08-27)

A tabela ganhou a **décima entrada**, o **Arco Vigilante (18145)** — terceiro
caso do tipo "Chapéu do Éden", e o primeiro em que as duas metades da entrada
estão em **línguas diferentes**: nome em coreano (`자경단 보우`) e descrição em
inglês, do ROenglishRE. O bRO tem o ID, mas também em coreano e **sem
descrição**, então o `completa_iteminfo.py` não tinha o que copiar.

O que ele acrescentou de método foi o **terceiro caminho da arte**. Os dois
conhecidos não serviam:

| caminho | por que não serviu aqui |
|---|---|
| `recurso: u'...'` | é ASCII, e o recurso deste é coreano |
| `arte_de: 18145` | auto-referência — a armadilha da seção acima |

A saída foi `arte_de: **18163**`: outro item do vendor que usa o **mesmo**
`identifiedResourceName`, conferido byte a byte no `itemInfo.lua` desta máquina
(e são os dois únicos que o usam). Copiar do irmão é copiar o mesmo desenho
**sem ler o bloco que se vai sobrescrever**. Quando o recurso for coreano,
procurar quem mais o usa é o primeiro passo — e se ninguém usar, aí sim o campo
`recurso` precisa aprender a receber bytes.

**A descrição inglesa foi conferida contra o `Script:` do vendor antes de virar
tradução**, e é o que autoriza usá-la como fonte: *"for each 20 base DEX, +5%
bow damage"* é `5*(readparam(bDex)/20)`, o *"+10% additional"* do +7 é o
`.@bonus += 10`, e o *"+50% Double Strafing"* do +9 é
`bonus2 bSkillAtk,"AC_DOUBLE",50`. **Nada sobrou dos dois lados.** No 490029, em
2026-08-20, tinha sobrado — faltava a linha da Maestria Arcana —, e por isso lá
a fonte foi o `Script:` e não o texto.

**A linha `Classes:` não sai da entrada inglesa.** Ela dizia só *"Shadow
Chaser"*, mais apertado do que o `item_db` permite (`Jobs: Rogue` +
`Classes: All_Third`/`Fourth`). O 18109 (Catapulta) tem exatamente a mesma
combinação e **tem descrição no bRO**: *"Classes: Renegados e evoluções"*. Item
irmão com descrição em português é a fonte certa para essa linha.

### A corrente de 31 itens em coreano, e a receita que é montada (2026-08-28)

A tabela saltou de 12 para **43 entradas**, e as 31 novas entraram de uma vez
porque eram uma **corrente**, não uma lista: a Caixa de Primeiros Socorros que
todo personagem novo recebe (o **23484**, do `start_items` em
`conf/char_athena.conf:124`) entrega cinco itens, e um deles é a caixa
seguinte — de cinco em cinco níveis, até o 95. O fecho transitivo tem 35
itens, e 31 estavam em coreano.

É o quarto caso do tipo *"traduzir entrada alheia"*, depois do 19272, do
490029 e do 18145, e o primeiro em que a quantidade mudou a forma da receita.
Três coisas ficam dele:

**1. A lista de conteúdo é MONTADA a partir do `item_db`, não escrita ao lado
dele.** Cada caixa promete por extenso o que entrega; são 19 listas, e
escrevê-las à mão seria criar 19 chances de a §4.11 do `CLAUDE.md` acontecer —
menu e tabela indexados pelo mesmo número saindo de fontes diferentes, com a
divergência calada. A receita traz só `(id, nível, [(quantidade, id)])`,
transcrito do `Script:`, mais um de-para de nomes; o texto sai daí num laço.
Por isso a `class Erro` subiu para o topo do arquivo: a receita é montada em
tempo de carga do módulo e pode levantar erro antes de qualquer função rodar.

**2. O doador de arte é sempre o IRMÃO, e a varredura é o primeiro passo.**
Os nove `resourceName` envolvidos são coreanos, então `recurso` (ASCII) não
servia; e `arte_de` apontando para o próprio item é a auto-referência que a
seção anterior documenta — com 31 itens de uma vez, uma rodada ruim apagaria a
fonte de todos. A varredura *"quem mais usa este recurso?"* respondeu por
todos: `응급처치상자` → 7641, `파란포션` → 505, `수리용키트` → 6434, e assim
por diante. **Nenhum dos nove doadores está na receita**, o que é a condição
para a fonte não virar o resultado da rodada anterior.

**3. O número da descrição sai do `item_db`, mesmo quando a entrada inglesa
discorda.** O inglês do 11518 dizia peso 1 e o `Weight: 50` do vendor diz 5.
Quem manda o número para a janela é o servidor.

O texto veio do bRO onde havia de onde vir: sete destes itens são a variante
"não à venda" de um item comum que o bRO tem em português **com os mesmos
números**, conferidos campo a campo. Nas duas poções de velocidade de ataque a
lista de `Jobs:` foi comparada conjunto a conjunto com a do irmão antes de a
linha `Classes:` ser copiada — traduzir nome de classe à mão é onde aquela
linha erraria calada.

Medido: 31 blocos trocados e só eles, 0 recursos alterados, 0 U+FFFD,
`luac -p` compila, +3.153 bytes.

## `completa_iteminfo.py` — importa entradas do bRO para o `itemInfo.lua`

```
python completa_iteminfo.py              # aplica (faz backup antes)
python completa_iteminfo.py --verificar  # só relata, não grava
python completa_iteminfo.py --listar     # mostra o que o bRO tem
python completa_iteminfo.py --id 450222  # um item só (ou lista, com vírgula)
python completa_iteminfo.py --descricoes # reescreve a descrição das NOSSAS
python completa_iteminfo.py --id 450222 --descricoes --sem-acento   # ASCII puro
```

**Desde 2026-08-03 ele grava COM acento, em cp1252** — o `--com-acento`, que era
a sonda, virou o padrão e deu lugar ao `--sem-acento`. Ver a seção do
`traduz_ptbr.py`, logo abaixo, para o porquê. As duas bandeiras `--sem-acento`
(aqui e lá) têm de andar juntas: metade do `itemInfo.lua` com acento e metade
sem é o pior dos dois.

Vizinho de prateleira do `instala_item.py`, com a divisão clara: **aquele
*inventa* a entrada de um item nosso a partir de uma receita escrita à mão; este
*copia* a entrada de um item que já existe no bRO.**

O problema que ele resolve apareceu ao montar o Mercado Contemporâneo
(`npc/guerra/mercado_contemporaneo.txt`): 25 dos itens pedidos não tinham
entrada nenhuma no `itemInfo.lua`. O arquivo vem do ROenglishRE, que traduz o
que o kRO/iRO tem — item que exista no `item_db` do servidor mas não ali aparece
**sem nome e sem ícone**.

E a cura já estava nesta máquina, no mesmo padrão que se repetiu a sessão
inteira. A instalação do Ragnarok Brazil traz

```
C:\Program Files (x86)\Gravity Interactive, Inc\Ragnarok Brazil\System\iteminfo_new.lub
```

com **18845 itens em português**, bem mais nova que a nossa. É a mesma
instalação que já era fonte de arte do `instala_visual.py`.

**Esse arquivo é bytecode Lua 5.1** (header `\x1bLuaQ`), não texto — por isso o
script carrega um mini-desassemblador, primo do `luadis.py`, e cai na mesma
armadilha do operando `RK` que aquele documenta: um parser que só leia a forma
"constante" para nas ~127 primeiras entradas e devolve um número plausível e
errado. O destino, o `itemInfo.lua` do ROenglishRE, é texto puro. Não confundir
os dois.

**Duas conversões de codificação, e errar qualquer uma corrompe:**

| campo | do bRO | para o nosso | por quê |
|---|---|---|---|
| nome exibido | UTF-8 | ASCII sem acento | texto de jogo aqui vai sem acento |
| `resourceName` | UTF-8 | **CP949** | é nome de arquivo dentro do GRF |

O `resourceName` é o que mais engana: `Fafnir_Helm` atravessa igual e dá a
impressão de que não há conversão nenhuma, mas a maioria dos itens antigos tem
nome coreano, e gravar o UTF-8 cru faria o cliente procurar um arquivo que não
existe. Item cujo recurso não couber em CP949 é **pulado com aviso**, nunca
gravado pela metade.

### A descrição também vem — e foi a maior surpresa

A primeira versão deste script **não** trazia a descrição, com a justificativa de
que desmontar as tabelas aninhadas do bytecode não pagaria o esforço. Estava
errado por uma ordem de grandeza. A descrição do bRO traz, por extenso:

```
Armadura usada por guerreiros primitivos que gritavam Requiescat in Pace...
^0000ffVelocidade de ataque +10%.^000000
^0000ffDano fisico e magico contra todos os tamanhos +40%.^000000
Refino +5 ou mais:
^0000ffAumenta a velocidade de movimento.^000000
Tipo: ^777777Armadura^000000
DEF: ^777777150^000000 DEFM: ^77777715^000000
Peso: ^777777100^000000
Nivel necessario: ^77777790^000000
```

Ou seja: **cada bônus e cada número do item**, que é exatamente o que faltava
para preencher os 18 placeholders de `db/guerra/item_db.yml`. O esforço de
desmontar a tabela aninhada se pagou no mesmo dia.

O truque do bytecode: `identifiedDescriptionName = { "a", "b" }` compila para
NEWTABLE, LOADK em registradores consecutivos e **SETLIST no fim** — quando o
campo é atribuído, a lista ainda está vazia. Por isso o leitor guarda a
*referência* da lista viva e lê o conteúdo depois, em vez de copiar na hora.

O texto entra **em português, como está** — não é traduzido nem reescrito. A
última linha de cada descrição é a marca `Entrada importada da tabela do bRO`,
que também é o que autoriza o `--descricoes` a reescrever um bloco: sem ela, o
bloco veio do ROenglishRE e não se toca.

### `--com-acento` é uma sonda, não uma opção de estilo

Por padrão o acento é removido, e a razão é **encoding, não idioma**: o
`itemInfo.lua` é ANSI e os `resourceName` dele são bytes CP949. Em CP949 o
intervalo `0x80-0xFF` é byte-líder de hangul, então um `á` gravado ali não vira
só um caractere torto — ele engole o byte seguinte.

`--com-acento` grava em cp1252, a codepage ANSI desta máquina. Existe para ser a
experiência de uma linha que responde **se este cliente desenha byte acentuado**
— pergunta que trava a fase PT-BR inteira (ver `PENDENCIAS.md`, "Acentuação no
diálogo"). Rodar num item só, olhar no jogo, decidir.

**A ordem em relação ao `valida_visual.py` importa, e não é a intuitiva.** O
validador lê o `identifiedResourceName` do `itemInfo.lua`; sem entrada ele nem
consegue avaliar o item, e responde `<id> nao esta no itemInfo.lua`. Então é
**este script primeiro, o validador depois** — e aí sim, se faltar arte, o
`instala_visual.py`.

Aplicado em 2026-08-01: 25 entradas, +11404 bytes, todas inseridas na posição
numérica certa. O efeito medido nos 7 chapéus que estavam cegos: **3 passaram a
validar limpo** (400006, 19445, 420110) e 4 se revelaram sem arte de verdade —
`View` que nem existe no `accessoryid.lub` deste cliente, o caso que o
`instala_visual.py` não cura. Ou seja, o script não só resolveu nome: **trocou
"não sei" por diagnóstico** em todos os sete.

Idempotente: item que já tenha entrada não é tocado — nem para conferir se é
igual, porque a entrada existente pode ser a do ROenglishRE, em inglês, e
trocá-la por uma nossa sem descrição seria piorar.

## `ajusta_covas_do_cliente.py` — o `[1]` no nome igual ao `Slots:` do servidor

```
python ajusta_covas_do_cliente.py             # aplica (faz backup antes)
python ajusta_covas_do_cliente.py --conferir  # só relata; sai 1 se faltar
python ajusta_covas_do_cliente.py --id 1328   # só estes (lista com vírgula)
```

Cova de item é mais um caso de **metade da configuração no cliente**
(`CLAUDE.md` §4.9), e a divisão não é a que se imagina:

- quem decide se a carta **entra** é o servidor — a janela de encaixe é montada
  em `clif_use_card` a partir do `slots` do `item_db`, então `Slots: 1` no `db/`
  já basta para o jogador encaixar;
- quem desenha o **`[1]` no nome da arma** é o `slotCount` do `itemInfo.lua`, do
  lado do cliente, e ele não pergunta nada ao servidor.

Mexer só no `db/` deixa um item que **aceita carta e não parece aceitar** — o
jogador não tenta, e nada dá erro. Mexer só no cliente é pior: promete uma cova
que o servidor recusa.

**A fonte da verdade aqui é o SERVIDOR, não o bRO**, e é de propósito: o nosso
`item_db` pode discordar do bRO por decisão nossa (a seção de OVERRIDES do
`db/guerra/item_db.yml` existe para isso), e o que o jogador precisa é que a
tela diga o que o servidor faz. Para ver os três lados de uma vez —
servidor, cliente e bRO — é o `estado_item.py --id <n>`.

**Vizinho de prateleira do `completa_iteminfo.py`, e a diferença importa:**
aquele *importa* a entrada inteira de um item que o cliente não tem, e por
desenho não toca entrada que já exista. Este mexe num **campo** de entrada que
já existe, e não olha para o bRO.

**A lista `COVAS` é escrita à mão, e isso foi medido.** A alternativa — varrer
as vitrines e alinhar tudo — daria 16 divergências entre os 3396 itens de loja
(2026-09-03), e em **13 delas quem promete a cova é o cliente** (entrada de
2021) enquanto o servidor não a dá. Alinhar esses 13 tiraria da tela uma cova
que o jogador já vê, e isso é decisão do dono, não consequência de script — os
16 estão anotados no `PENDENCIAS.md`. **Ao mudar `Slots:` de um item,
acrescentar o ID à lista e rodar.**

Estreou em 2026-09-03 com as 15 Armas Brutais do Senhor das Armas: 15 trocas de
um byte cada (`slotCount = 0` → `= 1`), arquivo do mesmo tamanho, e o
`luac.exe -p` do ROenglishRE compilando o resultado. Tudo `rb`/`wb`, byte a
byte, sem decodificar nada — a mesma regra do `instala_item.py`, e a razão é a
mesma: os `resourceName` daquele arquivo são bytes CP949 coreanos.

Como o `itemInfo.lua` mora em `C:\GuerraDoEmperium\cliente\`, **rodar este
script não leva a mudança a ninguém**: o cliente lê o arquivo só na
inicialização (fechar e reabrir), e o jogador só a recebe por patch
(`CLAUDE.md` §4.18).

## `nomes_pt_item_db.py` — o `Name` do servidor igual ao nome que o cliente desenha

```
python nomes_pt_item_db.py --relatar    # só mede
python nomes_pt_item_db.py              # grava, deixando .INGLES ao lado
python nomes_pt_item_db.py --reverter
```

O problema só aparece **dentro de diálogo de NPC**, e por isso demorou a ser
visto. O nome que o jogador lê na bolsa vem do `itemInfo.lua` do **cliente**,
que já está em português. Mas `getitemname()` e `getequipname()`, que os
scripts usam para montar a fala, leem o `Name` do `item_db` do **servidor**,
que está em inglês.

O Mestre do Refino dizia `+5 Weapon Refine Ticket` para o item que a bolsa do
jogador chama de `Pergaminho de Arma +5`. Mesmo item, dois nomes — e o único
que o jogador consegue procurar é o da bolsa.

**A fonte é o `itemInfo.lua` do nosso cliente, não o `iteminfo_new.lub` do
bRO.** Os dois quase sempre concordam (o nosso foi montado importando o dele),
mas quando discordarem quem está certo é o do cliente, porque é ele que está na
tela. Mesma regra do `npcidentity.lub` para view id e do `accessoryid.lub` para
visual: **manda o arquivo que o cliente lê.**

Por isso o objetivo não é "traduzir o item_db", é **sincronizar**. Onde o
cliente está em português o servidor fica em português; onde o cliente ficou em
inglês o servidor fica com o inglês *dele*. Consistência primeiro — o português
vem junto porque o cliente já está em português. 16412 itens.

### A primeira versão zerava o preço de venda de 7126 itens, em silêncio

Ela gerava um `db/guerra/item_db_nomes.yml` com entradas de `Id` + `Name`,
encadeado por import — que é o que a CONVENÇÃO DE CUSTOMIZAÇÃO pede, e que o
rAthena aceita de bom grado: `AegisName` e `Name` só são exigidos quando o item
é **novo** (`itemdb.cpp:57`). Parecia a solução limpa.

A armadilha está em `itemdb.cpp:239`:

```cpp
hasPriceValue[item->nameid] = { has_buy, has_sell };
```

Essa linha roda a **cada** parse do mesmo `Id`, e guarda só se *aquele bloco*
declarou `Buy`/`Sell`. Um bloco com `Id` + `Name` grava `{false, false}` por
cima do `{true, false}` que o `db/re/` tinha registrado. Depois, no
`loadingFinished` (`itemdb.cpp:1185`):

```cpp
if (!has_buy && has_sell)       value_buy  = value_sell * 2;
else if (has_buy && !has_sell)  value_sell = value_buy / 2;
```

Nenhum dos dois roda, e a derivação se perde. A Poção Vermelha declara só
`Buy: 10`; com o override o `value_sell` dela ia para **0** em vez de 5. Poção
Branca, 600 → 0. Poção Azul, 2500 → 0. **Todo drop que valia dinheiro passava a
não valer nada** — 7126 itens.

E foi silencioso: dos 7126, **um** imprimiu aviso na subida, e por outro motivo
(o `Gray_Shard`, que caiu na trava de exploit de zeny). Os outros 7125 não
disseram nada. Foi esse aviso solitário — ausente no log da rodada anterior —
que puxou o fio.

**A lição, que vale para qualquer override parcial de YAML do rAthena:** um
bloco parcial não é só "os campos que eu escrevi". Ele é um parse inteiro, e
campo ausente pode significar "não declarado" para lógica que roda **depois**,
no `loadingFinished`. Antes de sobrepor parcialmente, procurar o que o
`loadingFinished` daquele db faz com a ausência.

### Por isso ele reescreve o arquivo do rAthena

Trocar o `Name` no lugar não tem esse problema, porque **não acrescenta parse
nenhum**: o bloco continua sendo um só, com os mesmos campos de preço. Só a
string muda.

O conflito com a CONVENÇÃO é o mesmo que a frente de tradução já resolveu, e a
saída é a mesma: **fonte separada de resultado**. A fonte é o `itemInfo.lua` do
cliente mais esta ferramenta; o arquivo do rAthena é o resultado, com `.INGLES`
ao lado. `--reverter` desfaz, e `git checkout` também.

E, pela lição que custou 595 pares do `servico.cat`: **a leitura do nome antigo
sai do `.INGLES` quando ele existe.** Sem isso, rodar duas vezes compararia
contra o próprio resultado.

### O que fica de fora, e por quê

| motivo | quantos | o que acontece |
|---|---|---|
| nome ainda em **coreano** no cliente | 4587 | fica o inglês do rAthena, que é melhor que mojibake |
| item que o `item_db` não tem | 4220 | não há linha para trocar |
| nome já igual | 4094 | não vale gravação |
| acima de 50 caracteres (`ITEM_NAME_LENGTH`) | 40 | o rAthena cortaria; todos estão em inglês no cliente também |
| itens nossos (`db/guerra/item_db.yml`) | 1 | já nascem em português, com nome escolhido por nós |

Os 4587 coreanos são **um buraco do cliente, não deste script**: o jogador vê
coreano na bolsa deles também. `Claymore` (1190) é um exemplo — o bRO nunca os
traduziu.

### Travas

Estrutural, na mesma linha da do `traduz_npcs.py`: recusa gravar se o arquivo
mudar de número de linhas, de número de linhas `- Id:` ou de número de linhas
`Name:`. Conferido depois de gravar que **toda** linha alterada nos três
arquivos é uma linha `Name:` — nenhuma outra.

O nome sai sempre **entre aspas**: nome de item tem `+`, `[`, `]`, `:` e às
vezes espaço na ponta, e cada um muda o sentido de um escalar solto. O próprio
db do rAthena já põe aspas em 631 nomes pelo mesmo motivo. Como isso faria toda
linha "mudar de aspa" parecer diferente, a comparação de "já está igual" é
feita nos **valores**, não nas linhas.

Dois riscos que foram conferidos e não se confirmaram: nome duplicado não dá
erro (o `nameToItemDataMap` só sobrescreve, `itemdb.cpp:104-131` — o que muda é
que `@item <nome>` passa a achar pelo nome em português); e nenhum script do
`npc/` compara `getitemname()` com texto — nos 623 usos, as únicas comparações
são contra `"null"` e `""`, que é o que a função devolve para id inexistente.

## `traduz_ptbr.py` — põe o jogo em português, trazendo o texto do bRO

```
python traduz_ptbr.py tudo --verificar     # relata, não grava um byte
python traduz_ptbr.py tudo                 # aplica
python traduz_ptbr.py itens skills         # só essas partes
python traduz_ptbr.py tudo --sem-acento    # a saída de emergência
```

Catorze partes, catorze fontes diferentes dentro da instalação do Ragnarok
Brazil.
Nenhum texto é traduzido por nós — tudo é importado, cumprindo o ACORDO de
2026-08-02 (`PENDENCIAS.md`).

| parte | o que aparece traduzido | fonte no bRO |
|---|---|---|
| `msgstrid` | rótulo de janela e de botão | `msgstring_br.lub` (bytecode) |
| `msgtable` | mensagem de sistema e de erro | `data\msgstringtable.txt` |
| `itens` | nome e descrição de item | `System\iteminfo_new.lub` |
| `skills` | nome e descrição de habilidade | `skillinfolist.lua`, `skilldescript.lua` |
| `quests` | o **fallback** do texto de quest | `data\questid2display.txt` |
| `questinfo` | a janela de missões | `System\OngoingQuestInfoList_True.lub` |
| `questreco` | a aba RECOMENDADAS | `System\RecommendedQuestInfoList_True.lub` |
| `conquistas` | o modal de conquista | `System\achievement_list.lub` |
| `mapas` | nome do mapa no minimapa | `System\mapInfo.lub` |
| `mapinfo` | o letreiro ao entrar no mapa | `System\mapInfo.lub` |
| `cartas` | o prefixo que a carta põe no nome | `data\cardprefixnametable.txt` |
| `monstros` | o nome que flutua sobre o monstro | `navi_mob_br.lub` |
| `encantamentos` | o efeito do encantamento na janela do item | `addrandomoptionnametable.lub` |
| `efeitos` | o balão do ícone de status (buff e debuff) | `stateicon\stateiconinfo.lub` |

Toda parte é **idempotente** e faz backup antes de gravar.

### A regra que governa o arquivo inteiro: mesclar, nunca trocar

O destino é sempre o arquivo que o cliente **já usa** — o do ROenglishRE —, e o
bRO só preenche o texto, por chave. O reflexo de copiar o arquivo do bRO por
cima estaria errado, e o motivo é contraintuitivo: **o ROenglishRE é mais novo
que o bRO.** Trocar arquivo por arquivo apagaria o conteúdo que o bRO nunca
recebeu — 5234 quests ficariam em branco em vez de em inglês.

### `questinfo` e `questreco` — e por que `quests` não bastava

A parte `quests` traduz o `data\questid2display.txt`, e **não é ele que a janela
de missões lê.** Quem desenha título, descrição e resumo é o global
`QuestInfoList`, do `System\OngoingQuestInfoList_Sakray.lub`; o `.txt` só é
consultado quando o ID não está na tabela. A prova, de 2026-08-07: a quest 5153
estava em inglês no `.txt` e aparecia em coreano na tela.

Nestas duas a **estrutura vem do arquivo coreano de 2021**, e não do
ROenglishRE — mesma razão do `parte_abas`. Metade dos campos não é texto e sim
referência (`NpcSpr`, `NpcNavi`, `BgName`, `IconName`, `RewardItemList`), e a
versão do ROenglishRE é de 2026: sprite que este exe não conhece derruba a
janela. Como a primeira rodada troca o bytecode por texto puro, o coreano é
congelado em `<alvo>.COREANO` ao lado e é sempre dele que se parte.

**A trava que importa é o `luac -p`** (`ROenglishRE\Tools\luac.exe`), o Lua 5.1
de verdade. As travas por linha passaram todas e o arquivo não compilava: 37
descrições do bRO vêm como `título\n\t\tcorpo`, e string Lua não aceita quebra
de linha crua — a quebra deixa duas linhas com contagem ímpar de aspas, e o
`split` por `\r\n` não as separa. Todo `.lub` de texto que gerarmos passa pelo
`luac` antes de ser gravado.

A única troca de arquivo é `conquistas`, e ela se justifica: o
`achievement_list.lub` daqui é o coreano do instalador de 2021, então não há
inglês a preservar, e ele é **código, não tabela de texto** (cada conquista
carrega a função que monta o progresso). O do bRO tem 349 das nossas 361; as 12
que faltam passam de coreano para vazio.

### `encantamentos` — a única parte cujas CHAVES saem do nosso GRF

As duas linhas abaixo da descrição de uma arma ilusional — o efeito da opção
aleatória — vinham em **coreano**, e não por engano de tradução: o
`addrandomoptionnametable.lub` não existe solto em `cliente\data`, então o
cliente lia o do `data.grf`, que é o original da Gravity. Nunca houve arquivo
para vencê-lo.

O que torna esta parte diferente das outras doze é de onde vem a **chave**. Nas
outras, o destino é o arquivo do ROenglishRE e o bRO só preenche o texto; aqui
o destino não existia, e a chave não é um número — é `EnumVAR.<X>[1]`,
resolvida em tempo de execução contra o `enumvar.lub` **deste exe**. Chave que
ele não conheça vira `nil`, e `nil[1]` é erro de Lua que derruba a tabela
inteira: a janela voltaria a não mostrar encantamento nenhum. Por isso as
chaves saem do **nosso GRF** (Gravity, 2021-11-03), que compilou contra esse
mesmo `enumvar`, e não do bRO nem do ROenglishRE — que é de 2025 e conhece
opção que este cliente não tem.

O texto vem, em ordem: **bRO** onde ele tem (239 de 252), **ROenglishRE** no
resto (13). Nada fica em coreano. Os 13 são as siglas de 4ª classe — POW, SPL,
STA, WIS, CON, CRT, P.ATK, S.MATK, RES, MRES, H.PLUS, C.RATE — que são iguais
nos dois idiomas, porque o bRO daquela época ainda não tinha 4ª classe.

**Isto é cliente, e cliente não vai pelo deploy** (`CLAUDE.md` §4.18): depois
de gerar, fechar e reabrir o cliente para ver, e mandar por patch para chegar
ao jogador.

Uma armadilha do leitor de bytecode ficou registrada no `CLAUDE.md` §5: a chave
desta tabela é um símbolo **indexado por número**, e um leitor que só saiba
tratar símbolo indexado por string devolve `None` para todas — a tabela de 252
entradas colapsa numa só, sem erro nenhum, e o número que ele imprime é 1.

### `efeitos` — o balão do ícone de status, e o `.lua` do bRO que mente

Os ícones da direita da tela — o que avisa que a Agilidade está aumentada, que
o veneno corre, quanto tempo falta — mostram um balão ao passar o mouse, e esse
balão estava **inteiro em coreano**. É o mesmo caso do `encantamentos`: o
`stateiconinfo.lub` não existe solto em `cliente\data`, então o cliente lia o do
`data.grf`, que é o original da Gravity. E é dos poucos textos de tela que o
jogador vê o tempo todo sem abrir janela nenhuma.

As chaves saem do **nosso GRF** pelo motivo de sempre — `EFST_IDs.<X>` é
resolvido em tempo de execução contra o `efstids.lub` deste exe, e o arquivo do
ROenglishRE traz 120 efeitos que só existem em cliente mais novo, cada um deles
uma chave `nil` capaz de derrubar a tabela inteira. São **720** efeitos; o texto
vem do bRO em 515, do ROenglishRE em 202, e 3 ficam em coreano.

**A entrada é trocada inteira, e não linha a linha.** O `posTimeLimitStr` é o
índice da linha do relógio dentro do `descript` — só faz sentido ao lado do
descript que veio junto, e os dois discordam de verdade: no `EFST_QUEST_BUFF1`
o coreano diz 3 e o bRO diz 2. Os 202 blocos ingleses entram **verbatim**: são
texto já válido, e não há o que reescrever.

**A armadilha é a fonte, e ela é convidativa.** O bRO entrega os dois lado a
lado — `stateiconinfo.lua`, texto puro e legível, e `stateiconinfo.lub`,
bytecode — e o `.lua` está **velho**: 340 efeitos contra 530 do `.lub`, 193 a
menos. Escolher o legível custaria mais de um terço das traduções, sem erro
nenhum. Ver `CLAUDE.md` §5.

**Isto já foi tentado uma vez, do jeito errado.** Em 2026-07-30 o arquivo do
ROenglishRE foi copiado inteiro para essa pasta e o cliente morreu em
`[string "buf"]:6801: table index is nil` — a linha 6801 é
`StateIconList[EFST_IDs.EFST_VR_BOOK002] = {`, uma das 120 chaves que este exe
não conhece. O arquivo foi tirado dali e os ícones voltaram ao coreano, e é essa
dívida que esta parte paga. O episódio deixou uma prova de graça: o cliente
**leu** aquele arquivo solto, então o `DataFolderFirst` alcança a pasta
`stateicon\` — não é uma pasta a provar, como foi a `effecttool\`.

**Isto é cliente, e cliente não vai pelo deploy** (`CLAUDE.md` §4.18): depois de
gerar, fechar e reabrir o cliente para ver, e mandar por patch para chegar ao
jogador.

### O `msgstringtable.txt` é o único sem chave, e por isso o único com risco

Todos os outros arquivos têm chave — ID de item, `SKID.X`, ID de quest, nome de
`.rsw`, `MSI_*`. Este não: **o cliente pede a linha pelo número.** As duas
tabelas divergem (4023 contra 4216) e não é só no fim.

O alinhamento é por **âncora**: linhas cuja assinatura sobrevive à tradução
(`%s`, `^RRGGBB`, número, sigla em maiúscula, comando com barra) são casadas em
ordem; entre duas âncoras, se a distância bater dos dois lados, a corrida
inteira entra. Dá 651 âncoras e **73,1% das linhas**. O resto fica em inglês de
propósito — **linha não mapeada é melhor que linha trocada**.

Duas travas fecham os buracos que sobravam: corrida maior que 120 linhas é
recusada, e linha vazia só casa com linha vazia.

**É também a única parte que não pode ler o próprio destino.** O alinhamento é
por conteúdo, e a primeira rodada muda o conteúdo — a segunda alinharia
português contra português e sairia diferente da primeira. Por isso o inglês do
ROenglishRE é congelado em `data\msgstringtable.txt.INGLES` na primeira
gravação, e é sempre dele que se parte. **Apagar esse arquivo com o destino já
traduzido é o único jeito de estragar esta parte** — se acontecer, recuperar de
um `.BACKUP-*` ou do clone do ROenglishRE, onde ele é byte a byte idêntico.

### Encoding: dois no mesmo arquivo, de propósito

O bRO entrega **UTF-8** no `iteminfo_new.lub` e **cp1252** no GRF. O destino é
sempre cp1252, que é a codepage ANSI desta máquina; `decodifica()` detecta a
origem tentando UTF-8 primeiro — a ordem não é simétrica e inverter aceitaria o
UTF-8 cru, produzindo "AÃ§Ã£o" calado.

**No `itemInfo.lua` convivem cp1252 e CP949.** O texto de tela é cp1252; o
`identifiedResourceName` continua em **CP949 coreano**, porque é nome de arquivo
dentro do GRF. Reescrevê-lo com o valor do bRO faria o cliente procurar arquivo
que não existe e o item perderia o ícone.

Para o cliente **desenhar** esses bytes é preciso o `ajusta_charset_fonte.py`
(logo abaixo). Sem ele o `0xE7` vira byte-líder de sílaba coreana em vez de
`ç`, e o acento come a letra seguinte.

`--sem-acento` reverte a fase inteira sem tocar em código — mas aí o
`ajusta_charset_fonte.py --reverter` tem de andar junto.

## `ajusta_tamanho_fonte.py` — o tamanho e o peso da fonte do jogo

```
python ajusta_tamanho_fonte.py --verificar     # so relata
python ajusta_tamanho_fonte.py                 # aplica o estado aprovado
python ajusta_tamanho_fonte.py --mapa          # imprime a tabela de alturas
python ajusta_tamanho_fonte.py --tabela        # LE o cliente NO AR: o que ele pediu
python ajusta_tamanho_fonte.py --bonus 1       # cada letra um pixel maior
python ajusta_tamanho_fonte.py --teto 12       # afrouxa o achatamento
python ajusta_tamanho_fonte.py --livre 15      # daqui para cima o pedido passa intacto
python ajusta_tamanho_fonte.py --altura 48=42  # so este pedido, esta altura
python ajusta_tamanho_fonte.py --negrito 48    # estes pedidos saem em negrito
python ajusta_tamanho_fonte.py --face Gulim    # Gulim, Arial, Tahoma, Verdana
python ajusta_tamanho_fonte.py --fixo 20       # uma altura so, para diagnostico
python ajusta_tamanho_fonte.py --reverter
```

A altura de cada tamanho pedido sai de uma **tabela de 64 bytes gravada no
exe** — o stub le, nao calcula. A tabela e montada nesta ordem:

```
pedido <  --livre   ->  altura = min(pedido, --teto) + --bonus
pedido >= --livre   ->  altura = pedido + --bonus      (intacto)
--altura P=A        ->  sobrepoe o pedido P com a altura A
--negrito P         ->  o pedido P sai com peso 700 em vez de 400
```

Os padroes ja sao os valores aprovados no jogo: face **Arial**, **`--bonus 0`**,
**`--teto 11`**, **`--livre 15`**, **`--altura 48=42`**, **`--negrito 48`**, sem
suavizacao. Rodar sem argumento reproduz esse estado.

**`--bonus 0` nao e o mesmo que `--reverter`.** A face e nossa, nao a do
cliente, e duas faces na mesma altura em pixels nao desenham do mesmo tamanho —
entao `+0` ja e mudanca de tamanho. Foi assim que o ponto certo apareceu: nao
subindo o bonus, mas **zerando** ele. Negativo tambem vale.

**Nao existe opcao de tamanho de fonte neste cliente** — nem no Setup.exe, nem
no menu, nem no `OptionInfo.lua` (a lista inteira de chaves que ele grava esta
em `data/luafiles514/lua files/optioninfo/optioninfo.lub`, e nao ha nenhuma de
fonte). O `/font` da lista de comandos e outra coisa: troca a fonte do **chat**
por uma das `.eot` de `System/Font`.

**Resolucao tambem nao resolve, e piora.** A interface e de pixel fixo: subir a
resolucao deixa tudo menor. Medido a 1900x1080 — o nome do mapa na selecao de
personagem ficou ilegivel.

### O ponto de desvio, e por que e esse

```
0x004C4938  call 0x004C3660    ; pega o HFONT
0x004C4940  call [SelectObject]
0x004C494D  call [GetTextExtentPoint32W]   <- MEDE

0x004C4A6E  call 0x004C3660    ; a MESMA funcao
0x004C4A79  call [SelectObject]
0x004C4A89  call [TextOutW]                <- DESENHA
```

`0x004C3660` e o distribuidor de fontes do cliente, e **medicao e desenho tiram
a fonte dele**. Trocar a fonte so no desenho daria texto grande medido como
pequeno — cortado e sobreposto. Trocando aqui, a quebra de linha acompanha.

E thiscall (`mov esi,ecx` no prologo), cinco argumentos de `[ebp+8]` a
`[ebp+18]`, logo `ret 14h`. Devolve HFONT em eax. O **segundo** argumento e o
tamanho pedido — medido, comparando a mesma caixa de dialogo com `--fixo` e
com `--bonus`.

A fonte nova sai de `CreateFontA`, que estava importada com **zero** chamadas:
livre, sem risco de atropelar uso existente. Charset 0 (ANSI), o mesmo que o
`ajusta_charset_fonte.py` forcou e o que faz o acento cp1252 aparecer. Altura
negativa e altura de caractere; positiva seria altura de celula. A do cliente
e 13.

### O que ele NAO pega

Titulo de janela e botao saem do outro caminho de texto (`TextOutA`, em
`0x004D83BA`) e ficam do tamanho original. Medido: com o desvio ligado, "Do you
agree?" cresce e "message"/"OK"/"cancel" nao.

### Que tamanhos este cliente pede — medido, nao suposto

Com `--tabela`, andando por Prontera em 2026-08-10. **Sao oito, e so oito:**

| pedido | quem |
|---|---|
| 11 | o texto miudo: chat, placas de NPC, nome de personagem |
| 12, 13, 14 | a janela de informacoes basicas — HP/SP, Base Lv., peso e zeny |
| 16, 17, 18 | titulos de janela e o subtitulo do mapa ("A Capital de Rune-Midgard") |
| 48 | **o nome do mapa** — "Prontera", e nada mais no jogo inteiro |

Essa lista e o que torna a calibragem cirurgica: 48 e exclusivo do nome do mapa,
entao mexer nele nao toca em mais nada. Sem a medicao, seria chute.

### O achatamento, e por que virou faixa

Algumas linhas pedem corpo maior que o resto — na janela de informacoes
basicas, HP, SP, Base Lv., Job Lv. e a linha de peso e zeny. **Essa hierarquia
e do proprio cliente e ja existia antes de qualquer patch**, conferido contra
captura do estado original. So que a nossa face desenha maior na mesma altura
pedida, e a diferenca, que era discreta, ficou gritante.

De 2026-08-09 a 2026-08-10 isso foi um **teto plano** de 11, e a calibragem
degrau a degrau parecia fechada:

| teto | o que aconteceu |
|---|---|
| 14 | **nada** — prova que aquelas linhas pedem 14 ou menos |
| 12 | a janela encolheu e o resto do jogo ficou igual |
| 11 | parecia o ponto |

O `14` nao ter feito efeito e o dado mais util da tabela: matou a hipotese de
que aquelas linhas pediam um corpo muito maior.

**Mas o teto plano estava errado, e a tabela acima nao denunciava.** Ele nao
limitava exageros — achatava os oito corpos do cliente **num so**. O jogo
inteiro saia na mesma altura, sem hierarquia nenhuma: o nome do mapa do tamanho
do chat. Cada texto isolado parecia plausivel, e por isso demorou. Quem
denunciou foi o cache, que tinha **uma unica entrada preenchida**, a de indice
11 — se nada abaixo de 11 e pedido, tudo estava batendo no teto.

A correcao e o `--livre`: as duas pontas nao cabem num numero so, porque a
janela de informacoes basicas pede ate 14 e precisa ser achatada, enquanto o
nome do mapa pede 48 e precisa passar. Abaixo de `--livre` vale o `--teto`;
dali para cima o pedido passa intacto. O corte em 15 e o menor que segura a
janela sem tocar no resto.

Abaixo de 11 o teto passa a ficar **abaixo** do que a maioria dos textos pede,
e deixa de ser limite para virar reducao geral. O sintoma e a descricao de item
e o inventario encolherem junto.

### `--tabela` — ler o cliente vivo

O cache do stub e indexado pelo **tamanho pedido cru**, entao as entradas
nao-zeradas dizem exatamente quais tamanhos aquele cliente pediu. O `--tabela`
le isso do processo no ar (`ReadProcessMemory`) e imprime.

**E o unico jeito honesto de calibrar.** Sem ele, escolher onde cortar e chute,
e chute aqui custa um fechar-e-reabrir por rodada. Foi ele que respondeu numa
rodada o que a tabela de tetos acima nao respondeu em duas sessoes.

Duas ressalvas: so aparece o que ja foi desenhado — para ver o nome do mapa,
entrar num mapa antes —, e um cliente patcheado com a versao de ate 2026-08-09
indexava pelo tamanho **ja achatado**, entao a leitura dele nao vale nada.

### O que fica de fora, e nao da para consertar por aqui

"Abernus" e "Rune Knight", na mesma janela, continuam do tamanho antigo: saem
do `TextOutA`, que este desvio nao toca. Se um dia incomodar, o alvo esta
identificado em `0x004D83BA`.

### Calibrar — a interface e de caixa fixa

`--bonus` soma sobre o tamanho pedido e preserva a proporcao entre titulo,
corpo e rodape; e por isso o padrao. `--fixo` da a mesma altura para tudo e
achata essas diferencas — serve para provar que o desvio pegou, nao para uso.

Com `--fixo 20` o painel de selecao cortou "Interior de Prontera" em
"Interior d" e os valores do inventario se sobrepuseram. Subir de 4 em 4 e
olhar.

O cache por tamanho (64 entradas em `.xdiff`) **nao e enfeite**: sem ele cada
pedido criaria um HFONT novo e o processo vazaria handles ate cair.

### Onde cada peca mora no exe — e a metade da secao que nao existe em disco

A `.xdiff` tem `VirtualSize` de 0x1000 e **`SizeOfRawData` de 0x400**. Isso
parte a secao em duas metades de naturezas diferentes, e confundi-las custa uma
tarde:

```
0x013B5000 .. 0x013B5400   vem do ARQUIVO — stub e tabela de alturas moram aqui,
                           porque dado nosso so existe se for gravado
0x013B5400 .. 0x013B6000   NAO vem do arquivo — o carregador zera. Serve de
                           rascunho, e so. Gravar valor aqui no .exe nao chega
                           na memoria: o byte fica no fim do arquivo, fora de
                           qualquer secao mapeada

0x013B5320  64 bytes   altura + negrito por tamanho pedido   (arquivo)
0x013B5390  112 bytes  o stub                                (arquivo)
0x013B5400  64 dwords  o cache de HFONT                      (rascunho)
```

O cache funciona por sorte estrutural: zero e justamente o estado inicial certo
para ele. **Um mapa de alturas ali nao funcionaria** — seria lido como zeros.

Os 64 bytes do mapa sao um vao entre dois stubs do NEMO (um acaba em
`0x013B531A`, o outro comeca em `0x013B5360`). Antes de ocupar, foi conferido
que nenhuma constante do exe aponta para la e que **nenhum `e8`/`e9` do `.text`
aterrissa naquela faixa**.

**O negrito viaja no bit 7 do byte de altura**, nao numa segunda tabela: depois
do mapa vem stub do NEMO, e o maior vao de zeros que sobra na metade util da
secao tem 40 bytes. Custa 5 instrucoes e nenhum espaco novo; em troca, a altura
vai so ate 127 (o maior pedido do cliente e 48).

O stub tem 101 bytes dos 112 que cabem. Para caber, o indice fica em `ebx` por
cima da chamada em vez de reler `[esp+8]` e relimitar depois — `ebx` e
salvo-pelo-chamado no Win32, entao a `CreateFontA` devolve ele intacto.

### A versao anterior nao funcionava — e dizia que sim

Ate 2026-08-09 esta ferramenta somava na altura do `LOGFONTA` nos 8
`CreateFontIndirectA` do exe. **Nao tinha efeito nenhum, em nenhum valor**, e o
`--verificar` respondia *"8 ja desviadas"* porque procurava o formato do
proprio stub — aplicado, confirmado, inocuo. Tres A/B independentes fecharam o
caso, inclusive um stub que forcava sublinhado e nao apareceu em lugar nenhum.

A licao, que vale para qualquer patch de exe: **antes de subir o numero, provar
que o patch chega a tela**, com uma marca que nao dependa do efeito procurado.
O relato inteiro esta na secao "Tamanho da fonte" do `HISTORICO.md`.

O exe fica travado enquanto o cliente roda, e o cliente segura o proprio exe
(renomear tambem nao resolve, ao contrario do `Setup.exe`). Fechar e o unico
caminho — e o que ja esta aberto segue na copia em memoria, entao **fechar e
reabrir**.

## `ajusta_charset_fonte.py` — faz o cliente desenhar Latin-1

```
python ajusta_charset_fonte.py --verificar   # só relata
python ajusta_charset_fonte.py               # aplica (faz backup)
python ajusta_charset_fonte.py --reverter    # volta ao HANGUL
python ajusta_charset_fonte.py <outro.exe>   # alvo alternativo
```

**Um byte.** O cliente tem a tabela de charset por idioma em `.data`
(VA `0x00F392D0`), lida num único lugar dentro do `DrawDC::SetFont`:

```asm
85 ff                  test edi, edi
75 0a                  jnz  +10
a1 d0 92 f3 00         mov  eax, [tabela]          ; índice 0
83 fa 14               cmp  edx, 14h
7d 07                  jge  +7
8b 04 95 d0 92 f3 00   mov  eax, [edx*4 + tabela]  ; índice = langtype
```

A entrada 0 era `0x81` (HANGUL) e passa a `0x00` (ANSI). Pega os dois ramos do
`if` e independe de quem alimenta o `EDX`, que é o que torna a correção
robusta: não foi preciso descobrir qual variável é o langtype.

A tabela é achada por **assinatura de conteúdo** (`SHIFTJIS, GB2312, BIG5,
THAI` nas entradas 2 a 5), não por endereço fixo — e ancorada na entrada 2, não
na 0. A primeira versão ancorava na 0, que é justamente a que o script troca:
aplicava certo e o `--verificar` seguinte respondia "não achei a tabela".

### Por que não é um patch do WARP

Três tentativas antes desta, todas registradas no `PENDENCIAS.md`:

| patch | o que aconteceu |
|---|---|
| `AlwaysAscii` | não tem nada a ver — anula um `jnz` em `CSession::IsOnlyEnglish`, que é chat |
| `CustomFontCharset` = ANSI | aplicou (17 bytes) e não mudou nada: o cliente também usa `CreateFontIndirectA` |
| `FixFontsCharset` | é o certo em conceito e **não existe para este exe**: só tem `case` para `Exe.Version` 6/9/10/11, e o nosso é VC140 |

O terceiro é o que mais engana: o WARP **descarta o patch calado** e regrava o
binário idêntico, só com data nova. **Conferir o SHA do exe depois de cada
rodada de WARP** — data de modificação não prova nada.

E o exe fica travado enquanto o cliente roda. Nesse caso o script morre com
`Permission denied`; renomear também não funciona (o cliente segura o próprio
exe, ao contrário do `Setup.exe`). Fechar o cliente é o único caminho.

### A aspa escapada — o erro que derrubou o cliente em 2026-08-03

Custou uma reabertura do cliente e seis diálogos de erro, então fica registrado
inteiro. O `msgstring_kr_s.lub` tem quatro valores com **aspa escapada**:

```lua
MSI_PARTY_BOOKING_MAKE = "/organize \"Party Name\": Creates a party.",
```

O regex do valor era `[^"\r\n]*`, que para na aspa **escapada**. A substituição
trocou meio valor e deixou o resto da linha solto:

```lua
MSI_PARTY_BOOKING_MAKE = "/organize 'nome do grupo': Cria um novo Grupo."Party Name\": Creates a party.",
```

O arquivo perdeu a sintaxe, `MsgStrID` virou nil, e o cliente abriu numa
cascata de diálogos — `hotkey.lua:135`, `party_booking_function.lua:3`,
`OptionInfo\CmdInfo:49` — **nenhum deles citando o arquivo culpado**. Só o
primeiro diálogo dizia a verdade: `[string "buf"]:433: '}' expected near
'Party'`. Ler o primeiro erro, não o mais frequente.

Duas correções, e a segunda é a que importa:

1. Todo regex de valor passou a usar `VALOR = (?:[^"\\\r\n]|\\.)*`, e o
   `aspas()` desfaz `\"` antes de trocar as aspas, para não sobrar barra solta.
2. **`confere_linhas()` recusa a gravação** se qualquer linha que atribui um
   campo de texto deixar de casar com a forma `campo = "valor",`.

A trava #2 existe porque a linha estragada é **lexicamente válida** — as aspas
fecham, as chaves batem. Um verificador de balanceamento foi escrito, testado
contra o arquivo quebrado e **passou**. O que pega é exigir a forma da linha
inteira. Há teste de controle: a trava recusa o arquivo quebrado e aceita tanto
o inglês original (com escape) quanto o português correto.

`confere_blocos()` complementa, comparando a lista de chaves de primeiro nível
antes e depois — pega o caso em que uma entrada engole a seguinte.

### Duas armadilhas de regex que custariam caro

- `unidentifiedDisplayName` **contém** `identifiedDisplayName`. Sem o
  `(?<![A-Za-z])`, o nome do item identificado ia parar no campo do
  não-identificado e o outro ficava em inglês. Vale igual para a descrição.
- Do `skillinfolist` **só o `SkillName` é trocado**. O resto do bloco é
  estrutura, e a nossa é a que combina com o cliente de 2021: os arquivos daqui
  já foram recortados por SKID para não citar habilidade de 4ª classe, que
  derruba a janela de habilidades inteira. Importar o bloco inteiro desfaria o
  recorte. Do `skilldescript`, aí sim, o bloco todo — ali tudo é texto.

### `ptbr.py` — a base que ele usa

Não faz nada sozinho. Guarda os caminhos das fontes, a conversão de codificação
e duas peças reaproveitáveis:

- **`tabelas(dados)`** — bytecode Lua 5.1 → as tabelas montadas, não só as
  strings soltas. Interpreta `NEWTABLE`/`SETTABLE`/`SETLIST`/`GETGLOBAL` e
  guarda valor de tempo de execução como `Sym`, que é o que torna legível um
  `[SKID.NV_BASIC] = {...}`: no bytecode aquela chave não é constante nenhuma, é
  `GETGLOBAL SKID` seguido de `GETTABLE "NV_BASIC"`.
- **`blocos_lua(texto)`** — quebra `TABELA = { [chave] = {...} }` em blocos, por
  contagem de chaves fora de string. Aceita as três formas de chave
  (`[SKID.X]`, `[123]`, `["prontera.rsw"]`) e salta para o próximo caractere que
  importa em vez de percorrer byte a byte — no `itemInfo.lua`, que tem 22 MB, a
  diferença é 2,4 s contra minutos.

## `traduz_npcs.py` — traduz o diálogo dos NPCs do rAthena, por catálogo

```
python traduz_npcs.py --extrair kafra        # gera/atualiza o catálogo
python traduz_npcs.py --preencher            # aplica o glossário nos catálogos
python traduz_npcs.py --preencher --forcar   # e SOBRESCREVE o que divergir
python traduz_npcs.py --aplicar kafra        # escreve nos arquivos do rAthena
python traduz_npcs.py --estado               # quanto já foi traduzido
```

### As instâncias: um grupo por instância, e o nome é intocável

Acrescentado em 2026-08-09. Os grupos `magoas`, `orcs`, `sarah`, `hospital`,
`charleston`, `brinquedos`, `jitterbug`, `vermes`, `bakonawa`, `fenrir`,
`demonio`, `porings`, `polvo`, `crescente` e `glastheim` são **um arquivo cada**
— um por instância que a Ordem dos Exploradores manda caçar.

**Por que não um grupo `instancias` único:** a regra é só aplicar grupo
inteiro, e as 16 juntas dão 4.910 falas com distribuição muito torta (Sonho
Sombrio 1.261, Lago de Bakonawa 62). Num grupo só, nada seria aplicável até a
última estar pronta. Uma por vez, cada uma fecha e entra em jogo sozinha.

**O nome da instância nunca se traduz, e agora a ferramenta garante.** Ele é
CHAVE — `instance_create` e `instance_enter` resolvem por string — e aparece no
script como `.@md_name$ = "Palácio das Mágoas";`. Essa atribuição casa com o
`RE_ATRIB`, então o nome **entra no catálogo como se fosse fala**; e o
`RE_TECNICO` não cobre, porque ele protege literal que está *dentro* da chamada
e ali a chamada recebe uma variável.

Quem protege é o `nomes_de_instancia()`, que lê os `Name:` de
`db/re/instance_db.yml` e `db/guerra/instance_db.yml` e os põe em
`tokens_intocaveis` — o `--aplicar` passa a **recusar** esses textos. A lista
sai do banco e não de uma constante, então acompanha sozinha uma renomeação.

**O que fica em branco de propósito** num catálogo de instância, e é bastante:
nome de mapa (`1@spa`), label de evento (`::OnMyMobDead1`), nome único de NPC
(`Lurid Royal Guard#dk`, que vem de `disablenpc`/`npctalk`) e o `.bmp` dos
cutins. No Palácio das Mágoas foram 48 de 303. O `--estado` conta esses como
"não feitos", então **84% ali quer dizer completo** — é o mesmo efeito dos 7
que sobram em `cidades`, que marca 99%.

O `--forcar` existe porque corrigir o glossário não bastava: `--preencher`
sozinho só enche o que está vazio, então uma tradução já gravada continuava
errada. Apareceu ao descobrir que cinco nomes de habilidade que eu tinha
traduzido de cabeça não batiam com os do bRO que já estão no cliente — `Cure`
é **Medicar**, não "Cura"; `Demon Bane` é **Flagelo do Mal**; `Pneuma` é
**Escudo Sagrado**; `Increase/Decrease AGI` são **Aumentar/Diminuir
Agilidade**. Sem o `--forcar`, o NPC continuaria falando um nome que a janela
de habilidades não usa.

**A regra que isso estabelece: nome de habilidade, item, mapa e classe sai da
tabela do bRO que já está no cliente, não da cabeça.** Conferir antes de
escrever — `skillinfolist.lub` para habilidade, `mapnametable.txt` para mapa,
`map_msg_por.conf` (550+) para classe.

São **19.260 falas** em centenas de arquivos. Editar arquivo a arquivo não
termina, não dá para revisar e não sobrevive a uma atualização do vendor.

### Fonte separada de resultado

Há um conflito com a CONVENÇÃO DE CUSTOMIZAÇÃO: diálogo traduzido não tem como
morar em pasta própria, porque o servidor lê o script de onde ele está. A saída
foi separar as duas coisas:

- a **tradução** vive em `rathena/npc/guerra/traducao/*.cat` — nosso,
  versionado, revisável linha a linha;
- o arquivo do rAthena é o **resultado** de aplicar o catálogo, e tem um
  `.INGLES` ao lado.

No dia de atualizar o vendor: restaurar do upstream, reaplicar, e o que não
casar mais **aparece no relatório** em vez de sumir calado — é para isso que o
registro guarda o original:

```
#: npc/kafras/functions_kafras.txt#12 (mes)
- "Welcome to the"        <- trava: se o upstream mudar, recusa
+ "Bem-vindo à"           <- vazio quer dizer "deixa em inglês"
```

### A unidade de trabalho é o texto, não a ocorrência

**43% das 19.260 falas são repetição** (`Cancel`, `[Kafra Employee]`, o nome do
NPC uma vez por fala). São 10.903 distintas. Por isso existe o
`glossario.cat`: traduz uma vez, o `--preencher` espalha por todos os
catálogos. 203 entradas preencheram 718 espaços.

### As duas travas, e a segunda nasceu de a primeira estar errada

**`tokens_intocaveis`** é a parte que impede o pior erro possível. O caso real
que a ensinou, no `functions_kafras.txt`:

```
setarray @wrpD$[0], "Izlude", "Geffen", "Orc Dungeon", ...
else if (@wrpD$[.@j] == "Orc Dungeon") warp "gef_fild10", 52, 326;
```

A mesma string é o rótulo do menu **e** a chave da comparação. Traduzir só o
`setarray` (que é contexto de exibição) sem traduzir o `if` (que não é) faz o
teletransporte **parar em silêncio**: menu bonito em português, destino que
nunca chega.

A primeira correção foi recusar todo texto usado fora de exibição — e derrubou
o menu inteiro da Kafra, que sofre do mesmo padrão. A regra certa distingue:

| | |
|---|---|
| **token interno** — nasce e morre no arquivo | traduz **todas** as ocorrências |
| **nome externo** — `warp "prontera"`, `getitem "Red_Potion"`, label `::On…` | nunca se toca |

**`confere`** completa: recusa a gravação se o arquivo mudar de número de
linhas, de número de literais, ou ficar com aspas ímpares numa linha que antes
estava par. Script do rAthena é sensível a aspas — uma a mais faz o parser
engolir o resto do arquivo, e o erro sai na subida do servidor citando uma
linha que não tem nada a ver.

### `--extrair` num grupo já aplicado apagava o catálogo — 2026-08-04

A extração lia o arquivo **vivo** do rAthena. Depois de um `--aplicar`, aquele
arquivo está em português — então a linha `-`, que é a trava contra mudança do
upstream, passava a guardar a *tradução*, e a `+` saía vazia. Acrescentar um
arquivo novo a um grupo já aplicado e rodar `--extrair servico` esvaziou **595
pares** de uma vez.

O que faz isso perigoso é não dar erro: o comando imprime `595 mudaram no
upstream`, que parece informação e é o relatório do estrago. Um `git checkout`
desfez, mas só porque alguém olhou.

A correção é uma linha: a fonte passa a ser o `.INGLES` quando ele existe — que
é justamente o backup que o `--aplicar` deixa ao lado. Depois dela, o mesmo
comando devolve `714 já traduzidos, 0 mudaram no upstream`.

**A regra que fica: a fonte da extração é sempre o inglês.** Se um dia o
`.INGLES` for apagado, a extração daquele arquivo volta a mentir e não avisa.

### O contexto `atrib` — a palavra que ficava metade em inglês

Entrou em 2026-08-04, com o Mestre do Refino. O `ticket_refiner.txt` guarda a
palavra `"Weapon"`/`"Armor"` numa variável e depois a **interpola** em três
frases de `mes`:

```
.@type$ = "Weapon";
mes "If you want to refine this ^006400"+.@type$+"^000000, ...";
```

O catálogo só extraía literal em contexto de exibição, e atribuição não era um.
A frase sairia "Para refinar esta ^006400**Weapon**" — metade em português,
metade em inglês, e sem erro nenhum para denunciar.

É exatamente o **token interno** da tabela acima: nasce e morre no arquivo, e o
único destino dele é a tela. O `RE_TECNICO` continua sendo testado depois e
ganha de qualquer contexto, então nome externo segue protegido.

**O custo foi medido antes de ligar** — e essa é a parte que vale copiar: +54
pares nos dez catálogos (campal 14, guerra 17, kafra 12, servico 11, o resto
zero), todos nascendo **vazios**, e vazio quer dizer "deixa em inglês". Nenhuma
tradução existente se mexe. Os índices também não andam: eles contam *todos* os
literais, e o comentário do `literais_todos` diz que isso é de propósito,
justamente para a lista de contextos poder crescer. Era o ponto de extensão
previsto.

## `preenche_catalogo.py` — o meio do caminho do `traduz_npcs.py`

```
python preenche_catalogo.py --pendentes crescente          # o que falta traduzir
python preenche_catalogo.py --pendentes crescente saida.txt
python preenche_catalogo.py --gravar crescente t_crescente.py
```

Acrescentado em 2026-08-09, ao traduzir as instâncias. O `traduz_npcs.py`
extrai e aplica; **o que faltava era o meio** — tirar do catálogo só o que
ainda não foi traduzido, e devolver a tradução sem destruir o acento.

**Por que não editar o `.cat` a mão:** porque escrever é o passo perigoso, não
ler (`CLAUDE.md` §4.1). O `.cat` é cp1252, todo editor grava UTF-8 por padrão,
e o estrago é calado — o acento vira `\xef\xbf\xbd` e o byte original já não
está lá. Um catálogo de instância tem 300 a 700 pares e umas 150 linhas
acentuadas: editar isso a mão é apostar 150 vezes seguidas.

### O ciclo completo, por grupo

```
python traduz_npcs.py --extrair <grupo>            # SEMPRE antes (CLAUDE.md §4.13)
python preenche_catalogo.py --pendentes <grupo>
# ... escrever o t_<grupo>.py ...
python preenche_catalogo.py --gravar <grupo> t_<grupo>.py
python traduz_npcs.py --aplicar <grupo> --verificar
python traduz_npcs.py --aplicar <grupo>
```

### A entrada é um módulo Python, e não um TSV

```python
# -*- coding: utf-8 -*-
TRAD = {
    2: u"O aventureiro ",
    3: u" do grupo ",
}
```

O índice é o número que o `--pendentes` imprimiu, do **mesmo** catálogo e na
**mesma** ordem. Índice ausente fica em branco, e branco quer dizer "deixa em
inglês" — é assim que se marca nome de mapa, label e nome único de NPC.

**Não é TSV de propósito.** Metade dos textos de instância são fragmentos de
frase montada com `+`, e o espaço no início e no fim deles é significativo:
` of the party ` vira ` do grupo `. Num TSV esse espaço se perde no primeiro
editor que apara linha, e a frase sai grudada em jogo sem nada denunciar. Entre
aspas ele é visível e sobrevive.

Pelo mesmo motivo a trava é `if not trad` e **não** `if not trad.strip()`:
tradução de **um espaço só** é legítima. No `FacewormsNest.txt` o script monta
`n + " unbroken " + ("eggs"|"egg")`, e em português o adjetivo anda junto do
substantivo — o fragmento do meio vira `" "` e `intactos` migra para o
substantivo. Filtrar por `.strip()` deixava ` unbroken ` em inglês no meio da
frase, calado.

### As três travas, todas fatais

1. **Recusa caractere fora do cp1252** — aspa curva, travessão longo e
   reticências de um byte só passam batido num editor e viram `?` no jogo.
2. **Recusa `\xef\xbf\xbd`** (U+FFFD) em qualquer ponto do resultado.
3. **Recusa aspa dupla** dentro da tradução — o `.cat` delimita com aspas e o
   script do rAthena também.

A gravação troca **só o miolo da linha `+`**, por fatia de bytes. Reescrever o
registro inteiro exigiria remontar o cabeçalho `#:` com o contexto entre
parênteses, e inventar isso é como se perde informação.

### `--pendentes` é distinto por TEXTO, e na ordem do script

43% do acervo é repetição, e a tradução vale para todas as ocorrências. A ordem
é a de primeira aparição no catálogo, que é a ordem do arquivo — o diálogo vem
em sequência, e é o que torna possível traduzir uma conversa inteira sem pular
de um lado para o outro.

## `planta_adereco.py` — copia um adereço de um mapa para outro

```
python planta_adereco.py <nosso-data.grf> <pasta-saida> [mapa] [grf-origem]
```

Receita declarativa no topo do arquivo. Serve para pôr uma peça específica num
lugar específico, em qualquer mapa.

**Por que não é o `edita_mapa.py`.** Aquele é a frente de destruição: tem
semente, fração, sorteio, e **recusa rodar em Prontera** por decisão de ficção.
Relaxar aquele guarda para caber um adereço seria estragar o motivo de ele
existir.

**A peça não é desenhada, é copiada.** A receita não diz "planta o `.rsm` tal
com rotação tal": diz *"vai em `moc_ruins 112,127`, pega o que estiver lá com
este nome de `.rsm`, e põe igual em `prontera 168,199`"*. Foi a tenda do bazar
de Morroc que ditou o projeto, porque três coisas dela um "planta o `.rsm`"
teria perdido:

- **a altura é relativa ao chão.** A tenda está a `y=-2,5` num chão de `-4,0`:
  1,5 afundada de propósito. O que se copia é o **afastamento**, não o `y`
  absoluto — chão `+1,0` em Prontera, tenda em `+2,5`.
- **a escala negativa.** Ela são **duas metades**, e uma tem `escala.x = -0,8`
  — é a outra espelhada. Copiar `1,0` daria duas metades viradas para o mesmo
  lado. O grupo inteiro é reposicionado pelo **centro**, então o afastamento
  entre as metades também sobrevive.
- **o `nodename`** (`RC_sr005`). O `Modelo.novo` do `rsw.py` deixa esse campo
  vazio e o próprio comentário dele avisa que isso é **não verificado**.
  Copiando, a dúvida não se aplica.

Duas armadilhas do caminho, as duas de ferramenta e não de conteúdo:

1. **No nosso `data.grf` o `moc_ruins.rsw` está com flag DES**, que o `grf.py`
   não lê — o de Prontera não está. Por isso o mapa de **origem** sai do GRF do
   bRO, onde ele é `flags=1`. Mesmo tamanho, 141758 bytes. O parâmetro existe
   para isso e tem esse default.
2. **O `verificar()` do `rsw.py` compara contra os bytes de entrada**, então só
   vale *antes* de mexer. Depois de mexer a prova é outra: reabrir a saída,
   conferir a contagem de objetos e a quadtree fechando no byte exato. Este
   script faz as duas, e aborta antes de gravar.

Todo `.rsm` da receita é conferido contra a tabela do GRF **de destino** —
caminho errado não dá erro em parser nenhum, só aparece no cliente, um diálogo
por modelo, e trava quem tiver personagem salvo no mapa.

Instalação: copiar a saída para `cliente\data\`, onde o `DataFolderFirst` a faz
vencer o GRF. **Apagar reverte.** Não toca luz, água, chão nem `.gat` — e por
não tocar o `.gat`, **o adereço não bloqueia passagem**: o jogador atravessa a
tenda.

### A receita de Prontera está vazia — a tenda foi tirada

A tenda foi plantada em 2026-08-04 e **removida no mesmo dia**, por decisão do
dono do projeto: não ficou boa na praça. Remover foi apagar
`cliente\data\prontera.rsw` — sem o override, o GRF volta a servir o mapa
original. Foi a prova prática de que o "apagar reverte" acima é verdade.

A receita continua no arquivo, **comentada**, com a explicação ao lado.
Descomentar replanta. Não é um TODO pendente, é registro — e a ferramenta fica
porque é genérica e porque o que ela ensinou sobre `.rsw` vale para o próximo
adereço.

## `traduz_reputacao.py` — põe em português o modal Reputation Status

```
python traduz_reputacao.py              # aplica
python traduz_reputacao.py --verificar  # só relata, não grava
python traduz_reputacao.py --reverter   # apaga o override
```

**O texto do modal não vem do servidor.** O `ZC_REPUTE_INFO` carrega só `type` e
`points` — dois inteiros por linha. O `Name:` do `db/re/reputation.yml` é rótulo
interno do rAthena e nunca sai da máquina. Quem nomeia as linhas é o cliente,
por dois BSON dentro do `data.grf`:

```
data\contentdata\repute\reputeinfodata.bson    as reputações (chave = o `type`)
data\contentdata\repute\reputegroupdata.bson   os grupos do combo
```

**Os nomes são ASCII de propósito.** O BSON guarda UTF-8, mas o cliente converte
para **CP949** antes de desenhar. A prova está no próprio print: 오크 부락 chega
na tela como `¿ÀÅ© ºÎ¶ô`, que são exatamente os bytes CP949 dessa palavra lidos
com a fonte cp1252 do `AlwaysAscii`. A codepage ANSI desta máquina é 1252 — o 949
é fixo do cliente. E CP949 não tem `á`, `ã`, `ç` nem `ó`: acento aqui não daria
erro em lugar nenhum, daria nome sujo na tela. O `_so_ascii` aborta em vez de
deixar passar.

**Ele também alinha cliente e servidor.** O rAthena declara quatro reputações e
três grupos; o GRF de 2021-11-03 só conhece três e dois — falta Isgard nos dois.
Sem a entrada, o servidor manda `type=4` e o cliente não tem o que desenhar.
Isgard entra como `VISIBLE_EXIST`, então só aparece depois que houver ponto.

**E é por aqui que entra reputação NOSSA.** A quinta entrada, "Honra de Combate",
é a pontuação de PvP da arena (`npc/guerra/honra_de_combate.txt`). São três peças
que precisam do mesmo `Id: 5` — a tabela deste script, o
`db/guerra/reputation.yml` e o NPC —, e mexer numa sem as outras quebra calado.

Ela é `VISIBLE_TRUE` e não `VISIBLE_EXIST` porque a pontuação dela fica
**negativa**: o print de 2026-08-06 provou que `VISIBLE_EXIST` some com o valor
zerado, e o comentário coreano do arquivo diz que ele mostra "quando o valor é 0
ou mais". Com o jogador em −3, a linha sumiria.

Só o **servidor de jogo não lê grupo nenhum**: o `reputationgroup_db.load()` está
dentro de um `#ifdef MAP_GENERATOR` (`src/map/pc.cpp`). O combo do alto do modal é
inteiramente do cliente — ou seja, deste script.

Grava em `cliente\data\contentdata\repute\` e vence o GRF pelo `DataFolderFirst`.
A base é sempre relida do GRF, nunca do override — mesma regra do
`estende_accessoryid.py`. Dois round-trips antes de gravar: o BSON do GRF tem que
voltar idêntico pelo `bson.py`, e o gerado tem que reler igual. BSON tem tamanho
embutido — campo mal medido não dá erro, dá arquivo que o cliente descarta calado.

O cliente só lê isto na **inicialização**: fechar e reabrir.

## `bson.py` — BSON mínimo, com escrita byte a byte fiel

Só os quatro tipos que os `contentdata\*.bson` usam: `0x02` string UTF-8, `0x03`
documento, `0x04` array, `0x10` int32. Qualquer outro **levanta exceção** em vez
de ser pulado — tipo novo tem que parar a ferramenta, não virar dado perdido na
regravação.

Documento é uma **lista de pares** (`Doc`), não um dicionário: a ordem do arquivo
é preservada, e é isso que permite o round-trip byte a byte que prova que o
escritor está certo. Não há `bson` neste Python 2.7, e o pymongo traria tipos e
ordenação que estes arquivos não têm.

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

## `catalogo_cutins.py` — os retratos de NPC que o diálogo pode exibir

```
python catalogo_cutins.py <data.grf> [saida.md]
```

Um *cutin* é a ilustração ao lado do diálogo, ligada com uma linha de script:
`cutin "kafra_01",2;`. Saída em `CATALOGO-CUTINS.md`, na raiz: **1294** nomes
ASCII em 134 prefixos, mais 59 de nome coreano que ficam de fora (o nome teria
de ser escrito em CP949 dentro do script).

**A pasta certa é a de nome coreano:** `data\texture\유저인터페이스\illust\`.
Existe também `data\texture\userinterface\illust` no GRF, com 106 arquivos de
nome ASCII, e ela **não é lida** para cutin — a única string ASCII de illust
dentro do executável é `UserInterface\illust\PET_NOIMAGE.bmp`, um caso isolado.
Conferido nos bytes crus do `GuerraDoEmperium.exe`, e batendo com o
`doc/script_commands.txt` do rAthena.

**Aqui o DES atrapalha**, ao contrário do `inventario_rsm.py`: para plantar um
modelo num mapa basta o nome, mas para *escolher* um retrato é preciso vê-lo.
742 dos arquivos da pasta estão cifrados, e a cifra bate justamente nos retratos
clássicos (`job_*`, `aca_*`, `nov_*`, `moc_*`, quase todo `kafra_*`) — extrair só
os livres dá amostra enviesada. Para pré-visualizar, um extrator com DES (GRF
Editor) ou o próprio jogo.

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

### `acrescentar` aceita rotação e escala explícitas — 2026-08-11

A tupla é `(modelo, célula x, célula y[, rotação Y em graus[, escala]])`.

**Sem o quarto campo a rotação é sorteada**, que era o comportamento único até
aqui: certo para destroço espalhado, onde o sorteio dá variedade de graça, e
errado para peça posta de propósito, onde número sorteado é número inventado.

**Sem o quinto, escala 1,0.** A escala é aplicada em volta da **origem** do
modelo, que nestes fica na base — encolher não tira a peça do chão. Medido: a
fonte do Centro da Ordem desceu de 1,0 para 0,57 e continuou apoiada.

### A célula pode ser FRACIONÁRIA, e em vão par ela precisa ser

`mundo()` devolve o **centro da célula**. Então coordenada inteira só centraliza
em vão de largura **ímpar**: num vão de 4 células o centro cai na **fronteira**
entre a 2ª e a 3ª, e nenhum inteiro o acerta — o mais perto erra **meia célula**,
2,5 unidades.

Foi o que aconteceu com a fonte do Centro da Ordem. O pedido dizia `180,72`, o
pedestal é `x178-181, y70-73`, e o centro dele é mundo `(400, 110)`; a célula
180,72 tem centro em `(402,5, 112,5)`. Em tela a fonte apareceu deslocada para
cima e um pouco à direita do tampo. A correção é `179.5, 71.5`.

**Como achar o número certo:** os limites do vão em mundo são
`(cel_min - largura/2) * 5` e `(cel_max + 1 - largura/2) * 5`; o centro é a média
dos dois. Vale conferir assim depois de plantar — erro de meia célula é pequeno
demais para saltar aos olhos numa planta ASCII e grande o bastante para aparecer
na tela.

A altura continua saindo da célula que **contém** o ponto (`altura_media` indexa
o `.gat` e quer inteiro). Em vão plano tanto faz qual das quatro.

**Achar o vão é o passo anterior, e ele pode ser invisível.** O pedestal da
fonte estava no `.gat` como um platô de altura −5, e uma varredura de alturas o
achou. O tapete da escrivaninha (2026-08-11) não estava em lugar nenhum que se
olhe por reflexo: o `.gat` dá oito células andáveis e planas, e o `.gnd` dá uma
textura só para o corredor inteiro. Os três tapetes de 8x8 células da ala leste
de `auction_01` são **regiões de UV** do mesmo `.bmp`. Antes de escolher a
célula, desenhar as regiões de UV da superfície de topo tile a tile — é o único
jeito de o tapete aparecer, e é ele que define o centro.

O relatório agora imprime uma linha por modelo acrescentado, com a coordenada de
mundo e a rotação — antes dizia só quantos foram.

### Como escolher a escala: procure o modelo nos mapas oficiais

A escala é o número que não dá para adivinhar, e o `Modelo.novo` grava 1,0. O
jeito barato de calibrar é ver **o que a Gravity fez com o mesmo modelo**:
varrer os 821 `.rsw` do GRF do bRO procurando o `filename` leva pouco mais de um
minuto e responde com escala, rotação e em que mapa. Para o
`oldcastle\fountain.rsm` deu cinco instâncias, todas com rotação `0,0,0` e
escala 1,0 (duas com 1,04).

**Para modelo que não é radial, a varredura pode não resolver nada.** As três
instâncias oficiais de `prontera_re\desk_h_02.rsm` no GRF do bRO dão rotação
**90, 180 e 270**, duas delas espelhadas em X (`escala.x = -1,0`): a Gravity
usou os quatro lados, e a média disso não é resposta. Aí quem decide é o lugar
— os quatro sofás de `auction_01` estão todos em 90, e foi de lá que a
escrivaninha tirou a dela. Escolha, não medida, e anotada como tal na receita.

**Mas escala oficial é pista, não resposta** — e nesta mesma rodada ela errou. A
rotação 0 valeu; a escala 1,0 ficou grande em tela e desceu para 0,57. O motivo
é estrutural: a Gravity usa aquela fonte em pátio de castelo de Glast Heim, onde
há espaço, e o pedestal do nosso salão tem 4 células. **Quem copia a escala
oficial copia junto o tamanho do lugar de origem.** A medida que decide é a
outra, logo abaixo: a largura do `.rsm` contra o tamanho do lugar.

**Use o GRF do bRO para essa varredura, não o nosso:** 640 dos 910 `.rsw` do
nosso estão com DES e o `grf.py` não os lê. No do bRO estão todos limpos.

### Medir se o modelo cabe: é o `mede_rsm.py`, logo abaixo

Saber a largura do modelo antes de plantar evita a rodada de "ficou gigante".
Isso deixou de ser trabalho de rascunho em 2026-08-11: virou ferramenta.

## `mede_rsm.py` — o tamanho e a frente de um modelo 3D

```
python mede_rsm.py <data.grf> prontera/sofa_01.rsm
```

Imprime, para cada nó do `.rsm`, a caixa envolvente em unidades de mundo (5 por
célula) e em células; depois o nó de maior planta, de que lado está a parte
alta, e a lista de **texturas conferidas contra aquele GRF**.

É o passo 4 da receita de "mudar a aparência de um mapa" (`RECEITAS.md` §6), e
existe porque **escala oficial é pista e não resposta**: ela veio do lugar de
origem do modelo. A fonte do Centro da Ordem entrou com o 1,0 de Glast Heim e
ficou grande num pedestal de 4 células.

**A barra pode ser normal** no argumento — o caminho é normalizado dentro do
script, porque barra invertida no `argv` do console daqui é uma dor.

### As quatro coisas que ele embute, e as quatro custaram caro

1. **`X` = largura, `Y` = profundidade, `Z` = ALTURA.** Ler `X × Z` como planta
   troca profundidade por altura e devolve número plausível e errado — a
   escrivaninha do Centro da Ordem é 4,0 × 2,8 células e pelo eixo errado sai
   3,9 × 1,5, que é a direção que faz um móvel parecer caber onde não cabe. A
   prova é medir peça alta e fina: a coluna `내부소품\기둥2` dá
   6,34 × 6,34 × **30,21**.
2. **Nó a nó.** O `pos` do nó raiz é offset no espaço do modelo, não dimensão.
   Juntar tudo num box só dá 148,90 de largura (29,8 células) para uma
   escrivaninha de 4,0.
3. **A trava dos 0 bytes.** Depois dos nós de um `.rsm` 1.x vêm dois `int32`
   (`numPosKeyframes` e `numVolumeBoxes`, zero nos modelos vistos). Quem parar
   nos nós sobra 8 bytes — e as dimensões impressas até ali **parecem boas**.
   Formato de malha é cheio de campo opcional por versão; sobrar ou faltar byte
   significa que a suposição estava errada, e aí nada do que sai vale. O script
   aborta em vez de imprimir.
4. **As texturas.** O `edita_mapa.py` confere o caminho do `.rsm` e para aí.
   Textura que não resolve **não dá erro em parser nenhum** — dá superfície
   quebrada na tela.

### De que lado é a frente, e daí a rotação

A última linha da medida (`parte ALTA em Y médio ... -> lado +Y`) é o que
resolve rotação de móvel sem chutar: **o encosto é o lado do Y onde o modelo é
alto**. Nos dois sofás do Centro da Ordem é o `+Y`.

Com isso, e com a calibragem feita nos quatro sofás que o `auction_01` já
tinha (todos em rot 90, com o par leste e o oeste separados só pelo **sinal da
terceira escala**, que espelha a profundidade), a regra fechou:

**`+Y` → (sen θ, cos θ) em (X, Z).** Em **rot 0 as costas apontam para o
norte**; em rot 90, para o leste. E a consequência que engana sozinha:
**rot 0/180 põem a LARGURA no eixo leste-oeste, e 90/270 no norte-sul** — o
contrário do que a intuição sugere.

Confirmado pelo outro lado nos 22 usos oficiais do `sofa_01` em `prt_cas` e
`prt_cas_q`: todas as instâncias de rot 270 têm parede colada a oeste.

Em 2026-08-11 as duas estátuas do Centro da Ordem fecharam a mesma regra por
fora, e vale escrever o ângulo do jeito que se usa: **rot 0 olha para o sul,
90 para oeste, 180 para norte, 270 para leste** (é a mesma conta — as costas
apontam para o lado oposto). Junto veio a ressalva: **qual ângulo é o "de
frente" muda de modelo para modelo, mesmo dentro de uma família numerada.**
No `prt_lib`, lado a lado na mesma parede e olhando as duas para o norte, a
`prn_statue_08` está em rot 180 e a `prn_statue_02` em rot 0.

### O que ele NÃO responde: onde é o centro da peça

Ele mede **nó a nó** de propósito (item 2 acima), e nó a nó não remonta o
modelo. Nas `prn_statue_*` isso aparece como duas caixas que não se encontram —
a base em `X −21,50..−14,45` e a figura em `X −5,13..3,91`, uma fora da outra,
o que parece leitura corrompida e não é.

Quem precisa do centro remonta na mão, e a regra é curta: o vértice do nó
**raiz** entra como `vértice − pos_raiz`; o do **filho**, deslocado de
`pos_filho − pos_raiz`. A prova de que está certo é a base cair centrada na
origem (`−3,53..+3,53` nos dois eixos, nas duas estátuas). Daí sai o que
interessa ao `edita_mapa.py`: **a origem do modelo é o centro da base**.

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

## `valida_visual.py` — quais itens este cliente consegue desenhar

```
python valida_visual.py                     # resumo, TODOS os itens
python valida_visual.py --cabeca            # só chapéu com View (recorte antigo)
python valida_visual.py --id 420047         # um item, recurso por recurso
python valida_visual.py --id 32258,490337   # vários
python valida_visual.py --listar            # os que quebram
python valida_visual.py --ok                # os que funcionam
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

Para cada item, confere no GRF **e** no `data\` solto (o `DataFolderFirst` faz o
disco vencer, mas para existir basta um dos dois):

| camada | vale para | arquivos |
|---|---|---|
| sprite de chão | **todo item** | `.spr` + `.act` em `sprite\<item>\` |
| ícones | **todo item** | `texture\<ui>\item\` e `\collection\` |
| sprite de cabeça | só chapéu com `View` | `.spr` + `.act` masculino e feminino |

### O recorte estava errado, e isso foi corrigido em 2026-08-01

Até essa data o script só olhava **item de cabeça com `View`** — 5301 dos 13001
itens. Os outros 7700 nunca eram conferidos, e a conclusão silenciosa era que
não podiam quebrar.

Quem desmentiu foi o Mercado Contemporâneo. O **Anel de Júpiter (32258)** é
acessório, não passava nem perto do filtro, e abrir a loja do Acessorista
entregava caixa modal:

```
Resource File Loading fail
texture\<ui>\item\ringofjupiter.bmp
```

**Ícone que falta é modal, não só feio** — e ícone todo item tem. Nove dos onze
acessórios do mercado estavam nesse estado, e o validador dizia que estava tudo
bem porque nem olhava. Por isso `icone do inventario` entrou na lista `FATAIS`.

Consequência para leitura de números antigos: **medição de antes de 2026-08-01
não é comparável com medição de depois**, porque o critério mudou nos dois eixos
(mais itens considerados, e ícone passou a contar como quebra). O `--cabeca`
existe para reproduzir o recorte antigo quando for preciso comparar.

Duas outras cegueiras caíram junto:

- **Só lia o `item_db_equip.yml` do rAthena.** Item NOSSO, de
  `db/guerra/item_db.yml`, era invisível — os cinco placeholders do mercado
  foram pulados com "não está no item_db_equip.yml" numa passada que resolveu
  todos os outros, e o motivo não era arte faltando, era o arquivo não ser
  lido. Agora lê os dois, na mesma ordem em que o servidor os encadeia.
- **Arma tem `View` também**, e significa outra coisa (a classe de sprite da
  arma, não um id de `accessoryid`). Por isso o campo usado na camada de cabeça
  é `view_cabeca`, que só é preenchido quando o item ocupa slot de cabeça.

### Medições

| | 2026-07-31 (só chapéu) | 2026-08-01 (só chapéu) | 2026-08-01 (todos) |
|---|---|---|---|
| considerados | 5301 | 5301 | **13001** |
| desenháveis | 3618 | 3620 | 8502 |
| **quebram** | **548** | **552** | **1902** |
| sem `itemInfo.lua` | 1135 | 1129 | 2597 |

O salto de 548 para 1902 não é regressão: é o que já estava quebrado e ninguém
media. As diferenças pequenas na coluna do meio vêm das 25 entradas postas pelo
`completa_iteminfo.py` e do ícone ter virado critério de quebra.

## `instala_visual.py` — põe a arte de um chapéu no lugar certo

```
python instala_visual.py --id 420047                     # só mostra os destinos
python instala_visual.py --id 420047 --grf <outra.grf>   # puxa da outra GRF
python instala_visual.py --id 32258,490337 --grf <...>   # vários de uma vez
python instala_visual.py --id 420047 --de C:\extraido    # ou de pasta extraída
python instala_visual.py --todos --grf <outra.grf>       # conta o que daria
python instala_visual.py --todos --grf <outra.grf> --aplicar
```

O par do `valida_visual.py`: aquele diz o que falta, este põe no lugar. Herda
dele o alcance, então desde 2026-08-01 também cobre **item que não é chapéu** —
ver a seção acima sobre o recorte que estava errado.

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

   **Cuidado ao mexer nessa regra:** ela vale *só para chapéu*. Item que não é
   chapéu tem `view_cabeca` nulo e não tem camada de cabeça nenhuma para
   faltar — passá-lo por esse teste o descartaria como incurável quando ele só
   precisa dos 4 ícones.

### Rodada de 2026-08-01 — os 77 itens do Mercado Contemporâneo

Primeira aplicação com o alcance novo, e o resultado mede o tamanho da cegueira
anterior: **43 dos 77 itens do mercado estavam sem NENHUM dos 4 arquivos**, e
nenhum deles aparecia no validador antigo porque quase todos são acessório,
armadura, escudo, capa, sapato ou arma.

```
python valida_visual.py  --id <os 77>                       # 43 com falta
python instala_visual.py --id <os 77> --grf "<grf do bRO>"  # 272 arquivos
python valida_visual.py  --id <os 77>                       # 0 com falta
```

272 arquivos copiados, **0 faltando** — a GRF do bRO tinha tudo. Detalhe do
percurso que vale registrar: a primeira passada pulou 5 itens com "não está no
item_db_equip.yml", e eram justamente os placeholders NOSSOS. Foi o que motivou
o `valida_visual.py` a ler também o `db/guerra/item_db.yml`.

### Rodada de 2026-08-01 — `--todos --aplicar` no cliente inteiro

Logo depois, o lote completo. Dos 1902 itens quebrados:

| | | |
|---|---|---|
| **resolvidos** | **446** | a GRF do bRO tinha tudo |
| parciais, pulados pelo tudo-ou-nada | 102 | tinha só parte |
| a GRF do bRO não tem | 977 | |
| `View` fora do `accessoryid.lub` | 377 | sem cura por arte |

Medido pelo `valida_visual.py`, sobre os 13001 itens:

| | antes | depois |
|---|---|---|
| desenháveis | 8502 | **8948** |
| quebram o cliente | 1902 | **1456** |

**1980 arquivos, 22,1 MB** escritos em `cliente\data\` no dia (505 `.spr`,
505 `.act`, 970 `.bmp`), contando as duas rodadas — a do mercado e esta.

Detalhe que confirma que o lote de 2026-07-31 tinha feito o serviço na camada
de cabeça: os números do `--cabeca` **não se mexeram** (3620 desenháveis, 552
quebram). Os 446 curados agora são todos item que não é chapéu — exatamente o
que o recorte antigo nunca olhou.

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

## `doura_arte.py` — faz arte nova recolorindo a arte que já existe

```
python doura_arte.py --de 6121 --recurso pincel_do_infinito
python doura_arte.py --de 6121 --recurso pincel_do_infinito --aplicar
python doura_arte.py --de 6121 --recurso pincel_do_infinito --previa <pasta>
python doura_arte.py --recurso pincel_do_infinito --reverter --aplicar
```

**É o terceiro caminho da arte de um item nosso.** Os outros dois são o
`arte_de` do `instala_item.py` (dois IDs apontando para o mesmo desenho) e o
`instala_visual.py` (trazer arte pronta do bRO). Este serve para o caso em que
nenhum dos dois serve: quando o item novo tem de ser **reconhecível ao lado** do
velho, e não igual a ele.

Foi o caso do **Pincel do Infinito (30992)**: ele senta na mochila ao lado do
Pincel de Maquiagem e do Pincel de Grafite, e três pincéis idênticos é problema
de leitura. A Tinta Infinita (30993) podia usar `arte_de` porque o jogador nunca
tem as duas tintas com a mesma função ativa.

**Custa quase nada porque a arte de item de RO é quase toda indexada.** Dos
quatro arquivos, o `.spr` de chão e o ícone de 24x24 são imagens de 256 cores
com a paleta em bloco próprio — recolorir é reescrever **1024 bytes**, e nenhum
pixel é tocado. Só a `collection` é RGB de verdade, e mesmo ela tem 75x100.

### A rampa, e por que não se empurra o matiz

Não se escolhe cor por pixel: escolhe-se uma **rampa**. Cada cor da origem vira
uma luminância (`0.299R + 0.587G + 0.114B`) e a luminância escolhe um ponto da
rampa, que vai de marrom escuro a amarelo pálido passando por ouro. O volume da
peça original — o que é sombra e o que é brilho — fica intacto, porque é
exatamente isso que a luminância carrega.

**Empurrar o matiz daria amarelo chapado.** É essa a diferença entre "amarelo" e
"dourado", e é por isso que a rampa tem cinco paradas: menos que isso o meio-tom
achata, mais que isso não se distingue na tela. Trocar de metal é trocar cinco
pares de números em `RAMPA_OURO`.

### A aura

`--aura x,y,raio,força`, em coordenadas de **tela** (y=0 no topo), e só na
`collection` — no ícone de 24x24 ela vira borrão. É um halo radial que mistura o
que estiver embaixo com uma cor quente, com intensidade caindo com o quadrado da
distância.

**A mistura é por interpolação, não por soma**, e isso não é detalhe: o fundo
daquela imagem é branco puro, e luz somada a (255,255,255) não vai a lugar
nenhum.

### Três coisas que são armadilha

- **A fonte é o GRF do bRO, não o nosso.** As entradas de arte de item no
  `data.grf` de 2021-11-03 estão com DES (flags 3 e 5) e o `grf.py` não lê
  arquivo cifrado. O do bRO é mais novo e não usa DES — o mesmo caminho que o
  `instala_visual.py` já usava.
- **A ordem dos canais muda entre os formatos**: BMP guarda BGRA, SPR guarda
  RGBA. Trocar transformaria o marrom da rampa em azul.
- **Duas cores nunca são tocadas**: o magenta puro (255,0,255), que é a
  transparência do ícone e do `.spr` (e o índice 0 do `.spr`, que o cliente
  trata como vazio seja qual for a cor), e o branco puro da `collection`.
  Dourar a primeira pinta o fundo do ícone de ouro sólido; dourar a segunda
  pinta a moldura da janela de descrição.

O `.act` passa **intacto** — é animação, não imagem. Está na lista só para o
item ter os quatro arquivos: sem ele o cliente dá `Cannot find File` ao desenhar
o item no chão.

### Onde grava, e o que isso obriga

Em `cliente\data\...`, que vence o GRF pelo `DataFolderFirst` — a mesma lógica
do `tinge_dimensao.py` e do `destroi_mapa.py`. Ou seja: **é mudança de cliente e
vai por patch**, não pelo `implanta.sh` (`RECEITAS.md` §0). O original nunca sai
do GRF, então `--reverter` é só apagar os arquivos e não há backup a manter.

O nome do recurso é **ASCII de propósito** — recurso novo não tem a amarra do
byte CP949 coreano dos itens do kRO, e ASCII é o único que sobrevive ao console,
ao git e ao campo `recurso` do `instala_item.py`. As pastas continuam coreanas:
quem monta os caminhos é o `valida_visual.caminhos()`, fonte única deles no
projeto.

O `--previa` grava PNGs (antes/depois, 4x) para conferir com o olho antes de
gravar. PNG cru, escrito no próprio script: o cliente não lê PNG, e instalar
PIL para conferir uma imagem de 75x100 seria trocar uma dependência por um
olhar.

**Depois de aplicar**: `valida_visual.py --id <id>` tem que dar 4 de 4, e o
cliente precisa ser fechado e reaberto.

## `instala_manto.py` — põe a arte de um manto cosmético no lugar certo

```
python instala_manto.py --id 480117                    # só relata
python instala_manto.py --id 480117 --aplicar
python instala_manto.py --ids 480055,480096 --aplicar
python instala_manto.py --id 480117 --grf <outra.grf>   # outra origem
```

Irmão do `instala_visual.py`, para a camada que ele não alcança. Escrito em
2026-08-08, quando o Manteleiro (`Costume_Garment`) abriu no Mercado de
Visuais — até então manto era a única frente cosmética sem ferramenta, e o
`PENDENCIAS.md` §4 registrava isso como aberto.

**A diferença que obrigou um script separado é a FORMA da arte:**

| | chapéu | manto |
|---|---|---|
| arquivos de item | 4 | 4 |
| arquivos de visual | 4 (M/F × spr/act) | **uma pasta por recurso**, com spr e act por CLASSE de personagem e por sexo |
| total por item | 8 | **250 a 700** |

Por isso aqui não existe lista canônica de caminhos como o
`valida_visual.Cliente.caminhos`: o alvo é a subárvore
`data\sprite\<manto>\<recurso>\` inteira, e o que vai para o disco é a
**diferença** entre o que a origem tem e o que o nosso cliente já tem. Rodar
duas vezes não copia nada na segunda.

### O que ele NÃO faz — e quem faz, desde 2026-08-09

Ele **não** mexe no `spriterobeid.lub`/`spriterobename.lub` — a tabela que
traduz o `View` do `item_db` no nome da pasta. Isso é do
**`estende_robeid.py`**, logo abaixo. A divisão é a mesma dos dois do lado do
chapéu: **um cuida do nome da pasta, o outro traz os arquivos**, e só os dois
juntos curam o item.

**Este cliente não desenha manto com slot acima de 120** — medido em tela em
2026-08-09, e não é a tabela que limita. Então o `estende_robeid.py` não
acrescenta slot: ele **reaproveita** um dos 40 slots que este cliente aceita e
que não têm arte nenhuma. A seção dele explica; aqui basta a consequência
prática.

**Manto com `View` fora da tabela continua sendo RECUSADO** por este script,
com o motivo por extenso, em vez de copiar 600 arquivos que o cliente nunca vai
procurar. O conserto é pôr um `View:` reaproveitado no `db/guerra/item_db.yml`
e rodar o `estende_robeid.py` — aí a pasta passa a existir para o script, e ele
copia.

### Duas correções de 2026-08-16, as duas achadas pela mesma capa

As duas apareceram ao pôr a Som do Luar (480446) e as Asas de Garuda (480278)
no Capeiro — as primeiras capas de **status** a precisar de arte de manto por
conta própria. A 480188, que era a única com `View` até então, andava de carona
na versão cosmética dela (480189), e foi essa carona que escondeu as duas por
uma semana.

**A trava de tipo era `Costume_Garment` e só.** Ela nasceu assim em 2026-08-08,
quando o Manteleiro era a única frente de manto — e ficou errada no dia em que
uma capa de status apareceu. O cliente não pergunta em que slot a peça se
equipa: quem manda o sprite desenhar é o `View`, e o caminho da arte é o mesmo
nos dois casos. Eram **duas definições da mesma coisa** (o
`estende_robeid.manto()` já lia os dois locais) e só uma estava certa; agora as
duas leem `Garment` **ou** `Costume_Garment`.

**O `item_de` devolvia a entrada do rAthena, não a nossa** — e esta não era
regressão: os dez mantos já instalados eram recusados exatamente do mesmo
jeito. O `vv.le_item_db` recebe os dois `item_db` e devolve uma **lista chata**,
com um registro por bloco; pegar o primeiro é pegar o do `db/re/`, com o `View`
**original**. O script então procurava 122, 131, 160 ou 165 na tabela do
cliente — que para em 120 de propósito — e respondia *"view X só existe no
spriterobeid do bRO, rode antes o `estende_robeid.py`"* sobre itens cujo
`estende_robeid.py` já tinha rodado. Alto, e pelo motivo errado.

Pegar o **último** também não serve: o bloco de override é YAML parcial, só tem
`Id`, `AegisName`, `Name` e `View`, e `locais` viria vazio — aí a trava de capa
recusaria a peça. Por isso é **mescla campo a campo**, com o que o override
declarou vencendo e o resto vindo do rAthena.

Os dez antigos escaparam por acidente: a arte deles foi copiada em 2026-08-09,
**antes** de o `View` ser reapontado, e ela vai para uma pasta cujo nome não
depende do slot — sobreviveu à troca, e ninguém rodou a ferramenta de novo para
descobrir. **Foi por eles que a correção se provou:** rodar com 480155 e 480188
na mesma linha e ver *"já completo neste cliente"* é uma marca que não depende
do efeito procurado, a mesma lição do `ajusta_tamanho_fonte.py`.

**As outras duas ferramentas que leem o `le_item_db` ainda erram**, do outro
lado — elas montam `dict` por compreensão e ficam com a última. Está no
`CLAUDE.md` §5 e em `PENDENCIAS.md` §1v, com a medição.

### Duas correções de 2026-08-09, as duas vindas do `estende_robeid.py`

**Disco primeiro, quando o GRF é o nosso.** O `tabelas_robe` lia só o GRF, e o
`DataFolderFirst` faz `cliente\data\` vencer — então, logo depois de o
`estende_robeid.py` gravar o override, este script continuava respondendo pelo
GRF de 2021 e **recusava um manto cuja entrada acabara de ser posta**. Mesma
lição que o `valida_visual.le_tabelas_acessorio` já tinha aprendido do lado do
chapéu, e que aqui custou uma rodada.

**`RobeNameTable`, e não `RobeNameTable_Eng`.** O `spriterobename.lub` tem
**três** globais, e o `vv.tabela_lua` devolve os pares de todos numa lista só —
um `dict()` por cima ficava com a última, que é a `_Eng`. Das 120 entradas do
nosso cliente, 98 têm os dois nomes iguais e a diferença não aparecia; nas **17
em que eles diferem, a pasta que existe no GRF é a da `RobeNameTable`** (nome
coreano) em 17 de 17, e a da `_Eng` em 0. O `_Eng` é lista paralela de
consulta, não caminho. Com ele, manto antigo dava *"a origem não tem a pasta de
manto"* — alto, mas pelo motivo errado.

### Duas armadilhas que ele resolve

**O prefixo tem de ser exato, com a barra no fim.** `Wing_Of_Angel_Move` é
prefixo de `Wing_Of_Angel_Move_RD` e de `_BK` e `_GD`: casar por substring
mistura quatro mantos diferentes num só e faz a conta de arquivos faltando dar
um número plausível e errado.

**Manto sem `View` não é manto quebrado.** A Aura Nevada (480097) não tem
`View` nenhum, e não é falha: o que ela faz é um `hateffect` no `Script` do
item — efeito de tela, não desenho vestido. O script separa esse caso dos
outros e diz que não há arte a instalar.

### O que ele compartilha com o `instala_visual.py`

Grava em `cliente\data\`, que o `DataFolderFirst` faz vencer o GRF — **o GRF
nunca é aberto para escrita**, e apagar a pasta reverte. E usa o
`vv.caminho_disco` para o nome no disco, que **não** é o nome coreano: é o
mojibake que o `CreateFileA` produz na codepage ANSI do sistema. Gravar com o
nome "certo" cria uma pasta que o cliente nunca abre.

## `estende_accessoryid.py` — ensina ao cliente um slot de visual que ele não conhece

```
python estende_accessoryid.py                          # o que já foi acrescentado
python estende_accessoryid.py --id 400287 --grf <bro>  # pelo item
python estende_accessoryid.py --view 2260 --grf <bro>  # pelo View
python estende_accessoryid.py --id 400287 --grf <bro> --verificar
python estende_accessoryid.py --reverter               # apaga o override
```

Escrito em 2026-08-02 para pôr o **Capacete de Intensificação (400287)** no
Chapeleiro. Ele fecha o buraco que os outros dois deixavam em aberto, e a
diferença entre os três é o que importa entender:

| ferramenta | traz o quê |
|---|---|
| `completa_iteminfo.py` | **nome e descrição** do item, para o `itemInfo.lua` |
| `instala_visual.py` | os **arquivos** de arte (`.spr`, `.act`, `.bmp`) |
| `estende_accessoryid.py` | a **entrada de tabela** que diz que o slot existe |

Os **377 itens** que o lote de 2026-08-01 marcou como "sem cura por arte" eram
exatamente este caso. O relatório da época dizia "`View` fora do
`accessoryid.lub`" e concluía, corretamente para as ferramentas de então, que
copiar arquivo não resolveria — **mas a conclusão virou "não tem solução", e
essa parte estava errada.** Não faltava arquivo: faltava a linha
`ACCESSORY_Legacy_of_Wise_One_J = 2260` numa tabela que ninguém editava porque
ela é bytecode dentro do GRF.

Nosso GRF de 2021-11-03 conhece **2192 slots** (View máximo 2203); o do bRO
conhece **2654** (máximo 2668). Este script copia de lá para cá as entradas que
pedirmos, uma a uma.

### Grava em texto, e não encosta no GRF

A saída são dois arquivos Lua **em texto puro** em
`cliente\data\luafiles514\lua files\datainfo\`:

```
accessoryid.lub   ACCESSORY_IDs = { ACCESSORY_X = 2260, ... }
accname.lub       AccNameTable  = { [ACCESSORY_IDs.ACCESSORY_X] = "_X", ... }
```

O cliente lê `.lub` em texto e em bytecode indiferentemente — os arquivos do
ROenglishRE que ele consome todo dia são texto —, e o `DataFolderFirst` faz o
disco vencer o GRF. **Apagar os dois arquivos reverte** (ou `--reverter`), e o
GRF nunca é aberto para escrita.

Como toda mudança de `.lub`, **só entra na inicialização do cliente**.

### A base é sempre o nosso GRF — o override é derivado, nunca acumulado

Esta é a regra que mantém a coisa segura, porque o raio de alcance é grande:
essas duas tabelas valem para os **5301 chapéus** do cliente, não só para o que
se está acrescentando.

A cada rodada a base é **relida do GRF** e as entradas nossas são reaplicadas
por cima. As já acrescentadas são recuperadas do próprio override, como
**diferença contra o GRF** — então rodar duas vezes não duplica, não perde
nada, e as 2192 originais não têm como derivar de rodada em rodada.

Toda entrada nova passa por duas travas, que são as duas formas de estrago que
a rodada do `skillid.lub` (2026-07-30) ensinou:

- **constante que já existe aqui com id diferente** → aborta;
- **View que já existe aqui com constante diferente** → aborta, porque
  sobrescrever trocaria a arte de um chapéu que hoje funciona.

E antes de gravar um byte, o texto gerado é **relido e comparado entrada a
entrada** com o que deveria conter. Mesmo critério de round-trip do `rsw.py`:
layout errado não dá erro, dá arquivo corrompido — e aqui o arquivo corrompido
levaria junto o cliente inteiro.

### O round-trip pegou os dois erros da primeira rodada

Vale registrar porque nenhum dos dois daria erro visível:

1. **Cabeçalho `unicode` promovendo o corpo inteiro.** Os sufixos de acessório
   são bytes CP949 escapados em `\ddd`; com o cabeçalho como `u"""..."""` a
   concatenação virava `unicode` e o `chr(176)` da releitura estourava. A
   correção é o cabeçalho ser `str`. Sem o round-trip isso teria virado arquivo
   gravado meio certo.
2. **`ACCESORY_RED_NAVY_HAT` e `ACCESORY_BERET`** — a tabela da própria Gravity
   tem duas constantes escritas com **um S só**. O leitor de texto prendia o
   nome a `ACCESSORY_\w+` e perdia as duas caladas; o round-trip acusou "2191
   lidas contra 2193 gravadas". O padrão agora aceita qualquer identificador.

### A ordem completa, para um item que precisa de tudo

```
1. python completa_iteminfo.py --id <n>                    # nome e descricao
2. python estende_accessoryid.py --id <n> --grf "<bro>"    # o slot de visual
3. python instala_visual.py     --id <n> --grf "<bro>"     # os arquivos
4. python valida_visual.py      --id <n>                   # tem que dar 0
5. fechar e reabrir o cliente
```

**O passo 2 vem antes do 3, e não é intuitivo.** O `instala_visual.py` só sabe
procurar as 4 sprites de cabeça depois que o `accessoryid` lhe diz o sufixo do
arquivo (`_Legacy_of_Wise_One_J`). Rodando na ordem errada ele instala os 4
ícones, relata "faltando 0" e o chapéu continua invisível.

Por isso o `valida_visual.py` passou a ler as duas tabelas **do disco antes do
GRF** (`le_tabelas_acessorio`), que é a ordem que o cliente usa. Sem essa
mudança as duas ferramentas continuariam respondendo pelo GRF de 2021 e
jurariam que o View não existe — com o chapéu desenhado na tela.

### Rodada de 2026-08-02 — o 400287

```
base (nosso GRF): 2192 constantes, 2187 nomes, View maximo 2203
  [novo] View 2260 -> ACCESSORY_Legacy_of_Wise_One_J  sufixo '_Legacy_of_Wise_One_J'
round-trip OK: 2193 constantes, 2188 nomes
```

Depois dele o `instala_visual.py` achou as 4 sprites de cabeça na GRF do bRO e
o `valida_visual.py --id 400287` deu **0 faltando**, com os 8 recursos.

Medido no cliente inteiro, o efeito é exatamente o esperado e nada mais:

| | antes | depois |
|---|---|---|
| desenháveis | 8948 | **8949** |
| quebram o cliente | 1456 | **1455** |

**+1/−1 e nenhum outro número se mexeu** — que é a prova de que estender a
tabela não mexeu nos 2192 slots que já funcionavam.

### O par meio-presente — 2026-08-05

São **duas** tabelas, e até esta data o script tratava as duas como uma só. Se
o `View` já estivesse no `accessoryid.lub` ele imprimia `[ja tem]` e ia embora —
sem olhar se o `accname.lub` tinha o sufixo correspondente.

**Cinco Views deste cliente estão exatamente assim: id sim, sufixo não.** O
efeito no jogo é o pior tipo: o cliente sabe que o slot existe e não sabe que
arquivo abrir, então o chapéu fica **invisível, sem caixa de erro nenhuma**.
Quem denunciou foi o 18742 (Luar de Cristal, View 881) — os 4 arquivos dele
estão no nosso GRF, o View também, e mesmo assim o `valida_visual.py` acusava
`view 881 no accessoryid`. Está certo: o `Cliente.acc` só conta o View cujo par
exista nas **duas** tabelas.

O ramo novo é o `[nome]`, que acrescenta só o sufixo. E ele tem uma **trava que
os outros ramos não têm**, escrita depois de o estrago acontecer:

> Dos 5, o bRO tem sufixo para os 5 — mas para **três** (880, 883, 1074) o
> arquivo de sprite não existe em GRF nenhum. Gravar o sufixo desses três
> trocou "invisível calado" por `Cannot find File` **modal** em 6 itens. Antes o
> cliente não tinha nome de arquivo para procurar; depois passou a ter um que
> não existe.

Por isso o ramo `[nome]` confere que as 4 sprites existem em algum dos dois
GRFs **antes** de gravar, e recusa se não existirem. A trava vale **só para
ele**: View novo já chega quebrado com modal, então acrescentar não piora nada e
o `instala_visual.py` copia a arte logo em seguida. Aqui não há o que copiar.

A recuperação do override também precisou mudar. Entrada só-de-nome tem a
constante **dentro** da base do GRF, então o teste antigo (`const not in
base_ids`) não a reconhecia como nossa — e como a base é relida do GRF a cada
rodada, a rodada seguinte a apagaria calada. Agora `const in ov_nomes and const
not in base_nomes` também conta.

## `estende_robeid.py` — põe a arte de um manto num slot que o cliente aceita

```
python estende_robeid.py                    # aplica e relata
python estende_robeid.py --verificar        # só relata
python estende_robeid.py --reverter         # apaga o override
python estende_robeid.py --sonda 114=C_20th_Anniversary_Wing
```

Escrito em 2026-08-09 para ser o irmão do `estende_accessoryid.py` do lado do
manto — e **reescrito no mesmo dia**, quando a medição em tela mostrou que
estender a tabela não serve para nada neste cliente. O nome ficou; o que ele
faz é outra coisa.

### O teto de 120 — a medição que mudou a ferramenta

**Este cliente não desenha manto com slot acima de 120.** A tabela não tem nada
a ver com isso: ela foi levada a 158 entradas contíguas, o cliente a leu, e
nada mudou.

| | slot |
|---|---|
| desenham | 61, 73, 75, 82, 90, 99, 104, 114 |
| **não** | 122, 136, 148, 154, 158 |

As outras explicações caíram uma a uma, e vale registrar **por quê** cada uma
caiu — é o que impede alguém de refazer o mesmo caminho:

| hipótese | como foi descartada |
|---|---|
| falta de arte | o Escudo de Oridecon (slot 90) desenha, e a arte dele foi copiada na mesma rodada pelo mesmo `instala_manto.py` |
| o arquivo não chega ao cliente | o horário de **acesso** dos dois `.lub` mostra o cliente abrindo os dois na inicialização — e a sonda confirmou na tela |
| buraco na numeração | a faixa foi fechada de 1 a 158 e continuou sem desenhar |
| corte no servidor | o campo é `uint16` no pacote e `int16` no `status` |

Sobra teto no próprio cliente. Levantá-lo é patch de exe, e está no
`PENDENCIAS.md` §4 — **não** foi feito: sem desmontador, varredura de bytes só
devolve `cmp` que não são instrução.

### A sonda — "este arquivo chega à tela?"

```
python estende_robeid.py --sonda 114=C_20th_Anniversary_Wing
```

Reaponta um slot que **já funciona** para a pasta de outro manto, bem
diferente. Serve para uma pergunta só, e é a que tentativa e erro não responde:
o cliente está montando a tabela a partir deste arquivo, ou lê o arquivo e usa
a do GRF?

O slot 114 é a Espada do General. Depois de reabrir o cliente e equipá-la:
**asas** = o override manda; **espada** = o override é lido e ignorado.

É a mesma lição do `ajusta_tamanho_fonte.py` (`CLAUDE.md` §5): antes de
calibrar valor, provar que o patch chega à tela com uma marca que **não**
dependa do efeito procurado. Aqui ela respondeu numa rodada o que três
hipóteses não responderam.

A sonda se escreve em duas linhas no topo dos `.lub` gerados — sonda esquecida
no disco é um manto desenhando a coisa errada meses depois. Rodar sem
`--sonda` desfaz.

### O que ele faz: reaproveita slot morto

Dos 120 slots que este cliente aceita, **40 não têm arte nenhuma** — a tabela
conhece o nome da pasta e a pasta não existe em GRF nenhum. Esses já não
desenham nada, então apontá-los para a arte de um manto novo não tira coisa
alguma de ninguém.

**A fonte da verdade é o `View:` do `db/guerra/item_db.yml`**, e isso é
deliberado. Quem decide qual manto usa qual slot é o item_db; o script lê de lá
e escreve a tabela do cliente para combinar. **Não há lista de-para do outro
lado, e não pode haver** — seria a metade-no-cliente do `CLAUDE.md` §9 outra
vez, duas listas divergindo sem dar erro. Com uma fonte só, rodar de novo não
muda nada, e `--reverter` e "tirar o `View:` do item_db" dão no mesmo.

Três travas, e as três abortam:

- slot doador **acima de 120** — este cliente não o desenha;
- slot doador que **tem arte** aqui — reaproveitar apagaria um manto que hoje
  funciona (é a que protege os 80 que valem);
- pasta de destino que não existe em GRF nem no disco — viraria caixa de erro.

**O override é refeito do zero a cada rodada**, e o arquivo do disco não é lido
para recuperar nada. A versão da manhã relia o próprio override para não perder
o que rodadas anteriores tinham posto — o que fazia sentido quando o script
*acrescentava* slot. Depois da reescrita isso só arrastava decisão velha: as 38
entradas acima de 120 da tentativa que não funcionou sobreviviam a cada rodada
sem que nada as pedisse.

### Três globais, não dois — e o terceiro é uma LISTA

| arquivo | global | forma |
|---|---|---|
| `spriterobeid.lub` | `SPRITE_ROBE_IDs` | `{const = view}` |
| `spriterobename.lub` | `RobeNameTable` | `{[SPRITE_ROBE_IDs.const] = "pasta"}` |
| | `RobeNameTable_Eng` | idem, a lista paralela em inglês |
| | `RobeTopLayer` | **vetor** de constantes |

`RobeNameTable` é quem dá o nome da **pasta** de sprite; nas entradas velhas
ela vem em coreano (CP949) e nas novas em ASCII. `RobeTopLayer` **não é mapa**:
é o vetor dos mantos que o cliente desenha **por cima** do personagem —
mochila, bolsa, asa que passa na frente. São 38 dos nossos 120, e 151 dos 258
do bRO.

**Reescrever o arquivo sem o `RobeTopLayer` compila, sobe e não dá erro
nenhum** — os 38 que hoje desenham na frente passariam a desenhar atrás,
calados. Por isso ele é preservado inteiro, na ordem original (vetor reordenado
é mudança de conteúdo), e um slot reaproveitado entra nele se, e só se, o bRO
puser lá o manto de origem. Dos nove de 2026-08-09, oito entraram; o único de
fora foi a Capa de Herói, que é capuz e desenha atrás.

Ler os três exigiu cortar o bytecode por `SETGLOBAL` — o `vv.tabela_lua`
devolve tudo numa lista só, e `RobeNameTable` e `_Eng` têm as **mesmas
chaves**: um `dict()` por cima colapsa uma na outra sem avisar. Foi essa a
armadilha que o `instala_manto.py` tinha desde 2026-08-08.

### O que sobrou de custo

Cada manto novo **queima um slot doador**, e eram 40. Nove foram usados; sobram
**31**. Passado isso, ou se faz o patch de exe, ou não entra manto novo — está
no `PENDENCIAS.md` §4.

## `varre_cosmeticos.py` — o que dá para vestir, e o que daria depois da cura

```
python varre_cosmeticos.py                    # resumo por slot
python varre_cosmeticos.py --listar curavel   # os que o bRO resolve
python varre_cosmeticos.py --listar sem-cura  # os que não há como salvar
python varre_cosmeticos.py --listar manto     # só os de Costume_Garment
python varre_cosmeticos.py --ids curavel      # os ids, prontos para o --id
```

Escrito em 2026-08-05 para montar o **Mercado de Visuais**
(`npc/guerra/mercado_de_visuais.txt`).

**A pergunta dele é diferente da do `valida_visual.py`**, e é essa diferença que
justifica a ferramenta existir. Aquele mede o estado de **agora**: o que o
cliente desenha hoje. Este mede o estado **possível**: o que desenharia depois
de rodar as três ferramentas de cura.

A diferença importa porque as camadas se encadeiam e nenhuma sozinha enxerga o
fim. Item sem entrada no `itemInfo.lua` nem tem `resourceName` para o validador
consultar — ele responde `não está no itemInfo.lua`, que **parece um veredito e
é só uma pergunta sem resposta**. Este script vai buscar o `resourceName` no
bRO, o sufixo de cabeça no `accessoryid.lub` do bRO, e só então pergunta pelos
arquivos, nos dois GRFs ao mesmo tempo.

Por isso `curavel` é uma **promessa verificável**: os oito arquivos existem em
algum dos dois lados. Quem cumpre é o `instala_visual.py`; quem confere se foi
cumprida é o `valida_visual.py`.

Estado em 2026-08-05, **depois** da cura dos três slots de cabeça:

| slot | ok | curável | sem cura |
|---|---|---|---|
| Costume topo | 1265 | 0 | 296 |
| Costume meio | 466 | 0 | 157 |
| Costume baixo | 543 | 0 | 169 |
| Costume manto | 107 | 45 | 193 |

Os 622 "sem cura" de cabeça são itens **mais novos que a instalação do bRO**
desta máquina: não há arte para eles em lugar nenhum ao nosso alcance.

### Manto é contado e não é prometido

`Costume_Garment` tem uma camada a mais, a `spriterobeid.lub`/`spriterobename.lub`
— e não existe ferramenta nossa para ela. Os mantos são classificados e
listáveis, mas **nunca saem como `curavel`**: prometer o que não há como
cumprir é o erro simétrico ao de 2026-08-01, quando se chamou de "sem cura" o
que só precisava de outra ferramenta. Ver `PENDENCIAS.md`, seção "EM ABERTO — o
manto cosmético".

### A guarda que a primeira rodada não tinha

`view_cabeca` é `None` para item que não é chapéu, e `None not in acc` é sempre
verdadeiro. Sem a guarda explícita, **todo manto e todo acessório caía em
`curavel`** — a primeira rodada relatou 152 mantos curáveis e nenhum `ok`, que
era o próprio erro se anunciando. Número redondo demais num lado e zero no
outro é sintoma, não resultado.

### O que ele acrescentou ao `valida_visual.py` (e o `varre_cartas.py` reusa)

O `le_item_db` passou a guardar o campo **`locais`** — o conjunto de
`Locations:` do item — em vez de só o booleano `cabeca`. A lista de nomes
aceitos é **fechada** (`LOCAIS`) de propósito: dentro do bloco de um item há
outros mapas com a mesma forma (`Flags:`, `Trade:`), e sem lista fechada um
`NoDrop: true` entraria como se fosse slot.

## `varre_cartas.py` — classifica as cartas e monta as nove lojas

```
python varre_cartas.py                    # resumo: os DOIS eixos, arte e nome
python varre_cartas.py --listar curavel   # o que o bRO resolve
python varre_cartas.py --listar ingles    # ou coreano, pt, ausente
python varre_cartas.py --listar mvp       # ou qualquer loja, pelo nome
python varre_cartas.py --ids sem-cura
python varre_cartas.py --gerar            # escreve o NPC e o catálogo
```

Irmã da `varre_cosmeticos.py`, escrita em 2026-08-05 para o **Mercado de
Cartas**. Reaproveita dela a parte que decide se o cliente desenha o item — a
pergunta de arte é a mesma. **O que ela tem de próprio é a classificação**, e é
aí que estão as três armadilhas.

### O eixo que decide a loja é o NOME, não a arte — e isso foi medido

A primeira versão filtrava só por arte e vendia **1410** cartas. Em jogo, a
lista da loja saía com nome em coreano e em inglês no meio das traduzidas.

A causa: **toda** carta do `itemInfo.lua` tem o mesmo `identifiedResourceName`
— a arte genérica de verso de carta, cujo nome em coreano quer dizer "carta sem
nome". Não é defeito da nossa tabela; o `iteminfo_new.lub` do bRO traz o mesmo
valor para todas. Logo os quatro arquivos que o `varre_cosmeticos.estado`
confere são **os mesmos quatro para todas**, e ele responde `ok` para as 1410
que têm entrada. **Arte não separa nada aqui.** O que separa é o nome:

| nome na lista da loja | quantas | entra? |
|---|---|---|
| português | 964 | sim |
| inglês — o bRO nunca implementou | 392 | não |
| coreano — nem o bRO traduziu | 54 | não |
| sem entrada no `itemInfo.lua` | 135 | não |

**A fonte do nome é o `itemInfo.lua` do cliente, não o `Name` do `item_db`.**
Mesma regra do `npcidentity.lub` para view id: manda o arquivo que o cliente lê.
Os dois divergem — 4209 é `Violy Card` no servidor e `Carta Violinista` na tela.

#### Inglês e coreano se detectam por caminhos diferentes, e um não serve para o outro

**Inglês** é ausência no `iteminfo_new.lub` do bRO. Os dois critérios possíveis
foram medidos um contra o outro antes de escolher, e **concordam nas 1545 sem
uma exceção**: das 392 cujo nome tem a palavra `Card`, nenhuma está no bRO; e
nenhuma das que estão no bRO deixa de ter nome em português. Ficou o primeiro,
que é fato sobre a tabela e não palpite sobre a forma da palavra.

**Coreano não pode ser isso**, porque as 54 coreanas *estão* no bRO — o bRO
simplesmente nunca as traduziu. Elas se detectam por byte, e aí mora a
pegadinha: o nome PT deste cliente está em cp1252 e **tem acento de propósito**.
`if byte >= 0x80: é coreano` acusaria `Carta Lunático` e tiraria da loja meia
tradução. O teste certo é byte alto **fora** do conjunto de acentos da fase
PT-BR — e esse conjunto precisa do `\xa0` (espaço não separável), que o bRO usa
em `Carta\xa0Violinista`. Foi o único falso positivo da medição.

#### O `Resource File Loading fail` das cartas não é sintoma de carta ruim

Ao abrir a arte de uma carta o chat mostra
`Resource File Loading fail` / `texture\<ui>\cardbmp\....bmp`. Como o
`resourceName` é o mesmo para todas, esse arquivo é o mesmo para todas — e ele
**não existe em GRF nenhum**, nem no nosso nem no do bRO. Ou seja, o erro sai
para **qualquer** carta, inclusive as traduzidas.

Limpar a loja não mexe nisso, e foi por pouco que não se concluiu o contrário:
o sintoma apareceu junto das cartas em inglês, e a hipótese natural era que
fosse delas. É frente separada — a pasta `cardbmp` dos dois GRFs guarda 985 e
948 imagens de carta com nome *próprio*, que nenhuma entrada de `itemInfo`
aponta.

### 1. `Type: Card` não quer dizer carta de monstro

São **5593** entradas, e **4048 delas não têm `Locations:` nenhum**: são as
**pedras de encanto**, que o mesmo tipo abriga. Delas, 1915 não têm arte em GRF
nenhum — iriam sujar o relatório com "sem cura" que não é problema de arte, e
sujar a loja com item que não encaixa em equipamento nenhum.

**O filtro é ter slot, não ser do tipo.** Sobram 1545 cartas de verdade, das
quais 1410 desenham — e dessas, 964 chegam à loja, pelo eixo do nome logo
abaixo.

### 2. Para carta, `Locations:` significa outra coisa

Não é onde a carta se equipa — é **em que equipamento ela pode ser encaixada**.
`Right_Hand` é carta de arma, `Left_Hand` é carta de escudo. A mesma chave que
num chapéu quer dizer "vai na cabeça" aqui quer dizer "encaixa em coisa de
cabeça".

### 3. MVP e chefe não existem no `item_db` — e há duas formas de marcar MVP

Saem do `mob_db`, por quem dropa (e o `mob_db` referencia o drop pelo
`AegisName`, nunca pelo id). O rAthena marca MVP de **duas** maneiras:

| marca | quantas cartas |
|---|---|
| `MvpExp:` | 91 |
| `Modes: Mvp: true` | mais 56 |

Ler só a primeira perde metade — a segunda é que traz **Dark Lord, Fenrir, os
chefes de Bio Lab e os de instância**. `Class: Boss` que não seja MVP é chefe
menor: Ghostring, Angeling, Mysteltainn. Dá 147 e 82.

**São exclusivos:** a Carta do Doppelganger saiu da loja de arma e ficou só na
de MVP. A alternativa era a mesma carta em duas lojas, que para o jogador parece
erro de catálogo.

### O teto do `w4` — hoje adormecido, e por isso mesmo vale registrar

O parser copia o quarto campo para um `char w4[2048]` e **trunca com aviso** em
vez de recusar (`npc.cpp`, `npc_parsesrcfile`) — o tipo de limite que não dá
erro, dá loja com metade dos itens.

Com as 1410 a lista de arma dava **2804** caracteres e estourava: 255 iam na
linha e 104 entravam por `npcshopadditem` num `OnInit`. **Depois do filtro de
nome ela dá 1682, e nenhuma das nove passa do teto** — o arquivo gerado hoje não
tem um `npcshopadditem` sequer.

A máquina fica no gerador. O corpo de um `script` não tem o limite (o
`npc_parse_script` procura o `,{` no **buffer original**, não no `w4`), e o
corte é **por tamanho, não por nome**: se uma loja voltar a crescer, o gerador
refaz isso sozinho, sem ninguém precisar lembrar.

### Preço

1 zeny, como os dois mercados de cima. Medido antes de escolher: a revenda
máxima entre as 5593 é **10 zeny** — toda carta do rAthena tem `Buy: 20` e
nenhuma declara `Sell`. São 9 de lucro por compra, a mesma ordem dos itens do
Mercado Contemporâneo.

Diferente do Mercado de Visuais, **este arquivo imprime o aviso**
`npc_parse_shop: Item X discounted buying price`, um por carta. É esperado, e é
o próprio servidor apontando esses 9 zeny.

## `zera_revenda_das_lojas.py` — fecha o dinheiro infinito das lojas de Prontera

```
python zera_revenda_das_lojas.py             # gera db/guerra/item_db_lojas.yml
python zera_revenda_das_lojas.py --conferir  # só relata; sai 1 se achar lucro
```

**O dinheiro infinito nunca esteve na vitrine — está na revenda.** As lojas de
Prontera vendem a 1 zeny; quem compra revende em **qualquer** NPC pelo `Sell`
do `item_db`, que vale `Buy/2` quando o item não declara o campo. A diferença é
lucro por clique, em laço, num servidor de drop 50x.

Medido em 2026-08-17, antes desta ferramenta existir: **918 dos 1603 itens** das
22 lojas davam lucro. Quase todos 9 zeny (carta de `Buy: 20`), e três não:

| id | item | vitrine | revenda |
|---|---|---|---|
| 19446 | Tapa-Olho Ferido (Ocleiro) | 1 z | **1.000.000 z** |
| 500009 | Cópia de Gram (Senhor das Armas) | 1 z | 250.000 z |
| 2204 | Óculos_ (Ocleiro) | 1 z | 2.000 z |

**O que ele escreve é um override com só o `Buy: 1`.** O `Sell` cai junto sem
ser escrito, e isso é consequência do leitor, não sorte: o
`ItemDatabase::parseBodyNode` guarda **por item** se o bloco trouxe `Buy` e se
trouxe `Sell` (`hasPriceValue[item->nameid] = { has_buy, has_sell };`), e essa
linha é uma **atribuição** — o último arquivo a falar do item vence. Como o
nosso é o último, o item fica com `has_buy` e sem `has_sell` ainda que o
`db/re/` tenha declarado `Sell` explícito, e no fim do carregamento o rAthena
faz `value_sell = value_buy / 2`, que dá **0**.

Escrever `Sell: 0` seria a mesma coisa com um campo a mais para divergir.

**Que lojas entram:** as três de vitrine a 1 zeny —
`mercado_contemporaneo.txt` (9 lojas), `mercado_de_cartas.txt` (9) e
`mercado_de_visuais.txt` (4). **A Tranqueiras fica de fora**, por decisão do
dono no mesmo dia: ela vende a `-1` (o `Buy` do item) e já tinha lucro **zero**
medido nos 55; `Buy: 1` nela derrubaria o Ouro (969) de 150.000 para 1 zeny e
daria a alquimia e as dez receitas de Runa de graça.

**Rodar depois de mexer em qualquer uma das 22 lojas.** Item novo posto numa
vitrine sem passar por aqui nasce com o `Buy` do `item_db` e reabre o buraco —
calado, porque a loja sobe, vende e o log não reclama. O `--conferir` compara
preço de vitrine com revenda loja a loja e diz se falta rodar; é ele a trava, e
não o comentário no cabeçalho da loja.

**O que isso alcança, e a decisão foi tomada sabendo:** toda cópia do item no
servidor, não só a que saiu da loja — valor de item mora no `item_db`, não na
instância. Carta que o jogador caçou também deixa de valer zeny no NPC.

Recarregar: `@reloaditemdb` em jogo, ou reiniciar o map-server. As linhas de
`shop` não mudam com isso — elas já estão todas a 1 zeny.

## `marca_indestrutiveis.py` — faz valer o "Indestrutível" que a descrição promete

```
python marca_indestrutiveis.py             # gera db/guerra/item_db_indestrutivel.yml
python marca_indestrutiveis.py --conferir  # só relata; sai 1 se achar divergência
```

**A descrição que o jogador lê e o efeito que o servidor aplica saem de lugares
diferentes**, e este é o desacordo que custa item: o `itemInfo.lua` do cliente
diz `^a400cdIndestrutível em batalha.^000000` e o `Script:` do `item_db` não traz
`bonus bUnbreakableWeapon;`. A peça quebra, e nada no log aponta para nada — é a
mesma família da Capa do Comandante (`CLAUDE.md` §5), com a diferença de que
aqui o jogador **perde o equipamento**.

Quem quebra é o `skill_break_equip` (`src/map/skill.cpp:1944`), chamado pelas
habilidades de monstro `NPC_ARMORBRAKE`, `NPC_HELMBRAKE`, `NPC_SHIELDBRAKE` e
`NPC_WEAPONBRAKER`. A primeira coisa que ele faz é
`where &= ~sd->bonus.unbreakable_equip` — **a trava existe e funciona, só não
estava ligada nesses itens.** E não há campo de `item_db` nem flag para
ligá-la: o `unbreakable_equip` só recebe bit por `bonus bUnbreakable<slot>`
rodando no `Script:` do próprio item (`src/map/pc.cpp:4262`).

Medido em 2026-08-18: **540 itens do nosso cliente dizem "Indestrutível" e 27
não tinham o bônus.** Sete estão à venda em Prontera:

| id | item | loja |
|---|---|---|
| 500009 | Lâmina Sagrada | Senhor das Armas |
| 28962 | Escudo Divino | Escudeiro |
| 460023 | Escudo da Fênix | Escudeiro |
| 15421 | Robe da Graça Divina | Mercado Contemporâneo |
| 480023 | Sobretudo do Mestre | Mercado Contemporâneo |
| 400396 | Chifres Oníricos | Mercado Contemporâneo |
| 400476 | Boina Sustenida | loja de troca (`barters_guerra.yml`) |

**O que ele escreve é um override que REPETE O SCRIPT INTEIRO** com uma linha a
mais. Repetir é obrigatório: o `parseBodyNode` **substitui** o `Script:` quando
o campo aparece, não acrescenta. E `EquipScript:` não serve — aquele roda uma
vez, no clique de equipar, e o `status_calc_pc_` refaz os bônus do zero sem ele.

**O bônus entra na primeira linha, não na última**, de propósito: script que
termine em `if (cond)` sem chaves engoliria a linha seguinte.

O slot sai do `Locations:`, nunca do nome (§4.14): `Type: Weapon` →
`bUnbreakableWeapon`, `Left_Hand` → `Shield`, `Armor` → `Armor`, `Head_*` →
`Helm`, `Garment` → `Garment`, `Shoes` → `Shoes`.

**Duas famílias ficam de fora, e o `--conferir` diz quantas:**

- **Machado, maça, cajado, livro e huuma** — 241 armas. O próprio
  `skill_break_equip` já as isenta por tipo, antes de sortear
  (`skill.cpp:1968`). Pô-las aqui congelaria o `Script:` de 241 armas do vendor
  por um efeito que já existe.
- **Equipamento sombrio** (`Type: Shadowgear`) — 4 itens (24152, 24153, 24154,
  24155). Não existe `bUnbreakableShadow`: o `unbreakable_equip` só tem bit
  para os seis slots acima. Eles caem no `EQP_SHADOW_GEAR`, que nenhuma
  habilidade de monstro pede — na prática não quebram, mas não há como travar
  por `db/` se um dia quebrarem.

**Esta ferramenta só roda no Windows**: a lista sai do `itemInfo.lua` do nosso
cliente, que está fora do git. O arquivo gerado é versionado e vale para as três
máquinas — o que não dá para fazer no Mac é regerá-lo.

**Rodar de novo** sempre que o `itemInfo.lua` ganhar item (`instala_item.py`) ou
o vendor do rAthena for atualizado. Enquanto este arquivo existir, correção do
rAthena no `Script:` desses 27 itens não chega ao jogo — o nosso vence.

Recarregar: `@reloaditemdb`, e só. Não precisa relogar nem trocar de mapa — o
`itemdb_reload` (`src/map/itemdb.cpp`) termina com um
`status_calc_pc(sd, SCO_FORCE)` por jogador online, e é ele que refaz os bônus.
Diferente do `Locations:`, que exige relogar (`CLAUDE.md` §5).

## `escala_drops_de_mapa.py` — põe o drop de mapa na taxa do servidor

```
python escala_drops_de_mapa.py             # gera db/guerra/map_drops.yml
python escala_drops_de_mapa.py --fator 50  # o padrão
python escala_drops_de_mapa.py --conferir  # só relata; sai 1 se divergir
```

**Equipamento ilusional não cai, e não é bug de script.** O pedido chega como
"o Congelador Ominoso deveria dropar a Espada Ilusional (13469) e não dropa" —
e ele realmente não dropa: a espada **não está** no `Drops:` do monstro em
`db/re/mob_db.yml`. Ela é **drop de mapa**, um banco separado
(`db/re/map_drops.yml`) indexado por mapa e processado no fim do `mob_dead`
(`src/map/mob.cpp:3372`).

**E drop de mapa não passa pela taxa do servidor.** O `mob_getdroprate` chamado
ali (`mob.cpp:3388`) só aplica bônus de LUK e de equipamento do jogador; os
nossos `item_rate_*: 5000` não alcançam campo nenhum daquele arquivo. O
cabeçalho do próprio `map_drops.yml` do rAthena diz isso numa linha em inglês:
*"These drops are unaffected by server drop rate and cannot be stolen."*

Medido em 2026-08-18, antes desta ferramenta existir — num servidor de 50x, o
ramo ilusional inteiro rodava a **1x**:

| item | `Rate` | chance | onde |
|---|---|---|---|
| Espada Ilusional (13469) | 25 | **0,025%** | Congelador Ominoso, 549.071 de HP |
| Pedra da Ilusão | 10 | **0,010%** | e a troca oficial pede **100** |
| Caixa da Ilha da Tartaruga | 5 | 0,005% | — |

Nada estava quebrado, e por isso nada aparecia no log: o sintoma é
indistinguível de azar.

**O que ele escreve** é um override que redeclara cada drop com a taxa
multiplicada pelo fator, com teto de 100000. A mescla é do rAthena e é por
**(Mapa, Monstro, Index)** — o `parseBodyNode` procura o mapa antes de criar e o
`parseDrop` procura o Index dentro do monstro. Campo não declarado fica como
estava, e é por isso que o arquivo **não** escreve `RandomOptionGroup`: as
opções aleatórias do vendor continuam valendo.

**O teto não é cortado, é recusado.** `Rate` acima de 100000 faz o `parseDrop`
devolver `false` e o `parseBodyNode` descartar o **mapa inteiro**
(`mob.cpp:7072`) — com os drops já lidos daquele mapa aplicados, ou seja um
override pela metade, calado. O `min()` mora no gerador por isso.

**117 dos 687 batem no teto e ficam em 100%**, todos de chefe (taxa base ≥ 2%).
Não é exagero da ferramenta: é o mesmo que já acontece com todo drop normal
deste servidor, onde `item_rate_equip: 5000` com `item_drop_equip_max: 10000`
já torna garantido qualquer drop de 2% ou mais.

**O `Item:` é escrito em cada linha ainda que o leitor não precise dele.** A
mescla é por `Index`; se o vendor reordenar os Index de um monstro numa
atualização, o nosso arquivo passaria a escrever a taxa de um item na linha de
outro — calado. O `--conferir` compara os pares e denuncia três coisas: taxa
fora do fator, `Index → Item` que mudou de lado no vendor, e drop que existe no
vendor e não aqui. **Rodar depois de atualizar o `rathena/`.**

Recarregar: **`@reloadmobdb`** — é ele que chama `mob_reload()`, que refaz o
`map_drop_db` (`mob.cpp:7216`). `@reloaditemdb` e `@reloadscript` não pegam.

## `gera_char_guerra.py` — a lista de letras que o nome de personagem aceita

Gera `rathena/conf/guerra/char_guerra.txt`, o arquivo que diz ao char-server
quais bytes podem aparecer num nome. Roda sem argumento:

```
C:\Python27\python.exe ferramentas\gera_char_guerra.py
```

Depois **reiniciar o char-server** — config só é lida na inicialização, e não há
comando de recarga para ela.

### Por que isto é um gerador e não um arquivo escrito à mão

Porque o arquivo tem de ser **cp1252** e o estrago de salvá-lo em UTF-8 é
calado. O filtro do rAthena compara byte a byte
(`strchr(char_name_letters, name[i])`, `char.cpp:1365`); em UTF-8 cada acento
vira **dois** bytes, e a lista passa a permitir as duas metades soltas de cada
acento em vez de permitir a letra. O resultado não é um erro: é uma lista que
aceita lixo e continua recusando `ã`.

O gerador escreve os acentuados por escape `\xNN`, então ele próprio é ASCII
puro — não existe editor capaz de estragá-lo sem que se veja. E confere o
resultado antes de sair: recusa `U+FFFD` no arquivo e relê em cp1252 exigindo
que as 48 letras tenham voltado.

### O que entra na lista

O ASCII de sempre (letras, dígitos e o espaço) mais 48 acentuadas: as cinco
vogais com crase, agudo, circunflexo, til e trema conforme o caso, mais `ç` e
`ñ`, em minúscula e maiúscula.

Só **letras**. Hífen e apóstrofo ficaram de fora de propósito — nome é chave em
comando de GM, em sussurro e na janela de troca.

### Ele sozinho não resolve

A outra metade é `conf/guerra/inter_guerra.txt` (`default_codepage: latin1`).
Sem ela o filtro deixa o nome passar e o **banco** o recusa, com
*"Incorrect string value"* — ver `CLAUDE.md` §5 e a seção de 2026-08-10 do
`HISTORICO.md`.

E a lista vale para mais do que o nome de personagem: clã
(`int_guild.cpp:1199`), grupo (`int_party.cpp:517`) e homúnculo
(`int_homun.cpp:302`) leem a **mesma** variável.

## `act.py` e `levanta_sprite_npc.py` — sprite de NPC que nasce enterrado

O `.spr` guarda os desenhos; o **`.act`** diz, para cada ação e cada quadro,
onde cada desenho é colado em relação à célula. O par que interessa é o
`(x, y)` de cada **camada** — o deslocamento do centro do desenho em relação ao
ponto de ancoragem no chão.

**Com `y` perto de zero o centro do sprite fica na altura do chão**, a metade de
baixo vai para debaixo do piso, o depth buffer do terreno a corta, e o NPC
aparece com um **corte reto e horizontal** na base. Parece defeito de célula, de
altura de mapa ou de modelo — e não é.

### Uso

```
python levanta_sprite_npc.py --ver <SPRITE>      # mede, não escreve
python levanta_sprite_npc.py <SPRITE> <y>        # aplica
```

O `--ver` avisa sozinho quando `y > -20`. Que valor usar: **`-(altura/2 - 8)`**,
que é a conta que os oficiais deste cliente seguem — o centro sobe meia altura e
a base afunda uns 8 pixels, para a peça parecer plantada e não flutuando.

| sprite | altura | `y` |
|---|---|---|
| `4_vending_machine` | 122 | −53 |
| `4_VENDING_MACHINE` | 122 | −53 |
| `2_DROP_MACHINE` | 118 | −44 |
| `2_VENDING_MACHINE1` | 114 | −40 |
| `2_COLAVEND` | 123 | **0** — a exceção, corrigida para −53 em 2026-08-12 |

### O que ele grava, e onde isso dói

Em `C:\GuerraDoEmperium\cliente\data\sprite\npc\<SPRITE>.act`, que é **cliente,
fora do git**, e vence o GRF pelo `DataFolderFirst`. **Cliente novo perde o
conserto** e a peça volta a afundar, sem erro nenhum. Esta ferramenta é a
receita versionada para repor; apagar o arquivo solto reverte, porque o original
nunca saiu do GRF. Override anterior vai para `backup-registro` antes de ser
sobrescrito.

Depois de rodar: **fechar e reabrir o cliente.** `@reloadscript` não alcança
sprite.

### Duas ressalvas do leitor

**O `.act` de vários sprites antigos está com DES no nosso `data.grf`** e não se
lê; nesses casos ele vem do GRF do bRO, que é a mesma revisão oficial. O `--ver`
diz de onde veio. Foi o caso do `2_COLAVEND`.

**O `act.py` recusa-se a devolver dados se sobrar byte** — a regra do
`mede_rsm.py`: formato com campo opcional por versão desalinha calado e devolve
números plausíveis. Há **4 bytes não identificados** entre o fim das ações e o
vetor de atrasos; sem pulá-los o vetor sai lido como `[0.0, 4.0 ×7]` em vez de
`[4.0 ×8]`. Ficam pulados e documentados.

O alinhamento dos `(x, y)` foi provado **por fora**, não pelo próprio leitor: no
`2_DROP_MACHINE` as oito camadas dão todas `(6, −44)`, e o padrão de bytes
correspondente aparece exatamente **oito** vezes no binário.

A escrita é **byte a byte no lugar** (`Act.desloca_y`), não re-serialização: só
os `y` mudam, o tamanho não mexe, e qualquer campo que o leitor não entenda
sobrevive. O `aplica` ainda relê o resultado e confere que só o `y` mudou.

## `simula_blackjack.py` — o viés das duas mesas do Cassino de Comodo

```
python simula_blackjack.py                 # as duas mesas como estão hoje
python simula_blackjack.py --varredura     # a tabela de viés, para calibrar
python simula_blackjack.py --maos 200000   # mais mãos, menos ruído
```

Acrescentado em 2026-08-12, com o cassino. As duas mesas de
`npc/guerra/cassino_de_comodo.txt` são **viciadas de propósito e em direções
opostas** — no primeiro andar o baralho ajuda o jogador, no segundo ajuda a
casa — e esta ferramenta é o que decide o quanto.

### Por que não dá para escolher o número a olho

O viés age nos **dois lados da mesa ao mesmo tempo**: favorecer o jogador é
melhorar a mão dele *e* piorar a do crupiê. O efeito é mais que o dobro do que
o número sugere, e a diferença é cara. Medido:

| viés a favor do jogador | lucro médio dele |
|---|---|
| 0% | −5,4% (o jogo honesto já é da casa) |
| 5% | **+6,4%** |
| 10% | +18,1% — faucet de moeda |

**10% parece pouco e é faucet.** Foi por isso que a ferramenta nasceu antes do
script, e não depois.

### O que está em jogo hoje

| | aposta | 21 natural | viés | ganha | perde | lucro médio |
|---|---|---|---|---|---|---|
| 1º andar | 2 | 3:2 | 5% pró-jogador | 46,7% | 44,1% | +0,13 moeda/mão |
| 2º andar | 10 | 2:1 | 10% pró-casa | 32,3% | 58,9% | −2,31 moeda/mão |

A isca é o próprio pagamento: em cima o 21 natural paga **mais** (2:1 contra
3:2) e a aposta é cinco vezes maior — e a mesa drena dezoito vezes mais rápido
do que a de baixo enche.

### As três estratégias, e por que são três

O lucro depende de como o jogador joga, então mede-se `pede até 17` (a que
quase todo mundo joga), `para sempre` e `pede até 12`. A do meio não é
curiosidade: é o **contra-jogo**. Um jogador que desconfia da mesa de cima e
para de comprar precisa continuar perdendo, senão a falcatrua tem saída. Ela
continua — **−34,5% contra os −23,1%** de quem joga normal, porque metade do
viés age na mão do *crupiê*, onde a estratégia do jogador não alcança.

Na mesa de baixo vale o contrário, e também por escolha: parar sempre dá
−5,8%, então a mesa boa só paga para quem realmente joga.

### É um espelho, e espelho quebra calado

O arquivo reimplementa o `S_Compra` do NPC linha a linha — baralho de 52 sem
reposição, sorteio por **valor** (o naipe só enfeita a tela), Ás que cai de 11
para 1, "melhor carta" = maior total ≤ 21, "pior" = uma que estoure, crupiê que
para em todo 17.

**Mexeu no `S_Compra`, mexe aqui.** Se o script mudar e a ferramenta não, ela
passa a medir um jogo que não existe — e responde com a mesma cara de certeza.
É a mesma família do `ajusta_tamanho_fonte.py`, que confirmava o próprio
trabalho e era inócuo.

A semente é fixa por estratégia (`random.seed(20260812)`), então as três veem o
**mesmo baralho** e a diferença entre elas é a estratégia, não o ruído.

## `ordena_bandeiras_ctrl.py` — qual bandeira cada CTRL+`<n>` solta

```
python ordena_bandeiras_ctrl.py --verificar   # só relata, não grava
python ordena_bandeiras_ctrl.py               # aplica (faz backup antes)
```

Pedido de 2026-08-12: *"CTRL+1 tem que ser bandeira do Brasil"*. Estava em
CTRL+6, e o CTRL+1 dava a da Coreia.

**O primeiro lugar onde se procura é o errado**, e é o que justifica esta
seção. O `data\luafiles514\lua files\emotion\emotionlist.lub` define o `enum`
inteiro das emoções — `ET_FLAG` 13, `ET_BR_FLAG` 51 e as outras sete — e ainda
um `EMOTION_ORDERLIST`, o que o faz parecer a lista a reordenar. **Não é:**
aquela lista tem 64 entradas e nenhuma bandeira. Ela é a ordem da *janela* de
emoções, e bandeira não aparece na janela.

Quem trata a tecla é o **exe**, num `switch` de nove casos:

```
0x00638950  mov  ecx, [00F3D1D4]        ; o objeto que envia a emocao
            test ecx, ecx / jz fim
            mov  eax, [ebp+8]           ; a tecla
            add  eax, -0D2h             ; 210 -> caso 0
            cmp  eax, 8 / ja fim
            jmp  [eax*4 + 00638B1Ch]    ; a tabela de saltos
```

e **cada caso é uma cadeia de comparações contra o `<servicetype>` do
`clientinfo.xml`** (o global `[012BF51C]`: `korea`=0 … `brazil`=12, na ordem em
que os nomes estão no `.rdata`) antes de chegar ao trecho que de fato empurra a
emoção — `8B 01`, cinco `push`, `FF 50 18`. Ou seja a mesma tecla dá bandeiras
diferentes conforme o servicetype, e na maioria deles não dá nenhuma: com
`korea` as nove funcionam, com `brazil` só o CTRL+1, com `america`/`japan`/
`thai` nenhuma.

**O que a ferramenta faz:** reescreve as nove entradas da tabela de saltos para
apontarem direto nesses trechos, pulando a cadeia de servicetype inteira. São
36 bytes, todos de dados. É seguro porque o trecho só precisa do `ecx`, que o
prólogo carrega **antes** do salto — não há nada na cadeia pulada além das
comparações. Duas consequências, as duas boas: a ordem passa a ser a da tabela
`ORDEM` no topo do arquivo, e as nove teclas funcionam em qualquer servicetype.

A ordem entregue é a de `korea` com Brasil e Coreia **trocados** — CTRL+1
Brasil, CTRL+6 Coreia, o resto onde estava. Trocar em vez de empurrar a fila foi
escolha: quem já decorou CTRL+3 continua com Filipinas. Mudar isso é reordenar
a lista `ORDEM`.

**Nada é procurado por endereço fixo.** A tabela é achada pelo padrão do prólogo
e os nove trechos pelo padrão dos `push`; os endereços acima são documentação.
Se o exe for repatchado ou trocado, a ferramenta reacha — e recusa (`Exception`)
se não achar exatamente um `switch` ou se faltar algum trecho.

Dois cuidados que valem para todo patch de exe daqui:

- **Fechar o cliente ANTES.** O exe fica travado enquanto roda, e o que já está
  aberto segue na cópia em memória.
- **`--verificar` dizendo "aplicado" não é prova de efeito.** Ver
  `CLAUDE.md` §5, "Tamanho da fonte": script que confere o próprio trabalho não
  prova nada. Quem prova é apertar CTRL+1 no jogo.

O backup vai para `GuerraDoEmperium.exe.BACKUP-bandeiras-AAAAMMDD-HHMM`, e a
gravação recusa qualquer coisa que mude o tamanho do arquivo.

## `aponta_cliente.py` — para onde o cliente desta máquina aponta

```
python aponta_cliente.py                # só relata, não grava
python aponta_cliente.py --dev          # 127.0.0.1 (o servidor desta máquina)
python aponta_cliente.py --producao     # o servidor de verdade
```

O cliente de `C:\GuerraDoEmperium\cliente` é o de **DEV/HML** desde 2026-08-16;
produção se testa noutra pasta, instalada pelo instalador como um jogador faria
(`CLAUDE.md` §1). Este script existe porque manter esse combinado à mão já
falhou duas vezes.

**São dois arquivos e dois campos, e cada par tem uma armadilha própria.** Os
dois xml são `data\clientinfo.xml` e `data\sclientinfo.xml`, e **quem vale é o
segundo** — este exe é `<servertype>sakray</servertype>`, e trocar só o primeiro
deixa o cliente indo para o lugar antigo (uma hora perdida em 2026-08-14). Os
dois campos são o `<address>` e o `<admin>`: o `group_id 99` do banco dá os
*comandos*, mas quem dá o **visual** de GM é a lista dentro do cliente — 2000000
aqui (`teste`), 2000004 lá (`librasupremo`), que nem existe neste banco. Trocar
só o endereço deixa o GM sem visual do outro lado, e foi o que custou o patch
0004.

**O que desaponta o cliente sozinho é o Atualizador.** Há um `Jogar.exe` dentro
da pasta de dev, e o patch 0004 leva os dois `clientinfo` com o endereço de
produção: rodá-lo ali reaponta tudo, sem perguntar. O `monta_patch.py` protege a
*saída* (`confere_apontamento` recusa publicar cliente apontado para local);
nada protegia a *entrada*, e a falha é calada da pior maneira — o jogo abre,
loga e joga, só que no servidor errado. Para jogar no local, abrir pelo
`GuerraDoEmperium.exe`.

**Os backups são dos dois lados**, e não eram: até 2026-08-18 só existia
`.BACKUP-138.197.155.31`, então quando o lado de dev foi sobrescrito não havia
de onde restaurar. O script grava o lado de onde saiu **antes** de trocar. Os
dois pacotadores ignoram nome com `BACKUP` (o `LIXO` deles), então esses
arquivos não vão para patch nem para a base.

Conferido em 2026-08-18: a ida e a volta são idênticas byte a byte, e o
`--producao` reproduz exatamente o backup de produção de 2026-08-17.

## `monta_patch.py` — o zip que leva a mudança do cliente até o jogador

```
python monta_patch.py --nome "IA do homunculo" AI_sakray data/sclientinfo.xml
python monta_patch.py --nome "Arte nova" --desde 2026-08-14
python monta_patch.py --lista      # o que já foi montado
python monta_patch.py --confere    # o registro contra os .zip desta máquina
```

Monta `C:\GuerraDoEmperium\patches\NNNN-apelido.zip` com os arquivos indicados,
**relativos à raiz do cliente**, e acrescenta a linha em `patcher/patches.txt` —
que é o registro versionado e, sem tradução nenhuma, a `lista.txt` que o
servidor serve. Publicar é outro passo (`publica_patch.sh`).

**O `--desde` é a via preguiçosa e a mais perigosa.** Ele varre o cliente por
data de modificação e traz junto o que foi tocado por acidente; a lista impressa
antes de gravar existe para isso ser visto.

**Filtra o lixo que as próprias ferramentas deixam** — `*BACKUP*`, `.ORIGINAL`,
`.INGLES`, `.KOREA`. São 65 arquivos e 711 MB no cliente desta máquina, 28 deles
cópias de 22 MB do `itemInfo.lua`: sem o filtro, um `--desde` manda tudo isso
para o jogador.

**E pula a pasta `savedata\` inteira**, que é outra coisa: aquilo não é lixo
nosso, é **estado do jogador** — teclas (`UserKeys_s.lua`), opções de vídeo,
layout da janela de conversa —, e o cliente reescreve tudo isso toda vez que
fecha. Mandar em patch sobrescreve a configuração de **todo** jogador com a
desta máquina, e o sintoma para ele é *"minhas teclas mudaram sozinhas"*, sem
nada no jogo apontando para um patch.

> São **duas** listas porque são duas perguntas: `LIXO` olha o **nome** do
> arquivo, `PASTAS_FORA` olha o **caminho**. `OptionInfo.lua` não tem marca
> nenhuma no nome, então só a segunda o pega. Apareceu em 2026-08-28, quando um
> `--desde` do dia trouxe quatro arquivos de `savedata` junto com a arte do
> Pincel do Infinito — só porque o cliente tinha sido aberto para testar o item.

**Recusa o `Jogar.exe`**, que tem canal próprio pelo motivo do
`patcher/LEIAME.md` §3.

**E recusa `clientinfo.xml`/`sclientinfo.xml` apontados para a máquina local**
(`127.0.0.1`, `localhost`, `0.0.0.0`, vazio). Desde 2026-08-16 o cliente desta
máquina é o de dev e aponta para o servidor local: um patch com esse arquivo
dentro **tira do ar todo jogador que já tem o cliente**, e o sintoma que chega é
só "não consigo entrar". A conferência só roda quando um dos dois xml está no
patch — patch que não os inclui passa direto.

Duas armadilhas do Python 2 que ele resolve e que valem para qualquer
ferramenta que ande pela pasta do cliente:

- **os caminhos nascem `unicode`.** A `AI_sakray\` tem arquivo de nome coreano;
  com caminho `str` o `os.walk` usa a API ANSI, devolve `????` e o primeiro
  `os.stat` estoura com *"A sintaxe do nome do arquivo está incorreta"* — erro
  que parece do arquivo e é do leitor.
- **e o `print` também quebra.** Nome que o console não representa derruba a
  ferramenta com `UnicodeEncodeError` **depois** de o zip já estar escrito. A
  saída passa por um `codecs.getwriter(..., 'replace')` no topo do arquivo.

## `publica_patch.sh` — põe os patches no ar

```
ferramentas/publica_patch.sh                # os patches que faltam
ferramentas/publica_patch.sh --atualizador  # o Jogar.exe novo
ferramentas/publica_patch.sh --confere      # o placar, local e remoto
```

**Roda no Windows**, e não no Mac: os zips saem de `C:\GuerraDoEmperium\cliente`,
que só existe aqui. Precisa de acesso SSH ao servidor (`SERVIDOR=libraro`).

**O zip sobe antes da lista**, sempre — na ordem inversa, quem abrisse o
Atualizador no intervalo pediria um arquivo que ainda não existe. E **zip antigo
não se apaga do servidor**: quem instalou o cliente ontem ainda vai baixar o
patch 0001 amanhã.

Confere o sha256 de cada zip contra o registro antes de enviar. Divergência aí é
zip remontado com o mesmo nome e conteúdo diferente — o jeito silencioso de o
Atualizador do jogador recusar tudo depois.

## `monta_cliente.py` — empacota o PRIMEIRO download

```
python ferramentas/monta_cliente.py            # monta tudo, do zero
python ferramentas/monta_cliente.py --lista    # o que já foi montado
python ferramentas/monta_cliente.py --confere  # o registro descreve o que há em disco?
python ferramentas/monta_cliente.py --so nosso # remonta só um grupo
```

O irmão do `monta_patch.py`, e a diferença é o público: o patch fala com quem
já tem o cliente, este fala com quem não tem nada. Escreve `patcher/base.txt`
(versionado) e os pedaços em `C:\GuerraDoEmperium\instalador\`.

Quatro grupos, na ordem em que o jogador os vê descer: **o mundo** (o
`data.grf`), **as músicas**, **a Guerra do Emperium** (tudo que é nosso) e **o
motor do jogo** (o que sobrou). O último é definido por exclusão de propósito —
arquivo novo na raiz do cliente entra sozinho, em vez de ser esquecido calado.

**O `data.grf` não vira zip.** São 2,95 GB num arquivo só: não há como fatiá-lo
por arquivo, zipá-lo não ganha nada (já é comprimido) e custaria o dobro de
disco no jogador. Ele entra no registro como tipo `bruto` e é publicado **direto
de `cliente\`**, sem cópia — daí o registro ter seis campos e não cinco.

O que **não** entra: `savedata\`, `patch\`, `Emblem\`, `_tmpEmblem\`,
`ScreenShot\`, `Replay\`, `memo\` (estado local, nasce sozinho), `_extras\` (os
exes originais, material nosso) e o próprio `Jogar.exe`/`.ini` — o jogador já os
tem na mão, e um exe não se sobrescreve rodando.

Números de 2026-08-16: **19.866 arquivos empacotados de 19.904**, 4,07 GB
brutos, **3.499 MB para o jogador baixar**. A nossa parte comprime a 17% (765,6
→ 134,4 MB), o que faz refazer só ela custar 134 MB.

**Antes de qualquer sha256 ele confere o apontamento** e para se um dos dois
`clientinfo` estiver em `127.0.0.1` — desde 2026-08-16 esta máquina é dev, e um
pacote montado assim manda todo jogador novo logar na própria máquina: 3,4 GB
corretos, sha fechando, ninguém entra. `--permite-local` passa por cima, para
quando for de propósito.

## `publica_cliente.sh` — põe a base no ar

```
ferramentas/publica_cliente.sh            # sobe o que falta
ferramentas/publica_cliente.sh --confere  # o placar, local e no bucket
ferramentas/publica_cliente.sh --tudo     # reenvia tudo
```

Destino é o bucket `ftn` da DigitalOcean Spaces, servido por
`cdn.filiponegrao.com.br`. Usa o `rclone` (`C:\GuerraDoEmperium\bin\`) e lê a
chave de `C:\GuerraDoEmperium\spaces.env`, **fora do git**.

**Os pedaços sobem antes da `base.txt`**, pela mesma razão do publicador de
patch. Confere o sha de cada um antes de enviar — no `data.grf` isso lê 2,95 GB
e leva algumas dezenas de segundos, e vale: é o que separa "o registro está
certo" de "o registro descreve o que vai subir".

O rclone é configurado por **variável de ambiente**, não por `rclone.conf`: um
arquivo de config guardaria a chave secreta num segundo lugar, fora do alcance
do `.gitignore` e da nossa atenção. Assim o segredo vive num lugar só e some
quando o processo morre.

Duas armadilhas que custaram rodadas e estão no `CLAUDE.md` §5: **chave do
Spaces só-leitura** (lista bem, não escreve) e o **`CreateBucket` do rclone**
(daí o `NO_CHECK_BUCKET`).

## `tinge_dimensao.py` — o céu roxo da Anomalia Dimensional

```
python tinge_dimensao.py                        # a luz de hoje + a escala inteira
python tinge_dimensao.py --aplicar              # grava o override (intensidade 6)
python tinge_dimensao.py --aplicar --intensidade 4
python tinge_dimensao.py --reverter             # apaga o override
```

Troca a cor da luz da **`pprontera`**, o mapa onde a Anomalia Dimensional
acontece (`npc/guerra/anomalia_dimensional.txt`), para que ela pareça uma
dimensão corrompida em vez da Prontera de sempre.

**Por que existe:** no bRO o evento roda numa cópia corrompida da cidade.
Aqueles mapas são de 2024 e não existem no nosso cliente de 2021-11-03, então o
evento usa a `pprontera` — uma cópia *limpa* de Prontera que já mora no GRF.
Esta ferramenta é o que faz a cópia parecer outra coisa.

**O que ele mexe são 24 bytes.** O `.rsw` guarda a luz do mapa em dois trios de
float: a **difusa** (a luz direta) e o **ambiente** (a cor da sombra). Eles
multiplicam tudo que é desenhado ali, então o mapa inteiro muda de clima sem
uma textura nova, sem um modelo novo e sem tocar o `.gnd` — que tem 3,3 MB e
pesaria no patch. O arquivo gravado tem **o mesmo tamanho** do original; o
script confere isso e aborta se mudar.

**Calibrar é UM número, não seis floats.** O `--intensidade` vai de 0 a 10 e
mistura a luz de fábrica com o alvo: 0 devolve a Prontera normal, 10 entrega o
alvo puro. Rodar sem argumento imprime a escala inteira, para escolher olhando.
O padrão é **6**, calibrado em jogo em 2026-08-26.

**Quem manda no matiz é a posição relativa de VERDE e AZUL** — e essa é a única
coisa que se precisa lembrar aqui. `B > G` puxa para o roxo/rosa; `B < G` puxa
para o laranja; a distância entre os dois diz o quanto disso aparece. O vermelho
fica intacto nos dois casos.

Custou três idas ao jogo para chegar nisso:

| tentativa | difusa | G − B | em tela |
|---|---|---|---|
| 1ª | 1,000 / 0,550 / 0,800 | −0,250 | magenta, rosa-choque |
| 2ª (alvo laranja, 3/10) | 1,000 / 0,916 / 0,835 | +0,081 | laranja limpo, suave demais |
| 3ª (alvo roxo, 4/10) | 1,000 / 0,832 / 0,896 | −0,064 | roxo avermelhado, aprovado |
| **atual (6/10)** | 1,000 / 0,748 / 0,844 | −0,096 | o mesmo tom, mais forte |

Note que subir a intensidade **não muda o matiz** — só a distância até a luz de
fábrica. Foi para isso que a escala existe: a cor nunca "vira outra coisa" no
meio da calibragem.

**Onde ele grava, e por que isso importa:** em `cliente\data\pprontera.rsw`, que
vence o GRF pelo `DataFolderFirst`. Ou seja, é **mudança de cliente** — não vai
ao jogador pelo `implanta.sh`, precisa de patch (`CLAUDE.md` §4.18,
`RECEITAS.md` §11). Quem não receber o patch joga a Anomalia inteira, sem erro
nenhum, numa Prontera de cor normal: a falha é calada e só cosmética.

**O original nunca sai do GRF**, então `--reverter` é só apagar o arquivo — não
há backup a manter. É a mesma lógica do `destroi_mapa.py`.

**Duas travas antes de gravar:** o `rsw.verificar()` (ler e reescrever sem mexer
tem de devolver os bytes originais — sem isso não há como saber se o layout está
certo, e layout errado não dá erro, dá arquivo corrompido) e uma releitura do
resultado conferindo que os seis floats gravaram o que foi pedido.

**O cliente só relê o mapa ao entrar nele.** Se você já estiver na `pprontera`,
sair e voltar — ou reabrir o cliente.

## `planta_brilho.py` — um emissor de partículas numa célula de mapa

```
python planta_brilho.py              # o que há no mapa hoje, e onde o nosso iria
python planta_brilho.py --aplicar    # gera e instala o override
python planta_brilho.py --sonda      # diagnóstico: ver se o cliente LÊ o arquivo
python planta_brilho.py --reverter   # apaga o override
```

**O `--sonda` é a marca que não depende do efeito procurado** (`CLAUDE.md` §5):
em vez de acrescentar um emissor, ele troca a textura das **três fumaças que já
aparecem**, sem mexer em mais nada. Se as chaminés de Prontera passarem a soltar
o brilho, o arquivo está sendo lido e o problema é do nosso emissor; se
continuarem soltando fumaça, o cliente não lê este arquivo — e nenhum ajuste de
tamanho ou cor vai resolver.

Põe um brilho no chão sob o **Sábio Varmunt** (`prontera 156,303`), com a
textura `effect\mineffect\new_epiclesis\epi_glow_01.bmp` — a mesma arte que o
Epiclesis usa.

**Por que não é `specialeffect`:** o brilho de Epiclesis não é um efeito
numerado do cliente, é uma **unidade de habilidade** (`UNT_EPICLESIS`), que só
existe enquanto a magia está no chão. Não há constante `EF_` para ele no
rAthena e não há como pedi-lo por script. O que existe — e é melhor — é o
sistema de **emissores de partículas por mapa** do cliente, em
`data\luafiles514\lua files\effecttool\<mapa>.lub`, que aceita **o caminho da
textura direto**. É o mesmo mecanismo que faz a fumaça sair das chaminés de
Prontera (três emissores com `effect\smoke1.bmp`, que a ferramenta preserva).

**A conversão de célula para mundo**, que é a parte que erra calado:

```
mundo_x = (célula_x + 0,5 − largura/2)   × 5
mundo_z = (célula_y + 0,5 − altura_mapa/2) × 5
mundo_y = −altura_do_terreno    (o eixo Y é negativo para cima)
```

Os dois primeiros **não são chute**: saem do único caso do projeto já conferido
em tela pelo dono — a fonte do Centro da Ordem, em `auction_01` (200×100),
documentada no cabeçalho do `edita_mapa.py` como *"centro na fronteira entre a
179 e a 180: mundo (400, 110)"*. Conferindo: `180×5 − 500 = 400` e
`72×5 − 250 = 110`. E **o Z não é invertido** — cresce junto com o y de célula.
A altura sai do `.gat`, com o sinal trocado.

**O arquivo do GRF é bytecode Lua 5.1**, mas o que a ferramenta grava é **texto
Lua** — e é de propósito. O cliente aceita os dois, e o texto é o formato que
este projeto já usa e comprovou: o `OngoingQuestInfoList.lub`, o
`CheckAttendance.lub` e os `.lub` de `data\` gerados pelo `traduz_ptbr.py` são
todos texto puro (começam com `--`) e são lidos. A primeira versão desta
ferramenta compilava com `luac -s`, e o resultado não apareceu em tela; não
ficou provado que o bytecode era a causa, mas ele era a única peça do caminho
**sem precedente no projeto**, e trocar por texto custa nada e elimina a dúvida.

O arquivo tem só duas globais, sem nenhuma função, o que torna a regeração
segura. A conferência do fim **compila o que foi gravado para um bytecode
temporário e o lê com o mesmo parser que lê os `.lub` do GRF** — conferir texto
por regex provaria só que a string está lá, não que o Lua entende o arquivo.

**E o emissor novo HERDA de um que já funciona.** A primeira versão inventou os
quinze campos do zero; esta parte de um dos emissores de fumaça das chaminés e
troca só o que precisa mudar (textura, posição, gravidade, tamanho, cor, vida).
Os campos de desenho — `srcmode`, `destmode`, `zenable`, `speed` — são modos de
blending do Direct3D, não há como conferir o valor certo offline, e o que se
sabe é que **aqueles** desenham neste cliente. É a regra de mesclar por chave
em vez de escrever por cima (§4.5).

**Ele lê a base sempre do GRF, nunca do override** — reler o próprio arquivo
gerado faria a receita apontar para si mesma, e uma rodada ruim viraria a fonte
da seguinte (a armadilha do `arte_de` do `instala_item.py`).

**É cliente: vai por PATCH, não por deploy** (`CLAUDE.md` §4.18). E o cliente só
relê o mapa ao entrar nele — sair e voltar a Prontera.

**O que ainda não foi conferido em tela** são os números do emissor (`size`,
`color`, `rate`, `life`, `maxcount`): foram escolhidos para um halo parado — sem
gravidade, sem velocidade, mistura aditiva — em vez de uma fumaça, mas só o jogo
diz se o tamanho e o brilho estão bons. Todos estão em `_emissor_nosso()`, num
lugar só.

---

## `lista_efeitos_do_cliente.py` — que número desenha aquela textura

```
python lista_efeitos_do_cliente.py                    # resumo + grava a lista
python lista_efeitos_do_cliente.py --id 1642          # o que é o efeito 1642
python lista_efeitos_do_cliente.py --textura castaura # quem desenha essa .bmp
python lista_efeitos_do_cliente.py --conferir         # a prova de calibragem
```

**Existe por causa de uma pergunta errada.** Pedido de brilho chega pelo nome de
um `.bmp`, e o reflexo é procurar onde enfiar aquele caminho — o que leva ao
`effecttool` e ao `planta_brilho.py`, que custou quatro idas ao jogo sem
desenhar nada. A pergunta certa é **"que número de efeito já desenha esta
textura?"**, e na maioria das vezes existe um: aí o pedido inteiro vira uma
linha de script no servidor, sem patch de cliente e sem override de pasta
nenhuma.

**O sinal de que existe número é um `.str` na mesma pasta da textura, no GRF.**
`.str` é definição de efeito numerado. Textura sem `.str` por perto — o
`epi_glow_01.bmp` do Epiclesis, que é unidade de habilidade — não tem, e para
essa o `effecttool` é mesmo o único caminho.

### O teto do rAthena não é o do cliente

`specialeffect` para no `EF_MAX` do emulador, **1243**. Este cliente conhece
efeitos até **2372**, e **941 deles têm `.str` acima daquele teto**. Para
alcançá-los há o **`efeitoespecial`**, nosso, em `src/custom/script.inc` — mesmo
comando, faixa do cliente.

### De onde sai a numeração

Do próprio exe. Um `switch` de tabela direta, em `GuerraDoEmperium.exe` no
offset de arquivo `0x006b6ce4`:

```
lea eax, [ebx-13]                  ; ebx = numero do efeito
cmp eax, 0x937                     ; 2359
ja  <default: nao desenha nada>
jmp dword [eax*4 + 0x00ABFEE0]     ; tabela de 2360 entradas
```

ou seja `número = 13 + índice`, faixa 13..2372. Cada `case` empilha o caminho de
um `.str`; quando há dois, são as variantes `mineffect\` e normal, escolhidas em
tempo de execução por `cmp [0x011d189c], 1`.

### `--conferir` é o que torna isso confiável

Ler a instrução seria aceitar uma medição só. O `--conferir` cruza os efeitos
resolvidos com o enum `e_special_effects` do próprio rAthena, pelo nome do
arquivo, e testa **todos** os deslocamentos de 0 a 26:

| deslocamento | acertos |
|---|---|
| **13** | **25**, de `EF_STORMGUST` (89) a `EF_FULLMOON_KICK` (1230) |
| todos os outros | **zero** |

Pico único, e os acertos vão de ponta a ponta da faixa que o rAthena nomeia —
não há deriva nos ids altos, que é justamente onde moram os efeitos que só o
cliente conhece. **Sai 1 se o pico deixar de ser o 13**, o que quer dizer
cliente novo e endereços a remedir.

### Duas armadilhas que ele existe para evitar

- **Número fora da faixa não desenha nada e não avisa** — cai no `default` do
  switch, sem erro de Lua, sem caixa, sem log. Errar o número é indistinguível
  de "o efeito não existe".
- **As duas variantes usam texturas diferentes.** O efeito 1642 desenha
  `sound_castaura_0..9.bmp` com efeitos reduzidos e `sou_cast_00..09.bmp` com
  efeitos normais. Uma `.bmp` pedida pode existir só de um lado, e aí ela só
  aparece com aquela opção ligada. O `--id` mostra os dois lados, com a duração
  de cada um — que é o número que decide o intervalo do laço.

**Isto é leitura do cliente, mas o resultado é servidor:** o brilho entregue com
ele é uma linha de script e vai por **deploy**, não por patch.

## `remove_placas_mortas.py` — tira placa do cliente que anuncia coisa que não existe

```
python remove_placas_mortas.py            # regera o override
python remove_placas_mortas.py --conferir # não grava; sai 1 se o disco divergir
```

### O que é uma placa

O `data\luafiles514\lua files\signboardlist.lub` é uma tabela de **514
entradas** que o **cliente** desenha sozinho, por mapa e célula, sem o servidor
participar: um ícone em moldura laranja mais uma placa marrom com um texto. Não
há NPC por trás — a placa fica boiando sobre a célula, e clicar nela não faz
nada.

Cada entrada tem 6 ou 8 campos, e os nomes saem do `signboardlist_f.lub`:

```
{ MAPNAME, CELLX, CELLY, HEIGHT, ICONID, FILEPATH [, CONTENTS, CHARCOLOR] }
```

O `ICONID` é uma das quatro globais que o próprio arquivo define no topo
(`IT_NONE`, `IT_BMP`, `IT_SPRITE`, `IT_SIGNBOARD`). **107 das 514 têm texto**, e
boa parte dele continua em coreano — o `traduz_ptbr.py` nunca tocou este
arquivo.

### O que ela tira hoje

As três da *Ragnarok Booster Promotion* de 2021, campanha paga de pré-venda do
kRO que aqui nunca existiu:

| mapa | célula | texto |
|---|---|---|
| `prontera` | 166,300 | 부스터 프로모션 |
| `sp_cor` | 98,136 | 부스터일루시온인챈트 |
| `malangdo` | 152,136 | 부스터 의상 인챈트 |

A de Prontera foi a que apareceu: o `itemInfo` ainda traz a Moeda Booster com um
`<NAVI>...<INFO>prontera,166,300,...</INFO>`, que era onde ficava o NPC de
troca. Sobrou a placa sobre chão vazio.

**As outras dezenove placas de Prontera são legítimas** — as quatro de salão de
clã, o `등급강화소` e o teleportador da Ordem (`낙원단 공간이동사`, 124,76).
Apagar o arquivo inteiro levaria todas junto.

### Por que regerar a tabela, e não usar o `SignBoardIgnore`

O `signboardlist_f.lub` que o ROenglishRE já deixou em `cliente\data\` tem um
`SignBoardIgnore` feito exatamente para isto — três linhas em
`SystemEN\Sign_Data.lub` e pronto. **Não é o caminho escolhido**, porque ele
depende de uma corrente que não está provada neste cliente: o `_f` do override
precisa vencer o que está no GRF, e o `require('SystemEN/LuaFiles514/rotp_f')`
do topo dele precisa achar um arquivo que existe como **`.lua`** e não como
`.lub`. Se qualquer um dos dois falhar, o cliente cai no `_f` do GRF — que não
conhece `SignBoardIgnore` — e a placa continua na tela, **calada**.

Tirar a entrada da própria tabela não depende de nada disso: seja qual for o
`_f` que rodar, ele indexa `SignBoardList[idx]`, e o que não está lá não é
desenhado.

### O que ela grava, e por que é texto

**Texto Lua, não bytecode.** O do GRF é bytecode (`\x1bLuaQ`), mas o cliente
aceita os dois, e texto é o formato que este projeto já comprovou — mesma
decisão do `planta_brilho.py`, algumas seções acima. E **cp949**: os 511 textos
que ficam são coreanos, e gravar UTF-8 os destruiria sem aviso (§4.1).

**A base vem sempre do GRF**, nunca do override que ela mesma grava — reler o
próprio arquivo gerado faria a receita apontar para si mesma, e uma rodada ruim
viraria a fonte da seguinte (a armadilha do `arte_de` do `instala_item.py`).

### As três travas

1. **O conjunto de opcodes do bytecode tem de ser exatamente o esperado**
   (`LOADK`, `GETGLOBAL`, `SETGLOBAL`, `NEWTABLE`, `SETLIST`, `RETURN`).
   Qualquer outro aborta. Sem isso, uma construção que o leitor não entendesse
   seria **descartada em silêncio** e a regeração jogaria dado fora — o mesmo
   perigo do `RK` acima de 255 do `luadis.py`.
2. **As três placas casam por mapa+célula E pelo texto exato.** Coordenada
   sozinha se repete entre mapas, texto sozinho se repete entre cidades. Se
   qualquer uma das três não casar, aborta em vez de gravar duas.
3. **A conferência compila o que foi gravado e relê o bytecode com o mesmo
   parser**, comparando as 511 entradas uma a uma e exigindo que as três
   ausentes estejam ausentes. Conferir o texto por regex provaria só que a
   string sumiu, não que o Lua entende o arquivo.

### Como saber, em jogo, que deu certo

O cliente só lê a tabela na inicialização, e só redesenha ao entrar no mapa:
**fechar e reabrir o cliente**, e sair e voltar a Prontera.

A placa sumir **não basta** como prova — arquivo quebrado também some, e leva as
outras 511 junto. O que separa os dois é olhar uma que tem de **ficar**: o
`등급강화소` em `prontera 50,293`, ou o teleportador da Ordem em
`prontera 124,76`. As duas na tela + a de 166,300 fora = deu certo.

**É cliente: vai por PATCH, não por deploy** (`CLAUDE.md` §4.18).

---

## `monta_mobs_da_sombria.py` — os 14 monstros da Glast Heim Sombria

```
python monta_mobs_da_sombria.py             # gera os dois arquivos
python monta_mobs_da_sombria.py --conferir  # sai 1 se algo divergir
```

Gera `db/guerra/mob_db_sombria.yml` (os monstros) e
`db/import/mob_skill_db.txt` (as habilidades deles).

### O problema

Os monstros da Sombria — ids **3139 a 3152** — **não existem em versão nenhuma
do rAthena**. No `db/re/mob_db.yml` do nosso vendor, e também no master do
rAthena baixado em 2026-08-28, os catorze estão como *placeholder*: duas linhas
comentadas cada um, com `Id` e `AegisName` e mais nada.

```
#  - Id: 3139
#    AegisName: MG_ZOMBIE_H
```

Não há o que descomentar. Sem status, sem drop, sem habilidade.

### A regra de derivação, e por que ela não é invenção

Cada `_H` é o monstro normal da Maldição com **três campos** mexidos:

| campo | mudança |
|---|---|
| `Level` | +30 |
| `Hp` | ×2 — e **×10** nos dois MVPs (3150 e 3151) |
| `BaseExp` / `JobExp` | ×2 |

Todo o resto é idêntico: os seis atributos, `Defense`, `MagicDefense`,
`AttackRange`, `Size`, `Race`, `Element`, `ElementLevel`, as velocidades, o
`Ai`, o `Class` e a tabela de drops.

**Isso foi conferido campo a campo contra o divine-pride nos treze pares**, em
2026-08-28 — não deduzido. O HP bate nos treze (135.600 → 271.200,
208.100 → 416.200, … 4.290.000 → 42.900.000 no Amdarais); o EXP bate nos treze;
os atributos e as defesas batem em todos.

**`Attack` e `Attack2` não mudam**, e isso também foi medido: o divine-pride
mostra a faixa já **calculada**, não o campo. A razão entre a faixa do `_H` e o
`Attack2` do normal deu **1,50** nos dois casos magicamente isoláveis
(4804/3200 no Sanguinário, 4179/2787 na Alma) — ou seja o campo é o mesmo e o
que sobe é o nível.

### A leitura que engana: elemento

No divine-pride, a linha "Element" é a tabela de **resistência**, e ela mostra
`Neutral (100%)` para bicho de elemento **Morto-vivo**. Ler dali poria metade
dos catorze em Neutro. O elemento vem do monstro normal, e as duas leituras
concordam onde dá para separar: o Cavaleiro Sombrio aparece como "Dark 4" e o
2470 é `Dark`/4; o Arclouse como "Earth 2" e o 2467 é `Earth`/2. A linha
`Dark 0% | Undead 0%` do 3146 confirma Morto-vivo no Khalitzburg.

### A única coisa que a derivação não copia: a carta

Os dois MVPs têm carta própria, e ela já existe no `item_db` do vendor — a
**4602** (Carta Amdarais Sombrio) e a **4604** (Carta Origem da Escuridão).
Copiar a carta do normal faria a Sombria, que custa dez vezes mais HP, entregar
exatamente o mesmo prêmio da fácil, e deixaria as duas `_H` sem fonte no
servidor inteiro. A troca está na tabela `CARTAS` do gerador.

### Por que as habilidades moram em `db/import/`

O `mob_skill_db.txt` **não é YAML** — não tem `Footer: Imports:`. O
`mob_readskilldb` (`src/map/mob.cpp:7184`) lê de **dois** lugares e só dois:
`db/re/` e `db/import/`. Como `db/re/mob_skill_db.txt` é arquivo de terceiro e
a §2 do `CLAUDE.md` proíbe enxertar dado nele, o nosso vai para `db/import/`.

**E isso custou uma exceção no `rathena/.gitignore`**, que ignorava
`/db/import` inteiro. A forma que funciona é `/db/import/*` seguido de
`!/db/import/mob_skill_db.txt` — e a barra-asterisco **é o que faz funcionar**:
pasta excluída o git nem abre, então negar um arquivo dentro dela não tem
efeito nenhum. Os outros ~60 arquivos de `db/import` continuam fora do git, que
é onde devem ficar.

Onze dos treze têm habilidade; o Khalitzburg (2471) e os dois Comandantes
(2473, 2474) não têm nenhuma no vendor, então os `_H` deles também não ganham.

### Depois de rodar

**Reiniciar o map-server** (ou `@reloadmobdb`). O `--conferir` também checa se o
`- Path: db/guerra/mob_db_sombria.yml` está no rodapé de `db/re/mob_db.yml` e se
a exceção do `.gitignore` está lá — sem qualquer um dos dois a falha é calada.

---

## `confere_celula.py` — aquela célula é andável?

```
python confere_celula.py 1@gl_he 150,46 151,71 148,67
python confere_celula.py 1@gl_he2 --salas 8
```

Responde se uma coordenada é chão andável, e acha lugar bom para plantar coisa.

### Por que existe

Coordenada de spawn escrita a olho produz uma falha das caras: o `mob_spawn`
sorteia com `map_search_freecell`, então célula fechada vira *"o bicho nasceu em
outro lugar"* e **não** um erro. NPC plantado em célula fechada fica
inalcançável, e nada no log aponta para a linha.

### De onde vem a resposta, e por que isso importa

Do **`map_cache.dat` do servidor**, que é o que o rAthena de fato lê — não do
`.gat` do GRF. Dois motivos:

1. metade dos `.gat` de mapa de instância está **cifrada com DES** no
   `data.grf` (o `1@gl_k.gat` está), e o `grf.py` recusa. Ler dali devolveria
   *"mapa não existe"* sobre um mapa que existe;
2. são **três** `map_cache` e o primeiro que tiver o mapa vence
   (`map.cpp:3922`). Ferramenta que abra só o `db/map_cache.dat` responde pelo
   mapa errado — a `prontera` de renewal, por exemplo, só existe no `db/re/`.

A ferramenta percorre os três na ordem certa e diz de qual veio.

### `--salas`

Varre os **pedaços conectados** de chão e devolve, de cada um dos maiores, o
ponto de maior distância até a parede. É o que se quer para plantar chefe,
portal ou grupo de monstro.

O tamanho de cada pedaço responde de quebra a pergunta que o `vis_h01` levantou
(`CLAUDE.md` §5): pedaço de algumas centenas de células **solto no canto do
mapa** é ruído do `.gat`, não sala — o `1@gl_he` tem um de 599 células em
`299,0`, e monstro sorteado ali nunca é achado.

Foi ela que deu todas as coordenadas do `1@gl_he2`, que é planta para a qual não
existe referência em lugar nenhum.


## `monta_labirinto.py` — gera o Labirinto das Valquírias inteiro

```
python monta_labirinto.py              # grava o arquivo
python monta_labirinto.py --conferir   # só relata, não grava
python monta_labirinto.py --tabela     # imprime as salas e o grafo
```

Escreve `rathena/npc/guerra/labirinto_das_valquirias.txt` do zero: cabeçalho,
o Portal de Malangdo, as duas escadas, os catorze mapflags, **78 portais** e
**250 linhas de spawn**. O arquivo é gerado — editar à mão é perder na próxima
rodada.

**Por que gerado.** São 40 salas que não se tocam, e três números amarram uns
aos outros:

- o **destino** de cada portal é a célula de **chegada** da sala de destino.
  Mover uma chegada obriga a mover todo portal que aponta para ela;
- a chegada tem de ficar **a quatro células** dos portais da própria sala.
  Não basta ficar fora da área de toque de 3×3: desembarcar ao lado dela
  significa que o primeiro passo na direção errada teleporta o jogador antes
  de ele ver onde caiu;
- a **área de spawn** tem de caber dentro da sala — e nos quatro anéis do 1º
  andar ela não pode cobrir a câmara selada do meio, porque
  `map_search_freecell` olha se a célula é andável e nunca se dá para chegar
  nela.

Escrever isso à mão é a §4.11 do `CLAUDE.md` ao contrário: listas paralelas
que divergem em silêncio. Aqui há uma fonte só — o `map_cache` do servidor
mais a tabela `GRAFO` — e o arquivo sai dela.

**Onde mexer**, e é para isso que a ferramenta existe:

| constante | o quê |
|---|---|
| `GRAFO` | a fiação: que sala leva a que sala, quais expulsam, onde ficam as escadas |
| `POR_TIPO` | quantos monstros **de cada tipo** por sala — é o volume |
| `RENASCE` | o renascimento por andar, em ms |
| `TIPOS` | quais monstros em cada andar |
| `PRECO` | o pedágio de cada andar |

**O portal vai em cima do arco, e é o mapa que diz onde.** O `force_map1/2/3`
traz plantado no próprio `.rsw` o modelo cujo nome em coreano significa
literalmente **"dispositivo de warp semicircular"** — é o semicírculo de pedra
que aparece no chão encostado nas paredes. São **22 no 1º andar, 25 no 2º e 40
no 3º**, e eles são os pontos de portal do mapa: quem desenhou a arena marcou
onde cada warp devia ficar.

Duas versões desta ferramenta escolheram a célula por conta própria — primeiro
pelos extremos da sala, depois pela folga — e as duas erraram em jogo pelo
mesmo motivo: o portal caía no meio do chão liso com o semicírculo vazio a dez
células dali. A tabela `ARCOS` foi tirada do `.rsw` com o `rsw.py` e a conversão

```
célula_x = pos.x / 5 + largura/2
célula_y = altura/2 - pos.z / 5
```

encaixada depois na célula andável mais próxima, porque parte dos arcos é
desenhada meio dentro da parede. O `.rsw` sai do `data.grf` do **bRO** — no
nosso ele tem flag DES e o `grf.py` recusa.

**Sala sem arco fica fora do labirinto.** São as quatro câmaras seladas do 1º
andar (aquelas que se enxerga de dentro do anel e não se alcança) e a câmara
do sul do 3º. O autor do mapa não plantou warp em nenhuma; pôr um lá é voltar
ao defeito.

**A fiação é sorteada com semente fixa.** O primeiro arco de cada sala liga a
próxima da corrente, e a corrente passa por todas as salas com arco a partir
da entrada — então existe sempre um caminho, e ele atravessa o andar inteiro.
O último elo é a escada. Os arcos que sobram levam a uma sala sorteada, e um
em cada quatro expulsa para Malangdo. A semente é fixa para o labirinto não
mudar a cada rodada da ferramenta.

**Os seis tipos de monstro entram em TODAS as salas** — o que muda de sala
para sala é só a quantidade. Também veio do teste: com um tipo por sala, *"se
eu fizer sempre o mesmo caminho, vou encontrar sempre os mesmos"*, e sala com
elenco fixo não é labirinto, é rota.

**Depois de gerar:** mudança só de spawn ou de portal pega com
`@reloadscript`. Se tiver mexido em mapflag, é reiniciar o map-server.

**O que a ferramenta NÃO faz:** ligar os três mapas (isso é
`conf/guerra/mapas_guerra.txt`), a taxa da Mente Maligna (`db/guerra/
mob_db_guerra.yml`) e os NPCs de economia (`npc/guerra/valquirias_de_
malangdo.txt`, escrito à mão).
