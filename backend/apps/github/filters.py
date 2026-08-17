import django_filters

from github.models import GitHubTrend


class GitHubTrendFilter(django_filters.FilterSet):
    language = django_filters.CharFilter(field_name="language", lookup_expr="iexact")
    start_date = django_filters.DateFilter(field_name="trending_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="trending_date", lookup_expr="lte")
    min_stars = django_filters.NumberFilter(field_name="stars", lookup_expr="gte")

    class Meta:
        model = GitHubTrend
        fields = ["language", "start_date", "end_date", "min_stars"]