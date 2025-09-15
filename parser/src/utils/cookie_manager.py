"""
Простое управление cookies с поддержкой переменных окружения
"""
import json
import os

from config.settings import BASE_DIR

class CookieManager:
    """Менеджер cookies с приоритетами: env var > local file > example file"""
    
    def __init__(self, cookies_file="cookies.json"):
        self.cookies_file = os.path.join(BASE_DIR, "config", cookies_file)
        self.example_file = os.path.join(os.path.dirname(BASE_DIR), "cookies.example.json")
        self.cookies = {}
    
    def load_cookies(self):
        """Загрузить cookies с приоритетами: env var > local file > example file"""
        try:
            # 1. Проверяем переменную окружения PR_FP (высший приоритет)
            pr_fp_env = os.environ.get('PR_FP')
            if pr_fp_env:
                self.cookies = {"pr_fp": pr_fp_env}
                print(f"Загружено {len(self.cookies)} cookies из переменной окружения PR_FP")
                return True
            
            # 2. Проверяем локальный файл cookies.json (средний приоритет)
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
                print(f"Загружено {len(self.cookies)} cookies из локального файла")
                return True
            
            # 3. Проверяем example файл (низший приоритет)
            if os.path.exists(self.example_file):
                with open(self.example_file, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
                print(f"Загружено {len(self.cookies)} cookies из example файла (только для демонстрации)")
                return True
            
            print("Файлы cookies не найдены")
            return False
        except Exception as e:
            print(f"Ошибка загрузки cookies: {e}")
            return False
    
    def save_cookies(self, cookies_dict):
        """Сохранить cookies в локальный файл (не в example)"""
        try:
            # Создаем папку config если её нет
            os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
            
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
            
            self.cookies = cookies_dict
            print(f"Сохранено {len(cookies_dict)} cookies в локальный файл")
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
