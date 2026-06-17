import Link from "next/link";

/** Stub route — the real login form is built in a later prompt. */
export default function LoginPage() {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-md flex-col items-start justify-center gap-3 px-6">
      <h1 className="font-heading text-h2 font-bold">Log in</h1>
      <p className="text-sm text-muted-foreground">
        Coming soon. Need an account?{" "}
        <Link
          href="/signup"
          className="text-foreground underline underline-offset-4"
        >
          Get started
        </Link>
        .
      </p>
      <Link
        href="/"
        className="text-sm text-muted-foreground underline underline-offset-4"
      >
        Back home
      </Link>
    </div>
  );
}
