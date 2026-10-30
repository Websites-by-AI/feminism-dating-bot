"""
Enhanced Safety Features Handler
Bumble-inspired: Private Detector, Low-effort flags
Hinge-inspired: "Are You Sure?" nudge, Hidden Words
Pure-inspired: Screenshot blocking notification
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session, User, SafetySettings, ContentFilter
from languages import get_text
import logging

logger = logging.getLogger(__name__)


async def show_enhanced_safety(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show enhanced safety features menu"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return
        
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""🛡️ {get_text(lang, 'enhanced_safety_title')}

{get_text(lang, 'enhanced_safety_intro')}

🔹 {get_text(lang, 'private_detector')}
🔹 {get_text(lang, 'are_you_sure')}
🔹 {get_text(lang, 'hidden_words')}
🔹 {get_text(lang, 'low_effort_flag')}
🔹 {get_text(lang, 'screenshot_block')}"""
        
        buttons = [
            [InlineKeyboardButton(f"🔍 {get_text(lang, 'private_detector')}", callback_data='safety_private_detector')],
            [InlineKeyboardButton(f"⚠️ {get_text(lang, 'are_you_sure')}", callback_data='safety_are_you_sure')],
            [InlineKeyboardButton(f"🚫 {get_text(lang, 'hidden_words')}", callback_data='safety_hidden_words')],
            [InlineKeyboardButton(f"📉 {get_text(lang, 'low_effort_flag')}", callback_data='safety_low_effort')],
            [InlineKeyboardButton(f"📸 {get_text(lang, 'screenshot_block')}", callback_data='safety_screenshot')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def setup_hidden_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setup hidden words filter (like Hinge)"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Get existing filters
        filters = db.query(ContentFilter).filter_by(user_id=user.id).all()
        
        text = f"🚫 {get_text(lang, 'hidden_words_info')}\n\n"
        
        if filters:
            text += f"{get_text(lang, 'current_filters')}:\n"
            for f in filters:
                text += f"• {f.word}\n"
            text += "\n"
        
        text += get_text(lang, 'add_new_filter')
        
        buttons = [
            [InlineKeyboardButton(f"➕ {get_text(lang, 'add_word')}", callback_data='add_hidden_word')],
            [InlineKeyboardButton(f"🗑️ {get_text(lang, 'clear_all')}", callback_data='clear_hidden_words')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='enhanced_safety')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def add_hidden_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new hidden word"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        text = f"✏️ {get_text(lang, 'enter_word_to_block')}\n\n{get_text(lang, 'example_words')}: 'hey', 'hi', '🔥', '😍'"
        
        context.user_data['adding_hidden_word'] = True
        await query.edit_message_text(text)
        
    finally:
        db.close()


async def handle_hidden_word_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hidden word input"""
    if not context.user_data.get('adding_hidden_word'):
        return False
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        
        word = update.message.text.strip().lower()
        
        # Add filter
        existing = db.query(ContentFilter).filter_by(user_id=user.id, word=word).first()
        if not existing:
            new_filter = ContentFilter(user_id=user.id, word=word, filter_type='block')
            db.add(new_filter)
            db.commit()
        
        lang = user.language
        await update.message.reply_text(
            f"✅ '{word}' {get_text(lang, 'word_added')}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_hidden_words')
            ]])
        )
        
        del context.user_data['adding_hidden_word']
        return True
        
    finally:
        db.close()


async def clear_hidden_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all hidden word filters for the user"""
    query = update.callback_query
    await query.answer()
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if user:
            db.query(ContentFilter).filter_by(user_id=user.id).delete()
            db.commit()
    finally:
        db.close()
    await setup_hidden_words(update, context)

