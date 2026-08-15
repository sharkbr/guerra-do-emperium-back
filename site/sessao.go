package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"fmt"
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// Sessao em COOKIE ASSINADO, sem tabela.
//
// O painel do jogador tem tres botoes e nenhum estado entre requisicoes -
// nao ha' o que uma tabela de sessao guardaria. Um cookie com
// "<id>.<validade>.<hmac>" resolve, e ainda tira uma consulta ao banco de
// toda requisicao autenticada, o que importa numa maquina de 961 MB.
//
// O preco e' que nao da' para invalidar sessao do lado do servidor antes
// da validade. Para tres botoes, aceitavel; se um dia houver banimento
// pelo site, isto vira tabela.

const nomeCookie = "guerra_sessao"
const duracaoSessao = 7 * 24 * time.Hour

var ErrSessaoInvalida = errors.New("sessao invalida")

func (s *Servidor) assina(dados string) string {
	m := hmac.New(sha256.New, s.cfg.Segredo)
	m.Write([]byte(dados))
	return base64.RawURLEncoding.EncodeToString(m.Sum(nil))
}

func (s *Servidor) poeCookie(w http.ResponseWriter, r *http.Request, id int64) {
	dados := fmt.Sprintf("%d.%d", id, time.Now().Add(duracaoSessao).Unix())
	http.SetCookie(w, &http.Cookie{
		Name:     nomeCookie,
		Value:    dados + "." + s.assina(dados),
		Path:     "/",
		HttpOnly: true, // JavaScript nao le' - defesa contra XSS roubar sessao
		SameSite: http.SameSiteLaxMode,
		// Secure so' quando ha' TLS: em desenvolvimento (http://localhost)
		// um cookie Secure simplesmente nao e' guardado, e o login "nao
		// funciona" sem erro nenhum.
		Secure:  r.TLS != nil || r.Header.Get("X-Forwarded-Proto") == "https",
		Expires: time.Now().Add(duracaoSessao),
	})
}

func (s *Servidor) tiraCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name: nomeCookie, Value: "", Path: "/", MaxAge: -1, HttpOnly: true,
	})
}

// quemE devolve o account_id do cookie, ou erro. A comparacao da assinatura
// e' com hmac.Equal (tempo constante) e nao com ==, para nao vazar por
// quanto tempo a comparacao durou.
func (s *Servidor) quemE(r *http.Request) (int64, error) {
	c, err := r.Cookie(nomeCookie)
	if err != nil {
		return 0, ErrSessaoInvalida
	}
	partes := strings.Split(c.Value, ".")
	if len(partes) != 3 {
		return 0, ErrSessaoInvalida
	}
	dados := partes[0] + "." + partes[1]
	if !hmac.Equal([]byte(partes[2]), []byte(s.assina(dados))) {
		return 0, ErrSessaoInvalida
	}
	validade, err := strconv.ParseInt(partes[1], 10, 64)
	if err != nil || time.Now().Unix() > validade {
		return 0, ErrSessaoInvalida
	}
	id, err := strconv.ParseInt(partes[0], 10, 64)
	if err != nil {
		return 0, ErrSessaoInvalida
	}
	return id, nil
}

// ipDe respeita o X-Forwarded-For porque o site vai ficar atras do nginx -
// sem isto, TODO mundo aparece como 127.0.0.1 e o limitador por IP vira
// um limite global que tranca o servidor inteiro no primeiro engracadinho.
func ipDe(r *http.Request) string {
	if f := r.Header.Get("X-Forwarded-For"); f != "" {
		if i := strings.IndexByte(f, ','); i > 0 {
			return strings.TrimSpace(f[:i])
		}
		return strings.TrimSpace(f)
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

// Limitador: teto de tentativas por IP numa janela de tempo. Em memoria,
// de proposito - reiniciar o site zera a contagem, e para o volume de um
// beta isso e' irrelevante perto de manter estado em banco.
type Limitador struct {
	mu     sync.Mutex
	teto   int
	janela time.Duration
	visto  map[string][]time.Time
}

func NovoLimitador(teto int, janela time.Duration) *Limitador {
	return &Limitador{teto: teto, janela: janela, visto: map[string][]time.Time{}}
}

func (l *Limitador) Permite(chave string) bool {
	l.mu.Lock()
	defer l.mu.Unlock()

	agora := time.Now()
	corte := agora.Add(-l.janela)

	restantes := l.visto[chave][:0]
	for _, t := range l.visto[chave] {
		if t.After(corte) {
			restantes = append(restantes, t)
		}
	}
	if len(restantes) >= l.teto {
		l.visto[chave] = restantes
		return false
	}
	l.visto[chave] = append(restantes, agora)

	// Faxina barata: sem ela o mapa cresce para sempre com IP que passou
	// uma vez e nunca voltou.
	if len(l.visto) > 10000 {
		for k, v := range l.visto {
			if len(v) == 0 || v[len(v)-1].Before(corte) {
				delete(l.visto, k)
			}
		}
	}
	return true
}
