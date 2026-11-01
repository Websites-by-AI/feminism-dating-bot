import { NextRequest, NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { sessions, users } from "@/db/schema";
import { COOKIE_NAME, currentUser, hashPassword, hashToken, newToken, verifyPassword } from "@/lib/auth";

export async function GET() {
  return NextResponse.json({ user: await currentUser() });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const action = String(body.action || "");
    if (action === "logout") {
      const response = NextResponse.json({ user: null });
      const token = request.cookies.get(COOKIE_NAME)?.value;
      if (token) await db.delete(sessions).where(eq(sessions.tokenHash, hashToken(token)));
      response.cookies.delete(COOKIE_NAME);
      return response;
    }
    if (action !== "login" && action !== "register") return NextResponse.json({ error: "Invalid action." }, { status: 400 });
    const email = String(body.email || "").trim().toLowerCase();
    const password = String(body.password || "");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || password.length < 8) {
      return NextResponse.json({ error: "Enter a valid email and a password of at least 8 characters." }, { status: 400 });
    }
    let user: { id: number; name: string; email: string; passwordHash: string } | undefined;
    if (action === "register") {
      const name = String(body.name || "").trim().slice(0, 80);
      if (!name) return NextResponse.json({ error: "Please enter your name." }, { status: 400 });
      const existing = await db.select({ id: users.id }).from(users).where(eq(users.email, email)).limit(1);
      if (existing.length) return NextResponse.json({ error: "An account with this email already exists." }, { status: 409 });
      const inserted = await db.insert(users).values({ name, email, passwordHash: hashPassword(password) }).returning();
      user = inserted[0];
    } else {
      const found = await db.select().from(users).where(eq(users.email, email)).limit(1);
      user = found[0];
      if (!user || !verifyPassword(password, user.passwordHash)) {
        return NextResponse.json({ error: "Incorrect email or password." }, { status: 401 });
      }
    }
    if (!user) return NextResponse.json({ error: "Could not sign in." }, { status: 500 });
    const token = newToken();
    await db.insert(sessions).values({ userId: user.id, tokenHash: hashToken(token), expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) });
    const response = NextResponse.json({ user: { id: user.id, name: user.name, email: user.email } });
    response.cookies.set(COOKIE_NAME, token, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: 30 * 24 * 60 * 60 });
    return response;
  } catch {
    return NextResponse.json({ error: "Something went wrong. Please try again." }, { status: 500 });
  }
}
