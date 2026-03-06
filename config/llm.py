"""
LLM 설정

환경변수 기반으로 Gemini API 설정을 주입합니다.
"""

import os

# Gemini API 설정
LLM_CONFIG = {
    "api_key": os.environ.get("LLM_API_KEY"),
    "model_name": os.environ.get("LLM_MODEL_NAME"),
}
