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

