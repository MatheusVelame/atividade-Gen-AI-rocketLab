from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.agent import agent
from app.db.database import db

router = APIRouter()

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    sql: str
    thought: str
    results: list
    analysis: str

@router.post("/analyze", response_model=QueryResponse)
async def analyze_ecommerce_data(request: QueryRequest):
    try:
        ai_response = agent.generate_sql(request.prompt)
        sql = ai_response.get("sql")
        thought = ai_response.get("thought")
        
        results = db.execute_query(sql)
        
        analysis = agent.analyze_results(request.prompt, sql, results)
        
        return QueryResponse(
            sql=sql,
            thought=thought,
            results=results,
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
