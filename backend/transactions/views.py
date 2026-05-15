import logging
import requests
from django.conf import settings
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from transactions.models import Transaction, RiskLevel, TransactionStatus
from transactions.serializers import (
    TransactionSerializer,
    TransactionCreateSerializer,
    TransactionUpdateSerializer,
    TransactionStatsSerializer,
)
from transactions.fraud_rules import evaluate_transaction

logger = logging.getLogger(__name__)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related("user")
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "risk_level", "transaction_type", "user"]
    search_fields = ["merchant", "location", "user__email"]
    ordering_fields = ["timestamp", "amount", "fraud_score", "risk_level"]
    ordering = ["-timestamp"]

    def get_serializer_class(self):
        if self.action == "create":
            return TransactionCreateSerializer
        if self.action in ["update", "partial_update"]:
            return TransactionUpdateSerializer
        return TransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        min_amount = self.request.query_params.get("min_amount")
        max_amount = self.request.query_params.get("max_amount")

        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        self._process_transaction(transaction)

        return Response(
            TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED
        )

    def _process_transaction(self, transaction):
        logger.info(f"Processing transaction {transaction.id}")

        rule_result = evaluate_transaction(transaction)
        transaction.rule_triggers = rule_result.get("rules_triggered", [])

        ml_result = self._get_ml_prediction(transaction)

        if ml_result:
            transaction.fraud_probability = ml_result.get("fraud_probability", 0)
            transaction.is_anomaly = ml_result.get("is_anomaly", False)

        fraud_score = self._calculate_fraud_score(
            rule_result.get("rule_score", 0), transaction.fraud_probability * 100
        )
        transaction.fraud_score = fraud_score
        transaction.risk_level = self._get_risk_level(fraud_score)

        if fraud_score > 90:
            transaction.status = TransactionStatus.BLOCKED
        elif fraud_score > 70:
            transaction.status = TransactionStatus.FLAGGED

        transaction.save()

        self._trigger_alerts(transaction, rule_result)

        logger.info(
            f"Transaction {transaction.id} processed - Fraud Score: {fraud_score}, Risk: {transaction.risk_level}"
        )

    def _get_ml_prediction(self, transaction):
        try:
            ml_url = getattr(settings, "ML_SERVICE_URL", "http://localhost:8001")
            response = requests.post(
                f"{ml_url}/ml/fraud/predict",
                json={
                    "amount": float(transaction.amount),
                    "transaction_type": transaction.transaction_type,
                    "merchant_category": transaction.merchant_category or "UNKNOWN",
                    "hour": transaction.timestamp.hour,
                    "day_of_week": transaction.timestamp.weekday(),
                    "location": transaction.location or "UNKNOWN",
                },
                timeout=5,
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"ML service unavailable: {e}")
        return None

    def _calculate_fraud_score(self, rule_score: float, ml_score: float) -> float:
        return min((rule_score * 0.6) + (ml_score * 0.4), 100)

    def _get_risk_level(self, score: float) -> str:
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _trigger_alerts(self, transaction, rule_result):
        if transaction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            from dashboard.models import Alert, AlertType, AlertSeverity

            Alert.objects.create(
                transaction=transaction,
                alert_type=AlertType.FRAUD_DETECTED
                if transaction.fraud_score > 70
                else AlertType.HIGH_RISK,
                severity=AlertSeverity.HIGH
                if transaction.risk_level == RiskLevel.CRITICAL
                else AlertSeverity.MEDIUM,
                message=f"Transaction flagged - Score: {transaction.fraud_score:.1f}, Rules: {len(transaction.rule_triggers)}",
            )
            
            # Send WhatsApp Notification to user if fraud_score >= configured threshold
            from django.conf import settings
            if transaction.fraud_score >= getattr(settings, 'WHATSAPP_ALERT_THRESHOLD', 80):
                try:
                    from notifications.services import NotificationService
                    NotificationService.send_fraud_alert(transaction)
                    logger.info(f"WhatsApp alert dispatched for transaction {transaction.id}")
                except Exception as e:
                    logger.error(f"Failed to push WhatsApp alert: {e}")

    @action(detail=False, methods=["get"])
    def stats(self, request):
        queryset = self.get_queryset()

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total = queryset.count()
        total_volume = queryset.aggregate(Sum("amount"))["amount__sum"] or 0
        flagged = queryset.filter(status=TransactionStatus.FLAGGED).count()
        blocked = queryset.filter(status=TransactionStatus.BLOCKED).count()
        high_risk = queryset.filter(
            risk_level__in=[RiskLevel.HIGH, RiskLevel.CRITICAL]
        ).count()

        avg_fraud = queryset.aggregate(Avg("fraud_score"))["fraud_score__avg"] or 0

        fraud_rate = (flagged + blocked) / total * 100 if total > 0 else 0

        return Response(
            {
                "total_transactions": total,
                "total_volume": float(total_volume),
                "flagged_count": flagged,
                "blocked_count": blocked,
                "fraud_rate": round(fraud_rate, 2),
                "avg_fraud_score": round(avg_fraud, 2),
                "high_risk_count": high_risk,
            }
        )

    @action(detail=False, methods=["get"])
    def feed(self, request):
        limit = int(request.query_params.get("limit", 50))
        transactions = self.get_queryset()[:limit]
        return Response(TransactionSerializer(transactions, many=True).data)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        transaction = self.get_object()
        new_status = request.data.get("status")

        if new_status in dict(TransactionStatus.choices):
            transaction.status = new_status
            transaction.save()
            return Response(TransactionSerializer(transaction).data)

        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
