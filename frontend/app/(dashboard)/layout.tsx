import type { Metadata } from "next";
import { AuthGuard } from "@/components/auth/auth-guard";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";

// Authenticated area — not for indexing.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

/**
 * Protected shell: the client guard restores/verifies the session, then the
 * sidebar + topbar shell wraps every dashboard page.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <DashboardShell>{children}</DashboardShell>
    </AuthGuard>
  );
}
