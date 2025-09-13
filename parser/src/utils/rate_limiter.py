"""
Простое ограничение количества запросов
"""
import time
import threading
from datetime import datetime, timedelta

from config.settings import PARSING_SETTINGS


class DailyLimitExceeded(Exception):
    """Исключение, возникающее при превышении дневного лимита запросов"""
    pass


class RateLimiter:
    """Простой ограничитель запросов"""
    
    def __init__(self):
        self.max_requests = PARSING_SETTINGS["max_requests_per_day"]
        self.delay = PARSING_SETTINGS["request_delay_seconds"]
        self.requests_made = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self._lock = threading.Lock()  # Блокировка для потокобезопасности
        
    def can_make_request(self):
        """Проверить можно ли сделать запрос"""
        with self._lock:
            self._check_daily_reset()
            return self.requests_made < self.max_requests
    
    def make_request(self):
        """Зарегистрировать запрос"""
        # Проверяем лимит и регистрируем запрос атомарно
        with self._lock:
            self._check_daily_reset()
            if self.requests_made >= self.max_requests:
                raise DailyLimitExceeded(f"Дневной лимит запросов ({self.max_requests}) превышен")
            self.requests_made += 1
        
        # Задержка между запросами выполняется вне блокировки
        time.sleep(self.delay)
        
    def _check_daily_reset(self):
        """Проверить нужно ли сбросить счетчик на новый день"""
        now = datetime.now()
        if now >= self.daily_reset_time + timedelta(days=1):
            self.requests_made = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_status(self):
        """Получить статус лимитера"""
        with self._lock:
            self._check_daily_reset()
            return {
                "requests_made": self.requests_made,
                "max_requests": self.max_requests,
                "remaining": self.max_requests - self.requests_made,
                "daily_reset": self.daily_reset_time + timedelta(days=1)
            }

# Глобальный rate limiter
rate_limiter = RateLimiter()
