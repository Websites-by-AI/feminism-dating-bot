"""Database models and setup for the dating bot"""
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    language = Column(String(5), default='fa')
    
    # Profile fields
    name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)  # male, female, other
    looking_for = Column(String(50), nullable=True)  # male, female, anyone
    bio = Column(Text, nullable=True)
    city = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    photo_file_id = Column(String(500), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    profile_complete = Column(Boolean, default=False)
    
    # Preferences
    max_distance_km = Column(Integer, default=50)
    age_min = Column(Integer, default=18)
    age_max = Column(Integer, default=40)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    last_swipe = Column(DateTime, nullable=True)
    
    # Relationships
    likes = relationship('Like', foreign_keys='Like.from_user_id', back_populates='from_user')
    liked_by = relationship('Like', foreign_keys='Like.to_user_id', back_populates='to_user')
    matches = relationship('Match', foreign_keys='Match.user1_id', back_populates='user1')
    chats = relationship('Chat', foreign_keys='Chat.user1_id', back_populates='user1')


class Like(Base):
    __tablename__ = 'likes'
    
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_like = Column(Boolean, default=True)  # True = like, False = pass
    created_at = Column(DateTime, default=datetime.utcnow)
    
    from_user = relationship('User', foreign_keys=[from_user_id], back_populates='likes')
    to_user = relationship('User', foreign_keys=[to_user_id], back_populates='liked_by')


class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user1 = relationship('User', foreign_keys=[user1_id], back_populates='matches')


class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user1 = relationship('User', foreign_keys=[user1_id], back_populates='chats')
    messages = relationship('Message', back_populates='chat')


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_ai = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chat = relationship('Chat', back_populates='messages')


# ============================================================
# SAFETY SYSTEM MODELS (Based on Academic Research)
# ============================================================
# References:
# - Gillett (2023): Women's safety work on dating apps
# - Doria (2023): Dating app-facilitated sexualized violence
# - Amirkhani et al. (2024): Online romance scams in Iran
# - Bicharanlou & Siasirad (2017): Iranian women's online privacy
# - ACM CSCW (2024): "Body scam" and sextortion in Iran


class SafetySettings(Base):
    """User safety preferences and configurations"""
    __tablename__ = 'safety_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Secret Friend / Trusted Contact System
    # Based on: women need someone to know their location (Gillett 2023)
    secret_friend_telegram_id = Column(BigInteger, nullable=True)  # Trusted contact
    secret_friend_name = Column(String(255), nullable=True)
    secret_friend_active = Column(Boolean, default=False)
    share_location_with_friend = Column(Boolean, default=False)
    
    # Auto-activate for mutual protection
    # Women can request each other to activate safety features
    mutual_safety_active = Column(Boolean, default=False)
    safety_buddy_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Check-in System
    # Based on: "planning for a safe exit" (Gillett 2023)
    auto_checkin_enabled = Column(Boolean, default=True)
    checkin_interval_minutes = Column(Integer, default=30)
    last_checkin = Column(DateTime, nullable=True)
    
    # Panic Button / SOS
    sos_enabled = Column(Boolean, default=True)
    sos_contacts_notified = Column(Boolean, default=False)
    
    # Safe Word System
    safe_word = Column(String(50), nullable=True)  # Code word to signal distress
    safe_word_active = Column(Boolean, default=False)
    
    # Photo Verification
    # Based on: photo verification prevents catfishing
    photo_verified = Column(Boolean, default=False)
    photo_verification_date = Column(DateTime, nullable=True)
    requires_verification = Column(Boolean, default=True)  # Requires others to verify
    
    # Privacy Protection (Critical for Iran context)
    # Based on: Iranian women's privacy concerns (Bicharanlou 2017)
    hide_profile_from_strangers = Column(Boolean, default=False)
    anonymous_mode = Column(Boolean, default=False)  # No real name shown
    hide_exact_location = Column(Boolean, default=True)  # Show city only, not exact
    blur_photos = Column(Boolean, default=False)  # Blur until match confirmed
    delete_chat_after_days = Column(Integer, nullable=True)  # Auto-delete chats
    screenshot_protection = Column(Boolean, default=True)
    
    # Consent Education
    # Based on: "missing discourse of consent" (Thompson 2018)
    consent_education_shown = Column(Boolean, default=False)
    consent_quiz_passed = Column(Boolean, default=False)
    
    # Block/Report System
    auto_block_unverified = Column(Boolean, default=False)
    report_count = Column(Integer, default=0)
    blocked_count = Column(Integer, default=0)
    
    # Sextortion Protection (Iran-specific)
    # Based on: "body scam" awareness (Amirkhani et al. 2024)
    sextortion_warning_shown = Column(Boolean, default=False)
    block_nude_requests = Column(Boolean, default=True)  # Auto-flag requests
    media_sharing_consent = Column(Boolean, default=True)  # Consent for sharing media
    
    # Date Safety Planning
    date_plan_shared = Column(Boolean, default=False)  # Date plans shared with friend
    safe_meeting_places = Column(Boolean, default=True)  # Suggest public places only
    emergency_exit_ready = Column(Boolean, default=True)  # Pre-planned exit strategy
    
    # Safety Score
    safety_score = Column(Float, default=100.0)  # 0-100, decreases with reports
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


class SOSAlert(Base):
    """Emergency SOS alerts"""
    __tablename__ = 'sos_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    location = Column(String(500), nullable=True)
    message = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    user = relationship('User')


class SafetyReport(Base):
    """Reports of inappropriate behavior"""
    __tablename__ = 'safety_reports'
    
    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reported_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    report_type = Column(String(100), nullable=False)  # harassment, catfish, scam, etc.
    description = Column(Text, nullable=True)
    evidence_message_ids = Column(Text, nullable=True)  # JSON list of message IDs
    status = Column(String(50), default='pending')  # pending, reviewed, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    reporter = relationship('User', foreign_keys=[reporter_id])
    reported = relationship('User', foreign_keys=[reported_user_id])


class SafetyCheckIn(Base):
    """Automated safety check-ins during dates"""
    __tablename__ = 'safety_checkins'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Who they're with
    started_at = Column(DateTime, default=datetime.utcnow)
    last_checkin = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='active')  # active, safe, emergency
    checkin_count = Column(Integer, default=0)
    
    user = relationship('User', foreign_keys=[user_id])
    date_user = relationship('User', foreign_keys=[date_user_id])


class ConsentRecord(Base):
    """Records of consent education and agreements"""
    __tablename__ = 'consent_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    consent_type = Column(String(100), nullable=False)  # education, media_share, meetup
    agreed = Column(Boolean, default=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User')


class AIConversation(Base):
    """For AI dating coach conversations"""
    __tablename__ = 'ai_conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# PERSONALITY & PSYCHOLOGY MODELS
# ============================================================

class PersonalityProfile(Base):
    """MBTI + Love Language + Attachment Style + Big Five"""
    __tablename__ = 'personality_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # MBTI (Myers-Briggs Type Indicator)
    mbti_type = Column(String(4), nullable=True)  # e.g., INFJ, ENFP
    mbti_scores = Column(Text, nullable=True)  # JSON: {E:60, I:40, S:30, N:70, ...}
    
    # Enneagram
    enneagram_type = Column(Integer, nullable=True)  # 1-9
    
    # Love Languages (top 2-3)
    love_language_1 = Column(String(50), nullable=True)  # words_of_affirmation, quality_time, etc.
    love_language_2 = Column(String(50), nullable=True)
    love_language_3 = Column(String(50), nullable=True)
    
    # Attachment Style
    attachment_style = Column(String(50), nullable=True)  # secure, anxious, avoidant, disorganized
    
    # Big Five (OCEAN) - percentage scores
    openness = Column(Float, nullable=True)
    conscientiousness = Column(Float, nullable=True)
    extraversion = Column(Float, nullable=True)
    agreeableness = Column(Float, nullable=True)
    neuroticism = Column(Float, nullable=True)
    
    # Communication Style
    communication_style = Column(String(50), nullable=True)  # direct, diplomatic, analytical, expressive
    
    # Conflict Resolution Style
    conflict_style = Column(String(50), nullable=True)  # collaborative, competitive, accommodating, avoiding
    
    test_completed = Column(Boolean, default=False)
    test_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


class DatingIntentions(Base):
    """What users are looking for - inspired by Bumble's Dating Intentions"""
    __tablename__ = 'dating_intentions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Relationship type
    relationship_type = Column(String(100), nullable=True)
    # Options: life_partner, long_term, short_term, casual, open_to_anything, 
    #          ethical_nonmonogamy, friendship_first, figuring_it_out
    
    # Dating intentions (multiple, stored as JSON list)
    intentions = Column(Text, nullable=True)
    # Options: intimacy_with_commitment, intimacy_without_commitment, 
    #          marriage, children, travel_partner, emotional_connection,
    #          shared_values, intellectual_connection
    
    # Character traits prioritized
    priority_traits = Column(Text, nullable=True)  # JSON list: loyalty, humor, sarcasm, etc.
    
    # Causes they support
    causes = Column(Text, nullable=True)  # JSON list: feminism, BLM, climate, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


class LifestylePreferences(Base):
    """Diet, habits, lifestyle - for compatibility matching"""
    __tablename__ = 'lifestyle_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Diet
    diet = Column(String(50), nullable=True)
    # Options: vegan, vegetarian, pescatarian, flexitarian, omnivore, keto, halal, kosher
    
    # Smoking
    smoking = Column(String(50), nullable=True)
    # Options: never, former, occasional, regular, trying_to_quit
    
    # Drinking
    drinking = Column(String(50), nullable=True)
    # Options: never, rarely, socially, regularly
    
    # Exercise
    exercise = Column(String(50), nullable=True)
    # Options: never, rarely, sometimes, often, daily
    
    # Religion/Spirituality
    religion = Column(String(100), nullable=True)
    # Options: atheist, agnostic, christian, muslim, jewish, buddhist, hindu, spiritual, other
    
    # Political views (for values matching)
    politics = Column(String(50), nullable=True)
    # Options: very_liberal, liberal, moderate, conservative, very_conservative, apolitical
    
    # Has children
    has_children = Column(String(50), nullable=True)
    # Options: no, yes_living_with_me, yes_not_living_with_me
    
    # Wants children
    wants_children = Column(String(50), nullable=True)
    # Options: yes, no, maybe, already_have_them
    
    # Education
    education = Column(String(100), nullable=True)
    # Options: high_school, some_college, bachelors, masters, phd, other
    
    # Work
    work_field = Column(String(100), nullable=True)
    
    # Sleep schedule
    sleep_schedule = Column(String(50), nullable=True)
    # Options: early_bird, night_owl, flexible
    
    # Pet preference
    pets = Column(String(50), nullable=True)
    # Options: love_pets, allergic, have_pets, prefer_no_pets
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


class DateRecord(Base):
    """Track user's date history for AI analysis"""
    __tablename__ = 'date_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    match_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Date details
    date_number = Column(Integer, default=1)  # 1st date, 2nd date, etc.
    date_type = Column(String(100), nullable=True)  # coffee, dinner, walk, activity, etc.
    date_location = Column(String(255), nullable=True)
    date_date = Column(DateTime, nullable=True)  # When it happened
    
    # User's rating of the date (1-5)
    overall_rating = Column(Integer, nullable=True)
    connection_rating = Column(Integer, nullable=True)
    conversation_rating = Column(Integer, nullable=True)
    comfort_rating = Column(Integer, nullable=True)
    safety_rating = Column(Integer, nullable=True)
    
    # Feedback
    what_went_well = Column(Text, nullable=True)
    what_didnt_work = Column(Text, nullable=True)
    red_flags = Column(Text, nullable=True)  # JSON list
    green_flags = Column(Text, nullable=True)  # JSON list
    notes = Column(Text, nullable=True)
    
    # Outcome
    outcome = Column(String(50), nullable=True)
    # Options: want_second_date, not_interested, friendzoned, ghosted, rejected_by_them, still_deciding
    
    # AI Analysis
    ai_analysis = Column(Text, nullable=True)
    ai_suggestions = Column(Text, nullable=True)
    pattern_tags = Column(Text, nullable=True)  # JSON list of detected patterns
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])
    match_user = relationship('User', foreign_keys=[match_user_id])


class UserPatternAnalysis(Base):
    """AI-detected patterns from date history"""
    __tablename__ = 'user_pattern_analysis'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Patterns detected
    total_dates = Column(Integer, default=0)
    avg_connection_score = Column(Float, nullable=True)
    avg_comfort_score = Column(Float, nullable=True)
    avg_safety_score = Column(Float, nullable=True)
    second_date_rate = Column(Float, nullable=True)
    
    # Detected patterns
    common_red_flags = Column(Text, nullable=True)  # JSON
    common_green_flags = Column(Text, nullable=True)  # JSON
    recurring_issues = Column(Text, nullable=True)  # JSON
    strength_areas = Column(Text, nullable=True)  # JSON
    improvement_areas = Column(Text, nullable=True)  # JSON
    
    # AI recommendations
    ai_recommendations = Column(Text, nullable=True)
    
    # Compatibility insights
    best_date_types = Column(Text, nullable=True)  # What works best for them
    ideal_match_traits = Column(Text, nullable=True)
    
    last_analyzed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


class OpeningMove(Base):
    """Pre-written prompts for initiating conversation - like Bumble's Opening Moves"""
    __tablename__ = 'opening_moves'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    prompt = Column(Text, nullable=True)  # User's custom prompt
    # Default prompts: "What's your dream vacation?", "What book changed your life?", 
    # "What are your green and red flags?", "What's the last thing that made you smile?"
    
    is_active = Column(Boolean, default=True)
    response_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


class ContentFilter(Base):
    """Hidden words/content filter - like Hinge's Hidden Words"""
    __tablename__ = 'content_filters'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    word = Column(String(255), nullable=False)
    filter_type = Column(String(50), default='block')  # block, flag, warn
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])


# ============================================================
# RELATIONSHIP MODES & CONNECTION TESTS
# ============================================================

class RelationshipPreferences(Base):
    """User's relationship mode preferences"""
    __tablename__ = 'relationship_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Relationship mode
    relationship_mode = Column(String(50), nullable=False)
    # Options: serious, casual, one_night, friendship, marriage, open, emotional, intellectual
    
    # Additional preferences
    commitment_level = Column(String(50), nullable=True)  # high, medium, low
    communication_frequency = Column(String(50), nullable=True)  # daily, weekly, occasional
    meeting_frequency = Column(String(50), nullable=True)  # often, sometimes, rarely
    
    # Compatibility scores
    openness_score = Column(Float, nullable=True)  # 0-100
    compatibility_score = Column(Float, nullable=True)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])
    connection_tests = relationship('ConnectionTest', back_populates='relationship_pref')


class ConnectionTest(Base):
    """Connection compatibility test results"""
    __tablename__ = 'connection_tests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    relationship_pref_id = Column(Integer, ForeignKey('relationship_preferences.id'), nullable=False)
    
    # Test details
    test_type = Column(String(50), nullable=False)  # compatibility, readiness, values
    mode_specific = Column(Boolean, default=False)  # True if specific to relationship mode
    
    # Test results
    answers_json = Column(Text, nullable=False)  # JSON array of answers
    compatibility_score = Column(Integer, nullable=False)  # 0-100
    readiness_score = Column(Integer, nullable=True)  # 0-100
    values_alignment_score = Column(Integer, nullable=True)  # 0-100
    
    # AI Analysis
    ai_analysis = Column(Text, nullable=True)  # RAG-generated analysis
    strengths = Column(Text, nullable=True)  # JSON array
    areas_to_improve = Column(Text, nullable=True)  # JSON array
    recommendations = Column(Text, nullable=True)  # JSON array
    
    # Metadata
    completed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Tests expire after 30 days
    
    user = relationship('User', foreign_keys=[user_id])
    relationship_pref = relationship('RelationshipPreferences', back_populates='connection_tests')


# ============================================================
# ACADEMIC KNOWLEDGE BASE FOR RAG
# ============================================================

class AcademicKnowledge(Base):
    """Academic papers and research for RAG"""
    __tablename__ = 'academic_knowledge'
    
    id = Column(Integer, primary_key=True)
    
    # Source information
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=True)  # JSON array
    year = Column(Integer, nullable=True)
    source = Column(String(255), nullable=True)  # Journal, conference, etc.
    url = Column(String(500), nullable=True)
    
    # Content
    abstract = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)  # JSON array
    methodology = Column(String(255), nullable=True)
    sample_size = Column(Integer, nullable=True)
    
    # Relevance
    category = Column(String(100), nullable=True)  # safety, psychology, communication, etc.
    tags = Column(Text, nullable=True)  # JSON array of tags
    relevance_score = Column(Float, default=1.0)  # 0.0-1.0
    
    # Embedding for RAG
    embedding_text = Column(Text, nullable=True)  # Text used for embeddings
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatingNews(Base):
    """Dating news and trends for RAG"""
    __tablename__ = 'dating_news'
    
    id = Column(Integer, primary_key=True)
    
    # Source information
    title = Column(String(500), nullable=False)
    source = Column(String(255), nullable=True)  # News site, blog, etc.
    url = Column(String(500), nullable=True)
    published_date = Column(DateTime, nullable=True)
    
    # Content
    summary = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)
    
    # Relevance
    category = Column(String(100), nullable=True)  # trends, safety, technology, etc.
    tags = Column(Text, nullable=True)  # JSON array of tags
    relevance_score = Column(Float, default=1.0)
    
    # Embedding for RAG
    embedding_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatingRules(Base):
    """Dating rules and guidelines for RAG"""
    __tablename__ = 'dating_rules'
    
    id = Column(Integer, primary_key=True)
    
    # Rule information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Context
    category = Column(String(100), nullable=True)  # safety, etiquette, legal, cultural
    region = Column(String(100), nullable=True)  # Iran, global, specific country
    language = Column(String(10), default='fa')  # Rule language
    
    # Importance
    priority = Column(Integer, default=1)  # 1-5, 5 being most important
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Embedding for RAG
    embedding_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PersonalityCharacteristics(Base):
    """Personality traits and characteristics for matching"""
    __tablename__ = 'personality_characteristics'
    
    id = Column(Integer, primary_key=True)
    
    # Characteristic
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type
    characteristic_type = Column(String(100), nullable=True)  # personality, value, interest
    mbti_relevance = Column(Text, nullable=True)  # JSON array of MBTI types
    
    # Compatibility
    compatible_with = Column(Text, nullable=True)  # JSON array of characteristics
    incompatible_with = Column(Text, nullable=True)  # JSON array
    
    # Embedding for RAG
    embedding_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize the database and create all tables"""
    Base.metadata.create_all(engine)


def get_session():
    """Get a new database session"""
    return SessionLocal()
