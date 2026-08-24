"""
AI Dating Telegram Bot
======================
A multi-language dating bot with AI assistant, profile matching, and swiping features.

Languages: Farsi, English, Swedish, German, Turkish, Arabic, French, Spanish, Kurdish
AI Backends: HuggingFace → OpenRouter → Gemini (fallback chain)

Setup:
1. Install requirements: pip install -r requirements.txt
2. Create a .env file with your bot token (see .env.example)
3. Run: python main.py
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ConversationHandler, filters
)
from config import BOT_TOKEN
from database import init_db
from languages import get_text, SUPPORTED_LANGUAGES

# Import handlers
from handlers.start import (
    start, language_selected, handle_profile_input, 
    cancel, show_main_menu, SELECTING_LANGUAGE, SELECTING_LANGUAGE_MANUAL
)
from handlers.matching import (
    browse_profiles, handle_swipe, show_matches
)
from handlers.chat import (
    start_ai_chat, handle_ai_message, exit_ai_chat, AI_CHAT_STATE
)
from handlers.settings import (
    show_settings, handle_settings_action, 
    handle_preference_input, cancel_settings,
    SET_AGE_RANGE, SET_DISTANCE
)
from handlers.safety import (
    show_safety_menu, safety_callback_router, 
    handle_secret_friend_input, SAFETY_MENU
)
from handlers.personality import (
    start_personality_test, handle_mbti_question,
    MBTI_Q1, SHOW_RESULTS as PERSONALITY_DONE
)
from handlers.date_history import (
    show_date_history, start_add_date, handle_date_type,
    handle_date_input, handle_outcome, show_ai_analysis
)
from handlers.safety_enhanced import (
    show_enhanced_safety, setup_hidden_words, 
    add_hidden_word, handle_hidden_word_input
)
from handlers.relationship_modes import (
    show_relationship_modes, select_relationship_mode,
    start_connection_test, run_connection_test
)
from handlers.mode_coaching import (
    start_mode_coaching, handle_coaching_topic
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context):
    """Central callback query handler - routes to appropriate handlers."""
    query = update.callback_query
    data = query.data
    
    # Language selection
    if data.startswith('lang_'):
        return await language_selected(update, context)
    
    # Browse profiles
    elif data == 'browse' or data == 'browse_next':
        context.user_data['browsing'] = True
        await browse_profiles(update, context)
    
    # Swipe actions
    elif data.startswith('like_') or data.startswith('pass_') or data == 'browse_next':
        await handle_swipe(update, context)
    
    # Matches
    elif data == 'matches':
        await show_matches(update, context)
    
    # AI Chat
    elif data == 'ai_chat':
        return await start_ai_chat(update, context)
    
    # Personality Test
    elif data == 'personality_test':
        return await start_personality_test(update, context)
    
    # Date History
    elif data == 'date_history':
        return await show_date_history(update, context)
    
    # Add Date
    elif data == 'add_date':
        return await start_add_date(update, context)
    
    # AI Analysis
    elif data == 'ai_analysis':
        return await show_ai_analysis(update, context)
    
    # Enhanced Safety
    elif data == 'enhanced_safety':
        return await show_enhanced_safety(update, context)
    
    # Hidden Words
    elif data == 'hidden_words':
        return await setup_hidden_words(update, context)
    
    # Relationship Modes
    elif data == 'relationship_modes':
        return await show_relationship_modes(update, context)
    
    elif data.startswith('rel_mode_'):
        return await select_relationship_mode(update, context)
    
    elif data == 'start_connection_test':
        return await start_connection_test(update, context)
    
    elif data.startswith('connection_test_'):
        return await run_connection_test(update, context)
    
    # Mode-Specific Coaching
    elif data == 'mode_coaching':
        return await start_mode_coaching(update, context)
    
    elif data.startswith('coach_topic_'):
        return await handle_coaching_topic(update, context)
    
    # Settings
    elif data == 'settings':
        await show_settings(update, context)
    
    # Settings actions
    elif data.startswith('set_'):
        return await handle_settings_action(update, context)
    
    # Back to menu
    elif data == 'back_to_menu':
        context.user_data.clear()
        db = __import__('database').get_session()
        try:
            from database import User
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            lang = user.language if user else 'fa'
        finally:
            db.close()
        
        await query.edit_message_text(
            get_text(lang, 'main_menu'),
            reply_markup=_get_main_menu_buttons(lang)
        )
    
    # Edit profile
    elif data == 'edit_profile':
        db = __import__('database').get_session()
        try:
            from database import User
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            lang = user.language if user else 'fa'
            context.user_data['step'] = 'name'
            await query.edit_message_text(
                get_text(lang, 'ask_name'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'cancel'), callback_data='cancel')
                ]])
            )
        finally:
            db.close()
        return SELECTING_LANGUAGE_MANUAL
    
    # Cancel
    elif data == 'cancel':
        context.user_data.clear()
        db = __import__('database').get_session()
        try:
            from database import User
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            lang = user.language if user else 'fa'
        finally:
            db.close()
        
        await query.edit_message_text(
            get_text(lang, 'cancel'),
            reply_markup=_get_main_menu_buttons(lang)
        )
        return ConversationHandler.END
    
    # Cancel settings
    elif data == 'cancel_settings':
        return await cancel_settings(update, context)
    
    # Chat with match
    elif data.startswith('chat_'):
        await query.answer("💬 Chat feature coming soon!")
    
    else:
        await query.answer()


async def menu_command(update: Update, context):
    """Handle /menu command."""
    await show_main_menu(update, context)


async def help_command(update: Update, context):
    """Handle /help command."""
    db = __import__('database').get_session()
    try:
        from database import User
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else 'fa'
    finally:
        db.close()
    
    help_text = {
        'fa': '📖 راهنمای استفاده:\n\n/start - شروع کار\n/menu - منوی اصلی\n/help - راهنما\n\nاین ربات به شما کمک می‌کند:\n- پروفایل بسازید\n- افراد جدید پیدا کنید\n- با هوش مصنوعی چت کنید',
        'en': '📖 Help Guide:\n\n/start - Start the bot\n/menu - Main menu\n/help - This help message\n\nThis bot helps you:\n- Create your profile\n- Find new people\n- Chat with AI assistant',
        'sv': '📖 Hjälp:\n\n/start - Starta boten\n/menu - Huvudmeny\n/help - Denna hjälp',
        'de': '📖 Hilfe:\n\n/start - Bot starten\n/menu - Hauptmenü\n/help - Diese Hilfe',
        'tr': '📖 Yardım:\n\n/start - Botu başlat\n/menu - Ana menü\n/help - Bu yardım',
        'ar': '📖 المساعدة:\n\n/start - بدء البوت\n/menu - القائمة الرئيسية\n/help - هذه المساعدة',
        'fr': '📖 Aide:\n\n/start - Démarrer le bot\n/menu - Menu principal\n/help - Cette aide',
        'es': '📖 Ayuda:\n\n/start - Iniciar el bot\n/menu - Menú principal\n/help - Esta ayuda',
        'ku': '📖 یارمەتی:\n\n/start - دەستپێکردن\n/menu - لیستی سەرەکی\n/help - ئەم یارمەتییە',
    }
    
    await update.message.reply_text(
        help_text.get(lang, help_text['en']),
        reply_markup=_get_main_menu_buttons(lang)
    )


def _get_main_menu_buttons(lang: str) -> InlineKeyboardMarkup:
    """Get main menu inline keyboard."""
    buttons = [
        [InlineKeyboardButton('🧠 ' + get_text(lang, 'personality_test') if 'personality_test' in locals() else '🧠 Personality Test', callback_data='personality_test')],
        [InlineKeyboardButton('📅 ' + get_text(lang, 'date_history') if 'date_history' in locals() else '📅 Date History', callback_data='date_history')],
        [InlineKeyboardButton('🎯 ' + get_text(lang, 'relationship_modes') if 'relationship_modes' in locals() else '🎯 Relationship Modes', callback_data='relationship_modes')],
        [InlineKeyboardButton('🎓 Mode Coaching', callback_data='mode_coaching')],
        [InlineKeyboardButton(get_text(lang, 'browse_profiles'), callback_data='browse')],
        [InlineKeyboardButton(get_text(lang, 'my_matches'), callback_data='matches')],
        [InlineKeyboardButton(get_text(lang, 'ai_chat'), callback_data='ai_chat')],
        [InlineKeyboardButton('🛡️ ' + get_text(lang, 'safety_menu') if 'safety_menu' in locals() else '🛡️ Safety', callback_data='safety_menu')],
        [InlineKeyboardButton(get_text(lang, 'settings'), callback_data='settings')],
        [InlineKeyboardButton(get_text(lang, 'create_profile'), callback_data='edit_profile')],
    ]
    return InlineKeyboardMarkup(buttons)


def main():
    """Start the bot."""
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Build the application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for profile creation
    profile_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(language_selected, pattern='^lang_'),
            CallbackQueryHandler(show_settings, pattern='^edit_profile$'),
        ],
        states={
            SELECTING_LANGUAGE: [
                CallbackQueryHandler(language_selected, pattern='^lang_'),
            ],
            SELECTING_LANGUAGE_MANUAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_profile_input),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('menu', show_main_menu),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
        per_user=True,
    )
    
    # AI Chat conversation handler
    ai_chat_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_ai_chat, pattern='^ai_chat$'),
        ],
        states={
            AI_CHAT_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message),
                CallbackQueryHandler(exit_ai_chat, pattern='^back_to_menu$'),
            ],
        },
        fallbacks=[
            CommandHandler('menu', show_main_menu),
            CallbackQueryHandler(exit_ai_chat, pattern='^back_to_menu$'),
        ],
        per_user=True,
    )
    
    # Settings conversation handler
    settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_settings, pattern='^settings$'),
        ],
        states={
            # Settings menu is handled by the callback handler
            SET_AGE_RANGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference_input),
            ],
            SET_DISTANCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference_input),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_settings, pattern='^cancel_settings$'),
        ],
        per_user=True,
    )
    
    # Safety conversation handler
    safety_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_safety_menu, pattern='^safety_menu$'),
        ],
        states={
            SAFETY_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_secret_friend_input),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(show_safety_menu, pattern='^safety_menu$'),
        ],
        per_user=True,
    )
    
    # Personality Test conversation handler
    personality_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_personality_test, pattern='^personality_test$'),
        ],
        states={
            MBTI_Q1: [
                CallbackQueryHandler(handle_mbti_question, pattern='^mbti_'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(start_personality_test, pattern='^personality_test$'),
        ],
        per_user=True,
    )
    
    # Date History conversation handler
    date_history_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_date_history, pattern='^date_history$'),
            CallbackQueryHandler(start_add_date, pattern='^add_date$'),
        ],
        states={
            0: [  # Date type selection
                CallbackQueryHandler(handle_date_type, pattern='^date_type_'),
            ],
            1: [  # Text inputs (location, date, ratings, etc.)
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input),
            ],
            2: [  # Outcome selection
                CallbackQueryHandler(handle_outcome, pattern='^outcome_'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(show_date_history, pattern='^date_history$'),
        ],
        per_user=True,
    )
    
    # Relationship Modes conversation handler
    relationship_modes_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_relationship_modes, pattern='^relationship_modes$'),
        ],
        states={
            0: [  # Mode selection
                CallbackQueryHandler(select_relationship_mode, pattern='^rel_mode_'),
            ],
            1: [  # Connection test questions
                CallbackQueryHandler(run_connection_test, pattern='^connection_test_'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(show_relationship_modes, pattern='^relationship_modes$'),
        ],
        per_user=True,
    )
    
    # Mode Coaching conversation handler
    mode_coaching_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_mode_coaching, pattern='^mode_coaching$'),
        ],
        states={
            0: [  # Topic selection
                CallbackQueryHandler(handle_coaching_topic, pattern='^coach_topic_'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(start_mode_coaching, pattern='^mode_coaching$'),
        ],
        per_user=True,
    )
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('menu', show_main_menu))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('safety', lambda update, context: update.message.reply_text(
        "🛡️ Use the main menu to access safety features",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ Safety", callback_data='safety_menu')]])
    )))
    
    # Add conversation handlers
    app.add_handler(profile_conv)
    app.add_handler(ai_chat_conv)
    app.add_handler(settings_conv)
    app.add_handler(safety_conv)
    app.add_handler(personality_conv)
    app.add_handler(date_history_conv)
    app.add_handler(relationship_modes_conv)
    app.add_handler(mode_coaching_conv)
    
    # Central callback handler (for non-conversation callbacks)
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Safety callback handler (high priority - matches all safety_ patterns)
    app.add_handler(CallbackQueryHandler(safety_callback_router, pattern='^safety_'))
    
    # Start the bot
    logger.info("Bot is starting...")
    logger.info(f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.values())}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
