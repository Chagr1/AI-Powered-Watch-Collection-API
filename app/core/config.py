import os
from pathlib import Path
from dotenv import load_dotenv

# 1. GET THE EXACT PATH TO THE ROOT FOLDER (app/core/config.py -> app/core -> app -> root)
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = BASE_DIR / ".env"

# 2. FORCE LOAD THE .ENV FILE BEFORE PYDANTIC INITIALIZES
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)

# 3. YOUR PYDANTIC IMPORTS AND SETTINGS CLASS CONTINUE HERE...
# from pydantic_settings import BaseSettings ...

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    DATABASE_URL: str = "sqlite:///./watch_collection.db"


    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


settings = Settings()

if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from the .env file.")