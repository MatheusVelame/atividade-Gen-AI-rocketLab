from google import genai
from google.genai import types
from app.core.config import settings
from app.db.database import db
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ECommerceAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = settings.MODEL_NAME
        self.schema = db.get_schema()

    def _get_system_instruction(self) -> str:
        return f"""
Você é um analista de dados especialista em E-Commerce e SQL.
Seu objetivo é ajudar usuários não técnicos a extrair insights da base de dados SQLite.

Abaixo está o esquema das tabelas disponíveis no banco de dados:
{self.schema}

Conhecimento de Negócio Importante:
- 'Pedidos' é o mesmo que 'Vendas'.
- A tabela `fat_pedidos` contém colunas de data/hora (timestamps) e métricas de logística como `entrega_no_prazo`.
- A tabela `fat_itens_pedidos` liga produtos a vendedores e contém o preço (`preco_BRL`).
- A tabela `fat_avaliacoes_pedidos` contém a coluna `avaliacao` (nota de 1 a 5).

Exemplos de SQL para guiar você:
- Top 10 produtos mais vendidos: SELECT p.nome_produto, COUNT(i.id_pedido) as total_vendas FROM dim_produtos p JOIN fat_itens_pedidos i ON p.id_produto = i.id_produto GROUP BY p.nome_produto ORDER BY total_vendas DESC LIMIT 10;
- Receita total por categoria: SELECT p.categoria_produto, SUM(i.preco_BRL) as receita_total FROM dim_produtos p JOIN fat_itens_pedidos i ON p.id_produto = i.id_produto GROUP BY p.categoria_produto ORDER BY receita_total DESC;
- % de pedidos entregues no prazo por estado: SELECT c.estado, 100.0 * SUM(CASE WHEN p.entrega_no_prazo = 'sim' THEN 1 ELSE 0 END) / COUNT(*) as pct_no_prazo FROM dim_consumidores c JOIN fat_pedidos p ON c.id_consumidor = p.id_consumidor GROUP BY c.estado;

Regras Cruciais:
1. Sempre responda em Português.
2. Gere apenas comandos SQL do tipo SELECT. Nunca tente modificar os dados.
3. Se o usuário fizer uma pergunta que não pode ser respondida com estes dados, explique educadamente o motivo.
4. Suas respostas devem conter o SQL gerado e uma análise humana dos dados retornados.

Formato de Saída esperado (JSON):
{{
    "sql": "O comando SQL gerado",
    "thought": "Seu raciocínio sobre por que esta query responde à pergunta"
}}
"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def _safe_generate_content(self, prompt: str, config: types.GenerateContentConfig):
        return self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=config
        )

    def generate_sql(self, user_query: str) -> dict:
        config = types.GenerateContentConfig(
            system_instruction=self._get_system_instruction(),
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        prompt = f"Pergunta do usuário: {user_query}"
        response = self._safe_generate_content(prompt, config)
        return json.loads(response.text)

    def analyze_results(self, user_query: str, sql: str, results: list) -> str:
        config = types.GenerateContentConfig(
            system_instruction="Você é um analista que interpreta resultados de banco de dados e os explica de forma clara para um gestor.",
            temperature=0.5
        )
        
        prompt = f"""
        Pergunta original: {user_query}
        SQL executado: {sql}
        Resultados brutos do banco: {results}
        
        Explique estes resultados de forma clara e profissional, destacando os pontos principais.
        """
        
        response = self._safe_generate_content(prompt, config)
        return response.text

agent = ECommerceAgent()
