from rest_framework import viewsets

from github.filters import GitHubTrendFilter
from github.models import GitHubTrend
from github.serializers import GitHubTrendSerializer


class GitHubTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/github/trends/?language=&start_date=&end_date=&min_stars=&ordering=&page="""  # noqa: E501

    queryset = GitHubTrend.objects.all()
    serializer_class = GitHubTrendSerializer
    filterset_class = GitHubTrendFilter
    ordering_fields = ["stars", "forks", "trending_date", "repo_name"]
    ordering = ["-trending_date", "-stars"]