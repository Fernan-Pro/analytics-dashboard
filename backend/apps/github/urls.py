from django.urls import path

from github.views import GitHubTrendViewSet

urlpatterns = [
    path("trends/", GitHubTrendViewSet.as_view({"get": "list"})),
    path("trends/<int:pk>/", GitHubTrendViewSet.as_view({"get": "retrieve"})),
]