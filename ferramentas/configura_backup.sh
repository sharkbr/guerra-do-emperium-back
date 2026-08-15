#!/usr/bin/env bash
#
# configura_backup.sh - instala os temporizadores do backup (Etapa 10).
#
#     ssh libraro 'bash -s' < ferramentas/configura_backup.sh
#
# Idempotente. O script que faz o trabalho e' o ferramentas/backup.sh, que
# vem do repositorio - este aqui so' o agenda.
#
# ---------------------------------------------------------------------
# TEMPORIZADOR DO systemd, E NAO cron
#
# Tres razoes, e a terceira e' a que decide:
#   - Persistent=true recupera a execucao perdida se a maquina estiver
#     desligada na hora marcada; o cron simplesmente pula.
#   - RandomizedDelaySec espalha o horario, para o backup nao cair sempre
#     no mesmo minuto cheio.
#   - A saida vai para o journal com o nome da unit, entao
#     'journalctl -u guerra-backup-dia' conta a historia inteira - com cron
#     ela vira e-mail para o root, que ninguem le'.
#
# ---------------------------------------------------------------------
# O QUE ESTE SCRIPT NAO FAZ: MANDAR O BACKUP PARA FORA DA MAQUINA
#
# E' de proposito, e a razao e' de seguranca, nao de preguica.
#
# Se o SERVIDOR tiver credencial para escrever no destino do backup, quem
# invadir o servidor pode apagar ou criptografar os backups tambem - e' assim
# que um incidente vira perda total. Backup PUXADO de fora e' estruturalmente
# mais seguro que EMPURRADO de dentro.
#
# Entao a copia externa e' tarefa da maquina Windows, que tem espaco e HD
# externo: uma tarefa agendada que faz, por SSH,
#
#     scp -r libraro:/var/backups/guerra/dia  <destino local>
#
# A maquina de producao nao sabe onde os backups moram, e nao tem como
# alcanca-los. Ver IMPLANTACAO.md Etapa 10.
#
set -euo pipefail

FONTE="/opt/guerra-do-emperium/ferramentas/backup.sh"
DESTINO="/usr/local/sbin/guerra-backup"
AMBIENTE="/etc/guerra/backup.env"

passo() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()    { printf '    \033[32mok\033[0m   %s\n' "$*"; }
pula()  { printf '    \033[90m--\033[0m   %s\n' "$*"; }
erro()  { printf '\n\033[1;31mERRO: %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "precisa rodar como root"
[ -f "$FONTE" ] || erro "$FONTE nao existe - rode o atualiza_servidor.sh antes"

passo "Script"
install -m 750 -o root -g root "$FONTE" "$DESTINO"
ok "$DESTINO"

passo "Configuracao dos alertas"
install -d -m 750 -o root -g root /etc/guerra
if [ -f "$AMBIENTE" ]; then
    pula "$AMBIENTE ja' existe - preservado"
else
    cat > "$AMBIENTE" <<'FIM'
# Alertas do backup. Preencha quando o servico do outro lado existir.
#
# ALERTA_URL recebe POST quando ALGO DA ERRADO:
#   {"servidor":"...","evento":"falhou|tamanho|disco","mensagem":"..."}
#
# PULSO_URL recebe POST a cada backup BEM-SUCEDIDO:
#   {"servidor":"...","evento":"ok","ritmo":"hora|dia|semana","jogo_bytes":N,...}
#
# O PULSO E' O ALERTA QUE MAIS IMPORTA, e o unico que este servidor nao
# consegue dar sozinho: se a maquina parar, ninguem dispara nada, e o
# silencio e' identico a "esta' tudo bem". Configure do outro lado:
# "se nao chegar pulso em 3 horas, me avise".
ALERTA_URL=
PULSO_URL=

# Avisa quando a soma dos backups passar disto.
TETO_MB=500
FIM
    chmod 640 "$AMBIENTE"
    ok "$AMBIENTE criado (vazio - preencher quando houver endpoint)"
fi

passo "Temporizadores"
# hora   - 48 copias = dois dias. Perda maxima de uma hora de jogo.
# dia    - 30 copias = um mes. Cobre o bug percebido tarde.
# semana - 12 copias = tres meses. Cobre o "isso esta' errado ha' meses".
instala() {
    local ritmo="$1" quando="$2" espalha="$3"

    cat > "/etc/systemd/system/guerra-backup-$ritmo.service" <<FIM
[Unit]
Description=Guerra do Emperium - backup ($ritmo)
Documentation=file:///opt/guerra-do-emperium/IMPLANTACAO.md
After=mariadb.service
Requires=mariadb.service

[Service]
Type=oneshot
EnvironmentFile=-$AMBIENTE
ExecStart=$DESTINO $ritmo
FIM

    cat > "/etc/systemd/system/guerra-backup-$ritmo.timer" <<FIM
[Unit]
Description=Guerra do Emperium - backup ($ritmo)

[Timer]
OnCalendar=$quando
RandomizedDelaySec=$espalha
# Recupera a execucao perdida se a maquina estiver desligada na hora.
Persistent=true

[Install]
WantedBy=timers.target
FIM
    systemctl enable --now "guerra-backup-$ritmo.timer" >/dev/null 2>&1
    ok "guerra-backup-$ritmo.timer ($quando)"
}

instala hora   "hourly"         "5m"
instala dia    "*-*-* 04:20:00" "20m"
instala semana "Mon *-*-* 04:50:00" "20m"

systemctl daemon-reload

passo "Primeira execucao (a prova de que funciona)"
"$DESTINO" dia
ok "rodou"
ls -lh /var/backups/guerra/dia/ | tail -3 | sed 's/^/    /'

passo "Pronto"
cat <<FIM

    Backups em:  /var/backups/guerra/{hora,dia,semana}
    Ver:         systemctl list-timers 'guerra-backup-*'
    Log:         journalctl -t guerra-backup

    FALTA, e nao e' opcional:
      1. preencher ALERTA_URL e PULSO_URL em $AMBIENTE
      2. a copia PARA FORA da maquina - do Windows, puxando (ver o
         cabecalho deste script: puxar e' mais seguro que empurrar)
      3. testar uma restauracao. Backup nunca restaurado e' backup que
         nao existe.

FIM
