import { NextResponse, type NextRequest } from "next/server";
import { API_PREFIX, GATEWAY_INTERNAL_URL } from "@/lib/env";
import { CSRF_HEADER, CSRF_VALUE } from "@/lib/auth/constants";
import { setAuthCookies } from "@/lib/auth/cookies";
import { decodeAccessSub } from "@/lib/auth/jwt";

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

/**
 * Wraps the gateway's POST /auth/signup, then immediately logs in so signup lands
 * the user straight in the dashboard. Signup establishes a persistent session
 * (remember = true). Errors stay generic to avoid account enumeration.
 */
export async function POST(request: NextRequest) {
  if (request.headers.get(CSRF_HEADER) !== CSRF_VALUE) {
    return NextResponse.json({ detail: "Forbidden" }, { status: 403 });
  }

  let body: { email?: string; password?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid request" }, { status: 400 });
  }
  const { email, password } = body;

  try {
    const signupRes = await fetch(`${GATEWAY_INTERNAL_URL}${API_PREFIX}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!signupRes.ok) {
      const detail =
        signupRes.status === 422
          ? "Password does not meet the requirements."
          : "We couldn't create that account.";
      return NextResponse.json(
        { detail },
        { status: signupRes.status >= 500 ? 502 : signupRes.status },
      );
    }

    // Account created — establish a session via login.
    const loginRes = await fetch(`${GATEWAY_INTERNAL_URL}${API_PREFIX}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!loginRes.ok) {
      return NextResponse.json(
        { detail: "Account created — please log in." },
        { status: 502 },
      );
    }

    const tokens = (await loginRes.json()) as TokenPair;
    const response = NextResponse.json({
      access_token: tokens.access_token,
      user: {
        id: decodeAccessSub(tokens.access_token) ?? "",
        email: email ?? "",
      },
    });
    setAuthCookies(response, tokens.refresh_token, true);
    return response;
  } catch {
    return NextResponse.json(
      { detail: "Authentication service is unavailable." },
      { status: 502 },
    );
  }
}
