"""
Простая конфигурация для парсера арбитражных дел
"""
import os
from datetime import datetime, timedelta

def _get_base_dir():
    """
    Получить базовую директорию из переменной окружения или использовать fallback
    """
    # Проверяем переменную окружения
    env_dir = os.environ.get('PARSER_BASE_DIR')
    if env_dir:
        return os.path.expanduser(env_dir)
    
    # Используем XDG_DATA_HOME если доступен, иначе fallback на ~/.local/share/parser
    xdg_data_home = os.environ.get('XDG_DATA_HOME')
    if xdg_data_home:
        return os.path.join(xdg_data_home, 'parser')
    
    # Fallback на ~/.local/share/parser
    return os.path.expanduser('~/.local/share/parser')

# Базовые настройки
BASE_DIR = _get_base_dir()
DOCS_DIR = os.path.join(BASE_DIR, "docs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def ensure_dirs():
    """
    Создать необходимые директории
    Должна вызываться при запуске приложения
    """
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
    "search_endpoint": "https://kad.arbitr.ru/Kad/SearchInstances",
    "ras_arbitr": "https://ras.arbitr.ru"  # Для справки
}

# Настройки для POST запросов к search_endpoint
SEARCH_REQUEST_CONFIG = {
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://kad.arbitr.ru",
        "Referer": "https://kad.arbitr.ru/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    "required_cookies": ["pr_fp"],  # Обязательные cookies (wasm может отсутствовать)
    "json_template": {
        "Page": 1,
        "Count": 25,
        "Courts": [],
        "DateFrom": "2021-01-01",
        "DateTo": "2021-12-31",
        "Sides": [],
        "Judges": [],
        "CaseNumbers": [],
        "WithVKSInstances": False
    },
    "anti_bot_warning": True,  # Флаг для предупреждения о anti-bot защите
    "requires_wasm_token": True  # Флаг указывающий на необходимость WASM токена
}

# Добавляем обратно совместимый алиас для CaseNumbers
SEARCH_REQUEST_CONFIG["json_template"]["Cases"] = SEARCH_REQUEST_CONFIG["json_template"]["CaseNumbers"]

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

def build_default_search_params(tz=None, page_size=None):
    """
    Создать параметры поиска по умолчанию с актуальными датами
    
    Args:
        tz: Временная зона (tzinfo объект), по умолчанию None (локальное время)
        page_size: Размер страницы, по умолчанию берется из PARSING_SETTINGS
    
    Returns:
        dict: Свежие параметры поиска с актуальными timestamp'ами
    """
    # Получаем текущее время один раз
    now = datetime.now(tz)
    
    # Определяем размер страницы
    count = page_size if page_size is not None else PARSING_SETTINGS.get("items_per_page", 25)
    
    # Вычисляем даты
    date_from = (now - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
    date_to = now.strftime("%Y-%m-%dT23:59:59")
    
    result = {
        "GroupByCase": False,
        "Count": count,
        "Page": 1,
        "DisputeTypes": ["1782f653-0cbb-44b3-beab-067d6fa57c20"],  # Только завершенные дела
        "DateFrom": date_from,
        "DateTo": date_to,
        "Sides": [],
        "Judges": [],
        "CaseNumbers": [],
        "Text": ""
    }
    
    # Добавляем обратно совместимый алиас для CaseNumbers
    result["Cases"] = result["CaseNumbers"]
    
    return result

# User Agent для запросов
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
