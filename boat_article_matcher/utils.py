from loguru import logger
import sys


def setup_logging():
    logger.remove()
    
    logger.add(
        "logs/matcher.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )
    
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}"
    )
    
    logger.info("Логирование настроено")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.upper()
    
    cyrillic_to_latin = {
        'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'Н': 'H', 'К': 'K', 
        'М': 'M', 'О': 'O', 'Р': 'P', 'Т': 'T', 'У': 'Y', 'Х': 'X'
    }
    
    for cyrillic, latin in cyrillic_to_latin.items():
        text = text.replace(cyrillic, latin)
    
    text = text.replace('-', '')
    
    return text


def normalize_article(article: str) -> str:
    return normalize_text(article)


def normalize_brand(brand: str) -> str:
    return normalize_text(brand)


def is_only_digits(text: str) -> bool:
    return text.isdigit()


def validate_article_length(article: str) -> bool:
    try:
        from .config import config
    except ImportError:
        from config import config
    
    if not article:
        return False
    
    if is_only_digits(article):
        return len(article) >= config.MIN_ARTICLE_LEN_DIGITS
    else:
        return len(article) >= config.MIN_ARTICLE_LEN_ALPHANUM


def validate_brand(brand: str) -> bool:
    try:
        from .config import config
    except ImportError:
        from config import config
    
    if not brand:
        return False
    
    normalized_brand = normalize_brand(brand)
    normalized_valid_brands = [normalize_brand(b) for b in config.VALID_BRANDS]
    
    return normalized_brand in normalized_valid_brands


def remove_duplicates(data: list) -> list:
    if not data:
        return []
    
    seen = set()
    unique_data = []
    
    for item in data:
        if isinstance(item, dict) and 'article' in item and 'brand' in item:
            normalized_article = normalize_article(item['article'])
            normalized_brand = normalize_brand(item['brand'])
            key = (normalized_article, normalized_brand)
            
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        else:
            item_key = str(item)
            if item_key not in seen:
                seen.add(item_key)
                unique_data.append(item)
    
    return unique_data


def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.strip()
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    while '  ' in text:
        text = text.replace('  ', ' ')
    
    return text


def split_and_clean_string(text: str, delimiter: str = ',') -> list:
    if not text:
        return []
    
    parts = text.split(delimiter)
    return [clean_text(part) for part in parts if clean_text(part)]