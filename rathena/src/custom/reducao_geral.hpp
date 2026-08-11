// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// A REDUCAO GERAL DE DANO NOS MAPAS `pvp`
// =======================================
//
// O que este arquivo faz: aplicar nos mapas com mapflag `pvp` - a Arena de
// Combate de Prontera (`pvp_n_1-5`) na frente de todos - a MESMA reducao de
// dano final que o rAthena ja aplica nos mapas de guerra. E o pedido de
// 2026-08-10: o bRO reduzia 70% do dano final na Guerra do Emperium, decidido
// com a comunidade quando os danos ficaram altos demais, e a mesma conta passa
// a valer para o nosso PvP.
//
// ------------------------------------------------------------ o problema
//
// A metade da guerra e configuracao pura: o rAthena tem
// `gvg_weapon_attack_damage_rate` e as quatro irmas dela
// (conf/battle/guild.conf), aplicadas por `battle_calc_gvg_damage`
// (src/map/battle.cpp) em todo mapa `mapdata_flag_gvg2`. Baixar os cinco para
// 30 no conf/guerra/battle_guerra.txt resolve a guerra sem uma linha de C++.
//
// A metade do PvP NAO TEM equivalente. O rAthena tem os cinco
// `pk_*_attack_damage_rate` (conf/battle/misc.conf), que fazem exatamente isto
// e sao inclusive checados contra o mapflag `pvp`:
//
//     if (battle_config.pk_mode == 1 && map_getmapflag(bl->m, MF_PVP) > 0)
//         damage = battle_calc_pk_damage(*src, *bl, damage, skill_id, flag);
//
// So que eles estao trancados atras do `pk_mode`, e `pk_mode` NAO E uma opcao
// de reducao de dano - e o "servidor PK inteiro". Ligar o `pk_mode` faz o
// src/map/map.cpp:3791 marcar TODO MAPA como `pvp`:
//
//     if( battle_config.pk_mode && !mapdata_flag_vs2(mapdata) )
//         mapdata->setMapFlag(MF_PVP, true); // make all maps pvp for pk_mode
//
// e ainda arrasta consigo penalidade de morte por jogador, EXP extra por
// diferenca de nivel, `pk_min_level`, `pk_level_range` e o sumico da UI de PvP
// (src/map/clif.cpp:10836). Ou seja: para reduzir dano na arena, o rAthena
// pede que a cidade inteira vire campo aberto. Nao serve.
//
// Dai este arquivo: os mesmos cinco multiplicadores, com nome nosso, ligados ao
// mapflag `pvp` e a nada mais.
//
// ----------------------------------------------- NINGUEM ESCAPA (2026-08-10)
//
// A primeira versao deste arquivo, do mesmo dia, respeitava as duas isencoes que
// o rAthena da para a reducao de guerra. O dono cortou isso na volta, com a
// palavra que decide: "quero que TODOS os danos de pvp entrem nessa categoria".
//
// As duas isencoes eram o `INF2_IGNOREGVGREDUCTION` - `NJ_ZENYNAGE` (Chuva de
// Moedas) e `GN_FIRE_EXPANSION_ACID`, as unicas duas do renewal com
// `IgnoreGvgReduction: true` no db/re/skill_db.yml. Elas passam a ser reduzidas
// como todo o resto, e nao so aqui: o `reducao_isenta_habilidade()` abaixo e
// enxertado TAMBEM no `battle_calc_gvg_damage` do rAthena, para a guerra fazer
// igual. Sem esse segundo enxerto a Chuva de Moedas ficaria valendo CINCO VEZES
// o dano de qualquer outra habilidade dentro do castelo - com 80% de reducao a
// unica que escapa nao e "uma excecao", e a habilidade dominante.
//
// O `reducao_dano_isenta_habilidade: 1` devolve as duas isencoes, nos dois
// ambientes de uma vez, sem recompilar.
//
// A Batalha Campal tem a isencao IRMA (`INF2_IGNOREBGREDUCTION`, no
// `battle_calc_bg_damage`) e ela NAO foi tocada - campal ficou fora deste pedido
// por inteiro. Se um dia a campal entrar na regra, e la que falta o enxerto.
//
// -------------------------------------------------- e nem por tipo de atacante
//
// O outro lugar onde o caminho do `pk_mode` faz excecao e o tipo: ele reduz SO
// entre jogador e jogador (`src.type == BL_PC && bl.type == BL_PC`). A guerra
// reduz TUDO que acerta alguem no mapa, e e o que se faz aqui - Homunculo,
// mercenario, armadilha e invocacao pertencem a um jogador, e o furo mais caro
// deste projeto foi justamente uma parcela de dano que ficou fora de uma reducao
// (ver REDUCAO-DE-DANO.md secao 4f). Deixar tipo de fora e convidar o mesmo bug.
//
// CONSEQUENCIA A DIZER EM VOZ ALTA: monstro que acerte jogador em mapa `pvp`
// tambem passa a bater 20%. Hoje isso nao alcanca nada - os unicos mapas `pvp`
// do servidor sao as 84 arenas `pvp_n_*`/`pvp_y_*`, o `pvp_2vs2` e os tres
// `turbo_e_*` do Corrida Turbo (npc/mapflag/pvp.txt), e nenhum e mapa de caca.
// Se um dia um campo com monstro receber o mapflag `pvp`, os monstros dele ficam
// fracos junto, calados. E o mesmo comportamento que ele teria com `gvg`.
//
// ------------------------------------------------------------- onde na conta
//
// No fim dela, sobre o dano ja montado - e por isso o pedido fala de "dano
// FINAL". Este e o unico lugar em que uma reducao geral pode morar: as parcelas
// de `battle_calc_cardfix` (a resistencia a humano, REDUCAO-DE-DANO.md secao 2)
// sao somadas e depois multiplicadas por P.ATK, critico, distancia e
// multiplicador da habilidade. Reduzir la atras nao alcanca o dano fixo somado
// no fim; aqui alcanca.
//
// As duas reducoes se MULTIPLICAM, nao se somam. Um alvo com 50% de resistencia
// a humano na arena toma 20% de 50%, ou seja 10% do dano bruto. Ao calibrar
// resistencia depois disto, e essa a conta.
//
// ------------------------------------------------- o que AINDA fica de fora
//
// Nada do que escapava da reducao de carta escapa desta: e a ultima palavra
// sobre o dano do golpe, e alcanca inclusive o que o REDUCAO-DE-DANO.md secao 4
// lista como imune a carta - Assalto do Falcao, armadilha de Ranger, dano fixo
// de Asura. Com as duas isencoes de habilidade desligadas, NAO SOBRA EXCECAO
// DENTRO DO CALCULO DE BATALHA.
//
// O que continua fora fica fora porque NAO E ATAQUE e nunca passou por aqui, e
// nao ha como alcancar destas quatro chamadas: dano continuo de status (veneno,
// sangramento, queimadura), `bonus2 bHPVanishRate`, `percentheal` negativo de
// script e dano entregue por NPC. Sao caminhos de `status_fix_damage`, fora de
// todo o calculo de batalha. Ver REDUCAO-DE-DANO.md secao 4e. Se um dia isso
// incomodar em PvP, e outro trabalho e outro lugar - nao este arquivo.
//
// A Batalha Campal (`battleground`) tem os `bg_*_attack_damage_rate` dela,
// intocados neste pedido - continuam nos 60/80 do rAthena.
//
// ------------------------------------------------------------- por que em src
//
// Nao ha como fazer isto por db/, conf/ ou script: o unico gancho que o rAthena
// oferece para mapa `pvp` esta trancado atras do `pk_mode`, que traz o resto do
// servidor PK com ele. O enxerto no arquivo do rAthena e um include e CINCO
// chamadas, no padrao do src/custom/reducao_de_dano.hpp.

#ifndef CUSTOM_REDUCAO_GERAL_HPP
#define CUSTOM_REDUCAO_GERAL_HPP

#include <common/cbasetypes.hpp>

#include <map/battle.hpp>
#include <map/map.hpp>
#include <map/skill.hpp>

/// Uma habilidade escapa da reducao geral?
///
/// O rAthena isenta as que tem `IgnoreGvgReduction: true` no db/re/skill_db.yml -
/// duas no renewal, `NJ_ZENYNAGE` e `GN_FIRE_EXPANSION_ACID`. Por decisao de
/// 2026-08-10 ("TODOS os danos de pvp") a isencao esta DESLIGADA, e esta funcao
/// e o interruptor: `reducao_dano_isenta_habilidade: 0` no
/// conf/guerra/battle_guerra.txt, `1` para devolver o comportamento do rAthena.
///
/// USADA NOS DOIS AMBIENTES, e e por isso que ela existe em vez de um `if` solto
/// no `reducao_pvp()`: o `battle_calc_gvg_damage` do rAthena tem a mesma
/// checagem, e foi enxertado para chamar esta. Assim a guerra e a arena nao
/// podem divergir - um numero, os dois lugares.
///
/// NAO alcanca a isencao irma da campal (`INF2_IGNOREBGREDUCTION`, no
/// `battle_calc_bg_damage`): a campal ficou fora deste pedido.
///
/// @param skill_id Habilidade usada (0 em ataque normal)
/// @return true se este golpe deve passar sem reducao
inline bool reducao_isenta_habilidade(uint16 skill_id)
{
	if (battle_config.reducao_dano_isenta_habilidade == 0)
		return false;

	return skill_get_inf2(skill_id, INF2_IGNOREGVGREDUCTION);
}

/// Aplica a reducao de dano dos mapas `pvp`, do mesmo jeito e com a mesma
/// semantica com que o rAthena aplica a da guerra em `battle_calc_gvg_damage`.
///
/// Os cinco valores estao em conf/guerra/battle_guerra.txt e dizem QUANTO DO
/// DANO PASSA, em porcentagem - 100 e sem reducao, 20 e reducao de 80%. E a
/// convencao dos `gvg_*_attack_damage_rate` do rAthena de proposito: quem
/// comparar os dois arquivos le o mesmo numero querendo dizer a mesma coisa.
///
/// OS CINCO ESTAO NO MESMO NUMERO POR PEDIDO, e nao por acaso: "nao quero
/// diferenciar habilidades de ataque". A separacao em cinco e do rAthena e fica
/// porque e por onde a informacao chega (o `flag`); o que nao se faz e usar a
/// separacao. Quem for mexer aqui mexe nos cinco.
///
/// Chamavel sem checar mapa: a funcao devolve o dano intacto em todo mapa que
/// nao seja `pvp`. Ela tambem sai fora em mapa de guerra e de campal, que tem
/// as reducoes proprias deles aplicadas pelo chamador logo depois - sem isso as
/// duas se multiplicariam num mapa que tivesse os dois mapflags.
///
/// O mapa e lido do `bl`. Os dois estao sempre no mesmo mapa - nao ha ataque
/// entre mapas -, entao ler de um ou do outro da no mesmo, e e por isso que a
/// chamada do reflexo pode passar os dois na ordem invertida (quem toma o dano
/// refletido e o `src`) sem consequencia. O `battle_calc_pk_damage` do rAthena e
/// chamado com a mesma inversao, no mesmo lugar.
///
/// @param src Quem bate
/// @param bl Quem toma
/// @param damage Dano ja montado
/// @param skill_id Habilidade usada (0 em ataque normal)
/// @param flag Flags BF_* do golpe
/// @return O dano reduzido, nunca abaixo de 1 quando havia dano
inline int64 reducao_pvp(block_list& src, block_list& bl, int64 damage, uint16 skill_id, int32 flag)
{
	if (damage == 0) // Nada a reduzir, e o `i64max(damage, 1)` do fim nao pode
		return 0;    // transformar um golpe que errou em 1 de dano.

	map_data* mapdata = map_getmapdata(bl.m);

	if (mapdata == nullptr || mapdata->getMapFlag(MF_PVP) == 0)
		return damage;

	// Guerra e campal mandam mais: o chamador aplica a reducao delas depois
	// desta, e as duas se multiplicariam. Hoje nenhum mapa tem os dois
	// mapflags, mas o dia em que tiver nao pode custar uma tarde de medicao.
	if (mapdata_flag_gvg2(mapdata) || mapdata->getMapFlag(MF_BATTLEGROUND))
		return damage;

	// Desligada por padrao - ver "NINGUEM ESCAPA" no cabecalho. Fica a chamada,
	// e nao um `if` apagado, para o interruptor existir e para a guerra e a
	// arena lerem a MESMA regra.
	if (reducao_isenta_habilidade(skill_id))
		return damage;

	if (flag & BF_SKILL) { // Habilidade reduz por tipo de dano...
		if (flag & BF_WEAPON)
			damage = damage * battle_config.pvp_dano_arma / 100;
		if (flag & BF_MAGIC)
			damage = damage * battle_config.pvp_dano_magia / 100;
		if (flag & BF_MISC)
			damage = damage * battle_config.pvp_dano_misc / 100;
	} else {               // ...e ataque normal reduz por alcance.
		if (flag & BF_SHORT)
			damage = damage * battle_config.pvp_dano_curta / 100;
		if (flag & BF_LONG)
			damage = damage * battle_config.pvp_dano_longa / 100;
	}

	return i64max(damage, 1); // Minimo 1, como na guerra: golpe que acertou
}                             // sempre tira pelo menos 1 de HP.

#endif /* CUSTOM_REDUCAO_PVP_HPP */
