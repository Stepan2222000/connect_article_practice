import asyncpg
from loguru import logger
from typing import List, Dict, Any, Optional
from config import Config


class DatabaseManager:
    def __init__(self, config: Config):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.config.db_url)
            logger.info("Подключение к базе данных установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Соединение с базой данных закрыто")
    
    async def load_text_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        pass
    
    async def upsert_matches(self, matches: List[Dict[str, Any]]):
        pass