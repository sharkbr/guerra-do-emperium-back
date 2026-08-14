# Implantação — do HML ao servidor de produção

Plano escrito em **2026-08-14**, para levar o Guerra do Emperium da máquina de
homologação (este Windows) para um servidor Linux público.

**Como ler:** a §1 é a regra de escopo e vale para toda sessão no Mac — leia
inteira antes de qualquer etapa. As §§4–7 são as etapas, na ordem. A §8 guarda
as decisões que foram tomadas de propósito, para ninguém as redescobrir como se
fossem esquecimento.

Quando uma etapa terminar, **marque-a aqui** e registre o que foi feito no
`HISTORICO.md`, com data absoluta — a regra §7 do `CLAUDE.md` vale para este
arquivo como para qualquer outro.

---

## 1. Onde cada trabalho acontece — e o que fazer quando escapa

São três máquinas com papéis que **não se sobrepõem**. A confusão entre elas é o
risco de processo deste plano, e é por isso que esta seção vem antes das etapas.

| Máquina | Faz | Não faz |
|---|---|---|
| **Mac** | infra, deploy, systemd, nginx, banco (DDL), scripts, site, documentação | nada que o jogo leia |
| **Windows** (este) | tudo do cliente, teste em jogo, compilação MSVC, as ferramentas Python 2.7 | — |
| **Servidor Linux** | roda os quatro servidores; recebe `git pull` e build | nunca é editado à mão |

### A regra de escopo do Mac

**No Mac só entra trabalho que não precisa do jogo para ser conferido.**

O que está dentro:

- scripts de implantação, `systemd`, `nginx`, firewall, backup
- SQL de estrutura (criar banco, rodar os `.sql`, conferir charset)
- documentação (`.md` — são UTF-8 e podem ser editados à vontade)
- **renomear** arquivo por causa de case-sensitivity (é operação de git, não
  edita conteúdo)

O que está fora, e por quê:

| Fora do escopo | Por quê |
|---|---|
| Editar `npc/guerra/*.txt`, `db/guerra/item_db.yml`, `.lub` | são cp1252, e a conferência é em jogo |
| Qualquer coisa do cliente (GRF, `itemInfo.lua`, sprite, patch de exe) | as ferramentas são Windows, e o cliente não roda no Mac |
| Compilar para Windows | exige VS 2022 |
| Calibrar número de jogo (dano, preço, taxa) | só a tela decide |

### O sinal — o que o Claude deve fazer ao esbarrar no limite

Durante a execução no Mac vai acontecer de uma etapa de infra encostar em algo
de jogo. Quando isso acontecer, **o Claude para e sinaliza**, em vez de tentar
resolver. A forma:

> ⚠️ **Fora do escopo do Mac.** Isto exige `<o que exige>` — cliente / teste em
> jogo / ferramenta Python 2.7. Anotei em `IMPLANTACAO.md` §9 para a próxima
> sessão no Windows. Sigo com o resto da etapa.

E então **acrescenta uma linha na §9 deste arquivo** e continua o que dá para
continuar. O que não pode é: adivinhar o resultado, editar arquivo de jogo "só
para destravar", ou parar a etapa inteira por causa de um item.

**A armadilha específica do Mac:** o APFS é *case-insensitive* por padrão. Ele
esconde exatamente o defeito que o Linux pune — um `import:` com maiúscula
errada funciona no Mac, funciona no Windows, e morre calado no Linux. É o motivo
de a varredura da Etapa 2 existir e de ela rodar **no deploy**, não só uma vez.

---

## 2. O que já está apurado — não reabrir

Levantado em 2026-08-14, lendo o código. Estas respostas são a base do plano:

- **Linux serve, e sem mexer no build.** Todo o C++ nosso é `.hpp`/`.inc`
  incluído de dentro de arquivos que já compilam — nenhuma unidade de tradução
  nova, então o `Makefile.in` não muda. Os quatro servidores existem no alvo
  `server` do Makefile (`SERVER_DEPENDS=common login char map web import`).
- **Os itens não estão no banco.** `inter_athena.conf:176` tem
  `use_sql_db: no`; o conteúdo mora em `db/guerra/*.yml`, versionado. Os
  `sql-files/item_db*.sql` do rAthena estão inertes.
- **Nenhum estado nosso mora no banco.** Zero variáveis permanentes de servidor
  (`$var`) nos NPCs de `npc/guerra/`. O banco de produção **nasce vazio**.
- **O código custom é portável.** Só tipos de largura fixa (`int32`, `uint16`,
  `int64`) — nenhum `long`, que é a fonte nº 1 de divergência Windows→Linux.
  Funções `inline` puras, sem estado global, sem I/O, sem API de sistema. O
  `max()` do `reducao_piso` é função do rAthena (`cbasetypes.hpp:383`), não a
  macro do `<windows.h>`.
- **O MD5 de senha funciona com o nosso cliente.** O `clientinfo.xml` **não**
  tem `<passwordencrypt>`, que é o único caso em que o rAthena rejeita a
  conexão com MD5 ligado (`loginclif.cpp:312`). Ver Etapa 1.

---

## 3. O alvo — o que existe quando o plano terminar

Uma máquina Linux **x86_64** rodando os quatro servidores sob `systemd`, com
banco local fechado ao mundo, nginx na frente do web-server, backup diário fora
da máquina — e um comando só, rodado do Mac, que atualiza tudo:

```
ferramentas/implanta.sh
```

que por SSH faz `git pull` da branch principal, recompila o que mudou, e
reinicia os servidores na ordem certa.

---

## 4. Fase A — o que precisa ser feito no Windows

Estas duas etapas exigem o cliente. **Não são executáveis no Mac.** Se o Mac
chegar aqui, é o caso do sinal da §1.

### Etapa 1 — MD5 das senhas ✅ (2026-08-14)

> Feita no Windows em 2026-08-14, com as três contas do HML convertidas e os
> quatro servidores reiniciados. Falta só entrar uma vez pelo cliente — o
> char-server já autenticou com a senha hasheada. Ver `HISTORICO.md`, "A senha
> deixa de ser texto puro". O texto abaixo fica como o registro do porquê.

**Por que agora e não depois:** o rAthena guarda senha em **texto puro**
(`login_athena.conf:118`, `use_MD5_passwords: no`, que é o padrão). Vazamento de
banco expõe a senha de todo jogador, e gente reusa senha de e-mail. Ligar depois
do servidor abrir é possível, mas até lá as senhas estarão em texto puro em todo
backup que já tiver sido feito.

**Como funciona**, lido em 2026-08-14: no login normal o servidor hasheia a
senha recebida (`loginclif.cpp:279`) e compara com a coluna `user_pass`. Ou
seja, **o banco passa a guardar o hash**. O `logincnslif.cpp:80` já hasheia
sozinho ao criar conta pelo console.

**A única incompatibilidade** é com cliente que usa `<passwordencrypt>`: nesse
caso o servidor **recusa a conexão** com *"rejected from server"*
(`loginclif.cpp:312`). O nosso `clientinfo.xml` não usa — conferido. Se aparecer
essa mensagem no teste, é essa a causa e não outra.

**Onde a opção mora — feito em 2026-08-14.** Seguindo a lei da §2 do
`CLAUDE.md`, a opção é *regra*, e regra é versionada — só senha e IP ficam em
`conf/import/`. O que entrou:

1. `rathena/conf/guerra/login_guerra.txt`, com `use_MD5_passwords: yes` e o
   cabeçalho explicando o porquê;
2. `import: conf/guerra/login_guerra.txt` no `login_athena.conf`, **antes** do
   `import: conf/import/login_conf.txt` — o último import vence, e
   `conf/import/` tem de continuar com a última palavra;
3. a linha na tabela de enxertos do `CLAUDE.md` §2.

Assim a decisão viaja no git e não pode ser esquecida no servidor novo.

**Converter as contas que já existem NÃO é opcional, e a razão não é o
jogador.** A conta com que o char-server e o map-server se conectam ao login é
uma linha da mesma tabela (a de sexo `S`), e ela passa pelo mesmo hash
(`loginclif.cpp:411`). Sem converter, **o char-server para de conectar** — e o
sintoma é *"The server communication passwords (default s1/p1) are probably
invalid"* (`char_logif.cpp:279`), que aponta para a senha do `conf/import/` e
não para o MD5. Por isso a conversão é sem `WHERE`:

```sql
UPDATE login SET user_pass = MD5(user_pass);
```

De mão única: depois disso não há como voltar ao texto. Que é o ponto. E é
**uma vez só** — rodar de novo hasheia o hash e tranca todo mundo para fora.

Depois da conversão, **reiniciar** (`python ferramentas/servidor.py reiniciar`).
Quem só quiser derrubar o login-server pode: o `use_MD5_passwords` está **fora**
do bloco `if (normal)` do `login_config_read` (`login.cpp:606`), então o
`server:reloadconf` do console do login-server também o relê — mas os dois lados
têm de mudar juntos, e o banco não avisa qual está valendo.

**Como saber que deu certo:** logar no cliente com a senha de sempre. E conferir
no banco que a coluna virou 32 caracteres hexadecimais.

### Etapa 2 — apontar o cliente para o servidor ⬜

O `data\clientinfo.xml` tem `<address>127.0.0.1</address>`. Vai ter que apontar
para o IP (ou domínio) do servidor. **Fica para depois de a Fase B estar de pé**,
e é o que amarra este plano ao do instalador do patch — que é trabalho separado
e não está aqui.

Lembrar que o cliente inteiro está **fora do git**: essa alteração só existe
nesta máquina, e some em cliente novo.

---

## 5. Fase B — provisionar o servidor (do Mac)

### Etapa 3 — a máquina ✅ (2026-08-14)

**Feito:** droplet DigitalOcean `libraro-server`, **138.197.155.31**, Ubuntu
24.04.4 LTS, **x86_64** (atende a regra abaixo). 1 vCPU `DO-Regular`
compartilhada, 961 MB de RAM, 24 GB de disco.

É menor do que o recomendado, **de propósito**: a decisão do dono em 2026-08-14
foi abrir como servidor de teste, com ~20 jogadores simultâneos, e escalar
depois se crescer. A conta que sustentou isso: 20 jogadores custam ~4 MB de RAM
(a `map_session_data` dá 100–200 KB por personagem) e quase nada de CPU — o
map-server gasta CPU com IA de monstro, e o rAthena só roda a IA cara
(`mob_ai_sub_hard`) para monstro **perto de jogador**. O que pesaria de verdade
é a Guerra do Emperium, e a nossa é de **um castelo só**.

O aperto real é a **compilação**, não a operação: `g++ -O2` numa unidade grande
do map-server chega perto de 1 GB sozinho. Resolvido com **2 GB de swap**
(Etapa 4). Medir o consumo real depois de os quatro servidores subirem.



**x86_64, não ARM.** Em ARM (Graviton, Ampere) o `char` é *unsigned* por
padrão, e isso é fonte real de bug silencioso em código C++ com a idade do
rAthena. A economia não paga o risco.

Debian 12 ou Ubuntu LTS. Dimensionar depois de medir — servidor de RO é mais
sensível a CPU de núcleo único (o map-server é essencialmente uma thread) do que
a quantidade de núcleos.

### Etapa 4 — SO base e segurança ✅ (2026-08-14)

**Automatizada em `ferramentas/provisiona.sh`**, idempotente, rodada do Mac com
`ssh libraro 'bash -s' < ferramentas/provisiona.sh`.

Feito: swap de 2 GB (+ `vm.swappiness=10`), usuário de serviço **`ragnarok`**
sem sudo dono de `/opt/guerra-do-emperium`, chave SSH copiada do root, `ufw`
ativo abrindo só SSH/6900/6121/5121/80/443, e o endurecimento do SSH
(`ssh libraro 'bash -s -- endurece' < ferramentas/provisiona.sh`).

**Quem é quem, e por quê** — decisão do dono, 2026-08-14, e ela desvia da letra
desta etapa de propósito:

| Usuário | Papel | Privilégio |
|---|---|---|
| `root` | administra: scripts de atualização, `systemctl`, `apt` | entra **só por chave** (`prohibit-password`) |
| `ragnarok` | roda os quatro servidores | **nenhum**, sem sudo |

A etapa pedia "root login desabilitado". Não foi o que se fez, e a razão é que
os dois argumentos clássicos contra o root **não se aplicam aqui**: força bruta
morre com `PasswordAuthentication no` (não se adivinha chave ed25519), e rastro
de auditoria não tem a quem servir com **um** operador. O que um usuário com
`sudo` daria a mais seria o quebra-molas de digitar `sudo` — ergonomia, não
segurança, ainda mais com o sudo sem senha que a conta teria.

**A separação que importa foi mantida inteira:** o `ragnarok` não tem sudo. O
map-server processa pacote de gente anônima e o web-server recebe upload de
arquivo; são eles que um dia levam um estouro. O atacante cai no usuário do
processo e **ali fica**, em arquivos que voltam com um `git pull`.

Consequência prática para o `atualiza_servidor.sh`: rodando como root, ele
**não pode** fazer `git pull` direto no repositório do `ragnarok` — os arquivos
nasceriam `root:root` e o git ainda recusa com *"dubious ownership"*. A parte do
jogo vai com `runuser -u ragnarok`, só o `systemctl` fica como root.

**O perímetro inteiro é a chave privada do Mac** (`~/.ssh/ssh-libraro-key`), que
não tem passphrase — de propósito, para o deploy ser automatizável. Backup dela,
quando houver, criptografado.

Antes de qualquer coisa do rAthena:

- **usuário dedicado** para o servidor; o rAthena não precisa de privilégio
  nenhum e **não roda como root**
- **SSH por chave**, senha desabilitada, root login desabilitado
- **firewall** aberto só em: `6900` (login), `6121` (char), `5121` (map),
  `80`/`443` (site e patch), e a porta do SSH
- **`3306` nunca vai para a internet** — o MariaDB escuta em `127.0.0.1` e ponto.
  É o erro clássico e catastrófico.
- **`8888` (web-server) também não é exposta direta** — vai atrás do nginx na
  Etapa 8. Ele recebe upload de arquivo de usuário anônimo num HTTP embutido.

### Etapa 5 — dependências e a primeira compilação 🟡 (2026-08-14, falta compilar)

**Dependências instaladas** pelo `ferramentas/provisiona.sh`: `build-essential`
(GCC 13.3), `zlib1g-dev`, `libmariadb-dev`, `libpcre3-dev`, `git`, `make`,
`pkg-config`, mais `mariadb-server`, `nginx` e `ufw`. **A compilação ainda não
foi feita** — é o `ferramentas/atualiza_servidor.sh`.

**É o marco de risco do plano.** É aqui que se descobre se o código custom passa
pelo GCC — e, pela §2, o esperado é que passe.

Dependências, lidas do `tools/docker/Dockerfile` do próprio rAthena (que usa
Alpine; no Debian os equivalentes):

```
build-essential  zlib1g-dev  libmariadb-dev  git  make
```

O `libpcre3-dev` é opcional (habilita comandos de NPC com regex) — o `configure`
avisa se faltar, e a ausência não impede a subida.

```
./configure
make server
```

**O que esperar:** erros de compilação, se houver, serão de header transitivo
que o MSVC incluía sozinho ou de conversão que o GCC recusa. São barulhentos e
baratos. Corrigir em `src/custom/` quando for nosso; se for em arquivo do
rAthena, parar e pensar — a lei da §2 vale aqui também.

**Como saber que deu certo:** os quatro binários existem
(`login-server`, `char-server`, `map-server`, `web-server`).

### Etapa 6 — banco 🟡 (2026-08-14, falta rodar os `.sql`)

**Feito pelo `ferramentas/provisiona.sh`:** MariaDB 10.11.14 escutando só em
`127.0.0.1`, banco `guerra` e usuário `guerra`@localhost com senha de 32
caracteres em `/root/senha-banco.txt` (modo 600, fora do git).

Charset fixado **antes** de qualquer tabela nascer, que é o ponto do passo 2
abaixo. Conferido com o teste que a etapa pede, e com bytes de verdade: um
`x'4D61E7E3'` ("Maçã" em cp1252) gravado e lido de volta **byte por byte**,
`CHARSET(t) = latin1`. Duas afinações para a máquina de 1 GB:
`performance_schema = OFF` (devolve 100–200 MB) e `innodb_buffer_pool_size`
fixo em 96 MB.

**Falta rodar os quatro `.sql`** do passo 4 — dependem do repositório estar
clonado.

**Nasce vazio.** Não há migração de HML — ver §2.

1. instalar MariaDB, escutando só em `127.0.0.1`
2. **fixar o charset antes de criar as tabelas.** As 105 colunas de texto são
   `latin1`; se a distro instalar com `utf8mb4` como default do servidor, as
   tabelas nascem erradas e o defeito só aparece quando alguém criar personagem
   acentuado. Conferir com `SHOW VARIABLES LIKE 'character_set%'`.
3. criar banco e usuário com senha forte (a senha vai para `conf/import/`, não
   para o git)
4. rodar, nesta ordem:
   - `sql-files/main.sql`
   - `sql-files/logs.sql`
   - `sql-files/web.sql`
   - `sql-files/guerra_arena_pvp.sql` ← **o nosso**, a `guerra_pvp_placar` da
     Honra de Combate

**Sem isso a Honra de Combate falha de um jeito que engana:** ninguém pontua,
mas o anúncio de morte continua saindo (`PENDENCIAS.md` §1).

**Como saber que deu certo:** gravar e ler de volta uma string acentuada numa
coluna de texto. É o teste que pega o charset errado antes de ele custar caro.

### Etapa 7 — `conf/import/` na máquina alvo ⬜

**Sim, é criado à mão no servidor, e é a única configuração que não vem do git.**
É de propósito: ali moram senha do banco e IP, que não podem ser versionados.

O que precisa existir:

- `conf/import/inter_conf.txt` — credenciais do banco
- `conf/import/login_conf.txt`, `char_conf.txt`, `map_conf.txt` — IP público,
  nome do servidor

**O script de deploy nunca encosta nesta pasta.** Um `git checkout -f`
distraído apaga a configuração do servidor inteiro — é o acidente mais fácil de
cometer neste plano.

Vale criar, junto, um `conf/import-exemplo/` **versionado**, com as chaves e sem
os valores. Hoje o conteúdo dessa pasta só existe como conhecimento desta
máquina.

### Etapa 8 — nginx ⬜

Duas funções:

1. **proxy do web-server** (`8888`), com limite de tamanho de corpo e rate
   limit. Sem ele o emblema de clã não sobe — e a falha é *calada*
   (`CLAUDE.md` §3).
2. **servir os arquivos de patch** por HTTP estático, que é o gancho para o
   instalador do patch (trabalho separado, fora deste plano).

### Etapa 9 — systemd ⬜

Quatro units, uma por servidor, com `After=` expressando a ordem que o
`ferramentas/servidor.py` já conhece: **login → char → web → map**. O `web`
sobe junto de propósito, para não ser esquecido de novo — foi o que motivou
aquele script em 2026-08-04.

Vale que as units façam o que o `servidor.py status` faz: dizer **o que quebra**
quando cada peça está fora.

### Etapa 10 — backup ⬜

**A medida mais valiosa do plano.** Em servidor de jogo, perda de dados acontece
muito mais que invasão, e o efeito é o mesmo: jogador perde item e vai embora.

- `mysqldump --default-character-set=latin1` — **o parâmetro não é opcional**,
  sem ele os acentos morrem no dump e viram U+FFFD irreversível
- diário, com retenção
- **fora da máquina**

E um teste de **restauração**, uma vez. Backup nunca testado é backup que não
existe.

---

## 6. Fase C — o deploy

### Etapa 11 — a varredura de pré-voo ⬜

Três conferências que rodam **antes** de qualquer subida, e que existem porque
as três falham caladas no Linux e não falham no Mac nem no Windows:

1. **case-sensitivity** — todo `import:`, `- Path:` e `npc:` batendo
   exatamente com o nome do arquivo em disco. Um erro aqui faz o arquivo não
   carregar, sem log.
2. **fim de linha** — nenhum `\r` sobrando. O `npc_parsesrcfile` corta por
   `\n`, e o `\r` que sobra entra dentro do campo: em nome de evento, vira
   parte do nome e o evento nunca dispara.
3. **U+FFFD** — nenhum `\xef\xbf\xbd` nos arquivos que o jogo lê
   (`CLAUDE.md` §5).

Roda no Mac, roda no deploy, e é rápida. **É a rede de proteção da §1.**

### Etapa 12 — `ferramentas/implanta.sh` ⬜

Roda **no Mac**. Faz, por SSH:

```
git pull <branch principal>  →  make server  →  restart na ordem
```

**O detalhe que evita o problema do ovo e da galinha:** o script que roda no
servidor vem do próprio repositório, então o `pull` tem de vir **antes** de
chamá-lo. Na prática, o wrapper do Mac é fino:

```
ssh <servidor> 'cd <raiz> && git pull && ferramentas/atualiza_servidor.sh'
```

e toda a lógica mora no `atualiza_servidor.sh`, versionado.

Requisitos:

- **idempotente** — rodar duas vezes não pode quebrar nada
- **não recompila se `src/` não mudou** — build só quando precisa
- **nunca toca `conf/import/`**
- **roda a varredura da Etapa 11 antes de reiniciar**, e aborta se falhar
- **diz o que fez** — quais commits entraram, se compilou, quais serviços
  reiniciaram

**Uma decisão a tomar quando chegar lá:** mudança que é só de `db/` ou de script
de NPC não precisa de restart — precisa de `@reloadscript`, `@reloaditemdb` e
irmãos (`CLAUDE.md` §3). Um deploy que sempre reinicia o map-server derruba
todo mundo por causa de um preço de loja. Vale o script distinguir os dois
casos, mas **isso é otimização, não requisito da primeira versão**.

---

## 7. Fase D — validar

### Etapa 13 — as sondas ⬜

Não há teste novo a inventar: o roteiro já está escrito no `PENDENCIAS.md`. O
que importa aqui é rodar **algumas delas no Linux**, não porque a plataforma
seja suspeita, mas porque é o teste que já existe e é barato:

- a razão de **5x** de dano dentro e fora da arena (§1i)
- a **Chuva de Moedas** — é o único teste que pega a morte do enxerto mais
  frágil do projeto, o que *substitui* uma linha do rAthena (§1i)
- a escala do **guardião** pela defesa do castelo (§1s)
- **acentuação desenhada** em qualquer NPC — é o teste barato que pega erro de
  cp1252 ponta a ponta, e no Linux ele cobre também o charset do banco

### Etapa 14 — o corte ⬜

Manter o HML de pé até o Linux passar por tudo acima. Se algo aparecer em
execução, a resposta é voltar — em vez de virar madrugada de plantão.

---

## 8. Decisões tomadas de propósito

Registradas aqui para ninguém as redescobrir como se fossem esquecimento.

**Ofuscação de pacote fica para o próximo patch** (decisão do dono,
2026-08-14). O `PACKET_OBFUSCATION` está ligado (`src/config/packets.hpp:48`),
mas as três chaves seguem comentadas — ou seja, rodando com as chaves padrão do
rAthena, que são públicas. Isso não atrapalha o jogo e não atrapalha quem quiser
escrever bot. Trocar exige que cliente e servidor usem as mesmas chaves, ou
seja, mexer no exe do cliente: é trabalho de verdade, e entra junto com o
instalador do patch.

**O banco de produção nasce vazio** (2026-08-14). Nada de HML é levado — nem
contas, nem GM, nem placar. Os personagens daqui são grupo 99, que ignora as
sete travas de item, e o inventário deles tem coisa que não deveria circular.

**O MD5 é sem salt, e é o que o emulador oferece.** Fraco pelos padrões de hoje,
incomparavelmente melhor que texto puro. Melhorar é trabalho posterior e mexe em
`src/`.

**A Batalha Campal e os números de guerra não são revistos aqui.** Este plano é
de implantação; calibragem de jogo continua no `PENDENCIAS.md`.

---

## 9. Achados do Mac que precisam do Windows

Lista alimentada durante a execução, pelo sinal da §1. Cada linha vira trabalho
de uma sessão no Windows.

*(vazia — nada encontrado ainda)*
