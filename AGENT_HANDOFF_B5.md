# Feminism Dating — B5 agent handoff

**Project:** safety-first dating and relationship-reflection web app.  
**Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, PostgreSQL, Drizzle ORM.  
**Purpose:** hand this source archive to another developer or agent for continued work. This is not a user-data backup.

## Get running

1. Extract the source ZIP and run `npm ci` with Node.js 20+.
2. Run a local PostgreSQL database. Copy `.env.example` to `.env` and set `DATABASE_URL` to the database connection string. The included `drizzle.config.json` targets a local development database at `postgresql://postgres:postgres@127.0.0.1:5432/app_db`; update that config for a different development database.
3. Run `npx drizzle-kit push` to create the tables.
4. Run `npm run dev` for local development or `npm run build && npm run start` for production.
5. Visit `/api/health` to check database connectivity.

## Product map

- `src/app/page.tsx` — landing page, relationship-mode quizzes, love/sex/identity reflection topics, coach chat UI, safety center, account forms, dashboard, share modal.
- `src/app/globals.css` and `src/app/psychology.css` — responsive styles.
- `src/app/api/auth/route.ts` and `src/lib/auth.ts` — account registration/login, password hashing, session cookies.
- `src/app/api/progress/route.ts` — save/read quizzes, safety plans, journal reflections.
- `src/app/api/coach/route.ts` — curated rule-based educational replies.
- `src/db/schema.ts` — PostgreSQL tables for users, sessions, and progress.
- `public/images/hero-portrait.png` — generated hero image.

## Important implementation notes

- The coach is **curated rule-based guidance**, not a live generative AI model or a clinical service. There is no external AI key in the package.
- SOS is informational: the site **does not** dispatch emergency help, monitor users, send alerts to friends, or verify identities. It provides emergency-call links and planning advice.
- The website interface switches selected hero/navigation copy between English, Farsi, and Turkish; most remaining content is in English. Other displayed languages are not fully implemented.
- Quizzes are self-reflection tools, not psychological diagnoses. MBTI-inspired questions are not a validated clinical assessment.
- The Telegram area links to BotFather but does not run a connected bot. Never enter a bot token into the browser.
- Anonymous entries use a server-issued, HTTP-only guest cookie; signed-in entries are account-owned and do not remain visible as guest entries after sign-out. Guest data on a shared browser may still be visible to others using that browser. Progress requests do not accept a client-supplied session ID. Review privacy, data deletion, consent, and authorization before real-world sensitive-data deployment.
- No payment, subscription, analytics, accounting, or revenue/income reporting exists in this project. Do not invent financial figures.
- The site is an application prototype, not a production-ready dating matching service.

## Suggested next steps for another agent

1. Implement proper multilingual coverage and localization of all quizzes and coach guidance.
2. Add privacy controls, data export/deletion, and stricter authorization for sensitive saved content.
3. If requested, integrate a vetted AI provider server-side with transparent limitations and safety escalation.
4. Build actual matching, identity verification, and check-in services only with robust user consent and operational safeguards.
5. Add tests for authentication, progress isolation, and safety-critical copy.

## Research references used for the educational section

- Rashed, Fouladi & Fabian, *Navigating intimate relationships of Iranians in the context of immigration* (2025): https://journals.sagepub.com/doi/10.1177/02654075241307983
- McNeil, Rehman & Fallis, *The Influence of Attachment Styles on Sexual Communication Behavior* (2018): https://pubmed.ncbi.nlm.nih.gov/28509583/

**Share safely:** this archive excludes `.env`, database contents, user records, session tokens, `node_modules`, and build output. Recheck before redistributing modified copies.
