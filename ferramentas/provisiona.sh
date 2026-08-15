#!/usr/bin/env bash
#
# provisiona.sh - prepara uma maquina Ubuntu limpa para receber o servidor.
#
# Cobre as Etapas 4 (SO e seguranca), 5 (dependencias) e 6 (banco) do
# IMPLANTACAO.md. NAO clona o repositorio e NAO compila: isso e' o
# atualiza_servidor.sh.
#
# O repositorio e' PUBLICO, entao o servidor clona por HTTPS e nao precisa
# de chave nenhuma para o GitHub - nem deploy key, nem chave pessoal
# copiada para ca'. Se um dia ele fechar, e' aqui que entra a deploy key.
#
# COMO RODAR (do Mac, o script viaja pelo proprio ssh):
#
#     ssh libraro 'bash -s' < ferramentas/provisiona.sh
#
# Roda como root, na maquina alvo. E' IDEMPOTENTE: rodar de novo nao
# quebra nada e nao refaz o que ja' esta' feito - cada passo comeca
# perguntando se precisa agir. Isso e' requisito, nao capricho: e' o que
# permite rodar de novo depois de um passo falhar no meio.
#
# O ENDURECIMENTO DO SSH NAO ESTA AQUI, DE PROPOSITO.
# Mexer em quem pode entrar e' o jeito mais facil de se trancar para fora
# desta maquina, e a unica saida seria o console de recuperacao da
# DigitalOcean. Entao ele e' um passo separado, rodado a mao:
#
#     ssh libraro 'bash -s -- endurece' < ferramentas/provisiona.sh
#
# ---------------------------------------------------------------------
# QUEM E' QUEM NESTA MAQUINA (decisao do dono, 2026-08-14)
#
# root      - administra. Entra SO' por chave (prohibit-password), roda os
#             scripts de atualizacao e o systemctl. E' uma pessoa so' usando,
#             entao o rastro de auditoria que um usuario com sudo daria nao
#             tem a quem servir aqui.
# ragnarok  - roda os quatro servidores. SEM sudo, de proposito, e essa e' a
#             separacao que importa: o map-server processa pacote de gente
#             anonima da internet e o web-server recebe upload de arquivo.
#             Sao os programas que um dia levam um estouro de buffer. Quando
#             isso acontecer, o atacante cai no usuario que roda o processo -
#             e ali ele fica, preso em arquivos que voltam com um git pull.
#             Dar sudo ao ragnarok apagaria justamente esse limite.
#
# O perimetro inteiro, portanto, e' a chave privada do Mac - que nao tem
# passphrase, de proposito, para o deploy ser automatizavel. Backup dela,
# quando houver, criptografado.
#
# ---------------------------------------------------------------------
# Decisoes tomadas aqui, e o porque de cada uma:
#
# SWAP DE 2 GB - a maquina tem 1 GB e swap zero. O pico de memoria do
#   projeto e' a COMPILACAO (g++ -O2 numa unidade grande do map-server
#   chega perto de 1 GB sozinha), e sem swap o OOM killer mata o cc1plus
#   no meio do build. Em operacao normal o swap fica praticamente sem uso
#   - por isso o vm.swappiness baixo, que manda o kernel preferir a RAM.
#
# performance_schema DESLIGADO - ligado ele reserva sozinho 100-200 MB,
#   que numa maquina de 1 GB e' 10 a 20% de tudo. Nao usamos nada dele.
#
# innodb_buffer_pool_size FIXO EM 96M - o default se ajusta ao tamanho da
#   maquina, e queremos o numero previsivel para o map-server ter folga.
#
# CHARSET latin1 NO SERVIDOR, ANTES DE CRIAR AS TABELAS - as 105 colunas
#   de texto do rAthena sao latin1. Se o MariaDB subir com utf8mb4 como
#   default, as tabelas nascem erradas e o defeito so' aparece quando
#   alguem criar personagem acentuado, muito depois. Ver IMPLANTACAO.md
#   Etapa 6 e CLAUDE.md, secao 5, entrada da conexao utf8mb4.
#
# 3306 SO' EM 127.0.0.1 - e' o erro classico e catastrofico de servidor de
#   jogo. O bind-address entra junto do resto da configuracao.
#
# SENHA DO BANCO SO' COM LETRA E NUMERO - o parser de configuracao do
#   rAthena le' o valor ate' o fim da linha, sem aspas nem escape; caractere
#   de pontuacao ali e' pedir defeito calado. 32 caracteres alfanumericos
#   dao entropia de sobra sem correr esse risco.
#
# A SENHA NAO VAI PARA O GIT - ela e' gravada em /root/senha-banco.txt
#   (modo 600) e depois copiada a mao para conf/import/inter_conf.txt, que
#   e' a unica configuracao que nao vem do repositorio (Etapa 7).
#
set -euo pipefail

# ---------------------------------------------------------------------
# Parametros
# ---------------------------------------------------------------------
USUARIO="ragnarok"                       # dono dos quatro servidores; sem sudo
RAIZ="/opt/guerra-do-emperium"          # onde o repositorio vai ser clonado
BANCO="guerra"
BANCO_USUARIO="guerra"
ARQUIVO_SENHA="/root/senha-banco.txt"
SWAP="/swapfile"
# 4G, e nao 2G: medido em 2026-08-14 nesta maquina de 961 MB, o skill.cpp
# do map-server sozinho levou a RAM a 947 MB E o swap a 1,8 GB - sobravam
# 245 MB quando o cc1plus ainda estava subindo. Com 2G o build morre de OOM
# no meio, depois de vinte minutos de trabalho. Ver IMPLANTACAO.md Etapa 5.
SWAP_TAMANHO="4G"

# Portas que o mundo pode alcancar. A 8888 (web-server) NAO esta aqui de
# proposito: ela recebe upload de arquivo de usuario anonimo num HTTP
# embutido, e vai ficar atras do nginx (Etapa 8). A 3306 tambem nao, nunca.
PORTAS_PUBLICAS=(6900 6121 5121 80 443)

# ---------------------------------------------------------------------
# Saida
# ---------------------------------------------------------------------
passo()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()     { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()   { printf '    \033[90m--\033[0m   %s\n' "$*"; }
aviso()  { printf '    \033[33m!!\033[0m   %s\n' "$*"; }
erro()   { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "precisa rodar como root"

# =====================================================================
# endurece - passo separado, ver o cabecalho
# =====================================================================
if [ "${1:-}" = "endurece" ]; then
    passo "Endurecendo o SSH"

    # A trava: o root e' o caminho administrativo deste desenho, entao o que
    # nao pode faltar e' a chave DELE. Sem esta conferencia, um engano aqui
    # vira perda de acesso a' maquina, com o console de recuperacao da
    # DigitalOcean como unica saida.
    [ -s /root/.ssh/authorized_keys ] \
        || erro "/root/.ssh/authorized_keys vazio - endurecer agora TRANCA a maquina"
    aviso "root tem $(grep -c . /root/.ssh/authorized_keys) chave(s) autorizada(s)"

    # 10- e nao 99-: no sshd_config o PRIMEIRO valor obtido vence, nao o
    # ultimo (e' o inverso do nginx, do sysctl e de quase tudo que usa pasta
    # .d). O glob carrega em ordem alfabetica, e a imagem da DigitalOcean ja'
    # traz 50-cloud-init.conf e 60-cloudimg-settings.conf - um arquivo 99-
    # PERDERIA para os dois, calado. O Include na linha 12 do sshd_config vem
    # antes do PermitRootLogin da linha 42, entao o drop-in vence o arquivo
    # principal; e' so' entre drop-ins que a ordem importa.
    rm -f /etc/ssh/sshd_config.d/99-guerra.conf
    cat > /etc/ssh/sshd_config.d/10-guerra.conf <<'FIM'
# Endurecimento - Guerra do Emperium (ferramentas/provisiona.sh)
# Mora num drop-in para sobreviver a atualizacao de pacote sem merge.
# O 10 no nome e' deliberado: no sshd o primeiro valor vence.

# prohibit-password, e nao 'no': o root e' o usuario administrativo deste
# servidor (decisao do dono, 2026-08-14) e entra SO' por chave. Com 'yes'
# ele voltaria a aceitar senha; com 'no' a maquina ficaria sem nenhum
# acesso administrativo, porque o usuario do jogo nao tem sudo de proposito.
PermitRootLogin prohibit-password

# Ja' vinham desligados pelo cloud-init da imagem; repetidos aqui para a
# regra viajar no git e nao depender do que a imagem trouxe.
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
FIM

    sshd -t || erro "configuracao de sshd invalida - NADA foi aplicado"

    # No Ubuntu 24.04 o ssh e' ativado por socket: cada conexao gera um sshd
    # que le' a configuracao na hora. O reload cobre o servico; o restart do
    # socket cobre o caso de ele estar so' escutando. Nenhum dos dois derruba
    # sessao aberta.
    systemctl reload ssh 2>/dev/null || systemctl restart ssh.socket

    ok "aplicado - a sessao atual continua viva"
    echo
    sshd -T 2>/dev/null | grep -E '^(permitrootlogin|passwordauthentication|kbdinteractiveauthentication)' \
        | sed 's/^/    /'
    echo
    echo "    Teste em OUTRO terminal, sem fechar este:  ssh root@<ip>"
    exit 0
fi

# =====================================================================
# 1. Swap
# =====================================================================
passo "Swap"
if swapon --show | grep -q "$SWAP"; then
    pula "swap ja' ativo ($(free -h | awk '/^Swap:/{print $2}'))"
else
    fallocate -l "$SWAP_TAMANHO" "$SWAP" || dd if=/dev/zero of="$SWAP" bs=1M count=2048
    chmod 600 "$SWAP"
    mkswap "$SWAP" >/dev/null
    swapon "$SWAP"
    grep -q "^$SWAP" /etc/fstab || echo "$SWAP none swap sw 0 0" >> /etc/fstab
    ok "$SWAP_TAMANHO de swap ativo e persistente"
fi

# swappiness baixo: o swap existe para o pico do build, nao para o dia a dia.
if [ ! -f /etc/sysctl.d/99-guerra.conf ]; then
    echo "vm.swappiness=10" > /etc/sysctl.d/99-guerra.conf
    sysctl -q -p /etc/sysctl.d/99-guerra.conf
    ok "vm.swappiness=10"
else
    pula "vm.swappiness ja' configurado"
fi

# =====================================================================
# 2. Dependencias
# =====================================================================
passo "Pacotes"
export DEBIAN_FRONTEND=noninteractive

# O needrestart do Ubuntu 24.04 reinicia sozinho os servicos cuja
# biblioteca mudou - e a lista dele inclui o ssh.service. Rodando este
# script POR SSH, isso pode derrubar a propria conexao no meio do apt.
# Suspender o needrestart faz o apt so' instalar; quem reinicia servico
# aqui e' este script, na hora que ele escolher.
# (Nao confundir com o SIGPIPE de 2026-08-14, que era bug nosso na geracao
# da senha - ver o comentario la' embaixo. Esta precaucao continua valendo,
# mas nao foi ela que quebrou aquele dia.)
export NEEDRESTART_SUSPEND=1
export NEEDRESTART_MODE=l

# Lista lida do tools/docker/Dockerfile do proprio rAthena, traduzida de
# Alpine para Debian. O libpcre3-dev e' opcional (habilita comando de NPC
# com regex); o configure so' avisa se faltar.
#
# O libmariadb-dev-compat NAO e' redundante com o libmariadb-dev, e sem ele
# o configure para com "MySQL not found or incompatible" - com o MariaDB
# instalado e no ar. O motivo: o configure do rAthena procura os nomes do
# MySQL (mysql_config, mysql.h, -lmysqlclient), e o libmariadb-dev instala
# tudo com nome MariaDB (mariadb_config, /usr/include/mariadb/). O -compat
# e' o pacote que existe so' para fazer essa ponte. Medido em 2026-08-14.
PACOTES=(build-essential zlib1g-dev libmariadb-dev libmariadb-dev-compat
         libpcre3-dev mariadb-server nginx git make pkg-config ufw
         ca-certificates curl)

FALTANDO=()
for p in "${PACOTES[@]}"; do
    dpkg -s "$p" >/dev/null 2>&1 || FALTANDO+=("$p")
done

if [ ${#FALTANDO[@]} -eq 0 ]; then
    pula "todos os ${#PACOTES[@]} pacotes ja' instalados"
else
    ok "faltam ${#FALTANDO[@]}: ${FALTANDO[*]}"
    apt-get update -qq
    apt-get install -y -qq "${FALTANDO[@]}"
    ok "instalados"
fi
ok "$(gcc --version | head -1)"

# =====================================================================
# 3. Usuario dedicado
# =====================================================================
passo "Usuario $USUARIO"
# O rAthena nao precisa de privilegio nenhum e nao roda como root. Sem
# shell de login desabilitado: o deploy precisa de shell para o git pull.
if id "$USUARIO" >/dev/null 2>&1; then
    pula "usuario ja' existe"
else
    adduser --system --group --shell /bin/bash --home "/home/$USUARIO" "$USUARIO"
    ok "criado (sem senha, sem sudo)"
fi

# A chave que ja' funciona para o root serve para o usuario novo - e' o que
# torna o endurecimento seguro depois.
install -d -m 700 -o "$USUARIO" -g "$USUARIO" "/home/$USUARIO/.ssh"
if [ -f /root/.ssh/authorized_keys ]; then
    touch "/home/$USUARIO/.ssh/authorized_keys"
    while read -r linha; do
        [ -n "$linha" ] || continue
        grep -qxF "$linha" "/home/$USUARIO/.ssh/authorized_keys" 2>/dev/null \
            || echo "$linha" >> "/home/$USUARIO/.ssh/authorized_keys"
    done < /root/.ssh/authorized_keys
    chmod 600 "/home/$USUARIO/.ssh/authorized_keys"
    chown "$USUARIO:$USUARIO" "/home/$USUARIO/.ssh/authorized_keys"
    ok "$(wc -l < "/home/$USUARIO/.ssh/authorized_keys") chave(s) copiada(s) do root"
else
    aviso "root sem authorized_keys - o endurecimento vai recusar rodar"
fi

install -d -m 755 -o "$USUARIO" -g "$USUARIO" "$RAIZ"
ok "$RAIZ pronto"

# =====================================================================
# 4. Firewall
# =====================================================================
passo "Firewall"
# OpenSSH PRIMEIRO, sempre: habilitar o ufw sem essa regra derruba a sessao
# e tranca a maquina.
ufw allow OpenSSH >/dev/null
for porta in "${PORTAS_PUBLICAS[@]}"; do
    ufw allow "$porta/tcp" >/dev/null
done
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw --force enable >/dev/null
ok "aberto: SSH ${PORTAS_PUBLICAS[*]}"
ok "fechado: 3306 (banco) e 8888 (web-server, vai atras do nginx)"

# =====================================================================
# 5. MariaDB
# =====================================================================
passo "MariaDB"
CNF=/etc/mysql/mariadb.conf.d/99-guerra.cnf
if [ -f "$CNF" ]; then
    pula "configuracao ja' aplicada"
else
    cat > "$CNF" <<'FIM'
# Guerra do Emperium - ferramentas/provisiona.sh
# O porque de cada linha esta' no cabecalho daquele script.
[mysqld]
bind-address            = 127.0.0.1
performance_schema      = OFF
innodb_buffer_pool_size = 96M
character-set-server    = latin1
collation-server        = latin1_swedish_ci

[client]
default-character-set   = latin1
FIM
    ok "configuracao gravada"
fi

systemctl enable --now mariadb >/dev/null 2>&1 || true
systemctl restart mariadb
ok "no ar, escutando em 127.0.0.1"

# Senha: gerada uma vez e guardada. Se o arquivo ja' existe, reusa - assim
# rodar o script de novo nao invalida o conf/import/ que ja' esta' em uso.
if [ -f "$ARQUIVO_SENHA" ]; then
    SENHA="$(cat "$ARQUIVO_SENHA")"
    pula "senha reaproveitada de $ARQUIVO_SENHA"
else
    # openssl e nao 'tr -dc ... | head -c 32': naquela forma o head fecha o
    # cano ao completar 32 bytes, o tr morre de SIGPIPE e, com o pipefail
    # ligado la' em cima, o script inteiro cai - sem imprimir nada, porque
    # SIGPIPE e' silencioso. Custou duas rodadas em 2026-08-14.
    SENHA="$(openssl rand -hex 16)"
    umask 077; echo "$SENHA" > "$ARQUIVO_SENHA"; chmod 600 "$ARQUIVO_SENHA"
    ok "senha de 32 caracteres gerada em $ARQUIVO_SENHA"
fi

mariadb <<FIM
CREATE DATABASE IF NOT EXISTS \`$BANCO\` CHARACTER SET latin1 COLLATE latin1_swedish_ci;
CREATE USER IF NOT EXISTS '$BANCO_USUARIO'@'localhost' IDENTIFIED BY '$SENHA';
ALTER USER '$BANCO_USUARIO'@'localhost' IDENTIFIED BY '$SENHA';
GRANT ALL PRIVILEGES ON \`$BANCO\`.* TO '$BANCO_USUARIO'@'localhost';
FLUSH PRIVILEGES;
FIM
ok "banco '$BANCO' e usuario '$BANCO_USUARIO'@localhost prontos"

# A conferencia que a Etapa 6 pede: o charset tem de estar latin1 ANTES de
# as tabelas nascerem. Depois e' tarde.
CHARSET="$(mariadb -N -B -e "SELECT @@character_set_database;" "$BANCO")"
[ "$CHARSET" = "latin1" ] || erro "charset do banco e' '$CHARSET', esperado latin1"
ok "charset do banco conferido: latin1"

# =====================================================================
# Resumo
# =====================================================================
cat <<FIM

$(printf '\033[1;32m=== Provisionamento concluido ===\033[0m')

Memoria agora:
$(free -h | sed 's/^/    /')

FALTA FAZER, nesta ordem:

  1. Clonar e compilar:      ferramentas/atualiza_servidor.sh
  2. Escrever conf/import/   (Etapa 7) - a senha do banco esta' em
                             $ARQUIVO_SENHA
  3. Endurecer o SSH, DEPOIS de testar 'ssh $USUARIO@<ip>' do Mac:
     ssh libraro 'bash -s -- endurece' < ferramentas/provisiona.sh

FIM
