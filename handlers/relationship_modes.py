"""
10 Relationship Modes & Mode-Specific Compatibility Tests
=========================================================
Includes the 8 classic modes PLUS:
  - 🚀 startup: Startup Co-founder & Life Partner
  - 🌍 abroad: International & Cross-Cultural Dating
"""
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session, User, RelationshipPreferences, ConnectionTest
from ai_service import ai_service

RELATIONSHIP_MODES = {
    'startup': {
        'fa': {'emoji': '🚀', 'name': 'شریک استارتاپی (جدید)', 'desc': 'یافتن هم‌بنیان‌گذار و شریک زندگی با اهداف کارآفرینی و ارزش‌های برابر'},
        'en': {'emoji': '🚀', 'name': 'Startup Co-founder (NEW)', 'desc': 'Meet a co-founder & partner sharing your entrepreneurial vision and egalitarian values'},
        'tr': {'emoji': '🚀', 'name': 'Girişimci İş & Yaşam Ortağı', 'desc': 'Hem girişim hem yaşam vizyonunuzu paylaşan eşitlikçi kurucu ortak'},
    },
    'abroad': {
        'fa': {'emoji': '🌍', 'name': 'آشنایی بین‌المللی (جدید)', 'desc': 'ارتباط بین‌فرهنگی، راه دور و مهاجرت آگاهانه و ایمن'},
        'en': {'emoji': '🌍', 'name': 'International & Cross-Cultural (NEW)', 'desc': 'Safe cross-border dating, long-distance rhythm, and conscious relocation'},
        'tr': {'emoji': '🌍', 'name': 'Uluslararası Tanışma', 'desc': 'Güvenli sınır ötesi, kültürlerarası ve uzaktan ilişki'},
    },
    'serious': {
        'fa': {'emoji': '💍', 'name': 'رابطه جدی', 'desc': 'به دنبال شریک زندگی و تعهد بلندمدت برابر'},
        'en': {'emoji': '💍', 'name': 'Serious Relationship', 'desc': 'Looking for an egalitarian long-term life partner'},
    },
    'casual': {
        'fa': {'emoji': '🌸', 'name': 'آشنایی غیررسمی', 'desc': 'قرارهای محترمانه و امن بدون فشار تعهد فوری'},
        'en': {'emoji': '🌸', 'name': 'Casual Dating', 'desc': 'Respectful, low-pressure safe dating'},
    },
    'marriage': {
        'fa': {'emoji': '💒', 'name': 'ازدواج برابر', 'desc': 'آماده ازدواج مبتنی بر برابری حقوق و احترام متقابل'},
        'en': {'emoji': '💒', 'name': 'Egalitarian Marriage', 'desc': 'Ready for marriage built on equal rights and shared goals'},
    },
    'intellectual': {
        'fa': {'emoji': '🧠', 'name': 'اتصال فکری', 'desc': 'گفتگوهای عمیق علمی، فلسفی و فرهنگی'},
        'en': {'emoji': '🧠', 'name': 'Intellectual Connection', 'desc': 'Deep intellectual, cultural, and scientific conversations'},
    },
    'emotional': {
        'fa': {'emoji': '💝', 'name': 'اتصال عاطفی', 'desc': 'همدلی عمیق، امنیت روانی و صمیمیت تدریجی'},
        'en': {'emoji': '💝', 'name': 'Emotional Connection', 'desc': 'Deep empathy, emotional safety, and gradual intimacy'},
    },
    'friendship': {
        'fa': {'emoji': '👥', 'name': 'دوستی و جامعه حمایتی', 'desc': 'دوستی افلاطونی امن و شبکه‌سازی'},
        'en': {'emoji': '👥', 'name': 'Friendship & Community', 'desc': 'Safe platonic friendships and supportive community'},
    },
    'open': {
        'fa': {'emoji': '🌈', 'name': 'رابطه باز اخلاقی', 'desc': 'شفافیت کامل، توافق آگاهانه و مرزهای روشن'},
        'en': {'emoji': '🌈', 'name': 'Ethical Open Relationship', 'desc': 'Full transparency, clear boundaries, and informed consent'},
    },
    'one_night': {
        'fa': {'emoji': '🔥', 'name': 'قرار کوتاه‌مدت امن', 'desc': 'با رعایت کامل پروتکل‌های ایمنی و رضایت FRIES'},
        'en': {'emoji': '🔥', 'name': 'Safe Short-Term Encounter', 'desc': 'Strict FRIES consent and public-first safety protocols'},
    },
}


def get_mode_info(mode_key: str, lang: str) -> dict:
    mode_dict = RELATIONSHIP_MODES.get(mode_key, RELATIONSHIP_MODES['serious'])
    return mode_dict.get(lang, mode_dict.get('en'))


async def show_relationship_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all 10 relationship modes menu"""
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
        rel_prefs = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
        current_mode = rel_prefs.relationship_mode if rel_prefs else None

        if lang == 'fa':
            text = "🎯 انتخاب حالت رابطه (۱۰ حالت تخصصی)\n\n"
            if current_mode and current_mode in RELATIONSHIP_MODES:
                mi = get_mode_info(current_mode, lang)
                text += f"حالت فعلی شما: {mi['emoji']} {mi['name']}\n\n"
            text += "حالت مورد نظرتان را انتخاب کنید تا تست سازگاری و مربی اختصاصی آن فعال شود:"
        else:
            text = "🎯 Choose Your Relationship Mode (10 Specialized Modes)\n\n"
            if current_mode and current_mode in RELATIONSHIP_MODES:
                mi = get_mode_info(current_mode, lang)
                text += f"Current Mode: {mi['emoji']} {mi['name']}\n\n"
            text += "Select a mode to unlock tailored matching, compatibility tests, and AI coaching:"

        keyboard = []
        for mode_key in RELATIONSHIP_MODES:
            mi = get_mode_info(mode_key, lang)
            mark = "✅ " if mode_key == current_mode else ""
            keyboard.append([
                InlineKeyboardButton(f"{mark}{mi['emoji']} {mi['name']}", callback_data=f"mode_select_{mode_key}")
            ])

        if current_mode:
            keyboard.append([
                InlineKeyboardButton(
                    "🧪 تست سازگاری حالت فعلی" if lang == 'fa' else "🧪 Take Mode Compatibility Test",
                    callback_data=f"connection_test_{current_mode}",
                )
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


async def select_relationship_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save selected relationship mode and offer compatibility test"""
    query = update.callback_query
    await query.answer()
    mode_key = query.data.replace('mode_select_', '')

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            return
        lang = user.language or 'fa'

        rel_prefs = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
        if not rel_prefs:
            rel_prefs = RelationshipPreferences(user_id=user.id)
            db.add(rel_prefs)
        rel_prefs.relationship_mode = mode_key
        rel_prefs.updated_at = datetime.utcnow()
        db.commit()

        mi = get_mode_info(mode_key, lang)
        if lang == 'fa':
            text = (
                f"✅ حالت رابطه شما ذخیره شد!\n\n"
                f"{mi['emoji']} {mi['name']}\n{mi['desc']}\n\n"
                f"پیشنهاد می‌کنیم تست سازگاری این حالت را انجام دهید تا هوش مصنوعی تحلیل اختصاصی شما را ثبت کند."
            )
            kb = [
                [InlineKeyboardButton("🧪 شروع تست سازگاری", callback_data=f"connection_test_{mode_key}")],
                [InlineKeyboardButton("🎓 راهنمای هوش مصنوعی این حالت", callback_data='mode_coaching')],
                [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')],
            ]
        else:
            text = (
                f"✅ Relationship Mode Saved!\n\n"
                f"{mi['emoji']} {mi['name']}\n{mi['desc']}\n\n"
                f"Take the compatibility test for tailored AI insights!"
            )
            kb = [
                [InlineKeyboardButton("🧪 Start Compatibility Test", callback_data=f"connection_test_{mode_key}")],
                [InlineKeyboardButton("🎓 AI Coaching for This Mode", callback_data='mode_coaching')],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')],
            ]

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    finally:
        db.close()


def generate_mode_specific_questions(mode: str, lang: str) -> list:
    is_fa = (lang == 'fa')
    bank = {
        'startup': [
            {
                'question': '۱/۳: شفافیت در مکتوب کردن تقسیم سهام (Vesting) و نقش‌ها چقدر برایتان مهم است؟' if is_fa else '1/3: How important is written equity & role clarity (vesting) before co-founding?',
                'options': ['💯 کاملاً ضروری و مکتوب', '👍 مهم است', '🤔 هنوز مشخص نیست'] if is_fa else ['💯 Essential in writing', '👍 Important', '🤔 Unsure'],
            },
            {
                'question': '۲/۳: در زمان استرس استارتاپی چطور مرز رابطه عاطفی و کاری را حفظ می‌کنید؟' if is_fa else '2/3: How do you separate startup stress from emotional intimacy?',
                'options': ['✅ ساعت‌های بدون کار و گفتگوی شفاف', '⚖️ تفکیک وظایف', '🤷 در حال یادگیری'] if is_fa else ['✅ Dedicated work-free check-ins', '⚖️ Clear role boundaries', '🤷 Still learning'],
            },
            {
                'question': '۳/۳: واکنش شما به پیشنهاد «کار رایگان بدون قرارداد و سهام» چیست؟' if is_fa else '3/3: How do you respond to unpaid labor without written equity?',
                'options': ['🚩 خط قرمز قطعی', '⚠️ مذاکره مجدد فوری', '🤔 بستگی دارد'] if is_fa else ['🚩 Absolute red flag', '⚠️ Immediate renegotiation', '🤔 Depends'],
            },
        ],
        'abroad': [
            {
                'question': '۱/۳: آیا پیش از هر تصمیم سفری، تماس تصویری زنده و مستمر برقرار می‌کنید؟' if is_fa else '1/3: Do you verify identity via regular live video calls before travel?',
                'options': ['✅ همیشه و مستمر', '👍 بله', '❌ به‌ندرت'] if is_fa else ['✅ Always consistently', '👍 Yes', '❌ Rarely'],
            },
            {
                'question': '۲/۳: در برابر درخواست پول، رمزارز یا هزینه ویزا چه واکنشی دارید؟' if is_fa else '2/3: How do you react to requests for money, crypto, or visa fees?',
                'options': ['🛡️ رد قاطع و مسدودسازی', '⚠️ بررسی با احتیاط', '🤔 نامطمئن'] if is_fa else ['🛡️ Immediate block (scam red flag)', '⚠️ Cautious review', '🤔 Unsure'],
            },
            {
                'question': '۳/۳: حفظ استقلال مالی و حقوقی در کشور مقصد چقدر برایتان اولویت دارد؟' if is_fa else '3/3: How important is maintaining independent finances and legal status abroad?',
                'options': ['💯 اولویت مطلق', '👍 زیاد', '🙂 متوسط'] if is_fa else ['💯 Top priority', '👍 High', '🙂 Moderate'],
            },
        ],
    }
    default_qs = [
        {
            'question': '۱/۳: شفافیت در بیان مرزها و انتظارات چقدر برایتان اهمیت دارد؟' if is_fa else '1/3: How important is clear communication of boundaries and expectations?',
            'options': ['💯 بسیار ضروری', '👍 مهم', '🌱 در حال تمرین'] if is_fa else ['💯 Essential', '👍 Important', '🌱 Practicing'],
        },
        {
            'question': '۲/۳: در قرارهای ابتدایی کدام اصل ایمنی را همیشه رعایت می‌کنید؟' if is_fa else '2/3: Which safety habit do you follow on early dates?',
            'options': ['🛡️ مکان عمومی + اطلاع به دوست مخفی', '☕ فقط مکان عمومی', '📱 تماس تلفنی قبل از قرار'] if is_fa else ['🛡️ Public venue + Secret Friend', '☕ Public venue', '📱 Video call first'],
        },
        {
            'question': '۳/۳: مهم‌ترین ارزش شما در این حالت رابطه چیست؟' if is_fa else '3/3: What is your core value in this relationship mode?',
            'options': ['🤝 برابری، احترام و رضایت آگاهانه', '💬 صداقت و همدلی', '🌟 رشد مشترک'] if is_fa else ['🤝 Equality, respect & FRIES consent', '💬 Honesty & empathy', '🌟 Shared growth'],
        },
    ]
    return bank.get(mode, default_qs)


async def start_connection_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start compatibility test for a relationship mode"""
    query = update.callback_query
    await query.answer()
    mode = query.data.replace('connection_test_', '')

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else 'fa'
        questions = generate_mode_specific_questions(mode, lang)
        context.user_data['connection_test'] = {
            'mode': mode,
            'questions': questions,
            'answers': [],
            'current_q': 0,
        }
        await ask_test_question(query, context, lang)
    finally:
        db.close()


async def handle_test_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle test_answer_{q_index}_{opt_idx} button clicks"""
    query = update.callback_query
    await query.answer()

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else 'fa'
    finally:
        db.close()

    test_data = context.user_data.get('connection_test')
    if not test_data:
        await show_relationship_modes(update, context)
        return

    parts = query.data.split('_')
    opt_idx = int(parts[-1]) if parts[-1].isdigit() else 0
    q_idx = test_data['current_q']
    questions = test_data['questions']
    if q_idx < len(questions):
        opts = questions[q_idx]['options']
        chosen = opts[opt_idx] if opt_idx < len(opts) else opts[0]
        test_data['answers'].append({'choice_idx': opt_idx, 'text': chosen})
        test_data['current_q'] += 1

    await ask_test_question(query, context, lang)


async def ask_test_question(query, context: ContextTypes.DEFAULT_TYPE, lang: str):
    test_data = context.user_data['connection_test']
    q_index = test_data['current_q']
    questions = test_data['questions']

    if q_index >= len(questions):
        await complete_connection_test(query, context, lang)
        return

    q = questions[q_index]
    keyboard = [
        [InlineKeyboardButton(option, callback_data=f"test_answer_{q_index}_{idx}")]
        for idx, option in enumerate(q['options'])
    ]
    await query.edit_message_text(q['question'], reply_markup=InlineKeyboardMarkup(keyboard))


async def complete_connection_test(query, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Save test in SQLAlchemy ConnectionTest model properly and show AI analysis"""
    test_data = context.user_data.get('connection_test', {})
    mode = test_data.get('mode', 'serious')
    answers = test_data.get('answers', [])

    score = round(
        sum(100 if a['choice_idx'] == 0 else (82 if a['choice_idx'] == 1 else 68) for a in answers)
        / max(1, len(answers))
    )

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if user:
            rel_prefs = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
            if not rel_prefs:
                rel_prefs = RelationshipPreferences(user_id=user.id, relationship_mode=mode)
                db.add(rel_prefs)
                db.flush()

            mi = get_mode_info(mode, lang)
            prompt = (
                f"به فارسی در ۳ نکته کاربردی نتیجه تست سازگاری حالت «{mi['name']}» با امتیاز {score}% را تحلیل کن و یک توصیه ایمنی بده."
                if lang == 'fa'
                else f"In 3 short practical bullet points, analyze a {score}% readiness score for '{mi['name']}' mode and include one safety tip."
            )
            analysis = await ai_service.chat(user.id, prompt, lang)

            conn_test = ConnectionTest(
                user_id=user.id,
                relationship_pref_id=rel_prefs.id,
                test_type='compatibility',
                mode_specific=True,
                answers_json=json.dumps(answers, ensure_ascii=False),
                compatibility_score=int(score),
                readiness_score=int(score),
                ai_analysis=analysis,
                completed_at=datetime.utcnow(),
            )
            db.add(conn_test)
            rel_prefs.compatibility_score = float(score)
            db.commit()

            if lang == 'fa':
                text = (
                    f"🎉 تست سازگاری «{mi['emoji']} {mi['name']}» تکمیل شد!\n\n"
                    f"📊 امتیاز آمادگی شما: {score}%\n\n"
                    f"🤖 تحلیل هوش مصنوعی:\n{analysis}"
                )
                kb = [
                    [InlineKeyboardButton("💕 مشاهده پروفایل‌ها", callback_data='browse')],
                    [InlineKeyboardButton("🎓 نکات مربی رابطه", callback_data='mode_coaching')],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data='back_to_main')],
                ]
            else:
                text = (
                    f"🎉 '{mi['emoji']} {mi['name']}' Test Complete!\n\n"
                    f"📊 Readiness Score: {score}%\n\n"
                    f"🤖 AI Insights:\n{analysis}"
                )
                kb = [
                    [InlineKeyboardButton("💕 Browse Profiles", callback_data='browse')],
                    [InlineKeyboardButton("🎓 Mode Coaching", callback_data='mode_coaching')],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')],
                ]

            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    finally:
        db.close()
        context.user_data.pop('connection_test', None)
