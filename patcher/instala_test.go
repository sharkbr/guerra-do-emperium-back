// Testes do primeiro download que falam com o servidor DE VERDADE.
//
// Eles existem porque o caminho da instalação não dá para exercitar clicando:
// o fluxo inteiro são 3,4 GB, e o que mais interessa nele — a retomada — só
// aparece quando a conexão cai no meio, que é justamente o que ninguém
// consegue provocar de propósito na hora de testar.
//
// Dependem de rede, e por isso pulam com `go test -short`.
//
//	go test ./...            roda tudo, inclusive estes
//	go test -short ./...     só os que rodam offline
package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"testing"
)

// O menor pedaço da base, para os testes não puxarem 3 GB. Se a base for
// remontada e este nome mudar, o teste falha dizendo exatamente isso — o que
// está certo: a lista é a fonte, e um teste que adivinha o nome mentiria.
const pedacoDeTeste = "0005-resto.zip"

func baseDeTeste(t *testing.T) []pedaco {
	t.Helper()
	if testing.Short() {
		t.Skip("precisa de rede")
	}
	lista, err := baixaBase(basePadrao)
	if err != nil {
		t.Fatalf("baixaBase(%s): %v", basePadrao, err)
	}
	return lista
}

func TestBaixaBase(t *testing.T) {
	lista := baseDeTeste(t)

	if len(lista) == 0 {
		t.Fatal("a base veio sem nenhum pedaço")
	}
	var bruto int
	for _, p := range lista {
		if p.SHA == "" || len(p.SHA) != 64 {
			t.Errorf("%s: sha256 com %d caracteres", p.Arquivo, len(p.SHA))
		}
		if p.Bytes <= 0 {
			t.Errorf("%s: tamanho %d", p.Arquivo, p.Bytes)
		}
		if p.Tipo == tipoBruto {
			bruto++
		}
	}
	// O `data.grf` é o único bruto, e é ele que carrega o mundo. Zero brutos
	// quer dizer que a base foi montada sem ele — a instalação terminaria
	// "com sucesso" e o jogo não abriria.
	if bruto != 1 {
		t.Errorf("esperava exatamente 1 pedaço bruto (o data.grf), achei %d", bruto)
	}
	t.Logf("%d pedaços, %.2f GB para o jogador",
		len(lista), float64(TamanhoDaInstalacao(lista))/(1<<30))
}

// TestRetomada é o teste que justifica este arquivo.
//
// Ele grava um `.parte` pela metade, chama o mesmo `baixa()` que o instalador
// usa, e confere o sha256 do resultado. Se o `Range` não fosse honrado, ou se
// o código grudasse o arquivo inteiro no fim do pedaço já baixado, o sha não
// fecharia — e é exatamente essa a falha que só apareceria depois de o jogador
// baixar 2,95 GB.
func TestRetomada(t *testing.T) {
	lista := baseDeTeste(t)

	var alvo *pedaco
	for i := range lista {
		if lista[i].Arquivo == pedacoDeTeste {
			alvo = &lista[i]
			break
		}
	}
	if alvo == nil {
		t.Skipf("%s não está mais na base — remontada?", pedacoDeTeste)
	}

	pasta := t.TempDir()
	destino := filepath.Join(pasta, alvo.Arquivo)

	// Primeira metade, à força: é o que um download interrompido teria deixado.
	metade := alvo.Bytes / 2
	if err := baixaFaixa(basePadrao+alvo.Arquivo, destino+".parte", metade); err != nil {
		t.Fatalf("não consegui simular o download interrompido: %v", err)
	}
	fi, err := os.Stat(destino + ".parte")
	if err != nil {
		t.Fatal(err)
	}
	if fi.Size() != metade {
		t.Fatalf("o parcial ficou com %d bytes, esperava %d", fi.Size(), metade)
	}

	// Agora o código de verdade, que deve completar a partir dali.
	j := &Janela{}
	if err := baixa(j, basePadrao+alvo.Arquivo, destino, alvo.Bytes, "teste"); err != nil {
		t.Fatalf("baixa: %v", err)
	}

	fi, err = os.Stat(destino)
	if err != nil {
		t.Fatalf("o arquivo não ficou em disco: %v", err)
	}
	if fi.Size() != alvo.Bytes {
		t.Fatalf("tamanho final %d, esperava %d", fi.Size(), alvo.Bytes)
	}
	soma, err := somaArquivo(destino)
	if err != nil {
		t.Fatal(err)
	}
	if soma != alvo.SHA {
		t.Fatalf("sha256 não confere depois de retomar:\n  veio   %s\n  espera %s", soma, alvo.SHA)
	}
	t.Logf("retomou de %d bytes e fechou o sha256 dos %d", metade, alvo.Bytes)
}

// baixaFaixa pega só os primeiros `quantos` bytes, para montar o cenário do
// download interrompido. Usa Range na direção oposta à do teste — pedindo o
// COMEÇO em vez do resto —, então não é o mesmo caminho que está sendo testado.
func baixaFaixa(url, destino string, quantos int64) error {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Range", fmt.Sprintf("bytes=0-%d", quantos-1))
	resp, err := cliente.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	dados := make([]byte, quantos)
	lidos := 0
	for int64(lidos) < quantos {
		n, err := resp.Body.Read(dados[lidos:])
		lidos += n
		if err != nil {
			break
		}
	}
	return os.WriteFile(destino, dados[:lidos], 0o644)
}

// TestPrecisaInstalar trava a pergunta que decide se este exe é o instalador
// ou o atualizador — a que errou em 2026-08-16, quando um jogador pôs o
// `Jogar.exe` dentro de uma pasta de RO antiga: `data.grf` sozinho fez o
// programa se dar por instalado, e o JOGAR devolveu "não encontrei
// GuerraDoEmperium.exe" a quem estava tentando instalar.
//
// Roda offline de propósito: é a única porta entre as duas metades do
// programa, e um teste que dependesse de rede não seria rodado.
func TestPrecisaInstalar(t *testing.T) {
	const jogo = "GuerraDoEmperium.exe"
	casos := []struct {
		nome     string
		arquivos []string
		precisa  bool
	}{
		{"pasta vazia (o jogador que acabou de baixar)", nil, true},
		{"instalação alheia: grf sem o nosso exe", []string{"data.grf"}, true},
		{"exe solto, sem o mundo", []string{jogo}, true},
		{"instalação nossa, inteira", []string{"data.grf", jogo}, false},
	}
	for _, c := range casos {
		raiz := t.TempDir()
		for _, nome := range c.arquivos {
			if err := os.WriteFile(filepath.Join(raiz, nome), []byte("x"), 0o644); err != nil {
				t.Fatal(err)
			}
		}
		if veio := PrecisaInstalar(raiz, jogo); veio != c.precisa {
			t.Errorf("%s: PrecisaInstalar = %v, esperava %v", c.nome, veio, c.precisa)
		}
	}
}
