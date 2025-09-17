import os
import requests
import time
import json
from dotenv import load_dotenv
from mylogger import Logger

# Загружаем переменные окружения из .env файла
load_dotenv()

logger=Logger('LLM OPENROUTER', 'logs/_llmcall.log')

class OpenRouterClient:
    def __init__(self, model_name: str = None, api_key: str = None, site_url: str = None, site_name: str = None):
        # Получаем значения из переменных окружения, если не переданы явно
        self.api_key = api_key or os.getenv('API_KEY')
        self.model_name = model_name or os.getenv('MODEL_NAME', 'openai/gpt-4o')
        self.site_url = site_url or os.getenv('SITE_URL', '')
        self.site_name = site_name or os.getenv('SITE_NAME', '')
        
        if not self.api_key:
            raise ValueError("API_KEY не найден в переменных окружения или не передан явно")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        logger.info(f"OpenRouterClient инициализирован: model={self.model_name}")

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
        Вызывает OpenRouter API с обработкой исключений.
        
        :param messages: Список сообщений в формате OpenAI
        :param max_retries: Максимальное количество попыток
        :param delay: Задержка между попытками (в секундах)
        :param temperature: Параметр температуры для генерации
        :param max_tokens: Максимальное количество токенов в ответе
        :return: Кортеж (ответ, prompt_tokens, completion_tokens) или None
        """
        retries = 0
        
        while retries < max_retries:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Добавляем опциональные заголовки если они указаны
                if self.site_url:
                    headers["Referer"] = self.site_url
                if self.site_name:
                    headers["X-Title"] = self.site_name
                
                data = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                response = requests.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    
                    # Получаем информацию о токенах если доступна
                    usage = result.get('usage', {})
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    
                    if idop != 0:
                        try:
                            # Note: insert_system_log function needs to be implemented or imported
                            # For now, we'll log the information using the existing logger
                            logger.info(f"LLM call - idop: {idop}, model: {self.model_name}, prompt_tokens: {int(prompt_tokens)}, completion_tokens: {int(completion_tokens)}")
                        except Exception as e:
                            logger.error(f"Failed to log system call: {e}")
                    else:
                        logger.info("Call with NULL idop")
                    
                    return (content, prompt_tokens, completion_tokens)
                else:
                    logger.error("No choices in OpenRouter response")
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

    @staticmethod
    def prepare_messages(prompt: str, system_message: str = "") -> list:
        """
        Формирует список сообщений для OpenRouter API (совместимый с OpenAI форматом).
        
        :param prompt: Пользовательский промпт
        :param system_message: Системное сообщение (опционально)
        :return: Список сообщений в формате OpenAI
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        return messages