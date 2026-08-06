// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// PLACA DE VENDA SOBRE A CABECA DO NPC
// ====================================
//
// O que este arquivo faz: dar ao NPC a MESMA placa que aparece sobre um
// jogador que abriu barraca (a amarela, de venda), no lugar da barra de
// titulo de sala de conversa que o `waitingroom` desenha.
//
// -------------------------------------------------- por que precisa de src
//
// O rAthena nao tem comando de script para isso, e nao e esquecimento: a
// placa de venda nasce de `vending_openvending`, que exige um
// `map_session_data` - conta, inventario, item a venda. NPC nao tem nada
// disso e nunca abre barraca de verdade.
//
// Mas o PACOTE nao pede nada disso. O `ZC_STORE_ENTRY` (0x0131) carrega dois
// campos: o id do dono e o texto da placa. Quem o cliente procura nesse id e
// o ATOR na tela, e ator de NPC esta na mesma lista que ator de jogador -
// entao a placa gruda sobre o NPC do mesmo jeito.
//
// O que o NPC continua nao tendo e a barraca por tras: clicar na PLACA nao
// abre nada. Isso nao e regressao - com `waitingroom` de limite 0, clicar na
// barra tambem nao fazia nada. O clique que importa e o do CORPO do NPC, que
// segue chamando o script normalmente.
//
// -------------------------------------------------- por que exname, e nao id
//
// O registro e indexado pelo `exname` (o nome unico do NPC), nao pelo id de
// bloco. O id e reciclado: depois de um `@reloadscript` o mesmo numero pode
// cair em outro NPC, e a placa da loja antiga apareceria sobre um NPC
// qualquer. `exname` e estavel e unico por definicao - `duplicate` e
// `donpcevent` referenciam por ele.
//
// -------------------------------------------------- quando o pacote e enviado
//
// Duas vezes, e as duas sao necessarias:
//
//   1. Quando a placa e definida (`placadevenda` no OnInit) - para quem ja
//      esta em volta.
//   2. Quando o NPC entra na visao de um jogador - em `clif_getareachar_unit`,
//      no mesmo `case BL_NPC` que ja mandava o `waitingroom`. Sem isso a
//      placa so existiria para quem estava perto na hora do OnInit, que na
//      pratica e ninguem: o OnInit roda antes de qualquer jogador logar.

#ifndef CUSTOM_PLACA_DE_VENDA_HPP
#define CUSTOM_PLACA_DE_VENDA_HPP

#include <string>
#include <unordered_map>

#include <common/cbasetypes.hpp>
#include <common/strlib.hpp>

#include <map/clif.hpp>
#include <map/map.hpp>
#include <map/npc.hpp>
#include <map/pc.hpp>

#pragma pack(push, 1)

/// ZC_STORE_ENTRY (0x0131) - a placa de venda.
/// Declarado aqui, e nao reaproveitado de `packets_struct.hpp`, para este
/// arquivo poder ser incluido de qualquer lugar sem arrastar o cabecalho de
/// pacotes inteiro junto.
struct s_placa_de_venda_abre {
	int16 tipo;
	uint32 dono;
	char nome[MESSAGE_SIZE];
};

/// ZC_DISAPPEAR_ENTRY (0x0132) - tira a placa.
struct s_placa_de_venda_fecha {
	int16 tipo;
	uint32 dono;
};

#pragma pack(pop)

static_assert(sizeof(s_placa_de_venda_abre) == 86, "ZC_STORE_ENTRY tem 86 bytes");
static_assert(sizeof(s_placa_de_venda_fecha) == 6, "ZC_DISAPPEAR_ENTRY tem 6 bytes");

/// exname do NPC -> texto da placa. Fica em funcao para o `static` viver numa
/// unidade so, mesmo com o cabecalho incluido de varios .cpp.
inline std::unordered_map<std::string, std::string>& placa_de_venda_registro() {
	static std::unordered_map<std::string, std::string> registro;
	return registro;
}

/// Manda a placa de `nd` para `destino`. `alvo` nullptr = a area do proprio NPC.
inline void placa_de_venda_envia(npc_data& nd, const std::string& texto,
	block_list* alvo, enum send_target destino)
{
	s_placa_de_venda_abre p = {};

	p.tipo = 0x0131;
	p.dono = nd.id;
	safestrncpy(p.nome, texto.c_str(), sizeof(p.nome));

	clif_send(&p, sizeof(p), alvo != nullptr ? alvo : &nd, destino);
}

/// Tira a placa de `nd` da tela de todo mundo em volta.
inline void placa_de_venda_apaga(npc_data& nd) {
	s_placa_de_venda_fecha p = {};

	p.tipo = 0x0132;
	p.dono = nd.id;

	clif_send(&p, sizeof(p), &nd, AREA);
}

/// Define (ou remove, com texto vazio) a placa do NPC e avisa quem esta em volta.
inline void placa_de_venda_define(npc_data& nd, const char* texto) {
	auto& registro = placa_de_venda_registro();

	if (texto == nullptr || *texto == '\0') {
		registro.erase(nd.exname);
		placa_de_venda_apaga(nd);
		return;
	}

	registro[nd.exname] = texto;
	placa_de_venda_envia(nd, registro[nd.exname], nullptr, AREA);
}

/// O NPC entrou na visao de `sd`: manda a placa dele, se tiver uma.
/// Chamado do `clif_getareachar_unit`.
inline void placa_de_venda_mostra(npc_data& nd, map_session_data& sd) {
	auto& registro = placa_de_venda_registro();
	auto achado = registro.find(nd.exname);

	if (achado == registro.end())
		return;

	placa_de_venda_envia(nd, achado->second, &sd, SELF);
}

#endif /* CUSTOM_PLACA_DE_VENDA_HPP */
