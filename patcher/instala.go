// A instalação — o primeiro download, quando o jogador ainda não tem nada.
//
// O mesmo `Jogar.exe` é o instalador e o atualizador, e quem decide qual dos
// dois ele é hoje é a pasta em que está: com o cliente ao lado, atualiza; sem,
// instala. Não há um segundo programa, um segundo download nem um segundo
// código de rede para manter — o jogador baixa 9 MB, abre numa pasta qualquer,
// e recebe os 3,4 GB.
//
// O que ele baixa aqui é a BASE (`base.txt`, gerada por
// `ferramentas/monta_cliente.py`), e não os patches. Terminada a base, o fluxo
// normal do main.go continua e aplica os patches publicados desde que o pacote
// foi montado — é isso que permite o pacote ficar parado numa versão conhecida
// em vez de ser refeito a cada mudança.
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"unsafe"
)

// O nome da lista no bucket, e o destino padrão. O destino é `C:\` e não
// `Arquivos de Programas` de propósito: o cliente ESCREVE na própria pasta
// (screenshots, replays, `savedata`, o `patch\` do Atualizador), e sob
// `Program Files` isso cai no Virtual Store do Windows ou exige elevação a
// cada abertura. Servidor privado de RO instala na raiz desde sempre, e é o
// que os jogadores esperam.
const (
	arquivoBase    = "base.txt"
	destinoPadrao  = `C:\GuerraDoEmperium`
	margemDeDisco  = 600 << 20 // folga além do tamanho da instalação
	nomeDoAtalho   = "Guerra do Emperium"
	descricaoAlvo  = "Jogar Guerra do Emperium"
	arquivoIniBase = "Jogar.ini"
	// O configurador de vídeo e som que vem com o cliente do kRO. É ele que
	// escreve a chave de registro sem a qual o jogo não inicia — ver video.go.
	arquivoSetup = "Setup.exe"
)

// pedaco é uma linha da `base.txt`. São SEIS campos, contra os cinco de um
// patch: o campo a mais é o tipo, e ele existe porque o `data.grf` não é um
// zip — ver o cabeçalho do `ferramentas/monta_cliente.py`.
type pedaco struct {
	Numero  int
	Arquivo string
	SHA     string
	Bytes   int64
	Tipo    string // "zip" ou "bruto"
	Nome    string
}

const (
	tipoZip   = "zip"
	tipoBruto = "bruto"
)

// PrecisaInstalar diz se esta pasta ainda não tem um cliente NOSSO.
//
// São DOIS arquivos, e nenhum dos dois basta sozinho — a pergunta é "há aqui
// uma instalação que o botão JOGAR consegue abrir?", e ela só tem resposta
// afirmativa quando as duas metades estão presentes:
//
//	data.grf   o mundo. Sem ele não existe jogo nenhum, tem 2,95 GB e nunca é
//	           criado por acidente — mas EXISTE em qualquer instalação de
//	           Ragnarok, inclusive na de outro servidor ou na do bRO.
//	<jogo>     o exe do cliente. É o que o JOGAR abre; sem ele o Atualizador
//	           não tem o que lançar.
//
// Olhar só o `data.grf` foi o que quebrou em 2026-08-16: um jogador copiou o
// `Jogar.exe` para dentro da pasta de uma instalação antiga de RO, que tinha
// `data.grf` e não tinha o nosso exe. O programa concluiu "já instalado",
// entrou no modo atualizador, não baixou nada, acendeu o JOGAR — e o clique
// devolveu **"não encontrei GuerraDoEmperium.exe"**, uma mensagem de
// atualizador na cara de quem estava tentando INSTALAR, sem nenhum caminho de
// saída na tela.
//
// Olhar só o exe seria o erro simétrico (uma pasta com um exe velho e sem
// `data.grf` se calaria diante de uma instalação que não existe), e é por isso
// que os dois são exigidos e não um ou outro. Instalar por cima é barato: os
// pedaços que já estiverem em disco com o sha certo são pulados.
func PrecisaInstalar(raiz, jogo string) bool {
	for _, nome := range []string{"data.grf", jogo} {
		if _, err := os.Stat(filepath.Join(raiz, nome)); err != nil {
			return true
		}
	}
	return false
}

// baixaBase lê a `base.txt` do servidor. Linha malformada é ERRO e não linha
// pulada, pelo mesmo motivo da lista de patches: pular deixaria o cliente do
// jogador num estado que ninguém consegue reproduzir aqui.
func baixaBase(url string) ([]pedaco, error) {
	dados, err := baixaTexto(url + arquivoBase)
	if err != nil {
		return nil, err
	}
	var lista []pedaco
	for n, linha := range strings.Split(dados, "\n") {
		linha = strings.TrimRight(linha, "\r")
		if strings.TrimSpace(linha) == "" || strings.HasPrefix(strings.TrimSpace(linha), "#") {
			continue
		}
		campos := strings.Split(linha, "\t")
		if len(campos) != 6 {
			return nil, fmt.Errorf("%s linha %d: %d campos", arquivoBase, n+1, len(campos))
		}
		numero, err := strconv.Atoi(strings.TrimSpace(campos[0]))
		if err != nil {
			return nil, fmt.Errorf("%s linha %d: número inválido", arquivoBase, n+1)
		}
		bytes, err := strconv.ParseInt(strings.TrimSpace(campos[3]), 10, 64)
		if err != nil {
			return nil, fmt.Errorf("%s linha %d: tamanho inválido", arquivoBase, n+1)
		}
		tipo := strings.TrimSpace(campos[4])
		if tipo != tipoZip && tipo != tipoBruto {
			return nil, fmt.Errorf("%s linha %d: tipo desconhecido %q", arquivoBase, n+1, tipo)
		}
		lista = append(lista, pedaco{numero, campos[1], strings.TrimSpace(campos[2]),
			bytes, tipo, campos[5]})
	}
	if len(lista) == 0 {
		return nil, fmt.Errorf("%s não tem nenhum pedaço", arquivoBase)
	}
	return lista, nil
}

// TamanhoDaInstalacao é quanto o jogador vai baixar, para a conta de disco e
// para dizer o número na tela antes de ele decidir.
func TamanhoDaInstalacao(lista []pedaco) int64 {
	var total int64
	for _, p := range lista {
		total += p.Bytes
	}
	return total
}

var (
	kernel32ins             = syscall.NewLazyDLL("kernel32.dll")
	procGetDiskFreeSpaceExW = kernel32ins.NewProc("GetDiskFreeSpaceExW")
)

// EspacoLivre devolve quantos bytes cabem no disco daquele caminho.
//
// A pasta pode ainda não existir, então quem é consultado é o caminho mais
// próximo que exista — a API responde pelo VOLUME, e é isso que interessa.
func EspacoLivre(caminho string) (int64, error) {
	for {
		if _, err := os.Stat(caminho); err == nil {
			break
		}
		pai := filepath.Dir(caminho)
		if pai == caminho {
			break
		}
		caminho = pai
	}
	p, err := syscall.UTF16PtrFromString(caminho)
	if err != nil {
		return 0, err
	}
	var livre, total, totalLivre uint64
	r, _, err := procGetDiskFreeSpaceExW.Call(
		uintptr(unsafe.Pointer(p)),
		uintptr(unsafe.Pointer(&livre)),
		uintptr(unsafe.Pointer(&total)),
		uintptr(unsafe.Pointer(&totalLivre)),
	)
	if r == 0 {
		return 0, err
	}
	return int64(livre), nil
}

// ConfereDisco recusa a instalação ANTES de baixar qualquer coisa.
//
// A margem existe porque o pico não é o tamanho final: cada zip vive em disco
// junto com o que ele extraiu, e o maior deles são as músicas. Descobrir que
// faltou espaço depois de baixar 3 GB é o pior lugar possível para descobrir.
func ConfereDisco(destino string, precisa int64) error {
	livre, err := EspacoLivre(destino)
	if err != nil {
		// Não saber o espaço livre não é motivo para impedir a instalação —
		// no pior caso ela falha adiante, com uma mensagem de disco cheio.
		anota("espaço livre: %v", err)
		return nil
	}
	if livre < precisa+margemDeDisco {
		return fmt.Errorf("faltam %.1f GB livres em %s (tem %.1f, precisa de %.1f)",
			float64(precisa+margemDeDisco-livre)/(1<<30), filepath.VolumeName(destino),
			float64(livre)/(1<<30), float64(precisa+margemDeDisco)/(1<<30))
	}
	return nil
}

// aplicaPedaco baixa um pedaço e o põe no lugar. É onde os dois tipos se
// separam, e é a única diferença entre eles em todo o Atualizador.
func aplicaPedaco(j *Janela, raiz, trabalho, url string, p pedaco, rotulo string) error {
	if p.Tipo == tipoBruto {
		// Vai direto para o destino final, sem zip e sem cópia intermediária.
		// São 2,95 GB: passar por um arquivo temporário custaria o dobro de
		// disco e uma cópia inteira de 3 GB, sem ganhar nada.
		destino, err := destinoSeguro(raiz, p.Arquivo)
		if err != nil {
			return err
		}
		if err := os.MkdirAll(filepath.Dir(destino), 0o755); err != nil {
			return err
		}
		// Um arquivo já no lugar com o sha certo é reinstalação ou retomada
		// entre execuções — nos dois casos, não se baixa de novo.
		if soma, err := somaArquivo(destino); err == nil && soma == p.SHA {
			return nil
		}
		j.Status(rotulo + " — baixando…")
		if err := baixa(j, url+p.Arquivo, destino, p.Bytes, rotulo); err != nil {
			return err
		}
		j.Status(rotulo + " — conferindo…")
		soma, err := somaArquivo(destino)
		if err != nil {
			return err
		}
		if soma != p.SHA {
			os.Remove(destino)
			return fmt.Errorf("o arquivo baixado não confere (sha256)")
		}
		return nil
	}

	// Zip: o caminho é exatamente o de um patch, e reusa o mesmo código.
	return aplica(j, raiz, trabalho, url, patch{
		Numero:  p.Numero,
		Arquivo: p.Arquivo,
		SHA:     p.SHA,
		Bytes:   p.Bytes,
		Nome:    p.Nome,
	}, rotulo)
}

// Instala é a rodada inteira do primeiro download.
//
// Ela NÃO grava `aplicados.txt` para os pedaços da base: aquele arquivo é o
// registro dos PATCHES, e misturar os dois faria o Atualizador achar que já
// aplicou patches que nunca viu. A base não precisa de registro — quem
// pergunta se ela está instalada é o `PrecisaInstalar`, olhando o disco.
// A `cfg` inteira entra, e não só a URL da base, porque o `.ini` que fica na
// pasta do jogador precisa dos DOIS endereços — o da base e o dos patches.
func Instala(j *Janela, destino string, cfg config, comAtalho bool, exeAtual string) error {
	if err := os.MkdirAll(destino, 0o755); err != nil {
		return fmt.Errorf("não consegui criar %s: %w", destino, err)
	}

	j.Status("Consultando o servidor…")
	lista, err := baixaBase(cfg.base)
	if err != nil {
		return err
	}

	precisa := TamanhoDaInstalacao(lista)
	if err := ConfereDisco(destino, precisa); err != nil {
		return err
	}

	trabalho := filepath.Join(destino, "patch")
	if err := os.MkdirAll(trabalho, 0o755); err != nil {
		return err
	}

	for i, p := range lista {
		rotulo := fmt.Sprintf("[%d/%d] %s", i+1, len(lista), p.Nome)
		if err := aplicaPedaco(j, destino, trabalho, cfg.base, p, rotulo); err != nil {
			return fmt.Errorf("%s: %w", p.Nome, err)
		}
	}

	// O exe se copia para a pasta do jogo. Sem isto o jogador ficaria com o
	// atalho apontando para a pasta de Downloads — que é onde o navegador põe
	// as coisas e de onde as pessoas apagam sem pensar.
	j.Status("Finalizando…")
	if err := instalaASiMesmo(destino, cfg, exeAtual); err != nil {
		// Não é motivo para falhar a instalação: o jogo está inteiro em disco.
		anota("cópia do atualizador: %v", err)
	}

	if comAtalho {
		alvo := filepath.Join(destino, filepath.Base(exeAtual))
		if _, err := AtalhoNaAreaDeTrabalho(nomeDoAtalho, alvo, destino, descricaoAlvo); err != nil {
			// Idem: atalho é conveniência, não instalação.
			anota("atalho: %v", err)
			j.Status("Instalado (não consegui criar o atalho)")
		}
	}

	configuraVideo(j, destino)
	return nil
}

// configuraVideo roda o `Setup.exe` na primeira instalação desta máquina.
//
// Sem isto o cliente abre e morre com `Cannot init d3d OR grf file has
// problem` — ele lê o dispositivo Direct3D do registro, e numa máquina onde o
// Setup nunca rodou aquela chave não existe (ver `video.go`). Foi o que
// aconteceu no primeiro teste em outra máquina, em 2026-08-16: 4,2 GB corretos
// em disco, sha256 de cada pedaço fechando, e o jogo sem abrir.
//
// **Espera o Setup fechar**, e a ordem não é negociável: o cliente lê a chave
// na inicialização, então abrir os dois juntos leria o registro que o Setup
// ainda não escreveu.
//
// Nada aqui interrompe a instalação. Setup ausente, jogador que fecha a janela
// no X, placa que o Setup não reconhece — em todos os casos o jogo está em
// disco, e o pior que acontece é ele ter de rodar o Setup à mão, que é
// exatamente a situação de quem não tem esta função.
func configuraVideo(j *Janela, destino string) {
	if VideoConfigurado() {
		return
	}
	setup := filepath.Join(destino, arquivoSetup)
	if _, err := os.Stat(setup); err != nil {
		anota("Setup.exe não encontrado em %s", destino)
		return
	}
	j.Status("Configurando vídeo e som — confirme na janela que abriu…")
	if err := ExecutaEEspera(setup, destino); err != nil {
		anota("Setup.exe: %v", err)
		return
	}
	if !VideoConfigurado() {
		// O jogador fechou no X, ou o Setup não gravou. Dizer isso agora é
		// muito melhor do que ele descobrir com `Cannot init d3d`.
		j.Status("Configuração de vídeo não concluída — rode o Setup.exe se o jogo não abrir")
	}
}

// instalaASiMesmo copia o exe e escreve o `.ini` ao lado dele.
//
// A cópia é pulada quando a origem e o destino são o mesmo arquivo — o caso de
// quem já baixou o `Jogar.exe` direto para dentro da pasta escolhida. Copiar um
// arquivo em execução por cima de si mesmo é justamente o que o Windows não
// deixa, e daria um erro incompreensível bem no fim de uma instalação inteira.
func instalaASiMesmo(destino string, cfg config, exeAtual string) error {
	alvo := filepath.Join(destino, filepath.Base(exeAtual))
	if mesmoArquivo(alvo, exeAtual) {
		return escreveIni(destino, cfg)
	}
	origem, err := os.Open(exeAtual)
	if err != nil {
		return err
	}
	defer origem.Close()

	parcial := alvo + ".novo"
	saida, err := os.OpenFile(parcial, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o755)
	if err != nil {
		return err
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
	if err := os.Rename(parcial, alvo); err != nil {
		return err
	}
	return escreveIni(destino, cfg)
}

func mesmoArquivo(a, b string) bool {
	ia, err := os.Stat(a)
	if err != nil {
		return false
	}
	ib, err := os.Stat(b)
	if err != nil {
		return false
	}
	return os.SameFile(ia, ib)
}

// escreveIni deixa o `.ini` com a URL que ESTA instalação usou.
//
// Não se escreve por cima de um `.ini` que já exista: se o jogador editou o
// dele para apontar para outro lugar, a decisão é dele.
func escreveIni(destino string, cfg config) error {
	caminho := filepath.Join(destino, arquivoIniBase)
	if _, err := os.Stat(caminho); err == nil {
		return nil
	}
	texto := fmt.Sprintf("# Guerra do Emperium - configuração do Jogar.exe.\n"+
		"# Gerado pela instalação. Apagar este arquivo faz o programa usar os\n"+
		"# valores embutidos, que são estes mesmos.\n"+
		"#\n"+
		"# url  = de onde vêm as atualizações\n"+
		"# base = de onde veio a instalação (só serve se ela for refeita)\n\n"+
		"url=%s\nbase=%s\njogo=%s\n", cfg.url, cfg.base, cfg.jogo)
	return os.WriteFile(caminho, []byte(texto), 0o644)
}
