"""
Chatbot - Empresa de Extintores
Setores: Qualidade, Estoque e Financeiro

Como usar:
    Modo terminal (não precisa de Flask):   python app.py --cli
    Modo API web (precisa de Flask):        pip install flask flask-cors
                                            python app.py
    Endpoint:  POST http://localhost:5000/chat
               corpo JSON: {"session_id": "abc", "message": "oi"}

ATENÇÃO: os dados de estoque, preços e notas fiscais abaixo são FICTÍCIOS.
Substitua pelas consultas ao seu banco de dados / ERP quando for para produção.
"""

import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# DADOS FICTÍCIOS (trocar por banco de dados / ERP)
# ---------------------------------------------------------------------------

PRODUTOS = {
    "PQS-ABC-4":  {"nome": "Extintor PQS ABC 4 kg",   "qtd": 120, "preco": 135.00,
                   "chaves": ["pqs", "po", "abc", "4kg", "4 kg"]},
    "PQS-ABC-6":  {"nome": "Extintor PQS ABC 6 kg",   "qtd": 80,  "preco": 189.90,
                   "chaves": ["pqs", "po", "abc", "6kg", "6 kg"]},
    "PQS-BC-12":  {"nome": "Extintor PQS BC 12 kg",   "qtd": 15,  "preco": 320.00,
                   "chaves": ["pqs", "bc", "12kg", "12 kg"]},
    "CO2-6":      {"nome": "Extintor CO2 6 kg",       "qtd": 40,  "preco": 690.00,
                   "chaves": ["co2", "gas carbonico", "carbonico"]},
    "AGUA-10":    {"nome": "Extintor Água 10 L",      "qtd": 0,   "preco": 210.00,
                   "chaves": ["agua", "água", "10l", "10 l"]},
    "ESPUMA-9":   {"nome": "Extintor Espuma 9 L",     "qtd": 22,  "preco": 285.00,
                   "chaves": ["espuma", "9l", "9 l"]},
    "SUPORTE":    {"nome": "Suporte de parede",       "qtd": 300, "preco": 18.50,
                   "chaves": ["suporte", "parede"]},
    "PLACA":      {"nome": "Placa de sinalização",    "qtd": 500, "preco": 12.00,
                   "chaves": ["placa", "sinalizacao", "sinalização"]},
}

NOTAS_FISCAIS = {
    "1001": {"cliente": "Condomínio Solar",  "valor": 2450.00, "venc": "10/12/2026", "status": "Em aberto"},
    "1002": {"cliente": "Mercado Bom Preço", "valor": 980.00,  "venc": "01/11/2026", "status": "Vencida"},
    "1003": {"cliente": "Oficina Silva",     "valor": 540.00,  "venc": "05/11/2026", "status": "Paga"},
}

# ---------------------------------------------------------------------------
# UTILITÁRIOS
# ---------------------------------------------------------------------------

def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e sem espaços extras."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


def tem(texto: str, *palavras: str) -> bool:
    return any(p in texto for p in palavras)


def brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# RESPOSTAS FIXAS
# ---------------------------------------------------------------------------

MENU = (
    "Olá! Sou o assistente virtual da *Extintores Lumina* 🧯\n"
    "Com qual setor você quer falar?\n\n"
    "1 - Qualidade\n"
    "2 - Estoque\n"
    "3 - Financeiro\n"
    "4 - Falar com um atendente\n\n"
    "Digite o número ou o nome do setor. A qualquer momento, digite *menu* para voltar."
)

AJUDA_QUALIDADE = (
    "Setor de *Qualidade*. Posso ajudar com:\n"
    "- Prazos de recarga e manutenção\n"
    "- Teste hidrostático\n"
    "- Certificações e normas (INMETRO, ABNT)\n"
    "- Classes de incêndio e tipo de extintor\n"
    "- Reclamação ou não conformidade\n\n"
    "O que você precisa?"
)

AJUDA_ESTOQUE = (
    "Setor de *Estoque*. Posso ajudar com:\n"
    "- Consultar disponibilidade (ex.: \"tem PQS 6kg?\")\n"
    "- Consultar preço\n"
    "- Listar todos os produtos\n"
    "- Prazo de entrega\n\n"
    "Qual produto você procura?"
)


AJUDA_FINANCEIRO = (
    "Setor *Financeiro*. Posso ajudar com:\n"
    "- Consulta de nota fiscal / boleto (informe o número da NF)\n"
    "- Segunda via de boleto\n"
    "- Formas de pagamento\n"
    "- Prazos e condições\n\n"
    "O que você precisa?"
)


# ---------------------------------------------------------------------------
# LÓGICA POR SETOR
# ---------------------------------------------------------------------------

def responder_qualidade(msg: str, sessao: dict) -> str:
    if sessao.get("aguardando") == "reclamacao":
        sessao["aguardando"] = None
        protocolo = f"QLD-{abs(hash(msg)) % 100000:05d}"
        return (f"Obrigado! Registrei sua ocorrência com o protocolo *{protocolo}*. "
                "A equipe de Qualidade retorna em até 2 dias úteis.\n\n"
                "Algo mais? (ou digite *menu*)")

    if tem(msg, "recarga", "validade", "vencid", "prazo de manutencao", "manutencao"):
        return ("Prazos de referência (ABNT NBR 12962):\n"
                "- *Inspeção*: mensal, feita pelo próprio responsável (lacre, manômetro, pino).\n"
                "- *Recarga*: anual para PQS, água e espuma; CO2 conforme teste.\n"
                "- Recarregue sempre após qualquer uso, mesmo parcial.\n"
                "Quer agendar uma recarga? Fale com o atendente (opção 4).")

    if tem(msg, "hidrostatico", "teste"):
        return ("O *teste hidrostático* verifica a resistência do cilindro e deve ser feito "
                "a cada *5 anos*, em empresa certificada. Cilindros reprovados são inutilizados. "
                "Fazemos o serviço e emitimos o selo de conformidade.")

    if tem(msg, "inmetro", "certific", "norma", "abnt", "selo"):
        return ("Nossos extintores seguem as normas ABNT NBR 15808 / 15809 e possuem selo de "
                "conformidade INMETRO. Em cada unidade você encontra o selo, o número de série, "
                "a data de fabricação e a data da última manutenção.")

    if tem(msg, "classe", "tipo", "qual extintor", "incendio", "fogo"):
        return ("Escolha pelo tipo de fogo:\n"
                "- *Classe A* (madeira, papel, tecido): água, espuma ou PQS ABC\n"
                "- *Classe B* (líquidos inflamáveis): CO2, espuma ou PQS\n"
                "- *Classe C* (equipamentos elétricos): CO2 ou PQS\n"
                "- *Classe D* (metais combustíveis): pó especial\n"
                "Para uma indicação exata, fale com o atendente (opção 4).")

    if tem(msg, "reclama", "defeito", "problema", "nao conformidade", "falha"):
        sessao["aguardando"] = "reclamacao"
        return "Sinto muito pelo transtorno. Descreva o problema (produto, lote ou NF, se tiver):"

    return ("Não entendi bem. Tente: *recarga*, *teste hidrostático*, *certificação*, "
            "*classes de incêndio* ou *reclamação*. Ou digite *menu*.")


def buscar_produtos(msg: str):
    """Retorna produtos cujo nome/código/chaves aparecem na mensagem."""
    achados = []
    for cod, p in PRODUTOS.items():
        if any(normalizar(c) in msg for c in p["chaves"]) or normalizar(p["nome"]) in msg:
            achados.append((cod, p))
    # Se citou um tamanho específico (ex.: 6kg), filtra por ele
    tamanho = re.search(r"(\d+)\s?(kg|l)\b", msg)
    if tamanho and achados:
        alvo = f"{tamanho.group(1)}{tamanho.group(2)}"
        filtrados = [(c, p) for c, p in achados
                     if alvo in normalizar(p["nome"]).replace(" ", "")]
        if filtrados:
            achados = filtrados
    return achados


def linha_produto(p: dict, com_preco=True) -> str:
    estoque = f"{p['qtd']} un." if p["qtd"] > 0 else "indisponível"
    preco = f" - {brl(p['preco'])}" if com_preco else ""
    return f"- {p['nome']}: {estoque}{preco}"


def responder_estoque(msg: str, sessao: dict) -> str:
    if tem(msg, "lista", "todos", "catalogo", "produtos"):
        return "Produtos em estoque:\n" + "\n".join(
            linha_produto(p) for p in PRODUTOS.values()) + "\n\nQuer consultar algum item?"

    if tem(msg, "entrega", "prazo", "frete"):
        return ("Prazo de entrega: *1 a 2 dias úteis* na região metropolitana e "
                "*3 a 7 dias úteis* para as demais regiões. Pedidos acima de R$ 1.500,00 "
                "têm frete grátis na região metropolitana.")

    achados = buscar_produtos(msg)
    if achados:
        texto = "Encontrei:\n" + "\n".join(linha_produto(p) for _, p in achados)
        if any(p["qtd"] == 0 for _, p in achados):
            texto += "\n\nItens indisponíveis podem ser reservados com o atendente (opção 4)."
        return texto

    return ("Não localizei esse produto. Tente o tipo e o tamanho (ex.: *PQS 4kg*, *CO2*, "
            "*espuma*) ou digite *lista* para ver todos.")


def responder_financeiro(msg: str, sessao: dict) -> str:
    # Pode ter um número de NF na mensagem
    numero = re.search(r"\b(\d{4,})\b", msg)

    if sessao.get("aguardando") == "nf" or (numero and tem(msg, "nf", "nota", "boleto", "fatura")):
        if not numero:
            return "Não achei o número. Informe apenas os dígitos da NF (ex.: 1001):"
        sessao["aguardando"] = None
        nf = NOTAS_FISCAIS.get(numero.group(1))
        if not nf:
            return f"Não encontrei a NF {numero.group(1)}. Confira o número ou fale com o atendente (opção 4)."
        texto = (f"*NF {numero.group(1)}* - {nf['cliente']}\n"
                 f"Valor: {brl(nf['valor'])}\nVencimento: {nf['venc']}\nSituação: *{nf['status']}*")
        if nf["status"] == "Vencida":
            texto += "\n\nEsta nota está vencida. Posso gerar a segunda via com os encargos atualizados? Fale com o atendente (opção 4)."
        return texto

    if tem(msg, "segunda via", "2 via", "2a via", "boleto", "nota", "nf", "fatura", "consultar"):
        sessao["aguardando"] = "nf"
        return "Claro! Informe o *número da nota fiscal* (somente números):"

    if tem(msg, "pagamento", "pagar", "pix", "cartao", "parcel"):
        return ("Formas de pagamento:\n"
                "- PIX (5% de desconto à vista)\n"
                "- Boleto bancário (7, 14 ou 28 dias)\n"
                "- Cartão de crédito em até 6x sem juros\n"
                "Condições para empresas (CNPJ) sujeitas à análise de crédito.")

    if tem(msg, "prazo", "condicao", "juros", "multa", "atraso"):
        return ("Em caso de atraso: multa de 2% + juros de 1% ao mês, proporcionais aos dias. "
                "Para renegociar, fale com o atendente (opção 4).")

    return ("Não entendi. Tente: *segunda via*, *consultar NF*, *formas de pagamento* "
            "ou *prazos*. Ou digite *menu*.")


SETORES = {
    "qualidade":  (AJUDA_QUALIDADE,  responder_qualidade),
    "estoque":    (AJUDA_ESTOQUE,    responder_estoque),
    "financeiro": (AJUDA_FINANCEIRO, responder_financeiro),
}


# ---------------------------------------------------------------------------
# MOTOR DO CHATBOT
# ---------------------------------------------------------------------------

SESSOES = {}  # session_id -> {"setor": str|None, "aguardando": str|None}


def escolher_setor(msg: str):
    if msg in ("1",) or "qualidade" in msg:
        return "qualidade"
    if msg in ("2",) or "estoque" in msg:
        return "estoque"
    if msg in ("3",) or "financeiro" in msg or "financas" in msg:
        return "financeiro"
    if msg in ("4",) or tem(msg, "atendente", "humano", "pessoa"):
        return "atendente"
    return None


def responder(session_id: str, mensagem: str) -> str:
    sessao = SESSOES.setdefault(session_id, {"setor": None, "aguardando": None, "novo": True})
    msg = normalizar(mensagem)

    if not msg:
        return "Pode digitar sua mensagem, por favor."

    # Primeira mensagem ou comandos de menu
    if sessao.pop("novo", False) or tem(msg, "menu", "inicio", "voltar", "oi", "ola", "bom dia", "boa tarde", "boa noite") and len(msg) < 15:
        sessao.update(setor=None, aguardando=None)
        return MENU

    if tem(msg, "tchau", "obrigado", "valeu", "encerrar", "sair") and len(msg) < 20:
        sessao.update(setor=None, aguardando=None)
        return "Foi um prazer ajudar! Qualquer coisa, é só chamar. 🧯"

    # Troca de setor (a qualquer momento)
    novo_setor = escolher_setor(msg) if len(msg) < 25 else None
    if novo_setor == "atendente":
        sessao.update(setor=None, aguardando=None)
        return ("Certo! Vou encaminhar você a um atendente. "
                "Horário: seg a sex, 8h às 18h. Deixe seu nome e telefone que retornamos.")
    if novo_setor:
        sessao.update(setor=novo_setor, aguardando=None)
        return SETORES[novo_setor][0]

    # Já está em um setor
    if sessao["setor"]:
        return SETORES[sessao["setor"]][1](msg, sessao)

    # Sem setor: tenta adivinhar pelo conteúdo
    if tem(msg, "recarga", "inmetro", "hidrostatico", "reclama", "norma"):
        sessao["setor"] = "qualidade"
    elif tem(msg, "estoque", "tem ", "preco", "quanto custa", "disponivel", "pqs", "co2"):
        sessao["setor"] = "estoque"
    elif tem(msg, "boleto", "nota fiscal", "pagamento", "segunda via", "nf "):
        sessao["setor"] = "financeiro"

    if sessao["setor"]:
        return SETORES[sessao["setor"]][1](msg, sessao)

    return "Não consegui identificar o assunto.\n\n" + MENU


# ---------------------------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------------------------

def modo_terminal():
    print("=== Chatbot Extintores Lumina (digite 'sair' para encerrar) ===\n")
    print("Bot:", responder("cli", "oi"), "\n")
    while True:
        try:
            texto = input("Você: ")
        except (EOFError, KeyboardInterrupt):
            break
        if normalizar(texto) == "sair":
            print("Bot: Até logo! 🧯")
            break
        print("Bot:", responder("cli", texto), "\n")


def criar_app():
    from flask import Flask, jsonify, request
    try:
        from flask_cors import CORS
    except ImportError:
        CORS = None

    app = Flask(__name__)
    if CORS:
        CORS(app)  # permite o frontend (outra porta) chamar a API

    @app.get("/")
    def status():
        return jsonify({"status": "ok", "bot": "Extintores Lumina"})

    @app.post("/chat")
    def chat():
        dados = request.get_json(silent=True) or {}
        mensagem = str(dados.get("message", "")).strip()
        session_id = str(dados.get("session_id", "padrao"))
        if not mensagem:
            return jsonify({"error": "Campo 'message' é obrigatório."}), 400
        return jsonify({"reply": responder(session_id, mensagem)})

    return app


if __name__ == "__main__":
    if "--cli" in sys.argv:
        modo_terminal()
    else:
        criar_app().run(host="0.0.0.0", port=5000, debug=True)
