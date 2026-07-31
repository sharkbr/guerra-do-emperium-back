# Pendências — Guerra do Emperium

Registrado em 2026-07-29/30. **A v1 está de pé:** dá para logar e jogar, e o
cliente está **em inglês de ponta a ponta**. A seção 0 conta como o cliente foi
destravado e serve de referência quando ele voltar a quebrar; o resto são coisas
deliberadamente deixadas para depois.

**A frente de alterar código começou em 2026-07-30, ~22:00**, com o primeiro NPC
nosso e a convenção de customização definida — ver "CONVENÇÃO DE CUSTOMIZAÇÃO".
A frente de tradução está concluída e vive logo abaixo dela, como referência.

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
(Naquele momento, só parcialmente; foi concluída às ~21:20 do mesmo dia.)

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
| `data\` | ROenglishRE + nosso `clientinfo.xml`; 6 `.lub` removidos e 2 **recortados** (ver histórico) |
| `SystemEN\` | pasta **irmã** de `System\`, 12 arquivos (25 MB) com `LuaFiles514\` + `mapinfo_C.lub` |
| `System\` | `itemInfo_true` e `mapInfo_*` **substituídos pelas versões em inglês**; 2 `_Sakray` criados |
| `navigation\` | + `Addons\Navigation Legacy` (18 arquivos, 5,3 MB) |
| `DATA.INI` | `0=data.grf` (não usar o do ROenglishRE: ele pede `server.grf`) |
| Patches aplicados | 34 — as 33 originais + `MsgStrings`, em `WARP-rock_win32/LastSession.yml` |
| Backup do exe pré-`MsgStrings` | `cliente\GuerraDoEmperium.exe.BACKUP-20260730-2105` |
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

**RESOLVIDO** na rodada de 2026-07-30 ~19:30 — ver abaixo. A hipótese de "tabela
aninhada" registrada aqui estava **errada**: o global inteiro é que estava nil,
porque o exe procura um nome de arquivo que não existia.

### Rodada de 2026-07-30, ~19:30 — `_sak` vs `_Sakray`: o último diálogo caiu

O `RecommendedQuestInfoLoad` sumiu. **A causa não era conteúdo, era nome de
arquivo.**

Como foi diagnosticado (o método vale mais que o resultado):

1. Extraído `data\luafiles514\lua files\datainfo\questinfo_f.lub` do `data.grf` e
   **desassemblado** (é bytecode Lua 5.1, header `1b 4c 75 61 51`). A linha 57 é
   o laço **externo** — `for _, v in pairs(RecommendedQuestInfoList)`. Ou seja, o
   global inteiro estava nil, não uma tabela aninhada.
2. Desassemblados `System\RecommendedQuestInfoList.lub` e `_sak.lub`: os dois
   fazem `SETGLOBAL "RecommendedQuestInfoList"` corretamente. Logo o problema não
   era o conteúdo — era o arquivo nunca ser carregado.
3. Extraídas as strings do `GuerraDoEmperium.exe` filtrando por `^system[\\/]`.
   O exe pede literalmente **`system\RecommendedQuestInfoList_Sakray`** e
   **`system\OngoingQuestInfoList_Sakray`**.

**A generalização do item 2 da "cadeia já resolvida" estava incompleta.** Não é
que o exe queira `_sak` para tudo: cada arquivo tem o seu sufixo, e só o exe diz
qual. A lista completa do que este exe procura em `System\`:

| Arquivo pedido pelo exe | Sufixo |
|---|---|
| `iteminfo_Sak.lub`, `itemInfo_true.lub` | `_Sak` / `_true` |
| `mapInfo_sak.lub` | `_sak` |
| `monster_size_effect_sak_new.lub` | `_sak_new` |
| `PetEvolutionCln_sak.lub` | `_sak` |
| `PrivateAirplane_Sakray.lub` | **`_Sakray`** |
| `OngoingQuestInfoList_Sakray` | **`_Sakray`** |
| `RecommendedQuestInfoList_Sakray` | **`_Sakray`** |
| `Achievement_list.lub`, `CheckAttendance.lub`, `tipbox.lub`, `Towninfo.lub` | sem sufixo |
| `LuaFiles514\OptionInfo` | sem sufixo |

Criados por cópia das versões `_True` (mesmo pareamento que já funcionava no
`PrivateAirplane`):

- `System\RecommendedQuestInfoList_Sakray.lub`
- `System\OngoingQuestInfoList_Sakray.lub`

**Bônus:** o `OngoingQuestInfoList_True.lub` define o global `QuestInfoList`, que
é consumido por `GetOngoingQuestInfoByID`, `GetCoolTimeQuest`,
`GetOngoingDescription` e `GetOngoingRewardInfo`. Estava nil também — a janela de
quests ia estourar ao ser aberta, mais tarde e sem diálogo no boot.

**Receita, se aparecer outro `.lub` que "existe mas não carrega":** extrair as
strings do exe e conferir o nome exato. Nunca assumir o sufixo por analogia.

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

Conferir o `-- Last updated:` do `.lub`. Se for muito posterior a 2021-11, ele é
suspeito. **Mas mover para o backup é o remédio bruto — ver a rodada da janela de
habilidades abaixo, que estabeleceu um melhor.** Candidatos que ainda podem
quebrar: `hateffectinfo`, `datainfo\titletable`, `dressroom\jobdresslist`.

### Rodada de 2026-07-30, ~22:44 — a janela de habilidades derrubava o cliente

**RESOLVIDO e confirmado in-game às ~23:05:** a janela abre e os nomes das
habilidades aparecem em inglês.

`ALT + S` fechava o jogo com `0xC0000005` (violação de acesso) dentro do
`GuerraDoEmperium.exe`, sem diálogo de Lua. A causa estava nos 4 arquivos de
`data\luafiles514\lua files\skillinfoz\`, todos do ROenglishRE, de **2026-03-22**
(o `skilltreeview` é de 2025-11-16).

**A descoberta que muda a receita: recortar em vez de remover.**

Esses arquivos são tabelas indexadas por constante:

```lua
SKILL_INFO_LIST = {
    [SKID.NV_BASIC] = { SkillName = "Basic Skill", ... },
}
```

Comparando a tabela `SKID` do nosso cliente (do GRF) com a do ROenglishRE:

| | entradas | id máximo |
|---|---|---|
| 2021 (nosso cliente, GRF) | 1788 | 12999 |
| 2026 (ROenglishRE) | 1928 | 12999 |

São só **140 habilidades a mais**, todas de 4ª classe (`ABC_*`, `AG_*`, `AT_*`),
e **nenhuma se perde**. Ou seja: 92% do arquivo servia perfeitamente, e a receita
antiga jogava tudo fora. O que quebra é que `SKID.ABC_ABYSS_FLAME` não existe no
nosso cliente, então `[nil] = {...}` é erro em Lua, o arquivo inteiro aborta, a
tabela nunca é criada, e a janela recebe nil — o que estoura em C++.

Há também **3 constantes com o mesmo nome e id diferente** entre as duas versões
(`ABC_CHAIN_REACTION_SHOT_ATK`, `ABC_FROM_THE_ABYSS_ATK`, `NPC_LAST`). Só por
isso já não vale usar o `skillid.lub` de 2026.

**Como ficou resolvido:**

| Arquivo | Estado | Por quê |
|---|---|---|
| `skillid.lub` | no backup, permanente | é só `nome = número`, **não tem texto para traduzir** |
| `skilltreeview.lub` | no backup, permanente | é só a grade `classe → habilidade`, **idem** |
| `skillinfolist.lub` | **recortado**, 1559 de 1694 entradas | nomes das habilidades |
| `skilldescript.lub` | **recortado**, 1434 de 1546 entradas | descrições |

O recorte é feito por `ferramentas/filtra_lub_por_skid.py`. Originais intactos em
`_backup_luafiles_roenglish\skillinfoz\`.

**Regra que vale para os próximos:** antes de mover um `.lub` para o backup,
perguntar se ele tem texto traduzível. Metade dos arquivos que quebram é tabela
de estrutura ou de constante — perder esses não custa nada, e o GRF os fornece.
Nos que têm texto, recortar por constante conhecida preserva quase tudo.

**Validar sempre o recorte:** além das entradas de primeiro nível, essas tabelas
têm referências aninhadas a `SKID` (os pré-requisitos em `_NeedSkillList`). Uma
única referência órfã traz o crash de volta pelo mesmo caminho.

**Duas correções ao que estava escrito aqui:**

1. **Os `.lub` do ROenglishRE não são bytecode — são Lua em texto puro** com
   extensão `.lub`. O cliente lê os dois. Só os do GRF são bytecode. Logo, dá
   para ler e editar os do ROenglishRE direto, e **comparar tamanho entre GRF e
   ROenglishRE não significa nada** (bytecode contra texto). Eu comecei esta
   investigação por esse caminho e ele não levava a lugar nenhum.
2. **Ler tabela grande de bytecode tem uma armadilha** que produz número
   plausível e errado — ver `ferramentas/LEIAME.md`, seção do `luadis.py`. A
   primeira medição aqui deu "127 habilidades, id máximo 127", o que parecia
   confirmar a hipótese de teto estourado. Era artefato do parser: o real é 1788
   e 12999, e a hipótese estava errada.

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

### Nenhum diálogo de erro pendente

O cliente abre limpo. O `RecommendedQuestInfoLoad` foi o último e caiu na rodada
das ~19:30.

**"Abre limpo" não quer dizer "está tudo certo".** O crash da janela de
habilidades não dava diálogo nenhum: o `.lub` abortava calado no boot, a tabela
global nunca era criada, e o estrago só aparecia ao abrir a janela — como
violação de acesso em C++, sem nada de Lua na tela. Crash duro ao abrir uma
janela específica é sintoma da mesma família de erro de versão, e a ausência de
diálogo não inocenta os luafiles.

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
- **`.lub` do GRF é bytecode**, não texto: `Select-String` não acha strings
  dentro deles de forma confiável. Buscar em binário. **Mas os `.lub` do
  ROenglishRE são Lua em texto puro** — esses dá para ler e editar direto.
  Conferir o header (`\x1bLua`) antes de decidir. Corolário: **comparar tamanho
  de um arquivo do GRF com o do ROenglishRE não significa nada**, é bytecode
  contra texto.
- **Ler tabela grande de bytecode Lua 5.1:** o operando `RK` só endereça
  constante até o índice 255; depois disso o compilador emite `LOADK` num
  registrador e o `SETTABLE` referencia `R<n>`. Um parser que lê só
  `SETTABLE ... ; B="NOME" C=<valor>` captura as ~127 primeiras entradas e
  devolve um número plausível e errado.

### Ferramentas instaladas nesta sessão

- Visual Studio 2022 Community 17.14.37 (workload C++)
- Python 2.7.18 em `C:\Python27` — para o `get4.py` do NEMO e para o
  `ferramentas/` deste repo
- WARP 1.5.3 em `C:\Users\User\Downloads\WARP-rock_win32`
- ROenglishRE clonado em `C:\Users\User\Downloads\ROenglishRE`
- Instalador kRO em `C:\Users\User\Downloads\RAG_SETUP_211105.exe` (3,19 GB,
  SHA256 `d9067cc9ac62c85fa599ac94bbb19e9e96a1b7529181252806dc1df49e0293aa`)

---

## CONVENÇÃO DE CUSTOMIZAÇÃO — decidida em 2026-07-30

A pergunta estava em aberto desde 2026-07-30 ~21:30: o `rathena/` foi
**vendorizado sem histórico do upstream** (ver item 8), então customização nossa
misturada às pastas do rAthena fica **indistinguível de código de terceiros** num
`git diff`, e trazer correção do upstream vira arqueologia.

**A regra, em uma frase: tudo que é nosso mora em pasta própria, e tocamos
arquivo do rAthena só para apontar para ela.**

| Camada | Onde fica o nosso | Marca deixada em arquivo do rAthena |
|---|---|---|
| Scripts de NPC | `rathena/npc/guerra/` | **uma** linha `import:` no fim de `npc/scripts_custom.conf` |
| Código C++ | `rathena/src/custom/` | nenhuma — a pasta já é o ponto de extensão oficial |
| Configuração | `rathena/conf/import/` | nenhuma — idem, e está fora do git |

Como funciona a camada de script: o `map.cpp` lê `npc/re/scripts_main.conf`, que
importa `npc/scripts_custom.conf`, que agora importa
`npc/guerra/scripts_guerra.conf` — o **índice dos nossos NPCs**. `import:` é
recursivo e vale em qualquer conf de NPC (`src/map/map.cpp:4249`), então a cadeia
tem profundidade livre.

Ligar ou desligar um NPC nosso = comentar uma linha no `scripts_guerra.conf`.

Consequências práticas:

- `git diff` restrito a `npc/guerra/`, `src/custom/` e `conf/import/` mostra
  **exatamente** o que é nosso.
- Fora dessas pastas, qualquer diff em `rathena/` é alteração em código de
  terceiros e merece comentário explicando o porquê. Hoje existe **uma**: o
  `import:` no `scripts_custom.conf`.
- Mudança em `conf/` e em script de NPC **não** precisa de recompilação —
  `@reloadscript` in-game basta. Mudança em `src/` precisa (Visual Studio 2022
  Community 17.14.37, já instalado).

### Acentuação no diálogo — não testada

Os NPCs nossos estão escritos **sem acento**, de propósito. O rAthena grava os
próprios arquivos em Latin-1 (o `conf/msg_conf/map_msg_por.conf` tem `ç` como
byte `0xE7`), mas o nosso `clientinfo.xml` usa `langtype 0` (Coreia) e **nunca
testamos** como esse cliente desenha byte acentuado — pode sair caractere coreano
no lugar. Enquanto não houver teste, texto sem acento é o custo baixo.

Para testar: pôr um acento num `mes` e olhar in-game. Se sair certo, gravar os
arquivos em Latin-1 (não UTF-8 — aí cada acento vira dois bytes e sai lixo
garantido).

### NPCs nossos hoje

| NPC | Onde | O quê | Testado |
|---|---|---|---|
| Mestre de Classe | `prontera 160,191` | troca de classe por nível, até a 3ª classe | sim, ~22:40 |

O **Mestre de Classe** (`npc/guerra/mestre_de_classe.txt`) lê a classe em bits
com `eaclass()`/`roclass()` em vez de ter um `if` por classe, então as 6 linhas
clássicas mais Taekwon, Ninja e Justiceiro saem do mesmo código. Exigências no
`OnInit:`, no fim do arquivo — mudar é trocar um `setarray` e dar
`@reloadscript`, sem recompilar.

**Duas exclusões deliberadas, e o motivo importa:**

1. **4ª classe.** Nosso cliente é de 2021-11-03 e a 4ª classe só chegou ao kRO em
   2022-11 — os sprites não existem neste executável. O `npc/custom/jobmaster.txt`
   do próprio rAthena tem `.FourthClass = true` por padrão e ofereceria classe
   que o cliente não sabe desenhar. Foi a razão principal de escrever o nosso em
   vez de só ligar o dele.
2. **Classes Bebê**, que exigem adoção — não existe no servidor ainda.

Se um dia precisar dos dois, ligar o `jobmaster.txt` é o caminho; não reescrever
o nosso.

---

## CONCLUÍDO — tradução do cliente (2026-07-30)

**Estado final: o cliente está em inglês, de ponta a ponta.** Tela de login,
seleção de personagem, janelas do jogo, itens, habilidades, quests, letreiro de
mapa. O único coreano que resta é a arte da tela de classificação etária, que é
imagem, não texto.

A decisão foi **ligar o inglês primeiro** e traduzir para PT-BR depois, arquivo
por arquivo, em cima dessa base. A fase PT-BR não começou.

### A descoberta que destravou tudo

O `msgstringtable.txt` **não existe dentro do `data.grf`.** A tabela inteira (4022
entradas) está **compilada dentro do exe**, em coreano. Confere linha a linha com
o arquivo em inglês do ROenglishRE que já estava em `data\msgstringtable.txt`:

| # | No exe | Em `data\msgstringtable.txt` |
|---|---|---|
| 0 | `동의 하십니까?` | `Do you agree?` |
| 1 | `서버 연결 실패` | `Failed to Connect to Server.` |
| 2 | `서버와 연결이 끊어졌습니다.` | `Disconnected from Server.` |
| 4 | `서버 종료됨` | `Server Closed.` |

O cliente nunca abria esse arquivo porque faltava o patch **`MsgStrings`**. Esse
patch sozinho resolveu a tela de login inteira, os títulos de janela e os
diálogos.

### Onde vive cada texto do jogo — mapa final

| Camada | Arquivo | Como ficou resolvido |
|---|---|---|
| UI e mensagens de sistema | `data\msgstringtable.txt` | patch `MsgStrings` no WARP |
| Quests | `data\questid2display.txt` | já lido por padrão em `langtype 0` |
| Strings cravadas no exe | `WARP\Inputs\Translations_EN.yml` | `TranslateClient`, já aplicado antes |
| Itens | `System\itemInfo_true.lub` | trocado pelo stub do ROenglishRE |
| Letreiro e nome de mapa | `System\mapInfo_*.lub` | trocado pela versão em inglês |
| Habilidades | `data\...\skillinfoz\*.lub` | recortados em 2026-07-30 ~22:55 — ver a rodada da janela de habilidades |
| Texturas | `data\texture\유저인터페이스\` | já ativas via `DataFolderFirst` |
| Mensagens do servidor | `rathena\conf\msg_conf\map_msg_por.conf` | PT-BR de fábrica, via `@langtype por` |

**A regra que se repetiu quatro vezes:** quando um texto continua em coreano, o
arquivo traduzido quase sempre **já está no disco** — o que falta é o cliente ser
apontado para ele. Antes de traduzir qualquer coisa, confirmar que o cliente
realmente lê o arquivo.

### Pontos de partida para a fase PT-BR

Nenhum começou. Em ordem de retorno por esforço:

1. **`SystemEN\mapinfo_C.lub`** — mescla `mapTbl_C` por cima do inglês. As cidades
   que importam são ~15 e o efeito é imediato ao entrar no mapa.
2. **`rathena\conf\msg_conf\map_msg_por.conf`** — já pronto, só ativar.
3. **`data\msgstringtable.txt`** — 4022 linhas, a UI inteira. Volume grande.
4. **`SystemEN\itemInfo_C.lua`** — mesma ideia do mapinfo_C, para itens.
5. **`data\...\skillinfoz\skilldescript.lub`** — as descrições de habilidade. É o
   maior volume de texto corrido do cliente (1,0 MB). Fica por último, mas note
   que agora ele é um **arquivo nosso, recortado** — traduzir aqui significa
   editar a saída do `filtra_lub_por_skid.py`, então o recorte precisa ser
   refeito antes da tradução, nunca depois.

O estado de cada camada de texto está na tabela "Onde vive cada texto do jogo —
mapa final", acima.

### A camada de textura já está de pé — não confundir com as outras

Texturas **não passam por patch**. Com o `DataFolderFirst` aplicado, o `data\` do
disco vence o GRF direto, então os 502 arquivos que o ROenglishRE instalou em
`data\texture\유저인터페이스\` já estão valendo. É por isso que no diálogo do
`RecommendedQuestInfoLoad` os botões apareciam como `OK` e `cancel` em inglês no
meio de texto coreano: os botões eram BMP do disco, o texto vinha do exe.

Então as camadas têm **três** estados, não dois:

| Estado | Camadas |
|---|---|
| Já ativo, nada a fazer | texturas, habilidades |
| No disco, esperando patch do WARP | msgstringtable, quests, strings do exe |
| Não traduzido | nomes de mapa/monstro do servidor, conteúdo nosso |

**A msgstringtable em inglês tem 0 linhas com coreano remanescente** (4023 de
4023). Logo, o patch `MsgStrings` limpa de uma vez *todo* texto que venha dessa
tabela — não é preciso caçar entrada por entrada. A tela de login inteira está
lá: `[3250] Integrated Account`, `[3411] Save ID`, `[3412] Password`,
`[3413] ID`, `[3414] Sign Up`.

**Lacuna nas texturas do login:** o ROenglishRE entregou só o conjunto antigo
(`btn_back`, `btn_intro`, `btn_request`…). O conjunto novo que este cliente usa
(`bt_join_*`, `bt_start_*`, `bt_otp_*`, `bt_close_*`) não está no disco e cai para
o GRF. Não custa tradução nenhuma — o `bt_join_normal.bmp` é um retângulo vazio de
84×21 e o texto é desenhado por cima pelo cliente. É onde mexer para dar
identidade visual própria ao login.

**Armadilha de medição, registrada porque custou tempo:** `IndexOf` sobre uma
string decodificada de cp949 devolve índice de **caractere**, não byte — offsets
derivados dele ficam deslocados e apontam para lixo. E não adianta tentar derivar
o índice da msgstringtable andando pelas strings do binário: o linker reordena os
literais (no índice 100 o exe tem `파티설정`, enquanto a linha 100 da tabela é
`Information`). O único método confiável é procurar o texto **em inglês** no
`msgstringtable.txt`.

### WARP — RESOLVIDO em 2026-07-30 ~21:15

Backup do exe que funcionava: `GuerraDoEmperium.exe.BACKUP-20260730-2105`.

1. **`MsgStrings`** ("Always read msgstringtable.txt") — **APLICADO**. Foi o que
   destravou tudo: tela de login, títulos de janela, diálogos.
2. **`QuestDisplay`** — **não existe para o nosso caso, e não precisa.** A
   descrição do patch é "load questid2display.txt on all Langtypes (*instead of
   only 0*)" e o nosso `clientinfo.xml` usa `langtype 0`. O cliente já lê o
   arquivo por padrão. Não procurar de novo.
3. **`TranslateClient`** — **já estava aplicado desde a sessão anterior.** Eu tinha
   lido `$translationFile: data: ''` no `LastSession.yml` como "input vazio" e
   concluído errado: `data` vazio é só como o WARP serializa input do tipo
   arquivo. Medição que provou: **122 das 148** traduções do `Translations_EN.yml`
   já estavam gravadas no exe. A prova irrefutável é a string `Item Cmpare`
   presente no binário — um erro de digitação do arquivo do WARP, que não teria
   como existir num exe da Gravity.

Risco de desalinhamento da msgstringtable (arquivo de 2026 sobre exe de 2021):
**baixo**. A tabela é indexada por posição, mas a Gravity **acrescenta** entradas
no fim em vez de inserir no meio, e linhas sobrando nunca são referenciadas. Se
mesmo assim embaralhar, o WARP tem a extensão **"Extract msgstringtable"**, que
extrai a tabela do *nosso* exe com a contagem exata e aceita o
`Inputs\MsgStrMap_EN.yml` (641 KB) como tradução — alinhamento garantido por
construção.

### Feito em ~20:00, sem WARP

- **itemInfo em inglês.** O `CustomItemInfoLub` apontava para
  `System\itemInfo_true.lub`, que era o arquivo **coreano do instalador da
  Gravity** (6,6 MB, 62 mil sinais de coreano). Substituído pelo stub do
  ROenglishRE (`SystemEN\itemInfo.lua`, 3,7 KB), que faz `require` do
  `itemInfo_f` e `dofile` dos 22 MB de `SystemEN\LuaFiles514\itemInfo.lua`.
  Original salvo em `_backup_luafiles_roenglish\System_itemInfo_true.lub.KOREANO`.
  Ajustado `DisplayServer = 0` para não anexar `(kRO)` ao nome de cada item.

### Feito em ~21:20 — o letreiro do nome do mapa

Depois do `MsgStrings`, o único coreano que sobrou foi o letreiro que aparece ao
entrar no mapa (`룬-미드가츠 왕국 수도` / `프론테라`) e o campo MAP na seleção de
personagem. Vem do `System\mapInfo_*.lub`, que era o arquivo coreano do instalador
(8210 sinais de coreano nos dois, `_sak` e `_true`).

Desassemblado: define o global `mapTbl` e uma `main()` que percorre a tabela
chamando `AddMapDisplayName`, `AddMapSignName` e `AddMapBackgroundBmp`. Formato
por mapa:

```lua
["prontera.rsw"] = {
    displayName = "...",              -- o que o /where mostra
    notifyEnter = true,
    signName = { subTitle = "...", mainTitle = "..." },   -- o letreiro
    backgroundBmp = "field"           -- dungeon, field2, field, noname, siege, village
}
```

**Onde estava a versão em inglês:** `ROenglishRE\Translation\Compatibility\`.
Essas pastas com data no nome **não são espelhos completos do cliente** — são
recortes por recurso. A `2021-10-28` (a mais próxima do nosso cliente) só tem
Enchant e ItemReform. O único `mapInfo` em inglês está em **`2019-06-05`**, mas o
conteúdo dele é atual (`Last updated: 20260322`) — é o *formato* que é de 2019.

Instalado por cima de `mapInfo_sak.lub` e `mapInfo_true.lub`; originais em
`_backup_luafiles_roenglish\System_mapInfo_*.KOREANO`.

**Gancho para o PT-BR:** copiado também `SystemEN\mapinfo_C.lub`, um template
vazio que mescla `mapTbl_C` por cima do `mapTbl` via `F_ROTP` (de
`SystemEN\LuaFiles514\rotp_f.lua`, confirmado que a função existe). Dá para
traduzir mapa a mapa **sem tocar** no arquivo grande em inglês — é o melhor ponto
de partida para a fase PT-BR, porque as cidades importantes são poucas.

### A tela de classificação etária (12세 이용가) — parcialmente decifrada

São três peças independentes:

| Peça | Origem | Confirmado? |
|---|---|---|
| Os 2 selos no canto superior direito | `data\texture\유저인터페이스\t_GameGrade.tga`, 207×118 — bate com o tamanho no screenshot | sim |
| O diálogo `동의 하십니까?` | msgstringtable **#0** → cai junto com o patch `MsgStrings` | sim |
| O painel ciano com o texto da lei | não identificado | **não** |

**Busca encerrada — não vale mais tempo.** É uma tela cosmética de um clique de
OK, e o diálogo em cima dela já virou inglês com o `MsgStrings`. O que **já foi
eliminado**, para ninguém refazer:

- os 14 `loading*.jpg` do GRF, nas duas pastas — nenhum tem o painel ciano;
- **todos** os `.jpg` do GRF, sem exceção;
- os arquivos na raiz de `data\texture\`;
- imagens embutidas no exe — os 4 candidatos eram bytes coincidentes, nenhum abre;
- patch do WARP que pule a tela — não existe.

Hipótese testada e **descartada**: plantar uma imagem em
`data\texture\유저인터페이스\loading07.jpg` (o único DES-criptografado e fora da
lista do `clientinfo.xml`) não mudou nada. A sonda foi removida.

Se um dia incomodar, sobra um experimento de uma palavra: trocar
`<servicetype>korea</servicetype>` por `america` no `clientinfo.xml`. Pode
desligar o fluxo coreano inteiro — mas o patch `CallKoreaClientInfo` está
aplicado e força o modo Korea, então a chance é baixa. Reversível numa palavra.

Se alguém quiser retomar: o caminho que sobrou é decifrar as entradas com flag
DES do GRF, que o `ferramentas/grf.py` não lê.

### Ferramentas escritas nesta sessão

Versionadas em **`ferramentas/`**, com uso documentado no `ferramentas/LEIAME.md`:

- **`grf.py`** — extrator de GRF 0x200 em Python 2.7. **Não lê entradas com flag
  DES** (`flags & 6`), que existem às centenas no GRF da Gravity.
- **`luadis.py`** — desassembla bytecode Lua 5.1 mostrando o número de linha do
  fonte. Foi o que resolveu o `QuestInfo_f.lua:57`.

Cuidado com o argv: caminhos com trecho coreano **não sobrevivem** ao console do
PowerShell até o Python. Fazer o match por substring ASCII dentro do script.

---

## Referência — comandos `@`

Levantado em 2026-07-30. No teste da v1 apareceram no chat:

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
| Personagem da v1 | `Abernus` — hoje Swordman, Base 99 |
| Comandos `@` | `rathena/doc/atcommands.txt`; in-game `@commands` e `@help` |
| **NPCs nossos** | `rathena/npc/guerra/`, indexados em `scripts_guerra.conf` |
| Aplicar mudança de script | `@reloadscript` in-game — não precisa recompilar |
| Erro de script de NPC | só na janela do `map-server`; não há arquivo de log |
| Nomes e descrições de habilidade | `cliente\data\...\skillinfoz\skill{infolist,descript}.lub` — **recortados** |
| Textos da UI do cliente | `cliente\data\msgstringtable.txt` (4022 linhas) |
| Textos de quest | `cliente\data\questid2display.txt` |
| Nomes e descrições de item | `cliente\SystemEN\LuaFiles514\itemInfo.lua` (22 MB) |
| Config do itemInfo | `cliente\System\itemInfo_true.lub` (stub do ROenglishRE) |
| Mensagens do servidor em PT-BR | `rathena/conf/msg_conf/map_msg_por.conf`; in-game `@langtype por` |
| Inspecionar GRF e `.lub` | `ferramentas/` (ver `ferramentas/LEIAME.md`) |
| Recortar `.lub` novo demais | `ferramentas/filtra_lub_por_skid.py` |
| Config de vídeo do cliente | `Setup.exe` **como admin** (grava em HKLM) |
| `.lub` removidos e originais | `C:\GuerraDoEmperium\_backup_luafiles_roenglish\` |
| Subir os servidores | `login-server.exe`, `char-server.exe`, `map-server.exe` em `rathena/` |
| Parar os servidores | `Stop-Process -Name login-server,char-server,map-server -Force` |
