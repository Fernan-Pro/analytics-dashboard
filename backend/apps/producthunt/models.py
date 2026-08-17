from django.db import models


class ProductHuntLaunch(models.Model):
    """Launch del día de Product Hunt (GraphQL API)."""

    product_name = models.CharField("Nombre del producto", max_length=255)
    tagline = models.TextField("Tagline", null=True, blank=True)
    votes = models.PositiveIntegerField("Votos", default=0)
    url = models.URLField("URL", max_length=500, unique=True)
    launch_date = models.DateField("Fecha de lanzamiento", db_index=True)
    created_at = models.DateTimeField("Creado en BD", auto_now_add=True)

    class Meta:
        ordering = ["-launch_date", "-votes"]
        indexes = [
            models.Index(fields=["launch_date", "votes"], name="ph_date_votes_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.product_name} ({self.launch_date})"