"""
Get Progress Dashboard Query

Returns student's overall progress across all enrolled courses.

Implements F6 fix: lesson-based percentage calculation.
"""
from dataclasses import dataclass
from uuid import UUID
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class GetProgressDashboardQuery:
    """
    Query to get student's progress dashboard.

    Returns: list of courses with progress percentage.
    """
    user_id: UUID


@dataclass(frozen=True)
class CourseProgressSummary:
    """Summary of progress for one course."""

    enrollment_id: UUID
    course_id: UUID
    course_title: str
    course_thumbnail_url: str | None
    status: str  

    
    completion_percentage: int  

    total_lessons: int
    completed_lessons: int

    enrolled_at: datetime
    last_activity_at: datetime | None
    completed_at: datetime | None


@dataclass(frozen=True)
class ProgressDashboardResult:
    """Result of dashboard query."""

    courses: List[CourseProgressSummary]
    total_courses: int
    in_progress_count: int
    completed_count: int


class GetProgressDashboardHandler:
    """Handler for GetProgressDashboardQuery."""

    @staticmethod
    def handle(query: GetProgressDashboardQuery) -> ProgressDashboardResult:
        """
        Execute dashboard query.

        Returns progress summary across all user's enrollments.
        """
        from src.backend.enrollment.models import CourseEnrollment
        from src.backend.progress.domain.models import CourseProgress
        from src.backend.learning.domain.models import Course

        
        enrollments = CourseEnrollment.objects.filter(
            user_id=query.user_id,
            deleted_at__isnull=True
        ).select_related().order_by('-enrolled_at')

        courses_summary = []
        in_progress = 0
        completed = 0

        for enrollment in enrollments:
            
            try:
                course = Course.objects.get(id=enrollment.course_id, deleted_at__isnull=True)
            except Course.DoesNotExist:
                continue

            
            try:
                progress = CourseProgress.objects.get(
                    enrollment_id=enrollment.id
                )
                completion_percentage = progress.cached_percentage
                completed_lessons = progress.completed_modules_count  
                total_lessons = progress.total_modules_count  
                status = progress.status
                last_activity = progress.last_activity_at
                completed_at = progress.completed_at
            except CourseProgress.DoesNotExist:
                
                completion_percentage = 0
                completed_lessons = 0
                total_lessons = 0
                status = 'not_started'
                last_activity = None
                completed_at = None

            
            if status == 'completed':
                completed += 1
            elif status == 'in_progress':
                in_progress += 1

            courses_summary.append(
                CourseProgressSummary(
                    enrollment_id=enrollment.id,
                    course_id=enrollment.course_id,
                    course_title=course.title,
                    course_thumbnail_url=course.thumbnail_url,
                    status=status,
                    completion_percentage=completion_percentage,
                    total_lessons=total_lessons,
                    completed_lessons=completed_lessons,
                    enrolled_at=enrollment.enrolled_at,
                    last_activity_at=last_activity,
                    completed_at=completed_at,
                )
            )

        return ProgressDashboardResult(
            courses=courses_summary,
            total_courses=len(courses_summary),
            in_progress_count=in_progress,
            completed_count=completed,
        )
