import uuid
from django.db import models
from django.conf import settings


class TransactionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FLAGGED = "FLAGGED", "Flagged"
    BLOCKED = "BLOCKED", "Blocked"
    INVESTIGATING = "INVESTIGATING", "Under Investigation"


class TransactionType(models.TextChoices):
    DEBIT = "DEBIT", "Debit"
    CREDIT = "CREDIT", "Credit"
    TRANSFER = "TRANSFER", "Transfer"
    WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
    DEPOSIT = "DEPOSIT", "Deposit"


class RiskLevel(models.TextChoices):
    LOW = "LOW", "Low Risk"
    MEDIUM = "MEDIUM", "Medium Risk"
    HIGH = "HIGH", "High Risk"
    CRITICAL = "CRITICAL", "Critical Risk"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices, default=TransactionType.DEBIT
    )
    merchant = models.CharField(max_length=255)
    merchant_category = models.CharField(max_length=100, blank=True, null=True)
    merchant_country = models.CharField(max_length=3, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(default=models.functions.Now)
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    fraud_score = models.FloatField(default=0.0)
    risk_level = models.CharField(
        max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW
    )
    fraud_probability = models.FloatField(default=0.0)
    is_anomaly = models.BooleanField(default=False)
    alert_sent = models.BooleanField(default=False)
    rule_triggers = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["status", "-timestamp"]),
            models.Index(fields=["risk_level", "-timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.merchant}"

    @property
    def formatted_amount(self):
        return f"${self.amount:,.2f}"

    @property
    def is_high_risk(self):
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    @property
    def is_flagged(self):
        return self.status in [TransactionStatus.FLAGGED, TransactionStatus.BLOCKED]
