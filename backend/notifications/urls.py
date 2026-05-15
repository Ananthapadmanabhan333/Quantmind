from django.urls import path
from .views import WhatsAppWebhookView

app_name = "notifications"

urlpatterns = [
    path('whatsapp/webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
]
