import logging
import os
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

#from utils.mylogger import Logger
#logger=Logger('MOEX', '_moexlogs.log')


class Logger(logging.Logger):
    """Класс, обеспечивающий настройку логгирования с ротацией логов по времени."""
    def __init__(self, name, log_file, level=logging.INFO):
        """
        Инициализация класса Logger.

        :param name: Имя логгера.
        :param log_file: Имя файла для сохранения логов.
        :param level: Уровень логгирования.
        """
        # Валидация параметра name
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Parameter 'name' must be a non-empty string")
        
        # Валидация параметра log_file
        if not isinstance(log_file, (str, Path)) or not str(log_file).strip():
            raise ValueError("Parameter 'log_file' must be a non-empty string or Path-like object")
        
        # Валидация параметра level
        if not isinstance(level, (int, str)) and level not in [
            logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        ]:
            if isinstance(level, int):
                if level < 0 or level > 50:  # logging levels range from 0 to 50
                    raise ValueError(f"Invalid logging level: {level}. Must be between 0 and 50")
            else:
                raise TypeError(f"Parameter 'level' must be an integer or valid logging level constant, got {type(level)}")
        
        super().__init__(name, level)

        # Форматтер
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Попытка создания обработчика для ротации файлов по времени с обработкой ошибок
        handler = None
        try:
            # Преобразование log_file в Path объект для удобства работы
            log_path = Path(log_file)
            
            # Создание директории для логов если она не существует
            log_dir = log_path.parent
            if log_dir != Path('.') and not log_dir.exists():
                try:
                    log_dir.mkdir(parents=True, exist_ok=True)
                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not create log directory {log_dir}: {e}")
                    raise
            
            # Создание обработчика для ротации файлов по времени
            handler = TimedRotatingFileHandler(
                log_file, 
                when="midnight", 
                interval=1, 
                encoding='utf-8'
            )
            handler.suffix = "%Y-%m-%d"
            handler.setFormatter(formatter)
            
        except (OSError, PermissionError, ValueError, FileNotFoundError) as e:
            # В случае ошибки создания файлового обработчика, используем fallback
            print(f"Warning: Could not create file handler for {log_file}: {e}")
            print("Falling back to console logging...")
            
            try:
                # Создаем StreamHandler как fallback
                handler = logging.StreamHandler(sys.stderr)
                handler.setFormatter(formatter)
                handler.setLevel(logging.WARNING)  # Выводим только важные сообщения в stderr
            except Exception as fallback_error:
                # Если даже StreamHandler не удалось создать, используем базовую настройку
                print(f"Critical: Could not create any handler: {fallback_error}")
                logging.basicConfig(
                    level=level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stderr
                )
                return

        # Добавление обработчика в логгер
        if handler:
            self.addHandler(handler)
