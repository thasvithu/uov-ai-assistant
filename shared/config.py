"""
Shared configuration management for UoV AI Assistant.

This module loads and validates all environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Supabase Configuration
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon/service key")
    
    # Qdrant Configuration
    qdrant_url: str = Field(..., description="Qdrant instance URL")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key (optional for local)")
    qdrant_collection_name: str = Field(
        default="faculty_documents",
        description="Qdrant collection name"
    )
    
    # Groq API Configuration
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model: str = Field(
        default="llama-3.1-70b-versatile",
        description="Groq model name"
    )
    
    # Embedding Model Configuration
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-base",
        description="HuggingFace embedding model"
    )
    embedding_dimension: int = Field(
        default=768,
        description="Embedding vector dimension"
    )
    
    # Chunking Configuration
    chunk_size: int = Field(
        default=512,
        description="Maximum tokens per chunk",
        ge=100,
        le=512
    )
    chunk_overlap: int = Field(
        default=50,
        description="Overlap between chunks in tokens",
        ge=0,
        le=100
    )
    
    # Retrieval Configuration
    top_k_retrieval: int = Field(
        default=10,
        description="Number of chunks to retrieve",
        ge=1,
        le=20
    )
    similarity_threshold: float = Field(
        default=0.5,
        description="Minimum similarity score for retrieval",
        ge=0.0,
        le=1.0
    )
    
    # LLM Configuration
    llm_temperature: float = Field(
        default=0.3,
        description="LLM temperature for generation",
        ge=0.0,
        le=2.0
    )
    llm_max_tokens: int = Field(
        default=1024,
        description="Maximum tokens for LLM response",
        ge=100,
        le=4096
    )
    
    # Application Configuration
    backend_host: str = Field(default="0.0.0.0", description="Backend host")
    backend_port: int = Field(default=8000, description="Backend port", ge=1, le=65535)
    streamlit_port: int = Field(default=8501, description="Streamlit port", ge=1, le=65535)
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()



# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings: Application settings
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment.
    
    Returns:
        Settings: Reloaded application settings
    """
    global _settings
    _settings = Settings()
    return _settings


# Convenience function for direct import
settings = get_settings()
