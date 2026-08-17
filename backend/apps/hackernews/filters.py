import django_filters

from hackernews.models import HackerNewsStory


class HackerNewsStoryFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name="author", lookup_expr="iexact")
    min_points = django_filters.NumberFilter(field_name="points", lookup_expr="gte")
    min_comments = django_filters.NumberFilter(field_name="comments", lookup_expr="gte")
    start_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = HackerNewsStory
        fields = ["author", "min_points", "min_comments", "start_date", "end_date"]