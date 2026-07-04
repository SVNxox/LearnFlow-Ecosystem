"""
Session Detail Query
"""

from dataclasses import dataclass
from uuid import UUID

from src.backend.mentorship.domain.models.offline_session import OfflineSession


@dataclass
class SessionDetailQuery:
    """Query to get session details with attendances."""

    session_id: UUID


class SessionDetailQueryHandler:
    """Handler for SessionDetailQuery."""

    def handle(self, query: SessionDetailQuery) -> OfflineSession:
        """Get session details."""

        try:
            return OfflineSession.objects.prefetch_related(
                'attendances',
                'attendances__student',
            ).select_related('group', 'group__mentor').get(
                id=query.session_id
            )
        except OfflineSession.DoesNotExist:
            raise ValueError(f"Session {query.session_id} not found")
