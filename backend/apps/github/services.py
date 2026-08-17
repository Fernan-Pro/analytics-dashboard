"""Servicio de scraping de GitHub (Search API).

Documentación: https://docs.github.com/rest/search/search#search-repositories
Sin token: 10 req/min (búsqueda). Con token (GITHUB_TOKEN): 30 req/min.
"""

import logging
from datetime import date

from django.conf import settings
from django.utils import timezone

from analytics.services import request_with_retry
from github.models import GitHubTrend

logger = logging.getLogger(__name__)


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or getattr(settings, "GITHUB_TOKEN", "")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "analytics-dashboard/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def fetch_trending_repos(
        self, trending_date: date | None = None, per_page: int = 50
    ) -> list[dict]:
        """Repos creados en `trending_date` ordenados por estrellas (trending del día)."""
        trending_date = trending_date or timezone.localdate()
        params = {
            "q": f"created:{trending_date.isoformat()}",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
        }
        resp = request_with_retry(
            "GET",
            f"{self.BASE_URL}/search/repositories",
            headers=self.headers,
            params=params,
        )
        items = resp.json().get("items", [])
        logger.info("GitHub API: %d repos para %s", len(items), trending_date)
        return [self._normalize(item, trending_date) for item in items]

    @staticmethod
    def _normalize(item: dict, trending_date: date) -> dict:
        """Normaliza el payload de la API a los campos del modelo GitHubTrend."""
        return {
            "repo_name": item.get("full_name") or item.get("name") or "",
            "stars": item.get("stargazers_count") or 0,
            "forks": item.get("forks_count") or 0,
            "language": item.get("language"),
            "description": item.get("description"),
            "url": item.get("html_url") or "",
            "trending_date": trending_date,
        }

    @staticmethod
    def store_trends(items: list[dict]) -> int:
        """Persiste de forma idempotente (update_conflicts) y devuelve filas afectadas."""
        if not items:
            return 0
        return len(
            GitHubTrend.objects.bulk_create(
                [GitHubTrend(**item) for item in items],
                update_conflicts=True,
                update_fields=["repo_name", "stars", "forks", "language", "description"],
                unique_fields=["url", "trending_date"],
            )
        )