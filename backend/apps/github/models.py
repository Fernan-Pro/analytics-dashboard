from django.db import models


class GitHubTrend(models.Model):
    """Repositorio trending de GitHub para un día concreto (Search API)."""

    repo_name = models.CharField("Nombre del repo", max_length=255, db_index=True)
    stars = models.PositiveIntegerField("Estrellas", default=0)
    forks = models.PositiveIntegerField("Forks", default=0)
    language = models.CharField("Lenguaje", max_length=100, null=True, blank=True, db_index=True)
    description = models.TextField("Descripción", null=True, blank=True)
    url = models.URLField("URL", max_length=500)
    trending_date = models.DateField("Fecha del trending", db_index=True)
    created_at = models.DateTimeField("Creado en BD", auto_now_add=True)

    class Meta:
        ordering = ["-trending_date", "-stars"]
        constraints = [
            models.UniqueConstraint(
                fields=["url", "trending_date"],
                name="uniq_github_repo_per_trending_date",
            )
        ]
        indexes = [
            models.Index(fields=["language", "trending_date"], name="github_lang_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.repo_name} ({self.trending_date})"