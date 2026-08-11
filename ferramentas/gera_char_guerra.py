# -*- coding: cp1252 -*-
# Gera conf/guerra/char_guerra.txt em cp1252 (CLAUDE.md, regra 1).
# Os bytes acentuados sao escritos por escape \xNN de proposito: assim este
# script continua ASCII puro e nao ha como um editor grava-lo em UTF-8 e
# estragar a lista calado.

MINUSCULAS = ('\xe0\xe1\xe2\xe3\xe4'   # a com crase, agudo, circunflexo, til, trema
              '\xe7'                    # c cedilha
              '\xe8\xe9\xea\xeb'        # e
              '\xec\xed\xee\xef'        # i
              '\xf1'                    # n com til
              '\xf2\xf3\xf4\xf5\xf6'    # o
              '\xf9\xfa\xfb\xfc')       # u

MAIUSCULAS = ('\xc0\xc1\xc2\xc3\xc4'
              '\xc7'
              '\xc8\xc9\xca\xcb'
              '\xcc\xcd\xce\xcf'
              '\xd1'
              '\xd2\xd3\xd4\xd5\xd6'
              '\xd9\xda\xdb\xdc')

ASCII = 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

CABECALHO = """\
//--------------------------------------------------------------
// Guerra do Emperium - configuracao do char-server nossa.
//
// Este arquivo e VERSIONADO e vale para qualquer clone do repo.
// E importado por conf/char_athena.conf, logo antes de
// conf/import/char_conf.txt - o conf/import continua podendo
// sobrescrever qualquer coisa daqui, por maquina.
//
// ATENCAO: este arquivo e cp1252, nao UTF-8 (CLAUDE.md, regra 1).
// A lista de letras abaixo tem bytes acentuados; salvo em UTF-8,
// cada acento vira DOIS bytes e a lista passa a permitir lixo em
// vez de permitir "a com til". Gerado por
// ferramentas/gera_char_guerra.py - editar por la, nao a mao.
//--------------------------------------------------------------

//--------------------------------------------------------------
// Nome de personagem com acento.
//
// O rAthena filtra o nome BYTE A BYTE (char.cpp:1365,
// strchr(char_name_letters, name[i])); a lista padrao so tem
// ASCII, entao "Barao" com til virava "Character Creation is
// denied." sem dizer o motivo. O cliente manda o nome em cp1252,
// entao basta a lista conter os mesmos bytes.
//
// A lista vale tambem para nome de CLA, GRUPO e homunculo - os
// quatro pontos de checagem (char.cpp, int_guild.cpp,
// int_party.cpp, int_homun.cpp) leem esta mesma variavel.
//
// Entram so LETRAS. Hifen, apostrofo e pontuacao ficaram de
// fora de proposito: nome e usado como chave em comando de GM,
// em sussurro e no barter, e simbolo ali complica sem ganho.
//
// A outra metade da correcao mora em conf/guerra/inter_guerra.txt
// (default_codepage). Sem ela o filtro deixa passar e o INSERT
// no banco falha com "Incorrect string value" - ou seja, mexer
// so aqui NAO resolve.
//--------------------------------------------------------------
char_name_option: 1
"""

linha = 'char_name_letters: ' + ASCII + MINUSCULAS + MAIUSCULAS

destino = r'C:\Users\User\projects\guerra-do-emperium-back\rathena\conf\guerra\char_guerra.txt'
f = open(destino, 'wb')
f.write(CABECALHO)
f.write(linha + '\n')
f.close()

# Conferencia: reler em cp1252 e provar que os acentos voltam certos.
dados = open(destino, 'rb').read()
assert '\xef\xbf\xbd' not in dados, 'U+FFFD no arquivo - foi gravado em UTF-8'
texto = dados.decode('cp1252')
for b in MINUSCULAS + MAIUSCULAS:
    assert b.decode('cp1252') in texto, 'byte %r sumiu' % b
print 'OK: %d bytes, %d letras acentuadas' % (len(dados), len(MINUSCULAS + MAIUSCULAS))
print repr(linha[-52:])
