# Guerra do Emperium — guia de trabalho

Servidor privado de Ragnarok Online: rAthena vendorizado + cliente kRO
2021-11-03 traduzido para PT-BR.

**FASE 1 desde 2026-08-16: o caminho até o jogador está inteiro.** A fase 0 era
o servidor de pé sem como chegar nele; agora as três pontes existem e são
nossas — o **site** entrega o instalador, o **instalador** entrega o jogo
(3,4 GB de um bucket com CDN), e o **Atualizador** entrega toda melhoria
seguinte. Nada mais depende de pasta do Google Drive, e nenhuma correção de
cliente fica presa nesta máquina.

O que muda no dia a dia: **agora existe gente do outro lado.** Toda entrega
passa a ter um destino, e escolher o errado falha em silêncio — a tabela que
decide está em `RECEITAS.md` §0, e é a primeira coisa a ler antes de entregar
qualquer coisa.

Este arquivo é o ponto de partida de toda sessão. Ele não conta história: diz
onde as coisas estão, o que não se pode fazer, e **qual documento ler** para a
tarefa em mãos. O histórico e o "por quê" de cada decisão vivem nos diários
(`PENDENCIAS.md`, `ferramentas/LEIAME.md`) — grandes de propósito, e a serem
lidos **por seção**, nunca inteiros.

---

## 1. O mapa — onde fica o quê

| O que | Onde | Versionado |
|---|---|---|
| Emulador (terceiros) | `rathena/` | sim |
| **Nossos NPCs** | `rathena/npc/guerra/` | sim |
| **Nossos itens/mobs/reputação** | `rathena/db/guerra/` | sim |
| **Nosso C++** | `rathena/src/custom/` | sim |
| **Nossa regra de jogo** (taxas) | `rathena/conf/guerra/` | sim |
| Config de máquina (senha, IP) | `rathena/conf/import/` | **não** |
| Ferramentas (Python 2.7) | `ferramentas/` | sim |
| **Cliente (DEV/HML)** | `C:\GuerraDoEmperium\cliente\` | **não** |
| Override do cliente | `C:\GuerraDoEmperium\cliente\data\` | **não** |
| **O Atualizador** (patcher, em Go) | `patcher/` | sim |
| Registro dos patches publicados | `patcher/patches.txt` | sim |
| Os `.zip` de patch | `C:\GuerraDoEmperium\patches\` | **não** |
| Registro da BASE (primeiro download) | `patcher/base.txt` | sim |
| Os pedaços da base | `C:\GuerraDoEmperium\instalador\` | **não** |
| A chave do bucket | `C:\GuerraDoEmperium\spaces.env` | **não** |

**O cliente inteiro está fora do git.** Toda alteração nele (arte, `itemInfo.lua`,
`.lub`, `.bson`, mapas) é irreproduzível a partir do repositório — só existe nesta
máquina. Fazer backup antes de sobrescrever, sempre.

**E desde 2026-08-16 esse cliente é o de DEV/HML:** os dois `clientinfo` dele
apontam para `127.0.0.1`, o servidor local desta máquina. **Produção se testa
noutra pasta**, instalada pelo instalador como um jogador faria — decisão do
dono, e é o que separa "funciona aqui" de "funciona para quem baixou".

**Trocar de lado é `python ferramentas/aponta_cliente.py --dev` (ou
`--producao`); sem argumento ele só diz para onde os dois apontam hoje.** São
dois xml (`data\clientinfo.xml` e `data\sclientinfo.xml`, este último é o que
vale — §5) e **dois campos em cada**: o `<address>` e o `<admin>`, que é a conta
que ganha o visual de GM (2000000 aqui, 2000004 lá). Trocar só o endereço deixa
o GM sem visual do outro lado. As duas ferramentas de empacotamento **recusam**
cliente apontado para local, e é a única coisa que impede um pacote inteiro,
correto e inútil.

**O que desaponta esse cliente sozinho é o Atualizador** — há um `Jogar.exe`
naquela pasta, e patch que leve os `clientinfo` reaponta tudo para produção sem
avisar. Ver §5. Para jogar no local, abrir pelo `GuerraDoEmperium.exe`.

## 2. A lei da customização

**Tudo que é nosso mora em pasta própria; tocamos arquivo do rAthena só para
apontar para ela.**

O `rathena/` foi vendorizado **sem o histórico do upstream**. Customização
espalhada fica indistinguível de código de terceiros num `git diff`, e trazer
correção do rAthena vira arqueologia.

Os únicos enxertos permitidos em arquivo do rAthena, e os que existem hoje:

| Arquivo do rAthena | Enxerto |
|---|---|
| `npc/scripts_custom.conf` | uma linha `import: npc/guerra/scripts_guerra.conf` |
| `npc/barters.yml` | um `- Path: npc/guerra/barters_guerra.yml` no rodapé |
| `conf/battle_athena.conf` | uma linha `import: conf/guerra/battle_guerra.txt` |
| `conf/char_athena.conf` | uma linha `import: conf/guerra/char_guerra.txt` (nome de personagem com acento) |
| `conf/inter_athena.conf` | uma linha `import: conf/guerra/inter_guerra.txt` (`default_codepage: latin1`) |
| `conf/login_athena.conf` | uma linha `import: conf/guerra/login_guerra.txt` (`use_MD5_passwords: yes`) |
| `conf/maps_athena.conf` | uma linha `import: conf/guerra/mapas_guerra.txt` no rodapé — os mapas que o vendor conhece e **não** carrega. Hoje só `force_map1`, `force_map2` e `force_map3`, os três andares do Labirinto das Valquírias, que o rAthena traz **comentados** nas linhas 19–21 daquele arquivo. Funciona porque o `map_config_read` (`src/map/map.cpp:4166` e `:4206`) trata `map:` e `import:` no mesmo laço. **Não descomentar a linha do vendor no lugar disto:** descomentário morre na próxima atualização do rAthena, calado, e o sintoma aparece longe — o servidor sobe, o NPC carrega, e o `warp` nasce num mapa `-1` **sem uma linha de erro**, porque o `npc_parse_warp` só reclama do destino e nunca da origem (`npc.cpp:3906`). Quem denuncia é o `npc_parse_mapflag`, com *Unknown map* — e só se houver mapflag |
| `conf/groups.yml` | um `- Path: conf/guerra/groups_guerra.yml` no rodapé, **antes** do `conf/import/groups.yml` que já estava lá (permissão de comando por grupo — hoje o `@autoloot` e irmãos para o grupo 0). Funciona por merge: o `parseBodyNode` procura o `Id` antes de criar (`src/map/pc_groups.cpp:74`), e grupo que já existe recebe os campos por cima — por isso o nosso arquivo não repete `Name` nem `Level` |
| `db/item_combos.yml`, `db/re/reputation.yml`, `db/re/reputation_group.yml`, `db/attendance.yml`, `db/refine.yml`, `db/pet_db.yml` | um `- Path: db/guerra/...` no rodapé de cada. O do `pet_db` entrou em 2026-08-26 com a Anomalia Dimensional e aponta para `db/guerra/pet_db.yml`, hoje com um pet só — o Freeoni, que o rAthena traz **comentado** dos dois lados (a entrada de pet e o mob `PHREEONI2`, Id 20425). **Não existe `@reloadpetdb`:** mexer ali é reiniciar o map-server |
| `db/re/item_db.yml` | **três** `- Path:` no rodapé, nesta ordem, e a ordem é a regra — cada um tem a última palavra sobre um campo. `db/guerra/item_db.yml` é o nosso, escrito à mão (itens próprios e overrides de campo). `db/guerra/item_db_indestrutivel.yml` é **gerado** por `ferramentas/marca_indestrutiveis.py` e repete o `Script:` inteiro de 27 itens com um `bonus bUnbreakable<slot>` a mais — sem ele a peça que a descrição promete indestrutível quebra (§4.19). `db/guerra/item_db_lojas.yml` é **gerado** por `ferramentas/zera_revenda_das_lojas.py` e põe `Buy: 1` em todo item de vitrine de Prontera (§4.16) |
| `db/re/mob_db.yml` | **três** `- Path:` no rodapé, não um. `db/guerra/mob_db.yml` é o nome em português, **gerado** por `traduz_ptbr.py monstros` (reescreve o arquivo inteiro; editar à mão morre no próximo `--extrair`); `db/guerra/mob_db_guerra.yml` é o segundo, escrito à mão, para ajuste pontual de campo de combate (ex.: `Attack` de um guardião fora de castelo — ver o cabeçalho do arquivo e `PENDENCIAS.md` §1s); `db/guerra/mob_db_sombria.yml` é o terceiro, **gerado** por `ferramentas/monta_mobs_da_sombria.py`, e traz os **catorze monstros da Glast Heim Sombria** (ids 3139..3152), que o vendor tem só como placeholder comentado e que o rAthena **nunca implementou, nem no master** |
| `db/re/quest_db.yml` | o **`Footer: Imports:` inteiro** — aquele arquivo não tinha rodapé nenhum. Seguro porque o `parseImports` mora no `YamlDatabase` (`src/common/database.cpp:176`), não no leitor de quest: vale para todo banco em YAML, e o mesmo caminho serve para qualquer `db/re/*.yml` que ainda não tenha rodapé |
| `db/re/job_stats.yml` | o **`Footer: Imports:` inteiro**, com **dois** `- Path:`, e o primeiro deles não é nosso. `db/re/job_outfits.yml` é arquivo do **próprio rAthena** e estava **órfão**: o `JobDatabase::getDefaultLocation()` (`src/map/pc.cpp:13819`) aponta só para o `job_stats.yml`, então os treze `AlternateOutfits` (o "Roupa alternativa" do estilista) não eram lidos por ninguém e `job->alternate_outfits` ficava vazio para todo trabalho. `db/guerra/job_estilo_de_corpo.yml` é nosso e declara os ids 4332..4344 num `Jobs:`, porque a guarda `job_db.exists()` do `pc_changelook` reprova todo valor de estilo de corpo sem eles (§5). Sem os dois, o Cupom de Roupa some sem trocar nada |
| `db/re/map_drops.yml` | o **`Footer: Imports:` inteiro**, pelo mesmo caminho do `quest_db.yml` acima — aquele arquivo também não tinha rodapé. Aponta para `db/guerra/map_drops.yml`, **gerado** por `ferramentas/escala_drops_de_mapa.py` (drop de mapa não passa pela taxa do servidor — ver §5) |
| `src/map/clif.cpp` | **três** includes de `src/custom/` + **quatro** chamadas, comentadas no arquivo: `placa_de_venda_mostra`, o teto de refino nas duas pontas da janela de refino, e `brilho_da_carta` no `clif_dropflooritem` (o pilar de luz e o som quando cai carta — `src/custom/brilho_da_carta.hpp`) |
| `src/map/battle.cpp` | **dois** includes de `src/custom/` + **sete** chamadas, todas comentadas no arquivo. Duas de `reducao_de_dano.hpp`: `reducao_alcanca_percentatk` (no bloco "Card Fix for target" — põe o `percentAtk` na redução, sem ela `bonus bAtkRate` fura toda resistência) e `reducao_piso` (dentro do `APPLY_CARDFIX` — teto configurável, 99% hoje, no lugar do `max(0, …)` que deixa a redução zerar o dano). Cinco de `reducao_geral.hpp`, a redução geral de 80% (`REDUCAO-DE-DANO.md` §1c): quatro de `reducao_pvp` — três dentro do `battle_calc_damage` (o caminho normal + as duas saídas antecipadas de habilidade que pula tudo) e uma no `battle_calc_return_damage`, para o reflexo — e **uma que SUBSTITUI linha do rAthena**, a única do projeto: dentro do `battle_calc_gvg_damage`, `reducao_isenta_habilidade(skill_id)` no lugar do `skill_get_inf2(skill_id, INF2_IGNOREGVGREDUCTION)`. **Substituição não sobrevive a merge por si** — se `INF2_IGNOREGVGREDUCTION` reaparecer ali depois de atualizar o vendor, o enxerto morreu calado |
| `src/map/status.cpp` | um include de `src/custom/` + **duas** chamadas, comentadas no arquivo, as duas de `guardiao_do_castelo.hpp` (a escala do guardião pela defesa do castelo): `guardiao_tem_escala` num `flag\|=4` **acrescentado** ao lado do `guardup_lv` do rAthena — não substitui nada, e só existe porque sem flag nenhuma o `status_calc_mob_` sai antes, libera o `md->base_status` e passaria a escrever no status **compartilhado** do `mob_db`; e `guardiao_aplica_escala` no fim da mesma função, depois do bloco "Strengthen Guardians" e **antes** do `memcpy` final |
| `npc/scripts_guild.conf` | duas coisas. **(a)** 19 das 20 linhas de castelo da Guerra do Emperium 1 comentadas — só o `prtg_cas01.txt` (Kriemhild) fica. É o que tira Emperium, Kafra, Gerente e bandeiras dos castelos-museu de uma vez, e é também **o que limita a guerra ao Kriemhild**: sem o arquivo do castelo não há `Agit#<castelo>`, logo não nasce Emperium. Ver `npc/guerra/guardioes_dos_castelos.txt`. **Levou 279 bandeiras junto** — devolvidas por `npc/guerra/bandeiras_do_feudo.txt`, todas hasteando o dono do Kriemhild. **(b)** o `agit_controller.txt` comentado, substituído por `npc/guerra/horario_da_guerra.txt` (quinta 20–22, domingo 18–20, horário de Brasília). Nunca deixar os dois ligados |
| `src/map/pc.cpp` | um include de `src/custom/` + **uma** chamada, comentada no arquivo: `estilo_de_corpo_resolve` no topo do `case LOOK_BODY2:` do `pc_changelook`, **antes** do `job_db.exists`. Acréscimo, não substituição. Traduz o valor legado 0/1 que o `db/re/stylist.yml` ainda manda para o Id do trabalho do visual alternativo — sem ela a UI de estilista come o Cupom de Roupa e não muda nada (`src/custom/estilo_de_corpo.hpp`) |
| `src/map/mob.cpp` | um include de `src/custom/` + **uma** chamada, comentada no arquivo: `habilidade_de_monstro_proibida` no topo do laço do `mobskill_use`, **antes** do teste de recarga — monstro em mapa listado se comporta como se não tivesse aquela linha do `mob_skill_db`. Acréscimo, não substituição. Hoje a tabela tem uma entrada só: Instinto de Defesa (`ST_REJECTSWORD`) no Corredor Fantasma (`vis_h01`), que refletia 50% do dano do jogador sem passar por redução nenhuma (`src/custom/habilidade_proibida.hpp`) |
| `src/map/skill.cpp` | **dois** includes de `src/custom/` + **uma** chamada (um `if` com duas funções), comentada no arquivo, dentro do `skill_get_requirement`, na linha seguinte à do Magic Gear Fuel. `tinta_infinita_dispensa` zera o requisito de **Tinta para Parede** (6123) para quem carrega a **Tinta para Parede Infinita** (30993); `pincel_do_infinito_dispensa` zera os de **Pincel de Maquiagem** (6121), **Pincel de Grafite** (6122) e **Tinta para Pele** (6120) para quem carrega o **Pincel do Infinito** (30992). Com o requisito zerado a habilidade passa na checagem **e** nada é consumido. Acréscimo, não substituição, e usa a mesma forma que o rAthena já usa duas linhas acima (`req.itemid[i] = req.amount[i] = 0`). **Um ponto só basta porque o `skill_get_requirement` é a fonte única dos três caminhos** — `skill_check_condition_castbegin` (é quem recusa o lance), `..._castend` e `skill_consume_requirement` (é quem apaga o item). E ele resolve **ferramenta** (`Amount: 0`) junto com insumo: o castbegin reprova por `index[i] < 0` antes de olhar a quantidade, então pincel que falta na mochila derruba a habilidade igual a tinta que falta. Alcança as treze habilidades de Trapaceiro/Renegado envolvidas porque a condição olha o **insumo** e não uma lista de habilidades (`src/custom/tinta_infinita.hpp`, `src/custom/pincel_do_infinito.hpp`) |
| `rathena/.gitignore` | duas coisas. **(a)** `!/src/custom/` — o upstream ignora essa pasta inteira. **(b)** `/db/import` virou **`/db/import/*`** mais um `!/db/import/mob_skill_db.txt`: as habilidades dos monstros da Glast Heim Sombria só podem morar ali, porque o `mob_skill_db.txt` não é YAML (não tem rodapé de import) e o `mob_readskilldb` (`src/map/mob.cpp:7184`) lê de `db/re/` e `db/import/` e mais nada. **A barra-asterisco é o que faz funcionar** — pasta excluída o git nem abre, então negar um arquivo dentro dela não teria efeito; excluir o CONTEÚDO deixa a pasta visível e a negação passa a valer. Os outros ~60 arquivos de `db/import` continuam fora do git, que é onde devem ficar |

**Qualquer outro diff em `rathena/` fora de `npc/guerra`, `db/guerra`,
`src/custom`, `conf/guerra` é alteração em código de terceiros e precisa de
justificativa.** A receita para não editar arquivo do rAthena é sempre a mesma:
`disablenpc` no original + duplicata nossa (ver `portais_do_navio.txt`,
`armazem_do_cla.txt`, `arena_de_combate.txt`).

**`rathena/npc/guerra/scripts_guerra.conf` é o índice narrado dos nossos NPCs** —
cada linha vem com um parágrafo dizendo o que o NPC faz, onde fica e o que quebra
se for desligado. **Leia esse arquivo antes de mexer em qualquer conteúdo de
jogo**; ele responde a maioria das perguntas de "o que já existe?" sozinho.
Ligar/desligar um NPC = comentar uma linha ali.

## 3. Rodar o servidor

```
python ferramentas/servidor.py status      # o que está no ar E o que quebra sem cada peça
python ferramentas/servidor.py subir       # idempotente, na ordem certa
python ferramentas/servidor.py reiniciar
```

**São QUATRO servidores**, não três: `login` (6900), `char` (6121), `map` (5121)
e **`web` (8888)** — com PACKETVER > 20200300 é o web-server que recebe o emblema
de clã por HTTP, e sem ele a falha é **completamente calada**. Mais MariaDB (3306).
Nunca subir os `.bat` um a um.

Erro de script de NPC aparece na janela do map-server e em `log/map-msg_log.log`
(config não versionada — some em clone limpo).

### Qual recarregador para qual mudança

Errar o comando faz a mudança parecer que não pegou.

| Mudou | Comando |
|---|---|
| Script de NPC | `@reloadscript` |
| `db/` (item, conjunto) | `@reloaditemdb` — pega item **e** conjunto |
| `npc/guerra/barters_guerra.yml` (loja de troca) | `@reloadbarterdb` — **não** é `@reloadscript` |
| `conf/guerra/`, `battle_athena.conf` | `@reloadbattleconf` (chama `mob_reload()` sozinho se taxa de item mudou) |
| `conf/guerra/groups_guerra.yml` (permissão de comando) | `@reloadatcommand` — chama `pc_groups_reload()` (`src/map/atcommand.cpp:4422`). **Não** é `@reloadbattleconf` nem `@reloadscript` |
| `db/guerra/reputation.yml` | **reiniciar o map-server** — `reputation_db.load()` só roda no `do_init_pc` |
| `db/guerra/pet_db.yml` (pets) | **reiniciar o map-server** — não existe `@reloadpetdb`; o `pet_db.load()` só roda no `do_init_pet`. Login e char podem ficar de pé |
| `db/guerra/job_estilo_de_corpo.yml`, `db/re/job_outfits.yml` (estilo de corpo) | `@reloadpcdb` — chama `pc_readdb()` (`src/map/atcommand.cpp:4490`), que faz `job_db.clear()` + `job_db.load()` e segue o rodapé. **Não** exige reiniciar, e **não** é `@reloaditemdb` nem `@reloadscript` |
| `db/guerra/refine.yml`, `db/guerra/refine_evento.yml` | **reiniciar o map-server** — não existe `@reloadrefinedb`. Vale também para ligar/desligar o Evento de Refino, que é comentar a linha `- Path: db/guerra/refine_evento.yml` no rodapé de `db/refine.yml` |
| `db/guerra/attendance.yml` | `@reloadattendancedb` — mas o cliente **não** recarrega a metade dele |
| `db/guerra/quest_db.yml` (missões da Ordem) | `@reloadquestdb` — e **não** é `@reloadscript`. O recado e a recompensa de cada missão moram no NPC, o alvo mora aqui; mudar os dois exige os dois comandos. **Missão nova exige também `ferramentas/monta_missoes_da_ordem.py` e reabrir o cliente** — sem a entrada de lá, pegar a missão derruba o cliente (§5) |
| `db/guerra/map_drops.yml` (drop de mapa) | `@reloadmobdb` — é ele que chama `mob_reload()`, que refaz o `map_drop_db` (`src/map/mob.cpp:7216`). **Não** é `@reloaditemdb` nem `@reloadscript` |
| `db/guerra/instance_db.yml` (nome de instância) | `@reloadinstancedb` — existe, e **não** exige reiniciar. O nome é chave: o `instance_create` resolve por string, então rodar este **antes** do `@reloadscript` quando os dois lados mudaram juntos |
| `src/` | recompilar (VS 2022 Community, já instalado) |
| `itemInfo.lua` e afins no cliente | **fechar e reabrir o cliente** — só lido na inicialização |
| Exe do cliente (fonte, charset) | **fechar o cliente ANTES de gravar** — o exe fica travado enquanto roda, e o que já está aberto segue na cópia em memória |

Na dúvida, reiniciar o map-server resolve tudo do lado servidor; login e char
podem ficar de pé. **Derrubar o servidor por causa de `db/` é desnecessário.**

`@rates` in-game imprime as taxas carregadas em memória. "Unknown Command" **não**
é falta de permissão.

## 4. Regras que não se negociam

1. **Texto de jogo é cp1252, nunca UTF-8.** Acento sim; UTF-8 quebra. Quem faz o
   cliente desenhar byte acentuado é o patch `AlwaysAscii`. Vale para `.txt` de
   NPC, `itemInfo.lua` (ANSI/CP949), `.lub`, **e o `db/guerra/item_db.yml`**.
   Estes `.md` são UTF-8 — a regra é para texto que o **jogo** lê.
   **Escrever é o passo perigoso, não ler:** editor e ferramenta de edição
   gravam UTF-8 por padrão, e o estrago é calado. Depois de gerar um desses
   arquivos, converter e conferir — `python -c "open(p,'wb').write(open(p,'rb')
   .read().decode('utf-8').encode('cp1252'))"`, e então reler em cp1252 para
   ver os acentos certos. Ver §5, entrada do U+FFFD.
2. **Só entra na loja item com nome em português.** Inglês se detecta pela
   ausência no bRO; coreano por byte. Um critério não serve para o outro.
3. **Quando falta algo, traz-se do bRO** — a instalação do Ragnarok Brazil desta
   máquina é a fonte de arte, nome PT e descrição. Não inventar.
4. **Validar arte antes de pôr item na loja.** Item sem arte entrega caixa de erro
   ao jogador. `valida_visual.py` tem que dar 0.
5. **Mesclar por chave, nunca trocar o arquivo do bRO por cima** — vale para toda
   a tradução.
6. **Conferir se o mapa existe no GRF antes de teletransportar.** Mapa do rAthena
   pós-2021 sem `.rsw` no GRF derruba o cliente **e prende o personagem lá**.
7. **A conta de teste (grupo 99) ignora `NoDrop` e as outras seis travas** —
   testar restrição de item nela sempre dá falso negativo.
8. **`grep` em `npc/` não prova que um item é inútil** — a UI do cliente consome
   item direto no C++, por tabela em `db/` (ex.: cupom de estilista,
   `db/re/stylist.yml`).
   **E o item que TODO personagem novo recebe também não está em `npc/`:** ele
   mora no `start_items` do `conf/char_athena.conf` (linha 124 hoje —
   `1201,1,2:2301,1,16:23484,1,0`, ou seja Faca, Chapéu de Aprendiz e a Caixa
   de Primeiros Socorros (5)). Procurar o ID em `npc/` devolve zero, o que faz
   um item de primeira hora parecer órfão. Achado em 2026-08-28: o relato
   chegou pelo **23485**, que é só o que sobra na mochila depois de abrir a
   caixa de verdade.
9. **Sistema de UI do cliente tem metade da configuração NO CLIENTE.** O
   servidor manda o estado (um contador, um índice), não a lista. Mexer só no
   `db/` deixa as duas metades divergentes, e a divergência **não dá erro** — a
   janela mostra uma coisa e o servidor entrega outra. Caso vivo: o Logue e
   Ganhe (`db/guerra/attendance.yml` + `cliente\System\CheckAttendance.lub`),
   por isso gerado dos dois lados por `ferramentas/monta_logue_e_ganhe.py`.
   **Segundo caso vivo: o nome do item na janela de troca (barter).** O pacote
   leva só o ID (`clif.cpp:23225`) — quem desenha o nome é o `itemInfo.lua` do
   cliente. Menu de `select` usa `getitemname()` e lê o servidor; janela nativa,
   não. Nome errado numa loja de troca **não** se conserta com o
   `nomes_pt_item_db.py`.
   **Terceiro caso vivo, e o único que NÃO falha calado: a janela de
   missões.** Quest que o cliente não conhece **derruba o cliente**, não
   aparece sem título — ver §5. As missões da Ordem são geradas dos dois
   lados por `ferramentas/monta_missoes_da_ordem.py`.
   **Quarto caso vivo: a COVA do item.** Quem decide se a carta *entra* é o
   `Slots:` do `item_db`; quem desenha o `[1]` no nome é o `slotCount` do
   `itemInfo.lua`, e o cliente não pergunta nada ao servidor. Mexer só no
   `db/` deixa um item que **aceita carta e não parece aceitar** — o jogador
   não tenta, e nada dá erro. A segunda metade é gerada da primeira por
   `ferramentas/ajusta_covas_do_cliente.py`, e como mora no cliente **só
   chega ao jogador por patch** (§4.18). Caso vivo: as 15 Armas Brutais,
   2026-09-03.
10. **Loja que cobra em ITEM é `barter`, não `itemshop`.** São os dois tipos que
    parecem servir, e só um funciona aqui: o `itemshop` passa a moeda por
    `pc_can_sell_item`, que **recusa item `NoSell`** enquanto
    `allow_bound_sell` for `0x0` (o nosso padrão) — a loja abre e a compra
    falha, com a moeda na mão do jogador. O `barter` não faz essa checagem. Só
    ele abre a janela de troca com ícone de moeda por linha; `itemshop` e
    `pointshop` caem no `clif_cashshop_show`, que é outra janela.
11. **Menu de `select` e tabela de dados indexados pelo mesmo número saem da
    MESMA fonte.** Se o menu é uma string escrita à mão e o destino é um
    `setarray` escrito à parte, as duas ordens divergem mais cedo ou mais
    tarde — e a divergência **não dá erro**: o NPC funciona, cobra, entrega, e
    entrega a coisa errada. O certo é guardar os rótulos num array e **montar
    o menu num laço** a partir dele, mais um `getarraysize` que compare as
    colunas e grite com `debugmes`. Caso vivo, e caro: em 2026-08-08 o
    Teleportador da Ordem levou ao lugar errado nos **catorze** destinos —
    "Batalha dos Orcs" ia para a Vila dos Porings — porque o menu seguia a
    ordem das placas e os arrays seguiam a ordem em que os mapas tinham sido
    validados. **O cabeçalho do arquivo afirmava que as duas ordens eram a
    mesma. Comentário não é trava.**
12. **Ao traduzir diálogo, nome de habilidade, item, mapa e monstro sai da
    tabela que o JOGO lê — inclusive quando ela não traduziu.** As quatro
    fontes: `skillinfolist.lub` (habilidade), `itemInfo.lua` do nosso cliente
    (item), `data\mapnametable.txt` (mapa) e `db/guerra/mob_db.yml` (monstro,
    gerado do `navi_mob_br.lub` do bRO). A regra vale **nos dois sentidos**:
    `Mind Blaster` fica em inglês na Torre do Demônio porque é assim que o
    cliente o mostra, e `Explosive Powder` vira **Pó Explosivo** e não
    "Pólvora" porque é assim que o `itemInfo.lua` chama o item 6213. Nome que
    não está em tabela nenhuma **fica em inglês** — inventar nome de lugar é
    o que a regra 3 proíbe (caso vivo: `Ash Vacuum`).

    Duas consequências que já custaram retrabalho:
    - **Nome de criatura se traduz**, mesmo que o bicho apareça em inglês na
      tela. Dentro de instância o nome que flutua vem do 4º argumento do
      `monster` do próprio script, que **não** entra no catálogo — então a
      missão em português convive com um alvo rotulado em inglês. Aceita-se:
      meia frase em inglês é pior, e é o que a regra de "só aplicar grupo
      inteiro" existe para evitar.
    - **Linha `+` vazia num `.cat` não é dívida.** Nome de mapa, label de
      evento, nome único de NPC, `.bmp` de cutin, código de cor e pontuação
      solta ficam em branco de propósito. O `--estado` conta esses como não
      feitos, então **86% num grupo de instância quer dizer completo**.
13. **Rodar `--extrair` ANTES de traduzir um grupo, sempre — mesmo com
    catálogo commitado.** Catálogo velho abre, tem conteúdo, aplica sem recusa
    e marca 100%; o que falta nele simplesmente não existe para a ferramenta.
    Em 2026-08-09 onze dos dezesseis catálogos de instância estavam sem os
    `mapannounce`/`unittalk` (o `vermes` tinha 331 pares onde havia 453), e
    quatro grupos foram dados por prontos antes de o buraco aparecer.
14. **Em que loja um item entra é decidido pelo `Locations:` do `item_db`,
    nunca pelo nome nem pela lista em que ele foi pedido.** As doze lojas do
    quarteirão de Prontera são pares: uma de VISUAL e uma de EQUIPAMENTO por
    slot — Manteleiro/Capeiro (capa), Adereceiro/Ocleiro (cabeça meio), e
    assim por diante. `Costume_Garment` vai para a de visual, a 1 zeny;
    `Garment` com Defense, peso e refino vai para a de equipamento. Um pedido
    que diga "Capa" pode querer as duas, e em 2026-08-09 queria: onze
    cosméticos e três capas com cova, na mesma lista. **Ler a lista e não o
    `Locations:` põe equipamento de status numa vitrine de 1 zeny.**

    **E o `Locations:` do nosso rAthena não é a última palavra: o do bRO
    é.** São dois desacordos diferentes e o remédio de cada um é outro. Se o
    pedido discorda do nosso `item_db` mas **concorda com a descrição do
    bRO** (`estado_item.py --id <n> --descricao`, linha "Equipa em:"), quem
    está errado é o nosso vendor — corrige-se por override, com `false`
    explícito no slot velho, e a peça muda de loja. Se o bRO e o nosso
    `item_db` **concordam entre si** e só o pedido destoa, a peça vai para a
    loja do `Locations:` e a divergência é levantada por escrito. Em
    2026-08-12 a mesma lista trouxe os dois casos: Cachecol Glorioso e
    Coleira do Vassalo eram erro nosso (dois overrides), Gata Branca e Manto
    do Herói eram engano do pedido (duas ressalvas).

    O `estado_item.py --id <n>` responde isso numa linha, e a resposta pode
    contrariar o nome. Os dois casos vivos, os dois na fileira de visual:
    a **Piscadela de Freya** é de meio e o nosso rAthena a dava como baixo
    (2026-08-07, custou um override no `item_db`); a **Máscara de Minorous**
    é `Costume_Head_Low`/`_Mid` e foi pedida na lista de topo (2026-08-09,
    não custou nada — o `Locations:` já estava certo, faltava lê-lo). As
    duas acabaram no Adereceiro.

    **Divergência entre o pedido e o `item_db` é para levantar na entrega,
    não para resolver sozinho.** Escrever no comentário da loja e dizer ao
    dono; a Minorous foi entregue como pedida, com a ressalva por escrito, e
    a mudança de loja veio dele na volta. O que não pode é a divergência
    ficar só na cabeça de quem editou.
15. **Para fechar célula, `setwall` — nunca `setcell`.** São os dois que
    parecem servir, e a diferença é o cliente. O `setcell` muda a célula só do
    lado do servidor: o cliente continua achando que dá para andar ali, e o
    próprio `doc/script_commands.txt` avisa que *"the wall will not be shown
    nor known client-side, which may cause movement problems"*. O `setwall`
    faz o mesmo bloqueio e ainda manda `clif_changemapcell`
    (`map.cpp:3509`), com o `map_iwall_get` reenviando para quem entrar no
    mapa depois (`clif.cpp:11098`) — as duas metades ficam de acordo. Ele
    ainda vem com `delwall` (desfaz exato) e `checkwall` (testa), que são o
    que torna um `OnInit` idempotente.
    **Um cuidado ao desfazer:** o `map_iwall_remove` devolve a célula para
    andável+atirável **sem consultar o mapa original** (`map.cpp:3553`) —
    `delwall` numa célula que já nascia bloqueada abre buraco no cenário.
    E lembrar que **modelo de `.rsw` não bloqueia nada sozinho**: o override
    de mapa não toca o `.gat`, então móvel plantado é atravessável até que
    alguém escreva o `setwall`. As duas metades estão no `ARQUITETURA.md` §4.
16. **Item vendido em loja de Prontera vale 1 zeny nas DUAS pontas — na
    vitrine e na revenda.** Decisão do dono em 2026-08-17: *"itens que são
    vendidos nas lojas de Prontera devem ter valor 1 zeny pra evitar
    criação de dinheiro infinito"*. A vitrine já estava a 1; o que faltava
    era a outra ponta, e é ela que gera dinheiro.

    **O dinheiro infinito nunca esteve no preço da prateleira — está na
    REVENDA.** Comprar por 1 zeny e revender em **qualquer** NPC pelo
    `Sell` do `item_db` (que vale `Buy/2` quando o item não declara o
    campo) rende a diferença, por clique, em laço. Medido em 2026-08-17:
    **918 dos 1603 itens** das 22 lojas dos três mercados davam lucro, e
    três não eram de 9 zeny — Tapa-Olho Ferido (19446) a **999.999 por
    clique**, Cópia de Gram (500009) a 249.999, Óculos_ (2204) a 1.999.

    **A trava é `Buy: 1` por override**, em `db/guerra/item_db_lojas.yml`,
    **gerado por `ferramentas/zera_revenda_das_lojas.py`**. Com `Buy`
    declarado e `Sell` não, o rAthena faz `value_sell = value_buy / 2` no
    fim do carregamento (`itemdb.cpp:1188`) — ou seja **zero**. Não se
    escreve `Sell: 0`: seria um segundo campo para divergir.

    **Ao pôr item novo em qualquer vitrine de Prontera, rodar o script** —
    sem ele o item nasce com o `Buy` do `item_db` e reabre o buraco,
    calado. O `--conferir` do mesmo script mede o lucro por clique loja a
    loja e é a trava de verdade.

    **Isso alcança TODA cópia do item no servidor, não só a que saiu da
    loja** — valor de item mora no `item_db`, não na instância. Carta que
    o jogador caçou também deixa de valer zeny no NPC. Era a saída
    considerada e **recusada** em 2026-08-12 por esse motivo; em
    2026-08-17 a decisão foi a contrária, com o número dos 918 na mão.

    Três consequências:
    - **A regra de 2026-08-12 está REVOGADA.** Ela dizia *"todo item que
      tiver valor de venda a gente vende com o valor de compra dele"*, e
      pôs seis peças fora do 1 zeny — o **Elmo de Aegir (18728)** a
      200.000 na frente delas. Viveu cinco dias. As seis voltaram para 1
      zeny. Não procurar por ela nos cabeçalhos: eles foram acertados.
    - **A Tranqueiras é a exceção, e continua sendo.** Ela vende a `-1`
      (o `Buy` do item, `npc.cpp:4146`), tem lucro por clique **zero**
      medido nos 55, e ficou de fora por decisão do dono no mesmo dia:
      `Buy: 1` nela derrubaria o Ouro (969) de 150.000 para 1 e daria a
      alquimia e as dez receitas de Runa de graça.
    - **`npc_parse_shop` deixa de reclamar.** O aviso `discounted buying
      price (1->0) is less than overcharged selling price` testa
      `value*0.75 < value_sell*1.24` (`npc.cpp:4153`); com a revenda em 0
      o lado direito zera e o aviso não sai para nenhuma das 22 lojas.
17. **Antes de mudar uma regra, conferir se ela EXISTE — o cabeçalho pode
    estar descrevendo uma que nunca foi escrita.** Cabeçalho longo é o que
    torna este projeto navegável, e é justamente por isso que ele é lido como
    se fosse o código: quem chega para mexer parte da descrição e edita ao
    lado dela. Quando os dois divergem, **nada denuncia** — não há teste, não
    há log, e o NPC funciona.

    Caso vivo, e de graça só porque apareceu na leitura: o
    `honra_de_combate.txt` prometia desde 2026-08-08 que *"quem cai abaixo de
    zero para de valer para o matador, mas continua sendo alvo: morrer ainda
    tira ponto dele"*, e o código tinha um `if (.@pontos_morto < .Piso) end;`
    que saltava **as duas** pontuações. A regra escrita nunca rodou. Em
    2026-08-13 o dono pediu exatamente aquele comportamento como novidade — e
    era, apesar de estar documentado havia cinco dias.

    Na prática: ao receber "mude X para Y", **ler o trecho que implementa X**
    e não só o parágrafo que o explica. Se os dois discordarem, o pedido
    provavelmente é sobre o que o código faz, não sobre o que o texto diz — e
    a divergência entra na entrega, por escrito. É a mesma família da §4.11
    ("comentário não é trava"), do outro lado: lá o comentário mentia sobre
    uma ordem, aqui sobre uma regra.
18. **Mudança de CLIENTE não chega ao jogador pelo deploy — precisa de
    patch.** O `implanta.sh` leva servidor: NPC, `db/`, `conf/`, `src/`. Tudo
    que mora em `C:\GuerraDoEmperium\cliente\` (arte, `.lub`, `itemInfo.lua`,
    sprite, exe, `AI_sakray\`) está numa cópia congelada na máquina de cada
    jogador, do dia em que ele baixou o cliente, e **só se move por
    `ferramentas/monta_patch.py` + `publica_patch.sh`** (`RECEITAS.md` §11).

    Falha calada e assimétrica: aqui funciona, e para o jogador não existe.
    Pior quando as duas metades andam juntas — item novo cujo nome vive no
    `itemInfo.lua` do cliente e cuja entrega vive no `item_db` do servidor
    aparece **sem nome** para quem não recebeu o patch, sem erro nenhum. É a
    §4.9 ("metade da configuração no cliente") um degrau acima: lá as duas
    metades divergem entre arquivos, aqui divergem entre máquinas.

    Na prática: ao terminar qualquer trabalho, perguntar **onde o arquivo
    mora**. Se o caminho começa em `C:\GuerraDoEmperium\cliente\`, o trabalho
    não acabou no `git commit`.

    **A tabela dos quatro destinos — servidor, patch, base e site — está em
    `RECEITAS.md` §0.** Desde a fase 1 (2026-08-16) ela é a primeira coisa a
    consultar antes de dar qualquer trabalho por entregue.

19. **Efeito que a descrição promete e o `Script:` não entrega é uma família
    inteira, não um item — e a que DESTRÓI equipamento é o "Indestrutível".**
    A descrição vem do `itemInfo.lua` do cliente (tradução do bRO), o efeito
    vem do `Script:` do nosso vendor, e os dois são revisões diferentes
    (§5, entrada da Capa do Comandante). No caso do indestrutível o desacordo
    não custa uns pontos de resistência: o jogador **perde a peça**.

    Não há campo de `item_db` nem flag para isso. O `skill_break_equip`
    (`src/map/skill.cpp:1944`) só poupa quem tem o bit em
    `sd->bonus.unbreakable_equip`, e esse bit **só** entra por
    `bonus bUnbreakable<slot>` rodando no `Script:` do próprio item
    (`src/map/pc.cpp:4262`). Quem quebra na prática são as habilidades de
    monstro `NPC_ARMORBRAKE`, `NPC_HELMBRAKE`, `NPC_SHIELDBRAKE` e
    `NPC_WEAPONBRAKER`.

    A trava é `ferramentas/marca_indestrutiveis.py`, que gera
    `db/guerra/item_db_indestrutivel.yml`. **Ao pôr item de equipamento novo
    em qualquer vitrine, rodar o script** — é o mesmo hábito da §4.16 e da
    mesma natureza: o `--conferir` mede e sai 1 se faltar. Medido em
    2026-08-18: 540 itens do cliente dizem "Indestrutível" e **27** não
    tinham o bônus, sete deles à venda em Prontera.

    Duas consequências que o script já trata e que não se deve desfazer à
    mão: o override **repete o `Script:` inteiro** (o `parseBodyNode`
    substitui o campo, não acrescenta — e `EquipScript:` não serve, porque o
    `status_calc_pc_` refaz os bônus do zero sem ele), e o bônus entra na
    **primeira** linha, porque script que termine em `if (cond)` sem chaves
    engoliria a linha seguinte.

    E o preço de o arquivo existir: enquanto ele estiver ligado, correção do
    rAthena no `Script:` daqueles 27 itens **não chega ao jogo**. Rodar o
    script de novo depois de atualizar o vendor.

20. **NUNCA reiniciar o servidor de PRODUÇÃO por conta própria — só o de
    DEV/HML.** Decisão do dono em 2026-08-22. Reiniciar em PRD derruba todo
    jogador conectado ali; recompilar/parar/subir o servidor **local** (os
    quatro de `ferramentas/servidor.py`) continua liberado sem perguntar,
    porque só afeta esta máquina. Produção só se reinicia com pedido
    explícito do dono, e o caminho para chegar nela de qualquer jeito é outra
    máquina (Mac, ver §9) — nada aqui deveria alcançá-la sozinho.
21. **Mecânica construída sobre número que o cliente NÃO MOSTRA precisa do
    retorno visual como parte da mecânica, não como acabamento.** O caso que
    estreou a regra: as Pedras Guardiãs da Anomalia Dimensional
    (2026-08-26) são curadas com magia de cura, e **o cliente de RO não
    desenha barra de vida de monstro**. Curar e não curar produziam a mesma
    tela — o número verde subia, e nada mais. O dono jogou e relatou: *"eu
    consegui curar, mas fiquei curando muito e não dava nada"*, *"não sabia
    se algum dia ia parar"*.

    **É pior do que não funcionar**, por dois motivos: do lado de cá tudo
    parece certo (o servidor executa, o log fica limpo, a leitura de código
    confirma), e do lado de lá o jogador não consegue nem descrever o
    defeito — porque não há defeito, há ausência de informação.

    Vale para qualquer coisa que o jogador não enxergue: HP de monstro,
    contador interno, progresso de coleta, tempo restante, chance
    acumulada. **A pergunta a fazer ao desenhar é "como ele sabe que está
    funcionando?"**, e se a resposta for "não sabe", falta código.

    As três camadas que resolveram, e cada uma responde uma pergunta
    diferente: a Pedra anuncia a própria porcentagem (`unittalk` +
    `specialeffect`) toda vez que o HP sobe — *"minha magia entrou?"*; o
    `mapannounce` do conjunto a cada 10% — *"estou perto do fim?"*; e uma
    opção no NPC que lista os quatro números — *"qual é o estado exato?"*.
    Mais um `debugmes` periódico para o console, que é a única sonda que
    responde **do lado do servidor** (e é `debugmes`, não `ShowInfo`, pela
    §5).

    Da mesma família da §4.17, do outro lado: lá o texto prometia o que o
    código não fazia; aqui o código faz e não conta a ninguém.
22. **Um `mes` por PARÁGRAFO, nunca um `mes` por linha de tela — quem quebra
    a linha é o cliente.** O `clif_scriptmes` manda a string crua e a janela
    dobra o texto pela própria largura; um parágrafo já quebrado no script
    aparece quebrado **duas vezes**, e as sobras curtas caem no meio das
    frases. Escrever `mes` com 60 caracteres "para caber" é reproduzir à mão
    um trabalho que o cliente refaz por cima.

    O reflexo que produz isso é o de quem edita código: a linha do arquivo
    fica bonita, e é justamente por isso que o defeito passa na revisão —
    **só aparece na tela do jogador**. Reclamado pelo dono em 2026-08-28,
    e não pela primeira vez.

    Na prática: a frase inteira num `mes` só, por mais longa que fique no
    arquivo. Quebra de verdade se pede com um `mes` novo, e é aí que ela
    passa a significar alguma coisa — parágrafo, item de lista, linha de
    tabela. Vale para `mes`, `npctalk`, `unittalk` e `mapannounce`.

    Duas ressalvas que continuam valendo, e não são contradição:
    - **`mes` que começa com ESPAÇO não abre linha nova, cola na anterior**
      (§5). Para recuar uma lista, caractere visível (`- `, `. `).
    - O cliente **não** dobra `mes` sem espaços (um nome de item colado num
      código de cor, por exemplo) — aí a linha estoura a janela.

## 5. Armadilhas deste ambiente

**Cada linha abaixo já custou horas.** O caso inteiro — sintoma, causa
medida e saída — está no caderno nomeado no título do grupo; aqui fica só o
gatilho, para que a armadilha seja reconhecida **antes** de o tempo ser gasto.
Ao mexer numa peça, ler a lista do grupo dela de cima a baixo; ao ver na tela
um sintoma parecido com uma linha, abrir o caderno e ler aquela entrada.

**Referência a `CLAUDE.md` §5 espalhada pelos outros documentos continua
valendo** — e são cerca de duzentas. Ela chega aqui, no gatilho, e daqui ao
caderno do grupo, que é onde o caso está contado por inteiro. Não há link
quebrado a consertar.

### `ARMADILHAS-AMBIENTE.md` — Ambiente e ferramentas desta máquina

Shell, PowerShell, Python 2, encoding cp1252, regex, git, compilação local, ferramentas nossas.

- `strings` não existe no Git Bash daqui — com `2>/dev/null` falha calado e parece "zero resultados"
- `[Text.Encoding]::Latin1` não existe no PowerShell 5.1 → devolve `$null` e todo resultado derivado é lixo. Usar `GetEncoding(28591)`
- `Get-ChildItem -Include` sem curinga no caminho retorna vazio
- Arquivo cp1252 salvo como UTF-8 vira `\xef\xbf\xbd` (U+FFFD) e o acento se perde para sempre. Não é mojibake reversível
- E quem faz isso hoje é a FERRAMENTA DE EDIÇÃO do assistente. Ela lê e grava como UTF-8
- E o `$` de um regex com `re.M` NÃO casa antes do `\r` — ele casa DEPOIS, deixando o `\r` dentro do grupo capturado
- A conexão com o MariaDB nasce em `utf8mb4`, e byte acentuado morre nela. As 105 colunas de texto do banco são `latin1`, mas o `character_set_client`…
- `source` do mysql.exe quebra com barra invertida (`\U` = comando desconhecido). Usar barras normais no caminho
- Compilar pela linha de comando exige `SolutionDir` explícito. O `map-server.vcxproj` tira os caminhos de include dessa variável, que só o `.sln`…
- Heredoc do Bash aqui come a contrabarra dupla. `<<'EOF'` deveria ser literal e não é: `\\` chega como `\` no arquivo gerado
- No `.cat` de tradução, o `arquivo#N` NÃO é a linha — é a ordem do literal dentro do arquivo
- `os.system` com a linha começando por aspas falha no `cmd` do Windows: o primeiro par de aspas é comido e sai
- Nome de NPC pode ter ESPAÇO, e um `\S+` no lugar dele perde arquivo inteiro. Os campos de uma linha de NPC são separados por TAB
- Há arquivo de nome COREANO dentro do cliente, e ele quebra o Python 2 de duas maneiras diferentes
- `valida_visual.le_item_db` devolve uma LISTA CHATA com o item DUAS vezes, uma por arquivo — e nem a primeira nem a última é a resposta certa
- Crase dentro de `python -c "..."` chamado pelo Bash EXECUTA o que está entre elas. Aspas duplas não protegem crase
- `x += f()` em que `f` mexe em `x` perde o que `f` consumiu. O `+=` guarda o `x` de antes de avaliar a direita
- No `.gitignore`, negar um arquivo dentro de pasta excluída NÃO tem efeito — e o `git status` não denuncia, porque o arquivo simplesmente continua…
- Ferramentas rodam em Python 2.7 (`C:\Python27\python.exe`)

### `ARMADILHAS-CLIENTE.md` — O cliente de RO

GRF, .lub e bytecode Lua, tabelas do cliente, sprite e .act, .rsm e mapa, patch de exe, itemInfo, efeitos.

- Entrada de GRF marcada como "DES" NÃO é entrada ausente. O `ferramentas/grf.py` recusa arquivo com o bit de cifra (`flags & 6`) com um
- `.lub` do GRF é bytecode (header `\x1bLua`); os do ROenglishRE são texto puro. Comparar tamanho entre os dois não significa nada
- O bRO entrega o MESMO arquivo em `.lua` e em `.lub`, e o legível pode estar velho. O reflexo é pegar o texto puro e poupar o desmonte de bytecode
- `Tools\luac.exe -p` do ROenglishRE é o único jeito de provar que um `.lub` gerado compila
- Patch de exe "aplicado e confirmado" NÃO é patch com efeito — e script que confere o próprio trabalho não prova nada
- Comparar tamanho de texto a olho, em tela cheia, não decide. Duas rodadas foram gastas discutindo se a fonte tinha mudado
- Um TETO num valor que todo mundo pede não limita exageros: ele apaga a escala inteira. O `--teto 11` do `ajusta_tamanho_fonte.py` parecia calibrado
- Metade de uma seção de PE pode não existir em disco. A `.xdiff` deste exe tem `VirtualSize` 0x1000 e `SizeOfRawData` 0x400
- O vão que decide onde centrar um modelo pode não estar nem no `.gat` nem no id de textura do `.gnd`
- Caixa envolvente de `.rsm` com vários nós mente se juntar tudo num box só. O `pos` do nó raiz é offset no espaço do modelo, não dimensão
- No `.rsm`, a ALTURA é o Z e não o Y — a planta de um móvel é X × Y. Ler X × Z troca profundidade por altura e devolve uma planta plausível e errada…
- Modelos de uma mesma família numerada NÃO têm a mesma frente, e supor que têm vira metade deles de costas
- `mede_rsm.py` que não sobra 0 byte não vale nada. Formato de malha é cheio de campo opcional por versão
- São TRÊS `map_cache.dat`, e a `prontera` não está no grande. O rAthena abre `db/import/map_cache.dat`, `db/re/map_cache.dat` e `db/map_cache.dat`…
- Ler tabela grande de bytecode Lua 5.1: o operando `RK` só endereça constante até o índice 255
- Chave de tabela que é SÍMBOLO INDEXADO POR NÚMERO colapsa a tabela inteira numa entrada só, sem erro nenhum
- Tabela do cliente cujas chaves são `EnumVAR.<X>`, `SKID.<X>` e afins tem de ter as CHAVES tiradas do NOSSO GRF — nunca do ROenglishRE nem do bRO
- Um `.lub` pode definir MAIS DE UMA tabela, e ler tudo numa lista só colapsa uma na outra
- Este cliente NÃO desenha manto com slot acima de 120, e a tabela não tem nada a ver com isso. Medido em tela em 2026-08-09
- Rótulo de aba da janela de habilidades é escrito na VERTICAL: o comprimento gasta altura, não largura — e some com as abas de baixo
- Tabela certa + arte certa + arquivo lido pelo cliente ≠ desenha na tela. As três se verificam offline, as três deram OK
- O horário de ACESSO do arquivo diz se o cliente leu. `Get-ChildItem | Select LastAccessTime` no `cliente\data\...\datainfo` mostra o instante em que…
- O endereço do servidor mora no `sclientinfo.xml`, não no `clientinfo.xml`. Este exe é `<servertype>sakray</servertype>`
- A IA do homúnculo e a do mercenário moram em `cliente\AI_sakray\`, não em `cliente\AI\` — e a pasta errada não dá erro até alguém invocar o bicho
- Ferramenta que consulta tabela do cliente tem de ler `cliente\data\` ANTES do GRF
- Sprite de NPC "enterrado no chão" é o `.act`, não o mapa. O `.act` diz a que altura o desenho é colado em relação à célula
- Bandeira de `CTRL+<n>` não está no `emotionlist.lub`, está no EXE — e o que ela vale depende do `<servicetype>`
- O NOME do sprite não descreve a arte, e neste cliente NÃO EXISTE aura de chão colorida. O `4_PURPLE_WARP` (10237) não tem nada de roxo
- Quest que o cliente não conhece DERRUBA O CLIENTE. Não é "aparece sem título" — é caixa de erro de Lua, uma por missão e por atualização da janela…
- O cabeçalho do `map_cache.dat` tem 8 bytes, não 6. É `uint32 file_size; uint16 map_count;` e o compilador o alinha em 8
- Metade da configuração do cliente está no REGISTRO DO WINDOWS, e não no cliente. É a §4.9 um degrau adiante
- A censura de palavrão do jogo é do CLIENTE, e mora em `data\manner.txt` dentro do GRF — não no rAthena e não no exe
- "Unknown Item" com sprite de maçã NUNCA é problema de servidor — e a pergunta que resolve é *quais* itens, não *por que aquele item*
- O `identifiedResourceName` do bRO é o DESENHO, não a identidade do item — e dois itens diferentes o compartilham
- Gerador de entrada de cliente pode ter campo ZERO FIXO, e por seis itens seguidos isso pode estar certo
- O `ClassNum` de ARMA no `itemInfo.lua` não vem do `View:` do `item_db` — ele vive só do lado do cliente
- Nome e descrição do MESMO bloco do `itemInfo.lua` podem estar em línguas diferentes, e a ferramenta que resolve cada metade é outra
- `unidentifiedResourceName` TERMINA em `identifiedResourceName`, e um regex sem lookbehind casa com a linha errada
- O `DataFolderFirst` está provado para ALGUMAS pastas, não para todas — e tratar uma pasta nova como se já estivesse provada custa uma sessão inteira
- Dá para provar que o cliente ABRIU um arquivo, contornando a regra de uma hora do NTFS
- O `EF_MAX` do rAthena NÃO é o teto de efeitos do cliente — é o do emulador, e ele está 900 efeitos atrasado
- Antes de mexer no `effecttool` para pôr uma textura na tela, perguntar que EFEITO já a desenha
- O cliente desenha coisa no mundo SEM o servidor — `grep` em `npc/` não prova que algo não existe
- No `.rsw`, a posição do modelo vira célula com `altura/2 + pos.z/5` — com **`+`**, e o sinal errado espelha o mapa inteiro no eixo norte–sul. Em mapa simétrico o erro **não aparece**; quem decide são os pilares, que são célula fechada no `.gat`
- Ler mojibake a olho num screenshot dá resposta plausível e errada. No balão acima, `°Ô½ÃÆÇ` (게시판, "quadro de avisos") e `ºÎ½ºÅÍ` (부스터, "Booster") são…

### `ARMADILHAS-SCRIPT.md` — Script de NPC do rAthena

Comandos de script, variáveis e arrays, spawn, instância, unidades, sintaxe do parser.

- `setwall` com tamanho maior que 1 pode sair mais curto do que o pedido, e não avisa
- Comentário no fim de uma linha de spawn entra DENTRO do nome do evento. O `npc_parsesrcfile` enche o `w4` *"to end of line"* (`src/map/npc.cpp`)
- Uma linha ruim mata o ARQUIVO INTEIRO, não a linha — inclusive linha de comentário
- Em spawn com área, `<xs>,<ys>` NÃO é o lado do retângulo. O `mob_spawn` chama `map_search_freecell` com `xs-1` (`src/map/mob.cpp:1149`), que sorteia…
- Mapa pode ter pedaço andável solto, e `0,0` no spawn sorteia lá. O `vis_h01` tem 16.104 células no mapa de verdade mais 479 na linha y=239, ruído do…
- `rand(1)` não devolve 0: ele MATA o script. O `buildin_rand` (`src/map/script.cpp:5604`) na forma de um argumento só faz `maximum -= 1` e então…
- `getitem` com a mochila cheia LARGA O ITEM NO CHÃO. O `buildin_getitem` (`src/map/script.cpp`) chama `pc_additem`
- `mes` que começa com ESPAÇO não abre linha nova — cola na anterior. O `clif_scriptmes` (`src/map/clif.cpp:2472`) manda a string crua, sem `\n`
- `||` e `&&` do script do rAthena NÃO fazem curto-circuito. São o `C_LOR` e o `C_LAND`, operadores de dois números (`script.cpp:3839`) resolvidos pelo…
- O nome único de um NPC é o que vem DEPOIS do `::`, não a linha inteira. Em `<Nome na tela>::<Nome único>` o `npc_parsename` (`src/map/npc.cpp:3674`)…
- `explode` NÃO limpa o array de destino. Ele grava a partir do índice dado (`script.cpp:17305`) e para quando a string acaba
- `getarraysize()` de array de texto para no último elemento NÃO VAZIO. Então tabela de colunas paralelas em que a última coluna termine em `""`…
- Facing de NPC se calcula pela CÉLULA de destino, não pelo lado da tela. Tabela do `enum directions` (`src/map/path.hpp:16`) medida em jogo com a…
- NPC com sprite de CLASSE DE JOGADOR nasce pedindo o penteado 0, e o 0 não existe
- `OnNPCKillEvent` NUNCA dispara para mob que tem evento próprio. Em `mob.cpp:3592` os dois são ramos de um `else if`
- `disablenpc` NÃO desliga o NPC dentro da instância — a receita de §2 não vale para NPC de mapa de instância
- `getexp` NÃO passa pela taxa de EXP do servidor. A `base_exp_rate` é aplicada uma vez só, ao EXP de mob, no carregamento do `mob_db`…
- Literal de `setarray` pode virar NOME DE VARIÁVEL, e aí traduzir quebra. No `DevilTower.txt` os cinco `"DIR_NORTHWEST"`, `"DIR_NORTH"` etc
- `F_GetPlural` aplica regra de plural INGLESA à palavra que a gente escrever. O `callfunc("F_InsertPlural", n, "Second")` vira "3 Seconds"
- `killmonster` com o terceiro argumento tem o sentido INVERTIDO do que o nome sugere: sem ele o rótulo dos mortos não dispara
- `delequip` + `getitem2` devolve o item SEM vínculo, SEM prazo e SEM grau de encanto
- Zero em variável de `.` ou `.@` APAGA a entrada, então `setarray .@x[0], 0,0,0,0,0;` deixa um array VAZIO
- `mobcount` e `killmonster` com `"all"` não fazem nada, e não avisam. São dois enganos do mesmo dia e da mesma família
- `callsub` ABRE ESCOPO `.@` NOVO E VAZIO, igual ao `callfunc` — e ler as `.@` do chamador lá dentro devolve ZERO, calado
- `movenpc` move o BONECO e deixa a ÁREA DE TOQUE para trás. O `npc_movenpc` (`src/map/npc.cpp:5046`) faz `map_moveblock` e mais nada
- `strnpcinfo(2)` lê o nome de EXIBIÇÃO, não o nome único — e há script do rAthena que guarda dado no sufixo `#`. São campos diferentes
- `getunitdata` NÃO é função: é comando que PREENCHE UM ARRAY — e usado como função devolve zero, calado na tela
- `setunitdata UMOB_MAXHP` para BAIXAR o máximo CORROMPE o HP — é underflow `uint32` no rAthena, e o servidor cura em vez de reduzir
- Comando de script que "existe no rAthena" pode não existir NESTE rAthena, e o erro do parser aponta para o lugar errado

### `ARMADILHAS-RATHENA.md` — db/, conf/ e C++ do rAthena

Bancos em YAML, recarregadores, item_db, guardas do C++, operação dos quatro servidores.

- Em `db/refine.yml`, `Level:` é 1-based e NÃO é o refino do item. O leitor faz `refine_level -= 1`
- `invalidWarning` no leitor de YAML diz "skipping" e descarta o registro inteiro. No `RefineDatabase::parseBodyNode` (`status.cpp:183`), um nível de…
- Em `conf/groups.yml`, `false` não desliga nada. Herança de grupo é um OU binário aplicado depois do parse (`pc_groups.cpp:275`
- Equipamento ilusional não está no `Drops:` do monstro: é DROP DE MAPA — e drop de mapa NÃO passa pela taxa do servidor. São dois enganos em fila
- Em `TimeLimit` de quest, o `+` é o que decide o significado. `+3h` é intervalo (três horas a partir de agora); `6h`, sem o sinal, é hora exata
- `MAX_QUEST_OBJECTIVES` é 3 (`src/common/mmo.hpp:111`). Um quarto alvo numa quest emite *"Targets list exceeds the maximum"* e cai no mesmo `return 0`…
- A descrição do item na tela discorda do script do servidor — no NÚMERO, não só na presença
- Desligar um arquivo de castelo do rAthena leva 17 BANDEIRAS junto, e nada no log diz isso
- `DropEffect: CLIENT` no `item_db` NÃO é "sem efeito" nem "o padrão" — é uma escolha que este cliente resolve desenhando NADA
- `ShowInfo` NÃO chega ao `log/map-msg_log.log`. O `console_msg_log` deste servidor é 3 (`conf/import/map_conf.txt`)
- Trocar `Locations` de um item com o servidor NO AR deixa o item INEQUIPÁVEL até o jogador relogar — e a mensagem culpa o item
- As duas caixas de acessório da janela de equipamentos NÃO estão invertidas — a etiqueta só parece trocada porque o personagem está de frente
- `@reloadscript` sem `@reloaditemdb` FAZ O ITEM NOVO SUMIR DA VITRINE. O `npc_parse_shop` descarta todo item que não está no `item_db` em memória…
- `LOOK_BODY2` não é mais uma bandeira 0/1: guarda o Id do TRABALHO do visual alternativo — e o `db/re/stylist.yml` do vendor não foi atualizado
- A janela de encaixe de carta não abre quando o único equipamento compatível está EQUIPADO — e o servidor não manda pacote nenhum
- Arquivo de `db/` do vendor pode estar ÓRFÃO — formato certo, conteúdo certo, e ninguém o lê
- Guarda de validação do rAthena pode reprovar 100% dos valores válidos, e o chamador ainda relatar sucesso
- Padrão idêntico numa coluna do banco é evidência, e não se parece com erro. O que denunciou a guarda acima foi uma consulta ao `char` em que todo…
- Varredura por `nome_db.` NÃO acha quem itera o banco de dentro da própria classe
- O corpo de uma habilidade NÃO está mais no `skill.cpp` — cada uma tem classe própria em `src/map/skills/`
- Parar SÓ o map-server para recompilar deixa o jogador travado no login, e a mensagem culpa o cliente
- Subir o servidor a partir de um shell que pode ser encerrado deixa os quatro processos órfãos

### `ARMADILHAS-COMBATE.md` — Combate e números

Redução de dano, precisão, status de monstro, castelo e guerra.

- Nem toda parcela de dano do renewal passa pela redução de cartas. O dano físico é montado em `statusAtk`, `weaponAtk`, `equipAtk`, `masteryAtk` e…
- MONSTRO NÃO TEM RESISTÊNCIA POR RAÇA — não existe "redução humano" para mob. O `bonus2 bSubRace,RC_Player_Human` é bônus de jogador
- Dentro de castelo, a redução de 80% da guerra vale 24 HORAS POR DIA — e vale também quando o alvo é MONSTRO
- `status_calc_mob_` sem nenhuma flag LIBERA o `md->base_status` e passa a usar o status compartilhado do `mob_db`
- No renewal, a chance de acerto é literalmente `hit − esquiva` em pontos percentuais — e o piso de 5% esconde o quanto se está longe
- No `mob_db` do renewal, `Attack2` NÃO é o ATQ máximo — vira `rhw.matk`. O parser (`mob.cpp:5107`) manda `Attack2` para `status.rhw.matk` sob…
- `guardian` sem índice é guardião TEMPORÁRIO, e é o que se quer fora de castelo com dono
- Curar MONSTRO funciona, e é o Emperium que não pode — não o monstro. Vale o contrário da intuição de RO

### `ARMADILHAS-INFRA.md` — Infra, deploy, rede e publicação

SSH, Ubuntu, MariaDB, DigitalOcean, DNS, cache HTTP, deploy, Atualizador e patches.

- `tr -dc … | head -c N` mata o script inteiro sob `set -o pipefail`. O `head` fecha o cano ao completar os N bytes, o `tr` morre de SIGPIPE (exit…
- No `sshd_config` o PRIMEIRO valor vence, não o último — e isso inverte o sentido do número no nome do arquivo em `sshd_config.d/`
- Sessão SSH já aberta não prova endurecimento nenhum. Ela foi autenticada antes da mudança e continua viva de propósito — é o que impede o tiro no pé
- O `needrestart` do Ubuntu 24.04 reinicia serviço sozinho durante o `apt`, e o `ssh.service` está na lista dele
- O bit de execução NÃO está no git — no vendor `rathena/` e também em script NOSSO recém-criado, que nasce `100644` — e no Linux isso vira `Permission denied`, inclusive num script que ninguém roda à mão
- `git` como root em árvore de outro dono sai 128 com *dubious ownership* e não lê commit nenhum. Pior que o erro é o `|| echo desconhecido` que o transforma em aviso brando e desarma a trava de versão calado
- `libmariadb-dev` não basta para compilar o rAthena — falta o `libmariadb-dev-compat`
- A senha da conta de comunicação entre servidores tem teto de 23 caracteres, e passar disso falha CALADO — apontando para o lugar errado
- `StretchDIBits` falha de vez em quando, e mente no `GetLastError`. Duas execuções do mesmo binário devolveram 630 linhas (sucesso) e a terceira…
- O servidor de jogo NÃO tem relógio próprio: `gettime` e `OnClock` leem a hora LOCAL da máquina — e a máquina de produção nasce em UTC
- `nslookup` sai com código 0 mesmo quando o domínio NÃO existe. Uma sonda `nslookup $host && echo "resolve"` imprime *"resolve"* para NXDOMAIN
- Chave do DigitalOcean Spaces pode ser somente-leitura, e a listagem funciona igual
- O rclone chama `CreateBucket` antes de subir arquivo grande. Para usar cópia multi-thread (o que ele faz sozinho a partir de algumas centenas de MB)…
- Deploy parcial feito à mão desarma o gatilho de restart do deploy seguinte, e a perda é calada — CORRIGIDO em 2026-08-22
- O registro de patch do jogador é indexado por número, e DUAS contagens diferentes começam em 0001
- `go build` sem `GOOS`/`GOARCH` explícitos num script que PUBLICA binário é uma bomba de fuso horário de máquina. O `-o Jogar.exe` decide só o nome
- O deploy NÃO sai do Windows, e o pré-voo reprova aqui por um motivo que não existe no servidor. Duas coisas separadas
- `UPDATE` na tabela `char` com o jogador CONECTADO é desfeito na saída dele, e o comando não erra
- Resposta HTTP sem `Cache-Control` NÃO fica sem cache: o navegador inventa um — e quanto mais VELHO o arquivo, mais tempo a cópia velha vale

## 6. Caminho de LEITURA — leia só o que a tarefa pede

**Cada documento tem uma função. Nenhum se lê inteiro** (exceto este e o
`ARQUITETURA.md`, que são curtos de propósito).

| Documento | Função | Como ler |
|---|---|---|
| `CLAUDE.md` | mapa, regras, o que não se pode fazer | inteiro — é a partida |
| `ARMADILHAS-*.md` | os seis cadernos de armadilhas: o caso inteiro de cada linha da §5 — sintoma, causa medida e saída | **nunca inteiro**; a lista do grupo ao mexer na peça, e a entrada que o gatilho da §5 apontar |
| `ARQUITETURA.md` | quem lê o quê, o que muda junto | inteiro, ao mexer em peça nova |
| `RECEITAS.md` | passo a passo dos fluxos repetíveis | só a receita da tarefa |
| `PENDENCIAS.md` | **só o que está em aberto** | inteiro — é curto |
| `HISTORICO.md` | o que já foi feito, e por quê | **só a seção do assunto** |
| `REFERENCIA.md` | caminhos, portas, comandos, credenciais | só a tabela |
| `npc/guerra/scripts_guerra.conf` | índice narrado dos nossos NPCs | antes de tocar conteúdo |
| `ferramentas/LEIAME.md` | uma seção por ferramenta | só a seção da ferramenta |
| `CUSTOMIZACAO-VISUAL.md` | frente visual (cidade destruída) | só a seção |
| `REDUCAO-DE-DANO.md` | o que entra e o que escapa das duas reduções — a de cartas (resistência a humano) e a **geral de 80%** de guerra e PvP; a §1d é o inventário fechado do dano que escapa (veneno, sangramento e irmãos) | consulta, só a seção — **antes de discutir número de PvP** |
| `IMPLANTACAO.md` | o plano de subir para o servidor Linux — etapas, o que roda em qual máquina, e a regra de escopo do Mac | **§1 inteira antes de qualquer sessão no Mac**; depois só a etapa |
| `patcher/LEIAME.md` | como a mudança de cliente chega ao jogador: o Atualizador, o formato do patch e o ciclo de publicação | antes de mexer no patcher ou publicar patch |
| `CATALOGO-*.md` | o que está à venda, modelos, retratos | consulta |

**Ordem para uma tarefa nova:** `CLAUDE.md` → `scripts_guerra.conf` (o que já
existe?) → `RECEITAS.md` (como se faz?) → o **cabeçalho do arquivo** em
`npc/guerra/` → e só então o `HISTORICO.md`, se ainda faltar o porquê.

**Cada arquivo em `npc/guerra/` tem um cabeçalho longo explicando as decisões
dele.** Ler o cabeçalho custa menos que reconstruir o raciocínio — e é onde
estão as ressalvas que não cabem no índice.

## 7. Caminho de ESCRITA — onde registrar o que foi feito

**Escrever no arquivo errado é o que apodrece a documentação.** A regra é por
natureza do que se escreve, não por quando:

| O que você tem | Onde escrever |
|---|---|
| Trabalho **terminado** (o que foi feito e por quê) | `HISTORICO.md`, ao fim da seção do assunto, com **data absoluta** |
| Trabalho **em aberto** (falta fazer, falta testar) | `PENDENCIAS.md` |
| **Regra nova** ("nunca faça X", "sempre confira Y") | `CLAUDE.md` §4 |
| **Armadilha nova** de ferramenta/ambiente | **duas pontas:** o caso inteiro no `ARMADILHAS-*.md` do domínio, e uma linha de gatilho na §5 do `CLAUDE.md` |
| **Fluxo novo** que vai se repetir | `RECEITAS.md` |
| **Acoplamento novo** (mexer em A exige mexer em B) | `ARQUITETURA.md` §4 |
| Caminho, porta, comando, credencial | `REFERENCIA.md` |
| Por que **este** NPC/item é assim | cabeçalho do próprio arquivo |
| NPC novo | uma linha + parágrafo em `scripts_guerra.conf` |

**As três regras que mantêm isso vivo:**

1. **Ao concluir uma pendência, apague-a do `PENDENCIAS.md`** e registre no
   `HISTORICO.md`. Pendência concluída que fica é ruído — foi o motivo de os
   dois arquivos terem sido separados em 2026-08-07.
2. **Regra e armadilha SOBEM para o `CLAUDE.md`.** O `HISTORICO.md` guarda o
   *porquê*; o `CLAUDE.md` guarda a *regra*. Deixar a regra só no histórico é
   garantir que ela seja redescoberta do jeito caro.
3. **Não duplicar.** Se algo já está no `CLAUDE.md`, o histórico aponta para
   ele em vez de repetir — duas cópias divergem, e a errada é sempre a que
   alguém lê.
4. **Armadilha se escreve nas DUAS pontas, sempre.** O corpo mora no
   `ARMADILHAS-*.md` do domínio; o gatilho, na §5. Escrever só o corpo é
   enterrar a armadilha num caderno que ninguém abre sem já desconfiar dela
   — que é justamente o momento em que ela já custou o tempo. Escrever só
   o gatilho é perder a medição, que é o que separa esta lista de um
   palpite. **O gatilho é uma linha e não tem "continua abaixo": ele tem de
   bastar para a armadilha ser reconhecida na tela, sozinho.**

## 8. Convenções de trabalho

- Documentação e comentário em **português**.
- Comentário de código explica **por que**, não o que — é o padrão de todo o
  projeto e o que o faz navegável.
- Datas sempre **absolutas** (`2026-08-07`), nunca "ontem" ou "semana passada".
- Nunca colar senha real em arquivo versionado. Senhas vivem em `conf/import/`.

## 9. Se esta sessão está rodando no Mac

**Desde 2026-08-14 o projeto trabalha em três máquinas**, com papéis que não se
sobrepõem: o **Windows** faz tudo que o jogo lê e tudo que precisa do cliente; o
**Mac** faz infra (deploy, systemd, nginx, banco, scripts, site, documentação);
o **servidor Linux** só recebe `git pull` e nunca é editado à mão.

**No Mac só entra trabalho que não precisa do jogo para ser conferido.** Ficam
de fora: editar `npc/guerra/*.txt` e `db/guerra/*.yml` (são cp1252, e a
conferência é em jogo), qualquer coisa do cliente (GRF, `itemInfo.lua`, sprite,
patch de exe), compilar para Windows, e calibrar número de jogo.

**Ao esbarrar no limite, parar e sinalizar** — não adivinhar o resultado, não
editar arquivo de jogo "só para destravar", não abortar a etapa inteira:

> ⚠️ **Fora do escopo do Mac.** Isto exige `<o que exige>`. Anotei em
> `IMPLANTACAO.md` §9 para a próxima sessão no Windows. Sigo com o resto.

E então acrescentar a linha na §9 do `IMPLANTACAO.md` e continuar o que dá.

**A armadilha que o Mac introduz:** o APFS é *case-insensitive* por padrão, e
esconde exatamente o defeito que o Linux pune — um `import:` com maiúscula
errada funciona no Mac, funciona no Windows, e morre calado no Linux. É por isso
que a varredura de case roda **no deploy**, e não uma vez só.

O plano inteiro, com as etapas e o que já está apurado, está no
`IMPLANTACAO.md`.
