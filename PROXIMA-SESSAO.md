# Prompt para a próxima sessão — traduzir as instâncias

> Este arquivo é um **entregável de sessão**, não documentação permanente.
> Quando a tradução das instâncias fechar, **apague-o** e registre o resultado
> no `HISTORICO.md`, como manda o `CLAUDE.md` §7.

---

## Cole isto na sessão nova

```
Terminar a tradução PT-BR das instâncias e da Fenda Dimensional.

Leia primeiro: CLAUDE.md, depois PENDENCIAS.md §3 (a frente de tradução) e
ferramentas/LEIAME.md na seção do traduz_npcs.py. O contexto de por que isso
começou está no HISTORICO.md, seção "O Palácio das Mágoas em português".

O trabalho é preencher catálogos e aplicar. Tudo já está extraído.
```

---

## Onde as coisas pararam

Tudo commitado em `main` (`661d77a`).

**A máquina está montada e testada.** O `ferramentas/traduz_npcs.py` ganhou:

- **um grupo por instância** (`magoas`, `orcs`, `sarah`, `hospital`,
  `charleston`, `brinquedos`, `jitterbug`, `vermes`, `bakonawa`, `fenrir`,
  `demonio`, `porings`, `polvo`, `crescente`, `glastheim`) mais **`fenda`**,
  que é a Fenda Dimensional (`dali`/`dali02`) — o saguão por onde se entra em
  metade das instâncias;
- `nomes_de_instancia()`, que **protege o nome da instância** de ser
  traduzido. Ele é CHAVE (`instance_create` resolve por string) e cai no
  catálogo por causa do `.@md_name$ = "..."`. O `--aplicar` agora recusa;
- **`mapannounce`, `announce` e `unittalk` em `CONTEXTOS`** — o texto da faixa
  do alto e do balão de monstro nunca tinha sido extraído.

**Os 16 catálogos estão extraídos e commitados** em
`rathena/npc/guerra/traducao/`.

## O que já está pronto, e o que falta

| grupo | estado |
|---|---|
| `magoas` | **aplicado em jogo.** 255 falas prontas; **faltam ~55 broadcasts** que entraram na re-extração |
| `bakonawa` | 66 falas prontas, faltam ~55 broadcasts. **Não aplicado** |
| `orcs` | 63 falas prontas, faltam ~119 broadcasts. **Não aplicado** |
| `polvo` | 79 falas prontas, faltam ~58 broadcasts. **Não aplicado** |
| `fenda` | 334 textos, **nada traduzido** |
| os outros 11 | extraídos, **nada traduzido** |

Ordem sugerida, do mais barato ao mais caro (textos distintos a traduzir):

```
bakonawa 38   orcs 55   polvo 64   porings 67   hospital 105
sarah 133   brinquedos 200   vermes 200   glastheim 253   fenrir 277
demonio 402   charleston 438   crescente 666   jitterbug 1102
```

## O ciclo, por grupo

```
python ferramentas/traduz_npcs.py --extrair <grupo>   # só se o vendor mudou
# preencher as linhas `+` do .cat à mão
python ferramentas/traduz_npcs.py --aplicar <grupo> --verificar
python ferramentas/traduz_npcs.py --aplicar <grupo>
```

Depois: **reiniciar o map-server** e conferir o log
(`python ferramentas/servidor.py reiniciar`, depois procurar `Unknown syntax`
no `rathena/log/map-msg_log.log` — não ler o fim do log, procurar a palavra).

## As cinco regras que não se negociam aqui

1. **Só aplicar grupo INTEIRO.** Arquivo quase todo em inglês com uma frase
   solta em português é pior que arquivo em inglês. Foi por isso que virou um
   grupo por instância.
2. **O `.cat` é cp1252, e o `.txt` também.** Editar com script que grave
   explicitamente em `cp1252` — a ferramenta de edição comum grava UTF-8 e
   **destrói o acento sem avisar** (`CLAUDE.md` §4.1 e §5). Conferir depois:
   nenhum `\xef\xbf\xbd` no arquivo.
3. **Deixar em branco o que não é fala.** Nome de mapa (`1@spa`), label
   (`::OnMyMobDead1`), nome único de NPC (`Lurid Royal Guard#dk`), `.bmp` de
   cutin, fragmento que só tem pontuação ou código de cor. No Palácio foram
   48 de 303 — por isso o `--estado` mostra 84% e isso quer dizer **completo**.
4. **Preservar os códigos de cor** (`^0000ff`, `^000000`, `^FF0000`) byte a
   byte, e a posição deles na frase.
5. **Nome de habilidade, item, mapa e classe sai da tabela do bRO**, não da
   cabeça — `skillinfolist.lub`, `mapnametable.txt`, `map_msg_por.conf`. Já
   custou cinco correções antes.

## Duas convenções de tradução já fixadas

Do Palácio das Mágoas, para os dois guardas não se confundirem:

- `Unpleasant Royal Guard` → **Guarda Real Rabugento** (o da entrada)
- `Lurid Royal Guard` → **Guarda Real Sombrio** (o do roteiro, que vira Sakray)

E o nome da instância **nunca** se traduz de novo — ele já está em português no
script desde 2026-08-08, e a ferramenta agora recusa mexer nele.

## O que NÃO faz parte disto

Duas missões da Ordem continuam comentadas no `db/guerra/quest_db.yml`, e as
duas por falta de alvo — está no `PENDENCIAS.md` §1g:

- **Torneio de Magia** — o `Muliphen` do bRO não existe no nosso `mob_db`.
- **Sussurro Sombrio** — é a Sky Fortress Invasion (`dali02 121,63`), que já
  está carregada e serve; falta a página do browiki para saber quais são os
  três "Demônios de cada tipo" entre os onze mobs `Immortal_`.
