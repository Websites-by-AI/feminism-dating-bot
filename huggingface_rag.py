"""
RAG (Retrieval-Augmented Generation) with Academic Knowledge Base
=================================================================
Retrieves relevant peer-reviewed safety & psychology research from SQLite/SQLAlchemy
and generates responses via:
  1. Cloudflare Workers AI Edge RAG (Mistral-Small-3.1-24B / Llama-3.3-70B)
  2. HuggingFace Inference Router (https://router.huggingface.co/v1/chat/completions)
  3. Deterministic Local Academic Knowledge Synthesis (offline fallback)
"""
import aiohttp
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy import or_
from config import (
    HUGGINGFACE_API_KEY,
    HUGGINGFACE_API_KEY_2,
    CLOUDFLARE_API_URL,
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_API_TOKEN,
)
from database import (
    get_session,
    AcademicKnowledge,
    DatingNews,
    DatingRules,
    PersonalityCharacteristics,
)

logger = logging.getLogger(__name__)


class HuggingFaceRAG:
    """Multilingual Academic RAG engine with Cloudflare Workers AI + HuggingFace Router"""

    def __init__(self):
        self.api_keys = [
            k for k in [HUGGINGFACE_API_KEY, HUGGINGFACE_API_KEY_2]
            if k and k not in ('hf_your_token_here', 'hf_YOUR_TOKEN_HERE')
        ]
        self.current_key_index = 0
        self.hf_router_url = "https://router.huggingface.co/v1/chat/completions"
        self.hf_models = [
            "Qwen/Qwen2.5-72B-Instruct",
            "mistralai/Mistral-Small-24B-Instruct-2501",
            "meta-llama/Llama-3.1-8B-Instruct",
        ]
        self.current_model_index = 0
        logger.info(
            f"Initialized Academic RAG (HF keys: {len(self.api_keys)}, Cloudflare Edge URL: {bool(CLOUDFLARE_API_URL)})"
        )

    async def query(self, question: str, language: str = 'fa', context: dict = None) -> Optional[str]:
        """Query the RAG system with academic knowledge base context."""
        knowledge_context = self._retrieve_knowledge(question, language)
        prompt = self._build_rag_prompt(question, knowledge_context, language, context)

        # 1. Try Direct Cloudflare Workers AI REST API if credentials set
        if CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN:
            try:
                res = await self._call_cloudflare_direct(prompt)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Direct Cloudflare Workers AI failed: {e}")

        # 2. Try Deployed Cloudflare Edge RAG Worker
        if CLOUDFLARE_API_URL:
            try:
                res = await self._call_cloudflare_worker(question, language, context)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Cloudflare Edge Worker RAG failed: {e}")

        # 3. Try HuggingFace Inference Router (v1/chat/completions)
        for key_attempt in range(len(self.api_keys)):
            for model_attempt in range(len(self.hf_models)):
                key_index = (self.current_key_index + key_attempt) % len(self.api_keys)
                model_index = (self.current_model_index + model_attempt) % len(self.hf_models)
                api_key = self.api_keys[key_index]
                model = self.hf_models[model_index]
                try:
                    response = await self._call_huggingface_router(model, prompt, api_key)
                    if response:
                        self.current_key_index = key_index
                        self.current_model_index = model_index
                        return response
                except Exception as e:
                    logger.warning(f"HF Router {model} failed: {e}")
                    continue

        # 4. Local Knowledge Synthesis Fallback
        return self._synthesize_local_knowledge(knowledge_context, language)

    def _retrieve_knowledge(self, question: str, language: str) -> Dict:
        """Retrieve relevant knowledge from database using SQLAlchemy 2.0-safe expressions."""
        db = get_session()
        knowledge = {
            'academic': [],
            'news': [],
            'rules': [],
            'characteristics': [],
        }

        try:
            keywords = self._extract_keywords(question, language)
            if not keywords:
                keywords = ['safety', 'dating']

            # Academic papers
            paper_filters = [AcademicKnowledge.title.ilike(f'%{kw}%') for kw in keywords] + [
                AcademicKnowledge.category.ilike(f'%{kw}%') for kw in keywords
            ]
            academic_papers = (
                db.query(AcademicKnowledge)
                .filter(or_(*paper_filters))
                .order_by(AcademicKnowledge.relevance_score.desc())
                .limit(3)
                .all()
            )
            if not academic_papers:
                academic_papers = (
                    db.query(AcademicKnowledge)
                    .order_by(AcademicKnowledge.relevance_score.desc())
                    .limit(2)
                    .all()
                )

            for paper in academic_papers:
                knowledge['academic'].append({
                    'title': paper.title,
                    'year': paper.year,
                    'findings': json.loads(paper.key_findings) if paper.key_findings else [],
                    'abstract': paper.abstract,
                })

            # Dating news
            news_filters = [DatingNews.title.ilike(f'%{kw}%') for kw in keywords] + [
                DatingNews.category.ilike(f'%{kw}%') for kw in keywords
            ]
            news_items = (
                db.query(DatingNews)
                .filter(or_(*news_filters))
                .order_by(DatingNews.relevance_score.desc())
                .limit(2)
                .all()
            )
            for news in news_items:
                knowledge['news'].append({
                    'title': news.title,
                    'summary': news.summary,
                    'date': news.published_date.strftime('%Y-%m-%d') if news.published_date else None,
                })

            # Dating rules
            rule_filters = [DatingRules.title.ilike(f'%{kw}%') for kw in keywords] + [
                DatingRules.category.ilike(f'%{kw}%') for kw in keywords
            ]
            rules = (
                db.query(DatingRules)
                .filter(or_(*rule_filters))
                .order_by(DatingRules.priority.desc())
                .limit(5)
                .all()
            )
            if not rules:
                rules = db.query(DatingRules).order_by(DatingRules.priority.desc()).limit(3).all()

            for rule in rules:
                knowledge['rules'].append({
                    'title': rule.title,
                    'description': rule.description,
                    'priority': rule.priority,
                })

            # Personality characteristics
            char_filters = [PersonalityCharacteristics.name.ilike(f'%{kw}%') for kw in keywords] + [
                PersonalityCharacteristics.characteristic_type.ilike(f'%{kw}%') for kw in keywords
            ]
            characteristics = (
                db.query(PersonalityCharacteristics)
                .filter(or_(*char_filters))
                .limit(3)
                .all()
            )
            for char in characteristics:
                knowledge['characteristics'].append({
                    'name': char.name,
                    'description': char.description,
                    'type': char.characteristic_type,
                    'compatible_with': json.loads(char.compatible_with) if char.compatible_with else [],
                })

        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
        finally:
            db.close()

        return knowledge

    def _extract_keywords(self, question: str, language: str) -> List[str]:
        keywords = []
        keyword_map = {
            'fa': {
                'safety': ['امنیت', 'ایمنی', 'حفاظت', 'خطر', 'مزاحم', 'اخاذی'],
                'psychology': ['روانشناسی', 'شخصیت', 'دلبستگی', 'mbti'],
                'communication': ['ارتباط', 'گفتگو', 'صحبت', 'پیام'],
                'compatibility': ['سازگاری', 'تطابق', 'استارتاپ', 'بین‌المللی'],
                'relationship': ['رابطه', 'دوستی', 'عشق', 'ازدواج'],
                'dating': ['قرار', 'دیت', 'ملاقات', 'کافه'],
                'profile': ['پروفایل', 'بیو', 'معرفی'],
                'consent': ['رضایت', 'مرز', 'نه'],
            },
            'en': {
                'safety': ['safety', 'safe', 'danger', 'protection', 'scam'],
                'psychology': ['psychology', 'personality', 'attachment', 'mbti'],
                'communication': ['communication', 'conversation', 'talk', 'chat'],
                'compatibility': ['compatibility', 'match', 'startup', 'cofounder', 'international'],
                'relationship': ['relationship', 'love', 'dating', 'partner'],
                'dating': ['date', 'meeting', 'first date'],
                'profile': ['profile', 'bio'],
                'consent': ['consent', 'boundaries', 'respect'],
            },
        }
        lang_keywords = keyword_map.get(language, keyword_map['en'])
        q_lower = (question or '').lower()
        for category, category_keywords in lang_keywords.items():
            for kw in category_keywords:
                if kw.lower() in q_lower:
                    keywords.extend([category, kw])
                    break
        words = [w.strip('.,?!؟،') for w in q_lower.split()]
        keywords.extend([w for w in words if len(w) > 3][:6])
        return list(dict.fromkeys(keywords))

    def _build_rag_prompt(self, question: str, knowledge: Dict, language: str, context: dict = None) -> str:
        system_prompts = {
            'fa': 'تو مشاور هوشمند فمینیسم دوستیابی هستی که بر پایه مقالات علمی پاسخ می‌دهی. فقط به زبان فارسی روان، محترمانه و کاربردی پاسخ بده.',
            'en': 'You are the Feminist AI Dating & Safety Coach backed by peer-reviewed research. Reply concisely and practically in English.',
            'tr': 'Akademik araştırmalara dayalı Feminist Yapay Zeka İlişki ve Güvenlik Koçusun. Türkçe, net ve uygulanabilir yanıt ver.',
            'sv': 'Du är en forskningsbaserad dejting- och säkerhetscoach. Svara kort och praktiskt på svenska.',
            'de': 'Du bist ein wissenschaftlich fundierter Dating- und Sicherheitscoach. Antworte präzise auf Deutsch.',
            'ar': 'أنت مستشار ذكي للعلاقات والأمان مستند إلى الأبحاث العلمية. أجب بالعربية بوضوح وإيجاز.',
            'fr': 'Tu es un coach de rencontres et de sécurité basé sur la recherche scientifique. Réponds en français.',
            'es': 'Eres un asistente de citas y seguridad basado en investigación académica. Responde en español.',
            'ku': 'تۆ ڕاوێژکاری زیرەکی پەیوەندی و سەلامەتیت بە پشتبەستن بە توێژینەوەی زانستی. بە کوردی وەڵام بدەرەوە.',
        }
        system_prompt = system_prompts.get(language, system_prompts['en'])
        knowledge_text = ""

        if knowledge['academic']:
            knowledge_text += "\nRelevant Research:\n"
            for paper in knowledge['academic'][:2]:
                knowledge_text += f"- {paper['title']} ({paper['year']})"
                if paper['findings']:
                    knowledge_text += f": {'; '.join(paper['findings'][:2])}"
                knowledge_text += "\n"

        if knowledge['rules']:
            knowledge_text += "\nSafety & Dating Guidelines:\n"
            for rule in knowledge['rules'][:3]:
                knowledge_text += f"- {rule['title']}: {rule['description']}\n"

        user_context = ""
        if context:
            parts = [f"{k}={v}" for k, v in context.items() if v]
            if parts:
                user_context = "\nUser Context: " + ", ".join(parts)

        return f"{system_prompt}{user_context}\n{knowledge_text}\nUser Question: {question}"

    async def _call_cloudflare_worker(self, question: str, language: str, context: dict = None) -> Optional[str]:
        url = f"{CLOUDFLARE_API_URL.rstrip('/')}/api/ai/chat"
        payload = {
            "message": question,
            "language": language,
            "user_profile": context or {},
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={"User-Agent": "FeminismDatingBot/2.0", "Content-Type": "application/json"},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=25),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data.get("reply", "").strip()
                    if reply:
                        return reply
                raise RuntimeError(f"Cloudflare Worker status {resp.status}")

    async def _call_cloudflare_direct(self, prompt: str) -> Optional[str]:
        url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/mistralai/mistral-small-3.1-24b-instruct"
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 380,
            "temperature": 0.65,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    res = data.get("result", {})
                    text = res.get("response") or (res.get("choices") or [{}])[0].get("message", {}).get("content", "")
                    if text and text.strip():
                        return text.strip()
                raise RuntimeError(f"Cloudflare AI HTTP {resp.status}")

    async def _call_huggingface_router(self, model: str, prompt: str, api_key: str) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 350,
            "temperature": 0.7,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.hf_router_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=25),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    choices = data.get("choices") or []
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
                error_text = await resp.text()
                raise RuntimeError(f"HF Router {resp.status}: {error_text[:200]}")

    def _synthesize_local_knowledge(self, knowledge: Dict, language: str) -> str:
        rules = knowledge.get('rules') or []
        papers = knowledge.get('academic') or []
        if language == 'fa':
            lines = ["🛡️ توصیه‌های مبتنی بر پایگاه دانش علمی فمینیسم دوستیابی:"]
            for p in papers[:1]:
                lines.append(f"• پژوهش مرجع: {p['title']} ({p['year']})")
            for r in rules[:3]:
                lines.append(f"• {r['title']}: {r['description']}")
            if len(lines) == 1:
                lines.append("• همیشه قرارهای اول را در مکان عمومی برگزار کنید، دوست مخفی را فعال کنید و به مرزهای رضایت آگاهانه (FRIES) پایبند باشید.")
            return "\n".join(lines)
        lines = ["🛡️ Research-Backed Feminist Dating Guidance:"]
        for p in papers[:1]:
            lines.append(f"• Study: {p['title']} ({p['year']})")
        for r in rules[:3]:
            lines.append(f"• {r['title']}: {r['description']}")
        if len(lines) == 1:
            lines.append("• Meet in public spaces, enable your Secret Friend check-in, and honor enthusiastic FRIES consent.")
        return "\n".join(lines)


hf_rag = HuggingFaceRAG()
