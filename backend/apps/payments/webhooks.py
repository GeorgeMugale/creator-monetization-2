import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.payments.models import Payment
from apps.payments.models import PaymentWebhookLog as WebHook
from django.http import JsonResponse
from utils.exceptions import DuplicateTransaction
from apps.wallets.services.transaction_service import WalletTransactionService
from rest_framework.views import APIView

User = get_user_model()


class WebhookAPIView(APIView):
    """Handles pawapay deposit Callback requests"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        deposit_id = payload.get("depositId")
        status = payload.get("status").lower()
        external_id = payload.get("providerTransactionId")

        if not all([deposit_id, status]):
            return JsonResponse({"error": "Invalid payload"}, status=400)

        status = status.lower()

        # IDEMPOTENCY CHECK (fast path) - check for duplicate based on external_id
        if external_id and WebHook.objects.filter(external_id=external_id).exists():
            return JsonResponse({"message": "Duplicate callback ignored"}, status=200)
        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(id=deposit_id)
                # Dont update status if pending/submitted/accepted to
                # avoid overwriting final state
                skip_statuses = [
                    "pending",
                    "submitted",
                    "accepted",
                    "processing",
                    "in_reconciliation",
                ]
                if status in skip_statuses:
                    status = payment.status
                payment.status = status
                payment.save()

                # Create webhook log ONCE
                WebHook.objects.create(
                    parsed_payload=payload,
                    event_type=f"deposit.{status}",
                    payment=payment,
                    provider=payment.provider,
                    external_id=external_id,
                )
                if status == "completed" and payment.wallet is not None:
                    try:
                        WalletTransactionService.cash_in(
                            wallet=payment.wallet,
                            amount=payment.amount,
                            payment=payment,
                            reference=external_id,
                        )
                    except DuplicateTransaction:
                        pass

        except Payment.DoesNotExist:
            return JsonResponse({"status": "NOT_FOUND"}, status=404)

        except Exception:
            # If unique constraint triggered by race condition
            return JsonResponse({"message": "Duplicate callback ignored"}, status=200)
        return JsonResponse({"message": "Callback processed"}, status=200)
