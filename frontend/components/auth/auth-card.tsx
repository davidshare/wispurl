"use client";

import * as React from "react";
import { motion, useAnimationControls, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import { DURATION, EASE_OUT } from "@/lib/motion";

/**
 * Card wrapper for the auth forms: a subtle entrance (fade/rise) and a
 * reduced-motion-safe error shake. Increment `shakeSignal` to trigger the shake
 * (e.g. on a failed login). Under `prefers-reduced-motion: reduce` both the
 * entrance and the shake are skipped.
 */
export function AuthCard({
  children,
  shakeSignal = 0,
  className,
}: {
  children: React.ReactNode;
  shakeSignal?: number;
  className?: string;
}) {
  const reduceMotion = useReducedMotion();
  const controls = useAnimationControls();

  React.useEffect(() => {
    if (shakeSignal > 0 && !reduceMotion) {
      void controls.start({
        x: [0, -8, 8, -6, 6, 0],
        transition: { duration: DURATION.base, ease: "easeInOut" },
      });
    }
  }, [shakeSignal, reduceMotion, controls]);

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 12 }}
      animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
      transition={{ duration: DURATION.base, ease: EASE_OUT }}
    >
      <motion.div
        animate={controls}
        className={cn(
          "w-full rounded-2xl border border-border bg-card p-8 shadow-sm",
          className,
        )}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}
