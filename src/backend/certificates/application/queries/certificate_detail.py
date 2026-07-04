"""
Certificate Detail Query
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.backend.certificates.domain.models.certificate import Certificate


@dataclass
class CertificateDetailQuery:
    """Query to get certificate details."""

    certificate_id: UUID
    user_id: Optional[UUID] = None  


class CertificateDetailQueryHandler:
    """Handler for CertificateDetailQuery."""

    def handle(self, query: CertificateDetailQuery) -> Certificate:
        """Get certificate details."""

        queryset = Certificate.objects.select_related('user', 'template')

        if query.user_id:
            
            queryset = queryset.filter(user_id=query.user_id)

        try:
            return queryset.get(id=query.certificate_id)
        except Certificate.DoesNotExist:
            raise ValueError(f"Certificate {query.certificate_id} not found")
