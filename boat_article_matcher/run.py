import asyncio
from loguru import logger

from utils import setup_logging
from config import Config
from db import DatabaseManager
from matcher import ArticleMatcher


async def main():
    setup_logging()
    logger.info("Запуск системы поиска артикулов")
    
    config = Config()
    db_manager = DatabaseManager(config)
    matcher = ArticleMatcher(config)
    
    try:
        await db_manager.connect()
        
        matcher.load_csv_data()
        
        matches = await matcher.process_texts(db_manager)
        
        logger.info("Обработка завершена успешно")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())