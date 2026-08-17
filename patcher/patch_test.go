// Testes do registro de patches — o `patch\aplicados.txt`.
//
// Rodam OFFLINE, e é de propósito: este é o arquivo que decide o que o jogador
// recebe, e ele já errou uma vez de um jeito que nenhum teste de rede pegaria.
// Em 2026-08-17 todo cliente instalado tinha os PEDAÇOS DA BASE anotados no
// diário dos patches — o pedaço 0002 ("As musicas") ocupando o número do patch
// 0002 —, e o Atualizador pulava os patches 0002 e 0003 dizendo "cliente
// atualizado", com a barra cheia. O sintoma aparecia a três passos dali: item
// novo sem nome na loja, porque o `itemInfo.lua` do patch 0003 nunca chegou.
package main

import (
	"os"
	"path/filepath"
	"testing"
)

// faltam repete a decisão do `aplicaPatches`: é ela que este arquivo testa.
func faltam(aplicados map[int]string, lista []patch) []patch {
	var falta []patch
	for _, p := range lista {
		if aplicados[p.Numero] != p.SHA {
			falta = append(falta, p)
		}
	}
	return falta
}

func TestLeAplicados(t *testing.T) {
	trabalho := t.TempDir()

	// Arquivo ausente: nenhum patch aplicado. Reaplicar é barato; adivinhar
	// que já foi deixaria o jogador sem o conteúdo.
	if feitos := leAplicados(trabalho); len(feitos) != 0 {
		t.Fatalf("sem arquivo deveria dar vazio, deu %v", feitos)
	}

	p := patch{Numero: 3, Arquivo: "0003.zip", SHA: "abc123", Nome: "Itens novos"}
	if err := marcaAplicado(trabalho, p); err != nil {
		t.Fatalf("marcaAplicado: %v", err)
	}
	feitos := leAplicados(trabalho)
	if feitos[3] != "abc123" {
		t.Fatalf("esperava o sha do 3, veio %q", feitos[3])
	}
	if faltando := faltam(feitos, []patch{p}); len(faltando) != 0 {
		t.Fatalf("patch anotado não deveria faltar, faltou %v", faltando)
	}
}

// É O TESTE QUE IMPORTA: o registro sujo pelo instalador não pode calar patch.
func TestPedacoDaBaseNaoCalaPatch(t *testing.T) {
	trabalho := t.TempDir()

	// O estado exato de um cliente instalado em 2026-08-17: os pedaços da base
	// no diário dos patches, com os números 0002 a 0005 e os shas DELES.
	escrito := "# Patches aplicados neste cliente. Gerado pelo Atualizador.\n" +
		"0002\tddbebeaa\t2026-08-16 23:59\tAs musicas\n" +
		"0003\t2d7c9102\t2026-08-17 00:00\tA Guerra do Emperium (1 de 2)\n" +
		"0004\t1d57df90\t2026-08-17 00:00\tA Guerra do Emperium (2 de 2)\n" +
		"0005\t6a02f3c9\t2026-08-17 00:00\tO motor do jogo\n" +
		"0001\t921fabb6\t2026-08-17 00:00\tIA do homunculo e do mercenario\n"
	caminho := filepath.Join(trabalho, "aplicados.txt")
	if err := os.WriteFile(caminho, []byte(escrito), 0o644); err != nil {
		t.Fatal(err)
	}

	lista := []patch{
		{Numero: 1, SHA: "921fabb6", Nome: "IA do homunculo e do mercenario"},
		{Numero: 2, SHA: "23777341", Nome: "Sem censura de palavras"},
		{Numero: 3, SHA: "10f0b929", Nome: "Itens novos das lojas de Prontera"},
	}

	falta := faltam(leAplicados(trabalho), lista)
	if len(falta) != 2 {
		t.Fatalf("esperava faltar 0002 e 0003, faltaram %d: %v", len(falta), falta)
	}
	if falta[0].Numero != 2 || falta[1].Numero != 3 {
		t.Fatalf("faltaram os números errados: %v", falta)
	}

	// E depois de aplicados, o diário sujo não os traz de volta: a última
	// linha de cada número é que vale.
	for _, p := range falta {
		if err := marcaAplicado(trabalho, p); err != nil {
			t.Fatalf("marcaAplicado %04d: %v", p.Numero, err)
		}
	}
	if resto := faltam(leAplicados(trabalho), lista); len(resto) != 0 {
		t.Fatalf("depois de aplicar não deveria faltar nada, faltou %v", resto)
	}
}

// Linha sem sha (registro de uma versão antiga do Atualizador) não pode ser
// lida como "aplicado" nem derrubar a leitura do resto do arquivo.
func TestLinhaSemShaEIgnorada(t *testing.T) {
	trabalho := t.TempDir()
	escrito := "0002\n" + "0003\t10f0b929\t2026-08-17 00:00\tItens novos\n"
	if err := os.WriteFile(filepath.Join(trabalho, "aplicados.txt"),
		[]byte(escrito), 0o644); err != nil {
		t.Fatal(err)
	}
	feitos := leAplicados(trabalho)
	if _, tem := feitos[2]; tem {
		t.Fatalf("linha sem sha não deveria contar como aplicada: %v", feitos)
	}
	if feitos[3] != "10f0b929" {
		t.Fatalf("a linha boa depois dela deveria ser lida, veio %q", feitos[3])
	}
}
