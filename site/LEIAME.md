# O site — criação de conta e painel do jogador

Um binário Go que serve quatro telas e nove chamadas de API. Escrito em
2026-08-14, para o beta; a área logada ganhou download, destravamento de
personagem e chamados em 2026-08-22.

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

`sql/site.sql` cria duas. A `guerra_site_cadastro`, cujo cabeçalho explica as
duas decisões que não são óbvias — por que guardamos **hash** de CPF/celular e
não o número, e por que o `account_id` **nasce nulo** —, e a
`guerra_site_chamado`, que é a dos tickets.

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

A `db` fala **latin1** e serve o que o jogo lê (`login`, `char`). A `dbTexto`
fala **utf8mb4** e serve só a `guerra_site_chamado`.

Não há meio-termo: o charset é escolhido na **abertura** da conexão, e é ele que
decide como o MySQL interpreta os bytes que chegam. Chamado é texto livre de
jogador, com acento e emoji, e nunca passa pelo jogo — guardá-lo em latin1
perderia calado tudo o que não coubesse em cp1252. Com uma conexão só, o acento
viraria mojibake ou a gravação seria recusada inteira, as duas caladas.

**A volta do mesmo problema está na leitura**, e é a parte fácil de esquecer:
nome de personagem chega em latin1, e o nosso `char_guerra.txt` permite acento
em nome. Sem converter, o `encoding/json` troca cada byte acentuado por U+FFFD
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

