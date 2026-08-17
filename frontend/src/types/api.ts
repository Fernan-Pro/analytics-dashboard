export interface GitHubTrend {
  id: number;
  repo_name: string;
  stars: number;
  forks: number;
  language: string | null;
  description: string | null;
  url: string;
  trending_date: string;
  created_at: string;
}

export interface HackerNewsStory {
  id: number;
  hn_id: number;
  title: string;
  points: number;
  comments: number;
  author: string;
  url: string;
  created_at: string;
  fetched_at: string;
}

export interface ProductHuntLaunch {
  id: number;
  product_name: string;
  tagline: string | null;
  votes: number;
  url: string;
  launch_date: string;
  created_at: string;
}

export interface MetricSnapshot {
  metric_type: string;
  value: number;
  timestamp: string;
}

export interface MetricsSummary {
  total_github_trends: number;
  avg_stars: number;
  avg_forks: number;
  top_language: string | null;
  total_hn_stories: number;
  avg_hn_points: number;
  avg_hn_comments: number;
  top_author: string | null;
  total_ph_launches: number;
  avg_ph_votes: number;
  top_product: string | null;
  date_range: { start: string; end: string };
}

export interface MetricsSnapshotResponse {
  summary: MetricsSummary;
  history: MetricSnapshot[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type Category = "github" | "hackernews" | "producthunt";

export interface DateRange {
  start: string | undefined;
  end: string | undefined;
}

/** Filtros globales del dashboard compartidos por todos los endpoints. */
export interface GlobalFilters {
  category: Category | "all";
  start: string | undefined;
  end: string | undefined;
}