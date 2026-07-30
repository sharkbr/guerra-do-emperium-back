# Pendências — Guerra do Emperium

Registrado em 2026-07-29/30. **A v1 está de pé:** dá para logar e jogar. A seção
0 conta como o cliente foi destravado e serve de referência quando ele voltar a
quebrar; o resto são coisas deliberadamente deixadas para depois.

> Este arquivo é versionado, então **nunca colar senha real aqui.** As senhas
> reais vivem em `rathena/conf/import/`, que está fora do git.

---

## 0. V1 ALCANÇADA — dá para logar e jogar

**2026-07-30, ~16:19.** Personagem **Abernus** (Novice, Base Lv.1) criado e
**dentro do mapa**. A cadeia inteira está provada de ponta a ponta:

```
cliente → login-server → autenticação → char-server → map-server → mapa
```

A interface aparece **em inglês** — a tradução do ROenglishRE está funcionando.

### O pincode

No primeiro login o char-server pede para **criar** um pincode. Não é bug e
ninguém cadastrou: é o padrão do rAthena (`pincode_enabled: yes` e
`pincode_force: yes` em `conf/char_athena.conf`), com a coluna `pincode` da conta
vazia. Clicar 4 dígitos com o mouse — o teclado embaralha as posições de
propósito, é anti-keylogger. **Não** aceita repetidos (`1111`, por
`pincode_allow_repeated: no`) nem sequenciais (`1234`, por
`pincode_allow_sequential: no`).

Para tirar essa fricção do fluxo de teste: pôr `pincode_enabled: no` em
`conf/import/char_conf.txt` (hoje o arquivo não menciona pincode) e reiniciar o
char-server.

### Histórico — como o cliente foi destravado

Tudo abaixo é registro do que custou a sessão de 2026-07-30. O padrão se repete,
então vale reler antes de mexer no cliente de novo.

### O que está montado

| Peça | Estado |
|---|---|
| Pasta do cliente | `C:\GuerraDoEmperium\cliente` |
| Executável em uso | `GuerraDoEmperium.exe` (12,6 MB) — saída do WARP |
| Entrada do WARP | `Ragexe_unpacked.exe` (12,3 MB), do NEMO, desempacotado |
| Backup do oficial | `Ragexe.exe.original` (7,3 MB) — blindado, inútil para patch |
| Dados | `data.grf` 3,0 GB, oficial da Gravity, SHA256 conferido |
| `data\` | ROenglishRE + nosso `clientinfo.xml`; 4 `.lub` removidos (ver histórico) |
| `SystemEN\` | pasta **irmã** de `System\`, 12 arquivos (25 MB) com `LuaFiles514\` |
| `navigation\` | + `Addons\Navigation Legacy` (18 arquivos, 5,3 MB) |
| `DATA.INI` | `0=data.grf` (não usar o do ROenglishRE: ele pede `server.grf`) |
| Patches aplicados | 33, registrados em `WARP-rock_win32/LastSession.yml` |
| `PACKETVER` | 20211103, em `rathena/src/custom/defines_pre.hpp` |
| Vídeo | configurado via `Setup.exe` como admin, adaptador NVIDIA |
| Backup dos `.lub` removidos | `C:\GuerraDoEmperium\_backup_luafiles_roenglish\` |

Executável desempacotado: SHA256 `3f11ce8584e98834391fdb03a24ecfce420d0c84d5839f958713d0cb1c3baa35`,
build `2021-11-03 07:29 UTC` (timestamp 1635924593).

### Cadeia já resolvida — não reinvestigar

Cada item abaixo custou tempo. Estão resolvidos:

1. **O `Ragexe.exe` oficial da Gravity é blindado com WinLicense/Themida.** Seções
   PE `.winlice` e `.boot` + 5 sem nome. O WARP não consegue lê-lo e falha em
   *todos* os patches, com erros que parecem não relacionados
   (`LANGTYPE - 'america' not found`, `No known HardCoded IPs available`) e faz
   patches desaparecerem da lista. **Solução:** usar o exe desempacotado do NEMO.
2. **Descasamento `_sak` vs `_true`.** O exe (linhagem RagexeRE) procura
   `System\*_sak.lub`; o instalador main entrega `*_true.lub`. Criamos 8 cópias
   em `System\`: `itemInfo_sak`, `mapInfo_sak`, `PetEvolutionCln_sak`,
   `PrivateAirplane_sak`, `PrivateAirplane_Sakray`, `OngoingQuestInfoList_sak`,
   `RecommendedQuestInfoList_sak`, `monster_size_effect_sak_new`.
3. **`MsgStrID` nil quebrando dezenas de scripts Lua.** A definição está em
   `data\luafiles514\lua files\msgstring_kr.lub`, que o cliente kRO oficial não
   traz. Vem do ROenglishRE — já copiado.
4. **`clientinfo.xml`:** `langtype` é **0** (não 1) e a tag de GM é **`<aid>`**
   (não `<yellow>`, que é antiga). Corrigido conforme o modelo do ROenglishRE.
5. **`PACKETVER`:** o rAthena trata a janela 20211103–20211118 como uma geração
   única (todas as condições são `>= 20211103`, sem limite intermediário).
6. **Os luafiles do ROenglishRE são novos demais para o nosso cliente.** O repo
   mira o cliente mais recente (HEAD de 2026-07-08); nosso exe/GRF é 2021-11-03.
   Cada `.lub` traz um comentário `-- Last updated: AAAAMMDD` — dá para conferir
   a data extraindo strings do bytecode. Arquivos que **referenciam conteúdo
   inexistente no GRF de 2021** quebram. Foi a causa única dos 8 erros de Lua de
   2026-07-30 (ver abaixo).

### Rodada de 2026-07-30, ~12:35 — os 8 erros de Lua

O cliente passou a **abrir e executar Lua** (avanço grande: não é mais falha de
boot). Apareceram 8 diálogos de erro em sequência, todos com a mesma causa:
arquivos do ROenglishRE de 2024–2026 sobre um GRF de 2021-11-03.

| # | Onde | Mensagem |
|---|---|---|
| 1 | `DataInfo\PetInfo` | `[string "buf"]:118: table index is nil` |
| 2 | `StateIcon\StateIconInfo` | `[string "buf"]:6801: table index is nil` |
| 3 | `Navigation\Navi_f_krSak` | `cannot open SystemEN/Navi_Data.lub` |
| 4,8 | `querymaptable_load` | `worldviewdata_f.lua:23: attempt to index local 'table' (a nil value)` |
| 5 | `Error` | `querymaptable_load // WorldMap_Pw02 Line 3 읽기 실패` |
| 6 | `queryfieldtable_load` | `worldviewdata_f.lua:35: attempt to index local 'table'` |
| 7 | `Error` | `queryfieldtable_load // WorldMap_Pw02_Dun Line 3 읽기 실패` |
| 9 | `Error` | `querymaptable_load // worldtable_Isgard Line 9 읽기 실패` |

`읽기 실패` = "falha de leitura". A prova: `worldviewdata_list.lub`
(`Last updated: 20250416`) lista `WorldMap_Pw02` e `worldtable_Isgard`, mapas de
episódios de 2023–2025 que **não existem** no GRF de 2021. O loader não acha,
a tabela vira nil, e a linha 23 estoura.

**O que foi feito:**

1. Movidos para `C:\GuerraDoEmperium\_backup_luafiles_roenglish\` (fora do
   cliente, para reverter fácil) — o GRF volta a fornecer a versão de 2021:
   - `datainfo\petinfo.lub` (2025-10-08)
   - `stateicon\stateiconinfo.lub` (2026-03-22)
   - `worldviewdata\worldviewdata_list.lub` (2025-04-16)
2. Criada a pasta `C:\GuerraDoEmperium\cliente\SystemEN\` com `Navi_Data.lub`
   (214 KB, de `Translation\Renewal\SystemEN\`). **Correção de um erro do plano
   anterior:** `SystemEN` é uma pasta **irmã** de `System\`, não o conteúdo dela.
   O `navi_f_krsak.lub` faz literalmente `dofile("SystemEN/Navi_Data.lub")`.
   Copiar por cima de `System\` não resolveria nada.

Mantido `worldviewdata_language.lub`: é só a tabela passiva `WORLD_MSGID`
(chave → nome do mapa em inglês), sem indexar conteúdo novo.

**Custo:** nomes de pets, de ícones de status e do mapa-múndi voltam ao coreano.
Só isso — o resto da tradução (itens, habilidades, texturas) continua de pé.

### Rodada de 2026-07-30, ~13:07 — a instalação do ROenglishRE estava incompleta

Sobraram erros, mas de outra natureza: **não era versão descasada, era instalação
pela metade.** Copiamos o `data\` do ROenglishRE e **nada** do `SystemEN\`.

| Erro | Causa |
|---|---|
| `queryNavi_MapInfo: attempt to index global 'Navi_Map' (a nil value)` | faltavam as 8 tabelas de dados de navegação |
| `SignBoardList_F: module 'SystemEN/LuaFiles514/rotp_f' not found` | faltava a subpasta `SystemEN\LuaFiles514\` |

O volume de diálogos engana: o `navi_f_krsak.lub` tem ~12 funções `queryNavi_*`
e **cada uma estoura em separado** pelo mesmo `Navi_Map` nil. "Muitos erros" era
essencialmente **um arquivo**.

**O que foi feito — as duas correções são aditivas, sem perder tradução:**

1. Copiado o `SystemEN\` **inteiro** (12 arquivos, 25 MB, com a subpasta
   `LuaFiles514\`) de `Translation\Renewal\SystemEN\`. Antes só tinha sido
   copiado o `Navi_Data.lub` avulso — erro meu, ignorei que a pasta tem subpastas.
2. Copiado `Addons\Navigation Legacy\*.lub` (5,3 MB) para
   `data\luafiles514\lua files\navigation\`. Esse addon existe exatamente para
   clientes antigos como o nosso, e define as 8 tabelas que o `navi_f` consome:
   `Navi_Map`, `Navi_Npc`, `Navi_Mob`, `Navi_Link`, `Navi_Distance`,
   `Navi_NpcDistance`, `Navi_Scroll`, `navi_picknpc`.

Detalhe que confundiu: a pasta `NavigationData\` do cliente **não** guarda os
dados de navegação — tem só um `.txt` coreano. Os dados são `.lub` e vivem em
`data\luafiles514\lua files\navigation\`.

### Rodada de 2026-07-30, ~13:17 — a janela do jogo abriu

Restou **um** erro de Lua, e ele caiu no padrão já conhecido:
`DataInfo\AddRandomOptionNameTable → attempt to index field '?' (a nil value)`,
de `addrandomoptionnametable.lub` (`Last updated: 20251008`). Movido para o
backup, como os outros.

Depois dele **a janela do jogo abre**, e aí vem:

```
Cannot init d3d OR grf file has problem.
```

**Não é o GRF** — a mensagem é genérica ("d3d **OU** grf"), e o GRF já se provou
legível ao servir os Lua. É a **configuração de vídeo, que nunca foi feita**:

- `C:\GuerraDoEmperium\cliente\savedata\` está **vazia**;
- em `HKLM\SOFTWARE\WOW6432Node\Gravity Soft\Ragnarok` existem os valores de
  **som** (`SOUNDMODE`, `SPEAKERTYPE`…) mas **nenhum de vídeo** — `WIDTH`,
  `HEIGHT`, `BITPERPIXEL` e `ISFULLSCREENMODE` estão todos ausentes;
- `GUIDDEVICE` e `GUIDDRIVER` são 16 bytes zerados = nenhum adaptador D3D
  escolhido. O cliente tenta criar o dispositivo com GUID nulo e falha.

**Solução:** rodar `Setup.exe` (1,6 MB, na raiz do cliente) **como
administrador** — as chaves ficam em HKLM, e sem elevação ele não grava.
Escolher o adaptador, a resolução e preferir **modo janela** no primeiro teste.

Plano B, se o `Setup.exe` não gravar: criar as chaves à mão. Com
`ISFULLSCREENMODE = 0` e `WIDTH`/`HEIGHT` definidos, o cliente costuma aceitar o
adaptador padrão mesmo com os GUIDs zerados.

### Rodada de 2026-07-30, ~13:22 — O CLIENTE ABRE

Com o adaptador NVIDIA escolhido no `Setup.exe`, o `Cannot init d3d` sumiu e **o
cliente abre**. Sobrou **um** diálogo, e dando OK nele o jogo segue:

```
RecommendedQuestInfoLoad
.../data/LuaFiles514/Lua Files/Datainfo/QuestInfo_f.lua:57:
bad argument #1 to 'pairs' (table expected, got nil)
```

**Não bloqueia** — é a lista de "quests recomendadas", recurso de UI secundário.
Decidido seguir e validar a cadeia cliente↔servidor primeiro.

O que já foi descartado: os três `System\RecommendedQuestInfoList*.lub`
**contêm** as strings `RecommendedQuestInfoList` e `QuestInfo1`, então o arquivo
está lá e não está vazio. A hipótese que sobra é que o `QuestInfo_f.lua:57` (que
vem do GRF) itere uma tabela **aninhada** que a nossa versão do arquivo não
preenche — ou que o `_sak` que criamos por cópia do `_True` não seja o par certo
para este exe. Investigar só se incomodar.

### Estado dos 23 `.lub` do ROenglishRE ainda ativos

Varredura de datas (extraindo `-- Last updated:` do bytecode). **Nenhum é de
2021** — todos são candidatos a quebrar, mas só quebram os que indexam por
constante ausente ou dirigem carregamento. Tabelas passivas de strings passam:

| Data | Arquivos |
|---|---|
| 2026 | `msgstring_kr*` (2), `signboardlist_f`, `skillinfoz\skilldescript`, `skillid`, `skillinfolist` |
| 2025 | `datainfo\addrandomoptionnametable`, `optioninfo\cmdinfo`, `skilltreeview`, `worldviewdata_language` |
| 2024 | `navigation\navi_f_*` (2), `hateffectinfo`, `service_korea\ExternalSettings_kr*` (2) |
| 2023 | `agit\agitconfig`, `battlefield\battlefieldinfo`, `datainfo\helpmsgstr`, `titletable`, `dressroom\*` (2), `entryqueue\entryqueuelist`, `optioninfo\optioninfo` |

### Se o cliente voltar a dar erro de Lua

O remédio é quase sempre o mesmo: conferir o `-- Last updated:` do `.lub` e, se
for muito posterior a 2021-11, mover para o backup. Candidatos que ainda podem
quebrar: `skillinfoz\*`, `hateffectinfo`, `datainfo\titletable`,
`dressroom\jobdresslist`.

Outras pistas guardadas, se um dia forem úteis:

- Se o cliente abrir mas não achar o servidor: revisar se o `DataFolderFirst`
  está ativo no `LastSession.yml` — é ele que faz `data\` vencer o GRF.
- Se `System\tipbox.lua` reclamar: existe só `tipbox.lub`. Não copiar bytecode
  com extensão `.lua` sem testar — pode piorar.
- O `msgstringtable.txt` do ROenglishRE (4022 linhas) forma par com o patch
  `MsgStrings`, que foi **removido** numa rodada anterior. Agora que o arquivo
  existe, o patch pode voltar.
- Se o coreano que sobrou incomodar, a saída de fundo é clonar o ROenglishRE
  **completo** (`git fetch --unshallow` — hoje é clone raso, 1 só commit) e fazer
  checkout de um commit de ~novembro/2021. Caro em download.

### Pendência conhecida, não bloqueia

O diálogo `RecommendedQuestInfoLoad` aparece a cada abertura do cliente. É a
lista de "quests recomendadas", puramente cosmético. O que já foi descartado
está na rodada das ~13:22.

### Armadilhas de ferramenta deste ambiente

Estas produziram diagnósticos falsos e custaram retrabalho:

- **`strings` não existe** no Git Bash daqui. Com `2>/dev/null` ele falha calado e
  parece retornar zero resultados. Usar PowerShell com
  `[Text.Encoding]::GetEncoding(28591)` + regex.
- **`[Text.Encoding]::Latin1` não existe** no PowerShell 5.1 (só .NET Core). Dá
  `$null` e todo resultado derivado é lixo. Usar `GetEncoding(28591)`.
- **`Get-ChildItem -Include`** sem caminho com curinga retorna vazio. Usar
  `Get-ChildItem "dir\*.ext"`.
- **`source` do mysql.exe** quebra com barras invertidas (`\U` = comando
  desconhecido). Usar barras normais no caminho.
- **`.lub` é bytecode**, não texto: `Select-String` não acha strings dentro deles
  de forma confiável. Buscar em binário.

### Ferramentas instaladas nesta sessão

- Visual Studio 2022 Community 17.14.37 (workload C++)
- Python 2.7.18 em `C:\Python27` — só para o `get4.py` do NEMO
- WARP 1.5.3 em `C:\Users\User\Downloads\WARP-rock_win32`
- ROenglishRE clonado em `C:\Users\User\Downloads\ROenglishRE`
- Instalador kRO em `C:\Users\User\Downloads\RAG_SETUP_211105.exe` (3,19 GB,
  SHA256 `d9067cc9ac62c85fa599ac94bbb19e9e96a1b7529181252806dc1df49e0293aa`)

---

## PRÓXIMO PASSO — comandos `@`

Ponto de partida da próxima sessão. No teste da v1 apareceram no chat:

```
@ml is Unknown Command.
@wlup is Unknown Command.
```

**Não é problema de permissão.** A conta `teste` é `group_id 99` = grupo `Admin`
em `conf/groups.yml`, com `command_enable: true`. "Unknown Command" quer dizer
que o comando **não existe** — falta de permissão dá outra mensagem. `@ml`,
`@wlup`, `@lvup` e `@levelup` não existem no rAthena.

**Onde está a verdade:**

| O quê | Onde |
|---|---|
| Referência completa | `rathena/doc/atcommands.txt` (1235 linhas) |
| Implementação | `rathena/src/map/atcommand.cpp` (302 comandos) |
| Permissões por grupo | `rathena/conf/groups.yml` (grupo 99 = `Admin`) |

**Dentro do jogo:** `@commands` lista o que a sua conta pode usar, e
`@help <comando>` explica um específico. É o caminho mais rápido e não depende
de documentação externa desatualizada.

Comandos conferidos neste repo (existem de fato):

| Uso | Comando |
|---|---|
| Nível de base / de classe | `@blvl <±n>`, `@jlvl <±n>` |
| Mudar de classe | `@jobchange <classe>` — **`@job` não existe** |
| Todos os atributos no máximo | `@allstats` |
| Itens | `@item <nome/ID> {qtd}`, `@iteminfo`, `@itemreset`, `@storage` |
| Mover | `@warp <mapa> {x y}`, `@go <cidade>`, `@load`, `@save` |
| Monstros | `@monster <nome/ID>`, `@mobinfo` |
| Utilidades | `@heal`, `@zeny <n>`, `@speed <n>`, `@refine`, `@hide`, `@who` |
| Anúncios | `@kami <msg>`, `@broadcast <msg>` |
| Visual | `@mount`, `@size`, `@option` |

Conferidos como **inexistentes**: `@ml`, `@wlup`, `@lvup`, `@levelup`, `@job`,
`@god`, `@die`.

Note que o próprio `@` é configurável (`atcommand_symbol` em
`conf/battle/misc.conf`), e `#` é o prefixo para agir sobre outro jogador
(`@charcommands` lista esses).

---

## Antes de expor o servidor à rede

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

## Higiene, sem pressa

### 6. Não rodar os servidores como administrador

O rAthena avisa: `You are running rAthena with admin privileges, it is not
necessary.` Os três servidores só precisam abrir portas altas (6900, 6121, 5121)
e falar com o MariaDB — nada disso exige elevação. Rodar elevado só aumenta o
estrago de uma falha.

### 7. Reavaliar `db/map_cache.dat` no git

Hoje esse arquivo (3 MB) está **versionado de propósito**, contra a convenção do
brief. O motivo: sem ele o map-server carrega zero mapas, e regerar exige o GRF
do cliente. Com ele, carrega 1265 mapas num clone limpo.

Quando passarmos a gerar o cache a partir do GRF do bRO, o arquivo vira artefato
nosso e começa a mudar a cada geração — aí ele deve sair do git (já existe a
regra `*.mcache` no `.gitignore` esperando por isso).

### 8. Atualizações do rAthena upstream

O `rathena/` foi vendorizado como arquivos comuns, sem o histórico do upstream.
Trazer correção do rAthena hoje é diff manual. Se isso incomodar, a saída é
`git subtree` — mas decidir antes de acumular customização, porque depois fica
mais caro.

---

## Referência rápida

| Item | Onde |
|---|---|
| Credenciais do banco | `rathena/conf/import/inter_conf.txt` (fora do git) |
| Nome do servidor, IPs | `rathena/conf/import/char_conf.txt`, `map_conf.txt` |
| Criação de conta | `rathena/conf/import/login_conf.txt` |
| Schemas | `ragnarok` (jogo), `ragnarok_log` (logs) |
| Usuário do banco | `ragnarok` — sem acesso fora desses dois schemas |
| Portas | 6900 login, 6121 char, 5121 map |
| Versão de cliente alvo | kRO 2021-11-03 (`PACKETVER` padrão do rAthena) |
| Pasta do cliente | `C:\GuerraDoEmperium\cliente` (fora do git) |
| Executável do cliente | `GuerraDoEmperium.exe` |
| Conta de teste | `teste` / `teste123`, `group_id 99`, `account_id 2000000` |
| Personagem da v1 | `Abernus`, Novice Lv.1 |
| Comandos `@` | `rathena/doc/atcommands.txt`; in-game `@commands` e `@help` |
| Config de vídeo do cliente | `Setup.exe` **como admin** (grava em HKLM) |
| `.lub` removidos do cliente | `C:\GuerraDoEmperium\_backup_luafiles_roenglish\` |
| Subir os servidores | `login-server.exe`, `char-server.exe`, `map-server.exe` em `rathena/` |
| Parar os servidores | `Stop-Process -Name login-server,char-server,map-server -Force` |
