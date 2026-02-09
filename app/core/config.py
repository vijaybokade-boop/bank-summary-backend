import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:

    SETU_LOGIN_URL = os.getenv("SETU_LOGIN_URL", "https://orgservice-prod.setu.co/v1/users/login")
    SETU_CONSENT_URL = os.getenv("SETU_CONSENT_URL", "https://fiu-sandbox.setu.co/v2/consents")
    SETU_SESSION_URL = os.getenv("SETU_SESSION_URL", "https://fiu-sandbox.setu.co/v2/sessions")
    # Security Settings
    # Default to localhost for development if not specified
    ALLOWED_IPS = os.getenv("ALLOWED_IPS", "127.0.0.1,::1").split(",")
    
    # APP_CLIENT_SECRET = os.getenv("APP_CLIENT_SECRET","" )
    #redis-url 
    REDIS_URL = os.getenv("REDIS_URL")        

    #idempotency settings
    IDEMPOTENCY_TTL = os.getenv("IDEMPOTENCY_TTL")
    IDEMPOTENCY_LOCK_TTL = os.getenv("IDEMPOTENCY_LOCK_TTL")

settings = Settings()

    
