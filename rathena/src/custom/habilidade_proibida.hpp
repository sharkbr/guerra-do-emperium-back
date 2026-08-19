// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// HABILIDADE DE MONSTRO PROIBIDA POR MAPA
// =======================================
//
// O que este arquivo faz: uma tabela de (mapa, habilidade). Monstro que esteja
// num mapa listado se comporta como se NAO TIVESSE aquela habilidade - o
// mobskill_use pula a linha do mob_skill_db antes de avaliar qualquer condicao,
// entao nao ha lancamento, nao ha animacao, nao ha efeito e nao ha recarga
// gasta. Fora daquele mapa, o mesmo monstro continua com a habilidade inteira.
//
// ------------------------- a primeira entrada: Instinto de Defesa no Corredor
//
// Pedido do dono em 2026-08-18: "bloquear instinto de defesa na cheffenia por
// uso dos MVPs. Hoje os MVPs estao matando MUITO com essa skill! E nao ha nem o
// que fazer, nem como saber que ela esta ativa, perdendo qualquer forma de
// contornar ou suportar a situacao".
//
// Cheffenia e o Corredor Fantasma (npc/guerra/corredor_fantasma.txt), mapa
// vis_h01, os 130 chefes.
//
// QUEM LANCA, NA SALA INTEIRA, E UM SO: o 2239 Stalker Gertie - dois no chao,
// como todos os outros. Foi medido, nao suposto: dos 65 tipos da sala, ele e o
// unico com ST_REJECTSWORD no db/re/mob_skill_db.txt, e a linha dele e
//
//   2239,Stalker Gertie@ST_REJECTSWORD,idle,390,5,10000,0,30000,yes,self,always
//   (a mesma repetida em chase e em attack)
//
// nivel 5, 100% de chance, recarga de 30 segundos, nos tres estados. E o
// SC_REJECTSWORD de nivel 5 (src/map/status.cpp, case SC_REJECTSWORD) vale:
//
//   val2 = 15 x nivel = 75%    chance de refletir a cada golpe recebido
//   val3 = 3                   golpes refletidos antes de o status acabar
//   tick = INFINITE_TICK       nao expira sozinho
//
// POR QUE ISSO MATA AQUI E NAO MATAVA NO kRO. O reflexo e 50% do dano que o
// JOGADOR causou - src/map/battle.cpp, battle_calc_weapon_final_atk_modifiers,
// o bloco "Reject Sword". Num servidor em que se bate em MVP para centenas de
// milhares, metade disso volta de uma vez. E volta por battle_fix_damage, que
// NAO passa pelo battle_calc_damage: escapa da reducao de carta e escapa
// tambem da reducao geral de 80% (ver REDUCAO-DE-DANO.md, secao 4d). Nao ha
// resistencia, carta nem equipamento que segure - quanto mais forte o jogador,
// mais forte o golpe que o mata.
//
// E NAO DA PARA SABER QUE ESTA ATIVO, que e a segunda metade da queixa e a que
// nao tem conserto por numero: o SC_REJECTSWORD nao tem icone nenhum, e o
// monstro so desenha alguma coisa na tela QUANDO O REFLEXO JA ACONTECEU - o
// clif_skill_nodamage sai na mesma linha do dano. Quem morre descobre depois de
// morto.
//
// Um terceiro detalhe que torna o diagnostico pior: o reflexo so alcanca quem
// esta de adaga, espada de uma mao ou espada de duas maos (o teste de arma esta
// naquele mesmo bloco). Dois jogadores lado a lado no mesmo chefe, um cai e o
// outro nao.
//
// ------------------------------- por que proibir por mapa, e nao por monstro
//
// Tirar a linha do mob_skill_db seria o caminho curto, e nao serve por dois
// motivos:
//
//   1. NAO CHEGA NA PRODUCAO. O mob_skill_db e CSV, nao YAML: nao tem
//      "Footer: Imports", e os unicos caminhos que o sv_readdb le sao
//      db/re/mob_skill_db.txt (arquivo do rAthena, que a secao 2 do CLAUDE.md
//      proibe editar) e db/import/mob_skill_db.txt - e db/import esta no
//      .gitignore do vendor, ou seja nao e versionado e o deploy nao o leva.
//   2. ALCANCARIA OS OUTROS LUGARES. O 2239 tambem nasce na instancia
//      Laboratorio do Wolfchev (npc/re/instances/WolfchevLaboratory.txt), e os
//      irmaos dele - 2225 Gertie e 2232 Stalker Gertie - tem a mesma
//      habilidade em lhz_dun04. Nada disso foi pedido, e la os numeros sao
//      outros.
//
// A tabela por mapa deixa o pedido do jeito que ele veio: a sala de MVP fica
// sem a habilidade, o resto do servidor nao muda.
//
// -------------------------------------------------------------- como estender
//
// Uma linha na tabela abaixo, e recompilar o map-server. Nao existe recarga por
// comando para isto: e codigo, nao db.
//
// O que este arquivo NAO faz: nao mexe em monstro que ja esteja com o status
// ligado. Como so se recompila com o map-server parado, e todo monstro renasce
// no boot, isso nunca aparece na pratica.
//
// AS VIZINHAS QUE FICARAM DE FORA, de proposito, porque nao foram pedidas: na
// mesma sala ha CR_REFLECTSHIELD em seis chefes (1086 Golden Thief Bug e 2235
// Paladin Randel no nivel 10, 1719 Detale e 2319 Buwaya no 5, 2068 Boitata no
// 3, 2202 Kraken no 1) e NPC_MAGICMIRROR em tres (1871 Falling Bishop, 1874
// Beelzebub, 2131 Lost Dragon). Sao reflexos da mesma familia, mas de outra
// natureza: o CR_REFLECTSHIELD devolve uma fracao menor (10 + 3 x nivel por
// cento) e passa pelo battle_calc_return_damage, que a reducao geral alcanca.
// Se um dia doerem tambem, sao duas linhas aqui.

#ifndef HABILIDADE_PROIBIDA_HPP
#define HABILIDADE_PROIBIDA_HPP

#include <cstring>

#include <common/cbasetypes.hpp>

#include <map/map.hpp>
#include <map/mob.hpp>
#include <map/skill.hpp>

/// Uma proibicao: uma habilidade, num mapa.
struct s_habilidade_proibida {
	const char* mapa;
	uint16 habilidade;
};

static const s_habilidade_proibida HABILIDADES_PROIBIDAS[] = {
	// Instinto de Defesa no Corredor Fantasma - o 2239 Stalker Gertie.
	{ "vis_h01", ST_REJECTSWORD },
};

/// Verdadeiro se este monstro, no mapa em que esta, nao pode lancar esta
/// habilidade. Chamado pelo mobskill_use (src/map/mob.cpp), uma vez por linha
/// do mob_skill_db - por isso o teste barato, o numero da habilidade, vem
/// primeiro e o strncmp so roda quando ele casa.
inline bool habilidade_de_monstro_proibida(mob_data* md, uint16 skill_id) {
	if (md == nullptr)
		return false;

	map_data* mapa = map_getmapdata(md->m);

	if (mapa == nullptr)
		return false;

	for (const s_habilidade_proibida& proibida : HABILIDADES_PROIBIDAS) {
		if (proibida.habilidade == skill_id &&
			strncmp(proibida.mapa, mapa->name, MAP_NAME_LENGTH) == 0)
			return true;
	}

	return false;
}

#endif /* HABILIDADE_PROIBIDA_HPP */
