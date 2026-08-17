from rest_framework import viewsets

from hackernews.filters import HackerNewsStoryFilter
from hackernews.models import HackerNewsStory
from hackernews.serializers import HackerNewsStorySerializer


class HackerNewsStoryViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/hackernews/stories/?author=&min_points=&min_comments=&start_date=&end_date="""  # noqa: E501

    queryset = HackerNewsStory.objects.all()
    serializer_class = HackerNewsStorySerializer
    filterset_class = HackerNewsStoryFilter
    ordering_fields = ["points", "comments", "created_at", "author"]
    ordering = ["-created_at", "-points"]