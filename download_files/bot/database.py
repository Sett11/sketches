"""
Упрощённая версия database.py для бота
Содержит только необходимые методы для работы с подписчиками
"""
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с SQLite базой данных"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных (создание таблиц)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица подписчиков бота
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_subscribers (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            logger.info("База данных бота инициализирована")
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для работы с соединением"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Ошибка при работе с БД: {e}")
            raise
        finally:
            conn.close()
    
    def add_subscriber(self, chat_id: int, username: str = "", 
                      first_name: str = "", last_name: str = ""):
        """Добавить подписчика"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO bot_subscribers 
                    (chat_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (chat_id, username, first_name, last_name))
                logger.info(f"Подписчик {chat_id} ({username}) добавлен")
            except sqlite3.IntegrityError:
                logger.info(f"Подписчик {chat_id} уже существует")
    
    def get_all_subscribers(self) -> List[int]:
        """Получить всех подписчиков"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM bot_subscribers")
            return [row[0] for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM processed_dates")
            dates_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM downloaded_files")
            files_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bot_subscribers")
            subscribers_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(file_size) FROM downloaded_files")
            total_size = cursor.fetchone()[0] or 0
            
            return {
                'processed_dates': dates_count,
                'downloaded_files': files_count,
                'bot_subscribers': subscribers_count,
                'total_size_mb': round(total_size / 1024 / 1024, 2)
            }

