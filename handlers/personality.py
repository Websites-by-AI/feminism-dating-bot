"""
Personality Assessment & Compatibility Handler (MBTI + Love Languages + Attachment)
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User, PersonalityProfile
from ai_service import ai_service

MBTI_Q1, MBTI_Q2, MBTI_Q3, MBTI_Q4, LOVE_LANG, ATTACHMENT = range(10, 16)

MBTI_QUESTIONS = {
    'fa': [
        {
            'question': '۱/۴: در جمع‌های اجتماعی چطور انرژی می‌گیرید؟',
            'options': [
                ('E', '🗣️ با صحبت کردن با افراد زیاد انرژی می‌گیرم'),
                ('I', '📖 با گفتگوی عمیق با یک یا دو نفر انرژی می‌گیرم'),
            ],
        },
        {
            'question': '۲/۴: چطور اطلاعات دریافت و تحلیل می‌کنید؟',
            'options': [
                ('S', '🔍 روی واقعیت‌ها و جزئیات ملموس تمرکز می‌کنم'),
                ('N', '💡 روی ایده‌ها، الگوها و احتمالات آینده تمرکز می‌کنم'),
            ],
        },
        {
            'question': '۳/۴: چطور تصمیم‌های مهم می‌گیرید؟',
            'options': [
                ('T', '🧠 بر اساس منطق، تحلیل و عدالت'),
                ('F', '❤️ بر اساس احساسات، ارزش‌ها و همدلی'),
            ],
        },
        {
            'question': '۴/۴: سبک زندگی و برنامه‌ریزی شما چطور است؟',
            'options': [
                ('J', '📋 منظم، برنامه‌ریزی‌شده و مشخص'),
                ('P', '🎲 منعطف، خودجوش و باز به تغییر'),
            ],
        },
    ],
    'en': [
        {
            'question': '1/4: How do you recharge in social settings?',
            'options': [
                ('E', '🗣️ Energized by talking to many people'),
                ('I', '📖 Energized by deep 1-on-1 conversations'),
            ],
        },
        {
            'question': '2/4: How do you process information?',
            'options': [
                ('S', '🔍 Focus on concrete facts and details'),
                ('N', '💡 Focus on ideas, patterns, and possibilities'),
            ],
        },
        {
            'question': '3/4: How do you make important decisions?',
            'options': [
                ('T', '🧠 Logic, analysis, and fairness'),
                ('F', '❤️ Empathy, values, and human impact'),
            ],
        },
        {
            'question': '4/4: What is your lifestyle preference?',
            'options': [
                ('J', '📋 Structured, planned, and organized'),
                ('P', '🎲 Flexible, spontaneous, and adaptable'),
            ],
        },
    ],
}

LOVE_LANGUAGE_QUESTIONS = {
    'fa': {
        'question': '💕 کدام مورد در رابطه برای شما از همه ارزشمندتر است؟',
        'options': [
            ('words', '💬 کلام محبت‌آمیز و تشویق'),
            ('time', '⏰ وقت باکیفیت و توجه کامل'),
            ('gifts', '🎁 هدیه‌های معنادار و یادگاری'),
            ('service', '🤝 کمک عملی در کارها'),
            ('touch', '🤗 تماس فیزیکی محترمانه (آغوش)'),
        ],
    },
    'en': {
        'question': '💕 What makes you feel most valued in a relationship?',
        'options': [
            ('words', '💬 Words of affirmation'),
            ('time', '⏰ Undivided quality time'),
            ('gifts', '🎁 Thoughtful gifts'),
            ('service', '🤝 Acts of service'),
            ('touch', '🤗 Respectful physical affection'),
        ],
    },
}

ATTACHMENT_QUESTIONS = {
    'fa': {
        'question': '🔗 وقتی شریک عاطفی‌تان چند ساعت دیر پیام می‌دهد چه حسی دارید؟',
        'options': [
            ('secure', '😊 آرامم؛ می‌دانم سرش شلوغ است و به هم اعتماد داریم'),
            ('anxious', '😟 نگران می‌شوم که شاید علاقه‌اش کم شده'),
            ('avoidant', '😐 مهم نیست، من هم ترجیح می‌دهم فضای مستقل داشته باشم'),
            ('fearful', '😣 هم دلم نزدیکی می‌خواهد و هم از آسیب دیدن می‌ترسم'),
        ],
    },
    'en': {
        'question': '🔗 How do you feel when your partner replies late?',
        'options': [
            ('secure', '😊 Calm — I trust them and respect their busy time'),
            ('anxious', '😟 Worried something might be wrong between us'),
            ('avoidant', '😐 Fine — I value lots of independent space'),
            ('fearful', '😣 Torn between wanting closeness and fearing hurt'),
        ],
    },
}

MBTI_DESCRIPTIONS = {
    'INTJ': {'fa': '🎯 معمار استراتژیک — مستقل، عمیق و آینده‌نگر', 'en': '🎯 The Architect — Strategic, independent, visionary'},
    'INTP': {'fa': '🔬 متفکر تحلیلی — کنجکاو، خلاق و منطقی', 'en': '🔬 The Logician — Curious, analytical, inventive'},
    'ENTJ': {'fa': '👑 فرمانده هدفمند — قاطع، رهبر و برنامه‌ریز', 'en': '👑 The Commander — Bold, decisive, strategic leader'},
    'ENTP': {'fa': '⚡ نوآور خلاق — پرانرژی، ایده‌پرداز و مناظره‌گر', 'en': '⚡ The Debater — Smart, curious intellectual explorer'},
    'INFJ': {'fa': '🌟 حامی الهام‌بخش — همدل، شهودی و ارزش‌مدار', 'en': '🌟 The Advocate — Deeply empathetic, insightful idealist'},
    'INFP': {'fa': '🌸 میانجی مهربان — اصیل، احساسی و خلاق', 'en': '🌸 The Mediator — Poetic, kind, values-driven'},
    'ENFJ': {'fa': '💖 قهرمان الهام‌بخش — گرم، حامی و کاریزماتیک', 'en': '💖 The Protagonist — Warm, inspiring, supportive'},
    'ENFP': {'fa': '🌈 پیکارگر پرشور — صمیمی، خلاق و مشتاق ارتباط', 'en': '🌈 The Campaigner — Enthusiastic, creative free spirit'},
    'ISTJ': {'fa': '🏛️ بازرس وفادار — مسئولیت‌پذیر، صادق و پایدار', 'en': '🏛️ The Logistician — Reliable, grounded, loyal'},
    'ISFJ': {'fa': '🛡️ مدافع دلسوز — فداکار، آرام و حامی امنیت عاطفی', 'en': '🛡️ The Defender — Dedicated, warm protector'},
    'ESTJ': {'fa': '📋 مدیر منظم — ساختارمند، صریح و قابل اتکا', 'en': '📋 The Executive — Organized, honest, dependable'},
    'ESFJ': {'fa': '🤝 میزبان صمیمی — مهربان، اجتماعی و همراه', 'en': '🤝 The Consul — Caring, social, harmonious'},
    'ISTP': {'fa': '🛠️ مهارت‌گر مستقل — آرام، عمل‌گرا و حل‌کننده مسئله', 'en': '🛠️ The Virtuoso — Practical, calm problem-solver'},
    'ISFP': {'fa': '🎨 ماجراجوی لطیف — هنرمند، مهربان و در لحظه', 'en': '🎨 The Adventurer — Gentle, artistic explorer'},
    'ESTP': {'fa': '🚀 کارآفرین پرجنب‌وجوش — جسور، عمل‌گرا و اجتماعی', 'en': '🚀 The Entrepreneur — Energetic, perceptive doer'},
    'ESFP': {'fa': '🎉 سرگرم‌کننده شاداب — خون‌گرم، خودجوش و مثبت', 'en': '🎉 The Entertainer — Spontaneous, joyful, warm'},
}


def _ensure_user(db, tg_user):
    user = db.query(User).filter_by(telegram_id=tg_user.id).first()
    if not user:
        user = User(telegram_id=tg_user.id, username=tg_user.username, name=tg_user.first_name or 'User', language='fa')
        db.add(user)
        db.commit()
    return user


async def start_personality_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show personality test intro"""
    query = update.callback_query
    if query:
        await query.answer()

    db = get_session()
    try:
        user = _ensure_user(db, update.effective_user)
        lang = user.language if user.language in ('fa', 'en') else 'en'
        context.user_data['mbti_answers'] = []

        if user.language == 'fa':
            intro_text = (
                "🧠 **تست جامع شخصیت‌شناسی رابطه**\n\n"
                "این ارزیابی علمی ۶ مرحله‌ای شامل موارد زیر است:\n"
                "• تیپ شخصیتی MBTI (۴ سوال)\n"
                "• زبان عشق اصلی شما (۱ سوال)\n"
                "• سبک دلبستگی عاطفی (۱ سوال)\n\n"
                "آماده‌اید؟"
            )
            btn_start = "🚀 شروع تست"
            btn_back = "🔙 بازگشت"
        else:
            intro_text = (
                "🧠 **Relationship Personality Assessment**\n\n"
                "This 6-step research-backed quiz covers:\n"
                "• MBTI Personality Type (4 questions)\n"
                "• Primary Love Language (1 question)\n"
                "• Attachment Style (1 question)\n\n"
                "Ready to begin?"
            )
            btn_start = "🚀 Start Quiz"
            btn_back = "🔙 Back"

        keyboard = [
            [InlineKeyboardButton(btn_start, callback_data='personality_start')],
            [InlineKeyboardButton(btn_back, callback_data='back_to_main')],
        ]
        if query:
            await query.edit_message_text(intro_text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(intro_text, reply_markup=InlineKeyboardMarkup(keyboard))
    finally:
        db.close()


async def _send_mbti_question(query, lang: str, q_idx: int):
    q_lang = 'fa' if lang == 'fa' else 'en'
    q_data = MBTI_QUESTIONS[q_lang][q_idx]
    keyboard = [
        [InlineKeyboardButton(opt_text, callback_data=f'mbti_{q_idx}_{code}')]
        for code, opt_text in q_data['options']
    ]
    await query.edit_message_text(q_data['question'], reply_markup=InlineKeyboardMarkup(keyboard))


async def personality_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unified stateless/stateful callback router for all personality quiz steps"""
    query = update.callback_query
    data = query.data

    if data == 'personality_test':
        await start_personality_test(update, context)
        return

    await query.answer()
    db = get_session()
    try:
        user = _ensure_user(db, update.effective_user)
        lang = user.language or 'fa'
        q_lang = 'fa' if lang == 'fa' else 'en'

        if data == 'personality_start':
            context.user_data['mbti_answers'] = []
            await _send_mbti_question(query, lang, 0)
            return

        if data.startswith('mbti_'):
            parts = data.split('_')
            # Support both mbti_{q_idx}_{code} and legacy mbti_{code}
            if len(parts) == 3:
                q_idx = int(parts[1])
                code = parts[2]
            else:
                code = parts[1]
                q_idx = len(context.user_data.get('mbti_answers', []))

            answers = context.user_data.get('mbti_answers', [])
            if len(answers) > q_idx:
                answers = answers[:q_idx]
            answers.append(code)
            context.user_data['mbti_answers'] = answers

            if len(answers) < 4:
                await _send_mbti_question(query, lang, len(answers))
            else:
                context.user_data['mbti_type'] = ''.join(answers[:4])
                ll_data = LOVE_LANGUAGE_QUESTIONS[q_lang]
                kb = [
                    [InlineKeyboardButton(txt, callback_data=f'lovelang_{code}')]
                    for code, txt in ll_data['options']
                ]
                await query.edit_message_text(ll_data['question'], reply_markup=InlineKeyboardMarkup(kb))
            return

        if data.startswith('lovelang_'):
            context.user_data['love_language'] = data.replace('lovelang_', '')
            att_data = ATTACHMENT_QUESTIONS[q_lang]
            kb = [
                [InlineKeyboardButton(txt, callback_data=f'attach_{code}')]
                for code, txt in att_data['options']
            ]
            await query.edit_message_text(att_data['question'], reply_markup=InlineKeyboardMarkup(kb))
            return

        if data.startswith('attach_'):
            attachment_style = data.replace('attach_', '')
            mbti_type = context.user_data.get('mbti_type', 'INFJ')
            love_lang = context.user_data.get('love_language', 'time')

            personality = db.query(PersonalityProfile).filter_by(user_id=user.id).first()
            if not personality:
                personality = PersonalityProfile(user_id=user.id)
                db.add(personality)

            personality.mbti_type = mbti_type
            personality.love_language_primary = love_lang
            personality.attachment_style = attachment_style
            personality.assessment_completed = True
            db.commit()

            desc_map = MBTI_DESCRIPTIONS.get(mbti_type, MBTI_DESCRIPTIONS['INFJ'])
            desc = desc_map['fa'] if lang == 'fa' else desc_map['en']

            ai_prompt = (
                f"به فارسی در ۳ نکته کوتاه بگو تیپ شخصیتی {mbti_type} با زبان عشق {love_lang} و سبک دلبستگی {attachment_style} در رابطه عاطفی چه نقاط قوتی دارد و با چه افرادی سازگارتر است."
                if lang == 'fa'
                else f"In 3 concise bullet points, share relationship strengths and best partner compatibility for MBTI {mbti_type}, love language '{love_lang}', and '{attachment_style}' attachment."
            )
            ai_insights = await ai_service.chat(user.id, ai_prompt, lang)

            if lang == 'fa':
                result_text = (
                    f"🎉 نتیجه شخصیت‌شناسی شما آماده شد!\n\n"
                    f"🧠 تیپ MBTI: {mbti_type}\n{desc}\n\n"
                    f"💕 زبان عشق: {love_lang}\n"
                    f"🔗 سبک دلبستگی: {attachment_style}\n\n"
                    f"🤖 تحلیل هوش مصنوعی:\n{ai_insights}"
                )
                kb = [
                    [InlineKeyboardButton("💕 مشاهده پروفایل‌های سازگار", callback_data='browse')],
                    [InlineKeyboardButton("🔄 تکرار تست", callback_data='personality_start')],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data='back_to_main')],
                ]
            else:
                result_text = (
                    f"🎉 Your Personality Assessment Results!\n\n"
                    f"🧠 MBTI Type: {mbti_type}\n{desc}\n\n"
                    f"💕 Love Language: {love_lang}\n"
                    f"🔗 Attachment Style: {attachment_style}\n\n"
                    f"🤖 AI Insights:\n{ai_insights}"
                )
                kb = [
                    [InlineKeyboardButton("💕 Find Compatible Profiles", callback_data='browse')],
                    [InlineKeyboardButton("🔄 Retake Quiz", callback_data='personality_start')],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')],
                ]

            await query.edit_message_text(result_text, reply_markup=InlineKeyboardMarkup(kb))
    finally:
        db.close()
