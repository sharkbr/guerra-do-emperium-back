// Testes do changelog — a leitura do `novidades.txt` e o texto que o botão
// copiar põe na área de transferência.
//
// Rodam OFFLINE, como os do registro. O que se testa aqui é a TOLERÂNCIA: este
// arquivo é o único do canal de patches que uma pessoa edita à mão depois de
// publicado, e uma leitura que desista na primeira linha torta apagaria o
// painel inteiro por causa de um traço fora do lugar.
package main

import (
	"os"
	"testing"
)

const exemplo = `# Guerra do Emperium - as novidades.
# Comentário e linha solta antes do primeiro bloco não entram.

[0019] 2026-09-06  Festival de Brasilis
- Quatro Ligas
- A Arena

[0020] 2026-09-06  Aviso da trava de conta
`

func TestLeNovidades(t *testing.T) {
	lista := leNovidades(exemplo)
	if len(lista) != 2 {
		t.Fatalf("esperava 2 blocos, vieram %d: %v", len(lista), lista)
	}

	// Do mais novo para o mais velho: o de cima do painel é o que acabou de
	// sair, e o arquivo é escrito na ordem contrária.
	if lista[0].Numero != 20 || lista[1].Numero != 19 {
		t.Fatalf("ordem errada: %d e %d", lista[0].Numero, lista[1].Numero)
	}
	if lista[1].Titulo != "Festival de Brasilis" {
		t.Fatalf("título errado: %q", lista[1].Titulo)
	}
	if len(lista[1].Pontos) != 2 || lista[1].Pontos[1] != "A Arena" {
		t.Fatalf("pontos errados: %v", lista[1].Pontos)
	}
	// Patch que só conserta algo não tem ponto nenhum, e isso é normal.
	if len(lista[0].Pontos) != 0 {
		t.Fatalf("o 0020 não deveria ter pontos: %v", lista[0].Pontos)
	}
}

// O arquivo é editado à mão: bloco sem data, ponto sem traço e cabeçalho torto
// não podem derrubar os blocos bons ao redor.
func TestLeNovidadesTolerante(t *testing.T) {
	lista := leNovidades("[0001] Sem data nenhuma\numa linha sem traço\n" +
		"[abc] cabeçalho torto\n- ponto órfão\n" +
		"[0002] 2026-09-06  Com data\n")
	if len(lista) != 2 {
		t.Fatalf("esperava os 2 blocos bons, vieram %d: %v", len(lista), lista)
	}
	semData := lista[1]
	if semData.Numero != 1 || semData.Data != "" || semData.Titulo != "Sem data nenhuma" {
		t.Fatalf("bloco sem data lido errado: %+v", semData)
	}
	if len(semData.Pontos) != 1 || semData.Pontos[0] != "uma linha sem traço" {
		t.Fatalf("linha sem traço deveria virar ponto: %v", semData.Pontos)
	}
	// O ponto órfão do cabeçalho recusado cai no bloco anterior, e não no
	// seguinte: é o que evita que um erro de digitação mude o dono de um item.
	if len(lista[0].Pontos) != 0 {
		t.Fatalf("o bloco de baixo não deveria herdar ponto: %v", lista[0].Pontos)
	}
}

// A mensagem é o produto de verdade deste arquivo: é ela que vai para o grupo.
func TestMensagem(t *testing.T) {
	n := novidade{Numero: 21, Data: "2026-09-06", Titulo: "Cinco chapéus novos",
		Pontos: []string{"Chapéu de Palha", "Tiara de Prata"}}
	esperado := "LibraRO updates 06/09/2026\n\nCinco chapéus novos\n" +
		"- Chapéu de Palha\n- Tiara de Prata"
	if got := n.mensagem(); got != esperado {
		t.Fatalf("mensagem errada:\n%s\n--- esperava ---\n%s", got, esperado)
	}

	// Sem data o cabeçalho não pode sair com um espaço pendurado no fim — é o
	// que aconteceria com um `Sprintf` de campo sempre presente.
	sem := novidade{Numero: 1, Titulo: "Sem data"}
	if got := sem.mensagem(); got != "LibraRO updates\n\nSem data" {
		t.Fatalf("mensagem sem data errada: %q", got)
	}
}

// O arquivo DE VERDADE, o que vai para o servidor. Ele é editado à mão, e um
// bloco que a leitura recusa some do painel sem dizer nada a ninguém — aqui,
// pelo menos, o teste quebra antes de publicar.
func TestArquivoDoRepositorio(t *testing.T) {
	dados, err := os.ReadFile("novidades.txt")
	if err != nil {
		t.Fatalf("patcher/novidades.txt: %v", err)
	}
	lista := leNovidades(string(dados))
	if len(lista) < 20 {
		t.Fatalf("esperava pelo menos os 20 patches já publicados, li %d", len(lista))
	}
	vistos := map[int]bool{}
	for _, n := range lista {
		if n.Numero == 0 || n.Titulo == "" {
			t.Fatalf("bloco sem número ou sem título: %+v", n)
		}
		if vistos[n.Numero] {
			t.Fatalf("o patch %04d aparece duas vezes", n.Numero)
		}
		vistos[n.Numero] = true
		// Data ausente passa na leitura, mas não no arquivo nosso: sem ela a
		// mensagem do grupo sai sem o dia, que é justamente o que ela carrega.
		if len(n.Data) != 10 {
			t.Fatalf("o patch %04d está sem data: %+v", n.Numero, n)
		}
	}
}

// Sem `novidades.txt` no servidor, o painel ainda tem o que mostrar.
func TestDeLista(t *testing.T) {
	lista := deLista([]patch{
		{Numero: 1, Nome: "IA do homunculo"},
		{Numero: 2, Nome: "Sem censura de palavras"},
	})
	if len(lista) != 2 || lista[0].Numero != 2 {
		t.Fatalf("reserva errada: %+v", lista)
	}
	if lista[0].Data != "" || len(lista[0].Pontos) != 0 {
		t.Fatalf("a reserva não inventa data nem pontos: %+v", lista[0])
	}
	// E a mensagem continua copiável, só que sem data no cabeçalho.
	if got := lista[0].mensagem(); got != "LibraRO updates\n\nSem censura de palavras" {
		t.Fatalf("mensagem da reserva errada: %q", got)
	}
}
