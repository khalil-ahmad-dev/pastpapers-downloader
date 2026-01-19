"""
Application configuration settings.
"""
import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings."""
    
    # Application
    APP_NAME: str = "PastPapersDownloader"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    TEMP_DOWNLOAD_DIR: Path = BASE_DIR / "temp_downloads"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    
    # Download Settings
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "15"))
    DOWNLOAD_TIMEOUT: int = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
    CLEANUP_TTL_HOURS: int = int(os.getenv("CLEANUP_TTL_HOURS", "1"))
    
    # PapaCambridge URLs
    PAPACAMBRIDGE_BASE_URL: str = "https://pastpapers.papacambridge.com"
    AICE_URL: str = f"{PAPACAMBRIDGE_BASE_URL}/papers/caie/as-and-a-level"
    IGCSE_URL: str = f"{PAPACAMBRIDGE_BASE_URL}/papers/caie/igcse"
    O_LEVEL_URL: str = f"{PAPACAMBRIDGE_BASE_URL}/papers/caie/o-level"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Create necessary directories
settings.TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
