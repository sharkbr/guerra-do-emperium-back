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
