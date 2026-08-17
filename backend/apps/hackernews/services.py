"""Servicio de scraping de Hacker News (API oficial de Algolia, sin credenciales).

Endpoint usado: https://hn.algolia.com/api/v1/search?tags=front_page
Devuelve las historias de la portada con puntos, comentarios, autor y fecha.
"""

import logging
from datetime import datetime

from django.utils import timezone

from analytics.services import request_with_retry
from hackernews.models import HackerNewsStory

logger = logging.getLogger(__name__)

SEARCH_URL = "https://hn.algolia.com/api/v1/search"


class HackerNewsService:
    def fetch_front_page(self, hits_per_page: int = 50) -> list[dict]:
        """Historias de la portada de Hacker News (top del momento)."""
        resp = request_with_retry(
            "GET",
            SEARCH_URL,
            params={"tags": "front_page", "hitsPerPage": hits_per_page},
            timeout=25,
        )
        hits = resp.json().get("hits", [])
        logger.info("Hacker News API: %d historias en portada", len(hits))
        return [self._normalize(hit) for hit in hits]

    @staticmethod
    def _normalize(hit: dict) -> dict:
        """Normaliza un hit de Algolia a los campos del modelo HackerNewsStory."""
        hn_id = hit.get("objectID")
        created_raw = hit.get("created_at")
        created_at = (
            datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            if created_raw
            else timezone.now()
        )
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hn_id}"
        return {
            "hn_id": int(hn_id) if hn_id else 0,
            "title": (hit.get("title") or hit.get("story_title") or "")[:500],
            "points": hit.get("points") or 0,
            "comments": hit.get("num_comments") or 0,
            "author": hit.get("author") or "",
            "url": url[:1000],
            "created_at": created_at,
        }

    @staticmethod
    def store_stories(items: list[dict]) -> int:
        """Persiste de forma idempotente (update_or_create por hn_id) y devuelve nº de inserts."""
        created = 0
        for item in items:
            if not item["hn_id"]:
                continue
            _, was_created = HackerNewsStory.objects.update_or_create(
                hn_id=item["hn_id"],
                defaults={
                    "title": item["title"],
                    "points": item["points"],
                    "comments": item["comments"],
                    "author": item["author"],
                    "url": item["url"],
                    "created_at": item["created_at"],
                },
            )
            created += int(was_created)
        return created