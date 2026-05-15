import uuid
from django.db import models
from django.conf import settings

class DeliveryStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    DELIVERED = "DELIVERED", "Delivered"
    FAILED = "FAILED", "Failed"

class ActionType(models.TextChoices):
    BLOCK = "BLOCK", "Block User"
    IGNORE = "IGNORE", "Ignore Transaction"
    REVIEW = "REVIEW", "Flag for Review"

class AlertLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        'transactions.Transaction', on_delete=models.CASCADE, related_name='alert_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alert_logs'
    )
    message = models.TextField()
    delivery_status = models.CharField(
        max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING
    )
    message_sid = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alert_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Alert for Tx {self.transaction.id} to {self.user.email}"

class ActionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(
        AlertLog, on_delete=models.CASCADE, related_name='actions'
    )
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "action_logs"
        ordering = ["-performed_at"]

    def __str__(self):
        return f"Action {self.action_type} for Alert {self.alert.id}"
