import os
import requests
import time
import json
from mylogger import Logger

logger=Logger('LLM GEMINI', 'logs/_llmcall.log')

class GeminiClient:
    def __init__(self, model_name: str = None, api_key: str = None):
        # Получаем значения из переменных окружения, если не переданы явно
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = model_name or os.getenv('MODEL_NAME', 'gemini-2.0-flash')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY не найден в переменных окружения или не передан явно")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        logger.info(f"GeminiClient инициализирован: model={self.model_name}")

    def generate(
        self,
        messages: list,
        max_retries: int = 3,
        delay: int = 600,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        idop: int = 0
    ):
        """
        Вызывает Gemini API с обработкой исключений.
        
        :param messages: Список сообщений в формате OpenAI (будет преобразован в Gemini формат)
        :param max_retries: Максимальное количество попыток
        :param delay: Задержка между попытками (в секундах)
        :param temperature: Параметр температуры для генерации
        :param max_tokens: Максимальное количество токенов в ответе
        :return: Кортеж (ответ, prompt_tokens, completion_tokens) или None
        """
        retries = 0
        
        # Преобразуем сообщения в формат Gemini
        gemini_prompt = self._convert_messages_to_gemini_format(messages)
        
        while retries < max_retries:
            try:
                url = f"{self.base_url}/{self.model_name}:generateContent"
                headers = {
                    'Content-Type': 'application/json',
                    'X-goog-api-key': self.api_key
                }
                
                data = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": gemini_prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens
                    }
                }
                
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Подсчитываем примерные токены (Gemini не возвращает точные значения)
                    prompt_tokens = len(gemini_prompt.split()) * 1.3  # Примерная оценка
                    completion_tokens = len(content.split()) * 1.3
                    
                    if idop != 0:
                        # insert_system_log(idop, "LLM", self.model_name, int(prompt_tokens), int(completion_tokens))
                        pass
                    else:
                        logger.info("Call with NULL idop")
                    
                    return (content, int(prompt_tokens), int(completion_tokens))
                else:
                    logger.error("No candidates in Gemini response")
                    return None
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Error: {e}")
                if retries < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    retries += 1
                    time.sleep(delay)
                else:
                    return None
            
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                return None
        
        logger.error("Max retries reached. Failed to get response.")
        return None

    def _convert_messages_to_gemini_format(self, messages: list) -> str:
        """
        Преобразует сообщения из формата OpenAI в формат Gemini.
        
        :param messages: Список сообщений в формате OpenAI
        :return: Объединенный текст для Gemini
        """
        result = []
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                result.append(f"System: {content}")
            elif role == "user":
                result.append(f"User: {content}")
            elif role == "assistant":
                result.append(f"Assistant: {content}")
            else:
                result.append(content)
        
        return "\n\n".join(result)

    @staticmethod
    def prepare_messages(prompt: str, system_message: str = "") -> list:
        """
        Формирует список сообщений для API (совместимый с OpenAI форматом).
        
        :param prompt: Пользовательский промпт
        :param system_message: Системное сообщение (опционально)
        :return: Список сообщений в формате OpenAI
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        return messages