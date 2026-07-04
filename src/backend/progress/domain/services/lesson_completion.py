"""
Lesson Completion Service

Handles lesson completion logic including:
- Content gate checking
- Homework gate checking
- Completion cascade (lesson → module → course)

Implements critical fixes:
- F2: Atomic F() increments to prevent race conditions
- F12: Attendance bypasses content gate only, not homework gate
- F18: select_for_update() to prevent bulk attendance race conditions
"""
from uuid import UUID
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from src.backend.progress.domain.models import (
    LessonProgress,
    ModuleProgress,
    CourseProgress,
    LessonContentView,
)


class LessonCompletionService:
    """
    Core completion logic for lessons.

    All completion checks must use select_for_update() to prevent
    race conditions during bulk attendance marking (F18 fix).
    """

    @staticmethod
    @transaction.atomic
    def record_content_view(
        enrollment_id: UUID,
        lesson_id: UUID,
        content_id: UUID,
        is_required: bool,
        last_position_seconds: int = None,
        total_duration_seconds: int = None,
    ) -> dict:
        """
        Record that student viewed a content item.

        Implements F2 fix: atomic increment using F() expression.
        Implements F15 fix: video watch ratio tracking.

        Returns: dict with 'lesson_completed' boolean
        """
        
        lesson_progress = LessonProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
        )

        
        view, created = LessonContentView.objects.get_or_create(
            enrollment_id=enrollment_id,
            content_id=content_id,
            defaults={
                'lesson_progress_id': lesson_progress.id,
                'is_required': is_required,
                'last_position_seconds': last_position_seconds,
                'total_duration_seconds': total_duration_seconds,
            }
        )

        if not created:
            # Update existing view
            view.view_count = F('view_count') + 1
            view.last_position_seconds = last_position_seconds
            view.save(update_fields=['view_count', 'last_position_seconds', 'last_viewed_at'])
            view.refresh_from_db()

        # Increment counter if required content (F2 fix: atomic)
        if is_required and created:
            LessonProgress.objects.filter(pk=lesson_progress.pk).update(
                viewed_required_count=F('viewed_required_count') + 1
            )
            lesson_progress.refresh_from_db()

        # Check if lesson can be completed
        lesson_completed = LessonCompletionService._check_lesson_completion(
            lesson_progress
        )

        return {
            'lesson_completed': lesson_completed,
            'content_gate_passed': lesson_progress.content_gate_passed(),
            'homework_gate_passed': lesson_progress.homework_gate_passed(),
        }

    @staticmethod
    @transaction.atomic
    def mark_homework_submitted(enrollment_id: UUID, lesson_id: UUID) -> dict:
        """
        Mark homework as submitted.

        Called when: SubmissionApproved event from Submissions Domain.

        Returns: dict with 'lesson_completed' boolean
        """
        lesson_progress = LessonProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
        )

        lesson_progress.homework_submitted = True
        lesson_progress.homework_submitted_at = timezone.now()
        lesson_progress.save(update_fields=[
            'homework_submitted',
            'homework_submitted_at',
            'updated_at'
        ])

        # Check completion
        lesson_completed = LessonCompletionService._check_lesson_completion(
            lesson_progress
        )

        return {'lesson_completed': lesson_completed}

    @staticmethod
    @transaction.atomic
    def mark_attendance(
        enrollment_id: UUID,
        lesson_id: UUID,
        marked_by_id: UUID,
    ) -> dict:
        """
        Mark attendance for offline lesson.

        F12 fix: Attendance bypasses CONTENT gate only, NOT homework gate.

        Returns: dict with 'lesson_completed' boolean
        """
        lesson_progress = LessonProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
        )

        # F12: Bypass content gate by setting viewed = required
        lesson_progress.viewed_required_count = lesson_progress.required_content_count
        lesson_progress.completion_source = 'mentor_attendance'
        lesson_progress.save(update_fields=[
            'viewed_required_count',
            'completion_source',
            'updated_at'
        ])

        # Homework gate still applies!
        lesson_completed = LessonCompletionService._check_lesson_completion(
            lesson_progress
        )

        return {'lesson_completed': lesson_completed}

    @staticmethod
    @transaction.atomic
    def mark_override(
        enrollment_id: UUID,
        lesson_id: UUID,
        override_by_id: UUID,
        override_reason: str,
    ) -> LessonProgress:
        """
        Admin/Mentor override to mark lesson completed.

        F20 fix: Audit trail required.

        Returns: LessonProgress
        """
        lesson_progress = LessonProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
        )

        # Force completion with audit trail
        lesson_progress.status = 'completed'
        lesson_progress.completed_at = timezone.now()
        lesson_progress.completion_source = 'admin_override'
        lesson_progress.override_by_id = override_by_id
        lesson_progress.override_reason = override_reason
        lesson_progress.save(update_fields=[
            'status',
            'completed_at',
            'completion_source',
            'override_by_id',
            'override_reason',
            'updated_at'
        ])

        # Trigger cascade
        from .completion_cascade import CompletionCascadeService
        CompletionCascadeService.check_module_completion(
            enrollment_id,
            lesson_progress.module_id
        )

        return lesson_progress

    @staticmethod
    def _check_lesson_completion(lesson_progress: LessonProgress) -> bool:
        """
        Check if lesson can be marked completed.

        Called after any progress update.
        If both gates passed → mark completed → trigger cascade.

        Returns: True if lesson was completed
        """
        if lesson_progress.status == 'completed':
            return False  # Already completed (idempotent)

        if not lesson_progress.can_complete():
            return False  # Gates not passed

        # Mark completed
        lesson_progress.status = 'completed'
        lesson_progress.completed_at = timezone.now()
        if not lesson_progress.completion_source:
            lesson_progress.completion_source = 'student_activity'
        lesson_progress.save(update_fields=[
            'status',
            'completed_at',
            'completion_source',
            'updated_at'
        ])

        # Trigger cascade (in same transaction)
        from .completion_cascade import CompletionCascadeService
        CompletionCascadeService.check_module_completion(
            lesson_progress.enrollment_id,
            lesson_progress.module_id
        )

        return True
