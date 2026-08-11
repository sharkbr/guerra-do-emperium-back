# Redução de dano — o que entra na conta, e o que escapa

**Para que serve este arquivo:** responder, sem abrir o C++, se um dano
específico passa ou não pela redução de cartas do alvo — a `bSubRace`
(resistência a humano) e as irmãs dela. É documento de **consulta**: leia a
seção da sua dúvida, não o arquivo inteiro.

Ele existe porque em 2026-08-09 um Sura com **110%** de resistência a humano
tomou **53.061** de um Rune Knight que só tinha a arma no corpo. A resistência
estava certa; uma parcela do dano é que não estava sendo oferecida à conta. A
história inteira está no `HISTORICO.md`, "A resistência a humano que não fechava
a conta".

Todos os números de linha são do nosso `rathena/src/map/battle.cpp`, **já com o
nosso enxerto** (§2 do `CLAUDE.md`). Ao atualizar o `rathena/`, eles andam.

---

## 1. A regra, em uma frase

**A redução fecha a conta.** Todo bônus multiplicativo entra antes dela; o que
sobra depois é só dano fixo que a habilidade declara explicitamente como
acréscimo fixo.

E a redução fecha até um teto. O `APPLY_CARDFIX` (`battle.cpp:811`) grampeia o
multiplicador num piso nosso, e não no zero do rAthena — ver §1b.

**Depois de tudo isso vem uma segunda redução, que não é de carta:** na guerra e
nos mapas `pvp` o dano final é cortado em 80%. É outra camada, multiplicativa
sobre esta, e é a §1c.

---

## 1b. O teto de 99,9% — nada é imune

**`conf/guerra/battle_guerra.txt` → `reducao_dano_teto: 999`** (milésimos).

No rAthena puro o `APPLY_CARDFIX` usa `max(0, fix)`: somando **100% de
resistência, o dano vira zero**. Não é um teto de 99% que ninguém percebeu — é
imunidade completa a tudo que passa por carta, e um Sura de guerra chegava a
110% só com equipamento de loja (2026-08-09).

Desde 2026-08-10 o `0` virou um piso configurável
(`src/custom/reducao_de_dano.hpp`, `reducao_piso()`):

| Valor | Efeito |
|---|---|
| `999` | **o nosso** — no máximo 99,9% de redução; sempre passa 1 milésimo |
| `990` | no máximo 99% |
| `1000` | desliga a trava e devolve o comportamento do rAthena |

Muda com **`@reloadbattleconf`**, sem recompilar.

**Por que o piso mora no fim da conta e não no passo da raça:** o `cardfix` é
uma conta só, encadeada — elemento, tamanho, raça, classe, distância — e cada
passo é divisão inteira. Grampear no meio não sustenta: um `cardfix` reduzido a
1 no passo da raça vira **0** no passo seguinte (`1 * 90 / 100 == 0`) e a
imunidade volta pela porta dos fundos.

**A consequência que precisa ser dita:** o teto vale para a redução de carta
**inteira**, não só para a de raça. Combinação de resistência a elemento, a
tamanho ou a classe que chegasse a 100% também passa a deixar 0,1%. É de
propósito — a regra é "nada é imune" —, mas quem for calibrar resistência a
elemento precisa saber.

E o teto **não alcança** nada da §4: o que já escapava da redução de carta
continua escapando por inteiro.

---

## 1c. A redução geral de 80% — guerra e mapas `pvp`

**`conf/guerra/battle_guerra.txt`: dez linhas em `20` — cinco
`gvg_*_attack_damage_rate` e cinco `pvp_dano_*` — mais
`reducao_dano_isenta_habilidade: 0`.**

Desde 2026-08-10, em mapa de guerra e em mapa `pvp` **o dano final é multiplicado
por 0,20, sem exceção dentro do cálculo de batalha**.

**O número não é do bRO.** Nasceu em 70%, que era como o bRO estava — decisão
tomada lá com a comunidade quando os danos ficaram altos demais —, e o dono subiu
para 80% no mesmo dia: *"70 era como o bRO estava, e me parece alto ainda"*. Neste
número o servidor **não segue mais o bRO**, e é bom lembrar disso antes de
"corrigir" para 70 achando que se está voltando à referência.

**Isto NÃO é redução de carta, e é o ponto que evita a conta errada:** as duas
camadas **se multiplicam**. Alvo com 50% de resistência a humano na arena toma
`0,50 × 0,20 = 10%` do dano bruto — não 30%, e não "130% de redução".

| Ambiente | Opções | De quem são |
|---|---|---|
| Guerra (`gvg`, `gvg_castle`, versões TE) | `gvg_weapon/magic/misc/short/long_attack_damage_rate` | do rAthena; padrão dele é 60 e 80 |
| Mapas `pvp` (84 arenas + `pvp_2vs2` + 3 `turbo_e_*`) | `pvp_dano_arma/magia/misc/curta/longa` | **nossas** (`src/custom/reducao_geral.hpp`) |
| Batalha Campal (`battleground`) | `bg_*_attack_damage_rate` | do rAthena — **intocadas**, seguem 60/80 |

**Os números dizem quanto do dano PASSA, não quanto ele cai.** `20` é redução de
80%. É a convenção do rAthena, mantida de propósito para os dois blocos lerem
igual; ler "20" como "reduz 20%" inverte a conta e o servidor não reclama.

**Os dez ficam no mesmo número, por pedido explícito** — *"não quero diferenciar
habilidades de ataque"*. A separação em cinco por ambiente é do rAthena
(habilidade reduz por TIPO, ataque normal por ALCANCE) e continua existindo porque
é por onde a informação chega; o que não se faz é **usá-la**. Mexer em um dos dez
é mexer nos dez — deixar um atrás não dá erro, e o sintoma é "tal classe passou a
doer mais".

### Por que a metade do PvP precisou de C++

O rAthena tem os cinco `pk_*_attack_damage_rate`, que fazem exatamente isso e são
inclusive checados contra o mapflag `pvp` (`battle.cpp:2038`). Só que estão
trancados atrás do **`pk_mode`**, e `pk_mode` não é uma opção de dano: o
`map.cpp:3791` marca **todo mapa do servidor** como `pvp`, e vêm junto penalidade
de morte por jogador, EXP extra por diferença de nível, `pk_min_level` e o sumiço
da UI de PvP. Para reduzir dano numa arena, o rAthena pede que a cidade inteira
vire campo aberto.

Daí o `src/custom/reducao_geral.hpp`: os mesmos cinco multiplicadores, ligados ao
mapflag `pvp` e a nada mais. Cinco chamadas no `battle.cpp` (`CLAUDE.md` §2).

### Ninguém escapa — e por que a isenção do rAthena teve de cair

O rAthena isenta da redução de guerra a habilidade com `IgnoreGvgReduction: true`
no `db/re/skill_db.yml`. No renewal são **duas**: **`NJ_ZENYNAGE`** (Chuva de
Moedas) e **`GN_FIRE_EXPANSION_ACID`**.

**Com 80% de redução, isenção não é detalhe — é dominância.** A habilidade que
escapa passa a valer **cinco vezes** o dano de qualquer outra no mesmo mapa. O
pedido de *"TODOS os danos de pvp"* fechou a porta: `reducao_dano_isenta_habilidade`
vale `0`, e as duas são reduzidas como o resto.

**O interruptor vale para os DOIS ambientes de uma vez**, e é de propósito: a
função `reducao_isenta_habilidade()` foi enxertada também dentro do
`battle_calc_gvg_damage` do rAthena, no lugar da checagem original. Assim a guerra
e a arena não podem divergir. `1` devolve as duas isenções, nos dois lugares, sem
recompilar.

**A campal tem a isenção irmã e ela ficou de pé** (`INF2_IGNOREBGREDUCTION`, em
`battle_calc_bg_damage:2139`). Se um dia a campal entrar na regra, faltam as cinco
linhas de `bg_*` **e** esse sexto enxerto — sem ele a Chuva de Moedas fica
dominante lá.

### O que AINDA fica de fora, e não tem conserto por aqui

Esta é a **última palavra** sobre o dano do golpe: alcança até o que a §4 lista
como imune a carta — Assalto do Falcão, armadilha de Ranger, o dano fixo de
Asura, a Lâmina de Aura. Com a isenção desligada, **não sobra exceção dentro do
cálculo de batalha**. Sobram duas coisas, e nenhuma se resolve nestas cinco
chamadas:

1. **O que não é ataque**: dano contínuo de status, `bonus2 bHPVanishRate`,
   `percentheal` negativo de script, dano entregue por NPC. Saem por
   `status_fix_damage`, fora de todo o cálculo de batalha. **A lista fechada, com
   fórmula, intervalo e quem aplica cada um, é a §1d** — levantada em 2026-08-10
   justamente para responder se esse dano serve de alavanca de balanceamento.
2. **Mapa que não é de guerra nem `pvp`.** Fora deles a redução não existe: campo
   aberto, masmorra e instância seguem intactos.

**Não há exceção por tipo de atacante.** O caminho do `pk_mode` reduz só entre
jogador e jogador; o nosso reduz tudo que acerta alguém no mapa — Homúnculo,
mercenário, armadilha, invocação. É a paridade com a guerra, e é o que evita
repetir o furo da §4f. **Consequência:** monstro em mapa `pvp` também bate 20%.
Hoje isso não alcança nada — nenhum mapa `pvp` do servidor é mapa de caça —, mas
campo com monstro que um dia receba o mapflag `pvp` fica fácil junto, calado.

Valor muda com **`@reloadbattleconf`**, sem recompilar. `100` nos dez devolve o
dano cheio.

---

## 1d. O inventário do que escapa da redução geral

**Para que serve esta seção:** a §1c diz que o dano que não é golpe escapa dos
80%. Isto é **a lista fechada**, levantada na fonte em 2026-08-10 a pedido do
dono, com a pergunta certa por trás: *se esse dano ficou relativamente cinco vezes
mais forte, ele serve como parte do balanceamento?*

**A resposta curta: não é muita coisa — são 13 danos contínuos e 4 avulsos** —,
**mas metade da lista não alcança jogador em PvP nosso**, e das que alcançam **a
maioria não mata**. Quem quiser usar isto como alavanca precisa da coluna "mata?"
tanto quanto da coluna "quanto".

**Como esta lista foi levantada, para poder ser refeita:** todo dano que chega a
um jogador **sem passar por `battle_calc_damage` nem por
`battle_calc_return_damage`** — que são os dois lugares onde as nossas cinco
chamadas moram. Na prática, os chamadores de `status_zap`,
`status_percent_damage`, `status_fix_damage` e `status_damage` dentro do
`status_change_timer` (`status.cpp:14135`), mais os de `battle_fix_damage`.

### A. Dano contínuo de status (DoT) — a lista inteira

`H` = HP máximo do alvo. "por segundo" é o dano dividido pelo intervalo, para dar
para comparar; nenhum deles tem intervalo configurável por nós.

| Status | Dano por tique | Tique | Por segundo | Mata? | Quem aplica |
|---|---|---|---|---|---|
| `SC_DPOISON` Veneno Mortal | `2 + H/50` | 1s | **2,0% H** | **não** — para em 25% HP | proc do Envenenamento (EDP) |
| `SC_POISON` Veneno | `2 + 3H/200` | 1s | **1,5% H** | **não** — para em 25% HP | **Envenenar** (TF_POISON), Pó Venenoso, Faca Envenenada |
| `SC_LEECHESEND` Sanguessuga | `VIT×(nv−3) + H/100` | 1s | **1,0% H + VIT×(nv−3)** | **sim** | Arma Envenenada (Guilhotina Cruzada) |
| `SC_MAGICMUSHROOM` | `3% H` | 4s | 0,75% H | **não** — `damage = hp−1` | Arma Envenenada (GC) |
| `SC_BURNING` Queimadura | `1000 + 3% H` | 3s | 0,33% H **+ 333 fixo** | **sim** | **Sopro do Dragão**, Armadilha Incendiária, Magma Eruption |
| `SC_STONE` Petrificação | `1% H` | 5s | 0,2% H | **não** — para em 25% HP | Maldição de Pedra e afins |
| `SC_BITESCAR` | `(nv + DEX/25)% H` | 1s | **até ~10% H** | **não** | `SU_SCAROFTAROU` (Doram) — **10% de chance** |
| `SC_BLEEDING` Sangramento | `200 a 799` | 10s | ~50 fixo | **sim, em jogador** | Golpe Traumático, Tiro Perfurante, Terror Ácido, Mass Spiral |
| `SC_PYREXIA` | `100` | 3s | 33 fixo | **sim** | Arma Envenenada (GC) |
| `SC_TOXIN` | `1` de HP + 3% MaxSP | 10s | irrisório em HP | não | Arma Envenenada (GC) |
| `SC_BURNT` | `2000` | 1s | 2000 fixo | **não** — `damage = hp−1` | `NPC_FIRESTORM` — **só monstro** |
| `SC_TEARGAS` Gás Lacrimogêneo | `val2` | 2s | — | sim | Genético (`GN_FIRE_EXPANSION_TEARGAS`) |
| `SC_GRADUAL_GRAVITY` | `val2% H` | 1s | — | sim | 4ª classe — **não alcançável neste cliente** |

**A leitura que decide:** as quatro primeiras escalam com HP máximo, e é só nelas
que a conversa de balanceamento existe. As de dano fixo (Sangramento 200–799,
Pyrexia 100) eram ruído antes e continuam ruído — **80% de redução não as promove
a nada**, porque o problema delas nunca foi o dano dos outros ser alto, era o
delas ser baixo em termos absolutos.

**E as três mais fortes não matam.** Veneno e Veneno Mortal param em 25% de HP;
Bite Scar não pode matar. Elas empurram o alvo para perto da morte e **entregam o
golpe final a outra pessoa** — o que em arena é bom demais para ignorar, e em
duelo 1×1 é quase nada.

**O que sobra como dano de status capaz de fechar uma luta sozinho:**
Sanguessuga, Queimadura e Pyrexia. As três são de classe específica — Guilhotina
Cruzada, Cavaleiro Rúnico / Ranger, Guilhotina Cruzada.

### B. Dano direto que também não é golpe

| O quê | Quanto | Mata? | Onde |
|---|---|---|---|
| `bonus2 bHPVanishRate` / `bSPVanishRate` | % do HP/SP **máximo**, por golpe | **não** | `battle.cpp:6776` |
| Prisão Branca ao acabar | `400 × nível` | sim | `status.cpp:13837` (`WL_WHITEIMPRISON`) |
| Controle Gravitacional ao acabar | `val2` | sim | `status.cpp:13910` (`SJ_BOOKOFDIMENSION`) |
| **Cotovelada Ascendente** | a parcela nova, calculada do zero por `battle_calc_base_damage` | sim | `battle.cpp:5247` |

**A Cotovelada Ascendente (`SR_CRESCENTELBOW`) é a única da lista que é dano de
combate de verdade e mesmo assim escapa** — ela sai por `battle_fix_damage`, que
não passa pelo `battle_calc_damage`. **É a primeira candidata a virar bug
reportado**, e a mais fácil de confundir com furo da redução.

Não confundir com as vizinhas dela, que **estão certas**: Instinto de Defesa
(`ST_REJECTSWORD`), Reflect Damage e Devoção reproduzem um dano **que já veio
reduzido** — carregar o mesmo número para outro alvo não é escapar.

### C. Auto-dano — aparece na conta e não é de ninguém

Nenhum destes é dano de inimigo, e por isso nenhum é alavanca de PvP; estão aqui
só para não serem confundidos com furo ao medir: Insígnias elementais (1% H/s),
Superaquecimento do Mado, o custo de HP do Frenesi, Full Throttle ao acabar.

### D. Script e NPC

`percentheal` negativo, `unitkill`, dano entregue por NPC e comando de GM. Não
passam por cálculo de batalha nenhum — e no nosso servidor não há NPC que dê dano
em jogador dentro de arena.

### O veredito, para a pergunta que originou esta seção

**Como alavanca de balanceamento, isto serve pouco — e o motivo é que a lista é
enviesada por classe.** Quem ganha com o dano de status ter ficado 5x mais
relevante é, em ordem: **Guilhotina Cruzada** (três venenos, um deles mata),
**Cavaleiro Rúnico / Ranger** (Queimadura), **Ladrão e derivados** (Envenenar) e
**Doram** (Bite Scar, se a sorte dos 10% ajudar). Classe sem acesso a status não
ganhou nada.

Se o objetivo é "PvP mais longo", isto já está feito pelos 80%. Se o objetivo é
"dar saída para lutas que travam em ninguém morrer", o dano de status **não
resolve**, porque as três parcelas mais fortes param em 25% de HP.

**O que mexer nisto exigiria:** nenhum destes números é configurável — todos são
literais no `status.cpp`, dentro do `status_change_timer`. Ajustar qualquer um é
`src/custom/` e recompilar, do mesmo jeito que a redução de PvP foi.

---

## 2. A ordem da conta (dano físico, renewal)

Isto é o que decide tudo o que vem abaixo. No renewal o dano físico é montado em
**parcelas**, e a redução do alvo é aplicada **em cada parcela, antes de somar**:

| # | Onde | O que acontece |
|---|---|---|
| 1 | `battle_calc_skill_base_damage` | nascem `statusAtk`, `weaponAtk`, `equipAtk`, `masteryAtk`, `percentAtk` |
| 2 | `battle.cpp:5499` | cartas **do atacante** (só ele) |
| 3 | **`battle.cpp:5509`** | **cartas do ALVO — a redução. Parcela a parcela.** |
| 4 | `battle.cpp:5528` | nosso enxerto: o `percentAtk` entra aqui |
| 5 | `battle.cpp:5535` | `wd.damage = statusAtk + weaponAtk + equipAtk + percentAtk` |
| 6 | `battle.cpp:5535+` | P.ATK, crítico, curta/longa distância — **multiplicativos** |
| 7 | `battle.cpp:5577` | multiplicador da habilidade — **multiplicativo** |
| 8 | `battle.cpp:5580` | `battle_calc_skill_constant_addition` — **dano fixo, SOMADO** |
| 9 | `battle.cpp:5635` | redução por DEF |
| 10 | `battle.cpp:5637` | `battle_calc_attack_post_defense` — **dano fixo, SOMADO** |
| 11 | fim | `battle_calc_attack_gvg_bg`, `battle_calc_weapon_final_atk_modifiers` — é aqui que a **redução geral de 80%** da §1c entra, dentro do `battle_calc_damage` e do `battle_calc_gvg_damage` |

**Por que reduzir na etapa 3 dá no mesmo que reduzir no fim:** tudo entre a 5 e a
7 é multiplicação, e multiplicação comuta. Reduzir parcela a parcela antes da
soma é idêntico a reduzir no fim — **desde que toda parcela entre na etapa 3**.
Era exatamente isso que faltava: o `percentAtk` não entrava.

**Onde escapa, então:** nas etapas 8 e 10, que **somam** depois da conta.

Magia e "misc" não têm esse problema — a redução é aplicada de uma vez sobre o
dano inteiro (`battle.cpp:6016` para magia no renewal, `battle.cpp:6652` para
misc), e tudo o que vem depois é multiplicativo.

---

## 3. O que a redução cobre

Quando ela roda, roda inteira. Estão todos no mesmo bloco
(`battle.cpp:1094` em diante):

- `bonus2 bSubRace,<raça>,n` e `bonus2 bSubRace,RC_All,n` — **somam na mesma
  conta**, então Cocar (`RC_All`) e Anel (`RC_Player_Human`) se acumulam
- `bonus3 bSubRace,<raça>,n,<bf>` (a versão com filtro de tipo de ataque)
- `bonus2 bSubRace2,...` (raça 2, tipo Illusion/Vampire)
- `bonus2 bSubEle,...`, `bonus2 bSubDefEle,...`
- `bonus2 bSubSize,...`
- `bonus2 bSubClass,Class_Normal|Class_Boss,n`
- `bonus bNearAtkDef` / `bonus bLongAtkDef`
- `SC_DEF_RATE` / `SC_MDEF_RATE`

**Jogador atacante é `RC_Player_Human` ou `RC_Player_Doram`, nunca
`RC_DemiHuman`.** Item que só tem `bSubRace,RC_DemiHuman` não vale nada em PvP,
por mais que a descrição diga "Humanoide".

---

## 4. O QUE NÃO ENTRA NA REDUÇÃO

### 4a. Habilidades que ignoram a carta de defesa do alvo

`IgnoreDefCard: true` no `db/re/skill_db.yml` liga o `NK_IGNOREDEFCARD`, e o
bloco inteiro da §3 é **pulado** — raça, elemento, tamanho, classe, tudo.

Nome em português pela tabela que o cliente lê (`skillinfolist.lub`, regra 12 do
`CLAUDE.md`); o que está em branco lá fica em inglês aqui.

| Habilidade | Nome na tela | Classe |
|---|---|---|
| `HT_LANDMINE` / `MA_LANDMINE` | Armadilha Atordoante | Caçador |
| `HT_BLASTMINE` | Instalar Mina | Caçador |
| `HT_CLAYMORETRAP` | Armadilha Explosiva | Caçador |
| `SN_FALCONASSAULT` | Assalto do Falcão | Sniper |
| `RA_WUGSTRIKE` | Investida de Worg | Ranger |
| `RA_WUGBITE` | Mordida Feroz | Ranger |
| `PF_SOULBURN` | Sifão de Alma | Professor |
| `NC_SELFDESTRUCTION` | Autodestruição | Mecânico |
| `NC_MAGMA_ERUPTION_DOTDAMAGE` | (dano contínuo do Magma Eruption) | Mecânico |
| `SJ_NOVAEXPLOSING` | Nova Explosion | Star Emperor |
| `SP_SOULEXPLOSION` | Soul Explosion | Soul Reaper |
| `HVAN_EXPLOSION` | Autodestruição | Homúnculo |
| `NPC_SELFDESTRUCTION`, `NPC_EVILLAND`, `NPC_ICEMINE`, `NPC_FLAMECROSS`, `NPC_MAXPAIN_ATK`, `NPC_KILLING_AURA`, `NPC_MAGMA_ERUPTION_DOTDAMAGE` | — | monstro/NPC |

E mais três que **não têm a flag no `.yml`** — o C++ liga na hora
(`battle.cpp:6563`), então procurar no `skill_db` não acha:
**`RA_CLUSTERBOMB`** (Bomba Relógio), **`RA_FIRINGTRAP`** (Armadilha
Incendiária) e **`RA_ICEBOUNDTRAP`** (Armadilha Glacial).

> Para a guerra, os que importam são o Assalto do Falcão, a Investida de Worg e
> a Mordida Feroz, as armadilhas de Caçador e de Ranger, o Nova Explosion e o
> Soul Explosion. **Nenhum equipamento de resistência a humano protege deles.**

### 4b. Habilidades que ignoram só uma parte

- **`IgnoreElement`** — pula só a parcela de elemento (`bSubEle`); **a raça
  continua valendo**. São 16, entre elas `NJ_ZENYNAGE` (Chuva de Moedas),
  `KO_MUCHANAGE` (Explosão de Moedas), `KO_MAKIBISHI` (Estrepes), `GS_FLING`
  (Atirar Moedas), `RL_D_TAIL` (Dragon Tail) e `SU_SV_ROOTTWIST_ATK`.
- **`IgnoreLongCard`** — pula só o `bonus bLongAtkDef`. Um caso só, e é
  conhecido: **`SR_GATEOFHELL`** (Portões do Inferno).

### 4c. Dano fixo somado depois da conta

Estes são somados nas etapas 8 e 10 da §2, ou seja, **depois** de a redução ter
fechado. É o comportamento correto: a habilidade declara um acréscimo fixo.

`battle_calc_skill_constant_addition` (`battle.cpp:4488`):

| Habilidade | Acréscimo fixo |
|---|---|
| `MO_EXTREMITYFIST` — Punho Supremo de Asura | `250 + 150 × nível` |
| `PA_SHIELDCHAIN` — Choque Rápido | valor do escudo, sorteado |
| `GS_MAGICALBULLET` — Bala Mágica | o MATK do atirador |
| `HT_FREEZINGTRAP` — Armadilha Congelante | `40 × nível de RA_RESEARCHTRAP` |

`battle_calc_attack_post_defense` (`battle.cpp:4899`):

| Efeito | Acréscimo fixo |
|---|---|
| `SC_AURABLADE` — Lâmina de Aura | `(3 + nível) × nível base do atacante` |

### 4d. Contra-ataque e reflexo — não é o seu dano, é o dele

`battle_calc_weapon_final_atk_modifiers` roda no fim de tudo, e o que ele produz
não passa por redução nenhuma sua:

- `SC_REJECTSWORD` — Instinto de Defesa; `SC_POISONREACT` — Refletir Veneno;
  `SC_CRESCENTELBOW` — Cotovelada Ascedente

  **Os três saem por `battle_fix_damage`, que não passa pelo
  `battle_calc_damage`** — logo escapam também da redução geral de 80% (§1c), e
  não só da de carta. Nos dois primeiros isso é inofensivo: eles devolvem uma
  fração de um dano **que já veio reduzido**. **A Cotovelada Ascendente é a
  exceção que importa:** metade do valor dela nasce de um
  `battle_calc_base_damage` novo (`battle.cpp:5247`), que nunca viu redução
  nenhuma. É a candidata mais provável a ser reportada como "furou a redução" —
  e, dessa vez, quem reportar tem razão. Ver §1d, bloco B.
- **Reflexo em geral** (`battle_calc_return_damage`, `battle.cpp:6816`, e o
  `CR_REFLECTSHIELD` em `battle.cpp:5118`): o dano refletido é calculado a
  partir do dano que o alvo **já tomou reduzido**, e entregue direto ao
  atacante por `battle_delay_damage`. **A resistência a humano de quem reflete
  não entra duas vezes, e a de quem toma o reflexo não entra nenhuma.**

### 4e. Dano que não é ataque

Nada disto passa por `battle_calc_cardfix` — não é ataque, é perda de HP. **Nem
pela redução geral de 80% da §1c**, e é por isso que a lista completa virou seção
própria: **§1d**, com fórmula, intervalo, se mata e quem aplica cada um. Aqui fica
só o resumo.

- **Dano contínuo de status**: `SC_POISON`, `SC_BLEEDING`, `SC_BURNING`,
  `SC_TOXIN` e afins — **treze ao todo**, listados na §1d. Saem por
  `status_fix_damage`, fora de todo o cálculo de batalha.
- **`bonus2 bHPVanishRate` / `bSPVanishRate`**: tiram HP/SP do alvo por
  percentual, direto.
- **Script**: `percentheal` negativo, `unitkill`, dano de NPC. Nenhum passa por
  aqui.
- **Emperium e afins**: alvo de tipo planta cai no `battle_calc_attack_plant`,
  que curto-circuita a conta em 1 de dano.

### 4f. Armas e encantamentos — o caso que custou caro

**`bonus bAtkRate` (ATQ +x%) do atacante gerava uma parcela que escapava
inteira.** Corrigido por nós em 2026-08-09; hoje entra na conta. Fica
registrado porque é a família de bônus a vigiar:

- item com `bonus bAtkRate` — o caso vivo foi a **Lâmina Sagrada**
  (`Copy_Gram`, 500009), que em +16 dá `bAtkRate 160`
- **opção aleatória `VAR_ATKPERCENT`** (`db/re/item_randomopt_db.yml`, Id 13) —
  é `bonus bAtkRate` com outro nome, e tinha o mesmo furo

Não confundir com o que **ignora DEF** e é outra coisa:

- **Carta Memória de Thanatos** (4399) = `bonus bDefRatioAtkClass,Class_All`.
  Ignora **DEF**, não passa perto da redução por raça. Ela amplifica muito o
  dano contra alvo blindado, e por isso *parece* estar furando resistência.
- `bIgnoreDefRace`, `bIgnoreDefClass`, `bIgnoreMdefRace` — idem: DEF/MDEF, não
  redução de carta.

---

## 5. O que ENTRA, mas parece que não

Estes são multiplicativos aplicados **depois** da soma das parcelas. Como a
redução já zerou cada parcela, multiplicar zero continua zero — eles **não**
furam nada, por maiores que sejam:

- **P.ATK** (`bonus bPAtk`) e **S.MATK**
- **taxa de crítico** (`bonus bCritAtkRate`) e `non_crit_atk_rate`
- **`bonus bLongAtkRate` / `bShortAtkRate`**
- **o multiplicador da própria habilidade** (etapa 7)
- **refino, `bonus bBaseAtk`, `bonus bAtk`** — entram nas parcelas, antes da
  redução
- **conjuntos (`item_combos`)** — são `bonus` comuns; o `pc_checkcombo`
  (`pc.cpp:11806`) deixa **uma mesma carta fechar dois conjuntos ao mesmo
  tempo**, e os dois somam

---

## 6. Como conferir um caso novo

Quando aparecer "fulano furou minha resistência", nesta ordem:

0. **Onde foi?** Guerra e mapa `pvp` cortam 80% do dano final por cima de tudo
   (§1c), e campo aberto não corta nada. Comparar um número medido na arena com
   um medido no campo dá diferença de **5x** que **não tem nada a ver com
   resistência**. Medir sempre no mesmo mapa.
1. **A habilidade tem `IgnoreDefCard`?** `grep -B 40 "IgnoreDefCard: true"` no
   `db/re/skill_db.yml`, ou olhe a §4a. Se tem, acabou — não é bug.
2. **É dano fixo declarado?** §4c. Se é, também não é bug.
3. **A soma do alvo é a que ele acha que é?** Refaça pelo `item_db`, **não pela
   descrição na tela** — a descrição vem do `itemInfo` do cliente e diverge
   (§5 do `CLAUDE.md`). Some `RC_Player_Human` **e** `RC_All`.
4. **Sobrou dano com a soma acima de 100?** Então há parcela fora da etapa 3 da
   §2. Abra o bloco `"Card Fix for target"` (`battle.cpp:5509`) e compare a
   lista de parcelas com a soma da linha 5535. **Parcela que aparece na soma e
   não aparece no bloco é o furo.**
5. **Meça na tela.** Verificação offline que passa não é prova de efeito. Mude
   só o termo suspeito (desrefinar a arma, tirar uma carta) e olhe o número.

**Ao atualizar o `rathena/`:** conferir se os enxertos do `battle.cpp`
sobreviveram — são **sete** chamadas hoje (`CLAUDE.md` §2) —, e se a lista de
parcelas da linha 5535 ganhou membro novo. Parcela nova que ninguém puser no
bloco de redução repete o bug de 2026-08-09, calada.

**O enxerto mais fácil de perder na atualização é o do
`battle_calc_gvg_damage`**, porque ele não *acrescenta* uma linha: ele
**substitui** o `if (skill_get_inf2(skill_id, INF2_IGNOREGVGREDUCTION))` do
rAthena pelo nosso `reducao_isenta_habilidade(skill_id)`. Um merge que traga a
linha original de volta compila, sobe, e devolve calado a dominância da Chuva de
Moedas na guerra. Procurar por `INF2_IGNOREGVGREDUCTION` depois de atualizar: se
ele reapareceu dentro do `battle_calc_gvg_damage`, o enxerto morreu.

E conferir se `battle_calc_damage` e `battle_calc_return_damage` continuam sendo
por onde **todo** dano passa: as quatro chamadas do `reducao_pvp` estão lá
justamente porque hoje não há caminho de dano de golpe fora desses dois. Caminho
novo que o rAthena crie fica sem a redução de 80% na arena, sem aviso.
