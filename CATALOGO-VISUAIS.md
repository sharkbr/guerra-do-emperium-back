# Catálogo de visuais — Mercado de Visuais

Os itens cosméticos que este cliente passou a desenhar em
2026-08-05, e que estão à venda a 1 zeny na quarta fileira do
quarteirão do Mercado Contemporâneo, em Prontera.

Gerado a partir de `ferramentas/varre_cosmeticos.py`. A loja em
`rathena/npc/guerra/mercado_de_visuais.txt`.

**Onze itens estão marcados com ★ e não saem da ferramenta.** Foram
pedidos a dedo — dez em 2026-08-05, o Disfarce de Jirtas em
2026-08-07 — e já desenhavam antes da rodada que montou estas lojas,
ou seja, o `varre_cosmeticos.py` os classifica como `ok` e não os
listaria. Regerar esta tabela pela ferramenta os perde — o porquê de
cada um está no cabeçalho do arquivo da loja.

**A rodada de 2026-08-07** mexeu nas três, e nenhuma das mudanças sai
da ferramenta tampouco:

- os doze NPCs do quarteirão viraram **mercador**, alternando homem e
  mulher — é por isso que os três `sprite` acima não são mais os de
  2026-08-05;
- entrou o **Disfarce de Jirtas** (20244) no Costumeiro;
- a **Piscadela de Freya** (410320) saiu do Camareiro e foi para o
  Adereceiro. Não foi só troca de vitrine: o item é `Costume_Head_Mid`
  no bRO e o nosso rAthena o dava como `Costume_Head_Low`, e a
  correção é um override em `db/guerra/item_db.yml`;
- saíram sete do Camareiro, a pedido: 20310, 31257 e os cinco balões
  (31421, 31422, 31423, 31424, 31429).

**A rodada de 2026-08-08** abriu a quarta loja da fileira, o
**Manteleiro** (`prontera 163,155`), com treze mantos cosméticos, e pôs
a **Glória Imperial** (420029) no Camareiro. Nenhum dos catorze sai da
ferramenta: foram pedidos item por item, e manto o `varre_cosmeticos.py`
nem classifica como curável — falta a metade dele que estende o
`spriterobeid.lub`.

Cinco dos treze não desenhavam neste cliente. O que faltava era arte, e
não tabela: os treze `View` (61 a 114) já estavam nas 120 entradas da
nossa `spriterobeid.lub`. Os 2925 arquivos de sprite de manto vieram da
GRF do bRO pelo `ferramentas/instala_manto.py`, escrito nesse dia — o
irmão do `instala_visual.py` para essa camada. **Cliente novo perde a
cópia**; a receita para repor está no cabeçalho da loja.

**A rodada de 2026-08-09** pôs **43 itens** nas quatro lojas — 18 no
Costumeiro, 8 no Adereceiro, 6 no Camareiro e 11 no Manteleiro —, todos
pedidos item por item e nenhum saindo de varredura. (Foram 47 no dia, mas
quatro caíram fora deste catálogo: três capas com cova foram para o
**Capeiro** e os Olhos Ilusórios para o **Ocleiro**, os dois no
`mercado_contemporaneo.txt`, porque são equipamento de verdade e não
visual — quem decide é o `Locations:` do `item_db`.)

**Foi a rodada que fechou a lacuna do manto.** Nove dos onze do Manteleiro
tinham `View` fora das 120 entradas da nossa tabela, e manto assim não
desenha por mais arte que se copie: o cliente nem chega a procurar
arquivo. O `ferramentas/estende_robeid.py` — escrito nesse dia, o irmão do
`estende_accessoryid.py` do lado do manto — levou a tabela a 129 slots. A
coluna `tabela` da lista do Manteleiro diz, item a item, qual dos dois
caminhos cada um usou.

**Uma peça mudou de loja no mesmo dia.** A Máscara de Minorous (21207)
veio na lista de topo e é `Costume_Head_Low`/`_Mid` no `item_db`, sem
`Head_Top` — no Costumeiro ela não equiparia no slot da placa. Foi para o
**Adereceiro**, onde equipa. É o mesmo motivo que moveu a Piscadela de
Freya em 2026-08-07, e a lição está no `CLAUDE.md` §4.14: **quem decide a
vitrine é o `Locations:` do `item_db`, não a lista do pedido.**

## Costumeiro — Costume topo (164 itens)

`prontera 151,155` — sprite `1_F_MERCHANT_01`

| id | nome |
|---|---|
| 15825 | Quepe Regional Preto |
| 15838 | Proteção de Vesper |
| 15841 | Capacete com Visores |
| 15842 | Cartola do Sumiço |
| 15846 | Selo do Artista de Verdade |
| 15847 | Boné Alado |
| 15851 | Coroa Realeza Gelada |
| 15854 | Cachecol Glorioso |
| 15875 | Diadema Élfico |
| 15888 | Garra do Dragão Demoníaco |
| 15893 | Solarium |
| 15925 | Boneco de Pouring |
| 15952 | Naga Tailandesa |
| 18740 | Cabelo de Super Saiadim |
| 19519 | Nuvem com Raios |
| 19598 | Elmo do Rei do Norte |
| 19602 | Chapéu Invisível ★ |
| 19630 | Coroa Valiosa |
| 19639 | Chapéu Rural |
| 19982 | Gorro de Noel |
| 19996 | Cavalo Rei ★ |
| 20135 | Coroa do Segredo |
| 20180 | Chapéu de Faroeste |
| 20183 | Presença Misteriosa |
| 20194 | Traje de Leão |
| 20234 | Máscara de Bafomé ★ |
| 20244 | Disfarce de Jirtas ★ |
| 20248 | Peruca de Saiadim |
| 20308 | Costume Koneko Hat |
| 20309 | Costume Dip Schmidt Helm |
| 20385 | Elmo do Herói |
| 21300 | Máscara do Guarda Leão |
| 21400 | Costume Blue Dragon Statue |
| 31108 | Balão de Fala (Abraços Grátis) |
| 31109 | Balão de Fala (Recruto para Clã) |
| 31110 | Balão de Fala (Procuro Grupo) |
| 31111 | Balão de Fala (Procuro Membros) |
| 31112 | Balão de Fala (Hue Hue Br) |
| 31156 | Costume Nut Shell |
| 31159 | Chapéu de Jormungand |
| 31172 | Cabeça de Glugluzão |
| 31177 | Chapéu Mãe Natureza |
| 31180 | Faixa do Shurão da Preula |
| 31324 | Fones da DJ Kitty |
| 31396 | Capuz Trevoso |
| 31409 | Elmo Reforçado |
| 31414 | Adorno de Câncer |
| 31419 | Tiara Flap Flap |
| 31501 | Fonte de Faíscas |
| 31535 | Chapéu de Titica |
| 31536 | Belzebu de Estimação |
| 31539 | Chapéu de Tapioca |
| 31557 | Gálea de Prata |
| 31558 | Gálea de Bronze |
| 31587 | Super Capacete de Kunlun |
| 31595 | Chapéu de Estudante |
| 31596 | Chapéu Biológico |
| 31597 | Chapéu de Peixinho |
| 31613 | Peruca do Super Saiadim Deus |
| 31665 | Poring Equilibrista |
| 31666 | Coroa de Cinzas |
| 31702 | Capuz de Felino Branco |
| 31722 | Gorrinho de Sedora |
| 31821 | Boné Estileira |
| 31890 | Adorno de Sagitário |
| 31897 | Elmo Submarino |
| 31935 | Chapéu de Dragonete Verde |
| 31950 | Cabeção de Esquilo |
| 31952 | Chapéu das Mil Dimensões |
| 400080 | Coroa do Renascimento |
| 400091 | Elmo Safira |
| 400092 | Chifres Luxuosos |
| 400093 | Chapéu de 18 Anos |
| 400131 | Diadema do Fogo Azul |
| 400133 | Visual do Éden |
| 400136 | Adorno dos Mil Ouros |
| 400143 | Asas de Asgard |
| 400158 | Coroa do Mal |
| 400166 | Capacete Aquático |
| 400167 | Chapéu Espanta Mosquitos |
| 400168 | Coroa de Izlude |
| 400175 | Chapéu Fogueira |
| 400195 | Pizza Tamanho Família com Borda Recheada |
| 400205 | Aplique de Coque Celeste |
| 400206 | Aplique de Coque Cereja |
| 400207 | Aplique de Coque Loiro |
| 400208 | Aplique de Coque Verde |
| 400209 | Aplique de Coque Preto |
| 400210 | Aplique de Coque Platinado |
| 400211 | Aplique de Coque Marrom |
| 400212 | Aplique de Coque Lilás |
| 400221 | Diadema de Jasper |
| 400224 | Boina Militar |
| 400225 | Capa Coelho Felpudo |
| 400232 | Homem de Neve |
| 400253 | Chapéu Doceria |
| 400271 | Utensílios de Jardim |
| 400272 | Coroa das Cem Flores |
| 400277 | Chapéu de Tarlock |
| 400278 | Ômega Faxineira |
| 400290 | Tiara Rosa de Anjo |
| 400309 | Chapéu do 20º Aniversário |
| 400310 | Tiara Alada |
| 400311 | Elmo do Arcanjo |
| 400313 | Tiara Galática |
| 400314 | Joia do Norte |
| 400321 | Gorro da Fada Vanda |
| 400343 | Chapéu de Bambu de Raposa |
| 400351 | Capacete de Proteção Porin GG |
| 400354 | Elmo de Vanargandr |
| 400355 | Gorro Bufante |
| 400356 | Quepe do Pô Pai |
| 400357 | Elmo do Dragão de Ouro |
| 400358 | Elmo do Dragão de Prata |
| 400370 | Chapéu de Bruxa com Orelhas |
| 400398 | Boina Alada Branca |
| 400402 | Bolo de Angeling |
| 400405 | Cartola do Arcanista |
| 400406 | Doces Cativantes |
| 400407 | Orelhas do Coelho Negro |
| 400424 | Cartola do Visconde Coruja |
| 400426 | Touca de Transformacento |
| 400428 | Ovo do Coelho da Páscoa |
| 400429 | Elmo de Montanhista |
| 400430 | Boina Verde e Amarela |
| 400431 | Chapéu Floral de Druida |
| 400432 | Gorro de Sansan Branco |
| 400435 | Chapéu do Chapeleiro |
| 400436 | Orelhonas de Piamette |
| 400439 | Beijo do Guardião |
| 400448 | Chapéu Juan |
| 400450 | Leão Rei |
| 400458 | Faixa da Preula Azul |
| 400460 | Proeminência Solar |
| 400462 | Quepe Náutico |
| 400466 | Peruca de Pipoca Colorida |
| 400480 | Gatopéu de Palha |
| 400496 | Orelhinhas Atentas Albinas |
| 400497 | Gorro da Fada Cosmos |
| 400502 | [Visual] Anel |
| 400517 | Tiara de Maçã Envenenada |
| 400567 | Mitra do Alvorecer |
| 400585 | Hominho de Neve |
| 400588 | Chapéu de Sacoleiro |
| 400594 | Cartola do Aparecimento |
| 400596 | Trufa Derretida |
| 400604 | Boina de Gato Preto |
| 400633 | Chapéu Multiclasse Azul |
| 400634 | Lacinhos Oníricos |
| 400635 | Chapéu de Malha |
| 400656 | Elmo Branco da Khalitzburg |
| 400664 | Fei-Chai Dorminhoco |
| 400671 | Ovo Frito |
| 400684 | Orelhas de Jerboa |
| 400692 | Chapéu de Peônia Dourada |
| 400693 | Chapéu de Peônia Vermelha |
| 400703 | Chapéu do Oráculo Sombrio |
| 400708 | Quepe Branco do Serumaninho |
| 430001 | Elmo do Clã |
| 430005 | Óculos do Tigre Branco |
| 440001 | Caixa Surpresa do Vário |
| 440004 | Elmo Antigo |
| 440005 | Coroa do Diabo |
| 440012 | Máscara de Eggman |

## Adereceiro — Costume meio (124 itens)

`prontera 155,155` — sprite `4_M_HUMERCHANT`

| id | nome |
|---|---|
| 15840 | Óculos de Bioproteção |
| 15953 | Carrinho do Zé |
| 18742 | Luar de Cristal |
| 19551 | Símbolo Élfico |
| 19554 | Máscara Tradicional |
| 19603 | Óculos Invisíveis ★ |
| 19638 | Sr. Sorriso |
| 19801 | Máscara da ANBU |
| 20286 | Óculos da Persona |
| 20397 | Máscara de Jakk |
| 21200 | Lágrimas Masculinas |
| 21207 | Máscara de Minorous |
| 31118 | Máscara do Vilão |
| 31462 | Brincos de Poring Rosa |
| 31515 | Gatinho Curioso |
| 31949 | Asas de Diabolus |
| 31953 | Fone de Ouvido Brilhante |
| 31954 | Coleira do Vassalo |
| 400491 | Faixa Brasileira |
| 410011 | Venda Sombrosa |
| 410030 | Trancinhas Azuis |
| 410031 | Trancinhas Vermelhas |
| 410032 | Trancinhas Amarelas |
| 410033 | Trancinhas Verdes |
| 410034 | Trancinhas Pretas |
| 410035 | Trancinhas Brancas |
| 410036 | Trancinhas Marrons |
| 410037 | Trancinhas Roxas |
| 410038 | Trançado Azulado |
| 410039 | Trançado Avermelhado |
| 410040 | Trançado Amarelado |
| 410041 | Trançado Esverdejado |
| 410042 | Trançado Escurecido |
| 410043 | Trançado Branquinho |
| 410044 | Trançado Bronzeado |
| 410045 | Trançado Roxinho |
| 410047 | Máscara do Homem de Alumínio |
| 410053 | Óculos de Sol Estiloso |
| 410059 | Máscara de Carniçal |
| 410060 | Aura de Morceguinhos |
| 410072 | Drones Vigilantes |
| 410074 | Venda de Sicário |
| 410098 | Máscara de Nero |
| 410111 | Mecha Azul |
| 410112 | Mecha Vermelha |
| 410113 | Mecha Loira |
| 410114 | Mecha Verde |
| 410115 | Mecha Castanho Escuro |
| 410116 | Mecha Branca |
| 410117 | Mecha Castanho Claro |
| 410118 | Mecha Lilás |
| 410121 | Meda Elmo |
| 410128 | Microfone de Mecânico |
| 410131 | Mascote Tigre Branco |
| 410132 | Mascote Tigre Negro |
| 410133 | Cookie & Biju |
| 410144 | Carrinho Ômega |
| 410156 | Buquê Colorido |
| 410157 | Lunáticos Amiguinhos |
| 410160 | Globo Celestial |
| 410178 | Headset de Angeling |
| 410179 | Headset de Deviling |
| 410182 | Chapéu de Lanterna do Viajante |
| 410196 | Lacinhos Orientais Amarelos |
| 410198 | Devirugangue |
| 410199 | Vela da Meia-Noite |
| 410200 | Coelho Serviçal das Maravilhas |
| 410201 | Caveiras Místicas |
| 410202 | Lambreta Elétrica do Poring |
| 410212 | Rei Dragão Bebê |
| 410217 | Cartas Mágicas |
| 410218 | Bola de Capotão |
| 410219 | Coelho Grandão |
| 410220 | Piscadela Congelante |
| 410224 | Lacinhos Vermelhos da Papisa |
| 410226 | Coelho Viena |
| 410234 | Relógio Insurgente |
| 410236 | Castiçal de Pajem |
| 410240 | Coelho Chinês |
| 410242 | Ornamento da Valquíria |
| 410245 | Olhar 43 |
| 410248 | Tuk Tuk |
| 410251 | Óculos de Alien Azul |
| 410252 | Óculos de Alien Vermelho |
| 410253 | Óculos de Alien |
| 410261 | Costume King Poring Headphones |
| 410262 | [Visual] Sonic |
| 410263 | [Visual] Super Sonic |
| 410264 | [Visual] Tails |
| 410277 | [MEGA] Gato |
| 410278 | Pupilas Avermelhadas |
| 410286 | Olho de Zauron |
| 410289 | Pesarinho |
| 410290 | Água-Viva |
| 410296 | Tollynho |
| 410297 | Pupilas Draconianas |
| 410311 | Diadema de Górgona |
| 410316 | Quiosque do Ursinho |
| 410317 | Máscara para Dormir |
| 410320 | Piscadela de Freya |
| 410326 | A-Ji Agitado |
| 410328 | Padaria Móvel |
| 410329 | Tambores de Invocação da Terra |
| 410330 | Tambores de Invocação do Fogo |
| 410331 | Tambores de Invocação do Vento |
| 410338 | Costume Sun God |
| 410351 | Guarda-Sol Azul |
| 410352 | Guarda-Sol Vermelho |
| 410353 | Olhos Chocados |
| 410357 | Bombaim de Ombro |
| 410359 | [MEGA] Cão |
| 410361 | Curativo Ocular |
| 410364 | Fone de Ouvido Cintilante |
| 420293 | Peruca Turquesa da Caçadora |
| 420294 | Peruca Loira da Caçadora |
| 420295 | Peruca Rosa da Caçadora |
| 420296 | Peruca Azul da Caçadora |
| 420297 | Peruca Violeta da Caçadora |
| 420298 | Peruca Morena da Caçadora |
| 420299 | Peruca Branca da Caçadora |
| 420300 | Peruca Marrom da Caçadora |
| 436008 | Fantasia de Tigre Branco |
| 436010 | Cabeça de Tarantuling |
| 480200 | Asas do Anjo Fiel |

## Camareiro — Costume baixo (123 itens)

`prontera 159,155` — sprite `1_F_MERCHANT_02`

| id | nome |
|---|---|
| 15954 | Espaguete & Lasanha |
| 19604 | Máscara Invisível ★ |
| 20798 | Traje do Ceifeiro |
| 31305 | Angeling de Estimação |
| 31386 | Orbes Místicos |
| 31490 | Cachecol de Poring |
| 31500 | Costume Sparkler Stick |
| 31503 | Deviling de Estimação |
| 31584 | Cachecol de Marin |
| 31593 | Lenço do Deserto |
| 31594 | Lápis de Cor Vermelho |
| 31698 | Chapéuzinho Carmesinho |
| 31700 | Cachecol dos Corajosos |
| 31735 | Gargalheira de Yawata |
| 31882 | Espetinho de Chocolate |
| 31932 | Gravata-Paletó |
| 400258 | Peruca Ondulada de Jade |
| 400327 | Peruca Estilosa Rosa |
| 400425 | Flauta de Falcão |
| 400427 | Cabelos de Freya |
| 410265 | [Visual] Anéis |
| 420014 | Peruca de Animação |
| 420026 | Gravata Bombom |
| 420029 | Glória Imperial ★ |
| 420044 | Gola Escolar de Marujo ★ |
| 420046 | Manta Digníssima ★ |
| 420047 | Capa de Cavaleiro ★ |
| 420054 | Cachecol de Fumacento ★ |
| 420070 | Capuz Macabro |
| 420071 | Cachecol com Tiras ★ |
| 420083 | Cachecol com Laço Creme |
| 420085 | Peruca Kururinpa Platinada |
| 420086 | Cacheado Marrom |
| 420091 | Peruca Sedosa Loira |
| 420104 | Cabelos Longos Azulados |
| 420107 | Peruca Três Cores |
| 420113 | Penteado Estiloso Moreno |
| 420114 | Penteado Estiloso Verde |
| 420115 | Penteado Estiloso Castanho |
| 420116 | Penteado Estiloso Rosa |
| 420117 | Penteado Estiloso Roxo |
| 420118 | Penteado Estiloso Ruivo |
| 420119 | Penteado Estiloso Branco |
| 420120 | Penteado Estiloso Loiro |
| 420121 | Peruca Longa Selvagem Preta |
| 420122 | Peruca Longa Selvagem Verde |
| 420123 | Peruca Longa Selvagem Castanha |
| 420124 | Peruca Longa Selvagem Rosa |
| 420125 | Peruca Longa Selvagem Roxa |
| 420126 | Peruca Longa Selvagem Ruiva |
| 420127 | Peruca Longa Selvagem Branca |
| 420128 | Peruca Longa Selvagem Loira |
| 420132 | Pequena Natureza Grandiosa |
| 420133 | Peruca Colorida Estelar |
| 420140 | Peruca de Alpha |
| 420150 | Peruca Duas Cores |
| 420151 | Aura da Luz e Escuridão |
| 420152 | Costume Master of Light and Darkness |
| 420156 | Peruca Florida |
| 420161 | Peruca Rosa Estelar |
| 420162 | Peruca Preta Estelar |
| 420163 | Cachecol de Corvo |
| 420165 | Tenda Preciosa |
| 420170 | Peruca Sedosa Morena |
| 420172 | Peruca Anil de Trancinhas |
| 420181 | Ombreira de Brinaranha |
| 420191 | Penteado Coelho das Neves |
| 420192 | Raposa Albina |
| 420193 | Cachecol com Lacinho |
| 420197 | Cabelo Dupla Cor |
| 420207 | Peruca da Rosa Eterna |
| 420208 | Peruca Trançada de Chocolate |
| 420209 | Fita da Confeiteira Mágica |
| 420211 | Ovelha Dorminhoca |
| 420212 | Cachecol Infernal |
| 420218 | Peruca Ondulada de Platina |
| 420219 | Picolé de Melão |
| 420221 | Peruca de Skia |
| 420232 | Espetinho de Queijo |
| 420233 | Penteado Rosa da Diva |
| 420237 | Cachecol Tigroso |
| 420241 | Peruca de Jujuba Rosa |
| 420254 | Bigode Mágico |
| 420255 | Peruca Sicária Marrom |
| 420264 | Peruca Branca do Meio-Youkai |
| 420273 | Penteado Ondulado Loiro |
| 420274 | Penteado Ondulado Loiro Rosado |
| 420275 | Penteado Ondulado Prateado |
| 420276 | Penteado Ondulado Azul Prateado |
| 420277 | Corte Joãozinho Turquesa |
| 420278 | Corte Joãozinho Loiro |
| 420279 | Corte Joãozinho Rosa |
| 420280 | Corte Joãozinho Azul |
| 420281 | Corte Joãozinho Roxo |
| 420282 | Corte Joãozinho Moreno |
| 420283 | Corte Joãozinho Prata |
| 420284 | Corte Joãozinho Grisalho |
| 420285 | Peruca Turquesa da Engenheira |
| 420286 | Peruca Loira da Engenheira |
| 420287 | Peruca Rosa da Engenheira |
| 420288 | Peruca Azul da Engenheira |
| 420289 | Peruca Violeta da Engenheira |
| 420290 | Peruca Morena da Engenheira |
| 420291 | Peruca Branca da Engenheira |
| 420292 | Peruca Marrom da Engenheira |
| 420303 | Esmeraldas do Caos |
| 420305 | Mini Tentáculo |
| 420307 | Peruca da Princesa Mestiça |
| 420317 | Peruca Trançada de Baunilha |
| 420320 | Pequeno Vento Bruto |
| 420321 | Peruca Longa de Neon |
| 420340 | Kombi do Lanche |
| 420341 | Peruca de Coque Loiro |
| 420344 | Costume Book of Sorcery |
| 420345 | Peruca do Laço Trançado |
| 420347 | Rosa Gótica |
| 420349 | Kit de Praia Azul |
| 420350 | Kit de Praia Verde |
| 420353 | Peruca de Rabo Duplo |
| 420357 | Bebê Foca |
| 420359 | Costume Catbell |
| 420360 | Peruca do Sino Felino |
| 490242 | Cabelo de Valquíria |

## Manteleiro — Costume capa (24 itens)

`prontera 163,155` — sprite `1_M_MERCHANT`

Aberta em 2026-08-08 com treze; onze entraram em 2026-08-09.
Os vinte e quatro foram pedidos item por item e **nenhum sai de
varredura** — ver a nota da rodada, no topo.

**São DUAS camadas, e as duas colunas dizem uma cada.** `arte` é de onde
veio a sprite de manto por classe: `GRF` significa que este cliente já a
tinha; `bRO` que ela foi copiada pelo `instala_manto.py`, e que um cliente
novo precisa da cópia de novo. `tabela` é o `spriterobeid.lub`, que traduz
o `View` no nome da pasta: `GRF` são os que cabiam nas 120 entradas de
2021-11-03; **`override`** são os nove que só passaram a existir com o
`estende_robeid.py`, em 2026-08-09.

**As duas se perdem num cliente novo, e em ordem.** Repor é rodar
`estende_robeid.py` e só depois `instala_manto.py` — invertido, o segundo
recusa.

| id | nome | view | arte | tabela |
|---|---|---|---|---|
| 20612 | Escudo de Oridecon | 90 | bRO | GRF |
| 480055 | Asas Encantadas de Rudra | 72 | bRO | GRF |
| 480056 | Asas Amaldiçoadas de Arcanjo | 73 | GRF | GRF |
| 480058 | Asas Áureas de Arcanjo | 75 | GRF | GRF |
| 480069 | Asas Encantadas de Arcanjo | 61 | GRF + bRO | GRF |
| 480071 | Recipiente das Areias | 82 | GRF + bRO | GRF |
| 480096 | Casaco Aconchegante | 99 | bRO | GRF |
| 480097 | Aura Nevada | — | não veste | — |
| 480107 | Espadas Cruzadas | 104 | GRF | GRF |
| 480110 | Mochila do Doram Aventureiro | 107 | GRF + bRO | GRF |
| 480117 | Guitarra de Rockstar | 108 | bRO | GRF |
| 480118 | Espada do General | 114 | bRO | GRF |
| 480121 | Asas Orientais | 111 | bRO | GRF |
| 480122 | Asas Carnavalescas | 112 | GRF | GRF |
| 480127 | Chapéu Pendurado de Palha | 115 | bRO | GRF |
| 480155 | Capa de Herói | 122 | bRO | **override** |
| 480169 | Guitarra de Deviling | 125 | bRO | **override** |
| 480189 | Asas Amaldiçoadas de Valquíria | 131 | bRO | **override** |
| 480198 | Asas Laureadas | 136 | bRO | **override** |
| 480207 | Mochila Multiuso | 137 | bRO | **override** |
| 480223 | Muranyasa | 147 | bRO | **override** |
| 480235 | Tridente com Lacinho | 148 | bRO | **override** |
| 480237 | Katanas do Mestre Tengu | 158 | bRO | **override** |
| 480246 | Lança de Valquíria | 154 | bRO | **override** |

**A Aura Nevada não é manto.** Ela não tem `View`: o que ela faz é um
`hateffect` (`HAT_EF_SNOW_POWDER`) no `Script` do item — efeito de tela,
não desenho vestido. Está na loja de propósito, e o `instala_manto.py`
a recusa dizendo exatamente isso. Não confundir com os três
"Invisíveis" das outras lojas, em que o nada é o produto: aqui o
produto é a neve, e ela aparece.
