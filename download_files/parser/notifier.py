"""
Модуль для отправки уведомлений в Telegram бот
Использует простой механизм через JSON файл
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import Config

logger = logging.getLogger(__name__)


class Notifier:
    """Класс для отправки уведомлений боту"""
    
    def __init__(self):
        self.notification_file = Config.STATE_DIR / "notifications.json"
    
    def send(self, message: str, level: str = "info"):
        """
        Отправить уведомление
        
        Args:
            message: текст сообщения
            level: уровень (info, warning, error, success)
        """
        try:
            # Эмодзи для разных уровней
            emoji_map = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'success': '✅',
                'start': '🚀',
                'finish': '🏁',
                'stats': '📊'
            }
            
            emoji = emoji_map.get(level, 'ℹ️')
            formatted_message = f"{emoji} {message}"
            
            notification = {
                "timestamp": datetime.now().isoformat(),
                "message": formatted_message,
                "level": level
            }
            
            # Записываем в файл (бот будет читать и удалять)
            with open(self.notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Уведомление отправлено: {message}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    def send_start(self):
        """Уведомление о старте парсера"""
        self.send("Парсер КАДР Арбитр запущен", level="start")
    
    def send_finish(self, stats: dict):
        """
        Уведомление о завершении работы
        
        Args:
            stats: статистика работы {
                'metadata_items': количество собранных метаданных,
                'pdfs_downloaded': количество скачанных PDF,
                'errors': количество ошибок,
                'requests_used': использовано запросов,
                'duration': время работы в секундах
            }
        """
        duration_min = round(stats.get('duration', 0) / 60, 1)
        
        message = (
            f"Парсер завершил работу\n\n"
            f"📊 Статистика:\n"
            f"• Метаданных собрано: {stats.get('metadata_items', 0)}\n"
            f"• PDF скачано: {stats.get('pdfs_downloaded', 0)}\n"
            f"• Ошибок: {stats.get('errors', 0)}\n"
            f"• Запросов использовано: {stats.get('requests_used', 0)}\n"
            f"• Время работы: {duration_min} мин"
        )
        
        level = "success" if stats.get('errors', 0) == 0 else "warning"
        self.send(message, level=level)
    
    def send_error(self, error_text: str):
        """Уведомление об ошибке"""
        self.send(f"ОШИБКА: {error_text}", level="error")
    
    def send_limits_info(self, limits: dict):
        """
        Уведомление о лимитах API
        
        Args:
            limits: {'limit': общий лимит, 'used': использовано, 'remaining': остаток}
        """
        message = (
            f"Лимиты API:\n"
            f"• Всего: {limits.get('limit', 0)}\n"
            f"• Использовано: {limits.get('used', 0)}\n"
            f"• Осталось: {limits.get('remaining', 0)}"
        )
        self.send(message, level="info")
    
    def send_progress(self, message: str):
        """Уведомление о прогрессе"""
        self.send(message, level="info")

