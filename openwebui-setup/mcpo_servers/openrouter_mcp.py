#!/usr/bin/env python3
"""
OpenRouter MCP Server
Provides tools for interacting with OpenRouter API
"""

import asyncio
import json
import os
import sys

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

# Server configuration
SERVER_NAME = "openrouter-mcp-server"
SERVER_VERSION = "1.0.0"

class OpenRouterMCPServer:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            print("Warning: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)

    async def query_openrouter(
        self, 
        prompt: str, 
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> dict:
        """Query OpenRouter API with the given prompt and model"""
        
        if not self.api_key:
            return {"error": "OpenRouter API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://open-webui.com",
            "X-Title": "Open WebUI MCP Server"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def get_available_models(self) -> dict:
        """Get list of available models from OpenRouter"""
        
        if not self.api_key:
            return {"error": "OpenRouter API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

# Create server instance
openrouter_server = OpenRouterMCPServer()

# Create MCP server
server = Server(SERVER_NAME)

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="query_openrouter",
            description="Query OpenRouter API with a prompt and model",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to send to the model"
                    },
                    "model": {
                        "type": "string",
                        "description": "The model to use (default: anthropic/claude-3.5-sonnet)",
                        "default": "anthropic/claude-3.5-sonnet"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to generate (default: 1000)",
                        "default": 1000
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for generation (default: 0.7)",
                        "default": 0.7
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="get_available_models",
            description="Get list of available models from OpenRouter",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "query_openrouter":
        prompt = arguments.get("prompt")
        model = arguments.get("model", "anthropic/claude-3.5-sonnet")
        max_tokens = arguments.get("max_tokens", 1000)
        temperature = arguments.get("temperature", 0.7)
        
        if not prompt:
            return [TextContent(type="text", text="Error: prompt is required")]
        
        result = await openrouter_server.query_openrouter(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_available_models":
        result = await openrouter_server.get_available_models()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

async def main():
    """Main entry point"""
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())