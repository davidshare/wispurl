import { API_URL } from "@/lib/env";
import { CSRF_HEADER, CSRF_VALUE } from "@/lib/auth/constants";
import { decodeAccessSub } from "@/lib/auth/jwt";
import { ApiError } from "@/lib/api/error";
import { useAuthStore } from "@/stores/auth";

interface RequestOptions extends Omit<RequestInit, "body"> {
  json?: unknown;
  auth?: boolean;
}

async function parseError(response: Response): Promise<ApiError> {
  let detail = response.statusText;
  try {
    const body = (await response.json()) as { detail?: string };
    if (typeof body.detail === "string") detail = body.detail;
  } catch {
    // non-JSON body; keep the status text
  }
  return new ApiError(response.status, detail);
}

/**
 * Silent refresh against the cookie-backed Next route. The refresh token lives in
 * an httpOnly cookie, so this request carries no token in JS — the server reads the
 * cookie, rotates it, and returns a fresh access token. Updates the store and
 * returns success.
 */
export async function refreshSession(): Promise<boolean> {
  const store = useAuthStore.getState();
  try {
    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { [CSRF_HEADER]: CSRF_VALUE },
    });
    if (!response.ok) {
      store.clear();
      return false;
    }
    const data = (await response.json()) as { access_token: string };
    // Keep the persisted user; fall back to the token's sub if we have none yet.
    const sub = decodeAccessSub(data.access_token);
    const user =
      store.user ?? (sub ? { id: sub, email: "" } : null);
    store.setSession({ user, accessToken: data.access_token });
    return true;
  } catch {
    store.clear();
    return false;
  }
}

// SINGLE-FLIGHT: all concurrent 401s await ONE refresh. The refresh token rotates
// on every use and reuse revokes the whole family, so it must never be spent twice
// in parallel — this shared promise guarantees exactly one refresh call at a time.
let refreshInFlight: Promise<boolean> | null = null;

function sharedRefresh(): Promise<boolean> {
  refreshInFlight ??= refreshSession().finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  const next = encodeURIComponent(window.location.pathname);
  window.location.assign(`/login?next=${next}`);
}

/**
 * Typed fetch wrapper for data calls to the gateway. Attaches the in-memory access
 * token; on a 401 it attempts ONE shared refresh and retries; if that fails it
 * clears the session and redirects to /login.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { json, auth = true, headers, ...init } = options;

  const send = (token: string | null): Promise<Response> => {
    const finalHeaders = new Headers(headers);
    if (json !== undefined) finalHeaders.set("Content-Type", "application/json");
    if (auth && token) finalHeaders.set("Authorization", `Bearer ${token}`);
    return fetch(`${API_URL}${path}`, {
      ...init,
      headers: finalHeaders,
      body: json !== undefined ? JSON.stringify(json) : undefined,
    });
  };

  let response = await send(auth ? useAuthStore.getState().accessToken : null);

  if (response.status === 401 && auth) {
    const refreshed = await sharedRefresh();
    if (!refreshed) {
      redirectToLogin();
      throw new ApiError(401, "Session expired");
    }
    response = await send(useAuthStore.getState().accessToken);
  }

  if (!response.ok) throw await parseError(response);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
