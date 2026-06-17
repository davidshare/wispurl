import type { Metadata } from "next";
import Link from "next/link";
import { Wordmark } from "@/components/marketing/wordmark";
import { Highlight } from "@/components/brand/highlight";
import { CompressionMeter } from "@/components/brand/compression-meter";

// Auth pages must not be indexed.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

/** Split layout: a dark brand panel beside a centered card on paper. */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen md:grid-cols-2">
      {/* Brand panel (hidden on mobile) */}
      <aside className="dark hidden flex-col justify-between bg-background p-12 text-foreground md:flex">
        <Wordmark />
        <div className="space-y-6">
          <h2 className="max-w-sm font-heading text-display-lg font-bold">
            Links worth <Highlight>sharing</Highlight>.
          </h2>
          <p className="max-w-sm text-base leading-relaxed text-muted-foreground">
            Short codes, branded slugs, and click analytics — all in one quiet,
            fast place.
          </p>
          <CompressionMeter className="max-w-xs" loop />
        </div>
        <p className="font-mono text-xs text-muted-foreground">
          wisp.url/<span className="text-signal">launch</span>
        </p>
      </aside>

      {/* Form card on paper */}
      <main className="flex flex-col items-center justify-center bg-background px-6 py-12">
        <div className="mb-8 md:hidden">
          <Wordmark />
        </div>
        <div className="w-full max-w-md">{children}</div>
        <p className="mt-8 text-xs text-muted-foreground">
          <Link
            href="/"
            className="rounded-sm underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Back home
          </Link>
        </p>
      </main>
    </div>
  );
}
