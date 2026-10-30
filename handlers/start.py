"""Start command, deep links (/start startup, /start abroad), language selection, and profile creation"""
from datetime import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User, RelationshipPreferences
from languages import get_text, SUPPORTED_LANGUAGES, detect_language_from_text
from config import DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_LANGUAGE, SELECTING_LANGUAGE_MANUAL = range(2)

VALID_DEEP_MODES = {
    'startup', 'abroad', 'serious', 'casual', 'marriage',
    'intellectual', 'emotional', 'friendship', 'open', 'one_night',
}


def build_main_menu_markup(lang: str) -> InlineKeyboardMarkup:
    """Categorized main menu with all 10 relationship modes, MBTI, safety, AI coach, and date history."""
    is_fa = (lang == 'fa')
    buttons = [
        [
            InlineKeyboardButton(get_text(lang, 'browse_profiles'), callback_data='browse'),
            InlineKeyboardButton(get_text(lang, 'my_matches'), callback_data='matches'),
        ],
        [
            InlineKeyboardButton('🎯 حالت رابطه (۱۰ حالت)' if is_fa else '🎯 10 Relationship Modes', callback_data='relationship_modes'),
            InlineKeyboardButton('🎓 مربی رابطه' if is_fa else '🎓 Mode Coach', callback_data='mode_coaching'),
        ],
        [
            InlineKeyboardButton('🧠 تست شخصیت MBTI' if is_fa else '🧠 MBTI Test', callback_data='personality_test'),
            InlineKeyboardButton('📅 تاریخچه قرارها' if is_fa else '📅 Date History', callback_data='date_history'),
        ],
        [
            InlineKeyboardButton('🛡️ مرکز ایمنی (۱۳ ابزار)' if is_fa else '🛡️ Safety Center (13)', callback_data='safety_menu'),
            InlineKeyboardButton(get_text(lang, 'ai_chat'), callback_data='ai_chat'),
        ],
        [
            InlineKeyboardButton(get_text(lang, 'settings'), callback_data='settings'),
            InlineKeyboardButton(get_text(lang, 'create_profile'), callback_data='edit_profile'),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start and deep links (/start startup, /start abroad, etc.)"""
    user = update.effective_user
    telegram_id = user.id
    deep_arg = (context.args[0].lower().strip() if getattr(context, 'args', None) else None)

    db = get_session()
    try:
        db_user = db.query(User).filter_by(telegram_id=telegram_id).first()

        if not db_user:
            db_user = User(
                telegram_id=telegram_id,
                username=user.username,
                first_name=user.first_name,
                language=DEFAULT_LANGUAGE,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            if deep_arg in VALID_DEEP_MODES:
                rel_pref = RelationshipPreferences(user_id=db_user.id, relationship_mode=deep_arg)
                db.add(rel_pref)
                db.commit()

            try:
                with open('welcome_banner.png', 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption="🌹 Welcome to Feminism AI Dating Bot!",
                    )
            except Exception:
                pass

            await _show_language_selection(update, db_user.language)
            return SELECTING_LANGUAGE

        # Existing user
        db_user.last_active = datetime.utcnow()
        lang = db_user.language or DEFAULT_LANGUAGE

        if deep_arg in VALID_DEEP_MODES:
            rel_pref = db.query(RelationshipPreferences).filter_by(user_id=db_user.id).first()
            if not rel_pref:
                rel_pref = RelationshipPreferences(user_id=db_user.id)
                db.add(rel_pref)
            rel_pref.relationship_mode = deep_arg
            db.commit()

            from handlers.relationship_modes import get_mode_info
            mi = get_mode_info(deep_arg, lang)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🧪 شروع تست سازگاری این حالت" if lang == 'fa' else "🧪 Start Mode Compatibility Test",
                    callback_data=f"connection_test_{deep_arg}",
                )],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
            ])
            await update.message.reply_text(
                f"✅ {mi['emoji']} {mi['name']}\n\n{mi['desc']}",
                reply_markup=kb,
            )
            return ConversationHandler.END

        db.commit()
        if not db_user.profile_complete:
            await update.message.reply_text(
                get_text(lang, 'welcome') + "\n\n" + get_text(lang, 'must_complete_profile'),
                reply_markup=build_main_menu_markup(lang),
            )
            return ConversationHandler.END

        await _show_main_menu(update, lang)
        return ConversationHandler.END
    finally:
        db.close()


async def _show_language_selection(update: Update, current_lang: str):
    buttons = []
    for code, name in SUPPORTED_LANGUAGES.items():
        buttons.append([
            InlineKeyboardButton(
                f"{'✅ ' if code == current_lang else ''}{name}",
                callback_data=f"lang_{code}",
            )
        ])
    await update.message.reply_text(
        get_text(current_lang, 'welcome') + "\n\n" + get_text(current_lang, 'select_language'),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle lang_* callback and begin profile setup"""
    query = update.callback_query
    await query.answer()
    lang_code = query.data.replace('lang_', '')

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            user = User(telegram_id=query.from_user.id, username=query.from_user.username, language=lang_code)
            db.add(user)
        else:
            user.language = lang_code
        db.commit()

        await query.edit_message_text(
            get_text(lang_code, 'language_selected') + "\n\n" + get_text(lang_code, 'must_complete_profile')
        )
        context.user_data['step'] = 'name'
        await query.message.reply_text(
            get_text(lang_code, 'ask_name'),
            reply_markup=_get_cancel_button(lang_code),
        )
        return SELECTING_LANGUAGE_MANUAL
    finally:
        db.close()


async def start_edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start profile creation/editing when user clicks edit_profile"""
    query = update.callback_query
    await query.answer()

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            user = User(telegram_id=query.from_user.id, username=query.from_user.username, language=DEFAULT_LANGUAGE)
            db.add(user)
            db.commit()
        lang = user.language or DEFAULT_LANGUAGE
        context.user_data['step'] = 'name'
        await query.edit_message_text(
            get_text(lang, 'ask_name'),
            reply_markup=_get_cancel_button(lang),
        )
        return SELECTING_LANGUAGE_MANUAL
    finally:
        db.close()


async def handle_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline buttons during profile creation: gender_*, looking_*, skip"""
    query = update.callback_query
    await query.answer()
    data = query.data

    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        lang = user.language or DEFAULT_LANGUAGE
        step = context.user_data.get('step', '')

        if data.startswith('gender_'):
            user.gender = data.replace('gender_', '')
            db.commit()
            context.user_data['step'] = 'looking_for'
            await query.edit_message_text(
                get_text(lang, 'ask_looking_for'),
                reply_markup=_get_looking_for_buttons(lang),
            )
            return SELECTING_LANGUAGE_MANUAL

        if data.startswith('looking_'):
            user.looking_for = data.replace('looking_', '')
            db.commit()
            context.user_data['step'] = 'bio'
            await query.edit_message_text(
                get_text(lang, 'ask_bio'),
                reply_markup=_get_skip_button(lang),
            )
            return SELECTING_LANGUAGE_MANUAL

        if data == 'skip':
            if step == 'bio':
                user.bio = user.bio or ''
                db.commit()
                context.user_data['step'] = 'city'
                await query.edit_message_text(
                    get_text(lang, 'ask_city'),
                    reply_markup=_get_skip_button(lang),
                )
                return SELECTING_LANGUAGE_MANUAL
            else:
                user.profile_complete = True
                db.commit()
                context.user_data.pop('step', None)
                await query.edit_message_text(
                    get_text(lang, 'profile_complete'),
                    reply_markup=build_main_menu_markup(lang),
                )
                return ConversationHandler.END

        return SELECTING_LANGUAGE_MANUAL
    finally:
        db.close()


async def handle_profile_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text & photo input during profile creation"""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(DEFAULT_LANGUAGE, 'error'))
            return ConversationHandler.END

        lang = user.language or DEFAULT_LANGUAGE
        step = context.user_data.get('step', 'name')

        if update.message.photo and step == 'photo':
            user.photo_file_id = update.message.photo[-1].file_id
            user.profile_complete = True
            db.commit()
            context.user_data.pop('step', None)
            await update.message.reply_text(
                get_text(lang, 'profile_complete'),
                reply_markup=build_main_menu_markup(lang),
            )
            return ConversationHandler.END

        text = (update.message.text or '').strip()

        if step == 'name':
            if not user.language:
                detected = detect_language_from_text(text)
                if detected and detected in SUPPORTED_LANGUAGES:
                    user.language = detected
                    lang = detected
            user.name = text[:100]
            db.commit()
            context.user_data['step'] = 'age'
            await update.message.reply_text(
                get_text(lang, 'ask_age'),
                reply_markup=_get_cancel_button(lang),
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
                        reply_markup=_get_gender_buttons(lang),
                    )
                else:
                    await update.message.reply_text(get_text(lang, 'invalid_age'))
            except ValueError:
                await update.message.reply_text(get_text(lang, 'invalid_age'))

        elif step == 'gender':
            if text.lower() in ('male', 'female', 'other'):
                user.gender = text.lower()
                db.commit()
                context.user_data['step'] = 'looking_for'
                await update.message.reply_text(
                    get_text(lang, 'ask_looking_for'),
                    reply_markup=_get_looking_for_buttons(lang),
                )

        elif step == 'looking_for':
            if text.lower() in ('male', 'female', 'anyone'):
                user.looking_for = text.lower()
                db.commit()
                context.user_data['step'] = 'bio'
                await update.message.reply_text(
                    get_text(lang, 'ask_bio'),
                    reply_markup=_get_skip_button(lang),
                )

        elif step == 'bio':
            user.bio = text[:500]
            db.commit()
            context.user_data['step'] = 'city'
            await update.message.reply_text(
                get_text(lang, 'ask_city'),
                reply_markup=_get_skip_button(lang),
            )

        elif step == 'city':
            user.city = text[:100]
            user.profile_complete = True
            db.commit()
            context.user_data['step'] = 'photo'
            await update.message.reply_text(
                get_text(lang, 'ask_photo'),
                reply_markup=_get_skip_button(lang),
            )

    finally:
        db.close()

    return SELECTING_LANGUAGE_MANUAL


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel active conversation via /cancel or inline button"""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else DEFAULT_LANGUAGE
    finally:
        db.close()

    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            get_text(lang, 'cancel'),
            reply_markup=build_main_menu_markup(lang),
        )
    else:
        await update.message.reply_text(
            get_text(lang, 'cancel'),
            reply_markup=build_main_menu_markup(lang),
        )
    return ConversationHandler.END


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu from command or callback"""
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        lang = user.language if user else DEFAULT_LANGUAGE
    finally:
        db.close()

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            get_text(lang, 'main_menu'),
            reply_markup=build_main_menu_markup(lang),
        )
    else:
        await _show_main_menu(update, lang)


async def _show_main_menu(update: Update, lang: str):
    await update.message.reply_text(
        get_text(lang, 'main_menu'),
        reply_markup=build_main_menu_markup(lang),
    )


def _get_gender_buttons(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_text(lang, 'male'), callback_data='gender_male'),
            InlineKeyboardButton(get_text(lang, 'female'), callback_data='gender_female'),
        ],
        [InlineKeyboardButton(get_text(lang, 'other'), callback_data='gender_other')],
    ])


def _get_looking_for_buttons(lang: str) -> InlineKeyboardMarkup:
    anyone_label = 'هر کسی' if lang == 'fa' else ('Anyone' if lang == 'en' else get_text(lang, 'other'))
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_text(lang, 'male'), callback_data='looking_male'),
            InlineKeyboardButton(get_text(lang, 'female'), callback_data='looking_female'),
        ],
        [InlineKeyboardButton(anyone_label, callback_data='looking_anyone')],
    ])


def _get_cancel_button(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, 'cancel'), callback_data='cancel')]])


def _get_skip_button(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, 'skip'), callback_data='skip')]])
