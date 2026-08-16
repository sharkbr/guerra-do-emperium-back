// Atualizador da Guerra do Emperium — o que o jogador clica para jogar.
//
// Ele baixa a lista de patches do servidor, aplica os que faltam na pasta do
// cliente e então abre o jogo. É a única peça do projeto que roda na máquina
// do jogador, e por isso a regra aqui é diferente do resto: NADA pode falhar
// de um jeito que impeça o jogador de entrar. Rede fora, servidor fora, disco
// cheio — em todos esses casos ele mostra o que houve e libera o botão Jogar
// com o cliente que já está em disco.
//
// Zero dependências externas de propósito: só a biblioteca padrão, com o Win32
// chamado por `syscall.NewLazyDLL`. `go build` funciona numa máquina sem rede,
// e não há um segundo repositório de terceiro para auditar num binário que vai
// para o computador dos outros.
//
// Compilar (a partir desta pasta):
//
//	go build -ldflags -H=windowsgui -o Jogar.exe .
//
// O `-H=windowsgui` é o que impede a janela preta de console de abrir junto.
package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// VERSAO é o número que o canal de auto-atualização compara. Sobe de um a cada
// Atualizador novo publicado — ver auto.go e `patcher/LEIAME.md`.
const VERSAO = 1

// Os valores padrão existem para o caso de o `Atualizador.ini` não vir no
// pacote ou ser apagado: sem ini, o Atualizador ainda funciona na produção.
const (
	urlPadrao  = "https://libraro.filiponegrao.com.br/patch/"
	jogoPadrao = "GuerraDoEmperium.exe"
)

// config é o `.ini` ao lado do exe. Formato chave=valor, uma por linha, `#`
// comenta. Não é INI de seção — a simplicidade aqui vale mais que a convenção,
// porque este arquivo pode acabar sendo editado por um jogador.
type config struct {
	url  string
	jogo string
}

// leConfig procura `<nome do exe>.ini` e, se não achar, `Atualizador.ini`.
//
// Os dois nomes existem porque o exe já mudou de nome uma vez — nasceu
// `Atualizador.exe` e virou `Jogar.exe` em 2026-08-16, para o jogador não ter
// dúvida sobre onde clicar. Amarrar a configuração ao nome do arquivo faria a
// próxima troca quebrar a instalação de todo mundo em silêncio: sem ini, o exe
// cai nos valores embutidos e continua funcionando — e é justamente por isso
// que a falha não apareceria.
func leConfig(exe string) config {
	c := config{url: urlPadrao, jogo: jogoPadrao}

	raiz := filepath.Dir(exe)
	semExtensao := strings.TrimSuffix(filepath.Base(exe), filepath.Ext(exe))
	var dados []byte
	var err error
	for _, nome := range []string{semExtensao + ".ini", "Atualizador.ini"} {
		dados, err = os.ReadFile(filepath.Join(raiz, nome))
		if err == nil {
			break
		}
	}
	if err != nil {
		return c
	}
	for _, linha := range strings.Split(string(dados), "\n") {
		linha = strings.TrimSpace(linha)
		if linha == "" || strings.HasPrefix(linha, "#") {
			continue
		}
		chave, valor, achou := strings.Cut(linha, "=")
		if !achou {
			continue
		}
		chave, valor = strings.TrimSpace(chave), strings.TrimSpace(valor)
		switch strings.ToLower(chave) {
		case "url":
			if valor != "" {
				c.url = valor
			}
		case "jogo":
			if valor != "" {
				c.jogo = valor
			}
		}
	}
	if !strings.HasSuffix(c.url, "/") {
		c.url += "/"
	}
	return c
}

func main() {
	exe, err := os.Executable()
	if err != nil {
		exe = os.Args[0]
	}
	raiz := filepath.Dir(exe)
	cfg := leConfig(exe)

	// A pasta de trabalho do Atualizador: estado, downloads e a cópia velha de
	// si mesmo. Fica dentro do cliente para o jogador poder apagar a pasta
	// inteira do jogo e não deixar rastro em lugar nenhum do sistema.
	trabalho := filepath.Join(raiz, "patch")
	os.MkdirAll(trabalho, 0o755)
	abreRegistro(trabalho)
	limpaVelho(trabalho, exe)

	j := Abre("Guerra do Emperium")
	j.Jogar = func() error { return jogar(raiz, cfg.jogo) }
	go trabalha(j, raiz, trabalho, cfg)
	j.Laco()
}

// trabalha é a rodada inteira, numa goroutine — a janela precisa da thread
// principal para o laço de mensagens, senão ela congela enquanto baixa.
func trabalha(j *Janela, raiz, trabalho string, cfg config) {
	defer func() {
		// Pânico aqui viraria uma janela morta sem explicação. O jogador
		// merece o botão Jogar mesmo quando o Atualizador se atrapalha.
		if r := recover(); r != nil {
			j.Status(fmt.Sprintf("Falha no atualizador: %v", r))
			j.Libera()
		}
	}()

	j.Status("Procurando atualizações…")

	// A auto-atualização vem primeiro: um Atualizador novo pode saber aplicar
	// algo que este não sabe, então ele tem de estar em pé antes dos patches.
	if trocou, err := autoAtualiza(j, raiz, trabalho, cfg); err != nil {
		// Falhar aqui não impede nada — segue com o Atualizador atual.
		j.Status("Não foi possível conferir o atualizador: " + resumo(err))
		time.Sleep(2 * time.Second)
	} else if trocou {
		return // o exe novo já foi lançado; este morre em silêncio
	}

	lista, err := baixaLista(cfg.url)
	if err != nil {
		// Sem "sem conexão": pode ser a lista ausente, o servidor em manutenção
		// ou a internet do jogador. Dizer qual das três é o que o log faz.
		anota("lista: %v", err)
		j.Status("Não consegui conferir as atualizações. Você pode jogar assim mesmo.")
		j.Libera()
		return
	}

	aplicados := leAplicados(trabalho)
	var faltam []patch
	for _, p := range lista {
		if !aplicados[p.Numero] {
			faltam = append(faltam, p)
		}
	}

	if len(faltam) == 0 {
		// Barra cheia, e não vazia: quem abre o Atualizador e vê a barra zerada
		// entende "não fez nada" — que é o contrário do que aconteceu.
		j.Progresso(100)
		j.Status(fmt.Sprintf("Cliente atualizado — %s.", plural(len(lista),
			"1 atualização instalada", "%d atualizações instaladas")))
		j.Libera()
		return
	}

	for i, p := range faltam {
		rotulo := fmt.Sprintf("[%d/%d] %s", i+1, len(faltam), p.Nome)
		if err := aplica(j, raiz, trabalho, cfg.url, p, rotulo); err != nil {
			j.Status("Falhou em " + p.Nome + ": " + resumo(err))
			j.Libera()
			return
		}
	}

	j.Progresso(100)
	j.Status("Pronto — " + plural(len(faltam),
		"1 atualização aplicada", "%d atualizações aplicadas") + ".")
	j.Libera()
}

// plural existe porque "1 atualização(ões) aplicada(s)" é o tipo de texto que
// denuncia programa mal-acabado logo na primeira tela que o jogador vê.
func plural(n int, um, muitos string) string {
	if n == 1 {
		return um
	}
	return fmt.Sprintf(muitos, n)
}

// resumo corta a mensagem de erro no que cabe na janela. Erro de rede em Go
// traz a URL inteira e o endereço IP, que estouram a linha e não ajudam quem
// está lendo.
func resumo(err error) string {
	msg := err.Error()
	if i := strings.LastIndex(msg, ": "); i > 0 && len(msg) > 70 {
		msg = msg[i+2:]
	}
	if len(msg) > 70 {
		msg = msg[:70] + "…"
	}
	return msg
}

// jogar troca o Atualizador pelo jogo. O `Dir` é obrigatório: o cliente resolve
// `data\`, `System\` e o GRF a partir da pasta de trabalho, e um atalho lançado
// de outro lugar faz o jogo abrir sem nada do que é nosso.
func jogar(raiz, jogo string) error {
	caminho := filepath.Join(raiz, jogo)
	if _, err := os.Stat(caminho); err != nil {
		return fmt.Errorf("não encontrei %s", jogo)
	}
	cmd := exec.Command(caminho)
	cmd.Dir = raiz
	return cmd.Start()
}
