# Armadilhas: db/, conf/ e C++ do rAthena

Bancos em YAML, recarregadores, item_db, guardas do C++, operação dos quatro servidores.

**Este arquivo é um dos seis cadernos de armadilhas do projeto.** O índice de
todos eles — uma linha de gatilho por armadilha, com o caderno onde o caso
está contado por inteiro — está na §5 do `CLAUDE.md`. **Leia aqui a entrada
que o gatilho apontar**; ler o caderno inteiro não é para ser preciso.

As entradas abaixo produziram diagnóstico falso e custaram retrabalho. Cada
uma traz o sintoma, a causa medida (com arquivo e linha, quando existe) e a
saída — e a medição é o que separa esta lista de um palpite. **Armadilha
nova se escreve nas duas pontas:** o caso aqui, o gatilho na §5.

---

- **Em `db/refine.yml`, `Level:` é 1-based e NÃO é o refino do item.** O leitor
  faz `refine_level -= 1` — comentário *"Database is 1 based, code is 0 based"*
  em `status.cpp:189` — e compara com o refino **atual**. `Level: 7` é a
  tentativa de sair do +6 para o +7. Ler o número como refino atual erra por um
  na tabela inteira, e o erro não se denuncia: a tabela continua fazendo
  sentido, só está deslocada. Foi por isso que a Bênção do Ferreiro pareceu
  "desativada" em 2026-08-07.

- **`invalidWarning` no leitor de YAML diz "skipping" e descarta o registro
  inteiro.** No `RefineDatabase::parseBodyNode` (`status.cpp:183`), um nível de
  refino acima do `MAX_REFINE` emite *"Refine level %hu is invalid, skipping"*
  e cai num `return 0` que joga fora o **grupo todo**, não a linha. Baixar o
  `MAX_REFINE` sem cortar os níveis do `.yml` desliga o refino de Armor e
  Weapon inteiros, com um aviso no log que parece inofensivo. O mesmo padrão
  aparece nos outros `parseBodyNode`.

- **Em `conf/groups.yml`, `false` não desliga nada.** Herança de grupo é um OU
  binário aplicado **depois** do parse (`pc_groups.cpp:275`,
  `permissions |= otherGroup->permissions`). Permissão que o pai concede, o
  filho não consegue tirar — `attendance: false` no `Super Player` é letra
  morta, porque ele herda do `Player`, que a concede. Ler a linha e concluir
  "esse grupo não tem" dá diagnóstico invertido.

- **Equipamento ilusional não está no `Drops:` do monstro: é DROP DE MAPA — e
  drop de mapa NÃO passa pela taxa do servidor.** São dois enganos em fila, e o
  segundo é o caro. O primeiro: procurar a Espada Ilusional (13469) no
  `mob_db` do Congelador Ominoso devolve **zero**, o que parece item que não
  cai de nada; ela mora em `db/re/map_drops.yml`, um banco separado, indexado
  por **mapa** e processado no fim do `mob_dead` (`mob.cpp:3372`, "Process map
  specific drops") — e para monstro dentro de instância a busca é pelo
  `instance_src_map`, o mapa-molde. O segundo: o `mob_getdroprate` chamado ali
  (`mob.cpp:3388`) só aplica bônus de LUK e de equipamento do jogador. Os
  `item_rate_*: 5000` de `conf/guerra/battle_guerra.txt` **não alcançam campo
  nenhum daquele arquivo**, e o cabeçalho do próprio `map_drops.yml` diz isso
  numa linha em inglês: *"These drops are unaffected by server drop rate"*.
  Consequência medida em 2026-08-18: num servidor de 50x, o ramo ilusional
  inteiro rodava a **1x** — a espada a 0,025% por Congelador Ominoso (549.071
  de HP) e a Pedra da Ilusão a 0,010%, com a troca oficial pedindo **cem**
  pedras. Nada estava quebrado, então nada aparecia no log; o sintoma é
  indistinguível de azar. Corrigido por `db/guerra/map_drops.yml`, gerado por
  `ferramentas/escala_drops_de_mapa.py`.
  **E o teto de `Rate` não é cortado, é recusado:** acima de 100000 o
  `parseDrop` devolve `false` e o `parseBodyNode` descarta o **mapa inteiro**
  (`mob.cpp:7072`) — com os drops já lidos daquele mapa aplicados, ou seja um
  override pela metade. Quem multiplicar taxa daquele arquivo põe o `min()` no
  gerador.

- **Em `TimeLimit` de quest, o `+` é o que decide o significado.** `+3h` é
  intervalo (três horas a partir de agora); `6h`, sem o sinal, é **hora
  exata** — o `quest_time()` (`quest.cpp:554`) devolve o próximo 06:00, hoje
  ou amanhã. Os dois caminhos saem do mesmo campo (`quest.cpp:71`), e trocar
  um pelo outro dá um prazo plausível e errado. Reset diário não precisa de
  temporizador: é a forma sem `+`.

- **`MAX_QUEST_OBJECTIVES` é 3** (`src/common/mmo.hpp:111`). Um quarto alvo
  numa quest emite *"Targets list exceeds the maximum"* e cai no mesmo
  `return 0` de sempre, que descarta a **quest inteira** — não o alvo a mais.
  O mesmo vale para `Mob:` com AegisName inexistente (`quest.cpp:132`).

- **A descrição do item na tela discorda do script do servidor — no NÚMERO, não
  só na presença.** A descrição vem do `itemInfo` do cliente, que é a tradução
  do kRO de 2021; o efeito vem do `Script:` do `item_db` do nosso rAthena, que é
  outra revisão. Caso vivo em 2026-08-09: a **Capa do Comandante** (20925) diz
  na tela *"Resistência as raças Humano e Doram +5%"* e o script dá
  `bonus2 bSubRace,RC_Player_Human,3` — 3, e nada para Doram. Somar resistência
  lendo a tela dá um total plausível e errado, e a diferença não aparece em
  lugar nenhum. **Conta de efeito se fecha no `item_db`.**
  *Esta capa foi consertada em 2026-08-10* (override no `db/guerra/item_db.yml`,
  do lado do servidor) — quem for conferir hoje acha 5, e a armadilha continua
  valendo para todo o resto do `item_db`.
  **O caso mais caro dessa família já tem trava própria: o "Indestrutível".**
  Ali a diferença não é de número — a peça quebra e some. Ver §4.19 e
  `ferramentas/marca_indestrutiveis.py`.

- **Desligar um arquivo de castelo do rAthena leva 17 BANDEIRAS junto, e nada
  no log diz isso.** Cada `npc/guild/<castelo>.txt` define, além do Emperium e
  do Gerente, **quatro bandeiras no feudo, doze dentro do castelo e uma na
  cidade** — nos dezenove que desligamos em 2026-08-13 eram **279 bandeiras em
  27 mapas**, incluindo Prontera, Geffen, Payon e Al De Baran. Bandeira que
  some não emite aviso; quem percebeu foi o dono, na tela. **Ao comentar
  qualquer `npc:` de castelo, contar o que mais estava naquele arquivo.** A
  boa notícia é que bandeira **não é atrelada ao castelo**: o que a prende é
  uma linha, o `FlagEmblem GetCastleData("<mapa>", CD_GUILD_ID)`, e trocar o
  mapa ali faz a bandeira hastear outro clã (ver
  `npc/guerra/bandeiras_do_feudo.txt`).

- **`DropEffect: CLIENT` no `item_db` NÃO é "sem efeito" nem "o padrão" — é
  uma escolha que este cliente resolve desenhando NADA, e ela já está em 1882
  itens do vendor.** O campo tem sete valores, e o 1 (`CLIENT`) quer dizer
  literalmente *"decide voce, cliente"*; os outros nomeiam um pilar de cor.
  O `db/re/` do nosso rAthena declara `DropEffect: CLIENT` em 1882 itens —
  **quase toda carta entre eles** —, e o cliente de 2021-11-03 decide não
  desenhar. Consequência que engana sozinha: código que trate "campo diferente
  de `NONE`" como "o item já escolheu" desliga a própria regra em silêncio,
  para exatamente os itens que mais importam. A guarda certa é
  `> DROPEFFECT_CLIENT`, nunca `!= DROPEFFECT_NONE`. Custou três hipóteses
  erradas em 2026-08-17 (`src/custom/brilho_da_carta.hpp`).

- **`ShowInfo` NÃO chega ao `log/map-msg_log.log`.** O `console_msg_log` deste
  servidor é **3** (`conf/import/map_conf.txt`), e a escala é 1 = Warning,
  2 = Error/SQL, 4 = Debug — **informação não tem bit**, em nenhum valor. Ou
  seja: sonda escrita com `ShowInfo` imprime só na **janela** do map-server, e
  quem for ler o arquivo conclui que a sonda não rodou — diagnóstico invertido
  sobre código que está funcionando. Sonda que precise ir para o arquivo usa
  `ShowWarning`.
  **E dá para ler a janela sem pedir print:** `AttachConsole(<pid do
  map-server>)` mais `ReadConsoleOutputCharacterW` sobre o `CONOUT$` devolve o
  buffer de tela inteiro. Foi o que fechou o caso do brilho de carta em
  2026-08-17, depois de o arquivo de log ter vindo vazio duas vezes.

- **Trocar `Locations` de um item com o servidor NO AR deixa o item
  INEQUIPÁVEL até o jogador relogar — e a mensagem culpa o item.** O cliente
  guarda o `location` de cada item do inventário de quando a lista lhe foi
  enviada (`clif_inventorylist` manda `pc_equippoint`, `clif.cpp:3092`), e ao
  equipar ele **manda essa posição de volta** (`clif_parse_EquipItem` repassa o
  `p->position` cru). O `pc_equipitem` então testa `!(pos & req_pos)`
  (`pc.cpp:12064`): com o servidor já dizendo `Acc. Direito` e o cliente ainda
  pedindo `Acc. Esquerdo`, a conta dá zero e sai *"You can't put this item
  on."*, uma por clique. **O `@reloaditemdb` não desfaz isso**: o
  `itemdb_reload` chama `pc_setinventorydata`, não `clif_inventorylist`
  (`itemdb.cpp:4992`). Quem reenvia a lista é o `clif_parse_LoadEndAck`
  (`clif.cpp:10795`) — ou seja **login ou troca de mapa**, e só isso.
  Duas consequências: em DEV, depois de mexer em `Locations`, **relogar antes
  de testar** — senão a própria conferência acusa um defeito que não existe;
  e em PRODUÇÃO o problema não aparece, porque o deploy reinicia o map-server e
  todo mundo reconecta. Isto vale para o item na MOCHILA; o que já está
  equipado tem o mesmo gatilho, e ali o `pc_checkitem` desequipa sozinho
  (`pc.cpp:12623`).

- **As duas caixas de acessório da janela de equipamentos NÃO estão
  invertidas — a etiqueta só parece trocada porque o personagem está de
  frente.** `Acc. Right` fica à **nossa esquerda** e `Acc. Left` à nossa
  direita, que é o correto: a direita do personagem é a nossa esquerda. Então
  "acessório direito caindo na caixa escrita Left" **não** é defeito de
  cliente, de etiqueta nem de pacote — é o `Locations:` do nosso vendor
  discordando da descrição que o jogador lê, que vem do `itemInfo.lua`, ou
  seja do bRO (a mesma família da §4.14). A leitura errada é cara: leva a
  inverter `EQP_ACC_R`/`EQP_ACC_L` no `mmo.hpp`, o que mudaria **todo** item
  do servidor para consertar três. **A medição que decide é a população**, e
  ela é barata: cruzar todo acessório de lado único do `item_db` com a linha
  `Tipo: Aces. Direito/Esquerdo` da descrição do bRO. Em 2026-08-17 deu 76
  acordos contra 3 divergências — inversão geral daria 79 a 0.

- **`@reloadscript` sem `@reloaditemdb` FAZ O ITEM NOVO SUMIR DA VITRINE.** O
  `npc_parse_shop` descarta todo item que não está no `item_db` em memória
  (`npc.cpp:4142`, *"Invalid sell item ... (id 'N')"*) — então recarregar o
  script de uma loja que ganhou item novo **antes** de recarregar o `item_db`
  publica a vitrine sem ele. A linha de aviso existe, e some sob centenas de
  `[Warning]` inofensivos dos mercados. **Item novo em loja: `@reloaditemdb`
  primeiro, `@reloadscript` depois.** Num boot completo o problema não existe
  (o `item_db` carrega antes dos NPCs), o que o torna exclusivo do
  recarregamento parcial — e faz o mesmo servidor se comportar de dois jeitos.
  Medido em 2026-08-17 com dois placeholders novos.

- **`LOOK_BODY2` não é mais uma bandeira 0/1: guarda o Id do TRABALHO do visual
  alternativo — e o `db/re/stylist.yml` do vendor não foi atualizado.** O
  arquivo ainda traz `Look: Body2` com `Value: 0` e `Value: 1`, do tempo em que
  estilo de corpo era liga/desliga; hoje o valor certo é `Rune_Knight_2nd` e
  irmãos, a faixa **4332..4349** (`JOB_SECOND_JOB_START = 4331`,
  `src/common/mmo.hpp`), listados por trabalho em `db/re/job_outfits.yml`. O
  próprio rAthena sabe do desencontro e não conserta: a validação de faixa do
  Body2 no `StylistDatabase::parseBodyNode` (`src/map/npc.cpp`) está dentro de um
  `#if 0` com o comentário *"TODO: Unsupported for now => This is job specific
  now"*.
  **A falha é calada e cobra:** o `clif_parse_stylist_buy_sub`
  (`src/map/clif.cpp`) chama `pc_delitem` **antes** do `switch` que muda o
  visual, então o Cupom de Roupa some; o `pc_changelook` aceita 0 e 1 porque
  `job_db.exists()` os conhece (Aprendiz e Espadachim); e o pacote de aparência
  reduz tudo a `p.body = (look > 4331 && < 4350) ? 1 : 0`, ou seja **0**. O
  servidor responde sucesso, o cliente não erra, e o único rastro é um cupom a
  menos. Consertado em 2026-08-17 por `src/custom/estilo_de_corpo.hpp` (§2).
  Duas consequências que valem para o resto: **valor de `db/` do vendor pode
  estar semanticamente vencido sem dar aviso** — o `#if 0` é o sinal a procurar
  —, e **override de `stylist.yml` não resolveria**, porque a tabela tem um valor
  por índice e o certo depende do trabalho de quem clicou (o `parseBodyNode`
  mescla por `Look`+`Index` e não sabe remover entrada nem zerar custo já
  existente).

- **A janela de encaixe de carta não abre quando o único equipamento compatível
  está EQUIPADO — e o servidor não manda pacote nenhum.** O `clif_use_card`
  (`src/map/clif.cpp`) monta a lista pulando o que já está no corpo
  (`if( sd->inventory.u.items_inventory[i].equip > 0 ) continue;`), o não
  identificado, o `itemdb_isspecial` e o que não tem cova livre; se sobrar zero
  ele faz `if( !c ) return;`. Não há erro, não há log, não há janela — o duplo
  clique na carta simplesmente não faz nada, o que parece carta quebrada.
  Some-se a isso que o `Locations:` de uma carta pode não ser o que o jogador
  lembra de outro servidor: a **Carta Senhor das Trevas (4168) é de CALÇADO**
  aqui, e o nosso `item_db` e a descrição do bRO concordam nisso (medido em
  2026-08-17).

- **Arquivo de `db/` do vendor pode estar ÓRFÃO — formato certo, conteúdo
  certo, e ninguém o lê.** É um degrau além do "valor semanticamente vencido"
  do `stylist.yml`: lá o dado era lido e estava velho; aqui o dado está certo e
  **não é carregado por código nenhum**. O `db/re/job_outfits.yml` viveu assim
  no nosso vendor: cabeçalho `JOB_STATS` válido, os treze `AlternateOutfits` do
  estilo de corpo dentro, e o `JobDatabase::getDefaultLocation()`
  (`src/map/pc.cpp:13819`) apontando **só** para `db/re/job_stats.yml`, que não
  tinha rodapé. Resultado: `job->alternate_outfits` vazio para **todo**
  trabalho. Falha calada e enganosa — o recado que sai é *"This job has no
  alternate body styles"*, que soa como "esta classe não tem", e não como "o
  arquivo inteiro não foi lido". **A sonda é `getDefaultLocation()` mais um
  `grep` pelo nome do arquivo em `src/` e `conf/`: arquivo de `db/` que não
  apareça em nenhum dos dois e não tenha rodapé apontando para ele não está
  sendo carregado.** O conserto é o mesmo `Footer: Imports:` do `quest_db.yml`.

- **Guarda de validação do rAthena pode reprovar 100% dos valores válidos, e o
  chamador ainda relatar sucesso.** No `pc_changelook`, `case LOOK_BODY2:`, o
  `if( !job_db.exists( val ) ) return;` foi escrito quando aquele campo valia 0
  ou 1 (Aprendiz e Espadachim, dois trabalhos que o `job_db` conhece). Hoje o
  campo guarda o Id do visual alternativo — 4332..4344 —, e **nenhum arquivo do
  vendor declara esses ids num `Jobs:`**: o `job_outfits.yml` só os cita em
  `AlternateOutfits`, que preenche o vetor do trabalho *pai* e não cria entrada.
  Como `job_db.exists()` é `find(key) != nullptr` (`src/common/database.hpp:103`),
  a guarda reprova sempre, o `clif_changelook` do fim da função nunca roda e
  nenhum pacote sai. E como `pc_changelook` é **`void`**, o `@bodystyle` imprime
  *"Aparência alterada"* logo depois, incondicionalmente. **Função `void` que
  desiste no meio é indistinguível de função que trabalhou** — ao depurar um
  "mudou e não mudou", ler o corpo da função e não a mensagem de quem a chamou.
  Consertado por dado (`db/guerra/job_estilo_de_corpo.yml`, §2), nunca por
  substituir a linha.

- **Padrão idêntico numa coluna do banco é evidência, e não se parece com
  erro.** O que denunciou a guarda acima foi uma consulta ao `char` em que
  **todo** personagem tinha `body` igual a `class` — 4060/4060, 1/1, 14/14. Não
  havia valor "errado" à vista: era o único ramo do nosso código que sobrevivia
  à guarda (`val == 0` → `sd->status.class_`), e o outro morria antes de gravar.
  **Coluna inteira com o mesmo relacionamento entre dois campos é sintoma**, do
  mesmo jeito que tabela de tamanho 1 é sintoma de chave não resolvida. Vale a
  pena olhar o banco cedo: ele mostra o que ficou gravado, que é diferente do
  que a tela mostra e do que o log conta.

- **Varredura por `nome_db.` NÃO acha quem itera o banco de dentro da própria
  classe.** Um `grep "job_db\."` filtrando `find|exists|load|clear` devolveu
  "ninguém enumera" — e o `JobDatabase::loadingFinished()` (`src/map/pc.cpp:14277`)
  itera `*this` e avisa sobre trabalho sem tabela de EXP. Método da classe usa
  `*this`, `this->`, ou nada; o nome da variável global não aparece. **Antes de
  concluir que acrescentar entrada num banco é inócuo, ler o `loadingFinished()`
  dele.** No caso do estilo de corpo o risco era real e não se concretizou: o
  laço faz `continue` quando `!pcdb_checkid(job_id)`, e nenhuma faixa do
  `pcdb_checkid` (`src/map/pc.hpp:1219`) cobre 4331+ — a última é
  `JOB_SKY_EMPEROR2 = 4316`.

- **O corpo de uma habilidade NÃO está mais no `skill.cpp` — cada uma tem
  classe própria em `src/map/skills/`.** Um `grep` por `case AL_HEAL` no
  `skill.cpp` devolve duas ocorrências e **nenhuma das duas é a cura**: uma é o
  desvio para dano em morto-vivo, a outra é a validação de alvo. Quem parar aí
  conclui que a habilidade não é tratada — e ela é, em
  `src/map/skills/acolyte/heal.cpp`, achada pelo `default:` do
  `skill_castend_nodamage_id` (`skill.cpp:4587`), que faz
  `skill->impl->castendNoDamageId(...)` e só imprime *"missing code case"* se
  não houver classe. Medido em 2026-08-26, ao apurar se dava para curar
  monstro. **Ao investigar o que uma habilidade faz, procurar primeiro em
  `src/map/skills/<classe>/<nome>.cpp`**; o switch grande hoje só guarda as
  que sobraram.

- **Parar SÓ o map-server para recompilar deixa o jogador travado no login, e a
  mensagem culpa o cliente.** O char-server mantém o personagem em memória e a
  coluna `online` em 1 (a entrada do `UPDATE` na tabela `char`, acima, é a
  mesma armadilha por outro ângulo); quem a destrava é o
  `char_set_all_offline_sql`, que roda **na subida do char-server** e em mais
  lugar nenhum. Quem tentar entrar recebe *"The game server still recognizes
  your last log-in. Please try again after about 30 seconds.(8)"* — que soa
  como problema de cliente ou de rede, e não é. **Depois de linkar, reiniciar o
  char-server junto**, não só o map. Medido em 2026-08-27.

- **Subir o servidor a partir de um shell que pode ser encerrado deixa os
  quatro processos órfãos — e a subida seguinte cria DUPLICATA em vez de
  reaproveitar.** O `servidor.py subir` é idempotente, mas a idempotência
  depende de o processo anterior estar **vivo** para ele reconhecer; processo
  morto não é pulado, é recriado. Rodado de dentro de um shell de ferramenta
  (ou de qualquer coisa que o sistema possa coletar), os servidores morrem
  junto com o pai e a próxima subida sobe um segundo de cada.
  **E o sintoma aparece três passos depois da causa:** dois char-servers
  brigando pelo login-server enchem o log de `Connection to Char Server lost`
  em laço, e o volume de conexões de `127.0.0.1` dispara o anti-DDoS
  (`connect_check: DDoS Attack detected from 127.0.0.1!`), que então recusa
  **todo mundo** — inclusive quem nunca teve nada a ver com o problema. Um bot
  de openkore reconectando a cada 40s alimenta o mesmo contador.
  A saída é subir **desacoplado** (`Start-Process` no PowerShell, ou o `.bat`
  fora do shell da ferramenta) e **conferir a contagem por serviço**, não só o
  `status`: `Get-Process -Name map-server,char-server,login-server,web-server |
  Group-Object ProcessName` tem de dar 1 em cada. O `status` do `servidor.py`
  responde pela **porta**, e porta ocupada por uma das duas cópias parece
  saudável. Medido em 2026-08-27.
