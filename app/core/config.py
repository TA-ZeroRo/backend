from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Optional

# .env 파일 경로 명시적으로 지정
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_gemini_api_key() -> str:
    """Gemini API key를 반환합니다."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
    return GEMINI_API_KEY

def get_supabase_config() -> tuple[str, str]:
    """Supabase 설정을 반환합니다."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")
    return SUPABASE_URL, SUPABASE_KEY