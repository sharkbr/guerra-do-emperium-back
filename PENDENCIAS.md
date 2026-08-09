# Pendências — Guerra do Emperium

**Só o que está em aberto.** O que já foi feito vive em `HISTORICO.md`; regras e
ordem de trabalho no `CLAUDE.md`; tabelas de consulta em `REFERENCIA.md`.

**Onde escrever:** ao concluir um item daqui, **apague-o deste arquivo** e
registre o que foi feito no `HISTORICO.md`, com data absoluta. Um item que
sobrevive aqui depois de pronto é ruído — foi por isso que este arquivo foi
separado em 2026-08-07.

> Este arquivo é versionado: **nunca colar senha real aqui.** As senhas reais
> vivem em `rathena/conf/import/`, que está fora do git.

Estado em 2026-08-08.

---

## 1. Falta ver no jogo

Tudo abaixo está **escrito, registrado no `scripts_guerra.conf` e conferido
offline**, mas nunca subiu uma vez sequer. Não são bugs conhecidos — são coisas
sem confirmação in-game.

| O quê | Onde | Desde |
|---|---|---|
| Mercado Contemporâneo (9 lojas de equipamento) | `prontera`, grade 3×3 | 2026-08-01 |
| Capacete de Intensificação (400287) | Chapeleiro | 2026-08-02 |
| Mesmerita (reset) | `prontera 144,173` | 2026-08-04 |
| Funcionária Kafra da praça | `prontera 152,191` | 2026-08-04 |
| Armazém do Clã | `prontera 149,191` | 2026-08-04 |
| Xanin e Edgard (estilista de roupa) | `prontera 172,201` / `170,200` | 2026-08-04 |
| Mestre do Refino | `prontera 184,177` | 2026-08-04 |
| Mercado de Visuais (3 lojas de traje) | `prontera`, y=155 | 2026-08-05 |
| Mercado de Cartas (9 lojas, 1410 cartas) | `prontera`, y=149/143/137 | 2026-08-05 |
| Logue e Ganhe — 20 dias de Moeda Nova | janela do cliente, sem NPC | 2026-08-07 |
| Criança — link de navegação e balão de MVP | `comodo 207,148` | 2026-08-08 |
| Manteleiro (13 mantos cosméticos) | `prontera 163,155` | 2026-08-08 |
| Mister Peso | `prontera 99,64` | 2026-08-08 |
| Mestre das Montarias (Riding Creature Master em PT) | `prontera 130,213` | 2026-08-08 |
| Arena e Área de Treinamento trocadas de lugar | `prontera 154/157,187` | 2026-08-08 |
| Placar da Arena — modal novo, na coordenada nova | `prontera 152,187` | 2026-08-08 |
| Caveira Humana caindo de jogador morto | `pvp_n_1-5` | 2026-08-08 |
| Teletransportadora de Alberta — chegada e NPC | `alberta 117,57` / `105,63` | 2026-08-08 |

**O roteiro é o mesmo para todos, e a ordem importa:**

1. `@reloaditemdb` e **depois** `@reloadscript` — a loja valida cada ID ao
   carregar, então o `item_db` precisa estar de pé antes. Loja de troca pede um
   terceiro, no meio: `@reloadbarterdb`.
2. **Fechar e reabrir o cliente** — entradas novas de `itemInfo.lua` e
   `accessoryid.lub` só são lidas na inicialização. Sem isso o item aparece sem
   nome ou o chapéu continua invisível, e a conclusão errada é achar que o
   script falhou.
3. Ir a Prontera, abrir cada loja e comprar um de cada. **É abrir a loja que
   dispara a caixa modal de arte faltando, não equipar.**

**Três coisas para olhar na primeira subida:**

- **Mercado de Cartas, loja de arma:** carrega 255 cartas na linha do `shop` e
  as outras 104 por `npcshopadditem` num `OnInit`. Se o `OnInit` falhar, a loja
  abre com 255 e **não dá erro nenhum** — o sintoma é só a lista curta. Conferir
  contando: `Carta de Arma` tem de mostrar **359**.
- **Honra de Combate:** exige rodar `sql-files/guerra_arena_pvp.sql` antes de
  subir, e **reiniciar o map-server** (não basta `@reloadscript`). Sem as
  tabelas ninguém pontua, mas o anúncio de morte continua saindo — e é esse o
  sintoma que aparece primeiro.
- **Manteleiro:** é a primeira loja de manto cosmético do projeto, e é onde a
  arte nova de 2026-08-08 aparece. O que provar: (1) a loja **abre** — item sem
  os 4 arquivos de item dispara caixa modal ao abrir, não ao equipar; (2)
  **equipar cada um dos cinco que vieram do bRO** (480055, 480096, 480117,
  480118, 480121) e ver o manto desenhado, porque é aí que a sprite por classe
  é lida. Um `Cannot find File` ao equipar significa que a classe do
  personagem de teste ficou de fora da cópia — repor com
  `python ferramentas/instala_manto.py --ids <id> --aplicar`; (3) a **Aura
  Nevada** (480097) não veste manto nenhum e não é falha: ela é efeito de tela.

- **Arena, Área de Treinamento e Placar:** os três trocaram de célula no mesmo
  pedido. O que denuncia erro aqui é **NPC empilhado**: se o `disablenpc` de um
  dos dois arquivos errar o alvo, sobram dois NPCs numa célula e nenhum na
  outra, e isso **não dá erro no log** — os dois arquivos imprimem um
  `debugmes` próprio se não acharem o NPC do rAthena, e é esse aviso que se
  procura. Andar de 152 a 157 em y=187 tem de mostrar, nesta ordem: placa,
  porta da arena, porta do treino.

- **Logue e Ganhe:** a janela abre sozinha no login e **não tem NPC** — se não
  aparecer, o roteiro acima não ajuda. O que provar, nesta ordem: (1) a janela
  abre e mostra **20 quadrados de Moeda Nova**, 10 nos dezenove primeiros e
  **50 no vigésimo** — se o ícone ou a quantidade divergirem, quem está
  desatualizado é o `CheckAttendance.lub` do cliente, não o servidor; (2) o
  prêmio chega por **RoDEX**, não direto no inventário; (3) o botão recusa a
  segunda retirada no mesmo dia.

  **Fechar e reabrir o cliente é obrigatório aqui**, e não pelo `itemInfo.lua`:
  o `System\CheckAttendance.lub` também só é lido na inicialização.

---

## 1b. Vence em dezembro de 2027 — os ciclos do Logue e Ganhe

`rathena/db/guerra/attendance.yml` tem **17 ciclos**, um por mês civil, e o
último termina em **2027-12-31**. Passado isso o sistema **morre calado**: sem
janela, sem erro, sem linha de log — o rAthena apenas não encontra período
corrente.

O conserto é uma linha: adiantar `ULTIMO` em
`ferramentas/monta_logue_e_ganhe.py` e rodar. Ele regrava os dois lados
(servidor e cliente) de uma vez. Ver `RECEITAS.md` §10.

Contexto de cada um: `HISTORICO.md`, e o cabeçalho do arquivo em `npc/guerra/`.

---

## 1c. O Corredor Fantasma — o que ficou em aberto

**A sala foi validada em jogo em 2026-08-08** e saiu do §1. O que sobrou aqui
não impede jogar: o primeiro é decisão, não esquecimento, e o segundo é só
confirmação que falta.

> **O destino da flor deixou de estar aberto em 2026-08-08.** A Alleria
> (`comodo 221,182`) paga 1 Moeda Nova por Flor Visionária — ver `HISTORICO.md`,
> seção "A Flor Visionária ganhou destino". Não é a troca do bRO (10 Flores por
> um Prêmio Visionário, com sorteio de carta de MVP), que continua cortada; os
> itens dela seguem sem uso no vendor (`23684` Cartão Visionário e o
> `IG_2018_VISIONARY_CARD` que ele abre). Os NPCs novos ainda não subiram — estão
> no §1.

**1. Os chefes aparecem com nome em inglês.** Nome de monstro vem do
**servidor**, não do `itemInfo.lua` — então o Corredor mostra "Amon Ra", não
"Amon Rá". Consertar é um `db/guerra/mob_db.yml` só com `Id` e `Name`, mas
**vale para o servidor inteiro**, não só para esta sala: é uma frente de
tradução própria, irmã da do §3, e não uma correção do Corredor. As linhas de
spawn já usam `--ja--`, então acompanham sozinhas no dia em que isso for feito.

**2. Os dois números novos nunca foram vistos em jogo.** O teste que aprovou a
sala pegou a versão de **2 flores garantidas e 65 chefes**. Logo depois eles
viraram **1 flor a 30% e 130 chefes**, e essa versão só foi conferida no boot
do servidor — não jogando. Nada sugere problema (é o mesmo caminho de código,
com outros números), mas fica dito.

Ao conferir a flor: **três mortes secas seguidas não querem dizer nada** com 30%
de chance — dá quase 35% de acontecer por acaso. Contar umas dez antes de
suspeitar. Se em dez não vier nenhuma, o suspeito é o nome do evento na linha de
spawn, e a armadilha está no `CLAUDE.md` §5.

---

## 1d. A Teletransportadora oferece destino que derruba o cliente

Aberto em 2026-08-08, e **não** é sobre o Corredor Fantasma — apareceu ao testar
ele. O personagem foi levado ao "Sticky Sea" (`1@slug`) e o cliente caiu, com o
personagem **preso**: ao reconectar ele voltava ao mapa quebrado e caía de novo.

A causa é a regra 6 do `CLAUDE.md` na forma completa:

| | |
|---|---|
| `1@slug` no `db/map_index.txt` do rAthena | **sim** — o servidor aceita o warp |
| `.rsw`, `.gat`, `.gnd` no GRF deste cliente | **nenhum dos três** |
| Apelido no `resnametable.txt` | **não** — não é o falso negativo do `pvp_n_1-5` |

O `npc/custom/warper.txt` é o do próprio rAthena (Euphy), montado para um
cliente moderno, e **o `1@slug` não deve ser o único**: o menu de Instâncias e o
de Masmorras têm mapas pós-2021 que este kRO de 2021-11-03 não tem.

> **Metade varrida em 2026-08-08.** Os **109 mapas do `db/re/instance_db.yml`**
> foram cruzados com o `data.grf`: 73 das 78 instâncias têm todos os mapas, e as
> 5 restantes dependem de quatro mapas ausentes — `1@iwp`, `1@jorchs`,
> `1@jorlab`, `1@whl`. Os quatro **já estão comentados** no
> `conf/maps_athena.conf`, então o `@warp` para eles agora responde "mapa não
> encontrado" em vez de prender o personagem. As cinco instâncias não perdem
> nada: nenhuma tem script, são registros órfãos do `db/`.
>
> **Falta ainda a varredura do menu de Masmorras** e dos destinos do
> `teletransportadora.txt` que não são instância — é lá que o `1@slug` mora.

**Sobre o passo 2 da receita abaixo:** o `resnametable.txt` deste cliente existe
e tem 2155 linhas (dentro do `data.grf`, sem cópia solta em `data\`) — a
checagem de apelido é obrigatória mesmo. Nenhum dos quatro mapas acima está
apelidado; eles faltam de verdade.

### Como fechar

A varredura é barata e já existe pronta em pedaços — `ferramentas/grf.py` lista
os `.rsw` do GRF, e foi assim que o `vis_h01` foi aprovado antes de virar o
Corredor. O que falta é o laço:

> **A cópia do passo 3 já existe desde 2026-08-08.** É o
> `npc/guerra/teletransportadora.txt`, criada por outro motivo (mover o par de
> Alberta — ver §4c), e é ela que sobe hoje. O passo 3 deixou de depender de
> nada: é editar aquele arquivo. O que falta é a varredura dos passos 1 e 2.

1. Extrair todo `warp "<mapa>"` do `npc/guerra/teletransportadora.txt`.
2. Cruzar com os `.rsw` do `data.grf` **e com o `resnametable.txt`** — pular a
   segunda tabela dá falso positivo em mapa apelidado.
3. Podar do menu os que faltarem — em cópia nossa em `npc/guerra/`, **não**
   editando o arquivo do rAthena (o cabeçalho do `scripts_guerra.conf` já
   registra que é esse o caminho no dia em que se quiser versão própria).

**Tirar personagem preso**, enquanto isso: com ele offline (`online = 0` na
tabela `char`), `UPDATE char SET last_map='prontera', last_x=152, last_y=188
WHERE char_id=...`. Conferir o `save_map` junto — se ele também estiver no mapa
quebrado, o personagem volta para lá ao morrer.

---

## 1e. A Criança de Comodo — duas estreias e uma promessa

Aberto em 2026-08-08, com a NPC de `comodo 207,148`
(`npc/guerra/crianca_de_comodo.txt`). A NPC em si está na tabela do §1, com
todas as outras que faltam ver no jogo. O que fica aqui é o que **não** se
resolve olhando a NPC aparecer.

**1. O link de navegação é o primeiro do projeto.** A marcação "Fica aqui" da
segunda caixa é uma etiqueta `<NAVI>` dentro do `mes`, e quem a lê é o
**cliente**, não o servidor — então nada no log do map-server vai dizer se
funcionou. O que provar, nesta ordem: (1) o texto sai **azul e sublinhado**, não
com as etiquetas à mostra — se aparecer `<NAVI>` cru na tela, este cliente não
tem o recurso e o conserto é tirar a etiqueta; (2) clicar traça o caminho até
`comodo 208,187` no minimapa.

Se sair o caminho mas sem marcador, é o campo do ícone (`000`, sem ícone) — o
cabeçalho do arquivo explica os três números e o que trocar. Se der para clicar
e nada acontecer, o suspeito é a tabela de navegação do cliente, e **não** o
script: `comodo` foi conferido em `navi_map` antes de escrever, mas o override
em `cliente\data\luafiles514\lua files\navigation\` é do ROenglishRE e pode
estar descasado do GRF de 2021 — a armadilha de sempre.

**2. O balão de MVP nunca foi disparado por NPC nosso.** É `specialeffect
EF_MVP` (68) num `OnTimer4000`, e o caminho é outro que o do emote da Alleria:
aquilo é `emotion`, isto é efeito de tela. Deve subir de 4 em 4 segundos sozinho,
sem clicar. **Não confundir com o emote da Alleria**, do outro lado da cidade: o
dela é um balão de conversa com a mão chamando; o desta é o banner de MVP, o
mesmo que sobe quando um chefe morre.

**3. A fala já promete o Cassino, que ainda não existe.** A segunda caixa termina
em "O Cassino também tá funcionando, com Moeda Nova!". Em 2026-08-08 **não há
cassino nenhum no servidor** — nem NPC, nem script, nem linha no
`scripts_guerra.conf`.

**Isso é adiantamento deliberado, não erro:** o dono do projeto confirmou no
mesmo dia que o cassino vem nos próximos dias, e a coordenada da Criança foi
escolhida em cima disso — `207,148` é o canto de aposta de Comodo. A frase fica.

Enquanto o cassino não nasce, a Criança é a única coisa no servidor que fala
dele. Se o plano mudar, o conserto é apagar **uma linha** — a última da segunda
caixa do arquivo.

A Moeda Nova citada na frase essa existe, e tem duas fontes (Logue e Ganhe, e a
Alleria de `comodo 221,182`). É só o cassino que falta.

### O que o canto de aposta já tem, para quem for construir

O rAthena põe em Comodo o par de `npc/other/comodo_gambling.txt`, e ele fica
exatamente ali: a **Devellin** em `204,148` (três células da Criança), que só
fala da obsessão da Kachua por diamante, e a **Kachua** em `219,158`, que troca
Diamante de 3 Quilates por item aleatório. É o que a cidade tem de cassino hoje —
e está **em inglês**, como todo NPC do rAthena que a frente do §3 ainda não
alcançou.

Decidir cedo se o Cassino novo convive com esses dois, substitui um deles pela
receita de sempre (`disablenpc` no original + duplicata nossa em `npc/guerra/`),
ou ignora os dois. As três saídas são legítimas; o que custa caro é descobrir
que existiam depois de plantar o NPC novo em cima.

---

## 1f. As instâncias da Ordem dos Exploradores — falta ver no jogo

Aberto em 2026-08-08. **A Ordem dos Exploradores já está construída** — ver a
§1g. O que continua em aberto é o outro lado: as **instâncias que ela manda
caçar** nunca foram abertas em jogo, uma a uma.

Isso importa mais agora do que quando esta seção nasceu. Cada uma das 14
missões escritas aponta para o chefe de uma destas instâncias, e o Id de mob
de cada alvo foi lido do `monster`/`areamonster` do script, não testado. Uma
instância que não abre, ou um chefe que não nasce, deixa a missão
correspondente **impossível sem nada no log**.

**A Vila dos Porings foi vista no jogo em 2026-08-08 e funcionou.** É a
primeira instância validada, e por isso é também o teste recomendado da Ordem
inteira (§1g, passo 2). **Faltam 15.**

### O que já está resolvido, e é quase tudo

**As instâncias do rAthena já estão todas carregadas.** O caminho é
`npc/re/scripts_main.conf` → `npc/re/scripts_athena.conf:65-112` (47 arquivos,
só `WaveMode.txt` comentado) + `npc/scripts_athena.conf:120-123` (4 pre-RE).
**Não há nada a "ativar"** — exceto uma, abaixo.

O critério "sem requisito de quest" do browiki foi **conferido contra o script**,
não aceito de fora: em todas as 15 da tabela, a quest que o NPC de entrada exige
é iniciada pelo **próprio script** (o `setquest` daquele id não existe em mais
nenhum arquivo de `npc/`). O gate é nível + tempo de espera, e se resolve
falando com a NPC.

| # | Instância (bRO) | rAthena | Script | Nv | Missão |
|---|---|---|---|---|---|
| 1 | Vila dos Porings | Poring Village | `re/instances/PoringVillage.txt` | 30 | C |
| 2 | Batalha dos Orcs | Orc's Memory | `instances/OrcsMemory.txt` | 50 | A |
| 3 | Quarto Crescente | Half Moon In The Daylight | `re/instances/EddaHalfMoonInTheDaylight.txt` | 80 | C |
| 4 | Torneio de Magia | Geffen Magic Tournament | `custom/official/GeffenMagicTournament.txt` | 90 | A |
| 5 | Caverna do Polvo | Octopus Cave | `re/instances/OctopusCave.txt` | 90 | C |
| 6 | Memórias de Sarah | Sara's Memories | `re/instances/SaraMemory.txt` | 99 | A |
| 7 | Hospital Abandonado | Bangungot Hospital 2F | `re/instances/BangungotHospital.txt` | 100 | A |
| 8 | Palácio das Mágoas | Ghost Palace | `re/instances/GhostPalace.txt` | 120 | A |
| 9 | Sonho Sombrio | Nightmarish Jitterbug | `re/instances/NightmarishJitterbug.txt` | 120 | A |
| 10 | Aos Pés do Rei | Charleston in Distress | `re/instances/CharlestonCrisis.txt` | 130 | A |
| 11 | Maldição de Glast Heim | Old Glast Heim | `re/instances/OldGlastHeim.txt` | 130 | C |
| 12 | Torre do Demônio | Devil's Tower | `re/instances/DevilTower.txt` | 130 | B |
| 13 | Fábrica do Terror | Horror Toy Factory | `re/instances/HorrorToyFactory.txt` | 140 | A |
| 14 | Covil de Vermes | Faceworm's Nest | `re/instances/FacewormsNest.txt` | 140 | A |
| 15 | Lago de Bakonawa | Bakonawa Lake | `re/instances/BakonawaLake.txt` | 140 | B |
| 16 | Sarah vs Fenrir | Fenrir and Sarah | `re/instances/SarahAndFenrir.txt` | 145 | B |

**Os 16 têm todos os mapas no GRF deste cliente** — conferido contra o
`data.grf` na varredura do §1d.

### A única que precisa ser ligada

**O Torneio de Magia (#4) está em `npc/custom/official/`, e essa pasta não é
carregada.** O `npc/scripts_custom.conf` tem uma linha só descomentada, a nossa
(`import: npc/guerra/scripts_guerra.conf`). Os três mapas (`1@gef`, `1@gef_in`,
`1@ge_st`) já estão no `maps_athena.conf` e existem no GRF; o gate é nível 90 +
espera (quest 9316).

**Ligar não é descomentar a linha do rAthena** — a lei da §2 do `CLAUDE.md` vale
aqui: cópia nossa em `npc/guerra/` + linha no `scripts_guerra.conf`. Vale
decidir antes se o Torneio entra: ele é `custom/`, não conversão oficial, e o
cabeçalho dele não diz de onde veio.

### Fora de escopo por decisão, em 2026-08-08

- **As Missões D inteiras** — são conversão de item por moeda, não caçada.
- **As instâncias com requisito de quest**, por enquanto: Salão de Ymir
  (Ritual de Coroação), Sala Final (Investigando o Passado), Ninho de Nidhogg
  (Guardiã de Yggdrasil), Caverna de Buwaya (Segredos na Floresta), Glast Heim
  Sombria (Maldição de Glastheim), Ilha Bios (Viagem Dimensional), Templo do
  Demônio Rei (Caverna de Mors), Laboratório Werner e Base Militar (Terra
  Gloria), Missão OS (Ocupação OS), Laboratório de Wolfchev (Rumores Sérios),
  Memorial COR (Ilusión), Caverna de Mors (Ilha Bios).

### O que ficou sem resposta

**"Sussurro Sombrio"** (Missões C, chefes Espírito/Habitante/Convidado
*Imortal*) **não foi identificado** — não aparece na lista de instâncias do
browiki e os chefes parecem variante da Torre do Demônio.

**Deixou de ser bloqueio:** as placas de Missões C foram montadas sem ele, com
as quatro instâncias que se identificaram (Vila dos Porings, Caverna do Polvo,
Quarto Crescente e Maldição de Glastheim). Se o Sussurro Sombrio um dia for
identificado, entra como missão nova — uma linha no `quest_db.yml` e uma na
tabela do `OnInit`.

### Como fechar

Entrar em cada uma das 16 e confirmar que abre, que o chefe nasce e que o mapa
não derruba o cliente. **A conta de teste (grupo 99) serve aqui** — o problema
dela é trava de item (§7 do `CLAUDE.md`), não instância.

### Os nomes já estão em português (2026-08-08)

As 16 têm nome PT no `db/guerra/instance_db.yml`, e os **26 literais** dos
scripts foram trocados na mesma passada — o nome é chave, não rótulo
(`ARQUITETURA.md` §4). O menu da `teletransportadora.txt` acompanhou, com 17
rótulos.

**Três rótulos do menu ficaram em inglês de propósito**, por falta de fonte no
bRO (regra §4.3 — não inventar): `Eclage Interior`, `Endless Tower` e
`Hazy Forest`. Achar o nome PT dos três e fechar.

E o menu **deixou de estar em ordem alfabética**, porque foi traduzido no
lugar. Reordenar é seguro — cada par `"texto",Label` anda junto —, mas não foi
feito.

### A tradução das instâncias — a pré-condição foi cumprida

**Resolvido em 2026-08-09.** O `traduz_npcs.py` ganhou o `nomes_de_instancia()`,
que lê os `Name:` dos dois `instance_db.yml` e os põe em `tokens_intocaveis` —
então o `--aplicar` **recusa** traduzir nome de instância, venha de onde vier.

Era preciso porque o `.@md_name$ = "..."` casa com o `RE_ATRIB` e entra no
catálogo como se fosse fala, e o `RE_TECNICO` não cobre esse caso: ele protege
literal que está *dentro* da chamada (`warp "gef_fild10"`), e ali a chamada
recebe uma variável. Uma segunda tradução divergente quebraria o
`instance_create` — falha calada, e só em jogo.

São **4.910 linhas de `mes`** nos 16, com distribuição muito torta: Sonho
Sombrio (1.261) e Quarto Crescente (973) são 45% do total; Batalha dos Orcs tem
55 e Lago de Bakonawa 62. Por isso a tradução é **um grupo por instância** —
ver §3.

---

## 1g. A Ordem dos Exploradores — falta ver em jogo

**Construída em 2026-08-08.** O briefing que morava aqui saiu: o que ele
mandava fazer está feito, e o *porquê* de cada decisão foi para o
`HISTORICO.md` e para os cabeçalhos de
`npc/guerra/ordem_dos_exploradores.txt` e `db/guerra/quest_db.yml`.

**O que está no ar, e conferido no carregamento:** a moeda (25737) nos dois
lados, as 15 missões de caçada + 3 de espera, as três placas, o
Teleportador, a Máquina de Troca, a **Opheliac com a loja de 28 itens**, os
**dois guardas**, os dois portais e os cinco NPCs do rAthena desligados. O
map-server subiu sem um `Unknown syntax`, sem aviso de quest descartada, sem
erro nos seis `disablenpc` e sem um único aviso de barter — o que prova que
o arquivo parseou, que o `OnInit` rodou e que os 29 AegisNames das três
lojas resolveram (item desconhecido descarta a loja inteira, com aviso).

**Nada disso foi tocado por um jogador ainda.** O que falta é entrar e usar:

1. **O caminho até lá.** Ir a `alberta 116,73`, atravessar o portal, e voltar
   por `auction_02 43,17`. Conferir que o de volta não devolve para dentro de
   si mesmo (a chegada é `43,21`, fora do raio 1,1 — mas só o jogo prova).
> **O primeiro teste em jogo foi feito em 2026-08-08 e achou um bug, já
> corrigido:** pegar as missões derrubava o cliente com dezenas de caixas de
> erro de Lua. Faltava a entrada das quests na tabela do CLIENTE, e a correção
> foi o `ferramentas/monta_missoes_da_ordem.py` — ver `HISTORICO.md`. **Rodar
> o cliente de novo exige fechar e reabrir**, porque aqueles `.lub` só são
> lidos na inicialização. O resto da lista abaixo continua por fazer.

2. **Uma missão inteira, do quadro ao pagamento.** **É o único teste que
   prova a decisão central** — que `HUNTING` conta onde `OnNPCKillEvent` não
   contaria. A **Batalha dos Orcs** é a candidata agora: a porta dela é nossa
   desde 2026-08-09 (`npc/guerra/porta_dos_orcs.txt`, nível 60+, party de 1),
   então um personagem de nível alto entra.

   > **A Vila dos Porings foi destravada em 2026-08-09.** A Emily
   > (`prt_fild05 145,235`) recusa `BaseLevel > 60`, e aqui **não deu para
   > copiar o bRO** como se fez com os Orcs: lá a instância entra por
   > `izlude 46,103`, outro *mapa*. A porta é nossa de verdade — o **Batedor
   > da Ordem**, `prt_fild05 147,235`
   > (`npc/guerra/porta_da_vila_dos_porings.txt`), que abre a mesma memória
   > sem teto. A Emily continua ligada, com a cadeia de história de novato
   > dela.
3. **A trava das 6h.** Entregar duas vezes seguidas e ver a segunda ser
   recusada.
4. **A Máquina de Troca.** Juntar 10 moedas e ver a janela de troca abrir com
   o ícone certo. **Atenção:** o nome do item na janela de barter vem do
   `itemInfo.lua` do cliente, não do servidor — se sair errado, o conserto é
   no cliente (`CLAUDE.md` §4.9). A entrada [25737] já foi posta, mas
   **exige fechar e reabrir o cliente**.
5. **O Teleportador**, nos 14 destinos. Ele **já foi testado e já teve um bug
   corrigido** em 2026-08-08: o menu e a tabela de destinos estavam em ordens
   diferentes e os catorze levavam ao lugar errado, sem erro nenhum. Depois do
   conserto o pareamento foi conferido lendo o arquivo gerado, destino a
   destino, mas **só duas opções foram vistas em jogo**. Falta percorrer as
   outras doze — e mapa que derruba cliente é justamente o que não se vê de
   fora.
6. **A loja da Opheliac.** Falar com ela e ver a janela de troca abrir com os
   28 itens. **Conferir nome e ícone linha a linha** — é aqui que a falta de
   uma entrada de cliente apareceria, e nove dos itens ganharam a entrada
   nesta sessão. Os dois itens criados por nós (Saltos da Rainha Scaraba
   15368, Memorável Anel Rústico 490174) merecem um olhar extra: equipar e
   ver se o bônus próprio pega.
7. **Os dois guardas e a fala da Opheliac**, só para ver a acentuação
   desenhada — é o teste barato que pega erro de cp1252.

**A conta de teste (grupo 99) NÃO serve para o passo 4.** As duas moedas são
`NoDrop`/`NoSell`/`NoTrade`, e o grupo 99 ignora as sete travas — ver
`CLAUDE.md` §4.7.

### As missões que continuam fora — e o que falta para cada uma

**São 15 missões desde 2026-08-09** (8 do grupo A, 3 do B, 4 do C). O Sonho
Sombrio entrou: o "Réquiem de Marfim" é o **`Awakened Ferre` (3073)**, o chefe
final, e estava lá o tempo todo — a varredura anterior o perdeu porque
procurava um padrão de spawn só. Ver `HISTORICO.md`.

Duas continuam **comentadas** em `db/guerra/quest_db.yml`, e as duas por falta
de alvo, não por escopo:

- **Torneio de Magia.** O alvo do bRO é *"1 Muliphen"*, e **`Muliphen` não
  existe no nosso `mob_db` com nome nenhum** — não é questão de achar o Id, o
  monstro não está no vendor. Os únicos mobs do arquivo são Alphonse (2565),
  Alphonse Jr (2566) e os capangas de Geffen; o Torneio é duelo de NPC. E a
  instância nem está carregada: mora em `npc/custom/official/`. **Para
  destravar seria preciso criar o mob**, o que é outra natureza de trabalho.

- **Sussurro Sombrio.** Esta é nova, e está mais perto do que parecia. A
  coordenada que o cliente do bRO dá (`dali02 121,63`) é a
  **`Scientist Doyeon#a2`**, ou seja a **Sky Fortress Invasion** — que já está
  carregada (`npc/re/scripts_athena.conf:101`) e pede só **nível 145**, sem
  teto e sem quest. Serviria.

  **O que falta é o alvo.** O bRO diz *"elimine os Demônios de cada tipo"*, e a
  instância tem **onze** monstros `Immortal_` (3474 a 3483) mais o
  Stefan.J.E.Wolf. Escolher três seria inventar, contra a regra §4.3.
  **Basta a página do browiki dela** — com os três nomes, é uma entrada no
  `quest_db.yml`, uma linha em cada tabela do `OnInit` e uma no
  `monta_missoes_da_ordem.py`.

  Nota: isto corrige o §1f, que listava o Sussurro Sombrio como *"não
  identificado"*.

### Decisões que continuam com o dono

1. **Os valores do bRO ficaram como estão** (5 a 25 moedas, 50k a 1M de EXP,
   troca 10:1), por decisão de 2026-08-08 — entra igual ao bRO e se ajusta
   depois de ver em jogo. Duas coisas a olhar quando isso for revisto: o
   `getexp` **não** passa pela nossa taxa 10x (`CLAUDE.md` §5), então a EXP
   das missões é relativamente menor aqui do que lá; e a taxa 10:1 faz uma
   missão média (7 moedas) valer sete décimos de uma Moeda Nova.
2. **A Ordem não tem loja de serviço.** O bRO tem Slot, Encantamento,
   Fortalecimento e Enriquecimento na mesma página. Nada disso foi levantado
   — se entrar, é trabalho separado. A **loja de itens** da Opheliac entrou
   em 2026-08-08; o que continua fora dela é abaixo.

### Os quatro itens da loja da Opheliac que ficaram de fora

A lista do browiki tem 32 itens e a loja tem 28. Os quatro que faltam não
foram esquecidos:

- **Combinador Heróico (100283), Combinador do Herói (100284) e Combinador de
  Tatuagens (100285).** Os três são pergaminho de **encantamento** — a
  descrição do bRO diz *"Abre a janela de Combinação"* —, e encantamento foi
  o que o pedido de 2026-08-08 excluiu. Mesmo que não fosse: janela de
  encantamento é sistema de UI do cliente, com metade da configuração do lado
  de lá (`CLAUDE.md` §4.9), e nenhuma delas está montada. Vendidos assim, não
  fariam nada.
- **Chapéus Sortidos (103189).** Caixa de chapéu aleatório, e não existe no
  nosso `item_db`. Não é só criar a entrada: precisa de um grupo em
  `item_group_db` com os sete chapéus dentro, e cada um deles precisa existir
  e ter arte. É um trabalho separado, e o único dos quatro que vale a pena
  fazer um dia.

**A transformação de visuais e o encantamento do Robozinho Sabe-Tudo**, que a
Opheliac também faz no bRO, ficaram de fora pela mesma razão — são janela do
cliente, não NPC.

---

## 2. Itens com `# TODO` — quatro efeitos e oito conjuntos

Placeholders que entraram sem bônus. Cada `# TODO` no `db/guerra/item_db.yml`
cita a linha em português que ficou de fora.

| item | o que falta | por quê |
|---|---|---|
| 28247 Espingarda | "Mantém [Espalhar Dano] ativo" | não há `bonus` que mantenha habilidade ligada, **e** "Espalhar Dano" não existe na tabela de habilidades do bRO |
| 510155 Ceuci | +11: remover Hipotermia/Cristalização ao apanhar de magia | `bonus3 bAutoSpellWhenHit` **conjura**, não **remove** status |
| 400687 Garra | +11: 10% de infligir Medo ao apanhar | idem |
| 15371, 28572, 400687, 510155 | os conjuntos | exigem a outra peça, que em geral nem está no servidor |

Os três primeiros exigiriam código em `src/custom/`, ou seja **recompilar**.

**Uma exceção é viável hoje:** o conjunto do Broche da Celine (28572) com a Luva
dos Espíritos Malignos (2980) — as duas estão no mesmo mercado, no Acessorista.
O Laço da Celine (18849) também já está na loja, no Chapeleiro.

**O Ceuci (510155) é permanente, não provisório:** é exclusivo do bRO, folclore
brasileiro, nunca existiu no kRO.

> **Armadilha para o dia da atualização do rAthena:** esses IDs estão *fora* da
> nossa faixa 30000-30999, e o `Footer: Imports:` faz o nosso arquivo ser lido
> **depois** do `db/re/item_db.yml`. Se o rAthena um dia trouxer esses itens de
> verdade, as nossas entradas vazias **venceriam a versão boa, caladas.**
> Conferir esta seção antes de qualquer outra coisa ao atualizar o vendor.

---

## 3. EM ANDAMENTO — diálogo dos NPCs do rAthena

**Onde parou em 2026-08-04.** Esta é a única frente da tradução que não está
fechada, e é a maior: **19.260 falas**, das quais 10.903 distintas.

| grupo | feito | | o que é |
|---|---|---|---|
| `cidades` | 715/722 | 99% | Prontera e Izlude |
| `pvp` | 202/222 | 91% | `npc/other/pvp.txt` |
| `campal` | 904/1055 | 86% | KVM, Flavius, Tierra |
| `kafra` | 486/569 | 85% | uma função serve todas as cidades |
| `servico` | 714/926 | 77% | forja, refinador, estalagem |
| `guerra` | 968/1437 | 67% | 20 feudos + WoE:SE |
| `novico` | 14/322 | 4% | **não começou** |
| `classe1` | 13/1518 | 1% | **não começou** |
| `classe2` | 235/12489 | 2% | **não começou** |
| `jitterbug` | 1073/2406 | 45% | Sonho Sombrio — **começado, NÃO aplicado** |

**As instâncias entraram na frente em 2026-08-09**, com um desenho próprio:
**um grupo por instância**, não um grupo `instancias` único — porque só se
aplica grupo inteiro, e as 16 juntas dão 9.518 pares com distribuição muito
torta. Uma por vez, cada uma fecha e entra em jogo sozinha.

**Quinze das dezesseis fecharam e estão aplicadas** na mesma data: `magoas`,
`bakonawa`, `orcs`, `polvo`, `porings`, `hospital`, `sarah`, `brinquedos`,
`fenda`, `vermes`, `glastheim`, `fenrir`, `demonio`, `charleston` e
`crescente`. Ver `HISTORICO.md`, "Quatorze instâncias e a Fenda Dimensional em
português".

**Sobrou uma, a maior, e ela está pela metade:**

| grupo | pares | distintos traduzidos | distintos a traduzir |
|---|---|---|---|
| `jitterbug` | 2.406 | 418 | **835** |

Sonho Sombrio, `npc/re/instances/NightmarishJitterbug.txt`. O catálogo está
extraído e em dia; 418 dos 1.253 textos distintos foram preenchidos em
2026-08-09, do começo do roteiro até o encontro com a Lagi.

> **O grupo NÃO foi aplicado, e não deve ser até fechar.** Meia instância em
> português é exatamente o que a regra de "só aplicar grupo inteiro" existe
> para evitar. O arquivo do rAthena continua 100% em inglês, e o `.cat` é a
> única coisa que mudou — reverter é `git checkout` de um arquivo só.

Como retomar: `preenche_catalogo.py --pendentes jitterbug` lista **só** o que
ainda está vazio e renumera sozinho, então é só continuar. O ciclo, as travas
e as convenções fixadas estão no `HISTORICO.md` da mesma data e no `CLAUDE.md`
§4.12/§4.13; o `--estado` mede.

Os três de baixo são as quests de mudança de classe — 88% do volume que resta,
e o que o dono do projeto pediu explicitamente por nostalgia. O pouco que
aparece traduzido neles **vazou do glossário** (`Cancelar`, `Sim`, `Não`), não
foi trabalho dirigido.

**Eles NÃO estão aplicados nos arquivos**, e isso é deliberado: um
`--aplicar tudo` chegou a tocar 17 arquivos a ~2% e foi revertido. Arquivo quase
todo em inglês com uma frase solta em português no meio é pior que arquivo em
inglês. Aplicar só quando o grupo estiver inteiro.

### Como retomar

```
python ferramentas/traduz_npcs.py --estado          # onde está cada grupo
python ferramentas/traduz_npcs.py --extrair classe2 # se o vendor mudou
# traduzir: acrescentar pares em npc/guerra/traducao/glossario.cat
python ferramentas/traduz_npcs.py --preencher --forcar
python ferramentas/traduz_npcs.py --aplicar classe2
```

O `ferramentas/LEIAME.md` tem o detalhe das travas e do formato. Duas regras que não estão
óbvias no código:

1. **Nome de habilidade, item, mapa e classe sai da tabela do bRO que já está
   no cliente**, não da cabeça — `skillinfolist.lub`, `mapnametable.txt`,
   `map_msg_por.conf` (550+). Cinco nomes tiveram de ser corrigidos por eu ter
   traduzido de memória.
2. **Traduzir por texto distinto, não por ocorrência.** 43% é repetição.

### O que também ficou pendente

- **Nomes de NPC.** Foram pedidos junto com as falas e não foram feitos. É a
  parte com risco real: no rAthena o nome exibido faz parte do identificador
  único, e `duplicate()`, `enablenpc` e `donpcevent` de outros arquivos
  referenciam por ele. Renomear exige construir a tabela nome-antigo →
  nome-novo e reescrever toda referência do `npc/` — errar faz NPC sumir do
  mapa, e o erro só aparece no jogo. Os nomes em português existem no
  `navi_npc_br.lub` do GRF do bRO, por mapa e coordenada.
- **`guerra` parado em 67%** não é por falta de tempo: os 469 que faltam são
  fragmentos de frase quebrada em várias linhas de `mes` do WoE:SE, que
  dependem do vizinho para ficar natural. Fechar exige olhar bloco a bloco, não
  string a string.

---

## 4. O manto cosmético (`Costume_Garment`) — falta só o `varre_cosmeticos.py`

Aberto em 2026-08-05, ao varrer o acervo cosmético para o Mercado de Visuais.
**A ferramenta que faltava foi escrita em 2026-08-09** (`estende_robeid.py`);
o que sobra aqui é uma consequência dela, não a lacuna original. O relato
completo está no `HISTORICO.md`, seção "O manto cosmético".

| camada | chapéu | manto | estado |
|---|---|---|---|
| nome e descrição | `itemInfo.lua` | igual | — |
| slot de visual | `accessoryid.lub` + `accname.lub` | `spriterobeid.lub` + `spriterobename.lub` | resolvido |
| ferramenta que estende o slot | `estende_accessoryid.py` | `estende_robeid.py` | resolvido |
| arquivos de arte | 4 de item + 4 de cabeça | 4 de item + sprite de manto **por classe** | resolvido |
| ferramenta que instala a arte | `instala_visual.py` | `instala_manto.py` | resolvido |

### O que continua em aberto

**O `varre_cosmeticos.py` ainda não classifica manto como `curavel`.** Ele se
recusava a isso porque a cura não existia — chamar de "sem cura" o que só
precisava de outra ferramenta foi o erro de 2026-08-01, e prometer cura que não
há como cumprir é o erro simétrico. Agora a cura existe, e a recusa virou
conservadorismo sem motivo.

Feita essa mudança, os **45 mantos** que estavam parados em `curavel` desde
2026-08-05 voltam à mesa — e com eles a pergunta de quantos dos 193 "sem cura"
daquela contagem eram, na verdade, `View` fora da tabela e não falta de arte.

Nada disso é bloqueio: manto pedido item por item continua entrando pelo
caminho de sempre, que é o que as rodadas de 2026-08-08 e 2026-08-09 fizeram.
O que falta é a **varredura**, para não depender de pedido.

### Duas confusões que continuam valendo

**Não confundir com as "capas" que já funcionam.** 420010 (Aura da Escuridão) e
420047 (Capa de Cavaleiro) estão no Retoqueiro e desenham normalmente — elas são
`Costume_Head_Low`, não `Costume_Garment`. O nome engana; quem manda é o
`Locations:` do `item_db`.

**Nem toda peça de `Costume_Garment` desenha manto.** A Aura Nevada (480097),
no Manteleiro, não tem `View`: ela é um `hateffect` no `Script` do item, efeito
de tela. Item assim não precisa de arte de manto nenhuma, e procurar a arte que
"falta" nele é perder tempo.

---

## 4b. A Caveira Humana já cai — falta o NPC que a compra

**A metade de baixo fechou em 2026-08-08**: o `OnPCKillEvent` do
`npc/guerra/honra_de_combate.txt` entrega a Caveira Humana (30995) no
inventário do matador. Ver `HISTORICO.md`, seção "A Caveira Humana (30995)".

**O que sobrou:** a descrição da Moeda Nova (30998) lista "em troca de Caveira
Humana" como uma das fontes de moeda, e **esse NPC de troca não existe**. Hoje
a caveira entra e não sai de lugar nenhum.

Quando for escrito, é `barter` e não `itemshop` — a caveira é `NoSell`, e o
`itemshop` passa a moeda por `pc_can_sell_item`, que recusa item `NoSell`. Ver
`CLAUDE.md` §4.10, que existe exatamente por causa deste caso.

---

## 4c. O Warper virou cópia nossa, e não foi podado

Aberto em 2026-08-08. Para mover o par de Alberta (chegada `28,234` → `117,57`,
NPC `28,240` → `105,63`) foi preciso **forkar** o `npc/custom/warper.txt` para
`npc/guerra/teletransportadora.txt`: o destino de cada cidade é um
`Go("mapa",x,y)` **dentro** do corpo do script, e nenhum comando alcança isso de
outro arquivo. A posição do NPC sairia com `movenpc`; a chegada, não.

A linha do arquivo do rAthena está **comentada** no `scripts_guerra.conf` — os
dois não podem subir juntos, porque os nomes de NPC batem.

**Duas consequências:**

1. **A cópia não acompanha o upstream.** Correção que o rAthena fizer no
   warper.txt tem de ser trazida à mão. O diff é barato enquanto a diferença
   forem as três linhas de Alberta, e é por isso que elas estão listadas uma a
   uma no cabeçalho da cópia.
2. **A poda do §1d agora tem onde ser feita.** Aquela seção pedia "cópia nossa
   em `npc/guerra/`" como pré-requisito para tirar do menu os mapas que este
   cliente não tem. A cópia existe; a poda **não foi feita**. Todo destino de
   Instância continua suspeito.

---

## 5. Antes de expor o servidor à rede

### 1. Trocar a conta interserver `s1` / `p1`

**O que é:** é com essa conta que o char-server e o map-server se autenticam no
login-server. Não é conta de jogador — é credencial de serviço. Está no padrão
do rAthena, que é público, e o próprio servidor reclama no boot:

```
[Warning]: Using the default user/password s1/p1 is NOT RECOMMENDED.
```

**Risco:** quem alcançar a porta 6900 pode se passar por um char-server e
conversar com o login-server.

**Como resolver** — três lugares, e os três têm que casar, senão os servidores
param de se enxergar:

1. Tabela `login` do schema `ragnarok`: a linha com `account_id = 1`, `sex = 'S'`
   (o `S` marca "server", não é personagem).
2. `rathena/conf/import/char_conf.txt` → `userid` e `passwd`.
3. `rathena/conf/import/map_conf.txt` → `userid` e `passwd`.

Fazer com os servidores parados. Depois subir e confirmar no log do login-server
que aparece `Authentication accepted` com o novo nome.

### 2. Voltar `new_account` para `no`

**Onde:** `rathena/conf/import/login_conf.txt`.

**O que é:** com `yes`, digitar `nome_M` na tela de login **cria a conta na
hora**, sem e-mail, sem validação, sem nada. Foi ligado só para o teste do Marco
Zero, quando ainda não havia painel de registro.

**Risco:** qualquer pessoa cria contas ilimitadas. É vetor de spam e de burlar
banimento por conta.

**Como resolver:** trocar para `no` assim que existir um caminho próprio de
registro — provavelmente o backend em Go.

### 3. Senhas de jogador estão em texto puro

**Onde:** `rathena/conf/login_athena.conf` → `use_MD5_passwords: no` (padrão do
rAthena).

**O que é:** a coluna `user_pass` da tabela `login` guarda a senha legível. Quem
ler o banco lê todas as senhas.

**Risco:** vazamento do banco vira vazamento de senhas. E como muita gente
reusa senha, o dano passa do seu servidor.

**Ressalva importante:** MD5 também é fraco por padrões de hoje — não é a
solução ideal, é só melhor que texto puro. Existe `sql-files/tools/convert_passwords.sql`
para converter as senhas existentes. Decidir isso junto com o backend em Go, que
é quem deveria tratar autenticação de verdade.

### 4. Pôr senha no `root` do MariaDB

**Situação:** o `root` do MariaDB local aceita conexão **sem senha**.

**Mitigação que já existe:** o rAthena *não* usa root. Criamos o usuário
`ragnarok`, com permissão apenas nos schemas `ragnarok` e `ragnarok_log` —
então um bug de SQL injection num script custom não alcança o resto do banco.

**Risco que sobra:** qualquer processo rodando na máquina abre o banco como root.

### 5. A conta de teste `teste`

Criada para o Marco Zero: senha trivial e `group_id 99`, que é **GM completo**.
Antes de abrir o servidor: apagar, ou trocar a senha e baixar o `group_id`.

---

## 6. Higiene, sem pressa

### 1. Não rodar os servidores como administrador

O rAthena avisa: `You are running rAthena with admin privileges, it is not
necessary.` Os três servidores só precisam abrir portas altas (6900, 6121, 5121)
e falar com o MariaDB — nada disso exige elevação. Rodar elevado só aumenta o
estrago de uma falha.

### 2. Reavaliar `db/map_cache.dat` no git

Hoje esse arquivo (3 MB) está **versionado de propósito**, contra a convenção do
brief. O motivo: sem ele o map-server carrega zero mapas, e regerar exige o GRF
do cliente. Com ele, carrega 1265 mapas num clone limpo.

Quando passarmos a gerar o cache a partir do GRF do bRO, o arquivo vira artefato
nosso e começa a mudar a cada geração — aí ele deve sair do git (já existe a
regra `*.mcache` no `.gitignore` esperando por isso).

### 3. Atualizações do rAthena upstream

O `rathena/` foi vendorizado como arquivos comuns, sem o histórico do upstream.
Trazer correção do rAthena hoje é diff manual. Se isso incomodar, a saída é
`git subtree` — mas decidir antes de acumular customização, porque depois fica
mais caro.

---

