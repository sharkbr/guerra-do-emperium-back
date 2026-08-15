# Referência — tabelas de consulta

Caminhos, portas, credenciais, comandos e ambiente. **Consulta pontual, por
tabela** — não se lê inteiro, e não conta história.

> Regras e ordem de trabalho estão no `CLAUDE.md`. Como as peças se encaixam,
> em `ARQUITETURA.md`. Passo a passo, em `RECEITAS.md`.

**Onde escrever:** caminho novo, porta nova, comando confirmado ou peça nova do
ambiente entram aqui. Se for uma **regra** ("nunca faça X"), vai para o
`CLAUDE.md`, não para cá.

---

## Referência rápida

| Item | Onde |
|---|---|
| Credenciais do banco | `rathena/conf/import/inter_conf.txt` (fora do git) |
| Nome do servidor, IPs | `rathena/conf/import/char_conf.txt`, `map_conf.txt` |
| Criação de conta | `rathena/conf/import/login_conf.txt` |
| Schemas | `ragnarok` (jogo), `ragnarok_log` (logs) |
| Usuário do banco | `ragnarok` — sem acesso fora desses dois schemas |
| Portas | 6900 login, 6121 char, 5121 map, **8888 web**, 3306 banco |
| Versão de cliente alvo | kRO 2021-11-03 (`PACKETVER` padrão do rAthena) |
| Pasta do cliente | `C:\GuerraDoEmperium\cliente` (fora do git) |
| Executável do cliente | `GuerraDoEmperium.exe` |
| **Servidor de produção** | `138.197.155.31` = `libraro.filiponegrao.com.br` (login 6900, char 6121, map 5121) |
| **Site de contas** | https://libraro.filiponegrao.com.br — é por ele que o jogador se cadastra (`new_account: no`) |
| **Endereço do servidor no cliente** | `cliente\data\sclientinfo.xml` — **é este que vale**, não o `clientinfo.xml`; manter os dois iguais (`CLAUDE.md` §5) |
| Patches do NEMO no exe | `cliente\GuerraDoEmperium.epi` — lista na seção abaixo |
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
| **Logue e Ganhe** | `rathena/db/guerra/attendance.yml` **e** `cliente\System\CheckAttendance.lub` — os dois, sempre; gerados por `ferramentas/monta_logue_e_ganhe.py` |
| Mensagens do servidor em PT-BR | `rathena/conf/msg_conf/map_msg_por.conf`; in-game `@langtype por` |
| Inspecionar GRF e `.lub` | `ferramentas/` (ver `ferramentas/LEIAME.md`) |
| Temática visual / cidade destruída | `CUSTOMIZACAO-VISUAL.md` |
| Mapas, modelos e texturas do cliente | `cliente\data\*.rsw`, `.gnd`, `.gat`; `data\model\`, `data\texture\` |
| Recortar `.lub` novo demais | `ferramentas/filtra_lub_por_skid.py` |
| Config de vídeo do cliente | `Setup.exe` **como admin** (grava em HKLM) |
| `.lub` removidos e originais | `C:\GuerraDoEmperium\_backup_luafiles_roenglish\` |
| **Subir / parar / conferir servidores** | `python ferramentas/servidor.py status\|subir\|parar\|reiniciar` — **são quatro**, não três |
| Algo estranho no jogo? | `servidor.py status` primeiro — ele diz qual peça caiu e o que ela quebra |

---

## Ambiente instalado nesta máquina

- Visual Studio 2022 Community 17.14.37 (workload C++)
- Python 2.7.18 em `C:\Python27` — para o `get4.py` do NEMO e para o
  `ferramentas/` deste repo
- WARP 1.5.3 em `C:\Users\User\Downloads\WARP-rock_win32`
- ROenglishRE clonado em `C:\Users\User\Downloads\ROenglishRE`
- Instalador kRO em `C:\Users\User\Downloads\RAG_SETUP_211105.exe` (3,19 GB,
  SHA256 `d9067cc9ac62c85fa599ac94bbb19e9e96a1b7529181252806dc1df49e0293aa`)

---

## Patches do NEMO aplicados no exe

Extraídos em 2026-08-14 de `C:\GuerraDoEmperium\cliente\GuerraDoEmperium.epi`
(8.437 bytes), o perfil que o NEMO grava ao lado do executável. **O exe é a
única peça do cliente sem gerador versionado** — esta lista é o que existe de
mais próximo de uma receita dele (`PENDENCIAS.md` §5b).

Para reextrair, os nomes estão em texto legível dentro do `.epi`:

```
python -c "import re;d=open(r'C:\GuerraDoEmperium\cliente\GuerraDoEmperium.epi','rb').read();
print '\n'.join(sorted(set(re.findall(r'[A-Za-z][A-Za-z0-9_]{4,40}', d))))"
```

| patch | para que serve aqui |
|---|---|
| `AlwaysAscii` | **desenha byte acentuado** — é o que sustenta a regra §4.1 do `CLAUDE.md` |
| `DataFolderFirst` | `cliente\data\` vence o GRF |
| `GRFsFromIni` | a lista de GRFs sai do `DATA.INI` |
| `EnableDnsSupport` | o `<address>` pode ser **domínio**, não só IP |
| `NoHardCodedAddr` | tira o endereço fixo do exe |
| `CustomItemInfoLub` | aponta o `itemInfo` para `System\itemInfo_true` |
| `TranslateClient` | usa o arquivo de tradução (`Translations_EN`) |
| `MsgStrings` | `msgstringtable.txt` |
| `CustomFontCharset` / `newFontCharset` | charset da fonte |
| `CustomWinTitle` | título da janela = `GuerraDoEmperium` |
| `CallKoreaClientInfo` | **atenção:** está aplicado e mesmo assim quem vale é o `sclientinfo.xml` (`CLAUDE.md` §5) |
| `OpenToServiceSelect`, `UseOldLogin`, `NoFilenameCheck`, `No1and1Arg` | entrada e login |
| `EnableShowName`, `EnableSysMenu`, `EnableWho`, `GuildBrackets`, `AllowSpaceInGName`, `Allow65kHairs`, `MediumCamAngle`, `PlainTextDesc`, `RestoreIcon` | interface e jogo |
| `NoNagle`, `SendClientFlags`, `FixLatestNCWin`, `FixChatAt`, `NoHourly`, `NoHelpMsg`, `HideBuildInfo`, `NoSerialDisplay`, `NoGravityLogo`, `NoGravityAds` | rede, avisos e telas da Gravity |

**Duas ressalvas.** Os nomes saem de um binário, então a fronteira de cada um
pode levar um byte de lixo junto (`Allow65kHairs4`, `EnableDnsSupportP`) — o
nome real é o prefixo. E o `.epi` guarda **quais** patches, não com que
parâmetros cada um foi aplicado; os parâmetros visíveis em texto são
`newItemInfo`, `System\itemInfo_true`, `dataINI`, `translationFile`,
`Translations_EN` e `customWindowTitle`.

---

## Comandos `@`

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
| Logue e Ganhe | `@reloadattendancedb` — recarrega **só o lado do servidor** |
| Visual | `@mount`, `@size`, `@option` |

Conferidos como **inexistentes**: `@ml`, `@wlup`, `@lvup`, `@levelup`, `@job`,
`@god`, `@die`.

Note que o próprio `@` é configurável (`atcommand_symbol` em
`conf/battle/misc.conf`), e `#` é o prefixo para agir sobre outro jogador
(`@charcommands` lista esses).

---

