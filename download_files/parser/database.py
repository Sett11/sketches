"""
Работа с SQLite базой данных для отслеживания состояния
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from contextlib import contextmanager

from config import Config

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с SQLite базой данных"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
    
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
    
    def init_database(self):
        """Инициализация таблиц БД"""
        logger.info(f"Инициализация базы данных: {self.db_path}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица обработанных дат
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_dates (
                    date TEXT PRIMARY KEY,
                    pages_count INTEGER NOT NULL,
                    items_count INTEGER DEFAULT 0,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица скачанных файлов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS downloaded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_number TEXT UNIQUE NOT NULL,
                    pdf_url TEXT UNIQUE NOT NULL,
                    pdf_path TEXT NOT NULL,
                    meta_path TEXT NOT NULL,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    date_from_metadata TEXT
                )
            """)
            
            # Таблица подписчиков бота
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_subscribers (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Индексы для быстрого поиска
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_downloaded_case 
                ON downloaded_files(case_number)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_downloaded_url 
                ON downloaded_files(pdf_url)
            """)
            
            conn.commit()
            logger.info("База данных инициализирована успешно")
    
    # ============================================
    # Методы для работы с обработанными датами
    # ============================================
    
    def add_processed_date(self, date: str, pages_count: int, items_count: int = 0):
        """Добавить обработанную дату"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO processed_dates 
                (date, pages_count, items_count, processed_at)
                VALUES (?, ?, ?, ?)
            """, (date, pages_count, items_count, datetime.now()))
            logger.info(f"Дата {date} добавлена в БД (страниц: {pages_count}, записей: {items_count})")
    
    def is_date_processed(self, date: str) -> bool:
        """Проверить, обработана ли дата"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_dates WHERE date = ?", (date,))
            return cursor.fetchone() is not None
    
    def get_last_processed_date(self) -> Optional[str]:
        """Получить последнюю обработанную дату"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date FROM processed_dates 
                ORDER BY date DESC LIMIT 1
            """)
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_oldest_processed_date(self) -> Optional[str]:
        """Получить самую раннюю обработанную дату (для движения в прошлое)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date FROM processed_dates 
                ORDER BY date ASC LIMIT 1
            """)
            row = cursor.fetchone()
            return row[0] if row else None
    
    # ============================================
    # Методы для работы со скачанными файлами
    # ============================================
    
    def add_downloaded_file(self, case_number: str, pdf_url: str, 
                           pdf_path: str, meta_path: str, 
                           file_size: int = 0, date_from_metadata: str = ""):
        """Добавить скачанный файл"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO downloaded_files 
                    (case_number, pdf_url, pdf_path, meta_path, file_size, date_from_metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (case_number, pdf_url, pdf_path, meta_path, file_size, date_from_metadata))
                logger.info(f"Файл {case_number} добавлен в БД")
            except sqlite3.IntegrityError:
                logger.warning(f"Файл {case_number} уже существует в БД")
    
    def is_file_downloaded(self, pdf_url: str) -> bool:
        """Проверить, скачан ли файл по URL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM downloaded_files WHERE pdf_url = ?", (pdf_url,))
            return cursor.fetchone() is not None
    
    def is_case_downloaded(self, case_number: str) -> bool:
        """Проверить, скачан ли файл по номеру дела"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM downloaded_files WHERE case_number = ?", (case_number,))
            return cursor.fetchone() is not None
    
    def get_downloaded_files_count(self) -> int:
        """Получить количество скачанных файлов"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM downloaded_files")
            return cursor.fetchone()[0]
    
    # ============================================
    # Методы для работы с подписчиками бота
    # ============================================
    
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
    
    # ============================================
    # Статистика
    # ============================================
    
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
            
            cursor.execute("""
                SELECT SUM(file_size) FROM downloaded_files
            """)
            total_size = cursor.fetchone()[0] or 0
            
            return {
                'processed_dates': dates_count,
                'downloaded_files': files_count,
                'bot_subscribers': subscribers_count,
                'total_size_mb': round(total_size / 1024 / 1024, 2)
            }

