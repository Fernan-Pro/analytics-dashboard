from django.urls import path

from hackernews.views import HackerNewsStoryViewSet

urlpatterns = [
    path("stories/", HackerNewsStoryViewSet.as_view({"get": "list"})),
    path("stories/<int:pk>/", HackerNewsStoryViewSet.as_view({"get": "retrieve"})),
]