"""
StudentEnrolled event — Critical event (Outbox Pattern).

Emitted when: Student successfully enrolls in a course.
Delivery: Outbox Pattern (guaranteed delivery).
Consumers:
- Progress Domain (initialize CourseProgress)
- Analytics Domain (track enrollment)
- Notifications Domain (welcome email)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class StudentEnrolledEvent:
    """
    Event payload for StudentEnrolled.

    This is a CRITICAL event that creates aggregate roots in other domains.
    Must use Outbox Pattern for guaranteed delivery.
    """
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    delivery_format: str
    status: str
    occurred_at: datetime

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            'enrollment_id': str(self.enrollment_id),
            'user_id': str(self.user_id),
            'course_id': str(self.course_id),
            'delivery_format': self.delivery_format,
            'status': self.status,
            'occurred_at': self.occurred_at.isoformat(),
        }
