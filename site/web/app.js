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

/* ---------- navegacao entre telas ---------- */
function vaiPara(nome) {
  // Quem ja entrou nao tem o que fazer no formulario de login.
  if (nome === "conta" && logado) nome = "painel";
  $$(".tela").forEach(t => t.classList.toggle("ativa", t.id === "tela-" + nome));
  // O hash deixa o botao voltar do navegador funcionar, que e' o primeiro
  // reflexo de quem se perde numa tela.
  if (location.hash !== "#" + nome) history.pushState({}, "", "#" + nome);
  window.scrollTo(0, 0);
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
  } catch (_) {
    logado = false;
    vaiPara("conta");
  }
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
    if (!location.hash || location.hash === "#inicio") vaiPara("painel");
  } catch (_) {
    // sem sessao: o inicio ja' esta' na tela
  }
})();
