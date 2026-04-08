import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Security Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Production-grade AI-powered security platform for detecting fake apps, clone apps, malware, phishing, and suspicious applications"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./security_platform.db")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-32chars-min")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS: List[str] = [".apk", ".xapk", ".aab", ".exe", ".dll", ".so", ".dylib"]
    
    # Analysis
    SANDBOX_TIMEOUT: int = 300  # 5 minutes
    MAX_CONCURRENT_SCANS: int = 10
    STATIC_ANALYSIS_ENABLED: bool = True
    DYNAMIC_ANALYSIS_ENABLED: bool = True
    ML_DETECTION_ENABLED: bool = True
    
    # ML Model Paths
    MALWARE_MODEL_PATH: str = "models/malware_detector.pkl"
    CLONE_MODEL_PATH: str = "models/clone_detector.pkl"
    PHISHING_MODEL_PATH: str = "models/phishing_detector.pkl"
    RISK_MODEL_PATH: str = "models/risk_scorer.pkl"
    
    # Threat Intelligence
    VIRUSTOTAL_API_KEY: Optional[str] = os.getenv("VIRUSTOTAL_API_KEY")
    ABUSEIPDB_API_KEY: Optional[str] = os.getenv("ABUSEIPDB_API_KEY")
    SHODAN_API_KEY: Optional[str] = os.getenv("SHODAN_API_KEY")
    
    # Monitoring
    ENABLE_REALTIME_MONITORING: bool = True
    MONITORING_INTERVAL: int = 5  # seconds
    NETWORK_CAPTURE_ENABLED: bool = True
    
    # Clone Detection
    CLONE_SIMILARITY_THRESHOLD: float = 0.85
    ICON_SIMILARITY_THRESHOLD: float = 0.90
    CODE_SIMILARITY_THRESHOLD: float = 0.75
    
    # Risk Scoring
    HIGH_RISK_THRESHOLD: int = 80
    MEDIUM_RISK_THRESHOLD: int = 50
    LOW_RISK_THRESHOLD: int = 20
    
    # Incident Management
    AUTO_TAKEDOWN_ENABLED: bool = False
    SLA_HOURS_HIGH: int = 4
    SLA_HOURS_MEDIUM: int = 24
    SLA_HOURS_LOW: int = 72
    
    # Federated Learning
    FEDERATED_ENABLED: bool = False
    FEDERATED_AGGREGATION_INTERVAL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
