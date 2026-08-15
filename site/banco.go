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
type Banco struct {
	db *sql.DB
}

func AbreBanco(dsn string) (*Banco, error) {
	// Ver regra 1 acima. Acrescentado aqui e nao pedido ao operador para
	// que esquecer no .env nao vire defeito calado.
	if !strings.Contains(dsn, "charset=") {
		sep := "?"
		if strings.Contains(dsn, "?") {
			sep = "&"
		}
		dsn += sep + "charset=latin1"
	}
	if !strings.Contains(dsn, "parseTime=") {
		dsn += "&parseTime=true"
	}

	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, err
	}
	// A maquina e' pequena e o MariaDB divide memoria com o map-server.
	// Poucas conexoes, recicladas.
	db.SetMaxOpenConns(8)
	db.SetMaxIdleConns(4)
	db.SetConnMaxLifetime(30 * time.Minute)

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("sem resposta do banco: %w", err)
	}
	return &Banco{db: db}, nil
}

func (b *Banco) Fecha() { _ = b.db.Close() }

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
