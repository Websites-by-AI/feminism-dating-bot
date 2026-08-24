"""Settings handler - user preferences and account management"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User
from languages import get_text, SUPPORTED_LANGUAGES
import logging

logger = logging.getLogger(__name__)

# States
SETTINGS_MENU, CHANGE_LANG, CHANGE_PREFS, SET_AGE_RANGE, SET_DISTANCE = range(5)


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu."""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        
        buttons = [
            [InlineKeyboardButton(get_text(lang, 'change_language'), callback_data='set_change_lang')],
            [InlineKeyboardButton(get_text(lang, 'change_preferences'), callback_data='set_change_prefs')],
            [InlineKeyboardButton(
                get_text(lang, 'deactivate') if user.is_active else get_text(lang, 'activate'),
                callback_data='set_toggle_active'
            )],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            get_text(lang, 'settings_menu'),
            reply_markup=keyboard
        )
        
    finally:
        db.close()


async def handle_settings_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings menu actions."""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        data = query.data
        
        if data == 'set_change_lang':
            # Show language selection
            buttons = []
            for code, name in SUPPORTED_LANGUAGES.items():
                buttons.append([InlineKeyboardButton(
                    f"{'✅ ' if code == lang else ''}{name}",
                    callback_data=f'set_lang_{code}'
                )])
            buttons.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='settings')])
            
            await query.edit_message_text(
                get_text(lang, 'select_language'),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            
        elif data.startswith('set_lang_'):
            new_lang = data.replace('set_lang_', '')
            user.language = new_lang
            db.commit()
            
            await query.edit_message_text(
                get_text(new_lang, 'language_selected'),
                reply_markup=_get_settings_back_button(new_lang)
            )
            
        elif data == 'set_change_prefs':
            # Show preferences
            prefs_text = (
                get_text(lang, 'change_preferences') + "\n\n"
                f"{get_text(lang, 'age_range')} {user.age_min or 18} - {user.age_max or 40}\n"
                f"{get_text(lang, 'max_distance')} {user.max_distance_km or 50} km"
            )
            
            buttons = [
                [InlineKeyboardButton(get_text(lang, 'age_range'), callback_data='set_age_range')],
                [InlineKeyboardButton(get_text(lang, 'max_distance'), callback_data='set_distance')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='settings')],
            ]
            
            await query.edit_message_text(
                prefs_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            
        elif data == 'set_toggle_active':
            user.is_active = not user.is_active
            db.commit()
            
            if user.is_active:
                msg = get_text(lang, 'account_activated')
            else:
                msg = get_text(lang, 'account_deactivated')
            
            await query.edit_message_text(msg, reply_markup=_get_settings_back_button(lang))
            
        elif data == 'set_age_range':
            context.user_data['setting'] = 'age_range'
            await query.edit_message_text(
                f"{get_text(lang, 'age_range')}\n\nCurrent: {user.age_min or 18} - {user.age_max or 40}\n\nPlease enter min age (e.g., 20):",
                reply_markup=_get_cancel_settings_button(lang)
            )
            return SET_AGE_RANGE
            
        elif data == 'set_distance':
            context.user_data['setting'] = 'distance'
            await query.edit_message_text(
                f"{get_text(lang, 'max_distance')}\n\nCurrent: {user.max_distance_km or 50} km\n\nPlease enter max distance in km:",
                reply_markup=_get_cancel_settings_button(lang)
            )
            return SET_DISTANCE
        
    finally:
        db.close()


async def handle_preference_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle preference input (age range, distance)."""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        setting = context.user_data.get('setting')
        text = update.message.text
        
        try:
            value = int(text)
        except ValueError:
            await update.message.reply_text(get_text(lang, 'invalid_input'))
            return SET_AGE_RANGE if setting == 'age_range' else SET_DISTANCE
        
        if setting == 'age_range':
            if 'age_min' not in context.user_data:
                context.user_data['age_min'] = value
                await update.message.reply_text("Now enter max age:")
                return SET_AGE_RANGE
            else:
                user.age_min = context.user_data['age_min']
                user.age_max = value
                db.commit()
                
                context.user_data.pop('age_min', None)
                await update.message.reply_text(
                    f"✅ {get_text(lang, 'age_range')} {user.age_min} - {user.age_max}",
                    reply_markup=_get_settings_back_button(lang)
                )
                return ConversationHandler.END
                
        elif setting == 'distance':
            user.max_distance_km = value
            db.commit()
            
            await update.message.reply_text(
                f"✅ {get_text(lang, 'max_distance')} {value} km",
                reply_markup=_get_settings_back_button(lang)
            )
            return ConversationHandler.END
        
    finally:
        db.close()


async def cancel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel settings change."""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language if user else 'en'
    finally:
        db.close()
    
    await query.edit_message_text(
        get_text(lang, 'settings_menu'),
        reply_markup=_get_settings_back_button(lang)
    )
    return ConversationHandler.END


def _get_settings_back_button(lang: str) -> InlineKeyboardMarkup:
    """Get back to settings button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, 'settings'), callback_data='settings')
    ]])


def _get_cancel_settings_button(lang: str) -> InlineKeyboardMarkup:
    """Get cancel settings button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, 'cancel'), callback_data='cancel_settings')
    ]])
