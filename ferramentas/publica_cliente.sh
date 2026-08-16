#!/usr/bin/env bash
#
# publica_cliente.sh - poe a BASE do cliente no ar, para o primeiro download.
#
#     ferramentas/publica_cliente.sh            # sobe o que falta
#     ferramentas/publica_cliente.sh --confere  # so mostra o placar
#     ferramentas/publica_cliente.sh --tudo     # reenvia tudo, inclusive o que ja esta la
#
# E' o irmao do `publica_patch.sh`, e as diferencas sao duas: o destino e' o
# bucket da DigitalOcean (nao o droplet) e o insumo e' o `patcher/base.txt`
# (nao o `patches.txt`). O motivo do bucket esta no HISTORICO: 3,4 GB por
# instalacao sairiam pela mesma placa de rede que serve o map-server.
#
# RODA NO WINDOWS (Git Bash): os pedacos nascem de C:\GuerraDoEmperium\, que
# so' existe aqui.
#
# ---------------------------------------------------------------------
# A ORDEM IMPORTA, E E' A UNICA COISA DELICADA AQUI
#
# Os pedacos sobem ANTES da base.txt - a mesma regra do publicador de patch, e
# pelo mesmo motivo. Se a lista subisse primeiro, todo instalador aberto
# naquele intervalo pediria um arquivo que ainda nao existe, e o jogador veria
# um erro por nada. Na ordem certa, o pior caso e' um pedaco parado no bucket
# que ninguem pediu ainda.
#
# ---------------------------------------------------------------------
# O QUE NAO E' COPIADO
#
# O `data.grf` (2,95 GB) e' publicado direto de C:\GuerraDoEmperium\cliente\ -
# ele nao tem copia em `instalador\`, porque copiar 3 GB para depois subir
# seria meia hora de disco a toa. Por isso as duas origens abaixo, e por isso
# o tipo de cada linha decide de onde o arquivo sai.
#
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRO="$RAIZ/patcher/base.txt"
PEDACOS="${PEDACOS:-/c/GuerraDoEmperium/instalador}"
CLIENTE="${CLIENTE:-/c/GuerraDoEmperium/cliente}"
SEGREDO="${SEGREDO:-/c/GuerraDoEmperium/spaces.env}"
RCLONE="${RCLONE:-/c/GuerraDoEmperium/bin/rclone.exe}"

azul() { printf '\n\033[1;34m%s\033[0m\n' "$*"; }
erro() { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ -f "$REGISTRO" ] || erro "nao achei $REGISTRO - rode ferramentas/monta_cliente.py primeiro"
[ -x "$RCLONE" ]   || erro "nao achei o rclone em $RCLONE"
[ -f "$SEGREDO" ]  || erro "nao achei $SEGREDO - e' onde moram a chave e o segredo do bucket"

# O arquivo de segredo tem comentario e linhas VAR=valor. O `set -a` faz cada
# atribuicao virar variavel de ambiente sem precisar exportar uma a uma.
set -a
# shellcheck disable=SC1090
. "$SEGREDO"
set +a

for v in SPACES_KEY SPACES_SECRET SPACES_BUCKET SPACES_REGIAO SPACES_CDN; do
    [ -n "${!v:-}" ] || erro "$v esta vazio em $SEGREDO"
done

# O rclone e' configurado por AMBIENTE e nao por rclone.conf, de proposito: um
# rclone.conf guardaria a chave secreta num segundo arquivo, em outro lugar,
# fora do alcance do .gitignore e da nossa atencao. Assim o segredo vive num
# lugar so' - o spaces.env - e some quando o processo morre.
# Sem arquivo de configuracao nenhum. Sem isto o rclone imprime um NOTICE
# dizendo que nao achou o rclone.conf - que e' inofensivo, mas cai no meio da
# listagem do bucket e se parece com conteudo dele.
export RCLONE_CONFIG=""

export RCLONE_CONFIG_SPACES_TYPE=s3
export RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean
export RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY"
export RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET"
export RCLONE_CONFIG_SPACES_ENDPOINT="$SPACES_REGIAO.digitaloceanspaces.com"

# `public-read` por objeto e' o que faz o instalador conseguir baixar sem
# credencial nenhuma. O BUCKET continua fechado para listagem (responde 403 na
# raiz), que e' a combinacao certa: qualquer um baixa o que sabe o nome,
# ninguem varre o conteudo.
export RCLONE_CONFIG_SPACES_ACL=public-read

# NAO tentar criar o bucket antes de subir.
#
# O rclone, ao usar copia multi-thread (que e' o que ele faz em arquivo grande,
# e o data.grf tem 2,95 GB), chama CreateBucket para garantir que o destino
# existe. A chave do Spaces tem acesso ao CONTEUDO do bucket mas nao permissao
# de CRIAR bucket - entao a chamada volta 403 e o upload morre antes de comecar,
# com uma mensagem que fala de `CreateBucket` e manda procurar defeito na chave.
# A chave esta certa; a verificacao e' que e' desnecessaria, porque o bucket ja
# existe. Medido em 2026-08-16, no primeiro upload.
export RCLONE_CONFIG_SPACES_NO_CHECK_BUCKET=true

REMOTO="spaces:$SPACES_BUCKET"

# As linhas do registro que valem: seis campos separados por TAB.
linhas() { grep -v '^[[:space:]]*#' "$REGISTRO" | grep -v '^[[:space:]]*$'; }

# De onde sai cada pedaco. E' a unica diferenca de tratamento entre os dois
# tipos, e ela existe so' aqui - no bucket os dois viram objeto igual.
origem() {
    local tipo="$1" arquivo="$2"
    if [ "$tipo" = "bruto" ]; then
        echo "$CLIENTE/$arquivo"
    else
        echo "$PEDACOS/$arquivo"
    fi
}

# Lista o bucket, e MORRE se nao conseguir - em vez de devolver vazio.
#
# Isto ja custou uma rodada em 2026-08-16: a primeira versao era
# `lsf "$REMOTO" 2>/dev/null || true`, e com uma chave invalida ela imprimia
# "(vazio)" com toda a calma. "O bucket esta vazio" e "eu nao consigo falar com
# o bucket" sao respostas identicas na tela e opostas no significado - e a
# segunda, tratada como a primeira, faria o publicador tentar subir 3,4 GB para
# so' entao falhar no primeiro pedaco.
#
# O erro do rclone vai para a tela de proposito: `InvalidAccessKeyId` e
# `SignatureDoesNotMatch` dizem qual dos dois campos do spaces.env esta errado,
# e essa distincao vale mais que uma mensagem nossa mais bonita.
remotos() {
    local saida
    if ! saida="$("$RCLONE" lsf "$REMOTO" 2>&1)"; then
        printf '%s\n' "$saida" >&2
        erro "nao consegui listar $REMOTO - confira SPACES_KEY e SPACES_SECRET em $SEGREDO"
    fi
    printf '%s' "$saida"
}

publica() {
    local tudo="${1:-}"

    azul "== O que o bucket ja tem =="
    local ja; ja="$(remotos)"
    if [ -z "$ja" ]; then
        echo "     (vazio)"
    else
        echo "$ja" | sed 's/^/     /'
    fi

    local enviados=0 pulados=0
    while IFS=$'\t' read -r numero arquivo sha bytes tipo nome; do
        local local_arq; local_arq="$(origem "$tipo" "$arquivo")"
        [ -f "$local_arq" ] || erro "o registro pede $arquivo, que nao esta em $(dirname "$local_arq")"

        if [ -z "$tudo" ] && echo "$ja" | grep -qx "$arquivo"; then
            printf '  %s  %-28s (ja esta la)\n' "$numero" "$nome"
            pulados=$((pulados + 1))
            continue
        fi

        # Confere o sha ANTES de enviar. O registro e' versionado e os pedacos
        # nao: um pedaco remontado com o mesmo nome e conteudo diferente e' o
        # jeito silencioso de o instalador do jogador recusar tudo depois - ele
        # confere o sha256 e para. Melhor descobrir aqui.
        #
        # No data.grf isso le 2,95 GB e leva algumas dezenas de segundos. Vale:
        # e' a unica coisa que separa "o registro esta certo" de "o registro
        # descreve o que vai subir".
        printf '  %s  %-28s conferindo sha256...\n' "$numero" "$nome"
        local aqui; aqui="$(sha256sum "$local_arq" | cut -d' ' -f1)"
        [ "$aqui" = "$sha" ] || erro "$arquivo nao confere com o registro (sha256) - remonte a base"

        azul "-> $numero  $nome  ($((bytes / 1048576)) MB)"
        # `copyto` e nao `copy`: o nome no bucket e' o do registro, e nao o do
        # arquivo em disco. Sao iguais hoje, e amarrar os dois seria criar uma
        # divergencia possivel de graca.
        # `--stats` e nao `--progress`: o progresso continuo reescreve a linha
        # dezenas de vezes por segundo, o que e' bom num terminal e vira
        # megabytes de lixo quando a saida e' um arquivo de log.
        "$RCLONE" copyto "$local_arq" "$REMOTO/$arquivo" \
            --s3-acl public-read --stats 15s --stats-one-line
        enviados=$((enviados + 1))
    done < <(linhas)

    azul "== A base.txt, por ultimo =="
    "$RCLONE" copyto "$REGISTRO" "$REMOTO/base.txt" --s3-acl public-read

    printf '\n\033[1;32m%d pedaco(s) enviado(s), %d ja estavam la; a base esta no ar.\033[0m\n' \
        "$enviados" "$pulados"
    printf 'Endereco do instalador: %s/base.txt\n' "$SPACES_CDN"
}

confere() {
    azul "== Registro (local) =="
    local total=0
    while IFS=$'\t' read -r numero arquivo sha bytes tipo nome; do
        local local_arq; local_arq="$(origem "$tipo" "$arquivo")"
        local marca="AUSENTE"
        [ -f "$local_arq" ] && marca="ok"
        total=$((total + bytes))
        printf '  %s  %-32s %7s MB  %-5s  %s\n' \
            "$numero" "${arquivo:0:32}" "$((bytes / 1048576))" "$tipo" "$marca"
    done < <(linhas)
    printf '     %s\n' "-------------------------------------------------"
    printf '     o jogador baixa %s MB\n' "$((total / 1048576))"

    azul "== Bucket ($REMOTO) =="
    local ja; ja="$(remotos)"
    if [ -z "$ja" ]; then echo "     (vazio)"; else echo "$ja" | sed 's/^/     /'; fi

    # A prova que importa nao e' o arquivo existir no bucket, e sim o CDN
    # entrega-lo: sao dois caminhos diferentes, e o subdominio proprio depende
    # de DNS e certificado que nada mais aqui verifica.
    azul "== O CDN responde? =="
    local code
    code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 -I "$SPACES_CDN/base.txt" 2>&1)" \
        || { echo "     $SPACES_CDN nao respondeu"; return 0; }
    echo "     $SPACES_CDN/base.txt -> HTTP $code"
}

case "${1:-}" in
    --confere) confere ;;
    --tudo)    publica tudo ;;
    "")        publica ;;
    *)         erro "opcao desconhecida: $1" ;;
esac
