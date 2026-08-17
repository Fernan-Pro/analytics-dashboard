from rest_framework import viewsets

from producthunt.filters import ProductHuntLaunchFilter
from producthunt.models import ProductHuntLaunch
from producthunt.serializers import ProductHuntLaunchSerializer


class ProductHuntLaunchViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/producthunt/launches/?start_date=&end_date=&min_votes=&ordering="""  # noqa: E501

    queryset = ProductHuntLaunch.objects.all()
    serializer_class = ProductHuntLaunchSerializer
    filterset_class = ProductHuntLaunchFilter
    ordering_fields = ["votes", "launch_date", "product_name"]
    ordering = ["-launch_date", "-votes"]