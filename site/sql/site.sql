-- Tabelas do site da Guerra do Emperium.
--
-- Moram no MESMO banco do rAthena, junto da `login`, e seguem o padrao do
-- sql-files/guerra_arena_pvp.sql: prefixo `guerra_` para separar o que e'
-- nosso do que e' do emulador. CHARSET latin1 como todo o resto deste
-- banco (CLAUDE.md secao 5).
--
-- Rodar com:
--   mysql -u guerra -p guerra < site/sql/site.sql

-- Liga uma conta ao documento que a autorizou.
--
-- POR QUE O HASH E NAO O NUMERO: a unica pergunta que o site faz e' "esse
-- documento ja tem conta?", e o hash responde igual. Guardar CPF ou celular
-- em claro so acrescentaria dano no dia de um vazamento. O hash e' HMAC com
-- o segredo do servidor (SITE_SEGREDO), e nao SHA-256 puro, porque CPF tem
-- so 11 digitos: alguem geraria a tabela inteira e reverteria um hash sem
-- chave em minutos.
--
-- CONSEQUENCIA QUE PRECISA ESTAR CLARA: trocar o SITE_SEGREDO invalida
-- todos os hashes ja gravados. As contas continuam funcionando, mas o
-- limite por documento deixa de reconhecer quem ja se cadastrou - todo
-- mundo ganha direito a mais uma conta. O segredo entra no backup e nao se
-- troca por capricho.
--
-- ------------------------------------------------------------------
-- POR QUE O account_id NASCE NULO, E POR QUE ISSO IMPORTA
--
-- A `login` do rAthena e' MyISAM, que NAO TEM TRANSACAO. Uma transacao
-- cobrindo as duas tabelas parece funcionar e nao funciona: o rollback nao
-- desfaz nada do lado da `login`. Se a conta fosse criada primeiro e a
-- gravacao do documento falhasse por duplicidade, sobraria uma conta
-- JOGAVEL e SEM DOCUMENTO - exatamente o furo que esta tabela existe para
-- fechar, aberto justamente por quem tentasse burla-la.
--
-- Entao a ordem e' invertida: RESERVA-SE O DOCUMENTO PRIMEIRO, com
-- account_id nulo, e a UNIQUE recusa o segundo pedido ali mesmo, antes de
-- qualquer conta nascer. So depois a conta e' criada e a reserva recebe o
-- account_id. Se a criacao falhar, a reserva e' apagada.
--
-- Preco: uma reserva pode ficar orfa se o processo morrer entre os dois
-- passos, e ela bloquearia aquele documento para sempre. Por isso o site
-- apaga reservas nulas com mais de 15 minutos antes de cada cadastro.
CREATE TABLE IF NOT EXISTS `guerra_site_cadastro` (
  `id`             int(11) unsigned NOT NULL AUTO_INCREMENT,
  `account_id`     int(11) unsigned DEFAULT NULL,
  `documento_hash` char(64)         NOT NULL,
  `documento_tipo` enum('cpf','celular') NOT NULL,
  `ip`             varchar(45)      NOT NULL DEFAULT '',
  `criado_em`      datetime         NOT NULL,
  PRIMARY KEY (`id`),

  -- A trava de verdade contra criacao desenfreada. A consulta que o site
  -- faz antes de inserir e' so' cortesia para dar mensagem boa: duas
  -- requisicoes simultaneas com o mesmo documento passariam pelas duas
  -- consultas e so' esbarrariam aqui.
  UNIQUE KEY `documento` (`documento_hash`),
  UNIQUE KEY `conta` (`account_id`),
  KEY `criado_em` (`criado_em`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ------------------------------------------------------------------
-- CHAMADOS ABERTOS PELO JOGADOR
--
-- Enquanto faltarem itens, traducoes, missoes e correcoes, o jogador
-- precisa de um lugar para avisar. Esta tabela e' esse lugar.
--
-- POR QUE utf8mb4 E NAO latin1, contra todo o resto deste banco:
-- as 105 colunas de texto do rAthena sao latin1 porque o JOGO as le', e o
-- cliente de 2021 nao entende outra coisa (CLAUDE.md secao 4.1). Chamado
-- nao passa pelo jogo em nenhum momento: nasce num formulario web (UTF-8),
-- e vai ser lido num painel web. Guardar em latin1 obrigaria a converter
-- nas duas pontas e perderia calado tudo o que nao couber em cp1252 - e
-- jogador escreve emoji em chamado.
--
-- O PRECO, e ele e' real: esta tabela NAO pode ser lida pela mesma conexao
-- que le' a `login` e a `char`. O site abre DUAS conexoes por isso - ver o
-- cabecalho de banco.go, que e' onde a decisao esta' documentada por
-- inteiro.
--
-- O ESTADO JA' NASCE AQUI, mesmo sem ninguem para le'-lo. O painel de
-- leitura vem depois (PENDENCIAS.md); acrescentar a coluna junto com ele
-- exigiria um ALTER TABLE numa tabela que ja' teria chamado dentro, e o
-- valor de um chamado antigo teria de ser adivinhado.
CREATE TABLE IF NOT EXISTS `guerra_site_chamado` (
  `id`            int(11) unsigned NOT NULL AUTO_INCREMENT,
  `account_id`    int(11) unsigned NOT NULL,

  -- Copia do nome da conta e do personagem no momento da abertura, e nao
  -- um JOIN. Nome de conta nao muda, mas personagem se apaga - e um
  -- chamado que diga "o item sumiu do meu Ferreiro" perde o sentido se o
  -- Ferreiro nao existir mais na hora de ler.
  `usuario`       varchar(23)      NOT NULL DEFAULT '',
  `personagem`    varchar(30)      NOT NULL DEFAULT '',

  `tipo`          enum('item','traducao','missao','mapa','conta','outro')
                                   NOT NULL DEFAULT 'outro',
  `assunto`       varchar(120)     NOT NULL,
  `mensagem`      text             NOT NULL,

  `estado`        enum('aberto','andamento','fechado') NOT NULL DEFAULT 'aberto',
  `resposta`      text             DEFAULT NULL,

  `ip`            varchar(45)      NOT NULL DEFAULT '',
  `criado_em`     datetime         NOT NULL,
  `fechado_em`    datetime         DEFAULT NULL,

  PRIMARY KEY (`id`),

  -- O teto de chamados por hora e' contado por conta; sem este indice a
  -- contagem varre a tabela inteira a cada abertura.
  KEY `conta_criado` (`account_id`, `criado_em`),

  -- A consulta do painel que ainda nao existe: os abertos, mais antigos
  -- primeiro.
  KEY `fila` (`estado`, `criado_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------
-- O QUE O ADMINISTRADOR FEZ COM A CONTA DE ALGUEM
--
-- O painel de usuarios (2026-09-10) bloqueia, suspende e libera conta
-- escrevendo direto na `login` do rAthena - que nao tem coluna nenhuma
-- para "quem fez", "quando" e "por que". Sem esta tabela, o unico registro
-- de um bloqueio seria a memoria de quem clicou.
--
-- E o MOTIVO importa mais do que parece: bloqueio sem motivo escrito vira
-- discussao com o jogador tres semanas depois, sem ninguem para arbitrar.
-- Ele e' o campo que o painel mostra de volta na ficha da conta.
--
-- POR QUE utf8mb4, e nao latin1 como a `login` ao lado: `motivo` e' texto
-- livre digitado por gente, com acento. Mesma decisao - e mesma conexao
-- (dbTexto) - da guerra_site_chamado; ver o cabecalho daquela tabela e o
-- de banco.go.
--
-- A COPIA DO NOME nas duas pontas (admin_usuario, alvo_usuario) segue a
-- regra do chamado: nome de conta nao muda, mas conta se apaga, e um
-- registro que diga "bloqueou a conta 2000031" nao serve para nada depois
-- que a 2000031 sumiu.
--
-- NAO HA ROTA QUE APAGUE LINHA DAQUI, e e' de proposito: registro de
-- moderacao que o proprio moderador apaga nao e' registro.
CREATE TABLE IF NOT EXISTS `guerra_site_admin_log` (
  `id`            int(11) unsigned NOT NULL AUTO_INCREMENT,

  `admin_id`      int(11) unsigned NOT NULL,
  `admin_usuario` varchar(23)      NOT NULL DEFAULT '',

  -- Nulo quando a acao nao e' sobre uma conta: liberar bloqueio de IP
  -- alcanca uma FAIXA (a.b.c.*), e nao um jogador.
  `alvo_id`       int(11) unsigned DEFAULT NULL,
  `alvo_usuario`  varchar(23)      NOT NULL DEFAULT '',

  `acao`          varchar(32)      NOT NULL,

  -- O que a acao fez, em numeros: "state 0 -> 5", "suspensa por 120 min",
  -- "faixa 187.12.3.*". E' o que permite reconstruir o estado de antes.
  `detalhe`       varchar(255)     NOT NULL DEFAULT '',
  `motivo`        varchar(255)     NOT NULL DEFAULT '',

  `ip`            varchar(45)      NOT NULL DEFAULT '',
  `criado_em`     datetime         NOT NULL,

  PRIMARY KEY (`id`),

  -- A consulta do painel: o historico de UMA conta, mais recente primeiro.
  KEY `alvo` (`alvo_id`, `criado_em`),
  KEY `quando` (`criado_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
