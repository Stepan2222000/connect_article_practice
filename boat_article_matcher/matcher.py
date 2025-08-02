import pandas as pd
from loguru import logger
from typing import List, Dict, Any, Tuple
from pathlib import Path

from config import Config
from utils import normalize_text
from db import DatabaseManager


class ArticleMatcher:
    def __init__(self, config: Config):
        self.config = config
        self.articles_data: Dict[str, List[str]] = {}
    
    def load_csv_data(self):
        data_dir = Path("data")
        csv_files = ["boats_net_data.csv", "partzilla_net_data.csv"]
        
        for csv_file in csv_files:
            csv_path = data_dir / csv_file
            if csv_path.exists():
                logger.info(f"Загрузка CSV файла: {csv_file}")
            else:
                logger.warning(f"CSV файл не найден: {csv_file}")
    
    def process_csv_data(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    
    def find_brands_in_text(self, text: str) -> List[str]:
        pass
    
    def find_articles_in_text(self, text: str, brand: str) -> List[str]:
        pass
    
    async def process_texts(self, db_manager: DatabaseManager) -> List[Dict[str, Any]]:
        pass