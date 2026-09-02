# Armadilhas: Infra, deploy, rede e publicação

SSH, Ubuntu, MariaDB, DigitalOcean, DNS, cache HTTP, deploy, Atualizador e patches.

**Este arquivo é um dos seis cadernos de armadilhas do projeto.** O índice de
todos eles — uma linha de gatilho por armadilha, com o caderno onde o caso
está contado por inteiro — está na §5 do `CLAUDE.md`. **Leia aqui a entrada
que o gatilho apontar**; ler o caderno inteiro não é para ser preciso.

As entradas abaixo produziram diagnóstico falso e custaram retrabalho. Cada
uma traz o sintoma, a causa medida (com arquivo e linha, quando existe) e a
saída — e a medição é o que separa esta lista de um palpite. **Armadilha
nova se escreve nas duas pontas:** o caso aqui, o gatilho na §5.

---

- **`tr -dc … | head -c N` mata o script inteiro sob `set -o pipefail`.** O
  `head` fecha o cano ao completar os N bytes, o `tr` morre de **SIGPIPE**
  (exit 141), o `pipefail` propaga e o `set -e` encerra tudo — **sem imprimir
  uma linha**, porque SIGPIPE é silencioso. Parece que o script "terminou" no
  meio. Para gerar senha, `openssl rand -hex 16`, que não usa cano. Custou duas
  rodadas em 2026-08-14 no `provisiona.sh`.

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
  **E o mesmo vale para ferramenta NOSSA escrita no Windows, onde o remédio é
  o oposto.** Em 2026-08-17 o `ferramentas/publica_patch.sh` recusou rodar no
  Mac (*"permission denied"*) porque estava no git como `100644` — o
  `publica_cliente.sh` também, e os dois são justamente os que nasceram do lado
  Windows. Os oito `.sh` restantes de `ferramentas/` estão `100755`, então a
  divergência não salta aos olhos: só se descobre ao rodar o script pela
  primeira vez de outra máquina. Como o arquivo é **nosso**, aqui a saída não é
  chamar `bash <script>` para sempre: é consertar o modo no índice,
  `git update-index --chmod=+x <arquivo>`, e commitar. Fica valendo para as
  três máquinas. Conferência: `git ls-files -s ferramentas/*.sh`.

  **Reincidiu em 2026-09-02, e o modo novo é o que interessa: o script que
  falhou não é rodado por gente.** Os três arquivos do bot fantasma
  (`configura_fantasma.sh`, `implanta_fantasma.sh` e
  `ferramentas/openkore/instala.sh`) entraram no git como `100644`. Os dois
  primeiros não deram sinal — um é chamado como `bash <arquivo>` e o outro
  viaja pelo *stdin* do `ssh`, e nenhuma dessas formas consulta o bit. Quem
  quebrou foi o terceiro, o único invocado pelo caminho puro, de dentro de
  outro script: `runuser: failed to execute
  /opt/guerra-do-emperium/ferramentas/openkore/instala.sh: Permission denied`.

  Duas coisas pioram esse caso em relação ao de 2026-08-17. A primeira é
  **quando** ele aparece: no passo 4 de 6, depois de instalar as dependências
  de build, clonar 233 MB de openkore e compilar o `XSTools.so` — todo o
  trabalho caro é feito antes de a falha existir. A segunda é que a
  conferência prescrita acima (*"só se descobre ao rodar o script pela
  primeira vez de outra máquina"*) **não alcança este arquivo**: ninguém o
  roda à mão em máquina nenhuma, então não há primeira vez.

  Por isso a saída agora é **dupla**, e não só o `--chmod=+x`: os dois
  chamadores (`configura_fantasma.sh` §4 e `atualiza_servidor.sh` §6b) passaram
  a invocá-lo como `como_jogo bash <caminho>`. Com o interpretador explícito o
  bit deixa de ser ponto único de falha, do mesmo jeito que o `sh configure`
  resolve o lado do vendor. O `git update-index --chmod=+x` continua sendo
  feito — é ele que conserta o arquivo para quem o chamar direto —, mas deixou
  de ser a única coisa entre o deploy e o `Permission denied`.

  **A regra que sai daqui: script novo NOSSO nasce sem o bit** (a ferramenta de
  edição do assistente grava `100644`), e a hora de conferir é ao criá-lo, não
  ao rodá-lo. `git ls-files -s ferramentas/**/*.sh` mostra os dois modos lado a
  lado, e o que destoa da coluna `100755` é o novo.

- **`git` rodado como root numa árvore de outro dono sai 128 sem ler nada — e
  um `2>/dev/null || echo desconhecido` transforma isso num aviso brando que
  DESARMA a trava.** O `/opt/guerra-do-emperium` pertence ao `ragnarok`; o
  `ssh libraro` entra como root. Qualquer `git -C /opt/guerra-do-emperium
  rev-parse HEAD` daí responde *"fatal: detected dubious ownership in
  repository"* e **não** imprime commit nenhum — é a proteção que o git ganhou
  em 2.35.2, e não tem nada a ver com permissão de arquivo. Por isso todo
  comando de git do `atualiza_servidor.sh` passa por `runuser -u ragnarok`.

  O estrago mora no tratamento do erro, e não no erro. O
  `implanta_fantasma.sh` compara o commit dos dois lados para não instalar um
  delta atrasado; ao não conseguir ler o remoto ele avisava *"nao consegui ler
  o commit do servidor - seguindo assim mesmo"* e seguia. Em 2026-09-02 isso
  aconteceu com o servidor **três commits atrás**, e os três eram do fantasma:
  a instalação ia aplicar um `control/config.txt` velho, que é exatamente o que
  aquela comparação existe para impedir. A trava não falhou — ela nunca chegou
  a ser consultada, e disse isso numa linha amarela no meio de duzentas linhas
  de `apt` e `g++`.

  Duas lições, e a segunda vale para qualquer sonda: ler repositório do
  servidor é `runuser -u ragnarok -- git …`, nunca git direto; e **degradar
  para "seguindo assim mesmo" só é honesto quando o que se perdeu é
  dispensável** — se a leitura era o que arma uma trava, o certo é o `2>&1`
  aparecer e o script parar.

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

- **`StretchDIBits` falha de vez em quando, e mente no `GetLastError`.** Duas
  execuções do mesmo binário devolveram 630 linhas (sucesso) e a terceira
  devolveu **0** — com o erro do sistema dizendo *"operação concluída com
  êxito"*. O sintoma é a janela do Atualizador nascer com o retângulo da arte
  preto, sem nada além do log dizer o que houve.
  **A primeira suspeita foi o modo `HALFTONE`, e estava errada:** tirar o
  HALFTONE e tirar a escala (cópia 1:1) não consertou — voltou a falhar na
  primeira execução seguinte. É a função, não o modo. Vale como lembrete de que
  "mexi e parou de acontecer" não é diagnóstico quando o defeito é
  intermitente: a versão sem HALFTONE rodou três vezes seguidas antes de
  falhar.
  **A saída é não usar aquele caminho:** `CreateDIBSection` devolve um ponteiro
  para os bits do bitmap, e os pixels são **copiados** para lá — sem conversão,
  sem escala, sem chamada que possa falhar por motivo obscuro. A redução de
  tamanho, quando precisa, se faz em código antes. Ver `patcher/janela.go`,
  `preparaArte` e `reduz`.

- **O servidor de jogo NÃO tem relógio próprio: `gettime` e `OnClock` leem a
  hora LOCAL da máquina — e a máquina de produção nasce em UTC.** A imagem
  Ubuntu da DigitalOcean vem em `Etc/UTC`, três horas à frente do Brasil, e
  nada no rAthena converte nada: o `gettime(DT_HOUR)` de script e os rótulos
  `OnClock<hhmm>` saem do `localtime` do processo. Consequência medida em
  2026-08-16: a Guerra do Emperium de quinta às 20h
  (`npc/guerra/horario_da_guerra.txt`, horário de Brasília) abriria às **17h**
  do Brasil — e a falha é completamente calada, porque o script roda, o anúncio
  sai e o Emperium nasce, só que na hora errada. O `ferramentas/provisiona.sh`
  passou a fazer `timedatectl set-timezone America/Sao_Paulo` como passo 0
  (`America/Sao_Paulo` e não `-03`: se o horário de verão voltar, quem resolve é
  o `tzdata`). **Processo já no ar mantém o fuso antigo** — reiniciar os quatro
  servidores depois. E a sonda que decide é `ssh <servidor> date`, nunca o
  relógio de quem está olhando.
  **E arrumar o `provisiona.sh` NÃO arruma a máquina que já está de pé:** o
  `implanta.sh` faz `git pull`, compila e reinicia — ele **não** roda o
  provisionamento. Um passo novo acrescentado lá só vale para a próxima
  máquina, e nada avisa que a atual ficou de fora. Medido em 2026-08-17:
  vinte e quatro horas depois de o passo 0 entrar no script, a produção ainda
  estava em `Etc/UTC` — corrigida à mão, com o `timedatectl` antes do deploy
  para o restart dele pegar o fuso novo de carona. **Passo novo de
  `provisiona.sh` é para aplicar à mão na produção no mesmo dia**, ou fica
  valendo só no papel.

- **`nslookup` sai com código 0 mesmo quando o domínio NÃO existe.** Uma sonda
  `nslookup $host && echo "resolve"` imprime *"resolve"* para NXDOMAIN, e em
  2026-08-16 isso deu por propagado um endereço de CDN que não existia — a
  conclusão errada durou até alguém tentar baixar. Quem decide é `curl`, que
  falha de verdade (`Could not resolve host`). Da mesma família: **cache DNS
  negativo local**, que faz o `curl` continuar recusando um host que já
  propagou; o `ipconfig /flushdns` limpa, e enquanto não limpar as duas sondas
  discordam sem que nenhuma esteja mentindo.

- **Chave do DigitalOcean Spaces pode ser somente-leitura, e a listagem
  funciona igual.** As chaves têm escopo (Read Only, ou acesso limitado por
  bucket), e com uma de leitura o `rclone lsf` responde normalmente enquanto
  **toda escrita volta `403 AccessDenied`**. Pior quando o script silencia o
  erro: `lsf … 2>/dev/null || true` transforma "não consigo falar com o bucket"
  em *"(vazio)"*, que é indistinguível de um bucket recém-criado — e aí a
  publicação tenta subir 3,4 GB para falhar no primeiro pedaço. O que separa os
  dois em um comando é um `PutObject` de 14 bytes. E o campo que engana no
  painel: o valor curto que a DigitalOcean mostra como nome da credencial
  (`key-1786915948100`) **não é** o Access Key — esse tem ~20 caracteres e
  começa com `DO00`.

- **O rclone chama `CreateBucket` antes de subir arquivo grande.** Para usar
  cópia multi-thread (o que ele faz sozinho a partir de algumas centenas de MB)
  ele garante que o destino existe — e uma chave com acesso ao CONTEÚDO do
  bucket mas sem permissão de criar bucket recebe `403` ali, antes de um byte
  sair. A mensagem fala em `CreateBucket` e manda procurar defeito na
  credencial, que está certa. A saída é `--s3-no-check-bucket` (ou
  `RCLONE_CONFIG_<remoto>_NO_CHECK_BUCKET=true`).

- **Deploy parcial feito à mão desarma o gatilho de restart do deploy seguinte,
  e a perda é calada — CORRIGIDO em 2026-08-22, e a armadilha continua valendo
  para quem der `git pull` no servidor por fora.** Até aquela data o
  `atualiza_servidor.sh` decidia reiniciar o jogo comparando o commit de
  **antes** do `git pull` com o de depois: quem fizesse o `git pull` por fora,
  para publicar só o site sem derrubar jogador, **consumia esse gatilho**, e o
  próximo `implanta.sh` achava `rathena/` sem mudança e não reiniciava. O que
  ficara no disco continuava no disco, o processo vivo seguia com a
  configuração velha, e nada no log denunciava — o deploy até dizia *"nada do
  jogo mudou, ninguém foi derrubado"*, que é a frase de sucesso. Aconteceu em
  2026-08-16, para não derrubar três jogadores.
  **O conserto é não perguntar "o que mudou no repositório desde o último
  pull?" e sim "o que mudou desde o que está RODANDO?".** Dois arquivos na raiz
  do servidor guardam isso e não vão para o git: `.carimbo-jogo` (o commit com
  que os quatro servidores estão no ar) e `.carimbo-site`. O
  `ferramentas/implanta_site.sh` publica só o site e **não toca** o primeiro,
  então a mudança de jogo que veio de carona no mesmo pull continua pendente
  aos olhos do deploy completo — e o próprio script a **lista** no fim, com os
  nomes dos arquivos. **O que continua sem rede é o `git pull` dado à mão no
  servidor**, que avança o repositório sem avançar carimbo nenhum; com o modo
  `--so-site` não há mais motivo para fazê-lo.

- **O registro de patch do jogador é indexado por número, e DUAS contagens
  diferentes começam em 0001.** O `patch\aplicados.txt` é o diário dos patches
  (`patcher/patches.txt`), mas o instalador numera os pedaços da BASE
  (`patcher/base.txt`) do 0001 também — e enquanto o `marcaAplicado` morou
  dentro do `aplica`, o instalador anotava os pedaços ali. Resultado medido em
  2026-08-17: todo cliente instalado tinha `0002 As musicas` e `0003 A Guerra
  do Emperium (1 de 2)` no diário, e o Atualizador **pulou os patches 0002 e
  0003 para sempre**, dizendo *"Cliente atualizado"* com a barra cheia. Os
  números 0004 e 0005 ficaram queimados para os dois patches seguintes.
  A trava é comparar **número E sha256** (`leAplicados` devolve o sha), e ela
  ainda **repara sozinha** quem já instalou. A regra geral: **número não
  identifica artefato entre duas contagens independentes** — quem decide é o
  conteúdo. E o sintoma aparece a três passos dali, na janela de loja, sem
  nada apontar para o registro.

- **`go build` sem `GOOS`/`GOARCH` explícitos num script que PUBLICA binário é
  uma bomba de fuso horário de máquina.** O `-o Jogar.exe` decide só o nome:
  rodado do Mac, o mesmo comando produz um **Mach-O chamado `Jogar.exe`**, com
  sha256 correto, que sobe para o canal de auto-atualização de todos os
  jogadores e não abre em máquina nenhuma. Nada mais no caminho olha para o
  formato do arquivo — nem o `scp`, nem o `patcher.txt`, nem o Atualizador que
  o baixa. O `publica_patch.sh` fixa `GOOS=windows GOARCH=amd64` e confere a
  assinatura `MZ` depois de compilar; achado em 2026-08-17, ao rever o caminho
  antes de publicar do Mac.

- **O deploy NÃO sai do Windows, e o pré-voo reprova aqui por um motivo que
  não existe no servidor.** Duas coisas separadas, e as duas dão a impressão de
  que algo quebrou quando nada quebrou:
  1. **A chave desta máquina é `ragnarok`, não `root`** — decisão do dono em
     2026-08-16, e está escrita no `~/.ssh/config` daqui: ela existe só para o
     `publica_patch.sh` copiar zip para `/var/www/patch`. O
     `atualiza_servidor.sh` responde *"precisa rodar como root"* e `sudo -n`
     pede senha. **Publicar patch daqui: sim. Deploy daqui: não** — o deploy
     sai do Mac, com a chave de lá.
  2. **A conferência de fim de linha do `prevoo.sh` é falso positivo no
     Windows.** Ela mede o *diretório de trabalho*, e com `* text=auto` no
     `.gitattributes` o checkout do Windows entrega CRLF de propósito — em
     2026-08-18 ela reprovou 25 arquivos e abortou o deploy antes de tocar no
     servidor. O que importa é o **índice**, que é LF, e é ele que o Linux
     recebe. A sonda que decide é `git ls-files --eol <caminho>`: a coluna
     `i/` é a que vale, a `w/` é a da máquina. Cuidado com `git show HEAD:<f>`
     nessa conferência — no Git for Windows ele aplica o filtro de checkout e
     **devolve CRLF de um blob que é LF**, confirmando o diagnóstico errado.
  É o espelho exato da armadilha do Mac (§9): lá o APFS esconde o defeito que o
  Linux pune; aqui o checkout do Windows inventa um defeito que o Linux não tem.

- **`UPDATE` na tabela `char` com o jogador CONECTADO é desfeito na saída
  dele, e o comando não erra.** O char-server carrega o personagem do banco
  quando ele entra no jogo e só escreve de volta ao sair
  (`char_mmo_char_tosql`, `src/char/char.cpp`): entre uma coisa e outra o
  banco é uma cópia velha, e quem escreve nele está escrevendo num rascunho
  que vai ser substituído. O `UPDATE` responde `1 row affected`, o valor
  aparece se alguém for conferir por `SELECT`, e some quando o jogador
  desloga — falha calada e com atraso de horas, do tipo que se atribui a
  qualquer outra coisa.
  A guarda é `AND online = 0` **no próprio `UPDATE`**, e não na leitura de
  antes: entre ler e escrever o jogador pode ter entrado. Zero linha afetada
  é a resposta, e ela quer dizer "ele está no jogo", não "não existe".
  Duas ressalvas: a coluna `online` fica **presa em 1** se o servidor cair, e
  quem a destrava é o `char_set_all_offline_sql` na subida do char-server; e
  a mesma armadilha vale para toda tabela que o char-server mantenha em
  memória, não só a `char`. Caso vivo: o botão de destravar personagem do
  site, 2026-08-22.

- **Resposta HTTP sem `Cache-Control` NÃO fica sem cache: o navegador
  inventa um — e quanto mais VELHO o arquivo, mais tempo a cópia velha vale.**
  É o cache heurístico do RFC 9111 §4.2.2, e a regra usual é guardar por 10%
  do tempo decorrido desde o `Last-Modified`. Consequência que inverte a
  intuição: um `estilo.css` parado há uma semana continua sendo servido do
  disco do jogador por umas **quinze horas** depois de trocado, e o navegador
  **nem pergunta** — não há requisição, então não há 304, e nada aparece no
  log do servidor. O deploy diz sucesso, o arquivo certo está no servidor, e
  a tela do jogador é a antiga. Medido em 2026-08-22, quando a caixa de texto
  do formulário de chamado apareceu sem estilo para o dono e o CSS no ar já
  estava correto — o diagnóstico que engana é culpar o CSS, que é o único
  lugar onde não está o defeito.
  **A sonda que decide é `curl -sI` no arquivo público** e comparar com o que
  a tela mostra: se o servidor entrega o certo, o problema é do outro lado.
  A saída é `Cache-Control: no-cache`, que **não** quer dizer "não guarde" e
  sim "guarde, mas pergunte antes de usar" — com o `Last-Modified` que o
  `http.FileServer` já manda, a pergunta volta como um 304 de zero byte.
  Resposta com dado pessoal (`/api/`) leva `no-store`, que é outra coisa.
  **Cache já envenenado não se conserta do servidor**: quem carregou a página
  antes só vê o novo com recarga forçada (Cmd+Shift+R) ou quando o prazo
  heurístico vencer.
