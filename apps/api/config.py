import math
from typing import Dict

# Ollama settings
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5-coder"
EMBEDDING_MODEL = "bge-m3"

# Qdrant / Vector Engine settings
EMBEDDING_DIMENSION = 1024  # bge-m3 default dimension
HNSW_M = 16
HNSW_EF_CONSTRUCT = 100

# Neo4j / Collaborative Engine settings
W_SAVED = 3
W_CLICKED = 2
W_VIEWED = 1

# Scoring Fusion settings
# Dynamic weight calibration constant (K)
# After ~1000 interactions, W2 = 0.40 -> K = ln(1001) / 0.40 ≈ 17.27
K = 17.27
MAX_W2 = 0.50
MIN_W2 = 0.05
