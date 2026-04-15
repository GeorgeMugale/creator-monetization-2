"""
Celery tasks for the creators app.
Handles async operations like sending welcome emails to new creators.
"""
import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from apps.wallets.models import Wallet
from utils.send_emails import (
    send_welcome_email, send_daily_weekly_summary_email,
    send_reminder_to_share_creator_link_email,
    welcome_early_adopter_email)
from celery.schedules import crontab
from config.celery import app

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email_task(user_id):
    """
    Async task to send a welcome email to a newly created creator.
    
    This task is triggered when a user with user_type='creator' is created.
    It sends a motivational welcome email with getting started instructions
    and tips for success on the TipZed platform.
    
    Args:
        user_id (int): The ID of the newly created user
        
    Returns:
        str: Status message indicating success or failure
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Only send welcome email to creators
        if user.user_type != 'creator':
            logger.info(f"Skipping welcome email for non-creator user {user.id}")
            return "Email skipped - not a creator"
        
        # Send the welcome email
        success = send_welcome_email(user)
        
        if success:
            logger.info(f"Welcome email task completed successfully for user {user.id}")
            return f"Welcome email sent to {user.email}"
        else:
            logger.warning(f"Welcome email task failed for user {user.id}")
            return f"Failed to send welcome email to {user.email}"
            
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found when sending welcome email")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Error in send_welcome_email_task for user {user_id}: {str(e)}")
        raise


@shared_task
def send_daily_summary_email_task(wallet_id):
    """
    Task wrapper for sending daily summary emails to creators.
    
    Args:
        wallet_id (int): The ID of the wallet
        
    Returns:
        str: Status message
    """
    try:
        wallet = Wallet.objects.get(id=wallet_id)
        success = send_daily_weekly_summary_email(wallet, period='daily')
        
        if success:
            logger.info(f"Daily summary email sent for wallet {wallet_id}")
            return f"Daily summary email sent to {wallet.creator.user.email}"
        else:
            logger.warning(f"Failed to send daily summary email for wallet {wallet_id}")
            return f"Failed to send daily summary email for wallet {wallet_id}"
            
    except Wallet.DoesNotExist:
        logger.error(f"Wallet with id {wallet_id} not found")
        return f"Wallet {wallet_id} not found"
    except Exception as e:
        logger.error(f"Error in send_daily_summary_email_task for wallet {wallet_id}: {str(e)}")
        raise


# Schedule task to send daily summary emails to creators every day at 7:30 AM
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Schedule the daily summary email task to run every day at 7:30 AM for
    every wallet with balance.
    Fetch all wallets and check if they have balance, then schedule the email task.
    """
    try:
        wallets = Wallet.objects.filter(balance__gt=0)
        for wallet in wallets:
            # Use task.s() to create a task signature for scheduling
            sender.add_periodic_task(
                crontab(hour=7, minute=30),  # Run every day at 7:30 AM
                send_daily_summary_email_task.s(wallet.id),
                name=f'Send daily summary email for wallet {wallet.id}'
            )
    except Exception as e:
        logger.error(f"Error setting up periodic tasks: {str(e)}")


@shared_task
def send_reminder_to_share_creator_link_email_task():
    """
    Task to send a reminder email to creators who haven't received a tip.
    
    This task can be scheduled to run periodically (e.g., every 3 days) to encourage
    creators to share their unique creator link and attract more supporters.
    """
    try:
        from apps.wallets.models import Wallet
        wallets = Wallet.objects.filter(balance=0)  # Creators with no tips received
        send_reminder_to_share_creator_link_email(wallets)
        logger.info(f"Sent reminder email to {wallets.count()} creators to share their creator link")
        return f"Sent reminder emails to {wallets.count()} creators"
    except Exception as e:
        logger.error(f"Error in send_reminder_to_share_creator_link_email_task: {str(e)}")
        raise

# Schedule the reminder email task to run every 3 days at 10:00 AM
@app.on_after_finalize.connect
def setup_reminder_email_task(sender, **kwargs):
    """Schedule the reminder email task to run every 3 days at 10:00 AM."""
    sender.add_periodic_task(
        crontab(hour=10, minute=0, day_of_month='*/3'),  # Every 3 days at 10:00 AM
        send_reminder_to_share_creator_link_email_task.s(),
        name='Send reminder to share creator link email every 3 days'
    )


@shared_task
def welcome_early_adopter_task(slug):
    """
    Task to send a welcome email to early adopters who signed up before the beta period ended.
    
    This task can be triggered for users who signed up during the beta period (before April 13, 2024)
    to welcome them and provide them with exclusive benefits or information about their early adopter status.
    
    Args:
        slug (str): The unique slug of the creator profile
        
    Returns:
        str: Status message
    """
    try:
        from apps.creators.models import CreatorProfile
        profile = CreatorProfile.objects.get(slug=slug)
        user = profile.user
        
        # Send welcome email to early adopter
        success = welcome_early_adopter_email(user.email)
        
        if success:
            logger.info(f"Welcome email sent to early adopter {user.email}")
            return f"Welcome email sent to early adopter {user.email}"
        else:
            logger.warning(f"Failed to send welcome email to early adopter {user.email}")
            return f"Failed to send welcome email to early adopter {user.email}"
            
    except CreatorProfile.DoesNotExist:
        logger.error(f"CreatorProfile with slug {slug} not found")
        return f"CreatorProfile with slug {slug} not found"
    except Exception as e:
        logger.error(f"Error in welcome_early_adopter_task for slug {slug}: {str(e)}")
        raise