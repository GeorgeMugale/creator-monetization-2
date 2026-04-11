from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from apps.wallets.models import Wallet, WalletTransaction
from apps.payments.services.payout_orchestrator import PayoutOrchestrator
from utils.send_emails import send_missing_payout_account_email


def superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_superuser)(view_func)


@staff_member_required
@superuser_required
@require_http_methods(["GET", "POST"])
def finalise_wallet_payout(request, payout_tx_id):
    """
    Superuser-only view to finalise a pending wallet payout.
    GET  -> confirmation screen
    POST -> execute provider payout
    """

    payout_tx = get_object_or_404(
        WalletTransaction,
        id=payout_tx_id,
        transaction_type="PAYOUT",
        status="PENDING",
    )

    wallet = payout_tx.wallet
    payout_account = wallet.payout_account
    app_label = wallet._meta.app_label
    model_name = wallet._meta.model_name

    wallet_change_url = reverse(
        f"admin:{app_label}_{model_name}_change",
        args=[wallet.id],
    )

    # =============================
    # STEP 1: Confirmation page
    # =============================
    if request.method == "GET":
        return render(
            request,
            "payouts/finalise_payout.html",
            {
                "wallet": wallet,
                "payout_tx": payout_tx,
                "wallet_change_url": wallet_change_url,
                "payout_account": payout_account,
            },
        )

    # =============================
    # STEP 2: Finalise payout
    # =============================
    try:
        PayoutOrchestrator.finalize(
            payout_tx=payout_tx,
            success=True,
            approved_by=request.user,
        )

        messages.success(
            request,
            f"Payout finalised successfully "
            f"(Reference: {payout_tx.reference})",
        )

    except Exception as exc:
        messages.error(request, f"Payout finalisation failed: {exc}")

    return redirect(wallet_change_url)


@staff_member_required
@require_http_methods(["GET", "POST"])
def trigger_wallet_payout(request, wallet_id):
    """
    Staff-only view to manually trigger a wallet payout.
    GET  -> show confirmation screen
    POST -> initiate payout
    """

    wallet = get_object_or_404(Wallet, id=wallet_id)
    payout_account = wallet.payout_account
    

    app_label = Wallet._meta.app_label
    model_name = Wallet._meta.model_name

    # Lipila admin wallet change page
    change_url = reverse(
        f"admin:{app_label}_{model_name}_change",
        args=[wallet.id],
    )

    # =============================
    # STEP 1: Confirmation page
    # =============================
    if request.method == "GET":
        # Check if payout account is verified
        has_payout_account = payout_account.verified if payout_account else False
        
        # Send email to creator if payout account is missing
        if not has_payout_account:
            send_missing_payout_account_email(wallet)
        
        return render(
            request,
            "payouts/confirm_payout.html",
            {
                "wallet": wallet,
                "change_url": change_url,
                "payout_account": payout_account,
                "has_payout_account": has_payout_account,
            },
        )

    # =============================
    # STEP 2: Execute payout
    # =============================
    # Check if payout account exists before proceeding
    if payout_account is None:
        messages.error(
            request,
            "Cannot initiate payout: The creator has not set up a payout account. "
            "An email has been sent to the creator requesting them to do so."
        )
        return redirect(change_url)
    
    try:
        payout_tx = PayoutOrchestrator.initiate_payout(
            wallet=wallet,
            initiated_by=request.user,
        )

        messages.success(
            request,
            f"Payout initiated successfully"
            f"(Reference: {payout_tx.reference})",
        )

    except Exception as exc:
        messages.error(request, f"Payout failed: {exc}")

    return redirect(change_url)


@staff_member_required
@superuser_required
def payout_summary(request):
    """
    Superuser-only view to display payout summary and statistics.
    Shows pending payouts, completed payouts, total amounts, etc.
    """
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from datetime import timedelta

    # Get all wallet transactions
    all_transactions = WalletTransaction.objects.filter(transaction_type="PAYOUT")
    
    # Pending payouts
    pending_payouts = all_transactions.filter(status="PENDING")
    pending_count = pending_payouts.count()
    pending_total = pending_payouts.aggregate(Sum("amount"))["amount__sum"] or 0
    
    # Completed payouts
    completed_payouts = all_transactions.filter(status="COMPLETED")
    completed_count = completed_payouts.count()
    completed_total = completed_payouts.aggregate(Sum("amount"))["amount__sum"] or 0
    
    # Failed payouts
    failed_payouts = all_transactions.filter(status="FAILED")
    failed_count = failed_payouts.count()
    failed_total = failed_payouts.aggregate(Sum("amount"))["amount__sum"] or 0
    
    # Recent payouts (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_payouts = all_transactions.filter(created_at__gte=thirty_days_ago)
    
    # Total statistics
    total_payouts = all_transactions.aggregate(Sum("amount"))["amount__sum"] or 0
    total_count = all_transactions.count()
    
    context = {
        "pending_payouts": pending_payouts[:10],  # Show last 10 pending
        "pending_count": pending_count,
        "pending_total": pending_total,
        "completed_payouts": completed_payouts[:10],  # Show last 10 completed
        "completed_count": completed_count,
        "completed_total": completed_total,
        "failed_payouts": failed_payouts[:10],  # Show last 10 failed
        "failed_count": failed_count,
        "failed_total": failed_total,
        "recent_payouts_count": recent_payouts.count(),
        "total_payouts": total_payouts,
        "total_count": total_count,
    }
    
    return render(request, "payouts/payout_summary.html", context)


@staff_member_required
@superuser_required
def stats(request):
    """
    Superuser-only view to display overall platform statistics.
    Shows creator counts, wallet statistics, payment statistics, etc.
    """
    from django.db.models import Sum, Count, Avg, Q
    from django.db.models.functions import Abs
    from django.utils import timezone
    from datetime import timedelta
    from apps.creators.models import CreatorProfile
    from apps.payments.models import Payment
    
    # Creator statistics
    total_creators = CreatorProfile.objects.count()
    verified_creators = Wallet.objects.filter(is_verified=True).count()
    active_creators = Wallet.objects.filter(is_active=True).count()
    
    # Wallet statistics
    total_wallets = Wallet.objects.count()
    total_balance = Wallet.objects.aggregate(Sum("balance"))["balance__sum"] or 0
    avg_balance = Wallet.objects.aggregate(Avg("balance"))["balance__avg"] or 0
    
    # Transaction statistics (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    cash_in_txns = WalletTransaction.objects.filter(
        transaction_type="CASH_IN",
        created_at__gte=thirty_days_ago
    )
    payout_txns = WalletTransaction.objects.filter(
        transaction_type="PAYOUT",
        created_at__gte=thirty_days_ago
    )
    
    cash_in_total = cash_in_txns.aggregate(Sum("amount"))["amount__sum"] or 0
    payout_total = payout_txns.aggregate(Sum("amount"))["amount__sum"] or 0
    
    # Payment statistics
    total_payments = Payment.objects.count()
    successful_payments = Payment.objects.filter(status="completed").count()
    pending_payments = Payment.objects.filter(status="pending").count()
    failed_payments = Payment.objects.filter(status="failed").count()
    
    # Only sum completed payments for total amount
    total_payment_amount = Payment.objects.filter(status="completed").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_failed_amount = Payment.objects.filter(status="failed").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_pending_amount = Payment.objects.filter(status="pending").aggregate(
        Sum("amount")
    )["amount__sum"] or 0
    
    # Fee statistics
    total_fees = WalletTransaction.objects.filter(
        transaction_type="FEE"
    ).aggregate(total=Sum(Abs("amount")))["total"] or 0
    
    context = {
        "total_creators": total_creators,
        "verified_creators": verified_creators,
        "active_creators": active_creators,
        "total_wallets": total_wallets,
        "total_balance": total_balance,
        "avg_balance": avg_balance,
        "cash_in_total": cash_in_total,
        "cash_in_count": cash_in_txns.count(),
        "payout_total": payout_total,
        "payout_count": payout_txns.count(),
        "total_payments": total_payments,
        "successful_payments": successful_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,
        "total_payment_amount": total_payment_amount,
        "total_pending_amount": total_pending_amount,
        "total_failed_amount": total_failed_amount,
        "total_fees": total_fees,
    }
    
    return render(request, "payouts/stats.html", context)
