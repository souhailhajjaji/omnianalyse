import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "omnianalyse-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

settings = Settings()