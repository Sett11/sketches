#!/usr/bin/env python3
"""
Быстрая проверка лимитов API (БЕЗ списания запросов!)
Только читает статистику - не делает запросов к данным
"""
import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

API_KEY = os.getenv('API_KEY')
STAT_URL = os.getenv('API_STAT_URL', 'https://service.api-assist.com/stat/')

if not API_KEY:
    print("❌ Ошибка: API_KEY не установлен в .env файле.")
    exit(1)

def check_limits():
    """Проверка лимитов API (НЕ списывается!)"""
    try:
        url = f"{STAT_URL}?key={API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # API возвращает список: [{"service": "ras_arbitr", ...}]
        if isinstance(data, list) and len(data) > 0:
            info = data[0]
        else:
            info = data  # На случай если вернётся словарь напрямую
        
        print("=" * 60)
        print("📊 ЛИМИТЫ API КАДР АРБИТР")
        print("=" * 60)
        print(f"Дневной лимит:      {info.get('day_limit', 'N/A')}")
        print(f"Использовано сегодня: {info.get('day_request_count', 'N/A')}")
        print(f"Осталось сегодня:   {info.get('day_limit', 0) - info.get('day_request_count', 0)}")
        print()
        print(f"Месячный лимит:     {info.get('month_limit', 'N/A')}")
        print(f"Использовано за месяц: {info.get('month_request_count', 'N/A')}")
        print(f"Осталось за месяц:  {info.get('month_limit', 0) - info.get('month_request_count', 0)}")
        print()
        print(f"Оплачено до:        {info.get('paid_till', 'N/A')}")
        print("=" * 60)
        
        # Предупреждения
        day_remaining = info.get('day_limit', 0) - info.get('day_request_count', 0)
        if day_remaining < 50:
            print("⚠️  ВНИМАНИЕ: Осталось мало дневных запросов!")
        elif day_remaining < 100:
            print("⚠️  Дневной лимит заканчивается")
        else:
            print("✅ Лимитов достаточно для работы")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при проверке лимитов: {e}")
        return False

if __name__ == "__main__":
    check_limits()

