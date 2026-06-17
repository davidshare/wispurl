"use client";

import * as React from "react";
import { usePathname, useRouter } from "next/navigation";
import { CompressionMeter } from "@/components/brand/compression-meter";
import { refreshSession } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth";

/**
 * Client guard for the in-memory session path. If there's already an access token
 * in memory, render immediately. Otherwise (e.g. after a reload, where the token is
 * gone but a refresh cookie may exist) attempt ONE silent refresh; on failure,
 * redirect to /login?next=… The render gate is driven purely by store state, so the
 * effect only kicks off async work — it never sets state synchronously.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const status = useAuthStore((state) => state.status);
  const accessToken = useAuthStore((state) => state.accessToken);

  const authenticated = status === "authenticated" && Boolean(accessToken);

  React.useEffect(() => {
    if (authenticated) return;
    let active = true;
    void refreshSession().then((ok) => {
      if (active && !ok) {
        router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      }
    });
    return () => {
      active = false;
    };
  }, [authenticated, router, pathname]);

  if (!authenticated) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-6">
        <div className="w-full max-w-xs space-y-3 text-center">
          <p className="font-mono text-sm text-muted-foreground">
            Restoring your session…
          </p>
          <CompressionMeter loop />
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
