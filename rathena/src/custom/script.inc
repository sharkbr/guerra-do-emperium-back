// Copyright (c) rAthena Dev Teams - Licensed under GNU GPL
// For more information, see LICENCE in the main folder

/**
 * Custom Script Commands
 * Place the body of custom script commands in this file.
 * Format:
 *	BUILDIN_FUNC(command_name)
 *	{
 *		<code>;
 *	}
 **/

#include <custom/placa_de_venda.hpp>
#include <custom/efeito_do_cliente.hpp>
#include <custom/roleta_do_cassino.hpp>

//BUILDIN_FUNC(example)
//{
//	ShowInfo("buildin_example: It works!\n");
//	script_pushint(st,1);
//	return 0;
//}

// ---------------------------------------------------------------------------
// Guerra do Emperium
// ---------------------------------------------------------------------------

/// placadevenda "<texto da placa>";
/// placadevenda "";                   // tira a placa
///
/// Poe sobre a cabeca do NPC a placa amarela de quem abriu barraca, no lugar
/// da barra de sala de conversa do `waitingroom`. O porque inteiro esta em
/// `src/custom/placa_de_venda.hpp`.
///
/// Vale para o NPC ao qual o script esta preso, como o `waitingroom` - e pelo
/// mesmo caminho: `st->oid`. O uso e no OnInit da loja.
///
/// O texto cabe em 79 caracteres (MESSAGE_SIZE); o que passar disso e cortado
/// pelo `safestrncpy`, sem erro.
BUILDIN_FUNC(placadevenda)
{
	const char* texto = script_getstr(st, 2);
	npc_data* nd = (npc_data *)map_id2bl(st->oid);

	if (nd == nullptr) {
		ShowError("buildin_placadevenda: sem NPC preso ao script.\n");
		return SCRIPT_CMD_FAILURE;
	}

	placa_de_venda_define(*nd, texto);

	return SCRIPT_CMD_SUCCESS;
}

/// efeitoespecial <numero>{,<alvo>{,"<nome unico do NPC>"}};
///
/// Igual ao `specialeffect` do rAthena, com uma diferenca so: aceita a faixa
/// inteira que o NOSSO cliente conhece (13..2372) em vez de parar no `EF_MAX`
/// do emulador, que e 1243. Ha 941 efeitos com arte propria acima daquele
/// teto, e o `specialeffect` recusa todos eles com "unsupported effect id".
///
/// O porque, a medicao do teto e a armadilha do numero fora da faixa (que nao
/// desenha nada e nao avisa) estao em `src/custom/efeito_do_cliente.hpp`.
///
/// Sem o terceiro argumento, sai no NPC ao qual o script esta preso - que e o
/// caso do uso em `OnTimer`, onde nao ha jogador anexado.
BUILDIN_FUNC(efeitoespecial)
{
	block_list* bl = map_id2bl(st->oid);
	int32 numero = script_getnum(st, 2);
	enum send_target target = script_hasdata(st, 3)
		? (send_target)script_getnum(st, 3) : AREA;

	if (bl == nullptr)
		return SCRIPT_CMD_SUCCESS;

	if (!efeito_do_cliente_existe(numero)) {
		ShowError("buildin_efeitoespecial: efeito %d fora da faixa que o "
			"cliente conhece (%d..%d).\n", numero,
			EFEITO_DO_CLIENTE_MINIMO, EFEITO_DO_CLIENTE_MAXIMO);
		return SCRIPT_CMD_FAILURE;
	}

	if (script_hasdata(st, 4)) {
		const char* nome = script_getstr(st, 4);
		npc_data* nd = npc_name2id(nome);

		if (nd == nullptr) {
			ShowError("buildin_efeitoespecial: NPC \"%s\" nao existe.\n", nome);
			return SCRIPT_CMD_FAILURE;
		}
		bl = nd;
	}

	if (target == SELF) {
		map_session_data* sd;

		if (!script_rid2sd(sd))
			return SCRIPT_CMD_FAILURE;

		clif_specialeffect_single(bl, numero, sd->fd);
	} else {
		clif_specialeffect(bl, numero, target);
	}

	return SCRIPT_CMD_SUCCESS;
}

/// roletagira(<ganhou>, "<NPC::Evento>")
///
/// Abre no cliente a roleta da captura de pet, girando, e responde <ganhou>
/// (1 ou 0) quando o jogador clica nela - ou quando passam 10 segundos sem
/// clique. No momento do resultado roda <NPC::Evento> com o jogador anexado;
/// e ali que se paga.
///
/// Devolve 0, sem abrir nada, se o personagem ja tem uma roleta girando. O
/// script deve cobrar SO depois de receber 1.
///
/// O porque, o que o exe faz e o desvio que o faz abrir a janela estao em
/// `src/custom/roleta_do_cassino.hpp`.
BUILDIN_FUNC(roletagira)
{
	map_session_data* sd;

	if (!script_rid2sd(sd)) {
		script_pushint(st, 0);
		return SCRIPT_CMD_FAILURE;
	}

	bool ganhou = script_getnum(st, 2) != 0;
	const char* evento = script_getstr(st, 3);

	if (strstr(evento, "::") == nullptr) {
		ShowError("buildin_roletagira: evento \"%s\" sem \"::\" - "
			"tem de ser \"<NPC>::<Evento>\".\n", evento);
		script_pushint(st, 0);
		return SCRIPT_CMD_FAILURE;
	}

	script_pushint(st, roleta_do_cassino_gira(*sd, ganhou, evento) ? 1 : 0);
	return SCRIPT_CMD_SUCCESS;
}
