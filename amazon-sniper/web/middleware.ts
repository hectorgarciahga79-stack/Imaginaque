import { NextResponse, type NextRequest } from "next/server";

// Private panel. By default the server only listens on 127.0.0.1.
// If you expose it on your network, set SNIPER_UI_PASSWORD to require HTTP Basic auth.
export function middleware(req: NextRequest) {
  const pass = process.env.SNIPER_UI_PASSWORD;
  if (!pass) return NextResponse.next();
  const h = req.headers.get("authorization") || "";
  const [scheme, enc] = h.split(" ");
  if (scheme === "Basic" && enc) {
    const [, p] = atob(enc).split(":");
    if (p === pass) return NextResponse.next();
  }
  return new NextResponse("Autenticación requerida", { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Amazon Sniper"' } });
}
export const config = { matcher: "/:path*" };
