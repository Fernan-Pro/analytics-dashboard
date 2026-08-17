from django.db import models


class MetricSnapshot(models.Model):
    """Snapshot de métricas agregadas por día para el histórico de gráficos."""

    class MetricType(models.TextChoices):
        TOTAL_GITHUB_TRENDS = "total_github_trends", "Total repos trending"
        AVG_STARS = "avg_stars", "Media de estrellas (GitHub)"
        AVG_FORKS = "avg_forks", "Media de forks (GitHub)"
        TOTAL_HN_STORIES = "total_hn_stories", "Total historias Hacker News"
        AVG_HN_POINTS = "avg_hn_points", "Media de puntos (Hacker News)"
        AVG_HN_COMMENTS = "avg_hn_comments", "Media de comentarios (Hacker News)"
        TOTAL_PH_LAUNCHES = "total_ph_launches", "Total launches Product Hunt"
        AVG_PH_VOTES = "avg_ph_votes", "Media de votos (Product Hunt)"

    metric_type = models.CharField(
        "Tipo de métrica", max_length=64, choices=MetricType.choices, db_index=True
    )
    value = models.FloatField("Valor")
    timestamp = models.DateTimeField("Timestamp (UTC)", db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        constraints = [
            models.UniqueConstraint(
                fields=["metric_type", "timestamp"],
                name="uniq_metric_per_timestamp",
            )
        ]

    def __str__(self) -> str:
        return f"{self.metric_type}={self.value} @ {self.timestamp:%Y-%m-%d %H:%M}"