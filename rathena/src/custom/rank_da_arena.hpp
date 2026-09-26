// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// O "M" DO RANK N/M DA ARENA CRESCIA SEM PARAR
// ============================================
//
// O que este arquivo faz: recontar, a cada calculo de rank de PvP, quantos
// jogadores VISIVEIS estao no mapa, e gravar o resultado no
// `mapdata->users_pvp` - o numero que o cliente desenha depois da barra.
//
// O SINTOMA, relatado em 2026-09-26: o dono entrou na Arena de Prontera
// (pvp_n_1-5, npc/guerra/arena_de_combate.txt) com apenas o fantasma la
// dentro e viu "1/43". O certo seria 1/2 ou 2/2.
//
// ------------------------------------------------------- de onde vem o defeito
//
// O rAthena nao CONTA o M: ele o mantem num contador incremental, o
// `users_pvp` do mapa, mexido em cinco lugares a mao:
//
//   ++  clif_parse_LoadEndAck, ao entrar no mapa, se nao estiver invisivel
//   --  unit_remove_map, ao sair do mapa, se nao estiver invisivel
//   --  pc_reg_received, quem ja chega com @hide
//   +-  ACMD_FUNC(hide), ao ligar/desligar o @hide
//
// O contrato implicito e que o bit OPTION_INVISIBLE (0x40) so muda por esses
// caminhos. NAO E VERDADE: a Copia Explosiva (SC__FEINTBOMB) tem
// `Options: Invisible: true` em db/re/status.yml - liga e desliga O MESMO BIT
// pelo status_change_start/end, que nao sabem que o contador existe. Toda
// vez que o bit vira por baixo, o contador fica um fora, e esse "um" nunca
// volta: ele vive na memoria do map-server ate o reinicio.
//
// E o fantasma (projects/FANTASMA-BOT.md) usa a Copia Explosiva como a sua
// abertura de combate, varias vezes por hora. Tres dos jeitos de vazar que
// ele percorre:
//
//   - visivel, lanca a Copia (bit liga, contador fica), e sai do mapa dentro
//     dos 1,5s - morte, @warp, queda: o unit_remove_map ve invisivel e nao
//     desconta. +1 para sempre.
//   - visivel, lanca a Copia, e manda @hide: o atcommand ve invisivel, cai no
//     ramo "Invisible: Off" e soma 1 a quem ja estava contado. +1.
//   - o inverso (Copia terminando por cima de um @hide) desconta sem ter
//     somado. -1, e com as duas direcoes o numero pode ate ficar negativo.
//
// ------------------------------------------------ por que recontar, e nao tapar
//
// Tapar os buracos um a um exigiria mexer no status_change_start/end para
// uma bandeira que qualquer status novo com `Invisible: true` reabriria -
// calado. A leitura do `users_pvp` e UMA so em todo o rAthena
// (pc_calc_pvprank, src/map/pc.cpp); recontando ali, os outros cinco lugares
// passam a nao importar, e o numero se conserta sozinho no segundo seguinte
// mesmo se ja estiver errado.
//
// O custo e nada: o pc_calc_pvprank JA percorre o mapa inteiro para achar a
// posicao (map_foreachinmap com o pc_calc_pvprank_sub), uma vez por jogador
// por segundo. Uma segunda volta com a mesma forma so dobra uma conta que,
// numa arena, e de meia duzia de jogadores.
//
// O criterio e o mesmo do pc_calc_pvprank_sub, de proposito: quem esta
// invisivel nao entra no N (o sub pula), entao nao entra no M. Assim o
// fantasma escondido some dos dois lados da barra, e o jogador sozinho ve 1/1
// - que e a verdade do que ele consegue enxergar.

#ifndef CUSTOM_RANK_DA_ARENA_HPP
#define CUSTOM_RANK_DA_ARENA_HPP

static int32 rank_da_arena_conta_sub(block_list* bl, va_list ap)
{
	map_session_data* sd = (map_session_data*)bl;

	if (pc_isinvisible(sd))
		return 0;

	return 1;
}

/// Reconta os jogadores visiveis do mapa e corrige o `users_pvp` no lugar.
/// Chamar antes de o pc_calc_pvprank comparar/mandar o numero ao cliente.
///
/// @param m Mapa
inline void rank_da_arena_reconta(int16 m)
{
	struct map_data* mapdata = map_getmapdata(m);

	if (mapdata == nullptr)
		return;

	mapdata->users_pvp = map_foreachinmap(rank_da_arena_conta_sub, m, BL_PC);
}

#endif /* CUSTOM_RANK_DA_ARENA_HPP */
