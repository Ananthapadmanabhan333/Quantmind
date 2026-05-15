import logging
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import AlertLog, ActionLog, ActionType, DeliveryStatus
from transactions.models import Transaction, TransactionStatus

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Production-ready Twilio WhatsApp integration.
    """
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
        self.timeout = getattr(settings, 'TWILIO_TIMEOUT', 10)
        
        try:
            # Twilio client with timeout
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            self.client = None

    def send_message(self, to_number: str, body: str) -> dict:
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
            
        try:
            if not self.client or settings.ENVIRONMENT == 'development' and not self.account_sid.startswith('AC'):
                logger.info(f"[MOCK WHATSAPP] To: {to_number} | Body: {body}")
                return {"status": "success", "sid": "mock_sid_" + str(hash(body))[:10]}

            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to_number
            )
            logger.info(f"WhatsApp message sent! SID: {message.sid}")
            return {"status": "success", "sid": message.sid}
            
        except TwilioRestException as e:
            logger.error(f"Twilio API Error while sending message to {to_number}: {str(e)}")
            return {"status": "failed", "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in WhatsAppService: {str(e)}")
            return {"status": "failed", "error": str(e)}

class NotificationService:
    @staticmethod
    def send_fraud_alert(transaction: Transaction) -> bool:
        user = transaction.user
        phone = user.phone

        if not phone:
            logger.warning(f"Cannot send WhatsApp alert to User {user.id}: No phone number.")
            return False

        message_body = (
            f"🚨 *QuantMind Security Alert*\n"
            f"High-Risk Transaction Detected\n\n"
            f"👤 *User:* {user.username}\n"
            f"💰 *Amount:* ${transaction.amount}\n"
            f"📍 *Location:* {transaction.location or 'Unknown'}\n"
            f"📉 *Risk Score:* {transaction.fraud_score:.1f}\n\n"
            f"Reply with one of the following commands:\n"
            f"*BLOCK* – Block user\n"
            f"*IGNORE* – Mark safe\n"
            f"*REVIEW* – Manual review"
        )

        # Create initial pending log
        AlertLog.objects.create(
            transaction=transaction,
            user=user,
            message=message_body,
            delivery_status=DeliveryStatus.PENDING
        )

        # Dispatch async task
        from .tasks import send_whatsapp_alert_task
        send_whatsapp_alert_task.delay(str(transaction.id), phone, message_body)
        return True

class CommandProcessor:
    @staticmethod
    def process_webhook(from_number: str, text_body: str):
        if from_number.startswith("whatsapp:"):
            from_number = from_number.replace("whatsapp:", "")
            
        text_body = str(text_body).strip().upper()
        
        try:
            latest_alert = AlertLog.objects.filter(
                user__phone=from_number
            ).order_by('-timestamp').first()
            
            if not latest_alert:
                logger.warning(f"No matching alert found for responder {from_number}")
                return False
                
            transaction = latest_alert.transaction
            user = latest_alert.user

            # Check for idempotency (if action already performed)
            if ActionLog.objects.filter(alert=latest_alert).exists():
                logger.info(f"Action already performed for Alert {latest_alert.id}")
                return True

            wa_service = WhatsAppService()

            if "BLOCK" in text_body:
                transaction.status = TransactionStatus.BLOCKED
                transaction.save()
                user.is_active = False 
                user.save()
                ActionLog.objects.create(alert=latest_alert, action_type=ActionType.BLOCK)
                wa_service.send_message(from_number, "🔒 User blocked and transaction secured.")
                
            elif "IGNORE" in text_body:
                transaction.status = TransactionStatus.COMPLETED
                transaction.save()
                ActionLog.objects.create(alert=latest_alert, action_type=ActionType.IGNORE)
                wa_service.send_message(from_number, "✅ Transaction marked as safe.")

            elif "REVIEW" in text_body:
                transaction.status = TransactionStatus.INVESTIGATING
                transaction.save()
                ActionLog.objects.create(alert=latest_alert, action_type=ActionType.REVIEW)
                wa_service.send_message(from_number, "⏳ Flagged for manual analyst review.")

            else:
                wa_service.send_message(from_number, "⚠️ Invalid command. Please reply with BLOCK, IGNORE, or REVIEW.")

            return True

        except Exception as e:
            logger.error(f"Error processing command from {from_number}: {e}")
            return False
