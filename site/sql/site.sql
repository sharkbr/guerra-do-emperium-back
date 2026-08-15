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
