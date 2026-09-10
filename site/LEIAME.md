# O site — criação de conta e painel do jogador

Um binário Go que serve cinco telas e treze chamadas de API. Escrito em
2026-08-14, para o beta; a área logada ganhou download, destravamento de
personagem e chamados em 2026-08-22, e o painel de usuários em 2026-09-10.

## Por que Go, e não Node

Não foi gosto: a máquina tem **961 MB** e o map-server sozinho ocupa 250–400 MB.
Este processo fica em torno de 20 MB de RSS; um Node ficaria em 150–300, que ali
é dinheiro de verdade. O deploy também fica igual ao resto do projeto — um
arquivo e uma unit.

## Rodar

```
cp config.exemplo.env config.env     # e preencha
set -a && . ./config.env && set +a
go run .
```

O `config.env` **não vai para o git** — mesma regra do `rathena/conf/import/`.

Para rodar no Mac contra o banco do servidor (que só escuta em `127.0.0.1`):

```
ssh -f -N -L 3399:127.0.0.1:3306 libraro
# e no DSN:  ...@tcp(127.0.0.1:3399)/guerra
```

**Não crie conta de verdade assim.** O `SITE_SEGREDO` local é descartável, e é
ele que gera o hash do documento — as contas criadas com um segredo diferente do
de produção não seriam reconhecidas pelo limite depois.

## As tabelas

`sql/site.sql` cria três: a `guerra_site_cadastro`, cujo cabeçalho explica as
duas decisões que não são óbvias — por que guardamos **hash** de CPF/celular e
não o número, e por que o `account_id` **nasce nulo**; a `guerra_site_chamado`,
que é a dos tickets; e a `guerra_site_admin_log`, que é o registro de moderação
do painel de usuários.

**Nenhum dos dois deploys roda SQL.** Eles fazem `git pull`, compilam e
reiniciam; não há passo de migração em lugar nenhum. Tabela nova é aplicada à
mão **antes**, e o site sobe sem ela sem reclamar — a falha aparece na cara do
primeiro jogador que usar a função. O arquivo é todo
`CREATE TABLE IF NOT EXISTS`, então rodá-lo inteiro é seguro:

```
ssh libraro 'mysql guerra' < site/sql/site.sql
```

## Publicar o site sem derrubar ninguém

```
ferramentas/implanta_site.sh      # do Mac; reinicia só o guerra-site
```

O `implanta.sh` completo reinicia os quatro servidores do jogo quando `rathena/`
muda, e isso **derruba todo mundo que estiver jogando**. Como o repositório é um
só, uma correção de CSS pode chegar junto com um NPC que alguém commitou do
Windows — e aí o deploy completo cobra o preço do jogo por uma mudança de site.

O `implanta_site.sh` recompila e reinicia **apenas** o `guerra-site`. A mudança
de jogo que vier de carona fica no disco, é **listada no fim** do script, e
continua pendente para o próximo deploy completo (é o `.carimbo-jogo` que
garante isso — `RECEITAS.md` §13).

## Duas conexões com o banco, e cada uma só encosta nas tabelas dela

A `db` fala **latin1** e serve o que o jogo lê (`login`, `char`, e também o
`loginlog` e o `ipbanlist` do painel de usuários). A `dbTexto` fala **utf8mb4** e
serve as duas tabelas de texto escrito à mão: a `guerra_site_chamado` e a
`guerra_site_admin_log`.

Não há meio-termo: o charset é escolhido na **abertura** da conexão, e é ele que
decide como o MySQL interpreta os bytes que chegam. Chamado é texto livre de
jogador, com acento e emoji, e nunca passa pelo jogo — guardá-lo em latin1
perderia calado tudo o que não coubesse em cp1252. Com uma conexão só, o acento
viraria mojibake ou a gravação seria recusada inteira, as duas caladas.

**A volta do mesmo problema está na leitura**, e é a parte fácil de esquecer:
nome de personagem chega em latin1, e o nosso `char_guerra.txt` permite acento
em nome. E não é só o nome de personagem — o **e-mail da conta** passava direto
até 2026-09-10, porque o formulário exige ASCII no *usuário* mas o
`mail.ParseAddress` aceita byte acentuado no endereço. Sem converter, o `encoding/json` troca cada byte acentuado por U+FFFD
e o jogador não reconhece o próprio personagem. Quem converte é o `deLatin1` do
`banco.go` — feito à mão, sem `golang.org/x/text`, e conferido nos 256 bytes
contra o cp1252.

## Destravar personagem: a guarda é o `online = 0`, e ela vai no `UPDATE`

Há mapas que o rAthena conhece e o nosso cliente de 2021 ainda não tem, e o
jogador consegue chegar neles — e fica preso, porque toda entrada seguinte o põe
de volta no mesmo lugar.

O char-server carrega o personagem do banco na entrada e só escreve de volta na
saída. Um `UPDATE` com o jogador conectado seria **sobrescrito**, sem erro
nenhum. Por isso a condição vai no próprio `UPDATE`, e não só na leitura de
antes: entre ler e escrever o jogador pode ter entrado. Está no `CLAUDE.md` §5.

Duas coisas que o conserto faz além do óbvio: zera o `last_instanceid` (senão
quem ficou preso dentro de instância continua sendo mandado para a cópia dela), e
só mexe no ponto de retorno quando ele aponta para o **mesmo** mapa da
armadilha — um `save_map` legítimo em Payon não se perde.

## O limite de uma conta por pessoa

O jogo dá vantagens diárias por conta, então conta ilimitada estraga o desenho do
jogo — não só o cadastro. O site amarra cada conta a um documento.

**A honestidade sobre o CPF:** o dígito verificador é conta pública e gerador de
CPF válido acha-se em qualquer lugar. Como barreira contra multi-conta ele vale
**pouco** — segura engano de digitação, não segura quem quer burlar. Quem barra
de verdade é o **celular**, porque número custa dinheiro. Validar o nome contra a
Receita resolveria, mas as bases sérias (Serpro Datavalid) são pagas e exigem
contrato — está em `PENDENCIAS.md` §5 como desejo futuro.

## A verificação tem dois modos

```
SITE_VERIFICACAO=nenhuma    # a conta nasce na hora (beta)
SITE_VERIFICACAO=penelope   # manda código por WhatsApp e espera
```

Foi assim que o beta subiu no mesmo dia em que o site ficou pronto: a integração
com o WhatsApp viria só depois. **O detalhe que faz isso valer a pena** é que,
mesmo em `nenhuma`, o hash do documento é gravado igual — então o limite vale
desde o primeiro cadastro, e ligar a verificação depois não deixa para trás um
bolo de contas que nunca passaram por limite nenhum.

O endpoint do Penelope recebe `POST {"destino": "5511912345678", "mensagem": "…"}`.

## Três coisas que o rAthena impõe, e que já estão no código

| | |
|---|---|
| `user_pass varchar(32)` | é MD5 hex. Gravar texto puro cria conta que **nunca loga** |
| `email varchar(39)` | trinta e nove. O MySQL **trunca** em silêncio se passar |
| `login` é **MyISAM** | não tem transação — ver o cabeçalho de `banco.go`, é o que decide a ordem das gravações |

## O PIN é apagado, não mostrado

O `pincode` do rAthena é `varchar(4)` em texto puro — daria para simplesmente
ler e devolver na tela. Não devolvemos: mostrar põe o PIN no histórico do
navegador e em qualquer print. Apagando, o cliente pede um novo no próximo login,
o que resolve melhor o "esqueci".

## A imagem de fundo

Um lugar só: `web/estilo.css`, `.fundo { background-image }`. Enquanto não houver
arte, um gradiente segura o layout — o site nasce apresentável sem depender de
arquivo que ainda não existe. O `.veu` por cima é o que mantém o texto legível
sobre **qualquer** imagem que entre ali depois.

## Duas armadilhas que este site já cobrou

**O fundo do `body` cobre camada de `z-index` negativo.** Havia
`html, body { background: … }`, e isso escondeu a arte de fundo por completo.
Quando o `html` já tem fundo próprio, o do `body` **não propaga** para a tela —
vira uma caixa opaca, e na ordem de pintura do CSS ela vem *depois* dos
elementos de `z-index` negativo. Passou despercebido de 2026-08-14 a 15 porque
os dois eram quase pretos: o gradiente de reserva também nunca apareceu. Só foi
visto quando entrou uma imagem de verdade e ela também não apareceu. **A saída
não é ajustar o negativo, é não usar negativo:** fundo `0`, véu `1`, conteúdo
`2`, e o fundo morando só no `html`.

**`og:image` precisa de endereço absoluto.** Caminho relativo funciona no
navegador e **não** funciona ali — o robô que lê a página não tem base para
resolver. E falha calado: o cartão aparece, só que sem imagem.


## O painel de usuários

Estreou em 2026-09-10, depois de um jogador errar a senha algumas vezes e
ficar sem conseguir entrar. Fica em `admin.go` e `banco_admin.go`, e aparece
como um botão a mais no painel de quem é administrador.

**Quem entra:** `login.group_id >= 99` — o grupo `Admin` do `conf/groups.yml`,
o mesmo que dá o `@` no jogo. Não há um segundo conceito de "quem manda", de
propósito: dois divergiriam no dia em que alguém ganhasse ou perdesse um deles.
O grupo é lido do banco **a cada requisição**, e não guardado no cookie — tirar
o 99 de alguém fecha a porta na requisição seguinte, e não daqui a sete dias.

### A trava de senha errada é por CONTA, e o painel precisa dizer isso

Desde 2026-09-06 (`CLAUDE.md` §4.23) errar a senha sete vezes suspende **aquela
conta** por 15 minutos, gravadas no `unban_time`; o ban automático de faixa de
IP está desligado em `conf/guerra/login_guerra.txt`. Ou seja: o jogador que diz
que "travou a conta" travou mesmo, e a trava aparece na ficha.

**O problema que isso cria para o painel:** castigo aplicado por gente e trava
posta pela máquina moram na **mesma coluna**, e chegam aqui com a mesma cara. A
trava não deixa marca nenhuma no banco — era justamente isso que a dispensava
de tabela e migração. Sem separá-las, o operador lê "suspensa" na ficha de quem
só esqueceu a senha e pune de novo.

Quem separa é o `travaAutomatica` de `banco_admin.go`, e é **palpite
fundamentado**, não certeza: dois sinais que só coincidem na trava — prazo
curto (ela escreve exatamente 15 minutos) e erros de senha recentes o bastante
para terem chegado ao limite. O erro é para o lado seguro: um administrador que
suspenda alguém por 15 minutos vê o rótulo de trava e sabe o que fez; o
contrário é que faria punir duas vezes.

Na tela isso vira a situação **"travada sozinha"**, com cor própria e um aviso
dizendo que não é castigo de ninguém e que passa sozinha.

### Por que a lista de bloqueios de endereço continua ali

Porque o `ipban_enable` continua **ligado** — só a parte automática saiu. Um IP
banido à mão barra **antes do login**, o jogador vê "Rejected from Server", e
**nenhuma ficha de conta denuncia isso**. Normalmente a lista está vazia; é
quando não está que ela paga o espaço que ocupa.

Para amarrar uma faixa ao jogador, a ficha usa o `loginlog` e não a
`login.last_ip`: a `last_ip` só é escrita no login que **deu certo**, então ela
é cega justamente em quem nunca conseguiu entrar.

### Os três estados são exclusivos, e isso é escolha nossa

O rAthena tem duas colunas independentes (`state` e `unban_time`), e uma conta
pode ter as duas. Aqui cada botão escreve as **duas**, deixando a conta num
estado só:

| botão | `state` | `unban_time` |
|---|---|---|
| Bloquear | 5 | 0 |
| Suspender | 0 | a data |
| Reativar | 0 | 0 |

Sem isso, suspender por um dia quem estava bloqueado não soltaria ninguém no
dia seguinte — o prazo vence, o `state` fica, e o painel diz que a punição
acabou. Ver `ARMADILHAS-RATHENA.md`.

**Reativar também solta a trava automática**, e é o caminho rápido para o
jogador que não pode esperar o quarto de hora. A resposta avisa de uma coisa
que o banco não mostra: a contagem de erros vive **em RAM no login-server** e
não é zerada por escrever no `unban_time` — quem zera é acertar a senha (ou
cinco minutos sem erro novo). Reativar e errar de novo tranca outra vez.

### O que ele NÃO faz: expulsar quem está jogando

Bloquear escreve no banco, e escrever no banco não manda o pacote `0x2731` que
derruba a sessão aberta — isso só o `@block` do jogo faz. **O bloqueio vale a
partir do login seguinte.** Por isso a ficha mostra "N no jogo" e a resposta
avisa para dar `@kick`. É a informação que evita o mal-entendido mais provável
do painel.

### As travas

1. **A conta de sexo `S` não se bloqueia.** É com ela que o char-server e o
   map-server falam com o login-server; bloqueá-la derruba o jogo para todo
   mundo. A trava está na leitura **e** no `WHERE` de cada `UPDATE`, porque uma
   só se esquece.
2. **Não se bloqueia outro administrador, nem a si mesmo.** Um clique errado
   ali tira do jogo justamente quem consertaria o clique errado.
3. **Bloquear e suspender pedem a senha de quem está clicando; reativar não.**
   Mesma regra do resto do painel: o que mexe em *acesso* pede senha, porque um
   cookie roubado não pode bastar. Reativar **devolve** acesso — o pior que um
   cookie roubado faz com ele é desfazer uma punição, que se refaz num clique.
4. Sessenta ações por hora por administrador. Não é para conter o dono: é para
   um cookie roubado não bloquear o servidor inteiro em dois minutos.
5. Quem tem sessão e não é administrador recebe **404**, e não 403 — um 403
   confirma que a rota existe.

### O registro de moderação

Toda ação vai para a `guerra_site_admin_log` com quem fez, o que mudou (**de**
qual estado **para** qual — o "de" é o único lugar de onde o estado anterior
ainda pode ser lido depois de sobrescrito) e o motivo escrito à mão. O motivo é
obrigatório para bloquear e suspender, e volta na tela pelo botão *Histórico* —
sem ele seria um campo que só se escreve.

**Se a tabela não existir, a moderação acontece assim mesmo** e a falta vai
para o log com `ATENCAO:` na frente. A alternativa seria a tabela de auditoria
poder derrubar a moderação. O mesmo vale para o `loginlog` e o `ipbanlist`, que
são do rAthena e podem estar noutro banco: o painel perde os números de
tentativa e continua servindo para todo o resto.
