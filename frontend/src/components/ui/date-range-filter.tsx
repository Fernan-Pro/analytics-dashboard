"use client";

import { CalendarRange, X } from "lucide-react";

import { cn } from "@/lib/utils";

interface DateRangeFilterProps {
  start: string | undefined;
  end: string | undefined;
  onChange: (start: string | undefined, end: string | undefined) => void;
  invalid?: boolean;
}

function dateInput(
  value: string | undefined,
  placeholder: string,
  onChange: (v: string) => void,
) {
  return (
    <input
      type="date"
      value={value ?? ""}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-200 [color-scheme:dark] focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
    />
  );
}

export function DateRangeFilter({
  start,
  end,
  onChange,
  invalid = false,
}: DateRangeFilterProps) {
  const hasFilter = Boolean(start || end);

  return (
    <div className="flex flex-wrap items-center gap-2">
      {dateInput(start, "Desde", (v) => onChange(v || undefined, end))}
      <span className="text-slate-600">—</span>
      {dateInput(end, "Hasta", (v) => onChange(start, v || undefined))}
      {hasFilter ? (
        <button
          type="button"
          onClick={() => onChange(undefined, undefined)}
          className="flex items-center gap-1 rounded-lg border border-slate-800 px-2.5 py-2 text-xs text-slate-400 transition-colors hover:bg-slate-800 hover:text-slate-200"
        >
          <X className="h-3.5 w-3.5" />
          Limpiar
        </button>
      ) : null}
      <span
        className={cn(
          "flex items-center gap-1.5 text-xs",
          invalid ? "text-rose-400" : "text-slate-500",
        )}
      >
        <CalendarRange className="h-3.5 w-3.5" />
        {invalid
          ? "El rango es inválido (desde > hasta)"
          : "Filtro global de fechas"}
      </span>
    </div>
  );
}