from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GovSwarm AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "SUPERSECRETKEY123"
    JWT_SECRET: str = "SUPERSECRETKEY123"
    
    # Database
    DATABASE_URL: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Redis & Celery
    REDIS_URL: str
    CELERY_BROKER_URL: str

    model_config = SettingsConfigDict(env_file="apps/backend/.env", extra="ignore")

settings = Settings()
