// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// O GUARDIAO CRESCE COM A DEFESA DO CASTELO
// =========================================
//
// O que este arquivo faz: dar ao Guardiao Soldado (1287), ao Arqueiro (1285) e
// ao Cavaleiro (1286) uma escala de HP, dano, velocidade de ataque e reducao de
// dano recebido que sobe junto com o investimento em DEFESA do castelo. Um
// monstro so por tipo; o que muda entre um castelo e outro e o numero, lido no
// spawn a partir do castelo a que aquele guardiao pertence.
//
// Pedido do dono em 2026-08-13: investir e caro num servidor novo, entao a
// recompensa por investir tem que aparecer na tela. A curva, ja com as DUAS
// revisoes da mesma noite (ver abaixo):
//
//     defesa    HP           reducao   ASPD   ATQ      precisao
//     0- 9       5.000.000      5%      168     5.000    530
//     10-19      6.000.000     10%      169    10.000    540
//     ...        ...           ...      ...    ...      ...
//     90-99      14.000.000     50%      177    50.000    620
//     100        15.000.000     50%      178    50.000    630
//
// O patamar e `defesa / 10`, de 0 a 10. Reducao e ATQ param no patamar 9 pelo
// teto de cada um; HP, velocidade e precisao chegam ao deles no 10.
//
// TRES CALIBRAGENS, E O QUE CADA UMA ENSINOU. A escala foi vista em jogo duas
// vezes e cortada nas duas:
//
//   1. Primeira: 50 milhoes de HP, 90-99% de reducao, ASPD 180-190. "A reducao
//      ficou realmente abissal" - com 99% mais os 20% que a guerra ja deixa
//      passar, chegavam 0,2% do dano bruto, ou 25 BILHOES para derrubar UM
//      guardiao, vezes oito por castelo.
//   2. Segunda: reducao cortada para 5-50%, HP e ASPD mantidos. Melhorou, mas
//      50 milhoes de HP ainda pediam 500 milhoes de dano, e ASPD 185 ainda era
//      rapido demais.
//   3. Esta: HP de 5 a 15 milhoes (um por patamar), ASPD de 168 a 178.
//
// O que se aprendeu no caminho, e que vale para a proxima vez que alguem for
// mexer nestes numeros: **a reducao e a alavanca nao-linear, o HP e a linear.**
// Sair de 50% para 90% de reducao multiplica a durabilidade por CINCO, e de 90%
// para 99% por mais DEZ; triplicar o HP triplica. Calibrar pelo HP e previsivel,
// calibrar pela reducao nao e - e foi por isso que a primeira versao errou por
// duas ordens de grandeza sem que a tabela parecesse absurda.
//
// ------------------------------------------------ nao existe "reducao humano"
//
// MONSTRO NAO TEM RESISTENCIA POR RACA. O `bonus2 bSubRace,RC_Player_Human` e
// bonus de JOGADOR: o `battle_calc_cardfix` (src/map/battle.cpp) le o `subrace`
// do `tsd`, e alvo do tipo BL_MOB nao tem ramo naquela funcao. Nao ha como dar
// "95% de resistencia a humano" a um guardiao por db/, por script nem por carta.
//
// O que existe e serve e o `md->damagetaken` - o `DamageTaken:` do mob_db, que
// o rAthena usa para a aura verde de MVP e aplica como multiplicador final sobre
// tudo que acerta aquele monstro (src/map/battle.cpp, no fim do
// `battle_calc_damage`). E reducao GERAL, nao por raca; dentro de castelo da no
// mesmo, porque quem bate em guardiao e jogador. Ele e por instancia - o
// `md->damagetaken` mora no monstro, nao no mob_db -, entao mexer nele aqui NAO
// contamina outros monstros do mesmo ID.
//
// O campo e inteiro em PORCENTAGEM: `10` deixa passar 10% (reducao de 90%) e o
// menor valor util e `1` (reducao de 99%). 99,9% nao cabe nele - para milesimos
// seria preciso outra funcao, ao lado daquela chamada. A escala pedida para no
// 99 justamente por isso.
//
// -------------------------------------------- as duas reducoes se MULTIPLICAM
//
// Mapa de castelo tem o mapflag `gvg_castle` PERMANENTE (npc/mapflag/gvg.txt),
// e o `mapdata_flag_gvg2` so olha mapflag - ou seja, os nossos
// `gvg_*_attack_damage_rate: 20` (conf/guerra/battle_guerra.txt) valem la dentro
// 24 horas por dia, com ou sem Guerra do Emperium aberta, e valem tambem quando
// o alvo e monstro. Entao o dano que de fato entra num guardiao e:
//
//     bruto x 0,20 (guerra) x (1 - reducao daqui)
//
// Com os numeros de hoje: no patamar 0 passam 19% do dano bruto, no patamar 9
// passam 10%. Com 5.000.000 e 50.000.000 de HP, sao 26 milhoes e 500 milhoes de
// dano bruto para derrubar um guardiao.
//
// QUEM CALIBRAR ESTA ESCALA CALIBRA ESSA CONTA, e nao o numero de HP sozinho -
// e o motivo de a primeira versao ter sido descartada. Perto do teto, um ponto
// de reducao vale muito mais que o HP: sair de 50% para 90% multiplica a
// durabilidade por CINCO, e de 90% para 99% por mais DEZ. Dobrar o HP dobra.
// Ver HISTORICO.md, "Guardioes que crescem com a defesa".
//
// ------------------------------------------------- velocidade: ASPD e adelay
//
// Monstro nao tem ASPD. Tem `AttackDelay` (o Soldado nasce com 1288 ms) e
// `AttackMotion` (288 ms). A escala pedida fala em 180-190 porque e o numero que
// o jogador conhece, entao a conversao usa a formula do proprio rAthena para
// jogador (src/map/status.cpp, `status_calc_bl_`):
//
//     amotion = AMOTION_ZERO_ASPD - ASPD * AMOTION_INTERVAL   // 2000 - ASPD*10
//     intervalo entre golpes = amotion * AMOTION_DIVIDER_PC   // o dobro
//
// ASPD 175 da 500 ms entre golpes (2 por segundo) e ASPD 185 da 300 ms (3,3 por
// segundo). Para MONSTRO o `adelay` ja E o intervalo - nao ha o fator 2 -, entao
// gravamos `adelay` com o intervalo e `amotion` com a metade, que e a mesma
// relacao que o jogador tem.
//
// 190 E O TETO DO EMULADOR, nao uma escolha. O `MAX_ASPD_NOPC` (src/map/status.hpp)
// trava o `amotion` de nao-jogador em 100 ms, e o `adelay` nunca fica abaixo do
// `amotion` (`cap_value(temp, AMOTION_DIVIDER_NOPC * status->amotion, MIN_ASPD)`).
// ASPD 190 cai exatamente em amotion 100. Pedir 191 nao acelera nada: o teto
// grampeia calado e a relacao amotion/adelay quebra.
//
// ------------------------------------------- precisao: por que ABSOLUTA
//
// No renewal a chance de acerto e literalmente `hit - esquiva`, em pontos
// percentuais, grampeada entre `min_hitrate` (5) e `max_hitrate` (100) -
// src/map/battle.cpp, `battle_is_hit`, onde a taxa base do renewal e ZERO e a
// unica coisa somada a ela e `sstatus->hit - flee`. Nao ha meio-termo suave:
// cem pontos de diferenca cobrem a escala inteira.
//
// O `hit` que o `status_calc_misc` da a um monstro e `nivel + DEX + 150`, e nos
// tres guardiaos isso da numeros MUITO diferentes:
//
//     Soldado   (1287)  56 + 103 + 150 = 309
//     Cavaleiro (1286)  86 + 150 + 150 = 386
//     Arqueiro  (1285)  74 + 198 + 150 = 422
//
// Contra um jogador de esquiva 385, isso e 5%, 5% e 37% - os dois primeiros no
// PISO do emulador. Foi o que se viu em jogo em 2026-08-13: "eles so nao
// ficaram monstros aniquiladores pois deram muito miss".
//
// E e por isso que a precisao aqui e ABSOLUTA e nao um bonus somado. Somar os
// mesmos 100 pontos nos tres deixaria o Soldado em 24% e os outros dois em
// 100% - tres guardiaos da mesma escala com precisoes que nao se parecem. Esta
// linha joga fora o `hit` do mob_db de proposito.
//
// COMO ESCOLHER O NUMERO: e `esquiva do alvo + a chance que se quer`. Contra
// esquiva 400, `guardiao_hit_base: 450` da 50% e `500` da 100%. A esquiva de
// verdade dos jogadores deste servidor NAO foi medida - o valor de hoje foi
// escolhido pela faixa que o dono pediu ("uns 100 pontos" a mais), nao por
// medicao. Quem for calibrar olha a Esquiva na janela de status do personagem e
// soma dali.
//
// ------------------------------------------------------------- onde na conta
//
// Tudo isto e escrito no FIM do `status_calc_mob_`, depois do
// `status_calc_misc` e depois do bloco "Strengthen Guardians" do rAthena, e
// antes do `memcpy` que copia o base status para o status de batalha. Tem que
// ser depois do `status_calc_misc` porque ele REESCREVE `rhw.atk` e `rhw.atk2`
// a partir do `Attack` do mob_db (80% e 120%); tem que ser depois do bloco do
// rAthena porque aquele bloco SOMA em cima do que encontrar, e os nossos valores
// sao absolutos - o nosso tem que ser a ultima palavra.
//
// O bloco do rAthena (o `flag&4`) so liga quando a guilda tem a habilidade
// Pesquisa de Guardiao. O nosso liga para todo guardiao, e por isso o enxerto
// no status.cpp ACRESCENTA um `flag|=4` - sem nenhuma flag ligada o
// `status_calc_mob_` sai antes, libera o `md->base_status` e passa a apontar
// para o status compartilhado do mob_db, onde escrever contaminaria todos os
// monstros daquele ID.
//
// ------------------------------------------------------------- por que em src
//
// Nao ha como fazer isto por db/, conf/ ou script. O `setunitdata` alcancaria
// HP, ATQ e `UMOB_DAMAGETAKEN`, mas so depois do monstro existir e so se alguem
// o chamasse a cada spawn - e guardiao nasce pelo `OnAgitInit` e pelo Gerente do
// Castelo, dois caminhos que sao arquivo do rAthena. Aqui a escala vale no
// instante em que o monstro nasce, venha de onde vier.

#ifndef CUSTOM_GUARDIAO_DO_CASTELO_HPP
#define CUSTOM_GUARDIAO_DO_CASTELO_HPP

#include <common/cbasetypes.hpp>
#include <common/utils.hpp> // cap_value

#include <map/battle.hpp>
#include <map/guild.hpp>
#include <map/mob.hpp>
#include <map/status.hpp>

/// Teto do `rhw.atk`/`rhw.atk2`, que sao `uint16` (src/map/status.hpp).
///
/// Nao e configuravel de proposito: e limite de tipo, nao regra de jogo. Fica
/// aqui com nome porque o `guardiao_atk_max` da conf aceita valor maior e a
/// variacao de +20% do `atk2` chega perto - com `guardiao_atk_max: 50000` o
/// `atk2` ja vale 60.000, a menos de 6.000 de estourar e dar a volta.
#define GUARDIAO_ATK_TETO_TIPO 65535

/// Este monstro entra na escala?
///
/// Tres condicoes, e todas as tres importam:
///
/// - `guardian_data` nao nulo: e o que separa guardiao de castelo de qualquer
///   outro monstro. So o `mob_spawn_guardian` preenche esse campo.
/// - `castle` nao nulo: e de onde sai a defesa. O `mob_spawn_guardian` sempre
///   grava, mas o `guardian_data` tambem e criado no `mob_once_spawn_sub` para
///   monstro comum invocado em mapa de castelo, e la o `castle` pode faltar.
/// - nao ser o Emperium: ele tem `flag&4` proprio no rAthena e uma regra de
///   quebra que nao e desta escala. Guardiao inquebravel e o pedido; Emperium
///   inquebravel e o fim da guerra.
///
/// @param md Monstro
/// @return true se a escala vale para ele
inline bool guardiao_tem_escala(const mob_data* md)
{
	if (battle_config.guardiao_escala == 0)
		return false;

	if (md == nullptr || md->guardian_data == nullptr)
		return false;

	if (md->guardian_data->castle == nullptr)
		return false;

	if (md->mob_id == MOBID_EMPERIUM)
		return false;

	return true;
}

/// O patamar da escala: `defesa / divisor`, limitado ao teto.
///
/// Separado da aplicacao porque e o unico numero que o resto do arquivo
/// compartilha, e porque e ele que se quer conferir quando a escala "nao pegou".
///
/// @param md Guardiao, ja aprovado pelo `guardiao_tem_escala`
/// @return Patamar, de 0 a `guardiao_patamar_max`
inline int32 guardiao_patamar(const mob_data* md)
{
	int32 divisor = battle_config.guardiao_patamar_divisor;

	if (divisor < 1) // Conf pode chegar zerada; divisao por zero derruba o mapa.
		divisor = 1;

	int32 patamar = md->guardian_data->castle->defense / divisor;

	return cap_value(patamar, 0, battle_config.guardiao_patamar_max);
}

/// Escreve a escala no status do guardiao.
///
/// Os quatro atributos seguem a MESMA forma - `base + passo * patamar`, cortado
/// por um teto -, e e de proposito: quem for calibrar le os doze numeros da conf
/// como tres colunas, nao como quatro formulas diferentes. Os tetos e que fazem
/// a curva do pedido: HP e ATQ chegam ao deles no patamar 9, reducao e
/// velocidade no 10.
///
/// O `damagetaken` mora no `md` e nao no `status` - e por isso que esta funcao
/// recebe os dois. Ele tambem precisa ser reescrito toda vez: o
/// `status_calc_mob_` o devolve ao valor do mob_db em todo `SCO_FIRST`
/// (src/map/status.cpp, `md->damagetaken = md->db->damagetaken`), bem antes
/// desta chamada.
///
/// @param md Guardiao
/// @param status O `base_status` que o `status_calc_mob_` esta montando
inline void guardiao_aplica_escala(mob_data* md, status_data* status)
{
	if (!guardiao_tem_escala(md) || status == nullptr)
		return;

	int32 patamar = guardiao_patamar(md);

	// ------------------------------------------------------------------ HP
	uint32 hp = static_cast<uint32>(cap_value(
		battle_config.guardiao_hp_base + battle_config.guardiao_hp_passo * patamar,
		1, battle_config.guardiao_hp_max));

	status->max_hp = hp;
	status->hp = hp; // Guardiao nasce cheio, como no bloco do rAthena logo acima.

	// ----------------------------------------------------------------- ATQ
	// O `Attack` do mob_db vira 80%..120% no `status_calc_misc`, e a variacao
	// existe para o dano nao sair sempre igual. A escala repete a mesma
	// proporcao para que `guardiao_atk_base: 5000` queira dizer "cinco mil em
	// media", que e como o pedido foi escrito.
	int32 atk = cap_value(
		battle_config.guardiao_atk_base + battle_config.guardiao_atk_passo * patamar,
		1, battle_config.guardiao_atk_max);

	status->rhw.atk = static_cast<uint16>(cap_value(atk * 80 / 100, 1, GUARDIAO_ATK_TETO_TIPO));
	status->rhw.atk2 = static_cast<uint16>(cap_value(atk * 120 / 100, 1, GUARDIAO_ATK_TETO_TIPO));

	// -------------------------------------------------------------- REDUCAO
	// Quanto do dano PASSA, em porcentagem - a mesma semantica dos
	// `gvg_*_attack_damage_rate` e da nossa `reducao_geral.hpp`. Reducao de 90%
	// vira `damagetaken` 10.
	int32 reducao = cap_value(
		battle_config.guardiao_reducao_base + battle_config.guardiao_reducao_passo * patamar,
		0, battle_config.guardiao_reducao_max);

	md->damagetaken = static_cast<uint16>(cap_value(100 - reducao, 1, 100));

	// ----------------------------------------------------------- VELOCIDADE
	// Ver o cabecalho: ASPD de jogador convertida em `adelay` de monstro. O
	// `aspd_rate` volta a 1000 porque o bloco "Strengthen Guardians" do rAthena
	// desconta 3 dele logo acima, e o `status_calc_bl_` multiplica o nosso
	// `adelay` por ele - sem esta linha os 400 ms viram 398 e o numero da conf
	// deixa de ser o numero da tela.
	int32 aspd = cap_value(
		battle_config.guardiao_aspd_base + battle_config.guardiao_aspd_passo * patamar,
		0, battle_config.guardiao_aspd_max);

	int32 amotion = AMOTION_ZERO_ASPD - aspd * AMOTION_INTERVAL;

	amotion = cap_value(amotion, MAX_ASPD_NOPC, MIN_ASPD);

	status->amotion = static_cast<uint16>(amotion);
	status->adelay = static_cast<uint16>(cap_value(amotion * AMOTION_DIVIDER_PC, amotion, MIN_ASPD));
	status->aspd_rate = 1000;

	// ------------------------------------------------------------- PRECISAO
	// ABSOLUTA, e nao somada ao que o mob_db dava - ver o cabecalho. O
	// `status_calc_misc` ja rodou e escreveu `nivel + DEX + 150` aqui; esta
	// linha joga aquilo fora de proposito, para os tres guardiaos acertarem
	// igual.
	status->hit = static_cast<int16>(cap_value(
		battle_config.guardiao_hit_base + battle_config.guardiao_hit_passo * patamar,
		1, battle_config.guardiao_hit_max));

	// O cliente cronometra a ANIMACAO de ataque por este campo (clif.cpp, no
	// `clif_damage`). O Soldado nasce com 624 no mob_db; deixado assim, o
	// desenho ficaria seis vezes mais lento que os golpes de verdade.
	status->clientamotion = static_cast<uint16>(amotion);
}

#endif /* CUSTOM_GUARDIAO_DO_CASTELO_HPP */
