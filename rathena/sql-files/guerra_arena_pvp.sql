--
-- Guerra do Emperium - Arena de Combate (Honra de Combate)
--
-- As duas tabelas de npc/guerra/honra_de_combate.txt. Prefixo `guerra_` para
-- que nenhuma delas se confunda com tabela do rAthena.
--
-- Aplicar:
--   mysql -h127.0.0.1 -uragnarok -p<senha> ragnarok < sql-files/guerra_arena_pvp.sql
--
-- MyISAM como o resto do main.sql. Sem transacao, e nao faz falta: os dois
-- INSERTs de uma morte sao independentes, e o pior caso de uma queda entre
-- eles e um ponto perdido, nao um placar corrompido.
--

--
-- O placar, e a FONTE DA VERDADE da pontuacao.
--
-- Existe porque a variavel de conta (#RepPointsPvP) so vai para acc_reg_num
-- quando o rAthena salva o personagem - autosave de 300s ou logout. Warp e
-- Asa de Borboleta NAO salvam (chrif_save nao e chamado ao trocar de mapa no
-- mesmo map-server), entao um placar lido de acc_reg_num mostraria numero
-- velho. Aqui a escrita e no instante da morte.
--
-- A variavel de conta e a COPIA que o modal de reputacao le, e o
-- OnPCLoginEvent a resincroniza a partir daqui - por isso uma queda do
-- map-server nao desencontra os dois.
--
CREATE TABLE IF NOT EXISTS `guerra_pvp_placar` (
  `account_id` int(11) unsigned NOT NULL,
  `nome` varchar(30) NOT NULL default '',
  `pontos` int(11) NOT NULL default '0',
  `atualizado` datetime NOT NULL,
  PRIMARY KEY (`account_id`),
  KEY `pontos` (`pontos`)
) ENGINE=MyISAM;

--
-- O livro-caixa do anti-conluio: um saldo assinado por PAR DE CONTAS por DIA.
--
-- `conta_a` e SEMPRE a menor das duas, e o saldo e do ponto de vista dela:
-- a matou b soma +1, b matou a soma -1. Assim o par tem uma linha so, e nao
-- duas que precisariam ser somadas.
--
-- Preso em [-2, +2] pelo script. Revezamento honesto (um mata, o outro mata
-- de volta) mantem o saldo perto de zero e continua pontuando o dia inteiro;
-- fazenda de um lado so trava no terceiro golpe.
--
-- `dia` e DATE, entao a virada e a meia-noite do servidor - o que foi pedido,
-- e mais simples que janela deslizante de 24h: nao guarda hora de cada morte.
--
-- Linha antiga nao atrapalha nada (a consulta sempre filtra por CURDATE()),
-- mas cresce. Se um dia incomodar:
--   DELETE FROM guerra_pvp_confronto WHERE dia < CURDATE() - INTERVAL 30 DAY;
--
CREATE TABLE IF NOT EXISTS `guerra_pvp_confronto` (
  `dia` date NOT NULL,
  `conta_a` int(11) unsigned NOT NULL,
  `conta_b` int(11) unsigned NOT NULL,
  `saldo` int(11) NOT NULL default '0',
  PRIMARY KEY (`dia`,`conta_a`,`conta_b`)
) ENGINE=MyISAM;
