# Armadilhas: Combate e números

Redução de dano, precisão, status de monstro, castelo e guerra.

**Este arquivo é um dos seis cadernos de armadilhas do projeto.** O índice de
todos eles — uma linha de gatilho por armadilha, com o caderno onde o caso
está contado por inteiro — está na §5 do `CLAUDE.md`. **Leia aqui a entrada
que o gatilho apontar**; ler o caderno inteiro não é para ser preciso.

As entradas abaixo produziram diagnóstico falso e custaram retrabalho. Cada
uma traz o sintoma, a causa medida (com arquivo e linha, quando existe) e a
saída — e a medição é o que separa esta lista de um palpite. **Armadilha
nova se escreve nas duas pontas:** o caso aqui, o gatilho na §5.

---

- **Nem toda parcela de dano do renewal passa pela redução de cartas.** O dano
  físico é montado em `statusAtk`, `weaponAtk`, `equipAtk`, `masteryAtk` e
  `percentAtk`, e a redução do alvo é aplicada **parcela a parcela, antes da
  soma** (`battle.cpp`, bloco "Card Fix for target"). Dá no mesmo que reduzir no
  fim — tudo que vem depois é multiplicativo — **desde que toda parcela entre**.
  O `percentAtk` não entrava (corrigido por nós; ver §2). Ao mexer em dano,
  desconfiar sempre: parcela que não está naquele bloco ignora resistência a
  raça, elemento, tamanho e classe, todas de uma vez, e nada denuncia.
  **A lista completa do que escapa — habilidades com `IgnoreDefCard`, dano fixo,
  reflexo, dano de status — está em `REDUCAO-DE-DANO.md`.** Consultar antes de
  chamar de bug.

- **MONSTRO NÃO TEM RESISTÊNCIA POR RAÇA — não existe "redução humano" para
  mob.** O `bonus2 bSubRace,RC_Player_Human` é bônus de **jogador**: o
  `battle_calc_cardfix` lê o `subrace` do `tsd`, e alvo `BL_MOB` **não tem ramo
  naquela função**. Não há como dar resistência a humano a um guardião por
  `db/`, por script ou por carta — e o pedido chega exatamente com essa
  palavra, porque é a que o dono conhece do lado do jogador. O que existe e
  serve é o **`md->damagetaken`** (o `DamageTaken:` do `mob_db`, também
  `setunitdata UMOB_DAMAGETAKEN`), aplicado no fim do `battle_calc_damage`
  (`battle.cpp:2072`) como multiplicador sobre tudo que acerta aquele monstro.
  É **por instância** — mora no `md`, não no `mob_db` —, então não contamina
  outros do mesmo ID. Mas é **inteiro em porcentagem**: `1` é o menor valor
  útil, ou seja **99% é o teto**, e 99,9% não cabe nele.

- **Dentro de castelo, a redução de 80% da guerra vale 24 HORAS POR DIA — e
  vale também quando o alvo é MONSTRO.** O mapflag é `gvg_castle`, posto
  estaticamente em `npc/mapflag/gvg.txt`, e o `mapdata_flag_gvg2`
  (`map.hpp:977`) só olha mapflag: não consulta o `agit_flag`. O `gvgon` da
  Guerra do Emperium acrescenta o `MF_GVG` por cima, mas a redução já estava
  ligada. Duas consequências: dano medido em castelo fora do horário de guerra
  é o **mesmo** da guerra (ótimo para testar), e qualquer resistência dada a um
  guardião **multiplica** com os `gvg_*_attack_damage_rate: 20` — 99% de
  redução no monstro com os nossos 20% que passam dá `0,20 × 0,01`, ou seja
  **0,2% do dano bruto**. Calibrar o HP sem fazer essa conta erra por duas
  ordens de grandeza.

- **`status_calc_mob_` sem nenhuma flag LIBERA o `md->base_status` e passa a
  usar o status compartilhado do `mob_db`.** O `if (!flag) { … aFree(md->base_status);
  … return 0; }` (`status.cpp:2812`) é a porta de saída de todo monstro comum.
  Quem enxertar ajuste de status de monstro **depois** dessa linha precisa
  garantir que alguma flag esteja ligada, senão escreve no registro do banco de
  monstros e altera **todos** os monstros daquele ID de uma vez — calado, e
  sobrevivendo até o próximo `@reloadmobdb`. O `setunitdata` não cai nessa
  armadilha porque aloca o `base_status` próprio antes de escrever
  (`script.cpp:19420`).

- **No renewal, a chance de acerto é literalmente `hit − esquiva` em pontos
  percentuais — e o piso de 5% esconde o quanto se está longe.** A taxa base do
  renewal é **zero** (no pre-renewal era 80), e a única coisa somada a ela é
  aquela subtração; o resultado é travado entre `min_hitrate: 5` e
  `max_hitrate: 100` (`battle.cpp:3289-3341`). Duas consequências que enganam
  juntas: **cem pontos cobrem a escala inteira**, de "nunca acerta" a "nunca
  erra" — não há meio-termo suave para calibrar; e **tudo que está 95 pontos
  abaixo parece igual**, porque o piso devolve 5% tanto para quem está a 10
  pontos quanto para quem está a 300. O `hit` de monstro é `nível + DEX + 150`
  (`status.cpp:2635`), o que dá 309 no Guardião Soldado e 422 no Arqueiro — os
  dois no piso contra jogador de guerra, com sintomas idênticos. Antes de somar
  precisão, **ler a Esquiva do alvo**: o número certo é `esquiva + a chance
  desejada`, e um bônus somado em monstros de bases diferentes espalha o
  resultado por toda a escala.

- **No `mob_db` do renewal, `Attack2` NÃO é o ATQ máximo — vira `rhw.matk`.**
  O parser (`mob.cpp:5107`) manda `Attack2` para `status.rhw.matk` sob
  `RENEWAL` e só cai em `rhw.atk2` no pre-renewal. Quem lê `Attack: 873,
  Attack2: 163` como "dano de 163 a 873" erra duas vezes: o mínimo e o máximo
  saem os dois do **`Attack`**, no `status_calc_misc`, como 80% e 120% dele
  (`status_base_atk_min`/`_max`, `status.cpp:2522`). Os dois campos são
  `uint16` — **teto de 65.535** para dano de monstro.

- **`guardian` sem índice é guardião TEMPORÁRIO, e é o que se quer fora de
  castelo com dono.** Com índice, ele ocupa um dos oito slots
  `CD_ENABLED_GUARDIAN` e passa a ser alcançado pelo `mob_guardian_guildchange`
  (`mob.cpp:3690`), que **apaga guardião de castelo sem dono** — o sumiço vem
  na primeira vez que alguém tocar na dona do castelo, e é calado. O preço do
  temporário é não ter respawn nem `guardianinfo`.

- **Curar MONSTRO funciona, e é o Emperium que não pode — não o monstro.** Vale
  o contrário da intuição de RO: o `SkillHeal::castendNoDamageId`
  (`src/map/skills/acolyte/heal.cpp`) chama `status_heal(bl, heal, 0, 0)` com o
  alvo que veio, monstro inclusive, e só zera a cura em três casos — alvo com
  `status_isimmune` (que só olha jogador, `status.cpp:9306`), o **Emperium**, e
  `Class: Battlefield`. O Santuário tem os mesmos três testes
  (`skill.cpp:6923`). **O que inverte o resultado é morto-vivo:** em alvo undead
  a cura vira dano ofensivo (`skill.cpp:4417`), então monstro de raça ou
  elemento morto-vivo **perde** HP. Quem for construir mecânica em cima disso
  escolhe um mob Neutro e sem raça — foi assim que a Anomalia Dimensional
  (2026-08-26) fez as Pedras Guardiãs sem uma linha de C++.
