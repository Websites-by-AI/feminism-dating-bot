"""AI Service with HuggingFace RAG as primary backend"""
import aiohttp
import json
import logging
from config import HUGGINGFACE_API_KEY, HUGGINGFACE_API_KEY_2, OPENROUTER_API_KEY, GEMINI_API_KEY
from huggingface_rag import hf_rag

logger = logging.getLogger(__name__)

# Conversation history per user
_user_conversations = {}
MAX_HISTORY = 10


class AIService:
    """AI service with HuggingFace RAG as primary"""
    
    def __init__(self):
        self.available_backends = []
        # Check both HF tokens
        hf_keys = [k for k in [HUGGINGFACE_API_KEY, HUGGINGFACE_API_KEY_2] if k and k != 'hf_your_token_here']
        if hf_keys:
            self.available_backends.append('huggingface_rag')
        if OPENROUTER_API_KEY:
            self.available_backends.append('openrouter')
        if GEMINI_API_KEY:
            self.available_backends.append('gemini')
        
        logger.info(f"Available AI backends: {self.available_backends}")
    
    async def chat(self, user_id: int, message: str, language: str = 'fa', 
                   user_profile: dict = None) -> str:
        """
        Send a message to the AI and get a response.
        Primary: HuggingFace RAG, Fallback: OpenRouter -> Gemini
        """
        # Get or create conversation history
        if user_id not in _user_conversations:
            _user_conversations[user_id] = []
        
        history = _user_conversations[user_id]
        history.append({'role': 'user', 'content': message})
        
        # Trim history if too long
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
            _user_conversations[user_id] = history
        
        # Try HuggingFace RAG first
        if 'huggingface_rag' in self.available_backends:
            try:
                response = await hf_rag.query(
                    question=message,
                    language=language,
                    context=user_profile
                )
                if response and len(response) > 10:
                    history.append({'role': 'assistant', 'content': response})
                    logger.info(f"✅ HuggingFace RAG response for user {user_id}")
                    return response
            except Exception as e:
                logger.warning(f"HuggingFace RAG failed: {e}")
        
        # Fallback to other backends
        system_prompt = self._build_system_prompt(language, user_profile)
        
        for backend in self.available_backends[1:]:  # Skip huggingface_rag
            try:
                response = await self._call_backend(backend, system_prompt, history)
                if response:
                    history.append({'role': 'assistant', 'content': response})
                    return response
            except Exception as e:
                logger.warning(f"AI backend {backend} failed: {e}")
                continue
        
        # If all backends fail, return fallback message
        fallback_messages = {
            'fa': 'متأسفم، الان نمی‌تونم جواب بدم. لطفاً بعداً دوباره تلاش کنید. 🛡️ در meantime از بخش ایمنی استفاده کنید!',
            'en': 'Sorry, I\'m having trouble responding right now. Please try again later. 🛡️ Check out the safety features!',
            'sv': 'Tyvärr, jag kan inte svara just nu. Försök igen senare.',
            'de': 'Entschuldigung, ich kann gerade nicht antworten. Bitte versuchen Sie es später erneut.',
            'tr': 'Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin.',
            'ar': 'عذراً، لا يمكنني الرد حالياً. يرجى المحاولة مرة أخرى لاحقاً.',
            'fr': 'Désolé, je ne peux pas répondre pour le moment. Veuillez réessayer plus tard.',
            'es': 'Lo siento, no puedo responder en este momento. Inténtalo de nuevo más tarde.',
            'ku': 'ببورە، ئێستا ناتوانم وەڵام بدەمەوە. تکایە دواتر هەوڵبدەرەوە.',
        }
        return fallback_messages.get(language, fallback_messages['en'])
    
    def _build_system_prompt(self, language: str, user_profile: dict = None) -> str:
        """Build the system prompt for the AI assistant."""
        prompts = {
            'fa': 'تو یک دستیار هوشمند دوستیابی هستی. به کاربران کمک می‌کنی با نکات گفتگو، ایده‌های قرار ملاقات، بهبود پروفایل و اعتماد به نفس. به فارسی پاسخ بده. پاسخ‌هایت کوتاه، دوستانه و کاربردی باشند.',
            'en': 'You are a smart dating assistant. Help users with conversation tips, date ideas, profile improvement, and confidence building. Reply in English. Keep responses short, friendly, and practical.',
            'sv': 'Du är en smart dejtingassistent. Hjälp användare med samtalstips, dejt-idéer, profilförbättring och självförtroende. Svara på svenska. Håll svaren korta, vänliga och praktiska.',
            'de': 'Du bist ein intelligenter Dating-Assistent. Hilf Benutzern mit Gesprächstipps, Dateen-Ideen, Profilverbesserung und Selbstvertrauen. Antworte auf Deutsch. Halte Antworten kurz, freundlich und praktisch.',
            'tr': 'Akıllı bir flört asistanısın. Kullanıcılara konuşma ipuçları, buluşma fikirleri, profil iyileştirme ve özgüven konularında yardım et. Türkçe cevap ver. Yanıtları kısa, dostane ve pratik tut.',
            'ar': 'أنت مساعد ذكي للتعارف. ساعد المستخدمين بنصائح المحادثة وأفكار المواعيد وتحسين الملف الشخصي وبناء الثقة. أجب بالعربية. اجعل الردود قصيرة وودية وعملية.',
            'fr': 'Tu es un assistant de rencontres intelligent. Aide les utilisateurs avec des conseils de conversation, des idées de rendez-vous, l\'amélioration du profil et la confiance. Réponds en français. Garde les réponses courtes, amicales et pratiques.',
            'es': 'Eres un asistente inteligente de citas. Ayuda a los usuarios con consejos de conversación, ideas de citas, mejora de perfil y confianza. Responde en español. Mantén las respuestas cortas, amigables y prácticas.',
            'ku': 'تۆ یاریدەدەرێکی زیرەکی دۆستابیت. یارمەتی بەکارهێنەران بدە لەگەڵ ئامۆژگاری گفتوگۆ، بیرۆکەی بەیاننامە، باشکردنی پرۆفایل و متمانە بە خۆ. بە کوردی وەڵام بدەوە. وەڵامەکانت کورت و دۆستانە و بەکارهاتوو بن.',
        }
        
        prompt = prompts.get(language, prompts['en'])
        
        if user_profile:
            profile_info = f"\n\nUser profile context: name={user_profile.get('name', 'Unknown')}, age={user_profile.get('age', 'Unknown')}, city={user_profile.get('city', 'Unknown')}"
            prompt += profile_info
        
        return prompt
    
    async def _call_backend(self, backend: str, system_prompt: str, history: list) -> str:
        """Call a specific AI backend."""
        if backend == 'huggingface':
            return await self._call_huggingface(system_prompt, history)
        elif backend == 'openrouter':
            return await self._call_openrouter(system_prompt, history)
        elif backend == 'gemini':
            return await self._call_gemini(system_prompt, history)
        return None
    
    async def _call_huggingface(self, system_prompt: str, history: list) -> str:
        """Call HuggingFace Inference API (using a conversational model)."""
        if not HUGGINGFACE_API_KEY:
            return None
        
        # Build the prompt from conversation history
        full_prompt = system_prompt + "\n\n"
        for msg in history:
            if msg['role'] == 'user':
                full_prompt += f"User: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                full_prompt += f"Assistant: {msg['content']}\n"
        full_prompt += "Assistant:"
        
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get('generated_text', '').replace(full_prompt, '').strip()
                elif resp.status == 503:
                    # Model is loading
                    raise Exception("Model loading")
                else:
                    raise Exception(f"HuggingFace error: {resp.status}")
        return None
    
    async def _call_openrouter(self, system_prompt: str, history: list) -> str:
        """Call OpenRouter API (access to many models)."""
        if not OPENROUTER_API_KEY:
            return None
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg['role'], "content": msg['content']})
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/dating_bot",
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",  # Can be changed
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.7,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    raise Exception(f"OpenRouter error: {resp.status}")
        return None
    
    async def _call_gemini(self, system_prompt: str, history: list) -> str:
        """Call Google Gemini API."""
        if not GEMINI_API_KEY:
            return None
        
        # Build contents for Gemini
        contents = []
        for msg in history:
            role = "user" if msg['role'] == 'user' else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg['content']}]
            })
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300,
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    raise Exception(f"Gemini error: {resp.status}")
        return None
    
    def clear_history(self, user_id: int):
        """Clear conversation history for a user."""
        if user_id in _user_conversations:
            del _user_conversations[user_id]


# Singleton instance
ai_service = AIService()
