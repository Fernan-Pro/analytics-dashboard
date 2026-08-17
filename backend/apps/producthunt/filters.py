import django_filters

from producthunt.models import ProductHuntLaunch


class ProductHuntLaunchFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="launch_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="launch_date", lookup_expr="lte")
    min_votes = django_filters.NumberFilter(field_name="votes", lookup_expr="gte")

    class Meta:
        model = ProductHuntLaunch
        fields = ["start_date", "end_date", "min_votes"]