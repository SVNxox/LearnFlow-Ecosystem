"""
Stripe Checkout — создание Stripe Checkout Session.

Endpoint: GET /api/v1/payment/stripe/checkout/{payment_id}/
Permissions: IsAuthenticated
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings

from src.backend.payment.domain.models import Payment

logger = logging.getLogger(__name__)


class StripeCheckoutView(APIView):
    """Создание Stripe Checkout Session и редирект."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, payment_id: str):
        """Создаёт Stripe Checkout Session и редиректит на оплату."""
        try:
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)

            
            if payment.status in ['succeeded', 'failed', 'cancelled', 'refunded']:
                return Response(
                    {"detail": f"Payment already in terminal status: {payment.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            stripe_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
            if not stripe_secret_key:
                return Response(
                    {"detail": "STRIPE_SECRET_KEY not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            
            try:
                import stripe
            except ImportError:
                return Response(
                    {"detail": "Stripe library not installed. Run: pip install stripe"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            
            stripe.api_key = stripe_secret_key

            
            course_title = "Course"
            if payment.enrollment_id:
                from src.backend.enrollment.domain.models import CourseEnrollment
                from src.backend.learning.domain.models import Course
                try:
                    enrollment = CourseEnrollment.objects.get(id=payment.enrollment_id)
                    course = Course.objects.get(id=enrollment.course_id)
                    course_title = course.title
                except Exception as e:
                    logger.error(f"Error fetching course: {e}")

            
            amount_in_cents = int(float(payment.amount) * 100)

            
            currency = payment.currency.lower() if payment.currency else 'usd'

            
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': course_title,
                            'description': 'LearnFlow Course',
                        },
                        'unit_amount': amount_in_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{frontend_url}/payment/status/{payment.id}?success=true",
                cancel_url=f"{frontend_url}/payment/status/{payment.id}?cancelled=true",
                metadata={
                    'payment_id': str(payment.id),
                    'user_id': str(payment.user_id),
                    'enrollment_id': str(payment.enrollment_id) if payment.enrollment_id else '',
                },
            )

            
            return redirect(session.url)

        except ImportError:
            return Response(
                {"detail": "Stripe library not installed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error creating Stripe Checkout Session: {e}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )