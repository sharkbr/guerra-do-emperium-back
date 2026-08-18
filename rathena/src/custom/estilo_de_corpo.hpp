// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// O CUPOM DE ROUPA E COMIDO E NADA MUDA
// =====================================
//
// O que este arquivo faz: traduzir o valor LEGADO de estilo de corpo (0 ou 1)
// para o ID do TRABALHO do visual alternativo do jogador, que e o que este
// rAthena de fato guarda em `LOOK_BODY2` hoje.
//
// O SINTOMA, relatado em 2026-08-17: o Estilista de Prontera
// (`Stylist#prontera`, prt_in 243,168, npc/re/merchants/Extended_Stylist.txt)
// aceita o Cupom de Roupa (6959), CONSOME o cupom, responde "sucesso" e o
// personagem continua exatamente igual.
//
// ------------------------------------------------------- de onde vem o defeito
//
// E dividido entre um banco de dados que o rAthena nao atualizou e um campo que
// mudou de significado por baixo dele:
//
//   1. `db/re/stylist.yml`, no fim, traz
//
//          - Look: Body2
//            Options:
//              - Index: 1
//                Value: 0        <- "sem visual alternativo"
//              - Index: 2
//                Value: 1        <- "com visual alternativo"
//
//      Esses 0 e 1 sao do tempo em que estilo de corpo era uma BANDEIRA.
//
//   2. No codigo de hoje, `LOOK_BODY2` guarda **o ID do trabalho** do visual
//      alternativo. Quem prova sao os dois lados do emulador:
//
//      - `db/re/job_outfits.yml` da a cada trabalho de 3a classe uma lista
//        `AlternateOutfits` (Rune_Knight -> Rune_Knight_2nd, e assim os treze),
//        e os `*_2ND` sao IDs da faixa 4332..4349 (src/common/mmo.hpp,
//        `JOB_SECOND_JOB_START = 4331`).
//      - o `@bodystyle` (src/map/atcommand.cpp) recusa qualquer numero que nao
//        seja `sd->status.class_` nem esteja no `alternate_outfits` do trabalho.
//
//      O proprio leitor do stylist admite o desencontro: em
//      `StylistDatabase::parseBodyNode` (src/map/npc.cpp) a checagem de faixa do
//      Body2 esta dentro de um `#if 0` com o comentario *"TODO: Unsupported for
//      now => This is job specific now"*. Ou seja: o rAthena SABE que aquele
//      valor deixou de servir e mesmo assim o carrega sem reclamar.
//
// Juntando os dois, o caminho do cupom fica assim:
//
//   clif_parse_stylist_buy_sub (src/map/clif.cpp)
//     -> pc_delitem   <- O CUPOM SOME AQUI, antes de qualquer visual mudar
//     -> pc_changelook(sd, LOOK_BODY2, 0 ou 1)
//          `job_db.exists(0)` e `job_db.exists(1)` sao Aprendiz e Espadachim:
//          existem, entao nada e recusado. Grava `status.body = 1`.
//     -> clif_changelook -> pacote de aparencia:
//          p.body = (look[LOOK_BODY2] > 4331 && < 4350) ? 1 : 0
//          1 nao esta naquela faixa, logo p.body = 0 -> visual PADRAO.
//
// Falha calada e cara: o servidor responde sucesso, o cliente nao erra, e o
// unico rastro e um cupom a menos na bolsa.
//
// -------------------------------------------------------- por que aqui, e nao
//                                                           num override de db/
//
// Nao da para consertar por `db/guerra/stylist.yml`. O valor certo **depende do
// trabalho de quem clicou** - Cavaleiro Runico quer 4332, Feiticeiro quer 4341 -
// e a tabela do stylist tem UMA lista global, um valor por indice. Foi
// exatamente por isso que o upstream desligou a validacao em vez de arrumar os
// numeros.
//
// Tambem nao da para tirar a opcao por override: o `parseBodyNode` MESCLA por
// `Look` + `Index` e nao tem como remover entrada nem zerar o custo de uma que
// ja exista (`entry_exists` faz o `CostsHuman` ausente ser ignorado em vez de
// virar nulo). Um override so alcanca o `Value`.
//
// ------------------------------------------------------------ o enxerto, e por
//                                                               que no pc.cpp
//
// A traducao mora no `pc_changelook`, no `case LOOK_BODY2:`, ANTES do
// `job_db.exists`. E uma linha ACRESCENTADA, nao uma substituicao - a regra da
// secao 2 do CLAUDE.md -, e cobre de uma vez os tres caminhos que escrevem esse
// campo: a UI do estilista, o `setlook` de script e o `@bodystyle`.
//
// O `@bodystyle` nao muda de comportamento: ele ja manda ID de trabalho
// (4332 e irmaos, ou `sd->status.class_` no `off`), e todo numero acima de 1
// sai daqui intocado.
//
// ------------------------------------------------------------ e a arte existe?
//
// Sim, conferido no `data.grf` deste cliente (2021-11-03) em 2026-08-17: a pasta
//
//     data\sprite\<humano>\<corpo>\<sexo>\costume_1\
//
// tem 127 sprites, um por trabalho de 3a classe e sexo - inclusive
// `<runeknight>_<sexo>_1.spr`. Quem escolhe a pasta e o CLIENTE, a partir do
// campo `body` do pacote de aparencia, que para o nosso PACKETVER ainda e uma
// bandeira 0/1 (src/map/clif.cpp, `#elif PACKETVER >= 20150513`). Ou seja: basta
// o servidor gravar um ID da faixa 4332..4349 para o desenho trocar.
//
// ------------------------------------------------------------ o que NAO muda
//
// Continua valendo o que o rAthena ja decidia, e nao e defeito:
//
// - so 3a classe (`JOBL_THIRD` e nao `JOBL_FOURTH`) chega a esta parte da
//   janela - `clif_parse_stylist_buy`, src/map/clif.cpp. Para os outros o
//   servidor responde sucesso e NAO come o cupom.
// - voltar ao visual padrao (Index 1) tambem custa um Cupom de Roupa; e o que o
//   `db/re/stylist.yml` diz, e nao foi mexido.

#ifndef CUSTOM_ESTILO_DE_CORPO_HPP
#define CUSTOM_ESTILO_DE_CORPO_HPP

#include <common/cbasetypes.hpp>

#include <map/pc.hpp>

/// Traduz o valor legado de estilo de corpo para ID de trabalho.
///
/// Regra, e a ambiguidade que ela resolve: **so 0 e 1 sao ambiguos.** Qualquer
/// outro numero ja e ID de trabalho - e o que o `@bodystyle` manda e o que esta
/// funcao mesma devolve -, entao sai intocado.
///
/// - `0` -> `sd->status.class_`, o "sem visual alternativo" do `@bodystyle off`.
/// - `n` -> `alternate_outfits[n - 1]`, o n-esimo visual alternativo do
///   trabalho. Hoje todo trabalho da lista tem exatamente um, entao na pratica
///   `1` e o unico usado; a forma indexada existe para o dia em que a Gravity
///   acrescentar o segundo, e para que o `Index` do `stylist.yml` continue
///   batendo com ele sem outra tabela no meio.
///
/// Nao ha colisao entre "valor legado" e "ID de trabalho de verdade": os IDs 0 e
/// 1 sao Aprendiz e Espadachim, e trabalho nenhum dessa faixa tem visual
/// alternativo - a funcao sai antes, no `alternate_outfits.empty()`.
///
/// @param sd Jogador
/// @param val Valor pedido, TROCADO no lugar quando for legado
inline void estilo_de_corpo_resolve(map_session_data* sd, int32* val)
{
	if (sd == nullptr || val == nullptr)
		return;

	if (*val < 0)
		return;

	std::shared_ptr<s_job_info> job = job_db.find(sd->status.class_);

	if (job == nullptr || job->alternate_outfits.empty())
		return;

	if (*val == 0) {
		*val = sd->status.class_;
		return;
	}

	if (static_cast<size_t>(*val) <= job->alternate_outfits.size())
		*val = job->alternate_outfits[*val - 1];
}

#endif /* CUSTOM_ESTILO_DE_CORPO_HPP */
