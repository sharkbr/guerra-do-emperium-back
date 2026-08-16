// A janela, em Win32 puro.
//
// Sem biblioteca de interface: são ~400 linhas de `syscall` contra user32,
// gdi32 e comctl32, e em troca o binário não depende de nada que não seja
// Windows. A janela é uma só, fixa, com quatro coisas dentro — arte, texto de
// estado, barra de progresso e o botão Jogar.
//
// Duas decisões que não são óbvias:
//
//   - a arte é desenhada UMA vez, escalada, num bitmap de memória; o WM_PAINT
//     só faz BitBlt. Repintar o JPEG a cada 100 ms de download faria o
//     atualizador consumir mais CPU desenhando do que baixando.
//   - quando o texto muda, só a FAIXA de baixo é invalidada. Invalidar a
//     janela inteira faz a arte piscar a cada atualização de progresso.
//
// O laço de mensagens precisa da thread principal (`runtime.LockOSThread`), e
// por isso todo o trabalho de rede vive numa goroutine que fala com a janela
// só por `PostMessage`.
package main

import (
	"bytes"
	_ "embed"
	"image"
	"image/draw"
	_ "image/jpeg"
	"runtime"
	"sync"
	"syscall"
	"unsafe"
)

//go:embed recursos/fundo.jpg
var fundoJPEG []byte

const (
	larguraJanela = 560
	alturaArte    = 294 // 1200x630 da arte do site, na largura da janela
	alturaFaixa   = 96
	alturaJanela  = alturaArte + alturaFaixa
)

// As mensagens que a goroutine de trabalho manda para a janela. WM_APP é a
// primeira faixa que o Windows reserva para o programa.
const (
	wmStatus    = 0x8000 + 1
	wmProgresso = 0x8000 + 2
	wmLibera    = 0x8000 + 3
	wmFecha     = 0x8000 + 4
)

var (
	user32   = syscall.NewLazyDLL("user32.dll")
	gdi32    = syscall.NewLazyDLL("gdi32.dll")
	kernel32 = syscall.NewLazyDLL("kernel32.dll")
	comctl32 = syscall.NewLazyDLL("comctl32.dll")

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
	pSendMessageW       = user32.NewProc("SendMessageW")
	pBeginPaint         = user32.NewProc("BeginPaint")
	pEndPaint           = user32.NewProc("EndPaint")
	pFillRect           = user32.NewProc("FillRect")
	pDrawTextW          = user32.NewProc("DrawTextW")
	pInvalidateRect     = user32.NewProc("InvalidateRect")
	pEnableWindow       = user32.NewProc("EnableWindow")
	pSetWindowTextW     = user32.NewProc("SetWindowTextW")
	pDestroyWindow      = user32.NewProc("DestroyWindow")
	pGetSystemMetrics   = user32.NewProc("GetSystemMetrics")
	pSetProcessDPIAware = user32.NewProc("SetProcessDPIAware")
	pLoadCursorW        = user32.NewProc("LoadCursorW")
	pAdjustWindowRect   = user32.NewProc("AdjustWindowRect")
	pGetDC              = user32.NewProc("GetDC")
	pReleaseDC          = user32.NewProc("ReleaseDC")

	pCreateFontW            = gdi32.NewProc("CreateFontW")
	pCreateSolidBrush       = gdi32.NewProc("CreateSolidBrush")
	pCreateCompatibleDC     = gdi32.NewProc("CreateCompatibleDC")
	pCreateCompatibleBitmap = gdi32.NewProc("CreateCompatibleBitmap")
	pSelectObject           = gdi32.NewProc("SelectObject")
	pStretchDIBits          = gdi32.NewProc("StretchDIBits")
	pBitBlt                 = gdi32.NewProc("BitBlt")
	pSetBkMode              = gdi32.NewProc("SetBkMode")
	pSetTextColor           = gdi32.NewProc("SetTextColor")

	pGetModuleHandleW     = kernel32.NewProc("GetModuleHandleW")
	pInitCommonControlsEx = comctl32.NewProc("InitCommonControlsEx")
)

type rect struct{ esquerda, topo, direita, base int32 }

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

type initCommonControls struct{ tamanho, controles uint32 }

func rgb(r, g, b uint32) uintptr { return uintptr(r | g<<8 | b<<16) }

func utf16(s string) *uint16 {
	p, err := syscall.UTF16PtrFromString(s)
	if err != nil {
		p, _ = syscall.UTF16PtrFromString("?")
	}
	return p
}

type janela struct {
	hwnd        uintptr
	barra       uintptr
	botao       uintptr
	fonte       uintptr
	arte        uintptr // bitmap de memória com a arte já escalada
	arteDC      uintptr
	pincelFaixa uintptr

	raiz string
	jogo string

	mu     sync.Mutex
	texto  string
	pct    int
	pronto bool
}

var jan *janela

// O nome da classe é global porque o Windows guarda o ponteiro enquanto a
// classe existir; um ponteiro para variável local do Go poderia ser recolhido.
var nomeClasse = utf16("GuerraAtualizador")

func abreJanela(raiz, jogo string) *janela {
	runtime.LockOSThread()
	pSetProcessDPIAware.Call() // sem isto a janela sai borrada em tela 4K

	instancia, _, _ := pGetModuleHandleW.Call(0)
	icc := initCommonControls{tamanho: 8, controles: 0x20} // ICC_PROGRESS_CLASS
	pInitCommonControlsEx.Call(uintptr(unsafe.Pointer(&icc)))

	j := &janela{raiz: raiz, jogo: jogo, texto: "Iniciando…"}
	jan = j

	// A arte é preparada ANTES de a janela existir, e não depois: decodificar o
	// JPEG leva uns 100 ms, e um WM_PAINT que chegue nesse intervalo pinta o
	// retângulo de cima vazio. Como só a faixa de baixo é invalidada daí em
	// diante, aquele preto ficaria na tela até algo passar por cima da janela.
	// Foi exatamente o que aconteceu na primeira montagem desta janela.
	j.preparaArte()

	cursor, _, _ := pLoadCursorW.Call(0, 32512) // IDC_ARROW
	wc := wndClassExW{
		tamanho:   uint32(unsafe.Sizeof(wndClassExW{})),
		proc:      syscall.NewCallback(processa),
		instancia: instancia,
		cursor:    cursor,
		classe:    nomeClasse,
	}
	pRegisterClassExW.Call(uintptr(unsafe.Pointer(&wc)))

	// WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX: sem borda de
	// redimensionar e sem maximizar — a janela tem um tamanho só.
	const estilo = 0x00000000 | 0x00C00000 | 0x00080000 | 0x00020000
	area := rect{0, 0, larguraJanela, alturaJanela}
	pAdjustWindowRect.Call(uintptr(unsafe.Pointer(&area)), estilo, 0)
	largura, altura := area.direita-area.esquerda, area.base-area.topo

	telaX, _, _ := pGetSystemMetrics.Call(0)
	telaY, _, _ := pGetSystemMetrics.Call(1)
	x := (int32(telaX) - largura) / 2
	y := (int32(telaY) - altura) / 2

	j.hwnd, _, _ = pCreateWindowExW.Call(0,
		uintptr(unsafe.Pointer(nomeClasse)),
		uintptr(unsafe.Pointer(utf16("Guerra do Emperium"))),
		estilo, uintptr(x), uintptr(y), uintptr(largura), uintptr(altura),
		0, 0, instancia, 0)

	j.pincelFaixa, _, _ = pCreateSolidBrush.Call(rgb(20, 16, 12))

	// Altura negativa é altura do caractere, não da célula; 400 é peso normal;
	// 1 é DEFAULT_CHARSET, que é o que faz o acento sair certo — a janela
	// desenha com API Unicode, então nada aqui é cp1252.
	altura13 := -13
	j.fonte, _, _ = pCreateFontW.Call(uintptr(altura13), 0, 0, 0, 400, 0, 0, 0, 1, 0, 0, 5, 0,
		uintptr(unsafe.Pointer(utf16("Segoe UI"))))

	const wsChild, wsVisible, wsDisabled = 0x40000000, 0x10000000, 0x08000000
	j.barra, _, _ = pCreateWindowExW.Call(0,
		uintptr(unsafe.Pointer(utf16("msctls_progress32"))),
		uintptr(unsafe.Pointer(utf16(""))),
		wsChild|wsVisible,
		18, alturaArte+50, 400, 14, j.hwnd, 0, instancia, 0)
	pSendMessageW.Call(j.barra, 0x0406, 0, 100) // PBM_SETRANGE32: 0 a 100

	j.botao, _, _ = pCreateWindowExW.Call(0,
		uintptr(unsafe.Pointer(utf16("BUTTON"))),
		uintptr(unsafe.Pointer(utf16("JOGAR"))),
		wsChild|wsVisible|wsDisabled,
		larguraJanela-142, alturaArte+38, 124, 36, j.hwnd, 1, instancia, 0)
	pSendMessageW.Call(j.botao, 0x0030, j.fonte, 1) // WM_SETFONT

	pShowWindow.Call(j.hwnd, 5) // SW_SHOW
	pUpdateWindow.Call(j.hwnd)
	return j
}

// preparaArte decodifica o JPEG embutido, reduz no tamanho da janela e guarda
// o resultado num bitmap de memória, que é o que o WM_PAINT copia. Falhar aqui
// não é fatal: sem arte a janela fica escura, e o jogador ainda joga.
//
// A REDUÇÃO É FEITA EM GO, e não pelo GDI, e isso não é preciosismo: o
// `StretchDIBits` com `HALFTONE` funcionou em duas execuções e devolveu 0 —
// falha, com `GetLastError` dizendo "operação concluída com êxito" — na
// terceira, no mesmo binário e na mesma máquina. Uma janela que às vezes nasce
// preta é pior que uma imagem levemente pior. Sem escala, a chamada de GDI
// vira uma cópia 1:1, que é a operação mais simples que existe ali.
func (j *janela) preparaArte() {
	img, _, err := image.Decode(bytes.NewReader(fundoJPEG))
	if err != nil {
		anota("arte: decode falhou: %v", err)
		return
	}
	origem := image.NewRGBA(img.Bounds())
	draw.Draw(origem, img.Bounds(), img, img.Bounds().Min, draw.Src)
	pixels := reduz(origem, larguraJanela, alturaArte)

	tela, _, _ := pGetDC.Call(0)
	defer pReleaseDC.Call(0, tela)
	j.arteDC, _, _ = pCreateCompatibleDC.Call(tela)
	j.arte, _, _ = pCreateCompatibleBitmap.Call(tela, larguraJanela, alturaArte)
	pSelectObject.Call(j.arteDC, j.arte)

	// Altura negativa: os nossos pixels vão de cima para baixo, e o padrão do
	// Windows é o contrário.
	cabecalho := bitmapInfoHeader{
		tamanho: uint32(unsafe.Sizeof(bitmapInfoHeader{})),
		largura: larguraJanela, altura: -alturaArte,
		planos: 1, bits: 32,
	}
	linhas, _, _ := pStretchDIBits.Call(j.arteDC,
		0, 0, larguraJanela, alturaArte,
		0, 0, larguraJanela, alturaArte,
		uintptr(unsafe.Pointer(&pixels[0])),
		uintptr(unsafe.Pointer(&cabecalho)),
		0, 0x00CC0020) // DIB_RGB_COLORS, SRCCOPY
	if int32(linhas) != alturaArte {
		anota("arte: StretchDIBits devolveu %d, esperava %d", int32(linhas), alturaArte)
	}
}

// reduz faz a média dos pixels de origem que caem em cada pixel de destino, e
// devolve BGRA — a ordem que o Windows espera num DIB de 32 bits. Média de
// caixa porque a redução é grande (1200 para 560): amostrar o pixel do meio
// deixaria a arte cheia de serrilha.
func reduz(origem *image.RGBA, largura, altura int) []byte {
	limites := origem.Bounds()
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

func (j *janela) laco() {
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

// status, progresso, libera e fecha são o que a goroutine de trabalho usa. Elas
// só guardam o valor e acordam a janela — desenhar de outra thread é o caminho
// curto para uma interface que trava.
func (j *janela) status(texto string) {
	j.mu.Lock()
	j.texto = texto
	j.mu.Unlock()
	pPostMessageW.Call(j.hwnd, wmStatus, 0, 0)
}

func (j *janela) progresso(pct int) {
	if pct < 0 {
		pct = 0
	} else if pct > 100 {
		pct = 100
	}
	j.mu.Lock()
	j.pct = pct
	j.mu.Unlock()
	pPostMessageW.Call(j.hwnd, wmProgresso, uintptr(pct), 0)
}

func (j *janela) libera() { pPostMessageW.Call(j.hwnd, wmLibera, 0, 0) }
func (j *janela) fecha()  { pPostMessageW.Call(j.hwnd, wmFecha, 0, 0) }

func processa(hwnd uintptr, msg uint32, wParam, lParam uintptr) uintptr {
	j := jan
	if j == nil || j.hwnd == 0 {
		// As primeiras mensagens chegam durante o próprio CreateWindowEx, antes
		// de a janela estar montada. Deixa o Windows tratá-las.
		r, _, _ := pDefWindowProcW.Call(hwnd, uintptr(msg), wParam, lParam)
		return r
	}
	switch msg {
	case 0x000F: // WM_PAINT
		var ps paintStruct
		hdc, _, _ := pBeginPaint.Call(hwnd, uintptr(unsafe.Pointer(&ps)))
		j.pinta(hdc)
		pEndPaint.Call(hwnd, uintptr(unsafe.Pointer(&ps)))
		return 0

	case 0x0014: // WM_ERASEBKGND — nós pintamos tudo, o padrão só faria piscar
		return 1

	case 0x0111: // WM_COMMAND
		if lParam == j.botao {
			if err := jogar(j.raiz, j.jogo); err != nil {
				j.status("Não consegui abrir o jogo: " + resumo(err))
				return 0
			}
			pDestroyWindow.Call(hwnd)
		}
		return 0

	case wmStatus:
		j.repintaFaixa()
		return 0

	case wmProgresso:
		pSendMessageW.Call(j.barra, 0x0402, wParam, 0) // PBM_SETPOS
		j.repintaFaixa()
		return 0

	case wmLibera:
		j.mu.Lock()
		j.pronto = true
		j.mu.Unlock()
		pEnableWindow.Call(j.botao, 1)
		pSetWindowTextW.Call(j.botao, uintptr(unsafe.Pointer(utf16("JOGAR"))))
		j.repintaFaixa()
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

// repintaFaixa invalida só a tarja de baixo. A arte fica quieta — é o que
// separa uma janela que atualiza de uma que pisca.
func (j *janela) repintaFaixa() {
	area := rect{0, alturaArte, larguraJanela, alturaJanela}
	pInvalidateRect.Call(j.hwnd, uintptr(unsafe.Pointer(&area)), 0)
}

func (j *janela) pinta(hdc uintptr) {
	if j.arteDC != 0 {
		pBitBlt.Call(hdc, 0, 0, larguraJanela, alturaArte, j.arteDC, 0, 0, 0x00CC0020)
	}

	faixa := rect{0, alturaArte, larguraJanela, alturaJanela}
	pFillRect.Call(hdc, uintptr(unsafe.Pointer(&faixa)), j.pincelFaixa)

	j.mu.Lock()
	texto, pronto := j.texto, j.pronto
	j.mu.Unlock()

	pSelectObject.Call(hdc, j.fonte)
	pSetBkMode.Call(hdc, 1) // TRANSPARENT
	if pronto {
		pSetTextColor.Call(hdc, rgb(220, 200, 150))
	} else {
		pSetTextColor.Call(hdc, rgb(200, 200, 200))
	}

	linha := rect{18, alturaArte + 14, larguraJanela - 18, alturaArte + 44}
	letras := syscall.StringToUTF16(texto)
	const dtWordBreak, dtEndEllipsis = 0x10, 0x8000
	pDrawTextW.Call(hdc, uintptr(unsafe.Pointer(&letras[0])), ^uintptr(0),
		uintptr(unsafe.Pointer(&linha)), dtWordBreak|dtEndEllipsis)
}
