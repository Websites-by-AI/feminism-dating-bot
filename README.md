# 🌹 Feminism AI Dating & Safety Platform

**Multilingual Feminist AI Dating Platform, 13-Layer Safety Center, Academic RAG Coach & Telegram Bot** — inspired by Bumble, HER, Hinge, and UN Women digital safety research.

---

## 🌐 Live Deployments

| Platform | Live URL | Role |
|----------|----------|------|
| **Cloudflare Pages (Web Platform)** | [https://feminism-dating-bot.pages.dev](https://feminism-dating-bot.pages.dev) | Trilingual Web Platform (`FA` / `EN` / `TR`), AI Studio (`app.html`), 13 Safety Tools (`safety.html`), User Dashboard, 10 Education Modules, Admin Panel |
| **HuggingFace Space** | [https://huggingface.co/spaces/Sosa654321/feminism-dating-bot](https://huggingface.co/spaces/Sosa654321/feminism-dating-bot) | Interactive Static Space (`https://sosa654321-feminism-dating-bot.hf.space`) — 24/7 `RUNNING` |
| **Cloudflare Edge RAG API & Webhook** | [https://feminism-dating-api.elasa2next.workers.dev/api/health](https://feminism-dating-api.elasa2next.workers.dev/api/health) | Serverless REST API (`KV` persistence + Cloudflare Workers AI `@cf/mistralai/mistral-small-3.1-24b-instruct` + `/webhook/telegram`) |
| **GitHub Repository** | [https://github.com/Websites-by-AI/feminism-dating-bot](https://github.com/Websites-by-AI/feminism-dating-bot) | Full Source Code (`cloudflare-site/`, `cloudflare-worker/`, and Python Telegram Bot) |

---

## ✨ Key Features

### 🛡️ 13 Research-Backed Feminist Safety Features
Grounded in peer-reviewed literature (*Gillett 2023*, *Amirkhani et al. 2024*, *Bicharanlou 2017*, *Thompson 2018*, *ACM CSCW 2024*):
1. **Secret Friend System** — Share date plans and live safety alerts with a trusted contact
2. **Mutual Safety Buddy** — Women-helping-women community check-ins
3. **Auto Check-In Timer** — 30-minute date countdown with automated SOS escalation
4. **One-Tap SOS Button** — Instant emergency logging & trusted contact alert
5. **Silent Safe Word** — Everyday phrase that covertly triggers SOS in chat
6. **Photo Verification** — Anti-catfish verification badge
7. **Privacy Controls** — Anonymous mode, city-only location, photo blur until mutual trust
8. **FRIES Consent Quiz** — Interactive *Freely given, Reversible, Informed, Enthusiastic, Specific* consent module
9. **Hidden Words Filter** — Hinge-style pre-emptive harassment & spam word blocker
10. **Anti-Sextortion / Body-Scam Shield** — Automatic protection against intimate image coercion
11. **Public Date Safety Planner** — First-date public venue checklist
12. **Emergency Exit Protocol** — Independent transport & exit call scripts
13. **Screenshot & Copy Protection** — Deterrence and boundary warnings

### 🎯 10 Specialized Relationship Modes
- 🚀 **Startup Co-founder Partner (`startup`)** — Compatibility quiz on equity/vesting, work-love boundaries, and anti-exploitation red flags
- 🌍 **International & Cross-Cultural (`abroad`)** — Long-distance communication rhythm, legal/financial autonomy, and romance-scam protection
- 💍 **Serious Relationship (`serious`)** · 💒 **Egalitarian Marriage (`marriage`)** · 🧠 **Intellectual (`intellectual`)** · 💝 **Emotional (`emotional`)** · 🌸 **Casual (`casual`)** · 👥 **Friendship (`friendship`)** · 🌈 **Ethical Open (`open`)** · 🔥 **Safe Short-Term (`one_night`)**

### 🧠 Psychology & Academic RAG AI Coach (9 Languages)
- **MBTI + Primary Love Language + Attachment Style** assessment with tailored AI compatibility insights
- **9 Supported Languages**: Farsi (`fa`), English (`en`), Turkish (`tr`), Swedish (`sv`), German (`de`), Arabic (`ar`), French (`fr`), Spanish (`es`), Kurdish (`ku`)
- **Multi-Tier RAG Engine**: Cloudflare Workers AI (`Mistral-Small-3.1-24B` & `Llama-3.3-70B`) → HuggingFace Inference Router (`v1/chat/completions`) → OpenRouter → Gemini → Local Academic Knowledge Synthesis

---

## 🏗️ Repository Structure

```text
feminism-dating-bot/
├── cloudflare-site/           # Complete 26-file Web Platform (Cloudflare Pages & HF Space)
│   ├── index.html             # Persian landing page (Bumble/HER inspired)
│   ├── en.html / tr.html      # English & Turkish landing pages
│   ├── app.html               # Interactive AI RAG Coach, 10 Modes Quiz, MBTI & Discovery
│   ├── safety.html            # Interactive 13 Feminist Safety Features & SOS Center
│   ├── login.html / register.html / dashboard.html / unified-dashboard.html
│   ├── admin.html             # Live Cloud Analytics, User Search & 1-Click Telegram Webhook
│   ├── education.html         # Feminist Relationship Academy + 10 edu-*.html modules
│   └── js/auth.js             # Cloud KV Auth + Offline localStorage Fallback
├── cloudflare-worker/         # Serverless Backend API + Serverless Telegram Bot Webhook
│   ├── worker.js              # Cloudflare Worker (Workers AI + KV bindings)
│   └── wrangler.toml          # Worker configuration
├── handlers/                  # Python Telegram Bot handlers (start, safety, personality, modes...)
├── main.py                    # Python Telegram Bot entry point (polling mode)
├── database.py                # 24 SQLAlchemy 2.0 models (Users, Safety, Modes, RAG KB)
├── huggingface_rag.py         # Academic RAG retrieval + Edge AI / HF Router client
├── ai_service.py              # Multi-backend conversational AI service
├── initialize_knowledge_base.py
└── requirements.txt
```

---

## 🚀 Running the Telegram Bot (2 Options)

### Option A: Zero-Server Cloud Webhook (Recommended — 24/7 Free on Cloudflare)
1. Create a bot via [@BotFather](https://t.me/BotFather) and copy your token.
2. Open [`/admin.html`](https://feminism-dating-bot.pages.dev/admin.html) (Admin login: `admin@feminism-dating.com` / `Admin@123456`).
3. Paste your `@BotFather` token in **Serverless Telegram Bot Webhook** and click **Connect**. Your bot runs 24/7 on Cloudflare's edge with KV state and Workers AI!

### Option B: Local / VPS Python Polling Bot
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set BOT_TOKEN=<your_telegram_bot_token>
python initialize_knowledge_base.py
python main.py
```
