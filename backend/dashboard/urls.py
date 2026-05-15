from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, AlertViewSet, AuditLogViewSet

router = DefaultRouter()
router.register("alerts", AlertViewSet, basename="alert")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", DashboardViewSet.as_view({"get": "stats"}), name="dashboard-stats"),
    path(
        "risk-distribution/",
        DashboardViewSet.as_view({"get": "risk_distribution"}),
        name="risk-distribution",
    ),
    path(
        "transaction-volume/",
        DashboardViewSet.as_view({"get": "transaction_volume"}),
        name="transaction-volume",
    ),
    path(
        "user-segments/",
        DashboardViewSet.as_view({"get": "user_segments"}),
        name="user-segments",
    ),
    path("", include(router.urls)),
]
