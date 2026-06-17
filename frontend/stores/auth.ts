import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AuthUser } from "@/lib/api/types";

/**
 * Auth/session state.
 *
 * Tokens are persisted to localStorage so a reload keeps the session. This is the
 * usual SPA tradeoff (vulnerable to XSS) — acceptable here because the frontend
 * only ever talks to the gateway over TLS; moving to httpOnly cookies later would
 * require gateway support.
 */
interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (session: {
    user: AuthUser | null;
    accessToken: string;
    refreshToken: string;
  }) => void;
  setTokens: (tokens: { accessToken: string; refreshToken: string }) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setSession: ({ user, accessToken, refreshToken }) =>
        set({ user, accessToken, refreshToken }),
      setTokens: ({ accessToken, refreshToken }) =>
        set({ accessToken, refreshToken }),
      clearSession: () =>
        set({ user: null, accessToken: null, refreshToken: null }),
    }),
    { name: "wispurl-auth" },
  ),
);
