import { NextRequest, NextResponse } from "next/server";

const guidance = [
  { words: ["unsafe", "danger", "emergency", "threat", "hurt", "scared", "sos"], reply: "Your safety comes first. If you are in immediate danger, leave if you can and contact your local emergency services now. Move toward a public place or trusted person, and share your location with someone you trust. This chat cannot monitor you or send emergency help." },
  { words: ["consent", "boundary", "pressure", "no ", "uncomfortable"], reply: "A boundary does not need a defense. You could say: ‘I’m not comfortable with that, and I need you to respect my decision.’ Notice whether they respond with care or try to negotiate your no. Consent should be freely given, specific, and reversible at any time." },
  { words: ["iranian", "diaspora", "persian", "family expectations", "between cultures", "two cultures"], reply: "There is no single way to be an Iranian woman or to honor your heritage. Some people feel pulled between family closeness, privacy, autonomy, and the expectations of where they grew up. You can appreciate what matters to you without surrendering your choices. You might ask yourself: ‘Which values feel like mine, and which expectations feel borrowed?’ If it feels safe, try telling a trusted person what support—not permission—you need." },
  { words: ["sex", "desire", "intimacy", "sexual", "shame", "waiting"], reply: "Your relationship with sex and intimacy belongs to you. There is no universal timeline and no ‘right’ level of desire. A gentle way to begin a conversation is: ‘I’d like to talk about what helps us both feel comfortable, and what we each do and don’t want.’ You can want closeness and still say no; you can also change your mind. A respectful partner makes room for both people’s needs without pressure." },
  { words: ["attachment", "reassurance", "independence in love", "fear of abandonment"], reply: "Wanting reassurance or space is human, not a flaw. Attachment ideas can help you notice patterns, but they are not fixed identities or diagnoses. Try naming a specific need: ‘I feel more connected when we check in after a difficult conversation.’ Then notice whether there is room for both connection and independence." },
  { words: ["startup",  "cofounder", "co-founder", "equity", "vesting", "founder"], reply: "Before mixing romance and business, write down roles, decision rights, equity, vesting, pay, and what happens if either relationship ends. Avoid open-ended unpaid work. A useful first question is: ‘What would a fair written agreement look like for both of us?’ Consider independent legal advice before signing." },
  { words: ["international", "long distance", "visa", "relocation", "abroad", "travel", "money", "scam"], reply: "Take cross-border relationships at a pace that preserves your independence. Verify identity through live video, keep control of your documents and money, and never send funds under pressure. Discuss communication expectations, cultural differences, and a realistic visit plan before considering relocation." },
  { words: ["first date", "meet", "location", "check-in", "date plan"], reply: "For a first meeting, choose a public place, arrange your own transportation, and tell a trusted person where you’ll be. Set a check-in time and an easy exit phrase. You can change your mind or leave at any point, for any reason." },
  { words: ["mbti", "personality", "compatible", "compatibility"], reply: "Personality types can start a useful conversation, but they cannot predict whether someone will treat you well. Look for consistent respect, communication, shared values, and how they handle boundaries. Ask: ‘How do we each prefer to repair a misunderstanding?’" },
  { words: ["red flag", "control", "jealous", "manipulat", "love bomb"], reply: "Trust patterns over promises. Isolation, pressure, monitoring, rushed commitment, and repeated boundary-pushing deserve attention. You don’t need proof that someone is ‘bad’ to step back. Consider talking through what happened with a trusted person." },
];

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();
    if (typeof message !== "string" || !message.trim() || message.length > 2000) return NextResponse.json({ error: "Please enter a message under 2,000 characters." }, { status: 400 });
    const lower = message.toLowerCase();
    const match = guidance.find((item) => item.words.some((word) => lower.includes(word)));
    const reply = match?.reply ?? "That sounds worth exploring with care. Start with what you want, what feels comfortable, and which boundaries matter most to you. In a healthy connection, you should be able to communicate those needs without pressure. What part of this situation feels most uncertain right now?";
    return NextResponse.json({ reply, note: "General educational guidance, not emergency, legal, or mental-health services." });
  } catch {
    return NextResponse.json({ error: "Could not process that message." }, { status: 400 });
  }
}
