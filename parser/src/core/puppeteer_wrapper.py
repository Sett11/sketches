"""
Python обертка для Puppeteer парсера
"""
import subprocess
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import DOCS_DIR, LOGS_DIR
from src.utils.logger import logger


class PuppeteerWrapper:
    """
    Обертка для вызова JavaScript Puppeteer парсера из Python
    """
    
    def __init__(self):
        self.script_path = os.path.join(os.path.dirname(__file__), 'puppeteer_main.js')
        self.cookies_temp_file = None
        
    def _create_temp_cookies_file(self, cookies_dict: Dict) -> str:
        """Создает временный файл с cookies"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(cookies_dict, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()
        return temp_file.name
    
    def _cleanup_temp_files(self):
        """Удаляет временные файлы"""
        if self.cookies_temp_file and os.path.exists(self.cookies_temp_file):
            try:
                os.unlink(self.cookies_temp_file)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл cookies: {e}")
    
    def init_browser(self) -> bool:
        """Инициализация браузера"""
        try:
            logger.info("🚀 Инициализация Puppeteer браузера...")
            
            # Вызываем JavaScript функцию инициализации
            result = self._run_js_command('init')
            
            if result.get('success'):
                logger.info("✅ Браузер инициализирован успешно")
                return True
            else:
                logger.error(f"❌ Ошибка инициализации браузера: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации браузера: {e}")
            return False
    
    def load_cookies(self, cookies_dict: Dict) -> bool:
        """Загрузка cookies"""
        try:
            logger.info("🍪 Загрузка cookies в Puppeteer...")
            
            # Создаем временный файл с cookies
            self.cookies_temp_file = self._create_temp_cookies_file(cookies_dict)
            
            # Вызываем JavaScript функцию загрузки cookies
            result = self._run_js_command('loadCookies', cookies_file=self.cookies_temp_file)
            
            if result.get('success'):
                logger.info("✅ Cookies загружены успешно")
                return True
            else:
                logger.error(f"❌ Ошибка загрузки cookies: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки cookies: {e}")
            return False
        finally:
            self._cleanup_temp_files()
    
    def search_documents(self, search_params: Dict) -> Optional[Dict]:
        """Поиск документов"""
        try:
            logger.info("🔍 Выполняем поиск документов через Puppeteer...")
            
            # Вызываем JavaScript функцию поиска
            result = self._run_js_command('searchDocuments', params=search_params)
            
            if result.get('success'):
                logger.info("✅ Поиск выполнен успешно")
                return result.get('data')
            else:
                logger.error(f"❌ Ошибка поиска документов: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска документов: {e}")
            return None
    
    def process_date_range(self, start_date: str, end_date: str, max_pages: int = 40) -> List[Dict]:
        """Обработка диапазона дат"""
        try:
            logger.info(f"📅 Обрабатываем диапазон дат: {start_date} - {end_date}")
            
            # Вызываем JavaScript функцию обработки диапазона дат
            result = self._run_js_command('processDateRange', 
                                        start_date=start_date, 
                                        end_date=end_date, 
                                        max_pages=max_pages)
            
            if result.get('success'):
                documents = result.get('data', [])
                logger.info(f"✅ Обработка завершена. Найдено документов: {len(documents)}")
                return documents
            else:
                logger.error(f"❌ Ошибка обработки диапазона дат: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки диапазона дат: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        try:
            result = self._run_js_command('getStats')
            
            if result.get('success'):
                return result.get('data', {})
            else:
                logger.error(f"❌ Ошибка получения статистики: {result.get('error')}")
                return {'total_documents': 0, 'last_update': None}
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {'total_documents': 0, 'last_update': None}
    
    def close_browser(self):
        """Закрытие браузера"""
        try:
            logger.info("🔒 Закрытие браузер...")
            result = self._run_js_command('close')
            
            if result.get('success'):
                logger.info("✅ Браузер закрыт успешно")
            else:
                logger.warning(f"⚠️ Предупреждение при закрытии браузера: {result.get('error')}")
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при закрытии браузера: {e}")
        finally:
            self._cleanup_temp_files()
    
    def _run_js_command(self, command: str, **kwargs) -> Dict:
        """Выполнение JavaScript команды"""
        try:
            # Подготавливаем аргументы для JavaScript
            args = [command]
            
            for key, value in kwargs.items():
                if isinstance(value, (dict, list)):
                    # Для сложных объектов создаем временный файл
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                    json.dump(value, temp_file, ensure_ascii=False, indent=2)
                    temp_file.close()
                    args.extend([f'--{key}', temp_file.name])
                else:
                    args.extend([f'--{key}', str(value)])
            
            # Выполняем Node.js скрипт
            cmd = ['node', self.script_path] + args
            
            logger.debug(f"Выполняем команду: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 минут таймаут
                cwd=os.path.dirname(self.script_path)
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {'success': True, 'data': result.stdout}
            else:
                error_msg = result.stderr or result.stdout or "Неизвестная ошибка"
                logger.error(f"Ошибка выполнения JavaScript: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут выполнения JavaScript команды")
            return {'success': False, 'error': 'Таймаут выполнения'}
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения JavaScript команды: {e}")
            return {'success': False, 'error': str(e)}
