# PaperBroker

PaperBroker é uma plataforma web de simulação financeira (paper trading) que permite aos usuários gerenciar portfólios de investimentos com dados de mercado em tempo real. O sistema processa cotações de ativos da B3 e do mercado americano.

**Acesso em Produção:**
- Frontend: [https://app-paperbroker.netlify.app](https://app-paperbroker.netlify.app)

## 🛠️ Tecnologias Utilizadas

O projeto adota uma arquitetura de Monorepo, separando as responsabilidades de cliente e servidor.

**Backend (`/src`)**
* **Linguagem:** Python
* **Framework:** FastAPI
* **ORM & Banco de Dados:** SQLAlchemy e PostgreSQL
* **Integração de Dados:** `yfinance` (Yahoo Finance API) para cotações em tempo real
* **Autenticação:** JWT (JSON Web Tokens)
* **Deploy:** Render (API) e Neon.tech (Database Serverless)

**Frontend (`/frontend`)**
* **Biblioteca Base:** React
* **Linguagem:** TypeScript
* **Build Tool:** Vite
* **Estilização:** Tailwind CSS
* **Deploy:** Netlify

## ⚙️ Funcionalidades Principais

* **Gestão de Identidade:** Cadastro de usuários e autenticação segura via tokens JWT.
* **Cotações em Tempo Real:** Integração com APIs financeiras para buscar valores atualizados de ações (ex: PETR4.SA, AAPL).
* **Simulação de Operações:** Registro de ordens de compra e venda de ativos.
* **Dashboard de Performance:** Cálculo e exibição do valor total da carteira e rentabilidade baseada no preço médio.

## 📂 Estrutura do Projeto

```text
.
├── frontend/               # Aplicação SPA em React/Vite
│   ├── src/                # Componentes, serviços e páginas
│   ├── public/             # Arquivos estáticos e regras de redirecionamento
│   └── package.json        # Dependências do frontend
├── src/                    # API em FastAPI
│   ├── main.py             # Ponto de entrada da API
│   ├── models.py           # Modelos de banco de dados
│   ├── schemas.py          # Validação de dados
│   ├── config.py           # Gerenciamento de variáveis de ambiente
│   └── requirements.txt    # Dependências do backend
├── docker-compose.yml      # Orquestração do banco de dados para executar localmente
└── README.md
