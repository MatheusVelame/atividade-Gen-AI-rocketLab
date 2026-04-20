from google import genai
from google.genai import types
from app.core.config import settings
from app.db.database import db
import json

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

Regras Cruciais:
1. Sempre responda em Português.
2. Gere apenas comandos SQL do tipo SELECT. Nunca tente modificar os dados (DELETE, UPDATE, DROP, etc).
3. Seja rigoroso com os nomes das colunas e tabelas fornecidos no esquema.
4. Se o usuário fizer uma pergunta que não pode ser respondida com estes dados, explique educadamente o motivo.
5. Suas respostas devem conter o SQL gerado e uma análise humana dos dados retornados.

Formato de Saída esperado (JSON):
{{
    "sql": "O comando SQL gerado",
    "thought": "Seu raciocínio sobre por que esta query responde à pergunta"
}}
"""

    def generate_sql(self, user_query: str) -> dict:
        """Transforma a linguagem natural em um comando SQL."""
        config = types.GenerateContentConfig(
            system_instruction=self._get_system_instruction(),
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        prompt = f"Pergunta do usuário: {user_query}"
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=config
        )
        
        return json.loads(response.text)

    def analyze_results(self, user_query: str, sql: str, results: list) -> str:
        """Gera uma explicação em linguagem natural baseada nos resultados do banco."""
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
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=config
        )
        
        return response.text

agent = ECommerceAgent()
