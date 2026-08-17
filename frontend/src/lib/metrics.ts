import type {
  GitHubTrend,
  MetricSnapshot,
  MetricsSummary,
} from "@/types/api";

import { formatDate } from "./utils";

export interface SeriesRow {
  fecha: string;
  [key: string]: string | number;
}

/** Metric types de totales y promedios (los mismos que genera el backend). */
export const METRIC_TOTAL_TYPES = [
  "total_github_trends",
  "total_hn_stories",
  "total_ph_launches",
] as const;

export const METRIC_AVG_TYPES = [
  "avg_stars",
  "avg_forks",
  "avg_hn_points",
  "avg_hn_comments",
  "avg_ph_votes",
] as const;

/** Pivotea el history de MetricSnapshot a filas por día para Recharts. */
export function pivotHistory(history: MetricSnapshot[]): SeriesRow[] {
  const byDay = new Map<string, Record<string, number>>();
  for (const snap of history) {
    const day = formatDate(snap.timestamp);
    if (!byDay.has(day)) byDay.set(day, {});
    byDay.get(day)![snap.metric_type] = snap.value;
  }
  return Array.from(byDay.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([fecha, values]) => ({ fecha, ...values }));
}

/** Agrupa repos por lenguaje y devuelve el top N (ordenado desc por cantidad). */
export function groupByLanguage(
  trends: GitHubTrend[],
  topN = 8,
): { language: string; repos: number }[] {
  const counts = new Map<string, number>();
  for (const t of trends) {
    const lang = t.language ?? "Sin lenguaje";
    counts.set(lang, (counts.get(lang) ?? 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([language, repos]) => ({ language, repos }))
    .sort((a, b) => b.repos - a.repos)
    .slice(0, topN);
}

export interface SourceStatus {
  name: string;
  ok: boolean;
  detail: string;
}

/** Infiere el estado de cada integración a partir del summary. */
export function sourceStatuses(summary: MetricsSummary | undefined): SourceStatus[] {
  if (!summary) return [];
  return [
    {
      name: "GitHub API",
      ok: summary.total_github_trends > 0,
      detail:
        summary.total_github_trends > 0
          ? `${summary.total_github_trends} repos indexados`
          : "Sin datos todavía",
    },
    {
      name: "Hacker News API",
      ok: summary.total_hn_stories > 0,
      detail:
        summary.total_hn_stories > 0
          ? `${summary.total_hn_stories} historias indexadas`
          : "Sin datos todavía",
    },
    {
      name: "Product Hunt API",
      ok: summary.total_ph_launches > 0,
      detail:
        summary.total_ph_launches > 0
          ? `${summary.total_ph_launches} launches indexados`
          : "Sin datos (falta el token)",
    },
  ];
}

export interface MetricCardData {
  title: string;
  value: number;
  hint: string;
  accent: string;
  key: keyof MetricsSummary;
}

/** Define las 6 tarjetas KPI a partir del summary. */
export function metricCards(summary: MetricsSummary | undefined): MetricCardData[] {
  const n = (key: keyof MetricsSummary): number =>
    summary ? (Number(summary[key]) || 0) : 0;
  return [
    {
      title: "Repos en tendencia",
      value: n("total_github_trends"),
      hint: "últimos 7 días",
      accent: "bg-indigo-500/10 text-indigo-400",
      key: "total_github_trends",
    },
    {
      title: "Estrellas promedio",
      value: n("avg_stars"),
      hint: "por repo",
      accent: "bg-amber-500/10 text-amber-400",
      key: "avg_stars",
    },
    {
      title: "Historias de HN",
      value: n("total_hn_stories"),
      hint: "últimos 7 días",
      accent: "bg-orange-500/10 text-orange-400",
      key: "total_hn_stories",
    },
    {
      title: "Puntos promedio HN",
      value: n("avg_hn_points"),
      hint: "por historia",
      accent: "bg-rose-500/10 text-rose-400",
      key: "avg_hn_points",
    },
    {
      title: "Launches de PH",
      value: n("total_ph_launches"),
      hint: "últimos 7 días",
      accent: "bg-pink-500/10 text-pink-400",
      key: "total_ph_launches",
    },
    {
      title: "Votos promedio PH",
      value: n("avg_ph_votes"),
      hint: "por launch",
      accent: "bg-emerald-500/10 text-emerald-400",
      key: "avg_ph_votes",
    },
  ];
}