from pydantic_settings import BaseSettings
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the root directory (parent of api_backend)
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / '.env'

# Load .env file from root directory
load_dotenv(dotenv_path=ENV_PATH)

print(f"📂 Loading .env from: {ENV_PATH}")
print(f"✅ .env exists: {ENV_PATH.exists()}")

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = os.getenv('APP_NAME', 'AI Startup Analyzer API')
    VERSION: str = os.getenv('VERSION', '1.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    HF_TOKEN: str = os.getenv('HF_TOKEN', '')
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    GOOGLE_SEARCH_API_KEY: str = os.getenv('GOOGLE_SEARCH_API_KEY', '')
    SEARCH_ENGINE_ID: str = os.getenv('SEARCH_ENGINE_ID', '')
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    # Gmail API Settings
    GMAIL_CLIENT_ID: str = os.getenv('GMAIL_CLIENT_ID', '')
    GMAIL_CLIENT_SECRET: str = os.getenv('GMAIL_CLIENT_SECRET', '')
    GMAIL_REFRESH_TOKEN: str = os.getenv('GMAIL_REFRESH_TOKEN', '')
    
    # File Storage
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')
    DATA_FOLDER: str = os.getenv('DATA_FOLDER', 'data')
    
    class Config:
        env_file = str(ENV_PATH)
        case_sensitive = True

settings = Settings()

# Debug: Print which keys are loaded
print("\n" + "=" * 50)
print("🔑 Environment Variables Status:")
print("=" * 50)
print(f"GEMINI_API_KEY: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Missing'}")
print(f"HF_TOKEN: {'✅ Set' if settings.HF_TOKEN else '❌ Missing'} (Length: {len(settings.HF_TOKEN) if settings.HF_TOKEN else 0})")
print(f"GROQ_API_KEY: {'✅ Set' if settings.GROQ_API_KEY else '❌ Missing'}")
print(f"GOOGLE_SEARCH_API_KEY: {'✅ Set' if settings.GOOGLE_SEARCH_API_KEY else '❌ Missing'}")
print("=" * 50 + "\n")






