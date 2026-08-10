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
| 11 | fim | `battle_calc_attack_gvg_bg`, `battle_calc_weapon_final_atk_modifiers` |

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
- **Reflexo em geral** (`battle_calc_return_damage`, `battle.cpp:6816`, e o
  `CR_REFLECTSHIELD` em `battle.cpp:5118`): o dano refletido é calculado a
  partir do dano que o alvo **já tomou reduzido**, e entregue direto ao
  atacante por `battle_delay_damage`. **A resistência a humano de quem reflete
  não entra duas vezes, e a de quem toma o reflexo não entra nenhuma.**

### 4e. Dano que não é ataque

Nada disto passa por `battle_calc_cardfix` — não é ataque, é perda de HP:

- **Dano contínuo de status**: `SC_POISON`, `SC_BLEEDING`, `SC_BURNING`,
  `SC_TOXIN` e afins. Saem por `status_fix_damage`, fora de todo o cálculo de
  batalha.
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

**Ao atualizar o `rathena/`:** conferir se o enxerto do `battle.cpp` sobreviveu,
e se a lista de parcelas da linha 5535 ganhou membro novo. Parcela nova que
ninguém puser no bloco de redução repete o bug de 2026-08-09, calada.
