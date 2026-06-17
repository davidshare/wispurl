"use client";

import { Eyebrow } from "@/components/brand/eyebrow";
import { LogoutButton } from "@/components/auth/logout-button";
import { useAuthStore } from "@/stores/auth";

/**
 * Placeholder dashboard — the real links/stats UI is a later prompt. It exists now
 * so the auth flow has a protected destination to land on.
 */
export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="mx-auto w-full max-w-[1200px] space-y-8 px-6 py-16">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-4">
          <Eyebrow>Dashboard</Eyebrow>
          <h1 className="font-heading text-display-lg font-bold">
            You&apos;re in.
          </h1>
          {user?.email ? (
            <p className="font-mono text-sm text-muted-foreground">
              {user.email}
            </p>
          ) : null}
        </div>
        <LogoutButton />
      </div>
      <p className="max-w-xl text-base leading-relaxed text-muted-foreground">
        Your links and analytics land here next. This protected page confirms the
        session layer is working end to end.
      </p>
    </div>
  );
}
