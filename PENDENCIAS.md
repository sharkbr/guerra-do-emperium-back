# Pendências — Guerra do Emperium

**Só o que está em aberto.** O que já foi feito vive em `HISTORICO.md`; regras e
ordem de trabalho no `CLAUDE.md`; tabelas de consulta em `REFERENCIA.md`.

**Onde escrever:** ao concluir um item daqui, **apague-o deste arquivo** e
registre o que foi feito no `HISTORICO.md`, com data absoluta. Um item que
sobrevive aqui depois de pronto é ruído — foi por isso que este arquivo foi
separado em 2026-08-07.

> Este arquivo é versionado: **nunca colar senha real aqui.** As senhas reais
> vivem em `rathena/conf/import/`, que está fora do git.

Estado em 2026-08-07.

---

## 1. Falta ver no jogo

Tudo abaixo está **escrito, registrado no `scripts_guerra.conf` e conferido
offline**, mas nunca subiu uma vez sequer. Não são bugs conhecidos — são coisas
sem confirmação in-game.

| O quê | Onde | Desde |
|---|---|---|
| Mercado Contemporâneo (9 lojas de equipamento) | `prontera`, grade 3×3 | 2026-08-01 |
| Capacete de Intensificação (400287) | Chapeleiro | 2026-08-02 |
| Mesmerita (reset) | `prontera 144,173` | 2026-08-04 |
| Funcionária Kafra da praça | `prontera 152,191` | 2026-08-04 |
| Armazém do Clã | `prontera 149,191` | 2026-08-04 |
| Xanin e Edgard (estilista de roupa) | `prontera 172,201` / `170,200` | 2026-08-04 |
| Mestre do Refino | `prontera 184,177` | 2026-08-04 |
| Mercado de Visuais (3 lojas de traje) | `prontera`, y=155 | 2026-08-05 |
| Mercado de Cartas (9 lojas, 1410 cartas) | `prontera`, y=149/143/137 | 2026-08-05 |
| Logue e Ganhe — 20 dias de Moeda Nova | janela do cliente, sem NPC | 2026-08-07 |

**O roteiro é o mesmo para todos, e a ordem importa:**

1. `@reloaditemdb` e **depois** `@reloadscript` — a loja valida cada ID ao
   carregar, então o `item_db` precisa estar de pé antes. Loja de troca pede um
   terceiro, no meio: `@reloadbarterdb`.
2. **Fechar e reabrir o cliente** — entradas novas de `itemInfo.lua` e
   `accessoryid.lub` só são lidas na inicialização. Sem isso o item aparece sem
   nome ou o chapéu continua invisível, e a conclusão errada é achar que o
   script falhou.
3. Ir a Prontera, abrir cada loja e comprar um de cada. **É abrir a loja que
   dispara a caixa modal de arte faltando, não equipar.**

**Três coisas para olhar na primeira subida:**

- **Mercado de Cartas, loja de arma:** carrega 255 cartas na linha do `shop` e
  as outras 104 por `npcshopadditem` num `OnInit`. Se o `OnInit` falhar, a loja
  abre com 255 e **não dá erro nenhum** — o sintoma é só a lista curta. Conferir
  contando: `Carta de Arma` tem de mostrar **359**.
- **Honra de Combate:** exige rodar `sql-files/guerra_arena_pvp.sql` antes de
  subir, e **reiniciar o map-server** (não basta `@reloadscript`). Sem as
  tabelas ninguém pontua, mas o anúncio de morte continua saindo — e é esse o
  sintoma que aparece primeiro.
- **Logue e Ganhe:** a janela abre sozinha no login e **não tem NPC** — se não
  aparecer, o roteiro acima não ajuda. O que provar, nesta ordem: (1) a janela
  abre e mostra **20 quadrados de Moeda Nova**, 10 nos dezenove primeiros e
  **50 no vigésimo** — se o ícone ou a quantidade divergirem, quem está
  desatualizado é o `CheckAttendance.lub` do cliente, não o servidor; (2) o
  prêmio chega por **RoDEX**, não direto no inventário; (3) o botão recusa a
  segunda retirada no mesmo dia.

  **Fechar e reabrir o cliente é obrigatório aqui**, e não pelo `itemInfo.lua`:
  o `System\CheckAttendance.lub` também só é lido na inicialização.

---

## 1b. Vence em dezembro de 2027 — os ciclos do Logue e Ganhe

`rathena/db/guerra/attendance.yml` tem **17 ciclos**, um por mês civil, e o
último termina em **2027-12-31**. Passado isso o sistema **morre calado**: sem
janela, sem erro, sem linha de log — o rAthena apenas não encontra período
corrente.

O conserto é uma linha: adiantar `ULTIMO` em
`ferramentas/monta_logue_e_ganhe.py` e rodar. Ele regrava os dois lados
(servidor e cliente) de uma vez. Ver `RECEITAS.md` §10.

Contexto de cada um: `HISTORICO.md`, e o cabeçalho do arquivo em `npc/guerra/`.

---

## 2. Itens com `# TODO` — quatro efeitos e oito conjuntos

Placeholders que entraram sem bônus. Cada `# TODO` no `db/guerra/item_db.yml`
cita a linha em português que ficou de fora.

| item | o que falta | por quê |
|---|---|---|
| 28247 Espingarda | "Mantém [Espalhar Dano] ativo" | não há `bonus` que mantenha habilidade ligada, **e** "Espalhar Dano" não existe na tabela de habilidades do bRO |
| 510155 Ceuci | +11: remover Hipotermia/Cristalização ao apanhar de magia | `bonus3 bAutoSpellWhenHit` **conjura**, não **remove** status |
| 400687 Garra | +11: 10% de infligir Medo ao apanhar | idem |
| 15371, 28572, 400687, 510155 | os conjuntos | exigem a outra peça, que em geral nem está no servidor |

Os três primeiros exigiriam código em `src/custom/`, ou seja **recompilar**.

**Uma exceção é viável hoje:** o conjunto do Broche da Celine (28572) com a Luva
dos Espíritos Malignos (2980) — as duas estão no mesmo mercado, no Acessorista.
O Laço da Celine (18849) também já está na loja, no Chapeleiro.

**O Ceuci (510155) é permanente, não provisório:** é exclusivo do bRO, folclore
brasileiro, nunca existiu no kRO.

> **Armadilha para o dia da atualização do rAthena:** esses IDs estão *fora* da
> nossa faixa 30000-30999, e o `Footer: Imports:` faz o nosso arquivo ser lido
> **depois** do `db/re/item_db.yml`. Se o rAthena um dia trouxer esses itens de
> verdade, as nossas entradas vazias **venceriam a versão boa, caladas.**
> Conferir esta seção antes de qualquer outra coisa ao atualizar o vendor.

---

## 3. EM ANDAMENTO — diálogo dos NPCs do rAthena

**Onde parou em 2026-08-04.** Esta é a única frente da tradução que não está
fechada, e é a maior: **19.260 falas**, das quais 10.903 distintas.

| grupo | feito | | o que é |
|---|---|---|---|
| `cidades` | 715/722 | 99% | Prontera e Izlude |
| `pvp` | 202/222 | 91% | `npc/other/pvp.txt` |
| `campal` | 904/1055 | 86% | KVM, Flavius, Tierra |
| `kafra` | 486/569 | 85% | uma função serve todas as cidades |
| `servico` | 714/926 | 77% | forja, refinador, estalagem |
| `guerra` | 968/1437 | 67% | 20 feudos + WoE:SE |
| `novico` | 14/322 | 4% | **não começou** |
| `classe1` | 13/1518 | 1% | **não começou** |
| `classe2` | 235/12489 | 2% | **não começou** |

Os três de baixo são as quests de mudança de classe — 88% do volume que resta,
e o que o dono do projeto pediu explicitamente por nostalgia. O pouco que
aparece traduzido neles **vazou do glossário** (`Cancelar`, `Sim`, `Não`), não
foi trabalho dirigido.

**Eles NÃO estão aplicados nos arquivos**, e isso é deliberado: um
`--aplicar tudo` chegou a tocar 17 arquivos a ~2% e foi revertido. Arquivo quase
todo em inglês com uma frase solta em português no meio é pior que arquivo em
inglês. Aplicar só quando o grupo estiver inteiro.

### Como retomar

```
python ferramentas/traduz_npcs.py --estado          # onde está cada grupo
python ferramentas/traduz_npcs.py --extrair classe2 # se o vendor mudou
# traduzir: acrescentar pares em npc/guerra/traducao/glossario.cat
python ferramentas/traduz_npcs.py --preencher --forcar
python ferramentas/traduz_npcs.py --aplicar classe2
```

O `ferramentas/LEIAME.md` tem o detalhe das travas e do formato. Duas regras que não estão
óbvias no código:

1. **Nome de habilidade, item, mapa e classe sai da tabela do bRO que já está
   no cliente**, não da cabeça — `skillinfolist.lub`, `mapnametable.txt`,
   `map_msg_por.conf` (550+). Cinco nomes tiveram de ser corrigidos por eu ter
   traduzido de memória.
2. **Traduzir por texto distinto, não por ocorrência.** 43% é repetição.

### O que também ficou pendente

- **Nomes de NPC.** Foram pedidos junto com as falas e não foram feitos. É a
  parte com risco real: no rAthena o nome exibido faz parte do identificador
  único, e `duplicate()`, `enablenpc` e `donpcevent` de outros arquivos
  referenciam por ele. Renomear exige construir a tabela nome-antigo →
  nome-novo e reescrever toda referência do `npc/` — errar faz NPC sumir do
  mapa, e o erro só aparece no jogo. Os nomes em português existem no
  `navi_npc_br.lub` do GRF do bRO, por mapa e coordenada.
- **`guerra` parado em 67%** não é por falta de tempo: os 469 que faltam são
  fragmentos de frase quebrada em várias linhas de `mes` do WoE:SE, que
  dependem do vizinho para ficar natural. Fechar exige olhar bloco a bloco, não
  string a string.

---

## 4. EM ABERTO — o manto cosmético (`Costume_Garment`)

Aberto em 2026-08-05, ao varrer o acervo cosmético para o Mercado de Visuais.
Os três slots de cabeça ficaram **zerados** — nenhum item curável restante —,
e o manto ficou inteiro de fora, com 45 curáveis parados.

O motivo é que manto tem **uma camada a mais** que chapéu, e não há ferramenta
nossa para ela:

| camada | chapéu | manto |
|---|---|---|
| nome e descrição | `itemInfo.lua` | igual |
| slot de visual | `accessoryid.lub` + `accname.lub` | `spriterobeid.lub` + `spriterobename.lub` |
| ferramenta que estende o slot | `estende_accessoryid.py` | **não existe** |
| arquivos de arte | 4 de item + 4 de cabeça | 4 de item + sprite de manto **por classe** |

A nossa `spriterobeid.lub` tem **120 entradas**. Manto cujo `View` esteja fora
dela não desenha, e arte nenhuma resolve — é exatamente o caso que o
`estende_accessoryid.py` cura do lado do chapéu.

O `varre_cosmeticos.py` já classifica manto e **se recusa a chamar de curável**
o que depende dessa ferramenta ausente. Isso é de propósito: chamar de "sem
cura" o que só precisava de outra ferramenta foi o erro de 2026-08-01, e
prometer cura que não há como cumprir é o erro simétrico.

**O que falta, se um dia valer a pena:** um `estende_robeid.py` espelhado no
`estende_accessoryid.py` (mesma base-relida-do-GRF, mesmo round-trip, mesmas
duas travas), mais estender o `valida_visual.Cliente.caminhos` para conhecer a
sprite de manto por classe. A segunda parte é a maior: manto não tem 4 arquivos
como chapéu, tem um por classe de personagem.

**Não confundir com as "capas" que já funcionam.** 420010 (Aura da Escuridão) e
420047 (Capa de Cavaleiro) estão no Retoqueiro e desenham normalmente — elas são
`Costume_Head_Low`, não `Costume_Garment`. O nome engana; quem manda é o
`Locations:` do `item_db`.

---

## 5. Antes de expor o servidor à rede

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

## 6. Higiene, sem pressa

### 1. Não rodar os servidores como administrador

O rAthena avisa: `You are running rAthena with admin privileges, it is not
necessary.` Os três servidores só precisam abrir portas altas (6900, 6121, 5121)
e falar com o MariaDB — nada disso exige elevação. Rodar elevado só aumenta o
estrago de uma falha.

### 2. Reavaliar `db/map_cache.dat` no git

Hoje esse arquivo (3 MB) está **versionado de propósito**, contra a convenção do
brief. O motivo: sem ele o map-server carrega zero mapas, e regerar exige o GRF
do cliente. Com ele, carrega 1265 mapas num clone limpo.

Quando passarmos a gerar o cache a partir do GRF do bRO, o arquivo vira artefato
nosso e começa a mudar a cada geração — aí ele deve sair do git (já existe a
regra `*.mcache` no `.gitignore` esperando por isso).

### 3. Atualizações do rAthena upstream

O `rathena/` foi vendorizado como arquivos comuns, sem o histórico do upstream.
Trazer correção do rAthena hoje é diff manual. Se isso incomodar, a saída é
`git subtree` — mas decidir antes de acumular customização, porque depois fica
mais caro.

---

