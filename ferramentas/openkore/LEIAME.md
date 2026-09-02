# ferramentas/openkore — o que é nosso no bot fantasma

Esta pasta é **o delta**: os ~74 KB que transformam um openkore de
prateleira no fantasma da Arena de Combate. O openkore em si — 233 MB de
código de terceiros — não mora aqui e nunca vai morar.

A arquitetura é a mesma lei de customização do `rathena/` (`CLAUDE.md`
§2), aplicada a outro pacote de terceiros: **tudo que é nosso mora em
pasta própria, e um script aponta o de fora para ela.**

| arquivo | o que é |
|---|---|
| `plugins/pvpGhost/pvpGhost.pl` | o plugin — os três estados, o ciclo de combate, as fases `panic` e `shadow` |
| `plugins/pvpGhost/README.md` | a operação: como ajustar, como trocar o personagem, o que cada `pvpGhost_*` faz |
| `control/config.txt` | login (sem a senha), IA nativa desligada, o bloco `pvpGhost_*`, `portalCompile -1`, `ignoreInvalidLogin 1` |
| `control/sys.txt` | `loadPlugins_list pvpGhost,reconnect` |
| `tables/servers.txt.bloco` | só o bloco `[Guerra do Emperium - Local]`, para ser **anexado** ao arquivo do upstream |
| `instala.sh` | sobrepõe os cinco acima num checkout do openkore |

## O delta foi provado, não deduzido

Em 2026-08-31, um `diff -r` do checkout de desenvolvimento contra o
upstream `51de1dd` mostrou que, fora dos itens da tabela, só diferem:

- arquivos que o próprio openkore **gera em execução** — `fields/*.dist`,
  `fields/*.weight`, `tables/monsters.txt`, `tables/npcs.txt`,
  `tables/portalsLOS.txt`;
- backups locais — `control/config.txt.bak`, `control/config.txt.pre-estados`.

E **nada do upstream está faltando** no nosso. Isso é o que autoriza o
clone limpo: não há edição escondida em `src/` para perder.

> Até essa data isso era um risco de verdade, não uma formalidade: o
> checkout de desenvolvimento **não tem git**, então a lista de "o que é
> nosso" era só o que alguém tinha anotado à mão. Se houvesse uma edição
> não registrada, o clone limpo a perderia em silêncio, e o sintoma
> apareceria semanas depois como comportamento estranho do bot.

## A senha

O `config.txt` daqui **não tem senha nem PIN**. Ele traz:

```
!include fantasma.txt
```

e `control/fantasma.txt` é um **link** para `/etc/guerra/fantasma.txt`,
criado pelo `configura_fantasma.sh`. Mesmo padrão do
`/etc/guerra/site.env`: fora do repositório, nenhum comando de git o
alcança, e ele sobrevive a um reclone.

**O caminho do include é relativo de propósito, e isso não é estilo.**
O `Utils::TextReader::add` (`TextReader.pm:80`) concatena *sempre* o
diretório do arquivo pai, sem testar se o caminho é absoluto — um
`!include /etc/guerra/fantasma.txt` vira
`/opt/openkore/control//etc/guerra/fantasma.txt` e o boot morre com
*"File does not exist"*. Por isso o include é relativo e quem aponta para
`/etc/guerra` é o link. Testado com o parser real.

### O include é a última palavra, e isso é de propósito

Ele fica no **fim** do bloco de login, depois do `char`. No parser do
openkore a última atribuição de uma chave vence, então
`/etc/guerra/fantasma.txt` pode sobrescrever **qualquer coisa** do
`config.txt` — não só a senha.

O caso que importa é o **slot do personagem**. Ele é estado da máquina,
mas o `config.txt` é versionado e o `instala.sh` o sobrescreve a cada
deploy. Sem o include no fim, quem ajustasse o `char N` no servidor veria
o valor voltar sozinho no próximo `implanta.sh`, e o bot entraria com
outro personagem sem reclamar. Com ele no fim, basta pôr `char 3` no
arquivo da máquina.

Na prática: `/etc/guerra/fantasma.txt` é o `conf/import/` deste bot.

> **O que o include NÃO protege.** Se o `configModify` disparar — senha
> errada, o openkore pergunta no console e grava a resposta —, ele não
> reescreve o arquivo incluído, mas **anexa o valor novo ao próprio
> `config.txt`**, que é versionado (`writeDataFileIntact`,
> `FileParsers.pm:1931`). O include tira o segredo do git, e nada mais.
> Quem impede o episódio inteiro continua sendo o `ignoreInvalidLogin 1`.

## Pôr o bot no ar em produção — o roteiro do Mac

Tudo daqui roda **no Mac**, na raiz do repositório. Nenhum passo precisa
de SQL na mão.

### 1. Publicar

```
git pull
ferramentas/implanta.sh
```

Leva `ferramentas/openkore/` ao servidor. O `configura_fantasma.sh` lê
essa pasta do disco de lá e **não puxa o repositório sozinho** — por isso
este passo vem primeiro.

### 2. Instalar (roda duas vezes, e isso não é defeito)

```
ferramentas/implanta_fantasma.sh
```

Na **primeira** vez ele instala dependências, clona o openkore no commit
fixado, compila o `XSTools`, aplica o delta, escreve a unit — e cria
`/etc/guerra/fantasma.txt` com uma senha de exemplo. **A conta não é
criada nessa passada**, de propósito: uma conta de produção não deve
existir com senha de exemplo nem por um minuto.

### 3. A senha, num lugar só

```
ssh libraro 'vi /etc/guerra/fantasma.txt'
```

```
password uma-senha-boa-sem-aspas
loginPinCode 4728
```

**Este arquivo é a fonte única.** A senha vive em dois lugares por
exigência do protocolo — em texto aqui (o openkore precisa mandá-la em
claro) e em MD5 na coluna `user_pass`. Dois lugares é uma chance de
divergir, e o projeto já pagou por isso com a conta interserver. Aqui a
divergência não existe: quem manda é o arquivo, e o script faz o banco
obedecer.

O arquivo nasce `chmod 600`, dono `ragnarok`, fora do repositório — nenhum
comando de git o alcança e ele sobrevive a um reclone.

### 4. Rodar de novo — agora a conta nasce

```
ferramentas/implanta_fantasma.sh
```

Desta vez o passo 6 cria a conta `fantasma` com `MD5(senha)`, `group_id`
20 e o PIN, confere que o grupo 20 está no `groups_guerra.yml`, e lista os
personagens que a conta tem. Rodar de novo depois disso **sincroniza** —
é assim que se troca a senha no futuro: edita o arquivo, roda, pronto.

### 5. O personagem — o único passo que não dá para automatizar

Não existe caminho por SQL: a criação passa pelo char-server. Entre no
cliente com a conta `fantasma` e crie um **Renegado** — a classe é
decisão, é dela que saem a Cópia Explosiva, as Máscaras e o Vínculo
Sombrio do ciclo.

Depois, com um GM, os dois itens infinitos:

```
#item <personagem> 30993 1     Tinta para Parede Infinita
#item <personagem> 30992 1     Pincel do Infinito
```

**Sem eles as habilidades do ciclo não saem** — e o `#` (char-command) é
obrigatório, porque `@item` só dá para si mesmo.

Se o personagem não nascer no slot 1, ponha `char N` no
`/etc/guerra/fantasma.txt`. Ele vence o valor do git, porque o `!include`
é a última linha do bloco de login (ver acima).

### 6. Ligar, com a arena vazia

```
ssh libraro 'systemctl enable --now guerra-fantasma'
ssh libraro 'journalctl -u guerra-fantasma -f'
```

E, se quiser o RSS real em Linux, que ainda é estimativa:

```
ssh libraro 'systemctl status guerra-fantasma | grep Memory'
```

### Desligar

```
ssh libraro 'systemctl disable --now guerra-fantasma'
```

Não derruba ninguém e não toca no jogo. O grupo 20 e os dois rótulos do
visual ficam inertes.

### Se o login for recusado sem explicação

É quase sempre o grupo. O `pc_group_pc_load`
(`src/map/pc_groups.cpp:348`) **chuta a conta** se o `group_id` não
existir nos grupos *carregados* — e o arquivo estar no disco não basta.
Recarrega com **`@reloadatcommand`**, não `@reloadscript`.

## Atualizar depois

Mudança no plugin ou na config viaja no deploy normal:

```
ferramentas/implanta.sh
```

A seção *6b* do `atualiza_servidor.sh` cuida disso: reaplica o delta e
reinicia o bot. Ela tem **carimbo próprio** (`.carimbo-fantasma`), e a
razão importa: reiniciar o fantasma não derruba ninguém, então amarrá-lo
ao `.carimbo-jogo` faria uma correção de plugin esperar pela próxima
janela de manutenção sem motivo. É a mesma lógica que separou o site do
emulador.

O `implanta_fantasma.sh` fica para instalar, reparar, trocar a senha, ou
subir a versão do openkore — casos em que há compilação ou banco
envolvidos. Ele **não** é o caminho de atualização de plugin: não reinicia
o serviço, então os arquivos mudariam em disco e o bot seguiria rodando o
código velho, calado.

## Subir a versão do openkore

O commit vive em `OPENKORE_COMMIT`, no `configura_fantasma.sh`. Trocar é
decisão consciente, e o roteiro é:

1. clonar o commit novo numa pasta à parte;
2. `diff -r` contra o commit antigo, olhando `src/Network/` — é ali que
   uma mudança de protocolo apareceria;
3. trocar a constante, rodar `configura_fantasma.sh --recompila`;
4. **testar o bot antes de considerar feito**, porque o sintoma de
   incompatibilidade de pacote não é um erro claro: é a tela de seleção
   de personagem travando calada.

## O que quebra este bot no futuro

**A ofuscação de pacote.** O `IMPLANTACAO.md` §8 registra que o
`PACKET_OBFUSCATION` está ligado com as chaves padrão do rAthena, que são
públicas, e que trocá-las "fica para o próximo patch". No dia em que as
três chaves virarem próprias, o fantasma **para de conectar**, e o
sintoma é falha de parsing, não uma mensagem clara.

O conserto é uma linha no `tables/servers.txt.bloco`:

```
sendCryptKeys 0xAAAAAAAA, 0xBBBBBBBB, 0xCCCCCCCC
```

com as mesmas três chaves do servidor. Caro é descobrir isso no dia.
