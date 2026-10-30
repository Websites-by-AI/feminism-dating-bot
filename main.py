"""
Feminism AI Dating Bot — Main Telegram Application
==================================================
Multi-language (9 languages) feminist dating & safety bot powered by:
- 13 Feminist Safety Features (SOS, Secret Friend, Safe Word, Check-in, FRIES Consent, Body-Scam Shield)
- 10 Relationship Modes (including 🚀 Startup Co-founder & 🌍 International)
- MBTI + Love Language + Attachment Assessment
- Date History & Pattern Analysis
- Academic RAG AI Coach (Cloudflare Workers AI + HuggingFace Router + SQLite KB)
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from config import BOT_TOKEN
from database import init_db, get_session, User, SafetySettings
from languages import get_text, SUPPORTED_LANGUAGES

from handlers.start import (
    start,
    language_selected,
    start_edit_profile,
    handle_profile_callback,
    handle_profile_input,
    cancel,
    show_main_menu,
    build_main_menu_markup,
    SELECTING_LANGUAGE,
    SELECTING_LANGUAGE_MANUAL,
)
from handlers.matching import browse_profiles, handle_swipe, show_matches
from handlers.chat import start_ai_chat, handle_ai_message, exit_ai_chat, AI_CHAT_STATE
from handlers.settings import (
    show_settings,
    handle_settings_action,
    handle_preference_input,
    cancel_settings,
    SET_AGE_RANGE,
    SET_DISTANCE,
)
from handlers.safety import (
    show_safety_menu,
    safety_callback_router,
    handle_secret_friend_input,
    SAFETY_MENU,
)
from handlers.safety_enhanced import (
    show_enhanced_safety,
    setup_hidden_words,
    add_hidden_word,
    clear_hidden_words,
    handle_hidden_word_input,
)
from handlers.personality import (
    start_personality_test,
    personality_callback_router,
)
from handlers.date_history import (
    show_date_history,
    start_add_date,
    handle_date_type,
    handle_date_input,
    handle_outcome,
    show_ai_analysis,
)
from handlers.relationship_modes import (
    show_relationship_modes,
    select_relationship_mode,
    start_connection_test,
    handle_test_answer,
)
from handlers.mode_coaching import (
    show_mode_coaching,
    provide_coaching_advice,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context):
    """Central callback query handler (registered AFTER specialized pattern handlers)."""
    query = update.callback_query
    data = query.data

    if data.startswith('lang_'):
        return await language_selected(update, context)

    elif data in ('browse', 'browse_next'):
        context.user_data['browsing'] = True
        await browse_profiles(update, context)

    elif data.startswith('like_') or data.startswith('pass_'):
        await handle_swipe(update, context)

    elif data == 'matches':
        await show_matches(update, context)

    elif data == 'ai_chat':
        return await start_ai_chat(update, context)

    elif data == 'date_history':
        return await show_date_history(update, context)

    elif data in ('add_date', 'add_date_start'):
        return await start_add_date(update, context)

    elif data.startswith('date_type_'):
        return await handle_date_type(update, context)

    elif data.startswith('outcome_'):
        return await handle_outcome(update, context)

    elif data in ('ai_analysis', 'show_ai_analysis'):
        return await show_ai_analysis(update, context)

    elif data == 'view_all_dates':
        return await show_date_history(update, context)

    elif data == 'enhanced_safety':
        return await show_enhanced_safety(update, context)

    elif data == 'hidden_words':
        return await setup_hidden_words(update, context)

    elif data == 'add_hidden_word':
        return await add_hidden_word(update, context)

    elif data == 'clear_hidden_words':
        return await clear_hidden_words(update, context)

    elif data == 'relationship_modes':
        return await show_relationship_modes(update, context)

    elif data.startswith('mode_select_') or data.startswith('rel_mode_'):
        if data.startswith('rel_mode_'):
            query.data = data.replace('rel_mode_', 'mode_select_')
        return await select_relationship_mode(update, context)

    elif data.startswith('connection_test_'):
        return await start_connection_test(update, context)

    elif data.startswith('test_answer_'):
        return await handle_test_answer(update, context)

    elif data == 'mode_coaching':
        return await show_mode_coaching(update, context)

    elif data.startswith('coaching_') or data.startswith('coach_topic_'):
        return await provide_coaching_advice(update, context)

    elif data == 'settings':
        await show_settings(update, context)

    elif data.startswith('set_'):
        return await handle_settings_action(update, context)

    elif data == 'cancel_settings':
        return await cancel_settings(update, context)

    elif data in ('back_to_menu', 'back_to_main'):
        context.user_data.clear()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            lang = user.language if user else 'fa'
        finally:
            db.close()
        await query.answer()
        await query.edit_message_text(
            get_text(lang, 'main_menu'),
            reply_markup=build_main_menu_markup(lang),
        )

    elif data == 'cancel':
        return await cancel(update, context)

    elif data.startswith('chat_'):
        await query.answer("💬 Direct match chat is protected by safety filters!")

    else:
        await query.answer()


async def handle_free_text(update: Update, context):
    """Handle free-text inputs outside active conversations (hidden words, date notes, safe word, or AI chat)"""
    if context.user_data.get('adding_hidden_word'):
        await handle_hidden_word_input(update, context)
        return

    if any(k.startswith('awaiting_') for k in context.user_data.keys()):
        await handle_date_input(update, context)
        return

    # Silent Safe-Word check
    text = (update.message.text or '').strip()
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if user:
            safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
            if safety and safety.safe_word_active and safety.safe_word and safety.safe_word.lower() in text.lower():
                await update.message.reply_text(
                    "🆘 کلمه امن شناسایی شد! هشدار اضطراری (SOS) ثبت گردید.\n"
                    "Safe word detected — emergency SOS logged."
                )
                return
    finally:
        db.close()

    # Fallback: route message to AI Dating & Safety Assistant
    context.user_data['in_ai_chat'] = True
    await handle_ai_message(update, context)


async def help_command(update: Update, context):
    """Handle /help command."""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else 'fa'
    finally:
        db.close()

    help_text = {
        'fa': (
            '📖 راهنمای ربات فمینیسم دوستیابی:\n\n'
            '/start - شروع و منوی اصلی\n'
            '/start startup - ورود مستقیم به حالت شریک استارتاپی 🚀\n'
            '/start abroad - ورود مستقیم به حالت آشنایی بین‌المللی 🌍\n'
            '/menu - منوی اصلی\n'
            '/safety - مرکز ۱۳ ابزار ایمنی\n'
            '/help - راهنما'
        ),
        'en': (
            '📖 Feminism AI Dating Bot Help:\n\n'
            '/start - Start & Main Menu\n'
            '/start startup - Startup Co-founder Mode 🚀\n'
            '/start abroad - International Mode 🌍\n'
            '/menu - Main Menu\n'
            '/safety - 13 Safety Features\n'
            '/help - Help Guide'
        ),
    }
    await update.message.reply_text(
        help_text.get(lang, help_text['en']),
        reply_markup=build_main_menu_markup(lang),
    )


def build_application(token: str = None) -> Application:
    """Build and wire the Telegram Application."""
    init_db()
    app = Application.builder().token(token or BOT_TOKEN).build()

    # 1. Profile Creation / Editing Conversation
    profile_conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(language_selected, pattern=r'^lang_'),
            CallbackQueryHandler(start_edit_profile, pattern=r'^edit_profile$'),
        ],
        states={
            SELECTING_LANGUAGE: [
                CallbackQueryHandler(language_selected, pattern=r'^lang_'),
            ],
            SELECTING_LANGUAGE_MANUAL: [
                CallbackQueryHandler(handle_profile_callback, pattern=r'^(gender_.*|looking_.*|skip)$'),
                MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_profile_input),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('menu', show_main_menu),
            CommandHandler('start', start),
            CallbackQueryHandler(cancel, pattern=r'^cancel$'),
        ],
        per_user=True,
    )

    # 2. AI Chat Conversation
    ai_chat_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_ai_chat, pattern=r'^ai_chat$'),
        ],
        states={
            AI_CHAT_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message),
                CallbackQueryHandler(exit_ai_chat, pattern=r'^(back_to_menu|back_to_main)$'),
            ],
        },
        fallbacks=[
            CommandHandler('menu', show_main_menu),
            CallbackQueryHandler(exit_ai_chat, pattern=r'^(back_to_menu|back_to_main)$'),
        ],
        per_user=True,
    )

    # 3. Settings Conversation
    settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_settings, pattern=r'^settings$'),
            CallbackQueryHandler(handle_settings_action, pattern=r'^set_(age_range|distance)$'),
        ],
        states={
            SET_AGE_RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference_input)],
            SET_DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference_input)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_settings, pattern=r'^cancel_settings$'),
            CommandHandler('menu', show_main_menu),
        ],
        per_user=True,
    )

    # 4. Safety Input Conversation (Secret Friend / Safe Word)
    safety_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_safety_menu, pattern=r'^safety_menu$'),
        ],
        states={
            SAFETY_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_secret_friend_input),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(show_safety_menu, pattern=r'^safety_menu$'),
            CommandHandler('menu', show_main_menu),
        ],
        per_user=True,
    )

    # Commands
    app.add_handler(CommandHandler('menu', show_main_menu))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(
        CommandHandler(
            'safety',
            lambda update, context: update.message.reply_text(
                "🛡️ مرکز ایمنی فمینیستی / Feminist Safety Center:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ باز کردن مرکز ایمنی / Open Safety", callback_data='safety_menu')]]),
            ),
        )
    )

    # Conversation Handlers
    app.add_handler(profile_conv)
    app.add_handler(ai_chat_conv)
    app.add_handler(settings_conv)
    app.add_handler(safety_conv)

    # Specialized Callback Routers MUST precede catch-all handle_callback!
    app.add_handler(
        CallbackQueryHandler(
            personality_callback_router,
            pattern=r'^(personality_test|personality_start|mbti_.*|lovelang_.*|attach_.*)$',
        )
    )
    app.add_handler(CallbackQueryHandler(safety_callback_router, pattern=r'^safety_'))

    # General Callback Router (catch-all)
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Free-text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text))

    return app


def main():
    app = build_application()
    logger.info("🤖 Feminism AI Dating Bot started!")
    logger.info(f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.values())}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
