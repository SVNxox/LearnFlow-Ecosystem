"""
Record Content View Command

Records that a student has viewed a lesson content item.
Updates viewed_required_count and checks lesson completion.

Implements F2 fix: atomic increment using F() expression.
Implements F15 fix: video watch ratio tracking.
"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass(frozen=True)
class RecordContentViewCommand:
    """
    Command to record a content view.

    Triggered by: POST /api/v1/progress/lessons/{id}/content/{id}/view/
    """
    enrollment_id: UUID
    lesson_id: UUID
    content_id: UUID
    is_required: bool

    
    last_position_seconds: Optional[int] = None
    total_duration_seconds: Optional[int] = None
