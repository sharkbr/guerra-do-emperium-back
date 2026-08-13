// Copyright (c) rAthena Dev Teams - Licensed under GNU GPL
// For more information, see LICENCE in the main folder

/**
 * Custom battle config structure
 * Place the definition of custom battle configuration structure members in this file.
 *
 * Make sure that the name you want is not already taken by looking into battle.hpp
 * Do not forget to add initilization logic to battle_config_init.inc
 *
 * Format:
 *	 <datatype> name;
 **/

// Guerra do Emperium: refino maximo que a janela de refino aceita.
// Usado em src/custom/refino.hpp. 0 desliga a trava.
int32 refino_teto;

// Guerra do Emperium: teto da reducao de dano por carta, em MILESIMOS.
// 999 = 99,9%; 1000 desliga a trava (comportamento do rAthena).
// Usado em src/custom/reducao_de_dano.hpp.
int32 reducao_dano_teto;

// Guerra do Emperium: quanto do dano PASSA nos mapas `pvp`, em PORCENTAGEM -
// 100 e sem reducao, 20 e reducao de 80%. Mesma semantica dos
// gvg_*_attack_damage_rate do rAthena. Usados em src/custom/reducao_geral.hpp.
int32 pvp_dano_arma;   // habilidade de arma
int32 pvp_dano_magia;  // habilidade de magia
int32 pvp_dano_misc;   // habilidade "misc"
int32 pvp_dano_curta;  // ataque normal corpo a corpo
int32 pvp_dano_longa;  // ataque normal a distancia

// Guerra do Emperium: a reducao geral isenta habilidade com
// `IgnoreGvgReduction`? 0 = ninguem escapa (nosso), 1 = comportamento do
// rAthena. Vale para a guerra E para os mapas `pvp` de uma vez.
// Usado em src/custom/reducao_geral.hpp.
int32 reducao_dano_isenta_habilidade;

// Guerra do Emperium: a escala do guardiao de castelo pela DEFESA investida.
// Os quatro atributos seguem a mesma forma - `base + passo * patamar`, cortada
// por um teto -, e o patamar e `defesa / divisor`. Usados em
// src/custom/guardiao_do_castelo.hpp.
int32 guardiao_escala;            // 0 desliga tudo e devolve o rAthena
int32 guardiao_patamar_divisor;   // defesa / isto = patamar
int32 guardiao_patamar_max;       // teto do patamar
int32 guardiao_hp_base;
int32 guardiao_hp_passo;
int32 guardiao_hp_max;
int32 guardiao_atk_base;
int32 guardiao_atk_passo;
int32 guardiao_atk_max;
int32 guardiao_reducao_base;      // reducao do dano RECEBIDO, em porcentagem
int32 guardiao_reducao_passo;
int32 guardiao_reducao_max;       // 99 e o maximo que o `damagetaken` expressa
int32 guardiao_aspd_base;         // ASPD de jogador; 190 e o teto do emulador
int32 guardiao_aspd_passo;
int32 guardiao_aspd_max;
int32 guardiao_hit_base;          // precisao ABSOLUTA; `hit - esquiva` = chance %
int32 guardiao_hit_passo;
int32 guardiao_hit_max;

