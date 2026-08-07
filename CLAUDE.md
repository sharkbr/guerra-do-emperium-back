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
| `conf/battle_athena.conf` | uma linha `import: conf/guerra/battle_guerra.txt` |
| `db/re/item_db.yml`, `db/item_combos.yml`, `db/re/mob_db.yml`, `db/re/reputation.yml`, `db/re/reputation_group.yml` | um `- Path: db/guerra/...` no rodapé de cada |
| `src/map/clif.cpp` | duas linhas (include + `placa_de_venda_mostra`), comentadas no arquivo |
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
| `conf/guerra/`, `battle_athena.conf` | `@reloadbattleconf` (chama `mob_reload()` sozinho se taxa de item mudou) |
| `db/guerra/reputation.yml` | **reiniciar o map-server** — `reputation_db.load()` só roda no `do_init_pc` |
| `src/` | recompilar (VS 2022 Community, já instalado) |
| `itemInfo.lua` e afins no cliente | **fechar e reabrir o cliente** — só lido na inicialização |

Na dúvida, reiniciar o map-server resolve tudo do lado servidor; login e char
podem ficar de pé. **Derrubar o servidor por causa de `db/` é desnecessário.**

`@rates` in-game imprime as taxas carregadas em memória. "Unknown Command" **não**
é falta de permissão.

## 4. Regras que não se negociam

1. **Texto de jogo é cp1252, nunca UTF-8.** Acento sim; UTF-8 quebra. Quem faz o
   cliente desenhar byte acentuado é o patch `AlwaysAscii`. Vale para `.txt` de
   NPC, `itemInfo.lua` (ANSI/CP949), `.lub`. Estes `.md` são UTF-8 — a regra é
   para texto que o **jogo** lê.
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

## 5. Armadilhas deste ambiente

Produziram diagnóstico falso e custaram retrabalho:

- **`strings` não existe** no Git Bash daqui — com `2>/dev/null` falha calado e
  parece "zero resultados".
- **`[Text.Encoding]::Latin1` não existe** no PowerShell 5.1 → devolve `$null` e
  todo resultado derivado é lixo. Usar `GetEncoding(28591)`.
- **`Get-ChildItem -Include`** sem curinga no caminho retorna vazio.
- **`.lub` do GRF é bytecode** (header `\x1bLua`); os do ROenglishRE são texto
  puro. Comparar tamanho entre os dois não significa nada.
- **`Tools\luac.exe -p` do ROenglishRE é o único jeito de provar que um `.lub`
  gerado compila.**
- **`source` do mysql.exe quebra com barra invertida** (`\U` = comando
  desconhecido). Usar barras normais no caminho.
- **Ler tabela grande de bytecode Lua 5.1:** o operando `RK` só endereça
  constante até o índice 255; depois disso o compilador emite `LOADK` num
  registrador e o `SETTABLE` referencia `R<n>`. Um parser que lê só
  `SETTABLE ... ; B="NOME" C=<valor>` captura as ~127 primeiras entradas e
  devolve um número **plausível e errado**.
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
