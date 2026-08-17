"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, MessageSquare, RefreshCw, Rocket, Star } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useMemo, useState } from "react";

import { AreaChart } from "@/components/charts/area-chart";
import { BarChart } from "@/components/charts/bar-chart";
import { chartCardGrid } from "@/components/charts/chart-card";
import { ChartCard } from "@/components/charts/chart-card";
import { LineChart } from "@/components/charts/line-chart";
import { SourceTable } from "@/components/tables/source-table";
import { DateRangeFilter } from "@/components/ui/date-range-filter";
import { MetricCard } from "@/components/ui/metric-card";
import { SectionCard } from "@/components/ui/section-card";
import { api, queryKeys, type QueryParams } from "@/lib/api";
import {
  groupByLanguage,
  METRIC_AVG_TYPES,
  METRIC_TOTAL_TYPES,
  metricCards,
  pivotHistory,
  sourceStatuses,
} from "@/lib/metrics";
import { cn } from "@/lib/utils";
import type { Category, MetricsSummary } from "@/types/api";

function formatMetricValue(value: number): string {
  return Number.isInteger(value) ? value.toLocaleString("en-US") : value.toFixed(1);
}

function LoadingCards() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={`skeleton-card-${i}`}
          className="h-[118px] animate-pulse rounded-2xl border border-slate-800 bg-slate-900/60"
        />
      ))}
    </div>
  );
}

function sourceTabs(summary: MetricsSummary | undefined): {
  id: Category;
  label: string;
  icon: LucideIcon;
  count: number;
}[] {
  return [
    { id: "github", label: "GitHub", icon: Star, count: summary?.total_github_trends ?? 0 },
    { id: "hackernews", label: "Hacker News", icon: MessageSquare, count: summary?.total_hn_stories ?? 0 },
    { id: "producthunt", label: "Product Hunt", icon: Rocket, count: summary?.total_ph_launches ?? 0 },
  ];
}

export default function Home() {
  const [filters, setFilters] = useState<{
    start: string | undefined;
    end: string | undefined;
  }>({ start: undefined, end: undefined });
  const [category, setCategory] = useState<Category>("github");

  const invalidRange = Boolean(
    filters.start && filters.end && filters.start > filters.end,
  );

  const dateParams = useMemo<QueryParams>(
    () => ({ start_date: filters.start, end_date: filters.end }),
    [filters.start, filters.end],
  );

  const snapshotQuery = useQuery({
    queryKey: queryKeys.metricsSnapshot(dateParams),
    queryFn: () => api.metricsSnapshot(dateParams),
    enabled: !invalidRange,
  });

  const trendsQuery = useQuery({
    queryKey: queryKeys.githubTrends({ ...dateParams, page_size: 100 }),
    queryFn: () => api.githubTrends({ ...dateParams, page_size: 100 }),
    enabled: !invalidRange,
  });

  const summary = snapshotQuery.data?.summary;
  const cards = metricCards(summary);
  const history = useMemo(
    () => snapshotQuery.data?.history ?? [],
    [snapshotQuery.data],
  );
  const totalSeries = useMemo(() => pivotHistory(history), [history]);
  const avgSeries = useMemo(() => pivotHistory(history), [history]);
  const languages = useMemo(
    () => groupByLanguage(trendsQuery.data?.results ?? []),
    [trendsQuery.data],
  );
  const statuses = sourceStatuses(summary);
  const tabs = sourceTabs(summary);

  const hasError = snapshotQuery.isError || trendsQuery.isError;
  const isLoading = snapshotQuery.isLoading || trendsQuery.isLoading;

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div>
            <h1 className="text-lg font-semibold text-slate-50">
              Analytics Dashboard
            </h1>
            <p className="text-xs text-slate-500">
              GitHub · Hacker News · Product Hunt
            </p>
          </div>
          <DateRangeFilter
            start={filters.start}
            end={filters.end}
            onChange={(start, end) => setFilters({ start, end })}
            invalid={invalidRange}
          />
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 space-y-4 px-6 py-6">
        {hasError ? (
          <div className="flex items-center justify-between gap-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 px-5 py-4">
            <p className="flex items-center gap-2 text-sm text-rose-300">
              <AlertTriangle className="h-4 w-4" />
              No se pudieron cargar los datos. Revisa que el backend esté
              corriendo en :8000.
            </p>
            <button
              type="button"
              onClick={() => snapshotQuery.refetch()}
              className="flex items-center gap-1.5 rounded-lg border border-rose-500/40 px-3 py-1.5 text-xs font-medium text-rose-300 transition-colors hover:bg-rose-500/10"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Reintentar
            </button>
          </div>
        ) : null}

        {isLoading && !hasError ? (
          <LoadingCards />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {cards.map((card) => (
              <MetricCard
                key={card.key}
                title={card.title}
                value={formatMetricValue(card.value)}
                icon={
                  card.key.includes("github")
                    ? Star
                    : card.key.includes("hn")
                      ? MessageSquare
                      : Rocket
                }
                hint={card.hint}
                accent={card.accent}
              />
            ))}
          </div>
        )}

        <div className={chartCardGrid()}>
          <ChartCard
            title="Evolución de métricas"
            description="Totales diarios por fuente"
            className="lg:col-span-2"
          >
            {isLoading ? (
              <div className="h-full w-full animate-pulse rounded-xl bg-slate-900" />
            ) : (
              <LineChart
                data={totalSeries}
                xKey="fecha"
                series={METRIC_TOTAL_TYPES.map((key) => ({
                  key,
                  label: key.replace("total_", "").replaceAll("_", " "),
                }))}
              />
            )}
          </ChartCard>
          <ChartCard
            title="Top lenguajes"
            description="Repos por lenguaje (GitHub)"
          >
            {isLoading ? (
              <div className="h-full w-full animate-pulse rounded-xl bg-slate-900" />
            ) : (
              <BarChart data={languages} xKey="language" barKey="repos" />
            )}
          </ChartCard>
        </div>

        <div className={chartCardGrid()}>
          <ChartCard
            title="Promedios diarios"
            description="Estrellas, forks, puntos y votos por día"
            className="lg:col-span-2"
          >
            {isLoading ? (
              <div className="h-full w-full animate-pulse rounded-xl bg-slate-900" />
            ) : (
              <AreaChart
                data={avgSeries}
                xKey="fecha"
                series={METRIC_AVG_TYPES.map((key) => ({
                  key,
                  label: key.replaceAll("_", " "),
                }))}
              />
            )}
          </ChartCard>
          <SectionCard
            title="Estado de fuentes"
            description="Disponibilidad de cada integración"
            className="flex flex-col justify-center gap-3"
          >
            {statuses.map((src) => (
              <div key={src.name} className="flex items-center gap-3 text-sm">
                <span
                  className={cn(
                    "h-2 w-2 rounded-full",
                    src.ok ? "bg-emerald-400" : "bg-rose-400",
                  )}
                />
                <span className="font-medium text-slate-200">{src.name}</span>
                <span className="ml-auto text-right text-xs text-slate-500">
                  {src.detail}
                </span>
              </div>
            ))}
            {summary ? (
              <p className="mt-2 border-t border-slate-800 pt-3 text-xs text-slate-500">
                Rango consultado: {summary.date_range.start} →{" "}
                {summary.date_range.end}
              </p>
            ) : null}
          </SectionCard>
        </div>

        <SectionCard
          title="Datos por fuente"
          description="Datos reales del backend — ordenable, con búsqueda y paginación"
          action={
            <div className="flex flex-wrap gap-1.5">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setCategory(tab.id)}
                  className={cn(
                    "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                    category === tab.id
                      ? "bg-indigo-500/15 text-indigo-300 ring-1 ring-indigo-500/40"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200",
                  )}
                >
                  <tab.icon className="h-3.5 w-3.5" />
                  {tab.label}
                  <span className="rounded-full bg-slate-800 px-1.5 py-0.5 text-[10px] tabular-nums text-slate-400">
                    {tab.count}
                  </span>
                </button>
              ))}
            </div>
          }
        >
          <SourceTable
            category={category}
            start={filters.start}
            end={filters.end}
            enabled={!invalidRange}
          />
        </SectionCard>
      </main>

      <footer className="border-t border-slate-800/80 py-4 text-center text-xs text-slate-600">
        Analytics Dashboard — GitHub · Hacker News · Product Hunt
      </footer>
    </div>
  );
}