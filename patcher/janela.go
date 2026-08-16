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
)

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
	hwnd     uintptr
	fonte    uintptr // o estado, no rodapé
	fonteTit uintptr // o nome do servidor, na moldura
	fonteBot uintptr // o JOGAR
	fonteMin uintptr // o crédito
	arte     uintptr
	arteDC   uintptr
	buffer   uintptr
	bufferDC uintptr

	// Jogar é chamado quando o botão é clicado. Devolver erro mantém a janela
	// aberta com a mensagem na tela — é o que acontece se o exe do jogo sumir.
	Jogar func() error

	mu     sync.Mutex
	texto  string
	pct    int
	pronto bool
	sobre  int // 0 nenhum, 1 jogar, 2 minimizar, 3 fechar
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
	j := &Janela{texto: "Iniciando…"}
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

	// O bitmap é criado com CreateDIBSection e os pixels são COPIADOS na memória
	// dele. Não há conversão de formato, não há escala, não há chamada que possa
	// falhar por motivo obscuro: o Windows devolve um ponteiro e nós escrevemos.
	//
	// A alternativa natural — `StretchDIBits` — foi tentada primeiro e falha de
	// forma intermitente nesta máquina: devolve 0 (erro) com `GetLastError`
	// dizendo "operação concluída com êxito", umas vezes sim e outras não, no
	// mesmo binário. Com HALFTONE, sem HALFTONE, com escala e sem escala. O
	// sintoma é a janela nascer com o retângulo da arte preto, e nada além do
	// log dizer o que houve. Ver `CLAUDE.md` §5.
	//
	// Altura negativa: os nossos pixels vão de cima para baixo, e o padrão do
	// Windows é o contrário.
	cabecalho := bitmapInfoHeader{
		tamanho: uint32(unsafe.Sizeof(bitmapInfoHeader{})),
		largura: larguraJanela, altura: -alturaArte,
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
		anota("arte: CreateDIBSection falhou (%v)", erroGDI)
		return
	}
	copy(unsafe.Slice((*byte)(bits), len(pixels)), pixels)

	j.arte = bmp
	j.arteDC, _, _ = pCreateCompatibleDC.Call(tela)
	pSelectObject.Call(j.arteDC, j.arte)
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
		anterior := j.ondeEstou()
		agora := 0
		switch {
		case areaJogar.contem(x, y) && j.estaPronto():
			agora = 1
		case areaMinimiza.contem(x, y):
			agora = 2
		case areaFechar.contem(x, y):
			agora = 3
		}
		if agora != anterior {
			j.mu.Lock()
			j.sobre = agora
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
		j.sobre = 0
		j.mu.Unlock()
		j.repinta()
		return 0

	case 0x0020: // WM_SETCURSOR — mãozinha sobre o que é clicável
		if j.ondeEstou() != 0 {
			mao, _, _ := pLoadCursorW.Call(0, 32649) // IDC_HAND
			pSetCursor.Call(mao)
			return 1
		}

	case 0x0201: // WM_LBUTTONDOWN
		switch {
		case areaFechar.contem(x, y):
			pDestroyWindow.Call(hwnd)
		case areaMinimiza.contem(x, y):
			pShowWindow.Call(hwnd, 6) // SW_MINIMIZE
		case areaJogar.contem(x, y) && j.estaPronto():
			if j.Jogar != nil {
				if err := j.Jogar(); err != nil {
					j.Status(err.Error())
					return 0
				}
			}
			pDestroyWindow.Call(hwnd)
		}
		return 0

	case wmStatus, wmProgresso:
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
	j.mu.Unlock()

	// 1. a arte
	if j.arteDC != 0 {
		pBitBlt.Call(b, 0, alturaBarra, larguraJanela, alturaArte, j.arteDC, 0, 0, 0x00CC0020)
	} else {
		preenche(b, areaArte, corFundo)
	}

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
	escreve(b, areaStatus, texto, j.fonte, corTexto, dtEsquerda|dtQuebra)
	escreve(b, areaCredito, "Ragnarok Online © Gravity Corp. & Lee Myoungjin",
		j.fonteMin, corApagado, dtCentro)

	// 4. a barra de progresso
	preenche(b, areaBarraProg, corTrilho)
	moldura(b, areaBarraProg, corLinha)
	largura := (areaBarraProg.direita - areaBarraProg.esquerda - 4) * int32(pct) / 100
	if largura > 0 {
		gradiente(b, rect{areaBarraProg.esquerda + 2, areaBarraProg.topo + 2,
			areaBarraProg.esquerda + 2 + largura, areaBarraProg.base - 2},
			corBrilho, corDourado)
	}

	// 5. o botão JOGAR — apagado enquanto o trabalho não termina
	if pronto {
		alto, baixo := corVerdeAlt, corVerde
		if sobre == 1 {
			alto, baixo = rgb(104, 200, 138), corVerdeAlt
		}
		gradiente(b, areaJogar, alto, baixo)
		moldura(b, areaJogar, corDourado)
		escreve(b, areaJogar, "JOGAR", j.fonteBot, rgb(255, 252, 240), dtCentro)
	} else {
		preenche(b, areaJogar, rgb(38, 32, 26))
		moldura(b, areaJogar, rgb(70, 60, 44))
		escreve(b, areaJogar, "JOGAR", j.fonteBot, rgb(96, 86, 68), dtCentro)
	}

	// 6. a moldura da janela inteira, por último, para nada passar por cima
	moldura(b, rect{0, 0, larguraJanela, alturaJanela}, corLinha)

	pBitBlt.Call(hdc, 0, 0, larguraJanela, alturaJanela, b, 0, 0, 0x00CC0020)
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
)

func escreve(hdc uintptr, r rect, texto string, fonte, cor uintptr, bandeiras uintptr) {
	pSelectObject.Call(hdc, fonte)
	pSetBkMode.Call(hdc, 1) // TRANSPARENT
	pSetTextColor.Call(hdc, cor)
	letras := syscall.StringToUTF16(texto)
	pDrawTextW.Call(hdc, uintptr(unsafe.Pointer(&letras[0])), ^uintptr(0),
		uintptr(unsafe.Pointer(&r)), bandeiras)
}
