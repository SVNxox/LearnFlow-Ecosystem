"""
Simulate Payment Success API — имитация успешной оплаты для тестирования.

Endpoint: POST /api/v1/payment/payments/{payment_id}/simulate-success/
Permissions: IsAuthenticated + IsAdminOrStaff (только для тестирования)
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
from src.backend.payment.domain.services.payment_processor import PaymentProcessor
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class SimulatePaymentSuccessView(APIView):
    """
    Имитация успешной оплаты для тестирования.

    Только в development режиме и только для admin/staff.
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, payment_id: str) -> Response:
        """Имитирует успешную оплату."""
        
        if not settings.DEBUG:
            return Response(
                {"detail": "This endpoint is only available in development mode"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            payment = get_object_or_404(Payment, id=payment_id)

            
            if payment.status in ['succeeded', 'failed', 'cancelled', 'refunded']:
                return Response(
                    {"detail": f"Payment already in terminal status: {payment.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            payment.status = Payment.Status.SUCCEEDED
            payment.succeeded_at = __import__('django.utils', fromlist=['timezone']).timezone.now()
            payment.provider_payment_id = f"test_{payment.id}"
            payment.save(update_fields=['status', 'succeeded_at', 'provider_payment_id'])

            
            if payment.enrollment_id:
                from src.backend.enrollment.domain.models import CourseEnrollment
                try:
                    enrollment = CourseEnrollment.objects.get(id=payment.enrollment_id)
                    if enrollment.status in ['pending', 'inactive']:
                        enrollment.status = 'active'
                        enrollment.payment_status = 'paid'
                        enrollment.save(update_fields=['status', 'payment_status'])
                        logger.info(f"Enrollment {enrollment.id} activated (simulated)")
                except CourseEnrollment.DoesNotExist:
                    logger.error(f"Enrollment {payment.enrollment_id} not found")

            logger.info(f"Payment {payment_id} simulated as succeeded")

            return Response(
                {"detail": "Payment simulated as succeeded"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error simulating payment success: {e}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )