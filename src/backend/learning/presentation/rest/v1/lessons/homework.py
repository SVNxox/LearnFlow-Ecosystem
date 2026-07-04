"""
Lesson Homework API — управление домашним заданием урока.

Endpoints:
- GET    /api/v1/learning/lessons/{lesson_id}/homework/ — получить homework
- POST   /api/v1/learning/lessons/{lesson_id}/homework/ — создать homework
- PATCH  /api/v1/learning/lessons/{lesson_id}/homework/ — обновить homework
- DELETE /api/v1/learning/lessons/{lesson_id}/homework/ — удалить homework
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.domain.models import Lesson, LessonHomework

logger = logging.getLogger(__name__)


class LessonHomeworkView(APIView):
    """Управление домашним заданием урока."""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, lesson_id: str) -> Response:
        """Получить homework урока."""
        lesson = get_object_or_404(Lesson, id=lesson_id, deleted_at__isnull=True)

        try:
            homework = LessonHomework.objects.get(lesson_id=lesson_id)
            return Response({
                "id": str(homework.id),
                "lesson_id": str(homework.lesson_id),
                "title": homework.title,
                "description": homework.description or '',
                "instructions": homework.instructions or '',
                "max_score": homework.max_score,
                "submission_type": homework.submission_type,
                "allowed_file_types": homework.allowed_file_types or [],
                "max_file_size_mb": homework.max_file_size_mb,
                "deadline_offset_days": homework.deadline_offset_days,
                "created_at": homework.created_at.isoformat() if homework.created_at else None,
                "updated_at": homework.updated_at.isoformat() if homework.updated_at else None,
            }, status=status.HTTP_200_OK)
        except LessonHomework.DoesNotExist:
            return Response(None, status=status.HTTP_200_OK)

    def post(self, request: Request, lesson_id: str) -> Response:
        """Создать homework для урока."""
        lesson = get_object_or_404(Lesson, id=lesson_id, deleted_at__isnull=True)

        
        if LessonHomework.objects.filter(lesson_id=lesson_id).exists():
            return Response(
                {"error": "Homework already exists for this lesson. Use PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data

        try:
            homework = LessonHomework.objects.create(
                lesson=lesson,
                title=data.get('title', ''),
                description=data.get('description', ''),
                instructions=data.get('instructions', ''),
                max_score=data.get('max_score', 100),
                submission_type=data.get('submission_type', 'text'),
                allowed_file_types=data.get('allowed_file_types', []),
                max_file_size_mb=data.get('max_file_size_mb', 50),
                deadline_offset_days=data.get('deadline_offset_days'),
            )

            return Response({
                "id": str(homework.id),
                "lesson_id": str(homework.lesson_id),
                "title": homework.title,
                "description": homework.description or '',
                "instructions": homework.instructions or '',
                "max_score": homework.max_score,
                "submission_type": homework.submission_type,
                "allowed_file_types": homework.allowed_file_types or [],
                "max_file_size_mb": homework.max_file_size_mb,
                "deadline_offset_days": homework.deadline_offset_days,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating homework: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request: Request, lesson_id: str) -> Response:
        """Обновить homework урока."""
        lesson = get_object_or_404(Lesson, id=lesson_id, deleted_at__isnull=True)

        try:
            homework = LessonHomework.objects.get(lesson_id=lesson_id)
        except LessonHomework.DoesNotExist:
            return Response(
                {"error": "Homework not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data

        
        if 'title' in data:
            homework.title = data['title']
        if 'description' in data:
            homework.description = data['description']
        if 'instructions' in data:
            homework.instructions = data['instructions']
        if 'max_score' in data:
            homework.max_score = data['max_score']
        if 'submission_type' in data:
            homework.submission_type = data['submission_type']
        if 'allowed_file_types' in data:
            homework.allowed_file_types = data['allowed_file_types']
        if 'max_file_size_mb' in data:
            homework.max_file_size_mb = data['max_file_size_mb']
        if 'deadline_offset_days' in data:
            homework.deadline_offset_days = data['deadline_offset_days']

        homework.save()

        return Response({
            "id": str(homework.id),
            "lesson_id": str(homework.lesson_id),
            "title": homework.title,
            "description": homework.description or '',
            "instructions": homework.instructions or '',
            "max_score": homework.max_score,
            "submission_type": homework.submission_type,
            "allowed_file_types": homework.allowed_file_types or [],
            "max_file_size_mb": homework.max_file_size_mb,
            "deadline_offset_days": homework.deadline_offset_days,
        }, status=status.HTTP_200_OK)

    def delete(self, request: Request, lesson_id: str) -> Response:
        """Удалить homework урока."""
        lesson = get_object_or_404(Lesson, id=lesson_id, deleted_at__isnull=True)

        try:
            homework = LessonHomework.objects.get(lesson_id=lesson_id)
            homework.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LessonHomework.DoesNotExist:
            return Response(
                {"error": "Homework not found"},
                status=status.HTTP_404_NOT_FOUND
            )