"""
Progress Initialization Service

Initializes CourseProgress, ModuleProgress, and LessonProgress
when a student enrolls in a course.

Triggered by: StudentEnrolled event (Outbox Pattern)
Handler: progress.application.handlers.event_handlers.handle_student_enrolled
"""
from uuid import UUID
from django.db import transaction
from django.utils import timezone

from src.backend.progress.domain.models import (
    CourseProgress,
    ModuleProgress,
    LessonProgress,
)


class ProgressInitializationService:
    """
    Initializes progress tracking for a new enrollment.

    Creates snapshots of course structure at enrollment time.
    """

    @staticmethod
    @transaction.atomic
    def initialize_progress(
        enrollment_id: UUID,
        user_id: UUID,
        course_id: UUID,
        delivery_format: str,
        is_sequential: bool,
    ) -> CourseProgress:
        """
        Initialize progress tracking (idempotent).

        Steps:
        1. Create CourseProgress (or get existing)
        2. Create ModuleProgress for all published modules
        3. Create LessonProgress for all published lessons
        4. Unlock first module/lesson (if sequential)

        Returns: CourseProgress
        """
        
        course_progress, created = CourseProgress.objects.get_or_create(
            enrollment_id=enrollment_id,
            defaults={
                'user_id': user_id,
                'course_id': course_id,
                'delivery_format': delivery_format,
                'is_sequential': is_sequential,
                'status': 'not_started',
                'total_modules_count': 0,  
                'completed_modules_count': 0,
            }
        )

        if not created:
            
            return course_progress

        
        
        from django.db import connections

        with connections['default'].cursor() as cursor:
            
            cursor.execute("""
                SELECT id, title, "order",
                       (SELECT COUNT(*) FROM courses_lesson l
                        WHERE l.module_id = m.id AND l.is_published = true
                        AND l.deleted_at IS NULL) as lesson_count,
                       (SELECT COUNT(*) > 0 FROM assessment_moduleassessment a
                        WHERE a.module_id = m.id) as has_assessment
                FROM courses_module m
                WHERE m.course_id = %s AND m.deleted_at IS NULL
                ORDER BY m."order"
            """, [str(course_id)])

            modules = cursor.fetchall()
            module_count = len(modules)

            
            course_progress.total_modules_count = module_count
            course_progress.save(update_fields=['total_modules_count'])

            first_module_id = None

            for idx, (module_id, title, order, lesson_count, has_assessment) in enumerate(modules):
                is_first = (idx == 0)
                if is_first:
                    first_module_id = module_id

                
                module_progress = ProgressInitializationService._create_module_progress(
                    enrollment_id=enrollment_id,
                    course_id=course_id,
                    module_data={
                        'id': module_id,
                        'order': order,
                        'lesson_count': lesson_count,
                        'has_assessment': has_assessment,
                    },
                    is_unlocked=(is_first and is_sequential) or not is_sequential,
                )

                
                cursor.execute("""
                    SELECT id, title, "order",
                           (SELECT COUNT(*) FROM courses_lessoncontent lc
                            WHERE lc.lesson_id = l.id AND lc.is_required = true) as required_content_count,
                           EXISTS(SELECT 1 FROM submissions_assignment a
                                  WHERE a.lesson_id = l.id) as has_homework
                    FROM courses_lesson l
                    WHERE l.module_id = %s AND l.is_published = true
                    AND l.deleted_at IS NULL
                    ORDER BY l."order"
                """, [str(module_id)])

                lessons = cursor.fetchall()

                for lesson_idx, (lesson_id, lesson_title, lesson_order, required_content, has_homework) in enumerate(lessons):
                    is_first_lesson = (lesson_idx == 0)

                    ProgressInitializationService._create_lesson_progress(
                        enrollment_id=enrollment_id,
                        module_id=module_id,
                        course_id=course_id,
                        lesson_data={
                            'id': lesson_id,
                            'order': lesson_order,
                            'required_content_count': required_content,
                            'has_homework': has_homework,
                        },
                        module_order=order,
                        is_unlocked=(is_first and is_first_lesson and is_sequential) or not is_sequential,
                    )

        return course_progress

    @staticmethod
    def _create_module_progress(
        enrollment_id: UUID,
        course_id: UUID,
        module_data: dict,
        is_unlocked: bool = False,
    ) -> ModuleProgress:
        """
        Create ModuleProgress for one module.

        Args:
            enrollment_id: Enrollment ID
            course_id: Course ID
            module_data: Dict with module info from Learning Domain
            is_unlocked: Whether to unlock this module

        Returns: ModuleProgress
        """
        return ModuleProgress.objects.create(
            enrollment_id=enrollment_id,
            module_id=module_data['id'],
            course_id=course_id,
            module_order=module_data['order'],
            status='unlocked' if is_unlocked else 'locked',
            total_lessons_count=module_data['lesson_count'],
            completed_lessons_count=0,
            assessment_required=module_data.get('has_assessment', False),
            assessment_passed=False,
            unlocked_at=timezone.now() if is_unlocked else None,
        )

    @staticmethod
    def _create_lesson_progress(
        enrollment_id: UUID,
        module_id: UUID,
        course_id: UUID,
        lesson_data: dict,
        module_order: int,
        is_unlocked: bool = False,
    ) -> LessonProgress:
        """
        Create LessonProgress for one lesson.

        Args:
            enrollment_id: Enrollment ID
            module_id: Module ID
            course_id: Course ID
            lesson_data: Dict with lesson info from Learning Domain
            module_order: Module order (for sorting)
            is_unlocked: Whether to unlock this lesson

        Returns: LessonProgress
        """
        return LessonProgress.objects.create(
            enrollment_id=enrollment_id,
            lesson_id=lesson_data['id'],
            module_id=module_id,
            course_id=course_id,
            lesson_order=lesson_data['order'],
            module_order=module_order,
            status='unlocked' if is_unlocked else 'locked',
            required_content_count=lesson_data['required_content_count'],
            viewed_required_count=0,
            homework_required=lesson_data.get('has_homework', False),
            homework_submitted=False,
            unlocked_at=timezone.now() if is_unlocked else None,
        )
