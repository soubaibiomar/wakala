import os
import requests
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
OLLAMA_MODEL_CODE = os.getenv("OLLAMA_MODEL_CODE", "qwen2.5-coder:7b")

def ask_ollama(prompt: str, temperature: float = 0.2) -> Optional[str]:
    """
    Sends a prompt to the Ollama model (specifically qwen2.5-coder:7b)
    to ask for code/selector generation.
    """
    url = f"{OLLAMA_BASE_URL}/chat/completions"
    
    payload = {
        "model": OLLAMA_MODEL_CODE,
        "messages": [
            {"role": "system", "content": "You are an expert data engineer and web scraping specialist. Your task is to output ONLY a valid CSS selector string or JSON object. Do not include markdown formatting or explanations."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip().strip('`').strip()
    except Exception as e:
        logger.error(f"Failed to query Ollama at {url}: {e}")
        return None
