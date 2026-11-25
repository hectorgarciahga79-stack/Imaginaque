import { dbExists, json, noDb, readDb } from "@/lib/db";
export const dynamic = "force-dynamic";

export function GET(req: Request) {
  if (!dbExists()) return noDb();
  const url = new URL(req.url);
  const q = (url.searchParams.get("q") || "").trim();
  const family = url.searchParams.get("family") || "";
  const limit = Math.min(1000, Number(url.searchParams.get("limit") || 300));
  const where: string[] = [];
  const args: unknown[] = [];
  if (q) {
    where.push("(p.title LIKE ? OR p.asin = ? OR p.model_label LIKE ?)");
    args.push(`%${q}%`, q.toUpperCase(), `%${q}%`);
  }
  if (family === "identified") where.push("p.model_key IS NOT NULL AND p.is_accessory=0");
  else if (family) {
    where.push("p.family = ?");
    args.push(family);
  }
  const rows = readDb()
    .prepare(
      `SELECT p.*, (SELECT COUNT(*) FROM observations o WHERE o.asin=p.asin) AS n_obs,
              (SELECT MIN(price) FROM observations o WHERE o.asin=p.asin) AS min_price,
              (SELECT MAX(price) FROM observations o WHERE o.asin=p.asin) AS max_price
       FROM products p ${where.length ? "WHERE " + where.join(" AND ") : ""}
       ORDER BY p.last_seen DESC LIMIT ?`
    )
    .all(...args, limit);
  const families = readDb().prepare("SELECT family, COUNT(*) n FROM products GROUP BY family ORDER BY n DESC").all();
  return json({ rows, families });
}
