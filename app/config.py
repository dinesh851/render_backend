from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Doctor Appointment API"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is required in .env file")
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY is required in .env file")