"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";

/** Group-level error boundary for dashboard pages. */
export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  React.useEffect(() => {
    console.error("[dashboard] error", error);
  }, [error]);

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-6 text-center">
      <h2 className="font-heading text-h2 font-bold">Something went wrong</h2>
      <p className="max-w-sm text-sm text-muted-foreground">
        We hit an unexpected error loading this page. Try again, and if it keeps
        happening, sign out and back in.
      </p>
      <Button variant="signal" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
