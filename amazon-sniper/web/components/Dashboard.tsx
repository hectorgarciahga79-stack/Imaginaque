"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import OfferCard, { type Opp } from "./OfferCard";
import {
  ago, Crosshair, dateTime, duration, Empty, eur, Panel, Pill, ScoreRing, Sparkline, STATUS_LABEL, until,
} from "./ui";

type Overview = {
  now: number; status: string; heartbeat: number; started_at: number | null; pid: number | null;
  current_task: { label: string; kind: string; started: number } | null;
  last_research: { ts: number; label: string; status: string; items: number; new: number } | null;
  delivery_location: string | null; blocks: Record<string, any>;
  counts: Record<string, number>;
};

const TABS = [
  ["extreme", "Chollos extremos"],
  ["possible", "Posibles errores"],
  ["products", "Productos investigados"],
  ["history", "Historial"],
  ["settings", "Configuración"],
  ["engine", "Estado del motor"],
] as const;
type Tab = (typeof TABS)[number][0];

async function getJSON<T>(url: string): Promise<T | null> {
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  }
}

function lsGet(k: string) { try { return localStorage.getItem(k); } catch { return null; } }
function lsSet(k: string, v: string) { try { localStorage.setItem(k, v); } catch { /* private mode */ } }

function beep() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    [0, 0.18, 0.36].forEach((t) => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = 1320; o.type = "square"; g.gain.value = 0.06;
      o.connect(g); g.connect(ctx.destination); o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.1);
    });
  } catch { /* audio blocked */ }
}

const STATUS_META: Record<string, { label: string; color: string }> = {
  running: { label: "INVESTIGANDO", color: "#38f5a0" },
  waiting: { label: "EN ESPERA", color: "#5cc8ff" },
  backoff: { label: "LIMITADO", color: "#ffb547" },
  paused: { label: "PAUSADO", color: "#ffb547" },
  stopped: { label: "DETENIDO", color: "#ff4d5e" },
  offline: { label: "SIN CONEXIÓN", color: "#ff4d5e" },
};

const SOURCE_LABEL: Record<string, string> = {
  search: "Búsqueda", product: "Fichas de producto", "listing:bestsellers": "Más vendidos",
  "listing:new-releases": "Novedades", "listing:movers-and-shakers": "Productos en alza",
};

export default function Dashboard() {
  const [tab, setTab] = useState<Tab>("extreme");
  const [ov, setOv] = useState<Overview | null>(null);
  const [dbMissing, setDbMissing] = useState(false);
  const [toast, setToast] = useState<{ title: string; body: string; url: string } | null>(null);
  const [notifPerm, setNotifPerm] = useState<string>("unknown");
  const [historyAsin, setHistoryAsin] = useState<string | null>(null);
  const lastAlert = useRef<number>(0);

  const refresh = useCallback(async () => {
    try {
      const r = await fetch("/api/overview", { cache: "no-store" });
      setDbMissing(r.status === 503);
      if (r.ok) setOv(await r.json());
    } catch { /* server restarting */ }
  }, []);

  const pollAlerts = useCallback(async () => {
    const rows = await getJSON<any[]>(`/api/alerts?since=${lastAlert.current}`);
    if (!rows?.length) return;
    const first = lastAlert.current === 0 && !lsGet("sniper.lastAlert");
    lastAlert.current = rows[rows.length - 1].id;
    lsSet("sniper.lastAlert", String(lastAlert.current));
    if (first) return; // don't replay old alerts on first visit
    for (const a of rows) {
      setToast({ title: a.title, body: a.body, url: a.url });
      beep();
      if (typeof Notification !== "undefined" && Notification.permission === "granted") {
        const n = new Notification(a.title, { body: a.body, tag: `sniper-${a.id}`, requireInteraction: true });
        n.onclick = () => window.open(a.url, "_blank");
      }
    }
  }, []);

  useEffect(() => {
    lastAlert.current = Number(lsGet("sniper.lastAlert") || 0);
    if (typeof Notification !== "undefined") setNotifPerm(Notification.permission);
    const t = lsGet("sniper.tab") as Tab | null;
    if (t && TABS.some(([k]) => k === t)) setTab(t);
    refresh(); pollAlerts();
    const a = setInterval(refresh, 5000), b = setInterval(pollAlerts, 7000);
    return () => { clearInterval(a); clearInterval(b); };
  }, [refresh, pollAlerts]);

  const choose = (t: Tab) => { setTab(t); lsSet("sniper.tab", t); };
  const st = STATUS_META[ov?.status || "offline"] || STATUS_META.offline;
  const uptime = ov?.started_at && ov.status !== "offline" && ov.status !== "stopped" ? duration(ov.now - ov.started_at) : "—";
  const blocks = Object.entries(ov?.blocks || {});
  const foreignGeo = ov?.delivery_location && !/espa|\b\d{5}\b|actualizar|update/i.test(ov.delivery_location);

  return (
    <div className="mx-auto max-w-7xl px-4 pb-16 sm:px-6">
      {/* header */}
      <header className="flex flex-wrap items-center justify-between gap-4 py-5">
        <div className="flex items-center gap-3">
          <Crosshair className="h-8 w-8 text-lock" />
          <div>
            <h1 className="font-mono text-lg font-bold tracking-[0.28em] text-ink-100">AMAZON SNIPER</h1>
            <p className="text-[11px] tracking-wider text-ink-500">Motor autónomo de detección de errores de precio · amazon.es</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {notifPerm === "default" && (
            <button onClick={async () => setNotifPerm(await Notification.requestPermission())}
              className="rounded border border-ink-600 px-3 py-1.5 text-xs text-ink-300 hover:border-lock-dim hover:text-lock">
              Activar notificaciones
            </button>
          )}
          <div className="flex items-center gap-2 rounded-full border border-ink-700 bg-ink-900 px-3 py-1.5">
            <span className="relative flex h-2.5 w-2.5">
              {ov?.status === "running" && <span className="ping-soft absolute inline-flex h-full w-full rounded-full" style={{ background: st.color }} />}
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full" style={{ background: st.color }} />
            </span>
            <span className="font-mono text-[11px] font-semibold tracking-widest" style={{ color: st.color }}>{st.label}</span>
          </div>
        </div>
      </header>

      {dbMissing && (
        <div className="mb-4 rounded-lg border border-heat-dim bg-heat/5 p-4 text-sm text-heat">
          No hay base de datos todavía. Arranca el motor: <code className="font-mono">cd engine && python -m sniper supervise</code>
        </div>
      )}

      {/* KPI strip */}
      <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-ink-700 bg-ink-700 sm:grid-cols-4 lg:grid-cols-7">
        <Kpi label="Estado del motor" value={st.label} color={st.color} sub={ov?.current_task ? `→ ${ov.current_task.label}` : ov?.heartbeat ? `latido ${ago(ov.heartbeat)}` : ""} />
        <Kpi label="Funcionando" value={uptime} sub={ov?.pid ? `pid ${ov.pid}` : ""} />
        <Kpi label="Productos investigados" value={ov?.counts.products ?? "—"} sub={ov ? `${ov.counts.products_identified} identificados` : ""} />
        <Kpi label="Anomalías" value={ov?.counts.anomalies ?? "—"} sub={ov ? `${ov.counts.live} activas` : ""} />
        <Kpi label="Ofertas verificadas" value={ov?.counts.verified ?? "—"} />
        <Kpi label="Última investigación" value={ov?.last_research ? ago(ov.last_research.ts) : "—"} sub={ov?.last_research?.label} />
        <Kpi wide label="Alertas extraordinarias" value={ov?.counts.extreme_alerts ?? "—"} color={(ov?.counts.extreme_alerts || 0) > 0 ? "#ff4d5e" : undefined}
          sub={ov ? `${ov.counts.pages_last_hour} páginas/h` : ""} />
      </div>

      {(blocks.length > 0 || foreignGeo) && (
        <div className="mt-3 space-y-2">
          {blocks.length > 0 && (
            <div className="flex flex-wrap items-start gap-2 rounded-md border border-warn-dim bg-warn/5 px-3 py-2 text-xs text-warn">
              <Pill tone="warn">Acceso limitado</Pill>
              <span className="flex-1">
                Amazon está rechazando el acceso automatizado a{" "}
                {blocks.map(([src, b]: [string, any], i) => (
                  <span key={src}>{i ? ", " : ""}<b>{SOURCE_LABEL[src] || src}</b> (reintento {until(b.until)})</span>
                ))}
                . El motor no lo elude: espera y mientras tanto investiga con las fuentes disponibles.
              </span>
            </div>
          )}
          {foreignGeo && (
            <div className="flex flex-wrap items-center gap-2 rounded-md border border-ink-600 bg-ink-850 px-3 py-2 text-xs text-ink-300">
              <Pill tone="cyan">Ubicación</Pill>
              <span>Amazon muestra precios con entrega a <b>{ov?.delivery_location}</b> (posiblemente sin IVA español). El historial sólo compara precios de la misma ubicación. Ejecuta el motor desde una conexión en España para ver precios finales.</span>
            </div>
          )}
        </div>
      )}

      {/* tabs */}
      <nav className="scrollbar-none -mx-4 mt-6 flex gap-1 overflow-x-auto border-b border-ink-700 px-4 sm:mx-0 sm:px-0">
        {TABS.map(([k, label]) => (
          <button key={k} onClick={() => choose(k)}
            className={`relative whitespace-nowrap px-3 py-2.5 text-[11px] font-semibold uppercase tracking-[0.16em] transition ${tab === k ? "text-lock" : "text-ink-400 hover:text-ink-200"}`}>
            {label}
            {k === "extreme" && (ov?.counts.unseen_alerts || 0) > 0 && <span className="ml-1.5 rounded bg-heat px-1 text-[10px] text-ink-950">{ov?.counts.unseen_alerts}</span>}
            {tab === k && <span className="absolute inset-x-2 -bottom-px h-px bg-lock" />}
          </button>
        ))}
      </nav>

      <main className="mt-5">
        {tab === "extreme" && <OppList view="extreme" onHistory={setHistoryAsin} empty={
          <Empty title="Ningún chollo extraordinario todavía">
            Aquí sólo aparece lo que supera 85 puntos y ha sido verificado. Lo normal es que esté vacío:
            el motor descarta los descuentos corrientes y sigue investigando en segundo plano.
          </Empty>} />}
        {tab === "possible" && <OppList view="possible" onHistory={setHistoryAsin} empty={
          <Empty title="Sin anomalías pendientes">Las anomalías de 60–85 puntos, o las que aún no se han podido verificar, aparecerán aquí. No generan notificación.</Empty>} />}
        {tab === "products" && <Products onHistory={setHistoryAsin} />}
        {tab === "history" && <History onHistory={setHistoryAsin} />}
        {tab === "settings" && <Settings />}
        {tab === "engine" && <EngineState ov={ov} />}
      </main>

      {historyAsin && <HistoryDrawer asin={historyAsin} onClose={() => setHistoryAsin(null)} />}

      {toast && (
        <div className="fixed inset-x-3 bottom-3 z-50 mx-auto max-w-md rounded-lg border border-heat bg-ink-900 p-4 shadow-2xl shadow-heat/20 sm:inset-x-auto sm:right-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[10px] font-bold tracking-[0.2em] text-heat">CHOLLO EXTRAORDINARIO</p>
              <p className="mt-1 text-sm font-semibold text-ink-100">{toast.title}</p>
              <p className="mt-1 whitespace-pre-line text-xs text-ink-400">{toast.body}</p>
            </div>
            <button onClick={() => { setToast(null); fetch("/api/alerts", { method: "POST" }); }} className="text-ink-500 hover:text-ink-200" aria-label="Cerrar">✕</button>
          </div>
          <a href={toast.url} target="_blank" rel="noopener noreferrer" className="mt-3 block rounded bg-heat py-2 text-center text-xs font-bold text-ink-950">ABRIR EN AMAZON</a>
        </div>
      )}
    </div>
  );
}

function Kpi({ label, value, sub, color, wide }: { label: string; value: React.ReactNode; sub?: React.ReactNode; color?: string; wide?: boolean }) {
  return (
    <div className={`min-w-0 bg-ink-900 px-4 py-3 ${wide ? "col-span-2 sm:col-span-1" : ""}`}>
      <div className="truncate text-[10px] uppercase tracking-[0.14em] text-ink-500">{label}</div>
      <div className="mt-1 truncate font-mono num text-lg font-semibold text-ink-100" style={color ? { color } : undefined}>{value}</div>
      {sub ? <div className="mt-0.5 truncate text-[11px] text-ink-500">{sub}</div> : null}
    </div>
  );
}

/* ---------------------------------------------------------------- opportunities */
function OppList({ view, empty, onHistory }: { view: string; empty: React.ReactNode; onHistory: (a: string) => void }) {
  const [rows, setRows] = useState<Opp[] | null>(null);
  useEffect(() => {
    let alive = true;
    const load = async () => { const r = await getJSON<Opp[]>(`/api/opportunities?view=${view}`); if (alive && r) setRows(r); };
    load();
    const t = setInterval(load, 8000);
    return () => { alive = false; clearInterval(t); };
  }, [view]);
  if (!rows) return <Loading />;
  if (!rows.length) return <>{empty}</>;
  return <div className="space-y-3">{rows.map((o) => <OfferCard key={o.id} o={o} onHistory={onHistory} />)}</div>;
}

/* ---------------------------------------------------------------- products */
function Products({ onHistory }: { onHistory: (a: string) => void }) {
  const [q, setQ] = useState("");
  const [family, setFamily] = useState("identified");
  const [data, setData] = useState<{ rows: any[]; families: { family: string; n: number }[] } | null>(null);
  useEffect(() => {
    const t = setTimeout(async () => setData(await getJSON(`/api/products?q=${encodeURIComponent(q)}&family=${family}`)), 250);
    return () => clearTimeout(t);
  }, [q, family]);
  return (
    <div>
      <div className="mb-3 flex flex-col gap-2 sm:flex-row">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar por nombre, modelo o ASIN…"
          className="flex-1 rounded border border-ink-700 bg-ink-900 px-3 py-2 text-sm text-ink-100 placeholder:text-ink-500 focus:border-lock-dim focus:outline-none" />
        <select value={family} onChange={(e) => setFamily(e.target.value)}
          className="rounded border border-ink-700 bg-ink-900 px-3 py-2 text-sm text-ink-200 focus:outline-none">
          <option value="identified">Sólo productos identificados</option>
          <option value="">Todos</option>
          {data?.families.map((f) => <option key={f.family} value={f.family}>{f.family} ({f.n})</option>)}
        </select>
      </div>
      {!data ? <Loading /> : !data.rows.length ? <Empty title="Sin productos" /> : (
        <div className="overflow-hidden rounded-lg border border-ink-700">
          {data.rows.map((p) => (
            <button key={p.asin} onClick={() => onHistory(p.asin)}
              className="flex w-full items-center gap-3 border-b border-ink-800 bg-ink-900 px-3 py-2.5 text-left last:border-0 hover:bg-ink-850">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded bg-white">
                {p.image ? <img src={p.image} alt="" className="max-h-full max-w-full object-contain" loading="lazy" /> : null}
              </div>
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm text-ink-100">{p.title}</div>
                <div className="flex flex-wrap gap-x-3 font-mono text-[11px] text-ink-500">
                  <span className="text-ink-300">{p.model_label || p.family}</span>
                  <span>{p.asin}</span>
                  <span>{p.n_obs} obs.</span>
                  <span>visto {ago(p.last_seen)}</span>
                  {p.is_accessory ? <span className="text-warn">accesorio/descartado</span> : null}
                </div>
              </div>
              <div className="shrink-0 text-right">
                <div className="font-mono num text-sm text-ink-100">{eur(p.last_price)}</div>
                {p.n_obs > 1 && <div className="font-mono num text-[10px] text-ink-500">{eur(p.min_price, 0)} – {eur(p.max_price, 0)}</div>}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------- history */
function History({ onHistory }: { onHistory: (a: string) => void }) {
  const [d, setD] = useState<any>(null);
  useEffect(() => { getJSON("/api/history").then(setD); }, []);
  if (!d) return <Loading />;
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Panel title="Anomalías detectadas" className="lg:col-span-2">
        {!d.opportunities.length ? <p className="text-sm text-ink-500">Todavía no se ha detectado ninguna anomalía de 60 puntos o más.</p> : (
          <div className="-mx-4 -my-4 divide-y divide-ink-800">
            {d.opportunities.map((o: any) => (
              <button key={o.id} onClick={() => onHistory(o.asin)} className="flex w-full items-center gap-3 px-4 py-2.5 text-left hover:bg-ink-850">
                <ScoreRing score={o.score} size={40} />
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm text-ink-100">{o.title}</div>
                  <div className="font-mono text-[11px] text-ink-500">{dateTime(o.created_at)} · {eur(o.price)} vs {eur(o.reference_price)} ({o.reference_source}) · −{Math.round((o.discount || 0) * 100)}%</div>
                </div>
                <Pill tone={o.status === "verified" ? "lock" : o.status === "expired" ? "neutral" : "warn"}>{STATUS_LABEL[o.status] || o.status}</Pill>
              </button>
            ))}
          </div>
        )}
      </Panel>
      <div className="space-y-4">
        <Panel title="Alertas enviadas">
          {!d.alerts.length ? <p className="text-sm text-ink-500">Ninguna. Sólo se avisa por encima de 85 puntos con verificación.</p> :
            d.alerts.map((a: any) => (
              <a key={a.id} href={a.url} target="_blank" rel="noopener noreferrer" className="mb-2 block rounded border border-heat-dim p-2 text-xs hover:bg-heat/5">
                <div className="font-semibold text-heat">{a.title}</div>
                <div className="text-ink-500">{dateTime(a.ts)}</div>
              </a>
            ))}
        </Panel>
        <Panel title="Verificaciones">
          {!d.verifications.length ? <p className="text-sm text-ink-500">Sin verificaciones todavía.</p> :
            d.verifications.slice(0, 30).map((v: any) => {
              const det = (() => { try { return JSON.parse(v.detail); } catch { return {}; } })();
              return (
                <div key={v.id} className="mb-2 border-b border-ink-800 pb-2 text-xs last:border-0">
                  <div className="flex justify-between gap-2"><span className="font-mono text-ink-300">{v.asin}</span>
                    <span className={v.ok ? "text-lock" : v.ok === 0 ? "text-heat" : "text-ink-500"}>{v.ok ? "confirmada" : v.ok === 0 ? "expirada" : "sin acceso"}</span></div>
                  <div className="text-ink-500">{dateTime(v.ts)} · {v.method} · {v.price ? eur(v.price) : ""} {det.reason || (det.problems || []).join(", ")}</div>
                </div>
              );
            })}
        </Panel>
      </div>
    </div>
  );
}

function HistoryDrawer({ asin, onClose }: { asin: string; onClose: () => void }) {
  const [d, setD] = useState<any>(null);
  useEffect(() => { getJSON(`/api/history?asin=${asin}`).then(setD); }, [asin]);
  const obs = (d?.observations || []).filter((o: any) => o.price != null);
  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/60" onClick={onClose}>
      <aside className="h-full w-full max-w-xl overflow-y-auto border-l border-ink-700 bg-ink-950 p-5" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="font-mono text-[11px] text-ink-500">ASIN {asin}</p>
            <h3 className="text-sm font-medium text-ink-100">{d?.product?.title || "…"}</h3>
            <p className="mt-1 font-mono text-[11px] text-ink-400">{d?.product?.model_label || d?.product?.family}</p>
          </div>
          <button onClick={onClose} className="text-ink-500 hover:text-ink-100" aria-label="Cerrar">✕</button>
        </div>
        {d?.product?.image && <div className="mb-4 flex h-40 items-center justify-center rounded bg-white"><img src={d.product.image} alt="" className="max-h-full object-contain" /></div>}
        <a href={`https://www.amazon.es/dp/${asin}`} target="_blank" rel="noopener noreferrer" className="mb-4 block rounded border border-lock-dim py-2 text-center text-xs font-semibold text-lock hover:bg-lock/10">Abrir en Amazon</a>
        <Panel title={`Historial propio de precios · ${obs.length} observaciones`}>
          <Sparkline points={obs.map((o: any) => ({ ts: o.ts, price: o.price }))} />
          <div className="mt-3 max-h-80 overflow-y-auto">
            <table className="w-full text-left text-[11px]">
              <thead className="text-ink-500"><tr><th className="py-1">Fecha</th><th>Precio</th><th>Fuente</th><th>Detalle</th></tr></thead>
              <tbody className="font-mono text-ink-300">
                {[...obs].reverse().map((o: any) => (
                  <tr key={o.id} className="border-t border-ink-800">
                    <td className="py-1 pr-2">{dateTime(o.ts)}</td>
                    <td className="pr-2 text-ink-100">{eur(o.price)}</td>
                    <td className="pr-2">{o.source}</td>
                    <td className="text-ink-500">{[o.offers_from ? `${o.offers_count || "?"} ofertas desde` : "", o.rank ? `#${o.rank}` : "", o.seller || "", o.geo || ""].filter(Boolean).join(" · ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
        {d?.opportunities?.length ? (
          <Panel title="Anomalías de este producto" className="mt-4">
            {d.opportunities.map((o: any) => (
              <div key={o.id} className="mb-2 flex items-center justify-between text-xs">
                <span className="font-mono text-ink-300">{dateTime(o.created_at)} · {eur(o.price)} · {Math.round(o.score)} pts</span>
                <Pill>{STATUS_LABEL[o.status] || o.status}</Pill>
              </div>
            ))}
          </Panel>
        ) : null}
      </aside>
    </div>
  );
}

/* ---------------------------------------------------------------- settings */
const SETTING_GROUPS: { title: string; keys: [string, string, string?][] }[] = [
  { title: "Alertas", keys: [
    ["notify_threshold", "Notificar sólo por encima de (mín. 85)", "number"],
    ["store_threshold", "Guardar oportunidades desde", "number"],
    ["allow_partial_verification_alerts", "Permitir alertas con verificación parcial (sin ficha de producto)", "bool"],
    ["partial_min_score", "Score mínimo para alertas con verificación parcial", "number"],
    ["desktop_notifications", "Notificaciones del sistema operativo", "bool"],
  ]},
  { title: "Ritmo de investigación", keys: [
    ["paused", "Pausar el motor", "bool"],
    ["min_delay_s", "Segundos mínimos entre peticiones", "number"],
    ["jitter_s", "Margen aleatorio (s)", "number"],
    ["max_requests_per_hour", "Máximo de páginas por hora", "number"],
    ["listing_interval_min", "Revisión de listados prioritarios (min)", "number"],
    ["search_cooldown_min", "No repetir una búsqueda antes de (min)", "number"],
    ["reverify_interval_min", "Recomprobar ofertas vivas cada (min)", "number"],
    ["listing_pages", "Páginas por lista de más vendidos", "number"],
    ["max_category_depth", "Profundidad de exploración de categorías", "number"],
  ]},
  { title: "Fuentes", keys: [
    ["enable_search", "Usar búsquedas de Amazon", "bool"],
    ["enable_product_pages", "Verificar en la ficha de producto", "bool"],
    ["fetch_backend", "Navegador (http | playwright)", "text"],
    ["respect_robots", "Respetar robots.txt", "bool"],
  ]},
  { title: "Historial y referencias", keys: [
    ["min_history_obs", "Observaciones propias mínimas", "number"],
    ["min_history_span_h", "Horas mínimas de historial", "number"],
    ["min_peers", "Productos equivalentes mínimos", "number"],
  ]},
];

function Settings() {
  const [s, setS] = useState<Record<string, any> | null>(null);
  const [saved, setSaved] = useState<string>("");
  useEffect(() => { getJSON<Record<string, any>>("/api/settings").then(setS); }, []);
  if (!s) return <Loading />;
  const save = async () => {
    const r = await fetch("/api/settings", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(s) });
    setSaved(r.ok ? "Guardado. El motor aplica los cambios en su siguiente ciclo." : "Error al guardar");
    setTimeout(() => setSaved(""), 5000);
  };
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {SETTING_GROUPS.map((g) => (
        <Panel key={g.title} title={g.title}>
          <div className="space-y-3">
            {g.keys.map(([k, label, type]) => (
              <label key={k} className="flex items-center justify-between gap-4 text-sm">
                <span className="text-ink-300">{label}</span>
                {type === "bool" ? (
                  <input type="checkbox" checked={!!s[k]} onChange={(e) => setS({ ...s, [k]: e.target.checked })} className="h-4 w-4 accent-[#38f5a0]" />
                ) : (
                  <input type={type === "number" ? "number" : "text"} value={s[k] ?? ""} step="any"
                    onChange={(e) => setS({ ...s, [k]: type === "number" ? Number(e.target.value) : e.target.value })}
                    className="w-28 rounded border border-ink-700 bg-ink-950 px-2 py-1 text-right font-mono text-sm text-ink-100 focus:border-lock-dim focus:outline-none" />
                )}
              </label>
            ))}
          </div>
        </Panel>
      ))}
      <div className="flex items-center gap-3 md:col-span-2">
        <button onClick={save} className="rounded bg-lock px-5 py-2 text-xs font-bold tracking-wider text-ink-950 hover:brightness-110">GUARDAR CONFIGURACIÓN</button>
        <span className="text-xs text-ink-400">{saved}</span>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------- engine */
function EngineState({ ov }: { ov: Overview | null }) {
  const [d, setD] = useState<any>(null);
  useEffect(() => {
    const load = async () => setD(await getJSON("/api/engine"));
    load();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, []);
  if (!d) return <Loading />;
  const now = Date.now() / 1000;
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Panel title="Fuentes de Amazon (24 h)" className="lg:col-span-2">
        <table className="w-full text-left text-xs">
          <thead className="text-ink-500"><tr><th className="py-1">Tipo</th><th>Resultado</th><th>Detalle</th><th className="text-right">Peticiones</th><th className="text-right">ms</th></tr></thead>
          <tbody className="font-mono">
            {d.fetch_summary.map((r: any, i: number) => (
              <tr key={i} className="border-t border-ink-800">
                <td className="py-1.5 text-ink-200">{r.kind}</td>
                <td className={r.outcome === "ok" ? "text-lock" : r.outcome === "blocked" ? "text-warn" : "text-heat"}>{r.outcome}</td>
                <td className="text-ink-500">{r.detail || ""}</td>
                <td className="text-right text-ink-200">{r.n}</td>
                <td className="text-right text-ink-500">{r.avg_ms}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {Object.keys(d.blocks).length > 0 && (
          <div className="mt-4 space-y-1 text-xs">
            {Object.entries(d.blocks).map(([k, b]: [string, any]) => (
              <div key={k} className="text-ink-400">
                <span className="text-warn">{SOURCE_LABEL[k] || k}</span>: nivel {b.level}, {b.until > now ? `reintento ${until(b.until)}` : "reintento permitido"} · {b.reason}
              </div>
            ))}
          </div>
        )}
      </Panel>
      <Panel title="Motor">
        <dl className="space-y-1.5 text-xs">
          {[
            ["Estado", ov?.status], ["PID", ov?.pid], ["Latido", ago(ov?.heartbeat)], ["Inicio", dateTime(ov?.started_at)],
            ["Tarea actual", ov?.current_task?.label || "—"], ["Entrega", ov?.delivery_location || "—"],
            ["Categorías", ov?.counts.categories], ["Consultas de búsqueda", ov?.counts.queries], ["Observaciones de precio", ov?.counts.observations],
          ].map(([k, v]) => (
            <div key={String(k)} className="flex justify-between gap-3"><dt className="text-ink-500">{k}</dt><dd className="truncate font-mono text-ink-200">{String(v ?? "—")}</dd></div>
          ))}
        </dl>
        <div className="mt-4 space-y-1 text-xs">
          {d.task_summary.map((t: any) => (
            <div key={t.kind} className="flex justify-between font-mono text-ink-400"><span>{t.kind}</span><span>{t.n} tareas · {t.runs || 0} ejecuciones · {t.due} pendientes</span></div>
          ))}
        </div>
      </Panel>

      <Panel title="Cola de investigación" className="lg:col-span-2">
        <div className="-mx-4 -my-4 max-h-[480px] overflow-y-auto">
          <table className="w-full text-left text-[11px]">
            <thead className="sticky top-0 bg-ink-900 text-ink-500"><tr><th className="px-4 py-1.5">Tarea</th><th>Prio</th><th>Último</th><th>Resultado</th><th>Próxima</th></tr></thead>
            <tbody className="font-mono">
              {d.tasks.map((t: any) => (
                <tr key={t.id} className="border-t border-ink-800">
                  <td className="max-w-[260px] truncate px-4 py-1.5 text-ink-200"><span className="mr-1.5 text-ink-500">{t.kind}</span>{t.label}</td>
                  <td className="text-ink-400">{t.priority}</td>
                  <td className="text-ink-500">{t.last_run_at ? ago(t.last_run_at) : "—"}</td>
                  <td className={String(t.last_status || "").startsWith("ok") ? "text-lock" : t.last_status ? "text-warn" : "text-ink-600"}>
                    {t.last_status ? `${String(t.last_status).split(":")[0]} · ${t.items_last}/${t.new_items_last} nuevos` : "pendiente"}
                  </td>
                  <td className="text-ink-500">{until(t.next_run_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel title="Registro">
        <div className="-mx-4 -my-4 max-h-[480px] overflow-y-auto px-4 py-3">
          {d.events.map((e: any) => (
            <div key={e.id} className="mb-1.5 text-[11px] leading-snug">
              <span className="font-mono text-ink-600">{new Date(e.ts * 1000).toLocaleTimeString("es-ES")} </span>
              <span className={e.level === "alert" ? "text-heat" : e.level === "warn" ? "text-warn" : e.level === "error" ? "text-heat" : "text-ink-300"}>{e.message}</span>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title={`Categorías descubiertas (${d.categories.length})`} className="lg:col-span-3">
        <div className="flex flex-wrap gap-1.5">
          {d.categories.map((c: any) => (
            <span key={c.store + c.node} className="rounded border border-ink-700 px-2 py-0.5 text-[11px] text-ink-300">
              <span className="font-mono text-ink-500">P{c.priority}</span> {c.name}
            </span>
          ))}
        </div>
      </Panel>
    </div>
  );
}

function Loading() {
  return (
    <div className="relative h-1 overflow-hidden rounded bg-ink-800">
      <div className="scanline absolute inset-y-0 w-1/4 bg-lock/60" />
    </div>
  );
}
