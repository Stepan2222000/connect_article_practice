import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class Config:
    VALID_BRANDS = os.getenv('VALID_BRANDS', 'YAMAHA,KAWASAKI,SUZUKI').split(',')
    MIN_ARTICLE_LEN_DIGITS = int(os.getenv('MIN_ARTICLE_LEN_DIGITS', '5'))
    MIN_ARTICLE_LEN_ALPHANUM = int(os.getenv('MIN_ARTICLE_LEN_ALPHANUM', '6'))
    TEXT_LIMIT = int(os.getenv('TEXT_LIMIT', '0')) or None
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'boat_parts')
    DB_USER = os.getenv('DB_USER', 'username')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    @property
    def db_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"