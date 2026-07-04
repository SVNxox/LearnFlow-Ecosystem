"""
Mark Lesson Completed Command

Marks a lesson as completed and triggers cascade completion check.

Used by:
- Mentor attendance (offline) - F12 fix
- Admin override - F20 fix (with audit trail)
"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass(frozen=True)
class MarkLessonCompletedCommand:
    """
    Command to manually mark a lesson as completed.

    Used for:
    - Mentor attendance (offline mode)
    - Admin override
    """
    enrollment_id: UUID
    lesson_id: UUID
    completion_source: str  

    
    override_by_id: Optional[UUID] = None
    override_reason: Optional[str] = None
