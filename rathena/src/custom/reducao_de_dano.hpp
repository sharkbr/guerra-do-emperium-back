// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// A REDUCAO POR RACA FECHA A CONTA
// ================================
//
// O que este arquivo faz: por o `percentAtk` - a parcela de dano que nasce do
// `bonus bAtkRate` da ARMA DO ATACANTE - dentro da reducao de cartas do alvo,
// junto com todas as outras parcelas. Sem isso ele sai inteiro, ignorando
// resistencia a raca, a elemento, a tamanho e a classe de uma vez so.
//
// --------------------------------------------------------------- o problema
//
// No renewal o dano fisico e montado em parcelas, e a reducao do alvo e
// aplicada em cada uma antes de somar (src/map/battle.cpp, no bloco
// "Card Fix for target"):
//
//     wd.statusAtk  += battle_calc_cardfix(...);   // reduzida
//     wd.weaponAtk  += battle_calc_cardfix(...);   // reduzida
//     wd.equipAtk   += battle_calc_cardfix(...);   // reduzida
//     wd.masteryAtk += battle_calc_cardfix(...);   // reduzida
//     ...
//     wd.damage = wd.statusAtk + wd.weaponAtk + wd.equipAtk + wd.percentAtk;
//
// O `percentAtk` nao esta na lista, e entra na soma inteiro. Ele e calculado
// bem antes, em `battle_calc_weapon_attack` (o trecho comentado como
// "AtkRate gives a static bonus from (W.ATK + E.ATK)"):
//
//     wd->percentAtk = (wd->weaponAtk + wd->equipAtk) * sd->bonus.atk_rate / 100;
//
// Como tudo que vem depois da soma e MULTIPLICATIVO (P.ATK, taxa de critico,
// curta/longa distancia e, por ultimo, o multiplicador da habilidade), reduzir
// as parcelas antes da soma da exatamente o mesmo resultado que reduzir no
// fim - **desde que toda parcela passe pela reducao**. A unica que nao passava
// era essa. Entao a reducao nao fechava a conta: ela fechava a conta de tudo,
// menos de uma fatia proporcional ao ATQ% do atacante.
//
// ------------------------------------------------------------ quanto custava
//
// Medido em 2026-08-09, na arena, com um Sura somando 110% de resistencia a
// humano (soma conferida peca a peca no item_db, incluindo os conjuntos
// Cocar do Orc Heroi + Carta Guerreiro Orc e Carta Caidos + Carta Guerreiro
// Orc): o Rune Knight, SEM NENHUM equipamento alem da arma, acertou 53.061
// com Impacto Flamejante. As quatro parcelas reduzidas iam a zero, como se
// esperava - e sobrava o `percentAtk`.
//
// A arma era a Lamina Sagrada (`Copy_Gram`, 500009) em +16:
//
//     if (BaseLevel>=100) { bonus bAtkRate,10*.@r; }    ->  bAtkRate 160
//
// Ou seja, `percentAtk` valia 1,6x (W.ATK + E.ATK) e passava intocado. Com
// 110% de resistencia o alvo tomava perto de 60% do dano que tomaria com
// resistencia nenhuma. Uma arma dessas e um "ignora reducoes" disfarcado de
// ATQ%, e nada no log denuncia.
//
// ------------------------------------------------------ o que NAO muda aqui
//
// Dano fixo somado DEPOIS da conta continua fora da reducao, de proposito - e
// o caso da Lamina de Aura (`SC_AURABLADE`) e dos outros `ATK_ADD` que a
// habilidade explicita como acrescimo fixo. A regra e: bonus multiplicativo
// entra na conta e a reducao fecha; dano fixo declarado como fixo fica fora.
//
// Tambem ficam de fora o NJ_ISSEN e o GN_FIRE_EXPANSION_ACID: o rAthena pula
// a reducao do alvo para os dois no bloco de parcelas e a aplica mais tarde,
// sobre o `wd.damage` inteiro - que ja inclui o `percentAtk`. Esses dois,
// portanto, nunca tiveram o furo.
//
// ------------------------------------------------------------- por que em src
//
// Nao ha como corrigir isto por db/, conf/ ou script: a ordem das parcelas so
// existe no C++. O enxerto no arquivo do rAthena e um include e uma chamada,
// no padrao do src/custom/refino.hpp.

#ifndef CUSTOM_REDUCAO_DE_DANO_HPP
#define CUSTOM_REDUCAO_DE_DANO_HPP

#include <bitset>

#include <common/cbasetypes.hpp>

#include <map/battle.hpp>
#include <map/map.hpp>

#ifdef RENEWAL

/// Passa o `percentAtk` pela reducao de cartas do alvo, do mesmo jeito e no
/// mesmo lugar em que o rAthena ja passa weaponAtk e equipAtk.
///
/// Usa o `nk` cheio (e nao o `ignoreele_nk` que o statusAtk usa) porque o
/// percentAtk nasce de weaponAtk + equipAtk, que sao parcelas COM elemento -
/// o `battle_attr_fix` ja rodou nas duas antes desta conta. Tratar diferente
/// faria a resistencia a elemento valer para o ATQ da arma e nao valer para a
/// porcentagem tirada dele.
///
/// @param wd Dano em montagem
/// @param src Atacante
/// @param target Alvo
/// @param nk Flags de "ignora ..." da habilidade
/// @param ele_direita Elemento da mao direita
/// @param ele_esquerda Elemento da mao esquerda
/// @param mao_esquerda O ataque tambem usa a mao esquerda?
inline void reducao_alcanca_percentatk(struct Damage& wd, block_list* src, block_list* target,
	std::bitset<NK_MAX> nk, int32 ele_direita, int32 ele_esquerda, bool mao_esquerda)
{
	wd.percentAtk += battle_calc_cardfix(BF_WEAPON, src, target, nk, ele_direita, ele_esquerda, wd.percentAtk, 0, wd.flag);

	if (mao_esquerda)
		wd.percentAtk2 += battle_calc_cardfix(BF_WEAPON, src, target, nk, ele_direita, ele_esquerda, wd.percentAtk2, 1, wd.flag);
}

#endif /* RENEWAL */

#endif /* CUSTOM_REDUCAO_DE_DANO_HPP */
