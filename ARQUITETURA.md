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
| 4b | `spriterobeid.lub` + `spriterobename.lub` | o slot de manto, **se for manto e novo** | **não existe** — ver `PENDENCIAS.md` §4 |
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

E a camada 4b não tem ferramenta: manto cujo `View` esteja fora das 120 entradas
da nossa `spriterobeid.lub` **não desenha, e arte nenhuma resolve**. O
`instala_manto.py` recusa esse caso em vez de copiar centenas de arquivos que o
cliente nunca vai procurar.

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
e as tabelas de `sql-files/guerra_arena_pvp.sql`. Sem as tabelas, o `query_sql`
falha e ninguém pontua — mas o anúncio de morte continua saindo, e é esse o
sintoma que aparece primeiro.

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

### Uma tradução de NPC vive em 2 lugares

O catálogo (`npc/guerra/traducao/*.cat`) é a **fonte**; o arquivo `.txt` do
rAthena é o **resultado**, reescrito por `traduz_npcs.py`. Editar o `.txt` à mão
é perder o trabalho na próxima passada. Grupos hoje: `campal`, `cidades`,
`classe1`, `classe2`, `glossario`, `guerra`, `kafra`, `novico`, `pvp`, `servico`.

### Uma placa sobre a cabeça de NPC

`src/custom/placa_de_venda.hpp` + duas linhas em `src/map/clif.cpp` + o comando
de script `placadevenda` (`src/custom/script.inc`). **Exige recompilar.** É o
único caso em que tocamos `src/map/`, e o porquê está no cabeçalho do `.hpp`.

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
