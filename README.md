# 🌹 AI Dating Telegram Bot

A multi-language AI-powered dating bot for Telegram with profile creation, matching, swiping, and an AI dating assistant.

## ✨ Features

### 🌐 Multi-Language Support (9 languages)
- **Farsi** (فارسی) - Default language
- **English**
- **Swedish** (Svenska)
- **German** (Deutsch)
- **Turkish** (Türkçe)
- **Arabic** (العربية)
- **French** (Français)
- **Spanish** (Español)
- **Kurdish** (کوردی)

Language is auto-detected from the user's text or can be manually selected.

### 👤 Profile System
- Name, age, gender, bio, city
- Photo upload
- Looking-for preferences
- Profile editing

### 💕 Matching & Swiping
- Browse profiles based on preferences
- Like/Pass swiping
- Mutual match notifications
- Age range and distance filters

### 🤖 AI Dating Assistant
- Conversation tips
- Date ideas
- Profile improvement suggestions
- Confidence building
- Context-aware (knows user profile)

### 🔄 AI Backend Fallback Chain
1. **HuggingFace** (DialoGPT) - First choice
2. **OpenRouter** (GPT-3.5) - Second choice
3. **Google Gemini** - Third choice

If one fails, it automatically falls back to the next.

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Your Bot Token
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token

### 3. Configure Environment
Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 4. (Optional) Add AI API Keys
For the AI assistant, add at least one:
- `HUGGINGFACE_API_KEY` - from [huggingface.co](https://huggingface.co/settings/tokens)
- `OPENROUTER_API_KEY` - from [openrouter.ai](https://openrouter.ai/keys)
- `GEMINI_API_KEY` - from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5. Run the Bot
```bash
python main.py
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot & create profile |
| `/menu` | Show main menu |
| `/help` | Show help |
| `/cancel` | Cancel current action |

## 🏗️ Project Structure

```
├── main.py              # Bot entry point
├── config.py            # Configuration & settings
├── database.py          # Database models (SQLAlchemy)
├── languages.py         # Translations for 9 languages
├── ai_service.py        # AI backend (HF/OpenRouter/Gemini)
├── handlers/
│   ├── start.py         # /start, language selection, profile creation
│   ├── matching.py      # Browse profiles, swiping, matching
│   ├── chat.py          # AI chat assistant
│   └── settings.py      # User preferences & settings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🗄️ Database

Uses SQLite by default. Tables:
- `users` - User profiles and preferences
- `likes` - Like/pass records
- `matches` - Mutual matches
- `chats` - Chat rooms
- `messages` - Chat messages
- `ai_conversations` - AI assistant history

## 🔒 Privacy Notes
- User data is stored locally in SQLite
- AI conversations can be reviewed/deleted
- No external data sharing
- Users can deactivate their accounts

## 🛠️ Customization

### Change Default Language
Edit `config.py`:
```python
DEFAULT_LANGUAGE = 'en'  # Change from 'fa' to any supported language
```

### Add More Languages
1. Add to `SUPPORTED_LANGUAGES` in `config.py`
2. Add translations in `languages.py`
3. Add AI system prompt in `ai_service.py`

### Change AI Model
Edit `ai_service.py`:
```python
# OpenRouter - change model
"model": "anthropic/claude-3-sonnet"  # or any OpenRouter model

# HuggingFace - change model
"url = .../models/YOUR_MODEL_NAME"
```

## 📝 License
MIT License - feel free to use and modify.
