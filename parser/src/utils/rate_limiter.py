"""
Простое ограничение количества запросов
"""
import time
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PARSING_SETTINGS

class RateLimiter:
    """Простой ограничитель запросов"""
    
    def __init__(self):
        self.max_requests = PARSING_SETTINGS["max_requests_per_day"]
        self.delay = PARSING_SETTINGS["request_delay_seconds"]
        self.requests_made = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
    def can_make_request(self):
        """Проверить можно ли сделать запрос"""
        self._check_daily_reset()
        return self.requests_made < self.max_requests
    
    def make_request(self):
        """Зарегистрировать запрос"""
        self._check_daily_reset()
        self.requests_made += 1
        
        # Задержка между запросами
        time.sleep(self.delay)
        
    def _check_daily_reset(self):
        """Проверить нужно ли сбросить счетчик на новый день"""
        now = datetime.now()
        if now >= self.daily_reset_time + timedelta(days=1):
            self.requests_made = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_status(self):
        """Получить статус лимитера"""
        return {
            "requests_made": self.requests_made,
            "max_requests": self.max_requests,
            "remaining": self.max_requests - self.requests_made,
            "daily_reset": self.daily_reset_time + timedelta(days=1)
        }

# Глобальный rate limiter
rate_limiter = RateLimiter()
