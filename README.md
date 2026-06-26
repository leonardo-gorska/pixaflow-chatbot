# PixaFlow ChatBot

Um chatbot de mercado simples e funcional desenvolvido como teste técnico. O projeto consiste em uma API backend em FastAPI com integração com o Google Gemini AI e um frontend em React com TypeScript.

## Arquitetura

O projeto segue uma arquitetura em camadas para separação de responsabilidades:

```
pixaflow-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/           # Rotas da API
│   │   ├── database/      # Modelos e configuração do banco
│   │   ├── services/      # Lógica de negócio (inventory, gemini, chat)
│   │   ├── tests/         # Testes pytest
│   │   ├── config.py      # Configurações e variáveis de ambiente
│   │   ├── schemas.py     # Schemas Pydantic
│   │   └── main.py        # Aplicação FastAPI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── api.ts         # Cliente HTTP
│   │   ├── App.tsx        # Componente principal
│   │   └── main.tsx       # Entry point
│   └── package.json
├── .gitignore
├── .env.example
└── README.md
```

## Tecnologias Utilizadas

### Backend
- **Python 3.12+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para acesso ao banco de dados
- **SQLite** - Banco de dados leve e sem configuração
- **Google Gemini AI** - LLM para gerar respostas naturais
- **Pytest** - Framework de testes
- **Pydantic** - Validação de dados

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool rápido
- **Axios** - Cliente HTTP

## Pré-requisitos

- Python 3.12 ou superior
- Node.js 18 ou superior
- npm ou yarn
- Chave de API do Google Gemini (gratuita em [Google AI Studio](https://makersuite.google.com/app/apikey))

## Configuração

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd pixaflow-chatbot
```

### 2. Configurar o Backend

```bash
cd backend

# Criar ambiente virtual (opcional mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
# Copiar o arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env e adicionar sua chave do Gemini
# GEMINI_API_KEY=sua_chave_aqui
```

### 4. Configurar o Frontend

```bash
cd frontend

# Instalar dependências
npm install
```

##  Executando o Projeto

### Iniciar o Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`

### Iniciar o Frontend

```bash
cd frontend
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`

## Executar Testes

```bash
cd backend

# Executar todos os testes
pytest

# Executar com verbosidade
pytest -v

# Executar testes específicos
pytest app/tests/test_inventory.py
pytest app/tests/test_chat.py
```

## Como Usar

1. Acesse `http://localhost:5173` no navegador
2. Digite perguntas sobre produtos do mercado, por exemplo:
   - "Tem arroz?"
   - "Quanto custa o feijão?"
   - "Quantos cafés existem?"
   - "Tem leite?"
3. O bot responderá com informações do estoque de forma natural

## Endpoints da API

### POST /api/chat
Envia uma mensagem para o chatbot. O Gemini AI extrai a intenção e o produto antes de consultar o banco.

**Request:**
```json
{
  "message": "Tem arroz?"
}
```

**Response:**
```json
{
  "answer": "Sim! Temos Arroz Camil 5kg. Atualmente há 18 unidades em estoque por R$ 29,90."
}
```

### GET /api/products
Retorna todos os produtos do estoque.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Arroz Camil 5kg",
    "description": "Arroz integral premium",
    "price": 29.90,
    "quantity": 18,
    "category": "Grãos"
  }
]
```

### GET /api/products/{id}
Retorna um produto específico por ID.

**Response:**
```json
{
  "id": 1,
  "name": "Arroz Camil 5kg",
  "description": "Arroz integral premium",
  "price": 29.90,
  "quantity": 18,
  "category": "Grãos"
}
```

### GET /
Endpoint raiz para verificar se a API está rodando.

### GET /health
Health check com status detalhado dos componentes (API, Database, Gemini).

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "api": true,
    "database": true,
    "gemini": true
  }
}
```

## Como Funciona

A arquitetura do chatbot foi projetada para evitar alucinações da IA e garantir respostas baseadas apenas em dados reais:

1. **Frontend (React)**: O usuário envia uma mensagem através da interface
2. **API (FastAPI)**: Recebe a mensagem e a processa
3. **Gemini Service (Intent Extraction)**: O Gemini analisa a mensagem e extrai:
   - A intenção do usuário (buscar produto, verificar preço, verificar quantidade)
   - O nome do produto mencionado
4. **Inventory Service**: Consulta o banco de dados SQLite com o produto extraído
5. **Gemini Service (Response Formatting)**: Formata os dados do banco em uma resposta natural
6. **Fallback**: Se o Gemini falhar, usa templates simples para garantir que o chat nunca pare
7. **Resposta**: Retorna ao frontend para exibição

**Vantagens desta arquitetura:**
- A IA nunca consulta o banco diretamente, evitando alucinações
- Separação clara entre extração de intenção e formatação de resposta
- Sistema robusto com fallbacks em caso de falha da API
- Respostas sempre baseadas em dados reais do estoque

O banco de dados é populado automaticamente com produtos de exemplo na primeira execução.

## Segurança

- O arquivo `.env` está incluído no `.gitignore` para evitar que chaves de API sejam commitadas
- Use apenas o `.env.example` como referência para configuração
- Nunca commit chaves de API ou dados sensíveis

## Produtos de Exemplo

O banco de dados é inicializado com os seguintes produtos:

| Produto | Preço | Quantidade |
|---------|-------|-------------|
| Arroz Camil 5kg | R$ 29,90 | 18 |
| Feijão Carioca Kicaldo 1kg | R$ 8,90 | 40 |
| Leite Integral Itambé 1L | R$ 6,50 | 12 |
| Café Pilão Tradicional 500g | R$ 17,80 | 9 |
| Macarrão Renata Espaguete 500g | R$ 5,20 | 25 |
| Açúcar União Refinado 1kg | R$ 4,90 | 31 |
| Óleo de Soja Soya 900ml | R$ 8,50 | 15 |
| Farinha de Trigo Dona Benta 1kg | R$ 6,20 | 22 |

## Destaques do Projeto

- Código organizado em camadas (API, Services, Database)
- Separação clara de responsabilidades
- Testes automatizados com pytest (cobertura de inventory, chat e endpoints)
- Validação de dados com Pydantic
- ORM com SQLAlchemy
- Integração inteligente com LLM (Gemini 1.5 Flash)
- Extração de intenção usando IA antes de consultar o banco
- Sistema robusto com fallbacks em caso de falha da API
- Health check detalhado com status de cada componente
- Endpoints REST para consulta direta de produtos
- Frontend moderno com React + TypeScript
- Interface simples e intuitiva
- Seed automática do banco de dados
- Configuração via variáveis de ambiente
- README completo e claro
- Arquitetura que evita alucinações da IA

## Notas

- O banco de dados SQLite é criado automaticamente na primeira execução
- O Gemini AI é usado em duas etapas: (1) extrair intenção e produto da mensagem, (2) formatar a resposta com dados do banco
- A IA nunca consulta o banco diretamente, garantindo que as respostas sejam baseadas apenas em dados reais
- Sistema possui fallbacks automáticos caso a API do Gemini falhe
- O projeto foi desenvolvido para ser fácil de clonar e executar

## Contribuindo

Este projeto foi desenvolvido como teste técnico. Para sugestões ou melhorias, sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto é parte de um teste técnico e está disponível para fins de avaliação.
