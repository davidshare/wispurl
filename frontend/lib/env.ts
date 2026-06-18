/**
 * Public runtime config. The frontend talks ONLY to the gateway; every API call
 * is built from this base. Set NEXT_PUBLIC_API_URL in the environment.
 */
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

/** API version prefix for every gateway endpoint (the short-link redirect is not versioned). */
export const API_PREFIX = "/v1";

/** Public site origin, used for canonical URLs and Open Graph metadata. */
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

/**
 * Gateway URL as seen FROM the Next.js server (route handlers). In Docker this is
 * the internal hostname (http://gateway:8000); locally it falls back to the public
 * URL. Distinct from API_URL, which the browser uses for direct data calls.
 */
export const GATEWAY_INTERNAL_URL =
  process.env.GATEWAY_INTERNAL_URL ?? API_URL;
