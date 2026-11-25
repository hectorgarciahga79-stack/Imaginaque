"use client";
import React from "react";

export const eur = (v?: number | null, d = 2) =>
  v == null ? "—" : v.toLocaleString("es-ES", { minimumFractionDigits: d, maximumFractionDigits: d }) + " €";

export const pct = (v?: number | null) => (v == null ? "—" : `${Math.round(v * 100)}%`);

export function ago(ts?: number | null) {
  if (!ts) return "—";
  const s = Math.max(0, Date.now() / 1000 - ts);
  if (s < 60) return `hace ${Math.round(s)} s`;
  if (s < 3600) return `hace ${Math.round(s / 60)} min`;
  if (s < 86400) return `hace ${(s / 3600).toFixed(1)} h`;
  return `hace ${(s / 86400).toFixed(1)} d`;
}

export function until(ts?: number | null) {
  if (!ts) return "—";
  const s = ts - Date.now() / 1000;
  if (s <= 0) return "ahora";
  if (s < 3600) return `en ${Math.ceil(s / 60)} min`;
  return `en ${(s / 3600).toFixed(1)} h`;
}

export function duration(sec: number) {
  const d = Math.floor(sec / 86400), h = Math.floor((sec % 86400) / 3600), m = Math.floor((sec % 3600) / 60);
  return d ? `${d}d ${h}h ${m}m` : h ? `${h}h ${m}m` : `${m}m ${Math.floor(sec % 60)}s`;
}

export const dateTime = (ts?: number | null) =>
  ts ? new Date(ts * 1000).toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "—";

export function tierColor(score: number) {
  if (score >= 90) return "#ff4d5e";
  if (score >= 75) return "#ffb547";
  if (score >= 60) return "#5cc8ff";
  return "#46515d";
}

export const TIER_LABEL: Record<string, string> = {
  extreme: "POSIBLE ERROR EXTREMO",
  exceptional: "OFERTA EXCEPCIONAL",
  interesting: "INTERESANTE",
  discard: "DESCARTAR",
};

export const STATUS_LABEL: Record<string, string> = {
  verified: "VERIFICADA",
  partial: "VERIFICACIÓN PARCIAL",
  candidate: "PENDIENTE",
  expired: "EXPIRADA",
  rejected: "RECHAZADA",
};

export const FULFILL_LABEL: Record<string, string> = {
  amazon: "Vendido y enviado por Amazon",
  fba: "Vendido por tercero · enviado por Amazon",
  third_party: "Vendido y enviado por tercero",
  unknown: "Vendedor sin confirmar",
};

export function ScoreRing({ score, size = 64 }: { score: number; size?: number }) {
  const r = size / 2 - 5;
  const c = 2 * Math.PI * r;
  const col = tierColor(score);
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }} title="SNIPER SCORE">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#20262d" strokeWidth="4" fill="none" />
        <circle cx={size / 2} cy={size / 2} r={r} stroke={col} strokeWidth="4" fill="none" strokeLinecap="round"
          strokeDasharray={`${(c * Math.min(100, score)) / 100} ${c}`} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center leading-none">
        <span className="font-mono num font-semibold" style={{ color: col, fontSize: size * 0.3 }}>{Math.round(score)}</span>
        <span className="text-[8px] tracking-[0.18em] text-ink-400 mt-0.5">SCORE</span>
      </div>
    </div>
  );
}

export function Pill({ children, tone = "neutral", className = "" }: { children: React.ReactNode; tone?: "neutral" | "lock" | "heat" | "warn" | "cyan"; className?: string }) {
  const tones = {
    neutral: "border-ink-600 text-ink-300 bg-ink-850",
    lock: "border-lock-dim text-lock bg-lock/5",
    heat: "border-heat-dim text-heat bg-heat/5",
    warn: "border-warn-dim text-warn bg-warn/5",
    cyan: "border-cyan/30 text-cyan bg-cyan/5",
  };
  return <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-medium tracking-wider uppercase whitespace-nowrap ${tones[tone]} ${className}`}>{children}</span>;
}

export function Panel({ title, right, children, className = "" }: { title?: React.ReactNode; right?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={`rounded-lg border border-ink-700 bg-ink-900/80 backdrop-blur ${className}`}>
      {title && (
        <header className="flex items-center justify-between gap-3 border-b border-ink-700 px-4 py-2.5">
          <h3 className="text-[11px] font-semibold tracking-[0.2em] text-ink-300 uppercase">{title}</h3>
          {right}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}

export function Empty({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-dashed border-ink-700 px-6 py-14 text-center">
      <Crosshair className="mx-auto mb-4 h-10 w-10 text-ink-600" />
      <p className="text-sm font-medium text-ink-200">{title}</p>
      {children && <div className="mx-auto mt-2 max-w-lg text-sm text-ink-400">{children}</div>}
    </div>
  );
}

export function Crosshair({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className={className}>
      <circle cx="12" cy="12" r="7.5" />
      <circle cx="12" cy="12" r="1.6" fill="currentColor" />
      <path d="M12 1.5v5M12 17.5v5M1.5 12h5M17.5 12h5" strokeLinecap="round" />
    </svg>
  );
}

export function Sparkline({ points, height = 56 }: { points: { ts: number; price: number }[]; height?: number }) {
  if (points.length < 2) return <div className="text-xs text-ink-500">Historial insuficiente ({points.length} observación{points.length === 1 ? "" : "es"}).</div>;
  const w = 600;
  const xs = points.map((p) => p.ts), ys = points.map((p) => p.price);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const sx = (x: number) => ((x - x0) / (x1 - x0 || 1)) * (w - 8) + 4;
  const sy = (y: number) => height - 6 - ((y - y0) / (y1 - y0 || 1)) * (height - 12);
  const d = points.map((p, i) => `${i ? "L" : "M"}${sx(p.ts).toFixed(1)},${sy(p.price).toFixed(1)}`).join(" ");
  const last = points[points.length - 1];
  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" preserveAspectRatio="none" style={{ height }}>
      <path d={d} fill="none" stroke="#38f5a0" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
      <circle cx={sx(last.ts)} cy={sy(last.price)} r="3" fill="#38f5a0" />
    </svg>
  );
}
