# pvpGhost — o fantasma da Arena de Combate

Bot de openkore que fica 24/7 invisível dentro de `pvp_n_1-5` (a Arena de
Combate de Prontera, `npc/guerra/arena_de_combate.txt`) e aparece para
caçar quando há **um** jogador sozinho por perto.

## Os três estados

Quem decide é só a contagem de jogadores no alcance de visão. Não há
estado escondido em booleano nenhum — o `pvpghost` do console sempre diz
em qual deles ele está.

| estado        | quando                        | o que ele faz                                              |
| ------------- | ----------------------------- | ---------------------------------------------------------- |
| **chasing**   | ninguém por perto             | invisível, patrulhando a cruz da arena sem parar            |
| **attacking** | 1 (até `pvpGhost_maxPlayers`) | fisga o alvo e roda o ciclo de combate, em loop              |
| **sleeping**  | acima do limite               | `@hide`, para tudo, reavalia de `pvpGhost_sleepCheck` em N s |

Fora disso há um único caso: **morreu**. O `OnPCDieEvent` da arena joga o
morto em Prontera, e daí ele volta sozinho com `@warp pvp_n_1-5`.

**A patrulha é a cruz do mapa** — centro, sala de cima, centro, sala da
direita, centro, sala de baixo, centro, sala da esquerda, e recomeça:

```
                99,130
                  |
  70,99 ------- 99,99 ------- 131,99
                  |
                 99,68
```

`pvp_n_1-5` **não tem field próprio** no openkore: o `resnametable.txt`
do cliente aponta ele para `job_knight`, e o pathfinding roda em cima de
`fields/job_knight.fld2.gz`. As oito células acima foram conferidas nesse
arquivo antes de entrar na config — todas `TILE_WALK`.

**Dormindo ele não olha a arena a cada quadro.** Abre os olhos de 5 em 5
segundos (`pvpGhost_sleepCheck`); enquanto houver 2 ou mais, continua
dormindo. Isso é de propósito: evita ele piscar entre dormir e caçar
quando alguém anda na borda do alcance de visão.

## O ciclo de combate é uma receita, não código

Dois valores do `config.txt`, os dois listas de passos separados por `;`.
`pvpGhost_approach` roda **uma vez**, ao fisgar o alvo; `pvpGhost_cycle`
**repete** até o alvo sumir ou chegar gente demais:

```
pvpGhost_approach hide; chase 10
pvpGhost_cycle attack 4; skill SC_WEAKNESS max target range 3 unless EFST_WEAKNESS; attack 2; emotion heh; skill SC_FEINTBOMB max self; cloak; chase 3 hold
```

Os verbos que existem hoje:

| verbo                                     | o que faz                                              |
| ----------------------------------------- | ------------------------------------------------------ |
| `attack <seg>`                            | aparece e bate no alvo por `<seg>`, perseguindo         |
| `chase <seg> [hold]`                      | anda até o alvo; **acaba ao chegar**, ou em `<seg>`. `hold` faz durar o tempo inteiro |
| `hide`                                    | some com `@hide` e espera o servidor confirmar          |
| `cloak`                                   | some com o **Espreitar** e espera confirmar             |
| `show`                                    | aparece (desliga os dois) e espera confirmar            |
| `emotion <nome\|num>`                     | um emoticon (nomes em `tables/emotions.txt`)            |
| `face <to\|away>`                         | vira o corpo para o alvo, ou de costas para ele         |
| `skill <nome\|id> [lv\|max] [target\|self\|ground]` | usa uma habilidade                          |
| `skill ... range <n>`                     | anda até `<n>` células do alvo antes de lançar          |
| `skill ... unless <EFST_X>`               | pula o passo se o alvo **já** está com esse status      |
| `skill ... if <EFST_X>`                   | só lança se o alvo estiver com esse status              |
| `wait <seg>`                              | fica parado                                             |

### `chase` acaba ao chegar — e por que isso importava

Enquanto o `chase` só terminava no tempo escrito, o `chase 10` da
aproximação segurava o ciclo por **dez segundos** mesmo com o jogador
encostado. Era essa a espera entre alguém entrar na arena e o fantasma
dar o primeiro golpe — não havia delay nenhum na detecção (o laço roda a
cada 0,2s), era o passo que não sabia que já tinha chegado.

Depois do `cloak`, porém, é justamente o tempo inteiro que se quer: ele
segue de perto e sumido. Daí o `hold` no `chase 3 hold` do ciclo.

### `unless <EFST>`: não relançar o que já está no alvo

A **Máscara da Vulnerabilidade** (`SC_WEAKNESS`, Id 2297) é a que tira
**arma e escudo**: ela dispara `SC_STRIPWEAPON` e `SC_STRIPSHIELD` a 100%
furando o Coating (`status.cpp`, `case SC__WEAKNESS`), e ainda impede
reequipar as mãos (`pc.cpp`, `EQP_ARMS`). Dura de 10 a 20s conforme o
nível.

Relançar antes de cair não faz nada — o `Fail: _Weakness` do
`db/re/status.yml` recusa — mas **gasta uma Tinta para Pele** do mesmo
jeito. Por isso o `unless EFST_WEAKNESS`: o plugin lê o status **real do
alvo** (`$actor->{statuses}`, preenchido pelo pacote que o rAthena manda
para a área em `clif_status_change`) e só relança quando o efeito cai.

### O passo `skill` espera o servidor, não o relógio

Ele acaba no instante em que chega o anúncio da própria habilidade
(`packet_skilluse` com o nosso `sourceID`); `pvpGhost_skillWait` virou só
o teto para o caso do anúncio não vir.

**Isso é o que faz o Espreitar sair dentro da invisibilidade da Cópia
Explosiva**, que dura só **1,5s** (`Duration1` do Id 2304). Com a espera
fixa de 1,5s o Espreitar saía justo quando ela acabava.

> **E há uma armadilha maior aí, que custou o resto dos segundos:** a
> Cópia Explosiva liga **o mesmo bit do `@hide`**. O status `_Feintbomb`
> tem `Options: Invisible: true` no `db/re/status.yml`, que é o
> `OPTION_INVISIBLE` (0x40) que este plugin lê para saber se o `@hide`
> está ligado — e não tem `Icon:`, então nem um EFST chega para
> desempatar. Sem tratar isso, o passo `cloak` via "estou escondido" e
> mandava `@hide` para desligar, **ligando de fato** a invisibilidade de
> staff; só depois de mais um `toggleCooldown` ele desligava e aí lançava
> o Espreitar. Era esse o fantasma parado na tela. O plugin agora abre uma
> janela (`pvpGhost_feintWindow`) ao lançar a habilidade, e dentro dela o
> `@hide` não é tocado e o Espreitar sai direto — o servidor deixa, porque
> `status_check_skilluse` (`src/map/status.cpp:2209`) só barra por
> `OPTION_HIDE` e `OPTION_CHASEWALK`, nunca por `OPTION_INVISIBLE`.

### Espreitando não se lança mais nada

`status_check_skilluse` (`src/map/status.cpp:2212`) recusa **qualquer**
habilidade que não seja o próprio `ST_CHASEWALK` enquanto o
`OPTION_CHASEWALK` estiver ligado — o pedido nem vira tentativa, morre no
servidor. Por isso o passo `skill` desliga o Espreitar sozinho antes de
lançar, e só **depois** de já ter andado para perto pelo `range`: ele
chega sumido e aparece só na hora do golpe.

---

## A reação ao golpe pesado

Quando uma **habilidade** tira do fantasma mais que `pvpGhost_panicDamage`
(0,27 = 27%) do **HP máximo**, o ciclo é largado na hora e entra uma quarta
fase, `panic`. O objetivo dela é um só: calar o oponente com a **Máscara
da Tolice** (`SC_IGNORANCE`, Id 2294, `States: NoCast` — ele para de poder
usar habilidade).

A referência é o HP **máximo**, não o atual: "27% da vida dele" tem de
querer dizer a mesma coisa com a barra cheia e com ela pela metade.

São duas receitas, e quem escolhe é a distância **no momento de cada
tentativa**:

```
pvpGhost_panicNear skill SC_IGNORANCE max target range 3 unless EFST_IGNORANCE
pvpGhost_panicFar  face away; skill SC_FEINTBOMB max self; cloak; chase 4; skill SC_IGNORANCE max target range 3 unless EFST_IGNORANCE
```

Com o alvo dentro de `pvpGhost_masqueradeRange` (3, que é o `Range` do Id
2294) vale a de perto — lança de cara. Mais longe, vale a de longe: vira
de costas, Cópia Explosiva, e vai de encontro para lançar.

**Ele tenta até `pvpGhost_panicTries` vezes, e para antes se conseguir.**
A prova de que conseguiu é o `EFST_IGNORANCE` no próprio alvo, não um
chute nosso. Entre duas reações há `pvpGhost_panicCooldown` segundos, para
uma sequência de golpes não virar reação em cima de reação.

> **O `face away` é aparência, não mecânica.** Neste rAthena a Cópia
> Explosiva **não empurra quem lança**: não há `skill_blown` do `src` em
> si mesmo, e o `Knockback` do Id 2304 é aplicado a quem a bomba acerta
> (`skill_unit_onplace_timer`). Virar de costas muda o que o oponente vê,
> não para onde o fantasma vai.

O comando `pvpghost` do console mostra, além do resto, se o alvo está sem
arma, se está calado, e em que tentativa da reação ele está.

---

## A reação ao HP baixo

Abaixo de `pvpGhost_lowHpPercent` (10%) do HP **máximo**, o fantasma larga
tudo — **inclusive a fase `panic`** — e entra na fase `shadow`: **Vínculo
Sombrio** (`SC_SHADOWFORM`, Id 2287, `Range` 5) no oponente, e depois grudado
nele por `pvpGhost_lowHpTimeout` segundos.

```
pvpGhost_lowHpPercent 10
pvpGhost_lowHpTimeout 15
pvpGhost_lowHp skill SC_SHADOWFORM max target range 5; chase 15 hold
```

### O status fica em quem lança, não em quem leva

Isto é o que mais engana no Vínculo, e é o motivo de a guarda de *"já está
ligado"* olhar o **próprio fantasma** e não o oponente. Quem faz isso é o
`sc_start4(src, src, ...)` de `src/map/skills/thief/shadowform.cpp`: o alvo
entra como `val2`, e é **ele** que come o dano que o fantasma levar — até
`4 + nível` golpes (9 no nível 5), ou até a duração acabar (30 a 70s), ou até a
distância quebrar.

### O preço: enquanto o Vínculo estiver de pé, ele não bate e não lança nada

`skill_check_condition_castbegin` recusa **qualquer** habilidade a quem tem
`SC__SHADOWFORM` (`src/map/skill.cpp:8327`), e o status ainda traz `NoAttack`
no `db/re/status.yml`. Isso é o preço do golpe, não defeito do plugin — mas é o
motivo de o `lowHpTimeout` existir, e a razão de a receita terminar em
`chase 15 hold` em vez de tentar atacar.

**E grudar não é enfeite:** o próprio rAthena corta a ligação se quem lançou se
afastar mais de **dez células** do alvo (o bloco *"Shadow Form Caster Moving"*,
`src/map/map.cpp:599`). Ficar colado mantém o vínculo vivo — e é onde a apanhar
acontece, que é o ponto do golpe.

Na prática, com o fantasma abaixo de 10% e o oponente batendo, os 9 golpes
saem em poucos segundos e o vínculo se desfaz sozinho. Os 30–70s de duração só
importam se o oponente **parar** de bater: aí o fantasma fica parado até o
tempo acabar. Se isso incomodar, o caminho é ele andar para longe do alvo
quando o `lowHpTimeout` vencer — é um verbo novo (`flee`), não uma linha de
config.

`pvpGhost_lowHpTimeout` é **as duas coisas**: o teto da fase e a folga mínima
até a próxima. E o `pvpghost` do console passou a mostrar o HP e se o vínculo
está ligado.

> **Também falha calado se o alvo já estiver ligado a outra pessoa** — o
> `castendNoDamageId` exige `dstsd && !dstsd->shadowform_id`. Na arena de um
> jogador só isso nunca aparece; em outro cenário, apareceria como um Vínculo
> que nunca cola.

### As duas furtividades não são a mesma coisa

**Fora do combate** ele some com `@hide` (`OPTION_INVISIBLE`) — é de staff,
não gasta nada e não cai sozinho. **Dentro do ciclo de combate** ele some
com o **Espreitar** (`ST_CHASEWALK`, `OPTION_CHASEWALK`), que é habilidade
de jogador: é o que um Renegado de verdade faria, gasta SP e cai quando ele
leva dano. Quem escolhe é o verbo — `hide` nos estados `chasing`/`sleeping`,
`cloak` no `pvpGhost_cycle`.

As duas **nunca ficam ligadas ao mesmo tempo**: o plugin desliga uma antes
de ligar a outra, e lê o estado real em `$char->{option}` em vez de manter
booleano próprio.

> **O Espreitar também é alternador**, igual ao `@hide` (`Toggleable: true`
> no `skill_db.yml`), e — isto custa tempo — **atacar não o cancela**. O
> bloco que quebra furtividade em `src/map/unit.cpp:2732` só trata
> `SC_CLOAKING`, `CLOAKINGEXCEED` e `NEWMOON`; o `ChaseWalk` não está lá.
> Por isso o passo `attack` desliga o Espreitar de propósito, em vez de
> contar com o golpe para isso.

### Nível de habilidade: `max` é o default

`max` — ou o nível omitido, ou um número acima do que ele sabe — usa **o
nível aprendido**. É de propósito: a habilidade sobe junto com o
personagem, e ninguém precisa lembrar de mexer no `config.txt`. O Espreitar
sempre sai no máximo, sem nível na config.

**Para entrar habilidade nova no ciclo, na maioria dos casos basta mexer
na linha do `config.txt`.** Só quando a ação não couber em nenhum verbo é
que se escreve um verbo novo — é um `if` em `runStep()`, e nada mais do
plugin muda.

Três detalhes que economizam depuração:

- **`attack` fica visível sozinho**, porque `@hide` impede o golpe. E o
  relógio dos `<seg>` só começa a correr depois que o servidor confirmou
  a saída da invisibilidade — não se perde metade do ataque esperando.
- **Quem escolhe `target`/`self`/`ground` é o `TargetType` do
  `db/re/skill_db.yml` do nosso rAthena**, não o `tables/skillsarea.txt`
  do openkore. Os dois discordam justamente na Cópia Explosiva: o
  openkore a marca como habilidade de chão, o servidor a tem como
  `TargetType: Self`. Por isso o `self` na linha.
- **Habilidade que o personagem não tem é pulada**, com um aviso uma vez
  só no console. O ciclo não trava por causa disso.

---

## Trocar o personagem do fantasma

O personagem é descartável e já foi trocado uma vez. Este README **não
guarda o nome nem o slot dele** de propósito: a fonte de verdade é a
linha `char N` do `control/config.txt`.

O que importa ao criar um novo:

1. Entre no cliente com **`fantasma` / `fant4smaArena26`**, PIN **4728**.
2. **A classe é Renegado.** É dela que saem as habilidades do
   `pvpGhost_cycle` e da reação — a Cópia Explosiva (`SC_FEINTBOMB`), a
   Máscara da Vulnerabilidade (`SC_WEAKNESS`) e a Máscara da Tolice
   (`SC_IGNORANCE`).
   Habilidade que o personagem não tiver é pulada com aviso, e aí o
   fantasma vira só pancada normal.
3. **Ajuste o `char N` do `config.txt` para o slot em que ele nasceu.**
   É o passo que mais dá trabalho de descobrir depois, porque errado ele
   simplesmente entra com outro personagem.
4. **Dê a ele os dois insumos infinitos, senão as habilidades do ciclo não
   saem:**

   ```
   #item <personagem> 30993 1    Tinta para Parede Infinita
   #item <personagem> 30992 1    Pincel do Infinito
   ```

   **São dois itens para quatro insumos**, e nenhum dos dois é gasto:

   | insumo do `skill_db` | quem dispensa |
   | --- | --- |
   | Tinta para Parede (6123) — Cópia Explosiva | Tinta para Parede Infinita (30993) |
   | Pincel de Grafite (6122) — as Pinturas | Pincel do Infinito (30992) |
   | Pincel de Maquiagem (6121) — as Máscaras | Pincel do Infinito (30992) |
   | Tinta para Pele (6120) — as Máscaras | Pincel do Infinito (30992) |

   > **A regra é C++, e por isso não basta o `@item`.** Ela vive em
   > `src/custom/tinta_infinita.hpp` e `src/custom/pincel_do_infinito.hpp`, e
   > entra numa linha do `skill_get_requirement` — **map-server compilado com
   > elas, ou o item existe e não faz nada.**
   >
   > E `Amount: 0` não quer dizer "opcional": o
   > `skill_check_condition_castbegin` (`src/map/skill.cpp:9559`) reprova por
   > `index[i] < 0` antes de olhar a quantidade, então pincel que falta na
   > mochila derruba a habilidade igual a tinta que falta. Se algum insumo
   > sumir, o console avisa — o plugin escuta o `packet_skillfail` e imprime
   > o motivo uma vez.

   O `@item` só dá para si mesmo; para entregar a outro personagem é o
   char-command `#`.

   > **Por que a Tinta Infinita existe:** a Cópia Explosiva consome uma
   > **Tinta para Parede (6123)** por uso — a cada volta do ciclo, ~5,5 por
   > minuto, da ordem de **oito mil por dia**. O item 30993 zera esse
   > requisito sem ser consumido (`rathena/src/custom/tinta_infinita.hpp`,
   > 2026-08-27). O **Pincel (6122) não é o que acaba** — ele é `Amount: 0`
   > no `skill_db`, ferramenta e não custo —, mas continua sendo exigido, e
   > sem ele a habilidade falha com o mesmo "item necessário não encontrado".
4. Não vista nada de GM — o visual de GM vem só da roupa/sprite, e o
   `Level: 0` do grupo não acende aura nenhuma. Ele tem que parecer um
   jogador comum, esse é o ponto.
5. Não precisa levá-lo até a arena: o próprio plugin manda
   `@warp pvp_n_1-5` sempre que acorda fora do mapa.

## Como rodar

O Perl está em `C:\Users\User\projects\strawberry-perl-5.12` — Strawberry
**5.12.3, 32 bits**, portable (não foi instalado no sistema; apagar a
pasta desfaz). É essa versão porque o `XSTools.dll` e o `start.exe` deste
checkout linkam `perl512.dll`.

```bat
set SP=C:\Users\User\projects\strawberry-perl-5.12
set PATH=%SP%\perl\site\bin;%SP%\perl\bin;%SP%\c\bin;%PATH%
cd /d C:\Users\User\projects\openkore-master
perl openkore.pl
```

**Tem que ser numa janela de terminal de verdade.** A interface do
openkore no Windows é `Win32::Console`; sem console alocado ela não
consegue ler a largura da tela e o processo trava depois de carregar as
tabelas. Rodar minimizado está ok, rodar sem janela não.

`Win32::Console` não vinha no Strawberry portable — foi compilado com o
gcc do próprio Strawberry e instalado em `perl\site\lib\Win32\`.

### Onde olhar o log

**Não é o `logs\console.txt`.** Assim que o openkore lê o `username` ele
troca de arquivo (`Settings::update_log_filenames`). O log que interessa
é:

```
logs\console_fantasma_<N>.txt      <N> = o `char N` do config.txt
```

O `console.txt` só guarda o carregamento das tabelas e para no meio — não
é sinal de travamento.

## A conta

Grupo **Id 20, `Fantasma`**, em `rathena/conf/guerra/groups_guerra.yml`.
Dá exatamente três coisas — `@hide`, `@warp` e o `hide_session` que tira
o char do `@who`. Nada de `@kill`/`@ban`: o cabeçalho do grupo explica
por quê. Já criada:

```
userid     fantasma        (account_id 2000002, group_id 20)
senha      fant4smaArena26
pincode    4728
```

> **A senha no banco é MD5, não texto puro.** `conf/guerra/login_guerra.txt:48`
> sobrescreve o `login_athena.conf` com `use_MD5_passwords: yes`. O
> servidor faz o MD5 do que o cliente manda e compara com a coluna
> (`src/login/loginclif.cpp:279`), então o `config.txt` do openkore guarda
> a senha **em texto** e o banco guarda `MD5('...')`. Trocar a senha é:
>
> ```sql
> UPDATE login SET user_pass = MD5('nova') WHERE userid='fantasma';
> ```
>
> e a mesma string em texto no `config.txt`.

O grupo entrou no restart do servidor de 01:50. Mudança futura no
`groups_guerra.yml` pega com **`@reloadatcommand`** — não `@reloadscript`.

## O que foi mexido neste openkore

| arquivo | o quê |
| --- | --- |
| `tables/servers.txt` | bloco `[Guerra do Emperium - Local]` |
| `control/config.txt` | login, IA nativa desligada, bloco `pvpGhost_*`, `portalCompile -1`, `ignoreInvalidLogin 1` (backup em `config.txt.bak`) |
| `control/sys.txt` | `loadPlugins_list pvpGhost,reconnect` |
| `plugins/pvpGhost/pvpGhost.pl` | o plugin |

Três dessas merecem explicação:

- **`ignoreInvalidLogin 1`** — sem isso, ao errar a senha o openkore
  *pergunta* a senha no console e **grava a resposta por cima do
  `config.txt`** (`configModify` em `Network/Receive.pm:5616`). Num bot
  que roda sozinho isso destrói a config no primeiro tropeço. Aconteceu
  durante o teste: o arquivo apareceu com `password teste123`.
- **`portalCompile -1`** — o openkore compila o cache de linha de visão
  dos portais no primeiro boot, e são ~1000 mapas, vários minutos. Este
  bot nunca faz rota entre mapas (usa `@warp`), então é tempo jogado fora
  a cada início.
- **`loadPlugins_list pvpGhost,reconnect`** — a lista de fábrica traz
  `LATAMTranslate`, `AdventureAgency`, `OTP` e mais meia dúzia que este
  bot não usa. Menos plugin, menos coisa para quebrar sozinha às 4 da
  manhã. O `reconnect` fica porque é ele que faz o backoff de reconexão.

### Os dois números do `servers.txt` que costumam quebrar

- `serverType kRO_RagexeRE_2021_11_03` — casa com o `#define PACKETVER
  20211103` de `src/custom/defines_pre.hpp`.
- `charBlockSize 175` — é o `sizeof(struct CHARACTER_INFO)` de
  `src/common/packets.hpp` para esse PACKETVER (em 20211103 `hp`, `maxhp`,
  `sp` e `maxsp` viraram `int64` e o bloco saiu de 155 para 175 bytes).
  Errado, trava na tela de seleção de personagem sem dizer por quê.

Se um dia o PACKETVER mudar, os dois mudam junto.

## Ajustes do fantasma

Tudo em `control/config.txt`:

```
pvpGhost 1
pvpGhost_map pvp_n_1-5
pvpGhost_maxPlayers 1                   até quantos jogadores ele encara
pvpGhost_ignore Fulano, Ciclano         nunca conta nem ataca estes

pvpGhost_sleepCheck 5                   de quantos em quantos segundos ele
                                        reavalia a arena dormindo

pvpGhost_patrol 99 99, 99 130, 99 99, 131 99, 99 99, 99 68, 99 99, 70 99
pvpGhost_patrolTolerance 3              quão perto basta chegar do ponto
pvpGhost_patrolLegTimeout 40            desiste da perna e vai pro próximo

pvpGhost_approach hide; chase 10
pvpGhost_cycle attack 5; emotion heh; skill SC_FEINTBOMB max self; cloak; chase 3
pvpGhost_targetGrace 5                  janela ao perder o alvo de vista
pvpGhost_attackInterval 2               reenvio de fundo do ataque
pvpGhost_attackRefresh 0.4              piso entre reenvios ao alvo andando
pvpGhost_chaseDistance 1                distância de parada ao perseguir

pvpGhost_hideCommand @hide              a furtividade de fora do combate
pvpGhost_cloakSkill ST_CHASEWALK        a furtividade de dentro do combate
pvpGhost_returnCommand @warp pvp_n_1-5
```

Há mais quatro, que raramente se mexe: `pvpGhost_targetGrace` (5s —
explicado abaixo), `pvpGhost_toggleCooldown` (2s entre dois `@hide`,
porque ele é alternador), `pvpGhost_toggleTimeout` (6s até desistir de
esperar a confirmação e seguir o ciclo) e `pvpGhost_routeRefresh` (1s
entre duas rotas, para o char não tremer atrás de um alvo que anda).

> **`pvpGhost_targetGrace` não é enfeite.** O alcance de visão tem borda,
> e um jogador andando em cima dela entra e sai da lista várias vezes por
> minuto. No teste de 2026-08-27 isso apareceu como troca de estado a
> cada **0,4 segundo** — e como cada entrada em `attacking` reiniciava o
> `approach`, o ciclo nunca fechava uma volta. Com a janela, o estado
> segura por 5s e o ciclo **continua de onde parou** se o alvo voltar. O
> relógio do passo congela junto, senão um `attack 5` terminaria sozinho
> enquanto o alvo estava fora da vista.

> **`pvpGhost_delay` não existe mais.** Os 10 segundos escondido antes de
> aparecer viraram o `chase 10` do `pvpGhost_approach` — mesmo tempo, mas
> agora ele passa esses segundos *andando até o alvo*, invisível, em vez
> de parado onde o `@warp` largou.

No console do openkore, `pvpghost` mostra três linhas: estado atual e há
quanto tempo, alvo, o passo do ciclo em que ele está, e em que ponto da
patrulha parou.

## O que ele NÃO faz

- **Não escolhe habilidade sozinho.** Ele usa as que estiverem no
  `pvpGhost_cycle`, na ordem em que estiverem. Se o personagem não tiver
  alguma delas, o passo é pulado com um aviso uma vez só no console — o
  ciclo não trava.
- **A contagem é por alcance de visão, não pelo mapa inteiro.** O openkore
  só conhece quem o servidor mandou para o cliente, e isso é o raio de
  `area_size` (14 células, `conf/battle/client.conf:39`). Um jogador do
  outro canto de `pvp_n_1-5` não conta. Se um dia precisar do mapa
  inteiro, o caminho é um NPC com `getmapusers()` avisando o bot.
- **Não desvia e não cura.** Habilidade ele usa, mas só as que estiverem
  escritas no `pvpGhost_cycle`, na ordem em que estiverem — não há
  decisão nenhuma em cima de HP, SP ou do que o alvo está fazendo.
- **O golpe normal não é perseguição do plugin.** O `attack` manda um
  `sendAction(ID, 7)`, o "ataque contínuo" do cliente, e daí em diante
  quem persegue e bate é o `unit_attack` do rAthena. O `chase` do ciclo é
  outra coisa: aí sim é o `Task::Route` do openkore andando, e serve para
  os trechos em que ele está invisível e não pode atacar.

## Nota para a staff

`macro_detection_*` existe em `conf/battle/client.conf`. Se alguém com
permissão `macro_detect` rodar `@macrochecker` na arena, o fantasma vai
ser pego — ele é um bot de verdade. Vale avisar quem tem o comando.
