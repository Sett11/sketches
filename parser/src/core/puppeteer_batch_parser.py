"""
Батчевый парсер с поддержкой Puppeteer для обхода anti-bot защиты
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from src.utils.logger import logger
from src.core.puppeteer_wrapper import PuppeteerWrapper
from config.settings import DOCS_DIR, ensure_dirs


class PuppeteerBatchParser:
    """Батчевый парсер с использованием Puppeteer для обхода anti-bot защиты"""
    
    def __init__(self):
        ensure_dirs()
        self.puppeteer = PuppeteerWrapper()
        self.downloaded_count = 0
        self.metadata = []
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Инициализация Puppeteer браузера"""
        try:
            logger.info("🚀 Инициализация Puppeteer парсера...")
            
            if self.puppeteer.init_browser():
                self.is_initialized = True
                logger.info("✅ Puppeteer парсер инициализирован успешно")
                return True
            else:
                logger.error("❌ Ошибка инициализации Puppeteer парсера")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Puppeteer парсера: {e}")
            return False
    
    def set_cookies(self, cookies_dict: Dict) -> bool:
        """Установить cookies для Puppeteer"""
        try:
            logger.info("🍪 Установка cookies в Puppeteer...")
            
            if not self.is_initialized:
                logger.error("❌ Puppeteer не инициализирован. Вызовите initialize() сначала")
                return False
            
            return self.puppeteer.load_cookies(cookies_dict)
            
        except Exception as e:
            logger.error(f"❌ Ошибка установки cookies: {e}")
            return False
    
    def search_documents(self, date_from: str, date_to: str, page: int = 1) -> List[Dict]:
        """Поиск документов через Puppeteer"""
        try:
            if not self.is_initialized:
                logger.error("❌ Puppeteer не инициализирован")
                return []
            
            logger.info(f"🔍 Поиск документов: {date_from} - {date_to}, страница {page}")
            
            # Создаем параметры поиска
            search_params = {
                "Page": page,
                "Count": 25,
                "Courts": [],
                "DateFrom": date_from,
                "DateTo": date_to,
                "Sides": [],
                "Judges": [],
                "CaseNumbers": [],
                "WithVKSInstances": False,
                "ReasonIds": [],
                "CaseTypeIds": [],
                "CaseCategoryIds": [],
                "InstanceIds": [],
                "RegionIds": [],
                "DateType": 0
            }
            
            result = self.puppeteer.search_documents(search_params)
            
            if result and result.get('data'):
                documents = result['data']
                logger.info(f"✅ Найдено {len(documents)} документов на странице {page}")
                return documents
            else:
                logger.info(f"📄 Страница {page} пустая")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска документов: {e}")
            return []
    
    def download_pdf(self, pdf_url: str, filename: str) -> bool:
        """Скачать PDF через Puppeteer"""
        try:
            if not self.is_initialized:
                logger.error("❌ Puppeteer не инициализирован")
                return False
            
            logger.info(f"📄 Скачиваем PDF: {filename}")
            
            filepath = await self.puppeteer.download_pdf(pdf_url, filename)
            
            if filepath:
                self.downloaded_count += 1
                logger.info(f"✅ PDF сохранен: {filepath}")
                return True
            else:
                logger.error(f"❌ Ошибка скачивания PDF: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка скачивания PDF {filename}: {e}")
            return False
    
    def process_date_range(self, date_from: str, date_to: str, max_pages: int = 40) -> int:
        """Обработка диапазона дат через Puppeteer"""
        try:
            if not self.is_initialized:
                logger.error("❌ Puppeteer не инициализирован")
                return 0
            
            logger.info(f"📅 Обработка диапазона дат: {date_from} - {date_to}")
            
            # Используем Puppeteer для обработки всего диапазона дат
            results = self.puppeteer.process_date_range(date_from, date_to, max_pages)
            
            if results:
                self.downloaded_count = len(results)
                self.metadata = results
                logger.info(f"✅ Обработка завершена. Скачано документов: {len(results)}")
                return len(results)
            else:
                logger.info("📄 Документы не найдены или не скачаны")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки диапазона дат: {e}")
            return 0
    
    def save_metadata(self):
        """Сохранить метаданные"""
        try:
            os.makedirs(DOCS_DIR, exist_ok=True)
            
            metadata_file = os.path.join(DOCS_DIR, "metadata.json")
            temp_file = os.path.join(DOCS_DIR, "metadata.json.tmp")
            
            # Записываем во временный файл
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "processed_at": datetime.now().isoformat(),
                    "total_documents": self.downloaded_count,
                    "documents": self.metadata
                }, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Атомарно заменяем целевой файл
            os.replace(temp_file, metadata_file)
            logger.info(f"✅ Метаданные сохранены: {metadata_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения метаданных: {e}")
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass
    
    def get_stats(self) -> Dict:
        """Получить статистику"""
        try:
            stats = self.puppeteer.get_stats()
            stats.update({
                "downloaded_count": self.downloaded_count,
                "is_initialized": self.is_initialized
            })
            return stats
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {
                "downloaded_count": self.downloaded_count,
                "is_initialized": self.is_initialized,
                "error": str(e)
            }
    
    def close(self):
        """Закрытие браузера"""
        try:
            if self.is_initialized:
                self.puppeteer.close_browser()
                self.is_initialized = False
                logger.info("🔒 Puppeteer браузер закрыт")
        except Exception as e:
            logger.error(f"❌ Ошибка закрытия браузера: {e}")
    
    def __del__(self):
        """Деструктор - автоматическое закрытие браузера"""
        try:
            self.close()
        except:
            pass


def create_puppeteer_batch_parser() -> PuppeteerBatchParser:
    """Factory функция для создания экземпляра PuppeteerBatchParser"""
    return PuppeteerBatchParser()
