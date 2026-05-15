import logging
from django.db.models import Count, Avg, Sum, Max, Min, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from auth_system.models import User
from transactions.models import Transaction, RiskLevel, TransactionStatus
from users.models import RiskProfile, RiskSegment
from dashboard.models import Alert, AlertStatus, AlertSeverity, AuditLog
from .serializers import (
    AlertSerializer,
    AlertUpdateSerializer,
    DashboardStatsSerializer,
    RiskDistributionSerializer,
    AuditLogSerializer,
)

logger = logging.getLogger(__name__)


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        now = timezone.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        total_transactions = Transaction.objects.count()
        total_volume = Transaction.objects.aggregate(Sum("amount"))["amount__sum"] or 0

        total_users = User.objects.filter(is_active=True).count()
        active_users = (
            User.objects.filter(transactions__timestamp__gte=day_ago).distinct().count()
        )

        flagged = Transaction.objects.filter(status=TransactionStatus.FLAGGED).count()
        blocked = Transaction.objects.filter(status=TransactionStatus.BLOCKED).count()
        fraud_rate = (
            (flagged + blocked) / total_transactions * 100
            if total_transactions > 0
            else 0
        )

        avg_risk = (
            RiskProfile.objects.aggregate(Avg("overall_score"))["overall_score__avg"]
            or 50
        )

        high_risk_users = RiskProfile.objects.filter(
            Q(overall_score__gte=70) | Q(is_high_risk=True)
        ).count()

        total_alerts = Alert.objects.count()
        pending_alerts = Alert.objects.exclude(
            status__in=[AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE]
        ).count()
        critical_alerts = Alert.objects.filter(
            severity=AlertSeverity.CRITICAL,
            status__in=[AlertStatus.NEW, AlertStatus.INVESTIGATING],
        ).count()

        return Response(
            {
                "total_transactions": total_transactions,
                "total_volume": float(total_volume),
                "total_users": total_users,
                "active_users": active_users,
                "fraud_rate": round(fraud_rate, 2),
                "avg_risk_score": round(avg_risk, 2),
                "high_risk_users": high_risk_users,
                "total_alerts": total_alerts,
                "pending_alerts": pending_alerts,
                "critical_alerts": critical_alerts,
            }
        )

    @action(detail=False, methods=["get"])
    def risk_distribution(self, request):
        distribution = (
            Transaction.objects.values("risk_level")
            .annotate(count=Count("id"))
            .order_by("risk_level")
        )

        total = Transaction.objects.count()

        result = []
        for item in distribution:
            result.append(
                {
                    "risk_level": item["risk_level"],
                    "count": item["count"],
                    "percentage": round(item["count"] / total * 100, 2)
                    if total > 0
                    else 0,
                }
            )

        return Response(result)

    @action(detail=False, methods=["get"])
    def transaction_volume(self, request):
        days = int(request.query_params.get("days", 7))
        start_date = timezone.now() - timedelta(days=days)

        daily_volume = (
            Transaction.objects.filter(timestamp__gte=start_date)
            .extra(select={"date": "DATE(timestamp)"})
            .values("date")
            .annotate(volume=Sum("amount"), count=Count("id"))
            .order_by("date")
        )

        return Response(
            [
                {
                    "date": item["date"],
                    "volume": float(item["volume"]),
                    "count": item["count"],
                }
                for item in daily_volume
            ]
        )

    @action(detail=False, methods=["get"])
    def user_segments(self, request):
        segments = (
            RiskProfile.objects.values("segment")
            .annotate(count=Count("id"))
            .order_by("segment")
        )

        return Response(
            [{"segment": item["segment"], "count": item["count"]} for item in segments]
        )


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related("transaction", "user", "resolved_by")
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        filters.BaseFilterBackend,
    ]
    filterset_fields = ["status", "severity", "alert_type"]
    search_fields = ["message", "transaction__merchant", "user__email"]
    ordering_fields = ["created_at", "severity"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return AlertUpdateSerializer
        return AlertSerializer

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        resolution = request.data.get("resolution", "")
        is_false_positive = request.data.get("is_false_positive", False)

        alert.status = (
            AlertStatus.FALSE_POSITIVE if is_false_positive else AlertStatus.RESOLVED
        )
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = resolution
        alert.save()

        AuditLog.objects.create(
            user=request.user,
            action="resolve_alert",
            entity_type="alert",
            entity_id=alert.id,
            details={"alert_id": str(alert.id), "resolution": resolution},
            ip_address=self.get_client_ip(request),
        )

        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def investigate(self, request, pk=None):
        alert = self.get_object()
        alert.status = AlertStatus.INVESTIGATING
        alert.save()

        return Response(AlertSerializer(alert).data)

    @action(detail=False, methods=["get"])
    def active_alerts(self, request):
        alerts = self.get_queryset().exclude(
            status__in=[AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE]
        )[:50]
        return Response(AlertSerializer(alerts, many=True).data)

    @action(detail=False, methods=["get"])
    def critical_alerts(self, request):
        alerts = self.get_queryset().filter(
            severity=AlertSeverity.CRITICAL,
            status__in=[AlertStatus.NEW, AlertStatus.INVESTIGATING],
        )
        return Response(AlertSerializer(alerts, many=True).data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        summary = {
            "total": self.queryset.count(),
            "new": self.queryset.filter(status=AlertStatus.NEW).count(),
            "investigating": self.queryset.filter(
                status=AlertStatus.INVESTIGATING
            ).count(),
            "resolved": self.queryset.filter(status=AlertStatus.RESOLVED).count(),
            "false_positive": self.queryset.filter(
                status=AlertStatus.FALSE_POSITIVE
            ).count(),
            "by_severity": {},
            "by_type": {},
        }

        for severity in AlertSeverity.values:
            summary["by_severity"][severity] = self.queryset.filter(
                severity=severity,
                status__in=[AlertStatus.NEW, AlertStatus.INVESTIGATING],
            ).count()

        return Response(summary)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "entity_type", "user__email"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        user_id = self.request.query_params.get("user")
        action_type = self.request.query_params.get("action")
        entity_type = self.request.query_params.get("entity_type")

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action_type:
            queryset = queryset.filter(action=action_type)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)

        return queryset[:1000]
