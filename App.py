"""
Platina Extintores - Chatbot por setores (arquivo único)

Como rodar:
    pip install flask
    python appy.py
Depois abra http://localhost:5000

O arquivo tem 6 partes, nesta ordem:
  1. DADOS         -> preços e estoque de exemplo (troque pelos reais)
  2. SETOR QUALIDADE
  3. SETOR ESTOQUE
  4. SETOR FINANCEIRO
  5. CHATBOT       -> escolhe o setor e devolve a resposta
  6. SITE E API    -> tela do chat e rotas
"""
import re
import unicodedata
from flask import Flask, jsonify, request, Response

# =====================================================================
# 1. DADOS (exemplos - troque pelos valores reais da empresa)
# =====================================================================
PRODUTOS = [
    {"nome": "Extintor PQS ABC 4 kg", "chaves": ["pqs", "4kg"], "estoque": 35, "minimo": 20, "preco": 129.90},
    {"nome": "Extintor PQS ABC 6 kg", "chaves": ["pqs", "6kg"], "estoque": 12, "minimo": 15, "preco": 169.90},
    {"nome": "Extintor CO2 6 kg", "chaves": ["co2", "6kg"], "estoque": 8, "minimo": 10, "preco": 489.00},
    {"nome": "Extintor Água 10 L", "chaves": ["agua", "10l"], "estoque": 22, "minimo": 10, "preco": 139.90},
    {"nome": "Extintor Espuma 9 L", "chaves": ["espuma", "9l"], "estoque": 4, "minimo": 8, "preco": 219.90},
]

SERVICOS = {"Recarga": 59.90, "Teste hidrostático": 89.90, "Manutenção": 45.00}


def reais(valor):
    """Escreve o valor no formato brasileiro: R$ 1.234,50"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def normalizar_medidas(texto):
    """Troca '6 kg' por '6kg' e 'litros' por 'l' para facilitar a busca."""
    texto = texto.replace("litros", "l").replace("litro", "l")
    return re.sub(r"(\d)\s+(kg|l)\b", r"\1\2", texto)


def achar_produto(texto):
    texto = normalizar_medidas(texto)
    for p in PRODUTOS:
        if all(chave in texto for chave in p["chaves"]):
            return p
    return None


# =====================================================================
# 2. SETOR QUALIDADE - prazos, selo, norma e inspeção
# =====================================================================
def qualidade(texto):
    if "hidrostatico" in texto:
        return ("O teste hidrostático verifica se o cilindro aguenta a pressão sem vazar ou deformar.\n"
                "Ele deve ser feito a cada 5 anos. Se o cilindro reprovar, ele precisa ser trocado.")
    if "selo" in texto or "inmetro" in texto:
        return ("O selo do Inmetro mostra que o extintor foi fabricado ou recarregado dentro das regras.\n"
                "Confira se o selo está inteiro, legível e dentro do prazo. Sem selo, o extintor não vale.")
    if any(p in texto for p in ["recarga", "prazo", "validade", "vencido", "vence"]):
        return ("Prazos principais:\n"
                "- Inspeção: todo mês, olhando lacre, manômetro e mangueira.\n"
                "- Recarga: a cada 12 meses (ou logo após qualquer uso).\n"
                "- Teste hidrostático: a cada 5 anos.\n"
                "A data de validade fica na etiqueta presa ao extintor.")
    if any(p in texto for p in ["inspecao", "inspecionar", "manometro", "lacre", "bom", "defeito"]):
        return ("Faça esta checagem rápida todo mês:\n"
                "1. O ponteiro do manômetro está na faixa verde?\n"
                "2. O lacre está intacto?\n"
                "3. A mangueira e o bico estão sem rachaduras ou entupimento?\n"
                "4. O cilindro está sem ferrugem ou amassados?\n"
                "5. O selo e a etiqueta estão dentro do prazo?\n"
                "Se alguma resposta for não, chame a manutenção.")
    if any(p in texto for p in ["norma", "abnt", "certificado", "laudo"]):
        return ("A norma que orienta inspeção, manutenção e recarga de extintores é a ABNT NBR 12962.\n"
                "Depois do serviço, a empresa deve entregar a etiqueta e o selo atualizados.")
    return ("Posso ajudar com: prazo de recarga, teste hidrostático, selo do Inmetro, "
            "inspeção mensal e normas. Qual desses você quer saber?")


# =====================================================================
# 3. SETOR ESTOQUE - quantidades e itens acabando
# =====================================================================
def _situacao(p):
    return "BAIXO - repor" if p["estoque"] < p["minimo"] else "ok"


def _linha_estoque(p):
    return f"- {p['nome']}: {p['estoque']} un. (mínimo {p['minimo']}) - {_situacao(p)}"


def estoque(texto):
    produto = achar_produto(texto)
    if produto:
        return (f"{produto['nome']}\nEm estoque: {produto['estoque']} un.\n"
                f"Estoque mínimo: {produto['minimo']} un.\nSituação: {_situacao(produto)}")

    if any(p in texto for p in ["acabando", "baixo", "reposicao", "repor", "falta"]):
        baixos = [p for p in PRODUTOS if p["estoque"] < p["minimo"]]
        if not baixos:
            return "Nenhum item está abaixo do estoque mínimo. Tudo certo!"
        return "Itens abaixo do mínimo (precisam de reposição):\n" + "\n".join(_linha_estoque(p) for p in baixos)

    if any(p in texto for p in ["todo", "todos", "lista", "estoque", "tudo"]):
        return "Estoque atual:\n" + "\n".join(_linha_estoque(p) for p in PRODUTOS)

    return ("Me diga o extintor que você quer consultar (ex.: 'PQS 6 kg' ou 'CO2 6 kg'), "
            "ou peça 'ver todo o estoque' ou 'o que está acabando'.")


# =====================================================================
# 4. SETOR FINANCEIRO - preços, orçamento, pagamento e nota fiscal
# =====================================================================
def financeiro(texto):
    texto = normalizar_medidas(texto)
    produto = achar_produto(texto)

    if produto:
        numeros = re.findall(r"(?<![\w])\d+(?![\w])", texto)  # número solto = quantidade
        qtd = int(numeros[0]) if numeros else None
        if qtd or "orcamento" in texto:
            qtd = qtd or 1
            return (f"Orçamento:\n{qtd} x {produto['nome']} a {reais(produto['preco'])}\n"
                    f"Total: {reais(qtd * produto['preco'])}\n"
                    "Valores de exemplo. Peça confirmação ao financeiro.")
        return f"{produto['nome']}: {reais(produto['preco'])} por unidade."

    if "orcamento" in texto:
        return "Para fazer o orçamento, diga o extintor e a quantidade. Exemplo: 'orçamento de 5 PQS 6 kg'."

    if any(p in texto for p in ["pagamento", "pagar", "boleto", "pix", "cartao", "parcela"]):
        return ("Formas de pagamento:\n"
                "- Pix: 5% de desconto à vista.\n"
                "- Cartão de crédito: em até 3x sem juros.\n"
                "- Boleto: 28 dias, para clientes com cadastro aprovado.")

    if "nota" in texto or "fiscal" in texto:
        return ("A nota fiscal é emitida no mesmo dia da entrega ou do serviço e enviada por e-mail.\n"
                "Se não recebeu, peça a segunda via ao financeiro informando o CNPJ.")

    if any(p in texto for p in ["preco", "valor", "tabela", "custa", "quanto"]):
        itens = [f"- {p['nome']}: {reais(p['preco'])}" for p in PRODUTOS]
        servicos = [f"- {nome}: {reais(v)}" for nome, v in SERVICOS.items()]
        return "Tabela de preços:\n" + "\n".join(itens) + "\n\nServiços:\n" + "\n".join(servicos)

    return "Posso ajudar com preços, orçamento, formas de pagamento e nota fiscal. O que você precisa?"


# =====================================================================
# 5. CHATBOT - escolhe o setor e devolve a resposta
# =====================================================================
SETORES = {
    "qualidade": {
        "nome": "Qualidade",
        "descricao": "Prazos, selos, normas e inspeção",
        "boas_vindas": "Setor de Qualidade. Posso explicar prazos de recarga, teste hidrostático, selo do Inmetro e como inspecionar um extintor.",
        "sugestoes": ["Qual o prazo de recarga?", "O que é teste hidrostático?", "Como ver se o extintor está bom?"],
        "palavras": ["qualidade", "inspecao", "inspecionar", "selo", "inmetro", "norma", "abnt", "validade",
                     "vencido", "vence", "prazo", "recarga", "hidrostatico", "manometro", "lacre",
                     "defeito", "certificado", "laudo"],
        "responder": qualidade,
    },
    "estoque": {
        "nome": "Estoque",
        "descricao": "Quantidades e itens acabando",
        "boas_vindas": "Setor de Estoque. Posso dizer quantas unidades temos de cada extintor e quais itens estão acabando.",
        "sugestoes": ["Ver todo o estoque", "O que está acabando?", "Quantos PQS 6 kg temos?"],
        "palavras": ["estoque", "quantos", "quantas", "unidades", "disponivel", "temos", "acabando",
                     "baixo", "reposicao", "repor", "saldo", "falta"],
        "responder": estoque,
    },
    "financeiro": {
        "nome": "Financeiro",
        "descricao": "Preços, orçamento e pagamento",
        "boas_vindas": "Setor Financeiro. Posso informar preços, fazer um orçamento simples e explicar formas de pagamento e nota fiscal.",
        "sugestoes": ["Tabela de preços", "Orçamento de 5 PQS 6 kg", "Formas de pagamento"],
        "palavras": ["financeiro", "preco", "valor", "custa", "quanto", "orcamento", "pagamento", "pagar",
                     "boleto", "pix", "cartao", "parcela", "nota", "fiscal", "desconto", "fatura", "cobranca"],
        "responder": financeiro,
    },
}

SAUDACAO = ("Olá! Eu sou o assistente da Platina Extintores. "
            "Escolha um setor ao lado ou escreva sua pergunta que eu encaminho.")


def limpar(texto):
    """Deixa tudo em minúsculo e sem acento para facilitar a busca."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def descobrir_setor(texto):
    pontos = {id_: sum(p in texto for p in s["palavras"]) for id_, s in SETORES.items()}
    melhor = max(pontos, key=pontos.get)
    return melhor if pontos[melhor] > 0 else None


def responder(mensagem, setor=None):
    texto = limpar(mensagem or "")
    if not texto:
        return {"setor": setor, "resposta": "Escreva sua pergunta para eu poder ajudar."}
    if texto in ("oi", "ola", "bom dia", "boa tarde", "boa noite"):
        return {"setor": setor, "resposta": SAUDACAO}

    # Se a frase é claramente de outro setor, troca. Senão, mantém o escolhido.
    escolhido = descobrir_setor(texto) or (setor if setor in SETORES else None)
    if escolhido is None:
        return {"setor": None, "resposta": "Não entendi bem. Sua dúvida é sobre Qualidade, Estoque ou Financeiro?"}
    return {"setor": escolhido, "resposta": SETORES[escolhido]["responder"](texto)}


# =====================================================================
# 6. SITE E API
# =====================================================================
app = Flask(__name__)

PAGINA = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Platina Extintores – Assistente</title>
<style>
:root { --vermelho:#c8102e; --grafite:#23272b; --aco:#e9ecee; --amarelo:#f4c20d; --borda:#cfd5d9; }
* { box-sizing:border-box; }
html, body { height:100%; margin:0; }
body { font-family:system-ui,"Segoe UI",Roboto,sans-serif; background:var(--aco); color:var(--grafite); }
.app { display:grid; grid-template-columns:280px 1fr; height:100%; max-width:1100px; margin:0 auto; }
.setores { background:var(--vermelho); color:#fff; padding:28px 20px; display:flex; flex-direction:column; gap:8px; }
.setores h1 { margin:0; font-size:1.7rem; line-height:1.05; letter-spacing:-.02em; }
.sub { margin:0 0 16px; opacity:.85; font-size:.9rem; }
#lista { display:flex; flex-direction:column; gap:8px; }
.setor-btn { text-align:left; border:0; border-left:6px solid transparent; background:rgba(255,255,255,.12); color:inherit; padding:12px 14px; border-radius:6px; cursor:pointer; font:inherit; }
.setor-btn strong { display:block; font-size:1.05rem; }
.setor-btn span { font-size:.85rem; opacity:.9; }
.setor-btn:hover { background:rgba(255,255,255,.2); }
.setor-btn.ativo { background:#fff; color:var(--grafite); border-left-color:var(--amarelo); }
.chat { display:flex; flex-direction:column; min-height:0; background:#fff; }
.topo { padding:16px 24px; border-bottom:1px solid var(--borda); display:flex; flex-direction:column; gap:2px; }
.topo span { font-size:.9rem; color:#5b6369; }
#mensagens { flex:1; overflow-y:auto; padding:20px 24px; display:flex; flex-direction:column; gap:10px; }
.msg { max-width:75%; padding:10px 14px; border-radius:10px; white-space:pre-line; line-height:1.45; }
.msg.bot { background:var(--aco); align-self:flex-start; border-bottom-left-radius:2px; }
.msg.eu { background:var(--grafite); color:#fff; align-self:flex-end; border-bottom-right-radius:2px; }
#sugestoes { display:flex; flex-wrap:wrap; gap:8px; padding:0 24px 12px; }
#sugestoes button { border:1px solid var(--grafite); background:#fff; color:var(--grafite); border-radius:999px; padding:6px 14px; cursor:pointer; font:inherit; font-size:.9rem; }
#sugestoes button:hover { background:var(--amarelo); border-color:var(--amarelo); }
form { display:flex; gap:8px; padding:14px 24px; border-top:1px solid var(--borda); }
form input { flex:1; padding:12px 14px; border:1px solid var(--borda); border-radius:6px; font:inherit; }
form button { background:var(--vermelho); color:#fff; border:0; border-radius:6px; padding:0 22px; font:inherit; font-weight:600; cursor:pointer; }
button:focus-visible, input:focus-visible { outline:3px solid var(--amarelo); outline-offset:2px; }
@media (max-width:720px) {
  .app { grid-template-columns:1fr; grid-template-rows:auto 1fr; }
  .setores { padding:14px; }
  .setores h1 br, .sub { display:none; }
  #lista { flex-direction:row; overflow-x:auto; }
  .setor-btn { min-width:130px; }
  .setor-btn span { display:none; }
  .msg { max-width:90%; }
}
</style>
</head>
<body>
<div class="app">
  <aside class="setores">
    <h1>Platina<br>Extintores</h1>
    <p class="sub">Escolha com quem quer falar</p>
    <nav id="lista" aria-label="Setores"></nav>
  </aside>
  <main class="chat">
    <header class="topo">
      <strong id="setor-atual">Atendimento geral</strong>
      <span id="setor-desc">Escreva sua pergunta e eu encaminho ao setor certo.</span>
    </header>
    <div id="mensagens" aria-live="polite"></div>
    <div id="sugestoes"></div>
    <form id="form" autocomplete="off">
      <input id="campo" type="text" placeholder="Digite sua pergunta" aria-label="Sua pergunta" required>
      <button type="submit">Enviar</button>
    </form>
  </main>
</div>
<script>
let setorAtual = null, setores = [];
const $msgs = document.getElementById("mensagens"), $sug = document.getElementById("sugestoes"), $lista = document.getElementById("lista");

function mostrar(texto, quem) {
  const d = document.createElement("div");
  d.className = "msg " + quem;
  d.textContent = texto;
  $msgs.appendChild(d);
  $msgs.scrollTop = $msgs.scrollHeight;
}

function marcarSetor(id) {
  setorAtual = id;
  const s = setores.find(x => x.id === id);
  document.getElementById("setor-atual").textContent = s ? s.nome : "Atendimento geral";
  document.getElementById("setor-desc").textContent = s ? s.descricao : "Escreva sua pergunta e eu encaminho ao setor certo.";
  document.querySelectorAll(".setor-btn").forEach(b => b.classList.toggle("ativo", b.dataset.id === id));
  $sug.innerHTML = "";
  (s ? s.sugestoes : []).forEach(t => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = t; b.onclick = () => enviar(t);
    $sug.appendChild(b);
  });
}

async function enviar(texto) {
  mostrar(texto, "eu");
  try {
    const r = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" },
                                         body: JSON.stringify({ mensagem: texto, setor: setorAtual }) });
    const d = await r.json();
    if (d.setor && d.setor !== setorAtual) marcarSetor(d.setor);
    mostrar(d.resposta, "bot");
  } catch (e) {
    mostrar("Não consegui falar com o servidor. Verifique se ele está ligado e tente de novo.", "bot");
  }
}

document.getElementById("form").addEventListener("submit", e => {
  e.preventDefault();
  const c = document.getElementById("campo"), t = c.value.trim();
  if (!t) return;
  c.value = "";
  enviar(t);
});

(async function iniciar() {
  try { setores = await (await fetch("/api/setores")).json(); }
  catch (e) { mostrar("Não consegui carregar os setores. Verifique se o servidor está ligado.", "bot"); return; }
  setores.forEach(s => {
    const b = document.createElement("button");
    b.className = "setor-btn"; b.dataset.id = s.id;
    b.innerHTML = "<strong></strong><span></span>";
    b.querySelector("strong").textContent = s.nome;
    b.querySelector("span").textContent = s.descricao;
    b.onclick = () => { marcarSetor(s.id); mostrar(s.boas_vindas, "bot"); };
    $lista.appendChild(b);
  });
  mostrar("Olá! Eu sou o assistente da Platina Extintores. Escolha um setor ao lado ou escreva sua pergunta que eu encaminho.", "bot");
})();
</script>
</body>
</html>"""


@app.get("/")
def inicio():
    return Response(PAGINA, mimetype="text/html")


@app.get("/api/setores")
def api_setores():
    return jsonify([{"id": id_, "nome": s["nome"], "descricao": s["descricao"],
                     "boas_vindas": s["boas_vindas"], "sugestoes": s["sugestoes"]}
                    for id_, s in SETORES.items()])


@app.post("/api/chat")
def api_chat():
    dados = request.get_json(silent=True) or {}
    return jsonify(responder(dados.get("mensagem", ""), dados.get("setor")))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
