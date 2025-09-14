"""
Основной батчевый парсер арбитражных дел
"""
import json
import os
import re
import requests
from datetime import datetime

from src.utils.logger import logger
from src.utils.cookie_manager import cookie_manager
from src.utils.rate_limiter import rate_limiter, DailyLimitExceeded
from src.utils.document_filter import document_filter
from config.settings import URLS, PARSING_SETTINGS, USER_AGENT, DOCS_DIR, ensure_dirs, build_default_search_params, SEARCH_REQUEST_CONFIG

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
    
    def check_anti_bot_protection(self):
        """Проверить наличие anti-bot защиты и необходимых токенов"""
        logger.info("🔍 Проверка anti-bot защиты...")
        
        # Проверяем наличие обязательных cookies
        missing_cookies = []
        for cookie_name in SEARCH_REQUEST_CONFIG.get("required_cookies", []):
            if not self.session.cookies.get(cookie_name):
                missing_cookies.append(cookie_name)
        
        if missing_cookies:
            logger.warning(f"⚠️ Отсутствуют обязательные cookies: {missing_cookies}")
            logger.warning("⚠️ Рекомендуется получить cookies из реального браузера")
            return False
        
        # Делаем тестовый запрос для проверки anti-bot
        test_data = SEARCH_REQUEST_CONFIG["json_template"].copy()
        test_data.update({
            "Count": 1,
            "Page": 1,
            "DateFrom": "2024-01-01",
            "DateTo": "2024-01-01"
        })
        
        try:
            headers = SEARCH_REQUEST_CONFIG["headers"].copy()
            response = self.session.post(
                URLS["search_endpoint"],
                json=test_data,
                headers=headers,
                timeout=PARSING_SETTINGS["timeout_seconds"],
                allow_redirects=False
            )
            
            # Обрабатываем редиректы как блокировку
            if 300 <= response.status_code < 400:
                logger.error(f"❌ Anti-bot защита активна - получен редирект {response.status_code}")
                logger.error("❌ Необходимо обновить WASM токен или использовать прокси")
                return False
            
            if response.status_code == 200:
                # Проверяем Content-Type для JSON ответов
                content_type = response.headers.get('Content-Type', '').lower()
                if not content_type.startswith('application/json'):
                    logger.error(f"❌ Anti-bot защита активна - получен не-JSON ответ")
                    logger.error(f"❌ Content-Type: {content_type}")
                    logger.error("❌ Необходимо обновить WASM токен или использовать прокси")
                    return False
                
                # Пытаемся парсить JSON
                try:
                    response.json()
                    logger.info("✅ Anti-bot защита обойдена успешно")
                    return True
                except ValueError as e:
                    logger.error(f"❌ Anti-bot защита активна - невалидный JSON ответ")
                    logger.error(f"❌ Ошибка парсинга JSON: {e}")
                    logger.error("❌ Необходимо обновить WASM токен или использовать прокси")
                    return False
                    
            elif response.status_code == 403:
                logger.error("❌ Anti-bot защита активна - запрос заблокирован")
                logger.error("❌ Необходимо обновить WASM токен или использовать прокси")
                return False
            else:
                logger.warning(f"⚠️ Неожиданный статус ответа: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке anti-bot защиты: {e}")
            return False
    
    def search_documents(self, date_from, date_to, page=1):
        """Поиск документов за указанный период"""
        # Проверяем anti-bot защиту перед выполнением запроса
        if SEARCH_REQUEST_CONFIG.get("anti_bot_warning", False):
            logger.warning("⚠️ ВНИМАНИЕ: Эндпоинт требует обхода anti-bot защиты!")
            logger.warning("⚠️ Необходим WASM токен или валидные cookies для успешного запроса")
        
        # Создаем правильную схему запроса согласно API
        search_data = SEARCH_REQUEST_CONFIG["json_template"].copy()
        search_data.update({
            "Count": PARSING_SETTINGS["items_per_page"],
            "Page": page,
            "DateFrom": date_from,
            "DateTo": date_to
        })
        
        # Проверяем наличие обязательных cookies
        missing_cookies = []
        for cookie_name in SEARCH_REQUEST_CONFIG.get("required_cookies", []):
            if not self.session.cookies.get(cookie_name):
                missing_cookies.append(cookie_name)
        
        if missing_cookies:
            logger.error(f"❌ Отсутствуют обязательные cookies: {missing_cookies}")
            logger.error("❌ БЕЗ ЭТИХ COOKIES ПАРСИНГ НЕВОЗМОЖЕН!")
            logger.error("❌ Получите cookies из браузера согласно инструкции в дашборде")
            return []
        else:
            logger.info(f"✅ Найдены обязательные cookies: {SEARCH_REQUEST_CONFIG.get('required_cookies', [])}")
            logger.info(f"✅ Всего cookies в сессии: {len(self.session.cookies)}")
            for cookie in self.session.cookies:
                logger.info(f"   - {cookie.name}: {cookie.value[:20]}...")
        
        try:
            rate_limiter.make_request()
            
            # Используем заголовки из конфигурации
            headers = SEARCH_REQUEST_CONFIG["headers"].copy()
            response = self.session.post(
                URLS["search_endpoint"],
                json=search_data,
                headers=headers,
                timeout=PARSING_SETTINGS["timeout_seconds"]
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Пробуем разные возможные поля для списка документов
                    documents = data.get('items', []) or data.get('documents', []) or data.get('results', []) or data.get('data', [])
                    logger.info(f"✅ Получено {len(documents)} документов на странице {page}")
                    return documents
                except ValueError as e:
                    logger.error(f"❌ Ошибка парсинга JSON ответа: {e}")
                    logger.error(f"Ответ сервера: {response.text[:500]}")
                    return []
            elif response.status_code == 403:
                logger.error("❌ Доступ запрещен (403) - возможно сработала anti-bot защита")
                logger.error("❌ Требуется обновить WASM токен или cookies")
                return []
            elif response.status_code == 451:
                logger.error("❌ ДОСТУП ЗАБЛОКИРОВАН (451) - Anti-bot защита активна!")
                logger.error("❌ Получите свежие cookies из браузера:")
                logger.error("   1. Откройте https://kad.arbitr.ru в браузере")
                logger.error("   2. F12 → Application → Cookies")
                logger.error("   3. Скопируйте pr_fp и wasm cookies")
                logger.error("❌ Cookies работают ограниченное время!")
                return []
            elif response.status_code == 429:
                logger.warning("⚠️ Слишком много запросов (429) - rate limiting")
                return []
            else:
                logger.error(f"❌ Ошибка поиска: {response.status_code}")
                logger.error(f"Ответ сервера: {response.text[:500]}")
                return []
                
        except DailyLimitExceeded as e:
            logger.warning(f"⚠️ Достигнут дневной лимит запросов: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске документов: {e}")
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
        success_count = 0  # Счетчик успешно скачанных файлов
        
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
                        # Увеличиваем счетчик успешных загрузок
                        success_count += 1
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
        
        return success_count
    
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
    
    def validate_endpoint_readiness(self):
        """Проверить готовность эндпоинта к использованию"""
        logger.info("🔍 Проверка готовности эндпоинта...")
        
        # Если anti-bot защита не требуется, эндпоинт готов
        if not SEARCH_REQUEST_CONFIG.get("anti_bot_warning", False):
            logger.info("ℹ️ Anti-bot защита не требуется - эндпоинт готов к использованию")
            return True
        
        # Проверяем наличие обязательных cookies
        missing_cookies = []
        for cookie_name in SEARCH_REQUEST_CONFIG.get("required_cookies", []):
            if not self.session.cookies.get(cookie_name):
                missing_cookies.append(cookie_name)
        
        if missing_cookies:
            logger.error(f"❌ Эндпоинт НЕ готов к использованию")
            logger.error(f"❌ Отсутствуют обязательные cookies: {missing_cookies}")
            logger.error("❌ Рекомендации:")
            logger.error("   1. Получите cookies из реального браузера")
            logger.error("   2. Используйте прокси с обходом anti-bot")
            logger.error("   3. Реализуйте генерацию WASM токена")
            return False
        
        # Делаем тестовый запрос
        if self.check_anti_bot_protection():
            logger.info("✅ Эндпоинт готов к использованию")
            return True
        else:
            logger.error("❌ Эндпоинт НЕ готов к использованию")
            logger.error("❌ Anti-bot защита блокирует запросы")
            return False

def create_batch_parser():
    """Factory функция для создания экземпляра BatchParser"""
    return BatchParser()


# Для обратной совместимости (deprecated - используйте create_batch_parser())
def get_batch_parser():
    """Получить экземпляр BatchParser (deprecated)"""
    import warnings
    warnings.warn("get_batch_parser() deprecated, используйте create_batch_parser()", DeprecationWarning)
    return create_batch_parser()
