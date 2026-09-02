#########################################################################
# pvpGhost - o "fantasma" da Arena de Combate
#
# Personagem de staff que vive dentro do mapa de PvP e alterna entre TRES
# ESTADOS, decididos so pela quantidade de jogadores no alcance de visao:
#
#   0 jogadores            -> CHASING   invisivel, patrulhando a cruz da
#                                       arena sem parar, ate achar alguem
#   1 jogador (ou ate      -> ATTACKING pega ele de alvo e roda o ciclo de
#   pvpGhost_maxPlayers)               combate (pvpGhost_cycle), em loop
#   acima do limite        -> SLEEPING  @hide, para tudo, e so reavalia de
#                                       pvpGhost_sleepCheck em N segundos
#
# CONTAGEM E POR ALCANCE DE VISAO, NAO PELO MAPA INTEIRO. O openkore so
# conhece os jogadores que o servidor mandou para o cliente, e isso e o
# raio de `area_size` do rAthena (conf/battle/client.conf, 14 celulas
# aqui). Na pratica e o comportamento que se quer de um fantasma - ele
# reage a quem esta perto dele, nao a quem esta no outro canto do mapa.
#
# O ESTADO DE INVISIBILIDADE NAO E CHUTADO. `@hide` no rAthena e um
# alternador puro (ACMD_FUNC(hide), src/map/atcommand.cpp) - mandar dois
# seguidos desfaz o primeiro. Em vez de manter um booleano nosso, que
# dessincroniza no primeiro pacote perdido, lemos OPTION_INVISIBLE
# (0x40, src/map/status.hpp) de $char->{option}, que o rAthena manda no
# ZC_STATE_CHANGE a cada mudanca. So mandamos o comando quando o estado
# lido difere do desejado, e nunca mais rapido que pvpGhost_toggleCooldown.
#
# O ATAQUE E UM PACOTE, MAS A PERSEGUICAO E NOSSA. sendAction(ID, 7) e o
# "ataque continuo" do cliente, e o rAthena chama unit_attack(...,
# continuous=1). "Continuo" NAO significa que o servidor persegue: em
# unit_attack_timer_sub (src/map/unit.cpp:3260) o alvo fora de alcance so
# e perseguido quando quem ataca e MONSTRO; quando e JOGADOR, o servidor
# manda clif_movetoattack() e para, porque no jogo de verdade quem anda
# ate o alvo e o cliente oficial. Como este bot nao e o cliente oficial,
# quem anda tem de ser o passo `attack` daqui. A IA nativa fica desligada
# na config (attackAuto 0) - ela so sabe atacar monstro.
#
# O ANDAR E DO OPENKORE. Patrulha e perseguicao usam $char->route(), que
# enfileira uma Task::Route no @ai_seq; quem a executa e o
# $char->processTask("route") da AI::CoreLogic, que roda com AI em MANUAL
# ou AUTO. O mapa `pvp_n_1-5` nao tem .fld2 proprio: o resnametable.txt do
# cliente o aponta para `job_knight` (fields/job_knight.fld2.gz), e e por
# isso que o pathfinding funciona nele.
#
#-----------------------------------------------------------------------
# O CICLO DE COMBATE E UMA RECEITA, NAO CODIGO
#
# `pvpGhost_approach` (uma vez, ao fisgar o alvo) e `pvpGhost_cycle` (em
# loop, ate o alvo sumir ou chegar gente) sao listas de passos separados
# por `;`. Cada passo e um verbo com argumentos:
#
#   attack <seg>              fica visivel e bate no alvo por <seg>
#   chase <seg> [hold]        anda ate o alvo; acaba AO CHEGAR, ou em <seg>.
#                             `hold` faz durar os <seg> inteiros (seguir de perto)
#   hide                      some com @hide e espera confirmar
#   cloak                     some com o Espreitar e espera confirmar
#   show                      aparece (desliga os dois) e espera confirmar
#   emotion <nome|num>        manda um emoticon (nomes em tables/emotions.txt)
#   face <to|away>            vira o corpo para o alvo, ou de costas para ele
#   skill <nome|id> [lv|max] [target|self|ground]   usa uma habilidade
#         [range <n>]         anda ate <n> celulas do alvo antes de lancar
#         [unless <EFST_X>]   pula o passo se o alvo JA esta com esse status
#         [if <EFST_X>]       so lanca se o alvo estiver com esse status
#   wait <seg>                fica parado
#
# O PASSO `skill` NAO ESPERA RELOGIO, ESPERA O SERVIDOR. Ele acaba no
# tique em que chega o anuncio da propria habilidade (packet_skilluse com
# sourceID nosso); o `pvpGhost_skillWait` virou so o teto de seguranca.
# Isso importa porque a Copia Explosiva da 1,5s de invisibilidade perfeita
# (Duration1 do Id 2304, db/re/skill_db.yml) e o Espreitar precisa sair
# DENTRO dessa janela - com o wait fixo de 1,5s ele saia justo quando ela
# acabava, e o fantasma aparecia parado antes de sumir de novo.
#
# E A COPIA EXPLOSIVA LIGA O MESMO BIT DO @hide. O status `_Feintbomb`
# tem `Options: Invisible: true` (db/re/status.yml), que e OPTION_INVISIBLE
# (0x40) - o bit que este plugin le para saber se o @hide esta ligado.
# Sem tratar isso, o passo `cloak` via "esta escondido" e mandava @hide
# para "desligar", LIGANDO de fato a invisibilidade de staff; so na volta
# seguinte, depois do toggleCooldown, ele desligava e ai lancava o
# Espreitar. Era dai que vinham os segundos parados. Ver feintActive().
#
# HA DUAS FURTIVIDADES E ELAS NAO SAO A MESMA COISA. Fora do combate o
# fantasma some com `@hide` (OPTION_INVISIBLE), que e de staff e nao
# gasta nada. Dentro do ciclo de combate ele some com o ESPREITAR
# (ST_CHASEWALK, OPTION_CHASEWALK), que e habilidade de jogador - e o que
# um Renegado de verdade faria, e some do @who junto. As duas nunca ficam
# ligadas ao mesmo tempo: applyStealth() desliga uma antes de ligar a
# outra. O nivel do Espreitar e sempre o maximo aprendido.
#
# Para acrescentar acoes no futuro, ou se muda a linha do config, ou se
# escreve um verbo novo em runStep() - o resto do plugin nao muda.
#
# Configuracao em control/config.txt:
#
#   pvpGhost 1                        liga/desliga
#   pvpGhost_map pvp_n_1-5            mapa da arena
#   pvpGhost_maxPlayers 1             ate quantos jogadores ele encara
#   pvpGhost_ignore Nome1, Nome2      nunca conta nem ataca estes chars
#   pvpGhost_sleepCheck 5             intervalo de reavaliacao dormindo
#   pvpGhost_patrol x y, x y, ...     a rota da patrulha, em loop
#   pvpGhost_patrolTolerance 3        quao perto basta chegar do ponto
#   pvpGhost_patrolLegTimeout 40      desiste da perna e vai pro proximo
#   pvpGhost_approach hide; chase 10  passos ao fisgar o alvo
#   pvpGhost_cycle ...                passos do combate, em loop
#   pvpGhost_attackInterval 2         reenvio do ataque, em segundos
#   pvpGhost_chaseDistance 1          distancia de parada ao perseguir
#   pvpGhost_skillWait 1.5            teto da espera do passo `skill`
#   pvpGhost_skillApproach 4          teto do `range` do passo `skill`
#   pvpGhost_returnCommand @warp pvp_n_1-5    como voltar depois de morrer
#   pvpGhost_hideCommand @hide        caso o simbolo de atcommand mude
#
#-----------------------------------------------------------------------
# A REACAO AO GOLPE PESADO
#
# Quando uma HABILIDADE tira do fantasma mais que `pvpGhost_panicDamage`
# do HP maximo dele, o ciclo e interrompido na hora e entra uma quarta
# fase, `panic`, cujo objetivo e uma so coisa: calar o oponente com a
# Mascara da Tolice (SC_IGNORANCE, `States: NoCast` no db/re/status.yml).
#
# Sao duas receitas, e quem escolhe e a distancia no momento da entrada:
# com o alvo dentro de `pvpGhost_masqueradeRange` vale `pvpGhost_panicNear`
# (lanca de cara); mais longe, `pvpGhost_panicFar` (vira de costas, Copia
# Explosiva, e vai de encontro para lancar). Ele tenta ate
# `pvpGhost_panicTries` vezes, e para antes se o status colar no alvo -
# a prova e o EFST do proprio alvo, nao um chute nosso.
#
#   pvpGhost_panicDamage 0.27         fracao do HP maximo que dispara
#   pvpGhost_panicTries 2             quantas tentativas, no maximo
#   pvpGhost_panicStatus EFST_IGNORANCE   como saber que colou
#   pvpGhost_panicCooldown 8          descanso entre duas reacoes
#   pvpGhost_masqueradeRange 3        alcance da mascara (Range do 2294)
#   pvpGhost_panicNear ...            receita de perto
#   pvpGhost_panicFar ...             receita de longe
#
#-----------------------------------------------------------------------
# A REACAO AO HP BAIXO
#
# Abaixo de `pvpGhost_lowHpPercent` do HP maximo o fantasma larga tudo -
# inclusive a fase `panic` - e entra na fase `shadow`: Vinculo Sombrio
# (SC_SHADOWFORM, Id 2287) no oponente, e depois grudado nele pelo tempo
# de `pvpGhost_lowHpTimeout`.
#
# O VINCULO POE O STATUS EM QUEM LANCA, NAO EM QUEM LEVA. Quem tem o
# SC__SHADOWFORM e o fantasma; o alvo entra como `val2`, e e ELE que come
# o dano que o fantasma levar, ate `4 + nivel` golpes (ver
# src/map/skills/thief/shadowform.cpp do nosso rAthena). Por isso a
# guarda de "ja esta ligado" olha o proprio char, e nao o oponente.
#
# E O PRECO E ALTO: quem esta com o Vinculo NAO LANCA MAIS NADA E NAO
# BATE (skill_check_condition_castbegin, src/map/skill.cpp:8327, mais o
# `NoAttack` do db/re/status.yml). Ficar perto e o unico jeito de o
# vinculo servir para alguma coisa, e por isso a receita acaba num
# `chase ... hold` - alem de manter a ligacao viva, que morre se ele
# passar de DEZ celulas do alvo (src/map/map.cpp:599).
#
#   pvpGhost_lowHpPercent 10          abaixo disso, dispara
#   pvpGhost_lowHpTimeout 15          teto da fase, e folga ate a proxima
#   pvpGhost_lowHpSkill SC_SHADOWFORM
#   pvpGhost_lowHpStatus EFST_SHADOWFORM   como saber que ja esta ligado
#   pvpGhost_lowHp ...                a receita
#
# Comando de console: `pvpghost` mostra o estado atual.
#########################################################################
package OpenKore::Plugins::pvpGhost;

use strict;
use Time::HiRes qw(time);

use Plugins;
use Commands;
use Globals qw(%config $char $field $net $playersList $messageSender $accountID);
use Log qw(message warning debug);
use Misc qw(sendMessage getEmotionByCommand);
use Utils qw(distance blockDistance calcPosition);
use Network;
use Skill;
use AI;

# src/map/status.hpp. O Espreitar (ST_CHASEWALK) liga OPTION_CHASEWALK e
# OPTION_CLOAK juntos (db/re/status.yml, bloco `Chasewalk`); usamos o
# primeiro, que e so dele.
use constant {
	OPTION_INVISIBLE => 0x40,
	OPTION_CHASEWALK => 0x4000,
};

Plugins::register('pvpGhost', 'Fantasma da arena PvP', \&onUnload);

my $hooks = Plugins::addHooks(
	['mainLoop_pre',      \&onMainLoop],
	['packet_mapChange',  \&onReset],
	['disconnected',      \&onReset],
	# Serve a duas coisas ao mesmo tempo: confirmar as NOSSAS habilidades
	# (e assim soltar o passo `skill` sem esperar relogio) e ver o golpe
	# que entra em cima do fantasma, que e o gatilho da fase `panic`.
	['packet_skilluse',   \&onSkillUse],
	# So para nao ficar mudo quando faltar insumo - as mascaras gastam
	# uma Pintura Facial (6120) por lance, e a Tinta Infinita nao cobre
	# esse item (src/custom/tinta_infinita.hpp so isenta a 6123).
	['packet_skillfail',  \&onSkillFail],
);

my $cmd = Commands::register(['pvpghost', 'Estado do fantasma da arena', \&onCommand]);

my %st;
my %parseCache;   # texto do config -> estrutura ja interpretada
my %warned;       # avisos que so valem uma vez por sessao

resetState();

sub onUnload {
	Plugins::delHooks($hooks);
	Commands::unregister($cmd);
}

sub resetState {
	%st = (
		state      => '',        # chasing | attacking | sleeping
		stateSince => 0,
		lastCheck  => 0,
		lastToggle => 0,        # ultimo @hide
		lastCloak  => 0,        # ultimo Espreitar
		lastReturn => 0,
		sleepUntil => 0,

		wpIndex    => 0,         # patrulha
		wpSince    => 0,

		targetID   => undef,     # combate
		phase      => '',        # approach | cycle | panic
		stepIndex  => 0,
		stepSince  => 0,
		stepData   => {},
		lastAttack => 0,
		lastSeen   => 0,         # ultima vez que havia alvo a vista
		frozenAt   => 0,         # desde quando o ciclo esta sem alvo

		skillOk    => {},        # idn -> quando o servidor anunciou a nossa
		feintUntil => 0,         # ate quando o 0x40 e da Copia Explosiva

		panicList  => undef,     # receita da tentativa em curso
		panicTries => 0,
		panicEnd   => 0,         # fim da ultima reacao (para o cooldown)

		shadowUntil => 0,        # teto do Vinculo Sombrio
		shadowEnd   => 0,        # fim do ultimo (para o cooldown)

		routeGoal  => undef,     # ultimo destino pedido ao Task::Route
		lastRoute  => 0,
	);
}

sub onReset {
	stopMoving();
	resetState();
}

sub cfg {
	my ($key, $default) = @_;
	my $v = $config{"pvpGhost_$key"};
	return (defined $v && $v ne '') ? $v : $default;
}

sub warnOnce {
	my ($key, $msg) = @_;
	return if $warned{$key};
	$warned{$key} = 1;
	warning "[pvpGhost] $msg\n";
}

sub optionOn {
	my ($mask) = @_;
	return 0 unless $char && defined $char->{option};
	return ($char->{option} & $mask) ? 1 : 0;
}

sub isHidden    { return optionOn(OPTION_INVISIBLE) }
sub isChaseWalk { return optionOn(OPTION_CHASEWALK) }

# A COPIA EXPLOSIVA TAMBEM LIGA O OPTION_INVISIBLE, e nao ha como
# distinguir os dois pelo bit: o status `_Feintbomb` do db/re/status.yml
# tem `Options: Invisible: true`, exatamente o 0x40 do @hide, e nao tem
# `Icon:` nenhum - entao nem EFST chega para desempatar. O que sobra e
# saber que fomos NOS que lancamos: o passo `skill` marca a janela ao
# mandar a habilidade, e ela morre sozinha no tempo ou assim que o
# Espreitar confirma, que e quando ela deixa de importar.
sub feintActive {
	my ($now) = @_;
	return 0 unless $st{feintUntil};
	if ($now >= $st{feintUntil} || isChaseWalk()) {
		$st{feintUntil} = 0;
		return 0;
	}
	return 1;
}

# Status de um ator como o openkore os guarda: $actor->{statuses}{HANDLE},
# preenchido em Network/Receive.pm (actor_status_active) a partir do
# tables/STATUS_id_handle.txt. Os dois que interessam aqui batem com o
# enum efst_type do nosso rAthena - EFST_IGNORANCE 411, EFST_WEAKNESS 418
# -, e o rAthena manda essas mudancas para a AREA (clif_status_change,
# src/map/clif.cpp:6574), entao o fantasma enxerga as do oponente.
sub hasStatus {
	my ($actor, $handle) = @_;
	return 0 unless $actor && $handle && $actor->{statuses};
	return $actor->{statuses}{$handle} ? 1 : 0;
}

# Direcao de corpo de `from` para `to`, na numeracao do servidor
# (src/map/path.hpp: 0=N, 1=NO, 2=O, 3=SO, 4=S, 5=SE, 6=L, 7=NE).
my %DIR_OF = (
	'0,1'  => 0, '-1,1'  => 1, '-1,0' => 2, '-1,-1' => 3,
	'0,-1' => 4, '1,-1'  => 5, '1,0'  => 6, '1,1'   => 7,
);

sub dirTo {
	my ($from, $to) = @_;
	my $dx = $to->{x} - $from->{x};
	my $dy = $to->{y} - $from->{y};
	my $sx = ($dx > 0) - ($dx < 0);
	my $sy = ($dy > 0) - ($dy < 0);
	my $dir = $DIR_OF{"$sx,$sy"};
	return defined $dir ? $dir : 0;
}

# Como o fantasma esta sumido agora: pelo @hide, pelo Espreitar, ou nada.
sub stealthNow {
	return 'hide'  if isHidden();
	return 'cloak' if isChaseWalk();
	return 'none';
}

# Jogadores no alcance de visao que contam como "gente na arena".
sub liveTargets {
	my %ignore = map { lc($_) => 1 }
	             grep { length }
	             split /\s*,\s*/, cfg('ignore', '');

	my @out;
	foreach my $p (@{ $playersList ? $playersList->getItems : [] }) {
		next unless $p && $p->{ID};
		next if $p->{name} && $ignore{ lc $p->{name} };
		push @out, $p;
	}
	return @out;
}

# ONDE O CHAR ESTA DE VERDADE. `$char->{pos_to}` e o DESTINO do passo em
# curso, nao a posicao atual - e o Task::Route manda o `sendMove` em
# saltos de `route_step` celulas, entao o pos_to corre muito a frente do
# personagem. Usar ele para medir distancia faz a patrulha "chegar" nos
# pontos sem ter andado: no teste de 2026-08-27 a ronda pulou 31 celulas
# em 1,48s, o que nenhuma velocidade de RO faz. O calcPosition interpola
# pos/pos_to pelo tempo decorrido, e e o que o proprio openkore usa em
# todo lugar que precisa da posicao real (Commands.pm:4750).
sub myPos { return calcPosition($char) }

sub nearestOf {
	my @list = @_;
	return undef unless @list && $char;
	my $me = myPos();
	my ($best) = sort {
		distance($me, $a->{pos_to}) <=> distance($me, $b->{pos_to})
	} @list;
	return $best;
}

#########################################################################
# Invisibilidade e movimento
#########################################################################

# Pede o estado de invisibilidade desejado. Devolve 1 quando o char JA
# esta nele - nunca quando o comando acabou de ser mandado, porque o
# rAthena so confirma no ZC_STATE_CHANGE seguinte.
sub applyHidden {
	my ($wantHidden, $now) = @_;
	my $hidden = isHidden();
	return 1 if $hidden == $wantHidden;

	# ESTE `return` E O CONSERTO DO ATRASO DEPOIS DA COPIA EXPLOSIVA.
	# Durante a habilidade o 0x40 nao e do @hide, e mandar o atcommand
	# aqui nao "desliga" nada: LIGA a invisibilidade de staff por cima,
	# e ai sao dois toggles e dois toggleCooldown ate o Espreitar sair -
	# os segundos em que se via o fantasma parado. Some sozinho quando a
	# janela expira, entao ninguem trava esperando.
	return 0 if !$wantHidden && $hidden && feintActive($now);

	if ($now - $st{lastToggle} >= cfg('toggleCooldown', 2)) {
		$st{lastToggle} = $now;
		sendMessage($messageSender, "c", cfg('hideCommand', '@hide'));
	}
	return 0;
}

# Liga/desliga o Espreitar. TAMBEM e alternador: ST_CHASEWALK tem
# `Toggleable: true` no db/re/skill_db.yml, entao mandar duas vezes
# desfaz - mesmo cuidado do @hide. E ATACAR NAO O CANCELA: o bloco que
# quebra furtividade em src/map/unit.cpp:2732 so trata SC_CLOAKING,
# CLOAKINGEXCEED e NEWMOON. Por isso o passo `attack` precisa desligar o
# Espreitar de proposito, em vez de contar com o golpe para isso.
sub applyChaseWalk {
	my ($want, $now) = @_;
	return 1 if isChaseWalk() == $want;
	return 0 if $now - $st{lastCloak} < cfg('toggleCooldown', 2);

	my $name = cfg('cloakSkill', 'ST_CHASEWALK');
	my $sk   = resolveSkill($name);
	if (!$sk) {
		warnOnce("cloak_$name", "habilidade de espreitar desconhecida: $name.");
		return 1;
	}
	my $have = $char->getSkillLevel($sk);
	if (!$have) {
		warnOnce("cloaklv_$name", "o personagem nao tem " . $sk->getName() . " ($name) - o fantasma vai usar so o " . cfg('hideCommand', '@hide') . ".");
		return 1;
	}

	$st{lastCloak} = $now;
	$messageSender->sendSkillUse($sk->getIDN, $have, $char->{ID});
	return 0;
}

# O jeito de sumir depende do estado: `hide` (atcommand) fora do combate,
# `cloak` (Espreitar) dentro dele, `none` para aparecer. Os dois nunca
# ficam ligados juntos - primeiro desliga o outro, depois liga o pedido.
# Devolve 1 so quando o char JA esta como pedido.
sub applyStealth {
	my ($mode, $now) = @_;

	if ($mode eq 'hide') {
		return 0 unless applyChaseWalk(0, $now);
		return applyHidden(1, $now);
	}
	if ($mode eq 'cloak') {
		# Dentro da janela da Copia Explosiva o Espreitar sai DIRETO, sem
		# passar pelo applyHidden: nao ha @hide para desligar, e cada
		# tique gasto aqui e tique fora da invisibilidade perfeita (1,5s,
		# Duration1 do Id 2304). O servidor deixa - status_check_skilluse
		# (src/map/status.cpp:2209) so barra por OPTION_HIDE e
		# OPTION_CHASEWALK, nunca por OPTION_INVISIBLE.
		return applyChaseWalk(1, $now) if feintActive($now);
		return 0 unless applyHidden(0, $now);
		return applyChaseWalk(1, $now);
	}
	my $off = applyHidden(0, $now);
	$off = applyChaseWalk(0, $now) && $off;
	return $off;
}

sub stopMoving {
	AI::clear('route', 'move');
	$st{routeGoal} = undef;
}

# Manda o char andar ate (x, y) do mapa atual. Nao reemite a rota se o
# destino praticamente nao mudou - o alvo se mexe, e refazer a Task::Route
# a cada tique deixaria o char tremendo no lugar.
sub routeTo {
	my ($x, $y, $stopAt, $now) = @_;
	return unless $char && $field;

	my $goal   = $st{routeGoal};
	my $moving = AI::inQueue('route');

	return if $moving && $goal && abs($goal->{x} - $x) <= 2 && abs($goal->{y} - $y) <= 2;
	return if $now - $st{lastRoute} < cfg('routeRefresh', 0.5);

	AI::clear('route', 'move') if $moving;
	$st{lastRoute} = $now;
	$st{routeGoal} = { x => $x, y => $y };
	# noMapRoute: e sempre dentro da arena, entao Task::Route direto -
	# a Task::MapRoute procuraria portais que este mapa nao tem.
	$char->route($field->baseName, $x, $y,
		noMapRoute    => 1,
		distFromGoal  => $stopAt,
		noSitAuto     => 1,
		attackOnRoute => 0,
	);
}

#########################################################################
# A receita: `verbo arg arg; verbo arg; ...`
#########################################################################

sub parseSteps {
	my ($spec) = @_;
	return [] unless defined $spec && length $spec;
	return $parseCache{$spec} if $parseCache{$spec};

	my @steps;
	foreach my $raw (split /\s*;\s*/, $spec) {
		$raw =~ s/^\s+//;
		$raw =~ s/\s+$//;
		next unless length $raw;
		my ($verb, @args) = split /\s+/, $raw;
		push @steps, { verb => lc($verb), args => \@args, raw => $raw };
	}
	$parseCache{$spec} = \@steps;
	return \@steps;
}

# Separa os argumentos posicionais das palavras-chave (`chave valor`), para
# que `skill SC_WEAKNESS max target range 3 unless EFST_WEAKNESS` continue
# sendo uma linha de config e nao um formato novo.
my %STEP_KEYWORDS = map { $_ => 1 } qw(range unless if);
my %STEP_FLAGS    = map { $_ => 1 } qw(hold);

sub splitArgs {
	my ($args) = @_;
	my (@pos, %opt);
	my @in = @$args;
	while (@in) {
		my $tok = shift @in;
		my $key = lc $tok;
		if ($STEP_KEYWORDS{$key} && @in) { $opt{$key} = shift @in }
		elsif ($STEP_FLAGS{$key})        { $opt{$key} = 1 }
		else                             { push @pos, $tok }
	}
	return (\@pos, \%opt);
}

sub approachSteps { return parseSteps(cfg('approach', 'hide; chase 10')) }

sub cycleSteps {
	return parseSteps(cfg('cycle', 'attack 4; skill SC_WEAKNESS max target range 3 unless EFST_WEAKNESS; attack 2; emotion heh; skill SC_FEINTBOMB max self; cloak; chase 3 hold'));
}

sub panicNearSteps {
	return parseSteps(cfg('panicNear',
		'skill SC_IGNORANCE max target range 3 unless EFST_IGNORANCE'));
}

sub panicFarSteps {
	return parseSteps(cfg('panicFar',
		'face away; skill SC_FEINTBOMB max self; cloak; chase 4; skill SC_IGNORANCE max target range 3 unless EFST_IGNORANCE'));
}

# O `chase ... hold` do fim nao e enfeite: enquanto o Vinculo estiver de pe o
# fantasma precisa ficar a menos de DEZ celulas do oponente, senao o proprio
# rAthena corta a ligacao no meio do passo (o bloco "Shadow Form Caster
# Moving" de src/map/map.cpp:599). Grudar nele e o que mantem o vinculo vivo -
# e, de quebra, e onde a apanhar acontece, que e o ponto do golpe.
sub lowHpSteps {
	return parseSteps(cfg('lowHp',
		'skill SC_SHADOWFORM max target range 5; chase 15 hold'));
}

sub resolveSkill {
	my ($name) = @_;
	my $sk = eval { Skill->new(auto => $name) };
	return undef unless $sk && defined $sk->getIDN;
	return $sk;
}

# Executa um passo. Devolve 1 quando ele terminou.
sub runStep {
	my ($step, $target, $now) = @_;
	my $v    = $step->{verb};
	my $a    = $step->{args};
	my $data = $st{stepData};

	if ($v eq 'hide' || $v eq 'cloak' || $v eq 'show') {
		my $mode = $v eq 'hide' ? 'hide' : $v eq 'cloak' ? 'cloak' : 'none';
		return 1 if applyStealth($mode, $now);
		# Se o ZC_STATE_CHANGE nao voltar, o ciclo nao pode ficar preso
		# aqui para sempre - segue e tenta de novo na proxima volta.
		if ($now - $st{stepSince} >= cfg('toggleTimeout', 6)) {
			warnOnce("toggle", cfg('hideCommand', '@hide') . " nao confirmou em " . cfg('toggleTimeout', 6) . "s - seguindo o ciclo mesmo assim.");
			return 1;
		}
		return 0;
	}

	if ($v eq 'wait') {
		my $secs = @$a ? $a->[0] : 1;
		return ($now - $st{stepSince}) >= $secs;
	}

	if ($v eq 'emotion' || $v eq 'emote') {
		my $arg = @$a ? $a->[0] : 'heh';
		my $num = ($arg =~ /^\d+$/) ? $arg : getEmotionByCommand($arg);
		if (defined $num) {
			$messageSender->sendEmotion($num);
		} else {
			warnOnce("emo_$arg", "emoticon desconhecido: $arg (ver tables/emotions.txt).");
		}
		return 1;
	}

	if ($v eq 'face') {
		# So aparencia: neste rAthena a Copia Explosiva nao empurra quem
		# lanca (nao ha skill_blown do src em si mesmo em src/map/skill.cpp;
		# o Knockback do Id 2304 e aplicado a QUEM a bomba acerta, em
		# skill_unit_onplace_timer). Virar de costas nao muda para onde o
		# fantasma vai - muda o que o oponente ve.
		my $how = @$a ? lc($a->[0]) : 'to';
		my $pos = $target && ($target->{pos_to} || $target->{pos});
		return 1 unless $pos;
		my $dir = dirTo(myPos(), $pos);
		$dir = ($dir + 4) % 8 if $how eq 'away' || $how eq 'costas';
		$messageSender->sendLook($dir, 0);
		return 1;
	}

	if ($v eq 'skill') {
		my ($pargs, $opt) = splitArgs($a);
		my ($name, $lv, $on) = @$pargs;
		return 1 unless defined $name;

		# JA MANDADA: quem solta o passo e o servidor, nao o relogio. O
		# anuncio da propria habilidade chega pelo packet_skilluse e e
		# gravado em $st{skillOk} - antes disso o passo so terminava no
		# `skillWait` cheio, e no caso da Copia Explosiva esse 1,5s comia
		# a janela inteira de invisibilidade perfeita. O wait continua,
		# agora como teto para o caso do anuncio nao vir.
		if ($data->{sent}) {
			my $ok = $data->{idn} ? ($st{skillOk}{ $data->{idn} } || 0) : 0;
			return 1 if $ok >= $data->{sent};
			# Segunda confirmacao, so para a Copia Explosiva: o 0x40 dela
			# acendendo E o comeco da invisibilidade perfeita. Se o
			# anuncio da habilidade nao vier, este vem.
			return 1 if $data->{feint} && isHidden();
			return ($now - $data->{sent}) >= cfg('skillWait', 1.5);
		}

		my $sk = resolveSkill($name);
		if (!$sk) {
			warnOnce("sk_$name", "habilidade desconhecida: $name - passo ignorado.");
			return 1;
		}
		my $have = $char->getSkillLevel($sk);
		if (!$have) {
			warnOnce("sklv_$name", "o personagem nao tem " . $sk->getName() . " ($name) - passo ignorado.");
			return 1;
		}
		# `max` (ou nivel omitido, ou numero acima do que ele sabe) usa o
		# nivel aprendido. E o default de proposito: a habilidade sobe de
		# nivel quando o personagem sobe, e nao se quer ter de lembrar de
		# mexer no config.txt junto.
		$lv = $have if !defined $lv || $lv !~ /^\d+$/ || $lv > $have;
		$on = defined $on ? lc($on) : 'target';

		# `unless EFST_X` / `if EFST_X`: a condicao e o status REAL de quem
		# vai levar, lido do que o servidor mandou. E o que faz a Mascara
		# da Vulnerabilidade nao ser relancada em cima de si mesma - alem
		# de inutil (o `Fail: _Weakness` do db/re/status.yml recusa), cada
		# lance gasta uma Pintura Facial.
		my $who = ($on eq 'self') ? $char : $target;
		if ($opt->{unless} && hasStatus($who, $opt->{unless})) {
			debug "[pvpGhost] " . $sk->getName() . ": o alvo ja esta com $opt->{unless} - pulando.\n", "pvpGhost";
			return 1;
		}
		if ($opt->{if} && !hasStatus($who, $opt->{if})) {
			return 1;
		}

		my $tpos = $target && ($target->{pos_to} || $target->{pos});

		# `range N`: as mascaras tem Range 3 (Id 2294/2297 do skill_db) e
		# de fora disso o lance nem sai. Anda ate entrar no alcance, com
		# teto - se nao der em skillApproach segundos, desiste do passo em
		# vez de segurar o ciclo.
		if ($opt->{range} && $on ne 'self' && $tpos) {
			if (blockDistance(myPos(), $tpos) > $opt->{range}) {
				if ($now - $st{stepSince} >= cfg('skillApproach', 4)) {
					debug "[pvpGhost] " . $sk->getName() . ": nao cheguei a $opt->{range} celulas - pulando.\n", "pvpGhost";
					stopMoving();
					return 1;
				}
				routeTo($tpos->{x}, $tpos->{y}, $opt->{range}, $now);
				return 0;
			}
			# Parar antes de lancar: no rAthena quem anda para de conjurar
			# (unit_walktoxy chama unit_skillcastcancel).
			stopMoving() if AI::inQueue('route');
		}

		# ESPREITANDO NAO SE LANCA MAIS NADA. status_check_skilluse
		# (src/map/status.cpp:2212) recusa qualquer habilidade que nao
		# seja o proprio ST_CHASEWALK enquanto OPTION_CHASEWALK estiver
		# ligado - o pedido nem vira tentativa, morre no servidor. Entao
		# o passo desliga o Espreitar antes, depois de ja ter andado para
		# perto: chega sumido, aparece so para lancar.
		# (Isto quase nunca dispara na fase `panic`: o Espreitar tem
		# `RemoveOnDamaged` no db/re/status.yml, e o golpe que dispara a
		# reacao ja o teria derrubado.)
		if (isChaseWalk() && $sk->getHandle ne cfg('cloakSkill', 'ST_CHASEWALK')) {
			# Relogio proprio, e nao o do passo: o `range` acima pode ter
			# comido o tempo todo andando, e ai o teto ja estaria vencido
			# antes do primeiro toggle sair.
			$data->{uncloak} = $now unless $data->{uncloak};
			return 0 unless applyChaseWalk(0, $now)
			             || $now - $data->{uncloak} >= cfg('toggleTimeout', 6);
		}

		# Sao tres pacotes diferentes, e quem decide qual e o `TargetType`
		# do db/re/skill_db.yml do NOSSO rAthena - nao o skillsarea.txt do
		# openkore, que sai da tabela do cliente e nem sempre concorda.
		# Ex.: SC_FEINTBOMB e `TargetType: Self` no servidor.
		if ($on eq 'ground') {
			return 1 unless $tpos;
			$messageSender->sendSkillUseLoc($sk->getIDN, $lv, $tpos->{x}, $tpos->{y});
		} else {
			$messageSender->sendSkillUse($sk->getIDN, $lv,
				($on eq 'self') ? $char->{ID} : $target->{ID});
		}
		message "[pvpGhost] " . $sk->getName() . " nivel $lv.\n", "success";
		$data->{sent} = $now;
		$data->{idn}  = $sk->getIDN;

		# Abre a janela em que o OPTION_INVISIBLE e da habilidade, e nao
		# do @hide: o tempo de conjuracao (CastTime 1000) mais a duracao
		# da invisibilidade perfeita (Duration1 1500), com folga.
		if ($sk->getHandle eq cfg('feintSkill', 'SC_FEINTBOMB')) {
			$data->{feint}  = 1;
			$st{feintUntil} = $now + cfg('feintWindow', 3);
		}
		return 0;
	}

	if ($v eq 'chase') {
		my ($pargs, $opt) = splitArgs($a);
		my $secs = @$pargs ? $pargs->[0] : 3;
		my $stop = defined $opt->{range} ? $opt->{range} : cfg('chaseDistance', 1);
		my $pos  = $target->{pos_to} || $target->{pos};
		return ($now - $st{stepSince}) >= $secs unless $pos;

		# CHEGOU: acaba o passo NA HORA. Enquanto ele so acabava no tempo
		# escrito, o `chase 10` da aproximacao segurava o ciclo por dez
		# segundos mesmo com o jogador encostado - era essa a espera entre
		# ver alguem entrar na arena e o primeiro golpe. Com `hold` o
		# passo dura o tempo inteiro de proposito, que e o que se quer
		# depois do `cloak`: seguir de perto, sumido.
		if (!$opt->{hold} && blockDistance(myPos(), $pos) <= $stop) {
			stopMoving() if AI::inQueue('route');
			return 1;
		}

		routeTo($pos->{x}, $pos->{y}, $stop, $now);
		return ($now - $st{stepSince}) >= $secs;
	}

	if ($v eq 'attack') {
		my $secs = @$a ? $a->[0] : 5;

		# @hide impede o golpe, entao o relogio do ataque so comeca a
		# correr quando o char esta mesmo visivel.
		if (!applyStealth('none', $now)) {
			$data->{waitVis} = $now unless $data->{waitVis};
			if ($now - $data->{waitVis} < cfg('toggleTimeout', 6)) {
				$st{stepSince} = $now;
				return 0;
			}
		}

		# Ao entrar no passo, matar o passo residual do `chase` anterior:
		# ha um sendMove em voo, e no rAthena quem anda para de atacar
		# (unit_walktoxy chama unit_stop_attack). Sem isto o sendAction
		# chega e e desfeito pelo movimento que ainda esta executando.
		unless ($data->{entered}) {
			$data->{entered} = 1;
			stopMoving();
			$char->sendAttackStop;
		}

		my $pos = $target->{pos_to} || $target->{pos};
		return ($now - $st{stepSince}) >= $secs unless $pos;

		# PERSEGUIR E TRABALHO NOSSO, E ISSO NAO E OPCIONAL.
		#
		# O sendAction(ID, 7) e "ataque continuo", mas continuo nao quer
		# dizer que o servidor persegue. Em unit_attack_timer_sub
		# (src/map/unit.cpp:3260) o alvo fora de alcance tem DOIS
		# tratamentos diferentes:
		#
		#   if (sd && !check_distance_client_bl(...))  clif_movetoattack()
		#   else if (md && !check_distance_bl(...))    unit_walktobl()
		#
		# So o MONSTRO (md) e perseguido pelo servidor. Quando quem ataca
		# e um JOGADOR (sd), o rAthena apenas avisa o cliente ("longe
		# demais, ande ate la") e devolve a bola - quem anda e o cliente
		# oficial. O openkore nao e o cliente oficial e a IA nativa esta
		# desligada, entao ninguem andava: bastava o alvo dar dois passos
		# para o fantasma ficar plantado ate o ciclo seguinte. Reenviar o
		# sendAction nao resolve, porque o comando chega e volta com a
		# mesma resposta.
		my $range = cfg('attackRange', 0) || $char->{attack_range} || 1;
		if (blockDistance(myPos(), $pos) > $range) {
			$data->{hit} = 0;   # ao encostar, o golpe sai no mesmo tique
			routeTo($pos->{x}, $pos->{y}, $range, $now);
			return ($now - $st{stepSince}) >= $secs;
		}

		stopMoving() if AI::inQueue('route');

		# Dentro do alcance: reafirma o alvo. Dois gatilhos - o intervalo
		# de fundo e a mudanca de celula do alvo, com attackRefresh de
		# piso para o alvo andando nao virar um pacote por tique.
		my $cell = "$pos->{x},$pos->{y}";
		my $due  = $now - $st{lastAttack};

		if (!$data->{hit}
		 || ($cell ne ($data->{cell} || '') && $due >= cfg('attackRefresh', 0.4))
		 || $due >= cfg('attackInterval', 2)) {
			$st{lastAttack} = $now;
			$data->{hit}    = 1;
			$data->{cell}   = $cell;
			$messageSender->sendAction($target->{ID}, 7);
		}
		return ($now - $st{stepSince}) >= $secs;
	}

	warnOnce("verb_$v", "passo desconhecido \"$step->{raw}\" - ignorado.");
	return 1;
}

sub startPhase {
	my ($phase, $now) = @_;
	$st{phase}     = $phase;
	$st{stepIndex} = 0;
	$st{stepSince} = $now;
	$st{stepData}  = {};
	$st{panicList} = undef;
}

sub advanceStep {
	my ($now) = @_;
	$st{stepIndex}++;
	$st{stepSince} = $now;
	$st{stepData}  = {};
}

#########################################################################
# Os tres estados
#########################################################################

sub enterState {
	my ($name, $now, $count) = @_;
	return if $st{state} eq $name;

	my $from = $st{state} || '-';
	$st{state}      = $name;
	$st{stateSince} = $now;

	if ($name eq 'chasing') {
		$st{targetID} = undef;
		$st{phase}    = '';
		$char->sendAttackStop;
		stopMoving();
		$st{wpSince}  = $now;
		message "[pvpGhost] $from -> em busca (patrulhando).\n", "success";

	} elsif ($name eq 'attacking') {
		startPhase('approach', $now);
		stopMoving();
		message "[pvpGhost] $from -> atacando.\n", "success";

	} elsif ($name eq 'sleeping') {
		$st{targetID}   = undef;
		$st{phase}      = '';
		$st{sleepUntil} = $now + cfg('sleepCheck', 5);
		$char->sendAttackStop;
		stopMoving();
		message "[pvpGhost] $from -> dormindo ($count jogadores).\n", "success";
	}
}

sub patrolPoints {
	my $spec = cfg('patrol', '99 99, 99 130, 99 99, 131 99, 99 99, 99 68, 99 99, 70 99');
	return $parseCache{"wp:$spec"} if $parseCache{"wp:$spec"};

	my @pts;
	foreach my $pair (split /\s*,\s*/, $spec) {
		my ($x, $y) = $pair =~ /^\s*(\d+)\s+(\d+)\s*$/;
		next unless defined $y;
		push @pts, { x => $x, y => $y };
	}
	$parseCache{"wp:$spec"} = \@pts;
	return \@pts;
}

sub tickChasing {
	my ($now) = @_;
	applyStealth('hide', $now);

	my $pts = patrolPoints();
	unless (@$pts) {
		warnOnce("nopatrol", "pvpGhost_patrol vazio ou mal escrito - o fantasma nao vai andar.");
		return;
	}

	my $wp  = $pts->[ $st{wpIndex} % scalar(@$pts) ];
	my $tol = cfg('patrolTolerance', 3);

	# Chegou: proximo ponto da cruz. TEM de ser blockDistance, a mesma
	# metrica que o `distFromGoal` do Task::Route usa para parar
	# (Task/Route.pm:285). Com a distancia euclidiana do Utils::distance
	# a rota terminaria a 3 celulas em diagonal, este teste diria 4,24 e
	# a patrulha ficaria reemitindo a mesma rota ate o patrolLegTimeout.
	if (blockDistance(myPos(), $wp) <= $tol) {
		$st{wpIndex} = ($st{wpIndex} + 1) % scalar(@$pts);
		$st{wpSince} = $now;
		stopMoving();
		# `debug`, nao `message`: em 24/7 uma perna a cada ~4s daria umas
		# 21 mil linhas por dia de log. Para ver onde ele esta na ronda
		# existe o comando `pvpghost`, que mostra o ponto atual.
		my $next = $pts->[ $st{wpIndex} ];
		debug sprintf("[pvpGhost] Ronda: cheguei em %d,%d - indo para %d,%d (ponto %d de %d).\n",
			$wp->{x}, $wp->{y}, $next->{x}, $next->{y},
			$st{wpIndex} + 1, scalar(@$pts)), "pvpGhost";
		return;
	}

	# Perna travada (rota impossivel, char preso): pula para a proxima em
	# vez de reemitir a mesma rota para sempre.
	if ($now - $st{wpSince} >= cfg('patrolLegTimeout', 40)) {
		warning "[pvpGhost] nao cheguei em ($wp->{x}, $wp->{y}) - pulando o ponto.\n";
		$st{wpIndex} = ($st{wpIndex} + 1) % scalar(@$pts);
		$st{wpSince} = $now;
		stopMoving();
		return;
	}

	routeTo($wp->{x}, $wp->{y}, $tol, $now);
}

sub tickAttacking {
	my ($now, @targets) = @_;

	# O alvo continua sendo o mesmo enquanto estiver a vista.
	my ($target) = grep { $st{targetID} && $_->{ID} eq $st{targetID} } @targets;

	# Sumiu da lista mas o estado ainda e attacking: e a janela de graca
	# do onMainLoop. O ciclo CONGELA em vez de recomecar - inclusive o
	# relogio do passo, senao um `attack 5` acabaria durante a piscada.
	if (!$target && !@targets) {
		$st{frozenAt} ||= $now;
		return;
	}
	if ($st{frozenAt}) {
		$st{stepSince} += $now - $st{frozenAt};
		$st{frozenAt} = 0;
	}

	# Alvo de verdade novo (ou o primeiro): a receita comeca do zero.
	if (!$target) {
		$target = nearestOf(@targets);
		return unless $target;
		$st{targetID} = $target->{ID};
		startPhase('approach', $now);
		message "[pvpGhost] Alvo: " . $target->name . ".\n", "success";
	}

	# SANGRANDO: abaixo de lowHpPercent ele para de tentar ganhar e passa a
	# tentar nao morrer. Tem precedencia sobre TUDO, inclusive sobre a
	# reacao ao golpe pesado - mascarar o oponente nao adianta nada com a
	# barra no fim.
	if ($st{phase} ne 'shadow' && lowHpTrigger($now)) {
		message sprintf("[pvpGhost] HP em %.0f%% - Vinculo Sombrio.\n",
			100 * ($char->{hp} || 0) / ($char->{hp_max} || 1)), "success";
		$st{shadowUntil} = $now + cfg('lowHpTimeout', 15);
		$char->sendAttackStop;
		stopMoving();
		startPhase('shadow', $now);
	}

	if ($st{phase} eq 'shadow') {
		my $steps = lowHpSteps();
		# O teto de tempo vale mesmo com a receita no meio: se o Vinculo
		# nao sair (SP curto, oponente ja ligado a outro), o fantasma nao
		# pode ficar preso aqui enquanto apanha.
		if (!@$steps || $st{stepIndex} > $#$steps || $now >= $st{shadowUntil}) {
			$st{shadowEnd} = $now;
			startPhase('cycle', $now);
			return;
		}
		my $sstep = $steps->[ $st{stepIndex} ];
		return unless runStep($sstep, $target, $now);
		$char->sendAttackStop if $sstep->{verb} eq 'attack';
		advanceStep($now);
		return;
	}

	# A REACAO AO GOLPE PESADO TEM PRIORIDADE SOBRE O CICLO. Ela nao e
	# uma receita so: a cada tentativa se escolhe entre a de perto e a de
	# longe pela distancia daquele instante, e se para assim que o status
	# cola no alvo - ou quando as tentativas acabam.
	if ($st{phase} eq 'panic') {
		if (!$st{panicList}) {
			startPanicAttempt($target, $now);
			return;
		}
		if ($st{stepIndex} > $#{ $st{panicList} }) {
			my $status = cfg('panicStatus', 'EFST_IGNORANCE');
			if (hasStatus($target, $status)) {
				message "[pvpGhost] Mascara colou - de volta ao ciclo.\n", "success";
				endPanic($now);
				return;
			}
			if ($st{panicTries} >= cfg('panicTries', 2)) {
				message "[pvpGhost] Mascara nao colou em $st{panicTries} tentativa(s) - de volta ao ciclo.\n", "success";
				endPanic($now);
				return;
			}
			startPanicAttempt($target, $now);
			return;
		}

		my $pstep = $st{panicList}[ $st{stepIndex} ];
		return unless runStep($pstep, $target, $now);
		$char->sendAttackStop if $pstep->{verb} eq 'attack';
		advanceStep($now);
		return;
	}

	my $steps = ($st{phase} eq 'approach') ? approachSteps() : cycleSteps();

	# Fim da lista: da aproximacao passa para o ciclo; do ciclo, repete o
	# ciclo. E o `startPhase` que zera o passo e o relogio.
	if (!@$steps || $st{stepIndex} > $#$steps) {
		startPhase('cycle', $now);
		return;
	}

	my $step = $steps->[ $st{stepIndex} ];
	return unless runStep($step, $target, $now);

	# Saindo de um `attack`: o rAthena continuaria perseguindo e batendo
	# sozinho (unit_attack, continuous=1) por conta do sendAction(ID, 7),
	# e ia brigar com o Task::Route do `chase` seguinte. O sendAttackStop
	# do openkore e um "andar para onde ja estou", que e o que o cliente
	# de verdade manda para cancelar o ataque continuo.
	$char->sendAttackStop if $step->{verb} eq 'attack';

	advanceStep($now);
}

#########################################################################
# A reacao ao HP baixo (fase `shadow`)
#########################################################################

# O VINCULO SOMBRIO POE O STATUS EM QUEM LANCA, NAO EM QUEM LEVA - e por
# isso a guarda de "ja esta ligado" olha o proprio fantasma, e nao o
# oponente. Quem faz isso e o `sc_start4(src, src, ...)` do
# src/map/skills/thief/shadowform.cpp: o alvo entra como `val2`, que e o
# id de quem vai COMER o dano que o fantasma levar, ate `4 + nivel` golpes.
#
# Duas consequencias que o passo `skill` sozinho nao teria como saber:
#
#   - QUEM ESTA COM O VINCULO NAO LANCA MAIS NADA E NAO BATE. O
#     skill_check_condition_castbegin recusa qualquer habilidade a quem
#     tem SC__SHADOWFORM (src/map/skill.cpp:8327), e o status ainda traz
#     `NoAttack` no db/re/status.yml. E o preco do golpe, nao defeito
#     daqui - mas e o motivo de existir o `pvpGhost_lowHpTimeout`.
#   - O ALVO TEM DE SER JOGADOR e nao pode ja estar ligado a outra pessoa
#     (`dstsd && !dstsd->shadowform_id`), senao o lance falha calado. Na
#     arena de um jogador so isso nunca aparece; em outro cenario,
#     apareceria como um Vinculo que nunca cola.
sub lowHpTrigger {
	my ($now) = @_;
	return 0 unless $char;

	my $max = $char->{hp_max} || 0;
	return 0 unless $max > 0;
	return 0 if 100 * ($char->{hp} || 0) / $max >= cfg('lowHpPercent', 10);

	# Ja ligado: o EFST fica em NOS.
	return 0 if hasStatus($char, cfg('lowHpStatus', 'EFST_SHADOWFORM'));
	return 0 if $now - $st{shadowEnd} < cfg('lowHpTimeout', 15);

	# Sem a habilidade nao ha reacao - e sem esta guarda o fantasma
	# entraria na fase, o passo `skill` avisaria e ele voltaria ao ciclo,
	# de novo e de novo, a cada tique abaixo dos 10%.
	my $sk = resolveSkill(cfg('lowHpSkill', 'SC_SHADOWFORM'));
	return 0 unless $sk && $char->getSkillLevel($sk);
	return 1;
}

#########################################################################
# A reacao ao golpe pesado (fase `panic`)
#########################################################################

# Escolhe a receita da tentativa PELA DISTANCIA DO MOMENTO, e nao uma vez
# so no comeco: entre a primeira tentativa e a segunda o oponente andou, e
# a Copia Explosiva da receita de longe nao faz sentido se ele ja esta
# colado.
sub startPanicAttempt {
	my ($target, $now) = @_;

	$st{panicTries}++;
	my $pos   = $target && ($target->{pos_to} || $target->{pos});
	my $range = cfg('masqueradeRange', 3);
	my $near  = ($pos && blockDistance(myPos(), $pos) <= $range) ? 1 : 0;

	$st{panicList} = $near ? panicNearSteps() : panicFarSteps();
	$st{stepIndex} = 0;
	$st{stepSince} = $now;
	$st{stepData}  = {};

	message sprintf("[pvpGhost] Mascara da Tolice, tentativa %d de %d (%s).\n",
		$st{panicTries}, cfg('panicTries', 2),
		$near ? "de perto" : "de longe"), "success";
}

sub endPanic {
	my ($now) = @_;
	$st{panicEnd} = $now;
	startPhase('cycle', $now);
}

# Chamada de dentro do hook de pacote, nao do laco principal: e por isso
# que ela mesma corta o ataque continuo e a rota em curso, em vez de
# esperar o proximo tique.
sub triggerPanic {
	my ($sourceID, $dmg, $max, $now) = @_;

	return unless $st{state} eq 'attacking';
	return if $st{phase} eq 'panic';
	# A fase `shadow` GANHA desta, e a guarda tem de estar aqui tambem: esta
	# funcao e chamada de dentro do hook de pacote, e nao pelo laco principal
	# - a precedencia escrita em tickAttacking nao a alcanca. Sem isto, o
	# primeiro golpe pesado que chegasse durante o Vinculo trocaria a fase e
	# mandaria o fantasma correr atras de uma mascara com a barra no fim.
	return if $st{phase} eq 'shadow';
	return if $now - $st{panicEnd} < cfg('panicCooldown', 8);

	# Quem bateu vira o alvo. Na arena de 1 jogador e sempre o mesmo, mas
	# se nao for, e nele que a mascara tem de ir.
	if ($sourceID && $playersList && $playersList->getByID($sourceID)) {
		$st{targetID} = $sourceID;
	}

	message sprintf("[pvpGhost] Levei %d de %d de HP (%.0f%%) - indo de Mascara da Tolice.\n",
		$dmg, $max, 100 * $dmg / $max), "success";

	$st{panicTries} = 0;
	$char->sendAttackStop;
	stopMoving();
	startPhase('panic', $now);
}

# Serve a dois donos, e por isso o `return` no meio: as habilidades que
# saem de nos so interessam como confirmacao para o passo `skill`; as que
# entram em nos sao o gatilho da fase `panic`.
sub onSkillUse {
	my (undef, $args) = @_;
	return unless $config{pvpGhost} && $char && $accountID;

	my $now = time;

	if ($args->{sourceID} && $args->{sourceID} eq $accountID) {
		$st{skillOk}{ $args->{skillID} } = $now;
		return;
	}

	return unless $args->{targetID} && $args->{targetID} eq $accountID;

	my $dmg = $args->{damage} || 0;
	return unless $dmg > 0;

	# A referencia e o HP MAXIMO, nao o atual: "27% da vida dele" tem de
	# querer dizer a mesma coisa com a barra cheia e com ela pela metade.
	my $max = $char->{hp_max} || 0;
	return unless $max > 0;
	return if $dmg < $max * cfg('panicDamage', 0.27);

	triggerPanic($args->{sourceID}, $dmg, $max, $now);
}

# As mascaras gastam uma Pintura Facial (6120) por lance e exigem o Pincel
# de Maquiagem (6121) no inventario, e a Tinta Infinita NAO cobre nenhum
# dos dois - ela so isenta a Tinta para Parede 6123
# (src/custom/tinta_infinita.hpp). Sem este aviso, acabar a Pintura seria
# um fantasma que simplesmente para de usar mascara, sem dizer por que.
sub onSkillFail {
	my (undef, $args) = @_;
	return unless $config{pvpGhost};
	my $name = eval { Skill->new(idn => $args->{skillID})->getName() } || $args->{skillID};
	warnOnce("fail_$args->{skillID}_$args->{cause}",
		"a habilidade $name falhou: " . ($args->{failMessage} || '?') .
		($args->{itemId} ? " (item $args->{itemId})" : '') . ".");
}

sub tickSleeping {
	my ($now) = @_;
	applyStealth('hide', $now);
	stopMoving() if AI::inQueue('route');
}

#########################################################################

sub onMainLoop {
	return unless $config{pvpGhost};
	return unless $net && $net->getState() == Network::IN_GAME;
	return unless $char && $field;

	my $now = time;
	return if $now - $st{lastCheck} < 0.2;
	$st{lastCheck} = $now;

	my $map = cfg('map', 'pvp_n_1-5');

	# Fora da arena: o unico caso normal e a morte - o OnPCDieEvent de
	# npc/guerra/arena_de_combate.txt cura e joga o morto em prontera.
	# Volta sozinho, com folga entre as tentativas para nao correr com
	# o teleporte do proprio script.
	if ($field->baseName ne $map) {
		my $lastReturn = $st{lastReturn};
		onReset();
		$st{lastReturn} = $lastReturn;
		my $back = cfg('returnCommand', '');
		return unless length $back;
		return if $now - $st{lastReturn} < 8;
		$st{lastReturn} = $now;
		message "[pvpGhost] Fora de $map, voltando com \"$back\".\n", "success";
		sendMessage($messageSender, "c", $back);
		return;
	}

	my @targets = liveTargets();
	my $count   = scalar @targets;
	my $max     = cfg('maxPlayers', 1);

	my $want = ($count > $max) ? 'sleeping'
	         : ($count >= 1)   ? 'attacking'
	         :                   'chasing';

	# HISTERESE NA PERDA DO ALVO. O alcance de visao tem borda (area_size,
	# 14 celulas), e um jogador andando nela entra e sai da lista varias
	# vezes por minuto. Sem esta janela o ciclo de combate reiniciava do
	# zero a cada piscada e nunca fechava uma volta - foi o que apareceu
	# no teste de 2026-08-27, com trocas de estado a cada 0,4s.
	$st{lastSeen} = $now if $count >= 1;
	if ($want eq 'chasing' && $st{state} eq 'attacking'
	 && $now - $st{lastSeen} < cfg('targetGrace', 5)) {
		$want = 'attacking';
	}

	# Dormindo ele nao olha a arena a cada tique: abre os olhos de
	# pvpGhost_sleepCheck em pvpGhost_sleepCheck segundos, e so entao a
	# contagem recem-feita vale.
	if ($st{state} eq 'sleeping') {
		if ($now < $st{sleepUntil}) {
			$want = 'sleeping';
		} else {
			$st{sleepUntil} = $now + cfg('sleepCheck', 5);
			message "[pvpGhost] Acordando: $count jogador(es) por perto.\n", "success"
				if $want ne 'sleeping';
		}
	}

	enterState($want, $now, $count);

	if    ($st{state} eq 'chasing')   { tickChasing($now) }
	elsif ($st{state} eq 'attacking') { tickAttacking($now, @targets) }
	elsif ($st{state} eq 'sleeping')  { tickSleeping($now) }
}

sub onCommand {
	my @targets = liveTargets();
	my $steps   = ($st{phase} eq 'approach') ? approachSteps()
	            : ($st{phase} eq 'cycle')    ? cycleSteps()
	            : ($st{phase} eq 'panic')    ? ($st{panicList} || [])
	            : ($st{phase} eq 'shadow')   ? lowHpSteps()
	            :                              [];
	my $step    = ($st{stepIndex} <= $#$steps) ? $steps->[ $st{stepIndex} ]{raw} : '-';
	my $target  = $st{targetID} ? Actor::get($st{targetID}) : undef;
	my $pts     = patrolPoints();
	my $wp      = @$pts ? $pts->[ $st{wpIndex} % scalar(@$pts) ] : undef;

	message sprintf(
		"[pvpGhost] ligado=%s mapa=%s aqui=%s sumido=%s perto=%d\n" .
		"[pvpGhost] estado=%s ha %.1fs | alvo=%s | passo=%s/%s\n" .
		"[pvpGhost] patrulha=ponto %d de %d (%s) | andando=%s\n" .
		"[pvpGhost] alvo-sem-arma=%s | alvo-calado=%s | reacao=%s\n" .
		"[pvpGhost] hp=%d/%d (%.0f%%) | vinculo=%s\n",
		($config{pvpGhost} ? 'sim' : 'nao'),
		cfg('map', 'pvp_n_1-5'),
		($field ? $field->baseName : '-'),
		stealthNow(),
		scalar(@targets),
		($st{state} || '-'),
		($st{stateSince} ? time - $st{stateSince} : 0),
		($target ? $target->name : '-'),
		($st{phase} || '-'), $step,
		($st{wpIndex} + 1), scalar(@$pts),
		($wp ? "$wp->{x},$wp->{y}" : '-'),
		(AI::inQueue('route') ? 'sim' : 'nao'),
		(hasStatus($target, 'EFST_WEAKNESS')  ? 'sim' : 'nao'),
		(hasStatus($target, cfg('panicStatus', 'EFST_IGNORANCE')) ? 'sim' : 'nao'),
		($st{phase} eq 'panic' ? "tentativa $st{panicTries}" : '-'),
		($char->{hp} || 0), ($char->{hp_max} || 0),
		(100 * ($char->{hp} || 0) / ($char->{hp_max} || 1)),
		(hasStatus($char, cfg('lowHpStatus', 'EFST_SHADOWFORM')) ? 'ligado' : 'nao'),
	), "list";
}

1;
