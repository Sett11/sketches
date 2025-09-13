"""
Главный файл приложения - парсер арбитражных дел
"""
import sys
import os

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.dashboard.gradio_app import GradioDashboard
from src.utils.logger import logger

def main():
    """Главная функция"""
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
