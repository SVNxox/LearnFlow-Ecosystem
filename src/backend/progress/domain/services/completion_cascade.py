"""
Completion Cascade Service

Handles cascade completion logic:
- Lesson completed → check Module completion
- Module completed → check Course completion

Implements critical fixes:
- F2: Atomic F() increments for counters
- F7: Assessment pending logic
- F17: Unlock first lesson of next module
- F18: select_for_update() to prevent race conditions
"""
from uuid import UUID
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from src.backend.progress.domain.models import (
    ModuleProgress,
    CourseProgress,
    LessonProgress,
)


class CompletionCascadeService:
    """
    Cascade completion checks (lesson → module → course).

    All methods must use select_for_update() to prevent
    race conditions (F18 fix).
    """

    @staticmethod
    @transaction.atomic
    def check_module_completion(enrollment_id: UUID, module_id: UUID):
        """
        Check if module should be marked completed.

        Called after: any lesson in this module completes.

        Completion criteria:
        1. All lessons completed
        2. Module assessment passed (if assessment_required)

        Then: unlock next module (if sequential)
        """
        
        module_progress = ModuleProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            module_id=module_id,
        )

        if module_progress.status == 'completed':
            return  

        
        ModuleProgress.objects.filter(pk=module_progress.pk).update(
            completed_lessons_count=F('completed_lessons_count') + 1
        )
        module_progress.refresh_from_db()

        
        if module_progress.completed_lessons_count < module_progress.total_lessons_count:
            
            if module_progress.status != 'in_progress':
                module_progress.status = 'in_progress'
                module_progress.save(update_fields=['status', 'updated_at'])
            return

        
        if module_progress.assessment_required and not module_progress.assessment_passed:
            
            module_progress.status = 'assessment_pending'
            module_progress.save(update_fields=['status', 'updated_at'])
            return

        
        module_progress.status = 'completed'
        module_progress.completed_at = timezone.now()
        module_progress.save(update_fields=[
            'status',
            'completed_at',
            'updated_at'
        ])

        
        course_progress = CourseProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id
        )

        
        if course_progress.is_sequential:
            CompletionCascadeService._unlock_next_module(
                enrollment_id,
                module_progress.module_order
            )

        
        CompletionCascadeService.check_course_completion(enrollment_id)

    @staticmethod
    @transaction.atomic
    def check_course_completion(enrollment_id: UUID):
        """
        Check if course should be marked completed.

        Called after: any module completes.

        Completion criteria: All modules completed.

        Then: emit CourseCompleted event (Outbox) → Enrollment & Certificates.
        """
        
        course_progress = CourseProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id
        )

        if course_progress.status == 'completed':
            return  

        
        CourseProgress.objects.filter(pk=course_progress.pk).update(
            completed_modules_count=F('completed_modules_count') + 1
        )
        course_progress.refresh_from_db()

        
        if course_progress.completed_modules_count < course_progress.total_modules_count:
            
            if course_progress.status != 'in_progress':
                course_progress.status = 'in_progress'
                course_progress.save(update_fields=['status', 'updated_at'])
            return

        
        course_progress.status = 'completed'
        course_progress.completed_at = timezone.now()
        course_progress.save(update_fields=[
            'status',
            'completed_at',
            'updated_at'
        ])

        
        
        
        
        
        
        

    @staticmethod
    @transaction.atomic
    def mark_assessment_passed(enrollment_id: UUID, module_id: UUID):
        """
        Mark module assessment as passed.

        Called when: AssessmentPassed event from Assessment Domain.

        Then: check module completion.
        """
        module_progress = ModuleProgress.objects.select_for_update().get(
            enrollment_id=enrollment_id,
            module_id=module_id,
        )

        module_progress.assessment_passed = True
        module_progress.assessment_passed_at = timezone.now()
        module_progress.save(update_fields=[
            'assessment_passed',
            'assessment_passed_at',
            'updated_at'
        ])

        
        CompletionCascadeService.check_module_completion(enrollment_id, module_id)

    @staticmethod
    def _unlock_next_module(enrollment_id: UUID, current_module_order: int):
        """
        Unlock the next module after current one completes.

        F17 fix: Also unlock first lesson of next module.
        """
        try:
            next_module = ModuleProgress.objects.get(
                enrollment_id=enrollment_id,
                module_order=current_module_order + 1,
                status='locked',
            )
        except ModuleProgress.DoesNotExist:
            
            return

        
        next_module.status = 'unlocked'
        next_module.unlocked_at = timezone.now()
        next_module.save(update_fields=['status', 'unlocked_at', 'updated_at'])

        
        try:
            first_lesson = LessonProgress.objects.filter(
                enrollment_id=enrollment_id,
                module_id=next_module.module_id,
                status='locked',
            ).order_by('lesson_order').first()

            if first_lesson:
                first_lesson.status = 'unlocked'
                first_lesson.unlocked_at = timezone.now()
                first_lesson.save(update_fields=['status', 'unlocked_at', 'updated_at'])
        except LessonProgress.DoesNotExist:
            pass  
