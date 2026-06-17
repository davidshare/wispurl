"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { logout } from "@/lib/api/auth";

/** Logs out (revokes refresh + clears cookies/store) then returns home. */
export function LogoutButton() {
  const router = useRouter();
  const [pending, setPending] = React.useState(false);

  const onClick = async () => {
    setPending(true);
    try {
      await logout();
      toast.success("Logged out.");
      router.replace("/");
    } finally {
      setPending(false);
    }
  };

  return (
    <Button variant="outline" onClick={onClick} disabled={pending}>
      {pending ? "Logging out…" : "Log out"}
    </Button>
  );
}
