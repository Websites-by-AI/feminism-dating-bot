"""Start command and language selection handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User
from languages import get_text, SUPPORTED_LANGUAGES, detect_language_from_text
from config import DEFAULT_LANGUAGE
import logging

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_LANGUAGE, SELECTING_LANGUAGE_MANUAL = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - welcome and language selection."""
    user = update.effective_user
    telegram_id = user.id
    
    # Get or create user in database
    db = get_session()
    try:
        db_user = db.query(User).filter_by(telegram_id=telegram_id).first()
        
        if not db_user:
            # New user - create with default language
            db_user = User(
                telegram_id=telegram_id,
                username=user.username,
                first_name=user.first_name,
                language=DEFAULT_LANGUAGE
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Send welcome banner image
            try:
                with open('welcome_banner.png', 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption="🌹 Welcome to Feminism AI Dating Bot!"
                    )
            except:
                pass  # Continue even if image fails
            
            # Show welcome and language selection
            await _show_language_selection(update, db_user.language)
            return SELECTING_LANGUAGE
        else:
            # Existing user
            db_user.last_active = __import__('datetime').datetime.utcnow()
            db.commit()
            
            # If profile is not complete, ask to complete it
            if not db_user.profile_complete:
                lang = db_user.language
                await update.message.reply_text(
                    get_text(lang, 'welcome') + "\n\n" + get_text(lang, 'must_complete_profile'),
                    reply_markup=_get_main_menu_buttons(lang)
                )
                return ConversationHandler.END
            else:
                # Show main menu
                await _show_main_menu(update, db_user.language)
                return ConversationHandler.END
    finally:
        db.close()


async def _show_language_selection(update: Update, current_lang: str):
    """Show language selection buttons."""
    buttons = []
    for code, name in SUPPORTED_LANGUAGES.items():
        buttons.append([InlineKeyboardButton(
            f"{'✅ ' if code == current_lang else ''}{name}",
            callback_data=f"lang_{code}"
        )])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        get_text(current_lang, 'welcome') + "\n\n" + get_text(current_lang, 'select_language'),
        reply_markup=keyboard
    )


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace('lang_', '')
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if user:
            user.language = lang_code
            db.commit()
        
        await query.edit_message_text(
            get_text(lang_code, 'language_selected') + "\n\n" + get_text(lang_code, 'must_complete_profile')
        )
        
        # Now start profile creation
        context.user_data['step'] = 'name'
        await query.message.reply_text(
            get_text(lang_code, 'ask_name'),
            reply_markup=_get_cancel_button(lang_code)
        )
        return SELECTING_LANGUAGE_MANUAL
    finally:
        db.close()


async def handle_profile_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile creation step by step."""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(DEFAULT_LANGUAGE, 'error'))
            return ConversationHandler.END
        
        lang = user.language
        step = context.user_data.get('step', 'name')
        text = update.message.text
        
        # Detect language from text if not set
        if not user.language or user.language == DEFAULT_LANGUAGE:
            detected = detect_language_from_text(text)
            # Only update if we're still in language selection phase
            if step == 'name' and detected != 'en':
                user.language = detected
                lang = detected
                context.user_data['step'] = 'name'
        
        if step == 'name':
            user.name = text.strip()
            user.language = lang  # Update with detected language
            db.commit()
            
            context.user_data['step'] = 'age'
            await update.message.reply_text(
                get_text(lang, 'ask_age'),
                reply_markup=_get_cancel_button(lang)
            )
            
        elif step == 'age':
            try:
                age = int(text)
                if 18 <= age <= 100:
                    user.age = age
                    db.commit()
                    
                    context.user_data['step'] = 'gender'
                    await update.message.reply_text(
                        get_text(lang, 'ask_gender'),
                        reply_markup=_get_gender_buttons(lang)
                    )
                else:
                    await update.message.reply_text(get_text(lang, 'invalid_age'))
            except ValueError:
                await update.message.reply_text(get_text(lang, 'invalid_age'))
        
        elif step == 'gender':
            if text in ['male', 'female', 'other']:
                user.gender = text
                db.commit()
                
                context.user_data['step'] = 'looking_for'
                await update.message.reply_text(
                    get_text(lang, 'ask_looking_for'),
                    reply_markup=_get_looking_for_buttons(lang)
                )
        
        elif step == 'looking_for':
            if text in ['male', 'female', 'anyone']:
                user.looking_for = text
                db.commit()
                
                context.user_data['step'] = 'bio'
                await update.message.reply_text(
                    get_text(lang, 'ask_bio'),
                    reply_markup=_get_skip_button(lang)
                )
        
        elif step == 'bio':
            user.bio = text.strip()[:500]
            db.commit()
            
            context.user_data['step'] = 'city'
            await update.message.reply_text(
                get_text(lang, 'ask_city'),
                reply_markup=_get_skip_button(lang)
            )
        
        elif step == 'city':
            user.city = text.strip()
            user.profile_complete = True
            db.commit()
            
            await update.message.reply_text(
                get_text(lang, 'profile_complete'),
                reply_markup=_get_main_menu_buttons(lang)
            )
            return ConversationHandler.END
        
    finally:
        db.close()
    
    return SELECTING_LANGUAGE_MANUAL


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current conversation."""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else DEFAULT_LANGUAGE
    finally:
        db.close()
    
    context.user_data.clear()
    await update.message.reply_text(
        get_text(lang, 'cancel'),
        reply_markup=_get_main_menu_buttons(lang)
    )
    return ConversationHandler.END


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu."""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if user:
            await _show_main_menu(update, user.language)
    finally:
        db.close()


async def _show_main_menu(update: Update, lang: str):
    """Display main menu with buttons."""
    await update.message.reply_text(
        get_text(lang, 'main_menu'),
        reply_markup=_get_main_menu_buttons(lang)
    )


def _get_main_menu_buttons(lang: str) -> InlineKeyboardMarkup:
    """Get main menu inline keyboard."""
    buttons = [
        [InlineKeyboardButton(get_text(lang, 'browse_profiles'), callback_data='browse')],
        [InlineKeyboardButton(get_text(lang, 'my_matches'), callback_data='matches')],
        [InlineKeyboardButton(get_text(lang, 'ai_chat'), callback_data='ai_chat')],
        [InlineKeyboardButton('🛡️ Safety', callback_data='safety_menu')],  # NEW: Safety button
        [InlineKeyboardButton(get_text(lang, 'settings'), callback_data='settings')],
        [InlineKeyboardButton(get_text(lang, 'create_profile'), callback_data='edit_profile')],
    ]
    return InlineKeyboardMarkup(buttons)


def _get_gender_buttons(lang: str) -> InlineKeyboardMarkup:
    """Get gender selection buttons."""
    buttons = [
        [
            InlineKeyboardButton(get_text(lang, 'male'), callback_data='gender_male'),
            InlineKeyboardButton(get_text(lang, 'female'), callback_data='gender_female'),
        ],
        [InlineKeyboardButton(get_text(lang, 'other'), callback_data='gender_other')],
    ]
    return InlineKeyboardMarkup(buttons)


def _get_looking_for_buttons(lang: str) -> InlineKeyboardMarkup:
    """Get looking for selection buttons."""
    buttons = [
        [
            InlineKeyboardButton(get_text(lang, 'male'), callback_data='looking_male'),
            InlineKeyboardButton(get_text(lang, 'female'), callback_data='looking_female'),
        ],
        [InlineKeyboardButton(get_text(lang, 'other'), callback_data='looking_anyone')],
    ]
    return InlineKeyboardMarkup(buttons)


def _get_cancel_button(lang: str) -> InlineKeyboardMarkup:
    """Get cancel button."""
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, 'cancel'), callback_data='cancel')]])


def _get_skip_button(lang: str) -> InlineKeyboardMarkup:
    """Get skip button."""
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, 'skip'), callback_data='skip')]])
