#!/usr/bin/env bash
#
# implanta_site.sh - publica SO' o site. Roda NO MAC.
#
#     ferramentas/implanta_site.sh
#
# ---------------------------------------------------------------------
# POR QUE EXISTE UM SEGUNDO COMANDO DE DEPLOY
#
# O site e o jogo tem ritmos diferentes. O site e' Go, sobe em segundos e
# nao encosta em ninguem; o emulador so' reinicia DERRUBANDO todo mundo
# que estiver jogando, com um "Erro desconhecido" na tela deles. Com um
# comando so', publicar uma correcao de CSS as oito da noite exige escolher
# entre "publico" e "nao derrubo ninguem" - e a escolha errada ja' custou
# uma vez, em 2026-08-15.
#
# Este comando reinicia APENAS o guerra-site. Se vier mudanca de jogo de
# carona no mesmo pull - e vem, porque o repositorio e' um so' -, ela fica
# no disco e o script DIZ isso no fim, com a lista de arquivos. Resolve-se
# com @reloadscript em jogo (CLAUDE.md secao 3) ou com o implanta.sh
# completo quando o servidor esvaziar.
#
# ---------------------------------------------------------------------
# O QUE ELE **NAO** FAZ, E E' O DETALHE QUE IMPORTA
#
# Ele nao consome o gatilho do deploy seguinte. Ate' 2026-08-22 a decisao
# de reiniciar o jogo era o diff entre o HEAD de antes do pull e o de
# depois - entao qualquer atualizacao parcial fazia o proximo implanta.sh
# achar rathena/ sem mudanca e NAO reiniciar, com a frase de sucesso na
# tela e a configuracao velha viva no processo. Agora quem responde e' o
# .carimbo-jogo, que so' este arquivo aqui nao toca. Ver o cabecalho do
# atualiza_servidor.sh e o CLAUDE.md secao 5.
#
# ---------------------------------------------------------------------
# O QUE ELE NAO RESOLVE: TABELA NOVA
#
# Nenhum dos dois deploys roda SQL. Tabela nova em site/sql/site.sql tem de
# ser aplicada a mao, ANTES, e o site sobe sem ela sem reclamar - a falha
# aparece na cara do primeiro jogador que usar a funcao:
#
#     ssh libraro 'mysql guerra' < site/sql/site.sql
#
set -euo pipefail

SERVIDOR="${SERVIDOR:-libraro}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

azul()  { printf '\n\033[1;34m%s\033[0m\n' "$*"; }
erro()  { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

azul "== Pré-voo local =="
"$RAIZ/ferramentas/prevoo.sh" "$RAIZ" || erro "pré-voo local reprovado — nada foi enviado"

# Não bloqueia, mas avisa: o servidor puxa do GitHub, e não deste diretório.
if [ -n "$(git -C "$RAIZ" status --porcelain)" ]; then
    printf '\n\033[33m!! há alterações não commitadas — elas NÃO vão para o servidor:\033[0m\n'
    git -C "$RAIZ" status --short | sed 's/^/     /'
fi

PENDENTES="$(git -C "$RAIZ" log '@{u}..HEAD' --oneline 2>/dev/null || true)"
if [ -n "$PENDENTES" ]; then
    printf '\n\033[33m!! há commits sem push — o servidor puxa do GitHub:\033[0m\n'
    printf '%s\n' "$PENDENTES" | sed 's/^/     /'
fi

azul "== Servidor ($SERVIDOR) — somente o site =="
# O '--' separa os argumentos do 'bash -s' e faz o --so-site chegar ao
# script que vem pelo stdin. Sem ele, o bash o leria como opcao dele.
ssh "$SERVIDOR" 'bash -s -- --so-site' < "$RAIZ/ferramentas/atualiza_servidor.sh"

azul "== Estado final =="
ssh "$SERVIDOR" 'for s in guerra-login guerra-char guerra-web guerra-map guerra-site; do
    printf "    %-14s %s\n" "$s" "$(systemctl is-active "$s" 2>/dev/null || echo ausente)"
done'
