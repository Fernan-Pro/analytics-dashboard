"""Cliente HTTP compartido para APIs externas con retry y manejo de rate limits.

- Retry exponencial (con jitter) en respuestas 429 / 5xx.
- Respeta cabeceras Retry-After y X-RateLimit-Reset cuando existen.
- Lanza ApiClientError con contexto útil para logs y Celery retry.
"""

import logging
import random
import time
from datetime import date, datetime, timedelta
from datetime import time as dtime
from datetime import timezone as dt_timezone

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
DEFAULT_TIMEOUT = 30
MAX_BACKOFF_SECONDS = 120


class ApiClientError(Exception):
    """Error de comunicación con una API externa (no retryable o agotado)."""


def _retry_after_seconds(resp: requests.Response, attempt: int) -> float:
    """Calcula segundos de espera: cabecera Retry-After > X-RateLimit-Reset > backoff."""
    header = resp.headers.get("Retry-After")
    if header:
        try:
            return min(float(header), MAX_BACKOFF_SECONDS)
        except ValueError:
            pass

    reset = resp.headers.get("X-RateLimit-Reset")
    if reset:
        try:
            return max(0.0, min(int(reset) - time.time() + 1.0, MAX_BACKOFF_SECONDS))
        except ValueError:
            pass

    return min(2 ** attempt + random.uniform(0, 0.5), MAX_BACKOFF_SECONDS)


def request_with_retry(
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    params: dict | None = None,
    json_body: dict | None = None,
    data: dict | None = None,
    auth: tuple[str, str] | None = None,
    max_retries: int = 3,
    timeout: int = DEFAULT_TIMEOUT,
) -> requests.Response:
    """Ejecuta una petición HTTP con reintentos. Devuelve la response final (status < 400)."""
    for attempt in range(max_retries + 1):
        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_body,
                data=data,
                auth=auth,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            # Errores de conexión/timeout: reintentar con backoff
            if attempt < max_retries:
                wait = min(2 ** attempt + random.uniform(0, 0.5), MAX_BACKOFF_SECONDS)
                logger.warning(
                    "Error de conexión en %s %s (%s). Reintento en %.1fs (intento %d/%d)",
                    method,
                    url,
                    exc,
                    wait,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(wait)
                continue
            raise ApiClientError(f"{method} {url}: error de conexión: {exc}") from exc

        if resp.status_code in RETRYABLE_STATUS and attempt < max_retries:
            wait = _retry_after_seconds(resp, attempt)
            logger.warning(
                "HTTP %s en %s %s. Reintento en %.1fs (intento %d/%d)",
                resp.status_code,
                method,
                url,
                wait,
                attempt + 1,
                max_retries,
            )
            time.sleep(wait)
            continue

        if resp.status_code >= 400:
            raise ApiClientError(
                f"{method} {url} -> HTTP {resp.status_code}: {resp.text[:300]}"
            )

        _log_rate_limit(resp, url)
        return resp

    raise ApiClientError(f"{method} {url}: reintentos agotados")  # pragma: no cover


def _log_rate_limit(resp: requests.Response, url: str) -> None:
    """Log en debug del rate limit restante si la API lo expone."""
    remaining = resp.headers.get("X-RateLimit-Remaining")
    limit = resp.headers.get("X-RateLimit-Limit")
    if remaining is not None:
        logger.debug("RateLimit %s: %s/%s restantes", url, remaining, limit)


class MetricAggregator:
    """Calcula métricas diarias por fuente y persiste snapshots (histórico de gráficos)."""

    def run_daily(self, days_back: int = 1) -> list["MetricSnapshot"]:
        """Agrega los últimos `days_back` días (incluido hoy) y guarda snapshots idempotentes."""
        snapshots: list[MetricSnapshot] = []
        today = timezone.localdate()
        for offset in range(days_back, -1, -1):
            snapshots.extend(self._aggregate_day(today - timedelta(days=offset)))
        return snapshots

    def _aggregate_day(self, day: date) -> list[MetricSnapshot]:
        from django.db.models import Avg

        from analytics.models import MetricSnapshot
        from github.models import GitHubTrend
        from hackernews.models import HackerNewsStory
        from producthunt.models import ProductHuntLaunch

        ts = datetime.combine(day, dtime.min, tzinfo=dt_timezone.utc)
        gh = GitHubTrend.objects.filter(trending_date=day)
        hn = HackerNewsStory.objects.filter(created_at__date=day)
        ph = ProductHuntLaunch.objects.filter(launch_date=day)

        metrics = {
            MetricSnapshot.MetricType.TOTAL_GITHUB_TRENDS: gh.count(),
            MetricSnapshot.MetricType.AVG_STARS: gh.aggregate(avg=Avg("stars"))["avg"],
            MetricSnapshot.MetricType.AVG_FORKS: gh.aggregate(avg=Avg("forks"))["avg"],
            MetricSnapshot.MetricType.TOTAL_HN_STORIES: hn.count(),
            MetricSnapshot.MetricType.AVG_HN_POINTS: hn.aggregate(avg=Avg("points"))["avg"],
            MetricSnapshot.MetricType.AVG_HN_COMMENTS: hn.aggregate(avg=Avg("comments"))["avg"],
            MetricSnapshot.MetricType.TOTAL_PH_LAUNCHES: ph.count(),
            MetricSnapshot.MetricType.AVG_PH_VOTES: ph.aggregate(avg=Avg("votes"))["avg"],
        }

        snapshots = []
        for metric_type, value in metrics.items():
            snapshot, _ = MetricSnapshot.objects.update_or_create(
                metric_type=metric_type,
                timestamp=ts,
                defaults={"value": value or 0},
            )
            snapshots.append(snapshot)
        return snapshots


class MetricsSummaryService:
    """Resumen de KPIs por rango de fechas para el endpoint /api/metrics/snapshot/."""

    def summary(self, start_date: date, end_date: date) -> dict:
        from django.db.models import Avg, Count, Sum

        from github.models import GitHubTrend
        from hackernews.models import HackerNewsStory
        from producthunt.models import ProductHuntLaunch

        gh = GitHubTrend.objects.filter(trending_date__range=[start_date, end_date])
        hn = HackerNewsStory.objects.filter(created_at__date__range=[start_date, end_date])
        ph = ProductHuntLaunch.objects.filter(launch_date__range=[start_date, end_date])

        top_language = (
            gh.exclude(language__isnull=True)
            .exclude(language="")
            .values("language")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )
        top_author = (
            hn.values("author")
            .annotate(total_points=Sum("points"))
            .order_by("-total_points")
            .first()
        )

        return {
            "total_github_trends": gh.count(),
            "avg_stars": round(gh.aggregate(avg=Avg("stars"))["avg"] or 0, 1),
            "avg_forks": round(gh.aggregate(avg=Avg("forks"))["avg"] or 0, 1),
            "top_language": top_language["language"] if top_language else None,
            "total_hn_stories": hn.count(),
            "avg_hn_points": round(hn.aggregate(avg=Avg("points"))["avg"] or 0, 1),
            "avg_hn_comments": round(hn.aggregate(avg=Avg("comments"))["avg"] or 0, 1),
            "top_author": top_author["author"] if top_author else None,
            "total_ph_launches": ph.count(),
            "avg_ph_votes": round(ph.aggregate(avg=Avg("votes"))["avg"] or 0, 1),
            "top_product": ph.order_by("-votes").values_list("product_name", flat=True).first(),
            "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        }