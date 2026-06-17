import type { Metadata } from "next";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Highlight } from "@/components/brand/highlight";
import { Reveal } from "@/components/marketing/reveal";
import { CtaBand } from "@/components/marketing/cta-band";
import { buildMetadata } from "@/lib/seo";

export function generateMetadata(): Metadata {
  return buildMetadata({
    title: "About",
    description:
      "Why WispURL exists: short links that are clean to share and honest about what happens after the click.",
    path: "/about",
  });
}

export default function AboutPage() {
  return (
    <>
      <section className="mx-auto w-full max-w-[1200px] px-6">
        <Reveal className="flex flex-col items-start gap-6 py-24 sm:py-28">
          <Eyebrow>About</Eyebrow>
          <h1 className="max-w-3xl font-heading text-display-lg font-bold">
            We think a link should be <Highlight>honest</Highlight>.
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
            WispURL started from a simple frustration: shortening a link
            shouldn&apos;t mean losing sight of it. So we built a shortener where
            the analytics are the point, not an afterthought.
          </p>
        </Reveal>
      </section>

      <section className="bg-mist dark:bg-card">
        <div className="mx-auto grid w-full max-w-[1200px] gap-12 px-6 py-24 md:grid-cols-2 md:py-32">
          <Reveal className="space-y-4">
            <Eyebrow>What we value</Eyebrow>
            <h2 className="font-heading text-h2 font-bold">
              Plain, fast, and a little playful.
            </h2>
          </Reveal>
          <Reveal delayMs={120} className="space-y-6">
            <p className="text-base leading-relaxed text-muted-foreground">
              No dark patterns, no vanity metrics — just the numbers that tell
              you whether a link is working. Short codes are the hero, the data
              is the brand, and the orange is reserved for the moments that
              matter.
            </p>
            <p className="text-base leading-relaxed text-muted-foreground">
              It&apos;s a small product with strong opinions, and we like it that
              way.
            </p>
          </Reveal>
        </div>
      </section>

      <CtaBand />
    </>
  );
}
