import os
import json
import time
import random
from pathlib import Path
from http.cookiejar import Cookie, CookieJar

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

KAD_HOME = "https://kad.arbitr.ru/"
RAS_HOME = "https://ras.arbitr.ru/"
SEARCH_URL = "https://ras.arbitr.ru/Ras/Search"

SAVE_DIR = str(Path.home() / "Downloads" / "ras_search_api")
os.makedirs(SAVE_DIR, exist_ok=True)

BASE_DELAY = 10
JITTER = 3
RETRY_LIMIT = 2
TIMEOUT = 60

# Пример полезной нагрузки (можно добавлять несколько)
PAYLOADS = [
    {
        "GroupByCase": False,
        "Count": 25,
        "Page": 1,
        "DateFrom": "2025-09-30T00:00:00",
        "DateTo":   "2025-10-01T23:59:59",
        "InstanceType": ["1","2","3","4","5","6","9","10","11","12","13"],
        "IsFinished": "1",
        "Judges": [],
        "Cases": [],
        "Sides": [],
        "Text": ""
    }
]

def build_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--lang=ru-RU")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "\
         "AppleWebKit/537.36 (KHTML, like Gecko) "\
         "Chrome/129.0.0.0 Safari/537.36"
    opts.add_argument(f"user-agent={ua}")
    # Для удобства логирования CDP (опционально)
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    driver = webdriver.Chrome(options=opts)
    # Включить CDP сеть (опционально, для расширенной диагностики)
    driver.execute_cdp_cmd("Network.enable", {})
    return driver, ua

def wait_ready(d, t=30):
    WebDriverWait(d, t).until(lambda x: x.execute_script("return document.readyState") == "complete")

def humanize(d, moves=8):
    actions = ActionChains(d)
    body = d.find_element(By.TAG_NAME, "body")
    actions.move_to_element(body).perform()
    time.sleep(0.3)
    for _ in range(moves):
        actions.move_by_offset(random.randint(-80,120), random.randint(-60,100)).perform()
        time.sleep(random.uniform(0.15,0.45))
    d.execute_script("window.scrollBy(0, 400);"); time.sleep(0.3)
    d.execute_script("window.scrollBy(0, -200);")

def cookiejar_from_selenium(cookies_list):
    jar = CookieJar()
    for c in cookies_list:
        # Безопасно извлекаем поля
        name = c.get("name")
        value = c.get("value")
        domain = c.get("domain")
        path = c.get("path", "/")
        secure = bool(c.get("secure", False))
        rest = {"HttpOnly": c.get("httpOnly", False)}
        # expiry может отсутствовать
        expires = c.get("expiry", None)
        # Собираем объект Cookie
        cookie = Cookie(
            version=0, name=name, value=value, port=None, port_specified=False,
            domain=domain, domain_specified=bool(domain), domain_initial_dot=domain.startswith(".") if domain else False,
            path=path, path_specified=True, secure=secure, expires=expires, discard=False,
            comment=None, comment_url=None, rest=rest, rfc2109=False
        )
        jar.set_cookie(cookie)
    return jar

def extract_csrf_from_ras_html(driver):
    # Опционально: попытка найти анти‑CSRF токен в DOM (если требуется сервером)
    html = driver.page_source
    # Простейший поиск по возможным шаблонам; при необходимости улучшить парсером
    token = None
    # Пример: <input name="__RequestVerificationToken" value="...">
    import re
    m = re.search(r'name="__RequestVerificationToken"\s+value="([^"]+)"', html)
    if m:
        token = m.group(1)
    return token



def session_from_driver(driver, ua: str):
    # Переходим на KAD и RAS, чтобы браузер поставил нужные куки
    driver.get(KAD_HOME)
    wait_ready(driver)
    try: humanize(driver, moves=random.randint(5,10))
    except: pass
    time.sleep(random.uniform(0.8, 1.5))

    driver.switch_to.new_window('tab')
    driver.get(RAS_HOME)
    wait_ready(driver)
    try: humanize(driver, moves=random.randint(3,6))
    except: pass
    time.sleep(random.uniform(0.7, 1.2))

    # Считываем куки из обеих вкладок/доменов
    # Текущая вкладка на ras; сначала соберем ras, затем вернёмся и соберем kad
    ras_cookies = driver.get_cookies()
    driver.switch_to.window(driver.window_handles[0])
    kad_cookies = driver.get_cookies()

    # Формируем CookieJar и переносим в requests.Session
    jar = CookieJar()
    for ck in (kad_cookies + ras_cookies):
        name = ck.get("name"); value = ck.get("value")
        domain = ck.get("domain"); path = ck.get("path", "/")
        secure = bool(ck.get("secure", False))
        expires = ck.get("expiry", None)
        rest = {"HttpOnly": ck.get("httpOnly", False)}
        cookie = Cookie(
            version=0, name=name, value=value, port=None, port_specified=False,
            domain=domain, domain_specified=bool(domain), domain_initial_dot=domain.startswith(".") if domain else False,
            path=path, path_specified=True, secure=secure, expires=expires, discard=False,
            comment=None, comment_url=None, rest=rest, rfc2109=False
        )
        jar.set_cookie(cookie)

    s = requests.Session()
    s.cookies = jar
    s.headers.update({
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://ras.arbitr.ru",
        "Referer": "https://ras.arbitr.ru/",
        "X-Requested-With": "XMLHttpRequest"
    })
    # Попытка вытащить анти‑CSRF токен из страницы ras
    driver.switch_to.window(driver.window_handles[1])
    token = extract_csrf_from_ras_html(driver)
    if token:
        s.headers.update({"RequestVerificationToken": token})
    return s

def post_search(session: requests.Session, payload: dict, timeout: int = TIMEOUT):
    r = session.post(SEARCH_URL, json=payload, timeout=timeout)
    # 451/403/302 и HTML вместо JSON = вероятная защита; сохраняем для диагностики
    ctype = r.headers.get("Content-Type", "")
    if r.status_code == 200 and "application/json" in ctype:
        return True, r.json()
    else:
        return False, {"status": r.status_code, "content_type": ctype, "text": r.text[:2000]}



def main():
    driver, ua = build_driver()
    try:
        session = session_from_driver(driver, ua)
        success = 0
        fail = 0
        for i, payload in enumerate(PAYLOADS, 1):
            ok = False
            backoff = 8
            for attempt in range(1, RETRY_LIMIT + 2):
                ok, data = post_search(session, payload, timeout=TIMEOUT)
                if ok:
                    out = os.path.join(SAVE_DIR, f"ras_search_{i:02d}.json")
                    with open(out, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print("OK:", out)
                    break
                else:
                    print(f"FAIL attempt {attempt}: {data.get('status')} {data.get('content_type')}")
                    diag = os.path.join(SAVE_DIR, f"ras_search_{i:02d}_diag_{attempt}.html")
                    with open(diag, "w", encoding="utf-8") as f:
                        f.write(data.get("text", ""))
                    # Мягкий бэкофф и короткий «прогрев» браузера на ras
                    sleep_s = backoff + random.uniform(0, 4)
                    time.sleep(sleep_s)
                    backoff *= 2
                    driver.get(RAS_HOME)
                    wait_ready(driver)
                    time.sleep(random.uniform(0.5, 1.0))
                    # Обновим куки в сессии вдруг что-то поменялось
                    session = session_from_driver(driver, ua)

            success += 1 if ok else 0
            fail += 0 if ok else 1
            # Базовая пауза между запросами
            time.sleep(max(0, BASE_DELAY + random.uniform(-JITTER, JITTER)))
        print(f"Done. Success: {success}, Fail: {fail}")
        input("Оставляю окно открытым. Enter для выхода...")
    finally:
        # driver.quit()
        pass

if __name__ == "__main__":
    main()


# не рабочий код, но сам подход... ловит 451 ошибку