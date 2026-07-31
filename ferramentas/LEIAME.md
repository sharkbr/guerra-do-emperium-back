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

## `filtra_lub_por_skid.py` — recorta arquivo de habilidade do ROenglishRE

```
python filtra_lub_por_skid.py <skillid-do-GRF.lub> <entrada.lub> <saida.lub>
```

Os arquivos de habilidade do ROenglishRE são tabelas indexadas por constante
(`SKILL_INFO_LIST = { [SKID.NV_BASIC] = {...} }`). A versão de 2026 traz ~140
habilidades de 4ª classe que o nosso cliente de 2021 não conhece. Como
`[nil] = {...}` é erro em Lua, o arquivo inteiro aborta, a tabela nunca é criada
e a janela de habilidades recebe nil — o que estoura em C++ com `0xC0000005`.

Este script mantém só as entradas cuja constante existe no `skillid.lub` do
**nosso** cliente (extraído do GRF com o `grf.py`). Ele também respeita strings ao
contar chaves, porque as descrições têm texto livre.

**É a alternativa a jogar o arquivo fora.** Antes a receita para `.lub` novo
demais era mover para o backup e perder a tradução inteira. Recortar preserva
tudo que o cliente sabe exibir — no caso das habilidades, 1559 de 1694.

**Sempre validar a saída**: além das entradas de primeiro nível, o arquivo tem
referências aninhadas a `SKID` (os pré-requisitos em `_NeedSkillList`). Uma
referência órfã traz o crash de volta. Conferir com:

```
python -c "import re;t=open('saida.lub','rb').read();print len(set(re.findall(r'SKID\.(\w+)',t)))"
```

e comparar com o conjunto conhecido do cliente.

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

**Só os `.lub` do GRF são bytecode.** Os do ROenglishRE são Lua em **texto puro**
com extensão `.lub` — o cliente lê os dois. Conferir o header antes de gastar
tempo com desassemblador:

```
python -c "print open('x.lub','rb').read(4) == '\x1bLua'"
```

Isso também significa que comparar o tamanho de um arquivo do GRF com o do
ROenglishRE **não diz nada**: um é bytecode e o outro é texto.

**Armadilha ao ler tabela grande de bytecode:** no Lua 5.1 o operando `RK` só
endereça constante até o índice 255. Passando disso o compilador emite `LOADK`
num registrador e o `SETTABLE` passa a referenciar `R<n>` em vez da constante.
Quem lê só as linhas `SETTABLE ... ; B="NOME" C=<valor>` captura apenas as ~127
primeiras entradas e conclui, errado, que a tabela é minúscula. É preciso
acompanhar os `LOADK` e resolver os registradores — ver
`filtra_lub_por_skid.py:skids_do_cliente`.
