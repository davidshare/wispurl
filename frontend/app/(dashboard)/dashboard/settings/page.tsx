"use client";

import { useRouter } from "next/navigation";
import { Monitor, Moon, Sun, TriangleAlert } from "lucide-react";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import { Eyebrow } from "@/components/brand/eyebrow";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { logout } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth";

const THEME_OPTIONS = [
  { value: "system", label: "System", Icon: Monitor },
  { value: "light", label: "Light", Icon: Sun },
  { value: "dark", label: "Dark", Icon: Moon },
];

export default function SettingsPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const { theme, setTheme } = useTheme();

  const onLogoutEverywhere = async () => {
    await logout();
    toast.success("Logged out.");
    router.replace("/");
  };

  return (
    <div className="max-w-2xl space-y-8 p-6 md:p-8">
      <div className="space-y-3">
        <Eyebrow>Settings</Eyebrow>
        <h1 className="font-heading text-display-lg font-bold">Settings</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading">Account</CardTitle>
          <CardDescription>Your account details.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={user?.email ?? ""} readOnly disabled />
          </div>
          <div className="space-y-1.5">
            <Button variant="outline" onClick={onLogoutEverywhere}>
              Log out everywhere
            </Button>
            <p className="text-xs text-muted-foreground">
              Logs out this session now. Full revocation across all devices needs
              backend support (refresh-token family revocation).
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading">Appearance</CardTitle>
          <CardDescription>Choose how WispURL looks.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {THEME_OPTIONS.map(({ value, label, Icon }) => (
              <Button
                key={value}
                type="button"
                variant={theme === value ? "default" : "outline"}
                onClick={() => setTheme(value)}
                className="gap-2"
              >
                <Icon className="size-4" />
                {label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-destructive/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-heading text-destructive">
            <TriangleAlert className="size-4" />
            Danger zone
          </CardTitle>
          <CardDescription>
            Irreversible account actions will live here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            disabled
            className="border-destructive/30 text-destructive"
          >
            Delete account (coming soon)
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
