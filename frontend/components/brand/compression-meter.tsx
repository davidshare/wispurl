"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

/**
 * Compression meter: a thin 2px bar that fills left-to-right. The platform's
 * progress/loading motif and a decorative accent beneath eyebrows. When
 * `loop`, it animates continuously (loading); otherwise it fills once on mount.
 */
export function CompressionMeter({
  className,
  loop = false,
  duration = 1.1,
}: {
  className?: string;
  loop?: boolean;
  duration?: number;
}) {
  return (
    <div
      className={cn("h-0.5 w-full overflow-hidden rounded-full bg-mist", className)}
      role="presentation"
    >
      <motion.div
        className="h-full origin-left rounded-full bg-signal"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{
          duration,
          ease: [0.22, 1, 0.36, 1],
          repeat: loop ? Infinity : 0,
          repeatType: "loop",
        }}
      />
    </div>
  );
}
