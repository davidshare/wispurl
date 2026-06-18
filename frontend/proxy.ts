import { NextResponse, type NextRequest } from "next/server";
import { REFRESH_COOKIE } from "@/lib/auth/constants";
import { API_URL } from "@/lib/env";

const isDev = process.env.NODE_ENV !== "production";

/** Build a per-request, nonce-based CSP. No unsafe-inline for scripts. */
function contentSecurityPolicy(nonce: string): string {
  return [
    "default-src 'self'",
    // strict-dynamic + nonce: only the nonce'd bootstrap (and scripts it loads) run.
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ""}`,
    // styles are not script — unsafe-inline here is acceptable (next/font, etc.).
    "style-src 'self' 'unsafe-inline'",
    `img-src 'self' data: blob: ${API_URL}`,
    "font-src 'self'",
    // The browser only ever connects to itself (Next routes) and the gateway.
    `connect-src 'self' ${API_URL}${isDev ? " ws:" : ""}`,
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
  ].join("; ");
}

/**
 * Proxy (Next 16): (1) edge auth gate for /dashboard/* — redirect to /login when no
 * refresh cookie; (2) attach a per-request nonce CSP to every page response. Next
 * reads the CSP from the request header and nonces its own scripts automatically.
 */
export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname === "/dashboard" || pathname.startsWith("/dashboard/")) {
    if (!request.cookies.has(REFRESH_COOKIE)) {
      const url = request.nextUrl.clone();
      url.pathname = "/login";
      url.search = `?next=${encodeURIComponent(pathname)}`;
      return NextResponse.redirect(url);
    }
  }

  const nonce = btoa(crypto.randomUUID());
  const csp = contentSecurityPolicy(nonce);

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("content-security-policy", csp);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("content-security-policy", csp);
  return response;
}

// Run on all routes except API handlers and static assets.
export const config = {
  matcher: [
    {
      source: "/((?!api|_next/static|_next/image|favicon.ico).*)",
    },
  ],
};
