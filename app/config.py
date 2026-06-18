from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    stt_model: str
    text_model: str
    host: str
    port: int
    database_path: str


settings = Settings(
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
    stt_model=os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo"),
    text_model=os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile"),
    host=os.getenv("HOST", "127.0.0.1"),
    port=int(os.getenv("PORT", "8080")),
    database_path=os.getenv("DATABASE_PATH", "./data/openvox.db"),
)
