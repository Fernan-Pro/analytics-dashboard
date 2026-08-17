from rest_framework import serializers

from analytics.models import MetricSnapshot


class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = ["metric_type", "value", "timestamp"]
        read_only_fields = fields