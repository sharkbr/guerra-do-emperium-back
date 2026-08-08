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

**Enquanto não for varrido, todo destino de Instância é suspeito.**

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

## 4. METADE RESOLVIDA — o manto cosmético (`Costume_Garment`)

Aberto em 2026-08-05, ao varrer o acervo cosmético para o Mercado de Visuais.
**Metade fechou em 2026-08-08**, com o Manteleiro e o `instala_manto.py`; a
outra metade continua aqui.

Manto tem **duas camadas a mais** que chapéu, e cada uma tinha a sua lacuna:

| camada | chapéu | manto | estado |
|---|---|---|---|
| nome e descrição | `itemInfo.lua` | igual | — |
| slot de visual | `accessoryid.lub` + `accname.lub` | `spriterobeid.lub` + `spriterobename.lub` | **em aberto** |
| ferramenta que estende o slot | `estende_accessoryid.py` | **não existe** | **em aberto** |
| arquivos de arte | 4 de item + 4 de cabeça | 4 de item + sprite de manto **por classe** | resolvido |
| ferramenta que instala a arte | `instala_visual.py` | `instala_manto.py` | resolvido |

### O que fechou

A arte. O `ferramentas/instala_manto.py` copia a subárvore de sprite de manto
da GRF do bRO para `cliente\data\`, item a item, só o que falta — 2925 arquivos
para os treze do Manteleiro. Tem `--verificar` implícito (sem `--aplicar` só
relata) e é idempotente. Ver `ferramentas/LEIAME.md`.

### O que continua em aberto

Estender a `spriterobeid.lub`. A nossa tem **120 entradas**; manto cujo `View`
esteja fora dela **não desenha, e arte nenhuma resolve**. Os treze do
Manteleiro não esbarraram nisso por sorte de catálogo — os `View` deles vão de
61 a 114, todos dentro das 120 —, mas o acervo maior esbarra.

O `instala_manto.py` **recusa** esse caso em vez de copiar 600 arquivos que o
cliente nunca vai procurar, e diz por quê. O `varre_cosmeticos.py` continua se
recusando a chamar manto de `curavel` pela mesma razão: chamar de "sem cura" o
que só precisava de outra ferramenta foi o erro de 2026-08-01, e prometer cura
que não há como cumprir é o erro simétrico.

**O que falta escrever:** um `estende_robeid.py` espelhado no
`estende_accessoryid.py` (mesma base-relida-do-GRF, mesmo round-trip, mesmas
duas travas). Feito isso, o `varre_cosmeticos.py` pode passar a classificar
manto como `curavel`, e os 45 que estavam parados em 2026-08-05 voltam à mesa.

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

## 4b. A Caveira Humana existe e nada a entrega

Aberto em 2026-08-08. O item **30995 Caveira Humana** foi criado dos dois lados
— `db/guerra/item_db.yml` e a entrada do `itemInfo.lua` pelo
`ferramentas/instala_item.py` — e está travado como pedido: peso 0, sem chão,
troca, armazém, RoDEX, leilão, carrinho ou revenda.

**Só que nenhum script a solta.** A descrição que o jogador lê promete que "só
cai de jogadores no level máximo com reputação positiva dentro da Arena de
Prontera", e em 2026-08-08 a única fonte é `@item`. Quem conta a morte na arena
é o `npc/guerra/honra_de_combate.txt`, no `OnPCKillEvent`, e ele hoje pontua e
não dá item nenhum.

**Onde entra, quando for escrito:** o mesmo `OnPCKillEvent`, depois das travas
que já existem — as duas condições da descrição são exatamente as que ele já
testa (`.Nivel` dos dois lados e `.Piso` do morto). Decidir se a caveira sai
**sempre** ou só quando a morte pontua; hoje o anúncio sai sempre e o ponto não.

**E ela já é citada de fora:** a descrição da Moeda Nova (30998) lista "em troca
de Caveira Humana" como uma das fontes de moeda. Esse NPC de troca também não
existe.

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

