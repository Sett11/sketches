"""
Главный файл приложения - парсер арбитражных дел
"""
import sys
import os
import traceback

from src.dashboard.gradio_app import GradioDashboard
from src.utils.logger import logger
from config.settings import ensure_dirs

def main():
    """Главная функция"""
    # Инициализируем файловую систему
    try:
        ensure_dirs()
    except Exception as e:
        print("Ошибка при инициализации файловой системы:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    logger.info("Запуск парсера арбитражных дел")
    
    try:
        # Создаем и запускаем дашборд
        dashboard = GradioDashboard()
        dashboard.launch(share=False, port=7860)
        
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
