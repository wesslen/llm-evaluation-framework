"""Configuration management for the LLM evaluation framework."""

import os
from typing import Optional
from pydantic import SecretStr, AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(protected_namespaces=('settings_',))
    
    # API Configuration
    api_base_url: AnyHttpUrl
    api_key: SecretStr
    llm_model_name: str  # Changed from model_name to avoid namespace conflict
    
    # Database Configuration
    database_url: str = "sqlite:///database/llm_evaluation.db"
    
    # Test Configuration
    test_timeout: int = 30  # seconds
    max_retries: int = 3
    retry_delay: int = 1  # seconds

# Global settings instance
settings = Settings(
    api_base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
    api_key=os.getenv("API_KEY", ""),
    llm_model_name=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
)