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
| `conf/char_athena.conf` | uma linha `import: conf/guerra/char_guerra.txt` (nome de personagem com acento) |
| `conf/inter_athena.conf` | uma linha `import: conf/guerra/inter_guerra.txt` (`default_codepage: latin1`) |
| `conf/login_athena.conf` | uma linha `import: conf/guerra/login_guerra.txt` (`use_MD5_passwords: yes`) |
| `db/re/item_db.yml`, `db/item_combos.yml`, `db/re/reputation.yml`, `db/re/reputation_group.yml`, `db/attendance.yml`, `db/refine.yml` | um `- Path: db/guerra/...` no rodapé de cada |
| `db/re/mob_db.yml` | **dois** `- Path:` no rodapé, não um — a única exceção da linha de cima. `db/guerra/mob_db.yml` é o nome em português, **gerado** por `traduz_ptbr.py monstros` (reescreve o arquivo inteiro; editar à mão morre no próximo `--extrair`); `db/guerra/mob_db_guerra.yml` é o segundo, escrito à mão, para ajuste pontual de campo de combate (ex.: `Attack` de um guardião fora de castelo — ver o cabeçalho do arquivo e `PENDENCIAS.md` §1s) |
| `db/re/quest_db.yml` | o **`Footer: Imports:` inteiro** — aquele arquivo não tinha rodapé nenhum. Seguro porque o `parseImports` mora no `YamlDatabase` (`src/common/database.cpp:176`), não no leitor de quest: vale para todo banco em YAML, e o mesmo caminho serve para qualquer `db/re/*.yml` que ainda não tenha rodapé |
| `src/map/clif.cpp` | dois includes de `src/custom/` + três chamadas (`placa_de_venda_mostra`, e o teto de refino nas duas pontas da janela de refino), comentadas no arquivo |
| `src/map/battle.cpp` | **dois** includes de `src/custom/` + **sete** chamadas, todas comentadas no arquivo. Duas de `reducao_de_dano.hpp`: `reducao_alcanca_percentatk` (no bloco "Card Fix for target" — põe o `percentAtk` na redução, sem ela `bonus bAtkRate` fura toda resistência) e `reducao_piso` (dentro do `APPLY_CARDFIX` — teto configurável, 99% hoje, no lugar do `max(0, …)` que deixa a redução zerar o dano). Cinco de `reducao_geral.hpp`, a redução geral de 80% (`REDUCAO-DE-DANO.md` §1c): quatro de `reducao_pvp` — três dentro do `battle_calc_damage` (o caminho normal + as duas saídas antecipadas de habilidade que pula tudo) e uma no `battle_calc_return_damage`, para o reflexo — e **uma que SUBSTITUI linha do rAthena**, a única do projeto: dentro do `battle_calc_gvg_damage`, `reducao_isenta_habilidade(skill_id)` no lugar do `skill_get_inf2(skill_id, INF2_IGNOREGVGREDUCTION)`. **Substituição não sobrevive a merge por si** — se `INF2_IGNOREGVGREDUCTION` reaparecer ali depois de atualizar o vendor, o enxerto morreu calado |
| `src/map/status.cpp` | um include de `src/custom/` + **duas** chamadas, comentadas no arquivo, as duas de `guardiao_do_castelo.hpp` (a escala do guardião pela defesa do castelo): `guardiao_tem_escala` num `flag\|=4` **acrescentado** ao lado do `guardup_lv` do rAthena — não substitui nada, e só existe porque sem flag nenhuma o `status_calc_mob_` sai antes, libera o `md->base_status` e passaria a escrever no status **compartilhado** do `mob_db`; e `guardiao_aplica_escala` no fim da mesma função, depois do bloco "Strengthen Guardians" e **antes** do `memcpy` final |
| `npc/scripts_guild.conf` | duas coisas. **(a)** 19 das 20 linhas de castelo da Guerra do Emperium 1 comentadas — só o `prtg_cas01.txt` (Kriemhild) fica. É o que tira Emperium, Kafra, Gerente e bandeiras dos castelos-museu de uma vez, e é também **o que limita a guerra ao Kriemhild**: sem o arquivo do castelo não há `Agit#<castelo>`, logo não nasce Emperium. Ver `npc/guerra/guardioes_dos_castelos.txt`. **Levou 279 bandeiras junto** — devolvidas por `npc/guerra/bandeiras_do_feudo.txt`, todas hasteando o dono do Kriemhild. **(b)** o `agit_controller.txt` comentado, substituído por `npc/guerra/horario_da_guerra.txt` (quinta 20–22, domingo 18–20, horário de Brasília). Nunca deixar os dois ligados |
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
| `db/guerra/instance_db.yml` (nome de instância) | `@reloadinstancedb` — existe, e **não** exige reiniciar. O nome é chave: o `instance_create` resolve por string, então rodar este **antes** do `@reloadscript` quando os dois lados mudaram juntos |
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

    **E o `Locations:` do nosso rAthena não é a última palavra: o do bRO
    é.** São dois desacordos diferentes e o remédio de cada um é outro. Se o
    pedido discorda do nosso `item_db` mas **concorda com a descrição do
    bRO** (`estado_item.py --id <n> --descricao`, linha "Equipa em:"), quem
    está errado é o nosso vendor — corrige-se por override, com `false`
    explícito no slot velho, e a peça muda de loja. Se o bRO e o nosso
    `item_db` **concordam entre si** e só o pedido destoa, a peça vai para a
    loja do `Locations:` e a divergência é levantada por escrito. Em
    2026-08-12 a mesma lista trouxe os dois casos: Cachecol Glorioso e
    Coleira do Vassalo eram erro nosso (dois overrides), Gata Branca e Manto
    do Herói eram engano do pedido (duas ressalvas).

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
15. **Para fechar célula, `setwall` — nunca `setcell`.** São os dois que
    parecem servir, e a diferença é o cliente. O `setcell` muda a célula só do
    lado do servidor: o cliente continua achando que dá para andar ali, e o
    próprio `doc/script_commands.txt` avisa que *"the wall will not be shown
    nor known client-side, which may cause movement problems"*. O `setwall`
    faz o mesmo bloqueio e ainda manda `clif_changemapcell`
    (`map.cpp:3509`), com o `map_iwall_get` reenviando para quem entrar no
    mapa depois (`clif.cpp:11098`) — as duas metades ficam de acordo. Ele
    ainda vem com `delwall` (desfaz exato) e `checkwall` (testa), que são o
    que torna um `OnInit` idempotente.
    **Um cuidado ao desfazer:** o `map_iwall_remove` devolve a célula para
    andável+atirável **sem consultar o mapa original** (`map.cpp:3553`) —
    `delwall` numa célula que já nascia bloqueada abre buraco no cenário.
    E lembrar que **modelo de `.rsw` não bloqueia nada sozinho**: o override
    de mapa não toca o `.gat`, então móvel plantado é atravessável até que
    alguém escreva o `setwall`. As duas metades estão no `ARQUITETURA.md` §4.
16. **Item com `Buy` no `item_db` entra na loja PELO `Buy`, não a 1 zeny.**
    Decisão do dono em 2026-08-12: *"todo item a partir de agora que tiver
    valor de venda a gente vende com o valor de compra dele"*. Sem `Buy`
    nenhum, 1 zeny como sempre. Não há meio-termo, e o motivo é aritmético:
    revenda paga `Buy/2`, então **qualquer preço abaixo de `Buy` deixa
    lucro** — e o lucro é por clique, em laço infinito, num servidor de
    drop 50x. É a saída que a Tranqueiras estreou na manhã do mesmo dia e
    que substituiu a anterior (**podar a peça cara da vitrine**, que foi o
    que aconteceu com a Boina Alada, 5170, e com o Ouro, 969).

    Quem disparou a regra foi o **Elmo de Aegir (18728)**, `Buy: 200000`:
    a 1 zeny seriam **99.999 de lucro por clique**. Levado ao dono como
    "tiro ou ponho?", a resposta foi uma terceira coisa — **cobra**.

    Duas consequências práticas:
    - **`npc_parse_shop` deixa de reclamar.** O aviso `discounted buying
      price (1->0) is less than overcharged selling price` só sai quando o
      preço de compra com desconto fica abaixo do de venda com
      supervalorização, e no preço de compra isso não acontece. Item posto
      pela regra nova **não** acrescenta linha de aviso na subida — os
      avisos que sobram são todos de item posto antes dela.
    - **A regra é "a partir de agora" e não foi aplicada para trás.** Os
      itens de `Buy: 20` que já estavam nas nove lojas a 1 zeny continuam
      a 1 zeny (9 zeny de lucro por clique, que o próprio dono chamou de
      "não move nada"). Preço de peça que já está na mão dos jogadores não
      se troca sem ele pedir.
17. **Antes de mudar uma regra, conferir se ela EXISTE — o cabeçalho pode
    estar descrevendo uma que nunca foi escrita.** Cabeçalho longo é o que
    torna este projeto navegável, e é justamente por isso que ele é lido como
    se fosse o código: quem chega para mexer parte da descrição e edita ao
    lado dela. Quando os dois divergem, **nada denuncia** — não há teste, não
    há log, e o NPC funciona.

    Caso vivo, e de graça só porque apareceu na leitura: o
    `honra_de_combate.txt` prometia desde 2026-08-08 que *"quem cai abaixo de
    zero para de valer para o matador, mas continua sendo alvo: morrer ainda
    tira ponto dele"*, e o código tinha um `if (.@pontos_morto < .Piso) end;`
    que saltava **as duas** pontuações. A regra escrita nunca rodou. Em
    2026-08-13 o dono pediu exatamente aquele comportamento como novidade — e
    era, apesar de estar documentado havia cinco dias.

    Na prática: ao receber "mude X para Y", **ler o trecho que implementa X**
    e não só o parágrafo que o explica. Se os dois discordarem, o pedido
    provavelmente é sobre o que o código faz, não sobre o que o texto diz — e
    a divergência entra na entrega, por escrito. É a mesma família da §4.11
    ("comentário não é trava"), do outro lado: lá o comentário mentia sobre
    uma ordem, aqui sobre uma regra.

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
- **E quem faz isso hoje é a FERRAMENTA DE EDIÇÃO do assistente.** Ela lê e
  grava como UTF-8: num arquivo cp1252 ela troca **todo** byte acentuado do
  arquivo por U+FFFD — não só os da linha editada, e sem avisar. Medido em
  2026-08-12 num arquivo de três linhas com seis acentos: trocar uma linha
  **sem acento nenhum** destruiu os seis. Vale para `npc/guerra/*.txt`,
  `db/guerra/item_db.yml`, `.lub`, `itemInfo.lua` — todo texto que o jogo lê.
  (Os `.md` são UTF-8 e podem ser editados à vontade.)
  **A saída é gravar por script**: âncora em ASCII, texto novo nascendo
  `unicode` e um `.encode('cp1252')` num lugar só, mais um `assert` de que a
  âncora é única e um `decode('cp1252')` de volta antes de valer. E **medir o
  fim de linha do arquivo antes de escrever a âncora, nunca supor**: âncora com
  o `\r\n` errado casa zero vezes, e linha remontada com o outro deixa o
  arquivo misturado. Não há padrão a decorar — medido em 2026-08-12, dos 44
  arquivos nossos em `npc/guerra` e `db/guerra` **18 são CRLF e 26 são LF**,
  nenhum misto, e o `.gitattributes` tem `text=auto` (com `*.yml eol=lf`), ou
  seja quem decide é o checkout. Os erros aconteceram nesta ordem em
  2026-08-12; os dois foram baratos porque o `assert` da âncora parou o script
  antes de gravar.
- **A conexão com o MariaDB nasce em `utf8mb4`, e byte acentuado morre nela.**
  As 105 colunas de texto do banco são `latin1`, mas o `character_set_client`
  padrão deste MariaDB 12.3 é `utf8mb4` — e o rAthena só manda `SET NAMES` se
  `default_codepage` estiver preenchido (`inter.cpp:978`, `map.cpp:4416`), o que
  **não era o caso**. Um byte cp1252 sozinho é UTF-8 inválido, então o
  MariaDB recusa a gravação inteira com *"ERROR 1366 (22007): Incorrect string
  value"*. Ou seja: **texto acentuado que o servidor tenta gravar no banco não
  chega lá**, e o caminho de erro é do lado do SQL, longe de onde o texto
  nasceu. Corrigido em 2026-08-10 por `conf/guerra/inter_guerra.txt`
  (`default_codepage: latin1`); a armadilha continua valendo para quem
  desconfiar do `conf/import/` e apagar esse import.
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
- **`setwall` com tamanho maior que 1 pode sair mais curto do que o pedido, e
  não avisa.** O `map_iwall_set` percorre as células uma a uma e **para na
  primeira que já esteja bloqueada** (`map.cpp:3503`), gravando
  `iwall->size = i` — a parede fica com o comprimento que deu, sem erro, sem
  log, e o `checkwall` depois responde que ela existe. Quem precisa das
  células exatas usa **tamanho 1 por célula**, que não tem o que truncar, e
  confere cada uma com `checkcell(..., CELL_CHKNOPASS)` antes de dar por
  fechado. Ver a escrivaninha em `npc/guerra/centro_da_ordem.txt`.
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
- **`source` do mysql.exe quebra com barra invertida** (`\U` = comando
  desconhecido). Usar barras normais no caminho.
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
- **No `.cat` de tradução, o `arquivo#N` NÃO é a linha — é a ordem do literal
  dentro do arquivo.** Está na docstring do `literais_todos`
  (`ferramentas/traduz_npcs.py`), e é de propósito: assim o índice não anda
  quando a lista de contextos muda. A armadilha é que o número **parece** linha
  e cai na mesma faixa de grandeza dela, então um recorte "só as falas deste
  NPC, que vai da linha A à B" filtra por engano e **devolve uma lista
  plausível**. Medido em 2026-08-12 ao recortar os cinco NPCs do Cassino de
  Comodo: o filtro errado deu 444 textos com o `Man#megin` zerado — e um NPC de
  203 linhas mudo era a única coisa que denunciava. Com a contagem certa deram
  353, com 59 dele. Para converter, recontar os literais com o mesmo
  `RE_LITERAL` guardando a linha de cada um.
- **`rand(1)` não devolve 0: ele MATA o script.** O `buildin_rand`
  (`src/map/script.cpp:5604`) na forma de um argumento só faz `maximum -= 1` e
  então recusa `maximum < 1` com *"range is too small. No randomness
  possible"*, pondo `st->state = END`. Ou seja **`rand(n)` só é seguro com
  `n >= 2`** — e o caso perigoso não é a constante, é a **variável**: `rand(.@x)`
  onde `.@x` é um contador que encolhe (cartas que restam, itens que sobraram,
  jogadores vivos) passa por 1 no fim, sempre, e aí o script morre no meio com
  o diálogo aberto e o que já foi cobrado, cobrado. Nada no cliente denuncia; o
  log traz uma linha longe de onde o número nasceu. Achado em 2026-08-12 no
  blackjack do Cassino de Comodo, onde `rand(@bj_resta[valor])` valia 1 toda vez
  que saía a última carta daquele valor. A saída é uma linha:
  `if (.@x > 1) .@i = rand(.@x);` com `.@i` já em 0.
- **`getitem` com a mochila cheia LARGA O ITEM NO CHÃO.** O
  `buildin_getitem` (`src/map/script.cpp`) chama `pc_additem`, e no fracasso
  cai num `map_addflooritem` — então "vai direto para o inventário" não é
  garantia do script, é garantia do **item**. Quem impede a queda é o
  `pc_candrop`, que recusa item `NoDrop`; com ele o item se perde e o cliente
  avisa. Item sem `NoDrop` entregue por script aparece no chão da arena, ao
  alcance de qualquer um, e nada no log denuncia. Caso vivo: a Caveira Humana
  (30995), em `npc/guerra/honra_de_combate.txt`.
- **`mes` que começa com ESPAÇO não abre linha nova — cola na anterior.** O
  `clif_scriptmes` (`src/map/clif.cpp:2472`) manda a string **crua**, sem `\n`:
  quem decide onde quebrar é o cliente, e o critério dele é o primeiro
  caractere. Visível abre linha; espaço é continuação. Então indentar uma
  lista com `mes "  item…"` **concatena a lista inteira**, e o que se vê na
  tela é o resultado da largura da caixa, não do script. Medido em 2026-08-11
  na Máquina de Sombrios Totais: das quatro linhas de prêmio, três pareciam
  certas — tinham estourado a largura e quebrado sozinhas — e a quarta apareceu
  grudada no fim da terceira. **Três das quatro estavam erradas e pareciam
  certas**, e mexer em qualquer texto (nome de item mais curto, porcentagem com
  menos dígitos) reorganiza a janela sem erro nenhum. Para recuar, caractere
  visível (`- `, `. `), nunca espaço.
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
- **`||` e `&&` do script do rAthena NÃO fazem curto-circuito.** São o `C_LOR`
  e o `C_LAND`, operadores de **dois números** (`script.cpp:3839`) resolvidos
  pelo `op_2num` depois de os dois lados já estarem na pilha — não há salto
  como em C. Então a guarda mais comum de todas, `if (i == 0 || v[i-1] != x)`,
  avalia `v[-1]` na primeira volta, **sempre**. O mesmo vale para
  `if (getarraysize(.a) > 0 && .a[0] == 1)` e para qualquer
  `if (x != 0 && y/x > 2)`. Falha barulhenta no log (*"getelementofarray:
  index out of range (-1)"*) e **calada na tela**: o comando devolve falha, o
  `OnInit` MORRE ALI, e tudo que ele ainda ia montar fica vazio — um menu
  construído depois abre em branco, sem nenhuma linha de erro que aponte para
  o menu. Achado em 2026-08-12 no Guia de Prontera. A saída é `if` aninhado ou
  `if`/`else if`, nunca o operador.
- **O nome único de um NPC é o que vem DEPOIS do `::`, não a linha inteira.**
  Em `<Nome na tela>::<Nome único>` o `npc_parsename` (`src/map/npc.cpp:3674`)
  põe a primeira metade em `nd->name` — que só serve para desenhar — e a
  segunda em `nd->exname`, que é a chave do `npcname_db` e o que
  `disablenpc`/`enablenpc`/`donpcevent` aceitam. Ou seja o
  `Guide#01prontera::GuideProntera` se desliga por **`GuideProntera`**.
  Confunde porque a metade da esquerda **parece** o nome único (tem `#`, é o
  que se lê no arquivo) e porque num NPC **sem** `::` as duas são a mesma
  coisa — inclusive nos `duplicate`, que quase nunca têm `::`. Erra-se num e
  acerta-se nos outros quatro, e o resultado é NPC velho de pé empilhado no
  novo: os dois aparecem, o jogador clica no de cima, e qual é o de cima
  ninguém escolheu. O log traz *"Attempted to disablenpc a non-existing NPC"*.
- **`explode` NÃO limpa o array de destino.** Ele grava a partir do índice
  dado (`script.cpp:17305`) e para quando a string acaba — o que sobrou de uma
  chamada anterior mais longa continua lá. Ler o resultado por
  `getarraysize()` depois de uma linha curta devolve o tamanho da linha
  ANTERIOR, e nada denuncia. `deletearray <array>[0];` antes de cada
  `explode`, sempre.
- **`getarraysize()` de array de texto para no último elemento NÃO VAZIO.**
  Então tabela de colunas paralelas em que a última coluna termine em `""`
  encolhe, e a conferência "todas as colunas têm o mesmo tamanho" — que é o
  que a regra §4.11 pede — passa a mentir justamente quando deveria pegar o
  desalinhamento. Usar um marcador visível (`"-"`) no lugar de `""`, e numerar
  coluna de inteiro a partir de 1 e não de 0, pelo mesmo motivo.
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
- **Facing de NPC se calcula pela CÉLULA de destino, não pelo lado da tela.**
  Tabela do `enum directions` (`src/map/path.hpp:16`) medida em jogo com a
  câmera padrão: **4 (sul) desenha para baixo-direita, 2 (oeste) para
  baixo-esquerda, 0 (norte) para cima-esquerda, 6 (leste) para cima-direita.**
  A pergunta certa é "que direção me leva daqui até lá". O cabeçalho da
  `npc/guerra/maquina.txt` traz uma tabela em termos de "direita/esquerda" que
  vale **só para aquele sprite** — reusá-la virou a Máquina de Sombrios Gerais
  para o lado errado em 2026-08-12.
  **E há um caso em que o ponto cardeal pedido é a resposta errada: NPC de
  FALA.** Quando o pedido diz "virado para leste" e o NPC fica de frente para o
  jogador, ótimo; quando fica **de costas**, não houve erro de conversão — foi o
  `6` fazendo o que a tabela promete. Para quem conversa, o que importa é a
  direção **na tela**, e com a câmera padrão quem olha para o jogador que sobe o
  salão é **4** ou **2**, nunca 6 ou 0. Custou uma rodada nos três NPCs de fala
  da Sala Secreta da Ordem em 2026-08-13, todos pedidos em "leste" e todos
  entregues de costas. Ao receber ponto cardeal para NPC que dialoga,
  **perguntar para onde ele deve OLHAR na tela**, não só que célula encarar.
- **NPC com sprite de CLASSE DE JOGADOR nasce pedindo o penteado 0, e o 0 não
  existe.** Sprite de NPC normal (`view id` ≥ 44, do `npcidentity.lub`) traz a
  aparência pronta do `npc_viewdb`; id de **classe** (`JOB_MERCHANT` = 5 e
  irmãos) cai noutro caminho — o `npcdb_checkid` recusa, e o
  `status_set_viewdata` (`src/map/status.cpp`, `case BL_NPC`) monta a aparência
  à mão num `else if (pcdb_checkid(class_))`: `look[LOOK_BASE] = class_` e
  `look[LOOK_HAIR] = cap_value(0, MIN_HAIR_STYLE, MAX_HAIR_STYLE)`. Com o nosso
  `min_hair_style: 0` (`conf/battle/client.conf`) isso dá **penteado 0**, e os
  penteados deste cliente vão de **1 a 42** nos dois sexos — não há
  `0_<sexo>.spr`. O corpo da classe existe; a cabeça é que não. Remédio, no
  `OnInit`: `setunitdata(getnpcid(0), UNPC_HAIRSTYLE, 1)` (e `UNPC_SEX`, que
  também nasce zerado pelo `memset`) — as duas **gravam no `nd->vd` do próprio
  NPC** (`clif_changelook`, `case LOOK_HAIR`, faz `vd->look[type] = val`), então
  valem para quem logar depois e não são pacote solto. **Nenhum dos 26 mil
  `script` do rAthena usa id de classe** — a varredura é barata e a ausência
  total é o aviso. Caso vivo: a Tranqueiras, `prontera 151,131`, 2026-08-12.
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
- **`disablenpc` NÃO desliga o NPC dentro da instância — a receita de §2 não
  vale para NPC de mapa de instância.** São dois campos diferentes e só um
  atravessa a clonagem: o `buildin_disablenpc` (`script.cpp:12388`) chama
  `npc_enable_target`, que mexe em `is_invisible` e `sc.option` e **nunca
  grava `nd->state`**; e é justamente `state`, e só ele, que o
  `npc_duplicate_sub` copia para a cópia (`npc.cpp:4655-4657`). Então
  `disablenpc "X"` num `OnInit` esconde o NPC do **mapa-molde**, onde ninguém
  entra, e **o clone de dentro da instância nasce ligado** — empilhado no
  substituto, com a regra velha de volta. Falha calada: os dois aparecem, o
  jogador clica no de cima, e qual é o de cima ninguém escolheu. Só o
  `script(DISABLED)` de tempo de parse propaga (`npc.cpp:3974`), e ele mora no
  arquivo do rAthena. **A saída é o `OnInstanceInit` do NPC substituto**, e ela
  é segura porque o `instance_addnpc` cria TODOS os clones antes de rodar
  qualquer `OnInstanceInit` — os dois laços estão um embaixo do outro em
  `instance.cpp:586-598`, com os comentários *"First add the NPCs"* e *"Now run
  their OnInstanceInit"*. Caso vivo: o seletor de dificuldade do Túmulo do
  Monarca, `npc/guerra/tumulo_do_monarca.txt`, 2026-08-12.
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
  *Esta capa foi consertada em 2026-08-10* (override no `db/guerra/item_db.yml`,
  do lado do servidor) — quem for conferir hoje acha 5, e a armadilha continua
  valendo para todo o resto do `item_db`.
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
- **MONSTRO NÃO TEM RESISTÊNCIA POR RAÇA — não existe "redução humano" para
  mob.** O `bonus2 bSubRace,RC_Player_Human` é bônus de **jogador**: o
  `battle_calc_cardfix` lê o `subrace` do `tsd`, e alvo `BL_MOB` **não tem ramo
  naquela função**. Não há como dar resistência a humano a um guardião por
  `db/`, por script ou por carta — e o pedido chega exatamente com essa
  palavra, porque é a que o dono conhece do lado do jogador. O que existe e
  serve é o **`md->damagetaken`** (o `DamageTaken:` do `mob_db`, também
  `setunitdata UMOB_DAMAGETAKEN`), aplicado no fim do `battle_calc_damage`
  (`battle.cpp:2072`) como multiplicador sobre tudo que acerta aquele monstro.
  É **por instância** — mora no `md`, não no `mob_db` —, então não contamina
  outros do mesmo ID. Mas é **inteiro em porcentagem**: `1` é o menor valor
  útil, ou seja **99% é o teto**, e 99,9% não cabe nele.
- **Dentro de castelo, a redução de 80% da guerra vale 24 HORAS POR DIA — e
  vale também quando o alvo é MONSTRO.** O mapflag é `gvg_castle`, posto
  estaticamente em `npc/mapflag/gvg.txt`, e o `mapdata_flag_gvg2`
  (`map.hpp:977`) só olha mapflag: não consulta o `agit_flag`. O `gvgon` da
  Guerra do Emperium acrescenta o `MF_GVG` por cima, mas a redução já estava
  ligada. Duas consequências: dano medido em castelo fora do horário de guerra
  é o **mesmo** da guerra (ótimo para testar), e qualquer resistência dada a um
  guardião **multiplica** com os `gvg_*_attack_damage_rate: 20` — 99% de
  redução no monstro com os nossos 20% que passam dá `0,20 × 0,01`, ou seja
  **0,2% do dano bruto**. Calibrar o HP sem fazer essa conta erra por duas
  ordens de grandeza.
- **`status_calc_mob_` sem nenhuma flag LIBERA o `md->base_status` e passa a
  usar o status compartilhado do `mob_db`.** O `if (!flag) { … aFree(md->base_status);
  … return 0; }` (`status.cpp:2812`) é a porta de saída de todo monstro comum.
  Quem enxertar ajuste de status de monstro **depois** dessa linha precisa
  garantir que alguma flag esteja ligada, senão escreve no registro do banco de
  monstros e altera **todos** os monstros daquele ID de uma vez — calado, e
  sobrevivendo até o próximo `@reloadmobdb`. O `setunitdata` não cai nessa
  armadilha porque aloca o `base_status` próprio antes de escrever
  (`script.cpp:19420`).
- **Desligar um arquivo de castelo do rAthena leva 17 BANDEIRAS junto, e nada
  no log diz isso.** Cada `npc/guild/<castelo>.txt` define, além do Emperium e
  do Gerente, **quatro bandeiras no feudo, doze dentro do castelo e uma na
  cidade** — nos dezenove que desligamos em 2026-08-13 eram **279 bandeiras em
  27 mapas**, incluindo Prontera, Geffen, Payon e Al De Baran. Bandeira que
  some não emite aviso; quem percebeu foi o dono, na tela. **Ao comentar
  qualquer `npc:` de castelo, contar o que mais estava naquele arquivo.** A
  boa notícia é que bandeira **não é atrelada ao castelo**: o que a prende é
  uma linha, o `FlagEmblem GetCastleData("<mapa>", CD_GUILD_ID)`, e trocar o
  mapa ali faz a bandeira hastear outro clã (ver
  `npc/guerra/bandeiras_do_feudo.txt`).
- **Nome de NPC pode ter ESPAÇO, e um `\S+` no lugar dele perde arquivo
  inteiro.** Os campos de uma linha de NPC são separados por **TAB**; o nome é
  `[^\t]+`, não `\S+`. As bandeiras dos cinco castelos de Payon se chamam
  `Bright Arbor#1-2`, e o regex errado devolveu **219 bandeiras em vez de
  279** — sem erro, com Payon zerado e um total plausível demais para
  desconfiar. Só uma coluna de zeros numa listagem por arquivo denunciou:
  **listar por arquivo, e não só o total**, é o que transforma esse tipo de
  perda silenciosa em algo visível.
- **No renewal, a chance de acerto é literalmente `hit − esquiva` em pontos
  percentuais — e o piso de 5% esconde o quanto se está longe.** A taxa base do
  renewal é **zero** (no pre-renewal era 80), e a única coisa somada a ela é
  aquela subtração; o resultado é travado entre `min_hitrate: 5` e
  `max_hitrate: 100` (`battle.cpp:3289-3341`). Duas consequências que enganam
  juntas: **cem pontos cobrem a escala inteira**, de "nunca acerta" a "nunca
  erra" — não há meio-termo suave para calibrar; e **tudo que está 95 pontos
  abaixo parece igual**, porque o piso devolve 5% tanto para quem está a 10
  pontos quanto para quem está a 300. O `hit` de monstro é `nível + DEX + 150`
  (`status.cpp:2635`), o que dá 309 no Guardião Soldado e 422 no Arqueiro — os
  dois no piso contra jogador de guerra, com sintomas idênticos. Antes de somar
  precisão, **ler a Esquiva do alvo**: o número certo é `esquiva + a chance
  desejada`, e um bônus somado em monstros de bases diferentes espalha o
  resultado por toda a escala.
- **No `mob_db` do renewal, `Attack2` NÃO é o ATQ máximo — vira `rhw.matk`.**
  O parser (`mob.cpp:5107`) manda `Attack2` para `status.rhw.matk` sob
  `RENEWAL` e só cai em `rhw.atk2` no pre-renewal. Quem lê `Attack: 873,
  Attack2: 163` como "dano de 163 a 873" erra duas vezes: o mínimo e o máximo
  saem os dois do **`Attack`**, no `status_calc_misc`, como 80% e 120% dele
  (`status_base_atk_min`/`_max`, `status.cpp:2522`). Os dois campos são
  `uint16` — **teto de 65.535** para dano de monstro.
- **`guardian` sem índice é guardião TEMPORÁRIO, e é o que se quer fora de
  castelo com dono.** Com índice, ele ocupa um dos oito slots
  `CD_ENABLED_GUARDIAN` e passa a ser alcançado pelo `mob_guardian_guildchange`
  (`mob.cpp:3690`), que **apaga guardião de castelo sem dono** — o sumiço vem
  na primeira vez que alguém tocar na dona do castelo, e é calado. O preço do
  temporário é não ter respawn nem `guardianinfo`.
- **`killmonster` com o terceiro argumento tem o sentido INVERTIDO do que o
  nome sugere:** sem ele o rótulo dos mortos **não** dispara; `1` é que faz
  disparar (`doc/script_commands.txt`, `*killmonster`). Para limpeza silenciosa,
  omitir.
- **O cabeçalho do `map_cache.dat` tem 8 bytes, não 6.** É
  `uint32 file_size; uint16 map_count;` e o compilador o alinha em 8; ler a
  partir do byte 6 desalinha o arquivo inteiro e o leitor estoura umas dezenas
  de mapas adiante, longe da causa. O cabeçalho de cada mapa
  (`char name[12]; int16 xs; int16 ys; int32 len;`) tem 20 e esse não tem
  surpresa. Ver §5, entrada dos TRÊS `map_cache.dat`, para saber em qual deles
  procurar.
- **No `sshd_config` o PRIMEIRO valor vence, não o último — e isso inverte o
  sentido do número no nome do arquivo em `sshd_config.d/`.** É o contrário do
  `nginx`, do `sysctl` e de praticamente tudo que usa pasta `.d`, onde o último
  a falar ganha. O glob carrega em ordem alfabética, e a imagem Ubuntu da
  DigitalOcean já traz `50-cloud-init.conf` e `60-cloudimg-settings.conf`: um
  drop-in nosso chamado `99-` **perderia para os dois, calado** — o arquivo
  existe, o `sshd -t` aprova, e a diretiva simplesmente não vale. Por isso o
  nosso é `10-guerra.conf`. Entre o drop-in e o `sshd_config` principal não há
  disputa: o `Include` está na linha 12 e vence o que vier depois. Medido em
  2026-08-14. **A conferência que decide é `sshd -T`**, que imprime a
  configuração efetiva — ler o arquivo não prova nada. Cuidado com um
  sinônimo que engana na saída: `prohibit-password` é reimpresso como
  `without-password`.
- **Sessão SSH já aberta não prova endurecimento nenhum.** Ela foi autenticada
  antes da mudança e continua viva de propósito — é o que impede o tiro no pé.
  Testar sempre em **conexão nova**, e testar também o que deve FALHAR
  (`ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no`), não
  só o que deve funcionar.
- **`tr -dc … | head -c N` mata o script inteiro sob `set -o pipefail`.** O
  `head` fecha o cano ao completar os N bytes, o `tr` morre de **SIGPIPE**
  (exit 141), o `pipefail` propaga e o `set -e` encerra tudo — **sem imprimir
  uma linha**, porque SIGPIPE é silencioso. Parece que o script "terminou" no
  meio. Para gerar senha, `openssl rand -hex 16`, que não usa cano. Custou duas
  rodadas em 2026-08-14 no `provisiona.sh`.
- **O `needrestart` do Ubuntu 24.04 reinicia serviço sozinho durante o `apt`, e
  o `ssh.service` está na lista dele.** Script de provisionamento rodado *por*
  SSH pode ter a própria conexão derrubada no meio da instalação. Exportar
  `NEEDRESTART_SUSPEND=1` antes do `apt`.
- **O bit de execução do `rathena/` NÃO está no git, e no Linux isso vira
  `Permission denied`.** O vendor foi feito no Windows, onde o git não registra
  esse bit: o `rathena/configure` está no repositório como **`100644`**, e no
  Linux `./configure` responde *"Permission denied"* — mensagem que parece
  problema de dono, de `runuser` ou de montagem, e não é. A saída **não** é
  `chmod` (o próximo `git reset --hard` do deploy o desfaz) nem mexer no modo
  do arquivo de terceiro: é chamar o interpretador direto, `sh configure`.
  Vale para qualquer `.sh` que venha do vendor. Medido em 2026-08-14.
- **`libmariadb-dev` não basta para compilar o rAthena — falta o
  `libmariadb-dev-compat`.** O `configure` procura os nomes do **MySQL**
  (`mysql_config`, `mysql.h`, `-lmysqlclient`) e o pacote do Ubuntu instala tudo
  com nome MariaDB (`mariadb_config`, `/usr/include/mariadb/`). O resultado é
  `configure: error: MySQL not found or incompatible` **com o MariaDB
  instalado, no ar e aceitando conexão** — o que manda procurar defeito no
  banco, que está perfeito. O `-compat` existe só para fazer essa ponte.
- **A senha da conta de comunicação entre servidores tem teto de 23
  caracteres, e passar disso falha CALADO — apontando para o lugar errado.**
  O `char_logif.cpp:826` monta o pacote de conexão com
  `memcpy(WFIFOP(login_fd,26), charserv_config.passwd, 24)`: vinte e quatro
  bytes, ponto, **ainda que o `PASSWD_LENGTH` do banco seja 33**. Senha maior é
  truncada ali: o `conf/import/char_conf.txt` aceita, o banco guarda o hash da
  senha inteira, e o login-server hasheia os 23 primeiros e recusa. A mensagem
  que sai é *"The server communication passwords (default s1/p1) are probably
  invalid"* — que manda conferir `s1`/`p1` e o sexo `S` da conta, tudo já
  correto. Medido em 2026-08-15 com uma senha de 32 caracteres. O
  `ferramentas/configura_servidor.sh` gera 20.
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
| `REDUCAO-DE-DANO.md` | o que entra e o que escapa das duas reduções — a de cartas (resistência a humano) e a **geral de 80%** de guerra e PvP; a §1d é o inventário fechado do dano que escapa (veneno, sangramento e irmãos) | consulta, só a seção — **antes de discutir número de PvP** |
| `IMPLANTACAO.md` | o plano de subir para o servidor Linux — etapas, o que roda em qual máquina, e a regra de escopo do Mac | **§1 inteira antes de qualquer sessão no Mac**; depois só a etapa |
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

## 9. Se esta sessão está rodando no Mac

**Desde 2026-08-14 o projeto trabalha em três máquinas**, com papéis que não se
sobrepõem: o **Windows** faz tudo que o jogo lê e tudo que precisa do cliente; o
**Mac** faz infra (deploy, systemd, nginx, banco, scripts, site, documentação);
o **servidor Linux** só recebe `git pull` e nunca é editado à mão.

**No Mac só entra trabalho que não precisa do jogo para ser conferido.** Ficam
de fora: editar `npc/guerra/*.txt` e `db/guerra/*.yml` (são cp1252, e a
conferência é em jogo), qualquer coisa do cliente (GRF, `itemInfo.lua`, sprite,
patch de exe), compilar para Windows, e calibrar número de jogo.

**Ao esbarrar no limite, parar e sinalizar** — não adivinhar o resultado, não
editar arquivo de jogo "só para destravar", não abortar a etapa inteira:

> ⚠️ **Fora do escopo do Mac.** Isto exige `<o que exige>`. Anotei em
> `IMPLANTACAO.md` §9 para a próxima sessão no Windows. Sigo com o resto.

E então acrescentar a linha na §9 do `IMPLANTACAO.md` e continuar o que dá.

**A armadilha que o Mac introduz:** o APFS é *case-insensitive* por padrão, e
esconde exatamente o defeito que o Linux pune — um `import:` com maiúscula
errada funciona no Mac, funciona no Windows, e morre calado no Linux. É por isso
que a varredura de case roda **no deploy**, e não uma vez só.

O plano inteiro, com as etapas e o que já está apurado, está no
`IMPLANTACAO.md`.
