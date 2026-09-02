#!/usr/bin/env bash
#
# implanta_fantasma.sh - poe o bot fantasma de pe' no servidor. Roda NO MAC.
#
#     ferramentas/implanta_fantasma.sh
#     ferramentas/implanta_fantasma.sh --recompila    (forca rebuild do XSTools)
#
# ---------------------------------------------------------------------
# POR QUE ESTE WRAPPER EXISTE
#
# O trabalho de verdade esta' no ferramentas/configura_fantasma.sh, que
# roda NA MAQUINA ALVO. Ele precisa viajar pelo stdin do ssh:
#
#     ssh libraro 'bash -s' < ferramentas/configura_fantasma.sh
#
# e esse "< arquivo" e' facil de errar. Sem ele o script executa NO MAC,
# passa pela checagem de root com sudo, e falha la' na frente com uma
# mensagem que aponta para a coisa errada. Aconteceu em 2026-09-02: a
# mensagem dizia "rode o provisiona.sh antes", o provisiona.sh tambem foi
# rodado no Mac, e morreu em "timedatectl: command not found" - dois erros,
# nenhum apontando para a causa real, que era so' onde o script rodava.
#
# O configura_fantasma.sh ganhou uma guarda propria para isso. Este arquivo
# fecha o outro lado: torna a forma certa a forma curta. E' o mesmo papel
# que o implanta.sh cumpre para o atualiza_servidor.sh.
#
# ---------------------------------------------------------------------
# ELE NAO INICIA O BOT, E ISSO E' DE PROPOSITO
#
# Ao final o servidor fica preparado e o servico escrito, mas parado. O
# start e' seu, quando a arena estiver vazia - e antes dele faltam tres
# coisas que moram no BANCO e nao vem do git: a senha real, a conta com
# group_id 20, e o personagem Renegado com os dois itens infinitos. O
# proprio configura_fantasma.sh lista isso no fim.
#
# ---------------------------------------------------------------------
# ELE NAO E' O CAMINHO DE ATUALIZACAO
#
# Mudou o plugin ou a config? Isso viaja no deploy normal
# (ferramentas/implanta.sh), pela secao 6b do atualiza_servidor.sh, que
# reaplica o delta E reinicia o bot. Este script aqui e' para instalar,
# reparar, ou trocar a versao do openkore - casos em que ha compilacao
# envolvida.
#
# ---------------------------------------------------------------------
# POR QUE NAO RODA O prevoo.sh
#
# O pre-voo confere arquivos de rathena/ - caixa de caminho, \r sobrando e
# U+FFFD - e este deploy nao encosta em rathena/ nem reinicia servidor de
# jogo. Rodar aqui so' criaria a chance de reprovar por algo que este
# comando nem publica. O implanta.sh continua sendo quem o roda.
#
set -euo pipefail

SERVIDOR="${SERVIDOR:-libraro}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

azul()   { printf '\n\033[1;34m%s\033[0m\n' "$*"; }
aviso()  { printf '\033[33m!! %s\033[0m\n' "$*"; }
erro()   { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------
azul "== Conferencias locais =="

[ -f "$RAIZ/ferramentas/configura_fantasma.sh" ] \
    || erro "nao achei ferramentas/configura_fantasma.sh - o checkout esta' incompleto"

# O servidor puxa do GitHub, nao deste diretorio. Nao bloqueia - as vezes
# se quer instalar o que ja' esta' publicado e seguir editando - mas avisar
# e' obrigatorio, porque o sintoma de esquecer isso e' o script rodar,
# dizer "ok", e instalar a versao velha.
if [ -n "$(git -C "$RAIZ" status --porcelain -- ferramentas/openkore ferramentas/configura_fantasma.sh)" ]; then
    aviso "ha alteracoes nao commitadas no que este comando instala:"
    git -C "$RAIZ" status --short -- ferramentas/openkore ferramentas/configura_fantasma.sh | sed 's/^/     /'
    aviso "elas NAO vao para o servidor."
fi

PENDENTES="$(git -C "$RAIZ" log '@{u}..HEAD' --oneline 2>/dev/null || true)"
if [ -n "$PENDENTES" ]; then
    aviso "ha commits sem push - o servidor puxa do GitHub:"
    printf '%s\n' "$PENDENTES" | sed 's/^/     /'
fi

printf '    ok  checkout local\n'

# ---------------------------------------------------------------------
azul "== O servidor tem o delta? =="
#
# O configura_fantasma.sh le' o ferramentas/openkore/ do disco do servidor,
# e NAO puxa o repositorio sozinho. Se o deploy ainda nao levou a pasta
# para la', ele so' descobriria isso depois de instalar dependencia e
# clonar 233 MB. Perguntar antes custa um ssh.
FALTA="$(ssh "$SERVIDOR" 'test -d /opt/guerra-do-emperium/ferramentas/openkore && echo nao || echo sim')"
if [ "$FALTA" = "sim" ]; then
    erro "o servidor ainda nao tem ferramentas/openkore/.
       Rode o deploy normal primeiro, que e' quem leva o repositorio:

           ferramentas/implanta.sh"
fi

# Nao basta existir: pode estar atrasado. Comparar o commit dos dois lados
# e' o que evita instalar um plugin de tres deploys atras sem perceber.
LOCAL="$(git -C "$RAIZ" rev-parse HEAD)"
REMOTO="$(ssh "$SERVIDOR" 'git -C /opt/guerra-do-emperium rev-parse HEAD 2>/dev/null || echo desconhecido')"
if [ "$REMOTO" = "desconhecido" ]; then
    aviso "nao consegui ler o commit do servidor - seguindo assim mesmo"
elif [ "$LOCAL" != "$REMOTO" ]; then
    aviso "o servidor esta' em ${REMOTO:0:10} e este Mac em ${LOCAL:0:10}."
    if ! git -C "$RAIZ" diff --quiet "$REMOTO" "$LOCAL" -- ferramentas/openkore ferramentas/configura_fantasma.sh 2>/dev/null; then
        erro "e a diferenca inclui o que este comando instala.
       Rode o deploy normal primeiro:

           ferramentas/implanta.sh"
    fi
    aviso "mas nada do fantasma mudou entre os dois - pode seguir."
else
    printf '    ok  servidor no mesmo commit (%s)\n' "${LOCAL:0:10}"
fi

# ---------------------------------------------------------------------
azul "== Servidor ($SERVIDOR) - configurando o fantasma =="
# O '--' separa os argumentos do 'bash -s' e faz o --recompila chegar ao
# script que vem pelo stdin. Sem ele o bash o leria como opcao dele.
ssh "$SERVIDOR" "bash -s -- ${*:-}" < "$RAIZ/ferramentas/configura_fantasma.sh"

# ---------------------------------------------------------------------
azul "== Estado final =="
ssh "$SERVIDOR" '
for s in guerra-login guerra-char guerra-web guerra-map guerra-fantasma; do
    printf "    %-17s %s\n" "$s" "$(systemctl is-active "$s" 2>/dev/null || echo ausente)"
done
printf "\n    unit do fantasma:  %s\n" "$(systemctl is-enabled guerra-fantasma 2>/dev/null || echo "nao habilitada")"
'
