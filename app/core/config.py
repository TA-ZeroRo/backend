"""Core configuration utilities for the backend app.

Provides a helper to retrieve Supabase credentials from environment
variables and optional .env files.
"""
import os
from typing import Tuple

from dotenv import load_dotenv


def get_supabase_config() -> Tuple[str, str]:
    """Return Supabase URL and KEY from environment.

    Loads a local .env if present. Raises ValueError if missing.
    """
    # Load from .env if available
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment")

    return url, key

