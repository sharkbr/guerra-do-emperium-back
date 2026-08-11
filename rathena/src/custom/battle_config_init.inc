// Copyright (c) rAthena Dev Teams - Licensed under GNU GPL
// For more information, see LICENCE in the main folder

/**
 * Custom battle config initializations
 * Place the definition of custom battle configuration initializations in this file.
 *
 * Do not forget to add a comma at the end of the line, if you want to add another config
 *
 * Format:
 *	 { "name", &battle_config.<variable name>, <default value>, <minimum value>, <maximum value> },
 **/

// Guerra do Emperium: teto de refino. O valor de verdade esta em
// conf/guerra/battle_guerra.txt; o 16 aqui e so o padrao de quem clonar o
// repo sem esse arquivo. Ver src/custom/refino.hpp.
{ "refino_teto",                        &battle_config.refino_teto,                     16,     0,      MAX_REFINE,     },

// Guerra do Emperium: teto da reducao de dano por carta, em milesimos.
// O valor de verdade esta em conf/guerra/battle_guerra.txt; o 999 aqui e
// so o padrao de quem clonar o repo sem esse arquivo. 1000 desliga a
// trava. Ver src/custom/reducao_de_dano.hpp.
{ "reducao_dano_teto",                  &battle_config.reducao_dano_teto,               999,    0,      1000,           },

// Guerra do Emperium: reducao geral de dano nos mapas `pvp`. Quanto do dano
// PASSA, em porcentagem - 100 e sem reducao, 30 e reducao de 70%. Os valores de
// verdade estao em conf/guerra/battle_guerra.txt; o 100 aqui e o padrao de quem
// clonar o repo sem esse arquivo, ou seja NENHUMA reducao. Isso e de proposito:
// esta e uma regra de jogo nossa, nao comportamento de emulador - um clone sem
// a nossa conf tem de se comportar como rAthena puro.
// Ver src/custom/reducao_geral.hpp.
{ "pvp_dano_arma",                      &battle_config.pvp_dano_arma,                   100,    0,      INT_MAX,        },
{ "pvp_dano_magia",                     &battle_config.pvp_dano_magia,                  100,    0,      INT_MAX,        },
{ "pvp_dano_misc",                      &battle_config.pvp_dano_misc,                   100,    0,      INT_MAX,        },
{ "pvp_dano_curta",                     &battle_config.pvp_dano_curta,                  100,    0,      INT_MAX,        },
{ "pvp_dano_longa",                     &battle_config.pvp_dano_longa,                  100,    0,      INT_MAX,        },

// Guerra do Emperium: a reducao geral isenta habilidade com `IgnoreGvgReduction`
// (Chuva de Moedas e GN_FIRE_EXPANSION_ACID)? O valor de verdade esta em
// conf/guerra/battle_guerra.txt, e la e 0 - ninguem escapa. O 1 aqui e o padrao
// de quem clonar o repo sem esse arquivo, e e o comportamento do rAthena.
// Ver src/custom/reducao_geral.hpp.
{ "reducao_dano_isenta_habilidade",     &battle_config.reducao_dano_isenta_habilidade,  1,      0,      1,              },

