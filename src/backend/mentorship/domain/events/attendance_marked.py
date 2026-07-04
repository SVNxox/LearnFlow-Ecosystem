"""
Attendance Marked event
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AttendanceMarkedEvent:
    """
    Attendance has been marked for a student in an offline session.

    This event triggers LessonCompleted for offline students.
    Dispatched via Django Signals (not critical for Outbox).
    """

    attendance_id: UUID
    session_id: UUID
    student_id: UUID
    enrollment_id: UUID
    lesson_id: UUID
    status: str  
    marked_by_id: UUID
    marked_at: datetime
    occurred_at: datetime
