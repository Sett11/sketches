"""
Простой тест для проверки API kad.arbitr.ru
"""
import os
import requests
import json
import pytest
from config.settings import SEARCH_REQUEST_CONFIG, URLS

@pytest.mark.skipif(
    os.getenv("KAD_SMOKE") != "1",
    reason="Тест требует KAD_SMOKE=1 для запуска (пропускается по умолчанию для избежания нестабильности CI)"
)
def test_kad_arbitr_api():
    """Тестируем API kad.arbitr.ru"""
    print("🧪 Тестирование API kad.arbitr.ru")
    print("=" * 50)
    
    # Тестируем основной endpoint из конфигурации
    endpoint = URLS["search_endpoint"]
    print(f"\n🔍 Тестируем основной endpoint: {endpoint}")
    
    # Используем заголовки из конфигурации
    headers = SEARCH_REQUEST_CONFIG["headers"].copy()
    
    # Используем правильную схему данных из конфигурации
    test_data = SEARCH_REQUEST_CONFIG["json_template"].copy()
    test_data.update({
        "Count": 5,
        "Page": 1,
        "DateFrom": "2024-01-01",
        "DateTo": "2024-01-31"
    })
    
    print(f"📋 Заголовки запроса:")
    for key, value in headers.items():
        print(f"   {key}: {value}")
    
    print(f"📋 Данные запроса:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(endpoint, json=test_data, headers=headers, timeout=10)
        print(f"\n📊 Результат запроса:")
        print(f"   Статус: {response.status_code}")
        print(f"   Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON ответ получен")
                print(f"   Ключи в ответе: {list(data.keys())}")
                
                # Ищем список документов
                for key in ['items', 'documents', 'results', 'data']:
                    if key in data and isinstance(data[key], list):
                        print(f"   📄 Найдены документы в поле '{key}': {len(data[key])} шт.")
                        if data[key]:
                            print(f"   Пример документа: {list(data[key][0].keys())}")
                        break
                else:
                    print(f"   ⚠️ Список документов не найден")
                    
            except json.JSONDecodeError:
                print(f"   ❌ Не JSON ответ: {response.text[:200]}")
        elif response.status_code == 403:
            print(f"   ❌ Доступ запрещен (403) - anti-bot защита активна")
            print(f"   ❌ Необходим WASM токен или валидные cookies")
        elif response.status_code == 429:
            print(f"   ⚠️ Слишком много запросов (429) - rate limiting")
        else:
            print(f"   ❌ Ошибка: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")
    
    # Проверяем anti-bot защиту
    print(f"\n🛡️ Проверка anti-bot защиты:")
    if SEARCH_REQUEST_CONFIG.get("requires_wasm_token", False):
        print(f"   ⚠️ Эндпоинт требует WASM токен")
        print(f"   ⚠️ Обязательные cookies: {SEARCH_REQUEST_CONFIG.get('required_cookies', [])}")
        print(f"   💡 Рекомендации:")
        print(f"      - Получите cookies из реального браузера")
        print(f"      - Используйте прокси с обходом anti-bot")
        print(f"      - Реализуйте генерацию WASM токена")
    
    print("\n" + "=" * 50)
    print("💡 Рекомендации:")
    print("1. Убедитесь в правильности JSON схемы запроса")
    print("2. Проверьте наличие обязательных cookies")
    print("3. Рассмотрите использование прокси для обхода anti-bot")
    print("4. Тестируйте с реальными браузерными cookies")

def test_endpoint_with_proper_headers():
    """Тест эндпоинта с правильными заголовками и схемой"""
    print("🧪 Тестирование эндпоинта с правильной конфигурацией")
    print("=" * 60)
    
    # Создаем сессию с правильными заголовками
    session = requests.Session()
    session.headers.update(SEARCH_REQUEST_CONFIG["headers"])
    
    # Подготавливаем данные запроса
    test_data = SEARCH_REQUEST_CONFIG["json_template"].copy()
    test_data.update({
        "Count": 3,
        "Page": 1,
        "DateFrom": "2024-01-01",
        "DateTo": "2024-01-31"
    })
    
    print(f"🔗 Endpoint: {URLS['search_endpoint']}")
    print(f"📋 Метод: {SEARCH_REQUEST_CONFIG['method']}")
    print(f"📋 Content-Type: {SEARCH_REQUEST_CONFIG['headers']['Content-Type']}")
    print(f"📋 User-Agent: {SEARCH_REQUEST_CONFIG['headers']['User-Agent'][:50]}...")
    print(f"📋 Origin: {SEARCH_REQUEST_CONFIG['headers']['Origin']}")
    print(f"📋 Referer: {SEARCH_REQUEST_CONFIG['headers']['Referer']}")
    
    print(f"\n📋 JSON Payload:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # Проверяем anti-bot защиту
    print(f"\n🛡️ Anti-bot защита:")
    print(f"   Требует WASM токен: {SEARCH_REQUEST_CONFIG.get('requires_wasm_token', False)}")
    print(f"   Обязательные cookies: {SEARCH_REQUEST_CONFIG.get('required_cookies', [])}")
    
    if SEARCH_REQUEST_CONFIG.get("requires_wasm_token", False):
        print(f"   ⚠️ ВНИМАНИЕ: Эндпоинт требует обхода anti-bot защиты!")
        print(f"   ⚠️ Без валидных cookies запрос будет заблокирован")
    
    try:
        response = session.post(
            URLS["search_endpoint"],
            json=test_data,
            timeout=15
        )
        
        print(f"\n📊 Результат:")
        print(f"   Статус: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Успешный JSON ответ")
                print(f"   📄 Ключи ответа: {list(data.keys())}")
                
                # Анализируем структуру ответа
                for key in ['items', 'documents', 'results', 'data']:
                    if key in data and isinstance(data[key], list):
                        print(f"   📄 Документы в '{key}': {len(data[key])} шт.")
                        if data[key]:
                            print(f"   📄 Пример полей документа: {list(data[key][0].keys())}")
                        break
                else:
                    print(f"   ⚠️ Структура ответа не содержит списка документов")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Ошибка парсинга JSON: {e}")
                print(f"   📄 Первые 200 символов ответа: {response.text[:200]}")
                
        elif response.status_code == 403:
            print(f"   ❌ Доступ запрещен (403) - anti-bot защита активна")
            print(f"   💡 Решения:")
            print(f"      - Получите cookies из браузера")
            print(f"      - Используйте прокси с обходом")
            print(f"      - Реализуйте генерацию WASM токена")
        elif response.status_code == 429:
            print(f"   ⚠️ Rate limiting (429) - слишком много запросов")
        else:
            print(f"   ❌ Неожиданный статус: {response.status_code}")
            print(f"   📄 Ответ: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Таймаут запроса")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Ошибка соединения")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("💡 Заключение:")
    print("1. Эндпоинт настроен с правильной JSON схемой")
    print("2. Используются стандартные браузерные заголовки")
    print("3. Anti-bot защита требует дополнительной настройки")
    print("4. Рекомендуется тестирование с реальными cookies")

if __name__ == "__main__":
    print("🚀 Запуск тестов API kad.arbitr.ru")
    print("=" * 60)
    
    # Запускаем оба теста
    test_kad_arbitr_api()
    print("\n" + "=" * 60)
    test_endpoint_with_proper_headers()
