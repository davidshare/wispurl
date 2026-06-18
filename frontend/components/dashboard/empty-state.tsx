import type { LucideIcon } from "lucide-react";

/** Directional empty state: an icon, a line of copy, and a primary action. */
export function EmptyState({
  Icon,
  title,
  description,
  action,
}: {
  Icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-border bg-card/50 px-6 py-16 text-center">
      <span className="flex size-12 items-center justify-center rounded-full bg-violet/10 text-violet">
        <Icon className="size-6" />
      </span>
      <div className="space-y-1">
        <h2 className="font-heading text-h3 font-medium">{title}</h2>
        <p className="mx-auto max-w-sm text-sm text-muted-foreground">
          {description}
        </p>
      </div>
      {action}
    </div>
  );
}
