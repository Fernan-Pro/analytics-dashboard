import type {
  Category,
  GitHubTrend,
  HackerNewsStory,
  MetricsSnapshotResponse,
  Paginated,
  ProductHuntLaunch,
} from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export type QueryParams = Record<string, string | number | undefined>;

export function buildQueryString(params?: QueryParams): string {
  if (!params) return "";
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(path: string, params?: QueryParams): Promise<T> {
  const url = `${API_URL}${path}${buildQueryString(params)}`;
  let res: Response;
  try {
    res = await fetch(url);
  } catch {
    throw new ApiError(0, "No se pudo conectar con la API. ¿Está corriendo el backend?");
  }
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body: unknown = await res.json();
      if (typeof body === "object" && body !== null) {
        const record = body as Record<string, unknown>;
        detail = String(record.error ?? record.detail ?? detail);
      }
    } catch {
      // cuerpo no JSON: usar el mensaje por defecto
    }
    throw new ApiError(res.status, detail);
  }
  return (await res.json()) as T;
}

/** Claves de query para TanStack Query (invalidación y cache). */
export const queryKeys = {
  githubTrends: (params?: QueryParams) => ["github-trends", params] as const,
  hackerNewsStories: (params?: QueryParams) =>
    ["hackernews-stories", params] as const,
  productHuntLaunches: (params?: QueryParams) =>
    ["producthunt-launches", params] as const,
  metricsSnapshot: (params?: QueryParams) => ["metrics-snapshot", params] as const,
};

export const api = {
  githubTrends: (params?: QueryParams) =>
    fetchApi<Paginated<GitHubTrend>>("/github/trends/", params),
  hackerNewsStories: (params?: QueryParams) =>
    fetchApi<Paginated<HackerNewsStory>>("/hackernews/stories/", params),
  productHuntLaunches: (params?: QueryParams) =>
    fetchApi<Paginated<ProductHuntLaunch>>("/producthunt/launches/", params),
  metricsSnapshot: (params?: QueryParams) =>
    fetchApi<MetricsSnapshotResponse>("/metrics/snapshot/", params),
  exportCsvUrl: (category: Category, params?: QueryParams): string =>
    `${API_URL}/export/csv/${buildQueryString({ ...params, category })}`,
};