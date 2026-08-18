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

// Guerra do Emperium: escala do guardiao de castelo pela defesa investida. Os
// valores de verdade estao em conf/guerra/battle_guerra.txt; os padroes daqui
// sao os de quem clonar o repo sem esse arquivo, e por isso `guardiao_escala`
// nasce DESLIGADA - esta e regra de jogo nossa, nao comportamento de emulador,
// e clone sem a nossa conf tem de se comportar como rAthena puro. Os outros
// catorze valem so quando ela e ligada, e trazem a curva pedida em 2026-08-13
// para que ligar a chave sozinha ja de o resultado documentado.
// Ver src/custom/guardiao_do_castelo.hpp.
{ "guardiao_escala",                    &battle_config.guardiao_escala,                 0,      0,      1,              },
{ "guardiao_patamar_divisor",           &battle_config.guardiao_patamar_divisor,        10,     1,      INT_MAX,        },
{ "guardiao_patamar_max",               &battle_config.guardiao_patamar_max,            10,     0,      INT_MAX,        },
{ "guardiao_hp_base",                   &battle_config.guardiao_hp_base,                5000000, 1,     INT_MAX,        },
{ "guardiao_hp_passo",                  &battle_config.guardiao_hp_passo,               1000000, 0,     INT_MAX,        },
{ "guardiao_hp_max",                    &battle_config.guardiao_hp_max,                 15000000, 1,    INT_MAX,        },
{ "guardiao_atk_base",                  &battle_config.guardiao_atk_base,               5000,   1,      65535,          },
{ "guardiao_atk_passo",                 &battle_config.guardiao_atk_passo,              5000,   0,      65535,          },
{ "guardiao_atk_max",                   &battle_config.guardiao_atk_max,                50000,  1,      65535,          },
{ "guardiao_reducao_base",              &battle_config.guardiao_reducao_base,           5,      0,      99,             },
{ "guardiao_reducao_passo",             &battle_config.guardiao_reducao_passo,          5,      0,      99,             },
{ "guardiao_reducao_max",               &battle_config.guardiao_reducao_max,            50,     0,      99,             },
{ "guardiao_aspd_base",                 &battle_config.guardiao_aspd_base,              168,    0,      190,            },
{ "guardiao_aspd_passo",                &battle_config.guardiao_aspd_passo,             1,      0,      190,            },
{ "guardiao_aspd_max",                  &battle_config.guardiao_aspd_max,               178,    0,      190,            },
{ "guardiao_hit_base",                  &battle_config.guardiao_hit_base,               530,    1,      SHRT_MAX,       },
{ "guardiao_hit_passo",                 &battle_config.guardiao_hit_passo,              10,     0,      SHRT_MAX,       },
{ "guardiao_hit_max",                   &battle_config.guardiao_hit_max,                630,    1,      SHRT_MAX,       },

// Guerra do Emperium: cor do brilho de carta caindo. O valor de verdade esta em
// conf/guerra/battle_guerra.txt; o 0 aqui e o padrao de quem clonar o repo sem
// esse arquivo, ou seja DESLIGADO - esta e regra de jogo nossa, e clone sem a
// nossa conf tem de se comportar como rAthena puro.
// O teto e 6 e nao uma constante do `e_item_drop_effect` de proposito: aquele
// enum MUDA DE VALOR conforme o PACKETVER (src/map/itemdb.hpp:3262 - o branco
// saiu e o laranja virou verde em 2020-03-04), e este arquivo e incluido em
// battle.cpp, que nao inclui o itemdb.hpp. O 6 e o vermelho no nosso 20211103.
// Ver src/custom/brilho_da_carta.hpp.
{ "brilho_da_carta",                    &battle_config.brilho_da_carta,                 0,      0,      6,              },

