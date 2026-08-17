import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp } from "lucide-react";

import { cn, formatNumber } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  /** Variación porcentual respecto al periodo anterior. */
  delta?: number;
  hint?: string;
  accent?: string;
}

export function MetricCard({
  title,
  value,
  icon: Icon,
  delta,
  hint,
  accent = "bg-indigo-500/10 text-indigo-400",
}: MetricCardProps) {
  const deltaUp = (delta ?? 0) >= 0;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="flex items-center justify-between gap-3">
        <p className="truncate text-xs font-medium uppercase tracking-wide text-slate-400">
          {title}
        </p>
        <span
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl",
            accent,
          )}
        >
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <p className="mt-3 text-2xl font-semibold tabular-nums text-slate-50">
        {typeof value === "number" ? formatNumber(value) : value}
      </p>
      <div className="mt-2 flex items-center gap-2 text-xs">
        {delta !== undefined ? (
          <span
            className={cn(
              "inline-flex items-center gap-1 font-medium",
              deltaUp ? "text-emerald-400" : "text-rose-400",
            )}
          >
            {deltaUp ? (
              <TrendingUp className="h-3.5 w-3.5" />
            ) : (
              <TrendingDown className="h-3.5 w-3.5" />
            )}
            {Math.abs(delta)}%
          </span>
        ) : null}
        {hint ? <span className="truncate text-slate-500">{hint}</span> : null}
      </div>
    </div>
  );
}