# 🚀 راهنمای کامل راه‌اندازی - Complete Setup Guide

## ✅ پروژه شما آماده است!

ربات دوستیابی فمینیستی با سیستم RAG HuggingFace و وب‌سایت Cloudflare Pages کاملاً آماده است.

---

## 📦 آنچه ساخته شده:

### 1. ربات تلگرام (Telegram Bot)
- ✅ ۱۳ ویژگی ایمنی فمینیستی
- ✅ دستیار هوش مصنوعی با HuggingFace RAG
- ✅ ۹ زبان با پیش‌فرض فارسی
- ✅ سیستم تطبیق هوشمند
- ✅ محافظت حریم خصوصی

### 2. وب‌سایت Cloudflare Pages
- ✅ صفحه فرود زیبا
- ✅ معرفی ویژگی‌ها
- ✅ نمایش ۱۳ ویژگی ایمنی
- ✅ بخش تحقیقات علمی
- ✅ دکمه‌های تماس با ربات

### 3. سیستم HuggingFace RAG
- ✅ مدل‌های زبانی پیشرفته
- ✅ سیستم بازیابی دانش (RAG)
- ✅ پشتیبانی از ۹ زبان
- ✅ مکانیزم Fallback

---

## 🛠️ مراحل راه‌اندازی:

### مرحله 1: دریافت کلید HuggingFace API

1. به [HuggingFace](https://huggingface.co/settings/tokens) بروید
2. ثبت‌نام کنید (رایگان)
3. روی "New Token" کلیک کنید
4. یک کلید API بسازید (Role: Read)
5. کلید را کپی کنید (شبیه: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### مرحله 2: تنظیم فایل .env

فایل `.env` را باز کنید و کلید HuggingFace را اضافه کنید:

```env
# Telegram Bot Token
BOT_TOKEN=8944962741:AAHJXca_OjSCdciyfW4bfNsQUn_iHmsxKeo

# HuggingFace API Key (اصلی)
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenRouter API Key (پشتیبان - اختیاری)
OPENROUTER_API_KEY=

# Google Gemini API Key (پشتیبان - اختیاری)
GEMINI_API_KEY=

# Database URL
DATABASE_URL=sqlite:///dating_bot.db

# Website URL
WEBSITE_URL=https://feminism-dating.pages.dev

# Default Language
DEFAULT_LANGUAGE=fa
```

### مرحله 3: نصب وابستگی‌های Python

```bash
pip install -r requirements.txt
```

### مرحله 4: اجرای ربات تلگرام

```bash
python main.py
```

یا:
```bash
./start.sh
```

### مرحله 5: استقرار وب‌سایت در Cloudflare Pages

#### روش 1: استفاده از Wrangler CLI (توصیه شده)

1. نصب Wrangler:
```bash
npm install -g wrangler
```

2. ورود به Cloudflare:
```bash
wrangler login
```

3. استقرار:
```bash
wrangler pages deploy cloudflare-site --project-name feminism-dating
```

#### روش 2: استفاده از Cloudflare Dashboard

1. به [Cloudflare Dashboard](https://dash.cloudflare.com) بروید
2. روی "Workers & Pages" کلیک کنید
3. "Create" → "Pages"
4. "Upload assets" را انتخاب کنید
5. پوشه `cloudflare-site` را آپلود کنید
6. نام پروژه: `feminism-dating`
7. روی "Deploy site" کلیک کنید

#### روش 3: استفاده از Git (Continuous Deployment)

1. کد را به GitHub/GitLab/GitPush کنید
2. در Cloudflare، "Connect to Git" را انتخاب کنید
3. Repository خود را انتخاب کنید
4. تنظیمات Build:
   - Build command: (خالی بگذارید)
   - Build output directory: `cloudflare-site`
5. Deploy کنید

### مرحله 6: تنظیم ربات تلگرام

#### تنظیم تصویر پروفایل ربات:

1. در تلگرام به [@BotFather](https://t.me/BotFather) بروید
2. `/mybots` را ارسال کنید
3. ربات خود را انتخاب کنید: `@femenism_ai_dating_bot`
4. روی "Bot Settings" → "Bot Picture" کلیک کنید
5. فایل `safety_logo.png` را ارسال کنید

#### تنظیم توضیحات ربات:

**Description** (قبل از شروع):
```
🌹 اولین ربات دوستیابی با ۱۳ ویژگی ایمنی فمینیستی

🛡️ ایمنی زنان در اولویت
🤖 دستیار هوش مصنوعی
🌍 ۹ زبان پشتیبانی
💕 تطبیق هوشمند

/start برای شروع
```

**About** (اطلاعات ربات):
```
🌹 Feminism AI Dating Bot
🛡️ ۱۳ ویژگی ایمنی فمینیستی
🤖 HuggingFace RAG AI
🌍 ۹ زبان

کانال اخبار: https://t.me/+jUAfCVzrrDgxMzdh
```

**Commands** (دستورات):
```
start - 🌹 شروع و ساخت پروفایل
menu - 🏠 منوی اصلی
safety - 🛡️ ویژگی‌های ایمنی
help - 📖 راهنما
cancel - ❌ لغو
```

### مرحله 7: تنظیم کانال تلگرام

1. کانال خود را باز کنید: https://t.me/+jUAfCVzrrDgxMzdh
2. روی نام کانال کلیک کنید → "Edit"
3. تصویر کانال: `channel_logo.png` را آپلود کنید
4. توضیحات کانال را از `channel_messages.md` کپی کنید

---

## 🧪 تست پروژه:

### تست ربات:

1. در تلگرام به ربات بروید: `@femenism_ai_dating_bot`
2. `/start` را ارسال کنید
3. زبان فارسی را انتخاب کنید
4. پروفایل بسازید
5. روی "🛡️ ایمنی" کلیک کنید
6. ویژگی‌های ایمنی را تست کنید
7. دستیار هوش مصنوعی را تست کنید

### تست وب‌سایت:

1. به آدرس وب‌سایت خود بروید (مثلاً: `https://feminism-dating.pages.dev`)
2. تمام بخش‌ها را بررسی کنید
3. دکمه‌های تلگرام را تست کنید

---

## 🎯 ویژگی‌های کلیدی:

### 13 ویژگی ایمنی:

1. 🤝 **دوست مخفی** - یک نفر مورد اعتماد که همیشه از وضعیت شما مطلع است
2. 👥 **یار ایمنی متقابل** - زنان از یکدیگر محافظت می‌کنند
3. ⏰ **چک‌این خودکار** - بررسی خودکار وضعیت در حین قرار
4. 🆘 **دکمه اضطراری** - هشدار اضطراری با یک کلیک
5. 🔐 **کلمه امن** - کلمه مخفی برای اعلام خطر
6. 📸 **تأیید عکس** - جلوگیری از پروفایل‌های جعلی
7. 🛡️ **حریم خصوصی** - حالت ناشناس، مخفی کردن محل
8. 💬 **آموزش رضایت** - ۵ اصل رضایت
9. 🚫 **مسدود و گزارش** - گزارش فوری رفتار نامناسب
10. ⚠️ **محافظت اخراج جنسی** - آگاهی از Body Scam
11. 📍 **برنامه‌ریزی قرار امن** - برنامه‌ریزی قبل از قرار
12. 🏃 **استراتژی خروج اضطراری** - برنامه خروج از پیش تعیین شده
13. 🏆 **امتیاز ایمنی** - سیستم امتیازدهی رفتار ایمن

### سیستم HuggingFace RAG:

- **مدل اصلی**: Mistral-7B-Instruct-v0.2
- **مدل جایگزین**: Zephyr-7B-beta
- **مدل دوم جایگزین**: DialoGPT-large
- **سیستم RAG**: بازیابی دانش مرتبط برای پاسخ‌های دقیق
- **پشتیبانی ۹ زبان**: فارسی، انگلیسی، سوئدی، آلمانی، ترکی، عربی، فرانسوی، اسپانیایی، کوردی

### وب‌سایت Cloudflare:

- **طراحی مدرن**: RTL (راست به چپ) برای فارسی
- **Responsive**: سازگار با موبایل و دسکتاپ
- **سریع**: استفاده از CDN Cloudflare
- **SEO**: بهینه برای موتورهای جستجو

---

## 📊 ساختار پروژه:

```
/home/user/
├── main.py                      # نقطه شروع ربات
├── config.py                    # تنظیمات
├── database.py                  # مدل‌های دیتابیس
├── languages.py                 # ترجمه‌های ۹ زبان
├── ai_service.py                # سرویس هوش مصنوعی
├── huggingface_rag.py          # سیستم RAG HuggingFace
├── handlers/
│   ├── start.py                # /start و ساخت پروفایل
│   ├── matching.py             # مرور و تطبیق
│   ├── chat.py                 # چت با AI
│   ├── settings.py             # تنظیمات
│   └── safety.py               # ۱۳ ویژگی ایمنی
├── cloudflare-site/
│   └── index.html              # وب‌سایت Cloudflare Pages
├── images/
│   ├── bot_logo.png            # تصویر ربات
│   ├── channel_logo.png        # تصویر کانال
│   ├── welcome_banner.png      # بنر خوش‌آمد
│   ├── safety_logo.png         # لوگوی ایمنی
│   └── safety_banner.png       # بنر ایمنی
├── requirements.txt             # وابستگی‌های Python
├── wrangler.toml               # تنظیمات Cloudflare
├── package.json                # برای استقرار Cloudflare
├── .env                        # تنظیمات محیط (کلیدها)
├── .env.example                # نمونه فایل .env
├── start.sh                    # اسکریپت شروع سریع
├── SAFETY_SYSTEM.md            # مستندات کامل ایمنی
├── PROJECT_SUMMARY.md          # خلاصه پروژه
└── COMPLETE_SETUP.md           # این فایل
```

---

## 🔧 عیب‌یابی:

### ربات کار نمی‌کند:

1. **خطای Token**:
   - بررسی کنید `BOT_TOKEN` در `.env` صحیح است
   - از [@BotFather](https://t.me/BotFather) کلید جدید بگیرید

2. **خطای HuggingFace**:
   - بررسی کنید `HUGGINGFACE_API_KEY` صحیح است
   - به [HuggingFace](https://huggingface.co/settings/tokens) بروید
   - کلید را دوباره بسازید

3. **خطای دیتابیس**:
   ```bash
   rm dating_bot.db
   python main.py
   ```

### وب‌سایت کار نمی‌کند:

1. **Cloudflare Pages**:
   - بررسی کنید فایل‌ها در پوشه `cloudflare-site` هستند
   - دوباره استقرار کنید: `wrangler pages deploy cloudflare-site`

2. **خطای Wrangler**:
   ```bash
   wrangler login
   wrangler whoami
   ```

---

## 🚀 گام‌های بعدی:

### برای بهبود پروژه:

1. **افزودن مدل‌های بیشتر**:
   - مدل‌های اختصاصی برای فارسی
   - مدل‌های تصویری برای تأیید عکس

2. **افزودن ویژگی‌های جدید**:
   - چت صوتی
   - تماس ویدیویی
   - بازی‌های تعاملی

3. **بهبود ایمنی**:
   - تشخیص خودکار رفتار نامناسب
   - سیستم احراز هویت دو مرحله‌ای
   - رمزنگاری پیام‌ها

### برای گسترش:

1. **اپلیکیشن موبایل**:
   - React Native
   - Flutter

2. **وب‌سایت کامل**:
   - سیستم ورود
   - پروفایل‌های پیشرفته
   - چت مستقیم

3. **هوش مصنوعی پیشرفته**:
   - مدل‌های اختصاصی
   - یادگیری تقویتی
   - تحلیل احساسات

---

## 📞 پشتیبانی:

### منابع:

- **ربات تلگرام**: [@femenism_ai_dating_bot](https://t.me/femenism_ai_dating_bot)
- **کانال اخبار**: [https://t.me/+jUAfCVzrrDgxMzdh](https://t.me/+jUAfCVzrrDgxMzdh)
- **وب‌سایت**: [https://feminism-dating.pages.dev](https://feminism-dating.pages.dev)

### مستندات:

- `SAFETY_SYSTEM.md` - مستندات کامل سیستم ایمنی
- `PROJECT_SUMMARY.md` - خلاصه پروژه
- `README.md` - راهنمای اصلی

---

## 🎉 تبریک!

پروژه شما کاملاً آماده است:

✅ ربات تلگرام با ۱۳ ویژگی ایمنی
✅ سیستم HuggingFace RAG
✅ وب‌سایت Cloudflare Pages
✅ ۹ زبان با پیش‌فرض فارسی
✅ مستندات کامل

**فقط کافی است:**

1. کلید HuggingFace را در `.env` اضافه کنید
2. `python main.py` را اجرا کنید
3. وب‌سایت را در Cloudflare استقرار دهید

**موفق باشید!** 🌹💕🛡️
