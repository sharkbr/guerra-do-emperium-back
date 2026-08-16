// O patch: baixar a lista, baixar o zip, conferir o sha256 e extrair por cima
// da pasta do cliente.
//
// Não há diff binário e não há GRF. O cliente tem `DataFolderFirst`, então
// arquivo solto em `cliente\data\` vence o `data.grf` — é assim que todo o
// nosso conteúdo já chega hoje, e um zip extraído por cima é exatamente a
// mesma coisa. A consequência boa é que aplicar duas vezes não faz diferença:
// apagar `patch\aplicados.txt` reaplica tudo e o cliente fica igual.
package main

import (
	"archive/zip"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// arquivoApagar é a lista de exclusões que pode vir dentro do zip. Ver
// `ferramentas/monta_patch.py`, constante APAGAR — os dois lados têm de
// concordar no nome, e este é o acoplamento.
const arquivoApagar = "_patch_apagar.txt"

type patch struct {
	Numero  int
	Arquivo string
	SHA     string
	Bytes   int64
	Nome    string
}

var cliente = &http.Client{Timeout: 30 * time.Minute}

// baixaLista lê o `lista.txt` do servidor — que é o `patcher/patches.txt` do
// repositório, publicado sem tradução. Uma linha por patch, cinco campos
// separados por TAB, `#` comenta.
//
// Linha malformada é ERRO e não linha pulada, de propósito: pular deixaria o
// cliente do jogador em um estado que ninguém consegue reproduzir aqui.
// baixaTexto pega um arquivo pequeno de texto do servidor: a lista de patches
// ou a base da instalação.
//
// O `LimitReader` não é paranoia: sem ele, um servidor mal configurado
// devolvendo o corpo errado — uma página de erro de 400 MB, um arquivo trocado
// — seria lido inteiro para a memória de uma máquina de jogador.
func baixaTexto(url string) (string, error) {
	resp, err := cliente.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return "", fmt.Errorf("%s respondeu %s", path.Base(url), resp.Status)
	}
	dados, err := io.ReadAll(io.LimitReader(resp.Body, 4<<20))
	if err != nil {
		return "", err
	}
	return string(dados), nil
}

func baixaLista(url string) ([]patch, error) {
	dados, err := baixaTexto(url + "lista.txt")
	if err != nil {
		return nil, err
	}

	var lista []patch
	for n, linha := range strings.Split(dados, "\n") {
		linha = strings.TrimRight(linha, "\r")
		if strings.TrimSpace(linha) == "" || strings.HasPrefix(strings.TrimSpace(linha), "#") {
			continue
		}
		campos := strings.Split(linha, "\t")
		if len(campos) != 5 {
			return nil, fmt.Errorf("lista.txt linha %d: %d campos", n+1, len(campos))
		}
		numero, err := strconv.Atoi(strings.TrimSpace(campos[0]))
		if err != nil {
			return nil, fmt.Errorf("lista.txt linha %d: número inválido", n+1)
		}
		bytes, err := strconv.ParseInt(strings.TrimSpace(campos[3]), 10, 64)
		if err != nil {
			return nil, fmt.Errorf("lista.txt linha %d: tamanho inválido", n+1)
		}
		lista = append(lista, patch{numero, campos[1], strings.TrimSpace(campos[2]), bytes, campos[4]})
	}
	return lista, nil
}

// leAplicados devolve os números que este cliente já tem. Arquivo ausente ou
// ilegível quer dizer "nenhum" — e isso está certo: reaplicar é barato e correto,
// enquanto adivinhar que já foi aplicado deixaria o jogador sem o conteúdo.
func leAplicados(trabalho string) map[int]bool {
	feitos := map[int]bool{}
	dados, err := os.ReadFile(filepath.Join(trabalho, "aplicados.txt"))
	if err != nil {
		return feitos
	}
	for _, linha := range strings.Split(string(dados), "\n") {
		linha = strings.TrimSpace(linha)
		if linha == "" || strings.HasPrefix(linha, "#") {
			continue
		}
		if numero, err := strconv.Atoi(strings.Split(linha, "\t")[0]); err == nil {
			feitos[numero] = true
		}
	}
	return feitos
}

func marcaAplicado(trabalho string, p patch) error {
	caminho := filepath.Join(trabalho, "aplicados.txt")
	novo := !existe(caminho)
	f, err := os.OpenFile(caminho, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	if novo {
		fmt.Fprintf(f, "# Patches aplicados neste cliente. Gerado pelo Atualizador.\n")
		fmt.Fprintf(f, "# Apagar este arquivo faz tudo ser baixado e aplicado de novo.\n")
	}
	_, err = fmt.Fprintf(f, "%04d\t%s\t%s\t%s\n", p.Numero, p.SHA,
		time.Now().Format("2006-01-02 15:04"), p.Nome)
	return err
}

// aplica baixa, confere e extrai um patch. O zip vai para disco antes de ser
// aberto — patch de arte passa dos 200 MB, e segurar isso em memória numa
// máquina de jogador é pedir para o Atualizador morrer justo no fim.
func aplica(j *Janela, raiz, trabalho, url string, p patch, rotulo string) error {
	zipado := filepath.Join(trabalho, p.Arquivo)

	// Um zip já em disco com o sha certo é download interrompido que chegou
	// inteiro, ou reaplicação — nos dois casos, não se baixa de novo.
	if soma, err := somaArquivo(zipado); err != nil || soma != p.SHA {
		j.Status(rotulo + " — baixando…")
		if err := baixa(j, url+p.Arquivo, zipado, p.Bytes, rotulo); err != nil {
			return err
		}
		soma, err := somaArquivo(zipado)
		if err != nil {
			return err
		}
		if soma != p.SHA {
			// Arquivo corrompido no caminho, ou trocado. Some com ele: deixar
			// para trás faria a próxima tentativa achar que já tem o patch.
			os.Remove(zipado)
			return fmt.Errorf("o arquivo baixado não confere (sha256)")
		}
	}

	j.Status(rotulo + " — aplicando…")
	if err := extrai(j, zipado, raiz, rotulo); err != nil {
		return err
	}
	if err := marcaAplicado(trabalho, p); err != nil {
		return err
	}
	os.Remove(zipado) // o zip já cumpriu o papel; não ocupa disco do jogador
	return nil
}

// baixa grava a URL em `destino`, RETOMANDO de onde parou se houver um
// download interrompido em disco.
//
// A retomada não é luxo: o `data.grf` da instalação tem 2,95 GB, e sem ela uma
// queda de conexão aos 90% joga fora quase três gigabytes. Num patch de 40 KB
// isso não faria diferença nenhuma; foi o instalador que trouxe a necessidade.
//
// A mecânica é o cabeçalho `Range: bytes=N-`, e o cuidado está na resposta:
//
//	206 Partial Content  o servidor honrou — o corpo continua de onde parou
//	200 OK               o servidor IGNOROU — está mandando o arquivo inteiro
//
// O 200 é o caso que engana. Tratá-lo como continuação grudaria o arquivo
// inteiro no fim do pedaço já baixado: sairia um arquivo maior que o original,
// com o sha errado, e a falha só apareceria no FIM — depois de o jogador
// baixar tudo de novo. Por isso o 200 descarta o que havia e recomeça.
func baixa(j *Janela, url, destino string, tamanho int64, rotulo string) error {
	parcial := destino + ".parte"

	var jaTem int64
	if fi, err := os.Stat(parcial); err == nil {
		jaTem = fi.Size()
	}
	// Parcial do tamanho final ou maior é resto de uma rodada anterior, ou de
	// um arquivo que mudou no servidor. Não há o que retomar — e quem decide se
	// o resultado presta é o sha256, mais adiante.
	if tamanho > 0 && jaTem >= tamanho {
		jaTem = 0
	}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}
	if jaTem > 0 {
		req.Header.Set("Range", fmt.Sprintf("bytes=%d-", jaTem))
	}

	resp, err := cliente.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	switch resp.StatusCode {
	case http.StatusPartialContent: // 206: continua de onde parou
	case http.StatusOK: // 200: veio inteiro, o que já tínhamos não serve
		jaTem = 0
	default:
		return fmt.Errorf("%s respondeu %s", path.Base(url), resp.Status)
	}

	// O modo de abertura segue a resposta, e não o pedido: APPEND quando o
	// servidor confirmou a continuação, truncar quando não.
	modo := os.O_CREATE | os.O_WRONLY | os.O_TRUNC
	if jaTem > 0 {
		modo = os.O_CREATE | os.O_WRONLY | os.O_APPEND
	}
	f, err := os.OpenFile(parcial, modo, 0o644)
	if err != nil {
		return err
	}

	buf := make([]byte, 256<<10)
	lidos := jaTem
	ultimo := time.Now()
	for {
		n, err := resp.Body.Read(buf)
		if n > 0 {
			if _, erroGravar := f.Write(buf[:n]); erroGravar != nil {
				f.Close()
				return erroGravar
			}
			lidos += int64(n)
			// Repintar a cada 100 ms: a barra anda igual e o Windows não fica
			// processando mensagem de janela no lugar de baixar.
			if tamanho > 0 && time.Since(ultimo) > 100*time.Millisecond {
				ultimo = time.Now()
				j.Progresso(int(lidos * 100 / tamanho))
				j.Status(fmt.Sprintf("%s — baixando %.1f de %.1f MB",
					rotulo, float64(lidos)/1048576, float64(tamanho)/1048576))
			}
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			f.Close()
			return err
		}
	}
	if err := f.Close(); err != nil {
		return err
	}
	return os.Rename(parcial, destino)
}

func extrai(j *Janela, zipado, raiz, rotulo string) error {
	r, err := zip.OpenReader(zipado)
	if err != nil {
		return err
	}
	defer r.Close()

	// A lista de exclusões é lida antes de qualquer escrita: se ela estiver
	// corrompida, nada foi tocado ainda.
	var apagar []string
	for _, f := range r.File {
		if f.Name == arquivoApagar {
			texto, err := leDoZip(f)
			if err != nil {
				return err
			}
			for _, linha := range strings.Split(texto, "\n") {
				if linha = strings.TrimSpace(linha); linha != "" {
					apagar = append(apagar, linha)
				}
			}
		}
	}

	total := len(r.File)
	for i, f := range r.File {
		if f.Name == arquivoApagar || f.FileInfo().IsDir() {
			continue
		}
		destino, err := destinoSeguro(raiz, f.Name)
		if err != nil {
			return err
		}
		if err := os.MkdirAll(filepath.Dir(destino), 0o755); err != nil {
			return err
		}
		if err := gravaDoZip(f, destino); err != nil {
			return err
		}
		if i%20 == 0 {
			j.Progresso(i * 100 / total)
			j.Status(fmt.Sprintf("%s — aplicando %d de %d", rotulo, i+1, total))
		}
	}

	for _, alvo := range apagar {
		if destino, err := destinoSeguro(raiz, alvo); err == nil {
			os.Remove(destino)
		}
	}
	return nil
}

// destinoSeguro é a trava contra zip-slip: um zip com `..\..\Windows\System32`
// dentro escreveria fora do cliente. O nome é limpo e conferido contra a raiz
// depois de resolvido, que é a única forma que não depende de adivinhar as
// grafias possíveis de `..`.
func destinoSeguro(raiz, nome string) (string, error) {
	nome = strings.ReplaceAll(nome, "\\", "/")
	if nome == "" || strings.HasPrefix(nome, "/") || strings.Contains(nome, ":") {
		return "", fmt.Errorf("caminho recusado no patch: %s", nome)
	}
	destino := filepath.Join(raiz, filepath.FromSlash(path.Clean(nome)))
	if destino != raiz && !strings.HasPrefix(destino, raiz+string(os.PathSeparator)) {
		return "", fmt.Errorf("caminho recusado no patch: %s", nome)
	}
	return destino, nil
}

// gravaDoZip escreve num arquivo ao lado e renomeia por cima. É o que evita
// deixar um arquivo do cliente pela metade se faltar energia no meio — o
// `os.Rename` do Windows substitui de uma vez.
func gravaDoZip(f *zip.File, destino string) error {
	origem, err := f.Open()
	if err != nil {
		return err
	}
	defer origem.Close()

	parcial := destino + ".parte"
	saida, err := os.Create(parcial)
	if err != nil {
		// Erro aqui é quase sempre arquivo em uso: o jogo aberto segurando o
		// GRF, ou um antivírus. Vale dizer isso em vez do texto do sistema.
		return fmt.Errorf("não consegui gravar %s (o jogo está aberto?)",
			filepath.Base(destino))
	}
	if _, err := io.Copy(saida, origem); err != nil {
		saida.Close()
		os.Remove(parcial)
		return err
	}
	if err := saida.Close(); err != nil {
		os.Remove(parcial)
		return err
	}
	return os.Rename(parcial, destino)
}

func leDoZip(f *zip.File) (string, error) {
	r, err := f.Open()
	if err != nil {
		return "", err
	}
	defer r.Close()
	dados, err := io.ReadAll(io.LimitReader(r, 1<<20))
	return string(dados), err
}

func somaArquivo(caminho string) (string, error) {
	f, err := os.Open(caminho)
	if err != nil {
		return "", err
	}
	defer f.Close()
	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

func existe(caminho string) bool {
	_, err := os.Stat(caminho)
	return err == nil
}
