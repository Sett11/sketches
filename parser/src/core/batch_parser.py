"""
Основной батчевый парсер арбитражных дел
"""
import json
import os
import re
import requests
from datetime import datetime

from ..utils.logger import logger
from ..utils.cookie_manager import cookie_manager
from ..utils.rate_limiter import rate_limiter, DailyLimitExceeded
from ..utils.document_filter import document_filter
from ...config.settings import URLS, PARSING_SETTINGS, USER_AGENT, DOCS_DIR, ensure_dirs, build_default_search_params

class BatchParser:
    """Основной класс для батчевого парсинга"""
    
    @staticmethod
    def sanitize_case_id(case_id):
        """Санитизация case_id для предотвращения path injection"""
        # Преобразуем в строку и убираем опасные символы
        safe_id = str(case_id)
        # Разрешаем только буквы, цифры, точки, подчеркивания и дефисы
        safe_id = re.sub(r'[^A-Za-z0-9._-]', '_', safe_id)
        # Ограничиваем длину
        safe_id = safe_id[:100]
        # Убираем ведущие точки и дефисы
        safe_id = safe_id.lstrip('.-')
        # Если результат пустой, используем дефолтное значение
        if not safe_id:
            safe_id = 'unknown_case'
        return safe_id
    
    def __init__(self):
        # Убеждаемся, что директории созданы
        ensure_dirs()
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Content-Type": "application/json; charset=utf-8"
        })
        self.downloaded_count = 0
        self.metadata = []
    
    def set_cookies(self, cookies_dict):
        """Установить cookies для сессии"""
        for name, value in cookies_dict.items():
            self.session.cookies.set(name, value)
        logger.info(f"Установлено {len(cookies_dict)} cookies")
    
    def search_documents(self, date_from, date_to, page=1):
        """Поиск документов за указанный период"""
        # Упрощенный поиск для kad.arbitr.ru
        search_data = {
            "Count": PARSING_SETTINGS["items_per_page"],
            "Page": page,
            "DateFrom": date_from,
            "DateTo": date_to,
            "Text": ""
        }
        
        try:
            rate_limiter.make_request()
            response = self.session.post(
                URLS["search_endpoint"],
                json=search_data,
                timeout=PARSING_SETTINGS["timeout_seconds"]
            )
            
            if response.status_code == 200:
                data = response.json()
                # Пробуем разные возможные поля для списка документов
                documents = data.get('items', []) or data.get('documents', []) or data.get('results', []) or data.get('data', [])
                logger.info(f"Получено {len(documents)} документов на странице {page}")
                return documents
            else:
                logger.error(f"Ошибка поиска: {response.status_code}")
                logger.error(f"Ответ сервера: {response.text[:500]}")
                return []
                
        except DailyLimitExceeded as e:
            logger.warning(f"Достигнут дневной лимит запросов: {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка при поиске документов: {e}")
            return []
    
    def download_pdf(self, file_url, case_id, filename):
        """Скачать PDF документ"""
        try:
            rate_limiter.make_request()
            response = self.session.get(file_url, stream=True, timeout=PARSING_SETTINGS["timeout_seconds"])
            
            if response.status_code == 200:
                # Ensure DOCS_DIR exists before writing files
                os.makedirs(DOCS_DIR, exist_ok=True)
                
                # Sanitize filename to prevent directory traversal
                safe_filename = os.path.basename(filename)
                # Remove any potentially dangerous characters
                safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in ('_', '-', '.'))
                filepath = os.path.join(DOCS_DIR, safe_filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Скачан документ: {filename}")
                self.downloaded_count += 1
                return True
            else:
                logger.error(f"Ошибка скачивания {filename}: {response.status_code}")
                return False
                
        except DailyLimitExceeded as e:
            logger.warning(f"Достигнут дневной лимит запросов: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при скачивании {filename}: {e}")
            return False
    
    def process_date_range(self, date_from, date_to):
        """Обработать диапазон дат"""
        logger.info(f"Обработка периода: {date_from} - {date_to}")
        
        all_documents = []
        
        # Получаем все страницы для данного диапазона
        for page in range(1, PARSING_SETTINGS["max_pages"] + 1):
            documents = self.search_documents(date_from, date_to, page)
            if not documents:
                logger.info(f"Страница {page} пустая, завершаем")
                break
                
            # Фильтруем документы
            filtered_docs = document_filter.filter_documents_list(documents)
            logger.info(f"После фильтрации осталось {len(filtered_docs)} из {len(documents)}")
            
            all_documents.extend(filtered_docs)
        
        # Скачиваем отфильтрованные документы
        for doc in all_documents:
            try:
                # Пробуем разные возможные поля для URL файла
                file_url = doc.get('FileUrl', '') or doc.get('DocumentUrl', '') or doc.get('Url', '') or doc.get('Link', '')
                case_id = doc.get('CaseId', '') or doc.get('Id', '') or doc.get('DocumentId', '') or str(doc.get('Number', ''))
                
                if file_url and case_id:
                    # Санитизируем case_id для безопасного использования в имени файла
                    safe_case_id = self.sanitize_case_id(case_id)
                    filename = f"{safe_case_id}.pdf"
                    if self.download_pdf(file_url, case_id, filename):
                        # Сохраняем метаданные
                        self.metadata.append({
                            "case_id": case_id,
                            "file_path": filename,
                            "metadata": doc,
                            "downloaded_at": datetime.now().isoformat()
                        })
            except DailyLimitExceeded:
                logger.warning("Достигнут дневной лимит запросов, прекращаем скачивание")
                break
        
        return len(all_documents)
    
    def save_metadata(self):
        """Сохранить метаданные в JSON файл с атомарной записью"""
        # Убеждаемся, что директория существует
        os.makedirs(DOCS_DIR, exist_ok=True)
        
        metadata_file = os.path.join(DOCS_DIR, "metadata.json")
        temp_file = os.path.join(DOCS_DIR, "metadata.json.tmp")
        
        try:
            # Записываем во временный файл
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                f.flush()  # Принудительно сбрасываем буфер
                os.fsync(f.fileno())  # Синхронизируем с диском
            
            # Атомарно заменяем целевой файл
            os.replace(temp_file, metadata_file)
            logger.info(f"Метаданные сохранены атомарно: {metadata_file}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения метаданных: {e}")
            # Очищаем временный файл в случае ошибки
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass  # Игнорируем ошибки при удалении временного файла
    
    def get_stats(self):
        """Получить статистику"""
        return {
            "downloaded_count": self.downloaded_count,
            "rate_limiter_status": rate_limiter.get_status()
        }

def create_batch_parser():
    """Factory функция для создания экземпляра BatchParser"""
    return BatchParser()


# Для обратной совместимости (deprecated - используйте create_batch_parser())
def get_batch_parser():
    """Получить экземпляр BatchParser (deprecated)"""
    import warnings
    warnings.warn("get_batch_parser() deprecated, используйте create_batch_parser()", DeprecationWarning)
    return create_batch_parser()
