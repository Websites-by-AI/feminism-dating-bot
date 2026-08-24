"""
Relationship Modes Handler
Supports different relationship types with connection tests
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session, User, RelationshipPreferences, ConnectionTest
from languages import get_text
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Relationship modes
RELATIONSHIP_MODES = {
    'serious': {
        'fa': '💍 رابطه جدی',
        'en': '💍 Serious Relationship',
        'description_fa': 'به دنبال شریک زندگی و ازدواج',
        'description_en': 'Looking for life partner and marriage'
    },
    'casual': {
        'fa': '🌸 رابطه دوستانه',
        'en': '🌸 Casual Dating',
        'description_fa': 'آشنایی بدون فشار',
        'description_en': 'Dating without pressure'
    },
    'one_night': {
        'fa': '🔥 قرار کوتاه',
        'en': '🔥 One Night / Short-term',
        'description_fa': 'ملاقات کوتاه مدت',
        'description_en': 'Short-term meeting'
    },
    'friendship': {
        'fa': '👥 دوستی',
        'en': '👥 Friendship',
        'description_fa': 'فقط دوستی',
        'description_en': 'Just friendship'
    },
    'marriage': {
        'fa': '💒 ازدواج',
        'en': '💒 Marriage',
        'description_fa': 'آماده ازدواج',
        'description_en': 'Ready for marriage'
    },
    'open': {
        'fa': '🌈 رابطه باز',
        'en': '🌈 Open Relationship',
        'description_fa': 'رابطه باز و اخلاقی',
        'description_en': 'Ethical non-monogamy'
    },
    'emotional': {
        'fa': '💝 اتصال عاطفی',
        'en': '💝 Emotional Connection',
        'description_fa': 'ارتباط عاطفی عمیق',
        'description_en': 'Deep emotional connection'
    },
    'intellectual': {
        'fa': '🧠 اتصال فکری',
        'en': '🧠 Intellectual Connection',
        'description_fa': 'ارتباط فکری و فرهنگی',
        'description_en': 'Intellectual and cultural connection'
    }
}

async def show_relationship_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show relationship mode selection"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language if user else 'fa'
        
        text = f"{get_text(lang, 'select_relationship_mode')}\n\n"
        text += get_text(lang, 'relationship_modes_description')
        
        buttons = []
        for mode_key, mode_data in RELATIONSHIP_MODES.items():
            mode_text = mode_data[lang]
            description = mode_data[f'description_{lang}']
            buttons.append([
                InlineKeyboardButton(
                    f"{mode_text}\n{description}",
                    callback_data=f'rel_mode_{mode_key}'
                )
            ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def select_relationship_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle relationship mode selection"""
    query = update.callback_query
    await query.answer()
    
    mode_key = query.data.replace('rel_mode_', '')
    mode_data = RELATIONSHIP_MODES.get(mode_key)
    
    if not mode_data:
        await query.answer("Invalid mode", show_alert=True)
        return
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Save to database
        rel_prefs = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
        if not rel_prefs:
            rel_prefs = RelationshipPreferences(user_id=user.id)
            db.add(rel_prefs)
        
        rel_prefs.relationship_mode = mode_key
        rel_prefs.updated_at = datetime.utcnow()
        db.commit()
        
        # Show confirmation with connection test option
        mode_text = mode_data[lang]
        text = f"✅ {get_text(lang, 'relationship_mode_set')}: {mode_text}\n\n"
        text += get_text(lang, 'connection_test_prompt')
        
        buttons = [
            [InlineKeyboardButton(
                f"🧪 {get_text(lang, 'take_connection_test')}",
                callback_data='start_connection_test'
            )],
            [InlineKeyboardButton(
                f"🔙 {get_text(lang, 'back_to_menu')}",
                callback_data='back_to_menu'
            )]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def start_connection_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the connection compatibility test"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Get user's relationship mode
        rel_prefs = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
        if not rel_prefs:
            await query.edit_message_text(
                get_text(lang, 'select_relationship_first'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        get_text(lang, 'select_mode'),
                        callback_data='select_relationship_mode'
                    )
                ]])
            )
            return
        
        mode_key = rel_prefs.relationship_mode
        mode_text = RELATIONSHIP_MODES[mode_key][lang]
        
        # Show test introduction
        text = f"🧪 {get_text(lang, 'connection_test_intro')}\n\n"
        text += f"{get_text(lang, 'current_mode')}: {mode_text}\n\n"
        text += get_text(lang, 'connection_test_description')
        
        buttons = [
            [InlineKeyboardButton(
                f"🚀 {get_text(lang, 'start_test')}",
                callback_data=f'connection_test_{mode_key}'
            )],
            [InlineKeyboardButton(
                f"🔙 {get_text(lang, 'back')}",
                callback_data='back_to_menu'
            )]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def run_connection_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run the actual connection test with AI analysis"""
    query = update.callback_query
    await query.answer()
    
    test_mode = query.data.replace('connection_test_', '')
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Show "testing" message
        await query.edit_message_text(
            f"🔍 {get_text(lang, 'analyzing_compatibility')}...\n\n"
            f"{get_text(lang, 'please_wait')}"
        )
        
        # Get user's personality profile
        from database import PersonalityProfile
        personality = db.query(PersonalityProfile).filter_by(user_id=user.id).first()
        
        # Prepare test questions based on mode
        test_questions = generate_mode_specific_questions(test_mode, lang)
        
        # Store test in context
        context.user_data['connection_test'] = {
            'mode': test_mode,
            'questions': test_questions,
            'current_question': 0,
            'answers': []
        }
        
        # Show first question
        await show_test_question(query, context, 0)
        
    finally:
        db.close()


def generate_mode_specific_questions(mode: str, lang: str) -> list:
    """Generate test questions specific to relationship mode"""
    
    questions = {
        'serious': [
            {
                'fa': 'آیا آماده تعهد بلندمدت هستید؟',
                'en': 'Are you ready for long-term commitment?',
                'options': ['✅ بله', '🤔 شاید', '❌ خیر']
            },
            {
                'fa': 'آیا به دنبال تشکیل خانواده هستید؟',
                'en': 'Are you looking to start a family?',
                'options': ['✅ بله', '⏰ در آینده', '❌ خیر']
            },
            {
                'fa': 'چقدر برای ازدواج جدی هستید؟',
                'en': 'How serious are you about marriage?',
                'options': ['💯 خیلی جدی', '👍 متوسط', '🤷 کم']
            }
        ],
        'casual': [
            {
                'fa': 'آیا با آشنایی بدون فشار راحت هستید؟',
                'en': 'Are you comfortable with casual dating?',
                'options': ['✅ بله', '🤔 بستگی دارد', '❌ خیر']
            },
            {
                'fa': 'چقدر وقت برای قرار گذاشتن دارید؟',
                'en': 'How much time do you have for dates?',
                'options': ['⏰ زیاد', '👌 متوسط', '🏃 کم']
            }
        ],
        'one_night': [
            {
                'fa': 'آیا به دنبال تجربه کوتاه مدت هستید؟',
                'en': 'Are you looking for short-term experience?',
                'options': ['✅ بله', '🤔 شاید', '❌ خیر']
            },
            {
                'fa': 'آیا با ملاقات حضوری راحت هستید؟',
                'en': 'Are you comfortable with in-person meetings?',
                'options': ['✅ بله', '🤔 با احتیاط', '❌ خیر']
            }
        ],
        'friendship': [
            {
                'fa': 'آیا به دنبال دوستی خالص هستید؟',
                'en': 'Are you looking for pure friendship?',
                'options': ['✅ بله', '🤔 بستگی دارد', '❌ نه']
            },
            {
                'fa': 'چه نوع فعالیت‌هایی را ترجیح می‌دهید؟',
                'en': 'What activities do you prefer?',
                'options': ['☕ کافه', '🎬 سینما', '🚶 پیاده‌روی']
            }
        ]
    }
    
    # Default questions if mode not found
    return questions.get(mode, [
        {
            'fa': 'آیا آماده برای شروع هستید؟',
            'en': 'Are you ready to start?',
            'options': ['✅ بله', '❌ خیر']
        }
    ])


async def show_test_question(query, context: ContextTypes.DEFAULT_TYPE, q_index: int):
    """Show a test question"""
    test_data = context.user_data.get('connection_test', {})
    questions = test_data.get('questions', [])
    
    if q_index >= len(questions):
        # Test complete
        await complete_connection_test(query, context)
        return
    
    question = questions[q_index]
    lang = 'fa'  # Default
    
    text = f"🧪 {get_text(lang, 'question')} {q_index + 1}/{len(questions)}\n\n"
    text += question[lang]
    
    buttons = []
    for option in question['options']:
        buttons.append([InlineKeyboardButton(option, callback_data=f'test_answer_{q_index}_{option}')])
    
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text, reply_markup=keyboard)


async def complete_connection_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Complete the test and show AI analysis"""
    query = update.callback_query
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        test_data = context.user_data.get('connection_test', {})
        mode = test_data.get('mode', 'unknown')
        answers = test_data.get('answers', [])
        
        # Calculate compatibility score
        compatibility_score = calculate_compatibility(mode, answers)
        
        # Generate AI analysis using RAG
        ai_analysis = await generate_ai_connection_analysis(user.id, mode, answers, lang)
        
        # Save test result to database
        test_result = ConnectionTest(
            user_id=user.id,
            relationship_mode=mode,
            answers_json=str(answers),
            compatibility_score=compatibility_score,
            ai_analysis=ai_analysis,
            completed_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        # Show results
        text = f"🎉 {get_text(lang, 'test_complete')}\n\n"
        text += f"📊 {get_text(lang, 'compatibility_score')}: {compatibility_score}%\n\n"
        text += f"🤖 {get_text(lang, 'ai_analysis')}:\\n{ai_analysis}\n\n"
        text += get_text(lang, 'test_recommendations')
        
        buttons = [
            [InlineKeyboardButton(
                f"🔄 {get_text(lang, 'retake_test')}",
                callback_data=f'connection_test_{mode}'
            )],
            [InlineKeyboardButton(
                f"🔙 {get_text(lang, 'back_to_menu')}",
                callback_data='back_to_menu'
            )]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
        # Clean up context
        if 'connection_test' in context.user_data:
            del context.user_data['connection_test']
        
    finally:
        db.close()


def calculate_compatibility(mode: str, answers: list) -> int:
    """Calculate compatibility score based on answers"""
    if not answers:
        return 50
    
    # Simple scoring based on positive answers
    positive_count = sum(1 for a in answers if '✅' in a or '💯' in a or 'بله' in a)
    score = int((positive_count / len(answers)) * 100)
    
    return max(0, min(100, score))


async def generate_ai_connection_analysis(user_id: int, mode: str, answers: list, lang: str) -> str:
    """Generate AI analysis using HuggingFace RAG"""
    from ai_service import ai_service
    
    # Prepare prompt with RAG context
    prompt = f"""You are a relationship psychology expert. Analyze this connection test result:

Relationship Mode: {mode}
User Answers: {', '.join(answers)}

Provide a brief, helpful analysis (2-3 sentences) about:
1. What this says about their relationship readiness
2. One strength they show
3. One area to consider

Keep it supportive and practical. Response in {'Persian' if lang == 'fa' else 'English'}."""
    
    try:
        response = await ai_service.chat(
            user_id=user_id,
            message=prompt,
            language=lang,
            user_profile=None
        )
        return response
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return get_text(lang, 'analysis_unavailable')


# Add new translation keys
RELATIONSHIP_TRANSLATIONS = {
    'fa': {
        'select_relationship_mode': '🎯 نوع رابطه خود را انتخاب کنید',
        'relationship_modes_description': 'این انتخاب به ما کمک می‌کند افراد مناسب‌تری برای شما پیدا کنیم',
        'relationship_mode_set': 'نوع رابطه شما تنظیم شد',
        'connection_test_prompt': 'آیا می‌خواهید تست اتصال را انجام دهید؟',
        'take_connection_test': 'تست اتصال را انجام دهید',
        'select_relationship_first': 'لطفاً ابتدا نوع رابطه را انتخاب کنید',
        'select_mode': 'انتخاب نوع رابطه',
        'connection_test_intro': '🧪 تست سازگاری اتصال',
        'current_mode': 'حالت فعلی',
        'connection_test_description': 'این تست به شما کمک می‌کند بفهمید چقدر برای این نوع رابطه آماده هستید',
        'analyzing_compatibility': 'در حال تحلیل سازگاری شما',
        'please_wait': 'لطفاً صبر کنید...',
        'question': 'سؤال',
        'test_complete': 'تست کامل شد!',
        'compatibility_score': 'امتیاز سازگاری',
        'ai_analysis': 'تحلیل هوش مصنوعی',
        'test_recommendations': '💡 برای نتایج بهتر، پروفایل خود را کامل کنید',
        'retake_test': 'تست مجدد',
        'analysis_unavailable': 'تحلیل در حال حاضر در دسترس نیست'
    },
    'en': {
        'select_relationship_mode': '🎯 Select Your Relationship Mode',
        'relationship_modes_description': 'This helps us find better matches for you',
        'relationship_mode_set': 'Your relationship mode has been set',
        'connection_test_prompt': 'Would you like to take the connection test?',
        'take_connection_test': 'Take Connection Test',
        'select_relationship_first': 'Please select a relationship mode first',
        'select_mode': 'Select Mode',
        'connection_test_intro': '🧪 Connection Compatibility Test',
        'current_mode': 'Current Mode',
        'connection_test_description': 'This test helps you understand your readiness for this relationship type',
        'analyzing_compatibility': 'Analyzing your compatibility',
        'please_wait': 'Please wait...',
        'question': 'Question',
        'test_complete': 'Test Complete!',
        'compatibility_score': 'Compatibility Score',
        'ai_analysis': 'AI Analysis',
        'test_recommendations': '💡 For better results, complete your profile',
        'retake_test': 'Retake Test',
        'analysis_unavailable': 'Analysis currently unavailable'
    }
}
