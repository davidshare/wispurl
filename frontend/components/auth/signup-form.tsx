"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Check } from "lucide-react";
import { toast } from "sonner";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { signup } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/error";
import { cn } from "@/lib/utils";

// Mirrors the backend password policy (min 12, max 1024, no surrounding whitespace).
// The backend remains authoritative; this is a client-side convenience.
const signupSchema = z
  .object({
    email: z.email("Enter a valid email address."),
    password: z
      .string()
      .min(12, "Use at least 12 characters.")
      .max(1024, "That password is too long.")
      .refine((value) => value.trim() === value, "No leading or trailing spaces."),
    confirm: z.string(),
  })
  .refine((data) => data.password === data.confirm, {
    path: ["confirm"],
    message: "Passwords don't match.",
  });

type SignupValues = z.infer<typeof signupSchema>;

function PolicyHint({ met, label }: { met: boolean; label: string }) {
  return (
    <li className="flex items-center gap-2">
      <span
        className={cn(
          "flex size-4 items-center justify-center rounded-full border transition-colors",
          met
            ? "border-violet bg-violet text-paper"
            : "border-border text-transparent",
        )}
        aria-hidden
      >
        <Check className="size-3" />
      </span>
      <span className={met ? "text-foreground" : "text-muted-foreground"}>
        {label}
      </span>
    </li>
  );
}

export function SignupForm() {
  const router = useRouter();
  const [formError, setFormError] = React.useState<string | null>(null);
  const [shake, setShake] = React.useState(0);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: "", password: "", confirm: "" },
    mode: "onChange",
  });

  // useWatch (not watch()) subscribes in a React-Compiler-friendly way.
  const password = useWatch({ control, name: "password" });
  const confirm = useWatch({ control, name: "confirm" });

  const onSubmit = async (values: SignupValues) => {
    setFormError(null);
    try {
      await signup({ email: values.email, password: values.password });
      toast.success("Account created — welcome to WispURL.");
      router.replace("/dashboard");
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "We couldn't create that account.";
      setFormError(message);
      setShake((count) => count + 1);
    }
  };

  return (
    <AuthCard shakeSignal={shake} className="space-y-6">
      <div className="space-y-2">
        <h1 className="font-heading text-h2 font-bold">Get started</h1>
        <p className="text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link
            href="/login"
            className="rounded-sm text-foreground underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Log in
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
            autoComplete="new-password"
            aria-invalid={errors.password ? true : undefined}
            {...register("password")}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirm">Confirm password</Label>
          <Input
            id="confirm"
            type="password"
            autoComplete="new-password"
            aria-invalid={errors.confirm ? true : undefined}
            {...register("confirm")}
          />
        </div>

        <ul className="space-y-1.5 text-sm" aria-live="polite">
          <PolicyHint met={password.length >= 12} label="At least 12 characters" />
          <PolicyHint
            met={password.length > 0 && password.trim() === password}
            label="No leading or trailing spaces"
          />
          <PolicyHint
            met={confirm.length > 0 && password === confirm}
            label="Passwords match"
          />
        </ul>

        <Button
          type="submit"
          variant="signal"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Creating account…" : "Create account"}
        </Button>
      </form>
    </AuthCard>
  );
}
