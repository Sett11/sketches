"""
Простой тест для проверки API kad.arbitr.ru
"""
import os
import requests
import json
import pytest
import copy
from config.settings import SEARCH_REQUEST_CONFIG, URLS

# Заголовки, содержащие чувствительную информацию
SENSITIVE_HEADERS = {
    'authorization', 'cookie', 'set-cookie', 'x-api-key', 'x-auth-token',
    'x-access-token', 'x-csrf-token', 'x-session-token', 'bearer'
}

def redact_header(name, value):
    """
    Скрывает чувствительные заголовки и обрезает длинные значения
    """
    name_lower = name.lower()
    
    # Проверяем, содержит ли имя заголовка чувствительные ключевые слова
    is_sensitive = any(sensitive in name_lower for sensitive in SENSITIVE_HEADERS)
    
    if is_sensitive:
        return "***redacted***"
    
    # Обрезаем длинные значения до ~80 символов
    if isinstance(value, str) and len(value) > 80:
        return value[:77] + "..."
    
    return value

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
    headers = copy.deepcopy(SEARCH_REQUEST_CONFIG["headers"])
    
    # Используем правильную схему данных из конфигурации
    test_data = copy.deepcopy(SEARCH_REQUEST_CONFIG["json_template"])
    test_data.update({
        "Count": 5,
        "Page": 1,
        "DateFrom": "2024-01-01",
        "DateTo": "2024-01-31"
    })
    
    print(f"📋 Заголовки запроса:")
    for key, value in headers.items():
        print(f"   {key}: {redact_header(key, value)}")
    
    print(f"📋 Данные запроса:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(endpoint, json=test_data, headers=headers, timeout=10)
        print(f"\n📊 Результат запроса:")
        print(f"   Статус: {response.status_code}")
        print(f"   Заголовки ответа:")
        for key, value in response.headers.items():
            print(f"      {key}: {redact_header(key, value)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON ответ получен")
                print(f"   Ключи в ответе: {list(data.keys())}")
                
                # Ищем список документов
                documents_found = False
                for key in ['items', 'documents', 'results', 'data']:
                    if key in data and isinstance(data[key], list):
                        print(f"   📄 Найдены документы в поле '{key}': {len(data[key])} шт.")
                        if data[key]:
                            print(f"   Пример документа: {list(data[key][0].keys())}")
                        documents_found = True
                        break
                
                # Assert что список документов найден
                assert documents_found, "Список документов не найден в ответе"
                    
            except json.JSONDecodeError as e:
                pytest.fail(f"Не JSON ответ: {response.text[:200]}")
        elif response.status_code == 403:
            pytest.xfail("Доступ запрещен (403) - anti-bot защита активна")
        elif response.status_code == 429:
            pytest.xfail("Слишком много запросов (429) - rate limiting")
        else:
            pytest.fail(f"Неожиданный статус код {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        pytest.fail(f"Исключение: {e}")
    
    # Проверяем anti-bot защиту
    print(f"\n🛡️ Проверка anti-bot защиты:")
    if SEARCH_REQUEST_CONFIG.get("requires_wasm_token", False):
        print(f"   ⚠️ Эндпоинт требует WASM токен")
        print(f"   ⚠️ Обязательные cookies: {SEARCH_REQUEST_CONFIG.get('required_cookies', [])}")
        print(f"   💡 Рекомендации:")
        print(f"      - Соблюдайте условия использования сайта")
        print(f"      - Используйте официальные API или документированные методы доступа")
        print(f"      - Обратитесь к владельцу сайта за разрешением или поддержкой")
    
    print("\n" + "=" * 50)
    print("💡 Рекомендации:")
    print("1. Убедитесь в правильности JSON схемы запроса")
    print("2. Проверьте наличие обязательных cookies")
    print("3. Рассмотрите использование прокси для обхода anti-bot")
    print("4. Тестируйте с реальными браузерными cookies")

@pytest.mark.skipif(
    os.getenv("KAD_SMOKE") != "1",
    reason="Тест требует KAD_SMOKE=1 для запуска (пропускается по умолчанию для избежания нестабильности CI)"
)
def test_endpoint_with_proper_headers():
    """Тест эндпоинта с правильными заголовками и схемой"""
    print("🧪 Тестирование эндпоинта с правильной конфигурацией")
    print("=" * 60)
    
    # Создаем сессию с правильными заголовками
    session = requests.Session()
    session.headers.update(SEARCH_REQUEST_CONFIG["headers"])
    
    # Подготавливаем данные запроса
    test_data = copy.deepcopy(SEARCH_REQUEST_CONFIG["json_template"])
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
        print(f"   Content-Type: {redact_header('Content-Type', response.headers.get('Content-Type', 'N/A'))}")
        print(f"   Content-Length: {redact_header('Content-Length', response.headers.get('Content-Length', 'N/A'))}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Успешный JSON ответ")
                print(f"   📄 Ключи ответа: {list(data.keys())}")
                
                # Анализируем структуру ответа
                documents_found = False
                for key in ['items', 'documents', 'results', 'data']:
                    if key in data and isinstance(data[key], list):
                        print(f"   📄 Документы в '{key}': {len(data[key])} шт.")
                        if data[key]:
                            print(f"   📄 Пример полей документа: {list(data[key][0].keys())}")
                        documents_found = True
                        break
                
                # Assert что список документов найден
                assert documents_found, "Структура ответа не содержит списка документов"
                    
            except json.JSONDecodeError as e:
                pytest.fail(f"Ошибка парсинга JSON: {e}. Первые 200 символов ответа: {response.text[:200]}")
                
        elif response.status_code == 403:
            pytest.xfail("Доступ запрещен (403) - anti-bot защита активна")
        elif response.status_code == 429:
            pytest.xfail("Rate limiting (429) - слишком много запросов")
        else:
            pytest.fail(f"Неожиданный статус: {response.status_code}. Ответ: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        pytest.fail("Таймаут запроса")
    except requests.exceptions.ConnectionError:
        pytest.fail("Ошибка соединения")
    except Exception as e:
        pytest.fail(f"Неожиданная ошибка: {e}")
    
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
