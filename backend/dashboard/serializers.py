from rest_framework import serializers
from dashboard.models import Alert, AlertStatus, AuditLog, SystemMetrics
from transactions.serializers import TransactionSerializer


class AlertSerializer(serializers.ModelSerializer):
    transaction_details = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    resolved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = [
            "id",
            "transaction",
            "transaction_details",
            "user",
            "user_email",
            "alert_type",
            "severity",
            "status",
            "message",
            "details",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "resolution_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_transaction_details(self, obj):
        return {
            "id": str(obj.transaction.id),
            "amount": float(obj.transaction.amount),
            "merchant": obj.transaction.merchant,
            "fraud_score": obj.transaction.fraud_score,
            "risk_level": obj.transaction.risk_level,
        }

    def get_resolved_by_name(self, obj):
        if obj.resolved_by:
            return obj.resolved_by.full_name
        return None


class AlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["transaction", "alert_type", "severity", "message", "details"]


class AlertUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["status", "resolved_by", "resolution_notes"]


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_name",
            "action",
            "entity_type",
            "entity_id",
            "details",
            "ip_address",
            "created_at",
        ]

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.email
        return None


class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = [
            "id",
            "metric_name",
            "metric_value",
            "metric_unit",
            "tags",
            "created_at",
        ]


class DashboardStatsSerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
    total_volume = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    fraud_rate = serializers.FloatField()
    avg_risk_score = serializers.FloatField()
    high_risk_users = serializers.IntegerField()
    total_alerts = serializers.IntegerField()
    pending_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()


class RiskDistributionSerializer(serializers.Serializer):
    risk_level = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class FraudTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_transactions = serializers.IntegerField()
    flagged_transactions = serializers.IntegerField()
    blocked_transactions = serializers.IntegerField()
    fraud_rate = serializers.FloatField()
