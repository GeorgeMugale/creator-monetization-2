# This module defines utility functions that send
# vairious emails to users. These functions can be called from views, 
# signals, or Celery tasks. 
# Types of emails
# - Missing payout account email: Sent to creators who have a pending payout but no payout account set up.
# - Transaction receipt email: Sent to users after they receive a tip, containing transaction details.
# - Daily/weekly summary email: Sent to creators summarizing their earnings and activity over a period of time (future feature).

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def send_missing_payout_account_email(wallet):
    """
    Send an email to a creator requesting them to set up a payout account.
    
    Used when there's a pending payout but no payout account is configured.
    
    Args:
        wallet (Wallet): The wallet object of the creator
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        creator_user = wallet.creator.user
        subject = "Action Required: Set Up Your Payout Account"
        
        # Plain text version
        message = f"""
Hello {creator_user.first_name or creator_user.username},

We are writing to inform you that an administrator is attempting to process a payout
for your account. However, we were unable to complete the payout because you have not
yet set up a payout account.

To receive your earnings, please:
1. Log into your creator dashboard
2. Navigate to your wallet settings
3. Add your payout account details (mobile money provider, account name, and phone number)

Once you've set up your payout account, the admin can proceed with the payout.

If you have any questions or need assistance, please don't hesitate to contact our support team.

Best regards,
TipZed Admin Team
        """
        
        # HTML version
        html_message = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <div style="background-color: #667eea; padding: 20px; border-radius: 8px 8px 0 0; color: white;">
                <h2 style="margin: 0;">Action Required: Set Up Your Payout Account</h2>
            </div>
            
            <div style="padding: 20px;">
                <p>Hello {creator_user.first_name or creator_user.username},</p>
                
                <p>We are writing to inform you that an administrator is attempting to process a payout for your account.
                However, we were unable to complete the payout because you have not yet set up a payout account.</p>
                
                <h3 style="color: #667eea;">To receive your earnings, please:</h3>
                <ol>
                    <li>Log into your creator dashboard</li>
                    <li>Navigate to your wallet settings</li>
                    <li>Add your payout account details (mobile money provider, account name, and phone number)</li>
                </ol>
                
                <p>Once you've set up your payout account, the admin can proceed with the payout.</p>
                
                <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                
                <p style="margin-top: 30px; color: #666; border-top: 1px solid #e0e0e0; padding-top: 20px;">
                    Best regards,<br>
                    <strong>TipZed Admin Team</strong>
                </p>
            </div>
        </div>
    </body>
</html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@tipzed.space',
            recipient_list=[creator_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Successfully sent payout account setup email to {creator_user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payout account email for wallet {wallet.id}: {str(e)}")
        return False


def send_transaction_receipt_email(payment, recipient_email=None):
    """
    Send a transaction receipt email to a user after they've sent a tip.
    
    Contains transaction details, amount, creator information, and receipt reference.
    
    Args:
        payment (Payment): The payment/transaction object
        recipient_email (str, optional): Email address to send to. If None, uses payment.patron_email
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Use provided email or fall back to payment's patron email
        email = recipient_email or payment.patron_email
        
        if not email:
            logger.warning(f"No recipient email found for payment {payment.reference}")
            return False
        
        # Get creator info from wallet
        creator = payment.wallet.creator
        creator_user = creator.user
        
        # Format currency display
        currency_display = dict(payment._meta.get_field('currency').choices).get(
            payment.currency, payment.currency
        )
        
        # Calculate provider fee display
        provider_fee = payment.provider_fee or Decimal('0.00')
        net_amount = payment.net_amount or (payment.amount - provider_fee)
        
        subject = f"TipZed Receipt: Your tip to {creator_user.get_full_name() or creator_user.username}"
        
        # Plain text version
        message = f"""
Hello {payment.patron_name or 'Valued Supporter'},

Thank you for your support! We've received your tip.

Transaction Details:
Reference: {payment.reference}
Amount: {payment.amount} {payment.currency}
Status: {payment.get_status_display()}
Date: {payment.created_at.strftime('%B %d, %Y at %I:%M %p')}

Creator: {creator_user.get_full_name() or creator_user.username}
Message: {payment.patron_message or 'No message included'}

Your support helps creators continue doing what they love.
You can view this transaction in your TipZed account anytime.

Thank you for being awesome!

Best regards,
TipZed Team
        """
        
        # HTML version
        status_color = '#4CAF50' if payment.status in ['completed', 'captured'] else '#FF9800'
        html_message = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <div style="background-color: #667eea; padding: 20px; border-radius: 8px 8px 0 0; color: white; text-align: center;">
                <h2 style="margin: 0;">TipZed Receipt</h2>
                <p style="margin: 10px 0 0 0; font-size: 14px;">Thank you for your support!</p>
            </div>
            
            <div style="padding: 20px;">
                <p>Hello {payment.patron_name or 'Valued Supporter'},</p>
                
                <p>Thank you for your support! We've received your tip to 
                <strong>{creator_user.get_full_name() or creator_user.username}</strong>.</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #667eea;">Transaction Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Reference:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0;">{payment.reference}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Amount:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                                <strong style="font-size: 18px; color: #667eea;">{payment.amount} {payment.currency}</strong>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Status:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                                <span style="background-color: {status_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                                    {payment.get_status_display()}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Date:</td>
                            <td style="padding: 8px 0;">{payment.created_at.strftime('%B %d, %Y at %I:%M %p')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0;">
                    <p><strong>Creator:</strong> {creator_user.get_full_name() or creator_user.username}</p>
                    <p><strong>Your Message:</strong></p>
                    <p style="margin: 10px 0; font-style: italic; color: #666;">
                        "{payment.patron_message or 'No message included'}"
                    </p>
                </div>
                
                <p>Your support helps creators continue doing what they love. You can view this transaction 
                in your TipZed account anytime.</p>
                
                <p style="margin-top: 30px; color: #666; border-top: 1px solid #e0e0e0; padding-top: 20px;">
                    Thank you for being awesome!<br>
                    <strong>TipZed Team</strong>
                </p>
            </div>
        </div>
    </body>
</html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@tipzed.space',
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Successfully sent transaction receipt email to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send transaction receipt email for payment {payment.reference}: {str(e)}")
        return False


def send_daily_weekly_summary_email(wallet, period='daily'):
    """
    Send a summary email to a creator with their earnings and activity.
    
    Future feature: Sends daily, weekly, or custom period summaries with:
    - Total earnings during period
    - Number of tips received
    - Average tip amount
    - Top supporters
    - Activity trend insights
    
    Args:
        wallet (Wallet): The wallet object of the creator
        period (str): 'daily', 'weekly', or 'custom' (default: 'daily')
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        creator_user = wallet.creator.user
        
        # Calculate the date range based on period
        now = timezone.now()
        if period == 'daily':
            start_date = now - timedelta(days=1)
            period_label = "Today"
        elif period == 'weekly':
            # Last 7 days
            start_date = now - timedelta(days=7)
            period_label = "This Week"
        else:
            # Default to daily
            start_date = now - timedelta(days=1)
            period_label = "Custom Period"
        
        # Get transactions for the period
        transactions = wallet.transactions.filter(
            created_at__gte=start_date,
            transaction_type='CASH_IN',
            status='COMPLETED'
        )
        
        # Calculate statistics
        total_earnings = Decimal('0.00')
        total_tips = 0
        total_fees = Decimal('0.00')
        
        for transaction in transactions:
            total_earnings += transaction.amount
            total_fees += transaction.fee
            total_tips += 1
        
        average_tip = total_earnings / total_tips if total_tips > 0 else Decimal('0.00')
        
        # Get recent supporters/payments
        from apps.payments.models import Payment
        payments = Payment.objects.filter(
            wallet=wallet,
            created_at__gte=start_date,
            status__in=['completed', 'captured']
        ).order_by('-created_at')[:5]
        
        subject = f"TipZed Summary: Your {period_label} Earnings"
        
        # Build supporters list HTML
        supporters_html = ""
        if payments.exists():
            supporters_html = "<h3 style='color: #667eea;'>Recent Tips:</h3><ul>"
            for payment in payments:
                supporter_name = payment.patron_name or 'Anonymous Supporter'
                supporters_html += f"""
                <li style="padding: 10px 0; border-bottom: 1px solid #e0e0e0;">
                    <strong>{supporter_name}</strong> sent {payment.amount} {payment.currency}
                    <br><small style="color: #999;">{payment.created_at.strftime('%B %d at %I:%M %p')}</small>
                </li>
                """
            supporters_html += "</ul>"
        
        # Plain text version
        message = f"""
Hello {creator_user.first_name or creator_user.username},

Here's a summary of your TipZed earnings for {period_label}:

Summary Statistics:
Total Earnings: {total_earnings} {wallet.currency}
Number of Tips: {total_tips}
Average Tip: {average_tip} {wallet.currency}
Total Fees: {total_fees} {wallet.currency}
Current Balance: {wallet.balance} {wallet.currency}

Keep creating amazing content, and your supporters will keep tipping!

Best regards,
TipZed Team
        """
        
        # HTML version
        html_message = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <div style="background-color: #667eea; padding: 20px; border-radius: 8px 8px 0 0; color: white; text-align: center;">
                <h2 style="margin: 0;">TipZed Earnings Summary</h2>
                <p style="margin: 10px 0 0 0; font-size: 14px;">{period_label}</p>
            </div>
            
            <div style="padding: 20px;">
                <p>Hello {creator_user.first_name or creator_user.username},</p>
                
                <p>Here's a summary of your TipZed earnings for <strong>{period_label}</strong>:</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #667eea;">Summary Statistics</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #e8eef7;">
                            <td style="padding: 12px; font-weight: bold; border-radius: 4px 0 0 0;">Total Earnings</td>
                            <td style="padding: 12px; text-align: right; font-size: 20px; color: #667eea; font-weight: bold; border-radius: 0 4px 0 0;">
                                {total_earnings} {wallet.currency}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Number of Tips:</td>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; text-align: right;">{total_tips}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Average Tip:</td>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; text-align: right;">{average_tip} {wallet.currency}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; font-weight: bold;">Total Fees:</td>
                            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; text-align: right;">{total_fees} {wallet.currency}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 0; font-weight: bold;">Current Balance:</td>
                            <td style="padding: 12px 0; text-align: right; font-weight: bold; color: #4CAF50;">
                                {wallet.balance} {wallet.currency}
                            </td>
                        </tr>
                    </table>
                </div>
                
                {supporters_html}
                
                <div style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0;">
                        <strong>💡 Pro Tip:</strong> Keep creating amazing content, and your supporters will keep tipping! 
                        Your dedication to your craft is what makes TipZed special.
                    </p>
                </div>
                
                <p style="margin-top: 30px; color: #666; border-top: 1px solid #e0e0e0; padding-top: 20px;">
                    Best regards,<br>
                    <strong>TipZed Team</strong>
                </p>
            </div>
        </div>
    </body>
</html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@tipzed.space',
            recipient_list=[creator_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Successfully sent {period} summary email to {creator_user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send summary email for wallet {wallet.id}: {str(e)}")
        return False

