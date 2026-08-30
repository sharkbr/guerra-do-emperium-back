# Armadilhas: Ambiente e ferramentas desta máquina

Shell, PowerShell, Python 2, encoding cp1252, regex, git, compilação local, ferramentas nossas.

**Este arquivo é um dos seis cadernos de armadilhas do projeto.** O índice de
todos eles — uma linha de gatilho por armadilha, com o caderno onde o caso
está contado por inteiro — está na §5 do `CLAUDE.md`. **Leia aqui a entrada
que o gatilho apontar**; ler o caderno inteiro não é para ser preciso.

As entradas abaixo produziram diagnóstico falso e custaram retrabalho. Cada
uma traz o sintoma, a causa medida (com arquivo e linha, quando existe) e a
saída — e a medição é o que separa esta lista de um palpite. **Armadilha
nova se escreve nas duas pontas:** o caso aqui, o gatilho na §5.

---

- **`strings` não existe** no Git Bash daqui — com `2>/dev/null` falha calado e
  parece "zero resultados".

- **`[Text.Encoding]::Latin1` não existe** no PowerShell 5.1 → devolve `$null` e
  todo resultado derivado é lixo. Usar `GetEncoding(28591)`.

- **`Get-ChildItem -Include`** sem curinga no caminho retorna vazio.

- **Arquivo cp1252 salvo como UTF-8 vira `\xef\xbf\xbd` (U+FFFD) e o acento se
  perde para sempre.** Não é mojibake reversível: o byte original já não está
  lá. Achado em 2026-08-07 no `db/guerra/item_db.yml` — 4 acentos de "Maçã da
  Inocência" e "Diadema do Paraíso" tinham virado isso, e ninguém percebeu
  porque o nome que o jogador lê vem do `itemInfo.lua`, não do servidor.
  O teste, em qualquer arquivo que o jogo leia:
  `python -c "d=open(p,'rb').read(); print '\xef\xbf\xbd' in d"`.

- **E quem faz isso hoje é a FERRAMENTA DE EDIÇÃO do assistente.** Ela lê e
  grava como UTF-8: num arquivo cp1252 ela troca **todo** byte acentuado do
  arquivo por U+FFFD — não só os da linha editada, e sem avisar. Medido em
  2026-08-12 num arquivo de três linhas com seis acentos: trocar uma linha
  **sem acento nenhum** destruiu os seis. Vale para `npc/guerra/*.txt`,
  `db/guerra/item_db.yml`, `.lub`, `itemInfo.lua` — todo texto que o jogo lê.
  (Os `.md` são UTF-8 e podem ser editados à vontade.)
  **A saída é gravar por script**: âncora em ASCII, texto novo nascendo
  `unicode` e um `.encode('cp1252')` num lugar só, mais um `assert` de que a
  âncora é única e um `decode('cp1252')` de volta antes de valer. E **medir o
  fim de linha do arquivo antes de escrever a âncora, nunca supor**: âncora com
  o `\r\n` errado casa zero vezes, e linha remontada com o outro deixa o
  arquivo misturado. Não há padrão a decorar — medido em 2026-08-12, dos 44
  arquivos nossos em `npc/guerra` e `db/guerra` **18 são CRLF e 26 são LF**,
  nenhum misto, e o `.gitattributes` tem `text=auto` (com `*.yml eol=lf`), ou
  seja quem decide é o checkout. Os erros aconteceram nesta ordem em
  2026-08-12; os dois foram baratos porque o `assert` da âncora parou o script
  antes de gravar.

- **E o `$` de um regex com `re.M` NÃO casa antes do `\r` — ele casa DEPOIS,
  deixando o `\r` dentro do grupo capturado.** Em arquivo CRLF, um
  `re.compile(r'^(.*)$', re.M)` devolve a linha **com o carriage return
  colado no fim**; reescrever a linha a partir daí grava só `\n`, e o
  arquivo fica com fins de linha misturados. Falha calada: o rAthena lê
  os dois, o `git diff` mostra a linha inteira como trocada e nada acusa.
  Medido em 2026-08-17 ao pôr as vitrines de Prontera a 1 zeny — as 9
  linhas de `shop` do `mercado_contemporaneo.txt` perderam o `\r`, e quem
  denunciou foi um contador que achou **41 preços trocados onde a medição
  anterior dizia 36**: as 5 linhas de sobra eram justamente as que já
  terminavam em `:1` e "mudaram" só por causa do `\r`. **Número que não
  bate com a medição anterior é o aviso** — sem ele o estrago passa.
  A saída é `(?=\r?$)` na âncora, ou partir por `\n` e tratar o `\r` na
  mão. Da mesma família da regra de medir o fim de linha antes de
  escrever, logo acima.

- **A conexão com o MariaDB nasce em `utf8mb4`, e byte acentuado morre nela.**
  As 105 colunas de texto do banco são `latin1`, mas o `character_set_client`
  padrão deste MariaDB 12.3 é `utf8mb4` — e o rAthena só manda `SET NAMES` se
  `default_codepage` estiver preenchido (`inter.cpp:978`, `map.cpp:4416`), o que
  **não era o caso**. Um byte cp1252 sozinho é UTF-8 inválido, então o
  MariaDB recusa a gravação inteira com *"ERROR 1366 (22007): Incorrect string
  value"*. Ou seja: **texto acentuado que o servidor tenta gravar no banco não
  chega lá**, e o caminho de erro é do lado do SQL, longe de onde o texto
  nasceu. Corrigido em 2026-08-10 por `conf/guerra/inter_guerra.txt`
  (`default_codepage: latin1`); a armadilha continua valendo para quem
  desconfiar do `conf/import/` e apagar esse import.

- **`source` do mysql.exe quebra com barra invertida** (`\U` = comando
  desconhecido). Usar barras normais no caminho.

- **Compilar pela linha de comando exige `SolutionDir` explícito.** O
  `map-server.vcxproj` tira os caminhos de include dessa variável, que só o
  `.sln` define. Sem ela o compilador não acha `common/cbasetypes.hpp` e
  despeja dezenas de `C1083` — que parecem código quebrado, e não são. E
  `MSBuild rAthena.sln -t:map-server` **não** funciona: o alvo é repassado a
  todo projeto da solução e cada um responde `MSB4057`. O que funciona:
  ```
  MSBuild.exe src/map/map-server.vcxproj -p:Configuration=Release \
    -p:Platform=x64 "-p:SolutionDir=<raiz>/rathena/"
  ```
  **Parar o map-server antes de linkar** — executável no ar dá `LNK1104`, e aí
  o binário em disco continua o antigo enquanto tudo mais indica sucesso.

- **Heredoc do Bash aqui come a contrabarra dupla.** `<<'EOF'` deveria ser
  literal e não é: `\\` chega como `\` no arquivo gerado. Se esse arquivo for um
  script Python, o `\n` que sobra vira quebra de linha de verdade dentro do
  texto — foi essa a causa da armadilha acima. Ao gerar texto com caminho do
  Windows (`data\sprite\npc\`), escrever o script com a ferramenta de escrita de
  arquivo, não por heredoc — ou montar a contrabarra com `chr(92)`.

- **No `.cat` de tradução, o `arquivo#N` NÃO é a linha — é a ordem do literal
  dentro do arquivo.** Está na docstring do `literais_todos`
  (`ferramentas/traduz_npcs.py`), e é de propósito: assim o índice não anda
  quando a lista de contextos muda. A armadilha é que o número **parece** linha
  e cai na mesma faixa de grandeza dela, então um recorte "só as falas deste
  NPC, que vai da linha A à B" filtra por engano e **devolve uma lista
  plausível**. Medido em 2026-08-12 ao recortar os cinco NPCs do Cassino de
  Comodo: o filtro errado deu 444 textos com o `Man#megin` zerado — e um NPC de
  203 linhas mudo era a única coisa que denunciava. Com a contagem certa deram
  353, com 59 dele. Para converter, recontar os literais com o mesmo
  `RE_LITERAL` guardando a linha de cada um.

- **`os.system` com a linha começando por aspas** falha no `cmd` do Windows: o
  primeiro par de aspas é comido e sai *"A sintaxe do nome do arquivo... está
  incorreta"* — que parece defeito do arquivo passado, e não é. Usar
  `subprocess.call([exe, arg, ...])`.

- **Nome de NPC pode ter ESPAÇO, e um `\S+` no lugar dele perde arquivo
  inteiro.** Os campos de uma linha de NPC são separados por **TAB**; o nome é
  `[^\t]+`, não `\S+`. As bandeiras dos cinco castelos de Payon se chamam
  `Bright Arbor#1-2`, e o regex errado devolveu **219 bandeiras em vez de
  279** — sem erro, com Payon zerado e um total plausível demais para
  desconfiar. Só uma coluna de zeros numa listagem por arquivo denunciou:
  **listar por arquivo, e não só o total**, é o que transforma esse tipo de
  perda silenciosa em algo visível.

- **Há arquivo de nome COREANO dentro do cliente, e ele quebra o Python 2 de
  duas maneiras diferentes.** A `AI_sakray\` traz o manual da IA do kRO
  (`호문클루스…htm`), e provavelmente não é o único. **Na leitura:** `os.walk`
  com caminho `str` usa a API ANSI, devolve o nome como `????` e o primeiro
  `os.stat` estoura com *"A sintaxe do nome do arquivo... está incorreta"* —
  mensagem que aponta para o arquivo, quando o defeito é do leitor. A saída é
  o caminho nascer `unicode` (`ur'C:\...'`), que faz o Python usar a API W.
  **Na escrita da tela:** um `print` daquele nome derruba a ferramenta com
  `UnicodeEncodeError` — e derruba **depois** de o trabalho já ter sido feito,
  deixando saída pela metade. A saída é uma linha no topo do arquivo:
  `sys.stdout = codecs.getwriter(sys.stdout.encoding or 'cp1252')(sys.stdout,
  'replace')`. Sem `sys.stdout.encoding` (saída redirecionada) o Python 2
  devolve `None`, então o `or` não é enfeite. Medido em 2026-08-15 no
  `monta_patch.py`.

- **`valida_visual.le_item_db` devolve uma LISTA CHATA com o item DUAS vezes**,
  uma por arquivo — e nem a primeira nem a última é a resposta certa. Ele recebe
  os dois `item_db` (o `db/re/` e o nosso `db/guerra/`) e emite um registro por
  bloco; **a primeira é a do rAthena** (o `View` original, o `Type`, os
  `Locations` completos) e **a última é o nosso override** (que, sendo bloco
  parcial de YAML, só tem os campos que a gente declarou). Quem pega a primeira
  ignora a decisão que o servidor de fato usa — o `Footer: Imports:` faz o nosso
  arquivo vencer; quem pega a última perde tudo o que o override não repetiu.
  As duas leituras erradas estão em uso hoje: `instala_manto.py` pegava a
  primeira (corrigido em 2026-08-16, com mescla campo a campo) e
  `instala_visual.py` e `estende_accessoryid.py` montam um `dict` por
  compreensão, que fica com a última. São **16 itens** hoje, medidos: com o
  `dict`, o Cachecol Glorioso (15854) perde o `Type` e o `View: 2079` do
  `db/re/` e passa a **não parecer chapéu** — os 4 arquivos de arte de cabeça
  dele seriam pulados, calados.
  A leitura certa é **mesclar**, com o campo que o override declarou vencendo e
  o resto vindo do rAthena; ver `instala_manto.item_de`. Ver `PENDENCIAS.md` §1v.

- **Crase dentro de `python -c "..."` chamado pelo Bash EXECUTA o que está
  entre elas.** Aspas duplas não protegem crase — o shell faz substituição de
  comando antes de o Python ver a linha, e o texto some ou vira saída de outro
  programa. Num script que gera comentário para arquivo do projeto — onde crase
  é a marca de nome de arquivo e de comando — o estrago é **calado**: o arquivo
  é gravado, o `assert` da âncora passa, e o comentário sai mutilado. Medido em
  2026-08-18, ao acrescentar linha ao `scripts_guerra.conf`; a única pista foram
  três `command not found` no meio de um "ok" final. A saída é a mesma da
  armadilha do heredoc: **gerar texto por arquivo de script**, escrito com a
  ferramenta de escrita, e não por `-c` de uma linha.

- **`x += f()` em que `f` mexe em `x` perde o que `f` consumiu.** O `+=` guarda
  o `x` de antes de avaliar a direita. Num leitor de arquivo binário,
  `self.p += 4 * self._u32()` joga fora os 4 bytes gastos para ler o próprio
  contador, e o estouro aparece muitas seções adiante, longe da causa. O mesmo
  código em duas linhas funciona.

- **No `.gitignore`, negar um arquivo dentro de pasta excluída NÃO tem efeito —
  e o `git status` não denuncia, porque o arquivo simplesmente continua
  invisível.** Pasta excluída o git nem abre. `/db/import` mais
  `!/db/import/mob_skill_db.txt` deixa o arquivo ignorado do mesmo jeito; o que
  funciona é excluir o **conteúdo**, `/db/import/*`, e só então negar. Custou
  uma rodada em 2026-08-29, e o próprio `rathena/.gitignore` já descrevia a
  regra vinte linhas abaixo, na nota do `!/src/custom/` — que resolve o caso
  oposto (lá se quer a pasta inteira, e negar a pasta basta).
  **A sonda que decide não é `git check-ignore`**, que imprime a regra de
  negação e sai 0 dos dois jeitos: é `git status --short --untracked-files=all
  <pasta>`, que só lista o que o git realmente enxerga.

- Ferramentas rodam em **Python 2.7** (`C:\Python27\python.exe`).
