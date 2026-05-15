import logging
import time
from celery import shared_task
from django.conf import settings
from .models import AlertLog, DeliveryStatus
from transactions.models import Transaction

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_whatsapp_alert_task(self, transaction_id, phone_number, message_body):
    """
    Asynchronous task to send WhatsApp message with retry logic.
    """
    from .services import WhatsAppService
    
    try:
        service = WhatsAppService()
        result = service.send_message(phone_number, message_body)
        
        if result["status"] == "success":
            # Update log status
            AlertLog.objects.filter(transaction_id=transaction_id).update(
                delivery_status=DeliveryStatus.SENT,
                message_sid=result["sid"]
            )
            # Update transaction
            Transaction.objects.filter(id=transaction_id).update(alert_sent=True)
            return f"Alert sent to {phone_number}"
        else:
            raise Exception(result.get("error", "Unknown error"))
            
    except Exception as exc:
        logger.error(f"Error sending WhatsApp alert for Tx {transaction_id}: {exc}")
        # Retry with exponential backoff or fixed delay
        raise self.retry(exc=exc)

@shared_task(ignore_result=True)
def process_webhook_response_task(from_number, body):
    """
    Task to process the webhook response asynchronously.
    """
    from .services import CommandProcessor
    CommandProcessor.process_webhook(from_number, body)
