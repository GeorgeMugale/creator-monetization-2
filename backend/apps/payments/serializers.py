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
            "patron_name",
            "patron_phone",
            "provider",
            "patron_email",
            "patron_message",
            "metadata",
        ]

    def create(self, validated_data):
        # Call the custom manager method instead of Model.objects.create()
        return Payment.objects.create_payment(**validated_data)
      