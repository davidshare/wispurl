"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/error";

const loginSchema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
  remember: z.boolean(),
});

type LoginValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/dashboard";

  const [formError, setFormError] = React.useState<string | null>(null);
  const [shake, setShake] = React.useState(0);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", remember: false },
  });

  const onSubmit = async (values: LoginValues) => {
    setFormError(null);
    try {
      await login(values);
      toast.success("Welcome back.");
      router.replace(next);
    } catch (error) {
      // Generic — never reveal whether the email or the password was wrong.
      setFormError("Email or password is incorrect.");
      setShake((count) => count + 1);
      if (error instanceof ApiError && error.status >= 500) {
        toast.error("Login is temporarily unavailable. Please try again.");
      }
    }
  };

  return (
    <AuthCard shakeSignal={shake} className="space-y-6">
      <div className="space-y-2">
        <h1 className="font-heading text-h2 font-bold">Log in</h1>
        <p className="text-sm text-muted-foreground">
          New here?{" "}
          <Link
            href="/signup"
            className="rounded-sm text-foreground underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Create an account
          </Link>
          .
        </p>
      </div>

      {formError ? (
        <p
          role="alert"
          className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
        >
          {formError}
        </p>
      ) : null}

      <form noValidate onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            aria-invalid={errors.email ? true : undefined}
            {...register("email")}
          />
          {errors.email ? (
            <p className="text-sm text-destructive">{errors.email.message}</p>
          ) : null}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            aria-invalid={errors.password ? true : undefined}
            {...register("password")}
          />
          {errors.password ? (
            <p className="text-sm text-destructive">
              {errors.password.message}
            </p>
          ) : null}
        </div>

        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <input
            type="checkbox"
            className="size-4 rounded border-border accent-violet"
            {...register("remember")}
          />
          Remember me on this device
        </label>

        <Button
          type="submit"
          variant="signal"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Logging in…" : "Log in"}
        </Button>
      </form>
    </AuthCard>
  );
}
