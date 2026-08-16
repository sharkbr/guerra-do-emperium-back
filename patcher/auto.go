// A auto-atualização do próprio Atualizador.
//
// O problema é que um programa em Windows não consegue gravar por cima do
// próprio .exe enquanto ele roda — mas CONSEGUE se renomear. É nisso que o
// truque se apoia, e é a razão de existir este arquivo separado:
//
//  1. baixa o exe novo para `patch\Atualizador.novo` e confere o sha256
//  2. renomeia a si mesmo para `patch\Atualizador.velho`
//  3. move o novo para o lugar do antigo
//  4. lança o novo e morre
//  5. o novo, ao subir, apaga o `.velho` (agora ninguém o segura)
//
// Se qualquer passo falhar, o Atualizador atual desfaz o que deu e segue a
// rodada normal. Ficar sem atualizar-se é inconveniente; ficar sem exe nenhum
// deixaria o jogador sem jogo e sem conserto que ele saiba fazer.
//
// Por isso também o Atualizador NÃO entra em patch comum — o
// `ferramentas/monta_patch.py` recusa. Patch comum é extração por cima, que é
// exatamente o que não funciona com o exe em execução.
package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Os nomes dos arquivos da troca saem do nome do próprio exe (`Jogar.novo`,
// `Jogar.velho`), e não de uma constante: assim renomear o executável não
// deixa para trás um `.velho` que ninguém mais apaga.
func nomeDaTroca(trabalho, exe, sufixo string) string {
	base := strings.TrimSuffix(filepath.Base(exe), filepath.Ext(exe))
	return filepath.Join(trabalho, base+sufixo)
}

// limpaVelho apaga a cópia deixada pela troca anterior. Roda em toda subida
// porque a única hora em que aquele arquivo pode ser apagado é quando ele já
// não está em execução — ou seja, na execução seguinte.
func limpaVelho(trabalho, exe string) {
	os.Remove(nomeDaTroca(trabalho, exe, ".velho"))
	os.Remove(filepath.Join(trabalho, "Atualizador.velho")) // do nome antigo
}

// autoAtualiza devolve `true` quando o exe novo foi lançado — nesse caso quem
// chamou deve voltar sem fazer mais nada, porque a rodada continua no outro
// processo.
func autoAtualiza(j *Janela, raiz, trabalho string, cfg config) (bool, error) {
	versao, arquivo, soma, err := leCanal(cfg.url)
	if err != nil {
		return false, err
	}
	if versao <= VERSAO {
		return false, nil
	}

	eu, err := os.Executable()
	if err != nil {
		return false, err
	}

	j.Status(fmt.Sprintf("Atualizando o próprio atualizador (versão %d)…", versao))
	novo := nomeDaTroca(trabalho, eu, ".novo")
	os.Remove(novo)
	if err := baixa(j, cfg.url+arquivo, novo, 0, "atualizador"); err != nil {
		return false, err
	}
	baixado, err := somaArquivo(novo)
	if err != nil {
		return false, err
	}
	if baixado != soma {
		os.Remove(novo)
		return false, fmt.Errorf("o atualizador baixado não confere (sha256)")
	}

	velho := nomeDaTroca(trabalho, eu, ".velho")
	os.Remove(velho)
	if err := os.Rename(eu, velho); err != nil {
		return false, err
	}
	if err := os.Rename(novo, eu); err != nil {
		os.Rename(velho, eu) // volta ao que era: melhor velho que nenhum
		return false, err
	}

	cmd := exec.Command(eu)
	cmd.Dir = raiz
	if err := cmd.Start(); err != nil {
		return false, err
	}
	// Uma respiração para o processo novo aparecer na tela antes de este sumir;
	// sem ela a janela pisca e parece que o programa fechou sozinho.
	time.Sleep(300 * time.Millisecond)
	j.Fecha()
	os.Exit(0)
	return true, nil
}

// leCanal busca o `patcher.txt` do servidor:
//
//	versao=2
//	arquivo=Atualizador-2.exe
//	sha256=…
//
// Ausência do arquivo (404) NÃO é erro — é o estado normal enquanto nenhum
// Atualizador novo foi publicado.
func leCanal(url string) (int, string, string, error) {
	resp, err := cliente.Get(url + "patcher.txt")
	if err != nil {
		return 0, "", "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode == 404 {
		return 0, "", "", nil
	}
	if resp.StatusCode != 200 {
		return 0, "", "", fmt.Errorf("patcher.txt respondeu %s", resp.Status)
	}
	dados, err := io.ReadAll(io.LimitReader(resp.Body, 64<<10))
	if err != nil {
		return 0, "", "", err
	}

	var versao int
	var arquivo, soma string
	for _, linha := range strings.Split(string(dados), "\n") {
		linha = strings.TrimSpace(linha)
		if linha == "" || strings.HasPrefix(linha, "#") {
			continue
		}
		chave, valor, achou := strings.Cut(linha, "=")
		if !achou {
			continue
		}
		chave, valor = strings.TrimSpace(chave), strings.TrimSpace(valor)
		switch strings.ToLower(chave) {
		case "versao":
			versao, _ = strconv.Atoi(valor)
		case "arquivo":
			arquivo = valor
		case "sha256":
			soma = valor
		}
	}
	if versao > 0 && (arquivo == "" || soma == "") {
		return 0, "", "", fmt.Errorf("patcher.txt sem arquivo ou sha256")
	}
	// Nome de arquivo e não caminho: o canal não escolhe onde gravar.
	if strings.ContainsAny(arquivo, "/\\:") {
		return 0, "", "", fmt.Errorf("patcher.txt: nome de arquivo recusado")
	}
	return versao, arquivo, soma, nil
}
