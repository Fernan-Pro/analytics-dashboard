"""Configuración central de fuentes de datos para el endpoint de export CSV."""

from github.filters import GitHubTrendFilter
from github.models import GitHubTrend
from hackernews.filters import HackerNewsStoryFilter
from hackernews.models import HackerNewsStory
from producthunt.filters import ProductHuntLaunchFilter
from producthunt.models import ProductHuntLaunch

CSV_SOURCES: dict[str, dict] = {
    "github": {
        "model": GitHubTrend,
        "filterset": GitHubTrendFilter,
        "headers": [
            "repo_name",
            "stars",
            "forks",
            "language",
            "description",
            "url",
            "trending_date",
        ],
        "columns": [
            "repo_name",
            "stars",
            "forks",
            "language",
            "description",
            "url",
            "trending_date",
        ],
        "order_by": ("-trending_date", "-stars"),
    },
    "hackernews": {
        "model": HackerNewsStory,
        "filterset": HackerNewsStoryFilter,
        "headers": ["title", "author", "points", "comments", "url", "created_at"],
        "columns": ["title", "author", "points", "comments", "url", "created_at"],
        "order_by": ("-created_at", "-points"),
    },
    "producthunt": {
        "model": ProductHuntLaunch,
        "filterset": ProductHuntLaunchFilter,
        "headers": ["product_name", "tagline", "votes", "url", "launch_date"],
        "columns": ["product_name", "tagline", "votes", "url", "launch_date"],
        "order_by": ("-launch_date", "-votes"),
    },
}


def filterset_for(category: str, query_params: dict, queryset):
    """Aplica el filterset de la categoría a un queryset (usado por export CSV)."""
    return CSV_SOURCES[category]["filterset"](query_params, queryset=queryset)