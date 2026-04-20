import sqlite3
from typing import List, Dict, Any
from app.core.config import settings
import os

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(root_dir, "banco.db")
        else:
            self.db_path = db_path

    def get_connection(self):
        """Retorna uma conexão bruta com o SQLite como solicitado na atividade."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Executa uma query SELECT e retorna os resultados como uma lista de dicionários."""
        query_check = query.strip().upper()
        if not query_check.startswith("SELECT") and not query_check.startswith("WITH"):
            raise ValueError("Apenas comandos SELECT são permitidos por segurança.")
            
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            raise e
        finally:
            conn.close()

    def get_schema(self) -> str:
        """Retorna o esquema de todas as tabelas para alimentar o contexto do Agente."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        schema_info = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            cols_str = ", ".join([f"{c['name']} ({c['type']})" for c in columns])
            schema_info.append(f"Table {table}: {cols_str}")
        
        conn.close()
        return "\n".join(schema_info)

db = Database()
