"""
Serializers for Payment model
"""
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    """Lightweight serializer for creating payments"""

    class Meta:
        model = Payment
        fields = [
            "amount",
            "isp_provider",
            "patron_email",
            "patron_phone",
            "patron_message",
        ]
      