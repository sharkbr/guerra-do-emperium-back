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
	"path/filepath"
	"strings"
	"time"
)

// VERSAO é o número que o canal de auto-atualização compara. Sobe de um a cada
// Atualizador novo publicado — ver auto.go e `patcher/LEIAME.md`.
const VERSAO = 5

// Os valores padrão existem para o caso de o `Atualizador.ini` não vir no
// pacote ou ser apagado: sem ini, o Atualizador ainda funciona na produção.
// São DOIS endereços, e a diferença não é arbitrária:
//
//	url    os patches — no nosso droplet, que já os serve e são pequenos
//	base   a instalação — num bucket com CDN, porque são 3,4 GB POR JOGADOR
//
// Servir a base do droplet mandaria 3,4 GB pela mesma placa de rede que atende
// o map-server, uma vez para cada pessoa que instala. O endereço da base é um
// subdomínio NOSSO (`cdn.filiponegrao.com.br`) e não o do provedor: ele fica
// congelado dentro do exe que o jogador baixou, e trocar de provedor um dia
// tem de ser mudar um CNAME, não republicar o instalador de todo mundo.
const (
	urlPadrao  = "https://libraro.filiponegrao.com.br/patch/"
	basePadrao = "https://cdn.filiponegrao.com.br/"
	jogoPadrao = "GuerraDoEmperium.exe"
)

// config é o `.ini` ao lado do exe. Formato chave=valor, uma por linha, `#`
// comenta. Não é INI de seção — a simplicidade aqui vale mais que a convenção,
// porque este arquivo pode acabar sendo editado por um jogador.
type config struct {
	url  string // de onde vêm os patches
	base string // de onde vem a instalação (só usado no primeiro download)
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
	c := config{url: urlPadrao, base: basePadrao, jogo: jogoPadrao}

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
		case "base":
			if valor != "" {
				c.base = valor
			}
		case "jogo":
			if valor != "" {
				c.jogo = valor
			}
		}
	}
	// A barra final é obrigatória porque os dois endereços são concatenados
	// direto com o nome do arquivo. Esquecê-la no .ini daria uma URL como
	// `…/patchlista.txt`, e o 404 resultante mandaria procurar o arquivo no
	// servidor — onde ele está, com o nome certo.
	if !strings.HasSuffix(c.url, "/") {
		c.url += "/"
	}
	if !strings.HasSuffix(c.base, "/") {
		c.base += "/"
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

	// O mesmo exe é o instalador e o atualizador, e quem decide é a pasta em
	// que ele está. Sem cliente ao lado, ele é o primeiro download de alguém
	// que acabou de baixar 9 MB e não tem mais nada. "Cliente ao lado" são o
	// `data.grf` E o exe do jogo — pasta com um só dos dois é instalação
	// alheia ou pela metade, e cai no instalador (ver `PrecisaInstalar`).
	if PrecisaInstalar(raiz, cfg.jogo) {
		instalacao(exe, cfg)
		return
	}

	// A pasta de trabalho do Atualizador: estado, downloads e a cópia velha de
	// si mesmo. Fica dentro do cliente para o jogador poder apagar a pasta
	// inteira do jogo e não deixar rastro em lugar nenhum do sistema.
	trabalho := filepath.Join(raiz, "patch")
	os.MkdirAll(trabalho, 0o755)
	abreRegistro(trabalho)
	limpaVelho(trabalho, exe)

	j := Abre("Guerra do Emperium")
	j.Jogar = func() error { return jogar(raiz, cfg.jogo) }
	go carregaNovidades(j, cfg)
	go trabalha(j, raiz, trabalho, cfg)
	j.Laco()
}

// instalacao é a primeira abertura: a janela pergunta onde instalar, e só
// então baixa. Perguntar antes é o que separa isto de um programa que despeja
// 3,4 GB no disco de alguém sem avisar.
func instalacao(exe string, cfg config) {
	j := Abre("Guerra do Emperium")
	j.Pergunta(destinoPadrao, true)

	// O changelog não espera a instalação: quem está escolhendo a pasta tem 3,4
	// GB pela frente e nada para ler enquanto isso.
	go carregaNovidades(j, cfg)

	// A raiz final só existe depois que o jogador confirma, e o botão JOGAR
	// precisa dela quando aparecer no fim. As duas atribuições acontecem na
	// thread da janela — a de baixo no clique, a de cima quando o botão é
	// usado —, então não há corrida entre elas.
	var raiz string
	j.Jogar = func() error { return jogar(raiz, cfg.jogo) }

	j.Instalar = func(destino string, atalho bool) {
		raiz = destino
		go func() {
			defer recuperaPanico(j)

			// O registro só pode ser aberto depois de a pasta existir, e ela é
			// escolhida agora — por isso ele não está no começo, como no outro
			// caminho.
			trabalho := filepath.Join(destino, "patch")
			os.MkdirAll(trabalho, 0o755)
			abreRegistro(trabalho)

			if err := Instala(j, destino, cfg, atalho, exe); err != nil {
				anota("instalação: %v", err)
				// O botão NÃO é liberado aqui: sem cliente em disco não há o
				// que jogar, e um JOGAR aceso depois de uma instalação que
				// falhou só levaria a um segundo erro, mais confuso que o
				// primeiro. É a única tela do programa em que isso vale.
				j.Status("Não consegui instalar: " + resumo(err))
				return
			}

			// Instalado. Daqui para a frente é uma rodada normal de patches —
			// os que foram publicados desde que o pacote da base foi montado.
			// A auto-atualização é pulada de propósito: o exe que acabou de se
			// copiar para a pasta é este, e trocá-lo agora seria substituir um
			// arquivo recém-gravado pela mesma versão.
			aplicaPatches(j, destino, trabalho, cfg)
		}()
	}
	j.Laco()
}

// trabalha é a rodada inteira, numa goroutine — a janela precisa da thread
// principal para o laço de mensagens, senão ela congela enquanto baixa.
func trabalha(j *Janela, raiz, trabalho string, cfg config) {
	defer recuperaPanico(j)

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

	aplicaPatches(j, raiz, trabalho, cfg)
}

// carregaNovidades põe o changelog no painel da janela. Roda em goroutine
// própria e à parte do trabalho: ele não decide nada — nem o que se baixa, nem
// se o botão acende —, e por isso não pode segurar a rodada. Falhar aqui deixa
// o painel escondido e mais nada.
func carregaNovidades(j *Janela, cfg config) {
	lista, err := baixaNovidades(cfg.url)
	if err != nil {
		anota("novidades: %v", err)
		return
	}
	j.Novidades(lista)
}

// recuperaPanico existe porque pânico numa goroutine de trabalho viraria uma
// janela morta, sem explicação nenhuma na tela. O jogador merece o botão Jogar
// mesmo quando o Atualizador se atrapalha.
func recuperaPanico(j *Janela) {
	if r := recover(); r != nil {
		anota("pânico: %v", r)
		j.Status(fmt.Sprintf("Falha no atualizador: %v", r))
		j.Libera()
	}
}

// aplicaPatches é a rodada de patches, separada do `trabalha` porque a
// instalação a reusa sem passar pela auto-atualização.
func aplicaPatches(j *Janela, raiz, trabalho string, cfg config) {
	lista, err := baixaLista(cfg.url)
	if err != nil {
		// Sem "sem conexão": pode ser a lista ausente, o servidor em manutenção
		// ou a internet do jogador. Dizer qual das três é o que o log faz.
		anota("lista: %v", err)
		j.Status("Não consegui conferir as atualizações. Você pode jogar assim mesmo.")
		j.Libera()
		return
	}

	// O painel sem `novidades.txt`: os nomes que a própria lista traz. Só entra
	// se o changelog de verdade não tiver chegado — as duas vias correm em
	// goroutines diferentes, e a boa, quando vem, vem por cima.
	if j.SemNovidades() {
		j.Novidades(deLista(lista))
	}

	// Um patch só conta como aplicado quando o NÚMERO e o SHA batem. O número
	// sozinho não identifica nada — ver `leAplicados`, que conta o caso vivo.
	aplicados := leAplicados(trabalho)
	var faltam []patch
	for _, p := range lista {
		if aplicados[p.Numero] != p.SHA {
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
		// O registro é DESTE laço, e não do `aplica` — o instalador chama a
		// mesma função e não tem o que anotar aqui. Anotar depois de extrair
		// erra para o lado certo: falha ao gravar faz o próximo início
		// reaplicar, o que é barato (o patch é idempotente por construção).
		if err := marcaAplicado(trabalho, p); err != nil {
			anota("marcaAplicado %04d: %v", p.Numero, err)
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

// jogar troca o Atualizador pelo jogo.
//
// O diretório é obrigatório: o cliente resolve `data\`, `System\` e o GRF a
// partir da pasta de trabalho, e um jogo lançado de outro lugar abre sem nada
// do que é nosso.
//
// Vai pelo `ShellExecuteW` e não por `exec.Command` porque o cliente pede
// elevação — ver o cabeçalho do `executa.go`.
func jogar(raiz, jogo string) error {
	return Executa(filepath.Join(raiz, jogo), raiz)
}
