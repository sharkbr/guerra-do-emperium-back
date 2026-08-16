#!/usr/bin/env bash
#
# publica_patch.sh - poe os patches no ar.
#
#     ferramentas/publica_patch.sh                # os patches que faltam
#     ferramentas/publica_patch.sh --atualizador  # o Atualizador.exe novo
#     ferramentas/publica_patch.sh --confere      # so mostra o placar
#
# RODA NO WINDOWS (Git Bash), e nao no Mac: os .zip nascem de
# C:\GuerraDoEmperium\cliente, que so existe aqui. E' a excecao a regra da §9
# do CLAUDE.md - nao porque precise do jogo para conferir, mas porque o insumo
# nao existe do outro lado.
#
# ---------------------------------------------------------------------
# A ORDEM IMPORTA, E E' A UNICA COISA DELICADA AQUI
#
# O zip sobe ANTES da lista. Se a lista subisse primeiro, todo cliente que
# abrisse o Atualizador naquele intervalo pediria um arquivo que ainda nao
# existe - erro na cara do jogador, por nada. Na ordem certa, o pior caso e'
# um zip parado no servidor que ninguem pediu ainda.
#
# Pelo mesmo motivo NAO se apaga zip antigo do servidor: quem instalou o
# cliente ontem ainda vai baixar o patch 0001 amanha. O que sai da lista sai
# do ar para sempre - por isso o registro so cresce.
#
set -euo pipefail

SERVIDOR="${SERVIDOR:-libraro}"
DESTINO="${DESTINO:-/var/www/patch}"
PATCHES="${PATCHES:-/c/GuerraDoEmperium/patches}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRO="$RAIZ/patcher/patches.txt"

azul() { printf '\n\033[1;34m%s\033[0m\n' "$*"; }
erro() { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ -f "$REGISTRO" ] || erro "nao achei $REGISTRO - monte um patch primeiro"

# As linhas do registro que valem: cinco campos separados por TAB.
linhas() { grep -v '^[[:space:]]*#' "$REGISTRO" | grep -v '^[[:space:]]*$'; }

remotos() { ssh "$SERVIDOR" "ls -1 $DESTINO 2>/dev/null" || true; }

publica_patches() {
    azul "== O que o servidor ja tem =="
    local ja; ja="$(remotos)"
    echo "$ja" | sed 's/^/     /' | head -20

    local enviados=0
    while IFS=$'\t' read -r numero arquivo sha bytes nome; do
        if echo "$ja" | grep -qx "$arquivo"; then
            printf '  %s  %s (ja esta la)\n' "$numero" "$nome"
            continue
        fi
        local local_zip="$PATCHES/$arquivo"
        [ -f "$local_zip" ] || erro "o registro pede $arquivo, que nao esta em $PATCHES"

        # Confere o sha ANTES de enviar. O registro e' versionado e o zip nao:
        # um zip remontado com o mesmo nome e conteudo diferente e' o jeito
        # silencioso de o cliente do jogador recusar tudo depois.
        local aqui; aqui="$(sha256sum "$local_zip" | cut -d' ' -f1)"
        [ "$aqui" = "$sha" ] || erro "$arquivo nao confere com o registro (sha256)"

        azul "-> $numero  $nome"
        scp "$local_zip" "$SERVIDOR:$DESTINO/"
        enviados=$((enviados + 1))
    done < <(linhas)

    azul "== A lista, por ultimo =="
    scp "$REGISTRO" "$SERVIDOR:$DESTINO/lista.txt"
    ssh "$SERVIDOR" "chmod 644 $DESTINO/* && ls -la $DESTINO"
    printf '\n\033[1;32m%d zip(s) enviado(s); a lista esta no ar.\033[0m\n' "$enviados"
}

# O Atualizador nao entra em patch comum - ele nao consegue se sobrescrever
# enquanto roda. Este e' o canal proprio: um exe com o numero da versao no
# nome, mais o patcher.txt que o aponta.
publica_atualizador() {
    command -v go >/dev/null || erro "go nao esta no PATH (C:\\Program Files\\Go\\bin)"
    local versao
    versao="$(grep -oE 'VERSAO = [0-9]+' "$RAIZ/patcher/main.go" | grep -oE '[0-9]+')"
    [ -n "$versao" ] || erro "nao achei o const VERSAO em patcher/main.go"

    azul "== Compilando o Atualizador versao $versao =="
    (cd "$RAIZ/patcher" && go build -ldflags -H=windowsgui -o Atualizador.exe .)

    local nome="Atualizador-$versao.exe"
    local sha; sha="$(sha256sum "$RAIZ/patcher/Atualizador.exe" | cut -d' ' -f1)"

    azul "== Enviando =="
    scp "$RAIZ/patcher/Atualizador.exe" "$SERVIDOR:$DESTINO/$nome"

    # O patcher.txt sobe DEPOIS do exe, pelo motivo da ordem la em cima.
    printf '# Canal de auto-atualizacao do Atualizador. Gerado por publica_patch.sh.\nversao=%s\narquivo=%s\nsha256=%s\n' \
        "$versao" "$nome" "$sha" | ssh "$SERVIDOR" "cat > $DESTINO/patcher.txt && chmod 644 $DESTINO/patcher.txt"

    printf '\n\033[1;32mAtualizador %s no ar (%s).\033[0m\n' "$versao" "$nome"
    printf 'Quem ja tem o Atualizador antigo troca sozinho na proxima abertura.\n'
}

confere() {
    azul "== Registro (local) =="
    linhas | while IFS=$'\t' read -r numero arquivo sha bytes nome; do
        local marca="ausente aqui"
        [ -f "$PATCHES/$arquivo" ] && marca="ok"
        printf '  %s  %-46s %8s KB  %s\n' "$numero" "${nome:0:46}" "$((bytes / 1024))" "$marca"
    done
    azul "== Servidor ($SERVIDOR:$DESTINO) =="
    remotos | sed 's/^/     /'
}

case "${1:-}" in
    --atualizador) publica_atualizador ;;
    --confere)     confere ;;
    "")            publica_patches ;;
    *)             erro "opcao desconhecida: $1" ;;
esac
