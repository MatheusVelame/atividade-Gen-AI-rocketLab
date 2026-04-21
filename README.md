# Rocket Lab 2026: Agente GenAI de E-Commerce 🚀

Este projeto é um agente inteligente capaz de realizar consultas e análises em tempo real sobre um banco de dados de E-Commerce utilizando Processamento de Linguagem Natural (Text-to-SQL).

Desenvolvido para a **Atividade GenAI - Visagio | Rocket Lab 2026**.

## 🛠️ Stack Tecnológica
- **Linguagem:** Python 3.10+
- **IA:** Gemini 2.5 Flash / Flash Lite
- **Framework de Backend:** FastAPI
- **Interface Visual:** Streamlit
- **Banco de Dados:** SQLite3

## 📋 Funcionalidades
- **Text-to-SQL:** Transformação de perguntas casuais em comandos SQL precisos.
- **Análise Interpretativa:** A IA não apenas entrega os dados, mas explica os insights para gestores.
- **Visualização de Dados:** Geração dinâmica de gráficos e tabelas.
- **Guardrails de Segurança:** O agente é restrito apenas a operações de leitura (SELECT).

## 🚀 Como Executar

### 1. Pré-requisitos
- Ter o Python instalado.
- Ter uma chave de API do Google Gemini.

### 2. Configuração do Ambiente
Clone o repositório e crie um ambiente virtual:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Linux/macOS)
source venv/bin/activate

# Ativar ambiente (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie o arquivo `.env` a partir do exemplo e adicione sua chave de API:
```bash
cp .env.example .env
```
Edite o arquivo `.env`:
```text
GEMINI_API_KEY=SUA_CHAVE_AQUI
DATABASE_URL=sqlite:///banco.db
MODEL_NAME=gemini-2.5-flash-lite
```

### 4. Executando a Aplicação
Você precisará de dois terminais abertos:

**Terminal 1 (Backend):**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
streamlit run frontend/app.py
```
Acesse a interface em `http://localhost:8501`.

### 5. Documentação da API (Swagger)
Com o backend rodando, você pode acessar a documentação interativa da API (Swagger UI) em:
`http://localhost:8000/docs`

## 📊 Categorias de Análise Suportadas
O agente está treinado para responder sobre:
- **Vendas e Receita:** (Ex: Top 10 produtos, receita por categoria).
- **Entrega e Logística:** (Ex: Pedidos no prazo por estado, status de entrega).
- **Satisfação:** (Ex: Média de avaliação por vendedor).
- **Consumidores:** (Ex: Ticket médio por estado, volume de pedidos).

---
