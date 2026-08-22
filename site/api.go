package main

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"errors"
	"net/http"
	"net/mail"
	"strconv"
	"strings"
)

// Os limites vem da tabela login do rAthena, e nao de gosto nosso. Passar
// deles nao da' erro no MySQL: ele TRUNCA - e a conta nasce com um nome
// cortado que o jogador nunca consegue digitar de novo.
const (
	maxUsuario = 23 // login.userid varchar(23)
	maxEmail   = 39 // login.email varchar(39)
	minSenha   = 6
	maxSenha   = 32
)

type resposta map[string]any

func devolve(w http.ResponseWriter, codigo int, corpo resposta) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(codigo)
	_ = json.NewEncoder(w).Encode(corpo)
}

func falha(w http.ResponseWriter, codigo int, msg string) {
	devolve(w, codigo, resposta{"erro": msg})
}

func leCorpo(r *http.Request, destino any) error {
	// Teto no corpo: sem ele, um POST de 2 GB derruba um processo que so'
	// tem 961 MB de maquina embaixo.
	return leCorpoAte(r, destino, 16*1024)
}

// leCorpoAte e' o mesmo com o teto escolhido. So' o chamado precisa de mais
// que os 16 KB: quatro mil caracteres de texto livre com acento passam de
// 8 KB so' de corpo, e um teto apertado devolveria "pedido malformado" para
// quem escreveu um relato longo - a mensagem menos util possivel.
func leCorpoAte(r *http.Request, destino any, teto int64) error {
	r.Body = http.MaxBytesReader(nil, r.Body, teto)
	return json.NewDecoder(r.Body).Decode(destino)
}

func md5hex(s string) string {
	soma := md5.Sum([]byte(s))
	return hex.EncodeToString(soma[:])
}

// validaCadastro reune as regras do formulario num lugar so'.
func validaCadastro(usuario, senha, email string) error {
	usuario = strings.TrimSpace(usuario)
	if len(usuario) < 4 || len(usuario) > maxUsuario {
		return errors.New("o nome de usuario precisa ter de 4 a 23 letras")
	}
	// So' ASCII: o cliente de RO manda o usuario num campo de bytes, e
	// acento aqui vira problema de codificacao no login, longe daqui.
	for _, r := range usuario {
		ok := (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') ||
			(r >= '0' && r <= '9') || r == '_'
		if !ok {
			return errors.New("o nome de usuario aceita apenas letras, numeros e _")
		}
	}
	if len(senha) < minSenha || len(senha) > maxSenha {
		return errors.New("a senha precisa ter de 6 a 32 caracteres")
	}
	if len(email) > maxEmail {
		// Limite do rAthena, nao nosso - ver a constante.
		return errors.New("o e-mail precisa ter no maximo 39 caracteres")
	}
	if _, err := mail.ParseAddress(email); err != nil {
		return errors.New("e-mail invalido")
	}
	return nil
}

type pedidoConta struct {
	Usuario   string `json:"usuario"`
	Senha     string `json:"senha"`
	Email     string `json:"email"`
	Sexo      string `json:"sexo"`
	Tipo      string `json:"tipo"` // "cpf" ou "celular"
	Documento string `json:"documento"`
	Pedido    string `json:"pedido"` // so' na confirmacao
	Codigo    string `json:"codigo"` // so' na confirmacao
}

// normaliza valida o documento e devolve (tipo, numero normalizado).
func normalizaDocumento(tipo, valor string) (string, string, error) {
	switch tipo {
	case "cpf":
		n, err := ValidaCPF(valor)
		return "cpf", n, err
	case "celular":
		n, err := ValidaCelular(valor)
		return "celular", n, err
	default:
		return "", "", errors.New("escolha CPF ou celular")
	}
}

// contaInicia e' o primeiro passo. Em modo beta (SITE_VERIFICACAO=nenhuma)
// ele ja' cria a conta e devolve pronto; com Penelope, manda o codigo e
// devolve o identificador do pedido para o passo seguinte.
func (s *Servidor) contaInicia(w http.ResponseWriter, r *http.Request) {
	ip := ipDe(r)
	if !s.limite.Permite(ip) {
		falha(w, http.StatusTooManyRequests,
			"tentativas demais deste endereco. Tente de novo daqui a pouco.")
		return
	}

	var p pedidoConta
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}
	p.Usuario = strings.TrimSpace(p.Usuario)
	p.Email = strings.TrimSpace(p.Email)

	if err := validaCadastro(p.Usuario, p.Senha, p.Email); err != nil {
		falha(w, http.StatusBadRequest, err.Error())
		return
	}
	if p.Sexo != "M" && p.Sexo != "F" {
		falha(w, http.StatusBadRequest, "escolha o sexo do personagem")
		return
	}

	tipo, numero, err := normalizaDocumento(p.Tipo, p.Documento)
	if err != nil {
		falha(w, http.StatusBadRequest, err.Error())
		return
	}

	// Barato antes de caro: conferir o nome e o documento ANTES de mandar
	// mensagem. Sem isto, o jogador recebe o codigo no WhatsApp e so'
	// depois descobre que o nome esta' tomado.
	if livre, err := s.banco.UsuarioLivre(p.Usuario); err != nil {
		falha(w, http.StatusInternalServerError, "erro ao consultar o banco")
		return
	} else if !livre {
		falha(w, http.StatusConflict, "ja existe uma conta com esse nome")
		return
	}

	hash := HashDocumento(s.cfg.Segredo, tipo, numero)
	n, err := s.banco.ContasPorDocumento(hash)
	if err != nil {
		falha(w, http.StatusInternalServerError, "erro ao consultar o banco")
		return
	}
	if n >= s.cfg.MaxContas {
		// Curto de proposito: dizer POR QUE o limite existe entrega o
		// roteiro a quem ainda nao tinha pensado em burla-lo. Mesma razao
		// do texto do formulario (web/index.html).
		falha(w, http.StatusConflict, "esse documento ja tem uma conta")
		return
	}

	// Sem verificacao (beta): cria agora.
	if !s.verifica.Exige(tipo) {
		s.criaEResponde(w, r, p, tipo, hash, ip)
		return
	}

	pedido, err := s.verifica.Envia(tipo, numero)
	if err != nil {
		falha(w, http.StatusBadGateway, "nao consegui enviar o codigo: "+err.Error())
		return
	}
	devolve(w, http.StatusOK, resposta{
		"precisa_codigo": true,
		"pedido":         pedido,
		"mensagem":       "Mandamos um codigo para o seu WhatsApp.",
	})
}

// contaConfirma fecha o cadastro que esperava codigo.
func (s *Servidor) contaConfirma(w http.ResponseWriter, r *http.Request) {
	var p pedidoConta
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}
	if err := validaCadastro(strings.TrimSpace(p.Usuario), p.Senha, strings.TrimSpace(p.Email)); err != nil {
		falha(w, http.StatusBadRequest, err.Error())
		return
	}

	numero, err := s.verifica.Confere(p.Pedido, strings.TrimSpace(p.Codigo))
	if err != nil {
		falha(w, http.StatusBadRequest, err.Error())
		return
	}

	tipo := p.Tipo
	if tipo == "" {
		tipo = "celular"
	}
	hash := HashDocumento(s.cfg.Segredo, tipo, numero)
	s.criaEResponde(w, r, p, tipo, hash, ipDe(r))
}

func (s *Servidor) criaEResponde(w http.ResponseWriter, r *http.Request,
	p pedidoConta, tipo, hash, ip string) {

	id, err := s.banco.CriaConta(p.Usuario, md5hex(p.Senha), p.Email, p.Sexo, hash, tipo, ip)
	switch {
	case errors.Is(err, ErrUsuarioExiste):
		falha(w, http.StatusConflict, "ja existe uma conta com esse nome")
		return
	case errors.Is(err, ErrDocumentoUsado):
		falha(w, http.StatusConflict, "esse documento ja tem conta")
		return
	case err != nil:
		falha(w, http.StatusInternalServerError, "nao consegui criar a conta")
		return
	}

	s.poeCookie(w, r, id)
	devolve(w, http.StatusCreated, resposta{
		"ok":      true,
		"usuario": p.Usuario,
	})
}

func (s *Servidor) sessaoAbre(w http.ResponseWriter, r *http.Request) {
	if !s.limite.Permite("login:" + ipDe(r)) {
		falha(w, http.StatusTooManyRequests, "tentativas demais. Espere um pouco.")
		return
	}
	var p struct {
		Usuario string `json:"usuario"`
		Senha   string `json:"senha"`
	}
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}

	c, err := s.banco.PorUsuarioESenha(strings.TrimSpace(p.Usuario), md5hex(p.Senha))
	if err != nil {
		// Mensagem unica de proposito: dizer "usuario nao existe" entrega
		// a quem esta' testando quais nomes existem.
		falha(w, http.StatusUnauthorized, "usuario ou senha invalidos")
		return
	}
	s.poeCookie(w, r, c.ID)
	devolve(w, http.StatusOK, resposta{"ok": true, "usuario": c.Usuario})
}

func (s *Servidor) sessaoFecha(w http.ResponseWriter, r *http.Request) {
	s.tiraCookie(w)
	devolve(w, http.StatusOK, resposta{"ok": true})
}

// exigeSessao e' a guarda dos tres botoes do painel.
func (s *Servidor) exigeSessao(w http.ResponseWriter, r *http.Request) (*Conta, bool) {
	id, err := s.quemE(r)
	if err != nil {
		falha(w, http.StatusUnauthorized, "entre na sua conta")
		return nil, false
	}
	c, err := s.banco.PorID(id)
	if err != nil {
		s.tiraCookie(w)
		falha(w, http.StatusUnauthorized, "entre na sua conta")
		return nil, false
	}
	return c, true
}

// config e' o que o front precisa saber antes de desenhar. Publico de
// proposito - nao ha' segredo aqui, e uma chamada a menos no caminho de
// quem so' quer baixar o jogo.
func (s *Servidor) config(w http.ResponseWriter, r *http.Request) {
	devolve(w, http.StatusOK, resposta{"download": s.cfg.DownloadURL})
}

func (s *Servidor) painel(w http.ResponseWriter, r *http.Request) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return
	}
	devolve(w, http.StatusOK, resposta{
		"usuario": c.Usuario,
		"email":   c.Email,
		"tem_pin": c.Pin != "",
	})
}

func (s *Servidor) trocaSenha(w http.ResponseWriter, r *http.Request) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return
	}
	var p struct {
		Atual string `json:"atual"`
		Nova  string `json:"nova"`
	}
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}
	// Pede a senha atual mesmo com sessao valida: sem isso, um cookie
	// roubado troca a senha e toma a conta de vez.
	if _, err := s.banco.PorUsuarioESenha(c.Usuario, md5hex(p.Atual)); err != nil {
		falha(w, http.StatusUnauthorized, "a senha atual nao confere")
		return
	}
	if len(p.Nova) < minSenha || len(p.Nova) > maxSenha {
		falha(w, http.StatusBadRequest, "a senha nova precisa ter de 6 a 32 caracteres")
		return
	}
	if err := s.banco.TrocaSenha(c.ID, md5hex(p.Nova)); err != nil {
		falha(w, http.StatusInternalServerError, "nao consegui trocar a senha")
		return
	}
	devolve(w, http.StatusOK, resposta{"ok": true})
}

// recuperaPin ESVAZIA o PIN em vez de mostrar o guardado.
//
// O pincode do rAthena e' varchar(4) em TEXTO PURO - da' para simplesmente
// ler e devolver. Nao devolvemos: mostrar na tela poe o PIN no histórico do
// navegador e em qualquer print. Com o campo vazio o cliente pede um PIN
// novo no proximo login, que resolve o "esqueci" de forma melhor.
func (s *Servidor) recuperaPin(w http.ResponseWriter, r *http.Request) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return
	}
	var p struct {
		Senha string `json:"senha"`
	}
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}
	if _, err := s.banco.PorUsuarioESenha(c.Usuario, md5hex(p.Senha)); err != nil {
		falha(w, http.StatusUnauthorized, "a senha nao confere")
		return
	}
	if err := s.banco.LimpaPin(c.ID); err != nil {
		falha(w, http.StatusInternalServerError, "nao consegui apagar o PIN")
		return
	}
	devolve(w, http.StatusOK, resposta{
		"ok": true,
		"mensagem": "PIN apagado. No proximo login o jogo vai pedir que voce " +
			"escolha um novo.",
	})
}

// ------------------------------------------------------------------
// PERSONAGENS: listar e destravar
//
// Por que isto existe: ha' mapas que o rAthena conhece e o nosso cliente
// de 2021 ainda nao tem, e o jogador consegue chegar neles. Quando isso
// acontece ele nao "morre" - ele fica PRESO, porque toda entrada seguinte
// no jogo o poe de volta no mesmo lugar. Sem este botao, so' um GM
// resolve, um a um.

func (s *Servidor) personagens(w http.ResponseWriter, r *http.Request) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return
	}
	lista, err := s.banco.Personagens(c.ID)
	if err != nil {
		falha(w, http.StatusInternalServerError, "nao consegui ler seus personagens")
		return
	}

	saida := make([]resposta, 0, len(lista))
	for _, p := range lista {
		saida = append(saida, resposta{
			"id":      p.ID,
			"nome":    p.Nome,
			"nivel":   p.Nivel,
			"mapa":    p.Mapa,
			"online":  p.Online,
			"em_casa": p.Mapa == mapaSeguro,
		})
	}
	devolve(w, http.StatusOK, resposta{"personagens": saida, "destino": mapaSeguro})
}

// destrava move um personagem para Prontera.
//
// NAO PEDE A SENHA, e as outras duas acoes do painel pedem. A diferenca e'
// o que esta' em jogo: trocar senha e apagar PIN mexem no acesso a' conta,
// entao um cookie roubado nao pode bastar. Mover personagem parado para a
// praca de Prontera nao tira nada de ninguem - e' reversivel andando, e so'
// funciona com o personagem DESCONECTADO, o que ja' impede o unico abuso
// imaginavel (arrancar alguem de uma guerra). Pedir senha aqui seria
// atrito na tela de quem ja' esta' travado e irritado.
func (s *Servidor) destrava(w http.ResponseWriter, r *http.Request) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return
	}
	// Teto por conta: o botao mexe na `char`, e um laco de requisicao nao
	// deve poder martelar a tabela que o char-server usa.
	if !s.limite.Permite("destrava:" + strconv.FormatInt(c.ID, 10)) {
		falha(w, http.StatusTooManyRequests, "muitos pedidos seguidos. Espere um pouco.")
		return
	}

	var p struct {
		Personagem int64 `json:"personagem"`
	}
	if err := leCorpo(r, &p); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}

	err := s.banco.MoveParaProntera(c.ID, p.Personagem)
	switch {
	case errors.Is(err, ErrNaoAchou):
		// O personagem nao e' dele, ou nao existe. As duas dao a mesma
		// resposta: dizer qual seria contar quem tem qual char_id.
		falha(w, http.StatusNotFound, "personagem nao encontrado nesta conta")
		return
	case errors.Is(err, ErrJaEmProntera):
		falha(w, http.StatusConflict, "esse personagem ja esta em Prontera")
		return
	case errors.Is(err, ErrPersonagemOnline):
		falha(w, http.StatusConflict,
			"esse personagem esta conectado. Saia do jogo por completo (fechar "+
				"a janela nao basta: espere alguns segundos) e tente de novo.")
		return
	case err != nil:
		falha(w, http.StatusInternalServerError, "nao consegui mover o personagem")
		return
	}

	devolve(w, http.StatusOK, resposta{
		"ok": true,
		"mensagem": "Pronto. Ao entrar no jogo, esse personagem vai aparecer na " +
			"praca de Prontera.",
	})
}

// ------------------------------------------------------------------
// CHAMADOS
//
// So' GRAVA. O painel de leitura vem depois (PENDENCIAS.md), e a tabela ja'
// nasce com o campo de estado para nao precisar de ALTER TABLE quando ele
// chegar.

const (
	maxAssunto      = 120  // guerra_site_chamado.assunto varchar(120)
	minMensagem     = 15   // menos que isso nao descreve nada
	maxMensagem     = 4000 // em RUNAS, nao em bytes - ver o comentario abaixo
	chamadosPorHora = 5
)

// Os tipos aceitos. A lista e' fechada aqui e no ENUM da tabela; um valor
// fora dela viraria string vazia no MySQL, calado.
var tiposDeChamado = map[string]bool{
	"item": true, "traducao": true, "missao": true,
	"mapa": true, "conta": true, "outro": true,
}

func (s *Servidor) abreChamado(w http.ResponseWriter, r *http.Request) {
	c, ok := s.exigeSessao(w, r)
	if !ok {
		return
	}

	var p struct {
		Tipo       string `json:"tipo"`
		Personagem string `json:"personagem"`
		Assunto    string `json:"assunto"`
		Mensagem   string `json:"mensagem"`
	}
	if err := leCorpoAte(r, &p, 64*1024); err != nil {
		falha(w, http.StatusBadRequest, "pedido malformado")
		return
	}

	p.Tipo = strings.TrimSpace(p.Tipo)
	p.Personagem = strings.TrimSpace(p.Personagem)
	p.Assunto = strings.TrimSpace(p.Assunto)
	p.Mensagem = strings.TrimSpace(p.Mensagem)

	if !tiposDeChamado[p.Tipo] {
		p.Tipo = "outro"
	}

	// CONTAGEM EM RUNAS, e nao em bytes: "correção" tem 9 letras e 11
	// bytes. Medir em len() faria o limite apertar sozinho para quem
	// escreve em portugues de verdade - e o campo do formulario, que conta
	// caracteres, discordaria do servidor sem ninguem entender por que.
	if n := len([]rune(p.Assunto)); n < 5 || n > maxAssunto {
		falha(w, http.StatusBadRequest,
			"o assunto precisa ter de 5 a 120 caracteres")
		return
	}
	if n := len([]rune(p.Mensagem)); n < minMensagem || n > maxMensagem {
		falha(w, http.StatusBadRequest,
			"conte o que aconteceu em pelo menos 15 e no maximo 4000 caracteres")
		return
	}
	if len([]rune(p.Personagem)) > 30 { // char.name varchar(30)
		falha(w, http.StatusBadRequest, "nome de personagem longo demais")
		return
	}

	n, err := s.banco.ChamadosNaHora(c.ID)
	if err != nil {
		falha(w, http.StatusInternalServerError, "erro ao consultar o banco")
		return
	}
	if n >= chamadosPorHora {
		falha(w, http.StatusTooManyRequests,
			"voce ja abriu cinco chamados nesta hora. Espere um pouco - "+
				"eles nao se perdem.")
		return
	}

	id, err := s.banco.CriaChamado(c.ID, c.Usuario, p.Personagem, p.Tipo,
		p.Assunto, p.Mensagem, ipDe(r))
	if err != nil {
		falha(w, http.StatusInternalServerError, "nao consegui registrar o chamado")
		return
	}

	// O numero vai para a tela: sem ele o jogador nao tem como cobrar
	// depois, e o painel de leitura vai indexar por ele.
	devolve(w, http.StatusCreated, resposta{
		"ok":     true,
		"numero": id,
		"mensagem": "Chamado registrado. Guarde o numero — ele identifica o seu " +
			"pedido quando a resposta vier.",
	})
}
