import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Highlight } from "@/components/brand/highlight";
import { CompressionMeter } from "@/components/brand/compression-meter";
import { Button } from "@/components/ui/button";

/**
 * Placeholder home. The foundation prompt builds nothing beyond this and the
 * styleguide — real marketing/dashboard pages come later.
 */
export default function Home() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto w-full max-w-[1200px] px-6">
        <section className="flex flex-col items-start gap-8 py-24 sm:py-32">
          <Eyebrow>Link shortener &amp; analytics</Eyebrow>
          <h1 className="max-w-3xl font-heading text-display-xl font-bold">
            Make every link <Highlight>shorter</Highlight> — and see what
            happens next.
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
            WispURL compresses long URLs into clean short codes, then tracks the
            clicks so you know what is actually working.
          </p>

          <div className="w-full max-w-md space-y-2">
            <div className="flex items-center gap-2 font-mono text-sm">
              <span className="text-muted-foreground">wisp.url/</span>
              <span className="font-bold text-signal">a1b2c3</span>
            </div>
            <CompressionMeter />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button variant="signal" size="lg" asChild>
              <Link href="/styleguide">Create link</Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link href="/styleguide">View the styleguide</Link>
            </Button>
          </div>
        </section>
      </main>
    </>
  );
}
