import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "todolist_db"
    SECRET_KEY: str = "e83a45a30a7d519b5d2bbde4be3db88e5d3c8c7bb86de27d096a605f2c4187f5"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    HF_TOKEN: str = "your_hugging_face_api_token_here"
    HF_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_gmail_app_password"
    FRONTEND_URL: str = "http://localhost:5173"
    GOOGLE_CLIENT_ID: str = ""

    class Config:
        # Resolve the relative path to backend/.env
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        extra = "ignore"

settings = Settings()
