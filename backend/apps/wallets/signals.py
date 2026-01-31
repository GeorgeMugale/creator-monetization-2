from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.creators.models import CreatorProfile
from apps.wallets.models.payment_related import Wallet

@receiver(post_save, sender=CreatorProfile)
def create_wallet_for_creator(sender, instance, created, **kwargs):
    """Create a Wallet when a CreatorProfile is created."""
    if created:
        Wallet.objects.get_or_create(creator=instance)