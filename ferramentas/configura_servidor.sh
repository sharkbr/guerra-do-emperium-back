#!/usr/bin/env bash
#
# configura_servidor.sh - Etapas 7 e 9 do IMPLANTACAO.md.
#
#   Etapa 7: escreve o conf/import/ da maquina (credenciais e IP publico)
#   Etapa 9: instala as quatro units do systemd, na ordem certa
#
# COMO RODAR (do Mac):
#
#     ssh libraro 'bash -s' < ferramentas/configura_servidor.sh
#
# IDEMPOTENTE, e aqui isso e' mais que boa pratica: os arquivos de
# conf/import/ guardam a senha da conta de comunicacao entre servidores, que
# tambem esta' gravada no BANCO. Reescrever um lado sem o outro faz o
# char-server parar de conectar - entao o script so' gera credencial nova
# quando ainda nao existe nenhuma, e nesse caso grava nos dois lugares.
#
# ---------------------------------------------------------------------
# POR QUE O conf/import/ NAO VEM DO GIT
#
# Ali moram senha do banco e IP publico. E' a unica configuracao que nasce
# na maquina, e o rAthena ja' a ignora no .gitignore dele (/conf/import) -
# ou seja, o 'git reset --hard' do atualiza_servidor.sh nao a alcanca.
# Conferido em 2026-08-15; era o acidente mais facil de cometer neste plano.
#
# ---------------------------------------------------------------------
# A ARMADILHA DA CONTA DE COMUNICACAO (a que este script existe para evitar)
#
# O char-server e o map-server se autenticam no login-server com uma conta
# da propria tabela `login`, a de sexo 'S'. Ela nasce do main.sql como
# s1/p1 com a senha EM TEXTO PURO - e o nosso use_MD5_passwords esta' ligado
# desde 2026-08-14. Sem converter, o char-server nao conecta, e o sintoma e'
#
#     "The server communication passwords (default s1/p1) are probably invalid"
#
# que aponta para o conf/import/ e nao para o MD5. Este script grava a senha
# ja' hasheada no banco e em claro nos arquivos - que e' como o rAthena
# espera os dois lados.
#
set -euo pipefail

USUARIO="ragnarok"
RAIZ="/opt/guerra-do-emperium"
EMULADOR="$RAIZ/rathena"
IMPORT="$EMULADOR/conf/import"
BANCO="guerra"
BANCO_USUARIO="guerra"
ARQUIVO_SENHA="/root/senha-banco.txt"

# O que o cliente vai procurar. Dominio e nao IP de proposito: o rAthena
# resolve com host2ip na subida e reresolve de tempos em tempos
# (char_logif.cpp:631), entao trocar de maquina um dia so' pede mexer no DNS.
ENDERECO_PUBLICO="${ENDERECO_PUBLICO:-libraro.filiponegrao.com.br}"
NOME_SERVIDOR="${NOME_SERVIDOR:-Guerra do Emperium}"

passo()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()     { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()   { printf '    \033[90m--\033[0m   %s\n' "$*"; }
aviso()  { printf '    \033[33m!!\033[0m   %s\n' "$*"; }
erro()   { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "precisa rodar como root"
[ -d "$EMULADOR" ] || erro "$EMULADOR nao existe - rode o atualiza_servidor.sh antes"
[ -f "$ARQUIVO_SENHA" ] || erro "$ARQUIVO_SENHA nao existe - rode o provisiona.sh antes"

SENHA_BANCO="$(cat "$ARQUIVO_SENHA")"
install -d -m 750 -o "$USUARIO" -g "$USUARIO" "$IMPORT"

# =====================================================================
# 1. Conta de comunicacao entre servidores
# =====================================================================
passo "Conta de comunicacao (a de sexo 'S')"

ARQUIVO_INTERSERVER="/root/senha-interserver.txt"
if [ -f "$ARQUIVO_INTERSERVER" ]; then
    # shellcheck disable=SC1090
    . "$ARQUIVO_INTERSERVER"
    pula "credencial reaproveitada de $ARQUIVO_INTERSERVER"
else
    # Alfanumerico: o parser de configuracao do rAthena le' o valor ate' o
    # fim da linha, sem aspas nem escape.
    #
    # 20 CARACTERES, E O TETO E' 23 - nao e' folga, e' limite duro. O
    # char_logif.cpp:826 monta o pacote de conexao com
    # 'memcpy(WFIFOP(login_fd,26), charserv_config.passwd, 24)': vinte e
    # quatro bytes, ponto, ainda que o PASSWD_LENGTH da tabela seja 33.
    # Senha maior e' TRUNCADA no pacote - o arquivo aceita, o banco guarda o
    # hash certo, e o login hasheia os 23 primeiros e recusa. A mensagem que
    # sai fala de "s1/p1 probably invalid", que manda procurar no lugar
    # errado. Medido em 2026-08-15 com uma senha de 32.
    INTER_USUARIO="srv_$(openssl rand -hex 4)"
    INTER_SENHA="$(openssl rand -hex 10)"
    umask 077
    printf 'INTER_USUARIO=%s\nINTER_SENHA=%s\n' "$INTER_USUARIO" "$INTER_SENHA" > "$ARQUIVO_INTERSERVER"
    chmod 600 "$ARQUIVO_INTERSERVER"
    ok "credencial nova gerada (substitui o s1/p1 padrao, que e' publico)"
fi

# A senha vai HASHEADA para o banco - use_MD5_passwords: yes. Ver o
# cabecalho. O MD5() e' do proprio MariaDB, o mesmo algoritmo do emulador.
mariadb "$BANCO" <<FIM
UPDATE login
   SET userid = '$INTER_USUARIO', user_pass = MD5('$INTER_SENHA')
 WHERE sex = 'S';
FIM
CONFERE="$(mariadb -N -B "$BANCO" -e "SELECT CONCAT(userid,' ',LENGTH(user_pass)) FROM login WHERE sex='S';")"
ok "no banco: $CONFERE (32 = MD5, como o use_MD5_passwords exige)"

# =====================================================================
# 2. conf/import/
# =====================================================================
passo "conf/import/ (Etapa 7)"

escreve() {
    local arquivo="$IMPORT/$1"; shift
    cat > "$arquivo"
    chown "$USUARIO:$USUARIO" "$arquivo"
    chmod 640 "$arquivo"
    ok "$(basename "$arquivo")"
}

escreve inter_conf.txt <<FIM
// Credenciais do banco - GERADO por ferramentas/configura_servidor.sh.
// NAO vai para o git: esta pasta esta' no .gitignore do rAthena.
//
// Os quatro servidores leem daqui, inclusive o web-server: ele carrega
// conf/inter_athena.conf na subida (src/web/web.cpp:463), que importa este
// arquivo no rodape.

login_server_ip: 127.0.0.1
login_server_port: 3306
login_server_id: $BANCO_USUARIO
login_server_pw: $SENHA_BANCO
login_server_db: $BANCO

ipban_db_ip: 127.0.0.1
ipban_db_port: 3306
ipban_db_id: $BANCO_USUARIO
ipban_db_pw: $SENHA_BANCO
ipban_db_db: $BANCO

char_server_ip: 127.0.0.1
char_server_port: 3306
char_server_id: $BANCO_USUARIO
char_server_pw: $SENHA_BANCO
char_server_db: $BANCO

map_server_ip: 127.0.0.1
map_server_port: 3306
map_server_id: $BANCO_USUARIO
map_server_pw: $SENHA_BANCO
map_server_db: $BANCO

web_server_ip: 127.0.0.1
web_server_port: 3306
web_server_id: $BANCO_USUARIO
web_server_pw: $SENHA_BANCO
web_server_db: $BANCO

log_db_ip: 127.0.0.1
log_db_port: 3306
log_db_id: $BANCO_USUARIO
log_db_pw: $SENHA_BANCO
log_db_db: $BANCO
FIM

escreve login_conf.txt <<FIM
// GERADO por ferramentas/configura_servidor.sh.

// EXPLICITO, e nao herdado do padrao: com 'yes', digitar nome_M na tela de
// login cria a conta na hora - e ai' o limite de uma conta por pessoa do
// site viraria decoracao, porque bastaria criar pelo cliente. O unico
// caminho para conta nova e' o site.
new_account: no
FIM

escreve char_conf.txt <<FIM
// GERADO por ferramentas/configura_servidor.sh.

// A conta de comunicacao com o login-server. A MESMA senha esta' no banco,
// hasheada - trocar aqui sem trocar la' derruba a conexao entre servidores.
userid: $INTER_USUARIO
passwd: $INTER_SENHA

// O nome que aparece na lista de servidores do cliente.
server_name: $NOME_SERVIDOR

// login_ip e' onde o CHAR procura o LOGIN: mesma maquina.
login_ip: 127.0.0.1

// char_ip e' o que o servidor ANUNCIA para o cliente. Tem de ser alcancavel
// da internet, senao o jogador loga e trava na selecao de personagem.
char_ip: $ENDERECO_PUBLICO
FIM

escreve map_conf.txt <<FIM
// GERADO por ferramentas/configura_servidor.sh.

userid: $INTER_USUARIO
passwd: $INTER_SENHA

// char_ip e' onde o MAP procura o CHAR: mesma maquina.
char_ip: 127.0.0.1

// map_ip e' o que o servidor ANUNCIA para o cliente.
map_ip: $ENDERECO_PUBLICO
FIM

# =====================================================================
# 3. Units do systemd (Etapa 9)
# =====================================================================
passo "systemd (Etapa 9)"

# A ordem e' a que o ferramentas/servidor.py ja' conhece:
#   login -> char -> web -> map
# O web entra no meio DE PROPOSITO. Com o nosso PACKETVER e' ele que recebe
# o emblema de cla por HTTP, e sem ele a falha e' completamente calada -
# ninguem reclama, o emblema so' nao aparece. Foi o que motivou aquele
# script em 2026-08-04 e e' o motivo de ele nao ficar por ultimo aqui.
anterior=""
for peca in login char web map; do
    unit="/etc/systemd/system/guerra-$peca.service"

    depende="After=network-online.target mariadb.service"
    [ -n "$anterior" ] && depende="$depende guerra-$anterior.service"

    cat > "$unit" <<FIM
[Unit]
Description=Guerra do Emperium - $peca-server
Documentation=file://$RAIZ/IMPLANTACAO.md
$depende
Wants=network-online.target
Requires=mariadb.service

[Service]
Type=simple
User=$USUARIO
Group=$USUARIO
WorkingDirectory=$EMULADOR
ExecStart=$EMULADOR/$peca-server
Restart=on-failure
RestartSec=5

# O rAthena nao precisa de privilegio nenhum. Estas quatro linhas custam
# nada e fecham a escalada mais obvia se um dia um dos servidores levar um
# estouro - e o map-server processa pacote de gente anonima da internet.
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
FIM
    ok "guerra-$peca.service"
    anterior="$peca"
done

systemctl daemon-reload
systemctl enable guerra-login guerra-char guerra-web guerra-map >/dev/null 2>&1
ok "as quatro habilitadas no boot"

# =====================================================================
passo "Pronto"
cat <<FIM

    Endereco anunciado ao cliente:  $ENDERECO_PUBLICO
    Nome na lista de servidores:    $NOME_SERVIDOR
    Conta de comunicacao:           $INTER_USUARIO (senha em $ARQUIVO_INTERSERVER)

    Subir:     systemctl start guerra-login guerra-char guerra-web guerra-map
    Ver:       systemctl status 'guerra-*'
    Log:       journalctl -u guerra-map -f

FIM
