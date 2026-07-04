"""
Stripe webhook handler — POST /api/v1/payment/webhooks/stripe/
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
class StripeWebhookView(APIView):
    """
    Stripe webhook handler.

    Handles payment status updates from Stripe.
    """

    permission_classes = []  
    authentication_classes = []

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string'},
                    'data': {'type': 'object'},
                },
            }
        },
        responses={200: None},
        tags=['Payment — Webhooks'],
        operation_id='stripe_webhook',
        description='Handle Stripe webhook events',
    )
    def post(self, request: Request) -> Response:
        """Handle Stripe webhook."""

        
        
        
        

        event_type = request.data.get('type')
        event_data = request.data.get('data', {}).get('object', {})

        logger.info(f"Received Stripe webhook: {event_type}")

        try:
            if event_type == 'payment_intent.succeeded':
                self._handle_payment_succeeded(event_data)
            elif event_type == 'payment_intent.payment_failed':
                self._handle_payment_failed(event_data)
            elif event_type == 'charge.refunded':
                self._handle_refund_succeeded(event_data)
            else:
                logger.warning(f"Unhandled Stripe event type: {event_type}")

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}", exc_info=True)
            return Response(
                {'error': 'Webhook processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_payment_succeeded(self, event_data: dict[str, Any]) -> None:
        """Handle successful payment."""
        provider_payment_id = event_data.get('id')

        if not provider_payment_id:
            logger.error("Missing payment ID in Stripe webhook")
            return

        PaymentProcessor.process_succeeded(
            provider_payment_id=provider_payment_id,
            provider_data=event_data,
        )

    def _handle_payment_failed(self, event_data: dict[str, Any]) -> None:
        """Handle failed payment."""
        provider_payment_id = event_data.get('id')
        failure_reason = event_data.get('last_payment_error', {}).get('message', 'Unknown error')

        if not provider_payment_id:
            logger.error("Missing payment ID in Stripe webhook")
            return

        PaymentProcessor.process_failed(
            provider_payment_id=provider_payment_id,
            failure_reason=failure_reason,
        )

    def _handle_refund_succeeded(self, event_data: dict[str, Any]) -> None:
        """Handle successful refund."""
        provider_refund_id = event_data.get('refunds', {}).get('data', [{}])[0].get('id')

        if not provider_refund_id:
            logger.error("Missing refund ID in Stripe webhook")
            return

        RefundProcessor.process_refund_succeeded(
            provider_refund_id=provider_refund_id,
        )

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature.

        TODO: Implement actual signature verification using stripe library.
        """
        
        
        
        
        
        
        

        logger.warning("Stripe signature verification not implemented (stub)")
        return True  
