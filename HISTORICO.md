# Histórico — Guerra do Emperium

**O que já foi feito, e por quê.** Registro cronológico das decisões, das
tentativas erradas e das armadilhas que custaram retrabalho. É a memória do
projeto: ninguém precisa reinvestigar o que está aqui.

> **Não é ponto de partida e não deve ser lido inteiro.** Comece pelo
> `CLAUDE.md`. Venha aqui **pela seção**, quando precisar do histórico de algo
> específico — as regras que sobreviveram já estão promovidas ao `CLAUDE.md`,
> `ARQUITETURA.md` e `RECEITAS.md`.
>
> O que está **em aberto** vive em `PENDENCIAS.md`. Tabelas de consulta
> (caminhos, portas, comandos, credenciais) vivem em `REFERENCIA.md`.

**Onde escrever:** trabalho terminado entra aqui, com **data absoluta**, ao fim
da seção do assunto. Se a conclusão gerar regra nova ou armadilha nova, ela
**sobe** para o `CLAUDE.md` — este arquivo guarda o porquê, não a regra.

---

## As frentes, e quando cada uma abriu

Registrado em 2026-07-29/30. **A v1 ficou de pé:** dá para logar e jogar. O
cliente foi destravado em inglês e, em **2026-08-03, passou para português** —
ver "CONCLUÍDO — tradução PT-BR". A seção 0 conta como ele foi destravado e
serve de referência quando voltar a quebrar.

**A frente de alterar código começou em 2026-07-30, ~22:00**, com o primeiro NPC
nosso e a convenção de customização definida — ver "CONVENÇÃO DE CUSTOMIZAÇÃO",
que é a decisão fundadora de toda a organização do repositório.

**A frente visual — a temática de cidade destruída — foi aberta em 2026-07-31.**
Vive em arquivo próprio: **`CUSTOMIZACAO-VISUAL.md`**.

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
7. **O rAthena tem um quarto servidor, o `web-server.exe`** — e ele não sobe
   junto se você chamar os `.bat` um a um. Ver "O quarto servidor" abaixo.

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
| `skilltreeview.lub` | no backup, permanente | é a grade `classe → habilidade` — mas **tem texto sim**, ver a correção abaixo |
| `skillinfolist.lub` | **recortado**, 1559 de 1694 entradas | nomes das habilidades |
| `skilldescript.lub` | **recortado**, 1434 de 1546 entradas | descrições |

O recorte é feito por `ferramentas/filtra_lub_por_skid.py`. Originais intactos em
`_backup_luafiles_roenglish\skillinfoz\`.

**Regra que vale para os próximos:** antes de mover um `.lub` para o backup,
perguntar se ele tem texto traduzível. Metade dos arquivos que quebram é tabela
de estrutura ou de constante — perder esses não custa nada, e o GRF os fornece.
Nos que têm texto, recortar por constante conhecida preserva quase tudo.

**CORRIGIDO em 2026-08-03 — o `skilltreeview.lub` TINHA texto.** A linha da
tabela acima dizia que ele era "só a grade `classe → habilidade`". Ele tem
**nove strings**, e são os **títulos das abas** da janela de habilidades —
`노비스·1차직업`, `2차·전승직업`, `3차직업`, `4차직업`, `NV·EX1`, `상위EX1`,
`상위EX2`, `도람족·소환사`, `혼령사`. Como o arquivo foi para o backup, o GRF
voltou a servi-lo, e as abas ficaram em coreano no meio de um jogo em
português — foi o que apareceu no teste.

A regra continua valendo; o que falhou foi a aplicação dela. **"É tabela de
estrutura" não é resposta: tem de olhar o pool de constantes.** Nove strings em
1198 constantes passam despercebidas numa olhada rápida.

Resolvido pelo `traduz_ptbr.py abas`, e por um caminho novo que vale registrar:
a fonte **não é o bRO**, é o **nosso próprio GRF**. A versão do bRO é de um
cliente mais novo e cairia na mesma armadilha de SKID inexistente que motivou a
remoção; a do nosso GRF é a que casa com este exe. Só as nove strings são
trocadas, direto no bytecode — o chunk Lua 5.1 não tem offset absoluto nenhum,
então trocar uma constante por outra de tamanho diferente é seguro (ver
`ptbr.troca_constante`). O resultado é reaberto pelo leitor antes de gravar.

Os títulos saem em **ASCII de propósito** (`Aprendiz-1a`, `2a-Transcend.`,
`Doram-Invocador`, `Espiritualista`): nenhum precisa de acento no vocabulário
do bRO, então eles funcionam mesmo antes do patch de charset.

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


> As armadilhas de ferramenta deste ambiente foram promovidas ao `CLAUDE.md`
> (secao 5), que e o lugar canonico delas. O ambiente instalado esta em
> `REFERENCIA.md`.

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
| Configuração de **regra de jogo** | `rathena/conf/guerra/` | **uma** linha `import:` em `conf/battle_athena.conf` |
| Configuração de **máquina** (senha, IP, nome do servidor) | `rathena/conf/import/` | nenhuma — a pasta já é o ponto de extensão oficial, e está fora do git |

Taxas em vigor, todas em `conf/guerra/battle_guerra.txt`: experiência 10x (base e
classe) e drop 50x. O drop 50x cobre as cinco categorias (comuns, curativos,
consumíveis, equipamentos e cartas) nas três variantes de cada uma — monstro
normal, chefe e MVP —, mais prêmio direto de MVP, drop concedido por equipamento
e baú de castelo. **A taxa é uma só, sem exceção.** O baú (`item_rate_treasure`)
entrou no 50x por decisão de 2026-08-01; ele é o único que **sobrepõe** os outros
modificadores em vez de multiplicar junto, e é recompensa de Guerra do Emperium —
mexer nele mexe na economia da guerra, não no farm de monstro. Carta a 50x sai de
0,01%–0,02% oficiais para 0,5%–1%, ou seja uma a cada 100–200 mortes; se um dia
pesar no equilíbrio, carta e baú são os primeiros a revisar.

A separação entre as duas últimas linhas foi decidida em 2026-08-01, ao subir a
experiência para 10x. `conf/import/` é ignorado de propósito — é lá que moram as
senhas —, então **regra de jogo versionada não cabe ali**: um clone limpo herdaria
o rAthena vanilla. Regra de jogo passa a viver em `conf/guerra/`, importada pelo
`conf/battle_athena.conf`, que é versionado. Como esse `import:` vem **antes** do
`import: conf/import/battle_conf.txt`, o `conf/import` continua tendo a última
palavra e pode sobrescrever qualquer coisa nossa numa máquina específica.

Como funciona a camada de script: o `map.cpp` lê `npc/re/scripts_main.conf`, que
importa `npc/scripts_custom.conf`, que agora importa
`npc/guerra/scripts_guerra.conf` — o **índice dos nossos NPCs**. `import:` é
recursivo e vale em qualquer conf de NPC (`src/map/map.cpp:4249`), então a cadeia
tem profundidade livre.

Ligar ou desligar um NPC nosso = comentar uma linha no `scripts_guerra.conf`.

Consequências práticas:

- `git diff` restrito a `npc/guerra/`, `src/custom/`, `conf/guerra/` e
  `conf/import/` mostra **exatamente** o que é nosso.
- Fora dessas pastas, qualquer diff em `rathena/` é alteração em código de
  terceiros e merece comentário explicando o porquê. Hoje existem **quatro**: o
  `import:` no `scripts_custom.conf`, o `import:` no `battle_athena.conf` e,
  desde 2026-08-06, mais duas.
- A primeira das duas novas: duas linhas em `src/map/clif.cpp` — um `#include`
  e uma chamada a `placa_de_venda_mostra`, dentro do `case BL_NPC` do
  `clif_getareachar_unit`. As duas estão comentadas no arquivo. Esse ponto é
  onde o servidor conta ao cliente o que há sobre a cabeça de um NPC que
  entrou na visão; não há gancho de extensão ali, e pôr a placa em qualquer
  outro lugar significaria ela existir só para quem estava perto no `OnInit` —
  ou seja, para ninguém.
- A segunda: uma linha `!/src/custom/` no fim de `rathena/.gitignore`. **O
  upstream ignora `/src/custom` inteiro**, que é exatamente a pasta que esta
  convenção elegeu para o nosso C++. Sem essa linha, arquivo novo lá dentro não
  aparece nem no `git status` — some calado no próximo clone. Os dois `.inc`
  não denunciavam o problema porque já vinham rastreados do upstream, e
  `.gitignore` não afeta arquivo rastreado. Descoberto ao criar o
  `placa_de_venda.hpp`.
- Mudança em `conf/` e em script de NPC **não** precisa de recompilação. Mudança
  em `src/` precisa (Visual Studio 2022 Community 17.14.37, já instalado).
- Mas **cada `conf/` tem o seu recarregador**, e errar o comando faz a mudança
  parecer que não pegou: script de NPC é `@reloadscript`; `battle_athena.conf` e
  o que ele importa (inclusive `conf/guerra/`) é `@reloadbattleconf`. Na dúvida,
  reiniciar o map-server resolve os dois — login e char podem ficar de pé, o map
  reconecta sozinho.
- Taxa de EXP e taxa de drop **não** se comportam igual. EXP é lida a cada morte,
  então vale assim que a config entra. Drop é aplicada quando o banco de monstros
  é carregado e fica gravada em cada entrada (`src/map/mob.cpp:6890` e `6905`) —
  exige recarregar o mob db. O `@reloadbattleconf` chama `mob_reload()` sozinho
  quando percebe que uma taxa de item mudou (`src/map/atcommand.cpp:4437-4474`).
- Para conferir taxa sem depender de impressão, `@rates` in-game imprime o que o
  servidor tem **carregado na memória** (`src/map/atcommand.cpp:8843`). Medir
  matando monstro engana: a penalidade por diferença de nível distorce o ganho.

### Acentuação — RESOLVIDA em 2026-08-04, com um byte

**Confirmado no jogo.** Todo o texto é cp1252 — cliente, NPCs, `mob_db` e
`item_db` nossos. **Nunca UTF-8**: ali cada acento vira dois bytes e sai lixo
garantido.

O sintoma era específico e vale saber reconhecer: **o acento não sumia, ele
comia a letra seguinte.** `Carvão` → `Carv?`, `Indestrutível` → `Indestrut?el`,
`Lâmina` → `L?ina`. Byte-líder CP949: `0xE3` é lido como início de sílaba
coreana, engole o próximo byte, e o par vira um hanja ou um `?`.

**A correção:** um dword de dados no exe, feito por
`ferramentas/ajusta_charset_fonte.py`. O cliente tem a tabela de charset por
idioma em `.data` (VA `0x00F392D0`), lida num único lugar dentro do
`DrawDC::SetFont`:

```asm
85 ff                  test edi, edi
75 0a                  jnz  +10
a1 d0 92 f3 00         mov  eax, [tabela]          ; índice 0
83 fa 14               cmp  edx, 14h
7d 07                  jge  +7
8b 04 95 d0 92 f3 00   mov  eax, [edx*4 + tabela]  ; índice = langtype
```

A entrada 0 era `0x81` (HANGUL) e passou a `0x00` (ANSI). Um byte. O custo é o
cliente não desenhar mais coreano, o que aqui não custa nada.

#### As três tentativas erradas, e por que cada uma parecia certa

Isto é o que a seção realmente ensina — o acerto foi barato, o caminho não.

1. **`AlwaysAscii`.** Escrevi aqui que ele "troca o charset da fonte de coreano
   para ANSI" e que já estava aplicado. **Falso.** Lendo o `.qjs`, ele anula um
   `jnz` dentro de `CSession::IsOnlyEnglish` — é sobre chat, não encosta em
   fonte. Deduzir função de patch pelo nome custou a primeira rodada.
2. **`CustomFontCharset` = ANSI.** Esse aplicou de verdade: 17 bytes,
   desviando o `call [CreateFontA]` para um cave que força charset 0. E não
   mudou nada, porque o cliente também usa `CreateFontIndirectA` e quem
   alimenta os dois é uma variável, não o argumento daquela chamada.
3. **`FixFontsCharset`.** Era o patch certo em conceito — e **não existe para
   este exe**. O `.qjs` dele só tem `case` para `Exe.Version` 6, 9, 10 e 11
   (VC6 a VC2012); o nosso é VC140 (`MSVCP140.dll`, `VCRUNTIME140.dll`). Cai
   no `throw Error("Function not found")` e o WARP **descarta calado**: o
   binário sai byte a byte igual, só com data de modificação nova.

**A armadilha de diagnóstico que se repetiu duas vezes:** "apliquei e não
mudou" era, nas duas, "não aplicou". Uma vez porque o cliente estava aberto e
o Windows não deixa sobrescrever exe em uso; outra porque o patch não suporta
esta versão. **Conferir o SHA do exe depois de cada rodada de WARP** custa
segundos e teria economizado duas noites — data de modificação nova não prova
nada.

E a pista boa veio do patch que não podia ser aplicado: foi lendo o
`FixFontsCharset.qjs` que apareceu a forma da tabela (`mov eax, [reg*4 +
g_fontCharSet]`, `cmp reg, 14h`), o que permitiu achá-la no nosso binário por
assinatura de conteúdo.

#### O `servicetype brazil` — ficou, mas não era a correção

No meio do caminho o `data/clientinfo.xml` e o `data/sclientinfo.xml` passaram
de `<servicetype>korea</servicetype>` para `brazil`, seguindo o `clientinfo.xml`
que veio de dentro do GRF do bRO (o deles **não tem `<langtype>` nenhum**).
Isso exigiu criar `data/luafiles514/lua files/service_brazil/` com
`ExternalSettings_br.lub` e `_br_s.lub` — cópias dos **nossos** `_kr`, não dos
do bRO, que apontam para servidor e URL deles.

Não foi o que resolveu: a tabela é indexada pelo **langtype**, e o nosso
continua 0. Foi mantido porque está de pé e é o que o bRO faz. Se um dia
atrapalhar, os backups `clientinfo.xml.KOREA` e `sclientinfo.xml.KOREA` estão
ao lado.

#### A saída de emergência continua existindo

Se algum dia o acento tiver de sair, é bandeira e não retrabalho:

```
python ferramentas/traduz_ptbr.py tudo --sem-acento
python ferramentas/ajusta_charset_fonte.py --reverter
```

e desfazer o commit dos `npc/guerra/*.txt`. As bandeiras `--sem-acento` do
`traduz_ptbr.py` e do `completa_iteminfo.py` têm de andar juntas.

### NPCs nossos hoje

| NPC | Onde | O quê | Testado |
|---|---|---|---|
| Mestre de Classe | `prontera 162,191` | troca de classe por nível, até a 3ª classe | sim, ~22:40 |
| Mestre de UP | `prontera 160,187` | +50 de base e de classe, consumindo a Maçã da Inocência | sim, 2026-07-31 |
| Emissário da Ordem | `iz_int 18,32` (e nas 5 cópias do navio) | recebe o novato, entrega a Maçã da Inocência e o leva direto a Izlude | sim, 2026-08-01 |
| Portais do Navio | flutuante, sem mapa | fecha os portais de `iz_int` para o Emissário ser a única saída | sim, 2026-08-01 |
| Mercado Contemporâneo | `prontera`, 9 lojas em grade 3×3 | equipamento por slot, tudo a 1 zeny | **não** |
| Mesmerita | `prontera 144,173` | reseta habilidades, atributos ou os dois — de graça | **não** |
| Funcionária Kafra da praça | `prontera 152,191` | a sexta Kafra de Prontera, a única na praça central | **não** |
| Armazém do Clã | `prontera 149,191` | move e renomeia o `Guild Warehouse Manager` do rAthena | **não** |
| Máquina | `prontera 167,199` | a loja da Moeda Nova: 17 itens em 3 grupos | **não** |
| Xanin | `prontera 172,201` | gato, uma fala | **não** |
| Edgard | `prontera 170,200` | estilista: troca a cor da roupa, de graça e sem limite | **não** |
| Mestre do Refino | `prontera 184,177` | refina com os Pergaminhos, sem chance de quebrar | **não** |

**Os quatro primeiros estão testados in-game e nada ficou pendente neles**
(confirmado em 2026-08-01). O Mercado Contemporâneo é de 2026-08-01 e **ainda
não foi visto no jogo** — ver a seção própria dele, logo abaixo.

O **Emissário da Ordem** (`npc/guerra/emissario_da_ordem.txt`) pula a ilha
(`int_land`) e a Academia: ele é o atalho da introdução até Izlude. Duas coisas
não óbvias sobre ele:

- Ele precisa existir nas **cinco** cópias do navio (`iz_int` e `iz_int01..04`),
  porque o `start_point` do `conf/char_athena.conf` sorteia uma delas. São o
  mesmo navio replicado, não mapas diferentes — não confundir com
  `izlude`/`izlude_a..d`, que são as cópias da *cidade*.
- Ele **não guarda estado em variável**. Quem responde "onde eu parei" é o
  inventário: sem a Maçã a conversa recomeça do zero, com a Maçã ela pula para a
  última fala e embarca. Isso também é o que impede uma segunda Maçã.
- Ele exibe um **retrato** (`cutin "3rd_rune_knight",2`), o primeiro do
  servidor. O cutin **não some sozinho** quando o diálogo fecha — fica na tela
  do jogador até outro NPC trocá-lo. Por isso toda saída do script limpa com
  `cutin "",255`, e por isso o guarda de peso usa `close2` em vez de `close`:
  depois de `close` não roda mais nada e a limpeza nunca aconteceria. Ver
  `CATALOGO-CUTINS.md` para o acervo e a pasta certa dentro do GRF.

O destino é a `izlude` principal, de propósito — é o `.rsw` dela que a frente
visual altera. Mandar para uma variante entregaria a cidade intacta, e a fala do
NPC menciona os muros destruídos.

O **Portais do Navio** (`npc/guerra/portais_do_navio.txt`) é o que faz do
Emissário a *única* saída. O navio são dois blocos andáveis sem caminho a pé
entre eles — cabine (onde o novato nasce, com o Emissário) e convés —, então
fechar o portal de `27,30` já isola o convés inteiro e, com ele, a saída do mapa
em `56,15`.

**Armadilha ao depurar:** quem abrir `npc/re/warps/cities/izlude.txt` vai ler os
três portais de pé e não vai bater com o navio do jogo. O fechamento é feito de
fora, com `disablenpc`, para deixar os arquivos do rAthena byte a byte iguais ao
upstream — mesma decisão do `sprite_teletransportadora.txt`.

Duas escolhas dentro dele que merecem registro:

- O `#room_in` (`47,30`, convés → cabine) fica **aberto de propósito**. Ele não é
  saída do mapa: leva de volta ao Emissário. Ninguém deveria chegar ao convés,
  mas quem chegar (warp de GM, mudança futura) volta por ele. Fechar os três
  deixaria mais "limpo" e criaria uma armadilha.
- O `#intro_start` (o NPC de dicas do rAthena) foi fechado junto, porque passou a
  mentir: ele chama `navigateto` para `52,30`, no convés, e anuncia "you can
  leave through the bluish warp gate". O custo são as duas dicas que continuavam
  válidas (clicar no chão para andar, arrastar para girar a câmera). Se um dia
  quisermos só essas duas, o caminho é um NPC nosso, não reabrir aquele.

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

### Três NPCs na praça de Prontera — 2026-08-04, NÃO testados in-game

Pedidos junto com a segunda rodada do mercado. Os três estão em
`npc/guerra/`, listados em `npc/guerra/scripts_guerra.conf`, e cada cabeçalho
tem o detalhe.

**Mesmerita** (`prontera 144,173`) reseta habilidades, atributos ou os dois,
**de graça e sem limite**. O corpo veio da "Reset Girl" do próprio rAthena
(`npc/custom/resetnpc.txt`, que continua desligada e intocada); saíram os
quatro preços e o campo de limite de usos. Duas confirmações antes de
executar, porque reset não tem volta.

O nome foi pedido de memória do bRO — e **a NPC não existe no bRO de hoje**.
Procurei no `navi_npc_br.lub` do GRF (a tabela de NPC por mapa e coordenada,
em português, que é a fonte que este documento aponta para nome de NPC): não
há "Mesmerita" nem "esmerit" como pedaço. Fica registrado para ninguém
refazer a busca. Ela é nossa, com o nome que o dono do projeto lembra.

**Funcionária Kafra da praça** (`prontera 152,191`) é a sexta de Prontera. As
cinco do rAthena estão todas nas **bordas** (`152,326`, `151,29`, `29,207`,
`282,200`, `146,89`) — a praça central, que é onde o jogador deste servidor
passa o tempo, não tinha nenhuma.

É **cópia e não `duplicate()`**, por um motivo só: o `duplicate` traria junto
o `savepoint` da original, que é o portão norte (`157,327`). A NPC diria "seu
ponto de retorno foi salvo aqui" e o jogador renasceria a 140 células dali.
O que é cópia é só a saudação; armazém, carrinho, teleporte e mensagem de fim
continuam saindo por `callfunc` para `npc/kafras/functions_kafras.txt`, então
correção lá — inclusive tradução — alcança esta NPC também.

**Armazém do Clã** (`prontera 149,191`) move e renomeia o
`Guild Warehouse Manager`, que ficava em `150,191`. Feito **de fora**, como o
`portais_do_navio.txt`: `disablenpc` na duplicata de Prontera do rAthena, mais
uma duplicata nossa na coordenada e com o nome novos. O
`npc/re/merchants/guild_warehouse.txt` fica byte a byte igual ao upstream e as
outras ~30 cidades não são tocadas.

Renomear NPC é a parte com risco real (ver "Nomes de NPC", na seção da
tradução): o nome exibido faz parte da chave única, e `duplicate()`,
`enablenpc` e `donpcevent` de outros arquivos referenciam por ele. Aqui foi
seguro porque o alvo é uma **duplicata folha** — conferido que nada em `npc/`
referencia `"Guild Warehouse Manager#prontera"`.

**O diálogo dele continua em inglês**, de propósito: tradução passa pelo
catálogo, não por texto escrito à mão dentro dos nossos arquivos. E o
`guild_warehouse.txt` **não está em grupo nenhum** do catálogo hoje
(conferido em `ferramentas/traduz_npcs.py`, `GRUPOS`). Para fechar:
acrescentá-lo ao grupo `servico`, `--extrair servico`, traduzir os pares novos
e `--aplicar servico`. É arquivo pequeno, ~90 linhas.

### A cena da tenda e o Mestre do Refino — 2026-08-04, NÃO testados in-game

Cinco coisas pedidas juntas: uma tenda, três NPCs em volta dela e o Mestre do
Refino. **A tenda saiu no mesmo dia** — ver abaixo. Os quatro NPCs estão de pé;
**nenhum foi visto no jogo.** O que foi provado é outra coisa — ver "Como foram
conferidos", no fim desta seção.

#### A TENDA FOI REMOVIDA, e a Máquina mudou de lugar

Decisão do dono do projeto poucas horas depois de ela entrar: não ficou boa na
praça. Como ela era **modelo 3D e não NPC**, remover foi apagar um arquivo —
`C:\GuerraDoEmperium\cliente\data\prontera.rsw`. Sem o override, o
`DataFolderFirst` deixa de ter o que servir e o GRF volta a entregar a Prontera
original. Nada mais foi tocado no cliente.

Junto, a **Máquina saiu de `170,197` para `167,199`**, onde fecha a diagonal
com os outros dois, a duas células da quina do quarteirão.

Isso desfez o agrupamento. Os três estavam num arquivo só porque eram **uma
cena em volta da tenda**; sem a tenda, sobrou a razão que era só do Xanin e do
Edgard — a fala de um cita o outro pelo nome. A Máquina passou a arquivo
próprio, que é o **padrão** daqui de qualquer forma (`mesmerita.txt`,
`kafra_da_praca.txt`, `mestre_de_classe.txt`...): juntar é que precisa de
motivo. Então o `tenda_da_praca.txt` virou dois:

| arquivo | quem | onde |
|---|---|---|
| `npc/guerra/xanin_e_edgard.txt` | Xanin, Edgard | `170,200` e `172,201` |
| `npc/guerra/maquina.txt` | Máquina | `167,199` |

**A receita que plantava a tenda continua em `ferramentas/planta_adereco.py`,
comentada**, com o porquê ao lado. Descomentar replanta — não é um TODO
pendente, é registro. A ferramenta em si fica: ela é genérica, se provou, e o
que ela ensinou sobre `.rsw` (altura relativa ao chão, escala espelhada,
`nodename`) vale para o próximo adereço.

**A seção abaixo descreve a tenda que existiu por algumas horas.** Ficou porque
o caminho até ela é o que tem valor — se um dia outro adereço for pedido, é
esta a receita.

#### A tenda era modelo 3D, não NPC — e isso mudou o caminho

O pedido dizia "adicionar uma tenda (sprite)". Não é sprite: em
`moc_ruins 112,127` não há NPC nenhum, e o que está lá são **duas instâncias
espelhadas** do modelo `라헬\상점천막02.rsm` ("tenda de loja", da pasta de
Rachel), a 110,3 e a 114,6 — o ponto 112,127 cai no meio das duas. Vive no
`.rsw`, que é arquivo de **cliente**.

Três detalhes que um "planta o `.rsm` na coordenada" teria perdido, e que por
isso viraram o projeto da ferramenta nova:

- **a altura é relativa ao chão.** A tenda está a `y=-2,5` num chão de `-4,0`:
  1,5 afundada de propósito. O que se copia é o afastamento, não o `y`
  absoluto. Em Prontera, chão `+1,0`, ela foi para `+2,5`.
- **uma das metades tem `escala.x = -0,8`** — é a outra espelhada. Copiar
  `1,0` entregaria duas metades viradas para o mesmo lado.
- **o `nodename` é `RC_sr005`.** O `Modelo.novo` do `rsw.py` deixa esse campo
  vazio e o comentário dele avisa que isso é **não verificado**. Copiando, a
  dúvida não se aplica.

Daí a ferramenta nova, `ferramentas/planta_adereco.py`: a receita não descreve
a peça, ela **aponta para onde a peça está** ("vai em `moc_ruins 112,127`, pega
o que tiver esse `.rsm`, põe igual em `prontera 168,199`"). O `edita_mapa.py`
não servia — ele é a frente de destruição, tem semente e sorteio, e **recusa
rodar em Prontera** por decisão de ficção. Relaxar aquele guarda para caber um
adereço seria estragar o motivo de ele existir.

Duas armadilhas do caminho, as duas de ferramenta e não de conteúdo:

1. **No nosso `data.grf` o `moc_ruins.rsw` está com flag DES**, que o `grf.py`
   não lê (o de Prontera não está). O mapa de origem sai do **GRF do bRO**, onde
   ele é `flags=1`. Mesmo tamanho de arquivo, 141758 bytes.
2. **O `verificar()` do `rsw.py` compara contra os bytes de entrada**, então só
   vale *antes* de mexer. Depois de mexer a prova possível é outra: reabrir a
   saída, conferir a contagem de objetos e a quadtree fechando no byte exato. O
   `planta_adereco.py` faz as duas.

Instalado em `C:\GuerraDoEmperium\cliente\data\prontera.rsw` (1484 → 1486
objetos). Conferido que **nenhum dos 1484 objetos preexistentes mudou um byte**
e que a quadtree é idêntica. **Apagar o arquivo reverte** — o original nunca
saiu do GRF.

**O `.rsw` não tem colisão.** Quem manda em passagem é o `.gat`, que não foi
tocado, então o jogador **atravessa a tenda**. Fechar a passagem seria mexer no
`.gat`, que o servidor também lê, e é decisão de outra ordem.

#### Os três NPCs

| NPC | Onde | Sprite | O quê | arquivo |
|---|---|---|---|---|
| Xanin | `172,201` | 495 `4_M_MERCAT1` | uma fala, sem função | `xanin_e_edgard.txt` |
| Edgard | `170,200` | 509 `4_ELEPHANT` | cor de roupa | `xanin_e_edgard.txt` |
| Máquina | `167,199` | 564 `2_VENDING_MACHINE1` | loja da Moeda Nova, desde 2026-08-07 | `maquina.txt` |

**`4_ELEPHANT3` não existe.** O pedido dizia "4_ELEPHANT3 ID: 509"; o ID está
certo e o nome não. Neste cliente 509 é `4_ELEPHANT`, e não há `4_ELEPHANT2`
nem `4_ELEPHANT3` — procurados por `.spr` e por `.act` no nosso `data.grf` e no
do bRO. Nas duas instalações há **um** elefante.

**O estilista não precisou de trabalho de sprite, e o porquê importa:** cor de
roupa não é sprite, é **palette**. O sprite do personagem é indexado, e o
cliente troca a tabela de cores por um `data\palette\몸\*.pal` que ele já tem;
o servidor só manda o número, com `setlook LOOK_CLOTHES_COLOR`.

Quantas cores existem de verdade, contando os 1809 `.pal` de corpo do nosso
GRF por classe e gênero:

| classes | índices |
|---|---|
| base (Aprendiz, Espadachim, Mago, Arqueiro, Noviço, Mercador, Gatuno) | 0..4 |
| 2ª e 3ª classes | **0..3** |
| parte das classes novas (4ª) | 0..7 |

Por isso o teto do Edgard é **3**, e não o `max_cloth_color: 7` do
`conf/battle/client.conf`. Aquele número é do **servidor**, e o servidor aceita
qualquer índice e manda para um cliente que pode não ter a palette. **Índice sem
palette não dá erro** — o cliente desenha a cor padrão, e a conclusão errada é
achar que o NPC falhou. É a mesma armadilha do view id de NPC, uma camada
adiante. Mudar o teto é trocar um número no `OnInit`.

#### Mestre do Refino — a NPC já existia, em inglês e desligada

`npc/re/merchants/ticket_refiner.txt`, o "Refine Master" do próprio rAthena.
Três coisas batem com o bRO e fecham a identificação: mapa `prontera`,
coordenada `184,177` e sprite `851`. O nome em português saiu do
`navi_npc_br.lub` do GRF do bRO, que é a fonte que este documento manda usar
para nome de NPC.

Vinha **desligado** no rAthena (`npc/re/scripts_athena.conf:174`, comentada —
"This NPC is currently disabled on official servers"). Foi ligado pelo nosso
`scripts_guerra.conf`, e não descomentando aquela linha, como no `warper.txt`.
O renomear é de fora, `disablenpc` + duplicata nossa, como no
`armazem_do_cla.txt`. **A ordem das duas linhas no `scripts_guerra.conf`
importa**: o `ticket_refiner.txt` tem de vir antes, senão o `duplicate` não acha
o original e a NPC não nasce.

Ele refina com os **Pergaminhos** (`Pergaminho de Arma +N` /
`Pergaminho de Armadura +N`, nomes lidos do `iteminfo` do bRO), sem chance de
quebrar, levando a peça direto ao nível do pergaminho. **Nenhum NPC nosso vende
pergaminho** — hoje eles só entram por `@item`.

Diferente do Armazém do Clã, **o diálogo deste foi traduzido**, pelo caminho que
aquele deixou escrito: arquivo no grupo `servico`, `--extrair`, traduzir,
`--aplicar`. 82 falas.

#### Duas correções no `traduz_npcs.py`, e a primeira é um estrago evitado

**1. `--extrair` num grupo já aplicado apagava o catálogo.** A extração lia o
arquivo **vivo** do rAthena. Depois de um `--aplicar`, aquele arquivo está em
português — então a linha `-`, que é a **trava** contra mudança do upstream,
passava a guardar a *tradução*, e a linha `+` saía vazia. Um
`--extrair servico` esvaziou **595 pares** de uma vez. O `git checkout` desfez.

O que faz isso perigoso é não dar erro: ele imprime `595 mudaram no upstream`,
que parece informação e é o relatório do estrago. A correção é uma linha — a
fonte passa a ser o `.INGLES` quando ele existe, que é justamente o backup que
o `--aplicar` deixa. Depois dela, o mesmo comando: `714 já traduzidos, 0
mudaram no upstream`.

**2. Contexto `atrib` — a palavra que ficava metade em inglês.** O
`ticket_refiner.txt` guarda "Weapon"/"Armor" em `.@type$` e **interpola** em
três frases de `mes`. O catálogo só extraía literal em contexto de exibição
(`mes`, `select`, `setarray`...), e atribuição não era um. O resultado seria
"Para refinar esta ^006400**Weapon**" — sem erro nenhum para denunciar.

É exatamente o **token interno** que a doutrina de `tokens_intocaveis` já mandava
traduzir: nasce e morre no arquivo, e o único destino dele é a tela. Ficou
"Arma" e "Armadura", que é como os pergaminhos se chamam no bRO — e as duas são
femininas, então "esta ..." e "sua reluzente ..." servem para os dois casos.

O custo foi **medido antes de ligar**: +54 pares nos dez catálogos (campal 14,
guerra 17, kafra 12, servico 11, o resto zero), todos nascendo **vazios**, e
vazio quer dizer "deixa em inglês". Os índices não andam: eles contam *todos* os
literais, e o comentário do `literais_todos` diz que isso é de propósito,
justamente para a lista de contextos poder crescer. Era o ponto de extensão
previsto.

#### Como foram conferidos, já que não houve teste in-game

Vale mais que o resultado, porque dá para repetir. Os servidores estavam no ar e
**não foram tocados**: subir um segundo map-server que se registre no
char-server faria o char derrubar o primeiro e cair quem estivesse jogando. A
saída foi uma conf de checagem que importa a real e depois aponta o
`char_port` para uma porta morta:

```
import: conf/map_athena.conf
char_ip: 127.0.0.1
char_port: 1
map_port: 15121
```

```
./map-server.exe --run-once --map-config <a conf acima>
```

O `--run-once` carrega tudo e sai. Resultado: **24244 NPCs, nenhum erro de
parse**, e nenhum `debugmes` das travas de `OnInit` disparou — o que prova que
o `disablenpc "Refine Master"` achou o alvo.

Depois disso, uma **sonda temporária** (um NPC flutuante que só imprime
`getnpcid` e `getmapxy` de cada nome no `OnInit`) confirmou nome **e
coordenada**, e foi apagada em seguida. Depois da saída da tenda:

```
SONDA Máquina          id=110024239 em prontera 167,199
SONDA Xanin            id=110024237 em prontera 172,201
SONDA Edgard           id=110024238 em prontera 170,200
SONDA Mestre do Refino id=110024241 em prontera 184,177
```

Isso prova que os NPCs **existem, o script compila e eles estão na célula
certa**. Não prova sprite na tela nem que a cor de roupa muda de verdade. Para
isso: `@reloadscript` e ir a Prontera.

**Comparar o log de subida com o da rodada anterior** é a outra metade do
método, e foi ela que pegou o quase-desastre do preço de venda (seção
seguinte). A conferência é `[Error]`/`[Warning]` agrupados e `diff` contra o
baseline; hoje o resultado é **idêntico ao baseline**, nenhum aviso novo e
nenhum perdido.

### Nome de item nos diálogos — 2026-08-04, e o quase-desastre no meio

Achado testando o Mestre do Refino: **as falas dele nomeavam os itens em
inglês**, mesmo com o diálogo todo traduzido. Não era a tradução faltando.

O nome que o jogador lê na bolsa vem do `itemInfo.lua` do **cliente**, que já
está em português desde a rodada de tradução. Mas `getitemname()` e
`getequipname()`, que os scripts usam para montar a fala, leem o `Name` do
`item_db` do **servidor**, que estava em inglês. Mesmo item, dois nomes — e o
único que o jogador consegue procurar é o da bolsa.

Resolvido por `ferramentas/nomes_pt_item_db.py`, que **sincroniza** os dois:
16412 itens. A fonte é o `itemInfo.lua` do nosso cliente e **não** o
`iteminfo_new.lub` do bRO — os dois quase sempre concordam, mas quando
discordarem quem está certo é o do cliente, porque é ele que está na tela.
Mesma regra do `npcidentity.lub` e do `accessoryid.lub`.

Onde o cliente ficou em inglês, o servidor fica com o inglês dele: o objetivo é
**consistência**, e o português vem junto porque o cliente já está em
português.

#### A primeira tentativa zerava o preço de venda de 7126 itens, calada

Vale mais que o resultado. A primeira versão gerava um
`db/guerra/item_db_nomes.yml` com entradas de `Id` + `Name`, encadeado por
`import` — que é exatamente o que a CONVENÇÃO DE CUSTOMIZAÇÃO pede, e que o
rAthena aceita: `AegisName` e `Name` só são exigidos quando o item é **novo**.

Só que `itemdb.cpp:239` faz `hasPriceValue[id] = { has_buy, has_sell }` a
**cada** parse do mesmo `Id`, guardando só se *aquele bloco* declarou preço. Um
bloco de `Id` + `Name` grava `{false,false}` por cima do `{true,false}` do
`db/re/`, e aí a derivação do `loadingFinished` (`value_sell = value_buy / 2`)
não roda. A **Poção Vermelha** ia de `venda 5` para `venda 0`; a Branca, de 600
para 0; a Azul, de 2500 para 0.

**Dos 7126 itens afetados, um único imprimiu aviso na subida** — e por outro
motivo. Foi esse aviso solitário, ausente no log da rodada anterior, que puxou
o fio. Sem comparar os dois logs, isso teria entrado no servidor e só apareceria
como "por que ninguém ganha dinheiro vendendo drop?".

**A lição, e ela é geral:** um override parcial de YAML do rAthena não é "só os
campos que eu escrevi". Ele é um parse inteiro, e **campo ausente pode
significar "não declarado"** para lógica que roda depois, no `loadingFinished`.
Antes de sobrepor parcialmente, olhar o que o `loadingFinished` daquele db faz
com a ausência.

A solução foi trocar o `Name` **no lugar**, com `.INGLES` ao lado — que não
acrescenta parse nenhum, então nenhum campo muda de sentido. É a mesma saída
que a frente de tradução já tinha achado para o mesmo conflito com a convenção:
**fonte separada de resultado**. `--reverter` desfaz, e `git checkout` também.

Conferido depois de gravar: **toda** linha alterada nos três `item_db_*.yml` é
uma linha `Name:`, nenhuma outra, e a contagem de linhas não mudou. E o log de
subida ficou **byte a byte igual ao anterior em avisos e erros** — nenhum novo,
nenhum perdido.

#### 4587 itens continuam em coreano, e isso é do cliente

Os que o bRO nunca traduziu ficaram com o inglês do rAthena no servidor, porque
o `itemInfo.lua` os tem em coreano — e **o jogador vê coreano na bolsa deles**.
`Claymore` (1190) é um exemplo. É um buraco da tradução do cliente, anterior a
tudo isto, e ainda em aberto. Traduzi-los seria escrever nome novo no
`itemInfo.lua`, não no `item_db`.

### Mercado Contemporâneo — aberto em 2026-08-01, NÃO testado in-game

Nove lojas de equipamento na rua principal de Prontera, uma por slot, em grade
3×3: colunas `x=151/155/159`, fileiras `y=173/167/161`. Tudo a **1 zeny**. O
arquivo é `npc/guerra/mercado_contemporaneo.txt` e o cabeçalho dele tem o mapa
da grade, a lista item a item e o porquê de cada ausência.

**O que falta fazer, em ordem:**

1. `@reloaditemdb` e **depois** `@reloadscript`. Nessa ordem: a loja valida cada
   ID na hora de carregar, então o `item_db` precisa estar em pé antes.
2. **Fechar e reabrir o cliente.** As 25 entradas novas do `itemInfo.lua` só
   entram na inicialização. Sem isso os itens novos aparecem sem nome, e a
   conclusão errada é achar que o script falhou.
3. Ir a Prontera e comprar um de cada. Chapéu é o que merece atenção — é o
   único slot que pode dar caixa modal.

Os servidores **não foram reiniciados** de propósito (pedido de 2026-08-01), e
o cliente também não foi reaberto. Nada disso foi visto no jogo ainda.

#### O aviso na subida não é erro

Ao carregar, o rAthena vai imprimir uma linha por item:

```
npc_parse_shop: Item X discounted buying price (1->0) is less than
overcharged selling price (...)
```

É o próprio servidor apontando um exploit real (`src/map/npc.cpp:4153`): quem
compra a 1 zeny pode **revender em qualquer NPC** pelo `Sell` do `item_db` e
ficar com a diferença. O pior caso da lista é a **Boina Alada (5170)**, que tem
`Buy: 30000` e revende por 15000 — 14999 de lucro por compra, em laço infinito.
O resto tem `Buy: 20`, que dá 9 de lucro e não move nada.

O remédio, se um dia incomodar, **não é mexer no preço da loja** — revender não
passa por ela. É `Sell: 0` na entrada do item, ou tirar a Boina da lista.

#### Segunda rodada — 2026-08-04: dez itens novos, e a arte acabou

Dez itens pedidos pelo dono do projeto, distribuídos em quatro das nove lojas.
O placar da rodada anterior (77 pedidos → 4 fora por falta de arte) **fechou**:

| loja | entrou |
|---|---|
| Chapeleiro | `400213` Asas de Yggdrasil [1], `400597` Caubói de Kiwawa [1] |
| Ocleiro | `19443` Tapa-Olho Cósmico, `410124` Orelhas em Chamas, `410142` Adorno Angelical [1], `410140` Tiara de Asmodeus [1] |
| Senhor das Armas | `510146` Jurupari [2], `1132` Lâmina Turca, `510147` Adaga dos Orcs [2] |
| Sapateiro | `470274` Botas de Guivra [1] |

**Não sobrou item fora por falta de arte.** Os três chapéus que estavam de fora
desde 2026-08-01 (`410124`, `410142`, `410140`) entraram pela receita que o
`400287` tinha estreado em 2026-08-02, e agora está confirmada como receita e
não como sorte — **duas ferramentas, nesta ordem, e nenhuma sozinha resolve**:

```
python ferramentas/estende_accessoryid.py --id <n> --grf "<data.grf do bRO>"
python ferramentas/instala_visual.py      --id <n> --grf "<data.grf do bRO>"
python ferramentas/valida_visual.py       --id <n>          # tem de dar 0 faltando
```

A primeira ensina ao cliente que o **slot de visual existe**; sem essa entrada
de tabela não há arquivo que ele vá procurar, e é por isso que o
`instala_visual.py` sozinho nunca curava esses três. Os dez terminaram com
`valida_visual.py` dando **0 faltando** cada um.

**O ID da Tiara de Asmodeus mudou.** Até 2026-08-02 o cabeçalho do mercado
dizia `410139`; o que entrou foi o `410140`. São dois itens de verdade — a
versão sem cova e a com cova (`Hairband_Of_Asmodeus` e
`Hairband_Of_Asmodeus_`) — e o pedido era "[1]", que é a segunda.

**Um item não existe, e a decisão foi do dono do projeto.** O "Chapéu de
Kiwawa 401147" não está no `item_db` do rAthena, nem nos 18845 itens do bRO,
nem no `itemInfo.lua` do cliente. Existe **um** item Kiwawa, o `400597`
"Caubói de Kiwawa" [1], e ele entrou no lugar. É o quinto nome da lista de
"não localizados" do cabeçalho do mercado.

**Dois placeholders novos** em `db/guerra/item_db.yml` (`510146` Jurupari e
`510147` Adaga dos Orcs), com os bônus lidos da descrição do bRO, como os 18 de
2026-08-01. O Jurupari é o par do **Ceuci** — os dois são exclusivos do bRO,
folclore brasileiro, e o `TODO` do Ceuci dizia "não implementado porque a outra
peça não está no servidor". Agora está. Falta só entender **como** um conjunto
de duas armas de mão direita fica ativo; está anotado no `item_db` e não foi
chutado.

**A lição de tradução voltou, e agora vale para item também.** O
"[Impacto Meteoro]" da Adaga dos Orcs **não** é a Chuva de Meteoros do Bruxo
(`WZ_METEOR`) — é o `ASC_METEORASSAULT` do Algoz. Quem diz é o
`skillinfolist.lub` do GRF do bRO, que traz os dois pares. Traduzir nome de
habilidade de memória põe a magia errada na arma e ninguém percebe. Mesma regra
que já estava escrita para o diálogo, na seção da tradução de NPCs.

##### CORRIGIDO: cinco placeholders de 2026-08-01 pesavam 1/10 do que deviam

Achado e corrigido em 2026-08-04, no mesmo dia, a pedido do dono do projeto.

O `Weight` do `item_db` é **décimo de unidade**: o cliente divide por 10 ao
desenhar. O `19443` prova (`Weight: 300` no rAthena → "Peso: 30" na tela), e o
override do `400287`, escrito em 2026-08-02, já anotava a regra por extenso —
o que faltava era ela ter valido também para as cinco entradas da véspera, que
copiaram o número da tela direto:

| item | era | passou a ser |
|---|---|---|
| `510155` Ceuci | 60 | **600** |
| `450120` Armadura Resistente | 100 | **1000** |
| `15371` Roupa de Natal do Antonio | 40 | **400** |
| `400687` Garra Diabólica | 30 | **300** |
| `28572` Broche da Celine | 50 | **500** |

Na prática esses cinco itens eram dez vezes mais leves do que a descrição que o
próprio cliente mostrava. **Quem já tiver um deles vai sentir a diferença de
peso** assim que o `@reloaditemdb` passar — é o efeito esperado, não regressão.

A troca foi feita **bloco a bloco por `Id`**, e não por busca e substituição de
texto: o `400287` também tem `Weight: 50` e o dele está certo (a descrição do
bRO diz "Peso: 5"). Um `replace` solto teria estragado esse.

Depois disso o arquivo inteiro foi conferido contra o `iteminfo_new.lub` do
bRO: **os 8 itens que declaram `Weight` batem**. As 13 armas Brutais não
declaram nenhum, e isso está certo — elas pesam `0` no próprio bRO, conferido
na descrição. Os dois placeholders de 2026-08-04 já nasceram certos
(`Weight: 650` para "Peso: 65").

#### Terceira rodada — 2026-08-07: onze itens, e os doze NPCs viraram mercador

A rodada mexeu nos **dois** mercados de uma vez — o Contemporâneo e o de
Visuais — porque o pedido de sprite atravessava os dois arquivos.

##### Os sprites: doze NPCs, um só ofício

Pedido: **todas as lojas devem ser um mercador**, alternando homem e mulher se
der. Antes, cada loja usava o sprite do ofício que ela evoca — ferreiro nas
armas, cavaleiro nos escudos, moças avulsas no resto — e o efeito colateral era
que **nenhuma parecia loja**: o Lorde das Armaduras tinha cara de NPC de forja,
o Escudeiro de guarda de portão.

Este cliente tem **cinco** sprites de mercador. Todos conferidos duas vezes —
existem no `npcidentity.lub` **e** têm `.spr`/`.act` em `data\sprite\npc\` do
nosso `data.grf`, que é a conferência que a seção "Sprite de NPC" logo abaixo
manda fazer:

| sprite | sexo | uso |
|---|---|---|
| `1_M_MERCHANT` | homem | Chapeleiro, Lorde das Armaduras, Acessorista |
| `1_F_MERCHANT_01` | mulher | Ocleiro, Escudeiro, Costumeiro |
| `1_F_MERCHANT_02` | mulher | Sr. das Armas, Sapateiro, Camareiro |
| `4_M_HUMERCHANT` | homem | Retoqueiro, Capeiro, Adereceiro |
| `4_EP18_MERCHANT` | — | **fora**, só por sobrar |

A alternância homem/mulher segue a ordem de leitura do quarteirão e
**atravessa os dois arquivos**: a quarta fileira (`mercado_de_visuais.txt`,
y=155) continua de onde a terceira para, senão começaria repetindo o sexo da
anterior. Os três clássicos são o mercador de sempre, com carrinho; o
`4_M_HUMERCHANT` entrou para os homens não virarem seis cópias do mesmo boneco
lado a lado.

##### Os itens

| loja | entrou | saiu |
|---|---|---|
| Chapeleiro | `18878` Chapéu da Guarda Real [1], `400396` Chifres Oníricos [1] | `18580` Coroa de Yggdrasil |
| Ocleiro | `410067` Mini Óculos [1], `410026` Herança Real [1], `5985` Máscara da Nobreza | — |
| Retoqueiro | `18985` Pena de Falcão | `420010` Aura da Escuridão |
| Capeiro | `20952` Echarpe Escarlate [1], `480077` Capa de Magma [1] | — |
| Sapateiro | `470112` Botas Decadentes [1] | — |
| Acessorista | `28322` Luva do Falcoeiro [1], `28321` Garra do Falcoeiro [1] | — |
| Costumeiro | `20244` Disfarce de Jirtas | — |
| Adereceiro | `410320` Piscadela de Freya *(veio do Camareiro)* | — |
| Camareiro | — | `20310`, `31257`, `31421`, `31422`, `31423`, `31424`, `31429`, e a Piscadela |

**A rodada foi barata em arte** — a primeira desde 2026-08-01 em que quase nada
faltou. Dos onze itens novos, **dez** já estavam inteiros nas quatro tabelas.
Os que custaram alguma coisa:

- `410067` e `410026` estavam no rAthena mas **não no cliente** — a mesma
  armadilha do `410125` da rodada anterior: sem entrada no `itemInfo.lua` o
  item aparece **sem nome e sem ícone na própria vitrine**. Vieram do bRO pelo
  `completa_iteminfo.py`, e os IDs foram postos na tabela `ITENS` dele;
- `480077` Capa de Magma faltava nas **duas** tabelas do cliente: sem entrada
  no `itemInfo.lua` *e* sem nenhum dos 4 arquivos de arte, trazidos da GRF do
  bRO pelo `instala_visual.py`. Capa não é chapéu — são 4 arquivos e não 8, e
  não passa pelo `accessoryid.lub`, então o `estende_accessoryid.py` não entra
  aqui;
- os três tinham `Name` em inglês no servidor (`Professor's Mini Glasses`,
  `Floating Artifacts`, `Magma Manteau`) e foram sincronizados pelo
  `nomes_pt_item_db.py`. Como esse script lê sempre do `.INGLES`, rodá-lo de
  novo mexeu em **exatamente 3 linhas** do `db/re/item_db_equip.yml`.

Todos passaram no `valida_visual.py` com **0 faltando** antes de entrar na
linha da loja.

##### A Piscadela de Freya estava no slot errado — e essa foi a única correção de `item_db`

Pedido: "mover a Piscadela de Freya **corretamente** para visuais meio". O
"corretamente" era literal, e trocar a linha da loja seria metade do serviço.

O nosso rAthena dá o `410320` como `Costume_Head_Low` — por isso ele estava no
Camareiro. O bRO dá como **meio**, e quem diz é a descrição por extenso
(`estado_item.py --id 410320 --descricao` → `Equipa em: ^777777Meio`). O bRO
está certo: o item é um par de **lentes de contato** ("imitam as cores dos
olhos da deusa Freya"), e o slot de baixo é o de cachecol e máscara. No slot
errado ele disputava espaço com o cachecol do jogador em vez de com os óculos.

A correção é um override em `db/guerra/item_db.yml`, e ele tem uma pegadinha
que a própria seção OVERRIDES daquele arquivo já documentava: **`Locations` é
OR (`item->equip |= constant`), não atribuição.** Só acrescentar
`Costume_Head_Mid: true` deixaria o item ocupando os **dois** slots; tirar o
antigo exige `Costume_Head_Low: false` explícito.

O override não cai na armadilha do `hasPriceValue` que quase custou os 7126
itens em 2026-08-04: o `410320` não declara `Buy` nem `Sell` no `db/re/`, então
o bloco parcial regrava `{false, false}` por cima de `{false, false}`.

##### Duas coisas do pedido não bateram com a realidade, e as duas foram resolvidas por leitura

**"remover 41321" — esse ID não existe.** Não está no `item_db` do rAthena, nem
no `itemInfo.lua` do cliente, nem nos 18845 itens do bRO (`estado_item.py --id
41321`). O que existe é o **`31421`** (Costume Pink Angeling Bubble), que
estava no Camareiro **entre o `31257` e o `31422`** — os dois vizinhos imediatos
do pedido — e é balão como os outros quatro da mesma leva. Foi lido como
digitação trocada, e o `31421` é que saiu.

**A "Aura da Escuridão" foi pedida como remoção da loja de visuais, mas não
estava lá.** Ela estava no **Retoqueiro**, a loja de `Head_Low` do Mercado
Contemporâneo, desde 2026-08-01 — e era a única peça de *visual*
(`Costume_Head_Low`) numa vitrine de equipamento. Ou seja: o slot errado é o
que a pôs lá, e sair dali era a remoção certa de qualquer forma. Era o único
lugar em que ela estava.

##### O conjunto do Falcoeiro atravessa duas lojas

A Pena de Falcão (`18985`, Retoqueiro), a Garra (`28321`) e a Luva (`28322`,
Acessorista) formam três conjuntos entre si no `db/re/item_combos.yml` do
próprio rAthena. **Nada nosso foi preciso** — é o primeiro conjunto deste
mercado que o jogador fecha comprando em duas vitrines diferentes.

Nenhum item da rodada tem `Buy` acima de 20, então o aviso de
`discounted buying price` na subida não ganhou caso novo pior que a Boina Alada.

#### ACORDO: quando o bRO tem, a gente traz de lá — 2026-08-02

Combinado explicitamente com o dono do projeto em 2026-08-02, e registrado aqui
a pedido dele para ser entendimento das duas partes.

**O bRO é a nossa fonte de referência.** A intenção original era partir do
servidor do bRO; não foi possível porque o back-end que conseguimos é mais
antigo, e a recomendação foi seguir com ele mesmo. A consequência prática é
esta: sempre que faltar alguma coisa aqui — item, arte, nome em português,
descrição, slot de visual —, **o primeiro lugar a olhar é a instalação do
Ragnarok Brazil desta máquina**, e o padrão é trazer de lá em vez de inventar.

```
C:\Program Files (x86)\Gravity Interactive, Inc\Ragnarok Brazil\
    data.grf                      205117 entradas (arte, sprites, tabelas)
    System\iteminfo_new.lub        18845 itens: id -> nome e descricao PT
```

Se der para trazer o lote inteiro, traz-se o lote inteiro; se não der, traz-se
sob demanda, conforme o pedido. As duas formas já aconteceram — o
`instala_visual.py --todos` foi lote (1980 arquivos), e o 400287 foi sob
demanda.

**A distinção que causou confusão, e que vale ter clara:** "trazer do bRO" não
é uma coisa só, são três camadas independentes, e resolver uma não resolve as
outras. Ver a tabela em `ferramentas/LEIAME.md`, seção do
`estende_accessoryid.py`:

| falta | ferramenta |
|---|---|
| nome e descrição do item | `completa_iteminfo.py` |
| os arquivos de arte | `instala_visual.py` |
| a entrada de tabela do slot de visual | `estende_accessoryid.py` |
| o item no servidor | entrada em `rathena/db/guerra/item_db.yml` |

Foi por isso que, depois do lote de 2026-08-01 ter copiado 1980 arquivos, ainda
sobravam 377 itens quebrados: o lote cobria a segunda linha, e o que faltava
neles era a terceira.

#### A ponte que resolveu a lista: o itemInfo do bRO

A lista de itens veio em português do bRO, que não é o idioma de tabela nossa
nenhuma. A ponte foi o `iteminfo_new.lub` da instalação do Ragnarok Brazil desta
máquina — **18845 itens com `id → nome em português`**, lidos por
`ferramentas/completa_iteminfo.py` (é bytecode Lua 5.1, não texto).

Isso vale muito além deste mercado: **qualquer pedido futuro que venha com nome
de item em português se resolve por aí**, sem depender de site de database nem
de adivinhação. Foi assim que se confirmou que os quatro IDs passados na lista
estavam certos (`450338` Algazarra, `450257` Mediadora Platinada, `450222`
Epitáfio, `450120` Armadura Resistente) e que "Boina Alaeda" era **Boina Alada**
(5170) e "Cuativo YSF" era **Curativo YSF01**.

Da conferência saíram três classes de problema, e vale registrar a proporção
porque ela deve se repetir no próximo pedido:

| | itens | como ficou |
|---|---|---|
| Perfeitos (servidor + cliente) | 47 | na loja |
| Sem entrada no `itemInfo.lua` | 25 | **resolvido** pelo `completa_iteminfo.py` |
| Não existem no nosso rAthena | 18 | **placeholder** em `db/guerra/item_db.yml` |
| Não localizados em tabela nenhuma | 4 | fora, listados no cabeçalho do script |

#### Os 18 placeholders — preenchidos no mesmo dia

O `rathena/` vendorizado é mais antigo que o bRO, e 18 itens da lista
simplesmente não existiam aqui — 13 deles são a linha **Brutal** (o vendor só
tinha o Machado 1328 e a Lança 32014, da família `Blut_`).

De manhã foram criados como casca vazia, com `# TODO bonus` em todas e a decisão
explícita de **não inventar efeito**. À tarde descobriu-se que **não era preciso
inventar**: a descrição completa de cada item, com os números e cada bônus por
extenso, estava no `iteminfo_new.lub` do bRO. Ela só não vinha porque a primeira
versão do `completa_iteminfo.py` pulava a descrição de propósito, achando que
desmontar a tabela aninhada do bytecode não pagaria o esforço. Pagou no mesmo
dia — ver `ferramentas/LEIAME.md`.

De onde veio cada coisa:

| número | fonte |
|---|---|
| ATQ, DEF, peso, nível | as linhas `Tipo:/ATQ:/Peso:` da descrição do bRO |
| os bônus | as linhas de efeito da mesma descrição |
| `Range`, `Jobs`, `Locations` | um item vizinho do mesmo `SubType` no rAthena |
| a forma do `Script` | o **Blut_Axe (1328)**, que o vendor já tinha |

A última linha é o que deu confiança ao resto: **duas das quinze armas Brutais já
estavam implementadas no rAthena**, com o script escrito por eles. As treze que
faltavam seguem o mesmo molde com os números que a descrição manda. Não é
tradução livre — é fechar a lacuna de uma família meio implementada.

Os quatro nomes de habilidade que apareciam em português (`Execução`,
`Expurgar`, `Calibre Letal`, `Lançar Míssil`) foram resolvidos pela mesma
técnica dos nomes de item, uma camada acima: o `skillinfolist.lub` da GRF do bRO
mapeia `SKID` → nome em português. Deu `RL_HAMMER_OF_GOD`, `RL_R_TRIP`,
`RL_SLUGSHOT` e `RL_D_TAIL`, todos conferidos no `skill_db.yml`.

#### O que ainda tem `# TODO`, e por quê

Sobraram **quatro** efeitos e **oito** conjuntos. Cada `# TODO` cita a linha em
português que ficou de fora, para não ser preciso reabrir a descrição.

| item | o que falta | por quê |
|---|---|---|
| 28247 Espingarda | "Mantém [Espalhar Dano] ativo" | não há `bonus` que mantenha habilidade ligada, **e** "Espalhar Dano" não existe na tabela de habilidades do bRO |
| 510155 Ceuci | +11: remover Hipotermia/Cristalização ao apanhar de magia | `bonus3 bAutoSpellWhenHit` **conjura**, não **remove** status |
| 400687 Garra | +11: 10% de infligir Medo ao apanhar | idem |
| 15371, 28572, 400687, 510155 | os conjuntos | exigem a outra peça, que em geral nem está no servidor |

Os três primeiros exigiriam código em `src/custom/`, o que significa recompilar.

**Uma exceção vale a pena:** o conjunto do Broche da Celine (28572) com a **Luva
dos Espíritos Malignos (2980)** é viável hoje — as duas estão no mesmo mercado,
no Acessorista. O Laço da Celine (18849), que forma outro conjunto com ele,
também já está na loja, no Chapeleiro.

Uma decisão que merece registro: o **Lança-Granadas (28248)** é a única das treze
**sem** `bUnbreakableWeapon`, e não é esquecimento — a descrição do bRO não traz
a linha "Indestrutível em batalha" que as outras doze trazem. Também é a de maior
ATQ da família (210), o que sugere troca deliberada. Mantido como está lá.

E o **Katar (28033)** não tem bônus de crítico apesar de a descrição dizer
"Duplica a chance de causar um ataque crítico": no rAthena dobrar o crítico é
propriedade do *tipo* Katar, aplicada em `src/map/battle.cpp`. Pôr um
`bonus bCritical` aqui dobraria de novo.

**Armadilha para o dia da atualização do rAthena:** esses IDs estão *fora* da
nossa faixa 30000-30999, e o `Footer: Imports:` faz o nosso arquivo ser lido
**depois** do `db/re/item_db.yml`. Se o rAthena um dia trouxer esses itens de
verdade, as nossas entradas vazias **venceriam a versão boa, caladas**. Conferir
essa seção antes de qualquer outra coisa ao atualizar o vendor.

Exceção: o **Ceuci (510155)** é exclusivo do bRO — folclore brasileiro, nunca
existiu no kRO. O placeholder dele é permanente, não provisório.

#### CORRIGIDO em 2026-08-01 — "chapéu é o único slot perigoso" era falso

O parágrafo que estava aqui dizia que só cabeça podia dar caixa modal, e que os
outros oito slots no máximo ficariam sem nome. **Isso foi desmentido in-game na
mesma tarde**, e o erro vale mais registrado do que apagado, porque a conclusão
errada vinha de confiar na ferramenta em vez de no jogo.

Abrir a loja do Acessorista entregou:

```
Resource File Loading fail
texture\<ui>\item\ringofjupiter.bmp
```

O Anel de Júpiter (32258) é **acessório**. Não tem sprite de cabeça nenhuma. O
que faltava era o **ícone de inventário**, e ícone todo item tem.

Por que o `valida_visual.py` não pegou: ele só olhava *item de cabeça com
`View`* — 5301 dos 13001 itens. Os outros 7700 nunca eram conferidos, e o
silêncio dele foi lido como aprovação. As três tabelas concordavam que o item
existia; quem discordava era o GRF; e desta vez o validador também não olhava.

**A regra corrigida: todo item tem 4 arquivos de arte (sprite de chão `.spr` e
`.act`, ícone de inventário, ícone grande). Chapéu tem mais 4.** Faltar o ícone
de inventário é modal, não é só feio.

O `valida_visual.py` e o `instala_visual.py` foram generalizados para cobrir
qualquer item, e passaram a ler também o `db/guerra/item_db.yml` — sem isso os
nossos placeholders eram invisíveis para eles. Detalhes em
`ferramentas/LEIAME.md`.

#### O processo, para a próxima loja

Esta é a sequência completa, e a ordem importa em dois pontos:

```
1. python completa_iteminfo.py --verificar     # nome e recurso do bRO
2. python completa_iteminfo.py                 # grava
3. python valida_visual.py  --id <lista>       # o que falta de arte
4. python estende_accessoryid.py --id <lista> --grf "<grf do bRO>"
5. python instala_visual.py --id <lista> --grf "<grf do bRO>"
6. python valida_visual.py  --id <lista>       # tem que dar 0
7. fechar e reabrir o cliente
```

- **1-2 antes de 3-5:** o validador lê o `identifiedResourceName` do
  `itemInfo.lua`. Sem entrada ele nem sabe qual arquivo procurar, e responde
  "não está no itemInfo.lua" — que parece "não tem arte" e não é.
- **4 antes de 5**, e essa também não é intuitiva: o `instala_visual.py` só
  sabe procurar as 4 sprites de cabeça depois que o `accessoryid` lhe diz o
  sufixo do arquivo. Na ordem errada ele instala os 4 ícones, relata
  "faltando 0" e o chapéu continua invisível. O passo 4 só é necessário quando
  o passo 3 acusar `view N no accessoryid`; nos outros casos ele não faz nada.
- **6 antes de 7:** conferir no disco custa segundos; descobrir no jogo custa
  reabrir o cliente.

Aplicado aos 77 itens do mercado em 2026-08-01: **43 estavam sem nenhum dos 4
arquivos**, 272 arquivos foram copiados da GRF do bRO, e a reconferência deu
**0 com falta**. A cura estava toda no disco desta máquina, como sempre.

#### O cliente inteiro foi curado no que dava — 2026-08-01

O mercado eram 77 itens de 13001, então o lote completo rodou logo em seguida:

```
python instala_visual.py --todos --grf "<grf do bRO>" --aplicar
```

| | antes | depois |
|---|---|---|
| desenháveis | 8502 | **8948** |
| **quebram o cliente** | **1902** | **1456** |

**446 itens curados**, e no total do dia **1980 arquivos / 22,1 MB** foram
escritos em `cliente\data\` (505 `.spr`, 505 `.act`, 970 `.bmp`), contando a
rodada do mercado e esta.

Detalhe que confirma que o lote de 2026-07-31 já tinha feito o serviço na camada
de cabeça: os números do `--cabeca` **não se mexeram** (3620 desenháveis, 552
quebram). Os 446 curados agora são **todos item que não é chapéu** — exatamente
o que o recorte antigo nunca olhou.

Nada disso toca o GRF. O `DataFolderFirst` faz o disco vencer, então tudo vai
solto para `cliente\data\` e apagar reverte. O servidor não fica sabendo.

#### Os 1456 que sobraram, e por quê

| | | |
|---|---|---|
| a GRF do bRO não tem a arte | 977 | conteúdo que nem o bRO recebeu |
| `View` fora do `accessoryid.lub` | 377 | **sem cura por arte** |
| parciais, pulados pelo tudo-ou-nada | 102 | a GRF do bRO tem só parte |

Os **377** são a categoria que não se resolve copiando arquivo: o cliente de
2021 não conhece aquele `View`, então não é falta de arquivo, é ele não saber
que slot desenhar. Resolver exigiria mexer no `accessoryid.lub` — **e foi
exatamente o que se fez em 2026-08-02**, ver a seção do Capacete de
Intensificação, mais abaixo. Enquanto isso não existia, era o motivo de os
quatro chapéus listados acima estarem fora da loja.

Os **102 parciais** são pulados de propósito: `.spr` sem o `.act` do par quebra
o cliente igual, e ainda esconde o problema do `valida_visual.py`. Tudo-ou-nada
por item.

Quatro chapéus pedidos ficaram de fora por isso — `400287`, `410124`, `410142`,
`410139`. Nos quatro o `View` **nem existe no `accessoryid.lub` deste cliente**,
que é o caso que o `instala_visual.py` não cura: não é falta de arquivo, é o
cliente não saber que aquele slot de visual existe.

**O `400287` saiu dessa lista em 2026-08-02** e está no Chapeleiro. Os outros
três continuam fora, mas agora por não terem sido pedidos — o caminho para eles
é uma linha de comando, não um problema em aberto.

Uma quinta observação, essa nova: o placeholder `400687` (Garra Diabólica) foi
criado **de propósito sem `View`**. Sem arte no GRF, dar `View` a ele seria
trocar "invisível na cabeça" por "caixa de erro". Item sem `View` equipa, ocupa
o slot e não desenha nada — que é o comportamento certo para um placeholder.

E ficou registrada uma inversão de ordem que não é intuitiva: **o
`completa_iteminfo.py` roda antes do `valida_visual.py`**, porque o validador lê
o `identifiedResourceName` do `itemInfo.lua` e sem entrada ele nem consegue
avaliar. Antes de completar, sete chapéus respondiam "não está no itemInfo";
depois, três passaram a validar limpo e quatro se revelaram sem arte de verdade.

#### Capacete de Intensificação (400287) — 2026-08-02, NÃO testado in-game

Pedido: pôr o item no Chapeleiro. Ele era um dos **quatro chapéus sem cura** de
2026-08-01, e destravá-lo exigiu abrir uma frente nova — a terceira camada de
"trazer do bRO", que até então não existia. Ver o ACORDO, mais acima.

**O que já estava pronto e o que faltava:**

| camada | estado em 2026-08-02 |
|---|---|
| nome e descrição no `itemInfo.lua` | **já estava**, posta em 2026-08-01 |
| os 4 arquivos de item (sprite de chão + ícones) | faltavam — vieram da GRF do bRO |
| o slot de visual `View 2260` | **faltava, e não havia ferramenta** |
| as 4 sprites de cabeça | faltavam — só localizáveis depois do slot |
| os bônus no servidor | **conflitavam** — ver abaixo |

O `View 2260` foi resolvido pelo `ferramentas/estende_accessoryid.py`, escrito
para isto. Ele grava um override de `accessoryid.lub` e `accname.lub` em
`cliente\data\` com as 2192 entradas do nosso GRF **mais** a nova, validado por
round-trip antes de gravar. Detalhes e as travas em `ferramentas/LEIAME.md`.

Medido no cliente inteiro: **8948 → 8949 desenháveis, 1456 → 1455 quebram.**
+1/−1 e nenhum outro número se mexeu — estender a tabela não tocou nos 2192
slots que já funcionavam.

**O conflito no servidor, que é o achado que vale guardar.** O rAthena
vendorizado *tem* o ID 400287, mas com outro item: o kRO chama de "Legacy of
Wise One" e dá bônus **elementais** com degraus de refino +7/+9. O bRO
rebalanceou e rebatizou: "Capacete de Intensificação", bônus de **raça**,
pós-conjuração −20%, degraus +10/+12. Mesmo ID, dois itens diferentes.

Como o `itemInfo.lua` do cliente já mostra a descrição do bRO, manter os bônus
do kRO faria a descrição **mentir** para o jogador — ele leria "−20% de
pós-conjuração" e receberia resistência elemental. Entre trocar a descrição do
cliente e trocar o efeito do servidor, trocar o servidor é o lado barato e o
lado certo.

Isso criou a **terceira categoria** de `db/guerra/item_db.yml`, documentada lá
na seção `OVERRIDES`:

| categoria | o que é |
|---|---|
| 30000-30999 | itens NOSSOS, inventados |
| placeholders | itens reais que o nosso rAthena não tem — preenchem lacuna |
| **overrides** | itens que o rAthena TEM, e cuja versão dele substituímos |

A diferença importa no dia da atualização do vendor: placeholder um dia some,
quando o rAthena trouxer o item de verdade; **override não some nunca**, porque
existe justamente porque discordamos da versão deles.

**E ID repetido é MESCLADO, não substituído** — conferido em
`src/map/itemdb.cpp:ItemDatabase::parseBodyNode`, que faz `find(nameid)` e, se
o item já existe, reaproveita a entrada e só sobrescreve os campos escritos.
Duas consequências, as duas contra-intuitivas:

- campo **omitido** no override **mantém o valor do `db/re/`** — não volta ao
  padrão do rAthena. Então o override só precisa listar aquilo em que
  discordamos, mas precisa listar *tudo* em que discordamos, porque o que
  sobrar do item deles fica;
- `Locations` é OR (`item->equip |= constant`), não atribuição: não dá para
  tirar um slot omitindo-o, só passando `false` explícito.

O risco novo que isso cria para o dia da atualização: se a versão do rAthena
ganhar um **campo novo**, ele vaza para dentro do nosso item pela mesclagem,
calado.

**O que falta fazer, em ordem:**

1. `@reloaditemdb` e **depois** `@reloadscript` — a loja valida cada ID ao
   carregar, então o `item_db` precisa estar de pé antes.
2. **Fechar e reabrir o cliente.** O `accessoryid.lub` novo só é lido na
   inicialização, como todo `.lub`. Sem isso o chapéu continua invisível na
   cabeça e a conclusão errada é achar que o override não funcionou.
3. Comprar no Chapeleiro, equipar, e olhar a cabeça do personagem.

Os servidores **não foram reiniciados** e o cliente **não foi reaberto** —
nada disto foi visto no jogo ainda.

#### Sprite de NPC: a conferência pegou mais uma

Os nove sprites foram checados no `npcidentity.lub` **deste** cliente antes de
usar, e `4_M_JOB_KNIGHT` caiu — não existe aqui, embora o rAthena o conheça. O
Escudeiro ficou com `4_M_UNCLEKNIGHT` por isso. Mesma família do 10605 do
Mestre de Classe: **a tabela do rAthena conhece nomes que este cliente de 2021
não desenha**, e a única autoridade é o `npcidentity.lub`.

> Os sprites desta rodada **não estão mais em uso**: em 2026-08-07 as doze
> lojas dos dois mercados viraram mercador — ver "Terceira rodada — 2026-08-07",
> acima. A conferência descrita aqui continua valendo como receita, e foi ela
> que aprovou os quatro sprites novos.

---

### A Máquina virou a loja da Moeda Nova — 2026-08-07 (manhã), a versão de menu

> **A Máquina de hoje não é esta.** O menu descrito aqui foi substituído por uma
> loja de troca na mesma noite, e essa sim está confirmada no jogo — ver "A
> Máquina virou loja de troca", logo abaixo. Esta seção fica porque **o trabalho
> de descobrir onde cada item é gasto continua valendo**: a lista, os cupons de
> estilista e a armadilha dos homônimos `LI_` atravessaram a mudança inteiros.
> O que envelheceu é a forma da loja, não o conteúdo dela.

A Máquina de `prontera 167,199` era uma fala só (*"a máquina não funciona"*).
Agora ela vende **17 itens em três grupos**, cobrando **Moeda Nova (30998)** —
e é o **primeiro NPC que cobra a moeda**. O arquivo passou de
`maquina_quebrada.txt` para `maquina.txt`, porque o nome afirmava um fato que
deixou de ser verdade. A lista, os preços e o raciocínio de cada linha estão no
cabeçalho dele; aqui fica só o que atravessa o projeto.

**Quando esta seção foi escrita, de manhã, a economia não fechava:** existia
onde gastar a moeda e **não existia fonte**. Isso durou até a tarde do mesmo
dia — ver "O Logue e Ganhe virou a fonte da Moeda Nova", logo abaixo. As outras
fontes pensadas (trocas por Flor Visionária / Moeda do Explorador / Caveira)
continuam por fazer.

#### O trabalho foi descobrir ONDE cada item é gasto

A parte fácil foi resolver 16 IDs por nome em português, pelo `iteminfo_new.lub`
do bRO — a ponte de sempre. A parte que valeu foi a coluna seguinte: **item
comprado que ninguém consome é Moeda queimada.** Metade da lista são cupons, e
cupom é exatamente o tipo de item que pode existir em quatro tabelas, ter nome,
ícone e arte, e não servir para nada neste servidor.

**Os cinco cupons de estilista quase foram dados como mortos.** Procurar `6707`,
`25736`, `6959` ou `6046` em `npc/` **não devolve nada** — nenhum script do
rAthena os cita. A conclusão fácil, e errada, seria que não têm consumidor.
Quem os gasta é **C++**: `clif_parse_stylist_buy` (`src/map/clif.cpp`), lendo
`db/re/stylist.yml`, servindo a **UI de estilista do cliente**. A UI se abre por
`openstylist()`, e há um `Stylist#prontera` do próprio rAthena em
`prt_in 243,168` — dentro de Prontera, então comprar e gastar ficam na mesma
cidade.

**A lição generaliza:** `grep` em `npc/` **não prova que um item é inútil**. Os
sistemas de UI do cliente (estilista, refino, achievement, reputação) consomem
item **direto no C++, por tabela em `db/`**, sem passar por script nenhum. Antes
de concluir que um item não tem destino, procurar também pelo **AegisName** em
`db/` e em `src/map/`.

#### Duas armadilhas caladas ficaram registradas, não resolvidas

As duas são do tipo que **consome o cupom e não muda nada na tela**, sem erro:

1. **Cupom de Tintura.** Ele cobre os valores 2..7 de `Clothes_Color`, e este
   cliente só tem palette de roupa **0..3** da 2ª classe em diante — a mesma
   contagem que fixou o teto do Edgard em 3. Índice sem palette não dá erro: o
   cliente desenha a cor padrão.
2. **Cupom de Roupa.** Ele mexe em `Body2`, o corpo alternativo. **Não foi
   verificado** se o GRF de 2021 tem os sprites `_body` que ele pede.

O remédio, se um dia incomodar, não é mexer no NPC: é podar as opções em
`db/re/stylist.yml` (que teria de virar override nosso) ou tirar o cupom da
lista.

#### O ID do pedido apontava para outra coisa

O pedido dizia "Passe Anti-Gravitacional (imagino que já tenhamos Passe
Antigravitacional 13710)". **O 13710 não é o Passe**: ele é uma *caixa* cujo
`Script:` faz `getitem 7776,10`. Dez passes, apesar de o nome no jogo dizer
"[1]". O passe de verdade é o **7776**, gasto no `Ripped Cabus#GymPass`
(`payon 173,141`), +10 de peso por passe, teto de 10 usos.

Decidido manter a caixa: 100 Moedas entregam os +100 de peso inteiros, ou seja
10 Moedas por passe — a mesma faixa dos cupons ao lado. Vender o 7776 avulso
pelas mesmas 100 sairia dez vezes mais caro.

**Homônimo também apareceu, quatro vezes**, e aí o critério não é óbvio:
`Elunium Perfeito` é 6241 **e** 6911; `Oridecon Perfeito` é 6240 e 6910;
`Carnium Perfeito` é 6225 e 6906; `Bradium Perfeito` é 6226 e 6327. Os segundos
são os `LI_*`, variantes de evento com o **mesmo nome exibido** e que **não
aparecem no `db/re/refine.yml`** — comprar um deles daria um item de nome certo
que a UI de refino recusa, calada. O critério virou: **vale o ID que o
`refine.yml` cita.**

#### Por que menu e não `itemshop`

> **Superado na mesma noite.** A conclusão abaixo estava certa sobre o
> `itemshop` e **errada sobre a alternativa**: existe um terceiro tipo, o
> `barter`, que era o caminho o tempo todo. Ver a seção seguinte.

O rAthena tem o tipo `itemshop`, que é literalmente "loja que cobra em item":
seria uma linha só, com a janela de compra de sempre e ícone. Não serve aqui
por um motivo único: ele cobra **por unidade**, e **onze das dezessete linhas
são pacote** — "Elunium Perfeito (5 unidades) x 1 Moeda" dá 0,2 Moeda por
unidade, que não existe. O custo da escolha é não ter ícone e não ter "comprar
3 de uma vez". Se um dia a lista perder os pacotes, o `itemshop` volta a ser o
caminho certo.

#### Como foi conferido, já que não houve teste in-game

- Os 17 IDs passaram pelo `ferramentas/estado_item.py`: **todos existem nas
  quatro tabelas** e a arte deu **4 de 4** em todos. Nada a instalar, nem no
  cliente nem em `db/guerra/item_db.yml` — bem diferente do Mercado
  Contemporâneo, onde 43 dos 77 não tinham arte.
- O map-server foi reiniciado com o script novo: **nenhum erro de parse**, e o
  `debugmes` da trava de `OnInit` **não disparou**, o que prova que os quatro
  `setarray` têm o mesmo tamanho.
- As quatro colunas foram relidas do arquivo por script e conferidas contra o
  pedido, uma a uma: 17 linhas, ID, quantidade e preço batendo.

Isso prova que **o script compila e a tabela está certa**. Não prova a
navegação dos menus nem que a compra entrega o item. Para isso:
`@reloadscript`, `@item 30998 200` e ir a Prontera.

---

### A Máquina virou loja de troca — 2026-08-07 (noite), CONFIRMADA no jogo

O pedido veio como uma pergunta com um print junto: a loja de pedras de
encantamento de Malangdo cobra em moeda de gato, com a janela nativa do
cliente — *"não conseguimos fazer igual pra máquina?"*

Conseguimos. E o caminho **não era o `itemshop`** que a seção anterior tinha
descartado por preço.

#### Aquela janela é `barter`, e nenhum dos dois candidatos óbvios a abre

O rAthena tem três tipos de loja que cobram em algo que não é zeny, e os três
foram confundidos até aqui:

| tipo | cobra em | janela |
|---|---|---|
| `itemshop` | um item | `clif_cashshop_show` — saldo em número, **sem ícone** |
| `pointshop` | uma variável | idem |
| **`barter`** | item, por linha | **janela de troca** — ícone da moeda em cada linha |

Quem desenha o ícone e a quantidade do print é o próprio pacote:
`currencyNameid` e `currencyAmount`, em `clif.cpp:23243`. `itemshop` e
`pointshop` nem carregam esse campo. Ou seja: o `itemshop` **nunca** teria
produzido a tela do print, independentemente de preço.

#### E o `itemshop` teria falhado por um motivo pior, que ninguém veria vindo

A Moeda Nova é `NoSell: true`. O `itemshop` cobra varrendo a bolsa e passando
cada item por `pc_can_sell_item` (`npc.cpp:2465`), que **recusa item `NoSell`**
enquanto `allow_bound_sell` não tiver o bit `ISR_SELLABLE` — e o nosso
`conf/battle/items.conf` traz `allow_bound_sell: 0x0`.

O sintoma seria cruel: a loja **abre**, mostra a lista, e a compra falha com
*"is not enough as payment"* mesmo com as moedas na bolsa. O conserto óbvio
seria tirar o `NoSell` da moeda — que é justamente a trava que a impede de
virar mercadoria de mula.

O `barter` não chama `pc_can_sell_item` em lugar nenhum (`npc_barter_purchase`,
`npc.cpp:3140`): ele só ignora item equipado, em *equip switch* e favorito.
Moeda `NoTrade`/`NoDrop`/`NoSell` paga normalmente.

#### A trava do pacote continuou existindo — e a saída foi embalagem

O `barter` cobra **por unidade** igual ao `itemshop`
(`requirement->amount * amount`, `npc.cpp:3206`), e o YAML dele **não tem campo
de quantidade para o item vendido** — só `Item`, `Stock`, `Zeny`, `Refine` e
`RequiredItems`.

A saída é a que o próprio RO usa, e que o **13710 já era desde o primeiro dia**
da Máquina: se o pacote for **um item só**, o preço unitário volta a existir.
Toda linha de pacote virou caixa.

**A surpresa foi quanta caixa já existia pronta.** O pedido listava cinco itens
como "vai ter que criar"; `estado_item.py` mostrou que **três deles já estavam
no bRO**, com nome em português e arte 4/4:

| pedido dizia | é | |
|---|---|---|
| "Elunium Perfeito (5) — não achei, vai ter que criar" | **16395** `HD_Elu_Box5` | já existia |
| "Oridecon Perfeito (5) — não achei, vai ter que criar" | **16393** `HD_Ori_Box5` | já existia |
| "Carnium: se não tiver a de 5, usa a de 10 a 4 Moedas" | **16263** `F_HD_Carnium_Box5` | a de 5 existe — preço fica 2 |

Das dezoito linhas, **dezesseis usam caixa do bRO**. Só duas foram feitas por
nós, e as duas por razão registrada:

- **30997 `Cx_Bencao_Do_Ferreiro_5`** — no rAthena inteiro só há caixa de 2 e a
  `Blacksmith_Bless_Box_3` (101047), e essa entrega por `getgroupitem`. Nenhuma
  de 5. Arte copiada da 101047.
- **30996 `Cx_Pocao_De_Guyak_30`** — a `Guyak_Pudding_20_Box` (22668) existe,
  mas traz 20 **e tem nome coreano no `itemInfo.lua`**: o item não está no bRO,
  então não há português para trazer. Reprovada pela regra do nome em PT. Arte
  copiada dela mesma, que está completa.

Duas linhas mudaram de tamanho por decisão do dono do projeto, aproveitando
caixa pronta: **Cogumelo Grelhado** e **Bala Amarga** passaram a 100 unidades
por 4 Moedas (13996 e 13999) — as duas são irmãs no bRO, mesmo tamanho e mesmo
preço. E entrou uma linha nova: **Pergaminho de Arma +6 (6231)**, ao lado do de
Armadura, 1 Moeda por unidade.

#### São dois NPCs agora, e o motivo não é organização

Loja de `barter` **não roda script nenhum**. Se a Máquina fosse a loja, o
jogador clicaria e cairia direto na janela — sem fala, sem saldo, sem máquina.

Então a loja virou **flutuante**: `Maquina#loja`, sem mapa e sem sprite, só a
lista. O NPC de script continua em `prontera 167,199`, dialoga, conta a moeda e
chama a loja com `close2` + `callshop`. Loja sem mapa continua alcançável por
nome — o rAthena faz `strdb_put(npcname_db, ...)` mesmo com `m < 0`
(`npc.cpp:843`), e o `callshop` aceita `NPCTYPE_BARTER` (`script.cpp:18222`).

#### O que mudou de lugar junto, e é o que vai custar caro esquecer

**O nome do item na loja agora vem do CLIENTE.** O menu montava cada linha com
`getitemname()`, que lê o `Name` do `item_db` do servidor. A janela de troca
recebe só o ID e desenha o que o `itemInfo.lua` tiver. Nome errado numa loja de
troca **não se conserta mais** com o `nomes_pt_item_db.py` — conserta-se no
cliente, e exige fechar e reabrir. Subiu para o `CLAUDE.md` §4.9, como segundo
caso vivo da regra que o Logue e Ganhe abriu.

**O `checkweight` saiu do script**, e não por descuido: `npc_barter_purchase` já
checa peso e slot livre **antes** de cobrar (`pc_checkadditem`, `requiredSlots`,
`requiredWeight`). Refazer a conta daria duas respostas para a mesma pergunta.

**Perderam-se os três grupos** ("Passes e cupons", "Refino", "Consumíveis") —
eram cabeçalho de menu e a janela de troca não tem separador. O que restou deles
é a **ordem** das linhas, pelo `Index` do YAML.

#### Um defeito antigo apareceu no caminho

O `db/guerra/item_db.yml` estava **em UTF-8**, contra a regra §4.1 — e pior:
os acentos já tinham virado `U+FFFD` (`\xef\xbf\xbd`). "Maçã da Inocência" e
"Diadema do Paraíso" estavam gravados com o byte do acento **perdido para
sempre**, não mojibake reversível.

Ninguém percebeu porque o nome que o jogador lê vem do `itemInfo.lua`; o `Name`
do servidor só aparece em log, `@iteminfo` e diálogo de NPC. O arquivo foi
convertido para cp1252 e os 4 caracteres reconstruídos do contexto. A armadilha
subiu para o `CLAUDE.md` §5, com o teste de uma linha.

#### Conferido offline, e depois no jogo

Antes de subir:

- As 18 linhas do YAML foram relidas por script e cruzadas contra os quatro
  `item_db`: **todo `AegisName` resolve para um ID real**, toda moeda é
  `Moeda_Nova`, nenhum `Index` repetido, um requisito por linha.
- Os itens novos e os já existentes passaram pelo `estado_item.py`: **arte 4 de
  4 em todos**.
- `instala_item.py --verificar` aprovou as duas entradas novas antes de gravar;
  o `itemInfo.lua` cresceu 1642 bytes e ganhou backup.
- O `item_db.yml` foi relido em cp1252 depois da conversão: os 4 acentos
  antigos e os 2 novos aparecem certos, e não sobrou nenhum `U+FFFD`.

**Validada no jogo pelo dono do projeto em 2026-08-07**, com
`@reloaditemdb` → `@reloadbarterdb` → `@reloadscript`, cliente fechado e
reaberto. Sem ressalva: a fala abre, a janela de troca aparece com as 18 linhas
e o ícone da Moeda, a compra múltipla cobra o valor certo e as caixas entregam
a quantidade certa. **É a primeira das onze pendências de "falta ver no jogo" a
ser fechada** — foi aberta e encerrada no mesmo dia, e por isso nunca chegou a
constar da lista num commit.

Vale registrar o que a validação prova além da Máquina, porque não era óbvio
antes: o `@reloadbarterdb` **funciona a quente**, sem reiniciar o map-server, e
a loja flutuante alcançada por `callshop` se recria junto. Loja de troca nova
não precisa de janela de manutenção.

---

### O Logue e Ganhe virou a fonte da Moeda Nova — 2026-08-07, NÃO testado in-game

De manhã a Máquina passou a cobrar Moeda Nova sem que houvesse de onde tirá-la.
À tarde o **Logue e Ganhe** (`attendance`, no vocabulário do rAthena) fechou o
circuito: **10 Moedas por dia nos dias 1 a 19, e 50 no dia 20** — **240 por
conta por ciclo**, e um ciclo por mês civil.

Não há NPC. O sistema é do próprio cliente: uma janela de 20 quadrados que abre
sozinha no login e entrega o prêmio por **RoDEX**.

#### O achado que decidiu a forma do arquivo: são DOIS arquivos, não um

A lista de prêmios existe **duas vezes**, em lugares diferentes, e o servidor
**não** manda a dele para o cliente:

| quem | arquivo | o que faz |
|---|---|---|
| servidor | `rathena/db/guerra/attendance.yml` | **entrega** o prêmio |
| cliente | `cliente\System\CheckAttendance.lub` | **desenha** os 20 ícones |

O pacote `ZC_UI_OPEN` leva **um número só** — o contador do jogador. Quem pinta
cada quadrado é o `.lub`. Divergir as duas tabelas **não dá erro em lugar
nenhum**: a janela promete um item e o correio entrega outro, e o jogador é o
primeiro a descobrir.

Por isso a tabela virou **saída de gerador**, não texto escrito à mão:
`ferramentas/monta_logue_e_ganhe.py` tem a receita uma vez e grava os dois
lados. Rodar de novo é idempotente, e o `.lub` gerado é conferido com o
`Tools\luac.exe -p` do ROenglishRE antes de o script sair.

#### Vinte dias é o teto, e o teto é do cliente

Perguntado se dava para passar de 20, a resposta é **não** — e são três provas
independentes, nenhuma delas "o rAthena documenta assim":

1. O `CheckAttendance.lub` do nosso cliente (kRO 2021-11-03) é bytecode Lua, e a
   última constante numérica da tabela `Reward` é `20.0`.
2. O do ROenglishRE, que é texto puro, também para no dia 20.
3. O próprio rAthena só abre a janela no login quando
   `pc_attendance_counter(sd) < 200` (`src/map/pc.cpp:14796`) — e esse contador
   é `10 * dias + hoje`, ou seja **`dias < 20`**.

Pedir um dia 21 no YAML não daria erro: o quadrado simplesmente não existe.

#### Por que um ciclo por mês, e não um período longo

O contador só zera **quando começa um período novo** — `pc_attendance_counter`
compara a data da última retirada com o `Start` do período corrente. Um período
único e longo daria 20 dias por conta **na vida inteira**: bônus de boas-vindas,
não renda. Foram gerados **17 ciclos**, de agosto de 2026 a dezembro de 2027,
um por mês civil.

**O contador é de CONTA**, não de personagem — as variáveis são
`#AttendanceDate` e `#AttendanceCounter`, e o `#` é o prefixo de conta no
rAthena. Trocar de personagem não rende de novo. Isso casa com o `NoTrade` da
moeda: sem ele, a renda passaria a ser por *conta criada*.

**Quando o último ciclo vencer, o sistema morre calado** — sem janela, sem erro.
Rodar o gerador de novo com `ULTIMO` adiantado antes de dezembro de 2027.

#### O `NoMail` da Moeda Nova assustou à toa

O prêmio chega por correio, e a Moeda Nova tem `NoMail: true`. Parecia
contradição fatal. Não é: o `itemdb_canmail` é checado **num lugar só**,
`mail.cpp:272`, dentro do `mail_setitem` — ou seja, quando um **jogador** anexa
item a uma carta que ele mesmo escreve. O correio do sistema é montado direto
em `pc_attendance_claim_reward` e não passa por ali. Retirar anexo também não
checa. A trava continua valendo para o que foi feita: impedir que a moeda vire
mercadoria.

#### O `attendance: false` do `Super Player` é letra morta

`conf/groups.yml:95` diz `attendance: false` no grupo **Super Player**, do qual
o grupo 99 herda. A leitura óbvia seria que a conta de teste não consegue abrir
a janela. **Está errado**, e a razão está em `pc_groups.cpp:275`: herança de
grupo é um **OU binário** (`group->permissions |= otherGroup->permissions`),
aplicado *depois* do parse. O `Super Player` herda do `Player`, que tem
`attendance: true` — então o bit volta a ligar, e desce até o 99.

Generaliza, e é a parte que vale guardar: **em `groups.yml`, `false` só
significa "não ligo"; nunca "desligo".** Permissão que o pai concede, o filho
não consegue tirar. Está no `CLAUDE.md` §5.

#### Como foi conferido, já que não houve teste in-game

- O map-server foi **reiniciado** com o YAML novo: **nenhuma linha de
  `attendance` no `log/map-msg_log.log`** — nem `Unknown item ID`, nem
  `Reward for day N is missing`, nem colisão de período. Os quatro servidores
  voltaram.
- O `.lub` gerado passa no `Tools\luac.exe -p`.
- `db/import/attendance.yml` foi conferido: só cabeçalho, sem `Body` — não há
  período da máquina colidindo com os nossos.
- A janela ativa hoje é a de agosto (`20260801`–`20260831`), e
  `pc_attendance_period()` casa `start <= hoje <= end`.

Isso prova que **o servidor carrega a tabela e o cliente compila a dele**. Não
prova que a janela abre, nem que o RoDEX entrega. Para isso: fechar e reabrir o
cliente (o `.lub` só é lido na inicialização) e logar.

## CONCLUÍDO — tradução do cliente para o inglês (2026-07-30)

**Esta seção é histórica.** Ela conta como o cliente saiu do coreano; o
português veio depois, em 2026-08-03, **por cima destes mesmos arquivos** — ver
"CONCLUÍDO — tradução PT-BR". O inglês continua sendo a camada de reserva:
onde o bRO não tem texto, é ele que aparece.

Estado ao fim daquele dia: tela de login, seleção de personagem, janelas do
jogo, itens, habilidades, quests e letreiro de mapa em inglês. O único coreano
que restava é a arte da tela de classificação etária, que é imagem, não texto.

A decisão foi **ligar o inglês primeiro** e traduzir para PT-BR depois, em cima
dessa base — e foi exatamente o que aconteceu.

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

Atualizada em 2026-08-03 com a coluna do português.

| Camada | Arquivo | Inglês (2026-07-30) | PT-BR (2026-08-03) |
|---|---|---|---|
| UI e mensagens de sistema | `data\msgstringtable.txt` | patch `MsgStrings` no WARP | `traduz_ptbr.py msgtable` |
| Rótulo de janela e de botão | `data\...\msgstring_kr.lub` | ROenglishRE | `traduz_ptbr.py msgstrid` |
| Quests (fallback) | `data\questid2display.txt` | já lido por padrão em `langtype 0` | `traduz_ptbr.py quests` |
| Janela de missões | `System\OngoingQuestInfoList_Sakray.lub` | **nunca saiu do coreano** | `traduz_ptbr.py questinfo` |
| Aba RECOMENDADAS | `System\RecommendedQuestInfoList_Sakray.lub` | **nunca saiu do coreano** | `traduz_ptbr.py questreco` |
| Strings cravadas no exe | `WARP\Inputs\Translations_EN.yml` | `TranslateClient`, já aplicado antes | **continua em inglês** |
| Itens | `SystemEN\LuaFiles514\itemInfo.lua` | stub do ROenglishRE em `System\itemInfo_true.lub` | `traduz_ptbr.py itens` |
| Letreiro e nome de mapa | `System\mapInfo_*.lub`, `data\mapnametable.txt` | trocado pela versão em inglês | `traduz_ptbr.py mapinfo mapas` |
| Habilidades | `data\...\skillinfoz\*.lub` | recortados em 2026-07-30 ~22:55 | `traduz_ptbr.py skills` |
| Conquistas | `System\achievement_list.lub` | **nunca saiu do coreano** | `traduz_ptbr.py conquistas` |
| Prefixo de carta | `data\cardprefixnametable.txt` | ROenglishRE | `traduz_ptbr.py cartas` |
| Texturas | `data\texture\유저인터페이스\` | já ativas via `DataFolderFirst` | **continua em inglês** |
| Mensagens do servidor | `rathena\conf\msg_conf\map_msg_por.conf` | inglês, o padrão | `conf/guerra/map_msg_guerra.conf` |
| Nome de monstro | `rathena\db\re\mob_db.yml` (`JapaneseName`) | inglês, o padrão | `traduz_ptbr.py monstros` |
| Janela do `Setup.exe` | recursos `RT_DIALOG` dentro do próprio exe | `ferramentas\traduz_setup.py` — ver abaixo | já estava em português |

As duas linhas "continua em inglês" são as que não têm fonte no bRO: as strings
compiladas dentro do exe precisariam de um `Translations_PT.yml` escrito à mão
para o patch `TranslateClient`, e as texturas são imagem.

**A regra que se repetiu cinco vezes:** quando um texto continua em coreano, a
versão traduzida quase sempre **já está no disco** — e no caso do `Setup.exe`,
dentro do próprio binário. O que falta é o cliente ser apontado para ela. Antes
de traduzir qualquer coisa, confirmar de onde o cliente realmente lê o texto.

### O `Setup.exe` — traduzido em 2026-07-30 ~23:55

A janela do `Setup.exe` continuava em coreano. **Não foi preciso editar texto
nenhum:** o exe da Gravity já traz os diálogos compilados em sete idiomas.

| par de IDs | idioma | | par de IDs | idioma |
|---|---|---|---|---|
| 103 / 104 | inglês | | 110 / 111 | chinês tradicional |
| 105 / 106 | **coreano — era o que estava em uso** | | 112 / 139 | **português — em uso agora** |
| 107 / 108 | chinês simplificado | | 140 / 141 | russo |
| | | | 142 / 143 | japonês |

O idioma **não** é escolhido por locale nem por arquivo de configuração — o exe
não importa uma única API de idioma. O ID do recurso está cravado no código, e no
build coreano é o do par coreano. Por isso o patch não mexe no código do
diálogo: faz o `IMAGE_RESOURCE_DATA_ENTRY` do ID 105 apontar para os bytes do
112, e o do 106 para os do 139 — **8 bytes por diálogo**. Os diálogos coreanos
continuam no arquivo, intactos.

Os três botões do rodapé são um caso à parte: não estão nos diálogos, são
literais **CP949 em `.rdata`**, escritos com `SetWindowTextA`. Eram eles que
apareciam como `È®ÀÎ` / `Ãë¼Ò` — mojibake de CP949 lido na codepage 1252, e não
hangul de verdade. Como `Cancelar` e `Restaurar` não cabiam no slot original de 8
bytes, as strings novas foram para o **padding zerado do fim da seção `.text`**
(492 bytes livres em RVA `0x20E14`, dentro da última página mapeada da seção) e
os três `push imm32` que as referenciavam passaram a apontar para lá.

O patch inteiro são **37 bytes**: 2 data entries, 3 operandos `push`, as strings
novas e o checksum do PE recalculado. Backup em
`cliente\Setup.exe.BACKUP-20260730-234917`.

Verificado com `LoadLibraryEx` + `FindResource`: o loader do Windows devolve para
o ID 106 o template com `Config. Gráfica` / `Dimensão da Tela`.

**Se um dia quiser o inglês em vez do português**, é trocar os pares em
`PARES`, no topo do `traduz_setup.py`, de `112`/`139` para `103`/`104`.

**A aba `Option` não tem tradução em nenhum idioma** exceto coreano: os rótulos
são os nomes crus dos comandos (`notrade`, `skillfail`, `fog`). Os IDs 103 e 112
são idênticos nesse ponto. Traduzir essa aba exigiria reconstruir o template, o
que não cabe no espaço atual do recurso — ficou de fora de propósito.

**Os títulos das abas continuam `System` e `Option`.** Estão embutidos no
template português; trocar por `Sistema` exigiria realocar o recurso, porque só
substituição de mesmo comprimento é segura dentro de um `DLGTEMPLATEEX`.

### Pontos de partida para a fase PT-BR — todos consumidos em 2026-08-03

A lista que vivia aqui (mapinfo_C, map_msg_por, msgstringtable, itemInfo_C,
skilldescript) foi feita inteira, e por um caminho diferente do que ela
sugeria: em vez de arquivo `_C` de sobreposição, **merge por chave sobre o
arquivo do ROenglishRE**. Ver a seção seguinte.

---

## CONCLUÍDO — tradução PT-BR (2026-08-03)

**O jogo está em português.** Item, habilidade, quest, conquista, mapa, monstro,
rótulo de janela, mensagem do servidor e os NPCs nossos. Uma ferramenta faz o
lado do cliente inteiro:

```
python ferramentas/traduz_ptbr.py tudo --verificar    # relata, não grava
python ferramentas/traduz_ptbr.py tudo               # aplica
```

Nada foi traduzido por nós: **tudo veio da instalação do Ragnarok Brazil desta
máquina**, cumprindo o ACORDO de 2026-08-02. A única exceção são 36 rótulos de
barra de atalho que o cliente do bRO não tem, resolvidos por analogia.

### O que ficou traduzido, e quanto

| parte | o que aparece | fonte no bRO | rendimento |
|---|---|---|---|
| `itens` | nome e descrição de item | `System\iteminfo_new.lub` | 16838 nomes, 11499 descrições |
| `skills` | nome e descrição de habilidade | `skillinfolist.lua` / `skilldescript.lua` do GRF | 1060 nomes, 872 descrições |
| `quests` | título e texto do diário | `data\questid2display.txt` | 3135 de 8369 |
| `questinfo` | a janela de missões | `System\OngoingQuestInfoList_True.lub` | 6318 em PT + 5365 em EN, 0 em coreano |
| `questreco` | a aba RECOMENDADAS | `System\RecommendedQuestInfoList_True.lub` | 1 em PT + 18 em EN, 1 em coreano |
| `msgstrid` | rótulo de janela e de botão | `msgstring_br.lub` | 425 + 36 por analogia |
| `msgtable` | mensagem de sistema e de erro | `data\msgstringtable.txt` | 2941 de 4023 |
| `conquistas` | o modal de conquista | `System\achievement_list.lub` | 349 de 361 |
| `mapas` | nome do mapa no minimapa | `System\mapInfo.lub` | 952 de 958 |
| `mapinfo` | o letreiro ao entrar no mapa | `System\mapInfo.lub` | 1982 campos |
| `cartas` | o prefixo que a carta põe no nome | `data\cardprefixnametable.txt` | 935 |
| `monstros` | o nome que flutua sobre o monstro | `navi_mob_br.lub` do GRF | 1061 de 2675 |

### A decisão que atravessa tudo: mesclar, nunca trocar o arquivo

O reflexo é copiar o arquivo do bRO por cima do nosso. **Estaria errado em quase
todos**, e o motivo é contraintuitivo: o **ROenglishRE é mais NOVO que o bRO**.
Ele acompanha o kRO de 2026; o cliente do bRO é anterior e não conhece conteúdo
que nós já temos. Trocar arquivo por arquivo traduziria o que existe nos dois e
**apagaria o resto** — 5234 quests ficariam em branco em vez de em inglês.

Então o destino é sempre o arquivo que o cliente já usa, e o bRO só preenche o
texto, por chave. O que o bRO não tem continua em inglês.

A exceção é `conquistas`, e ela se justifica sozinha: o `achievement_list.lub`
daqui é o **coreano do instalador de 2021** — não havia inglês a preservar. É
também o único que é código, não tabela de texto, e não daria para costurar.

### O `msgstringtable.txt` é o único arquivo sem chave

Todos os outros têm chave — ID de item, `SKID.X`, ID de quest, nome de `.rsw`,
`MSI_*`. O `msgstringtable.txt` não: **o cliente pede a linha pelo número**, e o
número é o que o exe de 2021 espera. As duas tabelas divergem (4023 linhas
contra 4216) e não é só no fim — medido, a diferença aparece no meio.

Trocar o arquivo entregaria a mensagem errada em todo lugar. A solução foi
alinhar por âncora: linhas cuja **assinatura sobrevive à tradução** (`%s`, `%d`,
`^RRGGBB`, número, sigla em maiúscula, comando com barra) são casadas em ordem
entre os dois arquivos; entre duas âncoras consecutivas, se a distância for a
mesma dos dois lados, a corrida inteira entra.

Dá 651 âncoras e **73,1% das linhas**. O resto fica em inglês de propósito —
**linha não mapeada é melhor que linha trocada**. Conferido à mão numa amostra
de 16 pares: todos casaram semanticamente.

### O lado do servidor

Duas camadas que nenhuma ferramenta de cliente alcança:

- **Mensagem do map-server** (resposta de `@comando`, aviso de peso, recusa de
  negociação). O rAthena já distribui a tradução: `map_msg_por.conf`, 1276 das
  1278 mensagens. O caminho **não** foi o `@langtype`: ele vem desligado em
  tempo de compilação (`LANG_ENABLE` é `0x000` em `src/common/msg_conf.hpp`) e,
  mesmo ligado, o padrão de cada personagem continua sendo o inglês. Em vez
  disso, `conf/guerra/map_msg_guerra.conf` importa o arquivo português por cima
  da tabela padrão — o leitor de mensagens é recursivo e sobrescreve por número.
  **Bônus:** `jobname()` lê a mensagem 550+, então os nomes de classe do Mestre
  de Classe passaram a sair em português sem tocar no script.
- **Nome de monstro.** Não vem de tabela do cliente: o servidor manda a string
  pronta, do campo `JapaneseName` do `mob_db` (`src/map/mob.cpp`, o `memcpy` em
  `mob_spawn_dataset`). O `Name` fica em inglês de propósito — é por ele que
  `@monster` e os scripts do rAthena procuram o bicho.

A ponte para o ID do monstro foi o **`navi_mob_br.lub`** do GRF do bRO: a tabela
que a navegação usa para dizer "o monstro X está no mapa Y" carrega o
**AegisName ao lado do nome em português**. O ID não aparece nela — foi o par
`AegisName` que resolveu 1061 dos 2675.

### Três linhas novas em arquivo do rAthena

A convenção manda ter conta delas. Agora são **cinco** no total:

| arquivo do rAthena | o quê |
|---|---|
| `npc/scripts_custom.conf` | `import:` dos nossos NPCs (de 2026-07-30) |
| `conf/battle_athena.conf` | `import:` de `conf/guerra/` (de 2026-08-01) |
| `conf/msg_conf/map_msg.conf` | `import:` de `conf/guerra/map_msg_guerra.conf` |
| `db/re/item_db.yml` | `Path:` de `db/guerra/item_db.yml` (de 2026-07-31) |
| `db/re/mob_db.yml` | **um `Footer:` inteiro**, que não existia |

A última merece nota: o `mob_db.yml` do rAthena **não trazia `Footer:` nenhum**,
e sem ele não existe caminho para acrescentar nada ao banco de monstros — nem
`db/import/mob_db.yml`, que é o lugar que todo mundo assume. O bloco teve de ser
criado.

### O que NÃO foi traduzido, e por quê

- **Diálogo dos NPCs do rAthena** — milhares de arquivos em `npc/`, e o bRO não
  é fonte para eles: o que temos do bRO é o **cliente**, não o servidor. Não há
  de onde importar. Os NPCs nossos (`npc/guerra/`) estão em português.
- **5234 quests, 1082 mensagens de sistema, 1614 monstros** — o bRO não tem.
  Continuam em inglês, que é o comportamento certo.
- **12 conquistas** (128038-128043, 128050-128052, 129021, 130005, 200032) —
  passam de coreano para vazio. Ver a seção do `traduz_ptbr.py` no
  `ferramentas/LEIAME.md`.
- **`char_msg.conf` e `login_msg.conf`** — não têm tradução PT no rAthena, e o
  que aparece na tela do jogador vem do map. Ficaram de fora.

### A primeira reabertura quebrou — a aspa escapada

Na primeira vez que o cliente foi reaberto, às ~20:50, ele subiu com **seis
diálogos de erro**. Não era o GRF, apesar da aparência: era um bug meu, e a
lição de diagnóstico vale mais que a correção.

Quatro valores do `msgstring_kr_s.lub` têm **aspa escapada** dentro da string:

```lua
MSI_PARTY_BOOKING_MAKE = "/organize \"Party Name\": Creates a party.",
```

O regex do valor era `[^"\r\n]*` e parava na aspa escapada. A substituição
trocou meia string e deixou o resto da linha solto, o arquivo perdeu a sintaxe,
`MsgStrID` virou nil — e aí **tudo que consome MsgStrID estourou em separado**:
`hotkey.lua:135`, `party_booking_function.lua:3`, `OptionInfo\CmdInfo:49`.

**Cinco dos seis diálogos não citavam o arquivo culpado.** Só o primeiro dizia
a verdade: `[string "buf"]:433: '}' expected near 'Party'`. É o mesmo padrão da
rodada de 2026-07-30, quando ~12 funções `queryNavi_*` estouraram por um único
`Navi_Map` nil: **volume de diálogo não indica volume de problema.** Ler o
primeiro erro, não o mais repetido.

Atingiu `msgstring_kr_s`, `msgstring_kr`, `skilldescript` e `itemInfo.lua`;
`skillinfolist` e `mapInfo` não têm escape nenhum e passaram limpos. Todos
foram restaurados do backup e refeitos.

O que ficou de proteção, além do regex corrigido: **`confere_linhas()` recusa a
gravação** se alguma linha de campo de texto deixar de casar com
`campo = "valor",`. Existe porque a linha estragada é **lexicamente válida** —
um verificador de balanceamento de aspas e chaves foi escrito, testado contra o
arquivo quebrado e **passou**. Detalhes no `ferramentas/LEIAME.md`.

### Confirmado no jogo — 2026-08-04

O cliente abre em português, **com acento**, depois do
`ferramentas/ajusta_charset_fonte.py`. Item, habilidade, quest, conquista,
mapa, UI e as abas do modal de habilidade, todos conferidos na tela.

Para conferir de novo depois de mexer:

1. Fechar e reabrir o cliente — ele lê esses arquivos **só na inicialização**.
2. Reiniciar o map-server, ou `@reloadmobdb` + `@reloadscript` (nome de
   monstro, NPCs nossos, mensagens do servidor).

### As abas do modal de habilidade

Resolvidas na mesma rodada, e por um caminho diferente do resto: a fonte foi o
**nosso próprio GRF**, não o bRO. Ver a correção do `skilltreeview.lub` na
seção da janela de habilidades, mais acima.

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

### Rodada de 2026-08-07 — a janela de missões não lia o `questid2display.txt`

O jogador reportou a janela de missões inteira em coreano, nas duas abas
(`ScreenShot\screenGuerra do Emperium023.jpg` e `024.jpg`), com a tradução de
quests marcada como concluída desde 2026-08-03.

**A medição que fechou o caso.** A quest ativa da foto era a **5153**, e ela está
em inglês no `data\questid2display.txt` (`5153#Refining tutorial (1)#`) —
traduzida, no disco, e mesmo assim coreana na tela. Logo o `.txt` **não é a
fonte**: quem desenha título e texto é o global `QuestInfoList`, do
`System\OngoingQuestInfoList_Sakray.lub`, e ele vence o `.txt`, que é só o
fallback de quando o ID não está na tabela. A aba RECOMENDADAS é o
`RecommendedQuestInfoList_Sakray.lub`, pelo mesmo caminho.

Esses dois arquivos são justamente **as cópias do `_True` criadas na rodada do
`_sak` vs `_Sakray`** (bem acima) — bytecode coreano do instalador da Gravity de
2021-11-03, que nunca teve versão traduzida instalada por cima. Igual ao que
aconteceu com o `itemInfo_true.lub` e o `mapInfo_*.lub`.

**Como foi resolvido:** partes `questinfo` e `questreco` no `traduz_ptbr.py`.

A **estrutura vem do arquivo coreano de 2021**, e não do ROenglishRE — mesma
razão do `parte_abas`. Metade dos campos não é texto e sim referência (`NpcSpr`,
`NpcNavi`, `BgName`, `IconName`, `RewardItemList`), e a versão do ROenglishRE é
de 2026: sprite que este exe não conhece derruba a janela. Só o texto é
importado, do bRO e, no que o bRO não tem, do ROenglishRE.

| | `questinfo` | `questreco` |
|---|---|---|
| entradas nossas | 7839 | 20 |
| em português (bRO) | 6318 | 1 |
| em inglês (ROenglishRE) | 5365 | 18 |
| sobraram em coreano | **0** | 1 (a `11`, `왕실 사냥 대회`) |

No `questinfo` a saída é a **união** dos três (11683 entradas): as que não estão
no arquivo de 2021 entram só com os três campos de texto, sem nenhuma referência
nova. No `questreco` só saem as 20 nossas — as 12 a mais do ROenglishRE trariam
`BgName` que este GRF não tem e a página viria com o fundo em branco. As chaves
batem uma a uma nos dois (a `77` é `바르문트의 바이오스피어` aqui e
"Varmundt's Biosphere" lá).

**Idempotência:** a primeira rodada troca bytecode por texto puro, então a
segunda não teria mais estrutura de onde partir. O coreano é congelado em
`<alvo>.COREANO` ao lado, e é sempre dele que se parte — mesma ideia do
`.INGLES` do `parte_msgtable`.

**A trava nova, e ela vale para todo `.lub` de texto que a gente gerar:**
`ROenglishRE\Tools\luac.exe -p`. O compilador Lua 5.1 de verdade. As travas por
linha do arquivo (`confere_linhas`, `confere_blocos`, contagem de aspas) deram
tudo certo e o arquivo **não compilava**: 37 descrições do bRO vêm no formato
`título\n\t\tcorpo`, e string Lua não aceita quebra de linha crua. A quebra faz o
par de aspas cair em duas linhas, as duas ficam com contagem ímpar, e o `split`
por `\r\n` não as separa — nenhuma trava de linha pega isso. Nos campos de lista
a quebra passou a virar item novo (que é o que ela queria dizer, e é como o bRO
mostra); no resto virou espaço.

---


---

## O quarto servidor — `web-server.exe`

Descoberto em 2026-08-04, depurando "escolho o emblema do clã e não acontece
nada". Não era o arquivo de imagem: era um servidor que nunca tinha subido.

> **CONFIRMADO in-game em 2026-08-04:** subido o `web-server`, o emblema entrou
> na primeira tentativa, com GIF. Nada mudou no arquivo de imagem nem na
> configuração do cliente — era só o processo que faltava.

**Rodávamos três servidores; o rAthena tem quatro.** O `web-server.exe` escuta
HTTP na porta **8888** (`conf/web_athena.conf`) e atende `/emblem/upload`,
`/emblem/download`, `/userconfig/*`, `/charconfig/*`, `/party/*`,
`/MerchantStore/*`.

Ele não é opcional em cliente moderno. Com `PACKETVER > 20200300`
(`src/config/packets.hpp:92`) — o nosso é 20211103 — o emblema de clã **deixou
de passar pelo map-server**. O cliente agora:

1. faz `POST http://<AssistAddr>/emblem/upload` via libcurl (a `libcurl.dll` da
   pasta do cliente é para isso);
2. só depois avisa o map-server da nova versão, pelo pacote `0x0b46`.

O `AssistAddr` sai de
`cliente\data\luafiles514\lua files\service_brazil\ExternalSettings_br.lub`, que
já apontava certo para `127.0.0.1:8888`. Quem escolhe a pasta `service_brazil`
é o `<servicetype>` do `clientinfo.xml`.

**O modo da falha é o pior possível: silêncio total.** Porta fechada, o `POST`
morre, e o cliente não mostra caixa de erro, não escreve no chat e não registra
nada na janela do map-server. O sintoma é o clique não fazer efeito — idêntico
para GIF e para BMP, o que empurra o diagnóstico para o lado errado (formato,
tamanho, transparência) e faz perder tempo convertendo imagem à toa.

**O resto da cadeia já estava pronto** desde a instalação, e foi conferido:

| Item | Onde | Estado |
|---|---|---|
| Tabelas `guild_emblems`, `user_configs`, `char_configs`, `merchant_configs` | schema `ragnarok` (de `sql-files/web.sql`) | existem |
| `use_web_auth_token: yes` | `conf/login_athena.conf` | ligado; preenche `login.web_auth_token` |
| `allow_gifs: yes` | `conf/web_athena.conf` | GIF liberado |
| `emblem_woe_change: yes` | `conf/inter_athena.conf` | WoE não bloqueia a troca |
| Credenciais do banco do web | `web_server_*` em `conf/import/inter_conf.txt` | preenchidas |

### Como subir — e a pegadinha

**Use `ferramentas/servidor.py`**, escrito em 2026-08-04 por causa deste bug:

```
python ferramentas/servidor.py status      # quem está no ar, e o que quebra se não estiver
python ferramentas/servidor.py subir       # sobe o que faltar, na ordem certa
```

O `subir` é idempotente — pula quem já está de pé —, então serve tanto para
subida do zero quanto para recuperar uma peça que caiu. Ver `ferramentas/LEIAME.md`.

A pegadinha que ele elimina: o `runserver.bat` sobe os quatro (chama `startWeb`),
mas **chamar os `.bat` individuais deixa o web de fora**. Foi o que aconteceu
aqui — `logserv.bat`, `charserv.bat` e `mapserv.bat` um a um, e o `webserv.bat`
nunca entrou na conta.

E a lição mais geral, que vale além deste caso: **o que executa ganha do que
está escrito.** Esta mesma "Referência rápida" listou *três* servidores por dias
sem ninguém notar. Documento envelhece errado em silêncio; um comando que
confere as portas não tem como mentir. Nota escrita fica para o "por quê", que
não dá para executar.

### Limites do emblema

| Regra | Valor | Onde |
|---|---|---|
| Tamanho máximo do arquivo | 50 KB | `MAX_EMBLEM_SIZE`, `src/web/emblem_controller.cpp:19` |
| Formatos aceitos pelo servidor | `BMP` e `GIF` | `emblem_controller.cpp:155` |
| Formatos listados pelo cliente | `*.bmp` e `*.gif` | filtro do próprio exe — **PNG não aparece na lista** |
| Pasta dos arquivos | `cliente\Emblem\` | o cliente também procura em `..\emblem\` e `..\..\emblem\` |

Só o dono do clã troca o emblema (`sd->state.gmaster_flag`).

---


---

## A conferencia offline dos mercados de Visuais e de Cartas — 2026-08-05

> O que falta fazer com eles esta em `PENDENCIAS.md`, secao 1. Aqui fica o
> registro do que foi conferido SEM subir o servidor.

O `npc/guerra/mercado_de_visuais.txt` foi escrito e registrado no
`scripts_guerra.conf` em 2026-08-05, mas o servidor **não foi reiniciado** —
então as três lojas ainda não subiram uma vez sequer. Conferido offline: as três
células são andáveis no `prontera.gat`, os três sprites existem tanto no
`npcidentity.lub` do cliente quanto no `npc.hpp` do rAthena, não há id repetido
nas listas, não há colisão de nome de NPC, e o maior `w4` tem 1243 caracteres
contra o teto de 2048 do parser (`npc.cpp`, `char w4[2048]`, que **trunca com
aviso** em vez de recusar).

Falta: `@reloadscript`, entrar em `prontera 155,155` e abrir as três lojas. É
abrir a loja que dispara a caixa modal de arte faltando, não equipar — e os 374
itens validaram 8 recursos cada, 2992 `[ok]` e nenhum `[FALTA]`.

O `mercado_de_cartas.txt` entrou logo depois, no mesmo estado: nove lojas em
`prontera` y=149/143/137, 1410 cartas, também sem uma subida sequer. Conferido
offline o mesmo conjunto — células andáveis, sprites nas duas tabelas, 1410 ids
distintos, nenhum repetido entre lojas.

**Nele há uma coisa a mais para olhar na primeira subida**, porque é a primeira
vez que usamos o truque: a loja de arma carrega 255 cartas na própria linha e as
outras **104 entram por `npcshopadditem` num `OnInit`**. Se o `OnInit` falhar, a
loja abre com 255 e **não dá erro nenhum** — o sintoma é só a lista curta.
Conferir contando: `Carta de Arma` tem de mostrar 359.

O caminho existe porque o parser copia o quarto campo para um `char w4[2048]` e
**trunca com aviso** em vez de recusar; a lista de arma dá 2804 caracteres. O
corpo de um `script` não tem esse teto — o `npc_parse_script` procura o `,{` no
buffer original, não no `w4`.

---

## A janela de refino — teto em +16 e a Bênção do Ferreiro (2026-08-07)

Começou como suspeita de configuração desligada: a Bênção do Ferreiro não
aparecia disponível ao refinar um Cocar do Orc Herói **+6**. Não estava
desligada — estava fazendo exatamente o que o `db/re/refine.yml` do rAthena
manda, e o que ele manda não é o que o bRO fazia.

### O que estava acontecendo

Quem acende o slot da bênção é o servidor, em `clif_refineui_info`
(`clif.cpp`): ele manda `p->blacksmithBlessing = info->blessing_amount`, e o
cliente desenha o slot morto quando esse valor é `0`. O valor sai do
`BlacksmithBlessingAmount` do `refine.yml`, que no rAthena só existe a partir
do `Level: 8`.

E `Level: 8` **não** quer dizer "item +8". A armadilha subiu para o
`CLAUDE.md` §5: o leitor faz `refine_level -= 1` e compara com o refino atual,
então `Level: 8` é a tentativa de sair do +7 para o +8. Era o degrau seguinte
ao do print — daí o slot apagado.

### A tabela do rAthena não é a do bRO

A descrição do item no cliente, que veio do bRO e é o que o jogador lê antes de
comprar, traz a tabela inteira — e ela discorda do rAthena em seis dos oito
degraus:

| Refino | descrição (bRO) | rAthena |
|---|---|---|
| +6 → +7 | 1 | não aceitava |
| +7 → +8 | 1 | 1 |
| +8 → +9 | 1 | 2 |
| +9 → +10 | 1 | 4 |
| +10 → +11 | 1 | 7 |
| +11 → +12 | 1 | 11 |
| +12 → +13 | 15 | 16 |
| +13 → +14 | 22 | 22 |
| +14 → +15 | não aceita | não aceita |

Ficou valendo a descrição, por decisão de 2026-08-07. O motivo não é nostalgia:
a janela de refino **mostra a quantidade exigida** ("0/4"), então divergência
entre o que o item promete e o que o servidor cobra aparece na tela, não fica
escondida. Repare que o topo da faixa já estava certo — o +13 → +14 sempre
funcionou e o +14 → +15 nunca funcionou, nos dois lados. Faltava só o degrau de
baixo, e os custos do meio estavam caros.

Mora em `db/guerra/refine.yml`, importado pelo rodapé do `db/refine.yml`. O
arquivo mexe **só** no `BlacksmithBlessingAmount`: o leitor de YAML mescla por
chave, então omitir `Chances` preserva as taxas do rAthena inteiras.

> `db/refine.yml` é o ponto de entrada do banco de refino, **não**
> `db/re/refine.yml` — o `getDefaultLocation()` do `RefineDatabase` devolve
> `db/refine.yml`, e é ele que importa o `re/`, o `pre-re/` e o `import/`.
> Procurar rodapé no `db/re/refine.yml` não acha nada e dá a impressão errada
> de que a base não aceita import.

### O teto em +16

Pedido junto: não deixar tentar o +17. O caminho barato seria apagar os níveis
17 a 20 do `refine.yml`, e ele não serve por dois motivos, os dois registrados
no `CLAUDE.md` §5 e no cabeçalho do `src/custom/refino.hpp`:

1. **Import não remove.** O leitor só mescla — acrescenta e sobrescreve campo,
   nunca tira nível. Cortar exigiria editar arquivo do rAthena.
2. **Baixar o `MAX_REFINE` para 16 quebra a base inteira.** Nível acima do
   `MAX_REFINE` não é "pulado" apesar do que o aviso diz: o `return 0` logo
   abaixo descarta o **grupo todo**. Armor e Weapon deixariam de carregar e
   ninguém refinaria mais nada, com um aviso no log de aparência inofensiva.

E nenhum dos dois daria a mensagem que o jogador lê. Ficou em C++, em
`src/custom/refino.hpp`, com duas chamadas na janela de refino: uma ao escolher
o item (a janela abre sem minério nenhum e o aviso vai para a caixa de chat) e
outra no pedido de refino em si (recusa calada, para cliente remendado).

**Só a janela precisou de trava.** Os três NPCs refinadores param no +10
sozinhos — `npc/merchants/refine.txt`, `advanced_refiner.txt` e o
`re/merchants/ticket_refiner.txt` que ligamos, todos comparando
`getequiprefinerycnt` com 10 ou com o nível do bilhete. Acima de +10 a janela
era o único caminho. Fora do alcance de propósito: `@refine` de GM e
`successrefitem` de script.

O número não está cravado no C++: é `refino_teto: 16` no
`conf/guerra/battle_guerra.txt`, pela mecânica de battle config custom que o
rAthena já oferece (`src/custom/battle_config_struct.inc` e
`battle_config_init.inc`, até então vazios). Muda com `@reloadbattleconf`, sem
recompilar; `0` desliga a trava.

A mensagem é a **1550** do `conf/guerra/map_msg_guerra.conf`, e não uma string
no `.cpp` — texto que o jogador lê é cp1252, e arquivo de código não é lugar
para guardar acento. A faixa 1550+ passou a ser nossa: o rAthena para na 1540 e
o teto da tabela subiu para 1600 no `src/custom/defines_pre.hpp`, que é o lugar
que o próprio rAthena documenta para isso.

**Validado no jogo em 2026-08-07**, no mesmo dia em que foi escrito — a bênção
acendendo no +6 e o teto recusando o +17, com a mensagem chegando na caixa de
chat com os acentos certos. Saiu do `PENDENCIAS.md`.

---

## O Corredor Fantasma — a sala de MVP de Comodo (2026-08-08)

Pedido assim: *"tínhamos no jogo o conceito de Cheffênia, que mais tarde virou
Corredor Fantasma. A mais recente ficava em Comodo, é um mapa que você entra
para matar apenas MVPs."*

### O que se descobriu antes de escrever uma linha

**O rAthena não tem nada disso.** O Corredor Fantasma é conteúdo exclusivo do
bRO — evento temporário, com três andares, encerrado junto com o servidor. Os
chefes de lá eram clones ("Fantasma de Rá", "Fantasma do Bode"), com elemento
trocado e sem drop de carta, e não existem no `mob_db` do vendor.

**Mas o vendor tem as peças.** Três achados que definiram o trabalho inteiro:

| O quê | Onde estava |
|---|---|
| O mapa `vis_h01` | `.rsw` e `.gat` no GRF do cliente, mais `db/map_index.txt`, `db/map_cache.dat` e `conf/maps_athena.conf` — nas quatro |
| A **Flor Visionária** | item `25503`, `Flower_V`, **já com o nome em português** |
| O nome PT do mapa | `data\mapnametable.txt` do override já dizia "Arena Fantasma (1)", da tradução de 2026-08-03 |

O nome do mapa foi o que destravou tudo: o pedido veio com "lá fora o evento se
chama *Corridor of Phantoms*, e o mapa é o `vis_h01`". Sem isso a busca teria
parado na bROWiki, que não publica código de mapa — e o caminho alternativo era
escolher um mapa parecido à mão.

### O que ficou de fora do bRO, e por quê

Três cortes, todos pedidos explicitamente:

- **A entrada é de graça.** No bRO comprava-se um Selo Visionário: grátis valia
  1 hora com recarga às 4 da manhã, ou 4 horas por 10.000.000z. Aqui não há
  preço, duração nem recarga. O item `25504` (Selo Visionário) segue no vendor
  sem uso nenhum.
- **Não há NPC de troca.** Lá 10 Flores viravam um Prêmio Visionário, e a cada
  200 trocas do servidor inteiro havia 1% de sair um Cartão Visionário (carta de
  MVP). **Consequência assumida: a Flor cai e não tem onde ser gasta.** Abrir o
  destino dela depois não exige mexer na sala — basta um NPC que consuma o
  25503.
- **Dano normal.** No bRO todo dano do jogador era reduzido em 30%, para o mapa
  não virar farm fácil.

E uma simplificação: **os três andares viraram uma sala só.** `vis_h02..04`
existem no GRF e ficaram vazios.

### O elenco: por que não são os "Fantasma de X"

A lista da bROWiki é de clones, e vários apelidos não mapeiam de volta para um
MVP conhecido ("Fantasma do Fofinho", "do Pesar", "da Malícia", "do Piano"). Com
a decisão de usar os MVPs normais — que o pedido aceitou explicitamente, desde
que largassem a Flor — a adivinhação sumiu junto.

Sobraram **65 tipos de chefe**, tirados dos 121 mobs que o `mob_db` marca com
`MvpExp` (viraram 130 no chão no mesmo dia — ver o fim desta seção).
O critério de corte foi um só: **chefe que existe sozinho no campo entra; chefe
que só faz sentido dentro da instância dele, não.** Os 56 descartados são 21
cópias de evento (`E_*`), 5 versões Infinitas, 7 de masmorra memorial, 2
Pesadelo, 2 Ilusão, 9 de instância, 6 de evento/piada e 4 variantes de cor da
Faceworm Queen. O que sobrou cobre quase inteira a lista dos três andares do
bRO.

### A armadilha que custou meia hora — e subiu para o `CLAUDE.md`

**Comentário no fim de uma linha de spawn entra dentro do nome do evento.** O
`npc_parsesrcfile` enche o `w4` *"to end of line"*, e o `npc_parse_mob` lê o
evento com `%77[^,]`, que só para na vírgula. O `mob_parse_dataset`
(`src/map/mob.cpp:446`) só tira a aspa quando ela é o **último** byte — com o
comentário atrás, não é.

O resultado é falha calada: o chefe nasce, anda, morre, e o evento nunca
dispara. Nada no log aponta para a linha. Por isso as 65 linhas de spawn são
mudas e quem diz quem é quem é a tabela do cabeçalho do arquivo.

Foi por essa mesma leitura que se descobriu o resto da mecânica de spawn:
`vis_h01,120,120,70,70` **não** é "70 células de lado" — o `mob_spawn` chama
`map_search_freecell` com `xs-1` e sorteia em `rnd_value(bx-rx, bx+rx)`, ou seja
120 ± 69. O retângulo foi escolhido para (1) excluir as 479 células soltas que o
`.gat` do `vis_h01` tem na linha y=239, que deixariam um chefe inalcançável, e
(2) deixar a chegada do jogador fora dele, para ninguém desembarcar em cima de
um Beelzebub.

### Como se provou que carregou

O log limpo não prova nada — provaria igual se o `npc:` novo tivesse sido
ignorado. A prova foi uma **sonda**: uma 66ª linha de spawn com um mob inexistente,
um reinício, e a confirmação de que o erro saiu **apontando para o arquivo e para
a linha certa**:

```
[ Error ] : npc_parse_mob: Unknown mob ID 999999 (file 'npc/guerra/corredor_fantasma.txt', line '393').
```

Isso provou de uma vez que o arquivo é lido, que a linha do `scripts_guerra.conf`
funciona, que o formato de spawn é aceito e que as outras 65 passaram sem uma
queixa. A sonda foi removida e o servidor reiniciado limpo.

**Falta ver no jogo** — está no `PENDENCIAS.md`.

### Primeiro teste em jogo, e os dois ajustes que ele pediu (2026-08-08)

O Corredor entrou funcionando na primeira subida — o mapa desenhou, o cliente
não caiu, os chefes nasceram e a flor caiu. Duas coisas apareceram só jogando:

**A flor virou chuva.** Eram 2 garantidas por morte, e com 65 chefes voltando de
2 em 2 minutos isso enche o inventário sem esforço — ainda mais sendo item sem
onde ser gasto. Passou para **1 flor com 30% de chance**. Os dois números são
`.FlorQtd` e `.FlorChance` no `OnInit`, e não há outro lugar para mexer. O
sorteio é `rand(100) < .FlorChance`, e o `rand(100)` do rAthena devolve 0..99 —
então 30 é 30% cravado, não 31%.

**A sala estava vazia demais.** 65 chefes espalhados em 240x240 dão muita
caminhada entre um e outro. O número **dobrou para 130** — 65 tipos, dois de
cada, pelo terceiro campo da linha de spawn (`,2,` no lugar de `,1,`). Cada um
dos dois tem vida e renascimento próprios; não é um mob que nasce duas vezes.

> **Isso acendeu uma dependência que antes não existia.** O `mob_count_rate` do
> `conf/battle/monster.conf` multiplica a quantidade, mas **só quando ela é maior
> que 1** (`if (mob.num > 1 && battle_config.mob_count_rate != 100)`, em
> `src/map/npc.cpp`). Enquanto era 1 por linha, essa taxa não alcançava a sala.
> Agora alcança. Hoje ela é 100, então 2 é 2 — mas mexer nela passou a mexer no
> Corredor, e está anotado no cabeçalho do arquivo.

As duas mudanças foram feitas **direto nos bytes cp1252**, por script com
asserção em cada troca — o arquivo tem acento no diálogo, e uma delas era
justamente a fala que prometia a flor em toda morte. Passar por UTF-8 para
trocar uma linha é exatamente como os acentos do `item_db.yml` viraram U+FFFD em
2026-08-07.

**Validado no jogo em 2026-08-08**, no mesmo dia em que foi escrito: o mapa
desenhou, o cliente não caiu, os chefes nasceram e a flor caiu. Saiu do
`PENDENCIAS.md` §1. O que continua sem confirmação in-game são só os dois
números ajustados **depois** desse teste — a flor a 30% e os 130 chefes —, que
foram conferidos no boot do servidor, não jogando. Está anotado no §1c.

### O efeito colateral que o teste revelou — e não era do Corredor

Para testar, o personagem `Abemus` foi levado pela Teletransportadora ao
**"Sticky Sea"** (`1@slug`) e o cliente caiu, com o personagem preso lá: ao
reconectar ele voltava ao mapa quebrado e caía de novo. É exatamente a regra 6
do `CLAUDE.md`, e desta vez completa:

| | |
|---|---|
| `1@slug` no `db/map_index.txt` do rAthena | **sim** (linha 1215) — por isso o servidor aceitou o warp |
| `.rsw`, `.gat`, `.gnd` no GRF do cliente | **nenhum dos três** |
| Apelido no `resnametable.txt` | **não** — não é o falso negativo que o `pvp_n_1-5` dá |

Saída pelo banco, com o personagem offline (`online = 0`): `UPDATE char SET
last_map='prontera', last_x=152, last_y=188`. O `save_map` dele não tinha sido
contaminado, e nenhum outro personagem estava preso em mapa `1@`/`2@` — foi
conferido na mesma consulta.

**O que isso revelou é maior que o incidente:** a Teletransportadora
(`npc/custom/warper.txt`, o do próprio rAthena, montado para cliente moderno)
**oferece destinos que derrubam este cliente**, e o `1@slug` não é o único. A
varredura do menu inteiro contra o GRF não foi feita — está no `PENDENCIAS.md`.
