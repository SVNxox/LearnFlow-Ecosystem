"""
Admin Payments List API — список всех платежей для администратора.

Endpoint: GET /api/v1/payment/admin/payments/
Permissions: IsAuthenticated + IsAdminOrStaff
"""

import logging
from django.db import models
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.payment.domain.models import Payment
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


def get_user_name(user) -> str | None:
    """Получает имя пользователя из разных возможных мест."""
    if not user:
        return None

    
    
    first_name = getattr(user, 'first_name', None) or ''
    last_name = getattr(user, 'last_name', None) or ''

    if first_name or last_name:
        return f"{first_name} {last_name}".strip()

    
    if hasattr(user, 'info') and user.info:
        first_name = getattr(user.info, 'first_name', '') or ''
        last_name = getattr(user.info, 'last_name', '') or ''
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()

    
    full_name = getattr(user, 'full_name', None)
    if full_name:
        return full_name

    
    return user.email if hasattr(user, 'email') else None


class AdminPaymentsListView(APIView):
    """Список всех платежей с фильтрацией и пагинацией."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request) -> Response:
        """Возвращает список всех платежей."""
        try:
            
            queryset = Payment.objects.select_related('user').all()

            
            payment_status = request.query_params.get('status')
            if payment_status and payment_status != 'all':
                queryset = queryset.filter(status=payment_status)

            
            payment_method = request.query_params.get('method')
            if payment_method and payment_method != 'all':
                queryset = queryset.filter(payment_method=payment_method)

            
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    models.Q(user__email__icontains=search) |
                    models.Q(user__first_name__icontains=search) |
                    models.Q(user__last_name__icontains=search) |
                    models.Q(user__info__first_name__icontains=search) |
                    models.Q(user__info__last_name__icontains=search)
                )

            
            ordering = request.query_params.get('ordering', '-created_at')
            queryset = queryset.order_by(ordering)

            
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size

            total_count = queryset.count()
            payments = queryset[start:end]

            
            enrollment_ids = [p.enrollment_id for p in payments if p.enrollment_id]
            course_titles = {}

            if enrollment_ids:
                from src.backend.enrollment.domain.models import CourseEnrollment
                from src.backend.learning.domain.models import Course

                
                enrollments = CourseEnrollment.objects.filter(
                    id__in=enrollment_ids
                ).only('id', 'course_id')

                
                enrollment_to_course = {str(e.id): e.course_id for e in enrollments}

                
                course_ids = [e.course_id for e in enrollments if e.course_id]

                
                if course_ids:
                    courses = Course.objects.filter(id__in=course_ids).only('id', 'title')
                    course_map = {str(c.id): c.title for c in courses}

                    
                    for enrollment_id, course_id in enrollment_to_course.items():
                        if course_id:
                            course_titles[enrollment_id] = course_map.get(str(course_id))

            
            data = []
            for p in payments:
                
                user_name = get_user_name(p.user)

                
                amount = str(p.amount)
                currency = p.currency or 'UZS'

                
                course_title = course_titles.get(str(p.enrollment_id)) if p.enrollment_id else None

                data.append({
                    "id": str(p.id),
                    "user_id": str(p.user_id),
                    "user_email": p.user.email if p.user else None,
                    "user_name": user_name,  
                    "enrollment_id": str(p.enrollment_id) if p.enrollment_id else None,
                    "course_title": course_title,
                    "amount": amount,
                    "currency": currency,
                    "status": p.status,
                    "payment_method": p.payment_method,
                    "idempotency_key": p.idempotency_key,
                    "created_at": p.created_at.isoformat(),
                    "completed_at": p.succeeded_at.isoformat() if p.succeeded_at else None,
                    "metadata": p.metadata or {},
                })

            return Response({
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
                "results": data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing payments: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)