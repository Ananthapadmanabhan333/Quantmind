from rest_framework import serializers
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from auth_system.serializers import UserSerializer
from auth_system.models import User
from .models import RiskProfile, RiskSegment, UserSegment, UserBehavior


class RiskProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = RiskProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "overall_score",
            "fraud_probability",
            "last_transaction_count",
            "last_24h_volume",
            "last_7d_volume",
            "avg_transaction_amount",
            "avg_transaction_frequency",
            "segment",
            "transaction_count",
            "total_volume",
            "flags",
            "last_flag_reason",
            "is_high_risk",
            "is_monitored",
            "updated_at",
            "created_at",
        ]
        read_only_fields = ["id", "updated_at", "created_at"]

    def get_user_name(self, obj):
        return obj.user.full_name


class UserSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSegment
        fields = [
            "id",
            "segment_name",
            "description",
            "cluster_id",
            "avg_transaction_amount",
            "avg_transaction_frequency",
            "total_users",
            "avg_risk_score",
            "characteristics",
            "created_at",
        ]


class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = [
            "id",
            "user",
            "metric_name",
            "metric_value",
            "period_start",
            "period_end",
            "created_at",
        ]


class UserWithRiskSerializer(serializers.ModelSerializer):
    risk_profile = RiskProfileSerializer(read_only=True)
    transaction_count = serializers.SerializerMethodField()
    total_volume = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "created_at",
            "last_login_at",
            "risk_profile",
            "transaction_count",
            "total_volume",
        ]

    def get_transaction_count(self, obj):
        return obj.transactions.count()

    def get_total_volume(self, obj):
        total = obj.transactions.aggregate(Sum("amount"))["amount__sum"]
        return float(total or 0)


class UserListSerializer(serializers.ModelSerializer):
    risk_score = serializers.SerializerMethodField()
    segment = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "risk_score",
            "segment",
            "transaction_count",
            "created_at",
        ]

    def get_risk_score(self, obj):
        if hasattr(obj, "risk_profile"):
            return obj.risk_profile.overall_score
        return 50.0

    def get_segment(self, obj):
        if hasattr(obj, "risk_profile"):
            return obj.risk_profile.segment
        return "NEW"

    def get_transaction_count(self, obj):
        return obj.transactions.count()


class UserDetailSerializer(serializers.ModelSerializer):
    risk_profile = RiskProfileSerializer(read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    behavior_summary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "phone",
            "department",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
            "last_login_at",
            "risk_profile",
            "recent_transactions",
            "behavior_summary",
        ]

    def get_recent_transactions(self, obj):
        from transactions.serializers import TransactionSerializer

        transactions = obj.transactions.all()[:10]
        return TransactionSerializer(transactions, many=True).data

    def get_behavior_summary(self, obj):
        return {
            "total_transactions": obj.transactions.count(),
            "avg_amount": float(
                obj.transactions.aggregate(Avg("amount"))["amount__avg"] or 0
            ),
            "preferred_merchants": list(
                obj.transactions.values("merchant")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
                .values("merchant", "count")
            ),
            "preferred_categories": list(
                obj.transactions.values("merchant_category")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
                .values("merchant_category", "count")
            ),
        }
