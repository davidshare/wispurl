"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CompressionMeter } from "@/components/brand/compression-meter";
import { CopyButton } from "@/components/dashboard/copy-button";
import { useCreateLink } from "@/lib/query/links";
import { ApiError } from "@/lib/api/error";
import type { Link } from "@/lib/api/types";

const SLUG_PATTERN = /^[A-Za-z0-9_-]{3,32}$/;

function isHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

// Mirrors the backend rules; the backend stays authoritative.
const createLinkSchema = z.object({
  long_url: z
    .string()
    .min(1, "Enter a URL.")
    .max(2048, "That URL is too long.")
    .refine(isHttpUrl, "Use an http:// or https:// URL."),
  custom_slug: z
    .string()
    .trim()
    .regex(SLUG_PATTERN, "3–32 characters: letters, numbers, - or _.")
    .or(z.literal(""))
    .optional(),
  expires_at: z
    .string()
    .refine(
      (value) =>
        value === "" || new Date(`${value}T23:59:59`).getTime() > Date.now(),
      "Pick a date in the future.",
    )
    .or(z.literal(""))
    .optional(),
});

type CreateLinkValues = z.infer<typeof createLinkSchema>;

/** Convert a date-input value (YYYY-MM-DD) to an end-of-day ISO timestamp. */
function toExpiryIso(value: string): string {
  return new Date(`${value}T23:59:59`).toISOString();
}

export function CreateLinkDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const createLink = useCreateLink();
  const [created, setCreated] = React.useState<Link | null>(null);

  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors },
  } = useForm<CreateLinkValues>({
    resolver: zodResolver(createLinkSchema),
    defaultValues: { long_url: "", custom_slug: "", expires_at: "" },
    mode: "onChange",
  });

  const today = new Date().toISOString().slice(0, 10);

  const onSubmit = (values: CreateLinkValues) => {
    const slug = values.custom_slug?.trim();
    createLink.mutate(
      {
        long_url: values.long_url.trim(),
        custom_slug: slug ? slug : undefined,
        expires_at: values.expires_at ? toExpiryIso(values.expires_at) : undefined,
      },
      {
        onSuccess: (link) => {
          setCreated(link);
          reset();
          toast.success("Link created");
        },
        onError: (error) => {
          if (error instanceof ApiError && error.status === 409) {
            setError("custom_slug", { message: "That slug is taken." });
          } else if (error instanceof ApiError && error.status === 429) {
            toast.error(
              "You're creating links quickly — try again in a moment.",
            );
          } else {
            toast.error("We couldn't create that link. Please try again.");
          }
        },
      },
    );
  };

  const handleOpenChange = (next: boolean) => {
    if (!next) {
      setCreated(null);
      reset();
    }
    onOpenChange(next);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        {created ? (
          <>
            <DialogHeader>
              <DialogTitle className="font-heading">Link created</DialogTitle>
              <DialogDescription>
                Your short link is ready to share.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <code className="flex-1 truncate rounded-lg border border-border bg-muted px-3 py-2 font-mono text-sm">
                  {created.short_url}
                </code>
                <CopyButton value={created.short_url} label="Copy short link" />
              </div>
              <CompressionMeter />
            </div>

            <DialogFooter className="sm:justify-between">
              <Button variant="ghost" onClick={() => setCreated(null)}>
                Create another
              </Button>
              <DialogClose asChild>
                <Button variant="signal">Done</Button>
              </DialogClose>
            </DialogFooter>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="font-heading">Create link</DialogTitle>
              <DialogDescription>
                Paste a long URL. Add a custom slug and expiry if you like.
              </DialogDescription>
            </DialogHeader>

            <form
              noValidate
              onSubmit={handleSubmit(onSubmit)}
              className="space-y-5"
            >
              <div className="space-y-2">
                <Label htmlFor="long_url">Long URL</Label>
                <Input
                  id="long_url"
                  inputMode="url"
                  placeholder="https://example.com/a-very-long-link"
                  aria-invalid={errors.long_url ? true : undefined}
                  {...register("long_url")}
                />
                {errors.long_url ? (
                  <p className="text-sm text-destructive">
                    {errors.long_url.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label htmlFor="custom_slug">Custom slug (optional)</Label>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-muted-foreground">
                    wisp.url/
                  </span>
                  <Input
                    id="custom_slug"
                    placeholder="launch"
                    aria-invalid={errors.custom_slug ? true : undefined}
                    {...register("custom_slug")}
                  />
                </div>
                {errors.custom_slug ? (
                  <p className="text-sm text-destructive">
                    {errors.custom_slug.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label htmlFor="expires_at">Expires (optional)</Label>
                <Input
                  id="expires_at"
                  type="date"
                  min={today}
                  aria-invalid={errors.expires_at ? true : undefined}
                  {...register("expires_at")}
                />
                {errors.expires_at ? (
                  <p className="text-sm text-destructive">
                    {errors.expires_at.message}
                  </p>
                ) : null}
              </div>

              <DialogFooter>
                <Button
                  type="submit"
                  variant="signal"
                  className="w-full"
                  disabled={createLink.isPending}
                >
                  {createLink.isPending ? "Creating…" : "Create link"}
                </Button>
              </DialogFooter>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
