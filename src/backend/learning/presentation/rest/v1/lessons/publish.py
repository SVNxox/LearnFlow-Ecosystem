"""
Lesson Publish/Unpublish API — публикация/снятие с публикации урока.

Endpoints:
- POST /api/v1/learning/lessons/{lesson_id}/publish/ — публикация урока
- POST /api/v1/learning/lessons/{lesson_id}/unpublish/ — снятие с публикации

Permissions: Admin, Staff, or Course Author
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.core.exceptions import BusinessValidationError, NotFoundError, AccessDeniedError
from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.commands import UpdateLessonCommand

logger = logging.getLogger(__name__)


class LessonPublishView(APIView):
    """
    POST /api/v1/learning/lessons/{lesson_id}/publish/ — публикация урока.

    Path Parameters:
    - lesson_id: UUID урока

    Business Rules:
    - Урок должен иметь минимум 1 компонент (content/homework/quiz/practice)
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        """Публикует урок."""

        try:
            
            lesson = UpdateLessonCommand.publish_lesson(
                lesson_id=lesson_id, actor=request.user
            )

            response_data = {
                "id": str(lesson.id),
                "title": lesson.title,
                "is_published": lesson.is_published,
                "message": "Lesson published successfully.",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error publishing lesson: {e.code}")
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
                f"Unexpected error publishing lesson: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An error occurred while publishing the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LessonUnpublishView(APIView):
    """
    POST /api/v1/learning/lessons/{lesson_id}/unpublish/ — снятие с публикации.

    Path Parameters:
    - lesson_id: UUID урока
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        """Снимает урок с публикации."""

        try:
            
            lesson = UpdateLessonCommand.unpublish_lesson(
                lesson_id=lesson_id, actor=request.user
            )

            response_data = {
                "id": str(lesson.id),
                "title": lesson.title,
                "is_published": lesson.is_published,
                "message": "Lesson unpublished successfully.",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error unpublishing lesson: {e.code}")
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
                f"Unexpected error unpublishing lesson: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An error occurred while unpublishing the lesson."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )