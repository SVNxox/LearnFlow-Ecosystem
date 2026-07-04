"""
Payme webhook handler — POST /api/v1/payment/webhooks/payme/
"""

import logging
from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from src.backend.payment.domain.services.payment_processor import PaymentProcessor
from src.backend.payment.domain.services.refund_processor import RefundProcessor

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaymeWebhookView(APIView):
    """
    Payme.uz webhook handler.

    Handles payment status updates from Payme (Uzbekistan payment provider).
    """

    permission_classes = []  
    authentication_classes = []

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'method': {'type': 'string'},
                    'params': {'type': 'object'},
                },
            }
        },
        responses={200: None},
        tags=['Payment — Webhooks'],
        operation_id='payme_webhook',
        description='Handle Payme webhook events',
    )
    def post(self, request: Request) -> Response:
        """Handle Payme webhook."""

        
        
        
        

        method = request.data.get('method')
        params = request.data.get('params', {})

        logger.info(f"Received Payme webhook: {method}")

        try:
            if method == 'PerformTransaction':
                self._handle_payment_succeeded(params)
            elif method == 'CancelTransaction':
                self._handle_payment_cancelled(params)
            else:
                logger.warning(f"Unhandled Payme method: {method}")

            return Response({'result': {'success': True}}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing Payme webhook: {e}", exc_info=True)
            return Response(
                {'error': {'code': -32400, 'message': 'Webhook processing failed'}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_payment_succeeded(self, params: dict[str, Any]) -> None:
        """Handle successful payment."""
        transaction_id = params.get('id')

        if not transaction_id:
            logger.error("Missing transaction ID in Payme webhook")
            return

        PaymentProcessor.process_succeeded(
            provider_payment_id=str(transaction_id),
            provider_data=params,
        )

    def _handle_payment_cancelled(self, params: dict[str, Any]) -> None:
        """Handle cancelled/failed payment."""
        transaction_id = params.get('id')
        reason = params.get('reason', 'Transaction cancelled')

        if not transaction_id:
            logger.error("Missing transaction ID in Payme webhook")
            return

        PaymentProcessor.process_failed(
            provider_payment_id=str(transaction_id),
            failure_reason=reason,
        )

    def _verify_auth(self, auth_header: str) -> bool:
        """
        Verify Payme authentication.

        TODO: Implement actual authentication verification.
        Payme uses Basic Auth with merchant credentials.
        """
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        logger.warning("Payme authentication not implemented (stub)")
        return True  
