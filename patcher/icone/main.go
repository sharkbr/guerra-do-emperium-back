// Gera o ícone do Jogar.exe a partir de um PNG: o `.ico` e o `.syso`.
//
//	cd patcher && go run ./icone recursos/icone-origem.png
//
// Sai daqui:
//
//	patcher/recursos/icone.ico          para atalho, site, instalador
//	patcher/icone_windows_amd64.syso    o recurso que o `go build` embute
//
// O `.syso` é um arquivo-objeto COFF que o linkador do Go junta ao binário sem
// que ninguém precise pedir — é assim que um programa Go ganha ícone. A
// ferramenta conhecida para isso é o `rsrc`, de terceiro; escrevemos o nosso
// pelo mesmo motivo de todo o resto do Atualizador: o que vai para a máquina
// dos jogadores não deve depender de binário que ninguém neste projeto leu.
// São ~200 linhas, e o formato não muda desde 1993.
//
// **O `.syso` é versionado**, e este gerador roda só quando o desenho mudar.
package main

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
)

// Os tamanhos que entram no ícone. O Windows escolhe conforme o contexto: 16
// na barra de título e na lista de arquivos, 32 no atalho, 48 nos ícones
// grandes, 256 na visualização extra-grande.
//
// Até 64 vão como BMP; o 256 vai como PNG. **Isso não é preciosismo:** o
// Windows só aceita PNG dentro de ícone a partir do Vista, e ainda há jogador
// de servidor privado no 7 — mas nenhum Windows mostra 256x256 em contexto
// onde o PNG não seja entendido, e um BMP de 256x256 em 32 bits custa 256 KB
// contra 20 do PNG.
var tamanhos = []int{16, 24, 32, 48, 64, 128, 256}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("uso: go run ./icone <arquivo.png>")
		os.Exit(1)
	}
	origem := os.Args[1]

	f, err := os.Open(origem)
	if err != nil {
		morre(err)
	}
	img, err := png.Decode(f)
	f.Close()
	if err != nil {
		morre(err)
	}
	rgba := paraRGBA(img)

	// Cada tamanho vira um blob no formato que o ícone espera.
	var imagens [][]byte
	for _, lado := range tamanhos {
		reduzida := reduz(rgba, lado, lado)
		if lado >= 256 {
			imagens = append(imagens, comoPNG(reduzida))
		} else {
			imagens = append(imagens, comoBMP(reduzida))
		}
		fmt.Printf("  %3dx%-3d  %6.1f KB\n", lado, lado,
			float64(len(imagens[len(imagens)-1]))/1024)
	}

	ico := montaICO(imagens)
	if err := os.WriteFile(filepath.Join("recursos", "icone.ico"), ico, 0o644); err != nil {
		morre(err)
	}
	syso := montaSYSO(imagens)
	if err := os.WriteFile("icone_windows_amd64.syso", syso, 0o644); err != nil {
		morre(err)
	}
	fmt.Printf("\nrecursos/icone.ico          %6.1f KB\n", float64(len(ico))/1024)
	fmt.Printf("icone_windows_amd64.syso    %6.1f KB\n", float64(len(syso))/1024)
	fmt.Println("\nRecompile o Jogar.exe para o ícone entrar.")
}

func morre(err error) {
	fmt.Println("ERRO:", err)
	os.Exit(1)
}

func paraRGBA(img image.Image) *image.RGBA {
	limites := img.Bounds()
	saida := image.NewRGBA(limites)
	for y := limites.Min.Y; y < limites.Max.Y; y++ {
		for x := limites.Min.X; x < limites.Max.X; x++ {
			r, g, b, a := img.At(x, y).RGBA()
			i := saida.PixOffset(x, y)
			saida.Pix[i] = byte(r >> 8)
			saida.Pix[i+1] = byte(g >> 8)
			saida.Pix[i+2] = byte(b >> 8)
			saida.Pix[i+3] = byte(a >> 8)
		}
	}
	return saida
}

// reduz faz média de caixa. O RGB é ponderado pelo ALFA — sem isso, o preto
// transparente das bordas entra na conta e o ícone ganha uma auréola escura,
// que é o defeito clássico de ícone redimensionado sem cuidado.
func reduz(origem *image.RGBA, largura, altura int) *image.RGBA {
	limites := origem.Bounds()
	saida := image.NewRGBA(image.Rect(0, 0, largura, altura))
	for y := 0; y < altura; y++ {
		y0 := limites.Min.Y + y*limites.Dy()/altura
		y1 := limites.Min.Y + (y+1)*limites.Dy()/altura
		if y1 <= y0 {
			y1 = y0 + 1
		}
		for x := 0; x < largura; x++ {
			x0 := limites.Min.X + x*limites.Dx()/largura
			x1 := limites.Min.X + (x+1)*limites.Dx()/largura
			if x1 <= x0 {
				x1 = x0 + 1
			}
			var r, g, b, a, peso, n int
			for sy := y0; sy < y1; sy++ {
				for sx := x0; sx < x1; sx++ {
					i := origem.PixOffset(sx, sy)
					alfa := int(origem.Pix[i+3])
					r += int(origem.Pix[i]) * alfa
					g += int(origem.Pix[i+1]) * alfa
					b += int(origem.Pix[i+2]) * alfa
					a += alfa
					peso += alfa
					n++
				}
			}
			j := saida.PixOffset(x, y)
			if peso > 0 {
				saida.Pix[j] = byte(r / peso)
				saida.Pix[j+1] = byte(g / peso)
				saida.Pix[j+2] = byte(b / peso)
			}
			saida.Pix[j+3] = byte(a / n)
		}
	}
	return saida
}

func comoPNG(img *image.RGBA) []byte {
	var buf bytes.Buffer
	if err := png.Encode(&buf, img); err != nil {
		morre(err)
	}
	return buf.Bytes()
}

// comoBMP escreve a imagem no formato que vive dentro de um `.ico`: um
// BITMAPINFOHEADER seguido dos pixels BGRA **de baixo para cima**, mais a
// máscara AND de 1 bit.
//
// Duas coisas que fazem o ícone sair errado se esquecidas: a **altura no
// cabeçalho é o dobro** da real (imagem + máscara), e a máscara existe mesmo
// em 32 bits, em que ela é ignorada — mas o tamanho do recurso é conferido, e
// sem ela o Windows lê lixo.
func comoBMP(img *image.RGBA) []byte {
	lado := img.Bounds().Dx()
	var buf bytes.Buffer

	binary.Write(&buf, binary.LittleEndian, struct {
		Tamanho                 uint32
		Largura, Altura         int32
		Planos, Bits            uint16
		Compressao, TamanhoImg  uint32
		XPPM, YPPM              int32
		Cores, CoresImportantes uint32
	}{40, int32(lado), int32(lado * 2), 1, 32, 0, 0, 0, 0, 0, 0})

	for y := lado - 1; y >= 0; y-- {
		for x := 0; x < lado; x++ {
			i := img.PixOffset(x, y)
			buf.Write([]byte{img.Pix[i+2], img.Pix[i+1], img.Pix[i], img.Pix[i+3]})
		}
	}
	// A máscara: 1 bit por pixel, cada linha alinhada em 4 bytes. Zerada.
	bytesPorLinha := ((lado + 31) / 32) * 4
	buf.Write(make([]byte, bytesPorLinha*lado))
	return buf.Bytes()
}

// montaICO escreve o arquivo `.ico` — cabeçalho, uma entrada por tamanho e os
// dados em seguida.
func montaICO(imagens [][]byte) []byte {
	var buf bytes.Buffer
	binary.Write(&buf, binary.LittleEndian, [3]uint16{0, 1, uint16(len(imagens))})

	deslocamento := 6 + 16*len(imagens)
	for i, lado := range tamanhos {
		buf.Write(entradaDir(lado, len(imagens[i])))
		binary.Write(&buf, binary.LittleEndian, uint32(deslocamento))
		deslocamento += len(imagens[i])
	}
	for _, img := range imagens {
		buf.Write(img)
	}
	return buf.Bytes()
}

// entradaDir são os 12 primeiros bytes de uma entrada de diretório de ícone —
// iguais no `.ico` e no recurso GROUP_ICON. 256 se escreve como **0**: o campo
// tem um byte só.
func entradaDir(lado, tamanho int) []byte {
	var buf bytes.Buffer
	dimensao := byte(lado)
	if lado >= 256 {
		dimensao = 0
	}
	buf.Write([]byte{dimensao, dimensao, 0, 0})
	binary.Write(&buf, binary.LittleEndian, [2]uint16{1, 32}) // planos, bits
	binary.Write(&buf, binary.LittleEndian, uint32(tamanho))
	return buf.Bytes()
}

// montaSYSO escreve o arquivo-objeto COFF com a seção `.rsrc`.
//
// A árvore de recursos tem três níveis fixos — tipo, id, idioma —, e as folhas
// são `IMAGE_RESOURCE_DATA_ENTRY`. O campo `OffsetToData` de cada folha guarda
// um endereço que só o linkador conhece, e por isso cada um deles precisa de
// uma **relocação**: sem elas o ícone aponta para o lugar errado dentro do exe
// e o Windows mostra o ícone padrão — falha calada e idêntica a "não pus ícone
// nenhum".
func montaSYSO(imagens [][]byte) []byte {
	const (
		rtIcon      = 3
		rtGrupoIcon = 14
		idioma      = 1033 // en-US; o Windows aceita qualquer um, e este é o padrão
	)

	// O grupo é o índice: diz quais ícones existem e com que id cada um está.
	var grupo bytes.Buffer
	binary.Write(&grupo, binary.LittleEndian, [3]uint16{0, 1, uint16(len(imagens))})
	for i, lado := range tamanhos {
		grupo.Write(entradaDir(lado, len(imagens[i])))
		binary.Write(&grupo, binary.LittleEndian, uint16(i+1)) // id do RT_ICON
	}

	// Os recursos, na ordem em que vão para a seção.
	type recurso struct {
		tipo, id uint32
		dados    []byte
	}
	var recursos []recurso
	for i, img := range imagens {
		recursos = append(recursos, recurso{rtIcon, uint32(i + 1), img})
	}
	recursos = append(recursos, recurso{rtGrupoIcon, 1, grupo.Bytes()})

	// --- o tamanho de cada pedaço, para calcular os deslocamentos ---
	tipos := []uint32{rtIcon, rtGrupoIcon}
	porTipo := map[uint32][]recurso{}
	for _, r := range recursos {
		porTipo[r.tipo] = append(porTipo[r.tipo], r)
	}

	tamDir := func(n int) int { return 16 + 8*n }
	inicioRaiz := 0
	inicioTipos := inicioRaiz + tamDir(len(tipos))
	posicao := inicioTipos
	inicioPorTipo := map[uint32]int{}
	for _, t := range tipos {
		inicioPorTipo[t] = posicao
		posicao += tamDir(len(porTipo[t]))
	}
	inicioIdiomas := posicao
	posicao += tamDir(1) * len(recursos)
	inicioFolhas := posicao
	posicao += 16 * len(recursos)
	inicioDados := alinha(posicao, 8)

	// --- os dados, e onde cada um cai ---
	var dados bytes.Buffer
	deslocamentoDado := make([]int, len(recursos))
	for i, r := range recursos {
		deslocamentoDado[i] = inicioDados + dados.Len()
		dados.Write(r.dados)
		for dados.Len()%8 != 0 {
			dados.WriteByte(0)
		}
	}

	// --- a árvore ---
	var rsrc bytes.Buffer
	escreveDir := func(n int) {
		binary.Write(&rsrc, binary.LittleEndian, [2]uint32{0, 0})         // flags, data
		binary.Write(&rsrc, binary.LittleEndian, [2]uint16{0, 0})         // versão
		binary.Write(&rsrc, binary.LittleEndian, [2]uint16{0, uint16(n)}) // nomeados, por id
	}
	entrada := func(id uint32, deslocamento int, subdiretorio bool) {
		valor := uint32(deslocamento)
		if subdiretorio {
			valor |= 0x80000000
		}
		binary.Write(&rsrc, binary.LittleEndian, [2]uint32{id, valor})
	}

	escreveDir(len(tipos))
	for _, t := range tipos {
		entrada(t, inicioPorTipo[t], true)
	}
	// Os diretórios de idioma são escritos na mesma ordem de `recursos` — todos
	// os ícones e depois o grupo —, que é a ordem em que as folhas foram
	// reservadas. As entradas de cada diretório saem em ID crescente porque o
	// Windows busca nelas por bisseção.
	posicaoIdioma := inicioIdiomas
	for _, t := range tipos {
		escreveDir(len(porTipo[t]))
		for _, r := range porTipo[t] {
			entrada(r.id, posicaoIdioma, true)
			posicaoIdioma += tamDir(1)
		}
	}
	for i := range recursos {
		escreveDir(1)
		entrada(idioma, inicioFolhas+16*i, false)
	}

	// --- as folhas, e as relocações que apontam para elas ---
	type relocacao struct {
		endereco, simbolo uint32
		tipo              uint16
	}
	var relocacoes []relocacao
	for i, r := range recursos {
		relocacoes = append(relocacoes, relocacao{uint32(rsrc.Len()), 0, 3}) // ADDR32NB
		binary.Write(&rsrc, binary.LittleEndian, [4]uint32{
			uint32(deslocamentoDado[i]), uint32(len(r.dados)), 0, 0})
	}
	for rsrc.Len() < inicioDados {
		rsrc.WriteByte(0)
	}
	rsrc.Write(dados.Bytes())

	// --- o COFF em volta ---
	const tamCabecalho, tamSecao = 20, 40
	ponteiroDados := tamCabecalho + tamSecao
	ponteiroRelocacoes := ponteiroDados + rsrc.Len()
	ponteiroSimbolos := ponteiroRelocacoes + 10*len(relocacoes)

	var saida bytes.Buffer
	binary.Write(&saida, binary.LittleEndian, struct {
		Maquina, Secoes              uint16
		Data                         uint32
		PtrSimbolos, NumSimbolos     uint32
		TamOpcional, Caracteristicas uint16
	}{0x8664, 1, 0, uint32(ponteiroSimbolos), 1, 0, 0})

	saida.Write([]byte(".rsrc\x00\x00\x00"))
	binary.Write(&saida, binary.LittleEndian, struct {
		TamVirtual, EnderecoVirtual uint32
		TamDados, PtrDados          uint32
		PtrRelocacoes, PtrLinhas    uint32
		NumRelocacoes, NumLinhas    uint16
		Caracteristicas             uint32
	}{0, 0, uint32(rsrc.Len()), uint32(ponteiroDados), uint32(ponteiroRelocacoes), 0,
		uint16(len(relocacoes)), 0, 0x40000040}) // INITIALIZED_DATA | MEM_READ

	saida.Write(rsrc.Bytes())
	for _, r := range relocacoes {
		binary.Write(&saida, binary.LittleEndian, r.endereco)
		binary.Write(&saida, binary.LittleEndian, r.simbolo)
		binary.Write(&saida, binary.LittleEndian, r.tipo)
	}

	// Um símbolo só: a própria seção. É o alvo de todas as relocações.
	saida.Write([]byte(".rsrc\x00\x00\x00"))
	binary.Write(&saida, binary.LittleEndian, uint32(0)) // valor
	binary.Write(&saida, binary.LittleEndian, int16(1))  // seção 1
	binary.Write(&saida, binary.LittleEndian, uint16(0)) // tipo
	saida.WriteByte(3)                                   // STATIC
	saida.WriteByte(0)                                   // sem auxiliares
	binary.Write(&saida, binary.LittleEndian, uint32(4)) // tabela de textos vazia

	return saida.Bytes()
}

func alinha(valor, multiplo int) int {
	if resto := valor % multiplo; resto != 0 {
		return valor + multiplo - resto
	}
	return valor
}
