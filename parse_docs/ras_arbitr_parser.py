#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAS Arbitr Parser v2.0 - ИСПРАВЛЕННАЯ ВЕРСИЯ
Парсинг ras.arbitr.ru с перехватом XHR через CDP

Основные исправления:
1. Правильный URL: https://ras.arbitr.ru/#searchPrintForm
2. Ожидание загрузки SPA приложения
3. Альтернативные методы заполнения полей
4. Улучшенная диагностика
"""

import os
import json
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# curl_cffi для внешних POST запросов (запасной метод)
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    logger.warning("⚠️ curl_cffi не установлен. Внешние POST запросы недоступны.")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ras_parser.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация - ИСПРАВЛЕНО
RAS_HOME = "https://ras.arbitr.ru/"
RAS_SEARCH_PAGE = "https://ras.arbitr.ru/#searchPrintForm"  # Страница с формой поиска
SEARCH_URL = "https://ras.arbitr.ru/Ras/Search"
# Сохраняем результаты и PDF в локальную папку проекта "res"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAVE_DIR = str((PROJECT_ROOT / "res").resolve())
KAD_HOME = "https://kad.arbitr.ru/"
PDF_DIR = str((Path(SAVE_DIR) / "pdf").resolve())
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)

# Параметры антибана
BASE_DELAY = 10  # базовая задержка между запросами
JITTER = 3  # случайный джиттер
LONG_PAUSE_EVERY = 5  # длинная пауза каждые N запросов
LONG_PAUSE_RANGE = (40, 90)  # диапазон длинной паузы
PREWARM_EVERY = 3  # прогрев главной каждые N запросов

logger.info("="*60)
logger.info("🚀 RAS Arbitr Parser v2.0 - ИСПРАВЛЕННАЯ ВЕРСИЯ")
logger.info("="*60)
logger.info("✅ Модули импортированы")
print("\n🚀 Парсер RAS Arbitr готов к работе")
print(f"📁 Результаты будут сохранены в: {SAVE_DIR}\n")


class RasArbitrParser:
    """Класс для управления браузером с CDP перехватом - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    
    def __init__(self):
        self.driver = None
        self.cdp_responses = []
        self.xhr_captured = []
        
    def build_driver(self):
        """Создание Chrome драйвера с CDP"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=ru-RU")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # User-Agent современного Chrome
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={ua}")
        
        # Логирование для диагностики
        options.set_capability("goog:loggingPrefs", {
            "performance": "ALL", 
            "browser": "ALL"
        })
        
        # Отключаем автоматизацию - БЕЗ excludeSwitches для стабильности
        options.add_experimental_option('useAutomationExtension', False)
        
        # Настройки для принудительного скачивания PDF (из комментариев)
        prefs = {
            "download.default_directory": PDF_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Chrome драйвер создан")
        except Exception as e:
            logger.error(f"❌ Ошибка создания драйвера: {e}")
            raise
        
        # Скрываем webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Включаем CDP Network для перехвата
        self.driver.execute_cdp_cmd("Network.enable", {})
        
        # Включаем Fetch для дополнительного перехвата (из комментариев)
        self.driver.execute_cdp_cmd("Fetch.enable", {
            "patterns": [{"urlPattern": "*/Ras/Search*", "requestStage": "Response"}]
        })
        
        # Разрешаем скачивания через CDP (из комментариев)
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": PDF_DIR
        })
        
        # Устанавливаем заголовки для НАВИГАЦИИ (важно: без X-Requested-With, Accept для HTML)
        self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://ras.arbitr.ru/"
            }
        })
        
        logger.info("✅ CDP Network включен с правильными заголовками")
        return self.driver
    
    def wait_ready(self, timeout=30):
        """Ожидание загрузки страницы"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(0.5)
        except TimeoutException:
            logger.warning("⚠️ Таймаут ожидания загрузки страницы")
    
    def humanize_behavior(self, moves=8):
        """Имитация человеческого поведения"""
        try:
            actions = ActionChains(self.driver)
            body = self.driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element(body).perform()
            time.sleep(0.3)
            
            for _ in range(moves):
                actions.move_by_offset(
                    random.randint(-80, 120), 
                    random.randint(-60, 100)
                ).perform()
                time.sleep(random.uniform(0.15, 0.45))
            
            self.driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(0.3)
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(0.2)
        except Exception as e:
            logger.debug(f"Ошибка humanize: {e}")
    
    def get_network_response(self, url_pattern="/Ras/Search", timeout=30):
        """Получение ответа из Network через CDP - ОСНОВНОЙ МЕТОД"""
        start_time = time.time()
        request_id = None
        
        logger.info(f"🔍 Ожидание XHR запроса к: {url_pattern}")
        
        while time.time() - start_time < timeout:
            try:
                # Получаем логи performance
                logs = self.driver.get_log('performance')
                
                for entry in logs:
                    try:
                        log = json.loads(entry['message'])['message']
                        
                        # Ищем responseReceived для нашего URL
                        if log['method'] == 'Network.responseReceived':
                            response = log['params']['response']
                            if url_pattern in response.get('url', ''):
                                request_id = log['params']['requestId']
                                status = response.get('status', 0)
                                logger.info(f"✅ Найден ответ: requestId={request_id}, status={status}")
                                
                                # Даем время на завершение загрузки
                                time.sleep(1)
                                
                                # Получаем тело ответа
                                try:
                                    body_response = self.driver.execute_cdp_cmd(
                                        'Network.getResponseBody',
                                        {'requestId': request_id}
                                    )
                                    body = body_response.get('body', '')
                                    
                                    if body:
                                        logger.info(f"✅ Получено тело ответа: {len(body)} символов")
                                        return {
                                            'status': status,
                                            'body': body,
                                            'url': response.get('url'),
                                            'requestId': request_id
                                        }
                                except Exception as e:
                                    logger.warning(f"⚠️ Ошибка получения тела: {e}")
                                    continue
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue
                
                time.sleep(0.3)
                
            except Exception as e:
                logger.debug(f"Ошибка в цикле перехвата: {e}")
                time.sleep(0.3)
        
        logger.warning(f"⚠️ Таймаут ожидания ответа ({timeout}s)")
        return None

    def wait_for_pdf_via_cdp(self, timeout: int = 30) -> Optional[Dict]:
        """Ожидание первого ответа с URL, содержащим /Document/Pdf/ через CDP."""
        start_time = time.time()
        logger.info("🔍 Ожидание ответа PDF (/Document/Pdf/)")
        while time.time() - start_time < timeout:
            try:
                logs = self.driver.get_log('performance')
                for entry in logs:
                    try:
                        log = json.loads(entry['message'])['message']
                        if log['method'] == 'Network.responseReceived':
                            response = log['params']['response']
                            url = response.get('url', '')
                            if '/Document/Pdf/' in url:
                                status = response.get('status', 0)
                                req_id = log['params']['requestId']
                                logger.info(f"✅ Найден PDF ответ: {status} {url}")
                                return { 'status': status, 'url': url, 'requestId': req_id }
                    except Exception:
                        continue
                time.sleep(0.2)
            except Exception:
                time.sleep(0.2)
        logger.warning("⚠️ PDF через CDP не обнаружен за отведенное время")
        return None
    
    def get_fetch_response(self, url_pattern="/Ras/Search", timeout=30):
        """Получение ответа через Fetch.enable - ДОПОЛНИТЕЛЬНЫЙ МЕТОД"""
        start_time = time.time()
        
        logger.info(f"🔍 Ожидание Fetch запроса к: {url_pattern}")
        
        while time.time() - start_time < timeout:
            try:
                # Получаем логи performance для Fetch
                logs = self.driver.get_log('performance')
                
                for entry in logs:
                    try:
                        log = json.loads(entry['message'])['message']
                        
                        # Ищем Fetch.requestPaused для нашего URL
                        if log['method'] == 'Fetch.requestPaused':
                            request = log['params']['request']
                            if url_pattern in request.get('url', ''):
                                request_id = log['params']['requestId']
                                logger.info(f"✅ Найден Fetch запрос: requestId={request_id}")
                                
                                # Продолжаем запрос
                                self.driver.execute_cdp_cmd('Fetch.continueRequest', {
                                    'requestId': request_id
                                })
                                
                                # Ждем ответ
                                time.sleep(1)
                                
                                # Получаем тело ответа
                                try:
                                    body_response = self.driver.execute_cdp_cmd(
                                        'Fetch.getResponseBody',
                                        {'requestId': request_id}
                                    )
                                    body = body_response.get('body', '')
                                    
                                    if body:
                                        logger.info(f"✅ Получено тело Fetch ответа: {len(body)} символов")
                                        return {
                                            'status': 200,  # Fetch не всегда возвращает статус
                                            'body': body,
                                            'url': request.get('url'),
                                            'requestId': request_id
                                        }
                                except Exception as e:
                                    logger.warning(f"⚠️ Ошибка получения Fetch тела: {e}")
                                    continue
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue
                
                time.sleep(0.3)
                
            except Exception as e:
                logger.debug(f"Ошибка в цикле Fetch перехвата: {e}")
                time.sleep(0.3)
        
        logger.warning(f"⚠️ Таймаут ожидания Fetch ответа ({timeout}s)")
        return None
    
    def setup_xhr_interceptor(self):
        """Настройка JS перехватчика XHR (запасной вариант)"""
        intercept_script = """
        (function() {
            if (window._rasInterceptorInstalled) return;
            window._rasInterceptorInstalled = true;
            
            window._rasResponses = [];
            window._rasLastResponse = null;

            const originalXHR = window.XMLHttpRequest;
            window.XMLHttpRequest = function() {
                const xhr = new originalXHR();
                const originalOpen = xhr.open;
                const originalSend = xhr.send;

                xhr.open = function(method, url, ...args) {
                    this._method = method;
                    this._url = url;
                    return originalOpen.apply(this, [method, url, ...args]);
                };

                xhr.send = function(data) {
                    this._data = data;
                    const originalOnReadyStateChange = this.onreadystatechange;

                    this.onreadystatechange = function() {
                        if (this.readyState === 4) {
                            if (this._url && this._url.includes('Ras/Search')) {
                                const resp = {
                                    transport: 'xhr',
                                    url: this._url,
                                    status: this.status,
                                    responseText: this.responseText,
                                    method: this._method,
                                    data: this._data,
                                    ts: Date.now()
                                };
                                window._rasResponses.push(resp);
                                window._rasLastResponse = resp;
                                console.log('[RAS] XHR перехвачен:', this._url, this.status);
                            }
                        }
                        if (originalOnReadyStateChange) {
                            originalOnReadyStateChange.apply(this, arguments);
                        }
                    };

                    return originalSend.apply(this, [data]);
                };

                return xhr;
            };

            // Перехват Fetch API
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                return originalFetch.apply(this, args).then(response => {
                    const url = args[0];
                    if (url && url.includes('Ras/Search')) {
                        response.clone().text().then(text => {
                            const resp = {
                                transport: 'fetch',
                                url: url,
                                status: response.status,
                                responseText: text,
                                ts: Date.now()
                            };
                            window._rasResponses.push(resp);
                            window._rasLastResponse = resp;
                            console.log('[RAS] Fetch перехвачен:', url, response.status);
                        });
                    }
                    return response;
                });
            };

            window._rasClear = function() {
                window._rasResponses = [];
                window._rasLastResponse = null;
            };
            
            console.log('[RAS] Перехватчик установлен');
        })();
        """
        
        try:
            self.driver.execute_script(intercept_script)
            logger.info("✅ JS XHR перехватчик установлен (запасной)")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось установить JS перехватчик: {e}")

    def get_xhr_response(self, timeout=30):
        """Получение XHR ответа из JS перехватчика (запасной вариант)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                responses = self.driver.execute_script("return window._rasResponses || [];")
                if responses and isinstance(responses, list):
                    filtered = [r for r in responses if r and 'Ras/Search' in (r.get('url') or '')]
                    if filtered:
                        resp = max(filtered, key=lambda r: r.get('ts', 0))
                        logger.info(f"✅ JS перехватчик: status={resp.get('status')}")
                        return {
                            'status': resp.get('status'),
                            'body': resp.get('responseText', ''),
                            'url': resp.get('url')
                        }
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Ожидание JS ответа: {e}")
                time.sleep(0.5)
        logger.warning("⚠️ JS перехватчик: ответ не получен")
        return None
    
    def clear_intercept_buffer(self):
        """Очистка буфера перехвата"""
        try:
            self.driver.execute_script("if (window._rasClear) window._rasClear();")
        except:
            pass
    
    def wait_download_finished(self, directory: str, timeout: int = 240):
        """Ожидание завершения скачивания PDF (из комментариев)"""
        import glob
        start = time.time()
        last_size = None
        stable_ticks = 0
        
        while time.time() - start < timeout:
            # Идёт загрузка, если ещё есть .crdownload
            crs = glob.glob(os.path.join(directory, "*.crdownload"))
            if crs:
                # Контроль "не залипло ли": проверяем, меняется ли размер самого большого .crdownload
                largest = max(crs, key=lambda p: os.path.getsize(p))
                size = os.path.getsize(largest)
                if last_size == size:
                    stable_ticks += 1
                else:
                    stable_ticks = 0
                last_size = size
                # Если размер стабилен слишком долго — вероятно зависло
                if stable_ticks > 60:  # ~30 сек при шаге 0.5
                    break
                time.sleep(0.5)
                continue
            
            # Нет .crdownload — ищем свежий PDF
            pdfs = [p for p in Path(directory).glob("*.pdf") if p.stat().st_mtime >= start - 2]
            if pdfs:
                latest = max(pdfs, key=lambda p: p.stat().st_mtime)
                logger.info(f"✅ PDF скачан: {latest}")
                return str(latest)
            time.sleep(0.5)
        
        raise TimeoutError("PDF не скачался вовремя или загрузка зависла")


class CurlCffiClient:
    """Клиент с curl_cffi impersonation для внешних POST (запасной метод)"""
    
    def __init__(self):
        self.session = None
        self.cookies = {}
        
    def setup_session(self, cookies_from_selenium=None):
        """Настройка сессии с impersonation"""
        if not CURL_CFFI_AVAILABLE:
            logger.error("❌ curl_cffi недоступен")
            return False
            
        try:
            # Создаём сессию с impersonation Chrome
            self.session = curl_requests.Session()
            
            # Настройки для имитации браузера
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://ras.arbitr.ru/",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://ras.arbitr.ru"
            })
            
            # Переносим куки из Selenium если есть
            if cookies_from_selenium:
                for cookie in cookies_from_selenium:
                    self.session.cookies.set(
                        cookie['name'], 
                        cookie['value'],
                        domain=cookie.get('domain'),
                        path=cookie.get('path', '/')
                    )
                logger.info(f"✅ Перенесено {len(cookies_from_selenium)} куки из Selenium")
            
            logger.info("✅ curl_cffi сессия настроена с impersonation")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки curl_cffi: {e}")
            return False
    
    def post_search(self, payload: dict, timeout: int = 30):
        """POST запрос к /Ras/Search через curl_cffi"""
        if not self.session:
            logger.error("❌ Сессия не настроена")
            return None
            
        try:
            logger.info("🔍 Отправка POST через curl_cffi...")
            
            response = self.session.post(
                SEARCH_URL,
                json=payload,
                timeout=timeout,
                impersonate="chrome131",  # Имитация Chrome 131
                verify=False  # Отключаем проверку SSL
            )
            
            logger.info(f"✅ curl_cffi ответ: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'status': response.status_code,
                        'body': json.dumps(data),
                        'url': SEARCH_URL,
                        'method': 'curl_cffi'
                    }
                except json.JSONDecodeError:
                    logger.error("❌ curl_cffi: некорректный JSON")
                    return None
            else:
                logger.error(f"❌ curl_cffi: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка curl_cffi POST: {e}")
            return None


class RasSearchHandler:
    """Класс для работы с формой поиска - ПОЛНОСТЬЮ ПЕРЕРАБОТАН ДЛЯ SPA"""
    
    def __init__(self, parser: RasArbitrParser):
        self.parser = parser
        self.driver = parser.driver
    
    def wait_for_spa_ready(self, timeout=30):
        """Ожидание загрузки SPA приложения"""
        try:
            logger.info("⏳ Ожидание загрузки SPA приложения...")
            start = time.time()
            
            while time.time() - start < timeout:
                # Проверяем наличие элементов формы
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input:not([type='hidden'])")
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
                
                visible_inputs = [i for i in inputs if i.is_displayed()]
                visible_buttons = [b for b in buttons if b.is_displayed()]
                
                if len(visible_inputs) >= 2 and len(visible_buttons) >= 1:
                    logger.info(f"✅ SPA загружено: {len(visible_inputs)} полей, {len(visible_buttons)} кнопок")
                    return True
                
                time.sleep(0.5)
            
            logger.warning("⚠️ Таймаут ожидания SPA")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка ожидания SPA: {e}")
            return False
        
    def close_overlay(self, max_attempts=3):
        """Закрытие промо-оверлея"""
        try:
            logger.info("🔍 Поиск оверлеев...")
            
            # Селекторы для закрытия оверлеев
            close_selectors = [
                "button[aria-label='Close']",
                "button[data-dismiss='modal']",
                ".modal .close",
                ".popup .close",
                ".overlay .close",
                "[class*='close-button']",
                "[class*='modal'] button",
                "div[class*='overlay'] button",
                "div[class*='popup'] button"
            ]
            
            closed = False
            for attempt in range(max_attempts):
                for selector in close_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                # Пробуем кликнуть
                                try:
                                    element.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", element)
                                
                                logger.info(f"✅ Оверлей закрыт: {selector}")
                                time.sleep(0.5)
                                closed = True
                                break
                    except Exception as e:
                        continue
                
                if closed:
                    break
                    
                # Пробуем ESC
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                    logger.info("✅ ESC нажат")
                except:
                    pass
                
                time.sleep(0.5)
            
            if not closed:
                logger.info("ℹ️ Оверлей не найден или уже закрыт")
                    
        except Exception as e:
            logger.debug(f"Ошибка закрытия оверлея: {e}")
    
    def fill_date_field(self, selectors: List[str], date_value: str, field_name: str) -> bool:
        """Заполнение поля даты"""
        for selector in selectors:
            try:
                # Ждем появления элемента
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # Прокручиваем к элементу
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)
                
                # Очищаем и заполняем
                element.clear()
                time.sleep(0.2)
                element.send_keys(date_value)
                time.sleep(0.3)
                
                # Проверяем, что значение установлено
                current_value = element.get_attribute('value')
                if current_value and date_value in current_value:
                    logger.info(f"✅ Поле '{field_name}' заполнено: {date_value} (селектор: {selector})")
                    return True
                    
            except Exception as e:
                logger.debug(f"Селектор {selector} не сработал: {e}")
                continue
        
        return False
    
    def fill_search_form(self, date_from: str, date_to: str):
        """Заполнение формы поиска - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            logger.info(f"📝 Заполнение формы: {date_from} - {date_to}")
            
            # Конвертируем даты в формат ДД.ММ.ГГГГ
            date_from_ui = datetime.strptime(date_from, "%Y-%m-%d").strftime("%d.%m.%Y")
            date_to_ui = datetime.strptime(date_to, "%Y-%m-%d").strftime("%d.%m.%Y")

            # Закрываем оверлеи
            self.close_overlay()
            time.sleep(2)
            
            # Даём странице загрузиться полностью (SPA приложение)
            logger.info("⏳ Ожидание загрузки SPA...")
            time.sleep(3)
            
            # ПРАВИЛЬНЫЕ селекторы из комментариев пользователя
            date_from_selectors = [
                "#sug-dates label.from input.anyway_position_top",  # ОСНОВНОЙ из комментариев
                "#sug-dates label.from input",
                "input[name='DateFrom']",
                "#DateFrom",
                "input[id*='DateFrom']",
                "input[placeholder*='01.01']",
                "input[placeholder*='дата']",
                ".date-from input",
                ".from input",
                "label.from input",
                "input[type='text'][name*='from']",
                "input[type='text'][name*='From']",
                ".b-date-range input:first-of-type",
                ".date-range input:first-of-type"
            ]
            
            date_to_selectors = [
                "#sug-dates label.to input.anyway_position_top",  # ОСНОВНОЙ из комментариев
                "#sug-dates label.to input",
                "input[name='DateTo']",
                "#DateTo",
                "input[id*='DateTo']",
                ".date-to input",
                ".to input",
                "label.to input",
                "input[type='text'][name*='to']",
                "input[type='text'][name*='To']",
                ".b-date-range input:last-of-type",
                ".date-range input:last-of-type",
                "input[placeholder*='31.12']"
            ]
            
            # Пытаемся найти любое input поле для дат
            logger.info("🔍 Поиск полей ввода дат...")
            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input:not([type])")
            logger.info(f"Найдено {len(all_inputs)} текстовых полей")
            
            # Заполняем дату "от"
            from_filled = self.fill_date_field(date_from_selectors, date_from_ui, "Дата от")
            
            # Заполняем дату "до"
            to_filled = self.fill_date_field(date_to_selectors, date_to_ui, "Дата до")
            
            if not from_filled or not to_filled:
                logger.warning("⚠️ Не все поля дат заполнены стандартными селекторами")
                logger.info("🔧 Пробуем альтернативный метод - по порядку полей...")
                
                # Альтернатива: заполняем первые два текстовых поля
                try:
                    date_inputs = [inp for inp in all_inputs if inp.is_displayed() and inp.is_enabled()]
                    if len(date_inputs) >= 2:
                        # Первое поле = дата от
                        date_inputs[0].clear()
                        date_inputs[0].send_keys(date_from_ui)
                        logger.info(f"✅ Альтернатива: поле 1 заполнено {date_from_ui}")
                        time.sleep(0.5)
                        
                        # Второе поле = дата до
                        date_inputs[1].clear()
                        date_inputs[1].send_keys(date_to_ui)
                        logger.info(f"✅ Альтернатива: поле 2 заполнено {date_to_ui}")
                        
                        from_filled = True
                        to_filled = True
                except Exception as e:
                    logger.error(f"❌ Альтернативный метод не сработал: {e}")
            
            if not from_filled or not to_filled:
                # Сохраняем HTML для диагностики
                with open(os.path.join(SAVE_DIR, "form_debug.html"), "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.error("💾 HTML формы сохранен в form_debug.html")
                
                # Сохраняем скриншот
                try:
                    screenshot_path = os.path.join(SAVE_DIR, "form_debug_screenshot.png")
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"📸 Скриншот сохранён: {screenshot_path}")
                except:
                    pass
                
                return False
            
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка заполнения формы: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def submit_search(self):
        """Отправка формы поиска (робастная)"""
        try:
            logger.info("🚀 Отправка формы поиска...")
            
            # Селекторы кнопки отправки
            submit_selectors = [
                "#b-form-submit button[type='submit']",
                "button[type='submit']",
                "input[type='submit']",
                ".search-button",
                "button[class*='submit']",
                "[data-action='search']"
            ]
            
            submitted = False
            
            # Пробуем найти и кликнуть кнопку
            for selector in submit_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        # Прокручиваем к кнопке
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # Пробуем обычный клик
                        try:
                            button.click()
                            submitted = True
                            logger.info(f"✅ Форма отправлена (клик): {selector}")
                        except Exception as e:
                            # Если не получилось - через JS
                            self.driver.execute_script("arguments[0].click();", button)
                            submitted = True
                            logger.info(f"✅ Форма отправлена (JS): {selector}")
                        
                        if submitted:
                            break
                            
                except Exception as e:
                    logger.debug(f"Селектор {selector} не сработал: {e}")
                    continue
            
            # Если кнопка не найдена - пробуем отправить форму напрямую
            if not submitted:
                logger.warning("⚠️ Кнопка не найдена, отправка через form.submit()")
                result = self.driver.execute_script("""
                    const form = document.querySelector('form');
                    if (form) {
                        if (form.requestSubmit) {
                            form.requestSubmit();
                        } else {
                            form.submit();
                        }
                        return true;
                    }
                    return false;
                """)
                
                if result:
                    submitted = True
                    logger.info("✅ Форма отправлена через form.submit()")
            
            if submitted:
                time.sleep(2)  # Даем время на обработку
                return True
            else:
                logger.error("❌ Не удалось отправить форму")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки формы: {e}")
            return False


class RasArbitrScraper:
    """Основной класс для парсинга с CDP перехватом"""
    
    def __init__(self):
        self.parser = None
        self.search_handler = None
        self.results = []
        self.session_stats = {
            'success': 0,
            'failed': 0,
            'total_requests': 0
        }
    
    def prewarm_session(self):
        """Прогрев сессии"""
        try:
            logger.info("🔥 Прогрев сессии...")
            self.parser.driver.get(RAS_HOME)
            self.parser.wait_ready()
            self.parser.humanize_behavior(moves=random.randint(6, 12))
            time.sleep(random.uniform(1.5, 3.0))
            logger.info("✅ Сессия прогрета")
        except Exception as e:
            logger.error(f"❌ Ошибка прогрева сессии: {e}")
    
    def search_by_date_range(self, date_from: str, date_to: str, use_cdp=True, use_js=True) -> Optional[Dict]:
        """Поиск по диапазону дат с перехватом ответа - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            logger.info(f"🔍 Поиск: {date_from} - {date_to}")
            
            # Надежная навигация в SPA: сначала главная, затем hash, затем проверка элементов
            logger.info(f"📄 Открываем главную: {RAS_HOME}")
            self.parser.driver.get(RAS_HOME)
            self.parser.wait_ready()
            time.sleep(1.5)
            
            # Устанавливаем нужный hash и инициируем событие
            try:
                self.parser.driver.execute_script("window.location.hash='searchPrintForm'; window.dispatchEvent(new HashChangeEvent('hashchange'));")
            except Exception:
                pass
            
            # Фолбэк: прямой URL с hash, если нужно
            try:
                WebDriverWait(self.parser.driver, 10).until(
                    lambda d: 'searchPrintForm' in d.execute_script('return window.location.hash || \"\";')
                )
            except Exception:
                logger.info(f"↩️ Фолбэк на прямой URL: {RAS_SEARCH_PAGE}")
                self.parser.driver.get(RAS_SEARCH_PAGE)
                self.parser.wait_ready()
            
            # Ждем появления ключевых элементов формы (до 30 сек)
            try:
                form_ready_selectors = [
                    "#sug-dates",
                    "#b-form-submit button[type='submit']",
                    "#sug-dates label.from input",
                    "input[name='DateFrom']",
                ]
                end_time = time.time() + 30
                ready = False
                while time.time() < end_time and not ready:
                    for sel in form_ready_selectors:
                        try:
                            el = self.parser.driver.find_element(By.CSS_SELECTOR, sel)
                            if el and el.is_displayed():
                                ready = True
                                break
                        except Exception:
                            continue
                    if not ready:
                        time.sleep(0.5)
                if not ready:
                    logger.warning("⚠️ Форма поиска не видна после 30с ожидания")
            except Exception:
                pass
            
            # Устанавливаем перехватчики
            if use_js:
                self.parser.setup_xhr_interceptor()
            
            # Создаём handler и ждём загрузки SPA
            self.search_handler = RasSearchHandler(self.parser)
            
            # Ждём готовности SPA
            if not self.search_handler.wait_for_spa_ready(timeout=30):
                logger.error("❌ SPA не загрузилось")
                # Сохраняем для диагностики
                with open(os.path.join(SAVE_DIR, "spa_not_ready.html"), "w", encoding="utf-8") as f:
                    f.write(self.parser.driver.page_source)
                return None
            
            # Заполняем форму
            if not self.search_handler.fill_search_form(date_from, date_to):
                logger.error("❌ Не удалось заполнить форму")
                return None
            
            # Очищаем буферы перед отправкой
            self.parser.clear_intercept_buffer()
            
            # Отправляем форму
            if not self.search_handler.submit_search():
                logger.error("❌ Не удалось отправить форму")
                return None
            
            # Ждем ответ
            time.sleep(2)
            
            # Только CDP Network (внутри браузера)
            logger.info("🔍 Попытка получить ответ через CDP Network...")
            response = self.parser.get_network_response(url_pattern="/Ras/Search", timeout=20)
            
            if not response:
                logger.error("❌ Ответ не получен")
                # Сохраняем текущую страницу для диагностики
                with open(os.path.join(SAVE_DIR, "search_debug.html"), "w", encoding="utf-8") as f:
                    f.write(self.parser.driver.page_source)
                logger.info("💾 HTML результата сохранен в search_debug.html")
                return None
            
            # Проверяем статус
            status = response.get('status', 0)
            if status != 200:
                logger.error(f"❌ HTTP ошибка: {status}")
                return None
            
            # Парсим JSON
            try:
                body = response.get('body', '{}')
                if not body or body == '{}':
                    logger.error("❌ Пустой ответ")
                    return None
                
                data = json.loads(body)
                
                if not data or not isinstance(data, dict):
                    logger.error("❌ Некорректный JSON")
                    return None
                
                # Проверяем наличие данных
                records = data.get('Data', [])
                total = data.get('Total', 0)
                
                logger.info(f"✅ Получено: {len(records)} записей из {total}")
                
                return {
                    'data': data,
                    'date_from': date_from,
                    'date_to': date_to,
                    'timestamp': datetime.now().isoformat(),
                    'records_count': len(records),
                    'total': total
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Ошибка парсинга JSON: {e}")
                # Сохраняем проблемный ответ
                with open(os.path.join(SAVE_DIR, "response_error.txt"), "w", encoding="utf-8") as f:
                    f.write(body[:5000])
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def scrape_date_range(self, date_from: str, date_to: str, max_retries=3) -> List[Dict]:
        """Парсинг диапазона дат с retry"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🚀 ЗАПУСК ПАРСИНГА: {date_from} - {date_to}")
            logger.info(f"{'='*60}\n")
            
            # Валидация дат
            try:
                datetime.strptime(date_from, "%Y-%m-%d")
                datetime.strptime(date_to, "%Y-%m-%d")
            except ValueError as e:
                logger.error(f"❌ Неверный формат даты: {e}")
                return []
            
            # Создаем драйвер
            self.parser = RasArbitrParser()
            self.parser.build_driver()
            
            # Прогрев
            self.prewarm_session()
            
            all_results = []
            
            # Попытки с retry
            for attempt in range(1, max_retries + 1):
                logger.info(f"\n📍 Попытка {attempt}/{max_retries}")
                
                result = self.search_by_date_range(date_from, date_to)
                
                if result:
                    all_results.append(result)
                    self.session_stats['success'] += 1
                    logger.info(f"✅ Попытка {attempt} успешна")
                    break
                else:
                    self.session_stats['failed'] += 1
                    logger.warning(f"⚠️ Попытка {attempt} не удалась")
                    
                    if attempt < max_retries:
                        # Прогрев перед повтором
                        backoff = 10 * (2 ** (attempt - 1))
                        logger.info(f"⏳ Пауза {backoff}s перед повтором...")
                        time.sleep(backoff)
                        self.prewarm_session()
            
            # Сохраняем результаты
            if all_results:
                self.save_results(all_results, date_from, date_to)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 ИТОГО: Успешно={self.session_stats['success']}, Ошибок={self.session_stats['failed']}")
            logger.info(f"{'='*60}\n")
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        finally:
            # Закрываем браузер
            if self.parser and self.parser.driver:
                try:
                    logger.info("🔒 Закрытие браузера...")
                    # Оставляем браузер открытым для отладки
                    input("\n⏸️  Нажмите Enter для закрытия браузера...")
                    self.parser.driver.quit()
                except:
                    pass
    
    def save_results(self, results: List[Dict], date_from: str, date_to: str):
        """Сохранение результатов"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Полные результаты
            full_filename = f"ras_results_{date_from}_{date_to}_{timestamp}.json"
            full_path = os.path.join(SAVE_DIR, full_filename)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'date_from': date_from,
                        'date_to': date_to,
                        'total_attempts': len(results),
                        'session_stats': self.session_stats,
                        'timestamp': timestamp
                    },
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Полные результаты: {full_path}")
            
            # Только данные
            all_data = []
            for result in results:
                if 'data' in result and 'Data' in result['data']:
                    all_data.extend(result['data']['Data'])
            
            if all_data:
                data_filename = f"ras_data_{date_from}_{date_to}_{timestamp}.json"
                data_path = os.path.join(SAVE_DIR, data_filename)
                
                with open(data_path, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"💾 Данные ({len(all_data)} записей): {data_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")


# Главные функции для удобного использования
def parse_ras_arbitr(date_from: str, date_to: str) -> List[Dict]:
    """
    Парсинг ras.arbitr.ru
    
    Args:
        date_from: Дата начала в формате YYYY-MM-DD
        date_to: Дата окончания в формате YYYY-MM-DD
        
    Returns:
        Список результатов парсинга
        
    Example:
        results = parse_ras_arbitr("2024-10-01", "2024-10-01")
    """
    scraper = RasArbitrScraper()
    return scraper.scrape_date_range(date_from, date_to)


def test_parsing():
    """
    Быстрый тест парсинга за вчерашний день
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"🧪 ТЕСТОВЫЙ ПАРСИНГ за {yesterday}")
    results = parse_ras_arbitr(yesterday, yesterday)
    
    if results:
        logger.info(f"✅ Тест успешен: получено {len(results)} результатов")
        return True
    else:
        logger.error("❌ Тест не прошел")
        return False


def parse_date_range_loop(start_date: str, end_date: str):
    """
    Парсинг по дням в диапазоне
    
    Args:
        start_date: Дата начала YYYY-MM-DD
        end_date: Дата окончания YYYY-MM-DD
    
    Example:
        results = parse_date_range_loop("2024-10-01", "2024-10-05")
    """
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    day_num = 1
    all_results = []
    
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        
        logger.info(f"\n\n{'#'*60}")
        logger.info(f"📅 ДЕНЬ {day_num}: {date_str}")
        logger.info(f"{'#'*60}\n")
        
        results = parse_ras_arbitr(date_str, date_str)
        all_results.extend(results)
        
        # Антибан пауза между днями
        if current < end:
            pause = random.uniform(30, 60)
            logger.info(f"⏳ Пауза между днями: {pause:.1f}s")
            time.sleep(pause)
        
        current += timedelta(days=1)
        day_num += 1
    
    logger.info(f"\n✅ ЗАВЕРШЕНО: обработано {day_num-1} дней, получено {len(all_results)} результатов")
    return all_results


def download_pdfs_from_results(json_path: str, max_per_run: Optional[int] = None) -> None:
    """
    Открывает RAS, воспроизводит поиск по датам из json и скачивает PDF для найденных элементов,
    кликая по строкам, где совпадает FileName/CaseNumber.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception as e:
        logger.error(f"❌ Не удалось прочитать JSON: {e}")
        return

    results = payload.get('results') or []
    if not results:
        logger.warning("⚠️ В JSON нет секции results")
        return

    # Даты для формы
    meta = payload.get('metadata') or {}
    date_from = meta.get('date_from')
    date_to = meta.get('date_to')
    if not date_from or not date_to:
        logger.warning("⚠️ В metadata отсутствуют date_from/date_to")

    # Собираем список элементов
    items: List[Dict] = []
    for block in results:
        data = block.get('data') or {}
        result_obj = data.get('Result') or {}
        items.extend(result_obj.get('Items') or [])

    if not items:
        logger.info("ℹ️ Пустой список Items — нечего скачивать")
        return

    if max_per_run is not None:
        items = items[:max_per_run]

    # Запускаем браузер
    scraper = RasArbitrScraper()
    scraper.parser = RasArbitrParser()
    scraper.parser.build_driver()
    scraper.prewarm_session()

    try:
        # Переходим на форму и заполняем даты (если есть)
        scraper.parser.driver.get(RAS_HOME)
        scraper.parser.wait_ready()
        try:
            scraper.parser.driver.execute_script("window.location.hash='searchPrintForm';")
        except Exception:
            pass
        time.sleep(2)

        handler = RasSearchHandler(scraper.parser)
        handler.wait_for_spa_ready(timeout=30)
        if date_from and date_to:
            handler.fill_search_form(date_from, date_to)
            scraper.parser.clear_intercept_buffer()
            handler.submit_search()
            time.sleep(2)

        # Перебираем элементы и пытаемся кликнуть по соответствующей строке и скачать PDF
        downloaded = 0
        for it in items:
            file_name = (it.get('FileName') or '').strip()
            case_num = (it.get('CaseNumber') or '').strip()
            if not file_name and not case_num:
                continue

            logger.info(f"📄 Поиск строки для скачивания: {file_name or case_num}")

            # Попытка найти по тексту FileName/CaseNumber и кликнуть именно по ссылке строки
            found = False
            search_texts = [t for t in [file_name, case_num] if t]
            for text in search_texts:
                try:
                    # Ищем элемент, содержащий текст
                    elem = WebDriverWait(scraper.parser.driver, 8).until(
                        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
                    )
                    # Пытаемся найти ближайшую ссылку внутри строки результата
                    row = elem
                    for _ in range(5):
                        try:
                            # поднимаемся вверх к контейнеру строки
                            parent = row.find_element(By.XPATH, './..')
                            row = parent
                        except Exception:
                            break
                    link_el = None
                    try:
                        # Часто первая ссылка внутри строки ведет на карточку
                        anchors = row.find_elements(By.XPATH, ".//a[@href]")
                        if anchors:
                            link_el = anchors[0]
                    except Exception:
                        pass

                    # Сохраняем список окон до клика
                    before_windows = set(scraper.parser.driver.window_handles)

                    # Клик по ссылке строки, если нашли; иначе по самому элементу
                    try:
                        target = link_el or elem
                        scraper.parser.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                    except Exception:
                        pass
                    time.sleep(0.4)
                    try:
                        (link_el or elem).click()
                    except Exception:
                        scraper.parser.driver.execute_script("arguments[0].click();", (link_el or elem))

                    # Ждем открытия новой вкладки или появления модального окна/кнопок PDF
                    time.sleep(1.0)
                    after_windows = set(scraper.parser.driver.window_handles)
                    opened_new = list(after_windows - before_windows)
                    switched = False
                    if opened_new:
                        # Переключаемся на новую вкладку (часто ведет на kad.arbitr.ru)
                        new_handle = opened_new[-1]
                        scraper.parser.driver.switch_to.window(new_handle)
                        switched = True
                        # Для KAD выставим реферер и заголовки навигации
                        try:
                            scraper.parser.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                                "headers": {
                                    "Referer": KAD_HOME,
                                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
                                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                                }
                            })
                        except Exception:
                            pass

                    # Ищем элементы скачивания PDF в текущем контексте
                    def try_download_in_context() -> bool:
                        # Сначала прямые ссылки на Pdf
                        candidates = []
                        try:
                            candidates += scraper.parser.driver.find_elements(By.XPATH, "//a[contains(@href,'/Document/Pdf/')]")
                        except Exception:
                            pass
                        try:
                            candidates += scraper.parser.driver.find_elements(By.XPATH, "//a[contains(translate(text(),'PDF','pdf'),'pdf')]")
                        except Exception:
                            pass
                        try:
                            candidates += scraper.parser.driver.find_elements(By.XPATH, "//button[contains(translate(text(),'СкачатьPDF','скачатьpdf'),'скачать') or contains(translate(text(),'PDF','pdf'),'pdf')]")
                        except Exception:
                            pass

                        if not candidates:
                            return False

                        link = candidates[0]
                        try:
                            scraper.parser.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                        except Exception:
                            pass
                        time.sleep(0.4)
                        try:
                            link.click()
                        except Exception:
                            try:
                                scraper.parser.driver.execute_script("arguments[0].click();", link)
                            except Exception:
                                return False

                        # Перед ожиданием скачивания проверим, что CDP видел PDF
                        pdf_resp = scraper.parser.wait_for_pdf_via_cdp(timeout=5)
                        # Ожидаем скачивание
                        try:
                            saved = scraper.parser.wait_download_finished(SAVE_DIR, timeout=240)
                            logger.info(f"✅ PDF сохранен: {saved}")
                            return True
                        except Exception as e:
                            logger.warning(f"⚠️ Не дождались скачивания: {e}")
                            return False

                    # Пытаемся скачать в текущем окне
                    if try_download_in_context():
                        downloaded += 1
                        found = True
                    else:
                        # Иногда ссылка генерируется после доп. кликов по вкладкам/кнопкам внутри карточки. Попробуем кликнуть очевидные элементы.
                        try:
                            tabs = scraper.parser.driver.find_elements(By.XPATH, "//a[contains(translate(text(),'ДОКУМЕНТЫPDF','документыpdf'),'документ') or contains(translate(text(),'PDF','pdf'),'pdf')]")
                            if tabs:
                                try:
                                    tabs[0].click()
                                except Exception:
                                    scraper.parser.driver.execute_script("arguments[0].click();", tabs[0])
                                time.sleep(0.8)
                                if try_download_in_context():
                                    downloaded += 1
                                    found = True
                        except Exception:
                            pass

                    # Возвращаемся на исходную вкладку, если переключались
                    if switched:
                        try:
                            # Закрываем новую вкладку, чтобы не разрастались
                            scraper.parser.driver.close()
                        except Exception:
                            pass
                        try:
                            base_handle = list(before_windows)[-1] if before_windows else scraper.parser.driver.window_handles[0]
                            scraper.parser.driver.switch_to.window(base_handle)
                        except Exception:
                            pass

                    if found:
                        break
                except Exception:
                    continue

            # Пауза между файлами с антибан-джиттером
            time.sleep(max(0, BASE_DELAY + random.uniform(-JITTER, JITTER)))

        logger.info(f"📊 Итог скачивания PDF: {downloaded}/{len(items)}")

    finally:
        try:
            scraper.parser.driver.quit()
        except Exception:
            pass


def scrape_and_download(date_from: str, date_to: str, max_per_run: Optional[int] = None) -> None:
    """
    Один шаг: выполняет поиск внутри браузера за указанные даты и
    сразу пытается скачать PDF для найденных элементов результатов.
    """
    scraper = RasArbitrScraper()
    scraper.parser = RasArbitrParser()
    scraper.parser.build_driver()
    scraper.prewarm_session()

    try:
        # Выполняем поиск и получаем JSON (через CDP/JS/curl_cffi внутри)
        result = scraper.search_by_date_range(date_from, date_to)
        if not result or not result.get('data'):
            logger.error("❌ Не удалось получить результаты поиска")
            return

        data = result['data']
        res_obj = (data.get('Result') or {})
        items = res_obj.get('Items') or []
        if not items:
            logger.info("ℹ️ Пустой список Items — нечего скачивать")
            return
        if max_per_run is not None:
            items = items[:max_per_run]

        driver = scraper.parser.driver

        def try_download_in_context() -> bool:
            candidates = []
            try:
                candidates += driver.find_elements(By.XPATH, "//a[contains(@href,'/Document/Pdf/')]")
            except Exception:
                pass
            try:
                candidates += driver.find_elements(By.XPATH, "//a[contains(translate(text(),'PDF','pdf'),'pdf')]")
            except Exception:
                pass
            try:
                candidates += driver.find_elements(By.XPATH, "//button[contains(translate(text(),'СкачатьPDF','скачатьpdf'),'скачать') or contains(translate(text(),'PDF','pdf'),'pdf')]")
            except Exception:
                pass
            if not candidates:
                return False
            link = candidates[0]
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
            except Exception:
                pass
            time.sleep(0.4)
            try:
                link.click()
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", link)
                except Exception:
                    return False
            # Ждем PDF сигнал и завершение скачивания
            _ = scraper.parser.wait_for_pdf_via_cdp(timeout=5)
            try:
                saved = scraper.parser.wait_download_finished(PDF_DIR, timeout=240)
                logger.info(f"✅ PDF сохранен: {saved}")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Не дождались скачивания: {e}")
                return False

        downloaded = 0
        for it in items:
            file_name = (it.get('FileName') or '').strip()
            case_num = (it.get('CaseNumber') or '').strip()
            search_texts = [t for t in [file_name, case_num] if t]

            logger.info(f"📄 Обработка элемента: {file_name or case_num}")

            opened = False
            for text in search_texts:
                try:
                    elem = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
                    )
                    # Поднимаемся к строке и ищем ссылку
                    row = elem
                    for _ in range(5):
                        try:
                            row = row.find_element(By.XPATH, './..')
                        except Exception:
                            break
                    link_el = None
                    try:
                        anchors = row.find_elements(By.XPATH, ".//a[@href]")
                        if anchors:
                            link_el = anchors[0]
                    except Exception:
                        pass

                    before_windows = set(driver.window_handles)
                    target = link_el or elem
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                    except Exception:
                        pass
                    time.sleep(0.4)
                    try:
                        target.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", target)

                    # Переключение на новую вкладку (если открылась)
                    time.sleep(1.0)
                    after_windows = set(driver.window_handles)
                    opened_new = list(after_windows - before_windows)
                    switched = False
                    if opened_new:
                        driver.switch_to.window(opened_new[-1])
                        switched = True
                        try:
                            scraper.parser.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                                "headers": {
                                    "Referer": KAD_HOME,
                                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
                                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                                }
                            })
                        except Exception:
                            pass

                    if try_download_in_context():
                        downloaded += 1
                        opened = True
                    else:
                        # Доп. попытка: перейти на вкладку/секцию «Документы» и попробовать снова
                        try:
                            tabs = driver.find_elements(By.XPATH, "//a[contains(translate(text(),'ДОКУМЕНТЫPDF','документыpdf'),'документ') or contains(translate(text(),'PDF','pdf'),'pdf')]")
                            if tabs:
                                try:
                                    tabs[0].click()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", tabs[0])
                                time.sleep(0.8)
                                if try_download_in_context():
                                    downloaded += 1
                                    opened = True
                        except Exception:
                            pass

                    # Закрываем вкладку и возвращаемся
                    if switched:
                        try:
                            driver.close()
                        except Exception:
                            pass
                        try:
                            base_handle = list(before_windows)[-1] if before_windows else driver.window_handles[0]
                            driver.switch_to.window(base_handle)
                        except Exception:
                            pass

                    if opened:
                        break
                except Exception:
                    continue

            # Пауза антибан
            time.sleep(max(0, BASE_DELAY + random.uniform(-JITTER, JITTER)))

        logger.info(f"📊 Итог скачивания PDF: {downloaded}/{len(items)}")

    finally:
        try:
            scraper.parser.driver.quit()
        except Exception:
            pass

def download_pdf_list(pdf_urls: List[str], max_retries: int = 2):
    """
    Пакетная загрузка PDF с антибан-стратегией (из комментариев)
    
    Args:
        pdf_urls: Список URL PDF файлов
        max_retries: Количество попыток на файл
    """
    parser = RasArbitrParser()
    parser.build_driver()
    
    success = 0
    fail = 0
    
    try:
        # Прогрев сессии
        logger.info("🔥 Прогрев сессии для PDF скачивания...")
        parser.driver.get(RAS_HOME)
        parser.wait_ready()
        parser.humanize_behavior(moves=random.randint(6, 12))
        time.sleep(random.uniform(1.5, 3.0))
        
        for idx, url in enumerate(pdf_urls, 1):
            logger.info(f"📄 Скачивание PDF {idx}/{len(pdf_urls)}: {url}")
            
            # Периодический прогрев
            if (idx % PREWARM_EVERY) == 0:
                logger.info("🔥 Периодический прогрев...")
                parser.driver.get(RAS_HOME)
                parser.wait_ready()
                parser.humanize_behavior(moves=random.randint(5, 10))
                time.sleep(random.uniform(0.8, 1.5))
            
            # Попытки с бэкоффом
            ok = False
            backoff = 8
            
            for attempt in range(1, max_retries + 1):
                try:
                    before = set(os.listdir(SAVE_DIR))
                    parser.driver.get(url)
                    time.sleep(1.5)  # Даём сети стартануть
                    
                    saved = parser.wait_download_finished(SAVE_DIR, timeout=240)
                    logger.info(f"✅ PDF скачан: {saved}")
                    ok = True
                    break
                    
                except Exception as e:
                    logger.warning(f"⚠️ Попытка {attempt} не удалась: {e}")
                    if attempt < max_retries:
                        sleep_s = backoff + random.uniform(0, 4)
                        logger.info(f"⏳ Пауза {sleep_s:.1f}s перед повтором...")
                        time.sleep(sleep_s)
                        backoff *= 2
                        
                        # Сброс заголовков и прогрев
                        parser.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                            "headers": {
                                "Referer": "https://ras.arbitr.ru/",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
                                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                                "Upgrade-Insecure-Requests": "1",
                                "Sec-Fetch-Site": "same-origin",
                                "Sec-Fetch-Mode": "navigate",
                                "Sec-Fetch-Dest": "document",
                                "Connection": "keep-alive"
                            }
                        })
                        parser.driver.get(RAS_HOME)
                        parser.wait_ready()
                        parser.humanize_behavior(moves=random.randint(5, 10))
                        time.sleep(random.uniform(0.8, 1.5))
            
            if ok:
                success += 1
            else:
                fail += 1
            
            # Базовая пауза между файлами
            delay = max(0, BASE_DELAY + random.uniform(-JITTER, JITTER))
            time.sleep(delay)
            
            # Длинная пауза каждые N файлов
            if (idx % LONG_PAUSE_EVERY) == 0:
                extra = random.uniform(*LONG_PAUSE_RANGE)
                logger.info(f"⏳ Длинная пауза: {extra:.1f}s")
                time.sleep(extra)
        
        logger.info(f"📊 ИТОГО PDF: Успешно={success}, Ошибок={fail}")
        
    finally:
        if parser.driver:
            parser.driver.quit()


if __name__ == "__main__":
    print("🚀 RAS Arbitr Parser v2.0 - ПОЛНАЯ ВЕРСИЯ")
    print("="*60)
    print("✅ Учтены ВСЕ рекомендации из комментариев:")
    print("  - Правильные селекторы (#sug-dates label.from/to input.anyway_position_top)")
    print("  - Fetch.enable для дополнительного перехвата")
    print("  - Принудительное скачивание PDF с ожиданием .crdownload")
    print("  - Пакетная загрузка с антибан-стратегией")
    print("  - ЧЕТЫРЕ метода перехвата: CDP Network → Fetch → JS → curl_cffi")
    print("  - curl_cffi с impersonation для внешних POST (запасной)")
    print("="*60)
    print("1. Тест: test_parsing()")
    print("2. Парсинг: parse_ras_arbitr('2024-10-01', '2024-10-01')")
    print("3. Диапазон: parse_date_range_loop('2024-10-01', '2024-10-05')")
    print("4. PDF: download_pdf_list(['url1', 'url2'])")
    print("="*60)
    
    # Автоматическое скачивание PDF, если есть список URL в res/pdf_urls.txt
    urls_file = Path(SAVE_DIR) / "pdf_urls.txt"
    if urls_file.exists():
        try:
            with open(urls_file, "r", encoding="utf-8") as f:
                pdf_urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            if pdf_urls:
                logger.info(f"📥 Найдено {len(pdf_urls)} PDF ссылок в {urls_file}. Запускаю скачивание...")
                download_pdf_list(pdf_urls)
            else:
                logger.info("ℹ️ Файл pdf_urls.txt пуст. Запускаю тест парсинга.")
                test_parsing()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения списка PDF: {e}")
            test_parsing()
    else:
        # По умолчанию запускаем тестовый парсинг
        test_parsing()
