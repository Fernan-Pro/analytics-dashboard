"""Rutas del proyecto: admin + API REST modular por app."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/github/", include("github.urls")),
    path("api/hackernews/", include("hackernews.urls")),
    path("api/producthunt/", include("producthunt.urls")),
    path("api/", include("analytics.urls")),
]