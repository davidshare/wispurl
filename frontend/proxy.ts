import { NextResponse, type NextRequest } from "next/server";
import { REFRESH_COOKIE } from "@/lib/auth/constants";

/**
 * Edge guard for the cookie path (Next 16 "proxy" convention, formerly middleware).
 * If there's no refresh cookie, the visitor has no resumable session, so the
 * authenticated routes are redirected to /login (preserving the intended path in
 * `next`) before the page loads. When the cookie is present, the request proceeds
 * and the in-memory client guard does a silent refresh.
 */
export default function proxy(request: NextRequest) {
  if (request.cookies.has(REFRESH_COOKIE)) {
    return NextResponse.next();
  }
  const url = request.nextUrl.clone();
  url.pathname = "/login";
  url.search = `?next=${encodeURIComponent(request.nextUrl.pathname)}`;
  return NextResponse.redirect(url);
}

// The entire authenticated app lives under /dashboard/*.
export const config = {
  matcher: ["/dashboard", "/dashboard/:path*"],
};
