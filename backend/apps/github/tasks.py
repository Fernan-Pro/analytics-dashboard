"""Tareas Celery para el scraping de GitHub (beat: cada 30 minutos)."""

import logging

from celery import shared_task

from analytics.services import ApiClientError
from github.models import GitHubTrend
from github.services import GitHubService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="github.tasks.fetch_github_trends")
def fetch_github_trends(self) -> dict:
    """Obtiene repos trending del día y los persiste de forma idempotente."""
    try:
        items = GitHubService().fetch_trending_repos()
    except ApiClientError as exc:
        logger.warning("fetch_github_trends: fallo de API, reintentando: %s", exc)
        raise self.retry(exc=exc)

    inserted = GitHubService.store_trends(items)
    total = GitHubTrend.objects.count()
    logger.info("fetch_github_trends: %d repos procesados, %d en BD", len(items), total)
    return {"fetched": len(items), "inserted": inserted, "total": total}