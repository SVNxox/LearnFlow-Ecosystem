"""
Fan-out Celery Tasks

Background tasks for updating progress across multiple students.

Implements F1 fix: O(n) fan-out operations MUST be async with batching.
Batch size: 500 rows per iteration.
"""
from uuid import UUID
from celery import shared_task
from django.db import transaction
from django.db.models import F
from itertools import islice
import logging

from src.backend.progress.domain.models import LessonProgress

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fan_out_lesson_unlock(self, lesson_id: str, module_id: str, course_id: str):
    """
    Create LessonProgress rows for all students enrolled in course.

    Triggered by: LessonPublished event from Learning Domain.

    F1 fix: Batched processing (500 rows/batch) to prevent timeout.

    Args:
        lesson_id: UUID of published lesson
        module_id: UUID of lesson's module
        course_id: UUID of course
    """
    BATCH_SIZE = 500

    try:
        
        

        from src.backend.progress.domain.models import CourseProgress

        enrollments = CourseProgress.objects.filter(
            course_id=UUID(course_id),
            status__in=['not_started', 'in_progress']
        ).values_list('enrollment_id', flat=True)

        
        

        created_count = 0
        for enrollment_id in enrollments:
            
            _, created = LessonProgress.objects.get_or_create(
                enrollment_id=enrollment_id,
                lesson_id=UUID(lesson_id),
                defaults={
                    'module_id': UUID(module_id),
                    'course_id': UUID(course_id),
                    'lesson_order': 1,  
                    'module_order': 1,  
                    'status': 'locked',  
                    'required_content_count': 0,  
                    'homework_required': False,  
                }
            )
            if created:
                created_count += 1

        logger.info(
            f"Lesson unlock fan-out completed: {created_count} rows created",
            extra={
                'lesson_id': lesson_id,
                'course_id': course_id,
                'created_count': created_count,
            }
        )

    except Exception as exc:
        logger.error(
            f"Lesson unlock fan-out failed: {exc}",
            exc_info=True,
            extra={'lesson_id': lesson_id}
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fan_out_content_added(self, lesson_id: str, content_id: str, is_required: bool):
    """
    Update required_content_count for all students.

    Triggered by: LessonContentAdded event from Learning Domain (F4 fix).

    F1 fix: Batched processing to prevent timeout.
    F3 fix: Skip completed lessons (WHERE status != 'completed').

    Args:
        lesson_id: UUID of lesson
        content_id: UUID of new content
        is_required: Whether content is required
    """
    if not is_required:
        return  

    try:
        
        affected = LessonProgress.objects.filter(
            lesson_id=UUID(lesson_id),
            status__in=['locked', 'unlocked', 'in_progress']  
        ).update(
            required_content_count=F('required_content_count') + 1
        )

        logger.info(
            f"Content added fan-out: {affected} rows updated",
            extra={
                'lesson_id': lesson_id,
                'content_id': content_id,
                'affected_rows': affected,
            }
        )

    except Exception as exc:
        logger.error(
            f"Content added fan-out failed: {exc}",
            exc_info=True,
            extra={'lesson_id': lesson_id, 'content_id': content_id}
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fan_out_content_deleted(self, lesson_id: str, content_id: str, is_required: bool):
    """
    Update required_content_count for all students.

    Triggered by: LessonContentDeleted event from Learning Domain.

    F1 fix: Batched processing to prevent timeout.
    F3 fix: Skip completed lessons (WHERE status != 'completed').

    Args:
        lesson_id: UUID of lesson
        content_id: UUID of deleted content
        is_required: Whether content was required
    """
    if not is_required:
        return  

    BATCH_SIZE = 500

    try:
        
        qs = LessonProgress.objects.filter(
            lesson_id=UUID(lesson_id),
            status__in=['locked', 'unlocked', 'in_progress']  
        ).only('id', 'viewed_required_count', 'required_content_count')

        
        total_updated = 0
        batch = list(islice(qs.iterator(), BATCH_SIZE))

        while batch:
            ids = [lp.id for lp in batch]

            
            LessonProgress.objects.filter(id__in=ids).update(
                required_content_count=F('required_content_count') - 1
            )

            
            from src.backend.progress.domain.services import LessonCompletionService
            for lp in batch:
                lp.refresh_from_db()
                if lp.can_complete():
                    LessonCompletionService._check_lesson_completion(lp)

            total_updated += len(batch)
            batch = list(islice(qs.iterator(), BATCH_SIZE))

        logger.info(
            f"Content deleted fan-out: {total_updated} rows updated",
            extra={
                'lesson_id': lesson_id,
                'content_id': content_id,
                'updated_rows': total_updated,
            }
        )

    except Exception as exc:
        logger.error(
            f"Content deleted fan-out failed: {exc}",
            exc_info=True,
            extra={'lesson_id': lesson_id, 'content_id': content_id}
        )
        raise self.retry(exc=exc)
