"""
Personality Test Handler
MBTI + Love Languages + Attachment Style + Enneagram
Based on apps like Boo, Birdy, and PersonalityMatch
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User, PersonalityProfile, DatingIntentions
from languages import get_text
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Conversation states
(
    MBTI_Q1, MBTI_Q2, MBTI_Q3, MBTI_Q4, MBTI_Q5, MBTI_Q6, MBTI_Q7, MBTI_Q8,
    LOVE_LANG_Q1, LOVE_LANG_Q2, LOVE_LANG_Q3, LOVE_LANG_Q4, LOVE_LANG_Q5,
    ATTACHMENT_Q1, ATTACHMENT_Q2, ATTACHMENT_Q3, ATTACHMENT_Q4,
    ENNEAGRAM_Q1, ENNEAGRAM_Q2, ENNEAGRAM_Q3,
    SHOW_RESULTS
) = range(21)


# MBTI Questions (simplified - 8 questions for 4 dimensions)
MBTI_QUESTIONS = {
    'fa': [
        {
            'question': '🎭 در یک مهمانی بزرگ، شما معمولاً:',
            'options': [
                ('E', '🗣️ با افراد جدید صحبت می‌کنم و انرژی می‌گیرم'),
                ('I', '📖 ترجیح می‌دهم با یک یا دو نفر صمیمی صحبت کنم')
            ],
            'dimension': 'EI'
        },
        {
            'question': '📚 وقتی چیزی یاد می‌گیرید، بیشتر توجه می‌کنید به:',
            'options': [
                ('S', '🔍 جزئیات عملی و واقعیت‌ها'),
                ('N', '💡 ایده‌ها و الگوهای کلی')
            ],
            'dimension': 'SN'
        },
        {
            'question': '⚖️ وقتی تصمیم مهمی می‌گیرید:',
            'options': [
                ('T', '🧠 منطق و استدلال را در نظر می‌گیرم'),
                ('F', '❤️ احساسات و تأثیر بر افراد را در نظر می‌گیرم')
            ],
            'dimension': 'TF'
        },
        {
            'question': '✈️ برای سفر ترجیح می‌دهید:',
            'options': [
                ('J', '📋 از قبل برنامه‌ریزی کنم'),
                ('P', '🎲 باز بگذارم و spontaneous باشم')
            ],
            'dimension': 'JP'
        },
        {
            'question': '💬 در مکالمات:',
            'options': [
                ('E', '🎤 بیشتر صحبت می‌کنم و فکر می‌کنم'),
                ('I', '🤔 اول فکر می‌کنم بعد صحبت می‌کنم')
            ],
            'dimension': 'EI'
        },
        {
            'question': '🎨 وقتی با یک پروژه جدید روبرو می‌شوید:',
            'options': [
                ('S', '📊 از تجربیات گذشته و روش‌های اثبات شده استفاده می‌کنم'),
                ('N', '🌟 روش‌های جدید و خلاقانه را امتحان می‌کنم')
            ],
            'dimension': 'SN'
        },
        {
            'question': '💔 وقتی کسی ناراحت است:',
            'options': [
                ('T', '🛠️ راه حل منطقی ارائه می‌دهم'),
                ('F', '🤗 اول همدردی و حمایت عاطفی می‌کنم')
            ],
            'dimension': 'TF'
        },
        {
            'question': '📅 برای آخر هفته:',
            'options': [
                ('J', '📝 برنامه مشخص دارم'),
                ('P', '🎈 بستگی به حال و هوا دارم')
            ],
            'dimension': 'JP'
        }
    ],
    'en': [
        {
            'question': '🎭 At a big party, you usually:',
            'options': [
                ('E', '🗣️ Talk to new people and gain energy'),
                ('I', '📖 Prefer deep conversations with one or two people')
            ],
            'dimension': 'EI'
        },
        {
            'question': '📚 When learning something, you focus more on:',
            'options': [
                ('S', '🔍 Practical details and facts'),
                ('N', '💡 Big ideas and patterns')
            ],
            'dimension': 'SN'
        },
        {
            'question': '⚖️ When making important decisions:',
            'options': [
                ('T', '🧠 I consider logic and reasoning'),
                ('F', '❤️ I consider feelings and impact on people')
            ],
            'dimension': 'TF'
        },
        {
            'question': '✈️ For travel, you prefer to:',
            'options': [
                ('J', '📋 Plan everything in advance'),
                ('P', '🎲 Keep it open and spontaneous')
            ],
            'dimension': 'JP'
        },
        {
            'question': '💬 In conversations:',
            'options': [
                ('E', '🎤 I talk and think out loud'),
                ('I', '🤔 I think first, then speak')
            ],
            'dimension': 'EI'
        },
        {
            'question': '🎨 When facing a new project:',
            'options': [
                ('S', '📊 I use proven methods from past experience'),
                ('N', '🌟 I try new and creative approaches')
            ],
            'dimension': 'SN'
        },
        {
            'question': '💔 When someone is upset:',
            'options': [
                ('T', '🛠️ I offer logical solutions'),
                ('F', '🤗 I offer empathy and emotional support first')
            ],
            'dimension': 'TF'
        },
        {
            'question': '📅 For the weekend:',
            'options': [
                ('J', '📝 I have a clear plan'),
                ('P', '🎈 It depends on how I feel')
            ],
            'dimension': 'JP'
        }
    ]
}

# Love Language Questions
LOVE_LANG_QUESTIONS = {
    'fa': [
        {
            'question': '💕 کدام یک بیشتر باعث می‌شود احساس دوست داشته شدن کنید؟',
            'options': [
                ('words', '💬 تعریف و کلمات محبت‌آمیز'),
                ('time', '⏰ وقت گذراندن با کیفیت'),
                ('gifts', '🎁 هدایای متفکرانه'),
                ('touch', '🤗 تماس فیزیکی و آغوش'),
                ('acts', '🛠️ کمک در کارها و خدمات')
            ]
        }
    ],
    'en': [
        {
            'question': '💕 Which makes you feel most loved?',
            'options': [
                ('words', '💬 Compliments and kind words'),
                ('time', '⏰ Quality time together'),
                ('gifts', '🎁 Thoughtful gifts'),
                ('touch', '🤗 Physical affection and hugs'),
                ('acts', '🛠️ Help with tasks and acts of service')
            ]
        }
    ]
}

# Attachment Style Questions
ATTACHMENT_QUESTIONS = {
    'fa': [
        {
            'question': '🔐 وقتی شریک عاطفی‌تان دیر جواب پیام می‌دهد:',
            'options': [
                ('secure', '😊 مشکلی نیست، احتمالاً مشغول است'),
                ('anxious', '😰 نگران می‌شوم و مدام گوشی‌ام را چک می‌کنم'),
                ('avoidant', '😐 اهمیتی نمی‌دهم، کار خودم را می‌کنم')
            ]
        },
        {
            'question': '💑 در رابطه عاطفی، شما معمولاً:',
            'options': [
                ('secure', '🤝 راحت اعتماد می‌کنم و صمیمی هستم'),
                ('anxious', '😟 نگرانم که طرف مقابل مرا ترک کند'),
                ('avoidant', '🏃 از صمیمیت زیاد معذب می‌شوم')
            ]
        }
    ],
    'en': [
        {
            'question': '🔐 When your partner takes long to reply:',
            'options': [
                ('secure', '😊 No problem, they\'re probably busy'),
                ('anxious', '😰 I get worried and keep checking my phone'),
                ('avoidant', '😐 I don\'t mind, I continue with my day')
            ]
        },
        {
            'question': '💑 In relationships, you usually:',
            'options': [
                ('secure', '🤝 I trust easily and am comfortable with intimacy'),
                ('anxious', '😟 I worry my partner will leave me'),
                ('avoidant', '🏃 I feel uncomfortable with too much closeness')
            ]
        }
    ]
}


async def start_personality_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the personality test"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        
        text = f"""🧠 {get_text(lang, 'personality_test_intro')}

{get_text(lang, 'personality_test_what')}
• 🎭 MBTI (16 نوع شخصیت)
• 💕 زبان عشق (Love Language)
• 🔐 سبک دلبستگی (Attachment Style)
• 🔢 انیاگرام (Enneagram)

{get_text(lang, 'personality_test_duration')}
{get_text(lang, 'personality_test_benefits')}"""
        
        buttons = [
            [InlineKeyboardButton(f"🚀 {get_text(lang, 'start_test')}", callback_data='personality_start')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def handle_mbti_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle MBTI test questions"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Initialize MBTI scores in context
        if 'mbti_scores' not in context.user_data:
            context.user_data['mbti_scores'] = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
        
        # Get selected option
        data = query.data  # e.g., 'mbti_E', 'mbti_I'
        if data.startswith('mbti_'):
            selected = data.replace('mbti_', '')
            context.user_data['mbti_scores'][selected] += 1
        
        # Get current question number
        current_q = context.user_data.get('mbti_question_num', 0)
        questions = MBTI_QUESTIONS.get(lang, MBTI_QUESTIONS['en'])
        
        # Move to next question
        current_q += 1
        context.user_data['mbti_question_num'] = current_q
        
        if current_q < len(questions):
            # Show next question
            q = questions[current_q]
            buttons = [
                [InlineKeyboardButton(opt[1], callback_data=f'mbti_{opt[0]}')]
                for opt in q['options']
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            
            progress = f"({current_q + 1}/{len(questions)})"
            await query.edit_message_text(
                f"{progress} {q['question']}",
                reply_markup=keyboard
            )
        else:
            # MBTI complete, calculate result
            scores = context.user_data['mbti_scores']
            mbti_type = ''
            mbti_type += 'E' if scores['E'] >= scores['I'] else 'I'
            mbti_type += 'S' if scores['S'] >= scores['N'] else 'N'
            mbti_type += 'T' if scores['T'] >= scores['F'] else 'F'
            mbti_type += 'J' if scores['J'] >= scores['P'] else 'P'
            
            context.user_data['mbti_type'] = mbti_type
            
            # Move to Love Language test
            context.user_data['love_lang_scores'] = {}
            await _show_love_lang_question(query, lang, 0, context)
            
    finally:
        db.close()


async def _show_love_lang_question(query, lang, q_num, context):
    """Show love language question"""
    questions = LOVE_LANG_QUESTIONS.get(lang, LOVE_LANG_QUESTIONS['en'])
    
    if q_num < len(questions):
        q = questions[q_num]
        buttons = [
            [InlineKeyboardButton(opt[1], callback_data=f'lovelang_{opt[0]}')]
            for opt in q['options']
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            f"💕 {get_text(lang, 'love_lang_question')} ({q_num + 1}/{len(questions)})\n\n{q['question']}",
            reply_markup=keyboard
        )
        context.user_data['love_lang_q_num'] = q_num
    else:
        # Calculate top love language
        scores = context.user_data.get('love_lang_scores', {})
        top_lang = max(scores, key=scores.get) if scores else 'words'
        context.user_data['love_lang'] = top_lang
        
        # Move to attachment style
        context.user_data['attachment_scores'] = {}
        await _show_attachment_question(query, lang, 0, context)


async def _show_attachment_question(query, lang, q_num, context):
    """Show attachment style question"""
    questions = ATTACHMENT_QUESTIONS.get(lang, ATTACHMENT_QUESTIONS['en'])
    
    if q_num < len(questions):
        q = questions[q_num]
        buttons = [
            [InlineKeyboardButton(opt[1], callback_data=f'attach_{opt[0]}')]
            for opt in q['options']
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            f"🔐 {get_text(lang, 'attachment_question')} ({q_num + 1}/{len(questions)})\n\n{q['question']}",
            reply_markup=keyboard
        )
        context.user_data['attachment_q_num'] = q_num
    else:
        # Calculate attachment style
        scores = context.user_data.get('attachment_scores', {})
        top_style = max(scores, key=scores.get) if scores else 'secure'
        context.user_data['attachment_style'] = top_style
        
        # Save all results
        await _save_personality_results(query, context)


async def _save_personality_results(query, context):
    """Save personality test results to database"""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Get or create personality profile
        profile = db.query(PersonalityProfile).filter_by(user_id=user.id).first()
        if not profile:
            profile = PersonalityProfile(user_id=user.id)
            db.add(profile)
        
        # Save MBTI
        profile.mbti_type = context.user_data.get('mbti_type')
        profile.mbti_scores = json.dumps(context.user_data.get('mbti_scores', {}))
        
        # Save Love Language
        profile.love_language_1 = context.user_data.get('love_lang')
        
        # Save Attachment Style
        profile.attachment_style = context.user_data.get('attachment_style')
        
        profile.test_completed = True
        profile.test_date = datetime.utcnow()
        
        db.commit()
        
        # Show results
        await _show_personality_results(query, context, lang)
        
    finally:
        db.close()


async def _show_personality_results(query, context, lang):
    """Display personality test results"""
    mbti = context.user_data.get('mbti_type', '????')
    love_lang = context.user_data.get('love_lang', 'words')
    attachment = context.user_data.get('attachment_style', 'secure')
    
    # MBTI descriptions
    mbti_descriptions = {
        'INFJ': get_text(lang, 'mbti_infj'),
        'ENFP': get_text(lang, 'mbti_enfp'),
        # Add all 16 types...
    }
    
    text = f"""🎉 {get_text(lang, 'personality_complete')}

━━━━━━━━━━━━━━━━━━
🎭 {get_text(lang, 'mbti_result')}: {mbti}
{mbti_descriptions.get(mbti, get_text(lang, 'mbti_generic'))}

💕 {get_text(lang, 'love_lang_result')}: {_get_love_lang_name(love_lang, lang)}

🔐 {get_text(lang, 'attachment_result')}: {_get_attachment_name(attachment, lang)}
━━━━━━━━━━━━━━━━━━

{get_text(lang, 'personality_match_info')}"""
    
    buttons = [
        [InlineKeyboardButton(f"💕 {get_text(lang, 'find_compatible')}", callback_data='find_compatible_matches')],
        [InlineKeyboardButton(f"🔄 {get_text(lang, 'retake_test')}", callback_data='personality_start')],
        [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(text, reply_markup=keyboard)


def _get_love_lang_name(lang_code, lang):
    """Get love language display name"""
    names = {
        'words': {'fa': '💬 کلمات محبت‌آمیز', 'en': '💬 Words of Affirmation'},
        'time': {'fa': '⏰ وقت با کیفیت', 'en': '⏰ Quality Time'},
        'gifts': {'fa': '🎁 هدایا', 'en': '🎁 Receiving Gifts'},
        'touch': {'fa': '🤗 تماس فیزیکی', 'en': '🤗 Physical Touch'},
        'acts': {'fa': '🛠️ خدمات', 'en': '🛠️ Acts of Service'},
    }
    return names.get(lang_code, {}).get(lang, lang_code)


def _get_attachment_name(style, lang):
    """Get attachment style display name"""
    names = {
        'secure': {'fa': '🤝 ایمن', 'en': '🤝 Secure'},
        'anxious': {'fa': '😟 مضطرب', 'en': '😟 Anxious'},
        'avoidant': {'fa': '🏃 اجتنابی', 'en': '🏃 Avoidant'},
        'disorganized': {'fa': '🌀 ناایمن', 'en': '🌀 Disorganized'},
    }
    return names.get(style, {}).get(lang, style)
