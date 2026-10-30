"""AI Service with Academic RAG (Cloudflare Workers AI + HuggingFace Router) as primary backend"""
import aiohttp
import logging
from config import OPENROUTER_API_KEY, GEMINI_API_KEY
from huggingface_rag import hf_rag

logger = logging.getLogger(__name__)

_user_conversations = {}
MAX_HISTORY = 10


class AIService:
    """Multilingual AI service with Academic RAG primary backend + OpenRouter & Gemini fallbacks."""

    def __init__(self):
        self.available_backends = ['academic_rag']
        if OPENROUTER_API_KEY:
            self.available_backends.append('openrouter')
        if GEMINI_API_KEY:
            self.available_backends.append('gemini')
        logger.info(f"Available AI backends: {self.available_backends}")

    async def chat(self, user_id: int, message: str, language: str = 'fa', user_profile: dict = None) -> str:
        if user_id not in _user_conversations:
            _user_conversations[user_id] = []

        history = _user_conversations[user_id]
        history.append({'role': 'user', 'content': message})
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
            _user_conversations[user_id] = history

        # 1. Primary: Academic RAG (Cloudflare Edge AI -> HF Router -> Local Knowledge Synthesis)
        try:
            response = await hf_rag.query(
                question=message,
                language=language,
                context=user_profile,
            )
            if response and len(response) > 5:
                history.append({'role': 'assistant', 'content': response})
                return response
        except Exception as e:
            logger.warning(f"Primary Academic RAG failed: {e}")

        # 2. Secondary Fallbacks: OpenRouter -> Gemini
        system_prompt = self._build_system_prompt(language, user_profile)
        for backend in self.available_backends[1:]:
            try:
                response = await self._call_backend(backend, system_prompt, history)
                if response:
                    history.append({'role': 'assistant', 'content': response})
                    return response
            except Exception as e:
                logger.warning(f"AI backend {backend} failed: {e}")

        return hf_rag._synthesize_local_knowledge({'academic': [], 'rules': []}, language)

    def _build_system_prompt(self, language: str, user_profile: dict = None) -> str:
        prompts = {
            'fa': 'تو دستیار هوشمند دوستیابی و ایمنی فمینیستی هستی. به فارسی روان، کوتاه و کاربردی پاسخ بده.',
            'en': 'You are a smart feminist dating and safety assistant. Keep responses concise, warm, and practical.',
            'tr': 'Akıllı bir feminist ilişki ve güvenlik asistanısın. Türkçe, kısa ve pratik yanıt ver.',
            'sv': 'Du är en smart dejtingassistent. Svara kort och praktiskt på svenska.',
            'de': 'Du bist ein intelligenter Dating-Assistent. Antworte kurz und praktisch auf Deutsch.',
            'ar': 'أنت مساعد ذكي للتعارف والأمان. أجب بالعربية بإيجاز.',
            'fr': 'Tu es un assistant de rencontres intelligent. Réponds brièvement en français.',
            'es': 'Eres un asistente inteligente de citas. Responde brevemente en español.',
            'ku': 'تۆ یاریدەدەرێکی زیرەکی دۆستابیت. بە کوردی وەڵام بدەرەوە.',
        }
        prompt = prompts.get(language, prompts['en'])
        if user_profile:
            prompt += f"\nUser profile: name={user_profile.get('name', 'User')}, age={user_profile.get('age', '?')}, city={user_profile.get('city', '?')}"
        return prompt

    async def _call_backend(self, backend: str, system_prompt: str, history: list):
        if backend == 'openrouter':
            return await self._call_openrouter(system_prompt, history)
        elif backend == 'gemini':
            return await self._call_gemini(system_prompt, history)
        return None

    async def _call_openrouter(self, system_prompt: str, history: list):
        if not OPENROUTER_API_KEY:
            return None
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m['role'], "content": m['content']} for m in history
        ]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": "openai/gpt-4o-mini", "messages": messages, "max_tokens": 350},
                timeout=aiohttp.ClientTimeout(total=25),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content'].strip()
                raise RuntimeError(f"OpenRouter error {resp.status}")

    async def _call_gemini(self, system_prompt: str, history: list):
        if not GEMINI_API_KEY:
            return None
        contents = [
            {"role": "user" if m['role'] == 'user' else "model", "parts": [{"text": m['content']}]}
            for m in history
        ]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={"system_instruction": {"parts": [{"text": system_prompt}]}, "contents": contents},
                timeout=aiohttp.ClientTimeout(total=25),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                raise RuntimeError(f"Gemini error {resp.status}")

    def clear_history(self, user_id: int):
        _user_conversations.pop(user_id, None)


ai_service = AIService()
