import { API_URL } from "@/lib/env";
import { useAuthStore } from "@/stores/auth";
import type { TokenPair } from "@/lib/api/types";

/** A typed API error carrying the HTTP status and a parsed detail message. */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  /** JSON body (serialized automatically). */
  json?: unknown;
  /** Skip attaching the access token (used by the auth endpoints themselves). */
  auth?: boolean;
}

async function parseError(response: Response): Promise<ApiError> {
  let detail = response.statusText;
  try {
    const body = (await response.json()) as { detail?: string };
    if (typeof body.detail === "string") detail = body.detail;
  } catch {
    // non-JSON error body; keep the status text
  }
  return new ApiError(response.status, detail);
}

// Single-flight refresh: refresh tokens ROTATE on every use and reuse revokes the
// whole family, so concurrent 401s must share ONE refresh call, never fire several.
let refreshInFlight: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const { refreshToken, setTokens, clearSession } = useAuthStore.getState();
  if (!refreshToken) throw new ApiError(401, "Not authenticated");

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    clearSession();
    throw await parseError(response);
  }
  const tokens = (await response.json()) as TokenPair;
  setTokens({
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
  });
  return tokens.access_token;
}

function getRefreshedToken(): Promise<string> {
  refreshInFlight ??= refreshAccessToken().finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

/**
 * Typed fetch wrapper: attaches the access token, transparently refreshes once on
 * a 401 (rotating the refresh token), and throws {@link ApiError} on failure.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { json, auth = true, headers, ...init } = options;

  const send = async (token: string | null): Promise<Response> => {
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
    const newToken = await getRefreshedToken();
    response = await send(newToken);
  }

  if (!response.ok) throw await parseError(response);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
