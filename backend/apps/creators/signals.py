from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.creators.models import CreatorProfile
from apps.creators.tasks import send_welcome_email_task, welcome_early_adopter_task

User = get_user_model()

@receiver(post_save, sender=User)
def create_creator_profile(sender, instance, created, **kwargs):
    """Create a CreatorProfile when a User with user_type 'creator' is created."""
    if created and instance.user_type == 'creator':
        CreatorProfile.objects.get_or_create(user=instance)
        # Send welcome email asynchronously
        send_welcome_email_task.delay(instance.id)


@receiver(post_save, sender=User)
def update_creator_profile(sender, instance, **kwargs):
    """Ensure that a CreatorProfile exists for users with user_type
    'creator' and delete it if user_type changes."""
    if instance.user_type == 'creator':
        CreatorProfile.objects.get_or_create(user=instance)
    else:
        CreatorProfile.objects.filter(user=instance).delete()


@receiver(post_save, sender=CreatorProfile)
def creator_profile_post_save(sender, instance, created, **kwargs):
    """Post-save signal for CreatorProfile to perform any additional actions
    after a profile is created or updated."""
    if created:
        # if in beta period before 13th April auto verify and set is_early_adopter to True
        if timezone.now() < datetime(2024, 4, 13, tzinfo=dt_timezone.utc):
            instance.verified = True
            instance.is_early_adopter = True
            instance.save()
            # Send welcome email to early adopter asynchronously
            welcome_early_adopter_task.delay(instance.user.slug)