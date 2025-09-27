"""
title: OpenRouter Manifold Pipeline
author: open-webui
date: 2024-09-23
version: 1.0
license: MIT
description: A manifold pipeline for OpenRouter API integration
requirements: requests, pydantic
"""

from typing import List, Union, Generator, Iterator
import os
import requests
from pydantic import BaseModel
import sys

# Добавляем путь для импорта логгера
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from mylogger import Logger

# Настройка логирования
logger = Logger('OPENROUTER_ADAPTER', 'logs/openrouter_adapter.log')


class Pipeline:
    class Valves(BaseModel):
        OPENROUTER_API_KEY: str
        OPENROUTER_BASE_URL: str

    def __init__(self):
        # Set this as a manifold pipeline to handle multiple models
        self.type = "manifold"
        
        # Pipeline name that will appear in the UI
        self.name = "OpenRouter: "
        
        # Initialize valves with environment variables
        self.valves = self.Valves(
            **{
                "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
                "OPENROUTER_BASE_URL": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            }
        )
        
        # Will be populated with available models
        self.pipelines = []

    async def on_startup(self):
        """Called when the server starts"""
        logger.info(f"on_startup: {__name__}")
        self.pipelines = self.get_openrouter_models()

    async def on_shutdown(self):
        """Called when the server stops"""
        logger.info(f"on_shutdown: {__name__}")

    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info(f"on_valves_updated: {__name__}")
        self.pipelines = self.get_openrouter_models()

    def get_openrouter_models(self):
        """Fetch available models from OpenRouter API"""
        if not self.valves.OPENROUTER_API_KEY:
            return [
                {
                    "id": "error",
                    "name": "OpenRouter API Key not set. Please configure it in the valves.",
                }
            ]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.valves.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.valves.OPENROUTER_BASE_URL}/models",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            models_data = response.json()
            models = []
            
            # Extract models from the response
            if "data" in models_data:
                for model in models_data["data"]:
                    models.append({
                        "id": model["id"],
                        "name": model.get("name", model["id"])
                    })
            
            return models if models else [
                {
                    "id": "openrouter/anthropic/claude-3.5-sonnet",
                    "name": "Claude 3.5 Sonnet"
                },
                {
                    "id": "openrouter/openai/gpt-4o",
                    "name": "GPT-4o"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error fetching OpenRouter models: {e}")
            return [
                {
                    "id": "error",
                    "name": f"Could not fetch models from OpenRouter: {str(e)}",
                }
            ]

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """Main pipeline function that processes requests"""
        
        # Log user information if available
        if "user" in body:
            logger.info("######################################")
            logger.info(f'# User: {body["user"]["name"]} ({body["user"]["id"]})')
            logger.info(f"# Model: {model_id}")
            logger.info(f"# Message: {user_message}")
            logger.info("######################################")

        # Check if API key is configured
        if not self.valves.OPENROUTER_API_KEY:
            return "Error: OpenRouter API Key not configured. Please set it in the pipeline valves."

        try:
            headers = {
                "Authorization": f"Bearer {self.valves.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://open-webui.com",
                "X-Title": "Open WebUI"
            }

            # Prepare the request body
            request_body = {
                **body,
                "model": model_id,
                "messages": messages
            }

            # Make request to OpenRouter
            response = requests.post(
                url=f"{self.valves.OPENROUTER_BASE_URL}/chat/completions",
                json=request_body,
                headers=headers,
                stream=body.get("stream", False),
                timeout=120
            )

            response.raise_for_status()

            # Handle streaming vs non-streaming responses
            if body.get("stream", False):
                return response.iter_lines()
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            error_msg = f"OpenRouter API Error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Pipeline Error: {str(e)}"
            logger.error(error_msg)
            return error_msg