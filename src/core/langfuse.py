from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from src.core.config import app_config


class LangfuseConfig:
    
    def __init__(self):
        self._client: Langfuse
        self._callback: CallbackHandler

    def setup(self):
        self._client = Langfuse(
            secret_key=app_config.langfuse_secret_key,
            public_key=app_config.langfuse_public_key,
            host=app_config.langfuse_base_url,
        )

        self._callback = CallbackHandler(
            public_key=app_config.langfuse_public_key,
        )