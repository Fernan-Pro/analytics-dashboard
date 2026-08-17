"""Vistas de Analytics: resumen de métricas (snapshot), exportación CSV y fetch protegido."""

import csv
import io
import logging
from datetime import date, timedelta

from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.filters import CSV_SOURCES, filterset_for
from analytics.models import MetricSnapshot
from analytics.serializers import MetricSnapshotSerializer
from analytics.services import MetricsSummaryService

logger = logging.getLogger(__name__)


def _parse_date(raw: str | None, default: date) -> date:
    """Convierte una fecha ISO del query param; 400 explícito si el formato es inválido."""
    if not raw:
        return default
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ValidationError(f"Fecha inválida: '{raw}' (formato esperado: YYYY-MM-DD)")


class MetricsSnapshotView(APIView):
    """GET /api/metrics/snapshot/?start_date=&end_date=

    Devuelve `summary` (KPIs del rango) y `history` (snapshots del histórico).
    """

    def get(self, request) -> Response:
        try:
            today = timezone.localdate()
            start_date = _parse_date(request.query_params.get("start_date"), today - timedelta(days=6))
            end_date = _parse_date(request.query_params.get("end_date"), today)
        except ValidationError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if start_date > end_date:
            return Response(
                {"error": "start_date no puede ser posterior a end_date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        summary = MetricsSummaryService().summary(start_date, end_date)
        history = MetricSnapshot.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date,
        ).order_by("timestamp")
        return Response(
            {
                "summary": summary,
                "history": MetricSnapshotSerializer(history, many=True).data,
            }
        )


@api_view(["GET"])
def export_csv(request) -> StreamingHttpResponse | Response:
    """GET /api/export/csv/?category=github|reddit|producthunt&<filtros>

    Exporta los datos filtrados a CSV (streaming). Filtros: los mismos que los endpoints.
    """
    category = request.query_params.get("category", "").lower()
    if category not in CSV_SOURCES:
        return Response(
            {"error": f"category inválida: '{category}'. Válidas: {', '.join(CSV_SOURCES)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    source = CSV_SOURCES[category]
    qs = filterset_for(category, request.query_params, source["model"].objects.all()).qs
    qs = qs.order_by(*source["order_by"])

    def stream() -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(source["headers"])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)
        for obj in qs.iterator(chunk_size=500):
            writer.writerow([getattr(obj, col) for col in source["columns"]])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

    today = timezone.localdate().isoformat()
    response = StreamingHttpResponse(stream(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="analytics_{category}_{today}.csv"'
    return response


@api_view(["POST"])
def admin_fetch(request) -> Response:
    """POST /api/admin/fetch/ — ejecuta las tareas de scraping de forma síncrona.

    Protegido con el token `ADMIN_FETCH_TOKEN` (header X-Admin-Token).
    Es el sustituto de Celery en entornos sin Redis: lo llama el cron de
    GitHub Actions cada 15 minutos (ver .github/workflows/fetch-data.yml).
    """
    token = request.headers.get("X-Admin-Token", "")
    expected = getattr(settings, "ADMIN_FETCH_TOKEN", "")
    if not expected or token != expected:
        return Response(
            {"error": "Token inválido"}, status=status.HTTP_401_UNAUTHORIZED
        )

    from analytics.tasks import aggregate_metrics
    from github.tasks import fetch_github_trends
    from hackernews.tasks import fetch_hackernews_stories
    from producthunt.tasks import fetch_producthunt_launches

    tasks = {
        "github": fetch_github_trends,
        "hackernews": fetch_hackernews_stories,
        "producthunt": fetch_producthunt_launches,
        "metrics": aggregate_metrics,
    }
    results: dict = {}
    for name, task in tasks.items():
        try:
            results[name] = task()
        except Exception as exc:  # noqa: BLE001 - un fallo no debe romper el resto
            logger.exception("admin_fetch: %s falló", name)
            results[name] = {"error": str(exc)[:300]}
    return Response(results)


class ValidationError(Exception):
    """Error de validación de query params."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)