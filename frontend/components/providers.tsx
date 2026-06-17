"use client";

import * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/theme-provider";
import { makeQueryClient } from "@/lib/query/client";

/**
 * App-wide client providers: theme (next-themes), server-state (TanStack Query),
 * tooltips, and toasts (sonner). Mounted once in the root layout.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  // One QueryClient per browser session, kept stable across re-renders.
  const [queryClient] = React.useState(makeQueryClient);

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        <TooltipProvider delayDuration={200}>{children}</TooltipProvider>
        <Toaster position="bottom-right" />
      </QueryClientProvider>
    </ThemeProvider>
  );
}
