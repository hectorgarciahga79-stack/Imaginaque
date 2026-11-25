import Database from "better-sqlite3";
import path from "node:path";
import fs from "node:fs";

// Same database the Python engine writes. Override with SNIPER_DB.
const DB_PATH = process.env.SNIPER_DB || path.resolve(process.cwd(), "..", "data", "sniper.db");

let ro: Database.Database | null = null;
let rw: Database.Database | null = null;

export function dbExists() {
  return fs.existsSync(DB_PATH);
}

export function readDb() {
  if (!ro) {
    ro = new Database(DB_PATH, { readonly: true, fileMustExist: true });
    ro.pragma("busy_timeout = 5000");
  }
  return ro;
}

// Only used for settings and marking alerts as seen.
export function writeDb() {
  if (!rw) {
    rw = new Database(DB_PATH, { fileMustExist: true });
    rw.pragma("busy_timeout = 10000");
  }
  return rw;
}

export function state(key: string): any {
  const row = readDb().prepare("SELECT value FROM engine_state WHERE key=?").get(key) as { value: string } | undefined;
  if (!row) return null;
  try {
    return JSON.parse(row.value);
  } catch {
    return row.value;
  }
}

export function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
}

export function noDb() {
  return json({ error: "La base de datos aún no existe. Arranca el motor: python -m sniper supervise", db: DB_PATH }, 503);
}
