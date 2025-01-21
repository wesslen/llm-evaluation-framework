"""Configuration management for the LLM evaluation framework."""

import os
from typing import Optional
from pydantic import SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_base_url: AnyHttpUrl
    api_key: SecretStr
    model_name: str  # Changed from llm_model_name to match env var
    
    # Database Configuration
    database_url: str
    
    # Test Configuration
    test_timeout: int = 30  # seconds
    max_retries: int = 3
    retry_delay: int = 1  # seconds

    model_config = {
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'protected_namespaces': ('settings_',)
    }

# Global settings instance
settings = Settings(
    api_base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"],
    model_name=os.environ["MODEL_NAME"],  # Changed to match the class attribute
    database_url=os.environ.get("DATABASE_URL", "sqlite:///database/llm_evaluation.db"),
)