# O Atualizador — como o jogador recebe melhoria sem baixar 4,9 GB de novo

Escrito em 2026-08-15, quando o dono precisou entregar uma correção do cliente
(a pasta `AI_sakray`, sem a qual criar homúnculo devolve caixa de erro) e não
havia caminho nenhum para isso: o cliente inteiro sai por uma pasta do Google
Drive, e não há como mandar 40 KB para quem já baixou.

**O que ele é:** um `.exe` de ~9 MB que fica na raiz do cliente, no lugar do
atalho do jogo. Ao abrir, ele confere o servidor, aplica o que falta e mostra o
botão JOGAR.

```
Atualizador.exe        o que o jogador clica
Atualizador.ini        url do servidor e nome do exe do jogo (opcional)
patch\aplicados.txt    o que este cliente já tem
patch\atualizador.log  a última rodada, para quando algo der errado
```

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
`C:\GuerraDoEmperium\patches\Atualizador-Guerra-do-Emperium.zip` (5,2 MB):
`Atualizador.exe`, `Atualizador.ini` e um `LEIA-ME.txt` em cp1252, para
extrair na pasta do jogo. Depois disso, tudo é automático — inclusive as
versões seguintes do próprio Atualizador (§3).

O zip é gerado à mão quando o exe muda; o pacote do primeiro download, quando
existir, leva os dois arquivos já dentro (`PENDENCIAS.md` §5b).

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
renomeia a si mesmo para `patch\Atualizador.velho`, põe o novo no lugar, lança
e morre; o novo apaga o velho ao subir. O `monta_patch.py` recusa pôr o
`Atualizador.exe` num zip, para ninguém tentar o caminho que não funciona.

## 4. O Atualizador em si

Go, sem uma única dependência externa: o Win32 é chamado por
`syscall.NewLazyDLL` contra user32, gdi32 e comctl32. O binário que vai para a
máquina dos jogadores não tem código de terceiro nenhum além da biblioteca
padrão do Go.

```
main.go      o fluxo e o Atualizador.ini
patch.go     lista, download, sha256, extração
auto.go      a troca do próprio exe
janela.go    a janela, em Win32 puro
registro.go  patch\atualizador.log
recursos/    a arte (a mesma do site)
```

Compilar:

```bash
cd patcher
go build -ldflags -H=windowsgui -o Atualizador.exe .
```

O `-H=windowsgui` é o que impede a janela preta de console de abrir junto.

**Publicar versão nova:** subir o `const VERSAO` em `main.go` e rodar
`ferramentas/publica_patch.sh --atualizador`. Quem tem a antiga troca sozinho na
próxima abertura.

**A armadilha que custou uma rodada:** a arte é preparada **antes** de a janela
ser criada. Decodificar o JPEG leva ~100 ms, e um `WM_PAINT` que chegue nesse
intervalo pinta o retângulo de cima vazio; como daí em diante só a faixa de
baixo é invalidada (para o progresso não fazer a arte piscar), aquele preto
ficaria na tela até algo passar por cima da janela.

## 5. O que falta

- **Ícone e manifest.** O exe usa o ícone padrão do Windows e a barra de
  progresso sai no estilo clássico, por falta de um `.syso` de recursos.
  Nenhum dos dois muda o que o programa faz.
- **Assinatura dos patches.** Hoje a garantia é o sha256 do registro servido
  por HTTPS — quem controlasse o servidor poderia trocar os dois. Assinar com
  chave nossa e conferir no Atualizador é o próximo degrau.
- **Painel de notícias.** Foi decidido fora da v1 (2026-08-15). O skin do
  `PatchClient\` do kRO, na raiz do cliente, tem os botões desenhados se um dia
  for a hora.
