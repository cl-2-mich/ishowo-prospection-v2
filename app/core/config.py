from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/ishowo_prospects"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    SERP_API_KEY: str = ""
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()