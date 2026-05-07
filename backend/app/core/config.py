import os
from pathlib import Path

# Load .env file from backend root
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "omnianalyse-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

settings = Settings()