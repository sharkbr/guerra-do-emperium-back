package main

import (
	"errors"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// O PAINEL DE USUARIOS - a area do site em que o dono ve' e mexe na conta
// dos outros. Estreou em 2026-09-10, depois de um jogador errar a senha
// algumas vezes e ficar sem conseguir entrar.
//
// O QUE ELE PRECISA DIZER ANTES DE QUALQUER OUTRA COISA: desde 2026-09-06
// (CLAUDE.md secao 4.23) errar a senha sete vezes suspende AQUELA CONTA por
// 15 minutos, e nao mais a faixa de IP. A suspensao vai para o `unban_time`,
// o mesmo campo do @ban - entao castigo de gente e trava de maquina moram na
// MESMA coluna e chegam aqui com a mesma cara. Separa-los e' o travaAutomatica
// de banco_admin.go, e nao e' capricho: sem o rotulo, o operador ve'
// "suspensa" na ficha de quem so' esqueceu a senha e pune de novo.
//
// QUEM ENTRA AQUI: `login.group_id >= 99`, o grupo Admin do
// conf/groups.yml - o mesmo que da' o @ no jogo. Lido do banco a cada
// requisicao (ver o cabecalho de Conta em banco.go): o cookie nao carrega
// grupo nenhum, entao tirar o 99 de alguem fecha a porta na requisicao
// seguinte.
//
// AS TRES TRAVAS QUE NAO SE TIRAM, e cada uma existe por um motivo
// diferente:
//
//  1. NAO SE BLOQUEIA A CONTA DE SERVIDOR (sexo 'S'). E' com ela que o
//     char-server e o map-server falam com o login-server; bloquea-la
//     derruba o jogo inteiro para todo mundo. A trava esta' aqui E no WHERE
//     de cada UPDATE (banco_admin.go).
//  2. NAO SE BLOQUEIA OUTRO ADMINISTRADOR, nem a si mesmo. Um clique errado
//     ali tira do jogo justamente quem consertaria o clique errado.
//  3. BLOQUEAR E SUSPENDER PEDEM A SENHA de quem esta' clicando; LIBERAR
//     nao pede. E' a mesma regra que o resto do painel ja' segue (api.go):
//     o que mexe em ACESSO pede senha, porque um cookie roubado nao pode
//     bastar. Liberar devolve acesso - o pior que um cookie roubado faz com
//     ele e' desfazer uma punicao, que se refaz num clique.
//
// O QUE ESTE PAINEL NAO FAZ, e e' a parte que precisa estar clara:
// bloquear NAO EXPULSA quem ja' esta' jogando. O @block do jogo manda o
// pacote 0x2731 do login-server para os outros servidores
// (loginchrif.cpp:335), e e' esse pacote que derruba a sessao aberta.
// Escrevendo direto no banco nao ha' pacote nenhum: o bloqueio vale a
// partir do LOGIN SEGUINTE. Por isso a ficha mostra "conectado agora" - e'
// a informacao que diz ao administrador se ele ainda precisa de um @kick no
// jogo.

// O teto de acoes por hora, por administrador. Nao existe para conter o
// dono - existe para um cookie roubado nao bloquear o servidor inteiro em
// dois minutos. Sessenta e' folga larga para moderacao de verdade.
const acoesAdminPorHora = 60

// Tamanho da pagina da lista.
const contasPorPagina = 50

// Limites do formulario de moderacao.
const (
	maxMotivo    = 255    // guerra_site_admin_log.motivo varchar(255)
	minMotivo    = 3      // menos que isso nao e' motivo, e' ruido
	maxSuspensao = 525600 // um ano em minutos
)

// exigeAdmin e' a guarda de todas as rotas deste arquivo.
//
// A resposta para quem tem sessao valida e nao e' administrador e' 404, e
// nao 403: um 403 confirma que a rota existe, e a lista de rotas de um site
// e' meio caminho para quem procura o que atacar. Para o front nao faz
// diferenca - ele so' desenha o botao quando /api/painel diz que ha'
// permissao.
func (s *Servidor) exigeAdmin(w http.ResponseWriter, r *http.Request) (*Conta, bool) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return nil, false
	}
	if c.Grupo < grupoAdmin {
		falha(w, http.StatusNotFound, "nao encontrado")
		return nil, false
	}
	return c, true
}

// situacaoDe resume o estado da conta numa palavra e numa frase.
//
// A ORDEM DOS TESTES E' A REGRA, porque as colunas sao independentes e uma
// conta pode estar em mais de um estado ao mesmo tempo. Vale o que barra
// primeiro no login_mmo_auth (login.cpp:360): prazo de validade, depois
// suspensao, depois bloqueio.
func situacaoDe(c *ContaAdmin) (string, string) {
	agora := time.Now().Unix()

	switch {
	case c.ContaDeServidor():
		return "servidor", "Conta de servidor — é com ela que o jogo conversa consigo mesmo. Não se mexe."
	case c.Expira != 0 && c.Expira <= agora:
		return "expirada", "O prazo de validade da conta venceu."
	case c.Suspensa > agora:
		ate := time.Unix(c.Suspensa, 0).Format("15:04")
		if travaAutomatica(c, time.Now()) {
			// O caso mais comum e o que menos parece: nao e' castigo, e
			// nao ha' nada a fazer. Dizer isso na primeira linha da ficha
			// e' o que evita punir de novo quem so' esqueceu a senha.
			return "trava", "Travada sozinha por errar a senha " +
				strconv.Itoa(travaLimiteErros) + " vezes. Libera às " + ate +
				", sem ninguém precisar fazer nada."
		}
		return "suspensa", "Suspensa até " +
			time.Unix(c.Suspensa, 0).Format("02/01/2006 15:04") + "."
	case c.Estado == estadoBloqueada:
		return "bloqueada", "Bloqueada. No cliente aparece como bloqueio da equipe do servidor."
	case c.Estado != estadoSolta:
		// Estado que o painel nao escreve, mas que o emulador pode ter
		// posto ali. Mostrar o numero cru e' melhor que inventar um nome.
		return "bloqueada", "Bloqueada pelo emulador (state " + strconv.Itoa(c.Estado) + ")."
	default:
		return "ok", "Entra normalmente."
	}
}

func instante(t time.Time) any {
	if t.IsZero() {
		return nil
	}
	return t.Format(time.RFC3339)
}

// contas lista as contas e, junto, os bloqueios de IP ativos.
//
// OS DOIS VEM NA MESMA RESPOSTA de proposito. O bloqueio de IP e' o que
// trava quem erra a senha, e ele nao aparece em coluna nenhuma da conta -
// quem for procurar o motivo de um jogador nao entrar olhando so' a ficha
// dele nao encontra nada, e conclui que o problema e' outro. Vindo lado a
// lado, a resposta esta' na mesma tela da pergunta.
func (s *Servidor) adminContas(w http.ResponseWriter, r *http.Request) {
	if _, ok := s.exigeAdmin(w, r); !ok {
		return
	}

	pagina, _ := strconv.Atoi(r.URL.Query().Get("pagina"))
	if pagina < 0 {
		pagina = 0
	}
	busca := r.URL.Query().Get("busca")

	lista, total, err := s.banco.Contas(busca, contasPorPagina, pagina*contasPorPagina)
	if err != nil {
		falha(w, http.StatusInternalServerError, "não consegui ler as contas")
		return
	}
	// Falha macia: sem o loginlog o painel perde os numeros de tentativa e
	// continua servindo para tudo o mais. Ver CompletaComTentativas.
	if err := s.banco.CompletaComTentativas(lista); err != nil {
		logaFalta("loginlog/ipbanlist", err)
	}

	saida := make([]resposta, 0, len(lista))
	for i := range lista {
		c := &lista[i]
		situacao, texto := situacaoDe(c)
		saida = append(saida, resposta{
			"id":             c.ID,
			"usuario":        c.Usuario,
			"email":          c.Email,
			"sexo":           c.Sexo,
			"grupo":          c.Grupo,
			"admin":          c.Grupo >= grupoAdmin,
			"situacao":       situacao,
			"situacao_texto": texto,
			"trava_auto":     travaAutomatica(c, time.Now()),
			// pode_moderar e' calculado no SERVIDOR e nao inferido no
			// front: e' a mesma conta que o handler de acao vai fazer, e
			// duas contas separadas divergem.
			"pode_moderar":     podeModerar(c) == nil,
			"suspensa_ate":     epochOuNada(c.Suspensa),
			"expira_em":        epochOuNada(c.Expira),
			"logins":           c.Logins,
			"ultimo_login":     instanteNulo(c.UltimoLogin.Valid, c.UltimoLogin.Time),
			"ultimo_ip":        c.UltimoIP,
			"personagens":      c.Personagens,
			"online":           c.Online,
			"falhas":           c.Falhas,
			"ultima_tentativa": instanteNulo(c.UltimaTenta.Valid, c.UltimaTenta.Time),
			"ip_tentado":       c.IPTentado,
			"faixa_banida":     c.FaixaBanida,
			"barrado_por_ip":   c.BarradoPorIP,
		})
	}

	bloqueios := []resposta{}
	if bans, err := s.banco.IPsBanidos(); err != nil {
		logaFalta("ipbanlist", err)
	} else {
		for _, v := range bans {
			bloqueios = append(bloqueios, resposta{
				"faixa":  v.Faixa,
				"desde":  instante(v.Desde),
				"ate":    instante(v.Ate),
				"motivo": v.Motivo,
				// Em segundos, e nao uma frase pronta: o front desenha
				// "faltam 3 min" e continua certo enquanto a tela fica
				// aberta, o que uma frase do servidor nao faria.
				"restam": int(time.Until(v.Ate).Seconds()),
			})
		}
	}

	devolve(w, http.StatusOK, resposta{
		"contas":       saida,
		"total":        total,
		"pagina":       pagina,
		"por_pagina":   contasPorPagina,
		"ip_bloqueios": bloqueios,
	})
}

func epochOuNada(v int64) any {
	if v == 0 {
		return nil
	}
	return time.Unix(v, 0).Format(time.RFC3339)
}

func instanteNulo(valido bool, t time.Time) any {
	if !valido {
		return nil
	}
	return instante(t)
}

// podeModerar diz se a conta aceita bloqueio/suspensao, e devolve o motivo
// de nao aceitar. Uma funcao so', usada pela listagem e pela acao, para as
// duas nunca discordarem - botao habilitado que o servidor recusa e' pior
// que botao desabilitado.
func podeModerar(c *ContaAdmin) error {
	if c.ContaDeServidor() {
		return errors.New("essa é a conta de serviço do servidor; bloqueá-la derruba o jogo para todo mundo")
	}
	if c.Grupo >= grupoAdmin {
		return errors.New("essa conta é de administrador; troque o grupo dela no banco antes, se for mesmo o caso")
	}
	return nil
}

// adminAcao e' o unico endereco que ESCREVE na conta de outra pessoa.
func (s *Servidor) adminAcao(w http.ResponseWriter, r *http.Request) {
	admin, ok := s.exigeAdmin(w, r)
	if !ok {
		return
	}
	if !s.limiteAdmin.Permite("admin:" + strconv.FormatInt(admin.ID, 10)) {
		falha(w, http.StatusTooManyRequests,
			"muitas ações seguidas. Espere um pouco antes de continuar.")
		return
	}

	var p struct {
		Conta   int64  `json:"conta"`
		Acao    string `json:"acao"`
		Minutos int    `json:"minutos"`
		Motivo  string `json:"motivo"`
		Senha   string `json:"senha"`
	}
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}
	p.Acao = strings.TrimSpace(p.Acao)
	p.Motivo = strings.TrimSpace(p.Motivo)

	alvo, err := s.banco.PorIDAdmin(p.Conta)
	if errors.Is(err, ErrNaoAchou) {
		falha(w, http.StatusNotFound, "conta não encontrada")
		return
	}
	if err != nil {
		falha(w, http.StatusInternalServerError, "erro ao consultar o banco")
		return
	}

	// As tentativas de senha VEM JUNTO, e nao so' na listagem.
	//
	// O PorIDAdmin le' a `login` e mais nada, entao `Falhas` chega zerado - e
	// o travaAutomatica, que depende dela, responderia "nao" para toda conta.
	// Sem esta linha, liberar uma conta travada sozinha daria a mensagem
	// generica em vez do aviso sobre a contagem em RAM, e o registro de
	// moderacao diria "de suspensa" onde era "de trava". A mesma falta ja'
	// tinha escondido o aviso de @kick uma vez - ver PorIDAdmin.
	//
	// Falha macia, como na listagem: sem o loginlog o rotulo se perde e a
	// acao acontece igual.
	umAlvo := []ContaAdmin{*alvo}
	if err := s.banco.CompletaComTentativas(umAlvo); err != nil {
		logaFalta("loginlog/ipbanlist", err)
	} else {
		*alvo = umAlvo[0]
	}

	// A comparacao e' por account_id e nao por nome: nome vem do banco nas
	// duas pontas, mas o id e' o que a sessao carrega.
	if alvo.ID == admin.ID && p.Acao != "liberar" {
		falha(w, http.StatusConflict,
			"essa é a sua própria conta — bloqueá-la tiraria você do jogo sem ninguém para desfazer")
		return
	}

	switch p.Acao {
	case "liberar":
		s.adminLibera(w, r, admin, alvo, p.Motivo)
	case "bloquear", "suspender":
		if err := podeModerar(alvo); err != nil {
			falha(w, http.StatusConflict, err.Error())
			return
		}
		// Ver a trava 3 no cabecalho: o que mexe em acesso pede a senha de
		// quem esta' clicando, porque um cookie roubado nao pode bastar.
		if _, err := s.banco.PorUsuarioESenha(admin.Usuario, md5hex(p.Senha)); err != nil {
			falha(w, http.StatusUnauthorized, "a sua senha não confere")
			return
		}
		if n := len([]rune(p.Motivo)); n < minMotivo || n > maxMotivo {
			falha(w, http.StatusBadRequest,
				"escreva o motivo, de 3 a 255 caracteres — é o que explica a decisão depois")
			return
		}
		if p.Acao == "bloquear" {
			s.adminBloqueia(w, r, admin, alvo, p.Motivo)
		} else {
			s.adminSuspende(w, r, admin, alvo, p.Minutos, p.Motivo)
		}
	default:
		falha(w, http.StatusBadRequest, "ação desconhecida")
	}
}

// deParaDe descreve a mudanca como "de <o que era> para <o que virou>".
//
// O "de" e' a parte que importa e a que se perderia: o registro guarda o
// estado ANTERIOR, que e' o unico lugar de onde ele ainda pode ser lido
// depois de a coluna ter sido sobrescrita. Sem ele, desfazer um bloqueio
// errado seria adivinhar.
func deParaDe(antes *ContaAdmin, virou string) string {
	de, _ := situacaoDe(antes)
	return "de " + de + " (state " + strconv.Itoa(antes.Estado) +
		", unban_time " + strconv.FormatInt(antes.Suspensa, 10) + ") para " + virou
}

func (s *Servidor) adminLibera(w http.ResponseWriter, r *http.Request,
	admin *Conta, alvo *ContaAdmin, motivo string) {

	antes, _ := situacaoDe(alvo)
	if antes == "ok" {
		falha(w, http.StatusConflict, "essa conta já entra normalmente")
		return
	}

	if err := s.banco.Libera(alvo.ID); err != nil {
		if errors.Is(err, ErrContaDeServidor) {
			falha(w, http.StatusConflict, "essa é a conta de serviço do servidor")
			return
		}
		falha(w, http.StatusInternalServerError, "não consegui liberar a conta")
		return
	}
	s.registra(admin, alvo, "liberar", deParaDe(alvo, "solta"), motivo, r)

	// LIBERAR A CONTA NAO TIRA O BLOQUEIO DE IP, e o painel diz isso em vez
	// de resolver sozinho: sao coisas de alcance diferente, e a faixa
	// alcanca gente que nao tem nada com esta conta. Quem decide e' o
	// administrador, no botao da outra lista.
	msg := "Conta liberada. Ela já entra no próximo login."
	if antes == "trava" {
		// A contagem de erros vive em RAM no login-server e NAO e' zerada
		// por escrever no banco (trava_de_conta.hpp). Ela morre no primeiro
		// acerto de senha ou depois de cinco minutos sem erro novo - ate'
		// la', duas erradas a mais tornam a trancar.
		msg = "Trava liberada. Ela entra agora — mas se errar a senha de novo " +
			"nos próximos minutos, tranca outra vez: quem zera a contagem é " +
			"acertar a senha."
	}
	devolve(w, http.StatusOK, resposta{"ok": true, "mensagem": msg})
}

func (s *Servidor) adminBloqueia(w http.ResponseWriter, r *http.Request,
	admin *Conta, alvo *ContaAdmin, motivo string) {

	if err := s.banco.Bloqueia(alvo.ID); err != nil {
		if errors.Is(err, ErrContaDeServidor) {
			falha(w, http.StatusConflict, "essa é a conta de serviço do servidor")
			return
		}
		falha(w, http.StatusInternalServerError, "não consegui bloquear a conta")
		return
	}
	s.registra(admin, alvo, "bloquear", deParaDe(alvo,
		"state "+strconv.Itoa(estadoBloqueada)+", sem prazo"), motivo, r)

	devolve(w, http.StatusOK, resposta{
		"ok":       true,
		"mensagem": avisoDeSessaoAberta(alvo, "Conta bloqueada."),
	})
}

func (s *Servidor) adminSuspende(w http.ResponseWriter, r *http.Request,
	admin *Conta, alvo *ContaAdmin, minutos int, motivo string) {

	if minutos < 1 || minutos > maxSuspensao {
		falha(w, http.StatusBadRequest, "escolha um prazo entre 1 minuto e 1 ano")
		return
	}
	ate := time.Now().Add(time.Duration(minutos) * time.Minute)

	if err := s.banco.Suspende(alvo.ID, ate); err != nil {
		if errors.Is(err, ErrContaDeServidor) {
			falha(w, http.StatusConflict, "essa é a conta de serviço do servidor")
			return
		}
		falha(w, http.StatusInternalServerError, "não consegui suspender a conta")
		return
	}
	s.registra(admin, alvo, "suspender", deParaDe(alvo,
		"prazo ate' "+ate.Format("02/01/2006 15:04")+" ("+strconv.Itoa(minutos)+" min)"), motivo, r)

	devolve(w, http.StatusOK, resposta{
		"ok": true,
		"mensagem": avisoDeSessaoAberta(alvo,
			"Conta suspensa até "+ate.Format("02/01/2006 15:04")+"."),
	})
}

// avisoDeSessaoAberta acrescenta o recado que evita o mal-entendido mais
// provavel deste painel: a punicao vale do proximo login em diante, e quem
// ja' esta' dentro do jogo continua dentro. Ver o cabecalho do arquivo.
func avisoDeSessaoAberta(alvo *ContaAdmin, base string) string {
	if alvo.Online > 0 {
		return base + " ATENÇÃO: há personagem dessa conta conectado agora, e o " +
			"bloqueio só vale a partir do próximo login — use @kick no jogo para " +
			"tirá-lo agora."
	}
	return base + " Vale a partir do próximo login."
}

// adminLiberaIP tira um bloqueio de faixa de IP - o que trava quem erra a
// senha, e que nao tem nada a ver com a conta.
//
// Nao pede senha, pela mesma razao que liberar conta nao pede: e' uma acao
// que DEVOLVE acesso. E o pior que tirar um bloqueio faz e' desfazer um
// atraso de cinco minutos que ia passar sozinho.
func (s *Servidor) adminLiberaIP(w http.ResponseWriter, r *http.Request) {
	admin, ok := s.exigeAdmin(w, r)
	if !ok {
		return
	}
	if !s.limiteAdmin.Permite("admin:" + strconv.FormatInt(admin.ID, 10)) {
		falha(w, http.StatusTooManyRequests, "muitas ações seguidas. Espere um pouco.")
		return
	}

	var p struct {
		Faixa  string `json:"faixa"`
		Motivo string `json:"motivo"`
	}
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}
	p.Faixa = strings.TrimSpace(p.Faixa)

	// A faixa vem da tela, mas e' conferida contra a LISTA ATIVA do banco
	// antes de virar DELETE. Sem isto o campo seria um apagador livre da
	// tabela: uma faixa inventada apagaria a linha que combinasse com ela.
	bans, err := s.banco.IPsBanidos()
	if err != nil {
		falha(w, http.StatusInternalServerError, "não consegui ler os bloqueios de IP")
		return
	}
	achou := false
	for _, v := range bans {
		if v.Faixa == p.Faixa {
			achou = true
			break
		}
	}
	if !achou {
		// Inclui o caso benigno e comum: o bloqueio venceu enquanto a tela
		// estava aberta. Dizer isso e' melhor que dizer "não encontrado".
		falha(w, http.StatusNotFound,
			"esse bloqueio não está mais ativo — pode ter vencido sozinho. Atualize a lista.")
		return
	}

	n, err := s.banco.LiberaIP(p.Faixa)
	if err != nil {
		falha(w, http.StatusInternalServerError, "não consegui tirar o bloqueio")
		return
	}
	s.registra(admin, nil, "liberar_ip",
		"faixa "+p.Faixa+" ("+strconv.FormatInt(n, 10)+" linha(s))", strings.TrimSpace(p.Motivo), r)

	devolve(w, http.StatusOK, resposta{
		"ok":       true,
		"mensagem": "Bloqueio de " + p.Faixa + " retirado. Quem estava nessa faixa já pode tentar entrar.",
	})
}

// adminHistorico devolve o registro de moderacao de uma conta. E' onde o
// motivo escrito no bloqueio volta a ser lido.
func (s *Servidor) adminHistorico(w http.ResponseWriter, r *http.Request) {
	if _, ok := s.exigeAdmin(w, r); !ok {
		return
	}
	conta, err := strconv.ParseInt(r.URL.Query().Get("conta"), 10, 64)
	if err != nil {
		falha(w, http.StatusBadRequest, "conta inválida")
		return
	}

	lista, err := s.banco.HistoricoDaConta(conta, 20)
	if err != nil {
		// A tabela pode nao existir ainda - nenhum dos dois deploys roda
		// SQL (LEIAME.md). Vazio e' melhor que erro na cara de quem so'
		// queria ver a ficha.
		logaFalta("guerra_site_admin_log", err)
		devolve(w, http.StatusOK, resposta{"historico": []resposta{}, "indisponivel": true})
		return
	}

	saida := make([]resposta, 0, len(lista))
	for _, m := range lista {
		saida = append(saida, resposta{
			"quando":  instante(m.Quando),
			"admin":   m.Admin,
			"acao":    m.Acao,
			"detalhe": m.Detalhe,
			"motivo":  m.Motivo,
		})
	}
	devolve(w, http.StatusOK, resposta{"historico": saida})
}

// registra grava no log de moderacao e NUNCA derruba a acao por causa
// disso - ver RegistraModeracao. O que aparece quando falta e' a linha de
// ATENCAO no journal do processo.
func (s *Servidor) registra(admin *Conta, alvo *ContaAdmin, acao, detalhe, motivo string, r *http.Request) {
	if err := s.banco.RegistraModeracao(admin, alvo, acao, detalhe, motivo, ipDe(r)); err != nil {
		alvoNome := "-"
		if alvo != nil {
			alvoNome = alvo.Usuario
		}
		logaAtencao("moderacao NAO registrada: %s fez '%s' em %s (%s): %v",
			admin.Usuario, acao, alvoNome, detalhe, err)
	}
}

// logaFalta anota que uma peca OPCIONAL nao respondeu, sem derrubar o
// pedido.
//
// Sao tres tabelas que podem legitimamente faltar: o `loginlog` e o
// `ipbanlist` sao do rAthena e o log_db pode apontar para outro banco; a
// `guerra_site_admin_log` e' nossa e nenhum dos dois deploys roda SQL
// (LEIAME.md), entao ela chega ao ar depois do binario que a usa. Em todos
// os casos, meio painel e' melhor que painel nenhum - e a linha de log e' o
// que impede o "meio" de passar despercebido para sempre.
func logaFalta(peca string, err error) {
	logaAtencao("painel de usuarios sem %s: %v", peca, err)
}

// logaAtencao poe a linha no journal com a marca que se procura com grep.
// Sem corpo de requisicao e sem senha - log e' o lugar classico onde
// segredo vaza (ver registra() em main.go).
func logaAtencao(formato string, args ...any) {
	log.Printf("ATENCAO: "+formato, args...)
}
