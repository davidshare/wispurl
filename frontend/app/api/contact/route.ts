import { NextResponse } from "next/server";

/**
 * Stub contact endpoint. A real build would forward to an email/CRM provider; here
 * it just acknowledges the submission so the form's success path can be exercised.
 */
export async function POST(request: Request) {
  const data = (await request.json().catch(() => null)) as unknown;
  console.log("[contact] received submission", data);
  return NextResponse.json({ ok: true });
}
