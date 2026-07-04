"""
Homework Info API — получение информации о homework для страницы отправки.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.domain.models import LessonHomework
from src.backend.submissions.domain.models import Assignment

logger = logging.getLogger(__name__)


class HomeworkInfoView(APIView):
    """Получить информацию о homework."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, homework_id: str) -> Response:
        try:
            homework = LessonHomework.objects.select_related(
                'lesson', 'lesson__module', 'lesson__module__course'
            ).get(id=homework_id)
        except LessonHomework.DoesNotExist:
            return Response(
                {"detail": "Homework not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        
        assignment = Assignment.objects.filter(lesson_id=homework.lesson_id).first()

        
        if not assignment:
            logger.info(f"Creating Assignment for lesson {homework.lesson_id}")
            assignment = Assignment.objects.create(
                lesson_id=homework.lesson_id,
                type='theory' if homework.submission_type == 'text' else 'coding',
                title=homework.title,
                description=homework.description or '',
                max_score=homework.max_score,
                deadline_offset_days=homework.deadline_offset_days,
                submission_types_allowed=['text_answer'],
                max_file_size_mb=homework.max_file_size_mb,
                created_by_id=request.user.id,
            )
            logger.info(f"Assignment created: {assignment.id}")

        logger.info(f"Homework {homework_id} -> Assignment {assignment.id}")

        return Response({
            "id": str(homework.id),
            "title": homework.title,
            "description": homework.description or '',
            "instructions": homework.instructions or '',
            "max_score": homework.max_score,
            "type": homework.submission_type,
            "deadline_offset_days": homework.deadline_offset_days,
            "max_file_size_mb": homework.max_file_size_mb,
            "lesson_id": str(homework.lesson_id),
            "lesson_title": homework.lesson.title,
            "module_title": homework.lesson.module.title,
            "course_title": homework.lesson.module.course.title,
            "course_slug": homework.lesson.module.course.slug,
            
            "assignment_id": str(assignment.id),
        }, status=status.HTTP_200_OK)