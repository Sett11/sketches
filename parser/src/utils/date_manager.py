"""
Простое управление диапазонами дат
"""
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PARSING_SETTINGS

class DateManager:
    """Простой менеджер диапазонов дат"""
    
    def __init__(self):
        self.date_step = PARSING_SETTINGS["date_step_days"]
    
    def generate_date_ranges(self, start_date, end_date):
        """Генерировать диапазоны дат с заданным шагом"""
        ranges = []
        current_start = start_date
        
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=self.date_step), end_date)
            ranges.append({
                "start": current_start.strftime("%Y-%m-%dT00:00:00"),
                "end": current_end.strftime("%Y-%m-%dT23:59:59")
            })
            current_start = current_end + timedelta(days=1)
        
        return ranges
    
    def get_default_range(self, days_back=30):
        """Получить диапазон по умолчанию (последние N дней)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        return self.generate_date_ranges(start_date, end_date)
    
    def parse_date_string(self, date_str):
        """Парсить дату из строки"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d.%m.%Y")
            except ValueError:
                print(f"Неверный формат даты: {date_str}")
                return None

# Глобальный менеджер дат
date_manager = DateManager()
