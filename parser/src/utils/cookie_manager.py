"""
Простое управление cookies
"""
import json
import os

from config.settings import BASE_DIR

class CookieManager:
    """Простой менеджер cookies"""
    
    def __init__(self, cookies_file="cookies.json"):
        self.cookies_file = os.path.join(BASE_DIR, "config", cookies_file)
        self.cookies = {}
    
    def load_cookies(self):
        """Загрузить cookies из файла"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
                print(f"Загружено {len(self.cookies)} cookies")
                return True
            else:
                print("Файл cookies не найден")
                return False
        except Exception as e:
            print(f"Ошибка загрузки cookies: {e}")
            return False
    
    def save_cookies(self, cookies_dict):
        """Сохранить cookies в файл"""
        try:
            # Создаем папку config если её нет
            os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
            
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
            
            self.cookies = cookies_dict
            print(f"Сохранено {len(cookies_dict)} cookies")
            return True
        except Exception as e:
            print(f"Ошибка сохранения cookies: {e}")
            return False
    
    def get_cookies(self):
        """Получить текущие cookies"""
        return self.cookies
    
    def is_valid(self):
        """Проверить есть ли cookies"""
        return len(self.cookies) > 0

# Глобальный менеджер cookies
cookie_manager = CookieManager()
