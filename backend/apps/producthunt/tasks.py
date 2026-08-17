"""Tareas Celery para el scraping de Product Hunt (beat: cada hora)."""

import logging

from celery import shared_task

from analytics.services import ApiClientError
from producthunt.models import ProductHuntLaunch
from producthunt.services import ProductHuntService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="producthunt.tasks.fetch_producthunt_launches")
def fetch_producthunt_launches(self) -> dict:
    """Obtiene launches de las últimas 24h y los persiste de forma idempotente."""
    try:
        items = ProductHuntService().fetch_launches()
    except ValueError as exc:
        # Token no configurado: no reintentar, solo loguear
        logger.warning("fetch_producthunt_launches: %s", exc)
        return {"skipped": True, "reason": str(exc)}
    except ApiClientError as exc:
        logger.warning("fetch_producthunt_launches: fallo de API, reintentando: %s", exc)
        raise self.retry(exc=exc)

    inserted = ProductHuntService.store_launches(items)
    total = ProductHuntLaunch.objects.count()
    logger.info("fetch_producthunt_launches: %d launches, %d en BD", len(items), total)
    return {"fetched": len(items), "inserted": inserted, "total": total}