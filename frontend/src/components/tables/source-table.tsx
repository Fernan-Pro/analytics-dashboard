"use client";

import { createColumnHelper } from "@tanstack/react-table";
import { useQuery } from "@tanstack/react-query";
import { ArrowBigUp, CalendarDays, Download, GitFork, MessageSquare, Rocket, Star } from "lucide-react";

import { DataTable } from "@/components/tables/data-table";
import { api, queryKeys, type QueryParams } from "@/lib/api";
import { formatCompact, formatDate, formatDateTime, formatNumber } from "@/lib/utils";
import type { Category, GitHubTrend, HackerNewsStory, ProductHuntLaunch } from "@/types/api";

const githubHelper = createColumnHelper<GitHubTrend>();
const hnHelper = createColumnHelper<HackerNewsStory>();
const phHelper = createColumnHelper<ProductHuntLaunch>();

const githubColumns = [
  githubHelper.accessor("repo_name", {
    header: "Repositorio",
    cell: ({ row }) => (
      <a
        href={row.original.url}
        target="_blank"
        rel="noopener noreferrer"
        className="font-medium text-indigo-400 hover:text-indigo-300 hover:underline"
      >
        {row.original.repo_name}
      </a>
    ),
  }),
  githubHelper.accessor("language", {
    header: "Lenguaje",
    cell: ({ row }) => (
      <span className="rounded-md bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
        {row.original.language ?? "—"}
      </span>
    ),
  }),
  githubHelper.accessor("stars", {
    header: "Estrellas",
    cell: ({ row }) => (
      <span className="flex items-center gap-1 tabular-nums">
        <Star className="h-3.5 w-3.5 text-amber-400" />
        {formatNumber(row.original.stars)}
      </span>
    ),
  }),
  githubHelper.accessor("forks", {
    header: "Forks",
    cell: ({ row }) => (
      <span className="flex items-center gap-1 tabular-nums">
        <GitFork className="h-3.5 w-3.5 text-slate-500" />
        {formatCompact(row.original.forks)}
      </span>
    ),
  }),
  githubHelper.accessor("description", {
    header: "Descripción",
    cell: ({ row }) => (
      <span className="line-clamp-1 max-w-md text-slate-400">
        {row.original.description ?? "—"}
      </span>
    ),
  }),
];

const hnColumns = [
  hnHelper.accessor("title", {
    header: "Título",
    cell: ({ row }) => (
      <a
        href={row.original.url}
        target="_blank"
        rel="noopener noreferrer"
        className="line-clamp-1 max-w-lg font-medium text-indigo-400 hover:text-indigo-300 hover:underline"
      >
        {row.original.title}
      </a>
    ),
  }),
  hnHelper.accessor("author", {
    header: "Autor",
    cell: ({ row }) => (
      <span className="rounded-md bg-orange-500/10 px-2 py-0.5 text-xs font-medium text-orange-400">
        {row.original.author}
      </span>
    ),
  }),
  hnHelper.accessor("points", {
    header: "Puntos",
    cell: ({ row }) => (
      <span className="flex items-center gap-1 tabular-nums">
        <ArrowBigUp className="h-3.5 w-3.5 text-orange-400" />
        {formatNumber(row.original.points)}
      </span>
    ),
  }),
  hnHelper.accessor("comments", {
    header: "Comentarios",
    cell: ({ row }) => (
      <span className="flex items-center gap-1 tabular-nums">
        <MessageSquare className="h-3.5 w-3.5 text-slate-500" />
        {formatNumber(row.original.comments)}
      </span>
    ),
  }),
  hnHelper.accessor("created_at", {
    header: "Publicado",
    cell: ({ row }) => (
      <span className="text-xs text-slate-400">
        {formatDateTime(row.original.created_at)}
      </span>
    ),
  }),
];

const phColumns = [
  phHelper.accessor("product_name", {
    header: "Producto",
    cell: ({ row }) => (
      <a
        href={row.original.url}
        target="_blank"
        rel="noopener noreferrer"
        className="font-medium text-indigo-400 hover:text-indigo-300 hover:underline"
      >
        {row.original.product_name}
      </a>
    ),
  }),
  phHelper.accessor("tagline", {
    header: "Tagline",
    cell: ({ row }) => (
      <span className="line-clamp-1 max-w-lg text-slate-400">
        {row.original.tagline ?? "—"}
      </span>
    ),
  }),
  phHelper.accessor("votes", {
    header: "Votos",
    cell: ({ row }) => (
      <span className="flex items-center gap-1 tabular-nums">
        <Rocket className="h-3.5 w-3.5 text-pink-400" />
        {formatNumber(row.original.votes)}
      </span>
    ),
  }),
  phHelper.accessor("launch_date", {
    header: "Lanzamiento",
    cell: ({ row }) => (
      <span className="flex items-center gap-1 text-xs text-slate-400">
        <CalendarDays className="h-3.5 w-3.5" />
        {formatDate(row.original.launch_date)}
      </span>
    ),
  }),
];

const EMPTY_MESSAGES: Record<Category, string> = {
  github: "No hay repositorios en el rango seleccionado",
  hackernews: "No hay historias de Hacker News en el rango seleccionado",
  producthunt: "Sin datos de Product Hunt — falta configurar el token",
};

interface SourceTableProps {
  category: Category;
  start: string | undefined;
  end: string | undefined;
  enabled: boolean;
}

export function SourceTable({ category, start, end, enabled }: SourceTableProps) {
  const dateParams = { start_date: start, end_date: end } as QueryParams;

  const githubQuery = useQuery({
    queryKey: queryKeys.githubTrends({ ...dateParams, page_size: 100 }),
    queryFn: () => api.githubTrends({ ...dateParams, page_size: 100 }),
    enabled: enabled && category === "github",
  });

  const hnQuery = useQuery({
    queryKey: queryKeys.hackerNewsStories({ ...dateParams, page_size: 100 }),
    queryFn: () => api.hackerNewsStories({ ...dateParams, page_size: 100 }),
    enabled: enabled && category === "hackernews",
  });

  const phQuery = useQuery({
    queryKey: queryKeys.productHuntLaunches({ ...dateParams, page_size: 100 }),
    queryFn: () => api.productHuntLaunches({ ...dateParams, page_size: 100 }),
    enabled: enabled && category === "producthunt",
  });

  const active =
    category === "github"
      ? githubQuery
      : category === "hackernews"
        ? hnQuery
        : phQuery;
  const githubData = githubQuery.data?.results ?? [];
  const hnData = hnQuery.data?.results ?? [];
  const phData = phQuery.data?.results ?? [];
  const exportUrl = api.exportCsvUrl(category, dateParams);

  return (
    <div>
      <div className="mb-3 flex justify-end">
        <a
          href={exportUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 rounded-lg border border-indigo-500/40 bg-indigo-500/10 px-3 py-1.5 text-xs font-medium text-indigo-300 transition-colors hover:bg-indigo-500/20 hover:text-indigo-200"
        >
          <Download className="h-3.5 w-3.5" />
          Exportar CSV
        </a>
      </div>
      {category === "github" ? (
        <DataTable
          columns={githubColumns}
          data={githubData}
          isLoading={active.isLoading}
          searchPlaceholder="Buscar repositorio, lenguaje, descripción..."
          emptyMessage={EMPTY_MESSAGES.github}
        />
      ) : category === "hackernews" ? (
        <DataTable
          columns={hnColumns}
          data={hnData}
          isLoading={active.isLoading}
          searchPlaceholder="Buscar título, autor..."
          emptyMessage={EMPTY_MESSAGES.hackernews}
        />
      ) : (
        <DataTable
          columns={phColumns}
          data={phData}
          isLoading={active.isLoading}
          searchPlaceholder="Buscar producto, tagline..."
          emptyMessage={EMPTY_MESSAGES.producthunt}
        />
      )}
    </div>
  );
}