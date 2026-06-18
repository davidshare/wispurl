"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";

/** Root error boundary (brand voice). Covers marketing + auth segments. */
export default function RootError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  React.useEffect(() => {
    console.error("[app] error", error);
  }, [error]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[1200px] flex-col items-start justify-center gap-6 px-6">
      <h1 className="max-w-2xl font-heading text-display-lg font-bold">
        Well, that snapped.
      </h1>
      <p className="max-w-md text-lg leading-relaxed text-muted-foreground">
        Something went wrong on this page. Try again — if it keeps happening, give
        it a minute.
      </p>
      <Button variant="signal" size="lg" onClick={reset}>
        Try again
      </Button>
    </main>
  );
}
