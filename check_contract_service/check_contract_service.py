"""
Сервис проверки договоров check_contract
Получает текст договора, категоризирует его и проверяет на соответствие требованиям
"""

import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

class ContractRequest(BaseModel):
    contract_text: str
    user_prompt: str = ""

class ContractResponse(BaseModel):
    category: str
    validation_result: str
    is_valid: bool

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
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="LLM API error")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail="Request failed")

class ContractChecker:
    """Основной класс для проверки договоров"""
    
    def __init__(self):
        self.llm_client = LLMClient(LLM_API_URL, LLM_API_KEY, LLM_MODEL)
        self.prompts = self._load_prompts()
        self.category_mapping = self._build_category_mapping()
    
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
    
    def _build_category_mapping(self) -> Dict[str, str]:
        """Создает маппинг отображаемых имен на ключи JSON"""
        mapping = {}
        categories = self.prompts.get("categories", {})
        
        for json_key, category_data in categories.items():
            if isinstance(category_data, dict) and "display_name" in category_data:
                display_name = category_data["display_name"]
                mapping[display_name.lower()] = json_key
            elif isinstance(category_data, str):
                # Если категория - просто строка, используем её как отображаемое имя
                mapping[category_data.lower()] = json_key
        
        logger.info(f"Создан маппинг категорий: {len(mapping)} элементов")
        return mapping
    
    def categorize_contract(self, contract_text: str) -> str:
        """Определяет категорию договора"""
        try:
            # Проверяем наличие категорий
            if not self.prompts.get("categories"):
                logger.error("No categories found in prompts")
                return None
            
            categories = list(self.prompts["categories"].keys())
            
            # Создаём промт для категоризации на основе загруженных категорий
            categories_data = self.prompts.get("categories", {})
            categories_list = ", ".join([
                item.get("display_name", item) if isinstance(item, dict) else item
                for item in categories_data.values()
                if item  # Фильтруем пустые значения
            ])
            
            # Fallback если JSON поврежден или пуст
            if not categories_list:
                logger.warning("Не удалось извлечь категории из JSON, используем пустой список")
                categories_list = ""
            
            prompt = f"""Определи категорию договора из следующего списка: {categories_list}

Текст договора: {contract_text}

Ответь ТОЛЬКО названием категории из списка выше и так, как в списке выше - с сохранением орфографии и регистра."""
            
            response = self.llm_client.generate_response(prompt)
            
            # Ищем совпадение с предварительно созданным маппингом
            response_clean = response.strip().lower()
            if response_clean in self.category_mapping:
                json_key = self.category_mapping[response_clean]
                if json_key in categories:
                    logger.info(f"Определена категория: {json_key}")
                    return json_key
            
            # Если категория не найдена в маппинге - возвращаем None
            logger.warning(f"Category not found in mapping: {response}")
            return None
            
        except Exception as e:
            logger.error(f"Error in categorization: {e}")
            return None
    
    def validate_contract(self, contract_text: str, category: str) -> str:
        """Проверяет договор на соответствие требованиям"""
        try:
            if category not in self.prompts.get("categories", {}):
                raise ValueError(f"Unknown category: {category}")
            
            validation_prompt = self.prompts["categories"][category]["validation_prompt"]
            prompt = validation_prompt.format(contract_text=contract_text)
            
            return self.llm_client.generate_response(prompt)
            
        except Exception as e:
            logger.error(f"Error in validation: {e}")
            return f"Ошибка при проверке договора: {str(e)}"
    
    def check_contract(self, contract_text: str, user_prompt: str = "") -> ContractResponse:
        """Основной метод проверки договора"""
        try:
            logger.info("Начинаем проверку договора")
            
            # 1. Категоризация
            category = self.categorize_contract(contract_text)
            
            # Если категория не найдена в JSON - возвращаем сообщение о неподдерживаемом типе
            if category is None:
                logger.info("Категория не найдена в поддерживаемых типах")
                return ContractResponse(
                    category="unsupported",
                    validation_result="Ваш тип договора на данный момент не поддерживается",
                    is_valid=False
                )
            
            logger.info(f"Определена категория: {category}")
            
            # 2. Валидация для найденной категории
            validation_result = self.validate_contract(contract_text, category)
            logger.info("Валидация завершена")
            
            # 3. Определяем, валиден ли договор (простая эвристика)
            is_valid = "нарушений" not in validation_result.lower() and "ошибок" not in validation_result.lower()
            
            return ContractResponse(
                category=category,
                validation_result=validation_result,
                is_valid=is_valid
            )
            
        except Exception as e:
            logger.error(f"Error in check_contract: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Инициализация
contract_checker = ContractChecker()

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "check_contract"}

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

@app.get("/categories")
async def get_categories():
    """Возвращает доступные категории договоров"""
    return {"categories": list(contract_checker.prompts.get("categories", {}).keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
