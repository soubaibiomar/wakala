import os
import requests
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "")
OPENROUTER_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "openrouter/free",
]

def ask_cloud_llm(prompt: str, temperature: float = 0.2) -> Optional[str]:
    """
    Sends a prompt to the configured cloud model for selector generation.
    """
    if not OPENROUTER_API_KEY or not OPENROUTER_MODEL:
        return None
    url = f"{OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
    
    payload = {
        "models": OPENROUTER_MODELS,
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
        logger.error(f"Failed to query cloud model at {url}: {e}")
        return None
