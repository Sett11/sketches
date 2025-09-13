"""
Простая система логирования
"""
import logging
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import LOGS_DIR, ensure_dirs

def setup_logger(name="arbitr_parser", level=logging.INFO):
    """Настройка простого логгера"""
    
    # Убеждаемся, что директории созданы
    ensure_dirs()
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Если уже настроен, обновляем существующие обработчики
    if logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(level)
            handler.setFormatter(formatter)
        return logger
    
    # Консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый handler
    # Дополнительная проверка создания директории
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = os.path.join(LOGS_DIR, f"parser_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger()
