import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    filename: str

    postgres_host: str
    postgres_user: str
    postgres_pass: str
    postgres_port: int
    postgres_db: str
    postgres_timeout: int

    langsmith_project: str
    langsmith_api_key: str
    langchain_tracing_v2: str

    openrouter_api_key: str
    

def get_config() -> Config:
    return Config()


app_config = get_config()

os.environ["OPENROUTER_API_KEY"] = app_config.openrouter_api_key
os.environ["LANGCHAIN_TRACING_V2"] = app_config.langchain_tracing_v2
os.environ["LANGSMITH_API_KEY"] = app_config.langsmith_api_key
os.environ["LANGSMITH_PROJECT"] = app_config.langsmith_project