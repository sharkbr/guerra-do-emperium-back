#!/usr/bin/env bash
#
# fantasma.sh - liga, desliga e mostra o bot fantasma da Arena. Roda NO MAC.
#
#     ferramentas/fantasma.sh                  (status - e' o padrao)
#     ferramentas/fantasma.sh liga
#     ferramentas/fantasma.sh liga --mesmo-assim
#     ferramentas/fantasma.sh desliga
#     ferramentas/fantasma.sh reinicia
#     ferramentas/fantasma.sh log [-f]
#
# ---------------------------------------------------------------------
# POR QUE ESTE SCRIPT EXISTE
#
# Ate' 2026-09-03 ligar o fantasma era "ssh libraro 'systemctl enable
# --now guerra-fantasma'", escrito de cabeca. O comando funciona - e e'
# justamente esse o problema: ele sobe o servico sem olhar nada, e as tres
# coisas que fazem o bot NAO jogar nao estao no systemd, estao no banco e
# no cliente. Sem personagem ele trava calado na tela de selecao; sem os
# dois itens infinitos ele apanha sem lancar nada; com a senha de exemplo
# ele nem loga. Nos tres casos o systemctl diz "active" e o journal fica
# quase limpo - o sintoma aparece so' para quem estiver na arena.
#
# Entao este arquivo e' o "servidor.py status" do fantasma: um lugar so'
# que responde "esta' no ar?" e "da' para ligar?" antes de ligar.
#
# ---------------------------------------------------------------------
# A TRAVA QUE MOTIVOU O SCRIPT: DOIS OPENKORE AO MESMO TEMPO
#
# O openkore tambem se roda a mao (`perl openkore.pl`, e' assim que ele
# nasceu no Windows), e nada impede que um avulso tenha ficado para tras
# num terminal, numa sessao de teste ou num `systemctl start` de um
# servico que depois foi reescrito. Dois processos com a MESMA conta e o
# MESMO personagem entram numa briga que nao para: o segundo login chuta
# o primeiro, o `reconnect` do primeiro reconecta e chuta o segundo, e o
# par fica se derrubando enquanto o journal enche de reconexao. Do lado
# de fora parece "o bot pisca e some", e o rastro que fica no servidor de
# jogo e' um contador de login duplicado subindo (ARMADILHAS-RATHENA.md).
#
# Por isso `liga` e `reinicia` fazem, nesta ordem: param o servico, MATAM
# todo openkore.pl que sobrar, e so' entao sobem o novo. O `desliga`
# tambem mata os avulsos - "desligado" com um bot solto rodando seria a
# pior das mensagens.
#
# ---------------------------------------------------------------------
# O QUE ELE NAO FAZ
#
#   - nao INSTALA: isso e' o ferramentas/implanta_fantasma.sh (clona o
#     openkore, compila o XSTools, escreve a unit, cria a conta);
#   - nao ATUALIZA o plugin: isso viaja no ferramentas/implanta.sh, pela
#     secao 6b do atualiza_servidor.sh, que reaplica o delta E reinicia;
#   - nao toca em NENHUM dos quatro servicos do jogo. Ligar ou desligar o
#     fantasma nao derruba jogador nenhum, e por isso este comando nao
#     esbarra na regra do CLAUDE.md secao 4.20.
#
set -euo pipefail

SERVIDOR="${SERVIDOR:-libraro}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ACAO="${1:-status}"
FORCA=0
[ "${2:-}" = "--mesmo-assim" ] && FORCA=1
[ "${2:-}" = "-f" ] && FORCA=0

erro() { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

case "$ACAO" in
    status|liga|desliga|reinicia|log) ;;
    -h|--help|ajuda)
        sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
        exit 0 ;;
    *) erro "acao desconhecida: $ACAO
       use: status | liga | desliga | reinicia | log [-f]" ;;
esac

# O `log -f` e' o unico que quer terminal do outro lado: sem o -t o
# journalctl -f fica sem TTY e o Ctrl+C nao volta limpo.
if [ "$ACAO" = "log" ] && [ "${2:-}" = "-f" ]; then
    exec ssh -t "$SERVIDOR" "journalctl -u guerra-fantasma -f"
fi

# ---------------------------------------------------------------------
# Tudo o que segue roda NO SERVIDOR, numa sessao so'. Sao ~15 consultas
# entre systemd, banco e processos: uma por ssh seria meio minuto de
# espera para imprimir uma tela.
ssh "$SERVIDOR" 'bash -s' -- "$ACAO" "$FORCA" <<'REMOTO'
set -uo pipefail

ACAO="$1"
FORCA="${2:-0}"

UNIT="guerra-fantasma"
SEGREDO="/etc/guerra/fantasma.txt"
OPENKORE="/opt/openkore"
BANCO="guerra"
CONTA="fantasma"

# O Renegado transcendido: JOB_SHADOW_CHASER_T, 4079 (o enum comeca em
# JOB_RUNE_KNIGHT = 4054, src/common/mmo.hpp). O 4072 e' o nao-trans.
# Nao e' trava - e' so' para o status dizer "Renegado" em vez de "4079".
CLASSE_RENEGADO="4079 4072"

titulo() { printf '\n\033[1;34m%s\033[0m\n' "$*"; }
linha()  { printf '    %-14s %s\n' "$1" "$2"; }
ok()     { printf '    \033[32mok\033[0m   %s\n' "$*"; }
aviso()  { printf '    \033[33m!!\033[0m   %s\n' "$*"; }
falta()  { printf '    \033[1;31mXX\033[0m   %s\n' "$*"; }

consulta() { mysql -N -B "$BANCO" -e "$1" 2>/dev/null || true; }

# O `systemctl is-enabled` de uma unit desabilitada IMPRIME "disabled" e
# ainda sai 1 - entao um "|| echo desconhecida" na frente dele imprime as
# DUAS coisas, uma por linha. O mesmo vale para o is-active com o
# "inactive" (sai 3). Aqui o valor e' capturado e o padrao so' entra
# quando ele vem vazio, que e' o caso de unit inexistente.
esta_habilitada() { local v; v="$(systemctl is-enabled "$UNIT" 2>/dev/null)"; printf '%s' "${v:-desconhecida}"; }
esta_ativa()      { local v; v="$(systemctl is-active  "$UNIT" 2>/dev/null)"; printf '%s' "${v:-inactive}"; }

# ---------------------------------------------------------------------
# O mapa da arena vem do config.txt do proprio bot, e nao de uma constante
# aqui: quem decide onde ele joga e' o pvpGhost_map, e uma segunda copia
# do nome so' serviria para divergir (CLAUDE.md secao 4.11).
MAPA="$(sed -n 's/^pvpGhost_map[[:space:]]\+\([^[:space:]]*\).*/\1/p' \
        "$OPENKORE/control/config.txt" 2>/dev/null | tail -1)"
[ -n "$MAPA" ] || MAPA="pvp_n_1-5"

# O slot do personagem: o config.txt versionado traz "char 1", e o
# fantasma.txt da maquina pode sobrescrever - o !include e' a ultima
# linha do bloco de login, entao a ultima atribuicao vence.
slot_configurado() {
    local v=""
    for f in "$OPENKORE/control/config.txt" "$SEGREDO"; do
        [ -r "$f" ] || continue
        local achado
        achado="$(sed -n 's/^[[:space:]]*char[[:space:]]\+\([0-9]\+\).*/\1/p' "$f" | tail -1)"
        [ -n "$achado" ] && v="$achado"
    done
    printf '%s' "$v"
}

le_do_segredo() {
    sed -n "s/^[[:space:]]*$1[[:space:]]\+\(.*\)$/\1/p" "$SEGREDO" 2>/dev/null \
        | tail -1 | tr -d '\r'
}

# ---------------------------------------------------------------------
# Os processos. O openkore e' um perl so'; o do servico e' o MainPID, e
# qualquer outro openkore.pl vivo e' avulso - foi iniciado a mao e o
# systemd nao sabe dele.
main_pid() { systemctl show -p MainPID --value "$UNIT" 2>/dev/null || echo 0; }

pids_openkore() { pgrep -f 'openkore\.pl' 2>/dev/null || true; }

pids_avulsos() {
    local principal
    principal="$(main_pid)"
    local p
    for p in $(pids_openkore); do
        [ "$p" = "$principal" ] && continue
        printf '%s\n' "$p"
    done
}

mata_avulsos() {
    local restantes
    restantes="$(pids_avulsos)"
    [ -n "$restantes" ] || { printf '    \033[90m--\033[0m   nenhum openkore avulso\n'; return; }

    aviso "openkore fora do systemd (pid $(printf '%s' "$restantes" | tr '\n' ' ' | sed 's/ $//')) - derrubando"
    # shellcheck disable=SC2086
    kill $restantes 2>/dev/null || true

    # O openkore fecha a conexao e sai no SIGTERM, mas leva um instante
    # para soltar o socket. Vale esperar antes do -9: matar no meio do
    # logout deixa o personagem preso "online" no char-server ate' o
    # timeout dele.
    local i
    for i in 1 2 3 4 5 6 7 8 9 10; do
        [ -n "$(pids_avulsos)" ] || break
        sleep 1
    done

    restantes="$(pids_avulsos)"
    if [ -n "$restantes" ]; then
        # shellcheck disable=SC2086
        kill -9 $restantes 2>/dev/null || true
        sleep 1
        aviso "precisou de -9 em: $(printf '%s' "$restantes" | tr '\n' ' ' | sed 's/ $//')"
    fi
    ok "so' sobra o servico"
}

# ---------------------------------------------------------------------
# O RETRATO - e' o "status", e tambem o pre-voo do "liga".
#
# BLOQUEIOS guarda o que impede o bot de JOGAR (nao de subir: o systemd
# sobe feliz em todos esses casos, e e' esse o ponto).
BLOQUEIOS=""
bloqueia() { BLOQUEIOS="$BLOQUEIOS$1
"; falta "$1"; }

retrato() {
    titulo "== Bot fantasma em $(hostname) =="

    if ! systemctl cat "$UNIT" >/dev/null 2>&1; then
        bloqueia "a unit $UNIT nao existe neste servidor"
        printf '\n         Instale primeiro, do Mac:  ferramentas/implanta_fantasma.sh\n'
        return
    fi

    linha "unit" "$(esta_habilitada) / $(esta_ativa)"

    local principal avulsos
    principal="$(main_pid)"
    if [ "$principal" != "0" ] && [ -n "$principal" ]; then
        linha "processo" "pid $principal (do servico)"
    else
        linha "processo" "nenhum pelo servico"
    fi
    avulsos="$(pids_avulsos | tr '\n' ' ')"
    [ -n "${avulsos// /}" ] && aviso "openkore AVULSO rodando fora do systemd: $avulsos"

    local jogo
    jogo="$(systemctl is-active guerra-map 2>/dev/null)"
    linha "map-server" "${jogo:-inactive}"
    [ "$jogo" = "active" ] || aviso "o map-server esta' fora - o bot sobe e fica reconectando"

    # a senha
    local senha
    senha="$(le_do_segredo password)"
    if [ ! -r "$SEGREDO" ]; then
        bloqueia "$SEGREDO nao existe - o bot nao consegue logar"
    elif [ -z "$senha" ] || [ "$senha" = "TROQUE-ME" ]; then
        bloqueia "a senha em $SEGREDO ainda e' a de exemplo"
    else
        linha "senha" "definida em $SEGREDO"
    fi

    # a conta
    local id_conta
    id_conta="$(consulta "SELECT account_id FROM login WHERE userid='$CONTA' LIMIT 1")"
    if [ -z "$id_conta" ]; then
        bloqueia "a conta '$CONTA' nao existe no banco - rode o implanta_fantasma.sh"
        return
    fi
    linha "conta" "$CONTA (account_id $id_conta, group_id $(consulta "SELECT group_id FROM login WHERE userid='$CONTA'"))"

    # o personagem - a peca que nao se cria por SQL, e a que costuma faltar
    local chars
    chars="$(consulta "SELECT COUNT(*) FROM \`char\` WHERE account_id=$id_conta")"
    if [ "${chars:-0}" = "0" ]; then
        bloqueia "a conta nao tem personagem - o bot trava na tela de selecao, calado"
        printf '         Crie um RENEGADO no cliente apontado para PRODUCAO\n'
        printf '         (ferramentas/aponta_cliente.py --producao) - IMPLANTACAO.md secao 7.\n'
        return
    fi

    local slot linha_char
    slot="$(slot_configurado)"
    linha_char="$(consulta "SELECT CONCAT(char_num,'|',name,'|',class,'|',base_level) FROM \`char\` WHERE account_id=$id_conta ORDER BY char_num LIMIT 1")"
    local n_slot nome classe nivel
    n_slot="${linha_char%%|*}"; linha_char="${linha_char#*|}"
    nome="${linha_char%%|*}";   linha_char="${linha_char#*|}"
    classe="${linha_char%%|*}"; nivel="${linha_char##*|}"

    local rotulo="classe $classe"
    case " $CLASSE_RENEGADO " in *" $classe "*) rotulo="Renegado ($classe)" ;; esac
    linha "personagem" "slot $n_slot: $nome - $rotulo, nivel $nivel"

    if [ -n "$slot" ] && [ "$slot" != "$n_slot" ]; then
        aviso "o config diz 'char $slot' e o personagem esta' no slot $n_slot"
        aviso "ponha 'char $n_slot' em $SEGREDO (nao no config.txt, que e' versionado)"
    fi

    # os dois insumos infinitos: sem eles o ciclo vira pancada normal
    local id_char tinta pincel
    id_char="$(consulta "SELECT char_id FROM \`char\` WHERE account_id=$id_conta ORDER BY char_num LIMIT 1")"
    tinta="$(consulta "SELECT COUNT(*) FROM inventory WHERE char_id=$id_char AND nameid=30993")"
    pincel="$(consulta "SELECT COUNT(*) FROM inventory WHERE char_id=$id_char AND nameid=30992")"
    if [ "${tinta:-0}" != "0" ] && [ "${pincel:-0}" != "0" ]; then
        linha "itens" "Tinta Infinita (30993) e Pincel do Infinito (30992) na mochila"
    else
        [ "${tinta:-0}"  = "0" ] && aviso "falta a Tinta para Parede Infinita (30993): #item $nome 30993 1"
        [ "${pincel:-0}" = "0" ] && aviso "falta o Pincel do Infinito (30992): #item $nome 30992 1"
        aviso "sem os dois as habilidades do ciclo nao saem - o bot vira pancada normal"
    fi

    # a arena. O last_map do banco e' o da ultima gravacao (autosave_time
    # 60 no char_athena.conf), entao isto e' uma foto de ate' um minuto
    # atras - serve de aviso, nao de prova.
    local na_arena
    na_arena="$(consulta "SELECT COUNT(*) FROM \`char\` WHERE online=1 AND last_map='$MAPA' AND account_id<>$id_conta")"
    if [ "${na_arena:-0}" = "0" ]; then
        linha "arena" "$MAPA vazia (pela ultima gravacao, ate' 60s atras)"
    else
        aviso "ha $na_arena jogador(es) em $MAPA agora - o dono pede a arena vazia para ligar"
    fi
}

# ---------------------------------------------------------------------
case "$ACAO" in

status)
    retrato
    if [ -n "$BLOQUEIOS" ]; then
        printf '\n\033[1;31mNao esta pronto para ligar.\033[0m\n'
    elif [ "$(esta_ativa)" = "active" ]; then
        printf '\n\033[1;32mNo ar.\033[0m  log:  ferramentas/fantasma.sh log -f\n'
    else
        printf '\n\033[1;32mPronto para ligar:\033[0m  ferramentas/fantasma.sh liga\n'
    fi
    ;;

liga|reinicia)
    retrato
    if [ -n "$BLOQUEIOS" ]; then
        if [ "$FORCA" = "1" ] && systemctl cat "$UNIT" >/dev/null 2>&1; then
            printf '\n\033[33mSeguindo mesmo assim, a seu pedido.\033[0m\n'
        else
            printf '\n\033[1;31mNAO liguei.\033[0m O bot subiria e nao jogaria:\n'
            printf '%s' "$BLOQUEIOS" | sed '/^$/d;s/^/    - /'
            printf '\n    Para ligar assim mesmo:  ferramentas/fantasma.sh liga --mesmo-assim\n\n'
            exit 1
        fi
    fi

    titulo "== Deixando um so' openkore de pe' =="
    # Parar ANTES de matar os avulsos: se o servico estiver de pe', o
    # MainPID e' o unico que nao pode morrer aqui - e depois do stop nao
    # ha mais essa distincao para errar.
    systemctl stop "$UNIT" 2>/dev/null || true
    mata_avulsos

    titulo "== Ligando =="
    # enable --now, e nao start: o bot tem de voltar sozinho se a maquina
    # reiniciar. Desligar de verdade e' o "desliga", que faz o disable.
    systemctl enable --now "$UNIT"
    sleep 8

    printf '    servico:  %s\n' "$(esta_ativa)"
    titulo "== Ultimas linhas do journal =="
    journalctl -u "$UNIT" -n 20 --no-pager --output=cat || true
    printf '\n    acompanhe com:  ferramentas/fantasma.sh log -f\n'
    ;;

desliga)
    titulo "== Desligando o fantasma =="
    systemctl disable --now "$UNIT" 2>/dev/null || true
    # O disable so' alcanca o que o systemd conhece. Um openkore avulso
    # continuaria jogando com "desligado" na tela de quem rodou isto.
    mata_avulsos
    printf '\n    unit:  %s / %s\n' "$(esta_habilitada)" "$(esta_ativa)"
    printf '    nenhum JOGADOR foi derrubado - isto nao encosta nos quatro do jogo.\n'
    ;;

log)
    journalctl -u "$UNIT" -n 60 --no-pager || true
    ;;
esac
REMOTO
