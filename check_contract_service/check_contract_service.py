"""
Сервис проверки договоров check_contract
Получает текст договора, категоризирует его и проверяет на соответствие требованиям
"""

import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uuid
from datetime import datetime
try:
    # Pydantic v2
    from pydantic import ConfigDict
    HAS_CONFIGDICT = True
except Exception:
    HAS_CONFIGDICT = False
import httpx
import os
import pathlib
import asyncio
import threading
import time

# Настройка логирования

# Создаем папку logs если её нет
logs_dir = os.getenv("LOGS_DIR", "/app/logs")
try:
    pathlib.Path(logs_dir).mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"WARNING: Could not create logs directory {logs_dir}: {e}")
    # Fallback на текущую директорию
    logs_dir = "logs"
    try:
        pathlib.Path(logs_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e2:
        print(f"WARNING: Could not create fallback logs directory {logs_dir}: {e2}")
        logs_dir = "."  # Используем текущую директорию

# Настраиваем логирование в файл
log_filename = os.path.join(logs_dir, f"check_contract_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()  # Также выводим в консоль
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Check Contract Service", version="1.0.0")

# Конфигурация
LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
PROMPTS_FILE = os.getenv("PROMPTS_FILE", "/app/contract_prompts.json")

# Ранняя валидация критичных переменных окружения
if not LLM_API_URL:
    logger.error("ENV LLM_API_URL is empty — внешний LLM API недоступен до корректной настройки")
if not LLM_API_KEY:
    logger.error("ENV LLM_API_KEY is empty — авторизация к внешнему LLM невозможна")

class ContractRequest(BaseModel):
    contract_text: str
    user_prompt: str = ""

class ContractResponse(BaseModel):
    category: str
    validation_result: str
    is_valid: bool | None
    session_id: Optional[str] = None


class ContractAnalysis(BaseModel):
    contract_id: str
    contract_text: str
    analysis_result: str
    timestamp: datetime
    user_prompt: str = ""


class SessionData(BaseModel):
    session_id: str
    created_at: datetime
    contracts: list[ContractAnalysis] = []
    conversation_history: list[Dict[str, Any]] = []
    last_activity: datetime


class SessionManager:
    """Менеджер сессий для поддержки диалога и анализа нескольких договоров"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        self.cleanup_interval = 3600  # 1 час
        self.max_session_age = 86400  # 24 часа
    
    def create_session(self) -> str:
        """Создает новую сессию"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        self.sessions[session_id] = SessionData(
            session_id=session_id,
            created_at=now,
            last_activity=now
        )
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Получает данные сессии"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str):
        """Обновляет время последней активности"""
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.now()
    
    def add_contract_analysis(self, session_id: str, contract_text: str, analysis_result: str, user_prompt: str = ""):
        """Добавляет анализ договора в сессию"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for contract analysis")
            return
        
        # Валидация входных данных
        if not contract_text or not contract_text.strip():
            logger.warning("Empty contract_text provided")
            return
        
        if not analysis_result or not analysis_result.strip():
            logger.warning("Empty analysis_result provided")
            return
        
        
        contract_id = str(uuid.uuid4())
        analysis = ContractAnalysis(
            contract_id=contract_id,
            contract_text=contract_text,
            analysis_result=analysis_result,
            timestamp=datetime.now(),
            user_prompt=user_prompt or ""
        )
        
        # Ограничиваем количество договоров в сессии (предотвращаем утечки памяти)
        if len(self.sessions[session_id].contracts) > 20:
            # Удаляем старые договоры
            self.sessions[session_id].contracts = self.sessions[session_id].contracts[-10:]
            logger.info(f"Trimmed contract history for session {session_id}")
        
        self.sessions[session_id].contracts.append(analysis)
        self.update_session_activity(session_id)
        logger.info(f"Added contract analysis to session {session_id}: {contract_id}")
    
    def add_conversation_message(self, session_id: str, role: str, content: str):
        """Добавляет сообщение в историю диалога"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found for conversation message")
            return
        
        # Валидация входных данных
        if not role or not content:
            logger.warning("Empty role or content provided")
            return
        
        
        # Ограничиваем количество сообщений в истории (предотвращаем утечки памяти)
        if len(self.sessions[session_id].conversation_history) > 100:
            # Удаляем старые сообщения
            self.sessions[session_id].conversation_history = self.sessions[session_id].conversation_history[-50:]
            logger.info(f"Trimmed conversation history for session {session_id}")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.sessions[session_id].conversation_history.append(message)
        self.update_session_activity(session_id)
    
    def get_session_context(self, session_id: str) -> str:
        """Получает контекст сессии для передачи в LLM"""
        if session_id not in self.sessions:
            return ""
        
        session = self.sessions[session_id]
        context_parts = []
        
        # Добавляем историю диалога
        if session.conversation_history:
            context_parts.append("История диалога:")
            for msg in session.conversation_history[-10:]:  # Последние 10 сообщений
                context_parts.append(f"{msg['role']}: {msg['content']}")
        
        # Добавляем информацию о предыдущих договорах
        if session.contracts:
            context_parts.append(f"\nПредыдущие анализы договоров ({len(session.contracts)}):")
            for i, contract in enumerate(session.contracts[-3:], 1):  # Последние 3 договора
                context_parts.append(f"Договор {i}: {contract.analysis_result[:200]}...")
        
        return "\n".join(context_parts)
    
    def cleanup_old_sessions(self):
        """Очищает старые сессии"""
        try:
            now = datetime.now()
            to_remove = []
            
            # Защита от бесконечных циклов
            if len(self.sessions) > 1000:
                logger.warning(f"Too many sessions: {len(self.sessions)}, performing aggressive cleanup")
                # Удаляем самые старые сессии
                sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1].last_activity)
                to_remove = [sid for sid, _ in sorted_sessions[:500]]  # Удаляем 500 самых старых
            else:
                for session_id, session in self.sessions.items():
                    age = (now - session.last_activity).total_seconds()
                    if age > self.max_session_age:
                        to_remove.append(session_id)
            
            for session_id in to_remove:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    logger.info(f"Cleaned up old session: {session_id}")
            
            logger.info(f"Cleanup completed: removed {len(to_remove)} sessions, {len(self.sessions)} remaining")
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Получает статистику сессий"""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len([s for s in self.sessions.values() 
                                    if (datetime.now() - s.last_activity).total_seconds() < 3600])
        }


# -------- OpenAI-compatible schemas (minimal) --------
class ChatMessage(BaseModel):
    role: str
    content: Any  # Может быть строкой или списком частей (OpenAI content parts)


class ChatCompletionsRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    max_tokens: int | None = None
    temperature: float | None = None
    # Разрешаем дополнительные поля (attachments, contract_text и т.п.)
    if HAS_CONFIGDICT:
        model_config = ConfigDict(extra="allow")


class ChatChoiceMessage(BaseModel):
    role: str
    content: str


class ChatChoice(BaseModel):
    index: int
    message: ChatChoiceMessage
    finish_reason: str = "stop"


class ChatCompletionsResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]

class LLMClient:
    """Клиент для работы с LLM API"""
    
    def __init__(self, api_url: str, api_key: str, model: str):
        if not api_url or not api_key or not model:
            raise ValueError("LLMClient requires non-empty api_url, api_key, and model")
        
        self.api_url = api_url.rstrip('/')  # Убираем trailing slash
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(self, prompt: str) -> str:
        """Генерирует ответ от LLM (асинхронно)"""
        try:
            logger.info(f"LLM request using model='{self.model}', prompt_len={len(prompt)}")
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("LLM response: success")
                    
                    # Проверяем структуру ответа
                    if not result.get("choices") or len(result["choices"]) == 0:
                        logger.error("LLM response has no choices")
                        raise HTTPException(status_code=500, detail="Invalid LLM response format")
                    
                    choice = result["choices"][0]
                    if not choice.get("message") or not choice["message"].get("content"):
                        logger.error("LLM response has no content")
                        raise HTTPException(status_code=500, detail="Empty LLM response")
                    
                    return choice["message"]["content"]
                else:
                    logger.error(f"LLM API error: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=500, detail="LLM API error")
                    
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail="Request failed")
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise HTTPException(status_code=500, detail="Request timeout")

class ContractChecker:
    """Основной класс для проверки договоров (один запрос к модели)"""

    def __init__(self):
        try:
            self.llm_client = LLMClient(LLM_API_URL, LLM_API_KEY, LLM_MODEL)
        except ValueError as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            # Создаем заглушку для тестирования
            self.llm_client = None
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Загружает промты из JSON файла"""
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Prompts file not found: {PROMPTS_FILE}")
            return {"categories": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in prompts file: {e}")
            return {"categories": {}}


    async def check_contract(self, contract_text: str, user_prompt: str = "", session_id: str = None, context: str = "") -> ContractResponse:
        """Прозрачная прокладка с поддержкой контекста диалога и сессий."""
        try:
            logger.info(f"Начинаем проверку договора (passthrough), session_id={session_id}")
            
            # Проверяем доступность LLM клиента
            if not self.llm_client:
                error_msg = "LLM client not available - check configuration"
                logger.error(error_msg)
                return ContractResponse(
                    category="error",
                    validation_result=error_msg,
                    is_valid=False,
                    session_id=session_id
                )
            
            # Базовая инструкция с передачей JSON промтов
            instruction = (
                "Ты - эксперт по анализу договоров. Твоя задача:\n"
                "1. Определи категорию договора из предоставленного списка категорий\n"
                "2. Используй соответствующий промт для анализа\n"
                "3. Учти дополнительные требования пользователя\n"
                "4. Проведи анализ и верни результат\n\n"
                "Доступные категории и промты:\n"
                f"{json.dumps(self.prompts, ensure_ascii=False, indent=2)}"
            )
            
            # Формируем промт с контекстом
            master_prompt_parts = [instruction]
            
            # Добавляем контекст сессии если есть
            if context:
                master_prompt_parts.append(f"\nКонтекст предыдущих диалогов и анализов:\n{context}")
            
            # Добавляем пользовательский промт
            if user_prompt and user_prompt.strip():
                master_prompt_parts.append(f"\nДополнительные требования пользователя:\n{user_prompt.strip()}")
            
            # Добавляем текст договора
            master_prompt_parts.append(f"\nТекст договора:\n{contract_text}")
            
            master_prompt = "\n".join(master_prompt_parts)

            llm_output = await self.llm_client.generate_response(master_prompt)
            validation_result = llm_output or ""

            return ContractResponse(
                category="passthrough",
                validation_result=validation_result,
                is_valid=None,  # Нейтральное значение для passthrough режима
                session_id=session_id
            )
        except Exception as e:
            logger.error(f"Error in check_contract(single-pass): {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Модульные helper функции
def extract_simple_data(body: ChatCompletionsRequest) -> tuple[str, str]:
    """Простое извлечение данных из стандартного формата OpenWebUI"""
    contract_text = ""
    user_prompt = ""
    
    if not body.messages:
        logger.warning("No messages in request")
        return contract_text, user_prompt
    
    first_message = body.messages[0]
    
    # Извлекаем текст договора из attachments (если есть)
    try:
        if hasattr(body, 'attachments') and getattr(body, 'attachments', None):
            attachments = getattr(body, 'attachments', [])
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, dict) and attachment.get('content'):
                        contract_text = attachment.get('content', '')
                        break
    except Exception as e:
        logger.debug(f"Error extracting from attachments: {e}")
    
    # Извлекаем промт из сообщения пользователя
    if first_message.content:
        if isinstance(first_message.content, str):
            user_prompt = first_message.content
        elif isinstance(first_message.content, list):
            # Обрабатываем массив частей контента
            for part in first_message.content:
                if isinstance(part, dict) and part.get("type") == "text":
                    user_prompt = part.get("text", "")
                    break
    
    # Если не нашли в attachments, пробуем извлечь из контента сообщения
    if not contract_text and user_prompt:
        # Простая эвристика: если контент длинный, считаем его договором
        if len(user_prompt) > 1000:
            contract_text = user_prompt
            user_prompt = ""
    
    logger.info(f"Extracted: contract_len={len(contract_text)}, prompt_len={len(user_prompt)}")
    return contract_text, user_prompt






# Инициализация
contract_checker = ContractChecker()
session_manager = SessionManager()

# Периодическая очистка старых сессий

def cleanup_sessions_periodically():
    """Периодическая очистка старых сессий в фоновом режиме"""
    while True:
        try:
            session_manager.cleanup_old_sessions()
            logger.info("Performed periodic session cleanup")
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
        except KeyboardInterrupt:
            logger.info("Session cleanup thread interrupted")
            break
        time.sleep(3600)  # Каждый час

# Запускаем фоновую задачу очистки (только если не в тестовом режиме)
if not os.getenv("TESTING", "").lower() in ("true", "1", "yes"):
    try:
        cleanup_thread = threading.Thread(target=cleanup_sessions_periodically, daemon=True)
        cleanup_thread.start()
        logger.info("Started background session cleanup thread")
    except Exception as e:
        logger.error(f"Failed to start cleanup thread: {e}")
else:
    logger.info("Skipping cleanup thread in testing mode")

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "check_contract"}

@app.get("/v1/models")
@app.get("/models")
async def list_models():
    """Минимальный список моделей для OpenAI-совместимого клиента (OpenWebUI)."""
    return {
        "object": "list",
        "data": [
            {
                "id": "check-contract",
                "object": "model",
                "created": 0,
                "owned_by": "local",
            }
        ],
    }

@app.post("/check", response_model=ContractResponse)
async def check_contract(request: ContractRequest, http_request: Request = None):
    """
    Основной endpoint для проверки договора
    """
    try:
        # Валидация входных данных
        if not request.contract_text or not request.contract_text.strip():
            raise HTTPException(status_code=400, detail="Contract text cannot be empty")
        
        
        # Получаем session_id если есть
        session_id = None
        if http_request:
            session_id = http_request.headers.get("X-Session-ID")
            if session_id:
                # Валидируем формат UUID
                try:
                    uuid.UUID(session_id)
                except ValueError:
                    session_id = None
        
        # Создаем новую сессию если нет
        if not session_id:
            session_id = session_manager.create_session()
        
        # Получаем контекст сессии
        session_context = session_manager.get_session_context(session_id)
        
        logger.info(f"Получен запрос на проверку договора (длина текста: {len(request.contract_text)}, session_id: {session_id})")
        
        result = await contract_checker.check_contract(
            contract_text=request.contract_text,
            user_prompt=request.user_prompt,
            session_id=session_id,
            context=session_context
        )
        
        # Сохраняем анализ в сессию
        session_manager.add_contract_analysis(
            session_id, 
            request.contract_text, 
            result.validation_result, 
            request.user_prompt
        )
        
        logger.info(f"Проверка завершена. Категория: {result.category}, Валиден: {result.is_valid}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /check endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions", response_model=ChatCompletionsResponse)
@app.post("/chat/completions", response_model=ChatCompletionsResponse)
async def chat_completions(body: ChatCompletionsRequest, request: Request):
    """OpenAI-совместимая обертка. Извлекает текст из сообщений и возвращает результат проверки."""
    try:
        logger.info(f"/v1/chat/completions: model='{body.model}', messages={len(body.messages)}")

        # Простое извлечение данных из стандартного формата OpenWebUI
        contract_text, user_prompt = extract_simple_data(body)

        if not contract_text:
            raise HTTPException(status_code=400, detail="contract_text is empty")

        # Получаем или создаем session_id из заголовков
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            # Валидируем формат UUID
            try:
                uuid.UUID(session_id)
                # Проверяем существование сессии
                if not session_manager.get_session(session_id):
                    session_id = None
            except ValueError:
                session_id = None
        
        if not session_id:
            session_id = session_manager.create_session()
            logger.info(f"Created new session for request: {session_id}")

        # Получаем контекст сессии
        session_context = session_manager.get_session_context(session_id)
        
        # Добавляем сообщение пользователя в историю диалога
        if user_prompt:
            session_manager.add_conversation_message(session_id, "user", user_prompt)

        logger.info(f"/v1/chat/completions: contract_text_len={len(contract_text)}, session_id={session_id}")
        result = await contract_checker.check_contract(
            contract_text=contract_text, 
            user_prompt=user_prompt,
            session_id=session_id,
            context=session_context
        )
        
        # Сохраняем анализ в сессию
        session_manager.add_contract_analysis(
            session_id, 
            contract_text, 
            result.validation_result, 
            user_prompt
        )
        
        # Добавляем ответ ассистента в историю диалога
        session_manager.add_conversation_message(session_id, "assistant", result.validation_result)

        # Формируем OpenAI-совместимый ответ
        now_ts = int(time.time())
        response = ChatCompletionsResponse(
            id=f"chatcmpl_{now_ts}",
            created=now_ts,
            model=body.model or "check-contract",
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatChoiceMessage(
                        role="assistant",
                        content=result.validation_result,
                    ),
                )
            ],
        )
        
        # Сохраняем session_id в response для логирования
        logger.info(f"Response generated for session: {session_id}")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /v1/chat/completions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Возвращает доступные категории договоров"""
    return {"categories": list(contract_checker.prompts.get("categories", {}).keys())}

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Получает информацию о сессии"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "contracts_count": len(session.contracts),
        "conversation_messages": len(session.conversation_history)
    }

@app.get("/sessions/{session_id}/contracts")
async def get_session_contracts(session_id: str):
    """Получает список договоров в сессии"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    contracts = []
    for contract in session.contracts:
        contracts.append({
            "contract_id": contract.contract_id,
            "timestamp": contract.timestamp.isoformat(),
            "user_prompt": contract.user_prompt,
            "analysis_preview": contract.analysis_result[:200] + "..." if len(contract.analysis_result) > 200 else contract.analysis_result
        })
    
    return {"contracts": contracts}

@app.get("/sessions/{session_id}/conversation")
async def get_session_conversation(session_id: str):
    """Получает историю диалога сессии"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"conversation": session.conversation_history}

@app.post("/sessions/{session_id}/compare")
async def compare_contracts(session_id: str, contract_ids: list[str]):
    """Сравнивает несколько договоров в сессии"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Находим договоры для сравнения
    contracts_to_compare = []
    for contract_id in contract_ids:
        for contract in session.contracts:
            if contract.contract_id == contract_id:
                contracts_to_compare.append(contract)
                break
    
    if len(contracts_to_compare) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 contracts to compare")
    
    # Формируем промт для сравнения
    comparison_prompt = "Сравни следующие договоры и выяви основные различия, риски и рекомендации:\n\n"
    
    for i, contract in enumerate(contracts_to_compare, 1):
        comparison_prompt += f"Договор {i}:\n{contract.analysis_result}\n\n"
    
    # Отправляем запрос к LLM для сравнения
    try:
        comparison_result = await contract_checker.llm_client.generate_response(comparison_prompt)
        
        # Добавляем результат сравнения в историю диалога
        session_manager.add_conversation_message(session_id, "system", f"Сравнение договоров: {comparison_result}")
        
        return {
            "comparison_result": comparison_result,
            "compared_contracts": len(contracts_to_compare),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error comparing contracts: {e}")
        raise HTTPException(status_code=500, detail="Error comparing contracts")

@app.get("/sessions/stats")
async def get_sessions_stats():
    """Получает статистику сессий"""
    return session_manager.get_session_stats()

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Удаляет сессию"""
    if session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del session_manager.sessions[session_id]
    logger.info(f"Deleted session: {session_id}")
    return {"message": "Session deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
