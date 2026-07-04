"""
Stripe Checkout Webhook — обработка webhook от Stripe.

Endpoint: POST /api/v1/payment/webhooks/stripe-checkout/
Permissions: AllowAny (Stripe подписывает запросы)
"""

import logging
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone

from src.backend.payment.domain.models import Payment
from src.backend.enrollment.domain.models import CourseEnrollment

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StripeCheckoutWebhookView(APIView):
    """Обработка webhook от Stripe Checkout."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        """Обрабатывает webhook от Stripe."""
        try:
            import stripe
        except ImportError:
            return Response(
                {'error': 'Stripe library not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        try:
            if webhook_secret and sig_header:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            else:
                
                import json
                event = json.loads(payload)

            logger.info(f"Received Stripe webhook: {event.get('type')}")

            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']

                
                payment_id = session.get('metadata', {}).get('payment_id')

                if not payment_id:
                    logger.error("Missing payment_id in Stripe session metadata")
                    return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

                
                try:
                    payment = Payment.objects.get(id=payment_id)

                    if payment.status == 'succeeded':
                        logger.warning(f"Payment {payment_id} already succeeded")
                        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

                    
                    payment.status = 'succeeded'
                    payment.succeeded_at = timezone.now()
                    payment.provider_payment_id = session.get('payment_intent')
                    payment.provider = 'stripe'
                    payment.metadata = {
                        **payment.metadata,
                        'stripe_session_id': session.get('id'),
                        'stripe_payment_intent': session.get('payment_intent'),
                        'payment_source': 'stripe_checkout',
                    }
                    payment.save()

                    
                    if payment.enrollment_id:
                        try:
                            enrollment = CourseEnrollment.objects.get(id=payment.enrollment_id)
                            if enrollment.status in ['pending', 'inactive']:
                                enrollment.status = 'active'
                                enrollment.payment_status = 'paid'
                                enrollment.save(update_fields=['status', 'payment_status'])
                                logger.info(f"Enrollment {enrollment.id} activated via Stripe")
                        except CourseEnrollment.DoesNotExist:
                            logger.error(f"Enrollment {payment.enrollment_id} not found")

                    logger.info(f"Payment {payment_id} successfully processed via Stripe")

                except Payment.DoesNotExist:
                    logger.error(f"Payment {payment_id} not found")
                    return Response({'status': 'error'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'status': 'ok'}, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )