/* Guerra do Emperium — o pouco de JavaScript que o site precisa.
 *
 * Sem framework de proposito: sao quatro telas e seis chamadas. Uma
 * dependencia aqui custaria mais para manter do que o arquivo inteiro.
 */
"use strict";

const $  = (s, raiz = document) => raiz.querySelector(s);
const $$ = (s, raiz = document) => [...raiz.querySelectorAll(s)];

/* Uma unica coisa de estado no arquivo: se ha sessao aberta.
 *
 * Existe porque o painel ganhou um botao de Download (2026-08-22), e com
 * ele o caminho painel -> download -> Voltar passou a ser comum. Sem saber
 * que ha sessao, o Voltar joga um jogador logado na tela de boas-vindas, e
 * o botao "Conta" de la abre o formulario de login para quem ja entrou. */
let logado = false;

/* E se essa sessao manda no painel de usuarios. Fica AQUI EM CIMA, e nao
 * junto do resto do codigo de administrador la' embaixo, porque o vaiPara
 * a le': um `let` declarado depois estaria na zona morta temporal, e a
 * primeira navegacao morreria com ReferenceError. */
let ehAdmin = false;

/* ---------- navegacao entre telas ---------- */
function vaiPara(nome) {
  // Quem ja entrou nao tem o que fazer no formulario de login.
  if (nome === "conta" && logado) nome = "painel";
  // E quem nao e' administrador nao tem o que fazer na tela de usuarios -
  // nem por link colado na barra de endereco. Isto e' cortesia, nao trava:
  // as rotas /api/admin/ conferem o grupo no banco (admin.go).
  if (nome === "admin" && !ehAdmin) nome = logado ? "painel" : "inicio";
  $$(".tela").forEach(t => t.classList.toggle("ativa", t.id === "tela-" + nome));
  // O hash deixa o botao voltar do navegador funcionar, que e' o primeiro
  // reflexo de quem se perde numa tela.
  if (location.hash !== "#" + nome) history.pushState({}, "", "#" + nome);
  window.scrollTo(0, 0);
  // Buscada ao ENTRAR, e nao na carga da pagina: a consulta varre a `login`
  // e o `loginlog`, e quem entrou so' para baixar o jogo nao paga por isso.
  if (nome === "admin") carregaAdmin();
}

addEventListener("popstate", () => aplicaHash());

function aplicaHash() {
  const nome = (location.hash || "#inicio").slice(1);
  const alvo = $("#tela-" + nome);
  $$(".tela").forEach(t => t.classList.remove("ativa"));
  (alvo || $("#tela-inicio")).classList.add("ativa");
}

$$("[data-ir]").forEach(b => b.onclick = () => vaiPara(b.dataset.ir));

/* ---------- abas de conta ---------- */
$$(".aba").forEach(aba => {
  aba.onclick = () => {
    $$(".aba").forEach(a => a.classList.toggle("ativa", a === aba));
    $$(".painel-aba").forEach(p => {
      p.classList.toggle("ativa", p.id === "form-" + aba.dataset.aba);
    });
  };
});

/* ---------- rotulo do documento ---------- */
const rotulos = {
  celular: ["Celular", "Com DDD. Ex: (11) 91234-5678"],
  cpf:     ["CPF", "Somente numeros ou com pontuacao"]
};
$$("input[name=tipo]").forEach(r => {
  r.onchange = () => {
    const [rotulo, ajuda] = rotulos[r.value];
    $("[data-rotulo-doc]").textContent = rotulo;
    $("[data-ajuda-doc]").textContent = ajuda;
  };
});

/* ---------- conversa com a API ---------- */
async function chama(caminho, corpo, metodo = "POST") {
  const opcoes = {
    method: metodo,
    headers: { "Content-Type": "application/json" },
    // O cookie de sessao e' HttpOnly; sem isto ele nao viaja.
    credentials: "same-origin"
  };
  if (corpo) opcoes.body = JSON.stringify(corpo);

  const r = await fetch(caminho, opcoes);
  let dados = {};
  try { dados = await r.json(); } catch (_) { /* resposta sem corpo */ }
  if (!r.ok) throw new Error(dados.erro || "Algo deu errado. Tente de novo.");
  return dados;
}

function recado(form, texto, tipo) {
  const p = $("[data-recado]", form) || $("[data-recado]", form.closest(".cartao"));
  if (!p) return;
  p.textContent = texto || "";
  p.className = "recado" + (tipo ? " " + tipo : "");
}

// Trava o botao durante a requisicao. Sem isto, clicar duas vezes rapido
// manda dois cadastros — e o segundo bate na trava de documento repetido,
// dando erro para quem nao fez nada de errado.
async function comBotaoTravado(form, tarefa) {
  const botao = $("button[type=submit]", form);
  const texto = botao.textContent;
  botao.disabled = true;
  botao.textContent = "Aguarde...";
  try { await tarefa(); }
  finally { botao.disabled = false; botao.textContent = texto; }
}

/* ---------- entrar ---------- */
$("#form-entrar").onsubmit = e => {
  e.preventDefault();
  const f = e.target;
  comBotaoTravado(f, async () => {
    recado(f, "");
    try {
      const d = await chama("/api/sessao", {
        usuario: f.usuario.value.trim(),
        senha: f.senha.value
      });
      f.reset();
      abrePainel(d.usuario);
    } catch (err) {
      recado(f, err.message, "erro");
    }
  });
};

/* ---------- criar conta ---------- */
$("#form-criar").onsubmit = e => {
  e.preventDefault();
  const f = e.target;
  comBotaoTravado(f, async () => {
    recado(f, "");

    const dados = {
      usuario: f.usuario.value.trim(),
      senha: f.senha.value,
      email: f.email.value.trim(),
      sexo: $("input[name=sexo]:checked", f).value,
      tipo: $("input[name=tipo]:checked", f).value,
      documento: f.documento.value
    };

    try {
      // Segundo passo: ja' temos um pedido aberto e o jogador digitou o
      // codigo. So' acontece quando o servidor esta' em modo Penelope.
      if (f.dataset.pedido) {
        dados.pedido = f.dataset.pedido;
        dados.codigo = f.codigo.value.trim();
        const d = await chama("/api/conta/confirma", dados);
        delete f.dataset.pedido;
        f.reset();
        abrePainel(d.usuario);
        return;
      }

      const d = await chama("/api/conta/inicia", dados);

      if (d.precisa_codigo) {
        f.dataset.pedido = d.pedido;
        $("#campo-codigo").classList.remove("escondido");
        $("button[type=submit]", f).textContent = "Confirmar codigo";
        recado(f, d.mensagem, "certo");
        f.codigo.focus();
        return;
      }

      f.reset();
      abrePainel(d.usuario);
    } catch (err) {
      recado(f, err.message, "erro");
    }
  });
};

/* ---------- painel ---------- */
function abrePainel(usuario) {
  $("[data-nome]").textContent = usuario || "jogador";
  entrouNaConta();
  vaiPara("painel");
  carregaPainel();
}

// entrouNaConta e' o unico lugar que liga o estado - e ele tambem reaponta
// o Voltar da tela de download. Ali o botao nasce apontando para o inicio,
// que e' o certo para visitante; para quem esta logado, o lugar de onde ele
// veio e' o painel.
function entrouNaConta() {
  logado = true;
  const voltar = $("#tela-download .voltar");
  if (voltar) voltar.dataset.ir = "painel";
}

async function carregaPainel() {
  try {
    const d = await chama("/api/painel", null, "GET");
    $("[data-nome]").textContent = d.usuario;
    $("[data-email]").textContent = d.email || "";
    entrouNaConta();
    aplicaPermissao(d.admin === true);
  } catch (_) {
    logado = false;
    aplicaPermissao(false);
    vaiPara("conta");
  }
}

// aplicaPermissao e' o unico lugar que liga e desliga o botao de Usuarios.
// Um so', para nao existir caminho que mostre o botao e outro que esqueca
// de esconde-lo - a saida da conta passa por aqui tambem.
function aplicaPermissao(pode) {
  ehAdmin = pode;
  $$(".so-admin").forEach(b => b.classList.toggle("escondido", !pode));
}

$$("[data-abre]").forEach(b => {
  b.onclick = () => {
    const alvo = $("#form-" + b.dataset.abre);
    const abrindo = alvo.classList.contains("escondido");
    $$(".dobra").forEach(d => d.classList.add("escondido"));
    alvo.classList.toggle("escondido", !abrindo);
    if (!abrindo) return;
    // A lista de personagens e' buscada ao ABRIR, e nao na carga da pagina:
    // quem entrou so' para trocar a senha nao paga uma consulta a tabela
    // `char` por isso.
    //
    // Nas duas dobras, e nao so' na de destravar: o formulario de chamado
    // completa o nome do personagem a partir da MESMA lista, e sem isto ela
    // so' existiria para quem tivesse aberto a outra dobra antes. A
    // diferenca e' que a de destravar sempre recarrega (o estado
    // "conectado" muda enquanto o jogador mexe na tela) e a de chamado
    // busca uma vez so'.
    if (b.dataset.abre === "personagens") carregaPersonagens();
    if (b.dataset.abre === "chamado" && !$("#lista-personagens").children.length) {
      buscaPersonagens().catch(() => { /* sem a lista o campo ainda aceita digitacao */ });
    }
  };
});

/* ---------- destravar personagem ----------
 *
 * Ha mapas que o rAthena conhece e o nosso cliente de 2021 ainda nao tem, e
 * o jogador consegue chegar neles. Quem chega fica PRESO: toda entrada
 * seguinte no jogo o poe de volta no mesmo lugar, e so' um GM tirava.
 *
 * A lista e desenhada por JS e nao por HTML fixo porque o numero de
 * personagens varia de 0 a 9, e o botao de cada um depende do estado dele.
 */
// buscaPersonagens traz a lista e ja' alimenta o datalist do formulario de
// chamado - quem abre chamado sobre um personagem digita o nome, e nome de
// RO se erra facil.
async function buscaPersonagens() {
  const d = await chama("/api/painel/personagens", null, "GET");
  const lista = d.personagens || [];
  preencheDatalist(lista);
  return lista;
}

async function carregaPersonagens() {
  const caixa = $("[data-lista-personagens]");
  caixa.innerHTML = '<p class="miudo">Carregando…</p>';

  let lista;
  try {
    lista = await buscaPersonagens();
  } catch (err) {
    caixa.innerHTML = "";
    caixa.append(paragrafo("miudo", err.message));
    return;
  }

  caixa.innerHTML = "";
  if (!lista.length) {
    caixa.append(paragrafo("miudo",
      "Você ainda não criou nenhum personagem nesta conta."));
    return;
  }

  for (const p of lista) caixa.append(linhaDePersonagem(p));
}

function paragrafo(classe, texto) {
  const el = document.createElement("p");
  el.className = classe;
  el.textContent = texto;
  return el;
}

function linhaDePersonagem(p) {
  const linha = document.createElement("div");
  linha.className = "personagem";

  const info = document.createElement("div");
  info.className = "quem";
  const nome = document.createElement("strong");
  // textContent e nao innerHTML: nome de personagem e' texto que o jogador
  // escolheu, e ele passa pelo filtro do jogo, nao pelo nosso.
  nome.textContent = p.nome;
  const onde = paragrafo("miudo", "nível " + p.nivel + " · " + p.mapa +
    (p.online ? " · conectado agora" : ""));
  info.append(nome, onde);

  const botao = document.createElement("button");
  botao.className = "botao fantasma curto";
  botao.type = "button";

  if (p.online) {
    botao.textContent = "Conectado";
    botao.disabled = true;
    botao.title = "Saia do jogo para poder mover este personagem";
  } else if (p.em_casa) {
    botao.textContent = "Em Prontera";
    botao.disabled = true;
  } else {
    botao.textContent = "Ir para Prontera";
    botao.onclick = () => destrava(p, botao);
  }

  linha.append(info, botao);
  return linha;
}

async function destrava(p, botao) {
  const caixa = $("[data-lista-personagens]");
  const texto = botao.textContent;
  botao.disabled = true;
  botao.textContent = "Movendo…";
  try {
    const d = await chama("/api/painel/destrava", { personagem: p.id });
    recado(caixa, d.mensagem, "certo");
    // Recarrega em vez de acertar a linha na mao: assim o que aparece na
    // tela e' o que o banco tem, e nao o que o JavaScript supos.
    await carregaPersonagens();
  } catch (err) {
    recado(caixa, err.message, "erro");
    botao.disabled = false;
    botao.textContent = texto;
  }
}

/* ---------- chamado ---------- */
function preencheDatalist(lista) {
  const dl = $("#lista-personagens");
  if (!dl) return;
  dl.innerHTML = "";
  for (const p of lista) {
    const o = document.createElement("option");
    o.value = p.nome;
    dl.append(o);
  }
}

// O contador de caracteres. O servidor conta em RUNAS e nao em bytes
// (api.go), e o .length do JavaScript conta unidades UTF-16 - as duas
// contas so' divergem em emoji e afins, que gastam duas unidades aqui e uma
// runa la'. A diferenca e' a favor do jogador: o campo trava antes.
const campoMensagem = $("#form-chamado [name=mensagem]");
if (campoMensagem) {
  const conta = $("[data-conta-mensagem]");
  const atualiza = () => { conta.textContent = campoMensagem.value.length; };
  campoMensagem.oninput = atualiza;
  atualiza();
}

$("#form-chamado").onsubmit = e => {
  e.preventDefault();
  const f = e.target;
  comBotaoTravado(f, async () => {
    try {
      const d = await chama("/api/painel/chamado", {
        tipo: f.tipo.value,
        personagem: f.personagem.value.trim(),
        assunto: f.assunto.value.trim(),
        mensagem: f.mensagem.value.trim()
      });
      f.reset();
      if (campoMensagem) campoMensagem.oninput();
      f.classList.add("escondido");
      // O NUMERO E' O QUE O JOGADOR LEVA. Nao ha tela de leitura de chamado
      // ainda; sem o numero na frente dele, ele nao tem como cobrar depois.
      recado(f, "Chamado nº " + d.numero + " registrado. " + d.mensagem, "certo");
    } catch (err) {
      recado(f, err.message, "erro");
    }
  });
};

$("#form-senha").onsubmit = e => {
  e.preventDefault();
  const f = e.target;
  comBotaoTravado(f, async () => {
    try {
      await chama("/api/painel/senha", { atual: f.atual.value, nova: f.nova.value });
      f.reset();
      f.classList.add("escondido");
      recado(f, "Senha trocada.", "certo");
    } catch (err) {
      recado(f, err.message, "erro");
    }
  });
};

$("#form-pin").onsubmit = e => {
  e.preventDefault();
  const f = e.target;
  comBotaoTravado(f, async () => {
    try {
      const d = await chama("/api/painel/pin", { senha: f.senha.value });
      f.reset();
      f.classList.add("escondido");
      recado(f, d.mensagem, "certo");
    } catch (err) {
      recado(f, err.message, "erro");
    }
  });
};

$("#botao-sair").onclick = async () => {
  await chama("/api/sessao/sair");
  logado = false;
  aplicaPermissao(false);
  const voltar = $("#tela-download .voltar");
  if (voltar) voltar.dataset.ir = "inicio";
  vaiPara("inicio");
};

/* ---------- endereco do download ----------
 * O botao entrega o INSTALADOR, que tem 9 MB - e nao o jogo, que tem
 * 3,4 GB. Quem baixa os 3,4 GB e' o proprio instalador, direto do
 * bucket (cdn.filiponegrao.com.br), com retomada se a conexao cair.
 *
 * Nada disso passa pelo nosso servidor, e o motivo e' de tamanho: sao
 * 3,4 GB POR JOGADOR, que sairiam pela mesma placa de rede que atende o
 * map-server. Os patches incrementais, esses sim, ficam no /patch/ do
 * proprio servidor - sao pequenos e o Atualizador precisa de HTTP
 * simples. (Ate 2026-08-16 o cliente saia de uma pasta do Google Drive;
 * ver HISTORICO.md.)
 */
(async function download() {
  const botao = $("[data-download]");
  try {
    const d = await chama("/api/config", null, "GET");
    if (d.download) {
      botao.href = d.download;
      botao.target = "_blank";
      botao.rel = "noopener";
      return;
    }
  } catch (_) { /* cai no estado desligado abaixo */ }

  // Sem endereco configurado, o botao NAO leva a lugar nenhum - e diz
  // isso. Um botao que parece funcionar e nao funciona e' pior que um
  // botao desligado.
  botao.classList.add("fantasma");
  botao.style.pointerEvents = "none";
  botao.style.opacity = ".55";
  $(".rotulo", botao).textContent = "Em breve";
  $("[data-tamanho]").textContent = "o instalador esta sendo preparado";
})();

/* ---------- entrada ---------- */
// Se ja' ha' sessao valida, o painel e' a tela util; senao fica no inicio.
(async function inicia() {
  aplicaHash();
  try {
    const d = await chama("/api/painel", null, "GET");
    $("[data-nome]").textContent = d.usuario;
    $("[data-email]").textContent = d.email || "";
    entrouNaConta();
    aplicaPermissao(d.admin === true);
    if (!location.hash || location.hash === "#inicio") vaiPara("painel");
    // O aplicaHash de cima ja' desenhou a tela pelo endereco, mas a
    // permissao so' chegou agora: quem colou um #admin precisa ser mandado
    // de volta, e quem tem direito precisa da lista carregada.
    else if (location.hash === "#admin") vaiPara("admin");
  } catch (_) {
    // sem sessao: o inicio ja' esta' na tela
  }
})();

/* ==================================================================
 * PAINEL DE USUARIOS — so' para administrador (2026-09-10)
 *
 * Estreou depois de um jogador errar a senha algumas vezes e ficar sem
 * conseguir entrar. A tela responde DUAS perguntas que parecem uma so':
 *
 *   "essa conta esta' travada?"        -> a lista de contas
 *   "essa PESSOA chega ate' o login?"  -> a lista de bloqueios de endereco
 *
 * Desde 2026-09-06 (CLAUDE.md secao 4.23) quem erra a senha cai na PRIMEIRA:
 * sete erradas suspendem aquela conta por 15 minutos. Antes disso caia na
 * segunda, com o /24 inteiro junto - e por isso a lista de enderecos continua
 * aqui, agora so' para ban feito a mao: quando houver linha nela, ela barra
 * antes do login e nenhuma ficha de conta denuncia isso.
 *
 * O QUE A TELA TEM DE SEPARAR: castigo de gente e trava de maquina moram na
 * MESMA coluna (`unban_time`). Sem o rotulo de "travada sozinha", o operador
 * ve' "suspensa" na ficha de quem so' esqueceu a senha - e pune de novo.
 *
 * NADA AQUI E' TRAVA. Esconder o botao e desabilitar o que nao se pode
 * fazer e' cortesia com quem esta' olhando; quem manda e' o exigeAdmin do
 * admin.go, que confere o group_id no banco a cada requisicao.
 */

let adminPagina = 0;
let adminBusca = "";

/* ---------- pecinhas de DOM ----------
 * Tudo por textContent e nunca por innerHTML: e-mail e nome de conta sao
 * texto que outra pessoa escreveu, e esta tela e' vista por quem tem
 * permissao para tudo. */
function cria(tag, classe, texto) {
  const el = document.createElement(tag);
  if (classe) el.className = classe;
  if (texto !== undefined && texto !== null) el.textContent = texto;
  return el;
}

function selo(classe, texto) { return cria("span", "selo " + classe, texto); }

/* Data curta em horario de quem esta' olhando. O servidor manda RFC 3339
 * com fuso, entao a conversao e' do navegador e nao ha' o que combinar. */
function quando(iso) {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d)) return null;
  return d.toLocaleString("pt-BR", {
    day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit"
  });
}

function daquiAPouco(segundos) {
  if (segundos <= 0) return "vence a qualquer instante";
  if (segundos < 60) return "faltam " + segundos + "s";
  return "faltam " + Math.ceil(segundos / 60) + " min";
}

/* ---------- carga ---------- */
async function carregaAdmin() {
  const caixaContas = $("[data-lista-contas]");
  const caixaIPs = $("[data-lista-ips]");
  caixaContas.innerHTML = '<p class="miudo">Carregando…</p>';

  let d;
  try {
    const q = new URLSearchParams({ busca: adminBusca, pagina: adminPagina });
    d = await chama("/api/admin/contas?" + q, null, "GET");
  } catch (err) {
    caixaContas.innerHTML = "";
    caixaContas.append(paragrafo("miudo", err.message));
    return;
  }

  desenhaBloqueiosDeIP(caixaIPs, d.ip_bloqueios || []);

  caixaContas.innerHTML = "";
  const contas = d.contas || [];
  if (!contas.length) {
    caixaContas.append(paragrafo("miudo", adminBusca
      ? "Nenhuma conta encontrada para essa busca."
      : "Nenhuma conta ainda."));
  } else {
    for (const c of contas) caixaContas.append(fichaDeConta(c));
  }

  desenhaPaginacao(d);
}

function desenhaPaginacao(d) {
  const inicio = d.pagina * d.por_pagina;
  const fim = inicio + (d.contas || []).length;
  $("[data-resumo-contas]").textContent = d.total
    ? "Mostrando " + (inicio + 1) + "–" + fim + " de " + d.total + " conta(s)."
    : "";

  const barra = $("[data-paginacao]");
  const temMais = fim < d.total;
  const temMenos = d.pagina > 0;
  barra.classList.toggle("escondido", !temMais && !temMenos);
  $("[data-pagina-atual]").textContent = "página " + (d.pagina + 1);
  $$("[data-pagina]", barra).forEach(b => {
    b.disabled = b.dataset.pagina === "1" ? !temMais : !temMenos;
  });
}

/* ---------- bloqueios de IP ----------
 * Ver o texto do index.html: sete erros de senha do mesmo endereco em cinco
 * minutos e o login-server bloqueia a FAIXA por cinco minutos. Passa
 * sozinho; o botao existe para quando nao da' para esperar. */
function desenhaBloqueiosDeIP(caixa, lista) {
  caixa.innerHTML = "";
  if (!lista.length) {
    caixa.append(paragrafo("miudo",
      "Nenhum endereço bloqueado agora. Se um jogador diz que não entra, o problema é outro — procure a conta dele abaixo."));
    return;
  }
  for (const b of lista) caixa.append(linhaDeIP(b));
}

function linhaDeIP(b) {
  const linha = cria("div", "ip-bloqueio");

  const quem = cria("div");
  quem.append(cria("div", "faixa", b.faixa));
  const desde = quando(b.desde);
  quem.append(paragrafo("miudo",
    (b.motivo || "bloqueio automático") +
    (desde ? " · desde " + desde : "") +
    " · " + daquiAPouco(b.restam)));

  const botao = cria("button", "botao fantasma curto", "Liberar agora");
  botao.type = "button";
  botao.onclick = () => liberaIP(b.faixa, botao);

  linha.append(quem, botao);
  return linha;
}

async function liberaIP(faixa, botao) {
  const caixa = $("#tela-admin .cartao");
  botao.disabled = true;
  botao.textContent = "Liberando…";
  try {
    const d = await chama("/api/admin/ip/libera", { faixa: faixa });
    recado(caixa, d.mensagem, "certo");
    await carregaAdmin();
  } catch (err) {
    recado(caixa, err.message, "erro");
    botao.disabled = false;
    botao.textContent = "Liberar agora";
  }
}

/* ---------- a ficha de uma conta ---------- */
function fichaDeConta(c) {
  const ficha = cria("div", "conta situacao-" + c.situacao);

  const cabeca = cria("div", "cabeca");
  cabeca.append(cria("strong", null, c.usuario));
  cabeca.append(cria("span", "numero", "#" + c.id));
  cabeca.append(selo(c.situacao, rotuloDeSituacao(c.situacao)));
  if (c.online > 0) cabeca.append(selo("online", c.online + " no jogo"));
  if (c.admin) cabeca.append(selo("admin", "admin"));
  ficha.append(cabeca);

  const linhas = cria("div", "linhas");
  linhas.append(cria("p", null, c.situacao_texto));

  const identidade = [c.email || "sem e-mail"];
  identidade.push(c.personagens === 1 ? "1 personagem" : c.personagens + " personagens");
  if (c.grupo > 0) identidade.push("grupo " + c.grupo);
  linhas.append(cria("p", null, identidade.join(" · ")));

  const acesso = [];
  const ultimo = quando(c.ultimo_login);
  acesso.push(ultimo ? "último login " + ultimo : "nunca entrou");
  if (c.logins) acesso.push(c.logins + " login(s) no total");
  if (c.ultimo_ip) acesso.push("IP " + c.ultimo_ip);
  linhas.append(cria("p", null, acesso.join(" · ")));

  /* As tentativas erradas sao a pista que explica o relato mais comum
   * ("nao consigo entrar") sem que a conta tenha nada de errado. */
  if (c.falhas > 0) {
    const t = quando(c.ultima_tentativa);
    linhas.append(cria("p", null,
      c.falhas + " tentativa(s) recusada(s) nas últimas 24h" +
      (t ? " · a última em " + t : "") +
      (c.ip_tentado ? " · de " + c.ip_tentado : "")));
  }
  ficha.append(linhas);

  if (c.trava_auto) {
    ficha.append(cria("div", "alerta calmo",
      "Isso não é castigo de ninguém: foi a trava automática de senha errada, " +
      "e ela se solta sozinha no horário acima. Só use Reativar se ele não " +
      "puder esperar — e avise que errar de novo tranca outra vez."));
  }

  if (c.faixa_banida) {
    const alerta = cria("div", "alerta");
    alerta.append(document.createTextNode("O endereço desta conta está numa faixa bloqueada agora: "));
    alerta.append(cria("code", null, c.faixa_banida));
    alerta.append(document.createTextNode(
      ". É isso que impede a entrada — e não a conta. Libere a faixa na lista do topo."));
    ficha.append(alerta);
  } else if (c.barrado_por_ip) {
    ficha.append(cria("div", "alerta",
      "A última tentativa desta conta foi recusada por bloqueio de endereço. " +
      "O bloqueio já venceu — ela deve conseguir entrar agora."));
  }

  ficha.append(botoesDaConta(c, ficha));
  ficha.append(cria("div", "acao escondido"));
  return ficha;
}

function rotuloDeSituacao(s) {
  return { ok: "ativa", bloqueada: "bloqueada", suspensa: "suspensa",
           trava: "travada sozinha", expirada: "expirada",
           servidor: "servidor" }[s] || s;
}

function botoesDaConta(c, ficha) {
  const barra = cria("div", "botoes");

  if (c.situacao !== "ok" && c.situacao !== "servidor") {
    const liberar = cria("button", "botao curto", "Reativar");
    liberar.type = "button";
    liberar.onclick = () => acaoDeConta(c, ficha, "liberar", {}, liberar);
    barra.append(liberar);
  }

  if (c.pode_moderar) {
    if (c.situacao !== "suspensa") {
      const suspender = cria("button", "botao fantasma curto", "Suspender");
      suspender.type = "button";
      suspender.onclick = () => abreFormulario(c, ficha, "suspender");
      barra.append(suspender);
    }
    if (c.situacao !== "bloqueada") {
      const bloquear = cria("button", "botao fantasma curto perigo", "Bloquear");
      bloquear.type = "button";
      bloquear.onclick = () => abreFormulario(c, ficha, "bloquear");
      barra.append(bloquear);
    }
  }

  const historico = cria("button", "botao fantasma curto", "Histórico");
  historico.type = "button";
  historico.onclick = () => mostraHistorico(c, ficha);
  barra.append(historico);

  return barra;
}

/* ---------- o formulario de bloquear/suspender ----------
 * Abre DENTRO da ficha: o motivo que se escreve e' sobre aquela conta, e
 * poder reler a ficha enquanto se escreve e' metade da decisao.
 *
 * A senha e' pedida porque a acao mexe em ACESSO - a mesma regra que o
 * resto do painel ja' segue (api.go). Reativar nao pede: devolve acesso. */
function abreFormulario(c, ficha, acao) {
  const area = $(".acao", ficha);
  area.innerHTML = "";
  area.classList.remove("escondido");

  const bloqueio = acao === "bloquear";
  area.append(paragrafo("nota", bloqueio
    ? "O bloqueio não tem prazo: vale até alguém reativar a conta aqui. No cliente o jogador vê a mensagem de bloqueio pela equipe do servidor."
    : "A suspensão vence sozinha na data escolhida, e o cliente mostra a data ao jogador."));

  // A classe "par" so' entra quando ha' DOIS campos para dividir a linha.
  // No bloqueio ha' um so' (a senha), e uma grade de duas colunas o
  // deixaria com metade da largura e um vao vazio do lado.
  const par = cria("div", bloqueio ? null : "par");

  if (!bloqueio) {
    const rotulo = cria("label", null, "Por quanto tempo");
    const select = document.createElement("select");
    select.name = "minutos";
    [[30, "30 minutos"], [120, "2 horas"], [720, "12 horas"], [1440, "1 dia"],
     [4320, "3 dias"], [10080, "7 dias"], [43200, "30 dias"]].forEach(([v, t]) => {
      const o = document.createElement("option");
      o.value = v; o.textContent = t;
      select.append(o);
    });
    select.value = "1440";
    rotulo.append(select);
    par.append(rotulo);
  }

  const senhaRotulo = cria("label", null, "Confirme a sua senha");
  const senha = document.createElement("input");
  senha.type = "password";
  senha.name = "senha";
  senha.autocomplete = "current-password";
  senhaRotulo.append(senha);
  par.append(senhaRotulo);
  area.append(par);

  const motivoRotulo = cria("label", null, "Motivo");
  const motivo = document.createElement("input");
  motivo.name = "motivo";
  motivo.maxLength = 255;
  motivo.placeholder = "Fica registrado, e é o que explica a decisão depois";
  motivoRotulo.append(motivo);
  area.append(motivoRotulo);

  const barra = cria("div", "botoes");
  const confirmar = cria("button", "botao curto" + (bloqueio ? " perigo" : ""),
    bloqueio ? "Bloquear a conta" : "Suspender a conta");
  confirmar.type = "button";
  confirmar.onclick = () => acaoDeConta(c, ficha, acao, {
    senha: senha.value,
    motivo: motivo.value.trim(),
    minutos: bloqueio ? 0 : Number($("select[name=minutos]", area).value)
  }, confirmar);

  const cancelar = cria("button", "botao fantasma curto", "Cancelar");
  cancelar.type = "button";
  cancelar.onclick = () => { area.innerHTML = ""; area.classList.add("escondido"); };

  barra.append(confirmar, cancelar);
  area.append(barra);
  motivo.focus();
}

async function acaoDeConta(c, ficha, acao, extra, botao) {
  const caixa = $("#tela-admin .cartao");
  const texto = botao.textContent;
  botao.disabled = true;
  botao.textContent = "Aguarde…";
  try {
    const d = await chama("/api/admin/conta/acao",
      Object.assign({ conta: c.id, acao: acao }, extra));
    recado(caixa, d.mensagem, "certo");
    // Recarrega em vez de acertar a ficha na mao: o que aparece na tela
    // passa a ser o que o banco tem, e nao o que o JavaScript supos.
    await carregaAdmin();
    caixa.scrollIntoView({ block: "start", behavior: "smooth" });
  } catch (err) {
    recado(caixa, err.message, "erro");
    botao.disabled = false;
    botao.textContent = texto;
  }
}

/* ---------- historico de moderacao ----------
 * E' onde o motivo escrito num bloqueio volta a ser lido. Sem esta tela ele
 * seria um campo que so' se escreve. */
async function mostraHistorico(c, ficha) {
  const area = $(".acao", ficha);
  area.innerHTML = "";
  area.classList.remove("escondido");
  area.append(paragrafo("miudo", "Carregando…"));

  let d;
  try {
    d = await chama("/api/admin/conta/historico?conta=" + c.id, null, "GET");
  } catch (err) {
    area.innerHTML = "";
    area.append(paragrafo("miudo", err.message));
    return;
  }

  area.innerHTML = "";
  const lista = d.historico || [];
  if (!lista.length) {
    area.append(paragrafo("miudo", d.indisponivel
      ? "O registro de moderação ainda não está disponível neste servidor."
      : "Nada foi feito nesta conta pelo painel."));
  } else {
    const caixa = cria("div", "historico");
    for (const m of lista) {
      const linha = cria("div", "linha");
      linha.append(cria("b", null, m.acao));
      linha.append(document.createTextNode(
        " · " + (quando(m.quando) || "") + " · por " + m.admin));
      if (m.detalhe) linha.append(document.createTextNode(" · " + m.detalhe));
      if (m.motivo) {
        linha.append(document.createElement("br"));
        linha.append(cria("span", "motivo", "“" + m.motivo + "”"));
      }
      caixa.append(linha);
    }
    area.append(caixa);
  }

  const fechar = cria("button", "botao fantasma curto", "Fechar");
  fechar.type = "button";
  fechar.onclick = () => { area.innerHTML = ""; area.classList.add("escondido"); };
  area.append(fechar);
}

/* ---------- busca e paginacao ----------
 * A busca espera o dedo parar: cada tecla dispararia uma consulta que varre
 * a `login` e, junto com ela, o `loginlog`. */
let temporizadorDaBusca;
$("#form-busca-contas").onsubmit = e => e.preventDefault();
$("#form-busca-contas [name=busca]").oninput = e => {
  clearTimeout(temporizadorDaBusca);
  const valor = e.target.value.trim();
  temporizadorDaBusca = setTimeout(() => {
    adminBusca = valor;
    adminPagina = 0;
    carregaAdmin();
  }, 350);
};

$$("[data-pagina]").forEach(b => {
  b.onclick = () => {
    adminPagina = Math.max(0, adminPagina + Number(b.dataset.pagina));
    carregaAdmin();
    $("#tela-admin .cartao").scrollIntoView({ block: "start", behavior: "smooth" });
  };
});
