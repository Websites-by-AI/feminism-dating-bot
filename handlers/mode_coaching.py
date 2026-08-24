"""
Mode-Specific AI Dating Coach
Provides tailored advice based on relationship mode
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User, RelationshipPreferences
from languages import get_text
from ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

# Conversation states
SELECT_COACHING_TOPIC, COACHING_RESPONSE = range(2)

# Mode-specific coaching topics
MODE_COACHING_TOPICS = {
    'serious': {
        'name': '💍 Serious Relationship',
        'topics': [
            '🗣️ How to build deep conversation',
            '💑 Signs of long-term compatibility',
            '🏡 Discussing future plans',
            '💕 Building trust and intimacy',
            '🎯 How to show commitment'
        ]
    },
    'casual': {
        'name': '🌸 Casual Dating',
        'topics': [
            '😊 Keeping things light and fun',
            '🎬 Creative date ideas',
            '💬 How to flirt without pressure',
            '🚩 Setting casual boundaries',
            '😄 Reading casual interest signals'
        ]
    },
    'one_night': {
        'name': '🔥 One Night',
        'topics': [
            '💬 How to chat confidently',
            '📍 How to find the right location',
            '🎯 Reading interest signals',
            '🔥 Building attraction quickly',
            '✅ Safety and consent tips'
        ]
    },
    'friendship': {
        'name': '👥 Friendship',
        'topics': [
            '🤝 Building platonic connection',
            '🎮 Fun friend activities',
            '💬 Deep friendship conversations',
            '🚫 Setting friendship boundaries',
            '🎉 Group social tips'
        ]
    },
    'marriage': {
        'name': '💒 Marriage',
        'topics': [
            '💍 Discussing marriage early',
            '🏠 Alignment on life goals',
            '💰 Financial compatibility talk',
            '👨‍👩‍👧 Family planning discussions',
            '🎯 Showing marriage readiness'
        ]
    },
    'open': {
        'name': '🌈 Open Relationship',
        'topics': [
            '💬 How to discuss ENM',
            '📋 Setting relationship rules',
            '🔒 Managing jealousy',
            '✅ Consent and boundaries',
            '🤝 Communication with multiple partners'
        ]
    },
    'emotional': {
        'name': '💝 Emotional Connection',
        'topics': [
            '💕 Deep emotional conversations',
            '🧠 Understanding attachment styles',
            '❤️ Building vulnerability',
            '🤗 Showing emotional availability',
            '🎯 Recognizing emotional compatibility'
        ]
    },
    'intellectual': {
        'name': '🧠 Intellectual Connection',
        'topics': [
            '💭 Stimulating conversations',
            '📚 Sharing intellectual interests',
            '🎭 Cultural discussion topics',
            '🧪 Debate and discussion tips',
            '🎯 Finding intellectual matches'
        ]
    }
}


async def start_mode_coaching(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start mode-specific coaching"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        # Get user's relationship mode
        rel_pref = db.query(RelationshipPreferences).filter_by(user_id=user.id).first()
        
        if not rel_pref:
            await query.edit_message_text(
                "❌ Please select a relationship mode first!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎯 Select Mode", callback_data='relationship_modes')
                ]])
            )
            return ConversationHandler.END
        
        mode = rel_pref.relationship_mode
        mode_data = MODE_COACHING_TOPICS.get(mode)
        
        if not mode_data:
            await query.edit_message_text(
                "❌ Mode not found!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
                ]])
            )
            return ConversationHandler.END
        
        # Show coaching topics
        buttons = []
        for i, topic in enumerate(mode_data['topics']):
            buttons.append([InlineKeyboardButton(topic, callback_data=f'coach_topic_{i}')])
        
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')])
        
        text = f"🎓 **{mode_data['name']} Coaching**\n\n"
        text += "What would you like to learn about?\n\n"
        text += "💡 I'll provide personalized advice based on your mode!"
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        context.user_data['coaching_mode'] = mode
        return SELECT_COACHING_TOPIC
        
    finally:
        db.close()


async def handle_coaching_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle selected coaching topic"""
    query = update.callback_query
    await query.answer()
    
    topic_index = int(query.data.replace('coach_topic_', ''))
    mode = context.user_data.get('coaching_mode')
    
    if not mode:
        await query.edit_message_text("❌ Mode not found!")
        return ConversationHandler.END
    
    mode_data = MODE_COACHING_TOPICS.get(mode)
    if not mode_data or topic_index >= len(mode_data['topics']):
        await query.edit_message_text("❌ Topic not found!")
        return ConversationHandler.END
    
    topic = mode_data['topics'][topic_index]
    
    # Generate AI coaching response
    coaching_prompt = f"""You are a professional dating coach specializing in {mode_data['name']} relationships.

The user wants to learn about: {topic}

Provide practical, actionable advice in 3-5 bullet points:
- Be specific and concrete
- Include real examples
- Focus on what TO DO (not just what not to do)
- Consider safety and consent
- Be encouraging and positive

Keep the response concise but valuable."""
    
    # Show loading message
    await query.edit_message_text(
        "🤖 Generating personalized coaching advice...\n\n"
        "💡 This may take a moment..."
    )
    
    try:
        # Get AI response using RAG
        db = get_session()
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language if user else 'en'
        
        response = await ai_service.chat(
            user_id=user.id,
            message=coaching_prompt,
            language=lang,
            user_profile={'name': user.name if user else 'User'}
        )
        
        db.close()
        
        # Format response
        formatted_response = f"🎓 **Coaching: {topic}**\n\n{response}\n\n"
        formatted_response += "💡 Want to learn more? Select another topic below!"
        
        # Show response with back to topics button
        buttons = []
        for i, t in enumerate(mode_data['topics']):
            if i != topic_index:  # Don't show current topic
                buttons.append([InlineKeyboardButton(t, callback_data=f'coach_topic_{i}')])
        
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')])
        
        await query.edit_message_text(
            formatted_response,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Coaching error: {e}")
        await query.edit_message_text(
            "❌ Sorry, I couldn't generate coaching advice right now.\n\n"
            "Please try again later!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')
            ]])
        )
    
    return SELECT_COACHING_TOPIC


# Add translations
COACHING_TRANSLATIONS = {
    'fa': {
        'coaching_menu': '🎓 مربیگری هوش مصنوعی',
        'select_topic': 'چه موضوعی را می‌خواهید یاد بگیرید؟',
        'generating': '🤖 در حال تولید مشاوره شخصی‌سازی شده...',
    },
    'en': {
        'coaching_menu': '🎓 AI Dating Coach',
        'select_topic': 'What would you like to learn about?',
        'generating': '🤖 Generating personalized coaching advice...',
    }
}
