// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// A ROLETA DO CASSINO - a roleta da captura de pet, sem o pet
// ===========================================================
//
// O que este arquivo faz: abre no cliente a roleta que ele desenha ao capturar
// um monstro, e responde o resultado que o SCRIPT escolheu, quando o jogador
// clica nela ou quando passam 10 segundos. Quem cobra, sorteia e paga e o NPC
// (npc/guerra/roleta_do_cassino.txt); aqui mora so o que script nao alcanca.
//
// ------------------------------------------------- como a roleta funciona no exe
//
// Medido no GuerraDoEmperium.exe em 2026-09-26, com capstone. A janela e a
// `UIPetTamingDeceiveWnd` (id de janela 0x5b, arte SlotMachine.spr), e o nome
// ja diz o que ela e: uma roleta de enganar, com o resultado decidido fora
// dela. A sequencia da captura de pet:
//
//   1. servidor manda 0x19e (ZC_START_CAPTURE) - o cursor de alvo aparece;
//   2. jogador clica num monstro - o CLIENTE abre a janela 0x5b girando e
//      guarda nela o id do alvo (mensagem 0x50, bandeira 0);
//   3. jogador clica na roleta - o cliente manda 0x19f (CZ_TRYCAPTURE_MONSTER)
//      com aquele id, e a roleta comeca a frear;
//   4. servidor responde 0x1a0 (ZC_TRYCAPTURE_MONSTER) - o cliente escolhe o
//      quadro onde ela para: 7 se ganhou, 3 se perdeu. Ela para ali, espera
//      2 segundos e fecha sozinha.
//
// Tres coisas desse desenho decidem este arquivo:
//
//   - O SERVIDOR NAO TEM COMO ABRIR A ROLETA. Quem abre e o passo 2, no
//     cliente; o 0x1a0 so atualiza uma janela que ja exista, e com ela
//     fechada nao faz nada. Por isso o exe ganhou um desvio
//     (ferramentas/abre_roleta_do_cassino.py): o 0x1a0 com resultado 2, que o
//     rAthena nunca manda, passou a significar "abra a roleta girando".
//   - O CLIQUE NA ROLETA CHEGA AO SERVIDOR (passo 3). E o 0x19f, o mesmo
//     pacote da captura - por isso o enxerto no clif_parse_CatchPet. Com a
//     roleta aberta pelo nosso 0x1a0 o alvo guardado e 0, e ele volta 0.
//   - A ROLETA NAO PARA SOZINHA. O unico teto de tempo da janela (o 10000 do
//     construtor, campo +0xa8) e de velocidade, nao de relogio: sem clique ela
//     gira para sempre. Os 10 segundos sao deste arquivo, num timer; ao
//     vencer, o servidor manda o resultado como se o clique tivesse chegado,
//     e o mesmo desvio do exe poe a janela no estado de "clicada" antes de
//     aplicar o quadro - sem isso ela pararia no quadro da animacao ociosa,
//     e um clique atrasado ainda reescreveria o quadro de parada para 7
//     (ganhou) na tela de quem perdeu.
//
// ------------------------------------------------ o que acontece em cada ponta
//
//   script  roletagira(<ganhou>, "<NPC::Evento>")
//             -> guarda {ganhou, evento}, manda 0x1a0 = 2, arma o timer
//   clique  0x19f chega -> roleta_do_cassino_clique -> resolve
//   10 s    timer vence -> resolve
//   resolve manda 0x1a0 = ganhou, apaga o pendente, roda o evento com o
//           jogador anexado. E o evento que paga.
//
// O EVENTO RODA NA HORA DO RESULTADO, e a roleta ainda leva uns instantes
// para frear. Quem quiser que o premio apareca depois dela parar espera no
// proprio evento (sleep2) - o numero fica no script, onde se ajusta sem
// recompilar.
//
// JOGADOR QUE SAI COM A ROLETA GIRANDO nao perde nada que o script tenha
// guardado: o timer vence, nao acha o personagem e so limpa o pendente. O
// premio mora em variavel permanente do personagem, gravada pelo script
// ANTES do giro, e e paga no proximo login. Aqui nao ha estado que precise
// sobreviver a nada.
//
// SEM O PATCH NO EXE, a roleta nao aparece e o jogo continua funcionando: o
// 0x1a0 = 2 cai no vazio (janela fechada), o timer vence em 10 segundos e o
// jogador recebe o resultado do mesmo jeito, so que sem animacao. Quem ainda
// nao baixou o patch joga as cegas, mas nao perde moeda.

#ifndef CUSTOM_ROLETA_DO_CASSINO_HPP
#define CUSTOM_ROLETA_DO_CASSINO_HPP

#include <unordered_map>

/// Quanto a roleta gira sem clique antes de o servidor parar por ela.
#define ROLETA_DO_CASSINO_ESPERA 10000

/// O valor do 0x1a0 que o desvio do exe le como "abra a roleta". O rAthena
/// so manda 0 e 1 (clif_pet_roulette recebe bool).
#define ROLETA_DO_CASSINO_ABRE 2

struct s_roleta_do_cassino {
	bool ganhou;
	int32 timer;
	char evento[EVENT_NAME_LENGTH];
};

/// Um giro por personagem, pela char_id. `inline` porque este cabecalho entra
/// em dois .cpp (clif.cpp e script.cpp) e os dois precisam ver o MESMO mapa.
inline std::unordered_map<uint32, s_roleta_do_cassino> roleta_do_cassino_giros;

inline void roleta_do_cassino_manda(map_session_data& sd, int8 valor)
{
	PACKET_ZC_TRYCAPTURE_MONSTER p{};

	p.PacketType = HEADER_ZC_TRYCAPTURE_MONSTER;
	p.result = valor;

	clif_send(&p, sizeof(p), &sd, SELF);
}

/// Da o resultado de um giro pendente e roda o evento que paga. Quem chama
/// ja tirou o timer do caminho (ou e o proprio timer).
inline void roleta_do_cassino_resolve(map_session_data& sd)
{
	auto it = roleta_do_cassino_giros.find(sd.status.char_id);

	if (it == roleta_do_cassino_giros.end())
		return;

	s_roleta_do_cassino giro = it->second;

	// Apaga ANTES de rodar o evento: o script pode querer girar de novo.
	roleta_do_cassino_giros.erase(it);

	roleta_do_cassino_manda(sd, giro.ganhou ? 1 : 0);
	npc_event(&sd, giro.evento, 0);
}

inline TIMER_FUNC(roleta_do_cassino_tempo)
{
	uint32 char_id = (uint32)data;
	auto it = roleta_do_cassino_giros.find(char_id);

	// O timer desta rodada ja foi desarmado pelo clique, ou e de um giro
	// anterior: nao e o nosso.
	if (it == roleta_do_cassino_giros.end() || it->second.timer != tid)
		return 0;

	map_session_data* sd = map_id2sd(id);

	if (sd == nullptr || sd->status.char_id != char_id) {
		// Saiu do jogo com a roleta girando. O premio, se houver, esta
		// guardado pelo script e sai no proximo login.
		roleta_do_cassino_giros.erase(it);
		return 0;
	}

	roleta_do_cassino_resolve(*sd);
	return 0;
}

/// Abre a roleta no cliente e arma os 10 segundos.
///
/// @return false se ja ha um giro deste personagem em andamento - nada foi
///         mandado, e o script nao deve cobrar.
inline bool roleta_do_cassino_gira(map_session_data& sd, bool ganhou, const char* evento)
{
	static bool registrado = false;

	if (!registrado) {
		add_timer_func_list(roleta_do_cassino_tempo, "roleta_do_cassino_tempo");
		registrado = true;
	}

	if (roleta_do_cassino_giros.count(sd.status.char_id))
		return false;

	s_roleta_do_cassino giro{};

	giro.ganhou = ganhou;
	safestrncpy(giro.evento, evento, sizeof(giro.evento));
	giro.timer = add_timer(gettick() + ROLETA_DO_CASSINO_ESPERA,
		roleta_do_cassino_tempo, sd.id, (intptr_t)sd.status.char_id);

	roleta_do_cassino_giros[sd.status.char_id] = giro;

	roleta_do_cassino_manda(sd, ROLETA_DO_CASSINO_ABRE);
	return true;
}

/// Enxerto no clif_parse_CatchPet: o 0x19f e o clique na roleta.
///
/// @return true se o pacote era da roleta do cassino e ja foi tratado - a
///         captura de pet NAO deve rodar. Captura de verdade (sem giro
///         pendente) passa direto.
inline bool roleta_do_cassino_clique(map_session_data& sd)
{
	auto it = roleta_do_cassino_giros.find(sd.status.char_id);

	if (it == roleta_do_cassino_giros.end())
		return false;

	delete_timer(it->second.timer, roleta_do_cassino_tempo);
	roleta_do_cassino_resolve(sd);
	return true;
}

#endif /* CUSTOM_ROLETA_DO_CASSINO_HPP */
