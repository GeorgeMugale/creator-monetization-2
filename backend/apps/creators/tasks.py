"""
Celery tasks for the creators app.
Handles async operations like sending welcome emails to new creators.
"""
from celery import shared_task
from django.contrib.auth import get_user_model
from utils.send_emails import send_welcome_email
import logging


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
