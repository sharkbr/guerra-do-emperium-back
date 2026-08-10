# Guerra do Emperium — guia de trabalho

Servidor privado de Ragnarok Online: rAthena vendorizado + cliente kRO
2021-11-03 traduzido para PT-BR. **A v1 está de pé** — dá para logar e jogar.

Este arquivo é o ponto de partida de toda sessão. Ele não conta história: diz
onde as coisas estão, o que não se pode fazer, e **qual documento ler** para a
tarefa em mãos. O histórico e o "por quê" de cada decisão vivem nos diários
(`PENDENCIAS.md`, `ferramentas/LEIAME.md`) — grandes de propósito, e a serem
lidos **por seção**, nunca inteiros.

---

## 1. O mapa — onde fica o quê

| O que | Onde | Versionado |
|---|---|---|
| Emulador (terceiros) | `rathena/` | sim |
| **Nossos NPCs** | `rathena/npc/guerra/` | sim |
| **Nossos itens/mobs/reputação** | `rathena/db/guerra/` | sim |
| **Nosso C++** | `rathena/src/custom/` | sim |
| **Nossa regra de jogo** (taxas) | `rathena/conf/guerra/` | sim |
| Config de máquina (senha, IP) | `rathena/conf/import/` | **não** |
| Ferramentas (Python 2.7) | `ferramentas/` | sim |
| **Cliente** | `C:\GuerraDoEmperium\cliente\` | **não** |
| Override do cliente | `C:\GuerraDoEmperium\cliente\data\` | **não** |

**O cliente inteiro está fora do git.** Toda alteração nele (arte, `itemInfo.lua`,
`.lub`, `.bson`, mapas) é irreproduzível a partir do repositório — só existe nesta
máquina. Fazer backup antes de sobrescrever, sempre.

## 2. A lei da customização

**Tudo que é nosso mora em pasta própria; tocamos arquivo do rAthena só para
apontar para ela.**

O `rathena/` foi vendorizado **sem o histórico do upstream**. Customização
espalhada fica indistinguível de código de terceiros num `git diff`, e trazer
correção do rAthena vira arqueologia.

Os únicos enxertos permitidos em arquivo do rAthena, e os que existem hoje:

| Arquivo do rAthena | Enxerto |
|---|---|
| `npc/scripts_custom.conf` | uma linha `import: npc/guerra/scripts_guerra.conf` |
| `npc/barters.yml` | um `- Path: npc/guerra/barters_guerra.yml` no rodapé |
| `conf/battle_athena.conf` | uma linha `import: conf/guerra/battle_guerra.txt` |
| `db/re/item_db.yml`, `db/item_combos.yml`, `db/re/mob_db.yml`, `db/re/reputation.yml`, `db/re/reputation_group.yml`, `db/attendance.yml`, `db/refine.yml` | um `- Path: db/guerra/...` no rodapé de cada |
| `db/re/quest_db.yml` | o **`Footer: Imports:` inteiro** — aquele arquivo não tinha rodapé nenhum. Seguro porque o `parseImports` mora no `YamlDatabase` (`src/common/database.cpp:176`), não no leitor de quest: vale para todo banco em YAML, e o mesmo caminho serve para qualquer `db/re/*.yml` que ainda não tenha rodapé |
| `src/map/clif.cpp` | dois includes de `src/custom/` + três chamadas (`placa_de_venda_mostra`, e o teto de refino nas duas pontas da janela de refino), comentadas no arquivo |
| `src/map/battle.cpp` | um include de `src/custom/` + **duas** chamadas, comentadas no arquivo: `reducao_alcanca_percentatk` (no bloco "Card Fix for target" — põe o `percentAtk` na redução, sem ela `bonus bAtkRate` fura toda resistência) e `reducao_piso` (dentro do `APPLY_CARDFIX` — teto de 99,9%, no lugar do `max(0, …)` que deixa a redução zerar o dano). Ver `REDUCAO-DE-DANO.md` |
| `rathena/.gitignore` | `!/src/custom/` — o upstream ignora essa pasta inteira |

**Qualquer outro diff em `rathena/` fora de `npc/guerra`, `db/guerra`,
`src/custom`, `conf/guerra` é alteração em código de terceiros e precisa de
justificativa.** A receita para não editar arquivo do rAthena é sempre a mesma:
`disablenpc` no original + duplicata nossa (ver `portais_do_navio.txt`,
`armazem_do_cla.txt`, `arena_de_combate.txt`).

**`rathena/npc/guerra/scripts_guerra.conf` é o índice narrado dos nossos NPCs** —
cada linha vem com um parágrafo dizendo o que o NPC faz, onde fica e o que quebra
se for desligado. **Leia esse arquivo antes de mexer em qualquer conteúdo de
jogo**; ele responde a maioria das perguntas de "o que já existe?" sozinho.
Ligar/desligar um NPC = comentar uma linha ali.

## 3. Rodar o servidor

```
python ferramentas/servidor.py status      # o que está no ar E o que quebra sem cada peça
python ferramentas/servidor.py subir       # idempotente, na ordem certa
python ferramentas/servidor.py reiniciar
```

**São QUATRO servidores**, não três: `login` (6900), `char` (6121), `map` (5121)
e **`web` (8888)** — com PACKETVER > 20200300 é o web-server que recebe o emblema
de clã por HTTP, e sem ele a falha é **completamente calada**. Mais MariaDB (3306).
Nunca subir os `.bat` um a um.

Erro de script de NPC aparece na janela do map-server e em `log/map-msg_log.log`
(config não versionada — some em clone limpo).

### Qual recarregador para qual mudança

Errar o comando faz a mudança parecer que não pegou.

| Mudou | Comando |
|---|---|
| Script de NPC | `@reloadscript` |
| `db/` (item, conjunto) | `@reloaditemdb` — pega item **e** conjunto |
| `npc/guerra/barters_guerra.yml` (loja de troca) | `@reloadbarterdb` — **não** é `@reloadscript` |
| `conf/guerra/`, `battle_athena.conf` | `@reloadbattleconf` (chama `mob_reload()` sozinho se taxa de item mudou) |
| `db/guerra/reputation.yml` | **reiniciar o map-server** — `reputation_db.load()` só roda no `do_init_pc` |
| `db/guerra/refine.yml` | **reiniciar o map-server** — não existe `@reloadrefinedb` |
| `db/guerra/attendance.yml` | `@reloadattendancedb` — mas o cliente **não** recarrega a metade dele |
| `db/guerra/quest_db.yml` (missões da Ordem) | `@reloadquestdb` — e **não** é `@reloadscript`. O recado e a recompensa de cada missão moram no NPC, o alvo mora aqui; mudar os dois exige os dois comandos. **Missão nova exige também `ferramentas/monta_missoes_da_ordem.py` e reabrir o cliente** — sem a entrada de lá, pegar a missão derruba o cliente (§5) |
| `src/` | recompilar (VS 2022 Community, já instalado) |
| `itemInfo.lua` e afins no cliente | **fechar e reabrir o cliente** — só lido na inicialização |
| Exe do cliente (fonte, charset) | **fechar o cliente ANTES de gravar** — o exe fica travado enquanto roda, e o que já está aberto segue na cópia em memória |

Na dúvida, reiniciar o map-server resolve tudo do lado servidor; login e char
podem ficar de pé. **Derrubar o servidor por causa de `db/` é desnecessário.**

`@rates` in-game imprime as taxas carregadas em memória. "Unknown Command" **não**
é falta de permissão.

## 4. Regras que não se negociam

1. **Texto de jogo é cp1252, nunca UTF-8.** Acento sim; UTF-8 quebra. Quem faz o
   cliente desenhar byte acentuado é o patch `AlwaysAscii`. Vale para `.txt` de
   NPC, `itemInfo.lua` (ANSI/CP949), `.lub`, **e o `db/guerra/item_db.yml`**.
   Estes `.md` são UTF-8 — a regra é para texto que o **jogo** lê.
   **Escrever é o passo perigoso, não ler:** editor e ferramenta de edição
   gravam UTF-8 por padrão, e o estrago é calado. Depois de gerar um desses
   arquivos, converter e conferir — `python -c "open(p,'wb').write(open(p,'rb')
   .read().decode('utf-8').encode('cp1252'))"`, e então reler em cp1252 para
   ver os acentos certos. Ver §5, entrada do U+FFFD.
2. **Só entra na loja item com nome em português.** Inglês se detecta pela
   ausência no bRO; coreano por byte. Um critério não serve para o outro.
3. **Quando falta algo, traz-se do bRO** — a instalação do Ragnarok Brazil desta
   máquina é a fonte de arte, nome PT e descrição. Não inventar.
4. **Validar arte antes de pôr item na loja.** Item sem arte entrega caixa de erro
   ao jogador. `valida_visual.py` tem que dar 0.
5. **Mesclar por chave, nunca trocar o arquivo do bRO por cima** — vale para toda
   a tradução.
6. **Conferir se o mapa existe no GRF antes de teletransportar.** Mapa do rAthena
   pós-2021 sem `.rsw` no GRF derruba o cliente **e prende o personagem lá**.
7. **A conta de teste (grupo 99) ignora `NoDrop` e as outras seis travas** —
   testar restrição de item nela sempre dá falso negativo.
8. **`grep` em `npc/` não prova que um item é inútil** — a UI do cliente consome
   item direto no C++, por tabela em `db/` (ex.: cupom de estilista,
   `db/re/stylist.yml`).
9. **Sistema de UI do cliente tem metade da configuração NO CLIENTE.** O
   servidor manda o estado (um contador, um índice), não a lista. Mexer só no
   `db/` deixa as duas metades divergentes, e a divergência **não dá erro** — a
   janela mostra uma coisa e o servidor entrega outra. Caso vivo: o Logue e
   Ganhe (`db/guerra/attendance.yml` + `cliente\System\CheckAttendance.lub`),
   por isso gerado dos dois lados por `ferramentas/monta_logue_e_ganhe.py`.
   **Segundo caso vivo: o nome do item na janela de troca (barter).** O pacote
   leva só o ID (`clif.cpp:23225`) — quem desenha o nome é o `itemInfo.lua` do
   cliente. Menu de `select` usa `getitemname()` e lê o servidor; janela nativa,
   não. Nome errado numa loja de troca **não** se conserta com o
   `nomes_pt_item_db.py`.
   **Terceiro caso vivo, e o único que NÃO falha calado: a janela de
   missões.** Quest que o cliente não conhece **derruba o cliente**, não
   aparece sem título — ver §5. As missões da Ordem são geradas dos dois
   lados por `ferramentas/monta_missoes_da_ordem.py`.
10. **Loja que cobra em ITEM é `barter`, não `itemshop`.** São os dois tipos que
    parecem servir, e só um funciona aqui: o `itemshop` passa a moeda por
    `pc_can_sell_item`, que **recusa item `NoSell`** enquanto
    `allow_bound_sell` for `0x0` (o nosso padrão) — a loja abre e a compra
    falha, com a moeda na mão do jogador. O `barter` não faz essa checagem. Só
    ele abre a janela de troca com ícone de moeda por linha; `itemshop` e
    `pointshop` caem no `clif_cashshop_show`, que é outra janela.
11. **Menu de `select` e tabela de dados indexados pelo mesmo número saem da
    MESMA fonte.** Se o menu é uma string escrita à mão e o destino é um
    `setarray` escrito à parte, as duas ordens divergem mais cedo ou mais
    tarde — e a divergência **não dá erro**: o NPC funciona, cobra, entrega, e
    entrega a coisa errada. O certo é guardar os rótulos num array e **montar
    o menu num laço** a partir dele, mais um `getarraysize` que compare as
    colunas e grite com `debugmes`. Caso vivo, e caro: em 2026-08-08 o
    Teleportador da Ordem levou ao lugar errado nos **catorze** destinos —
    "Batalha dos Orcs" ia para a Vila dos Porings — porque o menu seguia a
    ordem das placas e os arrays seguiam a ordem em que os mapas tinham sido
    validados. **O cabeçalho do arquivo afirmava que as duas ordens eram a
    mesma. Comentário não é trava.**
12. **Ao traduzir diálogo, nome de habilidade, item, mapa e monstro sai da
    tabela que o JOGO lê — inclusive quando ela não traduziu.** As quatro
    fontes: `skillinfolist.lub` (habilidade), `itemInfo.lua` do nosso cliente
    (item), `data\mapnametable.txt` (mapa) e `db/guerra/mob_db.yml` (monstro,
    gerado do `navi_mob_br.lub` do bRO). A regra vale **nos dois sentidos**:
    `Mind Blaster` fica em inglês na Torre do Demônio porque é assim que o
    cliente o mostra, e `Explosive Powder` vira **Pó Explosivo** e não
    "Pólvora" porque é assim que o `itemInfo.lua` chama o item 6213. Nome que
    não está em tabela nenhuma **fica em inglês** — inventar nome de lugar é
    o que a regra 3 proíbe (caso vivo: `Ash Vacuum`).

    Duas consequências que já custaram retrabalho:
    - **Nome de criatura se traduz**, mesmo que o bicho apareça em inglês na
      tela. Dentro de instância o nome que flutua vem do 4º argumento do
      `monster` do próprio script, que **não** entra no catálogo — então a
      missão em português convive com um alvo rotulado em inglês. Aceita-se:
      meia frase em inglês é pior, e é o que a regra de "só aplicar grupo
      inteiro" existe para evitar.
    - **Linha `+` vazia num `.cat` não é dívida.** Nome de mapa, label de
      evento, nome único de NPC, `.bmp` de cutin, código de cor e pontuação
      solta ficam em branco de propósito. O `--estado` conta esses como não
      feitos, então **86% num grupo de instância quer dizer completo**.
13. **Rodar `--extrair` ANTES de traduzir um grupo, sempre — mesmo com
    catálogo commitado.** Catálogo velho abre, tem conteúdo, aplica sem recusa
    e marca 100%; o que falta nele simplesmente não existe para a ferramenta.
    Em 2026-08-09 onze dos dezesseis catálogos de instância estavam sem os
    `mapannounce`/`unittalk` (o `vermes` tinha 331 pares onde havia 453), e
    quatro grupos foram dados por prontos antes de o buraco aparecer.
14. **Em que loja um item entra é decidido pelo `Locations:` do `item_db`,
    nunca pelo nome nem pela lista em que ele foi pedido.** As doze lojas do
    quarteirão de Prontera são pares: uma de VISUAL e uma de EQUIPAMENTO por
    slot — Manteleiro/Capeiro (capa), Adereceiro/Ocleiro (cabeça meio), e
    assim por diante. `Costume_Garment` vai para a de visual, a 1 zeny;
    `Garment` com Defense, peso e refino vai para a de equipamento. Um pedido
    que diga "Capa" pode querer as duas, e em 2026-08-09 queria: onze
    cosméticos e três capas com cova, na mesma lista. **Ler a lista e não o
    `Locations:` põe equipamento de status numa vitrine de 1 zeny.**

    O `estado_item.py --id <n>` responde isso numa linha, e a resposta pode
    contrariar o nome. Os dois casos vivos, os dois na fileira de visual:
    a **Piscadela de Freya** é de meio e o nosso rAthena a dava como baixo
    (2026-08-07, custou um override no `item_db`); a **Máscara de Minorous**
    é `Costume_Head_Low`/`_Mid` e foi pedida na lista de topo (2026-08-09,
    não custou nada — o `Locations:` já estava certo, faltava lê-lo). As
    duas acabaram no Adereceiro.

    **Divergência entre o pedido e o `item_db` é para levantar na entrega,
    não para resolver sozinho.** Escrever no comentário da loja e dizer ao
    dono; a Minorous foi entregue como pedida, com a ressalva por escrito, e
    a mudança de loja veio dele na volta. O que não pode é a divergência
    ficar só na cabeça de quem editou.

## 5. Armadilhas deste ambiente

Produziram diagnóstico falso e custaram retrabalho:

- **`strings` não existe** no Git Bash daqui — com `2>/dev/null` falha calado e
  parece "zero resultados".
- **`[Text.Encoding]::Latin1` não existe** no PowerShell 5.1 → devolve `$null` e
  todo resultado derivado é lixo. Usar `GetEncoding(28591)`.
- **`Get-ChildItem -Include`** sem curinga no caminho retorna vazio.
- **Arquivo cp1252 salvo como UTF-8 vira `\xef\xbf\xbd` (U+FFFD) e o acento se
  perde para sempre.** Não é mojibake reversível: o byte original já não está
  lá. Achado em 2026-08-07 no `db/guerra/item_db.yml` — 4 acentos de "Maçã da
  Inocência" e "Diadema do Paraíso" tinham virado isso, e ninguém percebeu
  porque o nome que o jogador lê vem do `itemInfo.lua`, não do servidor.
  O teste, em qualquer arquivo que o jogo leia:
  `python -c "d=open(p,'rb').read(); print '\xef\xbf\xbd' in d"`.
- **`.lub` do GRF é bytecode** (header `\x1bLua`); os do ROenglishRE são texto
  puro. Comparar tamanho entre os dois não significa nada.
- **`Tools\luac.exe -p` do ROenglishRE é o único jeito de provar que um `.lub`
  gerado compila.**
- **Patch de exe "aplicado e confirmado" NÃO é patch com efeito — e script que
  confere o próprio trabalho não prova nada.** O `ajusta_tamanho_fonte.py`
  desviava 8 chamadas, respondia *"8 ja desviadas"* no `--verificar` e era
  **inócuo**: procurava o formato do próprio stub, não o resultado na tela.
  Subir o número (2 → 4 → 6) só gastou rodadas. **Antes de calibrar valor,
  provar que o patch chega à tela com uma marca que não dependa do efeito
  procurado** — sublinhado, negrito, outra face de fonte. Responde numa rodada
  o que tentativa e erro não responde em cinco. Duas medições que enganam junto:
  contar call site só por `ff 15 [IAT]` ignora `mov reg,[IAT]`, thunk,
  delay-import e cave de patch anterior; e `int3` não mata processo quando a
  função tem SEH (`push fs:[0]`), então "subiu vivo" não quer dizer "não
  executou". Ver `HISTORICO.md`, "Tamanho da fonte".
- **Comparar tamanho de texto a olho, em tela cheia, não decide.** Duas rodadas
  foram gastas discutindo se a fonte tinha mudado. O que decidiu foi recortar a
  mesma região de dois screenshots e ampliar em nearest-neighbor — aí "idêntico
  ao pixel" ou "mudou" é fato, não impressão.
- **`source` do mysql.exe quebra com barra invertida** (`\U` = comando
  desconhecido). Usar barras normais no caminho.
- **Ler tabela grande de bytecode Lua 5.1:** o operando `RK` só endereça
  constante até o índice 255; depois disso o compilador emite `LOADK` num
  registrador e o `SETTABLE` referencia `R<n>`. Um parser que lê só
  `SETTABLE ... ; B="NOME" C=<valor>` captura as ~127 primeiras entradas e
  devolve um número **plausível e errado**.
- **Um `.lub` pode definir MAIS DE UMA tabela, e ler tudo numa lista só
  colapsa uma na outra.** O `valida_visual.tabela_lua` devolve os pares de
  todas as tabelas do arquivo achatados; um `dict()` por cima fica com a
  **última**. O `spriterobename.lub` tem três globais — `RobeNameTable`,
  `RobeNameTable_Eng` e `RobeTopLayer` —, e as duas primeiras têm as mesmas
  chaves com valores diferentes. O `instala_manto.py` leu a errada de
  2026-08-08 a 2026-08-09 e não doeu porque 98 das 120 entradas têm os dois
  nomes iguais; nas 17 em que diferem, a pasta que existe no GRF é a da
  **primeira**, em 17 de 17. Quem lê `.lub` corta o bytecode por `SETGLOBAL`
  (ver `estende_robeid._globais`) antes de indexar. E cuidado com o terceiro
  tipo: `RobeTopLayer` é **vetor** (`SETLIST`), não mapa — quem só olha
  `SETTABLE` o vê vazio e o descarta, e regerar o arquivo sem ele faz 38
  mantos passarem a desenhar atrás do personagem, calados.
- **Este cliente NÃO desenha manto com slot acima de 120**, e a tabela não
  tem nada a ver com isso. Medido em tela em 2026-08-09: slot 61, 73, 75, 82,
  90, 99, 104 e 114 desenham; 122, 136, 148, 154 e 158 não. A
  `spriterobeid.lub` foi levada a **158 entradas contíguas**, o cliente a
  leu, e nada mudou. É teto do exe. Enquanto ele não for levantado (patch de
  exe, ver `PENDENCIAS.md` §4), manto novo entra **reaproveitando** um dos 40
  slots ≤120 que não têm arte neste cliente — `ferramentas/estende_robeid.py`,
  com o de-para no `View:` do `db/guerra/item_db.yml`. Sobram 31.
- **Tabela certa + arte certa + arquivo lido pelo cliente ≠ desenha na
  tela.** As três se verificam offline, as três deram OK, e o item continuou
  invisível por um quarto motivo que nenhuma delas alcança. **Verificação
  offline que passa não é prova de efeito** — o que decide é uma marca na
  tela que não dependa do efeito procurado. Foi a sonda do
  `estende_robeid.py` (reapontar um slot que já funciona para outra arte) que
  respondeu em uma rodada o que três hipóteses plausíveis não responderam:
  falta de arte, arquivo não lido e buraco na numeração — todas descartadas
  **depois** de já terem custado tempo. Mesma família do
  `ajusta_tamanho_fonte.py`, logo acima.
- **O horário de ACESSO do arquivo diz se o cliente leu.** `Get-ChildItem |
  Select LastAccessTime` no `cliente\data\...\datainfo` mostra o instante em
  que cada `.lub` foi aberto — e compará-lo com a hora em que o cliente subiu
  separa "o override não chega" de "o override chega e não basta" sem entrar
  no jogo. Funciona mesmo com `DisableLastAccess = 2` neste Windows.
- **Ferramenta que consulta tabela do cliente tem de ler `cliente\data\`
  ANTES do GRF.** O `DataFolderFirst` faz o disco vencer, então depois de
  qualquer `estende_*.py` gravar o override é ele que o cliente lê. Uma
  ferramenta que só leia o GRF continua respondendo pelo arquivo de
  2021-11-03 e **nega a existência do que acabou de ser posto** — o
  `instala_manto.py` recusou, em 2026-08-09, um manto cuja entrada de tabela
  existia havia um minuto. O `valida_visual.le_tabelas_acessorio` já
  documentava isso do lado do chapéu; o erro foi não aplicar do outro.
- **Compilar pela linha de comando exige `SolutionDir` explícito.** O
  `map-server.vcxproj` tira os caminhos de include dessa variável, que só o
  `.sln` define. Sem ela o compilador não acha `common/cbasetypes.hpp` e
  despeja dezenas de `C1083` — que parecem código quebrado, e não são. E
  `MSBuild rAthena.sln -t:map-server` **não** funciona: o alvo é repassado a
  todo projeto da solução e cada um responde `MSB4057`. O que funciona:
  ```
  MSBuild.exe src/map/map-server.vcxproj -p:Configuration=Release \
    -p:Platform=x64 "-p:SolutionDir=<raiz>/rathena/"
  ```
  **Parar o map-server antes de linkar** — executável no ar dá `LNK1104`, e aí
  o binário em disco continua o antigo enquanto tudo mais indica sucesso.
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
- **Comentário no fim de uma linha de spawn entra DENTRO do nome do evento.**
  O `npc_parsesrcfile` enche o `w4` *"to end of line"* (`src/map/npc.cpp`), e o
  `npc_parse_mob` lê o evento com `%77[^,]` — que só para na vírgula. Um
  `<TAB>// Amon Ra` depois do evento vira parte dele, e o `mob_parse_dataset`
  (`src/map/mob.cpp:446`) só tira a aspa quando ela é o **último** byte. Falha
  **calada**: o chefe nasce, anda, morre, e o evento nunca dispara — nada no log
  aponta para a linha. Quem documenta um spawn documenta **acima** dele, ou no
  cabeçalho do arquivo (ver `npc/guerra/corredor_fantasma.txt`).
- **Uma linha ruim mata o ARQUIVO INTEIRO, não a linha — inclusive linha de
  comentário.** O `npc_parsesrcfile` (`src/map/npc.cpp:5646`) imprime
  *"Unknown syntax in file '...', line 'N'. Stopping..."* e **para de ler o
  arquivo ali**. Tudo que vier abaixo simplesmente não existe, sem outro aviso.
  Achado em 2026-08-08: um `\n` dentro do texto de um gerador partiu uma linha
  `//=` do **cabeçalho** em duas, e a metade órfã (`pc\ do`) derrubou os dois
  NPCs que estavam 25 linhas mais abaixo. Duas consequências:
  1. **Um erro no cabeçalho é tão fatal quanto um erro no código.** Depois de
     gerar arquivo de NPC, conferir que **toda linha antes da primeira definição
     começa com `//`** ou está vazia.
  2. **O log não ajuda a achar.** Essa única linha de `[Error]` fica soterrada
     sob centenas de `[Warning]` inofensivos dos mercados. Procurar por
     `Unknown syntax`, não ler o fim do log.
- **Heredoc do Bash aqui come a contrabarra dupla.** `<<'EOF'` deveria ser
  literal e não é: `\\` chega como `\` no arquivo gerado. Se esse arquivo for um
  script Python, o `\n` que sobra vira quebra de linha de verdade dentro do
  texto — foi essa a causa da armadilha acima. Ao gerar texto com caminho do
  Windows (`data\sprite\npc\`), escrever o script com a ferramenta de escrita de
  arquivo, não por heredoc — ou montar a contrabarra com `chr(92)`.
- **Em spawn com área, `<xs>,<ys>` NÃO é o lado do retângulo.** O `mob_spawn`
  chama `map_search_freecell` com `xs-1` (`src/map/mob.cpp:1149`), que sorteia em
  `rnd_value(bx-rx, bx+rx)`. `mapa,120,120,70,70` é **120 ± 69**, não 120±35 nem
  um quadrado de 70. Ler como lado erra a área por quatro, e o erro não se
  denuncia — os monstros nascem, só que em lugar diferente do planejado.
- **Mapa pode ter pedaço andável solto, e `0,0` no spawn sorteia lá.** O
  `vis_h01` tem 16.104 células no mapa de verdade **mais 479 na linha y=239**,
  ruído do `.gat`. Monstro sorteado ali fica inalcançável. Antes de usar `0,0`,
  varrer os pedaços conectados do `.gat` — ou dar coordenada e área, como o
  `corredor_fantasma.txt` faz.
- **`getitem` com a mochila cheia LARGA O ITEM NO CHÃO.** O
  `buildin_getitem` (`src/map/script.cpp`) chama `pc_additem`, e no fracasso
  cai num `map_addflooritem` — então "vai direto para o inventário" não é
  garantia do script, é garantia do **item**. Quem impede a queda é o
  `pc_candrop`, que recusa item `NoDrop`; com ele o item se perde e o cliente
  avisa. Item sem `NoDrop` entregue por script aparece no chão da arena, ao
  alcance de qualquer um, e nada no log denuncia. Caso vivo: a Caveira Humana
  (30995), em `npc/guerra/honra_de_combate.txt`.
- **Em `conf/groups.yml`, `false` não desliga nada.** Herança de grupo é um OU
  binário aplicado **depois** do parse (`pc_groups.cpp:275`,
  `permissions |= otherGroup->permissions`). Permissão que o pai concede, o
  filho não consegue tirar — `attendance: false` no `Super Player` é letra
  morta, porque ele herda do `Player`, que a concede. Ler a linha e concluir
  "esse grupo não tem" dá diagnóstico invertido.
- **`OnNPCKillEvent` NUNCA dispara para mob que tem evento próprio.** Em
  `mob.cpp:3592` os dois são ramos de um `else if`: se `md->npc_event[0]` está
  preenchido, roda o evento do mob e o global **não roda**. Como todo chefe de
  instância nasce com `instance_npcname(...)+"::OnMyMobDead"`, **nenhum deles
  dispara o evento global** — um contador de caçada feito assim compila, sobe,
  não erra no log e conta zero. Quem conta morte de verdade é o objetivo
  `HUNTING` de quest: o `quest_update_objective` roda antes, fora daquele `if`,
  e o `map_foreachinallrange` (`mob.cpp:3575`) ainda propaga para a **party
  inteira dentro de `AREA_SIZE`**. É o que as instâncias do próprio rAthena
  usam. Mesmo quando o global dispara, é para o `first_sd` — o primeiro do
  registro de dano, não o matador.
- **Quest que o cliente não conhece DERRUBA O CLIENTE.** Não é "aparece sem
  título" — é caixa de erro de Lua, uma **por missão e por atualização da
  janela**, até a conexão cair. O `GetOngoingQuestInfoByID`
  (`data\luafiles514\lua files\datainfo\questinfo_f.lub`, linha 4) faz
  `QuestInfoList[id].Title` **sem guarda de nil**, e sai
  *"attempt to index field '?' (a nil value)"*. As outras funções do mesmo
  arquivo (`Description`, `RewardItemList`, `CoolTimeQuest`) **têm** guarda —
  só a do título não. Pegar sete missões de uma vez rende dezenas de caixas
  seguidas. Achado em 2026-08-08, no primeiro teste das placas da Ordem.
  A entrada mora em `System\OngoingQuestInfoList_True.lub` e
  `_Sakray.lub`, e o mínimo que impede o estouro é
  `[<id>] = { Title = "...", Description = { "..." }, Summary = "..." }`.
  **Aqueles dois arquivos são gerados** pelo `traduz_ptbr.py questinfo`, que
  os reconstrói do coreano de 2021 — entrada posta à mão some na próxima
  rodada. Por isso as nossas são geradas por
  `ferramentas/monta_missoes_da_ordem.py`, que roda **depois** dele.
- **`getexp` NÃO passa pela taxa de EXP do servidor.** A `base_exp_rate` é
  aplicada uma vez só, ao EXP de **mob**, no carregamento do `mob_db`
  (`mob.cpp:5077`); o `getexp` de script só é multiplicado pelo
  `quest_exp_rate` (`conf/battle/exp.conf`), que está em **100**. Então
  `getexp 800000,800000` entrega 800.000 num servidor cujo monstro rende dez
  vezes mais — a recompensa de NPC vale **um décimo** do que o número sugere,
  em relação ao resto. Ler "somos 10x" e supor que o script acompanha erra a
  economia inteira, e nada denuncia.
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
- **`os.system` com a linha começando por aspas** falha no `cmd` do Windows: o
  primeiro par de aspas é comido e sai *"A sintaxe do nome do arquivo... está
  incorreta"* — que parece defeito do arquivo passado, e não é. Usar
  `subprocess.call([exe, arg, ...])`.
- **Literal de `setarray` pode virar NOME DE VARIÁVEL, e aí traduzir quebra.**
  No `DevilTower.txt` os cinco `"DIR_NORTHWEST"`, `"DIR_NORTH"` etc. são
  concatenados: `'coord_seal_DIR_NORTHWEST` e `'round[DIR_NORTHWEST]`. Chegam
  ao catálogo de tradução por um `setarray` de texto, **parecem rótulo de
  direção** e não são — traduzir faz o script procurar variável que não
  existe. Falha calada: o selo mágico simplesmente não anda. O `RE_TECNICO`
  cobre `setd`/`getd`, não este caso. Regra prática: literal em MAIÚSCULA com
  `_` dentro de `setarray` é suspeito até prova em contrário.
- **`F_GetPlural` aplica regra de plural INGLESA à palavra que a gente
  escrever.** O `callfunc("F_InsertPlural", n, "Second")` vira "3 Seconds";
  traduzido para `"Segundo"` vira "3 Segundos", que está certo — mas por sorte
  de terminação. A função (`npc/other/Global_Functions.txt`) acrescenta `-es`
  em `-s/-x/-z/-ch/-sh`, troca `-f/-fe` por `-ves`, `-y` por `-ies`, e tem uma
  lista de exceção em `-o` (`potato|tomato|…`). Palavra portuguesa que caia num
  desses ramos sai errada na tela e **nada avisa**. Conferir a terminação antes
  de traduzir argumento de `F_InsertPlural`.
- **A descrição do item na tela discorda do script do servidor — no NÚMERO, não
  só na presença.** A descrição vem do `itemInfo` do cliente, que é a tradução
  do kRO de 2021; o efeito vem do `Script:` do `item_db` do nosso rAthena, que é
  outra revisão. Caso vivo em 2026-08-09: a **Capa do Comandante** (20925) diz
  na tela *"Resistência as raças Humano e Doram +5%"* e o script dá
  `bonus2 bSubRace,RC_Player_Human,3` — 3, e nada para Doram. Somar resistência
  lendo a tela dá um total plausível e errado, e a diferença não aparece em
  lugar nenhum. **Conta de efeito se fecha no `item_db`.**
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
- Ferramentas rodam em **Python 2.7** (`C:\Python27\python.exe`).

## 6. Caminho de LEITURA — leia só o que a tarefa pede

**Cada documento tem uma função. Nenhum se lê inteiro** (exceto este e o
`ARQUITETURA.md`, que são curtos de propósito).

| Documento | Função | Como ler |
|---|---|---|
| `CLAUDE.md` | mapa, regras, o que não se pode fazer | inteiro — é a partida |
| `ARQUITETURA.md` | quem lê o quê, o que muda junto | inteiro, ao mexer em peça nova |
| `RECEITAS.md` | passo a passo dos fluxos repetíveis | só a receita da tarefa |
| `PENDENCIAS.md` | **só o que está em aberto** | inteiro — é curto |
| `HISTORICO.md` | o que já foi feito, e por quê | **só a seção do assunto** |
| `REFERENCIA.md` | caminhos, portas, comandos, credenciais | só a tabela |
| `npc/guerra/scripts_guerra.conf` | índice narrado dos nossos NPCs | antes de tocar conteúdo |
| `ferramentas/LEIAME.md` | uma seção por ferramenta | só a seção da ferramenta |
| `CUSTOMIZACAO-VISUAL.md` | frente visual (cidade destruída) | só a seção |
| `REDUCAO-DE-DANO.md` | o que entra e o que escapa da redução de cartas (resistência a humano) | consulta, só a seção — **antes de discutir número de PvP** |
| `CATALOGO-*.md` | o que está à venda, modelos, retratos | consulta |

**Ordem para uma tarefa nova:** `CLAUDE.md` → `scripts_guerra.conf` (o que já
existe?) → `RECEITAS.md` (como se faz?) → o **cabeçalho do arquivo** em
`npc/guerra/` → e só então o `HISTORICO.md`, se ainda faltar o porquê.

**Cada arquivo em `npc/guerra/` tem um cabeçalho longo explicando as decisões
dele.** Ler o cabeçalho custa menos que reconstruir o raciocínio — e é onde
estão as ressalvas que não cabem no índice.

## 7. Caminho de ESCRITA — onde registrar o que foi feito

**Escrever no arquivo errado é o que apodrece a documentação.** A regra é por
natureza do que se escreve, não por quando:

| O que você tem | Onde escrever |
|---|---|
| Trabalho **terminado** (o que foi feito e por quê) | `HISTORICO.md`, ao fim da seção do assunto, com **data absoluta** |
| Trabalho **em aberto** (falta fazer, falta testar) | `PENDENCIAS.md` |
| **Regra nova** ("nunca faça X", "sempre confira Y") | `CLAUDE.md` §4 |
| **Armadilha nova** de ferramenta/ambiente | `CLAUDE.md` §5 |
| **Fluxo novo** que vai se repetir | `RECEITAS.md` |
| **Acoplamento novo** (mexer em A exige mexer em B) | `ARQUITETURA.md` §4 |
| Caminho, porta, comando, credencial | `REFERENCIA.md` |
| Por que **este** NPC/item é assim | cabeçalho do próprio arquivo |
| NPC novo | uma linha + parágrafo em `scripts_guerra.conf` |

**As três regras que mantêm isso vivo:**

1. **Ao concluir uma pendência, apague-a do `PENDENCIAS.md`** e registre no
   `HISTORICO.md`. Pendência concluída que fica é ruído — foi o motivo de os
   dois arquivos terem sido separados em 2026-08-07.
2. **Regra e armadilha SOBEM para o `CLAUDE.md`.** O `HISTORICO.md` guarda o
   *porquê*; o `CLAUDE.md` guarda a *regra*. Deixar a regra só no histórico é
   garantir que ela seja redescoberta do jeito caro.
3. **Não duplicar.** Se algo já está no `CLAUDE.md`, o histórico aponta para
   ele em vez de repetir — duas cópias divergem, e a errada é sempre a que
   alguém lê.

## 8. Convenções de trabalho

- Documentação e comentário em **português**.
- Comentário de código explica **por que**, não o que — é o padrão de todo o
  projeto e o que o faz navegável.
- Datas sempre **absolutas** (`2026-08-07`), nunca "ontem" ou "semana passada".
- Nunca colar senha real em arquivo versionado. Senhas vivem em `conf/import/`.
