# Arquitetura — como as peças se encaixam

Complemento do `CLAUDE.md`. Aqui está **quem lê o quê**, em que ordem, e —
a parte que mais custa redescobrir — **o que precisa mudar junto**.

---

## 1. As quatro camadas

```
  ┌─────────────────────────────────────────────────────────────┐
  │  CLIENTE   C:\GuerraDoEmperium\cliente\   (fora do git)      │
  │  desenha, e decide sozinho nome, ícone, descrição e arte     │
  └───────────────────────────┬─────────────────────────────────┘
                              │ pacotes (PACKETVER 20211103)
  ┌───────────────────────────┴─────────────────────────────────┐
  │  SERVIDOR  rathena/     login 6900 · char 6121 · map 5121    │
  │            + web 8888 (emblema de clã, por HTTP)             │
  └───────────────────────────┬─────────────────────────────────┘
                              │
  ┌───────────────────────────┴─────────────────────────────────┐
  │  BANCO     MariaDB 3306                                      │
  └─────────────────────────────────────────────────────────────┘

  FERRAMENTAS  ferramentas/*.py (Python 2.7) — atravessam as camadas:
               leem o GRF do bRO e escrevem no cliente e no servidor
```

**A regra que explica quase todo bug estranho:** o servidor manda **IDs**, o
cliente decide o que desenhar. Nome, descrição, ícone e sprite de um item vêm
dos arquivos do cliente, não do `item_db.yml`. Item que existe no servidor e não
no cliente vira caixa de erro; nome trocado no servidor não muda o que o jogador
lê.

## 2. A cadeia de carga do servidor

**Scripts de NPC** — `import:` é recursivo, profundidade livre
(`src/map/map.cpp:4249`):

```
src/map/map.cpp
  └── npc/re/scripts_main.conf
        └── npc/scripts_custom.conf
              └── npc/guerra/scripts_guerra.conf   ← o índice dos nossos NPCs
                    └── npc/guerra/*.txt
```

**Ordem importa:** `scripts_custom.conf` é lido **depois** de
`scripts_mapflags.conf`. É disso que dependem `visual_sempre_visivel.txt` e as
mapflags de `arena_de_combate.txt` — eles desfazem mapflag do rAthena de fora.

**Configuração de regra de jogo:**

```
conf/battle_athena.conf
  ├── conf/battle/*.conf          (rAthena)
  ├── conf/guerra/battle_guerra.txt   ← nosso: exp 10x, drop 50x
  └── conf/import/battle_conf.txt     ← máquina; fora do git; ÚLTIMA palavra
```

`conf/import/` vem por último de propósito: pode sobrescrever qualquer coisa
nossa numa máquina específica. E **regra de jogo versionada não cabe ali** —
`conf/import/` está fora do git (é onde moram as senhas), então um clone limpo
herdaria o rAthena vanilla.

**Banco de dados** — cada arquivo do rAthena tem um `Footer`/`Imports` no rodapé
apontando para o nosso:

| Arquivo do rAthena | Importa |
|---|---|
| `db/re/item_db.yml` | `db/guerra/item_db.yml` |
| `db/item_combos.yml` | `db/guerra/item_combos.yml` |
| `db/re/mob_db.yml` | `db/guerra/mob_db.yml` |
| `db/re/reputation.yml` | `db/guerra/reputation.yml` |
| `db/re/reputation_group.yml` | `db/guerra/reputation_group.yml` |

## 3. O cliente: quem ganha na hora de resolver um arquivo

O patch **`DataFolderFirst` está aplicado**, então:

```
cliente\data\  (pasta solta)   ← VENCE
cliente\data.grf               ← só se não achar acima
```

Toda alteração visual nossa é um arquivo **solto em `cliente\data\`** que
sombreia o do GRF. Reverter = apagar o arquivo solto. É assim que Izlude arrasada
e os overrides de mapa funcionam.

**Os arquivos do cliente que importam, e o que cada um decide:**

| Arquivo | Decide | Encoding | Quando é lido |
|---|---|---|---|
| `SystemEN\LuaFiles514\itemInfo.lua` | nome PT, descrição, ícone, `identifiedResourceName`, slot | ANSI/CP949 | **só na inicialização** |
| `data\luafiles514\lua files\datainfo\accessoryid.lub` + `accname.lub` | qual slot de visual de cabeça o cliente conhece | — | inicialização |
| `data\sprite\...` | a arte (ícone `collection`, `.spr`/`.act`) | binário | em uso |
| `data\msgstringtable.txt` | texto de interface | cp1252 | inicialização |
| `data\contentdata\repute\*.bson` | nome da reputação — **só aceita ASCII** | BSON | inicialização |
| `System\OngoingQuestInfoList_Sakray.lub` | a janela de missões (o `questid2display.txt` é só fallback) | — | inicialização |

**Nada disso recarrega em quente. Mudou arquivo de cliente = fechar e reabrir.**

## 4. Os acoplamentos — o que precisa mudar junto

Esta é a seção a consultar antes de qualquer adição. Mexer numa peça sem as
outras **quebra calado**.

### Um item novo vive em até 6 lugares

| # | Onde | O que põe | Ferramenta |
|---|---|---|---|
| 1 | `db/guerra/item_db.yml` | ID, tipo, bônus, peso, preço, `Location` | à mão |
| 2 | `SystemEN\LuaFiles514\itemInfo.lua` | nome PT, descrição, ícone, recurso | `instala_item.py` / `completa_iteminfo.py` |
| 3 | `data\sprite\` | a arte (4 de item + 4 de cabeça) | `instala_visual.py` |
| 3b | `data\sprite\<manto>\` | a arte de manto, **se for `Costume_Garment`** — uma pasta, com um par de arquivos por CLASSE de personagem | `instala_manto.py` |
| 4 | `accessoryid.lub` + `accname.lub` | o slot de visual, **se for de cabeça e novo** | `estende_accessoryid.py` |
| 4b | `spriterobeid.lub` + `spriterobename.lub` | o slot de manto — **reaproveitando** um dos 40 slots ≤120 sem arte; o cliente ignora acima disso | `estende_robeid.py` |
| 5 | `npc/guerra/mercado_*.txt` | a loja que vende | à mão / gerador |
| 6 | `db/guerra/item_combos.yml` | o conjunto, se fizer parte de um | à mão |

**A ordem entre 2, 3 e 4 não é intuitiva e erra em silêncio** — ver `RECEITAS.md`.

Sem (2), o cliente mostra caixa de erro. Sem (3), o chapéu é invisível. Sem (4)
quando necessário, `instala_visual.py` relata "faltando 0" e o item continua
invisível.

**Manto é a exceção que muda onde a falha aparece.** As camadas 3 e 3b falham em
momentos diferentes, e a segunda é a cara:

| falta | quando estoura |
|---|---|
| os 4 arquivos de **item** (ícone, collection, spr, act de chão) | **ao abrir a loja** — caixa modal, antes de qualquer compra |
| a arte de **manto** por classe (3b) | **ao equipar** — a loja abre, vende, e só então falha |

**A camada 4b não é simétrica com a 4, e a assimetria é dupla.**

Primeiro no que o jogador vê quando falta a entrada de tabela:

| falta a entrada de tabela | chapéu (4) | manto (4b) |
|---|---|---|
| o que o jogador vê | `Cannot find File` **modal** | **nada, em silêncio** |
| gravar a entrada sem ter a arte | não piora — já era modal | **piora** — troca silêncio por modal |

Depois, e é o que manda: **a camada 4 estende, a 4b não.** O
`accessoryid.lub` aceita slot novo de cabeça (2192 → 2405 hoje); o
`spriterobeid.lub` aceita entrada nova e **o cliente ignora slot de manto acima
de 120** — medido em tela em 2026-08-09, com a tabela contígua até 158. Então a
4b não é "acrescentar", é **trocar**: o `estende_robeid.py` reaponta um dos 40
slots ≤120 sem arte, e quem decide qual é o `View:` do
`db/guerra/item_db.yml`. Sobram 31; depois disso, só patch de exe.

**A ordem entre 4b e 3b continua obrigatória:** o `instala_manto.py` só sabe em
que pasta copiar depois que a tabela conhece o slot.

**Nem todo `Costume_Garment` usa 3b:** peça sem `View` (a Aura Nevada, 480097) é
só um `hateffect` no `Script` do item — efeito de tela, sem desenho vestido.

### Uma loja de troca (`barter`) vive em 3 lugares, e o cliente é um deles

| Onde | O que | Recarrega com |
|---|---|---|
| `npc/guerra/barters_guerra.yml` | a lista: item, moeda e quantidade por linha | `@reloadbarterdb` |
| `npc/guerra/<npc>.txt` | a **porta** — a fala e o `callshop` | `@reloadscript` |
| `itemInfo.lua` do cliente | **o nome e o ícone que a janela desenha** | fechar e reabrir |

O terceiro é o contra-intuitivo: o pacote da janela de troca leva **só o ID**
(`clif.cpp:23225`), então quem nomeia cada linha é o cliente. Num menu de
`select` seria o servidor, via `getitemname()`. **Nome errado numa loja de
troca não se conserta com o `nomes_pt_item_db.py`.**

Os dois primeiros são independentes: desligar a linha do NPC no
`scripts_guerra.conf` tira a porta e **deixa a loja carregada e inalcançável**;
a loja é carregada pelo `npc/barters.yml`, não pelo índice dos nossos NPCs.

E há um acoplamento a mais quando a linha é um **pacote**: o `barter` cobra por
unidade e não tem campo de quantidade para o item vendido, então "5 por 1
Moeda" exige que as 5 sejam **um item** — uma caixa, que por sua vez é um item
novo com todos os lugares da tabela acima.

### Uma reputação vive em 3 lugares, todos com o mesmo `Id`

| Onde | O que |
|---|---|
| `db/guerra/reputation.yml` | o `Id`, a variável e os limites |
| `data\contentdata\repute\*.bson` | o **nome que o jogador lê** (`traduz_reputacao.py`) |
| `npc/guerra/honra_de_combate.txt` | as regras e o placar |

Exige **reiniciar o map-server** (`reputation_db.load()` só roda no `do_init_pc`)
e a tabela de `sql-files/guerra_arena_pvp.sql`. Sem ela, o `query_sql` falha e
ninguém pontua — mas o anúncio de morte continua saindo, e é esse o sintoma que
aparece primeiro.

**E o PISO da pontuação está escrito duas vezes**, uma em cada ponta: o
`Minimum: -10` do `Id 5` em `db/guerra/reputation.yml` (que o
`set_reputation_points` aplica com `cap_value`, `script.cpp:27229`) e o
`GREATEST(pontos + <delta>, -10)` do `UPDATE` em `honra_de_combate.txt`
(`.PisoQueda`). Baixar um sem o outro **não dá erro**: a tabela continua
descendo e o modal para no `Minimum`, então a placa mostra um número que o
jogador nunca vê no próprio status. O mesmo vale para o `Maximum: 3000`, que
hoje não tem par do lado do SQL porque ninguém chegou perto.

### O Logue e Ganhe vive em 2 lugares, e o servidor não conversa com o outro

| Onde | O que |
|---|---|
| `db/guerra/attendance.yml` | os ciclos e o prêmio que é **entregue** (por RoDEX) |
| `cliente\System\CheckAttendance.lub` | o prêmio que é **desenhado** nos 20 quadrados |

O pacote `ZC_UI_OPEN` leva **um número só** — o contador do jogador. A lista de
prêmios nunca trafega: o cliente pinta a dele. Divergir as duas tabelas **não
dá erro em lugar nenhum**; a janela promete um item e o correio entrega outro.

Por isso as duas são **saída** de `ferramentas/monta_logue_e_ganhe.py`, que tem
a receita uma vez só. `@reloadattendancedb` recarrega **só a metade do
servidor** — o `.lub` exige fechar e reabrir o cliente.

**Vinte dias é teto do cliente**, não escolha nossa, e o último ciclo gerado
vence em 2027-12-31 — depois disso o sistema some sem avisar (`PENDENCIAS.md`
§1b).

### O nome de uma instância vive em 2 lugares, e é CHAVE — não rótulo

Aberto em 2026-08-08, ao traduzir os nomes. **É a exceção à regra da §1**: o
nome da instância é o raro texto que o **servidor** manda. O
`clif_instance_create` (`clif.cpp:18794`) empacota `db->name` no pacote `0x2cb`,
e é esse o título que o jogador lê na janela. Não vem do `itemInfo.lua` —
traduzir é mudança de servidor só, sem fechar o cliente.

| Onde | O que | Recarrega com |
|---|---|---|
| `db/guerra/instance_db.yml` | o `Name:` — o título na janela e no `mapannounce` | `@reloadinstancedb` |
| o `.txt` da instância | o **literal** em `instance_create` / `instance_enter` / `.@md_name$` | `@reloadscript` |

**Os dois têm de mudar na mesma passada.** `instance_create("<nome>")`,
`instance_enter("<nome>")` e `instance_live_info(ILI_NAME,...) == "<nome>"`
resolvem por **string**: trocar o `Name:` no db sem trocar o literal faz a
instância parar de abrir. Na prática é barato — quase todo script declara
`.@md_name$ = "..."` **uma vez** e usa por variável.

O `db/guerra/` só precisa do `Id` e do `Name`: o `parseBodyNode`
(`instance.cpp:52`) faz `find(id)` e sobrescreve **apenas os campos presentes**.
Repetir `Enter`/`AdditionalMaps` seria criar uma segunda verdade.

**Duas armadilhas caladas:**

1. **Nome repetido é descartado sem erro.** O parser emite *"Instance name %s
   already exists, skipping"* e cai num `return 0` — a instância fica com o nome
   antigo e só um aviso afogado no log denuncia.
2. **O extrator da tradução captura o nome como se fosse fala.**
   `instance_create` **não** está em `CONTEXTOS` (`traduz_npcs.py:75`), mas
   `.@md_name$ = "..."` casa com `RE_ATRIB`, e o `RE_TECNICO` — que protege nome
   de mapa e item — **não cobre esse caso**. Criar o grupo `instancias` sem
   proteger antes deixa o catálogo oferecer o nome da instância para tradução,
   e uma segunda tradução divergente quebra o `instance_create`. Ver
   `PENDENCIAS.md` §1f.

O menu da `teletransportadora.txt` cita os mesmos nomes, mas ali é **rótulo de
verdade**: ela nunca chama `instance_create`, só `Go(mapa,x,y)`. Divergir não
quebra nada — só faz o jogador ler dois nomes para a mesma coisa.

### Uma missão da Ordem vive em 3 lugares, e um deles é o CLIENTE

Aberto em 2026-08-08, com a Ordem dos Exploradores. O **alvo** de uma caçada e
a **recompensa** dela moram em arquivos diferentes, porque o `quest_db` do
rAthena não tem campo de recompensa — ele só sabe de `Drops` (item que cai do
mob), e a Ordem paga na entrega. E o **texto** que o jogador lê na janela de
missões não vem de nenhum dos dois: vem do cliente.

| Onde | O que | Recarrega com |
|---|---|---|
| `db/guerra/quest_db.yml` | o `Id`, o `Title` e os `Targets` (mob + quantidade) | `@reloadquestdb` |
| o `OnInit` de `npc/guerra/ordem_dos_exploradores.txt` | `.quest[]`, `.nome$[]`, `.paga[]`, `.exp[]` — e `.ini[]`/`.fim[]`, que fatiam as tabelas por placa | `@reloadscript` |
| `cliente\System\OngoingQuestInfoList_True.lub` e `_Sakray.lub` | o título, a descrição e o resumo na janela de missões | **fechar e reabrir o cliente** |

**O terceiro não é cosmético: sem ele o cliente cai.** O
`GetOngoingQuestInfoByID` indexa `QuestInfoList[id].Title` sem guarda de nil,
então uma missão que o cliente não conhece abre caixa de erro de Lua **por
missão e por atualização da janela** até a conexão cair. Ver `CLAUDE.md` §5.

Aqueles dois `.lub` são **gerados** pelo `traduz_ptbr.py questinfo`, que os
reconstrói do coreano de 2021 — entrada posta à mão some na próxima rodada.
Por isso as nossas saem de `ferramentas/monta_missoes_da_ordem.py`, que lê as
ids do `quest_db.yml` e tem o texto PT dentro. **A ordem importa:**
`traduz_ptbr.py questinfo` primeiro, o nosso script depois. É o mesmo arranjo
do Logue e Ganhe.

**As quatro tabelas do NPC são lidas pelo mesmo índice.** Inserir uma missão no
meio de uma sem inserir nas outras troca o pagamento de missão — silenciosamente,
porque nada valida o alinhamento. Acrescentar missão é: uma entrada no
`quest_db.yml`, uma linha em **cada** uma das quatro tabelas, e o ajuste de
`.ini`/`.fim` do grupo.

**Esse alinhamento já quebrou uma vez, no Teleportador do mesmo arquivo** — o
menu e os destinos ficaram em ordens diferentes e os catorze teleportes foram
para o lugar errado, sem erro nenhum (`CLAUDE.md` §4.11). Lá o conserto foi
gerar o menu da própria tabela; aqui as placas não têm menu gerado, então o
alinhamento das quatro colunas **continua sendo responsabilidade de quem
edita**. Ao mexer, conferir contando: `.quest`, `.nome$`, `.paga` e `.exp` têm
de ter o mesmo tamanho, e `.fim[2]+1` tem de ser esse tamanho.

**As três placas dividem essas tabelas.** São um script e dois `duplicate`, e
variável de escopo `.` pertence ao *script* (`npc.cpp:4602`) — o mesmo arranjo
das duas Máquinas. Cada placa descobre quem é pelo pedaço depois do `#` do nome
(`strnpcinfo(2)`).

**Duas armadilhas caladas, as duas do leitor de YAML:**

1. **AegisName de mob inexistente descarta a quest inteira.** `quest.cpp:132`
   emite *"Mob %s does not exist, skipping"* e cai num `return 0` que joga fora
   a quest toda, não a linha do alvo. Conferir nome novo contra o `mob_db`
   antes de gravar.
2. **`MAX_QUEST_OBJECTIVES` é 3** (`src/common/mmo.hpp:111`), e a Torre do
   Demônio já usa os três. Um quarto alvo cai no mesmo `return 0`.

O nome da instância aparece nas duas tabelas do NPC (`.nome$[]` e o `.menu$` do
Teleportador) e ali é **rótulo**, não chave — a Ordem nunca chama
`instance_create`. Divergir não quebra nada; só faz o jogador ler dois nomes
para a mesma coisa.

### Uma tradução de NPC vive em 2 lugares

O catálogo (`npc/guerra/traducao/*.cat`) é a **fonte**; o arquivo `.txt` do
rAthena é o **resultado**, reescrito por `traduz_npcs.py`. Editar o `.txt` à mão
é perder o trabalho na próxima passada. Grupos hoje: `campal`, `cidades`,
`classe1`, `classe2`, `glossario`, `guerra`, `kafra`, `novico`, `pvp`, `servico`,
mais um por instância (`monarca`, `magoas`, `orcs`, `sarah`, …).

### Um NPC do rAthena BIFURCADO vive em 3 lugares, e o terceiro é um instantâneo

Quando a receita da §2 do `CLAUDE.md` não basta — `disablenpc` mais duplicata —
porque a regra a mudar mora **dentro** do script compartilhado, o jeito é
copiar o NPC para `npc/guerra/`. A cópia então tem uma **terceira** dependência,
e é a que não se denuncia:

| # | Onde | O quê |
|---|---|---|
| 1 | `npc/guerra/<nosso>.txt` | a cópia, com a regra nova, e o `disablenpc` do original |
| 2 | `npc/re/…/<upstream>.txt` | o original, agora desligado — mas ainda lido, ainda traduzido |
| 3 | `npc/guerra/traducao/<grupo>.cat` | a tradução, que continua escrevendo **só em (2)** |

**O texto de (1) é um instantâneo de (3) no dia em que a cópia foi feita.**
Reaplicar o catálogo conserta (2), que ninguém vê, e deixa (1) como estava —
quem melhorar uma fala no catálogo a vê mudar no NPC desligado e continuar
velha no que o jogador lê. Nada erra no log.

Regra prática: **quem mexe na tradução de um NPC bifurcado mexe nos dois lados,
ou regera a cópia.** Caso vivo: a Colecionadora do Túmulo do Monarca
(`npc/guerra/colecionadora_do_monarca.txt`, 2026-08-12), copiada porque a lista
de acessórios aceitos precisava crescer de 122 para 216 e a lista mora dentro
do `switch` do script do rAthena.

O outro custo é o de sempre: (1) não recebe correção do upstream. Vale a pena
quando a alternativa é editar código de terceiros — e não vale quando um
`duplicate` resolve, porque `duplicate` compartilha o script e não cria (3).

### Um móvel de cenário vive em 2 lugares, e um é o cliente e o outro o servidor

Plantar o modelo é metade. O `.rsw` **não toca o `.gat`**, então uma peça posta
por `edita_mapa.py` é **atravessável**: ela existe no desenho e não existe na
colisão. As duas metades:

| metade | onde | como se aplica |
|---|---|---|
| o desenho | `.rsw` — receita em `ferramentas/edita_mapa.py`, arquivo em `cliente\data\` | entrar no mapa (cliente reaberto) |
| o bloqueio | `setwall` no `OnInit` do NPC do mapa | `@reloadscript` |

A divergência **não dá erro nenhum** — dá móvel que se atravessa, ou pior, um
buraco invisível no chão se alguém mexer só na segunda metade. Caso vivo: a
escrivaninha do Centro da Ordem (`npc/guerra/centro_da_ordem.txt`, 2026-08-11),
cinco células fechadas para um modelo que o `.rsw` desenha.

**E é `setwall`, não `setcell`** — só ele avisa o cliente. Ver `CLAUDE.md` §4.

### Um NPC com sprite corrigido vive em 2 lugares, e um deles é o cliente

Nem todo sprite oficial está pronto para ser NPC. O `.act` diz a que altura o
desenho é colado na célula, e alguns vêm com `y = 0` — o centro do sprite fica
na altura do chão, a metade de baixo some sob o piso e o NPC aparece **cortado
reto na base**. Então o NPC passa a ter duas metades:

| metade | onde | como se aplica |
|---|---|---|
| o NPC | linha em `npc/guerra/` | `@reloadscript` |
| a altura do desenho | `.act` — receita em `ferramentas/levanta_sprite_npc.py`, arquivo em `cliente\data\sprite\npc\` | **fechar e reabrir o cliente** |

A divergência **não dá erro**: o NPC funciona, fala, abre loja — e aparece
enterrado. E o `@reloadscript` **não** conserta, porque a metade quebrada é do
lado de lá; foi assim que a correção do `2_COLAVEND` pareceu não pegar em
2026-08-12 (o `LastAccessTime` do `.act` provou que o cliente nunca o abriu).

Como todo override de cliente, **some em cliente novo**, calado. Caso vivo: a
Máquina de Sombrios Gerais (`npc/guerra/maquina_de_sombrios.txt`,
`auction_01 193,58`, sprite 910).

### O nome de um mapa vive em 2 arquivos do cliente e em 1 tabela da ferramenta

O jogador lê o nome de um mapa em **dois lugares distintos**, e um pedido de
renomear quase sempre quer os dois:

| metade | arquivo | o que é |
|---|---|---|
| o canto do minimapa | `cliente\data\mapnametable.txt` | uma linha `<rsw>#<nome>#` |
| o letreiro de entrada | `cliente\System\mapInfo_true.lub` e `_sak.lub` | `displayName` e `signName.mainTitle` do bloco |

**Nenhum dos dois é fonte.** Os três são **gerados** por
`ferramentas/traduz_ptbr.py mapas mapinfo` a partir do `mapInfo.lub` do bRO,
então edição à mão volta ao nome do bRO na próxima rodada, calada — mesma
família do `CheckAttendance.lub` e do `OngoingQuestInfoList` (`CLAUDE.md` §4.9).

A fonte é a tabela **`NOSSOS_MAPAS`**, dentro da própria ferramenta: só entra
ali mapa que **mudou de função** no nosso servidor. São dois hoje —
`auction_01` (Centro da Ordem) e `pvp_n_1-5` (Arena de Prontera, 2026-08-13).

O `parte_mapinfo` **só troca campo que já existe** no bloco: pôr `mainTitle`
num mapa cujo bloco não tem `signName` não dá erro nem efeito, fica inerte. E
trocar só o `displayName` deixa **metade do nome velho na tela** — foi o
letreiro, e não o minimapa, que ainda dizia "PvP Sala Bússola".

### Uma placa sobre a cabeça de NPC

`src/custom/placa_de_venda.hpp` + duas linhas em `src/map/clif.cpp` + o comando
de script `placadevenda` (`src/custom/script.inc`). **Exige recompilar.** Foi o
primeiro caso em que tocamos `src/map/`; hoje são quatro (mais o teto de refino
no `clif.cpp`, e a redução de carta e a de PvP no `battle.cpp` — a lista completa
dos enxertos está no `CLAUDE.md` §2). O porquê está no cabeçalho do `.hpp`.

### A redução de 80% vive em ONZE linhas, e metade não é nossa

Uma regra só — "dano final cai 80% em combate entre jogadores, sem exceção" —,
dois mecanismos diferentes, no mesmo arquivo (`conf/guerra/battle_guerra.txt`):

| Metade | Opções | De quem |
|---|---|---|
| guerra (`gvg*`) | `gvg_weapon/magic/misc/short/long_attack_damage_rate` | **do rAthena** — `battle_calc_gvg_damage` |
| mapa `pvp` | `pvp_dano_arma/magia/misc/curta/longa` | **nossas** — `src/custom/reducao_geral.hpp` |
| as duas | `reducao_dano_isenta_habilidade` | **nossa** — e é o que impede as duas de divergirem |

**Os dez valores andam juntos ou a regra racha, e nada avisa.** São cinco por
ambiente porque habilidade reduz por TIPO (arma, magia, misc) e ataque normal por
ALCANCE (curta, longa) — mudar um e esquecer os outros deixa parte dos golpes
fora, e o sintoma é "tal classe passou a doer mais".

**A décima primeira linha é a que evita a divergência de verdade.** A isenção de
habilidade (`IgnoreGvgReduction`) existia nos dois caminhos, um do rAthena e um
nosso; hoje os dois chamam a **mesma função**, então não há como desligar a
isenção só de um lado. Foi para isso que ela virou função em vez de um `if`.

Mudar **valor** é `@reloadbattleconf`. Mudar **a lógica** exige recompilar — são
cinco chamadas no `battle.cpp` (`CLAUDE.md` §2). Ver `REDUCAO-DE-DANO.md` §1c.

**A campal (`bg_*`) está fora das duas metades**, e para entrar precisa de conf
**e** de um sexto enxerto — não só das cinco linhas.

## 5. O que sobrevive a um clone limpo

| Sobrevive | Não sobrevive |
|---|---|
| Emulador, nossos NPCs, `db/guerra/`, `conf/guerra/`, `src/custom/`, ferramentas, catálogos | **Todo o cliente**, `conf/import/` (senhas, IP), binários compilados, GRFs, `log/` |

Consequência prática: **o repositório sozinho não põe o jogo de pé.** Ele põe o
servidor de pé. O cliente é trabalho manual desta máquina, documentado em
`PENDENCIAS.md` seção 0 — e é a peça de maior risco, porque não tem backup em
git.

## 6. Fontes externas de verdade

| Fonte | Onde | Para quê |
|---|---|---|
| **GRF do bRO** | instalação do Ragnarok Brazil desta máquina | arte, nome PT, descrição — a fonte de referência acordada |
| ROenglishRE | `C:\Users\User\Downloads\ROenglishRE` | luafiles em texto, `Tools\luac.exe -p` para validar sintaxe |
| WARP 1.5.3 | `C:\Users\User\Downloads\WARP-rock_win32` | patches do executável |
| NEMO / `Ragexe_unpacked.exe` | pasta do cliente | o exe oficial tem Themida e não aceita WARP |

**Cuidado com o ROenglishRE:** ele é atualizado para clientes mais novos que o
nosso (kRO 2021-11-03). Luafiles de 2024-2026 sobre GRF de 2021 quebram —
conferir "Last updated" antes de depurar.

### O cliente do bRO responde "como é lá?" — até certo ponto

Descoberto em 2026-08-09, ao perguntar se dava para saber como as instâncias
são no bRO. A instalação do Ragnarok Brazil não serve só de fonte de **arte e
nome**: ela carrega tabelas que descrevem **conteúdo**.

| Arquivo do bRO | O que responde |
|---|---|
| `System\OngoingQuestInfoList_True.lub` | título, descrição e resumo de toda missão — **incluindo as 30 missões de instância da Ordem dos Exploradores**, cada uma com a coordenada do NPC de entrada e o alvo por extenso |
| `System\iteminfo_new.lub` | nome PT, descrição e recurso de 18.845 itens |
| `navigation\navi_mob_br.lub` (no GRF) | nome PT de 2.473 monstros — **só os que aparecem na navegação**; chefe de instância **não está lá** |
| `navigation\navi_npc_br.lub` (no GRF) | NPCs de navegação, com mapa e coordenada |
| `data.grf` | mapas, sprites, ícones |

Os `.lub` são **bytecode Lua 5.1** — busca de string neles não é confiável;
quem os lê é o `ferramentas/luadis.py`.

**O limite, e ele é duro: o cliente NUNCA carrega a mecânica.** O que a
instância faz — o líder virar Orc Herói, as áreas com status escalando, o chefe
invocando flores — é script de **servidor**, e não sai da Gravity. Para isso só
há o browiki, e **`browiki.org` devolve 403** para busca automática: quem lê é
o dono, no navegador.

**Para que isso serve na prática:** comparar a **coordenada da porta** de cada
instância entre o bRO e o nosso rAthena é um teste barato de "é a mesma
versão?". Coincidir não prova que a mecânica é igual; **divergir prova que
não**. Foi assim que se soube que 14 das 16 instâncias da Ordem batem, e que só
a Batalha dos Orcs e a Vila dos Porings divergiram.

## 7. Os tetos — o que estoura primeiro quando o servidor encher

Levantado em 2026-08-08, ao avaliar ligar instâncias. **Nada aqui aperta hoje**;
está escrito para o dia em que a população crescer, para que a conta não precise
ser refeita.

### O gargalo é slot de mapa, e não é uma ladeira — é uma parede

```
MAX_MAP_PER_SERVER = 1500     src/common/mmo.hpp:42
mapas carregados   = 1258     conf/maps_athena.conf
                     ----
livres para clone  =  242
```

**Cada rodada de instância clona um mapa novo por mapa da instância**, em tempo
de execução (`map_addinstancemap`, `src/map/map.cpp:2818`). Não é uma cópia
lógica: é `CREATE`/`aCalloc` de células e blocos, ocupando um índice do array
global `map[MAX_MAP_PER_SERVER]`.

Das 78 instâncias do `db/re/instance_db.yml`, **62 usam 1 mapa** — mas a Endless
Tower usa 6 e a Thanatos Tower 8. Então o consumo não é "uma party, um slot":

| cenário | slots |
|---|---|
| 200 parties, todas em instância de 1 mapa | 200 — encosta em 242 |
| 40 dessas parties na Endless Tower | 40 × 6 = 240 — **estoura sozinho** |

**Quando estoura, a falha é limpa e visível:** `map_addinstancemap` devolve `-3`
e loga *"Could not add map ... the limit of maps has been reached"*
(`map.cpp:2844`). A instância não é criada. Não corrompe personagem nem banco —
mas o jogador leva um "não" sem explicação.

### As duas saídas, em ordem de custo

1. **Podar `conf/maps_athena.conf`.** Libera slot 1:1, não exige recompilar, e
   já há precedente no arquivo (os `tra_fild` e os quatro `1@jor*`/`1@iwp`/
   `1@whl` desligados). Carregamos 1258 mapas de episódios que em boa parte não
   usamos.
2. **Subir `MAX_MAP_PER_SERVER`.** O teto seguro é **9999**, e não é chute: o
   `#error` em `instance.cpp:803` marca exatamente esse limite, porque o nome do
   mapa clonado é montado como `%04u#%04u` (`instance_generate_mapname`) e só
   cabem 4 dígitos de cada lado em `MAP_NAME_LENGTH`. Exige recompilar o
   map-server.

### O que NÃO é gargalo — medido, não estimado

| Recurso | Veredito | Por quê |
|---|---|---|
| **Banco** | **zero** | `src/map/instance.cpp` não tem uma única chamada SQL. Instância vive só em memória (`instances`, um `unordered_map`). O único vestígio no banco é `char.last_instanceid`, um `int` (`sql-files/main.sql:262`) |
| **Memória** | desprezível | mediana **0,20 MB** por rodada; média 0,24; a maior (Endless Tower, 6 mapas) 1,51 MB. Mil jogadores em instância não passam de ~50 MB de células |
| **CPU** | neutra | mapa vazio não custa. Instância é *isolamento*, não trabalho novo — o custo continua proporcional a jogador e mob ativo, como em qualquer mapa |

A conta de memória por clone, para refazer: `cell` = `xs·ys·2` bytes
(`struct mapcell` são 2 bytes com `CELL_NOSTACK` desligado —
`src/config/core.hpp:31`), mais `block` e `block_mob`, cada um
`(xs/8)·(ys/8)·8` bytes. **Não inclui mobs nem NPCs da rodada**, que somam por
cima e não foram medidos.
