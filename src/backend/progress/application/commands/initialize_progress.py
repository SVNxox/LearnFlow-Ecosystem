"""
Initialize Progress Command

Creates CourseProgress, ModuleProgress, and LessonProgress records
when a student enrolls in a course.

Handler for StudentEnrolled event (Outbox Pattern).
"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass(frozen=True)
class InitializeProgressCommand:
    """
    Command to initialize progress tracking for a new enrollment.

    Triggered by: StudentEnrolled event from Enrollment Domain
    """
    enrollment_id: UUID
    user_id: UUID
    course_id: UUID
    delivery_format: str  
    is_sequential: bool
