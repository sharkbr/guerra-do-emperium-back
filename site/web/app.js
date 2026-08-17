/* Guerra do Emperium — o pouco de JavaScript que o site precisa.
 *
 * Sem framework de proposito: sao quatro telas e seis chamadas. Uma
 * dependencia aqui custaria mais para manter do que o arquivo inteiro.
 */
"use strict";

const $  = (s, raiz = document) => raiz.querySelector(s);
const $$ = (s, raiz = document) => [...raiz.querySelectorAll(s)];

/* ---------- navegacao entre telas ---------- */
function vaiPara(nome) {
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
  vaiPara("painel");
  carregaPainel();
}

async function carregaPainel() {
  try {
    const d = await chama("/api/painel", null, "GET");
    $("[data-nome]").textContent = d.usuario;
    $("[data-email]").textContent = d.email || "";
  } catch (_) {
    vaiPara("conta");
  }
}

$$("[data-abre]").forEach(b => {
  b.onclick = () => {
    const alvo = $("#form-" + b.dataset.abre);
    const abrindo = alvo.classList.contains("escondido");
    $$(".dobra").forEach(d => d.classList.add("escondido"));
    alvo.classList.toggle("escondido", !abrindo);
  };
});

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
    if (!location.hash || location.hash === "#inicio") vaiPara("painel");
  } catch (_) {
    // sem sessao: o inicio ja' esta' na tela
  }
})();
