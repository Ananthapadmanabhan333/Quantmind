from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RiskProfileViewSet, UserSegmentViewSet

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "profiles/", RiskProfileViewSet.as_view({"get": "list"}), name="risk-profiles"
    ),
    path(
        "segments/", UserSegmentViewSet.as_view({"get": "list"}), name="user-segments"
    ),
]
