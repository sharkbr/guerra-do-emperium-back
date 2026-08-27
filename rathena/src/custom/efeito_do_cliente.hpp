// Guerra do Emperium - efeito de tela por numero, sem o teto do rAthena.
//
// POR QUE ISTO EXISTE
// -------------------
// O `specialeffect` do rAthena recusa qualquer numero fora do enum dele:
//
//     if( type <= EF_NONE || type >= EF_MAX ) {
//         ShowError( "buildin_specialeffect: unsupported effect id %d\n", type );
//
// e o `EF_MAX` do nosso vendor vale 1243 - o ultimo efeito nomeado e o
// `EF_SOUL_EXPLOSION`, 1242. Acontece que o TETO E DO EMULADOR, NAO DO
// CLIENTE: o nosso kRO 2021-11-03 conhece efeitos ate 2372, e NOVECENTOS E
// QUARENTA E UM deles - com arte propria, `.str` no GRF - estao ACIMA daquele
// teto. Pedir um deles por `specialeffect` nao desenha nada e escreve a linha
// de erro acima no log; o efeito existe, a arte existe, e o caminho entre os
// dois e que estava fechado.
//
// E a mesma familia do `db/` do vendor semanticamente vencido (CLAUDE.md
// secao 5, entrada do `stylist.yml`): o dado nao esta errado, esta velho, e
// nada avisa.
//
// COMO O TETO DE 2372 FOI MEDIDO - e como remedi-lo se o cliente mudar
// ---------------------------------------------------------------------
// Nao foi chutado nem tirado de tabela de terceiro: saiu do proprio exe.
// O cliente despacha o efeito por um switch de tabela DIRETA, em
// `GuerraDoEmperium.exe` (offset de arquivo 0x006b6ce4):
//
//     lea eax, [ebx-13]                  ; ebx = numero do efeito
//     cmp eax, 0x937                     ; 2359
//     ja  <default: nao desenha nada>
//     jmp dword [eax*4 + 0x00ABFEE0]     ; tabela de 2360 entradas
//
// Ou seja a faixa aceita e 13..2372, e `numero = 13 + indice`. A prova de
// que o 13 e o deslocamento certo nao e a leitura da instrucao: e o
// cruzamento dos 1015 efeitos que tem `.str` com o proprio enum
// `e_special_effects` do rAthena. O deslocamento 13 casa 25 nomes, espalhados
// de `EF_STORMGUST` (89) ate `EF_FULLMOON_KICK` (1230); TODOS os outros
// deslocamentos, de 0 a 26, casam ZERO. Pico unico e sem deriva nos ids
// altos.
//
// A medicao inteira e reproduzivel por `ferramentas/lista_efeitos_do_cliente.py`,
// que refaz a leitura do exe e imprime o de-para numero -> arquivo `.str`.
//
// A ARMADILHA QUE ISTO NAO RESOLVE
// --------------------------------
// Numero FORA da faixa cai no `default` do switch e o cliente **nao desenha
// nada, calado** - sem erro de Lua, sem caixa, sem linha de log. Entao errar o
// numero aqui e indistinguivel de "o efeito nao existe". Antes de usar um
// numero novo, conferir na saida da ferramenta acima que ele tem `.str`.
//
// O que este arquivo NAO faz e afrouxar a checagem: o `specialeffect` do
// rAthena continua intacto e continua recusando acima de 1242. Quem quiser a
// faixa nova pede por `efeitoespecial`, e paga o preco de o numero nao ter
// nome.

#ifndef EFEITO_DO_CLIENTE_HPP
#define EFEITO_DO_CLIENTE_HPP

/// Maior numero de efeito que o nosso cliente conhece (ver o cabecalho).
/// Medido no exe, nao suposto. Cliente novo = remedir.
#define EFEITO_DO_CLIENTE_MAXIMO 2372

/// Menor numero da tabela do cliente. Abaixo disso cai no `default`.
#define EFEITO_DO_CLIENTE_MINIMO 13

/// O numero esta na faixa que este cliente sabe desenhar?
static inline bool efeito_do_cliente_existe(int32 numero)
{
	return numero >= EFEITO_DO_CLIENTE_MINIMO
	    && numero <= EFEITO_DO_CLIENTE_MAXIMO;
}

#endif /* EFEITO_DO_CLIENTE_HPP */
