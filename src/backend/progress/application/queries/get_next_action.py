"""
Get Next Action Query

Returns what student should do next in their learning journey.

Implements fixes:
- F8: module_order + lesson_order for correct sorting
- F9: in_progress priority over unlocked
- F10: assessment_pending detection
- F11: non-sequential course handling
"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional, Literal


@dataclass(frozen=True)
class GetNextActionQuery:
    """
    Query to get the next action for a student in a course.

    Returns one of:
    - lesson: next lesson to study
    - take_module_assessment: module assessment to complete
    - course_complete: all done
    """
    enrollment_id: UUID
    course_id: UUID


@dataclass(frozen=True)
class NextActionResult:
    """Result of GetNextAction query."""

    action_type: Literal['lesson', 'take_module_assessment', 'course_complete']

    
    lesson_id: Optional[UUID] = None
    lesson_title: Optional[str] = None
    module_title: Optional[str] = None

    
    module_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    assessment_title: Optional[str] = None
