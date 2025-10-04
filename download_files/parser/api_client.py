"""
Клиент для работы с API КАДР Арбитр через api-assist.com
"""
import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import json

from config import Config

logger = logging.getLogger(__name__)


class APIClient:
    """Клиент для работы с API КАДР Арбитр"""
    
    def __init__(self):
        self.api_key = Config.API_KEY
        self.api_url = Config.API_URL
        self.stat_url = Config.API_STAT_URL
        self.search_text = Config.SEARCH_TEXT
        self.delay = Config.DELAY_BETWEEN_REQUESTS
        self.requests_made = 0
        self.max_requests = Config.MAX_REQUESTS_PER_RUN
        self.limit_exceeded = False  # Флаг исчерпания дневного лимита API
    
    def get_limits_info(self) -> Optional[Dict]:
        """
        Получить информацию о лимитах API
        Returns: {
            'limit': общий лимит,
            'used': использовано,
            'remaining': остаток
        }
        """
        try:
            url = f"{self.stat_url}?key={self.api_key}"
            logger.info(f"Запрос лимитов: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Информация о лимитах: {data}")
            
            # API возвращает список с одним элементом: [{"service": "ras_arbitr", ...}]
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Берём первый элемент
            
            # Парсим ответ API
            # Формат: {"day_limit": 500, "day_request_count": 344, ...}
            day_limit = data.get('day_limit', 0)
            day_used = data.get('day_request_count', 0)
            remaining = day_limit - day_used
            
            return {
                'limit': day_limit,
                'used': day_used,
                'remaining': remaining,
                'month_limit': data.get('month_limit', 0),
                'month_used': data.get('month_request_count', 0),
                'paid_till': data.get('paid_till', ''),
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении лимитов: {e}")
            return None
    
    def can_make_request(self) -> bool:
        """Проверить, можем ли сделать ещё запрос"""
        return self.requests_made < self.max_requests
    
    def fetch_metadata_for_date(self, date_from: str, date_to: str) -> List[Dict]:
        """
        Скачать метаданные за указанный день
        
        Args:
            date_from: дата начала (YYYY-MM-DD)
            date_to: дата окончания (YYYY-MM-DD)
        
        Returns:
            Список всех items со всех страниц
        """
        all_items = []
        page = 1
        
        logger.info(f"Начало сбора метаданных за период {date_from} - {date_to}")
        
        try:
            # Первый запрос для определения количества страниц
            first_page_data = self._fetch_page(date_from, date_to, page)
            
            if not first_page_data:
                logger.warning(f"Не удалось получить данные за {date_from} - {date_to}")
                return []
            
            # Сохраняем первую страницу
            self._save_metadata_page(first_page_data, date_to, page)
            
            # Собираем items с первой страницы
            items = first_page_data.get('items', [])
            all_items.extend(items)
            logger.info(f"Страница 1: получено {len(items)} записей")
            
            # Узнаём общее количество страниц
            total_pages = first_page_data.get('pages', 1)
            logger.info(f"Всего страниц: {total_pages}")
            
            # Скачиваем остальные страницы
            for page in range(2, total_pages + 1):
                if not self.can_make_request():
                    logger.warning(f"Достигнут лимит запросов ({self.max_requests})")
                    break
                
                if self.limit_exceeded:
                    logger.warning("Прерывание сбора: дневной лимит API исчерпан")
                    break
                
                time.sleep(self.delay)
                
                page_data = self._fetch_page(date_from, date_to, page)
                
                if page_data:
                    self._save_metadata_page(page_data, date_to, page)
                    items = page_data.get('items', [])
                    all_items.extend(items)
                    logger.info(f"Страница {page}: получено {len(items)} записей")
                    
                    # Если установлен флаг лимита - прерываемся
                    if self.limit_exceeded:
                        logger.warning("Прерывание сбора: дневной лимит API исчерпан")
                        break
                else:
                    logger.warning(f"Не удалось получить страницу {page}")
            
            logger.info(f"Всего собрано {len(all_items)} записей за {date_from} - {date_to}")
            return all_items
            
        except Exception as e:
            logger.error(f"Ошибка при сборе метаданных: {e}")
            return all_items
    
    def _fetch_page(self, date_from: str, date_to: str, page: int) -> Optional[Dict]:
        """
        Получить одну страницу результатов
        """
        try:
            url = (f"{self.api_url}?key={self.api_key}"
                   f"&DateFrom={date_from}&DateTo={date_to}"
                   f"&Page={page}&Text={self.search_text}")
            
            logger.debug(f"Запрос страницы {page}: {url}")
            
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            self.requests_made += 1
            
            data = response.json()
            
            # Валидация структуры ответа
            if not isinstance(data, dict):
                logger.error(f"Неверный формат ответа API (не dict): {type(data)}")
                return None
            
            # Проверяем наличие обязательных полей
            if 'items' not in data:
                logger.warning(f"Ответ API не содержит 'items'. Ключи: {list(data.keys())}")
                # Иногда API может вернуть ошибку в поле 'error' или 'message'
                if 'error' in data:
                    error_msg = data['error']
                    logger.error(f"API вернул ошибку: {error_msg}")
                    # Если это ошибка превышения лимита - устанавливаем флаг
                    if 'limit' in error_msg.lower() and 'exceed' in error_msg.lower():
                        self.limit_exceeded = True
                        logger.warning("Дневной лимит API исчерпан")
                return data  # Вернём как есть, но items будет пустым списком
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе страницы {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON для страницы {page}: {e}")
            # Логируем первые 500 символов ответа для отладки
            try:
                logger.error(f"Тело ответа (первые 500 символов): {response.text[:500]}")
            except:
                pass
            return None
    
    def _save_metadata_page(self, data: Dict, date_str: str, page: int):
        """
        Сохранить страницу метаданных в файл
        """
        try:
            filename = Config.METADATA_DIR / f"{date_str}-{page}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Метаданные сохранены: {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении метаданных: {e}")
    
    def get_date_range_for_yesterday(self) -> tuple:
        """Получить диапазон дат для вчерашнего дня"""
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        return date_str, date_str
    
    def get_date_range_before(self, last_date: str) -> tuple:
        """
        Получить диапазон дат для дня перед указанной датой
        
        Args:
            last_date: последняя обработанная дата в формате YYYY-MM-DD
        
        Returns:
            (date_from, date_to) для предыдущего дня
        """
        last_dt = datetime.strptime(last_date, '%Y-%m-%d')
        prev_day = last_dt - timedelta(days=1)
        date_str = prev_day.strftime('%Y-%m-%d')
        return date_str, date_str

