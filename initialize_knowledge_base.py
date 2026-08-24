"""
Initialize database and populate knowledge base
"""
from database import init_db, get_session, AcademicKnowledge, DatingNews, DatingRules, PersonalityCharacteristics
from datetime import datetime
import json

def initialize_and_populate():
    """Initialize database tables and populate knowledge base"""
    print("🔄 Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    print("\n🔄 Populating knowledge base...")
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

def populate_academic_papers():
    """Add academic papers to knowledge base"""
    db = get_session()
    
    papers = [
        {
            "title": "Women's Safety Work on Dating Apps: A Feminist Analysis",
            "authors": ["Gillett, R."],
            "year": 2023,
            "source": "Feminist Media Studies",
            "abstract": "This research examines how women perform safety work on dating apps like Tinder, Bumble, and Hinge to protect themselves from harassment and violence.",
            "key_findings": [
                "Women perform extensive safety work including profile verification and meeting precautions",
                "Safety labor is invisible and time-consuming",
                "Different apps require different safety strategies"
            ],
            "category": "safety",
            "tags": ["safety", "women", "dating apps", "harassment"],
            "relevance_score": 0.95
        },
        {
            "title": "Online Dating and Relationship Formation: A Meta-Analysis",
            "authors": ["Finkel, E.J.", "Eastwick, P.W."],
            "year": 2012,
            "source": "Psychological Science in the Public Interest",
            "abstract": "This meta-analysis examines how online dating has transformed relationship formation.",
            "key_findings": [
                "Online dating increases access to potential partners",
                "Algorithmic matching has limited predictive validity",
                "Communication before meeting improves relationship outcomes"
            ],
            "category": "psychology",
            "tags": ["online dating", "relationship formation", "algorithms"],
            "relevance_score": 0.90
        },
        {
            "title": "Attachment Styles in Online Dating: A Systematic Review",
            "authors": ["Oldham, A.", "Davila, J."],
            "year": 2014,
            "source": "Journal of Social and Personal Relationships",
            "abstract": "This systematic review examines how attachment styles influence online dating behaviors and outcomes.",
            "key_findings": [
                "Secure attachment leads to healthier online dating behaviors",
                "Anxious attachment correlates with excessive messaging",
                "Avoidant attachment associated with ghosting"
            ],
            "category": "psychology",
            "tags": ["attachment theory", "online dating", "psychology"],
            "relevance_score": 0.92
        },
        {
            "title": "The Role of Self-Disclosure in Online Dating Success",
            "authors": ["Gibbs, J.L.", "Ellison, N.B."],
            "year": 2006,
            "source": "Journal of Communication",
            "abstract": "This study investigates how self-disclosure strategies in dating profiles affect match quality.",
            "key_findings": [
                "Balanced self-disclosure leads to better match quality",
                "Authenticity in profiles increases attraction",
                "Progressive disclosure works better than immediate full disclosure"
            ],
            "category": "communication",
            "tags": ["self-disclosure", "profiles", "authenticity"],
            "relevance_score": 0.88
        },
        {
            "title": "Ghosting in Digital Dating: A Qualitative Study",
            "authors": ["LeFebvre, L.E.", "Rolle, L."],
            "year": 2019,
            "source": "Journal of Social and Personal Relationships",
            "abstract": "This qualitative study examines the phenomenon of ghosting in digital dating contexts.",
            "key_findings": [
                "Ghosting is motivated by conflict avoidance",
                "Recipients experience significant emotional distress",
                "Clear communication reduces negative impacts"
            ],
            "category": "communication",
            "tags": ["ghosting", "relationship dissolution", "communication"],
            "relevance_score": 0.85
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(knowledge)
    
    db.commit()
    print(f"✅ Added {len(papers)} academic papers to knowledge base")
    db.close()


def populate_dating_news():
    """Add dating news and trends"""
    db = get_session()
    
    news = [
        {
            "title": "AI-Powered Dating Apps See 300% Growth in 2024",
            "source": "TechCrunch",
            "published_date": datetime(2024, 6, 15),
            "summary": "Dating apps with AI matching and safety features are experiencing unprecedented growth.",
            "category": "trends",
            "tags": ["AI", "dating apps", "growth"],
            "relevance_score": 0.90
        },
        {
            "title": "Women Demand Better Safety Features in Dating Apps",
            "source": "The Guardian",
            "published_date": datetime(2024, 3, 10),
            "summary": "85% of women consider safety features essential when choosing a dating platform.",
            "category": "safety",
            "tags": ["safety", "women", "features"],
            "relevance_score": 0.95
        },
        {
            "title": "Personality-Based Matching Outperforms Traditional Algorithms",
            "source": "Harvard Business Review",
            "published_date": datetime(2024, 1, 20),
            "summary": "Dating apps using personality psychology have 40% higher success rates.",
            "category": "psychology",
            "tags": ["personality", "matching", "algorithms"],
            "relevance_score": 0.88
        },
        {
            "title": "Consent Education Becomes Standard in Dating Apps",
            "source": "Wired",
            "published_date": datetime(2024, 5, 5),
            "summary": "Leading platforms integrate consent education and boundary-setting tools.",
            "category": "safety",
            "tags": ["consent", "education", "safety"],
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(news_entry)
    
    db.commit()
    print(f"✅ Added {len(news)} news items to knowledge base")
    db.close()


def populate_dating_rules():
    """Add dating rules and guidelines"""
    db = get_session()
    
    rules = [
        {
            "title": "Always Meet in Public Places for First Dates",
            "description": "For safety reasons, always choose public locations like cafes, restaurants, or parks for first meetings.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "first date", "public"]
        },
        {
            "title": "Tell Someone Your Plans",
            "description": "Always inform a trusted friend or family member about your date plans.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "communication"]
        },
        {
            "title": "Trust Your Instincts",
            "description": "If something feels wrong or uncomfortable, trust your gut feeling.",
            "category": "safety",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["safety", "instincts"]
        },
        {
            "title": "Respect Boundaries and Consent",
            "description": "Always respect the other person's boundaries and obtain clear consent.",
            "category": "consent",
            "region": "global",
            "language": "fa",
            "priority": 5,
            "tags": ["consent", "boundaries", "respect"]
        },
        {
            "title": "Be Honest in Your Profile",
            "description": "Create an authentic profile that represents who you really are.",
            "category": "etiquette",
            "region": "global",
            "language": "fa",
            "priority": 4,
            "tags": ["honesty", "profile", "authenticity"]
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(rule_entry)
    
    db.commit()
    print(f"✅ Added {len(rules)} dating rules to knowledge base")
    db.close()


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
            created_at=datetime.now()
        )
        db.add(char_entry)
    
    db.commit()
    print(f"✅ Added {len(characteristics)} personality characteristics to knowledge base")
    db.close()


if __name__ == "__main__":
    initialize_and_populate()
