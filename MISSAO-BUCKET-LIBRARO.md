# Missão: fechar a mudança do bucket para `libraro/` (Mac)

**Arquivo temporário. Apagar no passo 5 — ele não é documentação, é uma
ordem de serviço.** O registro permanente fica no `PENDENCIAS.md` §0 (até o
fim) e no `HISTORICO.md` (depois).

## Onde estamos (2026-10-07, feito no Windows)

| passo | estado |
|---|---|
| 1. copiar a raiz do `ftn` para `ftn/libraro/` | **feito** — 7 objetos, `rclone check` com 0 diferenças, CDN 200 |
| 2. Atualizador 7 no canal e em `libraro/Jogar.exe` | **feito** — sha `6dfddc50…` igual no canal, no bucket, no CDN e no local |
| 3. botão Baixar do site apontando para `libraro/` | **FALTA — é esta missão** |
| 4. apagar a raiz do bucket | depois, 1–2 semanas após o passo 3 (Windows — a chave do bucket só existe lá) |

Conferido em 2026-10-07 que o site de produção **ainda** entrega a raiz:

```
curl -s https://libraro.filiponegrao.com.br/api/config
{"download":"https://cdn.filiponegrao.com.br/Jogar.exe"}
```

O commit do Mac mudou só o modelo (`site/config.exemplo.env`) e o
`configura_web.sh` — que escreve o `site.env` **apenas se ele não existir**.
O valor que vale mora em `/etc/guerra/site.env`, fora do git, e nenhum deploy
o toca.

## Passos (no Mac)

**1. Conferir que o destino está de pé antes de apontar para ele:**

```bash
curl -sL https://cdn.filiponegrao.com.br/libraro/Jogar.exe | shasum -a 256
# tem de dar 6dfddc5062d9e54639e091f9cb9f2cc406fd055cfe69ce573e80f0267766b742
```

**2. Trocar o endereço em produção** (só a linha, sem reescrever o arquivo):

```bash
ssh libraro "sed -i 's#^SITE_DOWNLOAD_URL=.*#SITE_DOWNLOAD_URL=https://cdn.filiponegrao.com.br/libraro/Jogar.exe#' /etc/guerra/site.env && grep ^SITE_DOWNLOAD_URL /etc/guerra/site.env"
```

**3. Reiniciar SÓ o site** — `guerra-site`, não os servidores do jogo
(`CLAUDE.md` §4.20 não é violado: ninguém é derrubado do jogo):

```bash
ssh libraro 'systemctl restart guerra-site && systemctl is-active guerra-site'
```

**4. Conferir de fora:**

```bash
curl -s https://libraro.filiponegrao.com.br/api/config
# {"download":"https://cdn.filiponegrao.com.br/libraro/Jogar.exe"}
```

E clicar em Baixar no navegador uma vez.

**5. Fechar a missão no repositório:**

- `PENDENCIAS.md` §0: riscar o passo 3 com a data, e deixar o passo 4 com a
  data a partir da qual a raiz pode sair (hoje + 1–2 semanas);
- `IMPLANTACAO.md` §9 item 8: marcar como feito;
- `git rm MISSAO-BUCKET-LIBRARO.md`;
- commit e push.
