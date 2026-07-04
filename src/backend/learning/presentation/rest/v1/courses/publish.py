"""
Course Publish/Unpublish API — публикация/снятие с публикации курса.

Endpoints:
- POST /api/v1/learning/courses/{course_id}/publish/ — публикация курса
- POST /api/v1/learning/courses/{course_id}/unpublish/ — снятие с публикации

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
from src.backend.learning.application.commands import PublishCourseCommand

logger = logging.getLogger(__name__)


class CoursePublishView(APIView):
    """
    POST /api/v1/learning/courses/{course_id}/publish/ — публикация курса.

    Path Parameters:
    - course_id: UUID курса

    Business Rules:
    - Курс должен быть в статусе 'draft'
    - Минимум 1 опубликованный модуль с минимум 1 опубликованным уроком
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, course_id: str) -> Response:
        """Публикует курс."""

        try:
            
            course = PublishCourseCommand.execute(
                course_id=course_id, actor=request.user
            )

            response_data = {
                "id": str(course.id),
                "title": course.title,
                "slug": course.slug,
                "status": course.status,  
                "message": "Course published successfully.",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error publishing course: {e.code}")
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
                f"Unexpected error publishing course: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An error occurred while publishing the course."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CourseUnpublishView(APIView):
    """
    POST /api/v1/learning/courses/{course_id}/unpublish/ — снятие с публикации.

    Path Parameters:
    - course_id: UUID курса

    Business Rules:
    - Нельзя unpublish если есть active enrollments
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, course_id: str) -> Response:
        """Снимает курс с публикации."""

        try:
            
            course = PublishCourseCommand.unpublish_course(
                course_id=course_id, actor=request.user
            )

            response_data = {
                "id": str(course.id),
                "title": course.title,
                "slug": course.slug,
                "status": course.status,  
                "message": "Course unpublished successfully.",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BusinessValidationError as e:
            logger.warning(f"Business validation error unpublishing course: {e.code}")
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
                f"Unexpected error unpublishing course: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return Response(
                {"detail": "An error occurred while unpublishing the course."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )