# WispURL — "Ink & Signal" style

The design system for WispURL: a URL shortener + analytics product. Voice is
confident, plain, and a little playful. **Sentence case everywhere**, active-voice
labels ("Create link", not "Submit"). The signature idea: a link is something you
**compress** — monospace short codes as hero type, a compression animation, and a
thin meter motif.

> The palette intentionally avoids the mint/coral reference look. It leans on a near
> black ink, a warm paper, and a single loud signal-orange used sparingly.

## Color

Brand colors are defined as CSS variables in `app/globals.css` and converted to
**OKLCH** for Tailwind v4. Hex is the source of truth; OKLCH is what ships.

| Token        | Hex       | OKLCH                          | Role |
| ------------ | --------- | ------------------------------ | ---- |
| `--ink`      | `#0B0F14` | `oklch(0.1665 0.0124 254.17)`  | Foreground text, dark surfaces |
| `--paper`    | `#FCFCFA` | `oklch(0.9905 0.0026 106.45)`  | App background (warm off-white) |
| `--signal`   | `#FF5A1F` | `oklch(0.6824 0.2108 37.70)`   | Primary accent / CTA / brand highlight — **use sparingly** |
| `--violet`   | `#5B43F5` | `oklch(0.5299 0.2494 279.73)`  | Secondary accent: data viz, active/interactive states |
| `--mist`     | `#EEF0F2` | `oklch(0.9542 0.0034 247.86)`  | Cards, fills, alternating bands (light) |
| `--line-light` | `#E2E5E9` | `oklch(0.9208 0.0063 255.48)` | Borders (light) |
| `--line-dark`  | `#1A1F26` | `oklch(0.2374 0.0154 256.81)` | Borders / lifted surfaces (dark) |

**Dark mode** flips ink ↔ paper for surface/text, and **brightens** signal
(`oklch(0.72 0.19 40)`) and violet (`oklch(0.66 0.21 280)`) for contrast on ink.

All shadcn semantic tokens are mapped to the brand so components inherit it:
`primary = signal`, `secondary = violet`, `background = paper/ink`,
`foreground = ink/paper`, `muted/accent = mist`, `border = line`, `ring = violet`.
Charts lead with violet then signal.

## Type (`next/font`, self-hosted)

- **Display — Space Grotesk** (700/500): headlines, big numbers, section titles.
- **Body — Inter** (400/500/600): prose, labels, UI.
- **Mono — JetBrains Mono** (500/700): short codes, URLs, stats — _data is the brand_.

Fluid scale via `clamp()` (defined as Tailwind v4 `--text-*` tokens):

| Token         | Size                       | Line height | Letter spacing |
| ------------- | -------------------------- | ----------- | -------------- |
| `display-xl`  | `clamp(3.5rem, 6vw, 5rem)` | 1.05        | -0.02em |
| `display-lg`  | `clamp(2.5rem, 4.5vw, 3.5rem)` | 1.05    | -0.02em |
| `h2`          | `2rem`                     | 1.1         | -0.015em |
| `h3`          | `1.5rem`                   | 1.2         | -0.01em |
| body          | `1rem`                     | 1.6         | — |
| small         | `0.875rem`                 | —           | — |

Headlines are tight; body is relaxed (1.6).

## Spacing & layout

- 8px grid; **96–128px** vertical rhythm between major sections.
- Max content width **1200px**, centered, comfortable gutters.
- Cards: radius 16px (`--radius: 1rem`), 24–32px padding, subtle shadow + 1px border.
- Buttons: dark **ink pill** default; **signal-orange** for the single primary CTA
  per view (`<Button variant="signal">`). All buttons are pill-shaped.

## Signature devices

These ARE the brand — keep them consistent (`components/brand/`):

- **Eyebrow** — small uppercase mono label + a 24px rule, above section headings.
- **Highlight box** — one headline word in a solid signal box with paper text; at
  most once per page.
- **Compression meter** — a thin 2px bar that fills left-to-right; loading/progress
  motif and a decorative accent under eyebrows.
- **Short codes** — always JetBrains Mono, domain dimmed, code in full ink/signal.

**Alternating bands**: paper → mist → paper → ink (dark band) → paper, for rhythm
without heavy dividers.

## Stack

Next.js 16 (App Router, RSC, Turbopack) · React 19 · TypeScript strict · Tailwind v4
(CSS-first `@theme`, OKLCH) · shadcn/ui (radix base, neutral) · Zustand · TanStack
Query v5 · TanStack Table v8 · react-hook-form + zod · framer-motion · Recharts ·
next-themes. The frontend talks ONLY to the gateway via `NEXT_PUBLIC_API_URL`.

> Note: the prompt referenced shadcn's "new-york" style; the current shadcn CLI
> renamed styles (this project uses the `radix` base, `neutral` base color). The
> tokens above override shadcn's defaults regardless of style name.
