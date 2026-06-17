import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AuthUser } from "@/lib/api/types";

export type AuthStatus = "loading" | "authenticated" | "unauthenticated";

/**
 * Auth/session store.
 *
 * SECURITY: the access token lives IN MEMORY ONLY — it is never persisted, so it
 * can't be read from localStorage by an XSS payload and is gone on reload (a fresh
 * one is obtained via the httpOnly-cookie refresh path). Only the non-sensitive
 * user profile is persisted, purely so the UI can render an identity immediately on
 * reload while the access token is being refreshed. The refresh token is never in
 * this store at all — it lives only in an httpOnly cookie.
 */
interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  status: AuthStatus;
  setSession: (session: { user: AuthUser | null; accessToken: string }) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      status: "loading",
      setSession: ({ user, accessToken }) =>
        set({ user, accessToken, status: "authenticated" }),
      clear: () =>
        set({ user: null, accessToken: null, status: "unauthenticated" }),
    }),
    {
      name: "wispurl-user",
      // Persist ONLY the user profile — never the access token or status.
      partialize: (state) => ({ user: state.user }),
    },
  ),
);
