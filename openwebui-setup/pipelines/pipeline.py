"""
title: Document Transform Pipeline
author: open-webui
date: 2024-12-19
version: 1.0
license: MIT
description: A pipeline for transforming Word documents using LLM
requirements: python-docx, requests
"""

import os
import base64
from typing import Dict, Any, Union, Generator, Iterator, List
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

class Pipeline:
    def __init__(self):
        self.logger = Logger('DOCUMENT_TRANSFORM_PIPELINE', 'logs/document_transform.log')
        self.logger.info("🚀 Document Transform Pipeline инициализирован")

    async def on_startup(self):
        """Функция вызывается при запуске сервера"""
        self.logger.info("🚀 Document Transform Pipeline запущен")
        self.logger.info("📁 Папки: docs/ (входные файлы), new_docs/ (обработанные файлы)")
        # Создаем необходимые папки
        os.makedirs("docs", exist_ok=True)
        os.makedirs("new_docs", exist_ok=True)

    async def on_shutdown(self):
        """Функция вызывается при остановке сервера"""
        self.logger.info("🛑 Document Transform Pipeline остановлен")

    def transform_document(self, file_data: str, filename: str, prompt: str) -> Dict[str, Any]:
        """Трансформация документа"""
        try:
            self.logger.info(f"Начинаем трансформацию документа: {filename}")
            
            # Декодируем файл из base64
            if isinstance(file_data, str):
                file_bytes = base64.b64decode(file_data)
            else:
                file_bytes = file_data
            
            # Сохраняем файл
            input_path = f"docs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            with open(input_path, 'wb') as f:
                f.write(file_bytes)
            self.logger.info(f"Файл сохранен: {input_path}")
            
            # Импортируем и используем DocumentTransformPipeline
            try:
                from document_transform_pipeline import get_pipeline
                transform_pipeline = get_pipeline()
                if not transform_pipeline:
                    return {"success": False, "error": "Не удалось инициализировать pipeline трансформации"}
            except ImportError as e:
                self.logger.error(f"❌ Ошибка импорта DocumentTransformPipeline: {e}")
                return {"success": False, "error": f"Не удалось загрузить модуль трансформации: {e}"}
            
            # Выполняем трансформацию
            result = transform_pipeline.transform_document(input_path, prompt)
            
            if result.get("success"):
                # Читаем трансформированный файл и возвращаем в base64
                transformed_path = result["transformed_file"]
                with open(transformed_path, 'rb') as f:
                    transformed_data = f.read()
                transformed_base64 = base64.b64encode(transformed_data).decode('utf-8')
                
                return {
                    "success": True,
                    "transformed_file": transformed_base64,
                    "transformed_filename": os.path.basename(transformed_path),
                    "message": "Документ успешно трансформирован"
                }
            else:
                return {"success": False, "error": result.get("error", "Неизвестная ошибка трансформации")}
        except Exception as e:
            self.logger.error(f"❌ Ошибка трансформации документа: {e}")
            return {"success": False, "error": str(e)}

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Основная функция pipeline для обработки запросов
        Соответствует стандарту OpenWebUI Pipelines
        """
        try:
            self.logger.info(f"🔍 Обработка запроса: {user_message}")
            
            # Извлекаем данные из body
            file_data = body.get("file_data")
            prompt = body.get("prompt", user_message)  # Используем user_message как промт по умолчанию
            filename = body.get("filename", "document.docx")
            
            if not file_data:
                return "❌ Не предоставлен файл для трансформации"
            
            if not prompt:
                return "❌ Не указан промт для трансформации"
            
            # Выполняем трансформацию
            result = self.transform_document(file_data, filename, prompt)
            
            if result.get("success"):
                return f"✅ {result.get('message', 'Документ успешно трансформирован')}"
            else:
                return f"❌ {result.get('error', 'Ошибка трансформации')}"
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки запроса: {e}")
            return f"❌ Ошибка: {str(e)}"