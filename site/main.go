// Site da Guerra do Emperium - criacao de conta e painel do jogador.
//
// Um binario so', que serve o front estatico de web/ e a API em /api/.
// A escolha do Go nao foi de gosto: a maquina tem 961 MB e o map-server
// sozinho ocupa 250-400 MB. Este processo fica em torno de 20 MB de RSS,
// onde um Node ficaria em 150-300 - que ali e' dinheiro de verdade.
//
// COMO RODAR (local):
//
//	cp config.exemplo.env config.env   # e preencha
//	set -a && . ./config.env && set +a
//	go run .
//
// A configuracao mora em VARIAVEL DE AMBIENTE, nunca em arquivo versionado -
// mesma regra do conf/import/ do rAthena (CLAUDE.md secao 8).
package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"
)

// Config e' lida do ambiente na subida. Falta de valor obrigatorio derruba
// o processo ali mesmo, e nao no primeiro cadastro - erro de configuracao
// tem de aparecer no boot, nao na cara do jogador.
type Config struct {
	Endereco  string // onde escutar, ex ":8080"
	BancoDSN  string
	Segredo   []byte // assina o cookie de sessao
	MaxContas int    // contas por documento; 1 no beta

	// Verificacao: "nenhuma" cria a conta na hora (beta), "penelope" manda
	// codigo por WhatsApp. Ver verificacao.go.
	ModoVerificacao string
	PenelopeURL     string
	PenelopeToken   string

	// Para onde o botao Baixar aponta. Fica em configuracao, e nao no
	// HTML, para trocar o endereco nao exigir recompilar nem mexer em
	// arquivo do site - e' o tipo de coisa que muda a cada versao do
	// cliente. Vazio = o botao aparece desligado, dizendo "em breve".
	DownloadURL string
}

func leConfig() Config {
	c := Config{
		Endereco:        valor("SITE_ENDERECO", ":8080"),
		BancoDSN:        obrigatorio("SITE_BANCO_DSN"),
		Segredo:         []byte(obrigatorio("SITE_SEGREDO")),
		MaxContas:       numero("SITE_MAX_CONTAS", 1),
		ModoVerificacao: valor("SITE_VERIFICACAO", "nenhuma"),
		PenelopeURL:     valor("SITE_PENELOPE_URL", ""),
		PenelopeToken:   valor("SITE_PENELOPE_TOKEN", ""),
		DownloadURL:     valor("SITE_DOWNLOAD_URL", ""),
	}
	if len(c.Segredo) < 32 {
		log.Fatal("SITE_SEGREDO precisa de pelo menos 32 caracteres - " +
			"e' o que assina o cookie de sessao")
	}
	if c.ModoVerificacao == "penelope" && c.PenelopeURL == "" {
		log.Fatal("SITE_VERIFICACAO=penelope exige SITE_PENELOPE_URL")
	}
	return c
}

func valor(chave, padrao string) string {
	if v := strings.TrimSpace(os.Getenv(chave)); v != "" {
		return v
	}
	return padrao
}

func obrigatorio(chave string) string {
	v := strings.TrimSpace(os.Getenv(chave))
	if v == "" {
		log.Fatalf("falta a variavel de ambiente %s", chave)
	}
	return v
}

func numero(chave string, padrao int) int {
	if v := os.Getenv(chave); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return padrao
}

// Servidor amarra as pecas. Guardado num tipo para os handlers nao lerem
// estado global - facilita teste e deixa explicito quem depende de que.
type Servidor struct {
	cfg      Config
	banco    *Banco
	verifica Verificador
	limite   *Limitador
}

func main() {
	log.SetFlags(log.Ldate | log.Ltime)
	cfg := leConfig()

	banco, err := AbreBanco(cfg.BancoDSN)
	if err != nil {
		log.Fatalf("banco: %v", err)
	}
	defer banco.Fecha()

	s := &Servidor{
		cfg:      cfg,
		banco:    banco,
		verifica: NovoVerificador(cfg),
		// Teto por IP na criacao de conta. Nao substitui o limite por
		// documento - so' encarece a tentativa em massa.
		limite: NovoLimitador(10, time.Hour),
	}

	mux := http.NewServeMux()

	// API. Tudo POST menos as leituras, e tudo devolve JSON.
	mux.HandleFunc("POST /api/conta/inicia", s.contaInicia)
	mux.HandleFunc("POST /api/conta/confirma", s.contaConfirma)
	mux.HandleFunc("POST /api/sessao", s.sessaoAbre)
	mux.HandleFunc("POST /api/sessao/sair", s.sessaoFecha)
	mux.HandleFunc("GET /api/config", s.config)
	mux.HandleFunc("GET /api/painel", s.painel)
	mux.HandleFunc("POST /api/painel/senha", s.trocaSenha)
	mux.HandleFunc("POST /api/painel/pin", s.recuperaPin)
	mux.HandleFunc("GET /api/painel/personagens", s.personagens)
	mux.HandleFunc("POST /api/painel/destrava", s.destrava)
	// So' grava. A leitura dos chamados vira com o painel do dono
	// (PENDENCIAS.md); ate' la' nao ha' rota que devolva chamado nenhum,
	// nem o proprio.
	mux.HandleFunc("POST /api/painel/chamado", s.abreChamado)

	// Front estatico.
	mux.Handle("/", semCache(http.FileServer(http.Dir("web"))))

	srv := &http.Server{
		Addr:              cfg.Endereco,
		Handler:           registra(mux),
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	// Desligamento limpo: o systemd manda SIGTERM, e sem isto uma conexao
	// no meio de um cadastro morre pela metade.
	parar := make(chan os.Signal, 1)
	signal.Notify(parar, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-parar
		log.Println("desligando...")
		ctx, cancela := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancela()
		_ = srv.Shutdown(ctx)
	}()

	log.Printf("site no ar em %s (verificacao: %s, max %d conta(s) por documento)",
		cfg.Endereco, cfg.ModoVerificacao, cfg.MaxContas)
	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatal(err)
	}
	log.Println("ate' logo")
}

// semCache manda o navegador CONFERIR antes de usar o que ele guardou.
//
// Sem cabecalho de cache nenhum - que era o caso ate' 2026-08-22 - o
// navegador nao fica sem cache: ele inventa um. E' o cache HEURISTICO do
// RFC 9111, e a regra usual e' guardar por 10% do tempo desde o
// Last-Modified. Consequencia perversa: quanto mais VELHO o arquivo,
// MAIOR o tempo que a copia velha e' considerada fresca - um estilo.css
// parado ha' uma semana fica valendo por umas quinze horas depois de
// trocado, e o navegador nem pergunta.
//
// A falha e' calada e do pior tipo: o deploy dizia sucesso, o arquivo
// certo estava no servidor, e a tela do jogador continuava a antiga.
// Achado em 2026-08-22, quando a caixa de texto do formulario de chamado
// apareceu sem estilo para o dono - o CSS no ar ja' estava correto.
//
// "no-cache" NAO quer dizer "nao guarde": quer dizer "guarde, mas
// pergunte antes de usar". Com o Last-Modified que o FileServer ja' manda,
// a pergunta volta como um 304 de duzentos bytes - barato o bastante para
// um site deste tamanho, e a alternativa (versionar o nome de cada
// arquivo) exige um passo de build que aqui nao existe.
//
// Em /api/ o caso e' outro e o cabecalho tambem: ali trafega nome de
// conta, e-mail e lista de personagens. Resposta com dado pessoal nao se
// guarda em disco nenhum - "no-store".
func semCache(prox http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Cache-Control", "no-cache")
		prox.ServeHTTP(w, r)
	})
}

// registra poe uma linha por requisicao no log. Sem corpo e sem query -
// eles carregam senha e CPF, e log e' o lugar classico onde segredo vaza
// sem ninguem perceber.
func registra(prox http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		inicio := time.Now()
		// Ver semCache: /api/ carrega dado pessoal e nao se guarda em
		// lugar nenhum. Posto ANTES do handler para que valha tambem nas
		// respostas de erro, que saem por outros caminhos.
		if strings.HasPrefix(r.URL.Path, "/api/") {
			w.Header().Set("Cache-Control", "no-store")
		}
		prox.ServeHTTP(w, r)
		if strings.HasPrefix(r.URL.Path, "/api/") {
			log.Printf("%s %s %s (%v)", ipDe(r), r.Method, r.URL.Path,
				time.Since(inicio).Round(time.Millisecond))
		}
	})
}
