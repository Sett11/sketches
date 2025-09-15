"""
Автоматический сбор cookies через Puppeteer
"""
import subprocess
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Optional

from config.settings import DOCS_DIR, LOGS_DIR
from src.utils.logger import logger


class CookieAutomation:
    """
    Автоматический сбор cookies с kad.arbitr.ru через Puppeteer
    """
    
    def __init__(self):
        self.script_path = os.path.join(os.path.dirname(__file__), 'cookie_extractor_main.js')
        self.extracted_cookies = {}
        
    def extract_cookies(self, save_to_file: bool = True) -> Dict:
        """Автоматически извлечь cookies с kad.arbitr.ru"""
        try:
            logger.info("🍪 Начинаем автоматический сбор cookies...")
            
            # Вызываем JavaScript скрипт для сбора cookies
            result = self._run_cookie_extraction()
            
            if result.get('success'):
                self.extracted_cookies = result.get('cookies', {})
                
                # Валидируем cookies
                validation = self._validate_cookies()
                
                if validation['isValid']:
                    logger.info("✅ Cookies успешно собраны и валидированы")
                    
                    # Сохраняем в файл если требуется
                    if save_to_file:
                        self._save_cookies_to_file()
                    
                    return {
                        'success': True,
                        'cookies': self.extracted_cookies,
                        'validation': validation,
                        'message': 'Cookies успешно собраны автоматически'
                    }
                else:
                    logger.warning("⚠️ Cookies собраны, но есть проблемы с валидацией")
                    return {
                        'success': False,
                        'cookies': self.extracted_cookies,
                        'validation': validation,
                        'message': 'Cookies собраны, но требуют проверки'
                    }
            else:
                logger.error(f"❌ Ошибка сбора cookies: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error'),
                    'message': 'Не удалось собрать cookies автоматически'
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка автоматического сбора cookies: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Критическая ошибка при сборе cookies'
            }
    
    def get_cookies(self) -> Dict:
        """Получить собранные cookies"""
        return self.extracted_cookies
    
    def _run_cookie_extraction(self) -> Dict:
        """Запуск JavaScript скрипта для сбора cookies"""
        try:
            # Выполняем Node.js скрипт
            cmd = ['node', self.script_path]
            
            logger.info("🚀 Запускаем автоматический сбор cookies...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 минуты таймаут
                cwd=os.path.dirname(self.script_path)
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Если JSON парсинг не удался, пытаемся извлечь cookies из текста
                    logger.warning("⚠️ Не удалось распарсить JSON ответ, извлекаем cookies из текста")
                    return self._extract_cookies_from_text(result.stdout)
            else:
                error_msg = result.stderr or result.stdout or "Неизвестная ошибка"
                logger.error(f"Ошибка выполнения cookie extractor: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут сбора cookies")
            return {'success': False, 'error': 'Таймаут выполнения'}
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения cookie extractor: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_cookies_from_text(self, text: str) -> Dict:
        """Извлечение cookies из текстового вывода"""
        try:
            # Ищем JSON блок в тексте
            import re
            
            # Паттерн для поиска JSON с cookies
            json_pattern = r'\{[^{}]*"[^"]*"[^{}]*\}'
            matches = re.findall(json_pattern, text)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and any(key in data for key in ['pr_fp', 'wasm', 'PHPSESSID']):
                        return {'success': True, 'cookies': data}
                except json.JSONDecodeError:
                    continue
            
            return {'success': False, 'error': 'Не удалось извлечь cookies из ответа'}
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения cookies из текста: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_cookies(self) -> Dict:
        """Валидация собранных cookies"""
        validation = {
            'isValid': True,
            'errors': [],
            'warnings': [],
            'foundCookies': list(self.extracted_cookies.keys()),
            'criticalCookies': {}
        }

        # Проверяем критически важные cookies
        critical_cookies = {
            'pr_fp': 'Основной fingerprint cookie',
            'wasm': 'WebAssembly токен (опциональный)',
            'PHPSESSID': 'PHP сессия (опциональный)',
            'ASP.NET_SessionId': 'ASP.NET сессия (опциональный)'
        }

        for cookie_name, description in critical_cookies.items():
            if self.extracted_cookies.get(cookie_name):
                validation['criticalCookies'][cookie_name] = {
                    'found': True,
                    'description': description,
                    'value': self.extracted_cookies[cookie_name][:20] + '...'
                }
            else:
                if cookie_name == 'pr_fp':
                    validation['isValid'] = False
                    validation['errors'].append(f"Отсутствует критически важный cookie: {cookie_name} ({description})")
                else:
                    validation['warnings'].append(f"Отсутствует опциональный cookie: {cookie_name} ({description})")

        # Проверяем общее количество cookies
        total_cookies = len(self.extracted_cookies)
        if total_cookies < 5:
            validation['warnings'].append(f"Мало cookies ({total_cookies}), возможно anti-bot защита активна")
        elif total_cookies > 50:
            validation['warnings'].append(f"Много cookies ({total_cookies}), возможно есть лишние")

        return validation
    
    def _save_cookies_to_file(self):
        """Сохранение cookies в файл"""
        try:
            os.makedirs(DOCS_DIR, exist_ok=True)
            
            # Сохраняем в основной файл
            cookies_file = os.path.join(DOCS_DIR, 'auto_extracted_cookies.json')
            
            # Создаем резервную копию если файл существует
            if os.path.exists(cookies_file):
                backup_file = os.path.join(DOCS_DIR, f'cookies_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                os.rename(cookies_file, backup_file)
                logger.info(f"📁 Создана резервная копия cookies: {backup_file}")
            
            # Сохраняем новые cookies
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'extracted_at': datetime.now().isoformat(),
                    'cookies': self.extracted_cookies,
                    'validation': self._validate_cookies()
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Cookies сохранены в файл: {cookies_file}")
            
            # Также сохраняем в файл для совместимости с существующим кодом
            compatibility_file = os.path.join(DOCS_DIR, 'cookies.json')
            with open(compatibility_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_cookies, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Cookies сохранены для совместимости: {compatibility_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения cookies: {e}")
    
    def is_cookies_valid(self) -> bool:
        """Проверка валидности cookies"""
        validation = self._validate_cookies()
        return validation['isValid'] and len(self.extracted_cookies) > 0
    
    def get_cookies_summary(self) -> str:
        """Получить краткое описание cookies"""
        if not self.extracted_cookies:
            return "❌ Cookies не собраны"
        
        validation = self._validate_cookies()
        critical_count = len(validation['criticalCookies'])
        total_count = len(self.extracted_cookies)
        
        status = "✅ Валидны" if validation['isValid'] else "⚠️ Требуют проверки"
        
        return f"""🍪 Cookies: {status}
📊 Всего cookies: {total_count}
🔑 Критически важных: {critical_count}
⏰ Собраны: {datetime.now().strftime('%H:%M:%S')}"""


def create_cookie_automation() -> CookieAutomation:
    """Factory функция для создания экземпляра CookieAutomation"""
    return CookieAutomation()
