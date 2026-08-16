// O atalho da Área de Trabalho — a última coisa que a instalação faz, e a
// única que sai da pasta do jogo.
//
// Um `.lnk` do Windows é um formato binário documentado (MS-SHLLINK), e dava
// para escrevê-lo byte a byte. Não é o que fazemos: o formato tem campos que
// dependem do volume e do caminho relativo, e um `.lnk` malformado não dá erro
// — ele simplesmente não abre nada quando o jogador clica. A API oficial monta
// isso certo, e o custo é este arquivo.
//
// Zero dependência externa, como o resto do Atualizador: `ole32.dll` e
// `shell32.dll` chamados por `syscall`.
//
// As vtables são declaradas como STRUCT e não percorridas por índice. Custa
// vinte linhas a mais e paga duas vezes: o `go vet` para de acusar aritmética
// de ponteiro sobre `unsafe.Pointer` (que aqui seria segura, mas o aviso é
// indistinguível de um caso em que não é), e cada método passa a ter nome. Um
// índice errado numa vtable chama outro método com os mesmos argumentos — o
// que trava o processo em vez de devolver erro, e a pilha aponta para dentro
// do shell do Windows.
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"syscall"
	"unsafe"
)

var (
	ole32                = syscall.NewLazyDLL("ole32.dll")
	procCoInitializeEx   = ole32.NewProc("CoInitializeEx")
	procCoUninitialize   = ole32.NewProc("CoUninitialize")
	procCoCreateInstance = ole32.NewProc("CoCreateInstance")

	shell32              = syscall.NewLazyDLL("shell32.dll")
	procSHGetFolderPathW = shell32.NewProc("SHGetFolderPathW")
)

// guid é o layout do GUID do Windows: três campos numéricos e oito bytes
// crus. Escrever isso como string e converter na hora seria mais legível e
// mais fácil de errar em silêncio.
type guid struct {
	Data1 uint32
	Data2 uint16
	Data3 uint16
	Data4 [8]byte
}

var (
	clsidShellLink  = guid{0x00021401, 0, 0, [8]byte{0xC0, 0, 0, 0, 0, 0, 0, 0x46}}
	iidIShellLinkW  = guid{0x000214F9, 0, 0, [8]byte{0xC0, 0, 0, 0, 0, 0, 0, 0x46}}
	iidIPersistFile = guid{0x0000010B, 0, 0, [8]byte{0xC0, 0, 0, 0, 0, 0, 0, 0x46}}
	// A terceira interface do mesmo objeto, e a única que sabe marcar um
	// atalho como "Executar como administrador".
	iidIShellLinkDataList = guid{0x45E2B4AE, 0xB1C3, 0x11D0,
		[8]byte{0xB9, 0x2F, 0x00, 0xA0, 0xC9, 0x03, 0x12, 0xE1}}
)

// SLDF_RUNAS_USER é o bit de "Executar como administrador" na caixa de
// propriedades do atalho. Ele importa aqui porque o cliente de Ragnarok
// escreve a configuração de vídeo em `HKEY_LOCAL_MACHINE`, que não aceita
// escrita sem privilégio — ver `video.go`. Sem o bit, o jogador teria de
// lembrar de clicar com o botão direito toda vez.
const sldfRunAsUser = 0x00002000

// Toda interface COM começa pelos três do IUnknown, nesta ordem. A ORDEM é o
// contrato — ela vem do cabeçalho C e não pode ser reorganizada por gosto.
type iUnknownVtbl struct {
	QueryInterface uintptr
	AddRef         uintptr
	Release        uintptr
}

type iShellLinkWVtbl struct {
	iUnknownVtbl
	GetPath             uintptr
	GetIDList           uintptr
	SetIDList           uintptr
	GetDescription      uintptr
	SetDescription      uintptr
	GetWorkingDirectory uintptr
	SetWorkingDirectory uintptr
	GetArguments        uintptr
	SetArguments        uintptr
	GetHotkey           uintptr
	SetHotkey           uintptr
	GetShowCmd          uintptr
	SetShowCmd          uintptr
	GetIconLocation     uintptr
	SetIconLocation     uintptr
	SetRelativePath     uintptr
	Resolve             uintptr
	SetPath             uintptr
}

type iShellLinkW struct{ vtbl *iShellLinkWVtbl }

type iPersistFileVtbl struct {
	iUnknownVtbl
	GetClassID    uintptr
	IsDirty       uintptr
	Load          uintptr
	Save          uintptr
	SaveCompleted uintptr
	GetCurFile    uintptr
}

type iPersistFile struct{ vtbl *iPersistFileVtbl }

type iShellLinkDataListVtbl struct {
	iUnknownVtbl
	AddDataBlock    uintptr
	CopyDataBlock   uintptr
	RemoveDataBlock uintptr
	GetFlags        uintptr
	SetFlags        uintptr
}

type iShellLinkDataList struct{ vtbl *iShellLinkDataListVtbl }

// chama é a mecânica de toda chamada COM: o primeiro argumento é sempre o
// próprio objeto (o `this` do C++).
func chama(fn uintptr, obj unsafe.Pointer, args ...uintptr) uintptr {
	r, _, _ := syscall.SyscallN(fn, append([]uintptr{uintptr(obj)}, args...)...)
	return r
}

func (o *iShellLinkW) Release() {
	chama(o.vtbl.Release, unsafe.Pointer(o))
}

func (o *iShellLinkW) SetPath(p *uint16) uintptr {
	return chama(o.vtbl.SetPath, unsafe.Pointer(o), uintptr(unsafe.Pointer(p)))
}

func (o *iShellLinkW) SetWorkingDirectory(p *uint16) uintptr {
	return chama(o.vtbl.SetWorkingDirectory, unsafe.Pointer(o), uintptr(unsafe.Pointer(p)))
}

func (o *iShellLinkW) SetDescription(p *uint16) uintptr {
	return chama(o.vtbl.SetDescription, unsafe.Pointer(o), uintptr(unsafe.Pointer(p)))
}

func (o *iShellLinkW) SetIconLocation(p *uint16, indice int32) uintptr {
	return chama(o.vtbl.SetIconLocation, unsafe.Pointer(o),
		uintptr(unsafe.Pointer(p)), uintptr(indice))
}

// QueryPersistFile pede ao mesmo objeto a outra interface dele: o IShellLink
// descreve o atalho, o IPersistFile o põe em disco.
func (o *iShellLinkW) QueryPersistFile() (*iPersistFile, uintptr) {
	var ppf *iPersistFile
	r := chama(o.vtbl.QueryInterface, unsafe.Pointer(o),
		uintptr(unsafe.Pointer(&iidIPersistFile)),
		uintptr(unsafe.Pointer(&ppf)))
	return ppf, r
}

// QueryDataList pede a interface que sabe ler e escrever os bits do atalho.
func (o *iShellLinkW) QueryDataList() (*iShellLinkDataList, uintptr) {
	var pdl *iShellLinkDataList
	r := chama(o.vtbl.QueryInterface, unsafe.Pointer(o),
		uintptr(unsafe.Pointer(&iidIShellLinkDataList)),
		uintptr(unsafe.Pointer(&pdl)))
	return pdl, r
}

func (o *iShellLinkDataList) Release() {
	chama(o.vtbl.Release, unsafe.Pointer(o))
}

// MarcaComoAdministrador liga o SLDF_RUNAS_USER preservando o que já estava
// ligado. Sobrescrever os flags em vez de acrescentar apagaria o que o
// IShellLink montou até aqui — e isso não daria erro, só produziria um atalho
// pela metade.
func (o *iShellLinkDataList) MarcaComoAdministrador() uintptr {
	var flags uint32
	if r := chama(o.vtbl.GetFlags, unsafe.Pointer(o),
		uintptr(unsafe.Pointer(&flags))); falhou(r) {
		return r
	}
	return chama(o.vtbl.SetFlags, unsafe.Pointer(o), uintptr(flags|sldfRunAsUser))
}

func (o *iPersistFile) Release() {
	chama(o.vtbl.Release, unsafe.Pointer(o))
}

// Save grava o `.lnk`. O `lembrar` é o `fRemember` da API: guarda o caminho
// como o arquivo atual do objeto. Não muda o resultado em disco, e é o que a
// documentação da Microsoft usa no exemplo.
func (o *iPersistFile) Save(p *uint16, lembrar bool) uintptr {
	var f uintptr
	if lembrar {
		f = 1
	}
	return chama(o.vtbl.Save, unsafe.Pointer(o), uintptr(unsafe.Pointer(p)), f)
}

// CSIDL da pasta que queremos. `DESKTOPDIRECTORY` é a Área de Trabalho DESTE
// usuário — existe também a de "todos os usuários", que exigiria privilégio de
// administrador e poria o atalho na tela de gente que não instalou nada.
const (
	csidlDesktop     = 0x0010
	shgfpTypeCurrent = 0
	maxPath          = 260
)

// falhou traduz o HRESULT: negativo é erro, e o resto (inclusive S_FALSE) não.
func falhou(hr uintptr) bool { return int32(hr) < 0 }

// AreaDeTrabalho devolve a pasta da Área de Trabalho do usuário atual.
//
// Não se monta esse caminho com `%USERPROFILE%\Desktop`: quem tem OneDrive
// ativo, ou Windows em outro idioma, tem a Área de Trabalho em outro lugar — e
// o atalho iria para uma pasta que ninguém olha, sem erro nenhum.
func AreaDeTrabalho() (string, error) {
	buf := make([]uint16, maxPath)
	r, _, _ := procSHGetFolderPathW.Call(0, csidlDesktop, 0, shgfpTypeCurrent,
		uintptr(unsafe.Pointer(&buf[0])))
	if falhou(r) {
		return "", fmt.Errorf("não encontrei a Área de Trabalho (0x%x)", r)
	}
	return syscall.UTF16ToString(buf), nil
}

// CriaAtalho escreve um `.lnk` apontando para `alvo`.
//
// O `diretorio` vira o "Iniciar em" do atalho, e ele NÃO é opcional aqui: o
// cliente de Ragnarok resolve `data\`, `System\` e o GRF a partir do diretório
// de trabalho, então um atalho sem isso abre o jogo sem nada do que é nosso —
// exatamente a mesma armadilha que o `jogar()` do main.go já documenta.
func CriaAtalho(destino, alvo, diretorio, descricao string) error {
	// COM é ligado por thread, e uma goroutine pode trocar de thread do SO no
	// meio da função. Sem travar, o `CoCreateInstance` roda numa thread e o
	// `Save` pode acabar noutra, que nunca foi inicializada — e aí falha com um
	// código que não diz nada sobre threads.
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()

	// COINIT_APARTMENTTHREADED. S_FALSE (0x1) quer dizer "já estava
	// inicializado nesta thread", que é sucesso — e mesmo assim exige o
	// CoUninitialize correspondente.
	hr, _, _ := procCoInitializeEx.Call(0, 0x2)
	if !falhou(hr) {
		defer procCoUninitialize.Call()
	}

	var psl *iShellLinkW
	hr, _, _ = procCoCreateInstance.Call(
		uintptr(unsafe.Pointer(&clsidShellLink)),
		0,
		1, // CLSCTX_INPROC_SERVER
		uintptr(unsafe.Pointer(&iidIShellLinkW)),
		uintptr(unsafe.Pointer(&psl)),
	)
	if falhou(hr) || psl == nil {
		return fmt.Errorf("não consegui criar o atalho (0x%x)", hr)
	}
	defer psl.Release()

	alvo16, err := syscall.UTF16PtrFromString(alvo)
	if err != nil {
		return err
	}
	dir16, err := syscall.UTF16PtrFromString(diretorio)
	if err != nil {
		return err
	}
	desc16, err := syscall.UTF16PtrFromString(descricao)
	if err != nil {
		return err
	}

	if hr := psl.SetPath(alvo16); falhou(hr) {
		return fmt.Errorf("SetPath falhou (0x%x)", hr)
	}
	if hr := psl.SetWorkingDirectory(dir16); falhou(hr) {
		return fmt.Errorf("SetWorkingDirectory falhou (0x%x)", hr)
	}
	// A descrição é a dica que aparece ao parar o mouse em cima. O ícone vem do
	// próprio exe (índice 0), que já tem o nosso embutido pelo .syso — o
	// Windows faria isso sozinho na maioria dos casos, mas explícito é barato e
	// evita o ícone genérico quando o cache do shell se perde. Nenhum dos dois
	// é motivo para desistir do atalho, então o retorno não é conferido.
	psl.SetDescription(desc16)
	psl.SetIconLocation(alvo16, 0)

	// O atalho pede elevação, e isso vale para o Atualizador inteiro: o jogo
	// que ele lança HERDA o token elevado, então o jogador vê um UAC só, ao
	// abrir, em vez de um segundo no meio do caminho quando clica em JOGAR.
	//
	// Falhar aqui não invalida o atalho — ele continua abrindo o jogo, só sem
	// privilégio, que é exatamente a situação de quem não tem esta linha.
	if pdl, hr := psl.QueryDataList(); !falhou(hr) && pdl != nil {
		if hr := pdl.MarcaComoAdministrador(); falhou(hr) {
			anota("atalho: não consegui marcar como administrador (0x%x)", hr)
		}
		pdl.Release()
	}

	ppf, hr := psl.QueryPersistFile()
	if falhou(hr) || ppf == nil {
		return fmt.Errorf("QueryInterface(IPersistFile) falhou (0x%x)", hr)
	}
	defer ppf.Release()

	destino16, err := syscall.UTF16PtrFromString(destino)
	if err != nil {
		return err
	}
	if hr := ppf.Save(destino16, true); falhou(hr) {
		return fmt.Errorf("não consegui gravar %s (0x%x)", filepath.Base(destino), hr)
	}
	return nil
}

// AtalhoNaAreaDeTrabalho é o caso de uso completo: o atalho do jogo, com o
// nome que o jogador vai ler embaixo do ícone.
//
// Falhar aqui NÃO é motivo para a instalação falhar — o jogo está instalado e
// funcionando, e o que faltou foi um atalho. Quem chama decide, mas a intenção
// é essa: erro daqui vira aviso na tela, nunca interrupção.
func AtalhoNaAreaDeTrabalho(nome, alvo, diretorio, descricao string) (string, error) {
	mesa, err := AreaDeTrabalho()
	if err != nil {
		return "", err
	}
	destino := filepath.Join(mesa, nome+".lnk")
	// Um atalho velho apontando para outra pasta é pior que nenhum: o jogador
	// clica, o jogo abre do lugar errado, e nada explica por quê.
	os.Remove(destino)
	return destino, CriaAtalho(destino, alvo, diretorio, descricao)
}
