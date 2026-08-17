from django.contrib import admin

from github.models import GitHubTrend


@admin.register(GitHubTrend)
class GitHubTrendAdmin(admin.ModelAdmin):
    list_display = ("repo_name", "language", "stars", "forks", "trending_date")
    list_filter = ("language", "trending_date")
    search_fields = ("repo_name", "description")
    date_hierarchy = "trending_date"
    ordering = ("-trending_date", "-stars")