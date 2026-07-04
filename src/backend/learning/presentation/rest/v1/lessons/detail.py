"""
Lesson Detail API — просмотр, обновление и удаление урока.

Endpoints:
- GET    /api/v1/learning/lessons/{lesson_id}/ — детали урока (публичный)
- PATCH  /api/v1/learning/lessons/{lesson_id}/ — обновление урока (админский)
- DELETE /api/v1/learning/lessons/{lesson_id}/ — удаление урока (админский)

Permissions:
- GET: AllowAny (с проверкой видимости внутри)
- PATCH/DELETE: IsAuthenticated + IsAdminOrStaff
"""

import logging
from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import UpdateLessonCommand, UpdateLessonData
from src.backend.learning.application.queries import LessonDetailQuery

logger = logging.getLogger(__name__)


class LessonDetailView(APIView):
    """
    Детали урока. Поддерживает GET, PATCH, DELETE.

    - GET: публичный доступ с проверкой видимости
    - PATCH/DELETE: только admin/staff/course author
    """

    def get_permissions(self):
        """
        Разные права для разных методов:
        - GET: AllowAny (с проверкой visibility внутри)
        - PATCH/DELETE: IsAuthenticated + IsAdminOrStaff
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrStaff()]

    def get(self, request: Request, lesson_id: str) -> Response:
        """
        Возвращает детальную информацию об уроке.

        Visibility:
        - free_preview=True: доступен всем
        - Иначе: требуется active enrollment в курсе (или admin/staff/author)
        """
        user = request.user if request.user.is_authenticated else None

        lesson = LessonDetailQuery.get_lesson_detail(lesson_id=lesson_id, user=user)

        if not lesson:
            return Response(
                {"detail": "Lesson not found or not accessible."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        return Response(asdict(lesson), status=status.HTTP_200_OK)

    def patch(self, request: Request, lesson_id: str) -> Response:
        """
        Обновляет урок.

        Permissions: Admin, Staff, or Course Author
        """
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
                "is_published": lesson.is_published,
                "order": lesson.order,
                "module_id": str(lesson.module_id),
                "created_at": lesson.created_at.isoformat(),
                "updated_at": lesson.updated_at.isoformat(),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error updating lesson: {e.code}")
            return Response(
                {"detail": str(e.message) if hasattr(e, 'message') else str(e), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )
        except NotFoundError as e:
            logger.warning(f"Not found error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AccessDeniedError as e:
            logger.warning(f"Access denied error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(
                f"Unexpected error updating lesson: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An unexpected error occurred while updating the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request: Request, lesson_id: str) -> Response:
        """
        Удаляет урок (soft delete).

        Permissions: Admin, Staff, or Course Author
        """
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

        except NotFoundError as e:
            logger.warning(f"Not found error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AccessDeniedError as e:
            logger.warning(f"Access denied error: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except BusinessValidationError as e:
            logger.warning(f"Business validation error deleting lesson: {e.code}")
            return Response(
                {"detail": str(e.message) if hasattr(e, 'message') else str(e), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Unexpected error deleting lesson: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An unexpected error occurred while deleting the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )