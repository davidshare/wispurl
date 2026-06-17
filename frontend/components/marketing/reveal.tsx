"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Scroll-triggered reveal: fades + rises into place once, when it first enters the
 * viewport (IntersectionObserver, then disconnects).
 *
 * Reduced motion is respected two ways: the transition/initial-hidden classes are
 * all `motion-safe:` (so under `prefers-reduced-motion: reduce` the content is
 * simply visible with no movement), and the observer is skipped entirely in that
 * case — no animation work is scheduled.
 */
export function Reveal({
  children,
  className,
  delayMs = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delayMs?: number;
}) {
  const ref = React.useRef<HTMLDivElement>(null);
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    // Reduced motion: leave it to CSS (motion-safe classes won't apply) — visible.
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect();
            break;
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -10% 0px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={{ transitionDelay: delayMs ? `${delayMs}ms` : undefined }}
      className={cn(
        "motion-safe:transition-all motion-safe:duration-700 motion-safe:ease-out",
        visible
          ? "opacity-100 translate-y-0"
          : "motion-safe:translate-y-4 motion-safe:opacity-0",
        className,
      )}
    >
      {children}
    </div>
  );
}
