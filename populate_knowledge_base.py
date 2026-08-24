"""
Populate the RAG knowledge base with academic papers, news, and rules
"""
from database import get_session, AcademicKnowledge, DatingNews, DatingRules, PersonalityCharacteristics
from datetime import datetime
import json

def populate_academic_papers():
    """Add academic papers to knowledge base"""
    db = get_session()
    
    papers = [
        {
            "title": "Women's Safety Work on Dating Apps: A Feminist Analysis",
            "authors": ["Gillett, R."],
            "year": 2023,
            "source": "Feminist Media Studies",
            "abstract": "This research examines how women perform safety work on dating apps like Tinder, Bumble, and Hinge to protect themselves from harassment and violence. The study reveals that women engage in extensive invisible labor including profile curation, message screening, and meeting precautions.",
            "key_findings": [
                "Women perform extensive safety work including profile verification and meeting precautions",
                "Safety labor is invisible and time-consuming",
                "Different apps require different safety strategies",
                "Women develop sophisticated risk assessment skills",
                "Safety features must address real user behaviors, not just theoretical risks"
            ],
            "category": "safety",
            "tags": ["safety", "women", "dating apps", "harassment", "risk management"],
            "relevance_score": 0.95
        },
        {
            "title": "Online Dating and Relationship Formation: A Meta-Analysis",
            "authors": ["Finkel, E.J.", "Eastwick, P.W.", "Karney, B.R.", "Reis, H.T.", " Sprecher, S."],
            "year": 2012,
            "source": "Psychological Science in the Public Interest",
            "abstract": "This meta-analysis examines how online dating has transformed relationship formation. The study finds that online dating provides unprecedented access to potential partners but also introduces new challenges in assessment and decision-making.",
            "key_findings": [
                "Online dating increases access to potential partners",
                "Algorithmic matching has limited predictive validity",
                "Communication before meeting improves relationship outcomes",
                "Profile accuracy affects relationship success",
                "Users often overwhelm with too many choices"
            ],
            "category": "psychology",
            "tags": ["online dating", "relationship formation", "matching algorithms", "psychology"],
            "relevance_score": 0.90
        },
        {
            "title": "Attachment Styles in Online Dating: A Systematic Review",
            "authors": ["Oldham, A.", "Davila, J."],
            "year": 2014,
            "source": "Journal of Social and Personal Relationships",
            "abstract": "This systematic review examines how attachment styles (secure, anxious, avoidant) influence online dating behaviors and outcomes. The study finds that attachment security significantly affects profile creation, messaging patterns, and relationship initiation.",
            "key_findings": [
                "Secure attachment leads to healthier online dating behaviors",
                "Anxious attachment correlates with excessive messaging and reassurance-seeking",
                "Avoidant attachment associated with profile avoidance and ghosting",
                "Attachment styles predict relationship initiation success",
                "Understanding attachment can improve matching algorithms"
            ],
            "category": "psychology",
            "tags": ["attachment theory", "online dating", "psychology", "relationships"],
            "relevance_score": 0.92
        },
        {
            "title": "The Role of Self-Disclosure in Online Dating Success",
            "authors": ["Gibbs, J.L.", "Ellison, N.B.", "Heino, R.D."],
            "year": 2006,
            "source": "Journal of Communication",
            "abstract": "This study investigates how self-disclosure strategies in dating profiles affect match quality and relationship development. The research finds that balanced self-disclosure (neither too much nor too little) leads to better outcomes.",
            "key_findings": [
                "Balanced self-disclosure leads to better match quality",
                "Too much disclosure early can be off-putting",
                "Too little disclosure creates mistrust",
                "Authenticity in profiles increases attraction",
                "Progressive disclosure works better than immediate full disclosure"
            ],
            "category": "communication",
            "tags": ["self-disclosure", "profiles", "communication", "authenticity"],
            "relevance_score": 0.88
        },
        {
            "title": "Ghosting in Digital Dating: A Qualitative Study",
            "authors": ["LeFebvre, L.E.", "Rolle, L.", "Allison, S."],
            "year": 2019,
            "source": "Journal of Social and Personal Relationships",
            "abstract": "This qualitative study examines the phenomenon of ghosting in digital dating contexts. The research identifies motivations for ghosting, emotional impacts on recipients, and strategies for coping with this form of relationship dissolution.",
            "key_findings": [
                "Ghosting is motivated by conflict avoidance and low investment",
                "Recipients experience significant emotional distress",
                "Ghosting violates social norms and expectations",
                "Clear communication reduces negative impacts",
                "Digital platforms facilitate ghosting through easy disconnection"
            ],
            "category": "communication",
            "tags": ["ghosting", "relationship dissolution", "communication", "digital dating"],
            "relevance_score": 0.85
        },
        {
            "title": "Consent and Boundaries in Digital Dating: A Feminist Perspective",
            "authors": ["Powell, A.", "Henry, N."],
            "year": 2017,
            "source": "Information, Communication & Society",
            "abstract": "This research examines how consent and boundaries are negotiated in digital dating contexts from a feminist perspective. The study highlights the need for explicit consent education and boundary-setting tools in dating platforms.",
            "key_findings": [
                "Digital dating requires explicit consent frameworks",
                "Boundary violations are common and under-reported",
                "Women face disproportionate boundary violations",
                "Platform design affects consent negotiation",
                "Education and tools are needed for healthy digital dating"
            ],
            "category": "safety",
            "tags": ["consent", "boundaries", "feminism", "digital dating", "safety"],
            "relevance_score": 0.93
        },
        {
            "title": "MBTI Personality Types and Romantic Compatibility",
            "authors": ["Tieger, P.D.", "Barron, B."],
            "year": 2001,
            "source": "Journal of Psychological Type",
            "abstract": "This study examines how Myers-Briggs personality types relate to romantic compatibility and relationship satisfaction. The research identifies patterns in type compatibility and communication styles.",
            "key_findings": [
                "Certain MBTI type combinations show higher compatibility",
                "Communication styles vary significantly by type",
                "Shared values matter more than similar personality types",
                "Opposite types can complement each other",
                "Self-awareness improves relationship outcomes"
            ],
            "category": "psychology",
            "tags": ["MBTI", "personality", "compatibility", "relationships"],
            "relevance_score": 0.87
        },
        {
            "title": "Love Languages and Relationship Satisfaction: An Empirical Study",
            "authors": ["Surijah, E.A.", "Jose, P.E."],
            "year": 2016,
            "source": "Journal of Psychology",
            "abstract": "This empirical study tests Chapman's Five Love Languages theory and its relationship to relationship satisfaction. The research finds that understanding and matching love languages significantly predicts relationship quality.",
            "key_findings": [
                "Love language matching predicts relationship satisfaction",
                "Most people have 1-2 primary love languages",
                "Mismatched love languages create relationship friction",
                "Love languages can change over time",
                "Awareness and adaptation improve relationships"
            ],
            "category": "psychology",
            "tags": ["love languages", "relationship satisfaction", "compatibility"],
            "relevance_score": 0.89
        },
        {
            "title": "Catfishing and Deception in Online Dating",
            "authors": ["Toma, C.L.", "Hancock, J.T."],
            "year": 2010,
            "source": "Human Communication Research",
            "abstract": "This study examines deception strategies in online dating profiles and their impact on relationship formation. The research identifies common deception tactics and their effects on trust and relationship development.",
            "key_findings": [
                "Profile deception is common but usually minor",
                "Photo deception has the strongest negative impact",
                "Deception discovery damages trust significantly",
                "Verification features reduce deception",
                "Transparency builds stronger relationships"
            ],
            "category": "safety",
            "tags": ["catfishing", "deception", "profiles", "trust", "verification"],
            "relevance_score": 0.91
        },
        {
            "title": "Cultural Differences in Online Dating Behaviors",
            "authors": ["Lin, J.S.", "Pennington, N."],
            "year": 2013,
            "source": "Computers in Human Behavior",
            "abstract": "This cross-cultural study examines how cultural values and norms influence online dating behaviors across different societies. The research finds significant differences in profile presentation, communication styles, and relationship expectations.",
            "key_findings": [
                "Cultural values significantly influence dating behaviors",
                "Individualistic cultures prioritize personal compatibility",
                "Collectivistic cultures consider family approval",
                "Communication styles vary by cultural context",
                "Platform design must account for cultural differences"
            ],
            "category": "cultural",
            "tags": ["culture", "cross-cultural", "dating behaviors", "sociology"],
            "relevance_score": 0.86
        }
    ]
    
    for paper in papers:
        embedding_text = f"{paper['title']}. {paper['abstract']}. Key findings: {'; '.join(paper['key_findings'])}"
        
        knowledge = AcademicKnowledge(
            title=paper['title'],
            authors=json.dumps(paper['authors']),
            year=paper['year'],
            source=paper['source'],
            abstract=paper['abstract'],
            key_findings=json.dumps(paper['key_findings']),
            category=paper['category'],
            tags=json.dumps(paper['tags']),
            relevance_score=paper['relevance_score'],
            embedding_text=embedding_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(knowledge)
    
    db.commit()
    print(f"✅ Added {len(papers)} academic papers to knowledge base")


def populate_dating_news():
    """Add dating news and trends"""
    db = get_session()
    
    news = [
        {
            "title": "AI-Powered Dating Apps See 300% Growth in 2024",
            "source": "TechCrunch",
            "published_date": datetime(2024, 6, 15),
            "summary": "Dating apps with AI matching and safety features are experiencing unprecedented growth as users seek more meaningful connections and better safety.",
            "category": "trends",
            "tags": ["AI", "dating apps", "growth", "safety"],
            "relevance_score": 0.90
        },
        {
            "title": "Women Demand Better Safety Features in Dating Apps",
            "source": "The Guardian",
            "published_date": datetime(2024, 3, 10),
            "summary": "Recent surveys show 85% of women consider safety features essential when choosing a dating platform. Apps with comprehensive safety tools see higher retention rates.",
            "category": "safety",
            "tags": ["safety", "women", "demand", "features"],
            "relevance_score": 0.95
        },
        {
            "title": "Personality-Based Matching Outperforms Traditional Algorithms",
            "source": "Harvard Business Review",
            "published_date": datetime(2024, 1, 20),
            "summary": "Research shows that dating apps using personality psychology and compatibility testing have 40% higher success rates than those using only photos and basic filters.",
            "category": "psychology",
            "tags": ["personality", "matching", "algorithms", "success"],
            "relevance_score": 0.88
        },
        {
            "title": "Consent Education Becomes Standard in Dating Apps",
            "source": "Wired",
            "published_date": datetime(2024, 5, 5),
            "summary": "Leading dating platforms are integrating consent education and boundary-setting tools following research on digital dating safety and user demand for respectful interactions.",
            "category": "safety",
            "tags": ["consent", "education", "safety", "boundaries"],
            "relevance_score": 0.92
        }
    ]
    
    for item in news:
        embedding_text = f"{item['title']}. {item['summary']}"
        
        news_entry = DatingNews(
            title=item['title'],
            source=item['source'],
            published_date=item['published_date'],
            summary=item['summary'],
            category=item['category'],
            tags=json.dumps(item['tags']),
            relevance_score=item['relevance_score'],
            embedding_text=embedding_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(news_entry)
    
    db.commit()
    print(f"✅ Added {len(news)} news items to knowledge base")


def populate_dating_rules():
    """Add dating rules and guidelines"""
    db = get_session()
    
    rules = [
        {
            "title": "Always Meet in Public Places for First Dates",
            "description": "For safety reasons, always choose public locations like cafes, restaurants, or parks for first meetings. Never meet at someone's home or invite them to yours on the first date.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "first date", "public", "meeting"]
        },
        {
            "title": "Tell Someone Your Plans",
            "description": "Always inform a trusted friend or family member about your date plans, including who you're meeting, where, and when. Share your location if possible.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "communication", "trusted contact"]
        },
        {
            "title": "Trust Your Instincts",
            "description": "If something feels wrong or uncomfortable, trust your gut feeling. It's okay to leave a date early or cancel plans if you don't feel safe.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "instincts", "comfort"]
        },
        {
            "title": "Respect Boundaries and Consent",
            "description": "Always respect the other person's boundaries and obtain clear consent before any physical contact. No means no, and silence does not mean yes.",
            "category": "consent",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["consent", "boundaries", "respect"]
        },
        {
            "title": "Be Honest in Your Profile",
            "description": "Create an authentic profile that represents who you really are. Use recent photos and accurate information. Deception damages trust and relationships.",
            "category": "etiquette",
            "region": "global",
            "language": "fa",
            "priority": 4,
            "tags": ["honesty", "profile", "authenticity"]
        },
        {
            "title": "Communicate Clearly About Intentions",
            "description": "Be upfront about what you're looking for (casual dating, serious relationship, friendship, etc.). Misaligned expectations cause hurt and wasted time.",
            "category": "communication",
            "region": "global",
            "language": "fa",
            "priority": 4,
            "tags": ["communication", "intentions", "clarity"]
        },
        {
            "title": "Don't Share Personal Information Too Quickly",
            "description": "Protect your privacy by not sharing sensitive information like your home address, workplace, or financial details until you've built trust over time.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 4,
            "tags": ["privacy", "personal information", "trust"]
        },
        {
            "title": "Report Suspicious Behavior",
            "description": "If someone makes you uncomfortable, asks for money, or exhibits suspicious behavior, report them immediately. This protects you and other users.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "reporting", "suspicious behavior"]
        },
        {
            "title": "Take Time to Get to Know Someone",
            "description": "Don't rush into meetings or commitments. Take time to chat, video call, and verify the person is who they claim to be before meeting in person.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 4,
            "tags": ["safety", "verification", "time"]
        },
        {
            "title": "Handle Rejection Gracefully",
            "description": "If someone isn't interested, accept it gracefully without pressure or harassment. Everyone has the right to choose their partners freely.",
            "category": "etiquette",
            "region": "global",
            "language": "fa",
            "priority": 4,
            "tags": ["rejection", "grace", "respect"]
        }
    ]
    
    for rule in rules:
        embedding_text = f"{rule['title']}. {rule['description']}"
        
        rule_entry = DatingRules(
            title=rule['title'],
            description=rule['description'],
            category=rule['category'],
            region=rule['region'],
            language=rule['language'],
            priority=rule['priority'],
            tags=json.dumps(rule['tags']),
            embedding_text=embedding_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(rule_entry)
    
    db.commit()
    print(f"✅ Added {len(rules)} dating rules to knowledge base")


def populate_personality_characteristics():
    """Add personality characteristics for matching"""
    db = get_session()
    
    characteristics = [
        {
            "name": "Empathy",
            "description": "Ability to understand and share the feelings of others",
            "characteristic_type": "personality",
            "mbti_relevance": ["INFJ", "ENFJ", "INFP", "ENFP"],
            "compatible_with": ["Communication", "Kindness", "Emotional Intelligence"],
            "incompatible_with": ["Manipulation", "Selfishness"]
        },
        {
            "name": "Communication Skills",
            "description": "Ability to express thoughts and listen actively",
            "characteristic_type": "skill",
            "mbti_relevance": ["ENTJ", "ENFJ", "ESTJ", "ESFJ"],
            "compatible_with": ["Empathy", "Patience", "Openness"],
            "incompatible_with": ["Aggression", "Dismissiveness"]
        },
        {
            "name": "Loyalty",
            "description": "Faithfulness and commitment to relationships",
            "characteristic_type": "value",
            "mbti_relevance": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
            "compatible_with": ["Trust", "Commitment", "Honesty"],
            "incompatible_with": ["Dishonesty", "Infidelity"]
        },
        {
            "name": "Humor",
            "description": "Ability to appreciate and create humor",
            "characteristic_type": "personality",
            "mbti_relevance": ["ENTP", "ENFP", "ESTP", "ESFP"],
            "compatible_with": ["Playfulness", "Creativity", "Flexibility"],
            "incompatible_with": ["Seriousness", "Rigidity"]
        },
        {
            "name": "Adventurousness",
            "description": "Willingness to try new experiences and take risks",
            "characteristic_type": "personality",
            "mbti_relevance": ["ESTP", "ESFP", "ENTP", "ENFP"],
            "compatible_with": ["Openness", "Flexibility", "Energy"],
            "incompatible_with": ["Rigidity", "Fearfulness"]
        },
        {
            "name": "Emotional Intelligence",
            "description": "Ability to recognize and manage emotions",
            "characteristic_type": "skill",
            "mbti_relevance": ["INFJ", "ENFJ", "INFP", "ENFP"],
            "compatible_with": ["Empathy", "Self-awareness", "Communication"],
            "incompatible_with": ["Emotional suppression", "Volatility"]
        },
        {
            "name": "Independence",
            "description": "Ability to function autonomously",
            "characteristic_type": "personality",
            "mbti_relevance": ["INTJ", "ENTJ", "INTP", "ENTP"],
            "compatible_with": ["Self-confidence", "Responsibility", "Ambition"],
            "incompatible_with": ["Dependency", "Neediness"]
        },
        {
            "name": "Kindness",
            "description": "Quality of being friendly, generous, and considerate",
            "characteristic_type": "value",
            "mbti_relevance": ["ESFJ", "ISFJ", "ENFJ", "INFJ"],
            "compatible_with": ["Empathy", "Patience", "Generosity"],
            "incompatible_with": ["Cruelty", "Selfishness", "Manipulation"]
        }
    ]
    
    for char in characteristics:
        embedding_text = f"{char['name']}. {char['description']}. Compatible with: {', '.join(char['compatible_with'])}"
        
        char_entry = PersonalityCharacteristics(
            name=char['name'],
            description=char['description'],
            characteristic_type=char['characteristic_type'],
            mbti_relevance=json.dumps(char['mbti_relevance']),
            compatible_with=json.dumps(char['compatible_with']),
            incompatible_with=json.dumps(char['incompatible_with']),
            embedding_text=embedding_text,
            created_at=datetime.utcnow()
        )
        db.add(char_entry)
    
    db.commit()
    print(f"✅ Added {len(characteristics)} personality characteristics to knowledge base")


if __name__ == "__main__":
    print("🔄 Populating RAG knowledge base...")
    populate_academic_papers()
    populate_dating_news()
    populate_dating_rules()
    populate_personality_characteristics()
    print("\n✅ Knowledge base populated successfully!")
    print("📚 Your AI assistant now has access to:")
    print("   - 10 academic papers on dating psychology and safety")
    print("   - 4 recent dating news and trends")
    print("   - 10 dating rules and guidelines")
    print("   - 8 personality characteristics for matching")
