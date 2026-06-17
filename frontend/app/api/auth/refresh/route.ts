import { NextResponse, type NextRequest } from "next/server";
import { GATEWAY_INTERNAL_URL } from "@/lib/env";
import {
  CSRF_HEADER,
  CSRF_VALUE,
  REFRESH_COOKIE,
  REMEMBER_COOKIE,
} from "@/lib/auth/constants";
import { clearAuthCookies, setAuthCookies } from "@/lib/auth/cookies";

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

/**
 * Rotating refresh against the gateway, using the httpOnly cookie. Returns a fresh
 * access token and re-sets the (rotated) refresh cookie, preserving the original
 * remember-me persistence. On any failure the cookies are cleared and 401 returned,
 * so the client logs out cleanly. The single-flight guard on the client side keeps
 * this from being called concurrently (which would trip family revocation).
 */
export async function POST(request: NextRequest) {
  if (request.headers.get(CSRF_HEADER) !== CSRF_VALUE) {
    return NextResponse.json({ detail: "Forbidden" }, { status: 403 });
  }

  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }
  const remember = request.cookies.get(REMEMBER_COOKIE)?.value === "1";

  let upstream: Response;
  try {
    upstream = await fetch(`${GATEWAY_INTERNAL_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  } catch {
    const response = NextResponse.json(
      { detail: "Authentication service is unavailable." },
      { status: 502 },
    );
    clearAuthCookies(response);
    return response;
  }

  if (!upstream.ok) {
    const response = NextResponse.json(
      { detail: "Session expired" },
      { status: 401 },
    );
    clearAuthCookies(response);
    return response;
  }

  const tokens = (await upstream.json()) as TokenPair;
  const response = NextResponse.json({ access_token: tokens.access_token });
  setAuthCookies(response, tokens.refresh_token, remember);
  return response;
}
