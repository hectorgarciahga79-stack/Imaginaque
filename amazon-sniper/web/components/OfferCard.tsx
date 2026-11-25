"use client";
import { ago, dateTime, eur, FULFILL_LABEL, Pill, ScoreRing, STATUS_LABEL, TIER_LABEL, tierColor } from "./ui";

export type Opp = {
  id: number; asin: string; created_at: number; updated_at: number; price: number; reference_price: number | null;
  reference_source: string | null; discount: number | null; saving: number | null; score: number; tier: string;
  confidence: string; components: string; flags: string; status: string; verified_at: number | null; verification: string | null;
  notified: number; seller: string | null; fulfillment: string | null; condition: string | null; availability: string | null;
  title: string | null; model_label: string | null; family: string | null; image: string | null; category: string | null;
};

const REF_LABEL: Record<string, string> = {
  history: "historial propio",
  peers: "productos equivalentes",
  prior: "estimación de catálogo",
};
const COND: Record<string, string> = { new: "Nuevo", used: "Usado", refurbished: "Reacondicionado", unknown: "Sin confirmar" };
const AVAIL: Record<string, string> = { in_stock: "En stock", limited: "Pocas unidades", out_of_stock: "Sin stock", unknown: "Stock sin confirmar" };

function parse<T>(s: string | null, d: T): T {
  try { return s ? (JSON.parse(s) as T) : d; } catch { return d; }
}

export default function OfferCard({ o, base = "https://www.amazon.es", onHistory }: { o: Opp; base?: string; onHistory?: (asin: string) => void }) {
  const warnings = parse<string[]>(o.flags, []);
  const ver = parse<Record<string, any>>(o.verification, {});
  const col = tierColor(o.score);
  const url = `${base}/dp/${o.asin}`;
  const confTone = o.confidence === "ALTA" ? "lock" : o.confidence === "MEDIA" ? "warn" : "neutral";
  return (
    <article className="group relative overflow-hidden rounded-lg border border-ink-700 bg-ink-900/90 transition hover:border-ink-500">
      <div className="absolute inset-y-0 left-0 w-[3px]" style={{ background: col }} />
      <div className="flex flex-col gap-4 p-4 pl-5 sm:flex-row">
        <a href={url} target="_blank" rel="noopener noreferrer"
          className="flex h-32 w-full shrink-0 items-center justify-center overflow-hidden rounded-md bg-white sm:h-28 sm:w-28">
          {o.image ? <img src={o.image} alt="" className="max-h-full max-w-full object-contain" loading="lazy" /> : <span className="text-xs text-ink-500">sin imagen</span>}
        </a>

        <div className="min-w-0 flex-1">
          <div className="mb-1.5 flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-semibold tracking-[0.18em]" style={{ color: col }}>{TIER_LABEL[o.tier] || o.tier}</span>
            <Pill tone={o.status === "verified" ? "lock" : o.status === "partial" ? "warn" : o.status === "expired" ? "neutral" : "cyan"}>{STATUS_LABEL[o.status] || o.status}</Pill>
            <Pill tone={confTone as any}>Confianza {o.confidence}</Pill>
            {o.notified ? <Pill tone="heat">Notificada</Pill> : null}
          </div>
          <h4 className="line-clamp-2 text-sm font-medium leading-snug text-ink-100">
            <a href={url} target="_blank" rel="noopener noreferrer" className="hover:text-lock">{o.title || o.asin}</a>
          </h4>
          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-0.5 font-mono text-[11px] text-ink-400">
            <span className="text-ink-200">{o.model_label || "modelo sin identificar"}</span>
            <span>ASIN {o.asin}</span>
            {o.category && <span className="truncate">{o.category}</span>}
          </div>

          <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-4">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-ink-500">Precio actual</div>
              <div className="font-mono num text-lg font-semibold text-ink-100">{eur(o.price)}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-wider text-ink-500">Habitual estimado</div>
              <div className="font-mono num text-sm text-ink-300 line-through decoration-ink-500">{eur(o.reference_price)}</div>
              <div className="text-[10px] text-ink-500">{REF_LABEL[o.reference_source || ""] || "—"}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-wider text-ink-500">Diferencia</div>
              <div className="font-mono num text-sm font-semibold text-lock">−{eur(o.saving, 0)}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-wider text-ink-500">Descuento</div>
              <div className="font-mono num text-sm font-semibold" style={{ color: col }}>−{Math.round((o.discount || 0) * 100)}%</div>
            </div>
          </div>

          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-ink-400">
            <span>{FULFILL_LABEL[o.fulfillment || "unknown"]}{o.seller ? ` · ${o.seller}` : ""}</span>
            <span>{COND[o.condition || "unknown"]}</span>
            <span>{AVAIL[o.availability || "unknown"]}</span>
            <span title={dateTime(o.created_at)}>Detectada {dateTime(o.created_at)}</span>
            {o.verified_at && <span>Comprobada {ago(o.verified_at)}{ver.method ? ` (${ver.method === "product_page" ? "ficha" : ver.method === "listing_recheck" ? "listado" : ver.method})` : ""}</span>}
          </div>
          {warnings.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {warnings.map((w) => <Pill key={w} tone="warn">{w.replace(/_/g, " ")}</Pill>)}
            </div>
          )}
          {ver.problems?.length ? <p className="mt-2 text-[11px] text-heat">Verificación: {ver.problems.join(" · ")}</p> : null}
          {ver.reason && !ver.problems?.length ? <p className="mt-2 text-[11px] text-ink-400">Verificación: {ver.reason}</p> : null}
        </div>

        <div className="flex shrink-0 flex-row items-center justify-between gap-3 sm:flex-col sm:items-end">
          <ScoreRing score={o.score} />
          <div className="flex gap-2 sm:flex-col">
            <a href={url} target="_blank" rel="noopener noreferrer"
              className="rounded border border-lock-dim bg-lock/10 px-3 py-1.5 text-center text-xs font-semibold text-lock hover:bg-lock/20">
              Abrir en Amazon
            </a>
            {onHistory && (
              <button onClick={() => onHistory(o.asin)} className="rounded border border-ink-600 px-3 py-1.5 text-xs text-ink-300 hover:border-ink-400 hover:text-ink-100">
                Historial
              </button>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
