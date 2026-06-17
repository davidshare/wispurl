/**
 * Public runtime config. The frontend talks ONLY to the gateway; every API call
 * is built from this base. Set NEXT_PUBLIC_API_URL in the environment.
 */
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";
