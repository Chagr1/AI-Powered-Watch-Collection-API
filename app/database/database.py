import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. FIND THE EXACT PATH TO THE ROOT DIRECTORY AND FORCE LOAD .ENV
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)

# 2. FETCH THE DATABASE URL DIRECTLY FROM THE OS (BYPASSING CACHED SETTINGS)
ACTUAL_DATABASE_URL = os.getenv("DATABASE_URL")

print(f"\n=== FORCED CLOUD DATABASE CONNECTION ===\nURL: {ACTUAL_DATABASE_URL}\n")

# 3. INITIALIZE THE ENGINE BASED ON THE URL TYPE
if ACTUAL_DATABASE_URL and ACTUAL_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        ACTUAL_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(ACTUAL_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()