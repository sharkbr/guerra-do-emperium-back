# Catálogo de cutins — os retratos de NPC deste cliente

> Gerado por `ferramentas/catalogo_cutins.py`. Para refazer:
> `python ferramentas/catalogo_cutins.py <data.grf> CATALOGO-CUTINS.md`

**1294** ilustrações de nome ASCII, em 134 prefixos.
Existem ainda **59** de nome coreano, fora desta lista: o nome teria de
ser escrito em CP949 dentro do script, o que não vale o trabalho.

## Como usar

```
mes "[Emissario da Ordem]";
cutin "kafra_01",2;      // 2 = canto inferior direito
mes "Boa viagem.";
close2;
cutin "",255;            // 255 = limpa a tela
end;
```

Posições: `0` inferior esquerdo, `1` inferior centro, `2` inferior
direito, `3` centro em janela arrastável, `4` centro sem moldura,
`255` limpa tudo.

**A armadilha:** o cliente desenha um cutin por vez e ele NÃO some
sozinho quando o diálogo fecha. Sem o `cutin "",255;` antes do `end`,
a ilustração fica na tela do jogador até ele falar com outro NPC que
a troque. Todo caminho que sai do script precisa limpar — inclusive
os que saem por `close` no meio de um `if`.

## Onde a arte mora

Dentro do `data.grf`, em `data\texture\유저인터페이스\illust\`
(`유저인터페이스` = "interface do usuário", em CP949).

Não confundir com `data\texture\userinterface\illust`, que também
existe no GRF com 106 arquivos de nome ASCII: **o executável não lê
essa pasta para cutin.** A única string ASCII de illust dentro dele é
`UserInterface\illust\PET_NOIMAGE.bmp`, um caso isolado. Arte posta
lá não aparece.

Para pôr ilustração nossa, o caminho é o mesmo dos outros overrides:
gravar o `.bmp` em `cliente\data\texture\유저인터페이스\illust\`,
que vence o GRF pelo `DataFolderFirst`. Magenta (`#FF00FF`) é tratado
como transparente. O tamanho típico é 320x480; acima de ~700x700 o
cliente trava por um instante ao carregar.

## Por que não dá para pré-visualizar tudo fora do jogo

**742** dos arquivos desta pasta estão com a flag DES do GRF ligada, e o
`ferramentas/grf.py` recusa esses de propósito — ele não implementa a
cifra. O cliente lê todos normalmente; a limitação é só nossa. O DES
bate justamente nos retratos clássicos de NPC (`job_*`, `aca_*`,
`nov_*`, `moc_*` e quase todos os `kafra_*`), então extrair só os
livres dá uma amostra enviesada.

Duas saídas: um extrator de GRF que saiba DES (o GRF Editor, do Tokei,
mostra miniatura), ou testar no jogo mesmo — `cutin` aceita qualquer
nome desta lista e o custo de errar é ver a tela em branco.

## Os nomes

### `ep` — 314

`ep13_ahat_f`, `ep13_ahat_m`, `ep13_captin_edq`, `ep13_cheshire`, `ep13_cheshire_h`, `ep13_heslanta`, `ep13_loki01`, `ep13_loki02`, `ep13_plant01`, `ep13_shadow_edq`, `ep13_shy`, `ep143_taang`, `ep143_tadir`, `ep143_tahuk`, `ep143_tasmi`, `ep143_tasta`, `ep14_bif01`, `ep14_bif02`, `ep14_bif03`, `ep14_etran0`, `ep14_etran01`, `ep14_etran1`, `ep14_etran2`, `ep14_etran3`, `ep14_etran4`, `ep14_etran5`, `ep14_etran6`, `ep14_etran7`, `ep14_etran8`, `ep14_nyd01`, `ep14_nyd02`, `ep14_nyd03`, `ep14_nyd04`, `ep14_pro_worm`, `ep14_robert0`, `ep14_robert01`, `ep14_robert1`, `ep14_robert2`, `ep14_robert3`, `ep14_robert4`, `ep14_robert5`, `ep14_roki01`, `ep14_roki02`, `ep14_yai01`, `ep15_2_brt_1`, `ep15_2_brt_2`, `ep15_2_brt_3`, `ep15_2_brt_4`, `ep15_2_brt_5`, `ep15_2_brt_6`, `ep15_2_brt_7`, `ep15_2_fru_1`, `ep15_2_fru_2`, `ep15_2_fru_3`, `ep15_rekenber01`, `ep15_rekenber02`, `ep15_tatio01`, `ep15_tatio02`, `ep15_tatio03`, `ep162_ctn01`, `ep162_ctn01.png`, `ep162_ctn02`, `ep162_ctn02.png`, `ep162_dn01`, `ep162_dn01.png`, `ep162_dn02`, `ep162_dn02.png`, `ep162_dn03`, `ep162_dn03.png`, `ep162_dn04`, `ep162_dn04.png`, `ep162_dr_cut`, `ep162_est01`, `ep162_est01.png`, `ep162_est02`, `ep162_est02.png`, `ep162_est03`, `ep162_est03.png`, `ep162_rds01`, `ep162_rds01.png`, `ep162_rds02`, `ep162_rds02.png`, `ep162_rds03`, `ep162_rds03.png`, `ep162_rds04`, `ep162_rds04.png`, `ep162_rds05`, `ep162_rds05.png`, `ep16_crux_findel01`, `ep16_crux_findel01.png`, `ep16_crux_findel02`, `ep16_crux_findel02.png`, `ep16_crux_findel02_1`, `ep16_crux_findel02_1.png`, `ep16_crux_findel03`, `ep16_crux_findel03.png`, `ep16_crux_findel04`, `ep16_crux_findel04.png`, `ep16_eisen01`, `ep16_eisen01.png`, `ep16_eisen02`, `ep16_eisen02.png`, `ep16_eisen03`, `ep16_eisen03.png`, `ep16_evil101`, `ep16_evil101.png`, `ep16_evil102`, `ep16_evil102.png`, `ep16_evil103`, `ep16_evil103.png`, `ep16_evil201`, `ep16_evil201.png`, `ep16_evil202`, `ep16_evil202.png`, `ep16_evil203`, `ep16_evil203.png`, `ep16_evt_ws`, `ep16_friedrich_stolz_heine`, `ep16_friedrich_stolz_heine.png`, `ep16_kronecker_granz_heine`, `ep16_kronecker_granz_heine.png`, `ep16_nihi_miseria_heine01`, `ep16_nihi_miseria_heine01.png`, `ep16_nihi_miseria_heine02`, `ep16_nihi_miseria_heine02.png`, `ep16_nihi_miseria_heine03`, `ep16_nihi_miseria_heine03.png`, `ep16_nihi_miseria_heine04`, `ep16_nihi_miseria_heine04.png`, `ep16_petter_heine01`, `ep16_petter_heine01.png`, `ep16_petter_heine02`, `ep16_petter_heine02.png`, `ep16_seiren01`, `ep16_seiren01.png`, `ep16_seiren02`, `ep16_seiren02.png`, `ep16_skia_nerius01`, `ep16_skia_nerius01.png`, `ep16_skia_nerius02`, `ep16_skia_nerius02.png`, `ep16_skia_nerius03`, `ep16_skia_nerius03.png`, `ep16_skia_nerius04`, `ep16_skia_nerius04.png`, `ep16_skia_shadow01`, `ep16_skia_shadow01.png`, `ep16_skia_shadow02`, `ep16_skia_shadow02.png`, `ep16_skia_shadow03`, `ep16_skia_shadow03.png`, `ep16_skia_shadow04`, `ep16_skia_shadow04.png`, `ep16_skia_shadow05`, `ep16_skia_shadow05.png`, `ep16_spica_nerius01`, `ep16_spica_nerius01.png`, `ep16_spica_nerius02`, `ep16_spica_nerius02.png`, `ep16_spica_nerius03`, `ep16_spica_nerius03.png`, `ep16_spica_nerius04`, `ep16_spica_nerius04.png`, `ep16_spica_nerius05`, `ep16_spica_nerius05.png`, `ep16_spica_nerius06`, `ep16_spica_nerius06.png`, `ep16_spica_nerius07`, `ep16_spica_nerius07.png`, `ep16_spica_nerius08`, `ep16_spica_nerius08.png`, `ep16_tes01`, `ep16_tes01.png`, `ep16_tes02`, `ep16_tes02.png`, `ep16_tes03`, `ep16_tes03.png`, `ep16cook_king_1`, `ep16cook_king_2`, `ep16gao_1`, `ep16gao_2`, `ep16gao_3`, `ep171_as01`, `ep171_as01.png`, `ep171_as02`, `ep171_as02.png`, `ep171_as03`, `ep171_as03.png`, `ep171_coronation`, `ep171_elyumina01`, `ep171_elyumina01.png`, `ep171_elyumina02`, `ep171_elyumina02.png`, `ep171_elyumina03`, `ep171_elyumina03.png`, `ep171_elyumina04`, `ep171_elyumina04.png`, `ep171_kaya01`, `ep171_kaya01.png`, `ep171_kaya02`, `ep171_kaya02.png`, `ep171_kaya03`, `ep171_kaya03.png`, `ep171_miguel01`, `ep171_miguel01.png`, `ep171_miguel02`, `ep171_miguel02.png`, `ep171_miguel03`, `ep171_miguel03.png`, `ep171_morning01`, `ep171_morning01.png`, `ep171_morning02`, `ep171_morning02.png`, `ep171_morning03`, `ep171_morning03.png`, `ep171_nihil01`, `ep171_nihil01.png`, `ep171_nihil02`, `ep171_nihil02.png`, `ep171_trio_memory`, `ep172_alpha`, `ep172_alpha.png`, `ep172_barmund_a01`, `ep172_barmund_a01.png`, `ep172_barmund_a02`, `ep172_barmund_a02.png`, `ep172_barmund_a03`, `ep172_barmund_a03.png`, `ep172_barmund_b01`, `ep172_barmund_b01.png`, `ep172_barmund_b02`, `ep172_barmund_b02.png`, `ep172_barmund_b03`, `ep172_barmund_b03.png`, `ep172_barmund_b04`, `ep172_barmund_b04.png`, `ep172_barmund_b05`, `ep172_barmund_b05.png`, `ep172_beta`, `ep172_beta.png`, `ep172_beta_ng`, `ep172_beta_ng.png`, `ep172_guard`, `ep172_guard.png`, `ep172_guard_ng`, `ep172_guard_ng.png`, `ep172_nillem01`, `ep172_nillem01.png`, `ep172_nillem02`, `ep172_nillem02.png`, `ep172_nillem03`, `ep172_nillem03.png`, `ep172_nillem04`, `ep172_nillem04.png`, `ep172_nillem05`, `ep172_nillem05.png`, `ep172_nillem06`, `ep172_nillem06.png`, `ep172_omega`, `ep172_omega.png`, `ep172_sweety01`, `ep172_sweety01.png`, `ep172_sweety02`, `ep172_sweety02.png`, `ep172_sweety03`, `ep172_sweety03.png`, `ep172_sweety04`, `ep172_sweety04.png`, `ep172_tamarin01`, `ep172_tamarin01.png`, `ep172_tamarin02`, `ep172_tamarin02.png`, `ep172_tamarin03`, `ep172_tamarin03.png`, `ep172_tamarin04`, `ep172_tamarin04.png`, `ep18_alf_01.png`, `ep18_alf_02.png`, `ep18_alf_03.png`, `ep18_alf_04.png`, `ep18_alf_05.png`, `ep18_bagot_01.png`, `ep18_bagot_02.png`, `ep18_bagot_03.png`, `ep18_demifreya.png`, `ep18_dew_01.png`, `ep18_dew_02.png`, `ep18_dew_03.png`, `ep18_dew_04.png`, `ep18_dew_05.png`, `ep18_imril_01.png`, `ep18_imril_02.png`, `ep18_imril_03.png`, `ep18_imril_04.png`, `ep18_maram_01.png`, `ep18_maram_02.png`, `ep18_maram_03.png`, `ep18_mark_01.png`, `ep18_mark_02.png`, `ep18_mark_03.png`, `ep18_mark_04.png`, `ep18_merchant.png`, `ep18_miriam_01.png`, `ep18_miriam_02.png`, `ep18_miriam_03.png`, `ep18_shulang.png`, `ep18_suad_01.png`, `ep18_suad_02.png`, `ep18_suad_03.png`, `ep18_suad_04.png`, `ep18_tamarin_01.png`, `ep18_tamarin_02.png`, `ep18_tamarin_03.png`, `ep18_tamarin_04.png`

### `(sem prefixo)` — 164

`09_moon_evt`, `1`, `1-1`, `162elena_01`, `162elena_01.png`, `162elena_02`, `162elena_02.png`, `16agn_ang`, `16agn_ang.png`, `16agn_nor`, `16agn_nor.png`, `16go_01`, `16go_01.png`, `16go_02`, `16go_02.png`, `16go_03`, `16go_03.png`, `16hel`, `16hel.png`, `16isa`, `16isa.png`, `16jur_nor`, `16jur_nor.png`, `16jur_sim`, `16jur_sim.png`, `16kat_ang`, `16kat_ang.png`, `16kat_nor`, `16kat_nor.png`, `16lei_01`, `16lei_01.png`, `16lei_02`, `16lei_02.png`, `16lei_03`, `16lei_03.png`, `16loo_01`, `16loo_01.png`, `16loo_02`, `16loo_02.png`, `16loo_03`, `16loo_03.png`, `16mye_ang`, `16mye_ang.png`, `16mye_nor`, `16mye_nor.png`, `16wol_ang`, `16wol_ang.png`, `16wol_nor`, `16wol_nor.png`, `177_01`, `177_02`, `177_03`, `177_04`, `177_05`, `2`, `2-1`, `2010_new`, `2013_summer_fish_1`, `2013_summer_fish_2`, `2013_summer_fish_3`, `2013_summer_fish_4`, `2013_summer_fish_5`, `2013_summer_fish_6`, `3`, `3-1`, `3rd_ab_anghilde01`, `3rd_ab_anghilde02`, `3rd_ab_anghilde03`, `3rd_ab_valkyrie`, `3rd_gc_daora01`, `3rd_gc_daora02`, `3rd_gn_dbris01`, `3rd_gn_dbris02`, `3rd_gn_dbris03`, `3rd_gn_dbris04`, `3rd_gn_dbris05`, `3rd_gn_dbris06`, `3rd_gn_demi01`, `3rd_gn_demi02`, `3rd_kim_normal01`, `3rd_kim_normal02`, `3rd_kim_normal03`, `3rd_kim_normal04`, `3rd_mechanic`, `3rd_mins_bardsong01`, `3rd_mins_bardsong02`, `3rd_mins_bardsong03`, `3rd_mins_bardsong04`, `3rd_mins_song01`, `3rd_mins_song02`, `3rd_mins_song03`, `3rd_mins_song04`, `3rd_ranger`, `3rd_rg_heinrich01`, `3rd_rg_heinrich02`, `3rd_rg_heinrich03`, `3rd_rg_schmitt01`, `3rd_rg_schmitt02`, `3rd_rg_schmitt03`, `3rd_rune_knight`, `3rd_sc_doomk01`, `3rd_sc_doomk02`, `3rd_sc_doomk03`, `3rd_sc_doomk04`, `3rd_sc_doomk05`, `3rd_sc_doomk06`, `3rd_scr_caracas01`, `3rd_scr_merito01`, `3rd_scr_merito02`, `3rd_scr_merito03`, `3rd_scr_merito04`, `3rd_sura_bruno01`, `3rd_sura_bruno02`, `3rd_sura_bruno03`, `3rd_sura_bruno04`, `3rd_sura_bruno05`, `3rd_sura_master`, `3rd_wd_kimdancer01`, `3rd_wd_kimdancer02`, `3rd_wd_songguitar01`, `3rd_wd_songguitar02`, `3rd_wd_songguitar03`, `3rd_wd_songguitar04`, `3rd_wd_songguitar05`, `3rd_wd_songguitar06`, `3rd_wl_queen01`, `3rd_wl_queen02`, `3rd_wl_queen03`, `3rd_wl_queen04`, `3rd_wl_queen05`, `3rd_wl_queen06`, `4`, `4-1`, `4job_einhar_01.png`, `4job_einhar_02.png`, `4job_gregor_01.png`, `4job_gregor_02.png`, `4job_gregor_03.png`, `4job_gregor_04.png`, `4job_leticia_01.png`, `4job_leticia_02.png`, `4job_leticia_03.png`, `4job_leticia_04.png`, `4job_leticia_05.png`, `4job_maggi_01.png`, `4job_maggi_02.png`, `4job_maggi_03.png`, `4job_maggi_04.png`, `4job_maura_01.png`, `4job_maura_02.png`, `4job_maura_03.png`, `4job_maura_04.png`, `4job_robin_01.png`, `4job_robin_02.png`, `4job_robin_03.png`, `4job_serang_01.png`, `4job_serang_02.png`, `4job_silla_01.png`, `4job_silla_02.png`, `4job_silla_03.png`, `4job_silla_04.png`, `4job_silla_05.png`, `5`, `5-1`

### `hair` — 70

`hair_dr_f_01`, `hair_dr_f_02`, `hair_dr_f_03`, `hair_dr_f_04`, `hair_dr_f_05`, `hair_dr_f_06`, `hair_dr_m_01`, `hair_dr_m_02`, `hair_dr_m_03`, `hair_dr_m_04`, `hair_dr_m_05`, `hair_dr_m_06`, `hair_f_01`, `hair_f_02`, `hair_f_03`, `hair_f_04`, `hair_f_05`, `hair_f_06`, `hair_f_07`, `hair_f_08`, `hair_f_09`, `hair_f_10`, `hair_f_11`, `hair_f_12`, `hair_f_13`, `hair_f_14`, `hair_f_15`, `hair_f_16`, `hair_f_17`, `hair_f_18`, `hair_f_19`, `hair_f_20`, `hair_f_21`, `hair_f_22`, `hair_f_23`, `hair_f_24`, `hair_f_25`, `hair_f_26`, `hair_f_27`, `hair_f_28`, `hair_f_29`, `hair_m_01`, `hair_m_02`, `hair_m_03`, `hair_m_04`, `hair_m_05`, `hair_m_06`, `hair_m_07`, `hair_m_08`, `hair_m_09`, `hair_m_10`, `hair_m_11`, `hair_m_12`, `hair_m_13`, `hair_m_14`, `hair_m_15`, `hair_m_16`, `hair_m_17`, `hair_m_18`, `hair_m_19`, `hair_m_20`, `hair_m_21`, `hair_m_22`, `hair_m_23`, `hair_m_24`, `hair_m_25`, `hair_m_26`, `hair_m_27`, `hair_m_28`, `hair_m_29`

### `lhz` — 45

`lhz_benkaistin01`, `lhz_benkaistin02`, `lhz_benkaistin03`, `lhz_benkaistin04`, `lhz_diguts01`, `lhz_diguts02`, `lhz_diguts03`, `lhz_diguts04`, `lhz_diguts05`, `lhz_diguts06`, `lhz_diguts07`, `lhz_diguts08`, `lhz_karl`, `lhz_kaz01`, `lhz_kaz02`, `lhz_kaz03`, `lhz_kaz04`, `lhz_kaz05`, `lhz_kaz06`, `lhz_kaz07`, `lhz_kaz08`, `lhz_kaz09`, `lhz_kaz10`, `lhz_kaz11`, `lhz_macu01`, `lhz_macu02`, `lhz_macu03`, `lhz_macu04`, `lhz_macu05`, `lhz_macu06`, `lhz_macu07`, `lhz_ryo01`, `lhz_ryo02`, `lhz_ryo03`, `lhz_ryo04`, `lhz_ryo05`, `lhz_ryo06`, `lhz_ryo07`, `lhz_ryo08`, `lhz_ryo09`, `lhz_ryo10`, `lhz_ryo11`, `lhz_ryo12`, `lhz_ryo13`, `lhz_ryo14`

### `bio` — 35

`bio_eremes01`, `bio_eremes02`, `bio_eremes03`, `bio_eremes04`, `bio_eremes05`, `bio_harword01`, `bio_harword02`, `bio_harword03`, `bio_harword04`, `bio_harword05`, `bio_harword06`, `bio_katrinn01`, `bio_katrinn02`, `bio_katrinn03`, `bio_katrinn04`, `bio_seyren01`, `bio_seyren02`, `bio_seyren03`, `bio_seyren04`, `bio_seyren05`, `bio_seyren06`, `bio_shecil01`, `bio_shecil02`, `bio_shecil03`, `bio_shecil04`, `bio_shecil05`, `bio_shecil06`, `bio_sorin01`, `bio_sorin02`, `bio_sorin03`, `bio_worsev01`, `bio_worsev02`, `bio_worsev03`, `bio_ygnizem01`, `bio_ygnizem02`

### `bu` — 32

`bu_alp1`, `bu_alp2`, `bu_alp3`, `bu_alp4`, `bu_alp5`, `bu_du1`, `bu_du2`, `bu_du3`, `bu_du4`, `bu_du5`, `bu_maggi1`, `bu_maggi2`, `bu_maggi3`, `bu_maggi4`, `bu_mark1`, `bu_mark2`, `bu_mark3`, `bu_mark4`, `bu_oliver0`, `bu_oliver1`, `bu_oliver2`, `bu_oliver3`, `bu_oliver4`, `bu_oliver5`, `bu_oliver6`, `bu_oliver7`, `bu_oliver81`, `bu_oliver82`, `bu_oliver83`, `bu_oliver84`, `bu_oliver85`, `bu_oliver86`

### `v` — 31

`v_breid01`, `v_breid02`, `v_breid03`, `v_breid04`, `v_breid05`, `v_breid06`, `v_choco01`, `v_choco02`, `v_jinha01`, `v_jinha02`, `v_jinha03`, `v_jinha04`, `v_jinha05`, `v_jinha06`, `v_jinha07`, `v_jinha08`, `v_seryu01`, `v_seryu02`, `v_seryu03`, `v_seryu04`, `v_seryu05`, `v_seryu06`, `v_seryu07`, `v_seryu08`, `v_seryu09`, `v_seryu10`, `v_sprakki01`, `v_sprakki02`, `v_sprakki03`, `v_sprakki04`, `v_sprakki05`

### `ex` — 26

`ex_nw_gerhold.png`, `ex_sa_masterj01.png`, `ex_sa_masterj02.png`, `ex_sa_masterj03.png`, `ex_sa_seo01.png`, `ex_sa_seo02.png`, `ex_se_happycloud01.png`, `ex_se_happycloud02.png`, `ex_se_happycloud03.png`, `ex_se_star01.png`, `ex_se_star02.png`, `ex_se_star03.png`, `ex_se_star04.png`, `ex_sh_chulho00.png`, `ex_sh_chulho01.png`, `ex_sh_chulho02.png`, `ex_sh_chulho03.png`, `ex_sh_hyunrok00.png`, `ex_sh_hyunrok01.png`, `ex_sh_kisul00.png`, `ex_sh_kisul01.png`, `ex_sh_kisul02.png`, `ex_sh_kisul03.png`, `ex_sh_spirit01.png`, `ex_sh_spirit02.png`, `ex_ss_ninja.png`

### `job` — 20

`job_alche_vincent`, `job_bard_aiolo01`, `job_bard_aiolo02`, `job_black_hucke01`, `job_black_hucke02`, `job_black_hucke03`, `job_dancer_eir01`, `job_dancer_eir02`, `job_dancer_eir03`, `job_huntermaster`, `job_knight_herman1`, `job_knight_herman2`, `job_ko01`, `job_ko02`, `job_ko03`, `job_ko04`, `job_sage_kayron`, `job_wizard_maria01`, `job_wizard_maria02`, `job_wizard_maria03`

### `ra` — 19

`ra_bishop`, `ra_fano01`, `ra_fano02`, `ra_fano03`, `ra_gman`, `ra_gman2`, `ra_gwoman`, `ra_gwoman2`, `ra_magic1`, `ra_magic2`, `ra_magic3`, `ra_magic4`, `ra_nemma01`, `ra_nemma02`, `ra_nemma03`, `ra_nemma04`, `ra_sboy`, `ra_usti1`, `ra_usti2`

### `dress` — 17

`dress_f_acolyte`, `dress_f_archer`, `dress_f_ex`, `dress_f_masician`, `dress_f_merchant`, `dress_f_swordman`, `dress_f_thief`, `dress_f_tk`, `dress_m_acolyte`, `dress_m_archer`, `dress_m_ex`, `dress_m_masician`, `dress_m_merchant`, `dress_m_swordman`, `dress_m_thief`, `dress_m_tk`, `dress_novice`

### `kh` — 16

`kh_ellisia`, `kh_ellisia_port`, `kh_elly01`, `kh_elly02`, `kh_elly03`, `kh_elly04`, `kh_family_port`, `kh_kiel01`, `kh_kiel02`, `kh_kiel03`, `kh_kiel04`, `kh_kyel01`, `kh_kyel02`, `kh_kyel03`, `kh_kyel_port`, `kh_ring_port`

### `moc` — 11

`moc2_dan01`, `moc2_dan02`, `moc2_kid02`, `moc2_kid03`, `moc2_kid04`, `moc2_kid05`, `moc2_rin01`, `moc2_rin02`, `moc2_rin03`, `moc2_rin04`, `moc_soldier`

### `mocseal` — 11

`mocseal_dan01`, `mocseal_earth01`, `mocseal_earth02`, `mocseal_fire01`, `mocseal_fire02`, `mocseal_ice01`, `mocseal_ice02`, `mocseal_kid01`, `mocseal_rin01`, `mocseal_wind01`, `mocseal_wind02`

### `aca` — 10

`aca_gunb_01`, `aca_gunb_02`, `aca_gung_01`, `aca_gung_02`, `aca_ninja_h`, `aca_ninja_k`, `aca_salim01`, `aca_salim02`, `aca_salim03`, `aca_sword`

### `cat` — 10

`cat_g_01`, `cat_g_02`, `cat_g_03`, `cat_g_04`, `cat_g_05`, `cat_g_06`, `cat_g_07`, `cat_g_08`, `cat_g_lose`, `cat_g_win`

### `god` — 10

`god_kukur01`, `god_kukur02`, `god_kukur03`, `god_nelluad01`, `god_nelluad02`, `god_nelluad03`, `god_nelluad04`, `god_rebeireb`, `god_tialpi01`, `god_tialpi02`

### `h` — 10

`h_arcana01`, `h_arcana02`, `h_chaos01`, `h_chaos02`, `h_chaos03`, `h_guardian1`, `h_guardian2`, `h_guardian3`, `h_iris01`, `h_iris02`

### `kafra` — 10

`kafra_01`, `kafra_02`, `kafra_03`, `kafra_04`, `kafra_05`, `kafra_06`, `kafra_07`, `kafra_08`, `kafra_09`, `kafra_do01`

### `malaya` — 10

`malaya_diwata01`, `malaya_diwata02`, `malaya_ghost01`, `malaya_ghost02`, `malaya_nursea01`, `malaya_nursea02`, `malaya_nursea03`, `malaya_nursea04`, `malaya_nursea05`, `malaya_nurseb`

### `rock` — 10

`rock_cact01`, `rock_cact02`, `rock_cact03`, `rock_cow01`, `rock_cow01_all`, `rock_iboka`, `rock_iboka_all`, `rock_james`, `rock_james_all`, `rock_worp`

### `se` — 10

`se_moon01`, `se_moon02`, `se_moon03`, `se_star01`, `se_star02_1`, `se_star02_2`, `se_star03`, `se_sun01`, `se_sun02`, `se_sun03`

### `sara` — 9

`sara_9sara1`, `sara_9sara2`, `sara_9sara3`, `sara_beholder`, `sara_elder_irine1`, `sara_elder_irine2`, `sara_elder_irine3`, `sara_elder_irine4`, `sara_momdie`

### `wish` — 9

`wish_maiden11`, `wish_maiden12`, `wish_maiden13`, `wish_maiden21`, `wish_maiden22`, `wish_maiden23`, `wish_maiden31`, `wish_maiden32`, `wish_maiden33`

### `avn` — 8

`avn_book01`, `avn_book02`, `avn_desk01`, `avn_desk02`, `avn_desk03`, `avn_desk04`, `avn_desk05`, `avn_labo`

### `gc` — 8

`gc_mayssel01`, `gc_mayssel02`, `gc_mayssel03`, `gc_mayssel04`, `gc_mayssel05`, `gc_verkhasel01`, `gc_verkhasel02`, `gc_verkhasel03`

### `hu` — 8

`hu_alex01`, `hu_alex02`, `hu_alex03`, `hu_alex04`, `hu_laura01`, `hu_laura02`, `hu_laura03`, `hu_laura04`

### `nov` — 8

`nov_lumin01`, `nov_lumin02`, `nov_lumin03`, `nov_lumin04`, `nov_lumin05`, `nov_magicsoul01`, `nov_magicsoul02`, `nov_magicsoul03`

### `reno` — 8

`reno_kn_01`, `reno_kn_02`, `reno_kn_03`, `reno_kn_04`, `reno_swd_01`, `reno_swd_02`, `reno_swd_03`, `reno_swd_04`

### `betelgeuse` — 7

`betelgeuse01.png`, `betelgeuse02.png`, `betelgeuse03.png`, `betelgeuse04.png`, `betelgeuse05.png`, `betelgeuse06.png`, `betelgeuse07.png`

### `gl` — 7

`gl_barmund1`, `gl_barmund2`, `gl_barmund3`, `gl_heinrich1`, `gl_heinrich2`, `gl_himel1`, `gl_himel2`

### `orleans` — 7

`orleans_1`, `orleans_2`, `orleans_3`, `orleans_4`, `orleans_5`, `orleans_6`, `orleans_7`

### `schmidt` — 7

`schmidt01`, `schmidt02`, `schmidt03`, `schmidt04`, `schmidt05`, `schmidt06`, `schmidt07`

### `heinrich` — 6

`heinrich01`, `heinrich02`, `heinrich03`, `heinrich_a01`, `heinrich_a02`, `heinrich_a03`

### `lumin` — 6

`lumin_ac_01`, `lumin_ac_02`, `lumin_ac_03`, `lumin_ac_04`, `lumin_ac_05`, `lumin_ac_06`

### `wedding` — 6

`wedding_bomars01`, `wedding_bomars02`, `wedding_bomars03`, `wedding_marry01`, `wedding_marry02`, `wedding_marry03`

### `event` — 5

`event01`, `event02`, `event03`, `event04`, `event05`

### `g` — 5

`g_cat_00`, `g_cat_01`, `g_cat_02`, `g_cat_03`, `g_cat_04`

### `igu` — 5

`igu01`, `igu02`, `igu03`, `igu04`, `igu05`

### `kardui` — 5

`kardui01`, `kardui02`, `kardui03`, `kardui04`, `kardui05`

### `ma` — 5

`ma_starcandy`, `ma_tomas01`, `ma_tomas02`, `ma_tomas03`, `ma_tomas04`

### `mer` — 5

`mer_bayeri_card`, `mer_dieter_card`, `mer_eira_card`, `mer_eleanor_card`, `mer_sera_card`

### `nya` — 5

`nya_blue`, `nya_green`, `nya_off`, `nya_red`, `nya_yellow`

### `oscar` — 5

`oscar01`, `oscar02`, `oscar03`, `oscar04`, `oscar05`

### `pops` — 5

`pops_bug`, `pops_lau`, `pops_nor`, `pops_sim`, `pops_smi`

### `prm` — 5

`prm_1`, `prm_2`, `prm_3`, `prm_4`, `prm_5`

### `thf` — 5

`thf_lumin01`, `thf_lumin02`, `thf_lumin03`, `thf_lumin04`, `thf_lumin05`

### `tutorial` — 5

`tutorial01`, `tutorial02`, `tutorial03`, `tutorial04`, `tutorial05`

### `valkiwi` — 5

`valkiwi_1`, `valkiwi_2`, `valkiwi_3`, `valkiwi_4`, `valkiwi_5`

### `verus` — 5

`verus_aures`, `verus_ian01`, `verus_ian02`, `verus_ian03`, `verus_ian04`

### `wop` — 5

`wop_emb00`, `wop_emb01`, `wop_emb02`, `wop_emb03`, `wop_emb04`

### `acact` — 4

`acact_01`, `acact_02`, `acact_03`, `acact_04`

### `arquien` — 4

`arquien_n_atnad01`, `arquien_n_atnad02`, `arquien_n_atnad03`, `arquien_n_atnad04`

### `bard` — 4

`bard_eland01`, `bard_eland02`, `bard_eland03`, `bard_eland04`

### `bat` — 4

`bat_crua1`, `bat_crua2`, `bat_kiyom1`, `bat_kiyom2`

### `bijou` — 4

`bijou_01`, `bijou_02`, `bijou_03`, `bijou_death`

### `birman` — 4

`birman01`, `birman02`, `birman03`, `birman04`

### `dalle` — 4

`dalle01`, `dalle02`, `dalle03`, `dalle04`

### `debon` — 4

`debon01`, `debon02`, `debon03`, `debon04`

### `gelca` — 4

`gelca01`, `gelca02`, `gelca03`, `gelca04`

### `hisie` — 4

`hisie01`, `hisie02`, `hisie03`, `hisie04`

### `ins` — 4

`ins_cata_champ_a`, `ins_cata_champ_n`, `ins_cata_champ_s`, `ins_cata_pri_n`

### `laime` — 4

`laime_evenor01`, `laime_evenor02`, `laime_evenor03`, `laime_evenor04`

### `laperm` — 4

`laperm01`, `laperm02`, `laperm03`, `laperm04`

### `loo` — 4

`loo_ang`, `loo_nor`, `loo_sim`, `loo_smi`

### `looke` — 4

`looke_rapez01`, `looke_rapez02`, `looke_rapez03`, `looke_rapez04`

### `lunain` — 4

`lunain01`, `lunain02`, `lunain03`, `lunain04`

### `mal` — 4

`mal_homnya_n`, `mal_homnya_s`, `mal_nyapic`, `mal_octo_fes`

### `mark` — 4

`mark_wt_1`, `mark_wt_2`, `mark_wt_3`, `mark_wt_4`

### `nale` — 4

`nale01`, `nale02`, `nale03`, `nale04`

### `nines` — 4

`nines01`, `nines02`, `nines03`, `nines04`

### `nyuang` — 4

`nyuang_1`, `nyuang_2`, `nyuang_3`, `nyuang_4`

### `oliver` — 4

`oliver_hum`, `oliver_pre`, `oliver_smile`, `oliver_think`

### `richard` — 4

`richard_po01`, `richard_po01.png`, `richard_po02`, `richard_po02.png`

### `roel` — 4

`roel01`, `roel02`, `roel03`, `roel04`

### `rote` — 4

`rote01`, `rote02`, `rote03`, `rote04`

### `sc` — 4

`sc_vicente01`, `sc_vicente02`, `sc_vicente03`, `sc_vicente04`

### `shaloshi` — 4

`shaloshi01`, `shaloshi02`, `shaloshi03`, `shaloshi04`

### `sham` — 4

`sham01`, `sham02`, `sham03`, `sham04`

### `sign` — 4

`sign_01`, `sign_02`, `sign_03`, `sign_04`

### `soul` — 4

`soul_van01`, `soul_van02`, `soul_van03`, `soul_van04`

### `tama` — 4

`tama_cook_1`, `tama_cook_2`, `tama_cook_3`, `tama_cook_4`

### `tnm` — 4

`tnm_loki`, `tnm_lucile01`, `tnm_lucile02`, `tnm_lucile03`

### `valen` — 4

`valen_arle01`, `valen_arle02`, `valen_arle03`, `valen_arle04`

### `war` — 4

`war_y1`, `war_y2`, `war_y3`, `war_y4`

### `arang` — 3

`arang01`, `arang02`, `arang03`

### `choucream` — 3

`choucream_d`, `choucream_e`, `choucream_n`

### `fey` — 3

`fey_fun`, `fey_nor`, `fey_oneg`

### `fly` — 3

`fly_felrock`, `fly_felrock2`, `fly_trock`

### `heri` — 3

`heri1`, `heri2`, `heri3`

### `hero` — 3

`hero_chaos_01`, `hero_iris_01`, `hero_iris_02`

### `katsua` — 3

`katsua01`, `katsua02`, `katsua03`

### `min` — 3

`min01`, `min02`, `min03`

### `paymap` — 3

`paymap1`, `paymap2`, `paymap3`

### `ragi` — 3

`ragi01`, `ragi02`, `ragi03`

### `rutie` — 3

`rutie_snownow01`, `rutie_snownow02`, `rutie_snownow03`

### `white` — 3

`white_choco`, `white_retto`, `white_seed`

### `avant` — 2

`avant01`, `avant02`

### `ca` — 2

`ca_nor`, `ca_smil`

### `ein` — 2

`ein_hicman`, `ein_soldier`

### `fenrir` — 2

`fenrir_a`, `fenrir_b`

### `mami` — 2

`mami01`, `mami02`

### `minuel` — 2

`minuel01`, `minuel02`

### `navi` — 2

`navi01`, `navi02`

### `paycana` — 2

`paycana_a`, `paycana_b `

### `pet` — 2

`pet_ex_01`, `pet_ex_02`

### `pop` — 2

`pop_nor`, `pop_sim`

### `sarah` — 2

`sarah_hero3`, `sarah_hero3_2`

### `siide` — 2

`siide1`, `siide2`

### `var` — 2

`var_dan`, `var_nor`

### `wanted` — 2

`wanted1`, `wanted2`

### `zonda` — 2

`zonda_01`, `zonda_do01`

### `acamaster` — 1

`acamaster_a`

### `alice` — 1

`alice`

### `b` — 1

`b-tiara`

### `cry` — 1

`cry-b`

### `gbad` — 1

`gbad`

### `gef` — 1

`gef_soldier`

### `gnor` — 1

`gnor`

### `gsmi` — 1

`gsmi`

### `hg` — 1

`hg_book`

### `lydia` — 1

`lydia_a`

### `mets` — 1

`mets_alpha`

### `morocc` — 1

`morocc_kid`

### `npc` — 1

`npc-tiara`

### `pay` — 1

`pay_soldier`

### `prt` — 1

`prt_soldier`

### `sakray` — 1

`sakray`

### `sr` — 1

`sr_gentletouch_change`

### `stephan` — 1

`stephan_j_e_w`

### `tartanos` — 1

`tartanos`

### `teup` — 1

`teup_gye`

### `thumbs` — 1

`thumbs.db`

### `zherlthsh` — 1

`zherlthsh`
