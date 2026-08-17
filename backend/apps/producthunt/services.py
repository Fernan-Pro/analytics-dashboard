"""Servicio de scraping de Product Hunt (GraphQL API v2).

Requiere token de desarrollador (PRODUCT_HUNT_TOKEN):
https://www.producthunt.com/v2/oauth/applications -> "Create token"
"""

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from analytics.services import request_with_retry
from producthunt.models import ProductHuntLaunch

logger = logging.getLogger(__name__)


class ProductHuntService:
    API_URL = "https://api.producthunt.com/v2/api/graphql"

    GET_LAUNCHES_QUERY = """
    query GetLaunches($postedAfter: DateTime!, $first: Int!) {
      posts(order: VOTES, postedAfter: $postedAfter, first: $first) {
        edges {
          node {
            id
            name
            tagline
            votesCount
            createdAt
            url
          }
        }
      }
    }
    """

    def __init__(self, token: str | None = None) -> None:
        self.token = token or getattr(settings, "PRODUCT_HUNT_TOKEN", "")
        if not self.token:
            raise ValueError(
                "PRODUCT_HUNT_TOKEN no configurado. Crea un token de desarrollo en "
                "https://www.producthunt.com/v2/oauth/applications"
            )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def fetch_launches(self, since: datetime | None = None, limit: int = 20) -> list[dict]:
        """Launches ordenados por votos publicados desde `since` (por defecto, últimas 24h)."""
        since = since or (timezone.now() - timedelta(hours=24))
        payload = {
            "query": self.GET_LAUNCHES_QUERY,
            "variables": {"postedAfter": since.isoformat(), "first": limit},
        }
        resp = request_with_retry(
            "POST", self.API_URL, headers=self.headers, json_body=payload
        )
        edges = resp.json()["data"]["posts"]["edges"]
        logger.info("Product Hunt API: %d launches desde %s", len(edges), since)
        return [self._normalize(edge["node"]) for edge in edges]

    @staticmethod
    def _normalize(node: dict) -> dict:
        """Normaliza un node de GraphQL a los campos del modelo ProductHuntLaunch."""
        created_at = node.get("createdAt", "")
        launch_date = None
        if created_at:
            launch_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
        return {
            "product_name": node.get("name", ""),
            "tagline": node.get("tagline", ""),
            "votes": node.get("votesCount") or 0,
            "url": node.get("url", ""),
            "launch_date": launch_date or timezone.localdate(),
        }

    @staticmethod
    def store_launches(items: list[dict]) -> int:
        """Persiste de forma idempotente (update_or_create por url única) y devuelve nº de inserts."""
        created = 0
        for item in items:
            _, was_created = ProductHuntLaunch.objects.update_or_create(
                url=item["url"],
                defaults={
                    "product_name": item["product_name"],
                    "tagline": item["tagline"],
                    "votes": item["votes"],
                    "launch_date": item["launch_date"],
                },
            )
            created += int(was_created)
        return created