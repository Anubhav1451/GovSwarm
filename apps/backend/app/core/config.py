from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GovSwarm AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file="apps/backend/.env", extra="ignore")

settings = Settings()
