"""
Admin Payment Detail API — детали платежа для администратора.

Endpoint: GET /api/v1/payment/admin/payments/{payment_id}/
Permissions: IsAuthenticated + IsAdminOrStaff
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.payment.domain.models import Payment
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class AdminPaymentDetailView(APIView):
    """Детали платежа для администратора."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, payment_id: str) -> Response:
        """Возвращает детали платежа."""
        try:
            payment = get_object_or_404(Payment, id=payment_id)

            
            course_title = None
            if payment.enrollment_id:
                from src.backend.enrollment.domain.models import CourseEnrollment
                from src.backend.learning.domain.models import Course

                try:
                    enrollment = CourseEnrollment.objects.only('course_id').get(id=payment.enrollment_id)
                    if enrollment.course_id:
                        course = Course.objects.only('title').get(id=enrollment.course_id)
                        course_title = course.title
                except (CourseEnrollment.DoesNotExist, Course.DoesNotExist):
                    pass

            
            user_name = None
            if payment.user:
                first_name = getattr(payment.user, 'first_name', '') or ''
                last_name = getattr(payment.user, 'last_name', '') or ''
                if first_name or last_name:
                    user_name = f"{first_name} {last_name}".strip()

            data = {
                "id": str(payment.id),
                "user_id": str(payment.user_id),
                "user_email": payment.user.email if payment.user else None,
                "user_name": user_name,
                "enrollment_id": str(payment.enrollment_id) if payment.enrollment_id else None,
                "course_title": course_title,
                "amount": str(payment.amount),
                "currency": payment.currency or 'UZS',
                "status": payment.status,
                "payment_method": payment.payment_method,
                "provider": payment.provider,
                "provider_payment_id": payment.provider_payment_id,
                "idempotency_key": payment.idempotency_key,
                "created_at": payment.created_at.isoformat(),
                "succeeded_at": payment.succeeded_at.isoformat() if payment.succeeded_at else None,
                "failed_at": payment.failed_at.isoformat() if payment.failed_at else None,
                "refunded_at": payment.refunded_at.isoformat() if payment.refunded_at else None,
                "metadata": payment.metadata or {},
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting payment detail: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)