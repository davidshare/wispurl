/**
 * One motion language. Shared duration/easing tokens so every animation (reveals,
 * card entrance, compression meter, chart) feels consistent. Everything that uses
 * these is also gated on prefers-reduced-motion at the component level.
 */
export const EASE_OUT = [0.22, 1, 0.36, 1] as const;

export const DURATION = {
  fast: 0.2,
  base: 0.4,
  slow: 0.7,
  meter: 1.1,
} as const;
