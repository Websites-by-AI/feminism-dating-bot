"""
Mode-Specific Relationship Coaching (Supports All 10 Modes incl. Startup & International)
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session, User, RelationshipPreferences
from ai_service import ai_service
from handlers.relationship_modes import get_mode_info

MODE_COACHING_TOPICS = {
    'startup': {
        'fa': [
            ('📝 قرارداد هم‌بنیان‌گذاری و سهام', 'equity_vesting'),
            ('⚖️ مرز رابطه عاطفی و کاری', 'work_love_boundary'),
            ('🚩 نشانه‌های خطر سوءاستفاده کاری', 'startup_red_flags'),
            ('🤝 حل تعارض استارتاپی بدون آسیب به رابطه', 'founder_conflict'),
        ],
        'en': [
            ('📝 Co-founder Equity & Vesting', 'equity_vesting'),
            ('⚖️ Work vs. Relationship Boundaries', 'work_love_boundary'),
            ('🚩 Sweat-Equity Red Flags', 'startup_red_flags'),
            ('🤝 Healthy Founder Conflict Resolution', 'founder_conflict'),
        ],
    },
    'abroad': {
        'fa': [
            ('🌍 ریتم ارتباط سالم از راه دور', 'ldr_rhythm'),
            ('🛂 واقع‌بینی درباره ویزا و مهاجرت مستقل', 'visa_autonomy'),
            ('🛡️ پیشگیری از کلاهبرداری عاطفی بین‌المللی', 'intl_scam_safety'),
            ('✈️ پروتکل ایمنی اولین ملاقات حضوری در سفر', 'travel_meet_safety'),
        ],
        'en': [
            ('🌍 Healthy Long-Distance Rhythm', 'ldr_rhythm'),
            ('🛂 Visa & Legal Autonomy Abroad', 'visa_autonomy'),
            ('🛡️ Cross-Border Scam Protection', 'intl_scam_safety'),
            ('✈️ Safe First In-Person Travel Protocol', 'travel_meet_safety'),
        ],
    },
    'serious': {
        'fa': [
            ('🎯 ارزیابی سازگاری ارزش‌ها', 'compatibility'),
            ('💬 سوالات عمیق شناخت متقابل', 'deep_questions'),
            ('🚩 تشخیص نشانه‌های خطر اولیه', 'red_flags'),
            ('💍 زمان‌بندی سالم پیشرفت رابطه', 'timeline'),
        ],
        'en': [
            ('🎯 Assessing Core Values', 'compatibility'),
            ('💬 Deep Compatibility Questions', 'deep_questions'),
            ('🚩 Spotting Early Red Flags', 'red_flags'),
            ('💍 Healthy Relationship Pacing', 'timeline'),
        ],
    },
}

DEFAULT_TOPICS = {
    'fa': [
        ('🛡️ چک‌لیست ایمنی و حریم شخصی', 'safety_first'),
        ('💬 بیان محترمانه مرزها و رضایت FRIES', 'fries_boundaries'),
        ('🚩 تشخیص نشانه‌های کنترل‌گری', 'red_flags'),
        ('✨ شروع گفتگوی جذاب و محترمانه', 'opening_moves'),
    ],
    'en': [
        ('🛡️ Personal Safety & Privacy Checklist', 'safety_first'),
        ('💬 Communicating FRIES Consent & Boundaries', 'fries_boundaries'),
        ('🚩 Spotting Controlling Red Flags', 'red_flags'),
        ('✨ Respectful Opening Moves', 'opening_moves'),
    ],
}


async def show_mode_coaching(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI coaching topics tailored to the user's active relationship mode"""
    query = update.callback_query
    if query:
        await query.answer()

    db = get_session()
    try:
        tg_user = update.effective_user
        user = db.query(User).filter_by(telegram_id=tg_user.id).first()
        if not user:
            user = User(telegram_id=tg_user.id, username=tg_user.username, name=tg_user.first_name or 'User', language='fa')
            db.add(user)
            db.commit()

        lang = user.language or 'fa'
        t_lang = 'fa' if lang == 'fa' else 'en'
        rel_prefs = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
        mode = (rel_prefs.relationship_mode if rel_prefs and rel_prefs.relationship_mode else 'startup')

        mi = get_mode_info(mode, lang)
        topics = MODE_COACHING_TOPICS.get(mode, DEFAULT_TOPICS)[t_lang]

        if lang == 'fa':
            text = (
                f"🎓 مربی هوشمند رابطه — حالت {mi['emoji']} {mi['name']}\n\n"
                f"یکی از موضوعات تخصصی زیر را انتخاب کنید تا راهنمای مبتنی بر پژوهش دریافت کنید:"
            )
        else:
            text = (
                f"🎓 AI Relationship Coach — {mi['emoji']} {mi['name']}\n\n"
                f"Choose a specialized topic for research-backed guidance:"
            )

        keyboard = [
            [InlineKeyboardButton(label, callback_data=f"coaching_{mode}_{topic_key}")]
            for label, topic_key in topics
        ]
        keyboard.append([
            InlineKeyboardButton("🎯 تغییر حالت رابطه" if lang == 'fa' else "🎯 Change Mode", callback_data='relationship_modes')
        ])
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت" if lang == 'fa' else "🔙 Back", callback_data='back_to_main')
        ])

        if query:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    finally:
        db.close()


async def provide_coaching_advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate tailored AI coaching advice for coaching_{mode}_{topic}"""
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_', 2)
    mode = parts[1] if len(parts) > 1 else 'serious'
    topic = parts[2] if len(parts) > 2 else 'compatibility'

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else 'fa'
        mi = get_mode_info(mode, lang)

        await query.edit_message_text("🤔 در حال آماده‌سازی راهنمای تخصصی..." if lang == 'fa' else "🤔 Generating research-backed coaching...")

        prompt = (
            f"به عنوان مشاور فمینیستی دوستیابی، درباره موضوع '{topic}' در حالت رابطه '{mi['name']}' به فارسی ۴ نکته عملی، کوتاه و علمی بنویس."
            if lang == 'fa'
            else f"As a research-backed feminist relationship coach, give 4 concise practical tips on '{topic}' for someone in '{mi['name']}' mode."
        )
        advice = await ai_service.chat(user.id if user else 0, prompt, lang)

        keyboard = [
            [InlineKeyboardButton("📚 موضوعات دیگر" if lang == 'fa' else "📚 More Topics", callback_data='mode_coaching')],
            [InlineKeyboardButton("💬 پرسش آزاد از هوش مصنوعی" if lang == 'fa' else "💬 Ask AI Coach", callback_data='ai_chat')],
            [InlineKeyboardButton("🔙 منوی اصلی" if lang == 'fa' else "🔙 Main Menu", callback_data='back_to_main')],
        ]
        await query.edit_message_text(
            f"🎓 {mi['emoji']} {mi['name']}\n\n{advice}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    finally:
        db.close()
