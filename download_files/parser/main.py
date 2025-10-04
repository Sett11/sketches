"""
Главный модуль парсера КАДР Арбитр
Оркестрирует весь процесс сбора метаданных и скачивания PDF
"""
import logging
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from config import Config
from database import Database
from api_client import APIClient
from notifier import Notifier
from pdf_downloader import PDFDownloader

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / 'parser.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class KadrParser:
    """Главный класс парсера"""
    
    def __init__(self):
        # Валидация конфигурации
        Config.validate()
        
        # Инициализация компонентов
        self.db = Database(Config.DB_PATH)
        self.api = APIClient()
        self.notifier = Notifier()
        
        # Статистика
        self.stats = {
            'metadata_items': 0,
            'pdfs_downloaded': 0,
            'errors': 0,
            'requests_used': 0,
            'start_time': time.time()
        }
    
    def run(self):
        """Главная точка входа"""
        logger.info("=" * 80)
        logger.info("СТАРТ ПАРСЕРА КАДР АРБИТР")
        logger.info("=" * 80)
        
        try:
            # Уведомление о старте
            self.notifier.send_start()
            
            # 1. Проверка лимитов API
            if not self._check_limits():
                return
            
            # 2. Сбор метаданных
            all_metadata = self._collect_metadata()
            
            if not all_metadata:
                logger.warning("Метаданные не собраны")
                self.notifier.send("Метаданные не собраны. Завершение работы.", level="warning")
                return
            
            # 3. Фильтрация данных
            filtered_items = self._filter_metadata(all_metadata)
            
            if not filtered_items:
                logger.info("Нет документов для скачивания после фильтрации")
                self.notifier.send("Нет новых документов для скачивания", level="info")
                self._send_final_stats()
                return
            
            # 4. Скачивание PDF
            self._download_pdfs(filtered_items)
            
            # 5. Финальная статистика
            self._send_final_stats()
            
            logger.info("=" * 80)
            logger.info("ПАРСЕР ЗАВЕРШЁН УСПЕШНО")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.exception(f"Критическая ошибка в парсере: {e}")
            self.notifier.send_error(f"Критическая ошибка: {str(e)}")
            sys.exit(1)
    
    def _check_limits(self) -> bool:
        """Проверка лимитов API"""
        logger.info("Проверка лимитов API...")
        
        limits_info = self.api.get_limits_info()
        
        if not limits_info:
            logger.error("Не удалось получить информацию о лимитах")
            self.notifier.send_error("Не удалось получить информацию о лимитах API")
            return False
        
        remaining = limits_info.get('remaining', 0)
        
        logger.info(f"Лимиты: осталось {remaining} запросов")
        self.notifier.send_limits_info(limits_info)
        
        if remaining <= 0:
            logger.warning("Лимиты API исчерпаны")
            self.notifier.send("⚠️ Лимиты API исчерпаны. Скачивание отложено.", level="warning")
            return False
        
        return True
    
    def _collect_metadata(self) -> List[Dict]:
        """
        Сбор метаданных
        Приоритет: вчерашний день, затем движение в прошлое
        """
        logger.info("Начало сбора метаданных...")
        all_items = []
        
        # 1. Сначала собираем за вчерашний день
        yesterday_from, yesterday_to = self.api.get_date_range_for_yesterday()
        
        if not self.db.is_date_processed(yesterday_to):
            logger.info(f"Сбор метаданных за вчерашний день: {yesterday_to}")
            self.notifier.send_progress(f"Сбор данных за {yesterday_to}")
            
            items = self.api.fetch_metadata_for_date(yesterday_from, yesterday_to)
            
            if items:
                all_items.extend(items)
                self.db.add_processed_date(yesterday_to, len(items) // 20 + 1, len(items))
                logger.info(f"Собрано {len(items)} записей за {yesterday_to}")
        else:
            logger.info(f"Дата {yesterday_to} уже обработана")
        
        # 2. Если остались запросы - идём в прошлое
        if self.api.can_make_request():
            logger.info("Остались запросы. Движение в прошлое...")
            all_items.extend(self._collect_historical_data())
        
        self.stats['metadata_items'] = len(all_items)
        self.stats['requests_used'] = self.api.requests_made
        
        logger.info(f"Всего собрано {len(all_items)} записей метаданных")
        
        return all_items
    
    def _collect_historical_data(self) -> List[Dict]:
        """Сбор исторических данных (движение в прошлое)"""
        historical_items = []
        
        # Определяем с какой даты начинать
        oldest_date = self.db.get_oldest_processed_date()
        
        if oldest_date:
            # Начинаем с даты перед самой ранней обработанной
            current_date = datetime.strptime(oldest_date, '%Y-%m-%d') - timedelta(days=1)
        else:
            # Если нет обработанных дат, начинаем с позавчера
            current_date = datetime.now() - timedelta(days=2)
        
        logger.info(f"Начало сбора исторических данных с {current_date.strftime('%Y-%m-%d')}")
        
        # Идём в прошлое пока есть лимиты
        while self.api.can_make_request() and not self.api.limit_exceeded:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Проверяем, не обработана ли уже эта дата
            if self.db.is_date_processed(date_str):
                logger.info(f"Дата {date_str} уже обработана, пропускаем")
                current_date -= timedelta(days=1)
                continue
            
            logger.info(f"Сбор данных за {date_str}")
            self.notifier.send_progress(f"Сбор исторических данных за {date_str}")
            
            items = self.api.fetch_metadata_for_date(date_str, date_str)
            
            # Если API вернул ошибку лимита - прерываемся
            if self.api.limit_exceeded:
                logger.warning(f"Дневной лимит API исчерпан при сборе данных за {date_str}")
                # Не помечаем эту дату как обработанную - вернёмся к ней завтра
                break
            
            if items:
                historical_items.extend(items)
                self.db.add_processed_date(date_str, len(items) // 20 + 1, len(items))
                logger.info(f"Собрано {len(items)} записей за {date_str}")
            else:
                # Если нет данных, всё равно помечаем дату как обработанную
                self.db.add_processed_date(date_str, 0, 0)
            
            # Переходим к предыдущему дню
            current_date -= timedelta(days=1)
            
            # Ограничение: не уходим слишком далеко в прошлое (например, максимум год)
            if current_date < datetime.now() - timedelta(days=365):
                logger.info("Достигнут лимит глубины истории (365 дней)")
                break
        
        logger.info(f"Собрано {len(historical_items)} исторических записей")
        return historical_items
    
    def _filter_metadata(self, metadata: List[Dict]) -> List[Dict]:
        """
        Фильтрация метаданных по критериям
        
        Критерии:
        - InstanceLevel > FILTER_INSTANCE_LEVEL_MIN
        - Type != FILTER_EXCLUDE_TYPE
        - Не скачан ранее (проверка по БД)
        """
        logger.info("Фильтрация метаданных...")
        
        filtered = []
        
        for item in metadata:
            # Проверяем критерии
            instance_level = item.get('InstanceLevel', 0)
            doc_type = item.get('Type', '')
            
            if instance_level <= Config.FILTER_INSTANCE_LEVEL_MIN:
                continue
            
            if doc_type == Config.FILTER_EXCLUDE_TYPE:
                continue
            
            # Извлекаем URL PDF (может быть в разных полях)
            pdf_url = self._extract_pdf_url(item)
            
            if not pdf_url:
                logger.debug(f"Нет PDF URL для дела {item.get('CaseNumber', 'unknown')}")
                continue
            
            # Проверяем, не скачан ли уже
            if self.db.is_file_downloaded(pdf_url):
                logger.debug(f"Файл уже скачан: {item.get('CaseNumber', 'unknown')}")
                continue
            
            filtered.append(item)
        
        logger.info(f"После фильтрации осталось {len(filtered)} документов для скачивания")
        
        return filtered
    
    def _extract_pdf_url(self, item: Dict) -> str:
        """
        Извлечь URL PDF из метаданных
        
        Согласно документации API: https://api-assist.com/documentation/ras-arbitr-api.txt
        Поле FileUrl содержит прямую ссылку на PDF
        """
        # Логируем структуру первого item для отладки (только один раз)
        if not hasattr(self, '_logged_item_structure'):
            logger.info(f"Структура item из API: {json.dumps(item, ensure_ascii=False, indent=2)[:800]}")
            self._logged_item_structure = True
        
        # ОСНОВНОЕ ПОЛЕ согласно документации API
        if 'FileUrl' in item and item['FileUrl']:
            return item['FileUrl']
        
        # Резервные варианты (на случай изменения API)
        
        # Вариант 2: поле Url или Link
        for field in ['Url', 'url', 'PdfUrl', 'pdfUrl', 'DocumentUrl', 'FileURL', 'fileUrl']:
            if field in item and item[field]:
                url = item[field]
                if isinstance(url, str) and (('.pdf' in url.lower()) or ('PdfDocument' in url)):
                    return url
        
        # Вариант 3: ContentTypes может содержать ссылки (редкий случай)
        content_types = item.get('ContentTypes', [])
        if isinstance(content_types, list) and content_types:
            for ct in content_types:
                if isinstance(ct, dict) and 'Url' in ct:
                    url = ct['Url']
                    if url and '.pdf' in url.lower():
                        return url
        
        logger.warning(f"Не удалось извлечь PDF URL для дела {item.get('CaseNumber', 'unknown')}")
        logger.debug(f"Доступные ключи в item: {list(item.keys())}")
        return ""
    
    def _download_pdfs(self, filtered_items: List[Dict]):
        """Скачивание PDF файлов"""
        total = len(filtered_items)
        logger.info(f"Начало скачивания {total} PDF файлов...")
        
        self.notifier.send_progress(f"Начало скачивания {total} PDF файлов")
        
        success_count = 0
        error_count = 0
        
        # Используем контекстный менеджер для PDFDownloader
        with PDFDownloader(headless=True) as downloader:
            
            for idx, item in enumerate(filtered_items, 1):
                case_number = item.get('CaseNumber', f'unknown_{idx}')
                pdf_url = self._extract_pdf_url(item)
                
                logger.info(f"[{idx}/{total}] Скачивание {case_number}")
                
                try:
                    # Скачиваем PDF
                    pdf_path = downloader.download_pdf(pdf_url, case_number)
                    
                    if pdf_path:
                        # Сохраняем метаданные рядом с PDF
                        meta_path = self._save_pdf_metadata(item, case_number)
                        
                        # Получаем размер файла
                        file_size = Path(pdf_path).stat().st_size if Path(pdf_path).exists() else 0
                        
                        # Записываем в БД
                        self.db.add_downloaded_file(
                            case_number=case_number,
                            pdf_url=pdf_url,
                            pdf_path=pdf_path,
                            meta_path=meta_path,
                            file_size=file_size,
                            date_from_metadata=item.get('Date', '')
                        )
                        
                        success_count += 1
                        
                    else:
                        error_count += 1
                        self.stats['errors'] += 1
                        logger.error(f"Не удалось скачать {case_number}")
                    
                except Exception as e:
                    error_count += 1
                    self.stats['errors'] += 1
                    logger.exception(f"Ошибка при скачивании {case_number}: {e}")
                
                # Периодические уведомления о прогрессе
                if idx % 10 == 0:
                    self.notifier.send_progress(
                        f"Прогресс: {idx}/{total} (успешно: {success_count}, ошибок: {error_count})"
                    )
        
        self.stats['pdfs_downloaded'] = success_count
        
        logger.info(f"Скачивание завершено. Успешно: {success_count}, Ошибок: {error_count}")
    
    def _save_pdf_metadata(self, item: Dict, case_number: str) -> str:
        """
        Сохранить метаданные конкретного PDF
        
        Returns:
            Путь к файлу метаданных
        """
        meta_path = Config.PDFS_DIR / f"{case_number}.json"
        
        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(item, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Метаданные сохранены: {meta_path}")
            return str(meta_path)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении метаданных: {e}")
            return ""
    
    def _send_final_stats(self):
        """Отправка финальной статистики"""
        duration = time.time() - self.stats['start_time']
        self.stats['duration'] = duration
        
        # Статистика из БД
        db_stats = self.db.get_statistics()
        
        logger.info("Финальная статистика:")
        logger.info(f"  Метаданных собрано: {self.stats['metadata_items']}")
        logger.info(f"  PDF скачано: {self.stats['pdfs_downloaded']}")
        logger.info(f"  Ошибок: {self.stats['errors']}")
        logger.info(f"  Запросов использовано: {self.stats['requests_used']}")
        logger.info(f"  Время работы: {duration:.1f} сек")
        logger.info(f"  Всего в БД файлов: {db_stats['downloaded_files']}")
        logger.info(f"  Всего в БД дат: {db_stats['processed_dates']}")
        
        self.notifier.send_finish(self.stats)


def main():
    """Точка входа"""
    try:
        parser = KadrParser()
        parser.run()
    except KeyboardInterrupt:
        logger.info("Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

