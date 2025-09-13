"""
Простой тест для проверки API kad.arbitr.ru
"""
import requests
import json

def test_kad_arbitr_api():
    """Тестируем API kad.arbitr.ru"""
    print("🧪 Тестирование API kad.arbitr.ru")
    print("=" * 50)
    
    # Пробуем разные возможные endpoints
    endpoints = [
        "https://kad.arbitr.ru/api/search",
        "https://kad.arbitr.ru/Search",
        "https://kad.arbitr.ru/api/documents",
        "https://kad.arbitr.ru/api/cases"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"
    }
    
    test_data = {
        "Count": 5,
        "Page": 1,
        "DateFrom": "2024-01-01T00:00:00",
        "DateTo": "2024-01-31T23:59:59"
    }
    
    for endpoint in endpoints:
        print(f"\n🔍 Тестируем: {endpoint}")
        try:
            response = requests.post(endpoint, json=test_data, headers=headers, timeout=10)
            print(f"   Статус: {response.status_code}")
            
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
            else:
                print(f"   ❌ Ошибка: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Рекомендации:")
    print("1. Проверьте правильный endpoint в браузере")
    print("2. Убедитесь в правильности формата данных")
    print("3. Возможно нужна авторизация через cookies")

if __name__ == "__main__":
    test_kad_arbitr_api()
