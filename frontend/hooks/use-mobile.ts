import * as React from "react";

const MOBILE_BREAKPOINT = 768;

function subscribe(onChange: () => void): () => void {
  const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
  mql.addEventListener("change", onChange);
  return () => mql.removeEventListener("change", onChange);
}

/**
 * True when the viewport is below the mobile breakpoint. Implemented with
 * useSyncExternalStore (rather than an effect that sets state) so it's SSR-safe and
 * doesn't trip the effect-setState lint rule. The server snapshot is `false`.
 */
export function useIsMobile(): boolean {
  return React.useSyncExternalStore(
    subscribe,
    () => window.innerWidth < MOBILE_BREAKPOINT,
    () => false,
  );
}
