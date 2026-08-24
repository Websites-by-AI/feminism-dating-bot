"""Matching and browsing profiles handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session, User, Like, Match
from languages import get_text
from sqlalchemy import and_
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def browse_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a profile to browse (swipe feature)."""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return
        
        if not user.profile_complete:
            lang = user.language
            await query.message.reply_text(get_text(lang, 'must_complete_profile'))
            return
        
        lang = user.language
        
        # Find potential matches
        candidates = _find_candidates(db, user)
        
        if not candidates:
            await query.edit_message_text(
                get_text(lang, 'no_profiles_found'),
                reply_markup=_get_back_button(lang)
            )
            return
        
        # Pick a random candidate
        candidate = random.choice(candidates)
        
        # Store current candidate in context
        context.user_data['current_profile'] = candidate.id
        
        # Show the profile
        profile_text = get_text(lang, 'profile_preview').format(
            name=candidate.name or 'Unknown',
            age=candidate.age or '?',
            city=candidate.city or 'Unknown',
            bio=candidate.bio or ''
        )
        
        # Build action buttons
        buttons = [
            [
                InlineKeyboardButton(get_text(lang, 'like'), callback_data=f'like_{candidate.id}'),
                InlineKeyboardButton(get_text(lang, 'pass'), callback_data=f'pass_{candidate.id}'),
            ],
            [InlineKeyboardButton(get_text(lang, 'next'), callback_data='browse_next')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Send photo if available
        if candidate.photo_file_id:
            await query.message.reply_photo(
                photo=candidate.photo_file_id,
                caption=profile_text,
                reply_markup=keyboard
            )
            await query.message.delete()
        else:
            await query.edit_message_text(profile_text, reply_markup=keyboard)
            
    finally:
        db.close()


async def handle_swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle like or pass action."""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return
        
        lang = user.language
        data = query.data
        
        if data.startswith('like_'):
            target_id = int(data.replace('like_', ''))
            is_like = True
        elif data.startswith('pass_'):
            target_id = int(data.replace('pass_', ''))
            is_like = False
        elif data == 'browse_next':
            await browse_profiles(update, context)
            return
        else:
            return
        
        # Check if already liked/passed
        existing = db.query(Like).filter_by(
            from_user_id=user.id, 
            to_user_id=target_id
        ).first()
        
        if existing:
            if is_like:
                await query.edit_message_text(get_text(lang, 'liked'))
            else:
                await query.edit_message_text(get_text(lang, 'passed'))
            return
        
        # Record the like/pass
        like = Like(
            from_user_id=user.id,
            to_user_id=target_id,
            is_like=is_like
        )
        db.add(like)
        user.last_swipe = datetime.utcnow()
        db.commit()
        
        # Check if it's a match (mutual like)
        if is_like:
            mutual_like = db.query(Like).filter_by(
                from_user_id=target_id,
                to_user_id=user.id,
                is_like=True
            ).first()
            
            if mutual_like:
                # It's a match!
                match = Match(user1_id=user.id, user2_id=target_id)
                db.add(match)
                db.commit()
                
                target_user = db.query(User).filter_by(id=target_id).first()
                
                await query.edit_message_text(
                    get_text(lang, 'its_a_match'),
                    reply_markup=_get_back_button(lang)
                )
                
                # Notify the other user (if possible)
                if target_user:
                    try:
                        await context.bot.send_message(
                            chat_id=target_user.telegram_id,
                            text=get_text(target_user.language, 'its_a_match')
                        )
                    except Exception as e:
                        logger.warning(f"Could not notify user {target_user.telegram_id}: {e}")
                
                return
        
        # Show feedback
        if is_like:
            feedback = get_text(lang, 'liked')
        else:
            feedback = get_text(lang, 'passed')
        
        await query.edit_message_text(feedback)
        
        # Show next profile after a moment
        # (In production, you might want to add a delay or let user click next)
        
    finally:
        db.close()


async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's matches."""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return
        
        lang = user.language
        
        # Get matches
        matches = db.query(Match).filter(
            (Match.user1_id == user.id) | (Match.user2_id == user.id),
            Match.is_active == True
        ).all()
        
        if not matches:
            await query.edit_message_text(
                get_text(lang, 'no_matches'),
                reply_markup=_get_back_button(lang)
            )
            return
        
        # Build matches list
        match_texts = []
        buttons = []
        
        for match in matches:
            other_id = match.user2_id if match.user1_id == user.id else match.user1_id
            other = db.query(User).filter_by(id=other_id).first()
            
            if other:
                match_text = f"👤 {other.name or 'Unknown'}, {other.age or '?'} - {other.city or ''}"
                match_texts.append(match_text)
                buttons.append([InlineKeyboardButton(
                    f"💬 {other.name or 'Chat'}",
                    callback_data=f'chat_{other.id}'
                )])
        
        text = get_text(lang, 'my_matches') + "\n\n" + "\n".join(match_texts)
        buttons.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')])
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


def _find_candidates(db, user: User, limit: int = 20):
    """Find potential match candidates for a user."""
    # Get IDs of users already liked or passed
    existing_actions = db.query(Like.to_user_id).filter_by(from_user_id=user.id).all()
    excluded_ids = [action[0] for action in existing_actions]
    excluded_ids.append(user.id)  # Exclude self
    
    # Build query for candidates
    query = db.query(User).filter(
        User.profile_complete == True,
        User.is_active == True,
        User.id.notin_(excluded_ids) if excluded_ids else True,
    )
    
    # Filter by looking_for preference
    if user.looking_for and user.looking_for != 'anyone':
        query = query.filter(User.gender == user.looking_for)
    
    # Filter by age range
    if user.age_min:
        query = query.filter(User.age >= user.age_min)
    if user.age_max:
        query = query.filter(User.age <= user.age_max)
    
    # Filter by city if set
    if user.city:
        query = query.filter(User.city == user.city)
    
    candidates = query.limit(limit).all()
    return candidates


def _get_back_button(lang: str) -> InlineKeyboardMarkup:
    """Get back to menu button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')
    ]])
