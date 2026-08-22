package main

import (
	"database/sql"
	"errors"
	"fmt"
	"log"
	"strings"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

// Banco e' a mesma base que o rAthena usa. Duas regras que vem de la' e
// nao se negociam:
//
//  1. A CONEXAO TEM DE SER latin1. As 105 colunas de texto do rAthena sao
//     latin1, e o padrao do MariaDB 12 e' utf8mb4 - um byte acentuado
//     mandado por uma conexao utf8mb4 e' UTF-8 invalido e o servidor recusa
//     a gravacao inteira com "Incorrect string value". E' a mesma armadilha
//     que o CLAUDE.md secao 5 documenta do lado do emulador, e que o
//     conf/guerra/inter_guerra.txt resolve la' com default_codepage.
//
//  2. A SENHA VAI EM MD5. O use_MD5_passwords: yes esta' ligado desde
//     2026-08-14 (IMPLANTACAO.md Etapa 1), e a coluna user_pass e'
//     varchar(32) - exatamente o tamanho de um MD5 em hexadecimal. Gravar
//     texto puro aqui cria conta que nunca loga.
//
//  3. SAO DUAS CONEXOES, E CADA UMA SO' ENCOSTA NAS TABELAS DELA.
//     A `db` fala latin1 e serve o que o JOGO le' (login, char). A
//     `dbTexto` fala utf8mb4 e serve so' a `guerra_site_chamado`, que e'
//     texto livre de jogador e nunca passa pelo jogo - ver o cabecalho
//     daquela tabela em sql/site.sql.
//
//     Nao ha' meio-termo: o charset e' escolhido na abertura da conexao, e
//     e' ele que decide como o MySQL interpreta os bytes que chegam. Uma
//     conexao so' guardaria acento de chamado como mojibake (byte UTF-8
//     lido como latin1) ou recusaria a gravacao inteira - as duas caladas,
//     e a segunda so' na hora em que um jogador escrevesse com acento.
//
//     Custo medido em conexao ociosa, nao em memoria do processo: a
//     dbTexto vai a 4 conexoes e uma ociosa, porque chamado e' raro.
type Banco struct {
	db *sql.DB // latin1: login, char - tudo do rAthena

	// utf8mb4: so' guerra_site_chamado. Ver a regra 3 acima.
	dbTexto *sql.DB
}

func AbreBanco(dsn string) (*Banco, error) {
	// Ver regra 1 acima. Acrescentado aqui e nao pedido ao operador para
	// que esquecer no .env nao vire defeito calado.
	db, err := abreCom(dsn, "latin1", 8, 4)
	if err != nil {
		return nil, err
	}
	// Ver regra 3. O mesmo DSN, outro charset.
	dbTexto, err := abreCom(dsn, "utf8mb4", 4, 1)
	if err != nil {
		_ = db.Close()
		return nil, err
	}
	return &Banco{db: db, dbTexto: dbTexto}, nil
}

// abreCom monta o pool com o charset PEDIDO, ignorando o que estiver no
// DSN. E' de proposito: com duas conexoes de charsets diferentes saindo do
// mesmo endereco, deixar o valor do .env vencer transformaria um descuido
// de configuracao em dado corrompido - e corrompido so' na linha de quem
// escreveu com acento.
func abreCom(dsn, charset string, max, ocioso int) (*sql.DB, error) {
	// A ordem importa: o separador tem de ser decidido DEPOIS da limpeza.
	// Medido pelo caso real do config.env, que ja' traz "?charset=latin1" -
	// tirar o parametro deixa o DSN sem "?", e um "&" colado ali produz um
	// endereco que o driver aceita e le' errado.
	dsn = tiraParametro(dsn, "charset")
	sep := "?"
	if strings.Contains(dsn, "?") {
		sep = "&"
	}
	dsn += sep + "charset=" + charset
	if !strings.Contains(dsn, "parseTime=") {
		dsn += "&parseTime=true"
	}

	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, err
	}
	// A maquina e' pequena e o MariaDB divide memoria com o map-server.
	// Poucas conexoes, recicladas.
	db.SetMaxOpenConns(max)
	db.SetMaxIdleConns(ocioso)
	db.SetConnMaxLifetime(30 * time.Minute)

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("sem resposta do banco (%s): %w", charset, err)
	}
	return db, nil
}

// tiraParametro remove "chave=valor" da query do DSN, com a separacao que
// vier junto. Sem isto, o charset do .env ficaria no DSN e o segundo
// charset acrescentado seria ignorado pelo driver (ele fica com o
// primeiro), o que e' exatamente o defeito calado que abreCom evita.
func tiraParametro(dsn, chave string) string {
	i := strings.IndexByte(dsn, '?')
	if i < 0 {
		return dsn
	}
	base, query := dsn[:i], dsn[i+1:]
	var fica []string
	for _, p := range strings.Split(query, "&") {
		if p == "" || strings.HasPrefix(p, chave+"=") {
			continue
		}
		fica = append(fica, p)
	}
	if len(fica) == 0 {
		return base
	}
	return base + "?" + strings.Join(fica, "&")
}

func (b *Banco) Fecha() {
	_ = b.db.Close()
	_ = b.dbTexto.Close()
}

var (
	ErrUsuarioExiste  = errors.New("ja existe conta com esse nome")
	ErrDocumentoUsado = errors.New("esse documento ja tem conta")
	ErrNaoAchou       = errors.New("nao achou")
)

// Conta e' o pedaco da tabela login que o site enxerga. O resto (grupo,
// banimento, VIP) e' assunto do jogo e o site nao toca.
type Conta struct {
	ID      int64
	Usuario string
	Email   string
	Pin     string
	Criada  time.Time
}

// UsuarioLivre responde se o nome esta' disponivel. O rAthena nao poe
// UNIQUE em userid - ha' so' um indice comum -, entao a checagem e' nossa,
// e a corrida entre duas requisicoes simultaneas e' fechada pelo UNIQUE da
// nossa tabela de cadastro, nao por esta consulta.
func (b *Banco) UsuarioLivre(usuario string) (bool, error) {
	var n int
	err := b.db.QueryRow("SELECT COUNT(*) FROM login WHERE userid = ?", usuario).Scan(&n)
	if err != nil {
		return false, err
	}
	return n == 0, nil
}

// ContasPorDocumento conta quantas contas ja' nasceram daquele documento.
// E' o que segura a criacao desenfreada - ver documento.go para o porque
// de guardarmos o hash e nao o numero.
func (b *Banco) ContasPorDocumento(hash string) (int, error) {
	var n int
	err := b.db.QueryRow(
		"SELECT COUNT(*) FROM guerra_site_cadastro WHERE documento_hash = ?", hash).Scan(&n)
	return n, err
}

// CriaConta grava nas duas tabelas, e a ORDEM aqui e' a parte que importa.
//
// NAO ha' transacao cobrindo as duas, e nao adianta querer: a `login` do
// rAthena e' MyISAM, que ignora transacao - um BEGIN/ROLLBACK em volta das
// duas parece proteger e nao protege. Se a conta nascesse primeiro e a
// gravacao do documento falhasse por duplicidade, sobraria conta JOGAVEL e
// SEM DOCUMENTO: o furo no limite, aberto justamente por quem tentou
// burla-lo.
//
// Entao: reserva o documento -> cria a conta -> completa a reserva. A
// UNIQUE em documento_hash recusa o segundo pedido antes de qualquer conta
// existir. Ver o cabecalho de sql/site.sql.
func (b *Banco) CriaConta(usuario, senhaMD5, email, sexo, docHash, docTipo, ip string) (int64, error) {
	// Reserva orfa (processo morto entre os passos) bloquearia o documento
	// para sempre. Quinze minutos e' folga de sobra para um cadastro.
	_, _ = b.db.Exec(
		`DELETE FROM guerra_site_cadastro
		  WHERE account_id IS NULL AND criado_em < NOW() - INTERVAL 15 MINUTE`)

	res, err := b.db.Exec(
		`INSERT INTO guerra_site_cadastro (account_id, documento_hash, documento_tipo, ip, criado_em)
		 VALUES (NULL, ?, ?, ?, NOW())`, docHash, docTipo, ip)
	if err != nil {
		if strings.Contains(strings.ToLower(err.Error()), "duplicate") {
			return 0, ErrDocumentoUsado
		}
		return 0, err
	}
	reserva, err := res.LastInsertId()
	if err != nil {
		return 0, err
	}

	// Daqui para baixo, qualquer falha tem de devolver a reserva - senao o
	// documento fica preso sem conta nenhuma do outro lado.
	desfaz := func() {
		_, _ = b.db.Exec("DELETE FROM guerra_site_cadastro WHERE id = ?", reserva)
	}

	var n int
	if err := b.db.QueryRow("SELECT COUNT(*) FROM login WHERE userid = ?", usuario).Scan(&n); err != nil {
		desfaz()
		return 0, err
	}
	if n > 0 {
		desfaz()
		return 0, ErrUsuarioExiste
	}

	res, err = b.db.Exec(
		`INSERT INTO login (userid, user_pass, sex, email, group_id, character_slots)
		 VALUES (?, ?, ?, ?, 0, 9)`,
		usuario, senhaMD5, sexo, email)
	if err != nil {
		desfaz()
		return 0, err
	}
	id, err := res.LastInsertId()
	if err != nil {
		desfaz()
		return 0, err
	}

	if _, err := b.db.Exec(
		`UPDATE guerra_site_cadastro SET account_id = ? WHERE id = ?`, id, reserva); err != nil {
		// A conta existe e a reserva ficou pela metade. Apagar a conta aqui
		// seria pior (ela pode ja' estar em uso); a reserva sem account_id
		// vai embora na faxina e o documento volta a ficar livre. Fica no
		// log para aparecer.
		log.Printf("ATENCAO: conta %d criada mas a reserva %d nao foi completada: %v",
			id, reserva, err)
	}

	return id, nil
}

// PorUsuarioESenha e' o login. A comparacao e' feita no banco justamente
// porque a senha guardada e' MD5: a gente hasheia o que veio e compara.
func (b *Banco) PorUsuarioESenha(usuario, senhaMD5 string) (*Conta, error) {
	c := &Conta{}
	err := b.db.QueryRow(
		`SELECT account_id, userid, email, pincode FROM login
		 WHERE userid = ? AND user_pass = ?`, usuario, senhaMD5).
		Scan(&c.ID, &c.Usuario, &c.Email, &c.Pin)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, ErrNaoAchou
	}
	return c, err
}

func (b *Banco) PorID(id int64) (*Conta, error) {
	c := &Conta{}
	err := b.db.QueryRow(
		`SELECT account_id, userid, email, pincode FROM login WHERE account_id = ?`, id).
		Scan(&c.ID, &c.Usuario, &c.Email, &c.Pin)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, ErrNaoAchou
	}
	return c, err
}

func (b *Banco) TrocaSenha(id int64, novaMD5 string) error {
	_, err := b.db.Exec("UPDATE login SET user_pass = ? WHERE account_id = ?", novaMD5, id)
	return err
}

// LimpaPin esvazia o pincode. Com ele vazio, o cliente pede um PIN novo no
// proximo login - e' o "esqueci meu PIN" que de fato resolve, ja' que o
// jogador escolhe outro na hora.
func (b *Banco) LimpaPin(id int64) error {
	_, err := b.db.Exec("UPDATE login SET pincode = '', pincode_change = 0 WHERE account_id = ?", id)
	return err
}

// ------------------------------------------------------------------
// PERSONAGENS
//
// O site so' encosta na `char` para uma coisa: tirar personagem preso de
// mapa que ainda nao existe neste servidor. Nada mais - inventario, nivel
// e equipamento sao assunto do jogo.

// Personagem e' o pedaco da `char` que o painel precisa mostrar.
type Personagem struct {
	ID     int64
	Nome   string
	Nivel  int
	Mapa   string
	X, Y   int
	Online bool
}

// Prontera, o destino do destravamento. A celula foi conferida contra o
// db/re/map_cache.dat (o unico dos tres que tem a prontera de renewal -
// CLAUDE.md secao 5): 155,183 e' andavel, no meio da praca da fonte.
const (
	mapaSeguro = "prontera"
	xSeguro    = 155
	ySeguro    = 183
)

// Personagens lista os personagens da conta.
//
// `char` E' PALAVRA RESERVADA do MySQL: sem a crase a consulta nao compila,
// e a mensagem de erro aponta para o meio do SELECT.
//
// O nome vem em latin1 desta conexao, e o nosso conf/guerra/char_guerra.txt
// permite acento em nome de personagem - por isso o deLatin1. Sem ele o
// encoding/json troca cada byte acentuado por U+FFFD e o jogador nao
// reconhece o proprio personagem na lista.
func (b *Banco) Personagens(conta int64) ([]Personagem, error) {
	linhas, err := b.db.Query(
		"SELECT char_id, name, base_level, last_map, last_x, last_y, online "+
			"FROM `char` WHERE account_id = ? ORDER BY char_num", conta)
	if err != nil {
		return nil, err
	}
	defer linhas.Close()

	var lista []Personagem
	for linhas.Next() {
		var p Personagem
		var online int
		if err := linhas.Scan(&p.ID, &p.Nome, &p.Nivel, &p.Mapa, &p.X, &p.Y, &online); err != nil {
			return nil, err
		}
		p.Nome = deLatin1(p.Nome)
		p.Online = online != 0
		lista = append(lista, p)
	}
	return lista, linhas.Err()
}

var (
	ErrPersonagemOnline = errors.New("o personagem esta conectado")
	ErrJaEmProntera     = errors.New("o personagem ja esta em Prontera")
)

// MoveParaProntera destrava um personagem, e a guarda que faz isto ser
// seguro e' o `online = 0` do WHERE.
//
// O char-server carrega o personagem do banco quando ele entra no jogo e so'
// escreve de volta ao sair (char_mmo_char_tosql). Um UPDATE feito com o
// jogador conectado seria SOBRESCRITO na saida dele - o site diria "pronto"
// e nada teria acontecido, que e' a pior das duas falhas possiveis aqui.
// Por isso a condicao vai no proprio UPDATE e nao so' na leitura de antes:
// entre uma coisa e outra o jogador pode ter entrado.
//
// O `last_instanceid = 0` e' metade do conserto e a que se esquece: quem
// ficou preso dentro de instancia continua sendo mandado para a copia dela
// se o campo sobreviver.
//
// O PONTO DE RETORNO (save_map) so' e' mexido quando ele aponta para o
// MESMO mapa em que o personagem esta' preso. Zerar sempre custaria ao
// jogador um ponto de retorno legitimo em Payon ou Geffen; deixar sempre
// devolveria ele para a armadilha na primeira morte.
func (b *Banco) MoveParaProntera(conta, personagem int64) error {
	var mapa, salvo string
	err := b.db.QueryRow(
		"SELECT last_map, save_map FROM `char` WHERE char_id = ? AND account_id = ?",
		personagem, conta).Scan(&mapa, &salvo)
	if errors.Is(err, sql.ErrNoRows) {
		return ErrNaoAchou
	}
	if err != nil {
		return err
	}
	if mapa == mapaSeguro {
		return ErrJaEmProntera
	}

	// Nome de variavel que nao seja "sql": o pacote se chama assim, e
	// sombrea-lo aqui apagaria o sql.ErrNoRows lido logo acima.
	consulta := "UPDATE `char` SET last_map = ?, last_x = ?, last_y = ?, last_instanceid = 0"
	args := []any{mapaSeguro, xSeguro, ySeguro}
	if salvo == mapa || salvo == "" {
		consulta += ", save_map = ?, save_x = ?, save_y = ?"
		args = append(args, mapaSeguro, xSeguro, ySeguro)
	}
	consulta += " WHERE char_id = ? AND account_id = ? AND online = 0 LIMIT 1"
	args = append(args, personagem, conta)

	res, err := b.db.Exec(consulta, args...)
	if err != nil {
		return err
	}
	n, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if n == 0 {
		// A linha existe (foi lida acima) e nao foi tocada: so' o online = 0
		// pode ter recusado.
		return ErrPersonagemOnline
	}
	return nil
}

// ------------------------------------------------------------------
// CHAMADOS
//
// Tudo aqui vai pela dbTexto (utf8mb4). Ver a regra 3 no topo do arquivo.

// ChamadosNaHora conta os chamados que a conta abriu na ultima hora. E' o
// teto contra enxurrada, e mora no BANCO e nao no limitador de memoria de
// proposito: reiniciar o site nao pode zerar a contagem de quem estava
// justamente enchendo a fila.
func (b *Banco) ChamadosNaHora(conta int64) (int, error) {
	var n int
	err := b.dbTexto.QueryRow(
		"SELECT COUNT(*) FROM guerra_site_chamado "+
			"WHERE account_id = ? AND criado_em > NOW() - INTERVAL 1 HOUR", conta).Scan(&n)
	return n, err
}

// CriaChamado grava e devolve o numero, que e' o que o jogador leva embora.
// Sem numero na tela ele nao tem como cobrar depois, e o painel de leitura
// (PENDENCIAS.md) vai indexar por ele.
func (b *Banco) CriaChamado(conta int64, usuario, personagem, tipo, assunto, mensagem, ip string) (int64, error) {
	res, err := b.dbTexto.Exec(
		`INSERT INTO guerra_site_chamado
		   (account_id, usuario, personagem, tipo, assunto, mensagem, ip, criado_em)
		 VALUES (?, ?, ?, ?, ?, ?, ?, NOW())`,
		conta, usuario, personagem, tipo, assunto, mensagem, ip)
	if err != nil {
		return 0, err
	}
	return res.LastInsertId()
}

// deLatin1 converte texto vindo da conexao latin1 para o UTF-8 do Go.
//
// A tabela e' pequena porque so' a faixa 0x80-0x9F diverge: o "latin1" do
// MySQL e' na verdade CP1252, onde aqueles 32 bytes carregam aspas curvas,
// travessao e o cifrao do euro em vez dos caracteres de controle do
// ISO-8859-1. O resto e' identico a' tabela Unicode, byte a byte.
//
// Feito a' mao para nao acrescentar golang.org/x/text: o servidor compila
// sem rede, e uma dependencia nova por vinte linhas nao se paga.
func deLatin1(s string) string {
	// Caminho rapido, que e' o de quase todo nome: sem byte alto, nada a
	// fazer.
	alto := false
	for i := 0; i < len(s); i++ {
		if s[i] >= 0x80 {
			alto = true
			break
		}
	}
	if !alto {
		return s
	}

	var b strings.Builder
	b.Grow(len(s) + 8)
	for i := 0; i < len(s); i++ {
		c := s[i]
		switch {
		case c < 0x80:
			b.WriteByte(c)
		case c < 0xA0:
			b.WriteRune(cp1252Alto[c-0x80])
		default:
			b.WriteRune(rune(c))
		}
	}
	return b.String()
}

// Os 32 bytes em que CP1252 e ISO-8859-1 discordam. O 0x81, 0x8D, 0x8F,
// 0x90 e 0x9D nao existem em CP1252; viram o caractere de substituicao em
// vez de sumir, para que um nome estranho apareca estranho e nao encurte.
var cp1252Alto = [32]rune{
	'€', '�', '‚', 'ƒ', '„', '…', '†', '‡',
	'ˆ', '‰', 'Š', '‹', 'Œ', '�', 'Ž', '�',
	'�', '‘', '’', '“', '”', '•', '–', '—',
	'˜', '™', 'š', '›', 'œ', '�', 'ž', 'Ÿ',
}
