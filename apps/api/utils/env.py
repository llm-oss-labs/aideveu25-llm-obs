"""
Environment configuration management for the LLM API.
Handles loading and validation of environment variables.
"""
import os
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Provider Configuration
    llm_provider: Literal["ollama", "azure"] = Field(
        default="ollama", 
        env="LLM_PROVIDER",
        description="LLM provider to use (ollama or azure)"
    )
    
    # Ollama Configuration
    ollama_model: str = Field(
        default="phi3", 
        env="OLLAMA_MODEL",
        description="Ollama model name"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434", 
        env="OLLAMA_BASE_URL",
        description="Ollama server base URL"
    )
    
    # Azure OpenAI Configuration
    azure_openai_model: str = Field(
        default="gpt-4o-mini", 
        env="AZURE_OPENAI_MODEL",
        description="Azure OpenAI model name"
    )
    azure_openai_endpoint: str = Field(
        default="", 
        env="AZURE_OPENAI_ENDPOINT",
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: str = Field(
        default="", 
        env="AZURE_OPENAI_API_KEY",
        description="Azure OpenAI API key"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview", 
        env="AZURE_OPENAI_API_VERSION",
        description="Azure OpenAI API version"
    )
    
    # Application Configuration
    log_level: str = Field(
        default="INFO", 
        env="LOG_LEVEL",
        description="Logging level"
    )
    app_host: str = Field(
        default="0.0.0.0", 
        env="APP_HOST",
        description="Application host"
    )
    app_port: int = Field(
        default=8000, 
        env="APP_PORT",
        description="Application port"
    )
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


def validate_provider_config(settings: Settings) -> None:
    """Validate that required configuration is present for the selected provider."""
    if settings.llm_provider == "azure":
        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required when using Azure provider")
        if not settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required when using Azure provider")
    elif settings.llm_provider == "ollama":
        if not settings.ollama_base_url:
            raise ValueError("OLLAMA_BASE_URL is required when using Ollama provider")
        if not settings.ollama_model:
            raise ValueError("OLLAMA_MODEL is required when using Ollama provider")
