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

Medido no GRF: os arquivos de mapa estão **sem DES**.

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
| **Mapa-catálogo in-game** | a fazer | Plantar uma instância de cada modelo, numerada, em coordenada conhecida. Uma volta a pé e um print devolvem o índice visual inteiro. É o único que resolve de verdade, e vale para todas as cidades |

Um quarto caminho, mais caro e não iniciado: **renderizar os `.rsm` eu mesmo**
para gerar miniaturas e olhar sem intermediário. Exige o DES (os `.rsm` estão
atrás dele), um parser de `.rsm` e um rasterizador. É o único que me tornaria
autossuficiente.

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

## Ordem de trabalho proposta

Revisada em 2026-07-31, depois da amostra. Os passos 1, 3 e 5 da lista original
saíram: o DES não bloqueava, e clima e modelos já foram feitos juntos.

1. **Olhar Izlude in-game e calibrar.** Bloqueia todo o resto: os números da
   receita foram escolhidos no escuro, e não faz sentido propagar para outras
   cidades uma calibragem que ninguém viu. Ajustar é editar constante no topo do
   `destroi_mapa.py` e rodar de novo.
2. **Inventariar o GRF** atrás de modelo de ruína — parede quebrada, viga,
   entulho, casa danificada. É o que transforma "casa inclinada" em "casa
   destruída" de verdade, por troca do `filename` da instância. Provavelmente
   exige terminar o DES, porque `.rsm` está atrás dele.
3. **Estender a receita às outras cidades.** Cada uma precisa da sua lista de
   construções e adereços; o resto do script é genérico. Prontera fica fora.
4. **Textura de chão**, se a cor de superfície não bastar. É o passo mais caro e
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
