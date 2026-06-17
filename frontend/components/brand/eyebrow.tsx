import { cn } from "@/lib/utils";

/**
 * Eyebrow: small uppercase mono label with a 24px rule beside it, sitting above a
 * section heading. A core "Ink & Signal" device — keep it consistent everywhere.
 */
export function Eyebrow({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <span className="h-px w-6 bg-signal" aria-hidden />
      <span className="font-mono text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
        {children}
      </span>
    </div>
  );
}
