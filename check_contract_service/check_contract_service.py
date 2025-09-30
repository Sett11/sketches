"""
Сервис проверки договоров check_contract
Получает текст договора, категоризирует его и проверяет на соответствие требованиям
"""

import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
try:
    # Pydantic v2
    from pydantic import ConfigDict
    HAS_CONFIGDICT = True
except Exception:
    HAS_CONFIGDICT = False
import requests
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
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
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, prompt: str) -> str:
        """Генерирует ответ от LLM"""
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
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("LLM response: success")
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="LLM API error")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail="Request failed")

class ContractChecker:
    """Основной класс для проверки договоров (один запрос к модели)"""

    def __init__(self):
        self.llm_client = LLMClient(LLM_API_URL, LLM_API_KEY, LLM_MODEL)
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


    def check_contract(self, contract_text: str, user_prompt: str = "") -> ContractResponse:
        """Прозрачная прокладка: один запрос к модели и возврат её ответа как есть."""
        try:
            logger.info("Начинаем проверку договора (passthrough)")
            instruction = (
                "Проведи юридический анализ текста договора: выяви риски, несоответствия закону, пробелы, "
                "неоднозначные формулировки, рекомендации по исправлению и краткий итог. Ответ верни простым текстом."
            )
            
            # Включаем user_prompt в master_prompt, если он не пустой
            master_prompt = f"{instruction}\n\nТекст договора:\n{contract_text}"
            if user_prompt and user_prompt.strip():
                master_prompt = f"{instruction}\n\nДополнительные требования пользователя:\n{user_prompt.strip()}\n\nТекст договора:\n{contract_text}"

            llm_output = self.llm_client.generate_response(master_prompt)
            validation_result = (llm_output or "").strip()

            return ContractResponse(
                category="passthrough",
                validation_result=validation_result,
                is_valid=None,  # Нейтральное значение для passthrough режима
            )
        except Exception as e:
            logger.error(f"Error in check_contract(single-pass): {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Модульные helper функции
def normalize_content(raw: Any, captured_json_parts: list[dict[str, Any]] = None) -> str:
    """Нормализатор контента: извлекает текст из строки или массива частей"""
    if captured_json_parts is None:
        captured_json_parts = []
    
    try:
        if raw is None:
            return ""
        if isinstance(raw, str):
            return raw
        if isinstance(raw, list):
            parts: list[str] = []
            for item in raw:
                if isinstance(item, dict):
                    item_type = item.get("type")
                    # Стандарт OpenAI: {type: "text", text: "..."} и {type: "input_text", text: "..."}
                    if item_type in ("text", "input_text") and isinstance(item.get("text"), str):
                        parts.append(item.get("text", ""))
                    # Поддержка {type:"input_json", json:{...}}
                    elif item_type == "input_json" and isinstance(item.get("json"), dict):
                        captured_json_parts.append(item.get("json"))
                        try:
                            parts.append(json.dumps(item.get("json"), ensure_ascii=False))
                        except (json.JSONDecodeError, TypeError, ValueError):
                            pass
                    # Некоторые клиенты кладут "content" вместо text
                    elif isinstance(item.get("content"), str):
                        parts.append(item.get("content", ""))
                elif isinstance(item, str):
                    parts.append(item)
            return "\n\n".join([p for p in parts if p])
        if isinstance(raw, dict):
            # Единичный объект input_json
            if raw.get("type") == "input_json" and isinstance(raw.get("json"), dict):
                captured_json_parts.append(raw.get("json"))
                try:
                    return json.dumps(raw.get("json"), ensure_ascii=False)
                except (json.JSONDecodeError, TypeError, ValueError):
                    return ""
            # Нетривиальные клиенты
            if isinstance(raw.get("text"), str):
                return raw.get("text", "")
            if isinstance(raw.get("content"), str):
                return raw.get("content", "")
        return str(raw)
    except Exception:
        return ""


def extract_contract_text_from_messages(body: ChatCompletionsRequest, raw_payload: dict[str, Any]) -> tuple[str, str, str, int]:
    """Извлекает текст договора и пользовательский промт из сообщений"""
    captured_json_parts: list[dict[str, Any]] = []
    
    # Сливаем все пользовательские сообщения в один текст (для совместимости с простыми клиентами)
    user_messages = [m for m in body.messages if m.role == "user" and m.content]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message provided")

    concatenated_user_text = "\n\n".join([
        normalized.strip() for m in user_messages 
        for normalized in [normalize_content(m.content, captured_json_parts)] 
        if normalized.strip()
    ])
    content = concatenated_user_text
    logger.info(f"/v1/chat/completions: combined_user_text_len={len(content)}")

    # Дополнительно: ищем самый длинный текст среди ВСЕХ сообщений (любой роли)
    longest_text = content
    longest_len = len(longest_text)
    for msg in body.messages:
        try:
            txt = normalize_content(msg.content, captured_json_parts).strip()
            if txt and len(txt) > longest_len:
                longest_text = txt
                longest_len = len(txt)
        except Exception:
            continue

    # Пытаемся распарсить JSON c полями contract_text/user_prompt, иначе воспринимаем весь контент как текст договора
    contract_text = content
    user_prompt = ""
    parsed_from_text = False
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and parsed.get("contract_text"):
            contract_text = str(parsed.get("contract_text") or "").strip()
            user_prompt = str(parsed.get("user_prompt") or "").strip()
            parsed_from_text = True
            logger.info(f"/v1/chat/completions: detected JSON payload in text, contract_len={len(contract_text)}, user_prompt_len={len(user_prompt)}")
    except json.JSONDecodeError:
        logger.info("/v1/chat/completions: text is not JSON")

    # Если не удалось распарсить из текста, пробуем достать из input_json частей
    if not parsed_from_text and captured_json_parts:
        for obj in captured_json_parts:
            if isinstance(obj, dict) and obj.get("contract_text"):
                contract_text = str(obj.get("contract_text") or "").strip()
                user_prompt = str(obj.get("user_prompt") or "").strip()
                logger.info(f"/v1/chat/completions: detected input_json part, contract_len={len(contract_text)}, user_prompt_len={len(user_prompt)}")
                break

    return contract_text, user_prompt, longest_text, longest_len


def extract_from_attachment(att: dict, current_best: str) -> str:
    """Извлекает текст из attachment, возвращает более длинный кандидат если найден"""
    try:
        if not isinstance(att, dict) or not isinstance(current_best, str):
            return ""
        
        # Частые варианты: {type:"text", content:"..."} или {mime:"text/plain", data:"..."}
        if isinstance(att.get("content"), str) and att.get("type") in ("text", "document"):
            candidate = att.get("content")
            if len(candidate) > len(current_best):
                logger.info(f"/v1/chat/completions: extracted from attachments.content, len={len(candidate)}")
                return candidate
        elif isinstance(att.get("data"), str) and str(att.get("mime")).startswith("text"):
            candidate = att.get("data")
            if len(candidate) > len(current_best):
                logger.info(f"/v1/chat/completions: extracted from attachments.data, len={len(candidate)}")
                return candidate
    except Exception:
        pass
    return ""


# Инициализация
contract_checker = ContractChecker()

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
async def check_contract(request: ContractRequest):
    """
    Основной endpoint для проверки договора
    """
    try:
        # Валидация входных данных
        if not request.contract_text or not request.contract_text.strip():
            raise HTTPException(status_code=400, detail="Contract text cannot be empty")
        
        if len(request.contract_text) > 50000:  # Ограничение на размер
            raise HTTPException(status_code=400, detail="Contract text too long (max 50000 characters)")
        
        logger.info(f"Получен запрос на проверку договора (длина текста: {len(request.contract_text)})")
        
        result = contract_checker.check_contract(
            contract_text=request.contract_text,
            user_prompt=request.user_prompt
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
        # Полный дамп входного json (без чувствительных данных) для извлечения дополнительных полей
        try:
            raw_payload: dict[str, Any] = body.model_dump()  # pydantic v2
        except Exception:
            try:
                raw_payload = body.dict()  # pydantic v1 fallback
            except Exception:
                raw_payload = {}

        # Извлекаем текст договора и пользовательский промт из сообщений
        contract_text, user_prompt, longest_text, longest_len = extract_contract_text_from_messages(body, raw_payload)

        # Если всё ещё нет текста — пробуем извлечь из root-полей (attachments/contract_text)
        if not contract_text or len(contract_text) < 30:
            # contract_text на корневом уровне
            if isinstance(raw_payload.get("contract_text"), str) and raw_payload.get("contract_text").strip():
                contract_text = raw_payload.get("contract_text").strip()
                user_prompt = str(raw_payload.get("user_prompt") or "").strip()
                logger.info(f"/v1/chat/completions: detected root contract_text, contract_len={len(contract_text)}, user_prompt_len={len(user_prompt)}")
            # attachments
            elif isinstance(raw_payload.get("attachments"), list):
                for att in raw_payload.get("attachments"):
                    candidate = extract_from_attachment(att, contract_text)
                    if candidate:
                        contract_text = candidate
            # Поиск вложенного contract_text в любых словарях сообщений
            if (not contract_text or len(contract_text) < 30) and body.messages:
                # просматриваем все сообщения (любой роли), чтобы повторные вызовы тоже подхватывали текст из истории
                for m in body.messages:
                    try:
                        if isinstance(m.content, list):
                            for part in m.content:
                                if isinstance(part, dict) and part.get("contract_text"):
                                    candidate = str(part.get("contract_text") or "").strip()
                                    if len(candidate) > len(contract_text):
                                        contract_text = candidate
                                        user_prompt = str(part.get("user_prompt") or "").strip()
                                        logger.info(f"/v1/chat/completions: found nested contract_text in message part, len={len(contract_text)}")
                        elif isinstance(m.content, dict) and m.content.get("contract_text"):
                            candidate = str(m.content.get("contract_text") or "").strip()
                            if len(candidate) > len(contract_text):
                                contract_text = candidate
                                user_prompt = str(m.content.get("user_prompt") or "").strip()
                                logger.info(f"/v1/chat/completions: found nested contract_text in message dict, len={len(contract_text)}")
                    except Exception:
                        continue

                # Также пытаемся извлечь из attachments на уровне каждого сообщения (через raw_payload)
                try:
                    messages_raw = raw_payload.get("messages") if isinstance(raw_payload, dict) else None
                    if isinstance(messages_raw, list):
                        for rm in messages_raw:
                            if not isinstance(rm, dict):
                                continue
                            atts = rm.get("attachments")
                            if isinstance(atts, list):
                                for att in atts:
                                    candidate = extract_from_attachment(att, contract_text)
                                    if candidate:
                                        contract_text = candidate
                except Exception:
                    pass

        # Если по-прежнему коротко — подставим самый длинный найденный свободный текст из истории
        if (not contract_text or len(contract_text) < 30) and longest_len >= 100:
            contract_text = longest_text
            logger.info(f"/v1/chat/completions: fallback to longest message text, len={len(contract_text)}")

        if not contract_text:
            raise HTTPException(status_code=400, detail="contract_text is empty")

        logger.info(f"/v1/chat/completions: contract_text_len={len(contract_text)}")
        result = contract_checker.check_contract(contract_text=contract_text, user_prompt=user_prompt)

        # Формируем OpenAI-совместимый ответ
        now_ts = int(__import__("time").time())
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
