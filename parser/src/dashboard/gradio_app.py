"""
Простой Gradio дашборд для управления парсером
"""
import gradio as gr
import json
import os
import sys
from datetime import datetime, timedelta

# Устойчивые импорты - работают как при запуске как пакета, так и как скрипта
try:
    from src.core.batch_parser import create_batch_parser
except ImportError:
    try:
        from ..core.batch_parser import create_batch_parser
    except ImportError:
        # Добавляем корень проекта в sys.path для абсолютных импортов
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from src.core.batch_parser import create_batch_parser

try:
    from src.utils.cookie_manager import cookie_manager
except ImportError:
    try:
        from ..utils.cookie_manager import cookie_manager
    except ImportError:
        # Добавляем корень проекта в sys.path для абсолютных импортов
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from src.utils.cookie_manager import cookie_manager

try:
    from src.utils.date_manager import date_manager
except ImportError:
    try:
        from ..utils.date_manager import date_manager
    except ImportError:
        # Добавляем корень проекта в sys.path для абсолютных импортов
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from src.utils.date_manager import date_manager

try:
    from config.settings import DOCS_DIR, LOGS_DIR
except ImportError:
    try:
        from ...config.settings import DOCS_DIR, LOGS_DIR
    except ImportError:
        # Добавляем корень проекта в sys.path для абсолютных импортов
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from config.settings import DOCS_DIR, LOGS_DIR

class GradioDashboard:
    """Простой дашборд для управления парсером"""
    
    def __init__(self):
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
            
            # Генерируем диапазоны дат
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
            ✅ Парсинг завершен!
            
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
            
            return f"""
            📊 Текущая статистика:
            
            📁 Документы: {docs_count} PDF файлов
            🍪 Cookies: {cookies_status}
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
            
            # Информация
            gr.Markdown("""
            ## ℹ️ Информация
            
            **Ограничения:**
            - Максимум 500 запросов в день
            - 25 документов на страницу
            - Фильтрация по ключевым словам
            
            **Фильтры:**
            - ✅ Включаем: решения, кассации, постановления
            - ❌ Исключаем: переносы, отклонения, назначения времени
            
            ## 🍪 Как получить Cookies:
            
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
            - Без `pr_fp` парсинг НЕ РАБОТАЕТ!
            - Cookies работают ограниченное время, затем нужно обновлять!
            - Другие cookies (`wasm`, `PHPSESSID` и т.д.) опциональны
            """)
        
        return interface
    
    def launch(self, share=False, port=7860):
        """Запустить дашборд"""
        interface = self.create_interface()
        interface.launch(share=share, server_port=port, server_name="0.0.0.0")

# Создание и запуск дашборда
if __name__ == "__main__":
    dashboard = GradioDashboard()
    dashboard.launch()
