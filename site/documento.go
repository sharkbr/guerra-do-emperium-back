package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"strings"
)

// O documento existe por UM motivo: impedir conta ilimitada. O jogo tem
// vantagens diarias por conta (Logue e Ganhe e irmaos), entao conta de
// graca em quantidade estraga o desenho do jogo, nao so' o cadastro.
//
// GUARDAMOS O HASH, NUNCA O NUMERO.
// A unica pergunta que o site precisa responder e' "esse documento ja' foi
// usado?", e hash responde isso igual. O numero em claro so' acrescentaria
// risco no dia de um vazamento - e CPF e celular sao dado pessoal.
// O hash e' HMAC com o segredo do servidor, e nao SHA-256 puro: CPF tem
// 11 digitos, um espaco pequeno o bastante para alguem gerar a tabela
// inteira e reverter um SHA-256 sem chave. Com HMAC, sem o segredo nao ha'
// tabela que sirva.
//
// A HONESTIDADE SOBRE O CPF: o digito verificador e' conta publica, e
// gerador de CPF valido acha-se em qualquer lugar. Como barreira contra
// multi-conta ele vale POUCO - segura engano de digitacao, nao segura quem
// quer burlar. Quem barra de verdade e' o celular, porque numero custa
// dinheiro. Validar o nome contra a Receita resolveria, mas as bases
// serias (Serpro Datavalid) sao pagas e exigem contrato - ficou como
// desejo futuro em PENDENCIAS.md.

var (
	ErrCPFInvalido     = errors.New("CPF invalido")
	ErrCelularInvalido = errors.New("celular invalido")
)

// somenteDigitos tira pontuacao de mascara ("123.456.789-09", "(11) 91234-5678").
func somenteDigitos(s string) string {
	var b strings.Builder
	for _, r := range s {
		if r >= '0' && r <= '9' {
			b.WriteRune(r)
		}
	}
	return b.String()
}

// ValidaCPF confere o formato e os dois digitos verificadores.
func ValidaCPF(entrada string) (string, error) {
	cpf := somenteDigitos(entrada)
	if len(cpf) != 11 {
		return "", ErrCPFInvalido
	}

	// Os onze repetidos (00000000000, 11111111111...) passam na conta dos
	// digitos verificadores e sao invalidos por definicao. Sem esta linha
	// o validador aceita "11111111111", que e' o primeiro palpite de quem
	// esta' testando o cadastro.
	iguais := true
	for i := 1; i < 11; i++ {
		if cpf[i] != cpf[0] {
			iguais = false
			break
		}
	}
	if iguais {
		return "", ErrCPFInvalido
	}

	for _, dv := range []int{9, 10} {
		soma := 0
		peso := dv + 1
		for i := 0; i < dv; i++ {
			soma += int(cpf[i]-'0') * peso
			peso--
		}
		resto := (soma * 10) % 11
		if resto == 10 {
			resto = 0
		}
		if resto != int(cpf[dv]-'0') {
			return "", ErrCPFInvalido
		}
	}
	return cpf, nil
}

// ValidaCelular normaliza para o formato E.164 brasileiro (5511912345678).
// Aceita com ou sem DDI, com ou sem mascara.
func ValidaCelular(entrada string) (string, error) {
	n := somenteDigitos(entrada)
	n = strings.TrimPrefix(n, "0")

	// Sem DDI: 11 digitos (DDD + 9 + numero).
	if len(n) == 11 {
		n = "55" + n
	}
	if len(n) != 13 || !strings.HasPrefix(n, "55") {
		return "", ErrCelularInvalido
	}

	ddd := n[2:4]
	if ddd < "11" || ddd > "99" {
		return "", ErrCelularInvalido
	}
	// Celular brasileiro comeca com 9 depois do DDD. Fixo nao recebe
	// WhatsApp nem SMS, entao recusar aqui evita cadastro que nunca chega
	// a ser verificado.
	if n[4] != '9' {
		return "", ErrCelularInvalido
	}
	return n, nil
}

// HashDocumento e' o que vai para o banco. Ver o bloco no topo do arquivo.
func HashDocumento(segredo []byte, tipo, numero string) string {
	m := hmac.New(sha256.New, segredo)
	m.Write([]byte(tipo))
	m.Write([]byte{0})
	m.Write([]byte(numero))
	return hex.EncodeToString(m.Sum(nil))
}
