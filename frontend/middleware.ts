import { NextResponse, type NextRequest } from "next/server";
import { REFRESH_COOKIE } from "@/lib/auth/constants";

/**
 * Edge guard for the cookie path: if there's no refresh cookie, the visitor has no
 * resumable session, so /dashboard is redirected to /login (preserving the intended
 * path in `next`) before the page even loads. When the cookie is present, the
 * request proceeds and the in-memory client guard does a silent refresh.
 */
export function middleware(request: NextRequest) {
  if (request.cookies.has(REFRESH_COOKIE)) {
    return NextResponse.next();
  }
  const url = request.nextUrl.clone();
  url.pathname = "/login";
  url.search = `?next=${encodeURIComponent(request.nextUrl.pathname)}`;
  return NextResponse.redirect(url);
}

// The (dashboard) route group's pages live at top-level URLs (route groups don't
// add a URL prefix), so each protected path is listed explicitly.
export const config = {
  matcher: [
    "/dashboard",
    "/dashboard/:path*",
    "/links",
    "/links/:path*",
    "/analytics",
    "/analytics/:path*",
    "/settings",
    "/settings/:path*",
  ],
};
