import { Suspense } from "react";
import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/login-form";

export const metadata: Metadata = {
  title: "Log in",
  robots: { index: false, follow: false },
};

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="h-80 w-full animate-pulse rounded-2xl border border-border bg-card" />
      }
    >
      <LoginForm />
    </Suspense>
  );
}
