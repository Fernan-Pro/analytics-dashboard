from django.urls import path

from analytics.views import MetricsSnapshotView, admin_fetch, export_csv

urlpatterns = [
    path("metrics/snapshot/", MetricsSnapshotView.as_view()),
    path("export/csv/", export_csv),
    path("admin/fetch/", admin_fetch),
]