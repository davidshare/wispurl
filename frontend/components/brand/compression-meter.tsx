"use client";

import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import { DURATION, EASE_OUT } from "@/lib/motion";

/**
 * Compression meter: a thin 2px bar that fills left-to-right. The platform's
 * progress/loading motif and a decorative accent beneath eyebrows. When `loop`, it
 * animates continuously (loading); otherwise it fills once on mount.
 *
 * Reduced-motion-safe: under `prefers-reduced-motion: reduce` it renders a static
 * filled bar with no animation.
 */
export function CompressionMeter({
  className,
  loop = false,
  duration = DURATION.meter,
}: {
  className?: string;
  loop?: boolean;
  duration?: number;
}) {
  const reduceMotion = useReducedMotion();

  return (
    <div
      className={cn(
        "h-0.5 w-full overflow-hidden rounded-full bg-mist",
        className,
      )}
      role="presentation"
    >
      {reduceMotion ? (
        <div className="h-full w-full rounded-full bg-signal" />
      ) : (
        <motion.div
          className="h-full origin-left rounded-full bg-signal"
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{
            duration,
            ease: EASE_OUT,
            repeat: loop ? Infinity : 0,
            repeatType: "loop",
          }}
        />
      )}
    </div>
  );
}
