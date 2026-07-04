"""
My Certificates Query
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from django.db.models import QuerySet

from src.backend.certificates.domain.models.certificate import Certificate


@dataclass
class MyCertificatesQuery:
    """Query to get user's certificates."""

    user_id: UUID
    status: Optional[str] = None  


class MyCertificatesQueryHandler:
    """Handler for MyCertificatesQuery."""

    def handle(self, query: MyCertificatesQuery) -> QuerySet[Certificate]:
        """Get user's certificates."""

        queryset = Certificate.objects.filter(
            user_id=query.user_id
        ).select_related('template').order_by('-issued_at')

        if query.status:
            queryset = queryset.filter(status=query.status)

        return queryset
