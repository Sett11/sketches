"""
Конфигурация парсера из переменных окружения
"""
import os
from pathlib import Path


class Config:
    """Конфигурация приложения"""
    
    # API настройки
    API_KEY = os.getenv('API_KEY', '997834c96856bb3783da8c42a59d06b3')
    API_URL = os.getenv('API_URL', 'https://service.api-assist.com/parser/ras_arbitr_api/')
    API_STAT_URL = os.getenv('API_STAT_URL', 'https://service.api-assist.com/stat/')
    SEARCH_TEXT = os.getenv('SEARCH_TEXT', "'решение'")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Лимиты
    MAX_REQUESTS_PER_RUN = int(os.getenv('MAX_REQUESTS_PER_RUN', '500'))
    DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', '1'))
    SELENIUM_TIMEOUT = int(os.getenv('SELENIUM_TIMEOUT', '240'))
    RETRY_LIMIT = int(os.getenv('RETRY_LIMIT', '2'))
    BASE_DELAY_SEC = int(os.getenv('BASE_DELAY_SEC', '10'))
    JITTER_SEC = int(os.getenv('JITTER_SEC', '3'))
    LONG_PAUSE_EVERY = int(os.getenv('LONG_PAUSE_EVERY', '5'))
    LONG_PAUSE_MIN = int(os.getenv('LONG_PAUSE_MIN', '40'))
    LONG_PAUSE_MAX = int(os.getenv('LONG_PAUSE_MAX', '90'))
    PREWARM_EVERY = int(os.getenv('PREWARM_EVERY', '3'))
    
    # Критерии фильтрации
    FILTER_INSTANCE_LEVEL_MIN = int(os.getenv('FILTER_INSTANCE_LEVEL_MIN', '1'))
    FILTER_EXCLUDE_TYPE = os.getenv('FILTER_EXCLUDE_TYPE', 'Определение')
    
    # Пути
    DATA_DIR = Path(os.getenv('DATA_DIR', '/app/data'))
    METADATA_DIR = Path(os.getenv('METADATA_DIR', '/app/data/metadata'))
    PDFS_DIR = Path(os.getenv('PDFS_DIR', '/app/data/pdfs'))
    STATE_DIR = Path(os.getenv('STATE_DIR', '/app/data/state'))
    LOGS_DIR = Path(os.getenv('LOGS_DIR', '/app/data/logs'))
    DB_PATH = Path(os.getenv('DB_PATH', '/app/data/state/database.db'))
    
    # URL КАД Арбитр
    KAD_URL = "https://kad.arbitr.ru/"
    
    # Создаём директории сразу при импорте модуля
    @classmethod
    def _ensure_directories(cls):
        """Создание необходимых директорий"""
        for directory in [cls.METADATA_DIR, cls.PDFS_DIR, cls.STATE_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Проверка обязательных параметров"""
        if not cls.API_KEY:
            raise ValueError("API_KEY не установлен!")
        
        # Создаём директории
        cls._ensure_directories()


# Создаём директории при импорте модуля (до инициализации логирования)
Config._ensure_directories()

