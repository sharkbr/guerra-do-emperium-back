# Armadilhas: O cliente de RO

GRF, .lub e bytecode Lua, tabelas do cliente, sprite e .act, .rsm e mapa, patch de exe, itemInfo, efeitos.

**Este arquivo é um dos seis cadernos de armadilhas do projeto.** O índice de
todos eles — uma linha de gatilho por armadilha, com o caderno onde o caso
está contado por inteiro — está na §5 do `CLAUDE.md`. **Leia aqui a entrada
que o gatilho apontar**; ler o caderno inteiro não é para ser preciso.

As entradas abaixo produziram diagnóstico falso e custaram retrabalho. Cada
uma traz o sintoma, a causa medida (com arquivo e linha, quando existe) e a
saída — e a medição é o que separa esta lista de um palpite. **Armadilha
nova se escreve nas duas pontas:** o caso aqui, o gatilho na §5.

---

- **Entrada de GRF marcada como "DES" NÃO é entrada ausente.** O
  `ferramentas/grf.py` recusa arquivo com o bit de cifra (`flags & 6`) com um
  *"arquivo com DES: ..."*, e metade dos sprites antigos deste `data.grf` está
  assim — inclusive `.spr`/`.act` de NPC que desenham perfeitamente em jogo. Ler
  isso como "o cliente não tem o sprite" **reprova sprite bom**, que é
  exatamente a conferência que a regra do view id manda fazer. O que prova
  presença é o **nome estar na tabela** do GRF (`grf.py <grf> find <padrão>`),
  não o `read` devolver bytes. Medido em 2026-08-13 no `4_ghost_stand`.

- **`.lub` do GRF é bytecode** (header `\x1bLua`); os do ROenglishRE são texto
  puro. Comparar tamanho entre os dois não significa nada.

- **O bRO entrega o MESMO arquivo em `.lua` e em `.lub`, e o legível pode
  estar velho.** O reflexo é pegar o texto puro e poupar o desmonte de
  bytecode; ele funciona, abre, tem conteúdo e **está incompleto**. Medido em
  2026-08-28 no `stateiconinfo`: o `.lua` do bRO cita **340** efeitos e o
  `.lub` ao lado tem **530** — 193 a menos, mais de um terço das traduções,
  sem erro nenhum e sem nada na tela que denuncie (o efeito que faltasse
  simplesmente continuaria em coreano, que é o estado de antes). É a mesma
  família do catálogo velho da §4.13: o arquivo abre, tem conteúdo, e o que
  falta nele não existe para quem o lê. **Quem manda é o `.lub`** — é ele que
  o cliente do bRO carrega. Contar as entradas dos dois antes de escolher
  custa um comando.

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

- **Um TETO num valor que todo mundo pede não limita exageros: ele apaga a
  escala inteira.** O `--teto 11` do `ajusta_tamanho_fonte.py` parecia calibrado
  — cada degrau foi olhado na tela — e na verdade achatava os **oito** corpos do
  cliente num só. O jogo ficou sem hierarquia tipográfica: nome de mapa do
  tamanho do chat. **Passou porque cada texto isolado parecia plausível**; o que
  destoou foi o maior, e o pedido chegou como "o nome do mapa está pequeno", que
  aponta para o lugar errado. Antes de pôr teto, **medir a distribuição do que é
  pedido** — se nada cai abaixo dele, não é teto, é achatamento. E há como
  medir: o cache do stub é indexado pelo tamanho pedido, então lê-lo no processo
  vivo (`--tabela`, `ReadProcessMemory`) devolve o histograma. Uma leitura
  respondeu o que dois dias de calibragem a olho não responderam.

- **Metade de uma seção de PE pode não existir em disco.** A `.xdiff` deste exe
  tem `VirtualSize` 0x1000 e **`SizeOfRawData` 0x400**: de `0x013B5400` para
  cima o carregador zera, e byte gravado ali no arquivo **não chega na
  memória** — fica no fim do `.exe`, fora de qualquer seção mapeada. Rascunho
  funciona (zero é o estado inicial certo); **tabela de dados não**, e a falha é
  calada — lê-se zero. Conferir `SizeOfRawData` antes de escolher onde pôr dado
  em patch de exe.

- **O vão que decide onde centrar um modelo pode não estar nem no `.gat` nem
  no id de textura do `.gnd`.** Tapete, mosaico e faixa de piso costumam ser
  **outra região do mesmo `.bmp`**, escolhida pelas **coordenadas UV** da
  superfície — o `.bmp` é um atlas. Então: o `.gat` diz chão liso e andável, o
  id de textura diz uma textura só para o corredor inteiro, e o tapete que
  aparece no print não existe em nenhuma das duas leituras. Quem só olha essas
  duas conclui "aqui não há vão, célula inteira serve" e planta meia célula
  fora do centro — a mesma armadilha da fonte do Centro da Ordem (vão de
  largura **par**: nenhum inteiro acerta o centro), só que invisível.
  O que mostra é ler os **8 floats de UV** da superfície de topo tile a tile
  (`Gnd.superficie_topo` + os bytes 0..31) e desenhar: o tapete salta como um
  bloco de UVs distintos. Caso vivo em 2026-08-11: os três tapetes de 8x8
  células da ala leste de `auction_01`, todos na textura 3.

- **Caixa envolvente de `.rsm` com vários nós mente se juntar tudo num box
  só.** O `pos` do nó raiz é offset no espaço do modelo, não dimensão: no
  `desk_h_02.rsm` (4 nós, raiz em `x = -129,35`) a medida junta dá **148,90 de
  largura — 29,8 células** em vez de 20,02 (4,0 células). O número é plausível
  o bastante para condenar um modelo por "não cabe". Medir **nó a nó**.
  **E medir nó a nó não diz onde é o CENTRO da peça** — para isso é preciso
  remontar os nós, e a regra é: o vértice do nó **raiz** entra como
  `vértice − pos_raiz`, e o do **filho** deslocado de `pos_filho − pos_raiz`.
  Sem isso as caixas não se encontram e a leitura parece corrompida: nas
  `prn_statue_*` a base dá `X −21,50..−14,45` e a figura `X −5,13..3,91`, uma
  fora da outra. Quem remonta acha a base em **−3,53..+3,53 nos dois eixos** —
  um quadrado perfeitamente centrado —, e é essa coincidência que prova a
  leitura. Consequência prática: **a origem do modelo é o centro da base**, e é
  ela que o `edita_mapa.py` põe na célula.

- **No `.rsm`, a ALTURA é o Z e não o Y — a planta de um móvel é X × Y.** Ler
  X × Z troca profundidade por altura e devolve uma planta plausível e errada,
  na direção que faz um móvel parecer caber onde não cabe: a escrivaninha do
  Centro da Ordem é 4,0 × 2,8 células e pelo eixo errado sai 3,9 × 1,5. A prova
  é barata e não é teórica — medir uma peça alta e fina: a coluna
  `내부소품\기둥2` dá 6,34 × 6,34 × **30,21** e a estátua `모로코\동상` dá
  8,57 × 5,43 × **29,25**. O eixo de 30 é o vertical.
  Isso dá de graça **de que lado é a frente** de um móvel — o encosto é o lado
  do Y onde o modelo é alto (`+Y` nos dois sofás do salão) — e daí a rotação,
  que antes era palpite: **`+Y` → (sen θ, cos θ) em (X, Z)**, ou seja em
  **rot 0 as costas apontam para o norte** e em rot 90 para leste. Consequência
  que engana sozinha: **rot 0/180 põem a LARGURA no eixo leste-oeste, e 90/270
  no norte-sul** — o contrário do que a intuição sugere. Tudo isto está medido
  e conferido contra os 22 usos oficiais do sofá em `prt_cas`; a ferramenta é
  `ferramentas/mede_rsm.py`, que já imprime os eixos rotulados.

- **Modelos de uma mesma família numerada NÃO têm a mesma frente, e supor que
  têm vira metade deles de costas.** As oito `prontera\prn_statue_0*.rsm` são
  da mesma pasta, do mesmo conjunto e da mesma cara — e pelo menos uma nasceu
  virada ao contrário: em `prt_lib`, lado a lado na mesma parede sul e olhando
  as duas para o norte, a `_08` está em **rot 180** e a `_02` em **rot 0**.
  Calibrar a rotação de uma e reusar o número nas outras sete põe estátua de
  costas, calado. **Medir por modelo**, e a medida é de graça: varrer os `.rsw`
  do GRF do bRO pelo `filename` dá as instâncias oficiais, e o `.gat` em volta
  de cada uma diz para que lado está a parede — estátua encostada em parede
  olha para fora dela. A convenção de ângulo é a mesma do sofá (**rot 0 olha
  para o sul, 90 oeste, 180 norte, 270 leste**); o que muda de modelo para
  modelo é qual ângulo é o "de frente".

- **`mede_rsm.py` que não sobra 0 byte não vale nada.** Formato de malha é
  cheio de campo opcional por versão, e um campo lido a menos desalinha tudo o
  que vem depois **devolvendo números do mesmo jeito**. O `sofa_01.rsm` sobra
  exatamente 8 bytes se o leitor parar nos nós e não ler o rabicho de quadros
  de posição e caixas de volume — e as dimensões que ele imprime até ali
  parecem boas.

- **São TRÊS `map_cache.dat`, e a `prontera` não está no grande.** O rAthena
  abre `db/import/map_cache.dat`, `db/re/map_cache.dat` e `db/map_cache.dat`
  **nessa ordem** (`map.cpp:3922`), e o primeiro que tiver o mapa vence. O
  `db/re/` tem oito mapas — `prontera`, `alberta`, `izlude`, `morocc`,
  `prt_church`, `prt_fild05`, `prt_fild08`, `prt_in` — e são esses que valem.
  A `prontera` de renewal (312x392) **só existe lá**; o cache grande, de 1288
  mapas, tem uma `pprontera` do mesmo tamanho, que é outro mapa. Ferramenta
  que abra só o `db/map_cache.dat` responde *"prontera não está no cache"* —
  resposta do leitor, não do mapa — ou, pior, entrega a `pprontera` como se
  fosse a cidade. Conferir célula andável passa pelos três, na ordem.

- **Ler tabela grande de bytecode Lua 5.1:** o operando `RK` só endereça
  constante até o índice 255; depois disso o compilador emite `LOADK` num
  registrador e o `SETTABLE` referencia `R<n>`. Um parser que lê só
  `SETTABLE ... ; B="NOME" C=<valor>` captura as ~127 primeiras entradas e
  devolve um número **plausível e errado**.

- **Chave de tabela que é SÍMBOLO INDEXADO POR NÚMERO colapsa a tabela inteira
  numa entrada só, sem erro nenhum.** O `ptbr._interpreta` sabia resolver
  `SKID.NV_BASIC` (símbolo indexado por *string*) e devolvia `None` para
  qualquer outro caso — inclusive `EnumVAR.VAR_MAXHPAMOUNT[1]`, que é a chave
  do `addrandomoptionnametable.lub`. Como todas as chaves viram `None`, o
  `dict` fica com **uma** entrada, a última: o leitor responde *"tabela com 1
  entrada"* sobre um arquivo de 252, e nada quebra. Corrigido em 2026-08-18
  com um ramo de `Sym` indexado por número. A regra que sobra: **tamanho de
  tabela igual a 1 é sintoma de chave não resolvida**, não de arquivo vazio.

- **Tabela do cliente cujas chaves são `EnumVAR.<X>`, `SKID.<X>` e afins tem de
  ter as CHAVES tiradas do NOSSO GRF — nunca do ROenglishRE nem do bRO.** A
  chave não é constante: é resolvida em tempo de execução contra o `enumvar.lub`
  (ou equivalente) **deste exe**. Chave que ele não conheça vira `nil`, e
  indexar `nil[1]` é erro de Lua que derruba a tabela inteira — o efeito some da
  janela, não fica "sem nome". É a mesma família da armadilha do `skilltreeview`
  e da janela de missões; o texto pode vir de qualquer fonte, a chave não.

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
  com o de-para no `View:` do `db/guerra/item_db.yml`. Sobram 28.
  **E não é só manto cosmético:** capa de STATUS (`Garment`) com `View` cai no
  mesmo teto e gasta doador igual — foi o que a Som do Luar e as Asas de Garuda
  mostraram em 2026-08-16, no Capeiro.

- **Rótulo de aba da janela de habilidades é escrito na VERTICAL: o
  comprimento gasta altura, não largura — e some com as abas de baixo.** As
  nove abas do `skilltreeview.lub` empilham uma letra por linha (~13px cada) e
  dividem uma coluna de ~370px. `Aprendiz-1a` + `2a-Transcend.` bastavam para
  cortar a terceira aba ao meio, **fora do alcance do clique**, escondendo a
  habilidade que um equipamento concede (achado em 2026-08-11). Teto de **7
  caracteres**, travado por `LIMITE_ABA` no `traduz_ptbr.py`. Falha calada: a
  janela abre, funciona, e uma aba inteira do personagem não existe.

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
  **Mas o carimbo só anda de hora em hora, e isso inverte a resposta.** O NTFS
  só reescreve o `LastAccessTime` quando o valor guardado tem **mais de uma
  hora**; leitura dentro da mesma hora não mexe nele. Então qualquer coisa que
  tenha tocado o arquivo há pouco — inclusive a sua própria conferência depois
  de gravar — congela o carimbo, e a sonda responde *"o cliente não leu"* sobre
  um arquivo que ele leu. Medido em 2026-08-14, e custou uma hipótese inteira.
  Só vale como prova quando o último acesso é **anterior em mais de uma hora**
  ao instante em que o cliente subiu.

- **O endereço do servidor mora no `sclientinfo.xml`, não no `clientinfo.xml`.**
  Este exe é `<servertype>sakray</servertype>`, e o par sakray é o
  `cliente\data\sclientinfo.xml` — provado em 2026-08-14, quando trocar só o
  `clientinfo.xml` deixou o cliente indo em `127.0.0.1` e trocar o
  `sclientinfo.xml` fez o login na produção acontecer. Engana porque os **dois**
  existem em `cliente\data\`, os dois têm `<address>`, o exe carrega as duas
  strings sobrepostas (`sclientinfo.xml` em `0x9f707c`, `clientinfo.xml` um byte
  adiante) e o `.epi` ainda lista o patch `CallKoreaClientInfo`, que sugere o
  contrário. **Manter os dois com o mesmo endereço** é o que evita a próxima
  hora perdida. Vale para o instalador também: quem empacotar o cliente leva os
  dois.
  Três becos sem saída do mesmo dia, para não se repetirem: o cliente **resolve
  nome de domínio** (`EnableDnsSupport` está no `.epi`, então o `<address>` pode
  ser o domínio); **não há regra de firewall** para o exe e a saída é liberada; e
  **demora não descarta o loopback** — o SYN para `127.0.0.1:6900` com nada
  escutando ficou em `SynSent` até estourar o tempo, em vez da recusa imediata
  que a intuição promete. O que decide de verdade é olhar **para onde o pacote
  vai**: um laço de `Get-NetTCPConnection -OwningProcess <pid>` gravando o que
  aparece enquanto o jogador aperta Login responde numa tentativa o que três
  hipóteses plausíveis não responderam. Mesma família do `ajusta_tamanho_fonte.py`
  — marca que não depende do efeito procurado.
  **Desde 2026-08-16 isso ganhou um segundo gume:** este cliente é o de dev e
  aponta para `127.0.0.1`, então **empacotar a base ou mandar um dos dois xml
  em patch publica um cliente que ninguém consegue usar** — 3,4 GB corretos,
  sha256 fechando, e todo mundo tentando logar na própria máquina. O
  `monta_patch.py` e o `monta_cliente.py` passaram a recusar endereço local
  (`confere_apontamento`), e é bom que recusem: nada mais nesse caminho olha
  para esse campo.
  **E há o gume de VOLTA, que só apareceu em 2026-08-18: rodar o Atualizador
  dentro da pasta de dev transforma o cliente de dev em cliente de PRODUÇÃO.**
  Existe um `Jogar.exe` em `C:\GuerraDoEmperium\cliente`, e o patch 0004 leva
  os dois `clientinfo` com o endereço de produção — aplicá-lo ali reaponta o
  cliente sem perguntar nada. Os dois pacotadores protegem a **saída**; nada
  protegia a **entrada**, e essa falha é calada da pior maneira: o jogo abre,
  loga e joga, só que no servidor errado — quem estiver "testando local" está
  testando produção, e nada na tela diz isso. Vai voltar a acontecer em todo
  patch que leve os xml. O conserto é um comando, `ferramentas/aponta_cliente.py
  --dev`, e sem argumento ele só relata para onde os dois apontam.
  **E os backups eram de um lado só.** Existia `.BACKUP-138.197.155.31` e mais
  nada, então quando o de dev foi sobrescrito não havia de onde restaurar — o
  `127.0.0.1` teve de ser reconstruído à mão. Agora há `.BACKUP-` dos **dois**
  lados, e o `aponta_cliente.py` grava o lado de onde saiu antes de trocar.

- **A IA do homúnculo e a do mercenário moram em `cliente\AI_sakray\`, não em
  `cliente\AI\` — e a pasta errada não dá erro até alguém invocar o bicho.**
  Pelo mesmo `<servertype>sakray</servertype>` da entrada acima, as **cinco**
  strings de caminho de IA deste exe são todas da variante sakray
  (`.\AI_sakray\AI.lua`, `.\AI_sakray\AI_M.lua` e as duas de
  `USER_AI\`, mais a pasta) e **não existe nenhuma da pasta normal** — a
  instalação de 2021-11-05, porém, traz a pasta chamada `AI`. Resultado:
  clicar em Criar Homunculus devolve uma caixa `AI.lua error — cannot open
  .\AI_sakray\AI.lua`, com o embrião já consumido, e a suspeita cai em sprite
  ou IA quebrada — as duas erradas (os 21 `.spr` de homúnculo estão inteiros
  no GRF). A saída é copiar `AI` para `AI_sakray`, com o `USER_AI` junto. Os
  `require "AI\\Const"` de dentro **não** se mudam: o caminho traz o nome da
  própria pasta, ou seja a resolução é relativa à raiz do cliente. Medido em
  2026-08-15. **Fora do git** — some em cliente novo, e o instalador tem de
  levá-la.

- **Ferramenta que consulta tabela do cliente tem de ler `cliente\data\`
  ANTES do GRF.** O `DataFolderFirst` faz o disco vencer, então depois de
  qualquer `estende_*.py` gravar o override é ele que o cliente lê. Uma
  ferramenta que só leia o GRF continua respondendo pelo arquivo de
  2021-11-03 e **nega a existência do que acabou de ser posto** — o
  `instala_manto.py` recusou, em 2026-08-09, um manto cuja entrada de tabela
  existia havia um minuto. O `valida_visual.le_tabelas_acessorio` já
  documentava isso do lado do chapéu; o erro foi não aplicar do outro.

- **Sprite de NPC "enterrado no chão" é o `.act`, não o mapa.** O `.act` diz a
  que altura o desenho é colado em relação à célula; com `y` perto de zero o
  **centro** do sprite fica na altura do chão, a metade de baixo vai para
  debaixo do piso, e o depth buffer do terreno a corta — dá um **corte reto e
  horizontal** na base. Parece problema de célula, de altura de mapa ou de
  modelo, e não é: em 2026-08-12 a `2_COLAVEND` apareceu cortada em terreno
  medido como **plano** (4,00 nas duas células e na faixa inteira). As máquinas
  oficiais deste cliente levantam o desenho — `4_vending_machine` −53,
  `2_DROP_MACHINE` −44, `2_VENDING_MACHINE1` −40 — e a `2_COLAVEND` é a única
  com **`y = 0` nas oito direções**. A conta que os oficiais seguem é
  `-(altura/2 - 8)`. Ferramenta: `ferramentas/levanta_sprite_npc.py`; o
  override é **cliente, fora do git**, e some em cliente novo.

- **Bandeira de `CTRL+<n>` não está no `emotionlist.lub`, está no EXE — e o
  que ela vale depende do `<servicetype>`.** O `emotionlist.lub` define o
  `enum` inteiro (`ET_FLAG` 13, `ET_BR_FLAG` 51 e as outras sete) e ainda um
  `EMOTION_ORDERLIST`, o que o faz parecer o lugar certo; mas aquela lista tem
  **64 entradas e nenhuma bandeira** — é a ordem da *janela* de emoções, e
  bandeira não aparece na janela. Quem trata a tecla é um `switch` de nove
  casos no exe (`0x00638950`, tabela de saltos em `0x00638B1C`), e **cada caso
  é uma cadeia de comparações contra o `<servicetype>` do `clientinfo.xml`**
  (global `[012BF51C]`; `korea`=0 … `brazil`=12, na ordem dos nomes no
  `.rdata`) antes do trecho que empurra a emoção. Consequência que engana
  sozinha: com `korea` as nove teclas funcionam, com `brazil` **só o CTRL+1**,
  e com `america`/`japan`/`thai` **nenhuma**. Medido em 2026-08-12, quando o
  `data\clientinfo.xml` dizia `brazil` e o jogo se comportava como `korea`.
  Ferramenta: `ferramentas/ordena_bandeiras_ctrl.py`, que reaponta a tabela
  direto para os nove trechos e torna a ordem independente do servicetype.

- **O NOME do sprite não descreve a arte, e neste cliente NÃO EXISTE aura de
  chão colorida.** O `4_PURPLE_WARP` (10237) não tem nada de roxo: é um quadro
  só, 157x84, com **um único índice de paleta usado, o 255, que é preto** — o
  mesmo desenho do `1_SHADOW_NPC` (723), pixel por pixel. E não há outro:
  varridos em 2026-08-12 os 1.046 sprites de NPC com arte legível e view id
  abaixo do teto de 10508, **só esses dois** são decalque chato de quadro
  único. O arco-íris de sombras coloridas que o rAthena numera de 10554 a
  10560 (`1_SHADOW_RED` … `1_SHADOW_VIOLET`) é de um kRO posterior: não está no
  `npcidentity.lub` nem no `jobname.lub` daqui, não tem `.spr` no nosso GRF nem
  no do bRO, e o número ainda ficaria acima do teto. Pedido de "aura de chão"
  se responde com óvalo escuro ou com `specialeffect` em laço — o segundo
  reinicia a animação a cada disparo e some no intervalo. Ver `HISTORICO.md`,
  "Três ajustes em Comodo".

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

- **O cabeçalho do `map_cache.dat` tem 8 bytes, não 6.** É
  `uint32 file_size; uint16 map_count;` e o compilador o alinha em 8; ler a
  partir do byte 6 desalinha o arquivo inteiro e o leitor estoura umas dezenas
  de mapas adiante, longe da causa. O cabeçalho de cada mapa
  (`char name[12]; int16 xs; int16 ys; int32 len;`) tem 20 e esse não tem
  surpresa. Ver §5, entrada dos TRÊS `map_cache.dat`, para saber em qual deles
  procurar.

- **Metade da configuração do cliente está no REGISTRO DO WINDOWS, e não no
  cliente.** É a §4.9 um degrau adiante: lá as duas metades divergiam entre
  arquivos, aqui uma delas não é arquivo nenhum. O `GuerraDoEmperium.exe`
  escolhe em qual placa criar o dispositivo Direct3D lendo
  `HKLM\SOFTWARE\Gravity Soft\Ragnarok` (`DEVICENAME`, `GUIDDEVICE`,
  `GUIDDRIVER`, `SOUNDMODE`…), que quem escreve é o **`Setup.exe`** da raiz do
  cliente. Numa máquina onde ele nunca rodou a chave não existe, e o jogo morre
  na abertura com **`Cannot init d3d OR grf file has problem`** — mensagem que
  junta dois casos opostos com um `OR` e manda todo mundo conferir o GRF, que
  está perfeito. Medido em 2026-08-16, no primeiro teste do instalador em outra
  máquina: 4,2 GB corretos em disco, sha256 de cada pedaço fechando, e o jogo
  sem abrir.
  Duas consequências que andam juntas: **é por isso que o cliente pede
  elevação** (`HKEY_LOCAL_MACHINE` não se escreve sem privilégio), e um
  `exec.Command` do Go **não sabe elevar** — o `CreateProcess` devolve
  `ERROR_ELEVATION_REQUIRED` em vez de mostrar o UAC, e o jogador lê
  *"fork/exec …: The requested operation requires elevation"*. Quem eleva é o
  `ShellExecuteW`. Os dois sintomas eram a mesma causa vista de dois ângulos.
  **Consequência para qualquer cliente novo:** copiar a pasta do jogo NÃO
  basta. O `Setup.exe` tem de rodar uma vez por máquina, e o atalho precisa do
  bit `SLDF_RUNAS_USER`. O instalador faz os dois (`patcher/video.go`).

- **A censura de palavrão do jogo é do CLIENTE, e mora em `data\manner.txt`
  dentro do GRF — não no rAthena e não no exe.** Procurar `fuck`/`swear`/
  `badword` no `GuerraDoEmperium.exe` devolve zero e leva a concluir que o
  filtro não existe; procurar no `rathena/` também, porque o emulador não
  filtra palavra nenhuma. O arquivo tem 1409 linhas (uma palavra por linha,
  CP949, CRLF) e **25 delas são inglês** (`fuck`, `sex`, `shit`, `ass`,
  `damn`…), nenhuma em português — daí o sintoma parecer "censura de inglês".
  Desligar é um override em `cliente\data\manner.txt` (o `DataFolderFirst` faz
  o disco vencer o GRF), com uma palavra inócua dentro em vez de vazio, e vai
  ao jogador **por patch** — é cliente, ver §4.18.

- **"Unknown Item" com sprite de maçã NUNCA é problema de servidor — e a
  pergunta que resolve é *quais* itens, não *por que aquele item*.** O nome do
  item não trafega na rede: o servidor manda o ID e quem desenha é o
  `itemInfo.lua` do cliente (§4.9). Nenhum reinício, `@reloaditemdb` ou deploy
  muda uma letra daquela janela. O que a falta de carga no servidor produz é o
  sintoma **oposto**: o item **some da lista**, sem virar "Unknown".
  O que engana é a falha ser **seletiva** — numa vitrine de 23 linhas os itens
  antigos aparecem certos e só os novos caem no *fallback*, o que parece "cinco
  itens quebrados" e não "cliente com a tabela velha". O diagnóstico é uma
  medição só: **listar os IDs que falham e comparar com a lista dos que mudaram
  de tabela**. Em 2026-08-17 os 11 que falhavam eram exatamente as 11 entradas
  novas do `itemInfo.lua`, e a lista saiu de graça do backup que a ferramenta
  deixa ao lado (`itemInfo.lua.BACKUP-<data>`). Se bater, a causa é uma das
  duas: cliente aberto **antes** de o arquivo mudar (§3 — só se lê na
  inicialização), ou o patch não chegou à máquina do jogador (§4.18).

- **O `identifiedResourceName` do bRO é o DESENHO, não a identidade do item —
  e dois itens diferentes o compartilham.** É a ponte que resolve o caso em que
  o mesmo item tem número diferente aqui e lá (o bRO renumerou muita coisa), e
  por isso é tentador tratá-lo como chave. Não é: nome de recurso é só o
  caminho de um `.spr`, e sprite de arco, de bota e de capa é reaproveitado à
  vontade. Medido em 2026-08-18, nos quatro itens de um pedido que o nosso
  vendor não tinha, e **deu os dois resultados**:

  | pedido | recurso | quem mais usa | é o mesmo item? |
  |---|---|---|---|
  | 470004 Botas Imperiais | `Imperial_Boots` | 22207 | **sim** |
  | 22224 Sapatos Fofinhos | `Fluffy_FishShoes` | 22210 (`_J`) | **sim** |
  | 700102 Arco Experimental | `Local02_Bow` | 18173 Yinyang Bow | **não** |
  | 700080 Arco Mágico | `Hs_Rg_Bow` | 700061 Herosria Rogue Bow | **não** |

  Nos dois calçados a **ficha inteira** batia — peso, DEF, nível, e o `Script:`
  linha por linha —, e eram de fato o mesmo item, na versão sem cova. Nos dois
  arcos não batia **nada**: ATQ 130/nível 70 contra ATQ 180/nível 105, e ATQ
  200/sem cova/nível 200 contra ATQ 130/três covas/nível 100. Quem parasse no
  nome do recurso teria posto na loja o arco errado, com o nome certo e o
  desenho certo — falha calada e difícil de ver, porque a vitrine fica
  plausível. **O que decide é a ficha do `estado_item.py --id <n> --descricao`
  comparada campo a campo, nunca o recurso sozinho.**
  Da mesma família da §4.14 (o `Locations:` decide, não o nome) e da regra 3
  (traz-se do bRO, não se inventa): o recurso *sugere* de onde trazer, a ficha
  é que *prova*.

- **Gerador de entrada de cliente pode ter campo ZERO FIXO, e por seis itens
  seguidos isso pode estar certo.** O `instala_item.py` escrevia
  `slotCount = 0` e `ClassNum = 0` literais desde 2026-07-31, e nenhum dos
  seis itens nossos até 2026-08-18 tinha cova ou visual de cabeça — então o
  valor errado nunca apareceu. O primeiro item com os dois (o Chapéu do Éden,
  19272) sairia sem o `[1]` no nome, sem a cova na janela de encaixe de carta
  e sem o id de visual, **os três calados**. Os dois campos viraram
  `covas`/`visual`, opcionais, com zero por padrão. A lição não é sobre esse
  script: **campo constante num gerador é uma suposição sobre todos os casos
  já vistos**, e o `--verificar` não a denuncia porque ele compara com o que o
  próprio gerador produziria.

- **O `ClassNum` de ARMA no `itemInfo.lua` não vem do `View:` do `item_db` — ele
  vive só do lado do cliente, e zerá-lo troca o desenho da arma na mão, calado.**
  A regra que o `instala_item.py` documenta — *"`visual` bate com o `View:`"* —
  vale para equipamento de **cabeça**, onde o servidor manda o número. Para arma
  não há número a mandar: o `Vigilante_Bow` (18145) tem `ClassNum = 73` no
  cliente e **nenhum `View:`** no `item_db`, e **nenhum arco do vendor tem**.
  Quem for escrever receita de arma e procurar `View:` para copiar acha zero,
  escreve zero, e o arco passa a desenhar outra coisa — sem erro, sem log, e só
  se vê com a peça equipada. **Copiar o `ClassNum` que a entrada já traz.** Os
  vizinhos confirmam a numeração: 18109 e 1748 também são 73, o 18143 e o 18163
  são 11. Medido em 2026-08-27.

- **Nome e descrição do MESMO bloco do `itemInfo.lua` podem estar em línguas
  diferentes, e a ferramenta que resolve cada metade é outra.** O 18145 tem
  `identifiedDisplayName` em **coreano** e `identifiedDescriptionName` em
  **inglês** (do ROenglishRE) — ler só o nome faz o item parecer caso de
  `completa_iteminfo.py`, e ler só a descrição faz parecer que só falta
  traduzir. Não era nem um nem outro: o bRO tem o ID **em coreano e sem
  descrição**, então não há de onde copiar nada, e o caminho é receita à mão no
  `instala_item.py`. Ao classificar um item por idioma, **olhar os dois campos**.

- **`unidentifiedResourceName` TERMINA em `identifiedResourceName`, e um regex
  sem lookbehind casa com a linha errada.** No bloco do `itemInfo.lua` a linha
  do *unidentified* vem primeiro, então
  `re.search(r'identifiedResourceName = "([^"]*)"', bloco)` devolve o recurso do
  item **não identificado** — para equipamento, o gorro/veste genérica que o kRO
  põe ali. A saída é `(?<!un)` na âncora. Custou dois dias no `instala_item.py`
  (2026-08-18 a 2026-08-20), e a falha é calada **e seletiva**: quando as duas
  linhas trazem o mesmo recurso — o caso de todo `Etc` e todo consumível — o
  resultado é idêntico e nada aparece, então seis receitas seguidas passaram
  antes de a sétima morder. A mesma armadilha de nome espera em
  `unidentifiedDisplayName` e `unidentifiedDescriptionName`.
  **E o `valida_visual.py` NÃO pega isso**, porque ele confere *presença* de
  arquivo, não *identidade* de arte: o Chapéu do Éden (19272) deu "8 de 8 ok"
  com quatro dos oito arquivos apontando para a arte de outro item — os outros
  quatro estavam certos porque a cabeça vestida vem do `accessoryid`/`View`, não
  deste campo. **Validador de presença não separa "tem arte" de "tem a arte
  certa".**
  Uma consequência de desenho, e ela vale para qualquer gerador: **receita que
  aponta para si mesma (`arte_de: <o próprio id>`) não se recupera de uma rodada
  ruim** — o valor errado vira a fonte da rodada seguinte, e o certo não existe
  mais em lugar nenhum. Onde a intenção é "manter o que já está lá", escrever o
  valor **por extenso** na receita versionada (o campo `recurso`), nunca relê-lo
  do arquivo que se vai sobrescrever.

- **O `DataFolderFirst` está provado para ALGUMAS pastas, não para todas — e
  tratar uma pasta nova como se já estivesse provada custa uma sessão
  inteira.** As pastas onde o override de `cliente\data\` comprovadamente vale
  hoje são `System\`, `data\luafiles514\lua files\datainfo\` e as de sprite e
  textura. Em 2026-08-26 a `data\luafiles514\lua files\effecttool\` foi usada
  pela primeira vez — para pôr um emissor de partículas sob um NPC — e **quatro
  tentativas em jogo não desenharam nada**, incluindo uma que só clonava um
  emissor que já funcionava.

  **Antes de escrever conteúdo novo numa pasta de cliente que o projeto nunca
  usou, gravar ali uma CÓPIA IDÊNTICA do arquivo original do GRF e entrar no
  jogo.** Se o que já funcionava continuar funcionando, o override vale e o
  defeito é do que se escreve; se parar de funcionar, o problema é o mecanismo,
  e nenhum ajuste de conteúdo vai resolver. É o controle mais barato que existe
  e foi justamente o que faltou nas quatro tentativas — cada uma mudava conteúdo
  e posição ao mesmo tempo.

- **Dá para provar que o cliente ABRIU um arquivo, contornando a regra de uma
  hora do NTFS: basta empurrar o `LastAccessTime` para o passado antes do
  teste.** A entrada acima sobre o horário de acesso registra que o carimbo só
  é reescrito quando o valor guardado tem mais de uma hora — o que torna a sonda
  inútil logo depois de gravar o arquivo, que é justamente quando se quer usá-la.
  Empurrando o carimbo para ontem (`(Get-Item $f).LastAccessTime =
  (Get-Date).AddDays(-1)`), qualquer leitura seguinte passa a marcar, e a
  resposta vem sem depender do que se vê na tela. Medido em 2026-08-26: o
  carimbo pulou para treze segundos depois da abertura do cliente.

  **Mas ABRIR não é USAR.** No mesmo dia o cliente abriu o arquivo e não
  desenhou nada do que havia nele — então esta sonda responde "o arquivo chegou
  ao cliente", e só isso. Concluir dela que o conteúdo foi aplicado é o erro que
  custou duas tentativas.

- **O `EF_MAX` do rAthena NÃO é o teto de efeitos do cliente — é o do
  emulador, e ele está 900 efeitos atrasado.** O `buildin_specialeffect`
  recusa todo número a partir de `EF_MAX`, que vale **1243** no nosso vendor
  (o último nomeado é `EF_SOUL_EXPLOSION`, 1242). Só que este kRO de
  2021-11-03 conhece efeitos até **2372**, e **941 deles têm arte própria
  (`.str` no GRF) acima daquele teto**. Pedir um deles por `specialeffect`
  não desenha nada e escreve *"unsupported effect id"* no log — o efeito
  existe, a arte existe, e quem estava fechado era o caminho entre os dois.
  É a mesma família do `db/` do vendor semanticamente vencido (a entrada do
  `stylist.yml` acima): o dado não está errado, está velho, e nada avisa.
  A saída é o **`efeitoespecial`**, nosso, em `src/custom/script.inc` — o
  `specialeffect` com a faixa do cliente e nada mais. Entrou pelos ganchos
  oficiais `script.inc`/`script_def.inc`, então **não custou um byte de
  arquivo de terceiro**, e o `specialeffect` original continua intacto.
  **E há uma segunda armadilha dentro desta:** número fora da faixa 13..2372
  cai no `default` do switch do cliente e ele **não desenha nada, calado** —
  sem erro de Lua, sem caixa, sem log. Errar o número é indistinguível de "o
  efeito não existe". Conferir antes em
  `ferramentas/lista_efeitos_do_cliente.py --id <n>`.

- **Antes de mexer no `effecttool` para pôr uma textura na tela, perguntar
  que EFEITO já a desenha.** O pedido chega pelo nome de um `.bmp` e o
  reflexo é procurar onde enfiar aquele caminho — o que leva ao
  `effecttool\<mapa>.lub`, único mecanismo que aceita caminho de textura
  direto, e que custou **quatro idas ao jogo sem desenhar nada** em
  2026-08-26. Na maioria das vezes a textura pertence a um efeito que o
  cliente **já numera**, e aí o pedido inteiro é uma linha de script no
  servidor: sem patch, sem override, sem pasta nova para provar.
  **O sinal está no próprio GRF: um `.str` na mesma pasta da textura.**
  `.str` é definição de efeito numerado; textura sem `.str` por perto (o
  `epi_glow_01.bmp`, que é unidade de habilidade `UNT_EPICLESIS`) não tem
  número, e aí o `effecttool` é mesmo o único caminho. Foi essa diferença,
  e só ela, que separou o brilho que não saiu do que saiu de primeira.
  A pergunta se responde em um comando:
  `ferramentas/lista_efeitos_do_cliente.py --textura <padrão>`.
  **Cuidado com um detalhe que engana na entrega:** quase todo efeito tem
  **duas** variantes de arte, `mineffect\` e normal, escolhidas em tempo de
  execução pela opção de efeitos reduzidos do jogador. Elas costumam usar
  texturas **diferentes**, então a `.bmp` pedida pode só aparecer com aquela
  opção ligada — o `--id` diz de que lado cada uma está.

- **O cliente desenha coisa no mundo SEM o servidor — `grep` em `npc/` não
  prova que algo não existe.** O `data\luafiles514\lua files\signboardlist.lub`
  é uma tabela de **514 placas** (ícone em moldura laranja + plaquinha marrom
  com texto) que o cliente põe por mapa e célula, sozinho. Não há NPC por trás:
  clicar não faz nada, e nenhum `grep` no `rathena/` acha aquela coordenada.
  Boa parte anuncia coisa do kRO que aqui nunca existiu — em 2026-08-27 apareceu
  a `부스터 프로모션` em `prontera 166,300`, da campanha paga de 2021, e o
  `itemInfo` ainda traz a Moeda Booster com um `<NAVI>` para exatamente aquela
  célula. **107 das 514 têm texto, boa parte ainda em coreano** — o
  `traduz_ptbr.py` nunca tocou esse arquivo. É a §4.9 num terceiro grau: lá o
  cliente tinha metade da configuração, aqui ele tem as duas.
  Ferramenta: `ferramentas/remove_placas_mortas.py`. **É cliente — vai por
  patch** (§4.18).

- **Ler mojibake a olho num screenshot dá resposta plausível e errada.** No
  balão acima, `°Ô½ÃÆÇ` (게시판, "quadro de avisos") e `ºÎ½ºÅÍ` (부스터,
  "Booster") são o mesmo desenho naquele tamanho — `°`/`º` e `Ô`/`Î` diferem em
  um pixel, e o JPEG come esse pixel. O caminho que decide é mecânico: recortar,
  ampliar em **nearest-neighbor**, **binarizar por luminância** para tirar o
  ruído de JPEG, transcrever com alternativas para os glifos ambíguos e
  **decodificar por força bruta** — a combinação que der Coreano com sentido é a
  resposta. E quando uma palavra fecha, **procurar essa palavra pelo cliente**:
  foi o contexto do arquivo, não o print, que derrubou a leitura errada.
