from celery import shared_task
from apps.wallets.models import Wallet
from apps.payments.services.payout_orchestrator import PayoutOrchestrator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def auto_payout_wallets():
    # get superuser
    system_user = User.objects.filter(is_superuser=True).first()
    for wallet in Wallet.objects.filter(balance__gt=0, is_verified=True):
        PayoutOrchestrator.initiate_payout(
            wallet=wallet,
            initiated_by=system_user,  # System initiated
        )