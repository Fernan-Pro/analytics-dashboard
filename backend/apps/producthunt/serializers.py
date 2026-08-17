from rest_framework import serializers

from producthunt.models import ProductHuntLaunch


class ProductHuntLaunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHuntLaunch
        fields = [
            "id",
            "product_name",
            "tagline",
            "votes",
            "url",
            "launch_date",
            "created_at",
        ]
        read_only_fields = fields