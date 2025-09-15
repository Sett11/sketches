"""
Простой Gradio дашборд для управления парсером
"""
import gradio as gr
import importlib
import json
import os
import sys
from datetime import datetime, timedelta

def safe_import(module_paths, item_name=None):
    """
    Устойчивый импорт модулей с fallback логикой
    
    Args:
        module_paths: список путей для импорта в порядке приоритета
        item_name: имя элемента для импорта из модуля (если None, импортируется весь модуль)
    
    Returns:
        Импортированный модуль или элемент
    """
    for module_path in module_paths:
        try:
            module = importlib.import_module(module_path)
            return getattr(module, item_name) if item_name else module
        except ImportError:
            continue
    
    # Если все попытки не удались, добавляем корень проекта в sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Пробуем импортировать с абсолютным путем
    try:
        module = importlib.import_module(module_paths[-1])  # Берем последний путь как абсолютный
        return getattr(module, item_name) if item_name else module
    except ImportError:
        raise ImportError(f"Не удалось импортировать {module_paths[-1]} даже после добавления {project_root} в sys.path")

# Устойчивые импорты - работают как при запуске как пакета, так и как скрипта
create_batch_parser = safe_import(
    ["src.core.batch_parser", "..core.batch_parser"],
    "create_batch_parser"
)

create_puppeteer_batch_parser = safe_import(
    ["src.core.puppeteer_batch_parser", "..core.puppeteer_batch_parser"],
    "create_puppeteer_batch_parser"
)

create_cookie_automation = safe_import(
    ["src.core.cookie_automation", "..core.cookie_automation"],
    "create_cookie_automation"
)

cookie_manager = safe_import(
    ["src.utils.cookie_manager", "..utils.cookie_manager"],
    "cookie_manager"
)

date_manager = safe_import(
    ["src.utils.date_manager", "..utils.date_manager"],
    "date_manager"
)

settings_module = safe_import(
    ["config.settings", "...config.settings"]
)
DOCS_DIR = settings_module.DOCS_DIR
LOGS_DIR = settings_module.LOGS_DIR

def get_server_name():
    """
    Получить имя сервера из переменной окружения с безопасным дефолтом
    
    Returns:
        str: Имя сервера для привязки (127.0.0.1 по умолчанию для безопасности)
    """
    server_name = os.environ.get('GRADIO_SERVER_NAME', '127.0.0.1')
    
    # Валидация и нормализация
    if not server_name or not isinstance(server_name, str):
        server_name = '127.0.0.1'
    
    server_name = server_name.strip()
    
    # Предупреждение при использовании небезопасного значения
    if server_name == '0.0.0.0':
        print("⚠️  ВНИМАНИЕ: Сервер привязан к 0.0.0.0 - доступен извне!")
        print("   Убедитесь, что это намеренно (например, за прокси)")
    
    return server_name

class GradioDashboard:
    """Простой дашборд для управления парсером"""
    
    def __init__(self):
        self.parser = None
        self.parser_type = "puppeteer"  # По умолчанию используем Puppeteer
        self.cookie_automation = create_cookie_automation()
        self.initialize_parser()
    
    def initialize_parser(self):
        """Инициализация парсера"""
        try:
            if self.parser_type == "puppeteer":
                self.parser = create_puppeteer_batch_parser()
                # Инициализируем браузер
                if not self.parser.initialize():
                    print("❌ Ошибка инициализации Puppeteer, переключаемся на requests")
                    self.parser_type = "requests"
                    self.parser = create_batch_parser()
            else:
                self.parser = create_batch_parser()
                
            print(f"✅ Парсер инициализирован: {self.parser_type}")
        except Exception as e:
            print(f"❌ Ошибка инициализации парсера: {e}")
            # Fallback на requests парсер
            self.parser_type = "requests"
            self.parser = create_batch_parser()
    
    def start_parsing(self, start_date, end_date, cookies_text):
        """Запустить парсинг"""
        try:
            # Обработка cookies
            if cookies_text.strip():
                cookies_dict = json.loads(cookies_text)
                cookie_manager.save_cookies(cookies_dict)
                self.parser.set_cookies(cookies_dict)
            
            # Загружаем существующие cookies если есть
            if cookie_manager.load_cookies():
                self.parser.set_cookies(cookie_manager.get_cookies())
            
            # Парсинг дат
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            if self.parser_type == "puppeteer":
                # Используем Puppeteer для обработки всего диапазона
                total_downloaded = self.parser.process_date_range(
                    start_date, 
                    end_date, 
                    max_pages=40
                )
                
                # Сохраняем метаданные
                self.parser.save_metadata()
                
                stats = self.parser.get_stats()
                
                return f"""
                ✅ Парсинг завершен через Puppeteer!
                
                📊 Статистика:
                • Скачано документов: {total_downloaded}
                • Парсер: {self.parser_type}
                • Статус: {stats.get('is_initialized', False)}
                
                📁 Файлы сохранены в: {DOCS_DIR}
                
                🚀 Puppeteer успешно обошел anti-bot защиту!
                """
            else:
                # Используем старый requests подход
                date_ranges = date_manager.generate_date_ranges(start_dt, end_dt)
                
                results = []
                total_downloaded = 0
                
                for date_range in date_ranges:
                    result = self.parser.process_date_range(
                        date_range["start"], 
                        date_range["end"]
                    )
                    total_downloaded += result
                    results.append(f"Период {date_range['start'][:10]} - {date_range['end'][:10]}: {result} документов")
                
                # Сохраняем метаданные
                self.parser.save_metadata()
                
                stats = self.parser.get_stats()
                
                return f"""
                ✅ Парсинг завершен через requests!
                
                📊 Статистика:
                • Скачано документов: {total_downloaded}
                • Запросов использовано: {stats['rate_limiter_status']['requests_made']}
                • Осталось запросов: {stats['rate_limiter_status']['remaining']}
                
                📁 Файлы сохранены в: {DOCS_DIR}
                
                📋 Обработанные периоды:
                {chr(10).join(results)}
                """
            
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def get_stats(self):
        """Получить текущую статистику"""
        try:
            # Статистика парсера
            stats = self.parser.get_stats()
            
            # Количество файлов в docs
            docs_count = len([f for f in os.listdir(DOCS_DIR) if f.endswith('.pdf')]) if os.path.exists(DOCS_DIR) else 0
            
            # Статус cookies
            cookies_status = "✅ Загружены" if cookie_manager.is_valid() else "❌ Не загружены"
            
            if self.parser_type == "puppeteer":
                return f"""
                📊 Текущая статистика (Puppeteer):
                
                📁 Документы: {docs_count} PDF файлов
                🍪 Cookies: {cookies_status}
                🚀 Парсер: Puppeteer с stealth плагином
                📈 Скачано: {stats.get('downloaded_count', 0)} документов
                ⚙️ Инициализирован: {stats.get('is_initialized', False)}
                📅 Последнее обновление: {stats.get('last_update', 'Неизвестно')}
                """
            else:
                return f"""
                📊 Текущая статистика (Requests):
                
                📁 Документы: {docs_count} PDF файлов
                🍪 Cookies: {cookies_status}
                🚀 Парсер: Requests
                📈 Запросов сегодня: {stats['rate_limiter_status']['requests_made']}/{stats['rate_limiter_status']['max_requests']}
                ⏰ Сброс лимита: {stats['rate_limiter_status']['daily_reset'].strftime('%H:%M:%S')}
                """
            
        except Exception as e:
            return f"❌ Ошибка получения статистики: {str(e)}"
    
    def load_cookies_from_file(self, file_path):
        """Загрузить cookies из файла"""
        try:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                return json.dumps(cookies, ensure_ascii=False, indent=2)
            else:
                return "❌ Файл не найден"
        except Exception as e:
            return f"❌ Ошибка загрузки файла: {str(e)}"
    
    def auto_extract_cookies(self):
        """Автоматически извлечь cookies"""
        try:
            result = self.cookie_automation.extract_cookies(save_to_file=True)
            
            if result['success']:
                cookies_json = json.dumps(result['cookies'], ensure_ascii=False, indent=2)
                
                return f"""✅ Cookies автоматически собраны!

🍪 Статистика:
• Всего cookies: {result['validation']['foundCookies']}
• Критически важных: {len(result['validation']['criticalCookies'])}
• Статус: {'✅ Валидны' if result['validation']['isValid'] else '⚠️ Требуют проверки'}

📁 Сохранено в: {DOCS_DIR}/auto_extracted_cookies.json

🚀 Теперь можно запускать парсинг!

{cookies_json}"""
            else:
                return f"""❌ Ошибка автоматического сбора cookies:

{result.get('error', 'Неизвестная ошибка')}

💡 Попробуйте:
1. Проверить интернет соединение
2. Убедиться что kad.arbitr.ru доступен
3. Повторить попытку через несколько минут"""
                
        except Exception as e:
            return f"❌ Критическая ошибка: {str(e)}"
    
    def create_interface(self):
        """Создать интерфейс"""
        
        with gr.Blocks(title="Парсер Арбитражных Дел") as interface:
            gr.Markdown("# 🔍 Парсер Арбитражных Дел")
            gr.Markdown("Простой интерфейс для массовой загрузки решений арбитражных судов")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## ⚙️ Настройки")
                    
                    start_date = gr.Textbox(
                        label="Дата начала (YYYY-MM-DD)",
                        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        placeholder="2024-01-01"
                    )
                    
                    end_date = gr.Textbox(
                        label="Дата окончания (YYYY-MM-DD)",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        placeholder="2024-12-31"
                    )
                    
                    cookies_input = gr.Textbox(
                        label="Cookies (JSON формат)",
                        placeholder='{"cookie_name": "cookie_value", ...}',
                        lines=5,
                        max_lines=10
                    )
                    
                    with gr.Row():
                        start_btn = gr.Button("🚀 Начать парсинг", variant="primary")
                        stats_btn = gr.Button("📊 Статистика")
                    
                    with gr.Row():
                        auto_cookies_btn = gr.Button("🍪 Авто-сбор cookies", variant="secondary")
                        clear_btn = gr.Button("🗑️ Очистить", variant="stop")
                    
                    cookie_file = gr.File(
                        label="Или загрузить cookies из файла",
                        file_types=[".json"]
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("## 📋 Результаты")
                    
                    output = gr.Textbox(
                        label="Вывод",
                        lines=15,
                        max_lines=20,
                        interactive=False
                    )
            
            # Обработчики событий
            start_btn.click(
                fn=self.start_parsing,
                inputs=[start_date, end_date, cookies_input],
                outputs=output
            )
            
            stats_btn.click(
                fn=self.get_stats,
                inputs=[],
                outputs=output
            )
            
            cookie_file.change(
                fn=self.load_cookies_from_file,
                inputs=[cookie_file],
                outputs=cookies_input
            )
            
            auto_cookies_btn.click(
                fn=self.auto_extract_cookies,
                inputs=[],
                outputs=cookies_input
            )
            
            clear_btn.click(
                fn=lambda: "",
                inputs=[],
                outputs=cookies_input
            )
            
            # Информация
            gr.Markdown("""
            ## ℹ️ Информация
            
            **🚀 Автоматический сбор cookies:**
            - Нажмите "🍪 Авто-сбор cookies" для автоматического получения всех нужных cookies
            - Puppeteer автоматически обойдет anti-bot защиту
            - Cookies будут сохранены и готовы к использованию
            
            **Ограничения:**
            - Максимум 500 запросов в день
            - 25 документов на страницу
            - Фильтрация по ключевым словам
            
            **Фильтры:**
            - ✅ Включаем: решения, кассации, постановления
            - ❌ Исключаем: переносы, отклонения, назначения времени
            
            ## 🍪 Ручной способ получения Cookies (если авто-сбор не работает):
            
            1. Откройте https://kad.arbitr.ru в браузере
            2. Откройте Developer Tools (F12)
            3. Перейдите на вкладку Application/Storage → Cookies
            4. Найдите **ОБЯЗАТЕЛЬНЫЙ** cookie: `pr_fp`
            5. Скопируйте его в формате JSON:
            ```json
            {
                "pr_fp": "значение_из_браузера"
            }
            ```
            
            **⚠️ Важно:** 
            - 🚀 **РЕКОМЕНДУЕТСЯ**: Использовать автоматический сбор cookies!
            - Без `pr_fp` парсинг НЕ РАБОТАЕТ!
            - Cookies работают ограниченное время, затем нужно обновлять!
            - Другие cookies (`wasm`, `PHPSESSID` и т.д.) опциональны
            """)
        
        return interface
    
    def launch(self, share=False, port=7860):
        """Запустить дашборд"""
        interface = self.create_interface()
        server_name = get_server_name()
        interface.launch(share=share, server_port=port, server_name=server_name)

# Создание и запуск дашборда
if __name__ == "__main__":
    dashboard = GradioDashboard()
    dashboard.launch()
