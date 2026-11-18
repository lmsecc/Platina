# Platina Extintores – Chatbot por setores

Chatbot simples para atendimento de uma empresa de extintores, dividido em três setores:

| Setor | O que responde |
|---|---|
| **Qualidade** | Prazo de recarga, teste hidrostático, selo do Inmetro, inspeção mensal e norma NBR 12962 |
| **Estoque** | Quantidade de cada extintor, lista completa e itens abaixo do mínimo |
| **Financeiro** | Tabela de preços, orçamento, formas de pagamento e nota fiscal |

O cliente pode escolher um setor no menu lateral ou escrever direto. Se a pergunta for de outro assunto, o chatbot troca de setor sozinho.

## Arquivos

- `app.py`: o chatbot completo (dados, setores, API e tela do chat).
- `requirements.txt`: bibliotecas necessárias (apenas o Flask).

## Como rodar

1. Instale o [Python 3.9 ou mais novo](https://www.python.org/downloads/).
2. Abra o terminal na pasta do projeto e instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicie o chatbot:

   ```bash
   python app.py
   ```

4. Abra http://localhost:5000 no navegador.

## Exemplos de perguntas

- "Qual o prazo de recarga?"
- "Quantos PQS 6 kg temos?"
- "O que está acabando?"
- "Orçamento de 5 PQS 6 kg"
- "Formas de pagamento"

## Como mudar os dados

O `app.py` é dividido em blocos com cabeçalhos de comentário:

1. **DADOS:** lista de extintores, estoque, estoque mínimo, preços e serviços.
2. **SETOR QUALIDADE:** textos de prazos, selo, inspeção e norma.
3. **SETOR ESTOQUE:** respostas sobre quantidades.
4. **SETOR FINANCEIRO:** respostas sobre preços, pagamento e nota fiscal.
5. **CHATBOT:** palavras-chave que decidem qual setor responde.
6. **SITE E API:** tela do chat e rotas (`/api/setores` e `/api/chat`).

Para incluir um novo extintor, adicione uma linha na lista `PRODUTOS` do bloco 1.

## Atenção

Os preços, quantidades, descontos e prazos de pagamento são **exemplos**. Troque pelos dados reais da empresa antes de usar com clientes. Confirme também com o responsável técnico se os prazos de qualidade batem com o que a empresa pratica.

O chatbot entende as perguntas por palavras-chave, então frases muito livres podem não ser reconhecidas.

## Próximos passos

- Ligar o estoque e os preços a uma planilha ou banco de dados real.
- Criar novos setores (por exemplo, Vendas).
- Usar uma IA para entender frases mais livres.
