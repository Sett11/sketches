import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server import NotificationOptions

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalMCPServer:
    """MCP сервер для работы с юридическими документами"""
    
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
            
            # Анализ типа документа
            if file_info["extension"] == ".pdf":
                file_info["type"] = "PDF документ"
                file_info["status"] = "Документ уже обработан и находится в базе данных"
            else:
                file_info["type"] = "Неизвестный формат"
                file_info["status"] = "Документ не поддерживается"
            
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

# Создание экземпляра сервера
legal_server = LegalMCPServer()

# Создание MCP сервера
server = Server("legal-documents-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Список доступных инструментов"""
    return [
        Tool(
            name="analyze_legal_document",
            description="Анализ юридического документа (PDF, текст)",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "Путь к документу для анализа"
                    }
                },
                "required": ["document_path"]
            }
        ),
        Tool(
            name="search_legal_documents",
            description="Поиск юридических документов по запросу с поддержкой типов эмбеддингов",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос"
                    },
                    "embedding_type": {
                        "type": "string",
                        "description": "Тип эмбеддинга: small (параграфы), medium (статьи), large (главы), all (все)",
                        "enum": ["small", "medium", "large", "all"],
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество результатов",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="answer_legal_question",
            description="Ответ на юридический вопрос на основе базы документов",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Юридический вопрос"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="extract_legal_entities",
            description="Извлечение правовых сущностей из текста",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Текст для анализа"
                    }
                },
                "required": ["text"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка вызовов инструментов"""
    try:
        if name == "analyze_legal_document":
            document_path = arguments.get("document_path")
            if not document_path:
                return [TextContent(type="text", text="❌ Не указан путь к документу")]
            
            result = legal_server.analyze_legal_document(document_path)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "search_legal_documents":
            query = arguments.get("query", "")
            embedding_type = arguments.get("embedding_type", "all")
            limit = arguments.get("limit", 5)
            
            if not query:
                return [TextContent(type="text", text="❌ Не указан поисковый запрос")]
            
            results = legal_server.search_similar_documents(query, embedding_type, limit)
            return [TextContent(type="text", text=json.dumps({
                "query": query,
                "embedding_type": embedding_type,
                "results": results,
                "count": len(results)
            }, ensure_ascii=False, indent=2))]
        
        elif name == "answer_legal_question":
            question = arguments.get("question", "")
            if not question:
                return [TextContent(type="text", text="❌ Не указан вопрос")]
            
            result = legal_server.answer_legal_question(question)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "extract_legal_entities":
            text = arguments.get("text", "")
            if not text:
                return [TextContent(type="text", text="❌ Не указан текст для анализа")]
            
            result = legal_server.extract_legal_entities(text)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"❌ Неизвестный инструмент: {name}")]
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки инструмента {name}: {e}")
        return [TextContent(type="text", text=f"❌ Ошибка: {str(e)}")]

async def main():
    """Основная функция запуска сервера"""
    logger.info("🚀 Запуск Legal Documents MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
