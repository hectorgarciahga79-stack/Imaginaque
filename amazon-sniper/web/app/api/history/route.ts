import { dbExists, json, noDb, readDb } from "@/lib/db";
export const dynamic = "force-dynamic";

export function GET(req: Request) {
  if (!dbExists()) return noDb();
  const asin = new URL(req.url).searchParams.get("asin");
  const db = readDb();
  if (!asin) {
    return json({
      opportunities: db
        .prepare(
          `SELECT o.id,o.asin,o.created_at,o.updated_at,o.price,o.reference_price,o.reference_source,o.discount,o.score,o.tier,o.status,o.confidence,o.notified,p.title,p.model_label
           FROM opportunities o LEFT JOIN products p USING(asin) ORDER BY o.updated_at DESC LIMIT 300`
        )
        .all(),
      verifications: db
        .prepare(`SELECT v.*, o.asin FROM verifications v JOIN opportunities o ON o.id=v.opportunity_id ORDER BY v.id DESC LIMIT 100`)
        .all(),
      alerts: db.prepare("SELECT * FROM alerts ORDER BY id DESC LIMIT 100").all(),
    });
  }
  return json({
    product: db.prepare("SELECT * FROM products WHERE asin=?").get(asin),
    observations: db.prepare("SELECT * FROM observations WHERE asin=? ORDER BY ts ASC").all(asin),
    opportunities: db.prepare("SELECT * FROM opportunities WHERE asin=? ORDER BY id DESC").all(asin),
  });
}
