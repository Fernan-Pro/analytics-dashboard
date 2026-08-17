"""Tareas Celery para el scraping de Hacker News (beat: cada 15 minutos)."""

import logging

from celery import shared_task

from hackernews.models import HackerNewsStory
from hackernews.services import HackerNewsService

logger = logging.getLogger(__name__)


@shared_task(name="hackernews.tasks.fetch_hackernews_stories")
def fetch_hackernews_stories() -> dict:
    """Obtiene historias de la portada de Hacker News y las persiste."""
    items = HackerNewsService().fetch_front_page()
    inserted = HackerNewsService.store_stories(items)
    total = HackerNewsStory.objects.count()
    logger.info(
        "fetch_hackernews_stories: %d historias capturadas (%d nuevas), %d en BD",
        len(items),
        inserted,
        total,
    )
    return {"fetched": len(items), "inserted": inserted, "total": total}