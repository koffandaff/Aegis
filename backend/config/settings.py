"""
Application Settings and Configuration
"""
import os
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Fsociety Cybersecurity Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/fsociety.db")
    
    # AI/Ollama
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Scanning
    MAX_SCAN_TIMEOUT: int = 30  # seconds
    DEFAULT_RATE_LIMIT: int = 10  # requests per minute
    MAX_CONCURRENT_SCANS: int = 5
    
    # SSL/TLS Scanning
    SSL_SCAN_TIMEOUT: int = 10
    TLS_VERSIONS_TO_CHECK: List[str] = Field(default=["TLSv1.0", "TLSv1.1", "TLSv1.2", "TLSv1.3"])
    
    # Phishing Detection
    PHISHING_THRESHOLD: float = 0.7  # Score above which URL is considered phishing
    SUSPICIOUS_TLDS: List[str] = Field(default=[".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".loan", ".win"])
    SUSPICIOUS_KEYWORDS: List[str] = Field(default=["login", "secure", "account", "verify", "update", "banking", "paypal"])
    
    # File Analysis
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_HASH_TYPES: List[str] = Field(default=["md5", "sha1", "sha256", "sha512"])
    LOCAL_MALWARE_DB_PATH: str = "data/malware_hashes.json"
    
    # VirusTotal (Optional - requires API key)
    VIRUSTOTAL_API_KEY: Optional[str] = os.getenv("VT_KEY") or os.getenv("VIRUSTOTAL_API_KEY")
    VIRUSTOTAL_ENABLED: bool = True  # Auto-enabled if key exists
    VIRUSTOTAL_RATE_LIMIT: int = 4  # requests per minute for public API
    
    # Caching
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = 3600  # 1 hour in seconds
    MAX_CACHE_SIZE: int = 1000  # entries
    
    # User Agent for scanning
    USER_AGENT: str = "Fsociety-Security-Scanner/1.0 (+https://github.com/fsociety)"
    
    # Pydantic v2 Settings Configuration
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": "",  # No prefix for environment variables
        "extra": "ignore"  # Ignore extra fields in environment
    }
    
    @validator('DEBUG', pre=True)
    def parse_debug(cls, v):
        """Parse DEBUG from string to boolean"""
        if isinstance(v, str):
            return v.lower() == "true"
        return v
    
    @validator('VIRUSTOTAL_ENABLED', pre=True)
    def parse_virustotal_enabled(cls, v):
        """Parse VIRUSTOTAL_ENABLED from string to boolean"""
        if isinstance(v, str):
            return v.lower() == "true"
        return v
    
    @validator('CACHE_ENABLED', pre=True)
    def parse_cache_enabled(cls, v):
        """Parse CACHE_ENABLED from string to boolean"""
        if isinstance(v, str):
            return v.lower() == "true"
        return v

settings = Settings()