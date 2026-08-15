#!/usr/bin/env bash
#
# backup.sh - Etapa 10 do IMPLANTACAO.md.
#
#     backup.sh hora|dia|semana
#
# Roda NA MAQUINA, chamado por temporizador do systemd. O instalador dos
# temporizadores e' o ferramentas/configura_backup.sh.
#
# ---------------------------------------------------------------------
# O QUE E' SALVO, E POR QUE EM DOIS PACOTES SEPARADOS
#
# jogo  - o que o jogador perde se sumir: conta, personagem, inventario,
#         armazem, carrinho, cla, variaveis dos nossos NPCs, o placar da
#         Honra de Combate. Pequeno: para ~20 jogadores, poucos MB.
# logs  - as dez tabelas de logs.sql (picklog, zenylog, chatlog...). NAO
#         sao estado do jogo: se sumirem, ninguem perde item. Mas crescem
#         MUITO mais rapido - a picklog grava uma linha por item que troca
#         de mao, e num servidor de drop 50x isso e' dezenas de milhares
#         de linhas por dia.
#
# Separar deixa a rotina do jogo pequena o bastante para ser HORARIA e para
# guardar meses de historico de graca. E a picklog, apesar de grande, e' o
# que salva no desastre mais comum de servidor de RO: duplicacao de item.
# Nesse caso restaurar o banco inteiro pune quem nao teve culpa - o conserto
# certo e' cirurgico, lendo a log e desfazendo so' o que aconteceu.
#
# ---------------------------------------------------------------------
# --default-character-set=latin1 NAO E' OPCIONAL
#
# As 105 colunas de texto do rAthena sao latin1. Sem esse parametro o
# mysqldump conversa em utf8mb4 e os acentos morrem no dump - viram U+FFFD,
# que e' IRREVERSIVEL: o byte original ja' nao esta' la'. E o estrago so'
# aparece no dia da restauracao. Ver CLAUDE.md secao 5.
#
# ---------------------------------------------------------------------
# O ALERTA MAIS IMPORTANTE E' O DE AUSENCIA, E ELE NAO MORA AQUI
#
# Este script avisa quando falha e quando o tamanho estoura. Mas um alerta
# que mora na maquina NAO consegue avisar que a maquina parou: se o cron
# morrer, ou o droplet desligar, ninguem dispara nada - e o silencio e'
# identico a "esta' tudo bem".
#
# Por isso ele manda um PULSO a cada execucao bem-sucedida. Quem alerta e'
# o servico do outro lado, ao deixar de receber. Configure la': "se nao
# chegar pulso em 3 horas, me avise".
#
set -euo pipefail

QUANDO="${1:-}"
case "$QUANDO" in
    hora|dia|semana) ;;
    *) echo "uso: $0 hora|dia|semana" >&2; exit 2 ;;
esac

DESTINO="/var/backups/guerra"
BANCO="guerra"
AMBIENTE="/etc/guerra/backup.env"

# Quantas copias guardar de cada ritmo. Sao megabytes: ser generoso aqui
# nao custa nada e cobre o caso que o dono levantou - perceber o problema
# so' no segundo dia, quando o backup de ontem ja' esta' ruim.
GUARDA_hora=48      # dois dias, hora a hora
GUARDA_dia=30       # um mes
GUARDA_semana=12    # tres meses

# Teto de tamanho para avisar. Cruzar isto nao e' urgencia - e' sinal de
# crescimento fora do previsto.
TETO_MB="${TETO_MB:-500}"

[ -f "$AMBIENTE" ] && . "$AMBIENTE"
ALERTA_URL="${ALERTA_URL:-}"
PULSO_URL="${PULSO_URL:-}"

# As dez tabelas de logs.sql. Ficam fora do pacote do jogo e ganham o seu.
TABELAS_LOG=(atcommandlog branchlog cashlog chatlog feedinglog
             loginlog mvplog npclog picklog zenylog)

avisa() {  # avisa <evento> <mensagem>
    local evento="$1" msg="$2"
    logger -t guerra-backup "$evento: $msg"
    [ -n "$ALERTA_URL" ] || return 0
    curl -sS -m 15 -X POST "$ALERTA_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"servidor\":\"$(hostname)\",\"evento\":\"$evento\",\"mensagem\":\"$msg\"}" \
        >/dev/null 2>&1 || true
}

# Qualquer morte do script vira alerta - inclusive as que nao previmos.
trap 'avisa falhou "o backup ($QUANDO) morreu na linha $LINENO"' ERR

carimbo="$(date +%Y-%m-%d_%H%M)"
pasta="$DESTINO/$QUANDO"
mkdir -p "$pasta"

# --lock-tables e nao --single-transaction: a `login` e quase tudo do
# rAthena e' MyISAM, que nao tem transacao - o --single-transaction daria
# um dump inconsistente sem reclamar de nada. O lock dura o tempo do dump,
# que neste tamanho e' segundos.
comum=(--default-character-set=latin1 --lock-tables --routines --triggers)

# ---- pacote do jogo (sem as logs)
ignora=()
for t in "${TABELAS_LOG[@]}"; do ignora+=(--ignore-table="$BANCO.$t"); done
jogo="$pasta/jogo_$carimbo.sql.gz"
mysqldump "${comum[@]}" "${ignora[@]}" "$BANCO" | gzip -9 > "$jogo"

# ---- pacote das logs
logs="$pasta/logs_$carimbo.sql.gz"
mysqldump "${comum[@]}" "$BANCO" "${TABELAS_LOG[@]}" | gzip -9 > "$logs"

# Dump vazio ou truncado tem tamanho ridiculo. E' a conferencia que separa
# "o backup rodou" de "o backup serve" - sem ela, um banco fora do ar
# produziria um .gz de 20 bytes todo dia, sem erro nenhum.
for f in "$jogo" "$logs"; do
    tam=$(stat -c%s "$f")
    if [ "$tam" -lt 1024 ]; then
        avisa falhou "$(basename "$f") saiu com $tam bytes - dump vazio?"
        exit 1
    fi
    # gzip -t le' o arquivo inteiro e prova que ele descomprime.
    gzip -t "$f" || { avisa falhou "$(basename "$f") esta' corrompido"; exit 1; }
done

# ---- poda
guarda_var="GUARDA_$QUANDO"
guarda="${!guarda_var}"
for prefixo in jogo logs; do
    # shellcheck disable=SC2012
    ls -1t "$pasta/${prefixo}_"*.sql.gz 2>/dev/null | tail -n +$((guarda + 1)) \
        | xargs -r rm -f
done

# ---- alertas de tamanho
total_mb=$(du -sm "$DESTINO" | cut -f1)
if [ "$total_mb" -gt "$TETO_MB" ]; then
    avisa tamanho "os backups somam ${total_mb} MB, acima do teto de ${TETO_MB} MB"
fi

livre_pct=$(df --output=pcent / | tail -1 | tr -dc '0-9')
if [ "$livre_pct" -gt 85 ]; then
    avisa disco "o disco esta' ${livre_pct}% cheio"
fi

# ---- pulso (ver o cabecalho: e' o alerta de ausencia)
if [ -n "$PULSO_URL" ]; then
    curl -sS -m 15 -X POST "$PULSO_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"servidor\":\"$(hostname)\",\"evento\":\"ok\",\"ritmo\":\"$QUANDO\",\"jogo_bytes\":$(stat -c%s "$jogo"),\"logs_bytes\":$(stat -c%s "$logs")}" \
        >/dev/null 2>&1 || true
fi

logger -t guerra-backup "ok ($QUANDO): jogo $(du -h "$jogo" | cut -f1), logs $(du -h "$logs" | cut -f1), total ${total_mb} MB"
