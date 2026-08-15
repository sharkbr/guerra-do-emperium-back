#!/usr/bin/env bash
#
# configura_web.sh - Etapa 8 do IMPLANTACAO.md: o Apache na frente, e o
# site de criacao de conta publicado.
#
# COMO RODAR (do Mac):
#
#     ssh libraro 'bash -s' < ferramentas/configura_web.sh
#
# IDEMPOTENTE. Rodar de novo recompila o site e recarrega o Apache; nao
# regenera segredo nenhum (ver o bloco do /etc/guerra/site.env).
#
# ---------------------------------------------------------------------
# APACHE E NAO NGINX - decisao do dono, 2026-08-15.
#
# O provisiona.sh instalava nginx, mas nada nosso chegou a ser configurado
# nele: estava servindo a pagina padrao do Ubuntu. A troca custou uma
# desinstalacao. O preco em memoria e' pequeno e conhecido - o nginx ocupava
# 5 MB, o Apache com mpm_event fica entre 15 e 25 - e numa maquina com ~230
# MB livres isso e' perceptivel mas nao decisivo.
#
# ---------------------------------------------------------------------
# AS DUAS COISAS QUE O APACHE FAZ AQUI
#
# 1. PROXY DO web-server (8888). Com o nosso PACKETVER e' ele que recebe o
#    emblema de cla por HTTP, e a porta NAO fica exposta (o ufw a fecha):
#    quem fala com ela e' o Apache. Sem esse proxy o emblema simplesmente
#    nao sobe, e a falha e' COMPLETAMENTE CALADA - ninguem reclama, o
#    emblema so' nao aparece.
#
# 2. O SITE de criacao de conta, um binario Go em 127.0.0.1:8080.
#
# A ordem das regras importa: os caminhos do web-server vem ANTES do '/',
# senao o site engoliria tudo. E o /MerchantStore/ tem maiuscula no meio -
# o ProxyPass diferencia caixa, e escrever minusculo ali faz a loja de
# mercador falhar sem erro nenhum.
#
set -euo pipefail

USUARIO="ragnarok"
RAIZ="/opt/guerra-do-emperium"
SITE="$RAIZ/site"
DOMINIO="${DOMINIO:-libraro.filiponegrao.com.br}"
AMBIENTE="/etc/guerra/site.env"
ARQUIVO_SENHA="/root/senha-banco.txt"
BANCO="guerra"
BANCO_USUARIO="guerra"

passo()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()     { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()   { printf '    \033[90m--\033[0m   %s\n' "$*"; }
erro()   { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "precisa rodar como root"
[ -d "$SITE" ] || erro "$SITE nao existe - rode o atualiza_servidor.sh antes"
[ -f "$ARQUIVO_SENHA" ] || erro "$ARQUIVO_SENHA nao existe - rode o provisiona.sh antes"

export DEBIAN_FRONTEND=noninteractive NEEDRESTART_SUSPEND=1

# =====================================================================
# 1. Trocar nginx por Apache
# =====================================================================
passo "Servidor web"
if dpkg -s nginx >/dev/null 2>&1; then
    systemctl disable --now nginx >/dev/null 2>&1 || true
    apt-get purge -y -qq nginx nginx-common nginx-core >/dev/null 2>&1 || true
    apt-get autoremove -y -qq >/dev/null 2>&1 || true
    ok "nginx removido (nada nosso estava configurado nele)"
fi

if ! dpkg -s apache2 >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y -qq apache2
    ok "apache2 instalado"
else
    pula "apache2 ja' instalado"
fi

# mpm_event e' o de menor consumo dos tres, e e' o certo para um Apache que
# so' faz proxy e arquivo estatico - nao ha' PHP embutido aqui para exigir
# o prefork.
a2dismod mpm_prefork >/dev/null 2>&1 || true
a2enmod mpm_event proxy proxy_http headers rewrite >/dev/null 2>&1
ok "modulos: mpm_event, proxy, proxy_http, headers, rewrite"

# Go, para compilar o site. Cabe no servidor porque compilar Go leva
# segundos - ao contrario do C++ do emulador, que levou 67 minutos.
if ! command -v go >/dev/null 2>&1; then
    apt-get install -y -qq golang-go
    ok "$(go version)"
else
    pula "$(go version)"
fi

# =====================================================================
# 2. Configuracao do site (fora do repositorio, de proposito)
# =====================================================================
passo "Segredos do site"
# Mora em /etc/guerra/ e nao dentro de $SITE: assim NENHUM comando de git,
# nem o mais distraido, alcanca este arquivo.
install -d -m 750 -o root -g "$USUARIO" /etc/guerra

if [ -f "$AMBIENTE" ]; then
    pula "$AMBIENTE ja' existe - preservado"
else
    SEGREDO="$(openssl rand -hex 32)"
    SENHA_BANCO="$(cat "$ARQUIVO_SENHA")"
    cat > "$AMBIENTE" <<FIM
# GERADO por ferramentas/configura_web.sh - NAO vai para o git.
#
# ATENCAO ao SITE_SEGREDO: ele assina o cookie de sessao E gera o hash dos
# CPF/celular. Trocar invalida todos os hashes ja' gravados - as contas
# continuam funcionando, mas o limite de uma conta por documento deixa de
# reconhecer quem ja' se cadastrou, e todo mundo ganha direito a mais uma.
# Ele entra no backup e nao se troca por capricho.
SITE_ENDERECO=127.0.0.1:8080
SITE_BANCO_DSN=$BANCO_USUARIO:$SENHA_BANCO@tcp(127.0.0.1:3306)/$BANCO
SITE_SEGREDO=$SEGREDO
SITE_MAX_CONTAS=1
SITE_VERIFICACAO=nenhuma
SITE_PENELOPE_URL=
SITE_PENELOPE_TOKEN=
FIM
    chmod 640 "$AMBIENTE"
    chown root:"$USUARIO" "$AMBIENTE"
    ok "$AMBIENTE criado"
fi

# =====================================================================
# 3. Compilar o site
# =====================================================================
passo "Compilando o site"
cd "$SITE"
# GOCACHE e GOPATH proprios: o usuario do jogo nao tem HOME utilizavel para
# o Go, e sem isto o build falha com "failed to initialize build cache".
runuser -u "$USUARIO" -- env HOME=/tmp GOCACHE=/tmp/gocache GOPATH=/tmp/gopath \
    GOFLAGS=-mod=mod go build -o "$SITE/site" . \
    || erro "o site nao compilou"
ok "binario em $SITE/site ($(du -h "$SITE/site" | cut -f1))"

# =====================================================================
# 4. Unit do site
# =====================================================================
passo "systemd do site"
cat > /etc/systemd/system/guerra-site.service <<FIM
[Unit]
Description=Guerra do Emperium - site de criacao de conta
After=network-online.target mariadb.service
Wants=network-online.target
Requires=mariadb.service

[Service]
Type=simple
User=$USUARIO
Group=$USUARIO
WorkingDirectory=$SITE
EnvironmentFile=$AMBIENTE
ExecStart=$SITE/site
Restart=on-failure
RestartSec=5

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
FIM
systemctl daemon-reload
systemctl enable guerra-site >/dev/null 2>&1
systemctl restart guerra-site
ok "guerra-site.service"

# =====================================================================
# 5. O vhost
# =====================================================================
passo "Apache"
install -d -m 755 -o "$USUARIO" -g "$USUARIO" /var/www/patch

# ---------------------------------------------------------------------
# DOIS VHOSTS, GERADOS PELOS DOIS AQUI - e nao um deles pelo certbot.
#
# O certbot cria o guerra-le-ssl.conf copiando o guerra.conf do momento em
# que roda, e acrescenta o redirecionamento HTTP->HTTPS no de porta 80.
# Isso quebra na segunda vez que ESTE script roda: ele reescreve o
# guerra.conf, o redirecionamento some, e o vhost de 443 fica congelado na
# versao antiga. Aconteceu em 2026-08-15 e nao quebrou nada visivelmente -
# o site respondia nas duas portas -, o que e' exatamente o problema.
#
# Entao o script gera os dois, e o certbot so' cuida do certificado.
#
# ---------------------------------------------------------------------
# POR QUE A PORTA 80 NAO REDIRECIONA TUDO
#
# O cliente de Ragnarok fala HTTP PURO com o web-server (o AssistAddr dos
# ExternalSettings_*.lub e' uma string "host:porta", sem esquema). Se a
# porta 80 respondesse 301 para tudo, o POST do emblema morreria no
# redirecionamento - e a falha e' a mais calada que existe: o cliente nao
# mostra caixa de erro e o map-server nao registra nada. Ninguem relata
# isso como erro; dizem "escolhi o emblema e nao aconteceu nada".
#
# Entao: os cinco caminhos do web-server passam em HTTP; TODO o resto -
# site, cadastro, painel - e' redirecionado para HTTPS.
#
# O preco, registrado: nesses cinco caminhos o token de autenticacao do
# cliente viaja em claro. Se o cliente aceitar HTTPS no AssistAddr, e' so'
# apontar para 443 e apagar a excecao daqui.

CAMINHOS_WEB='(emblem|charconfig|userconfig|party|MerchantStore|twitter)'

corpo_proxy() {
    cat <<FIM
    ProxyPreserveHost On
    ProxyTimeout 30

    # O mod_proxy_http manda X-Forwarded-For e -Host sozinho, mas NAO o
    # -Proto. Sem esta linha o site nunca sabe que a conexao veio por HTTPS,
    # e o cookie de sessao deixa de ser marcado como Secure (sessao.go).
    RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}

    # O emblema e' um .bmp pequeno; qualquer coisa maior e' tentativa de
    # encher o disco de um servidor de 24 GB, e o upload vem de usuario
    # anonimo.
    <LocationMatch "^/$CAMINHOS_WEB/">
        LimitRequestBody 2097152
    </LocationMatch>

    # O /MerchantStore/ tem maiuscula, e o ProxyPass DIFERENCIA CAIXA -
    # escrever minusculo aqui faz a loja falhar sem erro nenhum.
    ProxyPass        /emblem/        http://127.0.0.1:8888/emblem/
    ProxyPassReverse /emblem/        http://127.0.0.1:8888/emblem/
    ProxyPass        /charconfig/    http://127.0.0.1:8888/charconfig/
    ProxyPassReverse /charconfig/    http://127.0.0.1:8888/charconfig/
    ProxyPass        /userconfig/    http://127.0.0.1:8888/userconfig/
    ProxyPassReverse /userconfig/    http://127.0.0.1:8888/userconfig/
    ProxyPass        /party/         http://127.0.0.1:8888/party/
    ProxyPassReverse /party/         http://127.0.0.1:8888/party/
    ProxyPass        /twitter/       http://127.0.0.1:8888/twitter/
    ProxyPassReverse /twitter/       http://127.0.0.1:8888/twitter/
    ProxyPass        /MerchantStore/ http://127.0.0.1:8888/MerchantStore/
    ProxyPassReverse /MerchantStore/ http://127.0.0.1:8888/MerchantStore/

    Alias /patch /var/www/patch
    <Directory /var/www/patch>
        Options -Indexes +FollowSymLinks
        Require all granted
    </Directory>
    ProxyPass /patch !

    ProxyPass        / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
FIM
}

{
    echo "# GERADO por ferramentas/configura_web.sh."
    echo "<VirtualHost *:80>"
    echo "    ServerName $DOMINIO"
    echo
    echo "    # Tudo para HTTPS, MENOS os caminhos do web-server - ver o"
    echo "    # cabecalho deste bloco no script."
    echo "    RewriteEngine On"
    echo "    RewriteCond %{REQUEST_URI} !^/$CAMINHOS_WEB/"
    echo "    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]"
    echo
    corpo_proxy
    echo "    ErrorLog  \${APACHE_LOG_DIR}/guerra-erro.log"
    echo "    CustomLog \${APACHE_LOG_DIR}/guerra-acesso.log combined"
    echo "</VirtualHost>"
} > /etc/apache2/sites-available/guerra.conf

CERT="/etc/letsencrypt/live/$DOMINIO/fullchain.pem"
if [ -f "$CERT" ]; then
    {
        echo "# GERADO por ferramentas/configura_web.sh."
        echo "<IfModule mod_ssl.c>"
        echo "<VirtualHost *:443>"
        echo "    ServerName $DOMINIO"
        echo
        corpo_proxy
        echo "    SSLEngine on"
        echo "    SSLCertificateFile    $CERT"
        echo "    SSLCertificateKeyFile /etc/letsencrypt/live/$DOMINIO/privkey.pem"
        echo "    Include /etc/letsencrypt/options-ssl-apache.conf"
        echo
        echo "    ErrorLog  \${APACHE_LOG_DIR}/guerra-erro.log"
        echo "    CustomLog \${APACHE_LOG_DIR}/guerra-acesso.log combined"
        echo "</VirtualHost>"
        echo "</IfModule>"
    } > /etc/apache2/sites-available/guerra-le-ssl.conf
    a2enmod ssl >/dev/null 2>&1
    a2ensite guerra-le-ssl >/dev/null 2>&1
    ok "vhost 443 (certificado presente)"
else
    ok "sem certificado ainda - so' o vhost 80. Rode o certbot e este script de novo."
fi

a2dissite 000-default >/dev/null 2>&1 || true
a2ensite guerra >/dev/null 2>&1
apache2ctl configtest 2>&1 | grep -v "Syntax OK" || true
apache2ctl configtest >/dev/null 2>&1 || erro "configuracao do Apache invalida - NADA aplicado"
systemctl enable apache2 >/dev/null 2>&1
systemctl restart apache2
ok "vhost $DOMINIO no ar"

# =====================================================================
passo "Pronto"
cat <<FIM

    Site:        http://$DOMINIO/
    Patch:       http://$DOMINIO/patch/   (pasta /var/www/patch)
    web-server:  atras do proxy, porta 8888 fechada no ufw

    Falta o HTTPS (certbot) - proximo passo.

FIM
