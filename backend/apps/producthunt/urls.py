from django.urls import path

from producthunt.views import ProductHuntLaunchViewSet

urlpatterns = [
    path("launches/", ProductHuntLaunchViewSet.as_view({"get": "list"})),
    path("launches/<int:pk>/", ProductHuntLaunchViewSet.as_view({"get": "retrieve"})),
]