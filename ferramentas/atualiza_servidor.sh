#!/usr/bin/env bash
#
# atualiza_servidor.sh - traz o repositorio, compila o que mudou e (quando
# as units existirem) reinicia os quatro servidores na ordem certa.
#
# Etapa 12 do IMPLANTACAO.md. Roda NA MAQUINA ALVO, como root. O wrapper
# fino que se chama do Mac e' o ferramentas/implanta.sh - a logica mora
# aqui, versionada, porque o script tem de vir do proprio repositorio.
#
# COMO RODAR (do Mac):
#
#     ssh libraro 'bash -s' < ferramentas/atualiza_servidor.sh
#
# ou, depois do primeiro clone, direto no servidor:
#
#     /opt/guerra-do-emperium/ferramentas/atualiza_servidor.sh
#
# ---------------------------------------------------------------------
# POR QUE root NAO PODE SIMPLESMENTE DAR git pull AQUI
#
# O repositorio pertence ao 'ragnarok', que roda o jogo sem privilegio
# nenhum (ver provisiona.sh). Se o root operar o git direto:
#
#   1. os arquivos novos nascem root:root, e o servidor - que roda como
#      ragnarok - perde a escrita em log/, save/ e no que mais precisar;
#   2. o git moderno recusa com "detected dubious ownership in repository",
#      que e' uma protecao dele contra exatamente esta situacao.
#
# Entao TUDO que e' do jogo passa por 'runuser -u ragnarok', e so' o que
# e' de maquina (systemctl) fica como root. A funcao 'como_jogo' abaixo
# existe para essa linha nao ser esquecida em nenhum lugar.
#
# ---------------------------------------------------------------------
# COMPILA SO' QUANDO PRECISA
#
# Requisito da Etapa 12: mudanca que e' so' de db/ ou de script de NPC nao
# justifica recompilar (nem, mais tarde, reiniciar - um deploy que sempre
# reinicia o map-server derruba todo mundo por causa de um preco de loja).
# A decisao e' por diff entre o commit que estava e o que chegou, olhando
# so' o que entra no binario: src/, configure e Makefile.in.
#
set -euo pipefail

USUARIO="ragnarok"
RAIZ="/opt/guerra-do-emperium"
REPO="https://github.com/sharkbr/guerra-do-emperium-back.git"
RAMO="main"
EMULADOR="$RAIZ/rathena"

# Os quatro binarios do alvo 'server' do Makefile. A ordem e' a mesma que o
# ferramentas/servidor.py ja' conhece: login -> char -> web -> map.
BINARIOS=(login-server char-server web-server map-server)

passo()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()     { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()   { printf '    \033[90m--\033[0m   %s\n' "$*"; }
aviso()  { printf '    \033[33m!!\033[0m   %s\n' "$*"; }
erro()   { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "precisa rodar como root"
id "$USUARIO" >/dev/null 2>&1 || erro "usuario $USUARIO nao existe - rode o provisiona.sh antes"

# Toda operacao de jogo passa por aqui. Ver o cabecalho.
como_jogo() { runuser -u "$USUARIO" -- "$@"; }

# =====================================================================
# 1. Codigo
# =====================================================================
passo "Repositorio"
if [ -d "$RAIZ/.git" ]; then
    ANTES="$(como_jogo git -C "$RAIZ" rev-parse HEAD)"
    como_jogo git -C "$RAIZ" fetch --quiet origin "$RAMO"
    como_jogo git -C "$RAIZ" reset --hard --quiet "origin/$RAMO"
    DEPOIS="$(como_jogo git -C "$RAIZ" rev-parse HEAD)"

    if [ "$ANTES" = "$DEPOIS" ]; then
        pula "ja' estava em $(echo "$DEPOIS" | cut -c1-8) - nada novo"
    else
        ok "$(echo "$ANTES" | cut -c1-8) -> $(echo "$DEPOIS" | cut -c1-8)"
        como_jogo git -C "$RAIZ" log --oneline "$ANTES..$DEPOIS" | sed 's/^/         /'
    fi
else
    # O diretorio ja' existe e pertence ao ragnarok (provisiona.sh), entao
    # o clone e' feito DENTRO dele, e nao criando-o.
    ANTES=""
    como_jogo git clone --quiet --branch "$RAMO" "$REPO" "$RAIZ"
    DEPOIS="$(como_jogo git -C "$RAIZ" rev-parse HEAD)"
    ok "clonado em $DEPOIS"
fi

[ -d "$EMULADOR" ] || erro "$EMULADOR nao existe - o clone veio incompleto?"

# =====================================================================
# 2. Precisa compilar?
# =====================================================================
passo "Decidindo se compila"
COMPILAR=0
FALTANDO=()
for b in "${BINARIOS[@]}"; do
    [ -x "$EMULADOR/$b" ] || FALTANDO+=("$b")
done

if [ ${#FALTANDO[@]} -gt 0 ]; then
    COMPILAR=1
    ok "faltam binarios: ${FALTANDO[*]}"
elif [ -z "$ANTES" ]; then
    COMPILAR=1
    ok "primeiro clone"
elif ! como_jogo git -C "$RAIZ" diff --quiet "$ANTES" "$DEPOIS" -- \
        rathena/src rathena/configure rathena/Makefile.in 2>/dev/null; then
    COMPILAR=1
    ok "src/ mudou entre os dois commits"
else
    pula "nada que entre no binario mudou - build dispensado"
fi

# =====================================================================
# 3. Compilar
# =====================================================================
if [ "$COMPILAR" = "1" ]; then
    passo "Compilando"

    if [ ! -f "$EMULADOR/Makefile" ] || \
       [ "$EMULADOR/configure" -nt "$EMULADOR/Makefile" ]; then
        # 'sh configure', e nao './configure': o vendor do rAthena foi feito
        # no Windows, onde o git nao registra o bit de execucao, entao o
        # arquivo esta' no repositorio como 100644 e no Linux ele chega sem
        # permissao de rodar. O erro que sai e' "Permission denied", que
        # parece problema de dono ou do runuser e nao e'. Chamar o
        # interpretador direto resolve sem tocar em arquivo de terceiro e sem
        # um chmod que o proximo 'git reset --hard' desfaria.
        ok "rodando sh configure"
        ( cd "$EMULADOR" && como_jogo sh configure ) > /tmp/configure.log 2>&1 \
            || { tail -30 /tmp/configure.log; erro "configure falhou (log em /tmp/configure.log)"; }
        ok "configure ok"
    else
        pula "Makefile ja' existe"
    fi

    # -j1 de proposito: 1 vCPU e 961 MB de RAM. Paralelismo aqui nao
    # ganharia tempo (nao ha' outro nucleo) e multiplicaria o pico de
    # memoria do g++, que ja' e' o aperto desta maquina - ver a Etapa 3.
    ok "make server -j1 (demora; o log completo vai para /tmp/build.log)"
    INICIO=$SECONDS
    if ! ( cd "$EMULADOR" && como_jogo make server -j1 ) > /tmp/build.log 2>&1; then
        echo
        aviso "ultimas 40 linhas do log:"
        tail -40 /tmp/build.log
        erro "compilacao falhou - log completo em /tmp/build.log"
    fi
    ok "compilado em $(( (SECONDS - INICIO) / 60 ))min $(( (SECONDS - INICIO) % 60 ))s"

    for b in "${BINARIOS[@]}"; do
        [ -x "$EMULADOR/$b" ] || erro "make terminou mas $b nao existe"
    done
    ok "os quatro binarios existem"

    # O que o GCC reclamou. Nao aborta - o rAthena compila com muitos
    # avisos proprios -, mas fica visivel: aviso em src/custom/ e' NOSSO,
    # e e' exatamente o que a Etapa 5 manda vigiar.
    NOSSOS="$(grep -c "src/custom/" /tmp/build.log || true)"
    if [ "$NOSSOS" -gt 0 ]; then
        aviso "$NOSSOS linha(s) do GCC mencionam src/custom/ - conferir:"
        grep "src/custom/" /tmp/build.log | head -20 | sed 's/^/         /'
    else
        ok "nenhum aviso do GCC em src/custom/"
    fi
fi

# =====================================================================
# 4. Reiniciar
# =====================================================================
passo "Servicos"
# As units sao a Etapa 9 e ainda nao existem. Enquanto nao existirem, este
# passo avisa em vez de fingir que reiniciou - silencio aqui viraria
# "o deploy passou e o servidor continua com o binario velho".
if systemctl list-unit-files 'guerra-*.service' --no-legend 2>/dev/null | grep -q .; then
    for s in guerra-login guerra-char guerra-web guerra-map; do
        systemctl restart "$s"
        ok "$s reiniciado"
    done
else
    aviso "units guerra-*.service ainda nao existem (Etapa 9) - nada reiniciado"
fi

passo "Pronto"
echo "    commit:  $(como_jogo git -C "$RAIZ" log -1 --format='%h %s')"
echo "    binario: $(date -r "$EMULADOR/map-server" '+%Y-%m-%d %H:%M' 2>/dev/null || echo 'nao compilado')"
