// Lançar o jogo — que não é um `exec.Command`, e a diferença tem nome.
//
// O `GuerraDoEmperium.exe` PEDE ELEVAÇÃO. Não é escolha nossa: o cliente de
// Ragnarok guarda a configuração de vídeo e som em
// `HKLM\SOFTWARE\WOW6432Node\Gravity Soft\Ragnarok`, e `HKEY_LOCAL_MACHINE`
// não se escreve sem privilégio. O manifesto do exe reflete isso.
//
// E o `exec.Command(...).Start()` do Go usa `CreateProcess`, que **não sabe
// elevar**: diante de um exe que exige privilégio ele falha com
// `ERROR_ELEVATION_REQUIRED` em vez de mostrar o UAC. O erro chega ao jogador
// como `fork/exec …: The requested operation requires elevation`, que é
// verdade e não ajuda ninguém.
//
// Quem sabe elevar é o `ShellExecuteW`: ele consulta o manifesto, levanta o
// UAC quando precisa, e o jogador vê a caixa de sempre do Windows.
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"syscall"
	"unsafe"
)

var procShellExecuteW = shell32.NewProc("ShellExecuteW")

const swShowNormal = 1

// Abaixo de 33 o retorno do ShellExecute é código de erro — a API é dos anos
// 90 e devolve "sucesso" como um HINSTANCE que ninguém usa.
const shellExecuteOK = 32

// Executa lança um programa pelo shell, a partir de `diretorio`.
//
// O verbo é vazio (o padrão, equivalente a dar duplo clique) e NÃO `runas`:
// com o padrão, quem decide se há elevação é o manifesto do programa. Forçar
// `runas` faria o UAC aparecer mesmo para quem não precisa dele.
func Executa(caminho, diretorio string) error {
	if _, err := os.Stat(caminho); err != nil {
		return fmt.Errorf("não encontrei %s", filepath.Base(caminho))
	}
	arquivo16, err := syscall.UTF16PtrFromString(caminho)
	if err != nil {
		return err
	}
	dir16, err := syscall.UTF16PtrFromString(diretorio)
	if err != nil {
		return err
	}

	r, _, errno := procShellExecuteW.Call(
		0, // sem janela dona: o Atualizador vai fechar em seguida
		0, // verbo padrão
		uintptr(unsafe.Pointer(arquivo16)),
		0, // sem argumentos
		uintptr(unsafe.Pointer(dir16)),
		swShowNormal,
	)
	if r > shellExecuteOK {
		return nil
	}

	// SE_ERR_ACCESSDENIED (5) é o que sai quando o jogador clica "Não" no UAC.
	// Dizer "acesso negado" ali seria acusar o Windows de um erro que foi uma
	// escolha da pessoa — e ela precisa saber que a escolha impede o jogo.
	if r == 5 {
		return fmt.Errorf("o Windows precisa de permissão para abrir o jogo")
	}
	return fmt.Errorf("não consegui abrir %s (código %d, %v)",
		filepath.Base(caminho), r, errno)
}

// A versão que ESPERA o programa fechar. O `ShellExecuteW` simples não dá o
// handle do processo; o `ShellExecuteExW` dá, com a máscara certa.
var (
	procShellExecuteExW     = shell32.NewProc("ShellExecuteExW")
	procWaitForSingleObject = kernel32.NewProc("WaitForSingleObject")
	procCloseHandleExecuta  = kernel32.NewProc("CloseHandle")
)

const (
	seeMaskNoCloseProcess = 0x00000040
	infinito              = 0xFFFFFFFF
)

type shellExecuteInfoW struct {
	cbSize         uint32
	fMask          uint32
	hwnd           uintptr
	lpVerb         *uint16
	lpFile         *uint16
	lpParameters   *uint16
	lpDirectory    *uint16
	nShow          int32
	hInstApp       uintptr
	lpIDList       uintptr
	lpClass        *uint16
	hkeyClass      uintptr
	dwHotKey       uint32
	hIconOrMonitor uintptr
	hProcess       uintptr
}

// ExecutaEEspera lança um programa e só volta quando ele fecha.
//
// Existe para o `Setup.exe`: ele precisa terminar ANTES de o jogo abrir, senão
// o cliente lê o registro que o Setup ainda não escreveu. Quem chamar isto tem
// de estar numa goroutine — a thread da janela não pode bloquear, ou o Windows
// marca o Atualizador como "não respondendo".
func ExecutaEEspera(caminho, diretorio string) error {
	if _, err := os.Stat(caminho); err != nil {
		return fmt.Errorf("não encontrei %s", filepath.Base(caminho))
	}
	arquivo16, err := syscall.UTF16PtrFromString(caminho)
	if err != nil {
		return err
	}
	dir16, err := syscall.UTF16PtrFromString(diretorio)
	if err != nil {
		return err
	}

	info := shellExecuteInfoW{
		fMask:       seeMaskNoCloseProcess,
		lpFile:      arquivo16,
		lpDirectory: dir16,
		nShow:       swShowNormal,
	}
	info.cbSize = uint32(unsafe.Sizeof(info))

	r, _, errno := procShellExecuteExW.Call(uintptr(unsafe.Pointer(&info)))
	if r == 0 {
		return fmt.Errorf("não consegui abrir %s (%v)", filepath.Base(caminho), errno)
	}
	if info.hProcess == 0 {
		// Abriu, mas sem handle — nada a esperar. Acontece quando o shell
		// entrega a um processo já em execução.
		return nil
	}
	defer procCloseHandleExecuta.Call(info.hProcess)
	procWaitForSingleObject.Call(info.hProcess, infinito)
	return nil
}
