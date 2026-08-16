// A configuração de vídeo do cliente, que não mora no cliente.
//
// O `GuerraDoEmperium.exe` decide em qual placa criar o dispositivo Direct3D
// lendo o REGISTRO DO WINDOWS, não um arquivo:
//
//	HKLM\SOFTWARE\Gravity Soft\Ragnarok    (visto pelo cliente, que é 32-bit)
//	    DEVICENAME   "NVIDIA GeForce GTX 1650 Ragnarok"
//	    GUIDDEVICE   {…}
//	    GUIDDRIVER   {…}
//	    SOUNDMODE, SPEAKERTYPE, DIGITALRATETYPE…
//
// Quem escreve isso é o `Setup.exe`, que vem na raiz do cliente. Numa máquina
// onde ele nunca rodou, a chave não existe — e o cliente morre logo na abertura
// com `Cannot init d3d OR grf file has problem`. A mensagem cobre dois casos
// muito diferentes com um `OR`, e manda todo mundo procurar defeito no GRF, que
// está perfeito.
//
// Foi o que aconteceu no primeiro teste do instalador em outra máquina, em
// 2026-08-16: os 4,2 GB desceram certos, o sha256 de cada pedaço fechou, e o
// jogo não abriu. O instalador entregava o cliente inteiro e parava uma casa
// antes do fim.
//
// É também por causa desta chave que o cliente PEDE ELEVAÇÃO: `HKEY_LOCAL_MACHINE`
// não se escreve sem privilégio. Os dois sintomas do primeiro teste — o erro de
// elevação e o `Cannot init d3d` — eram a mesma causa vista de dois ângulos.
package main

import (
	"syscall"
	"unsafe"
)

var (
	advapi32          = syscall.NewLazyDLL("advapi32.dll")
	procRegOpenKeyExW = advapi32.NewProc("RegOpenKeyExW")
	procRegQueryValue = advapi32.NewProc("RegQueryValueExW")
	procRegCloseKey   = advapi32.NewProc("RegCloseKey")
)

const (
	hkeyLocalMachine = 0x80000002
	keyRead          = 0x20019
	keyWow6432       = 0x0200 // ver a chave que um programa 32-bit veria
)

// Os dois caminhos possíveis. O Atualizador é 64-bit e o cliente é 32-bit,
// então a mesma chave tem dois nomes dependendo de quem pergunta: com
// `KEY_WOW64_32KEY` o caminho é o de cima; sem, o Windows a expõe no
// `WOW6432Node`. Tentar os dois custa uma chamada e evita depender de qual
// arquitetura este exe foi compilado.
var caminhosDoSetup = []struct {
	caminho string
	flags   uint32
}{
	{`SOFTWARE\Gravity Soft\Ragnarok`, keyRead | keyWow6432},
	{`SOFTWARE\WOW6432Node\Gravity Soft\Ragnarok`, keyRead},
	{`SOFTWARE\Gravity Soft\Ragnarok`, keyRead},
}

// VideoConfigurado diz se o `Setup.exe` já rodou nesta máquina.
//
// Na dúvida devolve TRUE. Um falso negativo mandaria o jogador para uma tela de
// configuração que ele não precisava; um falso positivo apenas deixa o jogo
// tentar abrir e falhar como falharia de qualquer jeito. Entre atrapalhar quem
// está bem e não ajudar quem está mal, a escolha é a segunda.
func VideoConfigurado() bool {
	for _, c := range caminhosDoSetup {
		if leValor(c.caminho, "GUIDDEVICE", c.flags) {
			return true
		}
	}
	return false
}

// leValor abre a chave e vê se o valor existe. Não interessa o CONTEÚDO — se o
// Setup gravou o GUID do dispositivo, ele rodou; e se rodou numa placa que
// depois foi trocada, quem resolve é o próprio Setup, não nós.
func leValor(caminho, valor string, flags uint32) bool {
	caminho16, err := syscall.UTF16PtrFromString(caminho)
	if err != nil {
		return false
	}
	var chave syscall.Handle
	r, _, _ := procRegOpenKeyExW.Call(
		hkeyLocalMachine,
		uintptr(unsafe.Pointer(caminho16)),
		0,
		uintptr(flags),
		uintptr(unsafe.Pointer(&chave)),
	)
	if r != 0 {
		return false
	}
	defer procRegCloseKey.Call(uintptr(chave))

	valor16, err := syscall.UTF16PtrFromString(valor)
	if err != nil {
		return false
	}
	var tamanho uint32
	r, _, _ = procRegQueryValue.Call(
		uintptr(chave),
		uintptr(unsafe.Pointer(valor16)),
		0, 0, 0,
		uintptr(unsafe.Pointer(&tamanho)),
	)
	return r == 0 && tamanho > 0
}
