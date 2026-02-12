from django.urls import path
from apps.payments.views import  DepositAPIView
from apps.payments.webhooks import  WebhookAPIView

app_name = "payments"

urlpatterns = [
    path("deposits/<uuid:wallet_id>/", DepositAPIView.as_view(), name="deposit"),
    path("webhook/", WebhookAPIView.as_view(), name="webhook"),
]