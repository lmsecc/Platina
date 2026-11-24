/* ============ CONFIGURAÇÃO ============ */
// WhatsApp da empresa, com código do país e DDD, só números. Ex.: "5521999999999"
// Pedidos e agendamentos são enviados para esse número.
const WHATSAPP = "";

/* ============ DADOS: produtos e serviços ============ */
// baixo: true mostra o selo "Poucas unidades" (estoque abaixo do mínimo)
const produtos = [
  { id: 1, nome: "Extintor PQS ABC 4 kg", cat: "extintores", preco: 129.90, emoji: "🧯", baixo: false, desc: "Pó químico para fogo em madeira, líquidos inflamáveis e equipamentos elétricos (classes A, B e C)." },
  { id: 2, nome: "Extintor PQS ABC 6 kg", cat: "extintores", preco: 169.90, emoji: "🧯", baixo: true,  desc: "Pó químico para fogo em madeira, líquidos inflamáveis e equipamentos elétricos (classes A, B e C)." },
  { id: 3, nome: "Extintor CO2 6 kg", cat: "extintores", preco: 489.00, emoji: "🧯", baixo: true,  desc: "Gás carbônico, não deixa resíduo. Para líquidos inflamáveis e equipamentos elétricos (classes B e C)." },
  { id: 4, nome: "Extintor Água 10 L", cat: "extintores", preco: 139.90, emoji: "🧯", baixo: false, desc: "Para fogo em madeira, papel e tecido (classe A). Não use em equipamentos elétricos." },
  { id: 5, nome: "Extintor Espuma 9 L", cat: "extintores", preco: 219.90, emoji: "🧯", baixo: true,  desc: "Para fogo em madeira, papel e líquidos inflamáveis (classes A e B)." },
  { id: 6, nome: "Recarga", cat: "servicos", preco: 59.90, emoji: "🔧", baixo: false, desc: "Recarga do extintor com etiqueta e selo atualizados." },
  { id: 7, nome: "Teste hidrostático", cat: "servicos", preco: 89.90, emoji: "🔧", baixo: false, desc: "Teste de resistência do cilindro, necessário a cada 5 anos." },
  { id: 8, nome: "Manutenção", cat: "servicos", preco: 45.00, emoji: "🔧", baixo: false, desc: "Revisão de manômetro, válvula, mangueira e lacre." }
];

let carrinho = {};  // formato: { idDoProduto: quantidade }
const $ = (id) => document.getElementById(id); // atalho
const moeda = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const esc = (t) => String(t).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const semAcento = (t) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const hojeLocal = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().split("T")[0];

function aviso(elemento, texto, ok) {
  elemento.className = "msg " + (ok ? "ok" : "erro");
  elemento.textContent = texto;
}

// Abre o WhatsApp com o texto pronto. Devolve false se o número não foi configurado.
function enviarPeloWhatsApp(texto) {
  if (!WHATSAPP) return false;
  window.open("https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(texto), "_blank", "noopener");
  return true;
}
const SEM_WHATSAPP = "Falta configurar o WhatsApp da empresa (constante WHATSAPP, no começo do script.js).";

/* ============ 1. MENU MOBILE ============ */
$("menuBtn").addEventListener("click", () => $("menu").classList.toggle("open"));
$("menu").addEventListener("click", () => $("menu").classList.remove("open"));
$("topBtn").addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

/* ============ 2. CATÁLOGO COM FILTRO ============ */
function mostrarProdutos(cat) {
  const lista = cat === "todos" ? produtos : produtos.filter(p => p.cat === cat);
  $("productGrid").innerHTML = lista.map(p => `
    <article class="product">
      <div class="emoji">${p.emoji}</div>
      <h3>${p.nome}</h3>
      <p class="desc">${p.desc}</p>
      ${p.baixo ? '<span class="badge">Poucas unidades</span>' : ""}
      <div class="price">${moeda(p.preco)}</div>
      <button class="btn" data-add="${p.id}">Adicionar</button>
    </article>`).join("");
}

$("filters").addEventListener("click", (e) => {
  if (!e.target.dataset.cat) return;
  document.querySelectorAll(".filter").forEach(b => b.classList.remove("active"));
  e.target.classList.add("active");
  mostrarProdutos(e.target.dataset.cat);
});

/* ============ 3. CARRINHO ============ */
$("productGrid").addEventListener("click", (e) => {
  const id = e.target.dataset.add;
  if (!id) return;
  carrinho[id] = Math.min((carrinho[id] || 0) + 1, 999);
  $("cartMsg").textContent = "";
  desenharCarrinho();
});

$("cartItems").addEventListener("click", (e) => {
  const { id, op } = e.target.dataset;
  if (!id) return;
  carrinho[id] += op === "mais" ? 1 : -1;
  if (carrinho[id] <= 0) delete carrinho[id];
  desenharCarrinho();
});

function desenharCarrinho() {
  const ids = Object.keys(carrinho);
  let total = 0;
  $("cartItems").innerHTML = ids.length ? ids.map(id => {
    const p = produtos.find(x => x.id == id);
    const subtotal = p.preco * carrinho[id];
    total += subtotal;
    return `<div class="cart-row"><span>${p.emoji} ${p.nome}</span>
      <span class="qty"><button data-id="${id}" data-op="menos" aria-label="Diminuir">−</button>
      <b>${carrinho[id]}</b>
      <button data-id="${id}" data-op="mais" aria-label="Aumentar">+</button></span>
      <span class="cart-sub">${moeda(subtotal)}</span></div>`;
  }).join("") : '<p class="empty">Seu pedido está vazio.</p>';
  $("cartTotal").textContent = moeda(total);
}

$("isCompany").addEventListener("change", (e) => { $("companyInfo").hidden = !e.target.checked; });

$("clearBtn").addEventListener("click", () => {
  carrinho = {};
  desenharCarrinho();
  $("cartMsg").textContent = "";
});

$("checkoutBtn").addEventListener("click", () => {
  const ids = Object.keys(carrinho);
  const nome = $("cartName").value.trim();
  const tel = $("cartPhone").value.replace(/\D/g, "");
  const empresa = $("isCompany").checked;
  const cnpj = $("companyInfo").value.trim();

  const problema = !ids.length ? "Adicione ao menos um item."
    : nome.length < 2 ? "Informe seu nome."
    : (tel.length < 10 || tel.length > 11) ? "Informe o telefone com DDD."
    : (empresa && !cnpj) ? "Informe o CNPJ e a razão social."
    : "";
  if (problema) { aviso($("cartMsg"), problema, false); return; }

  let total = 0;
  const linhas = ids.map(id => {
    const p = produtos.find(x => x.id == id);
    total += p.preco * carrinho[id];
    return `- ${carrinho[id]} x ${p.nome} (${moeda(p.preco * carrinho[id])})`;
  });
  const texto = `Pedido - Platina Extintores\nCliente: ${nome} (${$("cartPhone").value})\n`
    + (empresa ? `Nota fiscal: ${cnpj}\n` : "") + linhas.join("\n") + `\nTotal: ${moeda(total)}`;

  if (!enviarPeloWhatsApp(texto)) { aviso($("cartMsg"), SEM_WHATSAPP, false); return; }
  aviso($("cartMsg"), "Abrimos o WhatsApp com o seu pedido. Toque em enviar para concluir.", true);
  carrinho = {};
  desenharCarrinho();
});

/* ============ 4. CALCULADORA DE EXTINTORES ============ */
$("calcBtn").addEventListener("click", () => {
  const area = parseFloat($("calcArea").value);
  const m2PorExtintor = parseFloat($("calcRisk").value);   // vem do tipo de local (estimativa)
  if (!area || area < 1) {
    $("calcResult").textContent = "Informe a área do local em m².";
    return;
  }
  const qtd = Math.max(1, Math.ceil(area / m2PorExtintor));
  const maisBarato = Math.min(...produtos.filter(p => p.cat === "extintores").map(p => p.preco));
  $("calcResult").innerHTML = `🧯 Extintores: <strong>${qtd}</strong><br>
    💰 Investimento a partir de: <strong>${moeda(qtd * maisBarato)}</strong><br>
    <small>Estimativa. O número exato segue as regras do Corpo de Bombeiros do seu estado.</small><br>
    <button class="btn" id="useCalc">Usar no agendamento</button>`;
  $("useCalc").addEventListener("click", () => {
    $("evQty").value = qtd;
    $("agendar").scrollIntoView({ behavior: "smooth" });
  });
});

/* ============ 5. AGENDAMENTO COM VALIDAÇÃO ============ */
let eventos = [];
try { eventos = JSON.parse(localStorage.getItem("agendamentosPlatina")) || []; } catch (e) { eventos = []; }

function salvarEventos() {
  try { localStorage.setItem("agendamentosPlatina", JSON.stringify(eventos)); } catch (e) {}
}

// Data mínima: hoje (no horário do cliente)
$("evDate").min = hojeLocal();

// Serviços para marcar no formulário
$("evServices").innerHTML = produtos.filter(p => p.cat === "servicos").map(s =>
  `<label class="check"><input type="checkbox" name="item" value="${s.nome}"> ${s.nome}</label>`).join("");

function erro(campo, texto) {
  campo.classList.toggle("invalid", !!texto);
  campo.parentElement.querySelector(".err").textContent = texto;
  return !texto;
}

$("eventForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const nome = $("evName"), tel = $("evPhone"), data = $("evDate"), qtd = $("evQty"), local = $("evPlace");
  const servicos = [...document.querySelectorAll("input[name=item]:checked")].map(i => i.value);

  let ok = true;
  ok = erro(nome, nome.value.trim().length < 3 ? "Digite seu nome completo." : "") && ok;
  ok = erro(tel, tel.value.replace(/\D/g, "").length < 10 || tel.value.replace(/\D/g, "").length > 11 ? "Telefone inválido (use DDD)." : "") && ok;
  ok = erro(data, !data.value || data.value < data.min ? "Escolha uma data a partir de hoje." : "") && ok;
  ok = erro(qtd, !(parseInt(qtd.value) > 0) ? "Informe a quantidade de extintores." : "") && ok;
  ok = erro(local, local.value.trim().length < 3 ? "Informe a empresa ou o endereço." : "") && ok;
  $("itemsErr").textContent = servicos.length ? "" : "Escolha ao menos um serviço.";
  if (!servicos.length) ok = false;
  if (!ok) { aviso($("formMsg"), "Corrija os campos destacados.", false); return; }

  const dataBR = data.value.split("-").reverse().join("/");
  const texto = `Agendamento - Platina Extintores\nCliente: ${nome.value.trim()} (${tel.value})\nData: ${dataBR}\n`
    + `Local: ${local.value.trim()}\nExtintores: ${qtd.value}\nServiços: ${servicos.join(", ")}`;

  if (!enviarPeloWhatsApp(texto)) { aviso($("formMsg"), SEM_WHATSAPP, false); return; }

  eventos.push({ id: Date.now(), data: data.value, qtd: qtd.value, local: local.value.trim(), servicos });
  salvarEventos();
  aviso($("formMsg"), "Abrimos o WhatsApp com o seu agendamento. Toque em enviar para confirmar.", true);
  e.target.reset();
  desenharEventos();
});

function desenharEventos() {
  $("eventList").innerHTML = eventos.length ? eventos.map(ev => `
    <li><span><strong>${ev.data.split("-").reverse().join("/")}</strong> — ${esc(ev.local)}<br>
    ${esc(ev.qtd)} extintor(es) · ${ev.servicos.map(esc).join(", ")}</span>
    <button data-del="${ev.id}" title="Remover da lista" aria-label="Remover da lista">🗑️</button></li>`).join("")
    : '<li class="empty">Nenhum agendamento ainda.</li>';
}

$("eventList").addEventListener("click", (e) => {
  const id = e.target.dataset.del;
  if (!id) return;
  eventos = eventos.filter(ev => ev.id != id);
  salvarEventos();
  desenharEventos();
});

/* ============ 6. CHATBOT ============ */
// Cada item: palavras-chave (sem acento) e a resposta. A primeira que combinar responde.
// "exata: true" exige a palavra inteira (evita "oi" dentro de "oito"). r pode ser texto ou função.
const respostas = [
  { exata: true, chaves: ["oi", "ola", "bom dia", "boa tarde", "boa noite"],
    r: "Olá! Eu sou o assistente da Platina Extintores 🧯 Posso ajudar com preços, estoque, pagamento, prazos de recarga e agendamento." },

  { chaves: ["estoque", "disponivel", "disponibilidade", "acabando", "quantos", "quantas"],
    r: () => {
      const poucos = produtos.filter(p => p.baixo).map(p => p.nome);
      return "Trabalhamos com extintores PQS, CO2, água e espuma."
        + (poucos.length ? "\nPoucas unidades agora: " + poucos.join(", ") + ". Para quantidades grandes, fale com a gente antes de pedir." : "\nTodos os itens estão disponíveis.");
    } },

  { chaves: ["preco", "valor", "quanto", "custa", "tabela"],
    r: () => "Tabela de preços:\n" + produtos.map(p => `- ${p.nome}: ${moeda(p.preco)}`).join("\n") + "\nUse a calculadora para estimar quantos extintores você precisa." },

  { chaves: ["pagamento", "pagar", "pix", "cartao", "boleto", "parcela"],
    r: "Formas de pagamento:\n- Pix: 5% de desconto à vista.\n- Cartão de crédito: em até 3x sem juros.\n- Boleto: 28 dias, para clientes com cadastro aprovado." },

  { chaves: ["nota", "fiscal", "cnpj"],
    r: "A nota fiscal é emitida no mesmo dia da entrega ou do serviço e enviada por e-mail. Para empresa, marque \"Nota fiscal para empresa\" no pedido e informe o CNPJ." },

  { chaves: ["hidrostatico"],
    r: "O teste hidrostático verifica se o cilindro aguenta a pressão sem vazar ou deformar. Deve ser feito a cada 5 anos. Se o cilindro reprovar, ele precisa ser trocado." },

  { chaves: ["selo", "inmetro", "norma", "abnt", "certificado", "laudo"],
    r: "O selo do Inmetro mostra que o extintor foi fabricado ou recarregado dentro das regras. Confira se está inteiro, legível e dentro do prazo. A norma de inspeção, manutenção e recarga é a ABNT NBR 12962." },

  { chaves: ["recarga", "recarregar", "prazo", "validade", "vencido", "vence"],
    r: "Prazos principais:\n- Inspeção: todo mês (lacre, manômetro e mangueira).\n- Recarga: a cada 12 meses, ou logo após qualquer uso.\n- Teste hidrostático: a cada 5 anos.\nA validade fica na etiqueta presa ao extintor." },

  { chaves: ["inspecao", "inspecionar", "manometro", "lacre", "defeito"],
    r: "Checagem mensal: ponteiro do manômetro na faixa verde, lacre intacto, mangueira e bico sem rachaduras, cilindro sem ferrugem ou amassados e selo dentro do prazo. Se algo falhar, peça uma manutenção." },

  { chaves: ["qual extintor", "tipo de extintor", "tipos de extintor", "classe", "incendio"],
    r: "Resumo:\n- PQS ABC: madeira, líquidos inflamáveis e elétricos.\n- CO2: elétricos e líquidos inflamáveis.\n- Água: só madeira, papel e tecido.\n- Espuma: madeira, papel e líquidos inflamáveis.\nNa dúvida, use a calculadora ou agende uma visita." },

  { chaves: ["agendar", "agendamento", "visita", "servico", "manutencao"],
    r: "Para agendar, preencha o formulário em \"Agendar serviço\": data, quantidade de extintores, local e o serviço que você precisa." },

  { chaves: ["horario", "aberto", "funciona", "endereco", "telefone", "contato"],
    r: "Endereço, telefone e horário de atendimento estão no rodapé do site." },

  { exata: true, chaves: ["obrigado", "obrigada", "valeu"],
    r: "Por nada! Estamos aqui para ajudar 🧯" }
];

function addMsg(texto, tipo) {
  const d = document.createElement("div");
  d.className = "bubble " + tipo;
  d.textContent = texto;
  $("chatMsgs").appendChild(d);
  $("chatMsgs").scrollTop = $("chatMsgs").scrollHeight;
}

function acha(t) {
  return respostas.find(item => item.chaves.some(c => new RegExp("\\b" + c + (item.exata ? "\\b" : "")).test(t)));
}

function responder(texto) {
  addMsg(texto, "eu");
  const achou = acha(semAcento(texto));
  const resposta = achou ? (typeof achou.r === "function" ? achou.r() : achou.r)
    : "Não entendi bem 😅 Pergunte sobre preços, estoque, pagamento, prazos de recarga ou agendamento.";
  setTimeout(() => addMsg(resposta, "bot"), 500);
}

$("chatToggle").addEventListener("click", () => {
  $("chatBox").hidden = !$("chatBox").hidden;
  if (!$("chatMsgs").children.length) addMsg("Olá! Eu sou o assistente da Platina Extintores. Como posso ajudar? 🧯", "bot");
});
$("chatClose").addEventListener("click", () => { $("chatBox").hidden = true; });
$("chatForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const v = $("chatInput").value.trim();
  if (!v) return;
  responder(v);
  $("chatInput").value = "";
});
$("quick").addEventListener("click", (e) => { if (e.target.tagName === "BUTTON") responder(e.target.textContent); });

/* ============ INICIALIZAÇÃO ============ */
mostrarProdutos("todos");
desenharCarrinho();
desenharEventos();
