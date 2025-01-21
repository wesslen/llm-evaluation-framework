"""LLM client for making API calls to language models."""

import json
from typing import Dict, Any, Optional, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings

class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self):
        """Initialize the LLM client with configuration."""
        self.base_url = str(settings.api_base_url)
        self.api_key = settings.api_key.get_secret_value()
        self.model_name = settings.model_name  # Changed from llm_model_name
        
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=settings.retry_delay)
    )
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text from the LLM using chat completions.
        
        Args:
            prompt: Input text to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-2)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict containing the model response and metadata
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant for evaluating LLM capabilities."},
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=settings.test_timeout
            )
            response.raise_for_status()
            
            # Convert chat completion format to match test expectations
            raw_response = response.json()
            return {
                "choices": [{
                    "text": raw_response["choices"][0]["message"]["content"],
                    "finish_reason": raw_response["choices"][0]["finish_reason"]
                }],
                "model": raw_response["model"],
                "usage": raw_response.get("usage", {}),
                "response_ms": raw_response.get("response_ms")
            }
    
    async def get_embedding(self, text: str) -> Dict[str, Any]:
        """
        Get embeddings for the input text.
        
        Args:
            text: Input text to get embeddings for
            
        Returns:
            Dict containing the embeddings and metadata
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": f"{self.model_name}-embedding",  # Assume embedding model variant
            "input": text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/embeddings",
                headers=headers,
                json=payload,
                timeout=settings.test_timeout
            )
            response.raise_for_status()
            return response.json()
            
    async def analyze_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a model response for various metrics.
        
        Args:
            response: Raw model response dictionary
            
        Returns:
            Dict containing computed metrics
        """
        metrics = {
            "tokens_generated": len(response.get("choices", [{}])[0].get("text", "").split()),
            "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
            "latency_ms": response.get("response_ms", 0),
            "model_version": response.get("model", self.model_name),
            "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
            "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
            "total_tokens": response.get("usage", {}).get("total_tokens", 0)
        }
        
        return metrics