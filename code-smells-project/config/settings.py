import os

SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
AMBIENTE = os.environ.get("APP_ENV", "producao")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
TOKEN_MAX_AGE_SECONDS = int(os.environ.get("TOKEN_MAX_AGE_SECONDS", "28800"))


def validar():
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY não definida. Veja o .env.example")
