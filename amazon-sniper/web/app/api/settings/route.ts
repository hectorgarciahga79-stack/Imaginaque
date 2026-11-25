import { dbExists, json, noDb, readDb, writeDb } from "@/lib/db";
export const dynamic = "force-dynamic";

export function GET() {
  if (!dbExists()) return noDb();
  const rows = readDb().prepare("SELECT key, value FROM settings ORDER BY key").all() as { key: string; value: string }[];
  return json(Object.fromEntries(rows.map((r) => [r.key, JSON.parse(r.value)])));
}

export async function POST(req: Request) {
  if (!dbExists()) return noDb();
  const body = (await req.json()) as Record<string, unknown>;
  const known = new Set((readDb().prepare("SELECT key FROM settings").all() as { key: string }[]).map((r) => r.key));
  const db = writeDb();
  const upd = db.prepare("UPDATE settings SET value=? WHERE key=?");
  const changed: string[] = [];
  for (const [k, v] of Object.entries(body)) {
    if (!known.has(k)) continue;
    if (k === "notify_threshold" && Number(v) < 85) continue; // owner's rule: never notify at 85 or below
    upd.run(JSON.stringify(v), k);
    changed.push(k);
  }
  db.prepare("INSERT INTO events(ts,level,message) VALUES(?,?,?)").run(Date.now() / 1000, "info", `Configuración cambiada desde la web: ${changed.join(", ")}`);
  return json({ ok: true, changed });
}
