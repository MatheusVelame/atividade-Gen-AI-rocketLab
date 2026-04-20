from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DATABASE_URL: str = "sqlite:///./banco.db"
    MODEL_NAME: str = "gemini-2.0-flash-lite"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
