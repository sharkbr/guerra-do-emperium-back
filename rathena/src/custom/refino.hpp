// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// TETO DE REFINO
// ==============
//
// O que este arquivo faz: impedir que a janela de refino ofereca - e que o
// servidor aceite - tentativa acima de um refino maximo nosso, e avisar o
// jogador em vez de simplesmente nao fazer nada.
//
// -------------------------------------------------- por que precisa de src
//
// O caminho obvio seria apagar os niveis 17 a 20 do db/re/refine.yml. Nao
// serve, por dois motivos.
//
//   1. Nao da para apagar por import. O leitor de YAML do rAthena so MESCLA:
//      um arquivo importado acrescenta e sobrescreve campo, nunca remove
//      nivel. Cortar os niveis exigiria editar o arquivo do rAthena.
//
//   2. Baixar o MAX_REFINE para 16 QUEBRA a base inteira. Em
//      `RefineDatabase::parseBodyNode` (src/map/status.cpp:183), nivel acima
//      do MAX_REFINE nao e "pulado" apesar do que a mensagem diz - o
//      `return 0` que vem logo abaixo descarta o GRUPO todo. Com os niveis
//      17 a 20 ainda no arquivo, Armor e Weapon inteiros deixariam de
//      carregar e ninguem refinaria mais nada. O aviso no log fala em
//      "skipping", o que faz o estrago parecer inofensivo.
//
// E nenhum dos dois daria a mensagem que o jogador le.
//
// ------------------------------------------------ por que so a janela basta
//
// Os tres NPCs refinadores do rAthena param no +10 sozinhos
// (`npc/merchants/refine.txt`, `advanced_refiner.txt` e o
// `re/merchants/ticket_refiner.txt` que ligamos - todos comparam
// `getequiprefinerycnt` com 10, ou com o nivel do bilhete). Acima de +10 o
// unico caminho e a janela de refino, que e 100% C++. Fechar os dois pontos
// dela fecha o assunto.
//
// Fora do alcance, de proposito: `@refine` de GM e `successrefitem` de
// script. Sao ferramenta de administracao e de evento, e nao passam por
// aqui.
//
// --------------------------------------------------- por que battle_config
//
// O teto e `refino_teto` em conf/guerra/battle_guerra.txt, e nao um numero
// cravado aqui, para mudar de valor com `@reloadbattleconf` em vez de exigir
// recompilar. `refino_teto: 0` desliga a trava.
//
// A mensagem, pelo mesmo motivo, e a 1550 do conf/guerra/map_msg_guerra.conf
// e nao uma string neste arquivo: texto que o jogador le e cp1252, e .cpp
// nao e lugar de guardar acento.

#ifndef CUSTOM_REFINO_HPP
#define CUSTOM_REFINO_HPP

#include <common/cbasetypes.hpp>

#include <map/battle.hpp>
#include <map/clif.hpp>
#include <map/map.hpp>
#include <map/pc.hpp>

/// "Refinos acima de 16 trazem maus presagios. Va embora!"
/// O texto de verdade, com acento, esta em conf/guerra/map_msg_guerra.conf.
#define MSG_REFINO_TETO 1550

/// O item ja bateu no teto? Silencioso - use na checagem que so precisa
/// recusar (pacote do cliente), sem repetir aviso.
inline bool refino_no_teto(const struct item& item) {
	// 0 desliga a trava.
	if (battle_config.refino_teto <= 0)
		return false;

	return item.refine >= battle_config.refino_teto;
}

/// Igual ao de cima, mas manda o aviso na caixa de chat quando bate no teto.
/// Devolve true se bateu - ou seja, se quem chamou deve parar por aqui.
inline bool refino_no_teto_avisa(map_session_data& sd, const struct item& item) {
	if (!refino_no_teto(item))
		return false;

	clif_messagecolor(&sd, color_table[COLOR_RED], msg_txt(&sd, MSG_REFINO_TETO), false, SELF);
	return true;
}

#endif /* CUSTOM_REFINO_HPP */
