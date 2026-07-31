# Ferramentas de inspeção do cliente

Escritas em 2026-07-30 para diagnosticar o erro `RecommendedQuestInfoLoad`.
Rodam em **Python 2.7** (`C:\Python27\python.exe`), que já está instalado nesta
máquina por causa do `get4.py` do NEMO.

## `grf.py` — extrator de GRF 0x200

```
python grf.py <data.grf> find    <padrao>                # lista nomes que casam
python grf.py <data.grf> get     <nome-exato> <saida>
python grf.py <data.grf> getlike <padrao-ascii> <saida> [indice]
```

Lê o header de 46 bytes, descomprime a tabela de arquivos com zlib e extrai por
nome.

**Limitação conhecida:** não lê entradas com flag DES (`flags & 6`). O GRF oficial
da Gravity tem muitas — inclusive `data\texture\유저인터페이스\loading07.jpg`.

**Por que existe o `getlike`:** caminhos com trecho coreano não sobrevivem ao
console do PowerShell até o `argv` do Python. O `getlike` casa por substring ASCII
dentro do próprio script, contornando o problema.

## `luadis.py` — desassemblador de bytecode Lua 5.1

```
python luadis.py <arquivo.lub>
```

Os `.lub` do cliente são bytecode (header `1b 4c 75 61 51`), não texto — busca de
string neles não é confiável. Este script imprime, para cada função, os opcodes
com o **número de linha do fonte original**, as constantes e os globais lidos e
escritos.

Foi o que mostrou que `QuestInfo_f.lua:57` era o laço externo
(`pairs(RecommendedQuestInfoList)`), e não uma tabela aninhada como se supunha.
Também serve para descobrir que global um `.lub` define, via `SETGLOBAL`.
