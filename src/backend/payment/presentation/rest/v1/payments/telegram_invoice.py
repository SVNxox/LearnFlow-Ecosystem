"""
Telegram Invoice API — генерация URL для оплаты через Telegram.

Endpoint: POST /api/v1/payment/payments/{payment_id}/telegram-invoice/
Permissions: IsAuthenticated
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings

from src.backend.payment.domain.models import Payment
from src.backend.payment.application.services.telegram_payment_service import TelegramPaymentService

logger = logging.getLogger(__name__)


class TelegramInvoiceView(APIView):
    """Генерация URL для оплаты через Telegram."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, payment_id: str) -> Response:
        """Генерирует URL для оплаты через Telegram."""
        try:
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)

            
            if payment.status in ['succeeded', 'failed', 'cancelled', 'refunded']:
                return Response(
                    {"detail": f"Payment already in terminal status: {payment.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)
            if not bot_username:
                return Response(
                    {"detail": "TELEGRAM_BOT_USERNAME not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            
            invoice_url = TelegramPaymentService.create_invoice_url(
                payment_id=payment.id,
                bot_username=bot_username
            )

            return Response({
                "invoice_url": invoice_url,
                "payment_id": str(payment.id),
                "amount": str(payment.amount),
                "currency": payment.currency,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating Telegram invoice: {e}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )