// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// AS TRES HABILIDADES DE SOBREVIVENTE
// ===================================
//
// Tres passivas proprias, de nivel unico, que um personagem ganha de uma missao
// (a missao ainda nao existe - ver PENDENCIAS.md). Pedido do dono em
// 2026-09-22:
//
//   239  Sobrevivente Pragmatico   +20 AGI  e  +2000 de peso
//   240  Sobrevivente Astuto       +20 INT  e  +100 de ATQM
//   241  Sobrevivente Caotico      +10 em todos os status  e  +100 de ATQ
//
// O cadastro delas (Id, nome, MaxLevel, IsQuest) esta em
// `db/guerra/skill_db.yml`, e o cabecalho daquele arquivo explica por que os
// ids sao estes tres e nao 8000 e seguintes. Aqui fica so o EFEITO.
//
// ---------------------------------------------------------------------------
// POR QUE O EFEITO E C++ E NAO YAML
// ---------------------------------------------------------------------------
// O `skill_db` tem um campo `Status:`, e com ele uma habilidade ativa aplica um
// efeito de status pronto sem uma linha de codigo (e o que o `StatusSkillImpl`
// de `src/map/skills/skill_impl.cpp:57` faz). Nao serve aqui por dois motivos:
//
//   1. sao PASSIVAS - nao ha lancamento, entao nao ha o que aplicar um status;
//   2. nao existe status de efeito para peso nenhum, e os que somam ATQ plano
//      guardam o valor em `val2`/`val3`, que aquele caminho generico nao
//      preenche (ele so passa `val1 = nivel`).
//
// O rAthena resolve bonus passivo de habilidade em C++, sempre: o `AC_OWL` que
// da DEX e o `MC_INCCARRY` que da peso sao exatamente isto, e as duas funcoes
// abaixo entram ao lado deles, nos mesmos dois lugares.
//
// ---------------------------------------------------------------------------
// AS UNIDADES, QUE SAO DUAS ARMADILHAS DIFERENTES
// ---------------------------------------------------------------------------
// PESO: `sd->max_weight` esta em DECIMOS do que a janela mostra. O
// `MC_INCCARRY` soma 2000 por nivel e o jogador le "+200". Os 2000 pedidos sao
// os da TELA, entao aqui vao 20000 - o mesmo que Aumentar Capacidade no nivel
// 10. Esta escrito como `2000 * 10` de proposito, para que o numero pedido
// continue visivel no codigo.
//
// ATQ e ATQM: no renewal (`src/config/renewal.hpp:24`, que e o nosso caso) o
// ataque plano NAO entra em `base_status->batk`. Ele entra em `sd->bonus.eatk`,
// que o `status_calc_pc_` copia para `base_status->eatk` logo abaixo de onde
// esta funcao e chamada (`status.cpp:4370`); o magico entra em
// `sd->bonus.ematk`, lido pelo `status_calc_matk`. Sao os mesmos campos em que
// `bonus bBaseAtk` e `bonus bMatk` de item escrevem (`pc.cpp:3774` e o
// `export_constant2("bMatk", SP_EMATK)` do `script_constants.hpp:803`), ou
// seja: o bonus daqui se comporta em toda formula como se viesse de um
// equipamento.
//
// ---------------------------------------------------------------------------
// O QUE ESTE ARQUIVO NAO FAZ: a escolha entre as tres
// ---------------------------------------------------------------------------
// A decisao do dono e que o jogador escolhe UMA das tres, nao as tres. Essa
// trava NAO esta aqui - ela pertence a quem concede, que sera o NPC da missao:
// se um personagem tiver duas, os dois bonus somam, e e assim que se testa cada
// uma isolada com `@questskill`. Esta anotado em PENDENCIAS.md para nao se
// perder quando a missao for escrita.
//
// "Todos os status" sao os SEIS classicos. Os de 4a classe (POW, STA, WIS, SPL,
// CON, CRT) ficaram de fora de proposito: nenhuma classe daqui os usa hoje, e
// somar neles seria decidir sozinho uma coisa que nao foi pedida. Sao seis
// linhas a mais no dia em que forem.

#ifndef HABILIDADES_SOBREVIVENTE_HPP
#define HABILIDADES_SOBREVIVENTE_HPP

#include <common/cbasetypes.hpp>

#include <map/pc.hpp>
#include <map/status.hpp>

// Os ids, com o nome que ELES tem aqui.
//
// O `enum e_skill` do rAthena ja batiza estes tres numeros - 239 e
// AM_BIOTECHNOLOGY, 240 e AM_CREATECREATURE, 241 e AM_CULTIVATION -, e aquelas
// constantes continuam existindo: nao se apaga nome de terceiro. Sao habilidades
// de Alquimista que o rAthena nunca implementou e que nenhum `.cpp` cita, o que
// e justamente o motivo de a vaga estar livre (a conferencia esta no cabecalho
// do `db/guerra/skill_db.yml`).
//
// Escrever `pc_checkskill(sd, AM_CULTIVATION)` numa funcao que da peso e
// inteligencia seria mentira duas vezes, entao os ids ganham aqui o nome que o
// `db/guerra/skill_db.yml` lhes da do lado do servidor. Se algum dia o rAthena
// implementar o Cultivo de verdade, e esta constante que denuncia o conflito -
// o numero esta num lugar so.
static const uint16 GUE_SOBREVIVENTE_PRAGMATICO = 239;
static const uint16 GUE_SOBREVIVENTE_ASTUTO     = 240;
static const uint16 GUE_SOBREVIVENTE_CAOTICO    = 241;

/// Bonus de status, ATQ e ATQM das tres passivas.
///
/// Chamada pelo `status_calc_pc_` (src/map/status.cpp), no fim do bloco
/// "Absolute modifiers from passive skills" - ou seja ANTES de os valores base
/// serem somados aos de carta e equipamento, exatamente como o AC_OWL logo
/// acima. Acrescimo: nao substitui nada.
inline void sobrevivente_aplica_bonus(map_session_data* sd, status_data* base_status) {
	if (sd == nullptr || base_status == nullptr)
		return;

	// Pragmatico: agilidade. O peso dele esta na outra funcao, porque o
	// max_weight nao se calcula aqui.
	if (pc_checkskill(sd, GUE_SOBREVIVENTE_PRAGMATICO) > 0)
		base_status->agi += 20;

	// Astuto: inteligencia e ataque magico.
	if (pc_checkskill(sd, GUE_SOBREVIVENTE_ASTUTO) > 0) {
		base_status->int_ += 20;
		sd->bonus.ematk += 100;
	}

	// Caotico: os seis status e ataque fisico.
	if (pc_checkskill(sd, GUE_SOBREVIVENTE_CAOTICO) > 0) {
		base_status->str += 10;
		base_status->agi += 10;
		base_status->vit += 10;
		base_status->int_ += 10;
		base_status->dex += 10;
		base_status->luk += 10;
		sd->bonus.eatk += 100;
	}
}

/// O peso do Pragmatico.
///
/// Chamada pelo `status_calc_weight` (src/map/status.cpp), dentro do
/// `flag&CALCWT_MAXBONUS`, ao lado do MC_INCCARRY. Tem de ser ali e nao na
/// funcao acima: o max_weight e refeito noutro momento, e quem avisa o cliente
/// e o proprio status_calc_weight, logo abaixo.
///
/// O 10 e a conversao para decimos - ver o cabecalho. Mudar o 2000 muda o
/// numero que o jogador le na janela.
inline void sobrevivente_aplica_peso(map_session_data* sd) {
	if (sd == nullptr)
		return;

	if (pc_checkskill(sd, GUE_SOBREVIVENTE_PRAGMATICO) > 0)
		sd->max_weight += 2000 * 10;
}

#endif /* HABILIDADES_SOBREVIVENTE_HPP */
