"""
My Group Sessions Query
"""

from dataclasses import dataclass
from uuid import UUID

from django.db.models import QuerySet

from src.backend.mentorship.domain.models.offline_session import OfflineSession


@dataclass
class MyGroupSessionsQuery:
    """Query to get mentor's group sessions."""

    mentor_id: UUID
    group_id: UUID


class MyGroupSessionsQueryHandler:
    """Handler for MyGroupSessionsQuery."""

    def handle(self, query: MyGroupSessionsQuery) -> QuerySet[OfflineSession]:
        """Get mentor's group sessions."""

        return OfflineSession.objects.filter(
            group_id=query.group_id,
            group__mentor_id=query.mentor_id,
        ).prefetch_related('attendances').order_by('scheduled_start')
