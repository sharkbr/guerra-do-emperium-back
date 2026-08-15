#!/usr/bin/env bash
#
# prevoo.sh - Etapa 11 do IMPLANTACAO.md: as tres conferencias que rodam
# ANTES de qualquer subida.
#
#     ferramentas/prevoo.sh [raiz]
#
# Roda no Linux e no Mac. Sai com 0 se tudo passou, 1 se algo falhou - e' o
# que permite ao atualiza_servidor.sh abortar antes de reiniciar.
#
# ---------------------------------------------------------------------
# POR QUE ESTAS TRES, E NAO OUTRAS
#
# As tres falham CALADAS no Linux e NAO falham no Mac nem no Windows. Sao
# exatamente o tipo de defeito que so' aparece em producao:
#
# 1. CAIXA (maiuscula/minuscula). O APFS do Mac e o NTFS do Windows nao
#    diferenciam; o ext4 do Linux diferencia. Um 'import: conf/Guerra/x.txt'
#    funciona nas duas maquinas de desenvolvimento e no Linux o arquivo
#    simplesmente NAO CARREGA - sem erro, sem log, sem nada.
#
# 2. \r SOBRANDO. O npc_parsesrcfile corta a linha por \n; o \r que sobra
#    entra DENTRO do ultimo campo. Em nome de evento de spawn, vira parte
#    do nome - e o evento nunca dispara (CLAUDE.md secao 5).
#
# 3. U+FFFD. Arquivo cp1252 que passou por um editor UTF-8 tem o acento
#    trocado por \xef\xbf\xbd, e o byte original ja' nao esta' la' - nao e'
#    mojibake reversivel, e' perda. Vale para todo texto que o JOGO le'.
#
set -uo pipefail

RAIZ="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EMULADOR="$RAIZ/rathena"

verde()  { printf '\033[32m%s\033[0m' "$*"; }
vermelho() { printf '\033[31m%s\033[0m' "$*"; }
passo()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }

FALHAS=0
reprova() { printf '    %s %s\n' "$(vermelho '✗')" "$*"; FALHAS=$((FALHAS + 1)); }
aprova()  { printf '    %s %s\n' "$(verde '✓')" "$*"; }

[ -d "$EMULADOR" ] || { echo "nao achei $EMULADOR" >&2; exit 2; }

# =====================================================================
passo "1. Caixa dos caminhos (o que o Linux pune e o Mac esconde)"
# =====================================================================
# Junta os tres jeitos de um arquivo do rAthena apontar para outro.
CONFERIDOS=0
faltando=""

while IFS=$'\t' read -r origem caminho; do
    [ -n "$caminho" ] || continue

    # db/import/ e conf/import/ nascem AUSENTES de proposito: sao as pastas
    # de sobrescrita do proprio rAthena, estao no .gitignore dele, e o
    # emulador tolera a falta sem reclamar. Reprovar por elas encheria a
    # varredura de falso positivo - e varredura que grita a toa e' varredura
    # que ninguem le'. Medido em 2026-08-15: eram 11 dos 11 "erros".
    case "$caminho" in
        db/import/*|conf/import/*|*/import/*) continue ;;
    esac

    CONFERIDOS=$((CONFERIDOS + 1))
    # O teste E' a existencia: no ext4, [ -f ] ja' diferencia caixa.
    [ -e "$EMULADOR/$caminho" ] || faltando+="        $caminho  (citado em $origem)"$'\n'
done < <(
    # import: conf/...
    grep -rhn "^[[:space:]]*import:[[:space:]]*" "$EMULADOR/conf" --include="*.conf" --include="*.txt" 2>/dev/null \
        | sed -E 's/^([0-9]+):[[:space:]]*import:[[:space:]]*//' \
        | awk -v o="conf/*.conf" '{print o"\t"$0}'
    # - Path: db/...
    grep -rh "^[[:space:]]*-[[:space:]]*Path:[[:space:]]*" "$EMULADOR/db" --include="*.yml" 2>/dev/null \
        | sed -E 's/^[[:space:]]*-[[:space:]]*Path:[[:space:]]*//' \
        | tr -d '"' \
        | awk -v o="db/*.yml" '{print o"\t"$0}'
    # npc: npc/...
    grep -rh "^[[:space:]]*npc:[[:space:]]*" "$EMULADOR/npc" --include="*.conf" 2>/dev/null \
        | sed -E 's/^[[:space:]]*npc:[[:space:]]*//' \
        | awk -v o="npc/*.conf" '{print o"\t"$0}'
)

if [ -n "$faltando" ]; then
    reprova "$(printf '%s' "$faltando" | grep -c .) caminho(s) citados que nao existem em disco:"
    printf '%s' "$faltando"
else
    aprova "$CONFERIDOS caminhos citados, todos existem com a caixa exata"
fi

# =====================================================================
passo "2. Fim de linha nos arquivos que o servidor analisa"
# =====================================================================
# So' os NOSSOS: o \r em arquivo do rAthena e' problema do rAthena, e
# reprovar o vendor inteiro deixaria a varredura inutil (ninguem olharia).
com_cr=""
while IFS= read -r f; do
    grep -qU $'\r' "$f" 2>/dev/null && com_cr+="        ${f#"$EMULADOR/"}"$'\n'
done < <(find "$EMULADOR/npc/guerra" "$EMULADOR/db/guerra" "$EMULADOR/conf/guerra" \
              -type f \( -name "*.txt" -o -name "*.yml" -o -name "*.conf" \) 2>/dev/null)

if [ -n "$com_cr" ]; then
    reprova "$(printf '%s' "$com_cr" | grep -c .) arquivo(s) com \\r - em nome de evento, o \\r entra no nome:"
    printf '%s' "$com_cr"
else
    aprova "nenhum \\r sobrando nos nossos arquivos"
fi

# =====================================================================
passo "3. U+FFFD (acento perdido para sempre)"
# =====================================================================
# Aqui a varredura e' AMPLA de proposito: um U+FFFD nao e' estilo, e' dano
# irreversivel, e nao ha' motivo para tolera-lo em arquivo nenhum que o
# jogo leia.
estragados=""
while IFS= read -r f; do
    grep -qU $'\xef\xbf\xbd' "$f" 2>/dev/null && estragados+="        ${f#"$EMULADOR/"}"$'\n'
done < <(find "$EMULADOR/npc/guerra" "$EMULADOR/db/guerra" "$EMULADOR/conf/guerra" \
              -type f 2>/dev/null)

if [ -n "$estragados" ]; then
    reprova "$(printf '%s' "$estragados" | grep -c .) arquivo(s) com U+FFFD - o byte original ja' se perdeu:"
    printf '%s' "$estragados"
else
    aprova "nenhum U+FFFD"
fi

# =====================================================================
printf '\n'
if [ "$FALHAS" -eq 0 ]; then
    printf '\033[1;32m    pre-voo aprovado\033[0m\n\n'
    exit 0
fi
printf '\033[1;31m    pre-voo REPROVADO em %d conferencia(s)\033[0m\n\n' "$FALHAS"
exit 1
