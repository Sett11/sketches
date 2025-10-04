import os
import time
import glob
import random
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

# === Конфигурация ===
KAD_URL = "https://kad.arbitr.ru/"
DOWNLOAD_DIR = str(Path.home() / "Downloads" / "kad_arbitr")
BASE_DELAY_SEC = 10             # базовая задержка между файлами
JITTER_SEC = 3                  # случайный джиттер ±
RETRY_LIMIT = 2                 # ретраев на файл
LONG_PAUSE_EVERY = 5            # длинная пауза после каждых N файлов
LONG_PAUSE_RANGE = (40, 90)     # сек для длинной паузы
DOWNLOAD_TIMEOUT = 240          # сек ожидания скачивания одного файла
PREWARM_EVERY = 3               # прогрев главной перед каждыми N файлами

# Подставьте свой список PDF-URL-ов:
PDF_URLS = [
'https://kad.arbitr.ru/Document/Pdf/84b8c481-3244-422f-968a-c001fe20009d/d98a7f0f-a04e-46ce-96b6-e1c762a7e9a2/А75-16684-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/c67beca0-b4aa-44bc-906d-4058a940aad0/387d5868-cf59-4d98-9562-8e27ca89cabf/А14-12007-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/7741ce30-da6f-409b-8c82-7dd860a2d1e8/f0c5f10f-7f23-4226-8a80-648f30a2878a/А40-144131-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/4a0f4a03-cc21-4a55-b11b-fa90970bf377/f7a4426a-3158-4187-bfec-ca325a4e47cd/А41-65162-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/c7e346c0-d7e9-4eab-ba12-5e0ee5f39087/9ccfee8d-ab58-4bad-9c23-b8043b41db66/А41-66022-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/23f9eb5c-3c10-4db1-8e09-ac8378f7f986/1aa7b88e-9455-48c5-a06b-f67da42cb67c/А41-66660-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/fd831885-b696-4f2b-ba7d-e26a32865a2c/61df143a-a724-43ba-80eb-db0085252bc1/А41-66651-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/6e1ed3c3-dfba-49a8-9fc6-352254d6c727/3cc29a3e-4b3e-4900-b37c-5b9005fd07d1/А41-49169-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/82808e61-8cb8-4cae-9b44-1ad038b32ca3/1c2bb886-001c-4ff3-8db9-3e27c30e09af/А41-62278-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/9424dfa8-761b-418e-9400-63ea5cc09ae5/220d3f38-999c-4b93-9fb3-970aaabee75b/А41-66666-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/b3330945-db33-4263-8069-66d4cc5079d0/778b8390-b2bd-453f-a849-4c8b9d64ab4a/А40-193984-2025__20250926.pdf',
 'https://kad.arbitr.ru/Document/Pdf/6e7dc066-4179-45d4-bdef-6efab765e883/5e7619bf-e19b-43d7-8b5e-6a219ff83cf1/А40-196790-2025__20250926.pdf'
]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def build_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=ru-RU")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/129.0.0.0 Safari/537.36")

    # Принудительное скачивание PDF, а не просмотр
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    # Логи DevTools по желанию
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

    driver = webdriver.Chrome(options=options)

    # Разрешаем скачивания через CDP (устойчиво под разные версии)
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": DOWNLOAD_DIR
    })

    # Включаем сеть и ставим навигационные заголовки (важен Referer)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
        "headers": {
            "Referer": "https://kad.arbitr.ru/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Connection": "keep-alive"
        }
    })
    return driver

def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def humanize(driver, moves=8):
    actions = ActionChains(driver)
    body = driver.find_element(By.TAG_NAME, "body")
    actions.move_to_element(body).perform()
    time.sleep(0.3)
    for _ in range(moves):
        actions.move_by_offset(random.randint(-80, 120), random.randint(-60, 100)).perform()
        time.sleep(random.uniform(0.15, 0.45))
    driver.execute_script("window.scrollBy(0, 400);"); time.sleep(0.3)
    driver.execute_script("window.scrollBy(0, -200);")

def wait_download_finished(directory: str, timeout: int = 240):
    start = time.time()
    last_size = None
    stable_ticks = 0
    while time.time() - start < timeout:
        # Идёт загрузка, если ещё есть .crdownload
        crs = glob.glob(os.path.join(directory, "*.crdownload"))
        if crs:
            # Контроль “не залипло ли”: проверяем, меняется ли размер самого большого .crdownload
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
            return str(latest)
        time.sleep(0.5)
    raise TimeoutError("PDF не скачался вовремя или загрузка зависла")

def safe_sleep(base=BASE_DELAY_SEC, jitter=JITTER_SEC):
    delay = max(0, base + random.uniform(-jitter, jitter))
    time.sleep(delay)

def prewarm(driver):
    driver.get(KAD_URL)
    wait_ready(driver)
    # Небольшая имитация действий
    try:
        humanize(driver, moves=random.randint(5, 10))
    except Exception:
        pass
    time.sleep(random.uniform(0.8, 1.5))

def download_one(driver, url) -> bool:
    before = set(os.listdir(DOWNLOAD_DIR))
    driver.get(url)
    # Даём сети стартануть
    time.sleep(1.5)
    try:
        saved = wait_download_finished(DOWNLOAD_DIR, timeout=DOWNLOAD_TIMEOUT)
        print(f"OK: {url} -> {saved}")
        return True
    except Exception as e:
        print(f"FAIL (wait): {url} -> {e}")
        # Сохраняем HTML на случай выдачи челленджа/шаблона
        try:
            with open(os.path.join(DOWNLOAD_DIR, "last_page.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception:
            pass
        return False

def main():
    driver = build_driver()
    success = 0
    fail = 0
    try:
        prewarm(driver)
        for idx, url in enumerate(PDF_URLS, 1):
            # Периодический прогрев главной
            if (idx % PREWARM_EVERY) == 0:
                prewarm(driver)

            # Попытки с бэкоффом
            ok = False
            backoff = 8
            for attempt in range(1, RETRY_LIMIT + 2):
                ok = download_one(driver, url)
                if ok:
                    break
                # Экспоненциальный бэкофф
                sleep_s = backoff + random.uniform(0, 4)
                print(f"Backoff {sleep_s:.1f}s перед повтором (#{attempt})")
                time.sleep(sleep_s)
                backoff *= 2
                # Сброс заголовков и повторный прогрев после неудачи
                driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                    "headers": {
                        "Referer": "https://kad.arbitr.ru/",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8",
                        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Dest": "document",
                        "Connection": "keep-alive"
                    }
                })
                prewarm(driver)

            if ok:
                success += 1
            else:
                fail += 1

            # Базовая пауза между файлами
            safe_sleep()

            # Длинная пауза каждые N файлов
            if (idx % LONG_PAUSE_EVERY) == 0:
                extra = random.uniform(*LONG_PAUSE_RANGE)
                print(f"Длинная пауза: {extra:.1f}s")
                time.sleep(extra)

        print(f"Готово. Успехов: {success}, Ошибок: {fail}")

        input("Окно оставлено открытым. Нажмите Enter для выхода...")
    finally:
        # driver.quit()
        pass

if __name__ == "__main__":
    main()


# Это код, который умеет закачивать pdf - обратите внимание, что сейчас он запускается в полном режиме, для сервера надо перевести на headless