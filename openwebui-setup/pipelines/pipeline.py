import os
import base64
from typing import Dict, Any
from datetime import datetime

# Импортируем наш логгер
import sys
# Добавляем текущую директорию в путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from mylogger import Logger

# Настройка логирования
logger = Logger('DOCUMENT_TRANSFORM_PIPELINE', 'logs/document_transform.log')

class DocumentTransformPipeline:
    """Упрощенный Pipeline для трансформации документов с помощью LLM"""
    
    def __init__(self):
        logger.info("🚀 Document Transform Pipeline инициализирован")
    
    def transform_document(self, file_data: str, filename: str, prompt: str) -> Dict[str, Any]:
        """Трансформация документа с помощью LLM"""
        try:
            logger.info(f"Начинаем трансформацию документа: {filename}")
            
            # Создаем временные папки для файлов
            os.makedirs("docs", exist_ok=True)
            os.makedirs("new_docs", exist_ok=True)
            
            # Сохраняем загруженный файл
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_filename = f"{timestamp}_{filename}"
            input_path = f"docs/{input_filename}"
            
            # Обрабатываем file_data (может быть base64 или bytes)
            if isinstance(file_data, str):
                # Предполагаем base64
                file_bytes = base64.b64decode(file_data)
            else:
                file_bytes = file_data
            
            with open(input_path, 'wb') as f:
                f.write(file_bytes)
            
            logger.info(f"Файл сохранен: {input_path}")
            
            # Импортируем и используем DocumentTransformPipeline
            try:
                from document_transform_pipeline import get_pipeline
                transform_pipeline = get_pipeline()
                if not transform_pipeline:
                    return {
                        "success": False,
                        "error": "Не удалось инициализировать pipeline трансформации"
                    }
            except ImportError as e:
                logger.error(f"❌ Ошибка импорта DocumentTransformPipeline: {e}")
                return {
                    "success": False,
                    "error": f"Не удалось загрузить модуль трансформации: {e}"
                }
            
            # Трансформируем документ
            result = transform_pipeline.transform_document(input_path, prompt)
            
            if result.get("success"):
                # Читаем трансформированный файл для возврата
                transformed_path = result["transformed_file"]
                with open(transformed_path, 'rb') as f:
                    transformed_data = f.read()
                
                # Кодируем в base64 для передачи
                transformed_base64 = base64.b64encode(transformed_data).decode('utf-8')
                
                return {
                    "success": True,
                    "transformed_file": transformed_base64,
                    "transformed_filename": os.path.basename(transformed_path),
                    "message": "Документ успешно трансформирован"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Неизвестная ошибка трансформации")
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка трансформации документа: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Создание экземпляра Pipeline
pipeline = DocumentTransformPipeline()

def pipe(request: Dict[str, Any]) -> Dict[str, Any]:
    """Основная функция обработки запросов"""
    try:
        action = request.get("action", "transform_document")
        data = request.get("data", {})
        
        logger.info(f"🔍 Обработка запроса: {action}")
        
        if action == "transform_document":
            # Обработка трансформации документов
            file_data = data.get("file_data")  # base64 или multipart данные
            prompt = data.get("prompt", "")
            filename = data.get("filename", "document.docx")
            
            if not file_data:
                return {"error": "Не предоставлен файл для трансформации"}
            
            if not prompt:
                return {"error": "Не указан промт для трансформации"}
            
            result = pipeline.transform_document(file_data, filename, prompt)
            return {"action": action, "result": result}
        
        else:
            return {"error": f"Неизвестное действие: {action}. Доступно только: transform_document"}
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки запроса: {e}")
        return {"error": str(e)}

def on_startup():
    """Инициализация при запуске"""
    logger.info("🚀 Document Transform Pipeline запущен")
    logger.info("📁 Папки: docs/ (входные файлы), new_docs/ (обработанные файлы)")

def on_shutdown():
    """Очистка при остановке"""
    logger.info("🛑 Document Transform Pipeline остановлен")