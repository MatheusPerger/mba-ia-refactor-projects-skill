import os

from dotenv import load_dotenv


class Settings:
    def __init__(self, env):
        self.SECRET_KEY = env.get('SECRET_KEY')
        if not self.SECRET_KEY:
            raise RuntimeError('SECRET_KEY não definido. Copie .env.example para .env e preencha.')
        self.DATABASE_URI = env.get('DATABASE_URI', 'sqlite:///tasks.db')
        self.HOST = env.get('HOST', '127.0.0.1')
        self.PORT = int(env.get('PORT', '5001'))
        self.DEBUG = env.get('DEBUG', 'false').lower() == 'true'
        self.LOG_LEVEL = env.get('LOG_LEVEL', 'INFO').upper()
        self.TOKEN_MAX_AGE_SECONDS = int(env.get('TOKEN_MAX_AGE_SECONDS', '28800'))
        self.EMAIL_HOST = env.get('EMAIL_HOST', 'smtp.gmail.com')
        self.EMAIL_PORT = int(env.get('EMAIL_PORT', '587'))
        self.EMAIL_USER = env.get('EMAIL_USER', '')
        self.EMAIL_PASSWORD = env.get('EMAIL_PASSWORD', '')

    @classmethod
    def from_env(cls):
        load_dotenv()
        return cls(os.environ)
