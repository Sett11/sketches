

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalPipeline:
    """Pipeline для работы с юридическими документами"""
    
    def __init__(self):
        self.model = None
        self.db_connection = None
        self.setup_database()
        self.load_embedding_model()
    
    def setup_database(self):
        """Подключение к внешней базе данных PostgreSQL с pgvector"""
        try:
            # Парсим DB_URL для получения хоста и порта
            db_url = os.getenv('DB_URL', '')
            if ':' in db_url:
                host, port = db_url.split(':')
            else:
                host = db_url
                port = '5432'
            
            self.db_connection = psycopg2.connect(
                host=host,
                port=port,
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            logger.info(f"✅ Подключение к внешней БД установлено: {host}:{port}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            self.db_connection = None
    
    def load_embedding_model(self):
        """Загрузка модели для создания эмбеддингов"""
        try:
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ Модель эмбеддингов загружена")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели: {e}")
            self.model = None
    
    def create_embeddings(self, text: str) -> Optional[List[float]]:
        """Создание эмбеддингов для текста"""
        if not self.model:
            return None
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Ошибка создания эмбеддингов: {e}")
            return None
    
    def search_similar_documents(self, query: str, embedding_type: str = "all", limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск похожих документов в базе данных по типам эмбеддингов"""
        if not self.db_connection or not self.model:
            return []
        
        try:
            query_embedding = self.create_embeddings(query)
            if not query_embedding:
                return []
            
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            
            # Определяем таблицу в зависимости от типа эмбеддинга
            if embedding_type == "small":
                table_name = "paragraphs"  # Малые - параграфы
            elif embedding_type == "medium":
                table_name = "articles"    # Средние - статьи
            elif embedding_type == "large":
                table_name = "chapters"    # Большие - главы
            else:
                # Поиск по всем типам
                results = []
                for table in ["paragraphs", "articles", "chapters"]:
                    table_results = self._search_in_table(cursor, table, query_embedding, limit // 3)
                    results.extend(table_results)
                cursor.close()
                return sorted(results, key=lambda x: x['similarity'], reverse=True)[:limit]
            
            # Поиск в конкретной таблице
            results = self._search_in_table(cursor, table_name, query_embedding, limit)
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска в БД: {e}")
            return []
    
    def _search_in_table(self, cursor, table_name: str, query_embedding: List[float], limit: int) -> List[Dict[str, Any]]:
        """Поиск в конкретной таблице"""
        try:
            cursor.execute(f"""
                SELECT 
                    id,
                    title,
                    content,
                    document_path,
                    created_at,
                    embedding_type,
                    1 - (embedding <=> %s) as similarity
                FROM {table_name} 
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (query_embedding, query_embedding, limit))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска в таблице {table_name}: {e}")
            return []
    
    def analyze_legal_document(self, document_path: str) -> Dict[str, Any]:
        """Анализ юридического документа"""
        try:
            # Проверяем существование файла
            if not os.path.exists(document_path):
                return {"error": "Файл не найден"}
            
            # Получаем информацию о файле
            file_info = {
                "path": document_path,
                "name": os.path.basename(document_path),
                "size": os.path.getsize(document_path),
                "extension": os.path.splitext(document_path)[1].lower()
            }
            
            # Если это PDF, пытаемся извлечь текст
            if file_info["extension"] == ".pdf":
                # Здесь можно добавить логику извлечения текста из PDF
                # Пока возвращаем базовую информацию
                file_info["type"] = "PDF документ"
                file_info["status"] = "Готов к обработке"
            else:
                file_info["type"] = "Неизвестный формат"
                file_info["status"] = "Требует конвертации"
            
            return file_info
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа документа: {e}")
            return {"error": str(e)}
    
    def answer_legal_question(self, question: str, context_documents: List[Dict] = None) -> Dict[str, Any]:
        """Ответ на юридический вопрос"""
        try:
            # Поиск релевантных документов
            relevant_docs = self.search_similar_documents(question, limit=3)
            
            # Формирование контекста
            context = ""
            if relevant_docs:
                context = "\n\n".join([
                    f"Документ: {doc['title']}\nСодержание: {doc['content'][:500]}..."
                    for doc in relevant_docs
                ])
            
            # Формирование ответа
            response = {
                "question": question,
                "relevant_documents": relevant_docs,
                "context": context,
                "answer": f"На основе найденных документов: {context[:200]}..." if context else "Релевантные документы не найдены",
                "confidence": len(relevant_docs) / 3.0 if relevant_docs else 0.0
            }
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки вопроса: {e}")
            return {"error": str(e)}
    
    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """Извлечение правовых сущностей из текста"""
        try:
            # Простое извлечение ключевых слов (можно улучшить с помощью NER)
            legal_keywords = [
                "договор", "соглашение", "закон", "статья", "пункт", "параграф",
                "сторона", "обязательство", "ответственность", "право", "обязанность",
                "срок", "условие", "требование", "заявление", "иск", "суд"
            ]
            
            found_entities = []
            for keyword in legal_keywords:
                if keyword.lower() in text.lower():
                    found_entities.append(keyword)
            
            return {
                "legal_entities": found_entities,
                "count": len(found_entities),
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения сущностей: {e}")
            return {"error": str(e)}

# Создание экземпляра Pipeline
pipeline = LegalPipeline()

def pipe(request: Dict[str, Any]) -> Dict[str, Any]:
    """Основная функция обработки запросов"""
    try:
        action = request.get("action", "analyze")
        data = request.get("data", {})
        
        logger.info(f"🔍 Обработка запроса: {action}")
        
        if action == "analyze_document":
            document_path = data.get("document_path")
            if not document_path:
                return {"error": "Не указан путь к документу"}
            
            result = pipeline.analyze_legal_document(document_path)
            return {"action": action, "result": result}
        
        elif action == "search_documents":
            query = data.get("query", "")
            embedding_type = data.get("embedding_type", "all")  # small, medium, large, all
            limit = data.get("limit", 5)
            
            results = pipeline.search_similar_documents(query, embedding_type, limit)
            return {"action": action, "results": results, "count": len(results), "embedding_type": embedding_type}
        
        elif action == "answer_question":
            question = data.get("question", "")
            if not question:
                return {"error": "Не указан вопрос"}
            
            result = pipeline.answer_legal_question(question)
            return {"action": action, "result": result}
        
        elif action == "extract_entities":
            text = data.get("text", "")
            if not text:
                return {"error": "Не указан текст для анализа"}
            
            result = pipeline.extract_legal_entities(text)
            return {"action": action, "result": result}
        
        else:
            return {"error": f"Неизвестное действие: {action}"}
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки запроса: {e}")
        return {"error": str(e)}

def on_startup():
    """Инициализация при запуске"""
    logger.info("🚀 Юридический Pipeline запущен")
    logger.info(f"📁 Папка документов: {os.getenv('LEGAL_DOCUMENTS_PATH', '/app/legal_documents')}")
    logger.info(f"🗄️ База данных: {os.getenv('DB_NAME', 'legal_db')}")

def on_shutdown():
    """Очистка при остановке"""
    if pipeline.db_connection:
        pipeline.db_connection.close()
    logger.info("🛑 Юридический Pipeline остановлен")
