import Link from "next/link";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Highlight } from "@/components/brand/highlight";
import { Button } from "@/components/ui/button";

/** Brand-voice 404. */
export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[1200px] flex-col items-start justify-center gap-6 px-6">
      <Eyebrow>404</Eyebrow>
      <h1 className="max-w-2xl font-heading text-display-lg font-bold">
        That link led <Highlight>nowhere</Highlight>.
      </h1>
      <p className="max-w-md text-lg leading-relaxed text-muted-foreground">
        The page you&apos;re after doesn&apos;t exist — or its short code expired.
        Let&apos;s get you back.
      </p>
      <Button variant="signal" size="lg" asChild>
        <Link href="/">Back home</Link>
      </Button>
    </main>
  );
}
