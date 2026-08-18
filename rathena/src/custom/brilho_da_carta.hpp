// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// O BRILHO (E O SOM) QUANDO CAI UMA CARTA
// =======================================
//
// O que este arquivo faz: dar as CARTAS o pilar de luz roxo e o barulho que o
// bRO fazia quando uma carta caia no chao. Pedido do dono em 2026-08-17.
//
// -------------------------------------------------- quem desenha o que
//
// Nada disto e arte nossa e nada disto precisa de patch de cliente: os cinco
// pilares ja estao no data.grf de 2021-11-03, com o som ao lado -
//
//   data\texture\effect\new_dropitem\dropitem_purple\...\dropitem_purple.str
//   data\wav\effect\drop_purple.wav
//
// (e os irmaos _blue, _green, _pink e _red). Quem os liga e um campo do
// pacote de queda de item, o ZC_ITEM_FALL_ENTRY5 (0x0ADD): `showdropeffect` e
// `dropeffectmode`. O servidor manda o numero, o cliente acha o efeito e o
// wav sozinho. Ou seja: isto vale para quem ja instalou o jogo, sem
// atualizacao nenhuma do lado dele.
//
// ---------------------------------------------- por que src e nao db/
//
// O rAthena ja sabe fazer isso por item: `Flags: DropEffect:` no item_db
// (src/map/itemdb.cpp:729). O caminho de db/ existe e funciona - so nao serve
// AQUI, por dois motivos:
//
//   1. Sao mais de cinco mil cartas. O override teria uma entrada para cada,
//      e seria o maior arquivo de db/guerra por uma ordem de grandeza.
//   2. Ele nasceria desatualizado. Carta que entre depois - do upstream, de
//      um evento, de um item novo nosso - ficaria sem brilho, calada, ate
//      alguem lembrar de rodar o gerador de novo. A regra e "toda carta", e
//      "toda carta" se escreve uma vez.
//
// Aqui a regra e o TIPO do item (IT_CARD), entao carta nova ja nasce
// brilhando.
//
// ------------------------------------------- o item continua mandando
//
// Item que peca um PILAR ESPECIFICO no item_db nao e tocado - dar outra cor a
// uma carta continua sendo coisa de db/, sem mexer em codigo.
//
// MAS `DROPEFFECT_CLIENT` NAO CONTA COMO PEDIDO, e essa distincao e a razao
// de este arquivo ter nascido errado. `CLIENT` (o valor 1) quer dizer "decide
// voce, cliente" - e o cliente de 2021-11-03 decide nao desenhar nada. O
// vendor traz `DropEffect: CLIENT` em 1882 itens, quase toda carta inclusive,
// entao tratar qualquer valor nao-zero como escolha do item desligava a regra
// inteira, em silencio. A guarda e `> DROPEFFECT_CLIENT`, nao `!= NONE`.
//
// --------------------------------------------------- por que battle_config
//
// A cor e `brilho_da_carta` em conf/guerra/battle_guerra.txt, e nao um numero
// cravado aqui, para trocar com `@reloadbattleconf` em vez de recompilar. 0
// desliga e devolve o comportamento do rAthena.
//
// ------------------------------------------------------ o que NAO alcanca
//
// So a queda de MONSTRO. O `canShowEffect` do `map_addflooritem` e `!loot`
// (src/map/mob.cpp:2540): item que o monstro pegou do chao e devolveu na
// morte nao brilha, e item largado por jogador (`pc_dropitem`) tambem nao -
// aquele parametro nasce `false` (src/map/map.hpp:1178). Isso e do rAthena e
// e o que se quer: brilho de carta caindo, nao brilho de carta no chao.

#ifndef CUSTOM_BRILHO_DA_CARTA_HPP
#define CUSTOM_BRILHO_DA_CARTA_HPP

#include <common/cbasetypes.hpp>
#include <common/mmo.hpp>

#include <map/battle.hpp>
#include <map/itemdb.hpp>

/// Devolve o modo de efeito de queda que o pacote deve levar.
///
/// `efeito_do_item` e o que o item_db pediu (`itemdb_dropeffect`). Se ele ja
/// disse alguma coisa, e ele que vale; so o vazio e preenchido.
inline uint8 brilho_da_carta(t_itemid nameid, uint8 efeito_do_item) {
	// So o pedido de um PILAR ESPECIFICO manda aqui.
	//
	// `DROPEFFECT_CLIENT` (1) NAO e escolha de cor: e "decide voce, cliente"
	// - e este cliente de 2021-11-03 decide nao desenhar nada. Ler aquele 1
	// como "o item ja resolveu" era o que apagava o brilho de TODA carta, em
	// silencio: 1882 itens do vendor declaram `DropEffect: CLIENT`, e quase
	// toda carta esta entre eles (db/re/item_db_etc.yml). Medido em
	// 2026-08-17 com sonda no proprio caminho, depois de tres hipoteses
	// erradas - ver HISTORICO.md.
	if (efeito_do_item > DROPEFFECT_CLIENT)
		return efeito_do_item;

	// 0 desliga a regra e devolve o rAthena.
	if (battle_config.brilho_da_carta <= 0)
		return efeito_do_item;

	// `itemdb_search` nunca devolve nulo - item desconhecido cai no registro
	// falso, cujo `type` e IT_ETC. Por isso nao ha checagem de ponteiro.
	if (itemdb_search(nameid)->type != IT_CARD)
		return efeito_do_item;

	return static_cast<uint8>(battle_config.brilho_da_carta);
}

#endif /* CUSTOM_BRILHO_DA_CARTA_HPP */
