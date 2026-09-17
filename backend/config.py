import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_FAST_MODEL: str = "groq/compound-mini"
    GROQ_SMART_MODEL: str = "openai/gpt-oss-120b"
    GROQ_FALLBACK: str = "openai/gpt-oss-20b"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

settings = Settings()
