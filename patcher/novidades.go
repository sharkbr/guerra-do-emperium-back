// O changelog: o que mudou em cada patch, na janela do Atualizador e na área
// de transferência de quem vai anunciar no grupo.
//
// A `lista.txt` já tem um nome por patch, e é ele que aparece na barra de
// estado enquanto o patch é aplicado. Só que "Quarenta e sete itens nas lojas
// de Prontera" não diz QUAIS — e é justamente essa a pergunta de quem joga.
// Este arquivo é a segunda metade: um bloco por patch, com o título e, quando o
// patch acrescenta coisa, a lista do que entrou.
//
// Ele é opcional de propósito, nas duas pontas. Servidor sem `novidades.txt`
// (ou com um arquivo estragado) não tira o Atualizador do ar: o painel cai nos
// nomes da própria `lista.txt` e o jogador continua jogando. É a mesma regra do
// resto do programa — nada aqui pode impedir alguém de entrar.
package main

import (
	"fmt"
	"strconv"
	"strings"
	"syscall"
	"unsafe"
)

// O cabeçalho da mensagem que se cola no grupo. A data vem junto porque a
// mensagem é copiada patch a patch: colando três seguidas, é ela que diz qual é
// de qual dia.
const cabecalhoCopia = "LibraRO updates"

// novidade é o bloco de um patch. `Pontos` é o que ele acrescentou — os itens
// novos de uma loja, por exemplo — e fica vazio no patch que só conserta algo.
type novidade struct {
	Numero int
	Data   string // AAAA-MM-DD, como está no arquivo; pode vir vazia
	Titulo string
	Pontos []string
}

// baixaNovidades pega o changelog do servidor. Devolve do MAIS NOVO para o mais
// velho, que é a ordem em que o painel os mostra — o de cima é o que acabou de
// sair.
func baixaNovidades(url string) ([]novidade, error) {
	dados, err := baixaTexto(url + "novidades.txt")
	if err != nil {
		return nil, err
	}
	lista := leNovidades(dados)
	if len(lista) == 0 {
		return nil, fmt.Errorf("novidades.txt não tem bloco nenhum")
	}
	return lista, nil
}

// leNovidades lê o formato do `patcher/novidades.txt`:
//
//	[0021] 2026-09-06  Cinco chapéus novos
//	- Chapéu de Palha
//	- Tiara de Prata
//
// A leitura é TOLERANTE, ao contrário da `lista.txt` — e a diferença não é
// descuido. Lá, uma linha torta significa um patch que o jogador vai ou não vai
// receber, e parar é o certo; aqui o pior caso é um texto feio na tela. O
// arquivo também é editado à mão (corrigir a redação de um patch já publicado
// não deveria exigir um patch novo), e o que é editado à mão erra.
//
// Por isso: bloco sem data passa, linha solta dentro de um bloco vira ponto, e
// linha antes do primeiro `[` é ignorada — é onde mora o comentário do arquivo.
func leNovidades(texto string) []novidade {
	var lista []novidade
	var atual *novidade

	guarda := func() {
		if atual != nil {
			lista = append(lista, *atual)
		}
		atual = nil
	}

	for _, linha := range strings.Split(texto, "\n") {
		limpa := strings.TrimSpace(strings.TrimRight(linha, "\r"))
		if limpa == "" || strings.HasPrefix(limpa, "#") {
			continue
		}
		if strings.HasPrefix(limpa, "[") {
			guarda()
			if nova, ok := leCabecalhoNovidade(limpa); ok {
				atual = &nova
			}
			continue
		}
		if atual == nil {
			continue // texto solto antes do primeiro bloco
		}
		ponto := strings.TrimSpace(strings.TrimLeft(limpa, "-*"))
		if ponto != "" {
			atual.Pontos = append(atual.Pontos, ponto)
		}
	}
	guarda()

	// Do mais novo para o mais velho. O arquivo é escrito por acréscimo, em
	// ordem crescente de número, porque é assim que ele é lido por gente; o
	// painel quer o contrário.
	inverte(lista)
	return lista
}

// leCabecalhoNovidade lê `[0021] 2026-09-06  Título`. A data é opcional e o
// título não: bloco sem título não é bloco nenhum.
func leCabecalhoNovidade(linha string) (novidade, bool) {
	fim := strings.Index(linha, "]")
	if fim < 0 {
		return novidade{}, false
	}
	numero, err := strconv.Atoi(strings.TrimSpace(linha[1:fim]))
	if err != nil {
		return novidade{}, false
	}
	resto := strings.TrimSpace(linha[fim+1:])
	n := novidade{Numero: numero}
	if len(resto) >= 10 && resto[4] == '-' && resto[7] == '-' {
		if _, err := strconv.Atoi(strings.ReplaceAll(resto[:10], "-", "")); err == nil {
			n.Data, resto = resto[:10], strings.TrimSpace(resto[10:])
		}
	}
	n.Titulo = resto
	if n.Titulo == "" {
		return novidade{}, false
	}
	return n, true
}

// deLista é o painel sem `novidades.txt`: um bloco por patch, com o nome que a
// `lista.txt` já traz e sem pontos. Serve para o servidor que ainda não publicou
// o changelog — e para o dia em que o arquivo subir estragado.
func deLista(lista []patch) []novidade {
	var saida []novidade
	for _, p := range lista {
		saida = append(saida, novidade{Numero: p.Numero, Titulo: p.Nome})
	}
	inverte(saida)
	return saida
}

func inverte(lista []novidade) {
	for i, j := 0, len(lista)-1; i < j; i, j = i+1, j-1 {
		lista[i], lista[j] = lista[j], lista[i]
	}
}

// dataCurta é a data como o brasileiro a lê. Data ausente ou torta sai como
// está — inventar uma seria pior que não mostrar nenhuma.
func (n novidade) dataCurta() string {
	if len(n.Data) != 10 {
		return n.Data
	}
	return n.Data[8:10] + "/" + n.Data[5:7] + "/" + n.Data[0:4]
}

// mensagem é o que vai para a área de transferência — o texto pronto para o
// grupo. A data entra no cabeçalho, e não no fim, porque é assim que várias
// mensagens coladas em sequência continuam se distinguindo.
func (n novidade) mensagem() string {
	cabecalho := cabecalhoCopia
	if d := n.dataCurta(); d != "" {
		cabecalho += " " + d
	}
	linhas := []string{cabecalho, "", n.Titulo}
	for _, p := range n.Pontos {
		linhas = append(linhas, "- "+p)
	}
	return strings.Join(linhas, "\n")
}

// ---------------------------------------------------------------------------
// A área de transferência

var (
	pOpenClipboard    = user32.NewProc("OpenClipboard")
	pEmptyClipboard   = user32.NewProc("EmptyClipboard")
	pSetClipboardData = user32.NewProc("SetClipboardData")
	pCloseClipboard   = user32.NewProc("CloseClipboard")

	pGlobalAlloc  = kernel32.NewProc("GlobalAlloc")
	pGlobalLock   = kernel32.NewProc("GlobalLock")
	pGlobalUnlock = kernel32.NewProc("GlobalUnlock")
	pGlobalFree   = kernel32.NewProc("GlobalFree")
)

// copiaTexto põe o texto na área de transferência do Windows.
//
// Três coisas que não são óbvias e das quais o Windows não avisa:
//
//   - a memória é GMEM_MOVEABLE, e depois do `SetClipboardData` ela é DO
//     WINDOWS: liberá-la ali derrubaria quem colasse depois. Só se libera no
//     caminho de erro, que é o que este código faz;
//   - o formato é CF_UNICODETEXT, com o terminador NUL contado no tamanho — sem
//     ele, quem cola recebe lixo depois do texto;
//   - a quebra de linha tem de ser CRLF. Com LF puro o texto chega inteiro no
//     WhatsApp e numa linha só no Bloco de Notas, que é o tipo de defeito que só
//     aparece na máquina de outra pessoa.
func copiaTexto(hwnd uintptr, texto string) error {
	const (
		cfUnicodeText = 13
		moveavel      = 0x0002 | 0x0040 // GMEM_MOVEABLE|GMEM_ZEROINIT
	)
	letras := syscall.StringToUTF16(strings.ReplaceAll(texto, "\n", "\r\n"))

	mem, _, erro := pGlobalAlloc.Call(moveavel, uintptr(len(letras)*2))
	if mem == 0 {
		return fmt.Errorf("GlobalAlloc: %v", erro)
	}
	destino, _, erro := pGlobalLock.Call(mem)
	if destino == 0 {
		pGlobalFree.Call(mem)
		return fmt.Errorf("GlobalLock: %v", erro)
	}
	// O `go vet` recusa `unsafe.Pointer(destino)` — endereço que chega como
	// número é invisível para o coletor, e ele está certo na regra geral. Aqui a
	// memória é do Windows e ninguém a move; a leitura pelo ponteiro para a
	// variável local diz isso ao verificador sem apagar o aviso com comentário.
	inicio := *(*unsafe.Pointer)(unsafe.Pointer(&destino))
	copy(unsafe.Slice((*uint16)(inicio), len(letras)), letras)
	pGlobalUnlock.Call(mem)

	if ok, _, erro := pOpenClipboard.Call(hwnd); ok == 0 {
		pGlobalFree.Call(mem)
		return fmt.Errorf("OpenClipboard: %v", erro)
	}
	pEmptyClipboard.Call()
	if ok, _, erro := pSetClipboardData.Call(cfUnicodeText, mem); ok == 0 {
		pCloseClipboard.Call()
		pGlobalFree.Call(mem)
		return fmt.Errorf("SetClipboardData: %v", erro)
	}
	pCloseClipboard.Call()
	return nil
}
