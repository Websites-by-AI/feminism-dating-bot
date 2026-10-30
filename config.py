"""Configuration file for the Feminism AI Dating Bot"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Cloud Edge RAG API (Cloudflare Workers AI + KV)
CLOUDFLARE_API_URL = os.getenv(
    'CLOUDFLARE_API_URL',
    'https://feminism-dating-api.elasa2next.workers.dev'
)
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID', '')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN', '')

# AI API Keys (optional — fallback chain: Cloudflare Workers AI -> HuggingFace Router -> OpenRouter -> Gemini)
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
HUGGINGFACE_API_KEY_2 = os.getenv('HUGGINGFACE_API_KEY_2', '')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dating_bot.db')

# Bot Settings
MAX_BIO_LENGTH = 500
MAX_AGE = 100
MIN_AGE = 18
PHOTO_REQUIRED = False

# Supported Languages
SUPPORTED_LANGUAGES = {
    'fa': 'فارسی',
    'en': 'English',
    'sv': 'Svenska',
    'de': 'Deutsch',
    'tr': 'Türkçe',
    'ar': 'العربية',
    'fr': 'Français',
    'es': 'Español',
    'ku': 'کوردی',
}

DEFAULT_LANGUAGE = 'fa'
