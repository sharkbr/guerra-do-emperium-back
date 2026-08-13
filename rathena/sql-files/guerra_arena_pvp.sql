--
-- Guerra do Emperium - Arena de Combate (Honra de Combate)
--
-- A tabela de npc/guerra/honra_de_combate.txt. Prefixo `guerra_` para que ela
-- nao se confunda com tabela do rAthena.
--
-- Aplicar:
--   mysql -h127.0.0.1 -uragnarok -p<senha> ragnarok < sql-files/guerra_arena_pvp.sql
--
-- MyISAM como o resto do main.sql. Sem transacao, e nao faz falta: os dois
-- INSERTs de uma morte sao independentes, e o pior caso de uma queda entre
-- eles e um ponto perdido, nao um placar corrompido.
--
-- ERAM DUAS TABELAS ATE 2026-08-13. A segunda, `guerra_pvp_confronto`, era o
-- livro-caixa do anti-conluio: um saldo assinado por PAR DE CONTAS por DIA,
-- preso em [-2, +2], que travava revezamento no terceiro golpe do dia. O dono
-- pediu a retirada da regra inteira ("por enquanto as pessoas podem ficar
-- criando char ou ate conta pra isso, mas vamos observar primeiro"), entao o
-- script parou de escrever nela e o CREATE saiu daqui.
--
-- A TABELA CONTINUA NO BANCO de quem ja rodou este arquivo, sem ninguem
-- escrever nela. Nao atrapalha; para limpar:
--   DROP TABLE guerra_pvp_confronto;
-- O caminho de volta e o git, que tem o CREATE e o script na mesma revisao.
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
-- `pontos` NAO TEM PISO NA COLUNA, e sim no UPDATE: o script escreve
-- `GREATEST(pontos + <delta>, -10)`. O -10 tem de ser o mesmo `Minimum:` do
-- Id 5 em db/guerra/reputation.yml, que e onde o modal trava - sem os dois
-- iguais, a tabela desce e a tela para, caladas. Nao ha CHECK aqui porque
-- MyISAM ignora CHECK: quem garante o piso e a expressao do script.
--
CREATE TABLE IF NOT EXISTS `guerra_pvp_placar` (
  `account_id` int(11) unsigned NOT NULL,
  `nome` varchar(30) NOT NULL default '',
  `pontos` int(11) NOT NULL default '0',
  `atualizado` datetime NOT NULL,
  PRIMARY KEY (`account_id`),
  KEY `pontos` (`pontos`)
) ENGINE=MyISAM;
