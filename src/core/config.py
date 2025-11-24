import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    pdf_filename: str
    tabular_filename: str

    postgres_host: str
    postgres_user: str
    postgres_pass: str
    postgres_port: int
    postgres_db: str
    postgres_timeout: int

    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str

    openrouter_api_key: str

    pdf_vector_table_name: str
    tabular_table_name: str

    langsmith_api_key: str
    langsmith_project: str
    langchain_tracing_v2: str
    

def get_config() -> Config:
    return Config()


app_config = get_config()

os.environ["OPENROUTER_API_KEY"] = app_config.openrouter_api_key
os.environ["LANGFUSE_SECRET_KEY"] = app_config.langfuse_secret_key
os.environ["LANGFUSE_PUBLIC_KEY"] = app_config.langfuse_public_key
os.environ["LANGFUSE_BASE_URL"] = app_config.langfuse_base_url

os.environ["LANGSMITH_API_KEY"] = app_config.langsmith_api_key
os.environ["LANGSMITH_PROJECT"] = app_config.langsmith_project
os.environ["LANGCHAIN_TRACING_V2"] = app_config.langchain_tracing_v2