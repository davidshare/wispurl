"use client";

import * as React from "react";

function subscribe(onChange: () => void): () => void {
  window.addEventListener("online", onChange);
  window.addEventListener("offline", onChange);
  return () => {
    window.removeEventListener("online", onChange);
    window.removeEventListener("offline", onChange);
  };
}

/**
 * App-wide offline banner. Uses useSyncExternalStore (SSR-safe, no effect-setState)
 * so it never trips the purity/effect lint rules. Server snapshot assumes online.
 */
export function OfflineBanner() {
  const online = React.useSyncExternalStore(
    subscribe,
    () => navigator.onLine,
    () => true,
  );

  if (online) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed inset-x-0 top-0 z-[100] bg-destructive px-4 py-2 text-center text-sm font-medium text-white"
    >
      You&apos;re offline — changes may not save until you reconnect.
    </div>
  );
}
