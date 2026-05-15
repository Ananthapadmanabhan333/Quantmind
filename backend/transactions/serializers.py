from rest_framework import serializers
from django.utils import timezone
from .models import Transaction, TransactionStatus, TransactionType, RiskLevel
from auth_system.serializers import UserSerializer


class TransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    formatted_amount = serializers.ReadOnlyField()
    is_high_risk = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "amount",
            "currency",
            "transaction_type",
            "merchant",
            "merchant_category",
            "merchant_country",
            "location",
            "latitude",
            "longitude",
            "ip_address",
            "device_id",
            "timestamp",
            "status",
            "fraud_score",
            "risk_level",
            "fraud_probability",
            "is_anomaly",
            "rule_triggers",
            "metadata",
            "notes",
            "formatted_amount",
            "is_high_risk",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "fraud_score",
            "risk_level",
            "fraud_probability",
            "is_anomaly",
            "rule_triggers",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        return obj.user.full_name


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "user",
            "amount",
            "currency",
            "transaction_type",
            "merchant",
            "merchant_category",
            "merchant_country",
            "location",
            "latitude",
            "longitude",
            "ip_address",
            "device_id",
            "metadata",
        ]

    def create(self, validated_data):
        validated_data["status"] = TransactionStatus.PENDING
        return super().create(validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["status", "notes", "risk_level"]


class TransactionStatsSerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
    total_volume = serializers.DecimalField(max_digits=14, decimal_places=2)
    flagged_count = serializers.IntegerField()
    blocked_count = serializers.IntegerField()
    fraud_rate = serializers.FloatField()
    avg_fraud_score = serializers.FloatField()
    high_risk_count = serializers.IntegerField()


class RiskLevelDistributionSerializer(serializers.Serializer):
    risk_level = serializers.CharField()
    count = serializers.IntegerField()
    volume = serializers.DecimalField(max_digits=14, decimal_places=2)
