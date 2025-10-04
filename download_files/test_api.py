#!/usr/bin/env python3
"""
Скрипт для тестирования API КАДР Арбитр
Проверяет доступность API и структуру ответа
Запуск: python test_api.py
"""
import requests
import json
from datetime import datetime, timedelta

API_KEY = "997834c96856bb3783da8c42a59d06b3"
API_URL = "https://service.api-assist.com/parser/ras_arbitr_api/"
STAT_URL = "https://service.api-assist.com/stat/"

def test_limits():
    """Проверка лимитов API"""
    print("=" * 60)
    print("1. Проверка лимитов API")
    print("=" * 60)
    
    try:
        url = f"{STAT_URL}?key={API_KEY}"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("\n✅ Ответ API (лимиты):")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        return True
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False

def test_metadata():
    """Проверка получения метаданных"""
    print("\n" + "=" * 60)
    print("2. Проверка получения метаданных")
    print("=" * 60)
    
    try:
        # Запрос за вчерашний день
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = (f"{API_URL}?key={API_KEY}"
               f"&DateFrom={yesterday}&DateTo={yesterday}"
               f"&Page=1&Text='решение'")
        
        print(f"URL: {url}")
        print(f"Дата: {yesterday}")
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n✅ Ответ API (метаданные):")
        print(f"Ключи ответа: {list(data.keys())}")
        
        if 'items' in data:
            items = data['items']
            print(f"Количество items: {len(items)}")
            
            if items:
                print("\n📄 Структура первого item:")
                first_item = items[0]
                print(json.dumps(first_item, ensure_ascii=False, indent=2)[:1000])
                
                # Проверяем наличие важных полей
                print("\n🔍 Проверка полей:")
                fields_to_check = [
                    'CaseNumber', 'CaseId', 'Type', 'InstanceLevel', 
                    'ContentTypes', 'FileUrl', 'FileName', 'Court', 'RegistrationDate'
                ]
                for field in fields_to_check:
                    if field in first_item:
                        value = first_item[field]
                        print(f"  ✓ {field}: {type(value).__name__} = {str(value)[:150]}")
                    else:
                        print(f"  ✗ {field}: отсутствует")
                
                # Специальная проверка FileUrl
                if 'FileUrl' in first_item:
                    print(f"\n✅ FileUrl найден! Это прямая ссылка на PDF:")
                    print(f"   {first_item['FileUrl']}")
                else:
                    print(f"\n⚠️ FileUrl отсутствует! Проверьте структуру API.")
        else:
            print("⚠️ В ответе нет поля 'items'")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
        
        if 'pages' in data:
            print(f"\n📊 Всего страниц: {data['pages']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🔬 ТЕСТ API КАДР АРБИТР")
    print("=" * 60)
    
    # Тест 1: лимиты
    limits_ok = test_limits()
    
    # Тест 2: метаданные
    metadata_ok = test_metadata()
    
    # Итоги
    print("\n" + "=" * 60)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 60)
    print(f"Лимиты API: {'✅ OK' if limits_ok else '❌ FAIL'}")
    print(f"Метаданные: {'✅ OK' if metadata_ok else '❌ FAIL'}")
    
    if limits_ok and metadata_ok:
        print("\n✅ Все тесты пройдены! API работает корректно.")
    else:
        print("\n❌ Некоторые тесты не прошли. Проверьте API или ключ.")

if __name__ == "__main__":
    main()

