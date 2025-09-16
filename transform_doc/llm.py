#https://api.mistral.ai/v1/chat/completions
import openai
import time
from openai import RateLimitError, APIError, OpenAIError
from utils.db_postgres import insert_system_log

from utils.mylogger import Logger
logger=Logger('LLM OPENAI', 'logs/_llmcall.log')

class OpenAIClient:
    def __init__(self, model_name: str, api_key: str, base_url: str):
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model_name = model_name

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
        Вызывает OpenAI API с обработкой исключений.
        
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
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                if idop!=0:
                    insert_system_log(idop, "LLM", self.model_name, response.usage.prompt_tokens , response.usage.completion_tokens)
                else:
                    logger.info("Call wtih NULL idop")
                return (
                    response.choices[0].message.content,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
            
            except RateLimitError as e:
                logger.info(f"Rate limit exceeded. Retrying in {delay} seconds...")
                retries += 1
                time.sleep(delay)
            
            except (APIError, OpenAIError) as e:
                logger.error(f"API Error: {e}")
                return None
            
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                return None
        
        print("Max retries reached. Failed to get response.")
        return None

    @staticmethod
    def prepare_messages(prompt: str, system_message: str = "") -> list:
        """
        Формирует список сообщений для OpenAI API.
        
        :param prompt: Пользовательский промпт
        :param system_message: Системное сообщение (опционально)
        :return: Список сообщений в формате OpenAI
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        return messages