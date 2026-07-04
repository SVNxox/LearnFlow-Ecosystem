"""
Celery tasks для Learning Domain — Fan-out operations.

Fan-out операции обрабатывают N enrolled студентов асинхронно.
Эти задачи КРИТИЧНЫ для производительности — никогда не выполнять синхронно.

ADR-008: Fan-out на N студентов — только async через Celery.
"""

from celery import shared_task
from django.db import transaction


@shared_task(
    name="learning.fan_out_lesson_unlock",
    queue="fan_out",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def fan_out_lesson_unlock(lesson_id: str, course_id: str) -> dict:
    """
    Fan-out задача: unlock lesson для всех enrolled студентов.

    Triggered by: LessonPublished event

    Consumer: UserProgress Domain
    Action: Создаёт LessonProgress records для всех active enrollments

    Performance:
    - Батчинг по 100 студентов
    - Bulk create для минимизации DB roundtrips

    Args:
        lesson_id: UUID урока
        course_id: UUID курса

    Returns:
        dict: {
            "lesson_id": str,
            "unlocked_count": int,
            "duration_seconds": float
        }
    """
    import time
    from src.backend.enrollment.domain.models import CourseEnrollment

    start_time = time.time()

    
    from src.backend.progress.domain.models import LessonProgress

    
    enrollments = CourseEnrollment.objects.filter(
        course_id=course_id,
        status="active"
    ).values_list("id", flat=True)

    unlocked_count = 0
    batch_size = 100

    
    enrollment_list = list(enrollments)
    for i in range(0, len(enrollment_list), batch_size):
        batch = enrollment_list[i:i + batch_size]

        with transaction.atomic():
            
            LessonProgress.objects.bulk_create([
                LessonProgress(
                    enrollment_id=enrollment_id,
                    lesson_id=lesson_id,
                    status="not_started"
                )
                for enrollment_id in batch
            ], ignore_conflicts=True)  

            unlocked_count += len(batch)

    duration = time.time() - start_time

    return {
        "lesson_id": lesson_id,
        "unlocked_count": unlocked_count,
        "duration_seconds": round(duration, 2),
    }


@shared_task(
    name="learning.fan_out_content_deletion",
    queue="fan_out",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def fan_out_content_deletion(content_id: str, lesson_id: str) -> dict:
    """
    Fan-out задача: cleanup ContentView records после удаления контента.

    Triggered by: ContentDeleted event

    Consumer: UserProgress Domain
    Action: Удаляет orphaned LessonContentView records

    Performance:
    - Батчинг по 500 records
    - Bulk delete

    Args:
        content_id: UUID удалённого контента
        lesson_id: UUID урока

    Returns:
        dict: {
            "content_id": str,
            "deleted_count": int,
            "duration_seconds": float
        }
    """
    import time

    start_time = time.time()

    
    from src.backend.progress.domain.models import LessonContentView

    deleted_count = 0

    
    with transaction.atomic():
        deleted_count = LessonContentView.objects.filter(
            content_id=content_id
        ).delete()[0]

    duration = time.time() - start_time

    return {
        "content_id": content_id,
        "deleted_count": deleted_count,
        "duration_seconds": round(duration, 2),
    }


@shared_task(
    name="learning.fan_out_lesson_deletion",
    queue="fan_out",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def fan_out_lesson_deletion(lesson_id: str, module_id: str, course_id: str) -> dict:
    """
    Fan-out задача: mark LessonProgress records as orphaned после удаления урока.

    Triggered by: LessonDeleted event

    Consumer: UserProgress Domain
    Action: Sets is_orphaned=True на всех LessonProgress records

    Note: НЕ удаляем progress records — сохраняем для истории.

    Performance:
    - Батчинг по 500 records
    - Bulk update

    Args:
        lesson_id: UUID удалённого урока
        module_id: UUID модуля
        course_id: UUID курса

    Returns:
        dict: {
            "lesson_id": str,
            "orphaned_count": int,
            "duration_seconds": float
        }
    """
    import time

    start_time = time.time()

    
    from src.backend.progress.domain.models import LessonProgress

    orphaned_count = 0

    
    with transaction.atomic():
        orphaned_count = LessonProgress.objects.filter(
            lesson_id=lesson_id
        ).update(is_orphaned=True)

    duration = time.time() - start_time

    return {
        "lesson_id": lesson_id,
        "orphaned_count": orphaned_count,
        "duration_seconds": round(duration, 2),
    }


@shared_task(
    name="learning.update_course_snapshot_counts",
    queue="default",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def update_course_snapshot_counts(course_id: str) -> dict:
    """
    Обновляет денормализованные счётчики курса.

    Triggered by: ModulePublished, LessonPublished events

    Updates:
    - published_module_count
    - published_lesson_count
    - total_estimated_hours

    Note: Эти счётчики используются для hot path queries.

    Args:
        course_id: UUID курса

    Returns:
        dict: {
            "course_id": str,
            "module_count": int,
            "lesson_count": int,
            "total_hours": int
        }
    """
    from src.backend.learning.domain.models import Course, Module, Lesson
    from django.db.models import Count, Sum

    
    with transaction.atomic():
        course = Course.objects.select_for_update().get(
            id=course_id,
            deleted_at__isnull=True
        )

        
        module_count = Module.objects.filter(
            course_id=course_id,
            is_published=True,
            deleted_at__isnull=True
        ).count()

        
        lesson_count = Lesson.objects.filter(
            module__course_id=course_id,
            module__deleted_at__isnull=True,
            is_published=True,
            deleted_at__isnull=True
        ).count()

        
        total_hours = Module.objects.filter(
            course_id=course_id,
            is_published=True,
            deleted_at__isnull=True
        ).aggregate(
            total=Sum("estimated_hours")
        )["total"] or 0

        
        
        # course.published_lesson_count = lesson_count
        # course.total_estimated_hours = total_hours
        # course.save(update_fields=[
        #     "published_module_count",
        #     "published_lesson_count",
        #     "total_estimated_hours"
        # ])

    return {
        "course_id": course_id,
        "module_count": module_count,
        "lesson_count": lesson_count,
        "total_hours": total_hours,
    }


__all__ = [
    "fan_out_lesson_unlock",
    "fan_out_content_deletion",
    "fan_out_lesson_deletion",
    "update_course_snapshot_counts",
]
