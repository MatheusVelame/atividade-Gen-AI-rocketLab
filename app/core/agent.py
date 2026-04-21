from google import genai
from google.genai import types
from app.core.config import settings
from app.db.database import db
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.prompts import SYSTEM_PROMPT_TEMPLATE, ANALYSIS_INSTRUCTION

class ECommerceAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = settings.MODEL_NAME
        self.schema = db.get_schema()
        self.cache = {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _safe_generate_content(self, prompt: str, config: types.GenerateContentConfig):
        try:
            return self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config
            )
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"LIMITE DE COTAS ATINGIDO (429): {error_msg}")
            else:
                print(f"ERRO NA API GEMINI: {error_msg}")
            raise e

    def generate_sql(self, user_query: str) -> dict:
        cache_key = f"sql_{user_query}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT_TEMPLATE.format(schema=self.schema),
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        prompt = f"Pergunta do usuário: {user_query}"
        response = self._safe_generate_content(prompt, config)
        result = json.loads(response.text)
        self.cache[cache_key] = result
        return result

    def analyze_results(self, user_query: str, sql: str, results: list) -> str:
        cache_key = f"analysis_{user_query}_{sql}_{hash(str(results))}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
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
        self.cache[cache_key] = response.text
        return response.text

agent = ECommerceAgent()
