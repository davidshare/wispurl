import { NextResponse, type NextRequest } from "next/server";
import { API_PREFIX, GATEWAY_INTERNAL_URL } from "@/lib/env";
import {
  CSRF_HEADER,
  CSRF_VALUE,
  REFRESH_COOKIE,
} from "@/lib/auth/constants";
import { clearAuthCookies } from "@/lib/auth/cookies";

/**
 * Revoke the refresh token at the gateway and clear the cookies. Best-effort on the
 * upstream call — the cookies are cleared regardless so the client always ends up
 * logged out.
 */
export async function POST(request: NextRequest) {
  if (request.headers.get(CSRF_HEADER) !== CSRF_VALUE) {
    return NextResponse.json({ detail: "Forbidden" }, { status: 403 });
  }

  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value;
  if (refreshToken) {
    try {
      await fetch(`${GATEWAY_INTERNAL_URL}${API_PREFIX}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // best-effort; clear cookies regardless
    }
  }

  const response = NextResponse.json({ ok: true });
  clearAuthCookies(response);
  return response;
}
