"""Configurações do projeto via pydantic-settings."""
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

LLMProvider = Literal["groq", "openrouter", "gemini", "openai", "ollama"]


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    LLM_PROVIDER: LLMProvider = "groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_HOST: str = "http://localhost:11434"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "open-energy"

    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"
    EMBEDDING_DEVICE: str = "cpu"

    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    CHUNK_SIZE_TOKENS: int = 300
    CHUNK_OVERLAP_TOKENS: int = 40

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"


settings = _Settings()
