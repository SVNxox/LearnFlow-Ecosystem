"""
Course Create API — создание нового курса.

Endpoint: POST /api/v1/learning/courses/create/
Permissions: IsAuthenticated + IsAdminOrStaff
"""

import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.utils.permissions import IsAdminOrStaff  
from src.backend.learning.application.commands import CreateCourseCommand, CreateCourseData

logger = logging.getLogger(__name__)


class CourseCreateView(APIView):
    """
    POST /api/v1/learning/courses/create/ — создание курса.

    Permissions: Admin или Staff only
    """

    
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request) -> Response:
        """Создаёт новый курс."""
        data = request.data

        
        if not data.get("title"):
            return Response(
                {"detail": "Title is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            command_data = CreateCourseData(
                title=data.get("title"),
                slug=data.get("slug"),
                description=data.get("description", ""),
                short_description=data.get("short_description", ""),
                thumbnail_url=data.get("thumbnail_url"),
                category_id=data.get("category_id"),
                status=data.get("status", "draft"),  
                supports_online=data.get("supports_online", True),
                supports_offline=data.get("supports_offline", False),
                language=data.get("language", "ru"),
                estimated_weeks=data.get("estimated_weeks"),
                is_sequential=data.get("is_sequential", True),
                price=data.get("price", "0"),  
                currency=data.get("currency", "UZS"),
            )

            
            course = CreateCourseCommand.execute(data=command_data, actor=request.user)

            
            response_data = {
                "id": str(course.id),
                "title": course.title,
                "slug": course.slug,
                "description": course.description,
                "short_description": course.short_description,
                "thumbnail_url": course.thumbnail_url,
                "category_id": str(course.category_id) if course.category_id else None,
                "status": course.status,
                "supports_online": course.supports_online,
                "supports_offline": course.supports_offline,
                "language": course.language,
                "estimated_weeks": course.estimated_weeks,
                "is_sequential": course.is_sequential,
                "created_by": str(course.created_by_id),
                "created_at": course.created_at.isoformat(),
                "updated_at": course.updated_at.isoformat(),
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.warning(f"Validation error creating course: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except PermissionError as e:
            logger.warning(f"Permission error creating course: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        except Exception as e:
            logger.error(f"Error creating course: {e}", exc_info=True)
            return Response(
                {"detail": f"An error occurred while creating the course: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )