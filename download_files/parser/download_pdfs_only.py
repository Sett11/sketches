#!/usr/bin/env python3
"""
Скрипт для скачивания PDF файлов по уже собранным метаданным
Используется когда API лимиты исчерпаны, но метаданные уже есть
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import logging

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append('/app')

from pdf_downloader import PDFDownloader
from config import Config
from notifier import Notifier

# Настройка логирования
# Создаём директорию для логов
log_dir = Path('/app/data/logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/data/logs/download_pdfs_only.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFOnlyDownloader:
    """Класс для скачивания PDF по существующим метаданным"""
    
    def __init__(self):
        self.config = Config()
        self.notifier = Notifier()
        self.metadata_dir = Path(self.config.METADATA_DIR)
        self.pdfs_dir = Path(self.config.PDFS_DIR)
        
        # Создаём директории если их нет
        self.pdfs_dir.mkdir(parents=True, exist_ok=True)
    
    def load_existing_metadata(self) -> List[Dict]:
        """Загрузить все существующие метаданные из JSON файлов"""
        logger.info("Загрузка существующих метаданных...")
        
        all_items = []
        json_files = list(self.metadata_dir.glob("*.json"))
        
        if not json_files:
            logger.warning("JSON файлы метаданных не найдены!")
            return []
        
        logger.info(f"Найдено {len(json_files)} JSON файлов")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'items' in data and isinstance(data['items'], list):
                    all_items.extend(data['items'])
                    logger.debug(f"Загружено {len(data['items'])} записей из {json_file.name}")
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке {json_file}: {e}")
                continue
        
        logger.info(f"Всего загружено {len(all_items)} записей метаданных")
        return all_items
    
    def filter_metadata(self, items: List[Dict]) -> List[Dict]:
        """Фильтрация метаданных согласно настройкам"""
        logger.info("Фильтрация метаданных...")
        
        filtered_items = []
        
        for item in items:
            # Проверка InstanceLevel
            instance_level = item.get('InstanceLevel', 0)
            if instance_level <= self.config.FILTER_INSTANCE_LEVEL_MIN:
                logger.debug(f"Пропуск по InstanceLevel: {instance_level} <= {self.config.FILTER_INSTANCE_LEVEL_MIN}")
                continue
            
            # Проверка типа документа
            doc_type = item.get('Type', '')
            if self.config.FILTER_EXCLUDE_TYPE and doc_type == self.config.FILTER_EXCLUDE_TYPE:
                logger.debug(f"Пропуск по типу: {doc_type} == {self.config.FILTER_EXCLUDE_TYPE}")
                continue
            
            # Проверка наличия PDF URL
            pdf_url = self._extract_pdf_url(item)
            if not pdf_url:
                logger.warning(f"Нет PDF URL для дела {item.get('CaseNumber', 'unknown')}")
                continue
            
            logger.debug(f"Документ прошёл фильтрацию: {item.get('CaseNumber', 'unknown')}")
            filtered_items.append(item)
        
        logger.info(f"После фильтрации осталось {len(filtered_items)} документов для скачивания")
        return filtered_items
    
    def _extract_pdf_url(self, item: Dict) -> str:
        """Извлечь URL PDF из метаданных"""
        # Основное поле согласно документации API
        if 'FileUrl' in item and item['FileUrl']:
            return item['FileUrl']
        
        # Резервные варианты
        for field in ['Url', 'url', 'PdfUrl', 'pdfUrl', 'DocumentUrl', 'FileURL', 'fileUrl']:
            if field in item and item[field]:
                url = item[field]
                if isinstance(url, str) and (('.pdf' in url.lower()) or ('PdfDocument' in url)):
                    return url
        
        return ""
    
    def download_pdfs(self, items: List[Dict]) -> int:
        """Скачать PDF файлы"""
        if not items:
            logger.warning("Нет документов для скачивания")
            return 0
        
        logger.info(f"Начало скачивания {len(items)} PDF файлов...")
        self.notifier.send(f"Начало скачивания {len(items)} PDF файлов")
        
        downloaded_count = 0
        
        try:
            logger.info(f"Инициализация PDFDownloader для {len(items)} файлов...")
            with PDFDownloader(headless=True) as downloader:
                logger.info("PDFDownloader инициализирован, начинаем скачивание...")
                for i, item in enumerate(items, 1):
                    try:
                        pdf_url = self._extract_pdf_url(item)
                        if not pdf_url:
                            continue
                        
                        filename = item.get('FileName', f"document_{i}.pdf")
                        file_path = self.pdfs_dir / filename
                        
                        # ПРИНУДИТЕЛЬНОЕ СКАЧИВАНИЕ - игнорируем проверку существования
                        logger.info(f"Принудительное скачивание {filename}...")
                        
                        logger.info(f"Скачивание {i}/{len(items)}: {filename}")
                        
                        # Скачиваем PDF (унифицированный алгоритм как в main.py)
                        case_number = item.get('CaseNumber', f'document_{i}')
                        pdf_path = downloader.download_pdf(pdf_url, case_number)
                        
                        if pdf_path and Path(pdf_path).exists():
                            # Проверяем размер файла
                            file_size = Path(pdf_path).stat().st_size
                            
                            if file_size > 0:
                                # Проверяем что файл действительно PDF
                                try:
                                    with open(pdf_path, 'rb') as f:
                                        header = f.read(4)
                                        if header.startswith(b'%PDF'):
                                            downloaded_count += 1
                                            logger.info(f"✅ Скачан: {filename} ({file_size} байт)")
                                        else:
                                            logger.warning(f"❌ Файл не является PDF: {filename}")
                                except Exception as e:
                                    logger.warning(f"❌ Ошибка проверки файла {filename}: {e}")
                            else:
                                logger.warning(f"❌ Файл пустой: {filename}")
                        else:
                            logger.warning(f"❌ Не удалось скачать: {filename}")
                        
                        # Уведомление о прогрессе каждые 10 файлов
                        if i % 10 == 0:
                            self.notifier.send(f"Прогресс: {i}/{len(items)} файлов обработано")
                    
                    except Exception as e:
                        logger.error(f"Ошибка при скачивании файла {i}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Критическая ошибка при скачивании PDF: {e}")
            self.notifier.send_error(f"Критическая ошибка при скачивании PDF: {e}")
            return downloaded_count
        
        logger.info(f"Скачивание завершено. Успешно скачано: {downloaded_count}/{len(items)}")
        self.notifier.send(f"Скачивание завершено. Успешно скачано: {downloaded_count}/{len(items)}")
        
        return downloaded_count
    
    def run(self):
        """Главная функция"""
        logger.info("=" * 80)
        logger.info("СКАЧИВАНИЕ PDF ПО СУЩЕСТВУЮЩИМ МЕТАДАННЫМ")
        logger.info("=" * 80)
        
        try:
            # 1. Загружаем существующие метаданные
            all_items = self.load_existing_metadata()
            
            if not all_items:
                logger.warning("Метаданные не найдены!")
                self.notifier.send("Метаданные не найдены. Завершение работы.", level="warning")
                return
            
            # 2. Фильтруем данные
            filtered_items = self.filter_metadata(all_items)
            
            if not filtered_items:
                logger.info("Нет документов для скачивания после фильтрации")
                self.notifier.send("Нет документов для скачивания после фильтрации", level="info")
                return
            
            # 3. Скачиваем PDF файлы
            downloaded_count = self.download_pdfs(filtered_items)
            
            logger.info("=" * 80)
            logger.info(f"РАБОТА ЗАВЕРШЕНА. Скачано: {downloaded_count} файлов")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.exception(f"Критическая ошибка: {e}")
            self.notifier.send_error(f"Критическая ошибка: {e}")


def main():
    """Точка входа"""
    downloader = PDFOnlyDownloader()
    downloader.run()


if __name__ == "__main__":
    main()
