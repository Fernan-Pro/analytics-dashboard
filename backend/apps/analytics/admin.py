from django.contrib import admin

from analytics.models import MetricSnapshot


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ("metric_type", "value", "timestamp")
    list_filter = ("metric_type",)
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)