package main

import (
	"database/sql"
	"errors"
	"strconv"
	"strings"
	"time"
)

// As consultas do PAINEL DE USUARIOS. Ficam separadas de banco.go porque
// sao o unico lugar do site que le' a conta DE OUTRA PESSOA - e o unico que
// escreve na `login` de alguem que nao esta' do outro lado da requisicao.
//
// AS TRES TABELAS DO rAthena QUE ESTE ARQUIVO ENCOSTA, e nenhuma delas e'
// nossa:
//
//  1. `login`   - o estado da conta. Duas colunas mandam nele, e sao
//                 diferentes: `state` (0 = solta, 5 = bloqueada pela
//                 equipe) e `unban_time` (suspensao com prazo, em epoch).
//                 Os dois numeros sao os MESMOS que o @block e o @ban do
//                 jogo escrevem - char_mapif.cpp:798 poe state = 5, e o
//                 loginchrif.cpp:388 poe unban_time. Escolhidos de
//                 proposito: painel e comando de GM tem de contar a mesma
//                 historia, senao um desfaz o outro sem ninguem entender.
//
//  2. `ipbanlist` - o bloqueio que trava quem ERRA A SENHA, e que nao tem
//                 nada a ver com a conta. Ver o cabecalho de IPsBanidos.
//
//  3. `loginlog`  - o registro de cada tentativa de entrar, inclusive as
//                 que falharam. E' a unica fonte que sabe o IP de quem
//                 NUNCA conseguiu entrar - a `login.last_ip` so' e' escrita
//                 no login que deu certo, entao ela e' cega justamente no
//                 caso que interessa aqui.
//
// TUDO PELA CONEXAO latin1 (b.db), menos o registro de moderacao, que e'
// nosso e vai pela dbTexto (utf8mb4) porque tem motivo escrito a mao. E' a
// regra 3 do cabecalho de banco.go.

// grupoAdmin e' o group_id a partir do qual a conta manda no painel.
//
// 99 e' o grupo `Admin` do conf/groups.yml, o mesmo que da' o @ no jogo -
// e nao um numero novo. Um segundo conceito de "quem manda" divergiria do
// primeiro no dia em que alguem ganhasse ou perdesse um dos dois.
const grupoAdmin = 99

// Os dois valores de `login.state` que o painel escreve. O resto da escala
// existe (2 = expirada, 100 = apagada) e nao e' assunto daqui: sao estados
// que o proprio emulador produz.
const (
	estadoSolta     = 0 // entra normalmente
	estadoBloqueada = 5 // "You have been blocked by the GM Team" no cliente
)

// ContaAdmin e' a ficha de uma conta como o painel a mostra. Nada aqui e'
// escrito pelo site: sao todas colunas do rAthena, mais tres contagens.
type ContaAdmin struct {
	ID      int64
	Usuario string
	Email   string
	Sexo    string // M, F ou S - o 'S' e' conta de servidor, ver ContaDeServidor
	Grupo   int

	Estado   int   // login.state
	Suspensa int64 // login.unban_time, epoch; 0 = sem suspensao
	Expira   int64 // login.expiration_time, epoch; 0 = sem prazo

	Logins      int
	UltimoLogin sql.NullTime
	UltimoIP    string // login.last_ip: so' do ultimo login que DEU CERTO

	Personagens int
	Online      int

	// Preenchidos a partir do loginlog e do ipbanlist, e nao da `login`.
	// Ver CompletaComTentativas.
	Falhas       int
	UltimaTenta  sql.NullTime
	IPTentado    string // o IP da ultima tentativa, tenha ela dado certo ou nao
	FaixaBanida  string // a linha do ipbanlist que hoje barra esse IP, ou ""
	BarradoPorIP bool   // a ultima tentativa foi recusada pelo bloqueio de IP
}

// ContaDeServidor diz se a conta e' a que o char-server e o map-server usam
// para falar com o login-server (sexo 'S', account_id 1 no padrao do
// rAthena).
//
// ELA NAO PODE SER BLOQUEADA, e este e' o unico jeito de o painel derrubar
// o servidor inteiro com um clique: sem essa conta, char e map param de
// conectar no login e ninguem mais entra no jogo - inclusive quem ja'
// estava dentro, no proximo salto de mapa. A trava esta' em dois lugares de
// proposito (aqui, na leitura, e no WHERE de cada UPDATE), porque uma so'
// se esquece.
func (c *ContaAdmin) ContaDeServidor() bool { return c.Sexo == "S" }

// Contas devolve uma pagina da lista, opcionalmente filtrada.
//
// A busca aceita pedaco de nome, pedaco de e-mail ou o account_id inteiro.
// O numero e' testado a' parte e nao junto no mesmo OR: `account_id = ?`
// com uma string nao numerica faz o MySQL converter os dois lados para
// numero e casar com o account_id 0 - que nao existe, mas o dia em que
// existisse a busca por "abc" traria uma conta que ninguem pediu.
func (b *Banco) Contas(busca string, limite, salto int) ([]ContaAdmin, int, error) {
	var onde []string
	var args []any

	if busca = strings.TrimSpace(busca); busca != "" {
		curinga := "%" + escapaLike(busca) + "%"
		cond := []string{"userid LIKE ? ESCAPE '\\\\'", "email LIKE ? ESCAPE '\\\\'"}
		args = append(args, curinga, curinga)
		if n, err := paraInteiro(busca); err == nil {
			cond = append(cond, "account_id = ?")
			args = append(args, n)
		}
		onde = append(onde, "("+strings.Join(cond, " OR ")+")")
	}

	filtro := ""
	if len(onde) > 0 {
		filtro = " WHERE " + strings.Join(onde, " AND ")
	}

	var total int
	if err := b.db.QueryRow("SELECT COUNT(*) FROM login"+filtro, args...).Scan(&total); err != nil {
		return nil, 0, err
	}

	// As duas contagens de personagem sao subconsultas correlacionadas, e
	// nao um JOIN com GROUP BY: o JOIN obrigaria a agrupar por todas as
	// colunas da `login`, e o custo aqui esta' preso ao TAMANHO DA PAGINA
	// (50 contas), nao ao da tabela.
	//
	// `char` e' palavra reservada do MySQL - sem a crase a consulta nao
	// compila, e o erro aponta para o meio do SELECT.
	consulta := `
		SELECT account_id, userid, email, sex, group_id, state, unban_time,
		       expiration_time, logincount, lastlogin, last_ip,
		       (SELECT COUNT(*) FROM ` + "`char`" + ` c WHERE c.account_id = login.account_id),
		       (SELECT COUNT(*) FROM ` + "`char`" + ` c WHERE c.account_id = login.account_id AND c.online = 1)
		  FROM login` + filtro + `
		 ORDER BY account_id
		 LIMIT ? OFFSET ?`

	linhas, err := b.db.Query(consulta, append(args, limite, salto)...)
	if err != nil {
		return nil, 0, err
	}
	defer linhas.Close()

	lista := make([]ContaAdmin, 0, limite)
	for linhas.Next() {
		var c ContaAdmin
		if err := linhas.Scan(&c.ID, &c.Usuario, &c.Email, &c.Sexo, &c.Grupo,
			&c.Estado, &c.Suspensa, &c.Expira, &c.Logins, &c.UltimoLogin,
			&c.UltimoIP, &c.Personagens, &c.Online); err != nil {
			return nil, 0, err
		}
		// A conexao e' latin1 e estas duas colunas sao de texto. Nome e
		// e-mail nascem so' com ASCII pela validacao do cadastro, mas
		// conta feita pelo console do emulador nao passa por ela.
		c.Usuario = deLatin1(c.Usuario)
		c.Email = deLatin1(c.Email)
		lista = append(lista, c)
	}
	return lista, total, linhas.Err()
}

// escapaLike neutraliza os curingas do proprio LIKE dentro do que o
// administrador digitou. Sem isto, buscar por "%" lista a tabela inteira e
// buscar por "_" casa com qualquer letra - nao e' furo de seguranca (o
// valor continua indo por parametro), e' busca que mente.
func escapaLike(s string) string {
	r := strings.NewReplacer(`\`, `\\`, `%`, `\%`, `_`, `\_`)
	return r.Replace(s)
}

// paraInteiro e' ESTRITO: "2000abc" nao vale 2000. Um Sscanf("%d") pararia
// na primeira letra e devolveria o numero sem erro, o que faria a busca por
// um nome que comeca com digito trazer uma conta pelo id por acidente.
func paraInteiro(s string) (int64, error) {
	return strconv.ParseInt(strings.TrimSpace(s), 10, 64)
}

// ------------------------------------------------------------------
// O QUE TRAVA QUEM ERRA A SENHA - E QUE DESDE 2026-09-06 E' A CONTA
//
// Vale ler o CLAUDE.md secao 4.23 antes de mexer aqui.
//
// O rAthena bane o IP: sete erradas em cinco minutos punham na `ipbanlist` a
// faixa `x.y.z.*` - o /24 INTEIRO. Isso esta' DESLIGADO em
// conf/guerra/login_guerra.txt (`ipban_dynamic_pass_failure_ban: no`) desde
// 2026-09-06, depois de o caso aparecer em producao.
//
// O que trava hoje e' src/custom/trava_de_conta.hpp: sete erradas suspendem
// AQUELA CONTA por 15 minutos, gravadas no `unban_time` - o mesmo campo do
// @ban. Ou seja: o jogador que "travou a conta" travou mesmo, e a suspensao
// dele aparece na ficha como qualquer outra.
//
// PARA O PAINEL ISSO TEM DUAS CONSEQUENCIAS, e nenhuma e' obvia:
//
//   1. O `ipbanlist` continua existindo e continua barrando - o
//      `ipban_enable` segue ligado, porque e' ele que permite banir um IP a
//      mao. So' a parte AUTOMATICA saiu. A lista continua no painel por
//      isso, e nao mais como resposta a "errei a senha".
//   2. Uma conta suspensa agora pode ser duas coisas MUITO diferentes: um
//      castigo que alguem decidiu, ou quinze minutos que a propria trava
//      pos e que passam sozinhos. Sao a mesma coluna, e confundi-las faz o
//      operador punir de novo quem so' esqueceu a senha - ver travaAutomatica.

// Espelham os #define de src/custom/trava_de_conta.hpp. Existem SO' PARA
// ROTULAR o que a ficha mostra - nada aqui decide quem entra no jogo, entao
// se um dia divergirem do C++ o estrago e' um rotulo errado, e nao um
// jogador solto ou preso por engano.
const (
	travaLimiteErros = 7
	travaSuspensao   = 15 * time.Minute
)

// travaAutomatica diz se a suspensao desta conta tem cara de ter sido posta
// pela trava de senha errada, e nao por gente.
//
// E' PALPITE FUNDAMENTADO, e nao certeza: a trava nao deixa marca nenhuma no
// banco - ela escreve no mesmo `unban_time` do @ban, de proposito (era o que
// dispensava tabela e migracao). O que sobra sao dois sinais que so'
// coincidem nela: um prazo CURTO (a trava escreve exatamente 15 minutos) e
// erros de senha recentes o bastante para terem chegado ao limite.
//
// Errar para o lado seguro: um administrador que suspenda alguem por 15
// minutos vai ver o rotulo de trava automatica, e ele sabe o que fez. O
// contrario - trava automatica passando por castigo - e' que faria o
// operador punir de novo quem so' esqueceu a senha.
func travaAutomatica(c *ContaAdmin, agora time.Time) bool {
	if c.Suspensa <= agora.Unix() || c.Falhas < travaLimiteErros {
		return false
	}
	// A folga cobre o tempo entre o login-server gravar e esta consulta ler.
	return time.Unix(c.Suspensa, 0).Sub(agora) <= travaSuspensao+time.Minute
}

// IPBan e' uma linha ativa do ipbanlist.
type IPBan struct {
	Faixa  string // "187.12.3.*" ou um endereco inteiro
	Desde  time.Time
	Ate    time.Time
	Motivo string
}

// IPsBanidos devolve so' os bloqueios que ainda valem.
//
// O `rtime > NOW()` e' a mesma condicao que o ipban_check usa
// (ipban.cpp:49): linha vencida continua na tabela ate' a faxina de cada
// minuto passar, e mostra-la no painel faria o administrador liberar um
// bloqueio que ja' nao bloqueia nada.
func (b *Banco) IPsBanidos() ([]IPBan, error) {
	linhas, err := b.db.Query(
		"SELECT list, btime, rtime, reason FROM ipbanlist WHERE rtime > NOW() ORDER BY rtime DESC")
	if err != nil {
		return nil, err
	}
	defer linhas.Close()

	var lista []IPBan
	for linhas.Next() {
		var v IPBan
		if err := linhas.Scan(&v.Faixa, &v.Desde, &v.Ate, &v.Motivo); err != nil {
			return nil, err
		}
		v.Motivo = deLatin1(v.Motivo)
		lista = append(lista, v)
	}
	return lista, linhas.Err()
}

// LiberaIP apaga as linhas de uma faixa. Apaga TODAS as linhas daquela
// faixa e nao so' a mais recente: a chave primaria e' (list, btime), entao
// um jogador que insistiu deixou varias linhas ali, e sobrar uma so' deixa
// o bloqueio de pe' - com o painel dizendo que ele foi tirado.
func (b *Banco) LiberaIP(faixa string) (int64, error) {
	res, err := b.db.Exec("DELETE FROM ipbanlist WHERE list = ?", faixa)
	if err != nil {
		return 0, err
	}
	return res.RowsAffected()
}

// faixasQueBarram devolve as quatro formas de lista que barrariam este IP,
// na mesma ordem em que o ipban_check as testa (ipban.cpp:49): o /8, o /16,
// o /24 e o endereco exato. Replicado aqui, e nao consultado no banco, para
// o painel poder dizer QUAL linha barra QUAL conta sem uma consulta por
// conta.
//
// Devolve nada para o que nao for IPv4 em quatro partes decimais - o
// ipbanlist do rAthena guarda o endereco desmontado de um uint32, e IPv6
// simplesmente nao passa por ali.
func faixasQueBarram(ip string) []string {
	p := strings.Split(strings.TrimSpace(ip), ".")
	if len(p) != 4 {
		return nil
	}
	for _, parte := range p {
		if parte == "" || len(parte) > 3 {
			return nil
		}
		for _, d := range parte {
			if d < '0' || d > '9' {
				return nil
			}
		}
	}
	return []string{
		p[0] + ".*.*.*",
		p[0] + "." + p[1] + ".*.*",
		p[0] + "." + p[1] + "." + p[2] + ".*",
		strings.Join(p, "."),
	}
}

// ------------------------------------------------------------------
// AS TENTATIVAS DE ENTRAR
//
// O `loginlog` guarda uma linha por tentativa, com o `rcode` que o
// login-server devolveu ao cliente. Os que interessam ao painel:
//
//	 0  usuario inexistente        conta como falha de senha (ipban.cpp)
//	 1  senha errada               conta como falha de senha
//	-3  recusado por bloqueio de IP   NAO conta: quem esta' barrado nem
//	                                  chega a digitar, e e' por isso que o
//	                                  bloqueio nao se renova sozinho
const (
	rcodeUsuarioInexistente = 0
	rcodeSenhaErrada        = 1
	rcodeIPBanido           = -3
)

// janelaTentativas e' o quanto para tras o painel olha. Vinte e quatro
// horas, e nao os cinco minutos da regra do emulador: o administrador abre
// o painel horas depois do problema, e a pergunta dele nao e' "esta'
// bloqueado agora?" e sim "o que aconteceu com essa conta?".
const janelaTentativas = 24 * time.Hour

// tetoTentativas limita o que sai do banco numa leitura so'. O `loginlog` e'
// MyISAM e tem indice so' em `ip`: filtrar por `time` varre a tabela. Ele e'
// pequeno hoje; o teto e' o que garante que continue barato quando nao for.
const tetoTentativas = 3000

type tentativas struct {
	falhas     int
	ultima     time.Time
	ultimoIP   string
	ultimoCode int
}

// CompletaComTentativas preenche as colunas que vem do loginlog nas contas
// da pagina.
//
// UMA consulta para a pagina inteira, e nao uma por conta: sao 50 fichas na
// tela e a alternativa seriam 50 varreduras da mesma tabela sem indice.
//
// FALHA MACIA DE PROPOSITO: se o `loginlog` nao existir neste banco (ele e'
// opcional no rAthena, e o log_db pode apontar para outro lugar), o painel
// segue sem os numeros de tentativa em vez de nao abrir. O que ele mostra
// da' `login` continua inteiro.
func (b *Banco) CompletaComTentativas(contas []ContaAdmin) error {
	if len(contas) == 0 {
		return nil
	}

	linhas, err := b.db.Query(
		`SELECT user, ip, rcode, time FROM loginlog
		  WHERE time > NOW() - INTERVAL ? SECOND
		  ORDER BY time DESC
		  LIMIT ?`, int(janelaTentativas.Seconds()), tetoTentativas)
	if err != nil {
		return err
	}
	defer linhas.Close()

	// Chave em minusculas: a coluna e' latin1_swedish_ci, entao o MySQL
	// considera "Fulano" e "fulano" o mesmo usuario, e um mapa de Go nao.
	por := map[string]*tentativas{}
	for linhas.Next() {
		var usuario, ip string
		var rcode int
		var quando time.Time
		if err := linhas.Scan(&usuario, &ip, &rcode, &quando); err != nil {
			return err
		}
		chave := strings.ToLower(deLatin1(usuario))
		t := por[chave]
		if t == nil {
			// A consulta vem em ordem decrescente, entao a PRIMEIRA linha
			// de cada usuario e' a tentativa mais recente dele.
			t = &tentativas{ultima: quando, ultimoIP: ip, ultimoCode: rcode}
			por[chave] = t
		}
		if rcode == rcodeSenhaErrada || rcode == rcodeUsuarioInexistente {
			t.falhas++
		}
	}
	if err := linhas.Err(); err != nil {
		return err
	}

	banidos, err := b.IPsBanidos()
	if err != nil {
		return err
	}
	ativa := map[string]bool{}
	for _, v := range banidos {
		ativa[v.Faixa] = true
	}

	for i := range contas {
		c := &contas[i]
		if t := por[strings.ToLower(c.Usuario)]; t != nil {
			c.Falhas = t.falhas
			c.UltimaTenta = sql.NullTime{Time: t.ultima, Valid: true}
			c.IPTentado = t.ultimoIP
			c.BarradoPorIP = t.ultimoCode == rcodeIPBanido
		}
		// A ultima tentativa e' a melhor pista, mas ela pode estar fora da
		// janela; ai' vale o IP do ultimo login que deu certo.
		ip := c.IPTentado
		if ip == "" {
			ip = c.UltimoIP
		}
		for _, faixa := range faixasQueBarram(ip) {
			if ativa[faixa] {
				c.FaixaBanida = faixa
				break
			}
		}
	}
	return nil
}

// ------------------------------------------------------------------
// AS ESCRITAS
//
// Todas passam pelo mesmo WHERE de seguranca. Ver ContaDeServidor: a conta
// de sexo 'S' e' a que segura o servidor de pe', e bloquea-la derruba o
// jogo inteiro. A guarda esta' no proprio UPDATE e nao so' na leitura de
// antes porque entre uma coisa e outra a linha pode ter mudado - e' a mesma
// razao do `online = 0` do MoveParaProntera.

var ErrContaDeServidor = errors.New("essa conta e do servidor")

// PorIDAdmin le' a ficha de uma conta so'. Usada antes de cada escrita,
// para o registro de moderacao poder dizer de que estado se saiu.
//
// A CONTAGEM DE PERSONAGEM CONECTADO VEM JUNTO, e nao e' enfeite: e' o que
// decide se a resposta do bloqueio avisa para dar @kick no jogo (ver
// avisoDeSessaoAberta em admin.go). Sem ela o campo vinha zero, o aviso
// nunca saia, e o administrador ficava achando que o jogador tinha sido
// tirado do ar quando ele continuava jogando. Achado em 2026-09-10, num
// banco de teste com um personagem online.
func (b *Banco) PorIDAdmin(id int64) (*ContaAdmin, error) {
	c := &ContaAdmin{}
	err := b.db.QueryRow(
		`SELECT account_id, userid, email, sex, group_id, state, unban_time,
		        expiration_time, logincount, lastlogin, last_ip,
		        (SELECT COUNT(*) FROM `+"`char`"+` c WHERE c.account_id = login.account_id),
		        (SELECT COUNT(*) FROM `+"`char`"+` c WHERE c.account_id = login.account_id AND c.online = 1)
		   FROM login WHERE account_id = ?`, id).
		Scan(&c.ID, &c.Usuario, &c.Email, &c.Sexo, &c.Grupo, &c.Estado,
			&c.Suspensa, &c.Expira, &c.Logins, &c.UltimoLogin, &c.UltimoIP,
			&c.Personagens, &c.Online)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, ErrNaoAchou
	}
	if err != nil {
		return nil, err
	}
	c.Usuario = deLatin1(c.Usuario)
	c.Email = deLatin1(c.Email)
	return c, nil
}

// AS TRES ESCREVEM AS DUAS COLUNAS, SEMPRE. Nenhuma mexe so' na sua.
//
// `state` e `unban_time` sao INDEPENDENTES no rAthena, e uma conta pode ter
// as duas ao mesmo tempo. Quem barra primeiro e' o prazo (login.cpp:365,
// antes do teste de state), e disso saem duas confusoes de tamanhos
// diferentes:
//
//   - a pequena: bloquear uma conta ja' suspensa responde "conta
//     bloqueada" e a ficha continua marcada SUSPENSA, porque e' a
//     suspensao que ainda barra. Parece que o botao nao funcionou. Visto
//     na tela em 2026-09-10, e foi o que trouxe esta regra;
//   - a grande: suspender por um dia quem estava BLOQUEADO nao solta
//     ninguem no dia seguinte. O prazo vence, o state 5 continua la', e o
//     jogador segue de fora - com o painel dizendo que a punicao dele
//     acabou.
//
// Entao os tres botoes da tela sao mutuamente exclusivos, e cada um deixa a
// conta num estado so'. O preco e' que suspender ou liberar zera um `state`
// que o emulador tenha posto ali por outro motivo; e' aceito de proposito,
// porque quem clicou estava olhando a ficha e escolhendo o que a conta
// passa a ser.

// Bloqueia e' o @block do jogo, pelo mesmo numero (char_mapif.cpp:798).
// Sem prazo: vale ate' alguem liberar.
func (b *Banco) Bloqueia(conta int64) error {
	res, err := b.db.Exec(
		"UPDATE login SET state = ?, unban_time = 0 WHERE account_id = ? AND sex <> 'S' LIMIT 1",
		estadoBloqueada, conta)
	return conferiuUmaLinha(res, err)
}

// Suspende poe prazo em vez de bloqueio permanente. O valor e' epoch, igual
// ao que o @ban grava (loginchrif.cpp:388), e o cliente mostra a data.
//
// SEM SOMAR AO PRAZO QUE JA' EXISTE, ao contrario do @ban do jogo: ali o
// comando recebe um intervalo e empilha ("mais tres dias"); aqui o
// administrador esta' vendo a ficha e escolhendo ate' quando, e empilhar
// calado sobre uma suspensao antiga daria uma data que ninguem pediu.
func (b *Banco) Suspende(conta int64, ate time.Time) error {
	res, err := b.db.Exec(
		"UPDATE login SET state = 0, unban_time = ? WHERE account_id = ? AND sex <> 'S' LIMIT 1",
		ate.Unix(), conta)
	return conferiuUmaLinha(res, err)
}

// Libera devolve a conta ao estado de quem entra normalmente.
func (b *Banco) Libera(conta int64) error {
	res, err := b.db.Exec(
		"UPDATE login SET state = 0, unban_time = 0 WHERE account_id = ? AND sex <> 'S' LIMIT 1",
		conta)
	return conferiuUmaLinha(res, err)
}

// conferiuUmaLinha transforma "nenhuma linha tocada" em erro.
//
// Sem isto, tentar bloquear a conta de servidor - a unica que o WHERE
// recusa - responderia OK e nao teria feito nada, que e' a pior das duas
// falhas possiveis aqui.
func conferiuUmaLinha(res sql.Result, err error) error {
	if err != nil {
		return err
	}
	n, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if n == 0 {
		return ErrContaDeServidor
	}
	return nil
}

// ------------------------------------------------------------------
// O REGISTRO DE MODERACAO
//
// Pela dbTexto (utf8mb4): o `motivo` e' escrito a mao, com acento. Ver o
// cabecalho da tabela em sql/site.sql.

// Moderacao e' uma linha do registro, como o painel a mostra de volta.
type Moderacao struct {
	Quando  time.Time
	Admin   string
	Acao    string
	Detalhe string
	Motivo  string
}

// RegistraModeracao grava o que foi feito.
//
// NAO DEVOLVE ERRO AO CHAMADOR de proposito - ele so' loga. A alternativa
// seria desfazer o bloqueio porque o registro falhou, e ai' a tabela de
// auditoria passaria a poder derrubar a moderacao. Quem descobre que ela
// falta e' o log do processo, com ATENCAO na frente; e o site sobe sem a
// tabela sem reclamar, que e' a regra deste projeto (LEIAME.md).
func (b *Banco) RegistraModeracao(admin *Conta, alvo *ContaAdmin, acao, detalhe, motivo, ip string) error {
	var alvoID any
	alvoNome := ""
	if alvo != nil {
		alvoID = alvo.ID
		alvoNome = alvo.Usuario
	}
	_, err := b.dbTexto.Exec(
		`INSERT INTO guerra_site_admin_log
		   (admin_id, admin_usuario, alvo_id, alvo_usuario, acao, detalhe, motivo, ip, criado_em)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())`,
		admin.ID, admin.Usuario, alvoID, alvoNome, acao, detalhe, motivo, ip)
	return err
}

// HistoricoDaConta devolve as ultimas acoes de moderacao sobre uma conta.
// E' onde o `motivo` volta a ser lido - sem esta consulta ele seria um
// campo que so' se escreve.
func (b *Banco) HistoricoDaConta(conta int64, limite int) ([]Moderacao, error) {
	linhas, err := b.dbTexto.Query(
		`SELECT criado_em, admin_usuario, acao, detalhe, motivo
		   FROM guerra_site_admin_log
		  WHERE alvo_id = ?
		  ORDER BY criado_em DESC, id DESC
		  LIMIT ?`, conta, limite)
	if err != nil {
		return nil, err
	}
	defer linhas.Close()

	var lista []Moderacao
	for linhas.Next() {
		var m Moderacao
		if err := linhas.Scan(&m.Quando, &m.Admin, &m.Acao, &m.Detalhe, &m.Motivo); err != nil {
			return nil, err
		}
		lista = append(lista, m)
	}
	return lista, linhas.Err()
}
