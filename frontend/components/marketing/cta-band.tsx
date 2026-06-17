import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CompressionMeter } from "@/components/brand/compression-meter";
import { Reveal } from "@/components/marketing/reveal";

/** Closing call-to-action band (on mist). */
export function CtaBand() {
  return (
    <section id="contact" className="bg-mist dark:bg-card">
      <div className="mx-auto w-full max-w-[1200px] px-6 py-24 md:py-32">
        <Reveal className="mx-auto flex max-w-2xl flex-col items-center gap-8 text-center">
          <h2 className="font-heading text-display-lg font-bold">
            Make your links stand out.
          </h2>
          <p className="max-w-md text-lg leading-relaxed text-muted-foreground">
            Short, branded, and tracked from the first click. It takes about a
            minute.
          </p>
          <CompressionMeter className="max-w-xs" />
          <Button variant="signal" size="lg" asChild>
            <Link href="/signup">Register now</Link>
          </Button>
        </Reveal>
      </div>
    </section>
  );
}
