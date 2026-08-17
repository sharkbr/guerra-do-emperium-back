# O Atualizador — como o jogador recebe melhoria sem baixar 4,9 GB de novo

Escrito em 2026-08-15, quando o dono precisou entregar uma correção do cliente
(a pasta `AI_sakray`, sem a qual criar homúnculo devolve caixa de erro) e não
havia caminho nenhum para isso: o cliente inteiro sai por uma pasta do Google
Drive, e não há como mandar 40 KB para quem já baixou.

**O que ele é:** um `.exe` de ~9 MB que fica na raiz do cliente, no lugar do
atalho do jogo. Ao abrir, ele confere o servidor, aplica o que falta e mostra o
botão JOGAR.

```
Jogar.exe              o que o jogador clica
Jogar.ini              url do servidor e nome do exe do jogo (opcional)
patch\aplicados.txt    o que este cliente já tem
patch\atualizador.log  a última rodada, para quando algo der errado
```

**O arquivo se chama `Jogar.exe` desde 2026-08-16** — antes era
`Atualizador.exe`, e o dono trocou pelo motivo certo: o nome tem de dizer o que
fazer, não o que o programa é. O código **não depende do nome**: ele procura
`<nome do exe>.ini` e cai para `Atualizador.ini` se não achar, e os arquivos da
auto-atualização saem do nome do próprio exe. Trocar de novo é renomear e
pronto.

---

## 1. As três peças, e onde cada uma mora

| peça | onde | quem escreve |
|---|---|---|
| **o gerador** | `ferramentas/monta_patch.py` | nós, no Windows |
| **o registro** | `patcher/patches.txt` — **versionado** | o gerador |
| **o publicador** | `ferramentas/publica_patch.sh` | nós, no Windows |
| **os zips** | `C:\GuerraDoEmperium\patches\` — fora do git | o gerador |
| **o servidor** | `libraro:/var/www/patch/`, servido pelo Apache | o publicador |
| **o Atualizador** | esta pasta, em Go | nós |

O `patches.txt` **é** a `lista.txt` que o servidor serve: o publicador o envia
sem traduzir. Assim há uma fonte só, o git guarda o histórico do que foi ao ar,
e duas máquinas não inventam o mesmo número de patch.

## 2. O ciclo de um patch

```bash
# 1. o arquivo já está no cliente, testado em jogo (é sempre esta a ordem)
python ferramentas/monta_patch.py --nome "IA do homunculo" AI_sakray

# 2. confere o que vai no zip — a lista impressa é a hora de perceber engano
# 3. publica
ferramentas/publica_patch.sh

# 4. commita o registro
git add patcher/patches.txt && git commit
```

O `--desde 2026-08-14` varre o cliente por data de modificação, para quando a
mudança foi espalhada. **É a via preguiçosa e a mais perigosa** — ela pega
também o que foi tocado por engano —, por isso a lista sai impressa antes de
qualquer coisa ser publicada.

Para apagar arquivo do cliente do jogador: `--apagar data/algum.lub`. Vai
dentro do zip como `_patch_apagar.txt`, e o Atualizador processa depois de
extrair.

## 2b. Como o Atualizador chega a quem já tem o cliente

Quem baixou o cliente antes de 2026-08-15 não tem o Atualizador — e é
justamente esse pessoal que precisa dos patches. Para eles existe
`C:\GuerraDoEmperium\patches\Jogar-Guerra-do-Emperium.zip` (5,2 MB):
`Jogar.exe`, `Jogar.ini` e um `LEIA-ME.txt` em cp1252, para
extrair na pasta do jogo. Depois disso, tudo é automático — inclusive as
versões seguintes do próprio Atualizador (§3).

O zip é gerado à mão quando o exe muda. Quem baixa hoje pelo instalador não
precisa dele: o `Jogar.exe` se copia para a pasta do jogo sozinho (§2c).

## 2c. A instalação — o mesmo exe, do outro lado

**Desde 2026-08-16 este exe também é o instalador**, e não há um segundo
programa. Quem decide o que ele é hoje é a pasta em que ele está: com um
cliente nosso ao lado, atualiza; sem, instala.

**"Cliente nosso" são DOIS arquivos — o `data.grf` e o `GuerraDoEmperium.exe`
—, e a pergunta se faz com os dois.** Olhar só o `data.grf` foi o primeiro bug
relatado de fora: ele existe em qualquer instalação de Ragnarok, então quem
copiou o `Jogar.exe` para dentro de uma pasta de RO antiga foi tratado como
"já instalado", não baixou nada, e recebeu **"não encontrei
GuerraDoEmperium.exe"** ao clicar em JOGAR. Ver `PrecisaInstalar` no
`instala.go`, o `TestPrecisaInstalar`, e a seção do `HISTORICO.md`.

```
o jogador baixa Jogar.exe (9 MB)  ->  abre numa pasta vazia
  -> escolhe onde instalar, com o atalho já marcado
  -> baixa a base (3,4 GB) de cdn.filiponegrao.com.br
  -> copia a si mesmo para lá, escreve o Jogar.ini, cria o atalho
  -> emenda nos patches publicados desde que a base foi montada
  -> JOGAR
```

A base é a `base.txt` (`patcher/base.txt`, gerada por
`ferramentas/monta_cliente.py`), e ela tem **seis** campos contra os cinco de um
patch. O campo a mais é o tipo:

| tipo | o que é |
|---|---|
| `zip` | extraído por cima da raiz — exatamente como um patch |
| `bruto` | gravado direto no caminho que está no campo `arquivo` |

**O `bruto` existe por causa do `data.grf`**, que tem 2,95 GB num arquivo só.
Não há como fatiá-lo por arquivo, zipá-lo não ganha nada (já é comprimido por
dentro) e o zip custaria o dobro de disco no jogador. Então ele desce direto
para o destino, com retomada e conferido pelo sha no fim.

**As duas URLs são separadas** (`url` para patches, `base` para a instalação) e
isso não é detalhe: os patches saem do nosso droplet, que já os serve e são
pequenos; a base sai de um bucket com CDN, porque são 3,4 GB **por jogador** e
servi-los do droplet passaria isso pela mesma placa de rede que atende o
map-server. Ver `RECEITAS.md` §12.

**A retomada é obrigatória aqui, e não era antes.** Num patch de 40 KB uma
queda de conexão não custa nada; nos 2,95 GB do `data.grf` ela custa a
instalação inteira. O `baixa()` manda `Range: bytes=N-` e trata as duas
respostas possíveis — 206 continua, **200 recomeça**. O 200 é o caso que
engana: tratá-lo como continuação grudaria o arquivo inteiro no fim do pedaço
já baixado, e o sha só falharia no fim, depois de o jogador baixar tudo de novo.

Três decisões da tela, todas do mesmo princípio de que a instalação é
irreversível o bastante para merecer uma pergunta:

- **Pergunta antes de baixar.** Nenhum programa deve despejar 3,4 GB no disco
  de alguém sem dizer onde.
- **O padrão é `C:\GuerraDoEmperium`, não Arquivos de Programas.** O cliente
  escreve na própria pasta (screenshot, replay, `savedata`, o `patch\` daqui), e
  sob `Program Files` isso cai no Virtual Store ou pede elevação toda vez.
- **Instalação que falha não acende o JOGAR.** É a única tela do programa em que
  isso vale: sem cliente em disco, um botão aceso levaria a um segundo erro,
  mais confuso que o primeiro.

### Copiar a pasta do jogo NÃO basta — o registro é a outra metade

Descoberto no primeiro teste em outra máquina (2026-08-16), com os 4,2 GB
corretos em disco e o jogo sem abrir. O cliente escolhe o dispositivo Direct3D
lendo `HKLM\SOFTWARE\Gravity Soft\Ragnarok`, chave que só o **`Setup.exe`**
escreve. Sem ela: `Cannot init d3d OR grf file has problem` — que manda
conferir o GRF, e o GRF está perfeito.

E como a chave mora em `HKEY_LOCAL_MACHINE`, **é por isso que o cliente pede
elevação**. Os dois sintomas do primeiro teste eram a mesma causa.

Por isso a instalação faz três coisas que não são óbvias:

1. lança o jogo por **`ShellExecuteW`**, não por `exec.Command` — o
   `CreateProcess` do Go não sabe elevar, devolve `ERROR_ELEVATION_REQUIRED`;
2. cria o atalho com **`SLDF_RUNAS_USER`**, e o jogo herda o token elevado do
   Atualizador — um UAC só, na abertura;
3. roda o **`Setup.exe` no fim da instalação e espera ele fechar**, porque o
   cliente lê a chave na inicialização.

Detalhe da leitura: o Atualizador é 64-bit e o cliente é 32-bit, então a mesma
chave tem dois nomes. O `video.go` tenta `KEY_WOW64_32KEY` e o caminho
`WOW6432Node` explícito, e **na dúvida responde "configurado"** — abrir o Setup
para quem não precisa é pior do que deixar o jogo tentar.

## 3. As decisões que não são óbvias

**O patch é um zip extraído por cima, sem diff binário e sem GRF.** O cliente
tem `DataFolderFirst`, então arquivo solto em `data\` vence o `data.grf` — é
assim que todo o nosso conteúdo já chega. A consequência boa é a
idempotência: aplicar duas vezes não muda nada, e apagar o `aplicados.txt`
refaz tudo do zero sem estrago. Um formato com diff economizaria banda e
custaria a única propriedade que faz o suporte ser barato.

**O número só cresce e nunca se reaproveita.** Corrigir um patch publicado se
faz com um patch NOVO por cima. Editar a linha de um antigo não alcança quem
já o aplicou — e remover a linha faz o zip sumir do ar para quem ainda não
baixou.

**Mas o número sozinho NÃO identifica um patch, e o `aplicados.txt` é
conferido por número E sha256.** Não é zelo: a BASE tem numeração própria, que
também começa em 0001, e enquanto o registro morou dentro do `aplica` o
instalador anotava os pedaços do primeiro download no diário dos patches. Todo
cliente instalado até 2026-08-17 tinha `0002 As musicas` e `0003 A Guerra do
Emperium (1 de 2)` ali dentro — pedaços da base ocupando o número de dois
patches, que o Atualizador então pulava para sempre, com a barra cheia e a
mensagem *"Cliente atualizado"*. O sha faz o conteúdo ser a palavra final, e é
ele que **repara sozinho** um registro sujo: sha que não bate é patch que falta.
Por isso `leAplicados` devolve `map[int]string`, e por isso `aplica` não
escreve no diário — quem escreve é o laço de patches, o único dos dois
chamadores que tem o que registrar. Ver `HISTORICO.md`, "O 'Unknown Item' que
não era do servidor".

**O zip sobe antes da lista.** Na ordem inversa, todo cliente que abrisse o
Atualizador naquele intervalo pediria um arquivo que ainda não existe. Pelo
mesmo motivo, zip antigo **não se apaga** do servidor: quem instalou o cliente
ontem ainda vai baixar o patch 0001 amanhã.

**Nada pode impedir o jogador de jogar.** Rede fora, servidor fora, sha que não
confere — em todos os casos o Atualizador diz o que houve e libera o botão com
o cliente que já está em disco. É a única peça do projeto que roda na máquina
dos outros, e travar ali é pior do que não atualizar.

**O Atualizador não entra em patch comum.** Windows não deixa um programa
gravar por cima do próprio exe em execução — mas deixa **renomear**. O canal
próprio (`patcher.txt` no servidor) se apoia nisso: baixa, confere o sha,
renomeia a si mesmo para `patch\Jogar.velho`, põe o novo no lugar, lança e
morre; o novo apaga o velho ao subir. O `monta_patch.py` recusa pôr o
`Jogar.exe` num zip, para ninguém tentar o caminho que não funciona.

## 4. O Atualizador em si

Go, sem uma única dependência externa: o Win32 é chamado por
`syscall.NewLazyDLL` contra user32, gdi32 e kernel32. O binário que vai para a
máquina dos jogadores não tem código de terceiro nenhum além da biblioteca
padrão do Go.

```
main.go      o fluxo, o Jogar.ini e o desvio instalar/atualizar
patch.go     lista, download com retomada, sha256, extração
instala.go   o primeiro download: base.txt, disco, a cópia de si mesmo
atalho.go    o .lnk da Área de Trabalho, por COM
pasta.go     a caixa nativa de escolher pasta
auto.go      a troca do próprio exe
janela.go    a janela, em Win32 puro
registro.go  patch\atualizador.log
recursos/    a arte da capa

atalho_test.go   o .lnk é mesmo um .lnk, e aponta para onde devia
instala_test.go  a base do servidor de verdade, e a RETOMADA
```

**Os testes existem porque duas coisas aqui não se provam clicando.** O
`atalho.go` chama COM percorrendo vtable, e ali um índice errado **trava o
processo** em vez de devolver erro, com a pilha dentro do shell do Windows. E a
retomada só se manifesta quando a conexão cai no meio de 2,95 GB — que ninguém
provoca de propósito na hora de testar, e que falharia **depois** de o jogador
baixar tudo.

```
go test ./...          roda tudo (o de retomada fala com o CDN de verdade)
go test -short ./...   só o que roda sem rede
```

Compilar:

```bash
cd patcher
go build -ldflags -H=windowsgui -o Jogar.exe .
```

O `-H=windowsgui` é o que impede a janela preta de console de abrir junto.

**Publicar versão nova:** subir o `const VERSAO` em `main.go` e rodar
`ferramentas/publica_patch.sh --atualizador`. Quem tem a antiga troca sozinho na
próxima abertura.

## 4b. A janela — por que ela é desenhada à mão

A primeira versão usava a moldura do Windows com um botão e uma barra de
progresso nativos dentro. Funcionava, e **parecia um utilitário** — o dono
comparou lado a lado com o patcher do bRO e o veredito foi imediato. Um servidor
que vende nostalgia não abre com uma caixa de diálogo cinza.

A de hoje (2026-08-16) segue o formato que o jogador de RO reconhece: moldura
própria em vez da barra do Windows, arte ocupando quase tudo, e um rodapé com o
estado, a barra larga e o **JOGAR** grande à direita. Nada disso é controle
nativo — são ~600 linhas de GDI.

Três armadilhas que apareceram desenhando isso, e as três falham **calado**:

- **A arte tem de ser preparada ANTES de a janela existir.** Decodificar o JPEG
  leva ~100 ms, e um `WM_PAINT` que chegue nesse intervalo pinta o retângulo
  vazio — que fica assim até algo passar por cima da janela.
- **`StretchDIBits` falha de vez em quando e mente no `GetLastError`**
  (`CLAUDE.md` §5). A arte entra por `CreateDIBSection`, copiando os pixels na
  memória do bitmap: sem conversão, sem escala, sem chamada que possa falhar.
- **Interpolar cor em tipo sem sinal.** O gradiente que escurece (240 → 200) faz
  `r2-r1` dar −40 num `uintptr`, que vira um número astronômico e a cor sai
  aleatória. O sintoma foi o botão verde nascer **ciano** e a barra dourada
  nascer **invisível**, as duas de uma vez — a conta é a mesma.

E uma que não é armadilha, é regra do Win32: sem barra de título do Windows,
quem torna a janela arrastável é o `WM_NCHITTEST` devolvendo `HTCAPTION` na
faixa de cima. Os dois botões dela precisam devolver `HTCLIENT`, senão o clique
vira arrasto e eles nunca recebem `WM_LBUTTONDOWN`.

## 4c. O ícone

```bash
cd patcher && go run ./icone recursos/icone-origem.png
```

Sai daí o `recursos/icone.ico` (para atalho, site, instalador) e o
`icone_windows_amd64.syso` — o arquivo-objeto COFF que o `go build` embute
sozinho, e que é o único jeito de um programa Go ter ícone. **O `.syso` é
versionado**, e o gerador roda só quando o desenho mudar.

A ferramenta conhecida para isso é o `rsrc`, de terceiro. O nosso existe pelo
mesmo motivo do resto do Atualizador: o que vai para a máquina dos jogadores não
deve depender de binário que ninguém neste projeto leu. São ~200 linhas, e o
formato não muda desde 1993.

Três coisas que fazem o ícone sair errado, e todas falham calado:

- **Ícone no exe e ícone na JANELA são coisas separadas.** O recurso faz o
  Explorer desenhar o arquivo; para aparecer na barra de tarefas e no Alt+Tab é
  preciso pôr o `hIcon` na classe da janela. É comum acertar o primeiro e achar
  que o segundo veio junto.
- **Cada folha da árvore de recursos precisa de uma relocação.** Sem elas o
  ícone aponta para o lugar errado dentro do exe, e o Windows mostra o ícone
  padrão — indistinguível de "não pus ícone nenhum".
- **Reduzir sem ponderar pelo alfa deixa auréola escura.** O preto transparente
  das bordas entra na média e suja o contorno. O gerador pondera.

Nos tamanhos até 64 o ícone vai como BMP, e o 256 vai como PNG: PNG dentro de
ícone só é entendido a partir do Vista, e ainda há jogador de servidor privado
no 7 — mas nenhum Windows mostra 256x256 num contexto que não entenda PNG, e o
BMP daquele tamanho custaria 256 KB contra 13 do PNG.

## 5. O que falta

- **Assinatura dos patches.** Hoje a garantia é o sha256 do registro servido
  por HTTPS — quem controlasse o servidor poderia trocar os dois. Assinar com
  chave nossa e conferir no Atualizador é o próximo degrau.
- **Painel de notícias.** Foi decidido fora da v1 (2026-08-15). O skin do
  `PatchClient\` do kRO, na raiz do cliente, tem os botões desenhados se um dia
  for a hora.
