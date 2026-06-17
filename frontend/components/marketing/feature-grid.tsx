import {
  Gift,
  MousePointerClick,
  QrCode,
  ShieldCheck,
  Tag,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Reveal } from "@/components/marketing/reveal";

interface Feature {
  title: string;
  description: string;
  Icon: LucideIcon;
}

const FEATURES: Feature[] = [
  {
    title: "Easy",
    description: "Paste a long URL, get a short link back. That's the whole flow.",
    Icon: Zap,
  },
  {
    title: "Branded slugs",
    description: "Claim custom codes that read like you, not like noise.",
    Icon: Tag,
  },
  {
    title: "Free",
    description: "Shorten and track without reaching for your wallet.",
    Icon: Gift,
  },
  {
    title: "Click tracking",
    description: "See totals, trends, and top referrers for every link.",
    Icon: MousePointerClick,
  },
  {
    title: "QR codes",
    description: "Every link gets a scannable code, ready to download.",
    Icon: QrCode,
  },
  {
    title: "Safe redirects",
    description: "Only http and https — no sketchy schemes pass through.",
    Icon: ShieldCheck,
  },
];

/**
 * Feature grid (on paper): a 3x2 grid of cards, each a circular icon badge,
 * title, and one-line description. Hover micro-interactions are CSS-only (no
 * client JS): the card lifts and the badge shifts from violet to signal.
 */
export function FeatureGrid() {
  return (
    <section id="features" className="bg-background">
      <div className="mx-auto w-full max-w-[1200px] space-y-12 px-6 py-24 md:py-32">
        <Reveal className="space-y-4">
          <Eyebrow>More than a shortener</Eyebrow>
          <h2 className="max-w-2xl font-heading text-h2 font-bold">
            Everything you need to ship a link — and learn from it.
          </h2>
        </Reveal>

        <Reveal>
          <ul className="grid gap-5 sm:grid-cols-2 md:grid-cols-3">
            {FEATURES.map(({ title, description, Icon }) => (
              <li
                key={title}
                className="group h-full rounded-2xl border border-border bg-card p-8 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-signal/40 hover:shadow-md"
              >
                <span className="flex size-12 items-center justify-center rounded-full bg-violet/10 text-violet transition-colors duration-200 group-hover:bg-signal/15 group-hover:text-signal">
                  <Icon className="size-5" />
                </span>
                <h3 className="mt-5 font-heading text-h3 font-medium">
                  {title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {description}
                </p>
              </li>
            ))}
          </ul>
        </Reveal>
      </div>
    </section>
  );
}
