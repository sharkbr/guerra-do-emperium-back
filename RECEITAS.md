# Receitas — os fluxos que se repetem

Passo a passo do que já foi feito mais de uma vez. Onde a **ordem importa**, está
dito por quê — quase toda inversão de ordem aqui falha **em silêncio**, relatando
sucesso.

Comandos rodam de `ferramentas/` com Python 2.7. Toda ferramenta que grava tem
`--verificar` (relata sem gravar) e faz backup antes. **Sempre rodar
`--verificar` primeiro.**

---

## 0. ONDE ISTO VAI PARAR? — a pergunta antes de qualquer entrega

**Terminar de editar não é terminar de entregar.** São quatro destinos, com
caminhos que não se cruzam, e escolher o errado falha **em silêncio**: aqui
funciona, e para o jogador não existe.

A pergunta que decide é **onde o arquivo mora**:

| o arquivo mora em… | vai por | como | quando o jogador recebe |
|---|---|---|---|
| `rathena/npc/`, `db/`, `conf/`, `src/` | **deploy** | `ferramentas/implanta.sh` | na hora — ninguém baixa nada |
| `C:\GuerraDoEmperium\cliente\` | **patch** | `monta_patch.py` + `publica_patch.sh` (§11) | na próxima vez que abrir o `Jogar.exe` |
| idem, mas mudou **muita** coisa | **base** | `monta_cliente.py` + `publica_cliente.sh` (§12) | só quem instalar do zero |
| `site/` | **deploy do site** | ver `site/LEIAME.md` | na hora, ao recarregar a página |

Três consequências que já custaram retrabalho:

- **`git commit` não entrega nada de cliente.** O `implanta.sh` leva servidor. Se
  o caminho do que você mexeu começa em `C:\GuerraDoEmperium\cliente\`, o
  trabalho não acabou no commit — é `CLAUDE.md` §4.18.
- **Item novo costuma ser as DUAS coisas.** O nome vive no `itemInfo.lua`
  (cliente → patch) e a entrega vive no `item_db` (servidor → deploy). Só uma
  metade e o item aparece **sem nome**, sem erro nenhum.
- **A base quase nunca precisa ser refeita.** Quem instala hoje recebe a base
  parada mais todos os patches desde então. Refazer é para quando o acúmulo
  ficar grande demais — e mesmo aí, se só a nossa parte mudou, são 134 MB
  (`--so nosso`), não 3,4 GB.

**Nada disso vale para o `Jogar.exe`**, que tem canal próprio: ele não consegue
se sobrescrever rodando. Ver `patcher/LEIAME.md` §3.

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

**E, se a linha for numa loja de Prontera, um oitavo passo:**

```
8. python zera_revenda_das_lojas.py            # põe o `Buy: 1` do item novo
   python zera_revenda_das_lojas.py --conferir # tem que dizer OK
```

Sem ele o item nasce com o `Buy` do `item_db` e passa a render `Buy/2` por
clique em qualquer NPC do mundo — **calado**: a loja sobe, vende, e o log não
reclama. Ver `CLAUDE.md` §4.16.

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

**E o slot não se acrescenta — se troca.** Este cliente ignora slot de manto
acima de **120**, e a tabela não muda isso (medido em tela em 2026-08-09, com a
tabela contígua até 158). Manto novo tem de **reaproveitar** um dos 40 slots
≤120 que não têm arte aqui. Sobram 28 — depois disso, só patch de exe
(`PENDENCIAS.md` §4). Vale para capa de **status** também, e não só para a
cosmética: quem manda o desenho é o `View`, não o slot de equipar.

```
1. python completa_iteminfo.py --id <lista>       # se o cliente não o conhece
2. python instala_manto.py --ids <lista>          # vai RECUSAR se o slot > 120
3. escolher um slot doador livre e pôr `View: <doador>` no
   db/guerra/item_db.yml   <- a FONTE DA VERDADE do de-para
4. python estende_robeid.py                       # lê o item_db, escreve a tabela
5. python instala_manto.py --ids <lista> --aplicar
6. python instala_manto.py --ids <lista>          # TEM QUE DAR 0 faltando
7. python instala_visual.py --id <lista> --grf "<grf do bRO>"
8. python valida_visual.py  --id <lista>          # TEM QUE DAR 0
9. reiniciar o map-server E fechar/reabrir o cliente
```

**Como achar um doador livre** (passo 3): é um slot ≤120 cuja pasta de arte não
existe neste cliente — hoje ele já não desenha nada, então reaproveitá-lo não
tira nada de ninguém. O `estende_robeid.py` **aborta** se o doador tiver arte,
passar de 120, ou se a pasta de destino não existir. Preferir os que nenhum item
do `item_db` cita.

**Por que 4 antes de 5:** o `instala_manto.py` só sabe em que **pasta** copiar
depois que a tabela conhece o slot. Invertido, ele recusa — alto, com o motivo
por extenso.

**Por que 7, se o 5 já copiou centenas de arquivos:** são camadas diferentes. O
`instala_manto.py` cuida só da subárvore de sprite de manto; os **4 arquivos de
item** (sprite de chão e os dois ícones) são do `instala_visual.py`, valem para
qualquer item, e a falta deles entrega caixa modal **ao abrir a loja**. Foi o
que faltou em 2 dos 11 mantos de 2026-08-09, e quem pegou foi o passo 8.

**Por que os DOIS reinícios no passo 9:** o `View:` é do servidor e o
`spriterobeid.lub` é do cliente. Reiniciar só um deixa as metades divergentes,
e a divergência não dá erro — o manto simplesmente desenha outra coisa, ou
nada.

**Como ler o resultado do passo 2:**

| resposta | o que fazer |
|---|---|
| `N arquivo(s) faltando` | seguir para o 5 — o slot já está resolvido |
| `view N ... so existe no spriterobeid do bRO` | fazer os passos **3 e 4** e voltar ao 2 |
| `view N ... nao existe em spriterobeid nenhum` | **parar.** Não há o que instalar |
| `nao e Costume_Garment` | é capa **de verdade** (`Garment`) — vai para o Capeiro, e a arte é a receita 2 normal |

**Duas coisas que parecem defeito e não são:**

- **Manto sem `View`** (a Aura Nevada, 480097) é `hateffect` — efeito de tela,
  não desenho vestido. O passo 2 recusa dizendo isso, e o item funciona.
- **`valida_visual.py` dando "4 de 4" com centenas de arquivos faltando no passo
  2** é o caso normal, não contradição: as duas perguntas são diferentes.

**E uma que é defeito, e engana:** se o passo 2 recusar um item **logo depois**
de o passo 4 ter rodado, a ferramenta está lendo o GRF em vez do disco. Não
deveria mais acontecer — foi corrigido em 2026-08-09 —, mas é o sintoma a
reconhecer: o `DataFolderFirst` faz `cliente\data\` vencer, e ferramenta que
consulta a tabela tem de consultar a que o **cliente** lê.

**E a que mais custou:** tabela certa, arte certa e arquivo lido pelo cliente
**não** provam que a peça desenha. As três se verificam offline, as três deram
OK, e o manto continuou invisível. Quem decide é uma marca na tela que não
dependa do efeito procurado — `estende_robeid.py --sonda`.

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
Esperado no mercado de equipamento e nas cartas. No mercado de **visuais** são
nove, e só nove — a lista dos IDs está no cabeçalho do
`mercado_de_visuais.txt`. Aviso com item fora dela é item novo com preço:
conferir quanto ele revende antes de deixar passar.

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

1. **Tirar `<mapa>.rsw` e `<mapa>.gat` do GRF.** Se o nosso responder *"arquivo
   com DES"* (640 dos 910 `.rsw` respondem), tirar **do GRF do bRO**, onde estão
   limpos — e então **provar que é a mesma revisão** antes de usar: `csize` e
   `rsize` iguais nos dois GRFs, mais o `.gat` do bRO célula a célula contra o
   `map_cache.dat` do nosso servidor. Ver `CUSTOMIZACAO-VISUAL.md`.
2. `python catalogo_mapa.py <mapa.rsw> <saida.md>` — ver o que há no mapa.
3. Conferir **o que cada modelo é de verdade** antes de usar: a tradução literal
   do nome coreano engana (um "pilar de madeira" na pasta de *vegetação* virou
   tora gigante deitada na cidade). A pasta categoriza melhor que o nome.
4. **Antes de plantar modelo novo, medir duas coisas.** A primeira é o que a
   Gravity fez com ele: varrer os `.rsw` do GRF do bRO pelo `filename` devolve
   escala e rotação dos mapas oficiais, e é a calibragem mais barata que
   existe. A segunda é a **largura do `.rsm` contra o tamanho do lugar** — e é
   ela que decide. A escala oficial vem do lugar de origem do modelo, que
   costuma ser maior: a fonte do Centro da Ordem entrou com a escala 1,0 de
   Glast Heim, ficou grande num pedestal de 4 células, e desceu para 0,57.
5. **Para centralizar num vão, conferir se ele tem largura par.** O
   `edita_mapa.py` posiciona por célula e `mundo()` devolve o **centro da
   célula** — então em vão de largura par (4 células, 6…) nenhum inteiro
   acerta o centro, que cai na fronteira. Usar célula fracionária
   (`179.5`). Erro de meia célula não salta aos olhos na planta e aparece
   na tela.
   **E achar o vão é o passo antes deste.** Ele nem sempre é relevo no `.gat`
   (o pedestal da fonte era): pode ser um **tapete**, que é chão pintado —
   e tapete não aparece no `.gat` nem no id de textura do `.gnd`, só nas
   **coordenadas UV** da superfície de topo, porque o `.bmp` do piso é um
   atlas. Desenhar as regiões de UV tile a tile antes de escolher a célula
   custa uma rodada e é o que evita centrar no nada. Ver `CLAUDE.md` §5.
6. Escrever a receita em `edita_mapa.py` (`RECEITA[<mapa>]`) e rodar
   `python edita_mapa.py <pasta-entrada> <pasta-saida> <data.grf> <mapa>` —
   **o `<data.grf>` aqui é o NOSSO**, é contra ele que os `filename` são
   conferidos. Para a temática de destruição inteira, `destroi_mapa.py`.
7. Copiar o `.rsw` gerado para `cliente\data\` — ele sombreia o GRF.
8. Reverter = apagar o arquivo solto.

**Versiona-se a RECEITA, não o `.rsw`.** O mapa gerado é artefato, e o cliente
está fora do git: **cliente novo perde o override, calado**. Quem depende de um
modelo plantado escreve isso no cabeçalho do arquivo que depende dele.

**O `.gat` (colisão) não é tocado** pelo override de `.rsw`: o cenário muda, o
chão andável não. Um NPC pode acabar nascendo dentro de um escombro — e um
modelo pode ser plantado em célula não-andável de propósito, que é o caso comum
para peça decorativa no meio de uma sala.

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

## 11. Entregar uma mudança de CLIENTE aos jogadores (patch)

**Mudança de servidor** (NPC, `db/`, `conf/`, `src/`) chega pelo deploy —
`ferramentas/implanta.sh`, e ninguém baixa nada. **Mudança de cliente** (`data\`,
`itemInfo.lua`, sprite, `.lub`, exe, `AI_sakray\`) só chega pelo patch: o
cliente do jogador é uma cópia congelada do dia em que ele baixou.

A regra que evita retrabalho: **testar em jogo primeiro, montar o patch
depois.** O número de um patch nunca se reaproveita, então patch errado se
corrige com patch novo por cima.

1. Fazer e testar a mudança no cliente desta máquina, como sempre.
2. Montar o patch com os caminhos **relativos à raiz do cliente**:

   ```
   python ferramentas/monta_patch.py --nome "IA do homunculo" AI_sakray
   python ferramentas/monta_patch.py --nome "Arte da Ordem" data/sprite/...
   ```

   Sai a lista do que entrou no zip. **É aqui que se percebe engano** — o
   `--desde 2026-08-14`, que varre o cliente por data, costuma trazer junto o
   que foi tocado por acidente.
3. `ferramentas/publica_patch.sh` — envia os zips e, **por último**, a lista.
4. `git add patcher/patches.txt` e commitar: o registro é a fonte da
   `lista.txt` que o servidor serve.

O jogador não faz nada: o `Jogar.exe`, que é o que ele clica para jogar,
aplica sozinho na próxima abertura.

**Para apagar arquivo do cliente do jogador:** `--apagar data/algum.lub`.

**O Atualizador não vai por patch.** Ele não consegue se sobrescrever enquanto
roda; tem canal próprio. Detalhes em `patcher/LEIAME.md`, e a receita é a §11b
logo abaixo — que são **dois** lugares, não um.

---

## 11b. Publicar um `Jogar.exe` novo (o Atualizador)

**São dois destinos, e um só não basta** — a diferença é com quem cada um fala:

| destino | alcança | se faltar |
|---|---|---|
| canal de auto-atualização | quem **já instalou** | jogador antigo fica na versão velha |
| bucket / CDN | quem vai **baixar do site** | jogador novo baixa o exe com o defeito |

Publicar só o canal conserta exatamente quem não precisava do conserto: quem
está com problema de *instalação* não tem instalação nossa, logo nunca passa
pelo canal.

1. Subir o `const VERSAO` em `patcher/main.go`. É ele que o canal compara.
2. **O canal** — o script recompila antes de enviar, então não há como publicar
   binário velho por engano:

   ```bash
   export PATH="/c/Program Files/Go/bin:$PATH"
   ferramentas/publica_patch.sh --atualizador
   ```

3. **O bucket**, de onde o site serve o botão Baixar
   (`SITE_DOWNLOAD_URL = https://cdn.filiponegrao.com.br/Jogar.exe`):

   ```bash
   set -a; . /c/GuerraDoEmperium/spaces.env; set +a
   export RCLONE_CONFIG="" RCLONE_CONFIG_SPACES_TYPE=s3 \
          RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean \
          RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" \
          RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET" \
          RCLONE_CONFIG_SPACES_ENDPOINT="$SPACES_REGIAO.digitaloceanspaces.com" \
          RCLONE_CONFIG_SPACES_ACL=public-read \
          RCLONE_CONFIG_SPACES_NO_CHECK_BUCKET=true
   /c/GuerraDoEmperium/bin/rclone.exe copyto patcher/Jogar.exe \
       "spaces:$SPACES_BUCKET/Jogar.exe"
   ```

   O `public-read` e o `NO_CHECK_BUCKET` não são enfeite: sem o primeiro o
   download dá 403, e sem o segundo o rclone tenta `CreateBucket` e leva 403
   antes de subir um byte (`CLAUDE.md` §5).

4. **Conferir que os dois ficaram de acordo**, comparando o sha256 dos três:

   ```bash
   curl -s https://libraro.filiponegrao.com.br/patch/patcher.txt   # o do canal
   curl -sL https://cdn.filiponegrao.com.br/Jogar.exe | sha256sum  # o do CDN
   sha256sum patcher/Jogar.exe                                     # o local
   ```

   Divergência aí é um canal servindo uma versão e o outro servindo outra — e
   nada mais no caminho olha para isso.
5. `git add patcher/main.go` e commitar.

**O que nenhuma sonda responde** é se o exe faz na tela o que se espera. Toda
publicação de Atualizador termina com um teste manual, e ele vale mais que os
quatro passos acima.

---

## 12. Refazer o PRIMEIRO DOWNLOAD (a base do cliente)

Isto é o irmão da §11, e a diferença é o público: o patch fala com quem já tem
o cliente, a base fala com quem não tem nada. São 3,4 GB e vão para o bucket
(`cdn.filiponegrao.com.br`), não para o droplet.

**Na maioria das vezes você NÃO precisa disto.** Quem instala hoje recebe a base
desta versão mais todos os patches publicados desde então, na primeira abertura.
A base só se refaz quando o acúmulo de patches ficar grande a ponto de a
primeira abertura demorar demais — ou quando algo entrar no cliente que não dá
para entregar por patch.

```bash
# 1. o cliente desta máquina já está como se quer, testado em jogo
python ferramentas/monta_cliente.py            # ~10 min: sha de 3 GB + compressão
python ferramentas/monta_cliente.py --confere  # o registro descreve o que há em disco?

# 2. publica: os pedaços primeiro, a base.txt por último
ferramentas/publica_cliente.sh

# 3. commita o registro
git add patcher/base.txt && git commit
```

**Só a nossa parte mudou?** `--so nosso` remonta apenas os pedaços `nosso-*` e
mantém os outros três — e o publicador pula o que já está no bucket com o mesmo
nome. Na prática são **134 MB** em vez de 3,4 GB, porque o `data.grf` e as
músicas não mudam nunca.

**Conferir sem publicar:** `ferramentas/publica_cliente.sh --confere` mostra o
registro, o que já está no bucket e se o CDN responde.

### O que quebra se for feito errado

- **A ordem.** Os pedaços sobem antes da `base.txt`. Na ordem inversa, quem
  abrisse o instalador naquele intervalo pediria arquivo que ainda não existe.
- **Trocar pedaço sem trocar o número.** Os zips têm o número no nome, então
  isso não acontece com eles. O `data.grf` é a exceção: nome fixo, e o CDN tem
  cache — substituí-lo exige **purgar o cache** no painel do Spaces.
- **Chave sem escrita.** O publicador morre com o erro do rclone na tela; ver
  `CLAUDE.md` §5.

### Testar o instalador antes de anunciar

Pasta nova e vazia, `Jogar.exe` dentro, abrir. Ele detecta que não há cliente
(procura o `data.grf`), pergunta onde instalar e baixa. **Fechar e reabrir no
meio** é o teste que importa: tem de retomar de onde parou.

E **conferir o atalho** — se o "Iniciar em" não for a pasta do jogo, o cliente
abre sem `data\`, sem `System\` e sem nada do que é nosso, sem erro nenhum.
