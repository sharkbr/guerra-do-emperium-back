// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// TINTA PARA PAREDE INFINITA
// ==========================
//
// O que este arquivo faz: quem tiver a **Tinta para Parede Infinita** (item
// 30993) no inventario deixa de precisar da Tinta para Parede comum (6123)
// para lancar as habilidades que a gastam. O item infinito NAO e consumido -
// ele nem chega a entrar na conta, porque o que fazemos e ZERAR o requisito,
// nao paga-lo com outra coisa.
//
// ------------------------------------------------ por que zerar o requisito
//
// Porque e o mecanismo que o proprio rAthena usa para isto, e ja estava a duas
// linhas do nosso enxerto (src/map/skill.cpp, skill_get_requirement):
//
//     // Check requirement for Magic Gear Fuel
//     if (req.itemid[i] == ITEMID_MAGIC_GEAR_FUEL && sd->special_state.no_mado_fuel)
//         req.itemid[i] = req.amount[i] = 0;
//
// O combustivel do Mado Gear some da lista de exigencias em vez de ser
// descontado. A Tinta Infinita entra na linha de baixo, com a mesma forma.
//
// E POR QUE UM SO PONTO BASTA, que e o detalhe que economiza o trabalho: o
// `skill_get_requirement` e a FONTE UNICA dos tres caminhos que olham o custo
// de uma habilidade -
//
//     skill_check_condition_castbegin   (skill.cpp:8349)  e quem recusa o lance
//     skill_check_condition_castend     (skill.cpp:9501)  revalida ao terminar
//     skill_consume_requirement         (skill.cpp:9606)  e quem apaga o item
//
// - entao zerar ali faz a habilidade PASSAR na checagem e NAO CONSUMIR nada, de
// uma vez so. Nao ha um segundo lugar a mexer, e nao ha risco de um caminho
// concordar e o outro nao.
//
// -------------------------------------------- por que a regra e por ITEM
//
// A condicao olha o INSUMO exigido (6123), nao uma lista de habilidades. Sao
// sete as que gastam Tinta para Parede hoje -
//
//     SC_FEINTBOMB     Copia Explosiva
//     SC_MANHOLE       Pintar Armadilha
//     SC_DIMENSIONDOOR Porta Dimensional
//     SC_CHAOSPANIC    Simbolo do Caos
//     SC_MAELSTROM     Redemoinho de Absorcao
//     SC_BLOODYLUST    Sede de Sangue
//     SC_BODYPAINT     Borrifar Tinta
//
// - e escrever a lista aqui seria uma segunda fonte da mesma verdade, que ia
// divergir do db/re/skill_db.yml no dia em que alguem mexesse nele. Pela via do
// item, a regra acompanha o banco sozinha: habilidade que passe a pedir Tinta
// entra na isencao, e a que deixe de pedir sai.
//
// ------------------------------------------------------- o que NAO e coberto
//
// O PINCEL DE GRAFITE (6122) NAO E COBERTO POR ESTE ARQUIVO. Ele ja e
// `Amount: 0` no skill_db - a habilidade pede que ele esteja no inventario mas
// nunca o gasta -, entao ele nao e um custo que se esgota, e uma ferramenta.
// Custa 10z na Tranqueiras (npc/guerra/tranqueiras.txt) e vale uma vez so.
// Quem estiver com a Tinta Infinita e sem o Pincel continua sem lancar, e o
// erro no cliente e o mesmo "item necessario nao encontrado".
//
// Em 2026-08-28 isso ganhou resposta, e ela mora em OUTRO arquivo: o **Pincel
// do Infinito** (30992, `src/custom/pincel_do_infinito.hpp`) dispensa os dois
// pinceis (6121 e 6122) e a Tinta para Pele (6120). Ficaram dois itens com
// trabalhos separados de proposito - este cuida da tinta de PAREDE, aquele dos
// PINCEIS e da tinta de PELE -, e os dois entram na mesma linha do
// `skill_get_requirement`. Nao juntar os dois num arquivo so foi decisao: sao
// dois itens de jogo distintos, e um dia um pode existir sem o outro.
//
// ------------------------------------------------------------------- quem tem
//
// Hoje, so a staff: o item nasceu `NoDrop`/`NoTrade`/`NoSell`/`NoStorage` e nao
// esta em vitrine nenhuma nem em drop nenhum (db/guerra/item_db.yml, Id 30993).
// Entra por `@item 30993`. A intencao registrada do dono e que mais para a
// frente ele vire objetivo de uma quest grande - quando isso acontecer, o que
// muda e o item_db e o NPC da quest, nao este arquivo.
//
// O primeiro uso pratico e o fantasma da arena (pvp_n_1-5), que lanca a Copia
// Explosiva a cada volta do ciclo de combate - da ordem de oito mil Tintas por
// dia se fosse pagar por elas.

#ifndef GUERRA_TINTA_INFINITA_HPP
#define GUERRA_TINTA_INFINITA_HPP

#include <common/cbasetypes.hpp>

#include <map/itemdb.hpp>
#include <map/pc.hpp>

// A Tinta para Parede comum. O rAthena tem ITEMID_PAINT_BRUSH (6122) em
// itemdb.hpp, mas nao tem constante para esta - dai a nossa.
#define GUERRA_ITEMID_SURFACE_PAINT 6123

// A Tinta para Parede Infinita, nossa, faixa 30000-30999.
#define GUERRA_ITEMID_TINTA_INFINITA 30993

/// Devolve true quando este requisito de item deve sumir da conta da
/// habilidade: e Tinta para Parede, e o personagem carrega a Infinita.
static bool tinta_infinita_dispensa(map_session_data *sd, t_itemid itemid)
{
	if (sd == nullptr)
		return false;

	if (itemid != GUERRA_ITEMID_SURFACE_PAINT)
		return false;

	// pc_search_inventory devolve o indice, ou -1 se nao houver. Nao
	// exigimos quantidade: uma unica Tinta Infinita basta, e ela nunca sai
	// do inventario porque este caminho nao a desconta de nada.
	return pc_search_inventory(sd, GUERRA_ITEMID_TINTA_INFINITA) >= 0;
}

#endif // GUERRA_TINTA_INFINITA_HPP
