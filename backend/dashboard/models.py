import uuid
from django.db import models
from django.conf import settings


class AlertType(models.TextChoices):
    FRAUD_DETECTED = "FRAUD_DETECTED", "Fraud Detected"
    ANOMALY = "ANOMALY", "Anomaly Detected"
    HIGH_RISK = "HIGH_RISK", "High Risk"
    LOCATION_ANOMALY = "LOCATION_ANOMALY", "Location Anomaly"
    RAPID_TRANSACTION = "RAPID_TRANSACTION", "Rapid Transaction"
    LARGE_AMOUNT = "LARGE_AMOUNT", "Large Amount"
    RULE_TRIGGERED = "RULE_TRIGGERED", "Rule Triggered"


class AlertSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class AlertStatus(models.TextChoices):
    NEW = "NEW", "New"
    INVESTIGATING = "INVESTIGATING", "Investigating"
    RESOLVED = "RESOLVED", "Resolved"
    FALSE_POSITIVE = "FALSE_POSITIVE", "False Positive"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD", "Confirmed Fraud"


class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        "transactions.Transaction", on_delete=models.CASCADE, related_name="alerts"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="alerts",
    )
    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    severity = models.CharField(max_length=20, choices=AlertSeverity.choices)
    status = models.CharField(
        max_length=20, choices=AlertStatus.choices, default=AlertStatus.NEW
    )
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alerts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["severity", "-created_at"]),
            models.Index(fields=["alert_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.alert_type} - {self.severity} - {self.transaction.id}"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]


class SystemMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=20, blank=True)
    tags = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_metrics"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["metric_name", "-created_at"]),
        ]
