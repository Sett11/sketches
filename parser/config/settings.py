"""
Простая конфигурация для парсера арбитражных дел
"""
import os
from datetime import datetime, timedelta

# Базовые настройки
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Создаем папки если их нет
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Настройки парсинга
PARSING_SETTINGS = {
    "items_per_page": 25,
    "max_pages": 40,
    "max_requests_per_day": 500,
    "date_step_days": 2,
    "request_delay_seconds": 2,
    "timeout_seconds": 30
}

# URL для парсинга
URLS = {
    "kad_arbitr": "https://kad.arbitr.ru",
    "search_endpoint": "https://kad.arbitr.ru/api/search",  # Нужно уточнить правильный endpoint
    "ras_arbitr": "https://ras.arbitr.ru"  # Для справки
}

# Ключевые слова для фильтрации (исключаем ненужные типы документов)
EXCLUDE_KEYWORDS = [
    "перенос",
    "отклонение", 
    "отложение",
    "включение в реестр",
    "назначить время",
    "оставить без рассмотрения",
    "определение"
]

# Включаем только нужные типы
INCLUDE_KEYWORDS = [
    "решение",
    "кассация",
    "постановление"
]

# Настройки по умолчанию для поиска
DEFAULT_SEARCH_PARAMS = {
    "GroupByCase": False,
    "Count": 25,
    "Page": 1,
    "DisputeTypes": ["1782f653-0cbb-44b3-beab-067d6fa57c20"],  # Только завершенные дела
    "DateFrom": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00"),
    "DateTo": datetime.now().strftime("%Y-%m-%dT23:59:59"),
    "Sides": [],
    "Judges": [],
    "Cases": [],
    "Text": ""
}

# User Agent для запросов
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
