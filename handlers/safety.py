"""
Feminism-Focused Safety System
===============================
Based on academic research:
- Gillett (2023): Women's safety work on dating apps
- Doria (2023): Dating app-facilitated sexualized violence  
- Amirkhani et al. (2024): Online romance scams & "body scam" in Iran
- Thompson (2018): Missing discourse of consent on dating apps
- Bicharanlou & Siasirad (2017): Iranian women's online privacy

Features:
1. Secret Friend / Trusted Contact System
2. Mutual Safety Buddy System
3. Automated Check-in During Dates
4. Panic Button / SOS Alert
5. Safe Word System
6. Photo Verification
7. Privacy Protection (Iran-context aware)
8. Consent Education & Tracking
9. Block/Report System
10. Sextortion Protection (Body Scam awareness)
11. Date Safety Planning
12. Emergency Exit Strategy
13. Safety Score System
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User, SafetySettings, SOSAlert, SafetyReport, SafetyCheckIn
from languages import get_text
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Conversation states
SAFETY_MENU = 100
SECRET_FRIEND_SETUP = 101
SAFE_WORD_SETUP = 102
PRIVACY_SETTINGS = 103


async def show_safety_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main safety menu"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        if not safety:
            safety = SafetySettings(user_id=user.id)
            db.add(safety)
            db.commit()
            db.refresh(safety)
        
        # Build safety status summary
        active_features = []
        if safety.secret_friend_active:
            active_features.append("✅ " + get_text(lang, 'safety_secret_friend'))
        if safety.mutual_safety_active:
            active_features.append("✅ " + get_text(lang, 'safety_mutual_buddy'))
        if safety.auto_checkin_enabled:
            active_features.append("✅ " + get_text(lang, 'safety_auto_checkin'))
        if safety.sos_enabled:
            active_features.append("✅ " + get_text(lang, 'safety_sos'))
        if safety.safe_word_active:
            active_features.append("✅ " + get_text(lang, 'safety_safe_word'))
        if safety.photo_verified:
            active_features.append("✅ " + get_text(lang, 'safety_photo_verified'))
        if safety.anonymous_mode:
            active_features.append("✅ " + get_text(lang, 'safety_anonymous'))
        
        status_text = "\n".join(active_features) if active_features else get_text(lang, 'safety_no_features_active')
        
        text = f"{get_text(lang, 'safety_menu_header')}\n\n{get_text(lang, 'safety_status')}\n{status_text}\n\n{get_text(lang, 'safety_score')}: {safety.safety_score:.0f}/100"
        
        buttons = [
            [InlineKeyboardButton(f"🤝 {get_text(lang, 'safety_secret_friend')}", callback_data='safety_secret_friend')],
            [InlineKeyboardButton(f"👥 {get_text(lang, 'safety_mutual_buddy')}", callback_data='safety_mutual_buddy')],
            [InlineKeyboardButton(f"⏰ {get_text(lang, 'safety_auto_checkin')}", callback_data='safety_checkin')],
            [InlineKeyboardButton(f"🆘 {get_text(lang, 'safety_sos')}", callback_data='safety_sos')],
            [InlineKeyboardButton(f"🔐 {get_text(lang, 'safety_safe_word')}", callback_data='safety_safe_word')],
            [InlineKeyboardButton(f"📸 {get_text(lang, 'safety_photo_verify')}", callback_data='safety_photo_verify')],
            [InlineKeyboardButton(f"🛡️ {get_text(lang, 'safety_privacy')}", callback_data='safety_privacy')],
            [InlineKeyboardButton(f"💬 {get_text(lang, 'safety_consent')}", callback_data='safety_consent')],
            [InlineKeyboardButton(f"🚫 {get_text(lang, 'safety_block_report')}", callback_data='safety_block_report')],
            [InlineKeyboardButton(f"⚠️ {get_text(lang, 'safety_sextortion')}", callback_data='safety_sextortion')],
            [InlineKeyboardButton(f"📍 {get_text(lang, 'safety_date_plan')}", callback_data='safety_date_plan')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 1. SECRET FRIEND / TRUSTED CONTACT SYSTEM
# ============================================================
# Based on: Women need someone to know their location/date details (Gillett 2023)

async def setup_secret_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up a trusted contact who receives safety notifications"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""{get_text(lang, 'safety_secret_friend_info')}

{get_text(lang, 'safety_secret_friend_what')}
• 📍 {get_text(lang, 'safety_secret_friend_location')}
• ⏰ {get_text(lang, 'safety_secret_friend_time')}
• 🆘 {get_text(lang, 'safety_secret_friend_emergency')}

{get_text(lang, 'safety_secret_friend_how')}
"""
        
        if safety.secret_friend_telegram_id:
            text += f"\n✅ {get_text(lang, 'safety_secret_friend_current')}: {safety.secret_friend_name or 'Unknown'}"
            buttons = [
                [InlineKeyboardButton(f"✏️ {get_text(lang, 'safety_change')}", callback_data='safety_sf_change')],
                [InlineKeyboardButton(f"{'❌' if safety.secret_friend_active else '✅'} {get_text(lang, 'safety_toggle')}", callback_data='safety_sf_toggle')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
            ]
        else:
            text += f"\n\n{get_text(lang, 'safety_secret_friend_enter')}"
            buttons = [
                [InlineKeyboardButton(get_text(lang, 'safety_secret_friend_add'), callback_data='safety_sf_add')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
            ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=keyboard)
        
        return SAFETY_MENU
        
    finally:
        db.close()


async def handle_secret_friend_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle secret friend telegram ID input"""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = update.message.text.strip()
        
        # Try to parse Telegram ID or username
        if text.startswith('@'):
            # Username - we'll store it as name for now
            safety.secret_friend_name = text
            safety.secret_friend_active = True
            db.commit()
            
            await update.message.reply_text(
                f"✅ {get_text(lang, 'safety_secret_friend_added')}: {text}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'safety_menu'), callback_data='safety_menu')
                ]])
            )
        elif text.isdigit():
            # Numeric Telegram ID
            safety.secret_friend_telegram_id = int(text)
            safety.secret_friend_active = True
            db.commit()
            
            await update.message.reply_text(
                f"✅ {get_text(lang, 'safety_secret_friend_added')}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'safety_menu'), callback_data='safety_menu')
                ]])
            )
        else:
            await update.message.reply_text(
                f"❌ {get_text(lang, 'safety_invalid_input')}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_secret_friend')
                ]])
            )
        
        return ConversationHandler.END
        
    finally:
        db.close()


async def toggle_secret_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle secret friend on/off"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        safety.secret_friend_active = not safety.secret_friend_active
        db.commit()
        
        status = get_text(user.language, 'safety_activated') if safety.secret_friend_active else get_text(user.language, 'safety_deactivated')
        await query.answer(f"{status}!", show_alert=True)
        
        await setup_secret_friend(update, context)
        
    finally:
        db.close()


# ============================================================
# 2. MUTUAL SAFETY BUDDY SYSTEM
# ============================================================
# Women can request each other to activate safety features mutually

async def setup_mutual_buddy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up mutual safety buddy with another woman"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""{get_text(lang, 'safety_mutual_buddy_info')}

{get_text(lang, 'safety_mutual_buddy_what')}
• 👥 {get_text(lang, 'safety_mutual_buddy_both')}
• 🔔 {get_text(lang, 'safety_mutual_buddy_alert')}
• 🛡️ {get_text(lang, 'safety_mutual_buddy_protect')}
"""
        
        if safety.safety_buddy_user_id:
            buddy = db.query(User).filter_by(id=safety.safety_buddy_user_id).first()
            if buddy:
                text += f"\n✅ {get_text(lang, 'safety_mutual_buddy_current')}: {buddy.name or 'Unknown'}"
            
            buttons = [
                [InlineKeyboardButton(f"{'❌' if safety.mutual_safety_active else '✅'} {get_text(lang, 'safety_toggle')}", callback_data='safety_mb_toggle')],
                [InlineKeyboardButton(get_text(lang, 'safety_mutual_buddy_change'), callback_data='safety_mb_change')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
            ]
        else:
            text += f"\n{get_text(lang, 'safety_mutual_buddy_find')}"
            buttons = [
                [InlineKeyboardButton(get_text(lang, 'safety_mutual_buddy_search'), callback_data='safety_mb_search')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
            ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 3. AUTOMATED CHECK-IN SYSTEM
# ============================================================
# Based on: "planning for a safe exit" (Gillett 2023)

async def setup_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up automated check-in during dates"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""{get_text(lang, 'safety_checkin_info')}

{get_text(lang, 'safety_checkin_how')}
• ⏰ {get_text(lang, 'safety_checkin_interval')}: {safety.checkin_interval_minutes} {get_text(lang, 'safety_minutes')}
• 📱 {get_text(lang, 'safety_checkin_notify')}
• 🆘 {get_text(lang, 'safety_checkin_emergency')}

{get_text(lang, 'safety_checkin_status')}: {'✅' if safety.auto_checkin_enabled else '❌'}
"""
        
        buttons = [
            [InlineKeyboardButton(f"{'❌' if safety.auto_checkin_enabled else '✅'} {get_text(lang, 'safety_toggle')}", callback_data='safety_checkin_toggle')],
            [InlineKeyboardButton(f"⏱️ {get_text(lang, 'safety_checkin_change_interval')}", callback_data='safety_checkin_interval')],
            [InlineKeyboardButton(f"🚀 {get_text(lang, 'safety_checkin_start_now')}", callback_data='safety_checkin_start')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def start_checkin_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a check-in session for current date"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        # Create check-in session
        checkin = SafetyCheckIn(
            user_id=user.id,
            started_at=datetime.utcnow(),
            last_checkin=datetime.utcnow(),
            status='active'
        )
        db.add(checkin)
        db.commit()
        
        text = f"""{get_text(lang, 'safety_checkin_started')}

{get_text(lang, 'safety_checkin_reminder')}

{get_text(lang, 'safety_checkin_buttons_info')}"""
        
        buttons = [
            [InlineKeyboardButton(f"✅ {get_text(lang, 'safety_checkin_safe')}", callback_data='safety_ci_safe')],
            [InlineKeyboardButton(f"🆘 {get_text(lang, 'safety_checkin_help')}", callback_data='safety_ci_help')],
            [InlineKeyboardButton(f"🏠 {get_text(lang, 'safety_checkin_end')}", callback_data='safety_ci_end')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 4. PANIC BUTTON / SOS ALERT
# ============================================================

async def trigger_sos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger emergency SOS alert"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        # Create SOS alert
        alert = SOSAlert(
            user_id=user.id,
            triggered_at=datetime.utcnow(),
            message="SOS triggered"
        )
        db.add(alert)
        db.commit()
        
        text = f"""🆘 {get_text(lang, 'safety_sos_triggered')}

{get_text(lang, 'safety_sos_notifying')}

{get_text(lang, 'safety_sos_tips')}"""
        
        # Notify secret friend if active
        if safety.secret_friend_active and safety.secret_friend_telegram_id:
            try:
                await context.bot.send_message(
                    chat_id=safety.secret_friend_telegram_id,
                    text=f"🆘 {get_text(lang, 'safety_sos_friend_alert').format(name=user.name or 'Unknown')}"
                )
                text += f"\n\n✅ {get_text(lang, 'safety_sos_friend_notified')}"
            except Exception as e:
                logger.error(f"Could not notify secret friend: {e}")
                text += f"\n\n❌ {get_text(lang, 'safety_sos_friend_failed')}"
        
        buttons = [
            [InlineKeyboardButton(f"✅ {get_text(lang, 'safety_sos_im_safe')}", callback_data='safety_sos_safe')],
            [InlineKeyboardButton(f"📞 {get_text(lang, 'safety_sos_call_help')}", callback_data='safety_sos_call')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 5. SAFE WORD SYSTEM
# ============================================================

async def setup_safe_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up a safe word to signal distress"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""{get_text(lang, 'safety_safe_word_info')}

{get_text(lang, 'safety_safe_word_how')}
• 🔐 {get_text(lang, 'safety_safe_word_secret')}
• 📱 {get_text(lang, 'safety_safe_word_send')}
• 🆘 {get_text(lang, 'safety_safe_word_trigger')}

"""
        
        if safety.safe_word:
            masked_word = safety.safe_word[0] + '*' * (len(safety.safe_word) - 1)
            text += f"✅ {get_text(lang, 'safety_safe_word_set')}: {masked_word}"
            buttons = [
                [InlineKeyboardButton(f"✏️ {get_text(lang, 'safety_change')}", callback_data='safety_sw_change')],
                [InlineKeyboardButton(f"{'❌' if safety.safe_word_active else '✅'} {get_text(lang, 'safety_toggle')}", callback_data='safety_sw_toggle')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
            ]
        else:
            text += f"\n{get_text(lang, 'safety_safe_word_enter')}"
            buttons = [
                [InlineKeyboardButton(get_text(lang, 'safety_safe_word_create'), callback_data='safety_sw_create')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
            ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 6. PHOTO VERIFICATION
# ============================================================
# Prevents catfishing and "body scam" (Amirkhani et al. 2024)

async def setup_photo_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Photo verification to prevent catfishing"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""{get_text(lang, 'safety_photo_verify_info')}

{get_text(lang, 'safety_photo_verify_why')}

{get_text(lang, 'safety_photo_verify_how')}
• 📸 {get_text(lang, 'safety_photo_verify_selfie')}
• ✅ {get_text(lang, 'safety_photo_verify_confirm')}
• 🛡️ {get_text(lang, 'safety_photo_verify_badge')}

{get_text(lang, 'safety_photo_verify_status')}: {'✅ Verified' if safety.photo_verified else '❌ Not verified'}
"""
        
        buttons = [
            [InlineKeyboardButton(f"📸 {get_text(lang, 'safety_photo_verify_now')}", callback_data='safety_pv_verify')],
            [InlineKeyboardButton(f"{'✅' if safety.requires_verification else '❌'} {get_text(lang, 'safety_photo_require_others')}", callback_data='safety_pv_require')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 7. PRIVACY PROTECTION (Iran-context aware)
# ============================================================
# Based on: Bicharanlou & Siasirad (2017) - Iranian women's online privacy

async def setup_privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Privacy settings - critical for Iran context"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""🛡️ {get_text(lang, 'safety_privacy_info')}

{get_text(lang, 'safety_privacy_why')}

{get_text(lang, 'safety_privacy_current')}
"""
        
        privacy_status = []
        if safety.hide_profile_from_strangers:
            privacy_status.append(f"✅ {get_text(lang, 'safety_privacy_hide_strangers')}")
        if safety.anonymous_mode:
            privacy_status.append(f"✅ {get_text(lang, 'safety_privacy_anonymous')}")
        if safety.hide_exact_location:
            privacy_status.append(f"✅ {get_text(lang, 'safety_privacy_hide_location')}")
        if safety.blur_photos:
            privacy_status.append(f"✅ {get_text(lang, 'safety_privacy_blur')}")
        if safety.screenshot_protection:
            privacy_status.append(f"✅ {get_text(lang, 'safety_privacy_screenshot')}")
        
        text += "\n".join(privacy_status) if privacy_status else f"❌ {get_text(lang, 'safety_privacy_none')}"
        
        buttons = [
            [InlineKeyboardButton(f"{'✅' if safety.hide_profile_from_strangers else '❌'} {get_text(lang, 'safety_privacy_hide_strangers')}", callback_data='safety_priv_hide')],
            [InlineKeyboardButton(f"{'✅' if safety.anonymous_mode else '❌'} {get_text(lang, 'safety_privacy_anonymous')}", callback_data='safety_priv_anon')],
            [InlineKeyboardButton(f"{'✅' if safety.hide_exact_location else '❌'} {get_text(lang, 'safety_privacy_hide_location')}", callback_data='safety_priv_loc')],
            [InlineKeyboardButton(f"{'✅' if safety.blur_photos else '❌'} {get_text(lang, 'safety_privacy_blur')}", callback_data='safety_priv_blur')],
            [InlineKeyboardButton(f"{'✅' if safety.screenshot_protection else '❌'} {get_text(lang, 'safety_privacy_screenshot')}", callback_data='safety_priv_screen')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 8. CONSENT EDUCATION
# ============================================================
# Based on: Thompson (2018) - "missing discourse of consent"

async def show_consent_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show consent education module"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""💬 {get_text(lang, 'safety_consent_info')}

{get_text(lang, 'safety_consent_what')}

{get_text(lang, 'safety_consent_principles')}
1. 🔵 {get_text(lang, 'safety_consent_clear')}
2. 🔵 {get_text(lang, 'safety_consent_reversible')}
3. 🔵 {get_text(lang, 'safety_consent_informed')}
4. 🔵 {get_text(lang, 'safety_consent_enthusiastic')}
5. 🔵 {get_text(lang, 'safety_consent_specific')}

{get_text(lang, 'safety_consent_reminder')}
"""
        
        status = f"✅ {get_text(lang, 'safety_consent_completed')}" if safety.consent_education_shown else f"❌ {get_text(lang, 'safety_consent_not_completed')}"
        text += f"\n{status}"
        
        buttons = [
            [InlineKeyboardButton(f"📖 {get_text(lang, 'safety_consent_start')}", callback_data='safety_consent_start')],
            [InlineKeyboardButton(f"📋 {get_text(lang, 'safety_consent_quiz')}", callback_data='safety_consent_quiz')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 9. BLOCK & REPORT SYSTEM
# ============================================================

async def show_block_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block and report system"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        text = f"""🚫 {get_text(lang, 'safety_block_report_info')}

{get_text(lang, 'safety_block_report_types')}
• 🔴 {get_text(lang, 'safety_report_harassment')}
• 🔴 {get_text(lang, 'safety_report_catfish')}
• 🔴 {get_text(lang, 'safety_report_scam')}
• 🔴 {get_text(lang, 'safety_report_threats')}
• 🔴 {get_text(lang, 'safety_report_uncomfortable')}

{get_text(lang, 'safety_block_report_how')}"""
        
        buttons = [
            [InlineKeyboardButton(f"🚨 {get_text(lang, 'safety_report_someone')}", callback_data='safety_report_user')],
            [InlineKeyboardButton(f"📋 {get_text(lang, 'safety_report_history')}", callback_data='safety_report_history')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 10. SEXTORTION PROTECTION (Body Scam - Iran specific)
# ============================================================
# Based on: Amirkhani et al. (2024) - "body scam" and sextortion in Iran

async def show_sextortion_protection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Protection against sextortion and body scams"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""⚠️ {get_text(lang, 'safety_sextortion_info')}

{get_text(lang, 'safety_sextortion_what')}

{get_text(lang, 'safety_sextortion_signs')}
• 🔴 {get_text(lang, 'safety_sextortion_rush')}
• 🔴 {get_text(lang, 'safety_sextortion_pressure')}
• 🔴 {get_text(lang, 'safety_sextortion_threats')}
• 🔴 {get_text(lang, 'safety_sextortion_isolation')}

{get_text(lang, 'safety_sextortion_protection')}
• ✅ {get_text(lang, 'safety_sextortion_no_send')}
• ✅ {get_text(lang, 'safety_sextortion_report')}
• ✅ {get_text(lang, 'safety_sextortion_document')}
"""
        
        buttons = [
            [InlineKeyboardButton(f"{'✅' if safety.block_nude_requests else '❌'} {get_text(lang, 'safety_sextortion_auto_block')}", callback_data='safety_sex_block')],
            [InlineKeyboardButton(f"📖 {get_text(lang, 'safety_sextortion_education')}", callback_data='safety_sex_education')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# 11. DATE SAFETY PLANNING
# ============================================================

async def setup_date_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Plan safe dates and share with trusted contacts"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
        
        text = f"""📍 {get_text(lang, 'safety_date_plan_info')}

{get_text(lang, 'safety_date_plan_what')}
• 📍 {get_text(lang, 'safety_date_plan_location')}
• 👤 {get_text(lang, 'safety_date_plan_person')}
• ⏰ {get_text(lang, 'safety_date_plan_time')}
• 🚗 {get_text(lang, 'safety_date_plan_transport')}

{get_text(lang, 'safety_date_plan_tips')}
• ✅ {get_text(lang, 'safety_date_plan_public')}
• ✅ {get_text(lang, 'safety_date_plan_tell_friend')}
• ✅ {get_text(lang, 'safety_date_plan_own_transport')}
• ✅ {get_text(lang, 'safety_date_plan_phone_charged')}
• ✅ {get_text(lang, 'safety_date_plan_exit_plan')}
"""
        
        buttons = [
            [InlineKeyboardButton(f"📝 {get_text(lang, 'safety_date_plan_create')}", callback_data='safety_dp_create')],
            [InlineKeyboardButton(f"{'✅' if safety.date_plan_shared else '❌'} {get_text(lang, 'safety_date_plan_share')}", callback_data='safety_dp_share')],
            [InlineKeyboardButton(f"{'✅' if safety.safe_meeting_places else '❌'} {get_text(lang, 'safety_date_plan_safe_places')}", callback_data='safety_dp_places')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='safety_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


# ============================================================
# CALLBACK ROUTER
# ============================================================

async def safety_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route safety-related callbacks"""
    query = update.callback_query
    data = query.data
    
    if data == 'safety_menu':
        return await show_safety_menu(update, context)
    elif data == 'safety_secret_friend':
        return await setup_secret_friend(update, context)
    elif data == 'safety_sf_toggle':
        return await toggle_secret_friend(update, context)
    elif data == 'safety_mutual_buddy':
        return await setup_mutual_buddy(update, context)
    elif data == 'safety_checkin':
        return await setup_checkin(update, context)
    elif data == 'safety_checkin_toggle':
        await query.answer()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
            safety.auto_checkin_enabled = not safety.auto_checkin_enabled
            db.commit()
        finally:
            db.close()
        return await setup_checkin(update, context)
    elif data == 'safety_checkin_start':
        return await start_checkin_session(update, context)
    elif data == 'safety_sos':
        return await trigger_sos(update, context)
    elif data == 'safety_safe_word':
        return await setup_safe_word(update, context)
    elif data == 'safety_photo_verify':
        return await setup_photo_verification(update, context)
    elif data == 'safety_privacy':
        return await setup_privacy(update, context)
    elif data == 'safety_consent':
        return await show_consent_education(update, context)
    elif data == 'safety_block_report':
        return await show_block_report(update, context)
    elif data == 'safety_sextortion':
        return await show_sextortion_protection(update, context)
    elif data == 'safety_date_plan':
        return await setup_date_plan(update, context)
    
    # Privacy toggles
    elif data.startswith('safety_priv_'):
        await query.answer()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
            
            if data == 'safety_priv_hide':
                safety.hide_profile_from_strangers = not safety.hide_profile_from_strangers
            elif data == 'safety_priv_anon':
                safety.anonymous_mode = not safety.anonymous_mode
            elif data == 'safety_priv_loc':
                safety.hide_exact_location = not safety.hide_exact_location
            elif data == 'safety_priv_blur':
                safety.blur_photos = not safety.blur_photos
            elif data == 'safety_priv_screen':
                safety.screenshot_protection = not safety.screenshot_protection
            
            db.commit()
        finally:
            db.close()
        return await setup_privacy(update, context)
    
    # Sextortion toggles
    elif data == 'safety_sex_block':
        await query.answer()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
            safety.block_nude_requests = not safety.block_nude_requests
            db.commit()
        finally:
            db.close()
        return await show_sextortion_protection(update, context)
    
    # Date plan toggles
    elif data.startswith('safety_dp_'):
        await query.answer()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            safety = db.query(SafetySettings).filter_by(user_id=user.id).first()
            
            if data == 'safety_dp_share':
                safety.date_plan_shared = not safety.date_plan_shared
            elif data == 'safety_dp_places':
                safety.safe_meeting_places = not safety.safe_meeting_places
            
            db.commit()
        finally:
            db.close()
        return await setup_date_plan(update, context)
    
    # SOS safe
    elif data == 'safety_sos_safe':
        await query.answer()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            alert = db.query(SOSAlert).filter_by(user_id=user.id, resolved=False).first()
            if alert:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
        await query.edit_message_text("✅ You're safe! SOS alert resolved.")
        return await show_safety_menu(update, context)
    
    # Check-in actions
    elif data == 'safety_ci_safe':
        await query.answer("✅ Check-in confirmed! Stay safe.")
    elif data == 'safety_ci_help':
        return await trigger_sos(update, context)
    elif data == 'safety_ci_end':
        await query.answer()
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
            checkin = db.query(SafetyCheckIn).filter_by(user_id=user.id, status='active').first()
            if checkin:
                checkin.status = 'safe'
                db.commit()
        finally:
            db.close()
        await query.edit_message_text("✅ Date ended safely. Take care!")
    
    return ConversationHandler.END
