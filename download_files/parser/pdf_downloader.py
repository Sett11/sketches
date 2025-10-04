"""
Модуль для скачивания PDF файлов с kad.arbitr.ru через Selenium
Адаптирован для работы в Docker (headless режим)
"""
import os
import time
import glob
import random
import logging
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from config import Config

logger = logging.getLogger(__name__)


class PDFDownloader:
    """Класс для скачивания PDF через Selenium"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.download_dir = str(Config.PDFS_DIR)
        self.timeout = Config.SELENIUM_TIMEOUT
        self.retry_limit = Config.RETRY_LIMIT
        self.base_delay = Config.BASE_DELAY_SEC
        self.jitter = Config.JITTER_SEC
        self.long_pause_every = Config.LONG_PAUSE_EVERY
        self.long_pause_range = (Config.LONG_PAUSE_MIN, Config.LONG_PAUSE_MAX)
        self.prewarm_every = Config.PREWARM_EVERY
        self.kad_url = Config.KAD_URL
        
        self.driver = None
        self.files_downloaded = 0
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.driver = self._build_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Ошибка при закрытии драйвера: {e}")
    
    def _build_driver(self):
        """Создать и настроить WebDriver"""
        logger.info("Инициализация Chrome WebDriver")
        
        options = Options()
        
        # Настройки для headless режима
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=ru-RU")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        
        # User Agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.0.0 Safari/537.36"
        )
        
        # Настройки для автоматического скачивания PDF
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }
        options.add_experimental_option("prefs", prefs)
        
        # Логи DevTools
        options.set_capability("goog:loggingPrefs", {
            "performance": "ALL", 
            "browser": "ALL"
        })
        
        try:
            driver = webdriver.Chrome(options=options)
            
            # Настройки CDP для скачивания
            driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": self.download_dir
            })
            
            # Дополнительные HTTP заголовки
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                "headers": {
                    "Referer": self.kad_url,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Dest": "document",
                    "Connection": "keep-alive"
                }
            })
            
            logger.info("WebDriver успешно инициализирован")
            return driver
            
        except Exception as e:
            logger.error(f"Ошибка при создании WebDriver: {e}")
            raise
    
    def _wait_ready(self, timeout=30):
        """Ожидание полной загрузки страницы"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    
    def _humanize(self, moves=8):
        """Имитация человеческих движений мышью"""
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
            
            # Скроллинг
            self.driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(0.3)
            self.driver.execute_script("window.scrollBy(0, -200);")
            
        except Exception as e:
            logger.debug(f"Ошибка при humanize: {e}")
    
    def _wait_download_finished(self, timeout: int = None) -> Optional[str]:
        """
        Ожидание завершения скачивания файла
        
        Returns:
            Путь к скачанному файлу или None при ошибке
        """
        if timeout is None:
            timeout = self.timeout
        
        start = time.time()
        last_size = None
        stable_ticks = 0
        
        while time.time() - start < timeout:
            # Проверяем наличие .crdownload файлов
            crdownloads = glob.glob(os.path.join(self.download_dir, "*.crdownload"))
            
            if crdownloads:
                # Проверяем, не зависло ли скачивание
                largest = max(crdownloads, key=lambda p: os.path.getsize(p))
                size = os.path.getsize(largest)
                
                if last_size == size:
                    stable_ticks += 1
                else:
                    stable_ticks = 0
                
                last_size = size
                
                # Если размер не меняется более 30 секунд - вероятно зависло
                if stable_ticks > 60:  # 60 * 0.5 = 30 сек
                    logger.warning("Скачивание зависло (размер не меняется)")
                    break
                
                time.sleep(0.5)
                continue
            
            # Нет .crdownload - ищем свежий PDF
            pdf_files = [
                p for p in Path(self.download_dir).glob("*.pdf") 
                if p.stat().st_mtime >= start - 2
            ]
            
            if pdf_files:
                latest = max(pdf_files, key=lambda p: p.stat().st_mtime)
                logger.info(f"Файл скачан: {latest.name}")
                return str(latest)
            
            time.sleep(0.5)
        
        logger.error("Таймаут ожидания скачивания PDF")
        return None
    
    def _safe_sleep(self):
        """Безопасная пауза с джиттером"""
        delay = max(0, self.base_delay + random.uniform(-self.jitter, self.jitter))
        time.sleep(delay)
    
    def _prewarm(self):
        """Прогрев - открытие главной страницы для имитации активности"""
        try:
            logger.debug("Прогрев главной страницы")
            self.driver.get(self.kad_url)
            self._wait_ready()
            self._humanize(moves=random.randint(5, 10))
            time.sleep(random.uniform(0.8, 1.5))
        except Exception as e:
            logger.warning(f"Ошибка при прогреве: {e}")
    
    def download_pdf(self, url: str, case_number: str) -> Optional[str]:
        """
        Скачать один PDF файл
        
        Args:
            url: URL PDF файла
            case_number: номер дела для именования
        
        Returns:
            Путь к скачанному файлу или None при ошибке
        """
        logger.info(f"Начало скачивания: {case_number}")
        
        # Периодический прогрев
        if self.files_downloaded > 0 and (self.files_downloaded % self.prewarm_every) == 0:
            self._prewarm()
        
        # Попытки с бэкоффом
        backoff = 8
        
        for attempt in range(1, self.retry_limit + 1):
            try:
                logger.debug(f"Попытка {attempt}/{self.retry_limit}: {url}")
                
                # Запускаем скачивание
                self.driver.get(url)
                time.sleep(1.5)  # Даём сети стартануть
                
                # Ожидаем завершения скачивания
                downloaded_file = self._wait_download_finished()
                
                if downloaded_file:
                    # Переименовываем файл
                    new_filename = f"{case_number}.pdf"
                    new_path = os.path.join(self.download_dir, new_filename)
                    
                    # Если файл уже существует, удаляем старый
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    
                    os.rename(downloaded_file, new_path)
                    
                    self.files_downloaded += 1
                    logger.info(f"✓ Скачан: {case_number} ({self.files_downloaded} файлов)")
                    
                    # Пауза между файлами
                    self._safe_sleep()
                    
                    # Длинная пауза каждые N файлов
                    if (self.files_downloaded % self.long_pause_every) == 0:
                        extra = random.uniform(*self.long_pause_range)
                        logger.info(f"Длинная пауза: {extra:.1f}s")
                        time.sleep(extra)
                    
                    return new_path
                
                else:
                    logger.warning(f"Не удалось скачать файл (попытка {attempt})")
                    
                    # Сохраняем HTML для отладки
                    try:
                        html_path = os.path.join(self.download_dir, f"error_{case_number}.html")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                    except Exception:
                        pass
                
            except Exception as e:
                logger.error(f"Ошибка при скачивании (попытка {attempt}): {e}")
            
            # Бэкофф перед следующей попыткой
            if attempt < self.retry_limit:
                sleep_time = backoff + random.uniform(0, 4)
                logger.info(f"Ожидание {sleep_time:.1f}s перед повтором")
                time.sleep(sleep_time)
                backoff *= 2
                
                # Повторный прогрев после неудачи
                self._prewarm()
        
        logger.error(f"✗ Не удалось скачать: {case_number} после {self.retry_limit} попыток")
        return None
    
    def get_download_stats(self) -> dict:
        """Получить статистику скачиваний"""
        return {
            'files_downloaded': self.files_downloaded
        }

