# Receitas — os fluxos que se repetem

Passo a passo do que já foi feito mais de uma vez. Onde a **ordem importa**, está
dito por quê — quase toda inversão de ordem aqui falha **em silêncio**, relatando
sucesso.

Comandos rodam de `ferramentas/` com Python 2.7. Toda ferramenta que grava tem
`--verificar` (relata sem gravar) e faz backup antes. **Sempre rodar
`--verificar` primeiro.**

---

## 1. NPC novo

1. Escrever `rathena/npc/guerra/<nome>.txt`, com **cabeçalho explicando o porquê**
   das decisões (é o padrão do projeto e o que torna o resto navegável).
2. Acrescentar `npc: npc/guerra/<nome>.txt` em `npc/guerra/scripts_guerra.conf`,
   **com o parágrafo** dizendo o que faz, onde fica e o que quebra se desligado.
3. `@reloadscript` in-game.
4. Testar. Erro de parse aparece na janela do map-server.

**Nunca editar o arquivo do rAthena para mover/renomear/desligar um NPC dele.**
A receita é `disablenpc` no original + duplicata nossa na coordenada nova.
Exemplos prontos: `armazem_do_cla.txt` (move e renomeia), `portais_do_navio.txt`
(fecha), `arena_de_combate.txt` (substitui).

**Duas armadilhas conhecidas:**
- `disablenpc` no original **não desliga duplicatas já nascidas** (as outras
  quatro guias de Prontera continuaram guiando).
- `duplicate()` traz junto o `savepoint` do original — foi por isso que a Kafra
  da praça é cópia, não duplicata.

## 2. Item novo com arte (a ordem que erra calado)

```
1. python completa_iteminfo.py --verificar          # o que o bRO tem
2. python completa_iteminfo.py                      # grava nome/descrição/recurso
3. python valida_visual.py  --id <lista>            # o que falta de arte
4. python estende_accessoryid.py --id <lista> --grf "<grf do bRO>"
5. python instala_visual.py --id <lista> --grf "<grf do bRO>"
6. python valida_visual.py  --id <lista>            # TEM QUE DAR 0
7. fechar e reabrir o cliente
```

Mais a entrada em `db/guerra/item_db.yml` (à mão) e a linha na loja.

**Por que a ordem:**
- **1-2 antes de 3-5** — o validador lê o `identifiedResourceName` do
  `itemInfo.lua`. Sem entrada ele nem sabe que arquivo procurar e responde "não
  está no itemInfo.lua", que **parece** "não tem arte" e não é.
- **4 antes de 5** — `instala_visual.py` só sabe procurar as 4 sprites de cabeça
  depois que o `accessoryid` lhe diz o sufixo. Na ordem errada ele instala os 4
  ícones, relata **"faltando 0"**, e o chapéu continua invisível. O passo 4 só é
  necessário quando o passo 3 acusar `view N no accessoryid`.
- **6 antes de 7** — conferir no disco custa segundos; descobrir no jogo custa
  reabrir o cliente.

**A armadilha grande:** a pasta da arte no disco **não** tem o nome coreano que
se espera. Ver `ferramentas/LEIAME.md`, seção `instala_visual.py`.

## 2b. Manto cosmético novo (`Costume_Garment`)

O `valida_visual.py` **não serve sozinho aqui**, e é o ponto inteiro desta
receita: para manto ele confere só os 4 arquivos de item, e responder "4 de 4"
não diz nada sobre a arte de manto. Item aprovado por ele pode abrir a loja,
vender, equipar — e só então dar `Cannot find File`.

```
1. python varre_cosmeticos.py --listar manto        # tem de dizer `ok`
2. python instala_manto.py --ids <lista>            # o que falta de manto
3. python instala_manto.py --ids <lista> --aplicar
4. python instala_manto.py --ids <lista>            # TEM QUE DAR 0 faltando
5. fechar e reabrir o cliente
```

**Como ler o resultado do passo 1:**

| resposta | o que fazer |
|---|---|
| `ok` | seguir — o `View` está na nossa `spriterobeid.lub`. Falta só a arte |
| `view N de manto so existe no robe do bRO` | **parar.** Falta a ferramenta que estende a tabela — `PENDENCIAS.md` §4 |
| `view N de manto nao existe em robe nenhum` | **parar.** Não há o que instalar |

**Duas coisas que parecem defeito e não são:**

- **Manto sem `View`** (a Aura Nevada, 480097) é `hateffect` — efeito de tela,
  não desenho vestido. O passo 2 recusa dizendo isso, e o item funciona.
- **`ok` no passo 1 com centenas de arquivos faltando no passo 2** é o caso
  normal, não contradição: as duas perguntas são diferentes.

Depois disso, a receita 3 normalmente.

## 3. Item novo numa loja existente

1. Conferir se o item **desenha**: `python valida_visual.py --id <id>`. Se não
   der 0, fazer a receita 2 antes — ou a **2b**, se for `Costume_Garment`.
   **Item sem arte entrega caixa de erro ao jogador.**
2. Conferir se o nome está em **português** — só entra na loja quem está
   (`estado_item.py --id <id>`).
3. Acrescentar a linha no `npc/guerra/mercado_*.txt`.
4. `@reloadscript`.

**`mercado_de_cartas.txt` é GERADO** por `varre_cartas.py` — atualizar é rodar o
script de novo, não editar à mão.

**O aviso `npc_parse_shop: Item X discounted buying price` na subida não é erro:**
é o servidor apontando que preço 1 zeny permite comprar e revender com lucro.
Esperado no mercado de equipamento e nas cartas; **não** esperado no mercado de
visuais — se aparecer lá, item novo entrou com preço, conferir.

**Teto do parser:** a lista de itens de um `shop` não cabe nos 2048 bytes do
`char w4[2048]`. A loja de cartas de arma resolve carregando 256 na linha do
`shop` e o resto por `npcshopadditem` no `OnInit`.

## 4. Traduzir diálogo de NPC do rAthena

```
python traduz_npcs.py --extrair <grupo>      # gera/atualiza o catálogo
python traduz_npcs.py --preencher            # aplica o glossário
python traduz_npcs.py --aplicar <grupo>      # escreve nos arquivos do rAthena
python traduz_npcs.py --estado               # quanto já foi traduzido
```

O catálogo (`npc/guerra/traducao/<grupo>.cat`) é a **fonte**; o `.txt` do rAthena
é o **resultado**. Editar o `.txt` à mão é perder o trabalho na próxima passada.
A unidade de trabalho é o **texto**, não a ocorrência.

Grupos: `campal`, `cidades`, `classe1`, `classe2`, `glossario`, `guerra`,
`kafra`, `novico`, `pvp`, `servico`.

**`--extrair` num grupo já aplicado apagava o catálogo** — corrigido em
2026-08-04, mas vale conferir o `git status` depois de extrair.

## 5. Mudar taxa ou regra de jogo

1. Editar `rathena/conf/guerra/battle_guerra.txt`.
2. `@reloadbattleconf`.
3. Conferir com `@rates` — que imprime o que está **carregado em memória**.

**Não medir matando monstro**: a penalidade por diferença de nível distorce o
ganho. EXP vale na hora; **drop não** — fica gravado em cada entrada do mob db na
carga, e precisa de `mob_reload()` (que o `@reloadbattleconf` chama sozinho ao
perceber que uma taxa de item mudou).

Hoje: exp 10x (base e classe), drop 50x em todas as categorias, sem exceção.

## 6. Mudar a aparência de um mapa

1. `python catalogo_mapa.py <mapa.rsw> <saida.md>` — ver o que há no mapa.
2. Conferir **o que cada modelo é de verdade** antes de usar: a tradução literal
   do nome coreano engana (um "pilar de madeira" na pasta de *vegetação* virou
   tora gigante deitada na cidade). A pasta categoriza melhor que o nome.
3. `python destroi_mapa.py <pasta-entrada> <pasta-saida> [mapa]` ou
   `edita_mapa.py` para trocas pontuais.
4. Copiar o `.rsw` gerado para `cliente\data\` — ele sombreia o GRF.
5. Reverter = apagar o arquivo solto.

**O `.gat` (colisão) não é tocado** pelo override de `.rsw`: o cenário muda, o
chão andável não. Um NPC pode acabar nascendo dentro de um escombro.

## 7. Código C++ novo

1. Escrever em `rathena/src/custom/`.
2. Se precisar de gancho em `src/map/`, **comentar a alteração no arquivo** e
   registrar na tabela de enxertos do `CLAUDE.md`.
3. Comando de script novo: `src/custom/script.inc` + `src/custom/script_def.inc`.
   Comando `@`: `atcommand.inc` + `atcommand_def.inc`.
4. Recompilar (VS 2022 Community).

**`rathena/.gitignore` tem `!/src/custom/`** porque o upstream ignora a pasta
inteira. Sem essa linha, arquivo novo lá some calado no próximo clone — e
`.gitignore` não afeta arquivo já rastreado, então os `.inc` que vieram do
upstream não denunciavam o problema.

## 8. "Mudei e não pegou" — diagnóstico

Antes de investigar, conferir nesta ordem:

1. **Usei o recarregador certo?** Tabela no `CLAUDE.md` §3. Mudança de cliente
   exige **fechar e reabrir**; `reputation.yml` exige **reiniciar o map-server**.
2. **Os quatro servidores estão no ar?** `python ferramentas/servidor.py status`.
   O web-server fora derruba emblema de clã **sem nenhum sintoma**.
3. **É o cliente que decide isso?** Nome, descrição, ícone e arte vêm do cliente,
   não do `item_db.yml`.
4. **Estou testando na conta de teste?** Grupo 99 ignora `NoDrop` e as outras seis
   travas — teste de restrição nela sempre dá falso negativo.
5. **O arquivo está em cp1252?** UTF-8 em texto de jogo quebra.
6. **A ferramenta relatou sucesso mas nada mudou?** Ver as armadilhas de ambiente
   no `CLAUDE.md` §5 — várias falham **caladas** e produzem diagnóstico falso.

## 9. Antes de teletransportar para um mapa

**Conferir se o `.rsw` existe no GRF do cliente.** Mapa que o rAthena conhece mas
o GRF de 2021 não tem **derruba o cliente e prende o personagem lá** — na volta,
ele reconecta no mapa quebrado e cai de novo.

Foi por isso que o campo de treino usa `tra_fild` (o antigo) e não
`tra_fild01/02/03`.

## 10. Mexer no Logue e Ganhe (prêmio, ou renovar os ciclos)

**Nunca editar `db/guerra/attendance.yml` nem `CheckAttendance.lub` à mão.** Os
dois carregam a MESMA tabela de prêmios em formatos diferentes, e divergir os
dois **não dá erro**: a janela promete um item e o RoDEX entrega outro.

1. Editar a receita no topo de `ferramentas/monta_logue_e_ganhe.py` —
   `ITEM`, `PREMIOS` (vinte valores, e vinte é o teto do cliente), `PRIMEIRO`,
   `ULTIMO`.
2. `python ferramentas/monta_logue_e_ganhe.py --verificar` — diz o que mudaria.
3. `python ferramentas/monta_logue_e_ganhe.py` — grava os dois lados, faz backup
   do `.lub` e confere com o `luac -p`. Idempotente.
4. `@reloadattendancedb` no jogo (ou reiniciar o map-server).
5. **Fechar e reabrir o cliente.** O `.lub` só é lido na inicialização — sem
   isso a janela continua mostrando a tabela velha, sem avisar.

**Ciclo já vencido some calado.** Quando o `ULTIMO` passar, não há janela e não
há erro. Adiantar antes: hoje o último é 2027-12-31.
