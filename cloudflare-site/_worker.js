/**
 * Feminism AI Dating Bot & Platform — Cloudflare Edge Worker
 * ==========================================================
 * Bindings:
 *   - env.KV : Persistent Cloudflare KV storage (FEMINISM_DATING_KV)
 *   - env.AI : Cloudflare Workers AI (@cf/meta/llama-3.1-8b-instruct)
 *
 * Capabilities:
 *   1. Full REST API for Web Platform (Cloudflare Pages & HuggingFace Space)
 *   2. Academic RAG Knowledge Base + Multilingual AI Coach (9 languages)
 *   3. 13 Feminist Safety Features (SOS, Secret Friend, Safe Word, Check-in, Privacy, Consent, Body-Scam Shield)
 *   4. 10 Relationship Modes (incl. Startup Co-founder & International) + MBTI/Attachment/Love-Language Tests
 *   5. Serverless Telegram Bot Webhook (/webhook/telegram) + 1-Click Admin BotFather Connector
 */

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Admin-Key",
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...CORS_HEADERS,
    },
  });
}

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

// ============================================================
// ACADEMIC KNOWLEDGE BASE FOR RAG
// ============================================================
const KNOWLEDGE_BASE = [
  {
    id: "gillett-2023",
    title: "Gillett (2023) - Women's Safety Work on Dating Apps (Feminist Media Studies)",
    tags: ["safety", "first date", "public", "checkin", "friend", "ایمنی", "قرار", "güvenlik", "randevu"],
    summary:
      "Women perform extensive invisible 'safety labor' before and during dates: verifying identity, sharing live plans with a trusted Secret Friend, meeting in public venues, arranging independent transport, and planning safe exit strategies.",
  },
  {
    id: "amirkhani-2024",
    title: "Amirkhani et al. (2024 & 2025) - Online Romance Scams & 'Body Scam' Sextortion in Iran (ACM CSCW)",
    tags: ["scam", "sextortion", "photo", "nude", "blackmail", "iran", "abroad", "international", "کلاهبرداری", "اخاذی", "عکس", "بین‌المللی", "dolandırıcılık", "şantaj"],
    summary:
      "Identifies 'body scam' and sextortion patterns where perpetrators rush emotional intimacy, isolate targets, request private photos, or dangle marriage/visa promises to coerce victims. Key defense: never share intimate media under pressure, verify identity via live pose selfie, keep conversations on protected channels, and document/block coercion immediately.",
  },
  {
    id: "thompson-2018",
    title: "Thompson (2018) & Doria (2023) - Discourse of Enthusiastic Consent (FRIES Framework)",
    tags: ["consent", "boundaries", "respect", "pressure", "no", "رضایت", "مرز", "نه", "onay", "sınır"],
    summary:
      "Healthy feminist dating centers FRIES consent: Freely given, Reversible at any moment, Informed, Enthusiastic, and Specific. Silence or hesitation is never consent; boundary pushing early in chat is a major red flag.",
  },
  {
    id: "bicharanlou-2017",
    title: "Bicharanlou & Siasirad (2017) - Online Privacy Literacy for Women",
    tags: ["privacy", "anonymous", "location", "screenshot", "حریم خصوصی", "ناشناس", "مکان", "gizlilik", "anonim"],
    summary:
      "Layered digital privacy—anonymous nicknames until trust is earned, city-level rather than exact location sharing, photo blur before mutual verification, and separation of personal workplace details—dramatically reduces stalking and doxxing risks.",
  },
  {
    id: "attachment-finkel",
    title: "Finkel et al. (2012) & Oldham & Davila (2014) - Attachment Styles & Compatibility Science",
    tags: ["attachment", "mbti", "personality", "ghosting", "anxious", "avoidant", "secure", "شخصیت", "دلبستگی", "گوستینگ", "kişilik", "bağlanma"],
    summary:
      "Secure attachment fosters clear, warm communication; anxious-avoidant loops trigger over-texting followed by withdrawal/ghosting. Moving from endless texting to a brief, safe public coffee/video check within 1-2 weeks improves authentic assessment.",
  },
  {
    id: "startup-cofounder",
    title: "Feminist Startup Co-founder & Partner Compatibility Guide",
    tags: ["startup", "cofounder", "business", "equity", "vesting", "استارتاپ", "هم‌بنیان‌گذار", "سهام", "girişim", "ortak"],
    summary:
      "When combining romance or partnership with startup co-founding: formalize written equity splits with 4-year vesting and 1-year cliff, define clear role ownership, never accept unpaid labor without written equity ('sweat equity trap'), and agree on conflict resolution & exit terms upfront.",
  },
  {
    id: "international-dating",
    title: "Cross-Cultural & International Dating Safety Protocol",
    tags: ["international", "abroad", "visa", "long distance", "culture", "بین‌المللی", "مهاجرت", "ویزا", "راه دور", "uluslararası", "uzak mesafe"],
    summary:
      "In cross-border relationships: verify identity via regular live video calls, never send money or pay 'visa/ticket fees', maintain independent legal/financial agency when relocating, discuss cultural & gender-equality expectations explicitly, and ensure a local safety network when meeting abroad.",
  },
];

function retrieveKnowledge(queryText) {
  const q = (queryText || "").toLowerCase();
  const scored = KNOWLEDGE_BASE.map((item) => {
    let score = 0;
    for (const tag of item.tags) {
      if (q.includes(tag.toLowerCase())) score += 3;
    }
    const words = q.split(/\s+/).filter((w) => w.length > 3);
    for (const w of words) {
      if (item.summary.toLowerCase().includes(w) || item.title.toLowerCase().includes(w)) score += 1;
    }
    return { item, score };
  });
  scored.sort((a, b) => b.score - a.score);
  const top = scored.filter((s) => s.score > 0).slice(0, 3).map((s) => s.item);
  return top.length > 0 ? top : [KNOWLEDGE_BASE[0], KNOWLEDGE_BASE[2], KNOWLEDGE_BASE[4]];
}

const RELATIONSHIP_MODES = {
  serious: { emoji: "💍", en: "Serious Relationship", fa: "رابطه جدی", tr: "Ciddi İlişki" },
  casual: { emoji: "🌸", en: "Casual Dating", fa: "رابطه دوستانه", tr: "Rahat Tanışma" },
  marriage: { emoji: "💒", en: "Marriage", fa: "ازدواج", tr: "Evlilik" },
  friendship: { emoji: "👥", en: "Pure Friendship", fa: "دوستی", tr: "Arkadaşlık" },
  open: { emoji: "🌈", en: "Ethical Non-Monogamy", fa: "رابطه باز اخلاقی", tr: "Açık İlişki" },
  emotional: { emoji: "💝", en: "Emotional Connection", fa: "اتصال عاطفی عمیق", tr: "Duygusal Bağ" },
  intellectual: { emoji: "🧠", en: "Intellectual Connection", fa: "اتصال فکری و فرهنگی", tr: "Entelektüel Bağ" },
  one_night: { emoji: "🔥", en: "Short-Term / Spark", fa: "قرار کوتاه‌مدت", tr: "Kısa Süreli" },
  startup: { emoji: "🚀", en: "Startup Co-founder Partner", fa: "شریک استارتاپی", tr: "Girişim Kurucu Ortağı" },
  abroad: { emoji: "🌍", en: "International / Cross-Border", fa: "آشنایی بین‌المللی", tr: "Uluslararası Tanışma" },
};

// ============================================================
// DEFAULT SEED DATA IN KV
// ============================================================
async function ensureSeedData(env) {
  const existing = await env.KV.get("db:users", "json");
  if (existing && Array.isArray(existing) && existing.length > 0) {
    return existing;
  }

  const now = new Date().toISOString();
  const demoPass = await sha256("demo123");
  const adminPass = await sha256("admin123");

  const seedUsers = [
    {
      id: 1,
      telegram_id: 100001,
      username: "sara123",
      email: "sara@feminism-dating.org",
      password_hash: demoPass,
      firstName: "سارا",
      lastName: "احمدی",
      name: "سارا احمدی",
      age: 26,
      gender: "female",
      looking_for: "anyone",
      city: "تهران",
      country: "Iran",
      language: "fa",
      bio: "پژوهشگر علوم اجتماعی و علاقه‌مند به کتاب، کافه‌گردی و گفتگوهای عمیق فکری. ارزش اول من احترام متقابل و برابری است.",
      opening_move: "چه کتابی یا ایده‌ای نگاه تو به زندگی رو تغییر داده؟ 📚",
      relationship_mode: "serious",
      mbti_type: "INFJ",
      love_language: "time",
      attachment_style: "secure",
      safety_score: 100,
      photo_count: 3,
      is_active: true,
      is_premium: true,
      is_verified: true,
      profile_complete: true,
      role: "user",
      created_at: now,
      last_active: now,
    },
    {
      id: 2,
      telegram_id: 100002,
      username: "maryam123",
      email: "maryam@feminism-dating.org",
      password_hash: demoPass,
      firstName: "مریم",
      lastName: "کریمی",
      name: "مریم کریمی",
      age: 29,
      gender: "female",
      looking_for: "anyone",
      city: "اصفهان",
      country: "Iran",
      language: "fa",
      bio: "مهندس نرم‌افزار و بنیان‌گذار استارتاپ سلامت زنان 🚀 به دنبال هم‌بنیان‌گذار و شریک فکری با ارزش‌های مشترک.",
      opening_move: "اگر فردا یک استارتاپ برای بهتر کردن دنیا بسازیم، موضوعش چیه؟ 🚀",
      relationship_mode: "startup",
      mbti_type: "ENTJ",
      love_language: "words",
      attachment_style: "secure",
      safety_score: 98,
      photo_count: 2,
      is_active: true,
      is_premium: true,
      is_verified: true,
      profile_complete: true,
      role: "user",
      created_at: now,
      last_active: now,
    },
    {
      id: 3,
      telegram_id: 100003,
      username: "elif_ist",
      email: "elif@feminism-dating.org",
      password_hash: demoPass,
      firstName: "Elif",
      lastName: "Yılmaz",
      name: "Elif Yılmaz",
      age: 27,
      gender: "female",
      looking_for: "anyone",
      city: "Istanbul",
      country: "Turkey",
      language: "tr",
      bio: "UX Designer in Istanbul 🎨 Passionate about women-first tech, art exhibitions, and international cultural exchange.",
      opening_move: "What's your ideal safe & creative first date spot in the city? ☕",
      relationship_mode: "abroad",
      mbti_type: "ENFP",
      love_language: "time",
      attachment_style: "secure",
      safety_score: 100,
      photo_count: 4,
      is_active: true,
      is_premium: false,
      is_verified: true,
      profile_complete: true,
      role: "user",
      created_at: now,
      last_active: now,
    },
    {
      id: 4,
      telegram_id: 100004,
      username: "mina_berlin",
      email: "mina@feminism-dating.org",
      password_hash: demoPass,
      firstName: "Mina",
      lastName: "auer",
      name: "Mina Rad",
      age: 31,
      gender: "female",
      looking_for: "anyone",
      city: "Berlin",
      country: "Germany",
      language: "en",
      bio: "AI Ethics Researcher in Berlin 🧠 Looking for intellectual & emotional depth, honest boundaries, and weekend hikes.",
      opening_move: "Tell me one green flag you always appreciate in people 💚",
      relationship_mode: "intellectual",
      mbti_type: "INTJ",
      love_language: "acts",
      attachment_style: "secure",
      safety_score: 100,
      photo_count: 2,
      is_active: true,
      is_premium: true,
      is_verified: true,
      profile_complete: true,
      role: "user",
      created_at: now,
      last_active: now,
    },
    {
      id: 5,
      telegram_id: 100005,
      username: "rojda_ku",
      email: "rojda@feminism-dating.org",
      password_hash: demoPass,
      firstName: "روژدا",
      lastName: "کورد",
      name: "روژدا امینی",
      age: 25,
      gender: "female",
      looking_for: "anyone",
      city: "سنندج",
      country: "Iran",
      language: "ku",
      bio: "معمار و عکاس مستند 📸 عاشق موسیقی، طبیعت و دوستی‌های اصیل و امن.",
      opening_move: "کدام موسیقی حال دلت رو همیشه خوب می‌کنه؟ 🎵",
      relationship_mode: "emotional",
      mbti_type: "INFP",
      love_language: "words",
      attachment_style: "secure",
      safety_score: 99,
      photo_count: 3,
      is_active: true,
      is_premium: false,
      is_verified: true,
      profile_complete: true,
      role: "user",
      created_at: now,
      last_active: now,
    },
    {
      id: 6,
      telegram_id: 100006,
      username: "astrid_sv",
      email: "astrid@feminism-dating.org",
      password_hash: demoPass,
      firstName: "Astrid",
      lastName: "Lind",
      name: "Astrid Lind",
      age: 30,
      gender: "female",
      looking_for: "anyone",
      city: "Stockholm",
      country: "Sweden",
      language: "sv",
      bio: "Clean-tech founder in Stockholm 🌿 Co-building sustainable ventures and meaningful egalitarian partnerships.",
      opening_move: "Fika first or a walk by the water? ☕🌊",
      relationship_mode: "startup",
      mbti_type: "ENFJ",
      love_language: "time",
      attachment_style: "secure",
      safety_score: 100,
      photo_count: 2,
      is_active: true,
      is_premium: true,
      is_verified: true,
      profile_complete: true,
      role: "user",
      created_at: now,
      last_active: now,
    },
    {
      id: 99,
      telegram_id: 100099,
      username: "admin",
      email: "admin@feminism-dating.com",
      password_hash: adminPass,
      firstName: "مدیر",
      lastName: "سیستم",
      name: "مدیر سیستم (Admin)",
      age: 34,
      gender: "female",
      looking_for: "anyone",
      city: "تهران / Istanbul",
      country: "Global",
      language: "fa",
      bio: "تیم مدیریت ایمنی و هوش مصنوعی فمینیسم دوستیابی 🛡️",
      opening_move: "چطور می‌توانیم تجربه امن‌تری برای شما بسازیم؟",
      relationship_mode: "serious",
      mbti_type: "ENTJ",
      love_language: "acts",
      attachment_style: "secure",
      safety_score: 100,
      photo_count: 1,
      is_active: true,
      is_premium: true,
      is_verified: true,
      profile_complete: true,
      role: "admin",
      created_at: now,
      last_active: now,
    },
  ];

  const seedTests = [
    {
      id: 1,
      user_id: 1,
      test_type: "personality",
      mode: "serious",
      score: 92,
      mbti_type: "INFJ",
      love_language: "time",
      attachment_style: "secure",
      ai_analysis: "تیپ INFJ با دلبستگی ایمن: ارتباط عمیق، همدلی بالا و مرزبندی سالم در روابط جدی.",
      date: now,
    },
    {
      id: 2,
      user_id: 2,
      test_type: "compatibility",
      mode: "startup",
      score: 95,
      mbti_type: "ENTJ",
      love_language: "words",
      attachment_style: "secure",
      ai_analysis: "آمادگی عالی برای هم‌بنیان‌گذاری استارتاپی: شفافیت در تقسیم سهام، مدیریت ریسک و احترام متقابل.",
      date: now,
    },
    {
      id: 3,
      user_id: 3,
      test_type: "compatibility",
      mode: "abroad",
      score: 89,
      mbti_type: "ENFP",
      love_language: "time",
      attachment_style: "secure",
      ai_analysis: "High cross-cultural adaptability with strong awareness of international dating safety protocols.",
      date: now,
    },
  ];

  await env.KV.put("db:users", JSON.stringify(seedUsers));
  await env.KV.put("db:tests", JSON.stringify(seedTests));
  await env.KV.put("db:sos_alerts", JSON.stringify([]));
  await env.KV.put("db:matches_count", "128");
  return seedUsers;
}

function sanitizeUser(u) {
  if (!u) return null;
  const copy = { ...u };
  delete copy.password_hash;
  return copy;
}

function findUser(users, identifier) {
  const idStr = String(identifier);
  const idNum = Number(identifier);
  return users.find(
    (u) =>
      u.id === idNum ||
      u.telegram_id === idNum ||
      (u.username && u.username.toLowerCase() === idStr.toLowerCase())
  );
}

// ============================================================
// WORKERS AI + RAG GENERATION
// ============================================================
async function runRagAI(env, { message, language = "fa", userProfile = null, mode = null }) {
  const docs = retrieveKnowledge(message + " " + (mode || ""));
  const contextText = docs.map((d) => `- ${d.title}: ${d.summary}`).join("\n");

  const langNames = {
    fa: "Persian (فارسی)",
    en: "English",
    tr: "Turkish (Türkçe)",
    sv: "Swedish (Svenska)",
    de: "German (Deutsch)",
    ar: "Arabic (العربية)",
    fr: "French (Français)",
    es: "Spanish (Español)",
    ku: "Kurdish (کوردی)",
  };
  const replyLang = langNames[language] || "Persian (فارسی)";

  const profileLine = userProfile
    ? `User Context: Name=${userProfile.name || "User"}, Age=${userProfile.age || "?"}, City=${userProfile.city || "?"}, Mode=${mode || userProfile.relationship_mode || "general"}, MBTI=${userProfile.mbti_type || "unknown"}.`
    : "";

  const systemPrompt = `You are the Feminist AI Dating & Safety Coach — an empathetic, empowering, research-backed advisor inspired by Bumble, HER, and peer-reviewed feminist safety studies.
Always prioritize women's agency, enthusiastic consent (FRIES), emotional wellbeing, digital privacy, and practical safety.
Reply strictly in ${replyLang}. Keep your answer warm, structured with short bullet points where helpful, and concise (under 180 words).
${profileLine}

Relevant Research & Guidelines:
${contextText}`;

  if (env.AI) {
    const models = [
      "@cf/mistralai/mistral-small-3.1-24b-instruct",
      "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
      "@cf/meta/llama-3.1-8b-instruct-fast",
    ];
    for (const model of models) {
      try {
        const res = await env.AI.run(model, {
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: message },
          ],
          max_tokens: 420,
          temperature: 0.65,
        });
        const text =
          res?.response ||
          res?.choices?.[0]?.message?.content ||
          "";
        if (text && text.trim().length > 5) {
          return {
            reply: text.trim(),
            sources: docs.map((d) => d.title),
            model,
          };
        }
      } catch (err) {
        // try next model
      }
    }
  }

  // Deterministic research-backed fallback if AI binding encounters a transient limit
  const topDoc = docs[0];
  const fallbackByLang = {
    fa: `🛡️ بر اساس پژوهش‌های علمی (${topDoc.title}):\n• همیشه قرارهای اول را در مکان‌های عمومی امن برگزار کنید و گزینه «دوست مخفی» را فعال نگه دارید.\n• مرزهای شخصی و رضایت آگاهانه (FRIES) خط قرمز رابطه سالم است.\n• هرگز تحت فشار اطلاعات حساس یا تصاویر خصوصی ارسال نکنید.`,
    tr: `🛡️ Akademik araştırmalara göre (${topDoc.title}):\n• İlk buluşmaları her zaman güvenli, halka açık yerlerde planlayın ve Gizli Arkadaş özelliğini açın.\n• Açık ve gönüllü onay (FRIES) sağlıklı ilişkinin temelidir.\n• Baskı altında özel fotoğraf veya finansal bilgi paylaşmayın.`,
    en: `🛡️ Based on academic research (${topDoc.title}):\n• Plan first meetings in public venues and keep your Secret Friend check-in active.\n• Center enthusiastic, reversible consent (FRIES) and clear personal boundaries.\n• Never share intimate media or financial details under pressure.`,
  };
  return {
    reply: fallbackByLang[language] || fallbackByLang.en,
    sources: docs.map((d) => d.title),
    model: "rag-knowledge-engine",
  };
}

// ============================================================
// SERVERLESS TELEGRAM BOT WEBHOOK HANDLER
// ============================================================
async function tgSend(token, method, payload) {
  const resp = await fetch(`https://api.telegram.org/bot${token}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return resp.json();
}

function tgMainMenu(lang = "fa") {
  const labels = {
    fa: {
      modes: "🎯 ۱۰ حالت رابطه (استارتاپی و بین‌المللی)",
      mbti: "🧠 تست شخصیت MBTI و دلبستگی",
      safety: "🛡️ ۱۳ ویژگی ایمنی فمینیستی",
      ai: "🤖 مشاور هوش مصنوعی (RAG)",
      browse: "💕 مرور پروفایل‌های تاییدشده",
      lang: "🌐 تغییر زبان (9 Languages)",
    },
    tr: {
      modes: "🎯 10 İlişki Modu (Girişim & Uluslararası)",
      mbti: "🧠 MBTI & Bağlanma Testi",
      safety: "🛡️ 13 Feminist Güvenlik Aracı",
      ai: "🤖 Yapay Zeka İlişki Koçu (RAG)",
      browse: "💕 Doğrulanmış Profilleri Keşfet",
      lang: "🌐 Dil Değiştir (9 Languages)",
    },
    en: {
      modes: "🎯 10 Relationship Modes (Startup & Abroad)",
      mbti: "🧠 MBTI & Attachment Quiz",
      safety: "🛡️ 13 Feminist Safety Features",
      ai: "🤖 AI Dating & Safety Coach (RAG)",
      browse: "💕 Browse Verified Profiles",
      lang: "🌐 Change Language (9 Languages)",
    },
  };
  const l = labels[lang] || labels.en;
  return {
    inline_keyboard: [
      [{ text: l.modes, callback_data: "menu_modes" }],
      [{ text: l.mbti, callback_data: "menu_mbti" }],
      [{ text: l.safety, callback_data: "menu_safety" }],
      [{ text: l.ai, callback_data: "menu_ai" }],
      [{ text: l.browse, callback_data: "menu_browse" }],
      [{ text: l.lang, callback_data: "menu_lang" }],
    ],
  };
}

async function handleTelegramUpdate(env, update) {
  const botConf = (await env.KV.get("db:telegram_bot", "json")) || {};
  const token = env.BOT_TOKEN || botConf.token;
  if (!token) return { ok: false, reason: "BOT_TOKEN not configured" };

  const users = await ensureSeedData(env);

  if (update.message) {
    const msg = update.message;
    const chatId = msg.chat.id;
    const from = msg.from || {};
    const text = (msg.text || "").trim();

    let user = users.find((u) => u.telegram_id === from.id);
    if (!user) {
      user = {
        id: users.length + 100,
        telegram_id: from.id,
        username: from.username || `tg_${from.id}`,
        email: `tg_${from.id}@telegram.user`,
        firstName: from.first_name || "کاربر",
        lastName: from.last_name || "",
        name: [from.first_name, from.last_name].filter(Boolean).join(" ") || "Telegram User",
        age: 25,
        gender: "female",
        looking_for: "anyone",
        city: "Online",
        language: "fa",
        relationship_mode: "serious",
        safety_score: 100,
        photo_count: 0,
        is_active: true,
        is_verified: false,
        profile_complete: true,
        role: "user",
        created_at: new Date().toISOString(),
        last_active: new Date().toISOString(),
      };
      users.push(user);
      await env.KV.put("db:users", JSON.stringify(users));
    }

    const lang = user.language || "fa";

    if (text.startsWith("/start")) {
      const arg = text.split(/\s+/)[1] || "";
      if (arg === "startup" || arg === "abroad") {
        user.relationship_mode = arg;
        await env.KV.put("db:users", JSON.stringify(users));
        const modeInfo = RELATIONSHIP_MODES[arg];
        await tgSend(token, "sendMessage", {
          chat_id: chatId,
          text: `${modeInfo.emoji} حالت شما روی «${modeInfo[lang] || modeInfo.en}» تنظیم شد!\n\nمی‌توانید همین الان سؤالات خود درباره این حالت را بپرسید یا از منوی زیر استفاده کنید:`,
          reply_markup: tgMainMenu(lang),
        });
        return { ok: true };
      }

      const welcome = {
        fa: "🌹 به ربات دوستیابی هوشمند فمینیستی خوش آمدید!\n\n🛡️ مجهز به ۱۳ ویژگی ایمنی علمی، ۱۰ حالت رابطه (از جمله شریک استارتاپی 🚀 و بین‌المللی 🌍) و هوش مصنوعی RAG.\n\nهر سؤالی دارید مستقیم تایپ کنید یا یکی از بخش‌ها را انتخاب کنید:",
        tr: "🌹 Feminist Yapay Zeka Tanışma Botuna Hoş Geldiniz!\n\n🛡️ 13 bilimsel güvenlik özelliği, 10 ilişki modu (Girişim Ortağı 🚀 & Uluslararası 🌍 dahil) ve RAG Yapay Zeka Koçu aktif.",
        en: "🌹 Welcome to the Feminist AI Dating & Safety Bot!\n\n🛡️ Featuring 13 research-backed safety tools, 10 relationship modes (including Startup Co-founder 🚀 & International 🌍), and live RAG AI coaching.",
      };
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: welcome[lang] || welcome.en,
        reply_markup: tgMainMenu(lang),
      });
      return { ok: true };
    }

    if (text === "/menu" || text === "/help" || text === "/safety") {
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "🏠 منوی اصلی / Main Menu:",
        reply_markup: tgMainMenu(lang),
      });
      return { ok: true };
    }

    // Check Safe Word trigger
    const safetyKey = `safety:${user.id}`;
    const safety = (await env.KV.get(safetyKey, "json")) || {};
    if (safety.safe_word_active && safety.safe_word && text.toLowerCase().includes(safety.safe_word.toLowerCase())) {
      const alerts = (await env.KV.get("db:sos_alerts", "json")) || [];
      alerts.unshift({
        id: alerts.length + 1,
        user_id: user.id,
        message: "Safe word triggered via Telegram",
        resolved: false,
        triggered_at: new Date().toISOString(),
      });
      await env.KV.put("db:sos_alerts", JSON.stringify(alerts));
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "🆘 کلمه امن شما شناسایی شد و هشدار اضطراری (SOS) ثبت گردید. در مکان عمومی بمانید و با مخاطب مورد اعتماد تماس بگیرید.",
        reply_markup: tgMainMenu(lang),
      });
      return { ok: true };
    }

    // Free-form AI RAG response
    const aiRes = await runRagAI(env, {
      message: text,
      language: lang,
      userProfile: user,
      mode: user.relationship_mode,
    });
    await tgSend(token, "sendMessage", {
      chat_id: chatId,
      text: `🤖 ${aiRes.reply}`,
      reply_markup: tgMainMenu(lang),
    });
    return { ok: true };
  }

  if (update.callback_query) {
    const cq = update.callback_query;
    const chatId = cq.message.chat.id;
    const data = cq.data || "";
    const from = cq.from || {};
    let user = users.find((u) => u.telegram_id === from.id) || users[0];
    const lang = user?.language || "fa";

    await tgSend(token, "answerCallbackQuery", { callback_query_id: cq.id });

    if (data === "menu_lang") {
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "🌐 Select your language / زبان خود را انتخاب کنید:",
        reply_markup: {
          inline_keyboard: [
            [
              { text: "🇮🇷 فارسی", callback_data: "setlang_fa" },
              { text: "🇬🇧 English", callback_data: "setlang_en" },
              { text: "🇹🇷 Türkçe", callback_data: "setlang_tr" },
            ],
            [
              { text: "🇸🇪 Svenska", callback_data: "setlang_sv" },
              { text: "🇩🇪 Deutsch", callback_data: "setlang_de" },
              { text: "🇸🇦 العربية", callback_data: "setlang_ar" },
            ],
            [
              { text: "🇫🇷 Français", callback_data: "setlang_fr" },
              { text: "🇪🇸 Español", callback_data: "setlang_es" },
              { text: "☀️ کوردی", callback_data: "setlang_ku" },
            ],
          ],
        },
      });
    } else if (data.startsWith("setlang_")) {
      const newLang = data.replace("setlang_", "");
      if (user) {
        user.language = newLang;
        await env.KV.put("db:users", JSON.stringify(users));
      }
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: `✅ Language updated to: ${newLang.toUpperCase()}`,
        reply_markup: tgMainMenu(newLang),
      });
    } else if (data === "menu_modes") {
      const rows = Object.entries(RELATIONSHIP_MODES).map(([k, v]) => [
        { text: `${v.emoji} ${v[lang] || v.en}`, callback_data: `setmode_${k}` },
      ]);
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "🎯 حالت رابطه مورد نظر خود را انتخاب کنید:",
        reply_markup: { inline_keyboard: rows },
      });
    } else if (data.startsWith("setmode_")) {
      const m = data.replace("setmode_", "");
      if (user && RELATIONSHIP_MODES[m]) {
        user.relationship_mode = m;
        await env.KV.put("db:users", JSON.stringify(users));
        const info = RELATIONSHIP_MODES[m];
        const tip = await runRagAI(env, {
          message: `Give 3 concise safety & success tips for ${info.en} dating mode.`,
          language: lang,
          userProfile: user,
          mode: m,
        });
        await tgSend(token, "sendMessage", {
          chat_id: chatId,
          text: `✅ ${info.emoji} ${info[lang] || info.en}\n\n${tip.reply}`,
          reply_markup: tgMainMenu(lang),
        });
      }
    } else if (data === "menu_safety") {
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text:
          "🛡️ ۱۳ ویژگی ایمنی فمینیستی فعال:\n" +
          "1. 🤝 دوست مخفی (Secret Friend)\n2. 👥 یار ایمنی متقابل\n3. ⏰ چک‌این خودکار قرار\n4. 🆘 دکمه اضطراری SOS\n" +
          "5. 🔐 کلمه امن مخفی\n6. 📸 تأیید عکس زنده\n7. 🛡️ حریم خصوصی و حالت ناشناس\n8. 💬 آموزش رضایت (FRIES)\n" +
          "9. 🚫 مسدودسازی و گزارش فوری\n10. ⚠️ سپر ضد اخاذی تصویری (Body Scam)\n11. 📍 برنامه‌ریزی قرار عمومی امن\n12. 🏃 پروتکل خروج اضطراری\n13. 🏆 امتیاز ایمنی جامعه",
        reply_markup: {
          inline_keyboard: [
            [{ text: "🆘 فعال‌سازی فوری SOS", callback_data: "trigger_sos" }],
            [{ text: "🏠 بازگشت به منو", callback_data: "back_main" }],
          ],
        },
      });
    } else if (data === "trigger_sos") {
      const alerts = (await env.KV.get("db:sos_alerts", "json")) || [];
      alerts.unshift({
        id: alerts.length + 1,
        user_id: user?.id || 0,
        message: "SOS Button pressed in Telegram",
        resolved: false,
        triggered_at: new Date().toISOString(),
      });
      await env.KV.put("db:sos_alerts", JSON.stringify(alerts));
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "🆘 هشدار SOS ثبت شد! لطفاً فوراً به مکان شلوغ و عمومی بروید و با مخاطب امن یا اورژانس تماس بگیرید.",
        reply_markup: tgMainMenu(lang),
      });
    } else if (data === "menu_browse") {
      const candidates = users.filter((u) => u.role !== "admin" && u.telegram_id !== from.id);
      const pick = candidates[Math.floor(Math.random() * candidates.length)] || users[0];
      const modeLabel = RELATIONSHIP_MODES[pick.relationship_mode]?.emoji || "💕";
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: `👤 ${pick.name}, ${pick.age} — 📍 ${pick.city}\n${modeLabel} Mode: ${pick.relationship_mode} | 🧠 MBTI: ${pick.mbti_type || "INFJ"}\n🛡️ Safety Score: ${pick.safety_score}/100\n\n"${pick.bio}"\n\n💬 سوال آغازین (Opening Move):\n${pick.opening_move || "سلام! چه چیزی امروز خوشحالت کرد؟"}`,
        reply_markup: tgMainMenu(lang),
      });
    } else if (data === "menu_mbti") {
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "🧠 برای تست کامل تعاملی MBTI + سبک دلبستگی + زبان عشق یا پیام مستقیم شخصیت‌شناسی، ویژگی‌های خود را در یک جمله بنویسید تا هوش مصنوعی تحلیل کند، یا از وب‌اپ استفاده کنید:\n🌐 https://feminism-dating-bot.pages.dev/app.html",
        reply_markup: tgMainMenu(lang),
      });
    } else {
      await tgSend(token, "sendMessage", {
        chat_id: chatId,
        text: "💬 هر سؤالی درباره رابطه، ایمنی، پروفایل، هم‌بنیان‌گذاری استارتاپی یا آشنایی بین‌المللی دارید همینجا بنویسید:",
        reply_markup: tgMainMenu(lang),
      });
    }
    return { ok: true };
  }

  return { ok: true };
}

// ============================================================
// MAIN FETCH ROUTER
// ============================================================
export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    // When deployed inside Cloudflare Pages (_worker.js), serve static assets directly
    if (env.ASSETS && !path.startsWith("/api/") && !path.startsWith("/webhook/")) {
      return env.ASSETS.fetch(request);
    }

    try {
      const users = await ensureSeedData(env);

      // 1. Health & Root
      if (path === "/" || path === "/api/health") {
        const tests = (await env.KV.get("db:tests", "json")) || [];
        const botConf = (await env.KV.get("db:telegram_bot", "json")) || {};
        return jsonResponse({
          ok: true,
          service: "feminism-dating-api",
          version: "2.0.0",
          ai_enabled: Boolean(env.AI),
          kv_enabled: Boolean(env.KV),
          users_count: users.length,
          tests_count: tests.length,
          modes_supported: Object.keys(RELATIONSHIP_MODES),
          languages_supported: ["fa", "en", "tr", "sv", "de", "ar", "fr", "es", "ku"],
          telegram_webhook: {
            configured: Boolean(env.BOT_TOKEN || botConf.token),
            bot_username: botConf.username || "@femenism_ai_dating_bot",
          },
        });
      }

      // 2. Auth: Register
      if (path === "/api/auth/register" && request.method === "POST") {
        const body = await request.json();
        const username = (body.username || "").trim();
        const email = (body.email || "").trim().toLowerCase();
        const password = body.password || "";

        if (!username || !email || password.length < 6) {
          return jsonResponse({ success: false, message: "نام کاربری، ایمیل و رمز عبور (حداقل ۶ کاراکتر) الزامی است." }, 400);
        }
        if (users.some((u) => u.username.toLowerCase() === username.toLowerCase())) {
          return jsonResponse({ success: false, message: "این نام کاربری قبلاً ثبت شده است" }, 409);
        }
        if (users.some((u) => u.email.toLowerCase() === email)) {
          return jsonResponse({ success: false, message: "این ایمیل قبلاً ثبت شده است" }, 409);
        }

        const nextId = Math.max(...users.map((u) => u.id), 100) + 1;
        const firstName = (body.firstName || body.name || username).trim();
        const lastName = (body.lastName || "").trim();
        const newUser = {
          id: nextId,
          telegram_id: 200000 + nextId,
          username,
          email,
          password_hash: await sha256(password),
          firstName,
          lastName,
          name: `${firstName} ${lastName}`.trim(),
          age: Number(body.age) || 24,
          gender: body.gender || "female",
          looking_for: body.looking_for || "anyone",
          city: (body.city || "تهران").trim(),
          country: body.country || "",
          language: body.language || "fa",
          bio: body.bio || "",
          relationship_mode: body.relationship_mode || "serious",
          mbti_type: null,
          love_language: null,
          attachment_style: null,
          safety_score: 100,
          photo_count: 1,
          is_active: true,
          is_premium: false,
          is_verified: false,
          profile_complete: true,
          role: "user",
          created_at: new Date().toISOString(),
          last_active: new Date().toISOString(),
        };

        users.push(newUser);
        await env.KV.put("db:users", JSON.stringify(users));
        return jsonResponse({
          success: true,
          message: "ثبت‌نام با موفقیت انجام شد",
          user: sanitizeUser(newUser),
        });
      }

      // 3. Auth: Login
      if (path === "/api/auth/login" && request.method === "POST") {
        const body = await request.json();
        const username = (body.username || "").trim();
        const password = body.password || "";
        const passHash = await sha256(password);

        const user = users.find(
          (u) =>
            (u.username.toLowerCase() === username.toLowerCase() ||
              u.email.toLowerCase() === username.toLowerCase()) &&
            u.password_hash === passHash
        );

        if (!user) {
          return jsonResponse({ success: false, message: "نام کاربری یا رمز عبور اشتباه است" }, 401);
        }

        user.last_active = new Date().toISOString();
        await env.KV.put("db:users", JSON.stringify(users));
        return jsonResponse({ success: true, user: sanitizeUser(user) });
      }

      // 4. User Profile & Relationship Tests
      const userRelMatch = path.match(/^\/api\/user\/([^/]+)\/relationship$/);
      if (userRelMatch && request.method === "GET") {
        const identifier = decodeURIComponent(userRelMatch[1]);
        const user = findUser(users, identifier);
        if (!user) return jsonResponse({ error: "User not found" }, 404);
        const allTests = (await env.KV.get("db:tests", "json")) || [];
        const userTests = allTests.filter(
          (t) => t.user_id === user.id || t.user_id === user.telegram_id
        );
        return jsonResponse({
          relationship_mode: user.relationship_mode || "serious",
          mbti_type: user.mbti_type,
          love_language: user.love_language,
          attachment_style: user.attachment_style,
          tests: userTests,
        });
      }

      const userMatch = path.match(/^\/api\/user\/([^/]+)$/);
      if (userMatch) {
        const identifier = decodeURIComponent(userMatch[1]);
        const user = findUser(users, identifier);
        if (!user) return jsonResponse({ error: "User not found" }, 404);

        if (request.method === "GET") {
          return jsonResponse({
            ...sanitizeUser(user),
            photos: Array.from({ length: user.photo_count || 0 }, (_, i) => `photo_${i + 1}`),
          });
        }
        if (request.method === "PUT") {
          const updates = await request.json();
          const allowed = [
            "name", "firstName", "lastName", "age", "gender", "looking_for",
            "city", "country", "bio", "language", "relationship_mode",
            "mbti_type", "love_language", "attachment_style", "opening_move",
          ];
          for (const key of allowed) {
            if (updates[key] !== undefined) user[key] = updates[key];
          }
          if (updates.firstName || updates.lastName) {
            user.name = `${user.firstName || ""} ${user.lastName || ""}`.trim();
          }
          user.profile_complete = Boolean(user.name && user.age && user.city);
          user.last_active = new Date().toISOString();
          await env.KV.put("db:users", JSON.stringify(users));
          return jsonResponse({ success: true, user: sanitizeUser(user) });
        }
      }

      // 5. Profiles Discovery & Swiping
      if (path === "/api/profiles" && request.method === "GET") {
        const modeFilter = url.searchParams.get("mode");
        const langFilter = url.searchParams.get("language");
        let list = users.filter((u) => u.role !== "admin" && u.is_active);
        if (modeFilter && modeFilter !== "all") {
          list = list.filter((u) => u.relationship_mode === modeFilter);
        }
        if (langFilter && langFilter !== "all") {
          list = list.filter((u) => u.language === langFilter);
        }
        return jsonResponse({
          profiles: list.map(sanitizeUser),
          modes: RELATIONSHIP_MODES,
        });
      }

      if (path === "/api/swipe" && request.method === "POST") {
        const body = await request.json();
        const isLike = Boolean(body.is_like);
        let matchesCount = Number((await env.KV.get("db:matches_count")) || "128");
        const matched = isLike && Math.random() < 0.65;
        if (matched) {
          matchesCount += 1;
          await env.KV.put("db:matches_count", String(matchesCount));
        }
        return jsonResponse({
          success: true,
          liked: isLike,
          matched,
          total_matches: matchesCount,
        });
      }

      // 6. Safety Settings & SOS
      if (path === "/api/safety/sos" && request.method === "POST") {
        const body = await request.json();
        const alerts = (await env.KV.get("db:sos_alerts", "json")) || [];
        if (body.action === "resolve") {
          for (const a of alerts) {
            if (!body.user_id || a.user_id === body.user_id) a.resolved = true;
          }
          await env.KV.put("db:sos_alerts", JSON.stringify(alerts));
          return jsonResponse({ success: true, resolved: true });
        }
        const alertObj = {
          id: alerts.length + 1,
          user_id: body.user_id || 1,
          location: body.location || "Shared Safe Check-in",
          message: body.message || "Emergency SOS Triggered",
          resolved: false,
          triggered_at: new Date().toISOString(),
        };
        alerts.unshift(alertObj);
        await env.KV.put("db:sos_alerts", JSON.stringify(alerts));
        return jsonResponse({ success: true, alert: alertObj });
      }

      const safetyMatch = path.match(/^\/api\/safety\/([^/]+)$/);
      if (safetyMatch) {
        const uid = decodeURIComponent(safetyMatch[1]);
        const key = `safety:${uid}`;
        const defaultSafety = {
          user_id: uid,
          secret_friend_name: "",
          secret_friend_contact: "",
          secret_friend_active: false,
          mutual_safety_active: true,
          auto_checkin_enabled: true,
          checkin_interval_minutes: 30,
          sos_enabled: true,
          safe_word: "",
          safe_word_active: false,
          photo_verified: true,
          anonymous_mode: false,
          hide_exact_location: true,
          blur_photos: false,
          screenshot_protection: true,
          block_nude_requests: true,
          consent_quiz_passed: false,
          date_plan_shared: false,
          hidden_words: ["مزاحم", "nude", "crypto"],
          safety_score: 100,
        };
        const current = (await env.KV.get(key, "json")) || defaultSafety;
        if (request.method === "GET") {
          return jsonResponse(current);
        }
        if (request.method === "PUT") {
          const patch = await request.json();
          const merged = { ...current, ...patch, updated_at: new Date().toISOString() };
          await env.KV.put(key, JSON.stringify(merged));
          return jsonResponse({ success: true, safety: merged });
        }
      }

      // 7. Submit Personality / Relationship Mode Compatibility Test
      if (path === "/api/tests/submit" && request.method === "POST") {
        const body = await request.json();
        const userId = body.user_id || 1;
        const user = findUser(users, userId);
        const lang = body.language || user?.language || "fa";
        const testType = body.test_type || "compatibility";
        const mode = body.mode || user?.relationship_mode || "serious";
        const score = Number(body.score ?? 88);

        if (user) {
          if (body.mbti_type) user.mbti_type = body.mbti_type;
          if (body.love_language) user.love_language = body.love_language;
          if (body.attachment_style) user.attachment_style = body.attachment_style;
          if (body.mode) user.relationship_mode = body.mode;
          await env.KV.put("db:users", JSON.stringify(users));
        }

        const prompt =
          testType === "personality"
            ? `Analyze personality test results for safe feminist dating: MBTI=${body.mbti_type}, Love Language=${body.love_language}, Attachment Style=${body.attachment_style}. Provide 3 warm, actionable strengths and boundary tips.`
            : `Analyze compatibility readiness test for mode "${mode}" (${RELATIONSHIP_MODES[mode]?.en || mode}) with score ${score}%. Answers summary: ${JSON.stringify(body.answers || [])}. Give 3 practical insights on compatibility, communication, and safety.`;

        const ai = await runRagAI(env, {
          message: prompt,
          language: lang,
          userProfile: user,
          mode,
        });

        const allTests = (await env.KV.get("db:tests", "json")) || [];
        const record = {
          id: allTests.length + 1,
          user_id: user ? user.id : userId,
          test_type: testType,
          mode,
          score,
          mbti_type: body.mbti_type || user?.mbti_type || null,
          love_language: body.love_language || user?.love_language || null,
          attachment_style: body.attachment_style || user?.attachment_style || null,
          ai_analysis: ai.reply,
          sources: ai.sources,
          date: new Date().toISOString(),
        };
        allTests.unshift(record);
        await env.KV.put("db:tests", JSON.stringify(allTests));

        return jsonResponse({ success: true, test: record });
      }

      // 8. AI RAG Chat & Mode Coach
      if ((path === "/api/ai/chat" || path === "/api/ai/coach") && request.method === "POST") {
        const body = await request.json();
        const message = (body.message || "").trim();
        if (!message) {
          return jsonResponse({ error: "Message is required" }, 400);
        }
        const user = body.user_id ? findUser(users, body.user_id) : null;
        const lang = body.language || user?.language || "fa";
        const mode = body.mode || user?.relationship_mode || null;

        const result = await runRagAI(env, {
          message,
          language: lang,
          userProfile: body.user_profile || user,
          mode,
        });
        return jsonResponse({
          ok: true,
          reply: result.reply,
          sources: result.sources,
          model: result.model,
        });
      }

      // 9. Admin Stats & Paginated Searchable Users + Telegram Webhook Setup
      if (path === "/api/admin/stats" && request.method === "GET") {
        const tests = (await env.KV.get("db:tests", "json")) || [];
        const alerts = (await env.KV.get("db:sos_alerts", "json")) || [];
        const matchesCount = Number((await env.KV.get("db:matches_count")) || "128");
        const botConf = (await env.KV.get("db:telegram_bot", "json")) || {};

        const langDist = {};
        const modeDist = {};
        let totalPhotos = 0;
        const sevenDaysAgo = Date.now() - 7 * 24 * 3600 * 1000;
        let recent7 = 0;

        for (const u of users) {
          const l = u.language || "fa";
          langDist[l] = (langDist[l] || 0) + 1;
          const m = u.relationship_mode || "serious";
          modeDist[m] = (modeDist[m] || 0) + 1;
          totalPhotos += Number(u.photo_count || 0);
          if (u.created_at && new Date(u.created_at).getTime() >= sevenDaysAgo) {
            recent7 += 1;
          }
        }

        return jsonResponse({
          total_users: users.length,
          active_users: users.filter((u) => u.is_active).length,
          premium_users: users.filter((u) => u.is_premium).length,
          recent_users_7days: recent7,
          total_photos: totalPhotos,
          total_tests: tests.length,
          total_matches: matchesCount,
          active_sos_alerts: alerts.filter((a) => !a.resolved).length,
          language_distribution: langDist,
          relationship_modes: modeDist,
          telegram_bot: {
            connected: Boolean(env.BOT_TOKEN || botConf.token),
            username: botConf.username || "@femenism_ai_dating_bot",
            webhook_url: `${url.origin}/webhook/telegram`,
            updated_at: botConf.updated_at || null,
          },
        });
      }

      if (path === "/api/admin/users" && request.method === "GET") {
        const page = Math.max(1, Number(url.searchParams.get("page")) || 1);
        const perPage = Math.min(100, Math.max(1, Number(url.searchParams.get("per_page")) || 20));
        const search = (url.searchParams.get("search") || "").trim().toLowerCase();

        let filtered = users;
        if (search) {
          filtered = users.filter(
            (u) =>
              (u.name || "").toLowerCase().includes(search) ||
              (u.username || "").toLowerCase().includes(search) ||
              (u.city || "").toLowerCase().includes(search) ||
              (u.relationship_mode || "").toLowerCase().includes(search) ||
              (u.language || "").toLowerCase().includes(search)
          );
        }

        const total = filtered.length;
        const totalPages = Math.max(1, Math.ceil(total / perPage));
        const slice = filtered.slice((page - 1) * perPage, page * perPage).map(sanitizeUser);

        return jsonResponse({
          users: slice,
          page,
          per_page: perPage,
          total,
          total_pages: totalPages,
        });
      }

      if (path === "/api/telegram/status" && request.method === "GET") {
        const botConf = (await env.KV.get("db:telegram_bot", "json")) || {};
        return jsonResponse({
          connected: Boolean(env.BOT_TOKEN || botConf.token),
          username: botConf.username || "@femenism_ai_dating_bot",
          first_name: botConf.first_name || "Feminism AI Dating Bot",
          webhook_url: botConf.webhook_url || `${url.origin}/webhook/telegram`,
          updated_at: botConf.updated_at || null,
        });
      }

      if (path === "/api/admin/telegram-webhook" && request.method === "POST") {
        const body = await request.json();
        const botToken = (body.bot_token || "").trim();
        if (!botToken || !botToken.includes(":")) {
          return jsonResponse({ success: false, message: "فرمت توکن تلگرام نامعتبر است." }, 400);
        }

        const meResp = await fetch(`https://api.telegram.org/bot${botToken}/getMe`);
        const meData = await meResp.json();
        if (!meData.ok) {
          const isRevoked = meResp.status === 401;
          return jsonResponse(
            {
              success: false,
              error_code: meData.error_code || meResp.status,
              message: isRevoked
                ? "این توکن توسط تلگرام باطل شده است (401 Unauthorized). در @BotFather دستور /token را بزنید، @femenism_ai_dating_bot را انتخاب کنید و توکن جدید را وارد نمایید."
                : `توکن تلگرام توسط تلگرام رد شد: ${meData.description || "Unauthorized"}`,
            },
            400
          );
        }

        const webhookUrl = `${url.origin}/webhook/telegram`;
        const whResp = await fetch(`https://api.telegram.org/bot${botToken}/setWebhook`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: webhookUrl, drop_pending_updates: true }),
        });
        const whData = await whResp.json();

        // Register native Telegram command menu
        await fetch(`https://api.telegram.org/bot${botToken}/setMyCommands`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            commands: [
              { command: "start", description: "شروع و منوی اصلی / Start" },
              { command: "safety", description: "۱۳ ابزار ایمنی و SOS / 13 Safety Tools" },
              { command: "menu", description: "منوی اصلی / Main Menu" },
              { command: "help", description: "راهنما و مشاور هوش مصنوعی / AI Help" },
            ],
          }),
        }).catch(() => {});

        const botInfo = {
          token: botToken,
          username: `@${meData.result.username}`,
          first_name: meData.result.first_name,
          webhook_url: webhookUrl,
          updated_at: new Date().toISOString(),
        };
        await env.KV.put("db:telegram_bot", JSON.stringify(botInfo));

        return jsonResponse({
          success: Boolean(whData.ok),
          bot_username: botInfo.username,
          webhook_url: webhookUrl,
          telegram_response: whData,
        });
      }

      // 10. Telegram Webhook Receiver
      if (path === "/webhook/telegram" && request.method === "POST") {
        const update = await request.json();
        const res = await handleTelegramUpdate(env, update);
        return jsonResponse(res);
      }

      return jsonResponse({ error: "Not Found", path }, 404);
    } catch (err) {
      return jsonResponse({ error: err.message || "Internal Server Error" }, 500);
    }
  },
};
