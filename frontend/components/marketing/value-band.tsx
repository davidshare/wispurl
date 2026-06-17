import { Eyebrow } from "@/components/brand/eyebrow";
import { Reveal } from "@/components/marketing/reveal";
import { StatDonut } from "@/components/marketing/stat-donut";

const PROOF_POINTS = [
  "Every click counted — no analytics blind spots.",
  "Slugs people can actually read, trust, and type.",
  "Set it, share it, watch it work in real time.",
];

/**
 * Value band (on mist): the "why short" thesis, a few proof points, and a small
 * stat card with an animated donut + engagement figure.
 */
export function ValueBand() {
  return (
    <section id="about" className="bg-mist dark:bg-card">
      <div className="mx-auto grid w-full max-w-[1200px] items-center gap-12 px-6 py-24 md:grid-cols-2 md:py-32">
        <Reveal className="space-y-6">
          <Eyebrow>Why short</Eyebrow>
          <h2 className="font-heading text-h2 font-bold">
            A short link is a promise: clean to share, and impossible to lose
            track of.
          </h2>
          <ul className="space-y-3">
            {PROOF_POINTS.map((point) => (
              <li key={point} className="flex items-start gap-3">
                <span
                  className="mt-2 h-px w-6 shrink-0 bg-signal"
                  aria-hidden
                />
                <span className="text-base leading-relaxed text-muted-foreground">
                  {point}
                </span>
              </li>
            ))}
          </ul>
        </Reveal>

        {/* Stat card */}
        <Reveal
          delayMs={120}
          className="flex items-center gap-6 rounded-2xl border border-border bg-background p-8 shadow-sm"
        >
          <StatDonut />
          <div className="space-y-2">
            <div className="font-heading text-display-lg font-bold text-violet">
              2.4×
            </div>
            <p className="max-w-[12rem] text-sm leading-relaxed text-muted-foreground">
              more clicks tracked than raw links — and you see every single one.
            </p>
            <div className="flex flex-wrap gap-3 pt-1 font-mono text-xs">
              <span className="flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-violet" aria-hidden />
                Tracked
              </span>
              <span className="flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-signal" aria-hidden />
                Converted
              </span>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
