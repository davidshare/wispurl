"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

/**
 * Light/dark toggle. Icons are swapped purely via the `dark` class that
 * next-themes sets on <html>, so there's no theme-dependent render on the server
 * (no hydration mismatch, no mounted-guard effect). The resolved theme is only
 * read inside the click handler.
 */
export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();

  return (
    <Button
      variant="outline"
      size="icon"
      aria-label="Toggle theme"
      onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
    >
      <Sun className="hidden size-4 dark:block" />
      <Moon className="size-4 dark:hidden" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
