"""Tarea Celery de agregación de métricas diarias (beat: 00:05 UTC)."""

import logging

from celery import shared_task

from analytics.services import MetricAggregator

logger = logging.getLogger(__name__)


@shared_task(name="analytics.tasks.aggregate_metrics")
def aggregate_metrics(days_back: int = 1) -> dict:
    """Calcula métricas diarias de los últimos `days_back` días y persiste snapshots."""
    snapshots = MetricAggregator().run_daily(days_back=days_back)
    logger.info("aggregate_metrics: %d snapshots guardados", len(snapshots))
    return {"snapshots": len(snapshots)}