from google import genai
from google.genai import types
from app.core.config import settings
from app.db.database import db
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.prompts import SYSTEM_INSTRUCTION, ANALYSIS_INSTRUCTION

class ECommerceAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = settings.MODEL_NAME
        self.schema = db.get_schema()

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
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        prompt = f"Pergunta do usuário: {user_query}"
        response = self._safe_generate_content(prompt, config)
        return json.loads(response.text)

    def analyze_results(self, user_query: str, sql: str, results: list) -> str:
        config = types.GenerateContentConfig(
            system_instruction=ANALYSIS_INSTRUCTION,
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
