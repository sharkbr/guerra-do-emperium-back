// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// PINCEL DO INFINITO
// ==================
//
// O que este arquivo faz: quem tiver o **Pincel do Infinito** (item 30992) no
// inventario deixa de precisar de TRES insumos das habilidades de
// Trapaceiro/Renegado -
//
//     6121  Pincel de Maquiagem   (Makeover_Brush)  ferramenta das Mascaras
//     6122  Pincel de Grafite     (Paint_Brush)     ferramenta das Pinturas
//     6120  Tinta para Pele       (Face_Paint)      insumo GASTO pelas Mascaras
//
// - e o Pincel do Infinito nao e consumido, porque o que fazemos e ZERAR o
// requisito, nao paga-lo com outra coisa. E o mesmo mecanismo, o mesmo ponto de
// enxerto e a mesma justificativa da Tinta para Parede Infinita: ver
// `src/custom/tinta_infinita.hpp`, que explica por extenso por que
// `skill_get_requirement` e a fonte unica dos tres caminhos que olham o custo.
//
// ------------------------------------------- o que ele NAO cobre, de proposito
//
// A **Tinta para Parede (6123) continua exigindo a Tinta para Parede Infinita
// (30993)**. Os dois itens tem trabalhos separados e e assim que se quer: o
// Pincel substitui os dois PINCEIS e a tinta de ROSTO; a tinta de PAREDE e da
// Tinta Infinita. Quem quiser lancar a Copia Explosiva sem gastar nada precisa
// dos dois no inventario, e sao so dois - antes eram quatro.
//
// -------------------------------------- por que a ferramenta tambem precisa
//
// Porque `Amount: 0` no `db/re/skill_db.yml` NAO quer dizer "opcional". Os dois
// pinceis sao ferramenta: a habilidade exige que estejam no inventario e nunca
// os gasta. Quem cobra isso e o `skill_check_condition_castbegin`
// (src/map/skill.cpp:9559):
//
//     if( index[i] < 0 || sd.inventory...amount < require.amount[i] )
//
// - o `index[i] < 0` reprova mesmo com `require.amount[i] == 0`. Ou seja: sem o
// pincel na mochila a habilidade falha com "item necessario nao encontrado",
// exatamente como se faltasse a tinta. Zerar o `itemid` tira as duas coisas de
// uma vez, porque o laco pula todo requisito com id zero.
//
// -------------------------------------------- por que a regra e por ITEM
//
// Mesma razao do arquivo irmao: a condicao olha o INSUMO exigido, nao uma lista
// de habilidades, entao ela acompanha o `skill_db.yml` sozinha. Hoje isso
// alcanca treze habilidades, em dois grupos -
//
//     Tinta para Pele + Pincel de Maquiagem (as seis Mascaras):
//         SC_ENERVATION SC_GROOMY SC_IGNORANCE SC_LAZINESS SC_UNLUCKY
//         SC_WEAKNESS                                  (Id 2292 a 2297)
//
//     Pincel de Grafite (as sete Pinturas):
//         SC_BODYPAINT SC_MANHOLE SC_DIMENSIONDOOR SC_CHAOSPANIC
//         SC_MAELSTROM SC_BLOODYLUST SC_FEINTBOMB
//
// - e habilidade que passe a pedir um dos tres entra na isencao sem que se
// mexa aqui.
//
// ------------------------------------------------------------------- quem tem
//
// Hoje, so a staff: o item nasceu `NoDrop`/`NoTrade`/`NoSell`/`NoStorage` e nao
// esta em vitrine nenhuma nem em drop nenhum (db/guerra/item_db.yml, Id 30992).
// Entra por `@item 30992`. O primeiro uso pratico e o fantasma da arena
// (pvp_n_1-5), que passou a usar a Mascara da Vulnerabilidade a cada volta do
// ciclo e a Mascara da Tolice quando leva golpe pesado - sem esta isencao, uma
// Tinta para Pele por lance, reposta a mao para sempre.

#ifndef GUERRA_PINCEL_DO_INFINITO_HPP
#define GUERRA_PINCEL_DO_INFINITO_HPP

#include <common/cbasetypes.hpp>

#include <map/itemdb.hpp>
#include <map/pc.hpp>

// O rAthena tem ITEMID_PAINT_BRUSH (6122) em itemdb.hpp, mas nao tem constante
// para os outros dois - dai as nossas.
#define GUERRA_ITEMID_FACE_PAINT 6120
#define GUERRA_ITEMID_MAKEOVER_BRUSH 6121

// O Pincel do Infinito, nosso, faixa 30000-30999.
#define GUERRA_ITEMID_PINCEL_INFINITO 30992

/// Devolve true quando este requisito de item deve sumir da conta da
/// habilidade: e um dos tres que o Pincel do Infinito cobre, e o personagem
/// carrega o Pincel.
static bool pincel_do_infinito_dispensa(map_session_data *sd, t_itemid itemid)
{
	if (sd == nullptr)
		return false;

	if (itemid != GUERRA_ITEMID_FACE_PAINT
	 && itemid != GUERRA_ITEMID_MAKEOVER_BRUSH
	 && itemid != ITEMID_PAINT_BRUSH)
		return false;

	// pc_search_inventory devolve o indice, ou -1 se nao houver. Nao exigimos
	// quantidade: um unico Pincel basta, e ele nunca sai do inventario porque
	// este caminho nao o desconta de nada.
	return pc_search_inventory(sd, GUERRA_ITEMID_PINCEL_INFINITO) >= 0;
}

#endif // GUERRA_PINCEL_DO_INFINITO_HPP
