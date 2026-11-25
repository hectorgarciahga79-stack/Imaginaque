import { dbExists, json, noDb, readDb } from "@/lib/db";
export const dynamic = "force-dynamic";

// view=extreme  -> score > 85 (alert-grade), live
// view=possible -> 60..85 or not fully verified, live
// view=all      -> everything incl. expired (history)
export function GET(req: Request) {
  if (!dbExists()) return noDb();
  const url = new URL(req.url);
  const view = url.searchParams.get("view") || "extreme";
  const limit = Math.min(500, Number(url.searchParams.get("limit") || 200));
  let where = "1=1";
  if (view === "extreme") where = "o.score > 85 AND o.status IN ('verified','partial')";
  else if (view === "possible") where = "o.score >= 60 AND o.status IN ('candidate','verified','partial') AND NOT (o.score > 85 AND o.status IN ('verified','partial'))";
  const rows = readDb()
    .prepare(
      `SELECT o.*, p.title, p.model_label, p.family, p.image, p.category, p.url AS product_url
       FROM opportunities o LEFT JOIN products p ON p.asin = o.asin
       WHERE ${where} ORDER BY ${view === "all" ? "o.updated_at DESC" : "o.score DESC, o.updated_at DESC"} LIMIT ?`
    )
    .all(limit);
  return json(rows);
}
