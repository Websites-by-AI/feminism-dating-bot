"""
Date History & AI Analysis Handler
Track dates, analyze patterns, provide AI-powered insights
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_session, User, DateRecord, UserPatternAnalysis
from languages import get_text
from ai_service import ai_service
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Conversation states
(
    ADD_DATE_TYPE, ADD_DATE_LOCATION, ADD_DATE_DATE,
    RATE_OVERALL, RATE_CONNECTION, RATE_COMFORT, RATE_SAFETY,
    ADD_WENT_WELL, ADD_DIDNT_WORK, ADD_RED_FLAGS, ADD_GREEN_FLAGS,
    ADD_OUTCOME, ADD_NOTES, SHOW_ANALYSIS
) = range(14)


async def show_date_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show date history and analysis"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            return ConversationHandler.END
        
        lang = user.language
        
        # Get date records
        dates = db.query(DateRecord).filter_by(user_id=user.id).order_by(DateRecord.date_date.desc()).all()
        pattern = db.query(UserPatternAnalysis).filter_by(user_id=user.id).first()
        
        if not dates:
            text = f"""📅 {get_text(lang, 'no_dates_yet')}

{get_text(lang, 'add_first_date')}"""
            
            buttons = [
                [InlineKeyboardButton(f"➕ {get_text(lang, 'add_date')}", callback_data='add_date_start')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
            ]
        else:
            # Show summary
            total_dates = len(dates)
            second_dates = len([d for d in dates if d.outcome == 'want_second_date'])
            avg_rating = sum(d.overall_rating or 0 for d in dates) / total_dates if total_dates > 0 else 0
            
            text = f"""📅 {get_text(lang, 'date_history')}

━━━━━━━━━━━━━━━━━━
📊 {get_text(lang, 'stats')}:
• {get_text(lang, 'total_dates')}: {total_dates}
• {get_text(lang, 'second_date_rate')}: {second_dates}/{total_dates} ({(second_dates/total_dates*100):.0f}%)
• {get_text(lang, 'avg_rating')}: {avg_rating:.1f}/5
━━━━━━━━━━━━━━━━━━

{get_text(lang, 'recent_dates')}:"""
            
            # Add recent dates (last 3)
            for date in dates[:3]:
                rating_emoji = '⭐' * (date.overall_rating or 0)
                outcome_text = _get_outcome_text(date.outcome, lang)
                text += f"\n• {date.date_type or 'Date'} - {rating_emoji} {outcome_text}"
            
            buttons = [
                [InlineKeyboardButton(f"➕ {get_text(lang, 'add_new_date')}", callback_data='add_date_start')],
                [InlineKeyboardButton(f"📊 {get_text(lang, 'ai_analysis')}", callback_data='show_ai_analysis')],
                [InlineKeyboardButton(f"📜 {get_text(lang, 'view_all')}", callback_data='view_all_dates')],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
            ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def start_add_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new date record"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        context.user_data['new_date'] = {}
        
        text = f"📅 {get_text(lang, 'what_type_of_date')}"
        
        buttons = [
            [InlineKeyboardButton("☕ Coffee/Tea", callback_data='date_type_coffee')],
            [InlineKeyboardButton("🍽️ Dinner", callback_data='date_type_dinner')],
            [InlineKeyboardButton("🚶 Walk/Activity", callback_data='date_type_walk')],
            [InlineKeyboardButton("🎬 Movie/Show", callback_data='date_type_movie')],
            [InlineKeyboardButton("🎨 Other", callback_data='date_type_other')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


async def handle_date_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date type selection"""
    query = update.callback_query
    await query.answer()
    
    date_type = query.data.replace('date_type_', '')
    context.user_data['new_date']['type'] = date_type
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        text = f"📍 {get_text(lang, 'where_did_you_meet')}"
        
        await query.edit_message_text(text, reply_markup=None)
        context.user_data['awaiting_location'] = True
        
    finally:
        db.close()


async def handle_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for date details"""
    if 'awaiting_location' in context.user_data:
        context.user_data['new_date']['location'] = update.message.text
        del context.user_data['awaiting_location']
        
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
            lang = user.language
            
            text = f"📅 {get_text(lang, 'when_was_date')} (YYYY-MM-DD)"
            await update.message.reply_text(text)
            context.user_data['awaiting_date'] = True
            
        finally:
            db.close()
        
    elif 'awaiting_date' in context.user_data:
        try:
            date_str = update.message.text
            context.user_data['new_date']['date'] = datetime.strptime(date_str, '%Y-%m-%d')
            del context.user_data['awaiting_date']
            
            db = get_session()
            try:
                user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
                lang = user.language
                
                text = f"⭐ {get_text(lang, 'rate_overall')} (1-5)"
                await update.message.reply_text(text)
                context.user_data['awaiting_overall_rating'] = True
                
            finally:
                db.close()
        except ValueError:
            await update.message.reply_text("❌ Invalid date format. Please use YYYY-MM-DD")
    
    elif 'awaiting_overall_rating' in context.user_data:
        try:
            rating = int(update.message.text)
            if 1 <= rating <= 5:
                context.user_data['new_date']['overall_rating'] = rating
                del context.user_data['awaiting_overall_rating']
                
                db = get_session()
                try:
                    user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
                    lang = user.language
                    
                    text = f"💕 {get_text(lang, 'rate_connection')} (1-5)"
                    await update.message.reply_text(text)
                    context.user_data['awaiting_connection_rating'] = True
                    
                finally:
                    db.close()
            else:
                await update.message.reply_text("Please enter a number between 1-5")
        except ValueError:
            await update.message.reply_text("Please enter a valid number")
    
    elif 'awaiting_connection_rating' in context.user_data:
        try:
            rating = int(update.message.text)
            if 1 <= rating <= 5:
                context.user_data['new_date']['connection_rating'] = rating
                del context.user_data['awaiting_connection_rating']
                
                db = get_session()
                try:
                    user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
                    lang = user.language
                    
                    text = f"😊 {get_text(lang, 'rate_comfort')} (1-5)"
                    await update.message.reply_text(text)
                    context.user_data['awaiting_comfort_rating'] = True
                    
                finally:
                    db.close()
        except ValueError:
            await update.message.reply_text("Please enter a valid number")
    
    elif 'awaiting_comfort_rating' in context.user_data:
        try:
            rating = int(update.message.text)
            if 1 <= rating <= 5:
                context.user_data['new_date']['comfort_rating'] = rating
                del context.user_data['awaiting_comfort_rating']
                
                db = get_session()
                try:
                    user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
                    lang = user.language
                    
                    text = f"✅ {get_text(lang, 'what_went_well')}"
                    await update.message.reply_text(text)
                    context.user_data['awaiting_went_well'] = True
                    
                finally:
                    db.close()
        except ValueError:
            await update.message.reply_text("Please enter a valid number")
    
    elif 'awaiting_went_well' in context.user_data:
        context.user_data['new_date']['went_well'] = update.message.text
        del context.user_data['awaiting_went_well']
        
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
            lang = user.language
            
            text = f"❌ {get_text(lang, 'what_didnt_work')}"
            await update.message.reply_text(text)
            context.user_data['awaiting_didnt_work'] = True
            
        finally:
            db.close()
    
    elif 'awaiting_didnt_work' in context.user_data:
        context.user_data['new_date']['didnt_work'] = update.message.text
        del context.user_data['awaiting_didnt_work']
        
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
            lang = user.language
            
            text = f"🚩 {get_text(lang, 'any_red_flags')} (یا 'none')"
            await update.message.reply_text(text)
            context.user_data['awaiting_red_flags'] = True
            
        finally:
            db.close()
    
    elif 'awaiting_red_flags' in context.user_data:
        red_flags = update.message.text if update.message.text.lower() != 'none' else None
        context.user_data['new_date']['red_flags'] = red_flags
        del context.user_data['awaiting_red_flags']
        
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
            lang = user.language
            
            text = f"💚 {get_text(lang, 'any_green_flags')} (یا 'none')"
            await update.message.reply_text(text)
            context.user_data['awaiting_green_flags'] = True
            
        finally:
            db.close()
    
    elif 'awaiting_green_flags' in context.user_data:
        green_flags = update.message.text if update.message.text.lower() != 'none' else None
        context.user_data['new_date']['green_flags'] = green_flags
        del context.user_data['awaiting_green_flags']
        
        db = get_session()
        try:
            user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
            lang = user.language
            
            text = f"🎯 {get_text(lang, 'date_outcome')}"
            
            buttons = [
                [InlineKeyboardButton(get_text(lang, 'want_second'), callback_data='outcome_second')],
                [InlineKeyboardButton(get_text(lang, 'not_interested'), callback_data='outcome_not_interested')],
                [InlineKeyboardButton(get_text(lang, 'friendzoned'), callback_data='outcome_friend')],
                [InlineKeyboardButton(get_text(lang, 'ghosted'), callback_data='outcome_ghosted')],
                [InlineKeyboardButton(get_text(lang, 'still_deciding'), callback_data='outcome_deciding')],
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            
            await update.message.reply_text(text, reply_markup=keyboard)
            
        finally:
            db.close()


async def handle_outcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date outcome selection"""
    query = update.callback_query
    await query.answer()
    
    outcome = query.data.replace('outcome_', '')
    context.user_data['new_date']['outcome'] = outcome
    
    # Save date record
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        new_date_data = context.user_data['new_date']
        
        date_record = DateRecord(
            user_id=user.id,
            date_type=new_date_data.get('type'),
            date_location=new_date_data.get('location'),
            date_date=new_date_data.get('date'),
            overall_rating=new_date_data.get('overall_rating'),
            connection_rating=new_date_data.get('connection_rating'),
            comfort_rating=new_date_data.get('comfort_rating'),
            what_went_well=new_date_data.get('went_well'),
            what_didnt_work=new_date_data.get('didnt_work'),
            red_flags=new_date_data.get('red_flags'),
            green_flags=new_date_data.get('green_flags'),
            outcome=outcome
        )
        
        db.add(date_record)
        db.commit()
        
        # Update pattern analysis
        await _update_pattern_analysis(db, user.id)
        
        text = f"✅ {get_text(lang, 'date_added_success')}\n\n{get_text(lang, 'check_ai_analysis')}"
        
        buttons = [
            [InlineKeyboardButton(f"📊 {get_text(lang, 'view_analysis')}", callback_data='show_ai_analysis')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(text, reply_markup=keyboard)
        
        # Clear context
        if 'new_date' in context.user_data:
            del context.user_data['new_date']
        
    finally:
        db.close()


async def _update_pattern_analysis(db, user_id):
    """Update AI pattern analysis based on date history"""
    dates = db.query(DateRecord).filter_by(user_id=user_id).all()
    
    if not dates:
        return
    
    # Calculate statistics
    total = len(dates)
    avg_overall = sum(d.overall_rating or 0 for d in dates) / total
    avg_connection = sum(d.connection_rating or 0 for d in dates) / total
    avg_comfort = sum(d.comfort_rating or 0 for d in dates) / total
    
    second_dates = len([d for d in dates if d.outcome == 'want_second_date'])
    second_date_rate = (second_dates / total) * 100 if total > 0 else 0
    
    # Collect red flags
    all_red_flags = []
    for d in dates:
        if d.red_flags:
            all_red_flags.append(d.red_flags)
    
    # Collect green flags
    all_green_flags = []
    for d in dates:
        if d.green_flags:
            all_green_flags.append(d.green_flags)
    
    # Most common date types
    date_types = {}
    for d in dates:
        if d.date_type:
            date_types[d.date_type] = date_types.get(d.date_type, 0) + 1
    
    best_date_type = max(date_types, key=date_types.get) if date_types else None
    
    # Get or create pattern analysis
    pattern = db.query(UserPatternAnalysis).filter_by(user_id=user_id).first()
    if not pattern:
        pattern = UserPatternAnalysis(user_id=user_id)
        db.add(pattern)
    
    pattern.total_dates = total
    pattern.avg_connection_score = avg_connection
    pattern.avg_comfort_score = avg_comfort
    pattern.second_date_rate = second_date_rate
    pattern.common_red_flags = json.dumps(all_red_flags) if all_red_flags else None
    pattern.common_green_flags = json.dumps(all_green_flags) if all_green_flags else None
    pattern.best_date_types = best_date_type
    pattern.last_analyzed = datetime.utcnow()
    
    db.commit()


async def show_ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI-powered analysis of dating patterns"""
    query = update.callback_query
    await query.answer()
    
    db = get_session()
    try:
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        lang = user.language
        
        pattern = db.query(UserPatternAnalysis).filter_by(user_id=user.id).first()
        dates = db.query(DateRecord).filter_by(user_id=user.id).all()
        
        if not dates or not pattern:
            text = f"📊 {get_text(lang, 'not_enough_data')}"
            buttons = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='date_history')]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
            return
        
        # Build analysis prompt
        analysis_prompt = f"""You are a dating relationship analyst. Analyze this user's dating patterns:

Total dates: {pattern.total_dates}
Second date rate: {pattern.second_date_rate:.0f}%
Average connection rating: {pattern.avg_connection_score:.1f}/5
Average comfort rating: {pattern.avg_comfort_score:.1f}/5
Best date type: {pattern.best_date_types}

Recent dates summary:
"""
        
        for date in dates[-5:]:  # Last 5 dates
            analysis_prompt += f"- {date.date_type}: Rating {date.overall_rating}/5, Outcome: {date.outcome}"
            if date.red_flags:
                analysis_prompt += f", Red flags: {date.red_flags}"
            if date.green_flags:
                analysis_prompt += f", Green flags: {date.green_flags}"
            analysis_prompt += "\n"
        
        analysis_prompt += "\nProvide insights on:"
        analysis_prompt += "\n1. Patterns in their dating choices"
        analysis_prompt += "\n2. Strengths they show in dating"
        analysis_prompt += "\n3. Areas for improvement"
        analysis_prompt += "\n4. Recommendations for future dates"
        analysis_prompt += "\n\nKeep it supportive, constructive, and actionable."
        
        # Get AI analysis
        thinking_msg = await query.edit_message_text(f"🤖 {get_text(lang, 'analyzing_patterns')}")
        
        try:
            ai_response = await ai_service.chat(
                user_id=user.id,
                message=analysis_prompt,
                language=lang,
                user_profile={'name': user.name, 'age': user.age}
            )
            
            # Save analysis
            pattern.ai_recommendations = ai_response
            db.commit()
            
            text = f"""📊 {get_text(lang, 'ai_analysis_title')}

━━━━━━━━━━━━━━━━━━
{ai_response}
━━━━━━━━━━━━━━━━━━

💡 {get_text(lang, 'key_insights')}:"""
            
            # Add key insights
            if pattern.second_date_rate > 50:
                text += f"\n✅ {get_text(lang, 'good_second_date_rate')}"
            elif pattern.second_date_rate < 30:
                text += f"\n⚠️ {get_text(lang, 'low_second_date_rate')}"
            
            if pattern.avg_connection_score >= 4:
                text += f"\n✅ {get_text(lang, 'good_connection')}"
            elif pattern.avg_connection_score < 3:
                text += f"\n⚠️ {get_text(lang, 'low_connection')}"
            
            if pattern.best_date_types:
                text += f"\n💡 {get_text(lang, 'best_date_type')}: {pattern.best_date_types}"
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            text = f"❌ {get_text(lang, 'analysis_error')}"
        
        buttons = [
            [InlineKeyboardButton(f"🔄 {get_text(lang, 'refresh_analysis')}", callback_data='show_ai_analysis')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='date_history')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await thinking_msg.edit_text(text, reply_markup=keyboard)
        
    finally:
        db.close()


def _get_outcome_text(outcome, lang):
    """Get outcome display text"""
    outcomes = {
        'want_second_date': {'fa': '✅ قرار دوم', 'en': '✅ Want 2nd date'},
        'not_interested': {'fa': '❌ علاقه‌ای نبود', 'en': '❌ Not interested'},
        'friendzoned': {'fa': '🤝 دوستی', 'en': '🤝 Friendzoned'},
        'ghosted': {'fa': '👻 گوست شد', 'en': '👻 Ghosted'},
        'rejected_by_them': {'fa': '💔 رد شدم', 'en': '💔 Rejected'},
        'still_deciding': {'fa': '🤔 در حال تصمیم', 'en': '🤔 Still deciding'},
    }
    return outcomes.get(outcome, {}).get(lang, outcome)
