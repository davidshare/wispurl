import { cn } from "@/lib/utils";

/**
 * Highlight box: one word of a headline in a solid signal box with paper text.
 * Use at most once per page — it's the loudest brand device.
 */
export function Highlight({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-block rounded-xl bg-signal px-3 py-0.5 text-paper",
        className,
      )}
    >
      {children}
    </span>
  );
}
