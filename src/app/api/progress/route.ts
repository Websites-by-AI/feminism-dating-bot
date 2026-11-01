import { randomUUID } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { progress } from "@/db/schema";
import { currentUser } from "@/lib/auth";

const GUEST_COOKIE = "fd_guest_session";
const uuidPattern = /^[a-f0-9-]{36}$/;

function guestSession(request: NextRequest) {
  const existing = request.cookies.get(GUEST_COOKIE)?.value;
  return existing && uuidPattern.test(existing) ? { id: existing, fresh: false } : { id: randomUUID(), fresh: true };
}

function setGuestCookie(response: NextResponse, id: string) {
  response.cookies.set(GUEST_COOKIE, id, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 365 * 24 * 60 * 60,
  });
}

export async function GET(request: NextRequest) {
  try {
    const guest = guestSession(request);
    const user = await currentUser();
    const condition = user ? eq(progress.userId, user.id) : eq(progress.sessionId, guest.id);
    const items = await db.select().from(progress).where(condition).orderBy(desc(progress.createdAt)).limit(30);
    const response = NextResponse.json({ items });
    if (guest.fresh) setGuestCookie(response, guest.id);
    return response;
  } catch {
    return NextResponse.json({ error: "Could not load your saved moments." }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const kind = String(body.kind || "");
    const title = String(body.title || "").trim().slice(0, 120);
    const data = body.data;
    if (!["quiz", "safety-plan", "journal"].includes(kind) || !title || typeof data !== "object" || data === null || Array.isArray(data) || JSON.stringify(data).length > 10000) {
      return NextResponse.json({ error: "Invalid entry." }, { status: 400 });
    }
    const guest = guestSession(request);
    const user = await currentUser();
    const [item] = await db.insert(progress).values({ sessionId: user ? `user:${user.id}` : guest.id, userId: user?.id ?? null, kind, title, data }).returning();
    const response = NextResponse.json({ item }, { status: 201 });
    if (guest.fresh) setGuestCookie(response, guest.id);
    return response;
  } catch {
    return NextResponse.json({ error: "Could not save your progress." }, { status: 500 });
  }
}
