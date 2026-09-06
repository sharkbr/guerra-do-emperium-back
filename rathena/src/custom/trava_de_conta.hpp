// Guerra do Emperium - codigo nosso. O upstream so ganha ponteiro para ca.
//
// TRAVA DE CONTA POR SENHA ERRADA
// ===============================
//
// O que este arquivo faz: conta quantas senhas erradas cada CONTA levou nos
// ultimos minutos e, ao chegar no limite, suspende AQUELA CONTA por um tempo
// curto que expira sozinho. Nao ha lista para limpar a mao, nao ha chamado
// para abrir, e nenhum outro jogador e afetado.
//
// Substitui o ban dinamico de IP do rAthena, que passou a ficar desligado em
// conf/guerra/login_guerra.txt. Decisao do dono em 2026-09-05.
//
// ------------------------------------------------- por que trocar de alvo
//
// O rAthena ja tinha uma trava de forca bruta, e ela pune o lugar errado. O
// ipban_log (src/login/ipban.cpp:71) conta as falhas POR IP e, ao passar do
// limite, insere na ipbanlist a faixa
//
//     '%u.%u.%u.*'      ou seja o /24 INTEIRO - ate 254 enderecos
//
// Quem cai nessa faixa leva "Rejected from Server" ANTES de o login ser lido
// (loginclif.cpp, no logclif_parse) - nao importa a conta, nao importa a
// senha, e nao importa se a pessoa acabou de chegar. Num provedor brasileiro
// comum, vizinho de rua e jogador de celular na mesma saida NAT dividem esse
// /24.
//
// Foi medido, e foi o caso que originou este arquivo. Em 2026-09-05 um
// jogador errou a senha sete vezes entre 13:09 e 13:12, alternando entre as
// duas contas dele; das 13:16 as 13:17 o loginlog registra sete linhas
//
//     179.113.122.223  unknown  -3  ip banned
//
// e ele relatou a mensagem "Rejected from the Server (3)". Ele nao estava
// bloqueado por nada: a faixa dele estava. E a mensagem nao diz isso, nao diz
// por quanto tempo, e nao e a mesma que aparece quando a senha esta errada -
// entao do lado de la parecia conta banida.
//
// ------------------------------------------------------- o preco da troca
//
// Trava por conta tem uma fraqueza que a de IP nao tem: quem souber o nome de
// uma conta consegue suspende-la de proposito, so digitando senha errada. E o
// nome da conta nao e segredo - o jogador o escolhe e o digita na frente dos
// outros.
//
// O que torna isso aceitavel aqui e a suspensao EXPIRAR SOZINHA em 15
// minutos. O estrago maximo de quem quiser incomodar e esse quarto de hora, e
// custa ao atacante ficar digitando; nao ha estado acumulado, nao ha nada que
// se perca, e nao ha ninguem para destravar. Trava permanente - a outra opcao
// considerada em 2026-09-05 - transformaria o mesmo ataque em dano indefinido,
// e cada esquecimento de senha num chamado, sem painel para atender.
//
// ------------------------------------------- onde a suspensao e guardada
//
// Na coluna `unban_time` da tabela `login`, que e o campo que o rAthena ja usa
// para ban temporario (@block/@ban). Isso e de proposito, e da tres coisas de
// graca:
//
//   1. o login_mmo_auth ja testa esse campo e devolve o erro 6, que e a unica
//      recusa que o cliente MOSTRA COM DATA ("You are prohibited to log in
//      until %s") - o jogador ve a que horas pode voltar;
//   2. o char-server e o map-server ja respeitam o campo;
//   3. nao e preciso coluna, tabela nem migracao nenhuma.
//
// A guarda que isso exige esta no fim do trava_de_conta_erro: NUNCA ENCURTAR
// UM BAN QUE JA EXISTA. Se um GM bloqueou a conta ate o ano que vem, nossos 15
// minutos nao podem passar por cima - por isso o campo so e escrito quando o
// valor novo for maior que o que ja esta la.
//
// ----------------------------------------------- por que a contagem e em RAM
//
// O ipban_log consulta o loginlog para contar. Nao seguimos por ali de
// proposito: aquilo e uma consulta ao banco por senha errada, e esta contagem
// nao precisa sobreviver a nada. Reiniciar o login-server zera os contadores,
// e isso e desejavel - o reinicio ja derruba todo mundo, e ninguem deve voltar
// dele a um passo de ser suspenso.
//
// A tabela em RAM e pequena por construcao: so entra conta que ERROU a senha,
// a entrada morre no primeiro acerto, e o trava_de_conta_limpa varre o que
// expirou a cada chamada.
//
// ------------------------------------------------------- o que o jogador ve
//
// Nas seis primeiras erradas, o erro 1 - a frase do msgstringtable id 7, que
// foi reescrita no NOSSO cliente para avisar do limite ANTES de ele chegar.
// Isso so alcanca quem pegou o patch (CLAUDE.md secao 4.18); quem nao pegou
// continua vendo a frase em ingles, e a trava funciona igual.
//
// Na setima, e em qualquer tentativa durante os 15 minutos, o erro 6 com a
// hora da volta. Esse caminho depende da correcao do unblock_time no
// loginclif.cpp - sem ela o rAthena manda a data VAZIA e a frase sai pela
// metade. A correcao esta la, comentada, e e enxerto nosso.

#ifndef GUERRA_TRAVA_DE_CONTA_HPP
#define GUERRA_TRAVA_DE_CONTA_HPP

#include <ctime>
#include <map>
#include <string>

#include <common/cbasetypes.hpp>
#include <common/showmsg.hpp>

#include <login/account.hpp>

// Quantas senhas erradas suspendem a conta. A setima e a que trava: a contagem
// inclui a tentativa em curso, porque o trava_de_conta_erro roda depois de o
// login_log ja ter registrado a falha - a mesma ordem que o rAthena usa no
// ipban_log.
#define GUERRA_TRAVA_LIMITE 7

// Janela da contagem, em segundos. Erro isolado de quem so se atrapalhou nao
// se soma ao de meia hora atras.
#define GUERRA_TRAVA_JANELA (5 * 60)

// Quanto tempo a conta fica suspensa, em segundos.
#define GUERRA_TRAVA_SUSPENSAO (15 * 60)

struct guerra_trava_registro {
	int32 erros;      // quantas erradas dentro da janela
	time_t ultimo;    // quando foi a ultima - e o que envelhece a entrada
};

static std::map<std::string, guerra_trava_registro> guerra_trava_contador;

/// Descarta entradas cuja janela ja passou. Roda a cada erro, que e raro o
/// bastante para o custo nao importar e frequente o bastante para a tabela
/// nunca crescer.
static void trava_de_conta_limpa( time_t agora ){
	for( auto it = guerra_trava_contador.begin(); it != guerra_trava_contador.end(); ){
		if( agora - it->second.ultimo > GUERRA_TRAVA_JANELA ){
			it = guerra_trava_contador.erase( it );
		}else{
			++it;
		}
	}
}

/// Apaga a contagem de uma conta. Chamado quando ela entra: acertar a senha
/// desfaz o caminho andado, senao quem erra tres vezes hoje e quatro amanha
/// acabaria suspenso sem nunca ter errado seis seguidas.
static void trava_de_conta_esquece( const char* userid ){
	if( userid == nullptr || *userid == '\0' ){
		return;
	}

	guerra_trava_contador.erase( std::string( userid ) );
}

/// Registra uma senha errada e, no limite, suspende a conta.
///
/// Devolve true se ACABOU de suspender, so para quem chama poder avisar no
/// console. A recusa em si nao sai daqui: ela vem do proprio login_mmo_auth na
/// tentativa seguinte, pelo unban_time, que e o caminho que o rAthena ja tem.
static bool trava_de_conta_erro( AccountDB* accounts, const char* userid ){
	if( accounts == nullptr || userid == nullptr || *userid == '\0' ){
		return false;
	}

	time_t agora = time( nullptr );

	trava_de_conta_limpa( agora );

	std::string chave( userid );
	guerra_trava_registro& reg = guerra_trava_contador[chave];

	// Entrada recem-criada pelo operator[] (zerada), ou entrada cuja janela
	// expirou entre uma tentativa e outra.
	if( reg.ultimo == 0 || agora - reg.ultimo > GUERRA_TRAVA_JANELA ){
		reg.erros = 0;
	}

	reg.erros++;
	reg.ultimo = agora;

	if( reg.erros < GUERRA_TRAVA_LIMITE ){
		return false;
	}

	struct mmo_account acc;

	// Conta que nao existe nao tem o que suspender, e isso acontece: o erro 0
	// (usuario desconhecido) tambem passa por aqui, e alguem pode estar
	// chutando nome de conta.
	if( !accounts->load_str( accounts, &acc, userid ) ){
		return false;
	}

	// A CONTA DE SEXO 'S' NUNCA E SUSPENSA, e esta guarda nao e teorica: e com
	// ela que o char-server e o map-server se conectam ao login (o
	// logclif_parse_reqcharconnec passa pelo mesmo login_mmo_auth, e o
	// logclif_auth_failed pelo mesmo caminho daqui). Sem isto, sete tentativas
	// contra o nome dessa conta - que qualquer um pode chutar - derrubariam a
	// ligacao entre os servidores por 15 minutos, e o sintoma apareceria longe:
	// jogador preso na tela de login, sem nada de errado no map-server.
	// O rAthena usa sex_str2num (src/login/login.hpp:129), que trata como
	// SEX_SERVER tudo que nao for 'M' nem 'F'; a comparacao direta evita
	// arrastar login.hpp para dentro deste cabecalho.
	if( acc.sex != 'M' && acc.sex != 'F' ){
		return false;
	}

	time_t ate = agora + GUERRA_TRAVA_SUSPENSAO;

	// NUNCA encurtar ban que ja exista - ver o cabecalho.
	if( acc.unban_time >= ate ){
		return false;
	}

	acc.unban_time = ate;

	if( !accounts->save( accounts, &acc, false ) ){
		ShowError( "trava_de_conta: nao consegui suspender a conta '%s'.\n", userid );
		return false;
	}

	// Zera a contagem: a conta ja esta suspensa, e as tentativas dos proximos
	// 15 minutos nao devem empilhar uma suspensao em cima da outra.
	guerra_trava_contador.erase( chave );

	ShowNotice( "Conta '%s' suspensa por %d minutos apos %d senhas erradas.\n",
		userid, GUERRA_TRAVA_SUSPENSAO / 60, GUERRA_TRAVA_LIMITE );

	return true;
}

#endif /* GUERRA_TRAVA_DE_CONTA_HPP */
