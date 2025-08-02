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