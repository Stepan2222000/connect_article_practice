import os
from dotenv import load_dotenv
from loguru import logger
import sys


def load_env_file():
    if not load_dotenv():
        logger.error("Не удалось загрузить .env файл")
        sys.exit(1)


load_env_file()


class Config:
    def __init__(self):
        self._validate_required_params()
        
    def _validate_required_params(self):
        required_params = ['DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_params = []
        
        for param in required_params:
            if not os.getenv(param):
                missing_params.append(param)
        
        if missing_params:
            logger.error(f"Отсутствуют обязательные параметры в .env: {', '.join(missing_params)}")
            sys.exit(1)
    
    @property
    def VALID_BRANDS(self):
        brands = os.getenv('VALID_BRANDS', 'YAMAHA,KAWASAKI,SUZUKI').split(',')
        return [brand.strip() for brand in brands]
    
    @property
    def MIN_ARTICLE_LEN_DIGITS(self):
        try:
            return int(os.getenv('MIN_ARTICLE_LEN_DIGITS', '5'))
        except ValueError:
            logger.error("MIN_ARTICLE_LEN_DIGITS должен быть числом")
            sys.exit(1)
    
    @property
    def MIN_ARTICLE_LEN_ALPHANUM(self):
        try:
            return int(os.getenv('MIN_ARTICLE_LEN_ALPHANUM', '6'))
        except ValueError:
            logger.error("MIN_ARTICLE_LEN_ALPHANUM должен быть числом")
            sys.exit(1)
    
    @property
    def TEXT_LIMIT(self):
        try:
            limit = os.getenv('TEXT_LIMIT', '0')
            return int(limit) if limit and int(limit) > 0 else None
        except ValueError:
            logger.error("TEXT_LIMIT должен быть числом")
            sys.exit(1)
    
    @property
    def DB_HOST(self):
        return os.getenv('DB_HOST', 'localhost')
    
    @property
    def DB_PORT(self):
        try:
            return int(os.getenv('DB_PORT', '5432'))
        except ValueError:
            logger.error("DB_PORT должен быть числом")
            sys.exit(1)
    
    @property
    def DB_NAME(self):
        return os.getenv('DB_NAME')
    
    @property
    def DB_USER(self):
        return os.getenv('DB_USER')
    
    @property
    def DB_PASSWORD(self):
        return os.getenv('DB_PASSWORD')
    
    @property
    def db_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


config = Config()