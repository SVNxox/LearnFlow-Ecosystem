"""
PaymentList serializer — GET /api/v1/payment/payments/
"""

from rest_framework import serializers

from src.backend.payment.domain.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer for payment list view."""

    user_id = serializers.UUIDField(source='user.id', read_only=True)
    is_terminal = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id',
            'user_id',
            'enrollment_id',
            'amount',
            'currency',
            'provider',
            'status',
            'payment_method',
            'card_last4',
            'card_brand',
            'succeeded_at',
            'failed_at',
            'is_terminal',
            'created_at',
        ]
        read_only_fields = fields

    def get_is_terminal(self, obj: Payment) -> bool:
        """Check if payment is in terminal state."""
        return obj.is_terminal()
