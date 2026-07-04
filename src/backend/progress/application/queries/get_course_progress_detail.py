"""
Get Course Progress Detail Query

Returns detailed progress for a specific course enrollment.
Includes all modules and lessons with their status.
"""
from dataclasses import dataclass
from uuid import UUID
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class GetCourseProgressDetailQuery:
    """
    Query to get detailed progress for one course.

    Returns: full hierarchy of modules and lessons with progress.
    """
    enrollment_id: UUID
    course_id: UUID


@dataclass(frozen=True)
class LessonProgressDetail:
    """Progress detail for one lesson."""

    lesson_id: UUID
    lesson_title: str
    lesson_order: int
    status: str  

    
    content_gate_passed: bool
    homework_gate_passed: bool

    
    viewed_required_count: int
    required_content_count: int
    homework_required: bool
    homework_submitted: bool

    
    unlocked_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None


@dataclass(frozen=True)
class ModuleProgressDetail:
    """Progress detail for one module."""

    module_id: UUID
    module_title: str
    module_order: int
    status: str  

    
    total_lessons: int
    completed_lessons: int

    
    assessment_required: bool
    assessment_passed: bool

    
    unlocked_at: datetime | None
    completed_at: datetime | None

    
    lessons: List[LessonProgressDetail]


@dataclass(frozen=True)
class CourseProgressDetailResult:
    """Result of course progress detail query."""

    enrollment_id: UUID
    course_id: UUID
    course_title: str
    status: str  

    
    completion_percentage: int
    total_lessons: int
    completed_lessons: int

    
    enrolled_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    last_activity_at: datetime | None

    
    modules: List[ModuleProgressDetail]
