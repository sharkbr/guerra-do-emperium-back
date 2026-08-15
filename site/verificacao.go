package main

import (
	"bytes"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"math/big"
	"net/http"
	"sync"
	"time"
)

// Verificador diz se o cadastro precisa de um codigo antes de virar conta.
//
// SAO DUAS IMPLEMENTACOES, TROCADAS POR CONFIGURACAO, e essa foi a decisao
// que destravou o beta em 2026-08-14: o dono precisava do site no ar no
// mesmo dia, e a integracao com o WhatsApp (Penelope) so' sairia no dia
// seguinte.
//
//	SITE_VERIFICACAO=nenhuma   -> a conta nasce na hora (beta)
//	SITE_VERIFICACAO=penelope  -> manda codigo por WhatsApp e espera
//
// O DETALHE QUE FAZ ISSO VALER A PENA: mesmo em "nenhuma", o hash do
// documento e' gravado igual. Entao o limite de uma conta por CPF/celular
// vale desde o primeiro cadastro do beta - ligar a verificacao depois nao
// deixa para tras um bolo de contas que nunca passaram por limite nenhum.
// Trocar de modo e' uma linha no .env, nao uma migracao.
type Verificador interface {
	// Exige diz se este documento precisa de codigo.
	Exige(tipo string) bool
	// Envia gera e manda o codigo. Devolve o identificador do pedido.
	Envia(tipo, destino string) (string, error)
	// Confere valida o codigo e devolve o destino verificado.
	Confere(pedido, codigo string) (string, error)
}

func NovoVerificador(cfg Config) Verificador {
	switch cfg.ModoVerificacao {
	case "penelope":
		log.Println("verificacao: codigo por WhatsApp (Penelope)")
		return &Penelope{
			url:   cfg.PenelopeURL,
			token: cfg.PenelopeToken,
			pend:  &pendencias{m: map[string]pendencia{}},
		}
	default:
		log.Println("verificacao: NENHUMA - conta criada na hora (modo beta)")
		return SemVerificacao{}
	}
}

// SemVerificacao - o modo do beta. Nao pede codigo de ninguem.
type SemVerificacao struct{}

func (SemVerificacao) Exige(string) bool { return false }
func (SemVerificacao) Envia(_, destino string) (string, error) {
	return destino, nil
}
func (SemVerificacao) Confere(pedido, _ string) (string, error) { return pedido, nil }

// pendencia e' um cadastro esperando codigo.
type pendencia struct {
	destino string
	codigo  string
	expira  time.Time
	erros   int
}

type pendencias struct {
	mu sync.Mutex
	m  map[string]pendencia
}

// Penelope manda o codigo pelo WhatsApp, chamando a API que o dono ja'
// mantem. E' preferivel a SMS por dois motivos: custo marginal zero (SMS
// no Brasil sai a ~US$0,05 em qualquer provedor, e nao ha' gratuito
// confiavel) e entrega melhor.
//
// RESSALVA que depende de como o Penelope esta' montado: se ele usa a API
// oficial (Cloud API), mandar mensagem para quem nunca falou com o numero
// exige um TEMPLATE de categoria utilidade, aprovado antes - e ha' uma
// taxa pequena por conversa.
type Penelope struct {
	url   string
	token string
	pend  *pendencias
}

func (Penelope) Exige(tipo string) bool {
	// CPF nao tem para onde mandar codigo. Ele entra pelo formato apenas -
	// e o proprio documento.go registra que isso barra pouco.
	return tipo == "celular"
}

func (p *Penelope) Envia(tipo, destino string) (string, error) {
	if !p.Exige(tipo) {
		return destino, nil
	}

	codigo := codigoDe6()
	pedido := fmt.Sprintf("%d-%s", time.Now().UnixNano(), codigoDe6())

	p.pend.mu.Lock()
	p.pend.m[pedido] = pendencia{
		destino: destino,
		codigo:  codigo,
		expira:  time.Now().Add(10 * time.Minute),
	}
	// Faxina do que expirou, para o mapa nao crescer sem fim.
	for k, v := range p.pend.m {
		if time.Now().After(v.expira) {
			delete(p.pend.m, k)
		}
	}
	p.pend.mu.Unlock()

	corpo, _ := json.Marshal(map[string]string{
		"destino":  destino,
		"mensagem": "Guerra do Emperium: seu codigo de cadastro e' " + codigo + ". Vale por 10 minutos.",
	})

	req, err := http.NewRequest(http.MethodPost, p.url, bytes.NewReader(corpo))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	if p.token != "" {
		req.Header.Set("Authorization", "Bearer "+p.token)
	}

	cli := &http.Client{Timeout: 15 * time.Second}
	resp, err := cli.Do(req)
	if err != nil {
		return "", fmt.Errorf("nao consegui falar com o servico de mensagem: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return "", fmt.Errorf("servico de mensagem respondeu %d", resp.StatusCode)
	}
	return pedido, nil
}

func (p *Penelope) Confere(pedido, codigo string) (string, error) {
	p.pend.mu.Lock()
	defer p.pend.mu.Unlock()

	v, ok := p.pend.m[pedido]
	if !ok {
		return "", fmt.Errorf("pedido desconhecido ou expirado")
	}
	if time.Now().After(v.expira) {
		delete(p.pend.m, pedido)
		return "", fmt.Errorf("o codigo expirou - peca outro")
	}
	if v.codigo != codigo {
		// Teto de tentativas: sem ele, seis digitos caem por forca bruta
		// em poucos minutos.
		v.erros++
		if v.erros >= 5 {
			delete(p.pend.m, pedido)
			return "", fmt.Errorf("codigo errado vezes demais - peca outro")
		}
		p.pend.m[pedido] = v
		return "", fmt.Errorf("codigo errado")
	}
	delete(p.pend.m, pedido)
	return v.destino, nil
}

// codigoDe6 usa crypto/rand, e nao math/rand: codigo de verificacao
// previsivel e' o mesmo que nao ter verificacao.
func codigoDe6() string {
	n, err := rand.Int(rand.Reader, big.NewInt(1000000))
	if err != nil {
		// Falha do gerador do sistema e' coisa seria; melhor derrubar do
		// que emitir codigo fraco.
		log.Fatalf("sem entropia do sistema: %v", err)
	}
	return fmt.Sprintf("%06d", n.Int64())
}
