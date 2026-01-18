import os
import httpx
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
        
    async def generate(self, messages: List[Dict], temperature: float = 0.2, max_tokens: int = 512) -> str:
        """Generate response using OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(self.base_url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"OpenRouter API failed: {str(e)}")
                await asyncio.sleep(2 ** attempt)

client = OpenRouterClient()