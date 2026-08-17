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

### Etapa 2 — apontar o cliente para o servidor ✅ (2026-08-14)

**Feito, e confirmado pelo dono com login de verdade na produção**: conta criada
pelo site, cliente desta máquina, login → char → map, os três em
`138.197.155.31`. O relato completo está no `HISTORICO.md`, "O cliente aponta
para a produção — e o arquivo era o outro". (A sessão do Mac datou o mesmo
trabalho de 2026-08-15; é a mesma virada de noite, não duas datas.)

**A correção que esta etapa deixa para o plano:** o arquivo não era o
`data\clientinfo.xml`, como estava escrito aqui e no `SESSAO-WINDOWS.md`. Este
exe é `<servertype>sakray</servertype>` e quem vale é o **`data\sclientinfo.xml`**
— trocar só o primeiro não muda nada, e o sintoma é o cliente insistindo em
`127.0.0.1`. Os dois ficaram com o mesmo endereço; a regra subiu para o
`CLAUDE.md` §5.

O `SESSAO-WINDOWS.md` foi apagado, como ele próprio mandava.

Duas coisas que a etapa deixou em aberto, as duas registradas:

- o `<address>` está com o **IP**; o domínio serve (`EnableDnsSupport` está no
  perfil do NEMO) e é mais robusto, mas não se mexeu no que acabou de funcionar;
- **o quarto servidor não está fechando o circuito**: o web (8888) não é
  alcançável de fora, e os quatro `ExternalSettings_*.lub` do cliente ainda
  dizem `127.0.0.1:8888`. Login, char e map estão provados; este não.
  `PENDENCIAS.md` §5c tem o placar e a ordem — e o primeiro passo é de infra,
  no Linux.

Lembrar que o cliente inteiro está **fora do git**: essa alteração só existe
nesta máquina, some em cliente novo, e por isso o instalador tem de levar os
**dois** XML já apontados.

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

### Etapa 5 — dependências e a primeira compilação ✅ (2026-08-15)

**O marco de risco caiu, e a §2 estava certa: o código custom passa pelo GCC.**

Compilado em **67 minutos** (`make server -j1`, 1 vCPU) pelo
`ferramentas/atualiza_servidor.sh`. Os quatro binários existem, são ELF x86-64,
e os 17 pontos de enxerto de `src/custom/` sobreviveram ao clone — o
`battle.cpp` chama `reducao_pvp` nas quatro posições previstas.

**Ressalva sobre os "zero avisos":** o rAthena **não liga `-Wall`** — a linha de
compilação traz só `-Wformat` e `-Wformat-security`, que vêm do Ubuntu. Zero
avisos aqui não atesta a saúde do nosso C++; atesta que compila. Para valer como
revisão, seria preciso recompilar `battle.cpp`, `status.cpp` e `clif.cpp` com
`-Wall -Wextra` e olhar só o que mencione `src/custom/`.

**O que quase matou o build foi memória, não código.** O `skill.cpp` sozinho
levou a RAM a 947 MB **e** o swap a 1,8 GB; foi preciso acrescentar swap duas
vezes durante a compilação, chegando a 7 GB. O `provisiona.sh` já nasce com 4 GB
por isso. **Compilar nesta máquina não é rotina de deploy sustentável** — se
cada mudança em `src/` custar uma hora de *thrashing*, a saída é compilar fora
(Mac num container Ubuntu) e enviar só os binários.

Dependências instaladas: `build-essential` (GCC 13.3), `zlib1g-dev`,
`libmariadb-dev`, **`libmariadb-dev-compat`**, `libpcre3-dev`, `git`, `make`,
`pkg-config`, `mariadb-server`, `nginx`, `ufw`. As duas armadilhas do caminho
(bit de execução do `configure` e o `-compat` que falta) estão no `CLAUDE.md` §5. É aqui que se descobre se o código custom passa
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

### Etapa 6 — banco ✅ (2026-08-15)

**Os quatro `.sql` rodaram** (`main.sql`, `logs.sql`, `web.sql` e o nosso
`guerra_arena_pvp.sql`): 72 tabelas, todas em `latin1_swedish_ci`, conferidas
uma a uma. Mais a `guerra_site_cadastro`, do site (`site/sql/site.sql`).

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

### Etapa 7 — `conf/import/` na máquina alvo ✅ (2026-08-15)

**Automatizada em `ferramentas/configura_servidor.sh`** (que faz também a
Etapa 9), rodado do Mac com `ssh libraro 'bash -s' < …`. Escreve
`inter_conf.txt` (credenciais do banco, que servem aos quatro — o web-server
carrega `conf/inter_athena.conf` na subida, `src/web/web.cpp:463`),
`login_conf.txt`, `char_conf.txt` e `map_conf.txt`.

**O medo desta etapa não se confirmou:** `conf/import/` está no `.gitignore` do
próprio rAthena (`/conf/import`), então o `git reset --hard` do
`atualiza_servidor.sh` **não a alcança**. Conferido, não suposto.

**A conta de comunicação `s1`/`p1` foi trocada aqui** — fechando o item 1 da §5
do `PENDENCIAS.md`. Duas coisas que ela exige e que custaram uma rodada:

1. **A senha vai hasheada para o banco.** Com `use_MD5_passwords: yes` a conta
   de sexo `S` passa pelo mesmo hash das dos jogadores. Sem converter, o
   char-server não conecta.
2. **A senha tem teto de 23 caracteres** — `char_logif.cpp:826` copia 24 bytes
   e trunca o resto, calado. Ver `CLAUDE.md` §5.

**`new_account: no` foi fixado explicitamente**, e não herdado do padrão: com
`yes`, digitar `nome_M` na tela de login cria conta na hora — e o limite de uma
conta por pessoa do site viraria decoração, porque bastaria criar pelo cliente.

### Etapa 7 — o registro original

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

### Etapa 8 — Apache (era nginx) ✅ (2026-08-15)

**Trocado para Apache por decisão do dono**, em 2026-08-15. Custou uma
desinstalação: o `provisiona.sh` instalava nginx, mas nada nosso chegara a ser
configurado nele — servia a página padrão do Ubuntu. Automatizado em
`ferramentas/configura_web.sh`.

O que ficou de pé:

- **`https://libraro.filiponegrao.com.br`** com certificado Let's Encrypt e
  redirecionamento de HTTP, renovação automática pelo certbot
- **proxy do web-server** (8888, fechada no `ufw`) para os cinco caminhos que
  ele atende. **`/MerchantStore/` tem maiúscula e o `ProxyPass` diferencia
  caixa** — escrever minúsculo ali faz a loja de mercador falhar sem erro
- **`/patch/`** servindo `/var/www/patch`, que é o gancho do instalador
- **o site** (`guerra-site.service`), compilado no próprio servidor: Go leva
  segundos, ao contrário dos 67 minutos do C++

**Uma linha que não é óbvia e cuja falta é calada:**
`RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}`. O `mod_proxy_http`
manda `X-Forwarded-For` e `-Host` sozinho, mas **não o `-Proto`** — sem ela o
site nunca sabe que a conexão veio por HTTPS e o cookie de sessão deixa de sair
como `Secure`. Tudo continua funcionando; só o cookie passa a poder viajar em
claro. Conferido no cabeçalho: `HttpOnly; Secure; SameSite=Lax`.

**Os segredos do site moram em `/etc/guerra/site.env`**, fora do repositório de
propósito — assim nenhum comando de git alcança o arquivo.

#### A medição que muda a recomendação de tamanho

Depois do `apt` e da compilação do Go, o `map-server` apareceu com **28 MB de
RSS** — ele tem 437. Os ~400 MB de diferença **foram para o swap**: uma operação
de manutenção rotineira expulsou o servidor de jogo da memória.

Não é fatal — as páginas voltam —, mas o custo aparece como engasgo de latência
justo enquanto alguém joga. **Isto deixou de ser estimativa: 1 GB é apertado
demais para conviver com manutenção.** A recomendação de subir para 2 GB agora
tem evidência.

### Etapa 8 — o registro original

Duas funções:

1. **proxy do web-server** (`8888`), com limite de tamanho de corpo e rate
   limit. Sem ele o emblema de clã não sobe — e a falha é *calada*
   (`CLAUDE.md` §3).
2. **servir os arquivos de patch** por HTTP estático, que é o gancho para o
   instalador do patch (trabalho separado, fora deste plano).

### Etapa 9 — systemd ✅ (2026-08-15)

**As quatro units instaladas e habilitadas no boot**, por
`ferramentas/configura_servidor.sh`: `guerra-login`, `guerra-char`,
`guerra-web`, `guerra-map`, com `After=` na ordem **login → char → web → map**.
Cada uma roda como `ragnarok`, com `NoNewPrivileges`, `PrivateTmp`,
`ProtectSystem=full` e `ProtectHome`.

**Subiram, e a cadeia inteira fechou:** *Authentication accepted* no
login-server, char-server aceito, e **Map-Server conectado com 1258 mapas**.
Zero `Unknown syntax` no log — os 19.622 scripts dos nossos NPCs carregaram no
Linux sem um erro.

**A medição de memória com os quatro no ar** (2026-08-15), que a Etapa 3 pediu:

| | RSS |
|---|---|
| `map-server` | **437 MB** |
| `char-server` / `web-server` / `login-server` | 11 / 10 / 9 MB |
| **Total da máquina, com MariaDB e sistema** | **727 MB de 961 — 233 disponíveis** |

A estimativa de 250–400 MB para o map-server ficou curta. Funciona, e ainda cabe
o site (~20 MB) e o nginx (~10 MB), mas a folga real é de ~200 MB. Subir para
2 GB é decisão com número, não mais com estimativa.

### Etapa 9 — o registro original

Quatro units, uma por servidor, com `After=` expressando a ordem que o
`ferramentas/servidor.py` já conhece: **login → char → web → map**. O `web`
sobe junto de propósito, para não ser esquecido de novo — foi o que motivou
aquele script em 2026-08-04.

Vale que as units façam o que o `servidor.py status` faz: dizer **o que quebra**
quando cada peça está fora.

### Etapa 10 — backup ✅ (2026-08-15)

`ferramentas/backup.sh` + `ferramentas/configura_backup.sh`. **Dois pacotes
separados por natureza, não por tamanho:**

- **jogo** — conta, personagem, inventário, armazém, clã, variáveis dos nossos
  NPCs, placar da Honra de Combate. Pequeno.
- **logs** — as dez tabelas de `logs.sql`. Não são estado: se sumirem, ninguém
  perde item. Mas crescem muito mais rápido (a `picklog` grava uma linha por
  item que troca de mão, e o servidor é drop 50x).

Separar é o que deixa a rotina do jogo pequena a ponto de ser **horária**.
Ritmos: **48 horárias** (perda máxima de uma hora), **30 diárias**, **12
semanais**. São megabytes — ser generoso cobre o caso que motivou o desenho:
perceber o problema só no segundo dia, quando o backup de ontem já está ruim.

**`--lock-tables`, e não `--single-transaction`:** quase tudo do rAthena é
MyISAM, que não tem transação — o `--single-transaction` daria dump
inconsistente **sem reclamar de nada**.

**A restauração foi testada** (2026-08-15), que é o que separa backup de
esperança: um `0x4D6167E3` plantado no banco atravessou dump → gzip → restauro
**byte por byte**, ainda em `latin1`, e as 62 tabelas do pacote do jogo voltaram
(72 do banco menos as 10 de log).

**O alerta que mais importa é o de ausência, e ele não pode morar aqui.** Se o
droplet parar, nada dispara, e o silêncio é idêntico a "está tudo bem". Por isso
cada execução bem-sucedida manda um **pulso**; quem alerta é o serviço do outro
lado, ao deixar de receber. Falta preencher `ALERTA_URL` e `PULSO_URL` em
`/etc/guerra/backup.env`.

**A cópia externa é PUXADA, não empurrada** — e é decisão de segurança. Servidor
com credencial de escrita no destino do backup é servidor que, invadido, apaga
os próprios backups. A tarefa é do Windows, com `scp`.

### Etapa 10 — o registro original

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

### Etapa 11 — a varredura de pré-voo ✅ (2026-08-15)

`ferramentas/prevoo.sh`, rodando no Mac e no servidor, e chamada pelo deploy
**antes de reiniciar** — abortando se reprovar. Rodar depois seria inútil: o
estrago já estaria no ar.

Primeira execução: **1136 caminhos** conferidos, todos com a caixa exata.

**Ela reprovou 11 falsos positivos de saída** — os `db/import/*.yml`, que nascem
ausentes de propósito (são as pastas de sobrescrita do próprio rAthena, no
`.gitignore` dele). Passaram a ser ignorados, e o motivo está no código:
varredura que grita à toa é varredura que ninguém lê.

### Etapa 11 — o registro original

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

### Etapa 12 — `ferramentas/implanta.sh` ✅ (2026-08-15)

> **A "otimização" virou requisito no mesmo dia.** O texto original desta etapa
> dizia que distinguir "mudou só `db/`" de "mudou `src/`" era *"otimização, não
> requisito da primeira versão"*. Errado: em 2026-08-15 um deploy de **CSS**
> reiniciou os quatro servidores e derrubou o dono do jogo, com *"Erro
> desconhecido"* na tela. O aviso estava escrito nesta mesma seção, duas linhas
> abaixo, e não foi seguido.
>
> Agora o jogo só reinicia se algo dentro de `rathena/` mudou ou se o binário
> foi recompilado.

#### Quanto tempo o jogador fica fora — 28 segundos, medidos

O deploy inteiro roda com o jogo **no ar**: o `git pull` e a compilação (até 67
min) acontecem enquanto os quatro servidores seguem servindo o binário antigo. A
única janela de queda é o restart do fim, e ela foi medida em **28 segundos**
(2026-08-16), do `systemctl restart` até o `Map-Server 0 connected: 1258 maps` —
que é o marco certo, porque "o processo subiu" não quer dizer "dá para jogar".

**E o build não pode mais falhar no último minuto.** O kernel **recusa
sobrescrever executável em uso** (`Text file busy`, medido nesta máquina), então
um `make` que chegasse à linkagem com o map-server no ar poderia morrer *depois*
de uma hora de trabalho. Os binários passam a ser renomeados para `*.anterior`
antes do build: o processo em execução guarda o **inode**, não o nome, e segue
rodando sem sentir nada.

Isso deu de graça a **volta atrás**: build que falha devolve os binários antigos
sozinho, e build que passa deixa os anteriores em disco para reverter à mão. Site, documentação e ferramenta não encostam nele. O que
> continua sendo melhoria de verdade é trocar o restart por `@reloadscript`
> quando só `npc/` ou `db/` mudarem — e isso exige mandar comando ao console do
> map-server, que sob `systemd` não tem terminal.

```
ferramentas/implanta.sh
```

Roda no Mac, e é o wrapper fino que a §3 prometia. **Manda o
`atualiza_servidor.sh` pelo stdin do `ssh`** — assim o que roda é sempre a
versão deste diretório, e nenhuma cópia velha sobrevive no servidor para
atrapalhar. Resolve o ovo e a galinha sem truque.

Cumpre os cinco requisitos: idempotente, não recompila se `src/` não mudou
(o build custa ~67 min), nunca toca `conf/import/`, roda o pré-voo antes de
reiniciar, e diz o que fez. Avisa também do que está **sem commit ou sem push**
— deploy do que não está no git é a origem clássica do "funciona aqui e não lá".

**O buraco que ele fecha apareceu na prática em 2026-08-15:** o
`configura_web.sh` recompilou código velho porque não fazia `git pull`, e o
`/api/config` nasceu 404. Agora há um caminho só.

### Etapa 12 — o registro original

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

## 8b. O estado da produção em 2026-08-15

Varrido de fora nesta data. Serve de linha de base: se algum destes mudar sem
alguém ter mexido, é defeito.

| | |
|---|---|
| Site | `https://libraro.filiponegrao.com.br` — HTTP redireciona |
| Botão Baixar | ~~pasta do Google Drive~~ → **o instalador**, `https://cdn.filiponegrao.com.br/Jogar.exe` — **no ar desde 2026-08-16** (`SITE_DOWNLOAD_URL` em `/etc/guerra/site.env`) |
| Portas do jogo | 6900, 6121, 5121 abertas |
| 8888 | **fechada**, e o web-server responde pelo Apache na 80 e na 443 |
| Serviços | os quatro do jogo + site + Apache + MariaDB, todos `active` |
| Backup | três temporizadores armados; horário já rodando sozinho |
| Memória | 763 MB de 961 usados, 198 disponíveis |

**O `SITE_DOWNLOAD_URL` mora fora do git** (`/etc/guerra/site.env`) e sobrevive a
reexecuções do `configura_web.sh`, que preserva o arquivo. Mas **máquina nova
nasce sem ele** — e aí o botão aparece desligado dizendo "Em breve", que é o
comportamento certo, e não um botão quebrado.

## 9. Achados do Mac que precisam do Windows

Lista alimentada durante a execução, pelo sinal da §1. Cada linha vira trabalho
de uma sessão no Windows.

**1. ~~Apontar o cliente para o servidor (Etapa 2).~~ RESOLVIDO em 2026-08-14**,
com login de verdade. O que o Windows descobriu e o Mac precisa saber: o arquivo
é o **`sclientinfo.xml`**, não o `clientinfo.xml`. No lugar dele entra um item
novo, que volta para o Mac: **os quatro servidores têm de estar no ar E
alcançáveis de fora** — hoje login, char e map estão (provado pela captura do
primeiro login), e o **web (8888) não**. Sem ele o emblema de clã não sobe, e a
falha é calada. O inventário completo dos apontamentos do cliente, com a ordem
de execução e o que precisa voltar do Mac para cá, está no `PENDENCIAS.md` §5c.

**2. A conta interserver do HML continua `s1`/`p1`.** No Linux ela foi trocada
por credencial própria em 2026-08-15 (`PENDENCIAS.md` §5, item 1). No HML é
opcional — ambiente de teste, atrás de NAT — mas fica registrado para não
parecer esquecimento.

**3. A roupa de GM não aparece na conta de produção** (2026-08-15). A conta
`librasupremo` foi criada no Linux com `group_id 99` (grupo `Admin`) e **os
comandos funcionam** — quem os autoriza é o servidor, e isso está certo. O que
não aparece é a **aparência** de GM, e ela é do **cliente**: vem da lista
`<aid><admin>…</admin></aid>` dentro do `clientinfo.xml`, que enumera
`account_id`. No HML funciona porque a conta de teste de lá está nessa lista.

**O `account_id` da conta nova é `2000004`.** Falta acrescentá-lo — e
provavelmente nos **dois** XML, com o cuidado de sempre (cp1252, por script,
âncora com `assert`), lembrando que o que venceu no apontamento do servidor foi
o `sclientinfo.xml` e não o `clientinfo.xml`.

É mais um caso da §4.9 do `CLAUDE.md`: as duas metades — quem autoriza e quem
desenha — são independentes, e a divergência não dá erro.

**4. O instalador do cliente.** Levantamento em `PENDENCIAS.md` §5b. O servidor
já tem onde hospedar: `https://libraro.filiponegrao.com.br/patch/`, servindo
`/var/www/patch`. **O gancho passou a ser usado em 2026-08-15**: o Atualizador
(`patcher/`) já publica e aplica patch incremental por ali — falta só o primeiro
download. ~~*Uma dívida que volta para o Mac:* publicar patch exige SSH ao
servidor **a partir do Windows**, que é onde os zips nascem, e esta máquina não
tem chave autorizada (o deploy sempre foi do Mac).~~ **A chave do Windows foi
autorizada na conta `ragnarok` em 2026-08-16**, e o caminho `scp` → Apache →
HTTPS foi provado ponta a ponta, do Windows, com o patch 0001 (§10.3).
~~Antes de empacotar, **anotar a lista de patches do NEMO**~~
— **feito em 2026-08-14**: o `.epi` ao lado do exe traz os nomes, e a lista está
no `REFERENCIA.md`. O exe continua sendo o único arquivo do conjunto sem gerador
versionado, então a cópia fria dele continua obrigatória.

---

## 9b. Preparado no Windows, à espera do Mac

O inverso da §9: trabalho que já está pronto e commitado, e que só falta um
comando do lado da infra. **Ao concluir uma linha aqui, apague-a** e registre no
`HISTORICO.md`, como manda o `CLAUDE.md` §7.

*Nenhuma linha aberta hoje* — a última (ligar o botão Baixar ao instalador)
foi aplicada em 2026-08-16 e está no `HISTORICO.md`.

---

## 10. O servidor de patches — a especificação do lado de lá

Escrita em 2026-08-15, quando o Atualizador ficou pronto do lado do cliente
(`patcher/LEIAME.md`). **Esta seção é autocontida de propósito:** dá para
executá-la numa sessão do Mac sem ler o resto do plano, e sem o cliente.

O resumo em uma frase: **o servidor não roda nada — ele serve três arquivos
estáticos.** Não há processo, não há banco, não há repositório sendo lido. O
`ferramentas/publica_patch.sh` deposita arquivos em `/var/www/patch/` por `scp`,
e o Apache os entrega. Toda a inteligência está no cliente.

### 10.1 O contrato HTTP — três recursos, e nada mais

Base: `https://libraro.filiponegrao.com.br/patch/`

| recurso | o quê | ausência (404) |
|---|---|---|
| `lista.txt` | o índice dos patches | o Atualizador avisa e **libera o botão Jogar** |
| `<numero>-<apelido>.zip` | um patch | falha aquele patch; os anteriores continuam válidos |
| `patcher.txt` | canal de auto-atualização do próprio Atualizador | **normal** — é o estado enquanto não há versão nova |

**`lista.txt`** — UTF-8, uma linha por patch, **cinco campos separados por
TAB**, `#` comenta, linha vazia é ignorada:

```
0001<TAB>0001-ia-do-homunculo.zip<TAB><sha256><TAB>42236<TAB>IA do homunculo
```

Ele **não é escrito no servidor**: é o `patcher/patches.txt` do repositório,
enviado sem tradução nenhuma. Editar a cópia do servidor à mão funciona até a
próxima publicação, que sobrescreve — e aí a divergência aparece como patch que
"voltou".

Linha malformada é **erro fatal** para o Atualizador, e isso é de propósito:
pular linha ruim deixaria o cliente do jogador num estado que ninguém consegue
reproduzir aqui.

**`patcher.txt`** — chave=valor, `#` comenta:

```
versao=2
arquivo=Atualizador-2.exe
sha256=<64 hex>
```

**Códigos esperados: 200 e 404.** Qualquer outra coisa — 403, 500, redirect
para página de erro em HTML — vira mensagem de falha na tela do jogador. O
Atualizador segue redirect (até 10), o que é o que permite migrar de host sem
quebrar quem tem o `.ini` antigo (§10.6).

**Sem autenticação e sem cookie.** Patch não é segredo: quem tiver o link baixa.
A garantia de integridade é o sha256 do registro, servido por HTTPS.

### 10.2 O que já está pronto — não refazer

Tudo isto saiu do `ferramentas/configura_web.sh` na Etapa 8, e está no ar:

- `/var/www/patch`, dono `ragnarok`, modo 755
- no vhost de 443: `Alias /patch /var/www/patch`, com
  `Options -Indexes +FollowSymLinks` e `Require all granted`
- **`ProxyPass /patch !`** — a linha que impede o `ProxyPass /` do site de
  engolir o caminho. É a mais fácil de perder ao mexer no vhost, e a falha dela
  é traiçoeira: o Atualizador receberia **200 com o HTML do site** no lugar da
  lista, e o erro que apareceria na tela seria "lista.txt linha 12: 1 campos"
- HTTPS com Let's Encrypt e renovação automática

### 10.3 O que falta — o checklist da sessão paralela

**1. ~~Autorizar a chave do Windows~~ ✅ FEITO em 2026-08-16** — na conta
`ragnarok`, e provado do Windows: conecta, `/var/www/patch` é gravável, e o
patch 0001 foi publicado e baixado por HTTPS numa pasta limpa. O texto abaixo
fica como o registro do porquê.

**Autorizar a chave do Windows — na conta `ragnarok`, não na do root.** Era o
que travava a publicação. Os zips nascem em `C:\GuerraDoEmperium\cliente`,
que só existe no Windows, então quem publica é o Windows — e essa máquina nunca
teve chave no servidor (o deploy sempre foi do Mac). A chave foi gerada lá em
2026-08-15.

**Por que `ragnarok`** (decisão do dono, 2026-08-16): esta chave só precisa
copiar arquivo para `/var/www/patch`, e a pasta já pertence a ele — o
`configura_web.sh` a cria com `install -o ragnarok`. Uma chave de root faria
muito mais do que o trabalho pede, e ficaria numa máquina de desktop. Ele tem
`/bin/bash` (`provisiona.sh:250`, shell que o deploy exige para o `git pull`),
então `scp` funciona; conta com `nologin` não serviria.

Rodado do Mac, que entra como root:

```bash
ssh libraro '
  install -d -m 700 -o ragnarok -g ragnarok /home/ragnarok/.ssh
  echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAtTGgt4TsS2WSkrn3avQ4/ID63TsIBTtDWCREZiUK74 guerra-windows-patch" \
    >> /home/ragnarok/.ssh/authorized_keys
  chown ragnarok:ragnarok /home/ragnarok/.ssh/authorized_keys
  chmod 600 /home/ragnarok/.ssh/authorized_keys
'
```

Os dois últimos comandos não são zelo: **o `sshd` recusa `authorized_keys` que
não pertença ao dono da conta ou que esteja com permissão frouxa**, e recusa
*calado* — do lado do cliente sai o mesmo `Permission denied (publickey)` de
quando a chave não existe. Se a autorização "não pegar", é o primeiro lugar a
olhar (`/var/log/auth.log` diz o motivo real).

Conferir depois com `ssh -o BatchMode=yes libraro true` **do Windows** — do Mac
não prova nada, porque lá a chave é outra.

Apertar mais, se um dia fizer sentido: `restrict,command="…"` na frente da
chave no `authorized_keys` limita o que ela pode fazer a um comando só. Não é
necessário agora — a conta já não é privilegiada.

*Alternativa, se preferir não dar acesso ao Windows:* o publicador aceita
`SERVIDOR=` e `DESTINO=` por variável de ambiente, então os zips podem ir para o
Mac por outro caminho e serem publicados de lá. Custa um passo manual em toda
publicação; a chave custa uma linha, uma vez.

**2. Cabeçalhos de cache.** Não é urgente — hoje não há CDN e o cliente Go não
cacheia. Vira urgente no dia em que entrar um proxy na frente, e aí o sintoma é
"publiquei e ninguém recebeu". A regra é oposta para os dois tipos de arquivo,
porque um muda e o outro nunca:

```apache
<Directory /var/www/patch>
    <FilesMatch "\.(txt)$">
        Header set Cache-Control "no-cache, must-revalidate"
    </FilesMatch>
    <FilesMatch "\.(zip|exe)$">
        Header set Cache-Control "public, max-age=31536000, immutable"
    </FilesMatch>
</Directory>
```

O `immutable` é honesto aqui: zip publicado **nunca** muda de conteúdo — o
número não se reaproveita, e correção é patch novo.

**3. Disco e retenção.** Os zips só acumulam: **zip publicado não se apaga**,
porque quem instalou o cliente há seis meses ainda vai baixar o patch 0001. O
que decide quando o acúmulo incomoda é refazer o pacote de instalação (que já
nasce com tudo aplicado) e só então avaliar. Enquanto o total estiver na casa
das centenas de MB, não há o que fazer — mas convém saber o número: incluir
`du -sh /var/www/patch` na sonda da Etapa 13.

### 10.4 Como testar sem o cliente

Prova o contrato inteiro por fora, e roda de qualquer máquina:

```bash
BASE=https://libraro.filiponegrao.com.br/patch

# 1. a lista existe, é 200 e é texto (e NÃO o HTML do site)
curl -sI $BASE/lista.txt | head -3
curl -s  $BASE/lista.txt | head -20

# 2. os campos estão separados por TAB, e não por espaço
curl -s $BASE/lista.txt | grep -v '^#' | grep -P '\t.*\t.*\t.*\t' | wc -l

# 3. cada zip existe e confere com o sha da lista
curl -s $BASE/lista.txt | grep -v '^#' | while IFS=$'\t' read -r n a s b d; do
    curl -s "$BASE/$a" | sha256sum | grep -q "$s" && echo "$n ok" || echo "$n FALHOU"
done

# 4. o canal do Atualizador: 404 é resposta certa enquanto não há versão nova
curl -sI $BASE/patcher.txt | head -1
```

### 10.5 O que quebra calado

- **`ProxyPass /patch !` removido** — 200 com HTML do site (§10.2).
- **`lista.txt` com espaços no lugar de TAB** — o editor que "arruma" o arquivo
  no servidor quebra todo mundo de uma vez. Não editar lá; publicar de novo.
- **zip apagado do servidor mas mantido na lista** — só falha para quem ainda
  não o aplicou, ou seja, para o jogador novo. Ninguém percebe do lado de cá.
- **`Options +Indexes`** — expõe a lista de arquivos. Não quebra o patch, mas
  não há motivo para ligar.
- **certificado vencido** — o Go recusa e o jogador vê "não consegui conferir as
  atualizações". A renovação é automática, mas é o primeiro lugar a olhar se um
  dia todos falharem no mesmo dia.

### 10.6 Migrar para outro host, um dia

A URL base mora no `Jogar.ini` do jogador, então trocá-la só vale para
quem instalar depois. Para os que já têm, o caminho é manter o `/patch`
respondendo com **301** para o novo endereço — o Atualizador segue redirect.

Isso importa se o pacote de instalação (4 GB) sair do Drive para object storage:
os patches podem ir junto sem que ninguém precise reinstalar nada.
