"""
Centralized application configuration using Pydantic's BaseSettings.

This module defines a `Settings` class that loads configuration values from
environment variables and a `.env` file. This approach keeps configuration
separate from code, following the 12-factor app methodology.

The `settings` object is a singleton instance of this class and should be
imported by other modules that need access to configuration values.
"""
from typing import List, Union

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings class.
    Values are loaded from environment variables or a .env file.
    """
    # --- Core API Settings ---
    PROJECT_NAME: str = "StaffAlloc Local-First Prototype"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = """
    API for the StaffAlloc platform, designed for a local-first prototype.
    Manages projects, employees, allocations, and AI-driven features.
    """
    API_V1_STR: str = "/api/v1"

    # --- Database Configuration ---
    # The URL for the application's database. For the local prototype, this
    # defaults to a synchronous SQLite database file in the `data/` directory.
    # Changed from aiosqlite to sync sqlite for simplicity.
    DATABASE_URL: str = "sqlite:///./data/staffalloc.db"
    
    # Derived path for database file (for directory creation)
    SQLITE_DB_PATH: str = "./data/staffalloc.db"

    # --- Security and JWT Settings ---
    # A secret key for signing JWTs.
    # IMPORTANT: This is a default value for development. In production, this
    # should be replaced with a strong, randomly generated secret and loaded
    # from a secure source (e.g., environment variable, secrets manager).
    # You can generate a new one with: `openssl rand -hex 32`
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # --- CORS (Cross-Origin Resource Sharing) Settings ---
    # A list of origins that are allowed to make cross-origin requests.
    # The default includes the standard local development ports for React/Vite.
    # Use ["*"] to allow all origins (less secure).
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = [
        "http://localhost:5173",  # Default Vite/React dev server
        "http://localhost:3000",  # Common alternative for React
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # --- Local Storage Paths ---
    # As per the architecture document, all data is stored locally.
    REPORTS_DIR: str = "./data/reports"
    VECTOR_STORE_DIR: str = "./data/vector_store"
    
    # Aliases for compatibility
    REPORTS_PATH: str = "./data/reports"
    VECTOR_STORE_PATH: str = "./data/vector_store"

    # --- AI and LLM Integration Settings ---
    # The base URL for the locally running Ollama server.
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Alias for API endpoint
    OLLAMA_API_URL: str = "http://localhost:11434"
    
    # The name of the sentence-transformer model to use for embeddings in the RAG pipeline.
    # 'all-MiniLM-L6-v2' is a good default: fast, effective, and runs locally.
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    # The name of the LLM model to use for chat and generation via Ollama.
    # 'phi3:mini' is a small, fast model suitable for real-time interaction.
    LLM_MODEL_NAME: str = "phi3:mini"

    # Pydantic settings configuration
    # This tells Pydantic to look for a .env file and treat variable names
    # as case-insensitive.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )


# Create a single, globally accessible instance of the Settings class.
# Other modules should import this `settings` object.
settings = Settings()

