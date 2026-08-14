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

Os títulos saem em **ASCII de propósito**: nenhum precisa de acento no
vocabulário do bRO, então eles funcionam mesmo antes do patch de charset.

**2026-08-11 — os títulos foram encurtados para no máximo 7 caracteres, e o
motivo não é estética: os longos escondiam abas inteiras.** A aba dessa janela
é escrita na **vertical**, uma letra embaixo da outra (~13px por letra), então
o comprimento do rótulo não gasta largura — gasta **altura**, e a altura da
coluna é dividida entre todas as abas do personagem. Num Sura,
`Aprendiz-1a` (11) + `2a-Transcend.` (13) consumiam a coluna inteira e a
terceira aba (`3a`) ficava cortada ao meio, **fora do alcance do clique**. A
habilidade concedida por equipamento (Proteção Arcana, da Fada do Éden +11)
estava dentro dela, e o jogador simplesmente não conseguia chegar nela — sem
erro, sem log, só uma aba que não terminava de desenhar.

Os nove rótulos hoje: `Apr-1a`, `2a-Tr.`, `3a`, `4a`, `NV-EX1`, `Sup.EX1`,
`Sup.EX2`, `Doram`, `Espir.`. O teto virou trava no código
(`LIMITE_ABA`/`checa_abas` no `traduz_ptbr.py`), que recusa gerar o arquivo se
alguém alongar um rótulo — comentário não segura isso sozinho.

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

### Tamanho da fonte — RESOLVIDO em 2026-08-09, e não onde se procurava

O cliente **não tem** opção de tamanho de fonte: nem Setup.exe, nem menu, nem
`OptionInfo.lua`. O `/font` da lista de comandos troca a fonte do **chat**, e
só. E resolução não resolve: a interface é de pixel fixo, então subir a
resolução deixa tudo **menor** — medido a 1900×1080, onde o nome do mapa na
seleção de personagem ficou ilegível.

Hoje quem faz isso é `ferramentas/ajusta_tamanho_fonte.py`, que desvia o
distribuidor de fontes do cliente. **O `--verificar` diz em quanto está** — não
perguntar a este arquivo.

#### A versão anterior da ferramenta nunca funcionou, em nenhum valor

É o que a seção realmente ensina, e custou uma tarde. Ela somava na altura do
`LOGFONTA` nos 8 `CreateFontIndirectA` do exe. Aquilo **não tem efeito
nenhum** — e o script confirmava o próprio trabalho, respondendo *"8 ja
desviadas"*, porque procurava o formato do próprio stub. Aplicado, confirmado,
inócuo.

O pedido chegou como "já pedi e não fizemos". Estava em `+2`, e a primeira
reação — subir para `+4`, depois `+6` — só gastou rodadas. Três frentes
independentes fecharam o caso:

1. **A/B de captura entre +2 e +6.** Recortada e ampliada a mesma janela de
   informações básicas, os glifos são idênticos ao pixel; só o Weight muda.
   Comparar tamanho a olho, em tela cheia, não teria decidido nunca.
2. **Um stub que forçava SUBLINHADO** (`lfUnderline`, offset 0x15) além da
   altura. Sublinhado não depende de tamanho, de layout nem de caixa fixa — e
   não apareceu em lugar nenhum do jogo.
3. **A/B entre exe patcheado e exe original**, byte a byte revertido:
   indistinguíveis.

A regra que sai daí: **antes de subir número, provar que o patch chega à tela.**
Uma marca visual que não dependa do efeito procurado — sublinhado, negrito,
outra face — responde numa rodada o que tentativa e erro não responde em cinco.

#### Onde o texto realmente nasce

```
0x004C4938  call 0x004C3660    ; pega o HFONT
0x004C4940  call [SelectObject]
0x004C494D  call [GetTextExtentPoint32W]   <- MEDE

0x004C4A6E  call 0x004C3660    ; a MESMA funcao
0x004C4A79  call [SelectObject]
0x004C4A89  call [TextOutW]                <- DESENHA
```

`0x004C3660` é o distribuidor de fontes, e **medição e desenho tiram a fonte
dele**. Por isso o desvio vai ali: fonte trocada só no desenho daria texto
grande medido como pequeno — cortado e sobreposto. É thiscall, cinco
argumentos, `ret 14h`; o **segundo** argumento é o tamanho pedido, medido
comparando `--fixo` com `--bonus` na mesma caixa de diálogo.

A fonte nova sai de `CreateFontA`, que estava importada com **zero** chamadas —
livre. Charset 0 (ANSI), o mesmo que faz o acento cp1252 aparecer.

Duas coisas do caminho que valem além deste patch:

- **Contar call site só por `ff 15 [IAT]` engana.** Foi assim que a ferramenta
  antiga concluiu "CreateFontA: zero chamadas" e escolheu o alvo errado. Há
  `mov reg,[IAT]` + `call reg`, thunk do compilador, delay-import e cave de
  patch anterior. Aqui todos foram conferidos, um a um.
- **`int3` não prova nada em função com SEH.** Põe-se `int3` no stub esperando
  que o processo morra se aquilo executar; `0x004C3660` abre com
  `push 0x00C7E270; push fs:[0]`, e a exceção pode ser engolida. O cliente sobe
  vivo nos dois casos, e o teste não decide nada.

#### O que o desvio NÃO pega

Título de janela e botão saem do outro caminho de texto (`TextOutA`, em
`0x004D83BA`) e continuam do tamanho original. Medido: com o desvio ligado,
"Do you agree?" cresce e "message"/"OK"/"cancel" não. Se um dia incomodar, o
alvo já está identificado.

#### Os valores aprovados, e como se chegou neles

> **O `--teto 11` desta seção durou um dia e estava errado** — não pelo número,
> pela forma. Ver "A hierarquia tipográfica achatada", logo abaixo. O estado
> aprovado hoje está lá.

O estado no jogo em 2026-08-09 era face **Arial**, **`--bonus 0`**,
**`--teto 11`**, sem suavização.

Dois passos da calibragem valem registro porque contrariaram a intuição:

- **O tamanho certo veio de ZERAR o bônus, não de subir.** Depois de `+4` e
  `+2` ficarem grandes, `+1` ainda parecia levemente grande, e a pergunta que
  destravou foi do dono do servidor: se `+1` já está acima do ponto, `+0` não
  precisa ser o texto minúsculo de antes. **E não é** — nós não aumentamos a
  fonte do cliente, nós **trocamos** a fonte. Face diferente na mesma altura em
  pixels não desenha do mesmo tamanho, então `+0` já é mudança. A ferramenta
  chegou a recusar `0` por uma validação sem fundamento minha, que foi tirada;
  bônus negativo também é válido, pelo mesmo motivo.
- **O `--teto 14` não fez efeito, e foi esse o dado útil.** Provou que as
  linhas do status pedem 14 ou menos, matando a hipótese de que pediam um corpo
  muito maior. A diferença era de poucos pixels, amplificada pela face. De 14
  para 12 a janela encolheu sem tocar no resto; 11 fechou.

O contorno rosa que apareceu no caminho era ClearType: `DEFAULT_QUALITY` deixa
o Windows suavizar por subpixel, e o franjado colorido sobrevive à composição
do texto como textura. `NONANTIALIASED_QUALITY` resolveu, e é o que a fonte
original do cliente sempre foi.

#### Calibrar e olhar — a interface é de caixa fixa

Com `--fixo 20` o painel de seleção cortou "Interior de Prontera" em
"Interior d" e os valores do inventário se sobrepuseram. Por isso o padrão é
`--bonus`, que soma sobre o tamanho pedido e preserva a proporção entre título,
corpo e rodapé. Subir de 4 em 4 e olhar.

O cache por tamanho **não é enfeite**: sem ele cada pedido criaria um HFONT
novo, e o processo vazaria handles até cair.

### A hierarquia tipográfica achatada — 2026-08-10

O pedido chegou como um detalhe: *"depois que ajeitamos a fonte do jogo,
acabamos mexendo na fonte que anuncia o nome do mapa — o nome e o subtítulo da
cidade estão pequenos"*. Não era um detalhe, e não era o banner.

**O `--teto 11` não limitava exageros: ele achatava a tipografia inteira do
cliente num corpo só.** O jogo tem oito corpos distintos; todos batiam no teto e
saíam com 11. O nome do mapa ficava do tamanho do chat, os títulos de janela
também, e cada texto isolado parecia plausível — que é exatamente por que
passou. A hierarquia sumiu inteira e o sintoma que apareceu foi o do texto que
mais destoava.

#### O que denunciou, e por que foi rápido

**O cache tinha uma única entrada preenchida.** Ele é indexado por
`min(pedido, teto)`, então ler a memória dos três clientes no ar e achar só o
índice 11 prova que *nada* no jogo pede menos de 11 — ou seja, tudo estava
batendo no teto. Uma leitura, e a hipótese "o banner está pequeno" virou "não
existe mais hierarquia".

Isso virou o `--tabela`, que lê o cache do processo vivo por
`ReadProcessMemory`. Com o índice passando a ser o tamanho **cru**, o cache
deixa de ser só cache e vira **histograma**: as entradas não-zeradas são a
lista do que o cliente pediu. Medido em Prontera, são oito e só oito —
`11, 12, 13, 14, 16, 17, 18, 48`, e o **48 é exclusivo do nome do mapa**.

É a mesma lição da subseção anterior, do outro lado: lá, provar que o patch
chega à tela; aqui, **medir o que o cliente pede antes de escolher o número**.
Sem a medição, calibrar custa um fechar-e-reabrir por chute.

#### Por que teto virou faixa

As duas pontas não cabem num número só. A janela de informações básicas pede
até 14 e precisa ser achatada; o nome do mapa pede 48 e precisa passar. Então:

```
pedido <  15  ->  altura = min(pedido, 11)     a janela, como já estava
pedido >= 15  ->  altura = pedido              nome do mapa e títulos, intactos
```

O corte em 15 não é chute: é o menor valor que segura a janela sem tocar no
resto, e sai direto do `--teto 14` de 2026-08-09 não ter feito efeito nela.

O stub passou a **ler** a altura de uma tabela de 64 bytes no exe em vez de
calculá-la. Consequência prática: recalibrar deixou de ser patch e virou
comando — foi assim que o nome do mapa foi de 48 para 46 e depois para 42 sem
tocar em uma linha de assembly.

#### O estado aprovado hoje

Face **Arial**, **`--bonus 0`**, **`--teto 11`**, **`--livre 15`**,
**`--altura 48=42`**, **`--negrito 48`**, sem suavização — e são os padrões da
ferramenta, então rodá-la sem argumento reproduz isso.

O 42 e o negrito são do nome do mapa, pedidos pelo dono do servidor depois de
ver o corpo natural (48) na tela. Começou como "dois pontos menor"; levantei que
46 é uma diferença de 4% e sumiria ao lado do negrito, e ele fechou em 42.
**Número de tipografia se decide na tela, não na aritmética.**

#### O que o exe permitiu, e o que não permitiu

A `.xdiff` tem `VirtualSize` 0x1000 e **`SizeOfRawData` 0x400** — metade da
seção não existe em disco. O cache sempre morou nessa metade e funciona por
sorte estrutural: o carregador zera, e zero é o estado inicial certo para ele.
**A tabela de alturas não podia ir junto** — seria lida como zeros. Foi para um
vão de 64 bytes entre dois stubs do NEMO, depois de conferir que nenhuma
constante aponta para lá e que nenhum `e8`/`e9` do `.text` aterrissa na faixa.

O negrito viaja no **bit 7 do byte de altura** pelo mesmo aperto: depois do mapa
vem stub do NEMO, e o maior vão restante tem 40 bytes. E o stub, com 101 dos 112
bytes disponíveis, só coube guardando o índice em `ebx` por cima da chamada —
salvo-pelo-chamado no Win32 — em vez de reler `[esp+8]` e relimitar depois.

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

---

## A Flor Visionária ganhou destino — Alleria, Saback e a segunda Máquina (2026-08-08)

Três NPCs em Comodo, a poucos passos da porta do Corredor Fantasma, fechando o
circuito que a sala tinha deixado aberto no mesmo dia:

| NPC | Onde | Sprite | O que faz |
|---|---|---|---|
| Máquina | `comodo 214,185` | 564 `2_VENDING_MACHINE1` | `duplicate` da de Prontera — mesma loja de troca |
| Alleria | `comodo 221,182` | 612 `4_F_PINKWOMAN` | compra **todas** as Flores Visionárias da bolsa, a 1 Moeda Nova cada |
| Saback | `comodo 223,182` | 468 `4_M_KNIGHT_BLACK` | só fala — aponta o jogador para a Alleria |

### O circuito que se fechou

Até aqui a Flor Visionária (25503) caía em 30% das mortes dos 130 chefes e
**não tinha onde ser gasta** — era troféu, e estava escrito assim no cabeçalho
do `corredor_fantasma.txt` e no `PENDENCIAS.md` §1c. Agora:

```
Corredor Fantasma  ->  Flor Visionária (30% por chefe morto)
Alleria            ->  1 Moeda Nova por flor
Máquina de Comodo  ->  as dezoito linhas do barter, ali mesmo
```

A terceira peça é o motivo de a Máquina ter vindo junto: sem ela o jogador
venderia a flor em Comodo e teria de viajar a Prontera para gastar a moeda.

**A Alleria é a segunda fonte de Moeda Nova, e a primeira por esforço.** A
outra é o Logue e Ganhe, que entrega 240 por **conta** por mês independente de
jogar. Esta não tem teto: quem caçar mais chefe, ganha mais. Se um dia a moeda
inflacionar, os dois números a mexer são o `.preco` do `OnInit` da Alleria e o
`.FlorChance` do `corredor_fantasma.txt` — está anotado nos dois cabeçalhos.

**Não é a troca do bRO.** Lá se levavam 10 Flores ao Espectro por um Prêmio
Visionário, com 1% de sair um Cartão Visionário (carta de MVP) a cada 200 trocas
do servidor inteiro. Aquilo foi cortado a pedido em 2026-08-08 e continua
cortado — aqui a flor vira moeda, uma por uma, sem sorteio e sem contador.

### Por que a compra leva tudo de uma vez, e por que não há `checkweight`

"Sim, toma!" consome **todas** as flores da bolsa. Foi assim que o pedido veio, e
poupa a caixa de `input` — que pede um número e aceita zero, e teria de ser
validada à mão.

A ordem das duas linhas importa, e é o oposto da intuição:

```
delitem .flor, .@qtd;
getitem .moeda, .@pago;
```

O `delitem` esvazia o slot inteiro da flor, então o `getitem` seguinte **sempre**
tem onde entrar; e a flor pesa 10 contra 0 da Moeda Nova, então a troca só alivia
a bolsa. Um `checkweight` **antes** do `delitem` recusaria justamente quem está
com a bolsa cheia de flores — que é o cliente desta NPC.

> Comparar com o `maquina.txt`: lá o `checkweight` também não existe, mas por
> outro motivo — a loja de troca já o faz sozinha, em `npc_barter_purchase`.
> Mesma ausência, razões diferentes; as duas estão escritas nos cabeçalhos.

### A segunda Máquina é `duplicate`, e isso tem consequência no código

```
comodo,215,185,6	duplicate(Máquina)	Máquina#comodo	564
```

Mesmo código, mesmo sprite, mesma loja flutuante — não há segunda cópia da fala
para sair de sincronia, e a mercadoria continua vindo de um lugar só
(`barters_guerra.yml`).

**As duas dividem o `.moeda` do `OnInit`, e isso não é acidente do rAthena:**
variável de escopo `.` mora no `st->script->local` (`src/map/script.cpp:3050`),
que pertence ao **script**, e o `npc_duplicate_sub` aponta o duplicate para o
script do original (`src/map/npc.cpp:4602`). Trocar o ID da Moeda continua sendo
uma linha, valendo para as duas.

O nome único é `Máquina#comodo`; o jogador lê só o pedaço antes do `#`, então as
duas se chamam "Máquina" na tela. Nome único repetido faria a segunda não nascer.

### O que foi conferido antes de escrever

A receita de sempre, e desta vez nada caiu:

| Conferência | Resultado |
|---|---|
| `4_F_PINKWOMAN` e `4_M_KNIGHT_BLACK` no `npcidentity.lub` **deste** cliente | **612** e **468** — batem com o `npc.hpp` do rAthena |
| `.spr` e `.act` na pasta de sprite de NPC do nosso `data.grf` | os quatro arquivos existem |
| Células `215,185`, `221,182` e `223,182` no `comodo.gat` do GRF | as três tipo 0, andáveis |
| NPC do rAthena por perto | só o `Muff`, em `comodo 224,187` — sem sobreposição |
| Nomes `Alleria` e `Saback` no `npc/` inteiro | livres |

A leitura do `npcidentity.lub` passou pela armadilha do `RK` já documentada no
`CLAUDE.md` §5: o parser trata `LOADK` em registrador além do índice 255, e por
isso leu **4.578** entradas. A prova de que estava certo veio de graça —
`JT_4_M_JOB_KNIGHT` apareceu **ausente**, que é exatamente o sprite que caiu na
conferência de 2026-08-05.

### A primeira subida falhou — e a lição subiu para o `CLAUDE.md`

A Máquina de Comodo apareceu; a Alleria e o Saback, não. O `@reloadscript` deixou
**uma linha** no `log/map-msg_log.log`:

```
[ Error ] : npc_parsesrcfile: Unknown syntax in file
            'npc/guerra/flores_da_ordem.txt', line '64'. Stopping...
 * w1=pc\ do
```

A linha 64 era **comentário de cabeçalho**. O gerador do arquivo passou por um
heredoc do Bash que **comeu a contrabarra dupla**: o texto `data\\sprite\\npc\\`
chegou ao Python como `data\sprite\npc\`, e ali o `\n` virou quebra de linha de
verdade. A frase partiu em duas, e a metade órfã (`pc\ do`) deixou de começar
com `//`.

**O estrago foi desproporcional à causa, e é esse o ponto:** o
`npc_parsesrcfile` (`src/map/npc.cpp:5646`) **para de ler o arquivo** na primeira
linha que não entende. Os dois NPCs estavam 25 linhas abaixo e simplesmente não
existiram — sem erro próprio, sem sintoma no jogo além da ausência.

E o log não entrega isso de graça: essa única linha de `[ Error ]` fica soterrada
sob **centenas** de `[ Warning ]` inofensivos dos mercados de cartas. Quem lê o
fim do log vê aviso de preço de carta, não o erro. Procurar por `Unknown syntax`.

As duas armadilhas — a do parser e a do heredoc — estão no `CLAUDE.md` §5. A
conferência que passou a existir por causa disto: **toda linha antes da primeira
definição de NPC tem de começar com `//`**, verificada por varredura depois de
gerar o arquivo.

> A mesma frase quebrou na tabela de conferências deste histórico, gerada pelo
> mesmo caminho. Foi consertada junto.

### Confirmado no jogo, e os ajustes que o teste pediu (2026-08-08)

Depois da correção o `@reloadscript` levantou os dois, e a cena foi ajustada no
mesmo dia:

**A Máquina saiu de `215,185` para `214,185` e virou para a esquerda** — o
`facing` foi de 6 (leste) para 4 (sul). Com a câmera padrão deste cliente as
direções caem na diagonal da tela, então o ponto cardeal não é o que se vê:

| facing | como aparece |
|---|---|
| 6 (leste) | virada para a **direita** |
| 4 (sul) | virada para a **esquerda** |

A tabela está no cabeçalho do `maquina.txt`, porque é o tipo de coisa que se
redescobre por tentativa toda vez.

**Dois guardas novos**, `comodo 221,184` e `224,184`, sprite 966
`4_M_RUSKNIGHT`, um atrás da Alleria e um atrás do Saback. Só falam. Os dois se
chamam "Guarda da Ordem" na tela; o que os separa é o sufixo depois do `#`, que o
cliente não desenha.

> **As duas falas são metalinguagem** — as duas citam o servidor vazio ("não tem
> mais ninguém no server", "com o servidor vazio a Ordem decretou guarda"). É
> deliberado, e é a primeira coisa a reescrever no dia em que o servidor encher.
> Está anotado no cabeçalho e no `scripts_guerra.conf`.

Os dois usam o **mesmo** sprite de propósito: são tropa, e é o Saback que tem de
destacar. Nasceram com o 470 `4_M_KNIGHT_SILVER` e trocaram para o 966 no mesmo
dia, a pedido — e o 966 passou pela mesma conferência dos outros, que **vale
mesmo quando o pedido já traz o número pronto**: `npcidentity.lub` deste cliente
(966, batendo com o `npc.hpp`) e `.spr`/`.act` no `data.grf`.

### O emote da Alleria — `/vem` de 4 em 4 segundos

Mesmo par do Edgard de `prontera 170,199`: `initnpctimer` no `OnInit`, e um
`OnTimer4000` que solta o emote e rearma. O intervalo é o **nome do label**, não
um argumento — mudar de 4s para outro valor é renomear `OnTimer4000`, não mexer
no `initnpctimer`.

**O número é `ET_COMEON` (44)**, o emote de chamar com a mão, que o próprio
rAthena comenta como `/com, /comeon` no `emotion_type` (`src/map/clif.hpp:308`).
Conferido no `emotionlist.lub` do cliente, não chutado: a tabela de lá declara as
`ET_*` na mesma ordem do `clif.hpp`, e `ET_COMEON` cai no índice 44 nas duas. O
`ET_HUNGRY` do Edgard cai no 37 nas duas, o que revalida o método de 2026-08-04.
Lido do `.lub` do bRO, porque o do nosso `data.grf` está com a flag DES.

**O que não deu para provar:** que `/vem` é o nome bRO **deste** emote. Comando
de emote é string do executável, e não existe em nenhum dos dois desta máquina —
o nosso é kRO com os comandos em coreano, e o `Ragexe.exe` do bRO está
empacotado. `vem`, `fome` e `comeon` não aparecem em nenhum deles. A ligação é
pelo sentido, e é a mesma aposta que o `/fome` do Edgard fez e acertou. Se sair
o emote errado, é um número no `OnTimer4000`.

### O sprite dos guardas — 966, e a conferência valeu do mesmo jeito

Os guardas nasceram com o 470 `4_M_KNIGHT_SILVER`, escolha nossa, e trocaram para
**966 `4_M_RUSKNIGHT`** no mesmo dia, a pedido. Os dois usam o **mesmo** sprite de
propósito: são tropa, e é o Saback que tem de destacar.

> **A conferência foi refeita mesmo com o número vindo pronto no pedido**, e é
> essa a parte que vale guardar: `4_M_RUSKNIGHT` está no `npcidentity.lub` deste
> cliente valendo 966, batendo com o `npc.hpp`, e tem `.spr`/`.act` no
> `data.grf`. Um número correto no pedido não substitui a checagem — foi
> exatamente assim que o `4_M_JOB_KNIGHT` caiu em 2026-08-05.

O 470 saiu de toda a documentação junto com o código, para não sobrar número
velho contradizendo o arquivo.

### Estado — validado no jogo em 2026-08-08

A cena inteira de Comodo foi vista no jogo e está **fora do `PENDENCIAS.md`**: a
Máquina em `214,185` virada para a esquerda, a Alleria, o Saback, os dois guardas
com o sprite 966 e o emote saindo sozinho de 4 em 4 segundos.

**O `ET_COMEON` (44) era mesmo o `/vem`.** Era a única peça que não tinha como ser
provada offline — comando de emote é string do executável, e não existe nem no
nosso kRO nem no `Ragexe` empacotado do bRO. A aposta pelo sentido acertou pela
segunda vez, depois do `/fome` do Edgard, e isso consolida o método: **conferir o
número no `emotionlist.lub` e deduzir o nome PT pelo significado.**

O que o teste **não** cobriu, e fica dito sem virar pendência: a compra com a
bolsa **cheia** de flores. É o caso que o `delitem` antes do `getitem` foi
escrito para atender, e o único caminho do arquivo que um teste casual não
percorre.

---

## A Criança de Comodo — o primeiro link de navegação do projeto (2026-08-08)

`comodo 207,148`, sprite **944** (`4_M_DST_CHILD`, o menino da própria cidade),
virada para o sul. **Só fala.** Não vende, não troca, não teleporta e não guarda
variável nenhuma. Arquivo: `npc/guerra/crianca_de_comodo.txt`.

O que ela é: **um cartaz vivo.** A cena inteira do Corredor Fantasma — o Espectro
da Morte em `208,187`, a Alleria em `221,182`, o Saback, os dois guardas e a
Máquina em `214,185` — fica encostada na praia. Quem desembarca em Comodo **não
passa por lá** e não tem como saber que existe. Esta NPC fica na cidade e aponta
para o resto.

É a mesma função que o Saback exerce dentro da cena (a placa que manda procurar a
Alleria), um nível acima: a placa que manda até a cena.

### A coordenada mudou no mesmo dia, e melhorou por dois motivos

Ela nasceu em `190,153`, na praça, entre a Kafra e o Warper — escolha nossa, pelo
movimento. Foi movida para **`207,148`** a pedido, ainda em 2026-08-08, e o ponto
novo é melhor por duas razões que só apareceram ao conferir os vizinhos:

**1. Ela ficou na linha do Espectro.** De `207,148` para `208,187` é **uma**
célula em x e 39 em y — quase reto ao norte. Quem clica no "Fica aqui" só precisa
subir, e o caminho traçado no minimapa vira uma reta em vez de uma diagonal
atravessando a cidade.

**2. Ela caiu no canto de aposta de Comodo**, o que casa com a fala do Cassino
sem ter sido combinado. O rAthena já põe ali o par de
`npc/other/comodo_gambling.txt`: a **Devellin** de `204,148` — três células a
oeste —, que fala da obsessão da Kachua por diamante, e a própria **Kachua** de
`219,158`, que troca Diamante de 3 Quilates por item aleatório. É o que a cidade
tem de cassino hoje, e está em inglês.

A célula nova passou pela mesma conferência da antiga: tipo 0, andável, altura
0.01, com as vizinhas também tipo 0, e sem NPC nenhum em cima — os mais próximos
são a Devellin (`204,148`) e o Bulletin Board (`210,148`), três de cada lado.

> **O `plano_e_livre` do `gat.py` reprova esse ponto, e isso não é problema.** O
> terreno ali ondula de -0.36 a 0.78 nas células em volta, e aquela função é
> trava da frente **visual**, para plantar modelo 3D nivelado. NPC fica no chão e
> não se importa. Ler a reprovação como "célula ruim" seria diagnóstico falso.

### O link de navegação — e por que ele não é assunto do servidor

A marcação **"Fica aqui"** da segunda caixa é clicável e traça o caminho até o
Espectro no minimapa. A sintaxe é uma etiqueta HTML dentro do próprio `mes`:

```
<NAVI>Texto<INFO>mapa,x,y,tipo,ícone,flag</INFO></NAVI>
```

**Quem lê a etiqueta é o CLIENTE, não o servidor** (`doc/script_commands.txt`,
seção "Navigation", a partir do cliente 2011-10-10a). Isso tem uma consequência
prática que vale mais que a sintaxe: **nada no log do map-server vai dizer se
funcionou.** Link quebrado sai como texto cru na tela do jogador, e de mais lugar
nenhum.

Os três números do fim, e por que estão assim:

| campo | valor | por quê |
|---|---|---|
| tipo | `0` | ir a uma **posição**. É o único valor que aparece nos scripts do rAthena |
| ícone | `000` | sem ícone. O outro valor comum é `101`, que é sprite de NPC genérico (`JT_4W_F_01` no `npcidentity.lub` deste cliente) |
| flag | `0` | **não** abrir a janela de Navegação. O caminho é marcado no minimapa do mesmo jeito |

**Não dá para pedir o sprite do Espectro no campo do ícone:** o `4_M_DEATH` é
**10028** neste cliente, cinco dígitos num campo de três. O campo aceita o ícone
genérico ou nenhum.

O azul é nosso, não do cliente — o link não muda de cor sozinho, então vai um
`^4D4DFF` na mão, como fazem os scripts oficiais do rAthena. O texto do link é
ASCII puro de propósito: o `doc/script_commands.txt` avisa que código de cor
colado em letra acentuada embaralha.

### O que foi conferido antes de escrever o link

**A navegação depende de dado do CLIENTE**, e é uma tabela a mais que ninguém
lembra de olhar: `data\luafiles514\lua files\navigation\`. O `comodo` está no
`navi_map` com o tamanho **360×380** — o mesmo do `.gat`, o que fecha a
conferência dos dois lados.

> **Mapa fora daquela tabela não tem rota, e a falha é calada.** Fica dito para o
> dia em que alguém apontar um link para mapa nosso: o `vis_h01` do Corredor
> Fantasma, por exemplo, **não** está lá.

### O balão de MVP — `specialeffect`, não `emotion`

Ela solta o balão de MVP — o mesmo que sobe quando um chefe morre — de 4 em 4
segundos, sozinha. O par é o mesmo da Alleria e do Edgard: `initnpctimer` no
`OnInit`, e um `OnTimer4000` que dispara e rearma. O intervalo é o **nome do
label**, não um argumento.

**O que muda em relação ao emote da Alleria é o comando.** Aquilo é `emotion`
(balão de conversa); isto é `specialeffect` (efeito de tela). São dois caminhos
diferentes no cliente, e a confusão entre os dois é o que faz alguém procurar o
balão de MVP na lista de emotes, onde ele não está.

**O número é `EF_MVP` = 68, e foi contado, não chutado:** o enum `e_effect_type`
começa em `EF_NONE = -1` e `EF_HIT1 = 0` (`src/map/script.hpp:765`), não tem
nenhum valor explícito até o `EF_MVP` da linha 834 — 68 posições depois. Bate com
`doc/effect_list.md`, que o descreve como **"MVP Banner"**.

> **Não é o `clif_mvp_effect` do servidor**, e essa foi a primeira pista falsa.
> Aquele (`src/map/clif.cpp:8579`, pacote `ZC_MVP` `0x010c`) só aceita
> `map_session_data` — é **pacote de jogador**, e não há comando de script que o
> exponha. NPC não dispara aquele; dispara este. O próprio rAthena usa `EF_MVP`
> em NPC assim mesmo, em `npc/events/gdevent_aru.txt`.

`specialeffect` sem argumento de alvo sai do próprio NPC e vai para a área —
`map_id2bl(st->oid)` e `AREA` por padrão, exatamente como o `emotion`.

### As conferências de sempre

A célula foi lida no `comodo.gat` **deste** cliente — a antiga e a nova, cada uma
antes de ser usada. O detalhe da `207,148` está na seção da mudança, acima.

O sprite passou pelas duas conferências de sempre, **feitas mesmo com o número
vindo pronto no pedido**: `JT_4_M_DST_CHILD = 944` no `npcidentity.lub` deste
cliente, e `4_m_dst_child.spr`/`.act` em `data\sprite\npc\` do `data.grf`. O 944
bate com o `npc.hpp` do rAthena, ancorado no 966 do `4_M_RUSKNIGHT` e no 612 do
`4_F_PINKWOMAN`, que já estão em jogo.

O nome tem cedilha e til, e isso já tem precedente no projeto — "Máquina",
"Emissário da Ordem", "Funcionária Kafra" e "Área de Treinamento" desenham
normalmente com o patch `AlwaysAscii`.

### A fala anuncia um Cassino que ainda não existe

A segunda caixa termina em "O Cassino também tá funcionando, com Moeda Nova!".
Fica registrado que em 2026-08-08 **não há cassino nenhum no servidor** — nem
NPC, nem script, nem linha no `scripts_guerra.conf`. A busca por "cassino" no
projeto inteiro só acha essa frase.

**É adiantamento deliberado, não erro.** O dono do projeto confirmou no mesmo dia
que o cassino vem nos próximos dias, e foi por isso que a coordenada da Criança
mudou para o canto de aposta da cidade. Quem for construí-lo tem no
`PENDENCIAS.md` §1e o que já existe ali do rAthena, para não plantar em cima.

A Moeda Nova citada essa existe, e tem duas fontes — o Logue e Ganhe e a Alleria.

### Estado

Escrita, registrada no `scripts_guerra.conf` e conferida offline. **Nunca subiu
em jogo** — está no `PENDENCIAS.md` §1, e as duas estreias (o link de navegação e
o balão de MVP) têm roteiro próprio no §1e.

### 2026-08-13 — sprite novo, e a promessa do Cassino fechada

Quatro mudanças pedidas de uma vez, todas no mesmo arquivo.

**O sprite passou de 944 (`4_M_DST_CHILD`) para 962 (`4_M_RUSCHILD`)**, o menino
de Rachel. O pedido veio com o nome do sprite e a ressalva de que ele já tinha
sido conferido; as duas conferências de sempre foram refeitas assim mesmo, e
custaram uma rodada cada:

- `npcidentity.lub` **deste cliente** (extraído do `data.grf`, desmontado com o
  `luadis.py`): `JT_4_M_RUSCHILD = 962`.
- `data.grf`: `data\sprite\npc\4_m_ruschild.spr` e `.act` estão na tabela. O
  `.act` vem com o bit de DES, o que **não** é ausência — o que prova presença é
  o nome estar na tabela (`CLAUDE.md` §5).
- `src/map/npc.hpp` bate: o `JT_4_M_RUSCHILD` cai 18 posições depois do
  `JT_4_M_DST_CHILD` (944) e 4 antes do `JT_4_M_RUSKNIGHT` (966), que já está em
  jogo. 944 + 18 = 962.

Perdeu-se com a troca o argumento que justificava o 944 — "é o sprite da própria
cidade, e é o que faz ela parecer moradora e não NPC plantada". Ganhou-se uma
criança que não se confunde com as outras da praia. A decisão foi do dono.

**A fala mudou nas duas caixas.** "24!!" virou "24/7!!", que é como se diz; e
"Quando eu pegar level" virou "Quando eu for mais velho", que é o que uma criança
diria — a fala de criança é de propósito, e o troco não mexeu nisso.

**O link do Corredor ganhou a palavra que faltava.** Era "Fica aqui"; passou a
"Fica aqui o Corredor". Sem ela a segunda caixa tinha dois "Fica aqui" e nada
dizia qual levava aonde.

**E entrou o SEGUNDO link de navegação do projeto**, o do Cassino — que é o que
fecha a promessa de 2026-08-08 registrada logo acima. A frase passou a "O Cassino
Casa Rosa também tá funcionando com Moeda Nova! Fica aqui!", com o nome do
cassino que nasceu em 2026-08-12 e a marcação clicável.

O alvo é `comodo 154,98`, e o **por quê** é o que interessa a quem for repetir: o
Cassino mora no `cmd_in02`, mapa de interior, e o que o jogador precisa achar é a
**porta**. O `154,98` é a célula ao lado do warp `cmd_casino2-1`
(`comodo 153,97` → `cmd_in02 212,97`, `npc/warps/cities/comodo.txt`), a porta
leste — a que cai no salão de chegada, o primeiro andar. Célula conferida no
`comodo.gat` deste cliente: tipo 0, andável, altura 7,19.

**Apontar o link para dentro do `cmd_in02` seria o erro barato de cometer**: o
`<NAVI>` depende da tabela `navi_map` do cliente, e mapa fora dela não tem rota —
com falha calada. O `comodo` está lá; interior de cidade é outra conversa, e não
precisou ser respondida porque a porta resolve.

O arquivo é cp1252/LF: a edição foi por script, com âncora única e `assert`, como
manda o `CLAUDE.md` §5. Conferido depois de gravar — nenhum U+FFFD, LF
preservado, acentos íntegros, e toda linha de cabeçalho ainda começando com `//`.

**Falta ver em jogo**, inclusive o sprite: criança se enterra no chão com
facilidade (a armadilha do `.act`), e o 962 nunca foi usado neste servidor.

---

## A rodada de 2026-08-08 — dez pedidos numa tacada

Dez itens pedidos de uma vez, e não uma frente só: mudança de praça, regra de
PvP, tradução, item novo, NPC novo, Alberta, e três mexidas de loja. O que os
une é serem todos pequenos — e o que os separa é que dois deles cobraram um
preço que não estava no pedido. Esses dois têm seção própria mais abaixo.

### A praça: Arena, Área de Treinamento e Placar

A **Arena de Combate** e a **Área de Treinamento** trocaram de célula: a arena
foi de `prontera 157,187` para `154,187`, e o campo de treino o contrário. O
**Placar da Arena** saiu de `163,187` — a outra ponta da fileira — para
`152,187`. A fileira agora se lê, de oeste para leste: placa, arena, treino,
Mestre de UP.

**A troca arrastou junto o `disablenpc` de cada arquivo, e isso é o que tinha
como dar errado.** Cada um dos dois NPCs nossos existe porque desliga *de fora*
um NPC do rAthena que ocupava aquela célula: a arena desligava a
`Smile Assistance#prt` (157,187), o treino desligava o `GuideProntera`
(154,187). Trocar só a coordenada deixaria cada arquivo desligando o NPC da
célula do outro — dois NPCs empilhados numa, nenhum na outra, **sem erro
nenhum no log**. Então o alvo do `disablenpc` trocou junto: cada arquivo passa
a desligar o NPC que ocupa a célula que *ele* passou a ocupar.

O sprite e o `cutin "prt_soldier"` ficaram com a Área de Treinamento. São dela,
não da célula — só o lugar mudou.

### O modal do Placar da Arena, refeito

O texto do placar era uma lista de 20 e uma linha de saldo. Virou:

- **TOP 5 fixo**, sempre com cinco linhas — quando falta gente, a linha sai
  `vago`. Pódio com buraco diz "cabe mais um" melhor que uma lista curta;
- **as três regras por extenso**, com os números vindos do `OnInit` e não do
  texto, para mexer em `.Limite` consertar a regra e a explicação de uma vez;
- **um menu**: `Ranking completo` (até 15, só pontuação positiva) ou
  `Minha pontuação`, que é o caminho antigo para o modal de reputação.

**E uma regra de jogo mudou junto:** o piso saiu de `-10` para **0**. Só vale
matar quem tem pontuação zero ou positiva. Antes a faixa negativa ainda
pontuava, o que fazia de quem estava perdendo um alvo melhor que os outros.

O teste também mudou de `<=` para `<`. Não é detalhe: `.Piso` deixou de ser "o
primeiro valor que já não vale" e passou a ser "o menor que ainda vale". Trocar
um sem o outro erra por um, e o erro não se denuncia.

**Uma linha foi acrescentada ao texto pedido.** O pedido dizia "Pontuação só
ocorre se o morto tiver pontuação 0 ou maior e for nível máximo" — e o script
também exige nível máximo **do matador**, regra que já existia e que não foi
pedida para sair. Ela ficou, e o modal ganhou um `(O matador também precisa ser
nível 200.)` em cinza, para o jogador não ficar sem explicação quando a morte
não pontuar.

### O Mestre das Montarias

O `Riding Creature Master` de `prontera 130,213` — o NPC que dá Dragão a
Cavaleiro Rúnico e Grifo a Guardião Real — ganhou nome e diálogo em português,
em `npc/guerra/mestre_das_montarias.txt`. Receita de sempre: `disablenpc` no
original mais cópia nossa na mesma célula, com o
`npc/re/merchants/renters.txt` byte a byte igual ao upstream.

**Só Prontera mudou de idioma, e isso é consequência do pedido.** O de Prontera
é o *original* de que saem cinco duplicatas — Geffen, Payon, Al De Baran, Juno
e Rachel —, e desligar o original não desliga duplicata que já nasceu. As cinco
continuam em inglês.

**O nome é invenção nossa, e fica dito.** O `navi_npc_br.lub` da instalação do
bRO desta máquina **não tem este NPC** — conferido nas 5815 strings da tabela.
"Mestre das Montarias" foi escolhido aqui. Já `Cavaleiro Rúnico` e
`Guardião Real` vieram da tabela: são os nomes 625 e 631 de
`conf/msg_conf/map_msg_por.conf`.

### A Caveira Humana (30995)

Item novo dos dois lados: `db/guerra/item_db.yml` e a entrada do `itemInfo.lua`
pelo `instala_item.py`, com a arte copiada da Caveira comum (7420), que tem os
4 arquivos completos neste cliente. Peso 0 e travada como pedido — sem chão,
troca, armazém, RoDEX, leilão, carrinho ou revenda.

Ela já era citada de fora antes de existir: a descrição da Moeda Nova (30998)
lista "em troca de Caveira Humana" como fonte de moeda desde 2026-08-07.

#### Ela ganhou fonte no mesmo dia

Pedida horas depois da criação do item: cair de jogador morto na Arena de
Prontera, direto no inventário, só de quem tem Honra de Combate **maior que
zero** e nível máximo. Foi escrita no `OnPCKillEvent` do
`npc/guerra/honra_de_combate.txt`, que já lia as duas coisas — ele anexa no
morto para colher nível, nome e `#RepPointsPvP` antes de pontuar.

**"Maior que zero" não é o mesmo `.Piso` da pontuação.** Pontuar exige zero ou
mais; o troféu exige um ou mais. É uma diferença de um, e por isso os dois
números ficaram separados no `OnInit` (`.Piso` e `.TrofeuPiso`) em vez de um só
— quem ler o script tem de ver que a diferença é deliberada.

**A terceira condição não foi pedida: o troféu só sai quando a morte pontua**,
ou seja, passa também pelo anti-conluio do `.Limite`. O motivo é que a Caveira
é **moeda** — a descrição da Moeda Nova já promete trocá-la —, e sem essa trava
duas contas em nível máximo revezando mortes fabricariam moeda sem teto. O
`.Limite` já existia para o placar e saiu de graça aqui. Mover o bloco para
antes do `query_sql` do `.Limite` desfaz a decisão em uma linha.

**"Nunca no chão" não depende do script.** O `getitem`, com a mochila cheia,
tenta `map_addflooritem` — mas passa antes por `pc_candrop`
(`src/map/script.cpp`), que recusa item `NoDrop`. Como a caveira já era
`NoDrop`, mochila cheia **perde** a caveira em vez de largá-la no chão, e o
cliente avisa o jogador. Não havia o que escrever.

O texto da placa ganhou uma linha explicando o troféu, com o número vindo do
`.TrofeuPiso` — regra e explicação mudam juntas.

**Falta ver no jogo**, com o resto da praça (§1 do `PENDENCIAS.md`): matar na
arena e ver a caveira entrar. Lembrar da armadilha da conta de teste — grupo 99
ignora `NoDrop`, então testar "não cai no chão" nela dá falso negativo.

### O Mister Peso

`prontera 99,64`. Come Passe Antigravitacional (7776) e devolve peso: cada
passe sobe um nível de `ALL_INCCARRY`, que vale `2000 * skill` em
`src/map/status.cpp:3687` — ou **+200** no número que o jogador lê, já que a
tela divide por dez. Teto de 10, o mesmo `MaxLevel` da habilidade.

**É a segunda porta para o mesmo lugar.** O rAthena já tem o
`Ripped Cabus#GymPass` em `payon 173,141`, e ele está **ligado**
(`npc/scripts_athena.conf:183`). Os dois mexem na mesma variável de personagem
(`gympassmemory`) e na mesma habilidade, então ninguém soma vinte níveis indo
aos dois. Foi pedido acrescentar, não trocar de lugar — e por isso o de Payon
ficou.

O menu tem uma segunda opção, herdada do NPC oficial: repor a habilidade no
nível que a variável diz, sem cobrar passe. A variável é a verdade; a
habilidade é a cópia dela.

### As três mexidas de loja

- **Capeiro** (capa de verdade, `Garment`): entraram 480045 Manto do Guardião
  Morto, 480064 Abafador de Tempestades, 480075 Avental de Porquinho [1] e
  480114 Mikoshi Sagrado [1]. Passou de 11 para 15.
- **Camareiro** (`Costume_Head_Low`): entrou 420029 Glória Imperial. 117 itens.
- **Manteleiro**: loja nova — ver a seção própria abaixo.

**A lista pedida para o Capeiro trazia uma quinta capa, a Capa de Magma [1]
(480077) — e ela já estava lá** desde a rodada de 2026-08-01. Não entrou de
novo. Conferir antes de acrescentar é o que impede a mesma peça aparecer duas
vezes na vitrine.

Todas passaram no `valida_visual.py` com 4 de 4 (ou 8 de 8, na Glória Imperial)
**antes** de entrar, como manda o `CLAUDE.md` §4.4.

---

## O Manteleiro, e a ferramenta que faltava para o manto (2026-08-08)

O pedido era "adicionar NPC de Visuais: Capa" com treze mantos cosméticos. O
`PENDENCIAS.md` §4 dizia, desde 2026-08-05, que isso **não dava** — manto tinha
uma camada sem ferramenta nossa.

Estava certo pela metade, e a metade que faltava era menor do que parecia.

### O diagnóstico: eram duas lacunas, não uma

O §4 tratava como uma coisa só o que eram duas:

| lacuna | o que é | vale para os treze? |
|---|---|---|
| a tabela `spriterobeid.lub` | traduz o `View` do `item_db` no nome da pasta de arte. A nossa tem 120 entradas | **não** — os `View` dos treze vão de 61 a 114 |
| a arte de manto **por classe** | um `.spr` e um `.act` para cada classe de personagem e cada sexo | **sim, para cinco deles** |

A primeira é a cara, e é a que continua aberta. A segunda é mecânica.

**O que o `varre_cosmeticos.py` já respondia e o que não.** Ele classificou os
treze como `ok`, o que significa: entrada no `itemInfo.lua`, os 4 arquivos de
item, e o `View` dentro da nossa `spriterobeid.lub`. O que ele **não** olha é a
arte de manto — o próprio `PENDENCIAS.md` §4 dizia isso, na linha "estender o
`valida_visual.Cliente.caminhos` para conhecer a sprite de manto por classe".

Ou seja: `ok` ali não era promessa de que o manto desenha. E de fato **cinco
dos treze não tinham arte nenhuma neste cliente** — 480055 (Rudra), 480096
(Casaco Aconchegante), 480117 (Guitarra), 480118 (Espada do General) e 480121
(Asas Orientais), mais pedaços de outros três.

**Isso importa por causa de onde a falha aparece.** Item sem os 4 arquivos de
*item* estoura caixa modal **ao abrir a loja**. Manto sem a arte de *manto*
abre a loja, vende, equipa — e só então falha. É a falha mais cara das duas,
porque chega depois do dinheiro do jogador.

### A ferramenta: `ferramentas/instala_manto.py`

Irmão do `instala_visual.py`, para essa camada. Copia da GRF do bRO para
`cliente\data\` a subárvore de sprite de manto de um item, só o que falta.

A diferença que obrigou script separado é a **forma** da arte: chapéu são 8
arquivos de nomes fixos; manto é uma pasta inteira, com um par de arquivos por
classe de personagem — entre 250 e 700 por item. Por isso aqui não há lista
canônica de caminhos como o `vv.Cliente.caminhos`: o alvo é a subárvore, e o
que vai para o disco é a diferença entre as duas pontas.

**Ele recusa o que não tem como curar.** Manto cujo `View` esteja fora das 120
entradas da nossa tabela é rejeitado com o motivo por extenso, em vez de copiar
600 arquivos que o cliente nunca vai procurar. É a mesma disciplina do
`varre_cosmeticos.py`, e existe pela mesma razão: prometer cura que não há como
cumprir é o erro simétrico de chamar de "sem cura" o que só precisava de outra
ferramenta.

**Duas armadilhas que ele resolve, e que dariam número plausível e errado:**

1. **O prefixo tem de ser exato, com a barra no fim.** `Wing_Of_Angel_Move` é
   prefixo de `_RD`, `_BK` e `_GD`. Casar por substring mistura quatro mantos
   num só — a primeira medição deu 1235 arquivos para um item que tem 256.
2. **Manto sem `View` não é manto quebrado.** A Aura Nevada (480097) não tem
   `View` nenhum: ela é um `hateffect` (`HAT_EF_SNOW_POWDER`) no `Script` do
   item — efeito de tela, não desenho vestido. Procurar a arte que "falta" nela
   é perder tempo, e o script diz isso em vez de contar zero e parecer falha.

Aplicado em 2026-08-08: **2925 arquivos** copiados, e a segunda passada relata
"já completo" nos doze que vestem.

### A loja

`prontera 163,155`, quarta coluna da fileira de visual, sprite `1_M_MERCHANT` —
que continua a alternância homem/mulher que atravessa os dois arquivos do
quarteirão e que o Camareiro tinha deixado em aberto. Placa `Visuais: capa`.

**O nome é invenção nossa, e fica dito.** Costumeiro, Adereceiro e Camareiro
são cargos de guarda-roupa de teatro de verdade; para manto não há um, então
"Manteleiro" foi montado no mesmo molde (`-eiro`) para a fileira não destoar.

**Cliente novo perde os 2925 arquivos.** A receita para repor está no cabeçalho
da loja e no `CATALOGO-VISUAIS.md`, que agora traz, por item, se a arte veio do
nosso GRF ou do bRO.

---

## Alberta, e por que o Warper virou cópia nossa (2026-08-08)

O pedido era pequeno: mover a chegada do warp em Alberta de `28,234` para
`117,57`, e o NPC de `28,240` para `105,63`. O par ficava na quina noroeste,
longe de tudo — quem se teletransportava para a cidade caía num canto isolado.

O preço foi forkar o `npc/custom/warper.txt`.

### Por que não deu para fazer de fora

As duas metades do pedido não são iguais:

| o quê | dá de fora? |
|---|---|
| a **posição do NPC** (`28,240`) | **sim** — `movenpc "Warper#alb",105,63;` |
| a **chegada** (`28,234`) | **não** |

A chegada é um `Go("alberta",28,234)` **dentro** do corpo do script, num rótulo
(`T2:`). Não há comando de script que alcance o corpo de outro NPC. E o
`CLAUDE.md` §2 fecha a outra saída: editar o arquivo do rAthena é alteração em
código de terceiros.

Sobrou o caminho que o próprio `scripts_guerra.conf` já registrava por escrito,
desde que o warper foi ligado — *"se um dia quisermos versão própria, o caminho
é copiar para `npc/guerra/` e comentar esta linha, não editar o arquivo do
rAthena"*. Este foi esse dia.

`npc/guerra/teletransportadora.txt` é cópia byte a byte com **três linhas**
diferentes, todas de Alberta: o `Go` do rótulo `T2`, o `naviregisterwarp`
correspondente (que tem de bater com ele, senão o minimapa aponta para o lugar
antigo) e a coordenada da duplicata `Warper#alb`. As três estão listadas uma a
uma no cabeçalho do arquivo — é isso que mantém barato trazer correção futura
do rAthena.

A linha do arquivo do rAthena ficou **comentada** no `scripts_guerra.conf`. Os
dois não podem subir juntos: os nomes de NPC batem e o segundo a ser lido não
nasce.

### O que veio de graça, e o que continua caro

**De graça:** o `PENDENCIAS.md` §1d pedia "cópia nossa em `npc/guerra/`" como
pré-requisito para podar do menu os mapas que este cliente não tem — o `1@slug`
que derruba o cliente e prende o personagem. A cópia existe agora. A poda
**não** foi feita, e todo destino de Instância continua suspeito.

**Continua caro:** a cópia não acompanha o upstream. Está registrado no §4c.

### Uma armadilha evitada de propósito

A linha da duplicata levou um comentário — mas **acima** dela, nunca no fim.
`npc_parsesrcfile` enche o último campo *"to end of line"*, e comentário de fim
de linha vira parte dele. É a armadilha do `CLAUDE.md` §5, a mesma que em
2026-08-08 fez um evento de spawn nascer, andar, morrer e nunca disparar.

O `sprite_teletransportadora.txt` continua funcionando sem alteração de código:
ele acha as 45 duplicatas **pelo nome**, e nenhum nome mudou. Só as referências
do cabeçalho dele foram reapontadas.

### Estado

Tudo acima subiu num boot limpo em 2026-08-08 — sem `Unknown syntax`, sem nome
de NPC duplicado, sem item inválido em loja. **Nada foi visto em jogo**; está no
`PENDENCIAS.md` §1.

---

## As instâncias, o teto de mapas e um personagem preso (2026-08-08)

A pergunta que abriu o dia era de capacidade: **ligar instâncias deixa o
servidor pesado?** A resposta curta é que a premissa estava invertida — **as
instâncias já estavam todas ligadas** — e que o custo delas não está onde se
esperava.

### O que já estava de pé

`npc/re/scripts_main.conf` → `npc/re/scripts_athena.conf:65-112` carrega 47
arquivos de instância (só `WaveMode.txt` comentado), mais 4 pre-RE em
`npc/scripts_athena.conf`. Nada a ativar. O que separa o jogador da instância é
o gate **dentro do script**, não a configuração.

E o gate engana: "Requisito: -" no browiki não quer dizer "sem trava", quer
dizer "sem cadeia de quest anterior". O Hugin do Old Glast Heim exige nível 130
e a quest 12316 — que ele mesmo entrega na conversa. O teste que separa um caso
do outro é **onde está o `setquest` daquele id**: se só no próprio arquivo, o
gate é auto-suficiente. Nas 15 instâncias conferidas, era.

**A exceção é o Torneio de Magia**, que mora em `npc/custom/official/` — pasta
que o `scripts_custom.conf` não carrega, porque lá só está descomentada a nossa
linha. É a única do lote que precisa mesmo ser ligada.

### O custo não é banco nem CPU — é slot de mapa

A conta está no `ARQUITETURA.md` §7 e não se repete aqui. O resumo: banco é
**zero** (`instance.cpp` não tem uma chamada SQL), memória é desprezível
(mediana de 0,20 MB por rodada), CPU é neutra. O único limite real é
`MAX_MAP_PER_SERVER = 1500` contra 1258 mapas já carregados — e ele só aperta
perto de mil jogadores simultâneos em party.

**Decidido em 2026-08-08: não mexer em nada disso agora.** A análise foi
escrita para o dia em que a população crescer, não para ser executada.

### O acidente, e os quatro mapas que saíram do ar

Ao testar, um personagem foi levado a `1@jorlab` e ficou **preso**: o mapa não
existe no GRF deste cliente, o cliente caía ao entrar e caía de novo ao
reconectar. É exatamente a regra 6 do `CLAUDE.md`, e o segundo caso registrado
depois do `1@slug` (`PENDENCIAS.md` §1d).

Saiu de lá pelo banco, com o personagem offline — a receita já estava escrita no
§1d e funcionou sem alteração. **O `save_map` também precisa ser conferido**, ou
o personagem volta ao mapa quebrado ao morrer; neste caso estava em Prontera.

Aproveitando, os 109 mapas do `db/re/instance_db.yml` foram cruzados com o
`data.grf`: **73 das 78 instâncias têm todos os mapas**. As 5 restantes dependem
de `1@iwp`, `1@jorchs`, `1@jorlab` e `1@whl`, que faltam de verdade — nenhum
deles está apelidado no `resnametable.txt` do cliente, que existe e tem 2155
linhas. Os quatro foram comentados no `conf/maps_athena.conf`, com o mesmo
tratamento e o mesmo motivo dos `tra_fild`.

**Desligar não tirou conteúdo:** as cinco instâncias que usam esses mapas não
têm script nenhum, são registros órfãos do `db/`. Não havia porta de entrada
para o jogador — só para o `@warp` de quem administra, que foi justamente o que
aconteceu.

### Estado

A mudança no `conf/maps_athena.conf` **só vale no próximo boot do map-server** —
a lista de mapas é lida na inicialização. Até lá os quatro continuam
alcançáveis por `@warp`.

A meta seguinte era a **Ordem dos Exploradores**, que **não existe no rAthena**
e teve de ser escrita do zero — feita ainda em 2026-08-08, na seção "A Ordem
dos Exploradores" mais abaixo. As 16 instâncias que ela usa, e o que ficou de
fora, estão no `PENDENCIAS.md` §1f.

**A Vila dos Porings foi entrada e jogada no mesmo dia, e funcionou** — a
primeira instância validada do projeto. As outras 15 continuam por ver.

---

## Os nomes das instâncias em português (2026-08-08)

Logo depois de validar a Vila dos Porings veio a pergunta óbvia: **está tudo em
inglês, dá para traduzir?** Dá — e o nome da instância é um caso separado do
diálogo, muito mais barato e muito mais visível.

### É a exceção à regra que rege todo o resto

O projeto inteiro gira em torno de "o servidor manda ID, o cliente decide o que
desenhar". **O nome da instância é o contrário:** o `clif_instance_create`
(`clif.cpp:18794`) empacota o `Name:` do db no pacote `0x2cb`, e é esse o
título que o jogador lê na janela. Nada de `itemInfo.lua`, nada de fechar o
cliente — é mudança de servidor só.

### O que fez o trabalho ser cuidadoso: o nome é chave

`instance_create("<nome>")`, `instance_enter("<nome>")` e
`instance_live_info(ILI_NAME,...)` resolvem **por string**. Trocar o `Name:` no
db sem trocar o literal no script faz a instância deixar de abrir — e o db e o
script são arquivos diferentes, então nada acusa até alguém tentar entrar.

O levantamento achou **26 literais nos 16 arquivos**. A distribuição foi uma
boa notícia: quase todo script declara `.@md_name$ = "..."` **uma vez** e usa
por variável, então a maioria era uma linha. Só o Sarah vs Fenrir tinha três.

O detalhe que decidiu a forma: o `parseBodyNode` (`instance.cpp:52`) faz
`find(id)` e **sobrescreve apenas os campos presentes no nó**. Então
`db/guerra/instance_db.yml` tem só `Id` e `Name` — repetir `Enter` e
`AdditionalMaps` seria criar uma segunda verdade sobre a mesma coisa. O arquivo
do rAthena ganhou uma linha `- Path:` no rodapé, como os outros db.

A regra e as duas armadilhas (nome repetido é descartado calado; o extrator da
tradução captura o nome como se fosse fala) estão no `ARQUITETURA.md` §4 e não
se repetem aqui.

### O menu da teletransportadora veio junto, e ali é rótulo

Os mesmos nomes aparecem no menu de Instâncias da `teletransportadora.txt`, mas
**ali não são chave**: ela nunca chama `instance_create`, só `Go(mapa,x,y)`.
Foram 17 rótulos traduzidos. **Três ficaram em inglês de propósito** —
`Eclage Interior`, `Endless Tower` e `Hazy Forest` — por não haver fonte no bRO
para o nome deles, e a regra é não inventar.

### Um susto que não era

A conferência de encoding acusou `GeffenMagicTournament.txt` como "parece
UTF-8". Não foi obra da tradução: são **54 bytes `\xcf\xaf`** decorativos, de
uma régua de comentário que já vinha do arquivo, e **todos os 54 estão dentro de
linha `//`**. Conferido um a um, justamente porque a §5 do `CLAUDE.md` avisa que
uma linha ruim de comentário mata o arquivo inteiro. Vale lembrar que **esse
arquivo nunca foi carregado** — é o do Torneio de Magia, que está em
`npc/custom/official/` e continua desligado.

### Estado

Aplicado em disco e conferido: 16 nomes únicos, todos dentro dos 60 bytes do
`INSTANCE_NAME_LENGTH`, os 26 literais casando com o db um a um, nenhum U+FFFD,
tudo em cp1252. **Não foi visto em jogo ainda** — aplica com
`@reloadinstancedb` + `@reloadscript`, sem derrubar o servidor.

---

## A Ordem dos Exploradores (2026-08-08)

O pedido foi curto — *"vamos ativar a Ordem dos Exploradores, existe uma
análise feita"*. A análise era o briefing da §1g do `PENDENCIAS.md`, levantado
no mesmo dia, e ele estava certo no essencial e errado em três detalhes que
teriam custado caro.

**O que a Ordem é:** três placas em um salão, cada uma com um lote de caçadas
dentro de instâncias. Matar o chefe, voltar, receber **Moeda do Explorador**
(25737) e EXP. A moeda se gasta ali mesmo, numa Máquina de Troca, a 10 por 1
**Moeda Nova** — a moeda-corrente que as Máquinas de Prontera e Comodo já
cobram. É conteúdo exclusivo do bRO: o rAthena não tem nada disto.

### O que decidiu a arquitetura, e já estava no briefing

**`OnNPCKillEvent` nunca dispara para chefe de instância.** Em `mob.cpp:3592`
os dois caminhos são ramos de um `else if`: se o mob tem evento próprio, o
global não roda — e **todo** chefe de instância nasce com
`instance_npcname(...)+"::OnMyMobDead"`. Um contador de caçada feito assim
compila, sobe, não erra no log e conta zero.

Quem conta é o objetivo `HUNTING` de quest, que roda antes e fora daquele
`if` (`mob.cpp:3575`) e ainda propaga para a party dentro de `AREA_SIZE`.
A consequência boa é que a Ordem coube inteira em `npc/guerra/` mais um
`db/guerra/`, **sem tocar em nenhum dos 16 arquivos de instância** — a lei da
§2 do `CLAUDE.md` ficou intacta.

Isso já estava levantado. O que esta sessão acrescentou foi o resto.

### Três correções ao briefing, todas achadas lendo o script

O briefing tirou os Ids de mob do browiki cruzado com o `mob_db`, e marcou com
`?` os que não casaram. O jeito de fechar era abrir o script de cada instância
e ver qual mob morre no fim. Três estavam errados:

| Instância | O briefing dizia | O script diz |
|---|---|---|
| Fábrica do Terror | "Antonio **não spawna**; o chefe é a Celine Kimi (2996)" | `XM_ANTONIO` **2988**, em `HorrorToyFactory.txt:939`. Spawna. |
| Covil de Vermes | Faceworm Queen, 2529 ou 2532 | `FACEWORM_DARK` **2530** — e a quantidade é que confirma: o alvo do bRO é "4x Verme Sombrio com Rosto", e ele nasce **exatamente 4 vezes** |
| Vila dos Porings | "spawn por variável — não resolvido" | `MD_GOLDRING` **3811**. O spawn usa a *string* `"MD_GOLDRING"`, e por isso um grep por número não achava |

E um caso que só o código resolvia: o **Palácio das Mágoas** tem **dois**
"Torturous Redeemer", 2959 e 2961, com o mesmo nome na tela. O alvo é o
**2959**. O 2961 nasce numa cena e leva `killmonster` cinco segundos depois
(`GhostPalace.txt:758`) — morte por `killmonster` não passa pelo
`quest_update_objective`, então mirar nele daria uma missão **impossível, sem
nada no log**.

Os 17 AegisNames foram conferidos por script contra o `mob_db` antes de
escrever a primeira quest. Não é zelo: AegisName errado emite *"Mob %s does not
exist, skipping"* e **descarta a quest inteira** (`quest.cpp:132`), não a linha
do alvo.

### Duas missões não tinham alvo, e ficaram reservadas

- **Torneio de Magia.** O "Muliphen" do bRO **não existe como monstro em lugar
  nenhum** — o Torneio é duelo de NPC. E a instância nem está carregada.
- **Sonho Sombrio.** O "Réquiem de Marfim" também não casa com nada: o arquivo
  inteiro tem **seis** monstros (Ferre 3069-3072 e Jitterbug1/2 3108/3109), e
  nenhum é chefe único.

As duas foram cortadas a pedido, com a instrução de deixar a adição fácil
depois. Ficaram **comentadas lado a lado** no `quest_db.yml` e na tabela do
`OnInit` das placas, cada uma com o candidato anotado. Sobraram **14 missões**:
7 do grupo A, 3 do B, 4 do C.

### O lugar mudou, e o dono é que sabia

O briefing tinha conferido o `.gat` de Alberta e escolhido a alcova de
`116,71` — o pátio murado de 24 células atrás do prédio de portas azuis — com
as placas na fileira do fundo e a Máquina em `115,72`. Estava bem medido, e
estava errado: **no bRO aquelas coordenadas são um portal**, e a Ordem fica
*dentro* do prédio. O dono apontou isso com um screenshot do próprio cliente.

O primeiro caminho investigado foi `alberta_in` — varrendo as 18 regiões
andáveis do mapa e cruzando com os 76 NPCs que o rAthena planta lá, sobrava
uma sala vazia (`x60-77, y170-189`). Serviria. Mas o dono achou o lugar de
verdade: **`auction_02`**, a metade que era o Salão do Leilão de Lighthalzen,
cujo portal de saída (`43,17`) no bRO volta para Alberta — e aqui ia para
Lighthalzen, que é o padrão do rAthena.

Duas coisas tornaram isso barato:

1. **O mapa já está no nosso GRF** — `auction_02.rsw`, `.gnd` e `.gat`,
   conferidos. Sem mapa novo, sem o risco da §4.6.
2. **O leilão está desligado** (`feature.auction: off`). Os quatro salões são
   espaço morto e os Auction Broker não fazem nada. Reaproveitar um não tira
   função de ninguém.

A metade de Yuno do mesmo mapa não foi tocada: é uma região andável separada,
então o portal de Yuno continua como era.

**Cinco NPCs do rAthena foram desligados**, todos por `disablenpc` e sem
editar arquivo de terceiros: o warp `43,17 -> lighthalzen`, a porta do leilão
em Lighthalzen com a placa ao lado, e os três Auction Broker de dentro do
salão. Comentar a linha do `scripts_guerra.conf` devolve os cinco.

Empilhar o nosso warp na **mesma célula** do desligado funciona, e o código diz
por quê: `npc_touch_areanpc` devolve cedo quando o NPC está `is_invisible`
(`npc.cpp:1900`), e o laço de cima continua procurando (`npc.cpp:1978`).

### Um erro de codificação, e o que ele ensina

A primeira tentativa de pôr a moeda no `db/guerra/item_db.yml` foi com a
ferramenta de edição comum. Ela leu o arquivo cp1252 como UTF-8, não conseguiu
decodificar os 9 bytes acentuados, e regravou tudo em UTF-8 — **os 9 acentos
viraram U+FFFD**, o dano irreversível que o `CLAUDE.md` §5 descreve. O arquivo
foi restaurado do git e a inserção refeita por script, no nível de bytes, com
três asserções: mesmo número de bytes não-ASCII antes e depois, nenhum U+FFFD,
e o resultado tem de continuar decodificando em cp1252.

A regra já estava escrita (§4.1: *"escrever é o passo perigoso, não ler"*). O
que faltava era a consequência prática: **para qualquer arquivo que o jogo lê e
que já tenha acento, a edição é por script, não pela ferramenta de edição.**
Foi assim que o `ordem_dos_exploradores.txt` nasceu — 73 bytes acentuados,
gravados de uma vez, com a conferência do cabeçalho embutida no gerador.

### O que ficou no ar

Sete peças em `auction_02`: três placas (sprite 837, `JT_2_BULLETIN_BOARD`), o
Teleportador (10007, 5.000z, 14 destinos), a Máquina de Troca (564, o mesmo
sprite das outras duas Máquinas) e os dois portais. Mais a moeda nos dois
lados, 14 quests de caçada e 3 de espera.

**A espera trava a entrega, não a retirada** — ao entregar, a placa já devolve
os pedidos do dia seguinte, como no bRO. O prazo é `TimeLimit: 6h` **sem** o
`+`: sem o sinal o campo é *hora exata*, e o `quest_time()` devolve o próximo
06:00 sozinho, sem temporizador nenhum do nosso lado.

**Os valores são os do bRO**, por decisão do dono — 5 a 25 moedas, 50k a 1M de
EXP, troca 10:1. Ao medir isso um dia, lembrar do que se descobriu aqui: o
`getexp` **não passa pela nossa taxa de 10x**. A `base_exp_rate` só é aplicada
ao EXP de **mob**, no carregamento do `mob_db` (`mob.cpp:5077`); o que mexe no
`getexp` é o `quest_exp_rate`, que está em 100. Então 800.000 na tabela é
800.000 na tela, num servidor onde o monstro rende dez vezes mais — a
recompensa de missão vale relativamente um décimo do que o número sugere.
Subiu para o `CLAUDE.md` §5.

### O que foi verificado, e o que não foi

O map-server foi reiniciado e o trecho novo do `log/map-msg_log.log` lido: **zero
`Unknown syntax`**, zero aviso de quest descartada, zero erro nos seis
`disablenpc`. Esse último é a prova positiva que importa — `disablenpc` com
nome inexistente emite `ShowError` (`script.cpp:12368`), então o silêncio prova
que o arquivo parseou, que o `OnInit` rodou e que os seis nomes estão certos.
Os únicos erros no trecho são dois pré-existentes do `item_db.yml` (chicote e
instrumento musical dos placeholders Brutais), sem relação.

**Nada disso foi tocado por um jogador.** O que falta testar em jogo está no
`PENDENCIAS.md` §1g — e o teste que prova a decisão central é uma missão
inteira na Vila dos Porings, a única instância já validada.

### A Opheliac, os dois guardas, e o que a moeda compra

Ainda em 2026-08-08, o dono apontou o que faltava: **a moeda não comprava
nada além de outra moeda.** No bRO quem resolve isso é a **Opheliac**, e o
pedido veio com a tabela do browiki e com a fala dela escrita palavra por
palavra.

Ela faz três coisas lá — troca de moedas, transformação de visuais e
encantamento do Robozinho Sabe-Tudo — e **só a primeira entrou**, por decisão
do dono. As outras duas não são só escopo: são **janela do cliente**, com
metade da configuração do lado de lá (`CLAUDE.md` §4.9), e nenhuma está
montada neste cliente. Um NPC que as abrisse não faria nada.

**Resolver 32 nomes em português para 32 IDs** foi o trabalho de verdade, e
seguiu a ponte de sempre: o `iteminfo_new.lub` do bRO. Uma armadilha no
caminho — aquele arquivo é **bytecode Lua 5.1**, não texto, então a primeira
tentativa (regex) devolveu zero itens e parecia que a tabela estava vazia.
Quem o lê é o `le_bro()` do `ferramentas/completa_iteminfo.py`, que já
existia.

O resultado do cruzamento com o nosso `item_db`:

| Situação | Quantos | O que se fez |
|---|---|---|
| completos nos dois lados | 21 | nada |
| no servidor, **sem entrada de cliente** | 8 | `completa_iteminfo.py` — sem ela o item aparece **sem nome e sem ícone** |
| sem entrada de cliente **e sem arte** | 1 | o Cartão SSD (490578); a arte veio do GRF do bRO, pelo `instala_visual.py` |
| **fora do nosso `item_db`** | 2 | criados em `db/guerra/item_db.yml` |

Os dois criados são os **Saltos da Rainha Scaraba (15368)** e o **Memorável
Anel Rústico (490174)**, nos IDs oficiais do bRO, no mesmo molde da seção de
placeholders do Mercado Contemporâneo. Os bônus próprios funcionam; os de
**conjunto** ficaram como `# TODO` — o primeiro pertence a três conjuntos e o
segundo a cinco, e implementar metade de um conjunto dá bônus fantasma.

Aqui apareceu um número que não é óbvio e que vale para qualquer item trazido
do bRO: **a conversão de peso é ×10.** O bRO escreve *"Peso: 70"* e o rAthena
grava `Weight: 700`. Foi conferido contra as Botas do Ocultista (22138), que
existem nos dois lados — bRO "Peso: 50", nosso db `Weight: 500`.

E uma desambiguação que só o número de covas resolvia: existem **duas** "Botas
do Ocultista", `Demonist_Shoes` (22138, sem cova) e `Demonist_Shoes_` (22221,
com uma). A do browiki é a **22138** — a lista de lá marca cova com "[1]", como
faz na Venda Sombria, e esta linha não tem a marca.

**Quatro itens do bRO ficaram fora da loja**, todos com razão registrada no
`PENDENCIAS.md` §1g: os três "Combinador" (são encantamento, que o pedido
excluiu) e os Chapéus Sortidos (caixa aleatória, que precisaria de um grupo
em `item_group_db` e de sete chapéus com arte).

**A Opheliac também fechou uma pergunta que estava em aberto:** quem é o rosto
da Ordem. O salão tinha três placas que se apresentavam sozinhas; agora tem
alguém que recebe o jogador na entrada, e a fala dela — do dono — é o que
amarra a Ordem à ficção do servidor destruído. Sprite **894**
(`JT_4_F_KHELLISIA`), a que mais se aproxima da foto do browiki.

Os **dois guardas** (38,28 e 49,28) usam o sprite **966** (`4_M_RUSKNIGHT`), o
mesmo dos dois Guarda da Ordem que já estavam em Comodo — de propósito: é a
mesma Ordem, e o jogador reconhece a farda. Ficam virados para dentro, e a
direção seguiu a tabela empírica do `maquina.txt` (6 desenha virado para a
direita, 4 para a esquerda), não a intuição de ponto cardeal.

Da fala da Opheliac só se mexeu no que era acento faltando ao digitar (*"ja"*
e *"a ativa"*); o *"tava"* é coloquial e ficou.

**Verificação:** o map-server subiu de novo sem um `Unknown syntax` e **sem um
único aviso de barter**. Esse silêncio é a prova positiva que importa aqui —
`barter_parseBodyNode` (`npc.cpp:572`) emite *"Unknown item %s"* e **descarta
a loja inteira** para qualquer AegisName que não resolva. Zero avisos = os 29
AegisNames das três lojas existem. O que a loja ainda não teve é um jogador
abrindo a janela e conferindo nome e ícone linha a linha.

### O primeiro teste em jogo, e o bug que ele achou (2026-08-08)

As placas subiram e o primeiro clique em "Pegar os pedidos que faltam"
**derrubou o cliente**: mais de trinta caixas de erro seguidas, uma atrás da
outra, e a conexão caiu. A mensagem era

```
GetOngoingQuestInfoByID
.../data/LuaFiles514/Lua Files/Datainfo/QuestInfo_f.lua:4:
attempt to index field '?' (a nil value)
```

O erro **não é do script** — é do cliente, e é uma armadilha que o projeto já
tinha registrada **pela metade**. O que estava escrito, e que veio do episódio
da quest 5153 em 2026-08-07, era: *"a janela de missões não lê o
`questid2display.txt`; quem desenha é o `QuestInfoList` — missão sem entrada lá
aparece sem título."*

**Não aparece sem título. Derruba.** Desmontando o `questinfo_f.lub` com o
`luadis.py`, a linha 4 é

```lua
QuestInfoList[id].Title
```

sem guarda de nil. E o detalhe que torna isso uma enxurrada: as *outras* três
funções do mesmo arquivo — `GetOngoingDescription`, `GetOngoingRewardInfo` e
`GetCoolTimeQuest` — **têm** a guarda (`if ... == nil then return end`). Só a do
título não tem. Como a janela consulta o título a cada atualização, e as
Missões A são sete de uma vez, o cliente entra num laço de caixas de erro.

A correção certa não era editar o `.lub` à mão: `OngoingQuestInfoList_True.lub`
e `_Sakray.lub` são **gerados** pelo `traduz_ptbr.py questinfo`, que os
reconstrói do coreano de 2021 congelado no `.COREANO`. Entrada posta à mão
sobrevive até a próxima rodada da tradução e some sem aviso — e o sintoma seria
o cliente voltar a cair, meses depois, por um motivo aparentemente sem relação.

Então nasceu o **`ferramentas/monta_missoes_da_ordem.py`**, irmão do
`monta_logue_e_ganhe.py` e pelo mesmo motivo: sistema de UI com metade da
configuração no cliente. Ele lê as ids do `db/guerra/quest_db.yml` — que é onde
se diz quais missões existem — e tem o texto PT dentro. Três decisões nele
valem registro:

- **Aborta se faltar texto.** Missão no YAML sem entrada na tabela `TEXTO` para
  a gravação e lista o que falta. Uma missão sem entrada no cliente é
  exatamente o bug que o script existe para impedir; deixá-la passar com aviso
  seria repetir o acidente.
- **É idempotente**: antes de inserir, retira toda entrada da faixa
  30000–30049 que já esteja no arquivo. Rodar duas vezes dá o mesmo tamanho.
- **Passa pelo `luac -p`** antes de gravar, como todo `.lub` de texto que o
  projeto gera.

A ordem de uso é a única armadilha que sobra, e está no `LEIAME.md`:
`traduz_ptbr.py questinfo` **primeiro**, este script **depois**.

O texto segue o padrão do próprio bRO, que este cliente já traz: a caçada leva
o nome da instância, e a espera vem com `[Espera]` na frente — como a quest
293444, *"[Espera] Shibasays"*, com `Summary = "Reseta 4 da manhã."`.

**A regra subiu para o `CLAUDE.md`** — §5 (a armadilha, com o código) e §4.9
(terceiro caso vivo de UI do cliente, e o único que não falha calado).

### O segundo bug: o Teleportador levava ao lugar errado nos catorze

Com a janela de missões consertada, a Ordem funcionou — e o teste seguinte
achou outra coisa. O Teleportador cobrava os 5.000z, teleportava, e entregava
no lugar errado: *"Batalha dos Orcs"* levava a `prt_fild05` (Vila dos Porings)
e *"Hospital Abandonado"* levava a `mal_dun01` (Caverna do Polvo).

A causa é banal e o registro fica pelo **formato** dela: o menu e a tabela de
destinos tinham sido escritos em **ordens diferentes**. O `.menu$` seguia a
ordem das placas (grupo A, depois B, depois C); o `.mapa$`/`.mx`/`.my` seguia a
ordem em que os mapas tinham sido validados por script. O `select` devolve a
posição no menu, e essa posição indexava a outra lista. Nenhum dos catorze
caía no lugar certo.

**O que torna isso caro é o silêncio.** Não há erro: o NPC funciona, cobra o
zeny, teleporta. Nada no log. E o cabeçalho do próprio arquivo **afirmava** que
as ordens eram a mesma — a frase estava lá, escrita com confiança, e era falsa.

Duas coisas mudaram por causa disso, e a segunda importa mais que o conserto:

1. **O menu passou a ser gerado da própria tabela.** Não existe mais uma
   segunda lista de nomes: há `.dest$[]`, e o `.menu$` sai dela num laço no
   `OnInit`. Mais um `getarraysize` comparando as quatro colunas, que denuncia
   com `debugmes` se uma tiver tamanho diferente. A classe inteira de bug
   deixou de ser possível.
2. **A conferência passou a ler o arquivo GERADO.** O script que validou os
   destinos da primeira vez conferia a lista que eu tinha na cabeça, não a que
   foi gravada — e por isso passou com "14 destinos, 0 problemas" enquanto o
   NPC estava todo trocado. O novo extrai as quatro tabelas do `.txt` e cruza
   destino a destino.

**A regra subiu para o `CLAUDE.md` §4.11:** menu de `select` e tabela indexada
pelo mesmo número saem da mesma fonte, e a trava é um laço, não um comentário.
*Comentário não é trava* — foi a lição das duas noites.

### A porta da Batalha dos Orcs, e a instância que ninguém conseguia abrir

A pergunta foi *"cadê o NPC de entrada da instância dos Orcs?"*. A resposta
curta: era a **pedra** — `Dimensional Gorge Piece`, `gef_fild10 242,202`,
sprite 406 — e não parece um NPC, que é por que ninguém a acha. Mas ler o
código dela achou uma coisa bem maior.

```
instance_check_party(.@party_id, 2, 30, 80)
```

Party com **duas** pessoas online, e **todas entre nível 30 e 80**. O teto vale
para o grupo inteiro (`script.cpp:22081` sai do laço no primeiro membro fora da
faixa), então personagem de nível alto **não entra de jeito nenhum** — nem
sozinho, nem acompanhado. A missão "Batalha dos Orcs" da Ordem era impossível.

Varrendo as catorze portas, duas barram um personagem 200:

| Instância | Porta | O que barra |
|---|---|---|
| Batalha dos Orcs | Dimensional Gorge Piece | teto de nível 80 + party de 2 |
| Vila dos Porings | Emily (`prt_fild05 145,235`) | recusa `BaseLevel > 60` |

Ironia registrada: a Vila dos Porings era justamente a que o `PENDENCIAS.md`
recomendava como *"o teste mais barato"* da Ordem.

**O rAthena tem a versão antiga da instância.** O browiki de hoje
(`Batalha_dos_Orcs`) diz *"Nv. de base: 60"*, *"Grupo: 1 pessoa ou mais"*, e a
reserva é com a **Cientista** em `gef_fild10 231,203` — outro NPC, em outra
coordenada. Foi o dono quem apontou isso, com o print da página.

O conserto seguiu a receita da §2, e o corte foi o **menor possível**: não uma
cópia do `OrcsMemory.txt` (900 linhas, com os spawns, os quatro
`#Resurrect Monsters` e o Kruger), e sim **só a porta**. O
`npc/guerra/porta_dos_orcs.txt` tem um NPC e um `disablenpc`:

- **Cientista**, `gef_fild10 231,203` (a coordenada do bRO), sprite 982
  (`4_F_SCIENCE` — mulher, como o dono lembrou), com
  `instance_check_party(.@party_id, 1, 60)`. O `max` omitido vale `MAX_LEVEL`
  (`script.cpp:22048`), então **não há teto**; o `1` continua exigindo party,
  porque `instance_check_party` devolve 0 sem party e o `instance_create` é por
  party de qualquer jeito. Party de um serve.
- `disablenpc "Dimensional Gorge Piece"` — a porta velha.

O `Mad Scientist#orc` (238,202) **não foi tocado**: não abre instância nenhuma,
e a variável `mad` dele não aparece em mais nenhum arquivo de `npc/`.

**O tempo de espera acompanhou.** A quest 12059 é do rAthena e vinha com
`TimeLimit: +2h`; o browiki diz *"Reseta meia-noite"*. Virou `0h` — **sem** o
`+`, que é a forma de hora exata — num override em `db/guerra/quest_db.yml`,
o primeiro daquele arquivo a não ser da nossa faixa. Ela não pega mais nada:
os outros dois "12059" de `npc/` são o **item** 12059.

**Fora de escopo por decisão do dono:** o Anel dos Orcs, a troca de Insígnia
por chapéu (Mulher Suspeita) e o encantamento do anel (Homem Suspeito).
Nenhum item novo, nenhum encantamento.

E de quebra, o mesmo cruzamento achou que o Teleportador largava o jogador a
**28 passos** da porta da Vila dos Porings — no NPC de encantar legumes, e não
na Emily. O destino tinha vindo do menu de Instâncias do warper do rAthena, que
aponta para *o lugar*, não para *quem abre a instância*. Corrigido, junto com o
dos Orcs, que agora aponta para a Cientista. As catorze caem a 10 passos ou
menos da porta, conferido por script contra o arquivo gerado.

### O cliente do bRO como fonte, e três missões destravadas (2026-08-09)

A pergunta foi *"você tem acesso a como eram as instâncias no bRO?"*. A resposta
acabou valendo mais que a pergunta.

O `System\OngoingQuestInfoList_True.lub` da instalação do Ragnarok Brazil —
bytecode Lua, lido pelo `luadis.py` — carrega **as 30 missões de instância da
Ordem dos Exploradores**, cada uma no formato

```
Na <NAVI>[Batalha dos Orcs]<INFO>gef_fild10,231,203,000,0</INFO></NAVI>,
elimine 1 Orc Falso.
```

Ou seja: nome da instância, **coordenada do NPC de entrada** e **alvo**, ditos
pelo próprio jogo. É melhor que o browiki para a lista — e o browiki, aliás,
devolve **403** para busca automática, então só o dono o lê.

O que o cliente **não** tem é a mecânica. Isso ficou registrado no
`ARQUITETURA.md` §6, junto com o resto do que aquela instalação responde.

**O teste que a descoberta permitiu**, e que respondeu à preocupação real do
dono (*"se as outras forem no mesmo padrão acho que vamos tirar"*): comparar a
coordenada da porta entre os dois lados. **14 das 16 batem** — o rAthena tem o
NPC de entrada na coordenada exata do bRO, a 0 ou 1 passo. Só duas divergiram,
e eram justamente as duas que já tinham dado problema. Não é padrão; é exceção.

De quebra, o texto do bRO **confirmou quatro Ids de mob** que tinham sido
deduzidos lendo script: *"4 Vermes Sombrios com Rosto"*, *"1 Antonio"*,
*"6 Gigantes Ancestrais"*, *"Origem da Maldição e Amdarais"*.

#### O Réquiem de Marfim existia o tempo todo

A missão do Sonho Sombrio estava **comentada** no `quest_db.yml` com a
justificativa de que o alvo do bRO não casava com nada — *"o arquivo inteiro da
instância tem seis monstros e nenhum é chefe único"*.

Estava errado, e o erro é instrutivo. A varredura tinha procurado o padrão
`"--ja--", <id>`, que é como **quase todo** spawn daquele arquivo é escrito. A
linha do chefe é a única que usa o nome literal:

```
monster 'map_jtb$,322,335, "Awakened Ferre", 3073,1, .@label$;   // GRAND_PERE
```

**Levantamento por grep de um padrão só não prova ausência.** O `Awakened Ferre`
(3073) é o chefe final, nasce no quarto do chefe e o script guarda o id dele em
`'boss_id`. A missão 30007 entrou, com 10 moedas e 800.000 de EXP, e as placas
passaram de 14 para **15 missões** (8 do grupo A).

#### A Vila dos Porings ganhou porta própria

A Emily recusa `BaseLevel > 60` (`PoringVillage.txt:145`), e por isso a missão
era impossível para personagem de nível alto. Aqui **não deu para copiar o
bRO**, ao contrário dos Orcs: lá a Vila dos Porings entra por
**`izlude 46,103`** — outro *mapa* —, e o rAthena tem a versão antiga.

Então a porta é nossa de verdade: o **Batedor da Ordem**, `prt_fild05 147,235`,
sprite 755 (`4_M_SAGE_C`, o mesmo tipo do Hugin e do Magic Scholar, que é quem
abre memória no rAthena). Abre a mesma instância, sem teto.

**A Emily continua ligada**, e isso é a diferença para os Orcs: ela tem a cadeia
de história do campo (quests 12416/12417/12418), que é o conteúdo de novato
dali. As duas portas convivem e abrem a mesma memória; quem entra pelo Batedor
não ganha as quests dela.

#### As duas que continuam fora

- **Torneio de Magia.** O alvo do bRO é *"1 Muliphen"* — e **`Muliphen` não
  existe no nosso `mob_db`**, com nenhum nome. Não é questão de achar o Id: o
  monstro não está no vendor. Continua comentada.
- **Sussurro Sombrio.** A coordenada do bRO (`dali02 121,63`) é a `Scientist
  Doyeon#a2` da **Sky Fortress Invasion**, que já está carregada e pede só
  nível 145 (sem teto, sem quest) — serviria. Mas o alvo do bRO é *"elimine os
  Demônios de cada tipo"*, e a instância tem **onze** monstros `Immortal_`.
  Escolher três seria inventar, contra a regra §4.3. Falta a página do browiki.

### O Palácio das Mágoas em português (2026-08-09)

Testada e aprovada em jogo, a instância veio com o pedido óbvio: *"tá tudo em
inglês ainda"*. Traduzir instância já estava previsto na frente do §3 do
`PENDENCIAS.md`, mas com uma **pré-condição** anotada e não cumprida.

**A pré-condição, e ela era real.** O nome da instância é CHAVE —
`instance_create` e `instance_enter` resolvem por string —, e nos scripts ele
aparece assim:

```
.@md_name$ = "Palácio das Mágoas";
switch( instance_enter(.@md_name$) ) { ... }
```

A atribuição casa com o `RE_ATRIB` do extrator, então o nome entra no catálogo
como se fosse fala. E o `RE_TECNICO` **não** cobre: ele protege literal que
está *dentro* da chamada (`warp "gef_fild10"`), e aqui a chamada recebe uma
variável. Uma tradução divergente — "Palácio das Maguas", digamos — faria o
`instance_enter` procurar uma instância que não existe.

A cura foi o `nomes_de_instancia()`: lê os `Name:` de `db/re/instance_db.yml` e
`db/guerra/instance_db.yml` e os acrescenta a `tokens_intocaveis`. **A lista sai
do próprio banco, e não de uma constante** — assim acompanha sozinha quando uma
instância for renomeada.

**Um grupo por instância, e não um grupo `instancias`.** A regra do projeto é
só aplicar grupo inteiro: arquivo quase todo em inglês com uma frase solta em
português é pior que arquivo em inglês. As 16 juntas dão 4.910 falas, com
distribuição muito torta — num grupo só, nada seria aplicável até a última estar
pronta. Quinze apelidos entraram (`magoas`, `orcs`, `sarah`, …), um por arquivo.

**O Palácio das Mágoas fechou:** 303 pares, **201 textos distintos**, 255
traduzidos e **48 deixados em branco de propósito** — nome de mapa (`1@spa`),
label de evento (`::OnMyMobDead1`), nome único de NPC (`Lurid Royal Guard#dk`),
o `.bmp` dos cutins e o nome da instância. O `--aplicar` trocou 256 textos, com
**0 recusas**.

Duas escolhas de tradução que valem registro, porque os dois guardas se
confundem: **`Unpleasant Royal Guard` → Guarda Real Rabugento** (o da entrada,
que chama o jogador de "noob") e **`Lurid Royal Guard` → Guarda Real Sombrio**
(o do roteiro, que vira o Sakray).

Conferido depois de aplicar: o `instance_create("Palácio das Mágoas")` e o
`.@md_name$` continuam idênticos, os 128 labels e nomes únicos intactos, o
arquivo em cp1252 com 214 bytes acentuados e **zero U+FFFD**, e o map-server
subiu sem um `Unknown syntax`.

**As outras catorze continuam em inglês**, cada uma com o seu grupo pronto para
`--extrair`. A ordem barata é pelo tamanho: Batalha dos Orcs (55 falas) e Lago
de Bakonawa (62) são de uma sentada; Sonho Sombrio (1.261) é um projeto.

### Quatorze instâncias e a Fenda Dimensional em português (2026-08-09)

Continuação direta da seção acima, na mesma data. Dos dezesseis grupos da
frente, **quinze fecharam e foram aplicados**; sobrou o maior.

| grupo | pares | traduzidos | em branco |
|---|---|---|---|
| `magoas` | 358 | 309 | 49 |
| `bakonawa` | 121 | 88 | 33 |
| `orcs` | 189 | 109 | 80 |
| `polvo` | 141 | 104 | 37 |
| `porings` | 144 | 134 | 10 |
| `hospital` | 214 | 161 | 53 |
| `sarah` | 461 | 312 | 149 |
| `brinquedos` | 356 | 303 | 53 |
| `fenda` | 334 | 288 | 46 |
| `vermes` | 453 | 353 | 100 |
| `glastheim` | 495 | 406 | 89 |
| `fenrir` | 513 | 464 | 49 |
| `demonio` | 632 | 540 | 92 |
| `charleston` | 779 | 670 | 109 |
| `crescente` | 1.922 | 1.268 | 654 |

**"Em branco" não é dívida** — é nome de mapa, label de evento, nome único de
NPC, `.bmp` de cutin, código de cor e pontuação solta. O `--estado` conta esses
como não feitos, então 86% ali quer dizer completo. Ver `CLAUDE.md` §4.12.

**Falta um, o Sonho Sombrio (`jitterbug`), e ele ficou pela metade:** 418 dos
1.253 textos distintos preenchidos, do começo do roteiro até o encontro com a
Lagi. **O grupo não foi aplicado**, e não deve ser até fechar — meia instância
em português é o que a regra de "só aplicar grupo inteiro" existe para evitar.
O arquivo do rAthena continua inteiro em inglês; só o `.cat` mudou.

O `crescente` foi o primeiro feito **em levas** — 220 textos, gravar, pedir a
lista de novo, mais 460. O `--pendentes` só lista o que ainda está vazio,
então cada leva renumera e continua de onde parou. No fim sobraram 133
distintos, e os 133 eram exatamente os que ficam em branco de propósito: nome
de mapa, arquivo de cutin, nome único de NPC e pontuação. É esse o sinal de
que um grupo fechou.

#### Os catálogos commitados estavam velhos, e isso quase passou batido

O `PROXIMA-SESSAO.md` afirmava que os dezesseis catálogos estavam extraídos com
os contextos novos. **Não estavam.** O `vermes` tinha 331 pares e a re-extração
devolveu **453** — os 122 que faltavam eram justamente `mapannounce` e
`unittalk`, o texto da faixa do alto e do balão de monstro.

Onze dos dezesseis estavam assim, e o erro é do tipo que não se denuncia: o
catálogo abre, tem conteúdo, o `--aplicar` roda sem recusa e o grupo marca
100% — só que a instância continua gritando em inglês na tela. Quatro grupos
(`porings`, `hospital`, `sarah`, `brinquedos`) já tinham sido dados por prontos
antes de o problema aparecer e precisaram de uma segunda leva.

A regra que sobe disso está no `CLAUDE.md` §4.13: **`--extrair` antes de
traduzir, sempre.**

#### As três convenções que este lote fixou

**1. Nome de criatura TRADUZ.** A dúvida é real: dentro de instância o nome que
flutua sobre o monstro vem do 4º argumento do `monster`/`areamonster` do
próprio script, que está em inglês e **não** entra no catálogo — então
"Missão: elimine os 'Orcs Encantados'" convive com um bicho rotulado
`Enchanted Orc`. Optou-se por traduzir mesmo assim, por dois motivos: é o que o
Palácio das Mágoas já tinha aplicado (`Magic Sword Tartanos` → *Espada Mágica
Tartanos*), e meia frase em inglês é exatamente o que a regra de "só aplicar
grupo inteiro" existe para evitar. O `orcs` chegou a ser escrito com os nomes em
inglês e foi **revertido e refeito** para não criar duas convenções no mesmo
projeto.

Onde o bRO tem nome, é o do bRO — `db/guerra/mob_db.yml`, que foi gerado do
`navi_mob_br.lub`: `High Orc` → Grand Orc, `Orc Archer` → Orc Arqueiro,
`Stalactic Golem` → Golem Estalactítico, `Wraith` → Alma Penada, `Orc Hero` →
Orc Herói. Os exclusivos de instância (1981 a 1984, os `Faceworm*`, os
`Octopus`) não estão na tabela e foram traduzidos aqui.

**2. Nome de habilidade, item e mapa sai da tabela do CLIENTE, inclusive
quando ela não traduziu.** O `skillinfolist.lub` deu os treze nomes do roteiro
do Fenrir (`Thunder Storm` → Tempestade de Raios, `Road of Vermilion` → Ira de
Thor, `Cloud Kill` → Maldição de Jormungand, `White Imprison` → Exílio, …). E
deu também o contrário: **`Mind Blaster` fica em inglês** na Torre do Demônio,
porque é assim que o `MER_INVINCIBLEOFF2` aparece no arquivo do cliente. A
regra vale nos dois sentidos.

O mesmo para item: `Explosive Powder` é o 6213, e o `itemInfo.lua` o chama de
**Pó Explosivo** — traduzir de cabeça sairia "Pólvora", que é outro item. E
para mapa: `Dimensional Gap` virou **Espaço Dimensional** porque é o que o
`mapnametable.txt` põe em `dali.rsw`; `Dimensional Rift`/`Crack`, que são a
passagem e não o lugar, viraram **Fenda Dimensional**.

**`Ash Vacuum` ficou em inglês** — não está no `mapnametable`, nem em nenhuma
outra tabela PT desta máquina, e inventar nome de lugar é o que a regra §4.3
proíbe.

**3. Fragmento montado com `+` se traduz olhando a ORDEM, não a frase.** O
anúncio de entrada de instância aparece em oito arquivos e em três ordens
diferentes: `[grupo][frag][personagem][frag]` nos Orcs, no Polvo e no Hospital;
`[personagem][frag][grupo][frag]` no Palácio e na Sarah. Traduzir o fragmento
do meio como `", do grupo "` na primeira forma sairia *"GrupoX, do grupo
Fulano"* — plausível e invertido. A forma que serve para a primeira é
`" - o aventureiro "`.

O caso extremo está no Covil de Vermes: `n + " unbroken " + ("eggs"|"egg")`. Em
português o adjetivo anda junto do substantivo, então o fragmento do meio virou
**um espaço só** e `intactos` migrou para o substantivo.

#### Duas armadilhas achadas lendo o script

**`DIR_NORTHWEST` e irmãos, na Torre do Demônio, entram em NOME DE VARIÁVEL.**
O `DevilTower.txt` faz `'coord_seal_DIR_NORTHWEST` e `'round[DIR_NORTHWEST]`.
Eles chegam ao catálogo por um `setarray` de texto, parecem rótulo de direção e
não são: traduzir faria o script procurar variável que não existe, e o selo
mágico simplesmente não andaria. Subiu para o `CLAUDE.md` §5.

**`F_GetPlural` aplica regra de plural INGLESA ao que a gente escrever.** No
Covil de Vermes e no quadro de recordes, `verme`, `segundo`, `minuto` e `ovo`
passam por ela. Todos os quatro caem no ramo padrão (acrescenta `-s`) e saem
certos em português — mas só por sorte de terminação: palavra terminada em
`-s`, `-x`, `-z`, `-f`, `-y` ou na lista de exceção em `-o`
(`potato|tomato|…`) sairia errada, e nada avisaria.

#### O que foi verificado

Depois de cada lote, `--aplicar <grupo> --verificar` (0 recusas em todos) e
reinício do map-server procurando `Unknown syntax` no `log/map-msg_log.log` —
**nenhum**, nos quinze. O `--aplicar` recusou sozinho um caso, e corretamente:
`"Sarah Irene's alter ego"`, no Fenrir, é dado técnico.

A gravação passou por três travas próprias: recusa caractere fora do cp1252,
recusa `\xef\xbf\xbd` no resultado e recusa aspa dupla dentro da tradução.

---

## A rodada de 2026-08-09 — 47 itens, e a metade que faltava do manto

O pedido tinha seis listas de item e uma linha de trava, e o que ele
custou não estava nas listas: **nove dos onze mantos pedidos eram, até
aquele dia, impossíveis**. Fechar isso é a parte desta rodada que vai
sobreviver a ela.

### A trava: a Maçã da Inocência aparecia na aba de venda

A Maçã (30999) já tinha `NoDrop`, `NoTrade`, `NoStorage`,
`NoGuildStorage`, `NoMail`, `NoAuction` e `NoCart` — a lista inteira
menos uma, e a que faltava era justamente a que o jogador vê. Sem
`NoSell` ela entrava na aba de venda de qualquer NPC de loja.

Foi um campo. O que precisou ser conferido antes é o `CLAUDE.md` §10:
`itemshop` passa a moeda por `pc_can_sell_item`, que **recusa item
`NoSell`** — se a Maçã fosse cobrada por uma loja assim, a trava
quebraria a compra. Não é o caso: o Mestre de UP cobra com
`countitem`/`delitem` (`npc/guerra/mestre_de_up.txt:102`), fora de
qualquer loja.

### `ferramentas/estende_robeid.py` — escrito, e reescrito no mesmo dia

O §4 registrava desde 2026-08-05: *"o que falta escrever: um
`estende_robeid.py` espelhado no `estende_accessoryid.py`"*. Nove dos onze
mantos pedidos esbarraram exatamente nisso — `View` fora das 120 entradas
da nossa `spriterobeid.lub` de 2021-11-03, e o `instala_manto.py` os
recusava por escrito.

Escrito, aplicado, tabela de 120 para 129 slots, `luac -p` OK, round-trip
OK — **e nenhum dos nove desenhou.** A ferramenta que o `PENDENCIAS.md`
pedia havia quatro dias resolvia um problema que não era o problema. O que
veio depois está na seção seguinte, e é a parte que valeu a rodada.

Aqui ficam as três coisas do formato, que continuam valendo.

**O `spriterobename.lub` tem TRÊS globais, e o terceiro é um vetor.**
`RobeNameTable`, `RobeNameTable_Eng` e `RobeTopLayer` — este último não é
mapa: é a lista dos mantos que o cliente desenha **por cima** do
personagem (mochila, bolsa, asa que passa na frente), 38 dos nossos 120.
Regerar o arquivo sem ele compila, sobe e não dá erro nenhum; os 38
passariam a desenhar atrás, calados. Dos nove novos, oito entraram no
vetor porque o bRO os põe lá; o de fora é a Capa de Herói, que é capuz.

**O `instala_manto.py` estava lendo a tabela errada, e por sorte não doía.**
`vv.tabela_lua` devolve os pares de todas as tabelas do arquivo numa lista
só, e um `dict()` por cima ficava com a última — a `_Eng`. Medido: das 120
entradas, 98 têm os dois nomes iguais e a diferença não aparecia; **nas 17
em que diferem, a pasta que existe no GRF é a da `RobeNameTable` em 17 de
17, e a da `_Eng` em 0**. O `_Eng` é lista paralela de consulta, não
caminho. Os treze de 2026-08-08 caíram todos nas 98.

**A terceira trava é mais dura aqui do que no chapéu, e a assimetria é do
formato.** O `estende_accessoryid.py` só confere arte antes de gravar num
ramo, com o argumento de que View novo já chega quebrado com modal.
Manto **não**: sem entrada de tabela ele fica invisível e **calado**,
porque o cliente nem tem nome de pasta para procurar. Gravar a entrada sem
ter a arte troca silêncio por caixa de erro — e isso é piorar. Então aqui a
conferência vale para todo View novo.

**E o `instala_manto.py` precisou aprender a ler o disco antes do GRF.**
Custou uma rodada: com o override já gravado, ele continuou respondendo
pelo GRF de 2021 e recusou um manto cuja entrada acabara de ser posta.
Mesma lição que o `valida_visual.le_tabelas_acessorio` já tinha aprendido
do outro lado — o `DataFolderFirst` faz `cliente\data\` vencer, e
ferramenta que consulta a tabela tem de consultar a que o cliente lê.

### As seis lojas, e as três leituras que o pedido exigiu

O pedido listava "Capa" duas vezes e "Cabeça meio" duas vezes, e as duas
duplicatas não eram engano: quem decide é o `Locations:` do `item_db`.

| lista do pedido | loja | por quê |
|---|---|---|
| "NPC de Visuais: Capa" | Manteleiro | `Costume_Garment` |
| "Capa" (três com `[1]`) | **Capeiro** | `Garment` de verdade — Defense, peso, refino |
| "Visual: Cabeça topo/meio/baixo" | Costumeiro / Adereceiro / Camareiro | `Costume_Head_*` |
| "Cabeça meio" (um com `[1]`) | **Ocleiro** | `Head_Mid` de verdade |

Contagem final: Costumeiro 146→164, Adereceiro 116→124, Camareiro
117→123, Manteleiro 13→24, Capeiro 15→18, Ocleiro 11→12. **47 itens.**

**Duas repetições no pedido, e nenhuma virou item repetido na vitrine.**
O Meda Elmo (410121) estava no Adereceiro desde 2026-08-05 e não entrou de
novo; o Traje de Leão (20194) vinha listado duas vezes na mesma lista de
topo e entrou uma. Conferir antes de acrescentar é o que impede a mesma
peça aparecer duas vezes — a lição da Capa de Magma, de 2026-08-08.

**Uma mudou de loja no mesmo dia, e é a que deu a regra.** A Máscara de
Minorous (21207) veio na lista de topo e é `Costume_Head_Low`/`_Mid` no
`item_db`, sem `Head_Top` nenhum — no Costumeiro ela não equiparia no slot
que a placa anuncia. Entrou lá na primeira passada, a ressalva foi escrita,
e o dono mandou movê-la: foi para o **Adereceiro**, a loja de meio, onde
equipa. Os outros seis da rodada que servem a mais de um slot têm
`Costume_Head_Top` entre eles, então para esses a placa não mente e eles
ficaram.

É a segunda peça da fileira a mudar de vitrine por esse motivo. A primeira
foi a Piscadela de Freya, em 2026-08-07, e aquela ainda custou um override
no `item_db` porque o nosso rAthena discordava do bRO. Esta não custou
nada: o `Locations:` já estava certo, faltava lê-lo. Virou o `CLAUDE.md`
§4.14.

**Cinco itens estavam fora do `itemInfo.lua`** — apareceriam sem nome e sem
ícone na própria vitrine. Vieram do bRO pelo `completa_iteminfo.py`, com o
`Name` do servidor sincronizado depois pelo `nomes_pt_item_db.py`: 480155
(Capa de Herói, que o `item_db` chamava de "Costume National Flag"), 20612
(Escudo de Oridecon), 480188 (Asas da Valquíria Caída), 480251 (Asas
Majestosas) e 410010 (Olhos Ilusórios).

**A 480188 é a primeira capa do Capeiro com `View`.** As outras dezessete
são capa de status, sem desenho vestido. O `View` dela é 131, o **mesmo** da
versão cosmética que foi para o Manteleiro (480189) — então a entrada de
tabela e a pasta de sprite serviram às duas, e não houve nada a fazer por
ela em separado.

### O que foi verificado

`valida_visual.py` deu **0 faltando** nos 47. O map-server foi reiniciado e
o `log/map-msg_log.log` não trouxe nenhum `Unknown syntax` — a busca que o
`CLAUDE.md` §5 manda fazer, porque uma linha ruim mata o arquivo inteiro e
o erro fica soterrado sob centenas de `[Warning]` inofensivos. Os dois
`.lub` gerados passaram no `Tools\luac.exe -p` do ROenglishRE. E o
`estende_robeid.py` foi rodado três vezes seguidas para provar que o
override não deriva: 129 constantes nas três.

**O cabeçalho do `mercado_de_visuais.txt` mandava conferir uma coisa, e ela
aconteceu.** Ele afirmava que aquele arquivo não devia produzir o aviso
`npc_parse_shop: Item X discounted buying price`, e que se aparecesse era
para conferir. Apareceu, sete vezes. A conta foi refeita item a item: são
nove itens com `Buy` entre 435, todos com `Buy` 10 ou 20, ou seja 4 ou 9
zeny de lucro por compra — o mesmo tamanho das duas exceções que o
cabeçalho já aceitava. A frase mudou; a lista dos nove ficou escrita, para
que a próxima conferência saiba quais ignorar.

### O que faltava ver no jogo — e era exatamente isso

Ficou escrito, no fim desta seção, que o manto nas costas do personagem era
o único pedaço que ninguém tinha visto, *"e a tabela, a arte e a validação
dizem que sim, e as três já disseram isso junto antes sem que alguém
tivesse olhado"*. Olhou-se, e as três estavam certas e a peça não desenhava.
A seção seguinte é o que se aprendeu.

---

## O teto de 120 do manto — três hipóteses certas e uma peça invisível (2026-08-09)

Continuação direta da seção acima. Os onze mantos entraram na loja com
`valida_visual.py` dando 0, `luac -p` passando, round-trip conferido e o
map-server subindo limpo — e **cinco deles não desenhavam nas costas do
personagem**. É a rodada que vale mais pelo método do que pelo resultado.

### O relato do dono, que virou a única medida confiável

Doze peças equipadas, uma a uma:

| | slot |
|---|---|
| desenham | 61, 73, 75, 82, 90, 99, 104, 114 |
| **não** | 122, 136, 148, 154, 158 |

Maior que funciona: 114. Menor que falha: 122. A tabela do GRF de 2021-11-03
vai até **120**. A fronteira estava lá desde o começo, e só apareceu quando
alguém equipou as peças e disse quais.

### As três explicações plausíveis, e por que cada uma caiu

Todas as três eram verificáveis offline. **Todas as três deram OK, e nenhuma
era a causa** — que é o ponto inteiro desta seção.

**1. Falta de arte.** Descartada por um item: o Escudo de Oridecon (slot 90)
desenha, e a arte dele foi copiada na *mesma* rodada, pelo *mesmo*
`instala_manto.py`. Se o pipeline de arte estivesse quebrado, ele também
falharia. Conferido de perto: as pastas dos que falhavam tinham a sprite da
classe do personagem (Sura), idêntica à de um que funciona.

**2. O arquivo não chega ao cliente.** Descartada pelo **horário de acesso**:
`spriterobeid.lub` e `spriterobename.lub` foram abertos às 21:11:39, no mesmo
segundo que o `accessoryid.lub`, que comprovadamente funciona. Isso é um dado
que o Windows dá de graça e que ninguém tinha pensado em olhar.

**3. Buraco na numeração.** A hipótese mais bonita, e errada. A tabela do
cliente vai de 1 a 120 sem faltar número; a do bRO, de 1 a 259 com um só
buraco; a que eu tinha gravado pulava de 120 para 122, 125, 131 — **29
vazios**, e os nove pedidos estavam todos depois do primeiro. Fechei a faixa,
o cliente leu a tabela contígua de 1 a 158 (mtime 21:34, acesso 21:42,
screenshot 21:44) e **nada mudou**.

Também não era o servidor: o campo é `uint16` no pacote e `int16` no `status`.

### A sonda — o que respondeu em uma rodada

Depois de três hipóteses, a pergunta que faltava não era "o que está errado",
era **"o meu arquivo chega à tela?"**. E ela não se responde procurando o
efeito que se quer: se responde com uma marca que não dependa dele.

`estende_robeid.py --sonda 114=C_20th_Anniversary_Wing` reaponta o slot 114 —
a Espada do General, que desenha — para a pasta das Asas Laureadas. Reabrir o
cliente, equipar a espada:

- **apareceram asas** → o override manda, o cliente monta a tabela dele;
- **apareceu a espada** → o override é lido e ignorado.

Apareceram asas. Três coisas caíram no lugar de uma vez: o arquivo manda, a
arte das Asas Laureadas está boa (foi ela que apareceu), e **o defeito é só o
número do slot**.

É a mesma lição do `ajusta_tamanho_fonte.py`, e desta vez ela foi aplicada
tarde. Subiu para o `CLAUDE.md` §5 na forma geral: **tabela certa + arte certa
+ arquivo lido ≠ desenha na tela.**

### O conserto: reaproveitar slot morto

Levantar o teto é patch de exe. Tentei achar a constante em volta da
referência a `ReqRobSprName` (`0x008278ca` no `Ragexe_unpacked.exe`) e parei:
sem desmontador, varredura de bytes só devolve `cmp edi, 198` repetido, que
não são instrução. Está no `PENDENCIAS.md` §4, com o ponto de partida anotado.

O que dava para fazer hoje: dos 120 slots que o cliente aceita, **40 não têm
arte nenhuma** — a tabela sabe o nome da pasta e a pasta não existe em GRF
nenhum. Já não desenhavam nada, então apontá-los para a arte nova não tira
nada de ninguém. Sete dos nove doadores escolhidos não são citados por item
algum do `item_db`; os outros dois, por um item cada, nenhum deles em loja
nossa.

| peça | slot original | passa a usar |
|---|---|---|
| Capa de Herói | 122 | 41 |
| Guitarra de Deviling | 125 | 49 |
| Asas da Valquíria Caída / Amaldiçoadas | 131 | 74 |
| Asas Laureadas | 136 | 77 |
| Mochila Multiuso | 137 | 94 |
| Muranyasa | 147 | 100 |
| Tridente com Lacinho | 148 | 20 |
| Lança de Valquíria | 154 | 29 |
| Katanas do Mestre Tengu | 158 | 30 |

**Uma fonte da verdade, e é o `View:` do `db/guerra/item_db.yml`.** O
`estende_robeid.py` lê de lá e escreve a tabela do cliente para combinar. Não
há lista de-para do outro lado, e não pode haver: seria a metade-no-cliente do
`CLAUDE.md` §9 outra vez, duas listas divergindo sem dar erro. Com uma fonte
só, rodar de novo não muda nada, e `--reverter` e "tirar o `View:`" dão no
mesmo.

**Sobram 31 doadores.** Passado isso, ou sai o patch de exe, ou não entra
manto novo — e é por isso que o `varre_cosmeticos.py` **continua** sem
classificar manto como `curavel`: prometer cura para 45 quando cabem 31 é o
mesmo erro de prometer cura que não há como cumprir.

### Duas coisas que escrevi hoje e desfiz no mesmo dia

**O preenchimento de buracos**, escrito para a hipótese 3, ficou meia hora no
repositório e deixava 29 entradas inúteis. Saiu.

**A recuperação do próprio override.** Fazia sentido quando o script
*acrescentava* slot — relia o arquivo para não perder rodadas anteriores.
Depois da reescrita virou o oposto: arrastava, rodada após rodada, as 38
entradas acima de 120 da tentativa que não funcionou, sem que nada as pedisse.
Agora o override é refeito do zero toda vez, a partir do GRF mais o item_db.

### O que foi verificado

As 111 entradas não reaproveitadas ficaram byte a byte iguais às do GRF
(conferido com um leitor independente do que gera o arquivo — buraco que a
primeira versão tinha, porque `monta` e `confere` partiam do mesmo leitor). A
arte dos nove destinos existe. `luac -p` passa nos dois `.lub`. O map-server
subiu com as dez entradas novas de `item_db` e sem `Unknown syntax`. E, o que
decide, **o dono confirmou as cinco peças na tela.**

## A resistência a humano que não fechava a conta (2026-08-09)

O dono montou um Sura de guerra e somou, peça a peça, a resistência a humano
que ele deveria ter. Deu perto de 100%, e o motivo de o número importar é que
no bRO o teto ficou em 97% por muito tempo — acima de 100 o jogador
simplesmente não toma dano, e por isso lá algumas cartas foram bloqueadas. A
suspeita dele era a **Carta Caídos**, que fecha conjunto com a Carta Guerreiro
Orc e dá mais 15%.

Só que, com tudo equipado, um Rune Knight **sem nenhum equipamento além da
arma** acertou 53.061 com Impacto Flamejante. Alguma coisa não fechava.

### O que foi conferido antes de acusar qualquer um

A conta do dono saiu das descrições da tela. Descrição vem do `itemInfo` do
cliente, não do script do servidor (§4.9 do `CLAUDE.md`), então a primeira
coisa foi refazer a soma pelo `item_db`:

| Peça | ID | `RC_Player_Human` no servidor |
|---|---|---|
| Anel de Ameretat | 490290 | 3 |
| Amuleto Mitológico | 490337 | 3 |
| Botas de Guivra | 470274 | 10 |
| Capa do Comandante | 20925 | **3** — a tela diz 5, e diz "Humano e Doram" |
| Escudo Alado | 460025 | 5 |
| O Criador (cajado) | 550021 | 10 |
| Algazarra (armadura) | 450338 | 7 |
| Servos de Morroc | 420236 | 3 |
| Adorno Angelical | 410142 | 5, via `RC_All` |
| Cocar do Orc Herói +16 | 400006 | 16, via `RC_All` |
| conjunto Cocar + C. Guerreiro Orc | `db/re/item_combos.yml:22019` | 30 |
| conjunto C. Caídos + C. Guerreiro Orc | `db/re/item_combos.yml:5052` | 15 |

**Total: 110%.** `RC_All` entra na mesma soma que `RC_Player_Human`
(`battle.cpp:1129`), então Cocar e Adorno contam inteiros.

Três hipóteses caíram aqui:

1. **Não existe teto de 99%.** O `APPLY_CARDFIX` (`battle.cpp:806`) grampeia em
   `max(0, fix)` — passando de 100% o dano vira zero, não 1%.
2. **Os dois conjuntos funcionam juntos.** O `pc_checkcombo`
   (`pc.cpp:11806`) só recusa conjunto repetido **pelo id do conjunto**, e só
   impede reusar o mesmo item **dentro do mesmo conjunto**. Uma Carta Guerreiro
   Orc fecha os dois ao mesmo tempo, e fecha.
3. **A Thanatos não tem nada com isso.** A carta 4399 é
   `bonus bDefRatioAtkClass,Class_All` — ignora DEF, não passa perto do
   `battle_calc_cardfix`.

E a Caídos era inocente: sem ela o Sura ainda estava em 95%.

### O furo

No renewal o dano físico é montado em parcelas, e a redução do alvo é aplicada
em cada uma **antes** de somar (`battle.cpp`, bloco "Card Fix for target"):
`statusAtk`, `weaponAtk`, `equipAtk` e `masteryAtk` passam pela redução. O
`percentAtk` **não estava na lista**, e entrava inteiro na soma da linha
seguinte.

Isso funcionaria se `percentAtk` fosse desprezível. Ele é calculado bem antes,
no trecho comentado como *"AtkRate gives a static bonus from (W.ATK + E.ATK)"*:

```c
wd->percentAtk = (wd->weaponAtk + wd->equipAtk) * sd->bonus.atk_rate / 100;
```

A arma do Rune Knight era a **Lâmina Sagrada** (`Copy_Gram`, 500009), em +16:

```
if (BaseLevel>=100) { bonus bAtkRate,10*.@r; }     ->  bAtkRate 160
```

Ou seja: as quatro parcelas reduzidas iam a **zero**, como a conta de 110%
mandava — e sobrava `percentAtk`, valendo 1,6× (W.ATK + E.ATK), intocado, para
o multiplicador da habilidade multiplicar. Com 110% de resistência o alvo ainda
tomava perto de 60% do dano. **Uma arma com `bAtkRate` alto é um "ignora
reduções" disfarçado de ATQ%** — e fura resistência a raça, a elemento, a
tamanho e a classe, todas de uma vez, sem nada no log.

### A correção

`rathena/src/custom/reducao_de_dano.hpp` (nosso) põe o `percentAtk` na mesma
lista, no mesmo lugar. O enxerto no `battle.cpp` é um include e uma chamada —
sete linhas, no padrão do `src/custom/refino.hpp`. Entrou na tabela do §2 do
`CLAUDE.md`.

Usa o `nk` cheio, e não o `ignoreele_nk` do `statusAtk`, porque o `percentAtk`
nasce de `weaponAtk + equipAtk`, que são parcelas **com** elemento — o
`battle_attr_fix` já rodou nas duas.

**Por que corrigir a parcela e não mover a redução para o fim:** dá no mesmo.
Tudo que vem depois da soma é multiplicativo (P.ATK, crítico, curta/longa
distância e, por último, o multiplicador da habilidade), então reduzir parcela
a parcela antes da soma é idêntico a reduzir no fim — **desde que toda parcela
passe pela redução**. Faltava uma.

Fora da correção, de propósito: dano fixo somado depois da conta (a Lâmina de
Aura e os outros `ATK_ADD` que a habilidade declara como acréscimo fixo)
continua fora da redução. `NJ_ISSEN` e `GN_FIRE_EXPANSION_ACID` nunca tiveram o
furo — o rAthena pula a redução do alvo para os dois no bloco de parcelas e a
aplica mais tarde sobre o `wd.damage` inteiro, que já inclui o `percentAtk`.

Compilado e no ar em 2026-08-09, e **confirmado em jogo pelo dono em
2026-08-10** — que é o que decide, porque verificação offline que passa não é
prova de efeito.

O catálogo do que continua fora da redução — habilidades com `IgnoreDefCard`,
dano fixo declarado, reflexo, dano de status — virou documento próprio,
`REDUCAO-DE-DANO.md`, com a ordem das etapas da conta e uma receita de cinco
passos para o próximo "fulano furou minha resistência". O que sobrou em aberto
não é código, é economia: a soma de 110% agora zera dano de verdade, e decidir o
teto está em `PENDENCIAS.md` §1h.

## O teto de 99,9%, e a Carta Caídos fora da conta de humano (2026-08-10)

Com o furo do `percentAtk` fechado (seção acima) e confirmado em tela — 110% de
resistência passou a dar miss na maioria dos golpes —, o dono foi ao problema de
balanceamento que estava escondido atrás dele: **110% é imunidade**, e chegar lá
custava só equipamento de loja.

### A Carta Caídos sai da conta de humano

O topo de cabeça já oferece 13 a 16% de resistência a raça pelo próprio
equipamento — o Cocar do Orc Herói +16 dá 16 via `RC_All` — e o conjunto dele
com a Carta Guerreiro Orc soma outros 30. Mais 15 pela Carta Caídos encaixada
punha **a cabeça sozinha acima de 60%**, e o personagem em 110. O bRO resolveu
o mesmo problema bloqueando a carta.

Aqui ela continua existindo: o que saiu foi **uma linha** do conjunto 27328 +
4066. O `bonus2 bSubRace,RC_Player_Human,15` foi embora; o
`bonus2 bSubRace,RC_DemiHuman,15` **ficou**, porque vale contra monstro
humanoide e não vale nada em PvP — tirar também seria punir o uso em campo por
um problema de guerra.

**Como se sobrescreve conjunto sem tocar no arquivo do rAthena:** o
`ComboDatabase` casa conjunto pela **lista de itens ordenada**
(`find_combo_id`, `src/map/itemdb.cpp:3796`), não por um id declarado. Repetir a
mesma dupla num arquivo importado depois **troca o `Script` do conjunto que já
existe**, não cria um segundo. Está em `db/guerra/item_combos.yml`, e é o mesmo
caminho para qualquer outro conjunto que a gente queira mudar. Para apagar o
conjunto inteiro em vez de mudar o efeito, o campo é `Clear: true`.

Recarrega com `@reloaditemdb` — conjunto entra junto com item.

**O que isto não conserta:** a descrição na tela. O cliente continua dizendo
"Resistência as raças Humano e Humanoide +15%", porque quem escreve a descrição
é o `itemInfo` do cliente. Ficou em aberto no `PENDENCIAS.md`.

### O teto de 99,9%

Tirar 15 de um lugar não resolve a classe do problema: some outra peça e a soma
volta a 100. O rAthena grampeia a redução em `max(0, fix)` — **100% de
resistência entrega dano zero**, imunidade completa a tudo que passa por carta.

O `0` virou um piso configurável, em `src/custom/reducao_de_dano.hpp`
(`reducao_piso`), com o valor em `conf/guerra/battle_guerra.txt`:

```
reducao_dano_teto: 999      // milesimos. 999 = 99,9%; 1000 desliga a trava
```

Milésimos porque é a unidade que o `cardfix` já usa (1000 = sem redução), então
99,9% é exato — não foi preciso arredondar para 99. Muda com
`@reloadbattleconf`.

**Por que o piso mora no fim da conta e não no passo da raça.** Tentar grampear
o passo da raça não sustenta: o `cardfix` é uma conta só, encadeada, e cada
passo é divisão inteira — um `cardfix` reduzido a 1 na raça vira **0** no passo
seguinte (`1 * 90 / 100 == 0`), e a imunidade volta pela porta dos fundos. Só no
fim o piso se segura. Consequência aceita de propósito: **o teto vale para a
redução de carta inteira**, não só para a de raça — elemento, tamanho e classe
entram na mesma conta. A regra passou a ser "nada é imune".

O catálogo do que continua escapando — habilidade com `IgnoreDefCard`, dano fixo
declarado, reflexo, dano de status — está em `REDUCAO-DE-DANO.md`, que ganhou a
§1b sobre o teto.

---

## A Capa do Comandante passou a entregar o que promete (2026-08-10)

Rabo do trabalho acima. A **Capa do Comandante** (20925) foi o item que denunciou
a armadilha do `CLAUDE.md` §5 — *"a descrição do item na tela discorda do script
do servidor, no NÚMERO, não só na presença"*. Ela apareceu em 2026-08-09, ao
refazer no `item_db` uma soma de resistência a humano que tinha sido feita lendo
a tela, e ficou registrada como pendência sem conserto do lado do servidor.

A divergência era **dupla**, e a segunda metade é a que o relato de ontem não
tinha:

| | tela (`itemInfo.lua`) | servidor (`db/re/item_db_equip.yml`) |
|---|---|---|
| Humano | 5% | **3%** |
| Doram | 5% | **nada** |

O resto da descrição batia com o script linha por linha — HP e SP +3%, ATQ e
ATQM +10, os degraus em +5 e +7. Só a linha da resistência mentia.

### Corrigiu-se o servidor, e não o cliente

Decisão do dono. É o mesmo raciocínio do override do **400287** (Capacete de
Intensificação), e o comentário de lá já o dizia: entre trocar a descrição do
cliente e trocar o efeito do servidor, **trocar o servidor é o lado barato e o
lado certo**. Mexer no `itemInfo` custaria `instala_item.py` mais fechar e
reabrir o cliente, e deixaria a nossa descrição divergente da do bRO — que é a
nossa fonte de referência (`CLAUDE.md` §4.3).

O conserto é um override na seção OVERRIDES do `db/guerra/item_db.yml`, com
`RC_Player_Human,5` no lugar do `,3` e uma linha nova de `RC_Player_Doram,5`.

**A armadilha que este caso acrescenta: `Script:` é um campo só.** A mesclagem
do `ItemDatabase::parseBodyNode` é por **campo** — campo omitido mantém o valor
do `db/re/` —, mas ela não alcança *linha* de script. Sobrescrever uma linha
obriga a repetir o script **inteiro**, com os degraus de refino e tudo. O bloco
foi **copiado** do `db/re/item_db_equip.yml`; reescrever de cabeça é como se
perde um degrau sem que nada avise.

Provado com `difflib` contra o original: **uma linha trocada, uma acrescentada,
nada mais.**

### O `bonus bMdef,10` ficou — e não era divergência nenhuma

Era a dúvida aberta do pedido: o MDEF do script não aparece em linha azul de
efeito na descrição. Não aparece porque **MDEF de armadura nunca aparece** — ele
está no rodapé de status da própria descrição, `DEF: 20 DEFM: 10`, conferido no
`itemInfo.lua` deste cliente. Manter é o que a mesclagem faz de graça, e é o que
está certo.

### Os três conjuntos com as botas do Herói, no mesmo dia

Achados ao conferir a capa, e consertados logo em seguida, a pedido do dono. Os
**três conjuntos** (22035 Sapatos Relaxantes, 22036 Botas de Couro, 22037 Botas
de Ungoliant) prometem, cada um, *"Resistência as raças Humano e Doram +5%
adicional"*, e no `db/re/item_combos.yml` davam `RC_Player_Human,5` e **nada para
Doram**. Aqui o **valor já batia** — faltava só a raça, e era uma linha por
conjunto.

Foram para `db/guerra/item_combos.yml`, pelo caminho que a Carta Caídos abriu na
seção acima. Duas coisas que aquele caso não tinha mostrado, e que valem para
qualquer conjunto que a gente venha a sobrescrever:

- **A ordem em que se escrevem os itens não importa.** O `parseBodyNode`
  **ordena** a lista (`std::sort`, `src/map/itemdb.cpp:3940`) antes de guardá-la,
  e o `find_combo_id` compara vetor com vetor. O comentário do arquivo dizia
  "lista ordenada" e está certo — mas quem lê pode entender "na mesma ordem que
  eles escreveram", e não é isso.
- **Não há mesclagem de linha em conjunto, tampouco.** Conjunto que já existe tem
  o `combo->script` liberado (`script_free_code`) e substituído pelo nosso. É a
  mesma regra do `Script:` do item, e pela mesma razão cada bloco repete o script
  inteiro do rAthena, copiado de lá.

**A promessa mora só na descrição da capa.** As três botas não citam conjunto
nenhum no `itemInfo.lua` deste cliente — nem a capa, nem a palavra "Humano" —,
conferido entrada por entrada. É pela capa que o jogador lê o que ganha.

**Ninguém alcança esses conjuntos hoje:** as três botas não estão à venda em loja
nossa nenhuma (`estado_item.py --id 22035,22036,22037`). Entraram pela mesma
razão que o resto — a conta de resistência a humano se fecha no `item_db`, não na
tela —, e se um dia as botas entrarem no mercado já chegam certas.

Os três scripts foram gerados **copiando** os do `db/re/`, e o diff foi conferido
com `difflib`: **uma linha acrescentada em cada, nada mais.**

### A conta de resistência a humano, depois disto

A capa passou de 3 para 5 pontos. Com o teto de 99,9% no lugar, subir 2 pontos
não reabre a imunidade — mas é 2 a mais na soma que o dono está calibrando, e
vale lembrar de onde eles saem ao revisitar os números de PvP.

Recarrega com `@reloaditemdb`. Não exige reiniciar nem recompilar.

**A prova é medida, não lida.** O tooltip não serve — ele já dizia 5% quando o
servidor dava 3, é ele o mentiroso. Mesmo agressor, mesmo golpe, com e sem a
capa, **com o alvo bem abaixo de 100% de resistência somada**: perto do teto o
piso de 99,9% achata a comparação e 5 pontos parecem 0. Ficou no `PENDENCIAS.md`
§1h, junto com as outras duas sondas da mesma frente.

---

## A redução geral de 70% — guerra e a arena de Prontera (2026-08-10)

> **SUPERADA NO MESMO DIA.** O 70% virou **80%** e as duas isenções de
> habilidade caíram — ver "A redução subiu para 80%", mais abaixo. Esta seção fica
> porque é aqui que está o *como* (o `pk_mode`, as quatro chamadas, a sonda do
> nome falso), e nada disso mudou. **O que mudou foi o número e a última
> exceção.** O arquivo também mudou de nome: `reducao_pvp.hpp` →
> `reducao_geral.hpp`.

Pedido do dono no mesmo dia dos dois trabalhos acima, e é outra camada: aqueles
mexeram em **quem resiste**; este mexe no **dano final de todo mundo**.

O pedido, na íntegra do que importa: o bRO reduzia **70% do dano final na Guerra
do Emperium**, decisão tomada com a comunidade tempos atrás, quando os danos
começaram a ficar altos demais. Essa conta passa a valer para o nosso PvP —
principalmente a Arena de Combate de Prontera.

**Não é invenção nossa e não é ajuste fino de item:** é um multiplicador de 0,30
no fim da conta, nos mapas de guerra e nos mapas `pvp`.

### A metade da guerra não custou uma linha de C++

O rAthena já tem isso, e tem completo: `battle_calc_gvg_damage`
(`src/map/battle.cpp:2188`) multiplica o dano final por cinco taxas em todo mapa
`mapdata_flag_gvg2`. O padrão dele é **60 para habilidade e 80 para ataque
normal** (`conf/battle/guild.conf`) — ou seja, a guerra já vinha com 40% e 20% de
redução, e ninguém tinha reparado.

Os cinco foram para `conf/guerra/battle_guerra.txt` em `30`, que é o arquivo
importado **depois** do `guild.conf` (`conf/battle_athena.conf`, penúltima linha)
e portanto vence.

### A metade do PvP custou, e o motivo é uma armadilha inteira

**Não existe equivalente para mapa `pvp` no rAthena.** Existe algo que *parece*
ser: os cinco `pk_*_attack_damage_rate` (`conf/battle/misc.conf`), aplicados por
`battle_calc_pk_damage` e checados contra o mapflag `pvp` exatamente como se
quer:

```
if (battle_config.pk_mode == 1 && map_getmapflag(bl->m, MF_PVP) > 0)
    damage = battle_calc_pk_damage(*src, *bl, damage, skill_id, flag);
```

Três linhas prontas, o nome certo, o mapflag certo. **E não servem**, porque
estão trancadas atrás do `pk_mode` — que não é uma opção de dano, é o "servidor
PK inteiro". Ligar o `pk_mode` faz o `src/map/map.cpp:3791` marcar **todo mapa do
servidor** como `pvp`:

```
if( battle_config.pk_mode && !mapdata_flag_vs2(mapdata) )
    mapdata->setMapFlag(MF_PVP, true); // make all maps pvp for pk_mode
```

e arrasta consigo penalidade de morte por jogador (`pc.cpp:10024`), EXP extra por
diferença de nível (`pc.cpp:8382`), `pk_min_level`, `pk_level_range` e o sumiço
da UI de PvP (`clif.cpp:10836`). Para reduzir dano numa arena de 40x40 células, o
rAthena pede que Prontera vire campo aberto.

**A lição que vale para além deste caso:** opção com o nome exato do que se quer
pode estar amarrada a um modo de servidor inteiro. Ler o `battle_data` e achar o
nome não é o fim da busca — o fim é achar **o que mais liga naquele `if`**.

Daí o `src/custom/reducao_pvp.hpp` — hoje `reducao_geral.hpp`: os mesmos cinco
multiplicadores, com nome nosso (`pvp_dano_arma`, `_magia`, `_misc`, `_curta`,
`_longa`), ligados ao mapflag `pvp` e a nada mais.

### Cópia do GvG, e não do PK — as duas diferenças importam

A promessa do pedido é *"a mesma conta da guerra"*, então a função é cópia fiel do
`battle_calc_gvg_damage`. Os dois pontos em que ela difere do caminho do
`pk_mode`, os dois de propósito:

1. **Honra o `IgnoreGvgReduction`.** Duas habilidades do renewal declaram que
   escapam da redução de guerra — `NJ_ZENYNAGE` (Chuva de Moedas) e
   `GN_FIRE_EXPANSION_ACID`, as únicas duas no `db/re/skill_db.yml`. O caminho do
   PK não olha essa flag; o da guerra olha. Golpe que faz dano cheio no castelo
   tem de fazer dano cheio na arena, senão "a mesma conta" é mentira.

   > **ESTE ITEM CAIU NA MESMA TARDE**, e o argumento acima é o que estava
   > errado: a 80% de redução a habilidade isenta vale cinco vezes as vizinhas, o
   > que não é exceção, é dominância. Hoje ninguém escapa — nem na arena, nem na
   > guerra. Ver "A redução subiu para 80%". O item 2 continua valendo inteiro.
2. **Não filtra por tipo de atacante.** O `battle_calc_pk_damage` reduz só quando
   `src` e `bl` são os dois `BL_PC`; o de guerra reduz tudo que acerta alguém no
   mapa. Aqui reduz tudo — Homúnculo, mercenário, armadilha, invocação
   pertencem a um jogador, e o furo mais caro deste projeto (2026-08-09) foi
   justamente uma parcela de dano que ficou fora de uma redução. Deixar tipo de
   fora é convidar o mesmo bug.

   **Consequência dita em voz alta:** monstro em mapa `pvp` também passa a bater
   30%. Hoje não alcança nada — os únicos mapas `pvp` são as 84 arenas
   `pvp_n_*`/`pvp_y_*`, o `pvp_2vs2` e os três `turbo_e_*` do Corrida Turbo
   (`npc/mapflag/pvp.txt`), e nenhum é mapa de caça.

### Quatro chamadas, e por que não são duas

O enxerto no `battle.cpp` são quatro chamadas, três delas dentro do
`battle_calc_damage`. A repetição não é descuido — é onde o rAthena já repete a
dele:

- o **caminho normal** (`battle.cpp:2027`), por onde passam arma, magia e misc;
- **duas saídas antecipadas**, para habilidade que pula o resto da função:
  `SP_SOULEXPLOSION` (mais `PA_PRESSURE` e `HW_GRAVITATION` no pre-renewal) e
  `SJ_NOVAEXPLOSING`. As duas têm `return damage` próprio, e o rAthena põe a
  chamada de PK nas duas por isso mesmo. Cobrir só o caminho normal deixaria
  Soul Explosion e Nova Explosion **fora da redução** — e as duas já estão na
  lista de "ignora resistência de carta" do `REDUCAO-DE-DANO.md` §4a, ou seja
  seriam o golpe sem contra-medida nenhuma na arena;
- o **reflexo** (`battle_calc_return_damage`), que não passa pelo
  `battle_calc_damage`. Mesmo lugar onde o rAthena aplica GvG, campal e PK.

A função sai fora sozinha em mapa de guerra e de campal, então dá para chamá-la
sem checar mapa. Sem essa guarda, um mapa que tivesse os dois mapflags levaria as
duas reduções multiplicadas.

### As duas camadas se multiplicam — e é isso que muda a conta de PvP

Isto é o que precisa ser dito para quem for calibrar equipamento daqui em diante:
a redução de carta (resistência a humano) e a redução de 70% **não se somam**.
Alvo com 50% de resistência a humano na arena toma `0,50 × 0,30 = 15%` do dano
bruto.

Na prática o trabalho de ontem e de hoje empurram em direções opostas de
propósito: o teto de 99,9% garante que **nada é imune**, e o 0,30 garante que
**nada mata em um golpe**. As duas juntas é o que o bRO tinha.

### O que provou que pegou, e o que não provou

Compilou e subiu limpo: `MSBuild` no `map-server.vcxproj`, map-server parado
antes de linkar, e o boot sem um `Unknown syntax` e sem um `Unknown setting`.

**"Sem aviso" não vale como prova por si**, e aqui não valeu: um nome de opção que
o servidor não conhece produz `Unknown setting '%s' in file %s`
(`battle.cpp:9233`), mas ausência de aviso também é o que se vê quando o canal de
aviso não está chegando ao log. Então foi feita a sonda: uma linha
`pvp_dano_sonda_falsa: 30` no `battle_guerra.txt`, reinício do map-server, e o
aviso apareceu — **só para ela**, e nenhuma das dez linhas de verdade. Isso prova
as duas coisas de uma vez: o canal funciona, e os dez nomes foram aceitos. A
sonda saiu do arquivo e o map-server subiu limpo de novo.

**O que continua sem prova é o efeito na tela.** Está no `PENDENCIAS.md` §1i, com
a medição que decide.

---

## A redução subiu para 80%, e a última isenção caiu (2026-08-10)

Volta do pedido acima, no mesmo dia. Duas frases do dono, e cada uma custou uma
coisa diferente:

> "70 era como o bRO estava, e me parece alto ainda. Vamos aumentar a redução
> pra 80%! Lembrando que não quero diferenciar habilidades de ataque, quero que
> TODOS os danos de pvp entrem nessa categoria."

### O número: os dez valores foram de 30 para 20

Nada além de conf. Mas o registro importa por um motivo: **a partir daqui o
servidor deixou de seguir o bRO neste número.** A seção anterior justificava o 70%
dizendo "vem do bRO"; essa justificativa morreu. Está escrito no
`REDUCAO-DE-DANO.md` §1c e no cabeçalho do `battle_guerra.txt`, porque alguém que
leia só "o bRO usava 70" um dia vai "corrigir" o 20 para 30 pensando que está
voltando à referência.

### "Não diferenciar habilidade de ataque" já estava feito — e segue sendo risco de manutenção

Os dez valores já eram iguais. O que a frase mudou foi o **comentário**: o
`battle_guerra.txt` e o `reducao_geral.hpp` agora dizem que a separação em cinco
por ambiente é do rAthena, existe porque é por onde a informação chega (o `flag`
do golpe), e **não se usa**. Mexer em um dos dez é mexer nos dez.

Isto não dá para trancar em código sem inventar uma décima primeira opção que
governasse as dez, e uma opção que só existe para repetir um número é pior que o
comentário. Ficou no comentário, de propósito.

### "TODOS os danos" custou um enxerto, e é o enxerto mais frágil do projeto

Aqui estava a dívida de verdade. A primeira versão **respeitava** as duas isenções
do rAthena — `NJ_ZENYNAGE` (Chuva de Moedas) e `GN_FIRE_EXPANSION_ACID`, as únicas
duas do renewal com `IgnoreGvgReduction: true`. Eu as respeitei por um argumento
que era bom no dia anterior e ruim depois: *paridade com a guerra*.

O argumento morre na aritmética. **Com 80% de redução, a habilidade que escapa
vale cinco vezes o dano de qualquer outra.** Isso não é "uma exceção conhecida", é
a habilidade dominante do castelo. Uma isenção que custa 40% do dano é detalhe;
uma que custa 80% é regra nova.

Então a isenção caiu — **e caiu nos dois ambientes**, o que exigiu ir mexer no
lado que até então não tinha custado nada:

| | antes | agora |
|---|---|---|
| mapa `pvp` (nosso) | honrava a flag | `reducao_isenta_habilidade()` |
| guerra (do rAthena) | honrava a flag | `reducao_isenta_habilidade()` |
| campal (do rAthena) | honra a irmã (`IGNOREBGREDUCTION`) | **inalterada** |

**A função existe em vez de um `if` justamente para os dois não poderem
divergir.** Um número, um lugar, dois caminhos — `reducao_dano_isenta_habilidade`
em `conf/guerra/battle_guerra.txt`, `0` para ninguém escapar e `1` para devolver o
rAthena, sem recompilar.

### Por que este enxerto é diferente de todos os outros

**É o primeiro que SUBSTITUI uma linha do rAthena em vez de acrescentar uma.**
Todos os enxertos anteriores — os do `clif.cpp`, os dois do `reducao_de_dano.hpp` —
são linha nova ao lado do código de terceiros; um merge que os perca deixa um
buraco visível. Este trocou

```
if (skill_get_inf2(skill_id, INF2_IGNOREGVGREDUCTION))
```

por

```
if (reducao_isenta_habilidade(skill_id))
```

dentro do `battle_calc_gvg_damage`. Um merge do vendor que traga a linha original
de volta **compila, linka, sobe e não avisa** — e a Chuva de Moedas volta a ser
dominante na guerra, calada. Está no `CLAUDE.md` §2 e no `REDUCAO-DE-DANO.md` §6
com o que procurar: se `INF2_IGNOREGVGREDUCTION` reaparecer ali, o enxerto morreu.

A alternativa era não tocar o `battle_calc_gvg_damage` e deixar a arena mais
severa que o castelo em duas habilidades. Divergência silenciosa entre dois mapas
que deviam ter a mesma regra é exatamente o que este projeto já pagou caro para
aprender a não fazer.

### O arquivo mudou de nome

`src/custom/reducao_pvp.hpp` virou **`src/custom/reducao_geral.hpp`**. Deixou de
ser só do PvP no momento em que passou a abrigar a regra que a guerra também usa,
e nome de arquivo que mente é a primeira coisa que faz alguém procurar no lugar
errado. Era arquivo do mesmo dia, sem histórico a perder.

### O que se provou, e a sonda que ninguém pensaria em fazer

Compilou, subiu sem `Unknown syntax` e sem `Unknown setting` — e a técnica da
sonda de nome falso, da seção anterior, continua sendo o que dá valor a essa
ausência.

**O que NÃO se prova batendo com qualquer habilidade é a parte de "TODOS os
danos".** As duas habilidades que mudaram de comportamento são a Chuva de Moedas e
o `GN_FIRE_EXPANSION_ACID`; toda outra já era reduzida antes. Uma medição feita
com Impacto Flamejante confirma o 20% e **não diz nada** sobre a isenção. A sonda
certa está no `PENDENCIAS.md` §1i, e ela é também o único teste em jogo que
denuncia a morte do enxerto frágil acima.

### O que este par de rodadas deixou desequilibrado, e está anotado

Com 80% de corte no dano de golpe, **o dano que não é golpe passou a pesar cinco
vezes mais em termos relativos**: veneno, sangramento, queimadura,
`bonus2 bHPVanishRate` e dano de script saem por `status_fix_damage`, fora do
cálculo de batalha, e nenhuma das cinco chamadas os alcança. Não é bug e não tem
conserto neste arquivo — é consequência aritmética de reduzir tudo o resto. É o
candidato mais provável a aparecer no primeiro teste sério de arena, e por isso
está no `PENDENCIAS.md` §1i como decisão em aberto, e não como surpresa.

---

## O inventário do dano que escapa da redução (2026-08-10)

Terceira volta do mesmo dia, e a pergunta é boa o bastante para ficar registrada
inteira: se o dano de status ficou relativamente cinco vezes mais forte com o
corte de 80%, **isso é problema ou é parte do balanceamento que faltava?**

Não dava para responder sem a lista. A lista não existia. Agora existe:
`REDUCAO-DE-DANO.md` §1d.

### Como foi levantada, para poder ser refeita

O critério é único e mecânico: **todo dano que chega a um jogador sem passar por
`battle_calc_damage` nem por `battle_calc_return_damage`** — os dois lugares onde
as nossas chamadas moram. Na prática, os chamadores de `status_zap`,
`status_percent_damage`, `status_fix_damage` e `status_damage` dentro do
`status_change_timer` (`status.cpp:14135`), mais os de `battle_fix_damage`.

Deu **13 danos contínuos e 4 avulsos**. Cada um foi resolvido até o `case SC_`
que o contém, a fórmula, o intervalo (`status_get_sc_interval`, `status.cpp:9571`)
e a habilidade que o aplica — as últimas cruzando o `Status:` do
`db/re/skill_db.yml` com o nome da habilidade.

### A resposta: serve pouco, e o motivo não é o tamanho

**Três achados que só aparecem com os números na mão:**

1. **As três parcelas mais fortes não matam.** Veneno (1,5% HP máx/s) e Veneno
   Mortal (2%/s) param em 25% de HP — `if (status->hp > umax(status->max_hp / 4,
   damage))`. Bite Scar chama `status_percent_damage` com `kill = false`, que vira
   o `flag == 2` do `status_percent_change` e grampeia em `hp - 1`. Elas empurram
   o alvo para a beira e **entregam o golpe final a outra pessoa** — ótimo em
   arena cheia, quase nada em duelo.
2. **O dano fixo continua sendo ruído.** Sangramento é `rnd()%600 + 200` a cada
   dez segundos; Pyrexia é 100 a cada três. Reduzir o dano dos outros em 80% não
   promove essas duas a nada — o problema delas nunca foi o dano alheio ser alto,
   era o delas ser baixo em absoluto. **Só o que escala com HP máximo entrou na
   conversa.**
3. **O ganho é enviesado por classe**, e é isso que mata a ideia de usar o dano de
   status como alavanca geral: quem ganha é a **Guilhotina Cruzada** (três venenos
   pela Arma Envenenada, e o Sanguessuga mata), depois **Cavaleiro Rúnico e
   Ranger** (Queimadura), **Ladrão e derivados** (Envenenar) e **Doram** (Bite
   Scar, com 10% de chance). Classe sem status não ganhou nada.

**Nada foi mexido.** Nenhum desses números é configurável — são literais dentro do
`status_change_timer` —, então ajustar qualquer um é `src/custom/` e recompilar,
como foi a redução de PvP. A seção existe para a decisão ser tomada com os números
na mão, não para adiantá-la.

### E o levantamento achou um bug de verdade

**A Cotovelada Ascendente (`SR_CRESCENTELBOW`) escapa da redução de 80%.** Ela
entrega por `battle_fix_damage` (`battle.cpp:5247`), que chama `battle_damage`
direto e pula o `battle_calc_damage`.

O que faz dela um furo, e não mais um item da lista, é a composição:

```
rdamage = battle_calc_base_damage(...) * ratio / 100   <- nasce aqui, nunca reduzido
        + wd->damage * (10 + val1 * 20 / 10) / 10       <- vem do dano ja reduzido
```

e o `ratio` vai a **5000%**. A segunda parcela é proporcional a um número que já
levou o corte; a primeira cria valor novo.

**As vizinhas dela na mesma seção do `battle.cpp` estão certas**, e é a distinção
que impede um conserto atrapalhado: Instinto de Defesa devolve 50% de um dano já
reduzido; Reflect Damage, Devoção e Water Screen **redirecionam** o número já
reduzido para outro alvo. Nenhuma dessas cria valor. Só a Cotovelada.

Ficou no `PENDENCIAS.md` §1j, sem conserto, e com o motivo de não consertar no
susto: o bloco inteiro é contra-ataque, e "de quem é este dano" não é óbvio ali.

### O que esta rodada acrescenta ao método

**Pergunta de balanceamento se responde com a fonte, não com a intuição** — e a
intuição aqui estava errada em dois dos três pontos. "Dano de status ficou 5x mais
relevante" é verdade e **não** implica "dano de status virou alavanca": faltavam o
teto de 25% e o viés de classe, e nenhum dos dois aparece sem abrir o
`status_change_timer`.

## Nome de personagem com acento — as duas metades (2026-08-10)

Pedido do dono, com dois screenshots: `Barão de Libra` recusado na criação de
personagem, com a caixa *"Character Creation is denied."* — a mesma mensagem que
o char-server devolve para nome duplicado, nome curto e nome proibido. A
mensagem não distingue, e é por isso que o caminho da apuração foi o código.

### A causa: o filtro é BYTE A BYTE

O `char_check_char_name` (`src/char/char.cpp:1365`) faz

```
if( strchr(charserv_config.char_config.char_name_letters, name[i]) == nullptr )
    return -2;
```

com `char_name_option: 1` ("só as letras da lista") e a lista padrão do rAthena
contendo **apenas ASCII**. O cliente manda o nome em cp1252, então o `ã` chega
como o byte `0xE3`, que não está na lista — e o `-2` vira a caixa de erro.

A mesma variável governa **quatro** pontos, não um: personagem
(`char.cpp:1365`), clã (`int_guild.cpp:1199`), grupo (`int_party.cpp:517`) e
homúnculo (`int_homun.cpp:302`). Liberar a lista conserta os quatro de uma vez —
o que também quer dizer que quem mexer nela mexe em mais do que imagina.

### A segunda metade, que não aparece no código do filtro

Liberar as letras **não bastaria**, e essa foi a parte que só a medição
respondeu. As 105 colunas de texto do banco são `latin1`, mas o
`character_set_client` deste MariaDB 12.3 é `utf8mb4`, e o
`default_codepage` do `inter_athena.conf` vinha **comentado** — sem ele o
rAthena não manda `SET NAMES` nenhum (`inter.cpp:978`, `map.cpp:4416`).

Medido antes de mexer, com o nome do pedido:

| Conexão | Resultado do `INSERT` de `Barão de Libra` |
|---|---|
| `utf8mb4` (o que havia) | `ERROR 1366 (22007): Incorrect string value: '\xE3o de ...'` |
| `latin1` (a correção) | grava e devolve `426172E36F...` — o `0xE3` intacto |

Um byte cp1252 sozinho é UTF-8 inválido, então o MariaDB **recusa a gravação
inteira**. Se só o filtro tivesse sido liberado, a criação passaria pela
validação e morreria no SQL — outro sintoma, mesma frustração, e desta vez com
o erro num log que ninguém abre. Subiu para o `CLAUDE.md` §5.

`latin1` e cp1252 são o mesmo repertório na faixa `0xC0-0xFF`, onde moram todas
as letras acentuadas do português; divergem só em `0x80-0x9F` (aspas curvas, €,
™), que a lista de letras não permite. Nenhuma coluna do banco está fora de
`latin1`, então o `SET NAMES` não perde nada em lugar nenhum — conferido pelo
`information_schema` antes de aplicar.

### O que foi feito

Dois arquivos nossos, no padrão do `battle_guerra.txt`, e dois `import:` de uma
linha nos arquivos do rAthena (`CLAUDE.md` §2):

- **`rathena/conf/guerra/char_guerra.txt`** — `char_name_option: 1` mais a lista
  com as 48 letras acentuadas (24 minúsculas, 24 maiúsculas: as cinco vogais com
  crase/agudo/circunflexo/til/trema conforme o caso, mais `ç` e `ñ`).
  **Arquivo cp1252**, e é o ponto frágil: salvo em UTF-8, cada acento vira dois
  bytes e a lista passa a permitir lixo em vez de permitir "a com til", sem erro
  nenhum. Por isso é **gerado** por `ferramentas/gera_char_guerra.py`, que
  escreve os bytes por escape `\xNN` — o gerador é ASCII puro e não há como um
  editor estragá-lo calado.
- **`rathena/conf/guerra/inter_guerra.txt`** — `default_codepage: latin1`.

Entraram só **letras**. Hífen e apóstrofo ficaram de fora de propósito: nome é
chave em comando de GM, em sussurro e na janela de troca, e símbolo ali complica
sem ganho.

O `login_athena.conf` importa o `inter_athena.conf`, então o login-server
também lê o `default_codepage` — chave que ele não conhece. Não é problema:
`login.cpp:732` manda a chave desconhecida para os parsers de conta/ipban/log e
a ignora em silêncio se ninguém a quiser. O login subiu normal.

Config de servidor só é lida na inicialização: os quatro servidores foram
reiniciados. **`@reloadbattleconf` não pega nada disto.**

### Confirmado em jogo, no mesmo dia

O dono criou o personagem com acento na tela de criação. Nada ficou pendente.

Guardado aqui porque as duas metades falham com sintomas **diferentes**, e
saber qual apareceu é o que economiza a próxima apuração:

| Sintoma | Metade que falhou |
|---|---|
| *"Character Creation is denied."* | o filtro — `conf/guerra/char_guerra.txt` não foi lido, ou foi salvo em UTF-8 |
| outro erro, ou o personagem não aparece na lista | o banco — `default_codepage: latin1` não chegou (`conf/guerra/inter_guerra.txt`) |
| caractere errado no lugar do acento | cp1252 x latin1 — só possível com um byte da faixa `0x80-0x9F` na lista |

E o que decide sem depender do que a tela desenha é
`SELECT name, HEX(name) FROM \`char\`` — leitura e gravação passam por
codificações diferentes, então ver o nome certo ao criar não prova que ele
volta certo depois de sair e entrar.

### O que esta rodada acrescenta ao método

**Mensagem de erro que serve para três causas diferentes não é ponto de
partida.** *"Character Creation is denied."* é o texto do refuse code, e o
refuse code é o mesmo para nome duplicado, nome curto e byte proibido. Duas
consultas ao código custaram menos do que uma rodada de tentativa e erro no
cliente teria custado.

**Correção de encoding raramente tem uma metade só.** O filtro estava na cara —
o codepage do banco não estava, e teria devolvido o mesmo pedido com outro
sintoma. O que fechou a questão foi medir o `INSERT` nas duas codificações
**antes** de escrever qualquer arquivo: uma rodada de mysql.exe transformou uma
suposição plausível em fato.

## O Centro da Ordem — auction_01 vira uma casa da cidade (2026-08-10)

Pedido: uma conexão nova entre Prontera e uma casa. `auction_01` tinha portal
de saída e **nenhum de entrada**; passa a ser um salão de Prontera, alcançável
por um portal na praça.

- `prontera 165,168` (raio 1, um 3x3) → `auction_01 180,52`
- `auction_01 180,49` (raio 1) → `prontera 162,168`

O salão entra **vazio**: esta rodada abriu a porta e limpou o que havia
dentro. O conteúdo vem depois.

Tudo mora em `npc/guerra/centro_da_ordem.txt`, mais uma linha no
`scripts_guerra.conf` e duas linhas retiradas da Teletransportadora.

### É a segunda vez que um salão de leilão é reaproveitado

A primeira foi `auction_02`, que virou a Ordem dos Exploradores em 2026-08-08.
A receita é a mesma, e pelos mesmos dois motivos: **o mapa já existe** no
`data.grf` deste cliente (nenhum mapa novo, nenhum risco da armadilha do
`CLAUDE.md` §4.6) e **o leilão está desligado** no servidor
(`feature.auction: off`), o que faz dos quatro salões espaço morto.

A diferença é a porta. O `auction_02` já tinha uma — o portal de Lighthalzen,
que só precisou ser repontado para Alberta. A metade de `auction_01` que
usamos **só tinha saída**: quem entrava vinha do `Auction Hall Guide` das
Ruínas de Morroc. A entrada de Prontera é nova.

### As quatro portas, e por que três tinham de morrer

O que custou raciocínio nesta rodada não foi abrir o portal — foi **contar
quantas outras portas existiam**. Eram quatro, e três não estavam no arquivo
do leilão:

| Porta | Onde | Ia parar em |
|---|---|---|
| `Auction Hall Guide#moc` | `moc_ruins 78,173` | `auction_01 179,53` — **dentro do nosso salão** |
| `Auction Hall Guide#prt` | `prontera 218,120` | `auction_01 21,43` — o bloco oeste |
| warp `auction_entrance_moc` | `auction_01 180,49` | Ruínas de Morroc |
| **`"Auction Hall"` do Teletransportador** | menu de Áreas Especiais | `auction_01 22,68` — o bloco oeste |

A quarta é a que não aparece em busca nenhuma por `npc/other/auction.txt`: ela
mora em `npc/guerra/teletransportadora.txt`, que é **cópia nossa** do warper do
rAthena. Sem tirá-la, o jogador chegaria ao bloco oeste depois de o warp de
saída dele ter sido desligado — ou seja, **preso**.

### O bloco oeste fica selado, de propósito

`auction_01` são **dois blocos andáveis sem caminho a pé entre eles**: o do
leste (x164-195), que é o nosso salão, e o do oeste (x5-41), que era a metade
de Prontera do leilão. Depois desta rodada nada leva ao oeste: as duas portas
de fora estão fora do ar, o warp de saída também, e a entrada do
Teletransportador saiu.

Vira espaço morto dentro de um mapa que agora é uma casa — e fica guardado
inteiro para o dia em que quisermos um segundo cômodo. Selar foi escolha, não
descuido: com o warp `auction_entrance_prt` de pé, sobraria um portal que sai
de um lugar onde ninguém entra e desemboca na praça do guia de leilão que
também não existe mais.

### Onze `disablenpc`, todos de fora

Pela receita de sempre (`CLAUDE.md` §2): `npc/other/auction.txt` fica byte a
byte igual ao upstream. Os dois warps do mapa, as duas portas de fora com as
duas placas ao lado, e os **sete** Auction Broker — quatro no nosso salão,
três no bloco oeste.

O `centro_ordem_saida` fica na **mesma célula** do `auction_entrance_moc` desligado, e
isso funciona pelo mesmo motivo já registrado no `ordem_dos_exploradores.txt`:
o `npc_touch_areanpc` devolve cedo quando `is_invisible` (`npc.cpp:1900`) e o
laço de cima continua procurando.

As portas de **Yuno** não foram tocadas (levam a `auction_02`, outro mapa); as
de **Lighthalzen** já estavam desligadas desde 2026-08-08.

### O portal da praça passou por três raios em dois dias

**O raciocínio de partida foi este:** as outras portas do projeto usam `1,0` ou
`1,1`, mas todas ficam em porta de parede ou em corredor. Esta fica **no meio
da praça de Prontera**, com chão andável dos quatro lados, e raio grande suga
quem só está atravessando o quarteirão. Foi para uma célula só —
`npc_setcells` (`npc.cpp:4972`) com `xs=ys=0` marca exatamente uma, conferido
no código antes de usar.

**Visto no jogo, não ficou bom.** O dono pediu raio 2 e uma célula a leste, e
no mesmo pedido seguinte corrigiu para raio 1 — parou em `prontera 165,168`
com `1,1`, um 3x3 em x164-166, y167-169.

O que o raciocínio de partida errou não foi o risco — sugar quem atravessa a
praça continua sendo real —, foi **o peso relativo dos dois lados**. Uma célula
única é contornável na diagonal e difícil de acertar sem clicar em cima: a
porta que não pega é pior que a porta que pega demais, porque a primeira falha
para quem *quer* entrar. E o custo do erro não é simétrico: entrar sem querer
resolve-se com um portal de volta a três células; não conseguir entrar não se
resolve com nada.

**São 8 células de gatilho, e não 9.** O canto `166,167` é a quina de um bloco
sólido de 2x2 (x166-167, y166-167, um objeto da praça), e o `npc_setcells` pula
célula com `CELL_CHKNOPASS` — sem erro e sem aviso. Está anotado no cabeçalho
do arquivo para quem for contar as células na planta e achar que falta uma.

### O raio e a chegada são o mesmo número, e isso não estava óbvio

O raio 2 durou uma rodada, e o que o derrubou foi a **chegada da volta**.
`162,168` é a coordenada que o dono deu, e a borda oeste do portal anda com o
raio: em `0,0` era x165 e sobravam duas células de folga; em `2,2` foi a x163 e
a chegada ficou colada, com o jogador voltando para dentro ao dar um passo
para o leste. O `1,1` devolve a folga — borda em x164, a 163 livre entre os
dois.

**Cada ponto de raio come uma célula de folga, e no 3 a chegada está DENTRO do
portal** — um ciclo infinito, e desses que não dão erro nenhum: o jogador
simplesmente não consegue sair de casa. Ficou escrito no cabeçalho, porque a
próxima pessoa a mexer no raio vai olhar para o raio e não para a chegada. Se
um dia for preciso raio maior, mover a chegada para o oeste **antes**
(`160,168` anda e está livre).

### A `prontera` não está no `db/map_cache.dat`

Achado ao conferir se as duas células de Prontera são andáveis, e vale para
qualquer conferência futura de célula: **o rAthena lê três caches, em ordem** —
`db/import/map_cache.dat`, `db/re/map_cache.dat`, `db/map_cache.dat`
(`map.cpp:3922`) —, e o primeiro que tiver o mapa vence.

A `prontera` de renewal (312x392) **só existe em `db/re/`**. A grande, de 1288
mapas, não a tem: tem uma `pprontera` de mesmo tamanho, que é outra coisa. Uma
ferramenta que abra só a `db/map_cache.dat` responde *"prontera não está no
cache"* — e a resposta é do leitor, não do mapa. Subiu para `CLAUDE.md` §5.

Conferido assim: as 8 células do portal, a `162,168` e a `163,168` andam,
`auction_01 180,52` e `180,49` estão os dois no corredor de entrada (x176-183,
y48-55), e nenhum NPC ocupa nenhuma delas.

### O que se provou, e o que não

**Provado offline:** as quatro células andam e estão livres; o cabeçalho do
arquivo novo é todo comentário (a armadilha de `CLAUDE.md` §5 — uma linha ruim
mata o arquivo inteiro); os nomes dos onze alvos batem com `npc/other/auction.txt`
byte a byte, inclusive a diferença de grafia entre `auction_entrance_moc/prt` e
`auction_enterance_juno/lhz`; nenhum nome de NPC colide.

**Não provado:** nada em jogo. Falta o `@reloadscript` e a caminhada. Está no
`PENDENCIAS.md` §1k.

### Uma armadilha de encoding que quase passou

Editar `npc/guerra/teletransportadora.txt` **destruiu os 8 acentos cp1252 do
arquivo**, transformando cada um em `\xef\xbf\xbd` (U+FFFD) — exatamente o
estrago calado que o `CLAUDE.md` §5 descreve, e que já tinha acontecido no
`db/guerra/item_db.yml` em 2026-08-07. A ferramenta de edição grava UTF-8; o
arquivo é cp1252 (`"Torre do Demônio"` no menu de Instâncias).

Foi pego porque a conferência de encoding foi feita **depois de cada edição, e
não só nos arquivos criados** — e recuperado porque o `git show HEAD:` ainda
tinha os 8 bytes originais, na mesma ordem, para reinserir um a um.

**A lição, e ela é geral:** editar arquivo de NPC existente é tão perigoso
quanto gerar um novo. O arquivo criado nesta rodada saiu limpo (ASCII puro); o
que quase quebrou foi o que já estava lá. Conferir os arquivos **tocados**, não
os escritos.

## A fonte no meio do Centro da Ordem (2026-08-11)

Pedido: uma fonte no meio da sala, em `auction_01 180,72`, com o modelo dado —
`data\model\oldcastle\fountain.rsm`.

Feito, e **é mudança de cliente, não de servidor**: a fonte é um modelo 3D no
`.rsw` do mapa. Não há NPC, não há linha de script, e o `.gat` não foi tocado.
O arquivo instalado é `C:\GuerraDoEmperium\cliente\data\auction_01.rsw`, que
vence o GRF pelo `DataFolderFirst`. A receita — que é o que se versiona — é a
entrada `auction_01` do `RECEITA` em `ferramentas/edita_mapa.py`.

### O DES bloqueou, e o bRO destravou

`auction_01.rsw` está no nosso GRF com `flags=3`, e o `.gnd`/`.gat` com
`flags=5`: DES. O `grf.py` não lê nenhum dos três, e sem o `.rsw` de partida não
há o que editar. A frente visual já sabia disto de 2026-07-31 — **640 dos 910
`.rsw` estão com DES** — e a conclusão de lá era escolher mapa dentro dos 270
limpos. Aqui o mapa não era escolha: era o mapa do salão.

A saída foi a regra 3 do `CLAUDE.md`. O GRF do bRO tem os mesmos três arquivos
com `flags=1`, e abrem. O método e a prova ficaram no `CUSTOMIZACAO-VISUAL.md`;
o resumo é que **o `csize` idêntico já quase fecha** — o DES embaralha blocos de
8 bytes e não muda o comprimento do zlib — e o que fecha de verdade é comparar
o `.gat` do bRO com o `map_cache.dat` do nosso servidor, que foi gerado do nosso
`.gat`. Deu **20.000 células de 20.000**.

Isto vale muito mais que a fonte: abre os 910 mapas para a frente visual, e não
só os 270.

### O meio da sala já estava preparado para alguma coisa

Medido antes de plantar, e mudou o que eu esperava encontrar. O centro de
`auction_01` não é chão liso: é um **pedestal quadrado de 4x4 células**
(x178-181, y70-73) na altura -5, cercado por um fosso na altura 20, com
**quatro pontes** (`모로코\성_다리.rsm`) chegando nele pelos quatro lados, a 20-25
unidades do centro. E vazio — nenhum modelo a menos de 30 unidades.

`180,72` cai no meio desse pedestal. O pedido do dono acertou o centro
geométrico do salão e o centro do pedestal na mesma coordenada.

A célula é **não-andável**, e isso não é problema: modelo de cenário não precisa
de chão, e o `.gat` não muda com o override. É o oposto do caso do NPC, onde
célula bloqueada é decisão a justificar.

### Escala e rotação vieram da Gravity, não de chute

O `Modelo.novo` grava escala 1,0 e o `edita_mapa.py` sorteava a rotação. Sorteio
é bom para destroço espalhado e ruim para peça posta de propósito: **número
sorteado é número inventado**.

A calibragem barata foi varrer os 821 `.rsw` do GRF do bRO procurando o
`filename`. Cinco instâncias oficiais — `1@def02`, `1@gl_k`, `1@gl_kh`,
`2@gl_k`, `2@gl_kh` —, **todas com rotação `0,0,0`** e escala 1,0 (duas com
1,04). A rotação 0 ficou; a escala 1,0 não sobreviveu à tela (ver abaixo). O
`edita_mapa.py` ganhou dois campos opcionais na tupla de `acrescentar`, rotação
e escala, para poder dizer as duas coisas.

### A tela respondeu no mesmo dia: 1,0 ficou grande, e a escala foi para 0,57

O modelo tem **35,3 unidades de largura — 7,1 células**, medido nos dois
`.rsm` (o nosso, de 132.287 bytes, e o do bRO, de 79.463; são revisões
diferentes e a largura é a mesma). O pedestal tem **4 células**.

A 1,0 a fonte **transbordava o pedestal** e avançava sobre o fosso, parando logo
antes das quatro pontes. Havia um argumento bom para isso estar certo — raio
17,7 contra pontes a 20 parece encaixe desenhado — e ele **estava errado**: o
dono olhou e disse que ficou grande. Escala **0,57** (20 / 35,34 = 0,566), que
dá 20,1 unidades, o pedestal exato.

**A lição é sobre a calibragem por mapa oficial**, que nesta mesma rodada foi
elogiada acima por ter dado rotação e escala sem chute. Ela acertou a rotação e
**errou a escala**, e o motivo é estrutural: a Gravity usa esta fonte em pátio
de castelo de Glast Heim, onde há espaço. **Escala oficial é boa pista e não é
resposta** — quem copia a escala copia junto o tamanho do lugar de origem. A
medida que valia era a outra, a largura do `.rsm` contra o tamanho do lugar, e
ela estava na mão desde o início.

### E a segunda olhada achou meia célula de erro

Com o tamanho certo, o desalinhamento apareceu: a fonte não estava centrada no
tampo. **A causa é aritmética, não estimativa.** O `mundo()` do
`catalogo_ingame.py` devolve o **centro da célula** — `(cx - largura/2) * 5 +
2,5`. O pedestal ocupa **quatro** células (`x178-181, y70-73`), número **par**,
então o centro dele cai na **fronteira** entre a 179 e a 180: mundo `(400, 110)`.
A célula 180,72 tem centro em `(402,5, 112,5)`.

**Meia célula em cada eixo, e nenhum inteiro consegue acertar.** O pedido do dono
dizia `180,72` e estava certo em intenção — é a célula mais próxima do centro —,
mas em vão de largura par a célula mais próxima do centro nunca é o centro. A
correção foi célula **fracionária**: `179.5, 71.5`, que dá exatamente
`(400, 110)`.

Confirmado nos dois caminhos antes de instalar. Pela conta: varrendo o `.gat`
para achar o retângulo contíguo de altura -5, os limites em mundo dão
`x 390..410` e `z 100..120`, centro `(400, 110)`, e o modelo ficou com **erro
0,00 nos dois eixos**. E pelos pixels: recortando o tampo do screenshot e medindo
os quatro cantos do losango, o centro dava (365, 322) e a fonte estava em
(380, 288) — deslocada para cima e um pouco à direita, que é exatamente como
`+2,5 X` mais `+2,5 Z` se projetam nesta câmera.

**A lição é a mesma do teto de refino e do `Level:` 1-based: o erro de meia
unidade não se denuncia.** A planta ASCII do cabeçalho mostrava o pedestal
certo, a coordenada parecia o centro, e o número saiu plausível e errado. O que
o pega é conferir o centro do **vão** contra a posição do **modelo**, e é uma
linha de conta.

O que se confirmou junto, e sem custo: a **posição e a altura estavam certas**.
O dono disse "grande" e depois "torta", nunca "enterrada" nem "flutuando" — a
altura nunca esteve em questão, então a regra de plantar
na altura do `.gat` da célula, a mesma das quatro pontes, funcionou. E encolher
não tirou a peça do chão, o que prova que a origem do modelo está na base (a
caixa envolvente que eu tinha medido sugeria origem no meio, e ela estava errada
nesse eixo — o transform ignora a hierarquia de nós).

### As travas que rodaram antes de instalar

- **Round-trip do `rsw.py`**: ler e regravar o `.rsw` sem receita devolve os
  113.618 bytes **idênticos**. Sem isso, toda edição carregaria junto um estrago
  invisível.
- **Diff do gerado**: 206 -> 207 objetos, +252 bytes, que é exatamente um
  registro de modelo (248 + 4). Os **206 objetos originais preservados byte a
  byte**.
- **Os 178 `filename` conferidos contra o NOSSO GRF** — não o do bRO. Caminho
  que não resolve não dá erro em parser nenhum: aparece como um diálogo por
  modelo no cliente, e prende quem tiver personagem salvo no mapa.
- **O leitor de `.rsm` só valeu porque consumiu o arquivo inteiro.** A primeira
  versão parava nos nós e sobravam 8 bytes — `numPosKeyframes` e
  `numVolumeBoxes`, zero nos dois modelos. Sem a trava de "consumir tudo", a
  medida de largura teria saído plausível e falsa.

### O que não foi verificado

**A fonte foi vista duas vezes, e só ela.** O dono abriu o salão, reportou o
tamanho, e na segunda olhada o desalinhamento — então *aparece* e está *na
altura certa*; tamanho e centro foram corrigidos e **falta a terceira
olhada**. O
que ninguém exercitou ainda é o **portal de Prontera**, que nunca foi testado:
falta o `@reloadscript` e a caminhada de ida e volta. Está no `PENDENCIAS.md`
§1k, e o item da fonte encolheu para uma linha só — reconferir o tamanho a 0,57.

## O Centro da Ordem — conferido em jogo, e batizado (2026-08-11)

**Tudo funciona.** O dono percorreu o caminho inteiro e confirmou: o portal de
`prontera 165,168`, a chegada, a volta por `auction_01 180,49`, a limpeza dos
onze NPCs de leilão e a fonte no meio da sala. Com isso a `PENDENCIAS.md` §1k
saiu — era a lista de seis conferências abertas desde 2026-08-10.

O que a sessão de testes fechou, item a item: o `3x3` do portal pega sem sugar
quem atravessa a praça; a volta em `162,168` não devolve o jogador para dentro;
os onze `disablenpc` pegaram; o menu de Áreas Especiais da Teletransportadora
perdeu o "Auction Hall" sem deslocar as outras nove; e o bloco oeste está
selado.

### O nome veio depois do lugar estar de pé

O salão passou a se chamar **Centro da Ordem**, a pedido do dono. Não é uma
ordem nova: é a **mesma** do Emissário no navio, da Alleria em Comodo e dos
Exploradores em `auction_02`. Este é o pé dela na capital.

O arquivo virou `npc/guerra/centro_da_ordem.txt`, e com ele os identificadores
— `centro_ordem_entrada`, `centro_ordem_saida`, `#centro_ordem_montagem` e o
prefixo do `debugmes`. Os nomes de warp foram escolhidos com o prefixo
`centro_ordem_` e não `ordem_`, que já é dos Exploradores em `auction_02`.

### O nome do mapa tem duas metades, e as duas são GERADAS

O que o jogador lê não sai do nome do arquivo de NPC. São duas tabelas do
cliente — `data\mapnametable.txt` (canto do minimapa) e
`System\mapInfo_true.lub`/`_sak.lub` (o letreiro ao entrar) —, e **as duas são
geradas** por `traduz_ptbr.py` a partir do `mapInfo.lub` do bRO, onde este mapa
se chama **"Centro Comercial"**. Editar à mão volta atrás na próxima rodada,
calado. É a mesma família do `OngoingQuestInfoList` e do `CheckAttendance.lub`
— `CLAUDE.md` §9.

Por isso o nome entrou como **`NOSSOS_MAPAS`, uma tabela de override no
`traduz_ptbr.py`**, aplicada no fim do `_mapas_do_bro()` — que é o **único ponto
por onde as duas metades passam**. Uma entrada conserta as duas, e o
`traduz_ptbr.py mapas mapinfo` passa a ser idempotente com o nosso nome.

**O `auction_02` não precisou de entrada nenhuma**, e a descoberta explica uma
escolha antiga: o bRO **já** chama aquele mapa de "Ordem dos Exploradores". A
sessão de 2026-08-08 não rebatizou nada — pegou o mapa que já tinha o nome
certo. Só entra no `NOSSOS_MAPAS` mapa que **mudou de função** aqui.

### Um detalhe que a tabela quase escondeu

A primeira versão do override trazia `displayName`, `mainTitle` e `subTitle`.
Os dois últimos seriam **inertes**: o bloco deste mapa no `mapInfo_*.lub` tem
só `displayName`, e o `parte_mapinfo` **troca** campo existente, não acrescenta.
Ficariam na tabela parecendo configuração e sem efeito nenhum — pior que
ausentes. Ficou só o `displayName`, com o porquê escrito ao lado.

O que provou que a remoção era inerte foi rodar `--verificar` depois dela:
*"nada mudou (já estava aplicado)"* nos três arquivos. E o que provou que o
override não arrastou nada junto foi o `--verificar` de antes: **−1 byte** em
cada arquivo, que é exatamente `Centro Comercial` (16) → `Centro da Ordem` (15).

## A escrivaninha na ala leste do Centro da Ordem (2026-08-11)

Pedido: uma mesa escrivaninha em `auction_01 191,72`, com o modelo dado —
`data\model\prontera_re\desk_h_02.rsm`.

Feito, e é a mesma natureza da fonte: **mudança de cliente, não de servidor**.
Nenhum NPC, nenhuma linha de script, o `.gat` intocado. O arquivo instalado é
`C:\GuerraDoEmperium\cliente\data\auction_01.rsw` (114.122 bytes, 208 objetos),
que vence o GRF pelo `DataFolderFirst`; o que se versiona é a receita, a entrada
`auction_01` do `RECEITA` em `ferramentas/edita_mapa.py`, que hoje tem as duas
peças — a fonte e a mesa. **Cliente novo perde as duas, calado.**

### O tapete não estava no `.gat` nem no id de textura — é UV

Esta foi a descoberta que mudou a coordenada, e o caminho até ela foi errado
duas vezes antes de acertar.

`191,72` cai numa ala leste que o `.gat` descreve como oito células andáveis de
largura (x188-195), todas na altura 4,0, sem degrau, sem plataforma, sem nada
que marque um lugar. Pelo `.gat`, plantar em `191,72` seria plantar em chão
liso, e a lição de meia célula da fonte — que nasceu de um **pedestal** de 4x4
— não teria onde se aplicar.

O `.gnd` também disse que não havia nada: **as 8x8 células da ala inteira usam a
mesma textura**, a de índice 3 (`모로코내부\모로코성-바닥3.bmp`), do começo ao fim
do corredor. Mapear id de textura por tile devolve um bloco uniforme.

O que existe, e o print mostrava desde o começo, são **três tapetes**. Eles são
**outra região do mesmo `.bmp`**, escolhida pelas coordenadas **UV** de cada
superfície — o `.bmp` é um atlas. Lendo os 8 floats de UV por superfície em vez
do id de textura, o desenho aparece na hora: três tapetes de **8x8 células** em
`x188-195`, nos `y60-67`, `y68-75` e `y76-83`. Os de fora têm sofá; o do meio
estava vazio, e é nele que `191,72` cai.

### E aí a correção de meia célula voltou, pelo mesmo motivo

Tapete de **oito** células de lado é vão de largura **par**: o centro cai na
fronteira, em mundo `(460, 110)`, e as quatro células centrais são
`191/192 x 71/72`. Qualquer uma das quatro erra o centro por meia célula em
cada eixo — que é exatamente o que aconteceu com a fonte, e é a mesma distância.

`191,72` é uma das quatro, e é onde o personagem estava parado no print. A
intenção estava certa; o número, não. A mesa entrou em **`191.5, 71.5`**, com
erro medido de **0,00 nos dois eixos** contra o centro do tapete.

**A diferença que vale guardar em relação à fonte:** lá o vão era o pedestal,
visível no `.gat` como um platô de altura −5, e bastou varrer alturas para
achá-lo. Aqui o vão é **invisível para quem olha o `.gat`** (chão liso e
andável nas oito células) **e para quem olha o id de textura do `.gnd`** (uma
textura só). Só o UV o mostra. Subiu para o `CLAUDE.md` §5.

### Rotação 90, e desta vez quem decidiu foi a sala

Os três usos oficiais do modelo no GRF do bRO — dois em `1@gol1`, um em
`brz_gld` — dão rotação **90, 180 e 270**, e dois deles ainda vêm espelhados em
X (`escala.x = -1,0`). Ou seja: a varredura que resolveu a rotação da fonte
**não resolve nada aqui**, porque o modelo não é radial e a Gravity usou os
quatro lados.

Quem decidiu foi `auction_01`: os **quatro sofás** do mapa (`x165` e `x194`,
`y64` e `y80`) estão **todos em rotação 90**, e 90 põe o lado longo do modelo ao
longo do corredor, em vez de atravessá-lo. É o número menos inventado que havia
— mas é escolha, não medida, e está anotada como tal na receita: **é o campo
para mexer se o dono quiser outra cara.**

### Escala 1,0, e desta vez a oficial serviu

Medido com o mesmo leitor de `.rsm` da fonte: **20,02 x 13,84 unidades**
(4,0 x 2,8 células), 11,18 de altura. Num tapete de 8x8 células isso ocupa
**metade da largura** — proporção boa, e a mesma conta que derrubou a fonte de
1,0 para 0,57 aprova o 1,0 aqui.

O leitor precisou de um ajuste para dar esse número. O `mede_rsm.py` junta
todos os nós numa caixa só, e este modelo tem **quatro** (`desk_02`, `book_02`,
`ink_01`, `Object052`): ignorando a hierarquia, o `pos` do nó raiz
(`x = -129,35`) entra na conta como se fosse dimensão e a caixa sai com
**148,90 de largura — 29,8 células**, número plausível o bastante para alguém
concluir "não cabe" e trocar de modelo. Medir **nó a nó** desfaz o engano em
uma rodada. A trava de consumir o arquivo inteiro continuou valendo: 0 bytes
sobrando.

### As texturas do `.rsm` foram conferidas à parte

O `edita_mapa.py` confere o caminho de todo `.rsm` contra a tabela do nosso GRF
e **para aí**. Um `.rsm` que resolve com textura que não resolve não dá erro em
parser nenhum — dá superfície quebrada na tela. Como o modelo vem de
`prontera_re`, pasta que nada nosso usava até agora, as três
(`prontera_re\prt_h_14.bmp`, `prontera\prt_h_09.bmp`,
`prontera_re\prt_h_13.bmp`) foram conferidas uma a uma: as três estão no nosso
`data.grf`.

### As travas que rodaram antes de instalar

- **Round-trip do `rsw.py` na entrada**: os 113.618 bytes do `.rsw` original
  (o do GRF do bRO, sem DES) voltam **idênticos**.
- **Diff contra o override que já estava instalado**, o da fonte: 207 → 208
  objetos, **+252 bytes**, que é exatamente um registro de modelo (248 + 4). Os
  **178 modelos anteriores preservados campo a campo** — `filename`, posição,
  rotação e escala.
- **A saída reabre** e a quadtree fecha no byte exato.
- **Os 179 `filename` conferidos contra o NOSSO GRF**: todos resolvem.
- **Altura**: `.gat` em `191,71` = 4,0, e o modelo gravado em `y = 4,00`.

O arquivo anterior foi para
`C:\GuerraDoEmperium\backup-registro\auction_01.rsw.20260811-015345` antes da
gravação.

### Conferida em tela no mesmo dia, de primeira

O dono olhou e disse *"o resto tá perfeito"*: posição, tamanho e **rotação**
passaram sem correção. Vale registrar porque a fonte, duas seções acima,
precisou de **duas** rodadas depois de passar nas mesmas travas offline — e
porque a rotação era a única escolha desta rodada **sem número por trás**,
tirada dos quatro sofás da sala. Desta vez o palpite estruturado bastou.

### O que faltava era o chão, e ele é a outra metade

Modelo plantado no `.rsw` **não bloqueia passagem**: o override de mapa não
toca o `.gat`, então o jogador atravessa a mesa. O bloqueio veio a pedido do
dono, com as **cinco células que ele mediu andando em cima do móvel**:
`191,70`, `191,71`, `191,72`, `191,73` e `192,73`.

Elas foram fechadas no `OnInit` do `#centro_ordem_montagem`
(`npc/guerra/centro_da_ordem.txt`), e com isso o móvel passou a viver em **dois
lugares** — o desenho no cliente, o bloqueio no servidor. O acoplamento subiu
para o `ARQUITETURA.md` §4.

**`setwall` e não `setcell`.** Os dois fecham a célula no servidor; só o
`setwall` avisa o cliente (`clif_changemapcell`, `map.cpp:3509`), e o
`map_iwall_get` reenvia para quem entra no mapa depois (`clif.cpp:11098`). Com
`setcell` o cliente continuaria achando que dá para andar ali — o próprio
`doc/script_commands.txt` do rAthena avisa que isso *"may cause movement
problems"*. Virou regra no `CLAUDE.md` §4.15.

**Uma parede por célula, e não uma de tamanho 4 mais uma de 1.** O
`map_iwall_set` para na primeira célula já bloqueada e grava
`iwall->size = i` sem reclamar (`map.cpp:3503`): parede mais curta que a
pedida, **calada**, e o `checkwall` depois ainda responde que ela existe. Com
tamanho 1 não há o que truncar. O bloco confere as cinco com
`checkcell(..., CELL_CHKNOPASS)` e grita por `debugmes` se alguma continuar
andável — armadilha no `CLAUDE.md` §5.

**`delwall` antes de cada `setwall`, pela idempotência.** O `setwall` recusa
nome que já existe e devolve falha **calada**, então sem isso o segundo
`@reloadscript` não faria nada. O `delwall` tem seu próprio senão, anotado no
código: ele devolve a célula para andável+atirável **sem consultar o mapa
original** (`map.cpp:3553`) — inofensivo aqui, porque as cinco são chão andável
de verdade, e perigoso em célula que já nascesse bloqueada.

**`shootable` fica `true`**: fecha o andar e não a linha de tiro, que é o que
uma mesa faz — e não há combate no salão.

### As cinco células não são a pegada do modelo, e a diferença é visível

A mesa mede 4,0 x 2,8 células e cobre **`x191-192` em `y70-73`** — oito
células, com sobras de meia célula em `x190` e `x193`. A lista do dono é essa
menos três: **faltam `192,70`, `192,71` e `192,72`**, e dá para entrar na
metade leste do tampo.

Entregue como pedido, com a divergência escrita no comentário do bloco e dita
na entrega — a mesma conduta da Máscara de Minorous (`CLAUDE.md` §4.14):
diferença entre o pedido e a medida é para levantar, não para resolver
sozinho. Acrescentar os três é pôr os pares no `setarray`.

### O que falta ver

O bloqueio ainda **não foi exercitado** — falta o `@reloadscript` e andar em
volta da mesa. Está no `PENDENCIAS.md` §1.

## Os oito guardas do Centro da Ordem (2026-08-11)

O salão estava de pé e **vazio de NPC** desde 2026-08-10 — portal, fonte e
escrivaninha, e mais nada. Os primeiros habitantes vieram a pedido do dono, que
mandou a lista pronta: oito `Guarda`, sprite 966, com **posição, célula que cada
um olha e fala**, um por um. Moram em `npc/guerra/guardas_do_centro.txt`, arquivo
novo — o `centro_da_ordem.txt` continua sendo só a porta e a limpeza do leilão.

São quatro pares simétricos: a boca do corredor de chegada (`175,56` e `184,56`,
virados um para o outro), o meio do salão (`175,80` e `184,80`), a parede norte
(`171,86` e `188,86`) e os cantos do fundo (`165,87` e `194,87`). Nenhum faz
nada além de falar.

### O facing veio como célula alvo, não como ponto cardeal

O pedido dizia *"virado para 176,56"*, e a conversão sai do `dirx`/`diry`
(`src/map/unit.cpp:70`), a tabela que o `enum directions` de
`src/map/path.hpp:16` indexa. Ela anda **anti-horária** a partir do norte —
`0` N, `1` NO, `2` O, `3` SO, `4` S, `5` SE, `6` L, `7` NE —, e ler como se
fosse a ordem intuitiva (N, NE, L, SE…) erra por dois em quase todo mundo.
Daí os quatro valores usados: `6` para uma célula a leste, `2` para uma a
oeste, `4` para uma ao sul.

Isso é o ponto cardeal no mapa, e **não** é o que se vê na tela: com a câmera
padrão deste cliente as direções caem na diagonal (a tabela medida está no
`maquina.txt`, seção Notas). Aqui não atrapalha, porque o que o pedido fixou
foi a célula.

### As dezesseis células, conferidas antes de escrever

As oito dos guardas e as oito que eles olham foram lidas no `map_cache` — as
dezesseis andam. O `auction_01` está no `db/map_cache.dat`, o grande: **não**
está no `db/import/` nem no `db/re/`, então a armadilha dos três caches
(`CLAUDE.md` §5, a da `prontera`) não alcança este mapa. Nenhuma colide com
NPC: os quatro `Auction Broker` do salão ficavam em `177/182 × 68/75` e estão
desligados pelo `centro_da_ordem.txt`.

### Duas ressalvas levantadas na entrega

A fala de `184,80` diz **"Crânios Humanos"**, e o item que existe no servidor é
a **Caveira Humana** (30995, o troféu de PvP do `honra_de_combate.txt`).
Gravado como o dono escreveu, com a divergência no cabeçalho do arquivo e dita
na entrega — mesma conduta da Máscara de Minorous (`CLAUDE.md` §4.14). Quem
procurar "Crânio" no inventário não acha nada.

A fala de `171,86` veio com *"ganahndo"* e foi gravada **"ganhando"**: erro de
digitação, não gíria.

E a **Face-Sombria**, na fala de `188,86`, é a primeira aparição desse nome em
todo o servidor — não há item, NPC, mapa nem missão com ele. Nasce como boato
de guarda; quem for dar corpo a ela depois tem aquela linha como fonte da
grafia.

### O de sempre, que quase custou de novo

Os oito se chamam `Guarda` na tela e têm sufixo `#co_*` no nome único — nome
único repetido faz o segundo **não nascer**, calado. Os dois do fundo dizem a
mesma coisa, e o segundo é `duplicate` do primeiro.

E o arquivo saiu do editor **em UTF-8**, com os nove acentos já convertidos em
`U+FFFD` — a armadilha do `CLAUDE.md` §5, exatamente como descrita: escrever é
o passo perigoso, e o estrago é irreversível no próprio byte. Foram repostos
por escape (`í` e irmãos) e o arquivo regravado em cp1252, com a releitura
como prova. Vale como lembrete de que a conversão não é opcional nem
ocasional — é todo arquivo de NPC, toda vez.

### O que falta ver

Os oito ainda **não foram vistos em jogo**: falta o `@reloadscript` e olhar se
cada um está virado para onde o dono pediu. Está no `PENDENCIAS.md` §1.

## O Egebreu, e a Caveira Humana ganha destino (2026-08-11)

`npc/guerra/comprador_de_caveiras.txt`. Um NPC em `auction_01 192,72`, virado
para `191,72`, sprite **404** (`4_M_UNCLEKNIGHT`): compra Caveira Humana (30995)
e paga em Moeda Nova (30998), **1 por 1**, levando todas as da bolsa de uma vez.
A célula, o sprite, o nome e a fala inteira vieram do dono.

**Isso fecha a `PENDENCIAS.md` §4b, que estava aberta desde 2026-08-08.** A
metade de baixo daquela pendência — a caveira *caindo* do jogador morto na arena
— tinha sido feita no mesmo dia, pelo `OnPCKillEvent` do
`npc/guerra/honra_de_combate.txt`. O que faltava era o outro lado: o item entrava
no inventário e **não saía de lugar nenhum**, embora a descrição da própria Moeda
Nova (posta pelo `instala_item.py`) já listasse *"em troca de Caveira Humana"*
como uma das fontes de moeda. A promessa era mais velha que o NPC.

### É a terceira fonte de Moeda Nova, e a primeira que paga por PvP

| fonte | onde | quanto |
|---|---|---|
| Logue e Ganhe | `db/guerra/attendance.yml`, sem NPC | 240 por conta/mês, de graça |
| Alleria | `comodo 221,182` | 1 por Flor Visionária |
| **Egebreu** | `auction_01 192,72` | **1 por Caveira Humana** |

As duas de cima são presença e PvE. Esta só enche com jogador matando jogador
na arena — e com as três condições do `honra_de_combate.txt` cumpridas (os dois
lados em nível 200, o morto com 1 ponto de Honra ou mais, e a morte passando
pelo anti-colusão do `.Limite`).

**Não abre torneira nova, e vale dizer por quê:** quem limita quantas caveiras
nascem é o `honra_de_combate.txt`, não este NPC. O Egebreu só dá destino às que
já nasceram. Se um dia a Moeda inflacionar por este caminho, o número a mexer é
o `.preco` do `OnInit` **ou** o anti-colusão de lá — não os dois de uma vez.

### Diálogo, e não loja de troca — a regra §4.10 não se aplica aqui

A pendência §4b dizia, com razão, *"quando for escrito, é `barter` e não
`itemshop`"* — a caveira é `NoSell`, e o `itemshop` passa a moeda pelo
`pc_can_sell_item`, que recusa item `NoSell`. Continua verdade, e **não alcança
este NPC**: o pedido não é janela de loja nenhuma, é caixa de diálogo com
Sim/Não. O pagamento é `getitem` e a cobrança é `delitem`, e nenhum dos dois
passa por checagem de venda. As travas dos dois itens (a caveira `NoSell`, a
moeda `NoTrade`/`NoDrop`/`NoSell`) não atrapalham em nada.

É a mesma forma da Alleria, e de quebra poupa a outra metade que loja de troca
sempre tem: numa janela de barter o nome do item vem do `itemInfo.lua` do
**cliente** (`CLAUDE.md` §4.9); numa caixa de `mes` o texto é nosso.

E o `getitem` **não pode largar a moeda no chão** aqui, que é a armadilha de
sempre: com a mochila cheia o `buildin_getitem` cai num `map_addflooritem`, mas
a Moeda Nova é `NoDrop` e o `pc_candrop` recusa — a moeda se perde e o cliente
avisa. O `delitem` vir antes torna o caso quase impossível de todo jeito: o slot
da caveira acabou de vagar. Sem `checkweight`, e desta vez por um motivo novo:
**os dois itens pesam 0**, então a pergunta não teria resposta possível. (Na
Alleria não há `checkweight` por outro motivo — lá a flor pesa 10 e a troca
*alivia* a bolsa.)

### A célula é a da escrivaninha, e isso amarra as duas coisas

`192,72` é a quina sudeste da pegada da escrivaninha (`x191-192` em `y70-73`),
plantada no `.rsw` cinco dias antes. Ele atende de trás da mesa.

Isso só foi possível porque **das oito células da pegada, só cinco estão
fechadas** por `setwall` no `centro_da_ordem.txt` (`191,70-73` e `192,73`). As
três de fora — `192,70`, `192,71` e `192,72` — são a metade leste do tampo, e
estão registradas na `PENDENCIAS.md` §1 como possíveis de fechar.

**Fechar as três deixou de ser gratuito:** o Egebreu ficaria em célula
bloqueada. Ele continuaria clicável — NPC não precisa de chão andável para ser
falado —, mas ninguém mais encostaria nele, e **a mudança não dá erro nenhum**.
A saída está escrita nos dois lugares: ou `192,72` fica de fora do `setarray`,
ou o Egebreu vai para `193,72`, que anda, está livre e é uma célula a leste,
com o mesmo facing.

### O sprite 404, e as três tabelas

Estreia do `4_M_UNCLEKNIGHT` no servidor, então valeram as duas conferências de
sempre — e uma terceira, que resolveu o número:

| onde | o que diz |
|---|---|
| `npcidentity.lub` do **nosso** cliente | `jobtbl[404] = JT_4_M_UNCLEKNIGHT` |
| `src/map/npc.hpp` do rAthena | `JT_4_M_UNCLEKNIGHT = 404` (`NPC_RANGE2_START = 400`, e ele é o quarto depois) |
| `data.grf` | `data\sprite\npc\4_M_UNCLEKNIGHT.spr` e `.act`, os dois presentes |

O nome do arquivo de sprite **não foi chutado**: sai do `JobNameTable` do
`jobname.lub` do próprio cliente, indexado pela constante do `npcidentity` — que
é exatamente como o cliente resolve. Vale registrar o caminho, porque é reusável:
`ptbr.tabelas()` lê os dois `.lub` (são bytecode no GRF), e as chaves do
`JobNameTable` vêm como `Sym('jobtbl.JT_*')`, não como número.

Uma nota para quem for contar à mão no `npc.hpp`: `NPC_RANGE2_START = 400` **é**
o valor 400, então o primeiro nome depois dela é 401. Ler como se a lista
começasse em 400 erra por um a faixa inteira — e erraria aqui, dando
`4_F_VALKYRIE2`.

Facing **2** (oeste), de `192,72` para `191,72` — `x-1`, pela tabela do
`dirx`/`diry` (`unit.cpp:70`), que anda anti-horária a partir do norte.

### As palavras são do dono, inclusive as duas divergências

A fala foi gravada como veio. Duas coisas nela não batem com o servidor, e
ficaram registradas em vez de consertadas por conta própria — mesma conduta da
Máscara de Minorous (`CLAUDE.md` §4.14) e do "Crânios Humanos" do guarda de
`184,80`, dois dias antes:

1. **"Arena de Prontera"** na primeira caixa e **"Arena de Combate"** na terceira
   são o mesmo lugar, chamado de dois jeitos na mesma conversa. O que existe no
   servidor é a **Arena de Combate** (`prontera 154,187`,
   `npc/guerra/arena_de_combate.txt`, que leva a `pvp_n_1-5`). Não há nada
   chamado "Arena de Prontera" — embora ela *fique* em Prontera, então a frase
   não mente, só não é o nome.
2. **"24/7"** é a única expressão de fora do mundo do jogo em todo o diálogo do
   servidor. Foi pedida assim.

As duas se consertam trocando uma palavra na linha, se o dono quiser.

### Conferido em jogo no mesmo dia, de primeira

O dono deu `@reloadscript`, falou com ele e trocou — a linha
*"Você obteve Moeda Nova (4)"* no log do cliente é a troca de quatro caveiras
acontecendo. Passaram sem correção o sprite **404** (estreia do
`4_M_UNCLEKNIGHT` no servidor), o enquadramento dele em cima da escrivaninha, a
troca e a acentuação.

Vale registrar que a estreia de sprite passou de primeira **porque as três
tabelas foram conferidas antes** (`npcidentity.lub` do cliente, `npc.hpp` do
rAthena e os `.spr`/`.act` do GRF), e que o nome do arquivo de arte saiu do
`JobNameTable` do próprio cliente em vez de ser deduzido do nome da constante.

**O que ele não faz, e é de propósito:** as células dele continuam sendo as três
da metade leste do tampo que o `setwall` da mesa não fecha. Fechar as três agora
custa mexer nele — está anotado no `PENDENCIAS.md` §1 e no cabeçalho do
arquivo.

## O sofá da alcova norte do Centro da Ordem (2026-08-11)

`data\model\prontera\sofa_01.rsm` plantado em `auction_01`, célula
**179.5, 84.0**, rotação **0**, escala **1,0**. Terceira peça de cenário do
salão, depois da fonte e da escrivaninha, e a primeira em que **rotação foi
medida em vez de escolhida**.

O pedido do dono trouxe as três coisas que decidem: o par de células
(`179,84` e `180,84`), o eixo ("como são dois lugares, ideal que fique entre")
e o lado ("virado para frente, para `180,83`").

### A meia célula veio junto com o pedido, desta vez

Terceira vez que a coordenada é fracionária, e a primeira em que ninguém
precisou descobrir isso depois: o dono pediu **duas** células, e o centro de um
vão de largura 2 cai na fronteira entre elas. Mundo (400,0, 172,5).

O `84.0` fica inteiro de propósito — em `y` o vão é de uma célula só, e aí o
centro da célula É o centro do vão.

E `179.5` não é só aritmética: é **o eixo que a alcova já tinha**. As três
cortinas (`커텐01`) do fundo estão em `x175.4`, **`179.4`** e `183.4`; a renda
de cima (`침대레이스2-1`) em `176.0`, **`179.5`** e `182.9`; o forro de teto
(`천정틀`) em **`179.5`**, `86.5`. O sofá entrou no eixo da sala, não num
número nosso.

### O eixo vertical do `.rsm` é o Z, e errar isso troca profundidade por altura

Esta é a descoberta da rodada, e ela **muda a leitura de toda medida de modelo
feita até aqui**. A prova não é teórica — são os próprios modelos deste salão:

| modelo | X | Y | Z |
|---|---|---|---|
| `내부소품\기둥2` (coluna) | 6,34 | 6,34 | **30,21** |
| `모로코\동상` (estátua) | 8,57 | 5,43 | **29,25** |
| `내부소품\몽크난간02` (balaustrada) | 4,00 | 4,00 | **10,47** |

Coluna, estátua e balaustrada são **altas e finas**. O eixo de 30 é o vertical.
Logo **X = largura, Y = profundidade, Z = altura**, e a *planta* de um móvel é
X × Y.

Isso reconcilia a medida já publicada da escrivaninha ("20,02 × 13,84 unidades,
4,0 × 2,8 células"): aquilo era X × **Y**, e estava certo. Quem repetir a
medição lendo X × Z acha 3,9 × 1,5 células para a mesma mesa — número plausível
e errado, na direção que faz um móvel parecer caber onde não cabe.

Com o eixo certo, o sofá mede **27,71 × 11,27 unidades = 5,54 × 2,25 células**,
com 17,60 de altura (3,52 células). Lido pelo eixo errado ele daria 5,5 × 3,5 —
55% mais fundo do que é.

### A rotação, em três passos, e nenhum deles é palpite

A da escrivaninha ficou registrada como *"escolha, não medida"*. Esta não:

1. **Qual eixo é a altura** — o Z, pela tabela acima.
2. **De que lado do Y está o encosto** — o **+Y**, nos dois sofás do salão. É o
   lado onde o modelo é alto: no `sofa_01`, `Z` chega a 17,60 na faixa
   `Y 4,13..7,89` e não passa de 9,18 do outro lado, que é o assento com os
   braços.
3. **Para onde aponta o +Y em cada rotação** — calibrado nos **quatro sofás que
   o mapa já tinha** (`리히타르젠\소파02`, em `x164,9` e `x193,9`). Os quatro
   estão em rotação **90**, e o que separa o par leste do oeste é o **sinal da
   terceira escala**: `+1,50` contra `-1,50`, que espelha a profundidade. O par
   leste encosta na parede leste, então **em rot 90 o +Y aponta para +X**.

Os **22 usos oficiais** do `sofa_01` em `prt_cas` e `prt_cas_q` fecham a conta
pelo outro lado: todas as instâncias de rotação **270** têm parede colada a
oeste — encosto a oeste, ou seja `+Y → -X`. Bate com o passo 3, 180 graus
adiante.

Daí a regra, que vale para qualquer móvel: **+Y → (sen θ, cos θ) em (X, Z)**.
Em **rotação 0 o encosto aponta para +Z, que é o norte** — o sofá olha para o
sul, para `180,83`, que foi o pedido.

**E rot 0/180 põem a LARGURA no eixo leste-oeste; 90/270 a põem no norte-sul.**
Não é o contrário, e confundir poria o sofá atravessado na alcova. As quatro
pontes do fosso confirmam de graça: `모로코\성_다리` tem 58,97 de comprimento em
X, e as duas de rotação 90 estão nos corredores **norte-sul** de `x175` e
`x184`, enquanto as de 180 estão nos vãos **leste-oeste** de `y67` e `y76`.

### Escala 1,0 — a oficial serve, e a sala concorda

Os 22 usos no castelo de Prontera vão de **0,80 a 1,00**, com 1,00 o mais
comum. Isso já é mais forte que de costume: `prt_cas` é salão de castelo, não
pátio aberto, então o lugar de origem tem o tamanho do nosso — que é a ressalva
que derrubou a fonte de 1,0 para 0,57.

A conta confirma: 5,54 × 2,25 células numa alcova de ~9 células (entre as
colunas de arco de `x174,9` e `x184,0`) deixa 1,7 célula de folga de cada lado.
Em profundidade o sofá vai de `y82,9` a `y85,1`, parando antes da renda de
`y85,6`.

### A ferramenta que faltava virou `ferramentas/mede_rsm.py`

O leitor de `.rsm` das rodadas anteriores era de rascunho e não sobreviveu.
Agora está versionado, com as três coisas que custaram caro embutidas: a trava
dos **0 bytes sobrando** (o `sofa_01` sobra exatamente 8 sem o rabicho de
quadros/volumes depois dos nós, e um leitor desalinhado devolve números como se
nada fosse), a medição **nó a nó**, e os rótulos de eixo certos.

Ele ganhou também a conferência que o `edita_mapa.py` não faz: as **texturas**.
As três do sofá (`prontera\prt_h_04.BMP`, `prt_h_05.bmp`, `prt_h_01.bmp`)
resolvem no nosso GRF. Textura que falta não dá erro em parser nenhum — dá
superfície quebrada na tela.

### As travas antes de instalar

- **Round-trip do `rsw.py` na entrada**: os 113.618 bytes do `.rsw` do GRF do
  bRO voltam **idênticos**.
- **Diff contra o override instalado**: 208 → 209 objetos, **+252 bytes** —
  exatamente um registro de modelo (248 + 4), o mesmo delta da escrivaninha. Os
  **179 modelos anteriores preservados campo a campo e na mesma ordem**.
- **A saída reabre** e a quadtree fecha no byte exato; os 180 `filename`
  resolvem no NOSSO GRF.
- **Altura**: `.gat` em `179,84` e `180,84` = 4,00, e o modelo gravado em
  `y = 4,00`.

O arquivo anterior foi para
`C:\GuerraDoEmperium\backup-registro\auction_01.rsw.20260811-025907`.

### O que falta ver, e o que ele não faz

Falta a tela. **Não precisa de `@reloadscript`** — não há script nenhum nesta
rodada; o que precisa é o cliente **reler o mapa**, ou seja sair e voltar ao
salão (reabrir o cliente é a garantia).

E ele **não bloqueia passagem**, como todo modelo de `.rsw`: as células do sofá
(`x177-182` em `y83-85`) continuam andáveis e dá para atravessar o móvel. Foi
entregue assim porque o pedido foi de cenário, não de colisão — fechar é um
`setwall` no `centro_da_ordem.txt`, do mesmo jeito que a escrivaninha.

## As duas estátuas dos plintos do sul do Centro da Ordem (2026-08-11)

`data\model\prontera\prn_statue_03.rsm` em `auction_01` **182.5, 68.5**,
rotação **90**, escala **1,0**; `prn_statue_08.rsm` em **176.5, 68.5**, rotação
**0**, escala **1,0**. Quarta e quinta peças de cenário do salão, depois da
fonte, da escrivaninha e do sofá.

Pedido do dono: a `_03` em `183,69` *"virada pra esquerda"*, a `_08` em
`177,69` *"virada pra frente (177 67 por exemplo)"*, e *"se tiver que ajustar o
tamanho, ajusta a escala pra estátua ficar bem encaixada na base disponível, no
centro"*.

Mudança de cliente, não de servidor: nenhum NPC, nenhuma linha de script, o
`.gat` intocado. O que se versiona é a receita — a entrada `auction_01` do
`RECEITA` em `ferramentas/edita_mapa.py`, que hoje tem as cinco peças.
**Cliente novo perde as cinco, calado.**

### O vão estava à vista, desta vez — e é degrau no `.gat`

Depois do pedestal da fonte (platô no `.gat`) e do tapete da escrivaninha (só
o UV mostrava), este foi o caso fácil: varrer a altura média em volta do fosso
mostra **quatro blocos de 2×2 células na altura 0,0**, contra 4,0 do piso — e
no `.gat` o negativo é para **cima**, então 0,0 está 4 unidades *acima* do
chão. São `x176-177` e `x182-183`, nos `y68-69` (sul) e `y74-75` (norte),
quatro plintos de canto em volta do pedestal central (que está em −5,0) e do
fosso (15/20). Os quatro estavam vazios: a varredura de modelos em
`x172-188, y62-80` devolve só as quatro pontes.

`183,69` e `177,69` são a célula de canto de cada plinto sul, a mais perto do
meio do salão.

### Quarta meia célula seguida, e o motivo não muda

Plinto de **duas** células de lado é vão de largura **par**: o centro cai na
fronteira. Centrar em `183,69` ou `177,69` erraria meia célula nos dois eixos.
As peças entraram em **`182.5, 68.5`** e **`176.5, 68.5`** — mundo
`(415,0, 95,0)` e `(385,0, 95,0)`, com erro medido de **0,00 nos dois eixos**
contra o centro geométrico, e simétricos em volta de `400,0`, que é o eixo do
salão (o mesmo da fonte e do sofá).

### A origem destes modelos é o centro da base — e isso teve de ser provado

As duas caixas não se encontram na leitura crua. No `prn_statue_03` a base
(`Box031`) dá `X −21,50..−14,45` e a figura (`Object07`) dá `X −5,13..3,91`:
uma não está em cima da outra, e o `mede_rsm.py`, que mede **nó a nó**, mostra
as duas assim e não reconcilia.

O que reconcilia é o `pos` do nó raiz, que vale **exatamente o centro dos
vértices da raiz** (−17,976 é o centro de −21,50..−14,45). Os vértices da raiz
entram como `vértice − pos`, e o filho entra deslocado de
`pos_filho − pos_raiz` — aqui `(0,008; 0,441)`, quase nada. Com isso a base cai
em **−3,53..+3,53 nos dois eixos**, um quadrado de 7,06 perfeitamente centrado
na origem. **É essa coincidência que prova a leitura**, e ela vale nas duas
estátuas (a `_08` fecha igual, com `pos.x = 45,269` contra `41,74..48,80`).

Consequência prática: a origem que o `edita_mapa.py` planta na célula é o
**centro da base**. Subiu para o `CLAUDE.md` §5, junto da entrada que já falava
do `pos` do nó raiz.

### A escala oficial serve, e desta vez a conta aprova

Ao contrário da fonte — que veio de pátio de Glast Heim e desceu de 1,0 para
0,57 —, aqui os usos oficiais são **unânimes em 1,00** (`prt_lib`,
`prt_lib_q`, `prt_cas_q`, três cada), e os três são **salão fechado como o
nosso**. A ressalva que derrubou a fonte não se aplica.

A conta confirma, com a pegada remontada:

| | pegada | alcance do centro | plinto de 10×10 |
|---|---|---|---|
| `prn_statue_08` | 7,98 × 7,98 | 4,41 | sobra 0,59 |
| `prn_statue_03` | 9,04 × 9,04 | 5,22 | **passa 0,22** |

**A `_03` passa 0,22 unidade da beirada** — 4% do meio-lado, e é um braço a 3,5
células de altura, não a base, que tem 7,06 e sobra 1,47 de cada lado. Não vale
trocar a escala oficial por 0,96 para corrigir isso; fica registrado porque é
o tipo de folga que alguém mede depois e acha que foi descuido.

Altura: 25,03 e 23,92 unidades (5,0 e 4,8 células), **menos que os quatro
`모로코\동상` que o salão já tem em pé** (29,25, escala 1,0). Não esbarram em
nada.

### A rotação: a convenção do sofá reconfirmada por fora, e uma armadilha nova

`esquerda` e `frente` do pedido são tela, e em RO a câmera padrão põe o norte
para cima: esquerda = **oeste**. Daí `_03` → oeste → **rot 90**, e `_08` → sul
(para `177,67`) → **rot 0**.

A convenção — **rot 0 olha para o sul, 90 oeste, 180 norte, 270 leste** — é a
mesma que os 22 usos do sofá em `prt_cas` tinham fechado, e ganhou duas provas
independentes:

1. **As quatro instâncias oficiais destas duas estátuas.** Em `prt_lib` a `_08`
   está em rot 180 encostada na parede sul de `y29`, com o salão aberto ao
   norte; a `_03` em rot 180 na parede sul da alcova de `x103-106/y40-41`. Em
   `prt_cas_q` a `_08` em rot 0 tem chão ao sul e parede ao norte; a `_03` em
   rot 90 está num nicho fechado a leste. Nenhuma outra convenção põe as quatro
   olhando para fora da parede.
2. **A geometria.** A figura pende para `+Y` nas duas (centro em +0,70 e +0,42
   contra a base) — o passo à frente. E `+Y` é o sul em rot 0.

**A armadilha, e ela quase passou:** no mesmo salão do `prt_lib`, lado a lado
na mesma parede e olhando as duas para o norte, a `_08` está em **rot 180** e a
`prn_statue_02` em **rot 0**. São oito modelos numerados, da mesma pasta, com a
mesma cara de conjunto, e pelo menos um nasceu virado ao contrário. Calibrar um
e usar o número nos outros sete põe estátua de costas, calado. **Medir por
modelo.** Subiu para o `CLAUDE.md` §5.

### As travas antes de instalar

- **Round-trip do `rsw.py` na entrada**: os 113.618 bytes do `.rsw` limpo do
  GRF do bRO voltam **idênticos**.
- **206 → 211 objetos, +1.260 bytes** = exatamente cinco registros de modelo
  (252 cada). Os **177 modelos da entrada preservados campo a campo e na mesma
  ordem**, e as três peças anteriores saem **byte a byte iguais** às do arquivo
  instalado hoje — a receita é reprodutível.
- **A saída reabre** e a quadtree fecha no byte exato; os 182 `filename`
  resolvem no NOSSO GRF.
- **Texturas** conferidas pelo `mede_rsm.py`: `prontera\prt_j_12.bmp` nas duas,
  mais `prt_j_25` na `_03` e `prt_j_30` na `_08`. As quatro resolvem.
- **Altura e centro**: as 4 células de cada plinto na altura 0,0, as vizinhas em
  −5,0/4,0/20,0 (pedestal, piso, fosso) — o bloco é isolado —, e o modelo
  gravado em `y = 0,00`.

O arquivo anterior foi para
`C:\GuerraDoEmperium\backup-registro\auction_01.rsw.20260811-221109`.

### O que falta ver, e o que não precisou de `setwall`

Falta a tela. **Não precisa de `@reloadscript`** — não há script nesta rodada;
o que precisa é o cliente **reler o mapa**, ou seja sair e voltar ao salão
(reabrir o cliente é a garantia).

E, pela primeira vez, **a passagem não ficou aberta**: as células dos plintos
já nascem bloqueadas no `.gat` (tipo 1, e o dono nunca pôde subir nelas). O
modelo de `.rsw` continua não bloqueando nada — só que aqui o `.gat` já fazia
o serviço, e não há `setwall` a escrever.

## As duas Máquinas de Sombrios, no Centro da Ordem (2026-08-11)

Duas máquinas lado a lado na faixa aberta do salão, `auction_01` **189,58** e
**193,58**, as duas viradas para a esquerda (facing 4) — a segunda olha para a
primeira. Vieram no mesmo pedido, e a divisão de trabalho entre elas foi o que
decidiu a forma de cada uma:

| | Onde | Sprite | O que faz |
|---|---|---|---|
| **Sombrios Totais** | 189,58 | 10375 `4_VENDING_MACHINE2` | sorteia, 2 Moedas Novas o giro |
| **Sombrios Gerais** | 193,58 | 910 `2_COLAVEND` | vende a preço fixo |

A Totais devolve **um** de quatro itens, com peso: Caixa de Sombrios de Atributo
(14675, 15/34), Martelo de Refino Sombrio (23436, 15/34), Combinador de Atributo
(23247, 3/34) e Martelo Sombrio +9 (23926, 1/34).

A Gerais vende os três Cubos de Materiais Sombrios (100690, 23335 e 23663) a 2
Moedas Novas e o Combinador de Sombrios (22529) a 1.

Os oito itens já existiam no rAthena, com nome PT no `itemInfo.lua` e arte 4 de
4 no `estado_item.py`. **Nada foi criado no `db/`.**

### Por que uma é script e a outra é loja

Não é gosto: **sorteio exige `rand`, e loja de troca não roda script nenhum** —
o barter entrega exatamente a linha clicada. Por isso a Totais é script puro,
sem loja. E **preço fixo em ITEM exige barter e não `itemshop`**, porque a Moeda
Nova é `NoSell` (regra §4.10) — por isso a mercadoria da Gerais vive em
`npc/guerra/barters_guerra.yml`, na loja flutuante `SombriosGerais#loja`.

A Gerais **não sorteia de propósito**: três dos quatro itens dela são cubos, que
já são "abre e sai coisa aleatória". O sorteio está dentro do item, e sortear de
novo do lado de fora seria sortear duas vezes.

Isso deixa as duas em lados opostos da armadilha §4.9: na Totais o nome do item
sai do `getitemname()`, que lê o **servidor**; na Gerais sai do `itemInfo.lua` do
**cliente**, porque o pacote do barter leva só o ID.

### O sprite pedido não existe neste cliente

O pedido apontou o `4_GACHA_MACHINE`, que é o certo pelo nome — e este cliente
não o conhece. Ele é **10545** no `src/map/npc.hpp`, e o `npcidentity.lub` do
nosso `data.grf` para em **10508** na faixa 10xxx (403 entradas). A string
`4_GACHA_MACHINE` não aparece nem lá **nem no `npcidentity.lub` do GRF do bRO** —
não é caso de trazer do bRO, a arte não existe de nenhum lado. Teria dado NPC
invisível, calado; a mesma armadilha do 10605 no Mestre de Classe.

Os seis sprites de máquina que este cliente tem foram extraídos e **olhados**,
não só listados — um decodificador de `.spr` de rascunho, porque não havia
nenhum em `ferramentas/`:

| id | constante | o desenho |
|---|---|---|
| 506 | `4_VENDING_MACHINE` | máquina de bebidas alta |
| 562 | `2_DROP_MACHINE` | máquina de garra, cheia de cápsulas coloridas |
| 563 | `2_SLOT_MACHINE` | caça-níquel, letreiro JACKPOT |
| 564 | `2_VENDING_MACHINE1` | bebidas — **já em uso** em três NPCs |
| 10081 | `4_MACHINE_DEVICE` | aparelho pequeno, 32x29 |
| 10375 | `4_VENDING_MACHINE2` | cilindro de vidro sobre coluna |

O 562 é o que mais parece uma máquina de cápsula; **o dono escolheu o 10375**,
que também evita repetir o 564. O 910 (`2_COLAVEND`, a máquina de refrigerante
vermelha) veio pedido para a segunda e existe, com `.spr`/`.act`.

### O pedido dizia `auction_02`, e a coordenada decidiu sozinha

As duas máquinas foram pedidas em `auction_02`, que é o salão da Ordem dos
Exploradores — o Centro da Ordem é o `auction_01`. Não foi preciso perguntar: no
`auction_02` as células **189,58 e 193,58 são tipo 1, rocha**, e o bloco inteiro
em volta (x183-195, y54-62) também. No `auction_01` as duas são tipo 0, altura
4,00, na fileira que anda de x186 a x195.

O `.gat` dos dois mapas está com DES no nosso GRF (`flags=5`) e foi lido do GRF
do bRO, que é a mesma revisão do mapa.

### A prova de que o NPC carregou, e por que ela custou três tentativas

`@reloadscript` não estava disponível (o servidor no ar, e o dono é quem dá o
comando), então a prova foi por reinício do map-server e leitura do log. Zero
`Unknown syntax` prova só que nada quebrou — **não prova que o arquivo foi
lido**. A sonda que provaria foi um `debugmes` no `OnInit`, e ela não apareceu
por dois motivos empilhados, nenhum deles o esperado:

1. **`console_msg_log: 3`** em `conf/import/map_conf.txt` grava só Warning (1) e
   Error (2). Debug é o bit **4**, e estava desligado de propósito.
2. Mesmo com o bit 4 ligado, nada. O que faltava era **esperar**: o log continua
   sendo escrito depois de a porta 5121 abrir, e a leitura tinha sido feita cedo
   demais. O `servidor.py subir` volta assim que a porta responde.

A sonda que fechou foi um `errormes` (canal já provado pelos 916 avisos do boot),
e respondeu de uma vez: `SONDA-A: OnInit comecou` e
`SONDA-B: n=4 total=34 p0=14675 p3=23926` — arquivo lido, `OnInit` rodando, as
duas colunas da tabela em sincronia e o total certo. Sondas retiradas e
`console_msg_log` de volta em 3.

### A armadilha que só a tela mostrou

No primeiro teste em jogo o **Martelo Sombrio +9 apareceu grudado no fim da linha
do Combinador de Atributo**. A causa é a indentação: a lista de prêmios nascera
com dois espaços na frente de cada linha, e **`mes` que começa com espaço não
abre linha nova**. Subiu para o `CLAUDE.md` §5 — o registro completo está lá, e
o raciocínio, no cabeçalho do NPC.

O que vale guardar aqui é o formato da falha: das quatro linhas, **três pareciam
certas** porque tinham estourado a largura da caixa e quebrado sozinhas. Só a
quarta coube e denunciou. E o que decidiu não foi olhar o print inteiro — foi
recortar a caixa de diálogo e ampliar em nearest-neighbor, aí as seis linhas
puderam ser medidas uma a uma contra a hipótese.

### O título encurtou depois do teste

Nasceram "Máquina de Sombrios Totais" e "Máquina de Sombrios Gerais", e o dono
encurtou os dois para **"Sombrios Totais"** e **"Sombrios Gerais"** depois de ver
em jogo.

### Duas coisas ditas por escrito na entrega

- **A porcentagem do Combinador de Atributo veio 8,24% no pedido, e 3/34 é
  8,82%.** Os pesos somam 34 exatos e são o que a máquina usa; a tela imprime
  8,82% porque a conta é feita a partir deles. Se a intenção era 8,24%, o que
  muda é o peso.
- **Três dos quatro prêmios da Totais não têm `NoDrop`** (23436, 23247 e 23926 —
  só a Caixa 14675 tem). Sem `checkweight` eles cairiam no chão do salão com o
  jogador já cobrado, pela armadilha do `getitem` (§5). Daí a ordem do script:
  **sorteia → confere o prêmio sorteado → cobra → entrega**. O sorteio vem antes
  da cobrança porque o `checkweight` precisa saber qual item vai entregar — os
  quatro pesam 10 e são empilháveis, mas empilhável só dispensa slot livre se o
  jogador **já** tem aquele item.

### O segundo teste: a Gerais enterrada e virada para o lado errado (2026-08-12)

A Totais passou. A Gerais voltou com dois defeitos, e nenhum dos dois era do
script.

**Enterrada.** A máquina apareceu com a base cortada por uma linha reta e
horizontal. A primeira suspeita — degrau no terreno — foi medida e descartada:
as duas células e a faixa inteira de `y56` a `y60`, de `x186` a `x195`, estão em
altura **4,00**, plana, com os quatro cantos iguais.

Era o **`.act`**. Ele diz a que altura o desenho é colado em relação à célula, e
o `2_COLAVEND` vem com `y = 0` nas oito direções — o centro do sprite fica na
altura do chão e a metade de baixo vai para debaixo do piso, onde o depth buffer
do terreno a corta. Daí o corte reto, que é o que separa este caso de um
problema de posicionamento: sprite mal posicionado aparece inteiro e deslocado;
sprite cortado reto está sob o piso.

A medida que fechou o caso comparou as cinco máquinas do cliente, e a exceção
salta:

| sprite | altura | `y` |
|---|---|---|
| `4_vending_machine` (a Totais) | 122 | −53 |
| `4_VENDING_MACHINE` | 122 | −53 |
| `2_DROP_MACHINE` | 118 | −44 |
| `2_VENDING_MACHINE1` | 114 | −40 |
| **`2_COLAVEND`** | 123 | **0** |

Corrigido para **−53**, que é `-(altura/2 - 8)` — a conta que os quatro oficiais
seguem, e a mesma do `4_vending_machine`, de altura praticamente igual. O
override mora em `cliente\data\sprite\npc\2_COLAVEND.act`, **fora do git**, e a
receita ficou versionada em `ferramentas/levanta_sprite_npc.py`.

**Virada para o lado errado.** Nasceu em facing 4 por causa da tabela de
"direita/esquerda na tela" do cabeçalho da `maquina.txt` — que foi escrita para
*aquele* sprite e não se traduz. O que vale é o ponto cardeal: de `193,58` para
`189,58` a direção é **oeste**, `DIR_WEST = 2`. A tabela medida em jogo (4 sul →
baixo-direita, 2 oeste → baixo-esquerda, 0 norte → cima-esquerda, 6 leste →
cima-direita) subiu para o `CLAUDE.md` §5, junto com a armadilha do `.act`.

### As duas ferramentas que nasceram desta rodada

Não havia leitor de `.spr` nem de `.act` em `ferramentas/`. O de `.spr` ficou
como rascunho (serviu para **olhar** os seis sprites de máquina antes de
escolher, em vez de decidir pelo nome); o de `.act` virou peça:

- **`ferramentas/act.py`** — leitor de formato, na mesma prateleira do `gat.py`,
  `gnd.py` e `rsw.py`. **Recusa-se a devolver dados se sobrar byte**, pela regra
  do `mede_rsm.py`. Há 4 bytes não identificados entre o fim das ações e o vetor
  de atrasos; sem pulá-los o vetor sai `[0.0, 4.0 ×7]` em vez de `[4.0 ×8]`.
  O alinhamento dos `(x,y)` foi provado **por fora**: no `2_DROP_MACHINE` as
  oito camadas dão todas `(6,−44)` e o padrão de bytes aparece exatamente oito
  vezes no binário.
- **`ferramentas/levanta_sprite_npc.py`** — a ferramenta. Escreve **byte a byte
  no lugar**, não re-serializa: só os `y` mudam, o tamanho não mexe, e campo que
  o leitor não entenda sobrevive. Relê o resultado antes de dar por feito.

## Dezenove visuais, três equipamentos e uma máscara que não existia (2026-08-12)

Um pedido de vinte e dois itens para as lojas de Prontera, em oito grupos.
Entraram **19 nas quatro lojas de visual** (`mercado_de_visuais.txt`) e
**3 nas de equipamento** (`mercado_contemporaneo.txt`), e mais duas peças
**mudaram de vitrine** sem terem sido pedidas para isso.

O saldo por loja:

| loja | antes | depois |
|---|---|---|
| Costumeiro (visual topo) | 164 | 174 |
| Adereceiro (visual meio) | 124 | 125 |
| Camareiro (visual baixo) | 123 | 128 |
| Manteleiro (visual capa) | 24 | 25 |
| Retoqueiro (cabeça baixo) | 4 | 5 |
| Sapateiro | 9 | 10 |
| Acessorista | 13 | 14 |

**Dezessete dos vinte e dois não custaram nada** — `item_db`, `itemInfo.lua` e
arte já estavam os três no lugar, e `valida_visual.py` deu 8 de 8 (ou 4 de 4,
nos que não são de cabeça) antes de qualquer edição. Os outros cinco são o
assunto desta seção.

### Quatro divergências de slot, e o remédio de cada uma é outro

O pedido chegou agrupado por slot, e em **quatro** itens o grupo não batia com
o `Locations:` do `item_db`. A regra §4.14 do `CLAUDE.md` já dizia que quem
decide a vitrine é o `Locations:`; o que esta rodada acrescentou foi que **o
`Locations:` do nosso rAthena também pode estar errado**, e que separar um caso
do outro é uma consulta de um comando:

    python ferramentas/estado_item.py --id <n> --descricao

A linha `Equipa em:` da descrição do bRO é o desempate. Deu dois de cada:

**O vendor errado (dois) — corrigido por override, e a peça mudou de loja.**

- **Cachecol Glorioso (15854)** — nosso `item_db`: `Costume_Head_Top`. bRO:
  Baixo. Saiu do **Costumeiro** e foi para o **Camareiro**.
- **Coleira do Vassalo (31954)** — nosso `item_db`: `Costume_Head_Mid`. bRO:
  Baixo. Saiu do **Adereceiro** e foi para o **Camareiro**.

Nos dois o pedido concordava com o bRO, o que confirma a leitura. É o segundo e
o terceiro caso da fileira depois da Piscadela de Freya (2026-08-07), e nos três
o bRO ganhou. Os overrides estão em `db/guerra/item_db.yml`, com `false`
explícito no slot velho — `Locations` é OR e não atribuição, então omitir o
slot antigo deixaria a peça ocupando os dois.

**O pedido enganado (dois) — a peça foi para a loja do `Locations:`, com a
ressalva por escrito no comentário da loja e dita ao dono do projeto.**

- **Gata Branca (31452)** — pedida em cabeça baixo. `item_db` e bRO dizem
  **Meio**, os dois. Foi para o **Adereceiro**.
- **Manto do Herói (420112)** — pedido em cabeça meio. `item_db` e bRO dizem
  **Baixo**, os dois — e é `Head_Low`, equipamento de verdade (DEF 2, peso 10,
  nível 100, HP +15% e resistência a Humanoide +3%), não visual. Foi para o
  **Retoqueiro**, no Mercado Contemporâneo.

Mesmo caminho da Máscara de Minorous em 2026-08-09. Nos dois, mudar a vitrine
depois é mexer no `Locations:`, não na linha da loja — e essa é a decisão que
ficou com o dono (`PENDENCIAS.md` §1k).

### A Máscara de Loki (5983) não existia, e tem dois homônimos que enganam

Não estava em `item_db` nenhum — nem no `db/re/`, nem no nosso —, e nenhum dos
4 arquivos de arte estava no cliente. Só o `itemInfo.lua` e o bRO a conheciam.

O risco aqui não era a criação, era **pegar o item errado**: o nosso rAthena já
tem dois "Loki mask", e os dois dividem o `View 346`.

| id | AegisName | o que é |
|---|---|---|
| 5332 | `Loki_Mask` | equipamento, `Head_Low`/`Head_Mid`, View 346 |
| 19615 | `C_Loki_Mask` | visual, View 346 — o mesmo desenho do 5332 |
| **5983** | `C_Loki_Assassin_Mask` | visual, **View 1345** — outro desenho |

O que separou os três foi o **nome do recurso** do `itemInfo.lua` do cliente,
casado contra o `accname.lub` do bRO: ele dá `ACCESSORY_Loki_Assassin_Mask`,
View 1345. Escolher pelo nome em português teria pegado qualquer um dos três.

**O View 1345 já existia no `accessoryid.lub` do nosso GRF de 2021** — conferido
antes de escrever a entrada —, então este item não precisou do
`estende_accessoryid.py`. Faltava só a arte, e os 8 arquivos vieram da GRF do
bRO pelo `instala_visual.py`. A entrada nasceu como **placeholder** em
`db/guerra/item_db.yml`: `Costume_Head_Low` e nível 1, sem `bonus` nenhum,
porque a descrição do bRO não tem uma única linha azul de efeito.

### O Manto Invisível (20506) não gasta slot de manto

É `Costume_Garment` e foi para o **Manteleiro**, mas **não tem `View`** — então
não passou pela tabela `spriterobeid.lub` nem pelo `instala_manto.py`, e não
consumiu nenhum dos 31 slots doadores que sobram (`PENDENCIAS.md` §4). É o
quarto "Invisível" do mercado, e nele o nada é o produto, como nos três de
2026-08-05. Não confundir com a Aura Nevada, que também não tem `View` mas cujo
produto é um `hateffect` visível.

### O Manto do Herói estava fora do `itemInfo.lua`

O cliente o mostraria **sem nome e sem ícone na própria vitrine**. Veio do bRO
pelo `completa_iteminfo.py`, e o `Name` do servidor, que estava em inglês
("Guardian Claus"), foi sincronizado pelo `nomes_pt_item_db.py`. Arte não
faltou: 8 de 8. É a quarta vez que esse mesmo trio de passos aparece — 410125,
410067/410026, 410010, agora este.

**Efeito colateral do sincronizador, e ele é inofensivo:** ao rodar, ele
devolveu ao inglês o `Name` de **13 itens** no `db/re/item_db_equip.yml`. São
justamente os que têm override em `db/guerra/item_db.yml`, que o tolera de
propósito ("fora por nossos") porque o nosso arquivo é lido depois e vence a
mesclagem. O nome em memória não mudou; o que mudou foi o valor sombreado.

### Quatro avisos novos de `discounted buying price`

Quatro dos onze chapéus de topo têm `Buy` no `item_db` — 19789, 19829, 19966 e
20038 —, então o mercado de visuais passou de **nove** para **treze** linhas de
`npc_parse_shop: Item X discounted buying price` na subida. A conta foi refeita
item a item e a lista no cabeçalho do arquivo foi atualizada, que é o que
permite ignorar as treze e desconfiar da décima quarta. Revendem por 10 ou por
5, ou seja 9 e 4 de lucro por compra: não move nada.

### A armadilha que esta rodada pagou, e que subiu para o `CLAUDE.md`

Os arquivos de NPC são **cp1252 e CRLF**. A ferramenta de edição do assistente
lê e grava como UTF-8: usada num deles, ela troca **todo** byte acentuado do
arquivo por U+FFFD — não só os da linha editada. Foi medido de propósito, num
arquivo de rascunho de três linhas com seis acentos, antes de a regra ser
escrita: trocar uma linha **sem acento nenhum** destruiu os seis. O `CRLF`
sobrevive.

Por isso as sete linhas de loja e todos os comentários desta rodada foram
gravados **por script**, com âncora ASCII, `encode('cp1252')` num lugar só,
`assert` de âncora única e `decode('cp1252')` de volta antes de valer. Dois
erros apareceram nesse caminho e os dois foram baratos porque o `assert` parou
antes de gravar: âncora escrita com `\n` num arquivo CRLF casa zero vezes, e a
primeira versão do script remontou as linhas de loja **sem o `\r`**, deixando
fim de linha misturado no arquivo. A regra inteira está no `CLAUDE.md` §5.

### O que falta ver no jogo

Nada disto subiu. O roteiro está no `PENDENCIAS.md` §1, e a ordem importa:
`@reloaditemdb` **antes** de `@reloadscript`, porque a loja valida cada ID ao
carregar. E **fechar e reabrir o cliente**, por causa da entrada nova do
`itemInfo.lua` (420112) e da arte nova da Máscara de Loki — os dois só são
lidos na inicialização.

## A Tranqueiras, a Morte na porta da arena e duas gavetas na Máquina (2026-08-12)

Quatro pedidos numa tacada, no mesmo dia dos dezenove visuais acima. Três são
de conteúdo e um é de posição; o que custou não foi editar nenhum deles.

### A Máquina ganhou duas linhas, e as duas são de outra natureza

`npc/guerra/barters_guerra.yml`, na loja `Maquina#loja`:

| item | preço | o que é |
|---|---|---|
| 25792 Ticket de Expansão de Inventário | 10 Moedas Novas | +10 espaços |
| 12622 Rédea | 100 Moedas Novas | montaria permanente |

As dezoito de antes eram consumo — caixa que se abre, pergaminho que se gasta.
Estas duas **se gastam por personagem**, e por isso entraram num quarto grupo
no fim da lista em vez de dentro de "Consumíveis". O `Index` segue a regra de
sempre: item novo no fim do grupo dele, sem abrir buraco no meio.

**O Ticket é mais um caso da §4.9** — sistema de UI do cliente cuja metade de
configuração não está no `db/`. Quem o consome é o
`clif_parse_inventory_expansion_request` (`clif.cpp:23086`), que lê uma **tabela
fixa no C++** de três IDs, e 25792 é um deles. `grep` do ID em `npc/` não
devolve nada, e a conclusão fácil — a mesma armadilha dos cupons de estilista,
quinze linhas acima na mesma loja — seria que ele não serve para nada aqui.

**O teto é dez por personagem, e é de compilação.** `INVENTORY_BASE_SIZE` é 100
e `INVENTORY_EXPANSION_SIZE` é 100 (`src/common/mmo.hpp:44`), então o inventário
vai de 100 a 200 e para. O décimo primeiro ticket recebe `MAXIMUM_REACHED` e
**não é comido — mas já foi comprado**, e as 10 Moedas se perderam. O preço foi
calibrado para isso: 100 Moedas dobram o inventário.

**A Rédea é a única das cinco que não expira**, e o nome não separa uma da
outra:

| id | nome exibido | o que faz |
|---|---|---|
| **12622** | Rédea | **`NoConsume: true`** — não sai da bolsa, nunca |
| 16682 | Caixa de Rédea | entrega a 12622, por `getgroupitem` |
| 16683 | Caixa de Rédea [30 dias] | entrega a 12622 **alugada** |
| 17162 | Caixa de Rédea [7 dias] | idem |
| 17176 | Caixa de Rédea [3 dias] | idem |

Vender qualquer uma das três últimas entregaria uma montaria que expira, e o
jogador só descobriria dias depois. O `NoConsume` é o que faz a montaria durar
para sempre: o item roda `setmounting()` e continua na bolsa.

### A Arena de Combate mudou de cara e de esquina — e devolveu o Guia

`npc/guerra/arena_de_combate.txt`: sprite 966 (`4_M_RUSKNIGHT`) → **10028
(`4_M_DEATH`)**, `prontera 154,187` → **147,180**, facing **6 (leste)**.

As duas conferências que a regra do sprite manda, e as duas passaram:
`JT_4_M_DEATH = 10028` no `npcidentity.lub` **deste** cliente — não só no
`npc.hpp` do rAthena, que aceita qualquer número — e `4_m_death.spr` mais o
`.act` presentes no nosso `data.grf`. Bem abaixo do teto de 10508 medido em
2026-07-31. A célula de destino foi lida no `prontera.gat` do cliente: tipo 0,
andável, altura 1,00 nos quatro cantos, e sem NPC nenhum a menos de três
células.

**A consequência que veio junto foi a que valeu a rodada.** O OnInit daquele
arquivo carregava um `disablenpc "GuideProntera"` desde 2026-08-08, e ele
**nunca foi sobre a Arena — era sobre a célula**: 154,187 era do Guia de
Prontera, e dois NPCs empilhados numa célula não dão erro nenhum, só um NPC
invisível por cima do outro. Saindo a porta para uma célula vazia, não há mais
o que desligar: a linha saiu e **o Guia voltou a atender em 154,187**, onde
estava antes de 2026-08-08.

Isso deixou o arquivo sem nenhuma alteração em código de terceiros — o único
enxerto que sobra é a linha `pvp_nightmaredrop off`, e ela também é movimento
de fora.

**Três documentos afirmavam coisas que deixaram de ser verdade**, e os três
foram corrigidos na mesma passada: o cabeçalho do `porteiro_do_treinamento.txt`
("quem desliga o Guia agora é o arena_de_combate.txt"), a seção "A volta" do
próprio arquivo (media a distância até uma porta que mudou de lugar) e o
parágrafo do `scripts_guerra.conf`, que ainda prometia **duas** linhas de
mapflag — o `pvp_nocalcrank` já tinha sido tirado do arquivo e o índice não
soube. Índice que descreve o que o arquivo não faz mais é pior que índice sem
descrição: alguém o lê e acredita.

### A Tranqueiras — de 26 materiais a 1 zeny para 55 pelo preço de compra

*A loja nasceu e mudou de preço no mesmo dia. As quatro partes abaixo estão na
ordem em que aconteceram; quem quiser só o estado final vai para a última.*

> **Atenção a quem ler só a primeira metade:** o Ouro (969) sai da lista na
> manhã e **volta na tarde**, quando o preço muda. A poda descrita a seguir foi
> real, e foi desfeita horas depois pela causa que a tinha motivado.

`npc/guerra/tranqueiras.txt`, novo. `prontera 151,131`, o degrau seguinte da
grade dos mercados, uma fileira abaixo da Carta de Acessório. Três grupos, na
ordem em que a janela os desenha: as peças que as dez Runas do Cavaleiro
Rúnico pedem — **16 das 17**, porque o Ouro saiu (ver abaixo), três avulsos por nome (Teia de Aranha, Semente de Planta
Selvagem, Garrafa Vazia) e os **6 do Criar Veneno Mortal** que faltavam — a
Garrafa Vazia daquela receita é a mesma do grupo 2, e não aparece duas vezes.

**A loja não vende runa pronta, só o que elas custam.** Vender a runa feita
esvaziaria o forjar do Cavaleiro Rúnico, que é onde o Galho Antigo é gasto. Os
dez IDs ficaram registrados no cabeçalho para o dia em que a decisão mudar.

Os 26 passaram pela validação da §4.4 um a um — o Ouro incluído, e ele
só saiu depois, por economia: os 26 existem no `item_db` do
servidor, os 26 têm entrada no `itemInfo.lua` deste cliente **com nome em
português**, e os 26 deram "arte 4 de 4 ok". Nenhum precisou de entrada nova de
cliente nem de arte trazida do bRO — é a primeira lista da série que não
precisou de nada.

#### O preço de 1 zeny abriu um buraco, e ele foi fechado no mesmo dia

A convenção dos três mercados de Prontera é 1 zeny desde 2026-08-01, e o
cabeçalho do `mercado_contemporaneo.txt` já registrava o que ela abre: quem
compra por 1 revende em **qualquer** NPC pelo `Sell` do `item_db` — não depende
do NPC vendedor —, e o servidor avisa disso item a item ao carregar
(`npc_parse_shop`, `src/map/npc.cpp:4153`). O pior caso conhecido do projeto era
a Boina Alada do Chapeleiro, 14.999 de lucro por clique, **registrado e aceito**
desde a abertura do mercado.

A lista da Tranqueiras foi medida antes de o arquivo existir, e trouxe um caso
de outra ordem de grandeza:

| item | `Buy` | `Sell` | lucro por clique a 1 zeny |
|---|---|---|---|
| **969 Ouro** | 150.000 | **75.000** | **74.999** |
| 657 Poção da Fúria Selvagem | 4.500 | 2.250 | 2.249 |
| 7939 Galho Antigo / 7938 Partículas de Luz | 1.500 | 750 | 749 |
| os outros 22 | — | — | de 15 a 521 |

Em laço infinito, o Ouro sozinho tornaria zeny irrelevante — cinco vezes a
Boina, que já era o teto tolerado.

**A decisão veio do dono na mesma sessão, e com o motivo: o drop está em 50x.**
Saíram os dois — o **Ouro (969)** da Tranqueiras e a **Boina Alada (5170)** do
Chapeleiro. Das duas saídas possíveis, foi escolhida a segunda:

1. **`Sell: 0` / `Trade: NoSell` por override** em `db/guerra/item_db.yml`.
   Fecha de vez — e alcança **todo** o Ouro e toda a Boina do servidor,
   inclusive o que o jogador caçou. Descartada por isso.
2. **Tirar as peças das listas.** Uma linha em cada arquivo, não mexe em mais
   nada, e não toca no que já está na mão de ninguém.

Dois custos foram aceitos junto, e os dois estão escritos no arquivo de cada
loja para que não sejam "consertados" por engano:

- **A Runa Luxanima não fecha só com a Tranqueiras.** Ela pede 1 Galho Antigo,
  3 Partículas de Luz e **3 Ouros**, e o Ouro saiu. As outras nove receitas
  fecham inteiras na vitrine. *(Custo desfeito na mesma tarde: com o preço de
  compra o Ouro voltou, e as dez fecham.)*
- **A Boina Alada era peça irmã de um dos três conjuntos espelhados** para o
  19455 em `db/guerra/item_combos.yml`. O espelho **não mudou** — ele vive no
  `item_combos.yml` e não depende de loja nenhuma —, mas a peça deixou de ser
  comprável no mercado: quem quiser fechar aquele conjunto agora a caça. Sobrou
  o Traje Protetor (19381), no Retoqueiro, como única irmã à venda.

**O maior que ficou é a Poção da Fúria Selvagem (657), com 2.249** — sete vezes
o terceiro colocado. Não entrou na poda porque a decisão nomeou dois itens e não
uma faixa; se a conta de zeny apertar um dia, é por ela que se começa. Do
terceiro para baixo (749) nada move a economia.

#### O sprite é uma classe de jogador, e nenhum NPC do rAthena faz isso

Pedido: sprite **5**, `JOB_MERCHANT`. Os 26 mil `script` do vendor usam view id
de NPC (≥ 44) e **nenhum** usa id de classe — a varredura foi feita antes de
gravar, justamente porque a ausência total costuma querer dizer alguma coisa.

**Funciona, e o caminho é explícito.** O `status_set_viewdata`
(`src/map/status.cpp`, `case BL_NPC`) tenta o `npc_get_viewdata` primeiro, que
devolve nulo para 5 — o `npcdb_checkid` só aceita de 44 para cima —, e cai num
ramo `else if (pcdb_checkid(class_))` que monta a aparência à mão:
`look[LOOK_BASE] = 5`. O corpo de Mercador do jogador existe nos dois sexos no
nosso `data.grf` (conferido; o nome coreano da pasta é `상인`, não `머천트` —
procurar pelo segundo devolve zero e **parece ausência**).

**Mas aquele ramo deixa a cabeça em zero, e zero não existe.** Ele faz
`look[LOOK_HAIR] = cap_value(0, MIN_HAIR_STYLE, MAX_HAIR_STYLE)`, e o nosso
`min_hair_style` (`conf/battle/client.conf`) é **0** — então o NPC nasceria
pedindo o penteado 0. Os penteados deste cliente vão de **1 a 42**, nos dois
sexos: não há `0_<sexo>.spr`. Daí as duas linhas de `setunitdata` no OnInit, que
não são enfeite:

```
setunitdata(getnpcid(0), UNPC_SEX, SEX_MALE);
setunitdata(getnpcid(0), UNPC_HAIRSTYLE, 1);
```

As duas **gravam no `nd->vd` do próprio NPC** e não são um pacote solto: o
`clif_changelook`, no `case LOOK_HAIR`, faz `vd->look[type] = val`
(`clif.cpp:4031`), então valem para quem logar depois. Sem essa checagem a falha
seria da família de sempre — tabela certa, arte certa, e o NPC sem cabeça na
tela, calado.

A saída, se mesmo assim ele nascer errado, já veio escolhida no pedido e está no
cabeçalho: trocar por **776 (`4_M_TWMIDMAN`)**, que é sprite de NPC de verdade —
conferido no `npcidentity.lub` deste cliente e com `.spr` e `.act` em
`data\sprite\npc\`. As duas linhas de `setunitdata` saem junto, porque view id de
NPC traz a aparência pronta do `npc_viewdb`.

#### A alquimia entrou no mesmo dia, e levou o preço da loja inteira junto

O pedido veio pela **tabela de Preparar Poção do browiki** — 21 receitas, e a
coluna de ingredientes delas —, com uma exceção nomeada: **o Álcool não se
vende**. A loja passou de 25 para **55 itens**: 29 vieram da alquimia, e o
quinquagésimo quinto é o Ouro, que a troca de preço deixou voltar.

Dos ingredientes da tabela, **cinco já estavam na vitrine** pelos grupos de runa
e veneno — Mel, Garrafa Vazia, Esporo Venenoso, Espinho de Cacto e Gema Vermelha
—, então entraram **29**. A ordem da linha do `shop` é a da tabela, lida de cima
para baixo e da esquerda para a direita, e é por isso que a Garrafa de Poção
abre o grupo: ela é o primeiro ingrediente da primeira receita.

**Medir o preço antes de escrever a linha foi o que salvou a tarefa.** A conta
de lucro por clique a 1 zeny, feita contra o `item_db` e não a olho, achou três
itens numa faixa que a loja não tinha — e os três são a mesma linha da tabela, a
do Embrião:

| item | `Buy` | `Sell` | lucro por clique a 1 zeny |
|---|---|---|---|
| **7140 Semente da Vida** | 60.000 | 30.000 | **29.999** |
| **7141 Orvalho da Yggdrasil** | 20.000 | 10.000 | **9.999** |
| 7143 Cápsula da Criação | 5.000 | 2.500 | 2.499 |
| 504 Poção Branca | 1.200 | 600 | 599 |
| os outros 25 | — | — | de 0 a 419 |

A Semente sozinha é **treze vezes** o pior caso que tinha sobrado da poda da
manhã (a Poção da Fúria Selvagem, 2.249) e 40% do Ouro que acabara de sair. Pôr
os 29 a 1 zeny desfaria a decisão daquela manhã em silêncio.

**A decisão do dono não foi tirar os três: foi trocar o preço da loja inteira.**
A vitrine inteira passou a sair pelo **preço de compra do `item_db`** — e foi
esse mesmo movimento que deixou o Ouro voltar, logo abaixo.

Na linha do `shop` isso não é número escrito: é **`-1`**, que o
`npc_parse_shop` troca pelo `Buy` do item ao carregar —
`if (value < 0) value = id->value_buy;` (`src/map/npc.cpp:4146`). Escrever os
valores à mão criaria uma segunda fonte para o mesmo preço, e as duas
divergiriam calado no dia em que alguém pusesse um override em
`db/guerra/item_db.yml`; com `-1`, a vitrine acompanha o `item_db` sozinha.

**Isso fecha o exploit por inteiro, e dá para provar sem subir o servidor.** O
teste que dispara o aviso do `npc_parse_shop` (`npc.cpp:4153`) é
`value*0.75 < value_sell*1.24` — a compra mais barata possível, com Descontar
10, contra a venda mais cara possível, com Overcharge 10. Com o preço valendo
`Buy`, vira `0,75·Buy` contra `1,24·Sell`; e como **os 55 itens desta loja têm
`Sell` exatamente igual a `Buy/2`**, dá `0,75·Buy` contra `0,62·Buy`. **O aviso
não sai para nenhum dos 55** — conferido um a um contra o `item_db`. A loja que
imprimia 25 avisos ao carregar passa a imprimir zero.

Consequências que ficaram registradas nos cabeçalhos para não serem
"consertadas" por engano:

- **Esta é a única loja nossa de Prontera que não cobra 1 zeny.** Os três
  mercados seguem a convenção de 2026-08-01 e não foram tocados. Pôr a
  Tranqueiras de volta a 1 zeny reabre o buraco em 55 itens de uma vez.
- **O Ouro (969) voltou para a lista, e a volta é a mesma decisão.** Ele saíra
  de manhã por revender 75.000 a 1 zeny; à tarde, com o preço valendo `Buy`,
  ele passa no teste como qualquer outro item — **112.500 contra 93.000** —, e
  não dá lucro nenhum. Não é exceção aberta para ele: é a regra dos outros 54.
  Com isso **a Runa Luxanima voltou a fechar, e as dez receitas de runa fecham
  inteiras na vitrine**.

  **As duas decisões ficaram amarradas, e é isso que os cabeçalhos precisam
  dizer:** o Ouro só é seguro aqui *enquanto* o preço for o de compra. Baixar a
  loja de volta para 1 zeny com ele dentro devolve 74.999 por clique — o buraco
  original, inteiro. A Boina Alada (5170) **não** voltou: o Chapeleiro continua
  a 1 zeny, então a conta dela continua sendo a de antes, e repô-la lá é outra
  decisão, ainda não tomada.
- **O Tubo de Ensaio (1092) ficou de fora por decisão do dono**, junto com o
  Álcool. Dos três recipientes da tabela, dois estão à venda — a Garrafa de
  Poção (1093), que entrou com este grupo, e a Garrafa Vazia (713), que já
  estava. Sem o Tubo, **quatro das 21 receitas não fecham só com esta vitrine**:
  o Álcool e as três Poções Compactas. As outras dezessete fecham.

A validação da §4.4 rodou de novo, sobre **30** itens — os 29 que entraram mais
o Tubo de Ensaio, que passou na conferência e só depois ficou de fora. Todos
existem no `item_db`, todos têm entrada no `itemInfo.lua` deste cliente **com
nome em português**, e todos deram "arte 4 de 4 ok": **120 checagens, zero
quebra**. Nenhum precisou de entrada nova de cliente nem de arte do bRO — a
segunda lista seguida que não precisou de nada.

A placa acompanhou: `Materiais de runa e veneno` virou
`Materiais de runa, veneno e alquimia`, 36 dos 79 caracteres do `MESSAGE_SIZE`.

### O que falta ver no jogo

Nada disto subiu. `@reloadbarterdb` para as duas linhas da Máquina — **não** é
`@reloadscript` —, `@reloadscript` para a Tranqueiras, a Arena e o Guia.

**A Tranqueiras não deve mais imprimir aviso nenhum ao carregar.** Ela imprimia
25 `npc_parse_shop: ... discounted buying price` enquanto era de 1 zeny; com o
preço de compra, a conta acima diz que são zero. Se algum aparecer, é item cujo
`Sell` não é `Buy/2` — e aí o número no aviso diz qual.

O que só se decide na tela: se o Mercador de classe 5 desenha inteiro (corpo
**e** cabeça), e se a Morte da porta da arena ficou virada para o lado certo.

## Três ajustes em Comodo: o balão, a Morte e a aura que não existe (2026-08-12)

Pedido de três linhas, no mesmo dia da Tranqueiras. Dois foram uma palavra
cada; o terceiro não tinha como ser feito como pedido, e descobrir isso é o
que a rodada realmente produziu.

### O balão de MVP da Criança: de 4 em 4 para 3 em 3 segundos

`npc/guerra/crianca_de_comodo.txt`. Uma palavra — e é uma palavra porque **o
intervalo é o NOME do label**, não um argumento: `OnTimer4000:` virou
`OnTimer3000:`, e o `initnpctimer` do `OnInit` não se toca. Quem procurar o
número no `initnpctimer` não o acha.

### O Espectro da porta: sprite novo e facing pelo destino

`npc/guerra/corredor_fantasma.txt`, o de `comodo 208,187`:

| | antes | depois |
|---|---|---|
| sprite | `4_M_DEATH` (10028) | `4_M_DEATH2` (10092) |
| facing | 4 (sul) | 6 (leste) |

**O `4_M_DEATH2` é outra arte, não um apelido**, e isso foi conferido antes de
trocar: os dois `.spr` têm o mesmo tamanho no GRF (3.800.782 bytes, mesmas
dimensões e mesmo número de quadros) e md5 diferente — é um recolorido. Fosse
o mesmo arquivo, a troca seria um diff sem efeito nenhum na tela, e nada
denunciaria.

As duas conferências de sempre passaram para o número novo: `JT_4_M_DEATH2 =
10092` no `npcidentity.lub` **deste** cliente, e o `.spr` mais o `.act` no
nosso `data.grf` — este legível, enquanto o do `4_M_DEATH` está com DES (o
cliente decifra; a nossa `grf.py` não). Abaixo do teto de 10508.

O facing veio pedido como *"virado para 211 186 (leste)"*, e é assim que a
conta se faz: **a direção é a que leva DESTA célula até a que se quer
encarar**. De `208,187` para `211,186` são três a leste e uma ao sul — leste,
`DIR_EAST = 6` (`src/map/path.hpp:16`).

**O Espectro da saída, em `vis_h01 34,34`, ficou como estava** — perguntado e
decidido na hora. O mesmo personagem tem duas artes, uma em cada ponta, e o
cabeçalho do arquivo diz que é decisão e não esquecimento.

### A aura de chão: o `1_SHADOW_VIOLET` não existe neste cliente

O terceiro pedido era pôr o sprite `1_SHADOW_VIOLET` aos pés do Espectro. Ele
**não existe aqui**, e as quatro conferências foram todas negativas:

| Onde | Resposta |
|---|---|
| `src/map/npc.hpp` do rAthena | `JT_1_SHADOW_VIOLET` = **10560** |
| Teto de sprite deste cliente | **10508** — o número está acima |
| `npcidentity.lub` do nosso `data.grf` | ausente; das 4.578 chaves, a única `1_SHADOW_*` é a `1_SHADOW_NPC` (723) |
| `jobname.lub`, nosso e do bRO | nenhuma entrada com "violet" |
| `.spr`/`.act`, nosso GRF e o do bRO | não existem |

É o último de um arco-íris de sombras coloridas que o rAthena numera de 10554
a 10560 — RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET —, conjunto de um
kRO bem posterior ao nosso cliente de 2021-11-03. Escrever o número assim
mesmo faria o NPC nascer **invisível, calado**, que é a armadilha de sempre.

**E não há substituto colorido.** Isso não foi suposto, foi varrido: dos 1.046
sprites de NPC com arte legível e view id abaixo do teto, exatamente **dois**
são decalque chato de quadro único — o `4_PURPLE_WARP` (10237) e o
`1_SHADOW_NPC` (723) —, e os dois são o mesmo desenho pixel por pixel: 157x84,
com **um único índice de paleta usado, o 255, que é preto**. O nome
`4_PURPLE_WARP` engana; a arte não tem nada de roxo. Aura de chão colorida não
existe neste cliente, e não adianta procurar de novo.

Com isso por escrito, a escolha voltou para quem pediu, e foi o
`4_PURPLE_WARP`: um óvalo escuro de uns três tiles aos pés da Morte. Um
**segundo NPC na mesma célula** da porta, `#aura_do_espectro`, sem fala e sem
rótulo — nome começando em `#` não desenha label, e o corpo é só um `end;`,
então clicar nele não faz nada. O clique na figura da Morte continua caindo
nela, que é alta e está por cima do decalque.

Sprite e não `specialeffect` em laço porque **efeito reinicia a animação a cada
disparo e some no intervalo**; sprite fica parado. O `.act` foi conferido —
âncora (0,0), o desenho nasce centrado na célula, que é o certo para um
decalque deitado, e por isso este não precisou do `levanta_sprite_npc.py`.

### A quebra de linha destes arquivos não é a que o `CLAUDE.md` dizia

O §5 mandava escrever âncora com `\r\n` porque *"esses arquivos são CRLF"*. O
`crianca_de_comodo.txt` e o `corredor_fantasma.txt` são **LF**, as âncoras
casaram zero vezes, e o `assert` parou o script antes de gravar — de graça,
como da outra vez. Medido depois: dos 44 arquivos nossos de `npc/guerra` e
`db/guerra`, **18 são CRLF e 26 são LF**, nenhum misto. O `.gitattributes` tem
`text=auto` com `*.yml eol=lf`, então quem decide é o checkout. A regra subiu
corrigida para o `CLAUDE.md`: **medir antes de escrever a âncora**.

### O que falta ver no jogo

Nada disto subiu. `@reloadscript` pega os três.

O que só a tela decide: se o óvalo preto aos pés da Morte lê como sombra ou
como buraco no chão. Se ficar ruim, o conserto é comentar o
`#aura_do_espectro` — nada mais depende dele.


## O Túmulo do Monarca abre todo dia, e o encantamento fala português (2026-08-12)

Pedido do dono: deixar a instância **Túmulo do Monarca** ativa 24/7, e — na
volta do mesmo pedido — **o encantamento por Pedra Bruta é o ponto**, então a
NPC dele tinha de vir junto.

A instância já existia e já estava ligada: `npc/re/instances/FridayDungeon.txt`,
Id 46 do `instance_db`, mapa `1@md_gef`, com o `.rsw`/`.gnd`/`.gat` conferidos
no nosso `data.grf`. O que ela não era é **alcançável**:

```
.@day = gettime(DT_DAYOFWEEK);
if (.@day != FRIDAY) { ...não entra... }
```

Seis dias em sete, a caçada, os quatro baús, o Monarca Lich, a Pedra Bruta e os
dois encantamentos simplesmente não existiam.

### As três decisões, e por que a segunda arrastou trabalho

Perguntadas e respondidas antes de escrever:

| | rAthena | bRO | Ficou |
|---|---|---|---|
| Espera | 4h corridas | sexta-feira | **nenhuma** (ver abaixo) |
| Nível de entrada | 130 | 99 | **sem trava** |
| Interior em português | — | — | **sim, no mesmo trabalho** |

A espera passou por três formas no mesmo dia, e as duas primeiras duraram
horas: sexta-feira (o bRO) → diária pela quest 12379 → **nenhuma**. O que
decidiu foi ver as chances de encanto na tela: com 0,54% no topo da tabela de
acessório comum, uma corrida por dia transformava o encanto bom em algo
inalcançável.

Sobrou um limite só, e é do próprio sistema de instância: **uma memória aberta
por party de cada vez**. O `instance_create` devolve **-3** nesse caso
(`instance.cpp:630`), e como ele virou o único que o jogador encontra, ganhou
recado próprio em vez de cair no "a reserva falhou" genérico.

O override da 12379 **saiu** do `db/guerra/quest_db.yml` — ele descrevia uma
regra que não existe mais, e documento errado é pior que documento nenhum. O
NPC só a **apaga**, para tirar da janela de missões o registro de quem falou
com a Mariaju nas horas em que a regra valeu; essa limpeza pode sumir quando
ninguém mais tiver o registro.

"Sem trava" custou mais do que parecia. A trava de nível estava em **dois**
lugares: na porta e, de novo, no seletor de dificuldade **lá dentro**
(`if (BaseLevel < 'mob[0])`, com 130 e 200). Tirar só a da porta teria
entregue o pior resultado possível: o personagem entra, e não consegue começar
a caçada. Por isso o seletor também virou nosso — e foi ele que revelou a
armadilha abaixo.

### A armadilha: `disablenpc` não atravessa a clonagem da instância

A receita da §2 do `CLAUDE.md` é sempre a mesma — `disablenpc` no original mais
duplicata nossa. **Para NPC de dentro de instância ela não vale**, e o modo de
falhar é calado.

São dois campos, e só um atravessa:

- o `buildin_disablenpc` (`script.cpp:12388`) chama `npc_enable_target`, que
  mexe em `is_invisible` e `sc.option` e **nunca grava `nd->state`**;
- e é `state`, e só ele, que o `npc_duplicate_sub` copia para a cópia
  (`npc.cpp:4655-4657`).

Ou seja: `disablenpc "Marry Jay#0_1"` num `OnInit` esconde o NPC do **mapa-molde
`1@md_gef`**, onde ninguém entra, e o clone de dentro da instância **nasce
ligado**. Os dois seletores apareceriam empilhados na mesma célula, e o velho
voltaria a recusar quem tem menos de 130.

A saída é o `OnInstanceInit` do nosso seletor, e ela é segura por uma razão que
está escrita no próprio rAthena, com os dois laços um embaixo do outro:

```
// First add the NPCs               instance.cpp:586
// Now run their OnInstanceInit     instance.cpp:593
```

Quando o nosso roda, o clone do velho já existe e já tem nome. A regra subiu
para o `CLAUDE.md` §5.

### A Colecionadora nasceu `duplicate` e virou cópia no mesmo dia

Enquanto a regra do encantamento não mudava, duplicar era claramente o certo. O
`Amateur Collector#pa0829` do rAthena já estava em `gef_tower 57,167` — **a
coordenada exata da Colecionadora do bRO** —, já cobria os dois slots do Anel do
Monarca e já cobrava as 10 Pedra Bruta + 100.000z certas. Mudava o nome e a
língua, e nada mais. Uma linha resolvia:

```
gef_tower,57,167,3	duplicate(Amateur Collector#pa0829)	Colecionadora	1_F_01
```

**E aí veio o segundo print da bROWiki, e ele derrubou o desenho.** A lista de
acessórios que a Colecionadora aceita tem duas metades: "Acessórios Comuns" e
"Acessórios **Especiais**". A do rAthena tem só a primeira — 122 IDs, e
**nenhum** dos especiais. Faltavam os anéis zodiacais, o Anel de Iansã, o de
Oxóssi, as Luvas de Thor, o Keraunos, o Paraíso Perdido: 101 nomes.

E essa lista mora **dentro** do script compartilhado, num `switch` de 122
`case`. Duplicata não estende lista de dentro. Ou se editava o arquivo do
rAthena — proibido pela §2 —, ou o script virava nosso. Virou nosso:
`npc/guerra/colecionadora_do_monarca.txt`.

**Mas virou nosso por programa, não à mão.** O arquivo é fatia de bytes do
FridayDungeon.txt já traduzido: as sete tabelas de encanto, o anti-hack
(`F_IsEquipIDHack`/`F_IsEquipCardHack`) e o menu de acessório vieram byte a
byte. Três coisas mudaram, e o gerador tem `assert` para cada uma:

1. o cabeçalho do NPC — nome em português;
2. o `switch` de 122 `case` virou **`inarray` contra um `.aceitos` de
   `OnInit`** — lista que cresce é dado, não código (§4.11);
3. o `OnInit`, com a lista e o `disablenpc` do original.

A prova de que a cópia é fiel não é um limiar inventado: são os **133 encantos
e os 84 IDs distintos** das sete tabelas, contados dos dois lados e iguais.

### Resolver 101 nomes em IDs, sem inventar nenhum

O print traz nome em português; o script precisa de ID. Como o `item_db` do
nosso vendor já está traduzido, 80 casaram por nome exato. Os 21 restantes
foram um a um:

- **13 existiam, com nome em inglês** — o vendor não traduziu tudo. Os cinco
  anéis zodiacais que faltavam (`Aries_Ring_J`, `Scorpio_Ring_J`,
  `Gemini_Ring_J`, `Libra_Ring_J`, `Pisces_Ring_J`), mais `Emerald_Ring`,
  `Pollux_Ring_J`, `Petal_Tail`, `Shinobi_Sash_H_BR`, `Tip_Of_Thief_Vol2`,
  `Paradise_Lost` e os **dois** `Imperial_Ring` (28372 e 28515, este com sufixo
  `_BR`). Os dois entraram: aceitar um item a mais não quebra nada, e escolher
  errado deixaria o anel do jogador de fora sem explicação.
- **8 não existem no `item_db` inteiro** — não é falta de tradução, é ausência:
  Anel de Carnium, Brincos de Carnium, Colar de Juperos, Luvas de H. Motto,
  Luvas de Thor, Anel de Capricórnio, Amuleto Caolho e Broche do Reino. Ficaram
  de fora, nomeados no cabeçalho do arquivo e no `PENDENCIAS.md`.

**Uma suposição, e está marcada como tal:** "Anel da Colheita" virou o 490272,
que o nosso vendor chama de "Harvest Festival". É o único acessório de colheita
do `item_db`, mas o nome não bate — é o único ID da lista que não foi provado.

Total: **216 aceitos**, os 122 do rAthena mais 94. Cada um conferido como
existente **e** como acessório antes de entrar.

O bRO parte o encantamento em **duas** NPCs (a Colecionadora, para acessório
comum, e o Homem Suspeito em `gef_tower 36,177`, só para o Anel do Monarca); o
rAthena junta as duas, com as mesmas tabelas. Ficou junto — duas NPCs a nove
células uma da outra, com o mesmo preço e o mesmo resultado, só confundiriam.

**Conferido antes de prometer:** o Anel do Monarca (28483) cai a 10% do Monarca
Lich, então o caminho fecha sozinho, sem precisar de item novo.

### A falha do reset parou de destruir o acessório

Visto em jogo no mesmo dia, e o pedido foi imediato: *"não podemos destruir o
acessório na falha; coloque para apenas não dar certo, na mesma chance que já
existe"*.

O rAthena engolia a peça, e a ordem do script é o motivo:

```
delequip .@slot;                       // tira o item
if (rand(100) > .@success) {
        specialeffect2 EF_SUI_EXPLOSION;
        mes "... o acessório foi destruído.";
        close;                         // e nunca devolve
}
```

O `delequip` vem **antes** do sorteio, e o ramo de falha simplesmente não tem
`getitem2`. Agora tem, com os **quatro** slots — o item exato que foi tirado,
inclusive os encantos que se tentou remover. Perde-se só o custo: as 10 Pedra
Bruta e os 100.000z.

**As chances ficaram como estavam** (80% no Anel do Monarca, 20% no resto). O
pedido foi tirar a destruição, não facilitar o reset.

Três detalhes que andaram junto:

- **O aviso na tela mudou junto com a regra.** Ele prometia *"Se falhar, o
  acessório é destruído!"* — texto que teria virado mentira, e mentira em
  vermelho. Agora diz que se perdem as pedras e o zeny, e o acessório fica.
- **A explosão saiu.** `EF_SUI_EXPLOSION` é o efeito de coisa destruída; virou
  `EF_PHARMACY_FAIL`, que é o de operação que não deu certo.
- **Devolver com `getitem2 ...,1,1,0,0,...` passa refino 0**, o que apagaria o
  refino de uma peça refinável. Não apaga nada aqui porque **nenhum dos 216
  aceitos é refinável** — conferido nos 216, não por amostra, e o teste ficou na
  bateria justamente para o dia em que a lista crescer.

**A mudança foi feita no GERADOR, não no arquivo.** O
`colecionadora_do_monarca.txt` é gerado; corrigir só o arquivo faria a próxima
regeneração desfazer tudo, calada. É a quarta troca documentada do gerador, com
`assert` próprio — se o upstream mudar a forma daquele ramo, ele para em vez de
gravar meia troca.

### O acoplamento que a bifurcação criou

O texto do arquivo novo é um **instantâneo** da tradução do grupo `monarca` no
dia em que ele foi gerado. Reaplicar aquele catálogo conserta o
`FridayDungeon.txt` — que agora está desligado — e **não toca** na cópia. Quem
melhorar uma fala da Colecionadora no catálogo mexe nos dois lados, ou regera.

Está escrito no cabeçalho do arquivo, no `scripts_guerra.conf` e no
`ARQUITETURA.md` §4, porque é exatamente o tipo de coisa que falha calada.

### A tradução do miolo

Grupo novo `monarca` no `traduz_npcs.py`, catálogo
`npc/guerra/traducao/monarca.cat`: 205 textos, **188 aplicados**, 0 recusas.

Os 17 em branco são todos técnicos, e cada um quebraria alguma coisa calada:
`Friday Dungeon` (chave de instância), `gef_tower` e `1@md_gef` (nomes de mapa),
`md_gef_mobs_spawn` (nome único de NPC), **`fd_box1`..`fd_box4`** — que o script
compara contra `strnpcinfo(2)`, e traduzir faria os quatro baús pararem de
largar Pedra Bruta —, `null` (o que `getitemname()` devolve sem item) e duas
pontuações soltas.

Um detalhe de português que o inglês não tem: o script monta `"The " + <item> +
" ..."`, e o artigo teria de concordar com o gênero do item (o Anel, **a**
Presilha), que vem de `mesitemlink()` e não dá para saber. Virou **`O item `** —
o núcleo passa a ser "item", masculino, e toda concordância depois dele fecha:
*"O item Presilha foi encantado."*

### O que ficou de fora, e é de propósito

O miolo da instância continua sendo do rAthena, e foi só **traduzido**, não
alterado: os 100 monstros e a reposição, os quatro baús, o cadáver do Estranho,
a Escultura Bizarra e o Monarca Lich.

O Túmulo do Monarca **não** entrou no Teleportador da Ordem (`auction_02
37,39`), que hoje leva às catorze portas das instâncias da Ordem. Seria uma
linha em cada array — e a §4.11 do `CLAUDE.md` existe justamente porque mexer
naqueles arrays já custou os catorze destinos errados uma vez. Fica anotado nas
pendências.

### O que falta ver no jogo

Nada disto subiu — está tudo em disco, e os comandos estão no `PENDENCIAS.md`
§1l.

## Trinta e uma peças de cabeça, e o preço deixou de ser 1 zeny (2026-08-12)

Pedido do dono: 31 equipamentos de cabeça para as três lojas da fileira de
cima do Mercado Contemporâneo — nove no Chapeleiro (topo), quinze no Ocleiro
(meio), sete no Retoqueiro (baixo). A edição da loja foi meia hora; o resto do
dia foi o que veio junto.

### A regra que mudou no meio da rodada

O **Elmo de Aegir (18728)** tem `Buy: 200000` no `item_db`. A 1 zeny na
vitrine, isso é **99.999 de lucro por clique**, em laço — cinco vezes o buraco
da Boina Alada (5170) e maior que o do Ouro (969), os dois fechados na manhã
do mesmo dia. Levado ao dono como "tiro da lista ou ponho mesmo assim?", a
resposta foi uma terceira coisa, e virou regra da casa:

> *"Todo item a partir de agora que tiver valor de venda a gente vende com o
> valor de compra dele."*

É a saída que a Tranqueiras tinha estreado naquela manhã, agora generalizada:
em vez de **podar** a peça cara, **cobra-se** por ela o que o `item_db` diz que
ela vale. A regra está no `CLAUDE.md` §4, regra 16, com a aritmética que a
torna binária — revenda paga `Buy/2`, então qualquer preço abaixo de `Buy`
deixa lucro.

Dos 31, **16 têm `Buy`** e entraram por ele (um a 200.000, um a 10, catorze a
20); os outros 15 não valem nada revendidos e ficaram a 1 zeny. De quebra, os
16 **não** acrescentam linha de `npc_parse_shop: discounted buying price` na
subida — o aviso só sai quando o preço com desconto cai abaixo do de venda com
supervalorização, e no preço de compra isso não acontece.

Não foi aplicada para trás: os `Buy: 20` que já estavam nas nove lojas a 1
zeny continuam a 1 zeny.

### Três IDs vieram com um dígito a menos

E os três foram achados pelo **nome** na tabela do bRO antes de virar linha de
loja. Nenhum dos três números errados existia em tabela nenhuma — o
`estado_item.py` respondeu *"nao esta no rAthena NEM nos 18845 do bRO"* nos
três —, mas dois tinham vizinho plausível:

| pedido | certo | como se decidiu |
|---|---|---|
| `1943` | **19437** Adorno Florido | o 1943 **existe**: é o `Erhu`, uma ARMA de três covas com nome coreano no cliente. Teria entrado numa vitrine de chapéu sem erro nenhum |
| `41009` | **410097** Lacinhos Yin-Yang | o bRO tem **dois** com esse nome — 410096 sem cova, 410097 com. O `[1]` do pedido decidiu |
| `42018` | **420180** Espinha de Brinaranha | `Eis_Spinne`; não havia ambiguidade |

O `[1]` do pedido não era enfeite: bateu com o `Slots` do `item_db` nas 31, e
foi o que desempatou o único caso de nome repetido.

### O que cada peça custou

Dezoito das 31 **não estavam no `itemInfo.lua`** e apareceriam sem nome e sem
ícone na própria vitrine — a mesma lição do 410125, do 410067/410026 e do
410010 das rodadas anteriores, agora em escala: a faixa `410xxx` é nova demais
para o arquivo de 2021. Vieram do bRO pelo `completa_iteminfo.py`, e os `Name`
do servidor, todos em inglês, foram sincronizados pelo `nomes_pt_item_db.py`
(17 trocas, exatamente as esperadas — conferidas uma a uma no `git diff`).

**Três precisaram de arte**, e as três pelo par de sempre
(`estende_accessoryid.py`, porque o View não existia no `accessoryid.lub` de
2021, e depois `instala_visual.py`): Orelhas Fantasmagóricas (410130, View
2226), Lapela Sagrada (420187, View 2337) e Touca Exótica (400308, View 2269).

A **Lapela Sagrada foi o caso invertido, e engana**: era a única das sete do
Retoqueiro **com** nome em português no cliente, e a única das sete **sem**
arte. Nome no `itemInfo.lua` não diz nada sobre arte — são duas tabelas.

### A Touca Exótica (400308) — a única que não existia

Das 31, foi a única fora de todo `item_db`, nosso e do vendor. Entrou como
placeholder em `db/guerra/item_db.yml`, e as três frases de bônus da descrição
do bRO foram **conferidas contra item que o rAthena já tem** antes de virar
`bonus`, em vez de supostas:

| frase do bRO | `bonus` | quem provou |
|---|---|---|
| "Resistência a monstros Normais e Chefes +N%" | `bSubClass,Class_Normal` + `Class_Boss` | 400047 `Runaway_Accelerator`, mesma frase e os dois bônus |
| "Efetividade de cura +N%" | `bonus bHealPower,N` | Carta Lady Branca (4372): descrição "+30%", script `bHealPower,30` |
| "Esquiva perfeita +10" | `bonus bFlee2,10` | 1181, frase idêntica |

Dois detalhes que teriam passado calados: **`DEFM` não é campo de `item_db`** —
o rAthena não tem `MagicDefense` para equipamento, só para elemental, então os
15 viraram `bonus bMdef,15`, que é como as 1212 peças do `db/re/` fazem —, e
`Weight: 600` para o "Peso: 60" da tela, o decimal que estragou cinco entradas
deste arquivo em 2026-08-01.

O conjunto com a Carta Lady Branca (+60% de cura) está em
`db/guerra/item_combos.yml`. `AegisName` e `View` saíram do **cliente**, não de
palpite: `ACCESSORY_Exotic_traditional_Hat` / ClassNum 2269.

### Duas coincidências que não são erro

- **Diadema do Orgulho (410009) e Diadema Arco-íris (18894), as duas no
  Ocleiro, são o mesmo desenho** — View 1019 nas duas, e os `AegisName` só
  diferem pelo `_` do fim. Não é duplicata: a de 410009 tem cova e pede nível
  100, a de 18894 não tem cova e pede 70.
- **Ventinho Bruto (15923) e Gelinho Místico (15922) dividem o View 1262.** É
  do próprio jogo. Os quatro amuletos de elemento (15920-15923) vieram juntos
  de propósito, e cada um fecha conjunto com a capa do mesmo nome no
  `db/re/item_combos.yml` — as capas **não** estão à venda, então quem quiser
  fechar conjunto caça a capa.

### Uma divergência levantada, não resolvida sozinha

O **Véu das Gemas Sagradas (19106)** é `Head_Low` **e** `Head_Mid` **e**
`Head_Top` ao mesmo tempo. Foi pedido como topo, equipa como topo, e está no
Chapeleiro por isso — mas cabe nas outras duas lojas da fileira, e não é
engano vê-lo ocupar outro slot no jogo. Fica dito (regra 14).

### O que falta ver no jogo

Nada disto subiu. Os comandos estão no `PENDENCIAS.md`.

---

## O Cassino de Comodo, e o baralho que mente nos dois sentidos (2026-08-12)

O `cmd_in02` — o mapa de interiores de Comodo — passou a ser um cassino nosso,
a **Casa Rosa**. Dezesseis NPCs em `npc/guerra/cassino_de_comodo.txt`: três
recepcionistas nas portas, quatro garçonetes que oferecem um drink e **sete
mesas de blackjack** que cobram e pagam em Moeda Nova (30998).

### Os dois salões viraram dois andares, e a divisão é nossa

O `cmd_in02` tem dois salões de jogo lado a lado, ligados por dois warps do
rAthena (`168,113 → 63,73` e `187,78 → 84,37`). No arquivo eles não são
andares: estão na mesma altura, `-10,00` nas treze células medidas. A divisão
em "primeiro" e "segundo" é ficção nossa, e o salão **leste** ficou sendo o
primeiro porque é nele que desembocam a porta principal, a porta leste e o
Teleportador da Ordem.

O pedido chegou com os dois invertidos e foi corrigido pelo dono na mesma
conversa. **Valeu ter medido antes**: era o mapa que dizia qual salão é o de
chegada, e a inversão teria posto o jogador no "segundo andar" ao entrar pela
porta da frente.

### A falcatrua — e ela é o motivo de tudo

A decisão do dono foi contar uma história: *"no andar de baixo o jogador tinha
mais chance de ganhar do que o normal, mas os prêmios eram pequenos, o que
fazia ele querer subir para jogar nas máquinas mais caras de cima, onde a
chance estava a favor da casa (bem a favor)"*. O cassino é viciado, e uma quest
futura descobre isso.

O mecanismo é **um número por mesa**. A cada carta comprada rola-se
`rand(100)`; se cair abaixo do viés, a carta não é sorteada — é **escolhida**
do que resta do baralho. Favorecer o jogador é melhorar a mão dele *e* piorar
a do crupiê; favorecer a casa é o contrário.

|  | aposta | 21 natural | viés | ganha | perde | lucro médio |
|---|---|---|---|---|---|---|
| 1º andar (leste) | 2 | 3:2 | 5% pró-jogador | 46,7% | 44,1% | +0,13 moeda/mão |
| 2º andar (oeste) | 10 | 2:1 | 10% pró-casa | 32,3% | 58,9% | −2,31 moeda/mão |

**A isca é o próprio pagamento.** Em cima o 21 natural paga *mais* — 2:1 contra
3:2 — e a aposta é cinco vezes maior. O jogador sobe atrás do prêmio grande e
entra na mesa que drena dezoito vezes mais rápido do que a de baixo enche.

### Por que o número foi medido antes de ser escrito

Porque o viés age nos dois lados da mesa, o efeito dele é **mais que o dobro**
do que o número sugere. Medido: 10% a favor do jogador não dão 10% de vantagem,
dão **+18% de lucro médio**, que é faucet de moeda num servidor de drop 50x.
E 10% parece pouco.

Daí a ferramenta, `ferramentas/simula_blackjack.py`, escrita **antes** do
script e não depois — 80.000 mãos por ponto, espelhando o `S_Compra` linha a
linha. A regra que fica está no LEIAME: mexeu no `S_Compra`, mexe nela, senão
ela passa a medir um jogo que não existe e responde com a mesma cara de
certeza.

Ela também respondeu uma pergunta que não tinha sido feita: **a falcatrua tem
contra-jogo?** Não. Quem desconfia da mesa de cima e para de comprar carta sai
*pior* — −34,5% contra −23,1% —, porque metade do viés age na mão do crupiê,
onde a estratégia do jogador não alcança. Na mesa de baixo vale o contrário, e
também por escolha: parar sempre dá −5,8%, então a mesa boa só paga para quem
realmente joga.

### `rand(1)` não devolve 0 — ele mata o script

O defeito mais caro da rodada, achado na revisão e não em jogo. O sorteio de
naipe chamava `rand(@bj_resta[valor])`, e esse contador vale **1 toda vez que
sai a última carta daquele valor** — o que acontece o tempo todo. O
`buildin_rand` de um argumento faz `maximum -= 1` e recusa `maximum < 1` com
*"range is too small"*, pondo `st->state = END`: a mão morreria no meio, com o
diálogo aberto e a aposta já cobrada.

Subiu para o `CLAUDE.md` §5. O caso perigoso não é a constante — é a
**variável que encolhe** e passa por 1 no fim: cartas que restam, itens que
sobraram, jogadores vivos.

### O estado da mão mora em `@`, e não em `.@`

`callsub` **abre escopo novo de `.@`** — `st->stack->scope.vars =
i64db_alloc(...)`, em `src/map/script.cpp:5508`. Nenhuma subrotina enxergaria o
baralho se ele fosse `.@`. Variável `@` (temporária de personagem) resolve isso
e ainda resolve dois jogadores na mesma mesa ao mesmo tempo — variável `.` do
NPC seria compartilhada e as duas mãos se misturariam, calado.

### O resto da rodada

- **As três recepcionistas** (211,100 / 174,131 / 173,131, sprites 817/816/815).
  A terceira foi pedida em 174,131 também, e duas não cabem na mesma célula —
  foi para a célula ao lado. Fica registrado que o bolsão delas é fechado a
  leste por parede, e que quem chega pelo warp de 178,132 está do outro lado.
- **As quatro garçonetes** (1_F_PUBGIRL, 161,99 / 196,99 / 179,114 / 63,72).
  O drink chama `transform` direto, com os mesmos parâmetros do `Script:` dos
  itens 12658 e 12663 — nenhum item ocupa mochila. Beber de novo troca o
  disfarce sem precisar de código: o próprio `doc/script_commands.txt` diz que
  `transform` duas vezes cancela o bônus anterior. Era a "trava natural" que o
  pedido autorizou usar.
- **`Shalone#cmd` foi desligado** — ele ocupava 178,92, célula pedida para a
  terceira mesa do térreo. Sai por `disablenpc` de fora, com guarda de
  `getnpcid` e `debugmes`, pela receita da §2: o `comodo.txt` continua o do
  rAthena.
- **`npc/cities/comodo.txt` foi traduzido** — grupo `comodo` novo no
  `traduz_npcs.py`, 258 dos 302 textos. Os 44 em branco são nome próprio de NPC
  e o `kafra_07`, que é o `.bmp` do cutin. Nenhuma fala ficou em inglês.

Três nomes próprios saíram da tabela que o jogo lê (regra 4.12) e **dois
contrariaram o script em inglês**: `Paros Lighthouse` é **Farol de Pharos** e
`Sandaruman Fortress` é **Fortaleza de Sanderman** — com E, é assim que o
`mapnametable.txt` do cliente escreve. `Rogue` é **Gatuno**
(`map_msg_por.conf:556`). `Reudelus` ficou em inglês por não estar em tabela
nenhuma.

### O que ficou de fora

A **máquina caça-níquel**, pedida junto e adiada pelo dono — a ideia é
reaproveitar a roleta que o cliente já desenha, a da captura de pet. O sprite
está livre e conferido: 563 (`2_SLOT_MACHINE`). Registrado no `PENDENCIAS.md`
§1m, junto com os cinco NPCs de cadeia de missão que continuam em inglês.

### O que falta ver no jogo

Nada disto subiu — o servidor não foi recarregado. Os comandos e a lista de
conferência estão no `PENDENCIAS.md` §1m.

### Os quatro ajustes da volta (2026-08-12)

O cassino voltou do dono com quatro pedidos, e um deles rendeu investigação.

**A terceira recepcionista foi para 144,100**, não para a célula ao lado de
174,131 onde eu a tinha posto. E o lugar é melhor do que o meu por um motivo
que só aparece na planta: as três portas do primeiro andar têm chegada de warp
em 212,97, 178,132 e **144,97** — e 144,100 fica exatamente três células ao
norte da terceira, o mesmo arranjo da de 211,100. Uma por porta, e as duas de
nicho simétricas.

**A mesa de 92,47 passou a olhar para oeste** (facing 2), a única das sete que
não olha para o sul.

**A vitória agora acende uma animação:** `EF_THROW_MULTIPLE_COIN` (982) na
vitória comum e `EF_LEVEL99_4` (362) no 21 natural, num `specialeffect2` sobre
o jogador. Empate não acende — devolver a aposta não é ganhar.

#### O efeito que o pedido queria, e até onde deu para ir

O pedido apontou o `ui_success_y.tga` do efeito de sucesso da janela de
encantamento. O que se apurou:

- **Ele é alcançável em princípio.** Existe um `ui_enchant_success.str` na mesma
  pasta, e o caminho dele está na tabela de efeitos do exe, encostado em
  entradas de efeito de mundo comuns como o `npc_cane_of_evil_eye_hit.str`.
  `.str` é o formato que o `specialeffect` desenha — não é asset de UI preso à
  janela.
- **O número não sai offline.** A tabela é preenchida por uma corrida de 517
  instruções de 30 bytes no `.text`, cada uma um `push offset "<caminho>.str"`
  seguido de `mov [ebp-4], N`. O `N` é consecutivo e o do nosso alvo é 1100 —
  mas ele é o contador de desmontagem de exceção do compilador, não o número do
  efeito. **A prova custou uma rodada e é o que vale guardar:** cruzando os 517
  nomes da corrida com os `EF_` do rAthena naquele mesmo número, batem **zero**;
  e as âncoras de Summoner (`freshshrimp`, `chattering`, `heat_barrel`) caem
  noutra corrida, com índices 51 a 73, enquanto o rAthena as numera 1098 a 1104.
- **Parou aí de propósito.** Tirar o número dali exigiria rastrear o vetor em
  que o construtor escreve, e vale a regra do `CLAUDE.md` §5 que o
  `ajusta_tamanho_fonte.py` ensinou: verificação offline que passa não é prova
  de efeito. `@effect <n>` in-game responde em uma rodada o que a engenharia
  reversa não respondeu em várias.
- **E há um teto que vale saber:** o servidor não manda efeito acima de 1126.
  `buildin_specialeffect` (`script.cpp:15605`) e `@effect`
  (`atcommand.cpp:6027`) recusam `>= EF_MAX`, e o `EF_MAX` daqui é 1127 —
  enquanto o cliente tem ~1460 efeitos `.str`.

#### Os cinco NPCs de cadeia de missão, traduzidos sem tocar nas cadeias

Decisão do dono: *"vamos traduzir só os NPCs, e não os arquivos todos de suas
missões"*. É a única exceção do acervo à regra de aplicar arquivo inteiro, e o
mecanismo que a torna possível já existia: no `.cat`, tradução vazia quer dizer
"deixa em inglês". Grupo `cassino_missoes` novo, com os quatro arquivos e
**19.625 textos, dos quais 394 traduzidos** — só os de Manzi, dos dois
`Ordinary Man`, do `Man#megin` e do `Strange Guy`.

**A armadilha que quase entregou o recorte errado, e subiu para o `CLAUDE.md`
§5:** no `.cat` o `arquivo#N` não é a linha, é a ordem do literal dentro do
arquivo. O número parece linha e cai na mesma faixa de grandeza, então o
primeiro recorte — "as falas entre a linha A e a B" — devolveu 444 textos e
**passou**. O que denunciou foi o `Man#megin` aparecer com zero: um NPC de 203
linhas mudo não existe. Com a contagem certa deram 353, sendo 59 dele.

**Treze falas curtas ficaram em inglês, e por escolha.** Tradução vale por
texto e não por ocorrência: `Wha...?`, `Hmm...`, `Excuse me.` e irmãs são
compartilhadas com o resto das quatro cadeias, e traduzi-las poria português no
meio de 18 mil falas em inglês. A mais visível é o `Wha...?` na segunda linha
do `Man#megin`.

Três nomes próprios saíram das tabelas do jogo: o `Sobbing Starlight` do script
é o item 7177, que o cliente chama **Fragmento de Luz Estelar** — então a pedra
inteira virou "Luz Estelar" e o pedaço acompanha o item; `Crusader` é
**Templário** (`map_msg_por.conf:563`); e `Niflheim` é **Nifflheim**, com dois
F, que é como o `mapnametable.txt` escreve.

## O Guia de Prontera fala português, e a bandeira do Brasil sobe para o CTRL+1 (2026-08-12)

Quatro pedidos na mesma rodada. Três são de conteúdo e um é de patch de exe.

### CTRL+1 passa a ser a bandeira do Brasil

O pedido: *"CTRL + 1 tem que ser bandeira do Brasil, hoje brasil é CTRL + 6, e
CTRL + 1 é Korea"*.

**O primeiro lugar onde se procura é o errado.** As bandeiras parecem emoção
como qualquer outra, e emoção mora em `data\luafiles514\lua files\emotion\
emotionlist.lub` — que define o `enum` inteiro (`ET_FLAG` = 13,
`ET_BR_FLAG` = 51 e as outras sete) e ainda um `EMOTION_ORDERLIST`. Só que
aquela lista tem **64 entradas e nenhuma bandeira**: ela é a ordem da *janela*
de emoções, e bandeira não aparece na janela. Reordená-la não mexeria em nada.
(O `.lub` do nosso GRF ainda vem com DES e não abre; o do bRO é o mesmo arquivo,
mesma versão, sem DES — foi de lá que saiu.)

**Quem trata CTRL+`<n>` é o exe**, num `switch` de nove casos em
`0x00638950`: `add eax,-0D2h`, `cmp eax,8`, `jmp [eax*4 + 00638B1Ch]`. E cada
caso é uma **cadeia de comparações contra o `<servicetype>` do
`clientinfo.xml`** (o global `[012BF51C]`; `korea`=0 … `brazil`=12, na ordem em
que os nomes estão no `.rdata`) antes de chegar ao "rabicho" que empurra a
emoção. Ou seja a mesma tecla dá bandeiras diferentes conforme o servicetype, e
na maioria deles não dá bandeira nenhuma:

| servicetype | CTRL+1 | CTRL+6 |
|---|---|---|
| `korea` (0) | Coreia | Brasil |
| `brazil` (12) | Brasil | *nada* |
| `america`, `japan`, `thai`… | *nada* | *nada* |

**O `data\clientinfo.xml` daqui diz `brazil` e o jogo se comporta como
`korea`** — o relato do dono bate casa por casa com a linha de cima da tabela.
Não se foi atrás do porquê: qualquer que seja (o `clientinfo.xml` com DES
dentro do GRF, ordem de leitura, patch do NEMO), a saída escolhida é imune a
ele.

**A saída: reapontar a tabela de saltos direto para os rabichos**, pulando a
cadeia de servicetype inteira. São 36 bytes, todos de dados, nenhum de código,
e é seguro porque o rabicho só precisa do `ecx` — que o prólogo carrega **antes**
do salto. Com isso as nove teclas passam a funcionar sempre, e a ordem passa a
ser nossa: a de `korea`, com Brasil e Coreia **trocados de lugar** (CTRL+1
Brasil, CTRL+6 Coreia). Trocar em vez de empurrar a fila foi de propósito —
quem já decorou CTRL+3 continua com Filipinas.

Ferramenta: `ferramentas/ordena_bandeiras_ctrl.py`, com `--verificar`. Ela não
procura nada por endereço fixo — acha a tabela pelo padrão do prólogo e os nove
rabichos pelo padrão dos `push`; os endereços acima são só documentação. **E,
como todo patch de exe deste projeto, `--verificar` dizendo "aplicado" não é
prova de efeito** (§5, "Tamanho da fonte"): quem prova é apertar CTRL+1 no jogo.

### A Máquina ganha dois consumíveis, e a caixa de Guyak muda de cara

Duas linhas novas em `npc/guerra/barters_guerra.yml`, no fim do grupo
"consumíveis" — e são os **primeiros consumíveis avulsos** da gaveta, os
primeiros que não vêm em caixa:

| Item | Preço | O que faz |
|---|---|---|
| 7621 Amuleto de Ziegfried | 5 Moedas | ressuscita quem morre, com HP e SP cheios |
| 12210 Goma de Mascar | 5 Moedas | drop ×2 por 30 minutos |

O Amuleto é `Etc` **e mesmo assim se gasta**: quem o consome é o `pc_dead` no
C++, que o procura na bolsa quando o personagem morre. É a mesma armadilha dos
cupons de estilista e do Ticket de Expansão (`CLAUDE.md` §4.8) — procurar o 7621
em `npc/` não devolve nada, e a conclusão fácil seria que ele não serve para
nada aqui.

Os dois já tinham nome em português e arte completa no `itemInfo.lua`
(`estado_item.py`: "4 de 4 ok"), o que importa porque **a janela de troca
desenha o nome do cliente, não o do servidor** (§4.9).

**Entrar item no meio da lista custou renumerar**: os dois permanentes desceram
de 18/19 para 20/21. É seguro só enquanto nenhuma linha tiver `Stock` — se um
dia tiver, o `Index` vira chave de estoque no SQL e renumerar passa a mexer
nele. Ficou escrito no cabeçalho do YAML.

**E a Cx. Poção de Guyak (30996) trocou de arte**: usava o `resourceName` da
caixa de 20 do bRO (22668), que é a caixa genérica de consumível — igual a meia
dúzia de irmãs na mesma vitrine. Passou a usar o da **própria Poção de Guyak
(12710)**: a caixa tem a cara do que tem dentro. Uma linha na tabela `ITENS` do
`ferramentas/instala_item.py` (`arte_de`), que é o campo que copia
`resourceName` de outro item em tempo de execução.

### O Guia de Prontera, em português e com uma categoria nova

`npc/guerra/guia_de_prontera.txt`, cinco NPCs — as mesmas cinco células dos
cinco `Guide` do rAthena (154,187 na praça e um em cada portão), mesmo sprite
105, mesmo cutin `prt_soldier`.

**Por que arquivo nosso e não tradução por catálogo.** Diálogo do rAthena se
traduz em `npc/guerra/traducao/*.cat`, e foi assim com as cidades e a Kafra.
Aqui não serviria: o pedido não foi traduzir o Guia, foi **mudar** o que ele diz
e **acrescentar** uma categoria que o rAthena não tem. Catálogo troca texto por
texto; não inventa menu. Então vale a receita de sempre (§2) — `disablenpc` nos
originais mais NPC nossa na mesma célula, com o
`npc/re/guides/guides_prontera.txt` byte a byte igual ao upstream.

**São cinco `disablenpc` e não um.** Desligar o `Guide#01prontera` (que exporta
`GuideProntera`) não alcança os quatro `duplicate` dele — a mesma pegadinha do
Mestre das Montarias. Um por linha, no `OnInit`.

As três categorias:

- **Serviços Principais** — nova, e no topo. As três portas que são nossas:
  Centro da Ordem (165,168), Arena de Combate (147,180) e Máquina (167,199).
- **Lugares clássicos** — o antigo "Main Facilities", onze lugares.
- **Mercados e Assistências** — o antigo "Merchants & Helpers", doze. O
  **Hipnotizador saiu e a Mesmerita entrou**: aquela linha só dizia "mudei para
  Izlude" e nem marcava o mini-mapa (o `viewpoint` dele já vinha comentado no
  upstream), enquanto quem reseta habilidade e atributo aqui é a Mesmerita,
  `prontera 144,173`, de graça.

**O menu nasce do catálogo, num laço** — regra 11, a que o Teleportador da Ordem
custou em 2026-08-08. Não há string de menu escrita à mão no arquivo: há seis
colunas paralelas (`.nome$`, `.dono`, `.marcas$`, `.nota$`, `.nav$`,
`.navpos$`), o `select` é montado a partir da primeira, e o `OnInit` compara os
seis `getarraysize` e grita com `debugmes` se saírem de compasso.

Dois detalhes que a tabela obrigou:

- **Coluna opcional usa `"-"` e não `""`.** `getarraysize` de array de texto
  para no último elemento **não vazio**, então coluna terminada em `""`
  encolheria e a conferência de tamanhos passaria a mentir. Pelo mesmo motivo o
  `.dono` numera as categorias de 1 a 3, não de 0 a 2.
- **`.marcas$` é `"x y x y …"`, e o `explode` não limpa o destino** — ele grava
  a partir do índice dado (`script.cpp:17305`), então linha curta depois de
  linha longa herdaria o rabo da outra. Daí o `deletearray` antes de cada
  `explode`.

**Trinta marcas de mini-mapa, ids 0 a 29** — e trinta não é número solto: é o
maior que o rAthena inteiro usa, e quem o usa é justamente o Guia de Prontera de
`npc/re/guides`. Não há limite do lado do servidor; o do cliente não está
documentado em lugar nenhum, então ficou-se no que já se sabe que funciona. Foi
por isso que a Biblioteca e o Criador de Pecopeco perderam a segunda **marca** e
ganharam um segundo **link** (`.nav$`) — link leva ao mesmo lugar, é clicável e
não gasta id. A taverna do sul perdeu a marca de vez: o rAthena marcava as duas
e dizia, na mesma tela, que só a do norte abre.

**Nenhum `mes` começa com espaço** (§5): o recuo dos itens é `"- "`.

### O Guia quebrou no primeiro `@reloadscript`, e por dois motivos independentes

O primeiro teste em jogo, na mesma noite, deu dois sintomas que pareciam um só:
o Guia respondia **em inglês** logo depois do `@reloadscript`, e, ao trocar de
personagem, respondia em português e certo — mas **com a janela de menu em
branco**, só com OK e cancelar. São dois defeitos sem relação um com o outro, e
o log do map-server tinha os dois.

**1. `disablenpc` no nome errado.** *"Attempted to disablenpc a non-existing NPC
'Guide#01prontera'"*. O nome único de um NPC é o que vem **depois** do `::`: o
`npc_parsename` (`src/map/npc.cpp:3674`) põe a metade da esquerda em `nd->name`,
que só serve para desenhar, e a da direita em `nd->exname`, que é a chave do
`npcname_db`. Então o `Guide#01prontera::GuideProntera` se desliga por
**`GuideProntera`**. Os outros quatro são `duplicate` sem `::`, e aqueles quatro
tinham acertado — daí o sintoma: **um** Guia em inglês de pé, empilhado no
nosso, na célula da praça. Quem clicava caía no que estivesse por cima, e por
isso o resultado mudava entre uma sessão e outra. Subiu para o `CLAUDE.md` §5.

**2. `||` não faz curto-circuito.** *"getelementofarray: index out of range
(-1)"*, em `.dono`. A linha era a guarda mais comum que existe:

```
if (.@i == 0 || .dono[.@i - 1] != .@g)
```

O `||` do script do rAthena é o `C_LOR`, um operador de **dois números**
(`script.cpp:3840`) resolvido pelo `op_2num` depois de os dois lados já estarem
na pilha — não há salto como em C. Então `.dono[-1]` é avaliado na primeira
volta, sempre.

O que faz este valer §5 não é o erro, é o **efeito à distância**: o comando
devolve falha, o `OnInit` morre ali, e tudo que ele ainda ia montar — `.topo$`,
`.menu$`, `.ini`, `.fim` — fica vazio. O `select(.topo$)` recebe `""` e o
cliente desenha uma caixa de menu **em branco**. Nada na tela liga a caixa vazia
ao índice `-1`, e o diálogo antes dela funciona perfeitamente, o que empurra o
diagnóstico para o lado errado. Virou `if` / `else if`.

## Os guardiões crescem com a defesa, e dezenove castelos viram campo de treino (2026-08-13)

Pedido do dono: fazer o Guardião Soldado (1287) melhorar **de forma incremental
conforme o investimento do castelo** — redução de dano, velocidade de ataque,
dano e HP. A pergunta que veio junto era se daria para fazer isso com um monstro
só ou se seria preciso "criar alguns tipos de guardião e atribuir um por faixa".

Dá com um monstro só, e a resposta estava no próprio rAthena: o
`mob_spawn_guardian` grava `md->guardian_data->castle` (`mob.cpp:907`), então de
dentro do C++ todo guardião sabe de que castelo é e quanto ele tem de defesa. O
emulador inclusive **já faz** uma versão embrionária disso — o bloco comentado
como *"Strengthen Guardians"* (`status.cpp:2895`) escala HP, DEF, ATQ e ASPD
pela defesa —, só que preso à habilidade de clã Pesquisa de Guardião e com uma
curva que não é a que se queria.

A primeira análise foi entregue falando em **economia**, porque foi a palavra do
pedido; o dono corrigiu na volta — *"você tem razão, o correto é por defesa"* —
e a escala nasceu na defesa.

### A curva, e por que os dois últimos degraus não são iguais

O patamar é `defesa / 10`, de 0 a 10:

| defesa | HP | redução | ASPD | ATQ |
|---|---|---|---|---|
| 0–9 | 5.000.000 | 90% | 180 | 5.000 |
| 10–19 | 10.000.000 | 91% | 181 | 10.000 |
| … | … | … | … | … |
| 90–99 | 50.000.000 | 99% | 189 | 50.000 |
| **100** | 50.000.000 | 99% | **190** | 50.000 |

A defesa 100 rende **só o último ponto de velocidade** porque os outros três já
bateram no teto no patamar 9. Não é esquecimento: é o que o pedido descrevia
(*"do 90 não muda pro 100, limite continua 99"*), e foi a leitura que fez os
seis números dele fecharem ao mesmo tempo. Os quatro atributos seguem a mesma
forma — `base + passo × patamar`, cortada por um teto —, e são os tetos que
desenham a curva.

Os quinze valores estão em `conf/guerra/battle_guerra.txt` e pegam com
`@reloadbattleconf`; HP, ATQ e velocidade só valem no **próximo spawn**, a
redução vale na hora.

### O que não existia, e o que se usou no lugar

**Não há "redução humano" para monstro.** Foi o achado que mudou o desenho: o
`bonus2 bSubRace,RC_Player_Human` é bônus de jogador, e o `battle_calc_cardfix`
não tem ramo para alvo `BL_MOB`. O substituto é o `md->damagetaken`
(`battle.cpp:2072`), que é geral em vez de por raça — dentro de castelo dá no
mesmo, porque quem bate em guardião é jogador — e que é **inteiro em
porcentagem**, o que faz de 99% o teto real. Subiu para o `CLAUDE.md` §5, junto
com as outras cinco armadilhas desta rodada.

**Velocidade de ataque precisou de conversão.** Monstro não tem ASPD; tem
`AttackDelay` (1288 ms no Soldado) e `AttackMotion`. A escala fala 180–190
porque é o número que o jogador conhece, então usou-se a fórmula do próprio
rAthena: ASPD 180 dá 400 ms entre golpes, ASPD 190 dá 200 ms. E **190 é o teto
do emulador**, não uma escolha — o `MAX_ASPD_NOPC` trava o `amotion` de
não-jogador em 100 ms e o `adelay` nunca fica abaixo dele. A escala pedida
terminou exatamente na parede, por coincidência.

Na primeira análise esses dois números foram entregues **pela metade** (200 ms e
100 ms), por ter-se esquecido o `AMOTION_DIVIDER_PC` da conta do jogador. O erro
dobrava o DPS estimado do guardião no topo — 100.000/s em vez de 50.000/s — e
foi corrigido antes de virar código.

### A conta que decide tudo, e quase passou batida

Mapa de castelo tem o mapflag `gvg_castle` **permanente**, e o
`mapdata_flag_gvg2` só olha mapflag: os nossos `gvg_*_attack_damage_rate: 20`
valem lá dentro 24 horas por dia, com ou sem guerra aberta, e valem **também
quando o alvo é monstro**. Então a redução do guardião não age sozinha:

```
dano que entra = bruto × 0,20 (guerra) × (1 − redução do guardião)
```

No patamar 0 isso é 2% do bruto; no patamar 9, 0,2%. Com 5 e 50 milhões de HP,
são **250 milhões** e **25 bilhões** de dano bruto para derrubar um guardião —
vezes oito por castelo. Foi levada ao dono como ressalva antes de qualquer
linha ser escrita: defesa 100 torna um castelo matematicamente inconquistável.
Ele aceitou justamente por isso, porque os castelos que vão receber defesa 100
não têm Emperium.

O lado bom da mesma propriedade é o teste: como o mapflag não depende da guerra,
o número medido numa terça à tarde é o número da guerra de domingo.

### Os dezenove castelos-museu

Decisão do dono: o servidor começa com **um** castelo conquistável, o Kriemhild
(`prtg_cas01`), cuja defesa e economia continuam sendo as que a guilda dona
investir — este trabalho não encosta nele. Os outros dezenove da Guerra do
Emperium 1 viram campo de treino: defesa 100, oito guardiões cada, sem
Emperium, sem dono, sem nada.

Duas peças, e a primeira foi uma surpresa:

**O rAthena não invoca guardião em castelo sem dono.** No `OnAgitInit` do
`agit_main.txt`, castelo com `CD_GUILD_ID == 0` cai num `killmonsterall` e ganha
Evil Druid, Khalitzburg e companhia; o `OnSpawnGuardians` só existe no ramo do
castelo COM dono. Por isso existe `npc/guerra/guardioes_dos_castelos.txt` — um
NPC só, em `prt_gld 136,66`, ao lado da entrada do Kriemhild, com o sprite
`EP17_2_GUARDIAN_PARTS`. Um NPC basta para os dezenove porque o comando
`guardian` recebe o mapa como argumento.

**Desligar as dezenove linhas em `npc/scripts_guild.conf`** tira Emperium,
Kafra, Gerente, alavanca, baú e bandeiras de uma vez, porque cada um daqueles
arquivos é só um punhado de `duplicate` do `agit_main.txt`. Era a condição que o
dono pôs — *"vamos fazer apenas se for comentar algumas poucas linhas"* —, e é
exatamente isso. A Guerra do Emperium 2 (os dez castelos de `guild2`) ficou
intocada: *"vamos começar com a 1.0 primeiro"*.

Os guardiões são invocados **sem índice**, ou seja temporários. Não é economia
de digitação: com índice eles ocupariam os slots `CD_ENABLED_GUARDIAN` e
passariam a ser alcançados pelo `mob_guardian_guildchange` (`mob.cpp:3690`), que
**apaga guardião de castelo sem dono** — o sumiço viria calado na primeira vez
que alguém tocasse na dona do castelo. O preço é não ter respawn automático, e
daí o temporizador de um minuto que confere os 152 lugares por `unitexists()`.

O caminho óbvio para a reposição seria o rótulo de morte, e ele foi descartado
por um motivo concreto: responde "morreu um" sem dizer **qual**, e o `killedgid`
que resolveria isso é parâmetro de jogador — guardião morto sem matador anexado
não voltaria, e a falha seria calada.

### A armadilha que o enxerto em C++ quase criou

O `status_calc_mob_` tem uma porta de saída logo no começo: sem nenhuma flag
ligada ele **libera o `md->base_status`** e passa a apontar para o status
compartilhado do `mob_db` (`status.cpp:2812`). O bloco `flag&4` do rAthena só
liga com a habilidade Pesquisa de Guardião, então um guardião comum não teria
`base_status` próprio — e o nosso ajuste, escrito depois daquela linha, teria
alterado **todos os guardiões do servidor de uma vez**, calado, e sobreviveria
até o próximo `@reloadmobdb`.

A saída foi **acrescentar** um `flag|=4` ao lado do do rAthena em vez de mexer
no que já estava lá; o enxerto é uma adição, não uma substituição, e por isso
sobrevive a um merge do vendor. As duas chamadas em `status.cpp` estão na tabela
do `CLAUDE.md` §2.

### A subida, e a rodada dupla que virou uma

O dono fechou o cliente e mandou terminar; o map-server foi linkado
(`map-server.exe` de 01:55) e os quatro servidores subiram.

A primeira subida acusou uma coisa que não era erro mas atrapalhava: **16 avisos
de `mob_spawn_guardian` por mapa**, em dois blocos separados por três segundos —
o `OnInit` montava os 152 e o `OnAgitInit` derrubava e refazia. O resultado
final estava certo (é para isso que o `OnAgitInit` refaz: no `OnInit` a defesa
lida ainda é 0, porque o char-server não entregou os dados de castelo), **mas
não havia como provar de fora do jogo que a limpeza do meio tinha funcionado**.
Dezesseis avisos por mapa tanto podem ser "montou, limpou, montou" quanto
"montou duas vezes e empilhou".

O `OnInit` passou a só limpar, e quem monta é o `OnAgitInit` (subida) ou o
temporizador (depois de um `@reloadscript`, que não dispara `OnAgitInit`). Custa
até um minuto de mapa vazio depois de um reloadscript, e compra uma conferência
que se lê no log sem entrar no jogo. Na subida seguinte:

```
avisos de guardiao: 152    mapas: 19    todos com 8: True
kriemhild presente? False
```

Junto vieram `Unknown syntax` zero (o cabeçalho de 100 linhas passou) e nenhum
`debugmes` da conferência de colunas — ou seja, as dezenove tabelas de posição
têm as quatro colunas com 152 elementos. Os quatro `[ Error ]` da subida são os
de sempre, do `item_db.yml` (chicote e instrumento musical), e não têm relação
com isto.

O `S_Defesa` ganhou um `if` no mesmo passo: sem ele o temporizador mandaria
dezenove gravações de dado de castelo ao char-server **por minuto, para
sempre**. O `GetCastleData` lê a memória do map-server e não custa pacote, então
em regime a função passou a ser de graça.

### A revisão, na mesma noite: o teste em jogo cortou dois dos cinco números

O dono foi ver e voltou com duas frases que valem mais que a análise toda:
*"a redução ficou realmente abissal"* e *"eles só não ficaram monstros
aniquiladores pois deram muito miss"*.

Foram **duas revisões**, as duas com ele olhando o resultado em jogo entre uma e
outra. A escala final:

| | 1ª (tarde) | 2ª | 3ª (final) |
|---|---|---|---|
| HP no topo | 50.000.000 | 50.000.000 | **15.000.000** |
| redução no topo | 99% | 50% | 50% |
| ASPD | 180→190 | 175→185 | **168→178** |
| precisão | — | 450→550 | **530→630** |
| **dano bruto para derrubar um guardião** | **25 bilhões** | 500 milhões | **150 milhões** |

A primeira revisão cortou só a redução (de 90–99% para 5–50%, +5 por patamar) e
deixou HP e ATQ onde estavam; a segunda trouxe o HP para 5–15 milhões, um por
patamar, e desceu a velocidade mais um degrau. Do primeiro número ao último, a
durabilidade caiu **167 vezes** — e ainda são 150 milhões de dano bruto vezes
oito guardiões por castelo.

**A lição que ficou escrita nos dois arquivos:** a redução é a alavanca
**não-linear** e o HP é a linear. Sair de 50% para 90% de redução multiplica a
durabilidade por cinco; de 90% para 99%, por mais dez; triplicar o HP triplica.
O aviso de que a redução era o eixo errado estava na entrega original e não
bastou — porque a tabela de 90 a 99 **não parece absurda quando se olha para
ela**. Só a conta de "quanto dano bruto derruba isto" mostra a ordem de
grandeza, e é ela que precisa estar na conf, não a tabela de porcentagens.

### O miss não era pouca precisão: era o piso do emulador

Este foi o achado da revisão. No renewal a chance de acerto é literalmente
`hit − esquiva`, em pontos percentuais, travada entre `min_hitrate` (5) e
`max_hitrate` (100) — `battle.cpp:3289-3341`, onde a taxa base do renewal é
**zero** e a única coisa somada é aquela diferença. E o `hit` de monstro é
`nível + DEX + 150`:

| guardião | hit | contra esquiva ~385 |
|---|---|---|
| Soldado (1287) | 309 | −76 → **5%**, o piso |
| Cavaleiro (1286) | 386 | +1 → **5%**, o piso |
| Arqueiro (1285) | 422 | +37 → 37% |

Dois dos três estavam batendo no **mínimo absoluto do emulador**. Não era "pouca
precisão", era o chão — e explica por que o dono nomeou o Soldado.

O pedido foi *"eu chutaria em uns 100 pontos"*, somados. Não serviria como
somatório: as três bases diferem em 113 pontos, então os mesmos +100 deixariam o
Soldado em 24% e os outros dois em 100% contra o mesmo alvo. A precisão entrou
**absoluta**, e a linha joga fora o `nível + DEX + 150` de propósito — os três
guardiões da mesma escala acertam igual. Ficou em 450→550, e na revisão seguinte
subiu mais 80, para **530→630**.

**O que não foi medido, e está dito nos dois lugares:** a esquiva de verdade dos
jogadores deste servidor. Os 530 saem da faixa pedida somada aos 80 que ele
mandou acrescentar depois de ver em jogo — não de conta. Com a fórmula sendo uma
subtração travada em 5 e 100, cem pontos cobrem a escala inteira, então este é o
número da escala com mais chance de ainda estar errado. Calibra-se olhando a
Esquiva na janela de status e somando a chance desejada, não por tentativa e
erro.

### O que ainda falta, e só se vê em jogo

O log da subida com a escala revista fechou igual — 152 avisos, 19 mapas, oito em
cada, Kriemhild fora, zero `Unknown setting` (as dezoito opções foram aceitas).
Ele **não** prova que a escala pegou, que o sprite do Zelador desenha, nem
quanto dano um golpe tira. Está no `PENDENCIAS.md` §1o.

## O horário da guerra: quinta e domingo, só o Kriemhild (2026-08-13)

Fechando a rodada dos guardiões, o dono definiu quando a Guerra do Emperium
abre:

| dia | de | até |
|---|---|---|
| quinta-feira | 20:00 | 22:00 |
| domingo | 18:00 | 20:00 |

Horário de Brasília, que é o do relógio desta máquina — o `gettime` do script lê
a hora local do map-server, sem conversão. Conferido: `E. South America Standard
Time`, UTC−03:00.

O `npc/guild/agit_controller.txt` do rAthena (terça e quinta 21–23, sábado
16–18) foi desligado em `npc/scripts_guild.conf` e substituído por
`npc/guerra/horario_da_guerra.txt` — a receita de sempre da §2: comentar a linha
do original e pôr a nossa cópia ao lado.

Três diferenças além do horário:

- **Os avisos são em português**, e falam **só do Kriemhild**. O original
  percorre os vinte castelos e anuncia cada um; anunciar "castelo desocupado"
  dezenove vezes seria ruído e mentira ao mesmo tempo — aqueles dezenove são
  campo de treino sem Emperium, não estão em disputa.
- **Sem `||` encadeado.** O original monta as condições de dia e hora com `||`,
  que no script do rAthena não faz curto-circuito (`CLAUDE.md` §5). Aqui são
  `if` aninhados.
- O rótulo `OnClock2000` **vale por dois**: é o começo da quinta e o fim do
  domingo. Quem separa é o `gettime(DT_DAYOFWEEK)`.

**Não há lista de castelos no arquivo de horário, e é de propósito.** O
`AgitStart` é global — dispara `OnAgitStart` em todo NPC que tenha o rótulo.
Quem limita a guerra ao Kriemhild é o `npc/scripts_guild.conf`, onde as outras
dezenove linhas estão comentadas: sem o arquivo do castelo não existe
`Agit#<castelo>`, logo não nasce Emperium e não há o que conquistar. Uma segunda
lista aqui divergiria da primeira mais cedo ou mais tarde, e a divergência não
daria erro — é exatamente o padrão da regra §4.11.

Para pôr outro castelo em guerra, portanto, basta descomentar a linha dele lá;
ele passa a responder a este mesmo horário sozinho. Convém tirar o mapa do
`guardioes_dos_castelos.txt` no mesmo passo, senão os guardiões de defesa 100
ficam por cima dos guardiões de verdade.

A Guerra do Emperium 2 (`guild2`) tem o próprio controlador
(`npc/guild2/agit_start_se.txt`) e continua intocada.

## As bandeiras voltam, e todas hasteiam o emblema do Kriemhild (2026-08-13)

Desligar os dezenove castelos em `npc/scripts_guild.conf` tirou muito mais que o
Emperium. Cada arquivo de castelo do rAthena define **também as bandeiras dele**
— quatro do lado de fora no feudo, doze dentro do castelo e uma na cidade
correspondente. Dezenove arquivos comentados levaram **279 bandeiras** junto, em
27 mapas, e o dono percebeu na tela antes de qualquer log acusar. Nada no
servidor reclama de bandeira que some.

A pergunta dele foi a certa: *"elas eram atreladas ao castelo
necessariamente?"*. **Não.** O que prende uma bandeira a um castelo é **uma
linha** — o `FlagEmblem GetCastleData("<mapa>", CD_GUILD_ID)` do rótulo de
atualização. O resto é um NPC de sprite 722 parado numa célula. Trocar o mapa
dentro daquele `GetCastleData` basta para a bandeira passar a hastear outro clã.

Foi o que se fez em `npc/guerra/bandeiras_do_feudo.txt`: as 279 leem
`prtg_cas01`. Quem tomar o Kriemhild passa a ter o emblema em Al De Baran,
Geffen, Payon, Prontera e nos quatro feudos, de uma vez.

**As posições não foram digitadas** — são extraídas dos próprios dezenove
arquivos do rAthena pelo gerador, então as bandeiras voltaram exatamente onde a
Gravity as pôs, e uma mudança do upstream aparece ao regerar.

### A armadilha da extração: nome de NPC pode ter espaço

O primeiro regex cortava o nome com `\S+` e devolveu **219 bandeiras em vez de
279** — sem erro, sem aviso, e com um número plausível demais para levantar
suspeita. Os cinco castelos de Payon chamam as bandeiras de `Bright Arbor#1-2`,
com espaço no meio, e sumiram **inteiros**: cinco arquivos zerados numa listagem
onde todos os outros catorze traziam número. Só a coluna de zeros denunciou.
Corta-se por TAB, que é o separador de verdade.

### Um bug do rAthena que ficou consertado de lambuja

O `donpcevent "::OnRecvCastlePt01"` — o evento que manda as bandeiras se
atualizarem — só é chamado no ramo do castelo **com dono** do `OnRecvCastle`
(`agit_main.txt`). Quando o clã dono se desfaz, o `OnGuildBreak` põe o
`CD_GUILD_ID` em 0 e chama o `OnRecvCastle`, que dessa vez cai no ramo do
castelo vazio e **não avisa bandeira nenhuma**. No rAthena puro elas ficam com o
emblema do clã morto até o servidor reiniciar.

O `ControleDasBandeiras`, um NPC sem mapa no mesmo arquivo, confere o dono a
cada dez segundos e só acorda as 279 quando o número **muda**. É barato de
propósito: lê `GetCastleData`, que é memória do map-server, e compara um inteiro
— só gasta o `donpcevent` quando há o que dizer. O `.dono` começa em `-1` e não
em `0` porque `0` é um valor legítimo (castelo sem dono), e começar nele faria a
primeira conferência achar que nada mudou.

### O que as nossas não têm

O atalho de voltar ao castelo que as bandeiras de fora do rAthena oferecem ao
membro do clã dono. Aquilo é uma porta de entrada, e 279 portas para dentro do
Kriemhild seria outra coisa. Quem quer o atalho usa as bandeiras do próprio
Kriemhild, que continuam de pé — `prtg_cas01.txt` nunca foi desligado.

## A Arena de Prontera perde o anti-conluio, e o placar desce cinco casas (2026-08-13)

Quatro pedidos numa tacada só, todos sobre a arena de PvP: o nome do mapa, a
regra de pontuação, o sprite da porta e o lugar da placa. **Três vingaram** — o
sprite foi trocado, visto na tela e devolvido ao que era, no mesmo dia.

### O nome: "PvP Sala Bússola" virou "Arena de Prontera"

O `pvp_n_1-5` é uma das cinco salas numeradas de PvP do kRO, e a que abrimos é
a única com porta no servidor. O nome de origem não dizia isso a ninguém.

**Não há nada disso no servidor** — o nome é do cliente, e mora em duas metades
que o jogador lê em momentos diferentes: o `mapnametable.txt` (canto do
minimapa) e o `signName.mainTitle` do `mapInfo_*.lub` (o letreiro grande da
entrada). Era **o letreiro** que dizia "PvP Sala Bússola" ao atravessar a
porta, e trocar só o `displayName` teria deixado metade do nome velho na tela.

As duas metades são **geradas** por `ferramentas/traduz_ptbr.py mapas mapinfo`
a partir do bRO, então a mudança entrou pela tabela `NOSSOS_MAPAS` de dentro da
ferramenta — que agora tem dois mapas, o `auction_01` e este. Editar os
arquivos à mão teria funcionado e voltado ao nome do bRO na rodada seguinte,
calado. O acoplamento está no `ARQUITETURA.md` §4.

Os `mapInfo_*.lub` gerados passaram pelo `luac.exe -p` do ROenglishRE. Os
mesmos 215.458 bytes de antes, por coincidência aritmética: o `displayName`
encolheu um byte e o `mainTitle` cresceu um.

### A regra: o anti-conluio saiu inteiro

Até hoje um saldo por **par de contas por dia** (tabela
`guerra_pvp_confronto`, preso em ±2) travava revezamento no terceiro golpe.
Saiu por pedido — *"por enquanto as pessoas podem ficar criando char ou até
conta pra isso, mas vamos observar primeiro"*. Não há mais teto por par, nem
janela de 24 horas, nem espera entre uma morte e a seguinte.

O que **ficou**, e é o que o pedido listou:

| regra | como está |
|---|---|
| nível máximo dos dois lados | `.Nivel = 200`, sem mudança |
| o matador só pontua se o morto tinha 0 ou mais | `.Piso = 0`, sem mudança |
| o morto perde ponto até -10, e daí não desce | **novo**: `.PisoQueda = -10` |
| toda morte vira anúncio | sem mudança — o `announce` já vinha antes das travas |

**O achado da rodada foi que uma dessas regras já estava escrita e não
existia.** O cabeçalho de `honra_de_combate.txt` prometia, desde 2026-08-08,
que *"quem cai abaixo de zero para de valer para o matador, mas continua sendo
alvo: morrer ainda tira ponto dele"* — e o código fazia outra coisa: um
`if (.@pontos_morto < .Piso) end;` saltava **as duas** pontuações de uma vez.
Quem estava negativo parava de perder ponto. Agora o ganho do matador é que é
condicional, e a queda do morto não.

O piso de -10 **não é escolha nova**: o `Minimum: -10` do `Id 5` em
`db/guerra/reputation.yml` já travava o modal ali desde sempre (o
`set_reputation_points` passa por um `cap_value`, `script.cpp:27229`). Sem o
piso do lado do SQL, a tabela desceria abaixo de -10 e o modal ficaria parado —
as duas metades da pontuação discordando, caladas, e a placa mostrando um
número que o jogador nunca vê. Por isso ele foi para o `UPDATE`, e não para um
`if` do script: o valor novo tem de sair da **mesma expressão** que soma o
delta, senão duas mortes simultâneas leriam o mesmo total antigo.

A expressão foi conferida no MariaDB de verdade antes de valer, com as seis
combinações que importam:

```
GREATEST(5 + 1, -10)   = 6     GREATEST(-9 + -1, -10)  = -10
GREATEST(0 + -1, -10)  = -1    GREATEST(-10 + -1, -10) = -10
```

Nenhuma das duas linhas que existem hoje no `guerra_pvp_placar` está fora do
piso — as duas estão em zero —, então não houve migração de dado.

**A Caveira Humana perdeu o teto junto.** Ela é moeda (a descrição da Moeda
Nova promete trocá-la), e a condição "a morte precisa pontuar" incluía o
anti-conluio. Hoje quem segura é só a regra do `.Piso`: um alvo vale caveira
enquanto estiver em 1 ou mais, e cada morte o empurra para baixo. Uma conta
descartável rende **uma** caveira e **um** ponto, e só volta a render se
alguém lhe devolver pontuação. É freio, não é teto — está por escrito no
cabeçalho e no `scripts_guerra.conf`.

A tabela `guerra_pvp_confronto` saiu do `sql-files/guerra_arena_pvp.sql` e
continua no banco, sem ninguém escrever nela. O `DROP` está no comentário do
arquivo para quem quiser limpar.

### O sprite e o lugar

A porta trocou de cara e **voltou atrás no mesmo dia**. Saiu do `10028`
(`4_M_DEATH`, que era o sprite desde 2026-08-12) para o `10029`
(`4_GHOST_STAND`), o espectro de pé; foi visto na tela e reprovado — *"ficou
ruim"* —, e voltou ao `10028` horas depois. O facing nunca se mexeu: **6
(leste)** desde 2026-08-12.

Não houve defeito técnico nenhum no espectro: as duas conferências da regra
passaram para ele (`JT_4_GHOST_STAND = 10029` no `npcidentity.lub` **deste**
cliente, e `4_ghost_stand.spr`/`.act` no `data.grf`) e ele desenhou. Foi gosto.
A ida e a volta ficaram escritas no cabeçalho do arquivo justamente por isso —
sem o registro, a próxima pessoa que achar o espectro bonito refaz a rodada
inteira.

**O que sobrou de aproveitável foi uma armadilha de ferramenta**, e ela subiu
para o `CLAUDE.md` §5: os dois arquivos de arte do `4_ghost_stand` saem como
**"DES"** no `ferramentas/grf.py` — o bit de cifra da entrada —, e ler isso
como "o cliente não tem o sprite" **reprova sprite bom**. A prova de que é
falso negativo estava na própria tela o tempo todo: o `4_m_death` é DES do
mesmo jeito e desenha desde 2026-08-12. O que prova presença é o nome estar na
tabela do GRF (`grf.py <grf> find <padrão>`), não o extrator devolver bytes.

O **Placar da Arena** desceu de `prontera 152,187` para **`142,180`**, a
terceira casa dele. A célula foi conferida no `.gat` deste cliente (tipo 0,
andável) e a vizinhança, no `npc/`: o NPC ligado mais próximo é o `Clan Helper`
do rAthena em `138,183`, quatro células fora. O `Lottery` (141,182) e o `Stock
Market` (140,181) de `npc/custom/` cairiam em cima, e os dois estão comentados
no `scripts_custom.conf` — não nascem.

A placa e a porta agora dividem a fileira `y=180`, cinco células uma da outra.
A frase do ramo "placa limpa", que dizia *"a arena fica duas células a leste
daqui"*, virou **cinco** — era uma promessa errada desde 2026-08-08.

## O Rolinho de Arroz — o prêmio de guerra que cura tudo (2026-08-13)

Pedido do dono: um item chamado **"Bolinho de Arroz"**, cópia do que o bRO
tinha — cura 100% de HP e SP, prêmio de guerra, **sem tempo de recarga**. Com
duas condições ditas junto: se o item do bRO não fosse achado, criar o nosso
com a arte do **555**; e se o nome já existisse, criar o **"Rolinho de Arroz"**.

As duas condições dispararam, e por motivos independentes.

### O nome estava ocupado três vezes

`Bolinho de Arroz` não é o nome de um item deste cliente — é o nome de **três**:
o **555** (`Rice_Cake`), o **564** e o **7613** se chamam todos assim no
`itemInfo.lua`. Um quarto tornaria a busca da bolsa inútil justamente para o
item que o jogador mais vai procurar no meio da guerra. Valeu a alternativa
combinada no pedido: **Rolinho de Arroz**, que não aparece em nenhuma das
26.972 entradas.

### O item do bRO existe, e não é o 555

A busca por `percentheal 100,100` no `db/re/` devolveu 17 consumíveis. O que
casa com a descrição do pedido — prêmio de guerra, sem recarga — é o **14524**
(`Superb_Fish_Slice`, que o cliente chama de *"Biscoito de Arroz"*), um dos três
consumíveis de guerra do bRO: **14522** cura 100% de HP, **14523** cura 100% de
SP e o **14524** cura os dois. Os três têm peso 10, as mesmas sete travas de
comércio e **nenhum bloco `Delay:`**.

Ou seja o pedido conflacionava duas coisas: a **mecânica** que ele lembrava é a
do 14524, e o **nome** que ele lembrava é o do 555 — que cura `rand(105,145)` de
HP e nada de SP. O item novo copia os números do 14524 e o desenho do 555, que
é o que o nome pedido descrevia.

### A ausência de `Delay:` é a decisão cara

Os outros três 100/100 alcançáveis no servidor — Fruto de Yggdrasil (607),
Tônico Dourado (12858) e Sorvete de Melão (23322) — dividem o grupo
`Reuse_Limit_F`, e são **os únicos quatro itens do jogo inteiro** a usá-lo:
usar um trava os outros por 5s. O Rolinho fica fora do grupo, a pedido. É cura
total sem recarga, e vale enquanto durar a pilha — quem for calibrar PvP olha
aqui primeiro.

### O que ficou de pé

| Camada | Onde |
|---|---|
| servidor | `db/guerra/item_db.yml`, **30994** `Rolinho_De_Arroz` |
| cliente | `itemInfo.lua`, via a tabela `ITENS` do `ferramentas/instala_item.py` |
| arte | `arte_de: 555` — `estado_item.py --id 30994` dá **"4 de 4 ok"** |

`Type: Healing`, `Weight: 10` (1,0 na tela), sem `Buy`, e as sete travas do
14524 na ordem dele: `NoDrop`, `NoTrade`, `NoSell`, `NoGuildStorage`, `NoMail`,
`NoAuction`, `NoCart`. O armazém **pessoal** fica liberado de propósito —
consumível de guerra tem de caber na Kafra entre uma guerra e outra, ao
contrário do troféu da arena (30995), que leva `NoStorage` a mais.

O `NoDrop` não é só temático: é ele que impede o `getitem` de largar o prêmio no
chão da guerra quando a mochila do vencedor estiver cheia (`CLAUDE.md` §5).

**Falta quem o entregue** — nenhum NPC o paga. Está em `PENDENCIAS.md`.

### Um achado de lambuja, e ele é sobre a loja

A mesma varredura mostrou que o **`[MEGA] Elmo de Fafnir` (400177)**, à venda no
Chapeleiro do Mercado Contemporâneo **a 1 zeny**, traz
`autobonus3 { percentheal 100,100; … },1000,1000,"RK_REFRESH"` — cura total de
HP e SP a cada Refresh, para Cavaleiro Rúnico, com recarga de 1s e fora do
grupo `Reuse_Limit_F`. Era, até hoje, a **única** fonte de cura 100/100
acessível por loja no servidor. Levantado por escrito, não mexido — é decisão
do dono, pela regra §4.14.

## A Sala Secreta da Ordem, e o Álbum que não existia (2026-08-13)

Pedido de cinco NPCs num canto de `prt_in`: dois guardas dizendo "Fechado", um
Guardião da Sala, uma **Roleta Mágica** que sorteia por 10 Moedas e uma
**Máquina Especial** que troca sete consumíveis por Moeda Nova.

Quatro coisas do pedido não fechavam sozinhas, e três viraram pergunta ao dono
antes de qualquer linha ser escrita.

### As células, e a que não existe

As quatro coordenadas do pedido foram lidas no `map_cache` — as quatro são tipo
0, andáveis. `prt_in` está no **`db/re/map_cache.dat`**, o do meio dos três, e
não no grande (`CLAUDE.md` §5).

A leitura da região inteira mostrou o desenho: um salão de `x120-139` entre
`y104` e `y116`, com **quatro alcovas** em cima (`y117-123`) e um beco ao sul
que termina em parede. Os dois guardas ficam no fundo da segunda e da terceira
alcova; o Guardião e as máquinas, no salão.

**E mostrou que o lugar não tem entrada.** Nenhum warp e nenhum NPC de todo o
`rathena/` aponta para lá — varredura por `prt_in,1[0-3][0-9],1[01][0-9]`, nos
dois sentidos, zero linhas. Levado ao dono, a resposta foi "só os NPCs, sem
porta". Está em `PENDENCIAS.md` §1q.

### As duas máquinas estavam na mesma célula

O pedido pôs a Roleta **e** a Máquina Especial em `136,114`. O rAthena aceita
dois NPCs na mesma célula — não dá erro nenhum —, mas os sprites empilham e o
clique pega um dos dois sem que ninguém escolha qual. A Máquina Especial foi
para **`137,108`**, escolhido pelo dono.

Na mesma volta ele corrigiu o facing das máquinas: **oeste** (2), não leste. Os
três NPCs de fala ficaram em leste (6), como pedido — e **isso não sobreviveu ao
primeiro teste em jogo**, ver abaixo.

### O facing que só a tela reprovou

Subiu tudo, funcionou, e a única correção que voltou foi de olhar: os dois
Guardas e o Guardião da Sala apareceram **de costas** para quem chega. O dono
descreveu exatamente o que a tabela do projeto promete — *"hoje eles estão para
a diagonal nordeste"* — e pediu **sul**. Os três foram de **6** para **4**.

Não foi defeito do facing: `6` (DIR_EAST) desenha para **cima-direita** com a
câmera padrão, e a tabela medida no cabeçalho do `maquina_de_sombrios.txt` já
dizia isso. O que o episódio ensina é outra coisa, e vale para todo NPC de fala:
**ponto cardeal do enum e direção na tela são coisas diferentes, e para quem
conversa com o jogador o que importa é a segunda.** As duas máquinas não
mudaram — elas já tinham sido corrigidas para 2 (oeste) antes de subir, e em 2
estavam certas.

Fica também o contraste com a porta da Arena de Combate, que está em 6 desde
2026-08-12 e foi aprovada: lá o NPC é cenário na beira de uma rua, aqui são três
figuras no fundo de um salão que o jogador atravessa de frente.

### A saída, e o raio que não podia ser 1,1

No mesmo dia o dono pediu a porta de volta: `prt_in 128,103` → **`auction_01
192,85`**, o Centro da Ordem. O destino tem razão de ser — esta era a sala
secreta **daquele** salão, então a saída dá lá e não na rua.

A célula passou por dois valores. Nasceu em `180,52`, o corredor de chegada, por
ser o desembarque já provado do portal da praça de Prontera; o dono trocou para
`192,85` na volta, e é melhor por duas razões que só ficaram visíveis depois:
`192,85` é a **quina nordeste do salão**, então quem sai da sala secreta aparece
atrás de todo mundo e não na porta da frente — que é o que uma passagem secreta
faz; e ela está **longe dos dois únicos warps do mapa**, enquanto `180,52` ficava
a três células do `centro_ordem_saida` e dependia de uma folga de uma célula em
`y51` para o jogador não ser sugado de volta para Prontera ao dar um passo.

A célula foi conferida no `map_cache` (`auction_01` mora no `db/map_cache.dat`,
o grande) e está livre de NPC — os dois mais próximos são Guardas, a quatro
células a oeste e duas a leste.

**A entrada continua não existindo, e é de propósito:** vai ser feita por quest,
em outra sessão. Até lá o caminho é de mão única — entra-se com `@warp`, sai-se
pela porta. O que mudou é que **ninguém fica preso**, que era o risco enquanto
não havia saída nenhuma.

O raio foi a única decisão de verdade. Todas as outras portas do projeto são
`1,1`, e aqui esse valor seria **defeito**: o nicho do sul é um retângulo de 6×2
(`x126-131`, `y102-103`) pendurado na beirada do salão, que começa em `y104` —
com raio 1 na altura, o gatilho pegaria três células do salão e teleportaria
quem só estivesse passando rente à parede sul.

Ficou **`3,0`**. O `ys = 0` segura o gatilho na fileira do nicho; e o `xs = 3`
cobre a boca inteira por um efeito de borda que vale registrar: ele pede `x125`
a `x131`, e o `npc_setcells` (`npc.cpp:4972`) **pula célula com `CELL_CHKNOPASS`
sem erro e sem aviso** — `x125` é parede. Sobram exatamente as seis células
andáveis.

É a mesma mecânica que come uma célula do portal da praça de Prontera (o canto
`166,167`, documentado no `centro_da_ordem.txt`), só que lá ela tira algo que se
queria e aqui ela apara o que sobrava. **Se a boca do nicho mudar de largura, o
número muda junto — e a falha seria calada.**

### O Álbum de Cartas de Tarô não existia em item_db nenhum

Dos cinco prêmios da Roleta, quatro já estavam prontos no vendor — os disfarces
de Deviruchi, Poring, Mavka e Kobold Arqueiro, todos com nome PT no
`itemInfo.lua` e arte 4 de 4. O **600** não estava em lugar nenhum: varredura
por `tarot`, `taro` e `zilant` nos três `item_db` do `db/re/` devolveu nada.
Quem o conhecia era só o `itemInfo.lua` deste cliente e o `iteminfo_new.lub` do
bRO — e a arte faltava **inteira**, 4 de 4.

Ele foi criado no **ID oficial**, não num 30xxx nosso: mesmo critério da Moeda
do Explorador (25737). O `AegisName` (`Zilant_Tarot_Deck`) foi derivado do
`identifiedResourceName` do cliente, e é o único campo da entrada que é palpite
— todos os outros saem da descrição do bRO. A arte veio do GRF do bRO pelo
`instala_visual.py`, e mora em `cliente\data\`, **fora do git**.

### A regra do Tarô, e as duas habilidades que o palpite teria errado

O dono passou a regra e a tabela do browiki: soma os seis atributos **base**,
acha o maior divisor, e a tabela de catorze linhas diz qual habilidade sai. Se
a soma for prima, quem decide é o atributo em 125 ou mais.

A tabela vem com o **nome PT** da habilidade, não com o ID. O de-para foi feito
contra o `skillinfolist.lub` do **GRF do bRO** — a tabela de que a página fala,
regra §4.12 — e conferido **nos dois sentidos**. Duas teriam sido erradas:

- **"Dedicação" é `LK_CONCENTRATION`**, e não o `CR_DEVOTION` que o nome
  sugere: no bRO o `CR_DEVOTION` se chama **"Redenção"**.
- **"Ruído Estridente" é `WM_METALICSOUND`.** Ler o pool de constantes do
  `.lub` por **proximidade** devolvia `SA_GRAVITY` — plausível e errado. O que
  resolveu foi parsear o bytecode pela **estrutura** (`[SKID.X] = { SkillName =
  "Y" }`) em vez de pela vizinhança das strings.

Os catorze níveis foram conferidos contra o `MaxLevel` do `skill_db.yml`, e os
catorze cabem.

**O 5 não tem linha na tabela**, e isso é do bRO, não erro de transcrição. Soma
cujo único fator seja 5 cai no "Múltiplo de 1", ou seja Curar. Simulado sobre
todas as 775 somas possíveis: 5, 25, 115 e 125 caem em Curar; 35, 55, 65, 85,
95 e 175 são pegos antes por 7, 11, 13, 17 e 19.

O algoritmo foi rodado contra o exemplo da própria página — **374 = 2×11×17 →
17 → Chamas de Hela Nv. 3** — e bate.

### Os 5% de SP saem da descrição, não da página

A descrição do item começa com *"Drena 5% de SP para conjurar uma habilidade…"*,
e a página do browiki não cita isso. As duas não se contradizem — o dreno é
custo do Álbum, os requisitos são da habilidade —, mas o dreno entrou por
leitura da descrição. É `percentheal 0,-5`, e tirar é apagar uma linha.

`percentheal` com taxa negativa é o idioma certo, e não `heal`: o
`pc_percentheal` (`pc.cpp:10792`) manda taxa negativa para o
`status_percent_damage`, cujo comentário diz *"negative rates indicate % of max
rather than current"* — 5% do SP **máximo**, que é o que a descrição promete. E
só mata em -100.

### `DelayConsume` + `NoConsume`, e o `mes` que quebra tudo

Os dois campos são obrigatórios e nenhum é escolha: o `itemskill` **só funciona
em `DelayConsume`** (`doc/script_commands.txt`), e é o `NoConsume`
(`DELAYCONSUME_NOCONSUME`) que segura o `pc_delitem` no fim
(`skill.cpp:8310`). Precedente vivo no vendor: os dez Grimórios do Bruxo
(100065 a 100074).

E há uma armadilha que o mesmo parágrafo do doc entrega: **um `mes` dentro
daquela função quebra a conjuração** — *"It will not work properly if there is a
visible dialog window or menu"*. Mostrar qual carta saiu é a primeira coisa que
dá vontade de acrescentar, e é justamente o que não pode.

### Dois dos cinco prêmios cairiam no chão

O `getitem` com a mochila cheia larga o item no chão (`CLAUDE.md` §5), e quem
segura é o `NoDrop`. Aqui **dois dos cinco não o têm**: o Kobold Arqueiro
(22753), que já vinha assim do vendor, e o próprio Álbum — criado **sem
`Trade:` nenhum**, porque a descrição do bRO não traz a linha "Intransferível"
que a Moeda Nova e a Caveira Humana trazem. Pôr trava seria inventar (§4.3).

Então o que impede a queda é o **`checkweight` antes do `delitem`**, e só ele —
mesma forma da Sombrios Totais, com o sorteio antes da cobrança para o
`checkweight` saber qual item vai entregar.

### O anúncio é coluna, não `if`

Só o Álbum anuncia para o servidor. Escrever `if (.@premio == 600) announce …`
seria a divergência da §4.11 nascendo — no dia em que o prêmio raro mudasse de
ID, o `if` ficaria apontando para o item velho, calado. O anúncio é a **quarta
coluna** da mesma tabela do sorteio.

Ela é **numerada a partir de 1** (1 = calado, 2 = anuncia): em array de inteiro
do rAthena gravar 0 **remove** o elemento, e o `getarraysize` passaria a
devolver um tamanho menor que o das outras três — a conferência que existe para
pegar desalinhamento inventaria um.

### Os pesos, e por que são em décimos de milésimo

`0,2 + 24,95 × 4` fecha em 100,0 exatos. Com denominador **10000** (20 e quatro
de 2495) as cinco porcentagens saem sem arredondar nada, e a impressa na tela é
calculada dos mesmos pesos — não há número escrito à mão.

### O Rolinho de Arroz virou mercadoria

A Máquina Especial vende sete consumíveis a 1 Moeda Nova: seis pratos do bRO
que já existiam no vendor (12429 a 12434) e o **Rolinho de Arroz (30994)**, que
era nosso e que até a manhã do mesmo dia não tinha **quem o entregasse** — o
`PENDENCIAS.md` §1p dizia isso por escrito.

Ele foi feito como **prêmio de guerra** (cura 100% de HP e SP, sete travas) e
passou a ser comprado pelo mesmo preço de um prato comum. Foi o que o dono
pediu; o registro fica dos dois lados, e a decisão 2 daquela seção está
respondida — no sentido oposto ao que a frase "prêmio à venda deixa de ser
prêmio" antecipava.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `npc/guerra/sala_secreta_da_ordem.txt` | **novo** — os cinco NPCs |
| `npc/guerra/album_de_cartas_de_taro.txt` | **novo** — a `function F_AlbumDeTaro` |
| `db/guerra/item_db.yml` | o item **600** |
| `npc/guerra/barters_guerra.yml` | a loja `MaquinaEspecial#loja`, 7 linhas |
| `npc/guerra/scripts_guerra.conf` | as duas entradas narradas |
| `cliente\data\` | 4 arquivos de arte do 600, **fora do git** |

229 linhas inseridas nos três arquivos que já existiam, **zero removidas** — os
onze bytes acentuados do `item_db.yml` sobreviveram, conferido antes e depois.

---

## A missão do Amuleto — a Sala Secreta da Ordem ganha entrada (2026-08-14)

A Sala Secreta da Ordem (`sala_secreta_da_ordem.txt`, 2026-08-13) tinha saída
e não tinha entrada — `PENDENCIAS.md` §1q registrava isso como "vai ser por
quest, em outra sessão". Esta é aquela sessão: sete NPCs em três mapas, uma
variável de progresso e um teste de guardião. História 100% inventada, roteiro
dado pelo dono por inteiro em 2026-08-14.

### Por que variável, e não o sistema nativo de quest

O CLAUDE.md §5 documenta que quest não registrada no `QuestInfoList` do
cliente **derruba o cliente**, uma caixa de erro por missão. Registrar exigiria
`ferramentas/monta_missoes_da_ordem.py` e reabrir o cliente — e mesmo assim o
sistema nativo tem `MAX_QUEST_OBJETIVES` 3 (`src/common/mmo.hpp`), pensado para
caçada, não para uma cadeia de diálogo com ramo de aceitar/recusar em cada
NPC. A saída foi uma variável permanente por personagem comum,
`SalaSecretaOrdem` (0 a 12), sem risco nenhum de derrubar cliente — NPC comum
não passa pelo `QuestInfoList`.

### Dois erros pegos antes de escrever

O pedido veio com sprites `EP18_NPC_SUAD` e `EP18_NPC_MARAM` — **nenhum dos
dois existe** em `src/map/npc.hpp`. Os nomes certos, `JT_4_EP18_SUAD` e
`JT_4_EP18_MARAM` (`4_EP18_SUAD`/`4_EP18_MARAM` sem o prefixo `JT_` no
script), foram achados comparando com o `npc.hpp` e confirmados no
`data.grf` (`ferramentas/grf.py find`) antes de qualquer linha ser escrita —
usar o nome errado teria dado "Unknown syntax" e derrubado o arquivo inteiro
(CLAUDE.md §5). Os quatro sprites e as três imagens de retrato
(`ep18_maram_01/02/03.png`) são recursos **oficiais** do rAthena — o
`npc/re/quests/quests_18.txt` (Episódio 18, já carregado por padrão) usa os
mesmos, numa história totalmente diferente (a vila do Wolfchev). Só os
recursos foram reaproveitados.

O segundo achado durante a escrita foi **desfeito no teste em jogo**: a fala
do Suad dizia "o Daran pegou o amuleto", e isso foi lido como erro de
digitação de "Dario" — errado. **Daran e Dario são duas pessoas**: Daran é a
Criança (o sobrinho que pegou o amuleto, nunca nomeado na tela), Dario é o
irmão dela, o NPC do Centro da Ordem. Corrigido de volta para "Daran" em
2026-08-15, depois de o dono jogar a cadeia inteira — ver "O que o teste em
jogo corrigiu", abaixo.

### O guardião de teste: dois números errados discutidos ao vivo

O pedido dizia "guardião 1287... como se estivesse em um castelo com defesa
100" e citava, de memória, a **primeira** calibragem da escala de
`src/custom/guardiao_do_castelo.hpp` — 50 milhões de HP, 99% de redução —,
que tinha sido descartada na mesma noite em que nasceu (2026-08-13, "a
revisão, na mesma noite", acima). O dono corrigiu ao vivo: a calibragem de
verdade, em `conf/guerra/battle_guerra.txt` hoje, é a terceira (15 milhões de
HP, 50% de redução no patamar 10). **O `guardioes_dos_castelos.txt` também
citava a primeira calibragem, desatualizado desde aquela noite** — corrigido
na mesma entrega (cabeçalho e a fala do próprio Zelador dos Guardiões).

Mesmo com os números certos, não dá para usar o `guardian()` de verdade: a
escala só liga com um castelo de guilda por trás (`guardian_data->castle`), e
o mapa do teste não é castelo. O guardião nasce com `monster()` comum e os
sete números do patamar 10 são escritos à mão, por `setunitdata`, logo depois
do spawn — uma cópia estática da fórmula. Sem o multiplicador de guerra
(`gvg_castle` não está no mapa do teste), o dano bruto para derrubá-lo é 30
milhões, não os 150 milhões que valeriam dentro de um castelo de verdade — de
propósito mais fácil aqui, é demonstração, não guerra.

### O mapa que não existe no GRF, e o dono confirmou mesmo assim

O `job3_rune03` pedido para o teste **não existe** no `data.grf` desta
máquina — só `job3_rune01` e `job3_rune02` (`ferramentas/grf.py find`), e o
`DATA.INI` do cliente só lista esse GRF. Pela regra do CLAUDE.md §5 ("mapa
sem `.rsw` no GRF derruba o cliente e prende o personagem") isso deveria
travar. O dono trouxe uma captura de tela (personagem de pé em
`job3_rune03 39,44`, cena completa, sem queda, 2026-08-14) e pediu para
seguir com o mapa mesmo assim. A divergência fica registrada no cabeçalho do
`senha_da_sala_secreta.txt`, sem explicação — o `grf.py find` continua sem
achar os três arquivos, e o motivo de funcionar em jogo não foi descoberto.

Nenhum script do rAthena carregado usa `job3_rune03` hoje (só os quatro
`npc/re/mapflag/*.txt` genéricos de mapa de teste de 3ª classe) — é espaço
morto, como o `auction_01`/`auction_02` do Centro da Ordem e o `vis_h01` do
Corredor Fantasma.

### A cadeia, em uma tabela

| `SalaSecretaOrdem` | quem avança | onde |
|---|---|---|
| 0 → 1 | Criança | `prontera 142,186` |
| 1 → 2 | Dario | `auction_01 192,75` |
| 2 → 3 | Dario (com a Caveira Humana) | idem |
| 3 → 4 | Suad | `cmd_in02 74,76` |
| 4 → 5 | Assessor | `cmd_in02 63,66` |
| 5 → 6 | Bolãozão | `cmd_in02 182,89` |
| 6 → 7 | Assessor | `cmd_in02 63,66` |
| 7 → 8 | Suad | `cmd_in02 74,76` |
| 8 → 9 | Maram | `cmd_in02 73,86` |
| 9 → 10 | guardião derrotado | `job3_rune03` |
| 10 → 11 | Maram | `cmd_in02 73,86` |
| 11 → 12 | Guarda (senha) | `auction_01 194,87` |

O Guarda de `auction_01 194,87` deixou de ser `duplicate` do de `165,87`
(`guardas_do_centro.txt`) e ganhou script próprio: `< 11` continua "Sem
acesso.", `== 11` pede a senha por `input()`, `>= 12` vira um Sim/Não sem
repetir a senha. O destino é `prt_in 129,116`, a célula que o próprio
`PENDENCIAS.md` §1q já recomendava — conferida andável no `.gat` antes de
usar. O warp de saída (`128,103` → `auction_01 192,85`) não mudou.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `npc/guerra/menino_do_amuleto.txt` | **novo** — Criança e Dario |
| `npc/guerra/senha_da_sala_secreta.txt` | **novo** — Suad, Assessor, Bolãozão, Maram, o teste do guardião |
| `npc/guerra/guardas_do_centro.txt` | o Guarda de `194,87` deixou de ser `duplicate` |
| `npc/guerra/guardioes_dos_castelos.txt` | cabeçalho e fala corrigidos (99%→50%, 50M→15M HP) |
| `npc/guerra/scripts_guerra.conf` | as duas entradas narradas |
| `PENDENCIAS.md` | §1q fechada, §1s aberta ("falta ver no jogo") |

**Nada disto foi visto em jogo ainda** — ver `PENDENCIAS.md` §1s para a lista
de conferência, em ordem de risco.

### O que o teste em jogo corrigiu (2026-08-15)

O dono jogou a cadeia e trouxe cinco correções:

1. **A célula da Criança estava errada.** `prontera 142,168` não é onde ela
   fica — é `142,186`. Conferida andável antes de gravar.
2. **"Daran" não era erro de digitação — é a Criança.** A entrega anterior
   "corrigiu" a fala do Suad de "Daran" para "Dario", achando que fossem a
   mesma pessoa. Não são: Daran é o sobrinho que pegou o amuleto (a própria
   Criança, nunca nomeada na tela), Dario é o irmão dela, o NPC do Centro da
   Ordem. Desfeito.
3. **A fala do Bolãozão** ganhou "O Assessor disse" no início: "O Assessor
   disse o que?!!! HAHAHA Ele teve essa cara de pau?"
4. **A fala do Assessor**, na volta depois do Bolãozão, mudou para "O quee!!!
   ELE DISSE ISSO? Como ele.. quem.. hmmmm!!!"
5. **O Suad decorativo do teste do guardião** (`job3_rune03,42,45`) devia
   estar olhando para o sul (facing 4), e nasceu olhando para o oeste (2).
6. **A fala da senha não dizia ONDE o Guarda está**, só "a parede de cima" -
   ambíguo entre os quatro guardas que ficam nas fileiras de cima do salão
   (CLAUDE.md §4.11 é sobre isso: instrução sem endereço completo confia na
   sorte). Nas duas falas do Comandante Maram que citam a senha (a primeira
   entrega e o lembrete repetido) passou a dizer "a parede de cima direita
   do Centro da Ordem".

Nenhuma das seis mexeu em `SalaSecretaOrdem` nem na estrutura da cadeia — só
texto e duas coordenadas.

---

## O guardião de teste batia fraco, e não era calibragem (2026-08-15)

Continuação de "A missão do Amuleto" (acima). O dono testou o teste do
guardião e reportou: menos de 2.000 de dano por golpe, apesar do script pedir
40.000–60.000 via `setunitdata(UMOB_ATKMIN/ATKMAX, ...)`. O pedido de ajuste
veio com o alvo certo (HP 50 milhões, redução 90%, ATQ ~5.000) e uma condição:
"caso a redução de 80% da guerra não entre na geração dele, precisamos que a
redução geral seja de 90%" — ele já sabia que `job3_rune03` não tem o
multiplicador de guerra e pediu a compensação certa de cabeça.

### O bug, achado ao investigar por que o ATQ não pegava

`setunitdata` para `BL_MOB` tem dois comportamentos diferentes, e nada no
`doc/script_commands.txt` avisa qual é qual:

- `UMOB_HP`/`UMOB_MAXHP` chamam `status_set_hp`/`status_set_maxhp`
  (`src/map/script.cpp`), que escrevem **direto no status vivo**. Funcionam.
- `UMOB_DAMAGETAKEN` escreve em `md->damagetaken`, um campo solto no
  `mob_data`, fora da struct de status — `battle_calc_damage` o lê direto.
  Funciona.
- `UMOB_ATKMIN`, `UMOB_ATKMAX`, `UMOB_HIT`, `UMOB_AMOTION`, `UMOB_ADELAY` (e
  mais uns dez campos) escrevem em `md->base_status` e depois chamam
  `status_calc_bl_(md, status_db.getSCB_BATTLE())` para "aplicar". O
  problema: o combate lê `md->status`, não `md->base_status`
  (`status_get_status_data` devolve `&md->status` para `BL_MOB` —
  `src/map/status.cpp:9050`). E é `status_calc_mob_` quem copia
  `base_status` para `status`, só que **só roda se `flag[SCB_BASE]` estiver
  ligado** (`status_calc_bl_`, guardado atrás de um
  `if (flag[SCB_BASE]) switch(...)`). E `SCB_BATTLE` — o flag que
  `setunitdata` usa — **exclui `SCB_BASE` de propósito**:
  `SCB_BATTLE.set(); SCB_BATTLE.reset(SCB_BASE); SCB_BATTLE.reset(SCB_DYE);`
  (`src/map/status.hpp:3301-3303`).

Ou seja: as cinco linhas de `setunitdata` escreviam num lugar que o
recálculo que elas mesmas disparavam **nunca lia**. O guardião lutou o tempo
todo com o `Attack: 873` original do `mob_db` — daí o dano abaixo de 2.000.
`status_calc_mob(md, opt)` (o caminho que roda de verdade no spawn, e o que
`guardiao_do_castelo.hpp` usa) é `getSCB_ALL()`, que **inclui** `SCB_BASE` —
por isso o `Attack` do `mob_db` sempre esteve certo desde o primeiro spawn, e
por isso a saída foi mudar o `mob_db`, não o script.

### A saída: um segundo import em `db/re/mob_db.yml`

`db/guerra/mob_db.yml` já existe, mas é **gerado** por
`ferramentas/traduz_ptbr.py monstros` (só nome em português, reescrito
inteiro a cada rodada — editar à mão morre calado na próxima). Em vez de
arriscar isso, `db/re/mob_db.yml` ganhou um **segundo** `- Path:` no rodapé
(`CLAUDE.md` §2 atualizado — é a única exceção à regra de "um path por
arquivo"), apontando para `db/guerra/mob_db_guerra.yml`, novo, escrito à mão,
com uma linha: `Id: 1287, Attack: 5000`. Confirmado no `MobDatabase::
parseBodyNode` (`src/map/mob.cpp`) que isso é merge por campo, igual
`item_db.yml` — não redefine o resto do 1287 (nome, sprite, HP-base, etc.).

**Não contamina os guardiões de castelo de verdade**: aqueles escrevem
`status->rhw.atk`/`atk2` de forma absoluta em
`guardiao_aplica_escala` (`guardiao_do_castelo.hpp`), a partir de
`conf/guerra/battle_guerra.txt` — o `Attack` do `mob_db` nunca é consultado
ali. O override só é lido por quem invoca 1287 fora da escala, hoje só este
teste.

### O que ficou de fora, de propósito

`Hit`, `AttackMotion` e `AttackDelay` têm o mesmo bug de `setunitdata` e não
foram corrigidos — o pedido do dono falou só de dano, HP e redução. `Hit` nem
é campo do `mob_db` (sai de `nível + DEX`, então corrigir exigiria inflar o
DEX do monstro, efeito colateral não medido); velocidade de ataque ficou no
padrão do `mob_db` (`AttackDelay: 1288`, ~0,8 golpe/s) porque ninguém
reclamou de ritmo. As cinco linhas de `setunitdata` que não funcionavam
foram **removidas** do script, não deixadas mortas.

### Os números de hoje

| | antes (não funcionava) | agora |
|---|---|---|
| HP | 15.000.000 | **50.000.000** |
| redução | 50% (`damagetaken` 50) | **90%** (`damagetaken` 10) |
| ATQ | 40.000–60.000 (nunca aplicado) | **~5.000** (4.000–6.000, via `mob_db_guerra.yml`) |

Sem o multiplicador de guerra (`job3_rune03` não é `gvg_castle`),
`damagetaken = 10` já entrega os mesmos 10% finais que um castelo de verdade
daria com `0,20 (guerra) × 0,50 (guardião)` — foi o próprio dono quem pediu
essa conta, não uma dedução daqui. Dano bruto pra derrubar: 50.000.000 / 0,10
= 500 milhões.

### E um balão de quest

A pedido do mesmo teste: a Criança (`menino_do_amuleto.txt`) ganhou um balão
de fala repetindo "Quest" a cada 5 segundos (`npctalk`, mesma receita do
balão de MVP em `crianca_de_comodo.txt` — `initnpctimer` + `OnTimer5000`).
Não é por jogador (`npctalk` é visto por todo mundo perto, sem saber quem já
aceitou), mesma simplificação da Alleria e do Edgard.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `npc/guerra/menino_do_amuleto.txt` | Criança: célula (142,186), balão "Quest" |
| `npc/guerra/senha_da_sala_secreta.txt` | "Daran", falas do Bolãozão/Assessor, facing do Suad de teste, local da senha, números do guardião |
| `db/re/mob_db.yml` | **novo** segundo `- Path:` no rodapé |
| `db/guerra/mob_db_guerra.yml` | **novo** — `Attack: 5000` no 1287 |
| `CLAUDE.md` | §2, a exceção do `mob_db.yml` com dois imports |

## Três acertos finais: a chegada da Sala Secreta, o guardião revisto e o Zelador mudou de lugar (2026-08-14)

Três pedidos avulsos do dono, "pra deixar pronto pro deploy final".

### 1. A chegada da Sala Secreta, quatro células mais perto do centro

O Guarda de `auction_01 194,87` (`npc/guerra/guardas_do_centro.txt`) levava
para `prt_in 129,116`; passou a levar para **`prt_in 129,108`**, nos dois
ramos que fazem o `warp` (senha nova e "Entrar?" de quem já tem acesso). A
célula foi conferida andável no `prt_in.gat` (extraído do `data.grf` do
cliente, `ferramentas/grf.py`) antes de trocar.

### 2. O guardião de teste — o HP da seção anterior estava de memória, e não batia

Esta é uma CORREÇÃO da entrada logo acima ("O guardião de teste batia fraco").
O dono tinha pedido 50 milhões de HP de memória; ao conferir contra a tabela
real de `src/custom/guardiao_do_castelo.hpp` (a que os guardiões de castelo de
verdade usam no patamar 100/defesa 100), viu que o número certo é **15
milhões** — o mesmo teto da escala real. A redução continua em 90% (50% do
guardião × 80% da guerra, multiplicado e não somado — já estava certo). E dois
campos que a entrada anterior deixou de fora "por decisão de escopo" (Hit,
AttackMotion, AttackDelay) ganharam o mesmo tratamento do ATQ: `Dex: 369` e
`AttackDelay: 440` / `AttackMotion: 220` / `ClientAttackMotion: 220`, os
quatro em `db/guerra/mob_db_guerra.yml`, ao lado do `Attack: 5000` que já
estava lá. Resultado, pelas mesmas fórmulas do `.hpp` (ASPD 178 → amotion 220
→ adelay 440; Hit de monstro = nível + DEX + 150 → 56 + 369 + 150 = 575):

| | seção anterior | agora |
|---|---|---|
| HP | 50.000.000 | **15.000.000** |
| redução | 90% | 90% (sem mudança) |
| ATQ | ~5.000 | ~5.000 (sem mudança) |
| ASPD | padrão do mob_db (~0,8 golpe/s) | **178** (~2,3 golpes/s) |
| precisão | padrão do mob_db (309) | **~575** |

Conferido que subir o `Dex` do 1287 não mexe em mais nada que importe aqui:
`status.cpp` só usa `Dex` de `BL_MOB` no cálculo do `Hit` (linha 2635); o
resto das fórmulas que usam `dex` são de `BL_PC`. E nada disto toca os
guardiões de castelo de verdade — eles passam por
`guardiao_do_castelo.hpp`, que escreve `amotion`/`adelay`/`hit` de forma
absoluta, por cima de qualquer coisa que o `mob_db` (ou este arquivo) tenha.

Dano bruto pra derrubar, com o HP novo: 15.000.000 / 0,10 = **150 milhões**
(não mais 500).

### 3. O Zelador dos Guardiões mudou de `prt_gld 136,66` para `153,133`

Pedido direto do dono, sem explicação adicional — célula conferida andável no
`map_cache.dat` (`db/map_cache.dat`, o grande; `prt_gld.gat` cru tem o bit DES
e o `ferramentas/grf.py` não o lê, CLAUDE.md §5) antes de mover. O texto do
cabeçalho de `guardioes_dos_castelos.txt` que descrevia a posição antiga como
"a poucos passos da entrada do Kriemhild" foi reescrito — a nova célula não
está mais perto daquela entrada (`129,65`), e o cabeçalho não deveria
continuar afirmando isso.

### Uma armadilha pega no processo: o `Edit` corrompeu acentos de verdade

`guardioes_dos_castelos.txt` tem 24 bytes acentuados (cp1252) — ao contrário
de `mob_db_guerra.yml` e `senha_da_sala_secreta.txt`, que por acaso não têm
nenhum. Uma primeira tentativa de editar o cabeçalho com a ferramenta de
edição do assistente trocou os 24 por `\xef\xbf\xbd` (U+FFFD) — exatamente a
armadilha do CLAUDE.md §5. Pego na hora por medir `non-ascii bytes` antes e
depois de cada edição (o hábito que a mesma seção recomenda); corrigido com
`git checkout` do arquivo e reaplicado por script Python com âncora em
cp1252/CRLF (medido, não suposto — o arquivo é CRLF, ao contrário de
`senha_da_sala_secreta.txt`, que é LF puro).

### O que foi tocado

| arquivo | o quê |
|---|---|
| `npc/guerra/guardas_do_centro.txt` | destino do warp da Sala Secreta: 129,116 → 129,108 |
| `db/guerra/mob_db_guerra.yml` | `Dex`, `AttackDelay`, `AttackMotion`, `ClientAttackMotion` no 1287 |
| `npc/guerra/senha_da_sala_secreta.txt` | HP do guardião de teste: 50M → 15M; cabeçalho atualizado |
| `npc/guerra/guardioes_dos_castelos.txt` | Zelador: 136,66 → 153,133; cabeçalho atualizado |
| `PENDENCIAS.md` | seções 1o e 1s atualizadas com os números e a célula novos |
| `PENDENCIAS.md` | §1s atualizada |
