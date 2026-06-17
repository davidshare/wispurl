import type { NextResponse } from "next/server";
import {
  REFRESH_COOKIE,
  REFRESH_MAX_AGE_SECONDS,
  REMEMBER_COOKIE,
} from "@/lib/auth/constants";

// Secure requires HTTPS, which localhost-over-http isn't — so only in production.
const isProduction = process.env.NODE_ENV === "production";

/**
 * Set the refresh cookie (httpOnly, Secure in prod, SameSite=Strict) plus the
 * remember flag. With "remember me" the cookies persist for the refresh TTL;
 * otherwise they're session cookies (kept during the session, gone on browser
 * close). Either way the refresh token never reaches JavaScript.
 */
export function setAuthCookies(
  response: NextResponse,
  refreshToken: string,
  remember: boolean,
): void {
  const base = {
    httpOnly: true as const,
    secure: isProduction,
    sameSite: "strict" as const,
    path: "/",
  };
  const options = remember
    ? { ...base, maxAge: REFRESH_MAX_AGE_SECONDS }
    : base;
  response.cookies.set(REFRESH_COOKIE, refreshToken, options);
  response.cookies.set(REMEMBER_COOKIE, remember ? "1" : "0", options);
}

/** Expire both auth cookies (logout, or a failed/absent refresh). */
export function clearAuthCookies(response: NextResponse): void {
  const expired = {
    httpOnly: true as const,
    secure: isProduction,
    sameSite: "strict" as const,
    path: "/",
    maxAge: 0,
  };
  response.cookies.set(REFRESH_COOKIE, "", expired);
  response.cookies.set(REMEMBER_COOKIE, "", expired);
}
