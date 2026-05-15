import logging
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from twilio.request_validator import RequestValidator
from .tasks import process_webhook_response_task

logger = logging.getLogger(__name__)

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        Receives inbound messages from Twilio with signature validation.
        """
        # Get signature from header
        signature = request.headers.get('X-Twilio-Signature', '')
        
        # Build URL for validation
        scheme = request.scheme
        host = request.get_host()
        url = f"{scheme}://{host}{request.path}"
        
        # In production/deployment with ngrok or standard SSL
        # We validate the signature using the AUTH_TOKEN
        validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        
        # Twilio sends data as form-encoded
        data = request.POST.dict()

        # Validate request (only check if not in mock/dev mode without real token)
        if settings.ENVIRONMENT == 'production':
            if not validator.validate(url, data, signature):
                logger.warning(f"Invalid Twilio signature rejected for URL: {url}")
                return HttpResponseForbidden("Invalid signature")

        from_number = data.get('From', '')
        body = data.get('Body', '')

        if not from_number or not body:
            return HttpResponse("Missing data", status=400)

        logger.info(f"Accepted WhatsApp webhook from {from_number}")
        
        # Offload processing to a background task to respond instantly to Twilio
        process_webhook_response_task.delay(from_number, body)
        
        # Return empty TwiML response
        return HttpResponse('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', content_type='text/xml')
