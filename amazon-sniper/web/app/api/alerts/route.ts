import { dbExists, json, noDb, readDb, writeDb } from "@/lib/db";
export const dynamic = "force-dynamic";

export function GET(req: Request) {
  if (!dbExists()) return noDb();
  const since = Number(new URL(req.url).searchParams.get("since") || 0);
  return json(readDb().prepare("SELECT * FROM alerts WHERE id > ? ORDER BY id ASC LIMIT 50").all(since));
}

export async function POST() {
  if (!dbExists()) return noDb();
  writeDb().prepare("UPDATE alerts SET seen=1 WHERE seen=0").run();
  return json({ ok: true });
}
