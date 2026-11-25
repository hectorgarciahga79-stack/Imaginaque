import { dbExists, json, noDb, readDb, state } from "@/lib/db";
export const dynamic = "force-dynamic";

export function GET() {
  if (!dbExists()) return noDb();
  const db = readDb();
  const one = (sql: string, ...a: unknown[]) => (db.prepare(sql).get(...a) as { n: number }).n;
  const hb = state("heartbeat") || 0;
  const now = Date.now() / 1000;
  const blocks = state("blocks") || {};
  const activeBlocks = Object.fromEntries(Object.entries(blocks).filter(([, v]: any) => (v?.until || 0) > now));
  return json({
    now,
    status: now - hb < 120 ? state("status") || "running" : "offline",
    heartbeat: hb,
    started_at: state("started_at"),
    pid: state("pid"),
    current_task: state("current_task"),
    last_research: state("last_research"),
    delivery_location: state("delivery_location"),
    blocks: activeBlocks,
    counts: {
      products: one("SELECT COUNT(*) n FROM products"),
      products_identified: one("SELECT COUNT(*) n FROM products WHERE model_key IS NOT NULL AND is_accessory=0"),
      observations: one("SELECT COUNT(*) n FROM observations"),
      anomalies: one("SELECT COUNT(*) n FROM opportunities"),
      verified: one("SELECT COUNT(*) n FROM opportunities WHERE status='verified'"),
      live: one("SELECT COUNT(*) n FROM opportunities WHERE status IN ('verified','partial','candidate') AND score>=60"),
      extreme_alerts: one("SELECT COUNT(*) n FROM alerts"),
      unseen_alerts: one("SELECT COUNT(*) n FROM alerts WHERE seen=0"),
      categories: one("SELECT COUNT(DISTINCT store||node) n FROM categories"),
      queries: one("SELECT COUNT(*) n FROM tasks WHERE kind='search'"),
      pages_last_hour: one("SELECT COUNT(*) n FROM fetch_log WHERE ts > ?", now - 3600),
    },
  });
}
