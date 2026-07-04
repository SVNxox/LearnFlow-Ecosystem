"""
Telegram Webhook — обработка webhook от Telegram Bot.

Endpoint: POST /api/v1/payment/webhooks/telegram/
Permissions: AllowAny (Telegram подписывает запросы)
"""

import logging
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from src.backend.payment.application.services.telegram_payment_service import TelegramPaymentService

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    """Обработка webhook от Telegram Bot."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        """Обрабатывает webhook от Telegram."""
        update = request.data

        
        logger.info(f"Received Telegram webhook: {update}")

        try:
            
            if 'pre_checkout_query' in update:
                return self._handle_pre_checkout(update['pre_checkout_query'])

            
            if 'message' in update and 'successful_payment' in update['message']:
                return self._handle_successful_payment(update['message'])

            return Response({'status': 'ok'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing Telegram webhook: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _handle_pre_checkout(self, pre_checkout_query: dict) -> Response:
        """Обрабатывает pre_checkout_query."""
        
        return Response({
            'method': 'answerPreCheckoutQuery',
            'pre_checkout_query_id': pre_checkout_query['id'],
            'ok': True,
        }, status=status.HTTP_200_OK)

    def _handle_successful_payment(self, message: dict) -> Response:
        """Обрабатывает успешную оплату."""
        successful_payment = message['successful_payment']

        payment_id = successful_payment.get('invoice_payload')
        total_amount = successful_payment.get('total_amount')
        telegram_payment_charge_id = successful_payment.get('telegram_payment_charge_id')
        provider_payment_charge_id = successful_payment.get('provider_payment_charge_id')

        if not payment_id or not total_amount:
            logger.error("Missing payment_id or total_amount in successful_payment")
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = TelegramPaymentService.process_successful_payment(
                payment_id=payment_id,
                total_amount=total_amount,
                telegram_payment_charge_id=telegram_payment_charge_id,
                provider_payment_charge_id=provider_payment_charge_id,
            )

            logger.info(f"Payment {payment_id} processed successfully via Telegram")
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing successful payment: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )