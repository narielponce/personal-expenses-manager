from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"  # TODO: Change this to a strong, randomly generated key in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://user:password@db:5432/personal_expense_manager" # TODO: Configure in docker-compose

    class Config:
        if os.getenv("ENV") != "docker":
            env_file = ".env"

settings = Settings()
