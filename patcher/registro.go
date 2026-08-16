// O registro do Atualizador: `patch\atualizador.log`.
//
// Existe por um motivo prático — quando algo falha, quem está na frente da tela
// é o jogador, não nós. Um arquivo de texto ao lado do jogo é a única coisa que
// ele consegue mandar pelo Discord, e é o que separa "não funcionou" de um
// diagnóstico.
//
// O arquivo é reescrito a cada execução, de propósito: interessa a última
// rodada, e um log que cresce sozinho na máquina dos outros é falta de educação.
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

var (
	logMutex   sync.Mutex
	logArquivo *os.File
)

func abreRegistro(trabalho string) {
	f, err := os.Create(filepath.Join(trabalho, "atualizador.log"))
	if err != nil {
		return // sem log é inconveniente, não é motivo para parar
	}
	logArquivo = f
	anota("Atualizador versão %d", VERSAO)
}

func anota(formato string, args ...any) {
	logMutex.Lock()
	defer logMutex.Unlock()
	if logArquivo == nil {
		return
	}
	fmt.Fprintf(logArquivo, "%s  %s\n", time.Now().Format("15:04:05"),
		fmt.Sprintf(formato, args...))
	logArquivo.Sync() // travou no meio? o que já foi escrito tem de estar lá
}
