# Prompt para a próxima sessão — a instância que falta

> Este arquivo é um **entregável de sessão**, não documentação permanente.
> Quando `jitterbug` fechar, **apague-o** e registre o resultado no
> `HISTORICO.md`, como manda o `CLAUDE.md` §7.

---

## Cole isto na sessão nova

```
Terminar a tradução PT-BR das instâncias: falta uma, o Sonho Sombrio
(grupo `jitterbug`), e ela está pela metade — 418 de 1.253 textos
distintos preenchidos, e o grupo NÃO aplicado.

Leia primeiro: CLAUDE.md (§4.12 e §4.13 são as regras que este trabalho
criou), depois PENDENCIAS.md §3, e ferramentas/LEIAME.md nas seções do
traduz_npcs.py e do preenche_catalogo.py. O contexto e as convenções já
fixadas estão no HISTORICO.md, seção "Quatorze instâncias e a Fenda
Dimensional em português".

O trabalho é terminar um catálogo e aplicar. Tudo já está extraído, e o
`preenche_catalogo.py --pendentes` lista só o que ainda falta.
```

---

## Onde as coisas pararam (2026-08-09)

**Quinze dos dezesseis grupos fecharam e estão aplicados**, com o map-server
subindo sem um `Unknown syntax`: `magoas`, `bakonawa`, `orcs`, `polvo`,
`porings`, `hospital`, `sarah`, `brinquedos`, `fenda`, `vermes`, `glastheim`,
`fenrir`, `demonio`, `charleston` e `crescente`.

**Sobrou o maior, e ele está pela metade:**

| grupo | pares | distintos traduzidos | distintos a traduzir |
|---|---|---|---|
| `jitterbug` | 2.406 | 418 | **835** |

Sonho Sombrio, `npc/re/instances/NightmarishJitterbug.txt`. Os 418 cobrem do
começo do roteiro até o encontro com a Lagi.

> **O grupo NÃO foi aplicado.** Só o `.cat` mudou; o arquivo do rAthena
> continua inteiro em inglês. Não aplicar antes de fechar — meia instância em
> português é pior que instância em inglês, e é a razão de o desenho ser um
> grupo por instância.

## O ciclo, por grupo

```
python ferramentas/preenche_catalogo.py --pendentes jitterbug
# ... escrever o t_jitterbug.py (dicionário Python em UTF-8) ...
python ferramentas/preenche_catalogo.py --gravar jitterbug t_jitterbug.py
# repetir as duas linhas acima até sobrar só o que fica em branco
python ferramentas/traduz_npcs.py --aplicar jitterbug --verificar
python ferramentas/traduz_npcs.py --aplicar jitterbug
```

**Não rodar `--extrair jitterbug`** agora: o catálogo já está em dia e tem 418
traduções dentro. (Re-extrair não as apagaria — a fonte é o `.INGLES` quando
existe, e aqui ele nem existe porque o grupo nunca foi aplicado —, mas não há
motivo.)

Depois: **reiniciar o map-server** e procurar `Unknown syntax` no
`rathena/log/map-msg_log.log` — procurar a palavra, não ler o fim do log.

**Gravar em levas é o jeito, e foi assim que os outros fecharam.** O
`--pendentes` só lista o que ainda está vazio, então gravar 200 e pedir a lista
de novo renumera e continua de onde parou. Só não aplicar o grupo antes de ele
estar inteiro.

**Como saber que fechou:** quando o que sobrar na lista do `--pendentes` for
só nome de mapa, arquivo de cutin, nome único de NPC (`Nome#01`), código de
cor e pontuação. No `crescente` sobraram 133 assim, e era esse o sinal.

## O que este trabalho aprendeu, e não está óbvio

Tudo o que virou regra permanente subiu para o `CLAUDE.md` — **leia §4.12,
§4.13 e as duas armadilhas novas do §5 antes de começar.** O resumo:

1. **`--extrair` antes de traduzir, sempre.** Os catálogos commitados em
   `661d77a` estavam velhos: onze dos dezesseis não tinham os `mapannounce` e
   `unittalk`. Catálogo velho aplica sem recusa e marca 100% enquanto a
   instância grita em inglês na tela.
2. **Nome de habilidade, item, mapa e monstro sai da tabela que o JOGO lê** —
   `skillinfolist.lub`, `itemInfo.lua`, `mapnametable.txt`,
   `db/guerra/mob_db.yml`. Inclusive quando ela **não** traduziu (`Mind
   Blaster` ficou em inglês). Nome que não está em tabela nenhuma fica em
   inglês.
3. **Nome de criatura traduz**, mesmo aparecendo em inglês na tela — é o que o
   Palácio das Mágoas já fazia, e meia frase em inglês é pior.
4. **Linha `+` vazia não é dívida.** Nome de mapa, label, nome único de NPC,
   `.bmp` de cutin, código de cor e pontuação solta ficam em branco de
   propósito. 86% num grupo de instância quer dizer completo.
5. **Fragmento montado com `+` se traduz olhando a ORDEM**, não a frase. O
   anúncio de entrada aparece em três ordens diferentes entre as instâncias.
6. **Preservar os códigos de cor** (`^0000ff`, `^000000`, `^FF0000`) byte a
   byte, e a posição deles na frase.
7. **O nome da instância nunca se traduz** — é chave, e o `--aplicar` já
   recusa sozinho.

## Duas coisas para conferir neste arquivo em especial

- **`setarray` com literal em MAIÚSCULA e `_`** pode ser nome de variável
  concatenado, e traduzir quebra calado. Foi o caso do `DIR_NORTHWEST` na Torre
  do Demônio (`CLAUDE.md` §5). Conferir antes de traduzir qualquer coisa nesse
  formato.
- **Argumento de `F_InsertPlural`** passa por regra de plural inglesa.
  Terminação em `-s`, `-x`, `-z`, `-f`, `-y` ou na lista de exceção em `-o`
  sai errada na tela, e nada avisa.

## O que NÃO faz parte disto

- **As 16 instâncias nunca foram abertas em jogo, uma a uma** — `PENDENCIAS.md`
  §1f. A tradução é offline; ver o roteiro rodar é outra frente.
- **Nome de monstro do servidor inteiro** continua metade em inglês
  (`PENDENCIAS.md` §1c). Dentro de instância o nome vem do 4º argumento do
  `monster` do script, que não entra no catálogo — então mesmo com a tradução
  aplicada o bicho aparece em inglês. É trabalho separado, e mecânico.
- **Duas missões da Ordem continuam comentadas** no `db/guerra/quest_db.yml`,
  por falta de alvo — `PENDENCIAS.md` §1g.
