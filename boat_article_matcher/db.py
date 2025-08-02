import asyncpg
import asyncio
from loguru import logger
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

try:
    from .config import config
except ImportError:
    from config import config


class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._retry_attempts = 3
        self._retry_delay = 1
    
    async def connect(self):
        for attempt in range(self._retry_attempts):
            try:
                self.pool = await asyncpg.create_pool(config.db_url)
                logger.info("Подключение к базе данных установлено")
                return
            except Exception as e:
                logger.error(f"Ошибка подключения к базе данных (попытка {attempt + 1}/{self._retry_attempts}): {e}")
                if attempt == self._retry_attempts - 1:
                    logger.error("Не удалось подключиться к базе данных после всех попыток")
                    raise
                await asyncio.sleep(self._retry_delay)
    
    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Соединение с базой данных закрыто")
    
    async def ensure_table_exists(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS article_matches (
            id INTEGER REFERENCES special_model_data(id) PRIMARY KEY,
            first_article TEXT,
            first_brand TEXT,
            all_articles TEXT[],
            all_brands TEXT[],
            processed BOOLEAN DEFAULT FALSE,
            normalized_text TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_article_matches_processed ON article_matches(processed);
        """
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(create_table_sql)
                logger.info("Таблица article_matches создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка создания таблицы article_matches: {e}")
            raise
    
    async def load_text_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit is None:
            limit = config.TEXT_LIMIT
        
        if limit and limit <= 0:
            limit = None
            
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT id, description, characteristics 
        FROM text_model_data 
        ORDER BY id
        {limit_clause}
        """
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query)
                result = [dict(row) for row in rows]
                logger.info(f"Загружено {len(result)} записей из text_model_data")
                return result
        except Exception as e:
            logger.error(f"Ошибка загрузки данных из text_model_data: {e}")
            raise
    
    async def load_combined_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit is None:
            limit = config.TEXT_LIMIT
        
        if limit and limit <= 0:
            limit = None
            
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT 
            s.id,
            s.title,
            t.description,
            t.characteristics
        FROM special_model_data s
        JOIN text_model_data t ON s.id = t.id
        ORDER BY s.id
        {limit_clause}
        """
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query)
                
                combined_data = []
                for row in rows:
                    title = row['title'] or ''
                    description = row['description'] or ''
                    characteristics = row['characteristics'] or ''
                    
                    combined_text = f"{title} {description} {characteristics}".strip()
                    
                    combined_data.append({
                        'id': row['id'],
                        'title': title,
                        'description': description,
                        'characteristics': characteristics,
                        'combined_text': combined_text
                    })
                
                logger.info(f"Загружено и объединено {len(combined_data)} записей")
                return combined_data
                
        except Exception as e:
            logger.error(f"Ошибка загрузки объединенных данных: {e}")
            raise

    async def upsert_match(self, match_data: Dict[str, Any]):
        upsert_sql = """
        INSERT INTO article_matches (
            id, first_article, first_brand, all_articles, all_brands, 
            processed, normalized_text
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            first_article = EXCLUDED.first_article,
            first_brand = EXCLUDED.first_brand,
            all_articles = EXCLUDED.all_articles,
            all_brands = EXCLUDED.all_brands,
            processed = EXCLUDED.processed,
            normalized_text = EXCLUDED.normalized_text
        """
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    upsert_sql,
                    match_data['id'],
                    match_data.get('first_article'),
                    match_data.get('first_brand'),
                    match_data.get('all_articles', []),
                    match_data.get('all_brands', []),
                    match_data.get('processed', True),
                    match_data.get('normalized_text', '')
                )
                logger.debug(f"Сохранена запись с ID {match_data['id']}")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения записи {match_data.get('id')}: {e}")
            raise

    async def upsert_matches(self, matches: List[Dict[str, Any]]):
        if not matches:
            logger.info("Нет данных для сохранения")
            return
            
        upsert_sql = """
        INSERT INTO article_matches (
            id, first_article, first_brand, all_articles, all_brands, 
            processed, normalized_text
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            first_article = EXCLUDED.first_article,
            first_brand = EXCLUDED.first_brand,
            all_articles = EXCLUDED.all_articles,
            all_brands = EXCLUDED.all_brands,
            processed = EXCLUDED.processed,
            normalized_text = EXCLUDED.normalized_text
        """
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    for match_data in matches:
                        await conn.execute(
                            upsert_sql,
                            match_data['id'],
                            match_data.get('first_article'),
                            match_data.get('first_brand'),
                            match_data.get('all_articles', []),
                            match_data.get('all_brands', []),
                            match_data.get('processed', True),
                            match_data.get('normalized_text', '')
                        )
                        
                logger.info(f"Массово сохранено {len(matches)} записей")
                
        except Exception as e:
            logger.error(f"Ошибка массового сохранения записей: {e}")
            raise
    
    async def check_connection(self) -> bool:
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                if result == 1:
                    logger.info("Соединение с базой данных работает")
                    return True
                else:
                    logger.error("Неожиданный результат проверки соединения")
                    return False
        except Exception as e:
            logger.error(f"Ошибка проверки соединения с базой данных: {e}")
            return False
    
    async def count_processed_records(self) -> int:
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval("SELECT COUNT(*) FROM article_matches WHERE processed = TRUE")
                logger.info(f"Количество обработанных записей: {count}")
                return count
        except Exception as e:
            logger.error(f"Ошибка подсчета обработанных записей: {e}")
            raise
    
    async def reset_processed_flags(self):
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("UPDATE article_matches SET processed = FALSE")
                affected_rows = int(result.split()[-1])
                logger.info(f"Сброшены флаги обработки для {affected_rows} записей")
                return affected_rows
        except Exception as e:
            logger.error(f"Ошибка сброса флагов обработки: {e}")
            raise
    
    async def __aenter__(self):
        await self.connect()
        await self.ensure_table_exists()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        if exc_type:
            logger.error(f"Ошибка в контексте DatabaseManager: {exc_val}")
        return False


@asynccontextmanager
async def get_db_manager():
    db_manager = DatabaseManager()
    try:
        await db_manager.connect()
        await db_manager.ensure_table_exists()
        yield db_manager
    finally:
        await db_manager.close()