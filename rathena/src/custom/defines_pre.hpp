// Copyright (c) rAthena Dev Teams - Licensed under GNU GPL
// For more information, see LICENCE in the main folder

#ifndef CONFIG_CUSTOM_DEFINES_PRE_HPP
#define CONFIG_CUSTOM_DEFINES_PRE_HPP

/**
 * rAthena configuration file (http://rathena.org)
 * For detailed guidance on these check http://rathena.org/wiki/SRC/config/
 **/

// Versao do cliente, em AAAAMMDD. Define as tabelas de pacote inteiras: o
// formato exato dos bytes trocados com o cliente. Errar aqui nao da erro
// claro, da bug silencioso (item no slot errado, tela que congela).
//
// 20211103 e a data de compilacao real do executavel que usamos: timestamp
// 1635924593 no PE header = 2021-11-03 07:29 UTC (16:29 KST). Coincide com o
// padrao do proprio rAthena, que e a trilha mais testada.
//
// O executavel e o `2021-11-03_Ragexe_1635926200`, DESEMPACOTADO, obtido do
// repositorio do NEMO. Nao e o Ragexe.exe do instalador oficial da Gravity:
// aquele e blindado com WinLicense/Themida (o PE dele tem secoes `.winlice` e
// `.boot` mais 5 sem nome) e nenhuma ferramenta de patch consegue le-lo. O
// WARP falha em todo patch porque nao encontra `clientinfo`, `langtype` nem
// `data.grf` no binario - o desempacotado tem os tres.
//
// Os DADOS (data.grf, BGM/, System/) continuam vindo do instalador oficial da
// Gravity, com SHA256 conferido. Eles nao sao protegidos e sao a fonte mais
// confiavel. Somente o executavel foi substituido.
//
// ATENCAO ao conferir a data no WARP: ele converte o timestamp para o fuso
// LOCAL da maquina, entao em Brasilia (UTC-3) uma data pode aparecer como o dia
// anterior. Comparar sempre em UTC ou KST, nunca no fuso local.
#define PACKETVER 20211103

// Quantas mensagens de map-server cabem na tabela. O padrao do rAthena e 1550
// (src/map/map.cpp), e ele ja usa ate a 1540 - sobram nove numeros, que o
// upstream vai ocupar na proxima atualizacao. Mensagem nossa em cima de
// numero que o rAthena passe a usar nao da erro: simplesmente troca o texto
// de uma mensagem dele, calado.
//
// Subindo o teto, a faixa 1550+ e so nossa. Cada numero custa um ponteiro na
// tabela, entao a folga e de graca. As mensagens ficam em
// conf/guerra/map_msg_guerra.conf.
//
// O rAthena documenta este define exatamente aqui - ver o comentario no topo
// de conf/msg_conf/map_msg.conf.
#define MAP_MAX_MSG 1600

#endif /* CONFIG_CUSTOM_DEFINES_PRE_HPP */
