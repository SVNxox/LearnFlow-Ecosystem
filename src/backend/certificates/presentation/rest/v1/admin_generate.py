"""
Admin Generate Certificate API.

Endpoint: POST /api/v1/certificates/admin/certificates/generate/
"""

import logging
from decimal import Decimal, InvalidOperation
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.certificates.application.commands.generate_certificate import (
    GenerateCertificateData,
    GenerateCertificateHandler,
)
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class AdminGenerateCertificateView(APIView):
    """Generate a new certificate for a student."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request) -> Response:
        """Generate a new certificate."""
        data = request.data

        
        if not data.get('user_id'):
            return Response(
                {"detail": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not data.get('enrollment_id') and not data.get('course_id'):
            return Response(
                {"detail": "Either enrollment_id or course_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        final_score = None
        if data.get('final_score'):
            try:
                final_score = Decimal(str(data['final_score']))
            except (InvalidOperation, ValueError):
                return Response(
                    {"detail": "Invalid final_score format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            command_data = GenerateCertificateData(
                user_id=data['user_id'],
                enrollment_id=data.get('enrollment_id'),
                course_id=data.get('course_id'),
                template_id=data.get('template_id'),
                final_score=final_score,
                metadata=data.get('metadata'),
            )

            certificate = GenerateCertificateHandler.handle(command_data)

            return Response({
                "id": str(certificate.id),
                "certificate_number": certificate.certificate_number,
                "verification_code": certificate.verification_code,
                "student_full_name_snapshot": certificate.student_full_name_snapshot,
                "course_name_snapshot": certificate.course_name_snapshot,
                "status": certificate.status,
                "final_score": str(certificate.final_score) if certificate.final_score else None,
                "completion_date": certificate.completion_date.isoformat() if certificate.completion_date else None,
                "issued_at": certificate.issued_at.isoformat(),
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error generating certificate: {e}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request: Request) -> Response:
        """Return available data for certificate generation (users, courses, templates)."""
        try:
            from django.contrib.auth import get_user_model
            from src.backend.learning.domain.models import Course
            from src.backend.certificates.domain.models import CertificateTemplate
            from src.backend.enrollment.domain.models import CourseEnrollment

            User = get_user_model()

            
            enrollments = CourseEnrollment.objects.filter(
                status='active'
            ).select_related('user').order_by('-enrolled_at')[:100]

            
            course_ids = set(e.course_id for e in enrollments if e.course_id)
            courses = Course.objects.filter(id__in=course_ids)
            course_map = {str(c.id): c.title for c in courses}

            users = []
            for enr in enrollments:
                user_name = ""
                if hasattr(enr.user, 'info') and enr.user.info:
                    user_name = f"{enr.user.info.first_name or ''} {enr.user.info.last_name or ''}".strip()
                if not user_name:
                    user_name = enr.user.email

                users.append({
                    "id": str(enr.user.id),
                    "email": enr.user.email,
                    "name": user_name,
                    "enrollment_id": str(enr.id),
                    "course_id": str(enr.course_id),
                    "course_title": course_map.get(str(enr.course_id), "Unknown"),
                })

            
            templates = CertificateTemplate.objects.filter(is_active=True).values(
                'id', 'name', 'description'
            )

            return Response({
                "users_with_enrollments": users,
                "templates": list(templates),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting certificate generation data: {e}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )