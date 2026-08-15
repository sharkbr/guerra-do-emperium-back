# Sessão no Windows — apontar o cliente para o servidor Linux

> Este arquivo é um **entregável de sessão**, não documentação permanente.
> Quando a Etapa 2 fechar, **apague-o** e registre o resultado no
> `HISTORICO.md`, como manda o `CLAUDE.md` §7.

Escrito no Mac em **2026-08-15**, depois de o servidor Linux subir inteiro.

---

## Cole isto na sessão nova

```
O servidor Linux de produção está no ar e esperando o cliente. Falta a
Etapa 2 do IMPLANTACAO.md: apontar o cliente para ele e fazer o primeiro
login de verdade.

Leia primeiro: CLAUDE.md inteiro (a §5 tem duas armadilhas que decidem
este trabalho: cp1252 e a ferramenta de edição que destrói acento), depois
SESSAO-WINDOWS.md, que é o briefing completo, e o IMPLANTACAO.md Etapa 2.

Endereço do servidor: libraro.filiponegrao.com.br

O trabalho é curto — trocar um endereço num XML — mas o arquivo é cp1252 e
está fora do git, então o passo perigoso é ESCREVER. Fazer backup antes,
gravar por script, e conferir os acentos relendo em cp1252.

Depois: criar uma conta em https://libraro.filiponegrao.com.br e logar.
```

---

## O que está de pé do outro lado

Tudo isto foi verificado em 2026-08-15, não é suposição:

| | |
|---|---|
| Máquina | `libraro-server`, DigitalOcean, Ubuntu 24.04 x86_64 |
| Endereço | **`libraro.filiponegrao.com.br`** (138.197.155.31) |
| Portas | login **6900**, char **6121**, map **5121** — as três respondem da internet |
| Nome na lista de servidores | **Guerra do Emperium** |
| Site | **https://libraro.filiponegrao.com.br** — cria conta e tem painel |
| Banco | vazio de propósito: **nenhum personagem, nenhum GM** |
| MD5 de senha | **ligado** (a sua Etapa 1) |
| `new_account` | **`no`** — o cliente **não** cria conta digitando `nome_M` |

Os 19.622 scripts dos nossos NPCs carregaram no Linux **sem um erro** — zero
`Unknown syntax`.

---

## O trabalho — Etapa 2

### 1. O arquivo

`C:\GuerraDoEmperium\cliente\data\clientinfo.xml`, campo `<address>`, hoje
`127.0.0.1`. Trocar por **`libraro.filiponegrao.com.br`**.

Conferir também `<port>`, que deve ser **6900**.

### 2. O cuidado que decide

**O cliente inteiro está fora do git — backup antes de sobrescrever, sempre.**
E o `clientinfo.xml` é **cp1252**: ele tem `<desc>` com texto que pode ter
acento, e o `<servicetype>` importa (ver `CLAUDE.md` §5, entrada das bandeiras
de `CTRL+<n>`).

**Não editar com a ferramenta de edição do assistente.** Ela lê e grava como
UTF-8, e num arquivo cp1252 troca **todo** byte acentuado do arquivo por U+FFFD
— não só os da linha editada, e sem avisar (`CLAUDE.md` §5). A saída é a de
sempre: âncora em ASCII, gravar por script, `assert` de que a âncora é única, e
**reler em cp1252** para ver os acentos certos antes de dar por feito.

Medir o fim de linha do arquivo antes de escrever a âncora — não supor.

### 3. Fechar o cliente antes

`itemInfo.lua` e afins só são lidos na inicialização, e o exe fica travado
enquanto roda. Fechar, gravar, reabrir.

---

## Depois: o primeiro login

1. Criar uma conta em **https://libraro.filiponegrao.com.br**
   (usuário de 4 a 23 caracteres, senha de 6 a 32, e-mail de até 39 —
   é limite da coluna do rAthena, não capricho; mais CPF ou celular).
2. Abrir o cliente e entrar com ela.

### O que esperar, e o que cada falha significa

| Sintoma | O que é |
|---|---|
| *"rejected from server"* | `<passwordencrypt>` no `clientinfo.xml` brigando com o MD5. **O nosso não tem** — foi conferido. Se aparecer, é isso e não outra coisa |
| Loga e **trava na seleção de personagem** | o `char_ip` anunciado não é alcançável. Do lado do servidor está o domínio, e ele resolve — nesse caso o problema é DNS na sua máquina |
| Lista de servidores vazia | não chegou ao login-server: firewall local, antivírus, ou o `<address>` não pegou (cliente não foi reaberto) |
| Entra e o mapa não carrega | mapa faltando no GRF — mas o servidor carregou **1258 mapas**, então é do lado do cliente |

### Duas diferenças em relação ao HML que vão surpreender

1. **A conta nasce sem poder de GM** (`group_id 0`). No HML você usa a conta de
   grupo 99, que ignora `NoDrop` e as outras seis travas (`CLAUDE.md` §4.7). Lá
   nada disso vale — é a experiência do jogador de verdade. **Se quiser uma
   conta de GM para testar, peça na sessão do Mac**: é um `UPDATE` de uma linha,
   e é melhor que ele saia registrado do que feito à mão.
2. **Não há personagem nenhum.** O banco de produção nasceu vazio de propósito
   (`IMPLANTACAO.md` §8) — nada do HML foi levado, nem contas, nem itens.

---

## O que reportar de volta

- deu login? criou personagem? andou no mapa?
- **acentuação desenhando certo** em qualquer NPC — é o teste barato que pega
  erro de cp1252 ponta a ponta, e no Linux ele cobre também o charset do banco
  (`IMPLANTACAO.md` Etapa 13)
- qualquer coisa no log do map-server que não apareça no Windows

---

## O que **não** é desta sessão

- **O instalador do cliente.** O levantamento está no `PENDENCIAS.md` §5b e o
  servidor já tem onde hospedar (`https://libraro.filiponegrao.com.br/patch/`,
  servindo `/var/www/patch`). Mas antes de empacotar vale **anotar a lista de
  patches do NEMO** enquanto ainda se lembra quais foram aplicados: o exe é o
  único arquivo do conjunto sem gerador versionado, e sem essa lista ele é
  irreproduzível.
- **A conta interserver do HML.** Ela continua `s1`/`p1` naquela máquina. No
  Linux já foi trocada (`PENDENCIAS.md` §5, item 1). Trocar no HML é opcional —
  é ambiente de teste, atrás de NAT.
