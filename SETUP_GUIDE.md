# 🚀 Setup Guide - AI Dating Bot

## ✅ Step 1: Bot Profile Picture (Logo)

To set the bot's profile picture:

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/mybots`
3. Select your bot: `@femenism_ai_dating_bot`
4. Click **Bot Settings** → **Bot Picture**
5. Send the file: `bot_logo.png`

✅ Done! Your bot now has a beautiful profile picture.

---

## ✅ Step 2: Bot Description

In BotFather, for your bot set:

### Description (shown before starting):
```
🌹 AI-Powered Dating Bot
💕 Smart matching with AI assistant
🌍 9 languages: Farsi, English, Swedish, German, Turkish, Arabic, French, Spanish, Kurdish
🤖 Get dating advice from AI
👤 Create profile, swipe, match, and chat!

/start to begin
```

### About (shown in bot info):
```
🌹 Feminism AI Dating Bot
🤖 AI-powered matching & dating assistant
🌐 9 languages supported
💕 Swipe, match, chat with AI help

News Channel: https://t.me/+jUAfCVzrrDgxMzdh
```

### Commands list (set via /setcommands):
```
start - 🌹 Start the bot & create profile
menu - 🏠 Show main menu
help - 📖 Help & guide
cancel - ❌ Cancel current action
```

---

## ✅ Step 3: Channel Setup

Your news channel: https://t.me/+jUAfCVzrrDgxMzdh (Farsi language)

To set the channel logo:
1. Open the channel
2. Click the channel name → **Edit**
3. Click the camera icon on the profile picture
4. Send: `channel_logo.png`

Set channel description:
```
🌹 کانال خبری ربات دوستیابی هوش مصنوعی

📢 آخرین اخبار و به‌روزرسانی‌ها
💡 نکات دوستیابی
🤖 ویژگی‌های جدید ربات
🌐 ۹ زبان: فارسی، انگلیسی، سوئدی، آلمانی، ترکی، عربی، فرانسوی، اسپانیایی، کوردی

🤖 ربات: @femenism_ai_dating_bot
```

---

## ✅ Step 4: Run the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Start the bot
python main.py
```

Or use the quick start:
```bash
./start.sh
```

---

## ✅ Step 5: Test the Bot

1. Open Telegram
2. Go to: https://t.me/femenism_ai_dating_bot
3. Press **Start**
4. You should see the welcome banner
5. Select your language
6. Create a profile
7. Test browsing profiles
8. Test AI chat

---

## 📁 Image Files Created

| File | Purpose |
|------|---------|
| `bot_logo.png` | Bot profile picture |
| `channel_logo.png` | News channel profile picture |
| `welcome_banner.png` | Shown when new users start the bot |

---

## 🔧 Bot Configuration (config.py)

Current settings:
- **Default Language**: Farsi (fa)
- **Min Age**: 18
- **Max Age**: 100
- **Max Bio Length**: 500 characters
- **Database**: SQLite (dating_bot.db)

---

## 🎯 Next Steps

1. ✅ Set bot token (DONE)
2. ⬜ Set bot profile picture via BotFather
3. ⬜ Set bot description via BotFather
4. ⬜ Set bot commands via BotFather
5. ⬜ Set channel profile picture
6. ⬜ Install Python dependencies
7. ⬜ Run the bot
8. ⬜ Post first message in channel
9. ⬜ Test the bot
10. ⬜ Promote! 🚀

---

## 💡 Tips

- The bot auto-detects language from user messages
- Default is Farsi if detection fails
- AI features need at least one API key (HuggingFace, OpenRouter, or Gemini)
- SQLite database is created automatically on first run
- Users can change language anytime in Settings
