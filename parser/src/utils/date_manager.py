"""
Простое управление диапазонами дат
"""
from datetime import datetime, timedelta
import logging

from config.settings import PARSING_SETTINGS

# Модульный логгер
logger = logging.getLogger(__name__)

class _IntegerishError(ValueError):
    """Исключение для случаев, когда значение не является целым числом"""
    pass

class DateManager:
    """Простой менеджер диапазонов дат"""
    
    def __init__(self):
        self.date_step = self._validate_date_step(PARSING_SETTINGS["date_step_days"])
    
    def _validate_date_step(self, date_step):
        """
        Валидировать и привести date_step к безопасному значению
        
        Args:
            date_step: Значение шага даты (может быть int, float, str)
            
        Returns:
            int: Валидированное значение >= 1
            
        Raises:
            ValueError: Если значение не может быть приведено к допустимому или не является целым числом
        """
        # Явно отклоняем булевы значения
        if isinstance(date_step, bool):
            raise ValueError(f"date_step не может быть булевым значением, получено: {date_step}")
        
        try:
            # Если уже int, оставляем как есть
            if not isinstance(date_step, int):
                # Для всех не-int типов: единый путь валидации
                float_val = float(date_step)
                if not float_val.is_integer():
                    raise _IntegerishError(f"date_step должен быть целым числом, получено нецелое десятичное: {date_step}")
                date_step = int(float_val)
        except _IntegerishError:
            raise  # Перебрасываем наши кастомные ошибки для нецелых чисел
        except (ValueError, TypeError) as e:
            raise ValueError(f"date_step должен быть числом, получено: {date_step} ({type(date_step).__name__})") from e
        
        # Проверяем, что значение положительное
        if date_step < 1:
            raise ValueError(f"date_step должен быть >= 1, получено: {date_step}")
        
        return date_step
    
    def generate_date_ranges(self, start_date, end_date):
        """Генерировать диапазоны дат с заданным шагом"""
        ranges = []
        
        # Валидация входных параметров
        if not isinstance(start_date, datetime):
            raise ValueError(f"start_date должен быть объектом datetime, получено: {type(start_date).__name__}")
        if not isinstance(end_date, datetime):
            raise ValueError(f"end_date должен быть объектом datetime, получено: {type(end_date).__name__}")
        
        # Нормализация дат к полуночи (00:00:00)
        current_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Проверяем, что start_date не позже end_date
        if current_start > end_date:
            raise ValueError(f"start_date ({current_start}) не может быть позже end_date ({end_date})")
        
        # Дополнительная защита: убеждаемся, что date_step валиден
        # (хотя это уже проверено в конструкторе, но для безопасности)
        safe_date_step = max(1, self.date_step)
        
        # Счетчик итераций для защиты от бесконечного цикла
        max_iterations = 10000  # Разумный лимит
        iteration_count = 0
        
        while current_start <= end_date and iteration_count < max_iterations:
            # Вычисляем current_end так, чтобы каждый диапазон охватывал точно date_step дней
            current_end = min(current_start + timedelta(days=safe_date_step - 1), end_date)
            
            ranges.append({
                "start": current_start.strftime("%Y-%m-%dT00:00:00"),
                "end": current_end.strftime("%Y-%m-%dT23:59:59")
            })
            
            # Переходим к следующему окну
            current_start = current_end + timedelta(days=1)
            iteration_count += 1
        
        # Предупреждение, если достигнут лимит итераций
        if iteration_count >= max_iterations:
            print(f"Предупреждение: достигнут лимит итераций ({max_iterations}) в generate_date_ranges")
        
        return ranges
    
    def get_default_range(self, days_back=30):
        """Получить диапазон по умолчанию (последние N дней)"""
        # Валидируем days_back в узком try/except
        try:
            if not isinstance(days_back, (int, float)) or days_back <= 0:
                raise ValueError(f"days_back должен быть положительным числом, получено: {days_back}")
            days_back = int(days_back)
        except Exception as e:
            logger.error(f"Ошибка валидации days_back: {e}")
            # Fallback: возвращаем диапазон за последний день
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            return self.generate_date_ranges(start_date, end_date)
        
        # Выполняем основную логику без try/except, позволяя исключениям распространяться
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
