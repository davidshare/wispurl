"use client";

import { usePathname } from "next/navigation";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { pageTitle } from "@/components/dashboard/nav";

export function DashboardTopbar() {
  const pathname = usePathname();
  const title = pageTitle(pathname);

  return (
    <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-6" />
      <h1 className="font-heading text-lg font-medium">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        {/* The create-link dialog is wired in the next step (3b). */}
        <Button
          variant="signal"
          onClick={() => toast.info("Link creation arrives in the next step.")}
        >
          <Plus className="size-4" />
          Create link
        </Button>
        <ThemeToggle />
      </div>
    </header>
  );
}
