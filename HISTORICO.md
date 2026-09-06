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
   *(Respondido em 2026-08-22: os sprites existem — 101 `.spr` em `costume_1`.
   O defeito era outro, e eram três; ver "O estilo de corpo que nunca chegou a
   existir".)*

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

### Emenda: `*` e `-` liberados (2026-08-15)

Pedido do dono: *"hoje a criação de personagem não permite `*` e `-`. Deixa
permitir por favor"*. É a decisão de 2026-08-10 revista — aquela rodada tinha
deixado símbolo de fora **de propósito**, com o argumento de que nome é chave
em comando de GM e em sussurro. O dono quis os dois; entraram os dois, e só
eles.

Uma constante nova (`SIMBOLOS`) no `ferramentas/gera_char_guerra.py`, com o
cabeçalho gerado ajustado, e o `conf/guerra/char_guerra.txt` regerado. **Nada
de editar o `.txt` à mão** — é cp1252, e é exatamente para isso que o gerador
existe.

Três coisas apuradas no caminho, que evitam a próxima dúvida:

- **A lista é lida por `strchr`, não é regex.** O `-` não tem sentido de
  intervalo ali e pode ficar em qualquer posição da string.
- **O `#` não seria liberável pela lista.** O `char_check_char_name` recusa
  antes, no `char.cpp:1358`, qualquer nome cuja **primeira** letra seja `#` —
  o rAthena reserva o símbolo para canal. Pô-lo na lista não adiantaria, e o
  sintoma seria a mesma caixa de sempre.
- **Os quatro pontos de checagem seguem juntos**: personagem, clã, grupo e
  homúnculo passam a aceitar `*` e `-` na mesma tacada, como toda mudança
  nessa variável.

Config só é lida na inicialização, e **não existe recarregador para
`char_name_letters`**: exige reiniciar o char-server — que derruba quem está
jogando, porque o map-server perde a ligação com ele.

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

---

## O teto de redução baixou para 99% — por enquanto, sem classe 4 (2026-08-14)

Detalhe que faltou na calibragem do teto de redução de carta (ver "O teto de
99,9%" acima, 2026-08-10): o dono pediu **99%, não 99,9%**, enquanto o
servidor não tiver classe 4. `reducao_dano_teto` foi de `999` para `990` em
`conf/guerra/battle_guerra.txt`; muda com `@reloadbattleconf`, sem reiniciar.

A diferença é pequena em número (0,9 ponto) mas grande no que passa: no piso
de 99,9% um jogador com resistência somada acima de 100% ainda toma 0,1% do
dano bruto; a 99% ele toma dez vezes mais — 1%. Revisitar quando a classe 4
entrar no servidor.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `conf/guerra/battle_guerra.txt` | `reducao_dano_teto: 999` → `990`, comentário explica o "por enquanto" |
| `REDUCAO-DE-DANO.md` | §1b: título e tabela refletem 990/99% como o valor atual |
| `CLAUDE.md` | linha do enxerto de `reducao_piso` deixou de citar 99,9% fixo |
| `PENDENCIAS.md` | §1h, item 2, atualizado com o valor e a data novos |
| `PENDENCIAS.md` | seções 1o e 1s atualizadas com os números e a célula novos |
| `PENDENCIAS.md` | §1s atualizada |

---

## A senha deixa de ser texto puro (2026-08-14)

Etapa 1 do `IMPLANTACAO.md`, feita antes de o servidor Linux existir e pelo
motivo que o plano dá: senha em texto puro não é só risco de hoje, é risco de
**todo backup que já tiver sido feito** quando alguém resolver ligar o MD5.

Não houve linha de C++. O rAthena já faz isso — o que faltava era a decisão
estar **versionada**. Então o de sempre: um arquivo nosso
(`conf/guerra/login_guerra.txt`, com o cabeçalho explicando o porquê) e uma
linha de `import:` no `login_athena.conf`, posta **antes** da linha do
`conf/import/` para o arquivo de máquina continuar com a última palavra.

**O que o dia acrescentou ao que o plano previa:** a conversão das contas que já
existiam **não era opcional**, como estava escrito lá. A conta com que o
char-server e o map-server se conectam ao login é uma linha da mesma tabela
`login` (a de sexo `S`, o `s1` daqui), e ela passa pelo **mesmo** hash
(`loginclif.cpp:411`). Sem converter, o char-server para de conectar — e o
sintoma é *"The server communication passwords (default s1/p1) are probably
invalid"* (`char_logif.cpp:279`), que aponta para a senha do `conf/import/` e
não para o MD5 recém-ligado. É por isso que o `UPDATE` é **sem `WHERE`**.

As três contas do HML (`s1`, `teste`, `filiponegrao`) foram convertidas com
`UPDATE login SET user_pass = MD5(user_pass);` e os quatro servidores
reiniciados. **Roda uma vez só**: rodar de novo hasheia o hash e tranca todo
mundo para fora, e não há volta ao texto — que é o ponto.

**O que ficou provado, e como:** o `lastlogin` do `s1` foi para `2026-08-14
20:40:36`, o instante do reinício. Ou seja o char-server autenticou no
login-server com a senha já hasheada, ponta a ponta. O que **não** está provado
é o login de um jogador pelo cliente — falta entrar uma vez com a senha de
sempre. Se aparecer *"rejected from server"*, a causa é uma só e está no
cabeçalho do `login_guerra.txt`: cliente com `<passwordencrypt>`. O nosso
`clientinfo.xml` não tem — conferido no mesmo dia.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `rathena/conf/guerra/login_guerra.txt` | **novo** — `use_MD5_passwords: yes` e o porquê |
| `rathena/conf/login_athena.conf` | uma linha `import:`, antes da do `conf/import/` |
| `CLAUDE.md` | §2, a linha do enxerto novo |
| `IMPLANTACAO.md` | Etapa 1: o que entrou, e a correção do "opcional" |

---

## A implantação no servidor Linux (2026-08-14 e 15)

Em dois dias o projeto saiu de "roda no Windows de casa" para **um servidor
público com os quatro servidores sob systemd, site de criação de conta, HTTPS e
backup automático** — e com um comando só para atualizar tudo. O plano inteiro,
etapa por etapa, está no `IMPLANTACAO.md`; aqui fica o que se aprendeu.

**Tudo por script, e idempotente.** Quatro na `ferramentas/`: `provisiona.sh`
(máquina), `configura_servidor.sh` (conf/import + systemd), `configura_web.sh`
(Apache + site), `configura_backup.sh` (temporizadores), mais o par
`implanta.sh` / `atualiza_servidor.sh` do deploy e o `prevoo.sh` da varredura.
A idempotência não foi capricho: o primeiro `provisiona.sh` morreu no meio duas
vezes, e rodar de novo foi o que permitiu continuar de onde parou.

**A previsão de portabilidade se confirmou.** O C++ de `src/custom/` compilou no
GCC sem um ajuste — era o marco de risco do plano, e caiu em 67 minutos. O que
quase matou o build foi **memória**: o `skill.cpp` sozinho pediu 947 MB de RAM
*mais* 1,8 GB de swap.

**Cinco armadilhas novas foram para o `CLAUDE.md` §5**, e todas têm a mesma
assinatura — falham caladas, ou apontam para o lugar errado:

1. **No `sshd_config` o primeiro valor vence**, não o último — inverso do nginx
   e do sysctl. Um drop-in `99-` perde para o `50-cloud-init` da DigitalOcean.
2. **`tr -dc … | head -c N` mata o script sob `pipefail`**, por SIGPIPE, sem
   imprimir uma linha.
3. **O bit de execução do `rathena/` não está no git** (vendor feito no
   Windows): `./configure` responde *"Permission denied"*, que parece problema
   de dono.
4. **`libmariadb-dev` não basta** — falta o `-compat`, e o erro é *"MySQL not
   found or incompatible"* com o MariaDB instalado e no ar.
5. **A senha da conta de comunicação entre servidores tem teto de 23
   caracteres** (`char_logif.cpp:826` copia 24 bytes e trunca), e o erro que sai
   manda conferir `s1`/`p1`, que já estava certo.

**Um furo foi fechado antes de existir.** O site criava a conta e depois gravava
o documento — mas a `login` é MyISAM e ignora transação, então uma falha no
segundo passo deixaria conta **jogável e sem documento**: o furo no limite de
uma conta por pessoa, aberto justamente por quem tentasse burlá-lo. A ordem foi
invertida — reserva o documento, cria a conta, completa a reserva.

**Duas decisões do dono desviaram do plano escrito, e as duas com razão.** O
root continua entrando por SSH (só por chave): com um operador, os dois
argumentos clássicos contra ele não se aplicam, e a separação que importa — o
usuário do jogo sem sudo — ficou inteira. E o Apache entrou no lugar do nginx,
que custou uma desinstalação porque nada nosso chegara a ser configurado nele.

**O que ficou aberto** está no `PENDENCIAS.md` §5: o documento do cadastro ainda
não é verificado (falta plugar o Penelope, que é uma linha de configuração), e o
roadmap de segurança do beta.

---

## O cliente aponta para a produção — e o arquivo era o outro (2026-08-14)

Etapa 2 do `IMPLANTACAO.md`, fechada com **login de verdade no servidor Linux**:
conta `filiponegrao`, criada pelo site, entrando pelo cliente desta máquina. O
trabalho previsto era trocar um endereço num XML. O que custou a sessão foi
descobrir **qual XML**.

(O relógio desta máquina marcava 2026-08-14; a sessão do Mac datou o próprio
trabalho de 2026-08-15. É a mesma virada de noite, não duas datas.)

### O que o briefing mandava, e por que não bastou

O `SESSAO-WINDOWS.md` mandava trocar o `<address>` do `data\clientinfo.xml` de
`127.0.0.1` para o servidor. Feito com todo o cuidado que o arquivo pede — cp1252,
gravado por script, âncora única com `assert`, fim de linha medido antes (era LF),
relido em cp1252, e a conferência de que **só** o `<address>` mudou. O arquivo
ficou perfeito. E o cliente continuou falando com `127.0.0.1`.

**Quem manda é o `data\sclientinfo.xml`.** Este exe é
`<servertype>sakray</servertype>`, e o par sakray é o `sclientinfo.xml` — que
estava ali, na mesma pasta, com `<address>127.0.0.1</address>` e
`<display>Local</display>`, intocado desde 2026-08-03. Trocado ele, o login
aconteceu na primeira tentativa.

Por que engana: os dois arquivos existem, os dois têm `<address>`, o exe carrega
as duas strings sobrepostas (`sclientinfo.xml` em `0x9f707c`, `clientinfo.xml`
um byte adiante) e o `.epi` lista o patch `CallKoreaClientInfo`, que aponta para
o lado errado. **O mecanismo exato não foi perseguido** — o que existe é a prova
empírica, que é o que valia. Os dois arquivos ficaram com o mesmo endereço, de
modo que a pergunta não precise ser respondida de novo.

### Os três becos, e o que decidiu

Nenhum dos três era bobo, e os três estavam errados:

| hipótese | como caiu |
|---|---|
| O cliente não resolve nome de domínio (`inet_addr`) | trocado o domínio por `138.197.155.31`, o sintoma **não** mudou. E o `.epi` traz `EnableDnsSupport`: o domínio funcionaria |
| Firewall bloqueando o exe | `Get-NetFirewallApplicationFilter` não achou regra nenhuma para ele, e a saída padrão dos três perfis é permitir |
| "Demorou muito, logo não é o loopback" | falso. O SYN para `127.0.0.1:6900` sem nada escutando ficou em **`SynSent`** até estourar o tempo, em vez da recusa imediata que se espera |

Havia ainda uma quarta pista, que mentiu: o `LastAccessTime` do `clientinfo.xml`
não andou depois de o cliente subir, o que parecia provar que ele não lera o
arquivo. **O NTFS só atualiza esse carimbo quando o valor guardado tem mais de
uma hora** — a minha própria conferência, cinco minutos antes, o havia
congelado. A ressalva subiu para o `CLAUDE.md` §5, ao lado da regra que ela
corrige.

**O que decidiu foi olhar para onde o pacote ia**: um laço de
`Get-NetTCPConnection -OwningProcess <pid>` a cada 300 ms, gravando em arquivo,
enquanto o dono apertava Login. Saiu `127.0.0.1:6900 SynSent` — fato, não
impressão, e o diagnóstico inteiro em uma tentativa. Vale como técnica para
qualquer "o cliente não conecta".

### De quebra: a lista de patches do NEMO

O `GuerraDoEmperium.epi`, ao lado do exe, é o perfil do NEMO e **traz os nomes
dos patches aplicados em texto legível**. Isso é justamente o levantamento que o
`PENDENCIAS.md` §5b pedia "antes de empacotar, enquanto ainda se lembra" — o exe
é a única peça do conjunto sem gerador versionado. A lista foi para o
`REFERENCIA.md`.

Três entradas dela já pagaram o custo nesta sessão: `EnableDnsSupport` matou a
hipótese do domínio, `DataFolderFirst` confirmou que a pasta `data\` vence o GRF,
e `AlwaysAscii` é o que desenha o byte acentuado (regra §4.1).

### O que fica em aberto

- O `<address>` está com o **IP**, não com o domínio. Funciona e está provado;
  o domínio é mais robusto se o droplet mudar de IP, e o `EnableDnsSupport` diz
  que ele serve. Trocar é uma linha nos dois arquivos, e não foi feito para não
  mexer no que acabou de funcionar.
- A alteração **não está no git** — o cliente inteiro está fora. Ela some em
  cliente novo, e o instalador tem de levar os **dois** XML já apontados.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `cliente\data\sclientinfo.xml` | **fora do git** — `<address>` para `138.197.155.31` e `<display>` de `Local` para `Guerra do Emperium` |
| `cliente\data\clientinfo.xml` | **fora do git** — mesmo `<address>`, para os dois não divergirem |
| `CLAUDE.md` | §5: a entrada do `sclientinfo.xml` e a ressalva de uma hora no `LastAccessTime` |
| `REFERENCIA.md` | endereço da produção e a lista de patches do NEMO |
| `IMPLANTACAO.md` | Etapa 2 fechada; §9 item 1 resolvido |
| `PENDENCIAS.md` | §5b: a lista do NEMO deixou de ser dívida |
| `SESSAO-WINDOWS.md` | **apagado** — era entregável de sessão, e a Etapa 2 fechou |
| `PENDENCIAS.md` | §5c **nova** — os quatro servidores na produção e os apontamentos do cliente que sobraram (o web, em `127.0.0.1:8888`) |

## O homúnculo e a pasta que o exe procura (2026-08-15)

Ao clicar em **Criar Homunculus**, o cliente devolveu uma caixa `AI.lua error`:

```
cannot open .\AI_sakray\AI.lua: No such file or directory
```

O embrião foi consumido e o item criado — o chat mostra as duas linhas —, então
o lado servidor fez a parte dele. O que faltou é do cliente, e não é nem IA
quebrada nem sprite ausente.

### Não era sprite

Primeira hipótese descartada de graça: os quatro homúnculos estão inteiros no
`data.grf`, com evolução e as duas variantes de sexo — `lif`, `amistr`, `filir`,
`vanilmirth`, cada um com `_h`, `2` e `_h2` — mais os cinco homunculus S
(`mer_bayeri`, `mer_dieter`, `mer_eira`, `mer_eleanor`, `mer_sera`). Vinte e um
`.spr`, todos presentes.

### Era o nome da pasta

Este exe é `sakray` (o mesmo `<servertype>` que já tinha decidido, em
2026-08-14, que o endereço mora no `sclientinfo.xml`). As **cinco** strings de
caminho de IA no `GuerraDoEmperium.exe` são todas da variante sakray, e não há
nenhuma da pasta normal:

| endereço | string |
|---|---|
| `0x9ede48` | `.\AI_sakray\USER_AI` |
| `0x9ede5c` | `.\AI_sakray\USER_AI\AI.lua` |
| `0x9ede78` | `.\AI_sakray\AI.lua` |
| `0x9ede8c` | `.\AI_sakray\USER_AI\AI_M.lua` |
| `0x9edeac` | `.\AI_sakray\AI_M.lua` |

E a pasta que o cliente tem, desde a instalação de 2021-11-05, chama-se `AI`.
Ou seja: os arquivos sempre estiveram lá, com o nome errado para este exe. O
`AI_M.lua` é a IA do **mercenário** — o mesmo buraco o esperava.

Conserto: `AI_sakray` como cópia de `AI`, com a subpasta `USER_AI` junto (é a
IA customizada, que o exe procura primeiro).

Os `require` de dentro **não** precisaram mudar. Eles dizem `require "AI\Const"`
e `require "AI\Util"` — com o nome da própria pasta no caminho, o que prova que
a resolução é relativa à **raiz do cliente** e não à pasta do script; se fosse à
pasta do script, o `AI\AI.lua` original nunca teria funcionado em cliente
nenhum. Como a pasta `AI` continua existindo, os dois lados acham o que
carregar.

### O que fica em aberto

A pasta nova **não está no git** — o cliente inteiro está fora. Ela some em
cliente novo, e o instalador tem de levá-la, do mesmo jeito que os dois XML de
`clientinfo`.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `cliente\AI_sakray\` | **fora do git** — cópia de `cliente\AI\`, com `USER_AI` |
| `CLAUDE.md` | §5: a entrada da pasta de IA |

## O Atualizador: o cliente passa a receber melhoria sem baixar 4,9 GB (2026-08-15)

O pedido veio da falta que ele fazia. O dono tinha acabado de corrigir a
`AI_sakray` (seção acima) — 40 KB de arquivo dentro do cliente, sem os quais
criar homúnculo devolve caixa de erro — e **não havia caminho nenhum** para
entregar aquilo a quem já tinha baixado. O cliente sai por uma pasta do Google
Drive, e a alternativa era pedir a todo mundo que baixasse 4,9 GB de novo.

### As duas metades que o projeto já tinha, e a que faltava

O servidor já sabia entregar mudança sozinho: `implanta.sh`, `git pull`, quatro
serviços reiniciados, ninguém baixa nada. O cliente é o oposto — cada jogador
tem uma cópia congelada do dia em que instalou, e nada nossa alcança ela.

O gancho de infraestrutura já estava pronto desde 2026-08-15 de manhã, sem uso:
o Apache serve `/patch/` de `/var/www/patch` (Etapa 8 da implantação), e o
levantamento do que faltava estava escrito em `PENDENCIAS.md` §5b.

### A escolha: patcher nosso em Go, e não o Thor

Levado ao dono como decisão, com o Thor Patcher (o padrão da comunidade de RO)
do outro lado. O que pesou contra o Thor foi ele repetir o problema que este
projeto já tem uma vez: um binário fechado, sem gerador versionado, exatamente
como o `GuerraDoEmperium.exe` do NEMO. O que pesou a favor do nosso foi o
servidor já servir HTTP estático e o site já ser Go.

**Zero dependências externas** — o Win32 é chamado por `syscall.NewLazyDLL`
contra user32, gdi32 e comctl32. O binário que vai para o computador dos
jogadores não tem código de terceiro nenhum além da biblioteca padrão do Go.

Escopo da v1, também decidido pelo dono: baixar/aplicar, botão Jogar e
**auto-atualização do próprio Atualizador**. Painel de notícias ficou de fora.

### O formato: zip extraído por cima, e por quê

Sem diff binário e sem GRF. O cliente tem `DataFolderFirst`, então arquivo solto
em `data\` vence o `data.grf` — é assim que todo o nosso conteúdo já chega, e um
zip extraído por cima é a mesma coisa.

A propriedade que isso compra é **idempotência**: aplicar duas vezes não muda
nada, e apagar o `patch\aplicados.txt` refaz tudo do zero. É o que torna o
suporte barato — "apaga esse arquivo e abre de novo" é um conserto completo que
o jogador executa sozinho pelo Discord. Um formato com diff economizaria banda e
custaria justamente isso.

Três regras de ordem, todas com o mesmo motivo — não deixar o cliente do jogador
num estado que ninguém consegue reproduzir aqui:

- **o zip sobe antes da lista.** Na ordem inversa, quem abrisse o Atualizador
  no intervalo pediria arquivo que ainda não existe;
- **zip antigo não se apaga do servidor.** Quem instalou o cliente ontem ainda
  vai baixar o patch 0001 amanhã;
- **o número só cresce.** Corrigir patch publicado é patch novo por cima.

### O que foi medido, e as duas armadilhas que apareceram

**Nome de arquivo coreano dentro do cliente quebra o Python 2 de duas
maneiras.** A `AI_sakray` traz o manual da IA do kRO. Na leitura, `os.walk` com
caminho `str` usa a API ANSI, devolve `????` e o `os.stat` seguinte estoura com
*"A sintaxe do nome do arquivo... está incorreta"* — mensagem que aponta para o
arquivo quando o defeito é do leitor. E na **escrita da tela**: o `print` do
mesmo nome derruba a ferramenta com `UnicodeEncodeError`, depois de o zip já
estar gravado. As duas foram para o `CLAUDE.md` §5.

**`StretchDIBits` com `HALFTONE` falha de vez em quando e mente no
`GetLastError`.** Duas execuções do mesmo binário devolveram 630 linhas
(sucesso); a terceira devolveu **0**, com o erro do sistema dizendo *"operação
concluída com êxito"*. O sintoma era a janela nascer com o retângulo da arte
preto. A saída foi tirar o GDI da conta: a redução de 1200x630 para 560x294 é
feita **em Go**, por média de caixa, e o GDI só faz a cópia 1:1. Trinta linhas
em troca de a janela nunca mais nascer preta.

Antes disso houve um erro mais simples, e vale registrar porque é do tipo que se
repete: a arte era preparada **depois** de a janela ser criada. Decodificar o
JPEG leva ~100 ms, e um `WM_PAINT` que chegasse nesse intervalo pintava o
retângulo de cima vazio — e como daí em diante só a faixa de baixo é invalidada
(para o progresso não fazer a arte piscar), o preto ficava até algo passar por
cima da janela.

### O teste

Ponta a ponta, com um `SimpleHTTPServer` local no lugar da produção: montou o
patch 0001 (a `AI_sakray`, 9 arquivos, 40 KB no zip), baixou, conferiu o sha256,
extraiu — **inclusive o arquivo de nome coreano, com o nome intacto** —,
escreveu o `aplicados.txt`, liberou o botão e abriu o jogo. Depois, três
execuções seguidas medindo o brilho médio da área da arte: 76,7 nas três, contra
~0 de uma janela preta.

Contra a produção, que ainda não tem lista publicada, o caminho de falha também
foi conferido: `404`, mensagem em português e botão liberado. **Nada pode
impedir o jogador de jogar** — é a única peça do projeto que roda na máquina dos
outros, e travar ali é pior do que não atualizar.

### O que fica em aberto

~~**Publicar exige SSH ao servidor a partir do Windows**, que é onde os zips
nascem, e esta máquina não tem chave autorizada — o deploy sempre foi do Mac.~~
**Resolvido em 2026-08-16** — ver a seção "O primeiro patch no ar", abaixo.

Ícone e manifest do exe (a barra de progresso sai no estilo clássico),
assinatura dos patches e o painel de notícias estão em `patcher/LEIAME.md` §5.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `patcher/` | o Atualizador: `main.go`, `patch.go`, `auto.go`, `janela.go`, `registro.go`, `recursos/fundo.jpg`, `Jogar.ini`, `LEIAME.md` |
| `patcher/patches.txt` | o registro dos patches — **é** a `lista.txt` que o servidor serve |
| `ferramentas/monta_patch.py` | o gerador do zip |
| `ferramentas/publica_patch.sh` | o publicador (roda no Windows) |
| `cliente\Jogar.exe`, `.ini` | **fora do git** — instalados no cliente desta máquina |
| `CLAUDE.md` | §1 (o mapa), §4.18 (a regra nova), §5 (as duas armadilhas), §6 (leitura) |
| `ARQUITETURA.md` | §4: o acoplamento entre máquinas |
| `RECEITAS.md` | §11: o ciclo de um patch |
| `REFERENCIA.md` | caminhos, URL do patch, Go instalado |
| `PENDENCIAS.md`, `IMPLANTACAO.md` | §5b e §9: o que o patch fechou e o que sobrou |

### O fecho da v0 (2026-08-15)

O servidor abriu. Cliente conectando, site publicado com a arte do dono, conta
de GM, backup rodando sozinho e um comando de deploy.

**As duas últimas lições vieram no fim, e as duas foram do mesmo tipo — o aviso
existia por escrito e não foi seguido:**

- O `implanta.sh` reiniciava o jogo **toda vez**. Um deploy de CSS derrubou o
  dono do jogo com *"Erro desconhecido"*, e a Etapa 12 do `IMPLANTACAO.md`
  descrevia esse cenário palavra por palavra. É a §4.17 do `CLAUDE.md` de novo,
  do outro lado: lá o comentário mentia sobre o código; aqui o código não fazia
  o que o próprio plano mandava.
- A arte de fundo não aparecia porque o `body` tinha fundo opaco cobrindo-a — e
  **o defeito era mais velho que a imagem**: o gradiente que estava lá antes
  também nunca apareceu, e ninguém percebeu porque os dois eram quase pretos.
  Duas coisas erradas que se pareciam com uma certa.

### O primeiro patch no ar (2026-08-16)

A chave do Windows foi autorizada na conta **`ragnarok`** — decisão do dono no
mesmo dia, no lugar do root: a chave só precisa copiar arquivo para
`/var/www/patch`, que já pertence a ele.

Com isso o único trecho do sistema que nunca tinha sido exercitado contra o
servidor de verdade — `scp` → Apache → download por HTTPS — passou a estar
provado. Publicado o **patch 0001** (`AI_sakray`, 42.236 bytes), e conferido de
fora, na ordem: a lista responde 200 e é texto (não o HTML do site), tem os
cinco campos separados por TAB, o sha256 do zip bate com o do registro, e o
`patcher.txt` responde 404 — que é a resposta certa enquanto não há Atualizador
novo.

Depois, o teste que importa: uma pasta limpa, com o `Jogar.ini` apontando
para a produção. Ele baixou, conferiu, extraiu os nove arquivos (**inclusive o
de nome coreano**), escreveu o `aplicados.txt` e liberou o botão com *"Pronto —
1 atualização aplicada."*

**Publicar agora não entrega nada a ninguém, e foi por isso que valeu a pena.**
Nenhum jogador tem o Atualizador — o pacote do Drive é anterior a ele. Ou seja,
o caminho inteiro foi validado com a produção real, sem risco de entregar coisa
indesejada, e num dia em que descobrir um problema custa uma tarde em vez de
custar a véspera do lançamento.

Conferido também que os três `Jogar.exe` que existem hoje são **o mesmo
binário** (`2292a556…`): o do repositório, o instalado no cliente desta máquina
e o que está dentro do `Jogar-Guerra-do-Emperium.zip` de distribuição. É o
tipo de coisa que diverge calada e só aparece quando alguém relata um defeito
que "aqui não acontece".

### A janela ganha cara de Ragnarok, e a pasta do cliente fica limpa (2026-08-16)

Três pedidos do dono depois do primeiro patch funcionar em jogo, e os três eram
sobre a mesma coisa: o que o jogador vê ao abrir a pasta e ao abrir o programa.

**1. O nome do que se clica.** `Atualizador.exe` virou **`Jogar.exe`** — o nome
tem de dizer o que fazer, não o que o programa é. O `GuerraDoEmperium.exe`
continua sendo o jogo, e o Atualizador é quem o abre.

O código deixou de depender do próprio nome: o `.ini` procurado é
`<nome do exe>.ini` (com `Atualizador.ini` como reserva), e os arquivos da
auto-atualização saem do nome do exe. Se o nome mudar de novo, é só renomear —
o que interessa é que uma troca de nome **não** deixe instalação quebrada em
silêncio na máquina dos outros.

**2. A faxina da pasta.** `ferramentas/limpa_cliente.py`, versionado porque as
ferramentas vão continuar deixando backup:

| o quê | quanto | para onde |
|---|---|---|
| backups das ferramentas | 79 arquivos, **768 MB** | `C:\GuerraDoEmperium\_backups_removidos\` |
| executáveis do kRO | 6 arquivos, 20 MB | `cliente\_extras\` |

Os dois **movem**, não apagam, e o motivo é específico: entre os backups estão
as duas únicas cópias do exe **antes** dos nossos patches, e o exe é o único
arquivo do cliente sem gerador versionado. Apagar sairia de graça hoje e caro
no dia em que alguém precisasse refazer um patch de exe. Na raiz ficaram três
coisas: `Jogar.exe`, `GuerraDoEmperium.exe` e o `Setup.exe` — o único do kRO
que o jogador tem motivo para abrir.

**3. A janela.** O dono pôs lado a lado um print do patcher do bRO e o nosso, e
o veredito foi imediato: a nossa funcionava e **parecia um utilitário**. Um
servidor que vende nostalgia não abre com caixa de diálogo cinza.

A janela foi refeita no formato que o jogador de RO reconhece — moldura própria
no lugar da barra do Windows, arte ocupando quase tudo, rodapé com o estado, a
barra larga e o JOGAR grande à direita —, com arte nova mandada por ele (o
cavaleiro diante do Emperium, na cidade em ruínas). Nada é controle nativo:
some junto a barra de progresso em estilo clássico, que era uma pendência.

O layout tem 760x674, e a altura foi escolhida contra a **tela do jogador**, não
contra a arte: em 1366x768 sobram ~728 px depois da barra de tarefas, e uma
janela cortada embaixo esconderia justamente o botão JOGAR. Como a arte é 4:3 e
a moldura é mais larga, ela entra cobrindo e o recorte tira faixas iguais de
cima e de baixo — esticar deformaria o cavaleiro.

### As três armadilhas do desenho, e a que estava diagnosticada errada

- **`StretchDIBits` não falha por causa do `HALFTONE`.** Ontem o diagnóstico foi
  esse, e estava errado: tirar o HALFTONE **e** a escala não consertou — a
  versão "corrigida" rodou três vezes seguidas e falhou na quarta, devolvendo 0
  com o erro do sistema dizendo *"operação concluída com êxito"*. É a função. A
  saída foi trocá-la por `CreateDIBSection`, que devolve o ponteiro dos bits
  para nós escrevermos. Fica o lembrete: **"mexi e parou de acontecer" não é
  diagnóstico quando o defeito é intermitente.** O `CLAUDE.md` §5 foi corrigido.
- **Interpolar cor em tipo sem sinal.** Num gradiente que escurece (240 → 200),
  `r2-r1` dá −40 num `uintptr` e vira um número astronômico. O botão verde
  nasceu **ciano** e a barra dourada nasceu **invisível** — as duas ao mesmo
  tempo, porque a conta é a mesma.
- **`DrawTextW` come o `&`.** Sem `DT_NOPREFIX`, o `&` do crédito "Gravity Corp.
  & Lee Myoungjin" é lido como marca de tecla de atalho: o caractere some e a
  letra seguinte sai sublinhada.

### O que foi tocado

| arquivo | o quê |
|---|---|
| `patcher/janela.go` | reescrita: moldura própria, arte, rodapé, botão e barra desenhados |
| `patcher/recursos/fundo.jpg` | a arte nova da capa |
| `patcher/main.go`, `auto.go` | independência do nome do exe; barra cheia quando não há o que aplicar |
| `patcher/Jogar.ini` | renomeado de `Atualizador.ini` |
| `ferramentas/limpa_cliente.py` | **novo** — a faxina do cliente |
| `ferramentas/monta_patch.py`, `publica_patch.sh` | o nome novo do exe |
| `CLAUDE.md` §5 | a armadilha do `StretchDIBits`, agora com a causa certa |
| `patcher/LEIAME.md` | §4b, a janela; e o que sobrou de pendência |
| `REFERENCIA.md` | `Jogar.exe`, `_extras\`, `_backups_removidos\` |

### O ícone do Jogar.exe, e um gerador de recurso COFF (2026-08-16)

Última pendência visível do Atualizador: o exe usava o ícone padrão do Windows.
O dono mandou o desenho (um meteoro, que é o que cai no céu da capa) e ele
virou ícone de sete tamanhos, de 16 a 256.

**O gerador é nosso** (`patcher/icone/`, em Go, ~200 linhas). A ferramenta
conhecida para pôr ícone em programa Go é o `rsrc`, de terceiro; escrever o
nosso segue o mesmo critério do resto do Atualizador — o que vai para a máquina
dos jogadores não depende de binário que ninguém neste projeto leu. O formato
COFF de recurso não muda desde 1993, então é código que se escreve uma vez.

Saem dele o `recursos/icone.ico` (atalho, site, instalador) e o
`icone_windows_amd64.syso`, **versionado**, que o `go build` embute sozinho.

### As três armadilhas do ícone, e todas falham calado

- **Ícone no exe e ícone na JANELA são coisas separadas.** O recurso faz o
  Explorer desenhar o arquivo; a barra de tarefas e o Alt+Tab leem o `hIcon` da
  **classe da janela**. Acertar o primeiro e achar que o segundo veio junto é o
  erro natural — foi preciso um `LoadIconW` no `WNDCLASSEX` para fechar.
- **Cada folha da árvore de recursos precisa de uma relocação** no objeto COFF.
  Sem elas o `OffsetToData` aponta para o lugar errado dentro do exe e o Windows
  cai no ícone padrão: exatamente o que se vê quando não há ícone nenhum.
- **Reduzir sem ponderar pelo alfa deixa auréola escura** no contorno, porque o
  preto transparente das bordas entra na média.

Conferido nos dois lados: o `ExtractAssociatedIcon` tira do exe um 32x32 com a
transparência certa, e o `GetClassLongPtr(GCLP_HICON)` devolve handle não nulo
na janela em execução.

O `Jogar-Guerra-do-Emperium.zip` foi refeito com o exe que tem ícone.

| arquivo | o quê |
|---|---|
| `patcher/icone/main.go` | **novo** — o gerador de `.ico` e `.syso` |
| `patcher/icone_windows_amd64.syso` | o recurso embutido, versionado |
| `patcher/recursos/icone-origem.png`, `icone.ico` | a fonte e o ícone |
| `patcher/janela.go` | `LoadIconW` na classe da janela |
| `patcher/LEIAME.md` | §4c, o ícone; a pendência saiu da §5 |

---

## O instalador: o primeiro download deixa de ser uma pasta do Drive (2026-08-16)

O Atualizador resolveu a segunda vez em diante; **a primeira continuava sendo
um link do Google Drive com 4,9 GB**. O dono trouxe o pedido já com um desenho:
a parte imutável do kRO ficaria no Drive, a nossa no droplet, e um instalador
baixaria as duas e criaria o atalho.

Duas metades desse desenho não sobreviveram ao exame, e as duas por motivo
técnico — não por gosto.

### Por que o Google Drive não serve, e por que o droplet também não

**O Drive não entrega arquivo grande por URL.** Acima de ~100 MB ele devolve
uma página HTML de aviso de vírus em vez do arquivo; existe o truque do
`confirm=t`, que já mudou várias vezes. O instalador gravaria HTML dentro do
zip e o sha256 falharia **para todo mundo ao mesmo tempo**. Pior, há cota de
download por arquivo público: 3,4 GB vezes algumas dezenas de jogadores estoura,
e a resposta vira erro por 24 h — sem nada que possamos fazer.

**E o droplet não tem banda sobrando para isso.** São 3,4 GB **por jogador**,
saindo pela mesma placa de rede que atende o map-server. Dez instalações
simultâneas e o jogo engasga. O `libraro` continua servindo os patches, que são
pequenos; o primeiro download é outro problema.

### Cloudflare R2 foi a primeira escolha, e caiu por uma linha da documentação

O R2 tem **egress zero** — a taxa que normalmente mata esse caso de uso — e os
3,9 GB caberiam no free tier. A objeção veio do dono, e era de arquitetura, não
de preço: usar domínio próprio no R2 exige a zona inteira na Cloudflare, e ele
não queria a administração do `filiponegrao.com.br` sob o guarda-chuva deles.

Procurou-se o meio-termo, e **ele não existe no plano gratuito**. Três caminhos,
os três fechados pela documentação oficial:

- domínio próprio no R2 exige o domínio como zona na conta (*"must have been
  added as a zone in the same account"*);
- **delegar só o `cdn.`** por NS, mantendo o resto na DigitalOcean, é
  **Enterprise** — a tabela de disponibilidade é `Free: No / Pro: No /
  Business: No / Enterprise: Yes`;
- apontar um CNAME para o `r2.dev` é **listado como caminho não suportado**, e
  o próprio `r2.dev` é documentado como *"rate-limited… only for development"*,
  com o limite **não publicado**.

### DigitalOcean Spaces, que era a resposta melhor

$5/mês, **250 GiB de armazenamento e 1 TiB de saída**, CDN incluído. Resolve a
objeção do dono melhor que qualquer alternativa: **não acrescenta fornecedor
nenhum** — conta que ele já tem, DNS que já está lá, e o subdomínio próprio sai
com um CNAME dentro da zona que ele já administra.

Bucket `ftn` em `tor1`, servido por **`cdn.filiponegrao.com.br`**. O subdomínio
próprio resolveu de graça um problema que estava em aberto: o endereço fica
congelado dentro do exe que o jogador baixou, e trocar de provedor um dia é
mudar um CNAME em vez de republicar o instalador de todo mundo.

A instalação mede **3.499 MB**, o que dá ~299 por mês dentro da mensalidade.

### O empacotamento, e o número que mudou a economia

`ferramentas/monta_cliente.py` divide o cliente em cinco pedaços e escreve
`patcher/base.txt` — o irmão do `patches.txt`, com **seis** campos em vez de
cinco. O campo a mais é o tipo, e ele existe porque o `data.grf` não é um zip:

| pedaço | bruto | baixado |
|---|---|---|
| `data.grf` | 3.021 MB | 3.021 MB — vai **bruto** |
| `0002-musicas.zip` | 323,6 MB | 318,1 MB |
| `0003/0004-nosso-*.zip` | 765,6 MB | **134,4 MB** |
| `0005-resto.zip` | 58,7 MB | 26,1 MB |

**A nossa parte inteira comprime a 17%.** Os 800 MB de `data\` que pareciam o
peso do pacote são 134 MB na rede — são sprite, `.lua` e texto. O que pesa é o
GRF do kRO, que nunca muda. Consequência prática: **refazer a base quando o
nosso conteúdo mudar custa 134 MB**, e os outros três pedaços continuam com o
mesmo sha no bucket. O `--so nosso` existe para isso.

O `data.grf` vai bruto porque zipá-lo não ganha nada — já é comprimido por
dentro — e custaria o dobro de disco no jogador. E ele é publicado **direto de
`cliente\`**, sem cópia: copiar 3 GB para depois subir seria meia hora de disco
à toa.

A contabilidade da varredura fechou em **19.904 arquivos no cliente, 19.866
empacotados, 36 de estado local e 2 de propósito** (o `Jogar.exe` e o `.ini`,
que o jogador já tem na mão). Era o risco do §5b: esquecer o `itemInfo.lua` e
descobrir com todo item sem nome na loja.

### O instalador é o mesmo exe

**Não há um segundo programa.** O `Jogar.exe` decide o que é pela pasta em que
está: com `data.grf` ao lado, atualiza; sem, instala. O jogador baixa 9 MB, abre
numa pasta qualquer, escolhe onde instalar, e recebe os 3,4 GB — e ao terminar a
base o fluxo emenda nos patches publicados desde que o pacote foi montado.

O que foi escrito para isso:

| arquivo | o quê |
|---|---|
| `ferramentas/monta_cliente.py` | **novo** — o empacotador, com `--confere` e `--so` |
| `ferramentas/publica_cliente.sh` | **novo** — sobe ao bucket, pedaços antes da lista |
| `patcher/base.txt` | **novo**, versionado — o registro dos cinco pedaços |
| `patcher/instala.go` | **novo** — a base, o disco, a cópia de si mesmo, o `.ini` |
| `patcher/atalho.go` | **novo** — o `.lnk` por COM, com vtable tipada |
| `patcher/pasta.go` | **novo** — a caixa nativa de escolher pasta |
| `patcher/atalho_test.go`, `instala_test.go` | **novos** — os primeiros testes do projeto |
| `patcher/patch.go` | retomada por `Range`; `baixaTexto` extraída |
| `patcher/janela.go` | a tela de escolha: pasta, `Mudar…`, checkbox, `INSTALAR` |
| `patcher/main.go` | o desvio instalar/atualizar; `url` e `base` separadas |

**As duas URLs são separadas de propósito** (`url` = patches no droplet,
`base` = instalação no CDN). Foi um erro real: a primeira versão usava uma só,
e o instalador teria procurado a `base.txt` no droplet. Apareceu ao testar o
CDN, não ao compilar.

### Por que este é o primeiro código do projeto com teste automatizado

Duas coisas aqui não se provam clicando. O `atalho.go` chama COM percorrendo
vtable, onde um índice errado **trava o processo** em vez de devolver erro, com
a pilha dentro do shell do Windows. E a retomada só se manifesta quando a
conexão cai no meio de 2,95 GB — que ninguém consegue provocar de propósito na
hora de testar, e que falharia **depois** de o jogador baixar tudo.

O `TestRetomada` grava um `.parte` pela metade, chama o mesmo `baixa()` do
instalador contra o CDN de verdade, e confere o sha256 do resultado. Passou
retomando de 13.671.718 bytes e fechando o sha dos 27.343.437.

As vtables viraram **struct** em vez de índice numérico depois que o `go vet`
acusou a aritmética sobre `unsafe.Pointer`. Custou vinte linhas e pagou duas
vezes: o aviso sumiu e cada método passou a ter nome.

### Três armadilhas, todas subidas para o `CLAUDE.md` §5

**A chave do Spaces era somente-leitura, e o publicador dizia "(vazio)".** A
primeira versão do `remotos()` era `lsf … 2>/dev/null || true`, e "o bucket está
vazio" e "eu não consigo falar com o bucket" saíam idênticos na tela. Um
`PutObject` de **14 bytes** separou os dois em um comando.

**O rclone chama `CreateBucket` antes de subir arquivo grande**, e a chave tem
acesso ao conteúdo mas não permissão de criar bucket. A mensagem fala em
`CreateBucket` e manda procurar defeito na chave, que está certa. Resolve com
`--s3-no-check-bucket`.

**`nslookup` sai com código 0 mesmo em NXDOMAIN.** Uma sonda `nslookup … && echo
"resolve"` imprimiu "resolve" para um host que não existia, e deu o CDN por
propagado quando ele não estava. O que decidiu foi `curl`, que falha de verdade.

### O que ficou de fora

O `PENDENCIAS.md` §5b pedia um `monta_cliente.py` que reconstruísse o cliente
**do zero**, a partir de um kRO limpo. Não é o que foi feito: o que existe
empacota o cliente que está nesta máquina. A dívida continua aberta — o exe
segue sendo binário de origem única (com o `.epi` do NEMO ao lado), e o
`cliente\data\` continua sem gerador. O instalador tornou isso menos urgente,
não resolvido.

### O primeiro teste em outra máquina, e a casa que faltava

Os 4,2 GB desceram certos, o sha256 de cada pedaço fechou, o atalho apareceu —
**e o jogo não abriu**. Dois sintomas, que pareciam dois problemas:

```
sem admin:  fork/exec C:\GuerraDoEmperium\GuerraDoEmperium.exe:
            The requested operation requires elevation
com admin:  Cannot init d3d OR grf file has problem
```

Eram **o mesmo problema**. O cliente escolhe o dispositivo Direct3D lendo
`HKLM\SOFTWARE\Gravity Soft\Ragnarok` — `DEVICENAME`, `GUIDDEVICE`,
`GUIDDRIVER`, mais som —, chave que quem escreve é o **`Setup.exe`**. Nesta
máquina ela existe desde sempre (`DEVICENAME: NVIDIA GeForce GTX 1650
Ragnarok`); numa máquina nova, não. E como ela mora em `HKEY_LOCAL_MACHINE`,
escrevê-la exige privilégio — daí o exe pedir elevação, e daí o `exec.Command`
do Go falhar, porque o `CreateProcess` **não sabe elevar**.

O que denunciou não foi o log: foi comparar o registro desta máquina com o que
uma máquina nova teria. A mensagem do cliente junta dois casos opostos num
`OR` e manda conferir o GRF, que estava perfeito.

**O instalador entregava o cliente inteiro e parava uma casa antes do fim.**
É a `CLAUDE.md` §4.9 um degrau adiante: lá as duas metades da configuração
divergiam entre arquivos, aqui uma delas não é arquivo nenhum.

Três consertos, e o segundo veio do dono:

| o quê | onde |
|---|---|
| `ShellExecuteW` no lugar de `exec.Command` — ele consulta o manifesto e levanta o UAC | `patcher/executa.go` |
| **o atalho nasce marcado como "Executar como administrador"** (`SLDF_RUNAS_USER` via `IShellLinkDataList`), e o jogo herda o token — um UAC só, na abertura | `patcher/atalho.go` |
| o `Setup.exe` roda sozinho no fim da instalação, **e a instalação espera ele fechar** — o cliente lê a chave na inicialização, então abrir os dois juntos leria o registro que o Setup ainda não escreveu | `patcher/video.go`, `instala.go` |

A detecção lê a chave pelos **dois** nomes possíveis (`KEY_WOW64_32KEY` e o
caminho `WOW6432Node` explícito), porque o Atualizador é 64-bit e o cliente é
32-bit: a mesma chave tem nome diferente dependendo de quem pergunta. E na
dúvida ela responde **"configurado"** — um falso negativo abriria o Setup para
quem não precisa, um falso positivo só deixa o jogo falhar como falharia de
qualquer jeito.

Os dois testes novos cobrem exatamente o que não se vê daqui: que o bit
`RunAsUser` chega ao **arquivo** `.lnk` (byte 21, `0x20`) e não apenas à chamada
COM, e que a leitura do registro acerta o caminho numa máquina onde o jogo
comprovadamente roda.

### A fase 1 (2026-08-16)

Com o instalador testado em outra máquina e funcionando, o dono decidiu **não
publicar o Atualizador pelo canal de auto-atualização**: quem já tem cliente
vai rebaixar o instalador novo, e este passa a ser o definitivo. Menos uma
versão em circulação.

O `Jogar.exe` foi para o bucket — **`https://cdn.filiponegrao.com.br/Jogar.exe`**,
9.570.816 bytes — e o site já sabia consumi-lo: o `SITE_DOWNLOAD_URL` e a rota
`/api/config` existiam desde 2026-08-15, esperando um endereço. O que mudou no
site foi o **texto**, que ainda prometia 4,2 GB de download: agora diz que o
download é um instalador de 9 MB, que o jogo tem 3,4 GB e que ele continua de
onde parou se a conexão cair.

**Isto fecha a fase 0.** O que existia era um servidor de pé sem como chegar
nele; o que existe agora são três pontes, e as três são nossas — o site entrega
o instalador, o instalador entrega o jogo, o Atualizador entrega toda melhoria
seguinte. Nenhuma delas depende do Google Drive, e nenhuma correção de cliente
fica presa na máquina de quem a fez.

E isso muda a natureza do trabalho: **agora existe gente do outro lado.** Toda
entrega passa a ter um destino — servidor, patch, base ou site —, e escolher o
errado falha em silêncio. Daí a tabela nova em `RECEITAS.md` §0, apontada do
cabeçalho do `CLAUDE.md` e da §4.18: é a primeira coisa a consultar antes de
dar qualquer coisa por entregue.

O passo que falta é de infra e ficou preparado em `IMPLANTACAO.md` §9b — a
variável no `/etc/guerra/site.env`, que o deploy **não** sobrescreve, porque o
`configura_web.sh` preserva o arquivo onde mora o `SITE_SEGREDO`.

---

## Quatro pedidos da primeira semana com gente do outro lado (2026-08-16)

Os quatro chegaram juntos, e o que os separa não é o assunto — é **o destino**
(`RECEITAS.md` §0). Três são servidor e ficaram prontos esperando o deploy, que
o dono queria fazer junto com um anúncio; um é cliente, e por isso **já está no
ar** como patch `0002`.

### 1. O servidor está três horas à frente do Brasil

O dono viu **00:50** no servidor com 21:50 em Brasília. Não é o rAthena: a
imagem da DigitalOcean nasce em `Etc/UTC` e nada no provisionamento mexia nisso.

Importa porque **o servidor de jogo não tem relógio próprio**. O `gettime` de
script e os rótulos `OnClock<hhmm>` leem a hora **local** da máquina, sem
conversão — e a Guerra do Emperium está escrita em horário de Brasília
(`npc/guerra/horario_da_guerra.txt`, quinta 20–22 e domingo 18–20). Em UTC, a
guerra de quinta abriria às **17h** do Brasil. Falha calada e completa: o script
roda, o anúncio sai, o Emperium nasce — na hora errada. O cabeçalho daquele
arquivo já avisava, em 2026-08-13: *"se um dia o servidor mudar de fuso, estes
números mudam junto e nada avisa"*. Não era um "se": nunca tinha sido conferido.

A correção é uma linha, e ela entrou no `ferramentas/provisiona.sh` como **passo
0** — antes do swap, porque é o único passo que muda a hora de tudo que roda
depois, inclusive o carimbo dos logs que o MariaDB cria nos passos abaixo:

```bash
timedatectl set-timezone America/Sao_Paulo
```

`America/Sao_Paulo`, e não `-03`: o Brasil não tem horário de verão desde 2019,
mas se voltar a ter quem resolve é o `tzdata` num `apt upgrade`. Fuso fixo teria
de ser lembrado por alguém.

**Processo que já está no ar mantém o fuso antigo** — os quatro servidores
precisam ser reiniciados depois, e é isso que o passo avisa na tela.

### 2. Autoloot não existia, e a pista era enganosa

O `@autoloot` estava no grupo **1** (`Super Player`), que nenhuma conta de
jogador tem. O grupo **0** (`Player`, o de toda conta nova) só tinha `changedress`
e `resurrect`. Na prática o recurso não existia no servidor, e a única pista era
o *"Unknown Command"* na tela — que **não** quer dizer falta de permissão
(`CLAUDE.md` §3), então quem testasse concluiria que o comando não foi compilado.

Entraram os **três** comandos da mesma família, porque são três formas do mesmo
recurso e o rAthena as trata em separado: `@autoloot <0-100>` (tudo), `@alootid`
(um item) e `@autoloottype` (uma categoria).

**Nenhum deles vem ligado**, e foi decisão do dono: o jogador digita quando
quiser e o estado vale até o logout. Ligar sozinho exigiria um `OnPCLoginEvent`
com `atcommand`, e aí quem desligasse voltaria a ter ligado no login seguinte.

Pela lei da customização (§2), nada disso foi escrito no arquivo do rAthena: o
ajuste mora em `conf/guerra/groups_guerra.yml` e o `conf/groups.yml` ganhou **uma
linha** no rodapé, antes do `conf/import/groups.yml` — que continua podendo
sobrescrever, por máquina.

Isso funciona por uma propriedade do leitor que vale a pena registrar: o
`PlayerGroupDatabase::parseBodyNode` (`src/map/pc_groups.cpp:74`) procura o `Id`
antes de criar, e **grupo que já existe não é recriado** — os campos do import
são aplicados por cima. Por isso o arquivo novo não repete `Name` nem `Level`:
ele é só a diferença.

Recarrega com **`@reloadatcommand`**, que chama o `pc_groups_reload`
(`src/map/atcommand.cpp:4422`). Não é `@reloadscript` nem `@reloadbattleconf` —
e errar aqui faz a mudança parecer que não pegou.

### 3. A censura era do cliente, e estava num arquivo do GRF

O pedido: *"temos uma censura de inglês; palavra em português passa, em inglês
não. Quero tirar tudo."*

Não havia nada disso no rAthena — o emulador não filtra palavra nenhuma —, e o
exe também não: `fuck`, `shit`, `swear`, `badword` e irmãos **não aparecem no
binário**. A censura mora em **`data\manner.txt`**, dentro do `data.grf`: 1409
linhas, uma palavra por linha, quase tudo coreano em CP949, e no meio delas
**25 em inglês** — `fuck`, `sex`, `shit`, `bitch`, `suck`, `pussy`, `ass`, `cum`,
`damn`, `penis`, `vulva` e variações com espaço (`F U C K`, `S E X`). Nenhuma
palavra em português na lista, o que explica exatamente o sintoma descrito.

O remédio é um override em `cliente\data\manner.txt`, que o `DataFolderFirst`
(patch do exe) faz vencer o GRF. **Ele não ficou vazio de propósito**: leva uma
única palavra que ninguém digita (`zzguerradoemperiumzz`), o que preserva o
formato do arquivo sem censurar nada de verdade. Arquivo de zero byte seria uma
aposta no leitor do cliente, e não há por que apostar.

Como é cliente, foi por **patch** — `0002-sem-censura-de-palavras.zip`, montado e
publicado no mesmo dia. O jogador recebe na próxima vez que abrir o `Jogar.exe`.

### 4. A Criança de Prontera ganhou o balão de verdade

Desde 2026-08-15 a Criança do Amuleto (`prontera 142,186`) dizia a **palavra**
"Quest" num balão de fala, de 5 em 5 segundos, por `npctalk`. O comentário do
arquivo justificava assim: *"não existe ícone de '!' que o script alcance"*.
Existe — e é o `questinfo`.

A confusão era com o **`showevent`**, que de fato não serve aqui: ele exige
jogador anexado, e o `OnInit` roda na subida do servidor, sem ninguém. O
`questinfo` registra a condição no mapa e quem reavalia é o servidor, sozinho, a
cada ação do jogador (entrar no mapa, mudar de nível, ganhar item, mexer em
quest) — `pc_show_questinfo`, `src/map/pc.cpp`.

O ganho não é só estético: o balão novo é **por jogador**. Aparece só para quem
ainda não aceitou (`SalaSecretaOrdem == 0`) e some no instante em que aceita —
quem faz sumir na hora é um `questinfo_refresh` logo depois do
`SalaSecretaOrdem = 1`. Sem ele o ícone ficaria até a próxima ação que o
servidor reavalia por conta própria, o que engana justamente quem acabou de
falar com ela.

**E não corre o risco da §5 do `CLAUDE.md`** — "quest que o cliente não conhece
derruba o cliente". Quem derruba é a **janela** de missões, que lê o
`QuestInfoList` por ID. O balão é o pacote `0x446` (`clif_quest_show_event`), que
só desenha um ícone sobre um NPC e não carrega ID de quest nenhum. A missão do
Amuleto continua fora do sistema nativo, como o cabeçalho do arquivo explica.

Uma consequência operacional que engana: **depois de um `@reloadscript` o balão
só aparece para quem sair e voltar ao mapa.** O `pc_show_questinfo` desiste
enquanto a lista do jogador tiver tamanho diferente da lista do mapa (*"init was
not called yet"*), e quem redimensiona é a entrada no mapa. Não é defeito.

De quebra, o índice narrado tinha a Criança em `prontera 142,168`; o NPC nasce em
`142,186`. Corrigido.

---

## Esta máquina virou dev, e o apontamento ganhou uma trava (2026-08-16)

Com os quatro pedidos acima prontos e o servidor de produção no ar, o dono
separou os dois mundos: **`C:\GuerraDoEmperium\cliente` passa a ser o cliente de
dev/hml**, apontado para `127.0.0.1`, e produção se testa de **outra pasta**,
instalada pelo instalador como um jogador faria. É a separação que impede
"funciona aqui" de passar por "funciona para quem baixou".

Trocar o apontamento é editar o `<address>` — mas **dos dois** arquivos, e é a
mesma armadilha de 2026-08-14: este exe é `<servertype>sakray</servertype>`,
então quem vale é o `data\sclientinfo.xml`; o `clientinfo.xml` fica igual porque
há caminho de código que lê o outro. O endereço de produção ficou no backup ao
lado de cada um (`.BACKUP-138.197.155.31`), e o sufixo tem `BACKUP` no nome de
propósito: é o padrão que as duas ferramentas de empacotamento filtram, então
ele nunca vai parar no jogador.

### A trava, e por que ela precisava existir

Essa mudança criou um jeito novo de estragar tudo em silêncio, e ele é caro nos
dois caminhos de entrega:

- **base** montada com o cliente apontado para casa → 3,4 GB corretos, sha256 de
  cada pedaço fechando, CDN servindo — e **todo jogador novo tentando logar na
  própria máquina**;
- **patch** que inclua um dos dois xml → **tira do ar quem já tem o cliente**, e
  o que chega de volta é "não consigo entrar".

Nada no caminho olhava para esse campo, e ele mora num arquivo que ninguém
revisa antes de publicar. Então `monta_cliente.py` e `monta_patch.py` passaram a
recusar endereço local (`127.0.0.1`, `localhost`, `0.0.0.0`, `::1`, vazio) —
o primeiro **antes** do sha256 de 3 GB, o segundo só quando um dos dois xml está
de fato no patch. `--permite-local` passa por cima na base, para quando for de
propósito. As duas foram exercitadas com o cliente já apontado para local, e as
duas recusaram.

### E o servidor local subiu junto

Os quatro servidores locais voltaram ao ar para o teste, e a subida serviu de
conferência de sintaxe das mudanças do dia: **nenhum erro novo no
`log/map-msg_log.log`** — nem do `questinfo` da Criança, nem do
`conf/guerra/groups_guerra.yml`. Este último é a prova que interessa: import
que não abre gera um `Failed to open` do `YamlDatabase::load`
(`src/common/database.cpp:96`), e comando inexistente em grupo gera aviso do
`parseCommands`. Não houve nenhum dos dois. Os avisos que restam são os de
sempre — preço de 1 zeny nas lojas e guardião em castelo sem dono.

## O instalador que virou atualizador na pasta errada (2026-08-16)

O primeiro relato de fora: um amigo baixou o `Jogar.exe`, abriu, e **antes de
baixar coisa nenhuma** levou a mensagem **"não encontrei
GuerraDoEmperium.exe"** — texto de atualizador na cara de quem estava
instalando, e sem nenhuma saída na tela.

A causa está inteira em uma linha. O mesmo exe é o instalador e o atualizador,
e quem decidia qual dos dois ele era hoje era o `PrecisaInstalar`, que olhava
**só o `data.grf`**:

```go
func PrecisaInstalar(raiz string) bool {
	_, err := os.Stat(filepath.Join(raiz, "data.grf"))
	return err != nil
}
```

O comentário defendia a escolha — o `data.grf` tem 2,95 GB e nunca é criado por
acidente —, e ela erra num caso que o autor não considerou: **`data.grf` existe
em QUALQUER instalação de Ragnarok**, inclusive na de outro servidor privado e
na do bRO. O amigo tinha um cliente antigo e pôs o `Jogar.exe` dentro daquela
pasta. O programa concluiu "já instalado", entrou no modo atualizador, conferiu
a lista de patches (nenhum faltava — ele não tinha `aplicados.txt`… e também não
tinha o nosso cliente), acendeu o **JOGAR**, e o clique caiu no `Executa`, que
não achou o exe do jogo porque ele nunca esteve ali.

**O erro estava certo; a pergunta é que estava errada.** A mensagem descreve
com precisão o que aconteceu no fim do caminho, e o caminho inteiro não deveria
ter sido tomado.

### O conserto

`PrecisaInstalar` passou a exigir **as duas metades** — o `data.grf` e o exe do
jogo (`cfg.jogo`, para não repetir o nome em dois lugares):

```go
func PrecisaInstalar(raiz, jogo string) bool {
	for _, nome := range []string{"data.grf", jogo} {
		if _, err := os.Stat(filepath.Join(raiz, nome)); err != nil {
			return true
		}
	}
	return false
}
```

Olhar só o exe seria o erro simétrico (pasta com um exe velho e sem `data.grf`
se calaria diante de uma instalação que não existe), e é por isso que os dois
são exigidos, e não um ou outro. Instalar por cima é barato: `aplicaPedaco`
pula o pedaço cujo sha256 já bate em disco — quem tiver por acaso o **nosso**
`data.grf` não rebaixa 3 GB, e quem tiver o de outro servidor rebaixa, que é o
certo.

O caso virou o primeiro teste **offline** do Atualizador
(`TestPrecisaInstalar`, quatro combinações), e é o teste que mais importa do
lote: é a única porta entre as duas metades do programa, roda sem rede e por
isso é sempre exercitado.

### O que isto ensina, e vale para o instalador inteiro

Toda mensagem do modo atualizador é, para quem está instalando, uma **falha sem
saída** — não há botão que leve de volta à tela de escolher pasta. Então a
regra é a do `CLAUDE.md` §5, um degrau acima: *sonda que responde pela pergunta
errada*. "Tem `data.grf`?" não é "tem o jogo instalado?", do mesmo jeito que
"o patch foi aplicado?" não era "o patch teve efeito na tela?".

O `VERSAO` subiu para **2**, e o `Jogar.exe` foi recompilado.

### Publicado em 2026-08-16, nos DOIS lugares

Um só não bastava, e o que decide qual importa é **quem tem o problema**:

- **`publica_patch.sh --atualizador`** — o canal de auto-atualização, que
  alcança quem **já instalou**. `Jogar-2.exe` no ar, com o `patcher.txt`
  apontando para ele (o script recompila antes de enviar, então não há como
  publicar binário velho por engano).
- **O bucket** (`cdn.filiponegrao.com.br/Jogar.exe`), que é de onde o **site**
  serve o botão Baixar. **Este é o que resolve o caso do relato**: quem caiu
  nele não tem instalação nossa, logo não passa pelo canal de auto-atualização
  nunca. Publicar só o canal consertaria exatamente quem não precisava.

A conferência que fechou: o sha256 do que o CDN devolve
(`38c454c2ae1bc8…`) é **byte a byte** o do `patcher.txt` e o do binário local —
os dois canais servem o mesmo exe, e não uma versão cada.

**Falta o teste na tela**, que nenhuma sonda offline substitui: baixar do site
numa pasta que já tenha um `data.grf` e abrir. Tem de aparecer a tela de
escolher onde instalar, e não o botão JOGAR.

## 48 itens nas lojas de Prontera e 5 na Máquina de Sombrios (2026-08-16)

A maior leva que o Mercado Contemporâneo já recebeu de uma vez, e a primeira
depois de a fase 1 abrir — ou seja, a primeira em que o que entra na vitrine
alcança jogador de verdade, e por isso a primeira em que a §0 do `RECEITAS.md`
teve de ser respondida item a item: **metade deste trabalho não vai pelo
deploy.**

O pedido chegou como duas listas. A primeira, 48 itens "para as lojas de
Prontera", sem dizer quais lojas; a segunda, 6 itens para a Máquina de
Sombrios Gerais.

### Onde caiu cada peça, e quem decidiu

Quem decidiu foi o `Locations:` do `item_db`, e não o nome nem a ordem do
pedido (regra 4.14) — a lista vinha misturada, com anéis, capas e escudos numa
coluna só:

| loja | entraram | ficou com |
|---|---|---|
| Acessorista | 35 | 49 |
| Capeiro | 5 | 23 |
| Escudeiro | 3 | 11 |
| Ocleiro | 2 | 29 |
| Senhor das Armas | 2 | 25 |
| Lorde das Armaduras | 1 | 9 |

**Três peças cairiam na loja errada por leitura de nome.** As "asas de
singrum" e a "penugem de singrum" são `Head_Mid` e foram para o Ocleiro, não
para o Capeiro; e o **Punhal de Matagi**, que o nome entrega como arma, é
`Both_Accessory` e foi para o Acessorista.

O preço saiu da regra 4.16, e por isso não é uniforme: **19 acessórios entraram
a 1 zeny** (sem `Buy` no `item_db`) e **16 a 20 zeny** (`Buy: 20`), e o mesmo
vale nas outras lojas. Nenhum dos 48 acrescenta linha de `discounted buying
price` na subida — item posto pelo preço de compra não dispara aquele aviso.

### O trabalho não estava nos 48, estava em doze

Quarenta e seis dos 48 já existiam no servidor. O que custou:

| o que faltava | quantos | por onde |
|---|---|---|
| entrada no `itemInfo.lua` | 9 | `completa_iteminfo.py` |
| os 4 arquivos de arte | 7 | `instala_visual.py` |
| capa com `View` acima do teto | 2 | `estende_robeid.py` + `instala_manto.py` |
| não existia no servidor | 2 | `db/guerra/item_db.yml` |

**Os dois que não existiam** viraram a QUARTA LEVA DE PLACEHOLDERS:

- **Luvas de Somatologia (490497).** A resistência que a descrição do bRO chama
  de "Cobaias" não é raça nenhuma — é o grupo `RC2_BIOLAB`, e isso foi
  conferido e não suposto: a descrição lista as vinte cobaias por nome, e o
  grupo `Biolab` do `mob_db` tem exatamente esses 51 monstros. Também são
  **dois** bônus e não um: `bAddRace2` só alcança o físico, e "dano físico e
  mágico" exige o `bMagicAddRace2` ao lado.
- **Lacma (28739).** E aqui a armadilha: **este item já existe no nosso
  rAthena, no ID 13049**, com script próprio e os mesmos números. Ainda assim
  quem entrou foi o 28739, porque o `itemInfo.lua` deste cliente mostra o 13049
  com o nome **coreano** — e item sem nome em português não entra em loja
  (regra 4.2). O 28739 é a reedição traduzida. Onde os dois discordam está
  anotado na entrada.

### As duas capas com `View` acharam um erro de ferramenta

A Som do Luar (480446, View 165) e as Asas de Garuda (480278, View 160) são as
primeiras capas de **status** desta loja a precisar da tabela de manto por
conta própria — a 480188, que era a única com `View` até aqui, andava de carona
na versão cosmética dela. As duas nasceram acima do teto de 120 e gastaram um
slot doador cada; dos 39 sem arte, sobram 28 livres.

E o caminho estava quebrado em dois pontos, os dois no `instala_manto.py`:

1. **A trava de tipo era `Costume_Garment` e só.** Ela nasceu estreita em
   2026-08-08, quando o Manteleiro era a única frente de manto, e ficou errada
   no dia em que uma capa de status precisou de arte. O cliente não pergunta em
   que slot a peça se equipa: quem manda o sprite desenhar é o `View`. Eram
   **duas definições da mesma coisa** — o `estende_robeid.manto()` já lia os
   dois locais — e só uma estava certa.
2. **O `item_de` devolvia a entrada do rAthena, não a nossa.** O
   `vv.le_item_db` recebe os dois arquivos e devolve uma lista chata, com uma
   entrada por bloco; a primeira é a do `db/re/`, que traz o `View` **original**
   (160, 165). O script então não achava aquele número na tabela do cliente —
   que para em 120 de propósito — e respondia *"view X só existe no spriterobeid
   do bRO, rode antes o estende_robeid.py"*. Alto, e pelo motivo errado.

O segundo é o mais interessante porque **não era regressão desta rodada**: os
dez mantos já instalados eram recusados exatamente do mesmo jeito. Eles só
tinham escapado porque a arte deles foi copiada em 2026-08-09, **antes** de o
`View` ser reapontado — a arte vai para uma pasta cujo nome não depende do slot,
então ela sobreviveu à troca e ninguém rodou a ferramenta de novo para
descobrir. Devolver a última entrada também não serve (o bloco de override só
tem `Id`, `AegisName`, `Name` e `View`, e `locais` viria vazio), então a
correção é **mesclar campo a campo**, com o que o override declarou vencendo.

O que provou a correção não foi o item novo: foram os **dois antigos**. Rodar
com 480155 e 480188 na mesma linha e ver *"já completo neste cliente"* é uma
marca que não depende do efeito procurado — a mesma lição do
`ajusta_tamanho_fonte.py`.

### A Máquina de Sombrios Gerais, e o item que saiu da lista

A loja de troca foi de quatro para nove, e a divisão de preço que já existia
virou a regra da vitrine, a pedido do dono: **cubo 2 Moedas Novas, combinador
1**. Não é arbitrário — o cubo é que carrega o sorteio, e o combinador é insumo.
Os cinco já existiam inteiros, então esta metade do pedido é **só deploy**: não
há patch a montar por causa dela.

O pedido trazia um sexto, o **Anel do Viajante [1] (490193)**, e ele saiu daqui
por decisão do dono no mesmo dia: é acessório de equipar, não peça Sombria, e
teria sido a única coisa vestível entre nove consumíveis. Ele aparecia nas
**duas** listas, e era cópia acidental de uma para a outra. Entrou no
Acessorista, a 1 zeny, e só lá.

### O que já está no ar e o que não está

O **patch 0003** ("Itens novos das lojas de Prontera") foi montado, publicado e
conferido no ar: 2077 arquivos, 79,45 MB crus em 11,18 MB de zip — o
`itemInfo.lua`, as duas tabelas de manto, os 28 arquivos de arte de item e os
2046 de sprite de manto. Quem abrir o `Jogar.exe` já recebe.

A lista foi montada **à mão, arquivo a arquivo, e não por `--desde`**: a
varredura por data trazia 2099 arquivos, e 53 deles eram lixo de execução do
cliente (`savedata\`, `patch\`, `ScreenShot\`, `_tmpEmblem\`, a raiz e a
`AI_sakray\`, que já foi ao jogador no patch 0001).

**O lado servidor está pronto e não foi implantado** — as linhas das seis
lojas, a loja de troca, as quatro entradas novas de `db/guerra/item_db.yml` e
os sete `Name` que o `nomes_pt_item_db.py` sincronizou. O dono vai anunciar e
subir tudo do Mac.

---

## O botão Baixar deixa o Drive, e o jogo não cai junto (2026-08-16)

O passo de infra que a §9b esperava. O instalador já estava no bucket e o site
já sabia consumi-lo desde 2026-08-15; faltava a variável no servidor, que **o
deploy não põe sozinho** — o `configura_web.sh` preserva um
`/etc/guerra/site.env` que já exista, de propósito, porque é lá que mora o
`SITE_SEGREDO`.

Agora `https://libraro.filiponegrao.com.br/api/config` responde
`https://cdn.filiponegrao.com.br/Jogar.exe`, e a página serve o texto novo: um
instalador de 9 MB, o jogo com 3,4 GB, e a promessa de continuar de onde parou.
**Nenhum caminho até o jogador passa mais pelo Google Drive.**

O que foi conferido, e não só configurado:

| conferência | resultado |
|---|---|
| o `/api/config` devolve a URL, não vazio | ✅ — vazio não quebra o botão, ele aparece *"Em breve"*, e é assim que se esquece este passo sem perceber |
| os bytes que o CDN entrega são os do registro | ✅ 9.570.816 bytes, sha256 `c8c328be…31f4f`, igual ao anotado na §9b |
| o `Range` responde **206** | ✅ — é o que sustenta "continua de onde parou", e é a única frase do site que promete algo sobre a rede |
| `Content-Type: application/x-msdownload` | ✅ — o navegador baixa em vez de desenhar |
| o texto velho sumiu da página | ✅ zero ocorrências de "4,2 GB" e de `drive.google` |

### O deploy que não se rodou, e por quê

**Havia três jogadores online** (Prontera e Comodo, nenhum deles o dono), e
entre o commit do servidor e o `origin/main` vinha o
`rathena/conf/guerra/char_guerra.txt` — o `*` e o `-` no nome de personagem. O
`atualiza_servidor.sh` reinicia o jogo sempre que `rathena/` muda, e reiniciar
derruba todo mundo com *"Erro desconhecido"*. O dono decidiu: **só o site.**

Então rodou-se o subconjunto que não encosta no jogo — `git pull`, a variável,
`systemctl restart guerra-site` —, e os quatro servidores seguiram de pé desde
as 17:40 UTC, sem ninguém cair. Deu para fazer porque o front é **servido do
disco** (`http.FileServer(http.Dir("web"))`) e nenhum `.go` tinha mudado: o
`git pull` já publica o `index.html` e o `app.js` novos, e o restart do site
existiu só para reler a variável de ambiente.

**Isso deixou uma dívida com armadilha, e ela está na `PENDENCIAS.md` §0.** O
`ANTES`/`DEPOIS` do deploy é o commit de antes do pull comparado ao de depois —
com o pull já feito, o próximo `implanta.sh` vai concluir que `rathena/` não
mudou e **não** vai reiniciar o jogo. A mudança de nome ficaria no disco para
sempre, sem entrar em vigor e sem nada avisar.

---

## O primeiro deploy completo, e o fuso que ainda estava em UTC (2026-08-17)

O `implanta.sh` já existia desde 2026-08-14, mas até aqui só tinha rodado
levando o servidor de um estado vazio ao ar. **Esta foi a primeira vez que ele
levou trabalho de conteúdo a uma produção com gente dentro** — e a primeira em
que alguém foi derrubado de propósito.

A produção estava no `9649cee` e o `origin/main` no `be300c0`: quatro commits,
nenhum deles tocando `src/` (build de 67 minutos dispensado) nem `site/`.
Subiram as 6 lojas novas, os 53 itens, o `groups_guerra.yml` com o `@autoloot`
para o grupo 0, o `barters_guerra.yml` com 5 entradas — e, de carona, o
`char_guerra.txt` da dívida da `PENDENCIAS.md` §0, que sozinho nunca teria
entrado em vigor.

### O fuso, que o deploy não teria arrumado

A conferência de antes do deploy pegou o que ninguém procurava: `ssh libraro
date` respondeu **`Mon Aug 17 03:56 UTC`** — a máquina ainda em `Etc/UTC`,
vinte e quatro horas depois de o `provisiona.sh` ganhar o `timedatectl` como
passo 0. **O passo novo nunca chegou à máquina que já estava de pé**, porque o
deploy não roda o provisionamento; ele faz `git pull`, compila e reinicia.

Sem isso, a Guerra do Emperium de quinta às 20h teria aberto às **17h** do
Brasil, calada — o script roda, o anúncio sai, o Emperium nasce, na hora
errada. O conserto foi uma linha, e a **ordem** é que importou: o
`timedatectl set-timezone America/Sao_Paulo` **antes** do `implanta.sh`, para
que o restart do deploy fosse também o restart que faz os quatro processos
lerem o fuso novo. Duas coisas por um preço só.

A regra que saiu daí está no `CLAUDE.md` §5, na entrada do fuso: passo novo de
`provisiona.sh` se aplica à mão na produção no mesmo dia, senão vale só no
papel.

### O jogador que caiu era o dono

Havia **um** personagem online — `Abemus`, em `prt_in`, com conexão viva de
verdade no map-server (o `ss -tn` mostrando o IP; a coluna `online` da tabela
`char` sozinha não prova nada, porque fica presa depois de queda). Era o
próprio dono, que pediu para tocar assim mesmo: *"quero ver como seria tocar o
deploy com alguém online"*. Os quatro serviços reiniciaram entre 00:59:39 e
00:59:42, já no horário de Brasília.

### O que a subida disse do lado do servidor

| conferência | resultado |
|---|---|
| pré-voo local e no servidor (caixa de caminho, `\r`, U+FFFD) | ✅ 1136 caminhos, os dois lados aprovados |
| `Unknown syntax` no map-server | ✅ nenhum |
| `[Error]` no carregamento | 4, todos do parser do `item_db` sobre gênero de chicote e instrumento — inerentes, não são nossos |
| `npc/guerra/barters_guerra.yml` | ✅ 5 entradas lidas |
| `conf/guerra/char_guerra.txt` | ✅ *"Done reading"* no char-server, às 00:59:39 |
| os quatro serviços + site + apache + mariadb | ✅ `active` |

O `char_name_option: 1` estar lido é o que fecha a dívida do lado do servidor;
**a outra metade é de tela** e foi para a `PENDENCIAS.md` §1 — criar um
personagem com `*` ou `-` no nome e ver o servidor aceitar.

---

## Três pedidos: o zeny infinito, o relógio do mundo e o Evento de Refino (2026-08-17)

Três pedidos numa mensagem só, e nenhum deles onde parecia estar. Os três são
**servidor** — `npc/`, `db/` e nada de cliente —, então vão inteiros pelo
`implanta.sh` (`RECEITAS.md` §0).

### 1. "Itens das lojas de Prontera devem ter valor 1 zeny"

O pedido veio com a justificativa junto: *"pra evitar criação de dinheiro
infinito"*. **E as lojas já estavam a 1 zeny** — o pedido, lido ao pé da letra,
era um não-fazer-nada que não resolveria o que ele queria resolver.

O que a medição mostrou é que **o dinheiro infinito nunca esteve na vitrine**.
Está na revenda: comprar por 1 zeny e revender em **qualquer** NPC pelo `Sell`
do `item_db`, que vale `Buy/2` quando o item não declara o campo. Varridas as
22 lojas dos três mercados, **918 dos 1603 itens davam lucro por clique**, e
três não eram os 9 zeny de sempre:

| id | item | loja | vitrine | revenda | lucro/clique |
|---|---|---|---|---|---|
| 19446 | Tapa-Olho Ferido | Ocleiro | 1 z | 1.000.000 z | **999.999** |
| 500009 | Cópia de Gram | Senhor das Armas | 1 z | 250.000 z | 249.999 |
| 2204 | Óculos_ | Ocleiro | 1 z | 2.000 z | 1.999 |

O Tapa-Olho estava no ar desde que entrou. **A regra 4.16 de 2026-08-12 não o
tinha pego porque ela só olhava para item ENTRANDO** — "todo item *a partir de
agora* que tiver valor de venda". Ele já estava dentro.

Com o número na mão, a decisão do dono foi `Buy: 1` por override — a saída que
o cabeçalho do `mercado_contemporaneo.txt` tinha **considerado e recusado** cinco
dias antes, porque ela alcança toda cópia do item no servidor, inclusive a que o
jogador caçou. Em 2026-08-17 a resposta foi a contrária, e a §4.16 do
`CLAUDE.md` foi reescrita: **a regra do "vende pelo `Buy`" está revogada**, e o
Elmo de Aegir (18728) voltou de 200.000 para 1 zeny com as outras cinco peças
que estavam fora.

**Só o `Buy` é declarado, e o `Sell` cai junto** — não por sorte, por causa de
uma atribuição: o `hasPriceValue[item->nameid] = { has_buy, has_sell }` do
`ItemDatabase::parseBodyNode` é sobrescrito por quem falar por último, então o
nosso arquivo apaga o `Sell` explícito que o `db/re/` tenha declarado, e o
`value_sell = value_buy / 2` do fim do carregamento dá **0**.

**A Tranqueiras ficou de fora, e foi a segunda coisa que a medição mudou.** Ela
tinha sido incluída no escopo e a medição a tirou: é a única das 22 lojas com
lucro por clique **zero**, justamente porque vende a `-1` (o `Buy` do item) — a
saída que ela mesma estreou em 2026-08-12. `Buy: 1` nela não fecharia buraco
nenhum e abriria outro: o **Ouro (969) cairia de 150.000 para 1 zeny**, e com
ele as dez receitas de Runa e os 29 ingredientes da alquimia. Levado ao dono
com os números, ele a tirou do escopo.

A trava é `ferramentas/zera_revenda_das_lojas.py`, que gera
`db/guerra/item_db_lojas.yml` a partir das próprias linhas de `shop` — e cujo
`--conferir` mede o lucro loja a loja. **Não é o cabeçalho que garante isso**
(§4.11: comentário não é trava). O acoplamento está no `ARQUITETURA.md` §4.

De quebra, **os avisos de `discounted buying price` sumiram da subida**. Eram
um por item nas cartas e treze nos visuais; o teste é
`value*0.75 < value_sell*1.24`, e com a revenda em 0 o lado direito zera.

### 2. Amanhece às 06:00, anoitece às 18:00

Doze horas de cada. **O horário andou duas vezes no mesmo dia**: pedido como
06/18, alongado para 08/20 pelo dono antes de qualquer linha ser escrita, e
devolvido para 06/18 depois de o ciclo já estar no ar. Quem mexer nele de novo
troca **quatro lugares** — os dois rótulos `OnClock`, os dois números do
`OnInit` — mais o parágrafo do cabeçalho: não há configuração única a mudar.

**Não dá para fazer por configuração.** O `day_duration`/`night_duration` do
rAthena é ciclo por **duração em milissegundos**, contado a partir do boot:
servidor reiniciado às 14:37 amanheceria às 14:37 mais a sobra do ciclo, num
horário diferente a cada reinício. Os dois já estavam em 0, e ficaram — com
eles em 0 o `pc_init` não registra temporizador nenhum, e o NPC vira a única
fonte do estado. Ligar as duas coisas junto faria dois relógios brigarem, com
o sintoma "amanheceu na hora errada" e nada no log.

`npc/guerra/ciclo_do_dia.txt`, NPC flutuante com `OnClock0600`/`OnClock1800` e
um `OnInit` que acerta o estado na subida (`night_at_start: no` faz todo boot
começar de dia). Os comandos `day`/`night` de script chamam
`map_day_timer`/`map_night_timer` com `data = 1`, que é o caminho de GM — e
esse caminho **não** passa pelo `if (data == 0 && duration <= 0) return`, ou
seja funcionam justamente com as durações zeradas.

Duas coisas que caíram de graça: o anúncio sai pelas mensagens **59/60** do
`map_msg` (o par de GM), que em português já eram *"Está anoitecendo."* e
*"Está amanhecendo."* — melhores para um ciclo agendado que as 502/503 do
ciclo automático; e escurece só os **277 mapas** com o mapflag `nightenabled`,
cidade e campo aberto, Prontera inclusa.

**Depende do relógio da máquina**, como o `horario_da_guerra.txt` — a de
produção roda em `America/Sao_Paulo` desde 2026-08-16.

### 3. O Evento de Refino

O pedido veio com duas capturas do browiki
(`arquivo.browiki.org/wiki/Refinamento#Evento_de_Refino`, servidor Valhalla),
cada uma com as tabelas "fora do Evento" e "dentro do Evento".

**A primeira descoberta é que o `db/re/refine.yml` do rAthena JÁ É a tabela
"fora do Evento"** — conferido coluna a coluna, e bate em `Arma nv. 1` a
`nv. 4`, `Armadura` e `E. Sombrio`, com um ponto percentual de diferença só no
+10 (o rAthena é 9%/19% onde o browiki arredonda para 10%/20%). Isso resolveu o
mapeamento sozinho:

| coluna do browiki | rAthena |
|---|---|
| Arma nv. 1 a 4 | `Weapon` níveis 1 a 4 |
| Armadura | `Armor` nível 1 |
| E. Sombrio | `Shadow_Armor` e `Shadow_Weapon` |
| Minérios Comuns | `Type: Normal` |
| Minérios Especiais até +10 | `Type: Enriched` (o Refinado) |
| Minérios Especiais acima de +10 | `Type: HD` |

A última linha é a única que exigiu decisão: acima do +10 **não existe minério
Refinado**, então a coluna "especiais" só pode ser o HD — e o próprio rAthena já
o trata assim no tier Etel (`Armor` nível 2 e `Weapon` nível 5), onde o HD tem
taxa melhor que o comum. **O HD até o +10 ficou de fora de propósito:** dar a
ele a coluna dos especiais o deixaria idêntico ao Refinado em taxa e melhor em
penalidade (HD não quebra, só cai um nível), o que apagaria o Refinado do jogo.

`db/guerra/refine_evento.yml`, gerado, **176 taxas subiram** em 9 combinações
grupo/nível. O gerador aborta se alguma taxa do evento for **menor** que a de
hoje — nenhuma era. Só a taxa é tocada: preço, minério, chance de quebrar e
níveis perdidos vêm mesclados campo a campo do arquivo original
(`RefineDatabase::parseBodyNode`).

**Ligar e desligar custa um reinício**, e é uma linha: o
`- Path: db/guerra/refine_evento.yml` no rodapé de `db/refine.yml`. Não há
`@reloadrefinedb` — o `refine_db` só é lido no boot.

Duas ressalvas registradas: o **teto de refino do servidor é +16**
(`refino_teto` em `conf/guerra/battle_guerra.txt`), então as linhas de +17 a
+20 estão escritas por inteireza da tabela e hoje não são alcançáveis; e o
tier **Etel** (`Armor` 2, `Weapon` 5), que o browiki não tem coluna para,
recebeu as colunas `Armadura` e `Arma nv. 4` — 1.066 itens do `item_db` estão
nele.

### O deploy, na madrugada do mesmo dia (2026-08-17, 02:05)

Os três subiram juntos pelo `implanta.sh`, do Mac, de `be300c0` para `7692aba`.
Nenhum tocava `src/` nem `site/`, então **o build de 67 minutos foi
dispensado** e o deploy inteiro custou segundos. Não houve patch de cliente a
publicar: os três são servidor puro (`RECEITAS.md` §0).

Havia **um jogador conectado** — o mesmo IP da véspera —, e o dono mandou tocar
assim mesmo. Os quatro serviços reiniciaram, o que é o que o Evento de Refino
exigia de qualquer jeito (não há `@reloadrefinedb`), e de carona valeu pelos
`@reloaditemdb`/`@reloadscript` dos outros dois.

O fuso, que na véspera foi a surpresa, **estava certo**: `date` na produção
respondeu `Mon Aug 17 01:58 -03` antes de qualquer coisa. Foi a primeira
conferência da sessão, e é para continuar sendo.

| conferência | resultado |
|---|---|
| pré-voo local e no servidor | ✅ 1139 caminhos, os dois lados aprovados |
| `Unknown syntax` no map-server | ✅ nenhum |
| erro de script no `OnInit` | ✅ nenhum, com 3.252 NPCs executados |
| `db/guerra/item_db_lojas.yml` | ✅ 1.603 entradas lidas |
| `db/guerra/refine_evento.yml` | ✅ 9 entradas lidas |
| `[Error]` no carregamento | 4, os mesmos de sempre — gênero de chicote e instrumento, inerentes ao parser |
| os quatro serviços + site + apache + mariadb | ✅ `active` |

**O aviso `discounted buying price` sumiu, e isso é medição e não impressão:**
eram um por carta e treze nos visuais, e a subida trouxe **zero**. É a
confirmação, do lado do servidor, de que a revenda foi mesmo a 0 — o teste do
`npc_parse_shop` é `value*0.75 < value_sell*1.24`, e com o `Sell` zerado o lado
direito zera junto. Não substitui a sonda de tela (vender o Tapa-Olho Ferido e
ver 0 zeny), mas prova que o `Buy: 1` chegou aos 1.603 itens.

**O que continua de tela** — o ciclo do dia às 08:00 e 20:00, a janela de
refino com as chances novas e a venda a 0 zeny — está na `PENDENCIAS.md` §1a2,
que passou de "nenhum subiu" para "os três no ar, faltam as sondas".

### O Atualizador 3 no ar, e o deploy que não entregava nada (2026-08-17, 11:47)

O commit `a017b5d` — o conserto do registro de patches indexado só por número —
subiu para o servidor pelo `implanta.sh`, do Mac. **E o deploy não entregou
nada**, o que era o esperado e vale registrar: o commit toca só `patcher/` e
`ferramentas/publica_patch.sh`, nenhum dos quais o servidor executa. Sem `src/`,
sem `rathena/`, sem `site/` — build dispensado, os quatro no ar, ninguém
derrubado.

É a `RECEITAS.md` §0 no gume mais fino que ela já teve. Não é o caso comum de
"mexi no cliente e esqueci o patch": aqui o `git commit` estava feito, o deploy
rodou, relatou sucesso legítimo em toda linha — e o conserto continuava a zero
jogadores. O que denuncia é uma sonda de uma linha, e ela discorda do deploy:

```
$ curl -s https://libraro.filiponegrao.com.br/patch/patcher.txt
versao=2
```

com o `patcher/main.go` já em `const VERSAO = 3`. **O canal é a única sonda que
responde por quem executa o quê** — o commit do servidor não sabe nada sobre
isso.

Publicado então pelo passo 2 da §11b, **e daqui**: o próprio commit de hoje é o
que tornou isso seguro, com o `GOOS=windows GOARCH=amd64` explícito no
`publica_patch.sh` e a conferência do `MZ` atrás. Antes dele o mesmo comando
rodado do Mac teria subido um Mach-O chamado `Jogar.exe`.

| conferência | resultado |
|---|---|
| pré-voo local e no servidor | ✅ 1139 caminhos, os dois lados aprovados |
| build / reinício | dispensados — `src/` e `rathena/` intactos |
| os sete serviços | ✅ `active` |
| relógio da produção | ✅ `-03` |
| `go vet` (windows/amd64) | ✅ limpo |
| `patch_test.go` | ✅ compila para windows/amd64 |
| sha256 local / canal / baixado | ✅ os três `0106ae7f90e1…` |
| formato | ✅ `PE32+ executable (GUI) x86-64`, começa com `MZ` |

**O `go test` não roda no Mac, e não é defeito:** o pacote é `syscall` do
Windows de ponta a ponta (`NewLazyDLL`, `SyscallN`, `UTF16PtrFromString`), e o
`go test` compila para o GOOS do hospedeiro. Quem responde daqui é
`GOOS=windows go vet` e `go test -c`, que provam que compila — não que passa.
Rodar os três testes exige Windows.

**Faltava o CDN** nesta hora, que é Windows (`spaces.env` e `rclone.exe` moram
em `C:\`). Quem já instalou recebia a 3 sozinho na próxima abertura — e era
justamente quem estava com os patches 0002 e 0003 calados; quem baixasse do site
pegaria a 2 e se auto-atualizaria na primeira abertura. **O bucket foi acertado no
mesmo dia**, do Windows: origem do Spaces, CDN e `patcher.txt` os três em
`0106ae7f90e1…`.

## O "Unknown Item" que não era do servidor: dois patches calados por um número (2026-08-17)

O relato chegou como defeito de item: **"diversos itens dos requisitados
recentemente (52) tiveram itens não identificados, sprite de maçã, unknown
item"**, com dois screenshots do Acessorista e do Capeiro. O que se via era
"Unknown Item" com o desenho de uma maçã e `Item ID: 0`, no meio de itens que
apareciam com o nome certo.

Terminou três camadas abaixo, num arquivo de seis linhas na máquina do
jogador — e o caminho até lá passou por **dois diagnósticos errados meus**,
que ficam registrados porque cada um é uma lição desta casa em ação.

### O que os "Unknown" eram, e a primeira medição que fechou

O nome de item **não trafega na rede** (§4.9): o servidor manda o ID, e quem
desenha o nome é o `itemInfo.lua` do cliente. Então "Unknown Item" é sempre
cliente, nunca servidor — e a pergunta certa não é *por que aquele item*, é
*quais* itens.

Eram **exatamente as 11 entradas escritas no `itemInfo.lua` em 16/08 às
22:50**. A prova saiu de graça porque a ferramenta deixa cópia ao lado do
arquivo: comparar `itemInfo.lua` com `itemInfo.lua.BACKUP-20260816-2250` dá a
lista fechada, e ela bate item a item com o que a tela mostrava.

| loja | as que apareciam como *Unknown* |
|---|---|
| Capeiro | Manto Abstrato (20986), Manto Maligno (480085), Relíquia Divina (480319), Som do Luar (480446), Asas de Garuda (480278) |
| Acessorista | Anel da Colheita (490272), Núcleo de Verus (490336), Luvas de Somatologia (490497) |
| Senhor das Armas | Lacma (28739) |
| Lorde das Armaduras | Quatrenhum (450226) |
| Escudeiro | Símbolo do Éden (460050) |

**O sintoma é seletivo, e é isso que engana:** os itens antigos da mesma
vitrine desenham o nome certo, só os novos caem no *fallback*. Uma vitrine de
23 linhas onde 5 falham não parece "cliente desatualizado" — parece cinco
itens quebrados.

### O primeiro engano: o cliente de dev, que era mesmo cliente velho

Na máquina de desenvolvimento havia **dois clientes vivos**, um aberto às
22:23 e outro às 01:06, e o `itemInfo.lua` fora gravado às 22:50, entre os
dois. O cliente só lê aquele arquivo na inicialização (§3), então o de 22:23
tinha a tabela velha em memória. Diagnóstico correto **para aquela tela**, e a
correção era fechar e reabrir.

Ainda no mesmo exame apareceu um segundo defeito, esse do servidor e de outra
natureza: **duas peças não estavam na vitrine, nem como "Unknown"**. Ampliando
a lista em *nearest-neighbor* — a lição de 2026-08-11 sobre não comparar tela a
olho —, entre "Luvas de Proteção" e "Palheta de Elunium" havia **uma** linha
onde deviam existir duas. O log explicou:

```
(08/17/2026 01:10:10) [Warning] npc_parse_shop: Invalid sell item ... (id '490497').
(08/17/2026 01:10:10) [Warning] npc_parse_shop: Invalid sell item ... (id '28739').
```

Foi `@reloadscript` **sem** `@reloaditemdb`: os dois placeholders novos ainda
não existiam em memória, e o `npc_parse_shop` descarta da loja todo item que
não está no `item_db` — com uma linha de aviso que fica soterrada. Virou regra
no `CLAUDE.md` §5. Num boot completo isso não acontece, porque o `item_db`
carrega antes dos NPCs; é falha exclusiva do recarregamento parcial.

### O segundo engano, e o que o desfez

Fechado o caso da máquina de dev, veio a frase que mudou tudo: **"mas isso
também aconteceu em PRD, então esse restart também faltou em prd. Esse é meu
ponto."**

A resposta que dei foi metade certa e serve de aviso: conferi a produção —
`git` em dia, os quatro serviços reiniciados às 02:11:34, patch 0003 publicado
com o sha256 batendo — e concluí que, como "Unknown Item" é cliente, o jogador
devia ter aberto o jogo por fora do Atualizador. **Descartei a única hipótese
que sobrava sem medir a única coisa que faltava medir: o cliente instalado.**

O que desfez foi o dono mandar o caminho do print: `C:\Program Files
(x86)\GuerraDoEmperium\ScreenShot\`. Aquele é o cliente que o instalador
montou e o Atualizador mantém — e ele mostrava o mesmo defeito.

### A causa raiz: duas contagens que começam em 0001

O `patch\aplicados.txt` daquele cliente estava assim:

```
0002  ddbebeaa…  As musicas
0003  2d7c9102…  A Guerra do Emperium (1 de 2)
0004  1d57df90…  A Guerra do Emperium (2 de 2)
0005  6a02f3c9…  O motor do jogo
0001  921fabb6…  IA do homunculo e do mercenario
```

As quatro primeiras linhas **são os pedaços da base** — nome, número e sha256
idênticos aos do `patcher/base.txt`. O instalador estava anotando o primeiro
download no diário dos **patches**, e as duas contagens começam em 0001. O
Atualizador comparava só o número: viu 0002 e 0003, deu por aplicados, e
mostrou *"Cliente atualizado"* com a barra cheia.

Ou seja: **os patches 0002 (censura) e 0003 (itens novos das lojas de
Prontera) nunca chegaram a ninguém**, e os números 0004 e 0005 estavam
queimados para os dois patches seguintes.

A conferência independente, no disco daquele cliente, fechou sem margem: o
`itemInfo.lua` instalado tinha **23.829.419 bytes — byte a byte a versão de
antes das 11 entradas**, o `data\manner.txt` do patch 0002 não existia, e
nenhum arquivo de arte do 0003 estava lá.

**Por que passou tanto tempo parecendo saudável:** o pedaço 0001 da base é o
`data.grf`, do tipo `bruto`, que sai por outro ramo do `aplicaPedaco` e **não**
anota. Isso deixou o número 0001 livre, o patch 0001 foi aplicado de verdade, e
o conjunto se comportou como um sistema que funciona.

**E o comentário do `Instala` já dizia que isso não podia acontecer:**

> *Ela NÃO grava `aplicados.txt` para os pedaços da base: aquele arquivo é o
> registro dos PATCHES, e misturar os dois faria o Atualizador achar que já
> aplicou patches que nunca viu.*

Era verdade sobre o `Instala` e falsa sobre o programa — o `aplicaPedaco`
reusava o `aplica`, e o `marcaAplicado` morava lá dentro. É a §4.17 no
Atualizador: **o cabeçalho descrevia uma trava que o código não tinha.**

### O conserto, e por que ele repara sozinho

1. **`aplica` não anota mais.** Quem anota é o laço de patches, o único dos
   dois chamadores que tem o que registrar. O instalador não encosta no
   diário — agora de fato, e não só no comentário.
2. **O registro passa a ser conferido por número E sha256.** Esta metade é a
   que **conserta quem já instalou**: o `0002` gravado tem o sha da base, não
   bate com o do patch, e o patch é reaplicado na abertura seguinte. Nenhum
   jogador precisou reinstalar nem apagar arquivo — que era a saída de suporte
   prevista no `ARQUITETURA.md`, e que não foi preciso usar.

Três testes offline em `patcher/patch_test.go`, um deles com o conteúdo
**literal** do registro quebrado. `VERSAO` subiu para 3.

**O reparo foi medido no disco**, às 11:54 de 2026-08-17: o `itemInfo.lua` do
cliente instalado passou a 23.848.327 bytes com as 11 entradas, o `manner.txt`
apareceu, e o `aplicados.txt` ganhou duas linhas novas — `0002` e `0003` com os
shas dos patches de verdade, por cima das linhas da base, que ficam ali como
história inofensiva.

### O terceiro defeito, achado ao rever o caminho da publicação

O `publica_patch.sh --atualizador` chamava `go build` **sem fixar
`GOOS`/`GOARCH`**. Rodado do Mac — que é de onde sai o deploy —, produziria um
binário **Mach-O chamado `Jogar.exe`**, com sha256 correto, subindo para o
canal de auto-atualização de todos os jogadores e não abrindo em máquina
nenhuma. O `-o` só decide o nome do arquivo. Agora é explícito
(`GOOS=windows GOARCH=amd64`), com uma conferência de assinatura `MZ` atrás,
que pega qualquer outro jeito de o build sair errado.

### O que este caso ensina

- **"Unknown Item" é sempre cliente.** O nome do item não trafega na rede, e
  nenhum reinício de servidor muda uma letra do que a janela de loja escreve. O
  que a falta de restart produz é o sintoma **oposto**: o item some da lista.
- **A pergunta que resolveu foi *quais* itens.** A lista dos que falhavam bateu
  com uma lista que existia em outro lugar — as 11 entradas novas do
  `itemInfo.lua` —, e foi essa coincidência, e não o exame de nenhum item, que
  apontou a causa. Vale para toda falha seletiva.
- **Duas medições certas não fecham uma terceira.** Patch publicado com sha
  correto e servidor no ar são fatos, e eu tratei os dois como se
  respondessem "o jogador recebeu". Quem respondia era o disco do jogador — e
  ele estava a um `ls` de distância o tempo todo. Mesma família do
  `ajusta_tamanho_fonte.py`: verificação que passa não é prova de efeito.
- **O dono insistiu, e estava certo.** O primeiro diagnóstico explicava a tela
  que ele mandou e não explicava a produção; ele apontou isso, e a resposta foi
  mais uma explicação plausível em vez de mais uma medição. O que abriu o caso
  foi um caminho de arquivo.

## O brilho da carta e os três acessórios de lado trocado (2026-08-17)

Quatro pedidos na mesma rodada. O primeiro — devolver o ciclo do dia para
06/18 — está registrado na seção "Três pedidos", §2, que foi corrigida no
lugar. Os outros três estão aqui; o quarto (visual de GM) ficou em aberto e
está no `PENDENCIAS.md`.

### 1. O brilho (e o som) quando cai uma carta

> *"No bRO quando uma carta era dropada ela fazia um barulho e um sprite de
> brilho era carregado junto."*

O pedido veio com o caminho da arte dentro do GRF, e a primeira coisa que a
varredura mostrou é que **não há nada a trazer**: os cinco pilares já estão no
nosso `data.grf` de 2021-11-03, cada um com o `.wav` ao lado —
`data	exture\effect
ew_dropitem\dropitem_purple\...\dropitem_purple.str` e
`data\wav\effect\drop_purple.wav`, mais os irmãos azul, verde, rosa e vermelho.
Ou seja: **nada disto precisa de patch de cliente** (§4.18), e vale para quem
já instalou o jogo.

Quem liga o efeito é um campo do pacote de queda de item, o
`ZC_ITEM_FALL_ENTRY5` (0x0ADD): `showdropeffect` e `dropeffectmode`
(`clif.cpp:890`). O servidor manda o número, o cliente acha o efeito **e o wav**
sozinho.

**O rAthena já sabe fazer isso por item** — `Flags: DropEffect:` no `item_db`
(`itemdb.cpp:729`). Esse caminho existe e funciona, e mesmo assim o trabalho
foi para `src/custom/brilho_da_carta.hpp`, por dois motivos:

1. São **mais de cinco mil cartas**. O override teria uma entrada para cada, e
   seria o maior arquivo de `db/guerra` por uma ordem de grandeza.
2. Ele nasceria desatualizado. Carta que entre depois — do upstream, de um
   evento, de um item nosso — ficaria sem brilho, **calada**, até alguém
   lembrar de rodar o gerador de novo. A regra é "toda carta", e "toda carta"
   se escreve uma vez.

A regra escrita é o **tipo** do item (`IT_CARD`), então carta nova já nasce
brilhando. A cor é `brilho_da_carta` no `conf/guerra/battle_guerra.txt` (4 =
roxo, o do bRO; 0 desliga), pelo mesmo motivo do `refino_teto`: trocar com
`@reloadbattleconf` em vez de recompilar. **O número é o do `DropEffect` do
`item_db`, não o do pacote** — o pacote leva ele menos um —, e a escala **muda
com o PACKETVER**: o branco saiu e o laranja virou verde em 2020-03-04
(`itemdb.hpp:3262`). Por isso o teto no `battle_config_init.inc` é o literal
`6` e não uma constante do `enum`: aquele arquivo é incluído em `battle.cpp`,
que não inclui o `itemdb.hpp`.

**O que não alcança**, e é do rAthena: só queda de **monstro**. O
`canShowEffect` do `map_addflooritem` nasce `false` (`map.hpp:1178`) e o mob
passa `!loot` (`mob.cpp:2540`) — item que o monstro pegou do chão e devolveu na
morte não brilha, nem item largado por jogador. É o que se quer.

#### A primeira versão não funcionava, e a causa era uma linha de guarda

Compilou, subiu sem aviso nenhum, e **nenhuma carta brilhou**. O código estava
escrito assim:

```cpp
// O item mandou: nao ha o que decidir.
if (efeito_do_item != DROPEFFECT_NONE)
    return efeito_do_item;
```

A intenção era boa — item com cor própria no `item_db` continua mandando. O
erro é que **`DROPEFFECT_CLIENT` (o valor 1) não é uma cor**: quer dizer
literalmente *"decide você, cliente"*, e o cliente de 2021-11-03 decide não
desenhar nada. E o `db/re/` do nosso vendor traz `DropEffect: CLIENT` em
**1882 itens**, com quase toda carta entre eles. Ou seja: a guarda desligava a
regra inteira, em silêncio, justamente para os itens que o pedido nomeava.

A guarda certa é `> DROPEFFECT_CLIENT`, não `!= DROPEFFECT_NONE`.

#### O que custou caro foi CHEGAR na linha, não consertá-la

Três hipóteses plausíveis vieram antes, e todas foram descartadas por medição:

1. **`@autoloot`** — com ele ligado a carta nunca vira item de chão
   (`mob.cpp:2600` faz `return` antes do `push_back`), logo não há pacote de
   queda. Estava desligado.
2. **O valor da configuração não chegou** — descartado: a sonda imprimiu
   `config=4`.
3. **A checagem de `IT_CARD`** — descartada: a sonda imprimiu `type=6`, que é
   `IT_CARD`.

O que separou os quatro suspeitos foi **pintar cada caminho de uma cor**: Gosma
azul e Carta de Poring vermelha pelo caminho do `item_db` do rAthena, e o nosso
caminho em roxo. Aí a observação do dono — *"o brilho aparece na posição em que
o monstro morreu, e não na da carta"* — deixou de ser um mistério e virou um
fato: o pilar era o da **Gosma**, que cai na célula da morte (`DIR_CENTER`,
`mob.cpp:2530`), e a carta, que cai numa célula vizinha, nunca teve pilar
nenhum. Uma única cor teria escondido isso.

E o que fechou o caso foi uma sonda `ShowInfo` **antes de qualquer `return`**,
lida direto do buffer de tela do map-server — porque o `log/map-msg_log.log`
veio vazio duas vezes, e não por falta de sonda: `console_msg_log: 3` grava só
Warning e Error, e **informação não tem bit nessa escala**. Ler o arquivo e
concluir "a função não foi chamada" era o diagnóstico invertido que quase
custou uma quarta hipótese. As duas armadilhas estão no `CLAUDE.md` §5.

### 2. Os três acessórios de lado trocado — e a inversão que não existia

> *"Acessórios estão trocados. O que é direito aparece no esquerdo, e o que é
> esquerdo aparece no direito."*

A leitura natural é "o cliente inverte os dois lados", e ela é **errada**. O
print que veio junto já trazia a resposta, e ela é do lado do servidor.

Na janela de equipamentos as duas caixas dizem `Acc. Right` (à **nossa**
esquerda) e `Acc. Left` (à nossa direita) — e isso está certo: o personagem
está de frente, então a direita dele é a nossa esquerda. O Amuleto Mitológico
(490337) tem na descrição `Tipo: Aces. Direito` e entrava na caixa `Acc. Left`.

**Quem discordava era o `Locations:` do nosso vendor.** A medição fechou o
assunto numa rodada: dos **79** acessórios que cravam um lado só *e* que têm
lado declarado na descrição do bRO, **76 concordam e três divergem** — e
nenhum diz "os dois" onde o bRO crava um lado. Não havia inversão geral a
corrigir; havia três itens errados.

| ID | item | nosso vendor | bRO |
|---|---|---|---|
| 490290 | Anel de Ameretat | Direito | **Esquerdo** |
| 490336 | Núcleo de Verus | Esquerdo | **Direito** |
| 490337 | Amuleto Mitológico | Esquerdo | **Direito** |

Quem vence é o bRO, pela §4.14 e pelo mesmo raciocínio da Piscadela de Freya: a
descrição que o jogador lê vem do `itemInfo.lua`, ou seja do bRO — deixar o
servidor discordando dela faz a tela mentir, e o servidor é o lado barato de
trocar. Três overrides em `db/guerra/item_db.yml`, com o `false` explícito no
lado velho (`Locations` é OR, não atribuição).

Uma armadilha de nome, e ela quase custou o item do meio: o `_L_` de
`Dimension_L_Stone` **não é "left"**. A família `Dimension_*` usa a letra para
a classe (`_B_Greave`, `_H_Boots`, `_S_Shoes`, `_M_Shoes`), e não existe
nenhum `Dimension_R_Stone` — é o único `Dimension_*_Stone` do `item_db`
inteiro.

**Depois do `@reloaditemdb`, relogar antes de testar** — e essa parte custou
uma rodada, porque a instrução que dei estava pela metade. Eu avisei do item
já **equipado**, que não se move: o lado fica gravado na coluna `equip` do
inventário, e o `itemdb_reload` chama `pc_check_available_item`, não
`pc_checkitem` (`itemdb.cpp:4992`).

Faltou o outro lado, e é o que o dono viu: **o item na mochila também não
equipa**, e a mensagem culpa o item — *"You can't put this item on."*, uma por
clique. O cliente guarda o `location` de cada item de quando a lista de
inventário lhe foi enviada (`clif_inventorylist` manda `pc_equippoint`,
`clif.cpp:3092`) e **manda essa posição de volta** ao equipar
(`clif_parse_EquipItem` repassa o `p->position` cru). O `pc_equipitem` testa
`!(pos & req_pos)` (`pc.cpp:12064`): servidor dizendo `Acc. Direito`, cliente
ainda pedindo `Acc. Esquerdo`, a conta dá zero, recusa.

Quem conserta os dois é o reenvio da lista de inventário, que só acontece no
login ou na troca de mapa (`clif_parse_LoadEndAck`, `clif.cpp:10795`). Aí o
`pc_checkitem` desequipa o antigo sozinho (`pc.cpp:12623`) e reequipar põe na
caixa certa.

**Na produção isso não aparece**: o deploy reinicia o map-server e todo mundo
reconecta. É um sintoma exclusivo do recarregamento parcial em DEV — o mesmo
padrão do `@reloadscript` sem `@reloaditemdb`, que faz o mesmo servidor se
comportar de dois jeitos. Está no `CLAUDE.md` §5.

De quebra, a mesma varredura anotou uma divergência que **não** foi mexida por
estar fora do pedido: o bRO dá `DEF: 12` ao Núcleo de Verus e o nosso vendor
não lhe dá `Defense` nenhum.

### 3. O visual de GM na produção — uma conta que não existia lá

O cliente só dá o tratamento de GM para os `account_id` listados no
`<aid><admin>` dos dois `clientinfo` (`data\clientinfo.xml` e
`data\sclientinfo.xml` — os dois, pela §5), e lá estava **só o 2000000**, a
conta de DEV desta máquina. É por isso que funcionava no HML e não na
produção: o `group_id 99` do banco dá os **comandos**, o `<aid>` dá o
**visual**, e as duas metades são independentes — nenhuma delas reclama da
outra.

O número veio do dono (2000004) e foi conferido no banco da produção antes de
empacotar, porque **número de patch nunca se reaproveita** e publicar o id
errado gastaria um. A consulta fechou melhor do que o esperado: a única conta
com `group_id 99` é a 2000004 (`librasupremo`), e **o 2000000 nem existe na
produção** — a numeração de lá começa em 2000001. Por isso o arquivo publicado
leva **só** o 2000004: manter o 2000000 seria dar o visual de GM a quem viesse
a ter aquele número, e ele não serve para nada lá.

Virou o **patch 0004**, de 850 bytes — e a montagem dele tem um degrau que vale
registrar: o `monta_patch.py` empacota os arquivos **como eles estão** em
`C:\GuerraDoEmperium\cliente`, e este cliente aponta para `127.0.0.1` desde
2026-08-16. Então a montagem foi um sanduíche — trocar os dois xml pela versão
de produção, montar, devolver o dev —, com o `confere_apontamento` do próprio
`monta_patch.py` como rede de segurança no meio e uma conferência no fim de que
o cliente voltou ao `127.0.0.1`. Os dois `.BACKUP-138.197.155.31` que ficam ao
lado passaram a guardar a versão de produção **de verdade** (endereço + conta
de GM), que é o que se restaura ao voltar para lá.

**Publicado no mesmo dia.** A conferência não parou no "enviei": o zip foi
baixado de volta da CDN e conferido — 850 bytes, sha256 batendo com o
`patcher/patches.txt`, e os dois xml com o endereço de produção e o
`<admin>2000004</admin>` dentro. Falta a tela do outro lado (`PENDENCIAS.md`
§1w).

## A separação de cartas passa ao modelo novo, e o Jeremy sai de cena (2026-08-18)

O pedido veio curto e com uma imagem: *"Remoção de cartas no Richard: hoje temos
uma remoção antiga que só remove escudo e espada. Precisamos seguir o modelo
novo da imagem passada como referência"* — a página **Separação** do bRO, com
dez regras numeradas e uma tabela de quatro pagamentos.

### O que havia, e por que "só escudo e espada"

O `npc/re/merchants/card_separation.txt` do rAthena é **um script só com dois
`duplicate`**, e cada um atende metade dos slots:

| NPC | onde | slots |
|---|---|---|
| `Richard#pa0829` | malangdo 208,166 | mão direita e esquerda (arma e escudo) |
| `Jeremy#pa0829` | malangdo 215,166 | armadura, sapato, capa, chapéu de topo |

Os dois seguem o modelo **velho**: a falha destrói o item, a carta, ou os dois,
e o jogador escolhe antes qual dos dois quer que sobreviva. A frase do pedido
descrevia exatamente metade daquilo.

### O modelo novo, em uma linha

**Na falha não se perde nada.** Nem a peça, nem a carta, nem o refino, nem o
encantamento — perde-se só o que foi pago. O que o pagamento compra é a
**chance**:

| pagamento | custa | chance |
|---|---|---|
| nenhum | 1.000.000 de zeny | 2% |
| Lubrificante Básico (25238) | 4 Frutas dos Gatos | 10% |
| Lubrificante Refinado (25239) | 7 Frutas dos Gatos | 20% |
| Óleo Removedor Especial (6443) | 192 Frutas dos Gatos | 100% |

Mais o resto das dez regras: uma carta por vez, escolhida por cova; peça
vestida; carta de MVP **só** com o Óleo, e o Óleo **só** para carta de MVP
(selada conta como comum); Essência de Morroc não é carta e não sai; e no
**sucesso** os bônus aleatórios da peça se perdem.

Tudo isso é um NPC novo, `npc/guerra/separacao_de_cartas.txt`, com o Richard nas
mesmas coordenadas e **os dois do rAthena desligados no `OnInit`**. O Jeremy foi
desligado por decisão do dono, perguntada na entrega: o Richard novo cobre os
dez slots sozinho, e deixar o velho de pé ao lado manteria um serviço que
destrói equipamento, sem nada na tela dizendo qual dos dois é o seguro.

### O cliente já sabia de tudo — inclusive onde o Richard mora

A conferência que economizou o dia: os cinco itens envolvidos já estão inteiros
neste cliente. Nome em português e **arte 4 de 4** em 25238, 25239, 6443, 6440 e
6441, e a descrição dos três novos já traz os números do modelo novo — *"Aumenta
para 10% as chances de sucesso"*, *"Garante 100% de chance de remover uma carta
de MVP"*, *"Não funciona em Cartas Seladas de MVP"*. **Nenhum patch de cliente
foi preciso** (`CLAUDE.md` §4.18).

E foi essa leitura que decidiu a coordenada. A imagem diz **malangdo 220,160**;
o `itemInfo.lua` deste cliente diz **208,166**, nos três lubrificantes, no campo
`<NAVI>` — que é o link de navegação que o jogador clica na própria descrição do
item. Duas fontes do bRO discordando. Ficou 208,166, que é também onde o rAthena
já punha o Richard: as três pontas concordam e não custa patch. Mudar para
220,160 seria reescrever a descrição dos três itens **e** publicar patch, senão
o link levaria a um lugar vazio — e isso é decisão do dono, não da entrega.

### A moeda não existia

A parte que o pedido não podia prever: a **Fruta dos Gatos (6417)**, moeda dos
lubrificantes no bRO, **não tinha fonte nenhuma neste servidor**. Nenhum mob a
dropa, nenhuma loja nossa a vendia, e o próprio Coin Exchanger de Malangdo
recusa trocar por ela (*"Cannot exchange for Silvervine"*,
`coin_exchange.txt:75`). Só sumidouros. O sistema inteiro nasceria travado no
único caminho que não pede fruta — 1.000.000 de zeny com 2% de chance.

Levantado na entrega, a decisão do dono foi **barter da Máquina de Prontera,
pago em Moeda Nova**. Virou o `Index: 22` de `Maquina#loja` em
`npc/guerra/barters_guerra.yml`, a **1 Moeda Nova por fruta** — preço unitário
escolhido para que a tabela do bRO passasse a valer em Moeda Nova sem conta
nenhuma: 4, 7 e 192. Esse `Amount` é o único botão da economia inteira; mexer
nele mexe nos três pagamentos de uma vez.

Para comparar: o Passe Antigravitacional e a Rédea Eterna custam 100 Moedas
cada, então o Óleo (192) passa a ser a coisa mais cara que a Máquina vende — o
que combina com ele ser a única forma de tirar carta de MVP sem risco. A Fruta é
`NoDrop/NoTrade/NoSell/NoCart` no `item_db` do vendor, então ela não vaza para
mula nem volta em zeny num NPC.

Este acoplamento — **serviço que cobra em item exige a fonte da moeda** — virou
uma seção do `ARQUITETURA.md` §4.

### A Máquina Especial teve de ser reescrita inteira, e não acrescida

A regra 10 da imagem manda trocar os lubrificantes velhos na Máquina Especial
(malangdo 218,165), que é a `Special Vending Machine` do rAthena. Ela **não
vende só lubrificante**: vende também as três Proteções do Deus do Mar e as três
Caixas de Arpões de Polvo, que são a entrada das instâncias do Esgoto e da
Caverna do Polvo. Desligar a original e pôr no lugar uma máquina só de
lubrificante fecharia as duas instâncias, calado — então a nossa reproduz as
seis linhas, em português, mais os três lubrificantes novos e a troca dos dois
velhos.

A troca devolve **o que os dois custavam nela mesma**: 36 Frutas pelo
Lubrificante Comum e 56 pelo Sofisticado. Não há número oficial para isso;
devolver menos seria confisco e devolver mais abriria ganho para quem tivesse
estoque. E não é um gerador de moeda: conferido que os dois só tinham **aquela
máquina** como fonte, e ela deixou de vendê-los — a troca só drena estoque
antigo.

O nome único é `Máquina Especial#malangdo`, e o `#` não é enfeite: **já existe
uma "Máquina Especial" no projeto**, a da Sala Secreta da Ordem (`prt_in
137,108`). Nome único repetido derruba o segundo NPC na carga.

### O que o código teve de proteger

Três coisas que não estavam no pedido e teriam custado caro:

**A lista de cartas de MVP é gerada.** A do rAthena tem 45 ids escritos à mão e
está parada em 2015. A nossa tem **147**, e saiu de
`ferramentas/varre_cartas.chefes()` — a mesma função que monta a loja "Carta de
MVP" do `mercado_de_cartas.txt`, ou seja as duas listas concordam por
construção. Carta de MVP não se reconhece pelo `item_db` (não há marca lá): sai
do `mob_db`, por quem a dropa, e o rAthena marca MVP de duas formas. De quebra,
conferido que **nenhuma carta selada cai nessa lista** — é o que faz a regra 7
valer sozinha, sem uma segunda lista.

**Não existe comando que tire UMA carta de UMA cova.** O `successremovecards`
tira **todas** de uma vez, e tira a Essência de Morroc junto porque ela é `Type:
Card` — quebraria as regras 2 e 8 ao mesmo tempo. O caminho é desmontar e
remontar (`delequip` + `getitem4`), e aí aparece a armadilha que virou entrada
do `CLAUDE.md` §5: **vínculo, prazo e grau de encanto não têm `getequip*`
nenhum**. Quem os lê é o `getinventorylist`. Sem isso, separar carta de um item
vinculado o devolveria solto — item de conta virando mercadoria — e um item
alugado voltaria eterno. O primeiro é resolvido com `getitembound4`, o segundo
com uma recusa por escrito.

**O item é reconferido depois do último menu.** Entre escolher a cova e pagar há
`next` de sobra para trocar de equipamento; antes de cobrar, o NPC confere que a
peça continua vestida, que é a mesma (`getequipid`) e que as quatro covas não
mudaram (`F_IsEquipCardHack`). E peça **forjada ou assinada** é recusada: nela a
cova 0 é um marcador (254/255/256) e as covas 2 e 3 são o id do dono partido em
dois — números grandes que passam por id de item.

### O que ficou por fazer

Nada foi visto em jogo ainda — o servidor está no ar e o recarregamento é do
dono. A ordem importa: **`@reloadbarterdb` primeiro** (a Fruta na Máquina),
**`@reloadscript` depois** (os dois NPCs). O roteiro de teste está em
`PENDENCIAS.md`.

## O cliente de dev estava apontado para a produção, e quem o virou foi o Atualizador (2026-08-18)

O dono foi testar a separação de cartas no servidor local e reparou que o
cliente de `C:\GuerraDoEmperium\cliente` estava indo para a produção. Estava
mesmo — e os **quatro** arquivos concordavam nisso: os dois `clientinfo` vivos e
os dois `.BACKUP-138.197.155.31` ao lado, byte a byte idênticos, todos em
`138.197.155.31` com `<admin>2000004</admin>`.

### A suspeita óbvia estava errada

O primeiro palpite foi o **sanduíche** da `RECEITAS.md` §11: montar o patch 0004
(visual de GM) em 2026-08-17 exigiu apontar os dois xml para produção, e o passo
de volta poderia ter sido esquecido. Plausível, e falso.

O que decidiu foi o `patch\aplicados.txt` do próprio cliente de dev:

```
0004  f11c5f27…  2026-08-18 01:50  Visual de GM na producao
```

**Alguém rodou o `Jogar.exe` dentro da pasta de dev**, e o Atualizador fez
exatamente o que existe para fazer: aplicou o patch 0004, que leva os dois
`clientinfo` com o endereço de produção. O carimbo de 01:50 bate com o dos dois
xml vivos. Não foi descuido de receita — foi o caminho normal do produto,
rodando no lugar errado.

### A assimetria que ninguém tinha visto

O `monta_patch.py` e o `monta_cliente.py` protegem a **saída**: o
`confere_apontamento` recusa publicar um cliente apontado para `127.0.0.1`, e
foi essa trava que evitou publicar 3,4 GB inúteis em 2026-08-16. **Nada
protegia a entrada.** E a falha de entrada é pior de descobrir, porque não tem
sintoma: o jogo abre, loga, joga — no servidor errado. Quem estivesse "testando
local" estaria testando produção, e a única pista seria um personagem que não
existe.

Isso volta a acontecer em **todo patch futuro que leve os xml**, enquanto houver
um `Jogar.exe` naquela pasta.

### O segundo buraco: o backup era de um lado só

O nome `.BACKUP-138.197.155.31` diz o que ele guarda — a produção. Não havia
`.BACKUP-127.0.0.1`. Então, quando o lado de dev foi sobrescrito, **não havia de
onde restaurar**: o `127.0.0.1` teve de ser reconstruído à mão. A receita já
dizia "devolver o par de dev" e presumia um par de dev que nunca existiu como
arquivo.

E o `<admin>` mostrou que não bastava trocar o endereço: o `group_id 99` do
banco dá os *comandos*, mas quem dá o **visual** de GM é a lista dentro do
cliente. Local é `2000000` (`teste`, a única conta com group 99 neste banco);
produção é `2000004` (`librasupremo`), que aqui nem existe. Dois campos, dois
arquivos.

### O conserto virou uma ferramenta

`ferramentas/aponta_cliente.py`, com três modos:

```
python ferramentas/aponta_cliente.py              # só relata
python ferramentas/aponta_cliente.py --dev
python ferramentas/aponta_cliente.py --producao
```

Ele mexe no `<address>` **e** no `<admin>` dos **dois** xml, grava o lado de
onde saiu antes de trocar (agora há `.BACKUP-` dos dois lados), e avisa quando
os dois arquivos discordam entre si. O sanduíche da §11 passou a ser três
comandos sem nenhum passo à mão.

**Conferido, e a conferência é o que dá confiança nele:** a ida e a volta
devolvem os arquivos **byte a byte idênticos**, e o `--producao` reproduz
exatamente o `.BACKUP-138.197.155.31` de 2026-08-17 — ou seja o script chega ao
mesmo lugar em que a montagem manual do patch 0004 tinha chegado. Depois de
apontar para dev, o `confere_apontamento` foi chamado nos dois arquivos e
recusou os dois, que é a trava de saída rearmada.

O cliente ficou em `127.0.0.1` / `2000000`. **Para jogar no local, abrir pelo
`GuerraDoEmperium.exe`** — o `Jogar.exe` daquela pasta reaponta tudo de volta.

## O primeiro teste do Richard: a coordenada errada e a guarda que se autobloqueou (2026-08-18)

Duas correções no mesmo dia, as duas de responsabilidade da entrega anterior.

### A coordenada era 220,160, e estava no print

O pedido veio com a página do bRO em imagem, dizendo `malangdo 220, 160`. A
entrega pôs o Richard em **208,166** — onde o rAthena já o punha — com o
argumento de que é essa a coordenada que o `<NAVI>` da descrição dos três
lubrificantes aponta neste cliente, e que mudar exigiria patch. O argumento é
verdadeiro e **não era do dono**: ele tinha dito a coordenada, por escrito, no
próprio pedido. Corrigido para 220,160.

A ponta solta do `<NAVI>` continua existindo: o link da descrição do item manda
o jogador treze células ao lado. Não dá erro, e consertar é patch de cliente —
ficou registrado na `PENDENCIAS.md` §1x como decisão do dono.

**A lição, e ela é sobre a entrega e não sobre o código:** quando o pedido traz
um número explícito, ele não é um palpite a ser conferido contra outra fonte. Se
outra fonte discorda, isso se **relata**; não se troca o número por conta
própria. É a mesma família da §4.14 do `CLAUDE.md` ("divergência entre o pedido e
o `item_db` é para levantar na entrega, não para resolver sozinho"), e desta vez
foi o contrário do que aquela regra manda.

### "Minha bancada está desarrumada hoje" — a guarda pisou na própria armadilha

No primeiro clique em jogo o NPC recusou atender. A causa é de uma ironia útil:
a mensagem vem da guarda de §4.11 que confere se as três colunas da tabela de
slots têm o mesmo tamanho, e ela media `getarraysize(.@slot)`.

**`EQI_ACC_L` vale ZERO**, e é o último elemento daquela coluna. Zero em array
de `.` ou `.@` **apaga a entrada** (o `set_reg_num` tem um ramo só para isso),
então o array de dez colunas media **nove**, a guarda via desalinhamento onde
não havia e fechava o atendimento.

Essa armadilha tinha subido para o `CLAUDE.md` §5 **dois commits antes**, escrita
a propósito deste mesmo trabalho — e ainda assim foi pisada, porque lá ela estava
descrita no contexto dos arrays de opção aleatória do `getitem4`, não no de uma
tabela de constantes. Vale como lembrete de que armadilha registrada só protege
quem a procura no lugar certo.

**A saída é uma sentinela `-1` no fim das duas colunas de inteiro**, e ela deixa
a guarda mais forte do que era: com o último elemento sempre diferente de zero,
`getarraysize` volta a medir, e como o `setarray` grava por posição, uma coluna
com um valor a menos desloca a sentinela e o tamanho não bate. A coluna que dá o
tamanho passou a ser a de **texto**, que não tem elemento vazio e é a única das
três que `getarraysize` mede sem susto.

### E uma dúvida que o dono levantou, que o código já respondia

Ele perguntou se a coluna de Fruta dos Gatos da imagem tinha sido lida como
**custo do serviço**. Não foi: o serviço cobra `1.000.000 de zeny` **ou** um
lubrificante (`delitem .@paga, 1`), e a Fruta aparece só na Máquina Especial,
como preço de compra do lubrificante. O que estava errado era a **tabela do
relatório de entrega**, que pôs as duas coisas na mesma coluna sob o título
"custa" — e uma tabela ambígua num relatório custa a mesma rodada que um bug.

## Trinta e três itens em oito vitrines de Prontera (2026-08-18)

O pedido chegou como uma lista só, 35 números com o nome ao lado, sem dizer
quais lojas. Entraram **33** em oito das treze vitrines do quarteirão; um já
estava à venda e um ficou de fora por decisão do dono. É a segunda maior leva
que o Mercado Contemporâneo recebeu, atrás só da de 2026-08-16.

### Onde caiu cada peça, e quem decidiu

De novo foi o `Locations:` do `item_db`, e não o nome (regra 4.14):

| loja | entraram | ficou com |
|---|---|---|
| Sapateiro | 14 | 24 |
| Senhor das Armas | 7 | 32 |
| Lorde das Armaduras | 6 | 15 |
| Chapeleiro | 2 | 21 |
| Ocleiro | 1 | 30 |
| Capeiro | 1 | 24 |
| Acessorista | 1 | 50 |
| Adereceiro (visuais) | 1 | 126 |

**Cinco peças teriam ido para a loja errada por leitura de nome**, e desta vez
o engano seria sempre o mesmo: o nome descreve o *aspecto*, o `Locations:`
descreve o *slot*.

| id | nome | o que parece | o que é |
|---|---|---|---|
| 480023 | Sobretudo do Mestre | armadura | **capa** → Capeiro |
| 15383 | Sobretudo do Senhor do Tempo | capa | **armadura** → Armaduras |
| 450252 | Mensageiro da Morte | arma | **armadura** |
| 550018 | Pluma de Fênix | arco | **cajado** |
| 19118 | Super Óculos Poring | chapéu | `Head_Mid` → Ocleiro |

Os dois "Sobretudos" da mesma lista terminaram em lojas diferentes, e é o
exemplo mais limpo que este mercado já produziu de por que a regra existe.

**Nenhum override foi preciso.** Os cinco foram conferidos contra a linha
`Tipo:`/`Equipa em:` da descrição do bRO (`estado_item.py --id <n>
--descricao`), e nos cinco o bRO e o nosso `item_db` concordaram — o desacordo
que a regra 4.14 prevê simplesmente não apareceu nesta leva.

### Dois números do pedido não existiam, e os dois eram um dígito a menos

O `estado_item.py` respondeu *"não está no rAthena NEM nos 18845 do bRO"* para
dois IDs. Nos dois casos o vizinho de cinco dígitos tinha o **nome exato** que
o pedido pedia, o que fecha a identificação sem chute:

- `47007` → **470007** Botas do Caçador
- `170106` → **470106** Sapatos da Persistência

### O trabalho não estava nos 33, estava em 21

Treze das 33 peças não custaram nada: o rAthena tinha, o cliente tinha em
português, e o `valida_visual.py` aprovou antes de entrarem. O que custou:

| o que faltava | quantos | por onde |
|---|---|---|
| entrada no `itemInfo.lua` | 16 | `completa_iteminfo.py` |
| os 4 arquivos de arte | 6 | `instala_visual.py` |
| não existia no servidor | 4 | `db/guerra/item_db.yml` |
| estava no `itemInfo.lua` **em coreano** | 1 | `instala_item.py` |

### O Chapéu do Éden, e por que a receita da Lacma não serviu

O 19272 existe inteiro no nosso rAthena — `Garden_Of_Eden`, `Head_Top`, uma
cova, `View 1653`, arte 8 de 8. O que faltava era o **nome**: o `itemInfo.lua`
deste cliente o traz em coreano, e item sem nome em português não entra em loja
(regra 4.2).

O remédio de sempre não serviu, porque **o bRO também tem o 19272 em coreano**.
Quem tem o nome em português lá é o **19315** — que é o mesmo item com outro
número, e isso não é palpite: mesmo `identifiedResourceName` (`Garden_Of_Eden`),
mesmo `ClassNum` 1653, mesma cova, e a mesma ficha (DEF 5, peso 40, INT+5
DEX+5).

A receita registrada para esse caso é a da **Lacma** (13049 → 28739, 2026-08-16):
criar aqui o ID traduzido e pôr esse na vitrine. **Não foi o que se fez, e a
razão é combo.** O 19272 é citado por três conjuntos do `db/re/item_combos.yml`
— `B_Katrinn_Card`, `Fairy_Of_Eden` e `Symbol_Of_Eden` — e **dois dos parceiros
já estão à venda no mesmo quarteirão**: a Fada do Éden (20991) no Capeiro e o
Símbolo do Éden (460050) no Escudeiro. Conjunto é casado por AegisName, então
renumerar derrubaria os três, calado, e o jogador não veria bônus faltando —
veria um número menor.

Saiu mais barato traduzir a entrada de cliente: uma receita nova no
`instala_item.py`, com o texto do 19315 palavra por palavra. O ID pedido fica,
os três conjuntos ficam.

**Uma ressalva ficou por escrito**, na própria receita: a descrição do bRO
promete *"Dano mágico de todas as propriedades +15%"* e o `Script:` do nosso
vendor dá `bMagicAtkEle,10`. É a armadilha de sempre (§5, "a descrição discorda
do script") — o vendor é de outra revisão. O número não foi mexido: mudar bônus
é decisão do dono, não consequência de pôr a peça na vitrine.

### O campo que era zero fixo havia dezoito dias

Escrever aquela entrada esbarrou num defeito do `instala_item.py` que nunca
tinha tido como aparecer: ele gravava `slotCount = 0` e `ClassNum = 0`
**literais**, desde 2026-07-31.

Por seis itens seguidos isso esteve certo — nenhum dos nossos tinha cova nem
visual de cabeça. O Chapéu do Éden é o primeiro com os dois, e teria saído sem
o `[1]` no nome, sem a cova na janela de encaixe de carta e sem o id de visual,
**os três calados**. Os campos viraram `covas` e `visual`, opcionais, com zero
por padrão — as seis receitas antigas não mudaram de comportamento. A lição
subiu para o `CLAUDE.md` §5, junto com a outra desta rodada.

### A quinta leva de placeholders, e o recurso que não é identidade

Quatro itens não existiam no servidor e viraram entrada nossa. Ao procurar de
onde copiar a ficha de cada um, o `identifiedResourceName` do bRO apontou para
um item que o nosso vendor **já tem** nos quatro casos — e em dois deles isso
teria posto na loja o item errado:

| pedido | recurso | quem mais usa | é o mesmo? |
|---|---|---|---|
| 470004 Botas Imperiais [1] | `Imperial_Boots` | 22207 | **sim**, versão sem cova |
| 22224 Sapatos Fofinhos [1] | `Fluffy_FishShoes` | 22210 | **sim**, versão sem cova |
| 700102 Arco Experimental [2] | `Local02_Bow` | 18173 Yinyang Bow | **não** |
| 700080 Arco Mágico [3] | `Hs_Rg_Bow` | 700061 Herosria Rogue Bow | **não** |

Nos dois calçados a ficha inteira batia — peso, DEF, nível e o `Script:` linha
por linha —, e é o caso da Diadema do Paraíso (19024 → 19455) repetido: são
dois itens de verdade, a versão com cova e a sem, os dois presentes no bRO. O
pedido veio pelo ID **com** cova, então é esse que entrou, com o script copiado
do irmão e um `Slots: 1`.

Nos dois arcos não batia nada: ATQ 130 / nível 70 contra ATQ 180 / nível 105, e
ATQ 200 / sem cova / nível 200 contra ATQ 130 / três covas / nível 100. Nome de
recurso é o **desenho**, e sprite de arco é reaproveitado. Quem parasse ali
teria posto o arco errado na vitrine, com o nome certo e o desenho certo — e a
loja ficaria plausível. Virou armadilha no `CLAUDE.md` §5.

Os dois arcos entraram com a ficha do bRO e os conjuntos como `# TODO`, pelo
motivo das outras levas: as peças que os fecham (as quatro flechas, a Carta
Alma de Cecil, as sete cartas de Lichtern e irmãs) não estão em loja nossa, e
conjunto pela metade dá bônus fantasma.

### A revenda, que a regra 4.16 manda fechar e que quase escapou

Rodar `zera_revenda_das_lojas.py --conferir` **depois** de mexer nas vitrines
apontou **dez itens com lucro de 9 zeny por clique** — os dez que trazem
`Buy: 20` do vendor. Regenerado o `db/guerra/item_db_lojas.yml`, os 1636 itens
das 22 lojas voltaram a revender por zero.

O número é a própria conferência: a medição de 2026-08-17 dizia **1603**, e
1603 + 33 = **1636**. Bater com a medição anterior é o que separa "entrou o que
eu pus" de "entrou o que eu pus mais alguma coisa".

### O que ficou de fora, e por quê

**A Caixa do ArchAngeling (23073).** É `Type: Usable` / `Container` e não tem
`Locations:` nenhum; as treze lojas do quarteirão são todas por slot, então
nenhuma serve. E ela é caixa de sorteio: entrega 1x Botas do ArchAngeling
(22101) garantido mais um visual entre seis, o que a 1 zeny numa vitrine é
fonte infinita das botas. Levado ao dono no mesmo dia, a decisão foi deixá-la
fora e decidir depois — está na `PENDENCIAS.md` §1y, com as duas medições
prontas para quando a decisão vier.

Vale notar que o conjunto está a meio caminho sem ninguém ter pedido: as botas
que a caixa entrega são o par do **Super Óculos Poring (19118)**, que entrou
nesta mesma leva, no Ocleiro.

### Três nomes que o diff mostra indo do português para o inglês

O `nomes_pt_item_db.py` roda como parte desta receita, e desta vez o diff dele
tem uma linha que assusta: **três itens perderam o nome em português** no
`db/re/item_db_equip.yml`.

| id | antes, no `db/re/` | depois |
|---|---|---|
| 490290 | Anel de Ameretat | `Ameretat` |
| 490336 | Núcleo de Verus | `Dimension Linkage Stone` |
| 490337 | Amuleto Mitológico | `Amulet of Genesis Stone` |

**Não é regressão, e o jogo não muda.** Os três viraram itens NOSSOS em
2026-08-17 (os acessórios de lado trocado), e ganharam `Name:` em português no
`db/guerra/item_db.yml` — que é importado **depois** e vence. O nome efetivo do
servidor continua o português, e o cliente já mostrava português.

O que aconteceu é uma consequência de como a ferramenta funciona: ela
**reconstrói a partir do `.INGLES`** e **pula os itens nossos**. Pular, num
script que reconstrói, quer dizer *devolver o original do vendor*. As linhas em
português que estavam ali eram sobra de uma passada anterior a esses três serem
nossos. Ou seja o arquivo do vendor voltou ao estado canônico e a duplicata de
tradução sumiu — é limpeza, não perda.

**A leitura errada é cara**, e por isso fica registrada: quem vir esse diff e
"consertar" à mão devolve a duplicata, e aí passa a haver dois lugares dizendo o
nome do mesmo item, com o `db/re/` perdendo sempre. A conferência que decide é
`estado_item.py --id 490290,490336,490337`, que mostra de qual arquivo o nome
efetivo sai.

### Um comentário vencido, corrigido de passagem

A entrada da Lacma no `db/guerra/item_db.yml` afirmava desde 2026-08-16 que a
regra 4.16 fazia aquela adaga custar **20 zeny** na vitrine. A linha do Senhor
das Armas sempre disse `28739:1`, e desde 2026-08-17 o `item_db_lojas.yml` põe
`Buy: 1` por cima — ou seja o comentário descrevia uma regra que não roda. É a
regra 4.17 na variante "deixou de valer", e foi encontrada só porque a mesma
frase seria copiada para as entradas novas.


## Cinco martelos por giro, e o drop de mapa que rodava a 1x (2026-08-18)

Dois pedidos do dono no mesmo dia, sem relação entre si — mas o segundo virou o
achado da semana.

### A Sombrios Totais entrega cinco Martelos de Refino por giro

A máquina de sorteio do Centro da Ordem (`npc/guerra/maquina_de_sombrios.txt`,
`auction_01 189,58`) cobrava 2 Moedas Novas e devolvia **um** item de uma tabela
de quatro. O Martelo de Refino Sombrio (23436) é o consumível de refinar
equipamento Sombrio — um por tentativa, e a tentativa falha. A 15/34 de chance
de sair, o jogador pagava duas Moedas por *uma* tentativa de refino.

Passou a sair **5 por giro**. Os outros três prêmios continuam em 1.

**A quantidade virou a terceira coluna da tabela, e não um número no
`getitem`.** É a regra 4.11 pela terceira vez neste arquivo: a lista na tela, a
porcentagem, o `checkweight` e a entrega leem todos os mesmos arrays do
`OnInit`. Número escrito no `getitem` sairia de sincronia com o texto da janela
no dia em que alguém mudasse um dos dois, e a divergência **não daria erro** — a
máquina anunciaria cinco e entregaria um.

Três consequências que vieram junto:

- **O `checkweight` passou a receber a quantidade.** Cinco martelos pesam 50,
  não 10. Conferir 1 para entregar 5 é exatamente o buraco que a seção "Por que
  checkweight ANTES de cobrar" existe para fechar — e o Martelo de Refino é um
  dos três prêmios **sem `NoDrop`**, ou seja o que não cabe na mochila cai no
  chão do salão com o jogador já cobrado.
- **A guarda do `OnInit` ficou mais forte**: compara as três colunas, não duas,
  e a mensagem de `debugmes` diz qual delas destoou. Feita com dois `if` e não
  com um `||`, porque os operadores lógicos do rAthena não fazem curto-circuito.
- **Nenhuma quantidade pode ser 0** — além de não fazer sentido, zero em
  variável de `.` apaga a entrada do array e a coluna encolheria calada.

A quantidade só aparece na tela quando passa de 1 (`Martelo de Refino Sombrio
x5`), então as outras três linhas continuam como sempre foram.

### Os equipamentos ilusionais não caíam, e o motivo não estava no script

O pedido chegou assim: *"Equips ilusionais não estão caindo dos mapas
ilusionais. Exemplo: Ilusão da Tartaruga, o monstro Congelador Ominoso deveria
dropar Espada Ilusional 13469, que existe no game. As outras instâncias
Ilusionais também não."*

**E ele realmente não dropava.** A espada não está no `Drops:` do Congelador
Ominoso (3801, `ILL_FREEZER`) em `db/re/mob_db.yml` — procurar ali devolve
zero, o que parece item que não cai de nada. Equipamento ilusional é **drop de
mapa**: vive em `db/re/map_drops.yml`, um banco separado, indexado por mapa e
processado no fim do `mob_dead` (`src/map/mob.cpp:3372`, "Process map specific
drops"). Para monstro dentro de instância a busca é pelo `instance_src_map`.

Até aí, tudo montado e funcionando. **O problema é que drop de mapa não passa
pela taxa do servidor.** O `mob_getdroprate` chamado ali (`mob.cpp:3388`) só
aplica bônus de LUK e de equipamento do jogador; os `item_rate_*: 5000` de
`conf/guerra/battle_guerra.txt` não alcançam campo nenhum daquele arquivo. O
cabeçalho do próprio `map_drops.yml` do rAthena avisa, numa linha em inglês no
meio da documentação de campos: *"These drops are unaffected by server drop rate
and cannot be stolen."*

Ou seja: **num servidor de 50x, o ramo ilusional inteiro rodava a 1x.**

| item | `Rate` | chance por morte |
|---|---|---|
| Espada Ilusional (13469) | 25 | **0,025%** |
| Pedra da Ilusão | 10 | **0,010%** |
| Caixa da Ilha da Tartaruga | 5 | 0,005% |

O Congelador Ominoso tem **549.071 de HP**. A 0,025% são ~2.800 mortes para
meio a meio — e essa é a espada, o item barato do mapa. A troca de
`barter_ill_turtle` (`npc/re/merchants/barters/enchan_illusion_dungeons.yml`)
pede **100 Pedras da Ilusão** a 0,010% cada. Nada estava quebrado, e por isso
nada aparecia no log: o sintoma é indistinguível de azar.

**O conserto é um override gerado**, `db/guerra/map_drops.yml`, por
`ferramentas/escala_drops_de_mapa.py`, com o `Footer: Imports:` acrescentado ao
rodapé de `db/re/map_drops.yml` — que também não tinha rodapé nenhum, pelo mesmo
caminho do `quest_db.yml` de 2026-08-08. Decisão do dono: **fator 50**, o mesmo
`item_rate_equip: 5000`, e nos **18 mapas** do arquivo e não só nos dez
ilusionais. A espada passou a 1,25%, a pedra a 0,5%, as caixas a 0,25%.

Três coisas que o caminho ensinou, e que estão no `CLAUDE.md` §5:

- **O teto de `Rate` não é cortado, é recusado.** Acima de 100000 o `parseDrop`
  devolve `false` e o `parseBodyNode` descarta o **mapa inteiro**
  (`mob.cpp:7072`) — com os drops já lidos daquele mapa aplicados, ou seja um
  override pela metade e calado. O `min()` mora no gerador por isso. **117 dos
  687** batem no teto e ficam em 100%, todos de chefe: não é exagero da
  ferramenta, é o mesmo que já acontece com todo drop normal deste servidor,
  onde `item_rate_equip: 5000` com `item_drop_equip_max: 10000` já torna
  garantido qualquer drop de 2% ou mais.
- **A mescla é por `(Mapa, Monstro, Index)`, não por item.** Por isso o gerador
  escreve o `Item:` em cada linha ainda que o leitor não precise dele: se o
  vendor reordenar um Index numa atualização, o nosso arquivo escreveria a taxa
  de um item na linha de outro, calado. O `--conferir` compara os pares e
  denuncia.
- **Recarrega com `@reloadmobdb`**, e só com ele: é quem chama `mob_reload()`,
  que refaz o `map_drop_db` (`mob.cpp:7216`). `@reloaditemdb` e `@reloadscript`
  não pegam.

### E os encantamentos vinham em coreano

Com a espada caindo, apareceu o que estava atrás dela: as duas linhas de
**opção aleatória** na janela do item — o encantamento — vinham em coreano.

Não era erro de tradução, era um arquivo que nunca teve como ser traduzido. O
`data\luafiles514\lua files\datainfo\addrandomoptionnametable.lub` **não existe
solto em `cliente\data`**: o cliente lia o do `data.grf`, que é o original da
Gravity de 2021-11-03. As doze partes do `traduz_ptbr.py` nunca o tocaram
porque nenhuma delas tinha destino ali.

Virou a **décima terceira parte**, `encantamentos`. O que a torna diferente das
outras doze é de onde vem a **chave**:

| | fonte | por quê |
|---|---|---|
| chave | **o nosso GRF** (Gravity, 2021-11-03) | é `EnumVAR.<X>[1]`, resolvida em tempo de execução contra o `enumvar.lub` deste exe |
| texto | bRO, 239 de 252 | o acordo de 2026-08-02 |
| resto | ROenglishRE, 13 | as siglas de 4ª classe |

**A chave não podia sair do ROenglishRE**, que é de 2025 e traz opção que este
cliente não conhece — `EnumVAR.<X>` desconhecido vira `nil`, e `nil[1]` derruba
a tabela inteira: o efeito sumiria da janela em vez de aparecer sem nome. É a
mesma razão pela qual o `skilltreeview.lub` e a janela de missões partem do
coreano de 2021.

Os 13 que o bRO não tem são POW, SPL, STA, WIS, CON, CRT, P.ATK, S.MATK, RES,
MRES, H.PLUS e C.RATE, mais um de reflexão — as siglas de 4ª classe, iguais nos
dois idiomas, porque o bRO daquela época ainda não as tinha. **Nada ficou em
coreano:** 239 + 13 = 252.

### A armadilha do leitor, que quase escondeu o arquivo inteiro

O `ptbr.tabelas` respondeu, na primeira leitura, que aquela tabela tinha **uma**
entrada. Não era arquivo vazio nem leitura corrompida: o `_interpreta` sabia
resolver símbolo indexado por *string* (`SKID.NV_BASIC`) e devolvia `None` para
qualquer outro caso — e a chave desta tabela é símbolo indexado por **número**,
`EnumVAR.VAR_MAXHPAMOUNT[1]`. Com todas as chaves em `None`, o `dict` fica com a
última e o leitor responde "1", sem erro nenhum.

Um ramo novo no `GETTABLE` resolveu, e a regra ficou no `CLAUDE.md` §5:
**tamanho de tabela igual a 1 é sintoma de chave não resolvida.** O ramo é
acréscimo — só alcança o caso que antes virava `None` — e as sete outras partes
que usam o mesmo leitor continuam idênticas.

**Isto é cliente, e cliente não vai pelo deploy** (regra 4.18): o arquivo está
gerado em `C:\GuerraDoEmperium\cliente\`, e foi ao jogador como **patch 0006**,
publicado no mesmo dia - um arquivo só, 3.454 bytes no zip. A metade de
servidor (os cinco martelos e o `map_drops.yml`) continua dependendo do
`implanta.sh`, que sai do Mac.

---

## Vinte e nove itens em sete vitrines, e o número que existia dos dois lados (2026-08-18)

O segundo pedido do mesmo dia, e o mesmo formato: uma lista só, **33 números**
com o nome ao lado, sem dizer quais lojas. Entraram **29** em sete das nove
lojas do Mercado Contemporâneo. Dos quatro que sobraram, nenhum caiu por falha:
dois já estavam à venda desde 2026-08-16 (a Adaga do RWC, 13092, e a Lacma,
28739, as duas no Senhor das Armas) e dois são consumíveis sem slot, que o dono
decidiu deixar de fora.

### O Senhor das Armas recebeu 18 e quase dobrou

| loja | entraram | ficou com |
|---|---|---|
| Senhor das Armas | 18 | 50 |
| Ocleiro | 3 | 33 |
| Escudeiro | 3 | 14 |
| Capeiro | 2 | 26 |
| Lorde das Armaduras | 1 | 16 |
| Sapateiro | 1 | 25 |
| Acessorista | 1 | 51 |

De novo foi o `Locations:` quem decidiu (regra 4.14), e de novo o nome teria
errado em três — as duas "Caudas" (26163 e 26150) são **arma** de mão direita,
e o "Mamaragan" (22243) é **calçado**. Nenhum override foi preciso: nas peças
conferidas contra a linha `Tipo:`/`Equipa em:` da descrição do bRO, o nosso
`item_db` e o bRO concordaram.

### O caso novo: o número errado também existia

O pedido trazia **"Escudo encouraçado 28943"**, e as duas metades apontavam
para itens diferentes:

- o **28943** existe, e é o **Grimório Proibido**;
- quem se chama **Escudo Encouraçado** é o **28953** (`Poring_B_Shield`).

É a terceira vez que um número deste tipo de lista erra por um dígito — as duas
da manhã foram `47007` → `470007` e `170106` → `470106` —, mas as duas
anteriores se resolviam sozinhas: o número pedido **não existia**, então só
havia um candidato. Aqui os dois existem, os dois são `Left_Hand`, os dois estão
inteiros no servidor e no cliente e os dois iriam para o Escudeiro. Não há
medição que desempate um pedido consigo mesmo, então foi ao dono: **entrou o
28953, pelo nome.**

### O trabalho estava em oito peças, não em 29

| o que faltava | quantos | por onde |
|---|---|---|
| entrada no `itemInfo.lua` | 7 | `completa_iteminfo.py` |
| os 4 arquivos de arte | 3 | `instala_visual.py` |
| não existia no servidor | 2 | `db/guerra/item_db.yml` |
| `Name` em inglês no servidor | 5 | `nomes_pt_item_db.py` |

As contas se sobrepõem — o Manual Estelar (540018), a Maça de Esculápio
(550095) e o Mastro da Princesa (590014) aparecem nas três primeiras linhas
cada um. As outras 21 peças não custaram nada: o rAthena tinha, o cliente tinha
em português, e o `valida_visual.py` aprovou antes de entrarem.

### A sexta leva de placeholders: um katar e um martelo

Os dois que não existiam no servidor viraram entrada nossa em
`db/guerra/item_db.yml`, com os bônus lidos da descrição do bRO, como nas cinco
levas anteriores:

- **28025 Katares do Monarca** — katar, ATQ 150, nível 130. O `AegisName` é
  palpite (`Kingly_Katar`), mas com um apoio que os arcos da quinta leva não
  tiveram: o vendor já traz a família Monarca **inteira** sob o prefixo
  `Kingly_` — armadura (450141), bota (470046), manto (480051) e anel (490042)
  —, e as quatro são de nível 130, o mesmo dele. Os quatro `- Combos:` dessa
  família só citam essas quatro peças: não há conjunto para espelhar nem para
  derrubar.
- **16074 Martelo Cósmico** — maça de Superaprendiz, ATQ 1, dois slots. O ATQ 1
  não é erro de leitura: o ataque inteiro dele vem das habilidades aprendidas e
  do refino.

**A duplicação de crítico do katar ficou fora do script de propósito.** A linha
*"Duplica a chance de causar um ataque crítico"* da descrição descreve o
comportamento **nativo** do tipo `W_KATAR` no rAthena — o `status->cri *= 2` de
`src/map/status.cpp:6170`, aplicado a toda arma katar. Repeti-la como `bonus`
dobraria de novo.

**Os nomes de habilidade saíram do `skillinfolist.lub` deste cliente** (regra
4.12), não de memória: Lâminas de Loki é `GC_ROLLINGCUTTER`, Castigo de Loki é
`GC_CROSSRIPPERSLASHER`, Lâminas Retalhadoras é `GC_CROSSIMPACT`, Impacto de
Tyr é `KN_BOWLINGBASH`, Cavalo-de-Pau é `MC_CARTREVOLUTION`. Duas linhas não
casaram com tabela nenhuma e viraram `# TODO` na própria entrada: *"Mantém
[Investigar] ativo"* (e "Investigar" não é o `MO_INVESTIGATE`, que aqui se
chama Impacto Psíquico) e *"a cada nível de [Perícia com Machado e Espada]"*,
que não existe em nenhuma das cinco habilidades de machado deste cliente —
provavelmente é de 4ª classe posterior a 2021-11-03.

### O buraco de revenda desta leva era de 1,5 milhão por clique

O `--conferir` do `zera_revenda_das_lojas.py` acusou lucro por clique em **15
dos 29**, e um não era de 9 zeny: o **Fone Danificado (19245)** revendia por
**1.500.000** com a vitrine a 1 zeny — 1.499.999 z por clique, em laço. O Robe
Mágico (450132) e o Escudo de Penas (460003) vinham logo atrás, com 99.999 cada
um.

Fechado pelo caminho de sempre (regra 4.16): `Buy: 1` por override em
`db/guerra/item_db_lojas.yml`, regerado pelo script para **1665 itens**. O
`--conferir` depois disso responde *"nenhum item das três lojas revende por mais
do que custa"*.

Vale como confirmação do que a regra 4.16 previa: **item novo em vitrine de
Prontera reabre o buraco calado**, e metade da leva o reabriu.

### Uma divergência de cova, e ela é do cliente

A **Cauda Arco-Íris (26163)** é `Slots: 1` no nosso `item_db` **e** no bRO, mas
o `itemInfo.lua` deste cliente de 2021 diz **2**. O nome aparece com `[2]` e a
janela de encaixe de carta abre com uma cova só. Não veio desta leva e não se
conserta pelo servidor — quem desenha o nome é o cliente (regra 4.9). Fica
registrado no cabeçalho do mercado.

### Metade disto é cliente, e não vai pelo deploy

Treze arquivos moram em `C:\GuerraDoEmperium\cliente\` e só chegam ao jogador
por **patch** (regra 4.18): o `SystemEN\LuaFiles514\itemInfo.lua`, com as sete
entradas novas, e os **12 arquivos de arte** dos três itens que estavam sem
(`540018`, `550095`, `590014`) — dois `.spr`/`.act` de chão e dois `.bmp` de
ícone cada. Sem o patch, esses três aparecem sem nome e com caixa modal para
quem baixou o cliente antes. O que anda pelo git é só a linha das lojas, o
`item_db` e o `item_db_lojas.yml`.

O dono conferiu as sete vitrines em jogo no mesmo dia, e a metade de cliente
foi ao jogador como **patch 0007** — 13 arquivos, 22,86 MB crus em 2,48 MB de
zip, sha `bee86d16…`, conferido por HTTP depois de publicado. A metade de
servidor continua dependendo do `implanta.sh`, que sai do Mac (`PENDENCIAS.md`
§1y2) — e o mesmo deploy fecha a leva da manhã.

## O "Indestrutível" que a descrição prometia e o servidor não entregava (2026-08-18)

O dono relatou que **item indestrutível estava quebrando em batalha com
monstro** — arma, escudo, armadura. O exemplo veio com nome: **Lâmina
Sagrada**.

### Achar o item custou uma volta, e a volta explica o resto

"Lâmina Sagrada" não existe em `db/guerra/`, não existe nos NPCs e não aparece
como `Name:` em lugar nenhum do `rathena/`. Ela existe no **cliente**: é o
`identifiedDisplayName` do item **500009**, cujo `AegisName` no nosso vendor é
`Copy_Gram` e cujo `Name:` é a mesma "Lâmina Sagrada" — o mesmo 500009 que a
`zera_revenda_das_lojas.py` já tinha pegado revendendo a 250.000 zeny, ali
chamado de "Cópia de Gram". Procurar por nome de tela dentro do `rathena/` é
procurar no lugar errado: quem batiza é o `itemInfo.lua`.

E a descrição dele, no cliente, diz em roxo:

```
^a400cdIndestrutível em batalha.^000000
```

O `Script:` do item, no `db/re/item_db_equip.yml`, **não trazia**
`bonus bUnbreakableWeapon;`.

### Não era bug de mecânica — a trava existe e estava desligada

Vale registrar o que foi descartado, porque cada descarte é uma hipótese que
não precisa voltar:

- **`equip_natural_break_rate` está em 0** (`conf/battle/battle.conf`), e não
  temos override em `conf/guerra/`. Arma não quebra por atacar.
- **`break_mob_equip: no`**, ou seja não quebramos equipamento de monstro.
- **`equip_skill_break_rate` e `equip_self_break_rate` estão nos 100 padrão.**
- A tradução PT do `item_db_equip.yml` (o par `.INGLES` ao lado) mexeu em
  **linha de `Name:` e em mais nada** — `diff` fechou em zero fora delas.

O que quebra equipamento de jogador são as quatro habilidades de monstro
`NPC_ARMORBRAKE`, `NPC_HELMBRAKE`, `NPC_SHIELDBRAKE` e `NPC_WEAPONBRAKER`,
todas passando pelo `skill_break_equip` (`src/map/skill.cpp:1944`). E a
**primeira coisa** que ele faz é:

```c
if (sd->bonus.unbreakable_equip)
    where &= ~sd->bonus.unbreakable_equip;
```

Ou seja: a trava existe, funciona, e só não estava ligada. **E não há como
ligá-la por campo de `item_db` nem por flag** — o `unbreakable_equip` só recebe
bit por `bonus bUnbreakable<slot>` rodando no `Script:` do próprio item
(`src/map/pc.cpp:4262`).

### A medição: 540 dizem, 27 não entregam

Cruzados o `itemInfo.lua` do cliente (descrição com "Indestrut") e o
`item_db` do servidor (`Script:` com `bUnbreakable<slot>`), com o slot saindo
do `Locations:` e não do nome (regra 4.14):

| slot | itens sem o bônus |
|---|---|
| Arma | 2 |
| Escudo | 3 |
| Armadura | 7 |
| Elmo | 10 |
| Manto | 1 |
| Calçado | 4 |
| **total** | **27** |

De 540 itens do cliente que prometem indestrutível. **Sete estão à venda em
Prontera** — Lâmina Sagrada (500009), Escudo Divino (28962), Escudo da Fênix
(460023), Robe da Graça Divina (15421), Sobretudo do Mestre (480023), Chifres
Oníricos (400396) e a Boina Sustenida (400476, na loja de troca). Os outros 20
caem de monstro ou vêm de outras fontes.

**Duas famílias ficaram de fora, de propósito:**

- **241 armas** de machado, maça, cajado, livro e huuma. O próprio
  `skill_break_equip` já as isenta por tipo, antes de sortear
  (`skill.cpp:1968`). Pô-las no override congelaria o `Script:` de 241 armas
  do vendor por um efeito que já existe — custo sem benefício.
- **4 equipamentos sombrios** (24152, 24153, 24154 e 24155 — um deles chamado,
  sem ironia, *Malha Sombria Indestrutível*). Não existe `bUnbreakableShadow`:
  o `unbreakable_equip` só tem bit para os seis slots normais. Eles caem no
  `EQP_SHADOW_GEAR`, que nenhuma habilidade de monstro pede — na prática não
  quebram, mas se um dia quebrarem não há como travar por `db/`. Ficou o aviso
  no `--conferir`.

### O conserto

`ferramentas/marca_indestrutiveis.py`, gerando
`db/guerra/item_db_indestrutivel.yml` — o terceiro `- Path:` do rodapé de
`db/re/item_db.yml`, entre o nosso `item_db.yml` e o `item_db_lojas.yml`.

Duas decisões de forma que valem para qualquer override de `Script:`:

1. **O override repete o script inteiro.** O `parseBodyNode` **substitui** o
   campo `Script:` quando ele aparece; não acrescenta. E `EquipScript:` não
   serve de atalho — aquele roda uma vez, no clique de equipar, e o
   `status_calc_pc_` refaz os bônus do zero sem ele.
2. **O `bonus` entra na primeira linha, não na última.** Script que termine em
   `if (cond)` sem chaves engoliria a linha seguinte. No topo não há o que
   engolir, e nenhum dos 27 scripts começa com algo que dependa de ordem.

O preço de o arquivo existir está escrito no cabeçalho dele: enquanto estiver
ligado, correção do rAthena no `Script:` desses 27 itens não chega ao jogo.
Rodar o script de novo depois de atualizar o vendor — o `--conferir` responde
em segundos e sai 1 se faltar.

**A ferramenta só roda no Windows**, porque a lista de quem promete
indestrutível sai do `itemInfo.lua`, que está fora do git. O `.yml` gerado é
versionado e vale para as três máquinas.

### O que recarrega

`@reloaditemdb`, e só — **não precisa relogar**. O `itemdb_reload`
(`src/map/itemdb.cpp`) termina com um `status_calc_pc(sd, SCO_FORCE)` para cada
jogador online, e é ele que refaz os bônus. É o oposto do `Locations:`, que
exige login ou troca de mapa porque quem reenvia o inventário é o
`clif_parse_LoadEndAck` (`CLAUDE.md` §5).

Tudo isto é **servidor**: nada aqui mora em `C:\GuerraDoEmperium\cliente\`, e
portanto nada depende de patch. Vai ao jogador pelo `implanta.sh`.

## O Instinto de Defesa dos MVPs, e por que ele matava tanto (2026-08-18)

Pedido do dono: *"bloquear instinto de defesa na cheffenia por uso dos MVPs.
Hoje os MVPs estão matando MUITO com essa skill! E não há nem o que fazer, nem
como saber que ela está ativa, perdendo qualquer forma de contornar ou suportar
a situação"*.

Cheffenia é o **Corredor Fantasma** (`npc/guerra/corredor_fantasma.txt`), mapa
`vis_h01`, os 130 chefes.

### Quem lançava era UM, não os MVPs

A primeira medição desfez o plural do pedido: dos **65 tipos** da sala, só um
tem `ST_REJECTSWORD` no `db/re/mob_skill_db.txt` — o **2239 Stalker Gertie**,
dois no chão como todos os outros. A linha dele, repetida em `idle`, `chase` e
`attack`:

```
2239,Stalker Gertie@ST_REJECTSWORD,idle,390,5,10000,0,30000,yes,self,always
```

Nível 5, **100% de chance**, recarga de 30 segundos. E o `SC_REJECTSWORD` de
nível 5 (`src/map/status.cpp`) vale `val2 = 15 × nível = 75%` de chance de
refletir, `val3 = 3` golpes, e `tick = INFINITE_TICK` — **não expira sozinho**.
Ou seja: praticamente sempre ligado, e recarregado a cada meio minuto.

### As três razões de doer aqui e não doer no kRO

1. **O reflexo é 50% do dano que o JOGADOR causou**, e não uma fração do HP do
   monstro (`battle.cpp`, `battle_calc_weapon_final_atk_modifiers`, bloco
   *"Reject Sword"*). Num servidor em que se bate em MVP para centenas de
   milhares, metade disso volta de uma vez. **Quanto mais forte o jogador, mais
   forte o golpe que o mata** — a única alavanca que ele tem é justamente a que
   piora a situação.
2. **Não passa por redução nenhuma.** Sai por `battle_fix_damage`, que não passa
   pelo `battle_calc_damage`: escapa da redução de carta e escapa também da
   redução geral de 80% (`REDUCAO-DE-DANO.md` §4d, onde ele já estava listado
   como inofensivo — e era, na conta de PvP em que a §4d foi escrita: ali ele
   devolve um dano *já reduzido*. Contra MVP, o dano de origem não veio
   reduzido de lugar nenhum).
3. **Não há como saber que está ativo.** O `SC_REJECTSWORD` não tem ícone, e o
   monstro só desenha alguma coisa na tela **quando o reflexo já aconteceu** —
   o `clif_skill_nodamage` sai na mesma linha do dano. Quem morre descobre
   depois de morto.

E um quarto detalhe que tornava o diagnóstico pior: o reflexo só alcança quem
está de **adaga, espada de uma mão ou espada de duas mãos** (o teste de arma
está naquele mesmo bloco). Dois jogadores no mesmo chefe, um cai e o outro não.

### A saída: proibição por mapa, em `src/custom`

`src/custom/habilidade_proibida.hpp` — uma tabela de `(mapa, habilidade)`,
consultada no topo do laço do `mobskill_use` (`src/map/mob.cpp`), **antes** do
teste de recarga. Monstro em mapa listado se comporta como se aquela linha do
`mob_skill_db` não existisse: sem lançamento, sem animação, sem recarga gasta.
Hoje a tabela tem uma entrada:

```
{ "vis_h01", ST_REJECTSWORD }
```

**Por que não tirar a linha do `mob_skill_db`**, que seria o caminho curto:

1. **Não chegaria à produção.** O `mob_skill_db` é CSV, não YAML — não tem
   `Footer: Imports:`, e os únicos caminhos que o `sv_readdb` lê são
   `db/re/mob_skill_db.txt` (arquivo do rAthena, que a §2 proíbe editar) e
   `db/import/mob_skill_db.txt` — e **`db/import` está no `.gitignore` do
   vendor**. Arquivo não versionado não sai desta máquina.
2. **Alcançaria os outros lugares.** O 2239 também nasce na instância
   Laboratório do Wolfchev, e os irmãos dele — **2225 Gertie** e **2232 Stalker
   Gertie** — têm a mesma habilidade em `lhz_dun04`. Nada disso foi pedido.

### O que ficou de fora, de propósito

Na mesma sala há mais reflexo, e **não foi mexido**: `CR_REFLECTSHIELD` em seis
chefes (1086 Golden Thief Bug e 2235 Paladin Randel no nível 10, 1719 Detale e
2319 Buwaya no 5, 2068 Boitata no 3, 2202 Kraken no 1) e `NPC_MAGICMIRROR` em
três (1871 Falling Bishop, 1874 Beelzebub, 2131 Lost Dragon). São de outra
natureza: o `CR_REFLECTSHIELD` devolve `10 + 3 × nível` por cento e passa pelo
`battle_calc_return_damage`, que a redução geral alcança. Se um dia doerem
também, são duas linhas na mesma tabela.

### O que recarrega

**Nada** — é código. Exige recompilar o map-server (e portanto pará-lo antes de
linkar), e a produção só recebe pelo `implanta.sh`.

**Em 2026-08-18 ainda NÃO tinha rodado em lugar nenhum**, e vale registrar como
a conferência se faz, porque a sonda é de graça e desfez um "funcionando" dito
de boa-fé: o `map-server.exe` do dev era de **2026-08-17 21:57** e o processo no
ar tinha subido às **01:54** daquele exe — ou seja, mais velhos que o `mob.obj`
recém-compilado. **Binário mais velho que o `.obj` é a prova de que o link não
aconteceu**, e nenhuma observação em jogo antes disso é sobre este código.

Tudo isto é **servidor** (`src/`): nada mora em `C:\GuerraDoEmperium\cliente\`,
então **não há patch a publicar** — vai ao jogador pelo deploy, que sai do Mac
(`CLAUDE.md` §5).

---

## O Zé do Caixão, e o Manteleiro que mudou de fileira (2026-08-20)

Pedido do dono, em duas partes: mover o **Manteleiro** de `prontera 163,155`
para `155,131`, e criar um NPC novo em `159,131` — **"Zé do Caixão"**, com o
**mesmo sprite da Tranqueiras** —, vendendo nove caixas e cubos nomeados um a
um. Oito entraram; um não, e o porquê está no fim.

### O que a mudança do Manteleiro fez com o desenho do mercado

A fileira dos visuais (`y=155`) tinha **quatro** colunas: Costumeiro,
Adereceiro e Camareiro nos três slots de cabeça, e o Manteleiro numa quarta
coluna (`x=163`), de capa. Ele saiu de lá e desceu duas fileiras, e com isso a
fileira de baixo — que era só a Tranqueiras — encheu:

```
           x=151          x=155          x=159          x=163
 y=155   Costumeiro     Adereceiro     Camareiro       (vazio)
 y=137   Carta Acess.   Carta MVP      Carta Chefe
 y=131   Tranqueiras    MANTELEIRO     ZÉ DO CAIXÃO
```

**Só a coordenada mudou.** O Manteleiro continua sendo de
`npc/guerra/mercado_de_visuais.txt`, continua sendo a quarta loja daquele
mercado, e os 25 itens, a placa e o sprite `1_M_MERCHANT` são os mesmos. Não
houve `disablenpc` nem duplicata: o NPC é nosso, e mover NPC nosso é editar a
linha dele.

O que custou trabalho foi o **contrário** de mexer no código: os quatro lugares
que descreviam a fileira antiga. O cabeçalho do `mercado_de_visuais.txt` tinha
um diagrama com a quarta coluna e um parágrafo dizendo *"As QUATRO células
foram conferidas… e a de x=163 com as nove vizinhas livres"*; o
`scripts_guerra.conf` dizia *"o Manteleiro (x=163)"*; o `CATALOGO-VISUAIS.md`
repetia a coordenada em dois pontos; e o cabeçalho da `tranqueiras.txt` tinha
um desenho da fileira de baixo com dois `--` onde agora há dois NPCs. Nenhum
deles daria erro — é a §4.17 outra vez, e a única defesa é procurar a
coordenada velha em vez de confiar na memória. `grep -n "163,155"` respondeu em
um comando.

### As duas células, conferidas antes de plantar

`155,131` e `159,131` no `prontera.gat` **deste cliente**: tipo 0, andável,
altura 1,00 nos quatro cantos, e as 24 vizinhas do quadrado 5×5 de cada uma
também tipo 0. O NPC ativo mais próximo de cada uma fica a quatro células
(Tranqueiras / Manteleiro) ou a seis (Carta de MVP / Carta de Chefe), então
nada foi desligado nem empilhado.

Um vizinho merece registro porque **está no arquivo e não está no ar**: o
`Suspicious Coffin#2013HE` do rAthena fica em `prontera 154,136`, a poucas
células — mas o `npc/events/halloween_2013.txt` está comentado no
`scripts_athena.conf`. Quem um dia ligar aquele arquivo ganha um NPC empilhado
ali perto, e isso está dito no cabeçalho do arquivo novo.

### O que o Zé do Caixão vende, e o que isso realmente é

Oito itens a **1 zeny**. Nenhum é equipamento: os oito são `Usable` com a
bandeira `Container`, e o `Script:` de cada um é **uma linha só**,
`getgroupitem(IG_<GRUPO>)`. Ou seja **o que a loja vende é um sorteio** — o
acervo de verdade são os itens dos oito grupos de `db/re/item_group_db.yml`:

| id | item | grupo | sorteia |
|---|---|---|---|
| 100547 | Caixa de Espólios | `IG_BIOWEAPON_HELM_BOX` | 12 |
| 23772 | Caixa de Armas OS | `IG_EP17_1_SPC01` | 16 |
| 23992 | Caixa de Bioarmas | `IG_BIO_W_BOX` | 39 |
| 23073 | Caixa do ArchAngeling | `IG_ANGELPORING_BOX` | 7 |
| 23766 | Caixa de Armadura do Herói | `IG_OVERWHELM_ARMOR_BOX` | 6 |
| 23806 | Caixa de Armas Ancestrais | `IG_HERO_WEAPON_BOX` | 38 |
| 100437 | Cubo Reforçado Primordial | `IG_HERO_WEAPON_CUBE` | 37 |
| 23115 | Cubo Sombrio de Classe | `IG_CLASS_SHADOW_CUBE` | 90 |

**245 itens no total, e essa foi a conferência que valeu a pena.** A §4.4 manda
validar a arte do item que entra na vitrine, e os oito passaram — 32 checagens,
zero falta. Mas caixa não entrega caixa: entrega o que está dentro, e **item
sem arte entrega caixa de erro ao jogador na hora de abrir**, longe da loja e
longe de quem editou. Os 245 foram conferidos de uma vez, numa chamada só do
`valida_visual.py`: os 245 existem no `item_db`, os 245 têm entrada no
`itemInfo.lua` deste cliente e os 245 deram arte completa — **1028 checagens,
zero falta**. Nenhum precisou de arte do bRO nem de entrada nova de cliente, e
**é por isso que esta entrega não precisa de patch**: vai inteira pelo deploy.

Os oito grupos também foram **contados**, não supostos. Grupo vazio faria a
caixa sumir na mão do jogador sem erro nenhum — nenhum está vazio.

### O preço: 1 zeny escrito, e não `-1`

A Tranqueiras — que tem o mesmo sprite e fica a oito células — cobra `-1`, que
o `npc_parse_shop` troca pelo `Buy` do `item_db` (`npc.cpp:4146`). **Aqui isso
daria tudo de graça:** nenhuma das oito caixas declara `Buy`, então o `Buy`
delas é zero. Por isso o preço é o **1 escrito na linha**, que é a convenção
das lojas de Prontera (§4.16).

A outra ponta — a revenda — já era zero antes de qualquer override, porque as
oito também não declaram `Sell` (e duas delas, a de Armas OS e a do
ArchAngeling, são `NoSell`). Ainda assim o arquivo novo **entrou na lista de
lojas do `zera_revenda_das_lojas.py`**, e essa é a parte que não podia ficar de
fora: a lista daquele script é escrita à mão, e vitrine que ele não conhece
**não é medida por ninguém**. Item novo posto ali amanhã reabriria o buraco de
dinheiro infinito calado. Depois de acrescentado, a contagem foi de **1665 para
1673** itens a `Buy: 1` — os oito, e só os oito, que é o número que se esperava
ver.

### Duas coisas que o jogador vai sentir e não estão escritas em lugar nenhum

**Duas das oito são presas ao personagem**, e isso vem do `item_db` do rAthena,
não de decisão nossa: a **Caixa de Armas OS (23772)** é
`NoDrop`/`NoTrade`/`NoSell`/`NoCart`/`NoStorage`/`NoGuildStorage`/`NoMail`/
`NoAuction`, e a **Caixa do ArchAngeling (23073)** é o mesmo menos o
`NoStorage`. Comprou, não sai do inventário. **Duas pesam 200 cada** — a de
Armadura do Herói e a de Armas Ancestrais, `Weight: 2000`. Nada avisa antes.

E há um detalhe do `getgroupitem` que **não** é o do `getitem` de script: com a
mochila cheia, **o conteúdo não cai no chão — ele some**. O `itemdb.cpp:3104`
chama `pc_additem` e, no fracasso, só manda um `clif_additem` de erro; não há
`map_addflooritem` naquele caminho. E o `pc_useitem` apaga a caixa **antes** de
rodar o script (`pc.cpp:6516`), então a caixa se perde junto. Na prática o
buraco que a própria caixa deixa quase sempre cabe o prêmio; o caso que morde é
pilha de caixas com a mochila no limite.

### O nono item, e por que ele não entrou

A **Caixa de Cubos Refinadores (102592)** foi pedida **duas vezes na mesma
lista** — a segunda como *"Cubo de cubos refinadores"*, mesmo id. Ela não
existe nem no nosso vendor nem no `itemInfo.lua` deste cliente: só no bRO.

E não é caso de trazer uma entrada e pronto. Pela descrição do bRO ela sorteia
**um de sete Cubos de Refino**, e **três deles também faltam aqui** (102589 de
Mora, 102590 de Brasilis, 102591 de Wolfchev). Os quatro que existem são
`DelayConsume` com `laphine_upgrade()` — o efeito não mora no item, mora em
`db/re/laphine_upgrade.yml`, uma tabela por conjunto de equipamento. Repor os
três é escrever três tabelas dessas à mão (as Relíquias de Mora ao +12, os
equipamentos do Festival de Brasilis ao +9 e os do Laboratório de Wolfchev ao
+12, cada lista com dezenas de itens), mais quatro entradas de `item_db`, mais
quatro entradas de cliente — e entrada de cliente só chega ao jogador por
patch.

**Um item de aparência trivial custava mais que os outros oito somados.** O que
respondeu isso em dois comandos foi o `estado_item.py --id <lista>` seguido de
`--descricao`: o primeiro disse que ela não existe dos dois lados, o segundo
listou os sete cubos que ela promete. A pendência está na `PENDENCIAS.md` §1z2,
com o caminho inteiro para quando o dono decidir se vale.

### O que recarrega

`@reloaditemdb` **antes** do `@reloadscript` — nesta ordem, porque o
`npc_parse_shop` descarta item que não esteja no `item_db` em memória e a
vitrine subiria sem ele, calada (§5). O `item_db_lojas.yml` regerado entra pelo
mesmo `@reloaditemdb`. Nada disto é cliente: **não há patch**, e a produção
recebe pelo `implanta.sh`, que sai do Mac.

## Quarenta e três itens em cinco destinos, e o gorro que não era do Éden (2026-08-20)

Pedido do dono, algumas horas depois do Zé do Caixão: uma lista de **43 itens**,
com o destino escrito ao lado de apenas sete deles. Os outros 36 vieram sem
destino nenhum — e foi o `Locations:` de cada um que decidiu, como manda a
§4.14.

A entrega fechou em **41 dos 43**. Um item não pôde entrar em vitrine nenhuma
(a Ferramenta Mágica de Gelo, e o motivo está adiante) e cinco já estavam à
venda — mas esses cinco não são perda, são a lista repetindo o que já existia.

### Os cinco destinos

| destino | itens | como |
|---|---|---|
| as nove lojas do quarteirão | **32** | `mercado_contemporaneo.txt`, 1 zeny |
| Tranqueiras | **4** | `tranqueiras.txt`, pelo preço de compra |
| Máquina de Sombrios Gerais | **3** | `barters_guerra.yml`, 10 Moedas Novas |
| Zé do Caixão | **1** | `ze_do_caixao.txt`, 1 zeny |
| nenhum | **1** | 490029 — sem arte |
| (já estavam à venda) | 5 | 490118, 490068, 19437, 400203, 2198 |

É a primeira rodada que toca **as nove lojas de equipamento de uma vez**. O
Acessorista levou 8, o Lorde das Armaduras 7 e o Sapateiro 6; as outras seis,
entre 1 e 3.

### O `Locations:` decidiu, e o nome teria errado em quatro

De novo (§4.14), e de novo o nome é a pista errada:

| id | nome | o que parece | onde foi |
|---|---|---|---|
| 450163 | **Manto** do Cientista | capa | Lorde das Armaduras (`Armor`) |
| 15169 | **Manto** do Kardui | capa | Lorde das Armaduras (`Armor`) |
| 28565 | **Máscara** de Oni | chapéu | Acessorista (`Left_Accessory`) |
| 32013 | **Perna** de Metal | calçado | Senhor das Armas (`Right_Hand`, lança) |

O que muda desta vez é o que **não** aconteceu: os 38 foram conferidos um a um
contra a linha `Tipo:`/`Equipa em:` da descrição do bRO, e o nosso `item_db` e o
bRO **concordaram nos 38**. É a primeira rodada grande sem um único override —
nas de 2026-08-09 e 2026-08-12 houve quatro.

### Três itens não existiam no servidor, e um deles tinha armadilha

Viraram a **sétima leva de placeholders** do `db/guerra/item_db.yml`:

- **470321 Sapato Fantasma** — o irmão que faltava da família Fantasma;
- **460000 Égide das Divindades** — escudo, `View: 4`;
- **490250 Anel Transcendental** — `Left_Accessory`, +5 em tudo (+15 no 180).

A armadilha é do calçado, e é a do `identifiedResourceName` (§5): o bRO chama o
470321 de **`Runaway_P_Shoes`**, e o nosso vendor **tem esse nome** — no 470089,
"Runaway Thoughtform Shoes". Não é o mesmo item: DEF 12 / nível 100 / HP e SP
+20% contra DEF 0 / nível 170 / ATQ da arma +5%. Reusar o nome do recurso como
AegisName teria colidido com um item de verdade. Ele entrou como `Phantom_Shoes`.

**Os bônus não foram adivinhados: foram calibrados contra o que o vendor já
implementa.** A descrição do bRO é prosa, e a mesma prosa aparece em itens cujo
`Script:` está escrito ali ao lado — os cinco pares da própria família Fantasma
(470293 a 470300). Isso fixou a tabela de equivalências, que ficou registrada no
cabeçalho da leva. A que mais engana:

> **"Dano físico +N%" não é "ATQ da arma +N%".** A segunda é
> `bonus bAtkRate,N`; a primeira é `bonus2 bAddClass,Class_All,N`, provada pelo
> conjunto [Medalha de Honra] do `Krieger_Ring1` (2772). O bRO usa **as duas no
> mesmo item** — o próprio 470321 —, então não há como serem sinônimos.

O calçado ganhou também o conjunto **[Aura Fantasma]** espelhado em
`db/guerra/item_combos.yml`: cópia exata do grupo de FOR que o vendor já dá aos
quatro irmãos dele. Os outros quatro conjuntos que a descrição promete
(Bate-Estacas Motorizado, Chave Maxi, Estal, Injetor Acoplável) ficaram como
`# TODO` — o vendor não conhece nenhum deles, então não havia o que copiar.

### A Ferramenta Mágica de Gelo: metade do pedido foi feita, e a outra metade não pode ser

O pedido era duplo — *"490029 (vamos traduzir para Ferramenta Mágica de Gelo)"*.

**A tradução foi feita.** A entrada de cliente estava em inglês (veio do
ROenglishRE, `Server = "jRO"`) e foi traduzida inteira, nome e descrição, pelo
`instala_item.py`. O bRO **não tem este ID** — nem ele nem nenhum outro da
família Magictool, varridos os 18845 do `iteminfo_new.lub` por nome e por
recurso —, então o texto saiu do **`Script:` do vendor**, e não de cópia. Isso
revelou de passagem que a descrição inglesa estava **incompleta**: faltava a
linha da Maestria Arcana (`bonus bDelayrate,-30`). Foi acrescentada.

**A venda não foi.** Os quatro arquivos de arte do recurso
`Geffenia_Magictool_Ice` **não existem** — nem no nosso `data.grf` nem no do
bRO, conferido nos dois. Item sem arte entrega caixa de erro ao jogador (§4.4),
então ele ficou fora da vitrine. Para entrar um dia basta escolher um doador de
arte, e isso é decisão do dono: é dar a ele o desenho de outro item.
`PENDENCIAS.md` §1z3.

### O gorro que não era do Éden — um bug calado, de dois dias

Foi achado **de raspão**, ao usar o `instala_item.py` para a tradução acima.

A função `recurso()` procurava o recurso do item doador com o regex
`identifiedResourceName = "([^"]*)"`. A string **`unidentifiedResourceName`
termina em `identifiedResourceName`**, e a linha do *unidentified* vem primeiro
no bloco — então o regex casava com **ela**, e o que voltava era o recurso do
item **não identificado**.

Falha calada e pela metade. Quando as duas linhas trazem o mesmo recurso — o
caso de todo `Etc` e todo consumível, ou seja das **seis primeiras receitas** da
tabela — o resultado é idêntico e nada aparece. Ela só morde **equipamento**, que
é onde o kRO põe um gorro genérico de "item não identificado" no primeiro campo.

E foi exatamente o que aconteceu com o **Chapéu do Éden (19272)**, a sétima
receita, posta em 2026-08-18: ele ficou com **`캡`** — o gorro genérico — no
ícone de inventário, na imagem de *collection* e no sprite de chão, no lugar de
`Garden_Of_Eden`.

**E o `valida_visual.py` dava "8 de 8 ok" sobre isso**, porque a cabeça vestida
vem do `accessoryid`/`View` e não deste campo: quatro dos oito arquivos estavam
certos, e os outros quatro apontavam para uma arte que existe — só que é a
errada. Validador que confere *presença* não pega troca de arte por outra arte.

A auto-referência agravava: `arte_de: 19272` faz o script **ler a si mesmo**,
então bastou uma rodada ruim para o valor errado virar a fonte da rodada
seguinte, e não havia mais de onde recuperar o certo.

O conserto foi em três partes:

1. `(?<!un)` no regex, com o porquê escrito ali;
2. um campo novo, **`recurso`**, que aceita o nome do recurso **por extenso** —
   é o que quebra o laço da auto-referência, porque a receita é versionada e o
   cliente não;
3. as duas receitas que apontavam para si mesmas (19272 e 490029) passaram a
   usá-lo. O Chapéu do Éden voltou a desenhar `Garden_Of_Eden`.

A regra que sobra subiu para o `CLAUDE.md` §5.

### O que mais custou trabalho

Onze peças, não 32:

| o que faltava | quantas | ferramenta |
|---|---|---|
| entrada no `itemInfo.lua` | 7 | `completa_iteminfo.py` |
| os 4 arquivos de arte | 6 | `instala_visual.py` |
| existir no servidor | 3 | `db/guerra/item_db.yml` |
| arte de **manto** | 1 | `instala_manto.py` |
| `Name` em inglês no servidor | 6 | `nomes_pt_item_db.py` |

(As contas se sobrepõem — o Manto do Cientista conta em três dessas linhas.) O
`nomes_pt_item_db.py` trocou **exatamente seis linhas** do `db/re/` — as dos
seis itens cuja entrada de cliente nasceu ou mudou nesta rodada. Nada mais se
moveu, o que é a prova de que ele é idempotente.

**Uma das onze acendeu uma promessa antiga.** O **Manto do Cientista (450163)**
diz *"Indestrutível em batalha"* na descrição e o `Script:` do vendor não trazia
`bonus bUnbreakableArmor` — a peça quebraria, e o jogador a perderia (§4.19). O
`marca_indestrutiveis.py` o pegou e gerou o override. Isso só apareceu porque a
**entrada de cliente dele nasceu nesta rodada**: a lista dos que "dizem
Indestrutível" sai do `itemInfo.lua`, então item novo ali pode acender uma
promessa que ninguém tinha como ver antes. É o efeito de segunda ordem que a
regra previa, agora medido.

A capa que precisou de arte de manto foi as **Asas de Arcanjo Caído (2589)**,
`View 3`. Os **Espinhos Violeta (20940)**, `View 39`, já a tinham completa. Os
dois `View` estão abaixo do teto de 120 que este exe desenha (§5), então
**nenhum dos dois gastou slot doador** — continuam 28 livres.

### Os quatro da Tranqueiras, e os treze usos que ninguém esperava

Três foram pedidos por nome (**Flauta Uivante 6124**, **Pincel de Grafite
6122**, **Pincel de Maquiagem 6121**) e o quarto — a **Muda de Mandrágora
(6217)** — veio no meio da lista de equipamento. Ela é `Etc`: nenhuma das nove
lojas do quarteirão servia, porque todas são por slot. Foi para a Tranqueiras
por decisão do dono, com os outros três.

A ligação item→habilidade foi **lida do `db/re/skill_db.yml`**, no `Item:` do
bloco de requisito de cada uma, e não suposta pelo nome. Os dois pincéis
surpreendem: não servem a uma habilidade cada, servem a **treze**.

| item | habilidades |
|---|---|
| 6124 Flauta Uivante | [Adestrar Worg] |
| 6122 Pincel de Grafite | **sete** de Trapaceiro — Borrifar Tinta, Pintar Armadilha, Sede de Sangue, Símbolo do Caos, Porta Dimensional, Cópia Explosiva, Redemoinho de Absorção |
| 6121 Pincel de Maquiagem | as **seis** Máscaras — Fraqueza, Melancolia, Tolice, Ociosidade, Infortúnio, Vulnerabilidade |
| 6217 Muda de Mandrágora | [Grito da Mandrágora] |

Os nomes saem do `skillinfolist.lub` **deste cliente**, que é a tabela que o
jogo lê (§4.12). Consequência prática, e o motivo de o grupo valer a pena: sem
esta vitrine o Trapaceiro não tinha onde comprar em Prontera o insumo de treze
das habilidades dele.

**A Tranqueiras vende a `-1`, ou seja pelo `Buy` do `item_db`**, e por isso os
quatro precisaram passar no teste do `npc_parse_shop` antes de entrar. Passam:
os quatro têm `Sell` exatamente igual a `Buy/2` (10/5 nos três pincéis e flauta,
2000/1000 na muda), então `0,75·Buy` contra `1,24·Sell` dá 7,50 contra 6,20 e
1500 contra 1240. Nenhum aviso sai, e o lucro por clique é zero.

### As três peças Sombrias, e a decisão de 2026-08-16 que elas não desfazem

A Máquina de Sombrios Gerais foi de nove para **doze**, e as três novas — Colar
(24155), Malha (24154) e Luvas (24152) Sombrias Indestrutíveis — são as
**primeiras peças de vestir** daquela vitrine, a **10 Moedas Novas** cada.

Isso parece contrariar 2026-08-16, quando o Anel do Viajante saiu de lá por ser
*"a única coisa vestível entre nove consumíveis"*. Não contraria: aquele era
acessório comum, e estas são **peças Sombrias** — `Shadow_Left_Accessory`,
`Shadow_Armor` e `Shadow_Weapon`, o mesmo equipamento que os seis cubos ao lado
sorteiam. O que a máquina passa a vender é o prêmio dela **sem o sorteio**, e é
por isso que o preço pulou uma ordem de grandeza (cubo 2, combinador 1).

**Uma ressalva de nome fica registrada, e ela é do cliente:** o pedido chamou a
24152 de *"Manopla Sombria Indestrutível"*, e o `itemInfo.lua` deste cliente a
chama de **"Luvas Sombrias Indestrutíveis"**. Quem desenha o nome de cada linha
da janela de troca é o cliente — o pacote leva só o ID (§4.9) —, então o que o
jogador lê é o segundo. Não se conserta pelo servidor.

De passagem, o `marca_indestrutiveis.py` avisa que essas três **não têm bônus
possível**: não existe `bUnbreakableShadow`, e elas caem no `EQP_SHADOW_GEAR`,
que nenhuma habilidade de monstro pede. Na prática não quebram; o aviso é para
o dia em que quebrarem.

### A nona caixa do Zé do Caixão

A **Caixa de Elmos Especiais (23767)** entrou no mesmo dia em que o NPC nasceu,
com o mesmo feitio das oito: `Usable`/`Container` com um `getgroupitem` de uma
linha. O grupo dela é o **menor da vitrine** — cinco elmos, contra os 90 do Cubo
Sombrio de Classe —, e os cinco foram conferidos um a um (40 checagens, zero
falta): Quepe do Cão-mandante (19300), Bênção Celestial (19249), Elmo do
Xogunato (19263), Chapéu Chique com Pena (19296) e Quepe de Amistr (19308).

### Duas divergências de cova, as duas registradas

- **Morango Cristalizado (2979)** — `Slots: 1` no nosso `item_db` **e** no bRO,
  mas o `itemInfo.lua` deste cliente de 2021 diz **0**. O nome aparece sem o
  "[1]" e a janela de encaixe de carta não enxerga a cova. Não se conserta pelo
  servidor (§4.9), e não veio desta leva — o `completa_iteminfo.py` não a
  corrige de propósito, porque não toca em entrada que já existe.
- **Égide das Divindades (460000)** — entrou com `Slots: 1`, que é o `slotCount`
  do bRO, enquanto o pedido a escreveu sem o "[1]". Onde os dois discordam vale
  o bRO (regra 3).

### O buraco de revenda

O `--conferir` do `zera_revenda_das_lojas.py` acusou lucro por clique em **8 dos
33** que entraram em vitrine de zeny, todos de 9 z — nenhum caso grande desta
vez. Fechado pelo caminho de sempre: `Buy: 1` por override em
`db/guerra/item_db_lojas.yml`, regerado para **1706 itens** (eram 1673).

### O que recarrega, e o que precisa de patch

`@reloaditemdb` **antes** do `@reloadscript` — nesta ordem, porque o
`npc_parse_shop` descarta item que não esteja no `item_db` em memória e a
vitrine subiria sem ele, calada (§5). Mais `@reloadbarterdb` para a Máquina de
Sombrios, que **não** pega com `@reloadscript`.

**Metade disto é cliente e não vai pelo deploy (§4.18):** as 8 entradas novas de
`itemInfo.lua`, a tradução do 490029, os 24 arquivos de arte de item, os 6 de
arte de manto e o conserto do Chapéu do Éden moram em
`C:\GuerraDoEmperium\cliente\` e só chegam ao jogador por **patch**. Sem ele, os
seis itens novos aparecem **sem nome** na vitrine e o Chapéu do Éden continua de
gorro genérico. `PENDENCIAS.md` §1z3.

---

## A missão da Sala Secreta ganha português e caminho no minimapa (2026-08-21)

Dois pedidos do dono, sobre a mesma missão: **acentuar o texto** dos NPCs da
Sala Secreta da Ordem e, nos diálogos **que se repetem**, pôr uma palavra
clicável apontando o próximo passo.

### O texto tinha nascido em ASCII puro

Não era mojibake nem U+FFFD (§5): os dois arquivos da missão simplesmente não
tinham **um único byte acentuado**. `menino_do_amuleto.txt` (a Criança e o
Dario) e `senha_da_sala_secreta.txt` (Suad, Assessor, Bolaozão, Maram e o teste
do guardião) foram escritos sem acento nenhum, e no
`guardas_do_centro.txt` só o Guarda do canto leste — o que fecha a missão —
estava assim, enquanto os outros sete já tinham acento desde 2026-08-11.

Foram **166 trocas** ao todo, em `mes`, rótulos de `select`, os dois
`mapannounce` e o `dispbottom` do teste, o nome do monstro invocado
("Guardião Reforçado") e os nomes de tela da **Criança** e do **Bolaozão**. Os
comentários continuam em ASCII, como em todo o projeto.

Feito **por script**, com âncora em ASCII, `assert` de contagem em cada troca e
um `decode('cp1252')` de volta antes de gravar — a ferramenta de edição do
assistente teria trocado todo byte acentuado do arquivo por U+FFFD (§5). Duas
armadilhas conhecidas apareceram e foram pagas de graça pelos `assert`: a
contagem de `mes "[Crianca]"` era 15 e não 10, e uma âncora de linha com **dois
tabs** de recuo casa também dentro da mesma linha com **seis** — a de dentro do
primeiro ramo da Criança —, então a âncora passou a levar o fim de linha nas
duas pontas.

Três correções que não são de acento, e ficam registradas por serem escolha e
não regra: `por hora` → **`por ora`** (Maram), `Bem vindo` → **`Bem-vindo`**
(Guarda) e o rótulo `Perguntar por que da euforia` → **`Perguntar o porquê da
euforia`** (Criança).

### Os quatro links de navegação, e os dois que ficaram de fora

A etiqueta `<NAVI>` dentro do próprio `mes` — lida pelo **cliente**, não pelo
servidor — já era conhecida do projeto: estreou em `crianca_de_comodo.txt` em
2026-08-13, e é lá que a sintaxe e os três números do fim estão explicados.

| Quem repete | Palavra | Vai para |
|---|---|---|
| Criança, estados 1–11 | `aqui` | portal do Centro da Ordem, `prontera 165,168` |
| Suad, estados 4–6 | `aqui` | Assessor, `cmd_in02 63,66` |
| Suad, estados 8–11 | `aqui` | Comandante Maram, `cmd_in02 73,86` |
| Bolaozão, repetição | `ali em cima` | Assessor, `cmd_in02 63,66` |

**Dois não têm link, por decisão do dono:** o Assessor mandando procurar o
Bolaozão (estado 5) e o Maram mandando procurar o Guarda do Centro (estado 11).
Achar esses dois **é** a missão — dar o caminho mataria o passo. O Dario, que
manda o jogador para Comodo, também ficou de fora pelo mesmo motivo.

Três decisões de desenho que valem para o próximo link:

- **Só no ramo que se repete**, nunca no que avança a variável. O primeiro é a
  cena; o segundo é o lembrete de quem se perdeu. No caso da Criança os dois
  blocos têm o mesmo texto palavra por palavra, e o que os separa é o recuo.
- **O texto do link é ASCII puro** — por isso o do Bolaozão diz `ali em cima` e
  não "lá em cima". O `doc/script_commands.txt` avisa que código de cor colado
  em letra acentuada pode sair errado, e o `^4D4DFF` do azul é nosso, na mão.
- **Os três de Comodo apontam para dentro do próprio `cmd_in02`**, o mapa de
  quem fala — navegação no mesmo mapa, o caso mais simples. O `cmd_in02` está
  na tabela de navegação deste cliente (`navi_map_krpri.lub` e
  `navi_link_krpri.lub`, conferido no `data.grf`), o que **não** é prova de
  efeito na tela (§5): só o clique em jogo diz se o caminho é traçado.

Pega com **`@reloadscript`**. Nada disto é cliente — não precisa de patch.

---

## Três coisas novas na área logada: download, personagem preso e chamados (2026-08-22)

Pedido do dono, três itens numa frase: um caminho para o download dentro do
painel, um jeito de o jogador tirar personagem preso, e um formulário de
chamados — *"como ainda faltam itens, traduções, quests e correções, precisamos
deixar um espaço pros jogadores abrirem ticket"*. O painel de leitura dos
chamados foi explicitamente adiado: **por ora só grava**.

### 1. O download dentro do painel

O botão existia só na tela de boas-vindas. Quem criava a conta caía direto no
painel, e o instalador ficava a um *Voltar* de distância que ninguém
descobria — o pior lugar possível para a única coisa que a pessoa precisa fazer
em seguida. Agora ele é o **primeiro** botão do painel, e o único em cor de
ação (`--rubro`); o resto continua fantasma.

**Isso obrigou o `app.js` a saber que há sessão aberta**, coisa que ele nunca
soube. O caminho painel → download → *Voltar* passou a ser comum, e sem esse
estado o *Voltar* jogava um jogador logado na tela de boas-vindas, onde o botão
"Conta" abre o formulário de **login** para quem já entrou. São três linhas:
uma variável `logado`, um desvio de `conta` para `painel` dentro do `vaiPara`, e
o `data-ir` do *Voltar* da tela de download reapontado para o painel quando há
sessão. O `data-ir` é lido **no clique**, não na ligação do evento, então
reapontar o atributo basta.

### 2. Destravar personagem — e a guarda que faz isso ser seguro

O problema é o da §1d da `PENDENCIAS.md` visto do outro lado: há mapas que o
rAthena conhece e o nosso cliente de 2021 ainda não tem, e o jogador **consegue
chegar neles**. Quem chega não morre — fica preso, porque toda entrada seguinte
no jogo o põe de volta no mesmo lugar. Até aqui só um GM tirava, um a um.

O botão lista os personagens da conta e move o escolhido para
`prontera,155,183` (célula conferida contra o `db/re/map_cache.dat`, que é o
único dos três que tem a Prontera de renewal — `CLAUDE.md` §5).

**A guarda é o `online = 0`, e ela vai dentro do próprio `UPDATE`.** O
char-server carrega o personagem do banco quando ele entra no jogo e só escreve
de volta na saída (`char_mmo_char_tosql`): um `UPDATE` feito com o jogador
conectado seria **sobrescrito**, e o site teria dito "pronto" para uma coisa que
não aconteceu — a pior das duas falhas possíveis aqui. Pôr a condição só na
leitura de antes não bastaria: entre ler e escrever o jogador pode ter entrado.

**Três decisões que não são óbvias:**

- **O `last_instanceid` é zerado junto.** É a metade do conserto que se
  esquece: quem ficou preso dentro de instância continua sendo mandado para a
  cópia dela se o campo sobreviver.
- **O ponto de retorno (`save_map`) só é mexido quando aponta para o MESMO mapa
  em que o personagem está preso.** Zerar sempre custaria ao jogador um ponto de
  retorno legítimo em Payon ou Geffen; deixar sempre o devolveria para a
  armadilha na primeira morte.
- **Não pede a senha, e as outras duas ações do painel pedem.** Trocar senha e
  apagar PIN mexem no acesso à conta, então cookie roubado não pode bastar.
  Mover personagem **parado** para a praça de Prontera não tira nada de ninguém:
  é reversível andando, e o `online = 0` já impede o único abuso imaginável
  (arrancar alguém de uma guerra). Pedir senha aqui seria atrito na tela de quem
  já está travado e irritado.

### 3. Os chamados — e por que o site passou a ter DUAS conexões com o banco

A tabela é a `guerra_site_chamado`, e ela é a **primeira do projeto em
utf8mb4**. Todo o resto do banco é latin1 porque o *jogo* lê, e o cliente de
2021 não entende outra coisa (`CLAUDE.md` §4.1). Chamado não passa pelo jogo em
momento nenhum: nasce num formulário web e vai ser lido num painel web. Guardar
em latin1 obrigaria a converter nas duas pontas e perderia calado tudo o que não
coubesse em cp1252 — e jogador escreve emoji em chamado.

**O preço é que o charset é escolhido na ABERTURA da conexão**, e é ele que
decide como o MySQL interpreta os bytes que chegam. Uma conexão só guardaria
acento de chamado como mojibake ou recusaria a gravação inteira, as duas
caladas — e a segunda só apareceria no dia em que alguém escrevesse com acento.
Então são dois pools: a `db` em latin1 para `login` e `char`, a `dbTexto` em
utf8mb4 só para os chamados. Custa conexão ociosa, não memória do processo.

**E a volta desse mesmo problema apareceu na leitura:** nome de personagem chega
em latin1, e o nosso `conf/guerra/char_guerra.txt` permite acento em nome. Sem
converter, o `encoding/json` troca cada byte acentuado por U+FFFD e o jogador
**não reconhece o próprio personagem na lista**. O `deLatin1` do `banco.go` faz
isso à mão — a tabela é de 32 entradas porque só a faixa `0x80-0x9F` diverge (o
"latin1" do MySQL é CP1252) — e foi conferida byte a byte contra o cp1252 do
Python, nos 256. Feito à mão para não acrescentar `golang.org/x/text`: o
servidor compila sem rede, e uma dependência nova por vinte linhas não se paga.

**A `estado` já nasce na tabela**, mesmo sem ninguém para lê-la. Acrescentá-la
junto com o painel exigiria um `ALTER TABLE` numa tabela que já teria chamado
dentro, e o valor de um chamado antigo teria de ser adivinhado.

Os limites: assunto de 5 a 120 caracteres, mensagem de 15 a 4000, **contados em
runas e não em bytes** — "correção" tem 9 letras e 11 bytes, e medir em `len()`
apertaria o limite sozinho para quem escreve português de verdade, com o campo
do formulário discordando do servidor sem ninguém entender por quê. O teto de
cinco chamados por hora é contado **no banco** e não no limitador de memória:
reiniciar o site não pode zerar a contagem de quem estava justamente enchendo a
fila. E o número do chamado vai para a tela, porque sem ele o jogador não tem
como cobrar depois.

### O que foi conferido, e como

Não há navegador nesta sessão, então a conferência foi de API contra um MariaDB
12 em contêiner, carregado com o `sql-files/main.sql` do rAthena e o nosso
`site/sql/site.sql`:

| | |
|---|---|
| nome de personagem com acento (`Filip\xE3o` em latin1) | volta `Filipão` no JSON |
| destravar preso em `1@dth3`, ponto de retorno no mesmo mapa | move os dois |
| destravar preso em `ba_maison`, ponto de retorno em Payon | move só a posição, **Payon preservado**; `last_instanceid` de 42 → 0 |
| personagem conectado | recusa, e a linha no banco não muda |
| personagem que já está em Prontera | recusa |
| `char_id` de outra conta | "não encontrado", sem dizer qual dos dois motivos |
| chamado com acento **e emoji** | volta idêntico do banco |
| `tipo` fora da lista (`"; DROP TABLE"`) | vira `outro` |
| sexto chamado na mesma hora | recusado |
| `deLatin1` nos 256 bytes | idêntico ao cp1252 do Python |

O que **não** foi conferido, por não haver navegador: a tela. Falta olhar o
painel com as cinco dobras, a lista de personagens no celular e o `<select>` do
tipo de chamado.

---

## O deploy do site sai do deploy do jogo, e o gatilho deixa de se desarmar (2026-08-22)

Ia rodar o `implanta.sh` para publicar as três novidades da área logada, com
três jogadores online, e a conta não fechou: o deploy leva tudo que está entre o
commit do servidor e o HEAD, e ali havia **dois commits do Windows com três
arquivos de NPC**. `rathena/` mudou é o gatilho de reiniciar o jogo — os três
cairiam por causa de uma mudança de site.

O dono decidiu, e ampliou o pedido: *"opção 1, mas inclusive se não temos um
script pra atualizar SÓ o site, precisamos. Não podemos ter um script só que
atualiza tudo."*

### Por que não foi um script novo

A lógica de deploy não é o `git pull`: é o `runuser -u ragnarok` (sem ele os
arquivos nascem `root:root` e o servidor perde a escrita), o pré-voo que aborta,
a ordem dos quatro serviços. Copiar isso para um segundo arquivo garante que as
duas cópias divirjam, e a errada é sempre a que alguém roda.

Então virou um **modo**: `atualiza_servidor.sh --so-site`, com dois wrappers no
Mac — `implanta.sh` e `implanta_site.sh`. O `--` do `ssh libraro 'bash -s --
--so-site'` é o que faz a opção chegar ao script que vem pelo stdin, em vez de
ser lida pelo próprio bash.

### O problema de verdade não era o modo: era o gatilho

Um deploy só de site **consumia** o gatilho do deploy seguinte, e isso já estava
documentado no `CLAUDE.md` §5 desde 2026-08-16, quando foi feito à mão pelo
mesmo motivo (não derrubar três jogadores). A decisão de reiniciar era o diff
entre o HEAD de **antes** do `git pull` e o de depois; quem atualizasse só o
site já teria feito o pull, então o `implanta.sh` seguinte achava `rathena/` sem
mudança e **não reiniciava** — imprimindo *"nada do jogo mudou, ninguém foi
derrubado"*, que é a frase de sucesso. O disco novo, o processo velho, e nada no
log.

Construir o modo `--so-site` em cima disso seria **industrializar a armadilha**:
o que era um deslize manual passaria a acontecer toda vez.

**O conserto é trocar a pergunta.** Não *"o que mudou no repositório desde o
último pull?"* — que qualquer atualização parcial responde errado — e sim *"o
que mudou desde o que está RODANDO?"*. Dois arquivos na raiz do servidor, fora
do git, guardam a resposta:

| | |
|---|---|
| `.carimbo-jogo` | o commit com que os quatro servidores estão no ar |
| `.carimbo-site` | o commit com que o binário do site foi construído |

O `--so-site` mexe **só no segundo**. E o script ainda **lista** no fim os
arquivos de `rathena/` que chegaram ao disco e não estão no ar, com o lembrete
do `@reloadscript` — porque o modo só é honesto se a mudança que ficou para trás
for visível.

Três detalhes que fazem os carimbos não terem lado errado:

- **Carimbo ausente cai no `ANTES`**, o HEAD de antes do pull. É o valor certo
  na primeira execução e para quem vem da versão anterior do script, porque até
  aqui "o que estava no disco" e "o que estava rodando" eram a mesma coisa.
- **Carimbo apontando para commit que o repositório não conhece** (ramo
  reescrito, clone novo) é pior que carimbo nenhum: todo diff contra ele
  falharia e o script cairia no lado errado de cada decisão. Um `cat-file -e`
  filtra, e o inválido cai no mesmo `ANTES` — ou seja, **reinicia**.
- **O carimbo do jogo só avança quando os processos de fato passam a rodar o
  commit novo**: por restart, ou porque nada do jogo mudou. Ele é escrito no
  **fim**, e como o script morre no primeiro erro (`set -e`), não chegar lá é a
  forma de não carimbar.

### A prova, antes de tocar no servidor

A lógica das três decisões foi extraída para um script de mesa e rodada contra o
repositório de verdade, com o servidor em `244f71c` e o HEAD em `eb160c6`:

| cenário | compila | reinicia | site |
|---|---|---|---|
| hoje, sem carimbo nenhum | não | **sim (derruba)** | sim |
| depois do `--so-site` | não | **sim (derruba)** | não |
| idem, com `.carimbo-jogo` parado | não | **sim (derruba)** | não |
| depois de um `implanta.sh` completo | não | não | não |
| carimbo com lixo dentro | não | **sim (derruba)** | sim |

A linha que importa é a segunda: **depois de publicar só o site, o gatilho
continua armado.** Era exatamente o que se perdia antes.

### O defeito que só apareceu no deploy de verdade

O primeiro `implanta_site.sh` fez tudo certo — ninguém caiu, os três NPCs foram
listados como pendentes — e **não criou o `.carimbo-jogo`**. Ler com fallback
não bastava: no modo `--so-site` o carimbo do jogo não avança, então um carimbo
que não existisse também não **nascia**. A execução seguinte voltaria ao
fallback, que a essa altura já é o commit novo — e as mudanças de jogo que
vieram naquele mesmo pull passariam a estar **atrás** da base, sumindo da conta.
A armadilha inteira, de volta, pelo caminho oposto.

A correção é semear os dois carimbos **logo depois de lê-los**, e não no fim: no
instante seguinte ao `git pull`, com nada reiniciado ainda, o `ANTES` descreve
com exatidão o que está no ar. A sequência foi então provada em três rodadas
(`--so-site`, `--so-site`, `implanta.sh`), e o carimbo do jogo fica parado em
`244f71c` nas duas primeiras, com o *reinicia* continuando **sim** — só a
terceira o avança.

Vale como lembrete de que **script de deploy não se prova rodando uma vez**: o
primeiro `--so-site` passou em tudo o que dava para ver, e o defeito morava na
execução *seguinte*. Foi a leitura do estado deixado no servidor — e não a saída
do script — que o denunciou.

### O que ficou registrado onde

A entrada do `CLAUDE.md` §5 não foi apagada — foi **corrigida**. A armadilha
deixou de existir pelo caminho do script, e continua valendo para quem der
`git pull` à mão no servidor, que avança o repositório sem avançar carimbo
nenhum. A receita nova é a `RECEITAS.md` §13, e a tabela dos quatro destinos da
§0 ganhou a linha do `site/sql/`, que nenhum deploy roda.

---

## A caixa de texto sem estilo, e o cache que o navegador inventa (2026-08-22)

O dono abriu o formulário de chamado e mandou o print: a caixa de texto dividia
a linha com o rótulo *"O que aconteceu"*, estreita e desalinhada. O pedido foi
direto — *"vamos deixar ele sozinho em uma linha"*.

**O CSS no ar já fazia exatamente isso.** Um `curl` na folha pública mostrava a
regra `select, textarea { display: block; width: 100% }` no lugar. O que a tela
mostrava era uma cópia velha, guardada pelo navegador do dono.

### Por que o navegador guardou, se ninguém mandou guardar

Resposta sem `Cache-Control` **não fica sem cache**: o navegador inventa um. É o
cache heurístico do RFC 9111, e a regra usual é considerar a cópia fresca por
**10% do tempo decorrido desde o `Last-Modified`**. Isso inverte a intuição —
quanto mais velho o arquivo, mais tempo a versão obsoleta continua valendo. Um
`estilo.css` parado havia uma semana seguiria sendo servido do disco por umas
quinze horas depois de trocado, **sem uma única requisição ao servidor**: sem
requisição não há 304, e sem 304 não há linha no log.

Ou seja, era a família de falha que este projeto mais persegue: o deploy diz
sucesso, o arquivo certo está no servidor, e para o jogador não mudou nada. E o
diagnóstico natural — mexer no CSS — aponta para o único lugar onde o defeito
não está.

Três pistas que confirmaram antes de qualquer conserto:

- os `input` apareciam estilizados e o `select`/`textarea` não. Os primeiros já
  estavam na regra **antiga**; os dois últimos só entraram na nova;
- o `select` tinha a aparência nativa do macOS, com as setinhas azuis;
- o `curl -sI` mostrava `Last-Modified` e **nenhum** `Cache-Control`.

### O conserto

`Cache-Control: no-cache` no estático, que não quer dizer *"não guarde"* e sim
*"guarde, mas pergunte antes de usar"*. Com o `Last-Modified` que o
`http.FileServer` já manda, a pergunta volta como um **304 de zero byte** —
medido. Para um site deste tamanho isso é mais barato que a alternativa
(versionar o nome de cada arquivo), que exigiria um passo de build que aqui não
existe.

E em `/api/` o cabeçalho é outro: `no-store`. Ali trafega nome de conta, e-mail
e lista de personagens, e resposta com dado pessoal não se guarda em disco
nenhum. Foi posto **antes** do handler, para valer também nas respostas de erro,
que saem por outros caminhos — conferido no 401.

**O que o conserto não alcança:** cache já envenenado. Quem carregou a página
antes só vê o novo com recarga forçada ou quando o prazo heurístico vencer — e
o próprio `index.html` está no mesmo caso, o que descarta o truque de versionar
o endereço do CSS. Daqui para a frente não acontece mais.

A caixa ganhou de passagem 150px de altura de partida, em vez de 120: é o campo
principal daquele formulário, e caixa pequena convida ao relato de uma linha,
que é justamente o relato que não resolve.

---

## O estilo de corpo que nunca chegou a existir (2026-08-22)

O Cupom de Roupa voltou da `PENDENCIAS.md` §0b-a, e o que parecia o fim de um
conserto de 2026-08-17 era o começo de outro. **Eram três defeitos empilhados,
e cada um só ficava visível depois de o anterior sair da frente.** Nenhum deles
dava erro.

### O primeiro: o binário no ar era anterior ao conserto

O `src/custom/estilo_de_corpo.hpp` e o enxerto no `pc.cpp` foram escritos em
2026-08-17 às 23:17. O `map-server.exe` que estava rodando era das **21:57 do
mesmo dia** — o `pc.obj` chegou a ser recompilado em 18/08, mas o link nunca
sobrescreveu o executável (o `LNK1104` de servidor no ar, §5). Vinte e quatro
horas de teste em jogo contra um binário que não tinha o conserto dentro.

Recompilado e religado. **O sintoma não mudou em nada** — e é isso que fez o
resto aparecer.

### O segundo: um arquivo do vendor que ninguém lia

Com o binário certo, o `@bodystyle 4332` respondia *"This job has no alternate
body styles"*. Esse recado sai de `job->alternate_outfits.empty()`
(`src/map/atcommand.cpp:1965`), e o vetor estava vazio **para todo trabalho**.

A causa: o `JobDatabase::getDefaultLocation()` (`src/map/pc.cpp:13819`) aponta
só para `db/re/job_stats.yml`, e é o **`db/re/job_outfits.yml`** que traz os
treze `AlternateOutfits`. Aquele arquivo não tinha `Footer:`, não era citado em
`conf/` nenhum e não era carregado por código nenhum: estava **órfão no
vendor**, com o formato certo e sem ninguém para lê-lo. Religado por
`Footer: Imports:` no `job_stats.yml` — o mesmo caminho do `quest_db.yml` e do
`map_drops.yml`, seguro porque o `parseImports` mora no `YamlDatabase`
(`src/common/database.cpp:176`) e os dois arquivos têm o mesmo cabeçalho
(`JOB_STATS`, versão 4).

Depois de `@reloadpcdb` o recado mudou para *"Número inválido especificado"* —
a lista passou a existir. Ainda não funcionava.

### O terceiro: a guarda vencida, e o que a denunciou

O `pc_changelook`, no `case LOOK_BODY2:`, faz:

```cpp
estilo_de_corpo_resolve( sd, &val );   // nosso: 0 -> classe, 1 -> 4332
if( !job_db.exists( val ) ){
    return;                            // <- morria aqui
}
sd->status.body = val;
```

`job_db.exists()` é `find(key) != nullptr` (`src/common/database.hpp:103`), e o
`job_db` só ganha entrada por um `Jobs:`. **Nenhum arquivo do vendor declara os
ids 4332..4344 num `Jobs:`** — o `job_outfits.yml` só os cita dentro de
`AlternateOutfits`, que empurra o número para o vetor do trabalho *pai* e não
cria entrada nenhuma. Então a guarda reprovava **todo** valor válido, sempre, e
o `clif_changelook` do fim da função nunca rodava: nenhum pacote saía. Como
`pc_changelook` é `void`, o `@bodystyle` imprimia *"Aparência alterada"* logo
depois, incondicionalmente.

É a mesma vencidez do `db/re/stylist.yml` de 2026-08-17, uma camada abaixo: a
guarda foi escrita quando `LOOK_BODY2` valia 0 ou 1 — Aprendiz e Espadachim,
dois trabalhos que o `job_db` conhece.

**O que denunciou foi o banco, e a evidência era um padrão, não um erro.** Uma
consulta ao `char` mostrou **todo** personagem com `body` igual a `class`
(Abemus 4060/4060, Libra 4077/4077, Carmelio 1/1, Fagas 14/14). Esse é
exatamente — e somente — o ramo `val == 0` do `estilo_de_corpo_resolve`, que
devolve `sd->status.class_`, um id que o `job_db` conhece e que por isso passa
pela guarda. Nenhum personagem tinha 4332: o outro ramo morria antes de gravar.
Ou seja a função rodava, e só metade dela sobrevivia.

### O conserto, e por que é dado e não C++

`db/guerra/job_estilo_de_corpo.yml` declara os treze ids num `Jobs:`, sem campo
de propriedade nenhum, e entra pelo mesmo rodapé. A alternativa era **substituir**
a linha `if( !job_db.exists( val ) )` do rAthena, e substituição não sobrevive a
merge por si (§2 do `CLAUDE.md` — há exatamente uma no projeto, no `battle.cpp`,
listada como risco). Não foi preciso: os treze são trabalhos de verdade, estão
no enum de `src/common/mmo.hpp` e são citados pelo próprio `job_outfits.yml`.
Declará-los é dar ao `job_db` o dado que o vendor esqueceu de embarcar.

**Efeito colateral conferido em vez de suposto, e a primeira leitura estava
errada.** Uma varredura por `job_db.` sugeriu que nada enumera o banco — mas o
`JobDatabase::loadingFinished()` (`pc.cpp:14277`) itera `*this` e avisa sobre
trabalho sem tabela de EXP. Ele faz `continue` quando `!pcdb_checkid(job_id)`, e
nenhuma faixa do `pcdb_checkid` (`pc.hpp:1219`) cobre 4331+ — a última é
`JOB_SKY_EMPEROR2 = 4316`. As entradas ficam inertes, só para a guarda achar.

### O que ficou provado, e o que era palpite

A arte **existe** e nunca foi o problema: 101 `.spr` de corpo em
`data\sprite\<humano>\<corpo>\<sexo>\costume_1\` no `data.grf` de 2021-11-03,
incluindo `룬나이트_남_1.spr` e `슈라_남_1.spr`. Isso responde a pergunta que
ficou em aberto na seção do Xanin e Edgard, onde se registrou que *"não foi
verificado se o GRF de 2021 tem os sprites que ele pede"*.

Conferido em jogo em 2026-08-22, nos **dois** caminhos: `@bodystyle 4332` num
Rune Knight e o Cupom de Roupa na Estilista de Prontera (`prt_in 243,168`) num
Sura. Os dois trocam o visual.

**Nada disto é cliente — não precisa de patch.** São dois arquivos de `db/`, que
vão por deploy (`RECEITAS.md` §0). Em jogo pega com **`@reloadpcdb`**, que chama
o `pc_readdb` (`src/map/atcommand.cpp:4490`) e não derruba ninguém.

## Quarenta e seis itens nas nove vitrines de Prontera (2026-08-26)

O pedido veio **já agrupado por slot** — "Equipamentos para cabeça (topo)",
"(meio)", "(baixo)", armaduras, calçados, capas, armas, escudos, acessórios —,
com 47 números. Entraram **46**, nas nove lojas do Mercado Contemporâneo. O
quadragésimo sétimo não é equipamento e foi para o **Zé do Caixão**, a loja de
caixas — ver o último bloco desta seção.

| loja | entraram | ficou com |
|---|---|---|
| Retoqueiro | 10 | 23 |
| Chapeleiro | 8 | 30 |
| Acessorista | 8 | 67 |
| Ocleiro | 6 | 42 |
| Senhor das Armas | 4 | 55 |
| Lorde das Armaduras | 3 | 26 |
| Capeiro | 3 | 32 |
| Sapateiro | 3 | 34 |
| Escudeiro | 1 | 17 |

### A primeira lista grande em que o `Locations:` não discordou de nada

Toda rodada anterior teve pelo menos uma peça cuja loja o nome errava — a
Piscadela de Freya, a Máscara de Minorous, as duas "Caudas" que eram arma, o
"Manto do Cientista" que era armadura. Nesta, as **duas** conferências que a
regra 4.14 manda fazer deram acordo nos 46: o agrupamento do dono bateu com o
`Locations:` do nosso `item_db`, e o `item_db` bateu com a linha
`Tipo:`/`Equipa em:` da descrição do bRO. **Nenhum override de `Locations:`.**

O agrupamento do pedido acertou até onde costuma escorregar: a **Máscara de
Onça-Pintada** (5539) é `Head_Low` **e** `Head_Mid` **e** `Head_Top` no
`item_db`, foi pedida como topo, e foi para o Chapeleiro — o mesmo caso do Véu
das Gemas Sagradas (19106), de 2026-08-12.

### O trabalho estava em 24 peças, não em 46

| o que faltava | quantos | por onde |
|---|---|---|
| entrada no `itemInfo.lua` | 23 | `completa_iteminfo.py` |
| `Name` em inglês no servidor | 17 | `nomes_pt_item_db.py` |
| os 4 arquivos de arte | 8 | `instala_visual.py` |
| não existia no servidor | 5 | `db/guerra/item_db.yml` |
| entrada de `accessoryid` | 1 | `estende_accessoryid.py` |

As contas se sobrepõem: o **Sanctus** (420198) aparece em quatro linhas. As
outras 22 peças não custaram nada — o rAthena tinha, o cliente tinha em
português, e o `valida_visual.py` aprovou os 8 (ou 4) arquivos antes de
entrarem. A reconferência fechou em **0 faltando nos 47**.

### O ID pedido existia aqui com outro número, e a prova não foi o nome do recurso

A **Raposa Ilusional** foi pedida como **420227**, e o nosso vendor tem a mesma
peça no **420314**, `White_Fox_US` — "Calming White Fox", em inglês. As três
provas de que são o mesmo item, e a última é a que decide:

1. o `ClassNum` do 420227 no bRO é **2335**, que é o `View` do 420314;
2. o `identifiedResourceName` é `C_Friendly_White_Fox`;
3. os **quatro** conjuntos que a descrição do bRO lista para o 420227 são, um a
   um, os quatro `- Combos:` que `db/re/item_combos.yml` dá ao `White_Fox_US` —
   `Long_Mace_IL`, `Apple_Of_Archer_IL`, `Shoes_IL` e `Muffler_IL`.

Sozinho, o nome do recurso não provaria nada (`CLAUDE.md` §5, a armadilha dos
dois arcos de 2026-08-18); é a coincidência dos quatro conjuntos que fecha.

**Entrou o 420227**, e não o 420314, por uma razão só: o 420314 **não existe no
bRO**, então não há de onde tirar o nome em português, e só entra na loja item
com nome em português (regra 4.2). Os quatro conjuntos foram **espelhados** em
`db/guerra/item_combos.yml` — sem isso o item entraria com os quatro conjuntos
que a descrição promete mortos, e conjunto que não fecha não dá erro: o jogador
vê um número menor.

### A oitava leva de placeholders: dois de cabeça e três armas

As cinco que não existiam no servidor viraram entrada nossa em
`db/guerra/item_db.yml`, com os bônus lidos da descrição do bRO:

| id | item | o que é |
|---|---|---|
| 420227 | Raposa Ilusional | `Head_Low`, dano +20% contra a Ilusão da Lua |
| 420326 | Sistema Elyumina | `Head_Low`, taxa de drop +5% |
| 590041 | Mangual Ogro | Maça, ATQ 150, Mercadores |
| 510064 | Ninjaken | Adaga, ATQ 80 / ATQM 120, Ninjas |
| 550073 | Vara Morta | Cajado, ATQ 60 / ATQM 160, Arcebispos |

As **três armas** trazem *"Indestrutível em batalha"* na descrição e já
nasceram com `bonus bUnbreakableWeapon` — não dependeram do
`marca_indestrutiveis.py`, que só alcança item do vendor. Duas delas nem
precisariam: maça e cajado já são isentos no C++, e o script conta 241 armas
nessa condição. A adaga precisava.

Duas equivalências novas entraram no glossário do arquivo, as duas com
testemunha: *"Taxa de DROP +N%"* → `bonus2 bDropAddRace,RC_All,N` e
*"Efetividade de cura +N%"* → `bonus bHealPower,N`.

### O peso é o da tela vezes dez, e isso foi medido antes de escrever

Nenhuma das cinco tinha molde direto para o peso, então a escala foi conferida
em cinco testemunhas em que os dois lados são conhecidos: 19311 (tela 80 /
campo 800), 22171 (60 / 600), 490381 (10 / 100), 19137 (10 / 100) e 500005
(130 / 1300). Vale para arma e para armadura igual.

Isso **contradiz o cabeçalho da quinta leva**, que afirma o contrário para os
dois arcos de 2026-08-18 e os deixou dez vezes leves. Não foi corrigido nesta
sessão porque mexe em item que jogador já pode ter — está em `PENDENCIAS.md`
§1z7.

### O único que precisou das duas ferramentas de visual

O **Sanctus** (420198) tem `View 2351`, que não existe no `accessoryid.lub` de
2021: sem a entrada de tabela não há arquivo que o cliente vá procurar, e o
`instala_visual.py` sozinho não cura. Foi `estende_accessoryid.py` primeiro,
`instala_visual.py` depois — a mesma receita que o 400287 estreou em
2026-08-02. Os outros sete que faltavam arte eram só os 4 arquivos de item.

### As duas travas de sempre rodaram, e uma mediu 16 buracos

O `zera_revenda_das_lojas.py` achou **16 itens dando lucro por clique** entre os
46 novos — quinze a 9 zeny e a Mão do Demônio a 4 —, e o `Buy: 1` fechou os
1752 itens das 23 lojas. O `marca_indestrutiveis.py` regerou o override e o
Chapéu de Moranguinho (18853) já estava lá desde 2026-08-20.

### O quadragésimo sétimo não era capa, e foi para a loja de caixas

A **Caixa de Mantos Temporais (100100)** veio na lista sob *"Capas"*, e não é
capa nem equipamento nenhum: é `Usable` com `Flags: Container`, sem
`Locations:`, e o `Script:` inteiro dela é `getgroupitem(IG_TEMPORAL_MANTEAU_BOX)`.
Sem `Locations:` não há vitrine do quarteirão que a receba por regra (4.14) — o
mesmo impasse da Caixa de Cubos Refinadores (102592) de 2026-08-20, que ficou de
fora.

Desta vez o destino existia: o **Zé do Caixão** (`prontera 159,131`), a loja de
caixas e cubos criada naquele mesmo 2026-08-20. Foi decisão do dono, e ela é a
décima da vitrine.

O grupo dela são **seis capas de verdade** — `Garment` com DEF, refino e uma
cova, uma por atributo (20963 a 20968, FOR/AGI/VIT/INT/DES/SOR). As seis foram
conferidas antes de a caixa entrar, pela mesma regra que aquele arquivo já
aplicava aos 245 itens dos outros nove grupos: existem no `item_db`, têm nome em
português no `itemInfo.lua` deste cliente, e deram **24 de 24** no
`valida_visual.py`. Caixa que sorteia item sem arte entrega caixa de erro ao
jogador, e a falha só aparece na hora de abrir — longe de onde ela nasceu.

A alternativa considerada era pôr as **seis capas direto no Capeiro**, o que
dava o mesmo acervo sem o sorteio e cabia por regra. O dono escolheu a caixa.

Ela não declara `Buy` nem `Sell`, como as outras nove: o preço `1` **escrito** na
linha vale (e não `-1`, que viraria zero — `npc.cpp:4146`), e o lucro por clique
é zero. O `zera_revenda_das_lojas.py` foi de 1752 para 1753 itens.

### A subida não trouxe erro novo — e os três contadores que importam deram zero

Os quatro servidores locais subiram com o conteúdo novo. As três sondas que
denunciariam este trabalho deram **zero** no log da subida:

| o que procurar | denuncia | saiu |
|---|---|---|
| `Unknown syntax` | linha ruim no `.txt` — e ela mata o **arquivo inteiro** dali para baixo | 0 |
| `Invalid sell item` | item de vitrine que o `item_db` não conhece — a linha some da loja, calada | 0 |
| `discounted buying price` | revenda maior que a vitrine | 0 |

O log **não** está vazio de `[Error]`: saem **72**, e as três famílias são todas
anteriores a esta sessão. Conferido contra a subida de 2026-08-22, que tem as
mesmas famílias:

- **34** são `Job <X>_2nd is already in the alternate outfit list`, de
  `db/re/job_outfits.yml` — vieram com o estilo de corpo daquele dia. O número
  34 é exatamente a soma dos trabalhos dos treze blocos daquele arquivo, e as
  mensagens saem na mesma proporção por trabalho: **o arquivo é processado duas
  vezes**. Ficou registrado em `PENDENCIAS.md` §1z8;
- **2** são de `db/guerra/item_db.yml`, nos itens **26206** (`Blut_Whip`) e
  **510155** (`Ceuci`): *"Whips are always female-only"* e *"Musical instruments
  are always male-only"*, os dois com o rAthena corrigindo sozinho;
- os outros **36** são as linhas `Occurred in file` que acompanham cada um.

Nenhum toca a oitava leva — o `git diff` deste arquivo é um acréscimo puro a
partir da linha 2855, e as duas linhas citadas nos erros são 819 e 1176.

## A Anomalia Dimensional, e a descoberta de que se cura monstro (2026-08-26)

O pedido foi *"vamos implementar a Anomalia Dimensional, o evento que adiciona
Pets de MVP"*, com a página do bROWiki mandada em quatro capturas de tela — o
site devolve 403 para leitura automática, e as capturas trouxeram a página
inteira, inclusive a tabela de sorteio com as dez faixas de chance.

O evento é temporário no bRO (janeiro) e entrou aqui **permanente**.

### O que ele é

Fala-se com o **Sábio Varmunt** (`prontera 156,303`, nível 60+), ele abre uma
fenda, e do outro lado há uma cópia de Prontera com **quatro Pedras Guardiãs
morrendo**. As Pedras não se quebram e não revidam: elas precisam ser
**curadas**, com Curar, Curatio ou Santuário, enquanto Entidades Sombrias
nascem de dez em dez segundos e, raramente, um MVP atravessa junto — com
anúncio para o servidor inteiro. Curadas as quatro, Varmunt paga **7 Moedas de
Estimação**, uma vez por dia, com a virada às 4 da manhã.

As moedas compram giros na **Máquina Dimensional** (`prontera 165,304`), 10 por
giro, e é de lá que saem os ovos de pet. Ao lado está o **Manouro**
(`prontera 167,304`), que troca 30 Âmagos por um Ovo de Freeoni, 1 Âmago por um
ovo menor, e reabre a missão do dia por 2 Moedas Novas.

### A descoberta que fez o evento caber em script: curar monstro FUNCIONA

A mecânica central parecia exigir C++, porque a intuição de RO diz que Curar só
alcança jogador. Metade disso é verdade — a metade dos mortos-vivos.

Quem decide é o `SkillHeal::castendNoDamageId`
(`src/map/skills/acolyte/heal.cpp`, neste rAthena refatorado em que cada
habilidade tem classe própria). A função calcula o valor e a **única** coisa que
faz com alvo monstro é zerar a cura em três casos:

```cpp
if (status_isimmune(bl) || (dstmd && (status_get_class(bl) == MOBID_EMPERIUM ||
    status_get_class_(bl) == CLASS_BATTLEFIELD)))
        heal = 0;
```

e logo abaixo faz `status_heal(bl, heal, 0, 0)` com o `bl` que veio — monstro
inclusive. O `status_isimmune` (`status.cpp:9306`) só olha jogador (a Garra do
Golden Thief Bug) e `SC_HERMODE`, então para monstro devolve 0 sempre. O
Santuário segue o mesmo caminho noutro lugar: o `case UNT_SANCTUARY` do
`skill_unit_onplace_timer` (`skill.cpp:6923`) tem os **mesmos três testes** e o
mesmo `status_heal`.

Ou seja, as duas metades do pedido do bRO — "Curar, Curatio e Santuário" —
funcionam nativas, e **nenhuma linha de C++ nosso entrou neste evento**.

Achar isso custou uma escavação que vale registrar: o `grep` por `case AL_HEAL`
no `skill.cpp` devolve duas ocorrências, e **nenhuma delas é a cura** — uma é o
desvio para dano em morto-vivo, a outra é a validação de alvo. O corpo do heal
não está no `skill.cpp`: este vendor é a versão em que o `default:` do
`skill_castend_nodamage_id` chama `skill->impl->castendNoDamageId`, e cada
habilidade mora em `src/map/skills/<classe>/<nome>.cpp`. Quem procurar o
comportamento de uma habilidade no switch grande vai concluir que ele não
existe.

### Por que a Pedra é o Guardian Stone (1907)

Precisávamos de um monstro com cara de pedra que o cliente de 2021 desenhasse.
O 1907 (`S_EMPEL_1`) serve por quatro motivos somados:

1. o cliente o conhece — `JT_S_EMPEL_1 = 1907` no `npcidentity.lub`, com sprite
   `s_empel_1` presente no `data.grf`;
2. `Ai: 06`, que em `src/map/mob.hpp` é `MONSTER_TYPE_06 = 0` — **modos
   zerados**. Não anda, não ataca, não revida, não chama amigo. É uma pedra de
   verdade sem precisar de uma linha de script para isso;
3. **nenhum script do servidor o usa.** Os "1907" e "1908" que aparecem numa
   varredura por `npc/` são o item Guitarra, não o monstro — a Guerra do
   Emperium 2.0 não roda aqui;
4. ele passa nos três testes do `heal.cpp`: é `Element: Neutral` e
   `Race: Formless` (morto-vivo receberia **dano** em vez de cura), é
   `Class: Boss` e não `Battlefield`, e tem MDEF 50.

O HP sai de `setunitdata` no script, sem override de `db/`. **A ordem não é
livre:** `UMOB_MAXHP` atualiza o HP atual junto (está no exemplo do Poring em
`doc/script_commands.txt`), então o máximo vem antes e o HP baixo depois —
invertido, a Pedra nasce cheia e a rodada acaba no segundo em que começa.

### O mapa: `pprontera`, e a instância que foi descartada

No bRO a dimensão é uma cópia corrompida de Rachel, Lighthalzen ou Prontera,
conforme o dia. Aqueles três mapas são de 2024 e **não existem** neste cliente
de 2021-11-03 — e mapa sem `.rsw` no GRF derruba o cliente e ainda prende o
personagem lá (regra 6).

A saída foi a **`pprontera`**, e ela é boa demais para ser sorte: uma cópia de
Prontera que já mora no GRF, 312×392 igual à original, com os mesmos 1480
objetos e os mesmos modelos coreanos (muralha, torre do relógio, casas) —
conferido modelo a modelo com `ferramentas/rsw.py`. Já está no
`conf/maps_athena.conf`, já está no `db/map_cache.dat`, e tem **zero NPC**:
nenhuma linha de `npc/` a menciona. Uma Prontera inteira e vazia, de graça.

Ela já era conhecida do projeto pelo lado errado: o `CLAUDE.md` §5 a cita como
a armadilha de quem lê o `map_cache` grande e recebe a `pprontera` achando que
é a cidade. Desta vez ela era exatamente o que se queria.

**Instância foi descartada por uma linha do rAthena:** o `instance_addnpc`
(`instance.cpp:590`) faz `map_foreachinallarea(..., BL_NPC, ...)`, ou seja
**clona todos os NPCs do mapa-molde**. Instanciar a nossa Prontera clonaria as
22 lojas e as Kafras, por party. Com a `pprontera` vazia até seria viável, mas
aí o evento perderia o que tem de melhor — várias pessoas curando a mesma pedra
e o broadcast de MVP para o servidor inteiro.

**O rodízio do bRO foi mantido mudando de eixo:** lá trocava o mapa por dia da
semana, aqui trocam as **quatro posições das Pedras** dentro da mesma Prontera —
três conjuntos, exatamente como os três minimapas da página do bRO mostram três
arranjos diferentes. As doze células saíram de uma varredura do `map_cache`:
andáveis, com raio 3 livre em volta e a pelo menos 90 células umas das outras.

### O céu roxo é mudança de CLIENTE

O dono pediu que a `pprontera` não fosse a Prontera de sempre: *"uma cópia de
prontera assim como era no bRO, com a coloração parecida com o que era"*. Isso
virou `ferramentas/tinge_dimensao.py`, que troca os **24 bytes de luz** do
`.rsw` — difusa de (1,00/1,00/1,00) para (1,00/0,55/0,80) e ambiente de
(0,55/0,50/0,50) para (0,62/0,30/0,68). Luz direta rosada, sombra roxa.

Sem textura nova, sem modelo novo e sem tocar o `.gnd` (3,3 MB, que pesaria no
patch): a luz multiplica tudo que é desenhado ali, então o mapa inteiro muda de
clima de uma vez. O arquivo gravado tem **exatamente o mesmo tamanho** do
original e 16 bytes diferentes.

**E isso põe o evento nos dois destinos do `RECEITAS.md` §0 ao mesmo tempo:** o
servidor vai por deploy, e o `cliente\data\pprontera.rsw` vai por **patch**.
Quem não receber o patch joga a Anomalia inteira, sem erro nenhum, numa Prontera
de cor normal — falha calada e só cosmética, mas é a diferença entre "uma fenda
dimensional" e "a cidade de sempre com pedras no chão".

### O que já existia, e foi a melhor notícia do dia

O levantamento antes de escrever uma linha achou o evento quase todo pronto no
vendor e no cliente:

| peça | estado |
|---|---|
| Moeda de Estimação (25376), Âmago Dimensional (7925), Ração Luxuosa (25377) | existiam, com nome PT |
| os 23 ovos, as 14 iscas e as 15 comidas da tabela | **29 de 29** resolvidos por nome, sem homônimo |
| os 15 itens no `itemInfo.lua` do cliente | **15 de 15** — nenhum item precisou de entrada nova |
| os 23 pets no `petinfo.lub` do cliente | todos, com sprite, ilustração e comida |
| Gibbet 1503, Dullahan 1504, Loli Ruri 1505 | existiam |
| "Serial Killer" | é o **Bloody Murderer (1507)** — o nome PT saiu do nosso `mob_db.yml`, gerado do `navi_mob_br.lub` do bRO |

### O Freeoni: o que faltava era só o servidor

O prêmio máximo estava **comentado em dois lugares do vendor ao mesmo tempo**: o
mob `PHREEONI2` (Id 20425) no `db/re/mob_db.yml`, só com o esqueleto `Id` +
`AegisName`, e a entrada de pet correspondente no `db/re/pet_db.yml` — 44 pets
estão assim. Um depende do outro: o `pet_db` resolve o pet por AegisName, e
AegisName que não existe faz o `parseBodyNode` descartar a entrada inteira.

O que decidiu usar o 20425 em vez de inventar outro Id é que **o cliente já
sabia tudo sobre ele**:

```
npcidentity.lub   JT_PHREEONI2 = 20425
jobname.lub       20425 -> sprite `phreeoni`
data.grf          data\sprite\<monstro>\phreeoni2.spr e .act, e o ovo
petinfo.lub       PetEggItemID_PetJobID[9111] = JT_PHREEONI2
                  PetFoodTable = 25377 (Ração Luxuosa)
                  PetIllustNameTable = 'pet_phreeoni.bmp' (existe no GRF)
```

A metade de cliente do Freeoni estava inteira desde 2021 e só o servidor
faltava. Trocar o Id quebraria as cinco tabelas de uma vez, e a falha seria a
calada de sempre (§4.9).

Os status do mob vieram do **PHREEONI (1159)** campo a campo, sem `Modes: Mvp`,
sem os `MvpDrops`, sem os `Drops` e sem EXP — o vendor não diz quais são os do
20425, e o único número honesto disponível é o do monstro que ele copia
(regra 3). O que não se pode herdar é a premiação: um mob que só existe para ser
bicho de estimação não pode valer 63.800 de base por `@monster`.

O `db/guerra/pet_db.yml` é o primeiro pet nosso, e entrou por **uma linha** no
rodapé de `db/pet_db.yml` — aquele rodapé já existia, então não foi preciso
criar `Footer:` como no `quest_db` e no `job_stats`.

### A tabela de sorteio, e o ×50 que não cabia

O dono pediu para **multiplicar as chances por 50**, com o exemplo do Freeoni:
de 0,006664% para 0,3332%, *"1 para 333"*.

Multiplicar a tabela **inteira** por 50 é impossível: os ovos somam 5,52% no
bRO, e ×50 dá **276%**. Então o fator decresce conforme o prêmio fica comum —
×50 no Freeoni, ×10 no Gato de Nove Caudas, ×5 nos nove raros, ×4 nos doze
comuns — e o espaço sai das comidas de pet, que continuam sendo a maior parte da
tabela. A chance de sair **algum** ovo passou de 5,52% para **24,32%**.

Os pesos estão em milionésimos e somam **1.000.000 exatos**. O `OnInit` da
Máquina confere isso sozinho e grita com `debugmes` se a soma mudar ou se as
três colunas paralelas ficarem desalinhadas — a regra §4.11, que existe porque
coluna desalinhada não dá erro: entrega o prêmio errado, calada.

### O reset das 4h sem quest, de propósito

O caminho óbvio para "repete após as 4 da manhã" seria uma quest com
`TimeLimit: 4h` — o `CLAUDE.md` §5 até registra que a forma sem `+` devolve o
próximo 04:00. **Não foi usado**, e a razão é o custo do outro lado: quest nova
exige entrada na tabela do cliente, e quest que o cliente não conhece **derruba
o cliente**, uma caixa por missão e por atualização da janela. Custou um bug em
2026-08-08 nas placas da Ordem. Um temporizador de evento não vale esse risco.

O que se usa é um "dia lógico" calculado na função `AnomaliaDia`, guardado na
variável permanente `anomalia_dia`. A conta **não tem constante de fuso**: ela
descobre o deslocamento comparando a hora local que o servidor dá
(`gettime(DT_HOUR)`, `America/Sao_Paulo` desde 2026-08-16) com a hora UTC
derivada do `gettimetick(2)`, e só então corta o dia às 4h. Se o horário de
verão voltar, ela acompanha sozinha.

### Duas falhas caladas que a leitura do doc pegou antes de irem para o jogo

- **`mobcount("mapa","all")` não conta nada.** O `mobcount` conta monstros que
  tenham *aquele* label; o especial de "todos" é a **string vazia**, que conta os
  sem label — que é o caso dos nossos. Com `"all"` ele procuraria um label
  chamado `all`, acharia zero, e o teto de monstros nunca pegaria: o mapa
  entupiria em silêncio.
- **`killmonster "mapa","all"` não mata nada.** O buildin compara
  `strcmp(event,"All")` — maiúsculo e exato (`script.cpp:11486`). Trocado por
  `killmonsterall`, que não tem como errar a capitalização.

E uma terceira, do próprio rAthena: **`callsub` não abre escopo novo** — ele
enxerga e sobrescreve as `.@` de quem chamou (só o `callfunc` isola). O
subprograma que planta a Pedra usa `.@pn`/`.@php`/`.@pk` com prefixo por causa
disso; um `.@hp` ali dentro apagaria o `.@hp` do laço que mede as Pedras.

### O que ficou como número a calibrar

O HP de cada Pedra (**50.000**, começando em 1.000) e a chance de MVP por onda
(**2%**) são escolha nossa — o bRO não publica nenhum dos dois, e o wiki diz
literalmente que a chance de MVP é *"desconhecida e bem baixa"*. Os dois estão
em constante nomeada no `OnInit`, num arquivo só.

E a conta da economia, que o dono vai querer ver com o evento rodando: a missão
paga 7 moedas por dia, o giro custa 10, e a tabela devolve em média 4,14 por
giro — custo líquido de 5,86, ou **1,19 giros por dia** para quem só faz a
diária. Com o Freeoni a 1 em 300, isso dá cerca de **250 dias** de missão pura.
É o prêmio máximo e tem dois atalhos (o reset pago e os 30 Âmagos do Manouro),
mas o número está aqui para quando a calibragem for revista.

### O primeiro teste em jogo, no mesmo dia: o rosa-choque e o relog

O dono entrou na dimensão poucas horas depois, e a captura de tela respondeu de
graça três coisas que estavam em `PENDENCIAS.md` esperando o jogo: o Varmunt de
Prontera **teleporta**, a `pprontera` **abre** sem derrubar o cliente, e a
rodada **começa sozinha** — o `mapannounce` *"A fenda se abre. Quatro Pedras
Guardiãs pedem socorro."* saiu no topo da tela e no chat.

Duas coisas vieram junto, e as duas foram corrigidas na mesma sessão.

**1. A cor estava magenta, não roxa.** O preset da estreia era difusa
`(1,00 / 0,55 / 0,80)` e ambiente `(0,62 / 0,30 / 0,68)` — derrubar o verde e
**subir** o azul. Isso não é roxo: é **rosa-choque**, e a cidade inteira ficou
pink. O pedido de correção veio com uma escala: *"levemente avermelhado,
alaranjado, mas mais suave — intensidade 3 numa escala de 1 a 10"*.

A regra que faltava é de uma linha, e vale para qualquer tingimento futuro:
**verde baixo + azul alto = rosa; azul baixo = laranja.** Vermelho intacto e
azul derrubado é o que produz o tom quente de fim de tarde.

E a lição de desenho: **o `tinge_dimensao.py` pedia seis floats, e seis floats
não são calibráveis por quem não decorou a regra acima.** Ele passou a ter
`--intensidade`, de 0 a 10, que mistura a luz de fábrica com um alvo quente
único — 0 devolve a Prontera normal, 10 entrega o alvo puro. Assim a cor nunca
"vira outra coisa" no meio do caminho: só fica mais forte ou mais fraca na mesma
direção. Rodar sem argumento imprime a escala inteira, para escolher olhando.
O valor em uso é **3**: difusa `(1,000 / 0,916 / 0,835)`, ambiente
`(0,601 / 0,476 / 0,440)`.

**2. Ninguém pode morar na dimensão.** Pedido do dono na sequência: quem
deslogar lá dentro tem de relogar em Prontera. Resolvido com três mapflags no
próprio arquivo do evento:

```
pprontera	mapflag	nosave	prontera,156,300
pprontera	mapflag	nomemo
pprontera	mapflag	nobranch
```

O `nosave` com ponto explícito é lido no `pc.cpp:2001`, e o comentário do
próprio rAthena ali entrega o detalhe que importa — *"Maybe since the player's
logout the nosave mapflag was added to the map"*: **a troca acontece no LOGIN, e
não na hora de deslogar.** Duas consequências boas: isso resgata também quem já
estava preso lá dentro de antes da linha existir, sem tocar no banco; e o
personagem nunca chega a ter `pprontera` como ponto de retorno, então morrer
também não o traz de volta para lá.

Os outros dois são a mesma intenção: `nomemo` impede memorizar a dimensão com o
Portal (entrar sem passar pelo Varmunt) e `nobranch` impede Galho Seco — um mapa
que já invoca MVP sozinho não precisa de ajuda. **`noreturn` foi deixado de fora
de propósito:** ele bloquearia a Asa de Borboleta, que é justamente como se sai
de lá.

**A prova de que as três linhas foram aceitas é indireta e sólida:** elas estão
nas linhas 210-212 do arquivo, e a sonda `ANOMALIA: Maquina Dimensional pronta`
vem do `OnInit` da linha 587. Linha inválida faz o `npc_parsesrcfile` parar e
**abandonar o resto do arquivo** (`CLAUDE.md` §5) — se os mapflags tivessem
falhado, a sonda não teria saído.

### O mapa vazio, e a promessa que ninguém tinha escrito (2026-08-26, noite)

O segundo teste em jogo veio com uma pergunta que era um diagnóstico: *"falo com
o NPC, ele diz que existe uma pedra marcada no mini-mapa, mas não tem nada, e
nada aparece no mapa. O mapa fica vazio, é isso mesmo?"*

Não era. Eram **dois defeitos empilhados**, e o primeiro é da família mais cara
do projeto.

**1. A fala prometia uma marcação que não existia.** O Varmunt dizia *"As Pedras
estão marcadas no seu mini-mapa pelo brilho que ainda lhes resta"* — e não havia
uma linha de código que marcasse coisa alguma. É a **§4.17 pega no ato**, e da
pior maneira: não é um cabeçalho descrevendo regra que ninguém escreveu, é o
**próprio NPC dizendo ao jogador** o que o servidor não faz. Escrito por mim, no
mesmo dia, sem que nada denunciasse — nem no boot, nem no log.

O conserto é o `viewpoint`, que existia o tempo todo: `viewpoint 1,<x>,<y>,<n>,
<cor>` marca no mini-mapa de quem está anexado. Entrou em três lugares, e são
três porque o RID muda em cada um:

- ao falar com o Varmunt e aceitar (`callsub S_Marca`, tem jogador anexado);
- ao **entrar** na dimensão, via `OnPCLoadMapEvent` — que exigiu o mapflag
  `loadevent`, sem o qual aquele label simplesmente nunca dispara;
- ao **começar** a rodada, e aí é `viewpointmap` e não `viewpoint`: o
  `OnComecaRodada` roda pelo temporizador, **sem RID nenhum**, e o `viewpoint`
  comum precisa de um. Sem essa terceira, quem entrasse *antes* da rodada
  começar ficaria sem marca até falar com o Varmunt de novo.

**2. As Pedras estavam longe demais para serem achadas.** O arranjo original
espalhava as quatro pela Prontera inteira — até **200 células** do ponto de
chegada — num rodízio de três conjuntos por dia da semana, imitando os três
minimapas da página do bRO. No papel era fidelidade; em jogo era um mapa vazio
em todas as direções.

Decisão do dono: **as quatro ficam sempre em volta do centro.** O rodízio caiu
inteiro. As posições novas são fixas, uma por quadrante, a 16-17 células do
Varmunt:

```
    SO 145,179      SE 167,179
             (156,190)
    NO 143,201      NE 168,201
```

Escolhidas pela varredura do `map_cache` como as mais próximas de um quadrado
simétrico ideal que tivessem **raio 2 livre** em volta. A cruz perfeita não
serve: `156,205`, ao norte, esbarra na fonte da praça.

A lição, que vale além deste evento: **variedade que ninguém acha não é
variedade.** O rodízio custava zero para implementar e custou uma ida ao jogo
para descobrir que tornava o evento injogável.

### Duas correções finas na mesma rodada

**O sprite do Varmunt virou o 654 (`4_M_BARMUND`)** — nos dois, o de Prontera e
o da dimensão, porque são o mesmo personagem. O 755 (`4_M_SAGE_C`) era palpite
meu, escolhido por ser "um sábio"; o `BARMUND` é o sprite do próprio NPC no kRO,
e o nome quase idêntico ao do personagem é o que o entrega. Conferido no cliente
antes: `JT_4_M_BARMUND = 654` no `npcidentity.lub`, com o sprite presente no GRF.

**O Mensageiro Continental mudou de esquina.** O `Continental Messenger#01` do
rAthena mora em `prontera 164,304`, e a Máquina Dimensional nasceu em `165,304`
— uma célula ao lado. Pior: aquele NPC tem **área de toque `3,3`**, um quadrado
de 7×7 que cobria a Máquina e o Manouro inteiros, jogando um diálogo por cima de
quem fosse girar a Máquina. Foi para `150,306`, com a área junto.

**O `movenpc` não serviria, e é uma armadilha que vale guardar:** ele faz
`map_moveblock` e mais nada (`npc.cpp:5046`) — não chama `npc_unsetcells` nem
`npc_setcells`. E a área de toque **não mora no NPC, mora no mapa**: o
`npc_setcells` (`npc.cpp:4971`) marca `CELL_NPC` célula por célula no
carregamento. Com `movenpc` o boneco andaria e o gatilho ficaria em `164,304` —
a fala continuaria disparando em cima da Máquina e não dispararia no lugar novo.
Silencioso e exatamente ao contrário do pedido.

Foi então a receita da §2 (`disablenpc` + duplicata nossa), com uma sutileza que
quase mordeu: o script daquele NPC descobre a cidade lendo o **próprio nome**,
com `set .@area$,strnpcinfo(2)` e um `if (.@area$ == "01")`. O sufixo `#01` não
é enfeite, é o dado — uma duplicata chamada `#01b` faria o NPC anunciar "01b"
como se fosse o nome da cidade. O que salva é que `strnpcinfo(2)` lê o
`nd->name` (`script.cpp:9276`) enquanto o nome único é o `nd->exname`, que é o
`strnpcinfo(3)`: campos diferentes. Então a duplicata mantém `#01` na parte
visível e ganha nome próprio depois do `::`.

Os dois blocos ficaram **no arquivo do evento**, e de propósito: foi o evento que
empurrou o Mensageiro, e desligar o evento devolve o Mensageiro ao lugar sozinho,
porque o `disablenpc` que o esconde mora ali.

**A prova de que os dois nasceram é uma contagem:** o boot passou de **24168
para 24170 NPCs**, exatamente os dois acrescentados, sem um único
`npc_parsename` (nome único repetido) e sem *"Attempted to disablenpc a
non-existing NPC"*.

### "Curava, mas eu não tive feedback" — a mecânica invisível (2026-08-26)

O terceiro teste em jogo trouxe o relato mais útil de todos, em três frases:
*"eu consegui curar, mas fiquei curando muito e não dava nada"*, *"curava, com
um valor, mas eu não tive feedback"*, *"então não sabia se algum dia ia parar"*.

Nada estava quebrado. **A mecânica funcionava e era invisível** — que é uma
falha pior do que não funcionar, porque não deixa rastro nenhum para diagnosticar.

**O cliente de RO não desenha barra de vida de monstro.** Essa frase é o defeito
inteiro. Curar uma Pedra e não curar produziam exatamente a mesma tela: o número
verde subia (isso o cliente mostra) e nada mais acontecia. O jogador não tinha
como saber se faltava um lançamento ou cinquenta, nem se o evento estava de pé.
Toda a leitura de código que provou que `status_heal` alcança monstro não serviu
de nada para quem estava lá dentro.

**E o número estava errado por cima disso.** As Pedras estrearam com 50.000 de
HP cada, escolhido supondo que um Curar entregasse uns 2.000. A fórmula
(`skill.cpp:552`) diz outra coisa:

```
hp = ((nivel + INT) / 8) * (4 + nivel_da_magia * 8)
```

Num personagem de nível 200 com INT 200 isso dá `(400/8) * 84` ≈ **4.200 por
lançamento** — mas mesmo assim 50.000 por Pedra eram uns 12 lançamentos em cada
uma e **48 na rodada inteira**, para uma pessoa só. Passou para **15.000**: ~4
por Pedra, ~16 na rodada, e cai proporcionalmente com mais gente curando.

### O que entrou como retorno, em três camadas

Nenhuma delas é enfeite — cada uma responde uma pergunta diferente:

1. **A Pedra fala.** Sempre que o HP dela sobe, ela anuncia a própria
   porcentagem (`unittalk`) e solta um `EF_HEAL`. Responde *"minha magia está
   entrando?"* na hora, e no lugar onde o jogador está olhando. Um balão por
   segundo no máximo, e só quando há progresso de verdade.
2. **O aviso do conjunto passou de 25% para 10%.** O balão diz como vai **uma**
   Pedra; o `mapannounce` diz como vai a **rodada**. Responde *"estou perto do
   fim?"*.
3. **O Varmunt ganhou "Como estão as quatro?"**, que lista as quatro com HP,
   máximo e porcentagem, mais o total. É a barra de vida que o cliente não
   desenha, e a fala termina dizendo o que fazer se o número não subir: *"é
   porque a magia não é de cura — ou não está alcançando a Pedra"*.

E uma quarta camada, essa para nós: um `debugmes` de dez em dez segundos com os
quatro HPs, no console do map-server. Existe porque a pergunta que importa nesta
mecânica não tinha resposta na tela **nem no log** — e é `debugmes` e não
`ShowInfo` de propósito, porque informação não tem bit no `console_msg_log` 3 e
não chegaria ao arquivo (`CLAUDE.md` §5).

**A lição, que é maior que este evento:** ao construir mecânica em cima de um
número que o cliente não mostra — HP de monstro, contador interno, progresso de
qualquer coisa —, o retorno visual **faz parte da mecânica**, não é acabamento.
Sem ele o jogador não consegue nem relatar o defeito direito, e do lado de cá
tudo parece funcionando.

### A cor, terceira e última versão

O laranja 3/10 do ajuste anterior ficou *"muito suave"*. Pedido: mais roxo, 4/10.

A regra que faltava, e que resume as três tentativas: **quem manda no matiz é a
posição relativa de verde e azul.** `B > G` puxa para o roxo/rosa; `B < G` puxa
para o laranja; a distância entre os dois diz o quanto disso aparece.

| tentativa | difusa | G − B | resultado |
|---|---|---|---|
| 1ª | 1,000 / 0,550 / 0,800 | −0,250 | magenta, rosa-choque |
| 2ª (3/10) | 1,000 / 0,916 / 0,835 | +0,081 | laranja limpo, suave demais |
| 3ª (4/10) | 1,000 / 0,832 / 0,896 | −0,064 | roxo avermelhado |

O alvo da escala mudou para `(1,00 / 0,58 / 0,74)` — o **verde** é quem cai
mais, não o azul — e a intensidade padrão subiu para 4.

### "A cura não está pegando" — e estava. O leitor é que lia zero (2026-08-26)

O relato veio com duas capturas e uma suspeita bem formulada: *"eu curo e a
estatística não muda. Minha suspeita procede, a cura não está pegando mesmo
aparecendo que curou."*

A suspeita **procedia como sintoma e apontava para o lugar errado**, e as
capturas continham a resposta:

- na primeira, a Pedra Guardiã em pé, com números **verdes** de cura subindo
  sobre ela — ou seja, `clif_skill_nodamage` com `heal > 0`;
- na segunda, o painel novo do Varmunt dizendo **`0% (0 de 15000)` nas quatro**.

Curando e lendo zero ao mesmo tempo. Se a cura não entrasse, o número verde não
sairia; se entrasse, o painel não leria zero. Um dos dois lados estava mentindo,
e o único jeito de saber qual era olhar a janela do map-server:

```
[Warning]: buildin_getunitdata: Error in argument! Please give a variable to store values in.
[Warning]: Script command 'getunitdata' returned failure.
```

**`getunitdata` não é função — é comando que preenche um array.** A forma certa
é `getunitdata <GID>,<array>;`, com os índices sendo as próprias constantes
(`.@dados[UMOB_HP]`). Eu havia escrito `.@hp = getunitdata(gid, UMOB_HP)`, que
é o reflexo natural justamente porque o **`setunitdata` irmão tem três
argumentos** e parece autorizar a leitura simétrica. Escrito assim ele devolve
**sempre zero**.

**A cura sempre funcionou.** O `SkillHeal`, o elemento do mob, o `damagetaken`,
a guarda dos três casos — tudo aquilo que foi lido e reconferido estava certo o
tempo todo. O defeito eram duas linhas de leitura, uma no `OnTimer1000` e outra
no painel do NPC.

O que torna esse erro caro é a combinação de três coisas: o aviso sai **só na
janela** (o `console_msg_log` 3 não manda informação para o arquivo), o zero é
um valor **plausível** para quase toda pergunta que se faça a uma unidade, e o
sintoma resultante — "curo e nada acontece" — descreve com perfeição um bug de
mecânica que não existia. Foram três hipóteses investigadas no lugar errado
antes de alguém olhar o console.

Corrigido nos dois lugares. O painel passou a ler também o **`UMOB_MAXHP` do
próprio monstro** em vez da nossa constante — assim ele prova, de quebra, que o
`setunitdata` do plantio pegou: se aparecer `120500` ali, o HP base do 1907
voltou a valer.

**A regra que sobra, e virou entrada da §5:** quando um valor lido vier zero de
forma suspeita, desconfiar **do leitor antes do fenômeno**. É a mesma família do
"tabela com 1 entrada é sintoma de chave não resolvida" — o número plausível é
justamente o que impede de ver o defeito.

E a ironia útil: o painel "Como estão as quatro?", que existia havia uma hora
para dar feedback ao jogador, foi o que **entregou o bug** — não pelo que
mostrava, mas por mostrar um número que não podia ser verdade.

### A Pedra que nascia cheia: underflow no `status_set_maxhp` (2026-08-26)

Corrigida a leitura, o evento passou a se comportar de um jeito novo e pior: a
rodada abria e **fechava no mesmo segundo**, em laço, com o chat alternando *"A
fenda se abre"* e *"A luz voltou por inteiro!"*. O dono descreveu com precisão e
já ofereceu as duas hipóteses certas: *"ou é resquício de cura das minhas
interações passadas que não foram contadas, ou a instância se auto-encerra"*.

Era uma terceira: **as Pedras nasciam com o HP cheio.**

Desta vez não houve teoria. Um NPC de teste temporário plantou um 1907 no boot e
leu o HP de volta depois de cada `setunitdata`, imprimindo tudo no console:

| passo | resultado |
|---|---|
| só `monster` | `120500/120500` |
| após `UMOB_MAXHP 15000` | **`2147604147`**/15000 |
| após `UMOB_HP 1000` | `120500`/15000 |
| `UMOB_HP 1000` **primeiro** | `1000/120500` |
| `UMOB_MAXHP 15000` depois | `15000/15000` |
| `UMOB_HP 1000` de novo | **`1000/15000`** |

O `2147604147` entregou a causa. O `status_set_maxhp` (`status.cpp:1343`) faz:

```c
heal = maxhp - status->max_hp;   // os dois lados sao uint32
...
if (heal > 0) status_heal(...); else status_zap(...);
```

**Reduzir o máximo dá underflow**: `15000 - 120500` em `uint32` vira um número
enorme e positivo, o `if (heal > 0)` acerta, e o servidor **cura** em vez de
reduzir. O HP estoura no teto de `int32` e, dali em diante, nenhum `UMOB_HP`
consegue trazê-lo de volta.

A saída é nunca deixar o HP acima do máximo novo na hora da troca — **três
chamadas**: baixa o HP (ainda dentro do máximo velho), troca o máximo (o
underflow ainda ocorre, mas o `status_heal` que ele dispara é limitado ao máximo
recém-gravado, então o HP para nele), baixa o HP de novo. Validado no mesmo NPC
de teste antes de entrar no evento: `1000/15000`.

**E o comentário do arquivo dizia exatamente o contrário** — *"o MaxHP vem
primeiro e o HP baixo depois; invertido, a pedra nasce cheia"* —, escrito por mim
no mesmo dia com base no exemplo do Poring do `doc/script_commands.txt`, que é
verdadeiro só quando o máximo **aumenta**. Era a §4.17 de novo, agora num
comentário que descrevia a ordem errada com toda a confiança. Corrigido junto.

### Duas coisas que caíram na mesma rodada

**A trava de participação saiu.** Havia um `@anomalia_rodada != .rodada_num` que
respondia *"você chegou depois do trabalho feito"* a quem não tivesse escolhido
"Quero ajudar" no menu — e o dono levou essa recusa tendo acabado de curar. Era
injusta em dois casos comuns: quem já estava no mapa quando a rodada começou (não
passa pelo menu) e quem cura sem falar com o Varmunt antes. Quem está falando com
ele está dentro da dimensão, e a janela de pagamento dura 30 segundos; **o que
protege a economia é o reset diário**, que vale por personagem e por dia. A
variável foi removida inteira, sem deixar escrita órfã.

**O `.PedraHpMax` foi de 50.000 para 15.000** — ~4 lançamentos de cura por Pedra
e ~16 na rodada, para uma pessoa só (a fórmula de `skill.cpp:552` dá ~4.200 por
lançamento num personagem de nível 200 com INT 200).

### O método, que é a parte reaproveitável

Três defeitos seguidos neste evento — a leitura que devolvia zero, a marcação de
mini-mapa que não existia, e agora o HP corrompido — e os três foram resolvidos
do mesmo jeito: **parar de deduzir e instrumentar**. O que decidiu aqui foi um
NPC descartável que fazia o plantio no boot e imprimia o estado depois de cada
passo; ele custou dez minutos e respondeu o que a leitura de `status_set_maxhp`
sozinha não tinha respondido (eu havia lido aquela função **antes**, e o
underflow não salta aos olhos).

Ficou no evento uma versão permanente disso: o `S_Planta` lê o HP de volta logo
depois de plantar e imprime `pedi hp=N -> ficou X/Y`. Se algum dia o número
divergir, aparece de graça na primeira rodada.

### O acabamento, e o painel que se tornou desnecessário (2026-08-26)

Com o underflow corrigido o evento rodou inteiro e foi aprovado: *"agora deu
certo! ficou ótimo!"*. Três ajustes finos vieram junto.

**O painel "Como estão as quatro?" saiu do NPC.** Ele tinha nascido como muleta
para um problema que deixou de existir: enquanto não havia retorno nenhum, era o
único jeito de o jogador saber se a cura entrava. Depois que a Pedra passou a
anunciar a própria porcentagem e o conjunto a avisar de 10 em 10%, o painel
virou uma opção de menu que ninguém precisaria abrir. Saiu inteiro, e com ele o
array `.Canto$` — que existia só para rotular aquelas quatro linhas e viraria
código morto. A conferência de colunas paralelas do `OnInit` ficou, agora
comparando `.px` e `.py` entre si.

Vale registrar a ordem em que isso aconteceu, porque ela é o oposto do
desperdício que parece: **o painel foi o que entregou o bug do `getunitdata`** —
não pelo que mostrava, mas por mostrar `0 de 15000`, um número que não podia ser
verdade. Ele cumpriu duas funções (sonda de diagnóstico e muleta de feedback) e
saiu quando as duas deixaram de ser necessárias.

**Receber as moedas devolve o jogador a Prontera.** Fecha o ciclo no lugar
certo: as moedas só servem na Máquina Dimensional, que fica a doze células do
ponto de chegada, e ninguém tem o que fazer na dimensão depois de receber. É
`close2` e não `close` — o `close` devolve o controle e encerra o script ali, e
o `warp` nunca rodaria.

**A cor foi para 6/10**, mesmo alvo roxo avermelhado da rodada anterior. Como a
escala mistura sempre na mesma direção, subir a intensidade **não muda o matiz**
— só a distância até a luz de fábrica. Foi exatamente para isso que ela existe:
depois de três tentativas em que a cor "virava outra coisa" a cada ajuste, as
duas últimas calibragens foram um dígito cada.

### Calibragem e embelezamento, com a mecânica fechada (2026-08-26)

*"AGORA SIM! mecânica fechada!"* — e então os números de verdade. Três pedidos.

**Três vezes mais Entidades por onda, mantendo a cadência.** O pedido veio com a
instrução exata (*"manter a cadência, apenas aumentar a quantidade por spawn"*),
que separa os dois botões: a quantidade mudou de 2 para **6** no `areamonster`, e
o intervalo de dez segundos do `OnTimer1000` ficou onde estava. Mexer no errado
faria as Entidades chegarem em rajadas curtas em vez de em maior número.

**E o teto subiu junto, sem ter sido pedido** — de 60 para 180. Não é escopo
esticado: mantido em 60, o teto seria alcançado em dez ondas e as Entidades
parariam de nascer, ou seja **o triplo pedido não apareceria em jogo**. É o teto,
e não a quantidade por onda, o botão a mexer se o mapa pesar; ficou escrito no
próprio arquivo.

**Quatro vezes mais HP nas Pedras**, de 15.000 para **60.000** cada — de ~4
lançamentos de cura por Pedra para ~14, e de ~16 para ~57 na rodada inteira,
para uma pessoa só. É a passagem de "provar que funciona" para "dar trabalho", e
escala para baixo sozinha quando há mais de um curandeiro.

**Brilhos sob o Varmunt, e o caminho que não era o óbvio.** O pedido nomeou a
arte: `effect\mineffect\new_epiclesis\epi_glow_01.bmp`. Não dá para pedir isso
por `specialeffect` — o brilho de Epiclesis não é um efeito numerado do cliente,
é uma **unidade de habilidade** (`UNT_EPICLESIS`) que só existe enquanto a magia
está no chão; não há `EF_` para ele no rAthena.

O que existe é melhor: o cliente tem um sistema de **emissores de partículas por
mapa**, em `data\luafiles514\lua files\effecttool\<mapa>.lub`, que aceita **o
caminho da textura direto**. É o que faz a fumaça sair das chaminés de Prontera —
três emissores com `effect\smoke1.bmp`, que estavam ali o tempo todo. Virou
`ferramentas/planta_brilho.py`.

A parte que erra calado é a conversão de célula para mundo, e ela foi **derivada
de um caso já conferido em tela**, não chutada: o cabeçalho do `edita_mapa.py`
registra que a fonte do Centro da Ordem, em `auction_01` (200×100), tem centro em
"mundo (400, 110)". Daí saem as duas fórmulas — `célula×5 − (lado/2)×5` nos dois
eixos — e o fato de que **o Z não é invertido**. O Varmunt, em `prontera 156,303`
de um mapa 312×392 com terreno na altura 1,0, cai em mundo `(2,5, −1,5, 537,5)`;
a sanidade é que os emissores de fumaça existentes ficam em z 27–54, o que dá
células y≈202–207, as casas ao norte da praça.

O `.lub` é bytecode Lua 5.1 e tem só duas globais, sem função nenhuma — por isso
regerar é seguro. A ferramenta lê a base **sempre do GRF** (nunca do próprio
override, que faria a receita apontar para si mesma), acrescenta o emissor,
compila com o `luac` do ROenglishRE e **relê o arquivo gravado** para conferir
que o novo está lá: `3 -> 4 emissores`, o nosso no índice 3.

**Isto é cliente e vai por patch** — junto com a cor, que na mesma rodada foi
para **6/10**, mesmo alvo roxo. Como a escala mistura sempre na mesma direção,
subir a intensidade não muda o matiz, só a distância até a luz de fábrica.

O que os números do emissor (`size`, `color`, `rate`, `life`) têm de frágil é o
de sempre: foram escolhidos para um halo parado — sem gravidade, sem velocidade,
mistura aditiva — e **só a tela diz se estão bons**. Estão todos em
`_emissor_nosso()`, num lugar só.

### O brilho que não apareceu, e o que foi eliminado (2026-08-26)

Primeira ida ao jogo com o emissor instalado: **nada**. O relato veio com a
captura e a pergunta certa — *"sem brilho. O que houve? não conseguimos?"*.

Ainda não há resposta, e vale registrar o que **já foi eliminado**, para a
próxima tentativa não refazer o caminho:

- **a textura existe** no GRF, nos dois caminhos, e a ferramenta recusa aplicar
  se não estiver;
- **o caminho do arquivo é único**: só há `data\luafiles514\lua files\
  effecttool\` no GRF — não é o caso do `petinfo.lub`, que tem dois;
- **o arquivo gerado é válido**: passa no `luac -p` e, relido pelo mesmo parser
  que lê os `.lub` do GRF, entrega os quatro emissores com a textura e a posição
  certas;
- **o carimbo de acesso não decide nada aqui.** O arquivo foi gravado às 22:20 e
  o cliente subiu às 22:33 — treze minutos, dentro da mesma hora, e o NTFS só
  reescreve o `LastAccessTime` quando o valor guardado tem mais de uma hora
  (`CLAUDE.md` §5). A sonda é inconclusiva por construção.

**Duas coisas foram trocadas por precaução, e as duas por terem precedente:**

**O arquivo passou a ser gravado como TEXTO Lua**, não bytecode. O cliente
aceita os dois, mas texto é o formato que este projeto já comprovou — o
`OngoingQuestInfoList.lub`, o `CheckAttendance.lub` e os `.lub` de `data\`
gerados pelo `traduz_ptbr.py` são todos texto puro e são lidos. O bytecode era a
única peça do caminho **sem precedente aqui**, e trocá-lo custa nada.

**O emissor passou a HERDAR de um que já funciona.** A primeira versão inventou
os quinze campos do zero, incluindo `srcmode`, `destmode` e `zenable` — modos de
blending do Direct3D que não se conferem offline. Agora ele parte de um dos
emissores de fumaça das chaminés de Prontera e troca só o que precisa mudar:
textura, posição, gravidade (zerada, para o halo não subir), tamanho, cor e
vida. É a regra de mesclar por chave em vez de escrever por cima (§4.5), agora
aplicada a um arquivo de cliente.

**E entrou um `--sonda`, que é o que decide se houver uma segunda falha.** Em
vez de acrescentar um emissor, ele troca a textura das **três fumaças que já
aparecem** e não mexe em mais nada. Se as chaminés passarem a soltar o brilho, o
arquivo está sendo lido e o defeito é do nosso emissor; se continuarem soltando
fumaça, o cliente não lê este arquivo, e nenhum ajuste de cor ou tamanho vai
resolver. É a "marca que não depende do efeito procurado" do `CLAUDE.md` §5 — a
mesma técnica que resolveu o `estende_robeid.py` e o `ajusta_tamanho_fonte.py`.

**A hipótese mais simples ainda não foi descartada:** havia **dois clientes
abertos** na máquina no momento da captura, um deles de **16:34** — seis horas
antes de o arquivo existir. Se a captura veio dele, ele nunca teve o que ler. O
próximo teste começa fechando os dois.

### O brilho que não saiu: quatro tentativas e o controle que faltou (2026-08-26)

O pedido era simples — *"uns brilhos embaixo da célula do Sábio Varmunt, com a
textura `epi_glow_01.bmp`"*. **Quatro idas ao jogo e nada apareceu.** O dono
mandou parar e registrar: *"em algum momento vou querer brilho e não podemos
errar de novo"*. Isto é esse registro.

O override foi **revertido** — Prontera voltou a ler o effecttool do GRF, com as
três fumaças de sempre. Nada ficou pior do que estava.

### Por que o caminho escolhido era o certo

Não dá para pedir aquela arte por `specialeffect`: o brilho de Epiclesis não é
um efeito numerado do cliente, é uma **unidade de habilidade**
(`UNT_EPICLESIS`), que só existe enquanto a magia está no chão — não há `EF_`
para ele no rAthena. O que existe é o sistema de **emissores de partículas por
mapa** (`data\luafiles514\lua files\effecttool\<mapa>.lub`), que aceita **o
caminho da textura direto** e é o que faz a fumaça sair das chaminés de
Prontera. A escolha continua sendo essa; o que falhou foi a execução.

### O que ficou ELIMINADO — não vale reinvestigar

- **a textura existe** no GRF, nos dois caminhos (a ferramenta recusa sem ela);
- **o caminho do effecttool é único** — não é o caso do `petinfo.lub`, que tem
  dois, e era uma hipótese boa que morreu na medição;
- **o arquivo gerado é válido**: passa no `luac -p` e, recompilado e relido pelo
  mesmo parser que lê os `.lub` do GRF, entrega os emissores certos;
- **o cliente ABRE o arquivo.** Provado empurrando o `LastAccessTime` para
  ontem e reabrindo o jogo: o carimbo pulou para **treze segundos depois** da
  abertura do cliente. Esse truque contorna a regra de uma hora do NTFS que o
  `CLAUDE.md` §5 registra, e passa a valer para conferir **qualquer** override
  de cliente — é o subproduto mais útil desta sessão;
- **a conversão de célula para mundo está certa**, e não por dedução: os
  **1.304 modelos** do `.rsw` de Prontera foram convertidos para célula pelas
  duas hipóteses de eixo Z e cruzados com o `.gat` — modelo é construção,
  construção bloqueia. **Z direto acerta 76,1%** de célula bloqueada; Z
  invertido, 41,1%;
- **bytecode contra texto não explica**: as duas formas foram tentadas.

### As quatro tentativas, na ordem

| # | o que foi | resultado |
|---|---|---|
| 1 | emissor novo, 15 campos inventados, em **bytecode** | nada |
| 2 | idem em **texto**, herdando os campos de desenho da fumaça | nada |
| 3 | sonda: **mover** a fumaça da chaminé para a célula do Varmunt | nada |
| 4 | régua: **seis clones** da fumaça que funciona, mudando só o z | **nada, nem a original** |

### O erro de método, e o que ele custou

Na tentativa 3 eu troquei o `pos` **inteiro** — mexendo em posição horizontal e
altura de uma vez. Se não aparecesse, e não apareceu, não haveria como saber
qual das duas era. É exatamente o que o `CLAUDE.md` §5 manda não fazer, cometido
dentro da própria ferramenta de diagnóstico. Corrigido na tentativa 4.

**E o passo 4 derruba a leitura do passo 3.** Como nem a fumaça de origem
apareceu, o que se viu no passo 3 — *"as outras fumaças continuam saindo"* —
pode ter sido **o arquivo do GRF o tempo todo**. Ou seja: a conclusão de que "o
arquivo é lido e aplicado", que eu dei como fechada, nunca esteve provada. O
carimbo prova que o cliente **abre**; nada prova que ele **usa**.

### A sonda que faltou, e é por onde começar da próxima vez

**Gravar em `data\...\effecttool\prontera.lub` o arquivo ORIGINAL DO GRF, byte
por byte, sem mudar nada, e entrar no jogo.**

- **fumaças continuam saindo** → o override funciona, e o defeito está no que a
  ferramenta *escreve* (formato do texto, índice base 0, ordem dos campos, o
  valor de `_prontera_effect_version`);
- **fumaças somem** → o cliente abre o arquivo de `data\` mas não consegue
  usá-lo, e o suspeito passa a ser o próprio mecanismo de override para essa
  pasta — não o conteúdo.

É o controle mais básico que existe — copiar o original sem alterar — e **não
foi feito em nenhuma das quatro tentativas**. Cada uma mudou conteúdo e posição
ao mesmo tempo, então nenhuma separa "o que eu escrevo está errado" de "override
desta pasta não vale".

A lição, e ela é maior que este brilho: **antes de mexer numa peça nova do
cliente, provar que o mecanismo de override funciona para aquela pasta — com uma
cópia idêntica do original.** As pastas onde ele comprovadamente vale hoje são
`System\`, `data\luafiles514\lua files\datainfo\` e as de sprite; `effecttool\`
**nunca tinha sido usada** por este projeto, e foi tratada como se já estivesse
provada.

A ferramenta ficou no repositório com esse roteiro no cabeçalho, marcada como
não funcional, e com `--sonda` e `--regua` prontos para a próxima tentativa.

### O brilho que saiu do cliente e virou uma linha de servidor (2026-08-27)

O pedido voltou no dia seguinte, e com **outra textura**:
`effect\mineffect\new_soundofdestruction\new_soundofdestruction_cast\
sound_castaura_7.bmp`, no Sábio Varmunt de `prontera 156,303`. Funcionou de
primeira, **sem tocar em um arquivo de cliente sequer** — e o que mudou não foi
a execução, foi a pergunta.

**A pergunta errada era "como faço o cliente desenhar esta textura?".** Ela leva
ao `effecttool`, que é o único mecanismo que aceita caminho de textura direto —
e foi por ali que se gastaram quatro idas ao jogo. A pergunta certa é **"que
número de efeito JÁ desenha esta textura?"**. Na maioria das vezes existe um, e
aí o pedido inteiro é uma linha de script, sem patch, sem override, sem pasta
nova para provar.

O que separou um caso do outro foi um detalhe do próprio pedido: junto do
`.bmp` havia um **`.str`** na mesma pasta do GRF. `.str` é definição de efeito
numerado; `epi_glow_01.bmp`, do pedido anterior, não tinha um — era unidade de
habilidade (`UNT_EPICLESIS`), e por isso ali o `effecttool` era mesmo o único
caminho. **A presença de um `.str` ao lado da textura é o sinal de que existe
número**, e é a primeira coisa a olhar.

#### Como o número foi achado — e por que não bastava lê-lo

O cliente numera efeito num `switch` de tabela direta, em
`GuerraDoEmperium.exe` (offset 0x006b6ce4):

```
lea eax, [ebx-13]                  ; ebx = numero do efeito
cmp eax, 0x937                     ; 2359
ja  <default: nao desenha nada>
jmp dword [eax*4 + 0x00ABFEE0]     ; tabela de 2360 entradas
```

Ou seja `número = 13 + índice`, faixa **13..2372**, e o bloco de cada `case`
empilha o caminho do `.str`. Daí sai **1642** para o
`new_soundofdestruction_cast`.

**Ler a instrução não é prova** — é uma medição só, e o projeto já pagou caro
por aceitar uma. A prova foi cruzar os 1015 efeitos com `.str` contra o enum
`e_special_effects` do próprio rAthena, pelo nome do arquivo:

| deslocamento | acertos |
|---|---|
| **13** | **25**, de `EF_STORMGUST` (89) a `EF_FULLMOON_KICK` (1230) |
| todos os outros, de 0 a 26 | **zero** |

Pico único, e os acertos vão de uma ponta à outra da faixa que o rAthena
nomeia — ou seja não há deriva nos ids altos, que é justamente onde o 1642
está. Mesma natureza da medição que decidiu o eixo Z do `.rsw` (76,1% contra
41,1%).

#### O teto que não era do cliente

`specialeffect 1642` **não funcionaria**, e o motivo é uma armadilha nova: o
`buildin_specialeffect` recusa a partir do `EF_MAX` do rAthena, que vale
**1243**. Só que esse teto é do **emulador**, não do cliente — este kRO de
2021-11-03 conhece efeitos até 2372, e **941 deles, com arte própria no GRF,
estão acima daquele teto**. O rAthena simplesmente não os nomeou.

Não se mexeu no enum nem no `specialeffect` (§2: código de terceiro não se
edita). Entrou um comando nosso, `efeitoespecial`, pelos ganchos oficiais
`src/custom/script.inc` e `src/custom/script_def.inc` — que o rAthena já
inclui sozinho, então **nenhum arquivo de terceiro foi tocado**. Ele é o
`specialeffect` com a faixa do cliente e nada mais; o original continua
intacto e continua recusando acima de 1242.

#### Os dois números que a tela decidiu

**900ms de laço.** O `.str` tem 54 quadros a 60 fps = 0,90s, então o laço fecha
exatamente na duração. Quem estiver com efeitos **normais** vê a outra variante
(67 quadros, 1,12s) e o disparo corta os últimos 0,22s. Preferiu-se cortar a
piscar: buraco entre voltas lê-se como defeito, corte lê-se como pulso.

**A textura pedida é a da variante REDUZIDA.** O efeito 1642 tem dois `.str`,
escolhidos em tempo de execução por `cmp [0x011d189c], 1` — a opção de efeitos
reduzidos. O `mineffect\` usa `sound_castaura_0..9.bmp` (a pedida); o normal
usa `sou_cast_00..09.bmp`, que é a mesma aura em resolução maior. Quem joga com
efeitos normais vê a segunda. Foi entregue assim, e o dono aprovou em tela.

#### A prova de que o laço gira, sem olhar para a tela

Log limpo não prova nada — é o silêncio de quem não rodou, e é exatamente o que
enganou nas quatro tentativas. A sonda foi a de sempre, a marca que não depende
do efeito procurado: **trocar 1642 por um número fora da faixa** e reiniciar. O
`efeitoespecial` gritou no log **37 vezes, uma por segundo**, provando de uma
vez que o `OnInit` rodou, que o temporizador gira e que o comando executa.
Depois, com o 1642 de volta: zero linha. Custou dois reinícios de dev e
respondeu o que a tela sozinha não separa.

#### O que sobrou

`ferramentas/lista_efeitos_do_cliente.py` — o de-para número ↔ `.str`, com
`--id`, `--textura` (qual efeito desenha tal `.bmp`) e `--conferir`, que refaz a
prova de calibragem e sai 1 se o cliente mudar. **É a ferramenta que responde o
próximo pedido de brilho em um comando.**

O `planta_brilho.py` continua onde estava, sem uso e marcado como não
funcional — o `effecttool` só volta a fazer falta para textura que não pertença
a efeito numerado nenhum, e nesse dia a sonda de controle do capítulo anterior
continua sendo o primeiro passo.

## A placa coreana sobre chão vazio, e as 514 que o cliente desenha sozinho (2026-08-27)

O dono mandou um print: em `prontera 166,300`, ao lado da Máquina Dimensional,
um balãozinho em coreano boiando sobre chão vazio. Pediu para tirar, mas antes
para saber do que se tratava.

### Não era NPC — e o `grep` provou isso primeiro

Varredura em `rathena/npc/` na faixa `prontera,16x,29x-30x` devolveu quatro
linhas, todas em `y=304/305` (Máquina Dimensional, Manouro, o Continental
Messenger duplicado e o `Billboard#Prt6`). Em `166,300`, nada. Se não é NPC e
mesmo assim desenha, é cliente.

### Ler o texto: recortar, binarizar, e decodificar byte a byte

O texto estava em CP949 renderizado como cp1252 — a mojibake de sempre. O
caminho que resolveu foi mecânico, não adivinhação:

1. Recortar a região do balão do `.jpg` e ampliar em **nearest-neighbor**, que
   é a mesma técnica da comparação de fonte de 2026-08-10 — a olho, naquele
   tamanho, `°` e `º` são o mesmo pixel.
2. Binarizar por luminância (>150 vira branco), o que tira o ruído de JPEG e
   deixa a forma de cada glifo inequívoca.
3. Transcrever os glifos e **decodificar por força bruta**, com alternativas
   para os ambíguos.

A segunda palavra fechou de primeira: `ÇÁ·Î¸ð¼Ç` = `C7C1 B7CE B8F0 BCC7` =
**프로모션**, "promoção". A primeira levou mais tempo porque a primeira leitura
(`°Ô½ÃÆÇ`, 게시판, "quadro de avisos") era **plausível e errada** — e o que a
derrubou não foi olhar de novo o print, foi procurar `프로모션` no cliente e
achar o contexto.

### O que a busca respondeu — e o `<NAVI>` que entregou a coordenada

Varrendo os bytes de `프로모션` pela pasta do cliente (pulando o `data.grf`, que
é grande demais para ler cru), o `System\itemInfo_sak.lub` deu 18 ocorrências.
Uma delas trazia a descrição da **Moeda Booster**:

```
프로모션 아이템 교환: <NAVI>[센트로]<INFO>prontera,166,300,0,100,0,0</INFO></NAVI>
```

**A própria coordenada do print.** Ou seja: no kRO havia ali um NPC de troca da
*Ragnarok Booster Promotion* de 2021, uma campanha paga de pré-venda. Aqui o
NPC nunca existiu; sobrou o anúncio. Com o contexto, a primeira palavra saiu
sozinha: `ºÎ½ºÅÍ` = **부스터**, "Booster".

### De onde a placa sai: um arquivo que o projeto nunca tinha aberto

Varrer as 282 entradas de texto do GRF apontou
`data\luafiles514\lua files\signboardlist.lub` — bytecode Lua 5.1, uma tabela
`SignBoardList` de **514 entradas** que o **cliente desenha sozinho**, por mapa
e célula, sem o servidor participar. Os nomes dos campos saem do
`signboardlist_f.lub` ao lado:

```
{ MAPNAME, CELLX, CELLY, HEIGHT, ICONID, FILEPATH [, CONTENTS, CHARCOLOR] }
```

A entrada é a **segunda do arquivo**:

```lua
{ "prontera", 166, 300, 6, IT_SIGNBOARD,
  "item\콜오브네메시스.bmp", "  부스터 프로모션", "#0x00FFFFFF" }
```

E não estava sozinha: a mesma campanha morta tem mais duas, `sp_cor 98,136`
(부스터일루시온인챈트) e `malangdo 152,136` (부스터 의상 인챈트). O dono mandou
arrancar as três.

### O caminho fácil que foi recusado, e por quê

O `cliente\data\...\signboardlist_f.lub` — que o ROenglishRE já tinha deixado
lá — traz um **`SignBoardIgnore`** feito exatamente para isto: declarar mapa e
coordenada em `SystemEN\Sign_Data.lub` e a função devolve `0`. Três linhas.

Não foi o caminho escolhido, porque ele pende de uma corrente que **não está
provada neste cliente**: o `_f` do override precisa vencer o do GRF, e o
`require('SystemEN/LuaFiles514/rotp_f')` do topo dele precisa achar um arquivo
que existe como **`.lua`**, não `.lub`. Se qualquer um dos dois falhar, o
cliente cai no `_f` do GRF — que não conhece `SignBoardIgnore` — e a placa
continua na tela, **calada**. Tirar a entrada da própria tabela não pende de
nada disso: seja qual for o `_f` que rodar, ele indexa `SignBoardList[idx]`, e o
que não está lá não é desenhado.

Custa mais: regerar 514 entradas a partir de bytecode. Foi o que
`ferramentas/remove_placas_mortas.py` passou a fazer.

### A trava que impede a regeração de jogar dado fora

Regerar um arquivo a partir de um leitor próprio tem um perigo específico: uma
construção que o leitor não entenda é **descartada em silêncio**, e o arquivo
novo sai plausível e incompleto — a mesma família do `RK` acima de 255 do
`luadis.py` e da tabela de uma entrada só do `ptbr._interpreta`.

A trava é exigir que o **conjunto de opcodes** do bytecode seja exatamente o
esperado (`LOADK`, `GETGLOBAL`, `SETGLOBAL`, `NEWTABLE`, `SETLIST`, `RETURN`) e
abortar em qualquer outro. Deu certo: o arquivo tem só esses seis.

Mais duas: as três placas casam por mapa+célula **e** pelo texto exato (nenhuma
das duas chaves identifica sozinha), e a conferência **compila o que foi gravado
e relê o bytecode com o mesmo parser**, comparando as 511 entradas uma a uma —
conferir por regex provaria só que a string sumiu, não que o Lua entende o
arquivo. É a mesma conferência do `planta_brilho.py`.

O gravado é **texto Lua**, não bytecode, pelo mesmo motivo do `planta_brilho.py`
— é o formato que este projeto já comprovou. E **cp949**: os 511 textos que
ficam são coreanos.

### Um bug de uma linha, que o Python esconde

O leitor de bytecode estourou na primeira execução, dentro da seção de depuração
do arquivo — longe da causa. A linha era:

```python
self.p += 4 * self._u32()
```

O `+=` guarda o `self.p` **de antes** de avaliar a direita, e o `_u32()` avança
o ponteiro no meio da conta — os 4 bytes gastos para ler o próprio contador se
perdem. O mesmo código em duas linhas, que era como estava no rascunho,
funcionava. Vale para qualquer `x += f()` em que `f` mexa em `x`.

### O que ficou de fora, por escolha

Das 514 entradas, **107 têm texto**, e boa parte segue em coreano — o
`traduz_ptbr.py` nunca tocou este arquivo. Foram tiradas só as três da campanha
morta. As outras dezenove de Prontera são legítimas: as quatro de salão de clã,
o `등급강화소` e o teleportador da Ordem (`낙원단 공간이동사`, 124,76). **Apagar o
arquivo inteiro levaria todas junto**, e é por isso que a conferência em jogo
não podia ser só "a placa sumiu": arquivo quebrado também some. O que separou os
dois foi olhar, na mesma ida, uma que tinha de ficar.

Traduzir as que sobraram continua em aberto, e pelo caminho da ferramenta é
trocar o campo `CONTENTS` na própria tabela.

### Publicado

Conferido em jogo pelo dono e publicado como **patch 0010**, "Placas mortas fora
do cliente" (5.946 bytes). É cliente: não anda por deploy.

## Vinte e um itens em oito vitrines de Prontera (2026-08-27)

O pedido veio com **57 números** e o próprio dono avisou que podia haver
repetição — *"alguns podem estar duplicados ou já existirem, ignore se for o
caso"*. Havia: **36 dos 57 já estavam à venda**. Os **21 que faltavam entraram
todos**, em oito das nove lojas do Mercado Contemporâneo — os dois últimos
depois de o dono escolher de que item cada um pegaria o desenho.

| loja | entraram | ficou com |
|---|---|---|
| Escudeiro | 5 | 22 |
| Chapeleiro | 3 | 33 |
| Lorde das Armaduras | 3 | 29 |
| Senhor das Armas | 3 | 58 |
| Acessorista | 3 | 70 |
| Sapateiro | 2 | 36 |
| Retoqueiro | 1 | 24 |
| Capeiro | 1 | 33 |

O **Ocleiro** foi a única loja que não recebeu nada: nenhum dos 21 é
equipamento de cabeça-meio.

### A metade do pedido que já estava pronta

Cruzar a lista com as linhas de `shop` dos três mercados antes de qualquer outra
coisa custou um script de vinte linhas e economizou a rodada inteira: **36 dos
57** já estavam em vitrine. Vale registrar porque dois deles pareceriam perdidos
a quem procurasse só no Mercado Contemporâneo — a **Muda de Mandrágora** (6217)
está na **Tranqueiras** e a **Caixa de Elmos Especiais** (23767) está no **Zé do
Caixão** (`prontera 159,131`). As duas são lojas de Prontera, só não são deste
quarteirão.

### O `Locations:` concordou com o pedido nos 21 — a segunda rodada seguida

As duas conferências que a regra 4.14 manda fazer deram acordo: o `Locations:`
do nosso `item_db` bateu com o destino pedido, e o `item_db` bateu com a linha
`Tipo:`/`Equipa em:` da descrição do bRO nos 21. **Nenhum override de
`Locations:` e nenhuma divergência a levantar.**

### O trabalho estava em 16 peças, não em 21

| o que faltava | quantos | por onde |
|---|---|---|
| entrada no `itemInfo.lua` | 10 | `completa_iteminfo.py` |
| `Name` em inglês no servidor | 10 | `nomes_pt_item_db.py` |
| os 4 arquivos de arte | 6 | `instala_visual.py` |
| não existia no servidor | 3 | `db/guerra/item_db.yml` |
| receita de cliente escrita à mão | 3 | `instala_item.py` |
| conjunto a espelhar | 2 | `db/guerra/item_combos.yml` |

As contas se sobrepõem — cada **Escudo Ilusión** aparece em três linhas, e a
**Greva Fantasma** nas quatro. As outras cinco peças não custaram nada: o
rAthena tinha, o cliente tinha em português, e o `valida_visual.py` aprovou os 4
(ou 8) arquivos antes de entrarem. A reconferência fechou em **0 faltando nos
21**.

### A nona leva de placeholders, e uma delas é renumeração de novo

As três que não existiam no servidor viraram entrada nossa em
`db/guerra/item_db.yml`, com os bônus lidos da descrição do bRO:

| id | item | o que é |
|---|---|---|
| 810011 | Velho Rifle | Rifle, ATQ 110, Justiceiros, dano de [Execução] por INT |
| 19317 | Elmo Alado Dourado | `Head_Top`, VIT +3, dano de [Explosão Rúnica] |
| 470309 | Greva Fantasma | `Shoes`, ATQ da arma +5%, ATQ +80 no +8 |

O **Elmo Alado Dourado (19317)** é o mesmo item que o **5970 do vendor**
(`RuneHelm`), renumerado pelo bRO — o mesmo padrão da Diadema do Paraíso
(19024 → 19455) e da Raposa Ilusional (420314 → 420227), e ele foi provado por
três caminhos independentes:

1. o `ClassNum` do 19317 no bRO é **1361**, que é o `View` do 5970;
2. o `Script:` do 5970 abre com as **três mesmas linhas** que a descrição do
   19317 promete — `bonus bVit,3`, `bonus bMaxHPrate,4` e o dano de [Explosão
   Rúnica];
3. o 5970 traz o pacote de **oito `autobonus3`** que é como o vendor escreve
   *"Mantém [Milagre das Runas] ativo"* — frase que a descrição do 19317 tem por
   extenso.

A terceira é a que fecha, e ela só apareceu porque a frase foi procurada nos
18845 itens do bRO em vez de ser interpretada: os únicos dois equipamentos que a
têm são o 19317 e o **[MEGA] Elmo de Fafnir (400177)**, que já está no
Chapeleiro desde a primeira rodada — e o `Script:` do Fafnir mostrava o pacote
pronto. No vendor ele aparece em três itens (5970, 19468 e 400177), então é
padrão e não invenção de um deles.

**Entrou o 19317 e não o 5970** pela razão de sempre: o nome do 5970 é **coreano**
no nosso cliente, e o bRO também o traz em coreano e **sem descrição** — o bRO
traduziu o número novo e deixou o velho para trás. Só entra na loja item com
nome em português (regra 4.2).

Onde a descrição do bRO discordou do 5970, quem venceu foi ela, porque é o texto
que o jogador lê: `Defense` 0 em vez de 15, nível mínimo 1 em vez de 50, e os
degraus de [Explosão Rúnica] em +9/+11 em vez de +6/+8 (os três valores são os
mesmos: 30/50/70). Uma linha do 5970 ficou **de fora de propósito** — o
`bonus2 bFixedCastrate,"RK_REFRESH",-100`, que a descrição do 19317 não promete.

### A Greva Fantasma repetiu a armadilha do Sapato Fantasma, com outro número

O `identifiedResourceName` do **470309** no bRO é `Arrogance_P_Shoes`, e o nosso
vendor **tem** esse nome — no **470080** ("Arrogant Thoughtform Shoes"), com o
`_` no 470081. Não é o mesmo item: DEF 12 / nível 100 / HP e SP +20% contra DEF
0 / nível 170 / ATQ da arma +5%. É exatamente o que aconteceu com o 470321 em
2026-08-20 (`Runaway_P_Shoes`), e pelo mesmo motivo: nome de recurso é só o
**desenho**, e a família Fantasma reaproveita os desenhos das *Thoughtform*.
Daí `Phantom_Greave`.

O conjunto **[Aura Fantasma]** dela foi espelhado em `db/guerra/item_combos.yml`
— cópia exata do grupo de FOR do vendor, que já serve aos 470293-470296 e ao
nosso 470321. Os outros quatro da descrição ([Argen Blanco], [Vernan],
[Fortridge] e [Ferramenta Dourada]) viraram **TODO**: as quatro armas existem no
vendor — `Argen_Blanco` (32023), `Vernan` (21052), `Fortrage` (32025) e
`Golden_Wrench` (1333) —, mas **nenhum `- Combos:` do `db/re/` casa qualquer uma
delas com calçado**, então não há o que copiar. Escrever quatro conjuntos do zero
a partir de prosa é o que as levas anteriores recusaram fazer.

### O nome de duas habilidades não estava no cliente, e uma delas veio do bRO

Os nomes saem do `skillinfolist.lub` **deste** cliente (regra 4.12), e ele
resolveu [Explosão Rúnica] = `RK_STORMBLAST`, [Vento Cortante] =
`RK_WINDCUTTER`, [Espiral Lunar] = `LG_MOONSLASHER`, [Arremesso de Machado] =
`NC_AXEBOOMERANG` e [Lança das Mil Pontas] = `RK_HUNDREDSPEAR`.

**[Execução] não estava lá** — é habilidade posterior a 2021-11-03. O
`skillinfolist.lub` do GRF do bRO (que é bytecode, lido com o `ptbr.py`) a dá
como **`RL_HAMMER_OF_GOD`**, e o vendor confirma o par sem margem: os únicos
itens do `item_db` que citam essa habilidade são os rifles **810000** e
**810002**, os dois de Justiceiro. Duas fontes independentes apontando para o
mesmo `SKID` é o que autoriza usá-lo.

**[Milagre das Runas] não é habilidade nenhuma** — foi o que a busca por nome
mostrou, e é o que evitou inventar um `bonus`. Ver o bloco do 19317, acima.

### As duas travas de sempre rodaram

O `zera_revenda_das_lojas.py` achou **4 itens dando lucro por clique** entre os
novos, e um deles não era de 9 zeny: o **Robe Chique (450010)** tem
`Buy: 200000` no vendor e revendia por **100.000 por clique**. O `Buy: 1` fechou
os 1774 itens das 23 lojas, e o `--conferir` deu OK.

O `marca_indestrutiveis.py` regerou o override sem mudar um byte: **nenhum dos
21** está entre os 28 que dizem "Indestrutível" sem ter o bônus. O Velho Rifle
diz, e já nasceu com `bonus bUnbreakableWeapon` — como as três armas da oitava
leva.

### O Arco Vigilante entrou por um terceiro caminho: nome coreano, descrição inglesa

O **18145** ia ficar de fora pela regra 4.2 — só entra na loja item com nome em
português, e o `itemInfo.lua` deste cliente o traz em **coreano** (`자경단 보우`).
O bRO tem o ID, mas também em coreano e **sem descrição**, exatamente como o
5970: o `completa_iteminfo.py` não tinha de onde copiar.

Só que o item está **inteiro** do lado do servidor (`Vigilante_Bow`, com
conjunto) e a arte deu **4 de 4**. O que faltava era só texto — e o próprio
pedido já trazia o nome: *"Arco Vigilante = 18145"*. É o caso **"Chapéu do
Éden"** pela terceira vez, e o primeiro em que as duas metades da entrada estão
em **línguas diferentes**: nome em coreano, descrição em inglês (ROenglishRE).

Virou a **décima receita** do `instala_item.py`, o único script que substitui
bloco existente. A descrição é tradução da inglesa que já estava lá, e as duas
foram conferidas linha por linha contra o `Script:` do vendor — *"for each 20
base DEX, +5% bow damage"* é `5*(readparam(bDex)/20)`, o *"+10% additional"* do
+7 é o `.@bonus += 10`, e o *"+50% Double Strafing"* do +9 é
`bonus2 bSkillAtk,"AC_DOUBLE",50`. **Nada sobrou dos dois lados**, que é o que
autoriza usar o texto inglês como fonte (no 490029, em 2026-08-20, tinha
sobrado — faltava a linha da Maestria Arcana).

Três decisões desse bloco que valem para a próxima receita:

- **A arte veio de `arte_de: 18163`, e não do próprio ID.** O recurso é coreano
  (`자경단보우`), então não cabe no campo `recurso`, que é ASCII; e `arte_de:
  18145` seria a auto-referência que a nota do 19272 proíbe — o script se leria
  a si mesmo. A saída foi o terceiro caminho: o **18163 usa o mesmo
  `identifiedResourceName`**, e são os dois únicos que o usam. Copiar dele é
  copiar o mesmo desenho sem ler o bloco que se vai sobrescrever.
- **`visual: 73` não bate com `View:` nenhum, e isso é o certo para arma.** O
  18145 não tem `View:` no `item_db`, e **nenhum arco do vendor tem** — o
  `ClassNum` do `itemInfo.lua` é a numeração de arma do cliente, que vive só
  daquele lado. Zerá-lo trocaria o desenho do arco na mão do personagem,
  calado. Os vizinhos confirmam a numeração: 18109 e 1748 também são 73, o
  18143 e o 18163 são 11. **A regra do LEIAME de que `visual` bate com `View:`
  vale para equipamento de cabeça, não para arma.**
- **O conjunto não é citado na descrição, de propósito.** O 18145 fecha um trio
  com o `Vigilante_Suits` (15176) e o `Vigilante_Bedge` (28441), e o conjunto
  **continua valendo** — só não aparece no texto. As duas outras peças têm nome
  **coreano** no `itemInfo.lua` deste cliente e não estão à venda: citá-las
  seria pôr coreano na tela do jogador.

A linha de classes saiu do bRO e não da entrada inglesa: o **18109**
(Catapulta) tem exatamente o mesmo `Jobs: Rogue` + `Classes: All_Third`/`Fourth`
e a descrição dele no bRO diz *"Classes: Renegados e evoluções"*. A entrada
inglesa dizia só *"Shadow Chaser"*, que é mais apertado do que o `item_db`
permite.

### Os dois últimos estavam presos na arte, e o destravamento foi uma escolha do dono

| id | item | o que faltava |
|---|---|---|
| 490029 | Ferramenta Mágica de Gelo | **arte** |
| 490482 | Pingente da Celine | **arte, nome e descrição** |

O **490029** já tinha ficado de fora em 2026-08-20 pelo mesmo motivo, e a
reconferência de hoje repetiu o resultado: os quatro arquivos de
`Geffenia_Magictool_Ice` não existem nem no nosso `data.grf` nem no do bRO. Item
sem arte entrega caixa modal ao aparecer na loja (regra 4.4). Dar a ele o
desenho de outro item — o que o `arte_de` do `instala_item.py` faz numa linha —
é decisão do dono. O pedido também trazia um nome novo, *"Ferramenta Mágica de
Gelo da Geffenia"*; o que o cliente desenha hoje é *"Ferramenta Mágica de Gelo"*,
e trocar é editar a receita daquele script.

O **490482** é o beco completo: o item existe no vendor (`Cel_Design_Pendant`),
mas o bRO **não tem este ID** — nem por número nem por nome; varridos os 18845,
o que há de "Celine" é o Broche (28572, já no Acessorista), o Laço, a Fita, o
Adereço e os dois vestidos. Sem entrada no bRO não há de onde trazer nome nem
descrição, e os quatro arquivos de arte também não estão em GRF nenhum. Ele tem
**dois conjuntos** no vendor, com o Broche e com o Laço, então não é peça
qualquer.

Os dois travavam na mesma coisa, e ela **não é decisão técnica**: dar a uma peça
o desenho de outra muda o que o jogador vê. Perguntado, o dono escolheu os
doadores por arquivo — `ice_stone_4th.bmp` para a Ferramenta e
`celine_brooch.spr` para o Pingente. Os dois recursos têm os **quatro** arquivos
no nosso `data.grf`, conferido antes de escrever a receita, e a consequência boa
disso é que **essa arte não entra no patch**: quem tem o cliente já a tem, desde
2021.

A **Ferramenta** também mudou de nome, como o pedido escreveu por extenso:
*"Ferramenta Mágica de Gelo da Geffenia"*. São 37 caracteres, dentro do corte de
40 do `nomes_pt_item_db.py`.

O **Pingente** precisou de descrição escrita do zero — não há texto de origem em
língua nenhuma —, e as três frases saíram de testemunhas do próprio bRO em vez
de tradução livre: `bonus2 bMagicAtkEle,Ele_All,10` é *"Dano mágico de todas as
propriedades +10%"* (22204, 20943), `bonus2 bMagicAddEle,Ele_All,25` é *"Dano
mágico contra oponentes de todas as propriedades +25%"* (490015) e
`bonus2 bMagicAddRace,RC_All,N` é *"Dano mágico contra todas as raças +N%"*
(1670, 15824).

**Uma linha do `Script:` dele é inerte neste cliente, e isso ficou no comentário
e não na tela — quase.** O `bonus bSpl,3` mexe em SPL, uma das seis
características de 4ª classe (POW, STA, WIS, SPL, CON, CRT) que chegaram ao kRO
em **2022**, depois do nosso 2021-11-03: este cliente não tem janela para elas e
o pacote não as leva. O bRO desta máquina também não as nomeia em descrição
nenhuma — procurado "SPL" nos 18845, zero. A linha entrou na descrição **com a
sigla**, que é como o rAthena a chama, para que a conta de efeito feche com o
`item_db` (`CLAUDE.md` §5) e para que ela já faça sentido no dia em que o
cliente subir de versão.

### O conjunto do Pingente com o Broche não fechava, e os dois ficam na mesma loja

O `db/re/item_combos.yml` casa o `Cel_Design_Pendant` com o **`Celine_Brooch`**,
que é o **28513** — e o broche da nossa vitrine é o **28572**,
`Celine_Brooch_BR`, o ID do bRO, que entrou como placeholder em 2026-08-01. São
itens diferentes, então o conjunto do vendor **não fecha com a peça que o
jogador compra ao lado**: os dois acessórios ficam no Acessorista, a poucos
cliques um do outro.

Foi espelhado em `db/guerra/item_combos.yml`, cópia exata do `Script:` do vendor
com o nosso AegisName no lugar do dele — a mesma receita da Diadema do Paraíso
(19455) e do Sapato Fantasma (470321). Sem ele a descrição prometeria um
conjunto que não acontece, e conjunto que não fecha não dá erro.

O outro conjunto do Pingente, com o **Laço da Celine** (18849, no Chapeleiro),
já fechava sozinho: o vendor casa `Celines_Ribbon` com o `Cel_Design_Pendant`, e
o Laço está à venda com nome em português.

### A subida não trouxe erro novo

Os quatro servidores locais foram reiniciados com o conteúdo novo. As três
sondas que denunciariam este trabalho deram **zero**:

| o que procurar | denuncia | saiu |
|---|---|---|
| `Unknown syntax` | linha ruim no `.txt` — mata o arquivo inteiro dali para baixo | 0 |
| `Invalid sell item` | item de vitrine que o `item_db` não conhece | 0 |
| `discounted buying price` | revenda maior que a vitrine | 0 |

O log traz **72 `[Error]`**, o mesmo número da subida de 2026-08-26 e das mesmas
duas famílias: os 34+34 do `job_outfits.yml` lido duas vezes (`PENDENCIAS.md`
§1z8) e os 2+2 de chicote/instrumento do nosso `item_db.yml`, nas linhas 819 e
1176 — as duas anteriores a esta sessão, que só acrescentou a partir da 3090.

### Publicado

Conferido em jogo pelo dono em 2026-08-27 e commitado em `e864db7`. A metade de
cliente virou o **patch `0011`**, "Vinte e um itens nas lojas de Prontera" — 25
arquivos, 23 MB crus em 2,53 MB de zip, quase tudo o `itemInfo.lua`.

Duas armadilhas do caminho de montagem ficaram registradas em `PENDENCIAS.md`
§1z10, porque a lista **não** pôde vir do `--desde`: o `ITEM`/`UI` do
`valida_visual.py` decodificam em **cp1252** e não em cp949 (é o que a API ANSI
gravou no disco, e é o que o Explorer mostra), e **não se envolve o `sys.stdout`
num segundo `codecs.getwriter`** — o `monta_patch.py` já tem o dele, e dois
empilhados quebram no meio do zip, no primeiro nome coreano.

A conferência de que os caminhos internos do zip estão certos foi comparar as
pastas dele com as do **patch 0009**, que os jogadores já aplicaram: conjuntos
idênticos.

**No ar desde 2026-08-27**, com o `publica_patch.sh --confere` fechando local e
remoto nos onze. Todo jogador o recebe na próxima vez que abrir o `Jogar.exe`.
Falta só o `implanta.sh`, que sai do Mac — e enquanto ele não roda nada
quebra: o item que o servidor ainda não conhece simplesmente não aparece na
vitrine.

## A Tinta para Parede Infinita, e o insumo que o fantasma queimava (2026-08-27)

O bot fantasma da Arena de Combate (`..\FANTASMA-BOT.md`) ganhou um ciclo de
combate que lança **Cópia Explosiva** (`SC_FEINTBOMB`) a cada volta, mais ou
menos a cada onze segundos. Isso expôs um custo que ninguém tinha medido: a
habilidade **gasta uma Tinta para Parede por uso** — da ordem de **oito mil por
dia** naquele ritmo. O estoque do personagem acabou no meio do próprio teste, e
a partir dali o log encheu de `Item necessário não encontrado - item 6123
(erro 71)`.

O pedido do dono foi por um item: *"seria ideal que ele tivesse um item 'Tinta
de Parede Infinita' que não fosse consumida quando a habilidade é usada, mas
que permitisse que a habilidade fosse usada"*.

### O que se descobriu antes de escrever qualquer coisa

**A habilidade pede DOIS itens, e o que acaba não é o que se imagina.** O
`Requires` dela no `db/re/skill_db.yml`:

```yaml
ItemCost:
  - Item: Paint_Brush     # 6122 Pincel de Grafite
    Amount: 0             # so precisa TER, nao gasta
  - Item: Surface_Paint   # 6123 Tinta para Parede
    Amount: 1             # gasta 1 por uso
```

O **Pincel de Grafite é ferramenta, não custo** — fica no inventário e nunca
some. Quem se esgota é a **Tinta para Parede (6123)**. É fácil trocar os dois,
e a troca leva a consertar o item errado.

**E a Tranqueiras vende o 6122, não o 6123.** O cabeçalho dela
(`npc/guerra/tranqueiras.txt`) diz que a vitrine existe para o Trapaceiro ter
onde comprar o insumo de treze habilidades em Prontera — mas o que aquelas
habilidades de fato consomem é a Tinta, que não está lá. O 6123 só é vendido
pelos `Part-Timer` do `s_atelier` (`npc/re/merchants/shops.txt:93`). Fica
levantado, e não foi mexido: é decisão de conteúdo, não do bot.

### O mecanismo: zerar o requisito, e um ponto só basta

O rAthena já faz exatamente isto para outro item, duas linhas acima de onde o
nosso enxerto entrou (`skill_get_requirement`, `src/map/skill.cpp`):

```c
// Check requirement for Magic Gear Fuel
if (req.itemid[i] == ITEMID_MAGIC_GEAR_FUEL && sd->special_state.no_mado_fuel)
    req.itemid[i] = req.amount[i] = 0;
```

O combustível do Mado Gear **some da lista de exigências** em vez de ser
descontado. A Tinta Infinita entra na linha de baixo, com a mesma forma.

**E um ponto só resolve as duas metades do problema** porque o
`skill_get_requirement` é a fonte única dos três caminhos que olham o custo:

| chamador | linha | papel |
| --- | --- | --- |
| `skill_check_condition_castbegin` | 8349 | é quem recusa o lance (o `erro 71`) |
| `skill_check_condition_castend` | 9501 | revalida ao terminar o cast |
| `skill_consume_requirement` | 9606 | é quem apaga o item |

Zerar ali faz a habilidade **passar na checagem** e **não consumir nada**, de
uma vez. Não há segundo lugar a mexer, nem risco de um caminho concordar e o
outro não.

### A regra é por ITEM, não por lista de habilidades

A condição olha o **insumo exigido** (6123), e não uma lista de `skill_id`.
São sete as habilidades que gastam Tinta — Cópia Explosiva, Pintar Armadilha,
Porta Dimensional, Símbolo do Caos, Redemoinho de Absorção, Sede de Sangue e
Borrifar Tinta —, e escrever essa lista no C++ criaria uma segunda fonte da
mesma verdade, que divergiria do `skill_db.yml` no dia em que alguém mexesse
nele. Pela via do item, a regra acompanha o banco sozinha.

O **Pincel de Grafite continua exigido**, de propósito: ele não é um custo que
se esgota, e custa 10z na Tranqueiras.

### O que ficou

| arquivo | o quê |
| --- | --- |
| `rathena/src/custom/tinta_infinita.hpp` | novo — a regra e o porquê |
| `rathena/src/map/skill.cpp` | um include + **uma** chamada (§2 do `CLAUDE.md`; era o primeiro enxerto neste arquivo) |
| `rathena/db/guerra/item_db.yml` | o item **30993**, `Tinta_Parede_Infinita`, Etc, com as sete travas da Maçã |
| `ferramentas/instala_item.py` | a receita da entrada de cliente, com `arte_de: 6123` |
| `cliente\...\itemInfo.lua` | aplicado nesta máquina (backup `.BACKUP-20260827-2052`) |

**Quem pode ter, hoje: só a staff.** O item nasceu `NoDrop`/`NoTrade`/`NoSell`/
`NoStorage`, sem vitrine e sem drop. A decisão do dono foi *"agora só a
staff/fantasma, mas mais pra frente ele pode se tornar um item objetivo de
quest grande"* — ou seja isto é o estado inicial, não o final. Quando a quest
existir, muda o `item_db` e o NPC que a entrega; **o C++ não muda**, porque a
regra pergunta "tem o item?", não como ele chegou.

### Medido em jogo, não suposto

Com o item no inventário do fantasma, contado a partir do restart das 20:53:

| medida | antes | depois |
| --- | --- | --- |
| falhas `item 6123 (erro 71)` | 79 | **0** |
| `Item removido do inventário` | 1 por volta do ciclo | **0** |
| usos confirmados pelo servidor | — | 11 |

As duas metades são medidas separadas de propósito: a primeira prova que a
habilidade passou a ser **lançável**, a segunda que **nada é gasto**.

### Pendência

O `itemInfo.lua` é cliente, e só existe nesta máquina. Enquanto o item for de
staff isso não alcança jogador nenhum, mas **antes de a quest existir ele tem
de ir por patch** (§4.18) — senão o item aparece como "Unknown Item" com
sprite de maçã para quem o receber, que foi exatamente o sintoma visto aqui
antes de o `instala_item.py` rodar.

## A caveira do fantasma, e o disfarce que o teria tornado inatacável (2026-08-28)

O pedido do dono foi o visual: que o personagem da conta fantasma — *"que
todos de preferência"* — aparecesse como uma **caveira FLAME_SKULL (1869)**.
Ele já veio com duas hipóteses próprias: reusar *"o mesmo mecanismo que define
o grupo da conta de GM podendo os personagens terem a roupa do GM"*, ou então
*"criar um pergaminho de transformação que atribui essa forma, mas aí teríamos
outras logísticas como fornecimento e obtenção dos mesmos"*.

As duas foram investigadas antes de escrever uma linha. **A primeira não
existe. A segunda existe — e o pergaminho é justamente a parte dispensável
dela.**

### O visual de GM não vem do grupo. Vem do cliente, e é estático

Isto já estava apurado no `PENDENCIAS.md` §1w, de 2026-08-17: o `group_id 99`
do banco dá os **comandos**; quem dá o **visual** é a lista `<aid><admin>`
dentro dos dois `clientinfo.xml`. É lista fixa dentro do cliente, fixa também
no sprite de GM, e a frase que ficou escrita lá vale inteira aqui: *"não há
como o servidor promover ninguém ao visual"*.

Ou seja, não há grupo a criar. Aquele caminho não tem para onde apontar.

### O `@disguise` faz exatamente o que se pediu — e mataria o recurso

O rAthena tem, sim, o mecanismo de "trocar o sprite inteiro do personagem": é
o `pc_disguise` (`src/map/pc.cpp`). Mas quem está disfarçado deixa de ser
anunciado como jogador:

```c
case BL_PC:  return (disguised(bl) && !pcdb_checkid(...))? 0x1:0x0; //PC_TYPE
```

`clif_bl_type`, `src/map/clif.cpp`. O `0x1` é **NPC_TYPE** — e cliente nenhum
ataca um NPC. O fantasma viraria um alvo que ninguém consegue acertar, que é o
oposto exato do que ele existe para ser. Três defeitos menores vêm de brinde: o
disfarce não sobrevive ao logout (é memória), o `pc_changelook` o desfaz, e o
pacote de rank de PvP é pulado de propósito para disfarçados (`clif.cpp`,
comentário *"Causes crashes when a 'mob' with pvp info dies"*).

### O que entrou: o motor do pergaminho, sem o pergaminho

O pergaminho de transformação é só um item que liga `SC_MONSTER_TRANSFORM`. O
status pode ser ligado direto por script — `transform 1869, INFINITE_TICK;` —
e com isso toda a logística de fornecimento que preocupava o dono desaparece.

E ele não é só mais conveniente que o disfarce; é tecnicamente melhor:

| | |
| --- | --- |
| **quem troca o sprite** | o **cliente**, ao receber o `EFST_MONSTER_TRANSFORM` com o id do monstro dentro (`SendVal1: true`, `db/re/status.yml`). O servidor não mexe no tipo da unidade: continua jogador — clicável, atacável e no rank da arena |
| **quando o fantasma sai do `@hide`** | o `clif_spawn` reenvia os EFST para a área (`clif.cpp`), então quem está por perto vê a caveira materializando |
| **no logout** | sobrevive sozinho: o status não tem `NoSave` nem `NoSaveInfinite`, o `chrif_save_scdata` grava a duração como infinita, e o `debuff_on_logout: 0` de `conf/battle/status.conf` não limpa nada na saída |
| **jogador tirando na marra** | não tira: `NoDispell`, `NoClearance`, `NoClearbuff`, `NoBanishingBuster` |
| **na morte** | cai — e é o único jeito de cair |

### Duas ordens, e as duas decidem se funciona

**A morte apaga o status antes do `OnPCDieEvent` rodar.** O
`status_change_clear` está no meio do `status_damage`, e os eventos de jogador
vêm depois — o próprio rAthena comenta a linha: *"Always run NPC scripts for
players last"* (`src/map/status.cpp`). É essa ordem que torna a reaplicação
possível ali dentro: quando o rótulo executa, não há status velho a atrapalhar.

**E ela precisa vir depois do `recovery`**, porque status nenhum inicia em quem
está morto. O `OnPCDieEvent` da arena já levantava e curava antes de teleportar
(por outro motivo — não mandar cadáver andando para o cliente), e essa linha já
existente é o que abre espaço para a nova.

### Não nasceu NPC nenhum na arena, e a dúvida era boa

O dono perguntou, ao ver a proposta: *"mas vai ficar um NPC na arena? visível?
clicável? ocupando uma célula?"*. Não — e a pergunta merece ficar registrada,
porque a palavra "NPC" no rAthena cobre duas coisas diferentes.

**Rótulo de evento não tem lugar no mapa.** O `npc_script_event`
(`src/map/npc.cpp`) percorre a lista de todos os NPCs que carregam o rótulo e
chama cada um, esteja ele onde estiver. Existe até o NPC *flutuante* para isso
(`-<TAB>script<TAB>Nome<TAB>-1`), sem mapa e sem célula — mas nem ele foi
preciso: os dois rótulos moram dentro da porta da arena, que já estava de pé em
`prontera,147,180`. A arena continua sem NPC nosso lá dentro.

### O que ficou

| arquivo | o quê |
| --- | --- |
| `rathena/npc/guerra/arena_de_combate.txt` | `.Fantasma`/`.Caveira` no `OnInit`, o rótulo `OnPCLoginEvent` novo, e uma linha no `OnPCDieEvent` depois do `recovery` — mais a seção "O visual do fantasma" no cabeçalho |
| `rathena/npc/guerra/scripts_guerra.conf` | o parágrafo do índice narrado |
| `..\FANTASMA-BOT.md` | a linha na tabela do §2 e a subseção "O visual de caveira" |

**Nenhum arquivo do rAthena foi tocado**, e **não há patch de cliente**: o
sprite 1869 é kRO padrão, já usado pelo `EndlessTower.txt` e pelo
`SealedShrine.txt`, e o cliente o desenha sem saber de nós. Isto vai por deploy
e só por deploy (`RECEITAS.md` §0).

**O visual é do GRUPO, não do personagem** — era o pedido. O teste é
`getgroupid() == 20`, o grupo `Fantasma` de `conf/guerra/groups_guerra.yml`.
Nenhum nome nem `char_id` foi escrito em lugar nenhum, então trocar o
personagem do bot não encosta em nada disto.

### Conferido

`@reloadscript` rodado pelo dono, e o `log/map-msg_log.log` não ganhou **uma
linha** de erro de parse (as 19.800 que entraram são todas
`mob_spawn_guardian`, o barulho normal de todo reload). Visto em jogo em
seguida: *"funciona exatamente como esperado"*.

### Duas pendências, nenhuma bloqueante

- **O `FANTASMA-BOT.md` continua fora do git** — ele mora em `..\`, na pasta
  guarda-chuva, que não é repositório. A parte do fantasma que este commit leva
  é a de dentro do `rathena/`; o resto segue sendo a decisão **D6** daquele
  documento.
- **Em mapa de Guerra do Emperium o rAthena desliga a transformação sozinho**
  (`mon_trans_disable_in_gvg`, `clif.cpp`). Não alcança nada hoje — o fantasma
  só vive em `pvp_n_1-5` —, mas se um dia ele pisar num castelo, volta a ser
  gente até sair de lá.

---

## O Pincel do Infinito, e a arte dourada que saiu de uma paleta (2026-08-28)

**Pedido do dono, na mesma sessão em que o fantasma da arena ganhou as duas
Máscaras.** Com elas o bot passou a gastar **Tinta para Pele (6120)** — uma por
lance, para sempre —, e o item que já resolvia esse tipo de problema, a Tinta
para Parede Infinita, não cobria essa tinta nem os pincéis. Nasceu o irmão dela.

### O que ele faz, e o que deliberadamente não faz

Quem carrega o **Pincel do Infinito (30992)** tem **três** requisitos zerados:

| item | o que é | quem exige |
| --- | --- | --- |
| 6121 Pincel de Maquiagem | ferramenta (`Amount: 0`) | as seis Máscaras, 2292–2297 |
| 6122 Pincel de Grafite | ferramenta (`Amount: 0`) | as sete Pinturas, 2289 e 2299–2304 |
| 6120 Tinta para Pele | insumo, 1 por lance | as seis Máscaras |

**A Tinta para Parede (6123) ficou de fora de propósito** — ela continua sendo
trabalho da Tinta para Parede Infinita (30993). Os dois itens têm funções
separadas, e quem quiser lançar a Cópia Explosiva sem gastar nada carrega os
dois. Eram quatro itens no inventário do fantasma; passaram a ser dois.

O pedido inicial era só "supre a Tinta para Pele"; **a correção veio no meio da
implementação** e acrescentou os dois pincéis, mantendo a tinta de parede fora.

### `Amount: 0` não quer dizer "opcional" — a parte que engana

Os dois pincéis são ferramenta: a habilidade exige que estejam no inventário e
nunca os gasta. Parece que não precisariam de isenção nenhuma. Precisam, e quem
mostra isso é o `skill_check_condition_castbegin` (`src/map/skill.cpp:9559`):

```cpp
if( index[i] < 0 || sd.inventory...amount < require.amount[i] )
```

O `index[i] < 0` reprova **antes** de olhar a quantidade. Sem o pincel na
mochila a habilidade falha com o mesmo *"item necessário não encontrado"* de
quando falta tinta. Zerar o `itemid` tira as duas exigências de uma vez, porque
o laço pula todo requisito com id zero.

### Um arquivo novo, e não uma linha no antigo

O enxerto entrou onde já estava o da Tinta, na mesma linha do
`skill_get_requirement` — mas a regra foi para
**`src/custom/pincel_do_infinito.hpp`**, arquivo próprio. Juntar os dois num só
teria sido menos código e mais confusão: são dois itens de jogo distintos, com
coberturas distintas, e um dia um pode existir sem o outro. O `skill.cpp`
passou a ter dois includes e um `if` com duas chamadas.

Vale de novo o que valeu para a Tinta: **um ponto só basta**, porque o
`skill_get_requirement` alimenta o `castbegin` (quem recusa), o `castend` e o
`consume` (quem apaga o item).

### A arte: recolorir vale mais que desenhar

Aqui o `arte_de` do `instala_item.py` — o campo que resolveu as dez receitas
anteriores copiando o `resourceName` de outro item — **não servia**, e o motivo
é o ponto do item: a Tinta Infinita podia usar o desenho da Tinta comum porque
o jogador nunca tem as duas com a mesma função ativa. O Pincel do Infinito
senta na mochila **ao lado** do Pincel de Maquiagem e do de Grafite. Três
pincéis idênticos é problema de leitura, não de estética.

O dono pediu um pincel dourado e ofereceu ele mesmo abrir o Photoshop. Não
precisou: **a arte de item de RO é quase toda indexada.** Dos quatro arquivos,
o `.spr` de chão e o ícone de 24x24 são imagens de 256 cores com a paleta em
bloco próprio — recolorir é reescrever **1024 bytes** e nenhum pixel é tocado.
Só a imagem de `collection` é RGB de verdade, e mesmo ela tem 75x100.

Daí o **`ferramentas/doura_arte.py`**. Ele não escolhe cor por pixel: escolhe
uma **rampa**. Cada cor vira uma luminância (0.299R + 0.587G + 0.114B) e a
luminância escolhe um ponto da rampa, que vai de marrom escuro a amarelo pálido
passando por ouro. O volume da peça original — o que é sombra e o que é brilho —
sobrevive intacto, porque é exatamente isso que a luminância carrega. Empurrar
o matiz teria dado amarelo chapado; é essa a diferença entre "amarelo" e
"dourado".

Mais uma **aura na ponta**, que é o que a descrição do item promete. Ela é um
halo radial só na `collection` (no ícone de 24x24 viraria borrão), e é misturada
por **interpolação e não por soma**: o fundo daquela imagem é branco puro, e luz
somada a (255,255,255) não vai a lugar nenhum.

### Três coisas que o script teve de saber, e que são armadilha

- **O nosso GRF não serve de fonte.** As quatro entradas do 6121 estão com DES
  no `data.grf` de 2021-11-03 (flags 3 e 5) e o `grf.py` não lê arquivo
  cifrado. A arte saiu do **GRF do bRO**, que é mais novo e não usa DES — o
  mesmo caminho que o `instala_visual.py` já usava.
- **A ordem dos canais da paleta muda entre os dois formatos**: BMP guarda
  BGRA, SPR guarda RGBA. Trocar os canais transformaria o marrom da rampa em
  azul.
- **Duas cores nunca são tocadas**: o magenta puro (255,0,255), que é a
  transparência do ícone e do `.spr`, e o branco puro da `collection`. Dourar
  a primeira pinta o fundo do ícone de ouro sólido; dourar a segunda pinta a
  moldura inteira da janela de descrição.

O `.act` passa intacto — é animação, não imagem. Existe na lista só para o item
ter os **quatro** arquivos: sem ele o cliente dá `Cannot find File` ao desenhar
o item no chão.

### O que isso torna possível daqui pra frente

O `doura_arte.py` é o **terceiro caminho da arte** de um item nosso, ao lado do
`arte_de` (copiar o desenho de outro) e do `instala_visual.py` (trazer arte
pronta do bRO). Ele serve sempre que o item novo precisa ser *reconhecível ao
lado* do velho, e não *igual* a ele — e não custa nem um repack de GRF nem uma
rodada de editor de imagem.

### Como foi conferido

- `cl /Zs` sobre o `skill.cpp` com os `defines` e includes do
  `map-server.vcxproj` (Release|x64): **exit 0, sem erro e sem warning**.
- `valida_visual.py --id 30992`: **4 de 4 ok**, os quatro no disco, em
  `cliente\data\`.
- `instala_item.py --verificar` antes de gravar; a entrada entrou entre 29715 e
  30993, +973 bytes, backup em `itemInfo.lua.BACKUP-20260828-0139`.

### O que falta, e não é pouco

- **Recompilar o map-server e reiniciá-lo.** A regra é C++: enquanto o binário
  for o antigo, o item existe, aparece com nome e arte, e **não faz nada**. O
  servidor estava no ar durante o trabalho, então o `.exe` estava travado.
- **Mandar o patch de cliente.** `itemInfo.lua` e os quatro arquivos de arte
  moram em `C:\GuerraDoEmperium\cliente\` — não vão pelo `implanta.sh`
  (`RECEITAS.md` §0). Quem não receber vê o item sem nome e com caixa de erro
  de arte.
- **A descrição diz "pinturas de rosto e corporal"** e o item também cobre as
  de parede, desde a correção. O texto é do dono, palavra por palavra, e foi
  mantido assim de propósito — a ficha logo abaixo dele conta a mecânica
  inteira, mas a linha de sabor merece uma decisão.

### O Vínculo Sombrio, o `savedata` que quase foi no patch, e o UTF-8 que voltou (2026-08-28, noite)

Fechamento da sessão do fantasma. Três coisas, e duas delas são armadilha.

#### O Vínculo Sombrio como último recurso

Pedido do dono: **abaixo de 10% do HP**, o fantasma joga o **Vínculo Sombrio**
(`SC_SHADOWFORM`, Id 2287) no oponente, com teto de 15s. Virou a fase `shadow`
do plugin, com precedência sobre tudo — inclusive sobre a fase `panic`, porque
mascarar o oponente não adianta nada com a barra no fim.

**O que muda o desenho é que o status fica em QUEM LANÇA, não em quem leva.**
O `sc_start4(src, src, ...)` de `src/map/skills/thief/shadowform.cpp` põe o
`SC__SHADOWFORM` no próprio caster; o alvo entra como `val2`, e é **ele** que
come o dano que o fantasma levar, até `4 + nível` golpes. Por isso a guarda de
*"já está ligado"* olha o próprio char.

E o preço é alto: **quem está com o Vínculo não bate e não lança mais nada** —
`skill_check_condition_castbegin` recusa qualquer habilidade a quem o tem
(`src/map/skill.cpp:8327`) e o status ainda traz `NoAttack` no
`db/re/status.yml`. Daí o `lowHpTimeout`, e daí a receita terminar em
`chase 15 hold` em vez de tentar atacar: **grudar mantém o vínculo vivo**, que
morre se o caster se afastar mais de dez células do alvo (o bloco *"Shadow Form
Caster Moving"*, `src/map/map.cpp:599`).

Nada disso é código novo: é uma receita de config a mais, como as outras três.

#### O `savedata` que o `--desde` teria mandado a todo mundo

Ao montar o patch, o `monta_patch.py --desde 2026-08-28` trouxe **quatro
arquivos de `savedata\`** junto com a arte — `UserKeys_s.lua`,
`OptionInfo.lua`, `ChatWndInfo_U.lua`, `MiniPartyInfo.lua` — só porque o
cliente tinha sido aberto para testar o item.

Aquilo é **estado do jogador**, não conteúdo: teclas, opções de vídeo, layout
de janela. Mandar em patch sobrescreve a configuração de **todo** jogador com a
desta máquina, e o sintoma para ele é *"minhas teclas mudaram sozinhas"* — sem
nada no jogo apontando para um patch.

O filtro `LIXO` não pegava porque **ele olha só o NOME do arquivo**, e
`OptionInfo.lua` não tem marca nenhuma. Entrou o `PASTAS_FORA`, que olha o
**caminho** — são duas perguntas diferentes e cada uma precisa da sua.

Sobreviveu por ser a única coisa que o resumo impresso antes de gravar existe
para pegar. **Esse resumo é a última linha de defesa do `--desde`, e foi lido.**

#### O `item_db.yml` reescrito em UTF-8, e quem pegou

Ao acrescentar a entrada do 30992, o `item_db.yml` foi gravado em **UTF-8 e
CRLF** — e ele é **cp1252 e LF** (a codificação é a regra 4.1 do `CLAUDE.md`; o
LF é regra explícita do `.gitattributes`, `*.yml text eol=lf`). Doze acentos
viraram U+FFFD, dano irreversível, e **nada no jogo teria reclamado**.

Quem pegou foi o **`prevoo.sh`**, no passo 3. Não foi teste, não foi revisão,
não foi o servidor: foi a varredura que existe exatamente para isso. O conserto
foi `git checkout` do arquivo e reaplicar as duas alterações por um script
`rb`/`wb`, byte a byte, sem decodificar nada.

**A lição não é nova — é a §4.1 inteira** —, mas ganhou um detalhe: *escrever*
é o passo perigoso, e a ferramenta de edição erra o encoding **e** o fim de
linha na mesma gravação. Rodar o `prevoo.sh` antes de considerar terminado
qualquer trabalho que toque `db/guerra/` é barato e pega os dois.

#### O que ficou pronto, e o que não

- **Patch 0013 montado e conferido** (`monta_patch.py --confere`: 0 problemas),
  5 arquivos, 2,46 MB. **Não publicado** — `publica_patch.sh` é o passo do dono.
- **`prevoo.sh` reprova por um motivo pré-existente**: 25 arquivos nossos com
  `\r`, todos assim **no próprio git** e nenhum tocado nesta sessão. Não é
  desta sessão, mas **bloqueia o `implanta.sh`**, que aborta com o pré-voo
  reprovado — precisa ser resolvido antes do próximo deploy de servidor.
- **A fase `shadow` não foi testada em jogo.** O Pincel, as Máscaras e a
  reação ao golpe pesado foram (*"FICOU LINDO! tudo testado!"*); o Vínculo
  entrou depois.

## A caixa de socorros que todo personagem novo recebe, em coreano (2026-08-28)

O dono mandou dois prints. No primeiro, o item que ele tinha na mochila desde
o primeiro minuto de jogo — a caixa de primeiros socorros — com o nome
`구급 상자(10)` e a descrição em inglês. No segundo, um dos itens que saem de
dentro dela: `초보자용 파란포션`, também em coreano. O pedido foi corrigir os
dois lados, *"todos os itens que vem dela assim como a descrição da própria e
nome"*.

### O buraco era uma corrente, não um item

O 23485 do print entrega cinco itens, e **um deles é a caixa seguinte**. Ela
entrega outra, de cinco em cinco níveis, até o 95. O fecho transitivo tem
**35 itens**, e **31 deles** estavam com o nome em coreano — tudo que um
personagem novo vê pela frente.

E o item de verdade não é o do print: o `start_items` do
`conf/char_athena.conf`, linha 124, entrega o **23484**, a caixa de nível 5. O
23485 é o que sobra na mochila depois de abrir a primeira. **Não há `grep` em
`npc/` que ache isso** — a linha mora no conf, e mais nada no servidor cita
aquele ID. Subiu para o `CLAUDE.md` §4.8.

### Nenhuma das duas ferramentas vizinhas servia

O `completa_iteminfo.py` importa do bRO, e **o bRO tem os IDs em coreano
também**; além disso ele se recusa a reescrever bloco alheio, de propósito. O
`nomes_pt_item_db.py` copia o nome do cliente para o servidor, e o buraco
estava justamente do lado do cliente. Sobrou o `instala_item.py`, que é o
único que **substitui** bloco existente — o mesmo caso do Chapéu do Éden
(19272) e do Arco Vigilante (18145), agora em escala.

### De onde saiu o texto, que é o que a regra 3 governa

A maioria destes itens é a variante *"não à venda"* de um item comum **que o
bRO já tem em português, com os mesmos números**. Conferido campo a campo no
`item_db`, não suposto:

| nosso | é o mesmo que | conferido |
|---|---|---|
| 11570 | 501 Poção Vermelha | 45~65 HP, peso 7 |
| 11566 | 503 Poção Amarela | 175~235 HP, peso 13 |
| 11572 | 505 Poção Azul | 40~60 SP, peso 15 |
| 11614 | 519 Leite | 27~37 HP, peso 3 |
| 11615 | 516 Batata Doce | 15~23 HP, peso 2 |
| 22544 | 656 Poção do Despertar | mesmo `Script:`, mesmo `Jobs:`, nível 40 |
| 22543 | 657 Poção da Fúria Selvagem | idem, nível 85 |

Nas duas últimas a lista de `Jobs:` foi comparada **conjunto a conjunto** com
a do irmão do bRO antes de a linha `Classes:` ser copiada — deram iguais, e é
isso que autoriza copiar a frase por extenso. Traduzir nome de classe para o
português é onde essa linha erraria calada.

**O prefixo `[Evento]` não é invenção nossa.** É como o bRO já traduz o
`[비매품]` (*"não à venda"*) do kRO nos dois itens desta mesma corrente que ele
tinha em português: 11565 `[Evento] Poção Branca` e 22542 `[Evento] Poção da
Concentração`. Seguir o vizinho de mochila vale mais que a tradução literal.

### O peso saiu do `item_db`, e num caso os dois discordavam

A descrição inglesa do 11518 dizia peso **1**; o `Weight: 50` do vendor diz
**5**. Quem manda o número para a janela é o servidor, então a descrição que
fecha com ele é a certa — a mesma família da Capa do Comandante
(`CLAUDE.md` §5).

### A lista de conteúdo é montada, não escrita

Cada caixa promete por extenso o que entrega. São 19 listas, e escrevê-las ao
lado do `Script:` seria criar 19 chances de a §4.11 acontecer — divergência
calada entre duas fontes indexadas pelo mesmo número. A receita traz só
`(id, nível, [(quantidade, id)])`, transcrito do `item_db`, e o texto sai daí
num laço. O aviso vermelho de perda de item foi mantido, e não é enfeite:
`getitem` com a mochila cheia **larga o item no chão**, e as caixas despejam
até 120 unidades de uma vez.

### A arte veio do irmão, nunca do próprio item

Os nove `resourceName` envolvidos são todos coreanos, então o campo `recurso`
(ASCII) não servia, e `arte_de` apontando para o próprio item é a
auto-referência que a seção do 19272 documenta. Cada um foi resolvido pelo
**irmão que compartilha o mesmo recurso** e que não está na receita — o
`응급처치상자` das 19 caixas saiu do 7641 (Caixa com Primeiros Socorros), o
`파란포션` do 505, o `수리용키트` do 6434, e assim por diante.

### Medições

- **31 blocos trocados, e só eles.** Comparado bloco a bloco com o backup: 0
  entradas fora da receita, 0 sumiram, 0 apareceram.
- **0 recursos trocados** — os 31 `identifiedResourceName` são byte a byte os
  de antes.
- **0 ocorrências de U+FFFD** no arquivo, e os 31 blocos decodificam em cp1252.
- `luac -p` compila o `itemInfo.lua` inteiro.
- +3.153 bytes.

### O que ficou de fora, por escrito

- **O `Name:` do servidor continua em inglês nestes 31.** Ele só aparece dentro
  de diálogo de NPC (`getitemname()`), e nenhum destes itens é citado por NPC
  nenhum — o único lugar que os menciona é o `start_items`. Sincronizar exige
  `nomes_pt_item_db.py`, que hoje mediria **16.746 trocas** em três arquivos do
  vendor: é decisão de outra sessão, não carona desta.
- **É cliente, então precisa de patch** (§4.18). Saiu no **0014**, e não
  remontando o 0013 — que já estava montado, conferido e com a linha escrita
  no registro quando isto entrou. Rebobinar um número já registrado, ainda que
  não publicado, é o hábito que o cabeçalho do `patches.txt` desaconselha, e o
  preço de não rebobinar é conhecido e pequeno: o `itemInfo.lua` viaja inteiro
  em todo patch que o toque, então o jogador baixa 2,45 MB comprimidos duas
  vezes em vez de uma. Os dois foram publicados juntos.

## O balão do ícone de status sai do coreano, 720 efeitos depois (2026-08-28)

O dono passou o mouse nos ícones da direita da tela e mandou quatro
screenshots: todo balão de status — o que diz o que o efeito faz e quanto tempo
falta — vinha em **coreano**. *"todos os status, que aparecem."* Num deles dava
para ver a tradução funcionando em volta do texto que não estava traduzido:
`53 segundos` em português na segunda linha, e a primeira ilegível.

### Onde o texto morava, e por que nunca esteve traduzido

No `data\luafiles514\lua files\stateicon\stateiconinfo.lub`, **dentro do
`data.grf`**, em coreano — sem arquivo solto em `cliente\data` para vencê-lo. É
o mesmo desenho do `addrandomoptionnametable.lub` de 2026-08-18: o
`traduz_ptbr.py` tinha catorze partes e nenhuma tocava este arquivo. Não foi
regressão, foi ausência.

O que o cliente pede está escrito no exe, em `Lua Files\StateIcon\StateIconInfo`,
ao lado de `EFSTIDs`, `StateIconInfo_F` e `StateIconImgInfo`.

### Já tinha sido tentado uma vez — e derrubou o cliente

Em **2026-07-30, ~12:35** (seção acima) o arquivo do ROenglishRE foi copiado
inteiro para essa pasta e virou o erro nº 2 dos oito: `StateIcon\StateIconInfo`
— `[string "buf"]:6801: table index is nil`. Ele foi movido para
`_backup_luafiles_roenglish\stateicon\`, e o custo registrado ali — *"nomes de
ícones de status voltam ao coreano"* — é exatamente a dívida que esta sessão
paga. A pasta `cliente\data\...\stateicon\` ficou vazia desde então.

Aquele arquivo foi reaberto agora, e a causa fecha no detalhe: das 842 entradas
dele **120 usam `EFST_IDs.<X>` que este exe não conhece**, a primeira na linha
6727 (`EFST_VR_SPEED`); a linha 6801, a que o cliente citou, é
`StateIconList[EFST_IDs.EFST_VR_BOOK002] = {`. Chave que o `efstids.lub` deste
cliente não tem vira `nil`, e `tabela[nil] = {...}` é erro de Lua que mata o
arquivo inteiro.

**O lado bom desse episódio é uma prova de graça:** o cliente *leu* aquele
arquivo solto e estourou nele, então o `DataFolderFirst` alcança a pasta
`stateicon\`. Não é uma pasta a provar, como foi a `effecttool\` em
2026-08-26 — é uma pasta já provada, de um jeito barulhento.

### As três fontes, e por que a chave só pode sair de uma

Entrou como a parte **`efeitos`** do `traduz_ptbr.py`, com a mesma arquitetura
do `encantamentos`:

1. **O nosso GRF dá as chaves** — 720 efeitos, todos por definição conhecidos
   deste exe. É o que impede o estrago de 2026-07-30 de se repetir.
2. **O bRO dá o português** — 515 dos 720, casado por chave (§4.5).
3. **O ROenglishRE preenche o resto** — 202, com o bloco dele verbatim, já que
   é texto puro e válido.

Sobram **3** em coreano (`EFST_NEEDLE_OF_PARALYZE`, `EFST_PERIOD_PLUSEXP_2ND`,
`EFST_PERIOD_RECEIVEITEM_2ND`), que nenhuma das duas fontes conhece.

### A entrada vai inteira, e não linha a linha

O `posTimeLimitStr` é o **índice** da linha do relógio dentro do `descript` —
só faz sentido ao lado do descript que veio junto. E os dois discordam de
verdade: no `EFST_QUEST_BUFF1` o coreano diz `3` e o bRO diz `2`, porque a
ordem das linhas mudou entre as revisões. Trocar só os textos e manter o
`posTimeLimitStr` de cá poria o relógio na linha errada, calado.

### A armadilha que quase custou um terço do trabalho

O bRO entrega o **mesmo arquivo duas vezes**: `stateiconinfo.lua`, texto puro e
legível, e `stateiconinfo.lub`, bytecode ao lado. O reflexo é pegar o legível —
e ele está **velho**: cita 340 efeitos contra os 530 do `.lub`. Ler o `.lua`
teria entregado 193 traduções a menos, sem erro nenhum, e o sintoma seria
indistinguível de *"o bRO não tem esse efeito"*. Subiu para o `CLAUDE.md` §5.

### Medições

- 720 entradas geradas para 720 do GRF; **0** entradas do GRF perdidas.
- **0** chaves que o `efstids.lub` deste exe não conheça — a trava que 2026-07-30
  pagou para descobrir.
- **0** ocorrências de U+FFFD; 520 linhas de texto com byte acentuado.
- 0 linhas com contagem ímpar de aspas.
- `luac -p` compila o arquivo inteiro.
- 169.318 bytes, CRLF, cp1252.

### O que fica em aberto

- **A conferência em jogo.** O cliente só lê isto na inicialização (§3): fechar
  e reabrir. O `LastAccessTime` do arquivo gerado foi empurrado para ontem, então
  o carimbo andar é a prova mecânica de que o cliente o abriu.
- **É cliente, então precisa de patch** (§4.18), e o patch fica para depois
  daquela conferência: publicar um `.lub` que o cliente recusasse tiraria o
  balão de **todos** os efeitos de quem já joga.

## O Líder da Ordem, o anel que ele comeu, e a frase do CLAUDE.md que o mandou comer (2026-08-28)

Pedido do dono: *"adicione na Ordem dos Exploradores o NPC que encanta os
equipamentos, em auction_02 43 65, com a sprite 4_M_HUMAN_01, que já esteve no
bRO fazendo o seguinte"* — com dois prints da página "Ordem dos Exploradores"
do browiki, que trazem as sete regras do serviço e as três colunas de encantos.

O NPC ficou em `npc/guerra/encantamento_da_ordem.txt`, arquivo próprio: são
onze peças, quarenta e seis pedras e um cabeçalho longo, e enfiar isso no
`ordem_dos_exploradores.txt` teria dobrado um arquivo que já é grande.

### O que o Líder faz

Põe **um** encanto por vez em capa, calçado ou acessório da lista do bRO, e
reseta todos de uma vez. Cobra 10 Moedas do Explorador mais 100.000 zeny nas
duas coisas — o preço da página. Capa e calçado aceitam 3 encantos, acessório
2, e acessório só conta no lado **direito**.

O encanto não é campo de item: é uma carta gravada nas covas 4, 3 e 2, de trás
para frente, deixando a cova 1 para carta de verdade. É o arranjo oficial, o
mesmo que os encantadores do próprio rAthena usam (`enchan_verus.txt:229`).
Como não existe comando que escreva numa cova, a peça sai e volta por
`delequip` + `getitem4`, levando de volta refino, covas, vínculo, grau de
encanto e bônus aleatório — os três últimos só existem no `getinventorylist`,
que é por isso que ele é chamado.

### O bug que apagou um Anel de Jasper

**Na primeira ida a jogo o NPC destruiu um item do dono e travou a janela.** O
`picklog` fechou o caso em uma linha: às 19:21:27, `type N`, `nameid 490113`
(Anel de Jasper) com `card0 27322` (Carta Ahat), `amount -1`, e nada devolvido.
No log do map-server, no mesmo segundo:

```
buildin_getitem2: Nonexistant item 0 requested
Script command 'getitem4' returned failure
```

A remontagem morava num `callsub S_Remonta`, e foi escrita sobre esta frase,
que estava no `CLAUDE.md` §5:

> `callsub` NÃO abre escopo novo: ele enxerga e sobrescreve as `.@` de quem
> chamou. Só o `callfunc` isola.

**É o contrário.** As duas últimas linhas do `buildin_callsub`
(`src/map/script.cpp:5508`) são as mesmas do `buildin_callfunc`:

```c
st->stack->scope.vars   = i64db_alloc(DB_OPT_RELEASE_DATA);
st->stack->scope.arrays = idb_alloc(DB_OPT_BASE);
```

Escopo novo e **vazio**. A única diferença entre os dois é o `callsub` passar
`.@` como argumento por referência, para o `getarg` — e **array não passa por
`getarg`**, o que torna `callsub` errado por natureza para uma sub-rotina que
mexa em `.@cova[]`.

Lá dentro, então, `.@part` valia **0**, que é `EQI_ACC_L`: o `delequip 0` tirou
e apagou o que estivesse no acessório esquerdo. E `.@equip_id` valia 0, então o
`getitem4` seguinte morreu, deixando o diálogo aberto no "Deixa comigo". **Os
dois sintomas relatados eram a mesma linha**, e por isso travava justamente
"quando ia dar certo": o caminho do sucesso era o único que chamava a
sub-rotina.

O que sobra, e vale mais que o conserto:

- **Zero é um valor plausível para quase tudo** — posição de equipamento, id de
  item, índice de tabela. Sub-rotina que devolva zero não parece quebrada,
  parece que não achou.
- **Comando que apaga coisa do jogador não roda sobre valor que não foi
  conferido na linha de cima.** A remontagem passou a ser inline, e ganhou uma
  trava redundante de propósito imediatamente antes do `delequip`: se algo
  voltar a zerar aquelas variáveis, o Líder recusa atender em vez de comer
  equipamento.

A entrada do `CLAUDE.md` §5 foi invertida, com o trecho do fonte e o custo. O
`anomalia_dimensional.txt` repetia a mesma frase num comentário — **o código
dele sempre esteve certo** (o `S_Planta` recebe tudo por `getarg`, e o
`S_Marca`/`S_Desmarca` só leem variáveis `.`), só o porquê estava errado, e foi
corrigido. Os outros seis arquivos com `callsub` foram auditados um a um:
`guardioes_dos_castelos`, `horario_da_guerra`, `senha_da_sala_secreta`,
`honra_de_combate`, `guia_de_prontera` e `porta_dos_orcs` passam por `getarg`
ou só leem `.`. Nenhum outro estava quebrado.

### A regra 7, e a metade que não estava escrita

A página do browiki diz, textualmente: *"Equipamentos refinados no +9 garantem
encantos melhores (Indicados em negrito abaixo)"*. A primeira versão leu isso
como **troca de faixa**: abaixo do +9 sorteava as comuns, do +9 para cima
sorteava só as de negrito.

Essa segunda metade não estava escrita em lugar nenhum. A página marca quais
são melhores; não diz que o sorteio encolhe. E o resultado em jogo foi o
contrário do que a própria regra promete: refinar a capa para +9 derrubava as
possibilidades de **dezesseis para três**. Quem pegou foi o dono, com a conta
na mão — *"deveríamos ter 20% de chance de falha, 80% de sucesso, e dentro dos
80% cada um teria 6,25%"*, que é 1/16, e o que saía era 1/3.

Cortada inteira por decisão dele: **chances iguais**, sem faixa separada e sem
peso por linha. O refino não influi em nada; o negrito ficou sendo só a ordem
da tabela.

É a §4.17 do `CLAUDE.md` pelo outro lado: lá o texto prometia o que o código
não fazia, aqui o código fez o que o texto **não** prometia. Regra de fonte
externa que só diz "X é melhor" não autoriza escrever "só X".

### Medições

- **46 pedras e 11 peças**, conferidas uma a uma nas duas travas: existem no
  `item_db` (as 46 com `SubType: Enchant`, que é o `CARD_ENCHANT` do reset) e
  têm entrada no `itemInfo.lua` deste cliente.
- Distribuição, dentro dos 80% de sucesso: calçado 12 pedras a **8,33%**,
  acessório 18 a **5,56%**, capa 16 a **6,25%** — o número que o dono mediu.
- As três faixas são contíguas e cobrem as 46; o `OnInit` recusa subir se
  deixarem de ser.
- `4_M_HUMAN_01` = view id **898**, conferido no `npcidentity.lub` e com
  `.spr`/`.act` no `data.grf` deste cliente.
- Três ids que não saem do nome: **22105** (Grilhões *com* cova — a sem cova é
  a 2408), **28388** (Bola de Ferro Ensanguentada com cova — a sem é a 2655) e
  **4767** (`Atk3`, "ATQ+3%"; o vendor tem *dois* itens chamados "ATQ +1%",
  4819 e 4882, na vizinhança do "ATQM +3%", e nenhum é o par dele).

### O de sempre, que também apareceu

Os diálogos tinham sido escritos com quebra de linha manual, e na tela o
cliente quebrou de novo por cima — sobras curtas no meio das frases. O dono
apontou: *"já não é a primeira vez, então adicione isso como observação"*.
Virou a **§4.22** do `CLAUDE.md`: um `mes` por parágrafo, nunca um `mes` por
linha de tela.

### Reposição

Uma unidade perdida: Anel de Jasper (490113) refino 0 com Carta Ahat (27322).
Os outros três travamentos morreram no `delequip` com o acessório esquerdo já
vazio — cobraram e não apagaram nada. Cinco cobranças ao todo: 50 Moedas do
Explorador e 500.000z.

## O Explorador da Ordem — a troca de moeda no sentido inverso (2026-08-28)

Pedido do dono: um NPC em `auction_02 56,46`, sprite `4_M_HUMAN_02` (899), que
troque **Moeda Nova por Moeda do Explorador, 1 para 1**, com a fala dele palavra
por palavra — *"O rapaz que ficava aqui fazia uns itens. Era um bruxo. Mas se
você quiser eu troco uma Moeda Nova sua por uma Moeda do Explorador"*.

### A conta que se faz antes de escrever: por que 1:1 não imprime moeda

A Máquina de Troca do mesmo salão (50,39) já fazia o caminho contrário desde
2026-08-08: **10 Moedas do Explorador por 1 Moeda Nova**. Duas lojas convertendo
a mesma dupla de moedas nos dois sentidos é a forma clássica de abrir dinheiro
infinito, e é o tipo de coisa que ninguém percebe pelo log — percebe-se pela
economia, semanas depois.

Não fecha, e sobra folga: 1 Moeda Nova vira 1 Moeda do Explorador aqui, e são
precisas **dez** para comprar 1 Moeda Nova de volta na Máquina — a ida e volta
custa nove décimos. O ciclo só passaria a **render** se uma Moeda Nova comprasse
mais de dez Moedas do Explorador, que é exatamente a taxa cobrada do outro lado.
A conta ficou escrita nos dois arquivos, porque mexer num `Amount` sem olhar o
outro é o que a quebraria.

O barter ainda ajuda de graça: **não há campo de quantidade para o item
vendido** (o cabeçalho do `barters_guerra.yml` já registrava a trava), então
"mais de dez por moeda" só se alcançaria por uma **caixa** de moedas. Se algum
dia entrar uma, a conta se refaz com o número de dentro dela.

### A célula, que é bloqueada de propósito

`56,46` não é andável, e não é engano — é a mesma família da Opheliac e das três
placas. O salão afunila entre y43 e y49 (anda só de x34 a x53) e volta a alargar
em y50; x54–x57 nessa faixa é o bloco de parede do lado leste.

O rAthena já punha NPC ali dentro: o `Auction Broker#lhz1` de **57,46**, uma
célula ao lado, que o `OnInit` do `ordem_dos_exploradores.txt` desliga desde
2026-08-08. Ou seja a célula está livre e a vizinha já foi provada por NPC
oficial. Da última célula andável do salão (x53) são três de distância, e o
alcance de clique é quinze (`npc_checknear`, `npc.cpp:2158`).

Facing **2** (oeste), o mesmo do Broker que ficava ao lado: olha para dentro do
salão, para quem sobe do corredor.

### Onde ficou, e o que isso quer dizer para a entrega

| o quê | onde |
|---|---|
| o NPC | `npc/guerra/ordem_dos_exploradores.txt` |
| a loja flutuante `Explorador#loja` | `npc/guerra/barters_guerra.yml` |
| a linha do índice narrado | `npc/guerra/scripts_guerra.conf` |

**Nada do cliente.** As duas moedas já têm entrada no `itemInfo.lua` desde a
Máquina e a Opheliac, então isto é **só deploy** — não há patch (`RECEITAS.md`
§0).

Recarrega com `@reloadbarterdb` **e só então** `@reloadscript`: com o barter
ainda não lido, o `callshop` do NPC procura um nome que não existe.

### Duas escolhas nossas, por escrito

- **O nome de tela.** O pedido não trazia um, e a tela precisa. Ficou
  "Explorador da Ordem", na família dos dois "Guarda da Ordem" do mesmo salão.
- **O "rapaz que fazia uns itens"** não tem NPC nenhum atrás — é sabor, e serve
  para explicar por que há alguém novo numa célula que estava vazia.

Conferido em jogo pelo dono no mesmo dia.

---

## A Glast Heim Sombria, que estava pré-instalada e faltando (2026-08-29)

O dono pediu para "deixar ativa" a **Maldição de Glast Heim Sombria** — a
versão difícil da Maldição de Glast Heim. A expectativa razoável era descomentar
alguma coisa. Não havia nada para descomentar: **a instância não existe em
versão nenhuma do rAthena**.

O que o vendor tem é uma linha de `Enter:` no `instance_db` (Id 49, mapa
`1@gl_he`) e **catorze monstros comentados** — `Id` e `AegisName`, sem um único
status. O `db/re/mob_db.yml` do **master do rAthena baixado neste dia** está
igual. E o `OldGlastHeim.txt` registra no próprio changelog que o NPC de acesso
a ela chegou a existir e foi **removido** na v1.5, sem que o outro lado da porta
tivesse sido escrito:

```
//= 1.2 Add NPC Hugin's Follower [exneval]
//=     NPC that give access to Glast Heim Nightmare Mode.
//= 1.5 idAthena merge. Removed Hugin's Follower NPCs. [Secretdataz]
```

### A medição que mudou o tamanho do trabalho

A parte cara de escrever instância é a planta: sem as coordenadas de dentro do
mapa, cada spawn e cada NPC é chute, e chute em coordenada falha **calado**.

O `1@gl_he` tem `.gnd` e `.rsw` do **mesmo tamanho** que o `2@gl_k`, o segundo
mapa da Maldição normal. Isso levou à comparação que decidiu tudo — e ela não
saiu do GRF, porque o `1@gl_k.gat` está **cifrado com DES** lá dentro e o
`grf.py` recusa. Saiu do `map_cache.dat` do próprio servidor:

```
mapa       xs   ys    bytes  md5 das celulas
1@gl_k     300  300     4012  91bd3083a9f2f1b2648b3e56786e6124
2@gl_k     300  300     3720  d983b45802caca950d2c1b530828370e
1@gl_he    300  300     3720  d983b45802caca950d2c1b530828370e   <-
1@gl_he2   300  300     3790  23c4bdfb86bbe6acaa1242a3ce12229e
1@gl_k2    300  300     4012  91bd3083a9f2f1b2648b3e56786e6124
```

**As células andáveis do `1@gl_he` são idênticas às do `2@gl_k`** — mesmo md5.
A Sombria roda na planta do segundo mapa da Maldição normal, e toda coordenada
do `OldGlastHeim.txt` vale nela sem conversão: a entrada (150,46), o Varmunt
(151,71), o Henrich (148,67) e os três portais do corredor central. De quebra,
o `1@gl_k2` (o modo Iniciante, também sem script) é cópia do `1@gl_k`.

Só o `1@gl_he2` é planta própria, e para ela não há referência em lugar nenhum.
As coordenadas dele saíram do `confere_celula.py --salas`, escrito para isso.

### O que já estava pronto, e ninguém tinha usado

Três descobertas em sequência, todas na direção de "isto custa menos do que
parece":

**O cliente conhece os catorze monstros.** Os ids 3139..3152 estão no
`npcidentity.lub` deste kRO de 2021, casando exatamente com os `AegisName` que o
vendor tem comentados. O `jobname.lub` dá o sprite de cada um: doze reusam arte
que já existe (`zombie`, `ghoul`, `khalitzburg`…) e **os dois MVPs têm arte
própria** — `mg_amdarais_h.spr` e `mg_corruption_root_h.spr`, os dois no
`data.grf`.

**O cliente conhece as quests, traduzidas.** O `QuestInfoList` traz as seis da
Sombria em português, e ninguém as tinha achado porque nada as citava:

```
12334  "Glast Heim Sombria"  /  "Retorne apos 3 dias."
12335  "Glast Heim Sombria"  /  "Entre na instancia Glast Heim Sombria."
12336  "Glast Heim Sombria"  /  "Elimine a Origem da Escuridao."
12337  "Glast Heim Sombria"  /  "Elimine o Amdarais Sombrio."
12338  "Glast Heim Sombria"  /  "Reporte o caso a Hugin."
12339  "Glast Heim Sombria"  /  "Reporte o caso a Hugin."
```

**E o `quest_db` do vendor já declarava quatro delas** — 12334 inclusive com o
`TimeLimit: 3d 4h` certo —, órfãs, sem nenhum script do rAthena as citando.
Faltavam só 12336 e 12337, e a razão é exata: são as únicas que precisam de
`Targets:`, e o alvo delas era um monstro que não existia.

Somando: **a instância inteira não pede patch de cliente.** Os mapas, os
sprites e os textos já estão na máquina de quem baixou o jogo.

### A derivação dos monstros

Cada `_H` é o monstro normal da Maldição com `Level +30`, `Hp ×2` (×10 nos dois
MVPs) e `EXP ×2`; todo o resto idêntico. Isso foi **conferido campo a campo
contra o divine-pride nos treze pares**, não deduzido — o HP bate nos treze, o
EXP bate nos treze, os seis atributos e as duas defesas batem em todos.

Ficou em `ferramentas/monta_mobs_da_sombria.py`, com `--conferir`, em vez de à
mão: a regra é mecânica, e assim ela se refaz se o vendor for atualizado.

Três detalhes que o gerador trata e não se devem desfazer:

- **`Attack` e `Attack2` não mudam.** O divine-pride mostra a faixa já
  *calculada*, não o campo. A razão entre a faixa do `_H` e o `Attack2` do
  normal deu 1,50 nos dois casos que dá para isolar (4804/3200 no Sanguinário,
  4179/2787 na Alma) — o campo é o mesmo, o que sobe é o nível.
- **O elemento vem do monstro normal, não do divine-pride**, onde a linha
  "Element" é a tabela de *resistência* e mostra `Neutral (100%)` para bicho
  Morto-vivo. Ler dali poria metade dos catorze em Neutro.
- **A carta é a única coisa que não se copia.** Os dois MVPs têm carta própria
  já no `item_db` (4602 e 4604). Copiar a do normal faria a Sombria, que custa
  dez vezes mais HP, entregar o mesmo prêmio da fácil — e deixaria as duas `_H`
  sem fonte no servidor inteiro.

### As habilidades, e a exceção no `.gitignore`

O `mob_skill_db.txt` não é YAML — não tem rodapé de import. O `mob_readskilldb`
(`mob.cpp:7184`) lê de `db/re/` e `db/import/` e mais nada, e `db/re/` é arquivo
de terceiro. Então as 78 linhas foram para `db/import/mob_skill_db.txt`, que o
`.gitignore` do vendor ignorava.

A primeira tentativa de exceção **não funcionou, e isso não aparece no `git
status`**: `/db/import` exclui a *pasta*, o git não desce nela, e o
`!/db/import/mob_skill_db.txt` é letra morta. A forma que vale é
`/db/import/*` mais a negação. O próprio `rathena/.gitignore` já descrevia a
regra vinte linhas abaixo, na nota do `!/src/custom/` — que resolve o caso
oposto.

Vale a ressalva de que `git check-ignore -v` **não** separa os dois casos: ele
imprime a regra de negação e sai 0 nos dois. Quem responde é
`git status --short --untracked-files=all db/import/`.

### O script

`npc/guerra/glast_heim_sombria.txt`, 851 linhas, seguindo os vinte passos da
página `Glast_Heim_Sombria` do `arquivo.browiki.org` — cada um marcado no código
como `// browiki N`. Entrada pelo **Sósia de Hugin** em `glast_01 179,282`, que é
onde a browiki o põe, ao lado do Hugin da Maldição normal.

Os diálogos são nossos: a browiki descreve o que acontece em cada passo, não o
texto das falas. O que veio de lá e não se inventa é o **nome** de cada coisa.

Os sete bônus do Fantasma de Varmunt saíram inteiros: os sete `SC_GLASTHEIM_*`
do rAthena são **exatamente** os sete "Temporais" que a browiki lista, com os
mesmos valores (+20 atributos, DEF+200/DEFM+50, HP+10.000/SP+1.000, cura
+100%/+50%, +100% de resistência ao Amdarais, +90% contra as barreiras de fogo,
+100% de dano). A Maldição normal já usa quatro deles com esses números, o que
serviu de conferência.

### Dois comandos que não existem neste rAthena

O script não subiu de primeira, e as duas falhas foram da mesma família:
`has_instance` e `getnpcx()`/`getnpcy()` **não estão na tabela de buildins deste
vendor**. O parser não diz "comando desconhecido" — diz `unmatched ')'` na
coluna do parêntese, porque tratou o nome como variável. A mensagem manda
procurar erro de sintaxe numa linha sintaticamente perfeita. Está no
`CLAUDE.md` §5, com a sonda que responde em um comando.

O `has_instance` saiu sem substituto: o `IE_NOINSTANCE` do próprio
`instance_enter` já responde "a fenda não está aberta" — uma checagem a menos, e
uma verdade a menos para divergir. O `getnpcx()` virou
`getmapxy(.@m$,.@x,.@y,BL_NPC)` sem valor de busca, que devolve a posição do NPC
que está rodando — e é o que faz os seis Homens caídos saberem cada um onde
está sem repetir coordenada.

### O que ficou medido

| antes do conserto | depois |
|---|---|
| erros de script na subida | 2 → **0** |
| monstros da Sombria no servidor | 14, `Loading` = `Done reading` |
| linhas de habilidade | 78 |
| erros de carga dos nossos arquivos | nenhum |

O `Loading '14'` igual ao `Done reading '14'` é a prova de que nada foi
descartado — e as quests 12336/12337 carregarem sem erro prova que os mobs 3150
e 3151 existem com o `AegisName` certo, porque o `parseBodyNode` do `quest_db`
descarta a quest inteira quando o `Mob:` não resolve (`quest.cpp:132`).

### Uma ressalva que fica por escrito

As recompensas de EXP são as do bRO — 250.000/150.000 no Varmunt e
350.000/250.000 no Hugin. O `getexp` **não passa pela taxa de EXP do servidor**,
só pelo `quest_exp_rate`, que está em 100 (`CLAUDE.md` §5). Num servidor onde
monstro rende 50x, essas recompensas valem um cinquenta avos do que o número
sugere em relação ao resto. Foi mantido assim porque a decisão do dono neste dia
foi seguir o bRO; ajustar é trocar quatro números no arquivo.

### Uma sujeira achada de passagem

O `rathena/.gitignore` tem **saída de `git status` commitada no meio de um
comentário**, entre as linhas 158 e 186 — `Your branch is up to date with
'origin/main'.`, uma lista de `modified:` e o `no changes added to commit`
partindo a frase da nota do `!/src/custom/` em duas. É anterior a este trabalho
(está no `HEAD`) e é da família do heredoc que come contrabarra, do `CLAUDE.md`
§5. **Não é funcional** — nenhuma daquelas linhas casa com caminho de verdade, e
o `!/src/custom/` no fim continua valendo —, mas está num arquivo que decide o
que chega à produção. Anotado em `PENDENCIAS.md`.

---

## A §5 sai do `CLAUDE.md` e vira seis cadernos (2026-08-30)

O `CLAUDE.md` chegou a **168.083 bytes**, e a divisão interna dele explicava
por quê:

| seção | bytes | % |
|---|---|---|
| §5 Armadilhas | **120.484** | **72%** |
| §4 Regras | 21.467 | 13% |
| §2 Lei da customização | 11.090 | 7% |
| §1, §3, §6–§9 | 11.614 | 7% |

Eram **140 armadilhas** numa lista única. O arquivo que a §6 manda ler
inteiro por ser "curto de propósito" tinha passado a carregar, em toda sessão,
a armadilha do `sshd_config` para quem ia mexer num NPC e a do `.rsm` para quem
ia fazer deploy.

**O corte foi por domínio, e o critério foi "que peça a pessoa está tocando":**

| caderno | armadilhas | bytes |
|---|---|---|
| `ARMADILHAS-CLIENTE.md` | 44 | 41.869 |
| `ARMADILHAS-SCRIPT.md` | 29 | 27.479 |
| `ARMADILHAS-RATHENA.md` | 22 | 20.450 |
| `ARMADILHAS-AMBIENTE.md` | 19 | 12.314 |
| `ARMADILHAS-INFRA.md` | 18 | 17.917 |
| `ARMADILHAS-COMBATE.md` | 8 | 6.868 |

O `CLAUDE.md` foi para **66.307 bytes — 61% menor**.

### O que ficou para trás, e por que não podia sair

**O valor de uma armadilha é reconhecer o sintoma antes de gastar horas
nele.** Mover o texto inteiro para outro arquivo resolveria o tamanho e
desligaria a lista: ninguém abre `ARMADILHAS-SCRIPT.md` para descobrir que
`callsub` abre escopo `.@` novo — abre depois de o `delequip 0` já ter
apagado o anel, que é quando a armadilha já cobrou.

Então o que saiu foi o **corpo**; o que ficou foi o **gatilho**, uma linha por
armadilha, agrupada pelo caderno onde o caso está contado por inteiro. A §5
continua sendo uma lista de 140 linhas que se lê de cima a baixo — só que
custa 21 KB em vez de 120.

**As ~200 referências a `CLAUDE.md` §5` espalhadas pelos outros documentos
não foram tocadas, e continuam certas:** a §5 existe, e agora leva ao caderno.
Reescrevê-las seria muito risco por nenhum ganho — boa parte dos `§5` do
`HISTORICO.md` e do `PENDENCIAS.md` são de *outros* documentos
(`PENDENCIAS.md §5b`, `IMPLANTACAO.md §5`), e um `sed` largo trocaria os dois.

### A regra que subiu

A §7 ganhou uma quarta regra: **armadilha se escreve nas duas pontas**, o
corpo no caderno e o gatilho na §5. Escrever só o corpo é enterrar; escrever
só o gatilho é perder a medição. E o gatilho tem de bastar sozinho — se
precisar de "continua abaixo", não é gatilho.

### Três coisas que a própria divisão quase quebrou

As três estão na §5 e as três morderam durante o trabalho, o que é um
argumento a favor da lista:

1. **O `CLAUDE.md` é CRLF.** O divisor leu por `split('\n')`, o que deixa o
   `\r` dentro de cada linha, e as linhas novas do índice nasceram em LF: o
   arquivo ficou **misto** (580 CR em 758 linhas) sem nada denunciar. O
   `git ls-files --eol` foi quem contou — `w/mixed` contra o `w/crlf` dos
   vizinhos. Tudo passou a ser lido em LF e gravado em CRLF, num lugar só.
2. **Heredoc com acento.** As âncoras de substituição passadas por
   `<<'EOF'` para o Python 2 casaram **zero vezes** — o `assert` parou antes
   de gravar, que é exatamente o que a §5 manda ter. Os scripts passaram a
   ser escritos como arquivo, com escapes `\xNN` nas âncoras.
3. **`cd` dentro de comando composto.** Um `cd` no início de uma linha fez o
   `cp` seguinte restaurar o backup **dentro do scratchpad** em vez do
   projeto, e o divisor releu o arquivo já dividido. A validação de
   classificação pegou (140 linhas sem grupo), de novo antes de gravar.

A conferência que fechou o trabalho compara o corpo das 140 armadilhas com o
backup, **linha a linha**: 1.635 linhas idênticas, nenhuma perdida nem
alterada.


## A Arena de Prontera fica com uma regra só (2026-08-30)

O pedido foi de derrubar, não de acrescentar: *"vamos derrubar a maioria das
regras, a única regra que vai valer agora é: pra contabilizar ponto e dropar a
caveira humana o jogador precisa ser level 200. Quando mata-se ganha um ponto.
Quando morre-se, perde 1 ponto. É isso"*.

### O que existia, e o que sobrou

| Regra | Desde | Hoje |
|---|---|---|
| só em `pvp_n_1-5` | 2026-08-07 | fica |
| matador e morto em nível 200 | 2026-08-07 | fica — e é a única condição |
| o matador só pontua se o morto tinha 0 ou mais (`.Piso`) | 2026-08-08 | **saiu** |
| a Caveira Humana só sai se o morto tinha 1 ponto ou mais (`.TrofeuPiso`) | 2026-08-08 | **saiu** |
| o morto perde 1 ponto em toda morte válida, até o piso de −10 | 2026-08-07 (o piso, 2026-08-13) | fica |

As duas que saíram eram de 2026-08-08 e viveram 22 dias. As variáveis foram
**apagadas** do `OnInit`, e não zeradas: regra que não existe mais não deve
continuar configurável, senão o próximo leitor a encontra e supõe que ela ainda
decide alguma coisa.

Com o `.Piso` fora, o `.@pontos_morto` perdeu o único uso que tinha — o script
não lê mais a reputação do morto em lugar nenhum. O `attachrid` até ele
continua, e hoje é só pelo nível e pelo nome.

O `getitem` do troféu e o `callsub` que pontua o matador ficaram lado a lado, no
mesmo caminho, depois do único `if` que sobrou: **onde sai um, sai o outro.**

### O nível 200 continua valendo dos DOIS lados

Perguntado ao dono antes de escrever, porque a frase do pedido está no singular
("o jogador precisa ser level 200") e as duas leituras dão servidores
diferentes. Com o `.Piso` fora, exigir o nível só de quem mata abriria a fazenda
de alt nível 1: matar o próprio boneco descartável em laço renderia um ponto e
uma caveira por morte, sem custo nenhum.

### O piso de −10 ficou, e é o único número que ainda limita alguma coisa

Também perguntado. Tirá-lo obrigaria a mexer no `Minimum: -10` do Id 5 em
`db/guerra/reputation.yml` — o piso tem dois donos, ver `ARQUITETURA.md` —, e
isso exige **reiniciar o map-server**, enquanto a mudança das regras pega com
`@reloadscript`. Ficou como estava.

### O freio da economia saiu junto, e isso é deliberado

O que segurava a Caveira Humana — que é MOEDA, trocada por Moeda Nova no
Egebreu — vinha em camadas, e a última caiu aqui:

- até 2026-08-13 havia teto por par de contas (o anti-conluio, `.Limite`);
- de 2026-08-13 a 2026-08-30 sobrou o `.Piso`, que era um freio de fato: cada
  morte empurra o alvo para baixo, então uma conta descartável rendia UMA
  caveira e UM ponto e depois parava;
- desde 2026-08-30 não há mais nada além do nível 200.

Uma dupla de nível 200 em revezamento produz uma caveira **por morte**, sem teto
nem espera. Está escrito nos três cabeçalhos que citam a torneira
(`honra_de_combate.txt`, `comprador_de_caveiras.txt` e a entrada 30995 do
`db/guerra/item_db.yml`), porque foi decidido sabendo disso — a mesma linha do
"vamos observar primeiro" de 2026-08-13.

### A descrição do item ficou mentindo, e virou o patch 0016

A Caveira Humana (30995) dizia, no `itemInfo.lua` do cliente:

> *"Essa caveira só cai de jogadores no level máximo **com reputação positiva**
> dentro da Arena de Prontera."*

A segunda metade deixou de ser verdade no instante em que o `.TrofeuPiso` saiu —
é a §4.17 do `CLAUDE.md` pelo lado do cliente. O conserto tem três pontas e
nenhuma delas é o deploy:

1. o texto, em `ferramentas/instala_item.py`, que é o gerador versionado;
2. `python ferramentas/instala_item.py`, que reescreve o `itemInfo.lua` desta
   máquina — **−23 bytes**, e o resto do arquivo byte a byte idêntico ao backup
   depois de deslocar o buraco (conferido, não suposto: o primeiro byte
   diferente é o 14.965.271 e `a[i+23:] == b[i:]`);
3. o **patch 0016**, "Descricao da Caveira Humana", 2,45 MB, já publicado — sem
   ele o jogador que já baixou o cliente continuaria lendo a frase velha
   (§4.18).

A frase que ficou: *"Essa caveira só cai de jogadores no level máximo dentro da
Arena de Prontera."*

### Onde encostou

| Arquivo | O que mudou |
|---|---|
| `npc/guerra/honra_de_combate.txt` | as duas travas, o `.@pontos_morto`, o texto da placa e três seções do cabeçalho |
| `npc/guerra/scripts_guerra.conf` | o índice narrado do NPC |
| `npc/guerra/comprador_de_caveiras.txt` | o cabeçalho dizia "três condições" e citava o anti-conluio, fora desde 2026-08-13 |
| `db/guerra/item_db.yml` (30995) | o mesmo engano, na entrada do item |
| `ferramentas/instala_item.py` | a descrição que o cliente mostra |
| `patcher/patches.txt` | o registro do patch 0016 |

Pega com **`@reloadscript`**. Nenhum valor de `db/` mudou, então não há
recarregador de banco nem reinício a dar. O lado do cliente já está no ar
(patch 0016); o do servidor espera o deploy.

## O Labirinto das Valquírias, que estava inteiro no vendor e desligado (2026-09-01)

Pedido em 2026-08-31: *"no bRO tinha um evento sazonal chamado Labirinto das
Valquírias. Quero implementá-lo permanente aqui"*. Veio com quatro prints da
bROWiki e um aviso — a descrição de lá está incompleta sobre mapa e monstros,
*"o mapa na verdade são dois ou três andares, e cada andar possui portais
'labirinto'"*.

Estava certo nas duas coisas, e a segunda foi o trabalho todo.

### O evento morreu, e a documentação morreu junto

O bRO fechou em **2026-07-29**. A página da wiki existe, mas descreve só a
economia: os dez pares de upgrade [MEGA], as tabelas de encanto, os preços e as
coordenadas dos NPCs em Malangdo. Sobre o calabouço ela diz três frases —
três andares, 1.000.000z por andar, e *"existem portais no calabouço que
enviarão seu personagem para fora do mapa"*. Nome de mapa, nenhum. Nome de
monstro, nenhum.

As três notícias oficiais do evento (2023, duas de 2024) foram recuperadas do
Wayback e repetem o mesmo, com uma frase a mais: *"uma sala exclusiva com
monstros poderosos que dropam a Mente Maligna. Os monstros não dão EXP e nem
dropam nenhum outro item"*.

### O mapa saiu de um minimapa de screenshot

A notícia de 2023 trazia duas imagens embutidas, e a segunda era uma
**screenshot in-game** — um grupo parado numa sala de pedra escura, ao lado de
uma estátua, com o **minimapa do cliente no canto da tela**.

O minimapa foi recortado da imagem, reduzido a uma máscara binária e comparado
contra **os 761 minimapas do `data.grf` do bRO**. Casou com `force_map1`. A
conferência contra o `.gat` fechou desenho por desenho: quatro salas de canto,
quatro corredores de borda, cruz central, e a cruz do sul com um bloco no meio
— o bloco é o pedestal da estátua da screenshot.

**`force_map1`, `force_map2` e `force_map3` são três arenas que a Gravity
desenhou e nunca usou.** O rAthena as traz **comentadas** em
`conf/maps_athena.conf` (linhas 19–21), sem um NPC, sem um warp e sem um spawn
— mas com verbete no `db/map_index.txt`, células no `map_cache.dat` e
`.gat`/`.gnd`/`.rsw`/minimapa no GRF do nosso cliente. Estavam prontas e
apagadas.

**Não é o Labirinto da Floresta (`prt_maze01..03`) nem o Ilusão do Labirinto
(`prt_mz03_i`).** O dono levantou isso no meio da sessão — *"que eu me lembre
existem cerca de 3 labirintos no jogo"* — e foi o que derrubou a primeira
hipótese, que era o `prt_maze`. São três labirintos diferentes, e este é o
terceiro.

### As salas não se tocam, e isso não é desenho nosso

Contadas pelo `map_cache` do próprio servidor (`confere_celula.py --salas`):
**13 salas no 1º andar, 11 no 2º, 16 no 3º**. Nenhuma encosta em outra —
nem uma célula de ligação. É assim que os mapas foram feitos.

Foi isso que explicou a pergunta do pedido. O portal da direita não leva ao
pedaço da esquerda porque **não existe "esquerda"**: existem 40 ilhas soltas e
um grafo de portais por cima. O bRO não desenhou labirinto nenhum; ligou salas
que já eram ilhas.

As quatro salas de canto do 1º andar são o detalhe bonito: cada uma é um
**anel com uma câmara selada no meio**, e a câmara é outra sala, só alcançável
por portal. A escada para o 2º andar fica dentro de uma delas.

### Os monstros já estavam no vendor, com o drop certo e sem spawn

A wiki não os nomeia. O caminho foi pelo item: `7583` = `Evil_Mind`
(사악한 마음), a Mente Maligna, e o Divine-Pride lista seis monstros que a
largam a 50% — os Ids **1799 a 1804**, os seis heróis selados
(`B_SEYREN_`, `B_EREMES_`, `B_HARWORD_`, `B_MAGALETA_`, `B_SHECIL_`,
`B_KATRINN_`).

No **nosso** `db/re/mob_db.yml` esses seis já vinham com **um único drop, a
Mente Maligna**, e com **spawn em lugar nenhum**: nada em `npc/` os invoca. O
conteúdo do evento estava inteiro no rAthena e nunca tinha sido ligado — a
mesma história dos três mapas.

Os andares 1 e 2 vieram do dono, com dois prints da RagnaPlace: os monstros de
**Biolaboratório 3** (`1634`–`1639` e o `2667`, Cecil Damon Brutal). Nível e HP
dos prints batem campo a campo com o nosso `mob_db` — os Ids do bRO são os do
rAthena, não houve nada a importar.

### As três decisões do dono, e a que mudou a implementação

1. **EXP fica** — nos três andares, contra o *"não dão EXP"* do bRO.
2. **Drop sai**, e **os MVPs de Bio 3 ficam de fora** (só a fileira de volume).
3. **Mente Maligna a 25%**, contra os 50% que o vendor herdou do kRO.

A segunda decisão é a que teve pegadinha. Tirar o drop dos `1634`–`1639` pelo
`mob_db` tiraria o drop **em `lhz_dun03` também** — valor de monstro mora no
`mob_db`, não na sala; é a mesma armadilha do `Buy: 1` das lojas de Prontera
(§4.16). A saída foi o mapflag **`nomobloot`**, que é por mapa: os andares 1 e
2 ficam secos e o Biolaboratório fica exatamente como estava.

O caminho oposto — `Rate: 0` no `mob_db` — **não funciona neste servidor**: o
`mob_getdroprate` (`mob.cpp:2884`) só respeita zero com `drop_rate0item`
ligado, e o nosso está em `no` (`conf/battle/drops.conf:137`). Taxa 0 volta
para 1, ou seja 0,01%.

E os 25% precisaram de **`Index: 0`** no override. Sem o índice o
`parseDropNode` (`mob.cpp:4854`) **acrescenta** um segundo drop em vez de
trocar o primeiro, e os seis passariam a ter Mente Maligna duas vezes, uma a
50% e outra a 25% — 62,5% efetivos, o contrário do pedido, e sem um aviso no
log.

### O que foi escrito

| Arquivo | O quê |
|---|---|
| `npc/guerra/labirinto_das_valquirias.txt` | o calabouço inteiro: Portal em `malangdo 211,155`, duas escadas, 14 mapflags, **78 portais** e 41 linhas de spawn |
| `conf/guerra/mapas_guerra.txt` | liga os três mapas |
| `conf/maps_athena.conf` | uma linha `import:` — enxerto novo, já na tabela do `CLAUDE.md` §2 |
| `db/guerra/mob_db_guerra.yml` | os seis overrides de taxa |
| `npc/guerra/scripts_guerra.conf` | a linha e o parágrafo |

**Toda coordenada foi conferida contra o `map_cache`** — chegada, portal e área
de spawn, uma a uma, por um script de conferência que também percorre o grafo.
Nove centros de spawn tinham caído em cima de pilar e foram recalculados. O
grafo alcança as 13, as 11 e as 16 salas a partir da entrada de cada andar, e
as duas salas de escada são alcançáveis.

A conferência achou também o que a §5 já avisava: **área de spawn é raio+1, não
lado**, e nos quatro anéis do 1º andar uma área "óbvia" põe monstro **dentro da
câmara selada** — o `map_search_freecell` olha se a célula é andável, nunca se
dá para chegar nela. Por isso os anéis têm duas linhas de spawn, uma por braço.

### A prova de que subiu

O map-server foi reiniciado e o `log/map-msg_log.log` não tem **uma linha**
sobre `force_map`. Isso é prova positiva, e não só ausência de erro: são 14
mapflags nos três mapas, e o `npc_parse_mapflag` (`npc.cpp:5434`) grita
*Unknown map* para mapa que não esteja **carregado**. Zero avisos = os três
carregaram.

Os 78 warps também passaram (`npc_parse_warp` erra em linha malformada e em
destino desconhecido), e o override do `mob_db` não levantou `invalidWarning`.

### O que ficou de fora, e é grande

Os três NPCs de economia do bRO — **Valquíria Mega**, **Valquíria Cena** e o
**Gerente** — não foram escritos. Quatro dos dez itens [MEGA] nem existem no
nosso `item_db`. E falta a entrada em português da Mente Maligna no
`itemInfo.lua`, que é patch de cliente. Tudo em `PENDENCIAS.md`.

## As duas Valquírias, e as três chamadas de script que não existiam (2026-09-01)

Segunda metade do Labirinto das Valquírias: o que se faz com a Mente Maligna.
A primeira metade — o calabouço — está na seção anterior.

### O que entrou

**Valquíria Mega** em `malangdo 204,147`, sprite `4_F_VALKYRIE`, virada para o
sudeste. Transforma dez equipamentos `+12` na versão `[MEGA]`, a 15%.
**Valquíria Cena** em `207,147`, sprite `4_F_VALKYRIE2`. Encanta essas
versões, até três encantos por peça, 800.000z e 10 Mentes por tentativa.

Os três sprites do dia — os dois da tabela acima e o `PORTAL` (10007) que o
dono pediu no lugar do `45` para a entrada do calabouço — foram conferidos
neste cliente antes de serem escritos: os três estão no `npcidentity.lub`,
abaixo do teto de 10508 deste exe, e os `.spr`/`.act` dos três estão em
`data\sprite\npc\` do nosso GRF. O rAthena exporta as três constantes com o
prefixo `JT_` cortado (`export_constant_offset(a,3)`), então no script elas se
escrevem `4_F_VALKYRIE`, `4_F_VALKYRIE2` e `PORTAL`.

### Os quatro itens que faltavam, com o nome certo

Das dez transformações, seis já tinham os dois lados no vendor. Quatro tinham
só o original. Os quatro `[MEGA]` entraram na décima leva de
`db/guerra/item_db.yml`.

O que muda em relação às nove levas anteriores: **os `AegisName` não são
palpite**. As levas de antes registram por escrito que os deles eram — o nome
oficial não estava ao alcance. Desta vez estava, no Divine-Pride, que os traz
como itens de jRO: `Assault_Rifle_89_`, `Spiritual_Dagger_`, `Shinboku_Wand_`
e `God_Ogre_Frail_`. O `_` final é a convenção da própria Gravity para "versão
melhorada", e casa com o par de cada um.

Efeito colateral do achado: descobrimos que dois nomes de levas anteriores
estão errados — `Ninjaken` (510064) devia ser `Spiritual_Dagger`, e
`Old_Rifle` (810011) devia ser `Assault_Rifle_89`. Não foram trocados, e o
porquê está em `PENDENCIAS.md`.

### O `.lua` legível estava velho, e teria mentido

Os quatro itens citam doze habilidades pelo nome em português, e três delas
são de Justiceiro: [Espiral Perfurante], [Explosão Antimatéria] e [Execução].
Procurá-las no `skillinfolist.lua` do bRO — o arquivo de **texto**, o que se
abre e se lê — devolve "não existe" para as três.

E é resposta errada. O bRO entrega o mesmo arquivo em `.lua` e em `.lub`, e o
legível está atrasado: 278 KB e 1062 habilidades contra 433 KB e 1253. As três
só existem no bytecode. Foi preciso escrever um leitor de bytecode para
alcançá-las — `RL_MASS_SPIRAL`, `RL_AM_BLAST` e `RL_HAMMER_OF_GOD`.

A armadilha já estava registrada em `ARMADILHAS-CLIENTE.md` ("o legível pode
estar velho") e ainda assim custou a primeira tentativa. A diferença é que
desta vez ela **não** ia dar erro: ia dar uma lista de doze com três faltando,
e três `TODO` num arquivo cheio de `TODO` legítimos.

### Três comandos de script que eu inventei, e o rAthena não tem

O primeiro rascunho das duas NPCs lia o estado da peça com
`getequipisbound`, `getequipgrade` e `getequiprandomoption`. **Nenhum dos três
existe.** Vínculo, prazo, grau de encanto e bônus aleatório não têm `getequip*`
nenhum: saem do `getinventorylist`, cruzando `@inventorylist_equip[i]` com o
bit `EQP_*` da peça e conferindo o Id.

Isso já estava resolvido no `encantamento_da_ordem.txt`, escrito em agosto, e
o cabeçalho de lá diz exatamente isso. As duas Valquírias passaram a copiar o
padrão dele inteiro, e não só essa parte:

- o **retrato da peça** tirado antes do primeiro `next`, e as três
  `F_IsEquip*Hack` comparando contra ele depois do último menu — reler a peça
  para compará-la consigo mesma passaria sempre;
- a recusa de peça **forjada ou assinada** (cova 0 em 254/255/256), onde as
  covas guardam o id do dono e não carta;
- a recusa de peça **alugada**, que voltaria sem prazo — um presente;
- a **trava de remontagem** redundante antes do `delequip`, que devolve o
  pagamento em vez de comer a peça;
- o `delequip` **inline**, nunca em `callsub` — o escopo `.@` novo e vazio é
  o que comeu um anel em agosto. O único `callsub` deste arquivo recebe
  número, devolve número e não toca em nada do jogador.

### A contrabarra que matou um arquivo inteiro

O sprite da entrada do calabouço mudou de `45` para `PORTAL`, e junto foi um
parágrafo de comentário explicando por quê. O parágrafo citava o caminho
`data\sprite\npc\portal.spr`, e o `\n` de `\npc` **virou quebra de linha de
verdade** ao passar pelo shell.

O resultado: meia linha de comentário virou uma linha solta, e o
`npc_parsesrcfile` respondeu *"Unknown syntax ... Stopping"* — que **mata o
arquivo inteiro dali para baixo**, os 78 portais e os 41 spawns junto. Um
comentário derrubou o calabouço.

A armadilha é conhecida das duas pontas (`ARMADILHAS-AMBIENTE.md` traz o
heredoc que come a contrabarra dupla, e `ARMADILHAS-SCRIPT.md` traz "uma linha
ruim mata o ARQUIVO INTEIRO, inclusive linha de comentário") e ainda assim
aconteceu. O que a pegou foi o log: uma linha de `[ Error ]` nomeando arquivo
e linha. A cura foi tirar a contrabarra do comentário.

### As decisões que foram nossas, e estão ditas onde aparecem

- **A coluna de preço: Valhalla, não Thor.** O bRO cobrava diferente nos dois
  servidores dele, e o Thor pedia até 80.000.000z por peça. A nossa economia
  não imprime zeny — as lojas de Prontera recompram a 1 (§4.16) —, então a
  escala menor é a que faz sentido aqui.
- **A quantidade de Mente segue a notícia de 2024, não a wiki.** As duas
  discordam, e a wiki não atualizou metade da coluna: seguir ela daria Botas
  Espaciais por 20 Mentes e Mega Vara por 200, dez vezes mais, por dois itens
  do mesmo porte. A notícia dá 200 para tudo, 300 nas Patas de Raposas.
- **A chance de encanto é 70%, e é nossa.** O bRO só dizia "existem chances de
  falha".
- **O reset cobra mesmo com a peça limpa**, como no bRO — mas a Cena agora diz
  quantos encantos a peça tem **antes** de perguntar. A regra é a mesma; o que
  mudou é o jogador saber no que está clicando.

### O que não foi escrito

O **Gerente**, o terceiro NPC. Vendia "armas por 150 Frutas dos Gatos" e
nenhuma fonte diz quais. Em 2026-09-02 o dono encerrou o assunto: ele
**não vai existir** aqui.

## O primeiro teste em jogo do Labirinto, e as quatro coisas que ele derrubou (2026-09-01)

O dono jogou o 1º andar no dia em que ele ficou pronto. Quatro relatos, e
todos os quatro eram defeito de verdade — nenhum era gosto.

### 1. A sala tinha elenco fixo, e isso não é labirinto

*"Se eu fizer sempre o mesmo caminho, vou encontrar sempre os mesmos. (…)
monstros específicos estão entrando em partes específicas do mapa, quando
deveria ser aleatório."*

A distribuição original dava **um tipo por sala**, ciclando os seis em ordem.
A regra era limpa de ler e errada de jogar: com as salas fixas e os portais
fixos, o elenco de cada sala virava parte da rota. Agora **os seis tipos
entram em todas as salas**, e o que muda de sala para sala é só a quantidade.

### 2. O volume estava em um quarto do que devia

Pedido: mais 300%, ou seja 400% do que havia. **161 monstros viraram 640** —
246 no 1º andar, 238 no 2º, 156 no 3º.

### 3. Matar não adiantava nada

*"O respawn tá alto, quando o player mata, tem que ter um respiro no mapa.
Hoje não acontece."*

Os andares 1 e 2 estavam com os **5 segundos** que os monstros têm em
Biolaboratório 3 — copiados de lá junto com os monstros, sem pensar. Cinco
segundos é menos do que se leva para atravessar a sala: o jogador matava e o
bicho já estava de pé atrás dele. Agora são **30 segundos** nos andares 1 e 2
e **60** no 3º, sem variação.

O único caso em que a regra pedida acelerou algo foi o Cecil Damon Brutal,
que estava em 10 minutos e caiu para 60 segundos. Está registrado em
`PENDENCIAS.md` porque é o que mais provavelmente vai querer voltar atrás.

### 4. Os portais nasciam colados na parede

O print mostrava um portal entalado na quina da sala, meio atrás de um pilar.
A causa era o critério de colocação: **as duas células mais distantes entre
si** dentro da sala — o que, por construção, cai exatamente nos dois extremos,
que é onde ficam as paredes.

Agora a peneira é a **folga**: só entram células com espaço livre em volta, e
o par mais separado sai de dentro dessa peneira. A folga mínima resultante é
2 e a média fica entre 4 e 6.

E apareceu de brinde um defeito que ninguém tinha visto ainda: **duas salas
tinham a chegada a duas células de um portal.** Ficar fora da área de toque
de 3×3 não basta — desembarcar ao lado dela significa que o primeiro passo na
direção errada teleporta o jogador antes de ele ver onde caiu. A regra agora
é quatro células de distância, e as 40 salas passam.

### O arquivo virou gerado

Os quatro ajustes juntos mexeriam em 78 portais, uma tabela de chegada por
sala e 250 linhas de spawn — e mover uma chegada obriga a mover todo portal
que aponta para ela. Escrever isso à mão duas vezes seria a §4.11 do
`CLAUDE.md` ao contrário.

`npc/guerra/labirinto_das_valquirias.txt` passou a sair inteiro de
**`ferramentas/monta_labirinto.py`**, que lê o `map_cache` do próprio
servidor e a tabela `GRAFO`. Volume, renascimento, fiação e pedágio são cada
um uma constante no topo da ferramenta.

Foi o que tornou esta volta barata: os quatro pedidos viraram quatro
constantes e uma função de colocação reescrita.

### E as escadas ganharam o sprite da porta

O `PORTAL` (10007) que o dono pediu para a entrada valia para as escadas
também — elas são NPC de clicar, como a porta, e estavam com o `45`, que é o
sprite de warp: o desenho dizia "atravesse", e a coisa pedia clique.

### Conferido

O map-server subiu com o arquivo novo e o log não tem uma linha sobre
`force_map`. O conferidor de coordenadas passa nas 40 salas: as 78 origens e
destinos são andáveis, nenhuma das 250 áreas de spawn vaza para outra sala,
os 81 nomes são únicos, e o grafo alcança as 13, as 11 e as 16 salas a partir
da entrada de cada andar.

## O mapa sabia onde os portais iam, e ninguém tinha perguntado a ele (2026-09-01)

Terceira volta do Labirinto, e a que resolveu o problema de raiz.

### O relato

*"Todos os portais parecem estar errados. Existe um semicírculo no chão no
qual o portal deveria estar lá, nenhum portal está corretamente posto no
lugar."* — com quatro prints, e nos quatro dá para ver o semicírculo de pedra
encostado na parede, vazio, e o portal a dez células dali, no meio do chão
liso.

Junto veio a pergunta que importava: *"Você consegue confirmar o bRO a
respeito dos portais? Do contrário vou ter um longo trabalho de mapear cada
um."*

### A resposta estava no `.rsw`, e ninguém tinha aberto

O `force_map1/2/3` traz plantado, no próprio arquivo de mundo, o modelo 3D
`반원워프장치.rsm` — em coreano, ao pé da letra, **"dispositivo de warp
semicircular"**. São **22 no 1º andar, 25 no 2º e 40 no 3º**.

Quem desenhou a arena marcou onde cada warp devia ficar, e a marca está no
arquivo desde sempre. As duas versões anteriores escolheram a célula por conta
própria — primeiro pelos extremos da sala, depois pela folga — e as duas
erraram, porque **a pergunta certa não era "onde cabe um portal" e sim "onde o
mapa diz que tem um"**.

A conversão do `.rsw` para célula é `pos.x/5 + largura/2` e
`altura/2 - pos.z/5`, com encaixe na célula andável mais próxima porque parte
dos arcos é desenhada meio dentro da parede. O `.rsw` saiu do `data.grf` do
bRO — no nosso ele tem flag DES.

### O que os arcos revelaram de quebra

**Quatro salas do 1º andar não têm arco nenhum**: as câmaras seladas dentro
dos anéis, aquelas que se enxerga do corredor e não se alcança. E o 3º andar
tem uma na mesma situação. Isso não é esquecimento do autor do mapa — é a
resposta dele: aquelas salas **não fazem parte do labirinto**, são cenário
que se vê e não se pisa.

As quatro saíram do grafo, e a escada do 1º andar, que morava numa delas,
mudou para o Anel Sudeste, em cima de um arco. O 1º andar passou de 13 salas
para 9; o 3º, de 16 para 15.

### O que dá para confirmar do bRO, e o que não dá

**Confirmado:** o mapa, os três andares, o pedágio, as regras de teleporte e
os portais que expulsam. E agora a **posição** de cada portal, que é a fonte
mais forte que existe para isso — não é o bRO dizendo, é o mapa que o bRO
usou.

**Não confirmável:** a **fiação** — qual portal leva a qual sala. Ela só
existia no script do servidor do bRO. O histórico da página do wiki foi
puxado inteiro: são catorze revisões, todas na tabela de upgrade e nos
encantos, nenhuma sobre o calabouço. As três notícias oficiais dizem a mesma
frase de sempre. E o wiki tem duas imagens no total, nenhuma de mapa.

A fiação daqui é sorteada com **semente fixa** — fixa para o labirinto não
mudar a cada rodada da ferramenta e o jogador que aprendeu o caminho não o
perder sem aviso. É garantidamente resolvível: o primeiro arco de cada sala
liga a próxima de uma corrente que passa por todas, e o último elo é a
escada. Os arcos que sobram são o ruído, e um em cada quatro expulsa.

### E as duas coisas menores do mesmo relato

**Todas as salas ganharam monstro**, inclusive as de chegada — *"a primeira
sala continua sem monstros, logo que entra. Todas precisam ter"*. A regra
anterior deixava as três de chegada vazias por segurança; agora a segurança
vem da distância, não do vazio.

**A chegada ficou mais longe dos portais.** *"Às vezes ao passar de um portal
pro outro eu apareço quase no meio do novo portal."* Com os portais nos arcos,
que ficam nas paredes, e a chegada na célula mais aberta da sala a pelo menos
quatro células de qualquer arco, os dois deixam de disputar o mesmo canto.

### Conferido

76 portais (78 arcos menos as duas escadas), 238 linhas de spawn, 634
monstros. O map-server subiu sem uma linha sobre `force_map`, e o conferidor
passa: as 9, 11 e 15 salas são alcançáveis a partir da entrada de cada andar,
nenhuma área de spawn vaza para outra sala, e os 79 nomes são únicos.

## A corrente do 2º andar, que veio de um minimapa com setas (2026-09-01)

Um dia depois de eu dizer que a fiação do labirinto estava perdida, o dono
apareceu com um print do minimapa do `force_map2` — o do bRO — com o caminho
desenhado em setas verdes, sala a sala.

As onze salas casaram uma a uma com as nossas, pelo formato: o quadradinho do
canto, a barra com o dente em cima, o retângulo alto da direita, os dois
blocos em L. A corrente:

```
3 → 9 → 4 → 6 → 7 → 5 → 2 → 10 → 1 → 8 → 11
```

**E ela derrubou uma suposição nossa.** A sala 3 é a única sem seta chegando,
o que faz dela a chegada do andar — e nós estávamos usando a 11. As duas
trocaram de papel: a 11 passou a ser onde fica a escada para o 3º andar, que
é o fim da corrente. A escada do 1º andar acompanhou: agora desembarca em
`force_map2 25,25`, dentro da sala 3.

**Qual arco de cada sala**, quando a sala tem mais de um, saiu da direção da
seta. Seis das onze têm arco único e não deixam dúvida; nas outras cinco a
seta aponta para um lado só — a de 7 para 5 vai para oeste, a de 2 para 10
vai para leste, a de 10 para 1 desce para sudeste, a de 1 para 8 vai para
oeste no alto, e a de 8 para 11 sobe para noroeste. Cada uma casa com um arco
só.

**O que o print não diz** é para onde vão os nove arcos que sobram: o desenho
traz o caminho que resolve, não o labirinto inteiro. Esses continuam
sorteados — e são eles que fazem o andar ser labirinto em vez de fila.

O 1º e o 3º andar continuam com fiação nossa. Print equivalente entra na
ferramenta em minutos: são as constantes `CORRENTE_MANUAL` e
`ARCO_DA_CORRENTE`, e a validação que já existe recusa corrente que não
cubra todas as salas ou que não comece na entrada declarada.


## O 1o andar veio no mesmo dia, e trouxe "Comeco" e "Fim" escritos (2026-09-01)

Meia hora depois do print do 2o andar veio o do 1o, e esse era ainda melhor:
o desenho traz as duas pontas rotuladas.

```
1 → 6 → 3 → 8 → 5 → 9 → 4 → 7 → 2
```

Nove salas, nove elos, e cada seta desenhada DENTRO da sala apontando para o
lado em que fica a proxima - o que confirmou a leitura de qual arco usar em
todas as nove, sem chute. A entrada ja era a nossa, o Atrio da Estatua; o que
mudou foi a escada, que saiu do Anel Sudeste e foi para a Encruzilhada, que e
o "Fim" do print.

Sobrou UMA ambiguidade no levantamento inteiro, e esta escrita na ferramenta:
o print marca a sala 2 como Fim mas nao diz qual dos dois arcos dela e a
escada, porque a seta de la aponta para a chegada e nao para a saida.
Escolhemos o arco sul, que e o mais perto de onde a seta termina.

E o print pegou um defeito de brinde. Com a corrente do bRO travada, o sorteio
dos arcos-isca deu, na sala 6, o MESMO destino do elo da corrente: os dois
portais da sala levavam ao mesmo lugar, o que tira a escolha do jogador sem
avisar. O sorteio agora recusa repetir o destino do elo.

So o 3o andar continua com fiacao nossa.


## O 3º andar deu a chegada e os dois portais que expulsam (2026-09-01)

Terceiro print do mesmo dia, e o que traz menos - de propósito. Ele mostra o
minimapa do `force_map3` com a seta branca do jogador no alto e um aviso:
*"tome bastante cuidado com esses 2 portais! Eles o teleportarão para
Malangdo novamente"*, com duas setas apontando para eles.

O que dá para tirar dele:

- **A chegada é a sala 1**, a Grande Galeria Norte. O canto do minimapa mostra
  `110 188`, e essa célula cai dentro dela - confirmação numérica, não só
  visual. Nós estávamos usando a 15, a Câmara Noroeste.
- **Os dois portais que expulsam** são o `92,140`, na Câmara do Centro, e o
  `100,34`, na ponta sul do Corredor Central-Sul. São os únicos do andar: o
  sorteio deixou de criar expulsão no 3º andar.

E um detalhe de encaixe: o arco `92,140` é justamente o que a corrente usaria
como elo da Câmara do Centro. Como ele expulsa, o elo passou para o outro arco
da sala.

**A fiação do 3º andar continua sorteada**, e por decisão do dono: *"aqui não
temos o grafo, de onde vai pra aonde, mas aqui é livre, o importante é o
começo"*.


## O 1º andar deixa de ser deduzido e passa a ser ditado (2026-09-01)

Depois de percorrer o andar em jogo, o dono ditou a planta inteira: portal por
portal, com a célula de destino de cada um. O 1º andar deixou de sair de
`ARCOS` mais corrente e passou a sair de uma tabela própria,
`PORTAIS_MANUAIS`, onde **o destino é uma célula e não uma sala**.

### O que entrou

**Onze portais novos**, todos de raio 2 — gatilho 5×5 em vez de 3×3, que é o
tamanho de quem se trombra sem procurar. Um deles, em `99,11`, é o portal de
volta para Malangdo.

**Doze mudanças nos que já existiam**: a chegada do andar saiu do meio do mapa
para `99,18`; o portal de `66,26` andou três células para a esquerda; e dez
tiveram o destino trocado por uma célula exata. O de `100,180` deixou de
existir.

**A escada trocou de lugar com o portal de cima da Encruzilhada.** Ela estava
em `100,81` e o portal em `100,118`; agora o NPC fica em `99,123` e `100,81`
virou portal comum, herdando o destino que era do outro.

### Três destinos ditados caíram dentro de parede

`174,37`, `163,175` e `26,164`. Os dois primeiros estavam a uma e a duas
células da sala certa e foram encaixados em `174,38` e `161,175`.

O terceiro é o que merecia cuidado: **`26,164` tem a câmara selada a duas
células e o anel a três.** Encaixar pelo mais perto teria mandado o jogador
para uma sala sem saída — as quatro câmaras do 1º andar não têm arco, não têm
portal e não têm como sair. Foi para o anel, em `26,161`, que é onde outro
portal do próprio levantamento já manda.

### E duas chegadas tiveram de se mexer sozinhas

Isto não estava no pedido e só apareceu na conferência. Dois portais antigos
mandavam para células que os portais NOVOS agora cobrem:

- a chegada da sala 6 era `25,10`, e o portal novo de `25,8` tem raio 2 — o
  gatilho dele vai até `y=10`;
- a chegada da sala 8 era `10,173`, e o portal novo de `8,173` tem raio 2 — o
  gatilho vai até `x=10`.

Nos dois casos o jogador desembarcaria **em cima** de um warp e seria
teleportado de novo antes de dar um passo. As duas chegadas passaram a ser
calculadas descontando o raio de cada portal, e foram para `10,19` e `19,158`.

A ferramenta ganhou junto uma trava, o `confere_gatilhos`: nenhum destino pode
cair dentro do gatilho de nenhum portal, e a geração **para** se cair. É o
tipo de defeito que não dá erro no servidor - o jogador só é cuspido em
sequência e não entende por quê.

### Uma coisa para olhar em jogo

O portal de `156,26` manda para `121,100`, e o portal novo de `124,100` tem
raio 2, ou seja gatilho a partir de `x=122`. Estão a **uma célula** um do
outro: quem desembarca ali e dá um passo para leste é levado para `130,26`.
Passa na trava porque `121` está fora do gatilho, mas é de propósito ou é
engano - só quem jogou sabe.


## O portal fica na parede que dá para a próxima sala (2026-09-02)

O 2º andar foi percorrido em jogo e o relato foi o mesmo do 1º, mas com uma
regra junto: *"se estou no mapinha 2 e para ir para o mapinha 3, que fica
acima, o portal fica horizontalmente no meio e na parte de cima do mapinha"*.

E com dois exemplos com célula: da Sala Leste para a Sala do Centro o portal
tinha de ficar *"perto da célula 159 77"*, e não no meio da sala; e da Sala do
Sul para a Sala Sudeste tinha de ficar *"na direita"*, não embaixo.

### Por que isso contraria o `.rsw`, e por que está certo assim

No 1º andar os portais foram para cima dos semicírculos de pedra, e o dono
aprovou. No 2º não dá: as salas têm **um arco só**, e ele quase nunca está na
parede que dá para a sala seguinte. A Sala Leste tem o dela no meio; a Sala do
Sul, embaixo. Seguir o arco ali é pôr o jogador para procurar o portal em
qualquer parede menos a que faz sentido.

O 2º andar passou a ter regra própria, `PORTAL_NA_PAREDE`, e o 1º e o 3º
continuam como estavam.

### A conta

O eixo dominante entre os dois centros escolhe a parede; a posição **ao longo**
da parede mira o centro da sala vizinha, presa dentro da caixa. Reproduz os
três exemplos do relato célula por célula:

| de → para | onde fica a próxima | portal |
|---|---|---|
| Sala Leste → Sala do Centro | a oeste | `159,77` |
| Sala Sudeste → Sala Leste | ao norte | `173,40` |
| Sala do Sul → Sala Sudeste | a leste | `113,25` |

**Mirar em vez de centralizar não é enfeite:** no Grande Salão Nordeste a
seguinte e a anterior estão as duas a oeste, e é a mira que separa os dois
portais em 51 células, um apontando para o norte e outro para o sul. Centrar
os dois teria posto um em cima do outro.

### E cada sala ganhou o portal de volta

*"Depois que tivermos os portais corretamente localizados podemos adicionar
mais um portal em cada mapinha, sempre levando pro nó anterior, para dar o
efeito de labirinto."* Foi feito: raio 2, na parede que dá para a sala
anterior. A primeira sala não tem volta; a última tem a escada no lugar da
ida, na parede oposta à de onde se veio.

São 20 portais no andar — dez de ida e dez de volta — contra 19 antes.

### O que sumiu junto, e é para decidir

O 2º andar **ficou sem portal de expulsão**. Os dois que existiam eram sorteio
nosso sobre os arcos, e os arcos deixaram de ser usados ali. O print do bRO do
2º andar não marcava nenhum, ao contrário do 3º, onde os dois estão marcados e
foram respeitados. Está em `PENDENCIAS.md`.


## Os pilares como régua, e o sinal que o mapa simétrico escondia (2026-09-02)

O 2º andar foi percorrido de novo e voltou com seis relatos idênticos: *"o
portal tá muito pra direita, fora da marcação"*, com a coordenada de cada
sala. Num deles o desvio foi quantificado — *"cerca de 6 células"* — e num
outro, *"esse ficou bem distante, não só algumas células"*.

### O erro

A conta que tira a célula da posição do modelo no `.rsw` estava com o sinal do
`z` invertido. A tabela de marcações saía **espelhada no eixo norte–sul**.

E ela passou por duas rodadas sem ninguém ver, porque o primeiro mapa em que
foi usada, o `force_map1`, **é simétrico de cima para baixo**: o conjunto
espelhado cai em cima de si mesmo, e só troca de que sala cada marcação é. Os
portais do 1º andar ficaram certos por acidente — e depois foram ditados à
mão, o que apagou o rastro de vez.

### A régua estava no mesmo arquivo

O `.rsw` traz 82 modelos de **pilar** no 1º andar e 72 no 2º, e pilar é célula
fechada no `.gat`. Testadas as quatro combinações de sinal:

| conta | 1º andar | 2º andar |
|---|---|---|
| `x/5+L/2`, `A/2−z/5` | 70 de 82 | 50 de 72 |
| `x/5+L/2`, `A/2+z/5` | **82 de 82** | **72 de 72** |
| `L/2−x/5`, `A/2−z/5` | 70 de 82 | 51 de 72 |
| `L/2−x/5`, `A/2+z/5` | 82 de 82 | 60 de 72 |

Os dois sinais de `x` empatam no mapa simétrico. **Foi o segundo mapa que
desempatou** — e é a lição que ficou registrada nas armadilhas: validar num
mapa simétrico não valida nada.

### Com a tabela certa, os seis relatos fecham

| sala | portal estava em | arco está em | desvio |
|---|---|---|---|
| Sala Oeste | `33,92` | `26,92` | 7 |
| Salão Noroeste | `56,130` | `50,132` | 6 — *"cerca de 6 células"* |
| Sala Central-Norte | `85,129` | `92,128` | 7 |
| Sala Central-Norte | `115,142` | `108,144` | 7 |
| Grande Salão NE | `159,180` | `160,178` | 2 |
| Grande Salão NE | `159,129` | `174,116` | 28 — *"bem distante"* |

### A regra final: a parede escolhe, o arco decide

A geometria continua escolhendo **qual parede** — é a regra que o dono ditou
e que reproduz os exemplos dele. O que mudou é que o portal agora **encaixa no
arco** daquela parede, em vez de parar na conta. Guloso: o par mais próximo
casa primeiro e arco não se repete.

Duas salas do 2º andar têm **um arco só e dois portais**, e nelas um dos dois
fica fora de marcação, por falta de marcação: a Sala Sudeste (o de ida, na
parede norte) e o Vestíbulo (a escada, na parede oeste). Não é engano da
ferramenta — é o que o mapa tem.

### E a chegada passou a depender de onde se veio

*"Venho do mapinha da direita, aterrizo no da esquerda, e nasço no meio dele
em vez de nascer no canto direito, como se tivesse acabado de atravessar."*

A chegada deixou de ser uma célula por sala e passou a ser **uma por
travessia**: sai da parede que dá para a sala de origem e anda para dentro até
achar célula andável a pelo menos quatro células de qualquer portal daquela
sala, descontado o raio. Quem vem do leste desembarca no leste.

Vale no 2º andar. No 1º os destinos foram ditados célula a célula e continuam
como estão; o 3º ainda usa a chegada por sala.


## Bio 4 entra, e o portal do 3º andar deixa de cuspir para fora (2026-09-02)

Duas coisas no mesmo pedido, e a segunda foi um achado do dono jogando:
*"percebi que colocamos monstros apenas de transclasse. Faltaram aqueles que
representam as novas classes."*

### Os sete de Biolaboratório 4

Estavam à mão, e com nome em português: `2221` Randel Lawrence, `2222` Flamer
Emul, `2223` Celia Alde, `2224` Chen Liu, `2225` Gertie We, `2226` Alphoccio
Basil e `2227` Trentini. Nível 141-142, de 205 mil a 479 mil de HP — mesmo
patamar dos seis de Bio 3 que já estavam lá.

Não foi preciso ir ao bRO: os IDs dele são os do rAthena, o que já tinha sido
provado nos de Bio 3, e o `lhz_dun04` do vendor traz a lista inteira.

**Os `G_*` de Bio 4 (2228 a 2234) ficaram de fora**, pela mesma decisão que
tirou os de Bio 3 em 2026-09-01: são os MVPs do andar, de 2 a 3 milhões de HP.

### A repartição, ditada

| andar | antes | agora |
|---|---|---|
| 1º | 246 de Bio 3 | igual |
| 2º | 238 de Bio 3 | 162 de Bio 3 (−31%) + 77 de Bio 4 + 4 Brutais |
| 3º | 150 heróis | 156 heróis + 182 de Bio 4 |

*"Segundo andar reduz 30% pra colocar esses novos nesses cerca de 30%. E no
terceiro andar só adiciona eles, na mesma quantidade que os outros."* É o que
está. São 827 monstros no labirinto, contra 634.

### O portal do 3º andar agora sobe

Os dois que o print do bRO marcava como saída — `100,12` e `92,138` —
deixaram de mandar para Malangdo e passam a devolver o jogador para a
**chegada do 2º andar**, `force_map2 25,25`. Quem tomba num deles perde o
caminho, não a sessão, e não paga pedágio de novo.

O 2º andar continua **sem portal de expulsão**, por decisão. Só o 1º ainda
tem, e são três.

### Uma consequência que o pedido não previa

Os sete de Bio 4 têm **oito drops cada**, e o 3º andar é o único sem
`nomobloot` — ele não pode ter, porque é o mapflag que mataria a Mente
Maligna junto. Então o 3º andar passou a ser fonte de todo o loot de Bio 4:
182 monstros largando o que largam em `lhz_dun04`.

Nos andares 1 e 2 isso não acontece — o mapflag continua lá.

Está em `PENDENCIAS.md`. As saídas, se incomodar, são clonar os sete com IDs
nossos e sem drop (o que não toca `lhz_dun04`) ou aceitar.


## A Mente deixa de ser drop para o labirinto poder ser sem drop (2026-09-02)

*"Sem drop. Precisamos manter isso, sem drop."* — resposta ao aviso de que o
3º andar tinha virado fonte do loot de Bio 4.

### O impasse

O `nomobloot` é o único jeito de tirar o drop **sem tocar no `mob_db`** — e
tocar no `mob_db` tiraria o drop em `lhz_dun03` e `lhz_dun04` também, que é a
armadilha do `Buy: 1` das lojas outra vez. Só que o mapflag mata **todo** drop
do mapa, a Mente Maligna inclusive.

Enquanto o 3º andar tinha só os seis heróis — cujo único drop **é** a Mente —
dava para deixar o andar sem o mapflag. Com os sete de Bio 4 lá dentro, cada
um com oito drops, não dava mais.

### A saída, e ela ficou melhor do que o arranjo anterior

`nomobloot` nos **três** andares, e a Mente entregue pelo **evento de morte**
dos seis heróis:

```
OnHeroiMorto:
    if (rand(100) < .MenteChance)
        getitem .MenteId, 1;
    end;
```

`rand(100) < 25` é 25% cravado — o `rand(100)` do rAthena devolve 0..99.

**Quem recebe é quem deu o último golpe:** o `mob_npc_event_type` deste
servidor é 1 (`conf/battle/monster.conf:266`), a mesma regra do Corredor
Fantasma. E mochila cheia larga no chão, o que aqui é o comportamento certo.

**O evento não passa pelo mapflag**, e isso foi conferido no código antes de
escrever: o `nomobloot` guarda só o bloco de drop (`mob.cpp:3253`), enquanto o
`npc_event` roda mais adiante (`mob.cpp:3594`), independente.

### A regra do labirinto ficou uma só

Antes eram duas: "sem drop nos andares 1 e 2, e o 3º fica com drop porque
precisa da Mente". Agora é **sem drop em lugar nenhum**, e a Mente é a única
coisa que sai de lá — por construção, não por exceção.

### E o número mudou de casa

A chance de 25% morava em `db/guerra/mob_db_guerra.yml`, como `Rate: 2500` nos
seis. **O override foi removido**: com o mapflag no ar ele não alcançava mais
nada, e deixar os 25% nos dois lugares seria a segunda fonte que diverge da
primeira. Hoje o número está em `MENTE_CHANCE`, no
`ferramentas/monta_labirinto.py`, e o arquivo do `mob_db` guarda a nota
dizendo para onde ele foi.

## A Mente cai de 200 para 20, e os nove [MEGA] ganham nome (2026-09-02)

Primeiro relato de jogo das duas Valquírias de Malangdo, e ele trouxe dois
defeitos de naturezas diferentes: um número errado e um nome ausente.

### O preço em Mente: 20 nas seis primeiras, 200 nas quatro últimas

Pedido do dono, jogando: *"a quantidade está errada, não são 200 por
tentativa, são 20 por tentativa pra todos menos pra alguns, que são 200: pra
Vara Morta, Vestes de Bispo, Mangual Ogro e Elmo Alado Dourado"*.

**Isso troca a fonte, e é o interessante do caso.** A tabela de 2026-09-01
seguia a **notícia** do bRO de 2024, que dá 200 para tudo (300 nas Patas de
Raposas) nos dois servidores. Os quatro itens que o dono nomeou são
exatamente os **quatro últimos** da tabela — e são exatamente os quatro que a
**coluna Valhalla do wiki** cobra a 200, deixando os seis primeiros a 20. Ou
seja: o pedido, que veio da tela e não de documento nenhum, escolheu a outra
fonte inteira, coluna por coluna.

Quem decide entre duas fontes que discordam é a nossa economia, e não a idade
do documento — as lojas de Prontera vendem e recompram a 1 zeny justamente
para não fabricar dinheiro (§4.16). O cabeçalho do arquivo foi reescrito para
dizer isso, porque ele afirmava o contrário por extenso.

**Uma divergência ficou por escrito**, no cabeçalho e aqui: o wiki cobra
**30** nas Patas de Raposas (índice 2, o Sapato Infernal), a única das seis
fora dos 20. O pedido foi "20 para todos menos" os quatro, e é o que está na
tabela. Se a intenção era espelhar o wiki inteiro, a linha a mudar é essa, e
só ela.

### Os nove [MEGA] não existiam no cliente

O segundo relato foi *"o nome dos novos itens no NPC está em inglês, no
diálogo"*, e a causa tem duas metades que se somam.

O menu da Valquíria Mega é montado em laço com `getitemname()`, que lê o
`Name` do **servidor**. Cinco dos dez `[MEGA]` são itens do vendor e estavam
com o nome em inglês lá (`Awakened Robe of Worshiper` e irmãos). Os outros
quatro são nossos e já nasciam em português — por isso metade do menu estava
certa, o que torna o defeito mais fácil de ler como "alguns itens".

E o `Name` do servidor **sai do cliente**: quem o sincroniza é o
`ferramentas/nomes_pt_item_db.py`, que copia o nome que o `itemInfo.lua`
desenha. Ele não tinha o que copiar — **os nove `[MEGA]` estavam fora do
`itemInfo.lua`**, os cinco do vendor inclusive. Na mochila eles apareceriam
sem nome e sem ícone; no diálogo, em inglês. Um sintoma só, duas tabelas.

A cura foi a de sempre, e estava no disco: o `iteminfo_new.lub` do bRO tem os
nove, **com o nome oficial em português e a descrição**. Os nove entraram na
lista do `ferramentas/completa_iteminfo.py` (que é versionado; o
`itemInfo.lua` não é) e de lá para o cliente:

| Id | nome |
|---|---|
| 22245 | `[MEGA] Botas Espaciais` |
| 470047 | `[MEGA] Patas de Raposas` |
| 450181 | `[MEGA] Vestimenta de Seda` |
| 450158 | `[MEGA] Robe Gelado` |
| 450286 | `[MEGA] Vestes de Cardeal` |
| 810012 | `[MEGA] A.R.-89` |
| 510065 | `[MEGA] Totsuka` |
| 550074 | `[MEGA] Vara` |
| 590042 | `[MEGA] Mangual do Demônio` |

Depois o `nomes_pt_item_db.py` levou os cinco do vendor para o `item_db`, e o
diálogo passou a falar português nos dez destinos.

**A arte do 810012 faltava**, e só dele — os oito outros já tinham os quatro
arquivos. Veio do GRF do bRO por `instala_visual.py`, e o `valida_visual.py`
fecha em 4 de 4. Os quatro `[MEGA]` de arma herdam o `ClassNum` do original
(18, 31, 69 e 62), então o visual equipado já estava coberto.

### O que veio de brinde, e por que ficou

A passada do `nomes_pt_item_db.py` também sincronizou **31 itens de
`item_db_usable.yml`** que estavam parados desde 2026-08-28 — as dezoito
Caixas de Primeiros Socorros, as poções de evento e o Leite Fresco. São
entradas de cliente que entraram naquele dia sem a sincronia do servidor
depois. Ficaram: é a §4.9 sendo fechada, não escopo novo — com elas fora, a
mochila diria "Caixa de Primeiros Socorros (5)" e todo NPC diria "First aid
Box (5)".

### O que falta

O `itemInfo.lua` e os quatro arquivos de arte do 810012 moram em
`C:\GuerraDoEmperium\cliente\` e **não chegam ao jogador pelo deploy**
(§4.18). O patch está anotado no `PENDENCIAS.md` §1ab, junto com o resto do
Labirinto, que ainda não foi visto em jogo por inteiro.
## O fantasma não subiu por dois bits, e o segundo era pior (2026-09-02)

A primeira execução do `ferramentas/implanta_fantasma.sh` morreu no passo 4 de
6, depois de instalar as dependências de build, clonar os 233 MB do openkore e
compilar o `XSTools.so`:

```
runuser: failed to execute /opt/guerra-do-emperium/ferramentas/openkore/instala.sh: Permission denied
```

### O bit de execução, pela terceira vez

Os três arquivos do fantasma entraram no git como `100644` — a ferramenta de
edição do assistente grava assim, e os nove `.sh` mais velhos de `ferramentas/`
estão `100755`, então a divergência não salta aos olhos num `ls`. Dois dos três
não deram sinal: o `implanta_fantasma.sh` é chamado como `bash <arquivo>` e o
`configura_fantasma.sh` viaja pelo *stdin* do `ssh`, e nenhuma dessas formas
consulta o bit. Quebrou o terceiro, o `instala.sh`, que é o único invocado pelo
caminho puro — e de dentro de outro script, nunca por gente.

É a mesma armadilha de 2026-08-14 (vendor) e 2026-08-17 (`publica_patch.sh`),
com um agravante novo em cada ponta: a falha chega **depois** de todo o
trabalho caro, e a conferência que a entrada antiga prescrevia — *"só se
descobre ao rodar o script pela primeira vez de outra máquina"* — não alcança
um arquivo que não tem primeira vez.

Por isso a saída foi dupla. O `git update-index --chmod=+x` nos três, que é o
que conserta o arquivo para quem o chame direto; e os dois chamadores
(`configura_fantasma.sh` §4 e `atualiza_servidor.sh` §6b) passaram a invocá-lo
como `como_jogo bash <caminho>`, tirando o bit do caminho crítico de vez.

### E o aviso amarelo que ninguém devia ter deixado passar

Vinte linhas antes do erro, o mesmo log dizia:

```
!! nao consegui ler o commit do servidor - seguindo assim mesmo
```

A causa é o git recusando árvore de outro dono: o `/opt/guerra-do-emperium` é
do `ragnarok`, o `ssh` entra como root, e o `rev-parse` sai 128 com *detected
dubious ownership* sem imprimir commit nenhum. O `2>/dev/null` engolia a
explicação. Corrigido com o mesmo `runuser -u ragnarok` que todo comando de git
do `atualiza_servidor.sh` já usava.

**O que esse aviso escondia é o achado de verdade:** o servidor estava em
`694f38d`, **três commits atrás**, e os três eram exatamente do fantasma —
`configura_fantasma.sh`, o `LEIAME.md` e o `control/config.txt`. A comparação de
commits do `implanta_fantasma.sh` existe para barrar isso, e teria barrado; ela
não falhou, apenas nunca chegou a ser consultada. Se o bit de execução
estivesse certo, a instalação teria terminado com "ok" aplicando um
`config.txt` velho — que é a falha calada que aquela trava foi escrita para
impedir.

A lição ficou registrada no `ARMADILHAS-INFRA.md` como regra de sonda:
degradar para *"seguindo assim mesmo"* só é honesto quando o que se perdeu é
dispensável. Se a leitura é o que arma uma trava, o certo é o erro aparecer e o
script parar.

### E aí o fantasma subiu — menos o personagem

Feito no mesmo dia, nesta ordem: deploy completo (autorizado pelo dono, que era
o único jogador on), depois o `implanta_fantasma.sh` duas vezes.

**As duas passadas são o desenho, não um tropeço.** O `438d931` da sessão do
Windows fez o passo 6/7 criar a conta a partir do `/etc/guerra/fantasma.txt`, e
o script se recusa a criar conta de produção com a senha de exemplo — então a
primeira passada escreve o arquivo e para, a segunda cria. No meio entra a
senha de verdade.

Resultado em produção: openkore clonado e compilado, delta aplicado, link do
segredo resolvendo, unit escrita e `disabled`, e a conta:

```
account_id 2000037    userid fantasma    group_id 20    pincode 4728
```

O hash foi conferido dos dois lados por fora do script — `md5sum` da senha do
arquivo contra a coluna `user_pass` —, que é a premissa inteira do desenho de
fonte única. Casam.

**O `account_id` de produção não é o 2000002 do README.** Aquele é o da máquina
de DEV; a coluna é `AUTO_INCREMENT` e cada banco dá o próximo número dele. O
README foi acertado para trazer os dois lado a lado, porque procurar o 2000002
em produção não acha nada.

### Um defeito encontrado na leitura, antes de o SQL tocar o banco

O commit `438d931` avisava, com todas as letras, *"NAO TESTADO CONTRA UM
BANCO"*. Lendo o passo 6/7 antes de rodá-lo apareceu a guarda da senha:

```sh
case "$SENHA" in
    *\'*|*\*) erro "... tem aspa simples ou barra invertida" ;;
esac
```

O `\*` torna o asterisco **literal**, então o padrão casa *"qualquer coisa
terminada em asterisco"* — recusava um asterisco no fim (inofensivo em SQL) e
**aceitava barra invertida em qualquer posição**, que é exatamente o caractere
que quebraria o `INSERT` montado por concatenação. O oposto do que o comentário
prometia, e do que o próprio autor quis escrever.

Medido antes de corrigir:

```
[a\b]     -> aceita     <- deveria recusar
[senha\x] -> aceita     <- deveria recusar
[fim*]    -> RECUSA     <- não precisava
```

Corrigido para `*\\*`. É a §4.17 do `CLAUDE.md` em miniatura — o comentário
descrevia uma regra que o código não implementava —, e vale registrar o que a
achou: **ler o trecho que o commit disse não ter testado, antes de deixá-lo
tocar produção.**

### O que falta, e por que não sai do Mac

O **personagem Renegado**. Ele não se cria por SQL — precisa do cliente, que é
do Windows. Os três passos (criar, ajustar o `char N`, dar os dois insumos
infinitos) ficaram na §9 do `IMPLANTACAO.md`, item 7. O serviço está `disabled`
de propósito: o start é do dono, com a arena vazia.

## O Emperium era sagrado, e por isso não sentia o sagrado (2026-09-02)

Relato do dono: *"Emperium não tá tomando dano de sagrado. Emperium precisa
não ter elemento, elemento neutro."*

Não era dano baixo — era **zero**, e a conta fecha exatamente.

O Emperium é planta (os quatro `Modes: Ignore*` que o rAthena dá ao 1288), e
planta leva **1 de dano por golpe**; é por isso que ele tem `Hp: 100` no
`mob_db` e cai em cem pancadas. O que quase ninguém espera é que esse 1 ainda
passe pela tabela de elementos: o `battle_calc_attack_plant`
(`src/map/battle.cpp:4980`) tem um bloco só para o `MOBID_EMPERIUM` que chama
`battle_attr_fix` com o elemento da **arma** contra o `def_ele` dele. Com o
Emperium em `Element: Holy` / `ElementLevel: 1`, o `db/re/attr_fix.yml` dá
`Holy → Holy` = **0%**, e `1 × 0% = 0`: Aspersio, Conversor Sagrado, flecha
sagrada e arma de elemento sagrado tiravam literalmente nada. O veneno caía
na mesma armadilha por truncamento — 75% de 1 é 0.

**A correção é um override de três linhas** em
`rathena/db/guerra/mob_db_guerra.yml` (Id 1288, `Element: Neutral` /
`ElementLevel: 1`), pela lei da §2 — o arquivo do rAthena não se toca, e o
`parseBodyNode` do `mob_db` só escreve os campos presentes no nó
(`src/map/mob.cpp:5332` e `:5354`), então todo o resto do 1288 continua vindo
do vendor. O **porquê** de cada escolha, inclusive por que o nível 1 é o
melhor dos quatro (Neutral nível 1 resiste ao Ghost com 90%; os níveis 2, 3 e
4 resistem com 70%, 50% e 25%), está no cabeçalho do próprio arquivo.

**O que isso exige em jogo:** `@reloadmobdb` **não basta**. O Emperium já
plantado copiou o status no momento do spawn — ele é um dos monstros que
ganham `base_status` próprio (`src/map/status.cpp:2802`) — então o que estiver
no mapa continua sagrado até nascer de novo, no `OnAgitStart` seguinte
(`npc/guild/agit_main.txt:97`).


## As seis Almas de classe deixam de ser lixo permanente na mochila (2026-09-02)

Pedido do dono: *"poder jogar fora as Almas de classe: Alma de Espadachim
6814, Alma de Mercador 6815, Alma de Gatuno 6816 e assim por diante (a todas
as almas)"*.

São seis, e não mais: 6814 Espadachim, 6815 Mercador, 6816 Gatuno, 6817 Mago,
6818 Arqueiro e 6819 Noviço. São a moeda do Laboratório Pesadelo — o
`npc/re/merchants/nightmare_biolab.txt` as consome no `callsub S_Make` de cada
peça, e a lista fechada está na linha 576 daquele arquivo, num `setarray` com
os seis ids. Não existe alma de classe fora dessa faixa; o `Soul_Of_Tree`, o
`Soul_Of_Ahat` e os quinze `Soul_Of_*` do baú de clã são outra família.

O vendor as trazia com sete travas de uma vez: `NoDrop`, `NoTrade`, `NoSell`,
`NoCart`, `NoGuildStorage`, `NoMail` e `NoAuction`. A única que faltava era
`NoStorage` — ou seja, a alma que o jogador não ia gastar tinha exatamente um
destino no mundo, o armazém, e ocupava espaço lá para sempre.

**A correção mexe em um campo só.** `db/guerra/item_db.yml` ganhou seis
overrides com `Trade:` / `NoDrop: false`, e as outras seis travas ficam de pé:
a alma continua sem poder ser vendida, trocada, posta no carrinho, mandada por
RoDEX ou leiloada. Quem recusava o descarte era o `pc_candrop`
(`src/map/pc.cpp:11365`), que delega ao `itemdb_isdropable` — e ali só o bit de
drop é consultado.

**O `false` tinha de ser explícito.** O `parseBodyNode` do item_db lê o nó
`Trade:` campo a campo (`src/map/itemdb.cpp:938`): cada trava tem seu próprio
teste de existência, e o ramo que zera só roda quando o item **não existia
antes**. Omitir a linha num override, portanto, não apaga a trava do vendor —
ela sobrevive intacta. É o mesmo `false` explícito que os overrides de
`Locations:` já exigiam (CLAUDE.md §4.14).

Uma nota sobre o teste, porque desta vez ele vale: o `Override` das almas é 100
e a conta de teste é grupo 99, então **ela sentia a trava** — antes desta
mudança nem o GM de teste conseguia largar uma alma no chão. Não é o falso
negativo da §4.7.

Recarregador: `@reloaditemdb`. Não é `@reloadscript` — o que mudou foi campo de
item, e nenhum NPC foi tocado.

## A porta da arena desce duas células a oeste e uma ao sul (2026-09-03)

Pedido do dono: *"o NPC 'Arena de Combate' de Prontera deve ir 2 células pra
esquerda e uma pra baixo"*. De `prontera 147,180` para **`145,179`**, facing
inalterado (6, leste).

**A célula de destino foi conferida antes**, com
`ferramentas/confere_celula.py prontera 145,179`: andável, as nove células em
volta livres, e nenhum NPC — do rAthena ou nosso — a menos de três células. Isso
importa porque a porta é o caso que já custou um `disablenpc` em 2026-08-12:
NPC empilhado em célula ocupada não dá erro nenhum, só some por baixo do outro.
Como 145,179 também é vazia, **nada volta a ser desligado**.

**O que ela deixa de dividir.** A porta e o Placar da Arena (`142,180`)
dividiam a fileira `y=180` desde 2026-08-13; agora a porta ficou uma célula ao
sul, três a leste do Placar. E ela passa a ser o NPC mais próximo do Placar,
tomando o lugar do Clan Helper do rAthena (`138,183`) — os dois cabeçalhos
foram acertados.

**A marca do mini-mapa é a metade funcional que não está no arquivo da porta.**
O Guia de Prontera carrega as trinta marcas num `setarray .marcas$[]`, e a
segunda delas era `"147 180"` — o link "Arena de Combate" do menu dele leva a
essa coordenada. Coordenada velha ali não dá erro: pinta o ponto na célula
errada e o jogador anda até um lugar sem NPC. É a §4.11 outra vez, do lado dos
dados: quem move um NPC tem de procurar quem mais escreveu a coordenada dele.

### O que ficou

| arquivo | o quê |
| --- | --- |
| `rathena/npc/guerra/arena_de_combate.txt` | a linha do NPC e o cabeçalho (a seção "Onde", a terceira mudança de célula, a distância até o ponto de retorno e o comentário do `OnInit`) |
| `rathena/npc/guerra/guia_de_prontera.txt` | `"145 179"` no `.marcas$[]` — **funcional** — e o cabeçalho |
| `rathena/npc/guerra/honra_de_combate.txt` | o cabeçalho do Placar: a distância até a porta e qual é o NPC mais próximo |
| `rathena/npc/guerra/scripts_guerra.conf` | os dois parágrafos do índice narrado |
| `ferramentas/traduz_ptbr.py` | o comentário da entrada de `pvp_n_1-5` |
| `PENDENCIAS.md` | as três menções à coordenada |

Recarregador: `@reloadscript`. Vai por deploy e só por deploy — não há nada de
cliente aqui (`RECEITAS.md` §0).

---

## As quinze Armas Brutais ganham a cova que o bRO sempre deu (2026-09-03)

Pedido do dono: *"hoje as vendidas em Prontera não têm slot, precisamos trocar
pelas versões com slot"*. **Não havia versão com slot para trocar** — e é essa
a parte que vale registrar, porque o pedido descreve o remédio de RO clássico
(a peça com cova é *outro* item, `Sword_` e não `Sword`) e aqui esse item não
existe de nenhum lado.

Procurei "Brutal" nos 18845 itens do `iteminfo_new.lub` do bRO: **quinze**.
Procurei `Blut_*` no nosso `item_db`: **quinze**, os mesmos IDs. Não há segundo
ID para nenhuma delas. O que o `estado_item.py` mostrou é que a divergência era
outra, e estava nos dois lados de casa:

```
=== 1328  Machado Brutal
  servidor  db/re/item_db_equip.yml      Blut_Axe  Right_Hand
  cliente   itemInfo.lua                 "Machado Brutal"  0 cova(s)
  bRO       iteminfo_new.lub             "Machado Brutal"  1 cova(s)
```

**Nas quinze, o bRO dá `slotCount = 1` e nós dávamos 0 — no servidor e no
cliente.** A família nasceu sem cova aqui por herança: as duas que o vendor já
tinha (1328 Machado e 32014 Lança) são sem cova no rAthena, e as treze que
escrevemos em 2026-08-01 foram moldadas nelas, campo por campo. O cabeçalho da
linha Brutal chegou a registrar *"Todas: peso 0, nível de arma 4, nível mínimo
100, sem slot"* — descrevia fielmente o que tínhamos, e o que tínhamos estava
errado.

Então não houve troca de ID: as quinze passaram a ter a cova que sempre
tiveram lá.

### A cova mora em dois lugares, e um deles é o cliente

É a `CLAUDE.md` §4.9 outra vez, e a divisão não é a que se imagina:

| metade | onde | o que decide |
|---|---|---|
| servidor | `Slots:` no `item_db` | se a carta **entra** — a janela de encaixe é montada em `clif_use_card` a partir do `slots` |
| cliente | `slotCount` no `itemInfo.lua` | se o nome mostra **`[1]`** — o cliente desenha o sufixo sozinho, sem perguntar nada |

Só o servidor deixaria um item que **aceita carta e não parece aceitar**: o
jogador não tenta, e nada dá erro. Só o cliente seria pior — prometeria uma
cova que o servidor recusa. As duas entraram no mesmo dia.

Do lado do servidor, treze são nossas e receberam `Slots: 1` direto; as duas do
vendor (1328 e 32014) receberam **override de campo único** na seção de
OVERRIDES do `db/guerra/item_db.yml`, que é a única forma de mexer em item do
rAthena sem editar arquivo deles (§2). Aqui a armadilha do `Locations` — que é
OR e não atribuição — não pega: `Slots` é escalar, e o `parseBodyNode` mantém
todo o resto da entrada do `db/re/` (Attack 150, WeaponLevel 4, EquipLevelMin
100, o `Script:` com o `bUnbreakableWeapon`).

### A ferramenta nova, e por que a lista dela é escrita à mão

O lado do cliente virou `ferramentas/ajusta_covas_do_cliente.py`, que lê o
`Slots:` do servidor e grava o `slotCount` do `itemInfo.lua`. **A fonte da
verdade é o servidor, não o bRO** — o nosso `item_db` pode discordar do bRO por
decisão nossa, e o que o jogador precisa é que a tela diga o que o servidor
faz.

Ele não podia ser o `completa_iteminfo.py`: aquele importa a entrada inteira de
um item que o cliente **não tem**, e por desenho não toca entrada existente.
Aqui o que se muda é um campo de entrada que já existe. Resultado medido: 15
trocas de **um byte cada** (`0` → `1`), arquivo do mesmo tamanho, e o
`luac.exe -p` do ROenglishRE compilando os 22 MB depois.

A lista de IDs é uma constante escrita à mão, e a alternativa foi medida antes
de ser descartada: varrer as vitrines e alinhar tudo daria **16 divergências**
entre os 3396 itens de loja, e em **treze** delas quem promete a cova é o
cliente enquanto o servidor não a dá. Alinhar essas treze tiraria da tela uma
cova que o jogador já vê — decisão do dono, não consequência de script. Ficaram
no `PENDENCIAS.md` §1ac, com os dois consertos possíveis nomeados.

Uma delas está na vitrine ao lado das Brutais: a **Cauda Arco-Íris (26163)**, no
mesmo Senhor das Armas, mostra `[2]` e o servidor dá 1.

### O que ficou

| arquivo | o quê |
| --- | --- |
| `rathena/db/guerra/item_db.yml` | `Slots: 1` nas treze nossas, override de `Slots` para 1328 e 32014, e o cabeçalho da linha Brutal reescrito |
| `rathena/npc/guerra/mercado_contemporaneo.txt` | o parágrafo da vitrine: por que nenhum ID mudou, e onde moram as duas metades |
| `ferramentas/ajusta_covas_do_cliente.py` | **novo** — o lado do cliente, com `--conferir` |
| `ferramentas/LEIAME.md` | a seção da ferramenta |
| `CLAUDE.md` | §4.9 ganhou o quarto caso vivo |
| `ARQUITETURA.md` | §4 ganhou "A COVA de um item vive em 2 lugares" |
| `PENDENCIAS.md` | §1ac — conferir em jogo, o patch, o deploy e as 16 divergências |
| `C:\GuerraDoEmperium\cliente\...\itemInfo.lua` | **fora do git** — 15 bytes, reproduzível pelo script |

Recarregador: `@reloaditemdb` — e **fechar e reabrir o cliente**, sem o que o
nome continua sem o `[1]` com o servidor já certo. Vai por deploy **e** por
patch: as duas metades têm destinos diferentes (`RECEITAS.md` §0).

A metade do cliente saiu no mesmo dia: **patch 0018, "Cova nas quinze Armas
Brutais"** — 22,87 MB crus, 2,45 MB no zip, um arquivo só
(`SystemEN/LuaFiles514/itemInfo.lua`). Zip primeiro, `lista.txt` depois, que é
a única coisa delicada daquele caminho. Falta o deploy do `item_db.yml`, e a
defasagem nesse intervalo é inofensiva por desenho: quem receber o patch antes
do deploy vê o `[1]` e a carta ainda não entra — o contrário é que deixaria a
cova invisível.

## O Festival de Brasilis existe, e as quatro Ligas com ele (2026-09-05)

Brasilis era uma cidade de passagem: o mapa está no GRF desde sempre, a
Teletransportadora leva lá desde o primeiro dia, os monstros já têm nome em
português — e **as 40 peças do conjunto do Festival não tinham como ser
obtidas**. Existiam no `item_db`, existiam no cliente, com arte completa, e
nenhum NPC, drop, `item_group` ou tabela de encante citava uma só delas.

O levantamento que abriu a sessão respondeu por que: o **Festival da
Diversidade de Brasilis é evento exclusivo do bRO**, e o rAthena nunca o
implementou — nem no master. O vendor herdou as peças soltas e mais nada.

### O que o bRO tinha, e em que estado chegou aqui

Duas coisas com o mesmo nome, e as descrições do bRO as separam. O **evento**
divide a cidade em quatro Ligas — Fogo, Água, Vento e Terra —, cada uma com um
`Cartão da Liga` (25482–25485) e uma `Insígnia do Orgulho` (25486–25489). O
**conjunto** é a recompensa: 17 peças nomeadas na descrição do Cubo de Refino
de Brasilis (102590), organizadas nos mesmos quatro elementos, com as armas
batizadas de orixás — Xangô (fogo), Oxum (água), Iansã (vento) e Oxóssi
(terra).

O inventário, medido item a item:

| | estava no servidor | estava no cliente |
|---|---|---|
| 4 chapéus, 4 escudos, 4 capas, sapatos, bracelete | sim | sim, arte ok |
| 18 armas e 2 anéis (Oxum, Iansã, Oxóssi) | sim | sim, arte ok |
| **6 armas de Xangô** | **não, em item_db nenhum** | sim (2 sem arte) |
| 8 itens de Liga/Insígnia (`_BZ`) | sim, em inglês com `!todo` | **não** |
| 4 cartas "Poder de <orixá>" (`_BR`) | sim, em inglês com `!todo` | **não** |

Ou seja: três dos quatro elementos tinham arma e o **fogo não tinha**.

### O que entrou

**As seis armas de Xangô**, em `db/guerra/item_db.yml` — 13143, 16066, 18152,
26113, 28727 e 32006. A estrutura é espelhada da irmã de Oxum, que é a mesma
arma noutro elemento; os números de combate saem da descrição do bRO, que é
palavra por palavra a mesma fora o elemento. Bate em Água e Terra, e nas raças
Inseto e Humanoide, como a descrição promete — **`RC_DemiHuman` e não
`RC_Player_Human`**, para as seis não ficarem sozinhas com +30% contra jogador
no +9.

**O `Name` em português dos 12 itens** que estavam em inglês no vendor, por
override no mesmo arquivo. Não foi com o `nomes_pt_item_db.py`: aquele é
tudo-ou-nada e hoje acusa 16755 trocas pendentes nos três `item_db` — trabalho
inteiro, de outra sessão.

**As quatro barracas de troca**, em `npc/guerra/barters_guerra.yml`, 42 linhas.
Barter e não `itemshop` pelo motivo de sempre: a Insígnia é `NoSell`, e o
`itemshop` passa a moeda por `pc_can_sell_item`.

**O NPC**, `npc/guerra/festival_de_brasilis.txt`: a Mãe de Santo em
`brasilis 205,222` e um motor de caçada flutuante. A célula foi conferida no
`map_cache.dat` antes — o `.gat` do nosso GRF está cifrado e o `grf.py` recusa,
mas o servidor tem a mesma grade.

**A Capa Grandiosa (20747) no Capeiro de Prontera**, e é o achado de brinde da
sessão. O cabeçalho do `mercado_contemporaneo.txt` afirmava desde 2026-08-04
que *"a família existe, mas não tem terra. São três, e o terceiro é gelo"* — e
a capa de terra existe, com arte 4/4, no vendor e no cliente. A Mística tinha
entrado *"no lugar"* de uma peça que nunca faltou. É a §4.17 outra vez, do lado
do fato: comentário não é trava.

### As decisões do dono, nesta sessão

Três, todas em 2026-09-05: a mecânica é **caçar e trocar por insígnia** (e não
missão nem caixa); o escopo é **tudo** (armas, cliente, arte, NPC e capa); e
**trocar de Liga é livre**, com a Liga decidindo qual insígnia cai. A última é
o que faz os quatro grupos existirem em vez de serem quatro cores da mesma
coisa: quem quiser os quatro conjuntos passa pelas quatro Ligas.

### O que custou leitura de código, e o que ficou na lista de armadilhas

O drop depende de `OnNPCKillEvent` disparar para o Boitatá, e a leitura direta
diz que não dispara: as 74 linhas de `boss_monster` do vendor terminam em `,0`
ou `,1`, o quinto campo do spawn **é** o `eventname`, e mob com evento próprio
não roda o evento global. Salva uma guarda de comprimento três arquivos
adiante — o `mob_spawn_dataset` só copia evento com 4 caracteres ou mais
(`mob.cpp:486`). Está na §5 e no `ARMADILHAS-SCRIPT.md`.

A Bênção do Orixá é o único lugar que usa as quatro cartas de encante, e é o
único caminho arriscado do arquivo: `delitemidx` + `getitem2` perde vínculo,
grau e opção aleatória. Por isso o NPC **recusa** Bracelete com qualquer uma
dessas três coisas, em vez de tentar e destruir.

E duas linhas de `bonus bUnbreakableWeapon` foram escritas e depois apagadas: a
Clava e o Cetro prometem "Indestrutível em batalha", mas o `skill_break_equip`
(`skill.cpp:1973`) isenta maça e cajado **por tipo de arma**, com bônus ou sem.
É o mesmo motivo pelo qual o `marca_indestrutiveis.py` deixa 241 armas de fora.

### Estado

O servidor local reiniciou sem um erro de parse nos quatro arquivos novos, e as
duas travas passam: `zera_revenda_das_lojas.py --conferir` diz OK nas 23 lojas
(1775 itens, a Capa Grandiosa entre eles), e `marca_indestrutiveis.py
--conferir` continua nos mesmos 30, sem acusar nenhuma das seis armas novas.

A metade do cliente saiu no mesmo dia: **patch 0019, "Festival de Brasilis"** —
21 arquivos, 23,00 MB crus, 2,50 MB no zip (o `itemInfo.lua` mais a arte de
cinco itens: as três insígnias que faltavam e o Arco e o Punhal de Xangô). Zip
primeiro, `lista.txt` depois.

**Nada disto foi visto em jogo**, e o deploy não saiu — os dois estão no
`PENDENCIAS.md`.

## O jogador recusado, e a trava que passou a punir a conta (2026-09-05)

Um jogador relatou que ao tentar entrar recebia **"Rejected from the Server
(3)"**, enquanto os outros entravam normalmente. O diagnóstico saiu do
`loginlog` de produção, e a resposta não era a que o relato sugeria.

### O que o banco contou

O IP era `179.113.122.223`, dono de duas contas criadas pelo site em 30 e
31/08 — `lucas7679` (2000035) e `lucas9094` (2000036). A linha do tempo:

| Quando | O quê |
|---|---|
| 02, 03 e 04/09 | seis logins bem-sucedidos nas duas contas, o último em 04/09 20:58 |
| 05/09 13:09–13:12 | sete `Incorrect Password` seguidos, alternando entre as contas |
| **05/09 13:16–13:17** | **sete `ip banned`** — é aqui que ele viu o erro 3 |
| 05/09 13:19–13:43 | mais seis `Incorrect Password` |

Ou seja: **ele não estava bloqueado; a faixa dele estava**, pelo ban dinâmico
do próprio rAthena, disparado pelas tentativas dele. Quando o relato chegou,
o ban de cinco minutos já tinha expirado — a `ipbanlist` estava vazia.

As outras quatro causas de erro 3 foram descartadas com dado, e todas de uma
vez: nenhuma conta com `state != 0`, `new_account: no` em produção,
`use_dnsbl: no`, e as 36 contas do servidor **todas** em MD5 (nenhuma sobrou
em texto puro desde a conversão de 2026-08-14).

O que sobrou em aberto é a senha, não o ban: as duas contas pararam de aceitar
a senha no mesmo dia, depois de quatro dias entrando. Fica no `PENDENCIAS.md`,
junto com os dois defeitos do site que produzem exatamente isso.

### As duas coisas erradas, e elas eram independentes

**A primeira era o alvo.** O `ipban_log` (`ipban.cpp:71`) contava as falhas
por IP e inseria na `ipbanlist` a faixa `x.y.z.*` — o /24 inteiro, até 254
endereços. Quem caísse nela levava a recusa **antes de o login ser lido**: não
importava a conta, a senha, nem se a pessoa tinha acabado de chegar. Num
provedor brasileiro, vizinho de rua e celular na mesma saída NAT dividem esse
/24.

**A segunda era a mensagem**, e é a que fez o relato chegar errado. *"Rejected
from the Server (3)"* não diz que é o IP, não diz por quanto tempo, e não é a
mesma frase que aparece quando a senha está errada — do lado de lá parece
conta banida. Ele achou que tinha sido bloqueado.

### A decisão do dono

Trocar o alvo: **sete senhas erradas suspendem AQUELA conta por 15 minutos**,
e o ban automático de IP sai. As três decisões que vieram junto — punir a
conta, expirar sozinha em 15 minutos, e não mexer na conta do jogador — estão
na §4.23 do `CLAUDE.md`, que é onde a regra passou a morar.

### Como ficou

`src/custom/trava_de_conta.hpp` conta as erradas por conta, em memória, numa
janela de cinco minutos, e no limite grava `unban_time = agora + 15min`. Usar
o `unban_time` — o campo que o `@block`/`@ban` já usa — deu três coisas de
graça: o `login_mmo_auth` já o testa e devolve o **erro 6**, que é a única
recusa que o cliente desenha **com data**; o char e o map-server já o
respeitam; e não houve coluna, tabela nem migração.

Três guardas que o desenho exigiu, e nenhuma é decorativa:

- **nunca encurtar bloqueio existente** — o campo é o mesmo do GM, e escrever
  por cima apagaria o castigo dele;
- **a conta de sexo `S` fica de fora** — é com ela que o char e o map-server
  se conectam ao login, pelo mesmo caminho de autenticação; sem a guarda, sete
  chutes contra um nome adivinhável derrubariam a ligação entre os servidores;
- **acertar a senha zera a contagem** — senão quem erra três vezes hoje e
  quatro amanhã acabaria suspenso sem nunca ter errado sete seguidas.

Os enxertos ficaram em dois arquivos do vendor, os dois na tabela da §2. E um
deles é **substituição**, a segunda do projeto: o `logclif_auth_failed`
calculava a data do desbloqueio e a jogava fora, copiando `""` para o pacote.
Sem essa correção a trava não teria como se explicar — o `%s` do erro 6 sairia
vazio, e o jogador saberia que está bloqueado sem saber até quando.

### O cliente passou a explicar a regra antes de ela morder

Pedido do dono na mesma sessão. O login-server não manda texto: o pacote
`AC_REFUSE_LOGIN` leva um código, e quem escolhe a frase é o
`msgstringtable.txt` — que é **nosso**. Três frases reescritas, em cp1252, sem
mexer na contagem de linhas (4023, e mexer nisso deslocaria todos os ids):

| id | antes | agora |
|---|---|---|
| 7 | *Incorrect User ID or Password. Please try again.* | Usuário ou senha incorretos. **Após 7 tentativas erradas a conta fica suspensa por 15 minutos.** |
| 9 | *Rejected from Server.* | Acesso recusado pelo servidor. Se continuar, fale com a administração. |
| 449 | *You are prohibited to log in until %s.* | Sua conta está suspensa até %s. Isso acontece após 7 senhas erradas seguidas, e ela volta sozinha. |

O aviso aparece **nas seis primeiras**, que é onde ele serve. Isso mora no
cliente, então só chega por patch (§4.18) — e o patch tem de sair **depois**
do deploy, senão a frase promete uma regra que o servidor ainda não tem.

### A prova

Duas, no servidor local, falando o protocolo direto no socket:

1. sete senhas erradas → suspensa; a senha **certa** em seguida devolve erro 6
   com `ate '2026-09-05 14:39:32'` preenchido, e a `ipbanlist` fica vazia;
2. seis erradas → senha certa (entra, pacote `0x0ac4`) → mais seis erradas →
   `unban_time` continua **zerado**.

O primeiro teste falhou antes de passar, e o motivo virou armadilha: as sete
conexões saíam em um segundo e a sétima levava `[Errno 10054]` — não era a
trava nem o servidor caindo, era o `ddos_count: 5` em `ddos_interval: 3000` do
`packet_athena.conf`, que fecha a conexão **sem mandar pacote nenhum** por dez
minutos. As duas armadilhas estão no `ARMADILHAS-RATHENA.md`.

### O patch saiu antes do deploy, por decisão (2026-09-06)

**Patch 0020, "Aviso da trava de conta na tela de login"** — um arquivo
(`data/msgstringtable.txt`), 136,1 KB crus, 0,05 MB no zip. Zip primeiro,
`lista.txt` depois, como sempre.

A recomendação era publicar **depois** do deploy, porque a frase nova promete
uma regra que produção ainda não tem. O dono mandou publicar junto, e a
consequência está escrita no `PENDENCIAS.md`: até o deploy sair, quem errar
sete senhas ainda leva a faixa /24 banida por cinco minutos — só que agora com
o texto novo do id 9 ("Acesso recusado pelo servidor"), que é melhor que o
"Rejected from Server" de antes. O aviso do id 7 é o único que fica impreciso
nessa janela, e ela fecha no deploy.

Os três commits: `631fd3a` (o Festival, que estava pronto e sem commit desde
2026-09-05), `8596da4` (a trava) e `03012f7` — este último trocando o caminho
relativo dos includes do cabeçalho novo pelo `<common/...>` que os outros oito
de `src/custom` usam. Funcionava no MSVC daqui; o servidor compila com `make` e
GCC, e não era hora de descobrir a diferença no meio de um deploy.

Uma coisa foi conferida e vale ficar escrita, porque a dúvida era razoável: o
`atualiza_servidor.sh` reinicia os **quatro** serviços quando o binário é
recompilado, e o `guerra-login` está entre eles. Deploy que reiniciasse só o
map deixaria a trava compilada e sem efeito, sem nada denunciando.

## O changelog: o painel NOVIDADES e a mensagem do grupo (2026-09-06)

Vinte patches publicados, e o jogador nunca soube o que veio em nenhum deles. A
`lista.txt` sempre teve um nome por patch — mas ele passa voando na barra de
estado enquanto o zip é aplicado, e *"Quarenta e sete itens nas lojas de
Prontera"* não diz **quais**, que é a única coisa que quem joga quer saber. Do
outro lado, quem publica reescrevia o anúncio do WhatsApp à mão toda vez.

As duas pontas viraram a mesma peça, pedida pelo dono nestes termos: uma lista
de células, uma por patch, com os itens embaixo do título quando houver, **um
botão de copiar por célula** que aparece ao passar o ponteiro, e o cabeçalho
`LibraRO updates <data>` — a data no cabeçalho justamente porque se colam
várias mensagens em sequência, e é ela que diz qual é de qual dia.

**O texto mora em `patcher/novidades.txt`**, versionado ao lado do
`patches.txt`, gerado pelos `--nota` do `monta_patch.py` e publicado pelo
`publica_patch.sh` como `novidades.txt`. Os vinte blocos já publicados foram
semeados com a data que o `git log` sabia de cada linha do registro, e sem
pontos — eles são anteriores ao arquivo.

**No Atualizador é a coluna da direita, sobre a arte** (`patcher/novidades.go`
mais o painel em `janela.go`), à maneira do patcher de RO. Rola com a roda, com
o polegar ou clicando no trilho; o layout é medido uma vez e guardado, e o
desenho é recortado com `IntersectClipRect` — é o corte ao meio da primeira e
da última linha que diz ao olho que há mais coisa ali. Conferido em tela: título
longo quebra em duas linhas, item longo quebra com o recuo alinhado à primeira,
o botão vira "copiado!" por um segundo e meio, e o texto chega inteiro na área
de transferência (clique automatizado, `Get-Clipboard`).

Três decisões que valem para além deste painel:

- **A leitura do `novidades.txt` é tolerante, e a da `lista.txt` continua não
  sendo.** São perguntas diferentes: uma linha torta na lista significa um patch
  que o jogador vai ou não vai receber; aqui, o pior caso é um texto feio. Bloco
  sem data passa, linha sem traço vira ponto, cabeçalho torto é pulado e os
  vizinhos sobrevivem.
- **É o único arquivo do canal que se edita à mão depois de publicado.** O
  `publica_patch.sh` o envia em toda rodada, mesmo sem zip novo — corrigir a
  redação de um patch antigo deixou de exigir um patch novo, e o `monta_patch`
  escreve por acréscimo justamente para não apagar essas edições.
- **Sem o arquivo o painel não some**, cai nos nomes da `lista.txt`. Nada no
  Atualizador pode impedir alguém de entrar no jogo, e um changelog é a última
  coisa que teria direito a isso.

O Atualizador foi para a **versão 4**, e foi publicado no mesmo dia:
`Jogar-4.exe` mais o `patcher.txt` que o aponta, e o `novidades.txt` ao lado da
`lista.txt`. Quem já tem o 3 troca sozinho na próxima abertura. **O painel mora
no exe**, não no cliente — patch comum não o entregaria —, e nada disso toca o
servidor de jogo: não houve deploy nem reinício.

E uma regra saiu daqui, a §4.24 do `CLAUDE.md`: **a lista de itens é escrita
por quem monta o patch**, e não pedida ao dono. O pedido dele foi explícito —
*"isso não pode ser um passo a mais pra mim"* —, e o raciocínio é o que
sustenta a regra: a lista já está na mão de quem acabou de pôr os itens na
loja, e devolvê-la ao dono é garantir que o campo fique vazio. Com ele vazio, o
anúncio do dia volta a ser a frase que não informa nada, que é o defeito que
este trabalho existiu para consertar.
