"""
HuggingFace RAG (Retrieval-Augmented Generation) with Knowledge Base
====================================================================
Uses HuggingFace Inference API with knowledge base from academic papers,
dating news, rules, and personality characteristics.
"""
import aiohttp
import json
import logging
from typing import List, Dict, Optional
from config import HUGGINGFACE_API_KEY, HUGGINGFACE_API_KEY_2
from database import get_session, AcademicKnowledge, DatingNews, DatingRules, PersonalityCharacteristics
from sqlalchemy import or_

logger = logging.getLogger(__name__)


class HuggingFaceRAG:
    """RAG system using HuggingFace models with knowledge base"""
    
    def __init__(self):
        self.api_keys = [k for k in [HUGGINGFACE_API_KEY, HUGGINGFACE_API_KEY_2] if k and k != 'hf_your_token_here']
        self.current_key_index = 0
        self.base_url = "https://api-inference.huggingface.co"
        
        # Models to try in order
        self.models = [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "HuggingFaceH4/zephyr-7b-beta",
            "microsoft/DialoGPT-large"
        ]
        self.current_model_index = 0
        
        logger.info(f"Initialized HuggingFace RAG with {len(self.api_keys)} API keys")
    
    async def query(self, question: str, language: str = 'fa', context: dict = None) -> Optional[str]:
        """
        Query the AI with knowledge base context
        
        Args:
            question: User's question
            language: Language code
            context: User profile context
        
        Returns:
            AI response or None
        """
        # Retrieve relevant knowledge from database
        knowledge_context = self._retrieve_knowledge(question, language)
        
        # Build RAG prompt
        prompt = self._build_rag_prompt(question, knowledge_context, language, context)
        
        # Try each API key and model
        for key_attempt in range(len(self.api_keys)):
            for model_attempt in range(len(self.models)):
                key_index = (self.current_key_index + key_attempt) % len(self.api_keys)
                model_index = (self.current_model_index + model_attempt) % len(self.models)
                
                api_key = self.api_keys[key_index]
                model = self.models[model_index]
                
                try:
                    response = await self._call_huggingface_model(model, prompt, api_key)
                    if response:
                        self.current_key_index = key_index
                        self.current_model_index = model_index
                        return response
                except Exception as e:
                    logger.warning(f"Model {model} with key {key_index} failed: {e}")
                    continue
        
        return None
    
    def _retrieve_knowledge(self, question: str, language: str) -> Dict:
        """
        Retrieve relevant knowledge from database based on question
        """
        db = get_session()
        knowledge = {
            'academic': [],
            'news': [],
            'rules': [],
            'characteristics': []
        }
        
        try:
            # Extract keywords from question
            keywords = self._extract_keywords(question, language)
            
            # Retrieve academic papers
            academic_papers = db.query(AcademicKnowledge).filter(
                or_(
                    AcademicKnowledge.title.ilike(f'%{kw}%') for kw in keywords
                ) | or_(
                    AcademicKnowledge.category.ilike(f'%{kw}%') for kw in keywords
                )
            ).order_by(AcademicKnowledge.relevance_score.desc()).limit(3).all()
            
            for paper in academic_papers:
                knowledge['academic'].append({
                    'title': paper.title,
                    'year': paper.year,
                    'findings': json.loads(paper.key_findings) if paper.key_findings else [],
                    'abstract': paper.abstract
                })
            
            # Retrieve dating news
            news_items = db.query(DatingNews).filter(
                or_(
                    DatingNews.title.ilike(f'%{kw}%') for kw in keywords
                ) | or_(
                    DatingNews.category.ilike(f'%{kw}%') for kw in keywords
                )
            ).order_by(DatingNews.relevance_score.desc()).limit(2).all()
            
            for news in news_items:
                knowledge['news'].append({
                    'title': news.title,
                    'summary': news.summary,
                    'date': news.published_date.strftime('%Y-%m-%d') if news.published_date else None
                })
            
            # Retrieve dating rules
            rules = db.query(DatingRules).filter(
                or_(
                    DatingRules.title.ilike(f'%{kw}%') for kw in keywords
                ) | or_(
                    DatingRules.category.ilike(f'%{kw}%') for kw in keywords
                )
            ).order_by(DatingRules.priority.desc()).limit(5).all()
            
            for rule in rules:
                knowledge['rules'].append({
                    'title': rule.title,
                    'description': rule.description,
                    'priority': rule.priority
                })
            
            # Retrieve personality characteristics
            characteristics = db.query(PersonalityCharacteristics).filter(
                or_(
                    PersonalityCharacteristics.name.ilike(f'%{kw}%') for kw in keywords
                ) | or_(
                    PersonalityCharacteristics.characteristic_type.ilike(f'%{kw}%') for kw in keywords
                )
            ).limit(3).all()
            
            for char in characteristics:
                knowledge['characteristics'].append({
                    'name': char.name,
                    'description': char.description,
                    'type': char.characteristic_type,
                    'compatible_with': json.loads(char.compatible_with) if char.compatible_with else []
                })
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
        finally:
            db.close()
        
        return knowledge
    
    def _extract_keywords(self, question: str, language: str) -> List[str]:
        """Extract keywords from question for knowledge retrieval"""
        # Simple keyword extraction - can be enhanced with NLP
        keywords = []
        
        # Common dating-related keywords
        keyword_map = {
            'fa': {
                'safety': ['امنیت', 'ایمنی', 'حفاظت', 'danger', 'خطر'],
                'psychology': ['روانشناسی', 'شخصیت', 'رفتار', 'psychology', 'personality'],
                'communication': ['ارتباط', 'گفتگو', 'صحبت', 'communication', 'conversation'],
                'compatibility': ['سازگاری', 'تطابق', 'compatible', 'compatibility'],
                'relationship': ['رابطه', 'دوستی', 'عشق', 'relationship', 'love'],
                'dating': ['قرار', 'دیت', 'ملاقات', 'date', 'meeting'],
                'profile': ['پروفایل', 'معرفی', 'profile'],
                'trust': ['اعتماد', 'صداقت', 'trust', 'honesty'],
                'consent': ['رضایت', 'اجازه', 'consent', 'permission']
            },
            'en': {
                'safety': ['safety', 'safe', 'danger', 'protection', 'security'],
                'psychology': ['psychology', 'personality', 'behavior', 'mental'],
                'communication': ['communication', 'conversation', 'talk', 'chat'],
                'compatibility': ['compatibility', 'compatible', 'match', 'fit'],
                'relationship': ['relationship', 'love', 'dating', 'partner'],
                'dating': ['date', 'dating', 'meeting', 'first date'],
                'profile': ['profile', 'bio', 'introduction'],
                'trust': ['trust', 'honesty', 'sincere', 'genuine'],
                'consent': ['consent', 'permission', 'agreement', 'boundaries']
            }
        }
        
        lang_keywords = keyword_map.get(language, keyword_map['en'])
        
        # Check which categories the question relates to
        for category, category_keywords in lang_keywords.items():
            for kw in category_keywords:
                if kw.lower() in question.lower():
                    keywords.extend([category, kw])
                    break
        
        # Add original words from question
        words = question.lower().split()
        keywords.extend([w for w in words if len(w) > 3])
        
        return list(set(keywords))  # Remove duplicates
    
    def _build_rag_prompt(self, question: str, knowledge: Dict, language: str, context: dict = None) -> str:
        """Build RAG prompt with knowledge context"""
        
        # System prompts based on language
        system_prompts = {
            'fa': 'تو یک دستیار هوشمند دوستیابی هستی که بر اساس تحقیقات علمی و مقالات دانشگاهی پاسخ می‌دهی. از اطلاعات ارائه شده استفاده کن و پاسخ دقیق و کاربردی بده. به فارسی پاسخ بده.',
            'en': 'You are a smart dating assistant that responds based on scientific research and academic papers. Use the provided information to give accurate and practical responses. Reply in English.',
            'sv': 'Du är en smart dejtingassistent som svarar baserat på vetenskaplig forskning och akademiska artiklar. Använd den tillhandahållna informationen för att ge korrekta och praktiska svar. Svara på svenska.',
            'de': 'Du bist ein intelligenter Dating-Assistent, der auf wissenschaftlicher Forschung und akademischen Arbeiten basiert. Verwende die bereitgestellten Informationen, um genaue und praktische Antworten zu geben. Antworte auf Deutsch.',
            'tr': 'Bilimsel araştırmalara ve akademik makalelere dayalı yanıtlar veren akıllı bir flört asistanısın. Sağlanan bilgileri kullanarak doğru ve pratik yanıtlar ver. Türkçe cevap ver.',
            'ar': 'أنت مساعد ذكي للتعارف تستجيب بناءً على البحث العلمي والأوراق الأكاديمية. استخدم المعلومات المقدمة لتقديم ردود دقيقة وعملية. أجب بالعربية.',
            'fr': 'Tu es un assistant de rencontres intelligent qui répond en fonction de la recherche scientifique et des articles académiques. Utilise les informations fournies pour donner des réponses précises et pratiques. Réponds en français.',
            'es': 'Eres un asistente inteligente de citas que responde basándose en investigaciones científicas y artículos académicos. Utiliza la información proporcionada para dar respuestas precisas y prácticas. Responde en español.',
            'ku': 'تۆ یاریدەدەرێکی زیرەکی دۆستابیت کە بە پشتبەستن بە توێژینەوەی زانستی و بابەتە ئەکادیمییەکان وەڵام دەدەیتەوە. زانیارییە دابینکراوەکان بەکاربهێنە بۆ وەڵامی ورد و بەکارهاتوو. بە کوردی وەڵام بدەوە.'
        }
        
        system_prompt = system_prompts.get(language, system_prompts['en'])
        
        # Build knowledge context
        knowledge_text = ""
        
        # Add academic papers
        if knowledge['academic']:
            knowledge_text += "\n\n📚 Relevant Academic Research:\n"
            for paper in knowledge['academic'][:2]:
                knowledge_text += f"- {paper['title']} ({paper['year']})\n"
                if paper['findings']:
                    knowledge_text += f"  Key findings: {'; '.join(paper['findings'][:2])}\n"
        
        # Add dating rules
        if knowledge['rules']:
            knowledge_text += "\n\n💡 Dating Guidelines:\n"
            for rule in knowledge['rules'][:3]:
                knowledge_text += f"- {rule['title']}: {rule['description']}\n"
        
        # Add characteristics
        if knowledge['characteristics']:
            knowledge_text += "\n\n🎯 Personality Traits:\n"
            for char in knowledge['characteristics'][:2]:
                knowledge_text += f"- {char['name']}: {char['description']}\n"
                if char['compatible_with']:
                    knowledge_text += f"  Compatible with: {', '.join(char['compatible_with'][:3])}\n"
        
        # Add recent news
        if knowledge['news']:
            knowledge_text += "\n\n📰 Recent Trends:\n"
            for news in knowledge['news'][:2]:
                knowledge_text += f"- {news['title']}: {news['summary']}\n"
        
        # Build user context
        user_context = ""
        if context:
            if context.get('name'):
                user_context += f"\nUser: {context['name']}"
            if context.get('age'):
                user_context += f", Age: {context['age']}"
            if context.get('city'):
                user_context += f", City: {context['city']}"
        
        # Build full prompt
        prompt = f"""{system_prompt}{user_context}{knowledge_text}

Question: {question}

Please provide a helpful, accurate response based on the research and guidelines above. Keep it concise and practical:"""
        
        return prompt
    
    async def _call_huggingface_model(self, model: str, prompt: str, api_key: str) -> Optional[str]:
        """Call a HuggingFace model"""
        url = f"{self.base_url}/models/{model}"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get('generated_text', '').strip()
                elif resp.status == 503:
                    raise Exception("Model loading")
                else:
                    error_text = await resp.text()
                    raise Exception(f"HuggingFace error {resp.status}: {error_text}")
        
        return None


# Global instance
hf_rag = HuggingFaceRAG()
