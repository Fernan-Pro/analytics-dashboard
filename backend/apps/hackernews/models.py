from django.db import models


class HackerNewsStory(models.Model):
    """Historia top de Hacker News capturada por el scraper (API Algolia)."""

    hn_id = models.IntegerField("ID en Hacker News", unique=True)
    title = models.CharField("Título", max_length=500)
    points = models.IntegerField("Puntos", default=0)
    comments = models.PositiveIntegerField("Comentarios", default=0)
    author = models.CharField("Autor", max_length=100, db_index=True)
    url = models.URLField("URL", max_length=1000, blank=True, default="")
    created_at = models.DateTimeField("Fecha de la historia (UTC)", db_index=True)
    fetched_at = models.DateTimeField("Capturado en BD", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-points"]
        indexes = [
            models.Index(fields=["author", "created_at"], name="hn_author_created_idx"),
            models.Index(fields=["points"], name="hn_points_idx"),
        ]

    def __str__(self) -> str:
        return f"HN#{self.hn_id}: {self.title[:60]}"