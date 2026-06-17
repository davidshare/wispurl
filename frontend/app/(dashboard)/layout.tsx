import type { Metadata } from "next";
import { AuthGuard } from "@/components/auth/auth-guard";

// Authenticated area — not for indexing.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

/** Protected shell: the client guard restores/verifies the session before render. */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}
