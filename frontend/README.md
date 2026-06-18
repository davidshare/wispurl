# WispURL — Frontend

The single web client for WispURL: a marketing site, auth pages, and an authenticated
dashboard for creating links and viewing analytics. It talks **only to the gateway**.

Next.js 16 (App Router, RSC, Turbopack) · React 19 · TypeScript (strict) · Tailwind CSS v4
· shadcn/ui · TanStack Query v5 · Zustand · react-hook-form + zod · Recharts · framer-motion
· next-themes. Design system: see [STYLE.md](./STYLE.md) ("Ink & Signal").

## Structure

```
app/
  (marketing)/   public site: home, /features, /about, /contact  (indexable)
  (auth)/        /login, /signup                                  (noindex)
  (dashboard)/   /dashboard, /dashboard/links[/(code)/analytics], /analytics, /settings
  api/auth/*     BFF route handlers (login/signup/refresh/logout)
  api/contact    stub contact endpoint
components/  ui (shadcn) · brand · marketing · dashboard · auth
lib/         api (client, auth, types) · query (client, keys, hooks) · auth · env · seo
stores/      auth + ui (Zustand)
proxy.ts     edge auth gate for /dashboard/* + per-request nonce CSP
```

## Auth & session model

- **Access token in memory only** (Zustand) — never in localStorage. Only the
  non-sensitive user profile is persisted so the UI can render on reload.
- **Refresh token in an httpOnly + SameSite=Strict cookie**, set by the BFF route handlers
  in `app/api/auth/*` (a thin server layer that wraps the gateway so the refresh token
  never reaches JS). "Remember me" controls cookie persistence.
- **One fetch wrapper** (`lib/api/client.ts`): attaches the access token; on a 401 it does a
  **single-flight** refresh (shared in-flight promise so the rotating refresh token is never
  double-spent), retries once, else clears the session and redirects to `/login`.
- **Protection**: `proxy.ts` redirects cookieless `/dashboard/*` to `/login?next=…` at the
  edge; a client guard restores the in-memory session.

## API contract

The browser calls the gateway at `NEXT_PUBLIC_API_URL`; every endpoint is under `/v1`
(`API_PREFIX` in `lib/env.ts`). Auth flows go through same-origin BFF routes
(`/api/auth/*`), which call the gateway server-side via `GATEWAY_INTERNAL_URL`.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8080` | Gateway URL the **browser** uses (inlined at build time) |
| `GATEWAY_INTERNAL_URL` | `= NEXT_PUBLIC_API_URL` | Gateway URL the **server** (BFF routes) uses; in Docker, `http://gateway:8000` |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | Canonical/OG base URL |

## Develop

```bash
npm install
npm run dev      # http://localhost:3000
npm run lint
npm run build
```

> Requires Node 20.9+/22+ (this repo develops on Node via nvm). `NEXT_PUBLIC_*` values are
> baked at **build** time — changing the API URL requires a rebuild.

## Docker

Multi-stage build producing Next's standalone server, run as a non-root user
(`next.config.ts` sets `output: "standalone"`). `NEXT_PUBLIC_API_URL` is a build arg;
`GATEWAY_INTERNAL_URL` is a runtime env. See the root `docker-compose.yml`.

## Security headers / CSP

Static headers (HSTS, `nosniff`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`)
are set in `next.config.ts`; a per-request **nonce CSP** (no `unsafe-inline` scripts;
`connect-src` limited to the API) is applied in `proxy.ts`. Reading the nonce in the root
layout opts pages into dynamic rendering — the deliberate cost of the strict CSP.
