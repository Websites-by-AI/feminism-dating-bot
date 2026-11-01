import { createHash, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";
import { eq, and, gt } from "drizzle-orm";
import { db } from "@/db";
import { sessions, users } from "@/db/schema";

export const COOKIE_NAME = "feminism_dating_session";
export const hashToken = (token: string) => createHash("sha256").update(token).digest("hex");
export const newToken = () => randomBytes(32).toString("hex");
export const hashPassword = (password: string) => {
  const salt = randomBytes(16).toString("hex");
  return `${salt}:${scryptSync(password, salt, 64).toString("hex")}`;
};
export const verifyPassword = (password: string, stored: string) => {
  const [salt, key] = stored.split(":");
  if (!salt || !key) return false;
  const saved = Buffer.from(key, "hex");
  const candidate = scryptSync(password, salt, saved.length);
  return saved.length === candidate.length && timingSafeEqual(saved, candidate);
};
export async function currentUser() {
  const token = (await cookies()).get(COOKIE_NAME)?.value;
  if (!token) return null;
  const rows = await db.select({ id: users.id, name: users.name, email: users.email })
    .from(sessions).innerJoin(users, eq(sessions.userId, users.id))
    .where(and(eq(sessions.tokenHash, hashToken(token)), gt(sessions.expiresAt, new Date()))).limit(1);
  return rows[0] ?? null;
}
