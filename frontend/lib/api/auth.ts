import { CSRF_HEADER, CSRF_VALUE } from "@/lib/auth/constants";
import { ApiError } from "@/lib/api/error";
import type { AuthUser } from "@/lib/api/types";
import { useAuthStore } from "@/stores/auth";

interface SessionResponse {
  access_token: string;
  user: AuthUser;
}

const jsonHeaders = {
  "Content-Type": "application/json",
  [CSRF_HEADER]: CSRF_VALUE,
};

async function postSession(
  path: string,
  body: unknown,
): Promise<SessionResponse> {
  const response = await fetch(path, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = "Something went wrong. Please try again.";
    try {
      const data = (await response.json()) as { detail?: string };
      if (typeof data.detail === "string") detail = data.detail;
    } catch {
      // keep the default message
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as SessionResponse;
}

/** Log in via the cookie-backed Next route; stores the in-memory access token. */
export async function login(input: {
  email: string;
  password: string;
  remember: boolean;
}): Promise<void> {
  const session = await postSession("/api/auth/login", input);
  useAuthStore
    .getState()
    .setSession({ user: session.user, accessToken: session.access_token });
}

/** Create an account and establish a session in one round trip. */
export async function signup(input: {
  email: string;
  password: string;
}): Promise<void> {
  const session = await postSession("/api/auth/signup", input);
  useAuthStore
    .getState()
    .setSession({ user: session.user, accessToken: session.access_token });
}

/** Revoke the refresh token, clear cookies, and reset the store. */
export async function logout(): Promise<void> {
  try {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: { [CSRF_HEADER]: CSRF_VALUE },
    });
  } finally {
    useAuthStore.getState().clear();
  }
}
