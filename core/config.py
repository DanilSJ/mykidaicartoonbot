from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN', default='None')

    AI_API_KEY: str = os.getenv('AI_API_KEY', default='None')

    PLATEGA_BASE_URL: str = os.getenv('PLATEGA_BASE_URL', default='None')
    PLATEGA_MERCHANT_ID: str = os.getenv('PLATEGA_MERCHANT_ID', default='None')
    PLATEGA_SECRET: str = os.getenv('PLATEGA_SECRET', default='None')

    DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3"
    DB_ECHO: bool = os.getenv("DB_ECHO", "False") == "True"
    DB_POOL_NULL: bool = os.getenv("DB_POOL_NULL", "False") == "True"


settings = Settings()