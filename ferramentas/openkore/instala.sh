#!/usr/bin/env bash
#
# instala.sh - sobrepoe o que e' NOSSO num checkout limpo do openkore.
#
#     ferramentas/openkore/instala.sh /opt/openkore
#
# Roda no servidor, como o usuario dono da arvore (ragnarok). E' chamado
# pelo configura_fantasma.sh e tambem pelo atualiza_servidor.sh, que e'
# como uma mudanca no plugin chega la' depois do primeiro deploy.
#
# ---------------------------------------------------------------------
# POR QUE ESTE SCRIPT EXISTE, EM VEZ DE VERSIONAR O OPENKORE INTEIRO
#
# O openkore sao 233 MB de codigo de terceiros. O que e' nosso sao ~74 KB:
# um plugin e tres arquivos de configuracao. Versionar os 233 MB tornaria
# impossivel distinguir, num diff, o que mexemos do que veio de fora - o
# mesmo motivo pelo qual o rathena/ foi vendorizado com a "lei da
# customizacao" (CLAUDE.md secao 2).
#
# Entao: o upstream vem de um clone fixado num commit, e este script
# aplica os quatro enxertos por cima. Um clone novo nunca perde nada
# nosso, porque nada nosso mora dentro dele.
#
# O delta foi PROVADO em 2026-08-31, com um diff recursivo do checkout de
# desenvolvimento contra o upstream 51de1dd: fora dos quatro itens abaixo,
# so' diferem arquivos que o proprio openkore gera em tempo de execucao
# (fields/*.dist, fields/*.weight, tables/monsters.txt, tables/npcs.txt,
# tables/portalsLOS.txt) e backups locais (control/*.bak). Nada do
# upstream esta' faltando no nosso.
#
# ---------------------------------------------------------------------
# IDEMPOTENTE
#
# Pode rodar quantas vezes quiser. Os arquivos sao sobrescritos; o bloco
# do servers.txt so' e' acrescentado se ainda nao estiver la'.
#
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="${1:-}"

ok()    { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()  { printf '    \033[90m--\033[0m   %s\n' "$*"; }
erro()  { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ -n "$DESTINO" ] || erro "uso: instala.sh <caminho-do-openkore>"
[ -f "$DESTINO/openkore.pl" ] || erro "$DESTINO nao parece um openkore (falta openkore.pl)"

printf '\n\033[1;36m==> Aplicando o delta em %s\033[0m\n' "$DESTINO"

# ---------------------------------------------------------------------
# 1. o plugin
install -d "$DESTINO/plugins/pvpGhost"
install -m 644 "$AQUI/plugins/pvpGhost/pvpGhost.pl" "$DESTINO/plugins/pvpGhost/pvpGhost.pl"
install -m 644 "$AQUI/plugins/pvpGhost/README.md"   "$DESTINO/plugins/pvpGhost/README.md"
ok "plugins/pvpGhost/"

# ---------------------------------------------------------------------
# 2. as configuracoes
#
# O config.txt versionado NAO tem a senha: ele traz um "!include
# fantasma.txt", e quem cria o link control/fantasma.txt ->
# /etc/guerra/fantasma.txt e' o configura_fantasma.sh. Este script nao
# encosta nesse link, de proposito - assim rodar o instala.sh de novo
# nunca destroi o segredo da maquina.
install -m 644 "$AQUI/control/config.txt" "$DESTINO/control/config.txt"
install -m 644 "$AQUI/control/sys.txt"    "$DESTINO/control/sys.txt"
ok "control/config.txt e control/sys.txt"

if [ -e "$DESTINO/control/fantasma.txt" ]; then
    ok "control/fantasma.txt (o segredo ja' esta' no lugar)"
else
    printf '    \033[33m!!\033[0m   control/fantasma.txt NAO existe - o bot nao vai conseguir logar.\n'
    printf '         Crie /etc/guerra/fantasma.txt e o link, ou rode o configura_fantasma.sh.\n'
fi

# ---------------------------------------------------------------------
# 3. o bloco do servers.txt
#
# Aqui e' acrescimo, nao substituicao: o servers.txt do upstream tem
# ~400 linhas de outros servidores que nao nos interessam, mas trocar o
# arquivo inteiro por um nosso significaria reconciliar essas 400 linhas
# a cada atualizacao do openkore. Entao anexamos so' o nosso bloco.
SERVIDORES="$DESTINO/tables/servers.txt"
if grep -q '^\[Guerra do Emperium - Local\]' "$SERVIDORES"; then
    pula "tables/servers.txt (bloco ja' presente)"
else
    printf '\n' >> "$SERVIDORES"
    cat "$AQUI/tables/servers.txt.bloco" >> "$SERVIDORES"
    ok "tables/servers.txt (bloco acrescentado)"
fi

# ---------------------------------------------------------------------
# 4. o que NAO precisa viajar
#
# 43 dos 233 MB sao dois plugins que o sys.txt nem carrega
# (loadPlugins_list pvpGhost,reconnect). Num disco de 24 GB isso e'
# conforto, nao necessidade - mas e' peso morto que so' confunde quem
# for olhar a pasta depois.
for inutil in LATAMTranslate needs-review; do
    if [ -d "$DESTINO/plugins/$inutil" ]; then
        rm -rf "${DESTINO:?}/plugins/$inutil"
        ok "removido plugins/$inutil (nao esta' no loadPlugins_list)"
    fi
done

printf '\n\033[32mDelta aplicado.\033[0m\n'
