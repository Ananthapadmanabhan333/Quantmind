import uuid
from django.db import models
from django.conf import settings


class RiskSegment(models.TextChoices):
    PREMIUM = "PREMIUM", "Premium"
    REGULAR = "REGULAR", "Regular"
    SUSPICIOUS = "SUSPICIOUS", "Suspicious"
    HIGH_RISK = "HIGH_RISK", "High Risk"
    NEW = "NEW", "New User"


class RiskProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="risk_profile"
    )
    overall_score = models.FloatField(default=50.0)
    fraud_probability = models.FloatField(default=0.0)
    last_transaction_count = models.IntegerField(default=0)
    last_24h_volume = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_7d_volume = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    avg_transaction_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    avg_transaction_frequency = models.FloatField(default=0)
    segment = models.CharField(
        max_length=20, choices=RiskSegment.choices, default=RiskSegment.NEW
    )
    transaction_count = models.IntegerField(default=0)
    total_volume = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    flags = models.JSONField(default=dict)
    last_flag_reason = models.CharField(max_length=255, blank=True, null=True)
    is_high_risk = models.BooleanField(default=False)
    is_monitored = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "risk_profiles"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Risk Profile: {self.user.email} - Score: {self.overall_score}"


class UserSegment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    segment_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    cluster_id = models.IntegerField()
    avg_transaction_amount = models.DecimalField(max_digits=12, decimal_places=2)
    avg_transaction_frequency = models.FloatField()
    total_users = models.IntegerField(default=0)
    avg_risk_score = models.FloatField(default=50.0)
    characteristics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_segments"
        ordering = ["cluster_id"]

    def __str__(self):
        return self.segment_name


class UserBehavior(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="behaviors"
    )
    metric_name = models.CharField(max_length=100)
    metric_value = models.JSONField()
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_behaviors"
        ordering = ["-period_end"]
        indexes = [
            models.Index(fields=["user", "metric_name"]),
        ]
