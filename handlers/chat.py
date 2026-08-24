"""AI Chat handler - Dating assistant conversations"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, filters
from database import get_session, User, AIConversation
from languages import get_text
from ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

# Conversation state
AI_CHAT_STATE = 1


async def start_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start AI dating assistant chat."""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        
        await query.edit_message_text(
            get_text(lang, 'ai_assistant'),
            reply_markup=_get_ai_chat_buttons(lang)
        )
        
        context.user_data['in_ai_chat'] = True
        return AI_CHAT_STATE
        
    finally:
        db.close()


async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages in AI chat mode."""
    if not context.user_data.get('in_ai_chat'):
        return ConversationHandler.END
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        user_message = update.message.text
        
        # Check for exit commands
        if user_message.lower() in ['exit', 'quit', 'stop', 'back', '/menu']:
            context.user_data['in_ai_chat'] = False
            await update.message.reply_text(
                get_text(lang, 'main_menu'),
                reply_markup=_get_main_menu_buttons(lang)
            )
            return ConversationHandler.END
        
        # Show thinking indicator
        thinking_msg = await update.message.reply_text(get_text(lang, 'ai_thinking'))
        
        # Get user profile for context
        user_profile = {
            'name': user.name,
            'age': user.age,
            'city': user.city,
            'gender': user.gender,
            'bio': user.bio,
        }
        
        # Get AI response
        try:
            response = await ai_service.chat(
                user_id=user.id,
                message=user_message,
                language=lang,
                user_profile=user_profile
            )
            
            # Save conversation to database
            conv = AIConversation(
                user_id=user.id,
                role='user',
                content=user_message
            )
            db.add(conv)
            
            conv_ai = AIConversation(
                user_id=user.id,
                role='assistant',
                content=response
            )
            db.add(conv_ai)
            db.commit()
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            response = get_text(lang, 'error')
        
        # Delete thinking indicator and send response
        await thinking_msg.delete()
        await update.message.reply_text(
            response,
            reply_markup=_get_ai_chat_buttons(lang)
        )
        
    finally:
        db.close()
    
    return AI_CHAT_STATE


async def exit_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exit AI chat mode."""
    query = update.callback_query
    await query.answer()
    
    context.user_data['in_ai_chat'] = False
    ai_service.clear_history(query.from_user.id)
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language if user else 'en'
    finally:
        db.close()
    
    await query.edit_message_text(
        get_text(lang, 'main_menu'),
        reply_markup=_get_main_menu_buttons(lang)
    )
    return ConversationHandler.END


def _get_ai_chat_buttons(lang: str) -> InlineKeyboardMarkup:
    """Get AI chat action buttons."""
    buttons = [
        [
            InlineKeyboardButton("💬 " + get_text(lang, 'back'), callback_data='back_to_menu'),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def _get_main_menu_buttons(lang: str) -> InlineKeyboardMarkup:
    """Get main menu inline keyboard."""
    buttons = [
        [InlineKeyboardButton(get_text(lang, 'browse_profiles'), callback_data='browse')],
        [InlineKeyboardButton(get_text(lang, 'my_matches'), callback_data='matches')],
        [InlineKeyboardButton(get_text(lang, 'ai_chat'), callback_data='ai_chat')],
        [InlineKeyboardButton(get_text(lang, 'settings'), callback_data='settings')],
    ]
    return InlineKeyboardMarkup(buttons)
