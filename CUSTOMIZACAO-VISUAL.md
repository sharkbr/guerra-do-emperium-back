# Customização visual — a temática de cidade destruída

Registrado em 2026-07-31. **Nada foi feito ainda** — este arquivo é a análise de
viabilidade que abre a frente, não um relato de trabalho concluído. O que estiver
marcado como não verificado é hipótese, e hipótese aqui já se provou errada
várias vezes (ver o histórico do `PENDENCIAS.md`).

## O objetivo

O bRO fechou. Este servidor é para jogar PvP com um grupo fechado, e a ideia é
que as cidades apareçam **destruídas** — a ficção é que o meteoro passou e foi
ele que fechou o servidor original.

### A ficção, fechada em 2026-07-31 — e ela dita o desenho

**Foi um meteoro só, que caiu no mar. Quem matou o resto foi a onda.**

Isso não é detalhe de ambientação, é a especificação do trabalho visual:

- **Não há cratera.** Foi decidido explicitamente que não vamos fazer nenhuma.
  Isso elimina o item mais caro e mais arriscado da análise original — o único
  que atravessaria a fronteira do `.gat` e puxaria a regeração do
  `map_cache.dat` junto. Ver "a fronteira com o servidor".
- **Não há escombro projetado.** Impacto arremessa; onda **tomba, afunda e
  varre**. Construção inclinada e meio soterrada no limo, adereço leve levado
  embora, chão encardido de lama seca.
- **As casas estão quase todas destruídas.** As que restam de pé têm fissura ou
  outro dano — nenhuma fica intacta.
- **O chão fica mais sujo/destruído**, em todas as cidades menos uma.

### Prontera fica intacta, de propósito

Prontera é o centro da sobrevivência e **já foi restaurada** na ficção. É a
única cidade que não muda de aspecto. O `destroi_mapa.py` recusa rodar nela.

### Duas restrições de projeto

1. **Gastar o mínimo possível** no chão.
2. **Não onerar memória de renderização.**

As duas apontam para a mesma técnica e estão atendidas na amostra: sujar por
**cor de superfície** em vez de textura nova, e fazer destroço **clonando modelo
que o mapa já carrega** em vez de trazer `.rsm` novo. Ver "a amostra de Izlude",
onde a contagem de objetos do mapa terminou **menor** que a original.

Consequência de escopo que vale registrar: **PvP não precisa do mundo inteiro.**
Uma ou duas cidades e as arenas já entregam a temática.

---

## A correção do enunciado: quase nada disso é sprite

A pergunta original foi sobre "trocar/editar sprites". Cidade destruída não mora
nas sprites. Os prédios de Prontera são **modelos 3D com textura**, não desenhos.
O conteúdo visual do cliente se divide em famílias de formato bem separadas:

| Formato | O que é | Onde fica | Pesa na temática? |
|---|---|---|---|
| `.rsw` | o "mundo" do mapa: lista de modelos com posição/rotação/escala, **luz ambiente e difusa**, direção do sol, água, névoa | `data\<mapa>.rsw` | **muito** |
| `.gnd` | malha do chão: altura por vértice, textura por tile, lightmap, cor por superfície | `data\<mapa>.gnd` | **muito** |
| `.rsm` | modelos 3D — prédios, muros, fontes, árvores, destroços | `data\model\...` | **muito** |
| `.bmp` / `.tga` | texturas do chão e dos modelos | `data\texture\...` | **muito** |
| `.gat` | colisão e altura andável por célula | `data\<mapa>.gat` | só se mudar o relevo — **e aí mexe no servidor** |
| `.spr` + `.act` | sprites 2D: personagens, monstros, NPCs, itens | `data\sprite\...` | pouco |
| `.str` | efeitos animados | `data\texture\effect\` | opcional (fumaça, brasa) |

Traduzindo para a prática, "deixar destruído" é: escurecer e queimar texturas,
mudar a luz do mapa para vermelho-cinza com névoa, tombar e afundar modelos,
abrir cratera no chão, espalhar entulho.

---

## Os dois pontos de alavanca

### 1. O `DataFolderFirst` já está aplicado

O `data\` do disco vence o GRF (é o que faz a tradução funcionar hoje, e repare
que `data\airplane.gat` já está solto lá). Então um `prontera.rsw` modificado é
**um arquivo solto em `data\`**:

- sem repack do GRF de 3 GB;
- reversível apagando o arquivo;
- **versionável no git**, ao contrário do GRF;
- e o servidor não precisa saber de nada.

Isso encaixa direto na convenção de customização já decidida: o nosso mora em
pasta própria, o upstream (aqui, o GRF da Gravity) fica intacto.

### 2. A Gravity provavelmente já fez cidade destruída — NÃO VERIFICADO

Morroc foi destruída no episódio 13.1, e o kRO passou a ter a versão arruinada do
mapa: chão rachado, fissuras, entulho, paleta de cinzas. Se esses modelos e
texturas estiverem no nosso GRF de 2021-11-03, o trabalho deixa de ser "desenhar
arte nova" e vira "compor com peça existente" — que é justamente o que dá para
fazer bem por script.

**É a primeira coisa a conferir**, porque muda o plano inteiro. Ver "ordem de
trabalho" abaixo.

---

## O que dá para fazer aqui, e o que não dá

A divisão é clara: **transformar** ativo existente por script é viável;
**criar** arte nova não é.

### Viável, e é onde está o retorno

| O quê | Por que é barato |
|---|---|
| **Luz e névoa do `.rsw`** | meia dúzia de floats, transforma o clima do mapa inteiro. Maior efeito pelo menor risco de todos — é por onde começar |
| **Texturas em lote** | passar uma transformação tonal consistente (dessaturar, escurecer, fuligem, brasa alaranjada nas bordas) sobre as ~centenas de texturas de um mapa. Feito por script, o conjunto fica **coerente** — e coerência é o que vende "mesma catástrofe" |
| **Manipular modelos existentes** | rotacionar um pilar para virar coluna caída, afundar meio prédio no chão, escalar, duplicar destroços, remover. Tudo é entrada na lista de objetos do `.rsw` |
| **Troca de paleta de sprite** | `.pal` é 256 cores; recolorir NPC ou monstro é trivial |
| **Parsers em Python** | `.rsw`, `.gnd`, `.gat`, `.spr`, `.act` são formatos documentados e de tamanho fixo. Escrever leitor/escritor é trabalho mecânico, não pesquisa |

**Cratera saiu do escopo** por decisão de ficção — ver acima. Era o item mais
caro e o único que mexeria no `.gat`.

### Fora de alcance

- **Desenhar.** Nada de pixel art nova nem modelo 3D novo. Um prédio desabado
  *modelado do zero* não sai daqui.
- **Ver o resultado.** O ciclo depende de abrir o cliente e olhar. Toda alteração
  é feita às cegas e precisa de screenshot para fechar o laço.

### No meio

- **Empacotar GRF de distribuição** para os outros jogadores. Dá para escrever o
  writer, mas o GRF Editor pronto provavelmente é melhor uso do tempo. Enquanto
  for só teste local, o `data\` solto basta e nem se coloca a questão.

---

## A fronteira com o servidor: o `.gat`

**Enquanto a alteração for puramente visual — `.rsw`, `.gnd` de textura/cor,
modelos, texturas — o servidor é indiferente.** Não recompila, não regera
`map_cache.dat`, não reinicia. Para um servidor de PvP isso é perfeito: os
jogadores veem a ruína, a mecânica não muda uma vírgula.

O `.gat` é onde essa isenção acaba. Ele guarda colisão **e altura andável por
célula**, e é dele que o `map_cache.dat` do rAthena é gerado (ver `PENDENCIAS.md`
item 7 — regerar exige o GRF do cliente).

**Com a cratera fora do escopo, nada do trabalho planejado toca o `.gat`.** A
frente visual inteira fica do lado barato dessa fronteira: nenhum recompilar,
nenhum map cache, nenhum reinício de servidor. O `izlude.gat` sequer foi
modificado na amostra — só extraído para conferência.

Se um dia a cratera voltar à mesa, a ressalva a confirmar antes é se o
personagem tem a altura ditada pelo `.gat` e não pelo `.gnd`. Se tiver, rebaixar
só o chão visual faria o personagem andar no ar sobre o buraco, e os dois teriam
que mudar juntos.

Nota correlata: **substituir** um mapa existente (manter o nome `prontera`) não
custa nada além dos arquivos. **Adicionar** um mapa novo custa registro em três
lugares — `db/map_index.txt`, o map cache, e as tabelas de nome do cliente.
Preferir substituir enquanto der.

---

## O DES do `grf.py` — deixou de ser bloqueio para esta frente

A análise de 2026-07-31 dizia que o DES bloqueava tudo. **Estava errado**, e a
correção é o que destravou a amostra no mesmo dia.

**Segunda correção, de 2026-07-31 ~01:05:** a frase abaixo dizia "os arquivos de
mapa estão sem DES", e isso é largo demais. Contado no GRF: dos 910 `.rsw`,
**640 estão com DES e 270 sem**. Izlude caiu no lado bom por sorte, não por
regra — `prt_are01`, `quiz_01`, `job_hunte`, `poring_w01` e `sec_pri` estão
todos com `flags=3`. Escolher mapa base para trabalhar hoje significa **escolher
dentro dos 270**, e foi o que levou ao `x_prt` do mapa-catálogo.

Medido no GRF, para Izlude especificamente:

```
data\izlude.rsw   228430 bytes  flags=1
data\izlude.gnd  2327838 bytes  flags=1
data\izlude.gat  1608014 bytes  flags=1
data\model\izlude\iz_academy.rsm  48899 bytes  flags=3   <- DES
```

Os `.rsm` estão atrás do DES (`flags=3`), mas **isso não importa**: o `.rsw` só
*referencia* modelo por nome de arquivo, e é o cliente quem o abre do GRF. Então
tombar, afundar, escalar, clonar e remover prédio se faz mexendo **só no
`.rsw`** — sem extrair um `.rsm` sequer.

O DES continua pendente para o dia em que precisarmos **ler ou editar geometria
de modelo**, ou inventariar texturas que estejam atrás dele. Não é urgente.

**A lição, que já se repetiu nesta base:** medir antes de declarar bloqueio. O
custo de rodar `grf.py find izlude` era de segundos e teria evitado a conclusão
errada.

---

## O DES nos 640 `.rsw` deixou de ser trava — 2026-08-11

A seção acima fecha dizendo que escolher mapa para trabalhar significa
**escolher dentro dos 270 sem DES**. Isso deixou de valer, e a saída é a regra 3
do `CLAUDE.md`: quando falta algo, traz-se do bRO.

**O GRF do bRO tem os mesmos mapas sem DES.** Medido no `auction_01`, que no
nosso está com `flags=3` (`.rsw`) e `flags=5` (`.gnd`, `.gat`):

```
                       nosso (csize/rsize/flags)   bRO (csize/rsize/flags)
data\auction_01.rsw     17411 / 113618 / 3          17411 / 113618 / 1
data\auction_01.gnd     90305 / 468894 / 5          90305 / 468894 / 1
data\auction_01.gat      2569 / 400014 / 5           2569 / 400014 / 1
```

O `.rsw` do bRO abre no `grf.py`, e é a base de trabalho. **O `.rsw` gerado
continua sendo lido contra o NOSSO GRF** na hora de conferir os `filename` — o
cliente é o nosso, e é ele que precisa ter cada `.rsm`.

### A prova de que é o mesmo mapa, e ela é barata

Trazer arquivo de outro cliente sem conferir é trocar a revisão do mapa por
baixo do pano. São três medidas, em ordem de força:

1. **`rsize` igual** nos três arquivos. Necessário, longe de suficiente.
2. **`csize` igual.** O DES do GRF embaralha blocos de 8 bytes mas **não muda o
   comprimento do zlib**, então comprimido idêntico é sinal forte de plaintext
   idêntico. É a medida que quase fecha sozinha.
3. **O `.gat` do bRO contra o `map_cache.dat` do NOSSO servidor**, célula a
   célula. É a prova de verdade, e é a que fecha: o `map_cache` foi gerado do
   **nosso** `.gat`, então comparar os dois é comparar o mapa deles com o nosso
   sem precisar decifrar nada. No `auction_01` deram **20.000 de 20.000**.

O 3 só existe porque o servidor tem uma cópia do `.gat` em outro formato. Não há
equivalente para `.rsw` e `.gnd` — para esses o argumento é o `csize`.

### O que isto abre, e o que continua fechado

Abre os **910 mapas**, e não só os 270. O que continua fechado é editar
geometria de `.rsm` — mas isso nunca foi necessário para trocar, mover, escalar
ou plantar modelo, que é tudo feito no `.rsw`.

Continua valendo a decisão de sempre: **versionamos a receita, não o mapa
gerado**. O `.rsw` instalado é artefato; a fonte da verdade é a entrada do
`RECEITA` no `edita_mapa.py`.

---

## Armadilha herdada: caminho com coreano

As pastas de conteúdo do GRF têm nome em coreano — a de interface já apareceu na
frente de tradução como `data\texture\유저인터페이스\`, e as de modelo e textura
por cidade seguem o mesmo padrão.

Já está registrado que **caminho com trecho coreano não sobrevive ao console do
PowerShell até o `argv` do Python**. Foi por isso que o `grf.py` ganhou o
`getlike`, que casa por substring ASCII dentro do próprio script. Qualquer
ferramenta nova desta frente precisa nascer com o mesmo cuidado.

---

## A amostra de Izlude — 2026-07-31, branch `visual/izlude-amostra`

**Feita e instalada no cliente. Falta olhar in-game.** Escolhida Izlude porque é
cidade portuária: a onda ali é literal.

### O que ficou provado sobre os formatos

Tudo abaixo foi **medido**, não suposto. O método foi o mesmo nos dois formatos:
escrever leitor e escritor e exigir **round-trip byte a byte** do arquivo não
modificado. Se o arquivo reescrito não sai idêntico ao original, o layout está
errado e não se grava nada. Os dois passam.

| O quê | Valor conferido em Izlude |
|---|---|
| Versão do `.rsw` | 2.1 |
| Versão do `.gnd` | 1.7 — 134×150 tiles, 21 texturas, 20358 superfícies |
| Objetos no `.rsw` | 679: 552 modelos, 5 luzes, 110 sons, 12 efeitos |
| Luz original | difusa 0.99/0.97/1.00, ambiente 0.30/0.30/0.30, sombra 0.60 |
| Água | nível 45, onda alt. 1.0, vel. 2.0, incl. 50, anim 3 |

Três descobertas que valem para qualquer mapa daqui para frente:

1. **A "sobra" de 65520 bytes no fim do `.rsw` é a QuadTree**, não lixo nem erro
   de parser: 1365 nós de 48 bytes, que é a árvore de 5 níveis
   (1+4+16+64+256+1024). É índice espacial derivado do `.gnd`, **não** da
   posição dos modelos — por isso mexer em modelo não a invalida, e dá para
   preservá-la intacta.
2. **Cada superfície do `.gnd` tem cor BGRA própria**, que o cliente multiplica
   pela textura. É o caminho de sujar o chão **sem trocar textura nenhuma**:
   zero arquivo novo, zero memória de vídeo a mais. Atende as duas restrições de
   projeto de uma vez. Em Izlude 9611 das 20358 superfícies estavam em branco
   puro (255/255/255), ou seja, sem tinta alguma — espaço livre para trabalhar.
3. **O eixo Y de RO aponta para baixo.** Aumentar `y` **afunda** o modelo. Confere
   com os dados: folhagem de árvore em `y = -78` (no alto) e tronco em `y = 0`.

### O que a receita faz

Em `ferramentas/destroi_mapa.py`, tudo declarativo no topo do arquivo:

| Camada | O que faz |
|---|---|
| **Luz** | difusa 0.99/0.97/1.00 → 0.62/0.60/0.57 e ambiente 0.30 → 0.34/0.32/0.29. A difusa cai e **perde o azul** (o original puxa para o frio); o ambiente sobe um pouco para o sol sumido não fechar as sombras em preto; a opacidade da sombra vai de 0.60 a 0.35, porque dia encoberto não projeta contorno duro |
| **Construções** | as 13 instâncias de casa/loja/guilda de Izlude, tombadas e afundadas. 55% levam o tratamento pesado (11–24°, afunda 6–14) e leem como desabadas e meio soterradas; o resto leva 2,5–7° e afunda 1–3,5, o suficiente para o prumo sumir — que é a leitura de recalque/rachadura sem arte nova |
| **Adereço leve** | 70% dos vasos, flores, bancos, bancas de peixe/pão/fruta e placas: **removidos**, varridos pela onda |
| **Destroços** | 3 por construção afetada, **clonando modelo que o mapa já carrega** — barril, caixote, balde, tonel, coluna de madeira — deitados de lado (72–108° num eixo) com guinada livre |
| **Chão** | as 20358 superfícies escurecidas com o azul derrubado mais que o vermelho (escala R 0,74 / G 0,68 / B 0,55), com piso 28 para o que já era escuro não virar preto chapado e apagar o relevo |

### O resultado medido

```
construcoes  7 arrasadas, 6 avariadas
adereco      49 varridos pela onda
destrocos    39 clones de 7 modelos que o mapa ja carregava
chao         20358 de 20358 superficies encardidas
objetos      679 -> 669 (-10)
```

**O mapa terminou com menos objetos do que começou** e sem um único `.rsm` ou
textura novos. A restrição de memória não foi só respeitada — o saldo é
negativo.

A semente é fixa (`20260731`), então rodar de novo dá exatamente o mesmo mapa.

### Onde está e como reverter

Gerados e copiados para `C:\GuerraDoEmperium\cliente\data\izlude.rsw` e
`izlude.gnd`, que vencem o GRF pelo `DataFolderFirst`. **Apagar os dois arquivos
reverte** — o original nunca saiu do GRF, então não há backup a manter. O
`izlude.gat` não foi tocado.

Versionamos o **script**, não a saída: a receita é a fonte da verdade e o mapa é
artefato gerado, pelo mesmo critério do `map_cache.dat` no `PENDENCIAS.md`.

### Primeira rodada in-game — 2026-07-31, ~00:56

**O mapa abre e a temática funciona.** O chão encardido e a luz cinza leem como
pretendido, e o caixote de madeira lê certo como destroço.

**Um erro, e vale mais que o acerto:** as "construções destruídas" eram
**troncos de árvore gigantes** deitados pela cidade.

A causa é de classificação, não de código. Eu li
`나무잡초꽃\나무기둥01.rsm` como "pilar de madeira" — `기둥` é pilar/coluna — e
usei como destroço de construção. Mas a pasta `나무잡초꽃` significa
literalmente **"árvore, erva, flor"**: é a pasta de vegetação. O modelo é tronco
de árvore, e é enorme. Deitado a 90° virou tora atravessada na rua.

**A regra que sai disso: a pasta manda mais que o nome do arquivo.** A
informação para acertar estava à vista o tempo todo — eu classifiquei pela folha
e ignorei a raiz. Corrigido em `destroi_mapa.py`, com o motivo escrito no lugar
onde a linha estava, para ninguém repor.

### Como conferir modelo antes de usar — o fluxo

O problema de fundo é que os modelos têm nome em coreano e eu não consigo ver o
jogo. São três mecanismos, e eles se complementam:

| Como | Custo | Serve para |
|---|---|---|
| **Screenshot** | zero | Eu leio imagem direto. É o laço mais curto e foi o que pegou o tronco de árvore. Bom para diagnosticar, ruim para varrer muitos modelos |
| **Catálogo traduzido** | pronto — `CATALOGO-IZLUDE.md` | Os 90 modelos com pasta e nome traduzidos, a classificação atual da receita, e uma coluna vazia para correção humana. É o artefato de conferência **antes** de usar |
| **Mapa-catálogo in-game** | **pronto** — `@warp prt_fild08 122 146` | Um exemplar de cada modelo, de pé, com placa numerada ao lado. Uma volta a pé resolve o mapa inteiro. Ver a seção própria abaixo |

Um quarto caminho, mais caro e não iniciado: **renderizar os `.rsm` eu mesmo**
para gerar miniaturas e olhar sem intermediário. Exige o DES (os `.rsm` estão
atrás dele), um parser de `.rsm` e um rasterizador. É o único que me tornaria
autossuficiente.

## O mapa-catálogo — 2026-07-31

**`@warp prt_fild08 122 146`** põe você ao lado do modelo nº 1. Os 90 modelos de
Izlude, um exemplar de cada, de pé, em grade, com uma **placa numerada** ao lado.
O número da placa é o número do `CATALOGO-INGAME.md`, que também traz o
`@warp x,y` de cada um.

### Por que `prt_fild08`

A primeira versão foi para o `x_prt`, e **ficou confusa** — dito depois de olhar
in-game. Duas causas, e as duas foram corrigidas:

1. O `x_prt` é mapa de cidade: parede, beco e chão irregular no meio do
   catálogo.
2. A grade **espalhava os modelos pelo mapa inteiro** pulando célula bloqueada,
   o que deixava as fileiras irregulares.

`prt_fild08` é campo aberto de 400×400 células, `.rsw` sem DES e no
`map_index`. Tem spawn declarado em `npc/re/mobs/academy.txt` — 110 Poring, 100
Lunatic, 100 Fabre, 30 Little Poring — mas **todos passivos**: nada ataca, eles
só aparecem no cenário. O respawn é de 5 s, então `@killmonster` não segura.

Se um dia o cenário limpo importar mais que o espaço, o `x_prt` continua na
mesa: não tem spawn nenhum. É trocar `MAPA_BASE` no topo do
`catalogo_ingame.py`. O `bl_grass` é grande mas o terreno é irregular; o
`new_zone01` é plano e tem só 22% andável.

### Como foi construído

1. **Todos os objetos originais do mapa base são apagados** e substituídos pelo
   catálogo. Por isso o entulho do mapa base não atrapalha — o que estiver lá é
   nosso.
2. **Grade compacta e retangular**, 10 colunas × 11 fileiras com passo de 12
   células (60 unidades), ancorada no ponto do mapa que deixa mais pontos em
   chão livre — 105 de 110, e usamos 90. A folga é de propósito: com a grade
   justa de 10×9, três pontos caíam em chão bloqueado e três modelos ficavam de
   fora.
3. **Ordem por pasta**, não por frequência. Assim cada fileira tem um tema —
   vegetação junto de vegetação, construção junto de construção — e a volta a pé
   faz sentido. Era por frequência na primeira versão, o que misturava árvore
   com loja e balde.
4. A luz é forçada para neutra e clara (difusa 1,0 / ambiente 0,62). Catálogo é
   para identificar modelo, não para ambientar.
5. Cada modelo é **clonado do exemplar que Izlude usa**, o que preserva a escala
   com que ele aparece de verdade. Tamanho errado foi metade do problema do
   tronco de árvore — de pé e em escala real, aquele modelo se denunciaria na
   hora.

### A conversão de coordenadas foi medida

Esta é a parte que erra silencioso: se a conversão estiver errada, os modelos
aparecem no lugar errado ou enterrados, e nada acusa. Então foi **medida**, com
os 552 modelos de Izlude como amostra — a correlação entre a altura do terreno
sob cada modelo e o `y` do próprio modelo só aparece com o sinal certo de `z`:

| candidato | correlação |
|---|---|
| **`z` positivo, altura mesmo sinal** | **+0,389** |
| `z` positivo, altura invertida | −0,389 |
| `z` negativo | ±0,051 — ou seja, ruído |

O sinal errado de `z` destrói a correlação, o que torna o resultado decisivo:

```
mundo_x = (celula_x - largura_gat/2) * 5 + 2,5
mundo_z = (celula_y - altura_gat/2)  * 5 + 2,5
mundo_y = altura do .gat na celula (mesmo sinal)
```

O `.gat` tem o **dobro** da resolução do `.gnd` em cada eixo — uma célula de
`.gat` é um quarto de tile de `.gnd`. Confirmado pelo tamanho do arquivo:
`268 × 300 × 20 + 14 = 1608014`, exatamente o `izlude.gat`.

### Onde está cada peça

| Peça | Onde | Reverter |
|---|---|---|
| Mapa | `cliente\data\prt_fild08.rsw` | apagar o arquivo |
| Placas | `rathena\npc\guerra\catalogo_visual.txt` | comentar a linha no `scripts_guerra.conf` |
| Legenda | `CATALOGO-INGAME.md` | — |

As placas são **ferramenta de trabalho, não conteúdo de jogo**. Manter
desligadas no `scripts_guerra.conf` quando não estiverem em uso.

## MUDANÇA DE DIREÇÃO — 2026-07-31, depois de ver o catálogo de ruína

**Izlude foi revertida ao original.** Os overrides `izlude.rsw` e `izlude.gnd`
foram apagados do `cliente\data\`; o GRF voltou a servir o mapa. Nada do que a
amostra fez continua valendo.

A decisão, depois de olhar as ruínas in-game: **o acervo é bom demais para
continuar simulando destruição.** Em vez de tombar e afundar casa inteira, trocar
a casa pela ruína correspondente.

### O que muda na ficção

O meteoro **já passou** — faz tempo. O céu limpou. Então:

| Camada | Antes (amostra) | Agora |
|---|---|---|
| **Luz** | cinza de poeira, difusa 0,62 | **original**, sem alteração |
| **Chão** | encardido por cor de superfície | **original**, sem alteração |
| **Construções** | tombadas e afundadas | **substituídas** por modelo de ruína |
| **Adereço** | 70% varridos | manter; **acrescentar** entulho de ruína |

A destruição passa a viver **só na geometria**, não na atmosfera. É mais barato,
mais reversível e mais convincente: casa de verdade quebrada em céu limpo lê como
"a catástrofe foi há anos", que é exatamente a ficção.

### O que isso faz com o `destroi_mapa.py`

Fica **obsoleto para Izlude**, mas não foi apagado: as camadas de encardir chão e
varrer adereço podem servir a outra cidade, e o custo de manter é zero. O que não
serve mais é a de tombar e afundar construção — foi substituída por algo melhor.

### O protocolo para aplicar as trocas

Duas operações, e cada uma precisa de uma informação diferente:

**Substituir** — a casa X de Izlude vira a ruína Y:

> "trocar o **47** de Izlude pelo **73** do catálogo"

O número de Izlude sai do `CATALOGO-IZLUDE.md` (90 modelos); o da ruína, do
`CATALOGO-INGAME.md` (228 modelos, os mesmos que estão in-game em
`prt_fild08`). Por padrão vale para **todas as instâncias** daquele modelo.

**Acrescentar** — pôr a ruína Y num lugar de Izlude:

> "pôr o **15** do catálogo em izlude **128,150**"

A coordenada sai de `@where <nome do personagem>` no lugar onde quiser. Eu
converto para coordenada de mundo — a conversão já está medida e é a mesma que
posicionou o mapa-catálogo.

**O que não precisa:** rotação, escala ou altura. Eu tiro a altura do `.gat` e
uso escala natural do modelo, como no catálogo.

---

## Izlude, primeira rodada da abordagem nova — 2026-07-31

Aplicado com `ferramentas/edita_mapa.py`. Luz, água, chão e `.gat` **originais**;
só a geometria mudou.

```
66 de 66 arvores  ->  ossada 02 x26, ossada 04 x25, espinheiro x15
14 de 46 muros    ->  parede de casa abandonada (China), 30%
```

### A medição que evitou um estrago

Árvore em RO costuma ser **composta** — tronco e copa como modelos separados. Se
fosse o caso aqui, trocar o tronco deixaria copa flutuando a 78 unidades de
altura pela cidade inteira. Medido antes de aplicar:

| Peça | Instâncias | Sobre um tronco? |
|---|---|---|
| `나뭇잎01` (folhagem, y −78..−39) | 22 | **nenhuma** — é canópia independente |
| `나무받침` (base de árvore, y 0) | 20 | **todas as 20**, a menos de 6 unidades |

Então a folhagem fica onde está, corretamente. As 20 bases **foram deixadas de
propósito**: remover não foi pedido, e base sob a ossada lê como o toco onde a
árvore estava. Reversível numa linha se ficar estranho.

### As poças — TENTADO E ABANDONADO. Não refazer.

**O `izlude.gnd` foi removido; o chão de Izlude está original de novo.**

O que se fez: como não existe modelo de poça no GRF (procurado `웅덩이`, `연못`,
`수면`, `개울` — zero) e o plano de água do `.rsw` é global (um nível para o mapa
inteiro, 45 em Izlude), a saída foi pintar o chão pela cor de superfície do
`.gnd`. Sete poças nos tiles mais baixos, andáveis e acima do nível da água.

**Por que não serviu, e é o ponto que interessa:** *"todas essas localizações já
tinham água embaixo"*. Izlude é cidade portuária construída sobre a água — o
chão andável mais baixo é justamente o que está sobre o mar ou colado nele.
Pintar poça ali não acrescenta nada, porque já se vê água.

O erro foi de premissa, não de execução. "Água empoça no ponto mais baixo" vale
para terreno fechado; num porto, o ponto mais baixo **é** o mar. A heurística
estava certa e o mapa é que não era o caso de uso.

Se um dia se quiser poça em Izlude, o caminho é **escolher os pontos a olho** —
praça, rua interna, pátio longe da orla — e não por altura. Em cidade de terra
firme a heurística por altura provavelmente funciona; aqui não.

A ferramenta `pocas.py` foi removida junto. Está no histórico do git
(commit `57f3b86`) se algum dia servir a outra cidade. O que ficou de útil foram
os acessores `superficie_topo()` e `altura_tile()` no `gnd.py` — antes o bloco
de cubos era blob opaco e não dava para achar a superfície de um tile.

---

## O inventário do GRF — 2026-07-31

O primeiro mapa-catálogo tinha **só os 90 modelos que Izlude já usa**. Servia
para conferir minha classificação, mas não mostra peça nova — dito depois de
olhar: *"vi muito pouco componente lá, são os elementos que Izlude mesmo tem"*.
Estava certo, e a limitação era do desenho do catálogo, não do acervo.

### O acervo real

| | |
|---|---|
| Modelos `.rsm` no GRF | **7034** |
| Pastas de modelo | 91 |
| O que o primeiro catálogo mostrava | 90 — **1,3%** |

As pastas maiores: `ilusion` (507), `rockridge` (420), `verus` (394),
`prontera_re` (276), `내부소품` (adereço de interior, 236), `모로코` (Morroc,
146), `글래스트` (Glast Heim, 116).

### As ruínas existem, e são de Morroc

Busca por termo de destruição no nome: **228 modelos em 25 pastas**, e
`model\모로코` sozinho tem **78**:

| Modelo | Quantos | O que é |
|---|---|---|
| `민가폐허01a` … `14e` | 24 | **ruínas de casa popular** |
| `성폐허101/102/103` | 3 | ruínas de castelo |
| `깨진벽1/2` | 2 | **parede quebrada** |
| `모로코폐가` | 1 | casa abandonada |
| `동물뼈*` | 5 | ossada |

Isso confirma a hipótese que estava aberta desde a análise inicial, mas **não
pelo caminho que se supunha**: o mapa `morocc` deste GRF usa `민가01a/01b/01c`,
que são as casas **inteiras**. Ou seja, é a Morroc pré-destruição, e os modelos
de ruína estão no GRF sem nenhum mapa que os use. Melhor assim — estão livres.

### Correção: o DES nunca bloqueou isto

Estava escrito aqui que inventariar modelo de ruína "provavelmente exige
terminar o DES, porque `.rsm` está atrás dele". **Errado, e por dois motivos
independentes:**

1. A **tabela** do GRF é zlib, não DES. O `grf.py` já lê nome, tamanho e flag de
   todos os 7034 modelos. O DES protege o *conteúdo* das entradas, não o índice.
2. Para pôr um modelo num mapa basta o **nome**: o `.rsw` referencia por
   caminho, e quem abre o `.rsm` é o cliente. Nunca precisei ler a geometria.

O DES só passa a importar se um dia formos **editar** um modelo. Para compor com
o que existe, é irrelevante. É a segunda vez que o DES é declarado bloqueio sem
ter sido medido.

### O catálogo de ruína

`@warp prt_fild08 106 206` cai no bloco de Morroc (nº 72 em diante). Os 228
modelos de ruína, agrupados por pasta, com as mesmas placas numeradas.

O `catalogo_ingame.py` agora aceita **duas fontes**, e a diferença é o ponto:

| Fonte | Dá o quê | Escala |
|---|---|---|
| Um **mapa** | o que aquele mapa já usa | real, clonada do exemplar |
| O **GRF** | o acervo inteiro, inclusive o que nenhum mapa nosso usa | 1, não há referência |

### Traduzir por morfema, não por nome inteiro

Rotular 228 modelos exigiria enumerar 228 traduções — e 7034 seria impossível.
A saída foi traduzir por **composição de morfema**: `민가폐허01a` vira
"casa ruina 01a" a partir de `민가` (casa) + `폐허` (ruína) + o sufixo. Com ~80
morfemas, 218 dos 228 saem legíveis.

O próprio catálogo diz o que falta no dicionário: onde o morfema é desconhecido
sai `?`, e foi lendo os `?` da primeira rodada que veio a segunda leva de
termos. **Ressalva:** morfema de uma sílaba (`성` castelo, `벽` parede, `문`
porta) pode casar dentro de outra palavra. O casamento é sempre pelo mais longo
primeiro, o que reduz mas não elimina. É rótulo de catálogo, não verdade.

### O limite honesto desta amostra

**Nenhuma casa está de fato quebrada.** Não existe modelo de casa destruída
sendo usado aqui — o que há é casa inteira, inclinada e afundada. Para "quase
todas destruídas" no sentido literal, o caminho é achar no GRF modelo de ruína
que já exista (`.rsm` de parede quebrada, viga, entulho) e **substituir** o
`filename` da instância, que é troca de string no `.rsw` e continua barata. Isso
depende do inventário do passo 2 abaixo, que ainda não foi feito.

Também não sei como isso ficou na tela: não tenho como ver. Precisa de
screenshot para fechar o laço, e os números da receita foram escolhidos por
raciocínio, não por observação. É esperado que precisem de ajuste.

---

## Arte de item de visual — o processo, fechado em 2026-07-31

**Funciona e está validado in-game** com o item 420047 (Costume Honorable Knight
Cloak). Esta seção é o roteiro para quando faltar arte de qualquer chapéu — o
caso que vai aparecer em série no dia em que os visuais entrarem numa loja.

### O sintoma e a leitura correta dele

Duas caixas de erro modais, e elas querem dizer coisas diferentes:

| Mensagem | O que é |
|---|---|
| `Spr :: Cannot find File : sprite\<item>\x.spr` | o arquivo não existe em lugar nenhum |
| `Resource File Loading fail` | **o arquivo existe e o cliente não chegou nele** — quase sempre nome de pasta errado no disco |

O segundo é o traiçoeiro. Custou uma rodada inteira: o `.bmp` estava lá, íntegro,
byte a byte idêntico a um que o cliente lê sem reclamar.

### Por que o servidor não acusa nada

As três tabelas concordam que o item existe e **nenhuma delas é a autoridade**:

- `rathena/db/re/item_db_equip.yml` — o item, com `View`;
- `SystemEN\LuaFiles514\itemInfo.lua` do ROenglishRE — o `identifiedResourceName`;
- `accessoryid.lub` do nosso GRF — o `View` mapeado para nome de sprite.

Quem discorda é o GRF, que não tem os arquivos. **Olhar tabela não detecta;
só testar arquivo detecta.** É por isso que existe o `valida_visual.py`.

### A fonte da arte já está nesta máquina

`C:\Program Files (x86)\Gravity Interactive, Inc\Ragnarok Brazil\data.grf` —
a instalação do bRO, 205117 entradas, mais nova que a nossa de 2021-11-03. As
entradas de sprite estão sem DES, então o `grf.py` lê direto e **o GRF Editor
não precisa entrar**. O `event.grf` da mesma pasta não é 0x200 e nosso leitor
não abre; são 5,6 MB de conteúdo de evento, improvável que tenha sprite.

### O ciclo

```
python valida_visual.py --id <n>                    # o que falta, dos 8 recursos
python instala_visual.py --id <n> --grf "<grf do bro>"
python valida_visual.py --id <n>                    # confere
```

E em lote, `--todos [--aplicar]`. Nada entra no GRF: os arquivos vão soltos para
`cliente\data\`, onde o `DataFolderFirst` os faz vencer. **Apagar reverte.**

### A armadilha que vai repetir: o nome da pasta no disco

O cliente é um app coreano que chama as APIs **ANSI** do Windows. Ele monta o
caminho em bytes CP949 e entrega para `CreateFileA`, que os interpreta na
codepage ANSI do sistema — cp1252 aqui. **O nome que ele procura no disco é o
mojibake**, `À¯ÀúÀÎÅÍÆäÀÌ½º`, não `유저인터페이스`. Dentro do GRF isso não
aparece, porque a tabela guarda os bytes crus; só no disco, que é onde o
`DataFolderFirst` nos põe.

Gravar com o nome coreano "correto" cria uma segunda pasta, invisível para o
cliente, ao lado da que funciona. Aconteceu com 5855 arquivos. A prova estava no
disco o tempo todo: **a pasta que o ROenglishRE criou e que funciona tem o nome
mojibake** — bastava olhar como as pastas que já funcionavam estavam nomeadas.

As ferramentas já tratam isso (`valida_visual.caminho_disco`). O registro aqui é
para qualquer coisa nova que escreva em `cliente\data\`.

### O estado, e o que a loja precisa saber

Dos 5301 itens de cabeça com `View` no `item_db`:

| | | serve para loja? |
|---|---|---|
| desenháveis | **3618** | **sim** |
| `View` fora do `accessoryid.lub` | 374 | não — sem cura por arte |
| a GRF do bRO não tem a arte | 101 | não hoje |
| a GRF do bRO tem só parte | 73 | não hoje |
| sem entrada no `itemInfo.lua` | 1135 | não conferido |

**O `--ok` do `valida_visual.py` é a lista de onde montar a loja.** Pôr item de
fora dela é entregar caixa de erro modal ao jogador.

Os **374 não têm cura por arte**: o cliente de 2021 não conhece aquele `View`,
então não sabe que slot desenhar. Resolver exigiria editar o `accessoryid.lub`,
que é outro problema e ainda não foi tentado.

Os **1135 sem `itemInfo`** são um balde separado e **não medido in-game** — sem
`identifiedResourceName` o cliente não tem nem nome de recurso para procurar.
Destes, 785 têm `View` que o cliente conhece e 350 não. Se um dia a loja quiser
alcançá-los, o caminho provável é acrescentar as entradas ao `itemInfo.lua`, que
é texto puro e editável. **Não tentado.**

---

## Ordem de trabalho proposta

Revisada em 2026-07-31, depois da amostra. Os passos 1, 3 e 5 da lista original
saíram: o DES não bloqueava, e clima e modelos já foram feitos juntos.

1. **Olhar Izlude in-game e calibrar.** Bloqueia todo o resto: os números da
   receita foram escolhidos no escuro, e não faz sentido propagar para outras
   cidades uma calibragem que ninguém viu. Ajustar é editar constante no topo do
   `destroi_mapa.py` e rodar de novo.
2. ~~**Inventariar o GRF** atrás de modelo de ruína.~~ **Feito em 2026-07-31**:
   7034 modelos, 228 com cara de ruína, 78 deles em Morroc — incluindo 24
   variantes de casa em ruínas. Não precisou do DES. Ver a seção do inventário.
3. **Olhar o catálogo de ruína e escolher as substitutas.** É o que transforma
   "casa inclinada" em "casa destruída" de verdade: trocar o `filename` da
   instância no `.rsw` por uma `민가폐허*`. Continua sendo edição de string, e o
   cliente carrega o resto.
4. **Estender a receita às outras cidades.** Cada uma precisa da sua lista de
   construções e adereços; o resto do script é genérico. Prontera fica fora.
5. **Textura de chão**, se a cor de superfície não bastar. É o passo mais caro e
   o único que custa memória — só entrar nele se o passo 1 mostrar que precisa.

---

## O que não foi verificado

Lista explícita, para ninguém tratar como fato. Atualizada em 2026-07-31 —
o que caiu para "medido" migrou para a seção da amostra.

- **se o mapa alterado abre e fica bom na tela.** É a única que importa agora:
  os arquivos passam nos parsers, mas parser satisfeito não é jogo bonito;
- se este cliente de 2021 desenha modelo com rotação arbitrária sem artefato —
  os destroços deitados a 90° são o teste;
- se o GRF de 2021-11-03 traz os ativos da Morroc destruída, e o que mais existe
  de modelo de ruína;
- quanto do GRF está atrás da flag DES (sabe-se que `.rsm` está, mapa não);
- se o `.rsw` 2.1 tem campos de névoa — **não** achei nenhum no layout, e o
  round-trip fecha sem eles, então provavelmente névoa nesta versão não vem do
  `.rsw`. Não investigado a fundo;
- se dá para inundar Izlude mexendo no nível da água (o campo existe e vale 45).
  Seria a assinatura mais literal da onda e custa um float, mas não sei em que
  sentido o valor cresce nem o que o cliente faz com terreno submerso.
