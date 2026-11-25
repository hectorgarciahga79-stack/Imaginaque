import { dbExists, json, noDb, readDb, state } from "@/lib/db";
export const dynamic = "force-dynamic";

export function GET() {
  if (!dbExists()) return noDb();
  const db = readDb();
  const now = Date.now() / 1000;
  return json({
    blocks: state("blocks") || {},
    tasks: db
      .prepare(
        `SELECT id,kind,label,priority,interval_s,next_run_at,last_run_at,last_status,runs,items_last,new_items_last,new_items_total,enabled
         FROM tasks ORDER BY (last_run_at IS NULL), next_run_at ASC LIMIT 400`
      )
      .all(),
    task_summary: db.prepare("SELECT kind, COUNT(*) n, SUM(runs) runs, SUM(CASE WHEN next_run_at<=? THEN 1 ELSE 0 END) due FROM tasks GROUP BY kind").all(now),
    fetch_summary: db
      .prepare("SELECT kind, outcome, detail, COUNT(*) n, ROUND(AVG(ms)) avg_ms FROM fetch_log WHERE ts > ? GROUP BY kind, outcome, detail ORDER BY n DESC")
      .all(now - 86400),
    fetch_recent: db.prepare("SELECT ts,kind,url,status,outcome,bytes,ms,detail FROM fetch_log ORDER BY id DESC LIMIT 40").all(),
    events: db.prepare("SELECT * FROM events ORDER BY id DESC LIMIT 120").all(),
    categories: db.prepare("SELECT store, node, name, depth, priority FROM categories WHERE list_type='bestsellers' ORDER BY priority, depth, name").all(),
  });
}
