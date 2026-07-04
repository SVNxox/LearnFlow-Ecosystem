"""
CheckAccess Query — Check if student can access content.
"""

from dataclasses import dataclass
from typing import Tuple
from uuid import UUID

from django.contrib.auth import get_user_model

from src.backend.enrollment.domain.services import AccessControlService

User = get_user_model()


@dataclass
class CheckAccessQuery:
    """Query to check content access."""
    user_id: UUID
    course_id: UUID
    content_id: UUID


class CheckAccessHandler:
    """Handler for CheckAccess query."""

    @staticmethod
    def handle(query: CheckAccessQuery) -> Tuple[bool, str]:
        """
        Check if student can access content.

        Returns:
            (can_access, reason)
            - can_access: True if access granted
            - reason: Empty if granted, error message if denied

        Raises:
            User.DoesNotExist: If user not found
        """
        user = User.objects.get(id=query.user_id)

        can_access, reason = AccessControlService.can_access_content(
            user=user,
            course_id=query.course_id,
            content_id=query.content_id
        )

        return can_access, reason
