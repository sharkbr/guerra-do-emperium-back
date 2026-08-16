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
| Área de Treinamento no lugar novo | `prontera 157,187` | 2026-08-08 |
| Placar da Arena — modal novo, na coordenada nova | `prontera 142,180` | 2026-08-08 |
| Caveira Humana caindo de jogador morto | `pvp_n_1-5` | 2026-08-08 |
| Teletransportadora de Alberta — chegada e NPC | `alberta 117,57` / `105,63` | 2026-08-08 |
| Sombrios Gerais — loja, sprite levantado e facing novo | `auction_01 193,58` | 2026-08-11 |
| 22 itens novos em 7 lojas, e 2 que mudaram de vitrine | `prontera`, y=155 e y=161/173 | 2026-08-12 |
| Tranqueiras (55 materiais pelo preço de compra) — **e o sprite de classe** | `prontera 151,131` | 2026-08-12 |
| Chapeleiro sem a Boina Alada (10 itens, era 11) | `prontera 151,173` | 2026-08-12 |
| **31 peças de cabeça nas três lojas da fileira de cima, e o preço novo** | `prontera`, y=173 | 2026-08-12 |
| Arena de Combate com a Morte (`4_M_DEATH`), virada para leste | `prontera 147,180` | 2026-08-12 |
| Regra nova da arena: sem anti-conluio, com piso de -10 | `pvp_n_1-5` | 2026-08-13 |
| "Arena de Prontera" no minimapa **e** no letreiro de entrada | cliente, sem NPC | 2026-08-13 |
| Guia de Prontera de volta ao ar | `prontera 154,187` | 2026-08-12 |
| Ticket de Inventário e Rédea na Máquina | `prontera 167,199` / `comodo 214,185` | 2026-08-12 |

**A Tranqueiras é a única da lista que pode falhar por um motivo novo**, e ele
é do lado do cliente: ela usa **sprite 5 (`JOB_MERCHANT`), uma classe de
jogador**, e nenhum dos 26 mil NPCs do rAthena faz isso. O ramo do
`status_set_viewdata` que atende esse caso deixa o penteado em **0**, e este
cliente só tem de 1 a 42 — as duas linhas de `setunitdata` no `OnInit` existem
por causa disso. O que a tela decide, e só ela: **se o corpo E a cabeça
desenham**. Se não desenharem, a troca já está escolhida no cabeçalho do
arquivo — sprite **776 (`4_M_TWMIDMAN`)**, e as duas linhas de `setunitdata`
saem junto.

**Ela não deve imprimir aviso nenhum ao carregar**, e isso é a segunda coisa a
conferir. Enquanto era de 1 zeny, imprimia 25 `npc_parse_shop: ... discounted
buying price`; desde que passou a cobrar o **preço de compra do `item_db`**
(`-1` na linha do `shop`, 2026-08-12) a conta do `npc.cpp:4153` dá zero para os
55, porque todos têm `Sell` igual a `Buy/2`. Aviso que apareça aponta um item
cujo `Sell` não é `Buy/2` — o número no próprio aviso diz qual.

**O Ouro (969) está de volta na lista, e só é seguro enquanto o preço for o de
compra.** Ele saiu na manhã de 2026-08-12 e voltou na tarde, junto com a troca
de preço. Pôr a loja de volta a 1 zeny com ele dentro devolve 74.999 de lucro
por clique — o maior buraco que o projeto já teve. As duas decisões estão
amarradas; os cabeçalhos do arquivo e do `scripts_guerra.conf` dizem isso.

**As 31 peças de cabeça pedem uma conferência que as outras linhas não pedem:
o PREÇO na tela.** Foi a rodada que estreou a regra 16 do `CLAUDE.md` — item
com `Buy` no `item_db` entra pelo `Buy`, não a 1 zeny —, e o que decide é o que
a janela da loja mostra:

- **Chapeleiro (19 itens):** o **Elmo de Aegir** tem de aparecer a **200.000**.
  Se aparecer a 1, a linha do `shop` não pegou e o buraco de 99.999 por clique
  está aberto. Os outros quatro com preço são 5388, 19262, 18508 e 400194, os
  três primeiros a 20.
- **Ocleiro (27 itens):** dez com preço — o Fogo Fátuo (19380) a **10**, os
  outros nove a 20.
- **Retoqueiro (12 itens):** só a Aura Amaldiçoada (420105) a 20.

**O número de avisos de `discounted buying price` tem de CAIR, não subir.** As
16 peças com preço de compra não disparam o aviso; as 15 a 1 zeny disparam, e
só elas. Aviso com item **fora** dessas 15 é engano de preço — o ID sai no
próprio aviso.

E a **Touca Exótica (400308)** é o único item da rodada que não existe no
vendor: se ela não aparecer na vitrine, o problema é o `db/guerra/item_db.yml`,
não a loja. Ela também é a única das 31 com conjunto nosso (Carta Lady Branca,
`db/guerra/item_combos.yml`).

**A Sombrios Totais (189,58) está conferida em jogo** — corpo, sorteio e a lista
de prêmios, esta depois de tirar a indentação que colava as linhas
(`CLAUDE.md` §5).

Falta a **Gerais**, e ela pede três coisas de uma vez, porque os três defeitos
eram de camadas diferentes:

1. **`@reloadbarterdb` além do `@reloadscript`** — a mercadoria dela vive no
   `barters_guerra.yml`, e é o que faz a janela de troca abrir com as quatro
   linhas e o ícone da Moeda Nova. Nunca foi aberta.
2. **Fechar e reabrir o cliente** — o sprite dela precisa do override de `.act`
   (`levanta_sprite_npc.py 2_COLAVEND -53`) para não aparecer enterrado, e
   sprite só é relido na inicialização.
3. **Olhar para que lado ela está virada** — nasceu em facing 4 (errado, olhava
   para o sul) e foi para 2 (oeste, olhando para a Totais).

E ela carrega uma dívida que não é dela: **o override de `.act` está fora do
git** e some em cliente novo, sem erro nenhum. A receita para repor é uma linha,
e está em `ferramentas/levanta_sprite_npc.py`.

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
  subir, e **reiniciar o map-server** (não basta `@reloadscript`). Sem a
  tabela ninguém pontua, mas o anúncio de morte continua saindo — e é esse o
  sintoma que aparece primeiro.

  **A regra mudou em 2026-08-13** e o roteiro de teste mudou junto. São três
  coisas para provar, e duas delas só aparecem com um alvo **negativo**:
  (1) matar quem tem 0 ou mais pontua o matador e derruba o morto em 1;
  (2) matar quem já está negativo **não** dá ponto a ninguém, mas **continua**
  derrubando o morto — este é o caso que o código não fazia até agora;
  (3) o morto para em **-10** e não desce mais, e o número da placa tem de
  bater com o do modal de reputação (é o mesmo piso escrito em dois lugares —
  ver `ARQUITETURA.md` §4). Não há mais limite por par de contas nem espera
  entre uma morte e a seguinte: matar dez vezes seguidas tem de valer dez
  vezes, enquanto o alvo estiver em 0 ou acima.
- **Manteleiro:** é a primeira loja de manto cosmético do projeto, e é onde a
  arte nova de 2026-08-08 aparece. O que provar: (1) a loja **abre** — item sem
  os 4 arquivos de item dispara caixa modal ao abrir, não ao equipar; (2)
  **equipar cada um dos cinco que vieram do bRO** (480055, 480096, 480117,
  480118, 480121) e ver o manto desenhado, porque é aí que a sprite por classe
  é lida. Um `Cannot find File` ao equipar significa que a classe do
  personagem de teste ficou de fora da cópia — repor com
  `python ferramentas/instala_manto.py --ids <id> --aplicar`; (3) a **Aura
  Nevada** (480097) não veste manto nenhum e não é falha: ela é efeito de tela.

- **Arena, Área de Treinamento e Placar:** os três já trocaram de célula três
  vezes, e desde 2026-08-13 **não estão mais na mesma fileira**: a placa em
  `142,180` e a porta da arena em `147,180` dividem o `y=180`, e a porta do
  treino ficou sozinha em `157,187`. Nenhum dos dois arquivos da arena desliga
  NPC do rAthena hoje — o `disablenpc` saiu em 2026-08-12 —, então o sintoma
  antigo (NPC empilhado, sem erro no log) já não se aplica a eles; o do campo
  de treino ainda usa a receita e ainda imprime `debugmes` se errar o alvo. O
  que conferir na tela: **a placa aparece** em `142,180` (célula andável, sem
  vizinho a menos de quatro casas). O sprite da porta voltou ao `4_M_DEATH` no
  mesmo dia e já foi visto em jogo — esse não está mais em aberto.

- **Logue e Ganhe:** a janela abre sozinha no login e **não tem NPC** — se não
  aparecer, o roteiro acima não ajuda. O que provar, nesta ordem: (1) a janela
  abre e mostra **20 quadrados de Moeda Nova**, 10 nos dezenove primeiros e
  **50 no vigésimo** — se o ícone ou a quantidade divergirem, quem está
  desatualizado é o `CheckAttendance.lub` do cliente, não o servidor; (2) o
  prêmio chega por **RoDEX**, não direto no inventário; (3) o botão recusa a
  segunda retirada no mesmo dia.

  **Fechar e reabrir o cliente é obrigatório aqui**, e não pelo `itemInfo.lua`:
  o `System\CheckAttendance.lub` também só é lido na inicialização.

- **As células da escrivaninha do Centro da Ordem** (`auction_01`, escritas em
  2026-08-11). O móvel em si **já foi conferido pelo dono** — posição, tamanho
  e rotação passaram de primeira. O que falta é o bloqueio, que é a outra
  metade e mora no servidor: cinco `setwall` no `OnInit` de
  `npc/guerra/centro_da_ordem.txt`. Pede **`@reloadscript`** (só isso — o
  `.rsw` já está instalado). O que provar: (1) andar em volta e **não
  atravessar** `191,70-73` nem `192,73`; (2) **nenhum `debugmes`
  "A MESA ESTA ATRAVESSAVEL"** no log do map-server — é o aviso que o próprio
  bloco imprime se alguma célula não pegar; (3) que o caminho **contorna** a
  mesa em vez de o personagem travar, que é o sintoma de o cliente e o
  servidor discordarem.
  **A mesa cobre mais do que as cinco células**: a pegada medida é `x191-192`
  em `y70-73`, então dá para entrar em `192,70`, `192,71` e `192,72` — a
  metade leste do tampo. Foi entregue assim porque foi assim que veio o pedido;
  fechar é acrescentar os três pares ao `setarray` do bloco.
  **Mas fechar deixou de ser gratuito em 2026-08-11:** o Egebreu
  (`npc/guerra/comprador_de_caveiras.txt`) foi posto em `192,72`, uma das três.
  Fechá-la o deixa **em célula bloqueada** — ele continua clicável, mas ninguém
  mais encosta nele, e nada avisa. Quem fechar as três decide antes: ou deixa
  `192,72` de fora do `setarray`, ou move o Egebreu para `193,72` (anda, está
  livre, uma célula a leste, mesmo facing).

- **O sofá da alcova norte do Centro da Ordem** (`auction_01 179.5,84.0`,
  instalado em 2026-08-11). **Não pede `@reloadscript`** — não há script nesta
  peça; pede o cliente **reler o mapa**, ou seja sair e voltar ao salão
  (reabrir o cliente é a garantia). O que provar: (1) que ele aparece **entre**
  as células `179,84` e `180,84`, e não meia célula para o lado; (2) que está
  **de frente para o sul**, com o encosto na drapeação do fundo — a rotação foi
  medida e não escolhida (ver `HISTORICO.md`), mas é a primeira vez que essa
  medição decide alguma coisa, e é a tela que a confirma; (3) o **tamanho**:
  5,54 × 2,25 células numa alcova de ~9, com 1,7 de folga de cada lado — se
  ficar grande, o campo é a escala, e os usos oficiais descem até 0,80.

  **Ele não bloqueia passagem**, e isso é o esperado: as células `x177-182` em
  `y83-85` continuam andáveis e dá para atravessar o móvel. Fechar é um
  `setwall` no `centro_da_ordem.txt`, como o da escrivaninha — e aí vale a
  mesma conversa da mesa, sobre o Egebreu e as células dele.

- **As duas estátuas dos plintos do sul do Centro da Ordem**
  (`auction_01 182.5,68.5` e `176.5,68.5`, instaladas em 2026-08-11). Como o
  sofá: **não pede `@reloadscript`**, pede o cliente **reler o mapa** — sair e
  voltar ao salão. O que provar: (1) que cada uma está **centrada no seu
  plinto de 2×2**, e não meia célula para o lado; (2) o **facing**, que é a
  parte com risco de verdade — a `prn_statue_03` deve olhar para **oeste**
  (para o meio do salão) e a `prn_statue_08` para o **sul** (para a entrada,
  `177,67`). A convenção de ângulo está medida três vezes (ver
  `HISTORICO.md`), mas nesta família **modelos vizinhos têm frentes
  opostas** — a `prn_statue_02` está 180° fora da `_08` no `prt_lib` —, então
  estátua de costas é o defeito plausível aqui, e é mudar um número na receita.
  (3) O **tamanho**: 5,0 e 4,8 células de altura, contra os 29,25 unidades dos
  quatro `동상` que o salão já tem em pé. A `_03` passa **0,22 unidade** da
  beirada do plinto com um braço, a 3,5 células de altura — está previsto e
  medido; se incomodar na tela, o campo é a escala (0,96 resolve, ao custo de
  sair do 1,0 oficial).

  **Estas duas não precisam de `setwall`**, e é a primeira peça do salão que
  não precisa: as células dos plintos já nascem **bloqueadas** no `.gat`.

- **Os oito guardas do Centro da Ordem** (`npc/guerra/guardas_do_centro.txt`,
  escritos em 2026-08-11). Pede **`@reloadscript`** — nada de cliente. O que
  provar: (1) que **nascem os oito**, e não sete: os oito se chamam `Guarda` na
  tela e se distinguem só pelo sufixo `#co_*` do nome único, e nome único
  repetido faz o segundo não nascer, calado; (2) que cada um está **virado para
  a célula que o dono pediu** — o facing foi calculado da tabela do `dirx`/`diry`
  (`unit.cpp:70`), que anda anti-horária, e com a câmera padrão deste cliente as
  direções caem na diagonal da tela, então a conferência é olhar **para onde ele
  aponta no mapa**, não o lado da tela; (3) que os dois de `184,80` e `171,86`
  passam de tela com o `next` e fecham sem sobra.

  As dezesseis células (as oito deles e as oito que olham) já foram conferidas
  andáveis no `map_cache`, e nenhuma colide com NPC.

  **Duas coisas ditas ao dono e ainda não decididas por ele**: a fala de
  `184,80` diz "Crânios Humanos" e o item que existe é a **Caveira Humana**
  (30995) — quem procurar "Crânio" no inventário não acha nada; e a
  **Face-Sombria** (fala de `188,86`) não existe em lugar nenhum do servidor,
  nasce ali como boato.

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

## 1e. A Criança de Comodo — duas estreias

Aberto em 2026-08-08, com a NPC de `comodo 207,148`
(`npc/guerra/crianca_de_comodo.txt`). A NPC em si está na tabela do §1, com
todas as outras que faltam ver no jogo. O que fica aqui é o que **não** se
resolve olhando a NPC aparecer.

**1. Os links de navegação são os primeiros do projeto, e desde 2026-08-13 são
dois.** "Fica aqui o Corredor" e "Fica aqui" são etiquetas `<NAVI>` dentro do
`mes`, e quem as lê é o **cliente**, não o servidor — então nada no log do
map-server vai dizer se funcionou. O que provar, nesta ordem: (1) o texto sai
**azul e sublinhado**, não com as etiquetas à mostra — se aparecer `<NAVI>` cru
na tela, este cliente não tem o recurso e o conserto é tirar a etiqueta; (2)
clicar no primeiro traça o caminho até `comodo 208,187` (o Espectro) e clicar no
segundo até `comodo 154,98` (a porta leste do Cassino) no minimapa.

Os dois links convivem na mesma janela e apontam para lados opostos da cidade —
o Espectro fica ao norte, o Cassino a oeste. **Clicar num e depois no outro** é o
teste que separa "o link funciona" de "o link é decorativo": se o segundo clique
não redesenhar o caminho, o marcador está preso no primeiro alvo.

Se sair o caminho mas sem marcador, é o campo do ícone (`000`, sem ícone) — o
cabeçalho do arquivo explica os três números e o que trocar. Se der para clicar
e nada acontecer, o suspeito é a tabela de navegação do cliente, e **não** o
script: `comodo` foi conferido em `navi_map` antes de escrever, mas o override
em `cliente\data\luafiles514\lua files\navigation\` é do ROenglishRE e pode
estar descasado do GRF de 2021 — a armadilha de sempre.

**2. O balão de MVP nunca foi disparado por NPC nosso.** É `specialeffect
EF_MVP` (68) num `OnTimer3000`, e o caminho é outro que o do emote da Alleria:
aquilo é `emotion`, isto é efeito de tela. Deve subir de 3 em 3 segundos sozinho,
sem clicar. **Não confundir com o emote da Alleria**, do outro lado da cidade: o
dela é um balão de conversa com a mão chamando; o desta é o banner de MVP, o
mesmo que sobe quando um chefe morre.

**3. O sprite mudou em 2026-08-13**, a pedido do dono: era 944 (`4_M_DST_CHILD`,
o menino da própria Comodo), passou a **962** (`4_M_RUSCHILD`, o menino de
Rachel). As duas conferências de sempre foram feitas — `JT_4_M_RUSCHILD = 962` no
`npcidentity.lub` deste cliente e no `src/map/npc.hpp`, com
`data\sprite\npc\4_m_ruschild.spr` e `.act` na tabela do `data.grf`. O que falta
é olhar: **sprite de criança fica enterrado no chão com facilidade** (a
armadilha do `.act`, `CLAUDE.md` §5), e o 962 nunca foi usado neste servidor.

**A promessa do Cassino fechou.** A segunda caixa prometia, desde 2026-08-08, um
cassino que não existia — adiantamento deliberado, e a coordenada da Criança foi
escolhida em cima disso (`207,148` é o canto de aposta de Comodo). O **Cassino
Casa Rosa** entrou em 2026-08-12 (`npc/guerra/cassino_de_comodo.txt`, §1m), e em
2026-08-13 a frase ganhou o nome dele e o link para a porta.

O par de `npc/other/comodo_gambling.txt` do rAthena continua exatamente ali — a
**Devellin** de `204,148` (três células da Criança) e a **Kachua** de `219,158`,
as duas em inglês, à espera da frente de tradução do §3. O Cassino nasceu no
`cmd_in02` e **convive** com elas; não houve substituição.

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

## 1h. Resistência a humano — o que sobrou depois do teto

Feito e no ar em 2026-08-10, **falta a prova em tela das duas**:

1. **A Carta Caídos não dá mais resistência a humano.** O conjunto com a Carta
   Guerreiro Orc perdeu o `bonus2 bSubRace,RC_Player_Human,15`; o
   `RC_DemiHuman,15` ficou (vale contra monstro, não vale em PvP). Está em
   `db/guerra/item_combos.yml`, sobrescrevendo o conjunto do `db/re/`.
2. **Teto na redução de carta.** `reducao_dano_teto: 990` (99%) em
   `conf/guerra/battle_guerra.txt` desde 2026-08-14 — por enquanto, sem
   classe 4 no servidor; era `999` (99,9%) antes. Nada é imune.

### A sonda de cada uma

**Da Carta Caídos** — binária, e não depende de calcular dano nenhum: mesmo
Sura, mesmo agressor, mesmo golpe, **com e sem a carta encaixada no Cocar**. Os
dois números têm de ser **iguais**. Se com a carta doer menos, a sobrescrita do
conjunto não pegou e o `db/re/` ainda está valendo. Recarrega com
`@reloaditemdb`.

**Do teto** — o Sura completo agora soma 95%, então já não serve para testar o
teto. Para provar o piso é preciso **passar de 100 de propósito** (a Capa e o
Anel de volta, ou `@item` de uma peça de resistência) e conferir que o dano é
**pequeno mas nunca zero**. Se aparecer zero, o piso não está sendo aplicado.

### O que continua em aberto

- **Levantar os itens à venda com `bAtkRate` alto por refino.** A Lâmina Sagrada
  (`Copy_Gram`, 500009) dá 160 em +16. Não fura mais resistência, mas continua
  sendo ATQ enorme, e vale saber quantos outros existem.
- **A descrição na tela mente em dois lugares**, e nenhum dos dois tem conserto
  pelo servidor — quem escreve é o `itemInfo` do cliente:
  - a **Carta Caídos** continua anunciando "+15% Humano e Humanoide"
  - o **Cocar do Orc Herói** continua anunciando o conjunto com os 15

  Corrigir é trabalho de cliente (`itemInfo`, via `ferramentas/instala_item.py`),
  e exige fechar e reabrir o cliente. Decidir se vale.

  > A **Capa do Comandante** (20925) era o terceiro e **saiu em 2026-08-10**:
  > ali o conserto cabia no servidor, e foi feito — override em
  > `db/guerra/item_db.yml` levando a resistência a 5% para Humano **e** Doram,
  > como a tela sempre prometeu. Ver `HISTORICO.md`. **Falta a prova em tela**,
  > junto com as duas sondas acima: mesmo agressor, mesmo golpe, com e sem a
  > capa, e a diferença tem de ser de **5** pontos de resistência, não 3. O
  > tooltip não serve de prova — ele já dizia 5% quando o servidor dava 3.
  >
  > Os **três conjuntos dela com as botas do Herói** (22035, 22036, 22037)
  > tinham a mesma divergência pela metade — o valor batia, faltava o Doram — e
  > foram junto, em `db/guerra/item_combos.yml`. **Não precisam de prova em
  > tela:** as três botas não estão à venda em loja nossa nenhuma, então
  > ninguém alcança esses conjuntos hoje. Ficam certos para o dia em que
  > entrarem no mercado.
- **Calibrar resistência a elemento sabendo do teto.** Ele vale para a redução
  de carta inteira, não só para a de raça — combinação de elemento que chegasse
  a 100% agora deixa passar 0,1%. Ver `REDUCAO-DE-DANO.md` §1b.

**Ao atualizar o `rathena/`:** conferir se os **dois** enxertos do `battle.cpp`
sobreviveram (o `reducao_alcanca_percentatk` e o `reducao_piso`), e se a lista de
parcelas da linha 5535 ganhou membro novo. Parcela nova que ninguém puser no
bloco de redução repete o bug de 2026-08-09, calada.

## 1i. A redução geral de 80% — falta a medição em tela

No ar em 2026-08-10: dano final × 0,20 na guerra (`gvg_*_attack_damage_rate: 20`,
opções do rAthena) e nos mapas `pvp` (`pvp_dano_*: 20`, nossas, via
`src/custom/reducao_geral.hpp`), mais `reducao_dano_isenta_habilidade: 0` — nenhuma
habilidade escapa. Ver `HISTORICO.md` e `REDUCAO-DE-DANO.md` §1c.

**O número começou em 70% e subiu para 80% no mesmo dia**, por decisão do dono
("70 era como o bRO estava, e me parece alto ainda"). Daqui em diante **o servidor
não segue o bRO neste número** — anotado porque "voltar à referência" viraria uma
mudança sem que ninguém percebesse que é mudança.

**Compilou, subiu limpo e os onze nomes de opção foram provados aceitos** — a sonda
do nome falso está descrita no `HISTORICO.md`. O que falta é o efeito na tela.

### A sonda do valor

**É barata e é binária, e não exige calcular dano nenhum:** mesmo personagem,
mesmo golpe, mesmo alvo, **dentro e fora da arena**. Bater num alvo em Prontera e
no mesmo alvo em `pvp_n_1-5` tem de dar uma razão de **5x**.

Três coisas que enganam nessa medição:

1. **Não comparar habilidade com ataque normal.** São multiplicadores separados
   (`arma`/`magia`/`misc` contra `curta`/`longa`), e hoje estão todos em 20 — mas
   se um dia divergirem, medir um e concluir pelo outro erra.
2. **A conta de teste (grupo 99) serve aqui**, ao contrário do resto — a redução
   não é trava de item. Mas o alvo tem de ser **jogador ou monstro comum**, não
   Emperium: alvo de tipo planta curto-circuita em 1 de dano
   (`battle_calc_attack_plant`) e a razão sai 1x, o que pareceria falha.
3. **A resistência de carta multiplica por cima disto** (`REDUCAO-DE-DANO.md`
   §1c). Alvo com resistência a humano na arena embaralha a leitura — medir com
   alvo **sem equipamento de resistência**, ou aceitar que não vai dar 5x exato.

E **o piso de 1 de dano** passa a aparecer: com 80% de corte, golpe fraco encosta
no `i64max(damage, 1)`. Ver "1" na tela num golpe de raspão é o piso agindo, não
falha.

### A sonda da isenção — é a que ninguém vai pensar em fazer

A parte de "TODOS os danos" não se prova batendo com qualquer habilidade: as duas
que mudaram de comportamento são **`NJ_ZENYNAGE`** (Chuva de Moedas, Ninja) e
**`GN_FIRE_EXPANSION_ACID`** (Genético). Antes desta rodada as duas passavam
inteiras na guerra, por `IgnoreGvgReduction` do rAthena.

**O teste:** Chuva de Moedas na arena e em campo aberto. Tem de dar a **mesma
razão de 5x** que qualquer outra habilidade. Se a Chuva sair 5x mais forte que as
vizinhas, o `reducao_dano_isenta_habilidade` não pegou.

**E é o único teste que pega a morte do enxerto mais frágil do projeto:** o do
`battle_calc_gvg_damage` **substitui** uma linha do rAthena em vez de acrescentar
uma. Um merge do vendor que traga a linha original de volta compila, sobe e não
avisa — só a Chuva de Moedas denuncia.

### O que a medição da guerra tem de próprio

Na guerra o antes **não era 100%**: o rAthena já entregava 60 para habilidade e
80 para ataque normal. Então a razão esperada num castelo é **3x** para
habilidade e **4x** para ataque normal, e não 5x. Quem medir esperando 5x na
guerra vai concluir que a mudança não pegou.

### Três decisões que ficaram com o dono

1. **A Batalha Campal continua nos números do rAthena** (`bg_*` em 60 e 80). O
   pedido falava de guerra e de PvP; campal não é nem um nem outro. Se a ideia é
   "todo combate entre jogadores corta 80%", faltam as cinco linhas de conf **e**
   um sexto enxerto no `battle_calc_bg_damage`, para a isenção de habilidade cair
   lá também — a campal tem a irmã dela (`INF2_IGNOREBGREDUCTION`) de pé. Sem o
   enxerto, a Chuva de Moedas fica dominante na campal.
2. **As outras 83 arenas entraram junto**, mais o `pvp_2vs2` e os três
   `turbo_e_*`. É consequência de ligar pelo mapflag, que é o jeito certo de
   ligar; se algum dia se quiser arena com dano cheio, o caminho é outro mapflag
   ou uma lista de exceção no `reducao_geral.hpp`, e nenhum dos dois foi feito.
3. **O que não é ataque continua fora**, e isto não é ajuste de número: veneno,
   sangramento, queimadura, `bHPVanishRate` e dano de script saem por
   `status_fix_damage`, fora do cálculo de batalha, e nenhuma das cinco chamadas
   os alcança. Com 80% de corte no resto, **o dano de status passa a pesar cinco
   vezes mais em termos relativos** do que pesava antes desta rodada.

   > **A lista fechada foi levantada em 2026-08-10** — `REDUCAO-DE-DANO.md` §1d,
   > com fórmula, intervalo, se mata e quem aplica. **São 13 danos contínuos e 4
   > avulsos**, e a conclusão é que **serve pouco como alavanca**: as três
   > parcelas mais fortes (Veneno, Veneno Mortal, Bite Scar) **param em 25% de HP
   > e não matam**, e o ganho é enviesado por classe — Guilhotina Cruzada em
   > primeiro, depois Cavaleiro Rúnico/Ranger e Ladrão. Nenhum dos números é
   > configurável: são literais no `status.cpp`, e mexer é `src/custom/` mais
   > recompilar. **Nada foi mexido**; a seção existe para a decisão ser tomada
   > com os números na mão.

---

## 1j. A Cotovelada Ascendente escapa da redução de 80% — e é bug

Achado em 2026-08-10, ao levantar o inventário da §1d. **Não foi corrigido**, e
está separado do §1i porque não é decisão de balanceamento: é furo.

**`SR_CRESCENTELBOW` (Cotovelada Ascendente, Sura)** entrega o dano por
`battle_fix_damage` (`battle.cpp:5247`), que chama `battle_damage` direto e
**não passa pelo `battle_calc_damage`** — onde moram três das nossas quatro
chamadas. Então ela sai sem os 80% na arena e sem os 80% na guerra.

**Metade dela é agravante e metade é atenuante:**

```
rdamage = battle_calc_base_damage(...) * ratio / 100      <- nasce aqui, NUNCA reduzido
        + wd->damage * (10 + val1 * 20 / 10) / 10          <- vem do dano ja reduzido
```

A segunda parcela é proporcional a um dano que já levou o corte; a **primeira
não**, e o `ratio` dela vai a **5000%** (o teto do próprio rAthena, `HP do alvo /
100 × nível da habilidade × nível base / 125`).

**As vizinhas de seção estão certas e não devem ser "corrigidas" junto:**
Instinto de Defesa (`ST_REJECTSWORD`) devolve 50% de um dano já reduzido;
Reflect Damage, Devoção e Water Screen **redirecionam** o número já reduzido para
outro alvo. Só a Cotovelada cria valor novo.

**O conserto provável** é uma quinta chamada de `reducao_pvp` sobre o `rdamage`
antes do `battle_fix_damage` da linha 5247, mais o equivalente para a guerra —
mas isso precisa ser pensado com a §4d na mão, porque o bloco inteiro é
contra-ataque e a conta de "de quem é este dano" não é óbvia. **Não fazer no
susto.**

Enquanto não for feito: Sura com Cotovelada é o furo conhecido da arena, e é a
primeira explicação a testar quando alguém disser que um Sura mata rápido demais.

---

## 1k. Duas peças foram para a vitrine que o pedido não pediu

Da rodada de 2026-08-12. **Não é bug e não trava nada** — as duas estão à venda,
equipam e desenham. É uma decisão de gosto que ficou com o dono do projeto,
registrada aqui para não morrer no comentário da loja.

O pedido agrupou os itens por slot, e em quatro deles o grupo não batia com o
`Locations:` do `item_db`. Em **dois** o nosso vendor é que estava errado (o bRO
concordava com o pedido) e a correção foi um override — Cachecol Glorioso e
Coleira do Vassalo foram para o Camareiro, e não há nada em aberto neles.

Nos **outros dois**, `item_db` e bRO concordam entre si e é o pedido que destoa:

| item | pedido em | `item_db` e bRO dizem | foi para |
|---|---|---|---|
| Gata Branca (31452) | visual cabeça baixo | `Costume_Head_Mid` | **Adereceiro** (meio) |
| Manto do Herói (420112) | cabeça meio | `Head_Low` | **Retoqueiro** (baixo) |

Foram para a loja do `Locations:` porque na outra elas não equipariam no slot da
placa — `CLAUDE.md` §4.14, o mesmo caminho da Máscara de Minorous em 2026-08-09.
O Manto do Herói ainda é **equipamento** e não visual (DEF 2, peso 10, nível
100), o que o tira de vez das lojas de 1 zeny da fileira de visual.

**Se o dono quiser as peças nas vitrines do pedido**, o que muda de lugar é o
`Locations:` num override em `db/guerra/item_db.yml` — com o `false` explícito
no slot velho, porque `Locations` é OR e não atribuição —, e só depois a linha
da loja. Mexer só na linha da loja põe a peça numa vitrine em que ela não
equipa, que é o defeito que a regra existe para evitar.

---

## 1l. O Túmulo do Monarca — falta ver no jogo

Feito em 2026-08-12 (`HISTORICO.md`, "O Túmulo do Monarca abre todo dia").
**Nada disto subiu.** Tudo conferido em disco; o que só a tela decide está
embaixo.

### Os comandos, nesta ordem

```
@reloadinstancedb   # o Id 46 vira "Túmulo do Monarca" (existe, não precisa reiniciar)
@reloadscript       # os NPCs nossos e a tradução do miolo
```

O `@reloadinstancedb` **antes** do `@reloadscript`: o nome da instância é chave,
e o `instance_create` resolve por string contra o que estiver carregado.

Não há mais `@reloadquestdb` a dar: a instância deixou de usar quest, e o
override da 12379 saiu do `db/guerra/quest_db.yml`.

### O que só a tela decide

1. **Os três NPCs aparecem, e os três do rAthena sumiram.** Mariaju em
   `gef_tower 56,170`, Colecionadora em `57,167`. A porteira velha ficava em
   `57,170` — uma célula ao lado da nossa —, então **duas mulheres de avental
   lado a lado quer dizer que o `disablenpc` não pegou**.

2. **A prova da armadilha, e é a mais importante:** entrar na instância e olhar
   `1@md_gef 110,129`. Tem de haver **uma** Mariaju, não duas. Duas quer dizer
   que o `disablenpc instance_npcname("Marry Jay#0_1")` do `OnInstanceInit` não
   rodou — e aí o seletor velho volta a recusar quem tem menos de nível 130,
   que é exatamente o que este trabalho existiu para tirar. Ver `CLAUDE.md` §5.

3. **Entrar com personagem abaixo de 130**, que era o ponto do "sem trava":
   tem de passar pela porta **e** conseguir escolher a dificuldade.

4. **Entrar duas vezes seguidas com o mesmo personagem** — é o que a
   remoção da espera comprou, e o teste é imediato: terminar (ou deixar
   fechar) a memória e abrir outra na hora, sem recusa. Se a Mariaju disser
   que já há uma tumba aberta, é o limite do sistema de instância, não a
   espera: a memória anterior ainda está de pé.

5. **A Colecionadora encanta.** Com 10 Pedra Bruta e 100.000z, num acessório
   equipado. É o motivo de a instância ter sido pedida, então é o teste que
   mais importa. Ela se chama **Colecionadora** e fala português; se aparecer
   "Amateur Collector", o `disablenpc` do `OnInit` dela não pegou e há duas
   NPCs empilhadas em `gef_tower 57,167`.

5b. **Um acessório ESPECIAL encanta**, e não só um comum — é o que mudou o
   desenho da NPC. Um anel zodiacal serve (Anel de Câncer, de Touro, de
   Virgem…), ou o Anel de Iansã, ou as Luvas Imperiais. Se recusar com "Eu não
   consigo encantar este…", o `.aceitos` do `OnInit` não carregou.

5c. **O Anel do Monarca ainda encanta DOIS slots**, um de cada vez, com escolha
   de categoria — é o único item com regra própria, e a troca do `switch` por
   `inarray` passou perto dele. Reset dele é 80%; dos outros, 20%.

5d. **Falhar um reset NÃO pode mais comer o acessório** — é a única mudança de
   regra da NPC, e a que mais dói se estiver errada. Num acessório comum a
   falha vem em 4 de 5 tentativas, então o teste é barato: resetar até falhar e
   conferir que a peça **volta para a bolsa com o encanto intacto**. O que se
   perde é só o custo. Conferir também que o aviso vermelho antes de confirmar
   já não promete destruição.

6. **O cadáver do Estranho** (`1@md_gef 183,222`) larga Pedra Bruta, e **os
   baús** largam também depois de 100 mortes. Os baús são o teste do
   `strnpcinfo(2)`: os quatro `fd_box1`..`4` ficaram sem traduzir de propósito,
   e se algum tiver escapado o baú aparece e **não larga nada**.

### Oito acessórios do bRO ficaram de fora, e não por escolha

A lista de "Acessórios Especiais" da bROWiki tem 101 nomes. **93 entraram**
(mais o Anel Imperial em duas versões, dando 94 IDs). Estes oito **não existem
no `item_db` deste rAthena** — não é falta de tradução, é ausência do vendor:

| item do bRO | procurado por |
|---|---|
| Anel de Carnium | `carnium` — só existe o minério 6223 |
| Brincos de Carnium | idem |
| Colar de Juperos | `juperos` — nada no `item_db` inteiro |
| Luvas de H. Motto | `motto` — nada |
| Luvas de Thor | `thor` — só katar e cajado sem relação |
| Anel de Capricórnio | `capricorn` — os outros onze zodiacais existem |
| Amuleto Caolho | `oneeye`, `cyclop`, `charm` — nada que sirva |
| Broche do Reino | `kingdom`, `brooch` — nada que sirva |

**Como entrar com eles, se o dono quiser:** cada um é uma entrada nova em
`db/guerra/item_db.yml` (nome PT, `Locations: Accessory`, bônus) mais arte, mais
uma linha no `.aceitos` do `OnInit` da Colecionadora. É o fluxo normal de item
novo — `ARQUITETURA.md` §4, "Um item novo vive em até 6 lugares". Sem isso, o
jogador que vier do bRO procurando encantar um Colar de Juperos não vai achar
o item no servidor, quanto mais o encanto.

### Uma suposição para conferir: o "Anel da Colheita"

Virou o **490272**, que o nosso vendor chama de "Harvest Festival". É o único
acessório de colheita do `item_db`, mas **o nome não bate** — é o único dos 94
IDs que não foi provado, os outros 93 saíram de nome exato ou de `AegisName`
conferido um a um.

Se estiver errado, o estrago é pequeno e do tipo certo: um acessório a mais
aceito para encanto. A conferência é olhar o 490272 em jogo e ver se é o anel
que o bRO chama de Anel da Colheita. Se não for, sai uma linha do `.aceitos`.

### O que ficou de fora, de propósito

- **O Túmulo não entrou no Teleportador da Ordem** (`auction_02 37,39`), que
  hoje leva às catorze portas. Seria uma linha em cada array — mas a §4.11 do
  `CLAUDE.md` existe porque mexer naqueles arrays já errou os catorze destinos
  de uma vez. Se for entrar, entra pelo laço que monta o menu a partir do
  array, nunca pela string do menu.
- **O Homem Suspeito do bRO** (`gef_tower 36,177`), a segunda NPC de encanto.
  O NPC do rAthena já faz os dois papéis com as mesmas tabelas; separar seria
  duas NPCs idênticas a nove células uma da outra.
- **A lista de "Acessórios Comuns" da bROWiki não foi cruzada com a nossa.** O
  print que chegou era o dos Especiais; a metade dos Comuns ficou cortada acima.
  Os 122 do rAthena estão sendo tomados como equivalentes a ela, e é bem
  possível que sejam — mas não foi provado. Um print daquela metade fecha.
- **A dificuldade "Nv 200 +" não pede mais nível 200**, porque "sem trava" foi
  a decisão. Se na prática isso virar problema (grupo de nível baixo abrindo a
  fila difícil e travando a corrida), a volta é uma linha no `case 3` do
  seletor em `npc/guerra/tumulo_do_monarca.txt`.

---

## 1m. O Cassino de Comodo — falta ver no jogo (escrito em 2026-08-12)

`npc/guerra/cassino_de_comodo.txt`, ligado no `scripts_guerra.conf`. Dezesseis
NPCs em `cmd_in02`: três recepcionistas, quatro garçonetes e sete mesas de
blackjack que cobram e pagam em Moeda Nova (30998). O histórico da rodada está
no `HISTORICO.md`.

**Nada disto foi visto em jogo ainda — o servidor não foi recarregado.** O
primeiro passo é `@reloadscript` e ler o log procurando por `Unknown syntax`
(§5: uma linha ruim mata o arquivo inteiro, e a mensagem fica soterrada sob
avisos inofensivos dos mercados).

O que conferir, em ordem de risco:

- **A mão inteira de blackjack, das duas mesas.** É o único script do projeto
  com laço, subrotina e baralho — e o que mais tem como quebrar em silêncio.
  Jogar até ver: um 21 natural, um estouro do jogador, um estouro do crupiê e
  um empate. O texto das cartas ("A de Copas, 7 de Paus") sai do `S_Mao`; carta
  repetida na mesma mão quer dizer que o sorteio de naipe furou.
- **O `rand(1)` já mordeu uma vez** (§5). Se a mão morrer no meio com o diálogo
  aberto e a aposta cobrada, é isso — procurar `range is too small` no log.
- **Se o vies está agindo.** Não se prova numa sessão: 5% e 10% só aparecem em
  algumas centenas de mãos. O que dá para conferir barato é o extremo — jogar
  vinte mãos em cada andar e ver se a de cima *parece* pior. Divergência séria
  entre os dois andares é o sinal de que está funcionando; igualdade é o sinal
  de que o argumento do `callfunc` não chegou.
- **Os sete crupiês soltando `/$` de 3 em 3s e as quatro garçonetes soltando
  `/bj2` de 4 em 4s.** O `ET_CHUPCHUP` foi deduzido da ordem do enum, não visto
  em tela — se sair o emote errado é trocar um nome no `OnTimer4000`.
- **O drink.** Aceitar deve virar Deviruchi ou Poring por 20 minutos, e beber de
  novo deve trocar o disfarce (a trava é do próprio `transform`).
- **O `Shalone#cmd` sumiu de 178,92** e a mesa nasceu no lugar dele, sozinha.
  Dois NPCs empilhados ali querem dizer que o `disablenpc` não pegou — e nesse
  caso há um `debugmes` no log dizendo isso.
- **As três recepcionistas**, uma por porta: 211,100 (leste), 174,131
  (principal) e 144,100 (oeste). As de 211,100 e 144,100 ficam três células ao
  norte da chegada da sua porta, no fundo de um nicho; a de 174,131 fica num
  bolsão fechado a leste por parede, e **quem chega pelo warp de 178,132 está
  do outro lado dessa parede**. Vale olhar se ela é vista de fato.
- **A animação de vitória** — `EF_THROW_MULTIPLE_COIN` (982) na vitória comum e
  `EF_LEVEL99_4` (362) no 21 natural. Os dois números são palpite informado, não
  foram vistos em tela: se algum não desenhar nada neste cliente, sai uma linha
  de erro no log e a mão segue normal. Ver o item logo abaixo.

### A animação que o pedido queria, e por que ela não entrou

O pedido apontou o efeito de sucesso da janela de encantamento
(`data\texture\effect\ui_enchant\ui_enchant_success\ui_success_y.tga`). O que
se apurou, e vale para qualquer efeito futuro:

- **Ele é alcançável em princípio.** Há um `ui_enchant_success.str` na mesma
  pasta, e o caminho dele está na tabela de efeitos do exe, encostado em
  entradas de efeito de mundo comuns. `.str` é o formato que o `specialeffect`
  desenha.
- **O número dele não sai offline.** A tabela é preenchida por uma corrida de
  517 instruções de 30 bytes no `.text`, cada uma um `push offset "<caminho>"`
  seguido de `mov [ebp-4], N`. O `N` é consecutivo (1100 para o nosso), mas é o
  contador de desmontagem de exceção do compilador, **não** o número do efeito:
  cruzando os 517 nomes da corrida com os `EF_` do rAthena naquele mesmo
  número, batem **zero**.
- **Como achar, em uma rodada:** `@effect <n>` in-game. Achou o clarão dourado,
  é trocar os dois números no topo da `F_CassinoBlackjack`.
- **E há um teto:** o servidor não manda efeito acima de **1126**. O
  `buildin_specialeffect` (`script.cpp:15605`) e o `@effect`
  (`atcommand.cpp:6027`) recusam `>= EF_MAX`, e o `EF_MAX` do nosso rAthena é
  1127 — enquanto o cliente tem ~1460 efeitos `.str`. Se o do encantamento
  estiver acima do teto, alcançá-lo custa levantar o `EF_MAX` em
  `src/map/script.hpp` e recompilar, o que é enxerto em arquivo do rAthena e
  precisa ser decidido.

### O que ficou de fora, e foi decisão

- **A máquina caça-níquel.** Pedida na mesma rodada e adiada pelo dono: a ideia
  é reaproveitar a roleta que o cliente já desenha (a da captura de pet) em vez
  de inventar interface, e isso é uma sessão inteira. O sprite está livre e
  conferido: **563 (`2_SLOT_MACHINE`)**, o caça-níquel com letreiro JACKPOT.
  Coordenada não foi escolhida.
- **Treze falas curtas dos cinco NPCs de missão continuam em inglês** — `Wha...?`,
  `Hmm...`, `Excuse me.`, `Fine, fine.` e irmãs. Não é descuido: tradução vale
  por **texto** e não por ocorrência, e essas treze são compartilhadas com o
  resto das quatro cadeias de missão. Traduzi-las poria português no meio de
  18 mil falas em inglês. A lista fecha em `Man#megin` com `Wha...?` na segunda
  linha dele, que é a mais visível das treze.

---

## 1n. Quatro pedidos de 2026-08-12 — falta ver no jogo

### O CTRL+1 está gravado no exe — falta apertar a tecla

`ferramentas/ordena_bandeiras_ctrl.py` **foi aplicado em 2026-08-12 23:51**,
com o cliente fechado (o exe fica travado enquanto ele roda). Backup em
`GuerraDoEmperium.exe.BACKUP-bandeiras-20260812-2351`; reler a tabela do disco
devolve as nove entradas novas.

**Isso não prova nada.** Patch de exe "aplicado e confirmado" não é patch com
efeito, e script que confere o próprio trabalho não prova nada (`CLAUDE.md`
§5) — o `ajusta_tamanho_fonte.py` respondia *"8 ja desviadas"* e era inócuo. O
que falta é **abrir o jogo e apertar CTRL+1**. A ordem esperada, das nove
teclas:

| tecla | bandeira | | tecla | bandeira |
|---|---|---|---|---|
| CTRL+1 | **Brasil** | | CTRL+6 | Coreia |
| CTRL+2 | Indonésia | | CTRL+7 | Índia |
| CTRL+3 | Filipinas | | CTRL+8 | Bandeira 8 |
| CTRL+4 | Malásia | | CTRL+9 | Bandeira 9 |
| CTRL+5 | Cingapura | | | |

Se CTRL+1 sair certo e as outras não, o patch pegou e o que falhou é outra
coisa; se **nenhuma** mudar, o handler encontrado não é o que a tecla usa — e
aí vale a lição do `ajusta_tamanho_fonte.py`: pôr uma marca que não dependa do
efeito procurado (apontar um caso para uma emoção óbvia, um dado ou um coração)
antes de gastar rodada calibrando.

**E fica uma pergunta em aberto que não foi atrás:** o `data\clientinfo.xml`
diz `<servicetype>brazil</servicetype>` e o jogo se comporta como `korea`. O
patch é imune a isso de propósito, mas o servicetype gateia mais coisa no
cliente do que bandeira. Se algum dia aparecer outro recurso "que existe e não
liga", é o primeiro lugar para olhar — o `clientinfo.xml` do GRF vem com DES e
não se leu.

### A Máquina — duas linhas novas e uma arte trocada

`@reloadbarterdb` (**não** `@reloadscript`) e o jogo **fechado e reaberto**,
porque a arte e o nome vêm do `itemInfo.lua`. O que conferir na janela de troca
das duas Máquinas (prontera 167,199 e comodo 214,185):

- **Amuleto de Ziegfried (5 Moedas) e Goma de Mascar (5 Moedas)** aparecem no
  fim do grupo de consumíveis, com nome em português e ícone — o nome sai do
  cliente, não do servidor (§4.9).
- **Os dois permanentes continuam nos dois últimos lugares.** Eles desceram de
  `Index` 18/19 para 20/21; se aparecerem fora de ordem, foi a renumeração.
- **O Amuleto de verdade funciona:** morrer com um na bolsa e levantar no
  lugar, com HP e SP cheios. Quem o consome é o `pc_dead` no C++, então isto
  não se testa lendo script nenhum. **Na conta de teste o resultado não vale
  para restrição de item** (§4.7), mas para este efeito vale.
- **A Cx. Poção de Guyak (30996) agora tem a cara da Poção**, e não mais a da
  caixa genérica. Se vier caixa de erro no lugar do ícone, o `resourceName`
  copiado não resolveu — `estado_item.py --id 12710` dizia "4 de 4 ok".

### O Guia de Prontera — dois bugs consertados, falta o segundo teste

`npc/guerra/guia_de_prontera.txt`, ligado no `scripts_guerra.conf`. Cinco NPCs,
três categorias, 26 lugares e 30 marcas de mini-mapa.

**O primeiro teste em jogo derrubou dois defeitos, e os dois já estão
consertados** (o porquê de cada um está no `HISTORICO.md` e a regra geral subiu
para o `CLAUDE.md` §5):

1. `disablenpc "Guide#01prontera"` errava o nome — o nome único é o de **depois
   do `::`**, `GuideProntera`. Um Guia em inglês ficava de pé empilhado no
   nosso, na célula da praça.
2. `if (.@i == 0 || .dono[.@i - 1] != .@g)` estourava em `.dono[-1]`, porque o
   `||` do script do rAthena **não faz curto-circuito**. O `OnInit` morria ali
   e a janela de menu abria em branco.

**Falta rodar `@reloadscript` de novo e conferir**, começando por procurar
`Unknown syntax`, `index out of range` e `non-existing NPC` no log — o arquivo
usa construções que nenhum outro NPC nosso usa (`explode`, `atoi`,
`deletearray`, `select` de string montada em laço), então é o de maior risco da
leva.

Em ordem de risco:

- **Se o menu de cima abre com cinco linhas** — as três categorias, "Limpar as
  marcas" e "Sair". Caixa em branco quer dizer `OnInit` morto de novo, e a
  causa vai estar no log, longe da caixa.
- **Se os cinco Guides do rAthena sumiram.** Se sobrar um em inglês empilhado
  no nosso, é nome errado outra vez — são `GuideProntera` mais
  `Guide#02prontera` a `Guide#05prontera`.
- **Se cada linha do menu leva ao lugar que promete.** É o risco que a regra
  §4.11 existe para cobrir, e o `debugmes` do `OnInit` só pega desalinhamento
  de tamanho, não de conteúdo. Os três de "Serviços Principais" são os que
  ninguém mais conferiu: Centro da Ordem 165,168, Arena 147,180, Máquina
  167,199.
- **Se as trinta marcas cabem.** Trinta é o que o Guia do rAthena já usava,
  mas ele nunca marcou trinta *de uma vez* numa sessão. Abrir tudo, categoria
  por categoria, e ver se as últimas ainda pintam — e se "Limpar as marcas"
  apaga todas.
- **Se os links de navegação clicam.** O `F_Navi` só devolve link com
  `PACKETVER >= 20111010`; o nosso é 20211103, então deveria. Os dois `.nav$`
  (a segunda Biblioteca e o Criador de Pecopeco de Cruzados) são link **sem**
  marca, de propósito.
- **Se algum `mes` colou na linha anterior.** Nenhum começa com espaço, mas as
  notas são longas e quebram sozinhas pela largura da caixa (§5).

**Uma escolha de rótulo ficou por minha conta e pode ser trocada numa linha:**
o pedido dizia *"Stuffs (Máquina)"* e o menu diz **"Máquina"**, que é o nome que
o jogador lê sobre a cabeça da NPC. Se a intenção era o rótulo "Stuffs", é
trocar a terceira entrada do `.nome$` no `OnInit`.

---

## 1o. Os guardiões que crescem com a defesa — falta ver no jogo (2026-08-13)

**Está compilado, linkado e no ar.** O map-server foi reconstruído e os quatro
servidores subiram; o log da subida já confirma o que dá para confirmar de fora
do jogo:

```
avisos de mob_spawn_guardian: 152    mapas: 19    todos com 8: True
kriemhild presente? False            Unknown syntax: 0
```

Ou seja: os 152 guardiões nasceram, oito em cada um dos dezenove castelos, o
Kriemhild ficou intocado, o arquivo de NPC foi lido inteiro e as quatro colunas
de posição batem (nenhum `debugmes` da conferência da regra §4.11).

**O que isso NÃO prova:** que a escala pegou, que o sprite do Zelador desenha, e
quanto dano um golpe tira. É o que falta, e só se vê em jogo.

**O que entrou:**

| Peça | Onde |
|---|---|
| A escala em si | `rathena/src/custom/guardiao_do_castelo.hpp` |
| Os quinze números | `rathena/conf/guerra/battle_guerra.txt`, bloco final |
| Os dois enxertos | `rathena/src/map/status.cpp` (`CLAUDE.md` §2) |
| Os dezenove museus | `rathena/npc/guerra/guardioes_dos_castelos.txt` |
| Os castelos desligados | `rathena/npc/scripts_guild.conf`, 19 linhas comentadas |

**O que conferir em jogo, e por que cada um:**

- **Se o Zelador aparece em `prt_gld 153,133`, e desenhado por inteiro**
  (movido de 136,66 em 2026-08-14, a pedido do dono). O
  sprite `EP17_2_GUARDIAN_PARTS` (20679) foi conferido offline pelas três
  tabelas — `npcidentity.lub`, `jobname.lub` e o `.spr`/`.act` no GRF —, e
  `CLAUDE.md` §5 é explícito em que **as três darem OK não é prova de que
  desenha**. Vale olhar também se ele está **enterrado no chão**: é sprite de
  monstro usado como NPC, e a armadilha do `.act` com `y = 0` mora exatamente
  aí (`ferramentas/levanta_sprite_npc.py` conserta, e o override é do cliente,
  fora do git).
- **Se os 152 guardiões nasceram.** Falar com o Zelador: ele lista os dezenove
  castelos com a defesa de cada um e quantos guardiões estão de pé. **Se algum
  aparecer com defesa diferente de 100, o `SetCastleData` não pegou** e a escala
  saiu no patamar errado sem nada denunciar — é a sonda principal deste NPC.
- **Se a escala pegou de verdade.** `@mobinfo` num guardião de museu tem de
  mostrar 15 milhões de HP. Se mostrar 15.670, o enxerto do `status.cpp` não
  está rodando ou o `guardiao_escala` ficou em 0.
- **Quanto dano um golpe tira.** Com defesa 100 devem passar **10% do dano
  bruto** (50% do guardião × os 20% da guerra). Um golpe de 500.000 brutos tem
  de tirar cerca de **50.000**. É o número que fecha as duas contas de uma vez —
  se der 250.000, a redução do guardião não está sendo aplicada; se der 500.000,
  nem ela nem a da guerra. No total, **150 milhões de dano bruto derrubam um
  guardião do topo** — vezes oito por castelo.
- **A velocidade de ataque.** ASPD 178 é um golpe a cada 440 ms — pouco mais de
  dois por segundo.
- **Se eles acertam agora.** Era o problema da primeira rodada: dois dos três
  guardiões batiam no piso de 5% do emulador. A precisão passou a ser absoluta,
  630 no patamar 10. **Este é o número que mais provavelmente vai precisar de
  ajuste**, porque a esquiva real dos jogadores daqui nunca foi medida — e a
  fórmula do renewal é uma subtração travada em 5 e 100, então cem pontos cobrem
  de "nunca acerta" a "nunca erra". Para calibrar: olhar a **Esquiva** na janela
  de status do personagem e pôr `guardiao_hit_base` em `esquiva + a chance
  desejada`. Pega com `@reloadbattleconf`, mas só no próximo spawn — matar o
  guardião ou esperar o Zelador repor.
- **Se o Kriemhild continua intocado** — com Emperium, Kafra, Gerente e
  bandeiras, e com a defesa que estiver investida. Ele é a única linha de
  castelo que ficou de pé no `scripts_guild.conf`.
- **Se os dezenove mapas estão de fato vazios** de Evil Druid, Khalitzburg e
  companhia. Aqueles nascem no ramo de "castelo sem dono" do `agit_main.txt`,
  que deixou de rodar junto com os arquivos desligados.

**As duas linhas do log que já foram conferidas** (ficam registradas para a
próxima subida, porque é assim que se repete a checagem):

- `Zelador dos Guardioes: .tipo tem N e devia ter 152` (ou `.px`/`.py`) — a
  conferência de colunas paralelas da regra §4.11. **Não saiu**, que é o certo.
  Se um dia sair, uma das dezenove tabelas de posição foi digitada errada e
  **algum guardião está no lugar errado**, sem outro sintoma.
- `mob_spawn_guardian: Spawning guardian ... on a castle with no guild` — este é
  **esperado**, e o número dele é a prova: **152, oito por mapa**. Se der 304 /
  16 por mapa, o `OnInit` voltou a invocar (ele só limpa, de propósito); se der
  menos de 152, algum `guardian` falhou e aquele posto está vazio até o
  temporizador passar.

**Uma decisão que fica em aberto para depois do teste:** os três guardiões
continuam com **nome em inglês** ("Soldier Guardian" e irmãos), porque o
`db/guerra/mob_db.yml` não os traduz e este NPC lê o mesmo `getmonsterinfo` que
o `agit_main.txt` — de propósito, para os museus e o Kriemhild não divergirem.
Traduzir é uma entrada em `db/guerra/mob_db.yml`, que conserta **os dois lados
de uma vez** (`CLAUDE.md` §4.12).

**E a Guerra do Emperium 2 ficou fora**: os dez castelos de `guild2`
(Arunafeltz e Schwarzwald) continuam ligados, com Emperium e conquistáveis. Foi
escolha do dono — *"vamos começar com a 1.0 primeiro"*. Se um dia entrarem, são
mais dez linhas comentadas no `scripts_guild.conf` e mais dez blocos no NPC.

---

## 1p. O Rolinho de Arroz — ganhou fonte, e ela é uma máquina (2026-08-13)

O item **30994 `Rolinho_De_Arroz`** está de pé nas duas metades — servidor
(`db/guerra/item_db.yml`) e cliente (`itemInfo.lua`, com a arte do 555, "4 de 4
ok" no `estado_item.py`). Ele cura **100% de HP e SP**, não tem recarga, e não
se perde: `NoDrop`, `NoTrade`, `NoSell`, `NoGuildStorage`, `NoMail`,
`NoAuction`, `NoCart` — as sete travas do consumível de guerra do bRO (14524).
O histórico do porquê de cada número está em `HISTORICO.md`, "O Rolinho de
Arroz".

**A fonte apareceu no fim do mesmo dia, e não é a que este texto previa.** A
**Máquina Especial** da Sala Secreta da Ordem (`prt_in 137,108`,
`npc/guerra/sala_secreta_da_ordem.txt`) o **vende a 1 Moeda Nova**, ao lado dos
seis pratos comuns do bRO. Não é o `OnAgitEnd` do fim da guerra que o parágrafo
das decisões apontava como gancho natural: é vitrine.

Isso **responde a decisão 2 abaixo** e a responde no sentido oposto ao que a
frase "prêmio à venda deixa de ser prêmio" antecipava — o dono pediu assim, e o
registro fica dos dois lados (aqui e no cabeçalho da loja em
`barters_guerra.yml`). **As decisões 1 e 3 continuam abertas**, e a 1 mudou de
natureza: com o item comprável, "quem ganha no fim da guerra" deixou de ser a
única forma de tê-lo e passou a ser uma segunda.

Continua valendo que **nenhum monstro o dropa e nenhum NPC o paga** — a máquina
é a única saída, e ela cobra.

### Para ver em jogo, agora

```
@reloaditemdb          # o servidor
                       # e FECHAR E REABRIR O CLIENTE - o itemInfo.lua
                       # so e lido na inicializacao
@item 30994
```

O teste tem de ser numa conta **fora do grupo 99**: a de teste ignora as sete
travas (`CLAUDE.md` §4.7), então conferir "não dá para trocar" nela dá falso
negativo. O que se olha na tela: nome **Rolinho de Arroz** (não "Bolinho"),
ícone de bolinho de arroz, peso 1,0, e usar dois seguidos sem esperar — se
houver espera de 5s, o bloco `Delay:` voltou de algum lugar.

### As três decisões que ficaram com o dono

1. **Quem ganha, e quanto.** O gancho natural é o fim da guerra —
   `npc/guerra/horario_da_guerra.txt` já tem o `OnAgitEnd`. Dono do castelo?
   Todo mundo que estava no mapa? Quantos por guerra?
2. ~~**Se entra em loja.**~~ **Respondida em 2026-08-13: entra, a 1 Moeda
   Nova**, na Máquina Especial. A regra §4.16 do `CLAUDE.md` de fato não o
   alcança (ele não tem `Buy`), então o preço foi decisão nova — e a decisão
   foi 1 Moeda, o mesmo dos seis pratos ao lado.
3. **Se a ausência de recarga sobrevive ao primeiro teste de PvP.** Foi pedida
   explicitamente, e é o que separa este item dos outros três 100/100 do
   servidor — que se travam entre si pelo grupo `Reuse_Limit_F`. Pôr recarga
   depois é uma linha; tirar de quem já se acostumou, não.

### E há uma cura 100/100 a 1 zeny na loja, hoje

O **`[MEGA] Elmo de Fafnir` (400177)**, no Chapeleiro do Mercado Contemporâneo
(`npc/guerra/mercado_contemporaneo.txt:384`), traz
`autobonus3 { percentheal 100,100; … },1000,1000,"RK_REFRESH"`: cura total a
cada Refresh, para Cavaleiro Rúnico, recarga de 1s. Não foi mexido — a §4.14
manda levantar por escrito e deixar a decisão com o dono. Se o Rolinho for
calibrado sem contar com isto, a conta sai errada para uma classe.

---

## 1r. O Álbum de Cartas de Tarô — o que continua com o dono (2026-08-13)

O item **600 `Zilant_Tarot_Deck`** foi criado, a arte veio do GRF do bRO, e a
regra que ele conjura está em `npc/guerra/album_de_cartas_de_taro.txt`. **Visto
em jogo no mesmo dia**, com a sala inteira. O que sobra aqui não é bug nem
conferência que falte — são leituras que podem ser revistas.

1. **O `AegisName` é palpite.** `Zilant_Tarot_Deck` foi derivado do
   `identifiedResourceName` do cliente, porque o AegisName oficial não está em
   tabela nenhuma que alcançamos. É o **único** campo da entrada que não vem da
   descrição do bRO.
2. **Os 5% de SP saem da DESCRIÇÃO, não da página do browiki**, que não os
   cita. As duas não se contradizem — o dreno é custo do Álbum, os requisitos
   são da habilidade —, mas entrou por leitura. Tirar é apagar uma linha
   (`percentheal 0, -5;` na função).
3. **O empate entre atributos segue a ordem da página** (SOR, VIT, FOR, INT,
   DES, AGI), e a página não diz qual vence quando dois passam de 125 com soma
   prima. É leitura, não medição.
4. **As catorze cartas nunca foram percorridas uma a uma.** O algoritmo foi
   simulado sobre as 775 somas possíveis e bate com o exemplo da própria página
   (374 → 17 → Chamas de Hela), mas em jogo só se viu a carta da soma que o
   personagem de teste tinha. Se um dia houver dúvida, o teste barato é
   distribuir para uma soma conhecida: **38** tem de dar Dedicação, **25** tem
   de dar Curar (o 5 não tem linha na tabela).

### E uma armadilha para quem for mexer na função

**Nenhum `mes` ali dentro.** Se alguém acrescentar um para dizer qual carta
saiu — que é a primeira coisa que dá vontade de fazer —, o `itemskill` **para de
funcionar**: está no `doc/script_commands.txt`, *"will not work properly if
there is a visible dialog window or menu"*. O caminho, se a vontade voltar, é
`showscript` ou `specialeffect`.

**E a arte mora em `cliente\data\`, fora do git** — cliente novo perde os quatro
arquivos, calado, e a caixa de erro aparece ao **abrir a lista**, não ao usar.
Repor: `python ferramentas/instala_visual.py --id 600 --grf "<grf do bRO>"`.

---

## 1s. A missão do Amuleto — a entrada da Sala Secreta, quase pronta (2026-08-15)

`npc/guerra/menino_do_amuleto.txt` e `npc/guerra/senha_da_sala_secreta.txt`,
ligados no `scripts_guerra.conf`, mais a mudança em
`npc/guerra/guardas_do_centro.txt` (o Guarda de `auction_01 194,87` deixou de
ser `duplicate` e passou a aceitar a senha). Fecha a pendência da seção 1q
antiga: a Sala Secreta da Ordem tinha saída e não tinha entrada — agora tem,
por uma missão inteiramente narrativa (história 100% inventada, pedida pelo
dono em 2026-08-14), sete NPCs em três mapas e um teste de guardião.

**O dono já jogou a cadeia inteira uma vez** (2026-08-14/15) e trouxe seis
correções de texto/posição/facing (ver `HISTORICO.md`, "O que o teste em jogo
corrigiu") mais um achado sério: **o guardião de teste batia com menos de
2.000 de dano**, apesar do script pedir 40.000-60.000 por `setunitdata`. Não
era calibragem — era um bug do engine (`setunitdata` de ATK/HIT/AMOTION/
ADELAY escreve em `base_status`, o combate lê `status`, e o recálculo que o
próprio `setunitdata` dispara **exclui de propósito** o flag que copiaria um
no outro). Corrigido movendo o ATQ para `db/guerra/mob_db_guerra.yml` (novo -
ver CLAUDE.md §2), que é lido certo no spawn.

**Revisado em 2026-08-14, contra a tabela real de `guardiao_do_castelo.hpp`**
(o pedido original de HP era de memória e não batia com o patamar 100 real).
Números de hoje: HP 15 milhões (não 50), redução 90%, ATQ ~5.000 de média,
ASPD 178 (AttackDelay 440/AttackMotion 220) e precisão ~575 (Dex 369) — os
dois últimos deixaram de ser "decisão de escopo": foram consertados na mesma
rodada, pelo mesmo caminho do ATQ (mover pro `mob_db_guerra.yml`, ver o
cabeçalho de lá). Os detalhes completos estão no cabeçalho do
`senha_da_sala_secreta.txt`.

**O que ainda falta conferir:**

- **O teste do guardião, de novo** — é a parte que mudou por último e a
  única ainda não vista em jogo com os números novos. Descer o
  `@reloadscript` (que também recarrega o `mob_db_guerra.yml` por ele estar
  no import do `mob_db.yml` — conferir se pega sem reiniciar, ou se precisa
  de `@reloadmobdb`/reinício) e medir o dano que o guardião dá: deve rondar
  5.000 por golpe, não os menos-de-2.000 de antes; que ele bate uns dois
  golpes por segundo (ASPD 178); que ele acerta com folga (precisão ~575);
  e que os 15 milhões de HP com 90% de redução dão um combate longo, não
  instantâneo nem impossível.
- **O balão "Quest" sobre a Criança** (`npctalk "Quest"` a cada 5s, pedido em
  2026-08-15) — nunca visto em jogo. Conferir se aparece e se o intervalo
  não incomoda.
- **As quatro coordenadas do Cassino de Comodo (Suad, Assessor, Bolãozão,
  Maram) continuam sem conferência célula a célula** — o `cmd_in02.gat` tem
  o bit DES e o `ferramentas/grf.py` não lê esse tipo de entrada (CLAUDE.md
  §5). O dono já andou por ali no teste e não reportou problema, o que é
  evidência forte de que estão andáveis, mas não é a mesma coisa que medir.

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

**Um décimo-sétimo grupo entrou em 2026-08-12: `monarca`**
(`npc/re/instances/FridayDungeon.txt`, o Túmulo do Monarca), **fechado e
aplicado** — 188 de 205, os 17 restantes em branco de propósito, todos
técnicos. Ele não é uma das dezesseis da Ordem: entrou junto com a abertura da
instância, e o `--estado` marca **91,7%** porque conta os brancos como não
feitos. Ver `CLAUDE.md` §4.12, segundo travessão.

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

## 4. O manto cosmético — o teto de 120 do cliente, e 31 slots até acabar

Aberto em 2026-08-05. A ferramenta que faltava foi escrita em 2026-08-09, e no
mesmo dia a medição em tela mostrou que **o problema não era o que se pensava**.
O relato completo está no `HISTORICO.md`, seção da rodada de 2026-08-09.

| camada | chapéu | manto | estado |
|---|---|---|---|
| nome e descrição | `itemInfo.lua` | igual | — |
| slot de visual | `accessoryid.lub` + `accname.lub` | `spriterobeid.lub` + `spriterobename.lub` | resolvido |
| ferramenta do slot | `estende_accessoryid.py` | `estende_robeid.py` | resolvido |
| arquivos de arte | 4 de item + 4 de cabeça | 4 de item + sprite de manto **por classe** | resolvido |
| ferramenta da arte | `instala_visual.py` | `instala_manto.py` | resolvido |
| **teto de slot** | 2192 → estendível | **120, e não estende** | **em aberto** |

### 4a. O teto de 120 — o que está de fato aberto

**Este cliente não desenha manto com slot acima de 120.** Não é a tabela: ela
foi levada a 158 entradas contíguas, o cliente a leu (conferido pelo horário de
acesso do `.lub`) e nada mudou. As outras explicações caíram uma a uma —
`CLAUDE.md` §5 tem a lista.

A saída de hoje é **reaproveitar slot morto**: dos 120 que o cliente aceita, 40
não têm arte nenhuma neste cliente e já não desenhavam nada. Nove foram usados
em 2026-08-09. **Sobram 31.**

**O conserto de verdade é patch de exe**, e não foi feito. A busca pela
constante foi tentada e abandonada: sem desmontador, varredura de bytes em
volta da referência a `ReqRobSprName` (arquivo `0x008278ca` no
`Ragexe_unpacked.exe`) só devolve `cmp` que não são instrução. Quem for tentar
começa por ali, e com desmontador de verdade. O prêmio são os outros 138 slots
que o bRO conhece — e, com eles, a varredura abaixo.

### 4b. O `varre_cosmeticos.py` ainda não classifica manto como `curavel`

Ele se recusava a isso porque a cura não existia. Agora existe, mas é **cura de
estoque limitado**: cada manto novo queima um dos 31 slots restantes. Prometer
"curável" para 45 mantos quando só cabem 31 é o mesmo erro de prometer cura que
não há como cumprir — então a mudança certa **depende do patch de exe**, ou de
o script passar a contar o estoque.

Nada disso é bloqueio: manto pedido item por item continua entrando pelo
caminho de sempre, que é o que as rodadas de 2026-08-08 e 2026-08-09 fizeram.

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

## 4b. NPC sentado no sofá — o desenho está pronto, falta uma prova

Aberto em 2026-08-11, a pedido do dono: pôr personagens sentados no sofá da
alcova norte do Centro da Ordem (`auction_01 179.5,84.0`). Não é para agora —
fica registrado para quando for, porque **a parte cara já foi medida**.

### O desenho, e ele é uma divisão limpa entre cliente e servidor

| metade | onde | o quê |
|---|---|---|
| **altura** | override de `.gat` em `cliente\data\` | levanta a célula, e com ela a entidade desenhada nela |
| **bloqueio** | `setwall` no `centro_da_ordem.txt` | fecha a pegada do móvel do lado do servidor |

**Só as ALTURAS podem entrar no `.gat` do cliente — nunca o tipo da célula.**
O `.gat` é o arquivo de onde o *cliente* tira as duas coisas, e o servidor lê o
`map_cache.dat`, que guarda **só o tipo**, não as alturas. Então mexer em altura
é invisível para o servidor, e mexer em tipo faz as duas metades divergirem em
silêncio — a mesma razão pela qual bloqueio é `setwall` e não `setcell`
(`CLAUDE.md` §4.15).

**O NPC não precisa da célula andável.** NPC nasce e é clicável em célula
bloqueada — então dá para fechar a pegada inteira do sofá e pôr os NPCs em cima
mesmo assim. Deixar as células de assento andáveis só é preciso se a ideia for
o **jogador** poder subir no sofá também; aí ele sobe de verdade, porque o
cliente vai deixar.

### Os números já estão medidos

- O assento (`Object001` do `sofa_01.rsm`) tem o topo a **9,62 unidades** da
  base do modelo.
- O chão em `179,84` está em **4,0** no `.gat`.
- Em RO **mais negativo é mais alto**, então a célula de assento iria para
  cerca de **−5,6**. Isso é praticamente o pedestal da fonte (−5,0): o valor
  está no vocabulário do próprio mapa.
- As células de assento são as **duas que o dono já tinha nomeado**: `179,84` e
  `180,84` caem no meio do sofá (que cobre `x176,7..182,2`), com os braços em
  `x177` e `x182`.

### O que falta provar, e a sonda é de graça

**Que o cliente tira a altura da ENTIDADE do `.gat`, e não do `.gnd`.** Offline
dá para mostrar que são camadas separadas — neste mesmo mapa **277 células têm
`.gat` e `.gnd` discordando, 132 delas andáveis** —, mas isso não é prova de
efeito, que é a regra de sempre.

A sonda não custa arquivo nenhum, porque a Gravity já deixou o caso pronto:

```
@warp auction_01 20,52
```

Ali o `.gat` diz **−7,1** e o `.gnd` diz **4,0** — 11 unidades, mais de duas
células, e a célula é plana nos quatro cantos (não é média de rampa). Se o
personagem aparecer **flutuando acima do piso desenhado**, o cliente usa o
`.gat` e o desenho acima funciona inteiro. Se ele pisar no chão, a altura vem do
`.gnd` e o caminho é outro.

A célula fica no **bloco oeste**, que está selado — só se chega por `@warp`, e
sair é `@warp` de volta. Não há nada a desfazer.

### Duas ressalvas para quando for feito

1. **O sprite vai ficar EM PÉ, não sentado.** Não há sprite de NPC sentado neste
   cliente — varrido o `npcidentity.lub` inteiro, **zero** entradas com `SIT`,
   `CHAIR` ou `THRONE`. O efeito é "de pé na altura do assento", que da câmera
   isométrica costuma ler como sentado se a altura estiver certa; afundar um
   pouco o valor é o ajuste de sempre, e é ajuste de tela.
2. **Vira o SEGUNDO arquivo de cliente fora do git** para este mapa (o `.rsw` já
   é o primeiro). Cliente novo perde os dois, calados. E o `edita_mapa.py` hoje
   diz por escrito que **não toca o `.gat`** — então isso é capacidade nova na
   ferramenta, e precisa nascer com receita versionada como o resto.

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

### 1. Conta interserver `s1` / `p1` — RESOLVIDO no Linux em 2026-08-15

O `ferramentas/configura_servidor.sh` gera credencial própria e grava nos dois
lados (banco com a senha hasheada, `conf/import/` com ela em claro). Duas coisas
que o caminho ensinou e que estão no `CLAUDE.md` §5: a senha tem **teto de 23
caracteres** (`char_logif.cpp:826` copia 24 bytes e trunca calado), e com MD5
ligado ela precisa ir **hasheada** para o banco.

**Continua valendo para o HML (Windows)**, que ainda usa `s1`/`p1`. O texto
abaixo é o registro do porquê.

### 1b. O registro original

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

### 3. Senhas de jogador — RESOLVIDO em 2026-08-14

Ligado o `use_MD5_passwords: yes` por `conf/guerra/login_guerra.txt`, e as
contas existentes convertidas. Ver `HISTORICO.md`, "A senha deixa de ser texto
puro", e `IMPLANTACAO.md` Etapa 1.

**O que continua em aberto:** MD5 é sem salt e fraco pelos padrões de hoje —
incomparavelmente melhor que texto puro, e é o que o emulador oferece.
Melhorar mexe em `src/` e é decisão para junto do backend em Go, que é quem
deveria tratar autenticação de verdade.

### 4. Pôr senha no `root` do MariaDB

**Situação:** o `root` do MariaDB local aceita conexão **sem senha**.

**Mitigação que já existe:** o rAthena *não* usa root. Criamos o usuário
`ragnarok`, com permissão apenas nos schemas `ragnarok` e `ragnarok_log` —
então um bug de SQL injection num script custom não alcança o resto do banco.

**Risco que sobra:** qualquer processo rodando na máquina abre o banco como root.

### 5. A conta de teste `teste`

Criada para o Marco Zero: senha trivial e `group_id 99`, que é **GM completo**.
Antes de abrir o servidor: apagar, ou trocar a senha e baixar o `group_id`.

### 6. O documento do cadastro NÃO é verificado — aberto em 2026-08-15

**Estado de hoje: o site aceita qualquer CPF válido em formato e qualquer
celular bem formado, sem provar que pertencem a quem se cadastrou.** O modo é
`SITE_VERIFICACAO=nenhuma` (`/etc/guerra/site.env`), escolhido de propósito para
o beta subir no mesmo dia.

**O que já funciona apesar disso:** o hash do documento é gravado desde o
primeiro cadastro, então cada documento só serve uma vez, e o limite vale
retroativamente quando a verificação for ligada. Há também teto de 10 tentativas
por hora por IP.

**O que não funciona:** nada impede a mesma pessoa de usar dez CPFs gerados. O
dígito verificador é conta pública e gerador de CPF válido se acha em qualquer
lugar — como barreira, ele segura engano de digitação e mais nada. Quem barra é
o celular, porque número custa dinheiro.

**Como fechar** — é uma linha de configuração, não um trabalho:

```
SITE_VERIFICACAO=penelope
SITE_PENELOPE_URL=<endpoint>
SITE_PENELOPE_TOKEN=<token>
```

O endpoint recebe `POST {"destino": "5511912345678", "mensagem": "..."}`. O
código de 6 dígitos, o prazo de 10 minutos e o teto de 5 tentativas já estão
escritos (`site/verificacao.go`). Falta só o endereço do serviço, que é o
Penelope Chatbot do dono — decidido em 2026-08-14 por ser custo marginal zero e
entregar melhor que SMS no Brasil (não há SMS gratuito confiável).

**Uma alternativa mais barata se o beta crescer antes disso:** um código de
convite compartilhado com os testadores fecha a porta para a internet inteira e
custa ~20 linhas. Não substitui a verificação — é gambiarra de janela.

### 7. O roadmap de segurança do beta — anotado, sem banda por enquanto

Levantado pelo dono em **2026-08-14**, ao desenhar o backup. **Nenhum destes
bloqueia o beta**; estão aqui para não serem redescobertos, e a ordem abaixo é
de dano esperado, não de dificuldade.

**Duplicação de item por sessão concorrente.** É o desastre nº 1 de servidor de
RO, e o mecanismo é sempre o mesmo: duas sessões do mesmo personagem vivas ao
mesmo tempo, com o char-server gravando o inventário de uma por cima da outra.
Costuma ser explorado por desconexão forçada no instante certo (troca,
armazém, carrinho). Vale ler o que o rAthena já oferece antes de escrever
qualquer coisa. **É este o item que justifica a retenção longa de `picklog`**:
quando acontece, o conserto certo é cirúrgico — desfazer o que a log mostra —,
e não restaurar o banco inteiro, que puniria quem não teve culpa.

**Força bruta na tela de login.** Hoje não há limite de tentativa por IP. Com o
MD5 ligado (Etapa 1 da implantação) o vazamento do banco ficou menos grave, mas
a porta 6900 continua aceitando tentativa ilimitada.

**Verificador e assinatura de pacote, contra bot.** O `PACKET_OBFUSCATION` está
ligado, mas com as **chaves padrão do rAthena, que são públicas** — ou seja, não
atrapalha ninguém que queira escrever bot (ver `IMPLANTACAO.md` §8). Trocar as
chaves exige que cliente e servidor combinem, isto é, mexer no exe: é trabalho
de verdade e entra junto com o instalador do patch.

**DDoS.** Sem resposta hoje, e é o único da lista que **não se resolve dentro da
máquina** — depende de quem está na frente dela (proxy, provedor). Entender as
alternativas mais para frente.

---

## 5b. O cliente não tem build reproduzível

> **O INSTALADOR FOI FEITO em 2026-08-16** — `ferramentas/monta_cliente.py`,
> `ferramentas/publica_cliente.sh` e o modo de instalação do `Jogar.exe`, com a
> base hospedada em `cdn.filiponegrao.com.br` (DigitalOcean Spaces). A receita
> está no `RECEITAS.md` §12 e o porquê no `HISTORICO.md`. O que **continua
> aberto** é o item 1 da lista do fim desta seção: o empacotador embala o
> cliente **desta máquina**, e não sabe reconstruí-lo do zero.
>
> Três coisas que a seção pedia e que foram atendidas: o pacote leva os dois
> XML apontados para produção, leva a `AI_sakray\`, e leva o `itemInfo.lua`
> (que não está dentro de `data\`). A varredura fechou em 19.866 de 19.904
> arquivos, com os 38 restantes classificados um a um.

O que segue é o levantamento original de 2026-08-12, mantido porque a medição
e o raciocínio continuam valendo para quem for mexer no pacote.

> **O PATCH, que era a outra metade disto, FOI FEITO em 2026-08-15.** O
> `Jogar.exe` (`patcher/`), o gerador (`ferramentas/monta_patch.py`) e o
> publicador (`ferramentas/publica_patch.sh`) estão de pé e testados ponta a
> ponta; o ciclo está em `RECEITAS.md` §11. O que segue aberto aqui é só o
> **primeiro download**: empacotar os 4,9 GB de um jeito reproduzível.
> Duas consequências para quem for empacotar:
>
> - o pacote leva o `Jogar.exe` e o `Jogar.ini` na raiz, e o atalho
>   do jogador aponta para o Atualizador — não para o `GuerraDoEmperium.exe`;
> - **o pacote não precisa mais ser refeito a cada mudança.** Ele pode ficar
>   parado numa versão conhecida: quem baixar hoje recebe todos os patches
>   publicados desde então, na primeira abertura. Isso muda a economia do
>   problema — o que era "reempacotar 4,9 GB toda semana" virou "reempacotar
>   quando o acúmulo de patches ficar grande demais".

### As ferramentas NÃO entram no instalador

Foi a pergunta que abriu o assunto ("o instalador teria que incluir esses
passos?"), e a resposta é **não**: `completa_iteminfo.py`, `instala_visual.py`,
`estende_accessoryid.py` e as irmãs são **build**, não instalação. Três motivos,
e o primeiro sozinho decide:

1. **A fonte delas é a instalação do bRO desta máquina** — `C:\Program Files
   (x86)\Gravity Interactive, Inc\Ragnarok Brazil\`. O jogador não tem, e não
   vai ter.
2. Precisam de Python 2.7.
3. São determinísticas e idempotentes: rodar aqui uma vez e empacotar a saída é
   **exatamente equivalente** a rodar na máquina dele.

**Elas produzem arquivos; o instalador entrega os arquivos.**

### As três peças, e a que se esquece

Medido em 2026-08-12: o `C:\GuerraDoEmperium\cliente\` tem **4,9 GB em 20.044
arquivos**.

| peça | tamanho | o que é |
|---|---|---|
| `data.grf` + exe + `BGM\` na raiz | ~3,1 GB | o kRO 2021-11-03 e o exe patchado |
| **`cliente\data\`** | **720 MB, 19.077 arquivos** | **o override — tudo que é nosso** |
| `SystemEN\LuaFiles514\itemInfo.lua` | 22,7 MB | nome, descrição e ícone de item |

**A armadilha é que esquecer as duas últimas não quebra nada visível.** O
`DataFolderFirst` faz o disco vencer o GRF; sem a pasta `data\` o cliente
**abre, loga e joga** — só que chapéu não desenha, o texto volta ao coreano de
2021 e item aparece sem nome. Zero erro, zero log. É a mesma falha calada que o
`CLAUDE.md` §5 e o `ARQUITETURA.md` §4 documentam item por item.

E o `itemInfo.lua` **não está dentro de `data\`** — é outra pasta. Quem
empacotar "o GRF mais a pasta data" perde ele, e **todo item fica sem nome na
loja**.

O `cliente\data\` não é de uma rodada só: foi acumulado dia a dia desde
2026-07-30, com picos em 09-08 (6.154 arquivos), 08-08 (2.929) e 05-08 (2.544).
Não há como reconstituí-lo "de memória".

### 711 MB do pacote são lixo

**65 arquivos de backup**, deixados pelas próprias ferramentas — e **28 deles
são cópias do `itemInfo.lua`** em `SystemEN\LuaFiles514\`, 627 MB só nisso.
Somam-se backups do exe na raiz (58 MB) e do `System\` (21 MB).

Primeiro filtro do instalador, antes de qualquer compressão: excluir `*BACKUP*`,
`*.ORIGINAL*`, `*.original` e `*.INGLES`. Corta 14% do pacote.

### O problema de verdade que o instalador revela

**Hoje não existe build reproduzível do cliente.** O repositório tem as
ferramentas, e a documentação repete "cliente novo perde isso, calado" em pelo
menos oito lugares (`ARQUITETURA.md` §382, `CATALOGO-VISUAIS.md` ×3,
`CLAUDE.md` §5, `HISTORICO.md` ×3, `RECEITAS.md`, e a §1 deste arquivo) — mas
**não existe uma lista única** dizendo o que rodar, em que ordem, para sair de
um kRO limpo e chegar no nosso cliente.

O **exe é o caso extremo**: `GuerraDoEmperium.exe` é o Ragexe desempacotado do
NEMO, patchado. Sem NEMO e sem a lista de patches aplicados, ele é
irreproduzível — e é o único arquivo do conjunto do qual não há gerador
versionado.

**Se o instalador for feito só empacotando a pasta, ele vira a única cópia do
cliente**, e as ferramentas apodrecem sem ninguém notar — até o dia em que uma
delas precisar rodar de novo.

### Por onde começar, quando for a hora

1. Escrever a lista do que o cliente é feito — de preferência como
   `ferramentas/monta_cliente.py`, que rode a sequência inteira do zero, e uma
   seção nova no `RECEITAS.md` consolidando as oito menções espalhadas. **O
   instalador passa a ser a SAÍDA desse script**, não um pacote que ninguém
   sabe refazer.
2. ~~Resolver o exe: ou registrar a lista de patches do NEMO, ou aceitar por
   escrito que ele é binário de origem única e fazer cópia fria dele.~~
   **FEITO em 2026-08-14:** o `GuerraDoEmperium.epi`, ao lado do exe, é o perfil
   do NEMO e traz os nomes dos patches em texto legível. A lista está no
   `REFERENCIA.md`. Continua valendo a cópia fria do binário — a lista diz
   **quais** patches, não com que parâmetros cada um foi aplicado.
3. Só então empacotar. **E o pacote leva o `data\sclientinfo.xml` e o
   `data\clientinfo.xml` já apontados para a produção** — os dois, pelo motivo
   do `CLAUDE.md` §5.
4. **O pacote leva também a pasta `AI_sakray\`**, criada em 2026-08-15 como
   cópia de `AI\` (com o `USER_AI` dentro). Sem ela, criar homúnculo ou
   mercenário devolve caixa de erro de Lua — ver `CLAUDE.md` §5. É pasta fora
   do git, como o resto do cliente: quem empacotar tem de lembrar dela.

**Já existe um `PatchClient\`** na raiz do cliente (30 `.bmp`, 2,5 MB) — é o
skin do patcher do próprio kRO. ~~Se a ideia for patch incremental depois do
primeiro install, o esqueleto está lá.~~ **O patch incremental foi feito em
2026-08-15 sem usar esse skin** — o Atualizador desenha a própria janela, com a
arte do site. Os `.bmp` continuam lá se um dia entrar o painel de notícias.

---

## 5c. Os QUATRO servidores na produção — e os apontamentos que sobraram (2026-08-14)

**São quatro servidores, não três** (`CLAUDE.md` §3), e a produção só está
inteira quando os quatro estão no ar **e alcançáveis de fora**. Hoje três estão;
o quarto não. E o cliente aponta para o servidor a partir de **mais de um
arquivo** — o login foi só o primeiro.

### O placar, medido de fora em 2026-08-14

| peça | porta | quem aponta | estado |
|---|---|---|---|
| login | 6900 | **cliente**: `data\sclientinfo.xml` (e o `clientinfo.xml` junto) | ✅ apontado e conectando |
| char | 6121 | **servidor** anuncia (`char_ip`) | ✅ provado na captura — nada a fazer no cliente |
| map | 5121 | **servidor** anuncia (`map_ip`) | ✅ provado na captura |
| **web** | **8888** | **cliente**: `ExternalSettings_*.lub` | ❌ **porta fechada na produção, e o `.lub` ainda diz `127.0.0.1`** |

As três primeiras foram confirmadas pela captura de conexões do primeiro login
(`HISTORICO.md`, Etapa 2). A quarta apareceu na mesma captura, do lado errado:

```
127.0.0.1:8888  SynSent
```

E `connect` para `138.197.155.31:8888`, de fora, **estoura o tempo** — a porta
não está exposta. Não dá para saber daqui se o processo está de pé no Linux
(esta máquina não tem chave SSH do servidor); o que está medido é que **de fora
não se alcança**.

### De onde o cliente tira esse endereço

Chama-se `AssistAddr`, e **não vem de nenhum dos dois XML** — apontar o
`sclientinfo.xml` para a produção não o arrasta junto. Dele saem
`/emblem/upload`, `/emblem/download`, `/userconfig/*` e `/twitter/*`.

**São QUATRO arquivos, não um** — varridos em 2026-08-14, todos texto puro (não
bytecode), todos com `AssistAddr = "127.0.0.1:8888"` na linha 27:

```
data\luafiles514\lua files\service_brazil\ExternalSettings_br.lub
data\luafiles514\lua files\service_brazil\ExternalSettings_br_s.lub
data\luafiles514\lua files\service_korea\ExternalSettings_kr.lub
data\luafiles514\lua files\service_korea\ExternalSettings_kr_sak.lub
```

Duas divisões, e **nenhuma das duas está resolvida**: `_s`/`_sak` é a gêmea
sakray — e é justamente a gêmea sakray que venceu no caso do `sclientinfo.xml`
(`CLAUDE.md` §5) —; e `service_brazil` / `service_korea` é escolhido pelo
`<servicetype>`, que tem **pergunta aberta neste projeto**: o XML diz `brazil` e
o jogo se comporta como `korea` (§4 desta lista, na seção das bandeiras de
`CTRL+<n>`). Como hoje os quatro dizem a mesma coisa, a captura não desempata.
**Trocar os quatro** é mais barato que descobrir qual vale.

**Consequência:** contra a produção, o emblema de clã e a configuração de
usuário salva no servidor **não funcionam** — e a falha é a mais calada que
existe (`HISTORICO.md`, "O quarto servidor"): o `POST` morre, o cliente não
mostra caixa de erro e o map-server não registra nada. Ninguém vai relatar
isso como erro; vão dizer "escolhi o emblema e não aconteceu nada".

**Por que não foi trocado junto:** a porta **8888 está fechada na produção** —
medido no mesmo dia, `connect` estoura o tempo de fora. Apontar o cliente para
um endereço que não responde só troca uma falha calada por outra mais lenta.

### ✅ PASSOS 1 E 2 FEITOS NO MAC (2026-08-15) — o endereço é este

**`AssistAddr = "libraro.filiponegrao.com.br:80"`**

Se o cliente não resolver o nome, a forma equivalente por IP é
`138.197.155.31:80`. **Não use `:8888`** — aquela porta continua fechada, e de
propósito.

**O web-server sempre esteve no ar.** O `guerra-web.service` sobe junto dos
outros três desde 2026-08-15 e escuta em `0.0.0.0:8888`. O que a medição do
Windows pegou — `connect` estourando o tempo na 8888 — está certo, e é
deliberado: aquela porta é um HTTP embutido que recebe **upload de arquivo de
usuário anônimo**, e expô-la crua era o que a Etapa 8 queria evitar. Quem fala
com ela é o Apache.

**Por que a porta 80 e não a 443.** O `AssistAddr` é `host:porta`, sem esquema —
o cliente monta `http://`. O certbot tinha posto redirecionamento HTTP→HTTPS
para tudo, e um `POST` que morre num 301 seria trocar uma falha calada por
outra. Agora o vhost de porta 80 **atende em HTTP os seis caminhos do
web-server** (`/emblem/`, `/charconfig/`, `/userconfig/`, `/party/`,
`/twitter/`, `/MerchantStore/`) e **redireciona todo o resto** para HTTPS.

*Se* o cliente aceitar HTTPS no `AssistAddr`, `:443` é melhor e já funciona —
vale testar, porque nesses seis caminhos o token de autenticação viaja em claro
hoje. Mas não vale travar o beta por isso.

**A prova, e ela é do lado de dentro.** Requisições feitas da internet
apareceram uma a uma no log do próprio web-server:

```
web-server: [Info]: 127.0.0.1 [POST /emblem/upload]      400
web-server: [Info]: 127.0.0.1 [POST /userconfig/load]    400
web-server: [Info]: 127.0.0.1 [POST /MerchantStore/load] 400
```

O `400` é o rAthena recusando corpo malformado (os endpoints querem
`multipart/form-data`) — ou seja, **está processando**. O que faltava provar era
o caminho, e ele está provado.

**Falta só o passo 3 e o 4**, no Windows: trocar o `AssistAddr` nos quatro
`.lub` e conferir em jogo subindo um emblema.

---

**A ordem original, para registro:**

1. **Sessão do Mac.** Garantir que o `web-server` está no ar (é um dos quatro do
   `SERVER_DEPENDS`, e o `systemd` tem de subi-lo junto com os outros três) e
   decidir como ele é **exposto**: abrir a 8888, ou — melhor — pô-lo atrás do
   Apache que já está de pé, sob HTTPS no mesmo domínio. Estar rodando não
   basta: o cliente fala com ele **de fora**.
2. Dizer para cá **qual endereço** ficou valendo (IP com porta, ou o domínio),
   porque o `AssistAddr` é uma string `host:porta` e a forma muda conforme a
   escolha do passo 1.
3. **Sessão do Windows.** Trocar o `AssistAddr` **nos quatro `.lub`**, com o
   cuidado de sempre (cp1252, por script, âncora com `assert`) — e lembrar que
   isso é **cliente, fora do git**: some em cliente novo, e o instalador tem de
   levar os quatro já apontados, junto com os dois XML (§5b).
4. Conferir em jogo criando um clã e subindo um emblema — é o único teste que
   fecha, porque o caminho inteiro é silencioso.

### Dois apontamentos menores, achados na mesma varredura

Não quebram jogo, mas apontam para a máquina errada e são de graça quando
alguém estiver ali:

| arquivo | o que diz | efeito |
|---|---|---|
| `System\itemInfo_true.lub` e `SystemEN\itemInfo.lua`, linha 86 | `URL = "http://127.0.0.1/?module=item&action=view&id="` | é o link "ver este item na web" do menu do item — abre página morta |
| `data\msgstringtable.txt`, linha 456 | a string `127.0.0.1` crua | texto padrão de UI; conferir onde aparece antes de mexer |

O `itemInfo.lua` é **gerado** por ferramenta (§ do `ferramentas/LEIAME.md`), então
a troca tem de entrar no gerador, não no arquivo — senão volta na próxima rodada.

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

