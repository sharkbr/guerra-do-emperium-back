// O único teste automatizado do Atualizador, e ele existe por um motivo
// específico: o `atalho.go` chama COM percorrendo vtable, e ali um engano não
// devolve erro — trava o processo dentro do shell do Windows, com uma pilha
// que não aponta para o nosso código. É o tipo de coisa que se descobre na
// máquina do jogador, no meio da instalação, se ninguém provar antes.
//
//	go test ./...
package main

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"
)

// O cabeçalho de um `.lnk` válido: HeaderSize 0x4C e o CLSID do ShellLink,
// em little-endian. Conferir isso é o que separa "o arquivo foi criado" de "o
// arquivo é um atalho" — um `.lnk` de zero byte também existe em disco.
var cabecalhoLNK = []byte{
	0x4C, 0x00, 0x00, 0x00, // HeaderSize = 76
	0x01, 0x14, 0x02, 0x00, // CLSID_ShellLink, Data1
	0x00, 0x00, 0x00, 0x00, // Data2, Data3
	0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46, // Data4
}

func TestCriaAtalho(t *testing.T) {
	// O alvo tem de existir de verdade: o IShellLink resolve o caminho ao
	// gravar, e apontar para nada é justamente um dos casos em que ele grava
	// um atalho que não abre coisa nenhuma.
	alvo, err := os.Executable()
	if err != nil {
		t.Fatalf("não consegui descobrir o executável do teste: %v", err)
	}
	pasta := t.TempDir()
	destino := filepath.Join(pasta, "Guerra do Emperium.lnk")

	if err := CriaAtalho(destino, alvo, filepath.Dir(alvo), "Jogar Guerra do Emperium"); err != nil {
		t.Fatalf("CriaAtalho: %v", err)
	}

	dados, err := os.ReadFile(destino)
	if err != nil {
		t.Fatalf("o atalho não ficou em disco: %v", err)
	}
	if len(dados) < len(cabecalhoLNK) {
		t.Fatalf("atalho com %d bytes — curto demais para ser um .lnk", len(dados))
	}
	if !bytes.Equal(dados[:len(cabecalhoLNK)], cabecalhoLNK) {
		t.Fatalf("cabeçalho não é de .lnk: % x", dados[:len(cabecalhoLNK)])
	}

	// O caminho do alvo aparece no corpo do arquivo em UTF-16. Não é a leitura
	// formal da estrutura — é a checagem barata de que o SetPath pegou, que é o
	// campo cujo erro deixaria o atalho abrindo a coisa errada.
	var alvo16 []byte
	for _, r := range alvo {
		alvo16 = append(alvo16, byte(r), 0)
	}
	if !bytes.Contains(dados, alvo16) {
		t.Errorf("o caminho do alvo não aparece no .lnk — SetPath não pegou")
	}
}

// O bit "Executar como administrador" precisa chegar ao ARQUIVO, e não só à
// chamada COM que diz tê-lo posto. Sem ele o jogo abre sem privilégio e morre
// ao gravar a configuração de vídeo em HKEY_LOCAL_MACHINE — falha que só
// aparece na máquina de quem instalou, nunca aqui.
//
// No formato MS-SHLLINK os LinkFlags são o DWORD no offset 20, e
// SLDF_RUNAS_USER é 0x00002000 — ou seja o bit 0x20 do byte 21.
func TestAtalhoPedeAdministrador(t *testing.T) {
	alvo, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	destino := filepath.Join(t.TempDir(), "admin.lnk")
	if err := CriaAtalho(destino, alvo, filepath.Dir(alvo), "teste"); err != nil {
		t.Fatalf("CriaAtalho: %v", err)
	}
	dados, err := os.ReadFile(destino)
	if err != nil {
		t.Fatal(err)
	}
	if len(dados) < 24 {
		t.Fatalf("atalho com %d bytes", len(dados))
	}
	if dados[21]&0x20 == 0 {
		t.Errorf("o bit RunAsUser não está no arquivo (LinkFlags = % x)", dados[20:24])
	}
}

func TestVideoConfigurado(t *testing.T) {
	// Nesta máquina o jogo roda, logo o Setup.exe já rodou algum dia e a chave
	// existe. Se este teste falhar AQUI, a detecção está lendo o lugar errado —
	// e um falso negativo faria o instalador abrir o Setup para quem não
	// precisa.
	if !VideoConfigurado() {
		t.Error("VideoConfigurado() disse não numa máquina onde o jogo roda — " +
			"o caminho ou a flag WOW64 estão errados")
	}
}

func TestAreaDeTrabalhoExiste(t *testing.T) {
	// Se esta pasta não for encontrada, o atalho iria para um caminho vazio e a
	// instalação terminaria dizendo que criou um atalho que não existe.
	mesa, err := AreaDeTrabalho()
	if err != nil {
		t.Fatalf("AreaDeTrabalho: %v", err)
	}
	if mesa == "" {
		t.Fatal("AreaDeTrabalho devolveu caminho vazio")
	}
	if _, err := os.Stat(mesa); err != nil {
		t.Fatalf("a Área de Trabalho apontada não existe (%s): %v", mesa, err)
	}
}
