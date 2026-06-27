# PixaFlow ChatBot

Chatbot simples de mercado/vendinha desenvolvido como desafio técnico. O usuário acessa uma tela de chat, pergunta sobre produtos, preços, quantidades em estoque e informações básicas do mercado, e o bot responde com base no inventário cadastrado.

O projeto usa **FastAPI** no backend, **React + TypeScript** no frontend, **SQLite** como banco de dados e integração com **Google Gemini** para apoiar respostas em linguagem natural. Para manter o chatbot estável, perguntas comuns de mercado também são tratadas por regras locais antes de consultar o estoque.

## Funcionalidades

- Chat simples para atendimento de mercado
- Continuação de conversa com histórico curto, como perguntar "Quanto custa?" após "Tem café?"
- Consulta de produtos por nome, com suporte a acentos e plurais simples
- Respostas para preço, quantidade, disponibilidade e listagem de produtos
- Respostas para horário, endereço, contato, entregas, formas de pagamento, trocas e promoções
- Respostas úteis sobre categorias, menor preço, maior preço, baixo estoque e total de unidades
- Inventário persistido em SQLite com seed automático
- Integração com Gemini Flash
- Fallback local caso o Gemini não esteja configurado ou falhe
- API documentada automaticamente pelo FastAPI
- Testes automatizados com pytest

## Tecnologias

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Google Gemini AI
- Pytest
- Pydantic

### Frontend

- React 18
- TypeScript
- Vite
- Axios

## Estrutura

```text
pixaflow-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/           # Rotas HTTP
│   │   ├── database/      # Banco, modelos e seed
│   │   ├── services/      # Regras de chat, inventário e Gemini
│   │   ├── tests/         # Testes do backend
│   │   ├── config.py
│   │   ├── main.py
│   │   └── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── .env.example
└── README.md
```

## Pré-requisitos

- Python 3.12 ou superior
- Node.js 18 ou superior
- npm
- Chave gratuita do Gemini no [Google AI Studio](https://makersuite.google.com/app/apikey)

> O projeto possui fallback local e consegue responder perguntas básicas mesmo sem chave Gemini, mas a chave é recomendada porque o desafio pede uso de LLM.

## Configuração

Clone o repositório e entre na pasta do projeto:

```bash
git clone <url-do-repositorio>
cd ChatBot
```

Crie o arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` com sua chave:

```env
GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash-lite
DATABASE_URL=sqlite:///./inventory.db
```

## Rodando o Backend

```bash
cd backend
python -m venv venv
```

Ative o ambiente virtual:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie a API:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

A API ficará disponível em:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

Na primeira execução, o banco SQLite é criado automaticamente e preenchido com produtos de exemplo.

## Rodando o Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

A aplicação ficará disponível em:

```text
http://localhost:5173
```

O Vite já está configurado para redirecionar chamadas `/api` para o backend em `http://localhost:8000`.

## Testes

Para rodar todos os testes do backend:

```bash
cd backend
pytest app/tests -q
```

Também é possível rodar a partir da raiz:

```bash
python -m pytest backend/app/tests -q
```

Os testes cobrem:

- Busca no inventário
- Produtos inexistentes
- Busca sem diferenciar maiúsculas/minúsculas
- Busca com acentos e plurais simples
- Perguntas de chat sobre quantidade, preço, endereço, entrega, horário, listagem e informações da loja
- Endpoints principais da API

## Exemplos de Perguntas

```text
Tem arroz?
Tem café?
Quantos cafés tem?
Quais cafés tem?
Quanto custa o feijão?
O que vocês vendem?
Quais?
Quais categorias vocês têm?
Qual o produto mais barato?
Qual o produto mais caro?
Tem algum produto acabando?
Quantas unidades no total tem no estoque?
Qual o horário de funcionamento?
Qual o endereço?
Qual o telefone de contato?
Vocês entregam?
Vocês fazem troca?
Quais formas de pagamento vocês aceitam?
Tem promoção?
```

O bot foi pensado para responder perguntas naturais dentro do contexto de mercado. Perguntas fora desse contexto podem receber uma resposta de fallback orientando o usuário a perguntar sobre produtos, estoque ou informações da loja.

## Produtos de Exemplo

| Produto | Categoria | Preço | Quantidade |
| --- | --- | ---: | ---: |
| Arroz Camil 5kg | Grãos | R$ 29,90 | 18 |
| Feijão Carioca Kicaldo 1kg | Grãos | R$ 8,90 | 40 |
| Leite Integral Itambé 1L | Laticínios | R$ 6,50 | 12 |
| Café Pilão Tradicional 500g | Bebidas | R$ 17,80 | 9 |
| Macarrão Renata Espaguete 500g | Massas | R$ 5,20 | 25 |
| Açúcar União Refinado 1kg | Açúcar | R$ 4,90 | 31 |
| Óleo de Soja Soya 900ml | Óleos | R$ 8,50 | 15 |
| Farinha de Trigo Dona Benta 1kg | Farinhas | R$ 6,20 | 22 |

## Endpoints

### `POST /api/chat`

Envia uma mensagem para o chatbot.

**Request**

```json
{
  "message": "Quantos cafés tem?"
}
```

**Response**

```json
{
  "answer": "Temos 9 unidades de Café Pilão Tradicional 500g em estoque."
}
```

### `GET /api/products`

Lista todos os produtos do estoque.

### `GET /api/products/{product_id}`

Busca um produto pelo ID.

### `GET /health`

Retorna o status da API, banco de dados e Gemini.

## Como o Chatbot Funciona

O fluxo principal é:

1. O usuário envia uma mensagem pelo frontend.
2. A API recebe a mensagem e um histórico curto da conversa no endpoint `/api/chat`.
3. O `ChatService` identifica a intenção da pergunta.
4. O `InventoryService` consulta os produtos no SQLite.
5. O bot responde usando dados reais do banco.
6. Quando configurado, o `GeminiService` pode apoiar a interpretação ou a formatação das respostas.
7. Se o Gemini falhar ou não estiver configurado, o projeto usa respostas locais para manter o atendimento funcionando.

Essa abordagem evita que a LLM invente estoque, preço ou produto. O banco de dados continua sendo a fonte da verdade.

## Decisões Técnicas

### SQLite

Foi escolhido por simplicidade. O avaliador consegue clonar, instalar e rodar sem configurar PostgreSQL ou MySQL. Como o acesso ao banco usa SQLAlchemy, uma troca futura para outro banco seria simples.

### FastAPI

FastAPI oferece tipagem, validação com Pydantic e documentação automática via Swagger, o que facilita a avaliação do backend.

### Gemini com fallback

O desafio pede uma LLM com Gemini. O projeto integra o Gemini, mas não depende exclusivamente dele para perguntas básicas de mercado. Isso deixa o chat mais previsível, economiza chamadas ao modelo e mantém o sistema funcionando mesmo se a chave não estiver configurada durante testes locais.

### React + TypeScript

O frontend é propositalmente simples: uma tela de chat para enviar mensagens e visualizar respostas. TypeScript ajuda a manter o cliente HTTP e os componentes mais seguros.

## Observações

- Não commite o arquivo `.env`.
- O arquivo `.env.example` serve apenas como referência.
- O banco `inventory.db` é criado automaticamente quando o backend sobe.
- A interface foi mantida simples para ficar alinhada ao escopo do desafio.
- A documentação da API pode ser acessada em `/docs` enquanto o backend estiver rodando.
