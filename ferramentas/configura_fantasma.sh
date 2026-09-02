#!/usr/bin/env bash
#
# configura_fantasma.sh - poe o bot fantasma de pe' na maquina do servidor.
#
# COMO RODAR (do Mac):
#
#     ssh libraro 'bash -s' < ferramentas/configura_fantasma.sh
#
# Roda NA MAQUINA ALVO, como root. IDEMPOTENTE: pode rodar de novo sem
# medo - ele nao regera segredo que ja' existe e nao refaz build que ja'
# esta' feito (use --recompila para forcar).
#
# NAO INICIA O SERVICO. Ao final ele imprime o comando para voce dar o
# start quando quiser - a ideia e' poder preparar tudo com o servidor
# cheio e ligar o bot com ele vazio.
#
# ---------------------------------------------------------------------
# O QUE ELE FAZ
#
#   1. instala as dependencias de build do XSTools
#   2. clona o openkore no commit fixado, como o usuario ragnarok
#   3. compila o XSTools (a unica parte que pode falhar de verdade)
#   4. aplica o nosso delta (ferramentas/openkore/instala.sh)
#   5. cria /etc/guerra/fantasma.txt e o link control/fantasma.txt
#   6. escreve a unit do systemd
#
# ---------------------------------------------------------------------
# POR QUE O OPENKORE NAO MORA DENTRO DE /opt/guerra-do-emperium
#
# Aquele diretorio E' o nosso repositorio git, e o atualiza_servidor.sh
# roda "git reset --hard" nele. Um clone de terceiros ali dentro viraria
# submodulo acidental ou lixo nao rastreado, e o reset o destruiria. O
# openkore mora ao lado, em /opt/openkore, e a unica ponte entre os dois
# e' o instala.sh - que le' de um e escreve no outro.
#
# ---------------------------------------------------------------------
# AS TRES ARMADILHAS QUE ESTE SCRIPT EXISTE PARA EVITAR
#
# 1. O INCLUDE DA SENHA NAO ACEITA CAMINHO ABSOLUTO.
#    Utils::TextReader::add (TextReader.pm:80) concatena SEMPRE o
#    diretorio do arquivo pai, sem testar se o caminho e' absoluto:
#    "!include /etc/guerra/fantasma.txt" vira
#    "/opt/openkore/control//etc/guerra/fantasma.txt" e o boot morre com
#    "File does not exist". Por isso o config.txt usa "!include
#    fantasma.txt" (relativo) e este script cria o LINK. Testado com o
#    parser real em 2026-08-31.
#
# 2. O SCONS EMBUTIDO E' DE 2019 (scons-local-3.1.2) e nao e' confiavel
#    com o Python 3.12 do Ubuntu 24.04. Este script prefere o scons do
#    apt (4.x) e so' cai no embutido se o do sistema faltar.
#
# 3. O BOT NAO PODE SUBIR ANTES DO MAP-SERVER. O "After=" do systemd
#    ordena a partida mas nao espera o map-server ficar pronto - quem
#    resolve de fato e' o Restart=always somado ao plugin "reconnect".
#
set -euo pipefail

USUARIO="ragnarok"
RAIZ_REPO="/opt/guerra-do-emperium"
OPENKORE="/opt/openkore"
SEGREDOS="/etc/guerra"
ARQUIVO_SEGREDO="$SEGREDOS/fantasma.txt"
UNIT="/etc/systemd/system/guerra-fantasma.service"

# O commit do upstream contra o qual o nosso delta foi conferido. Subir
# este numero e' decisao consciente: depois de trocar, rode o instala.sh
# e teste o bot antes de considerar feito.
OPENKORE_REPO="https://github.com/OpenKore/openkore.git"
OPENKORE_COMMIT="51de1ddfc4449ae5217f6886de702f87ca934030"   # 2026-08-10

RECOMPILA=0
[ "${1:-}" = "--recompila" ] && RECOMPILA=1

passo()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()     { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()   { printf '    \033[90m--\033[0m   %s\n' "$*"; }
aviso()  { printf '    \033[33m!!\033[0m   %s\n' "$*"; }
erro()   { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

como_jogo() { runuser -u "$USUARIO" -- "$@"; }

# ---------------------------------------------------------------------
# "ESTOU NA MAQUINA CERTA?" - a primeira pergunta, e nao a terceira.
#
# Este script roda NO SERVIDOR. Rodado no Mac ele passa pela checagem de
# root (com sudo) e so' quebra la' na frente, num comando de systemd que
# o macOS nao tem - e a mensagem resultante manda consertar a coisa
# errada. Aconteceu em 2026-09-02: a checagem de usuario abaixo dizia
# "rode o provisiona.sh antes", o provisiona.sh foi rodado no Mac, e
# morreu em "timedatectl: command not found". Duas mensagens, nenhuma
# apontando para a verdadeira causa.
[ "$(uname -s)" = "Linux" ] || erro "isto roda no SERVIDOR, nao nesta maquina ($(uname -s)).
       Do Mac:  ssh libraro 'bash -s' < ferramentas/configura_fantasma.sh"
command -v systemctl >/dev/null 2>&1 || erro "nao ha systemd aqui - esta maquina nao e' o servidor.
       Do Mac:  ssh libraro 'bash -s' < ferramentas/configura_fantasma.sh"

[ "$(id -u)" = "0" ] || erro "rode como root"

# Se o ragnarok nao existe numa maquina que JA' passou nas duas checagens
# acima, entao ou e' um servidor novo, ou e' o servidor errado. O
# provisiona.sh so' entra no primeiro caso - e nunca de novo no servidor
# que ja' esta' no ar, porque ele mexe em usuario, firewall e SSH.
id "$USUARIO" >/dev/null 2>&1 || erro "usuario $USUARIO nao existe.
       Se esta e' a maquina de producao que ja' esta' no ar, algo esta' muito errado -
       NAO rode o provisiona.sh nela. Se e' uma maquina nova, ai' sim:
       ssh <maquina> 'bash -s' < ferramentas/provisiona.sh"

[ -d "$RAIZ_REPO/ferramentas/openkore" ] || erro "$RAIZ_REPO/ferramentas/openkore nao existe.
       O repositorio no servidor esta' desatualizado: rode o ferramentas/implanta.sh antes."

# ---------------------------------------------------------------------
passo "1/6  Dependencias de build"
#
# perl + libperl-dev  -> o XSTools e' um modulo XS; precisa dos headers e
#                        do xsubpp/typemap do ExtUtils
# libncurses-dev      -> SConstruct:193 checa ncurses
# libreadline-dev     -> SConstruct:195 aborta sem readline
# libcurl4-openssl-dev-> SConstruct:209 aborta sem libcurl
# scons               -> 4.x do apt, no lugar do 3.1.2 embutido (armadilha 2)
FALTANDO=()
for p in build-essential perl libperl-dev libncurses-dev libreadline-dev libcurl4-openssl-dev scons git; do
    dpkg -s "$p" >/dev/null 2>&1 || FALTANDO+=("$p")
done
if [ ${#FALTANDO[@]} -gt 0 ]; then
    aviso "instalando: ${FALTANDO[*]}"
    DEBIAN_FRONTEND=noninteractive apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${FALTANDO[@]}"
    ok "dependencias instaladas"
else
    pula "dependencias ja' instaladas"
fi

# ---------------------------------------------------------------------
passo "2/6  Clone do openkore ($OPENKORE)"
if [ -d "$OPENKORE/.git" ]; then
    ATUAL="$(como_jogo git -C "$OPENKORE" rev-parse HEAD)"
    if [ "$ATUAL" = "$OPENKORE_COMMIT" ]; then
        pula "ja' esta' no commit fixado (${OPENKORE_COMMIT:0:10})"
    else
        aviso "estava em ${ATUAL:0:10}, indo para ${OPENKORE_COMMIT:0:10}"
        como_jogo git -C "$OPENKORE" fetch --quiet origin
        como_jogo git -C "$OPENKORE" checkout --quiet --force "$OPENKORE_COMMIT"
        RECOMPILA=1
        ok "checkout trocado (vai recompilar)"
    fi
else
    install -d -o "$USUARIO" -g "$USUARIO" "$OPENKORE"
    como_jogo git clone --quiet "$OPENKORE_REPO" "$OPENKORE"
    como_jogo git -C "$OPENKORE" checkout --quiet --force "$OPENKORE_COMMIT"
    RECOMPILA=1
    ok "clonado em ${OPENKORE_COMMIT:0:10}"
fi

# ---------------------------------------------------------------------
passo "3/6  Compilando o XSTools"
#
# E' o unico passo com risco real de falhar. O XSTools e' um modulo XS em
# C++ e o openkore nao roda sem ele - "use XSTools" e' a linha 25 do
# openkore.pl. Em Linux o SConscript ja' cria o link XSTools.so ->
# libXSTools.so que o DynaLoader do Perl espera (SConscript:177).
ALVO="$OPENKORE/src/auto/XSTools/XSTools.so"
if [ -f "$ALVO" ] && [ "$RECOMPILA" = "0" ]; then
    pula "XSTools.so ja' existe (use --recompila para forcar)"
else
    if command -v scons >/dev/null 2>&1; then
        ok "usando o scons do sistema ($(scons --version 2>/dev/null | grep -o 'v[0-9.]*' | head -1))"
        como_jogo sh -c "cd '$OPENKORE' && scons" || erro "a compilacao do XSTools falhou - leia a saida acima. Sem XSTools o openkore nao sobe."
    else
        aviso "scons do sistema ausente, caindo no embutido (3.1.2, de 2019)"
        como_jogo sh -c "cd '$OPENKORE' && python3 src/scons-local-3.1.2/scons.py" || erro "a compilacao do XSTools falhou com o scons embutido. Instale o scons do apt e rode de novo."
    fi
    [ -f "$ALVO" ] || erro "a compilacao terminou sem erro mas $ALVO nao existe"
    ok "XSTools.so compilado"
fi

# ---------------------------------------------------------------------
passo "4/6  Aplicando o nosso delta"
como_jogo "$RAIZ_REPO/ferramentas/openkore/instala.sh" "$OPENKORE"

# ---------------------------------------------------------------------
passo "5/6  O segredo da conta"
#
# Mesmo padrao do /etc/guerra/site.env: fora do repositorio, para que
# nenhum comando de git o alcance e ele sobreviva a um reclone.
install -d -m 755 "$SEGREDOS"
if [ -f "$ARQUIVO_SEGREDO" ]; then
    pula "$ARQUIVO_SEGREDO ja' existe (nao foi tocado)"
else
    cat > "$ARQUIVO_SEGREDO" <<'FIM'
# Credenciais da conta do bot fantasma. Incluido pelo control/config.txt
# do openkore atraves de "!include fantasma.txt" (o link ao lado).
#
# TROQUE OS DOIS VALORES ABAIXO antes de iniciar o servico.
#
# A senha aqui e' TEXTO PURO - e' o que o protocolo exige. No banco ela
# fica em MD5 (use_MD5_passwords, conf/guerra/login_guerra.txt:48):
#
#     UPDATE login SET user_pass = MD5('a-senha') WHERE userid='fantasma';
#
# E aqui tambem entra qualquer coisa que seja DESTA MAQUINA e nao do
# repositorio, porque o include e a ultima palavra do config.txt. O caso
# que importa e o slot do personagem: se ele nao nascer no slot 1,
# descomente a linha abaixo em vez de editar o config.txt - aquele arquivo
# e versionado e o instala.sh o sobrescreve a cada deploy.
#
#   char 3
#
password TROQUE-ME
loginPinCode 0000
FIM
    aviso "criado $ARQUIVO_SEGREDO com valores de exemplo - TROQUE antes de iniciar"
fi
chown "$USUARIO:$USUARIO" "$ARQUIVO_SEGREDO"
chmod 600 "$ARQUIVO_SEGREDO"
ok "permissao 600, dono $USUARIO"

# o link relativo, que e' o que faz o !include funcionar (armadilha 1)
if [ -L "$OPENKORE/control/fantasma.txt" ]; then
    pula "link control/fantasma.txt ja' existe"
else
    rm -f "$OPENKORE/control/fantasma.txt"
    como_jogo ln -s "$ARQUIVO_SEGREDO" "$OPENKORE/control/fantasma.txt"
    ok "link control/fantasma.txt -> $ARQUIVO_SEGREDO"
fi

# ---------------------------------------------------------------------
passo "6/6  A unit do systemd"
#
# Console::Simple e' seguro sem terminal, e isso foi conferido no codigo
# (2026-08-31): o ritmo do laco principal vem do usleep(sleepTime) da
# Interface.pm:73, nao da entrada, entao stdin em EOF nao faz o processo
# girar em 100% de CPU. E todo prompt (senha, errorDialog) devolve undef
# em EOF e leva a um quit() limpo, que o Restart=always recolhe.
cat > "$UNIT" <<FIM
[Unit]
Description=Guerra do Emperium - bot fantasma da Arena de Combate
Documentation=file://$RAIZ_REPO/ferramentas/openkore/plugins/pvpGhost/README.md
After=guerra-map.service
Wants=guerra-map.service

[Service]
Type=simple
User=$USUARIO
Group=$USUARIO
WorkingDirectory=$OPENKORE
ExecStart=/usr/bin/perl $OPENKORE/openkore.pl --interface Console::Simple

# O After= ordena a partida mas nao espera o map-server aceitar conexao.
# Quem de fato resolve e' isto, junto com o plugin "reconnect" do
# sys.txt: o bot tenta, falha, e o systemd o traz de volta.
Restart=always
RestartSec=15

# Sem terminal. O laco nao depende de stdin (ver acima), e um prompt que
# apareca vira EOF -> undef -> quit(), que e' o comportamento desejado
# num servico: morrer alto em vez de pendurar calado.
StandardInput=null

# Mesmas quatro travas dos outros quatro servicos. O bot fala com o
# mundo por socket e nao precisa de privilegio nenhum.
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
FIM
systemctl daemon-reload
ok "$UNIT escrita"

# ---------------------------------------------------------------------
printf '\n\033[1;32m== Preparado. O servico NAO foi iniciado. ==\033[0m\n\n'
printf 'Antes de ligar, tres coisas que nao vem do git:\n\n'
printf '  1. a senha e o PIN de verdade em %s\n' "$ARQUIVO_SEGREDO"
printf '  2. a conta no banco, com group_id 20:\n'
printf '       INSERT ... userid='"'"'fantasma'"'"', user_pass=MD5('"'"'...'"'"'), group_id=20\n'
printf '  3. o personagem Renegado criado, o "char N" do config.txt\n'
printf '     apontando para o slot dele, e os dois itens na mochila:\n'
printf '       #item <char> 30993 1     (Tinta para Parede Infinita)\n'
printf '       #item <char> 30992 1     (Pincel do Infinito)\n'
printf '\nQuando a arena estiver vazia:\n\n'
printf '    systemctl enable --now guerra-fantasma\n'
printf '    journalctl -u guerra-fantasma -f\n\n'
printf 'Para desligar, a qualquer momento e sem afetar ninguem:\n\n'
printf '    systemctl disable --now guerra-fantasma\n\n'
