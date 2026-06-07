"""Конфигурация Flask-приложения."""

import os
from pathlib import Path

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# Секретный ключ для сессий и CSRF (в продакшене задать через переменную окружения)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# База данных SQLite
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_DIR / 'app.db'}",
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Учётные данные администратора (по умолчанию; переопределить через env)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# Логирование
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

# FAQ-ассистент (FastAPI backend)
CHAT_API_URL = os.environ.get("CHAT_API_URL", "http://127.0.0.1:8000")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "")
