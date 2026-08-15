#!/usr/bin/env bash
#
# implanta.sh - o comando unico do deploy. Roda NO MAC.
#
#     ferramentas/implanta.sh
#
# E' de propósito um wrapper fino: toda a lógica mora no
# ferramentas/atualiza_servidor.sh, que é versionado e roda no servidor.
#
# ---------------------------------------------------------------------
# O PROBLEMA DO OVO E DA GALINHA, E COMO ELE É RESOLVIDO AQUI
#
# O script que faz o trabalho vem do próprio repositório — então ele
# precisaria já estar atualizado no servidor para saber como se atualizar.
# A saída é mandá-lo pelo stdin do ssh: o que roda é sempre a versão do
# Mac, e o `git pull` que ele faz atualiza o resto. Nenhuma versão velha
# de script sobrevive no servidor para atrapalhar.
#
# ---------------------------------------------------------------------
# O QUE ELE FAZ, NESTA ORDEM
#
#   1. pré-voo LOCAL, antes de tocar no servidor (Etapa 11)
#   2. avisa se há coisa não commitada — deploy do que não está no git é
#      a origem clássica do "funciona aqui e não lá"
#   3. git pull no servidor
#   4. recompila o emulador SÓ se src/ mudou (o build custa ~67 min)
#   5. recompila o site se site/ mudou (custa segundos)
#   6. pré-voo no servidor, e ABORTA sem reiniciar se reprovar
#   7. reinicia os quatro na ordem certa
#
set -euo pipefail

SERVIDOR="${SERVIDOR:-libraro}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

azul()  { printf '\n\033[1;34m%s\033[0m\n' "$*"; }
erro()  { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

azul "== Pré-voo local =="
"$RAIZ/ferramentas/prevoo.sh" "$RAIZ" || erro "pré-voo local reprovado — nada foi enviado"

# Não bloqueia: às vezes se quer subir um commit e seguir editando. Mas
# avisa, porque o servidor puxa do GitHub e não deste diretório — o que
# estiver só aqui simplesmente não vai.
if [ -n "$(git -C "$RAIZ" status --porcelain)" ]; then
    printf '\n\033[33m!! há alterações não commitadas — elas NÃO vão para o servidor:\033[0m\n'
    git -C "$RAIZ" status --short | sed 's/^/     /'
fi

PENDENTES="$(git -C "$RAIZ" log '@{u}..HEAD' --oneline 2>/dev/null || true)"
if [ -n "$PENDENTES" ]; then
    printf '\n\033[33m!! há commits sem push — o servidor puxa do GitHub:\033[0m\n'
    printf '%s\n' "$PENDENTES" | sed 's/^/     /'
fi

azul "== Servidor ($SERVIDOR) =="
ssh "$SERVIDOR" 'bash -s' < "$RAIZ/ferramentas/atualiza_servidor.sh"

azul "== Estado final =="
ssh "$SERVIDOR" 'for s in guerra-login guerra-char guerra-web guerra-map guerra-site apache2 mariadb; do
    printf "  %-14s %s\n" "$s" "$(systemctl is-active $s)"
done'
