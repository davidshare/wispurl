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
 * Wraps the gateway's POST /auth/login: forwards credentials, stashes the refresh
 * token in an httpOnly cookie (never returned to JS), and returns the access token
 * plus the user profile to the client.
 */
export async function POST(request: NextRequest) {
  if (request.headers.get(CSRF_HEADER) !== CSRF_VALUE) {
    return NextResponse.json({ detail: "Forbidden" }, { status: 403 });
  }

  let body: { email?: string; password?: string; remember?: boolean };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid request" }, { status: 400 });
  }
  const { email, password, remember = false } = body;

  let upstream: Response;
  try {
    upstream = await fetch(`${GATEWAY_INTERNAL_URL}${API_PREFIX}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    return NextResponse.json(
      { detail: "Authentication service is unavailable." },
      { status: 502 },
    );
  }

  if (!upstream.ok) {
    // Generic message — never reveal whether the email or the password was wrong.
    return NextResponse.json(
      { detail: "Email or password is incorrect." },
      { status: upstream.status >= 500 ? 502 : 401 },
    );
  }

  const tokens = (await upstream.json()) as TokenPair;
  const response = NextResponse.json({
    access_token: tokens.access_token,
    user: { id: decodeAccessSub(tokens.access_token) ?? "", email: email ?? "" },
  });
  setAuthCookies(response, tokens.refresh_token, Boolean(remember));
  return response;
}
