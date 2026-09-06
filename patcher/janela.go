// A janela, em Win32 puro — no formato do patcher clássico de Ragnarok.
//
// A v1 era uma janela do Windows com controles nativos dentro: funcionava e
// parecia um utilitário. Esta é desenhada inteira por nós, seguindo o que o
// jogador de RO reconhece do patcher do bRO — moldura própria em vez da barra
// do Windows, arte ocupando quase tudo, e um rodapé com o estado no meio, a
// barra de progresso larga e o JOGAR grande à direita.
//
// Sem biblioteca de interface e sem controle nativo: são ~600 linhas de
// `syscall` contra user32 e gdi32. Em troca, o binário não depende de nada que
// não seja Windows, e o visual não muda com o tema de quem está jogando — o que
// para uma janela temática é o ponto todo.
//
// Quatro decisões que não são óbvias:
//
//   - **Tudo é desenhado num bitmap de memória e copiado de uma vez.** Com o
//     progresso repintando a cada 100 ms, desenhar direto no DC da janela faria
//     a arte piscar. O buffer é criado uma vez e reusado.
//   - **A arte é reduzida em Go e entra por `CreateDIBSection`.** O
//     `StretchDIBits` falha de forma intermitente nesta máquina (`CLAUDE.md`
//     §5) — com e sem HALFTONE, com e sem escala —, e uma janela que às vezes
//     nasce preta é pior que uma imagem levemente pior.
//   - **A janela não tem barra de título do Windows** (`WS_POPUP`). Quem faz
//     ela ser arrastável é o `WM_NCHITTEST` devolvendo `HTCAPTION` na faixa de
//     cima — e `HTCLIENT` nos dois botões, senão o clique vira arrasto e eles
//     nunca recebem `WM_LBUTTONDOWN`.
//   - **Os gradientes são desenhados linha a linha.** O `GradientFill` mora na
//     `msimg32.dll`, e uma DLL a mais para pintar 56 linhas não se paga.
package main

import (
	"bytes"
	_ "embed"
	"fmt"
	"image"
	"image/draw"
	_ "image/jpeg"
	"runtime"
	"strings"
	"sync"
	"syscall"
	"time"
	"unsafe"
)

//go:embed recursos/fundo.jpg
var fundoJPEG []byte

// O layout, em pixels.
//
// A altura total (674) é escolhida contra a tela do jogador, não contra a arte:
// em 1366x768 — que ainda é comum — sobram ~728 px depois da barra de tarefas,
// e uma janela que nasce cortada embaixo esconde justamente o botão JOGAR.
//
// A arte é 1280x1024 (proporção 1,25) e a moldura é 1,43, então ela entra
// COBRINDO e sobra nas pontas: o recorte tira faixas iguais de cima e de baixo
// (ver `cobre`). É de propósito — esticar deformaria o cavaleiro, e deixar
// tarja preta em cima e embaixo mataria o efeito de janela temática.
const (
	larguraJanela = 760
	alturaBarra   = 34
	alturaArte    = 532
	alturaRodape  = 108
	alturaJanela  = alturaBarra + alturaArte + alturaRodape
)

// As mensagens que a goroutine de trabalho manda para a janela. WM_APP é a
// primeira faixa que o Windows reserva para o programa.
const (
	wmStatus    = 0x8000 + 1
	wmProgresso = 0x8000 + 2
	wmLibera    = 0x8000 + 3
	wmFecha     = 0x8000 + 4
	wmNovidades = 0x8000 + 5
)

var (
	user32   = syscall.NewLazyDLL("user32.dll")
	gdi32    = syscall.NewLazyDLL("gdi32.dll")
	kernel32 = syscall.NewLazyDLL("kernel32.dll")

	pRegisterClassExW   = user32.NewProc("RegisterClassExW")
	pCreateWindowExW    = user32.NewProc("CreateWindowExW")
	pDefWindowProcW     = user32.NewProc("DefWindowProcW")
	pShowWindow         = user32.NewProc("ShowWindow")
	pUpdateWindow       = user32.NewProc("UpdateWindow")
	pGetMessageW        = user32.NewProc("GetMessageW")
	pTranslateMessage   = user32.NewProc("TranslateMessage")
	pDispatchMessageW   = user32.NewProc("DispatchMessageW")
	pPostQuitMessage    = user32.NewProc("PostQuitMessage")
	pPostMessageW       = user32.NewProc("PostMessageW")
	pBeginPaint         = user32.NewProc("BeginPaint")
	pEndPaint           = user32.NewProc("EndPaint")
	pFillRect           = user32.NewProc("FillRect")
	pDrawTextW          = user32.NewProc("DrawTextW")
	pInvalidateRect     = user32.NewProc("InvalidateRect")
	pDestroyWindow      = user32.NewProc("DestroyWindow")
	pGetSystemMetrics   = user32.NewProc("GetSystemMetrics")
	pSetProcessDPIAware = user32.NewProc("SetProcessDPIAware")
	pLoadCursorW        = user32.NewProc("LoadCursorW")
	pLoadIconW          = user32.NewProc("LoadIconW")
	pSetCursor          = user32.NewProc("SetCursor")
	pGetDC              = user32.NewProc("GetDC")
	pReleaseDC          = user32.NewProc("ReleaseDC")
	pTrackMouseEvent    = user32.NewProc("TrackMouseEvent")
	pSetCapture         = user32.NewProc("SetCapture")
	pReleaseCapture     = user32.NewProc("ReleaseCapture")

	pCreateFontW            = gdi32.NewProc("CreateFontW")
	pCreateSolidBrush       = gdi32.NewProc("CreateSolidBrush")
	pCreateCompatibleDC     = gdi32.NewProc("CreateCompatibleDC")
	pCreateCompatibleBitmap = gdi32.NewProc("CreateCompatibleBitmap")
	pSelectObject           = gdi32.NewProc("SelectObject")
	pDeleteObject           = gdi32.NewProc("DeleteObject")
	pCreateDIBSection       = gdi32.NewProc("CreateDIBSection")
	pBitBlt                 = gdi32.NewProc("BitBlt")
	pSetBkMode              = gdi32.NewProc("SetBkMode")
	pSetTextColor           = gdi32.NewProc("SetTextColor")
	pGetTextExtentPoint32W  = gdi32.NewProc("GetTextExtentPoint32W")
	pSaveDC                 = gdi32.NewProc("SaveDC")
	pRestoreDC              = gdi32.NewProc("RestoreDC")
	pIntersectClipRect      = gdi32.NewProc("IntersectClipRect")

	pGetModuleHandleW = kernel32.NewProc("GetModuleHandleW")
)

// A paleta. Escura e dourada de propósito: a arte é de guerra, e o cinza do
// Windows no meio dela denunciava o utilitário.
var (
	corFundo    = rgb(23, 18, 14)    // pedra escura — barra e rodapé
	corLinha    = rgb(90, 72, 38)    // o fio dourado que separa as faixas
	corDourado  = rgb(200, 162, 74)  // títulos e molduras
	corBrilho   = rgb(240, 216, 144) // o topo do gradiente da barra
	corTexto    = rgb(232, 220, 192) // creme, para o estado
	corApagado  = rgb(122, 106, 80)  // o crédito lá embaixo
	corSelo     = rgb(176, 156, 116) // o número e a data de cada novidade
	corTrilho   = rgb(14, 11, 8)     // o fundo da barra de progresso
	corVerde    = rgb(38, 105, 66)   // o verde do Emperium, base do botão
	corVerdeAlt = rgb(72, 168, 106)  // o mesmo verde, aceso — topo e hover
)

// As áreas clicáveis e desenháveis. Ficam juntas aqui porque layout espalhado
// pelo código é o que faz uma janela desenhada à mão ficar impossível de mexer.
var (
	areaBarra    = rect{0, 0, larguraJanela, alturaBarra}
	areaArte     = rect{0, alturaBarra, larguraJanela, alturaBarra + alturaArte}
	areaRodape   = rect{0, alturaBarra + alturaArte, larguraJanela, alturaJanela}
	areaFechar   = rect{larguraJanela - 42, 0, larguraJanela - 4, alturaBarra}
	areaMinimiza = rect{larguraJanela - 84, 0, larguraJanela - 46, alturaBarra}
	areaJogar    = rect{larguraJanela - 208, alturaBarra + alturaArte + 22,
		larguraJanela - 24, alturaBarra + alturaArte + 82}
	areaBarraProg = rect{24, alturaBarra + alturaArte + 58, larguraJanela - 232,
		alturaBarra + alturaArte + 80}
	areaStatus = rect{24, alturaBarra + alturaArte + 16, larguraJanela - 232,
		alturaBarra + alturaArte + 50}
	areaCredito = rect{24, alturaJanela - 26, larguraJanela - 24, alturaJanela - 6}

	// Só existem no modo instalação, e ocupam o lugar do estado e da barra de
	// progresso — que naquele momento não têm o que mostrar. Terminada a
	// pergunta, o rodapé volta a ser o de sempre.
	areaPasta  = rect{24, alturaBarra + alturaArte + 14, larguraJanela - 336, alturaBarra + alturaArte + 42}
	areaMudar  = rect{larguraJanela - 330, alturaBarra + alturaArte + 14, larguraJanela - 232, alturaBarra + alturaArte + 42}
	areaAtalho = rect{24, alturaBarra + alturaArte + 50, 24 + 330, alturaBarra + alturaArte + 78}
	// O quadradinho do checkbox, dentro da área clicável — que é maior de
	// propósito: acertar 16 pixels com o mouse é pior que ler o rótulo inteiro
	// como parte do botão.
	areaMarca = rect{26, alturaBarra + alturaArte + 56, 26 + 16, alturaBarra + alturaArte + 72}
)

// O painel de novidades, encostado na direita e por cima da arte — o lugar em
// que o jogador de RO procura o aviso do servidor, e a coluna que cabe mais
// linha sem tapar o cavaleiro.
//
// A largura é a medida que manda: 330 px dão umas 40 letras por linha na fonte
// de 12, que é o suficiente para "Chapéu de Bruxa Ancestral" não quebrar. O
// resto do layout (título da célula, pontos, botão de copiar) é calculado a
// partir dela em `montaNovidades`.
const (
	larguraNov   = 330
	margemNov    = 18
	recuoNov     = 14 // o respiro entre a moldura e o texto
	alturaCabNov = 32

	// A opacidade do fundo do painel, em porcentagem. Em 100 ele é uma tapadeira
	// e a arte some atrás dele; em 65 a cidade em chamas continua aparecendo por
	// baixo do texto, que foi o que o dono pediu em 2026-09-06. Abaixo disso o
	// dourado do título começa a disputar com o laranja do fundo.
	opacidadeNov = 65
)

var (
	areaNovidades = rect{larguraJanela - margemNov - larguraNov, alturaBarra + margemNov,
		larguraJanela - margemNov, alturaBarra + alturaArte - margemNov}
	areaNovCab = rect{areaNovidades.esquerda, areaNovidades.topo,
		areaNovidades.direita, areaNovidades.topo + alturaCabNov}
	areaNovLista = rect{areaNovidades.esquerda + 1, areaNovCab.base,
		areaNovidades.direita - 1, areaNovidades.base - 1}
	areaTrilhoNov = rect{areaNovLista.direita - 11, areaNovLista.topo + 6,
		areaNovLista.direita - 5, areaNovLista.base - 6}

	// A largura útil de texto: da margem esquerda até onde a barra de rolagem
	// começa. Ela é a mesma com e sem barra visível, de propósito — senão o
	// texto se requebraria sozinho ao passar de uma tela de altura.
	larguraTextoNov = areaTrilhoNov.esquerda - 8 - (areaNovLista.esquerda + recuoNov)
)

// linhaNov é uma linha já quebrada e medida, em coordenadas do CONTEÚDO do
// painel: y=0 é o topo do texto, e a rolagem só entra na hora de desenhar.
type linhaNov struct {
	texto  string
	x, y   int32
	altura int32
	fonte  uintptr
	cor    uintptr
}

// celulaNov é o bloco de um patch dentro do painel — o que o ponteiro realça e
// o que o botão de copiar leva para a área de transferência. A `mensagem` fica
// pronta aqui porque o clique não é hora de montar texto.
type celulaNov struct {
	topo, base int32
	botao      rect // o "copiar", também em coordenadas de conteúdo
	mensagem   string
}

type rect struct{ esquerda, topo, direita, base int32 }

func (r rect) contem(x, y int32) bool {
	return x >= r.esquerda && x < r.direita && y >= r.topo && y < r.base
}

type wndClassExW struct {
	tamanho      uint32
	estilo       uint32
	proc         uintptr
	extraClass   int32
	extraJanela  int32
	instancia    uintptr
	icone        uintptr
	cursor       uintptr
	fundo        uintptr
	menu         *uint16
	classe       *uint16
	iconePequeno uintptr
}

type mensagem struct {
	hwnd   uintptr
	valor  uint32
	wParam uintptr
	lParam uintptr
	tempo  uint32
	ponto  struct{ x, y int32 }
}

type paintStruct struct {
	hdc        uintptr
	apagar     int32
	area       rect
	restaurar  int32
	incompleto int32
	reservado  [32]byte
}

type bitmapInfoHeader struct {
	tamanho                 uint32
	largura                 int32
	altura                  int32
	planos                  uint16
	bits                    uint16
	compressao              uint32
	tamanhoImagem           uint32
	xPPM, yPPM              int32
	cores, coresImportantes uint32
}

type trackMouse struct {
	tamanho   uint32
	bandeiras uint32
	hwnd      uintptr
	tempo     uint32
}

func rgb(r, g, b uint32) uintptr { return uintptr(r | g<<8 | b<<16) }

func utf16(s string) *uint16 {
	p, err := syscall.UTF16PtrFromString(s)
	if err != nil {
		p, _ = syscall.UTF16PtrFromString("?")
	}
	return p
}

// Janela é a janela do Atualizador. Os métodos que a goroutine de trabalho usa
// (Status, Progresso, Libera, Fecha) só guardam o valor e acordam a janela —
// desenhar de outra thread é o caminho curto para uma interface que trava.
type Janela struct {
	hwnd        uintptr
	fonte       uintptr // o estado, no rodapé
	fonteTit    uintptr // o nome do servidor, na moldura
	fonteBot    uintptr // o JOGAR
	fonteMin    uintptr // o crédito, a data e o botão de copiar
	fonteNovTit uintptr // o título de cada novidade
	fonteNov    uintptr // os pontos de cada novidade
	arte        uintptr
	arteDC      uintptr
	buffer      uintptr
	bufferDC    uintptr

	// O fundo do painel de novidades e o da célula realçada, os dois já
	// MISTURADOS com a arte que fica atrás deles (ver `misturaComArte`). São
	// bitmaps prontos porque a arte não muda: a mistura acontece uma vez, no
	// carregamento, e o desenho vira uma cópia de retângulo.
	fundoNovDC  uintptr
	realceNovDC uintptr

	// Jogar é chamado quando o botão é clicado. Devolver erro mantém a janela
	// aberta com a mensagem na tela — é o que acontece se o exe do jogo sumir.
	Jogar func() error

	// Instalar é chamado no lugar do Jogar enquanto a janela está no modo
	// pergunta. Recebe o que o jogador escolheu; não devolve erro porque o
	// trabalho segue numa goroutine e o que der errado aparece no estado.
	Instalar func(destino string, atalho bool)

	mu     sync.Mutex
	texto  string
	pct    int
	pronto bool
	sobre  int // 0 nenhum, 1 botão principal, 2 minimizar, 3 fechar, 4 mudar, 5 atalho

	// O modo instalação. `pergunta` liga a tela de escolha; os outros dois são
	// o que ela coleta. Ficam sob o mesmo mutex do resto porque são lidos pelo
	// WM_PAINT, que roda na thread da janela, e escritos pelo clique.
	pergunta bool
	destino  string
	atalho   bool

	// O painel de novidades. `novidades` é o que veio do servidor; as duas
	// listas abaixo são o layout já medido, refeito só quando o conteúdo muda
	// (`linhasNov == nil` é o pedido de refazer). Medir texto exige um DC, e o
	// único lugar do programa que tem um é o WM_PAINT — por isso o layout nasce
	// lá, e não aqui.
	novidades   []novidade
	linhasNov   []linhaNov
	celulasNov  []celulaNov
	alturaNov   int32 // a altura de todo o conteúdo, para a barra de rolagem
	rolagem     int32
	celulaSobre int  // a célula sob o ponteiro, ou -1
	copiada     int  // a célula com o "copiado!" aceso, ou -1
	arrastando  bool // o polegar da rolagem está preso ao ponteiro
	agarrou     int32
}

// Pergunta põe a janela no modo instalação, com a pasta sugerida e o atalho já
// marcado. Chamada antes do `Laco()`, da mesma thread.
func (j *Janela) Pergunta(destino string, atalho bool) {
	j.mu.Lock()
	j.pergunta, j.destino, j.atalho = true, destino, atalho
	j.texto = ""
	j.mu.Unlock()
}

// Escolhas devolve o que o jogador marcou.
func (j *Janela) Escolhas() (string, bool) {
	j.mu.Lock()
	defer j.mu.Unlock()
	return j.destino, j.atalho
}

// noModoPergunta responde se a tela de escolha está no ar.
func (j *Janela) noModoPergunta() bool {
	j.mu.Lock()
	defer j.mu.Unlock()
	return j.pergunta
}

// botaoAceso diz se o botão principal aceita clique. No modo pergunta ele está
// sempre aceso — o que ele começa é a instalação, e não há nada a esperar.
func (j *Janela) botaoAceso() bool {
	j.mu.Lock()
	defer j.mu.Unlock()
	return j.pergunta || j.pronto
}

var jan *Janela

// O nome da classe é global porque o Windows guarda o ponteiro enquanto a
// classe existir; um ponteiro para variável local do Go poderia ser recolhido.
var nomeClasse = utf16("GuerraAtualizador")

// Abre cria a janela e a mostra. Tem de ser chamada da goroutine principal: o
// laço de mensagens exige a mesma thread do sistema até o fim.
func Abre(titulo string) *Janela {
	runtime.LockOSThread()
	pSetProcessDPIAware.Call() // sem isto a janela sai borrada em tela 4K

	instancia, _, _ := pGetModuleHandleW.Call(0)
	j := &Janela{texto: "Iniciando…", celulaSobre: -1, copiada: -1}
	jan = j

	// A arte é preparada ANTES de a janela existir. Decodificar o JPEG leva uns
	// 100 ms, e um WM_PAINT que chegue nesse intervalo pinta o retângulo vazio.
	j.preparaArte()

	cursor, _, _ := pLoadCursorW.Call(0, 32512) // IDC_ARROW

	// O ícone vem do recurso embutido pelo `icone_windows_amd64.syso`, e o `1`
	// é o id do grupo que o `go run ./icone` escreve. Ter o recurso no exe faz
	// o Explorer desenhar o ícone do arquivo; para ele aparecer na BARRA DE
	// TAREFAS e no Alt+Tab é preciso pô-lo na classe da janela — são duas
	// coisas separadas, e é comum acertar a primeira e achar que a segunda veio
	// junto.
	icone, _, _ := pLoadIconW.Call(instancia, 1)
	if icone == 0 {
		anota("icone: LoadIconW devolveu 0 — o exe foi compilado sem o .syso?")
	}

	wc := wndClassExW{
		tamanho:      uint32(unsafe.Sizeof(wndClassExW{})),
		proc:         syscall.NewCallback(processa),
		instancia:    instancia,
		cursor:       cursor,
		classe:       nomeClasse,
		icone:        icone,
		iconePequeno: icone,
	}
	pRegisterClassExW.Call(uintptr(unsafe.Pointer(&wc)))

	// WS_POPUP: nenhuma moldura do Windows — a barra de cima é nossa. O
	// WS_MINIMIZEBOX e o WS_SYSMENU não aparecem, mas são o que faz o botão de
	// minimizar e a barra de tarefas funcionarem; o WS_EX_APPWINDOW é o que
	// garante o ícone lá embaixo mesmo sem moldura.
	const estilo = 0x80000000 | 0x00020000 | 0x00080000 // POPUP|MINIMIZEBOX|SYSMENU
	const estiloEx = 0x00040000                         // WS_EX_APPWINDOW
	telaX, _, _ := pGetSystemMetrics.Call(0)
	telaY, _, _ := pGetSystemMetrics.Call(1)
	x := (int32(telaX) - larguraJanela) / 2
	y := (int32(telaY) - alturaJanela) / 2

	j.hwnd, _, _ = pCreateWindowExW.Call(estiloEx,
		uintptr(unsafe.Pointer(nomeClasse)),
		uintptr(unsafe.Pointer(utf16(titulo))),
		estilo, uintptr(x), uintptr(y), larguraJanela, alturaJanela,
		0, 0, instancia, 0)

	// Altura negativa é altura do caractere, não da célula; 1 é DEFAULT_CHARSET,
	// que é o que faz o acento sair certo — a janela desenha com API Unicode,
	// então nada aqui é cp1252. Georgia por ser serifada e existir em todo
	// Windows: é o que dá o ar antigo sem depender de fonte instalada.
	j.fonte = criaFonte(-15, 400, "Segoe UI")
	j.fonteTit = criaFonte(-16, 700, "Georgia")
	j.fonteBot = criaFonte(-26, 700, "Georgia")
	j.fonteMin = criaFonte(-11, 400, "Segoe UI")
	j.fonteNovTit = criaFonte(-14, 700, "Segoe UI")
	j.fonteNov = criaFonte(-12, 400, "Segoe UI")

	pShowWindow.Call(j.hwnd, 5) // SW_SHOW
	pUpdateWindow.Call(j.hwnd)
	return j
}

func criaFonte(altura, peso int, face string) uintptr {
	f, _, _ := pCreateFontW.Call(uintptr(altura), 0, 0, 0, uintptr(peso), 0, 0, 0,
		1, 0, 0, 5, 0, uintptr(unsafe.Pointer(utf16(face))))
	return f
}

// preparaArte decodifica o JPEG embutido, reduz no tamanho da janela e guarda
// o resultado num bitmap de memória. Falhar aqui não é fatal: sem arte a janela
// fica escura, e o jogador ainda joga.
func (j *Janela) preparaArte() {
	img, _, err := image.Decode(bytes.NewReader(fundoJPEG))
	if err != nil {
		anota("arte: decode falhou: %v", err)
		return
	}
	origem := image.NewRGBA(img.Bounds())
	draw.Draw(origem, img.Bounds(), img, img.Bounds().Min, draw.Src)
	pixels := reduz(origem, cobre(img.Bounds(), larguraJanela, alturaArte),
		larguraJanela, alturaArte)

	j.arte, j.arteDC = criaBitmap(pixels, larguraJanela, alturaArte)
	if j.arteDC == 0 {
		return
	}

	// Os fundos do painel saem daqui, e não do WM_PAINT, porque precisam DESTES
	// pixels: é a arte já reduzida no tamanho da janela, que só existe neste
	// ponto do programa.
	j.preparaFundosDoPainel(pixels)
}

// criaBitmap põe os pixels (BGRA, de cima para baixo) num bitmap de memória e
// devolve o bitmap e um DC com ele selecionado. Devolve 0,0 se falhar — sem
// arte a janela fica escura, e o jogador ainda joga.
//
// É CreateDIBSection com cópia direta na memória que o Windows devolve: não há
// conversão de formato, não há escala, não há chamada que possa falhar por
// motivo obscuro.
//
// A alternativa natural — `StretchDIBits` — foi tentada primeiro e falha de
// forma intermitente nesta máquina: devolve 0 (erro) com `GetLastError` dizendo
// "operação concluída com êxito", umas vezes sim e outras não, no mesmo
// binário. Com HALFTONE, sem HALFTONE, com escala e sem escala. O sintoma é a
// janela nascer com o retângulo da arte preto, e nada além do log dizer o que
// houve. Ver `CLAUDE.md` §5.
func criaBitmap(pixels []byte, largura, altura int32) (uintptr, uintptr) {
	// Altura negativa: os nossos pixels vão de cima para baixo, e o padrão do
	// Windows é o contrário.
	cabecalho := bitmapInfoHeader{
		tamanho: uint32(unsafe.Sizeof(bitmapInfoHeader{})),
		largura: largura, altura: -altura,
		planos: 1, bits: 32,
	}

	tela, _, _ := pGetDC.Call(0)
	defer pReleaseDC.Call(0, tela)

	// `bits` é declarado como unsafe.Pointer e não como uintptr de propósito: o
	// `go vet` recusa converter uintptr de volta em ponteiro ("possible misuse
	// of unsafe.Pointer"), e ele está certo — endereço guardado como número é
	// invisível para o GC. Aqui a memória é do Windows, mas manter o tipo certo
	// é de graça e cala o aviso pelo motivo certo.
	var bits unsafe.Pointer
	bmp, _, erroGDI := pCreateDIBSection.Call(tela,
		uintptr(unsafe.Pointer(&cabecalho)), 0, // DIB_RGB_COLORS
		uintptr(unsafe.Pointer(&bits)), 0, 0)
	if bmp == 0 || bits == nil {
		anota("bitmap %dx%d: CreateDIBSection falhou (%v)", largura, altura, erroGDI)
		return 0, 0
	}
	copy(unsafe.Slice((*byte)(bits), len(pixels)), pixels)

	dc, _, _ := pCreateCompatibleDC.Call(tela)
	pSelectObject.Call(dc, bmp)
	return bmp, dc
}

// preparaFundosDoPainel mistura a cor do painel com a arte que fica atrás dele
// e guarda o resultado em dois bitmaps: o fundo normal e o da célula realçada.
//
// É assim que o painel fica translúcido SEM a `msimg32.dll` (onde moram o
// `AlphaBlend` e o `GradientFill`): a arte é fixa e o painel não sai do lugar,
// então a mistura de cada pixel é sempre a mesma conta — fazê-la a cada
// WM_PAINT seria repetir 160 mil multiplicações por quadro para chegar ao mesmo
// bitmap.
func (j *Janela) preparaFundosDoPainel(arte []byte) {
	j.fundoNovDC = misturaComArte(arte, corFundo, opacidadeNov)
	// A célula sob o ponteiro é a mesma mistura com uma cor um pouco mais
	// clara. Fosse um retângulo opaco por cima, o realce apagaria a arte
	// justamente na parte do painel que se está olhando.
	j.realceNovDC = misturaComArte(arte, rgb(58, 47, 32), opacidadeNov)
}

// misturaComArte devolve um DC do tamanho do painel, pintado com `cor` sobre a
// arte na opacidade dada (em porcentagem: 100 é cor pura, 0 é só arte).
func misturaComArte(arte []byte, cor uintptr, opacidade int) uintptr {
	largura := int(areaNovidades.direita - areaNovidades.esquerda)
	altura := int(areaNovidades.base - areaNovidades.topo)
	if len(arte) < larguraJanela*alturaArte*4 {
		return 0 // sem arte não há o que misturar; o painel cai na cor cheia
	}

	// A ordem é BGRA, e a `cor` vem do `rgb()`, que empacota ao contrário — daí
	// o vermelho sair do byte baixo e ir para o terceiro.
	r := int(cor & 0xFF)
	g := int((cor >> 8) & 0xFF)
	b := int((cor >> 16) & 0xFF)
	mistura := func(fundo byte, frente int) byte {
		return byte((int(fundo)*(100-opacidade) + frente*opacidade) / 100)
	}

	pixels := make([]byte, largura*altura*4)
	for y := 0; y < altura; y++ {
		// A arte é desenhada abaixo da barra de cima, então a linha do painel
		// na janela não é a mesma linha dentro do bitmap da arte.
		naArte := ((y+int(areaNovidades.topo)-alturaBarra)*larguraJanela +
			int(areaNovidades.esquerda)) * 4
		naLinha := y * largura * 4
		for x := 0; x < largura; x++ {
			i, k := naLinha+x*4, naArte+x*4
			pixels[i] = mistura(arte[k], b)
			pixels[i+1] = mistura(arte[k+1], g)
			pixels[i+2] = mistura(arte[k+2], r)
		}
	}
	_, dc := criaBitmap(pixels, int32(largura), int32(altura))
	return dc
}

// cobre devolve o maior retângulo da imagem que tem a proporção do destino,
// centralizado — o "cover" do CSS. A arte preenche a moldura inteira e o que
// sobra na dimensão folgada é cortado igualmente dos dois lados.
func cobre(limites image.Rectangle, largura, altura int) image.Rectangle {
	if limites.Dx()*altura > limites.Dy()*largura {
		// origem mais larga que o destino: corta nas laterais
		w := limites.Dy() * largura / altura
		sobra := (limites.Dx() - w) / 2
		return image.Rect(limites.Min.X+sobra, limites.Min.Y,
			limites.Min.X+sobra+w, limites.Max.Y)
	}
	h := limites.Dx() * altura / largura
	sobra := (limites.Dy() - h) / 2
	return image.Rect(limites.Min.X, limites.Min.Y+sobra,
		limites.Max.X, limites.Min.Y+sobra+h)
}

// reduz faz a média dos pixels de origem que caem em cada pixel de destino, e
// devolve BGRA — a ordem que o Windows espera num DIB de 32 bits. Média de
// caixa porque a redução é grande: amostrar o pixel do meio serrilharia a arte.
func reduz(origem *image.RGBA, limites image.Rectangle, largura, altura int) []byte {
	destino := make([]byte, largura*altura*4)
	for y := 0; y < altura; y++ {
		y0 := limites.Min.Y + y*limites.Dy()/altura
		y1 := limites.Min.Y + (y+1)*limites.Dy()/altura
		if y1 <= y0 {
			y1 = y0 + 1
		}
		for x := 0; x < largura; x++ {
			x0 := limites.Min.X + x*limites.Dx()/largura
			x1 := limites.Min.X + (x+1)*limites.Dx()/largura
			if x1 <= x0 {
				x1 = x0 + 1
			}
			var r, g, b, n int
			for sy := y0; sy < y1; sy++ {
				linha := origem.PixOffset(x0, sy)
				for sx := x0; sx < x1; sx++ {
					r += int(origem.Pix[linha])
					g += int(origem.Pix[linha+1])
					b += int(origem.Pix[linha+2])
					linha += 4
					n++
				}
			}
			i := (y*largura + x) * 4
			destino[i] = byte(b / n)
			destino[i+1] = byte(g / n)
			destino[i+2] = byte(r / n)
			destino[i+3] = 0
		}
	}
	return destino
}

// Laco roda o laço de mensagens até a janela fechar.
func (j *Janela) Laco() {
	var m mensagem
	for {
		r, _, _ := pGetMessageW.Call(uintptr(unsafe.Pointer(&m)), 0, 0, 0)
		if int32(r) <= 0 {
			return
		}
		pTranslateMessage.Call(uintptr(unsafe.Pointer(&m)))
		pDispatchMessageW.Call(uintptr(unsafe.Pointer(&m)))
	}
}

func (j *Janela) Status(texto string) {
	j.mu.Lock()
	j.texto = texto
	j.mu.Unlock()
	pPostMessageW.Call(j.hwnd, wmStatus, 0, 0)
}

func (j *Janela) Progresso(pct int) {
	if pct < 0 {
		pct = 0
	} else if pct > 100 {
		pct = 100
	}
	j.mu.Lock()
	mudou := j.pct != pct
	j.pct = pct
	j.mu.Unlock()
	if mudou {
		pPostMessageW.Call(j.hwnd, wmProgresso, 0, 0)
	}
}

func (j *Janela) Libera() { pPostMessageW.Call(j.hwnd, wmLibera, 0, 0) }
func (j *Janela) Fecha()  { pPostMessageW.Call(j.hwnd, wmFecha, 0, 0) }

// Novidades põe o changelog na janela — chamada da goroutine de trabalho, como
// o Status. O layout é jogado fora e refeito no próximo desenho.
func (j *Janela) Novidades(lista []novidade) {
	j.mu.Lock()
	j.novidades, j.linhasNov, j.celulasNov = lista, nil, nil
	j.rolagem, j.celulaSobre, j.copiada = 0, -1, -1
	j.mu.Unlock()
	pPostMessageW.Call(j.hwnd, wmNovidades, 0, 0)
}

// SemNovidades diz se o painel ainda está vazio. É o que decide se vale cair
// nos nomes da `lista.txt` — ver `deLista`.
func (j *Janela) SemNovidades() bool {
	j.mu.Lock()
	defer j.mu.Unlock()
	return len(j.novidades) == 0
}

// Os quatro métodos abaixo mexem no estado do painel e SUPÕEM O MUTEX PRESO.
// Eles vivem juntos porque são a mesma conta vista de ângulos diferentes: onde
// o conteúdo está, onde ele cabe, e o que disso está debaixo do ponteiro.

func (j *Janela) limitaRolagem() {
	teto := j.alturaNov - (areaNovLista.base - areaNovLista.topo)
	if teto < 0 {
		teto = 0
	}
	if j.rolagem > teto {
		j.rolagem = teto
	}
	if j.rolagem < 0 {
		j.rolagem = 0
	}
}

// polegarNov devolve o retângulo do polegar da rolagem, e `false` quando o
// conteúdo cabe inteiro — aí não há barra nenhuma na tela.
func (j *Janela) polegarNov() (rect, bool) {
	visivel := areaNovLista.base - areaNovLista.topo
	if j.alturaNov <= visivel || len(j.celulasNov) == 0 {
		return rect{}, false
	}
	trilho := areaTrilhoNov.base - areaTrilhoNov.topo
	altura := trilho * visivel / j.alturaNov
	if altura < 28 { // polegar de 3 px não se agarra com o mouse
		altura = 28
	}
	topo := areaTrilhoNov.topo + (trilho-altura)*j.rolagem/(j.alturaNov-visivel)
	return rect{areaTrilhoNov.esquerda, topo, areaTrilhoNov.direita, topo + altura}, true
}

// celulaEm diz qual célula está sob o ponto, em coordenadas da JANELA. Só conta
// o que está dentro da área visível: célula rolada para fora não é clicável,
// mesmo que a conta do conteúdo a alcance.
func (j *Janela) celulaEm(x, y int32) int {
	if !areaNovLista.contem(x, y) {
		return -1
	}
	alvo := y - areaNovLista.topo + j.rolagem
	for i, c := range j.celulasNov {
		if alvo >= c.topo && alvo < c.base {
			return i
		}
	}
	return -1
}

// botaoDaCelula traz o botão de copiar para as coordenadas da janela.
func (j *Janela) botaoDaCelula(i int) rect {
	b := j.celulasNov[i].botao
	desloca := areaNovLista.topo - j.rolagem
	return rect{b.esquerda, b.topo + desloca, b.direita, b.base + desloca}
}

func (j *Janela) celulaSobreAgora() int {
	j.mu.Lock()
	defer j.mu.Unlock()
	return j.celulaSobre
}

// arrastaRolagem move o conteúdo enquanto o polegar está preso ao ponteiro, e
// diz se era isso que estava acontecendo.
func (j *Janela) arrastaRolagem(y int32) bool {
	j.mu.Lock()
	if !j.arrastando {
		j.mu.Unlock()
		return false
	}
	if polegar, tem := j.polegarNov(); tem {
		visivel := areaNovLista.base - areaNovLista.topo
		curso := (areaTrilhoNov.base - areaTrilhoNov.topo) - (polegar.base - polegar.topo)
		if curso > 0 {
			j.rolagem = (y - j.agarrou - areaTrilhoNov.topo) * (j.alturaNov - visivel) / curso
			j.limitaRolagem()
		}
	}
	j.mu.Unlock()
	j.repinta()
	return true
}

// cliqueNoPainel trata o clique dentro do painel e diz se ele era dali. Três
// destinos: o botão de copiar da célula, o polegar da rolagem (que passa a ser
// arrastado) e o trilho, que rola uma tela.
//
// Devolver `true` para clique no painel que não fez nada é de propósito: sem
// isso o clique cairia no `switch` de baixo e o painel viraria uma janela por
// onde se aperta o que está atrás.
func (j *Janela) cliqueNoPainel(hwnd uintptr, x, y int32) bool {
	j.mu.Lock()
	if len(j.celulasNov) == 0 || !areaNovidades.contem(x, y) {
		j.mu.Unlock()
		return false
	}
	if polegar, tem := j.polegarNov(); tem && areaTrilhoNov.contem(x, y) {
		if polegar.contem(x, y) {
			j.arrastando, j.agarrou = true, y-polegar.topo
			j.mu.Unlock()
			pSetCapture.Call(hwnd)
			return true
		}
		tela := areaNovLista.base - areaNovLista.topo
		if y < polegar.topo {
			j.rolagem -= tela
		} else {
			j.rolagem += tela
		}
		j.limitaRolagem()
		j.mu.Unlock()
		j.repinta()
		return true
	}
	celula := j.celulaEm(x, y)
	if celula < 0 || !j.botaoDaCelula(celula).contem(x, y) {
		j.mu.Unlock()
		return true
	}
	mensagem := j.celulasNov[celula].mensagem
	j.mu.Unlock()

	if err := copiaTexto(hwnd, mensagem); err != nil {
		// A área de transferência pode estar presa por outro programa — é uma
		// falha comum e passageira do Windows. Não vale mensagem na tela: o
		// jogador clica de novo e funciona.
		anota("copiar novidade: %v", err)
		return true
	}
	j.mu.Lock()
	j.copiada = celula
	j.mu.Unlock()
	j.repinta()

	// O "copiado!" apaga sozinho. Sem isso ele ficaria aceso até o ponteiro
	// sair da célula, e quem copiasse duas vezes seguidas não veria diferença
	// nenhuma na segunda.
	go func() {
		time.Sleep(1600 * time.Millisecond)
		j.mu.Lock()
		if j.copiada == celula {
			j.copiada = -1
		}
		j.mu.Unlock()
		pPostMessageW.Call(j.hwnd, wmNovidades, 0, 0)
	}()
	return true
}

func processa(hwnd uintptr, msg uint32, wParam, lParam uintptr) uintptr {
	j := jan
	if j == nil || j.hwnd == 0 {
		// As primeiras mensagens chegam durante o próprio CreateWindowEx, antes
		// de a janela estar montada. Deixa o Windows tratá-las.
		r, _, _ := pDefWindowProcW.Call(hwnd, uintptr(msg), wParam, lParam)
		return r
	}
	x, y := int32(int16(lParam&0xFFFF)), int32(int16((lParam>>16)&0xFFFF))

	switch msg {
	case 0x000F: // WM_PAINT
		var ps paintStruct
		hdc, _, _ := pBeginPaint.Call(hwnd, uintptr(unsafe.Pointer(&ps)))
		j.pinta(hdc)
		pEndPaint.Call(hwnd, uintptr(unsafe.Pointer(&ps)))
		return 0

	case 0x0014: // WM_ERASEBKGND — nós pintamos tudo, o padrão só faria piscar
		return 1

	case 0x0084: // WM_NCHITTEST
		// Coordenadas de tela nesta mensagem; converter para a janela.
		var p struct{ x, y int32 }
		p.x, p.y = x, y
		pScreenToClient := user32.NewProc("ScreenToClient")
		pScreenToClient.Call(hwnd, uintptr(unsafe.Pointer(&p)))
		// Os botões precisam de HTCLIENT para receber o clique; o resto da
		// faixa de cima é HTCAPTION, que é o que torna a janela arrastável sem
		// ter barra de título do Windows.
		if areaFechar.contem(p.x, p.y) || areaMinimiza.contem(p.x, p.y) {
			return 1 // HTCLIENT
		}
		if areaBarra.contem(p.x, p.y) {
			return 2 // HTCAPTION
		}
		return 1

	case 0x0200: // WM_MOUSEMOVE
		if j.arrastaRolagem(y) {
			return 0
		}
		anterior := j.ondeEstou()
		celulaAntes := j.celulaSobreAgora()
		agora := 0
		celula := -1
		perguntando := j.noModoPergunta()
		switch {
		case areaJogar.contem(x, y) && j.botaoAceso():
			agora = 1
		case areaMinimiza.contem(x, y):
			agora = 2
		case areaFechar.contem(x, y):
			agora = 3
		case perguntando && areaMudar.contem(x, y):
			agora = 4
		case perguntando && areaAtalho.contem(x, y):
			agora = 5
		default:
			// O painel de novidades não encosta em nenhum dos botões acima —
			// ele mora sobre a arte —, então só se pergunta por ele aqui.
			j.mu.Lock()
			celula = j.celulaEm(x, y)
			if celula >= 0 && j.botaoDaCelula(celula).contem(x, y) {
				agora = 6
			}
			j.mu.Unlock()
		}
		if agora != anterior || celula != celulaAntes {
			j.mu.Lock()
			j.sobre = agora
			j.celulaSobre = celula
			j.mu.Unlock()
			j.repinta()
			// Sem isto o realce fica aceso quando o ponteiro sai pela borda.
			tme := trackMouse{tamanho: uint32(unsafe.Sizeof(trackMouse{})),
				bandeiras: 0x00000002, hwnd: hwnd} // TME_LEAVE
			pTrackMouseEvent.Call(uintptr(unsafe.Pointer(&tme)))
		}
		return 0

	case 0x02A3: // WM_MOUSELEAVE
		j.mu.Lock()
		j.sobre, j.celulaSobre = 0, -1
		j.mu.Unlock()
		j.repinta()
		return 0

	case 0x020A: // WM_MOUSEWHEEL
		// A roda vai para a janela COM FOCO, e não para a que está sob o
		// ponteiro — por isso não se testa posição nenhuma aqui: se esta janela
		// recebeu a mensagem, o painel é a única coisa que rola nela.
		//
		// O delta é a metade de cima do wParam, e é COM SINAL: lido como
		// `uint16`, rolar para baixo (-120) viraria 65416 e a lista saltaria
		// para o fim numa volta só.
		volta := int32(int16(uint16(wParam>>16))) / 120
		j.mu.Lock()
		j.rolagem -= volta * 3 * 18 // três linhas por entalhe, como todo mundo
		j.limitaRolagem()
		j.mu.Unlock()
		j.repinta()
		return 0

	case 0x0202: // WM_LBUTTONUP
		j.mu.Lock()
		arrastava := j.arrastando
		j.arrastando = false
		j.mu.Unlock()
		if arrastava {
			pReleaseCapture.Call()
		}
		return 0

	case 0x0020: // WM_SETCURSOR — mãozinha sobre o que é clicável
		if j.ondeEstou() != 0 {
			mao, _, _ := pLoadCursorW.Call(0, 32649) // IDC_HAND
			pSetCursor.Call(mao)
			return 1
		}

	case 0x0201: // WM_LBUTTONDOWN
		if j.cliqueNoPainel(hwnd, x, y) {
			return 0
		}
		switch {
		case areaFechar.contem(x, y):
			pDestroyWindow.Call(hwnd)
		case areaMinimiza.contem(x, y):
			pShowWindow.Call(hwnd, 6) // SW_MINIMIZE
		case j.noModoPergunta() && areaMudar.contem(x, y):
			if escolhida, ok := EscolhePasta(hwnd, "Onde instalar a Guerra do Emperium?"); ok {
				j.mu.Lock()
				j.destino = escolhida
				j.mu.Unlock()
				j.repinta()
			}

		case j.noModoPergunta() && areaAtalho.contem(x, y):
			j.mu.Lock()
			j.atalho = !j.atalho
			j.mu.Unlock()
			j.repinta()

		case areaJogar.contem(x, y) && j.botaoAceso():
			// No modo pergunta o botão começa a instalação: a tela de escolha
			// sai do ar e o rodapé volta a ser estado e progresso. A janela NÃO
			// se fecha — é o contrário do JOGAR.
			if j.noModoPergunta() {
				destino, atalho := j.Escolhas()
				j.mu.Lock()
				j.pergunta = false
				j.texto = "Preparando…"
				j.sobre = 0
				j.mu.Unlock()
				j.repinta()
				if j.Instalar != nil {
					j.Instalar(destino, atalho)
				}
				return 0
			}
			if j.Jogar != nil {
				if err := j.Jogar(); err != nil {
					j.Status(err.Error())
					return 0
				}
			}
			pDestroyWindow.Call(hwnd)
		}
		return 0

	case wmStatus, wmProgresso, wmNovidades:
		j.repinta()
		return 0

	case wmLibera:
		j.mu.Lock()
		j.pronto = true
		j.mu.Unlock()
		j.repinta()
		return 0

	case wmFecha:
		pDestroyWindow.Call(hwnd)
		return 0

	case 0x0002: // WM_DESTROY
		pPostQuitMessage.Call(0)
		return 0
	}
	r, _, _ := pDefWindowProcW.Call(hwnd, uintptr(msg), wParam, lParam)
	return r
}

func (j *Janela) ondeEstou() int {
	j.mu.Lock()
	defer j.mu.Unlock()
	return j.sobre
}

func (j *Janela) estaPronto() bool {
	j.mu.Lock()
	defer j.mu.Unlock()
	return j.pronto
}

func (j *Janela) repinta() {
	pInvalidateRect.Call(j.hwnd, 0, 0)
}

// pinta desenha a janela inteira num bitmap de memória e copia de uma vez. É o
// que permite repintar tudo a cada 100 ms de download sem a arte piscar.
func (j *Janela) pinta(hdc uintptr) {
	if j.bufferDC == 0 {
		j.bufferDC, _, _ = pCreateCompatibleDC.Call(hdc)
		j.buffer, _, _ = pCreateCompatibleBitmap.Call(hdc, larguraJanela, alturaJanela)
		pSelectObject.Call(j.bufferDC, j.buffer)
	}
	b := j.bufferDC

	j.mu.Lock()
	texto, pct, pronto, sobre := j.texto, j.pct, j.pronto, j.sobre
	pergunta, destino, atalho := j.pergunta, j.destino, j.atalho
	j.mu.Unlock()

	// 1. a arte
	if j.arteDC != 0 {
		pBitBlt.Call(b, 0, alturaBarra, larguraJanela, alturaArte, j.arteDC, 0, 0, 0x00CC0020)
	} else {
		preenche(b, areaArte, corFundo)
	}

	// 1b. o painel de novidades, por cima da arte
	j.pintaNovidades(b)

	// 2. a moldura de cima, com o nome do servidor e os dois botões
	preenche(b, areaBarra, corFundo)
	preenche(b, rect{0, alturaBarra - 1, larguraJanela, alturaBarra}, corLinha)
	escreve(b, rect{20, 0, 500, alturaBarra}, "GUERRA DO EMPERIUM", j.fonteTit,
		corDourado, dtEsquerda)

	cor := corTexto
	if sobre == 2 {
		cor = corBrilho
	}
	escreve(b, areaMinimiza, "—", j.fonte, cor, dtCentro)
	cor = corTexto
	if sobre == 3 {
		preenche(b, areaFechar, rgb(150, 40, 32))
		cor = rgb(255, 240, 230)
	}
	escreve(b, areaFechar, "✕", j.fonte, cor, dtCentro)

	// 3. o rodapé
	preenche(b, areaRodape, corFundo)
	preenche(b, rect{0, areaRodape.topo, larguraJanela, areaRodape.topo + 1}, corLinha)
	escreve(b, areaCredito, "Ragnarok Online © Gravity Corp. & Lee Myoungjin",
		j.fonteMin, corApagado, dtCentro)

	if pergunta {
		// 3a. a tela de escolha, no lugar do estado e da barra: a instalação
		// ainda não começou, então não há progresso a mostrar.
		escreve(b, rect{areaPasta.esquerda, areaPasta.topo, areaPasta.direita, areaPasta.topo + 13},
			"INSTALAR EM", j.fonteMin, corApagado, dtEsquerda)
		escreve(b, rect{areaPasta.esquerda, areaPasta.topo + 12, areaPasta.direita, areaPasta.base},
			destino, j.fonte, corTexto, dtEsquerda|dtCaminho)

		corMudar := corDourado
		if sobre == 4 {
			corMudar = corBrilho
		}
		moldura(b, areaMudar, corMudar)
		escreve(b, areaMudar, "Mudar…", j.fonte, corMudar, dtCentro)

		// O checkbox. A marca é um "✓" desenhado com a fonte do botão, e não um
		// controle nativo — o resto da janela também não é.
		corMarca := corDourado
		if sobre == 5 {
			corMarca = corBrilho
		}
		preenche(b, areaMarca, corTrilho)
		moldura(b, areaMarca, corMarca)
		if atalho {
			escreve(b, areaMarca, "✓", j.fonte, corMarca, dtCentro)
		}
		escreve(b, rect{areaMarca.direita + 10, areaAtalho.topo, areaAtalho.direita, areaAtalho.base},
			"Criar atalho na Área de Trabalho", j.fonte, corTexto, dtEsquerda)
	} else {
		escreve(b, areaStatus, texto, j.fonte, corTexto, dtEsquerda|dtQuebra)

		// 4. a barra de progresso
		preenche(b, areaBarraProg, corTrilho)
		moldura(b, areaBarraProg, corLinha)
		largura := (areaBarraProg.direita - areaBarraProg.esquerda - 4) * int32(pct) / 100
		if largura > 0 {
			gradiente(b, rect{areaBarraProg.esquerda + 2, areaBarraProg.topo + 2,
				areaBarraProg.esquerda + 2 + largura, areaBarraProg.base - 2},
				corBrilho, corDourado)
		}
	}

	// 5. o botão principal — apagado enquanto o trabalho não termina. No modo
	// pergunta ele está sempre aceso, e diz INSTALAR: não há o que esperar.
	rotulo := "JOGAR"
	if pergunta {
		rotulo = "INSTALAR"
	}
	if pronto || pergunta {
		alto, baixo := corVerdeAlt, corVerde
		if sobre == 1 {
			alto, baixo = rgb(104, 200, 138), corVerdeAlt
		}
		gradiente(b, areaJogar, alto, baixo)
		moldura(b, areaJogar, corDourado)
		escreve(b, areaJogar, rotulo, j.fonteBot, rgb(255, 252, 240), dtCentro)
	} else {
		preenche(b, areaJogar, rgb(38, 32, 26))
		moldura(b, areaJogar, rgb(70, 60, 44))
		escreve(b, areaJogar, rotulo, j.fonteBot, rgb(96, 86, 68), dtCentro)
	}

	// 6. a moldura da janela inteira, por último, para nada passar por cima
	moldura(b, rect{0, 0, larguraJanela, alturaJanela}, corLinha)

	pBitBlt.Call(hdc, 0, 0, larguraJanela, alturaJanela, b, 0, 0, 0x00CC0020)
}

// pintaNovidades desenha o painel do changelog. Some da tela enquanto não há
// nada para mostrar — antes de a lista chegar do servidor, e quando ela não
// chega — porque um retângulo vazio sobre a arte seria pior que arte nenhuma.
func (j *Janela) pintaNovidades(b uintptr) {
	j.mu.Lock()
	if j.linhasNov == nil && len(j.novidades) > 0 {
		j.montaNovidades(b)
	}
	linhas, celulas := j.linhasNov, j.celulasNov
	rolagem, sobre, copiada := j.rolagem, j.celulaSobre, j.copiada
	polegar, temPolegar := j.polegarNov()
	j.mu.Unlock()
	if len(celulas) == 0 {
		return
	}

	if j.fundoNovDC != 0 {
		pBitBlt.Call(b, uintptr(areaNovidades.esquerda), uintptr(areaNovidades.topo),
			uintptr(areaNovidades.direita-areaNovidades.esquerda),
			uintptr(areaNovidades.base-areaNovidades.topo),
			j.fundoNovDC, 0, 0, 0x00CC0020)
	} else {
		preenche(b, areaNovidades, corFundo)
	}
	moldura(b, areaNovidades, corLinha)
	preenche(b, rect{areaNovCab.esquerda, areaNovCab.base - 1, areaNovCab.direita,
		areaNovCab.base}, corLinha)
	escreve(b, rect{areaNovCab.esquerda + recuoNov, areaNovCab.topo,
		areaNovCab.direita - recuoNov, areaNovCab.base},
		"NOVIDADES", j.fonteMin, corDourado, dtEsquerda)

	// O conteúdo é RECORTADO na área da lista, e é isso que faz a rolagem
	// parecer rolagem: a linha de cima e a de baixo saem cortadas ao meio, em
	// vez de sumirem inteiras. Sem o recorte, o texto rolado escaparia por cima
	// do cabeçalho e por baixo da moldura.
	salvo, _, _ := pSaveDC.Call(b)
	pIntersectClipRect.Call(b, uintptr(areaNovLista.esquerda), uintptr(areaNovLista.topo),
		uintptr(areaNovLista.direita), uintptr(areaNovLista.base))

	desloca := areaNovLista.topo - rolagem
	for i, c := range celulas {
		topo, base := c.topo+desloca, c.base+desloca
		if base < areaNovLista.topo || topo > areaNovLista.base {
			continue
		}
		realce := i == sobre || i == copiada
		if realce {
			j.realcaCelula(b, rect{areaNovLista.esquerda + 4, topo,
				areaNovLista.direita - 4, base})
		}
		if i > 0 {
			preenche(b, rect{areaNovLista.esquerda + recuoNov, topo - 8,
				areaNovLista.direita - recuoNov, topo - 7}, rgb(58, 47, 30))
		}
		// O botão só aparece na célula sob o ponteiro: um "copiar" em cada
		// bloco viraria uma coluna de botões, e a lista é para ser lida antes
		// de ser copiada.
		if realce {
			rotulo, cor := "copiar", corDourado
			if i == copiada {
				rotulo, cor = "copiado!", corBrilho
			}
			botao := rect{c.botao.esquerda, c.botao.topo + desloca,
				c.botao.direita, c.botao.base + desloca}
			preenche(b, botao, corTrilho)
			moldura(b, botao, cor)
			escreve(b, botao, rotulo, j.fonteMin, cor, dtCentro)
		}
	}
	for _, l := range linhas {
		y := l.y + desloca
		if y+l.altura < areaNovLista.topo || y > areaNovLista.base {
			continue
		}
		escreve(b, rect{l.x, y, areaNovLista.direita - recuoNov, y + l.altura},
			l.texto, l.fonte, l.cor, dtEsquerda)
	}
	pRestoreDC.Call(b, uintptr(salvo))

	if temPolegar {
		preenche(b, areaTrilhoNov, rgb(30, 24, 18))
		gradiente(b, polegar, corDourado, rgb(120, 96, 44))
	}
}

// realcaCelula pinta o fundo da célula sob o ponteiro copiando o pedaço
// correspondente do bitmap de realce — a mesma mistura do fundo, um tom acima.
//
// O retângulo é APARADO na área visível antes da cópia: o recorte do desenho
// cuidaria do destino, mas a origem sairia do bitmap e o BitBlt leria fora dele
// (célula meio rolada para fora é o caso normal, não a exceção).
func (j *Janela) realcaCelula(b uintptr, r rect) {
	if r.topo < areaNovLista.topo {
		r.topo = areaNovLista.topo
	}
	if r.base > areaNovLista.base {
		r.base = areaNovLista.base
	}
	if r.base <= r.topo {
		return
	}
	if j.realceNovDC == 0 {
		preenche(b, r, rgb(40, 32, 22))
		return
	}
	pBitBlt.Call(b, uintptr(r.esquerda), uintptr(r.topo),
		uintptr(r.direita-r.esquerda), uintptr(r.base-r.topo), j.realceNovDC,
		uintptr(r.esquerda-areaNovidades.esquerda),
		uintptr(r.topo-areaNovidades.topo), 0x00CC0020)
}

// montaNovidades mede e quebra o changelog inteiro de uma vez, guardando linhas
// já posicionadas em coordenadas de conteúdo. SUPÕE O MUTEX PRESO, e é chamada
// do WM_PAINT porque medir texto exige um DC com a fonte selecionada.
//
// Refazer isso a cada desenho custaria uma medição por palavra a cada 100 ms de
// download — e a rolagem, que é o que mais repinta, não muda medida nenhuma.
func (j *Janela) montaNovidades(hdc uintptr) {
	j.linhasNov, j.celulasNov, j.alturaNov = []linhaNov{}, nil, 0
	x := areaNovLista.esquerda + recuoNov
	y := int32(12)

	for _, n := range j.novidades {
		celula := celulaNov{topo: y - 8, mensagem: n.mensagem()}

		selo := fmt.Sprintf("%04d", n.Numero)
		if d := n.dataCurta(); d != "" {
			selo += "   ·   " + d
		}
		// A linha do número e da data usa um cinza mais claro que o do crédito
		// do rodapé: com o painel translúcido, ela cai sobre a parte clara da
		// arte de vez em quando, e o `corApagado` some ali.
		j.linhasNov = append(j.linhasNov, linhaNov{selo, x, y, 15, j.fonteMin, corSelo})
		celula.botao = rect{areaTrilhoNov.esquerda - 8 - 62, y - 1,
			areaTrilhoNov.esquerda - 8, y + 16}
		y += 18

		for _, linha := range quebra(hdc, j.fonteNovTit, n.Titulo, larguraTextoNov) {
			j.linhasNov = append(j.linhasNov, linhaNov{linha, x, y, 19, j.fonteNovTit, corDourado})
			y += 19
		}
		// O ponto e o texto são linhas separadas para as continuações ficarem
		// alinhadas com a primeira, e não embaixo da bolinha.
		for _, ponto := range n.Pontos {
			for k, linha := range quebra(hdc, j.fonteNov, ponto, larguraTextoNov-18) {
				if k == 0 {
					j.linhasNov = append(j.linhasNov,
						linhaNov{"•", x + 2, y, 16, j.fonteNov, corApagado})
				}
				j.linhasNov = append(j.linhasNov,
					linhaNov{linha, x + 18, y, 16, j.fonteNov, corTexto})
				y += 16
			}
		}
		y += 8
		celula.base = y
		j.celulasNov = append(j.celulasNov, celula)
		y += 16
	}
	j.alturaNov = y
	j.limitaRolagem()
}

// quebra corta o texto nas linhas que cabem na largura, medindo com a fonte que
// vai desenhá-las. O DrawTextW faria isso sozinho com DT_WORDBREAK — mas então
// o bloco inteiro seria desenhado de uma vez, e uma lista de trinta itens que
// rola dentro de um painel precisa saber onde cada linha começa.
func quebra(hdc, fonte uintptr, texto string, largura int32) []string {
	palavras := strings.Fields(texto)
	if len(palavras) == 0 {
		return nil
	}
	var linhas []string
	atual := ""
	for _, p := range palavras {
		tentativa := p
		if atual != "" {
			tentativa = atual + " " + p
		}
		// A segunda condição é o caso da palavra sozinha maior que a largura:
		// ela fica assim mesmo e o recorte a corta. Partir nome de item no meio
		// seria pior, e 40 letras não é um nome de item de RO.
		if mede(hdc, fonte, tentativa) <= largura || atual == "" {
			atual = tentativa
			continue
		}
		linhas = append(linhas, atual)
		atual = p
	}
	return append(linhas, atual)
}

type tamanhoTexto struct{ cx, cy int32 }

// mede devolve a largura do texto em pixels, na fonte dada.
func mede(hdc, fonte uintptr, texto string) int32 {
	pSelectObject.Call(hdc, fonte)
	letras := syscall.StringToUTF16(texto)
	var t tamanhoTexto
	// O comprimento é EM CARACTERES E SEM O TERMINADOR — daí o -1. Contá-lo
	// mediria o NUL como se fosse letra, e a conta erraria por um espaço em
	// toda linha.
	pGetTextExtentPoint32W.Call(hdc, uintptr(unsafe.Pointer(&letras[0])),
		uintptr(len(letras)-1), uintptr(unsafe.Pointer(&t)))
	return t.cx
}

func preenche(hdc uintptr, r rect, cor uintptr) {
	pincel, _, _ := pCreateSolidBrush.Call(cor)
	pFillRect.Call(hdc, uintptr(unsafe.Pointer(&r)), pincel)
	pDeleteObject.Call(pincel)
}

func moldura(hdc uintptr, r rect, cor uintptr) {
	preenche(hdc, rect{r.esquerda, r.topo, r.direita, r.topo + 1}, cor)
	preenche(hdc, rect{r.esquerda, r.base - 1, r.direita, r.base}, cor)
	preenche(hdc, rect{r.esquerda, r.topo, r.esquerda + 1, r.base}, cor)
	preenche(hdc, rect{r.direita - 1, r.topo, r.direita, r.base}, cor)
}

// gradiente pinta linha a linha, de cima para baixo. O GradientFill do Windows
// faria o mesmo, mas mora na msimg32.dll — uma DLL a mais para pintar algumas
// dezenas de linhas não se paga.
//
// A interpolação é em `int` COM SINAL, e isso é o defeito que ela já teve: com
// `uintptr`, um degradê que escurece (240 → 200) faz `r2-r1` dar -40 num tipo
// sem sinal, que vira um número astronômico e a cor sai aleatória. O sintoma
// foi um botão verde nascer ciano, e uma barra dourada nascer invisível — as
// duas ao mesmo tempo, porque a conta é a mesma.
func gradiente(hdc uintptr, r rect, alto, baixo uintptr) {
	altura := int(r.base - r.topo)
	if altura <= 0 {
		return
	}
	r1, g1, b1 := int(alto&0xFF), int((alto>>8)&0xFF), int((alto>>16)&0xFF)
	r2, g2, b2 := int(baixo&0xFF), int((baixo>>8)&0xFF), int((baixo>>16)&0xFF)
	for i := 0; i < altura; i++ {
		cor := rgb(uint32(r1+(r2-r1)*i/altura),
			uint32(g1+(g2-g1)*i/altura),
			uint32(b1+(b2-b1)*i/altura))
		preenche(hdc, rect{r.esquerda, r.topo + int32(i), r.direita, r.topo + int32(i) + 1}, cor)
	}
}

// O DT_NOPREFIX (0x0800) em todos: sem ele o `&` do crédito "Gravity Corp. &
// Lee Myoungjin" é lido como marca de tecla de atalho — o `&` some da tela e a
// letra seguinte aparece sublinhada. Nome de item de jogo com `&` cairia na
// mesma armadilha.
const (
	dtCentro   = 0x0001 | 0x0004 | 0x0020 | 0x0800 // CENTER|VCENTER|SINGLELINE|NOPREFIX
	dtEsquerda = 0x0000 | 0x0004 | 0x0020 | 0x0800 // LEFT|VCENTER|SINGLELINE|NOPREFIX
	dtQuebra   = 0x8000                            // END_ELLIPSIS
	// PATH_ELLIPSIS corta caminho pelo MEIO (`C:\Jogos\…\Emperium`), preservando
	// as duas pontas. Num caminho, o fim é o que identifica a pasta — cortá-lo
	// com reticências no final mostraria três caminhos diferentes iguais.
	dtCaminho = 0x4000
)

func escreve(hdc uintptr, r rect, texto string, fonte, cor uintptr, bandeiras uintptr) {
	pSelectObject.Call(hdc, fonte)
	pSetBkMode.Call(hdc, 1) // TRANSPARENT
	pSetTextColor.Call(hdc, cor)
	letras := syscall.StringToUTF16(texto)
	pDrawTextW.Call(hdc, uintptr(unsafe.Pointer(&letras[0])), ^uintptr(0),
		uintptr(unsafe.Pointer(&r)), bandeiras)
}
