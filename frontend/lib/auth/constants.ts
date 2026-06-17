/** Shared auth constants (cookie names + CSRF header) used by client and routes. */

// httpOnly refresh-token cookie and a companion flag recording "remember me".
export const REFRESH_COOKIE = "wisp_refresh";
export const REMEMBER_COOKIE = "wisp_remember";

// 7 days — matches the backend refresh-token TTL.
export const REFRESH_MAX_AGE_SECONDS = 60 * 60 * 24 * 7;

/**
 * Custom header the client attaches to every /api/auth/* request. Cross-site
 * forms can't set custom headers without triggering a CORS preflight (which these
 * same-origin routes never satisfy), so requiring it — together with the cookies'
 * SameSite=Strict — defends the cookie-backed routes against CSRF.
 */
export const CSRF_HEADER = "x-wisp-csrf";
export const CSRF_VALUE = "1";
