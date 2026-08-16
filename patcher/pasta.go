// A janela de escolher pasta — a única caixa nativa do Windows que este
// programa abre.
//
// Todo o resto da interface é desenhado à mão para não parecer um utilitário
// (ver `patcher/LEIAME.md` §4b), mas aqui a decisão é a inversa: escolher pasta
// envolve árvore de diretórios, unidades de rede, permissão e criação de pasta
// nova. Desenhar isso do zero seria muito trabalho para chegar num resultado
// pior — e é uma tela que o jogador vê por cinco segundos, uma vez na vida.
package main

import (
	"syscall"
	"unsafe"
)

var (
	procSHBrowseForFolderW  = shell32.NewProc("SHBrowseForFolderW")
	procSHGetPathFromIDList = shell32.NewProc("SHGetPathFromIDListW")
	procCoTaskMemFree       = ole32.NewProc("CoTaskMemFree")
)

type browseInfoW struct {
	hwndOwner      uintptr
	pidlRoot       uintptr
	pszDisplayName *uint16
	lpszTitle      *uint16
	ulFlags        uint32
	lpfn           uintptr
	lParam         uintptr
	iImage         int32
}

const (
	bifReturnOnlyFSDirs = 0x0001 // só pasta de verdade — nada de "Meu Computador"
	bifNewDialogStyle   = 0x0040 // caixa redimensionável e com o botão Nova Pasta
	bifEditBox          = 0x0010 // deixa digitar o caminho em vez de só navegar
)

// EscolhePasta abre a caixa do Windows e devolve a pasta escolhida.
//
// Devolve `"", false` quando o jogador cancela — que NÃO é erro, e é por isso
// que a assinatura não tem `error`: quem chama volta a mostrar a tela anterior
// com o valor que já estava lá.
func EscolhePasta(dono uintptr, titulo string) (string, bool) {
	// A caixa é COM por dentro, e precisa da thread inicializada. Sem isto ela
	// abre mesmo assim na maioria das máquinas, e falha nas outras — o tipo de
	// diferença que só aparece no computador de um jogador.
	hr, _, _ := procCoInitializeEx.Call(0, 0x2)
	if !falhou(hr) {
		defer procCoUninitialize.Call()
	}

	titulo16, err := syscall.UTF16PtrFromString(titulo)
	if err != nil {
		return "", false
	}
	nome := make([]uint16, maxPath)
	bi := browseInfoW{
		hwndOwner:      dono,
		pszDisplayName: &nome[0],
		lpszTitle:      titulo16,
		ulFlags:        bifReturnOnlyFSDirs | bifNewDialogStyle | bifEditBox,
	}

	pidl, _, _ := procSHBrowseForFolderW.Call(uintptr(unsafe.Pointer(&bi)))
	if pidl == 0 {
		return "", false // cancelou
	}
	// O PIDL é memória do shell, e quem a libera é o CoTaskMemFree. Esquecer
	// isso vaza alguns bytes por abertura — inofensivo aqui, e ainda assim
	// errado o bastante para não deixar passar.
	defer procCoTaskMemFree.Call(pidl)

	caminho := make([]uint16, maxPath)
	r, _, _ := procSHGetPathFromIDList.Call(pidl, uintptr(unsafe.Pointer(&caminho[0])))
	if r == 0 {
		return "", false
	}
	return syscall.UTF16ToString(caminho), true
}
