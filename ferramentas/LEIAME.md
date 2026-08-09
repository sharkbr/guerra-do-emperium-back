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

A tabela tem cinco itens em 2026-08-08 — 30999 Maçã da Inocência, 30998 Moeda
Nova, 30997 e 30996 (as duas caixas da Máquina) e 30995 Caveira Humana, que
copia a arte da Caveira comum (7420).

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

Doze partes, doze fontes diferentes dentro da instalação do Ragnarok Brazil.
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

## `ajusta_tamanho_fonte.py` — aumenta a fonte do jogo

```
python ajusta_tamanho_fonte.py --verificar   # so relata
python ajusta_tamanho_fonte.py               # aplica o estado aprovado
python ajusta_tamanho_fonte.py --bonus 1     # cada letra um pixel maior
python ajusta_tamanho_fonte.py --teto 12     # afrouxa o teto
python ajusta_tamanho_fonte.py --face Gulim  # Gulim, Arial, Tahoma, Verdana
python ajusta_tamanho_fonte.py --fixo 20     # uma altura so, para diagnostico
python ajusta_tamanho_fonte.py --reverter
```

A conta e **`altura = min(tamanho pedido, --teto) + --bonus`**, e os padroes ja
sao os valores aprovados no jogo em 2026-08-09: face **Arial**, **`--bonus 0`**,
**`--teto 11`**, sem suavizacao. Rodar sem argumento reproduz esse estado.

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

### O teto, e por que ele existe

Algumas linhas pedem corpo maior que o resto — na janela de informacoes
basicas, HP, SP, Base Lv., Job Lv. e a linha de peso e zeny. **Essa hierarquia
e do proprio cliente e ja existia antes de qualquer patch**, conferido contra
captura do estado original. So que a nossa face desenha maior na mesma altura
pedida, e a diferenca, que era discreta, ficou gritante.

O `--teto` limita o tamanho PEDIDO antes de criar a fonte, entao segura esses
poucos casos e deixa o resto passar intacto. A calibragem, degrau a degrau:

| teto | o que aconteceu |
|---|---|
| 14 | **nada** — prova que aquelas linhas pedem 14 ou menos |
| 12 | a janela encolheu e o resto do jogo ficou igual |
| 11 | o ponto: aprovado no jogo |

O `14` nao ter feito efeito e o dado mais util da tabela: matou a hipotese de
que aquelas linhas pediam um corpo muito maior. A diferenca era de poucos
pixels, amplificada pela face.

Abaixo de 11 o teto passa a ficar **abaixo** do que a maioria dos textos pede,
e deixa de ser limite para virar reducao geral. O sintoma e a descricao de item
e o inventario encolherem junto.

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

### O que ele NÃO faz, e por que isso não impediu de usá-lo

Ele **não** estende o `spriterobeid.lub`/`spriterobename.lub` — a tabela que
traduz o `View` do `item_db` no nome da pasta. É o que o
`estende_accessoryid.py` faz do lado do chapéu, e é a metade que continua
faltando.

A diferença é que ela nem sempre é necessária. A nossa tabela tem **120
entradas**, e todo manto cujo `View` já esteja lá precisa apenas da arte — que
é o que este script copia. Foi exatamente o caso dos treze do Manteleiro: os
`View` deles vão de 61 a 114, todos dentro das 120.

**Manto com `View` fora da tabela é RECUSADO**, com o motivo por extenso, em
vez de copiar 600 arquivos que o cliente nunca vai procurar. Prometer cura que
não há como cumprir foi o erro que o `varre_cosmeticos.py` já evita do outro
lado.

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
