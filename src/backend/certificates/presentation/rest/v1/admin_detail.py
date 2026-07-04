"""
Admin Certificate Detail API.

Endpoint: GET /api/v1/certificates/admin/certificates/{id}/
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.certificates.domain.models import Certificate
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class AdminCertificateDetailView(APIView):
    """Get certificate details."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, certificate_id: str) -> Response:
        """Return certificate details."""
        try:
            cert = get_object_or_404(Certificate, id=certificate_id)

            
            audit_logs = []
            if hasattr(cert, 'audit_logs'):
                for log in cert.audit_logs.all()[:20]:
                    audit_logs.append({
                        "id": str(log.id),
                        "action": log.action,
                        "actor_id": str(log.actor_id) if log.actor_id else None,
                        "details": log.details,
                        "ip_address": str(log.ip_address) if log.ip_address else None,
                        "created_at": log.created_at.isoformat(),
                    })

            
            reissue_requests = []
            if hasattr(cert, 'reissue_requests'):
                for req in cert.reissue_requests.all()[:10]:
                    reissue_requests.append({
                        "id": str(req.id),
                        "reason": req.reason,
                        "status": req.status,
                        "requested_at": req.requested_at.isoformat(),
                        "requested_by_id": str(req.requested_by_id) if req.requested_by_id else None,
                        "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
                        "reviewed_by_id": str(req.reviewed_by_id) if req.reviewed_by_id else None,
                    })

            data = {
                "id": str(cert.id),
                "certificate_number": cert.certificate_number,
                "verification_code": cert.verification_code,
                "student_full_name_snapshot": cert.student_full_name_snapshot,
                "course_name_snapshot": cert.course_name_snapshot,
                "course_description_snapshot": cert.course_description_snapshot,
                "user_id": str(cert.user_id) if cert.user_id else None,
                "user_email": cert.user.email if cert.user else None,
                "enrollment_id": str(cert.enrollment_id) if cert.enrollment_id else None,
                "course_id": str(cert.course_id) if cert.course_id else None,
                "template_id": str(cert.template_id) if cert.template_id else None,
                "status": cert.status,
                "final_score": str(cert.final_score) if cert.final_score else None,
                "completion_date": cert.completion_date.isoformat() if cert.completion_date else None,
                "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
                "pdf_url": cert.pdf_url,
                "pdf_generated_at": cert.pdf_generated_at.isoformat() if cert.pdf_generated_at else None,
                "revoked_at": cert.revoked_at.isoformat() if cert.revoked_at else None,
                "revoked_reason": cert.revoked_reason,
                "revoked_by_id": str(cert.revoked_by_id) if cert.revoked_by_id else None,
                "metadata": cert.metadata,
                "created_at": cert.created_at.isoformat(),
                "updated_at": cert.updated_at.isoformat(),
                "audit_logs": audit_logs,
                "reissue_requests": reissue_requests,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting certificate detail: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request: Request, certificate_id: str) -> Response:
        """Update certificate (edit metadata, score, etc.)."""
        try:
            cert = get_object_or_404(Certificate, id=certificate_id)
            data = request.data

            
            updatable_fields = [
                'final_score', 'completion_date', 'student_full_name_snapshot',
                'course_name_snapshot', 'course_description_snapshot', 'metadata'
            ]

            updated_fields = []
            for field in updatable_fields:
                if field in data:
                    setattr(cert, field, data[field])
                    updated_fields.append(field)

            if updated_fields:
                cert.save(update_fields=updated_fields + ['updated_at'])

                
                from src.backend.certificates.domain.models import CertificateAuditLog
                CertificateAuditLog.objects.create(
                    certificate=cert,
                    action='updated',
                    actor=request.user,
                    details={'updated_fields': updated_fields, 'new_values': {f: data[f] for f in updated_fields}},
                    ip_address=request.META.get('REMOTE_ADDR'),
                )

            
            return self.get(request, certificate_id)

        except Exception as e:
            logger.error(f"Error updating certificate: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)