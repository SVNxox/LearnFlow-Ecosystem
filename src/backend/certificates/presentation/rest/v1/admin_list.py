"""
Admin Certificates List API.

Endpoint: GET /api/v1/certificates/admin/certificates/
"""

import logging
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.certificates.domain.models import Certificate
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class AdminCertificatesListView(APIView):
    """List all certificates with filtering and search."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request) -> Response:
        """Return paginated list of certificates."""
        try:
            queryset = Certificate.objects.select_related(
                'user', 'template'
            ).all()

            
            cert_status = request.query_params.get('status')
            if cert_status and cert_status != 'all':
                queryset = queryset.filter(status=cert_status)

            
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(student_full_name_snapshot__icontains=search) |
                    Q(course_name_snapshot__icontains=search) |
                    Q(certificate_number__icontains=search) |
                    Q(verification_code__icontains=search) |
                    Q(user__email__icontains=search)
                )

            
            ordering = request.query_params.get('ordering', '-issued_at')
            queryset = queryset.order_by(ordering)

            
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size

            total_count = queryset.count()
            certificates = queryset[start:end]

            
            data = []
            for cert in certificates:
                data.append({
                    "id": str(cert.id),
                    "certificate_number": cert.certificate_number,
                    "verification_code": cert.verification_code,
                    "student_full_name_snapshot": cert.student_full_name_snapshot,
                    "course_name_snapshot": cert.course_name_snapshot,
                    "user_id": str(cert.user_id) if cert.user_id else None,
                    "user_email": cert.user.email if cert.user else None,
                    "enrollment_id": str(cert.enrollment_id) if cert.enrollment_id else None,
                    "course_id": str(cert.course_id) if cert.course_id else None,
                    "status": cert.status,
                    "final_score": str(cert.final_score) if cert.final_score else None,
                    "completion_date": cert.completion_date.isoformat() if cert.completion_date else None,
                    "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
                    "pdf_url": cert.pdf_url,
                    "revoked_at": cert.revoked_at.isoformat() if cert.revoked_at else None,
                    "revoked_reason": cert.revoked_reason,
                    "revoked_by_id": str(cert.revoked_by_id) if cert.revoked_by_id else None,
                })

            return Response({
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
                "results": data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing certificates: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)