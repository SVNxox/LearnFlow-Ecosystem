"""
Lesson Update API — обновление урока.

Endpoint: PATCH /api/learning/{course_id}/modules/{module_id}/lessons/{lesson_id}/
Permissions: IsStaff or IsAuthor
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError, PermissionDenied

from src.backend.learning.application.commands import UpdateLessonCommand, UpdateLessonData


class LessonUpdateView(APIView):
    """
    PATCH /api/learning/{course_id}/modules/{module_id}/lessons/{lesson_id}/
    — обновление урока.

    Permissions: Staff or Course Author

    Path Parameters:
    - course_id: UUID курса
    - module_id: UUID модуля
    - lesson_id: UUID урока

    Request Body:
    {
        "title": str (optional),
        "description": str (optional),
        "estimated_minutes": int (optional),
        "is_free_preview": bool (optional)
    }

    Response: Updated lesson
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, course_id: str, module_id: str, lesson_id: str) -> Response:
        """Обновляет урок."""

        data = request.data

        try:
            
            command_data = UpdateLessonData(
                title=data.get("title"),
                description=data.get("description"),
                estimated_minutes=data.get("estimated_minutes"),
                is_free_preview=data.get("is_free_preview"),
            )

            
            lesson = UpdateLessonCommand.execute(
                lesson_id=lesson_id, data=command_data, actor=request.user
            )

            
            response_data = {
                "id": str(lesson.id),
                "title": lesson.title,
                "description": lesson.description,
                "estimated_minutes": lesson.estimated_minutes,
                "is_free_preview": lesson.is_free_preview,
                "order": lesson.order,
                "is_published": lesson.is_published,
                "module_id": str(lesson.module_id),
                "created_at": lesson.created_at.isoformat(),
                "updated_at": lesson.updated_at.isoformat(),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"detail": "An error occurred while updating the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LessonDeleteView(APIView):
    """
    DELETE /api/learning/{course_id}/modules/{module_id}/lessons/{lesson_id}/
    — удаление урока (soft delete).

    Permissions: Staff or Course Author

    Path Parameters:
    - course_id: UUID курса
    - module_id: UUID модуля
    - lesson_id: UUID урока

    Response: Deleted lesson
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, course_id: str, module_id: str, lesson_id: str) -> Response:
        """Удаляет урок (soft delete)."""

        try:
            
            lesson = UpdateLessonCommand.delete_lesson(
                lesson_id=lesson_id, actor=request.user
            )

            
            response_data = {
                "id": str(lesson.id),
                "title": lesson.title,
                "deleted_at": lesson.deleted_at.isoformat() if lesson.deleted_at else None,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"detail": "An error occurred while deleting the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
