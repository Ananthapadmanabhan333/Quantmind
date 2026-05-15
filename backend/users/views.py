import logging
import requests
from django.conf import settings
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta
from auth_system.models import User
from .models import RiskProfile, RiskSegment, UserSegment, UserBehavior
from .serializers import (
    RiskProfileSerializer,
    UserSegmentSerializer,
    UserBehaviorSerializer,
    UserWithRiskSerializer,
    UserListSerializer,
    UserDetailSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering_fields = ["created_at", "email"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("risk_profile")

        risk_score_min = self.request.query_params.get("risk_score_min")
        risk_score_max = self.request.query_params.get("risk_score_max")
        segment = self.request.query_params.get("segment")

        if risk_score_min or risk_score_max:
            queryset = queryset.filter(risk_profile__isnull=False)
            if risk_score_min:
                queryset = queryset.filter(
                    risk_profile__overall_score__gte=risk_score_min
                )
            if risk_score_max:
                queryset = queryset.filter(
                    risk_profile__overall_score__lte=risk_score_max
                )

        if segment:
            queryset = queryset.filter(risk_profile__segment=segment)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self._update_risk_profile(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _update_risk_profile(self, user):
        profile, created = RiskProfile.objects.get_or_create(user=user)

        now = timezone.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        transactions = user.transactions.all()

        profile.transaction_count = transactions.count()
        profile.total_volume = transactions.aggregate(Sum("amount"))["amount__sum"] or 0

        profile.last_24h_volume = (
            transactions.filter(timestamp__gte=day_ago).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        profile.last_7d_volume = (
            transactions.filter(timestamp__gte=week_ago).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        profile.avg_transaction_amount = (
            transactions.aggregate(Avg("amount"))["amount__avg"] or 0
        )

        first_tx = transactions.order_by("timestamp").first()
        if first_tx:
            days_active = (now - first_tx.timestamp).days or 1
            profile.avg_transaction_frequency = profile.transaction_count / days_active

        profile.last_transaction_count = transactions.filter(
            timestamp__gte=day_ago
        ).count()

        flagged_count = transactions.filter(status__in=["FLAGGED", "BLOCKED"]).count()

        if profile.transaction_count > 0:
            fraud_rate = flagged_count / profile.transaction_count
            profile.fraud_probability = min(fraud_rate * 2, 1.0)

        ml_score = self._get_ml_risk_score(user)

        profile.overall_score = self._calculate_risk_score(profile, ml_score)
        profile.segment = self._determine_segment(profile.overall_score)
        profile.is_high_risk = profile.overall_score >= 80

        profile.save()

        return profile

    def _get_ml_risk_score(self, user):
        try:
            ml_url = getattr(settings, "ML_SERVICE_URL", "http://localhost:8001")
            transactions = user.transactions.all()[:100]

            features = {
                "user_id": str(user.id),
                "transaction_count": user.transactions.count(),
                "avg_amount": float(
                    user.transactions.aggregate(Avg("amount"))["amount__avg"] or 0
                ),
                "total_volume": float(
                    user.transactions.aggregate(Sum("amount"))["amount__sum"] or 0
                ),
                "flagged_count": user.transactions.filter(
                    status__in=["FLAGGED", "BLOCKED"]
                ).count(),
            }

            response = requests.post(
                f"{ml_url}/ml/risk/score", json=features, timeout=5
            )
            if response.status_code == 200:
                return response.json().get("risk_score", 50)
        except Exception as e:
            logger.warning(f"ML risk scoring unavailable: {e}")
        return 50

    def _calculate_risk_score(self, profile: RiskProfile, ml_score: float) -> float:
        base_score = 50

        fraud_weight = profile.fraud_probability * 30
        volume_weight = min(float(profile.last_24h_volume) / 10000 * 10, 10)
        frequency_weight = min(profile.last_transaction_count * 2, 10)
        ml_weight = ml_score * 0.4

        score = (
            base_score
            + fraud_weight
            + volume_weight
            + frequency_weight
            + ml_weight
            - 10
        )

        return max(0, min(100, score))

    def _determine_segment(self, score: float) -> str:
        if score >= 80:
            return RiskSegment.HIGH_RISK
        elif score >= 60:
            return RiskSegment.SUSPICIOUS
        elif score >= 40:
            return RiskSegment.REGULAR
        return RiskSegment.NEW

    @action(detail=True, methods=["get"])
    def risk_profile(self, request, pk=None):
        user = self.get_object()
        profile, created = RiskProfile.objects.get_or_create(user=user)
        self._update_risk_profile(user)
        profile.refresh_from_db()
        serializer = RiskProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def behavior(self, request, pk=None):
        user = self.get_object()
        transactions = user.transactions.all()

        now = timezone.now()
        daily_volume = {}
        hourly_distribution = {}
        category_distribution = {}

        for tx in transactions:
            day = tx.timestamp.date()
            daily_volume[day] = daily_volume.get(day, 0) + float(tx.amount)

            hour = tx.timestamp.hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1

            if tx.merchant_category:
                category_distribution[tx.merchant_category] = (
                    category_distribution.get(tx.merchant_category, 0) + 1
                )

        return Response(
            {
                "daily_volume": daily_volume,
                "hourly_distribution": hourly_distribution,
                "category_distribution": category_distribution,
                "statistics": {
                    "total_transactions": transactions.count(),
                    "avg_amount": float(
                        transactions.aggregate(Avg("amount"))["amount__avg"] or 0
                    ),
                    "max_amount": float(
                        transactions.aggregate(Max("amount"))["amount__max"] or 0
                    ),
                    "min_amount": float(
                        transactions.aggregate(Min("amount"))["amount__min"] or 0
                    ),
                },
            }
        )

    @action(detail=False, methods=["get"])
    def segments(self, request):
        segments = UserSegment.objects.all()
        serializer = UserSegmentSerializer(segments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def high_risk(self, request):
        profiles = RiskProfile.objects.filter(
            Q(overall_score__gte=70) | Q(is_high_risk=True)
        ).select_related("user")

        return Response(RiskProfileSerializer(profiles, many=True).data)


class RiskProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskProfile.objects.select_related("user")
    serializer_class = RiskProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__email", "user__username"]
    ordering_fields = ["overall_score", "updated_at"]
    ordering = ["-overall_score"]

    def get_queryset(self):
        queryset = super().get_queryset()

        segment = self.request.query_params.get("segment")
        min_score = self.request.query_params.get("min_score")
        max_score = self.request.query_params.get("max_score")
        is_high_risk = self.request.query_params.get("is_high_risk")

        if segment:
            queryset = queryset.filter(segment=segment)
        if min_score:
            queryset = queryset.filter(overall_score__gte=min_score)
        if max_score:
            queryset = queryset.filter(overall_score__lte=max_score)
        if is_high_risk == "true":
            queryset = queryset.filter(is_high_risk=True)

        return queryset


class UserSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserSegment.objects.all()
    serializer_class = UserSegmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "segment_name"

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        try:
            ml_url = getattr(settings, "ML_SERVICE_URL", "http://localhost:8001")
            response = requests.post(
                f"{ml_url}/ml/segment/refresh", json={}, timeout=30
            )
            if response.status_code == 200:
                return Response({"status": "Segments refreshed successfully"})
        except Exception as e:
            logger.error(f"Segment refresh failed: {e}")

        return Response(
            {"error": "Failed to refresh segments"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
