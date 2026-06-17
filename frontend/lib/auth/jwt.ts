/**
 * Decode the `sub` (user id) claim from an access token WITHOUT verifying it.
 *
 * This is display-only convenience (e.g. to know the user id after a silent
 * refresh). Verification is the backend's job — never trust this for authorization.
 * Uses `atob`, available in both the browser and the Node route-handler runtime.
 */
export function decodeAccessSub(token: string): string | null {
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const base64 = part
      .replace(/-/g, "+")
      .replace(/_/g, "/")
      .padEnd(Math.ceil(part.length / 4) * 4, "=");
    const payload = JSON.parse(atob(base64)) as { sub?: unknown };
    return typeof payload.sub === "string" ? payload.sub : null;
  } catch {
    return null;
  }
}
