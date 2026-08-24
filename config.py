"""Configuration file for the dating bot"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# AI API Keys (all optional, bot will use fallback chain)
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
    'fa': 'فارسی',  # Farsi
    'en': 'English',
    'sv': 'Svenska',  # Swedish
    'de': 'Deutsch',  # German
    'tr': 'Türkçe',  # Turkish
    'ar': 'العربية',  # Arabic
    'fr': 'Français',  # French
    'es': 'Español',  # Spanish
    'ku': 'کوردی',  # Kurdish
}

DEFAULT_LANGUAGE = 'fa'  # Farsi as default
