import { Eyebrow } from "@/components/brand/eyebrow";

/** Placeholder — account settings are built in a later prompt. */
export default function SettingsPage() {
  return (
    <div className="space-y-4 p-6 md:p-8">
      <Eyebrow>Settings</Eyebrow>
      <p className="max-w-xl text-base leading-relaxed text-muted-foreground">
        Account and preferences will live here.
      </p>
    </div>
  );
}
